# What this project does
Document Search helps find the right PDF from a collection of uploaded documents.

If the exact file name is forgotten, the user can type a few words, a line, or an idea remembered from the document. The app then returns the most relevant matching document sections.

# Technical overview
This project is built using:

Streamlit for the user interface.

Supabase Postgres for storing document metadata and text chunks.

Cloudinary for storing uploaded PDF files.

PyPDF for reading and extracting text from PDFs.

Sentence Transformers for generating embeddings.

FAISS for semantic similarity search.

## Flow:

- Upload PDF

- Store file in Cloudinary

- Store metadata and chunks in Supabase

- Generate embeddings

- Search through FAISS index

- Return the best matching results

## Setup
1. Install dependencies
```bash
pip install -r requirements.txt
```
2. Add secrets
Create .streamlit/secrets.toml:

```text
[postgres]
host = "YOUR_SUPABASE_POOLER_HOST"
port = 5432
database = "postgres"
user = "postgres.YOUR_PROJECT_REF"
password = "YOUR_PASSWORD"
sslmode = "require"
```
Add Cloudinary credentials too if your services use them.

3. Ignore secret files
Add this to .gitignore:
```text
.env
.streamlit/secrets.toml
__pycache__/
storage/
```
4. Run the app
```bash
streamlit run src/main.py
```