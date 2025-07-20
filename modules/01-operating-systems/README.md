# Module 1: Hệ Điều Hành (Linux & Windows)

## 🎯 Mục tiêu Module
Nắm vững kiến thức cơ bản về quản lý và vận hành hệ điều hành Linux và Windows, đây là nền tảng cho tất cả các hoạt động IT infrastructure.

## 📋 Nội dung Chính

### Linux (70% trọng số)
#### 1. Cấu hình Hệ thống
- **File system management**: ext4, xfs, LVM
- **Networking**: IP configuration, routing, DNS
- **Firewall**: iptables, firewalld
- **Services**: systemd, service management

#### 2. Giám sát Hệ thống
- **Process monitoring**: ps, top, htop, systemd
- **Resource monitoring**: memory, CPU, disk I/O
- **Log analysis**: journalctl, /var/log/*, rsyslog
- **Performance tuning**: kernel parameters

#### 3. Bảo mật
- **SSH configuration**: key-based auth, hardening
- **SELinux**: policies, contexts, troubleshooting
- **User management**: sudo, groups, permissions
- **Package management**: yum/dnf, apt, security updates

#### 4. Troubleshooting
- **Boot process**: GRUB, systemd targets
- **Network issues**: netstat, ss, tcpdump
- **Storage issues**: fsck, mount, lsblk
- **Performance issues**: iostat, vmstat, sar

### Windows (30% trọng số)
#### 1. Cấu hình
- **Services management**: services.msc, PowerShell
- **Registry**: regedit, registry keys
- **Networking**: netsh, PowerShell networking
- **Event management**: Event Viewer, PowerShell

#### 2. Giám sát
- **Performance Monitor**: perfmon, counters
- **Event Viewer**: Windows logs, application logs
- **PowerShell**: Get-Process, Get-Service, monitoring
- **Task Manager**: advanced monitoring

#### 3. Bảo mật
- **Windows Firewall**: advanced settings
- **Active Directory**: user management (cơ bản)
- **Group Policy**: security policies
- **Windows Updates**: WSUS, PowerShell

## 🛠️ Kỹ năng Thực hành

### Linux Tasks
1. **System Installation & Configuration**
   - Cài đặt CentOS/RHEL/Ubuntu server
   - Cấu hình network tĩnh
   - Setup SSH key authentication
   - Configure firewall rules

2. **Service Management**
   - Install và configure Apache/Nginx
   - Setup MariaDB/PostgreSQL
   - Configure log rotation
   - Create custom systemd services

3. **Monitoring & Troubleshooting**
   - Setup monitoring với top/htop
   - Analyze system logs
   - Troubleshoot network connectivity
   - Performance optimization

### Windows Tasks
1. **Server Configuration**
   - Windows Server installation
   - Configure IIS web server
   - Setup file sharing (SMB)
   - PowerShell scripting basics

2. **Monitoring & Maintenance**
   - Configure Event Viewer
   - Setup Performance Monitor
   - Schedule maintenance tasks
   - PowerShell automation

## 📚 Tài liệu Tham khảo

### Linux
- Red Hat System Administration Guide
- Ubuntu Server Guide
- Linux Command Line and Shell Scripting Bible
- Linux Performance and Tuning Guidelines

### Windows
- Windows Server Administration Fundamentals
- PowerShell in a Month of Lunches
- Windows Server 2019 Administration Guide

## 🎓 Chứng chỉ Liên quan
- **Linux**: RHCSA, LPIC-1, CompTIA Linux+
- **Windows**: Microsoft MTA, MCSA Windows Server

## ⏱️ Thời gian Học: 2-3 tuần
- Tuần 1: Linux fundamentals + hands-on labs
- Tuần 2: Linux advanced + Windows basics
- Tuần 3: Integration + troubleshooting scenarios

## 🔗 Chuyển sang Module tiếp theo
Sau khi hoàn thành module này, bạn sẽ có nền tảng vững chắc để học **Module 2: Ảo hóa & Cloud**.
