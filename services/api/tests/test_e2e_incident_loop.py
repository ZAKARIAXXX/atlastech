import uuid

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_end_to_end_operational_failure_and_resolution_cycle(client: AsyncClient):
    """
    End-to-End Proof Test:
    1. Healthy Endpoint transmits baseline telemetry.
    2. Fault Injected (DNS failure) -> Ingestion -> Threshold Engine creates CRITICAL incident.
    3. Duplicate fault arrives -> Deduplicated (appends audit event, no alert storm).
    4. Diagnostic Playbook triggered -> Execution findings attached to incident.
    5. Fault Remediated -> Healthy telemetry arrives -> Incident resolved.
    """
    hostname = f"AT-PC-E2E-{uuid.uuid4().hex[:6]}"

    # 1. Baseline Healthy Telemetry
    healthy_payload = {
        "hostname": hostname,
        "ip_address": "192.168.10.101",
        "os_version": "Windows 11 Enterprise",
        "department": "Finance",
        "cpu_percent": 18.5,
        "ram_percent": 45.0,
        "disk_percent": 52.0,
        "gateway_reachable": True,
        "dns_resolution_ok": True,
        "critical_services": [
            {"name": "dnscache", "display_name": "DNS Client", "status": "running"}
        ],
        "logged_in_user": "ATLASTECH\\sarah.miller",
    }
    h_res = await client.post("/api/v1/telemetry/", json=healthy_payload)
    assert h_res.status_code == 200
    assert h_res.json()["status"] == "accepted"
    assert h_res.json()["incidents_generated"] == 0
    device_id = h_res.json()["device_id"]

    # 2. Chaos Injected: DNS Failure
    fault_payload = {
        **healthy_payload,
        "dns_resolution_ok": False,  # Fault!
    }
    f_res = await client.post("/api/v1/telemetry/", json=fault_payload)
    assert f_res.status_code == 200
    assert f_res.json()["incidents_generated"] == 1

    # Verify Incident Created
    inc_res = await client.get("/api/v1/incidents/?severity=critical")
    assert inc_res.status_code == 200
    incidents = inc_res.json()
    incident = next((i for i in incidents if hostname in i["title"]), None)
    assert incident is not None
    assert incident["status"] == "open"
    assert incident["severity"] == "critical"
    incident_id = incident["id"]

    # 3. Subsequent Heartbeat During Outage -> Deduplication Check
    dup_res = await client.post("/api/v1/telemetry/", json=fault_payload)
    assert dup_res.status_code == 200
    assert dup_res.json()["incidents_generated"] == 0  # No duplicate incident created!

    # 4. Dispatch Automated Diagnostic Playbook
    diag_res = await client.post(
        "/api/v1/diagnostics/execute",
        json={
            "device_id": device_id,
            "playbook_id": "dns-diag",
            "incident_id": incident_id,
        },
    )
    assert diag_res.status_code == 200
    diag_data = diag_res.json()
    assert diag_data["status"] == "success"
    assert diag_data["playbook_name"] == "DNS & Name Resolution Diagnostic"

    # 5. Fault Remediated & Ticket Resolved
    recovered_res = await client.post("/api/v1/telemetry/", json=healthy_payload)
    assert recovered_res.status_code == 200

    resolve_res = await client.patch(
        f"/api/v1/incidents/{incident_id}",
        json={
            "status": "resolved",
            "resolution_notes": "DNS server restored to 192.168.10.10; client cache flushed.",
        },
    )
    assert resolve_res.status_code == 200
    resolved_incident = resolve_res.json()
    assert resolved_incident["status"] == "resolved"
    assert resolved_incident["resolved_at"] is not None

    # Verify Final Stats
    stats_res = await client.get("/api/v1/incidents/stats/summary")
    assert stats_res.status_code == 200
    stats = stats_res.json()
    assert stats["resolved_today"] >= 1
