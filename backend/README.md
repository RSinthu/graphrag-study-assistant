# Backend

FastAPI + LangChain + LangGraph + Neo4j.

## Setup

```bash
uv sync
cp .env.example .env   # fill in keys
uv run uvicorn app.main:app --reload
```

Health check: http://localhost:8000/health
