# ADR-007 — Healthcheck and readiness policy

- Status: Accepted
- Date: 2026-11-18
- Related: ADR-003 (Postgres & Redis data layer), ADR-005 (Docker
  Compose local environment), ADR-006 (Redis usage boundaries)

## Context

The local Compose stack has four moving parts: the Next.js web app,
the FastAPI service, PostgreSQL, and Redis. Without an explicit
readiness policy, "the stack is up" is ambiguous: containers can be
running while the database is still recovering, or the API can accept
requests it cannot serve. Ambiguity at startup produces the worst
class of local failures — intermittent, order-dependent, and hard to
reproduce.

## Decision

Every service defines a real healthcheck, and dependents wait for
healthy, not merely started:

- **PostgreSQL** — `pg_isready` against the configured user/database.
- **Redis** — `redis-cli ping`.
- **API** — its `/health` endpoint must answer successfully.
- **Web** — starts after the API reports healthy.

Two rules complete the policy:

1. **Health reflects dependencies honestly.** The API's health is not
   green if it cannot reach PostgreSQL. Redis is the exception: per
   ADR-006 the API degrades to PostgreSQL when Redis is down, so
   Redis health is reported but does not gate API readiness.
2. **Fail fast beats fail vague.** A service that cannot meet its
   contract (missing required configuration, database unreachable at
   startup) exits with a clear error instead of serving degraded
   behaviour silently. See `environment-and-secrets.md`.

## Consequences

- `docker compose up` has a deterministic meaning: when it returns,
  the stack can serve requests, or it has failed loudly.
- Startup is slightly slower; that cost is accepted in exchange for
  reproducible local environments.
- Runbooks can treat health endpoints as ground truth
  (`api-operations.md`, `postgres-operations.md`,
  `redis-operations.md` all build on these checks).
- The same checks are the natural probes if the stack is ever
  deployed beyond the local lab; no new mechanism will be needed.
