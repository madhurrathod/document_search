import streamlit as st
from groq import Groq
from services.search_service import SearchService

# Groq shut down llama-3.1-8b-instant on 16 Aug 2026; every RAG call failed
# after that. The model is now a setting, so the next retirement is a
# secrets change instead of a code change.
DEFAULT_GROQ_MODEL = "openai/gpt-oss-20b"

# Cosine-similarity cutoff below which a chunk is treated as irrelevant.
# 0.5 was very strict for all-MiniLM-L6-v2 (a relevant question/passage pair
# often scores 0.3-0.5), so real matches were being discarded and the app
# answered "No relevant document found." Provisional value: calibrate it
# with scripts/eval_retrieval.py on your own documents.
DEFAULT_MIN_SCORE = 0.3

MAX_CHUNKS_PER_DOCUMENT = 3
MAX_CONTEXT_CHUNKS = 5


class RagService:
    def __init__(self):
        self.search_service = SearchService()
        self.client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        self.model = st.secrets.get("GROQ_MODEL", DEFAULT_GROQ_MODEL)

    def retrieve_context(self, query: str, top_k: int = 10, min_score: float = DEFAULT_MIN_SCORE):
        ranked_documents = self.search_service.search_for_rag(
            query=query,
            top_k=top_k,
            min_score=min_score,
        )

        if not ranked_documents:
            return {
                "answer": "No relevant document found.",
                "context": "",
                "sources": [],
                "documents": [],
            }

        top_documents = ranked_documents[:2]
        selected_chunks = []

        # Chunks are now ~150 words instead of a whole page, so pass a few
        # more of them to keep roughly the same amount of context.
        for document in top_documents:
            selected_chunks.extend(document["chunks"][:MAX_CHUNKS_PER_DOCUMENT])

        selected_chunks = sorted(selected_chunks, key=lambda item: item["score"], reverse=True)[:MAX_CONTEXT_CHUNKS]

        context_parts = []
        for chunk in selected_chunks:
            context_parts.append(
                f"Document: {chunk['filename']}\n"
                f"Page: {chunk['page_number']}\n"
                f"Content: {chunk['text']}"
            )

        context = "\n\n".join(context_parts)

        return {
            "answer": None,
            "context": context,
            "sources": selected_chunks,
            "documents": top_documents,
        }

    def answer_query(self, query: str, top_k: int = 10, min_score: float = DEFAULT_MIN_SCORE):
        retrieved_data = self.retrieve_context(
            query=query,
            top_k=top_k,
            min_score=min_score,
        )

        if not retrieved_data["sources"]:
            return {
                "answer": "No relevant document found.",
                "sources": [],
                "documents": [],
            }

        prompt = f"""
You are a document assistant.

Answer the user's question using only the provided context.
If the context does not contain enough information, say:
Not enough information in the retrieved documents.
Do not mention information that is not present in the context.

User question:
{query}

Context:
{retrieved_data['context']}
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "Answer only from the provided document context."
                },
                {
                    "role": "user",
                    "content": prompt
                },
            ],
            temperature=0.2,
        )

        answer = response.choices[0].message.content

        return {
            "answer": answer,
            "sources": retrieved_data["sources"],
            "documents": retrieved_data["documents"],
        }
