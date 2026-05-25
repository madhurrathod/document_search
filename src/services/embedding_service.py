from sentence_transformers import SentenceTransformer
import numpy as np

class EmbeddingService:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def embed_texts(self, texts: list[str]) -> np.ndarray:
        if not texts:
            return np.array([], dtype="float32")
        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )
        return embeddings.astype("float32")

    def embed_query(self, query: str) -> np.ndarray:
        embedding = self.model.encode(
            [query],
            normalize_embeddings=True,
            convert_to_numpy=True,
        )
        return embedding.astype("float32")