# AtlasTech — System Design Document

**Date:** 2026-09-10
**Status:** Active
**Version:** 0.1.0

## 1. Overview

AtlasTech is a full-lifecycle Enterprise IT Operations & AIOps platform built on a simulated corporate infrastructure. The platform demonstrates end-to-end systems engineering: infrastructure fault generation, telemetry collection, automated incident creation, technician workflows, and AI-assisted root cause analysis.

## 2. Goals

- Build a realistic enterprise IT environment (Active Directory, DNS, DHCP, file shares)
- Create a production-grade operations platform (helpdesk, asset management, monitoring)
- Implement a lightweight telemetry agent for Windows endpoints
- Automate incident creation from threshold breaches
- Eventually layer AI/ML for ticket triage, anomaly detection, and RCA

## 3. Phase Plan

### Phase 0: Scaffolding & Spec (Current)
- Monorepo structure with CI/CD
- Docker Compose for local dev
- ADRs for major tech decisions
- Shared TypeScript schemas

### Phase 1: Backend & DB
- FastAPI with full CRUD endpoints
- PostgreSQL with Alembic migrations
- Telemetry ingestion pipeline
- Incident management API

### Phase 2: Telemetry Agent
- PowerShell collector on Windows endpoints
- System vitals (CPU, RAM, disk, network, services)
- Heartbeat every 30s via HTTPS
- Threshold engine for alert generation

### Phase 3: Operations Dashboard
- Next.js 15 with Tailwind CSS
- Fleet health overview with real-time data
- Incident management console
- Technician diagnostic launcher

### Phase 4: Enterprise Lab & Chaos
- Automated Vagrant/Docker lab provisioning
- atlastech.local domain environment
- Fault injection scripts (DNS, disk, SMB, print)
- PowerShell diagnostic automation

### Phase 5: AIOps & Knowledge
- pgvector embeddings for resolved incidents
- Similarity search against historical tickets
- LLM-assisted root cause analysis
- Anomaly detection with scikit-learn

## 4. Network Topology

```
Firewall / Router
       │
    Core Switch
       │
  ┌────┼────┬────┬────┐
  │    │    │    │    │
V10  V20  V30  V40  V50  V100
 IT   HR  Fin  Sales Mgmt Servers
```

## 5. Data Flow

1. PowerShell agent collects system telemetry every 30s
2. Agent POSTs JSON to `POST /api/v1/telemetry/`
3. Backend stores record linked to device in PostgreSQL
4. Threshold engine checks for breaches (disk > 90%, DNS failure, service down)
5. Breached thresholds auto-create incidents
6. Dashboard polls/subscribes for real-time display
7. (Future) Resolved incidents embedded for AI similarity search
