"""FastAPI entry point."""
from fastapi import FastAPI

app = FastAPI(title="GraphRAG Study Assistant")


@app.get("/health")
def health():
    return {"status": "ok"}
