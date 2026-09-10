<#
.SYNOPSIS
    AtlasTech Chaos Engineering — Scenario B: Disk Space Exhaustion.

.DESCRIPTION
    Simulates high disk pressure (>95% capacity) to trigger automated high/critical storage incidents.
#>

param(
    [Parameter(Mandatory = $false)]
    [string]$ApiUrl = "http://localhost:8000/api/v1/telemetry",

    [Parameter(Mandatory = $false)]
    [switch]$CreateRealFile
)

$hostname = $env:COMPUTERNAME
Write-Host "=== AtlasTech Chaos: Injecting Storage Volume Fault ===" -ForegroundColor Yellow

if ($CreateRealFile) {
    $tempFile = "$env:TEMP\AtlasTech_Chaos_DiskPressure.dat"
    Write-Host "[ACTION] Creating 500MB dummy allocation at $tempFile..."
    $fs = [System.IO.File]::Create($tempFile)
    $fs.SetLength(524288000)
    $fs.Close()
    Write-Host "[SUCCESS] Temporary file created. System drive free space decreased." -ForegroundColor Green
} else {
    Write-Host "[ACTION] Sending 96.8% Disk Utilization Telemetry..."
    $faultPayload = @{
        hostname         = $hostname
        ip_address       = "192.168.30.24"
        os_version       = "Windows 11 Enterprise"
        department       = "Finance"
        cpu_percent      = 35.0
        ram_percent      = 62.0
        disk_percent     = 96.8  # FAULT INJECTION (> 95% triggers CRITICAL)
        gateway_reachable = $true
        dns_resolution_ok = $true
        logged_in_user   = "ATLASTECH\sarah.miller"
    } | ConvertTo-Json -Depth 5

    try {
        $res = Invoke-RestMethod -Uri $ApiUrl -Method Post -Body $faultPayload -ContentType "application/json"
        Write-Host "[SUCCESS] Storage fault transmitted! Incidents Generated: $($res.incidents_generated)" -ForegroundColor Green
    } catch {
        Write-Warning "[ERROR] Failed to contact API: $_"
    }
}
