# Changelog

All notable changes to AtlasTech are recorded here, newest first.
Format follows [Keep a Changelog](https://keepachangelog.com/).

## Unreleased

### Added

- Contribution guide (`CONTRIBUTING.md`): workflow, branch/commit
  conventions, local checks, and documentation rules (2026-11-17).
- Runbook: Redis operations (`docs/runbooks/redis-operations.md`) —
  health checks, key inspection, safe cache clearing, failure table
  (2026-11-17).
- Runbook: incident response (`docs/runbooks/incident-response.md`) —
  severity levels, first-10-minutes procedure, closing criteria
  (2026-11-17).
- ADR-006: Redis usage boundaries
  (`docs/adr/ADR-006-redis-usage-boundaries.md`) — PostgreSQL as the
  only source of truth, TTL rule, degradation contract (2026-11-17).
- MIT license file (`LICENSE`) — the README badge link now resolves
  (2026-11-16).
- Security policy (`SECURITY.md`): vulnerability reporting route and the
  repository's documented security posture (2026-11-16).
- Runbook: local development (`docs/runbooks/local-development.md`) —
  environment setup, `make up` vs `make dev`, verification (2026-11-16).
- Runbook: database backup & restore
  (`docs/runbooks/database-backup-restore.md`) (2026-11-16).
- ADR-005: Docker Compose as the local environment
  (`docs/adr/ADR-005-docker-compose-local-environment.md`) (2026-11-16).
- Runbook: API lint & type check triage procedure
  (`docs/runbooks/api-lint-typecheck.md`).
- Documentation index (`docs/README.md`) mapping status, ADRs, runbooks,
  architecture and plans.
- CI pipeline runbook (`docs/runbooks/CI.md`, 2026-11-09).
- README now lists ADR-001 → ADR-004 and links the project status
  (2026-11-11).

### Changed

- Documentation index (`docs/README.md`) now also links the local
  development and backup/restore runbooks, ADR-005, the security policy,
  and the license; the main README's ADR list now includes ADR-005
  (2026-11-16).
- `docs/STATUS.md` refreshed for 2026-11-16: documentation state; CI state
  unchanged since its last verification on 2026-11-13.
- `docs/STATUS.md` refreshed for 2026-11-13: current CI state and a
  next-actions list.

### Known issues

- CI Security Scan fails: the `aquasecurity/trivy-action@0.28.0` tag no
  longer exists; the fix is the `v0.36.0` bump in
  `.github/workflows/ci.yml`.
- CI API Lint & Type Check fails (exit 1); cause under investigation —
  see the triage runbook.
