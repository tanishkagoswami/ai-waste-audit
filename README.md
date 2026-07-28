@"
# AI Waste Audit System

A two-module system that finds and fixes AI resource waste at every stage.

## Modules
- **Module 1** — Semantic deduplication of training datasets using embeddings
- **Module 2** — Autonomous runtime router that routes tasks to cheap vs expensive models and verifies output equivalence

## Setup
\`\`\`
pip install -r requirements.txt
\`\`\`

Create a \`.env\` file with your API key:
\`\`\`
GROQ_API_KEY=gsk_...
\`\`\`

## Run
\`\`\`
# Module 1 standalone
python module1_dedup/run.py

# Module 2 standalone  
python module2_router/run.py

# Full dashboard
uvicorn dashboard.app:app --port 8000
\`\`\`
Then open http://127.0.0.1:8000
"@ | Set-Content README.md