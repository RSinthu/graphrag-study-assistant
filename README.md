# ✦ StudyGraph: GraphRAG Study Assistant

Upload your study notes, see them turned into a **knowledge graph**, and ask questions about them.
StudyGraph combines **graph search** (how concepts connect) with **vector search** (what concepts mean),
and uses a **LangGraph agent** to pick the right one for every question.

**Stack:** FastAPI · LangChain · LangGraph · Neo4j · OpenAI · React · Vite

---

## Features

- **Notes → knowledge graph:** PDFs, text and Markdown files are split into chunks, and an LLM extracts
  the concepts and relationships into Neo4j.
- **Hybrid retrieval:** relationship questions use the graph (the LLM writes Cypher queries); descriptive
  questions use vector search over the original text.
- **Self-correcting agent:** the agent checks whether the retrieved context is good enough and rephrases
  the question to try again if it isn't.
- **Star-map UI:** your knowledge graph is drawn as a constellation. Concepts mentioned in an answer light
  up, and clicking a star shows its connections.
- **Transparent answers:** every answer shows which search was used and the sources behind it.

## How it works

```
                     ┌─────────────── Upload (LangChain) ───────────────┐
  PDF / TXT / MD ──► │ split into chunks → LLMGraphTransformer → Neo4j  │
                     │                   → embeddings → Neo4j vector    │
                     └──────────────────────────────────────────────────┘

                     ┌─────────────── Ask (LangGraph) ──────────────────┐
  Question ────────► │ router ─┬─► graph_search (Cypher) ─┐             │
                     │         └─► vector_search ─────────┤             │
                     │                                    ▼             │
                     │                       grade ── good ──► generate ──► Answer
                     │                         │ not enough             │
                     │                         ▼                        │
                     │                      rewrite ──► back to router  │
                     │                      (max 2 retries)             │
                     └──────────────────────────────────────────────────┘
```

Neo4j stores both the graph and the text embeddings, so there is only one database to run.

## Project structure

```
GraphRAG/
├── backend/                  # FastAPI + LangChain + LangGraph
│   ├── app/
│   │   ├── main.py           # FastAPI app, CORS, error handling
│   │   ├── config.py         # settings from .env
│   │   ├── api/routes/       # /upload, /ask, /graph
│   │   ├── schemas/          # request/response models
│   │   ├── services/         # LangChain: LLM, ingestion, Neo4j graph + vector store
│   │   └── agent/            # LangGraph: state, nodes, workflow
│   ├── tests/
│   ├── docker-compose.yml    # Neo4j
│   ├── pyproject.toml        # uv project
│   └── requirements.txt      # pinned, for pip users
└── frontend/                 # React + Vite
    └── src/
        ├── api.js
        ├── App.jsx
        ├── components/       # UploadZone, ChatPanel, GraphView
        └── styles.css
```

## Prerequisites

- [Python](https://www.python.org/) 3.12+ and [uv](https://docs.astral.sh/uv/)
- [Node.js](https://nodejs.org/) 20+
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- An [OpenAI API key](https://platform.openai.com/api-keys)

## Getting started

### 1. Configure

```bash
cd backend
cp .env.example .env
```

Edit `backend/.env` and set at least:

| Variable | Description | Default |
|---|---|---|
| `OPENAI_API_KEY` | Your OpenAI API key | (required) |
| `NEO4J_PASSWORD` | Password for Neo4j (8+ characters) | (required) |
| `LLM_MODEL` | Chat model | `gpt-5.4-mini` |
| `EMBEDDING_MODEL` | Embedding model | `text-embedding-3-small` |
| `NEO4J_URI` | Neo4j connection | `bolt://localhost:7687` |
| `NEO4J_USERNAME` | Neo4j user | `neo4j` |

### 2. Start Neo4j

From the `backend` folder:

```bash
docker compose up -d
```

The Neo4j Browser is at http://localhost:7474. Log in with `neo4j` and your password.

### 3. Start the backend

```bash
uv sync
uv run uvicorn app.main:app --reload
```

The API runs at http://localhost:8000, and interactive docs are at http://localhost:8000/docs.

Without uv: `pip install -r requirements.txt`, then `uvicorn app.main:app --reload`.

### 4. Start the frontend

In a new terminal:

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5174.

## Usage

1. **Upload** a PDF, `.txt` or `.md` file in the *Add notes* panel. Building the graph makes one LLM
   call per chunk, so larger files take longer.
2. **Explore** the knowledge sky. Click any star to see how it connects to other concepts.
3. **Ask** questions in the chat, for example:
   - *"What is photosynthesis?"* → 📄 Note search
   - *"How is chlorophyll connected to glucose?"* → 🔗 Graph search

## API

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `POST` | `/upload` | Upload a file (`multipart/form-data`, field `file`) and build the graph |
| `POST` | `/ask` | `{"question": "..."}` → `{answer, route, sources, retries}` |
| `GET` | `/graph?limit=300` | Nodes and edges for visualisation |

## Tests

```bash
cd backend
uv run pytest
```

The tests run without OpenAI or Neo4j.

## Troubleshooting

| Problem | Fix |
|---|---|
| *"Neo4j is unavailable"* (503) | Start Docker Desktop and run `docker compose up -d` in `backend/`. |
| *"The backend isn't responding"* in the UI | Start the backend on port 8000. |
| APOC procedure errors | The Docker setup enables APOC. If you use your own Neo4j, install the APOC plugin. |
| `uv` not found on Windows | Run it as `python -m uv ...`, or add Python's `Scripts` folder to `PATH`. |

## Notes

- `GraphCypherQAChain` runs LLM-generated Cypher against the database. For anything beyond local use,
  connect with a **read-only** Neo4j user.
- Uploaded files are saved in `backend/data/uploads/` (git-ignored).

## Roadmap

- [ ] Chat memory across questions (LangGraph checkpointer)
- [ ] "Both" route that combines graph and vector results
- [ ] Merge duplicate entities (e.g. "Elon" / "Elon Musk")
- [ ] Streaming answers
