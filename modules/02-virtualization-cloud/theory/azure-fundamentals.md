# Azure Fundamentals - Lý thuyết Cơ bản

## 🎯 Mục tiêu Học tập
Hiểu rõ kiến trúc, dịch vụ và mô hình quản lý của Microsoft Azure cho môi trường enterprise tại Viettel IDC.

## 🧠 Azure Cloud Theory

### 1. Microsoft Azure Architecture

#### Azure Global Infrastructure

**Geographic Regions**:
- **Definition**: Geographical areas containing multiple datacenters
- **Latency**: Low latency within region boundaries
- **Compliance**: Data residency và regulatory requirements
- **Availability**: Multiple regions for disaster recovery

**Availability Zones**:
- **Physical Separation**: Physically separate datacenters within region
- **Independent Infrastructure**: Separate power, cooling, networking
- **High Availability**: 99.99% availability SLA
- **Zone-redundant Services**: Automatic replication across zones

**Azure Datacenters**:
- **Scale**: Hundreds of thousands of servers per datacenter
- **Security**: Physical security, biometric access
- **Connectivity**: High-speed fiber connections
- **Sustainability**: Renewable energy initiatives

#### Azure Resource Management

**Azure Resource Manager (ARM)**:
- **Deployment Model**: Consistent management interface
- **Resource Groups**: Logical containers for resources
- **Template-based Deployment**: JSON-based infrastructure as code
- **Role-based Access Control**: Fine-grained permissions

**Resource Hierarchy**:
```
Management Groups
    └── Subscriptions
        └── Resource Groups
            └── Resources
```

**Subscription Model**:
- **Billing Boundary**: Separate billing for each subscription
- **Access Control**: Different permissions per subscription
- **Resource Limits**: Service limits per subscription
- **Policy Enforcement**: Azure Policy application

### 2. Azure Core Services

#### Compute Services

**Azure Virtual Machines**:

**VM Series và Use Cases**:
- **A-Series**: Basic workloads, dev/test
- **D-Series**: General purpose, balanced CPU/memory
- **F-Series**: CPU-intensive workloads
- **G-Series**: Memory-intensive applications
- **H-Series**: High-performance computing
- **L-Series**: Low latency, high disk throughput

**VM Sizing**:
- **vCPUs**: Virtual CPU cores
- **Memory**: RAM allocation
- **Storage**: Temp disk và data disk capacity
- **Network**: Network interface performance

**Availability Options**:
- **Availability Sets**: Fault và update domain distribution
- **Availability Zones**: Cross-zone deployment
- **Virtual Machine Scale Sets**: Auto-scaling capabilities
- **Azure Site Recovery**: Disaster recovery

#### Storage Services

**Azure Storage Types**:

**Blob Storage**:
- **Hot Tier**: Frequently accessed data
- **Cool Tier**: Infrequently accessed, stored 30+ days
- **Archive Tier**: Rarely accessed, stored 180+ days
- **Use Cases**: Website content, backup, analytics

**File Storage**:
- **SMB Protocol**: Server Message Block file shares
- **NFS Protocol**: Network File System (preview)
- **Azure File Sync**: Hybrid file synchronization
- **Use Cases**: Lift-and-shift applications, shared storage

**Queue Storage**:
- **Message Queuing**: Asynchronous message passing
- **Scalability**: Millions of messages
- **Durability**: Multiple copies across datacenters
- **Use Cases**: Decoupling application components

**Table Storage**:
- **NoSQL**: Key-value store
- **Schema-less**: Flexible data structure
- **Performance**: Fast lookups
- **Use Cases**: Web applications, user data

**Storage Replication**:
- **LRS (Locally Redundant)**: 3 copies within datacenter
- **ZRS (Zone Redundant)**: Copies across availability zones
- **GRS (Geo Redundant)**: Copies to secondary region
- **RA-GRS**: Read access to geo-replicated data

#### Networking Services

**Azure Virtual Network (VNet)**:

**VNet Components**:
- **Address Space**: Private IP address ranges
- **Subnets**: Network segmentation within VNet
- **Route Tables**: Traffic routing control
- **Network Security Groups**: Firewall rules

**Connectivity Options**:
- **VNet Peering**: Connect VNets within region
- **Global VNet Peering**: Connect VNets across regions
- **VPN Gateway**: Site-to-site và point-to-site VPN
- **ExpressRoute**: Dedicated private connection

**Load Balancing**:
- **Azure Load Balancer**: Layer 4 load balancing
- **Application Gateway**: Layer 7 load balancing
- **Traffic Manager**: DNS-based traffic distribution
- **Front Door**: Global load balancing với CDN

#### Database Services

**Azure SQL Database**:
- **PaaS Service**: Fully managed SQL Server
- **Scaling**: Dynamic scaling capabilities
- **High Availability**: Built-in HA và disaster recovery
- **Security**: Advanced threat protection, encryption

**Azure Cosmos DB**:
- **Multi-model**: Document, key-value, graph, column-family
- **Global Distribution**: Multi-region replication
- **Consistency Levels**: Five consistency models
- **APIs**: SQL, MongoDB, Cassandra, Gremlin, Table

### 3. Azure Management và Governance

#### Azure Resource Manager Templates

**Template Structure**:
```json
{
    "$schema": "...",
    "contentVersion": "1.0.0.0",
    "parameters": { },
    "variables": { },
    "resources": [ ],
    "outputs": { }
}
```

**Template Benefits**:
- **Declarative**: Describe desired state
- **Idempotent**: Same result on multiple deployments
- **Dependency Management**: Automatic resource ordering
- **Parameterization**: Reusable templates

#### Azure Policy

**Policy Definition**:
- **Rules**: If-then conditions
- **Effects**: Deny, audit, append, modify
- **Scope**: Management group, subscription, resource group
- **Compliance**: Track compliance status

**Initiative (Policy Set)**:
- **Grouping**: Multiple policies together
- **Compliance Dashboard**: Unified compliance view
- **Examples**: ISO 27001, SOC TSP, NIST

#### Azure Monitor

**Monitoring Components**:
- **Metrics**: Numerical performance data
- **Logs**: Text-based diagnostic data
- **Alerts**: Notifications based on conditions
- **Dashboards**: Visual representation of data

**Log Analytics**:
- **Kusto Query Language (KQL)**: Query language for logs
- **Workspaces**: Log data collection points
- **Solutions**: Pre-built monitoring packages
- **Custom Logs**: Import custom log data

#### Azure Security

**Azure Active Directory (AAD)**:
- **Identity Provider**: Cloud-based identity service
- **Single Sign-On**: SSO across applications
- **Multi-Factor Authentication**: Additional security layer
- **Conditional Access**: Risk-based access policies

**Azure Security Center**:
- **Security Posture**: Continuous security assessment
- **Threat Protection**: Advanced threat detection
- **Compliance**: Regulatory compliance tracking
- **Recommendations**: Security improvement suggestions

**Azure Key Vault**:
- **Secrets Management**: API keys, passwords, certificates
- **Hardware Security Modules**: FIPS 140-2 Level 2 validated
- **Access Policies**: Fine-grained access control
- **Integration**: Seamless application integration

### 4. Azure Pricing và Cost Management

#### Pricing Models

**Pay-as-you-go**:
- **No Upfront Costs**: Pay only for what you use
- **Flexible**: Scale up/down as needed
- **Per-minute Billing**: Fine-grained billing
- **Suitable for**: Variable workloads, development

**Reserved Instances**:
- **1 or 3 Year Terms**: Committed usage periods
- **Significant Discounts**: Up to 72% savings
- **Flexibility**: Size flexibility within series
- **Suitable for**: Steady-state workloads

**Azure Hybrid Benefit**:
- **License Mobility**: Use existing Windows Server và SQL licenses
- **Cost Savings**: Reduce Azure compute costs
- **Compliance**: License compliance maintained
- **Suitable for**: Organizations with existing licenses

#### Cost Management Tools

**Azure Cost Management**:
- **Cost Analysis**: Historical và forecasted costs
- **Budgets**: Set spending limits và alerts
- **Recommendations**: Cost optimization suggestions
- **Export**: Data export for external analysis

**Azure Advisor**:
- **Cost Recommendations**: Right-sizing suggestions
- **Performance**: Improve application performance
- **Security**: Security best practices
- **Reliability**: Improve service reliability

### 5. Azure DevOps và Automation

#### Azure DevOps Services

**Azure Repos**:
- **Git Repositories**: Distributed version control
- **Team Foundation Version Control**: Centralized version control
- **Branch Policies**: Code quality enforcement
- **Pull Requests**: Code review process

**Azure Pipelines**:
- **CI/CD**: Continuous integration và deployment
- **Multi-platform**: Windows, Linux, macOS
- **Cloud và On-premises**: Hybrid deployment
- **Integration**: Third-party tool integration

**Azure Boards**:
- **Work Item Tracking**: User stories, bugs, tasks
- **Kanban Boards**: Visual work management
- **Backlogs**: Product và sprint backlogs
- **Reporting**: Progress tracking và analytics

#### Infrastructure as Code

**Azure Resource Manager Templates**:
- **JSON Format**: Declarative template language
- **Deployment Modes**: Incremental và complete
- **Nested Templates**: Modular template design
- **Custom Scripts**: PowerShell và Bash extensions

**Terraform on Azure**:
- **Provider**: AzureRM provider for Terraform
- **State Management**: Remote state storage
- **Modules**: Reusable infrastructure components
- **Multi-cloud**: Consistent tooling across clouds

### 6. Azure Hybrid và Multi-cloud

#### Azure Arc

**Azure Arc-enabled Servers**:
- **On-premises Management**: Manage on-premises servers from Azure
- **Policy Compliance**: Apply Azure policies to on-premises
- **Extensions**: Install Azure VM extensions
- **Monitoring**: Azure Monitor for hybrid resources

**Azure Arc-enabled Kubernetes**:
- **Cluster Management**: Manage Kubernetes clusters from Azure
- **GitOps**: Configuration management via Git
- **Policy**: Apply Azure Policy to Kubernetes
- **Extensions**: Deploy Azure services to Kubernetes

#### Azure Stack

**Azure Stack Hub**:
- **On-premises Azure**: Azure services in your datacenter
- **Hybrid Applications**: Consistent development model
- **Disconnected Scenarios**: Air-gapped environments
- **Edge Computing**: Bring compute closer to data

**Azure Stack Edge**:
- **Edge Computing**: AI-enabled edge computing appliance
- **Data Processing**: Local data processing capabilities
- **Azure Integration**: Seamless Azure connectivity
- **IoT**: Industrial IoT scenarios

### 7. Azure Best Practices cho Viettel IDC

#### Design Principles

**Well-Architected Framework**:
- **Cost Optimization**: Optimize costs while maintaining performance
- **Operational Excellence**: Improve operational processes
- **Performance Efficiency**: Use resources efficiently
- **Reliability**: Design for failure và recovery
- **Security**: Protect applications và data

#### Governance Strategy

**Subscription Strategy**:
- **Environment Separation**: Separate dev, test, production
- **Business Unit Alignment**: Align with organizational structure
- **Billing Separation**: Clear cost attribution
- **Compliance**: Meet regulatory requirements

**Naming Conventions**:
- **Consistent Naming**: Standardized resource naming
- **Metadata**: Tags for organization và billing
- **Documentation**: Clear naming documentation
- **Automation**: Automated naming enforcement

#### Security Considerations

**Network Security**:
- **Network Segmentation**: Isolate workloads
- **Just-in-Time Access**: Temporary elevated access
- **Network Monitoring**: Monitor network traffic
- **DDoS Protection**: Protect against attacks

**Identity Security**:
- **Least Privilege**: Minimum required permissions
- **Regular Reviews**: Periodic access reviews
- **Conditional Access**: Risk-based access policies
- **Privileged Identity Management**: Elevated access management

---
*Azure provides a comprehensive cloud platform with enterprise-grade security, scalability, và management capabilities essential for Viettel IDC's cloud transformation journey.*
