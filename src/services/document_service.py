from services.db_service import insert_document, insert_chunk

def save_document_with_chunks(filename, cloudinary_url, cloudinary_public_id, chunks):
    doc_id = insert_document(filename, cloudinary_url, cloudinary_public_id)

    for page_number, text in chunks:
        insert_chunk(doc_id, page_number, text)

    return doc_id