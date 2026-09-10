import uuid

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_devices_initially(client: AsyncClient):
    response = await client.get("/api/v1/devices/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_create_and_get_device(client: AsyncClient):
    hostname = f"AT-PC-{uuid.uuid4().hex[:6]}"
    payload = {
        "hostname": hostname,
        "ip_address": "192.168.10.50",
        "mac_address": "00:1A:2B:3C:4D:5E",
        "os_version": "Windows 11 Enterprise 23H2",
        "department": "Finance",
    }
    create_res = await client.post("/api/v1/devices/", json=payload)
    assert create_res.status_code == 201
    dev = create_res.json()
    assert dev["hostname"] == hostname
    assert dev["ip_address"] == "192.168.10.50"
    assert dev["department"] == "Finance"
    assert dev["status"] == "online"
    assert "id" in dev

    device_id = dev["id"]
    get_res = await client.get(f"/api/v1/devices/{device_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == device_id


@pytest.mark.asyncio
async def test_create_duplicate_device_error(client: AsyncClient):
    hostname = f"AT-PC-DUP-{uuid.uuid4().hex[:6]}"
    payload = {
        "hostname": hostname,
        "ip_address": "192.168.10.55",
        "os_version": "Windows 11",
    }
    res1 = await client.post("/api/v1/devices/", json=payload)
    assert res1.status_code == 201

    res2 = await client.post("/api/v1/devices/", json=payload)
    assert res2.status_code == 409


@pytest.mark.asyncio
async def test_update_device(client: AsyncClient):
    hostname = f"AT-PC-UPD-{uuid.uuid4().hex[:6]}"
    payload = {
        "hostname": hostname,
        "ip_address": "192.168.10.60",
        "os_version": "Windows 11",
        "department": "Sales",
    }
    create_res = await client.post("/api/v1/devices/", json=payload)
    dev_id = create_res.json()["id"]

    patch_res = await client.patch(
        f"/api/v1/devices/{dev_id}",
        json={"department": "Management", "status": "maintenance"},
    )
    assert patch_res.status_code == 200
    updated = patch_res.json()
    assert updated["department"] == "Management"
    assert updated["status"] == "maintenance"
