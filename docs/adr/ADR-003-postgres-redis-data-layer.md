# ADR-003 — PostgreSQL + Redis as the Data Layer

## Status

Accepted

## Context

AtlasTech ingests high-volume telemetry from Windows endpoints, stores devices, incidents, and telemetry records, and serves a real-time operations dashboard. The data layer needs:

- Reliable relational storage for devices, incidents, and telemetry history.
- Fast caching and real-time data access for the dashboard.
- A proven, self-hostable stack that runs in Docker Compose for local development.

## Decision

- **PostgreSQL 16** as the primary relational database (devices, incidents, telemetry records), accessed via SQLAlchemy 2.0.
- **Redis 7** as the cache and real-time data layer for the dashboard.
- Both services run in Docker Compose alongside the API and web app for one-command local development (`make up`).

## Consequences

- PostgreSQL gives us ACID guarantees, migrations via Alembic, and a clear schema for incidents and telemetry.
- Redis keeps dashboard reads fast and decouples real-time updates from the relational store.
- Two data stores add operational overhead (backups, monitoring), but both are standard, well-understood tools that fit the Docker Compose workflow.
- Future AI work (Phase 5) can build on PostgreSQL via pgvector for embeddings.
