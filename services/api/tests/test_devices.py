import uuid

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_list_devices_empty():
    response = client.get("/api/v1/devices/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_and_get_device():
    payload = {
        "hostname": f"AT-PC-TEST-{uuid.uuid4().hex[:8]}",
        "ip_address": "192.168.10.1",
        "os_version": "Windows 11 Pro 23H2",
        "department": "IT",
    }
    create_response = client.post("/api/v1/devices/", json=payload)
    assert create_response.status_code == 201
    data = create_response.json()
    assert data["hostname"] == payload["hostname"]
    assert data["ip_address"] == payload["ip_address"]
    assert data["department"] == payload["department"]
    assert data["status"] == "online"
    assert "id" in data
    assert "created_at" in data

    device_id = data["id"]
    get_response = client.get(f"/api/v1/devices/{device_id}")
    assert get_response.status_code == 200
    assert get_response.json()["hostname"] == payload["hostname"]


def test_create_duplicate_device():
    hostname = f"AT-PC-DUP-{uuid.uuid4().hex[:8]}"
    payload = {
        "hostname": hostname,
        "ip_address": "192.168.10.2",
        "os_version": "Windows 11 Pro 23H2",
    }
    client.post("/api/v1/devices/", json=payload)
    response = client.post("/api/v1/devices/", json=payload)
    assert response.status_code == 409


def test_device_not_found():
    fake_id = str(uuid.uuid4())
    response = client.get(f"/api/v1/devices/{fake_id}")
    assert response.status_code == 404
