# Runbook — Logging and monitoring

Where AtlasTech's logs live, how to read them, and what to capture when
something goes wrong in the local environment.

## Principles

- Logs are the first evidence in any incident. Read them before
  restarting anything; a restart destroys the scene.
- Every service logs to stdout/stderr; Docker Compose collects them.
  There is no separate log server in the local environment.
- Secrets never appear in logs. If a log line contains a token or a
  connection string, treat it as a committed-secret incident (see the
  environment and secrets runbook).

## Reading logs

Whole stack, live:

```bash
docker compose logs -f
```

One service, last 200 lines:

```bash
docker compose logs --tail=200 api
docker compose logs --tail=200 web
docker compose logs --tail=200 postgres
docker compose logs --tail=200 redis
```

A time window (during an incident, always bound the window):

```bash
docker compose logs --since 30m api
```

## What each service logs

- **API (FastAPI, :8000)** — one line per request: method, path, status,
  duration. Unhandled errors log a traceback with the request context.
  A healthy API under light use is mostly 200s; a wall of 500s with the
  same traceback is one bug, not many.
- **Web (Next.js, :3000)** — build and render errors, failed API calls
  from the server side. Client-side errors appear in the browser
  console, not here.
- **PostgreSQL (127.0.0.1:5432)** — startup, checkpoints, connection
  errors, and slow statements when logging is enabled. Authentication
  failures here with a healthy API usually mean the credentials in
  `.env` and the database disagree.
- **Redis (127.0.0.1:6379)** — startup, persistence (RDB) events, memory
  warnings. Redis is rebuildable cache only (ADR-006); its logs matter
  for performance questions, rarely for correctness.

## Health signals without reading logs

```bash
docker compose ps        # state + healthcheck status per service
curl -s localhost:8000/health   # API view of its dependencies
docker stats --no-stream        # CPU / memory per container
```

Readiness and healthcheck semantics are defined in ADR-007: a service
reporting unhealthy is information, not noise — do not restart it away
before capturing its logs.

## Capturing evidence for an incident

1. Note the wall-clock time the symptom started.
2. Save the bounded log window for every involved service:
   `docker compose logs --since <window> <service> > incident-<service>.log`
3. Record `docker compose ps` and the failing request (method, path,
   status, response body) in the incident notes.
4. Only then restart or change anything.

## Failure table

| Symptom | Likely cause | First check |
|---|---|---|
| No logs from a service | Container never started or crashed pre-logging | `docker compose ps`, then `docker compose up <service>` in the foreground |
| API logs stop mid-request | Process killed (OOM) or container restarted | `docker stats`, host memory, `docker compose ps` restart count |
| Postgres log full of auth failures | `.env` credentials vs database mismatch | Environment and secrets runbook |
| Redis memory warnings | Cache growing without TTLs | ADR-006 boundaries; Redis operations runbook |
| Timestamps look wrong | Container timezone vs host timezone | Compare `date` on host and in container; log in UTC when correlating |
