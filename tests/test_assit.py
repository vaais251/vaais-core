from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_assist_valid_request(monkeypatch):
    monkeypatch.setenv("PROVIDER_MODE", "mock")
    monkeypatch.setenv("GEMINI_API_KEY", "")

    payload = {
        "inquiry_text": (
            "We are 4 travelers planning "
            "a 10-day trip to Skardu."
        ),
        "offering_id": "104",
    }

    response = client.post("/assist", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data["answer"], str)
    assert data["needs_review"] is True
    assert data["parsed_fields"]["price"] is None
    assert data["tool_summary"]["agent_status"] == "not_run"
    assert data["request_id"]
