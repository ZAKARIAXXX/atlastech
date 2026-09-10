from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db

router = APIRouter()


class TelemetryIngest(BaseModel):
    hostname: str
    ip_address: str
    mac_address: str | None = None
    os_version: str
    cpu_percent: float
    ram_percent: float
    disk_percent: float
    gateway_reachable: bool
    dns_resolution_ok: bool
    critical_services: list[dict] | None = None
    logged_in_user: str | None = None


class TelemetryResponse(BaseModel):
    device_id: str
    status: str


@router.post("/", response_model=TelemetryResponse)
async def ingest_telemetry(payload: TelemetryIngest, db: AsyncSession = Depends(get_db)):
    return TelemetryResponse(device_id=payload.hostname, status="accepted")


@router.get("/latest/{hostname}")
async def get_latest_telemetry(hostname: str, db: AsyncSession = Depends(get_db)):
    return {"hostname": hostname, "telemetry": None}
