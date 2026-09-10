<#
.SYNOPSIS
    AtlasTech Chaos Engineering — Reset Environment & Cleanup.

.DESCRIPTION
    Restores normal network configuration, deletes temporary disk allocation files,
    restarts core Windows services, and sends healthy telemetry.
#>

param(
    [Parameter(Mandatory = $false)]
    [string]$ApiUrl = "http://localhost:8000/api/v1/telemetry"
)

Write-Host "=== AtlasTech Chaos: Resetting Lab State ===" -ForegroundColor Cyan

# 1. Clean temp disk files
$tempFile = "$env:TEMP\AtlasTech_Chaos_DiskPressure.dat"
if (Test-Path $tempFile) {
    Remove-Item $tempFile -Force
    Write-Host "[CLEANUP] Deleted dummy storage pressure file." -ForegroundColor Green
}

# 2. Reset network adapter DNS
$adapter = Get-NetAdapter | Where-Object { $_.Status -eq "Up" } | Select-Object -First 1
if ($adapter) {
    Set-DnsClientServerAddress -InterfaceIndex $adapter.ifIndex -ResetServerAddresses -ErrorAction SilentlyContinue
    Clear-DnsClientCache -ErrorAction SilentlyContinue
    Write-Host "[CLEANUP] Reset DNS server addresses to DHCP automatic." -ForegroundColor Green
}

# 3. Restart stopped services
@("spooler", "dnscache", "lanmanworkstation") | ForEach-Object {
    $svc = Get-Service -Name $_ -ErrorAction SilentlyContinue
    if ($svc -and $svc.Status -ne "Running") {
        Start-Service -Name $_ -ErrorAction SilentlyContinue
        Write-Host "[RECOVERY] Restarted service: $_" -ForegroundColor Green
    }
}

# 4. Transmit healthy heartbeat
$hostname = $env:COMPUTERNAME
$healthyPayload = @{
    hostname         = $hostname
    ip_address       = "192.168.30.24"
    os_version       = "Windows 11 Enterprise"
    department       = "Finance"
    cpu_percent      = 12.0
    ram_percent      = 42.0
    disk_percent     = 52.0
    gateway_reachable = $true
    dns_resolution_ok = $true
    critical_services = @(
        @{ name = "dnscache"; display_name = "DNS Client"; status = "running" },
        @{ name = "spooler"; display_name = "Print Spooler"; status = "running" }
    )
    logged_in_user   = "ATLASTECH\sarah.miller"
} | ConvertTo-Json -Depth 5

try {
    $res = Invoke-RestMethod -Uri $ApiUrl -Method Post -Body $healthyPayload -ContentType "application/json"
    Write-Host "[SUCCESS] Transmitted healthy baseline telemetry to AtlasTech operations center." -ForegroundColor Green
} catch {
    Write-Host "[NOTE] Platform API offline; baseline payload prepared." -ForegroundColor DarkGray
}
