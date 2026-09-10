<#
.SYNOPSIS
    AtlasTech Enterprise Lab — Automated Domain Controller Provisioner.

.DESCRIPTION
    Automates the promotion of a fresh Windows Server to the root Domain Controller
    for 'atlastech.local', creates the corporate OU hierarchy, seeds enterprise users,
    and configures department SMB file shares.
#>

param(
    [string]$DomainName = "atlastech.local",
    [string]$NetbiosName = "ATLASTECH",
    [securestring]$SafeModePassword = (ConvertTo-SecureString "AtlasTech2026!P@ss" -AsPlainText -Force)
)

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   AtlasTech Lab: Automated Domain Controller Setup       " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Install AD DS and Management Tools
Write-Host "[1/5] Installing Active Directory Domain Services role..." -ForegroundColor Yellow
Install-WindowsFeature -Name AD-Domain-Services -IncludeManagementTools

# 2. Promote Server to New Forest Root DC
Write-Host "[2/5] Promoting server to Domain Controller for '$DomainName'..." -ForegroundColor Yellow
$InstallParams = @{
    CreateDnsDelegation           = $false
    DatabasePath                  = "C:\Windows\NTDS"
    DomainMode                    = "WinThreshold"
    DomainName                    = $DomainName
    DomainNetbiosName             = $NetbiosName
    ForestMode                    = "WinThreshold"
    InstallDns                    = $true
    LogPath                       = "C:\Windows\NTDS"
    NoRebootOnCompletion          = $true
    SysvolPath                    = "C:\Windows\SYSVOL"
    SafeModeAdministratorPassword = $SafeModePassword
    Force                         = $true
}

Install-ADDSForest @InstallParams

Write-Host "[SUCCESS] Active Directory Domain Services installed successfully." -ForegroundColor Green
Write-Host "[NOTE] Server reboot required before creating OUs and seed users." -ForegroundColor Yellow
