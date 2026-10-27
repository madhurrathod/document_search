# About Document Search
Document Search helps find the right PDF from a collection of uploaded documents.

If the exact file name is forgotten, the user can type a few words, a line, or an idea remembered from the document. The app then returns the most relevant matching document sections.

# Technical overview
This project is built using:

**Streamlit** for the user interface.

**Supabase Postgres + pgvector** for storing document metadata, text chunks and their embeddings, and for vector similarity search (HNSW index, cosine distance).

**Cloudinary** for storing uploaded PDF files.

**PyPDF** for reading and extracting text from PDFs.

**Sentence Transformers** for generating embeddings.

**Groq** for the RAG answer generation layer.

## Current Implementation
The current system supports PDF upload, text extraction, chunk storage, embedding generation, and semantic retrieval using pgvector. It is designed to return the most relevant document sections based on user queries instead of relying only on exact keyword or file-name matches.

At query time, the system embeds the user query, runs a cosine-similarity search over the chunk embeddings in Postgres (pgvector), and returns the most relevant results with document context. The next layer of the project uses those retrieved chunks as context for RAG-based answer generation. 

## Flow:
1.	Upload a PDF.
2.	Store the file in Cloudinary.
3.	Extract text using PyPDF.
4.	Split each page into ~150-word chunks with 30-word overlap (the embedding model truncates input after 256 word pieces).
5.	Store metadata and chunk text in Supabase Postgres.
6.	Generate embeddings using Sentence Transformers (all-MiniLM-L6-v2, 384 dimensions).
7.	Store embeddings in pgvector, indexed with HNSW.
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
# Optional; defaults to openai/gpt-oss-20b
GROQ_MODEL = "openai/gpt-oss-20b"

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

## Measuring retrieval quality
`scripts/eval_retrieval.py` runs a list of questions (with the file and page that answers each) through the search and reports hit@1, hit@5, MRR and the similarity scores of correct vs. wrong matches. Use it to choose the RAG relevance cutoff (`DEFAULT_MIN_SCORE` in `src/services/rag_service.py`).

```bash
python scripts/eval_retrieval.py scripts/eval_questions.csv
```

`scripts/eval_documents/` holds three fictional test PDFs whose key facts sit near the bottom of long pages, past where an un-chunked page would be truncated. `scripts/eval_questions.csv` has 12 questions with the file and page that answers each, plus 3 that none of the documents answer. Upload the three PDFs through the app, then run the script.

