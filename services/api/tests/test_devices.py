from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_list_devices_empty():
    response = client.get("/api/v1/devices/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_device():
    payload = {
        "hostname": "AT-PC-001",
        "ip_address": "192.168.10.1",
        "os_version": "Windows 11 Pro 23H2",
        "department": "IT",
    }
    response = client.post("/api/v1/devices/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["hostname"] == "AT-PC-001"
