<div align="center">

# AtlasTech

### Enterprise IT Operations & AIOps Platform

[![CI](https://github.com/ZAKARIAXXX/atlastech/actions/workflows/ci.yml/badge.svg)](https://github.com/ZAKARIAXXX/atlastech/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Next.js 15](https://img.shields.io/badge/next.js-15-black.svg)](https://nextjs.org/)

A full-lifecycle IT operations platform built on a simulated enterprise infrastructure.

**Infrastructure generates the problems. The platform receives, tracks, analyzes, and helps resolve them.**

</div>

---

## Architecture

```
                        ATLASTECH
                           │
                 ┌─────────┴─────────┐
                 │                   │
          ENTERPRISE LAB        IT PLATFORM
                 │                   │
       ┌─────────┼─────────┐         │
       │         │         │         │
      AD        DNS       DHCP    Helpdesk
       │         │         │         │
       └─────────┼─────────┘         │
                 │                   │
          Windows Clients ──── Monitoring
                 │                   │
                 └─────────┬─────────┘
                           │
                        Telemetry
                           │
                    ┌──────┴──────┐
                    │             │
                   Data        Event Logs
                    │             │
                    └──────┬──────┘
                           │
                       AI / ML
                           │
             ┌─────────────┼─────────────┐
             │             │             │
          Triage       Detection      Prediction
             │             │             │
             └─────────────┼─────────────┘
                           │
                     Technician
                           │
                       Resolution
                           │
                    Knowledge Base
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 15, TypeScript, Tailwind CSS v4 |
| Backend | FastAPI, Python 3.11, SQLAlchemy 2.0, Pydantic v2 |
| Database | PostgreSQL 16, Redis 7 |
| Agent | PowerShell 5.1+ / PowerShell Core |
| Infra | Docker Compose, Vagrant (lab VMs) |
| CI/CD | GitHub Actions |
| Future AI | pgvector, sentence-transformers, scikit-learn |

## Repository Structure

```
atlastech/
├── apps/
│   └── web/                 # Next.js 15 operations dashboard
├── services/
│   └── api/                 # FastAPI backend (telemetry ingestion, incidents, devices)
├── agents/
│   └── collector/           # PowerShell telemetry collector for Windows endpoints
├── infra/
│   ├── lab/                 # Vagrant/Docker lab provisioning (atlastech.local)
│   └── chaos/               # Fault injection scripts (DNS, disk, SMB, print)
├── packages/
│   └── schemas/             # Shared TypeScript telemetry & incident schemas
├── docs/
│   ├── adr/                 # Architecture Decision Records
│   ├── architecture/        # System diagrams & network topology
│   ├── plans/               # Design documents & roadmaps
│   └── runbooks/            # Incident response & lab setup guides
├── docker-compose.yml       # One-command local development
└── Makefile                 # Developer CLI commands
```

## Quick Start

### Prerequisites

- Docker Desktop v24+
- Node.js 22+
- Python 3.11+

### One-Command Start

```bash
# Clone the repository
git clone https://github.com/ZAKARIAXXX/atlastech.git
cd atlastech

# Start all services (PostgreSQL, Redis, API, Web)
make up
```

### Manual Start

```bash
# Start infrastructure
docker compose up -d postgres redis

# Start API
cd services/api
pip install -e .
alembic upgrade head
uvicorn app.main:app --reload --port 8000 &

# Start Web Dashboard
cd apps/web
npm install
npm run dev
```

### Access

| Service | URL |
|---------|-----|
| Dashboard | http://localhost:3000 |
| API Docs | http://localhost:8000/docs |
| API Health | http://localhost:8000/health |

## Running the Telemetry Collector

On any Windows endpoint:

```powershell
# Run directly
.\agents\collector\collector.ps1 -ApiUrl "http://YOUR_API:8000/api/v1/telemetry"

# Install as Windows Scheduled Task
.\agents\collector\install.ps1 -ApiUrl "http://YOUR_API:8000/api/v1/telemetry"
```

## Development

```bash
make help       # Show all commands
make dev        # Start in development mode
make test       # Run all tests
make lint       # Lint all code
make typecheck  # Type-check all code
make build      # Build production artifacts
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | API health check |
| GET | `/api/v1/health/` | Detailed health status |
| GET | `/api/v1/devices/` | List all devices |
| POST | `/api/v1/devices/` | Register a device |
| GET | `/api/v1/devices/{id}` | Get device details |
| POST | `/api/v1/telemetry/` | Ingest telemetry data |
| GET | `/api/v1/telemetry/latest/{hostname}` | Latest telemetry for device |
| GET | `/api/v1/incidents/` | List incidents (filterable) |
| POST | `/api/v1/incidents/` | Create incident |
| GET | `/api/v1/incidents/{id}` | Get incident details |

## Roadmap

- [x] **Phase 0** — Monorepo scaffolding & CI/CD
- [x] **Phase 1** — Backend API with full CRUD & DB migrations
- [x] **Phase 2** — PowerShell telemetry agent with threshold engine
- [x] **Phase 3** — Next.js operations dashboard with real-time data
- [x] **Phase 4** — Enterprise lab (AD/DNS/DHCP) & chaos engine
- [ ] **Phase 5** — AIOps: pgvector embeddings, RCA, anomaly detection

## Contributing & Commit Convention

All commits in this repository strictly follow [Conventional Commits](.github/COMMIT_CONVENTION.md) (e.g. `feat(api): ...`, `feat(lab): ...`, `fix(web): ...`).

To configure the commit template locally:

```bash
git config --local commit.template .gitmessage
```

## Architecture Decision Records

All major technical decisions are documented in [`docs/adr/`](docs/adr/):

- [ADR-001](docs/adr/ADR-001-fastapi-backend.md) — FastAPI as Backend Framework
- [ADR-002](docs/adr/ADR-002-nextjs-frontend.md) — Next.js 15 as Frontend Framework

## License

MIT
