# Linux System Fundamentals - Cơ bản về Hệ thống Linux

## 🎯 Mục tiêu Học tập
Hiểu sâu về kiến trúc Linux, filesystem, process management và networking để làm nền tảng cho công việc System Administrator tại Viettel IDC.

## 📚 1. Linux Architecture - Kiến trúc Linux

### Lý thuyết về Kiến trúc Hệ điều hành Linux

Linux được thiết kế theo kiến trúc phân lớp (layered architecture) nhằm tách biệt rõ ràng giữa các thành phần hệ thống, đảm bảo tính bảo mật, ổn định và hiệu suất. Kiến trúc này dựa trên nguyên lý **separation of concerns** và **privilege separation**.

### Kernel Space vs User Space

```
┌─────────────────────────────────────┐
│           User Space                │  ← Ring 3 (Unprivileged)
│  Applications │ Shell │ Libraries   │
├─────────────────────────────────────┤
│              Kernel Space           │  ← Ring 0 (Privileged)
│  System Calls │ Kernel │ Drivers    │
├─────────────────────────────────────┤
│              Hardware               │  ← Physical Layer
│     CPU │ Memory │ Storage │ Network │
└─────────────────────────────────────┘
```

#### Lý thuyết về Protection Rings

Linux sử dụng **CPU Protection Rings** để tạo ra các mức độ quyền hạn khác nhau:

- **Ring 0 (Kernel Mode)**: Có quyền truy cập trực tiếp vào hardware, thực thi các instruction đặc quyền
- **Ring 3 (User Mode)**: Bị hạn chế quyền truy cập, không thể thực thi instruction đặc quyền trực tiếp

**Lợi ích của việc phân chia này:**
1. **Security**: Ngăn chặn user applications làm hỏng hệ thống
2. **Stability**: Lỗi trong user space không crash toàn bộ hệ thống  
3. **Isolation**: Các process được cô lập với nhau
4. **Resource Management**: Kernel kiểm soát việc phân bổ tài nguyên

#### User Space - Không gian Người dùng

**Định nghĩa**: User Space là vùng nhớ và execution context nơi các ứng dụng người dùng chạy, bị hạn chế quyền truy cập trực tiếp vào hardware.

**Thành phần chính:**

1. **Applications**: 
   - Web servers (nginx, httpd): Xử lý HTTP requests
   - Database servers (mysql, postgresql): Quản lý dữ liệu
   - Application servers (java, python apps): Logic nghiệp vụ

2. **Shell**: 
   - Command interpreter (bash, zsh, fish)
   - Cung cấp interface giữa user và kernel
   - Script execution environment

3. **Libraries**: 
   - **glibc**: GNU C Library - cung cấp system call wrappers
   - **systemd libraries**: Quản lý services và system initialization
   - **Shared libraries**: Code được chia sẻ giữa các applications

4. **Utilities**: 
   - **Text processing**: grep, awk, sed - xử lý văn bản
   - **File operations**: find, locate - tìm kiếm files
   - **System info**: ps, top, df - monitoring hệ thống

#### Kernel Space - Không gian Kernel

**Định nghĩa**: Kernel Space là vùng nhớ được bảo vệ nơi kernel và device drivers chạy với đầy đủ quyền hạn hardware.

**Thành phần chính:**

1. **Process Management**:
   - **Scheduler**: Quyết định process nào được CPU execution time
   - **Process Creation**: fork(), exec() system calls
   - **Context Switching**: Chuyển đổi giữa các processes
   - **Inter-Process Communication (IPC)**: Pipes, shared memory, semaphores

2. **Memory Management**:
   - **Virtual Memory**: Tạo illusion về unlimited memory
   - **Paging**: Chia memory thành các pages cố định
   - **Memory Mapping**: Map files vào memory space
   - **Memory Protection**: Ngăn processes truy cập memory của nhau

3. **File System**:
   - **Virtual File System (VFS)**: Abstraction layer cho các filesystem types
   - **File System Drivers**: ext4, xfs, btrfs implementations
   - **Buffer Cache**: Cache frequently accessed disk blocks
   - **Directory Operations**: File creation, deletion, searching

4. **Network Stack**:
   - **TCP/IP Implementation**: Protocol stack implementation
   - **Socket Interface**: Communication endpoints cho applications
   - **Routing**: Packet forwarding decisions
   - **Firewall**: netfilter framework cho packet filtering

5. **Device Drivers**:
   - **Block Devices**: Hard drives, SSDs - data storage
   - **Character Devices**: Keyboards, mice - character streams  
   - **Network Devices**: Ethernet cards, WiFi adapters
   - **Hardware Abstraction**: Uniform interface cho diverse hardware

### Lý thuyết về Linux Boot Process

Boot process là chuỗi các bước được thực hiện tuần tự để đưa hệ thống từ trạng thái tắt đến trạng thái sẵn sàng phục vụ users. Hiểu rõ boot process giúp troubleshoot các vấn đề khởi động và tối ưu hóa thời gian boot.

### Linux Boot Process
```
1. BIOS/UEFI → 2. Bootloader (GRUB) → 3. Kernel → 4. Init (systemd) → 5. Services
```

**Mỗi giai đoạn có vai trò và mục đích riêng biệt:**

#### 1. BIOS/UEFI Phase - Power-On Self Test

**Basic Input/Output System (BIOS)**:
- **Firmware** cổ điển được lưu trữ trong ROM/Flash memory
- **Power-On Self Test (POST)**: Kiểm tra hardware cơ bản (CPU, RAM, storage)
- **Master Boot Record (MBR)**: Đọc sector đầu tiên (512 bytes) của boot device
- **Limitations**: 
  - Chỉ hỗ trợ disks ≤ 2TB
  - Partition table tối đa 4 primary partitions
  - 16-bit mode, addressing limitations

**Unified Extensible Firmware Interface (UEFI)**:
- **Modern replacement** cho BIOS với nhiều tính năng advanced
- **GPT (GUID Partition Table)**: Hỗ trợ disks lớn hơn, nhiều partitions hơn
- **Secure Boot**: Xác thực digital signatures của bootloaders và OS
- **EFI System Partition (ESP)**: FAT32 partition chứa bootloaders
- **Boot Manager**: Interface để chọn OS khi dual-boot

```bash
# Kiểm tra boot mode
[ -d /sys/firmware/efi ] && echo "UEFI" || echo "BIOS"

# Xem boot order (UEFI systems)
efibootmgr -v  
```

#### 2. GRUB Bootloader - Grand Unified Bootloader

**Vai trò của GRUB**:
- **Stage 1**: Code nhỏ trong MBR/ESP để load Stage 2
- **Stage 2**: Full bootloader với filesystem support và user interface
- **Configuration**: `/boot/grub2/grub.cfg` chứa menu entries và boot options
- **Multi-boot**: Có thể boot multiple operating systems

**GRUB Menu và Kernel Parameters**:
- **Kernel Selection**: Cho phép chọn kernel version khác nhau
- **Boot Parameters**: Truyền arguments cho kernel (như debug mode, recovery mode)
- **Recovery Options**: Single user mode, rescue mode
- **Memory Testing**: Memtest86+ integration

```bash
# GRUB configuration
cat /boot/grub2/grub.cfg

# Kernel parameters hiện tại
cat /proc/cmdline

# Update GRUB after configuration changes
grub2-mkconfig -o /boot/grub2/grub.cfg
```

#### 3. Kernel Initialization - Core System Startup

**Kernel Loading Process**:
1. **Decompression**: Kernel thường được nén để tiết kiệm space
2. **Memory Setup**: Initialize memory management subsystem
3. **Hardware Detection**: Probe và initialize hardware components
4. **Device Driver Loading**: Load essential drivers cho storage, network
5. **Root Filesystem Mount**: Mount root partition để access system files

**Key Kernel Subsystems Initialization**:
- **Memory Management**: Virtual memory, page tables, memory allocators
- **Process Scheduler**: CFS (Completely Fair Scheduler) initialization
- **Interrupt Handlers**: Setup hardware interrupt handling
- **System Call Interface**: Enable user-kernel communication

**initramfs (Initial RAM Filesystem)**:
- **Temporary root filesystem** trong RAM
- **Essential drivers và tools** cần thiết để mount real root filesystem
- **Module loading**: Load kernel modules cho specific hardware
- **Transition**: Switch từ initramfs sang real root filesystem

#### 4. Init System (systemd) - Service Manager

**systemd Architecture**:
- **PID 1**: First user-space process, parent của tất cả processes
- **Dependency Management**: Services được start theo dependency order
- **Parallel Startup**: Multiple services có thể start simultaneously
- **Target System**: Replacement cho traditional runlevels

**systemd Units**:
- **Service Units** (.service): Individual services như web server, database
- **Target Units** (.target): Grouping của multiple units (như runlevels)
- **Mount Units** (.mount): Filesystem mounts
- **Timer Units** (.timer): Scheduled tasks (replacement cho cron)

```bash
# Systemd units
systemctl list-units --type=service

# Boot targets (replacement for runlevels)
systemctl get-default
systemctl list-units --type=target

# Service dependencies
systemctl list-dependencies multi-user.target
```

**Boot Targets**:
- **rescue.target**: Single user mode, minimal services
- **multi-user.target**: Multi-user mode without GUI
- **graphical.target**: Multi-user mode với GUI
- **reboot.target**: System reboot
- **poweroff.target**: System shutdown

#### 5. Services Startup - Application Layer

**Service Startup Order**:
1. **Essential Services**: networking, logging, time synchronization
2. **Infrastructure Services**: databases, web servers, monitoring
3. **Application Services**: business applications, user services
4. **User Sessions**: Desktop environments, user-specific services

**Service Dependencies**:
- **Wants**: Soft dependency - service vẫn start nếu dependency fails
- **Requires**: Hard dependency - service không start nếu dependency fails
- **After/Before**: Ordering dependencies - không implicitly create dependencies
- **Conflicts**: Services không thể chạy cùng lúc

## 📁 2. File System Management

### Lý thuyết về File System

File System là **phương pháp tổ chức và lưu trữ dữ liệu** trên storage devices, cung cấp **abstraction layer** giữa applications và physical storage. Nó định nghĩa cách data được **structured, named, và accessed**.

### File System Hierarchy Standard (FHS) - Lý thuyết về Tổ chức Thư mục

**FHS** là standard định nghĩa **directory structure và directory contents** trong Unix-like operating systems. Mục đích là đảm bảo **consistency và predictability** across different Linux distributions.

**Nguyên tắc thiết kế FHS:**

1. **Separation of Concerns**: Mỗi directory có mục đích cụ thể
2. **Shareable vs Non-shareable**: Phân biệt data có thể share qua network và không thể
3. **Static vs Variable**: Phân biệt data không thay đổi và thay đổi thường xuyên
4. **Hierarchy**: Tree structure với root (/) là điểm bắt đầu

```
/                    # Root directory - điểm mount của toàn bộ filesystem
├── bin/            # Essential command binaries - commands cần thiết cho system boot
├── boot/           # Boot loader files, kernels - static files cho boot process
├── dev/            # Device files - device nodes cho hardware access
├── etc/            # Configuration files - system-wide configuration files
├── home/           # User home directories - personal data storage
├── lib/            # Essential shared libraries - libraries cần thiết cho /bin và /sbin
├── media/          # Removable media mount points - CD, USB drives
├── mnt/            # Temporary mount points - manual mounts
├── opt/            # Optional application software - third-party software
├── proc/           # Virtual filesystem (process info) - kernel data structures
├── root/           # Root user home directory - superuser's home
├── sbin/           # Essential system binaries - system administration commands
├── srv/            # Service data - data for services provided by system
├── sys/            # Virtual filesystem (kernel objects) - kernel subsystem info
├── tmp/            # Temporary files - temporary storage, cleared on reboot
├── usr/            # Secondary hierarchy - user programs và data
├── var/            # Variable data files - logs, spools, temporary files
└── run/            # Runtime data - volatile runtime data
```

**Chi tiết về các directory quan trọng:**

#### /etc - System Configuration
- **Purpose**: Chứa **configuration files** cho toàn bộ system
- **Characteristics**: Text-based files, readable bởi administrators
- **Examples**: `/etc/passwd` (user accounts), `/etc/fstab` (filesystem table)
- **Security**: Chỉ root có write access, users có read access

#### /var - Variable Data  
- **Purpose**: Chứa data **thay đổi thường xuyên** during normal operation
- **Subdirectories**:
  - `/var/log`: System logs và application logs
  - `/var/spool`: Print queues, mail queues, cron jobs
  - `/var/tmp`: Temporary files preserved between reboots
  - `/var/lib`: Variable state information for applications

#### /usr - User Programs
- **Purpose**: **Secondary hierarchy** chứa majority của user utilities và applications
- **Read-only**: Có thể được mounted read-only và shared across multiple systems
- **Subdirectories**:
  - `/usr/bin`: Non-essential command binaries
  - `/usr/lib`: Libraries cho /usr/bin và /usr/sbin
  - `/usr/local`: Local software installations
  - `/usr/share`: Architecture-independent shared data

#### /proc và /sys - Virtual Filesystems
- **Đặc điểm**: Không tồn tại trên disk, được kernel tạo ra trong memory
- **/proc**: Interface để access **process information và kernel parameters**
- **/sys**: Modern interface để access **kernel objects và hardware information**
- **Use cases**: System monitoring, configuration, debugging

### Lý thuyết về File System Types

#### ext4 (Fourth Extended Filesystem) - Lý thuyết

**Kiến trúc ext4:**

**Journaling Filesystem**:
- **Journal**: Metadata changes được log trước khi commit to main filesystem
- **Crash Recovery**: Sau crash, filesystem có thể được restored quickly bằng cách replay journal
- **ACID Properties**: Atomicity, Consistency, Isolation, Durability cho filesystem operations

**Extents-based Allocation**:
- **Traditional block mapping**: Mỗi file block được map individually (inefficient)
- **Extents**: Continuous range của blocks được describe bởi một single entry
- **Benefits**: Reduced metadata overhead, better performance cho large files, less fragmentation

**Technical Specifications**:
- **Max file size**: 16TB (với 4KB block size)
- **Max filesystem size**: 1 Exabyte
- **Max files per directory**: Unlimited (practical limit ~10 million)
- **Block sizes**: 1KB, 2KB, 4KB

```bash
# Tạo ext4 filesystem
mkfs.ext4 /dev/sdb1

# Mount với optimization options
mount -t ext4 -o defaults,noatime /dev/sdb1 /mnt/data

# Tune filesystem parameters
tune2fs -l /dev/sdb1  # View parameters
tune2fs -m 2 /dev/sdb1  # Set reserved space to 2%

# Check filesystem integrity
fsck.ext4 /dev/sdb1
```

**ext4 Features:**
- **Backward Compatibility**: Có thể mount ext2/ext3 filesystems as ext4
- **Online Defragmentation**: `e4defrag` tool để reduce fragmentation
- **Persistent Preallocation**: Preallocate space cho files để improve performance
- **Delayed Allocation**: Delay block allocation until data is actually written

#### XFS (High-performance filesystem) - Lý thuyết

**XFS Design Philosophy**:
- **Scalability**: Designed cho **high-performance, large-scale systems**
- **Parallel Operations**: Multiple threads có thể operate on filesystem simultaneously
- **B+ Tree Structures**: Efficient indexing cho directories và free space management

**Architecture Components**:
- **Allocation Groups (AGs)**: Filesystem được chia thành AGs để enable parallel operations
- **Real-time Subvolume**: Separate area cho real-time files với predictable access patterns
- **Log Subvolume**: Separate area cho metadata journal

**Advanced Features**:
- **Online Resizing**: Có thể grow filesystem while mounted (không thể shrink)
- **Quotas**: User và group quotas với project quota support
- **Snapshots**: Copy-on-write snapshots (LVM level)
- **Direct I/O**: Bypass page cache cho certain applications

```bash
# Tạo XFS filesystem
mkfs.xfs /dev/sdb1

# Mount với performance options
mount -t xfs -o defaults,noatime,inode64 /dev/sdb1 /mnt/data

# XFS-specific utilities
xfs_info /dev/sdb1      # Filesystem information
xfs_growfs /mnt/data    # Resize filesystem online
xfs_repair /dev/sdb1    # Repair filesystem (must be unmounted)
```

#### LVM (Logical Volume Management) - Lý thuyết

**LVM Abstraction Layers**:

**Physical Volumes (PV)**:
- **Hardware abstraction**: Physical disks, partitions, hoặc RAID arrays
- **Metadata**: LVM metadata được stored ở beginning của each PV
- **Extensibility**: Có thể add/remove PVs from volume groups

**Volume Groups (VG)**:
- **Storage Pool**: Collection của Physical Volumes
- **Unified Namespace**: Present multiple PVs as single storage pool
- **Flexibility**: Có thể span across multiple physical devices

**Logical Volumes (LV)**:
- **Virtual Partitions**: Logical divisions của Volume Group space
- **Dynamic Sizing**: Có thể resize without unmounting filesystem
- **Abstraction**: Applications see LVs as regular block devices

```bash
# LVM Architecture Implementation
Physical Volumes (PV) → Volume Groups (VG) → Logical Volumes (LV)

# Create Physical Volume
pvcreate /dev/sdb1 /dev/sdc1

# Create Volume Group
vgcreate vg_data /dev/sdb1 /dev/sdc1

# Create Logical Volume
lvcreate -L 10G -n lv_web vg_data

# Extend Logical Volume
lvextend -L +5G /dev/vg_data/lv_web
resize2fs /dev/vg_data/lv_web  # For ext4 filesystem

# LVM Snapshot mechanism
lvcreate -L 2G -s -n lv_web_snapshot /dev/vg_data/lv_web
```

**LVM Advanced Features**:

**Snapshots**:
- **Copy-on-Write**: Original data remains until overwritten
- **Point-in-time**: Consistent state của filesystem tại specific moment
- **Backup Strategy**: Create snapshot, backup from snapshot, remove snapshot

**Thin Provisioning**:
- **Over-allocation**: Logical volumes có thể be larger than available physical space
- **Space Efficiency**: Physical space chỉ allocated when actually used
- **Monitoring**: Cần monitor space usage để avoid out-of-space conditions

**RAID Integration**:
- **Software RAID**: LVM có thể implement RAID levels (0, 1, 5, 6, 10)
- **Performance**: Better performance than traditional software RAID in some cases
- **Flexibility**: Combine RAID với LVM features như snapshots và resizing

### Lý thuyết về File Permissions và Security Model

Linux security model dựa trên **Discretionary Access Control (DAC)**, nơi **owners của objects** (files, directories) có quyền quyết định ai có thể access objects đó.

#### Standard Permissions - Lý thuyết

**Permission Model Structure**:
```
File Type | Owner Permissions | Group Permissions | Other Permissions
    d     |      rwx          |       r-x         |       r-x
```

**Permission Types**:

1. **Read (r)**:
   - **Files**: Có thể đọc content của file
   - **Directories**: Có thể list directory contents (ls command)
   - **Bit value**: 4

2. **Write (w)**:
   - **Files**: Có thể modify file content
   - **Directories**: Có thể create, delete, rename files trong directory
   - **Bit value**: 2

3. **Execute (x)**:
   - **Files**: Có thể execute file as program
   - **Directories**: Có thể traverse directory (cd command)
   - **Bit value**: 1

**Permission Categories**:

1. **Owner (User)**: User who owns the file
2. **Group**: Users belonging to file's group
3. **Others**: All other users on system

**Octal Representation**:
- **Numeric system**: Base-8 representation of binary permissions
- **Calculation**: r(4) + w(2) + x(1) = permission value
- **Examples**: 
  - 755 = rwxr-xr-x (owner: full, group: read+execute, others: read+execute)
  - 644 = rw-r--r-- (owner: read+write, group: read, others: read)
  - 600 = rw------- (owner: read+write, group: none, others: none)

```bash
# Numeric permissions
chmod 755 file.txt    # rwxr-xr-x
chmod 644 file.txt    # rw-r--r--
chmod 600 file.txt    # rw-------

# Symbolic permissions
chmod u+x file.txt    # Add execute for owner
chmod g-w file.txt    # Remove write for group
chmod o=r file.txt    # Set only read for others

# Ownership changes
chown user:group file.txt
chown -R user:group directory/
```

#### Special Permissions - Advanced Security Features

**1. SUID (Set User ID) - Permission bit 4000**:

**Lý thuyết**: Khi SUID bit được set trên executable file, program sẽ **run with permissions của file owner** thay vì user đang execute.

**Use Cases**:
- **passwd command**: Users cần modify `/etc/shadow` file (chỉ root có write access)
- **sudo command**: Temporary privilege escalation
- **ping command**: Cần raw socket access (root privilege)

**Security Implications**:
- **Privilege Escalation**: Potential security risk nếu SUID programs có vulnerabilities
- **Audit Requirements**: Regular audit của SUID files trong system

```bash
# Set SUID bit
chmod u+s /usr/bin/passwd
ls -l /usr/bin/passwd  # -rwsr-xr-x (s indicates SUID)

# Find all SUID files (security audit)
find / -type f -perm -4000 2>/dev/null
```

**2. SGID (Set Group ID) - Permission bit 2000**:

**On Files**: Program runs với permissions của file's group
**On Directories**: Files created trong directory inherit directory's group ownership

**Use Cases**:
- **Shared project directories**: All files created có same group ownership
- **Collaboration**: Team members có thể access files created by others trong team

```bash
# Set SGID on directory
chmod g+s /shared/project
ls -ld /shared/project  # drwxrws--- (s indicates SGID)

# Files created trong directory inherit group
touch /shared/project/newfile
ls -l /shared/project/newfile  # Sẽ có same group như directory
```

**3. Sticky Bit - Permission bit 1000**:

**Lý thuyết**: Trên directories, sticky bit **prevents file deletion** by users khác owner, even if they have write permission trên directory.

**Classic Use Case**: `/tmp` directory
- **Shared temporary space**: All users có thể create files
- **Protection**: Users không thể delete files của other users
- **System security**: Prevents malicious deletion of temporary files

```bash
# Set sticky bit
chmod +t /tmp
ls -ld /tmp  # drwxrwxrwt (t indicates sticky bit)

# Create test scenario
mkdir /shared/temp
chmod 1777 /shared/temp  # Full permissions + sticky bit
```

### File Permissions Security Best Practices

**Principle of Least Privilege**:
- **Minimum necessary permissions**: Chỉ grant permissions cần thiết cho functionality
- **Regular audits**: Periodic review của file permissions
- **Default secure**: Start with restrictive permissions, add as needed

**Common Security Configurations**:

1. **System Files**: 
   - Configuration files: 644 (readable by all, writable by root)
   - Executables: 755 (executable by all, writable by root)
   - Sensitive configs: 600 (only root access)

2. **User Files**:
   - Personal files: 600 or 644
   - Personal executables: 700 or 755
   - Private directories: 700

3. **Shared Resources**:
   - Shared directories: 2775 (SGID + group write)
   - Shared files: 664 (group readable/writable)

**umask - Default Permission Mask**:
- **Purpose**: Defines **default permissions** cho newly created files và directories
- **Calculation**: Final permissions = Maximum permissions - umask
- **Common values**:
  - umask 022: Files 644, directories 755
  - umask 027: Files 640, directories 750 (more restrictive)

## 🔧 3. Process Management

### Lý thuyết về Process Management

**Process** là instance của **executing program**, bao gồm program code, current activity, và system resources được allocated. Process management là core function của operating system kernel.

### Process Lifecycle và State Management

#### Process States - Lý thuyết về Trạng thái Process

Linux processes có thể ở trong một trong các states sau, với transitions được controlled bởi kernel scheduler:

```
┌─────────────┐    fork()    ┌─────────────┐
│   RUNNING   │ ──────────→  │    READY    │
│    (R)      │              │    (R)      │  
└─────────────┘              └─────────────┘
       │                            │
       │ I/O wait                   │ scheduled
       ▼                            ▼
┌─────────────┐              ┌─────────────┐
│UNINTERRUPT. │              │   ZOMBIE    │
│ SLEEP (D)   │              │    (Z)      │
└─────────────┘              └─────────────┘
       │
       │ signal/interrupt
       ▼
┌─────────────┐
│INTERRUPTIBLE│
│ SLEEP (S)   │
└─────────────┘
```

**Chi tiết về Process States:**

1. **RUNNING (R)**:
   - Process đang **actively executing** trên CPU
   - Process đang trong **run queue** chờ được scheduled
   - Có thể switch giữa actual execution và ready-to-run

2. **INTERRUPTIBLE SLEEP (S)**:
   - Process đang **waiting for event** (I/O completion, signal)
   - Có thể bị **interrupted by signals**
   - Most common sleeping state
   - Examples: waiting for user input, network response, file read

3. **UNINTERRUPTIBLE SLEEP (D)**:
   - Process đang waiting for **critical system operation**
   - **Cannot be interrupted** by signals (kể cả SIGKILL)
   - Usually short-lived state
   - Examples: waiting for hardware I/O, critical kernel operations
   - **High D state processes** có thể indicate I/O problems

4. **ZOMBIE (Z)**:
   - Process đã **terminated** nhưng entry vẫn tồn tại trong process table
   - Parent process chưa **read exit status** (chưa call wait())
   - **No resources** consumed except process table entry
   - **Zombie accumulation** có thể exhaust process table

5. **STOPPED (T)**:
   - Process bị **suspended** bởi signal (SIGSTOP, SIGTSTP)
   - Can be **resumed** with SIGCONT
   - Used by job control (Ctrl+Z in shell)

### Process Creation và Management

#### Process Creation Theory

**fork() System Call**:
- **Creates identical copy** của calling process
- **Copy-on-Write (COW)**: Memory pages shared until modification
- **Return values**: 
  - Child process: returns 0
  - Parent process: returns child PID
  - Error: returns -1

**exec() Family**:
- **Replaces current process image** với new program
- **Preserves PID** nhưng replaces memory contents
- **Environment inheritance**: Environment variables passed to new program

**Process Hierarchy**:
- **Parent-Child relationship**: Every process có parent (except init)
- **Process Group**: Collection của related processes
- **Session**: Collection của process groups
- **Process tree**: Hierarchical structure từ init process

#### Process Scheduling Theory

**Completely Fair Scheduler (CFS)**:
- **Default scheduler** cho normal processes trong Linux
- **Virtual runtime**: Tracks CPU time used by each process
- **Red-black tree**: Efficient data structure cho process selection
- **Fairness**: Aims to give equal CPU time to all processes

**Scheduling Policies**:

1. **SCHED_NORMAL (CFS)**:
   - Default policy cho user processes
   - **Time-sharing** với dynamic priorities
   - **Nice values**: -20 (highest priority) to +19 (lowest priority)

2. **SCHED_FIFO (Real-time)**:
   - **First-In-First-Out** real-time scheduling
   - Process runs until completion hoặc voluntary yield
   - **Higher priority** than normal processes

3. **SCHED_RR (Round-Robin)**:
   - **Time-sliced** real-time scheduling
   - Each process gets time quantum
   - **Preemptive** among same priority processes

**Process Priority và Nice Values**:
- **Nice value**: User-space priority hint to scheduler
- **Range**: -20 (highest priority) to +19 (lowest priority)
- **Default**: 0 cho new processes
- **Calculation**: Lower nice value = higher priority = more CPU time

```bash
# Process monitoring commands
ps aux                    # All processes with resource usage
ps -ef                    # Full format with parent-child relationships
ps -eo pid,ppid,cmd,%mem,%cpu --sort=-%cpu  # Custom format sorted by CPU

# Dynamic monitoring
top                       # Real-time process viewer
htop                      # Enhanced top with better interface
iotop                     # I/O monitoring by process
atop                      # Advanced system & process monitor

# Process tree visualization
pstree                    # ASCII process tree
pstree -p                 # With PIDs shown

# Memory analysis
free -h                   # System memory usage
vmstat 1                  # Virtual memory statistics
cat /proc/meminfo         # Detailed memory information

# CPU analysis
mpstat 1                  # Multi-processor statistics
sar -u 1 10              # CPU utilization over time
cat /proc/loadavg        # Load average values
```

### Process Control và Signal Management

#### Signal Theory

**Signals** là **software interrupts** được delivered đến processes để notify về events hoặc request actions. Signals provide **asynchronous communication** mechanism.

**Signal Categories**:

1. **Termination Signals**:
   - **SIGTERM (15)**: Polite termination request, can be caught/ignored
   - **SIGKILL (9)**: Immediate termination, cannot be caught/blocked
   - **SIGQUIT (3)**: Quit with core dump

2. **Job Control Signals**:
   - **SIGSTOP (19)**: Stop process execution (cannot be caught)
   - **SIGTSTP (20)**: Terminal stop (Ctrl+Z)
   - **SIGCONT (18)**: Continue stopped process

3. **Error Signals**:
   - **SIGSEGV (11)**: Segmentation violation (memory access error)
   - **SIGBUS (7)**: Bus error (hardware fault)
   - **SIGFPE (8)**: Floating point exception

**Signal Handling**:
- **Default Action**: Each signal có default behavior (terminate, ignore, stop, core dump)
- **Custom Handlers**: Processes có thể install custom signal handlers
- **Signal Mask**: Processes có thể block specific signals temporarily

```bash
# Process control commands
command &                 # Run in background
jobs                      # List active jobs
fg %1                     # Bring job 1 to foreground
bg %1                     # Send job 1 to background

# Signal sending
kill -l                   # List all available signals
kill -TERM pid           # Send termination signal (graceful)
kill -KILL pid           # Force immediate termination
killall process_name     # Kill all processes by name
pkill -f pattern         # Kill processes matching pattern

# Process priority control
nice -n 10 command       # Start with lower priority (+10)
renice 5 -p pid          # Change priority of running process
```

### systemd Service Management Theory

#### systemd Architecture

**systemd** là **init system và service manager** cho modern Linux distributions, thay thế traditional SysV init.

**Key Concepts**:

1. **Units**: Basic building blocks của systemd
   - **.service**: Service units (daemons, applications)
   - **.target**: Grouping units (like runlevels)
   - **.mount**: Filesystem mounts
   - **.timer**: Scheduled tasks
   - **.socket**: Socket-based activation

2. **Dependencies**: 
   - **Wants**: Soft dependency (preferred but not required)
   - **Requires**: Hard dependency (must be satisfied)
   - **After/Before**: Ordering dependencies
   - **Conflicts**: Mutually exclusive units

3. **Activation Types**:
   - **Socket activation**: Services started on-demand when socket accessed
   - **Bus activation**: Services started when D-Bus request received
   - **Timer activation**: Services started on schedule
   - **Path activation**: Services started when filesystem path changes

**Service Lifecycle**:
1. **inactive**: Service not running
2. **activating**: Service starting up
3. **active**: Service running normally
4. **deactivating**: Service shutting down
5. **failed**: Service failed to start or crashed

```bash
# Service management
systemctl start service_name     # Start service immediately
systemctl stop service_name      # Stop service immediately
systemctl restart service_name   # Stop then start service
systemctl reload service_name    # Reload configuration without restart
systemctl enable service_name    # Enable service to start at boot
systemctl disable service_name   # Disable service from starting at boot

# Service status và information
systemctl status service_name    # Detailed service status
systemctl is-active service_name # Check if service is running
systemctl is-enabled service_name # Check if service enabled for boot

# Service listing và discovery
systemctl list-units --type=service        # List all service units
systemctl list-unit-files --type=service   # List all service unit files
systemctl list-dependencies service_name   # Show service dependencies

# Logging và debugging
journalctl -u service_name                  # Show service logs
journalctl -f -u service_name              # Follow service logs real-time
journalctl --since "1 hour ago"            # Logs from last hour
journalctl --until "2022-01-01"           # Logs until specific date
```

**systemd Targets (Runlevels Replacement)**:
- **rescue.target**: Single-user mode, minimal services
- **multi-user.target**: Multi-user mode without GUI
- **graphical.target**: Multi-user mode with GUI
- **reboot.target**: System reboot
- **poweroff.target**: System shutdown

## 🌐 4. Network Configuration

### Network Interface Management
```bash
# Legacy tools (still widely used)
ifconfig                  # Show interfaces
ifconfig eth0 up         # Bring interface up
ifconfig eth0 192.168.1.100 netmask 255.255.255.0

# Modern tools (iproute2)
ip addr show             # Show IP addresses
ip addr add 192.168.1.100/24 dev eth0
ip addr del 192.168.1.100/24 dev eth0

ip link show             # Show interfaces
ip link set eth0 up      # Bring interface up
ip link set eth0 down    # Bring interface down

# Routing
ip route show            # Show routing table
ip route add default via 192.168.1.1
ip route add 10.0.0.0/8 via 192.168.1.1
```

### Network Configuration Files

#### Red Hat/CentOS (NetworkManager)
```bash
# Interface configuration
cat /etc/sysconfig/network-scripts/ifcfg-eth0
```
```
TYPE=Ethernet
PROXY_METHOD=none
BROWSER_ONLY=no
BOOTPROTO=static
DEFROUTE=yes
IPV4_FAILURE_FATAL=no
IPV6INIT=yes
IPV6_AUTOCONF=yes
IPV6_DEFROUTE=yes
IPV6_FAILURE_FATAL=no
NAME=eth0
UUID=12345678-1234-1234-1234-123456789abc
DEVICE=eth0
ONBOOT=yes
IPADDR=192.168.1.100
NETMASK=255.255.255.0
GATEWAY=192.168.1.1
DNS1=8.8.8.8
DNS2=8.8.4.4
```

#### Ubuntu (Netplan)
```yaml
# /etc/netplan/01-network-manager-all.yaml
network:
  version: 2
  renderer: networkd
  ethernets:
    eth0:
      dhcp4: false
      addresses:
        - 192.168.1.100/24
      gateway4: 192.168.1.1
      nameservers:
        addresses: [8.8.8.8, 8.8.4.4]
```

### DNS Configuration
```bash
# DNS resolution files
cat /etc/resolv.conf      # DNS servers
cat /etc/hosts           # Static hostname resolution
cat /etc/nsswitch.conf   # Name service switch

# DNS testing
nslookup google.com
dig google.com
host google.com

# DNS troubleshooting
dig @8.8.8.8 google.com  # Query specific DNS server
dig +trace google.com    # Trace DNS resolution
```

### Network Troubleshooting Tools
```bash
# Connectivity testing
ping 8.8.8.8             # ICMP ping
ping6 ::1                # IPv6 ping
traceroute 8.8.8.8       # Trace route
mtr 8.8.8.8             # My traceroute (continuous)

# Port testing
telnet google.com 80     # Test TCP port
nc -zv google.com 80     # Netcat port scan
nc -l 8080              # Listen on port

# Network statistics
netstat -tuln           # Listen ports
netstat -rn             # Routing table
ss -tuln                # Modern netstat
ss -t state established # Active connections

# Traffic monitoring
tcpdump -i eth0         # Packet capture
tcpdump -i eth0 port 80 # HTTP traffic
iftop                   # Interface traffic
nethogs                 # Process network usage
```

## 🔒 5. Security Fundamentals

### SSH Configuration và Hardening
```bash
# SSH client configuration
cat ~/.ssh/config
```
```
Host server1
    HostName 192.168.1.100
    User admin
    Port 2222
    IdentityFile ~/.ssh/id_rsa_server1
    StrictHostKeyChecking yes
```

```bash
# SSH server configuration (/etc/ssh/sshd_config)
```
```
# Basic security settings
Port 2222                        # Change default port
Protocol 2                       # Use SSH protocol version 2
PermitRootLogin no              # Disable root login
PasswordAuthentication no       # Use key-based auth only
PubkeyAuthentication yes        # Enable public key auth
MaxAuthTries 3                  # Limit auth attempts
ClientAliveInterval 300         # Keep connection alive
ClientAliveCountMax 2           # Max missed heartbeats

# Allow/Deny specific users
AllowUsers admin user1 user2
DenyUsers guest
AllowGroups sudo admin
```

### Firewall Configuration

#### iptables (Traditional)
```bash
# View current rules
iptables -L -n -v

# Basic rules
iptables -A INPUT -i lo -j ACCEPT                    # Allow loopback
iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
iptables -A INPUT -p tcp --dport 22 -j ACCEPT       # Allow SSH
iptables -A INPUT -p tcp --dport 80 -j ACCEPT       # Allow HTTP
iptables -A INPUT -p tcp --dport 443 -j ACCEPT      # Allow HTTPS
iptables -A INPUT -j DROP                           # Drop everything else

# Save rules
iptables-save > /etc/iptables/rules.v4
```

#### firewalld (Modern)
```bash
# Zone management
firewall-cmd --get-default-zone
firewall-cmd --list-all-zones
firewall-cmd --set-default-zone=public

# Service management
firewall-cmd --list-services
firewall-cmd --add-service=http --permanent
firewall-cmd --add-service=https --permanent
firewall-cmd --remove-service=dhcpv6-client --permanent

# Port management
firewall-cmd --add-port=8080/tcp --permanent
firewall-cmd --list-ports

# Reload configuration
firewall-cmd --reload
```

### User Management và sudo
```bash
# User creation
useradd -m -s /bin/bash -G sudo username
passwd username

# User modification
usermod -aG group username      # Add to group
usermod -s /bin/zsh username    # Change shell
usermod -l newname oldname      # Rename user

# Group management
groupadd developers
groupdel oldgroup
gpasswd -a username groupname   # Add user to group

# sudo configuration (/etc/sudoers)
```
```
# User privilege specification
root    ALL=(ALL:ALL) ALL
admin   ALL=(ALL:ALL) ALL

# Group privileges
%sudo   ALL=(ALL:ALL) ALL
%wheel  ALL=(ALL:ALL) ALL

# Specific commands
user1   ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart apache2
user2   ALL=(ALL) /usr/bin/apt-get update, /usr/bin/apt-get upgrade

# Command aliases
Cmnd_Alias NETWORKING = /sbin/route, /sbin/ifconfig, /bin/ping
%netadmin ALL = NETWORKING
```

### SELinux (Security-Enhanced Linux)
```bash
# SELinux status
getenforce                      # Current mode
sestatus                        # Detailed status

# SELinux modes
setenforce 0                    # Set permissive (temporary)
setenforce 1                    # Set enforcing (temporary)

# Permanent mode change (/etc/selinux/config)
SELINUX=enforcing               # enforcing, permissive, disabled

# Context management
ls -Z file.txt                  # View context
chcon -t httpd_exec_t /path/to/file  # Change context
restorecon /path/to/file        # Restore default context

# Troubleshooting
sealert -a /var/log/audit/audit.log  # Analyze denials
ausearch -m AVC -ts recent      # Recent AVC denials
```

## 📈 6. Performance Monitoring

### System Resource Monitoring
```bash
# CPU monitoring
top                             # Real-time process viewer
htop                           # Enhanced top
sar -u 1 10                    # CPU utilization
mpstat 1                       # Multiprocessor statistics

# Memory monitoring
free -h                        # Memory usage
vmstat 1                       # Virtual memory statistics
sar -r 1 10                    # Memory utilization

# Disk I/O monitoring
iostat -x 1                    # Extended I/O statistics
iotop                          # I/O usage by process
sar -d 1 10                    # Disk activity

# Network monitoring
iftop                          # Network interface usage
nethogs                        # Network usage by process
sar -n DEV 1 10               # Network interface statistics
```

### Log Analysis
```bash
# System logs
journalctl                     # systemd journal
journalctl -f                  # Follow logs
journalctl -u servicename      # Service logs
journalctl --since "1 hour ago"

# Traditional logs
tail -f /var/log/messages      # System messages
tail -f /var/log/secure        # Authentication logs
tail -f /var/log/apache2/access.log  # Web server logs

# Log analysis tools
grep ERROR /var/log/messages
awk '{print $1}' /var/log/apache2/access.log | sort | uniq -c
sed -n '/ERROR/p' /var/log/application.log
```

## 💡 Practical Tips cho Viettel IDC

### 1. Automation Scripts
```bash
# System health check script
#!/bin/bash
echo "=== System Health Check ==="
echo "Date: $(date)"
echo "Uptime: $(uptime)"
echo "CPU Usage: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)"
echo "Memory Usage: $(free | grep Mem | awk '{printf "%.2f%%", $3/$2 * 100.0}')"
echo "Disk Usage: $(df -h / | awk 'NR==2{printf "%s", $5}')"
echo "Active Services: $(systemctl list-units --type=service --state=active | wc -l)"
```

### 2. Monitoring Best Practices
- Set up log rotation để tránh disk full
- Monitor critical services với systemd
- Use centralized logging (rsyslog, ELK stack)
- Set up alerting cho resource thresholds
- Regular backup của system configurations

### 3. Security Checklist
- [ ] Disable root SSH login
- [ ] Use key-based SSH authentication  
- [ ] Configure firewall rules
- [ ] Regular security updates
- [ ] Monitor failed login attempts
- [ ] Set up intrusion detection (fail2ban)
- [ ] Use strong passwords và password policies

## � 7. Package Management

### Package Management Systems

#### RPM-based Systems (Red Hat, CentOS, Fedora)
```bash
# YUM (Yellowdog Updater Modified)
yum search package_name          # Search packages
yum info package_name           # Package information
yum install package_name        # Install package
yum update package_name         # Update specific package
yum update                      # Update all packages
yum remove package_name         # Remove package
yum history                     # Transaction history
yum grouplist                   # List package groups
yum groupinstall "Development Tools"

# DNF (Dandified YUM) - Modern replacement
dnf search package_name
dnf install package_name
dnf update
dnf remove package_name
dnf autoremove                  # Remove unused dependencies
dnf clean all                   # Clean cache

# RPM (Red Hat Package Manager)
rpm -qa                         # List all installed packages
rpm -qi package_name            # Package info
rpm -ql package_name            # List package files
rpm -qf /path/to/file          # Which package owns this file
rpm -ivh package.rpm           # Install RPM package
rpm -Uvh package.rpm           # Update RPM package
rpm -e package_name            # Remove package
rpm --verify package_name      # Verify package integrity
```

#### DEB-based Systems (Debian, Ubuntu)
```bash
# APT (Advanced Package Tool)
apt update                      # Update package lists
apt upgrade                     # Upgrade all packages
apt search package_name         # Search packages
apt show package_name          # Package information
apt install package_name       # Install package
apt remove package_name        # Remove package
apt purge package_name         # Remove package and config files
apt autoremove                 # Remove unused dependencies
apt list --installed          # List installed packages
apt list --upgradable         # List upgradable packages

# DPKG (Debian Package Manager)
dpkg -l                        # List installed packages
dpkg -i package.deb           # Install DEB package
dpkg -r package_name          # Remove package
dpkg -P package_name          # Purge package
dpkg -s package_name          # Package status
dpkg -L package_name          # List package files
dpkg -S /path/to/file         # Which package owns this file
```

#### Source Compilation
```bash
# Compile from source (traditional method)
wget https://source.tar.gz
tar -xzf source.tar.gz
cd source/
./configure --prefix=/usr/local
make
sudo make install

# Dependencies for compilation
# Red Hat/CentOS
yum groupinstall "Development Tools"
yum install gcc gcc-c++ make cmake

# Ubuntu/Debian
apt install build-essential
apt install gcc g++ make cmake
```

### Repository Management

#### YUM/DNF Repositories
```bash
# Repository configuration files
ls /etc/yum.repos.d/

# Add EPEL repository
yum install epel-release
dnf install epel-release

# Custom repository configuration
cat > /etc/yum.repos.d/custom.repo << EOF
[custom]
name=Custom Repository
baseurl=http://repo.example.com/centos/7/x86_64/
enabled=1
gpgcheck=1
gpgkey=http://repo.example.com/RPM-GPG-KEY
EOF

# Repository operations
yum repolist                   # List enabled repositories
yum repolist all              # List all repositories
yum-config-manager --enable repo_name
yum-config-manager --disable repo_name
```

#### APT Repositories
```bash
# Repository sources
cat /etc/apt/sources.list
ls /etc/apt/sources.list.d/

# Add repository
add-apt-repository "deb http://archive.ubuntu.com/ubuntu focal main"
add-apt-repository ppa:user/ppa-name

# GPG keys
wget -qO - https://example.com/key.gpg | apt-key add -
curl -fsSL https://example.com/key.gpg | gpg --dearmor -o /etc/apt/trusted.gpg.d/example.gpg

# Update after adding repository
apt update
```

## 🐚 8. Shell Scripting và Automation

### Bash Scripting Fundamentals

#### Script Structure
```bash
#!/bin/bash
# Script: system_check.sh
# Description: System health check script
# Author: Admin
# Date: $(date)

# Exit on any error
set -e

# Variables
HOSTNAME=$(hostname)
DATE=$(date '+%Y-%m-%d %H:%M:%S')
LOG_FILE="/var/log/system_check.log"

# Functions
check_disk_space() {
    echo "=== Disk Space Check ==="
    df -h | grep -E '^/dev/' | awk '{
        if ($5+0 > 80) {
            print "WARNING: " $6 " is " $5 " full"
        } else {
            print "OK: " $6 " is " $5 " full"
        }
    }'
}

check_memory() {
    echo "=== Memory Check ==="
    total_mem=$(free -m | awk 'NR==2{printf "%.2f", $2/1024}')
    used_mem=$(free -m | awk 'NR==2{printf "%.2f", $3/1024}')
    mem_usage=$(free | grep Mem | awk '{printf "%.2f", $3/$2 * 100.0}')
    
    echo "Total Memory: ${total_mem}GB"
    echo "Used Memory: ${used_mem}GB"
    echo "Memory Usage: ${mem_usage}%"
    
    if (( $(echo "$mem_usage > 80" | bc -l) )); then
        echo "WARNING: High memory usage!"
    fi
}

check_services() {
    echo "=== Service Check ==="
    services=("sshd" "httpd" "mysqld" "NetworkManager")
    
    for service in "${services[@]}"; do
        if systemctl is-active --quiet "$service"; then
            echo "✓ $service is running"
        else
            echo "✗ $service is not running"
        fi
    done
}

# Main execution
main() {
    echo "System Check Report - $DATE" | tee "$LOG_FILE"
    echo "Hostname: $HOSTNAME" | tee -a "$LOG_FILE"
    echo "===========================================" | tee -a "$LOG_FILE"
    
    check_disk_space | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    
    check_memory | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    
    check_services | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    
    echo "Report saved to: $LOG_FILE"
}

# Execute main function
main "$@"
```

#### Advanced Scripting Techniques
```bash
# Error handling
trap 'echo "Error on line $LINENO"; exit 1' ERR

# Command line argument parsing
while getopts "h:u:p:" opt; do
    case $opt in
        h) hostname="$OPTARG" ;;
        u) username="$OPTARG" ;;
        p) password="$OPTARG" ;;
        \?) echo "Invalid option: -$OPTARG" >&2; exit 1 ;;
    esac
done

# Arrays
declare -a servers=("web1" "web2" "db1" "cache1")
for server in "${servers[@]}"; do
    echo "Checking $server..."
    ssh "$server" "uptime"
done

# Associative arrays (Bash 4+)
declare -A server_roles
server_roles[web1]="frontend"
server_roles[web2]="frontend"
server_roles[db1]="database"

for server in "${!server_roles[@]}"; do
    echo "$server role: ${server_roles[$server]}"
done

# File operations
while IFS= read -r line; do
    echo "Processing: $line"
done < input.txt

# Network operations
if ping -c 1 8.8.8.8 &> /dev/null; then
    echo "Internet connection available"
else
    echo "No internet connection"
fi
```

### Cron Jobs và Task Scheduling
```bash
# Crontab format
# Min Hour Day Month DayOfWeek Command
# *   *    *   *     *         /path/to/command

# Edit crontab
crontab -e                     # Edit current user's crontab
crontab -l                     # List current user's crontab
crontab -r                     # Remove current user's crontab
crontab -u username -e         # Edit another user's crontab

# Common examples
0 2 * * *    /usr/local/bin/backup.sh           # Daily at 2 AM
*/5 * * * *  /usr/local/bin/monitor.sh          # Every 5 minutes
0 0 1 * *    /usr/local/bin/monthly_report.sh   # Monthly on 1st
0 9 * * 1-5  /usr/local/bin/weekday_task.sh     # Weekdays at 9 AM

# System-wide cron
cat /etc/crontab
ls /etc/cron.d/
ls /etc/cron.daily/
ls /etc/cron.weekly/
ls /etc/cron.monthly/

# Anacron for systems that aren't always on
cat /etc/anacrontab
```

### systemd Timers (Modern Cron Alternative)
```bash
# Create timer unit file
cat > /etc/systemd/system/backup.timer << EOF
[Unit]
Description=Daily Backup Timer
Requires=backup.service

[Timer]
OnCalendar=daily
Persistent=true

[Install]
WantedBy=timers.target
EOF

# Create corresponding service file
cat > /etc/systemd/system/backup.service << EOF
[Unit]
Description=Daily Backup Service
Wants=backup.timer

[Service]
Type=oneshot
ExecStart=/usr/local/bin/backup.sh

[Install]
WantedBy=multi-user.target
EOF

# Enable and start timer
systemctl enable backup.timer
systemctl start backup.timer

# Check timer status
systemctl list-timers
systemctl status backup.timer
```

## 🔄 9. System Backup và Recovery

### Backup Strategies

#### Full System Backup với rsync
```bash
# Local backup
rsync -avHAXS --exclude='/dev' --exclude='/proc' --exclude='/sys' \
      --exclude='/tmp' --exclude='/run' --exclude='/mnt' \
      --exclude='/media' --exclude='/lost+found' \
      / /backup/full_backup/

# Remote backup
rsync -avz -e ssh /important/data/ user@backup-server:/backup/data/

# Incremental backup
rsync -avz --link-dest=/backup/previous /source/ /backup/current/

# Backup script with logging
#!/bin/bash
BACKUP_SOURCE="/home /etc /var/www"
BACKUP_DEST="/backup/$(date +%Y%m%d)"
LOG_FILE="/var/log/backup.log"

mkdir -p "$BACKUP_DEST"

for source in $BACKUP_SOURCE; do
    echo "$(date): Backing up $source" >> "$LOG_FILE"
    rsync -avz "$source" "$BACKUP_DEST/" >> "$LOG_FILE" 2>&1
    if [ $? -eq 0 ]; then
        echo "$(date): Successfully backed up $source" >> "$LOG_FILE"
    else
        echo "$(date): ERROR: Failed to backup $source" >> "$LOG_FILE"
    fi
done
```

#### Database Backup
```bash
# MySQL backup
mysqldump -u root -p --all-databases > all_databases.sql
mysqldump -u root -p database_name > database_name.sql

# Automated MySQL backup script
#!/bin/bash
DB_USER="backup_user"
DB_PASS="backup_password"
BACKUP_DIR="/backup/mysql"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p "$BACKUP_DIR"

# Get list of databases
databases=$(mysql -u"$DB_USER" -p"$DB_PASS" -e "SHOW DATABASES;" | tr -d "| " | grep -v Database)

for db in $databases; do
    if [[ "$db" != "information_schema" ]] && [[ "$db" != "performance_schema" ]] && [[ "$db" != "mysql" ]]; then
        echo "Backing up database: $db"
        mysqldump -u"$DB_USER" -p"$DB_PASS" --databases "$db" > "$BACKUP_DIR/${db}_${DATE}.sql"
        gzip "$BACKUP_DIR/${db}_${DATE}.sql"
    fi
done

# PostgreSQL backup
pg_dumpall -U postgres > all_databases.sql
pg_dump -U postgres database_name > database_name.sql
```

#### Archive và Compression
```bash
# tar archives
tar -czf backup.tar.gz /path/to/backup     # Create compressed archive
tar -cjf backup.tar.bz2 /path/to/backup    # Bzip2 compression (better ratio)
tar -cJf backup.tar.xz /path/to/backup     # xz compression (best ratio)

# Extract archives
tar -xzf backup.tar.gz                     # Extract gzip
tar -xjf backup.tar.bz2                    # Extract bzip2
tar -xJf backup.tar.xz                     # Extract xz

# List archive contents
tar -tzf backup.tar.gz                     # List gzip archive
tar -tf backup.tar                         # List uncompressed archive

# dd for disk imaging
dd if=/dev/sda of=/backup/disk_image.img bs=64K conv=noerror,sync
dd if=/backup/disk_image.img of=/dev/sdb bs=64K
```

### System Recovery

#### GRUB Recovery
```bash
# Boot from GRUB rescue prompt
grub rescue> ls                            # List partitions
grub rescue> set root=(hd0,1)             # Set root partition
grub rescue> linux /vmlinuz root=/dev/sda1
grub rescue> initrd /initrd.img
grub rescue> boot

# Reinstall GRUB
mount /dev/sda1 /mnt
mount --bind /dev /mnt/dev
mount --bind /proc /mnt/proc
mount --bind /sys /mnt/sys
chroot /mnt
grub-install /dev/sda
update-grub
exit
```

#### Single User Mode Recovery
```bash
# Boot into single user mode
# At GRUB menu, edit kernel line and add:
systemd.unit=rescue.target
# or
init=/bin/bash

# Mount filesystem read-write
mount -o remount,rw /

# Reset forgotten root password
passwd root

# Fix filesystem issues
fsck /dev/sda1
```

## 📊 10. Advanced System Administration

### System Monitoring và Alerting

#### Nagios-style Monitoring Script
```bash
#!/bin/bash
# monitoring.sh - System monitoring with alerting

# Configuration
CRITICAL_CPU=90
WARNING_CPU=80
CRITICAL_MEM=90
WARNING_MEM=80
CRITICAL_DISK=90
WARNING_DISK=80
EMAIL="admin@company.com"

# Check CPU usage
check_cpu() {
    cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
    cpu_usage=${cpu_usage%.*}  # Remove decimal
    
    if [ "$cpu_usage" -gt "$CRITICAL_CPU" ]; then
        echo "CRITICAL: CPU usage is ${cpu_usage}%"
        echo "CPU usage critical: ${cpu_usage}%" | mail -s "CPU Alert" "$EMAIL"
        return 2
    elif [ "$cpu_usage" -gt "$WARNING_CPU" ]; then
        echo "WARNING: CPU usage is ${cpu_usage}%"
        return 1
    else
        echo "OK: CPU usage is ${cpu_usage}%"
        return 0
    fi
}

# Check memory usage
check_memory() {
    mem_usage=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')
    
    if [ "$mem_usage" -gt "$CRITICAL_MEM" ]; then
        echo "CRITICAL: Memory usage is ${mem_usage}%"
        echo "Memory usage critical: ${mem_usage}%" | mail -s "Memory Alert" "$EMAIL"
        return 2
    elif [ "$mem_usage" -gt "$WARNING_MEM" ]; then
        echo "WARNING: Memory usage is ${mem_usage}%"
        return 1
    else
        echo "OK: Memory usage is ${mem_usage}%"
        return 0
    fi
}

# Check disk usage
check_disk() {
    disk_usage=$(df / | tail -1 | awk '{print $5}' | cut -d'%' -f1)
    
    if [ "$disk_usage" -gt "$CRITICAL_DISK" ]; then
        echo "CRITICAL: Disk usage is ${disk_usage}%"
        echo "Disk usage critical: ${disk_usage}%" | mail -s "Disk Alert" "$EMAIL"
        return 2
    elif [ "$disk_usage" -gt "$WARNING_DISK" ]; then
        echo "WARNING: Disk usage is ${disk_usage}%"
        return 1
    else
        echo "OK: Disk usage is ${disk_usage}%"
        return 0
    fi
}

# Main monitoring function
main() {
    echo "=== System Monitor $(date) ==="
    
    check_cpu
    check_memory
    check_disk
    
    # Check critical services
    services=("sshd" "NetworkManager" "firewalld")
    for service in "${services[@]}"; do
        if systemctl is-active --quiet "$service"; then
            echo "OK: $service is running"
        else
            echo "CRITICAL: $service is not running"
            echo "Service $service is down" | mail -s "Service Alert" "$EMAIL"
        fi
    done
}

main "$@"
```

### Log Management

#### Log Rotation Configuration
```bash
# Custom logrotate configuration
cat > /etc/logrotate.d/myapp << EOF
/var/log/myapp/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 myapp myapp
    postrotate
        systemctl reload myapp
    endscript
}
EOF

# Manual log rotation test
logrotate -d /etc/logrotate.d/myapp        # Debug mode
logrotate -f /etc/logrotate.d/myapp        # Force rotation
```

#### Centralized Logging với rsyslog
```bash
# rsyslog client configuration (/etc/rsyslog.conf)
# Forward logs to central server
*.* @@log-server.company.com:514

# rsyslog server configuration
# Accept logs from network
$ModLoad imudp
$UDPServerRun 514
$UDPServerAddress 0.0.0.0

# Store logs by hostname
$template DynamicFile,"/var/log/remote/%HOSTNAME%/%programname%.log"
*.* ?DynamicFile
```

### Performance Tuning

#### Kernel Parameter Tuning
```bash
# View current kernel parameters
sysctl -a

# Network performance tuning (/etc/sysctl.conf)
net.core.rmem_max = 16777216
net.core.wmem_max = 16777216
net.ipv4.tcp_rmem = 4096 87380 16777216
net.ipv4.tcp_wmem = 4096 65536 16777216
net.core.netdev_max_backlog = 5000
net.ipv4.tcp_congestion_control = bbr

# File system performance
vm.dirty_ratio = 15
vm.dirty_background_ratio = 5
vm.swappiness = 10

# Apply changes
sysctl -p
```

#### I/O Scheduler Optimization
```bash
# Check current I/O scheduler
cat /sys/block/sda/queue/scheduler

# Change I/O scheduler
echo deadline > /sys/block/sda/queue/scheduler
echo noop > /sys/block/sda/queue/scheduler       # For SSDs
echo cfq > /sys/block/sda/queue/scheduler        # For HDDs

# Permanent change (/etc/default/grub)
GRUB_CMDLINE_LINUX="elevator=deadline"
grub2-mkconfig -o /boot/grub2/grub.cfg
```

## �📝 Exercises cho Module 1
1. **Lab 1**: Install và configure CentOS/Ubuntu server
2. **Lab 2**: Set up SSH key authentication và hardening
3. **Lab 3**: Configure static networking và DNS
4. **Lab 4**: Create custom systemd service
5. **Lab 5**: Implement log rotation và monitoring
6. **Lab 6**: Set up firewall rules và security policies
7. **Lab 7**: Write backup automation scripts
8. **Lab 8**: Configure package repositories và software installation
9. **Lab 9**: Create comprehensive monitoring solution
10. **Lab 10**: Implement system performance tuning

## 🎯 Real-world Scenarios cho Viettel IDC

### Scenario 1: High Load Investigation
```bash
# When server is experiencing high load
top -c                          # Check processes
iotop                          # Check I/O
netstat -tuln | grep LISTEN   # Check listening ports
ps aux --sort=-%cpu            # Sort by CPU usage
ps aux --sort=-%mem            # Sort by memory usage
lsof +D /path                  # Check file locks
```

### Scenario 2: Disk Space Emergency
```bash
# Find large files quickly
find / -type f -size +100M 2>/dev/null | head -20
du -ah /var | sort -rh | head -20
ncdu /var                      # Interactive disk usage

# Clean up space
journalctl --vacuum-size=100M  # Clean systemd logs
yum clean all                  # Clean package cache
apt clean                      # Clean package cache
find /tmp -type f -atime +7 -delete  # Clean old temp files
```

### Scenario 3: Network Connectivity Issues
```bash
# Systematic network troubleshooting
ping -c 4 8.8.8.8             # Test internet
ping -c 4 gateway_ip           # Test gateway
traceroute destination         # Trace route
nslookup domain.com            # Test DNS
netstat -rn                    # Check routing table
arp -a                         # Check ARP table
ethtool eth0                   # Check interface status
```

---
*Module này tạo nền tảng vững chắc cho tất cả các module tiếp theo. Thành thạo Linux administration là chìa khóa thành công tại Viettel IDC.*
