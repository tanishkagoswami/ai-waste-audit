"""
dedup.py
Orchestrates the full deduplication pipeline:
  load raw_dataset  →  embed  →  find duplicates  →  write clean_dataset  →  calculate savings
"""
import json
import sys
import os

# make root importable when running from inside module1_dedup/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from embedder import embed
from similarity import find_duplicate_indices
from calculator import calculate_savings
import savings_store
from config import RAW_DATASET, CLEAN_DATASET, DEDUP_THRESHOLD


def load_jsonl(path: str) -> list[dict]:
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def save_jsonl(records: list[dict], path: str) -> None:
    with open(path, "w") as f:
        for record in records:
            f.write(json.dumps(record) + "\n")


def run(threshold: float = DEDUP_THRESHOLD, show_progress: bool = True) -> dict:
    """
    Full dedup run. Returns the savings dict written to the store.
    """
    print(f"[M1] Loading dataset from {RAW_DATASET} …")
    records = load_jsonl(RAW_DATASET)
    if not records:
        print("[M1] Dataset is empty — nothing to deduplicate.")
        return {}

    texts = [r.get("text", "") for r in records]
    rows_before = len(texts)
    print(f"[M1] {rows_before} rows loaded. Embedding …")

    embeddings = embed(texts, show_progress=show_progress)
    print(f"[M1] Embeddings done. Finding duplicates (threshold={threshold}) …")

    dup_indices = find_duplicate_indices(embeddings, threshold)
    rows_removed = len(dup_indices)

    clean_records = [r for i, r in enumerate(records) if i not in dup_indices]
    save_jsonl(clean_records, CLEAN_DATASET)

    savings = calculate_savings(rows_before, rows_removed)
    savings_store.update(savings)

    print(f"[M1] Done.")
    print(f"     Before : {rows_before} rows")
    print(f"     Removed: {rows_removed} duplicates")
    print(f"     After  : {savings['m1_rows_after']} rows")
    print(f"     Saved  : ${savings['m1_cost_usd']:.4f}  |  "
          f"{savings['m1_gpu_hours']:.4f} GPU-hrs  |  "
          f"{savings['m1_kwh']:.4f} kWh  |  "
          f"{savings['m1_litres']:.4f} L water")
    return savings
