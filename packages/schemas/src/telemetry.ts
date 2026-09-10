export interface DeviceTelemetry {
  hostname: string;
  ip_address: string;
  mac_address: string;
  os_version: string;
  cpu_percent: number;
  ram_percent: number;
  disk_percent: number;
  gateway_reachable: boolean;
  dns_resolution_ok: boolean;
  critical_services: ServiceStatus[];
  logged_in_user: string | null;
  timestamp: string;
}

export interface ServiceStatus {
  name: string;
  display_name: string;
  status: "running" | "stopped" | "paused" | "error";
  pid: number | null;
}

export interface TelemetryResponse {
  device_id: string;
  received_at: string;
  status: "accepted" | "rejected";
}
