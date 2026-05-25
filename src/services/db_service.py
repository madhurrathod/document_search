import sqlite3
import os

DB_PATH = "storage/docs.db"
os.makedirs("storage", exist_ok=True)

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def insert_document(filename, cloudinary_url, cloudinary_public_id):
    conn = get_connection()
    cursor = conn.execute("""
        INSERT INTO documents (filename, cloudinary_url, cloudinary_public_id)
        VALUES (?, ?, ?)
    """, (filename, cloudinary_url, cloudinary_public_id))
    conn.commit()
    doc_id = cursor.lastrowid
    conn.close()
    return doc_id

def insert_chunk(document_id, page_number, text):
    conn = get_connection()
    conn.execute("""
        INSERT INTO chunks (document_id, page_number, text)
        VALUES (?, ?, ?)
    """, (document_id, page_number, text))
    conn.commit()
    conn.close()

def get_all_documents():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM documents").fetchall()
    conn.close()
    return [dict(row) for row in rows]