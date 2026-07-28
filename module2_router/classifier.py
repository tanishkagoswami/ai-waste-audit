"""
classifier.py
Scores each task's difficulty from 0.0 (trivial) to 1.0 (complex).
Uses two signals:
  1. Embedding distance from known-simple anchor tasks
  2. Token (word) length of the prompt
No ML training required.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
from module1_dedup.embedder import embed

# ── Anchor prompts that represent "simple" tasks ──────────────────────────────
SIMPLE_ANCHORS = [
    "What is 2 + 2?",
    "What is the capital of France?",
    "Translate 'hello' into Spanish.",
    "Give me a synonym for happy.",
    "What colour is the sky?",
    "Convert 100 Fahrenheit to Celsius.",
    "How many days are in a week?",
    "What is the plural of mouse?",
]

_anchor_embeddings: np.ndarray | None = None


def _get_anchor_embeddings() -> np.ndarray:
    global _anchor_embeddings
    if _anchor_embeddings is None:
        _anchor_embeddings = embed(SIMPLE_ANCHORS)
    return _anchor_embeddings


def score_difficulty(task: str) -> float:
    """
    Returns a float in [0.0, 1.0].
    0.0 = very simple (matches anchor examples well)
    1.0 = very complex (far from anchors AND long)
    """
    task_emb = embed([task])[0]          # shape (384,)
    anchors  = _get_anchor_embeddings()  # shape (N, 384)

    # cosine similarities (embeddings are L2-normalised → dot product)
    sims = anchors @ task_emb            # shape (N,)
    max_sim = float(np.max(sims))        # highest similarity to any simple anchor

    # length factor: 0.0 for very short prompts, 1.0 at 200+ words
    word_count    = len(task.split())
    length_factor = min(word_count / 200.0, 1.0)

    # weighted combination: high anchor sim → low difficulty; long text → higher
    score = 1.0 - (0.6 * max_sim + 0.4 * (1.0 - length_factor))
    return round(float(np.clip(score, 0.0, 1.0)), 4)
