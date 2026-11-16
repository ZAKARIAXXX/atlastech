# Runbook — Local Development

How to get AtlasTech running on a developer machine, from the actual
`Makefile`, `docker-compose.yml`, and `.env.example` in this repository.

## Prerequisites

- Docker Desktop v24+
- Node.js 22+
- Python 3.11+

## 1. Configure the environment

```bash
cp .env.example .env
```

Then replace every placeholder in `.env`. These variables are **required** —
`docker-compose.yml` refuses to start without them:

| Variable | Used by |
|---|---|
| `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` | PostgreSQL 16 |
| `ATLASTECH_DATABASE_URL` | API → PostgreSQL |
| `ATLASTECH_REDIS_PASSWORD`, `ATLASTECH_REDIS_URL` | Redis 7 / API → Redis |
| `ATLASTECH_JWT_SECRET_KEY` | API auth (≥ 32 characters in production) |
| `ATLASTECH_API_KEY` | Agent telemetry ingestion (≥ 16 characters in production) |

Optional: `NEXT_PUBLIC_API_URL` (defaults to `http://localhost:8000/api/v1`)
and `ATLASTECH_ENVIRONMENT` (defaults to `development`).

Never commit `.env` — it is git-ignored; `.env.example` is the template.

## 2. Start — pick one mode

### Option A: everything in Docker (`make up`)

```bash
make up        # docker compose up -d --build
```

| Service | Address | Notes |
|---|---|---|
| Web dashboard | http://localhost:3000 | Next.js 15 |
| API | http://localhost:8000 | FastAPI; `/docs` and `/health` |
| PostgreSQL | 127.0.0.1:5432 | localhost only |
| Redis | 127.0.0.1:6379 | localhost only, password-protected |

Startup order is enforced: the API waits for PostgreSQL and Redis
healthchecks (`pg_isready`, `redis-cli ping`) via
`depends_on: condition: service_healthy`, and the web waits for the API.

### Option B: services on the host (`make dev`)

For debugging the API or web directly:

```bash
make install   # pip install -e ".[dev]" (API) + npm install (web, schemas)
make dev       # compose starts only PostgreSQL + Redis;
               # then Alembic migrations, uvicorn --reload :8000,
               # and the Next.js dev server
```

## 3. Verify

```bash
curl http://localhost:8000/health     # API health
open http://localhost:8000/docs       # interactive API docs
open http://localhost:3000            # dashboard
```

## 4. Daily commands

| Command | What it does |
|---|---|
| `make help` | List all Makefile targets |
| `make test` | API pytest with coverage + schemas typecheck |
| `make lint` | Ruff (API) + ESLint (web) |
| `make typecheck` | mypy (API) + TypeScript (web, schemas) |
| `make build` | Production build of the web app |
| `make clean` | Remove build artifacts and caches |
| `make down` | Stop all services |

## 5. Stop and reset

`make down` stops the stack and **keeps** the data in the named volumes
(`postgres_data`, `redis_data`). `docker compose down -v` **deletes** those
volumes and all local data with them — take a backup first
(see `database-backup-restore.md`).
