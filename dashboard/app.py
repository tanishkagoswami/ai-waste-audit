from dotenv import load_dotenv
import os as _os
# Always find .env relative to this file (ai-waste-audit/) regardless of cwd
load_dotenv(_os.path.join(_os.path.dirname(__file__), "..", ".env"))

"""
app.py — FastAPI dashboard backend
Endpoints:
  GET  /api/summary          → full savings_store dict
  GET  /api/module2/tasks    → per-task audit log
  POST /api/run/dedup        → trigger Module 1
  POST /api/run/pipeline     → trigger Module 2
  GET  /                     → serve index.html
"""
import json
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

import savings_store
from config import RESULTS_FILE

app = FastAPI(title="AI Waste Audit Dashboard")

# Serve static assets
_static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=_static_dir), name="static")


# ── Helper ────────────────────────────────────────────────────────────────────

def _load_results() -> list[dict]:
    if not os.path.exists(RESULTS_FILE):
        return []
    with open(RESULTS_FILE) as f:
        return [json.loads(line) for line in f if line.strip()]


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def index():
    html_path = os.path.join(os.path.dirname(__file__), "index.html")
    with open(html_path, encoding="utf-8") as f:
        return HTMLResponse(content=f.read(), media_type="text/html; charset=utf-8")


@app.get("/api/summary")
async def summary():
    return JSONResponse(content=savings_store.get())


@app.get("/api/module2/tasks")
async def tasks():
    return JSONResponse(content=_load_results())


@app.post("/api/run/dedup")
async def run_dedup():
    """Trigger Module 1 deduplication synchronously."""
    from module1_dedup.dedup import run
    savings = run(show_progress=False)
    return JSONResponse(content=savings)


@app.post("/api/run/pipeline")
async def run_pipeline():
    """Trigger Module 2 autonomous pipeline synchronously."""
    from module2_router.pipeline import run
    snapshot = run(verbose=False)
    return JSONResponse(content=snapshot)


@app.post("/api/reset")
async def reset():
    return JSONResponse(content=savings_store.reset())
