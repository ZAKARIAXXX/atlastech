import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.incident import Incident

router = APIRouter()


class IncidentCreate(BaseModel):
    title: str
    description: str
    severity: str
    source: str = "manual"
    device_id: uuid.UUID | None = None


class IncidentResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    severity: str
    status: str
    source: str

    model_config = {"from_attributes": True}


@router.get("/", response_model=list[IncidentResponse])
async def list_incidents(
    status: str | None = None,
    severity: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(Incident)
    if status:
        query = query.where(Incident.status == status)
    if severity:
        query = query.where(Incident.severity == severity)
    query = query.order_by(Incident.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(incident_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Incident).where(Incident.id == incident_id))
    incident = result.scalar_one_or_none()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@router.post("/", response_model=IncidentResponse, status_code=201)
async def create_incident(payload: IncidentCreate, db: AsyncSession = Depends(get_db)):
    incident = Incident(**payload.model_dump(), status="open")
    db.add(incident)
    await db.flush()
    await db.refresh(incident)
    return incident
