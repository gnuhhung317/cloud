# System Monitoring và Troubleshooting - Giám sát và Xử lý Sự cố

## 🎯 Mục tiêu Học tập
Thành thạo các kỹ thuật monitoring, troubleshooting và performance tuning cho cả Linux và Windows systems, đáp ứng yêu cầu vận hành 24/7 tại Viettel IDC.

## 🔬 Lý thuyết về System Monitoring

### Monitoring Theory và Fundamentals

#### Định nghĩa về System Monitoring
**System Monitoring** là quá trình **thu thập, phân tích và báo cáo** về trạng thái hoạt động của systems, applications và infrastructure components. Mục đích chính là **đảm bảo availability, performance và security** của IT services.

**Các nguyên tắc cơ bản của Monitoring:**

1. **Observability**: Khả năng **hiểu internal state** của system thông qua external outputs
2. **Proactive Detection**: **Phát hiện sớm** các vấn đề trước khi chúng ảnh hưởng đến users
3. **Data-Driven Decisions**: **Ra quyết định dựa trên data** thay vì assumptions
4. **Continuous Improvement**: **Liên tục cải thiện** monitoring strategies dựa trên lessons learned

#### The Four Golden Signals (SRE Theory)

**Google SRE** đã định nghĩa **Four Golden Signals** là metrics quan trọng nhất cần monitor:

1. **Latency**: **Thời gian phản hồi** của requests
   - **Definition**: Time taken to serve a request
   - **Importance**: Direct impact lên user experience
   - **Measurement**: Response time, processing time, queue time

2. **Traffic**: **Lượng demand** đặt lên system
   - **Definition**: Amount of stress on system
   - **Measurement**: Requests per second, transactions per minute, concurrent users

3. **Errors**: **Tỷ lệ requests thất bại**
   - **Definition**: Rate of requests that fail
   - **Types**: Explicit errors (HTTP 500), implicit errors (HTTP 200 with wrong content)

4. **Saturation**: **Mức độ "fullness"** của service
   - **Definition**: How full service is
   - **Measurement**: CPU utilization, memory usage, disk I/O, network bandwidth

#### Monitoring Methodologies

**USE Method (Utilization, Saturation, Errors)**:
- **Utilization**: **Percentage of time** resource was busy
- **Saturation**: **Amount of work** resource has to do, often queued
- **Errors**: **Count of error events**

**RED Method (Rate, Errors, Duration)**:
- **Rate**: **Number of requests** per second
- **Errors**: **Number of failed requests** per second  
- **Duration**: **Amount of time** each request takes

**KPIS vs Metrics vs Indicators**:
- **KPIs**: **Business-level measurements** (revenue, customer satisfaction)
- **Metrics**: **Quantitative measurements** (CPU usage, response time)
- **Indicators**: **Signals** that suggest something might be wrong

## 📊 1. Linux System Monitoring

### Lý thuyết về CPU Monitoring

#### CPU Architecture và Performance Theory

**CPU (Central Processing Unit)** là **brain của computer system**, thực hiện **instruction execution và data processing**. Hiểu CPU architecture và behavior là crucial cho effective monitoring.

**CPU Components:**
1. **Cores**: **Physical processing units** - mỗi core có thể execute instructions independently
2. **Threads**: **Virtual processing units** - hyper-threading cho phép multiple threads per core
3. **Cache**: **High-speed memory** hierarchy (L1, L2, L3) để reduce memory access latency
4. **Registers**: **Fastest storage** directly accessible by CPU

**CPU States và Time Accounting:**

**User Time (%user)**:
- **Definition**: Time spent executing **user-space applications**
- **Characteristics**: Normal application code execution
- **High %user indicates**: CPU-intensive applications, computation-heavy workloads

**System Time (%system)**:
- **Definition**: Time spent executing **kernel code**
- **Includes**: System calls, kernel functions, device drivers
- **High %system indicates**: Heavy I/O operations, system calls overhead

**I/O Wait Time (%iowait)**:
- **Definition**: Time CPU spends **waiting for I/O operations** to complete
- **Important**: CPU is **idle** during iowait, nhưng system has pending I/O
- **High %iowait indicates**: I/O bottlenecks, slow storage, network delays

**Idle Time (%idle)**:
- **Definition**: Time CPU spends **doing nothing**
- **Calculation**: 100% - (user + system + iowait + other)
- **Interpretation**: Available CPU capacity

**Steal Time (%steal)** - Virtual Environments:
- **Definition**: Time **stolen by hypervisor** for other virtual machines
- **Context**: Only relevant trong virtualized environments
- **High %steal indicates**: Resource contention trong hypervisor

#### Load Average Theory

**Load Average** represents **system load** over time periods (1, 5, 15 minutes), indicating **how many processes** are running hoặc waiting for resources.

**Calculation Formula**:
```
Load Average = (Running Processes + Waiting Processes) / Time Period
```

**Interpretation Guidelines**:
- **Load = Number of CPU cores**: System at **full capacity**
- **Load < Number of CPU cores**: System has **spare capacity**  
- **Load > Number of CPU cores**: System is **overloaded** (processes waiting)

**Example on 4-core system**:
- Load 2.0: **50% utilization** (2/4 cores busy)
- Load 4.0: **100% utilization** (all cores busy)
- Load 6.0: **150% utilization** (overloaded, 2 processes waiting)

### CPU Monitoring và Analysis

#### Real-time CPU Monitoring - Lý thuyết và Implementation

**Process Scheduling Theory**:
Linux sử dụng **Completely Fair Scheduler (CFS)** để manage CPU time allocation:

- **Virtual Runtime**: Mỗi process có **virtual runtime** tracking CPU time used
- **Red-Black Tree**: Processes stored trong **balanced binary tree** for O(log n) operations
- **Fairness**: Scheduler aims để give **equal CPU time** cho all processes với same priority

```bash
# Top - Classic process monitor với detailed explanation
top                              # Real-time process view
# Top display interpretation:
# PID: Process ID
# USER: Process owner
# PR: Priority (20 = default, lower = higher priority)
# NI: Nice value (-20 to 19, affects priority)
# VIRT: Virtual memory used by process
# RES: Resident memory (physical memory currently used)
# SHR: Shared memory
# S: Process state (R=running, S=sleeping, D=uninterruptible sleep, Z=zombie)
# %CPU: Percentage of CPU time used since last update
# %MEM: Percentage of physical memory used
# TIME+: Total CPU time used by process
# COMMAND: Command name/command line

top -u username                  # Filter by user
top -p PID                       # Monitor specific process

# Htop - Enhanced top với advanced features
htop                            # Interactive process viewer
# Htop advantages:
# - Color-coded display
# - Mouse support
# - Tree view of processes
# - Easy sorting và filtering
# - Built-in kill functionality
htop -u username                # Filter by user
htop -t                         # Tree view showing parent-child relationships

# System load interpretation
uptime                          # Load averages
# Output example: up 25 days, 3:45, 2 users, load average: 0.25, 0.30, 0.35
# Numbers represent: 1-minute, 5-minute, 15-minute averages
w                               # Who is logged in và load
cat /proc/loadavg               # Raw load data: current + 1,5,15min averages + running/total processes + last PID
```

#### CPU Statistics và Performance Analysis

**System Activity Reporter (SAR) Theory**:
SAR is part of **sysstat package**, provides **historical performance data** collection và analysis. SAR data is crucial cho **capacity planning và trend analysis**.

```bash
# Sar - System Activity Reporter với comprehensive analysis
sar -u 1 10                     # CPU utilization every 1 second, 10 times
# Output columns explained:
# %user: User space CPU usage
# %nice: User space với low priority (nice > 0)
# %system: Kernel space CPU usage  
# %iowait: Waiting for I/O completion
# %steal: Time stolen by hypervisor (virtualization)
# %idle: Idle time

sar -u -f /var/log/sa/sa01      # Historical CPU data from specific day
# SAR data collection:
# - Data collected by sadc (system activity data collector)
# - Stored in /var/log/sa/ directory
# - Default collection interval: 10 minutes

# Mpstat - Multiprocessor statistics với per-CPU analysis
mpstat                          # Current CPU stats across all CPUs
mpstat 1 5                      # Every 1 second, 5 times
mpstat -P ALL                   # Per-CPU statistics
# Per-CPU analysis benefits:
# - Identify CPU core imbalances
# - Detect single-threaded bottlenecks
# - Analyze NUMA effects
# - Understand CPU affinity impacts

# Iostat - I/O and CPU statistics
iostat -c 1 5                   # CPU stats only
# Iostat provides correlation between CPU và I/O performance
```

#### Advanced Process Analysis Theory

**Process Memory Model**:
Linux processes có **virtual memory address space** được mapped đến **physical memory** bởi MMU (Memory Management Unit).

**Memory Types**:
- **Virtual Memory (VIRT)**: **Total virtual address space** used by process
- **Resident Memory (RES)**: **Physical memory currently in RAM**
- **Shared Memory (SHR)**: **Memory shared** with other processes
- **Swap**: **Memory stored on disk** when physical memory full

```bash
# Process monitoring với memory analysis
ps aux                          # All processes với resource usage
# ps aux columns:
# USER: Process owner
# PID: Process ID
# %CPU: CPU percentage since process start
# %MEM: Physical memory percentage  
# VSZ: Virtual memory size (KB)
# RSS: Resident Set Size - physical memory (KB)
# TTY: Terminal associated with process
# STAT: Process state codes
# START: Start time
# TIME: CPU time consumed
# COMMAND: Command line

ps -ef                          # Full format với parent-child relationships
ps -eo pid,ppid,cmd,%mem,%cpu --sort=-%cpu  # Custom format sorted by CPU usage

# Process tree analysis - Understanding process hierarchy
pstree                          # Process tree visualization
# Process tree shows:
# - Parent-child relationships
# - Process spawning patterns  
# - Service dependencies
# - System initialization flow
pstree -p                       # With PIDs for detailed analysis
pstree username                 # User's process tree

# Advanced process statistics
pidstat                         # Per-process statistics
# pidstat provides:
# - CPU usage per process
# - Memory usage trends
# - I/O statistics per process
# - Context switching rates
pidstat 1 5                     # Every 1 second, 5 times for trending
pidstat -p PID                  # Specific process detailed analysis

# Resource-intensive process identification
ps aux --sort=-%cpu | head -10  # Top CPU consumers
ps aux --sort=-%mem | head -10  # Top memory consumers
# Sorting strategies:
# - CPU sorting: Identify compute-intensive processes
# - Memory sorting: Find memory leaks hoặc heavy applications
# - Combined analysis: Understand resource usage patterns
```

### Lý thuyết về Memory Management và Monitoring

#### Linux Memory Architecture Theory

**Virtual Memory System**:
Linux sử dụng **virtual memory management** để cung cấp **illusion of unlimited memory** cho processes. System này bao gồm nhiều components working together:

**Memory Hierarchy**:
1. **CPU Registers**: Fastest access, limited capacity
2. **CPU Cache (L1/L2/L3)**: High-speed buffer between CPU và main memory
3. **Physical RAM**: Main system memory
4. **Swap Space**: Disk-based virtual memory extension
5. **Storage**: Slowest but largest capacity

**Virtual Memory Concepts**:

**Virtual Address Space**:
- Mỗi process có **independent virtual address space**
- **32-bit systems**: 4GB virtual address space per process
- **64-bit systems**: Theoretically 16 exabytes (practical limits apply)

**Memory Mapping**:
- **Page Tables**: Map virtual addresses to physical addresses
- **Page Size**: Typically 4KB on x86/x64 systems
- **Translation Lookaside Buffer (TLB)**: Cache cho frequently used page translations

**Memory Types và Categories**:

**Physical Memory Usage**:
- **Used Memory**: Actually occupied by processes và kernel
- **Free Memory**: Completely unused memory
- **Buffer Memory**: Disk block cache trong kernel
- **Cached Memory**: Page cache cho file content

**Linux Memory Management Philosophy**:
Linux follows **"free memory is wasted memory"** principle:
- **Aggressive Caching**: Use available memory cho filesystem cache
- **Lazy Allocation**: Allocate physical memory chỉ khi actually needed
- **Copy-on-Write (COW)**: Share memory pages until modification

#### Memory Pressure và Swapping Theory

**Memory Pressure Indicators**:

**Page Fault Types**:
1. **Minor Page Faults**: Page exists trong memory but not trong process page table
2. **Major Page Faults**: Page must be loaded from disk (swap hoặc file)

**Swapping Mechanisms**:
- **Swap Out**: Move less frequently used pages to disk
- **Swap In**: Load pages back from disk to memory
- **Thrashing**: Excessive swapping causing performance degradation

**OOM (Out of Memory) Killer**:
- **Last Resort**: When system runs out of memory
- **Process Selection**: Uses heuristics to choose victim process
- **OOM Score**: Each process has score based on memory usage và importance

### Memory Monitoring Implementation

```bash
# Basic memory information với comprehensive explanation
free                            # Memory usage overview
# free command output explained:
#               total        used        free      shared  buff/cache   available
# Mem:        16777216     8388608     2097152      524288     6291456    7340032
#
# total: Total physical RAM
# used: Used memory (total - free - buffers - cache)  
# free: Completely unused memory
# shared: Memory used by tmpfs filesystems
# buff/cache: Buffers (metadata) + Cache (file contents)
# available: Estimate of available memory for new applications

free -h                         # Human readable format (GB, MB, KB)
free -m                         # Display in megabytes
free -s 5                       # Update every 5 seconds for trending

# Detailed memory information
cat /proc/meminfo               # Comprehensive memory statistics
# Key /proc/meminfo fields:
# MemTotal: Total usable RAM
# MemFree: Amount of free memory
# MemAvailable: Available memory for applications
# Buffers: Temporary storage for raw disk blocks
# Cached: In-memory cache for files read from disk
# SwapCached: Memory that was swapped out và swapped back in
# Active: Recently used memory, less likely to be reclaimed
# Inactive: Less recently used memory, candidates for reclaim
# Slab: Kernel data structures cache

# Virtual memory statistics
vmstat                          # Virtual memory statistics snapshot
vmstat 1 5                      # Every 1 second, 5 times for trending
# vmstat columns explanation:
# Procs:
#   r: processes waiting for run time  
#   b: processes in uninterruptible sleep
# Memory:
#   swpd: virtual memory used (KB)
#   free: idle memory (KB)
#   buff: memory used as buffers (KB)
#   cache: memory used as cache (KB)
# Swap:
#   si: memory swapped in from disk (KB/s)
#   so: memory swapped out to disk (KB/s)
# IO:
#   bi: blocks received from block device (blocks/s)
#   bo: blocks sent to block device (blocks/s)
# System:
#   in: interrupts per second
#   cs: context switches per second
# CPU:
#   us, sy, id, wa, st: user, system, idle, wait, stolen time percentages

# Memory breakdown analysis:
# Available Memory Calculation:
# Available ≈ Free + Buffers + Cache - (some cache that can't be freed)
# This represents memory that can be allocated to applications
```

#### Advanced Memory Analysis

**Memory Usage by Process**:

```bash
# Process memory analysis với detailed interpretation  
ps aux --sort=-%mem | head -20  # Top memory consumers
# %MEM calculation: (RSS / Total Physical Memory) * 100
# RSS (Resident Set Size): Physical memory currently used by process

# Detailed process memory mapping
pmap PID                        # Memory map of specific process
# pmap output shows:
# - Virtual memory segments
# - Memory permissions (r/w/x)
# - File mappings vs anonymous memory
# - Shared libraries vs private memory

pmap -d PID                     # Detailed memory map với additional info
# Additional fields:
# - Dirty pages: Modified pages not yet written to disk
# - Writeable/private pages: Process-specific modifiable memory
# - Address space layout: Understanding memory organization

# Memory pressure analysis
sar -r                          # Memory utilization statistics
sar -r 1 10                     # Memory utilization trending
# SAR memory fields:
# kbmemfree: Free memory (KB)
# kbmemused: Used memory (KB) 
# %memused: Percentage of memory used
# kbbuffers: Kernel buffers (KB)
# kbcached: Cached memory (KB)
# kbcommit: Committed memory (KB) - memory allocated by processes
# %commit: Percentage of committed memory

sar -S                          # Swap usage statistics
sar -W                          # Swapping activity (pages swapped in/out)
# Swap analysis:
# pswpin/s: Pages swapped in per second
# pswpout/s: Pages swapped out per second
# High swap activity indicates memory pressure

# Out of Memory (OOM) analysis
dmesg | grep -i "killed process" # OOM killer messages
# OOM killer selection criteria:
# - Memory usage (RSS + swap)
# - Process lifetime
# - Process importance (oom_score_adj)
# - Whether process is privileged

grep -i "out of memory" /var/log/messages
# System logs contain detailed OOM information:
# - Available memory at time of OOM
# - Process memory usage
# - Kernel memory usage
# - Why OOM killer was triggered
```

#### Swap Space Theory và Monitoring

**Swap Space Architecture**:

**Swap Types**:
1. **Swap Partitions**: Dedicated disk partitions cho swap
2. **Swap Files**: Regular files used as swap space
3. **Swap Priority**: Multiple swap spaces với different priorities

**Swap Strategies**:
- **Swappiness Parameter**: Controls tendency to swap pages
  - Value 0-100: 0 = avoid swapping, 100 = aggressive swapping
  - Default: Usually 60
- **Swap Algorithms**: LRU (Least Recently Used) based selection

```bash
# Swap monitoring và analysis
swapon -s                       # Active swap devices
# Output shows:
# - Swap device/file path
# - Type (partition hoặc file)
# - Size in KB
# - Used space
# - Priority level

cat /proc/swaps                 # Swap information from kernel perspective
# Similar to swapon -s but directly from kernel

# Swap activity monitoring
vmstat 1                        # Monitor si (swap in) và so (swap out) columns
# Swap activity interpretation:
# si > 0: Pages being read from swap (memory pressure recovery)
# so > 0: Pages being written to swap (memory pressure)
# Both > 0: Active swapping (potential thrashing)

sar -S 1 10                     # Detailed swap statistics
# Additional swap metrics:
# kbswpfree: Free swap space
# kbswpused: Used swap space  
# %swpused: Percentage of swap used
# kbswpcad: Cached swap (swapped out then back in)

# Memory pressure indicators (modern kernels)
cat /proc/pressure/memory       # PSI (Pressure Stall Information)
# PSI provides:
# - some avg10/avg60/avg300: Percentage of time some processes waited for memory
# - full avg10/avg60/avg300: Percentage of time all processes waited for memory
# - total: Total time spent in pressure state
```

### Lý thuyết về Disk I/O và Storage Performance

#### Storage Subsystem Architecture

**Storage Hierarchy Theory**:
Modern systems có **multi-tier storage hierarchy** với different performance characteristics:

1. **CPU Cache**: Nanoseconds access time
2. **RAM**: Microseconds access time  
3. **SSD**: Milliseconds access time
4. **HDD**: 5-15 milliseconds access time
5. **Network Storage**: 10-100+ milliseconds access time

**I/O Subsystem Components**:

**Block Layer**:
- **Block Devices**: Storage devices that transfer data trong fixed-size blocks
- **I/O Scheduler**: Determines order of I/O requests to optimize performance
- **Request Queue**: Buffer cho pending I/O operations

**I/O Schedulers**:
1. **Deadline**: Ensures maximum latency bounds cho reads và writes
2. **CFQ (Complete Fair Queuing)**: Provides fair access across processes
3. **NOOP**: Minimal scheduling, optimal cho SSDs
4. **mq-deadline**: Multi-queue version của deadline scheduler

**File System Layer**:
- **VFS (Virtual File System)**: Abstraction layer cho different filesystem types
- **Page Cache**: Kernel cache cho file content trong memory
- **Buffer Cache**: Kernel cache cho filesystem metadata

#### Disk Performance Metrics Theory

**IOPS (Input/Output Operations Per Second)**:
- **Definition**: Number of I/O operations device có thể perform per second
- **Factors**: Access patterns, block size, queue depth, storage type
- **Typical Values**:
  - HDD: 100-200 IOPS
  - SATA SSD: 10,000-30,000 IOPS  
  - NVMe SSD: 100,000+ IOPS

**Throughput (Bandwidth)**:
- **Definition**: Amount of data transferred per unit time
- **Units**: MB/s, GB/s
- **Relationship**: Throughput = IOPS × Average I/O Size

**Latency Components**:
- **Service Time**: Time device takes to process request
- **Wait Time**: Time request spends trong queue
- **Total Latency**: Service Time + Wait Time

**Queue Depth**:
- **Definition**: Number of outstanding I/O requests
- **Impact**: Higher queue depth có thể improve throughput but increase latency
- **Optimal Values**: Depends on storage type và workload

### Disk I/O Monitoring

#### Disk Usage
```bash
# Filesystem usage
df -h                           # Human readable filesystem usage
df -i                           # Inode usage
du -sh /path/to/directory       # Directory size
du -sh * | sort -hr             # Sort directories by size

# Large file detection
find /path -type f -size +100M  # Files larger than 100MB
find /path -type f -size +1G    # Files larger than 1GB
ncdu /path                      # Interactive disk usage analyzer
```

#### I/O Performance
```bash
# I/O statistics
iostat                          # I/O statistics
iostat -x 1 5                   # Extended stats every 1 second
iostat -d 1 5                   # Device stats only

# Per-process I/O
iotop                           # I/O usage by process
iotop -o                        # Only show processes doing I/O
pidstat -d 1 5                  # Per-process I/O stats

# I/O metrics interpretation:
# r/s, w/s: reads/writes per second
# rkB/s, wkB/s: KB read/written per second
# %util: Percentage of time device was busy
# await: Average wait time for I/O requests
# svctm: Average service time for I/O requests
```

#### Advanced I/O Analysis
```bash
# Block device information
lsblk                           # List block devices
lsblk -f                        # With filesystem info
blkid                           # Block device attributes

# I/O scheduler
cat /sys/block/sda/queue/scheduler  # Current I/O scheduler
echo mq-deadline > /sys/block/sda/queue/scheduler  # Change scheduler

# Filesystem performance
sync && echo 3 > /proc/sys/vm/drop_caches  # Clear filesystem cache
time dd if=/dev/zero of=testfile bs=1G count=1 oflag=direct  # Write test
time dd if=testfile of=/dev/null bs=1G count=1 iflag=direct  # Read test
```

### Network Monitoring

#### Network Interface Statistics
```bash
# Interface statistics
ip -s link                      # Interface statistics
cat /proc/net/dev               # Network device statistics
sar -n DEV 1 5                  # Network interface activity

# Network configuration
ip addr show                    # IP addresses
ip route show                   # Routing table
ss -tuln                        # Listening sockets
netstat -tuln                   # Listening sockets (legacy)
```

#### Network Traffic Analysis
```bash
# Real-time network monitoring
iftop                           # Network usage by connection
iftop -i eth0                   # Specific interface
nethogs                         # Network usage by process
bmon                            # Bandwidth monitor

# Network connections
ss -tulpn                       # All sockets with processes
ss -t state established         # Established TCP connections
ss -t state time-wait           # TIME_WAIT connections

# Traffic capture và analysis
tcpdump -i eth0                 # Capture packets
tcpdump -i eth0 port 80         # HTTP traffic only
tcpdump -i eth0 host 192.168.1.1  # Specific host
wireshark                       # GUI packet analyzer
```

#### Network Performance Testing
```bash
# Bandwidth testing
iperf3 -s                       # Server mode
iperf3 -c server_ip             # Client mode
iperf3 -c server_ip -t 30       # 30-second test

# Connectivity testing
ping -c 5 google.com            # Ping test
traceroute google.com           # Route tracing
mtr google.com                  # My traceroute (continuous)

# DNS performance
dig google.com                  # DNS lookup
nslookup google.com             # DNS lookup (legacy)
host google.com                 # DNS lookup
```

## 🔍 2. Advanced Troubleshooting Techniques

### Lý thuyết về Systematic Troubleshooting

#### Troubleshooting Methodology Framework

**Scientific Approach to Problem Solving**:
Effective troubleshooting requires **systematic methodology** thay vì random trial-and-error approach. Framework này được based trên **scientific method** adapted cho IT environments.

**The Troubleshooting Process**:

1. **Problem Identification và Scope Definition**:
   - **Symptom Collection**: Gather all observable symptoms
   - **Impact Assessment**: Determine business và technical impact
   - **Scope Boundary**: Define what is và isn't affected
   - **Timeline Establishment**: When did problem start, frequency, patterns

2. **Information Gathering và Evidence Collection**:
   - **System State Documentation**: Current system configuration và status
   - **Historical Analysis**: Recent changes, maintenance, updates
   - **Environmental Factors**: Load patterns, external dependencies
   - **Reproduction Steps**: Conditions that trigger the problem

3. **Hypothesis Formation**:
   - **Root Cause Theories**: Based on symptoms và available evidence
   - **Probability Assessment**: Likelihood of each hypothesis
   - **Test Design**: How to validate hoặc invalidate each theory
   - **Resource Requirements**: Time, tools, và access needed for testing

4. **Testing và Validation**:
   - **Controlled Testing**: Isolate variables, test one hypothesis at a time
   - **Non-destructive First**: Start với tests that won't impact production
   - **Evidence Documentation**: Record results of each test
   - **Hypothesis Refinement**: Modify theories based on test results

5. **Solution Implementation**:
   - **Risk Assessment**: Evaluate potential impact of proposed solution
   - **Rollback Plan**: Prepare method to reverse changes if needed
   - **Implementation Strategy**: Staged approach, testing at each step
   - **Monitoring**: Verify solution effectiveness

6. **Documentation và Prevention**:
   - **Root Cause Documentation**: Record actual cause và contributing factors
   - **Solution Documentation**: Steps taken và lessons learned
   - **Process Improvement**: Update procedures to prevent recurrence
   - **Knowledge Sharing**: Communicate findings to team

#### Troubleshooting Tools và Techniques

**System Analysis Tools Classification**:

**Real-time Monitoring Tools**:
- **Purpose**: Observe current system behavior
- **Examples**: top, htop, iostat, sar
- **Use Cases**: Performance bottleneck identification, resource utilization analysis

**Historical Analysis Tools**:
- **Purpose**: Analyze trends và patterns over time  
- **Examples**: sar logs, system logs, performance baselines
- **Use Cases**: Capacity planning, incident correlation, trend analysis

**Deep Diagnostic Tools**:
- **Purpose**: Detailed investigation of specific components
- **Examples**: strace, tcpdump, gdb, perf
- **Use Cases**: Application debugging, network analysis, kernel investigation

### System Performance Analysis

#### Performance Baseline Theory

**Baseline Establishment**:
Performance baselines provide **reference points** để compare current performance against known good states. Without baselines, it's impossible to determine if current performance is normal hoặc degraded.

**Baseline Components**:
1. **Resource Utilization**: CPU, memory, disk, network usage patterns
2. **Application Metrics**: Response times, throughput, error rates
3. **System Metrics**: Load averages, context switches, interrupts
4. **Business Metrics**: Transaction volumes, user activity patterns

**Baseline Collection Strategy**:
- **Time Periods**: Collect data across different time periods (hourly, daily, weekly, monthly)
- **Load Conditions**: Capture performance under various load conditions
- **Seasonal Variations**: Account for business cycles và seasonal patterns
- **Configuration States**: Document performance after major changes

```bash
# Create performance baseline script với comprehensive data collection
#!/bin/bash
# baseline.sh - System performance baseline establishment

LOGFILE="/var/log/baseline_$(date +%Y%m%d_%H%M%S).log"

echo "=== SYSTEM PERFORMANCE BASELINE ===" >> $LOGFILE
echo "Date: $(date)" >> $LOGFILE
echo "Hostname: $(hostname)" >> $LOGFILE
echo "Uptime: $(uptime)" >> $LOGFILE
echo "Kernel: $(uname -r)" >> $LOGFILE
echo "" >> $LOGFILE

# Hardware configuration baseline
echo "=== HARDWARE CONFIGURATION ===" >> $LOGFILE
lscpu >> $LOGFILE
echo "" >> $LOGFILE
echo "Memory Configuration:" >> $LOGFILE
dmidecode -t memory | grep -E "Size|Speed|Type:" >> $LOGFILE 2>/dev/null
echo "" >> $LOGFILE

# System resource baseline
echo "=== SYSTEM RESOURCES ===" >> $LOGFILE
echo "CPU Information:" >> $LOGFILE
cat /proc/cpuinfo | grep -E "processor|model name|cpu MHz|cache size" >> $LOGFILE
echo "" >> $LOGFILE

echo "Memory Information:" >> $LOGFILE
free -h >> $LOGFILE
cat /proc/meminfo | head -20 >> $LOGFILE
echo "" >> $LOGFILE

echo "Storage Information:" >> $LOGFILE
df -h >> $LOGFILE
lsblk >> $LOGFILE
echo "" >> $LOGFILE

echo "Network Configuration:" >> $LOGFILE
ip addr show >> $LOGFILE
echo "" >> $LOGFILE

# Performance metrics baseline
echo "=== PERFORMANCE METRICS ===" >> $LOGFILE
echo "Load Average:" >> $LOGFILE
cat /proc/loadavg >> $LOGFILE
echo "" >> $LOGFILE

echo "Running Processes:" >> $LOGFILE
ps aux --sort=-%cpu | head -20 >> $LOGFILE
echo "" >> $LOGFILE

echo "Network Connections:" >> $LOGFILE
ss -tuln >> $LOGFILE
echo "" >> $LOGFILE

echo "System Statistics:" >> $LOGFILE
vmstat >> $LOGFILE
iostat >> $LOGFILE
echo "" >> $LOGFILE

# Service status baseline
echo "=== SERVICE STATUS ===" >> $LOGFILE
systemctl list-units --type=service --state=active >> $LOGFILE
echo "" >> $LOGFILE

echo "Baseline saved to: $LOGFILE"
```

#### Continuous Performance Monitoring

**Monitoring Strategy Design**:

**Sampling Intervals**:
- **High Frequency (1-5 seconds)**: Real-time troubleshooting, immediate issue detection
- **Medium Frequency (1-5 minutes)**: Operational monitoring, alerting
- **Low Frequency (15+ minutes)**: Trend analysis, capacity planning

**Data Retention Strategy**:
- **Raw Data**: Keep detailed data for short periods (days to weeks)
- **Aggregated Data**: Keep summarized data for longer periods (months to years)
- **Anomaly Data**: Preserve unusual events indefinitely for analysis

```bash
#!/bin/bash
# monitor.sh - Continuous performance monitoring với intelligent data collection

INTERVAL=60
LOGFILE="/var/log/performance_$(date +%Y%m%d).log"
ALERT_THRESHOLD_CPU=80
ALERT_THRESHOLD_MEM=85
ALERT_THRESHOLD_DISK=90

# Initialize log với headers
if [ ! -f "$LOGFILE" ]; then
    echo "timestamp,cpu_usage,mem_usage,load_avg,disk_usage,connections,disk_io_read,disk_io_write" > $LOGFILE
fi

while true; do
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
    
    # CPU usage calculation
    CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
    
    # Memory usage calculation với detailed breakdown
    MEM_USAGE=$(free | grep Mem | awk '{printf "%.2f", $3/$2 * 100.0}')
    
    # Load average (1-minute)
    LOAD_AVG=$(cat /proc/loadavg | awk '{print $1}')
    
    # Disk usage (root filesystem)
    DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | cut -d'%' -f1)
    
    # Network connections count
    CONNECTIONS=$(ss -t state established | wc -l)
    
    # Disk I/O rates
    DISK_IO_READ=$(iostat -d 1 2 | tail -n +4 | awk '{read += $3} END {print read}')
    DISK_IO_WRITE=$(iostat -d 1 2 | tail -n +4 | awk '{write += $4} END {print write}')
    
    # Log data point
    echo "$TIMESTAMP,$CPU_USAGE,$MEM_USAGE,$LOAD_AVG,$DISK_USAGE,$CONNECTIONS,$DISK_IO_READ,$DISK_IO_WRITE" >> $LOGFILE
    
    # Alert logic
    if (( $(echo "$CPU_USAGE > $ALERT_THRESHOLD_CPU" | bc -l) )); then
        echo "ALERT: High CPU usage ($CPU_USAGE%) at $TIMESTAMP" | logger -t "performance_monitor"
    fi
    
    if (( $(echo "$MEM_USAGE > $ALERT_THRESHOLD_MEM" | bc -l) )); then
        echo "ALERT: High memory usage ($MEM_USAGE%) at $TIMESTAMP" | logger -t "performance_monitor"
    fi
    
    if [ "$DISK_USAGE" -gt "$ALERT_THRESHOLD_DISK" ]; then
        echo "ALERT: High disk usage ($DISK_USAGE%) at $TIMESTAMP" | logger -t "performance_monitor"
    fi
    
    sleep $INTERVAL
done
```

### Log Analysis và Troubleshooting

#### Centralized Logging Analysis
```bash
# System logs analysis
journalctl                      # All systemd logs
journalctl -f                   # Follow logs in real-time
journalctl -u service_name      # Specific service logs
journalctl --since "1 hour ago" # Recent logs
journalctl --since "2024-01-01" --until "2024-01-02"  # Date range

# Log filtering
journalctl -p err               # Error messages only
journalctl -p warning           # Warning and above
journalctl --grep="ERROR"       # Search for pattern

# Traditional logs
tail -f /var/log/messages       # System messages
tail -f /var/log/secure         # Authentication logs
tail -f /var/log/maillog        # Mail logs
tail -f /var/log/httpd/access_log  # Web server access
tail -f /var/log/httpd/error_log   # Web server errors
```

#### Log Analysis Tools
```bash
# Text processing for log analysis
grep "ERROR" /var/log/messages | wc -l  # Count errors
awk '{print $1}' /var/log/httpd/access_log | sort | uniq -c | sort -nr  # Top IPs
sed -n '/ERROR/,/END/p' /var/log/application.log  # Extract error blocks

# Log rotation management
logrotate -d /etc/logrotate.conf  # Debug log rotation
logrotate -f /etc/logrotate.conf  # Force log rotation

# Advanced log analysis
goaccess /var/log/httpd/access_log --log-format=COMBINED  # Web log analyzer
multitail /var/log/messages /var/log/secure  # Multiple log files
lnav /var/log/messages          # Log navigator
```

### System Diagnostics

#### Hardware Diagnostics
```bash
# Hardware information
lshw                            # List hardware
lshw -short                     # Brief hardware list
lscpu                           # CPU information
lsusb                           # USB devices
lspci                           # PCI devices
lsblk                           # Block devices

# Memory testing
memtester 1G                    # Test 1GB of memory
badblocks /dev/sdb              # Check for bad blocks

# Temperature monitoring
sensors                         # Hardware sensors
watch -n 1 sensors              # Monitor temperatures

# System health
dmesg                           # Kernel messages
dmesg | grep -i error           # Kernel errors
cat /var/log/dmesg              # Boot messages
```

#### Network Diagnostics
```bash
# Network connectivity
ping -c 4 8.8.8.8              # Basic connectivity
ping6 -c 4 2001:4860:4860::8888  # IPv6 connectivity
traceroute 8.8.8.8             # Route tracing
mtr --report 8.8.8.8           # Network quality report

# DNS diagnostics
dig @8.8.8.8 google.com         # DNS query
dig +trace google.com           # Trace DNS resolution
nslookup google.com 8.8.8.8     # DNS lookup

# Port connectivity
telnet google.com 80            # Test TCP port
nc -zv google.com 80            # Port scan
nmap -p 80,443 google.com       # Port scan with nmap

# Network configuration validation
ip route get 8.8.8.8            # Route to destination
ss -rn                          # Routing table
arp -a                          # ARP table
```

### Performance Troubleshooting Scenarios

#### High CPU Usage Investigation
```bash
# Identify high CPU processes
top -bn1 | head -20
ps aux --sort=-%cpu | head -10

# CPU per core
mpstat -P ALL

# Check for CPU-bound processes
pidstat -u 1 5

# CPU wait states
iostat -c 1 5

# Investigation steps:
# 1. Identify the process consuming CPU
# 2. Check if it's a legitimate process
# 3. Analyze process behavior with strace
# 4. Check for infinite loops or inefficient code
# 5. Consider process limits và nice values
```

#### Memory Issues Investigation
```bash
# Memory pressure indicators
free -h
cat /proc/meminfo
vmstat 1 5

# Check for memory leaks
ps aux --sort=-%mem | head -20
pmap -d PID

# OOM killer analysis
dmesg | grep -i "killed process"
grep -i "out of memory" /var/log/messages

# Swap analysis
swapon -s
vmstat 1 5  # Look at si/so columns

# Investigation steps:
# 1. Identify memory-consuming processes
# 2. Check for memory leaks
# 3. Analyze swap usage
# 4. Review OOM killer logs
# 5. Consider memory limits và tuning
```

#### Disk I/O Performance Issues
```bash
# I/O bottleneck identification
iostat -x 1 5
iotop -o

# Disk space issues
df -h
du -sh /* | sort -hr

# Inode exhaustion
df -i

# File system errors
dmesg | grep -i "error"
fsck /dev/sdb1  # Check filesystem (unmounted)

# Investigation steps:
# 1. Check disk utilization (%util)
# 2. Identify I/O-heavy processes
# 3. Analyze wait times (await)
# 4. Check for disk errors
# 5. Consider I/O scheduler tuning
```

## 🖥️ 3. Windows System Monitoring

### Windows Performance Monitoring

#### Performance Monitor (PerfMon)
```powershell
# Key performance counters
Get-Counter "\Processor(_Total)\% Processor Time"
Get-Counter "\Memory\Available MBytes"
Get-Counter "\LogicalDisk(_Total)\% Free Space"
Get-Counter "\Network Interface(*)\Bytes Total/sec"

# Multiple counters with sampling
$counters = @(
    "\Processor(_Total)\% Processor Time",
    "\Memory\Available MBytes",
    "\LogicalDisk(C:)\% Free Space",
    "\System\Processor Queue Length"
)
Get-Counter -Counter $counters -SampleInterval 5 -MaxSamples 12

# Performance counter sets
Get-Counter -ListSet * | Where-Object {$_.CounterSetName -like "*Process*"}
Get-Counter -ListSet Processor | Select-Object -ExpandProperty Counter
```

#### System Resource Monitoring
```powershell
# CPU monitoring
Get-WmiObject -Class Win32_Processor | Select-Object Name, LoadPercentage
Get-CimInstance -ClassName Win32_PerfRawData_PerfOS_Processor

# Memory monitoring
Get-WmiObject -Class Win32_OperatingSystem | Select-Object TotalVisibleMemorySize, FreePhysicalMemory
$memory = Get-CimInstance Win32_OperatingSystem
$memUsagePercent = [math]::Round(($memory.TotalVisibleMemorySize - $memory.FreePhysicalMemory) / $memory.TotalVisibleMemorySize * 100, 2)

# Disk monitoring
Get-WmiObject -Class Win32_LogicalDisk | Select-Object DeviceID, Size, FreeSpace, @{Name="FreePercent";Expression={[math]::Round($_.FreeSpace/$_.Size*100,2)}}

# Process monitoring
Get-Process | Sort-Object CPU -Descending | Select-Object -First 10
Get-Process | Sort-Object WorkingSet -Descending | Select-Object -First 10
```

### Windows Event Log Analysis

#### Event Log Management
```powershell
# Get event logs
Get-EventLog -List
Get-WinEvent -ListLog * | Where-Object {$_.RecordCount -gt 0}

# Critical events
Get-EventLog -LogName System -EntryType Error -Newest 50
Get-EventLog -LogName Application -EntryType Error -Newest 50
Get-WinEvent -FilterHashtable @{LogName='System'; Level=1,2,3; StartTime=(Get-Date).AddHours(-24)}

# Security events
Get-WinEvent -FilterHashtable @{LogName='Security'; ID=4625; StartTime=(Get-Date).AddHours(-24)}  # Failed logons
Get-WinEvent -FilterHashtable @{LogName='Security'; ID=4624; StartTime=(Get-Date).AddHours(-24)}  # Successful logons

# Custom event queries
Get-WinEvent -FilterXPath "*[System[EventID=1000 and TimeCreated[timediff(@SystemTime) <= 86400000]]]"
```

#### Advanced Event Analysis
```powershell
# Event correlation script
$events = Get-WinEvent -FilterHashtable @{LogName='System'; StartTime=(Get-Date).AddHours(-24)}
$events | Group-Object Id | Sort-Object Count -Descending | Select-Object Count, Name

# Performance-related events
Get-WinEvent -FilterHashtable @{LogName='System'; ID=2004,2005}  # Resource exhaustion
Get-WinEvent -FilterHashtable @{LogName='Application'; ProviderName='Application Error'}

# Service-related events
Get-WinEvent -FilterHashtable @{LogName='System'; ID=7034,7035,7036}  # Service events
```

### Windows Network Monitoring

#### Network Performance
```powershell
# Network adapter statistics
Get-NetAdapterStatistics
Get-NetAdapterStatistics | Select-Object Name, BytesReceived, BytesSent

# Network connections
Get-NetTCPConnection | Where-Object {$_.State -eq "Established"}
Get-NetTCPConnection | Group-Object State | Select-Object Name, Count

# Network utilization
Get-Counter "\Network Interface(*)\Bytes Total/sec"
Get-Counter "\Network Interface(*)\Current Bandwidth"

# Network troubleshooting
Test-NetConnection google.com -Port 80
Test-NetConnection 192.168.1.1 -TraceRoute
Resolve-DnsName google.com
```

## 🚨 4. Incident Response Procedures

### Incident Detection và Classification

#### Alert Thresholds
```bash
# CPU threshold monitoring
cpu_threshold=80
cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1 | cut -d'.' -f1)
if [ $cpu_usage -gt $cpu_threshold ]; then
    echo "ALERT: CPU usage is ${cpu_usage}%" | mail -s "High CPU Alert" admin@company.com
fi

# Memory threshold monitoring
mem_threshold=90
mem_usage=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')
if [ $mem_usage -gt $mem_threshold ]; then
    echo "ALERT: Memory usage is ${mem_usage}%" | mail -s "High Memory Alert" admin@company.com
fi

# Disk space monitoring
disk_threshold=85
for filesystem in $(df -h | awk 'NR>1 {print $5 " " $6}'); do
    usage=$(echo $filesystem | awk '{print $1}' | cut -d'%' -f1)
    mount=$(echo $filesystem | awk '{print $2}')
    if [ $usage -gt $disk_threshold ]; then
        echo "ALERT: Disk usage on $mount is ${usage}%" | mail -s "Disk Space Alert" admin@company.com
    fi
done
```

#### Incident Response Checklist
```bash
# Incident response script template
#!/bin/bash
# incident_response.sh

INCIDENT_ID="INC-$(date +%Y%m%d-%H%M%S)"
LOG_DIR="/var/log/incidents"
INCIDENT_LOG="$LOG_DIR/$INCIDENT_ID.log"

mkdir -p $LOG_DIR

echo "=== INCIDENT RESPONSE: $INCIDENT_ID ===" | tee $INCIDENT_LOG
echo "Start Time: $(date)" | tee -a $INCIDENT_LOG

# 1. System snapshot
echo "=== SYSTEM SNAPSHOT ===" | tee -a $INCIDENT_LOG
uptime | tee -a $INCIDENT_LOG
free -h | tee -a $INCIDENT_LOG
df -h | tee -a $INCIDENT_LOG
ps aux --sort=-%cpu | head -20 | tee -a $INCIDENT_LOG

# 2. Network status
echo "=== NETWORK STATUS ===" | tee -a $INCIDENT_LOG
ss -tuln | tee -a $INCIDENT_LOG
ip route show | tee -a $INCIDENT_LOG

# 3. Service status
echo "=== SERVICE STATUS ===" | tee -a $INCIDENT_LOG
systemctl --failed | tee -a $INCIDENT_LOG

# 4. Recent logs
echo "=== RECENT LOGS ===" | tee -a $INCIDENT_LOG
journalctl --since "1 hour ago" --no-pager | tail -50 | tee -a $INCIDENT_LOG

echo "End Time: $(date)" | tee -a $INCIDENT_LOG
echo "Incident log saved to: $INCIDENT_LOG"
```

### Root Cause Analysis

#### Systematic Troubleshooting Approach
```
1. Problem Identification
   ├── What is the exact problem?
   ├── When did it start?
   ├── What systems are affected?
   └── What is the business impact?

2. Information Gathering
   ├── System logs analysis
   ├── Performance metrics review
   ├── Recent changes identification
   └── User reports collection

3. Hypothesis Formation
   ├── Based on symptoms
   ├── Based on recent changes
   ├── Based on historical patterns
   └── Based on system knowledge

4. Testing và Validation
   ├── Test each hypothesis
   ├── Gather evidence
   ├── Isolate variables
   └── Document findings

5. Solution Implementation
   ├── Plan the fix
   ├── Test in staging (if possible)
   ├── Implement fix
   └── Monitor results

6. Documentation và Follow-up
   ├── Document root cause
   ├── Document solution
   ├── Update procedures
   └── Prevent recurrence
```

## 💡 Best Practices cho Viettel IDC

### 1. Proactive Monitoring
- Set up comprehensive monitoring dashboards
- Implement predictive alerting
- Regular performance baseline reviews
- Automated health checks
- Capacity planning based on trends

### 2. Documentation Standards
- Maintain runbooks for common issues
- Document all troubleshooting procedures
- Keep system configuration documentation current
- Create incident response playbooks
- Regular procedure reviews và updates

### 3. Performance Optimization
- Regular performance tuning
- Resource usage optimization
- Bottleneck identification và resolution
- System maintenance scheduling
- Preventive maintenance procedures

### 4. Incident Management
- Clear escalation procedures
- Rapid response protocols
- Communication plans
- Post-incident reviews
- Continuous improvement processes

---
*Effective monitoring and troubleshooting are critical skills for maintaining 24/7 operations at Viettel IDC. Proactive monitoring prevents issues, while systematic troubleshooting resolves them quickly.*
