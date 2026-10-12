"""LangGraph state shared by all agent nodes."""
from typing import Literal, TypedDict


class AgentState(TypedDict, total=False):
    question: str  # the user's original question
    search_query: str  # what we search with (rewritten on retries)
    route: Literal["graph", "vector"]
    context: str
    sources: list[str]
    is_relevant: bool
    retries: int
    answer: str
