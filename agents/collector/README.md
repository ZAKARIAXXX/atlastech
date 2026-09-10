# AtlasTech Telemetry Collector

Lightweight PowerShell agent that collects system telemetry from Windows endpoints and sends it to the AtlasTech API.

## Capabilities

- CPU, RAM, Disk usage
- Network connectivity (gateway, DNS)
- Critical Windows service status
- Hostname, IP, OS info
- Heartbeat every 30 seconds

## Usage

```powershell
# Run directly
.\collector.ps1 -ApiUrl "http://localhost:8000/api/v1/telemetry"

# Install as scheduled task
.\install.ps1 -ApiUrl "http://localhost:8000/api/v1/telemetry"
```
