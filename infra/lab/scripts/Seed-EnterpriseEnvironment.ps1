<#
.SYNOPSIS
    AtlasTech Enterprise Lab — Seed Directory & Corporate Resources.

.DESCRIPTION
    Creates the corporate Organizational Units (OUs), security groups, employee
    accounts, and department SMB file shares (\\AT-DC-01\Finance, HR, IT).
#>

Import-Module ActiveDirectory

$DomainDN = (Get-ADDomain).DistinguishedName
$DefaultPassword = ConvertTo-SecureString "AtlasEmployee2026!" -AsPlainText -Force

Write-Host "=== Seeding AtlasTech Corporate Directory ===" -ForegroundColor Cyan

# 1. Create Top-Level & Department OUs
$Departments = @("IT", "Finance", "HR", "Sales", "Management", "Workstations")
$BaseOU = "OU=AtlasTech,$DomainDN"

if (-not (Get-ADOrganizationalUnit -Filter "Name -eq 'AtlasTech'" -ErrorAction SilentlyContinue)) {
    New-ADOrganizationalUnit -Name "AtlasTech" -Path $DomainDN
}

foreach ($dept in $Departments) {
    if (-not (Get-ADOrganizationalUnit -Filter "Name -eq '$dept'" -SearchBase $BaseOU -ErrorAction SilentlyContinue)) {
        New-ADOrganizationalUnit -Name $dept -Path $BaseOU
        Write-Host "[OU] Created: $dept under AtlasTech" -ForegroundColor Green
    }
}

# 2. Seed Realistic Employees
$Employees = @(
    @{ Sam = "sarah.miller"; First = "Sarah"; Last = "Miller"; Dept = "Finance"; Title = "Senior Financial Analyst" },
    @{ Sam = "alex.chen"; First = "Alex"; Last = "Chen"; Dept = "IT"; Title = "L2 Systems Administrator" },
    @{ Sam = "elena.rostova"; First = "Elena"; Last = "Rostova"; Dept = "HR"; Title = "HR Business Partner" },
    @{ Sam = "marcus.vance"; First = "Marcus"; Last = "Vance"; Dept = "Sales"; Title = "Enterprise Account Executive" },
    @{ Sam = "david.sterling"; First = "David"; Last = "Sterling"; Dept = "Management"; Title = "Director of Operations" }
)

foreach ($emp in $Employees) {
    $userOU = "OU=$($emp.Dept),$BaseOU"
    if (-not (Get-ADUser -Filter "SamAccountName -eq '$($emp.Sam)'" -ErrorAction SilentlyContinue)) {
        New-ADUser -SamAccountName $emp.Sam `
                   -UserPrincipalName "$($emp.Sam)@atlastech.local" `
                   -Name "$($emp.First) $($emp.Last)" `
                   -GivenName $emp.First `
                   -Surname $emp.Last `
                   -Department $emp.Dept `
                   -Title $emp.Title `
                   -AccountPassword $DefaultPassword `
                   -Enabled $true `
                   -PasswordNeverExpires $true `
                   -Path $userOU
        Write-Host "[USER] Created user: $($emp.First) $($emp.Last) ($($emp.Sam))" -ForegroundColor Green
    }
}

# 3. Create Department SMB Shares
$ShareBasePath = "C:\Shares"
if (-not (Test-Path $ShareBasePath)) {
    New-Item -Path $ShareBasePath -ItemType Directory | Out-Null
}

foreach ($dept in @("Finance", "HR", "IT", "Public")) {
    $folder = "$ShareBasePath\$dept"
    if (-not (Test-Path $folder)) {
        New-Item -Path $folder -ItemType Directory | Out-Null
        New-SmbShare -Name $dept -Path $folder -FullAccess "Everyone" -ErrorAction SilentlyContinue
        Write-Host "[SHARE] Created SMB share \\AT-DC-01\$dept at $folder" -ForegroundColor Green
    }
}

Write-Host "=== AtlasTech Directory & Shares Successfully Seeded ===" -ForegroundColor Cyan
