import uuid
from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.db.artifact_repository import sanitize_html
from app.agent.service import format_history

client = TestClient(app)


def test_health_endpoints():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "provider" in data

    readiness_response = client.get("/health/ready")
    assert readiness_response.status_code == 200
    rdata = readiness_response.json()
    assert "status" in rdata
    assert "database" in rdata


def test_session_lifecycle():
    # 1. Create Session
    create_res = client.post("/api/sessions")
    assert create_res.status_code == 200
    session = create_res.json()
    session_id = session["id"]
    assert session_id is not None

    # 2. Get Session
    get_res = client.get(f"/api/sessions/{session_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == session_id

    # 3. Non-existent Session
    fake_id = str(uuid.uuid4())
    fake_res = client.get(f"/api/sessions/{fake_id}")
    assert fake_res.status_code == 404
    err = fake_res.json()["error"]
    assert err["code"] == "SESSION_NOT_FOUND"


def test_html_sanitization():
    unsafe_html = "<div><h1>Title</h1><script>alert('hack');</script><button onclick='doBad()'>Click</button><a href='javascript:void(0)'>Link</a></div>"
    clean = sanitize_html(unsafe_html)
    assert "<script>" not in clean
    assert "onclick" not in clean
    assert "javascript:" not in clean
    assert "<h1>Title</h1>" in clean


def test_history_formatting():
    history = [
        {"role": "user", "content": "How do we improve activation?"},
        {"role": "assistant", "content": "Focus on early user onboarding steps."},
    ]
    formatted = format_history(history)
    assert "User: How do we improve activation?" in formatted
    assert "Assistant: Focus on early user onboarding steps." in formatted


@patch("app.agent.service.generate_llm_response")
def test_message_flow_grounded(mock_llm):
    mock_llm.return_value = "Test grounded answer based on transcripts."
    
    # Create session
    create_res = client.post("/api/sessions")
    session_id = create_res.json()["id"]

    # Post message
    res = client.post(
        f"/api/sessions/{session_id}/messages",
        json={"role": "user", "content": "How can we improve product retention?"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["grounded"] is True
    assert "sources" in data
    assert len(data["sources"]) > 0
    assert data["assistant_message"]["content"] == "Test grounded answer based on transcripts."


@patch("app.agent.service.generate_llm_response")
def test_ship30_endpoint(mock_llm):
    mock_llm.return_value = "# Strong Hook\n\nSample Ship30 essay content (~1250 words)."

    create_res = client.post("/api/sessions")
    session_id = create_res.json()["id"]

    res = client.post(
        f"/api/sessions/{session_id}/ship30",
        json={"topic": "Product activation strategies"},
    )
    assert res.status_code == 200
    data = res.json()
    assert "content" in data
    assert data["grounded"] is True
    assert "# Strong Hook" in data["content"]


@patch("app.agent.service.generate_llm_response")
def test_artifact_endpoint(mock_llm):
    mock_llm.return_value = "# Growth Framework\n- Step 1: Onboarding\n- Step 2: Retention"

    create_res = client.post("/api/sessions")
    session_id = create_res.json()["id"]

    res = client.post(
        f"/api/sessions/{session_id}/artifacts",
        json={"title": "Growth Framework", "type": "markdown"},
    )
    assert res.status_code == 200
    data = res.json()
    artifact_id = data["id"]
    assert data["title"] == "Growth Framework"
    assert data["type"] == "markdown"
    assert "# Growth Framework" in data["content"]

    # Retrieve artifact
    get_res = client.get(f"/api/artifacts/{artifact_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == artifact_id
