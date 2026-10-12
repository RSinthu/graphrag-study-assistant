"""FastAPI entry point."""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from neo4j.exceptions import ServiceUnavailable

from app.api.routes import ask, graph, upload
from app.config import get_settings
from app.services.graph_store import DatabaseUnavailableError

app = FastAPI(title="GraphRAG Study Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router)
app.include_router(ask.router)
app.include_router(graph.router)


@app.exception_handler(DatabaseUnavailableError)
@app.exception_handler(ServiceUnavailable)
def database_unavailable(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=503,
        content={"detail": f"Neo4j is unavailable. Is the Docker container running? ({exc})"},
    )


@app.get("/health")
def health():
    return {"status": "ok"}
