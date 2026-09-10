# AtlasTech End-to-End Operational Failure Scenario

This runbook documents and proves the core operational loop:

$$\text{Infrastructure Fault} \longrightarrow \text{Telemetry Agent} \longrightarrow \text{Automated Ingestion} \longrightarrow \text{Threshold Alert} \longrightarrow \text{Console Triage} \longrightarrow \text{Remote Diagnostic} \longrightarrow \text{Remediation} \longrightarrow \text{Resolution}$$

---

## 🔁 The Complete 7-Step Life of an Incident

```mermaid
sequenceDiagram
    autonumber
    actor Tech as Technician / Console
    participant Win as Windows Client (AT-PC-024)
    participant Agent as PowerShell Collector
    participant API as FastAPI Ingestion & Engine
    participant DB as PostgreSQL Database

    Note over Win,Agent: Phase 1: Healthy State
    Agent->>API: POST /v1/telemetry (dns_resolution_ok: true)
    API->>DB: Record telemetry & update status="online"

    Note over Win: Phase 2: Fault Injection (Chaos)
    Win->>Win: DNS misconfigured / resolver cache broken
    Agent->>API: POST /v1/telemetry (dns_resolution_ok: false)
    API->>DB: ThresholdEngine detects fault -> creates CRITICAL Incident

    Note over Tech,API: Phase 3: Investigation & Diagnostic
    Tech->>API: GET /v1/incidents?severity=critical
    Tech->>API: POST /v1/diagnostics/execute (playbook: "dns-diag")
    API->>Win: Remote diagnostic runs & records findings
    API->>DB: Append diagnostic output to IncidentEvents

    Note over Win,Tech: Phase 4: Remediation & Resolution
    Win->>Win: DNS restored to DC (192.168.10.10)
    Agent->>API: POST /v1/telemetry (dns_resolution_ok: true)
    Tech->>API: PATCH /v1/incidents/{id} (status: "resolved")
    API->>DB: Mark incident resolved with timestamp
```

---

## 🛠️ Step-by-Step Execution Guide

### Step 1: Baseline Telemetry
On client workstation `AT-PC-024`:
```powershell
.\agents\collector\collector.ps1 -ApiUrl "http://192.168.10.1:8000/api/v1/telemetry"
```
*Expected: Device `AT-PC-024` shows green status lights on Operations Console (`http://localhost:3000`).*

---

### Step 2: Inject Chaos Fault (DNS Outage)
On client workstation `AT-PC-024`:
```powershell
.\infra\chaos\inject-dns-fault.ps1
```
*Expected:*
1. PowerShell agent detects `dns_resolution_ok = $false`.
2. Transmits payload to API.
3. API ThresholdEngine generates ticket: **`[DNS] Resolution Failure on AT-PC-024`** with `CRITICAL` severity.
4. Open the **Incident Desk** on `http://localhost:3000` to inspect the newly opened incident.

---

### Step 3: Run Remote Diagnostic Playbook
From the web console (or API):
1. Click **"Run Diag"** on `AT-PC-024`.
2. Select **"DNS & Name Resolution Diagnostic"**.
3. View the terminal output identifying failed domain controller lookup.

---

### Step 4: Remediate & Resolve
On client workstation `AT-PC-024`:
```powershell
.\infra\chaos\reset-chaos.ps1
```
1. DNS client cache is cleared and adapter DNS is reset to `192.168.10.10`.
2. Collector agent sends healthy heartbeat.
3. On the web dashboard, click **"Resolve Ticket"**.
