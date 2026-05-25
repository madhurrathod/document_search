from db.database import get_connection


def insert_document(filename, cloudinary_url, cloudinary_public_id):
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            INSERT INTO documents (filename, cloudinary_url, cloudinary_public_id)
            VALUES (?, ?, ?)
            """,
            (filename, cloudinary_url, cloudinary_public_id),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def insert_chunk(document_id, page_number, text):
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            INSERT INTO chunks (document_id, page_number, text)
            VALUES (?, ?, ?)
            """,
            (document_id, page_number, text),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def insert_chunks(document_id, chunks):
    conn = get_connection()
    inserted_chunks = []

    try:
        for page_number, text in chunks:
            cursor = conn.execute(
                """
                INSERT INTO chunks (document_id, page_number, text)
                VALUES (?, ?, ?)
                """,
                (document_id, page_number, text),
            )
            inserted_chunks.append(
                {
                    "chunk_id": cursor.lastrowid,
                    "document_id": document_id,
                    "page_number": page_number,
                    "text": text,
                }
            )

        conn.commit()
        return inserted_chunks
    finally:
        conn.close()


def get_all_documents():
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT *
            FROM documents
            ORDER BY uploaded_at DESC, id DESC
            """
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_chunks_by_document_id(document_id):
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT id, document_id, page_number, text
            FROM chunks
            WHERE document_id = ?
            ORDER BY page_number ASC
            """,
            (document_id,),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_all_chunks_with_documents():
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT
                c.id AS chunk_id,
                c.document_id,
                c.page_number,
                c.text,
                d.filename,
                d.cloudinary_url,
                d.cloudinary_public_id
            FROM chunks c
            JOIN documents d ON d.id = c.document_id
            ORDER BY c.id ASC
            """
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_chunk_results_by_ids(chunk_ids):
    if not chunk_ids:
        return []

    conn = get_connection()
    try:
        placeholders = ",".join(["?"] * len(chunk_ids))
        rows = conn.execute(
            f"""
            SELECT
                c.id AS chunk_id,
                c.document_id,
                c.page_number,
                c.text,
                d.filename,
                d.cloudinary_url,
                d.cloudinary_public_id
            FROM chunks c
            JOIN documents d ON d.id = c.document_id
            WHERE c.id IN ({placeholders})
            """,
            chunk_ids,
        ).fetchall()

        row_map = {row["chunk_id"]: dict(row) for row in rows}
        return [row_map[chunk_id] for chunk_id in chunk_ids if chunk_id in row_map]
    finally:
        conn.close()