import streamlit as st
from groq import Groq
from services.search_service import SearchService

class RagService:
    def __init__(self):
        self.search_service = SearchService()
        self.client = Groq(api_key=st.secrets["GROQ_API_KEY"])

    def retrieve_context(self, query: str, top_k: int = 5, min_score: float = 0.5):
        results = self.search_service.search_for_rag(
            query=query,
            top_k=top_k,
            min_score=min_score,
        )

        if not results:
            return {
                "answer": "No relevant document found.",
                "context": "",
                "sources": [],
            }

        selected_results = results[:3]

        context_parts = []
        for result in selected_results:
            context_parts.append(
                f"Document: {result['filename']}\n"
                f"Page: {result['page_number']}\n"
                f"Content: {result['snippet']}"
            )

        context = "\n\n".join(context_parts)

        return {
            "answer": None,
            "context": context,
            "sources": selected_results,
        }

    def answer_query(self, query: str, top_k: int = 5, min_score: float = 0.5):
        retrieved_data = self.retrieve_context(
            query=query,
            top_k=top_k,
            min_score=min_score,
        )

        if not retrieved_data["sources"]:
            return {
                "answer": "No relevant document found.",
                "sources": [],
            }

        prompt = f"""
You are a document assistant.

Answer the user's question using only the provided context.
If the context does not contain enough information, say:
Not enough information in the retrieved documents.

User question:
{query}

Context:
{retrieved_data['context']}
"""

        response = self.client.chat.completions.create(
            model="llama-3.1-8b-instant",
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
        }
