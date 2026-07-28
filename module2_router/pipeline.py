"""
pipeline.py
Autonomous loop: reads tasks → scores → routes → verifies → logs.
Writes per-task audit records to results.jsonl and cumulative savings to savings_store.
"""
import json
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from classifier  import score_difficulty
from router      import route
from equivalence import is_equivalent
import savings_store
from config import TASK_QUEUE, RESULTS_FILE, CHEAP_MODEL


def load_tasks(path: str = TASK_QUEUE) -> list[dict]:
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def _append_result(record: dict, path: str = RESULTS_FILE) -> None:
    with open(path, "a") as f:
        f.write(json.dumps(record) + "\n")


def run(verbose: bool = True) -> dict:
    """
    Runs the full autonomous pipeline over every task in task_queue.jsonl.
    Returns the final savings snapshot.
    """
    # Clear previous results
    open(RESULTS_FILE, "w").close()

    tasks = load_tasks()
    if not tasks:
        print("[M2] Task queue is empty.")
        return {}

    audited   = 0
    rerouted  = 0
    escalated = 0
    cost_saved = 0.0

    for task in tasks:
        prompt = task.get("prompt", task.get("text", ""))
        task_id = task.get("id", audited + 1)

        # 1. Score difficulty
        difficulty = score_difficulty(prompt)

        # 2. Route: get both model outputs
        result = route(prompt, difficulty)

        # 3. Equivalence check
        equivalent, sim_score = is_equivalent(
            result["cheap_output"],
            result["expensive_output"],
            prompt=prompt,
        )

        # 4. Decide adopted output and log savings
        if equivalent:
            adopted       = CHEAP_MODEL
            saved         = result["expensive_cost"]  # avoided the expensive call
            cost_saved   += saved
            rerouted     += 1
            decision_note = "cheap adopted - outputs equivalent"
        else:
            adopted       = result["primary_model"]
            saved         = 0.0
            escalated    += 1
            decision_note = "expensive retained - outputs differ"

        audited += 1

        record = {
            "id":             task_id,
            "prompt":         prompt[:120],
            "difficulty":     difficulty,
            "primary_model":  result["primary_model"],
            "similarity":     sim_score,
            "equivalent":     equivalent,
            "adopted":        adopted,
            "cost_saved_usd": round(saved, 6),
            "note":           decision_note,
        }
        _append_result(record)

        if verbose:
            flag = "REROUTED " if equivalent else "ESCALATED"
            print(f"  [{flag}] task {task_id:>3} | diff={difficulty:.2f} | "
                  f"sim={sim_score:.3f} | saved=${saved:.5f} | {decision_note}")

    # Write cumulative M2 savings
    savings_store.update({
        "m2_tasks_audited":  audited,
        "m2_tasks_rerouted": rerouted,
        "m2_escalations":    escalated,
        "m2_cost_saved_usd": round(cost_saved, 6),
    })

    snapshot = savings_store.get()
    print(f"\n[M2] Done. {audited} tasks audited | "
          f"{rerouted} rerouted | {escalated} escalated | "
          f"${cost_saved:.5f} saved")
    return snapshot
