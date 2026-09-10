# AtlasTech Lab Setup Guide

## Prerequisites

- Docker Desktop (v24+)
- Node.js 22+
- Python 3.11+
- (Optional) Vagrant + VirtualBox for full Windows domain lab

## Quick Start (API + DB)

```bash
# From project root
docker compose up -d postgres redis

# Run migrations
cd services/api
pip install -e .
alembic upgrade head

# Start API
uvicorn app.main:app --reload --port 8000
```

## Quick Start (Full Stack)

```bash
# Start everything
make up

# Or individually
docker compose up -d
cd apps/web && npm run dev
```

## Running the Collector

On a Windows machine:

```powershell
.\agents\collector\collector.ps1 -ApiUrl "http://YOUR_API_HOST:8000/api/v1/telemetry"
```

## Database Access

```bash
docker exec -it atlastech-postgres psql -U atlastech -d atlastech
```
