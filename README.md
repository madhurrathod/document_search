# About Document Search
Document Search helps find the right PDF from a collection of uploaded documents.

If the exact file name is forgotten, the user can type a few words, a line, or an idea remembered from the document. The app then returns the most relevant matching document sections.

# Technical overview
This project is built using:

**Streamlit** for the user interface.

**Supabase Postgres** for storing document metadata and text chunks.

**Cloudinary** for storing uploaded PDF files.

**PyPDF** for reading and extracting text from PDFs.

**Sentence Transformers** for generating embeddings.

**FAISS** for semantic similarity search.

**Groq** for the RAG answer generation layer.

## Current Implementation
The current system supports PDF upload, text extraction, chunk storage, embedding generation, and semantic retrieval using FAISS. It is designed to return the most relevant document sections based on user queries instead of relying only on exact keyword or file-name matches.

At query time, the system embeds the user query, searches the FAISS index, fetches the matching chunk metadata from Postgres, and returns the most relevant results with document context. The next layer of the project uses those retrieved chunks as context for RAG-based answer generation. 

## Flow:
1.	Upload a PDF.
2.	Store the file in Cloudinary.
3.	Extract text using PyPDF.
4.	Split the document into chunk-based sections.
5.	Store metadata and chunk text in Supabase Postgres.
6.	Generate embeddings using Sentence Transformers.
7.	Index embeddings in FAISS for semantic retrieval.
8.	Retrieve top matching chunks for a user query.
9.	Use retrieved chunks as context for RAG-based answers with Groq.

## Setup
1. Install dependencies
```bash
pip install -r requirements.txt
```
2. Add secrets
Create .streamlit/secrets.toml:

```text
GROQ_API_KEY = "your_groq_api_key"

[postgres]
host = "YOUR_SUPABASE_POOLER_HOST"
port = 5432
database = "postgres"
user = "postgres.YOUR_PROJECT_REF"
password = "YOUR_PASSWORD"
sslmode = "require"

[cloudinary]
cloud_name = "your_cloudinary_cloud_name"
api_key = "your_cloudinary_api_key"
api_secret = "your_cloudinary_api_secret"
```

3. Run the app
```bash
streamlit run src/main.py
```