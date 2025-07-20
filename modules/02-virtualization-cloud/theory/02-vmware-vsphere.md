# VMware vSphere Theory - Lý thuyết VMware vSphere

## 🎯 Mục tiêu Học tập
Hiểu sâu về kiến trúc và các components của VMware vSphere, từ ESXi hypervisor đến vCenter management, đáp ứng yêu cầu triển khai enterprise virtualization tại Viettel IDC.

## 🏗️ 1. vSphere Architecture Overview

### vSphere Platform Components

#### Core Infrastructure Components
```
┌─────────────────────────────────────────────────────────┐
│                vSphere Client                          │
├─────────────────────────────────────────────────────────┤
│                vCenter Server                          │
├─────────────────────────────────────────────────────────┤
│     ESXi Host 1    │    ESXi Host 2    │   ESXi Host 3  │
├─────────────────────────────────────────────────────────┤
│              Shared Storage (SAN/NAS)                  │
└─────────────────────────────────────────────────────────┘
```

**vSphere Core Components**:
- **ESXi**: Type-1 hypervisor, bare-metal installation
- **vCenter Server**: Centralized management platform
- **vSphere Client**: HTML5-based management interface
- **vSphere API**: RESTful API cho automation
- **ESXi Shell**: Command-line interface cho troubleshooting

**Extended Components**:
- **vSAN**: Software-defined storage
- **NSX**: Network virtualization platform
- **vRealize Suite**: Cloud management và automation
- **Site Recovery Manager**: Disaster recovery automation
- **vSphere Replication**: VM-level replication

### vSphere Licensing Model

**License Editions**:
- **vSphere Standard**: Basic virtualization features
- **vSphere Enterprise**: Advanced features (vMotion, HA)
- **vSphere Enterprise Plus**: Full feature set (DRS, Storage vMotion)

**Feature Comparison**:
| Feature | Standard | Enterprise | Enterprise Plus |
|---------|----------|------------|-----------------|
| vMotion | ❌ | ✅ | ✅ |
| HA | ❌ | ✅ | ✅ |
| DRS | ❌ | ❌ | ✅ |
| Storage vMotion | ❌ | ❌ | ✅ |
| Distributed Switch | ❌ | ❌ | ✅ |

## 🖥️ 2. ESXi Hypervisor Architecture

### VMkernel Architecture

#### Core VMkernel Components
**VMkernel** là heart của ESXi hypervisor, designed như một microkernel với minimal footprint.

**Key VMkernel Subsystems**:
- **CPU Scheduler**: Manages CPU resources across VMs
- **Memory Manager**: Handles memory allocation và sharing
- **Storage Stack**: Manages storage I/O và protocols
- **Network Stack**: Handles network traffic và protocols
- **Device Drivers**: Hardware abstraction layer

#### CPU Virtualization trong ESXi

**CPU Scheduler Architecture**:
- **Proportional Share Scheduler**: Fair sharing dựa trên shares
- **World Concept**: Basic scheduling unit (VMs, hypervisor tasks)
- **CPU Affinity**: Binding VMs to specific physical CPUs
- **CPU Hot-add**: Dynamic CPU allocation to VMs

**Hardware-Assisted Virtualization**:
- **Intel VT-x/AMD-V**: Hardware virtualization extensions
- **EPT/RVI**: Hardware-assisted memory management
- **VPID/ASID**: Virtual Processor IDs cho TLB efficiency

**CPU Performance Features**:
- **CPU Ready Time**: Time VM waits for physical CPU
- **Co-scheduling**: Synchronous scheduling for SMP VMs
- **CPU Limits/Reservations**: Resource controls
- **Hyperthreading**: Considerations và best practices

#### Memory Virtualization trong ESXi

**Memory Management Techniques**:

**Transparent Page Sharing (TPS)**:
- **Page Deduplication**: Identical pages shared across VMs
- **Security Considerations**: Disabled by default due to security
- **Performance Impact**: CPU overhead for scanning
- **Memory Savings**: Significant savings trong homogeneous environments

**Memory Ballooning**:
- **VMware Tools Balloon Driver**: Guest OS memory reclamation
- **Balloon Target**: Amount of memory to reclaim
- **Guest OS Cooperation**: Relies on guest OS memory management
- **Performance Impact**: May cause guest OS paging

**Memory Compression**:
- **Compression Cache**: Compress less-accessed pages
- **4:1 Compression Ratio**: Typical compression efficiency
- **CPU Trade-off**: CPU cycles for memory savings
- **Performance**: Better than swapping to disk

**Hypervisor Swapping**:
- **Last Resort**: When other techniques insufficient
- **Performance Impact**: Significant performance degradation
- **Swap File Location**: Host swap file storage
- **Avoidance**: Proper capacity planning prevents swapping

**Memory Overcommitment**:
- **Overcommit Ratios**: 1.2-1.5x typical, up to 2x possible
- **Memory Reservations**: Guaranteed memory allocation
- **Memory Limits**: Maximum memory allocation
- **Memory Shares**: Relative priority during contention

#### Storage Architecture trong ESXi

**Storage Stack Components**:
- **VMkernel Storage Stack**: Native storage framework
- **PSA (Pluggable Storage Architecture)**: Modular storage framework
- **Device Drivers**: Hardware-specific storage drivers
- **Multipathing**: Path management cho redundancy

**Storage Protocols Support**:

**Block Storage Protocols**:
- **Fibre Channel (FC)**: High-performance SAN protocol
- **iSCSI**: IP-based storage protocol
- **FCoE**: Fibre Channel over Ethernet
- **NVMe over Fabrics**: Next-generation storage protocol

**File Storage Protocols**:
- **NFS v3/v4.1**: Network File System support
- **vSAN**: VMware's software-defined storage
- **vVols**: Virtual Volumes for array integration

**VMFS (Virtual Machine File System)**:
- **Cluster File System**: Multiple hosts access simultaneously
- **Lock Management**: File-level locking mechanisms
- **Journaling**: Metadata consistency và recovery
- **Block Size**: Variable block sizes (1MB, 2MB, 4MB, 8MB)

#### Network Architecture trong ESXi

**Virtual Networking Components**:

**vSphere Standard Switch (vSS)**:
- **Host-level**: Each ESXi host has own vSS
- **Port Groups**: Network configuration templates
- **Uplinks**: Physical network connections
- **VLAN Support**: 802.1Q VLAN tagging

**vSphere Distributed Switch (vDS)**:
- **Cluster-level**: Spans multiple ESXi hosts
- **Centralized Management**: Single point of configuration
- **Advanced Features**: NetFlow, port mirroring, LACP
- **Network I/O Control**: Bandwidth management

**Virtual Network Components**:
- **Virtual NICs (vNICs)**: VM network interfaces
- **vmknic**: VMkernel network interfaces
- **Port Groups**: Network policy configuration
- **Uplink Adapters**: Physical network connections

**Network I/O Control (NIOC)**:
- **Bandwidth Allocation**: Guaranteed bandwidth cho traffic types
- **Traffic Types**: Management, vMotion, vSAN, VM traffic
- **QoS Policies**: Quality of Service configuration
- **Resource Pools**: Network resource allocation

### ESXi Installation và Configuration

#### Installation Methods

**Interactive Installation**:
- **Local Media**: DVD/USB installation
- **Hardware Compatibility**: Check HCL (Hardware Compatibility List)
- **Installation Process**: Boot from media, follow wizard
- **Post-installation**: Network configuration, licensing

**Scripted Installation**:
- **Kickstart Script**: Automated installation configuration
- **PXE Boot**: Network-based installation
- **Auto Deploy**: Stateless ESXi deployment
- **Host Profiles**: Standardized configuration deployment

**ESXi Installation Requirements**:
- **CPU**: 64-bit x86 processor với VT-x/AMD-V
- **Memory**: 4GB minimum, 8GB+ recommended
- **Storage**: 8GB minimum cho ESXi installation
- **Network**: At least one Gigabit NIC

#### ESXi Configuration

**Management Network Configuration**:
- **Management vmknic**: ESXi management traffic
- **IP Configuration**: Static IP recommended
- **VLAN Tagging**: Management network VLAN
- **Default Gateway**: Network routing configuration

**Storage Configuration**:
- **Local Storage**: VMFS datastore creation
- **Shared Storage**: SAN/NAS configuration
- **Storage Adapters**: FC HBA, iSCSI, NFS configuration
- **Path Management**: Multipathing configuration

**Security Configuration**:
- **Firewall**: ESXi firewall service configuration
- **SSH**: Secure Shell access (disable in production)
- **Lockdown Mode**: Restrict local access
- **Certificate Management**: SSL certificate configuration

## 🏢 3. vCenter Server Architecture

### vCenter Server Appliance (VCSA)

#### VCSA Architecture Components

**Platform Services Controller (PSC)**:
- **Single Sign-On (SSO)**: Authentication service
- **License Service**: License management
- **Certificate Authority**: SSL certificate management
- **VMware Directory Service**: LDAP directory

**vCenter Server Services**:
- **Inventory Service**: Object management và relationships
- **vCenter Server**: Core management functionality
- **Content Library**: Template và ISO management
- **Auto Deploy**: Stateless ESXi deployment

**Embedded vs External PSC**:
| Deployment | Embedded PSC | External PSC |
|------------|--------------|--------------|
| Complexity | Simple | Complex |
| Scalability | Limited | High |
| HA | vCenter HA | PSC HA + vCenter HA |
| Use Case | Small-medium | Large enterprise |

#### vCenter Server Deployment

**VCSA Deployment Process**:
1. **Stage 1**: Deploy OVA template
2. **Stage 2**: Configure VCSA services
3. **Post-deployment**: Additional configuration

**Deployment Sizes**:
- **Tiny**: Up to 10 hosts, 100 VMs
- **Small**: Up to 100 hosts, 1,000 VMs
- **Medium**: Up to 400 hosts, 4,000 VMs
- **Large**: Up to 1,000 hosts, 10,000 VMs
- **X-Large**: Up to 2,000 hosts, 35,000 VMs

**Storage Requirements**:
| Size | vCPU | Memory | Storage |
|------|------|--------|---------|
| Tiny | 2 | 12GB | 415GB |
| Small | 4 | 16GB | 480GB |
| Medium | 8 | 24GB | 700GB |
| Large | 16 | 32GB | 1.2TB |
| X-Large | 24 | 48GB | 1.7TB |

### Single Sign-On (SSO) Architecture

#### SSO Domain Structure

**SSO Domain Components**:
- **SSO Domain**: Authentication domain (e.g., vsphere.local)
- **Identity Sources**: Authentication backends
- **Users và Groups**: SSO users và group memberships
- **Solution Users**: Service accounts cho vSphere services

**Identity Sources**:
- **localos**: Local system users
- **vsphere.local**: Built-in SSO domain
- **Active Directory**: Domain integration
- **OpenLDAP**: LDAP directory integration

#### Permission Model

**vCenter Permissions Structure**:
- **Objects**: vCenter inventory objects
- **Roles**: Collections of privileges
- **Principals**: Users hoặc groups
- **Permissions**: Object + Role + Principal combination

**Default Roles**:
- **Administrator**: Full administrative access
- **Read-only**: View-only access
- **No access**: Explicitly deny access
- **Virtual machine power user**: VM operational access
- **Datastore consumer**: Datastore access for VMs

**Permission Inheritance**:
- **Propagation**: Permissions inherit down object hierarchy
- **Override**: Child permissions can override parent permissions
- **Effective Permissions**: Combination of direct và inherited permissions

### Inventory Management

#### vCenter Object Hierarchy
```
vCenter Server
├── Datacenters
│   ├── Clusters
│   │   ├── ESXi Hosts
│   │   └── Virtual Machines
│   ├── Resource Pools
│   └── VM Templates
├── Storage
│   ├── Datastores
│   └── Storage Policies
└── Networks
    ├── Standard Switches
    ├── Distributed Switches
    └── Port Groups
```

**Datacenter Objects**:
- **Datacenter**: Top-level container for hosts và VMs
- **Folders**: Organizational containers
- **Clusters**: Collections của ESXi hosts
- **Resource Pools**: Hierarchical resource allocation

**Virtual Machine Objects**:
- **Virtual Machines**: Guest operating systems
- **Templates**: Master images cho VM deployment
- **vApps**: Multi-tier application containers
- **Snapshots**: Point-in-time VM states

## 🔄 4. VM Lifecycle Management

### VM Creation và Deployment

#### VM Creation Methods

**New Virtual Machine Wizard**:
- **Compatibility**: Hardware version selection
- **Guest OS**: Operating system selection
- **Hardware**: CPU, memory, storage configuration
- **Network**: Network adapter configuration

**Template-based Deployment**:
- **VM Templates**: Master VM images
- **Customization Specs**: OS customization automation
- **Clone Operations**: Full clones vs linked clones
- **Deployment Speed**: Faster than manual creation

**OVF/OVA Deployment**:
- **OVF (Open Virtualization Format)**: Standard VM package format
- **OVA (Open Virtual Appliance)**: Single-file OVF package
- **Portability**: Cross-platform VM deployment
- **Vendor Appliances**: Pre-built virtual appliances

#### VM Hardware Configuration

**Virtual Hardware Versions**:
- **Hardware Version**: VM compatibility level
- **Feature Support**: Newer versions support more features
- **Backwards Compatibility**: Newer hosts support older versions
- **Upgrade Process**: Hardware version upgrade process

**CPU Configuration**:
- **vCPU Allocation**: Virtual CPU assignment
- **CPU Reservations**: Guaranteed CPU allocation
- **CPU Limits**: Maximum CPU usage
- **CPU Shares**: Relative CPU priority

**Memory Configuration**:
- **Memory Size**: VM memory allocation
- **Memory Reservations**: Guaranteed memory allocation
- **Memory Limits**: Maximum memory usage
- **Memory Shares**: Relative memory priority

**Storage Configuration**:
- **Virtual Disks**: VMDK file format
- **Disk Types**: Thick/thin provisioning
- **SCSI Controllers**: LSI Logic, Paravirtual SCSI
- **Storage Policies**: VM storage requirements

### VM Templates và Cloning

#### Template Management

**Template Creation Process**:
1. **Prepare Source VM**: Install OS, applications, sysprep
2. **Convert to Template**: Mark VM as template
3. **Template Storage**: Store trong Content Library
4. **Version Control**: Maintain multiple template versions

**Template Best Practices**:
- **Minimal Installation**: Only necessary components
- **Security Hardening**: Apply security baselines
- **Regular Updates**: Keep templates current
- **Documentation**: Template specifications và change log

#### Cloning Operations

**Full Clone**:
- **Independent Copy**: Complete VM copy
- **Storage Requirements**: Full storage allocation
- **Performance**: No dependency on original
- **Use Cases**: Production VMs, isolation required

**Linked Clone**:
- **Shared Base**: Shares disk với parent/template
- **Storage Efficiency**: Significant storage savings
- **Performance**: Potential I/O impact on shared storage
- **Use Cases**: Development, testing, VDI

**Instant Clone**:
- **Memory Fork**: Fork running VM's memory state
- **Rapid Deployment**: Near-instantaneous deployment
- **Use Cases**: Horizon VDI, development environments
- **Requirements**: vSphere 6.0+ và specific use cases

### Snapshot Management

#### Snapshot Technology

**Snapshot Components**:
- **Base Disk**: Original VMDK file (read-only)
- **Delta Disk**: Changes since snapshot (read-write)
- **Snapshot File**: VM state và configuration
- **Memory File**: VM memory state (if memory included)

**Snapshot Chain**:
```
Base VMDK → Snapshot 1 → Snapshot 2 → Current State
   (RO)        (RW)         (RW)         (RW)
```

**Snapshot Performance Impact**:
- **Write Performance**: Overhead for delta tracking
- **Chain Length**: Longer chains = more overhead
- **Consolidation**: Merge snapshots to improve performance
- **Storage Growth**: Delta files can grow significantly

#### Snapshot Best Practices

**When to Use Snapshots**:
- **Pre-change Backup**: Before major changes
- **Testing**: Rollback capability
- **Temporary**: Short-term use only
- **Automation**: Scripted backup solutions

**Snapshot Limitations**:
- **Performance Impact**: Degrades VM performance
- **Storage Growth**: Unpredictable storage usage
- **Chain Limits**: Maximum recommended chain length
- **RDM Limitations**: Raw Device Mapping restrictions

## 🔧 5. vMotion Technology

### vMotion Architecture

#### vMotion Process

**Pre-migration Checks**:
- **Compatibility**: CPU compatibility checks
- **Resources**: Target host resource availability
- **Network**: vMotion network connectivity
- **Storage**: Shared storage accessibility

**Migration Phases**:
1. **Setup Phase**: Establish vMotion connection
2. **Iterative Memory Copy**: Copy VM memory pages
3. **Switchover**: Brief pause to complete migration
4. **Cleanup**: Remove VM from source host

**vMotion Networks**:
- **Dedicated vMotion Network**: Separate network cho vMotion traffic
- **Bandwidth Requirements**: 1GbE minimum, 10GbE recommended
- **Network Isolation**: Separate vMotion traffic from other traffic
- **Security**: Encrypted vMotion (vSphere 6.5+)

#### vMotion Requirements

**CPU Compatibility**:
- **CPU Families**: Same CPU vendor (Intel/AMD)
- **Feature Sets**: Compatible instruction sets
- **EVC (Enhanced vMotion Compatibility)**: CPU masking for compatibility
- **Clock Speed**: No requirement for identical speeds

**Storage Requirements**:
- **Shared Storage**: All hosts must access VM files
- **Storage Protocols**: FC, iSCSI, NFS, vSAN
- **Path Availability**: All hosts must have storage paths
- **Performance**: Adequate storage performance

**Network Requirements**:
- **Layer 2 Connectivity**: Same broadcast domain
- **VLAN Configuration**: Consistent VLAN configuration
- **Network Speed**: Adequate bandwidth cho migration
- **vMotion vmknic**: Dedicated vMotion kernel interface

### Storage vMotion

#### Storage vMotion Process

**Migration Types**:
- **Change Datastore**: Move VM to different datastore
- **Change Format**: Thin ↔ thick provisioning conversion
- **Change Policy**: Storage policy changes
- **Concurrent Operations**: Multiple disk migrations

**Storage vMotion Phases**:
1. **Setup**: Prepare destination storage
2. **Disk Copy**: Copy VM disk contents
3. **Switchover**: Redirect I/O to new location
4. **Cleanup**: Remove old VM files

**Performance Considerations**:
- **I/O Impact**: Additional load on storage systems
- **Network Utilization**: Storage network bandwidth usage
- **Migration Time**: Depends on VM size và storage performance
- **Concurrent Migrations**: Limit concurrent Storage vMotions

### Enhanced vMotion Compatibility (EVC)

#### EVC Concepts

**CPU Masking**:
- **Feature Hiding**: Hide newer CPU features
- **Compatibility**: Enable migration between different CPU generations
- **EVC Modes**: Predefined CPU compatibility levels
- **Cluster-wide**: EVC applied at cluster level

**EVC Modes (Intel)**:
- **Merom**: Core 2 Duo generation
- **Penryn**: Core 2 Duo enhanced
- **Nehalem**: Core i7 generation
- **Westmere**: Newer Core i7
- **Sandy Bridge**: 2nd generation Core
- **Ivy Bridge**: 3rd generation Core
- **Haswell**: 4th generation Core
- **Broadwell**: 5th generation Core
- **Skylake**: 6th generation Core

**EVC Implementation**:
- **Cluster Creation**: Set EVC mode during cluster creation
- **Mode Changes**: Can only increase EVC mode
- **VM Compatibility**: VMs limited to EVC mode features
- **Performance Impact**: Minimal performance impact

## 📈 6. Performance Monitoring và Optimization

### Performance Metrics

#### Key Performance Indicators

**CPU Metrics**:
- **CPU Usage**: Percentage of CPU utilization
- **CPU Ready**: Time VM waits for physical CPU
- **CPU Co-stop**: SMP VM scheduling delays
- **CPU Swap Wait**: Time waiting during memory swapping

**Memory Metrics**:
- **Memory Usage**: Active memory consumption
- **Memory Balloon**: Ballooned memory amount
- **Memory Swapped**: Hypervisor swapped memory
- **Memory Compressed**: Compressed memory amount

**Storage Metrics**:
- **IOPS**: Input/Output Operations Per Second
- **Throughput**: Data transfer rate (MB/s)
- **Latency**: Storage response time (ms)
- **Queue Depth**: Pending I/O operations

**Network Metrics**:
- **Throughput**: Network data transfer rate
- **Packet Loss**: Dropped network packets
- **Network Utilization**: Bandwidth usage percentage
- **Network Errors**: Network transmission errors

#### Performance Troubleshooting

**CPU Performance Issues**:
- **High CPU Ready**: Resource contention, reduce vCPU count
- **CPU Limit Hit**: Increase CPU limit or remove
- **Poor CPU Performance**: Check for CPU affinity settings
- **SMP Performance**: Reduce vCPU count cho single-threaded apps

**Memory Performance Issues**:
- **Memory Overcommitment**: Reduce VM memory allocations
- **Ballooning**: Add host memory or reduce VM allocations
- **Swapping**: Critical - add memory immediately
- **TPS Savings**: Enable TPS if security allows

**Storage Performance Issues**:
- **High Latency**: Check storage array performance
- **Queue Depth**: Adjust queue depth settings
- **IOPS Limits**: Identify storage bottlenecks
- **Multipathing**: Verify proper path configuration

---

*Với kiến thức chi tiết về VMware vSphere, chúng ta có foundation vững chắc để triển khai và quản lý enterprise virtualization infrastructure.*
