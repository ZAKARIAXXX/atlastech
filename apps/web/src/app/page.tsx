import {
  Activity,
  AlertTriangle,
  CheckCircle,
  Monitor,
  Server,
} from "lucide-react";

export default function Dashboard() {
  return (
    <main className="min-h-screen p-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">
          AtlasTech <span className="text-cyan-400">IT Operations</span>
        </h1>
        <p className="mt-1 text-zinc-400">
          Enterprise Operations Console — v0.1.0
        </p>
      </header>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
        <StatCard
          icon={<AlertTriangle className="h-5 w-5 text-orange-400" />}
          label="Open Incidents"
          value="—"
        />
        <StatCard
          icon={<Activity className="h-5 w-5 text-red-400" />}
          label="Critical"
          value="—"
        />
        <StatCard
          icon={<CheckCircle className="h-5 w-5 text-green-400" />}
          label="Resolved Today"
          value="—"
        />
        <StatCard
          icon={<Monitor className="h-5 w-5 text-cyan-400" />}
          label="Devices Online"
          value="—"
        />
      </div>

      <section className="mt-10">
        <h2 className="mb-4 text-xl font-semibold">System Health</h2>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
          <ServiceCard name="Domain Controller" status="unknown" />
          <ServiceCard name="DNS" status="unknown" />
          <ServiceCard name="DHCP" status="unknown" />
          <ServiceCard name="File Server" status="unknown" />
        </div>
      </section>

      <section className="mt-10">
        <h2 className="mb-4 text-xl font-semibold">Recent Alerts</h2>
        <div className="rounded-lg border border-zinc-800 bg-zinc-900 p-6 text-zinc-500">
          No alerts — connect telemetry agent to begin.
        </div>
      </section>
    </main>
  );
}

function StatCard({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
}) {
  return (
    <div className="rounded-lg border border-zinc-800 bg-zinc-900 p-5">
      <div className="flex items-center gap-2 text-zinc-400 text-sm">
        {icon}
        {label}
      </div>
      <div className="mt-2 text-3xl font-bold">{value}</div>
    </div>
  );
}

function ServiceCard({ name, status }: { name: string; status: string }) {
  const color =
    status === "online"
      ? "bg-green-500"
      : status === "offline"
        ? "bg-red-500"
        : "bg-zinc-600";

  return (
    <div className="flex items-center gap-3 rounded-lg border border-zinc-800 bg-zinc-900 p-4">
      <Server className="h-5 w-5 text-zinc-400" />
      <span className="flex-1 text-sm font-medium">{name}</span>
      <span className={`h-2 w-2 rounded-full ${color}`} />
      <span className="text-xs text-zinc-500 capitalize">{status}</span>
    </div>
  );
}
