#Requires -RunAsAdministrator

<#
.SYNOPSIS
    Installs the AtlasTech Telemetry Collector as a Windows Scheduled Task.
#>

param(
    [Parameter(Mandatory = $true)]
    [string]$ApiUrl,

    [int]$IntervalSeconds = 30
)

$ScriptPath = Join-Path $PSScriptRoot "collector.ps1"
$TaskName = "AtlasTech-TelemetryCollector"

$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$ScriptPath`" -ApiUrl `"$ApiUrl`" -IntervalSeconds $IntervalSeconds"
$trigger = New-ScheduledTaskTrigger -AtStartup
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Description "AtlasTech Telemetry Collector" -Force

Write-Host "Installed scheduled task: $TaskName"
Write-Host "Collector will start on next reboot or run: Start-ScheduledTask -TaskName '$TaskName'"
