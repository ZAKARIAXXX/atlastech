from fastapi import APIRouter

from app.api.v1.endpoints import devices, health, incidents, telemetry

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(devices.router, prefix="/devices", tags=["Devices"])
api_router.include_router(telemetry.router, prefix="/telemetry", tags=["Telemetry"])
api_router.include_router(incidents.router, prefix="/incidents", tags=["Incidents"])
