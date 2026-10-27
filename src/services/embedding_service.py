import numpy as np
import streamlit as st
from sentence_transformers import SentenceTransformer

DEFAULT_MODEL = "all-MiniLM-L6-v2"


@st.cache_resource(show_spinner="Loading embedding model...")
def _load_model(model_name: str) -> SentenceTransformer:
    # Streamlit reruns the whole script on every interaction. Without this
    # cache the ~90 MB model was reloaded on every search and upload (twice
    # per RAG question). cache_resource keeps one copy per server process.
    return SentenceTransformer(model_name)


class EmbeddingService:
    def __init__(self, model_name: str = DEFAULT_MODEL):
        self.model = _load_model(model_name)

    @property
    def max_tokens(self) -> int:
        # all-MiniLM-L6-v2 silently truncates anything past 256 word pieces.
        return self.model.max_seq_length

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
