# ADR-001: FastAPI as Backend Framework

## Status

Accepted

## Context

AtlasTech requires a high-performance, async-first backend to handle concurrent telemetry ingestion from multiple Windows endpoints, manage incident CRUD operations, and serve the Next.js web dashboard. The backend must also integrate smoothly with PostgreSQL (via async drivers) and leave a clear path for future ML model integration.

## Decision

We chose **FastAPI** (Python 3.11+) as the backend framework for the following reasons:

- Native async/await with `asyncpg` for PostgreSQL
- Automatic OpenAPI specification generation
- Pydantic v2 for high-performance request/response validation
- Mature ecosystem for ML/AI integration (scikit-learn, PyTorch, sentence-transformers)
- Strong typing alignment with the team's TypeScript-first frontend

## Alternatives Considered

| Framework | Pros | Cons |
|-----------|------|------|
| **NestJS** | Full TypeScript stack, type safety across layers | ML integration requires Python interop; heavier boilerplate for simple REST |
| **Express/Fastify** | Lightweight, huge ecosystem | No native async DB drivers as mature as SQLAlchemy 2.0+asyncpg |
| **Django REST Framework** | Mature, battle-tested ORM | Sync-first design; async support still maturing; heavier for microservices |

## Consequences

- The backend is Python-based, creating a polyglot monorepo (TypeScript frontend + Python backend + PowerShell agent). This is intentional to demonstrate cross-platform engineering.
- Future ML integration (embeddings, anomaly detection) can be added directly within the same service or as a sibling Python service without FFI overhead.
- Team members must be comfortable with both Python and TypeScript.
