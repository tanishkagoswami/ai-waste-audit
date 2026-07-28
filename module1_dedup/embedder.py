"""
embedder.py
Loads the embedding model once and exposes a single embed() function.
Used by both Module 1 (dedup) and Module 2 (difficulty scoring + equivalence).
"""
import numpy as np
from sentence_transformers import SentenceTransformer
from config import EMBEDDING_MODEL

_model: SentenceTransformer | None = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model


def embed(texts: list[str], batch_size: int = 64, show_progress: bool = False) -> np.ndarray:
    """
    Encode a list of strings into L2-normalised embeddings.
    Returns ndarray of shape (len(texts), 384).
    """
    model = _get_model()
    vectors = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=show_progress,
        normalize_embeddings=True,   # L2-normalise so dot product == cosine sim
    )
    return np.array(vectors, dtype=np.float32)
