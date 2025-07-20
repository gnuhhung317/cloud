# Module 2: Ảo hóa & Cloud (VMware, OpenStack, AWS, Azure)

## 🎯 Mục tiêu Module
Nắm vững kiến thức về ảo hóa và điện toán đám mây, từ on-premises virtualization đến public cloud, đáp ứng yêu cầu triển khai hạ tầng hiện đại tại Viettel IDC.

## � Lý thuyết Chi tiết
- 📖 **[Cloud Computing Theory](./theory/cloud-computing-theory.md)** - Lý thuyết tổng quan về cloud computing và hybrid strategies
- 🖥️ **[VMware vSphere Theory](./theory/vmware-vsphere-theory.md)** - Kiến trúc và quản lý VMware infrastructure  
- ☁️ **[OpenStack Theory](./theory/openstack-theory.md)** - Private cloud với OpenStack platform
- 🌐 **[AWS Theory](./theory/aws-theory.md)** - Amazon Web Services fundamentals
- 🔷 **[Azure Theory](./theory/azure-fundamentals.md)** - Microsoft Azure cloud platform
- 🧪 **[Hands-on Labs](./labs/hands-on-labs.md)** - Practical labs và exercises
- 📋 **[Module Summary](./module-summary.md)** - Tóm tắt và learning roadmap

## �📋 Nội dung Chính

### VMware vSphere (40% trọng số)
#### 1. ESXi Host Management
- **Installation**: ESXi installation và configuration
- **Networking**: vSwitches, VLANs, port groups
- **Storage**: VMFS, NFS, iSCSI configuration
- **Host monitoring**: performance, alerts, logs

#### 2. vCenter Server
- **vCenter deployment**: appliance installation
- **Datacenter objects**: clusters, resource pools
- **VM management**: templates, cloning, snapshots
- **vMotion**: live migration setup và troubleshooting

#### 3. High Availability & DRS
- **HA configuration**: admission control, failover
- **DRS setup**: load balancing, affinity rules
- **Backup strategies**: vSphere Data Protection
- **Performance optimization**: resource allocation

### OpenStack (25% trọng số)
#### 1. Core Services
- **Nova** (Compute): instance management
- **Neutron** (Networking): networks, subnets, routers
- **Cinder** (Block Storage): volumes, snapshots
- **Glance** (Image): image management
- **Keystone** (Identity): users, projects, roles

#### 2. Deployment & Management
- **DevStack**: development environment
- **OpenStack CLI**: command line operations
- **Dashboard (Horizon)**: web interface
- **API usage**: REST API automation

### AWS (20% trọng số)
#### 1. Core Services
- **EC2**: instances, AMIs, security groups
- **S3**: buckets, storage classes, lifecycle
- **RDS**: managed databases
- **VPC**: networking, subnets, route tables

#### 2. Management & Automation
- **IAM**: users, roles, policies
- **CloudFormation**: infrastructure as code
- **Auto Scaling**: scaling groups, policies
- **CloudWatch**: monitoring và alerting

### Azure (15% trọng số)
#### 1. Core Services
- **Virtual Machines**: deployment, management
- **Storage Accounts**: blob, file, queue storage
- **Virtual Networks**: subnets, NSGs, peering
- **Azure SQL**: managed database services

#### 2. Management Tools
- **Resource Groups**: organization
- **Azure Portal**: web management
- **Azure CLI/PowerShell**: automation
- **Azure Monitor**: logging và monitoring

## 🛠️ Kỹ năng Thực hành

### VMware Labs
1. **vSphere Infrastructure Setup**
   ```bash
   # ESXi installation checklist
   - Configure management network
   - Setup shared storage (NFS/iSCSI)
   - Install vCenter Server Appliance
   - Create datacenter và cluster
   ```

2. **VM Lifecycle Management**
   - Create VM templates
   - Deploy VMs from templates
   - Configure VM hardware
   - Manage snapshots

3. **HA & DRS Configuration**
   - Setup HA cluster
   - Configure DRS rules
   - Test failover scenarios
   - Monitor cluster health

### OpenStack Labs
1. **All-in-One Deployment**
   ```bash
   # DevStack installation
   git clone https://git.openstack.org/openstack-dev/devstack
   cd devstack
   ./stack.sh
   ```

2. **Instance Management**
   - Create flavors và images
   - Launch instances
   - Configure networking
   - Attach storage volumes

### AWS Labs
1. **EC2 & VPC Setup**
   ```bash
   # AWS CLI examples
   aws ec2 create-vpc --cidr-block 10.0.0.0/16
   aws ec2 create-subnet --vpc-id vpc-xxx --cidr-block 10.0.1.0/24
   aws ec2 run-instances --image-id ami-xxx --instance-type t2.micro
   ```

2. **Infrastructure as Code**
   - Create CloudFormation templates
   - Deploy stacks
   - Update và rollback
   - Monitor resources

### Azure Labs
1. **Resource Deployment**
   ```powershell
   # Azure PowerShell examples
   New-AzResourceGroup -Name "TestRG" -Location "East US"
   New-AzVM -ResourceGroupName "TestRG" -Name "TestVM"
   ```

## 📚 Tài liệu Tham khảo

### VMware
- vSphere Installation và Setup Guide
- vSphere Administration Guide
- VMware Certified Professional Study Guide

### OpenStack
- OpenStack Architecture Guide
- OpenStack Operations Guide
- OpenStack User Guide

### AWS
- AWS Well-Architected Framework
- AWS Solutions Architect Study Guide
- AWS CLI User Guide

### Azure
- Azure Fundamentals Learning Path
- Azure Administrator Guide
- Azure CLI Reference

## 🎓 Chứng chỉ Liên quan
- **VMware**: VCP-DCV (vSphere)
- **OpenStack**: Certified OpenStack Administrator
- **AWS**: Solutions Architect Associate, SysOps Administrator
- **Azure**: Azure Fundamentals (AZ-900), Azure Administrator (AZ-104)

## ⏱️ Thời gian Học: 3-4 tuần
- Tuần 1: VMware vSphere fundamentals + labs
- Tuần 2: OpenStack deployment + management
- Tuần 3: AWS core services + automation
- Tuần 4: Azure services + integration scenarios

## 🔗 Chuyển sang Module tiếp theo
Với kiến thức về virtualization và cloud, bạn đã sẵn sàng cho **Module 3: Container Management**.
