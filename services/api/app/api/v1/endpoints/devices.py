import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.device import Device

router = APIRouter()


class DeviceCreate(BaseModel):
    hostname: str
    ip_address: str
    mac_address: str | None = None
    os_version: str
    department: str | None = None


class DeviceResponse(BaseModel):
    id: uuid.UUID
    hostname: str
    ip_address: str
    os_version: str
    department: str | None
    status: str

    model_config = {"from_attributes": True}


@router.get("/", response_model=list[DeviceResponse])
async def list_devices(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Device))
    return result.scalars().all()


@router.get("/{device_id}", response_model=DeviceResponse)
async def get_device(device_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Device).where(Device.id == device_id))
    device = result.scalar_one_or_none()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device


@router.post("/", response_model=DeviceResponse, status_code=201)
async def create_device(payload: DeviceCreate, db: AsyncSession = Depends(get_db)):
    device = Device(**payload.model_dump())
    db.add(device)
    await db.flush()
    await db.refresh(device)
    return device
