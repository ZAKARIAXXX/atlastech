import uuid

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_telemetry_ingestion_registers_device_and_metrics(client: AsyncClient):
    hostname = f"AT-PC-TEL-{uuid.uuid4().hex[:6]}"
    payload = {
        "hostname": hostname,
        "ip_address": "192.168.20.101",
        "mac_address": "00:50:56:C0:00:08",
        "os_version": "Windows 11 Pro 23H2",
        "department": "HR",
        "cpu_percent": 34.5,
        "ram_percent": 58.2,
        "disk_percent": 62.0,
        "gateway_reachable": True,
        "dns_resolution_ok": True,
        "critical_services": [
            {"name": "dnscache", "display_name": "DNS Client", "status": "running"},
            {"name": "spooler", "display_name": "Print Spooler", "status": "running"},
        ],
        "logged_in_user": "ATLASTECH\\sarah.miller",
        "latency_ms": 4,
    }

    ingest_res = await client.post("/api/v1/telemetry/", json=payload)
    assert ingest_res.status_code == 200
    data = ingest_res.json()
    assert data["status"] == "accepted"
    assert data["hostname"] == hostname
    assert data["incidents_generated"] == 0

    # Verify device exists
    latest_res = await client.get(f"/api/v1/telemetry/latest/{hostname}")
    assert latest_res.status_code == 200
    latest = latest_res.json()
    assert latest["hostname"] == hostname
    assert latest["cpu_percent"] == 34.5
    assert latest["disk_percent"] == 62.0
    assert latest["gateway_reachable"] is True

    # Check history
    hist_res = await client.get(f"/api/v1/telemetry/history/{hostname}")
    assert hist_res.status_code == 200
    assert len(hist_res.json()) >= 1
