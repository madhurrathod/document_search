from db.database import get_connection


def insert_document(filename, cloudinary_url, cloudinary_public_id):
    conn = get_connection()
    try:
        cur = conn.cursor()

        cur.execute(
            """
            SELECT id
            FROM documents
            WHERE cloudinary_public_id = %s
            """,
            (cloudinary_public_id,),
        )
        existing = cur.fetchone()

        if existing:
            return existing["id"]

        cur.execute(
            """
            INSERT INTO documents (filename, cloudinary_url, cloudinary_public_id)
            VALUES (%s, %s, %s)
            RETURNING id
            """,
            (filename, cloudinary_url, cloudinary_public_id),
        )
        doc_id = cur.fetchone()["id"]
        conn.commit()
        return doc_id
    finally:
        conn.close()


def insert_chunk(document_id, page_number, text):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO chunks (document_id, page_number, text)
            VALUES (%s, %s, %s)
            ON CONFLICT (document_id, page_number) DO NOTHING
            RETURNING id
            """,
            (document_id, page_number, text),
        )
        row = cur.fetchone()
        conn.commit()
        return row["id"] if row else None
    finally:
        conn.close()


def insert_chunks(document_id, chunks):
    conn = get_connection()
    inserted_chunks = []

    try:
        cur = conn.cursor()

        for page_number, text in chunks:
            cur.execute(
                """
                INSERT INTO chunks (document_id, page_number, text)
                VALUES (%s, %s, %s)
                ON CONFLICT (document_id, page_number) DO NOTHING
                RETURNING id
                """,
                (document_id, page_number, text),
            )
            row = cur.fetchone()

            if row:
                inserted_chunks.append(
                    {
                        "chunk_id": row["id"],
                        "document_id": document_id,
                        "page_number": page_number,
                        "text": text,
                    }
                )

        conn.commit()

        if inserted_chunks:
            return inserted_chunks

        cur.execute(
            """
            SELECT id AS chunk_id, document_id, page_number, text
            FROM chunks
            WHERE document_id = %s
            ORDER BY page_number ASC
            """,
            (document_id,),
        )
        rows = cur.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_all_documents():
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT *
            FROM documents
            ORDER BY uploaded_at DESC, id DESC
            """
        )
        rows = cur.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_chunks_by_document_id(document_id):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, document_id, page_number, text
            FROM chunks
            WHERE document_id = %s
            ORDER BY page_number ASC
            """,
            (document_id,),
        )
        rows = cur.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_all_chunks_with_documents():
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
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
        )
        rows = cur.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_chunk_results_by_ids(chunk_ids):
    if not chunk_ids:
        return []

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
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
            WHERE c.id = ANY(%s)
            """,
            (chunk_ids,),
        )
        rows = cur.fetchall()
        row_map = {row["chunk_id"]: dict(row) for row in rows}
        return [row_map[chunk_id] for chunk_id in chunk_ids if chunk_id in row_map]
    finally:
        conn.close()