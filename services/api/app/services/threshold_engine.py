from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.device import Device
from app.models.incident import Incident, IncidentEvent


class ThresholdEngine:
    """
    Evaluates real-time device telemetry against operational thresholds
    and automatically manages incidents (creation, deduplication, event tracking).
    """

    DISK_CRITICAL_PERCENT = 95.0
    DISK_HIGH_PERCENT = 90.0
    RAM_CRITICAL_PERCENT = 95.0
    CPU_CRITICAL_PERCENT = 98.0

    @classmethod
    async def evaluate(
        cls,
        device: Device,
        telemetry: dict[str, Any],
        db: AsyncSession,
    ) -> list[Incident]:
        generated_incidents: list[Incident] = []

        # 1. DNS Resolution Check
        if not telemetry.get("dns_resolution_ok", True):
            incident = await cls._handle_fault(
                db=db,
                device=device,
                title=f"[DNS] Resolution Failure on {device.hostname}",
                description=(
                    f"Endpoint {device.hostname} ({device.ip_address}) failed internal domain DNS resolution "
                    f"for 'dc01.atlastech.local'. This prevents Active Directory authentication and network shares."
                ),
                severity="critical",
                event_payload={
                    "fault": "dns_failure",
                    "ip_address": device.ip_address,
                    "os_version": device.os_version,
                },
            )
            if incident:
                generated_incidents.append(incident)

        # 2. Gateway Reachability Check
        if not telemetry.get("gateway_reachable", True):
            incident = await cls._handle_fault(
                db=db,
                device=device,
                title=f"[NETWORK] Gateway Unreachable on {device.hostname}",
                description=(
                    f"Default gateway ping failed for {device.hostname}. The host may be disconnected from "
                    f"the local VLAN or experiencing interface failure."
                ),
                severity="high",
                event_payload={"fault": "gateway_unreachable", "ip": device.ip_address},
            )
            if incident:
                generated_incidents.append(incident)

        # 3. Disk Space Capacity Check
        disk_pct = float(telemetry.get("disk_percent", 0.0))
        if disk_pct >= cls.DISK_HIGH_PERCENT:
            severity = "critical" if disk_pct >= cls.DISK_CRITICAL_PERCENT else "high"
            incident = await cls._handle_fault(
                db=db,
                device=device,
                title=f"[STORAGE] Volume C: Capacity Alert ({disk_pct}%) on {device.hostname}",
                description=(
                    f"Storage utilization on system drive C: reached {disk_pct}%, exceeding the "
                    f"{cls.DISK_HIGH_PERCENT}% threshold. Service disruption or log write failure imminent."
                ),
                severity=severity,
                event_payload={"fault": "disk_pressure", "disk_percent": disk_pct},
            )
            if incident:
                generated_incidents.append(incident)

        # 4. Critical Windows Services Check
        services = telemetry.get("critical_services") or []
        for svc in services:
            if isinstance(svc, dict) and svc.get("status") in ["stopped", "failed"]:
                svc_name = svc.get("name", "unknown")
                display_name = svc.get("display_name", svc_name)
                # Only alert for key infrastructure services
                if svc_name in ["dnscache", "spooler", "lanmanworkstation", "dns"]:
                    incident = await cls._handle_fault(
                        db=db,
                        device=device,
                        title=f"[SERVICE] Critical Service '{display_name}' Stopped on {device.hostname}",
                        description=(
                            f"Windows service '{display_name}' ({svc_name}) is currently stopped on {device.hostname}. "
                            f"Associated dependent subsystems may be unavailable."
                        ),
                        severity="medium",
                        event_payload={"fault": "service_stopped", "service": svc},
                    )
                    if incident:
                        generated_incidents.append(incident)

        return generated_incidents

    @classmethod
    async def _handle_fault(
        cls,
        db: AsyncSession,
        device: Device,
        title: str,
        description: str,
        severity: str,
        event_payload: dict[str, Any],
    ) -> Incident | None:
        """
        Deduplicates open incidents to avoid alert flooding.
        Creates a new incident if none is open, or appends a timestamped event.
        """
        query = (
            select(Incident)
            .where(
                Incident.device_id == device.id,
                Incident.title == title,
                Incident.status.in_(["open", "in_progress"]),
            )
            .limit(1)
        )
        result = await db.execute(query)
        existing = result.scalar_one_or_none()

        if existing:
            # Append heartbeat evidence event
            event = IncidentEvent(
                incident_id=existing.id,
                event_type="telemetry_breach_recurrent",
                payload=event_payload,
                created_by="ThresholdEngine",
            )
            db.add(event)
            return None

        # Create new incident
        new_incident = Incident(
            title=title,
            description=description,
            severity=severity,
            status="open",
            source="automated",
            device_id=device.id,
        )
        db.add(new_incident)
        await db.flush()

        initial_event = IncidentEvent(
            incident_id=new_incident.id,
            event_type="incident_created_auto",
            payload=event_payload,
            created_by="ThresholdEngine",
        )
        db.add(initial_event)
        return new_incident
