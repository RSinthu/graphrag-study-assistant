"""GET /graph - return nodes and edges for the React graph view."""
from fastapi import APIRouter, Query

from app.schemas.models import GraphResponse
from app.services.graph_store import get_graph_data

router = APIRouter(tags=["graph"])


@router.get("/graph", response_model=GraphResponse)
def read_graph(limit: int = Query(300, ge=1, le=2000)) -> GraphResponse:
    return GraphResponse(**get_graph_data(limit))
