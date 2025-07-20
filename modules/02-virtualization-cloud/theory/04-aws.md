# AWS Theory - Amazon Web Services Lý thuyết

## 🎯 Mục tiêu Học tập
Hiểu sâu về kiến trúc và core services của Amazon Web Services, từ compute đến storage và networking, đáp ứng yêu cầu triển khai hybrid cloud tại Viettel IDC.

## ☁️ 1. AWS Cloud Overview

### AWS Global Infrastructure

#### Geographic Distribution

**AWS Regions**:
- **Definition**: Geographic area với multiple Availability Zones
- **Global Presence**: 25+ regions worldwide
- **Data Sovereignty**: Comply với local data residency requirements
- **Service Availability**: Not all services available trong all regions
- **Latency Optimization**: Choose region closest to users

**Availability Zones (AZs)**:
- **Definition**: Isolated datacenter facilities within region
- **High Availability**: Multiple AZs per region (minimum 3)
- **Physical Separation**: Separate buildings, power, cooling
- **Network Connectivity**: Low-latency links between AZs
- **Fault Isolation**: Independent failure domains

**Edge Locations**:
- **CloudFront CDN**: Content delivery network endpoints
- **Global Coverage**: 200+ edge locations worldwide
- **Caching**: Static content caching closer to users
- **AWS Services**: Some services available at edge locations

#### AWS Well-Architected Framework

**Five Pillars**:

1. **Operational Excellence**:
   - **Automation**: Infrastructure as Code
   - **Monitoring**: Comprehensive observability
   - **Continuous Improvement**: Regular review và optimization
   - **Documentation**: Runbooks và procedures

2. **Security**:
   - **Identity Management**: Strong identity foundation
   - **Data Protection**: Encryption at rest và in transit
   - **Infrastructure Protection**: Defense in depth
   - **Incident Response**: Automated response capabilities

3. **Reliability**:
   - **Fault Tolerance**: System continues operating despite failures
   - **Recovery**: Quick recovery from failures
   - **Scaling**: Horizontal scaling capabilities
   - **Change Management**: Controlled change processes

4. **Performance Efficiency**:
   - **Resource Selection**: Right tool for the job
   - **Monitoring**: Performance monitoring và alerting
   - **Trade-offs**: Balance performance vs cost
   - **Evolution**: Regular architecture reviews

5. **Cost Optimization**:
   - **Cost-effective Resources**: Right-sizing instances
   - **Matching Supply và Demand**: Auto-scaling
   - **Expenditure Awareness**: Cost monitoring
   - **Optimizing Over Time**: Regular cost reviews

### AWS Service Categories

#### Compute Services
- **EC2**: Virtual servers trong cloud
- **Lambda**: Serverless compute
- **ECS**: Container orchestration
- **EKS**: Managed Kubernetes
- **Fargate**: Serverless containers
- **Batch**: Batch processing

#### Storage Services
- **S3**: Object storage
- **EBS**: Block storage
- **EFS**: File storage
- **Glacier**: Archive storage
- **Storage Gateway**: Hybrid storage

#### Database Services
- **RDS**: Managed relational databases
- **DynamoDB**: NoSQL database
- **Redshift**: Data warehouse
- **ElastiCache**: In-memory caching
- **Neptune**: Graph database

#### Networking Services
- **VPC**: Virtual private cloud
- **CloudFront**: Content delivery network
- **Route 53**: DNS service
- **Direct Connect**: Dedicated network connection
- **API Gateway**: API management

## 🖥️ 2. EC2 - Elastic Compute Cloud

### EC2 Architecture

#### Instance Types

**General Purpose**:
- **T3/T4g**: Burstable performance instances
- **M5/M6i**: Balanced compute, memory, networking
- **A1**: ARM-based processors

**Compute Optimized**:
- **C5/C6i**: High-performance processors
- **C5n**: Enhanced networking capabilities
- **C6gn**: ARM-based compute optimized

**Memory Optimized**:
- **R5/R6i**: Memory-intensive applications
- **X1e**: High memory instances
- **z1d**: High frequency và NVMe SSD

**Storage Optimized**:
- **I3**: NVMe SSD storage
- **D2**: Dense HDD storage
- **H1**: High disk throughput

**Accelerated Computing**:
- **P3/P4**: GPU instances cho machine learning
- **G4**: GPU instances cho graphics workloads
- **F1**: FPGA instances

#### Instance Purchasing Options

**On-Demand Instances**:
- **Pay-per-use**: Hourly hoặc per-second billing
- **No Commitment**: No long-term contracts
- **Flexibility**: Start/stop anytime
- **Use Cases**: Development, testing, unpredictable workloads

**Reserved Instances**:
- **Commitment**: 1 or 3-year terms
- **Discount**: Up to 75% savings
- **Payment Options**: All upfront, partial upfront, no upfront
- **Use Cases**: Steady-state workloads

**Spot Instances**:
- **Bid Price**: Bid on spare capacity
- **Savings**: Up to 90% discount
- **Interruption**: Can be terminated với 2-minute notice
- **Use Cases**: Fault-tolerant, flexible workloads

**Dedicated Hosts**:
- **Physical Server**: Dedicated hardware
- **Compliance**: Regulatory requirements
- **Licensing**: Use existing server-bound licenses
- **Use Cases**: Compliance, licensing requirements

### AMI - Amazon Machine Images

#### AMI Components

**AMI Structure**:
- **Root Volume**: Operating system installation
- **Data Volumes**: Additional storage volumes
- **Permissions**: Who can access AMI
- **Block Device Mapping**: Storage configuration

**AMI Types**:
- **EBS-backed**: Root volume on EBS
- **Instance Store-backed**: Root volume on instance store
- **Public AMIs**: Available to all AWS accounts
- **Private AMIs**: Owned by specific account
- **Marketplace AMIs**: Commercial AMIs

#### AMI Lifecycle

**Creating AMIs**:
1. **Launch Instance**: Start từ base AMI
2. **Customize**: Install software, configure system
3. **Create Image**: Snapshot current state
4. **Register**: Make AMI available

**AMI Best Practices**:
- **Golden Images**: Standardized base images
- **Security Hardening**: Apply security configurations
- **Regular Updates**: Keep AMIs current
- **Documentation**: Document AMI contents

### EC2 Storage

#### EBS - Elastic Block Store

**EBS Volume Types**:

**General Purpose SSD (gp3/gp2)**:
- **Performance**: Baseline 3 IOPS per GB
- **Burst**: Up to 3,000 IOPS
- **Size**: 1 GB to 16 TB
- **Use Cases**: General workloads

**Provisioned IOPS SSD (io2/io1)**:
- **Performance**: Up to 64,000 IOPS
- **Consistency**: Consistent performance
- **Size**: 4 GB to 16 TB
- **Use Cases**: I/O intensive workloads

**Throughput Optimized HDD (st1)**:
- **Performance**: Up to 500 MiB/s
- **Cost**: Lower cost per GB
- **Size**: 500 GB to 16 TB
- **Use Cases**: Big data, data warehouses

**Cold HDD (sc1)**:
- **Performance**: Up to 250 MiB/s
- **Cost**: Lowest cost option
- **Size**: 500 GB to 16 TB
- **Use Cases**: Infrequent access

#### Instance Store

**Characteristics**:
- **Temporary Storage**: Data lost on instance stop/termination
- **High Performance**: Direct-attached storage
- **No Cost**: Included với instance
- **Use Cases**: Temporary data, caches, buffers

### EC2 Networking

#### VPC Integration

**Network Interfaces**:
- **Primary ENI**: Default network interface
- **Secondary ENIs**: Additional network interfaces
- **Elastic IPs**: Static public IP addresses
- **IPv6 Support**: IPv6 addressing

**Security Groups**:
- **Virtual Firewall**: Instance-level security
- **Stateful**: Return traffic automatically allowed
- **Default Deny**: Deny all inbound by default
- **Rule Types**: Allow rules only

**Placement Groups**:
- **Cluster**: Low-latency, high bandwidth
- **Partition**: Distributed across hardware
- **Spread**: Separate underlying hardware

## 🗄️ 3. S3 - Simple Storage Service

### S3 Architecture

#### S3 Storage Model

**Bucket Structure**:
- **Global Namespace**: Unique bucket names worldwide
- **Regional**: Buckets created trong specific region
- **Object Storage**: Store files as objects
- **Flat Structure**: No traditional folder hierarchy

**Object Components**:
- **Key**: Object name/path
- **Version**: Object version (if versioning enabled)
- **Value**: Object data
- **Metadata**: System và user metadata
- **Access Control**: Object-level permissions

#### S3 Storage Classes

**Standard**:
- **Durability**: 99.999999999% (11 9's)
- **Availability**: 99.99%
- **Use Cases**: Frequently accessed data

**Standard-IA**:
- **Lower Cost**: Reduced storage cost
- **Retrieval Fee**: Per-GB retrieval charge
- **Use Cases**: Infrequently accessed data

**One Zone-IA**:
- **Single AZ**: Lower durability
- **Cost**: 20% less than Standard-IA
- **Use Cases**: Recreatable data

**Glacier**:
- **Archive Storage**: Long-term archival
- **Retrieval Time**: Minutes to hours
- **Use Cases**: Backup, archive

**Glacier Deep Archive**:
- **Lowest Cost**: Cheapest storage option
- **Retrieval Time**: 12+ hours
- **Use Cases**: Long-term archives

#### S3 Features

**Versioning**:
- **Multiple Versions**: Keep multiple object versions
- **Delete Protection**: Protect against accidental deletion
- **Storage Cost**: Cumulative storage cost
- **Lifecycle**: Manage version lifecycle

**Cross-Region Replication**:
- **Automatic**: Asynchronous replication
- **Requirements**: Versioning enabled
- **Use Cases**: Compliance, latency reduction
- **Storage Class**: Can change storage class

**Lifecycle Management**:
- **Transition Rules**: Move objects between storage classes
- **Expiration Rules**: Delete objects after specified time
- **Cost Optimization**: Automate cost optimization
- **Versioning**: Lifecycle applies to versions

### S3 Security

#### Access Control

**Bucket Policies**:
- **JSON Format**: Resource-based policies
- **Principal**: Who can access
- **Actions**: What actions allowed
- **Conditions**: When access allowed

**Access Control Lists (ACLs)**:
- **Legacy**: Older access control method
- **Grantees**: Specific users or groups
- **Permissions**: Read, write, read ACP, write ACP
- **Use Cases**: Simple access control

**IAM Policies**:
- **User-based**: Attached to IAM users/roles
- **JSON Format**: Same format as bucket policies
- **Cross-service**: Works với other AWS services
- **Best Practice**: Preferred access control method

#### Encryption

**Server-Side Encryption**:
- **SSE-S3**: S3-managed keys
- **SSE-KMS**: KMS-managed keys
- **SSE-C**: Customer-provided keys
- **Default**: Can set default encryption

**Client-Side Encryption**:
- **Application**: Application handles encryption
- **KMS Integration**: Can use KMS cho key management
- **Control**: Full control over encryption process
- **Performance**: Client handles encryption overhead

## 🌐 4. VPC - Virtual Private Cloud

### VPC Architecture

#### Core Concepts

**VPC Components**:
- **CIDR Block**: IP address range
- **Subnets**: Subdivision của VPC
- **Route Tables**: Network routing configuration
- **Internet Gateway**: Internet connectivity
- **NAT Gateway**: Outbound internet access

**Subnet Types**:
- **Public Subnet**: Direct internet access
- **Private Subnet**: No direct internet access
- **Database Subnet**: Isolated database tier
- **Availability Zone**: Subnets are AZ-specific

#### Networking Components

**Route Tables**:
- **Default Route**: 0.0.0.0/0 for internet traffic
- **Local Route**: Within VPC communication
- **Custom Routes**: Specific routing rules
- **Subnet Association**: Each subnet associated với route table

**Internet Gateway**:
- **VPC Attachment**: One IGW per VPC
- **Horizontally Scaled**: Redundant và highly available
- **Public Access**: Required cho public subnet access
- **NAT**: Performs NAT cho public instances

**NAT Gateway**:
- **Managed Service**: AWS-managed NAT solution
- **Availability Zone**: Deployed trong specific AZ
- **Bandwidth**: Up to 45 Gbps
- **High Availability**: Deploy trong multiple AZs

**VPC Endpoints**:
- **Gateway Endpoints**: S3 và DynamoDB access
- **Interface Endpoints**: Other AWS services
- **Private Access**: Access services without internet
- **Security**: Traffic stays within AWS network

### Security Groups vs NACLs

#### Security Groups

**Characteristics**:
- **Instance Level**: Applied to EC2 instances
- **Stateful**: Return traffic automatically allowed
- **Allow Rules**: Only allow rules (no deny)
- **Default Deny**: Deny all inbound by default

**Rules**:
- **Protocol**: TCP, UDP, ICMP
- **Port Range**: Specific ports or ranges
- **Source/Destination**: IP ranges or other security groups
- **Dynamic**: Changes take effect immediately

#### Network ACLs

**Characteristics**:
- **Subnet Level**: Applied to subnets
- **Stateless**: Must allow return traffic explicitly
- **Allow và Deny**: Both allow và deny rules
- **Rule Numbers**: Processing order important

**Default NACL**:
- **Allow All**: Default NACL allows all traffic
- **Custom NACL**: Custom NACLs deny all by default
- **Rule Evaluation**: Rules processed trong order
- **Last Resort**: Backup security layer

### VPC Connectivity

#### VPC Peering

**Characteristics**:
- **Point-to-Point**: One-to-one VPC connection
- **Cross-Region**: Can peer across regions
- **Non-transitive**: No transitive routing
- **Private**: Uses private IP addresses

**Limitations**:
- **CIDR Overlap**: No overlapping CIDR blocks
- **Route Tables**: Must update route tables
- **Security Groups**: Cannot reference across peers
- **DNS**: DNS resolution configuration required

#### Transit Gateway

**Architecture**:
- **Hub và Spoke**: Central routing hub
- **Scalable**: Supports thousands of connections
- **Cross-Region**: Inter-region connectivity
- **Route Tables**: Centralized routing control

**Benefits**:
- **Simplified**: Reduces network complexity
- **Scalable**: Easy to add new connections
- **Centralized**: Central point of control
- **Monitoring**: Centralized monitoring

#### Direct Connect

**Components**:
- **Dedicated Connection**: Physical connection to AWS
- **Virtual Interfaces**: Layer 3 connectivity
- **BGP**: Border Gateway Protocol routing
- **Bandwidth**: Up to 100 Gbps connections

**Benefits**:
- **Consistent Performance**: Predictable bandwidth
- **Lower Costs**: Reduced data transfer costs
- **Security**: Private connection to AWS
- **Hybrid**: Enables hybrid architectures

## 🗃️ 5. RDS - Relational Database Service

### RDS Architecture

#### Database Engines

**Supported Engines**:
- **MySQL**: Open-source relational database
- **PostgreSQL**: Advanced open-source database
- **MariaDB**: MySQL-compatible database
- **Oracle**: Enterprise database system
- **SQL Server**: Microsoft database system
- **Aurora**: AWS-native database engine

#### RDS Features

**Automated Backups**:
- **Point-in-time Recovery**: Restore to any point trong backup window
- **Backup Window**: Preferred backup time
- **Retention Period**: 7-35 days
- **Cross-Region**: Can copy backups to other regions

**Multi-AZ Deployments**:
- **High Availability**: Automatic failover
- **Synchronous Replication**: Data replicated synchronously
- **Automatic Failover**: Transparent failover
- **Maintenance**: Zero-downtime maintenance

**Read Replicas**:
- **Read Scaling**: Scale read operations
- **Asynchronous**: Asynchronous replication
- **Cross-Region**: Can create across regions
- **Promotion**: Can promote to standalone database

### Aurora Architecture

#### Aurora Storage

**Storage Architecture**:
- **Distributed**: Storage distributed across multiple AZs
- **Auto-scaling**: Storage grows automatically
- **Performance**: Up to 5x faster than MySQL
- **Replication**: 6 copies across 3 AZs

**Backup và Recovery**:
- **Continuous Backup**: Continuous backup to S3
- **Point-in-time Recovery**: Second-level granularity
- **Fast Recovery**: Fast database recovery
- **Parallel Recovery**: Parallel recovery processes

#### Aurora Features

**Aurora Serverless**:
- **Auto-scaling**: Automatic scaling based on demand
- **Pay-per-use**: Pay only for consumed resources
- **Pause và Resume**: Automatically pause when idle
- **Use Cases**: Infrequent, intermittent workloads

**Global Database**:
- **Cross-Region**: Spans multiple regions
- **Low Latency**: Sub-second replication lag
- **Disaster Recovery**: Fast recovery trong different region
- **Read Scaling**: Global read scaling

## 🔧 6. IAM - Identity and Access Management

### IAM Architecture

#### Core Components

**Users**:
- **Individual Identity**: Represents person or service
- **Credentials**: Password và/hoặc access keys
- **Permissions**: Attached directly or through groups
- **MFA**: Multi-factor authentication support

**Groups**:
- **Collection**: Collection of users
- **Permissions**: Permissions applied to all group members
- **Management**: Easier permission management
- **Best Practice**: Use groups instead of individual permissions

**Roles**:
- **Temporary Credentials**: Assumed temporarily
- **Cross-Account**: Can be assumed cross-account
- **Service Roles**: For AWS services
- **Federated Access**: For external identity providers

**Policies**:
- **JSON Documents**: Permission definitions
- **Managed Policies**: AWS hoặc customer managed
- **Inline Policies**: Embedded trong users/groups/roles
- **Resource-based**: Attached to resources

#### Policy Structure

**Policy Elements**:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow|Deny",
      "Principal": "User/Role/Service",
      "Action": "service:action",
      "Resource": "arn:aws:service:region:account:resource",
      "Condition": {
        "ConditionKey": "Value"
      }
    }
  ]
}
```

**Policy Evaluation**:
1. **Explicit Deny**: Deny always wins
2. **Explicit Allow**: Allow if explicitly allowed
3. **Default Deny**: Deny if no explicit allow

### IAM Best Practices

#### Security Best Practices

**Principle of Least Privilege**:
- **Minimum Permissions**: Grant minimum required permissions
- **Regular Review**: Regular permission audits
- **Just-in-time**: Temporary elevated permissions
- **Monitoring**: Monitor permission usage

**Access Keys**:
- **Rotation**: Regular key rotation
- **Temporary**: Use temporary credentials when possible
- **Least Privilege**: Limit access key permissions
- **Monitoring**: Monitor access key usage

**Multi-Factor Authentication**:
- **Root Account**: Always enable MFA on root
- **Privileged Users**: MFA for administrative users
- **Virtual MFA**: Software-based MFA devices
- **Hardware MFA**: Hardware security keys

## 🎛️ 7. CloudFormation - Infrastructure as Code

### CloudFormation Architecture

#### Template Structure

**Template Sections**:
```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Template description'

Parameters:
  # Input parameters

Mappings:
  # Static lookup tables

Conditions:
  # Conditional logic

Resources:
  # AWS resources

Outputs:
  # Return values
```

#### Resource Management

**Resource Types**:
- **AWS Resources**: EC2, S3, RDS, etc.
- **Properties**: Resource configuration
- **Dependencies**: Resource creation order
- **Updates**: How resources handle updates

**Stack Operations**:
- **Create**: Deploy new stack
- **Update**: Modify existing stack
- **Delete**: Remove stack và resources
- **Rollback**: Automatic rollback on failure

### Advanced Features

#### Nested Stacks

**Benefits**:
- **Modularity**: Reusable template components
- **Organization**: Logical separation
- **Limits**: Overcome template size limits
- **Updates**: Independent stack updates

#### Cross-Stack References

**Exports**:
- **Output Values**: Export values from one stack
- **ImportValue**: Import values trong another stack
- **Dependencies**: Create stack dependencies
- **Updates**: Coordinate stack updates

#### Change Sets

**Preview Changes**:
- **Change Preview**: See changes before execution
- **Impact Analysis**: Understand change impact
- **Approval**: Approval workflow cho changes
- **Safety**: Prevent unexpected changes

---

*Với kiến thức chi tiết về AWS services và architecture, chúng ta có thể thiết kế và triển khai scalable, reliable cloud solutions.*
