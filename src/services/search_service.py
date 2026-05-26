from collections import defaultdict

from db.db_service import get_chunk_results_by_ids
from services.embedding_service import EmbeddingService
from services.faiss_search_service import FaissSearchService


class SearchService:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.embedding_service = EmbeddingService(model_name=model_name)
        sample_embedding = self.embedding_service.embed_query("test")
        self.faiss_service = FaissSearchService(dimension=sample_embedding.shape[1])

    def search(self, query: str, top_k: int = 5):
        query = query.strip()
        if not query:
            return []

        query_embedding = self.embedding_service.embed_query(query)
        matches = self.faiss_service.search(query_embedding, top_k=top_k)

        if not matches:
            return []

        chunk_ids = [match["chunk_id"] for match in matches]
        chunk_rows = get_chunk_results_by_ids(chunk_ids)

        row_map = {row["chunk_id"]: row for row in chunk_rows}
        results = []

        for match in matches:
            row = row_map.get(match["chunk_id"])
            if not row:
                continue

            text = row["text"].strip()
            snippet = text[:300] + "..." if len(text) > 300 else text

            results.append(
                {
                    "chunk_id": row["chunk_id"],
                    "document_id": row["document_id"],
                    "filename": row["filename"],
                    "page_number": row["page_number"],
                    "cloudinary_url": row["cloudinary_url"],
                    "cloudinary_public_id": row["cloudinary_public_id"],
                    "text": text,
                    "snippet": snippet,
                    "score": float(match["score"]),
                }
            )

        return results

    def search_for_rag(self, query: str, top_k: int = 8, min_score: float = 0.5):
        results = self.search(query, top_k=top_k)

        if not results:
            return []

        filtered_results = [
            result for result in results
            if result["score"] >= min_score
        ]

        if not filtered_results:
            return []

        grouped_by_document = defaultdict(list)
        for result in filtered_results:
            grouped_by_document[result["document_id"]].append(result)

        ranked_documents = []
        for document_id, chunks in grouped_by_document.items():
            chunks = sorted(chunks, key=lambda item: item["score"], reverse=True)
            best_score = chunks[0]["score"]
            avg_score = sum(chunk["score"] for chunk in chunks) / len(chunks)

            ranked_documents.append(
                {
                    "document_id": document_id,
                    "filename": chunks[0]["filename"],
                    "cloudinary_url": chunks[0]["cloudinary_url"],
                    "best_score": best_score,
                    "avg_score": avg_score,
                    "match_count": len(chunks),
                    "chunks": chunks,
                }
            )

        ranked_documents.sort(
            key=lambda doc: (doc["best_score"], doc["avg_score"], doc["match_count"]),
            reverse=True,
        )

        return ranked_documents
