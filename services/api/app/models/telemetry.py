import uuid

from sqlalchemy import Float, ForeignKey, Integer, JSON, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class TelemetryRecord(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "telemetry_records"

    device_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("devices.id"), nullable=False, index=True
    )
    cpu_percent: Mapped[float] = mapped_column(Float, nullable=False)
    ram_percent: Mapped[float] = mapped_column(Float, nullable=False)
    disk_percent: Mapped[float] = mapped_column(Float, nullable=False)
    gateway_reachable: Mapped[bool] = mapped_column(nullable=False)
    dns_resolution_ok: Mapped[bool] = mapped_column(nullable=False)
    critical_services: Mapped[dict] = mapped_column(JSON, nullable=True)
    logged_in_user: Mapped[str | None] = mapped_column(String(255), nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    device: Mapped["Device"] = relationship(back_populates="telemetry_records")  # noqa: F821
