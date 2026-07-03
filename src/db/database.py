import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor

# Dimension of the all-MiniLM-L6-v2 sentence-transformer embeddings.
EMBEDDING_DIMENSION = 384


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

        # pgvector stores the embeddings alongside the chunk text, so the
        # vector index lives in Supabase (durable) instead of on the app's
        # ephemeral local disk.
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector")

        cur.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id SERIAL PRIMARY KEY,
                filename TEXT NOT NULL,
                cloudinary_url TEXT NOT NULL,
                cloudinary_public_id TEXT NOT NULL UNIQUE,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS chunks (
                id SERIAL PRIMARY KEY,
                document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
                page_number INTEGER NOT NULL,
                text TEXT NOT NULL,
                embedding vector({EMBEDDING_DIMENSION}),
                UNIQUE(document_id, page_number)
            )
        """)

        # Backfill for databases created before the embedding column existed.
        cur.execute(f"""
            ALTER TABLE chunks
            ADD COLUMN IF NOT EXISTS embedding vector({EMBEDDING_DIMENSION})
        """)

        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_chunks_document_id
            ON chunks(document_id)
        """)

        # HNSW index for fast cosine-similarity search. Embeddings are
        # L2-normalized, so cosine distance and inner product agree.
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_chunks_embedding
            ON chunks USING hnsw (embedding vector_cosine_ops)
        """)

        conn.commit()
    finally:
        conn.close()