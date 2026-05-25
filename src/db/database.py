import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor


def get_connection():
    return psycopg2.connect(
        host=st.secrets["postgres"]["host"],
        port=st.secrets["postgres"]["port"],
        dbname=st.secrets["postgres"]["database"],
        user=st.secrets["postgres"]["user"],
        password=st.secrets["postgres"]["password"],
        sslmode=st.secrets["postgres"]["sslmode"],
        cursor_factory=RealDictCursor,
    )


def init_db():
    conn = get_connection()
    try:
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id SERIAL PRIMARY KEY,
                filename TEXT NOT NULL,
                cloudinary_url TEXT NOT NULL,
                cloudinary_public_id TEXT NOT NULL UNIQUE,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS chunks (
                id SERIAL PRIMARY KEY,
                document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
                page_number INTEGER NOT NULL,
                text TEXT NOT NULL,
                UNIQUE(document_id, page_number)
            )
        """)

        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_chunks_document_id
            ON chunks(document_id)
        """)

        conn.commit()
    finally:
        conn.close()