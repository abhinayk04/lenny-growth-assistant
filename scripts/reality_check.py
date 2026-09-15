#!/usr/bin/env python3
"""
End-to-End Reality Check & Verification Suite for Lenny Growth Assistant.
Tests every assignment requirement against the live FastAPI application.
"""

import sys
import time
from pathlib import Path

# Add backend directory to sys.path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from fastapi.testclient import TestClient
from app.main import app
from app.db.artifact_repository import sanitize_html
from app.agent.pi_runner import run_pi_agent

client = TestClient(app)

results = {}


def run_check(name, check_fn):
    print(f"\n--- Running Check: {name} ---")
    t0 = time.time()
    try:
        details = check_fn()
        latency = time.time() - t0
        results[name] = {
            "status": "PASS",
            "latency_sec": round(latency, 2),
            "details": details,
        }
        print(f"[PASS] ({latency:.2f}s): {details}")
    except Exception as e:
        latency = time.time() - t0
        results[name] = {
            "status": "FAIL",
            "latency_sec": round(latency, 2),
            "error": str(e),
        }
        print(f"[FAIL] ({latency:.2f}s): {e}")



def check_health():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert "provider" in data
    assert "model" in data
    return f"Status: {data['status']}, Provider: {data['provider']}, Model: {data['model']}"


def check_health_ready():
    res = client.get("/health/ready")
    assert res.status_code == 200
    data = res.json()
    assert data["database"] == "connected"
    return f"Status: {data['status']}, Database: {data['database']}"


def check_create_session():
    res = client.post("/api/sessions")
    assert res.status_code == 200
    data = res.json()
    assert "id" in data
    return f"Created Session ID: {data['id']}"


def check_grounded_question():
    # 1. Create Session
    sres = client.post("/api/sessions")
    session_id = sres.json()["id"]

    # 2. Grounded Question
    qres = client.post(
        f"/api/sessions/{session_id}/messages",
        json={"role": "user", "content": "How can we improve retention?"},
    )
    assert qres.status_code == 200
    data = qres.json()
    assert data["grounded"] is True
    assert len(data["sources"]) > 0
    ans = data["assistant_message"]["content"]
    assert len(ans) > 20
    return f"Session: {session_id[:8]}..., Sources: {len(data['sources'])}, Grounded: {data['grounded']}, Answer Preview: '{ans[:80]}...'"


def check_followup_question():
    # 1. Create Session
    sres = client.post("/api/sessions")
    session_id = sres.json()["id"]

    # Turn 1
    client.post(
        f"/api/sessions/{session_id}/messages",
        json={"role": "user", "content": "How can we improve retention?"},
    )

    # Turn 2 (Follow-up)
    qres = client.post(
        f"/api/sessions/{session_id}/messages",
        json={"role": "user", "content": "What about onboarding?"},
    )
    assert qres.status_code == 200
    data = qres.json()
    assert data["grounded"] is True
    ans = data["assistant_message"]["content"]
    return f"Follow-up answered cleanly. Grounded: {data['grounded']}, Answer Preview: '{ans[:80]}...'"


def check_unsupported_question():
    sres = client.post("/api/sessions")
    session_id = sres.json()["id"]

    qres = client.post(
        f"/api/sessions/{session_id}/messages",
        json={"role": "user", "content": "What is the capital of France?"},
    )
    assert qres.status_code == 200
    data = qres.json()
    assert data["grounded"] is False
    ans = data["assistant_message"]["content"]
    assert "couldn't find enough evidence" in ans.lower()
    return f"Correctly refused out-of-domain question. Grounded: False, Message: '{ans}'"


def check_ship30_generation():
    sres = client.post("/api/sessions")
    session_id = sres.json()["id"]

    res = client.post(
        f"/api/sessions/{session_id}/ship30",
        json={"topic": "Product activation principles"},
    )
    assert res.status_code == 200
    data = res.json()
    assert "content" in data
    assert len(data["content"]) > 100
    return f"Ship30 Essay generated. Content Length: {len(data['content'])} characters, Grounded: {data['grounded']}"


def check_artifact_generation_and_retrieval():
    sres = client.post("/api/sessions")
    session_id = sres.json()["id"]

    # Generate
    res = client.post(
        f"/api/sessions/{session_id}/artifacts",
        json={"title": "Retention Matrix", "type": "markdown"},
    )
    assert res.status_code == 200
    data = res.json()
    art_id = data["id"]
    assert data["title"] == "Retention Matrix"

    # Retrieve
    get_res = client.get(f"/api/artifacts/{art_id}")
    assert get_res.status_code == 200
    gdata = get_res.json()
    assert gdata["id"] == art_id
    return f"Artifact Created & Retrieved. ID: {art_id}, Title: {gdata['title']}"


def check_html_sanitization():
    dirty = "<div><h1>Title</h1><script>alert('xss')</script><button onclick='evil()'>Click</button></div>"
    clean = sanitize_html(dirty)
    assert "<script>" not in clean
    assert "onclick" not in clean
    assert "<h1>Title</h1>" in clean
    return f"Unsafe script tags and onclick handlers stripped. Clean output: '{clean}'"


def check_provider_model_display():
    res = client.get("/health")
    data = res.json()
    return f"Active LLM Provider: {data['provider']}, Model Tag: {data['model']}"


def main():
    print("==================================================")
    print("STARTING LENNY GROWTH ASSISTANT E2E REALITY CHECK")
    print("==================================================")

    run_check("1. /health Endpoint", check_health)
    run_check("2. /health/ready Endpoint", check_health_ready)
    run_check("3. Session Creation", check_create_session)
    run_check("4. Grounded Question Q&A", check_grounded_question)
    run_check("5. Multi-Turn Follow-Up", check_followup_question)
    run_check("6. Unsupported Question Gate", check_unsupported_question)
    run_check("7. Ship30 Generation", check_ship30_generation)
    run_check("8. Artifact Generation & Retrieval", check_artifact_generation_and_retrieval)
    run_check("9. HTML Sanitization", check_html_sanitization)
    run_check("10. Provider / Model Display", check_provider_model_display)

    print("\n==================================================")
    print("SUMMARY RESULTS")
    print("==================================================")
    for name, info in results.items():
        print(f"{info['status']} | {name} ({info['latency_sec']}s)")


if __name__ == "__main__":
    main()
