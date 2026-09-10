export type Severity = "critical" | "high" | "medium" | "low";

export type IncidentStatus =
  | "open"
  | "in_progress"
  | "awaiting_user"
  | "resolved"
  | "closed";

export type IncidentSource = "automated" | "manual" | "user_report";

export interface Incident {
  id: string;
  title: string;
  description: string;
  severity: Severity;
  status: IncidentStatus;
  source: IncidentSource;
  device_hostname: string;
  assigned_technician_id: string | null;
  created_at: string;
  updated_at: string;
  resolved_at: string | null;
}

export interface IncidentEvent {
  id: string;
  incident_id: string;
  event_type:
    | "created"
    | "status_change"
    | "comment"
    | "diagnostic_run"
    | "resolved";
  payload: Record<string, unknown>;
  created_by: string;
  created_at: string;
}

export interface DiagnosticResult {
  incident_id: string;
  hostname: string;
  tests: DiagnosticTest[];
  summary: string;
  suggested_root_cause: string | null;
  run_at: string;
}

export interface DiagnosticTest {
  name: string;
  passed: boolean;
  output: string;
  severity: Severity;
}
