# Virtualization Fundamentals - Lý thuyết Cơ bản về Ảo hóa

## 🎯 Mục tiêu Học tập
Hiểu sâu về các khái niệm cơ bản của ảo hóa, từ lý thuyết đến kiến trúc, đáp ứng yêu cầu triển khai hạ tầng ảo hóa tại Viettel IDC.

## 🧠 1. Virtualization Theory Fundamentals

### Khái niệm Ảo hóa (Virtualization)

#### Định nghĩa và Bản chất
**Virtualization** là công nghệ cho phép tạo ra các phiên bản ảo (virtual) của tài nguyên máy tính thay vì sử dụng trực tiếp phần cứng vật lý. Đây là quá trình trừu tượng hóa (abstraction) các tài nguyên vật lý thành các tài nguyên logic.

**Nguyên lý Cốt lõi**:
- **Abstraction**: Tách biệt logical resources khỏi physical resources
- **Isolation**: Cách ly các workloads khỏi nhau
- **Encapsulation**: Đóng gói entire systems thành các files
- **Hardware Independence**: Không phụ thuộc vào specific hardware

#### Lịch sử Phát triển Ảo hóa

**1960s - Mainframe Era**:
- **IBM System/360**: Đầu tiên introduced virtualization concepts
- **Hypervisor Type 1**: CP/CMS (Control Program/Cambridge Monitor System)
- **Purpose**: Share expensive mainframe resources among multiple users

**1990s - x86 Challenges**:
- **x86 Architecture**: Không originally designed cho virtualization
- **Privileged Instructions**: Không thể fully virtualized
- **Performance Issues**: Software emulation was slow

**2000s - Hardware Assistance**:
- **Intel VT-x (2005)**: Intel Virtualization Technology
- **AMD-V (2006)**: AMD Virtualization
- **Hardware Support**: Enabled efficient x86 virtualization

**2010s - Cloud Era**:
- **Public Cloud**: AWS, Azure, Google Cloud
- **Container Revolution**: Docker, Kubernetes
- **Edge Computing**: Virtualization at the edge

#### Business Drivers cho Virtualization

**Cost Reduction**:
- **Server Consolidation**: Reduce physical server count from 10:1 to 20:1 ratios
- **Power Savings**: Significant reduction in electricity costs
- **Space Savings**: Smaller datacenter footprint
- **Cooling Costs**: Reduced heat generation

**Operational Efficiency**:
- **Provisioning Speed**: Minutes instead of weeks for new servers
- **Management**: Centralized management tools
- **Standardization**: Consistent configurations
- **Automation**: Scripted deployment và management

**Business Agility**:
- **Scalability**: Quick scaling up/down
- **Flexibility**: Easy workload migration
- **Innovation**: Faster time-to-market
- **Disaster Recovery**: Simplified DR strategies

### 2. Types of Virtualization

#### Server Virtualization

**Definition**: Partitioning một physical server thành multiple virtual machines, mỗi VM có own OS và applications.

**Key Components**:
- **Hypervisor**: Software layer managing VMs
- **Virtual Machines**: Isolated guest systems
- **Host System**: Physical hardware và hypervisor
- **Guest Systems**: VMs running on hypervisor

**Resource Abstraction**:
- **CPU Virtualization**: Virtual CPUs mapped to physical cores
- **Memory Virtualization**: Virtual memory space cho each VM
- **Storage Virtualization**: Virtual disks backed by physical storage
- **Network Virtualization**: Virtual network interfaces

**Benefits**:
- **Consolidation**: Multiple workloads on single hardware
- **Isolation**: Applications isolated from each other
- **Portability**: VMs can move between hosts
- **Snapshot Capability**: Point-in-time VM states

#### Network Virtualization

**Software-Defined Networking (SDN)**:
- **Control Plane**: Centralized network control logic
- **Data Plane**: Packet forwarding infrastructure
- **APIs**: Programmable network interfaces
- **Benefits**: Centralized control, policy consistency, automation

**Virtual LANs (VLANs)**:
- **IEEE 802.1Q**: VLAN tagging standard
- **Logical Segmentation**: Separate broadcast domains
- **Security**: Network isolation
- **Flexibility**: Dynamic network reconfiguration

**Overlay Networks**:
- **VXLAN**: Virtual Extensible LAN
- **NVGRE**: Network Virtualization using Generic Routing Encapsulation
- **STT**: Stateless Transport Tunneling
- **Benefits**: Multi-tenancy, scalability, mobility

#### Storage Virtualization

**Block-level Virtualization**:
- **Storage Arrays**: Multiple storage devices presented as one
- **LUN Masking**: Logical Unit Number management
- **Multipathing**: Multiple paths to storage
- **Benefits**: Simplified management, improved utilization

**File-level Virtualization**:
- **Global Namespace**: Single view of distributed files
- **Location Independence**: Files can move transparently
- **Protocol Translation**: NFS ↔ CIFS translation
- **Benefits**: Simplified file management, mobility

**Software-Defined Storage (SDS)**:
- **Storage Abstraction**: Separate control from storage hardware
- **Policy-driven**: Automated storage provisioning
- **Scale-out Architecture**: Horizontal scaling
- **Benefits**: Flexibility, cost reduction, automation

#### Desktop Virtualization

**Virtual Desktop Infrastructure (VDI)**:
- **Centralized Desktops**: Desktop VMs in datacenter
- **Thin Clients**: Lightweight endpoint devices
- **Session Management**: User session handling
- **Benefits**: Centralized management, security, BYOD support

**Application Virtualization**:
- **Application Streaming**: Apps delivered on-demand
- **Application Isolation**: Apps run in isolated environments
- **Compatibility**: Legacy application support
- **Benefits**: Simplified deployment, reduced conflicts

### 3. Hypervisor Architecture

#### Type 1 Hypervisor (Bare Metal)

**Architecture Overview**:
```
┌─────────────────────────────────────┐
│          Virtual Machines          │
├─────────────────────────────────────┤
│            Hypervisor               │
├─────────────────────────────────────┤
│         Physical Hardware           │
└─────────────────────────────────────┘
```

**Characteristics**:
- **Direct Hardware Access**: Hypervisor chạy directly on hardware
- **Minimal Host OS**: Hypervisor itself is the host OS
- **Better Performance**: Lower overhead, better resource access
- **Enhanced Security**: Smaller attack surface

**Examples**:
- **VMware ESXi**: Enterprise-grade hypervisor
- **Microsoft Hyper-V**: Windows Server hypervisor
- **Citrix XenServer**: Open-source based hypervisor
- **Red Hat KVM**: Linux-based hypervisor

**Use Cases**:
- **Production Environments**: Mission-critical workloads
- **Enterprise Datacenters**: Large-scale deployments
- **Cloud Infrastructure**: Public cloud providers
- **High-Performance Computing**: Resource-intensive applications

#### Type 2 Hypervisor (Hosted)

**Architecture Overview**:
```
┌─────────────────────────────────────┐
│          Virtual Machines          │
├─────────────────────────────────────┤
│            Hypervisor               │
├─────────────────────────────────────┤
│           Host OS                   │
├─────────────────────────────────────┤
│         Physical Hardware           │
└─────────────────────────────────────┘
```

**Characteristics**:
- **Host OS Dependency**: Runs on top of existing OS
- **Easier Installation**: Standard application installation
- **Hardware Compatibility**: Leverages host OS drivers
- **Higher Overhead**: Additional OS layer

**Examples**:
- **VMware Workstation**: Professional desktop virtualization
- **Oracle VirtualBox**: Open-source virtualization
- **Parallels Desktop**: Mac virtualization
- **Microsoft Virtual PC**: Windows virtualization

**Use Cases**:
- **Development Environment**: Testing và development
- **Desktop Virtualization**: Running multiple OSes
- **Training Labs**: Educational environments
- **Personal Use**: Home users running multiple OSes

#### Hypervisor Comparison

| Aspect | Type 1 (Bare Metal) | Type 2 (Hosted) |
|--------|---------------------|------------------|
| Performance | High (direct hardware) | Lower (OS overhead) |
| Security | Better (smaller TCB) | Lower (larger attack surface) |
| Management | Requires specialized tools | Uses host OS tools |
| Installation | Complex | Simple |
| Hardware Support | Limited | Extensive |
| Use Case | Production | Development/Testing |

### 4. Hardware-Assisted Virtualization

#### CPU Virtualization Extensions

**Intel VT-x (Virtualization Technology)**:
- **VMX Operation**: Virtual Machine Extensions
- **Root Mode**: Hypervisor execution mode
- **Non-root Mode**: Guest VM execution mode
- **VM Entry/Exit**: Transitions between modes

**AMD-V (AMD Virtualization)**:
- **SVM**: Secure Virtual Machine extensions
- **Host Mode**: Hypervisor execution
- **Guest Mode**: VM execution
- **VMCB**: Virtual Machine Control Block

**Benefits of Hardware Assistance**:
- **Performance**: Near-native execution speed
- **Simplicity**: Simplified hypervisor design
- **Security**: Hardware-enforced isolation
- **Compatibility**: Full x86 instruction support

#### Memory Virtualization

**Memory Management Challenges**:
- **Address Translation**: Guest virtual → Guest physical → Host physical
- **TLB Management**: Translation Lookaside Buffer overhead
- **Page Table Walks**: Multiple levels of translation
- **Memory Protection**: Isolation between guests

**Intel EPT (Extended Page Tables)**:
- **Hardware MMU**: Memory Management Unit support
- **Two-level Translation**: Guest và host page tables
- **Reduced Overhead**: Hardware handles translation
- **Better Performance**: Fewer VM exits

**AMD RVI (Rapid Virtualization Indexing)**:
- **Nested Page Tables**: AMD's equivalent to EPT
- **Hardware Acceleration**: MMU-assisted translation
- **Performance Improvement**: Reduced software overhead
- **Scalability**: Better support for multiple VMs

#### I/O Virtualization

**Traditional I/O Virtualization Challenges**:
- **Device Emulation**: Software emulation overhead
- **Trap and Emulate**: Performance penalties
- **Driver Complexity**: Multiple device drivers
- **Scalability**: Limited by hypervisor

**SR-IOV (Single Root I/O Virtualization)**:
- **Hardware Support**: PCIe standard
- **Physical Function (PF)**: Primary device function
- **Virtual Functions (VFs)**: Lightweight PCIe functions
- **Direct Assignment**: VMs access hardware directly

**IOMMU (I/O Memory Management Unit)**:
- **DMA Protection**: Direct Memory Access isolation
- **Address Translation**: I/O address translation
- **Intel VT-d**: Intel's IOMMU implementation
- **AMD-Vi**: AMD's IOMMU implementation

### 5. Virtualization Performance Considerations

#### Resource Overhead

**CPU Overhead**:
- **Hypervisor Overhead**: 2-10% typical overhead
- **Context Switching**: VM to hypervisor transitions
- **Interrupt Handling**: Virtual interrupt processing
- **Scheduling**: VM CPU scheduling algorithms

**Memory Overhead**:
- **Hypervisor Memory**: Memory used by hypervisor
- **VM Memory**: Guest OS và application memory
- **Memory Ballooning**: Dynamic memory allocation
- **Memory Sharing**: Deduplication techniques

**Storage Overhead**:
- **Virtual Disk Format**: VMDK, VHD, QCOW2
- **Snapshot Storage**: Additional storage requirements
- **I/O Path**: Additional layers trong I/O stack
- **Storage Protocols**: Network storage overhead

**Network Overhead**:
- **Virtual Switching**: Software-based switching
- **Network Protocols**: Tunneling và encapsulation
- **Bandwidth Sharing**: Multiple VMs sharing links
- **Latency**: Additional network layers

#### Performance Optimization Techniques

**CPU Optimization**:
- **CPU Affinity**: Bind VMs to specific CPUs
- **NUMA Awareness**: Optimize for NUMA topology
- **CPU Hot-add**: Dynamic CPU allocation
- **Hyperthreading**: Considerations và best practices

**Memory Optimization**:
- **Memory Overcommitment**: Allocate more than physical
- **Transparent Page Sharing**: Deduplicate identical pages
- **Memory Compression**: Compress less-used pages
- **NUMA Optimization**: Memory locality optimization

**Storage Optimization**:
- **Thin Provisioning**: Allocate storage on-demand
- **Storage vMotion**: Live storage migration
- **Flash Storage**: SSD acceleration
- **Storage Array Integration**: Native array features

**Network Optimization**:
- **SR-IOV**: Hardware-assisted networking
- **Network Load Balancing**: Distribute traffic
- **Jumbo Frames**: Larger frame sizes
- **RDMA**: Remote Direct Memory Access

### 6. Security Implications

#### Hypervisor Security

**Attack Vectors**:
- **VM Escape**: Breaking out of VM isolation
- **Hypervisor Bugs**: Vulnerabilities trong hypervisor code
- **Side-channel Attacks**: Information leakage
- **Management Interface**: Attacks on management tools

**Security Best Practices**:
- **Minimal Hypervisor**: Reduce attack surface
- **Regular Updates**: Patch management
- **Access Control**: Restrict hypervisor access
- **Monitoring**: Security event monitoring

#### VM-to-VM Security

**Isolation Mechanisms**:
- **Memory Isolation**: Separate memory spaces
- **CPU Isolation**: Scheduler isolation
- **Network Isolation**: Virtual network segmentation
- **Storage Isolation**: Separate storage access

**Security Challenges**:
- **Shared Resources**: Resource contention
- **Covert Channels**: Information leakage paths
- **VM Migration**: Security during live migration
- **Snapshot Security**: Protecting VM snapshots

### 7. Management and Orchestration

#### Lifecycle Management

**VM Provisioning**:
- **Template-based**: Standardized VM creation
- **Clone Operations**: Full và linked clones
- **Automated Deployment**: Script-based provisioning
- **Self-service**: User-initiated provisioning

**Configuration Management**:
- **Guest Customization**: OS configuration automation
- **Application Deployment**: Automated app installation
- **Policy Enforcement**: Configuration compliance
- **Change Management**: Track configuration changes

**Monitoring and Alerting**:
- **Performance Metrics**: CPU, memory, storage, network
- **Health Monitoring**: VM và hypervisor health
- **Capacity Planning**: Resource utilization trends
- **Alert Management**: Proactive issue notification

#### Automation and Orchestration

**Infrastructure as Code**:
- **Declarative Configuration**: Desired state specification
- **Version Control**: Infrastructure versioning
- **Automated Testing**: Infrastructure validation
- **Rollback Capabilities**: Quick recovery mechanisms

**Orchestration Platforms**:
- **VMware vRealize**: VMware's cloud management
- **Microsoft SCVMM**: System Center Virtual Machine Manager
- **OpenStack**: Open-source cloud platform
- **Kubernetes**: Container orchestration (extending to VMs)

---

*Với kiến thức fundamental về virtualization, chúng ta sẵn sàng đi sâu vào các công nghệ cụ thể như VMware vSphere, OpenStack, và cloud platforms.*
