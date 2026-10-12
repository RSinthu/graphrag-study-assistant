"""POST /ask - run the LangGraph agent on a question."""
from fastapi import APIRouter

from app.agent.graph import get_agent
from app.schemas.models import AskRequest, AskResponse

router = APIRouter(tags=["ask"])


@router.post("/ask", response_model=AskResponse)
def ask(request: AskRequest) -> AskResponse:
    state = get_agent().invoke(
        {"question": request.question, "search_query": request.question, "retries": 0}
    )
    return AskResponse(
        answer=state["answer"],
        route=state["route"],
        sources=state.get("sources", []),
        retries=state["retries"],
    )
