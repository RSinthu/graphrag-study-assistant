"""Neo4j connection, Cypher Q&A chain, and graph data for the React view."""
from functools import lru_cache

from langchain_neo4j import GraphCypherQAChain, Neo4jGraph

from app.config import get_settings
from app.services.llm import get_llm

# Source chunks (Document nodes) and their MENTIONS links are hidden from the
# Cypher-writing LLM so it only queries entities and their relationships.
EXCLUDED_TYPES = ["Document", "MENTIONS"]


class DatabaseUnavailableError(RuntimeError):
    """Raised when Neo4j can't be reached or the login is wrong."""


@lru_cache
def get_graph() -> Neo4jGraph:
    settings = get_settings()
    try:
        return Neo4jGraph(
            url=settings.neo4j_uri,
            username=settings.neo4j_username,
            password=settings.neo4j_password,
        )
    except ValueError as exc:  # Neo4jGraph wraps connection/auth errors in ValueError
        raise DatabaseUnavailableError(str(exc)) from exc


def get_cypher_chain() -> GraphCypherQAChain:
    # Built per call: the chain captures the graph schema when it is created,
    # and the schema changes after every upload.
    return GraphCypherQAChain.from_llm(
        llm=get_llm(),
        graph=get_graph(),
        exclude_types=EXCLUDED_TYPES,
        validate_cypher=True,
        return_direct=True,  # return DB rows; the agent writes the final answer
        return_intermediate_steps=True,
        allow_dangerous_requests=True,  # the LLM writes Cypher - use a read-only user in production
    )


def get_graph_data(limit: int) -> dict:
    graph = get_graph()
    nodes = graph.query(
        "MATCH (n:__Entity__) "
        "RETURN n.id AS id, [l IN labels(n) WHERE l <> '__Entity__'][0] AS type "
        "LIMIT $limit",
        {"limit": limit},
    )
    edges = graph.query(
        "MATCH (a:__Entity__)-[r]->(b:__Entity__) "
        "RETURN a.id AS source, b.id AS target, type(r) AS relation "
        "LIMIT $limit",
        {"limit": limit},
    )
    return {"nodes": nodes, "edges": edges}
