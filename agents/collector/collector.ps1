#Requires -Version 5.1

<#
.SYNOPSIS
    AtlasTech Telemetry Collector — collects system vitals and sends to the platform API.

.DESCRIPTION
    Lightweight agent that runs on Windows endpoints, gathering CPU, RAM, disk,
    network, and service health data, then POSTs it to the AtlasTech ingestion API.

.PARAMETER ApiUrl
    The telemetry ingestion endpoint URL.

.PARAMETER IntervalSeconds
    Heartbeat interval in seconds. Default: 30.

.EXAMPLE
    .\collector.ps1 -ApiUrl "http://localhost:8000/api/v1/telemetry"
#>

param(
    [Parameter(Mandatory = $true)]
    [string]$ApiUrl,

    [Parameter(Mandatory = $false)]
    [int]$IntervalSeconds = 30
)

$CriticalServices = @(
    "wuauserv",
    "dnscache",
    "lanmanworkstation",
    "spooler",
    "dhcp",
    "dns"
)

function Get-SystemTelemetry {
    $hostname = $env:COMPUTERNAME
    $os = Get-CimInstance Win32_OperatingSystem
    $cpu = (Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average
    $ramTotal = $os.TotalVisibleMemorySize
    $ramFree = $os.FreePhysicalMemory
    $ramPercent = [math]::Round((($ramTotal - $ramFree) / $ramTotal) * 100, 1)

    $disk = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='C:'"
    $diskPercent = if ($disk.Size -gt 0) {
        [math]::Round((($disk.Size - $disk.FreeSpace) / $disk.Size) * 100, 1)
    } else { 0 }

    $gateway = Get-NetRoute -DestinationPrefix "0.0.0.0/0" -ErrorAction SilentlyContinue | Select-Object -First 1
    $gatewayReachable = if ($gateway) {
        Test-Connection -ComputerName $gateway.NextHop -Count 1 -Quiet -ErrorAction SilentlyContinue
    } else { $false }

    $dnsOk = try {
        $null = Resolve-DnsName "dc01.atlastech.local" -ErrorAction Stop
        $true
    } catch { $false }

    $ipConfig = Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue | Where-Object { $_.InterfaceAlias -notlike "Loopback*" } | Select-Object -First 1

    $macAddress = $null
    if ($ipConfig) {
        $adapter = Get-NetAdapter -InterfaceIndex $ipConfig.InterfaceIndex -ErrorAction SilentlyContinue
        if ($adapter) { $macAddress = $adapter.MacAddress }
    }

    $services = $CriticalServices | ForEach-Object {
        $svc = Get-Service -Name $_ -ErrorAction SilentlyContinue
        if ($svc) {
            [PSCustomObject]@{
                Name         = $svc.Name
                DisplayName  = $svc.DisplayName
                Status       = $svc.Status.ToString().ToLower()
                ProcessId    = $null
            }
        }
    }

    $currentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name

    return @{
        hostname         = $hostname
        ip_address       = if ($ipConfig) { $ipConfig.IPAddress } else { "0.0.0.0" }
        mac_address      = $macAddress
        os_version       = $os.Caption
        cpu_percent      = [math]::Round($cpu, 1)
        ram_percent      = $ramPercent
        disk_percent     = $diskPercent
        gateway_reachable = $gatewayReachable
        dns_resolution_ok = $dnsOk
        critical_services = $services | ForEach-Object {
            @{
                name         = $_.Name
                display_name = $_.DisplayName
                status       = $_.Status
                pid          = $_.ProcessId
            }
        }
        logged_in_user   = $currentUser
    }
}

function Send-Telemetry {
    param([hashtable]$Data)

    $json = $Data | ConvertTo-Json -Depth 10 -Compress

    try {
        $response = Invoke-RestMethod -Uri $ApiUrl -Method Post -Body $json -ContentType "application/json" -TimeoutSec 10
        Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Telemetry sent — status: $($response.status)"
    } catch {
        Write-Warning "[$(Get-Date -Format 'HH:mm:ss')] Failed to send telemetry: $_"
    }
}

Write-Host "=== AtlasTech Telemetry Collector ==="
Write-Host "API Endpoint: $ApiUrl"
Write-Host "Interval: ${IntervalSeconds}s"
Write-Host ""

while ($true) {
    $telemetry = Get-SystemTelemetry
    Send-Telemetry -Data $telemetry
    Start-Sleep -Seconds $IntervalSeconds
}
