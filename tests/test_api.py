from fastapi.testclient import TestClient
from unittest.mock import patch

from app.main import app


def test_health():
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


def test_chat_contract():
    fake_result = {
        "answer": "The eBook describes perception, reasoning, planning, learning, verification and execution.",
        "confidence_score": 0.91,
        "grounded": True,
        "retrieved": [
            {"page": 19, "score": 0.91, "text": "Core pillars...", "source": "ebook", "chunk_id": "x"}
        ],
    }

    fake_rag = type("FakeRAG", (), {"invoke": lambda self, q: fake_result})()

    with patch("app.main.rag", fake_rag):
        with TestClient(app) as client:
            response = client.post("/chat", json={"question": "What are the core pillars?"})

    assert response.status_code == 200
    body = response.json()
    assert body["grounded"] is True
    assert body["confidence_score"] == 0.91
    assert body["retrieved_context"][0]["page"] == 19
