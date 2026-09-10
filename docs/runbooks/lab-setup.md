# AtlasTech Enterprise Lab Setup Guide

This runbook guides you through provisioning the **`atlastech.local`** corporate Active Directory infrastructure and client fleet.

---

## 1. Architecture & Network Topology

```text
Host PC (192.168.10.1) ──── VirtualBox Internal Network (AtlasTechNet: 192.168.10.0/24)
                                  │
                 ┌────────────────┴────────────────┐
                 │                                 │
           AT-DC-01 (192.168.10.10)         AT-PC-024 (192.168.10.101)
           • Windows Server 2022/2025        • Windows 11 Enterprise
           • AD DS (atlastech.local)         • Joined to atlastech.local
           • DNS & DHCP                      • Runs AtlasTech Collector
           • SMB Shares: \\AT-DC-01\Finance
```

---

## 2. VirtualBox Network Configuration

1. In VirtualBox, go to **Tools** > **Network Manager** (or VM Settings).
2. Create a **Host-Only Adapter** or use an **Internal Network** named `AtlasTechNet`.
3. Set Host Adapter IP: `192.168.10.1`, Subnet Mask: `255.255.255.0`.

---

## 3. Provisioning VM 1: Domain Controller (`AT-DC-01`)

### Step 1: VM Creation
- **OS**: Windows Server 2022 or 2025 Evaluation
- **RAM**: 4096 MB (4 GB)
- **vCPUs**: 2
- **Disk**: 40 GB (Dynamically Allocated)
- **Network**: Attached to `AtlasTechNet` (Internal / Host-Only)

### Step 2: Configure Static IP
Open PowerShell as Administrator on the Server VM:
```powershell
$adapter = Get-NetAdapter | Where-Object { $_.Status -eq "Up" } | Select-Object -First 1
New-NetIPAddress -InterfaceIndex $adapter.ifIndex -IPAddress 192.168.10.10 -PrefixLength 24 -DefaultGateway 192.168.10.1
Set-DnsClientServerAddress -InterfaceIndex $adapter.ifIndex -ServerAddresses ("127.0.0.1")
```

### Step 3: Install Active Directory
Run the automated installation script:
```powershell
.\infra\lab\scripts\Install-DomainController.ps1
```
*The server will reboot automatically upon completion.*

### Step 4: Seed Corporate OUs, Users & SMB Shares
After reboot, log in as `ATLASTECH\Administrator` and run:
```powershell
.\infra\lab\scripts\Seed-EnterpriseEnvironment.ps1
```
This automatically creates:
- **OUs**: `IT`, `Finance`, `HR`, `Sales`, `Management`.
- **Users**: `sarah.miller` (Finance), `alex.chen` (IT), `elena.rostova` (HR), `marcus.vance` (Sales).
- **SMB Shares**: `\\AT-DC-01\Finance`, `\\AT-DC-01\HR`, `\\AT-DC-01\IT`.

---

## 4. Provisioning VM 2: Client Workstation (`AT-PC-024`)

### Step 1: VM Creation
- **OS**: Windows 11 Enterprise Evaluation
- **RAM**: 4096 MB (4 GB)
- **vCPUs**: 2
- **Network**: Attached to `AtlasTechNet`

### Step 2: Join Domain
Open PowerShell as Administrator on the Client VM and run:
```powershell
.\infra\lab\scripts\Join-Domain.ps1 -DomainControllerIP "192.168.10.10"
```
*The workstation will configure its DNS, join `atlastech.local`, and reboot.*

### Step 3: Log In as Corporate User
Log in as:
- **Username**: `ATLASTECH\sarah.miller`
- **Password**: `AtlasEmployee2026!`

---

## 5. Connecting the Telemetry Agent

On the client machine (`AT-PC-024`):
```powershell
.\agents\collector\collector.ps1 -ApiUrl "http://192.168.10.1:8000/api/v1/telemetry"
```

1. The device will immediately register in the database.
2. Open the **Operations Console** at `http://localhost:3000` to watch live CPU%, RAM%, Disk%, Gateway ping, and DNS status appear on the **Fleet Asset Grid**!

---

## 6. Testing Chaos Scenarios

From your client machine or host, test the AIOps alert pipeline:

```powershell
# Scenario A: Break DNS resolution
.\infra\chaos\inject-dns-fault.ps1

# Scenario B: Trigger critical disk volume exhaustion (>95%)
.\infra\chaos\fill-disk.ps1

# Recovery: Reset back to healthy baseline
.\infra\chaos\reset-chaos.ps1
```
