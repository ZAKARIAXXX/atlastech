# Runbook — API service operations

Operating the AtlasTech FastAPI service (`services/api`, Python 3.11)
in the local Compose environment. Local setup itself is covered by
`local-development.md`; this runbook covers the running service.

## Service facts

- Listens on port `8000` in the local environment.
- Depends on PostgreSQL (source of truth) and Redis (cache only —
  see ADR-006 for the degradation contract).
- Configuration comes from the environment; required secrets fail fast
  at startup when missing (see `environment-and-secrets.md`).

## Health checks

```bash
curl -s http://localhost:8000/health
docker compose ps        # api should report healthy/running
docker compose logs api --tail 50
```

A healthy API with an unhealthy database is not healthy: if `/health`
passes but data endpoints 500, go to `postgres-operations.md`.

## Restart procedure

```bash
docker compose restart api
docker compose logs api --follow   # confirm clean startup, no tracebacks
curl -s http://localhost:8000/health
```

Restart is safe at any time: the API holds no durable state. Anything
that must survive a restart belongs in PostgreSQL.

## Reading the logs

- Startup traceback mentioning an environment variable → fail-fast
  config check fired; fix `.env`, do not patch the code to skip it.
- Repeated `connection refused` to Redis → the API should degrade to
  PostgreSQL per ADR-006; if requests fail instead, that is a bug —
  record the endpoint and the error, then see `redis-operations.md`.
- A single endpoint 500ing with a traceback is an application bug, not
  an operations problem: capture the full traceback and the request
  that triggered it before restarting anything.

## Failure table

| Symptom | Likely cause | First action |
| --- | --- | --- |
| Port 8000 already in use | A previous dev process is still running | Find and stop the old process; do not change the port to hide it |
| API exits immediately at startup | Missing/invalid required env var | Read the first traceback line; fix `.env` |
| All data endpoints 500 | PostgreSQL down or unreachable | `postgres-operations.md` health checks |
| Slow responses, DB healthy | Redis down and cache misses hitting PostgreSQL | `redis-operations.md`; confirm the degradation contract holds |
