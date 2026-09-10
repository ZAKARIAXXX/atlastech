<#
.SYNOPSIS
    AtlasTech Chaos Engineering — Scenario A: DNS Resolution Outage.

.DESCRIPTION
    Simulates internal DNS failure by modifying endpoint DNS server or sending
    fault-injected telemetry to test the automated AIOps incident triage engine.
#>

param(
    [Parameter(Mandatory = $false)]
    [string]$ApiUrl = "http://localhost:8000/api/v1/telemetry",

    [Parameter(Mandatory = $false)]
    [switch]$DirectAdapterModification
)

$hostname = $env:COMPUTERNAME
Write-Host "=== AtlasTech Chaos: Injecting DNS Resolution Fault ===" -ForegroundColor Yellow
Write-Host "Target Host: $hostname"

if ($DirectAdapterModification) {
    Write-Host "[ACTION] Modifying network adapter DNS server to 127.0.0.99 (Invalid)..."
    $adapter = Get-NetAdapter | Where-Object { $_.Status -eq "Up" } | Select-Object -First 1
    if ($adapter) {
        Set-DnsClientServerAddress -InterfaceIndex $adapter.ifIndex -ServerAddresses ("127.0.0.99")
        Clear-DnsClientCache
        Write-Host "[SUCCESS] Adapter DNS set to invalid address. Local resolution broken." -ForegroundColor Red
    }
} else {
    Write-Host "[ACTION] Sending fault-injected telemetry packet directly to platform..."
    $faultPayload = @{
        hostname         = $hostname
        ip_address       = "192.168.30.24"
        mac_address      = "00:50:56:C0:00:08"
        os_version       = "Windows 11 Enterprise"
        department       = "Finance"
        cpu_percent      = 21.4
        ram_percent      = 54.0
        disk_percent     = 48.2
        gateway_reachable = $true
        dns_resolution_ok = $false  # FAULT INJECTION
        critical_services = @(
            @{ name = "dnscache"; display_name = "DNS Client"; status = "running" }
        )
        logged_in_user   = "ATLASTECH\sarah.miller"
    } | ConvertTo-Json -Depth 5

    try {
        $res = Invoke-RestMethod -Uri $ApiUrl -Method Post -Body $faultPayload -ContentType "application/json"
        Write-Host "[SUCCESS] Fault telemetry accepted! Incidents Generated: $($res.incidents_generated)" -ForegroundColor Green
    } catch {
        Write-Warning "[ERROR] Failed to contact API: $_"
    }
}
