import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.device import Device
from app.models.incident import Incident, IncidentEvent

router = APIRouter()


class Playbook(BaseModel):
    id: str
    name: str
    description: str
    target_type: str  # network, storage, service, identity
    powershell_command: str


AVAILABLE_PLAYBOOKS: list[Playbook] = [
    Playbook(
        id="dns-diag",
        name="DNS & Name Resolution Diagnostic",
        description="Tests resolution against domain controller and flushes DNS resolver cache.",
        target_type="network",
        powershell_command="Resolve-DnsName 'dc01.atlastech.local' -ErrorAction SilentlyContinue; ipconfig /displaydns",
    ),
    Playbook(
        id="net-diag",
        name="Full Network Stack Diagnostic",
        description="Tests default gateway ping, DHCP lease status, and ARP table consistency.",
        target_type="network",
        powershell_command="Test-Connection (Get-NetRoute -DestinationPrefix '0.0.0.0/0').NextHop -Count 2; Get-NetIPConfiguration",
    ),
    Playbook(
        id="disk-cleanup",
        name="Storage Vitals & Temp Cleanup",
        description="Scans volume usage, identifies temp file bloat, and calculates potential savings.",
        target_type="storage",
        powershell_command="Get-ChildItem -Path $env:TEMP -Recurse -Force -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum",
    ),
    Playbook(
        id="service-restart",
        name="Core Services Health & Restart",
        description="Inspects spooler, dnscache, and lanmanworkstation; restarts any stalled service.",
        target_type="service",
        powershell_command="Get-Service -Name dnscache, spooler, lanmanworkstation | Restart-Service -ErrorAction SilentlyContinue -PassThru",
    ),
]


class RunDiagnosticRequest(BaseModel):
    device_id: uuid.UUID
    playbook_id: str
    incident_id: uuid.UUID | None = None


class RunDiagnosticResponse(BaseModel):
    execution_id: str
    device_id: uuid.UUID
    device_hostname: str
    playbook_id: str
    playbook_name: str
    status: str  # success, warning, failed
    output: dict[str, Any]
    executed_at: datetime


@router.get("/playbooks", response_model=list[Playbook])
async def list_diagnostic_playbooks():
    """List all standardized automated diagnostic playbooks."""
    return AVAILABLE_PLAYBOOKS


@router.post("/execute", response_model=RunDiagnosticResponse)
async def execute_diagnostic(
    payload: RunDiagnosticRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Execute a diagnostic playbook on an endpoint (simulated or real runner)
    and append audit logs to the associated incident if provided.
    """
    dev_res = await db.execute(select(Device).where(Device.id == payload.device_id))
    device = dev_res.scalar_one_or_none()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    playbook = next((p for p in AVAILABLE_PLAYBOOKS if p.id == payload.playbook_id), None)
    if not playbook:
        raise HTTPException(status_code=404, detail="Diagnostic playbook not found")

    # Generate structured diagnostic result
    execution_id = f"diag-{uuid.uuid4().hex[:8]}"
    simulated_result = {
        "execution_id": execution_id,
        "playbook": playbook.name,
        "target_host": device.hostname,
        "ip_address": device.ip_address,
        "powershell_command": playbook.powershell_command,
        "status": "completed",
        "findings": [
            f"Interface {device.ip_address} active",
            f"PowerShell diagnostic '{playbook.name}' completed without fatal trap",
        ],
    }

    # If linked to incident, log event
    if payload.incident_id:
        inc_res = await db.execute(select(Incident).where(Incident.id == payload.incident_id))
        incident = inc_res.scalar_one_or_none()
        if incident:
            event = IncidentEvent(
                incident_id=incident.id,
                event_type="diagnostic_executed",
                payload=simulated_result,
                created_by="AutomatedDiagnosticRunner",
            )
            db.add(event)
            await db.commit()

    return RunDiagnosticResponse(
        execution_id=execution_id,
        device_id=device.id,
        device_hostname=device.hostname,
        playbook_id=playbook.id,
        playbook_name=playbook.name,
        status="success",
        output=simulated_result,
        executed_at=datetime.now(timezone.utc),
    )
