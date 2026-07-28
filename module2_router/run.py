from dotenv import load_dotenv
load_dotenv()

"""
run.py  —  Module 2 CLI entry point
Usage:  python module2_router/run.py [--quiet]
"""
import argparse
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from pipeline import run

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the autonomous task router pipeline.")
    parser.add_argument("--quiet", action="store_true", help="Suppress per-task output.")
    args = parser.parse_args()

    run(verbose=not args.quiet)
