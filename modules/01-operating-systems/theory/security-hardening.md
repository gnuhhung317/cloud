# Security và Hardening - Bảo mật và Gia cố Hệ thống

## 🎯 Mục tiêu Học tập
Nắm vững các kỹ thuật bảo mật và hardening cho Linux và Windows systems, đáp ứng yêu cầu bảo mật nghiêm ngặt của môi trường enterprise tại Viettel IDC.

## 🧠 Security Theory Fundamentals - Lý thuyết Cơ bản về Bảo mật

### Information Security Triad (CIA Triad)

#### Confidentiality (Tính Bảo mật)
**Khái niệm**: Đảm bảo thông tin chỉ được truy cập bởi những người có thẩm quyền.

**Các Mối Đe dọa**:
- **Data Breach**: Rò rỉ dữ liệu do tấn công hoặc lỗi kỹ thuật
- **Insider Threats**: Nguy cơ từ nhân viên nội bộ
- **Eavesdropping**: Nghe lén thông tin truyền tải
- **Social Engineering**: Lừa đảo để lấy thông tin

**Biện pháp Bảo vệ**:
- **Encryption**: Mã hóa dữ liệu (AES, RSA, ECC)
- **Access Control**: Kiểm soát truy cập (RBAC, ABAC)
- **Data Classification**: Phân loại dữ liệu theo mức độ nhạy cảm
- **Network Segmentation**: Phân đoạn mạng để hạn chế truy cập

#### Integrity (Tính Toàn vẹn)
**Khái niệm**: Đảm bảo dữ liệu không bị thay đổi trái phép và duy trì tính chính xác.

**Các Mối Đe dọa**:
- **Data Tampering**: Sửa đổi dữ liệu trái phép
- **Man-in-the-Middle**: Tấn công ở giữa để thay đổi dữ liệu
- **Malware**: Phần mềm độc hại làm hỏng dữ liệu
- **System Corruption**: Lỗi hệ thống làm hỏng dữ liệu

**Biện pháp Bảo vệ**:
- **Digital Signatures**: Chữ ký số để xác thực
- **Hash Functions**: Hàm băm (SHA-256, SHA-3) để kiểm tra toàn vẹn
- **Checksums**: Tổng kiểm tra dữ liệu
- **Version Control**: Quản lý phiên bản và thay đổi
- **Database Constraints**: Ràng buộc cơ sở dữ liệu

#### Availability (Tính Khả dụng)
**Khái niệm**: Đảm bảo hệ thống và dữ liệu luôn sẵn sàng khi cần thiết.

**Các Mối Đe dọa**:
- **Denial of Service (DoS)**: Tấn công từ chối dịch vụ
- **Distributed DDoS**: Tấn công phân tán
- **Hardware Failures**: Lỗi phần cứng
- **Natural Disasters**: Thiên tai
- **Human Errors**: Lỗi con người

**Biện pháp Bảo vệ**:
- **Redundancy**: Dự phòng hệ thống
- **Load Balancing**: Cân bằng tải
- **Disaster Recovery**: Khôi phục sau thảm họa
- **Backup Systems**: Hệ thống sao lưu
- **Monitoring**: Giám sát liên tục

### Defense in Depth Strategy

#### Lý thuyết Defense in Depth
**Khái niệm**: Chiến lược bảo mật nhiều lớp, không dựa vào một biện pháp bảo vệ duy nhất.

**Nguyên lý Core**:
1. **Redundancy**: Dự phòng - Nhiều lớp bảo vệ cùng lúc
2. **Diversity**: Đa dạng - Sử dụng các công nghệ khác nhau
3. **Depth**: Chiều sâu - Bảo vệ từ ngoại vi đến lõi hệ thống

#### Seven Layers of Defense in Depth

**Layer 1: Physical Security**
- **Mục đích**: Bảo vệ thiết bị vật lý và cơ sở hạ tầng
- **Biện pháp**: Kiểm soát ra vào, camera giám sát, tủ khóa server
- **Các Thành phần**:
  - Data Center Security: Bảo mật trung tâm dữ liệu
  - Equipment Protection: Bảo vệ thiết bị
  - Environmental Controls: Kiểm soát môi trường (nhiệt độ, độ ẩm)

**Layer 2: Network Perimeter Security**
- **Mục đích**: Kiểm soát traffic vào/ra khỏi mạng
- **Biện pháp**: Firewall, IDS/IPS, VPN gateways
- **Các Thành phần**:
  - Border Routers: Router biên giới
  - Firewalls: Tường lửa
  - VPN Concentrators: Tập trung VPN
  - Network Intrusion Detection: Phát hiện xâm nhập mạng

**Layer 3: Network Segmentation**
- **Mục đích**: Phân chia mạng thành các vùng bảo mật
- **Biện pháp**: VLANs, subnets, internal firewalls
- **Các Thành phần**:
  - Network Zones: Vùng mạng (DMZ, Internal, Management)
  - Micro-segmentation: Phân đoạn vi mô
  - Software-Defined Perimeters: Ranh giới được định nghĩa bằng phần mềm

**Layer 4: Endpoint Security**
- **Mục đích**: Bảo vệ các thiết bị đầu cuối
- **Biện pháp**: Antivirus, EDR, device encryption
- **Các Thành phần**:
  - Host-based Firewalls: Tường lửa cấp host
  - Endpoint Detection and Response: Phát hiện và ứng phó tại endpoint
  - Mobile Device Management: Quản lý thiết bị di động

**Layer 5: Application Security**
- **Mục đích**: Bảo vệ ứng dụng khỏi các lỗ hổng
- **Biện pháp**: Input validation, secure coding, WAF
- **Các Thành phần**:
  - Web Application Firewalls: Tường lửa ứng dụng web
  - Application Whitelisting: Danh sách trắng ứng dụng
  - Secure Development Lifecycle: Vòng đời phát triển an toàn

**Layer 6: Data Security**
- **Mục đích**: Bảo vệ dữ liệu ở mọi trạng thái
- **Biện pháp**: Encryption, DLP, classification
- **Các Thành phần**:
  - Data Encryption: Mã hóa dữ liệu
  - Data Loss Prevention: Ngăn chặn mất dữ liệu
  - Database Security: Bảo mật cơ sở dữ liệu
  - Backup Protection: Bảo vệ sao lưu

**Layer 7: Mission Critical Assets**
- **Mục đích**: Bảo vệ tài sản quan trọng nhất
- **Biện pháp**: Privileged access management, monitoring
- **Các Thành phần**:
  - Crown Jewel Protection: Bảo vệ tài sản quý giá nhất
  - Privileged Access Management: Quản lý truy cập đặc quyền
  - Critical System Monitoring: Giám sát hệ thống quan trọng

### Zero Trust Security Model

#### Khái niệm Zero Trust
**Nguyên tắc**: "Never trust, always verify" - Không bao giờ tin tưởng, luôn xác minh.

**Các Nguyên lý Cốt lõi**:
1. **Verify Explicitly**: Xác minh rõ ràng mọi request
2. **Least Privilege Access**: Truy cập với đặc quyền tối thiểu
3. **Assume Breach**: Giả định đã bị xâm nhập

**Kiến trúc Zero Trust**:
- **Identity-Centric**: Tập trung vào danh tính
- **Device-Centric**: Tập trung vào thiết bị
- **Network-Centric**: Tập trung vào mạng
- **Application-Centric**: Tập trung vào ứng dụng
- **Data-Centric**: Tập trung vào dữ liệu

### Risk Management Framework

#### Risk Assessment Process
**Bước 1: Asset Identification**
- Xác định tài sản cần bảo vệ
- Phân loại theo giá trị và tầm quan trọng
- Mapping dependencies giữa các tài sản

**Bước 2: Threat Identification**
- Advanced Persistent Threats (APT)
- Insider Threats
- Cybercriminal Groups
- Nation-State Actors
- Accidental Threats

**Bước 3: Vulnerability Assessment**
- Technical Vulnerabilities: Lỗ hổng kỹ thuật
- Procedural Vulnerabilities: Lỗ hổng quy trình
- Physical Vulnerabilities: Lỗ hổng vật lý
- Human Factor Vulnerabilities: Lỗ hổng con người

**Bước 4: Risk Calculation**
```
Risk = Threat × Vulnerability × Impact
```

**Risk Matrix**:
- **Very High**: Immediate action required
- **High**: Action required within 1 month
- **Medium**: Action required within 3 months
- **Low**: Action required within 6 months
- **Very Low**: Monitor và review annually

#### Risk Treatment Strategies
1. **Risk Avoidance**: Tránh rủi ro bằng cách không thực hiện hoạt động
2. **Risk Mitigation**: Giảm thiểu rủi ro thông qua các biện pháp kiểm soát
3. **Risk Transfer**: Chuyển giao rủi ro (bảo hiểm, outsourcing)
4. **Risk Acceptance**: Chấp nhận rủi ro sau khi đánh giá cost-benefit

## 🔒 1. Linux Security Fundamentals

### User và Group Management Security

#### Lý thuyết Authentication, Authorization và Accounting (AAA)

**Authentication (Xác thực)**
- **Single Factor**: Chỉ sử dụng một yếu tố (password)
- **Multi-Factor Authentication (MFA)**:
  - Something you know: Password, PIN
  - Something you have: Token, smart card, phone
  - Something you are: Biometrics (fingerprint, iris)
  - Somewhere you are: Geolocation
  - Something you do: Behavioral patterns

**Authorization (Phân quyền)**
- **Discretionary Access Control (DAC)**: Chủ sở hữu quyết định quyền truy cập
- **Mandatory Access Control (MAC)**: Hệ thống quyết định dựa trên security labels
- **Role-Based Access Control (RBAC)**: Phân quyền dựa trên vai trò
- **Attribute-Based Access Control (ABAC)**: Phân quyền dựa trên thuộc tính

**Accounting (Kiểm toán)**
- Ghi lại mọi hoạt động của user
- Audit trails để tracking changes
- Compliance reporting
- Forensic analysis support

#### Password Security Theory

**Password Complexity Requirements**:
- **Length**: Minimum 12-15 characters cho enterprise
- **Character Sets**: Uppercase, lowercase, numbers, special characters
- **Entropy Calculation**: 
  ```
  Entropy = log2(charset_size^password_length)
  ```
- **Password Strength Metrics**:
  - Weak: < 30 bits entropy
  - Fair: 30-60 bits entropy
  - Strong: 60-120 bits entropy
  - Very Strong: > 120 bits entropy

**Password Storage Security**:
- **Hashing Algorithms**: bcrypt, scrypt, Argon2
- **Salt Usage**: Unique salt cho mỗi password
- **Iterations/Work Factor**: Tăng cost để chống brute force
- **Password History**: Ngăn tái sử dụng password cũ

**Common Password Attacks**:
- **Brute Force**: Thử tất cả combinations
- **Dictionary Attacks**: Sử dụng wordlist phổ biến
- **Rainbow Tables**: Pre-computed hash lookups
- **Credential Stuffing**: Sử dụng leaked credentials
- **Password Spraying**: Thử common passwords với nhiều accounts

#### Linux User Account Architecture

**User Identification System**:
- **UID (User ID)**: Unique identifier cho user
  - UID 0: Root user (superuser)
  - UID 1-999: System users và services
  - UID 1000+: Regular users
- **GID (Group ID)**: Primary group identifier
- **Supplementary Groups**: Additional group memberships

**Linux Password File Structure**:

**/etc/passwd Format**:
```
username:x:UID:GID:GECOS:home_directory:shell
```
- **username**: User login name
- **x**: Password placeholder (actual password in /etc/shadow)
- **UID**: User ID number
- **GID**: Primary group ID
- **GECOS**: User information field
- **home_directory**: User's home directory path
- **shell**: Default shell program

**/etc/shadow Format**:
```
username:encrypted_password:last_change:min_age:max_age:warn:inactive:expire:reserved
```
- **encrypted_password**: Hashed password với salt
- **last_change**: Days since epoch of last password change
- **min_age**: Minimum days between password changes
- **max_age**: Maximum days password is valid
- **warn**: Days before expiry để warning user
- **inactive**: Days after expiry before account is disabled
- **expire**: Absolute expiry date for account

#### Privilege Escalation Theory

**Horizontal Privilege Escalation**:
- User gains access to another user's privileges
- Same privilege level, different user context
- Often achieved through:
  - Session hijacking
  - Token manipulation
  - Shared resources exploitation

**Vertical Privilege Escalation**:
- User gains higher privileges (e.g., root access)
- Common attack vectors:
  - SUID/SGID binaries exploitation
  - Kernel vulnerabilities
  - Misconfigured sudo rules
  - Service account compromise

**Sudo Security Model**:
- **sudoers File Parsing**: Line-by-line evaluation
- **User_Alias**: Grouping users for easier management
- **Cmnd_Alias**: Grouping commands for specific tasks
- **Host_Alias**: Grouping hosts for distributed management
- **Runas_Alias**: Specifying target users for command execution

**PAM (Pluggable Authentication Modules) Architecture**:
- **Modular Design**: Separate authentication methods
- **Four Management Groups**:
  - **auth**: Authentication và identity verification
  - **account**: Account restrictions và availability
  - **password**: Password updating mechanisms
  - **session**: Session management và environment setup

**PAM Control Flags**:
- **required**: Must succeed, continue với other modules
- **requisite**: Must succeed, stop immediately if fails
- **sufficient**: Success means immediate success, failure continues
- **optional**: Success/failure doesn't affect overall result
- **include**: Include another PAM configuration file
- **substack**: Include another config với independent stack

#### Secure User Account Management
```bash
# Strong password policies
# /etc/login.defs configuration
PASS_MAX_DAYS   90      # Maximum password age
PASS_MIN_DAYS   1       # Minimum password age  
PASS_MIN_LEN    8       # Minimum password length
PASS_WARN_AGE   7       # Password expiration warning

# PAM password complexity (/etc/pam.d/common-password)
password requisite pam_pwquality.so retry=3 minlen=8 difok=3 ucredit=-1 lcredit=-1 dcredit=-1 ocredit=-1

# Account lockout policy (/etc/pam.d/common-auth)
auth required pam_faillock.so deny=5 unlock_time=900 fail_interval=900

# User account auditing
passwd -S username              # Password status
chage -l username               # Password aging information
lastlog                         # Last login times
last                           # Login history
who                            # Currently logged in users
w                              # Active users và processes
```

#### Privilege Escalation Control
```bash
# sudo configuration (/etc/sudoers)
# Best practices:
%wheel ALL=(ALL) ALL           # Group-based sudo access
user1 ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart httpd  # Specific commands only
user2 ALL=(webserver) /usr/bin/systemctl restart nginx      # Limited user context

# sudo logging
Defaults logfile=/var/log/sudo.log
Defaults log_year, loglinelen=0
Defaults syslog=authpriv

# sudo aliases for better management
User_Alias WEBADMINS = user1, user2, user3
Cmnd_Alias WEBCOMMANDS = /usr/bin/systemctl restart httpd, /usr/bin/systemctl reload httpd
WEBADMINS ALL = WEBCOMMANDS

# Restrict su command
# Only allow wheel group members to use su
echo "auth required pam_wheel.so use_uid" >> /etc/pam.d/su
```

### File System Security

#### Linux File System Security Theory

**Unix File Permissions Model**:
- **Owner (User)**: Người sở hữu file
- **Group**: Nhóm sở hữu file  
- **Others**: Tất cả users khác
- **Permission Types**:
  - **Read (r)**: Permission to read file content hoặc list directory
  - **Write (w)**: Permission to modify file hoặc create/delete files in directory
  - **Execute (x)**: Permission to execute file hoặc access directory

**Octal Permission Notation**:
```
4 = Read (r)
2 = Write (w)  
1 = Execute (x)
```
**Common Permission Combinations**:
- 755: rwxr-xr-x (Owner: full, Group/Others: read+execute)
- 644: rw-r--r-- (Owner: read+write, Group/Others: read only)
- 600: rw------- (Owner: read+write, Group/Others: no access)
- 777: rwxrwxrwx (Full permissions for all - DANGEROUS)

**Special Permission Bits**:

**SUID (Set User ID) - Bit 4000**:
- **Khái niệm**: File execution với owner's privileges
- **Use Cases**: passwd, sudo commands cần root privileges
- **Security Risk**: Có thể được exploit để privilege escalation
- **Identification**: 's' trong owner execute position (rwsr-xr-x)

**SGID (Set Group ID) - Bit 2000**:
- **On Files**: Execute với group owner's privileges
- **On Directories**: New files inherit directory's group ownership
- **Security Considerations**: Useful cho shared directories
- **Identification**: 's' trong group execute position (rwxr-sr-x)

**Sticky Bit - Bit 1000**:
- **Khái niệm**: Chỉ owner hoặc root có thể delete/rename files
- **Common Usage**: /tmp directory để prevent users deleting others' files
- **Identification**: 't' trong others execute position (rwxr-xr-t)

#### Access Control Lists (ACLs) Theory

**Standard ACLs vs Extended ACLs**:
- **Standard**: Owner, group, others (traditional Unix)
- **Extended**: Additional users và groups với specific permissions

**ACL Types**:
- **Access ACLs**: Applied to specific files và directories
- **Default ACLs**: Applied to directories, inherited by new files
- **Mask ACL**: Maximum permissions for named users và groups

**ACL Inheritance**:
- Default ACLs on directories tự động apply cho new files
- Effective permissions = ACL permissions ∩ Mask permissions

**ACL Best Practices**:
- Use groups thay vì individual user ACLs
- Document ACL usage cho maintenance
- Regular audit ACL assignments
- Backup ACL settings với getfacl

#### Extended File Attributes Theory

**File Attributes in ext2/3/4**:
- **Immutable (i)**: File cannot be modified, deleted, renamed
- **Append-only (a)**: Data can only be appended
- **No-dump (d)**: File excluded from backup
- **Synchronous (S)**: All changes written immediately
- **Secure deletion (s)**: Overwrite with zeros when deleted
- **Undeletable (u)**: Contents saved when deleted

**Security Applications**:
- **System Files**: chattr +i /etc/passwd (prevent modification)
- **Log Files**: chattr +a /var/log/secure (append-only logging)
- **Configuration Files**: Protect critical configs from tampering

#### File System Mount Security

**Security Mount Options**:

**nodev**: 
- **Purpose**: Prevent device files trong filesystem
- **Security**: Ngăn tạo device files để bypass permissions
- **Usage**: Recommended cho /home, /tmp, /var

**nosuid**:
- **Purpose**: Ignore SUID và SGID bits
- **Security**: Prevent privilege escalation through SUID programs
- **Usage**: Essential cho /tmp, /home, removable media

**noexec**:
- **Purpose**: Prevent execution of binaries
- **Security**: Stop malware execution trong writable directories
- **Usage**: /tmp, /home, /var (except /var/lib)

**ro (read-only)**:
- **Purpose**: Mount filesystem as read-only
- **Security**: Prevent any modifications
- **Usage**: System directories that don't need writes

**Filesystem Hardening Strategy**:
1. **Separate Partitions**: /tmp, /var, /home on separate partitions
2. **Appropriate Mount Options**: Apply security options based on usage
3. **Quota Management**: Prevent disk space exhaustion attacks
4. **Regular Integrity Checks**: Use AIDE, Tripwire cho monitoring

#### File Integrity Monitoring Theory

**Baseline Creation**:
- **Initial State**: Capture known-good file states
- **Hash Calculations**: MD5, SHA-1, SHA-256 checksums
- **Metadata Storage**: Permissions, ownership, timestamps
- **Database Protection**: Secure integrity database storage

**Change Detection Methods**:
- **Periodic Scanning**: Scheduled integrity checks
- **Real-time Monitoring**: Immediate change notifications
- **Signature Verification**: Compare current vs baseline hashes
- **Anomaly Detection**: Identify suspicious patterns

**AIDE (Advanced Intrusion Detection Environment)**:
- **Configuration**: Define which files/directories to monitor
- **Rule-based Monitoring**: Different check levels cho different areas
- **Report Generation**: Detailed change reports
- **Database Management**: Regular database updates

**File Integrity Tools Comparison**:
- **AIDE**: Open source, comprehensive
- **Tripwire**: Commercial, advanced features
- **OSSEC**: Integrated với IDS capabilities
- **Samhain**: Network-capable, centralized monitoring

#### File Permissions và ACLs
```bash
# Standard permissions review
find /home -type f -perm 777    # World-writable files (security risk)
find /home -type d -perm 777    # World-writable directories
find / -perm -4000 2>/dev/null  # SUID files
find / -perm -2000 2>/dev/null  # SGID files
find / -perm -1000 2>/dev/null  # Sticky bit files

# Advanced ACLs
getfacl filename                # View ACLs
setfacl -m u:username:rw filename  # Grant user read/write
setfacl -m g:groupname:r filename  # Grant group read
setfacl -x u:username filename     # Remove user ACL
setfacl -b filename                # Remove all ACLs

# Default ACLs for directories
setfacl -d -m u:username:rw /shared/directory  # Default ACLs for new files

# File attributes
lsattr filename                 # List file attributes
chattr +i filename              # Make file immutable
chattr +a filename              # Append-only file
chattr -i filename              # Remove immutable attribute
```

#### File System Hardening
```bash
# Mount options for security
# /etc/fstab security options:
/dev/sdb1 /home ext4 defaults,nodev,nosuid,noexec 0 2
/dev/sdc1 /tmp ext4 defaults,nodev,nosuid,noexec 0 2
/dev/sdd1 /var/log ext4 defaults,nodev,nosuid,noexec 0 2

# Temporary filesystem security
mount -o remount,noexec,nosuid,nodev /tmp
mount -o remount,noexec,nosuid,nodev /var/tmp
mount -o remount,noexec,nosuid,nodev /dev/shm

# File integrity monitoring
aide --init                     # Initialize AIDE database
aide --check                    # Check file integrity
rpm -Va                         # Verify all RPM packages (Red Hat)
debsums -c                      # Verify package checksums (Debian)
```

### Network Security

#### Network Security Fundamentals

**Network Security Models**:

**OSI Security Architecture (ISO 7498-2)**:
- **Security Services**:
  - **Authentication**: Xác thực danh tính entities
  - **Access Control**: Kiểm soát truy cập resources
  - **Data Confidentiality**: Bảo vệ thông tin khỏi disclosure
  - **Data Integrity**: Đảm bảo dữ liệu không bị modification
  - **Non-repudiation**: Ngăn chặn từ chối trách nhiệm
  - **Availability**: Đảm bảo resource luôn accessible

**Network Perimeter Security**:
- **Trusted Network**: Internal network (high trust)
- **Untrusted Network**: Internet (zero trust)
- **DMZ (Demilitarized Zone)**: Buffer zone giữa trusted và untrusted
- **Network Segmentation**: Chia network thành security zones

#### Firewall Theory và Architecture

**Firewall Types**:

**Packet Filtering Firewalls**:
- **Stateless**: Examine individual packets independently
- **Rules Based**: Allow/deny dựa trên source/destination IP, ports
- **Performance**: High throughput, low latency
- **Limitations**: Cannot track connection state, vulnerable to spoofing

**Stateful Inspection Firewalls**:
- **Connection Tracking**: Maintain state table của active connections
- **Context Awareness**: Understand connection state (NEW, ESTABLISHED, RELATED)
- **Security**: Better protection through connection correlation
- **Performance**: Moderate overhead cho state tracking

**Application Layer Firewalls (Proxy)**:
- **Deep Inspection**: Analyze application protocol content
- **Protocol Validation**: Ensure protocol compliance
- **Content Filtering**: Block malicious content
- **Performance**: Higher latency due to full inspection

**Next-Generation Firewalls (NGFW)**:
- **Integrated Features**: IPS, antivirus, web filtering
- **Application Awareness**: Identify applications regardless of port
- **User Identity**: User-based policies
- **Threat Intelligence**: Real-time threat feeds

#### iptables Architecture và Theory

**Netfilter Framework**:
- **Kernel Space**: Netfilter hooks trong kernel
- **User Space**: iptables command để configure rules
- **Hook Points**: 
  - PREROUTING: Before routing decision
  - INPUT: Packets destined cho local system
  - FORWARD: Packets being routed through system
  - OUTPUT: Packets generated by local system
  - POSTROUTING: After routing decision

**iptables Tables**:
- **filter**: Default table cho packet filtering (INPUT, OUTPUT, FORWARD)
- **nat**: Network Address Translation (PREROUTING, OUTPUT, POSTROUTING)
- **mangle**: Packet alteration (all hooks)
- **raw**: Connection tracking exceptions (PREROUTING, OUTPUT)
- **security**: SELinux packet security (INPUT, OUTPUT, FORWARD)

**Rule Processing**:
1. **Table Priority**: raw → mangle → nat → filter → security
2. **Chain Traversal**: Sequential rule evaluation
3. **Match Criteria**: Protocol, IP, port, interface, state
4. **Target Actions**: ACCEPT, DROP, REJECT, LOG, QUEUE

**Connection Tracking (conntrack)**:
- **State Tracking**: NEW, ESTABLISHED, RELATED, INVALID
- **Connection Table**: /proc/net/nf_conntrack
- **Memory Management**: Automatic cleanup của expired connections
- **Performance Tuning**: Connection limits và timeouts

#### Advanced Firewall Concepts

**Rate Limiting Theory**:
- **Token Bucket Algorithm**: Fixed rate với burst capability
- **Leaky Bucket Algorithm**: Smooth output rate
- **Sliding Window**: Time-based rate calculation
- **Application**: DDoS mitigation, service protection

**Connection State Analysis**:
- **TCP State Machine**: SYN, SYN-ACK, ACK handshake tracking
- **UDP Pseudo-state**: Time-based state tracking
- **ICMP Handling**: Error message correlation
- **Fragment Handling**: Packet reassembly để inspection

**Geo-blocking và IP Reputation**:
- **Country-based Blocking**: Block traffic from specific countries
- **IP Reputation Lists**: Known malicious IP addresses
- **Dynamic Updates**: Real-time threat intelligence feeds
- **False Positive Management**: Whitelist legitimate sources

#### Intrusion Detection Systems (IDS) Theory

**IDS Types**:

**Network-based IDS (NIDS)**:
- **Deployment**: Network segments hoặc choke points
- **Detection Method**: Analyze network traffic patterns
- **Coverage**: Entire network segment
- **Limitations**: Encryption blindness, switch fabric issues

**Host-based IDS (HIDS)**:
- **Deployment**: Individual hosts
- **Detection Method**: System calls, file changes, log analysis
- **Coverage**: Single host focus
- **Advantages**: Encrypted traffic visibility, detailed host data

**Detection Methods**:

**Signature-based Detection**:
- **Pattern Matching**: Known attack signatures
- **Advantages**: Low false positives, specific threat identification
- **Disadvantages**: Cannot detect zero-day attacks
- **Database**: Regular signature updates required

**Anomaly-based Detection**:
- **Baseline Establishment**: Normal behavior patterns
- **Statistical Analysis**: Deviation from normal patterns
- **Machine Learning**: Advanced pattern recognition
- **Challenges**: High false positives, baseline drift

**Hybrid Detection**:
- **Combined Approach**: Signature + anomaly detection
- **Complementary Strengths**: Cover different attack types
- **Correlation**: Cross-reference detection results
- **Risk Scoring**: Weighted threat assessment

#### Firewall Configuration (iptables)
```bash
# Basic iptables hardening script
#!/bin/bash
# firewall_hardening.sh

# Flush existing rules
iptables -F
iptables -X
iptables -t nat -F
iptables -t nat -X

# Set default policies
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT

# Allow loopback
iptables -A INPUT -i lo -j ACCEPT
iptables -A OUTPUT -o lo -j ACCEPT

# Allow established connections
iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

# Allow SSH (change port from default)
iptables -A INPUT -p tcp --dport 2222 -m conntrack --ctstate NEW -j ACCEPT

# Allow HTTP/HTTPS
iptables -A INPUT -p tcp --dport 80 -m conntrack --ctstate NEW -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -m conntrack --ctstate NEW -j ACCEPT

# Rate limiting for SSH
iptables -A INPUT -p tcp --dport 2222 -m recent --name SSH --set
iptables -A INPUT -p tcp --dport 2222 -m recent --name SSH --rcheck --seconds 60 --hitcount 4 -j DROP

# Log dropped packets
iptables -A INPUT -j LOG --log-prefix "DROPPED: " --log-level 4
iptables -A INPUT -j DROP

# Save rules
iptables-save > /etc/iptables/rules.v4
```

#### Firewall Configuration (firewalld)
```bash
# firewalld zones và services
firewall-cmd --get-default-zone
firewall-cmd --list-all-zones

# Create custom zone
firewall-cmd --permanent --new-zone=webserver
firewall-cmd --permanent --zone=webserver --add-interface=eth0
firewall-cmd --permanent --zone=webserver --add-service=http
firewall-cmd --permanent --zone=webserver --add-service=https
firewall-cmd --permanent --zone=webserver --add-port=8080/tcp

# Rich rules for advanced filtering
firewall-cmd --permanent --add-rich-rule='rule family="ipv4" source address="192.168.1.0/24" service name="ssh" accept'
firewall-cmd --permanent --add-rich-rule='rule family="ipv4" source address="10.0.0.0/8" port port="3306" protocol="tcp" accept'

# Rate limiting
firewall-cmd --permanent --add-rich-rule='rule family="ipv4" source address="0.0.0.0/0" service name="ssh" accept limit value="10/m"'

# Reload configuration
firewall-cmd --reload
```

#### Network Monitoring và Intrusion Detection
```bash
# Install và configure fail2ban
yum install fail2ban -y  # CentOS/RHEL
apt install fail2ban -y  # Ubuntu/Debian

# /etc/fail2ban/jail.local
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3
backend = systemd

[sshd]
enabled = true
port = 2222
logpath = /var/log/secure
maxretry = 3

[httpd-auth]
enabled = true
port = http,https
logpath = /var/log/httpd/error_log

# Start fail2ban
systemctl enable fail2ban
systemctl start fail2ban

# Monitor fail2ban
fail2ban-client status
fail2ban-client status sshd
fail2ban-client unban IP_ADDRESS
```

### SSH Hardening

#### SSH Protocol Theory

**SSH Architecture Components**:
- **SSH Client**: User interface cho SSH connections
- **SSH Server (sshd)**: Daemon handling incoming connections
- **SSH Keys**: Cryptographic keys cho authentication
- **SSH Agent**: Key management service
- **SSH Protocol Versions**:
  - SSH-1: Deprecated due to security flaws
  - SSH-2: Current standard với better security

**SSH Connection Process**:
1. **Version Negotiation**: Client và server agree on protocol version
2. **Key Exchange**: Establish session keys using Diffie-Hellman
3. **Server Authentication**: Client verifies server identity
4. **User Authentication**: Server verifies user identity
5. **Channel Establishment**: Secure channel cho data transmission

#### SSH Cryptographic Algorithms

**Key Exchange Algorithms**:
- **Diffie-Hellman**: Traditional key exchange
- **Elliptic Curve Diffie-Hellman (ECDH)**: More efficient
- **Curve25519**: High-security elliptic curve

**Symmetric Encryption**:
- **AES (Advanced Encryption Standard)**: Industry standard
- **ChaCha20**: Stream cipher with high performance
- **3DES**: Legacy, should be disabled

**Message Authentication**:
- **HMAC-SHA2**: Hash-based message authentication
- **Poly1305**: Used with ChaCha20
- **HMAC-MD5**: Legacy, weak

**Host Key Algorithms**:
- **Ed25519**: Edwards curve, recommended
- **ECDSA**: Elliptic curve, good performance
- **RSA**: Traditional, require 2048+ bit keys
- **DSA**: Deprecated due to weaknesses

#### SSH Authentication Methods

**Password Authentication**:
- **Vulnerabilities**: Brute force, dictionary attacks
- **Mitigation**: Strong passwords, account lockout
- **Best Practice**: Disable in favor of key-based auth

**Public Key Authentication**:
- **Key Pairs**: Public key (shareable) + Private key (secret)
- **Algorithm Support**: RSA, ECDSA, Ed25519
- **Security Benefits**: Strong cryptographic authentication
- **Key Management**: Secure storage và distribution

**Multi-Factor Authentication**:
- **Two-Factor**: Key + something else (TOTP, hardware token)
- **Certificate-based**: SSH certificates với CA validation
- **GSSAPI/Kerberos**: Integrated enterprise authentication

#### SSH Security Best Practices Theory

**Port Security**:
- **Default Port 22**: Well-known target cho attacks
- **Port Obscurity**: Change to non-standard port
- **Port Knocking**: Require sequence để open SSH port
- **VPN Access**: Restrict SSH access through VPN

**Access Control**:
- **User Restrictions**: Limit which users can SSH
- **Group-based Access**: Use groups cho easier management
- **Host-based Access**: IP address restrictions
- **Time-based Access**: Scheduled access windows

**Session Management**:
- **Connection Limits**: Prevent resource exhaustion
- **Idle Timeouts**: Automatically close idle sessions
- **Keep-alive**: Maintain connections through firewalls
- **Login Grace**: Limit authentication time

**Logging và Monitoring**:
- **Authentication Logs**: Track login attempts
- **Session Logging**: Record user activities
- **Failed Login Monitoring**: Detect brute force attacks
- **Key Usage Tracking**: Monitor SSH key usage

#### SSH Key Cryptography Theory

**Key Generation**:
- **Entropy Sources**: /dev/random, /dev/urandom
- **Key Strength**: Bit length determines security level
- **Algorithm Choice**: Ed25519 > ECDSA > RSA
- **Passphrase Protection**: Encrypt private key với passphrase

**Key Sizes và Security**:
- **RSA**: 2048-bit minimum, 4096-bit recommended
- **ECDSA**: 256-bit (equivalent to RSA 3072-bit)
- **Ed25519**: 256-bit (equivalent to RSA 3072-bit)

**Key Distribution**:
- **Secure Channel**: Initial key exchange over secure channel
- **Out-of-band Verification**: Verify fingerprints manually
- **Certificate Authority**: Centralized key management
- **Key Rotation**: Regular key replacement

**SSH Agent Security**:
- **Memory Protection**: Keys stored in protected memory
- **Agent Forwarding**: Risks và mitigation
- **Key Lifetime**: Automatic key expiration
- **Agent Hijacking**: Protection against unauthorized access

#### SSH Tunneling và Port Forwarding

**Local Port Forwarding**:
- **Use Case**: Access remote services through SSH tunnel
- **Security**: Encrypt traffic to remote server
- **Command**: ssh -L local_port:remote_host:remote_port user@ssh_server

**Remote Port Forwarding**:
- **Use Case**: Expose local services to remote network
- **Security Risk**: Can bypass firewall restrictions
- **Command**: ssh -R remote_port:local_host:local_port user@ssh_server

**Dynamic Port Forwarding (SOCKS)**:
- **Use Case**: SOCKS proxy through SSH
- **Applications**: Web browsing, general network access
- **Command**: ssh -D local_port user@ssh_server

**Security Considerations**:
- **Tunnel Restrictions**: Disable if not needed
- **Bandwidth Limits**: Prevent abuse
- **Access Controls**: Limit tunnel destinations
- **Monitoring**: Log tunnel usage

#### SSH Configuration Security
```bash
# /etc/ssh/sshd_config hardening
Port 2222                       # Change default port
Protocol 2                      # Use SSH v2 only
PermitRootLogin no              # Disable root login
PasswordAuthentication no       # Use key-based auth only
PubkeyAuthentication yes        # Enable public key auth
AuthorizedKeysFile .ssh/authorized_keys
PermitEmptyPasswords no         # No empty passwords
ChallengeResponseAuthentication no
UsePAM yes
X11Forwarding no                # Disable X11 forwarding
PrintMotd no                    # Disable MOTD
PrintLastLog yes
TCPKeepAlive yes
ClientAliveInterval 300         # Keep alive interval
ClientAliveCountMax 2           # Max missed heartbeats
MaxAuthTries 3                  # Limit auth attempts
MaxSessions 2                   # Limit sessions per connection
LoginGraceTime 60               # Login timeout

# Restrict users và groups
AllowUsers admin user1 user2
DenyUsers guest
AllowGroups sudo wheel
DenyGroups users

# Host-based restrictions
Match Address 192.168.1.0/24
    PasswordAuthentication yes
    
Match User backup
    ForceCommand /usr/local/bin/backup-script.sh
    PermitTTY no
```

#### SSH Key Management
```bash
# Generate strong SSH keys
ssh-keygen -t ed25519 -b 4096 -C "user@hostname"  # Ed25519 (recommended)
ssh-keygen -t rsa -b 4096 -C "user@hostname"      # RSA 4096-bit

# Deploy keys securely
ssh-copy-id -i ~/.ssh/id_ed25519.pub user@server
# Or manually:
cat ~/.ssh/id_ed25519.pub | ssh user@server "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"

# Key security
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
chmod 600 ~/.ssh/id_ed25519
chmod 644 ~/.ssh/id_ed25519.pub

# SSH agent for key management
eval $(ssh-agent)
ssh-add ~/.ssh/id_ed25519
ssh-add -l                      # List loaded keys
```

### SELinux Security

#### SELinux Theory và Architecture

**Mandatory Access Control (MAC)**:
- **Concept**: System-enforced access control, không thể bypassed bởi users
- **Contrast với DAC**: Traditional Unix permissions (user-controlled)
- **Policy-driven**: Central security policy định nghĩa tất cả access rules
- **Non-discretionary**: Users không thể change security attributes

**SELinux Core Concepts**:

**Security Context**:
- **Format**: user:role:type:level
- **User**: SELinux user identity (khác với Linux user)
- **Role**: Set of permissions cho user
- **Type**: Security type cho objects (files, processes)
- **Level**: Multi-level security classification (optional)

**Type Enforcement (TE)**:
- **Domain**: Security context cho processes
- **Type**: Security context cho objects (files, sockets, etc.)
- **Policy Rules**: Allow/deny access giữa domains và types
- **Transition Rules**: How processes change domains

**Role-Based Access Control (RBAC)**:
- **Roles**: Collections of permissions
- **User-Role Mapping**: Users assigned to roles
- **Role-Domain Mapping**: Roles can access specific domains

**Multi-Level Security (MLS)**:
- **Security Levels**: Confidentiality levels (e.g., Top Secret, Secret)
- **Categories**: Compartmentalization within levels
- **Bell-LaPadula Model**: No read up, no write down

#### SELinux Policy Architecture

**Policy Types**:

**Targeted Policy**:
- **Default**: Most common policy type
- **Scope**: Protects specific services (httpd, ssh, etc.)
- **Unconfined Domain**: Most user processes run unconfined
- **Confined Services**: Network-facing services are confined

**Strict Policy**:
- **Comprehensive**: All processes are confined
- **Complex**: Requires extensive configuration
- **High Security**: Maximum protection
- **Administrative Overhead**: Difficult to manage

**MLS Policy**:
- **Military-grade**: Multi-level security classification
- **Compartmentalization**: Information isolation
- **Formal Model**: Based on Bell-LaPadula model
- **Specialized Use**: Government và military environments

#### SELinux Modes

**Enforcing Mode**:
- **Active Protection**: SELinux policy được enforced
- **Access Denials**: Violations are blocked và logged
- **Production Mode**: Recommended cho live systems
- **Performance Impact**: Minimal overhead

**Permissive Mode**:
- **Learning Mode**: Policy violations are logged but not blocked
- **Troubleshooting**: Useful cho debugging policy issues
- **Transition**: Safe mode khi switching policies
- **Audit Logs**: Generate data cho policy development

**Disabled Mode**:
- **No Protection**: SELinux completely disabled
- **No Overhead**: No performance impact
- **Security Risk**: No MAC protection
- **Re-enable Complexity**: Requires relabeling filesystem

#### SELinux Context Management

**File Contexts**:
- **Default Contexts**: Defined in policy files
- **Context Inheritance**: New files inherit parent directory context
- **Context Transition**: Files can change context based on rules
- **Relabeling**: Restore correct contexts after changes

**Process Contexts**:
- **Domain Transitions**: How processes change domains
- **Entry Points**: Executable files that trigger transitions
- **Auto Transitions**: Automatic domain changes
- **Manual Transitions**: User-initiated domain changes

**Network Contexts**:
- **Port Labels**: Network ports have SELinux types
- **Node Labels**: Network nodes có security contexts
- **Packet Labels**: Network packets có security labels
- **Network Isolation**: Separate network traffic by context

#### SELinux Booleans

**Boolean Variables**:
- **Policy Switches**: Turn policy features on/off
- **Runtime Changes**: Modify policy without rebuilds
- **Common Booleans**:
  - httpd_can_network_connect: Allow web server network access
  - ftpd_use_passive_mode: Enable FTP passive mode
  - samba_enable_home_dirs: Allow Samba home directories

**Boolean Management**:
- **Query**: getsebool -a (list all booleans)
- **Set Temporary**: setsebool boolean_name on
- **Set Permanent**: setsebool -P boolean_name on
- **Policy Integration**: Booleans integrated into policy rules

#### SELinux Policy Development

**Policy Modules**:
- **Modular Design**: Separate modules cho different services
- **Base Policy**: Core policy functionality
- **Optional Modules**: Additional service-specific policies
- **Custom Modules**: User-developed policies

**Policy Language**:
- **Reference Policy**: Standard policy framework
- **Type Enforcement Language**: Low-level policy language
- **Policy Macros**: High-level policy constructs
- **Interface Definitions**: APIs cho policy modules

**Audit Log Analysis**:
- **AVC Messages**: Access Vector Cache denials
- **Audit Tools**: ausearch, aureport, sealert
- **Policy Generation**: audit2allow tool
- **False Positives**: Legitimate denials that need exceptions

#### SELinux Configuration và Management
```bash
# SELinux status và modes
getenforce                      # Current mode
sestatus                        # Detailed status
setenforce 0                    # Permissive (temporary)
setenforce 1                    # Enforcing (temporary)

# Permanent mode change (/etc/selinux/config)
SELINUX=enforcing               # enforcing, permissive, disabled
SELINUXTYPE=targeted            # targeted, minimum, mls

# SELinux contexts
ls -Z /var/www/html/            # View file contexts
ps axZ                          # View process contexts
id -Z                           # Current user context

# Context management
chcon -t httpd_exec_t /path/to/file      # Change context
restorecon /path/to/file                 # Restore default context
restorecon -Rv /var/www/html/            # Recursive restore

# SELinux policies
getsebool -a                             # List all booleans
setsebool httpd_can_network_connect on   # Enable boolean
setsebool -P httpd_can_network_connect on # Make permanent

# Custom SELinux modules
audit2allow -a                          # Generate policy from denials
audit2allow -a -M mypolicy               # Create policy module
semodule -i mypolicy.pp                  # Install policy module
```

#### SELinux Troubleshooting
```bash
# Analyze denials
sealert -a /var/log/audit/audit.log     # Analyze all denials
ausearch -m AVC -ts recent              # Recent AVC denials
tail -f /var/log/audit/audit.log | grep denied

# SELinux troubleshooting tools
yum install setroubleshoot-server policycoreutils-python -y
sealert -l "*"                          # List all alerts

# Generate custom policies
grep httpd /var/log/audit/audit.log | audit2allow -M myhttpd
semodule -i myhttpd.pp
```

## 🛡️ 2. Windows Security Hardening

#### Windows Security Architecture Theory

**Windows Security Model**:
- **Access Tokens**: Security context cho processes và threads
- **Security Identifiers (SIDs)**: Unique identifiers cho security principals
- **Access Control Lists (ACLs)**: Permissions lists cho objects
- **Security Reference Monitor**: Kernel component enforcing access control
- **Local Security Authority (LSA)**: Authentication và authorization subsystem

**Windows Security Subsystem Components**:

**Security Accounts Manager (SAM)**:
- **Local Account Database**: Storage cho local user accounts
- **Password Hashing**: LM và NTLM hash storage
- **Account Policies**: Password và lockout policies
- **Security Database**: Registry-based security information

**Local Security Authority Subsystem (LSASS)**:
- **Authentication Services**: Login validation
- **Security Policy Management**: Local security policy enforcement
- **Audit Logging**: Security event logging
- **Token Management**: Access token creation và management

**Security Reference Monitor (SRM)**:
- **Access Control**: Object access validation
- **Audit Generation**: Security audit trail
- **Privilege Management**: User rights và privileges
- **Security Descriptor Processing**: ACL evaluation

#### Windows Authentication Theory

**Authentication Protocols**:

**NTLM (NT LAN Manager)**:
- **Challenge-Response**: Three-way authentication handshake
- **Hash-based**: Uses NTLM hash của password
- **Backward Compatibility**: Legacy protocol support
- **Security Limitations**: Vulnerable to pass-the-hash attacks

**Kerberos**:
- **Ticket-based**: Uses tickets cho authentication
- **Key Distribution Center (KDC)**: Central authentication service
- **Mutual Authentication**: Both client và server authenticated
- **Delegation Support**: Service-to-service authentication

**Certificate-based Authentication**:
- **Smart Cards**: Hardware-based authentication
- **Digital Certificates**: PKI-based authentication
- **Certificate Authorities**: Trusted certificate issuers
- **Certificate Validation**: Chain of trust verification

#### Windows Access Control Theory

**Discretionary Access Control (DAC)**:
- **Object Ownership**: Owners control access permissions
- **Access Control Entries (ACEs)**: Individual permission entries
- **Inheritance**: Child objects inherit parent permissions
- **Effective Permissions**: Cumulative effect của multiple ACEs

**Access Control List (ACL) Types**:

**Discretionary ACL (DACL)**:
- **Purpose**: Controls access to objects
- **Allow ACEs**: Grant specific permissions
- **Deny ACEs**: Explicitly deny permissions
- **ACE Ordering**: Deny ACEs processed before Allow ACEs

**System ACL (SACL)**:
- **Purpose**: Controls auditing của object access
- **Audit Success**: Log successful access attempts
- **Audit Failure**: Log failed access attempts
- **Audit Policies**: System-wide audit configuration

**Access Rights**:
- **Standard Rights**: Read, Write, Execute, Delete
- **Specific Rights**: Object-type specific permissions
- **Generic Rights**: Mapped to specific rights
- **Combined Rights**: Full Control, Modify, Read & Execute

#### User Account Control (UAC) Theory

**UAC Architecture**:
- **Admin Approval Mode**: Administrators run với standard user token
- **Elevation Prompts**: Request administrator permissions
- **Secure Desktop**: Isolated environment cho UAC prompts
- **Application Compatibility**: Legacy application support

**UAC Levels**:
- **Level 0**: Never notify (UAC disabled)
- **Level 1**: Notify when apps make changes (no secure desktop)
- **Level 2**: Notify when apps make changes (default)
- **Level 3**: Always notify (highest security)

**UAC Bypass Techniques (để understanding threats)**:
- **Auto-elevation**: Certain Windows programs auto-elevate
- **DLL Hijacking**: Replace legitimate DLLs với malicious ones
- **Registry Manipulation**: Modify registry keys cho elevation
- **Process Injection**: Inject code into elevated processes

### Windows Account Security

#### Windows Account Types Theory

**Local Accounts**:
- **Built-in Accounts**: Administrator, Guest, system accounts
- **User-created Accounts**: Regular user accounts
- **Service Accounts**: Accounts cho Windows services
- **Virtual Accounts**: Managed service accounts

**Domain Accounts**:
- **Domain Users**: Authenticated by domain controllers
- **Domain Admins**: Administrative access to domain
- **Enterprise Admins**: Forest-wide administrative access
- **Service Principals**: Service accounts trong Active Directory

**Group Types**:
- **Security Groups**: Used cho access control
- **Distribution Groups**: Used cho email distribution
- **Local Groups**: Exist on local machine only
- **Domain Groups**: Exist trong Active Directory

#### Local Security Policy
```powershell
# Password policy configuration
secedit /export /cfg C:\temp\current_policy.inf

# Account lockout policy
net accounts /lockoutthreshold:5 /lockoutduration:30 /lockoutwindow:30

# Password policy
net accounts /maxpwage:90 /minpwage:1 /minpwlen:8 /uniquepw:5

# User rights assignment (use secpol.msc or Group Policy)
# Key security settings:
# - Log on as a service: Limit to service accounts only
# - Log on locally: Limit to authorized users
# - Access this computer from network: Remove Everyone group
# - Deny log on locally: Add Guest account
```

#### User Account Control (UAC)
```powershell
# UAC configuration via registry
# UAC levels:
# 0 = Never notify (least secure)
# 1 = Notify me only when apps try to make changes (no dimming)
# 2 = Notify me only when apps try to make changes (default)
# 3 = Always notify (most secure)

Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" -Name "ConsentPromptBehaviorAdmin" -Value 2
Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" -Name "EnableLUA" -Value 1
Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" -Name "PromptOnSecureDesktop" -Value 1
```

### Windows Firewall Hardening

#### Windows Firewall Theory

**Windows Firewall Architecture**:
- **Stateful Inspection**: Track connection state
- **Profile-based**: Different rules cho different networks
- **Bidirectional Filtering**: Control inbound và outbound traffic
- **Application Control**: Per-application firewall rules
- **Integration**: Integrated với Windows Security Model

**Firewall Profiles**:

**Domain Profile**:
- **Activation**: When connected to domain network
- **Group Policy**: Centrally managed through AD
- **Default Settings**: Generally more permissive
- **Use Case**: Corporate network environments

**Private Profile**:
- **Activation**: Home/work networks (trusted)
- **User Control**: User can configure settings
- **Default Settings**: Moderately restrictive
- **Use Case**: Home offices, small business networks

**Public Profile**:
- **Activation**: Public networks (untrusted)
- **Security**: Most restrictive settings
- **Default Settings**: Block most inbound connections
- **Use Case**: Coffee shops, airports, hotels

#### Windows Firewall Features

**Connection Security Rules**:
- **IPSec Integration**: Authentication và encryption
- **Isolation Rules**: Require authentication
- **Server-to-Server Rules**: Protect specific connections
- **Tunnel Rules**: Site-to-site VPN connections

**Advanced Security Features**:
- **Edge Traversal**: Allow traffic through NAT
- **Interface Types**: Specific network interface rules
- **Protocol Authentication**: Require authenticated connections
- **Encryption Requirements**: Mandate encrypted communications

**Rule Processing Order**:
1. **Block rules**: Processed first
2. **Allow rules**: Processed if no block rules match
3. **Default action**: Applied if no rules match
4. **Profile precedence**: Most restrictive profile wins

#### Windows Defender Firewall vs Third-party

**Built-in Advantages**:
- **OS Integration**: Deep integration với Windows
- **Performance**: Kernel-level filtering
- **Compatibility**: No driver conflicts
- **Management**: PowerShell và Group Policy support

**Third-party Advantages**:
- **Advanced Features**: More sophisticated filtering
- **Centralized Management**: Enterprise management consoles
- **Reporting**: Detailed logging và reporting
- **Custom Rules**: More granular rule creation

#### Advanced Firewall Configuration
```powershell
# Firewall profiles
Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled True
Set-NetFirewallProfile -Profile Domain,Public,Private -DefaultInboundAction Block
Set-NetFirewallProfile -Profile Domain,Public,Private -DefaultOutboundAction Allow
Set-NetFirewallProfile -Profile Domain,Public,Private -NotifyOnListen True
Set-NetFirewallProfile -Profile Domain,Public,Private -LogAllowed True
Set-NetFirewallProfile -Profile Domain,Public,Private -LogBlocked True

# Remove default rules that are too permissive
Remove-NetFirewallRule -DisplayName "File and Printer Sharing*"
Remove-NetFirewallRule -DisplayName "Network Discovery*"

# Create specific allow rules
New-NetFirewallRule -DisplayName "Allow HTTP Inbound" -Direction Inbound -Protocol TCP -LocalPort 80 -Action Allow
New-NetFirewallRule -DisplayName "Allow HTTPS Inbound" -Direction Inbound -Protocol TCP -LocalPort 443 -Action Allow
New-NetFirewallRule -DisplayName "Allow SSH Inbound" -Direction Inbound -Protocol TCP -LocalPort 22 -RemoteAddress 192.168.1.0/24 -Action Allow

# Advanced rules with authentication
New-NetFirewallRule -DisplayName "Allow SMB with Auth" -Direction Inbound -Protocol TCP -LocalPort 445 -Authentication Required -Action Allow

# Application-specific rules
New-NetFirewallRule -DisplayName "Allow SQL Server" -Direction Inbound -Program "C:\Program Files\Microsoft SQL Server\MSSQL15.MSSQLSERVER\MSSQL\Binn\sqlservr.exe" -Action Allow
```

### Windows Security Features

#### Windows Defender Theory

**Windows Defender Architecture**:
- **Real-time Protection**: On-access scanning
- **Cloud Protection**: Microsoft cloud intelligence
- **Behavior Monitoring**: Suspicious activity detection
- **Network Protection**: Malicious URL blocking
- **Controlled Folder Access**: Ransomware protection

**Detection Technologies**:

**Signature-based Detection**:
- **Definition Files**: Known malware signatures
- **Update Frequency**: Regular signature updates
- **Performance**: Fast scanning với minimal resources
- **Limitations**: Cannot detect zero-day threats

**Heuristic Analysis**:
- **Behavior Analysis**: Suspicious program behavior
- **Code Analysis**: Static analysis của executables
- **Machine Learning**: AI-powered threat detection
- **False Positives**: Balance between detection và usability

**Cloud Protection**:
- **Microsoft Active Protection Service (MAPS)**: Cloud intelligence
- **Real-time Analysis**: Immediate threat assessment
- **Reputation-based**: File và URL reputation scoring
- **Sample Submission**: Automatic malware sample uploading

#### BitLocker Encryption Theory

**BitLocker Architecture**:
- **Full Volume Encryption**: Entire drive encryption
- **Boot Protection**: Secure boot process validation
- **Key Management**: Multiple key protection methods
- **Performance**: Hardware-accelerated encryption

**Encryption Methods**:

**AES Encryption**:
- **AES-128**: Standard encryption strength
- **AES-256**: Enhanced encryption strength
- **XTS-AES**: Stronger mode cho disk encryption
- **CBC Mode**: Legacy mode (less secure)

**Key Protection Methods**:

**TPM (Trusted Platform Module)**:
- **Hardware Security**: Dedicated security chip
- **Key Storage**: Secure key storage
- **Platform Integrity**: Boot process validation
- **Anti-tampering**: Hardware-based protection

**TPM + PIN**:
- **Multi-factor**: TPM + user knowledge
- **Pre-boot Authentication**: PIN required at startup
- **Enhanced Security**: Protection against stolen devices
- **User Experience**: Additional step for users

**Recovery Keys**:
- **Backup Purpose**: Access when primary unlock fails
- **48-digit Key**: Numerical recovery key
- **Storage Options**: Active Directory, USB, cloud
- **Administrative Access**: IT department key management

**USB Key Protection**:
- **Startup Key**: USB device required cho boot
- **Portable**: External key storage
- **Risk**: USB device can be lost
- **Use Case**: Systems without TPM

#### Controlled Folder Access Theory

**Ransomware Protection**:
- **Folder Monitoring**: Protect specific folders
- **Process Whitelisting**: Allow trusted applications
- **Behavioral Analysis**: Detect encryption attempts
- **Real-time Blocking**: Stop unauthorized access

**Protected Folders**:
- **System Folders**: Windows system directories
- **User Data**: Documents, Pictures, Desktop
- **Custom Folders**: User-defined protected areas
- **Inheritance**: Subfolder protection

#### Windows Defender Configuration
```powershell
# Windows Defender status
Get-MpComputerStatus

# Real-time protection
Set-MpPreference -DisableRealtimeMonitoring $false
Set-MpPreference -DisableBehaviorMonitoring $false
Set-MpPreference -DisableOnAccessProtection $false
Set-MpPreference -DisableScanOnRealtimeEnable $false

# Scan configuration
Set-MpPreference -ScanScheduleDay 1  # Sunday
Set-MpPreference -ScanScheduleTime 02:00:00
Set-MpPreference -SignatureScheduleDay 0  # Daily
Set-MpPreference -SignatureScheduleTime 01:00:00

# Exclusions (use carefully)
Add-MpPreference -ExclusionPath "C:\TrustedApp"
Add-MpPreference -ExclusionExtension ".log"
Add-MpPreference -ExclusionProcess "trustedapp.exe"

# Advanced threat protection
Set-MpPreference -EnableControlledFolderAccess Enabled
Set-MpPreference -EnableNetworkProtection Enabled
```

#### BitLocker Encryption
```powershell
# Enable BitLocker
Enable-BitLocker -MountPoint "C:" -EncryptionMethod XtsAes256 -UsedSpaceOnly -TmpProtector

# Add recovery key
Add-BitLockerKeyProtector -MountPoint "C:" -RecoveryKeyProtector
(Get-BitLockerVolume -MountPoint "C:").KeyProtector | Where-Object {$_.KeyProtectorType -eq "RecoveryKey"}

# Backup recovery key to AD (if domain-joined)
Backup-BitLockerKeyProtector -MountPoint "C:" -KeyProtectorId (Get-BitLockerVolume -MountPoint "C:").KeyProtector[1].KeyProtectorId

# BitLocker status
Get-BitLockerVolume
```

### Windows Service Hardening

#### Service Configuration Security
```powershell
# Disable unnecessary services
$servicesToDisable = @(
    "Fax",
    "TelnetServer", 
    "RemoteRegistry",
    "Messenger",
    "NetMeeting Remote Desktop Sharing"
)

foreach ($service in $servicesToDisable) {
    if (Get-Service -Name $service -ErrorAction SilentlyContinue) {
        Set-Service -Name $service -StartupType Disabled
        Stop-Service -Name $service -Force
        Write-Output "Disabled service: $service"
    }
}

# Service account security
# Use managed service accounts or virtual accounts
Set-Service -Name "MyService" -Credential (Get-Credential "NT SERVICE\MyService")

# Service recovery configuration
sc.exe failure "MyService" reset= 86400 actions= restart/60000/restart/60000/run/1000
```

## 🔐 3. Advanced Security Measures

#### Advanced Threat Landscape Theory

**Advanced Persistent Threats (APTs)**:
- **Characteristics**: Long-term, stealthy, sophisticated attacks
- **Targets**: High-value organizations, government, critical infrastructure
- **Tactics**: Social engineering, zero-day exploits, living-off-the-land
- **Objectives**: Data theft, espionage, disruption, financial gain

**Attack Kill Chain**:
1. **Reconnaissance**: Target identification và intelligence gathering
2. **Weaponization**: Exploit coupling với backdoor payload
3. **Delivery**: Transmission của weapon to target environment
4. **Exploitation**: Code execution on victim's system
5. **Installation**: Installation của remote access trojan
6. **Command & Control**: Establish command channel
7. **Actions on Objectives**: Data exfiltration, lateral movement

**MITRE ATT&CK Framework**:
- **Tactics**: High-level goals (Initial Access, Execution, Persistence)
- **Techniques**: How tactics are achieved
- **Procedures**: Specific implementations by threat actors
- **Mitigation**: Defensive measures against techniques

#### Security Operations Center (SOC) Theory

**SOC Functions**:
- **Monitoring**: 24/7 security event monitoring
- **Detection**: Identify security incidents
- **Analysis**: Investigate và assess threats
- **Response**: Coordinate incident response
- **Threat Hunting**: Proactive threat discovery

**SOC Tiers**:
- **Tier 1**: Alert triage và initial investigation
- **Tier 2**: Deep analysis và threat correlation
- **Tier 3**: Expert analysis và threat hunting
- **Management**: SOC operations oversight

**Security Orchestration, Automation and Response (SOAR)**:
- **Orchestration**: Coordinate security tools
- **Automation**: Automate repetitive tasks
- **Response**: Standardized incident response
- **Playbooks**: Documented response procedures

### Intrusion Detection Systems

#### IDS/IPS Architecture Theory

**Detection Methodologies**:

**Signature-based Detection**:
- **Pattern Matching**: Known attack signatures
- **Rule Database**: Continuously updated rules
- **Low False Positives**: High accuracy cho known threats
- **Limitations**: Cannot detect unknown attacks

**Anomaly-based Detection**:
- **Baseline Establishment**: Normal behavior patterns
- **Statistical Analysis**: Deviation detection
- **Machine Learning**: Adaptive learning systems
- **Challenges**: High false positive rates

**Behavior-based Detection**:
- **User Behavior**: Establish user activity patterns
- **Entity Behavior**: Monitor system behavior
- **Contextual Analysis**: Consider environmental factors
- **Adaptive**: Learn và adapt to changes

#### Network IDS vs Host IDS

**Network IDS (NIDS)**:
- **Deployment**: Network chokepoints và segments
- **Scope**: Network-wide visibility
- **Data Source**: Network traffic analysis
- **Limitations**: Encrypted traffic blindness

**Host IDS (HIDS)**:
- **Deployment**: Individual systems
- **Scope**: Deep host visibility
- **Data Source**: System logs, file changes, process activity
- **Advantages**: Encrypted traffic visibility

**Hybrid Approaches**:
- **SIEM Integration**: Centralized log management
- **Correlation**: Cross-reference NIDS và HIDS data
- **Comprehensive Coverage**: Network + host visibility
- **Unified Response**: Coordinated incident response

#### OSSEC HIDS Theory

**OSSEC Architecture**:
- **Manager**: Central collection và analysis
- **Agents**: Deployed on monitored systems
- **Agentless**: Remote monitoring via SSH/WMI
- **Database**: Log storage và analysis

**Detection Capabilities**:
- **Log Analysis**: Real-time log monitoring
- **File Integrity Monitoring**: Change detection
- **Rootkit Detection**: System compromise identification
- **Active Response**: Automated threat response

**Alert Correlation**:
- **Rule Chaining**: Multiple events correlation
- **Frequency Analysis**: Anomalous event frequency
- **Threshold Detection**: Event count thresholds
- **Time-based Correlation**: Time window analysis

#### OSSEC Installation và Configuration (Linux)
```bash
# Install OSSEC
wget https://github.com/ossec/ossec-hids/archive/3.7.0.tar.gz
tar -xzf 3.7.0.tar.gz
cd ossec-hids-3.7.0
./install.sh

# OSSEC configuration (/var/ossec/etc/ossec.conf)
<ossec_config>
  <global>
    <email_notification>yes</email_notification>
    <email_to>admin@company.com</email_to>
    <smtp_server>localhost</smtp_server>
    <email_from>ossec@server.com</email_from>
    <email_maxperhour>5</email_maxperhour>
  </global>

  <rules>
    <include>rules_config.xml</include>
    <include>pam_rules.xml</include>
    <include>sshd_rules.xml</include>
    <include>telnetd_rules.xml</include>
    <include>syslog_rules.xml</include>
    <include>arpwatch_rules.xml</include>
    <include>symantec-av_rules.xml</include>
    <include>symantec-ws_rules.xml</include>
    <include>pix_rules.xml</include>
    <include>named_rules.xml</include>
    <include>smbd_rules.xml</include>
    <include>vsftpd_rules.xml</include>
    <include>pure-ftpd_rules.xml</include>
    <include>proftpd_rules.xml</include>
    <include>ms_ftpd_rules.xml</include>
    <include>ftpd_rules.xml</include>
    <include>hordeimp_rules.xml</include>
    <include>roundcube_rules.xml</include>
    <include>wordpress_rules.xml</include>
    <include>cimserver_rules.xml</include>
    <include>vpopmail_rules.xml</include>
    <include>vmpop3d_rules.xml</include>
    <include>courier_rules.xml</include>
    <include>web_rules.xml</include>
    <include>web_appsec_rules.xml</include>
    <include>apache_rules.xml</include>
    <include>nginx_rules.xml</include>
    <include>php_rules.xml</include>
    <include>mysql_rules.xml</include>
    <include>postgresql_rules.xml</include>
    <include>ids_rules.xml</include>
    <include>squid_rules.xml</include>
    <include>firewall_rules.xml</include>
    <include>cisco-ios_rules.xml</include>
    <include>netscreenfw_rules.xml</include>
    <include>sonicwall_rules.xml</include>
    <include>postfix_rules.xml</include>
    <include>sendmail_rules.xml</include>
    <include>imapd_rules.xml</include>
    <include>mailscanner_rules.xml</include>
    <include>dovecot_rules.xml</include>
    <include>ms-exchange_rules.xml</include>
    <include>racoon_rules.xml</include>
    <include>vpn_concentrator_rules.xml</include>
    <include>spamd_rules.xml</include>
    <include>msauth_rules.xml</include>
    <include>mcafee_av_rules.xml</include>
    <include>trend-osce_rules.xml</include>
    <include>ms-se_rules.xml</include>
    <include>zeus_rules.xml</include>
    <include>solaris_bsm_rules.xml</include>
    <include>vmware_rules.xml</include>
    <include>ms_dhcp_rules.xml</include>
    <include>asterisk_rules.xml</include>
    <include>ossec_rules.xml</include>
    <include>attack_rules.xml</include>
    <include>local_rules.xml</include>
  </rules>

  <syscheck>
    <frequency>79200</frequency>
    <directories check_all="yes">/etc,/usr/bin,/usr/sbin</directories>
    <directories check_all="yes">/bin,/sbin,/boot</directories>
    <ignore>/etc/mtab</ignore>
    <ignore>/etc/hosts.deny</ignore>
    <ignore>/etc/mail/statistics</ignore>
    <ignore>/etc/random-seed</ignore>
    <ignore>/etc/random.seed</ignore>
    <ignore>/etc/adjtime</ignore>
    <ignore>/etc/httpd/logs</ignore>
    <ignore>/etc/utmpx</ignore>
    <ignore>/etc/wtmpx</ignore>
    <ignore>/etc/cups/certs</ignore>
    <ignore>/etc/dumpdates</ignore>
    <ignore>/etc/svc/volatile</ignore>
  </syscheck>

  <rootcheck>
    <rootkit_files>/var/ossec/etc/shared/rootkit_files.txt</rootkit_files>
    <rootkit_trojans>/var/ossec/etc/shared/rootkit_trojans.txt</rootkit_trojans>
    <system_audit>/var/ossec/etc/shared/system_audit_rcl.txt</system_audit>
    <system_audit>/var/ossec/etc/shared/system_audit_ssh.txt</system_audit>
    <system_audit>/var/ossec/etc/shared/cis_debian_linux_rcl.txt</system_audit>
    <system_audit>/var/ossec/etc/shared/cis_rhel_linux_rcl.txt</system_audit>
    <system_audit>/var/ossec/etc/shared/cis_rhel5_linux_rcl.txt</system_audit>
  </rootcheck>

  <localfile>
    <log_format>syslog</log_format>
    <location>/var/log/messages</location>
  </localfile>

  <localfile>
    <log_format>syslog</log_format>
    <location>/var/log/secure</location>
  </localfile>

  <localfile>
    <log_format>syslog</log_format>
    <location>/var/log/maillog</location>
  </localfile>

  <localfile>
    <log_format>apache</log_format>
    <location>/var/log/httpd/access_log</location>
  </localfile>

  <localfile>
    <log_format>apache</log_format>
    <location>/var/log/httpd/error_log</location>
  </localfile>
</ossec_config>
```

### Security Monitoring Scripts

#### Comprehensive Security Audit Script (Linux)
```bash
#!/bin/bash
# security_audit.sh - Comprehensive security audit

AUDIT_LOG="/var/log/security_audit_$(date +%Y%m%d_%H%M%S).log"
HOSTNAME=$(hostname)

echo "=== SECURITY AUDIT REPORT ===" | tee $AUDIT_LOG
echo "Hostname: $HOSTNAME" | tee -a $AUDIT_LOG
echo "Date: $(date)" | tee -a $AUDIT_LOG
echo "Auditor: $(whoami)" | tee -a $AUDIT_LOG
echo "" | tee -a $AUDIT_LOG

# System information
echo "=== SYSTEM INFORMATION ===" | tee -a $AUDIT_LOG
uname -a | tee -a $AUDIT_LOG
cat /etc/os-release | tee -a $AUDIT_LOG
uptime | tee -a $AUDIT_LOG
echo "" | tee -a $AUDIT_LOG

# User accounts audit
echo "=== USER ACCOUNTS AUDIT ===" | tee -a $AUDIT_LOG
echo "Users with UID 0 (root privileges):" | tee -a $AUDIT_LOG
awk -F: '($3 == 0) {print $1}' /etc/passwd | tee -a $AUDIT_LOG
echo "" | tee -a $AUDIT_LOG

echo "Users with empty passwords:" | tee -a $AUDIT_LOG
awk -F: '($2 == "") {print $1}' /etc/shadow | tee -a $AUDIT_LOG
echo "" | tee -a $AUDIT_LOG

echo "Password aging information:" | tee -a $AUDIT_LOG
for user in $(awk -F: '($3 >= 1000) {print $1}' /etc/passwd); do
    echo "User: $user" | tee -a $AUDIT_LOG
    chage -l $user | tee -a $AUDIT_LOG
    echo "" | tee -a $AUDIT_LOG
done

# File permissions audit
echo "=== FILE PERMISSIONS AUDIT ===" | tee -a $AUDIT_LOG
echo "World-writable files:" | tee -a $AUDIT_LOG
find / -type f -perm -002 2>/dev/null | head -20 | tee -a $AUDIT_LOG
echo "" | tee -a $AUDIT_LOG

echo "SUID files:" | tee -a $AUDIT_LOG
find / -type f -perm -4000 2>/dev/null | tee -a $AUDIT_LOG
echo "" | tee -a $AUDIT_LOG

echo "SGID files:" | tee -a $AUDIT_LOG
find / -type f -perm -2000 2>/dev/null | tee -a $AUDIT_LOG
echo "" | tee -a $AUDIT_LOG

# Network security audit
echo "=== NETWORK SECURITY AUDIT ===" | tee -a $AUDIT_LOG
echo "Listening services:" | tee -a $AUDIT_LOG
ss -tuln | tee -a $AUDIT_LOG
echo "" | tee -a $AUDIT_LOG

echo "Firewall status:" | tee -a $AUDIT_LOG
if command -v firewall-cmd &> /dev/null; then
    firewall-cmd --list-all | tee -a $AUDIT_LOG
elif command -v iptables &> /dev/null; then
    iptables -L -n | tee -a $AUDIT_LOG
fi
echo "" | tee -a $AUDIT_LOG

# Service audit
echo "=== SERVICE AUDIT ===" | tee -a $AUDIT_LOG
echo "Running services:" | tee -a $AUDIT_LOG
systemctl list-units --type=service --state=running | tee -a $AUDIT_LOG
echo "" | tee -a $AUDIT_LOG

# Log analysis
echo "=== LOG ANALYSIS ===" | tee -a $AUDIT_LOG
echo "Recent authentication failures:" | tee -a $AUDIT_LOG
grep "authentication failure" /var/log/secure | tail -10 | tee -a $AUDIT_LOG
echo "" | tee -a $AUDIT_LOG

echo "Recent sudo usage:" | tee -a $AUDIT_LOG
grep "sudo:" /var/log/secure | tail -10 | tee -a $AUDIT_LOG
echo "" | tee -a $AUDIT_LOG

# Package audit
echo "=== PACKAGE AUDIT ===" | tee -a $AUDIT_LOG
echo "Available security updates:" | tee -a $AUDIT_LOG
if command -v yum &> /dev/null; then
    yum list-security | tee -a $AUDIT_LOG
elif command -v apt &> /dev/null; then
    apt list --upgradable 2>/dev/null | grep -i security | tee -a $AUDIT_LOG
fi

echo "" | tee -a $AUDIT_LOG
echo "=== AUDIT COMPLETE ===" | tee -a $AUDIT_LOG
echo "Report saved to: $AUDIT_LOG" | tee -a $AUDIT_LOG
```

### Compliance và Standards

#### Security Compliance Framework Theory

**Regulatory Compliance**:
- **Legal Requirements**: Government-mandated security standards
- **Industry Standards**: Sector-specific security requirements
- **International Standards**: Global security frameworks
- **Penalties**: Financial và operational consequences

**Common Compliance Frameworks**:

**ISO 27001/27002**:
- **Scope**: Information Security Management System (ISMS)
- **Approach**: Risk-based security management
- **Controls**: 114 security controls across 14 domains
- **Certification**: Third-party audit và certification

**SOC 2 (Service Organization Control 2)**:
- **Purpose**: Service provider security auditing
- **Trust Principles**: Security, Availability, Processing Integrity
- **Types**: Type I (design) vs Type II (operational effectiveness)
- **Audience**: Customers và stakeholders

**PCI DSS (Payment Card Industry Data Security Standard)**:
- **Scope**: Organizations handling cardholder data
- **Requirements**: 12 high-level requirements
- **Validation**: Annual assessment và quarterly scans
- **Levels**: Based on transaction volume

**NIST Cybersecurity Framework**:
- **Functions**: Identify, Protect, Detect, Respond, Recover
- **Implementation Tiers**: Partial, Risk Informed, Repeatable, Adaptive
- **Profiles**: Current state vs target state
- **Voluntary**: Guidance rather than mandate

#### CIS (Center for Internet Security) Benchmarks

**CIS Benchmark Theory**:
- **Consensus-based**: Community-developed standards
- **Platform-specific**: OS và application-specific guidance
- **Prioritized**: Critical Security Controls (CSCs)
- **Implementation Levels**: Profile 1 (basic) vs Profile 2 (defense-in-depth)

**CIS Critical Security Controls**:
1. **Inventory của Hardware Assets**: Know what you're protecting
2. **Inventory của Software Assets**: Authorized và unauthorized software
3. **Continuous Vulnerability Management**: Identify và remediate weaknesses
4. **Controlled Use của Administrative Privileges**: Limit và monitor admin access
5. **Secure Configuration**: Harden systems theo established standards

**Implementation Methodology**:
- **Assessment**: Current state analysis
- **Gap Analysis**: Identify compliance gaps
- **Remediation Planning**: Prioritized improvement plan
- **Implementation**: Execute security improvements
- **Monitoring**: Continuous compliance monitoring

#### NIST Special Publication 800-53

**Security Control Framework**:
- **Control Families**: 20 families of security controls
- **Control Baselines**: Low, Moderate, High impact systems
- **Control Enhancement**: Additional security measures
- **Assessment Procedures**: Methods để evaluate effectiveness

**Control Categories**:
- **Technical Controls**: Automated safeguards
- **Administrative Controls**: Policies và procedures
- **Physical Controls**: Environmental protections

#### CIS Benchmarks Implementation
```bash
# CIS Benchmark automation script
#!/bin/bash
# cis_hardening.sh - CIS Benchmark hardening

# 1.1.1.1 Disable unused filesystems
echo "install cramfs /bin/true" >> /etc/modprobe.d/CIS.conf
echo "install freevxfs /bin/true" >> /etc/modprobe.d/CIS.conf
echo "install jffs2 /bin/true" >> /etc/modprobe.d/CIS.conf
echo "install hfs /bin/true" >> /etc/modprobe.d/CIS.conf
echo "install hfsplus /bin/true" >> /etc/modprobe.d/CIS.conf

# 1.4.1 Set permissions on /etc/motd
chmod 644 /etc/motd

# 1.4.2 Set permissions on /etc/issue
chmod 644 /etc/issue

# 1.4.3 Set permissions on /etc/issue.net
chmod 644 /etc/issue.net

# 2.2.2 Disable xinetd
systemctl disable xinetd

# 2.2.7 Disable NFS và RPC
systemctl disable nfs
systemctl disable rpcbind

# 3.1.1 Disable IP forwarding
echo "net.ipv4.ip_forward = 0" >> /etc/sysctl.conf

# 3.1.2 Disable send packet redirects
echo "net.ipv4.conf.all.send_redirects = 0" >> /etc/sysctl.conf
echo "net.ipv4.conf.default.send_redirects = 0" >> /etc/sysctl.conf

# 3.2.1 Disable source routed packet acceptance
echo "net.ipv4.conf.all.accept_source_route = 0" >> /etc/sysctl.conf
echo "net.ipv4.conf.default.accept_source_route = 0" >> /etc/sysctl.conf

# 3.2.2 Disable ICMP redirects acceptance
echo "net.ipv4.conf.all.accept_redirects = 0" >> /etc/sysctl.conf
echo "net.ipv4.conf.default.accept_redirects = 0" >> /etc/sysctl.conf

# 3.2.4 Log suspicious packets
echo "net.ipv4.conf.all.log_martians = 1" >> /etc/sysctl.conf
echo "net.ipv4.conf.default.log_martians = 1" >> /etc/sysctl.conf

# Apply sysctl settings
sysctl -p

echo "CIS hardening complete. Please review and test all changes."
```

## 💡 Security Best Practices cho Viettel IDC

### 1. Defense in Depth Strategy
- Multiple layers of security controls
- Network segmentation
- Application-level security
- Data encryption at rest và in transit
- Regular security assessments

### 2. Access Control
- Principle of least privilege
- Role-based access control (RBAC)
- Regular access reviews
- Multi-factor authentication
- Privileged account management

### 3. Monitoring và Incident Response
- 24/7 security monitoring
- Automated threat detection
- Incident response procedures
- Security event correlation
- Regular security drills

### 4. Compliance Management
- Regular compliance audits
- Policy documentation
- Staff security training
- Vulnerability management
- Change management procedures

---
*Security is not a one-time task but an ongoing process. Regular audits, updates, and monitoring are essential for maintaining a secure environment at Viettel IDC.*
