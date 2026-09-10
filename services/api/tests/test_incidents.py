import uuid

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_threshold_engine_triggers_dns_incident(client: AsyncClient):
    hostname = f"AT-PC-DNSFAULT-{uuid.uuid4().hex[:6]}"
    fault_payload = {
        "hostname": hostname,
        "ip_address": "192.168.30.24",
        "os_version": "Windows 11 Pro",
        "cpu_percent": 15.0,
        "ram_percent": 45.0,
        "disk_percent": 50.0,
        "gateway_reachable": True,
        "dns_resolution_ok": False,  # Fault: DNS resolution failed
        "critical_services": [],
    }

    res = await client.post("/api/v1/telemetry/", json=fault_payload)
    assert res.status_code == 200
    assert res.json()["incidents_generated"] == 1

    # Verify incident exists in list
    inc_res = await client.get("/api/v1/incidents/?severity=critical")
    assert inc_res.status_code == 200
    incidents = inc_res.json()
    assert len(incidents) >= 1
    dns_inc = next((i for i in incidents if hostname in i["title"]), None)
    assert dns_inc is not None
    assert dns_inc["severity"] == "critical"
    assert dns_inc["status"] == "open"
    assert "events" in dns_inc
    assert len(dns_inc["events"]) >= 1


@pytest.mark.asyncio
async def test_threshold_engine_triggers_disk_capacity_incident(client: AsyncClient):
    hostname = f"AT-PC-DISKFAULT-{uuid.uuid4().hex[:6]}"
    disk_fault_payload = {
        "hostname": hostname,
        "ip_address": "192.168.30.99",
        "os_version": "Windows 11 Pro",
        "cpu_percent": 20.0,
        "ram_percent": 40.0,
        "disk_percent": 96.5,  # Fault: Disk > 95%
        "gateway_reachable": True,
        "dns_resolution_ok": True,
    }

    res = await client.post("/api/v1/telemetry/", json=disk_fault_payload)
    assert res.status_code == 200
    assert res.json()["incidents_generated"] == 1

    # Verify incident
    inc_res = await client.get("/api/v1/incidents/")
    incidents = inc_res.json()
    disk_inc = next((i for i in incidents if hostname in i["title"]), None)
    assert disk_inc is not None
    assert disk_inc["severity"] == "critical"
    assert "96.5" in disk_inc["title"]


@pytest.mark.asyncio
async def test_incident_manual_create_and_resolve(client: AsyncClient):
    create_res = await client.post(
        "/api/v1/incidents/",
        json={
            "title": "Printer queue stalled on print01",
            "description": "5 jobs waiting in spooler queue for Finance department",
            "severity": "medium",
            "source": "technician",
        },
    )
    assert create_res.status_code == 201
    inc = create_res.json()
    inc_id = inc["id"]
    assert inc["status"] == "open"

    # Resolve incident
    patch_res = await client.patch(
        f"/api/v1/incidents/{inc_id}",
        json={
            "status": "resolved",
            "resolution_notes": "Restarted Spooler service on print01",
        },
    )
    assert patch_res.status_code == 200
    resolved = patch_res.json()
    assert resolved["status"] == "resolved"
    assert resolved["resolved_at"] is not None


@pytest.mark.asyncio
async def test_ops_stats_summary(client: AsyncClient):
    res = await client.get("/api/v1/incidents/stats/summary")
    assert res.status_code == 200
    stats = res.json()
    assert "open_incidents" in stats
    assert "critical_incidents" in stats
    assert "total_devices" in stats
