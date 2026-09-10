import uuid
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.device import Device
from app.models.telemetry import TelemetryRecord

router = APIRouter()


class DeviceCreate(BaseModel):
    hostname: str
    ip_address: str
    mac_address: str | None = None
    os_version: str
    department: str | None = None


class DeviceUpdate(BaseModel):
    department: str | None = None
    status: str | None = None
    ip_address: str | None = None


class TelemetrySnapshot(BaseModel):
    cpu_percent: float
    ram_percent: float
    disk_percent: float
    gateway_reachable: bool
    dns_resolution_ok: bool
    timestamp: datetime


class DeviceDetailResponse(BaseModel):
    id: uuid.UUID
    hostname: str
    ip_address: str
    mac_address: str | None
    os_version: str
    department: str | None
    status: str
    created_at: datetime
    updated_at: datetime
    latest_telemetry: TelemetrySnapshot | None = None

    model_config = {"from_attributes": True}


@router.get("/", response_model=list[DeviceDetailResponse])
async def list_devices(
    department: str | None = Query(None),
    status: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """List all registered devices with their latest telemetry snapshot."""
    query = select(Device)
    if department:
        query = query.where(Device.department == department)
    if status:
        query = query.where(Device.status == status)

    result = await db.execute(query.order_by(Device.hostname))
    devices = result.scalars().all()

    device_list = []
    for dev in devices:
        # Fetch latest telemetry
        t_stmt = (
            select(TelemetryRecord)
            .where(TelemetryRecord.device_id == dev.id)
            .order_by(desc(TelemetryRecord.created_at))
            .limit(1)
        )
        t_res = await db.execute(t_stmt)
        latest_t = t_res.scalar_one_or_none()

        snapshot = None
        if latest_t:
            snapshot = TelemetrySnapshot(
                cpu_percent=latest_t.cpu_percent,
                ram_percent=latest_t.ram_percent,
                disk_percent=latest_t.disk_percent,
                gateway_reachable=latest_t.gateway_reachable,
                dns_resolution_ok=latest_t.dns_resolution_ok,
                timestamp=latest_t.created_at,
            )

        device_list.append(
            DeviceDetailResponse(
                id=dev.id,
                hostname=dev.hostname,
                ip_address=dev.ip_address,
                mac_address=dev.mac_address,
                os_version=dev.os_version,
                department=dev.department,
                status=dev.status,
                created_at=dev.created_at,
                updated_at=dev.updated_at,
                latest_telemetry=snapshot,
            )
        )

    return device_list


@router.get("/{device_id}", response_model=DeviceDetailResponse)
async def get_device(device_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Retrieve detailed information for a single device."""
    result = await db.execute(select(Device).where(Device.id == device_id))
    dev = result.scalar_one_or_none()
    if not dev:
        raise HTTPException(status_code=404, detail="Device not found")

    t_stmt = (
        select(TelemetryRecord)
        .where(TelemetryRecord.device_id == dev.id)
        .order_by(desc(TelemetryRecord.created_at))
        .limit(1)
    )
    t_res = await db.execute(t_stmt)
    latest_t = t_res.scalar_one_or_none()

    snapshot = None
    if latest_t:
        snapshot = TelemetrySnapshot(
            cpu_percent=latest_t.cpu_percent,
            ram_percent=latest_t.ram_percent,
            disk_percent=latest_t.disk_percent,
            gateway_reachable=latest_t.gateway_reachable,
            dns_resolution_ok=latest_t.dns_resolution_ok,
            timestamp=latest_t.created_at,
        )

    return DeviceDetailResponse(
        id=dev.id,
        hostname=dev.hostname,
        ip_address=dev.ip_address,
        mac_address=dev.mac_address,
        os_version=dev.os_version,
        department=dev.department,
        status=dev.status,
        created_at=dev.created_at,
        updated_at=dev.updated_at,
        latest_telemetry=snapshot,
    )


@router.post("/", response_model=DeviceDetailResponse, status_code=201)
async def create_device(payload: DeviceCreate, db: AsyncSession = Depends(get_db)):
    """Manually register an asset/device."""
    existing = await db.execute(select(Device).where(Device.hostname == payload.hostname))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail=f"Device '{payload.hostname}' already registered")

    device = Device(**payload.model_dump())
    db.add(device)
    await db.commit()
    await db.refresh(device)

    return DeviceDetailResponse(
        id=device.id,
        hostname=device.hostname,
        ip_address=device.ip_address,
        mac_address=device.mac_address,
        os_version=device.os_version,
        department=device.department,
        status=device.status,
        created_at=device.created_at,
        updated_at=device.updated_at,
        latest_telemetry=None,
    )


@router.patch("/{device_id}", response_model=DeviceDetailResponse)
async def update_device(
    device_id: uuid.UUID,
    payload: DeviceUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update device metadata."""
    result = await db.execute(select(Device).where(Device.id == device_id))
    dev = result.scalar_one_or_none()
    if not dev:
        raise HTTPException(status_code=404, detail="Device not found")

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(dev, key, value)

    await db.commit()
    await db.refresh(dev)
    return await get_device(device_id=device_id, db=db)


@router.delete("/{device_id}", status_code=204)
async def delete_device(device_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Deregister / delete a device and associated records."""
    result = await db.execute(select(Device).where(Device.id == device_id))
    dev = result.scalar_one_or_none()
    if not dev:
        raise HTTPException(status_code=404, detail="Device not found")

    await db.delete(dev)
    await db.commit()
