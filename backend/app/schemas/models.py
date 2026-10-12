"""Request/response Pydantic models."""
from typing import Literal

from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    filename: str
    chunks: int
    nodes: int
    relationships: int


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)


class AskResponse(BaseModel):
    answer: str
    route: Literal["graph", "vector"]
    sources: list[str]
    retries: int


class GraphNode(BaseModel):
    id: str
    type: str | None = None


class GraphEdge(BaseModel):
    source: str
    target: str
    relation: str


class GraphResponse(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]
