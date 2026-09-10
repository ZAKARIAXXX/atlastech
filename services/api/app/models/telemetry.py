import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, Integer, JSON, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.device import Device


class TelemetryRecord(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "telemetry_records"

    device_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("devices.id", ondelete="CASCADE"), nullable=False, index=True
    )
    cpu_percent: Mapped[float] = mapped_column(Float, nullable=False)
    ram_percent: Mapped[float] = mapped_column(Float, nullable=False)
    disk_percent: Mapped[float] = mapped_column(Float, nullable=False)
    gateway_reachable: Mapped[bool] = mapped_column(nullable=False)
    dns_resolution_ok: Mapped[bool] = mapped_column(nullable=False)
    critical_services: Mapped[list[dict] | None] = mapped_column(JSON, nullable=True)
    logged_in_user: Mapped[str | None] = mapped_column(String(255), nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    device: Mapped["Device"] = relationship("Device", back_populates="telemetry_records")
