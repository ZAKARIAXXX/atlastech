import uuid

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_list_incidents_empty():
    response = client.get("/api/v1/incidents/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_incident():
    payload = {
        "title": f"Test Incident {uuid.uuid4().hex[:8]}",
        "description": "Automated test incident for validation",
        "severity": "medium",
        "source": "manual",
    }
    response = client.post("/api/v1/incidents/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == payload["title"]
    assert data["severity"] == "medium"
    assert data["status"] == "open"
    assert data["source"] == "manual"


def test_incident_not_found():
    fake_id = str(uuid.uuid4())
    response = client.get(f"/api/v1/incidents/{fake_id}")
    assert response.status_code == 404


def test_ops_summary():
    response = client.get("/api/v1/incidents/stats/summary")
    assert response.status_code == 200
    data = response.json()
    assert "open_incidents" in data
    assert "critical_incidents" in data
    assert "total_devices" in data
