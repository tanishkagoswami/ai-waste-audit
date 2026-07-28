"""
router.py
Calls Groq models (llama-3.1-8b-instant = cheap, llama-3.3-70b-versatile = expensive).
Falls back to mock responses when GROQ_API_KEY is not set.
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from config import (
    CHEAP_MODEL, EXPENSIVE_MODEL,
    DIFFICULTY_THRESHOLD,
    COST_CHEAP_PER_1K_TOKENS,
    COST_EXPENSIVE_PER_1K_TOKENS,
)

# ── Groq client ───────────────────────────────────────────────────────────────
_client = None
try:
    from groq import Groq
    _api_key = os.getenv("GROQ_API_KEY", "")
    if _api_key:
        _client = Groq(api_key=_api_key)
except Exception:
    pass


def _call_model(model: str, prompt: str) -> tuple[str, int]:
    """Returns (response_text, token_count). Falls back to mock if no client."""
    if _client is None:
        return f"[MOCK {model}] Answer to: {prompt[:60]}", len(prompt.split()) + 10

    try:
        response = _client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=512,
        )
        text   = response.choices[0].message.content or ""
        tokens = response.usage.total_tokens if response.usage else len(text.split())
        return text, tokens
    except Exception as e:
        print(f"  [WARN] Groq call failed ({model}): {e} - using mock.")
        return f"[MOCK {model}] Answer to: {prompt[:60]}", len(prompt.split()) + 10


def _token_cost(tokens: int, model: str) -> float:
    rate = COST_EXPENSIVE_PER_1K_TOKENS if model == EXPENSIVE_MODEL else COST_CHEAP_PER_1K_TOKENS
    return round((tokens / 1000.0) * rate, 6)


def route(task_prompt: str, difficulty_score: float) -> dict:
    """
    Run the task through both models and return a result dict.
    """
    cheap_out,     cheap_tokens     = _call_model(CHEAP_MODEL,     task_prompt)
    expensive_out, expensive_tokens = _call_model(EXPENSIVE_MODEL, task_prompt)

    return {
        "cheap_output":     cheap_out,
        "expensive_output": expensive_out,
        "primary_model":    CHEAP_MODEL if difficulty_score < DIFFICULTY_THRESHOLD else EXPENSIVE_MODEL,
        "cheap_cost":       _token_cost(cheap_tokens,     CHEAP_MODEL),
        "expensive_cost":   _token_cost(expensive_tokens, EXPENSIVE_MODEL),
    }
