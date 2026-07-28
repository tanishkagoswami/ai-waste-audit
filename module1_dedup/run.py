"""
run.py  —  Module 1 CLI entry point
Usage:  python module1_dedup/run.py [--threshold 0.92]
"""
import argparse
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dedup import run

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deduplicate a JSONL dataset.")
    parser.add_argument(
        "--threshold", type=float, default=None,
        help="Cosine similarity threshold (default: from config.py)"
    )
    args = parser.parse_args()

    kwargs = {}
    if args.threshold is not None:
        kwargs["threshold"] = args.threshold

    run(**kwargs)
