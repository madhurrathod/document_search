import json
import os
from typing import List

import faiss
import numpy as np

INDEX_PATH = "storage/faiss.index"
MAPPING_PATH = "storage/faiss.mapping.json"

class FaissSearchService:
    def __init__(self, dimension: int):
        self.dimension = dimension
        os.makedirs("storage", exist_ok=True)
        self.index = self._load_or_create_index()
        self.mapping = self._load_mapping()

    def _load_or_create_index(self):
        if os.path.exists(INDEX_PATH):
            try:
                return faiss.read_index(INDEX_PATH)
            except Exception:
                if os.path.exists(INDEX_PATH):
                    os.remove(INDEX_PATH)
                return faiss.IndexFlatIP(self.dimension)
        return faiss.IndexFlatIP(self.dimension)

    def _load_mapping(self):
        if os.path.exists(MAPPING_PATH):
            try:
                with open(MAPPING_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                if os.path.exists(MAPPING_PATH):
                    os.remove(MAPPING_PATH)
                return []
        return []

    def _save_index(self):
        faiss.write_index(self.index, INDEX_PATH)

    def _save_mapping(self):
        with open(MAPPING_PATH, "w", encoding="utf-8") as f:
            json.dump(self.mapping, f, indent=2)

    def add_embeddings(self, chunk_ids: List[int], embeddings: np.ndarray):
        if embeddings.size == 0 or not chunk_ids:
            return

        if len(chunk_ids) != len(embeddings):
            raise ValueError("chunk_ids and embeddings length mismatch")

        faiss.normalize_L2(embeddings)
        self.index.add(embeddings)

        for chunk_id in chunk_ids:
            self.mapping.append(chunk_id)

        self._save_index()
        self._save_mapping()

    def search(self, query_embedding: np.ndarray, top_k: int = 5):
        if self.index.ntotal == 0:
            return []

        faiss.normalize_L2(query_embedding)
        scores, indices = self.index.search(query_embedding, top_k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue
            if idx >= len(self.mapping):
                continue

            results.append(
                {
                    "chunk_id": self.mapping[idx],
                    "score": float(score),
                }
            )
        return results