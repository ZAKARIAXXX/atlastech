import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_diagnostic_playbooks(client: AsyncClient):
    res = await client.get("/api/v1/diagnostics/playbooks")
    assert res.status_code == 200
    playbooks = res.json()
    assert isinstance(playbooks, list)
    assert len(playbooks) >= 4
    ids = [p["id"] for p in playbooks]
    assert "dns-diag" in ids
    assert "net-diag" in ids
    assert "disk-cleanup" in ids


@pytest.mark.asyncio
async def test_execute_diagnostic_playbook(client: AsyncClient):
    # 1. Register device
    dev_res = await client.post(
        "/api/v1/devices/",
        json={
            "hostname": "AT-PC-DIAG-01",
            "ip_address": "192.168.10.12",
            "os_version": "Windows 11",
            "department": "IT",
        },
    )
    dev_id = dev_res.json()["id"]

    # 2. Execute playbook
    exec_res = await client.post(
        "/api/v1/diagnostics/execute",
        json={
            "device_id": dev_id,
            "playbook_id": "dns-diag",
        },
    )
    assert exec_res.status_code == 200
    diag = exec_res.json()
    assert diag["status"] == "success"
    assert diag["device_hostname"] == "AT-PC-DIAG-01"
    assert diag["playbook_id"] == "dns-diag"
    assert "findings" in diag["output"]
