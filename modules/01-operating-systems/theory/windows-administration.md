# Windows Server Administration - Quản trị Windows Server

## 🎯 Mục tiêu Học tập
Nắm vững các kỹ năng quản trị Windows Server cần thiết cho môi trường enterprise tại Viettel IDC, bao gồm services, registry, networking và PowerShell automation.

## 📚 1. Windows Server Architecture

### Windows Server Editions
```
Windows Server 2019/2022 Editions:
├── Standard Edition
│   ├── Full GUI installation
│   ├── Server Core installation
│   └── Nano Server (container optimized)
├── Datacenter Edition
│   ├── Unlimited virtualization rights
│   ├── Software-Defined Datacenter features
│   └── Storage Spaces Direct
└── Essentials Edition
    ├── Small business focused
    ├── Up to 25 users
    └── Built-in cloud integration
```

### Windows Server Core vs Full Installation
```powershell
# Check installation type
Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion" | Select-Object InstallationType

# Convert Full to Core (Server 2019+)
Uninstall-WindowsFeature Server-Gui-Mgmt-Infra -Restart

# Convert Core to Full
Install-WindowsFeature Server-Gui-Mgmt-Infra, Server-Gui-Shell -Restart
```

### Windows Boot Process
```
1. UEFI/BIOS → 2. Windows Boot Manager → 3. Windows Boot Loader → 4. NT Kernel → 5. Session Manager → 6. Services
```

**Chi tiết từng bước:**

#### 1. Boot Configuration Data (BCD)
```cmd
# View boot configuration
bcdedit /enum

# Create backup
bcdedit /export C:\BCDBackup

# Modify boot options
bcdedit /set {current} description "Windows Server 2019"
bcdedit /timeout 10
```

#### 2. Boot Logging
```cmd
# Enable boot logging
bcdedit /set {current} bootlog yes

# View boot log
type %SystemRoot%\ntbtlog.txt
```

## 🔧 2. Services Management

### Service Control Methods

#### Services Console (services.msc)
- GUI-based service management
- Start, stop, pause, resume services
- Configure startup type và recovery options
- View service dependencies

#### Command Line (sc.exe)
```cmd
# Service information
sc query                          # List all services
sc query ServiceName              # Specific service info
sc qc ServiceName                 # Service configuration

# Service control
sc start ServiceName              # Start service
sc stop ServiceName               # Stop service
sc pause ServiceName              # Pause service
sc continue ServiceName           # Resume service

# Service configuration
sc config ServiceName start= auto # Set startup type
sc config ServiceName obj= "domain\user" password= "password"
sc failure ServiceName reset= 86400 actions= restart/60000
```

#### PowerShell Service Management
```powershell
# Get services
Get-Service                       # All services
Get-Service -Name "Spooler"       # Specific service
Get-Service | Where-Object {$_.Status -eq "Running"}

# Service control
Start-Service -Name "Spooler"
Stop-Service -Name "Spooler" -Force
Restart-Service -Name "Spooler"
Suspend-Service -Name "Spooler"
Resume-Service -Name "Spooler"

# Service configuration
Set-Service -Name "Spooler" -StartupType Automatic
Set-Service -Name "Spooler" -Status Running

# Service dependencies
Get-Service -Name "Spooler" -DependentServices
Get-Service -Name "Spooler" -RequiredServices
```

### Creating Custom Services
```powershell
# Create service with PowerShell
New-Service -Name "MyCustomService" `
    -BinaryPathName "C:\MyApp\service.exe" `
    -DisplayName "My Custom Service" `
    -Description "Custom service for monitoring" `
    -StartupType Automatic

# Using sc command
sc create MyService binPath= "C:\MyApp\service.exe" start= auto
```

### Service Recovery Configuration
```cmd
# Configure service recovery
sc failure ServiceName reset= 86400 actions= restart/60000/restart/60000/run/1000

# Recovery actions explained:
# restart/60000 = restart after 60 seconds
# run/1000 = run recovery program after 1 second
# reset= 86400 = reset failure count after 24 hours
```

## 📝 3. Registry Management

### Registry Structure
```
Registry Hives:
├── HKEY_LOCAL_MACHINE (HKLM)
│   ├── HARDWARE          # Hardware information
│   ├── SAM              # Security Account Manager
│   ├── SECURITY         # Security policies
│   ├── SOFTWARE         # Installed software
│   └── SYSTEM           # System configuration
├── HKEY_CURRENT_USER (HKCU)
│   ├── Software         # User-specific software settings
│   ├── Environment      # User environment variables
│   └── Network          # Network connections
├── HKEY_USERS (HKU)
│   └── [SID]            # User profiles by SID
├── HKEY_CURRENT_CONFIG (HKCC)
│   └── System           # Current hardware profile
└── HKEY_CLASSES_ROOT (HKCR)
    └── File associations and COM objects
```

### Registry Operations with PowerShell
```powershell
# Registry navigation
Set-Location HKLM:\
Get-ChildItem                     # List subkeys
Get-ChildItem -Recurse            # Recursive listing

# Read registry values
Get-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion" -Name "ProductName"
Get-ItemPropertyValue -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion" -Name "ProductName"

# Create registry keys
New-Item -Path "HKLM:\SOFTWARE\MyCompany" -Force
New-Item -Path "HKLM:\SOFTWARE\MyCompany\MyApp" -Force

# Set registry values
Set-ItemProperty -Path "HKLM:\SOFTWARE\MyCompany\MyApp" -Name "Version" -Value "1.0"
New-ItemProperty -Path "HKLM:\SOFTWARE\MyCompany\MyApp" -Name "InstallDate" -Value (Get-Date) -PropertyType String

# Remove registry items
Remove-ItemProperty -Path "HKLM:\SOFTWARE\MyCompany\MyApp" -Name "TempSetting"
Remove-Item -Path "HKLM:\SOFTWARE\MyCompany\MyApp" -Recurse
```

### Registry Command Line Tools
```cmd
# REG command
reg query HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion /v ProductName
reg add HKLM\SOFTWARE\MyApp /v Version /t REG_SZ /d "1.0"
reg delete HKLM\SOFTWARE\MyApp /v OldSetting /f

# Export/Import registry
reg export HKLM\SOFTWARE\MyApp C:\backup\myapp.reg
reg import C:\backup\myapp.reg
```

### Important Registry Locations
```powershell
# System information
HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion

# Installed programs
HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall
HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall

# Services
HKLM:\SYSTEM\CurrentControlSet\Services

# Environment variables
HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Environment

# Network settings
HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters

# Startup programs
HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run
HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run
```

## 🌐 4. Network Configuration

### Network Interface Configuration
```powershell
# View network adapters
Get-NetAdapter
Get-NetAdapter | Where-Object {$_.Status -eq "Up"}

# IP configuration
Get-NetIPConfiguration
Get-NetIPAddress
Get-NetRoute

# Configure static IP
New-NetIPAddress -InterfaceIndex 12 -IPAddress 192.168.1.100 -PrefixLength 24 -DefaultGateway 192.168.1.1
Set-DnsClientServerAddress -InterfaceIndex 12 -ServerAddresses 8.8.8.8,8.8.4.4

# Remove IP configuration
Remove-NetIPAddress -InterfaceIndex 12 -IPAddress 192.168.1.100
```

### NetSH Commands (Legacy but still useful)
```cmd
# Interface configuration
netsh interface ip show config
netsh interface ip set address "Local Area Connection" static 192.168.1.100 255.255.255.0 192.168.1.1

# DNS configuration
netsh interface ip set dns "Local Area Connection" static 8.8.8.8
netsh interface ip add dns "Local Area Connection" 8.8.4.4 index=2

# DHCP configuration
netsh interface ip set address "Local Area Connection" dhcp
netsh interface ip set dns "Local Area Connection" dhcp

# Firewall (deprecated, use Windows Firewall with PowerShell)
netsh advfirewall firewall show rule name=all
netsh advfirewall firewall add rule name="Allow Port 80" dir=in action=allow protocol=TCP localport=80
```

### Windows Firewall Configuration
```powershell
# Firewall profiles
Get-NetFirewallProfile
Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled True

# Firewall rules
Get-NetFirewallRule | Where-Object {$_.Enabled -eq "True"}
Get-NetFirewallRule -DisplayName "*Remote Desktop*"

# Create firewall rules
New-NetFirewallRule -DisplayName "Allow HTTP" -Direction Inbound -Protocol TCP -LocalPort 80 -Action Allow
New-NetFirewallRule -DisplayName "Allow HTTPS" -Direction Inbound -Protocol TCP -LocalPort 443 -Action Allow
New-NetFirewallRule -DisplayName "Block Telnet" -Direction Inbound -Protocol TCP -LocalPort 23 -Action Block

# Modify firewall rules
Set-NetFirewallRule -DisplayName "Allow HTTP" -Enabled False
Remove-NetFirewallRule -DisplayName "Old Rule"

# Port and application rules
New-NetFirewallRule -DisplayName "Allow App" -Direction Inbound -Program "C:\MyApp\app.exe" -Action Allow
New-NetFirewallRule -DisplayName "Allow Subnet" -Direction Inbound -RemoteAddress 192.168.1.0/24 -Action Allow
```

### Network Troubleshooting
```powershell
# Connectivity testing
Test-NetConnection google.com -Port 80
Test-NetConnection 192.168.1.1 -TraceRoute

# Network statistics
Get-NetTCPConnection | Where-Object {$_.State -eq "Established"}
Get-NetUDPEndpoint
Get-NetTCPConnection -LocalPort 80

# DNS testing
Resolve-DnsName google.com
Test-DnsServer -IPAddress 8.8.8.8 -Name google.com

# Route management
Get-NetRoute
New-NetRoute -DestinationPrefix 10.0.0.0/8 -NextHop 192.168.1.1 -InterfaceIndex 12
Remove-NetRoute -DestinationPrefix 10.0.0.0/8
```

## 📊 5. Event Viewer và Logging

### Event Log Structure
```
Windows Event Logs:
├── Windows Logs
│   ├── Application      # Application events
│   ├── Security        # Security/audit events
│   ├── Setup           # Setup and deployment events
│   ├── System          # System component events
│   └── Forwarded Events # Forwarded from other computers
├── Applications and Services Logs
│   ├── Microsoft       # Microsoft application logs
│   ├── Internet Explorer # Browser logs
│   └── [Custom Apps]   # Third-party application logs
└── Custom Views
    └── Administrative Events # Critical, Error, Warning events
```

### PowerShell Event Log Management
```powershell
# Get event logs
Get-EventLog -List
Get-WinEvent -ListLog *

# Read event logs
Get-EventLog -LogName System -Newest 100
Get-EventLog -LogName Application -EntryType Error -Newest 50

# Filter events
Get-WinEvent -FilterHashtable @{LogName='System'; Level=2; StartTime=(Get-Date).AddDays(-1)}
Get-WinEvent -FilterHashtable @{LogName='Security'; ID=4624,4625}

# Search events
Get-WinEvent -FilterHashtable @{LogName='Application'; StartTime=(Get-Date).AddHours(-4)} | 
    Where-Object {$_.Message -like "*error*"}

# Export events
Get-EventLog -LogName System | Export-Csv C:\logs\system_events.csv
Get-WinEvent -LogName Application | Export-Clixml C:\logs\app_events.xml
```

### Event Log Configuration
```powershell
# Event log properties
Get-WinEvent -ListLog Application | Select-Object LogName, LogType, MaximumSizeInBytes, RecordCount

# Configure log size and retention
wevtutil sl Application /ms:104857600    # Set max size to 100MB
wevtutil sl Application /rt:false        # Disable log rotation

# Clear event logs
Clear-EventLog -LogName Application
wevtutil cl System
```

### Custom Event Logging
```powershell
# Create custom event source
New-EventLog -LogName Application -Source "MyApplication"

# Write events
Write-EventLog -LogName Application -Source "MyApplication" -EventId 1001 -EntryType Information -Message "Application started successfully"
Write-EventLog -LogName Application -Source "MyApplication" -EventId 1002 -EntryType Warning -Message "Configuration file not found, using defaults"
Write-EventLog -LogName Application -Source "MyApplication" -EventId 1003 -EntryType Error -Message "Database connection failed"
```

## 💻 6. PowerShell Administration

### PowerShell Execution Policy
```powershell
# Check current execution policy
Get-ExecutionPolicy
Get-ExecutionPolicy -List

# Set execution policy
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
Set-ExecutionPolicy Unrestricted -Scope LocalMachine

# Bypass execution policy for single script
powershell.exe -ExecutionPolicy Bypass -File script.ps1
```

### PowerShell Profiles
```powershell
# Profile locations
$PROFILE                          # Current user, current host
$PROFILE.AllUsersAllHosts        # All users, all hosts
$PROFILE.AllUsersCurrentHost     # All users, current host
$PROFILE.CurrentUserAllHosts     # Current user, all hosts

# Create profile
New-Item -ItemType File -Path $PROFILE -Force
notepad $PROFILE

# Sample profile content
# Set location
Set-Location C:\Scripts

# Custom functions
function Get-SystemInfo {
    Get-ComputerInfo | Select-Object WindowsProductName, TotalPhysicalMemory, CsProcessors
}

# Aliases
Set-Alias ll Get-ChildItem
Set-Alias grep Select-String

# Modules
Import-Module ActiveDirectory
```

### PowerShell Remoting
```powershell
# Enable PS Remoting
Enable-PSRemoting -Force

# Remote session
$session = New-PSSession -ComputerName Server01
Enter-PSSession -Session $session
Exit-PSSession

# Run commands remotely
Invoke-Command -ComputerName Server01 -ScriptBlock {Get-Service}
Invoke-Command -ComputerName Server01,Server02 -FilePath C:\Scripts\script.ps1

# Copy files
Copy-Item C:\local\file.txt -Destination C:\remote\ -ToSession $session
```

### PowerShell Scripting Best Practices
```powershell
# Script template
[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [string]$ComputerName,
    
    [Parameter(Mandatory=$false)]
    [int]$Port = 80
)

# Error handling
try {
    $result = Test-NetConnection -ComputerName $ComputerName -Port $Port
    if ($result.TcpTestSucceeded) {
        Write-Output "Connection successful"
    } else {
        Write-Warning "Connection failed"
    }
}
catch {
    Write-Error "Error: $($_.Exception.Message)"
}
finally {
    Write-Output "Script completed"
}

# Logging
$logPath = "C:\Logs\script.log"
"$(Get-Date): Script started" | Add-Content $logPath
```

## 🔒 7. Security Features

### User Account Control (UAC)
```powershell
# Check UAC status
Get-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" -Name "EnableLUA"

# UAC levels (via registry)
# 0 = Never notify
# 1 = Notify me only when apps try to make changes (no dimming)
# 2 = Notify me only when apps try to make changes (default)
# 3 = Always notify
Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" -Name "ConsentPromptBehaviorAdmin" -Value 2
```

### Windows Defender Configuration
```powershell
# Windows Defender status
Get-MpComputerStatus

# Scan operations
Start-MpScan -ScanType QuickScan
Start-MpScan -ScanType FullScan
Start-MpScan -ScanType CustomScan -ScanPath "C:\Temp"

# Update definitions
Update-MpSignature

# Exclusions
Add-MpPreference -ExclusionPath "C:\MyApp"
Add-MpPreference -ExclusionExtension ".log"
Add-MpPreference -ExclusionProcess "myapp.exe"

# Real-time protection
Set-MpPreference -DisableRealtimeMonitoring $false
```

### Local Security Policy
```powershell
# Password policy
net accounts /maxpwage:90 /minpwage:1 /minpwlen:8 /uniquepw:5

# Account lockout policy
net accounts /lockoutthreshold:5 /lockoutduration:30 /lockoutwindow:30

# User rights (use secedit for complex policies)
secedit /export /cfg C:\temp\current_policy.inf
# Edit the .inf file
secedit /configure /db C:\temp\policy.sdb /cfg C:\temp\modified_policy.inf
```

## 📈 8. Performance Monitoring

### Performance Monitor (PerfMon)
```powershell
# Performance counters
Get-Counter "\Processor(_Total)\% Processor Time"
Get-Counter "\Memory\Available MBytes"
Get-Counter "\LogicalDisk(_Total)\% Free Space"

# Multiple counters
$counters = @(
    "\Processor(_Total)\% Processor Time",
    "\Memory\Available MBytes",
    "\Network Interface(*)\Bytes Total/sec"
)
Get-Counter -Counter $counters -SampleInterval 5 -MaxSamples 10

# Performance counter sets
Get-Counter -ListSet Processor
Get-Counter -ListSet Memory
```

### Task Manager và Resource Monitor
```cmd
# Launch tools
taskmgr                          # Task Manager
resmon                           # Resource Monitor
perfmon                          # Performance Monitor
```

### System Information Commands
```powershell
# System information
Get-ComputerInfo
Get-WmiObject -Class Win32_ComputerSystem
Get-CimInstance -ClassName Win32_OperatingSystem

# Hardware information
Get-WmiObject -Class Win32_Processor
Get-WmiObject -Class Win32_PhysicalMemory
Get-WmiObject -Class Win32_LogicalDisk

# Installed software
Get-WmiObject -Class Win32_Product
Get-ItemProperty HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*

# Running processes
Get-Process | Sort-Object CPU -Descending | Select-Object -First 10
Get-Process | Sort-Object WorkingSet -Descending | Select-Object -First 10
```

## 🔧 9. IIS Web Server Management

### IIS Installation và Configuration
```powershell
# Install IIS feature
Enable-WindowsOptionalFeature -Online -FeatureName IIS-WebServerRole
Enable-WindowsOptionalFeature -Online -FeatureName IIS-WebServer
Enable-WindowsOptionalFeature -Online -FeatureName IIS-CommonHttpFeatures
Enable-WindowsOptionalFeature -Online -FeatureName IIS-HttpErrors
Enable-WindowsOptionalFeature -Online -FeatureName IIS-HttpRedirect
Enable-WindowsOptionalFeature -Online -FeatureName IIS-ApplicationDevelopment
Enable-WindowsOptionalFeature -Online -FeatureName IIS-ASPNET45

# IIS PowerShell module
Import-Module WebAdministration

# Sites management
Get-Website
New-Website -Name "TestSite" -Port 8080 -PhysicalPath "C:\inetpub\testsite"
Set-Website -Name "TestSite" -Port 8081
Remove-Website -Name "TestSite"

# Application pools
Get-IISAppPool
New-WebAppPool -Name "TestAppPool"
Set-ItemProperty -Path "IIS:\AppPools\TestAppPool" -Name "processModel.identityType" -Value "ApplicationPoolIdentity"
Remove-WebAppPool -Name "TestAppPool"
```

### IIS Configuration
```powershell
# Bindings
New-WebBinding -Name "Default Web Site" -IPAddress "*" -Port 443 -Protocol https
Get-WebBinding -Name "Default Web Site"

# Virtual directories
New-WebVirtualDirectory -Site "Default Web Site" -Name "Images" -PhysicalPath "C:\Images"

# Authentication
Set-WebConfiguration -Filter "/system.webServer/security/authentication/anonymousAuthentication" -Value @{enabled="false"} -PSPath "IIS:\Sites\Default Web Site"
Set-WebConfiguration -Filter "/system.webServer/security/authentication/windowsAuthentication" -Value @{enabled="true"} -PSPath "IIS:\Sites\Default Web Site"
```

## 💡 Practical Scenarios cho Viettel IDC

### 1. Server Health Check Script
```powershell
# ServerHealthCheck.ps1
[CmdletBinding()]
param(
    [string]$LogPath = "C:\Logs\HealthCheck.log"
)

function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$timestamp - $Message" | Add-Content $LogPath
    Write-Output $Message
}

# System uptime
$uptime = (Get-Date) - (Get-CimInstance Win32_OperatingSystem).LastBootUpTime
Write-Log "System uptime: $($uptime.Days) days, $($uptime.Hours) hours"

# CPU usage
$cpu = Get-Counter "\Processor(_Total)\% Processor Time" | Select-Object -ExpandProperty CounterSamples | Select-Object -ExpandProperty CookedValue
Write-Log "CPU usage: $([math]::Round($cpu, 2))%"

# Memory usage
$memory = Get-CimInstance Win32_OperatingSystem
$memoryUsage = [math]::Round(($memory.TotalVisibleMemorySize - $memory.FreePhysicalMemory) / $memory.TotalVisibleMemorySize * 100, 2)
Write-Log "Memory usage: $memoryUsage%"

# Disk space
Get-CimInstance -ClassName Win32_LogicalDisk | Where-Object {$_.DriveType -eq 3} | ForEach-Object {
    $freePercent = [math]::Round($_.FreeSpace / $_.Size * 100, 2)
    Write-Log "Drive $($_.DeviceID) free space: $freePercent%"
}

# Critical services status
$criticalServices = @("Spooler", "BITS", "Winmgmt", "EventLog")
foreach ($service in $criticalServices) {
    $status = (Get-Service -Name $service).Status
    Write-Log "Service $service status: $status"
}
```

### 2. Automated Software Deployment
```powershell
# SoftwareDeployment.ps1
[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [string]$InstallerPath,
    
    [string]$LogPath = "C:\Logs\Deployment.log"
)

try {
    # Pre-installation checks
    if (-not (Test-Path $InstallerPath)) {
        throw "Installer not found: $InstallerPath"
    }
    
    # Stop related services
    $servicesToStop = @("MyAppService", "RelatedService")
    foreach ($service in $servicesToStop) {
        if (Get-Service -Name $service -ErrorAction SilentlyContinue) {
            Stop-Service -Name $service -Force
            "$(Get-Date): Stopped service $service" | Add-Content $LogPath
        }
    }
    
    # Install software
    $process = Start-Process -FilePath $InstallerPath -ArgumentList "/S" -Wait -PassThru
    if ($process.ExitCode -eq 0) {
        "$(Get-Date): Installation successful" | Add-Content $LogPath
    } else {
        throw "Installation failed with exit code: $($process.ExitCode)"
    }
    
    # Start services
    foreach ($service in $servicesToStop) {
        if (Get-Service -Name $service -ErrorAction SilentlyContinue) {
            Start-Service -Name $service
            "$(Get-Date): Started service $service" | Add-Content $LogPath
        }
    }
}
catch {
    "$(Get-Date): Error - $($_.Exception.Message)" | Add-Content $LogPath
    exit 1
}
```

### 3. Security Audit Script
```powershell
# SecurityAudit.ps1
$report = @()

# Check UAC status
$uac = Get-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" -Name "EnableLUA"
$report += "UAC Enabled: $($uac.EnableLUA -eq 1)"

# Check Windows Firewall
$firewallProfiles = Get-NetFirewallProfile
foreach ($profile in $firewallProfiles) {
    $report += "$($profile.Name) Firewall: $($profile.Enabled)"
}

# Check for admin accounts
$adminAccounts = Get-LocalGroupMember -Group "Administrators"
$report += "Administrator accounts: $($adminAccounts.Count)"

# Check password policy
$passwordPolicy = net accounts
$report += "Password policy: $($passwordPolicy -join '; ')"

# Check for shared folders
$shares = Get-SmbShare | Where-Object {$_.Name -ne "ADMIN$" -and $_.Name -ne "C$" -and $_.Name -ne "IPC$"}
$report += "Shared folders: $($shares.Count)"

# Output report
$report | Out-File "C:\Logs\SecurityAudit_$(Get-Date -Format 'yyyyMMdd').txt"
```

## 📝 Best Practices cho Windows Server

### 1. Performance Optimization
- Regular disk cleanup và defragmentation
- Monitor và manage page file size
- Configure virtual memory appropriately
- Regular registry cleanup
- Monitor service startup impact

### 2. Security Hardening
- Disable unnecessary services
- Configure strong password policies
- Enable account lockout policies
- Regular security updates
- Configure Windows Firewall properly
- Use least privilege principle

### 3. Monitoring và Maintenance
- Set up performance baselines
- Configure event log retention
- Schedule regular maintenance tasks
- Monitor disk space usage
- Regular backup verification

### 4. PowerShell Best Practices
- Use approved verbs for functions
- Include help documentation
- Implement proper error handling
- Use Write-Verbose for detailed output
- Follow consistent naming conventions

---
*Windows Server administration skills are essential for managing mixed environments at Viettel IDC. PowerShell automation will significantly improve efficiency and reduce manual errors.*
