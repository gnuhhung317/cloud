# OpenStack Theory - Lý thuyết OpenStack

## 🎯 Mục tiêu Học tập
Hiểu sâu về kiến trúc OpenStack và các core services, từ lý thuyết đến deployment, đáp ứng yêu cầu triển khai private cloud tại Viettel IDC.

## ☁️ 1. OpenStack Overview và Architecture

### OpenStack Introduction

#### What is OpenStack?
**OpenStack** là open-source cloud computing platform cho việc triển khai Infrastructure as a Service (IaaS). Được thiết kế để cung cấp scalable và flexible cloud infrastructure.

**Key Characteristics**:
- **Open Source**: Apache 2.0 license, community-driven
- **Modular Architecture**: Loosely coupled services
- **API-driven**: RESTful APIs cho tất cả services
- **Vendor Neutral**: Works với diverse hardware và software
- **Scalable**: From small deployments to massive public clouds

#### OpenStack History

**Project Origins**:
- **2010**: Joint project by Rackspace và NASA
- **2012**: OpenStack Foundation established
- **Release Cycle**: 6-month release cycle với code names
- **Community**: Thousands của contributors worldwide

**Major Releases**:
- **Austin (2010)**: Initial release
- **Essex (2012)**: First stable release
- **Havana (2013)**: Heat orchestration added
- **Juno (2014)**: Sahara data processing
- **Liberty (2015)**: Keystone v3 API
- **Newton (2016)**: Improved upgrade process
- **Pike (2017)**: Containerized services
- **Stein (2019)**: Python 3 migration complete
- **Ussuri (2020)**: Latest stable release

### OpenStack Architecture Overview

#### Logical Architecture
```
┌─────────────────────────────────────────────────────────┐
│                    Dashboard (Horizon)                 │
├─────────────────────────────────────────────────────────┤
│  Identity   │  Compute  │ Networking │    Storage      │
│ (Keystone)  │  (Nova)   │ (Neutron)  │ (Cinder/Swift)  │
├─────────────────────────────────────────────────────────┤
│          Image Service (Glance)                        │
├─────────────────────────────────────────────────────────┤
│          Orchestration (Heat)                          │
└─────────────────────────────────────────────────────────┘
```

#### Core Services Overview

**Essential Services (Big Tent)**:
- **Keystone**: Identity và authentication service
- **Nova**: Compute service for VM management
- **Neutron**: Networking service
- **Cinder**: Block storage service
- **Glance**: Image service for VM images
- **Swift**: Object storage service

**Optional Services**:
- **Heat**: Orchestration service
- **Horizon**: Web dashboard
- **Ceilometer**: Telemetry service
- **Barbican**: Key management service
- **Designate**: DNS service
- **Magnum**: Container orchestration

#### Service Communication

**API Communication**:
- **RESTful APIs**: HTTP-based communication
- **Message Queue**: Asynchronous messaging (RabbitMQ/Apache Qpid)
- **Database**: Shared database layer (MySQL/PostgreSQL)
- **Authentication**: Keystone-based auth cho all services

**Message Queue Architecture**:
- **AMQP Protocol**: Advanced Message Queuing Protocol
- **RPC Calls**: Remote Procedure Call mechanism
- **Notifications**: Event notifications between services
- **Scalability**: Queue-based scalability

## 🔑 2. Keystone - Identity Service

### Keystone Architecture

#### Core Concepts

**Identity Concepts**:
- **User**: Individual cloud user account
- **Group**: Collection của users
- **Domain**: Administrative namespace
- **Project (Tenant)**: Resource isolation boundary
- **Role**: Permission set assigned to users

**Service Concepts**:
- **Service**: OpenStack service (nova, neutron, etc.)
- **Endpoint**: Service access point (URL)
- **Region**: Geographic or logical service grouping

#### Authentication Process

**Token-based Authentication**:
1. **Initial Auth**: User provides credentials to Keystone
2. **Token Issuance**: Keystone returns authentication token
3. **Service Access**: Token used cho subsequent API calls
4. **Token Validation**: Services validate tokens với Keystone

**Token Types**:
- **UUID Tokens**: Simple UUID format (deprecated)
- **PKI Tokens**: Public Key Infrastructure tokens
- **Fernet Tokens**: Lightweight, encrypted tokens (recommended)
- **JWT Tokens**: JSON Web Tokens (future direction)

#### Identity Backends

**Identity Providers**:
- **SQL Backend**: Local user database
- **LDAP Integration**: Active Directory, OpenLDAP
- **Federation**: SAML, OpenID Connect
- **Multi-domain**: Multiple identity backends

**Assignment Backends**:
- **SQL**: Role assignments in database
- **LDAP**: Role assignments trong LDAP
- **Hybrid**: Mixed backend configurations

### Keystone Configuration

#### Service Configuration

**keystone.conf Structure**:
```ini
[DEFAULT]
# Basic configuration

[database]
# Database connection settings

[token]
# Token configuration

[identity]
# Identity backend settings

[assignment]
# Assignment backend settings

[auth]
# Authentication method settings
```

**Key Configuration Sections**:
- **Token Expiration**: Token lifetime settings
- **Password Policy**: Password complexity requirements
- **Federation**: External identity provider integration
- **Security**: Security-related settings

#### Multi-tenancy

**Project Isolation**:
- **Resource Separation**: Projects cannot access each other's resources
- **Quota Management**: Per-project resource limits
- **Network Isolation**: Separate networks per project
- **Security Groups**: Project-level security rules

**Domain Concepts**:
- **Administrative Domains**: Separate administrative spaces
- **Project Domains**: Projects belong to domains
- **User Domains**: Users belong to domains
- **Cross-domain**: Limited cross-domain access

## 🖥️ 3. Nova - Compute Service

### Nova Architecture

#### Nova Components

**Nova Services**:
- **nova-api**: REST API service
- **nova-scheduler**: VM placement scheduler
- **nova-compute**: Hypervisor management
- **nova-conductor**: Database proxy service
- **nova-consoleauth**: Console authentication
- **nova-novncproxy**: VNC console proxy

**Nova Databases**:
- **nova**: Main Nova database
- **nova_api**: API-specific database
- **nova_cell0**: Special database cho failed instances

#### Compute Node Architecture

**Hypervisor Support**:
- **KVM**: Kernel-based Virtual Machine (default)
- **Xen**: Xen hypervisor support
- **Hyper-V**: Microsoft Hyper-V support
- **VMware vSphere**: VMware integration
- **LXC**: Linux Containers support

**Compute Services on Node**:
- **nova-compute**: Primary compute service
- **libvirt**: Hypervisor abstraction layer
- **neutron-agent**: Networking agent
- **Hypervisor**: Actual virtualization platform

### Instance Lifecycle

#### Instance States

**VM Power States**:
- **ACTIVE**: Running instance
- **SHUTOFF**: Stopped instance
- **PAUSED**: Paused instance
- **SUSPENDED**: Suspended to disk
- **ERROR**: Error state
- **BUILDING**: Being created

**Task States**:
- **scheduling**: Finding suitable host
- **networking**: Setting up network
- **spawning**: Creating VM on hypervisor
- **rebooting**: Restart operation
- **deleting**: Deletion in progress

#### Instance Deployment Process

**Launch Sequence**:
1. **API Request**: User requests instance via API
2. **Authentication**: Keystone validates request
3. **Quota Check**: Nova checks project quotas
4. **Scheduling**: Scheduler finds suitable compute node
5. **Image Preparation**: Glance provides VM image
6. **Network Setup**: Neutron configures networking
7. **Storage Setup**: Cinder attaches volumes (if needed)
8. **VM Creation**: Hypervisor creates VM
9. **Post-deployment**: Final configuration và startup

### Nova Scheduler

#### Scheduler Architecture

**Scheduling Process**:
1. **Filter Scheduler**: Default scheduler implementation
2. **Host Filtering**: Remove unsuitable hosts
3. **Host Weighting**: Rank suitable hosts
4. **Host Selection**: Choose best host for instance

**Filter Types**:
- **AvailabilityZoneFilter**: Zone-based placement
- **ComputeFilter**: CPU architecture compatibility
- **RamFilter**: Available memory check
- **DiskFilter**: Available disk space check
- **ImagePropertiesFilter**: Image requirement matching

**Weighing Methods**:
- **RAMWeigher**: Prefer hosts với more available RAM
- **DiskWeigher**: Prefer hosts với more available disk
- **MetricsWeigher**: Custom metrics-based weighing
- **IoOpsWeigher**: I/O operations weighing

#### Placement Service

**Placement API**: Resource tracking và allocation
- **Resource Providers**: Compute nodes, storage pools
- **Resource Classes**: CPU, memory, disk, custom resources
- **Traits**: Qualitative capabilities (SSD, GPU)
- **Allocation**: Resource consumption tracking

## 🌐 4. Neutron - Networking Service

### Neutron Architecture

#### Neutron Components

**Core Neutron Services**:
- **neutron-server**: API service và plugin coordination
- **neutron-dhcp-agent**: DHCP service management
- **neutron-l3-agent**: Layer 3 routing services
- **neutron-metadata-agent**: Metadata service proxy
- **neutron-openvswitch-agent**: Open vSwitch integration

#### Network Abstractions

**Neutron Network Model**:
- **Networks**: Layer 2 broadcast domains
- **Subnets**: IP address ranges within networks
- **Ports**: Virtual network interfaces
- **Routers**: Layer 3 routing between networks
- **Security Groups**: Firewall rules

**Network Types**:
- **Flat**: Simple flat network
- **VLAN**: 802.1Q VLAN networks
- **VXLAN**: Virtual Extensible LAN
- **GRE**: Generic Routing Encapsulation
- **Geneve**: Generic Network Virtualization Encapsulation

### Neutron Plugins

#### ML2 Plugin Architecture

**Modular Layer 2 (ML2)**:
- **Type Drivers**: Network type implementations
- **Mechanism Drivers**: Backend implementation
- **Extension Drivers**: Additional functionality
- **Agent Communication**: ML2 agent coordination

**Popular Mechanism Drivers**:
- **Open vSwitch**: Software-defined switching
- **Linux Bridge**: Linux bridge networking
- **OVN**: Open Virtual Network
- **ODL**: OpenDaylight SDN controller
- **Calico**: Container networking

#### SDN Integration

**Software-Defined Networking**:
- **Centralized Control**: SDN controller manages network
- **Flow-based**: Network behavior defined by flows
- **Programmable**: API-driven network configuration
- **Vendor Support**: Multiple SDN vendor integration

### Network Services

#### Load Balancing (Octavia)

**LBaaS Architecture**:
- **Load Balancer**: Entry point for traffic
- **Listener**: Protocol và port specification
- **Pool**: Backend server group
- **Members**: Individual backend servers
- **Health Monitor**: Backend health checking

#### VPN as a Service (VPNaaS)

**VPN Types**:
- **Site-to-Site**: IPSec VPN connections
- **SSL VPN**: SSL-based remote access
- **MPLS VPN**: Multi-Protocol Label Switching
- **GRE Tunnels**: Generic routing encapsulation

#### Firewall as a Service (FWaaS)

**Firewall Components**:
- **Firewall**: Virtual firewall instance
- **Firewall Policy**: Collection of rules
- **Firewall Rules**: Individual filtering rules
- **Router Association**: Firewall applied to routers

## 💾 5. Storage Services

### Cinder - Block Storage

#### Cinder Architecture

**Cinder Components**:
- **cinder-api**: REST API service
- **cinder-scheduler**: Volume placement scheduler
- **cinder-volume**: Volume management service
- **cinder-backup**: Volume backup service

**Storage Backends**:
- **LVM**: Logical Volume Manager
- **Ceph**: Distributed storage system
- **NetApp**: NetApp storage arrays
- **EMC**: Dell EMC storage systems
- **Pure Storage**: Pure Storage arrays

#### Volume Management

**Volume Types**:
- **Standard Volume**: Basic block storage
- **Boot Volume**: Bootable system volume
- **Backup Volume**: Backup destination
- **Encrypted Volume**: Encrypted block storage

**Volume Operations**:
- **Create**: Provision new volumes
- **Attach**: Attach volume to instance
- **Detach**: Detach volume from instance
- **Snapshot**: Point-in-time volume copy
- **Clone**: Create volume from another volume
- **Extend**: Increase volume size

#### Multi-backend Configuration

**Backend Selection**:
- **Volume Types**: User-selectable storage classes
- **Extra Specs**: Backend-specific parameters
- **Scheduler Filters**: Backend selection logic
- **QoS Specifications**: Performance requirements

### Swift - Object Storage

#### Swift Architecture

**Swift Components**:
- **swift-proxy**: API gateway service
- **swift-account**: Account service
- **swift-container**: Container service
- **swift-object**: Object service

**Swift Ring**:
- **Consistent Hashing**: Data distribution algorithm
- **Replicas**: Multiple copies cho durability
- **Zones**: Failure domains
- **Regions**: Geographic distribution

#### Object Storage Concepts

**Swift Hierarchy**:
```
Account
├── Container 1
│   ├── Object 1
│   ├── Object 2
│   └── Object N
├── Container 2
└── Container N
```

**Data Durability**:
- **Replication**: Multiple copies of data
- **Erasure Coding**: Space-efficient durability
- **Consistency**: Eventually consistent model
- **Conflict Resolution**: Last-write-wins

## 🖼️ 6. Glance - Image Service

### Glance Architecture

#### Glance Components

**Core Services**:
- **glance-api**: REST API service
- **glance-registry**: Image metadata service (deprecated)

**Storage Backends**:
- **File System**: Local file storage
- **Swift**: Object storage backend
- **Ceph**: Distributed storage
- **HTTP**: Remote HTTP locations
- **S3**: Amazon S3 compatible storage

#### Image Management

**Image Formats**:
- **Raw**: Unstructured disk image
- **QCOW2**: QEMU Copy-On-Write version 2
- **VMDK**: VMware Virtual Machine Disk
- **VHD**: Virtual Hard Disk
- **AMI**: Amazon Machine Image
- **ISO**: ISO 9660 disk image

**Image Properties**:
- **Disk Format**: Image file format
- **Container Format**: Image container
- **Visibility**: Public, private, shared
- **Protected**: Deletion protection
- **Metadata**: Custom key-value pairs

### Image Lifecycle

#### Image States

**Image Status**:
- **queued**: Identified, not uploaded
- **saving**: Upload in progress
- **active**: Available for use
- **killed**: Upload error occurred
- **deleted**: Marked for deletion
- **pending_delete**: Scheduled deletion

#### Image Operations

**Image Management**:
- **Upload**: Add new images
- **Download**: Retrieve image data
- **Update**: Modify image properties
- **Delete**: Remove images
- **Share**: Share with other projects
- **Copy**: Duplicate images

## 🌡️ 7. Heat - Orchestration Service

### Heat Architecture

#### Heat Components

**Core Services**:
- **heat-api**: REST API service
- **heat-api-cfn**: CloudFormation-compatible API
- **heat-engine**: Orchestration engine

**Template Formats**:
- **HOT**: Heat Orchestration Template (YAML)
- **CFN**: CloudFormation Template (JSON)

#### Template Structure

**HOT Template Sections**:
```yaml
heat_template_version: 2018-08-31

description: Template description

parameters:
  # Input parameters

resources:
  # Resource definitions

outputs:
  # Output values
```

**Resource Types**:
- **OS::Nova::Server**: Virtual machine instances
- **OS::Neutron::Net**: Network resources
- **OS::Cinder::Volume**: Block storage volumes
- **OS::Heat::Stack**: Nested stacks

### Stack Management

#### Stack Lifecycle

**Stack Operations**:
- **Create**: Deploy new stack
- **Update**: Modify existing stack
- **Delete**: Remove stack và resources
- **Suspend**: Temporarily halt stack
- **Resume**: Restart suspended stack

**Stack States**:
- **CREATE_IN_PROGRESS**: Creation in progress
- **CREATE_COMPLETE**: Successfully created
- **CREATE_FAILED**: Creation failed
- **UPDATE_IN_PROGRESS**: Update in progress
- **DELETE_IN_PROGRESS**: Deletion in progress

## 📊 8. Horizon - Dashboard

### Horizon Architecture

#### Dashboard Components

**Django Framework**:
- **Web Framework**: Python-based web framework
- **Panel Structure**: Modular dashboard panels
- **Theme Support**: Customizable themes
- **Multi-language**: Internationalization support

**Dashboard Structure**:
- **Dashboards**: Top-level groupings (Project, Admin, Identity)
- **Panel Groups**: Related functionality grouping
- **Panels**: Individual feature interfaces
- **Tables**: Data presentation tables
- **Forms**: Input forms cho operations

#### User Interface

**Project Dashboard**:
- **Compute**: Instance management
- **Volume**: Block storage management
- **Network**: Network configuration
- **Orchestration**: Heat stack management

**Admin Dashboard**:
- **System**: System-wide administration
- **Compute**: Hypervisor management
- **Volume**: Storage backend management
- **Network**: Network agent management

## 🔧 9. OpenStack Deployment

### Deployment Methods

#### Manual Deployment

**Installation Steps**:
1. **Prerequisites**: OS installation và basic configuration
2. **Database Setup**: MySQL/PostgreSQL installation
3. **Message Queue**: RabbitMQ configuration
4. **Keystone**: Identity service deployment
5. **Glance**: Image service deployment
6. **Nova**: Compute service deployment
7. **Neutron**: Networking service deployment
8. **Horizon**: Dashboard deployment

#### Automated Deployment Tools

**DevStack**:
- **Development Focus**: Single-node development environment
- **Quick Setup**: Automated script-based installation
- **Configuration**: local.conf configuration file
- **Use Cases**: Development, testing, learning

**Kolla-Ansible**:
- **Container-based**: Docker container deployment
- **Ansible Playbooks**: Infrastructure automation
- **Production Ready**: Suitable cho production deployments
- **High Availability**: Multi-node HA configurations

**TripleO**:
- **OpenStack on OpenStack**: Uses OpenStack to deploy OpenStack
- **Ironic**: Bare metal provisioning
- **Heat**: Orchestration-based deployment
- **Red Hat**: RDO và Red Hat OpenStack Platform

**Juju**:
- **Charm-based**: Ubuntu charm deployments
- **MAAS Integration**: Metal as a Service
- **Cloud Agnostic**: Multiple cloud support
- **Canonical**: Ubuntu-focused deployment

### Configuration Management

#### Service Configuration

**Configuration Files**:
- **Central Config**: /etc/<service>/<service>.conf
- **Policy Files**: JSON-based authorization policies
- **Logging**: Centralized logging configuration
- **API Paste**: WSGI application configuration

**Common Configuration Patterns**:
- **Database Connections**: Service database connectivity
- **Message Queue**: RabbitMQ connection settings
- **Keystone Integration**: Authentication configuration
- **API Endpoints**: Service discovery configuration

#### High Availability

**HA Components**:
- **Load Balancers**: HAProxy, nginx load balancing
- **Database Clustering**: MySQL/MariaDB Galera cluster
- **Message Queue**: RabbitMQ clustering
- **API Services**: Multiple API service instances
- **Pacemaker**: Resource management

**HA Considerations**:
- **Stateless Services**: API services easily scaled
- **Stateful Services**: Database và queue clustering
- **Shared Storage**: Consistent storage access
- **Network Redundancy**: Multiple network paths

---

*Với kiến thức sâu về OpenStack architecture và services, chúng ta có thể triển khai và quản lý private cloud infrastructure hiệu quả.*
