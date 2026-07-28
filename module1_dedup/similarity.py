"""
similarity.py
Cosine similarity helpers and duplicate-index detection.
Because embedder.py already L2-normalises, cosine sim == dot product.
"""
import numpy as np
from config import DEDUP_THRESHOLD


def cosine_matrix(embeddings: np.ndarray) -> np.ndarray:
    """Return (N, N) pairwise cosine similarity matrix."""
    # embeddings are already normalised → dot product == cosine sim
    return embeddings @ embeddings.T


def find_duplicate_indices(embeddings: np.ndarray, threshold: float = DEDUP_THRESHOLD) -> set[int]:
    """
    Return the set of row indices to REMOVE.
    For each cluster of near-duplicates the first occurrence (lowest index) is kept.
    """
    sim = cosine_matrix(embeddings)
    to_remove: set[int] = set()

    for i in range(len(embeddings)):
        if i in to_remove:
            continue
        # find all rows with sim >= threshold (excluding self at diagonal)
        dupes = np.where(sim[i] >= threshold)[0]
        # keep i, remove everything with a higher index
        to_remove.update(int(d) for d in dupes if d > i)

    return to_remove


def cosine_sim(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    """Scalar cosine similarity between two 1-D vectors (need not be normalised)."""
    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(vec_a, vec_b) / (norm_a * norm_b))
