"""
savings_store.py
Single source of truth for all resource savings.
Both modules write here; the dashboard reads from here.
Persists to savings.json after every update.
"""
import json, os
from config import SAVINGS_FILE

_DEFAULTS = {
    # Module 1
    "m1_rows_before":    0,
    "m1_rows_removed":   0,
    "m1_rows_after":     0,
    "m1_gpu_hours":      0.0,
    "m1_kwh":            0.0,
    "m1_litres":         0.0,
    "m1_cost_usd":       0.0,
    # Module 2
    "m2_tasks_audited":  0,
    "m2_tasks_rerouted": 0,
    "m2_escalations":    0,
    "m2_cost_saved_usd": 0.0,
    # Totals
    "total_cost_usd":    0.0,
}


def _load() -> dict:
    if os.path.exists(SAVINGS_FILE):
        with open(SAVINGS_FILE) as f:
            data = json.load(f)
        # backfill any keys added later
        for k, v in _DEFAULTS.items():
            data.setdefault(k, v)
        return data
    return dict(_DEFAULTS)


def _save(data: dict) -> None:
    with open(SAVINGS_FILE, "w") as f:
        json.dump(data, f, indent=2)


def get() -> dict:
    return _load()


def update(patch: dict) -> dict:
    """Merge patch into the store and persist. Returns the updated store."""
    data = _load()
    data.update(patch)
    data["total_cost_usd"] = round(data["m1_cost_usd"] + data["m2_cost_saved_usd"], 4)
    _save(data)
    return data


def reset() -> dict:
    """Wipe the store back to zeros."""
    _save(dict(_DEFAULTS))
    return dict(_DEFAULTS)


# Initialise the file on first import so the dashboard always has something to read
if not os.path.exists(SAVINGS_FILE):
    _save(dict(_DEFAULTS))
