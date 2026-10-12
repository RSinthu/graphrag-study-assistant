"""Vector index over the source chunks (Document nodes) stored in Neo4j."""
from functools import lru_cache

from langchain_core.documents import Document
from langchain_neo4j import Neo4jVector

from app.services.graph_store import get_graph
from app.services.llm import get_embeddings

INDEX_NAME = "document_embeddings"

# Return clean chunk text plus a small metadata dict instead of every node property.
RETRIEVAL_QUERY = (
    "RETURN node.text AS text, score, "
    "{source: node.source, page: node.page} AS metadata"
)


@lru_cache
def get_vector_store() -> Neo4jVector:
    # from_existing_graph creates the index if missing and embeds any
    # Document node that doesn't have an embedding yet.
    return Neo4jVector.from_existing_graph(
        embedding=get_embeddings(),
        graph=get_graph(),
        node_label="Document",
        text_node_properties=["text"],
        embedding_node_property="embedding",
        index_name=INDEX_NAME,
        retrieval_query=RETRIEVAL_QUERY,
    )


def embed_new_chunks() -> None:
    get_vector_store.cache_clear()
    get_vector_store()


def search_chunks(query: str, k: int) -> list[Document]:
    return get_vector_store().similarity_search(query, k=k)
