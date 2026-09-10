import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.device import Device
from app.models.telemetry import TelemetryRecord
from app.services.threshold_engine import ThresholdEngine

router = APIRouter()


class ServiceStatus(BaseModel):
    name: str
    display_name: str | None = None
    status: str
    pid: int | None = None


class TelemetryIngest(BaseModel):
    hostname: str
    ip_address: str
    mac_address: str | None = None
    os_version: str
    department: str | None = None
    cpu_percent: float = Field(ge=0.0, le=100.0)
    ram_percent: float = Field(ge=0.0, le=100.0)
    disk_percent: float = Field(ge=0.0, le=100.0)
    gateway_reachable: bool = True
    dns_resolution_ok: bool = True
    critical_services: list[dict[str, Any]] | None = None
    logged_in_user: str | None = None
    latency_ms: int | None = None


class TelemetryResponse(BaseModel):
    device_id: str
    hostname: str
    status: str
    incidents_generated: int
    timestamp: datetime


@router.post("/", response_model=TelemetryResponse, status_code=200)
async def ingest_telemetry(payload: TelemetryIngest, db: AsyncSession = Depends(get_db)):
    """
    Ingest endpoint telemetry, upsert device registry, persist metrics,
    and evaluate real-time threshold alert rules.
    """
    # 1. Upsert Device
    stmt = select(Device).where(Device.hostname == payload.hostname)
    result = await db.execute(stmt)
    device = result.scalar_one_or_none()

    if not device:
        device = Device(
            hostname=payload.hostname,
            ip_address=payload.ip_address,
            mac_address=payload.mac_address,
            os_version=payload.os_version,
            department=payload.department,
            status="online",
        )
        db.add(device)
        await db.flush()
    else:
        device.ip_address = payload.ip_address
        device.os_version = payload.os_version
        device.status = "online"
        if payload.department:
            device.department = payload.department
        if payload.mac_address:
            device.mac_address = payload.mac_address

    # 2. Record Telemetry
    record = TelemetryRecord(
        device_id=device.id,
        cpu_percent=payload.cpu_percent,
        ram_percent=payload.ram_percent,
        disk_percent=payload.disk_percent,
        gateway_reachable=payload.gateway_reachable,
        dns_resolution_ok=payload.dns_resolution_ok,
        critical_services=payload.critical_services,
        logged_in_user=payload.logged_in_user,
        latency_ms=payload.latency_ms,
    )
    db.add(record)

    # 3. Threshold Evaluation
    incidents = await ThresholdEngine.evaluate(
        device=device,
        telemetry=payload.model_dump(),
        db=db,
    )

    await db.commit()

    return TelemetryResponse(
        device_id=str(device.id),
        hostname=device.hostname,
        status="accepted",
        incidents_generated=len(incidents),
        timestamp=datetime.now(timezone.utc),
    )


@router.get("/latest/{hostname}")
async def get_latest_telemetry(hostname: str, db: AsyncSession = Depends(get_db)):
    """Retrieve the most recent telemetry snapshot for a given hostname."""
    dev_stmt = select(Device).where(Device.hostname == hostname)
    dev_res = await db.execute(dev_stmt)
    device = dev_res.scalar_one_or_none()
    if not device:
        raise HTTPException(status_code=404, detail=f"Device '{hostname}' not found")

    rec_stmt = (
        select(TelemetryRecord)
        .where(TelemetryRecord.device_id == device.id)
        .order_by(desc(TelemetryRecord.created_at))
        .limit(1)
    )
    rec_res = await db.execute(rec_stmt)
    record = rec_res.scalar_one_or_none()

    if not record:
        return {"device": device.hostname, "telemetry": None}

    return {
        "device_id": str(device.id),
        "hostname": device.hostname,
        "ip_address": device.ip_address,
        "os_version": device.os_version,
        "cpu_percent": record.cpu_percent,
        "ram_percent": record.ram_percent,
        "disk_percent": record.disk_percent,
        "gateway_reachable": record.gateway_reachable,
        "dns_resolution_ok": record.dns_resolution_ok,
        "critical_services": record.critical_services,
        "logged_in_user": record.logged_in_user,
        "timestamp": record.created_at,
    }


@router.get("/history/{hostname}")
async def get_telemetry_history(
    hostname: str,
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve time-series telemetry records for graphing."""
    dev_stmt = select(Device).where(Device.hostname == hostname)
    dev_res = await db.execute(dev_stmt)
    device = dev_res.scalar_one_or_none()
    if not device:
        raise HTTPException(status_code=404, detail=f"Device '{hostname}' not found")

    rec_stmt = (
        select(TelemetryRecord)
        .where(TelemetryRecord.device_id == device.id)
        .order_by(desc(TelemetryRecord.created_at))
        .limit(limit)
    )
    rec_res = await db.execute(rec_stmt)
    records = rec_res.scalars().all()

    return [
        {
            "id": str(r.id),
            "cpu_percent": r.cpu_percent,
            "ram_percent": r.ram_percent,
            "disk_percent": r.disk_percent,
            "gateway_reachable": r.gateway_reachable,
            "dns_resolution_ok": r.dns_resolution_ok,
            "timestamp": r.created_at,
        }
        for r in records
    ]
