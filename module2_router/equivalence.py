"""
equivalence.py
Checks whether two model outputs are semantically equivalent
using cosine similarity on their embeddings.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from module1_dedup.embedder import embed
from module1_dedup.similarity import cosine_sim
from config import EQUIVALENCE_THRESHOLD


def is_equivalent(
    output_a: str,
    output_b: str,
    prompt: str = "",
    threshold: float = EQUIVALENCE_THRESHOLD,
) -> tuple[bool, float]:
    """
    Compare two outputs.

    Parameters
    ----------
    output_a, output_b : the two texts to compare
    prompt             : optional — prepended to very short outputs to add context
    threshold          : cosine similarity threshold

    Returns
    -------
    (equivalent: bool, similarity_score: float)
    """
    # For very short outputs, prepend the prompt to avoid false positives
    def _pad(text: str) -> str:
        return f"{prompt} {text}".strip() if len(text.split()) < 5 and prompt else text

    embs = embed([_pad(output_a), _pad(output_b)])
    sim  = cosine_sim(embs[0], embs[1])
    return sim >= threshold, round(sim, 4)
