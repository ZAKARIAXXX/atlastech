# AtlasTech — Status

Active development. See the Roadmap in README.md for the current phase.

## Documentation (2026-11-16)

- Added the MIT `LICENSE` file — the README badge link now resolves.
- Added `SECURITY.md`: vulnerability reporting route and the repository's
  documented security posture.
- Added runbooks for local development (`docs/runbooks/local-development.md`)
  and database backup & restore (`docs/runbooks/database-backup-restore.md`).
- Added ADR-005 recording the Docker Compose local-environment decision.

## Documentation (2026-11-17)

- Added `CONTRIBUTING.md`: workflow, branch/commit conventions, and the
  local checks expected before pushing.
- Added runbooks for Redis operations (`docs/runbooks/redis-operations.md`)
  and incident response (`docs/runbooks/incident-response.md`).
- Added ADR-006 recording the Redis usage boundaries: PostgreSQL is the
  only source of truth; Redis holds rebuildable, expiring data only.

## CI (last verified 2026-11-13)

No CI change has been recorded since 2026-11-13; the two failures below
remain the open items.

- Main is red: the Security Scan job fails because `aquasecurity/trivy-action@0.28.0` no longer resolves (tag deleted after the March 2026 Trivy compromise; fix is the `v0.36.0` bump in `.github/workflows/ci.yml`).
- API Lint & Type Check also fails (exit 1); cause still under investigation — triage procedure in `docs/runbooks/api-lint-typecheck.md`.
- See `docs/runbooks/TROUBLESHOOTING.md` (CI section) for details.

## Next actions

- [ ] Bump `aquasecurity/trivy-action` to `v0.36.0` in `.github/workflows/ci.yml` (one line).
- [ ] Run the API lint/type check locally from `services/api` and record the first error here.
- [ ] After the Trivy bump, re-run CI and update this file with the verified result.
