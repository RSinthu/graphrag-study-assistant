"""Builds and compiles the LangGraph workflow.

START -> router -> graph_search | vector_search -> grade
grade -> generate -> END     (context is good, or out of retries)
grade -> rewrite -> router   (context is missing or irrelevant)
"""
from functools import lru_cache

from langgraph.graph import END, START, StateGraph

from app.agent.nodes import (
    decide_after_grade,
    generate_answer,
    grade_context,
    graph_search,
    rewrite_question,
    route_question,
    vector_search,
)
from app.agent.state import AgentState


@lru_cache
def get_agent():
    workflow = StateGraph(AgentState)

    workflow.add_node("router", route_question)
    workflow.add_node("graph_search", graph_search)
    workflow.add_node("vector_search", vector_search)
    workflow.add_node("grade", grade_context)
    workflow.add_node("rewrite", rewrite_question)
    workflow.add_node("generate", generate_answer)

    workflow.add_edge(START, "router")
    workflow.add_conditional_edges(
        "router",
        lambda state: state["route"],
        {"graph": "graph_search", "vector": "vector_search"},
    )
    workflow.add_edge("graph_search", "grade")
    workflow.add_edge("vector_search", "grade")
    workflow.add_conditional_edges(
        "grade", decide_after_grade, {"generate": "generate", "rewrite": "rewrite"}
    )
    workflow.add_edge("rewrite", "router")
    workflow.add_edge("generate", END)

    return workflow.compile()
