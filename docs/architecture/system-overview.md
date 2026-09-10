# AtlasTech — System Architecture Overview

## High-Level Architecture

```mermaid
flowchart LR
    subgraph Endpoints["Windows Endpoints"]
        A[PowerShell Collector] -->|HTTPS POST /v1/telemetry| B[FastAPI Backend]
    end

    subgraph Platform["AtlasTech Platform"]
        B --> C[(PostgreSQL 16)]
        B --> D[Threshold Engine]
        D -->|Breached| E[Auto-Incident Creator]
        E --> C
        B --> F[REST API]
        F --> G[Next.js Dashboard]
    end

    subgraph Intelligence["Future: AIOps Layer"]
        C --> H[pgvector Embeddings]
        H --> I[Similarity Search]
        I --> J[AI Root Cause Suggestion]
    end
```

## Network Topology

```mermaid
flowchart TD
    FW[Firewall / Router] --> SW[Core Switch]
    SW --> V10[VLAN 10 — IT<br/>192.168.10.0/24]
    SW --> V20[VLAN 20 — HR<br/>192.168.20.0/24]
    SW --> V30[VLAN 30 — Finance<br/>192.168.30.0/24]
    SW --> V40[VLAN 40 — Sales<br/>192.168.40.0/24]
    SW --> V50[VLAN 50 — Management<br/>192.168.50.0/24]
    SW --> SRV[VLAN 100 — Servers<br/>192.168.100.0/24]
```

## Data Flow

1. **Telemetry Collection**: PowerShell agent on each endpoint gathers system vitals every 30 seconds.
2. **Ingestion**: Agent POSTs JSON payload to `POST /api/v1/telemetry/`.
3. **Storage**: Backend writes telemetry record linked to device in PostgreSQL.
4. **Threshold Engine**: Background worker checks for threshold breaches (disk > 90%, DNS failure, service down).
5. **Auto-Incident**: Breached thresholds auto-create incidents in the incidents table.
6. **Dashboard**: Next.js polls or subscribes to incidents and telemetry for real-time display.
7. **Future — AI**: Resolved incidents are embedded and stored for similarity search against new incidents.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 15, TypeScript, Tailwind CSS v4, shadcn/ui |
| Backend | FastAPI, Python 3.11, SQLAlchemy 2.0, Pydantic v2 |
| Database | PostgreSQL 16, Redis 7 |
| Agent | PowerShell 5.1 / PowerShell Core |
| Infra | Docker Compose, Vagrant (lab VMs) |
| CI/CD | GitHub Actions |
| Future AI | pgvector, sentence-transformers, scikit-learn |
