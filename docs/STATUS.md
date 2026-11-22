# AtlasTech — Status

Active development. See the Roadmap in README.md for the current phase.

## CI status (2026-11-22)

- CI is currently red on the latest head. The Security Scan job is
  blocked by the retired `aquasecurity/trivy-action@0.28.0` tag; the
  fix is a one-line bump to `v0.36.0` in `.github/workflows/ci.yml`
  (pending). The API Lint & Type Check failure is still under
  investigation — no fix proposed until the failing log is read.

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

## Documentation (2026-11-18)

- Added runbooks for PostgreSQL operations
  (`docs/runbooks/postgres-operations.md`), API service operations
  (`docs/runbooks/api-operations.md`), and environment variables and
  secrets (`docs/runbooks/environment-and-secrets.md`).
- Added ADR-007 recording the healthcheck and readiness policy:
  dependents wait for healthy, health reflects dependencies honestly,
  and services fail fast instead of failing vague.

## Documentation (2026-11-19)

- Added runbooks for logging and monitoring
  (`docs/runbooks/logging-and-monitoring.md`) and performance
  troubleshooting (`docs/runbooks/performance-troubleshooting.md`).
- Added ADR-008 recording the API versioning and error format policy:
  major-version URL prefixes, backwards-compatible changes only within
  a major version, and one error envelope for every endpoint.

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
