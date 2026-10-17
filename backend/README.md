# GraphRAG Study Assistant — Backend

FastAPI · LangChain · LangGraph · Neo4j (Docker) · OpenAI

## Tech Stack

| Layer | Library / Tool |
|---|---|
| Web framework | FastAPI + Uvicorn |
| LLM & embeddings | `langchain-openai` (configurable model) |
| Knowledge graph | `langchain-neo4j` · Neo4j 2026.09 + APOC |
| Graph ingestion | `LLMGraphTransformer` + `Neo4jVector` |
| Agent | LangGraph `StateGraph` |
| Text splitting | `langchain-text-splitters` |
| PDF parsing | `pypdf` |
| Config | `pydantic-settings` (`.env`) |
| Python | >= 3.12 |

---

## Project Structure

```
backend/
├── app/
│   ├── main.py            # FastAPI app, CORS, error handlers
│   ├── config.py          # Settings loaded from .env (pydantic-settings)
│   ├── api/routes/
│   │   ├── upload.py      # POST /upload
│   │   ├── ask.py         # POST /ask
│   │   └── graph.py       # GET  /graph
│   ├── agent/
│   │   ├── graph.py       # LangGraph workflow (compiled, cached)
│   │   ├── nodes.py       # router, graph_search, vector_search, grade, rewrite, generate
│   │   └── state.py       # AgentState TypedDict
│   └── services/
│       ├── ingestion.py   # File → chunks → Neo4j graph + vector index
│       ├── graph_store.py # Neo4jGraph helpers, Cypher chain
│       ├── vector_store.py# Neo4jVector similarity search
│       └── llm.py         # Shared LLM singleton
├── tests/
│   └── test_api.py        # Unit / integration tests (no OpenAI/Neo4j required)
├── docker-compose.yml     # Neo4j service
├── .env.example           # Required environment variables
├── pyproject.toml
└── requirements.txt
```

---

## Quick Start

### 1 · Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (for Neo4j)
- Python >= 3.12
- [uv](https://docs.astral.sh/uv/) *(recommended)* **or** pip

### 2 · Environment

```bash
cp .env.example .env
```

Open `.env` and fill in the required values:

| Variable | Required | Default | Description |
|---|---|---|---|
| `OPENAI_API_KEY` | yes | — | Your OpenAI secret key |
| `NEO4J_PASSWORD` | yes | — | Neo4j password (min 8 chars) |
| `LLM_MODEL` | | `gpt-5.4-mini` | OpenAI chat model |
| `EMBEDDING_MODEL` | | `text-embedding-3-small` | OpenAI embedding model |
| `NEO4J_URI` | | `bolt://localhost:7687` | Neo4j Bolt URI |
| `NEO4J_USERNAME` | | `neo4j` | Neo4j username |

### 3 · Start Neo4j

```bash
docker compose up -d
```

- Neo4j Browser: http://localhost:7474
- Bolt port: `7687`

The APOC plugin is loaded automatically (required by LangChain's `Neo4jGraph`).

### 4 · Install dependencies & run

**With uv (recommended):**
```bash
uv sync
uv run uvicorn app.main:app --reload
```

**With pip:**
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API docs: http://localhost:8000/docs

---

## API Reference

| Method | Route | Description |
|---|---|---|
| `GET` | `/health` | Liveness check — returns `{"status": "ok"}` |
| `POST` | `/upload` | Upload a `.pdf`, `.txt`, or `.md` file and build the knowledge graph |
| `POST` | `/ask` | Ask a question; the LangGraph agent routes to graph or vector search |
| `GET` | `/graph?limit=300` | Return nodes and edges for the graph visualisation (max 2000) |

### `POST /upload`

Accepts a multipart file upload. The ingestion pipeline:
1. Chunks the document with configurable `chunk_size` / `chunk_overlap`
2. Extracts entities and relationships via `LLMGraphTransformer` → stored in Neo4j
3. Embeds chunks with `Neo4jVector` for similarity search

Returns `{ filename, nodes_created, relationships_created, chunks }`.

### `POST /ask`

```json
{ "question": "How is attention related to transformers?" }
```

Returns `{ answer, route, sources, retries }`.

### `GET /graph`

Query param `limit` (default `300`, max `2000`) caps the number of nodes returned.

Returns `{ nodes: [...], edges: [...] }`.

---

## How It Works

### Ingestion (LangChain)

```
file → text chunks → LLMGraphTransformer
                           ├─→ Neo4j graph  (entities + relationships)
                           └─→ Neo4jVector  (embeddings for similarity search)
```

Each chunk is stored as a `Document` node linked to the entities extracted from it.

### Agent (LangGraph)

```
START → router ──→ graph_search → grade ──→ generate → END
               └─→ vector_search ↗         ↓ (retry)
                                           rewrite → router
```

| Node | What it does |
|---|---|
| `router` | Classifies the question as `"graph"` (relational) or `"vector"` (definitional) |
| `graph_search` | Asks the LLM to write Cypher; runs it against Neo4j |
| `vector_search` | Embeds the query; retrieves the top-K similar chunks |
| `grade` | Checks whether retrieved context is relevant to the question |
| `rewrite` | Rephrases the question using key terms likely in study notes |
| `generate` | Produces the final answer grounded in the retrieved context |

The `rewrite → router` loop runs up to `max_retries` times (default `2`) before
falling back to generation even without relevant context.

---

## Configuration

All settings live in `app/config.py` and are read from `.env` via `pydantic-settings`.

| Setting | Default | Description |
|---|---|---|
| `chunk_size` | `1000` | Characters per text chunk |
| `chunk_overlap` | `100` | Overlap between adjacent chunks |
| `vector_top_k` | `4` | Number of chunks returned by vector search |
| `max_retries` | `2` | Max question-rewrite iterations before giving up |
| `cors_origins` | `["http://localhost:5174"]` | Allowed CORS origins |
| `upload_dir` | `data/uploads/` | Where uploaded files are saved |

---

## Tests

Tests run without a live OpenAI or Neo4j connection.

```bash
uv run pytest
# or
pytest
```

Covered cases:

- `/health` returns 200
- `/upload` rejects unsupported file types (e.g. `.docx`)
- `/ask` rejects empty questions (422 validation error)
- Agent compiles with the expected nodes
- `decide_after_grade` routing logic

---

## Dependency Management

Dependencies are declared in `pyproject.toml`. After adding or upgrading a package
with `uv add <pkg>`, regenerate `requirements.txt` for pip users:

```bash
uv export --format requirements-txt --no-dev --no-hashes --no-emit-project --no-annotate -o requirements.txt
```
