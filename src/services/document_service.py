import hashlib
from io import BytesIO

from pypdf import PdfReader

from db.db_service import (
    find_document_by_public_id,
    insert_document,
    insert_chunks,
    update_chunk_embeddings,
    get_chunks_without_embeddings,
)
from services.cloudinary_service import upload_pdf
from services.embedding_service import EmbeddingService

# all-MiniLM-L6-v2 truncates input after 256 word pieces. English averages
# roughly 1.3 word pieces per word, so 150-word windows stay safely under the
# limit. Before this, each whole page was one chunk and everything after the
# first ~200 words of a page was invisible to search.
CHUNK_WORDS = 150
CHUNK_OVERLAP_WORDS = 30  # so a sentence cut at a boundary appears whole in one chunk


def split_into_chunks(text, chunk_words=CHUNK_WORDS, overlap=CHUNK_OVERLAP_WORDS):
    words = text.split()
    if not words:
        return []

    step = chunk_words - overlap
    chunks = []
    for start in range(0, len(words), step):
        chunks.append(" ".join(words[start:start + chunk_words]))
        if start + chunk_words >= len(words):
            break
    return chunks


def extract_chunks(file_bytes):
    """Return [(page_number, chunk_index, text), ...] for a PDF."""
    reader = PdfReader(BytesIO(file_bytes))
    chunks = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        for chunk_index, chunk_text in enumerate(split_into_chunks(text)):
            chunks.append((page_number, chunk_index, chunk_text))

    return chunks


def process_uploaded_document(uploaded_file):
    file_bytes = uploaded_file.getvalue()

    # Validate before uploading, so a scanned/empty PDF doesn't leave an
    # orphaned file in Cloudinary.
    chunks = extract_chunks(file_bytes)
    if not chunks:
        raise ValueError("No readable text found in the uploaded PDF.")

    # Identify a document by its content, not its filename. Previously two
    # different files named "notes.pdf" shared one Cloudinary id: the second
    # upload overwrote the first PDF, but the database kept the first file's
    # text, so search results pointed at the wrong file.
    content_hash = hashlib.sha256(file_bytes).hexdigest()[:16]
    public_id = f"documents/{content_hash}-{uploaded_file.name}"

    existing_id = find_document_by_public_id(public_id)
    if existing_id is not None:
        return existing_id  # identical file already indexed

    result = upload_pdf(file_bytes, public_id)

    doc_id = insert_document(
        uploaded_file.name,
        result["secure_url"],
        result["public_id"],
    )

    inserted_chunks = insert_chunks(doc_id, chunks)

    texts = [chunk["text"] for chunk in inserted_chunks]
    chunk_ids = [chunk["chunk_id"] for chunk in inserted_chunks]

    embedding_service = EmbeddingService()
    embeddings = embedding_service.embed_texts(texts)

    if embeddings.size > 0:
        update_chunk_embeddings(zip(chunk_ids, embeddings.tolist()))

    return doc_id


def backfill_missing_embeddings():
    """Compute and store embeddings for any chunks that don't have one yet.
    Returns the number of chunks updated."""
    pending = get_chunks_without_embeddings()
    if not pending:
        return 0

    texts = [chunk["text"] for chunk in pending]
    chunk_ids = [chunk["chunk_id"] for chunk in pending]

    embedding_service = EmbeddingService()
    embeddings = embedding_service.embed_texts(texts)

    if embeddings.size == 0:
        return 0

    update_chunk_embeddings(zip(chunk_ids, embeddings.tolist()))
    return len(chunk_ids)
