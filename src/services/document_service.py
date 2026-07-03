from io import BytesIO

from pypdf import PdfReader

from db.db_service import (
    insert_document,
    insert_chunks,
    update_chunk_embeddings,
    get_chunks_without_embeddings,
)
from services.cloudinary_service import upload_pdf
from services.embedding_service import EmbeddingService


def process_uploaded_document(uploaded_file):
    file_bytes = uploaded_file.getvalue()
    result = upload_pdf(file_bytes, uploaded_file.name)

    reader = PdfReader(BytesIO(file_bytes))
    chunks = []

    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text and text.strip():
            chunks.append((i + 1, text.strip()))

    if not chunks:
        raise ValueError("No readable text found in the uploaded PDF.")

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
    Used to repopulate vectors for documents ingested before pgvector, or
    after the old on-disk FAISS index was lost. Returns the number of
    chunks updated."""
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