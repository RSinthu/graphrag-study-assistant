# Backend

FastAPI + LangChain + LangGraph + Neo4j (Docker) + OpenAI.

## Setup

```bash
cp .env.example .env          # add OPENAI_API_KEY and a NEO4J_PASSWORD (8+ chars)
docker compose up -d          # start Neo4j (browser: http://localhost:7474)
uv sync
uv run uvicorn app.main:app --reload
```

API docs: http://localhost:8000/docs

Without uv: `pip install -r requirements.txt`, then `uvicorn app.main:app --reload`.
After changing dependencies with `uv add`, regenerate it:

```bash
uv export --format requirements-txt --no-dev --no-hashes --no-emit-project --no-annotate -o requirements.txt
```

## Endpoints

| Method | Route | What it does |
|---|---|---|
| `GET` | `/health` | Health check |
| `POST` | `/upload` | Upload a `.pdf`, `.txt` or `.md` file and build the knowledge graph |
| `POST` | `/ask` | Ask a question; the LangGraph agent picks graph or vector search |
| `GET` | `/graph` | Nodes and edges for the graph view |

## How it works

- **Upload (LangChain):** file → chunks → `LLMGraphTransformer` → Neo4j graph.
  Each chunk is stored as a `Document` node linked to its entities, and embedded
  for vector search (`Neo4jVector`).
- **Ask (LangGraph):** `router` → `graph_search` (LLM writes Cypher) or
  `vector_search` → `grade` → `generate`, with a `rewrite` loop when nothing
  useful is found.


