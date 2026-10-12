"""Upload pipeline: file -> chunks -> knowledge graph + embeddings in Neo4j."""
from pathlib import Path

from langchain_core.documents import Document
from langchain_neo4j import LLMGraphTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

from app.config import get_settings
from app.services.graph_store import get_graph
from app.services.llm import get_llm
from app.services.vector_store import embed_new_chunks

SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md"}


def load_file(path: Path) -> list[Document]:
    if path.suffix.lower() == ".pdf":
        reader = PdfReader(path)
        return [
            Document(page_content=page.extract_text() or "", metadata={"source": path.name, "page": number})
            for number, page in enumerate(reader.pages, start=1)
        ]
    text = path.read_text(encoding="utf-8")
    return [Document(page_content=text, metadata={"source": path.name})]


def ingest_file(path: Path) -> dict:
    settings = get_settings()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size, chunk_overlap=settings.chunk_overlap
    )
    chunks = [c for c in splitter.split_documents(load_file(path)) if c.page_content.strip()]
    if not chunks:
        raise ValueError("No readable text found in the file.")

    # One LLM call per chunk: extract entities and relationships.
    graph_documents = LLMGraphTransformer(llm=get_llm()).convert_to_graph_documents(chunks)

    graph = get_graph()
    # include_source links each entity to the chunk (Document node) it came from.
    graph.add_graph_documents(graph_documents, baseEntityLabel=True, include_source=True)
    graph.refresh_schema()
    embed_new_chunks()

    return {
        "chunks": len(chunks),
        "nodes": sum(len(d.nodes) for d in graph_documents),
        "relationships": sum(len(d.relationships) for d in graph_documents),
    }
