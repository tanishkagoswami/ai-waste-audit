"""
calculator.py
Converts a count of removed dataset rows into real-world resource savings.
Returns a dict that savings_store.update() can accept directly.
"""
from config import (
    GPU_SECONDS_PER_SAMPLE,
    KWH_PER_GPU_HOUR,
    LITRES_PER_KWH,
    COST_PER_GPU_HOUR,
)


def calculate_savings(rows_before: int, rows_removed: int) -> dict:
    """
    Parameters
    ----------
    rows_before   : total rows in the original dataset
    rows_removed  : number of near-duplicates removed

    Returns
    -------
    dict with m1_* keys ready for savings_store.update()
    """
    gpu_seconds = rows_removed * GPU_SECONDS_PER_SAMPLE
    gpu_hours   = gpu_seconds / 3600
    kwh         = gpu_hours * KWH_PER_GPU_HOUR
    litres      = kwh * LITRES_PER_KWH
    cost_usd    = gpu_hours * COST_PER_GPU_HOUR

    return {
        "m1_rows_before":  rows_before,
        "m1_rows_removed": rows_removed,
        "m1_rows_after":   rows_before - rows_removed,
        "m1_gpu_hours":    round(gpu_hours, 6),
        "m1_kwh":          round(kwh, 6),
        "m1_litres":       round(litres, 6),
        "m1_cost_usd":     round(cost_usd, 6),
    }
