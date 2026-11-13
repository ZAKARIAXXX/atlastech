# AtlasTech — Documentation

Start with the status, then the roadmap. ADRs record why decisions were
made; runbooks record how to operate and recover the system.

## Status & roadmap

- [Status](STATUS.md) — current state, CI health, next actions.
- [Project status & roadmap](PROJECT_STATUS_AND_ROADMAP.md) — phases and direction.
- [Changelog](../CHANGELOG.md) — notable changes, newest first.

## Architecture

- [System overview](architecture/system-overview.md)
- [Lab network topology](architecture/lab-network-topology.png)

## Architecture decisions (ADR)

- [ADR-001 — FastAPI backend](adr/ADR-001-fastapi-backend.md)
- [ADR-002 — Next.js frontend](adr/ADR-002-nextjs-frontend.md)
- [ADR-003 — Postgres & Redis data layer](adr/ADR-003-postgres-redis-data-layer.md)
- [ADR-004 — Trivy security scanning](adr/ADR-004-trivy-security-scanning.md)

## Runbooks

- [CI](runbooks/CI.md)
- [Troubleshooting](runbooks/TROUBLESHOOTING.md)
- [API lint & type check triage](runbooks/api-lint-typecheck.md)
- [Lab setup](runbooks/lab-setup.md)
- [E2E failure scenario](runbooks/e2e-failure-scenario.md)

## Plans

- [System design (2026-09-10)](plans/2026-09-10-system-design.md)
- [Task plan](plans/task.md)
