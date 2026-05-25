from io import BytesIO

from pypdf import PdfReader

from db.db_service import insert_document, insert_chunks
from services.cloudinary_service import upload_pdf
from services.embedding_service import EmbeddingService
from services.faiss_search_service import FaissSearchService


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
        faiss_service = FaissSearchService(dimension=embeddings.shape[1])
        faiss_service.add_embeddings(chunk_ids, embeddings)

    return doc_id