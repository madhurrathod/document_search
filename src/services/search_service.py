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

        score_map = {match["chunk_id"]: match["score"] for match in matches}
        results = []

        for row in chunk_rows:
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
                    "snippet": snippet,
                    "score": score_map.get(row["chunk_id"], 0.0),
                }
            )

        return results
    
    def search_for_rag(self, query: str, top_k: int = 5, min_score: float = 0.5):
        results = self.search(query, top_k=top_k)

        if not results:
            return []

        filtered_results = [
            result for result in results
            if result["score"] >= min_score
        ]

        return filtered_results
