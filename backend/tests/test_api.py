"""Tests that run without OpenAI or Neo4j."""
from fastapi.testclient import TestClient

from app.agent.graph import get_agent
from app.agent.nodes import decide_after_grade
from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_upload_rejects_unsupported_file_type():
    response = client.post("/upload", files={"file": ("notes.docx", b"hello")})
    assert response.status_code == 400


def test_ask_rejects_empty_question():
    response = client.post("/ask", json={"question": ""})
    assert response.status_code == 422


def test_agent_compiles_with_expected_nodes():
    nodes = set(get_agent().get_graph().nodes)
    assert {"router", "graph_search", "vector_search", "grade", "rewrite", "generate"} <= nodes


def test_decide_after_grade():
    assert decide_after_grade({"is_relevant": True, "retries": 0}) == "generate"
    assert decide_after_grade({"is_relevant": False, "retries": 0}) == "rewrite"
    assert decide_after_grade({"is_relevant": False, "retries": 2}) == "generate"
