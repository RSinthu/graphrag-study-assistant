"""LangGraph nodes: router, graph_search, vector_search, grade, rewrite, generate."""
from typing import Literal

from neo4j.exceptions import ClientError
from pydantic import BaseModel, Field

from app.agent.state import AgentState
from app.config import get_settings
from app.services.graph_store import get_cypher_chain
from app.services.llm import get_llm
from app.services.vector_store import search_chunks

ROUTER_PROMPT = (
    "You route questions about a student's study notes to a search method.\n"
    "- 'graph': questions about relationships or connections between concepts, "
    "people, or things (e.g. 'How is X related to Y?', 'What does X depend on?').\n"
    "- 'vector': questions asking for definitions, explanations, or summaries "
    "(e.g. 'What is X?', 'Explain X')."
)

GRADER_PROMPT = (
    "Decide whether the retrieved context contains enough information to answer "
    "the question. Answer true only if it is relevant and useful."
)

REWRITE_PROMPT = (
    "The previous search found nothing useful. Rewrite the question so it is "
    "clearer and uses the key terms likely to appear in study notes. "
    "Return only the rewritten question."
)

ANSWER_PROMPT = (
    "You are a helpful study assistant. Answer the question using only the "
    "context below. If the context does not contain the answer, say you could "
    "not find it in the uploaded notes. Keep the answer short and clear."
)


class RouteDecision(BaseModel):
    route: Literal["graph", "vector"] = Field(description="Which search method to use.")


class ContextGrade(BaseModel):
    is_relevant: bool = Field(description="True if the context can answer the question.")


def route_question(state: AgentState) -> AgentState:
    router = get_llm().with_structured_output(RouteDecision)
    decision = router.invoke([("system", ROUTER_PROMPT), ("human", state["search_query"])])
    return {"route": decision.route}


def graph_search(state: AgentState) -> AgentState:
    try:
        result = get_cypher_chain().invoke({"query": state["search_query"]})
    except ClientError:  # the generated Cypher was invalid - treat as "nothing found"
        return {"context": "", "sources": []}
    cypher = result["intermediate_steps"][0]["query"]
    rows = result["result"]
    return {
        "context": "\n".join(str(row) for row in rows),
        "sources": [f"Cypher: {cypher}"] if rows else [],
    }


def vector_search(state: AgentState) -> AgentState:
    docs = search_chunks(state["search_query"], k=get_settings().vector_top_k)
    sources = []
    for doc in docs:
        page = doc.metadata.get("page")
        name = doc.metadata.get("source") or "unknown"
        sources.append(f"{name} (page {page})" if page else name)
    return {
        "context": "\n\n".join(doc.page_content for doc in docs),
        "sources": list(dict.fromkeys(sources)),  # dedupe, keep order
    }


def grade_context(state: AgentState) -> AgentState:
    if not state.get("context", "").strip():
        return {"is_relevant": False}
    grader = get_llm().with_structured_output(ContextGrade)
    grade = grader.invoke([
        ("system", GRADER_PROMPT),
        ("human", f"Question: {state['question']}\n\nContext:\n{state['context']}"),
    ])
    return {"is_relevant": grade.is_relevant}


def rewrite_question(state: AgentState) -> AgentState:
    message = get_llm().invoke([
        ("system", REWRITE_PROMPT),
        ("human", f"Original question: {state['question']}\nLast search: {state['search_query']}"),
    ])
    return {"search_query": message.text.strip(), "retries": state.get("retries", 0) + 1}


def generate_answer(state: AgentState) -> AgentState:
    context = state.get("context") or "No relevant information was found."
    message = get_llm().invoke([
        ("system", ANSWER_PROMPT),
        ("human", f"Question: {state['question']}\n\nContext:\n{context}"),
    ])
    return {"answer": message.text}


def decide_after_grade(state: AgentState) -> Literal["generate", "rewrite"]:
    if state.get("is_relevant") or state.get("retries", 0) >= get_settings().max_retries:
        return "generate"
    return "rewrite"
