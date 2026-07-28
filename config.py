# ── Shared configuration ──────────────────────────────────────────────────────

EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Module 1 — deduplication
DEDUP_THRESHOLD = 0.80        # cosine similarity >= this => duplicate

# Resource cost factors (published benchmark approximations)
# Assumes dataset is one epoch of a fine-tuning run on A100
GPU_SECONDS_PER_SAMPLE = 0.12     # ~120ms per sample for a 7B model fine-tune pass
KWH_PER_GPU_HOUR       = 0.4      # A100 TDP ~400 W
LITRES_PER_KWH         = 1.8      # Google avg water usage effectiveness
COST_PER_GPU_HOUR      = 2.0      # USD, cloud spot price

# Module 2 — runtime router
DIFFICULTY_THRESHOLD   = 0.4      # score < threshold => route to cheap model
EQUIVALENCE_THRESHOLD  = 0.88     # cosine sim >= this => outputs are equivalent

# Groq models
CHEAP_MODEL            = "llama-3.1-8b-instant"
EXPENSIVE_MODEL        = "llama-3.3-70b-versatile"

COST_CHEAP_PER_1K_TOKENS     = 0.00005   # llama-3.1-8b-instant  (input)
COST_EXPENSIVE_PER_1K_TOKENS = 0.00059   # llama-3.3-70b         (input)

# Paths
import os
ROOT_DIR        = os.path.dirname(__file__)
SAVINGS_FILE    = os.path.join(ROOT_DIR, "savings.json")
RAW_DATASET     = os.path.join(ROOT_DIR, "module1_dedup", "data", "raw_dataset.jsonl")
CLEAN_DATASET   = os.path.join(ROOT_DIR, "module1_dedup", "data", "clean_dataset.jsonl")
TASK_QUEUE      = os.path.join(ROOT_DIR, "module2_router", "tasks", "task_queue.jsonl")
RESULTS_FILE    = os.path.join(ROOT_DIR, "module2_router", "tasks", "results.jsonl")
