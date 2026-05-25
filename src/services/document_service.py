from io import BytesIO
from pypdf import PdfReader
from services.cloudinary_service import upload_pdf
from db.db_service import insert_document, insert_chunk

def save_document_with_chunks(filename, cloudinary_url, cloudinary_public_id, chunks):
    doc_id = insert_document(filename, cloudinary_url, cloudinary_public_id)

    for page_number, text in chunks:
        insert_chunk(doc_id, page_number, text)

    return doc_id

def process_uploaded_document(uploaded_file):
    file_bytes = uploaded_file.getvalue()
    result = upload_pdf(file_bytes, uploaded_file.name)

    reader = PdfReader(BytesIO(file_bytes))
    chunks = []

    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text and text.strip():
            chunks.append((i + 1, text.strip()))

    return save_document_with_chunks(
        uploaded_file.name,
        result["secure_url"],
        result["public_id"],
        chunks
    )