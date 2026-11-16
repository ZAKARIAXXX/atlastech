# ADR-005 — Docker Compose as the Local Environment

## Status

Accepted

## Context

AtlasTech runs four services together: a Next.js 15 web dashboard, a FastAPI
backend, PostgreSQL 16, and Redis 7. The API must not start before the
database and cache are healthy, secrets differ per machine, and the manual
start sequence in the README (start infrastructure, migrate, run uvicorn,
run the dev server) is easy to get wrong or out of order. Every developer
machine needs the same environment, started the same way.

## Decision

- **Docker Compose** (`docker-compose.yml`) is the canonical local
  environment. `make up` (`docker compose up -d --build`) starts the whole
  platform in one command.
- **Healthcheck-gated startup:** PostgreSQL (`pg_isready`) and Redis
  (`redis-cli ping`) define healthchecks, and dependents use
  `depends_on: condition: service_healthy` — the API waits for both stores,
  the web waits for the API.
- **Localhost-only datastores:** PostgreSQL binds `127.0.0.1:5432` and Redis
  binds `127.0.0.1:6379`; only the web (3000) and API (8000) ports are
  published more broadly.
- **Persistent state in named volumes:** `postgres_data` and `redis_data`
  survive container restarts and `docker compose down`.
- **Fail-fast configuration:** required secrets are declared
  `${VAR:?… is required}` in the Compose file and templated in
  `.env.example`; the stack refuses to start with a missing secret instead
  of using a default.

## Consequences

- One command brings the platform up identically on any machine with Docker.
- The Compose file is a contract: adding a required environment variable
  means updating `.env.example` and the local development runbook in the
  same change.
- Host-run mode (`make dev`) remains available for debugging, but Compose is
  the reference environment when behaviour differs between the two.
- `docker compose down -v` is destructive (it deletes both named volumes) —
  see `docs/runbooks/database-backup-restore.md` before using it.
