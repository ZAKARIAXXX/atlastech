# Changelog

All notable changes to AtlasTech are recorded here, newest first.
Format follows [Keep a Changelog](https://keepachangelog.com/).

## Unreleased

### Added

- Runbook: API lint & type check triage procedure
  (`docs/runbooks/api-lint-typecheck.md`).
- Documentation index (`docs/README.md`) mapping status, ADRs, runbooks,
  architecture and plans.
- CI pipeline runbook (`docs/runbooks/CI.md`, 2026-11-09).
- README now lists ADR-001 → ADR-004 and links the project status
  (2026-11-11).

### Changed

- `docs/STATUS.md` refreshed for 2026-11-13: current CI state and a
  next-actions list.

### Known issues

- CI Security Scan fails: the `aquasecurity/trivy-action@0.28.0` tag no
  longer exists; the fix is the `v0.36.0` bump in
  `.github/workflows/ci.yml`.
- CI API Lint & Type Check fails (exit 1); cause under investigation —
  see the triage runbook.
