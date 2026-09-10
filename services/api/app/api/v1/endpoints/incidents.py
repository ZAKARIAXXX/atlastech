import uuid
from datetime import UTC, datetime
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.auth import verify_api_key
from app.core.database import get_db
from app.models.device import Device
from app.models.incident import Incident, IncidentEvent

router = APIRouter()

IncidentSeverity = Literal["critical", "high", "medium", "low"]
IncidentStatus = Literal["open", "in_progress", "resolved", "closed"]


class IncidentEventResponse(BaseModel):
    id: uuid.UUID
    event_type: str
    payload: dict[str, Any] | None
    created_by: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class IncidentCreate(BaseModel):
    title: str
    description: str
    severity: IncidentSeverity
    source: str = "manual"
    device_id: uuid.UUID | None = None


class IncidentUpdate(BaseModel):
    status: IncidentStatus | None = None
    severity: IncidentSeverity | None = None
    assigned_technician_id: uuid.UUID | None = None
    resolution_notes: str | None = None


class IncidentResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    severity: str
    status: str
    source: str
    device_id: uuid.UUID | None
    device_hostname: str | None = None
    assigned_technician_id: uuid.UUID | None
    resolved_at: datetime | None
    created_at: datetime
    updated_at: datetime
    events: list[IncidentEventResponse] = []

    model_config = {"from_attributes": True}


class OpsStatsSummary(BaseModel):
    open_incidents: int
    critical_incidents: int
    in_progress_incidents: int
    resolved_today: int
    total_devices: int
    devices_online: int


@router.get("/stats/summary", response_model=OpsStatsSummary)
async def get_ops_summary(db: AsyncSession = Depends(get_db)):
    """Summary metrics for the operations center main dashboard."""
    open_cnt = (
        await db.scalar(select(func.count(Incident.id)).where(Incident.status == "open")) or 0
    )
    crit_cnt = (
        await db.scalar(
            select(func.count(Incident.id)).where(
                Incident.severity == "critical", Incident.status.in_(["open", "in_progress"])
            )
        )
        or 0
    )
    in_prog_cnt = (
        await db.scalar(select(func.count(Incident.id)).where(Incident.status == "in_progress"))
        or 0
    )

    today_start = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
    resolved_cnt = (
        await db.scalar(
            select(func.count(Incident.id)).where(
                Incident.status == "resolved", Incident.resolved_at >= today_start
            )
        )
        or 0
    )

    total_dev = await db.scalar(select(func.count(Device.id))) or 0
    online_dev = (
        await db.scalar(select(func.count(Device.id)).where(Device.status == "online")) or 0
    )

    return OpsStatsSummary(
        open_incidents=open_cnt,
        critical_incidents=crit_cnt,
        in_progress_incidents=in_prog_cnt,
        resolved_today=resolved_cnt,
        total_devices=total_dev,
        devices_online=online_dev,
    )


@router.get("/", response_model=list[IncidentResponse])
async def list_incidents(
    status: IncidentStatus | None = Query(None),
    severity: IncidentSeverity | None = Query(None),
    device_id: uuid.UUID | None = Query(None),
    limit: int = Query(default=50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """List all incidents with optional filtering and joined device hostnames."""
    query = (
        select(Incident)
        .options(selectinload(Incident.device), selectinload(Incident.events))
        .order_by(desc(Incident.created_at))
    )

    if status:
        query = query.where(Incident.status == status)
    if severity:
        query = query.where(Incident.severity == severity)
    if device_id:
        query = query.where(Incident.device_id == device_id)

    query = query.limit(limit)
    result = await db.execute(query)
    incidents = result.scalars().all()

    return [
        IncidentResponse(
            id=inc.id,
            title=inc.title,
            description=inc.description,
            severity=inc.severity,
            status=inc.status,
            source=inc.source,
            device_id=inc.device_id,
            device_hostname=inc.device.hostname if inc.device else None,
            assigned_technician_id=inc.assigned_technician_id,
            resolved_at=inc.resolved_at,
            created_at=inc.created_at,
            updated_at=inc.updated_at,
            events=[IncidentEventResponse.model_validate(e) for e in inc.events],
        )
        for inc in incidents
    ]


@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(incident_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Get single incident details with audit events."""
    query = (
        select(Incident)
        .options(selectinload(Incident.device), selectinload(Incident.events))
        .where(Incident.id == incident_id)
    )
    result = await db.execute(query)
    incident = result.scalar_one_or_none()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    return IncidentResponse(
        id=incident.id,
        title=incident.title,
        description=incident.description,
        severity=incident.severity,
        status=incident.status,
        source=incident.source,
        device_id=incident.device_id,
        device_hostname=incident.device.hostname if incident.device else None,
        assigned_technician_id=incident.assigned_technician_id,
        resolved_at=incident.resolved_at,
        created_at=incident.created_at,
        updated_at=incident.updated_at,
        events=[IncidentEventResponse.model_validate(e) for e in incident.events],
    )


@router.post("/", response_model=IncidentResponse, status_code=201)
async def create_incident(
    payload: IncidentCreate,
    db: AsyncSession = Depends(get_db),
    _auth: str = Depends(verify_api_key),
):
    """Manually create a helpdesk incident ticket (Protected)."""
    incident = Incident(
        title=payload.title,
        description=payload.description,
        severity=payload.severity,
        source=payload.source,
        device_id=payload.device_id,
        status="open",
    )
    db.add(incident)
    await db.flush()

    event = IncidentEvent(
        incident_id=incident.id,
        event_type="incident_created_manual",
        payload={"created_via": "api"},
        created_by="Technician",
    )
    db.add(event)
    await db.commit()

    return await get_incident(incident_id=incident.id, db=db)


@router.patch("/{incident_id}", response_model=IncidentResponse)
async def update_incident(
    incident_id: uuid.UUID,
    payload: IncidentUpdate,
    db: AsyncSession = Depends(get_db),
    _auth: str = Depends(verify_api_key),
):
    """Update incident status, assign technician, or mark as resolved (Protected)."""
    query = (
        select(Incident).options(selectinload(Incident.events)).where(Incident.id == incident_id)
    )
    result = await db.execute(query)
    incident = result.scalar_one_or_none()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    if payload.status:
        prev_status = incident.status
        incident.status = payload.status
        if payload.status == "resolved" and not incident.resolved_at:
            incident.resolved_at = datetime.now(UTC)
        elif payload.status != "resolved":
            incident.resolved_at = None

        event = IncidentEvent(
            incident_id=incident.id,
            event_type="status_changed",
            payload={
                "previous_status": prev_status,
                "new_status": payload.status,
                "notes": payload.resolution_notes,
            },
            created_by="Technician",
        )
        db.add(event)

    if payload.severity:
        incident.severity = payload.severity

    if payload.assigned_technician_id is not None:
        incident.assigned_technician_id = payload.assigned_technician_id
        event = IncidentEvent(
            incident_id=incident.id,
            event_type="technician_assigned",
            payload={"technician_id": str(payload.assigned_technician_id)},
            created_by="Dispatcher",
        )
        db.add(event)

    await db.commit()
    return await get_incident(incident_id=incident.id, db=db)
