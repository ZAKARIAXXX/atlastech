<#
.SYNOPSIS
    AtlasTech Enterprise Lab — Automated Client Domain Join.

.DESCRIPTION
    Configures client network DNS to point to the Domain Controller (192.168.10.10)
    and joins the machine to the 'atlastech.local' domain.
#>

param(
    [string]$DomainName = "atlastech.local",
    [string]$DomainControllerIP = "192.168.10.10",
    [string]$AdminUser = "Administrator",
    [securestring]$AdminPassword = (ConvertTo-SecureString "AtlasTech2026!P@ss" -AsPlainText -Force)
)

Write-Host "=== AtlasTech Client Domain Join ===" -ForegroundColor Cyan

# 1. Set Primary DNS to DC IP
Write-Host "[1/3] Pointing DNS to Domain Controller ($DomainControllerIP)..." -ForegroundColor Yellow
$adapter = Get-NetAdapter | Where-Object { $_.Status -eq "Up" } | Select-Object -First 1
if ($adapter) {
    Set-DnsClientServerAddress -InterfaceIndex $adapter.ifIndex -ServerAddresses ($DomainControllerIP)
    Clear-DnsClientCache
    Write-Host "[SUCCESS] DNS configured to $DomainControllerIP." -ForegroundColor Green
}

# 2. Join Domain
Write-Host "[2/3] Joining domain '$DomainName'..." -ForegroundColor Yellow
$cred = New-Object System.Management.Automation.PSCredential ("$DomainName\$AdminUser", $AdminPassword)
Add-Computer -DomainName $DomainName -Credential $cred -Restart -Force

Write-Host "[SUCCESS] Machine joined to $DomainName. Restarting now..." -ForegroundColor Green
