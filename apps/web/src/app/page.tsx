"use client";

import React, { useEffect, useState } from "react";
import {
  AlertOctagon,
  AlertTriangle,
  CheckCircle,
  Globe,
  Laptop,
  Play,
  RefreshCw,
  Shield,
  Terminal,
  Wifi,
  WifiOff,
  Zap,
} from "lucide-react";

interface TelemetrySnapshot {
  cpu_percent: number;
  ram_percent: number;
  disk_percent: number;
  gateway_reachable: boolean;
  dns_resolution_ok: boolean;
  timestamp: string;
}

interface Device {
  id: string;
  hostname: string;
  ip_address: string;
  mac_address?: string;
  os_version: string;
  department?: string;
  status: string;
  created_at: string;
  updated_at: string;
  latest_telemetry?: TelemetrySnapshot;
}

interface IncidentEvent {
  id: string;
  event_type: string;
  payload?: any;
  created_by?: string;
  created_at: string;
}

interface Incident {
  id: string;
  title: string;
  description: string;
  severity: "critical" | "high" | "medium" | "low";
  status: "open" | "in_progress" | "resolved" | "closed";
  source: string;
  device_id?: string;
  device_hostname?: string;
  resolved_at?: string;
  created_at: string;
  events?: IncidentEvent[];
}

interface OpsStats {
  open_incidents: number;
  critical_incidents: number;
  in_progress_incidents: number;
  resolved_today: number;
  total_devices: number;
  devices_online: number;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export default function AtlasTechOperationsConsole() {
  const [activeTab, setActiveTab] = useState<"fleet" | "incidents" | "diagnostics" | "chaos">("fleet");
  const [devices, setDevices] = useState<Device[]>([]);
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [stats, setStats] = useState<OpsStats>({
    open_incidents: 0,
    critical_incidents: 0,
    in_progress_incidents: 0,
    resolved_today: 0,
    total_devices: 0,
    devices_online: 0,
  });
  const [loading, setLoading] = useState<boolean>(true);
  const [apiConnected, setApiConnected] = useState<boolean>(false);
  const [selectedIncident, setSelectedIncident] = useState<Incident | null>(null);
  const [selectedDevice, setSelectedDevice] = useState<Device | null>(null);
  const [diagnosticLogs, setDiagnosticLogs] = useState<string[]>([]);
  const [runningDiag, setRunningDiag] = useState<boolean>(false);
  const [severityFilter, setSeverityFilter] = useState<string>("all");

  const fetchData = async () => {
    try {
      const [statsRes, devRes, incRes] = await Promise.all([
        fetch(`${API_BASE}/incidents/stats/summary`).catch(() => null),
        fetch(`${API_BASE}/devices/`).catch(() => null),
        fetch(`${API_BASE}/incidents/`).catch(() => null),
      ]);

      if (statsRes?.ok && devRes?.ok && incRes?.ok) {
        setApiConnected(true);
        const statsData = await statsRes.json();
        const devData = await devRes.json();
        const incData = await incRes.json();

        setStats(statsData);
        setDevices(devData);
        setIncidents(incData);
      } else {
        setApiConnected(false);
        // Fallback demo state if backend is spinning up
        loadDemoState();
      }
    } catch {
      setApiConnected(false);
      loadDemoState();
    } finally {
      setLoading(false);
    }
  };

  const loadDemoState = () => {
    setStats({
      open_incidents: 3,
      critical_incidents: 1,
      in_progress_incidents: 1,
      resolved_today: 6,
      total_devices: 5,
      devices_online: 5,
    });
    setDevices([
      {
        id: "dev-01",
        hostname: "AT-PC-024",
        ip_address: "192.168.30.124",
        os_version: "Windows 11 Enterprise",
        department: "Finance",
        status: "online",
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        latest_telemetry: {
          cpu_percent: 42.1,
          ram_percent: 68.4,
          disk_percent: 96.2,
          gateway_reachable: true,
          dns_resolution_ok: false,
          timestamp: new Date().toISOString(),
        },
      },
      {
        id: "dev-02",
        hostname: "AT-PC-012",
        ip_address: "192.168.10.45",
        os_version: "Windows 11 Pro",
        department: "IT",
        status: "online",
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        latest_telemetry: {
          cpu_percent: 18.0,
          ram_percent: 44.5,
          disk_percent: 51.0,
          gateway_reachable: true,
          dns_resolution_ok: true,
          timestamp: new Date().toISOString(),
        },
      },
      {
        id: "dev-03",
        hostname: "AT-DC-01",
        ip_address: "192.168.10.10",
        os_version: "Windows Server 2022",
        department: "Infrastructure",
        status: "online",
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        latest_telemetry: {
          cpu_percent: 24.3,
          ram_percent: 55.0,
          disk_percent: 42.8,
          gateway_reachable: true,
          dns_resolution_ok: true,
          timestamp: new Date().toISOString(),
        },
      },
    ]);
    setIncidents([
      {
        id: "inc-01",
        title: "[DNS] Resolution Failure on AT-PC-024",
        description:
          "Endpoint failed internal domain DNS resolution for 'dc01.atlastech.local'. Active Directory shares unreachable.",
        severity: "critical",
        status: "open",
        source: "automated",
        device_hostname: "AT-PC-024",
        created_at: new Date().toISOString(),
        events: [
          {
            id: "ev-1",
            event_type: "telemetry_fault_detected",
            payload: { fault: "dns_failure" },
            created_at: new Date().toISOString(),
          },
        ],
      },
      {
        id: "inc-02",
        title: "[STORAGE] Volume C: Capacity Alert (96.2%) on AT-PC-024",
        description: "Storage utilization on drive C: reached 96.2%, exceeding 90% threshold.",
        severity: "high",
        status: "in_progress",
        source: "automated",
        device_hostname: "AT-PC-024",
        created_at: new Date().toISOString(),
      },
    ]);
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 8000);
    return () => clearInterval(interval);
  }, []);

  const handleResolveIncident = async (incidentId: string) => {
    try {
      if (apiConnected) {
        await fetch(`${API_BASE}/incidents/${incidentId}`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ status: "resolved", resolution_notes: "Resolved via Operations Console" }),
        });
      }
      setIncidents((prev) =>
        prev.map((inc) => (inc.id === incidentId ? { ...inc, status: "resolved", resolved_at: new Date().toISOString() } : inc))
      );
      setStats((s) => ({ ...s, open_incidents: Math.max(0, s.open_incidents - 1), resolved_today: s.resolved_today + 1 }));
    } catch (err) {
      console.error("Failed to resolve incident", err);
    }
  };

  const executeDiagnosticPlaybook = async (playbookId: string, playbookName: string, device: Device) => {
    setRunningDiag(true);
    setDiagnosticLogs([
      `[INIT] Dispatching playbook '${playbookName}' to endpoint ${device.hostname} (${device.ip_address})...`,
      `[POWERSHELL] Executing remote agent module...`,
    ]);

    try {
      if (apiConnected) {
        const res = await fetch(`${API_BASE}/diagnostics/execute`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            device_id: device.id,
            playbook_id: playbookId,
            incident_id: selectedIncident?.id,
          }),
        });
        const data = await res.json();
        setDiagnosticLogs((logs) => [
          ...logs,
          `[STDOUT] Execution ID: ${data.execution_id}`,
          `[STDOUT] Status: ${data.status.toUpperCase()}`,
          ...(data.output?.findings || []).map((f: string) => `[RESULT] ${f}`),
          `[SUCCESS] Diagnostic playbook complete.`,
        ]);
      } else {
        setTimeout(() => {
          setDiagnosticLogs((logs) => [
            ...logs,
            `[STDOUT] Ping test to Default Gateway (192.168.30.1): SUCCESS (latency < 1ms)`,
            `[STDOUT] Querying DNS SRV records for _ldap._tcp.dc._msdcs.atlastech.local...`,
            `[RESULT] Found Primary DC at 192.168.10.10`,
            `[SUCCESS] Playbook execution completed cleanly.`,
          ]);
        }, 1000);
      }
    } catch {
      setDiagnosticLogs((logs) => [...logs, `[ERROR] Failed to reach diagnostic runner service.`]);
    } finally {
      setRunningDiag(false);
    }
  };

  const triggerChaosFault = async (faultType: "dns" | "disk" | "service") => {
    const targetHost = devices[0]?.hostname || "AT-PC-001";
    let payload: any;

    if (faultType === "dns") {
      payload = {
        hostname: targetHost,
        ip_address: "192.168.30.100",
        os_version: "Windows 11",
        cpu_percent: 22.0,
        ram_percent: 50.0,
        disk_percent: 45.0,
        gateway_reachable: true,
        dns_resolution_ok: false,
      };
    } else if (faultType === "disk") {
      payload = {
        hostname: targetHost,
        ip_address: "192.168.30.100",
        os_version: "Windows 11",
        cpu_percent: 30.0,
        ram_percent: 60.0,
        disk_percent: 97.4,
        gateway_reachable: true,
        dns_resolution_ok: true,
      };
    } else {
      payload = {
        hostname: targetHost,
        ip_address: "192.168.30.100",
        os_version: "Windows 11",
        cpu_percent: 40.0,
        ram_percent: 75.0,
        disk_percent: 50.0,
        gateway_reachable: true,
        dns_resolution_ok: true,
        critical_services: [{ name: "spooler", display_name: "Print Spooler", status: "stopped" }],
      };
    }

    try {
      if (apiConnected) {
        await fetch(`${API_BASE}/telemetry/`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        await fetchData();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const filteredIncidents = incidents.filter((inc) => {
    if (severityFilter === "all") return true;
    return inc.severity === severityFilter;
  });

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 flex flex-col font-sans selection:bg-cyan-500 selection:text-black">
      {/* Top Header */}
      <header className="border-b border-zinc-800 bg-zinc-900/60 backdrop-blur-md px-6 py-4 sticky top-0 z-50 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="h-9 w-9 rounded-lg bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
            <Shield className="h-5 w-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-lg font-bold tracking-tight text-white">ATLASTECH</h1>
              <span className="text-xs px-2 py-0.5 rounded-full bg-cyan-950 text-cyan-400 border border-cyan-800 font-mono">
                ENTERPRISE ITOPS
              </span>
            </div>
            <p className="text-xs text-zinc-400">AIOps & Infrastructure Operations Console</p>
          </div>
        </div>

        {/* Status indicator & controls */}
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 text-xs font-mono px-3 py-1.5 rounded-md bg-zinc-900 border border-zinc-800">
            <span
              className={`h-2.5 w-2.5 rounded-full ${apiConnected ? "bg-emerald-500 animate-pulse" : "bg-amber-500"}`}
            />
            <span className="text-zinc-300">{apiConnected ? "API ONLINE" : "DEMO / STANDALONE"}</span>
          </div>

          <button
            onClick={fetchData}
            disabled={loading}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-zinc-300 bg-zinc-800 hover:bg-zinc-700 rounded-md border border-zinc-700 transition"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${loading ? "animate-spin" : ""}`} />
            Sync
          </button>
        </div>
      </header>

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-6 space-y-6">
        {/* KPI Stat Cards */}
        <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            icon={<AlertOctagon className="h-5 w-5 text-red-400" />}
            label="Critical Incidents"
            value={stats.critical_incidents.toString()}
            subtitle="Immediate remediation required"
            highlight={stats.critical_incidents > 0}
          />
          <StatCard
            icon={<AlertTriangle className="h-5 w-5 text-amber-400" />}
            label="Open Incidents"
            value={stats.open_incidents.toString()}
            subtitle="Active triage tickets"
          />
          <StatCard
            icon={<CheckCircle className="h-5 w-5 text-emerald-400" />}
            label="Resolved Today"
            value={stats.resolved_today.toString()}
            subtitle="Closed operations cases"
          />
          <StatCard
            icon={<Laptop className="h-5 w-5 text-cyan-400" />}
            label="Fleet Endpoints"
            value={`${stats.devices_online} / ${stats.total_devices || devices.length}`}
            subtitle="Online & transmitting vitals"
          />
        </section>

        {/* Navigation Tabs */}
        <div className="flex border-b border-zinc-800 gap-2">
          <TabButton
            active={activeTab === "fleet"}
            onClick={() => setActiveTab("fleet")}
            icon={<Laptop className="h-4 w-4" />}
            label="Fleet Asset Grid"
            badge={devices.length}
          />
          <TabButton
            active={activeTab === "incidents"}
            onClick={() => setActiveTab("incidents")}
            icon={<AlertTriangle className="h-4 w-4" />}
            label="Incident Triage Desk"
            badge={incidents.filter((i) => i.status !== "resolved").length}
          />
          <TabButton
            active={activeTab === "diagnostics"}
            onClick={() => setActiveTab("diagnostics")}
            icon={<Terminal className="h-4 w-4" />}
            label="Remote Diagnostics"
          />
          <TabButton
            active={activeTab === "chaos"}
            onClick={() => setActiveTab("chaos")}
            icon={<Zap className="h-4 w-4" />}
            label="Chaos / Fault Lab"
          />
        </div>

        {/* Tab 1: Fleet Grid */}
        {activeTab === "fleet" && (
          <div className="space-y-4">
            <div className="rounded-xl border border-zinc-800 bg-zinc-900/40 overflow-hidden">
              <div className="p-4 border-b border-zinc-800 flex items-center justify-between">
                <div>
                  <h2 className="text-sm font-semibold text-white">Registered Infrastructure Endpoints</h2>
                  <p className="text-xs text-zinc-400">Live CIM/WMI telemetry streamed via PowerShell Agent</p>
                </div>
                <span className="text-xs text-zinc-500 font-mono">{devices.length} Devices tracked</span>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-zinc-900/80 text-zinc-400 uppercase tracking-wider font-mono border-b border-zinc-800">
                    <tr>
                      <th className="py-3 px-4">Hostname / Dept</th>
                      <th className="py-3 px-4">IP & OS</th>
                      <th className="py-3 px-4">CPU Usage</th>
                      <th className="py-3 px-4">RAM Usage</th>
                      <th className="py-3 px-4">Disk (C:)</th>
                      <th className="py-3 px-4">Network & DNS</th>
                      <th className="py-3 px-4 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-zinc-800/60 font-sans">
                    {devices.map((device) => {
                      const t = device.latest_telemetry;
                      return (
                        <tr key={device.id} className="hover:bg-zinc-800/30 transition">
                          <td className="py-3.5 px-4">
                            <div className="font-semibold text-white flex items-center gap-2">
                              <span className="h-2 w-2 rounded-full bg-emerald-400" />
                              {device.hostname}
                            </div>
                            <span className="text-zinc-500 text-[11px]">{device.department || "General"}</span>
                          </td>
                          <td className="py-3.5 px-4 font-mono text-zinc-300">
                            <div>{device.ip_address}</div>
                            <span className="text-zinc-500 text-[11px] font-sans">{device.os_version}</span>
                          </td>
                          <td className="py-3.5 px-4">
                            {t ? (
                              <MetricGauge value={t.cpu_percent} label={`${t.cpu_percent}%`} />
                            ) : (
                              <span className="text-zinc-600">—</span>
                            )}
                          </td>
                          <td className="py-3.5 px-4">
                            {t ? (
                              <MetricGauge value={t.ram_percent} label={`${t.ram_percent}%`} />
                            ) : (
                              <span className="text-zinc-600">—</span>
                            )}
                          </td>
                          <td className="py-3.5 px-4">
                            {t ? (
                              <MetricGauge
                                value={t.disk_percent}
                                label={`${t.disk_percent}%`}
                                alert={t.disk_percent >= 90}
                              />
                            ) : (
                              <span className="text-zinc-600">—</span>
                            )}
                          </td>
                          <td className="py-3.5 px-4">
                            {t ? (
                              <div className="flex items-center gap-2">
                                <span
                                  className={`inline-flex items-center gap-1 text-[11px] px-1.5 py-0.5 rounded ${
                                    t.gateway_reachable ? "text-emerald-400 bg-emerald-950/50" : "text-red-400 bg-red-950/50"
                                  }`}
                                >
                                  {t.gateway_reachable ? <Wifi className="h-3 w-3" /> : <WifiOff className="h-3 w-3" />}
                                  GW
                                </span>
                                <span
                                  className={`inline-flex items-center gap-1 text-[11px] px-1.5 py-0.5 rounded ${
                                    t.dns_resolution_ok ? "text-emerald-400 bg-emerald-950/50" : "text-red-400 bg-red-950/50 font-bold"
                                  }`}
                                >
                                  <Globe className="h-3 w-3" />
                                  {t.dns_resolution_ok ? "DNS OK" : "DNS FAIL"}
                                </span>
                              </div>
                            ) : (
                              <span className="text-zinc-600">—</span>
                            )}
                          </td>
                          <td className="py-3.5 px-4 text-right">
                            <button
                              onClick={() => {
                                setSelectedDevice(device);
                                setActiveTab("diagnostics");
                              }}
                              className="px-2.5 py-1 text-[11px] bg-zinc-800 hover:bg-zinc-700 text-zinc-200 rounded border border-zinc-700 transition"
                            >
                              Run Diag
                            </button>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* Tab 2: Incident Triage */}
        {activeTab === "incidents" && (
          <div className="space-y-4">
            <div className="flex items-center justify-between gap-4">
              <div className="flex items-center gap-2">
                <span className="text-xs text-zinc-400">Filter Severity:</span>
                {["all", "critical", "high", "medium", "low"].map((sev) => (
                  <button
                    key={sev}
                    onClick={() => setSeverityFilter(sev)}
                    className={`text-xs px-2.5 py-1 rounded capitalize transition ${
                      severityFilter === sev
                        ? "bg-zinc-700 text-white font-semibold"
                        : "bg-zinc-900 text-zinc-400 hover:bg-zinc-800"
                    }`}
                  >
                    {sev}
                  </button>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Incident List */}
              <div className="lg:col-span-2 space-y-3">
                {filteredIncidents.map((inc) => (
                  <div
                    key={inc.id}
                    onClick={() => setSelectedIncident(inc)}
                    className={`p-4 rounded-xl border transition cursor-pointer ${
                      selectedIncident?.id === inc.id
                        ? "border-cyan-500 bg-cyan-950/20"
                        : "border-zinc-800 bg-zinc-900/40 hover:border-zinc-700"
                    }`}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex items-center gap-2">
                        <SeverityBadge severity={inc.severity} />
                        <span className="text-xs font-mono text-zinc-400 uppercase">{inc.status}</span>
                      </div>
                      <span className="text-[11px] text-zinc-500 font-mono">
                        {new Date(inc.created_at).toLocaleTimeString()}
                      </span>
                    </div>

                    <h3 className="text-sm font-semibold text-white mt-2">{inc.title}</h3>
                    <p className="text-xs text-zinc-400 mt-1 line-clamp-2">{inc.description}</p>

                    <div className="flex items-center justify-between mt-3 pt-3 border-t border-zinc-800/80">
                      <span className="text-xs text-zinc-400 flex items-center gap-1 font-mono">
                        <Laptop className="h-3.5 w-3.5 text-zinc-500" />
                        {inc.device_hostname || "System Core"}
                      </span>
                      {inc.status !== "resolved" && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleResolveIncident(inc.id);
                          }}
                          className="px-2.5 py-1 text-xs bg-emerald-950/80 hover:bg-emerald-900 text-emerald-300 border border-emerald-800 rounded transition"
                        >
                          Resolve Ticket
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>

              {/* Selected Incident Drawer / Details */}
              <div className="rounded-xl border border-zinc-800 bg-zinc-900/40 p-5 space-y-4 h-fit sticky top-24">
                <h3 className="text-sm font-semibold text-white flex items-center gap-2">
                  <Terminal className="h-4 w-4 text-cyan-400" />
                  Incident Triage & Evidence
                </h3>

                {selectedIncident ? (
                  <div className="space-y-4 text-xs">
                    <div>
                      <span className="text-zinc-500">Incident Title</span>
                      <p className="text-zinc-200 font-semibold mt-0.5">{selectedIncident.title}</p>
                    </div>

                    <div>
                      <span className="text-zinc-500">Root Cause Description</span>
                      <p className="text-zinc-300 bg-zinc-950 p-2.5 rounded border border-zinc-800 mt-1">
                        {selectedIncident.description}
                      </p>
                    </div>

                    <div>
                      <span className="text-zinc-500">Audit Trail / Events</span>
                      <div className="mt-1 space-y-1.5 font-mono text-[11px]">
                        {(selectedIncident.events || []).map((ev) => (
                          <div key={ev.id} className="p-2 rounded bg-zinc-950 border border-zinc-800/80">
                            <span className="text-cyan-400 font-bold">{ev.event_type}</span>
                            <div className="text-zinc-400 mt-0.5">{JSON.stringify(ev.payload || {})}</div>
                          </div>
                        ))}
                      </div>
                    </div>

                    <button
                      onClick={() => {
                        const targetDev = devices.find((d) => d.hostname === selectedIncident.device_hostname);
                        if (targetDev) setSelectedDevice(targetDev);
                        setActiveTab("diagnostics");
                      }}
                      className="w-full py-2 bg-cyan-600 hover:bg-cyan-500 text-black font-semibold rounded transition flex items-center justify-center gap-1.5"
                    >
                      <Play className="h-3.5 w-3.5" /> Launch Remote Playbook
                    </button>
                  </div>
                ) : (
                  <div className="text-zinc-500 text-xs py-8 text-center">
                    Select an incident to view live evidence and dispatch automated diagnostic playbooks.
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Tab 3: Remote Diagnostics */}
        {activeTab === "diagnostics" && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="space-y-3">
              <h2 className="text-sm font-semibold text-white">Select Automated Diagnostic Playbook</h2>

              <PlaybookCard
                title="DNS & Name Resolution Diagnostic"
                description="Tests resolution of dc01.atlastech.local and clears DNS cache."
                command="Resolve-DnsName 'dc01.atlastech.local'; ipconfig /displaydns"
                onRun={() =>
                  executeDiagnosticPlaybook(
                    "dns-diag",
                    "DNS & Name Resolution Diagnostic",
                    selectedDevice || devices[0]
                  )
                }
                disabled={runningDiag}
              />
              <PlaybookCard
                title="Full Network Stack Diagnostic"
                description="Tests gateway ping, verifies DHCP lease, and dumps IP routing table."
                command="Test-Connection (Get-NetRoute -DestinationPrefix '0.0.0.0/0').NextHop"
                onRun={() =>
                  executeDiagnosticPlaybook("net-diag", "Full Network Stack Diagnostic", selectedDevice || devices[0])
                }
                disabled={runningDiag}
              />
              <PlaybookCard
                title="Storage Vitals & Temp Cleanup"
                description="Scans C: drive temp directory bloat and calculates space reclamation."
                command="Get-ChildItem -Path $env:TEMP -Recurse | Measure-Object -Property Length -Sum"
                onRun={() =>
                  executeDiagnosticPlaybook(
                    "disk-cleanup",
                    "Storage Vitals & Temp Cleanup",
                    selectedDevice || devices[0]
                  )
                }
                disabled={runningDiag}
              />
            </div>

            {/* Terminal output box */}
            <div className="lg:col-span-2 rounded-xl border border-zinc-800 bg-black p-4 font-mono text-xs text-zinc-300 flex flex-col min-h-[380px]">
              <div className="flex items-center justify-between pb-3 mb-3 border-b border-zinc-800 text-zinc-500">
                <div className="flex items-center gap-2">
                  <Terminal className="h-4 w-4 text-cyan-400" />
                  <span>Terminal Diagnostic Output — {selectedDevice?.hostname || "Target Endpoint"}</span>
                </div>
                {runningDiag && <span className="text-cyan-400 animate-pulse font-bold">RUNNING...</span>}
              </div>

              <div className="flex-1 space-y-1 overflow-y-auto">
                {diagnosticLogs.length === 0 ? (
                  <div className="text-zinc-600 italic">Select a diagnostic playbook to execute on the endpoint.</div>
                ) : (
                  diagnosticLogs.map((log, i) => (
                    <div
                      key={i}
                      className={`${
                        log.includes("[ERROR]")
                          ? "text-red-400"
                          : log.includes("[SUCCESS]")
                          ? "text-emerald-400 font-bold"
                          : log.includes("[RESULT]")
                          ? "text-cyan-300"
                          : "text-zinc-400"
                      }`}
                    >
                      {log}
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        )}

        {/* Tab 4: Chaos & Fault Generator */}
        {activeTab === "chaos" && (
          <div className="rounded-xl border border-zinc-800 bg-zinc-900/40 p-6 space-y-6">
            <div>
              <h2 className="text-base font-semibold text-white flex items-center gap-2">
                <Zap className="h-5 w-5 text-amber-400" />
                AtlasTech Chaos & Fault Injection Suite
              </h2>
              <p className="text-xs text-zinc-400 mt-1">
                Inject real operational faults into the AtlasTech infrastructure to test automated telemetry alerts and triage.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <ChaosCard
                title="Scenario A: DNS Resolver Outage"
                description="Injects a DNS resolution failure to simulate broken internal name resolution."
                severity="CRITICAL"
                onTrigger={() => triggerChaosFault("dns")}
              />
              <ChaosCard
                title="Scenario B: Disk Space Exhaustion"
                description="Simulates C: drive volume capacity exceeding 97% to test threshold alerts."
                severity="CRITICAL"
                onTrigger={() => triggerChaosFault("disk")}
              />
              <ChaosCard
                title="Scenario C: Print Spooler Crash"
                description="Stops print spooler service to test critical Windows service health monitors."
                severity="MEDIUM"
                onTrigger={() => triggerChaosFault("service")}
              />
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

function StatCard({
  icon,
  label,
  value,
  subtitle,
  highlight = false,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
  subtitle: string;
  highlight?: boolean;
}) {
  return (
    <div
      className={`rounded-xl border p-4 bg-zinc-900/60 ${
        highlight ? "border-red-500/50 bg-red-950/10" : "border-zinc-800"
      }`}
    >
      <div className="flex items-center justify-between">
        <span className="text-xs text-zinc-400 font-medium">{label}</span>
        {icon}
      </div>
      <div className="mt-2 text-2xl font-bold font-mono text-white tracking-tight">{value}</div>
      <p className="mt-1 text-[11px] text-zinc-500">{subtitle}</p>
    </div>
  );
}

function TabButton({
  active,
  onClick,
  icon,
  label,
  badge,
}: {
  active: boolean;
  onClick: () => void;
  icon: React.ReactNode;
  label: string;
  badge?: number;
}) {
  return (
    <button
      onClick={onClick}
      className={`flex items-center gap-2 px-4 py-2.5 text-xs font-medium border-b-2 transition ${
        active
          ? "border-cyan-400 text-cyan-400 bg-cyan-950/20"
          : "border-transparent text-zinc-400 hover:text-zinc-200 hover:border-zinc-700"
      }`}
    >
      {icon}
      {label}
      {badge !== undefined && (
        <span
          className={`text-[10px] px-1.5 py-0.2 rounded-full font-mono ${
            active ? "bg-cyan-500 text-black font-bold" : "bg-zinc-800 text-zinc-400"
          }`}
        >
          {badge}
        </span>
      )}
    </button>
  );
}

function MetricGauge({ value, label, alert = false }: { value: number; label: string; alert?: boolean }) {
  const color = alert || value >= 90 ? "bg-red-500" : value >= 70 ? "bg-amber-500" : "bg-emerald-500";
  return (
    <div className="w-28 space-y-1">
      <div className="flex justify-between text-[11px] font-mono">
        <span className="text-zinc-400">{label}</span>
      </div>
      <div className="h-1.5 w-full bg-zinc-800 rounded-full overflow-hidden">
        <div className={`h-full rounded-full transition-all duration-500 ${color}`} style={{ width: `${Math.min(value, 100)}%` }} />
      </div>
    </div>
  );
}

function SeverityBadge({ severity }: { severity: string }) {
  const styles: Record<string, string> = {
    critical: "bg-red-950 text-red-400 border-red-800",
    high: "bg-orange-950 text-orange-400 border-orange-800",
    medium: "bg-amber-950 text-amber-400 border-amber-800",
    low: "bg-emerald-950 text-emerald-400 border-emerald-800",
  };
  return (
    <span
      className={`text-[10px] font-mono font-bold uppercase px-2 py-0.5 rounded border ${
        styles[severity] || styles.low
      }`}
    >
      {severity}
    </span>
  );
}

function PlaybookCard({
  title,
  description,
  command,
  onRun,
  disabled,
}: {
  title: string;
  description: string;
  command: string;
  onRun: () => void;
  disabled: boolean;
}) {
  return (
    <div className="p-4 rounded-xl border border-zinc-800 bg-zinc-900/40 space-y-2">
      <h3 className="text-xs font-semibold text-white">{title}</h3>
      <p className="text-[11px] text-zinc-400">{description}</p>
      <div className="p-2 rounded bg-zinc-950 border border-zinc-800 font-mono text-[10px] text-zinc-500 truncate">
        {command}
      </div>
      <button
        onClick={onRun}
        disabled={disabled}
        className="w-full py-1.5 text-xs bg-zinc-800 hover:bg-zinc-700 text-zinc-200 rounded border border-zinc-700 transition flex items-center justify-center gap-1.5 disabled:opacity-50"
      >
        <Play className="h-3 w-3" /> Run Playbook
      </button>
    </div>
  );
}

function ChaosCard({
  title,
  description,
  severity,
  onTrigger,
}: {
  title: string;
  description: string;
  severity: string;
  onTrigger: () => void;
}) {
  return (
    <div className="p-4 rounded-xl border border-zinc-800 bg-zinc-950/60 space-y-3">
      <div className="flex items-center justify-between">
        <SeverityBadge severity={severity.toLowerCase()} />
      </div>
      <h3 className="text-xs font-semibold text-white">{title}</h3>
      <p className="text-[11px] text-zinc-400">{description}</p>
      <button
        onClick={onTrigger}
        className="w-full py-2 text-xs bg-red-950 hover:bg-red-900 text-red-300 border border-red-800 font-semibold rounded transition flex items-center justify-center gap-1.5"
      >
        <Zap className="h-3.5 w-3.5" /> Inject Fault
      </button>
    </div>
  );
}
