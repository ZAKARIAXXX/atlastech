from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_telemetry_ingest():
    payload = {
        "hostname": "AT-PC-TEL-TEST",
        "ip_address": "192.168.10.50",
        "os_version": "Windows 11 Pro 23H2",
        "cpu_percent": 45.2,
        "ram_percent": 67.8,
        "disk_percent": 55.0,
        "gateway_reachable": True,
        "dns_resolution_ok": True,
        "critical_services": [
            {"name": "dnscache", "display_name": "DNS Client", "status": "running"}
        ],
        "logged_in_user": "ATLAS\\testuser",
    }
    response = client.post("/api/v1/telemetry/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "accepted"
    assert data["hostname"] == "AT-PC-TEL-TEST"
    assert "device_id" in data
    assert "incidents_generated" in data


def test_telemetry_latest():
    response = client.get("/api/v1/telemetry/latest/AT-PC-TEL-TEST")
    assert response.status_code == 200
    data = response.json()
    assert data["hostname"] == "AT-PC-TEL-TEST"


def test_telemetry_latest_not_found():
    response = client.get("/api/v1/telemetry/latest/NONEXISTENT")
    assert response.status_code == 404


def test_telemetry_history():
    response = client.get("/api/v1/telemetry/history/AT-PC-TEL-TEST?limit=5")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
