# Hands-on Labs - Virtualization & Cloud

## 🎯 Mục tiêu Labs
Áp dụng kiến thức lý thuyết vào thực hành với các scenario thực tế trong môi trường enterprise tại Viettel IDC.

## 🧪 VMware vSphere Labs

### Lab 1: vSphere Infrastructure Setup

#### Lab Environment Requirements
```yaml
Hardware Requirements:
  - Physical Servers: 3x ESXi hosts (minimum)
  - CPU: Intel VT-x or AMD-V support
  - Memory: 32GB per host (minimum)
  - Storage: Shared storage (NFS, iSCSI, or FC)
  - Network: Gigabit Ethernet (minimum)

Software Requirements:
  - VMware ESXi 7.0 or later
  - vCenter Server Appliance 7.0
  - vSphere Client (HTML5)
```

#### Lab 1.1: ESXi Host Installation và Configuration

**Step 1: ESXi Installation**
```bash
# ESXi Installation Checklist
1. Boot from ESXi installation media
2. Accept license agreement
3. Select installation disk
4. Configure root password
5. Configure management network:
   - IP Address: 192.168.100.10
   - Subnet Mask: 255.255.255.0
   - Gateway: 192.168.100.1
   - DNS: 8.8.8.8, 8.8.4.4
6. Complete installation và reboot
```

**Step 2: Post-Installation Configuration**
```bash
# Access ESXi Host Client
https://192.168.100.10/ui

# Configure NTP
1. Navigate to Manage > System > Time & date
2. Enable NTP client
3. Add NTP servers: pool.ntp.org
4. Start NTP service

# Configure SSH (if needed)
1. Navigate to Manage > Services
2. Start SSH service
3. Set to start automatically với host
```

**Step 3: Storage Configuration**
```bash
# Configure shared storage (NFS example)
1. Navigate to Storage > Datastores
2. Click "New datastore"
3. Select "Mount NFS datastore"
4. Configure:
   - Name: shared-storage-01
   - NFS server: 192.168.100.200
   - NFS share: /vol/vmware
   - NFS version: NFS 3
5. Mount datastore
```

#### Lab 1.2: vCenter Server Appliance Deployment

**Step 1: VCSA Deployment**
```powershell
# Download VCSA ISO và mount
# Run installer from mounted ISO
installer\win32\installer.exe

# Stage 1: Deploy VCSA
Target ESXi host: 192.168.100.10
VM name: vcenter-01
Root password: VMware123!
Network settings:
  - IP: 192.168.100.50
  - Subnet: 255.255.255.0
  - Gateway: 192.168.100.1
  - DNS: 8.8.8.8

# Stage 2: Configure VCSA
SSO Domain: vsphere.local
SSO Password: VMware123!
Enable SSH: Yes
```

**Step 2: vCenter Initial Configuration**
```bash
# Access vCenter via web client
https://192.168.100.50/ui

# Create datacenter
1. Right-click on vCenter
2. Select "New Datacenter"
3. Name: ViettelIDC-DC01

# Add ESXi hosts to datacenter
1. Right-click on datacenter
2. Select "Add Host"
3. Host IP: 192.168.100.10
4. Credentials: root/password
5. Complete wizard
```

#### Lab 1.3: Cluster Configuration

**Step 1: Create vSphere Cluster**
```bash
# Create cluster
1. Right-click on datacenter
2. Select "New Cluster"
3. Cluster name: ViettelIDC-Cluster01
4. Enable DRS: Yes
5. Enable HA: Yes
6. Enable vSAN: No (for this lab)

# Move hosts to cluster
1. Drag hosts from datacenter to cluster
2. Confirm move operation
```

**Step 2: Configure DRS**
```bash
# DRS Configuration
1. Select cluster > Configure > DRS
2. DRS Automation: Fully Automated
3. Migration Threshold: Conservative
4. Additional Options:
   - Enable VM Distribution: Yes
   - Enable CPU Over-Commitment: No
```

**Step 3: Configure HA**
```bash
# HA Configuration
1. Select cluster > Configure > HA
2. Admission Control: Enabled
3. Policy: Host failures cluster tolerates: 1
4. VM Monitoring: VM Monitoring only
5. Datastore heartbeating: Select 2 datastores
```

### Lab 2: VM Lifecycle Management

#### Lab 2.1: Create VM Templates

**Step 1: Create Base VM**
```yaml
VM Configuration:
  Name: template-rhel8-base
  Guest OS: Red Hat Enterprise Linux 8 (64-bit)
  CPU: 2 vCPUs
  Memory: 4 GB
  Disk: 40 GB (Thin Provision)
  Network: VM Network
```

**Step 2: OS Installation và Configuration**
```bash
# RHEL 8 Installation
1. Mount RHEL 8 ISO
2. Power on VM
3. Complete OS installation
4. Configure basic settings:
   - Root password
   - Network configuration
   - Install VMware Tools

# Post-installation configuration
# Install VMware Tools
sudo dnf install open-vm-tools

# Configure for template conversion
sudo dnf clean all
sudo rm -rf /var/log/*
sudo history -c
sudo shutdown -h now
```

**Step 3: Convert to Template**
```bash
# Convert VM to template
1. Right-click on VM
2. Select "Template" > "Convert to Template"
3. Confirm conversion
```

#### Lab 2.2: Deploy VMs from Template

**Step 1: Deploy from Template**
```bash
# Deploy new VM
1. Right-click on template
2. Select "New VM from This Template"
3. VM name: web-server-01
4. Select cluster/host
5. Select datastore
6. Customize guest OS:
   - Hostname: web-server-01
   - IP: 192.168.100.101
   - DNS: 8.8.8.8
7. Complete deployment
```

**Step 2: Post-Deployment Configuration**
```bash
# Power on VM và verify
1. Power on VM
2. Console access
3. Verify network connectivity
4. Install additional software as needed
```

### Lab 3: Advanced vSphere Features

#### Lab 3.1: vMotion Configuration

**Step 1: Configure vMotion Network**
```bash
# Create vMotion VMkernel adapter
1. Select host > Configure > Networking
2. VMkernel adapters > Add Networking
3. Connection Type: VMkernel Network Adapter
4. Target Device: New standard switch
5. Network Label: vMotion
6. VLAN ID: 100
7. IP Settings:
   - IP: 192.168.200.10
   - Subnet: 255.255.255.0
8. Enable vMotion: Yes
```

**Step 2: Test vMotion**
```bash
# Perform vMotion
1. Right-click on VM
2. Select "Migrate"
3. Change compute resource only
4. Select destination host
5. Complete migration
6. Verify VM accessibility
```

#### Lab 3.2: Storage vMotion

**Step 1: Add Additional Datastore**
```bash
# Add second datastore
1. Configure shared storage on second LUN
2. Mount as datastore: shared-storage-02
```

**Step 2: Migrate VM Storage**
```bash
# Storage vMotion
1. Right-click on VM
2. Select "Migrate"
3. Change storage only
4. Select destination datastore
5. Virtual disk format: Same as source
6. Complete migration
```

#### Lab 3.3: Snapshot Management

**Step 1: Create Snapshots**
```bash
# Create snapshot
1. Right-click on VM
2. Select "Snapshots" > "Take Snapshot"
3. Name: Before-Update-Install
4. Description: Snapshot before installing updates
5. Include memory: Yes (for running VM)
6. Create snapshot
```

**Step 2: Manage Snapshots**
```bash
# Snapshot operations
# View snapshots
1. Right-click VM > Snapshots > Manage Snapshots

# Revert to snapshot
1. Select snapshot
2. Click "Revert To"

# Delete snapshot
1. Select snapshot
2. Click "Delete"
```

## 🧪 OpenStack Labs

### Lab 4: OpenStack All-in-One Deployment

#### Lab 4.1: DevStack Installation

**Step 1: Environment Preparation**
```bash
# System requirements
OS: Ubuntu 20.04 LTS
CPU: 4 cores
Memory: 8 GB
Disk: 60 GB
Network: Internet connectivity

# Update system
sudo apt update && sudo apt upgrade -y

# Create stack user
sudo useradd -s /bin/bash -d /opt/stack -m stack
echo "stack ALL=(ALL) NOPASSWD: ALL" | sudo tee /etc/sudoers.d/stack
sudo -u stack -i
```

**Step 2: DevStack Download và Configuration**
```bash
# Clone DevStack
cd /opt/stack
git clone https://opendev.org/openstack/devstack

# Create local.conf
cd devstack
cat > local.conf << EOF
[[local|localrc]]
ADMIN_PASSWORD=secret
DATABASE_PASSWORD=\$ADMIN_PASSWORD
RABBIT_PASSWORD=\$ADMIN_PASSWORD
SERVICE_PASSWORD=\$ADMIN_PASSWORD

# Enable services
enable_service rabbit
enable_service mysql
enable_service key

# Nova services
enable_service n-api
enable_service n-cpu
enable_service n-cond
enable_service n-sch
enable_service n-novnc

# Neutron services
enable_service q-svc
enable_service q-agt
enable_service q-dhcp
enable_service q-l3
enable_service q-meta

# Cinder services
enable_service cinder
enable_service c-api
enable_service c-vol
enable_service c-sch

# Glance service
enable_service g-api

# Horizon
enable_service horizon

# Networking
HOST_IP=192.168.100.150
FLOATING_RANGE=192.168.100.224/27
FIXED_RANGE=10.11.12.0/24
FIXED_NETWORK_SIZE=256
FLAT_INTERFACE=eth0
EOF
```

**Step 3: Install OpenStack**
```bash
# Run stack.sh
./stack.sh

# Installation will take 30-60 minutes
# Upon completion, note the access URLs và credentials
```

#### Lab 4.2: OpenStack Basic Operations

**Step 1: Access Dashboard**
```bash
# Access Horizon dashboard
URL: http://192.168.100.150/dashboard
Username: admin
Password: secret
Domain: Default
```

**Step 2: Command Line Setup**
```bash
# Source admin credentials
cd /opt/stack/devstack
source openrc admin

# Verify services
openstack service list
openstack endpoint list
```

**Step 3: Create Project và User**
```bash
# Create project
openstack project create --domain default viettelidc

# Create user
openstack user create --domain default --password-prompt viettel-admin

# Assign role
openstack role add --project viettelidc --user viettel-admin admin
```

### Lab 5: OpenStack Instance Management

#### Lab 5.1: Image Management

**Step 1: Upload Image**
```bash
# Download CirrOS image
wget http://download.cirros-cloud.net/0.5.2/cirros-0.5.2-x86_64-disk.img

# Upload to Glance
openstack image create "cirros-0.5.2" \
  --file cirros-0.5.2-x86_64-disk.img \
  --disk-format qcow2 \
  --container-format bare \
  --public

# Verify image
openstack image list
```

**Step 2: Create Flavor**
```bash
# Create custom flavor
openstack flavor create --vcpus 1 --ram 512 --disk 1 m1.tiny.custom

# List flavors
openstack flavor list
```

#### Lab 5.2: Network Setup

**Step 1: Create Networks**
```bash
# Create provider network
openstack network create --share --external \
  --provider-physical-network provider \
  --provider-network-type flat provider

# Create subnet
openstack subnet create --network provider \
  --allocation-pool start=192.168.100.200,end=192.168.100.220 \
  --dns-nameserver 8.8.8.8 --gateway 192.168.100.1 \
  --subnet-range 192.168.100.0/24 provider

# Create private network
openstack network create private

# Create private subnet
openstack subnet create --network private \
  --dns-nameserver 8.8.8.8 --gateway 192.168.1.1 \
  --subnet-range 192.168.1.0/24 private-subnet
```

**Step 2: Create Router**
```bash
# Create router
openstack router create router1

# Add interface to private subnet
openstack router add subnet router1 private-subnet

# Set gateway
openstack router set router1 --external-gateway provider
```

#### Lab 5.3: Instance Launch

**Step 1: Security Groups**
```bash
# Create security group
openstack security group create web-sg

# Add rules
openstack security group rule create --protocol tcp --dst-port 22 web-sg
openstack security group rule create --protocol tcp --dst-port 80 web-sg
openstack security group rule create --protocol icmp web-sg
```

**Step 2: Launch Instance**
```bash
# Create keypair
openstack keypair create --public-key ~/.ssh/id_rsa.pub mykey

# Launch instance
openstack server create --flavor m1.tiny.custom \
  --image cirros-0.5.2 \
  --nic net-id=private \
  --security-group web-sg \
  --key-name mykey \
  test-instance

# Verify instance
openstack server list
```

**Step 3: Floating IP**
```bash
# Create floating IP
openstack floating ip create provider

# Assign to instance
openstack server add floating ip test-instance 192.168.100.201

# Test connectivity
ping 192.168.100.201
ssh cirros@192.168.100.201
```

## 🧪 AWS Labs

### Lab 6: AWS Infrastructure Setup

#### Lab 6.1: VPC và Networking

**Step 1: Create VPC**
```bash
# Create VPC
aws ec2 create-vpc --cidr-block 10.0.0.0/16 --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=ViettelIDC-VPC}]'

# Note VPC ID from output
VPC_ID=vpc-xxxxxxxxx

# Enable DNS hostnames
aws ec2 modify-vpc-attribute --vpc-id $VPC_ID --enable-dns-hostnames
```

**Step 2: Create Subnets**
```bash
# Create public subnet
aws ec2 create-subnet --vpc-id $VPC_ID --cidr-block 10.0.1.0/24 --availability-zone us-east-1a --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=Public-Subnet-1a}]'

PUBLIC_SUBNET_ID=subnet-xxxxxxxxx

# Create private subnet
aws ec2 create-subnet --vpc-id $VPC_ID --cidr-block 10.0.2.0/24 --availability-zone us-east-1a --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=Private-Subnet-1a}]'

PRIVATE_SUBNET_ID=subnet-yyyyyyyyy
```

**Step 3: Internet Gateway và Routing**
```bash
# Create Internet Gateway
aws ec2 create-internet-gateway --tag-specifications 'ResourceType=internet-gateway,Tags=[{Key=Name,Value=ViettelIDC-IGW}]'

IGW_ID=igw-zzzzzzzzz

# Attach to VPC
aws ec2 attach-internet-gateway --vpc-id $VPC_ID --internet-gateway-id $IGW_ID

# Create route table for public subnet
aws ec2 create-route-table --vpc-id $VPC_ID --tag-specifications 'ResourceType=route-table,Tags=[{Key=Name,Value=Public-RT}]'

PUBLIC_RT_ID=rtb-aaaaaaaaa

# Add route to internet
aws ec2 create-route --route-table-id $PUBLIC_RT_ID --destination-cidr-block 0.0.0.0/0 --gateway-id $IGW_ID

# Associate route table với public subnet
aws ec2 associate-route-table --subnet-id $PUBLIC_SUBNET_ID --route-table-id $PUBLIC_RT_ID
```

#### Lab 6.2: Security Groups

**Step 1: Create Security Groups**
```bash
# Web server security group
aws ec2 create-security-group --group-name web-sg --description "Web server security group" --vpc-id $VPC_ID

WEB_SG_ID=sg-bbbbbbbbb

# Add rules
aws ec2 authorize-security-group-ingress --group-id $WEB_SG_ID --protocol tcp --port 22 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --group-id $WEB_SG_ID --protocol tcp --port 80 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --group-id $WEB_SG_ID --protocol tcp --port 443 --cidr 0.0.0.0/0

# Database security group
aws ec2 create-security-group --group-name db-sg --description "Database security group" --vpc-id $VPC_ID

DB_SG_ID=sg-ccccccccc

# Allow MySQL from web servers
aws ec2 authorize-security-group-ingress --group-id $DB_SG_ID --protocol tcp --port 3306 --source-group $WEB_SG_ID
```

#### Lab 6.3: EC2 Instance Launch

**Step 1: Create Key Pair**
```bash
# Create key pair
aws ec2 create-key-pair --key-name viettelidc-key --query 'KeyMaterial' --output text > viettelidc-key.pem
chmod 400 viettelidc-key.pem
```

**Step 2: Launch Instances**
```bash
# Launch web server
aws ec2 run-instances \
  --image-id ami-0abcdef1234567890 \
  --count 1 \
  --instance-type t3.micro \
  --key-name viettelidc-key \
  --security-group-ids $WEB_SG_ID \
  --subnet-id $PUBLIC_SUBNET_ID \
  --associate-public-ip-address \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=Web-Server-01}]'

# Launch database server
aws ec2 run-instances \
  --image-id ami-0abcdef1234567890 \
  --count 1 \
  --instance-type t3.micro \
  --key-name viettelidc-key \
  --security-group-ids $DB_SG_ID \
  --subnet-id $PRIVATE_SUBNET_ID \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=DB-Server-01}]'
```

### Lab 7: AWS Auto Scaling

#### Lab 7.1: Load Balancer Setup

**Step 1: Create Application Load Balancer**
```bash
# Create load balancer
aws elbv2 create-load-balancer \
  --name viettelidc-alb \
  --subnets $PUBLIC_SUBNET_ID subnet-another-public \
  --security-groups $WEB_SG_ID

ALB_ARN=arn:aws:elasticloadbalancing:...

# Create target group
aws elbv2 create-target-group \
  --name web-targets \
  --protocol HTTP \
  --port 80 \
  --vpc-id $VPC_ID \
  --health-check-path /health

TG_ARN=arn:aws:elasticloadbalancing:...

# Create listener
aws elbv2 create-listener \
  --load-balancer-arn $ALB_ARN \
  --protocol HTTP \
  --port 80 \
  --default-actions Type=forward,TargetGroupArn=$TG_ARN
```

#### Lab 7.2: Auto Scaling Configuration

**Step 1: Create Launch Template**
```bash
# Create launch template
aws ec2 create-launch-template \
  --launch-template-name web-server-template \
  --launch-template-data '{
    "ImageId": "ami-0abcdef1234567890",
    "InstanceType": "t3.micro",
    "KeyName": "viettelidc-key",
    "SecurityGroupIds": ["'$WEB_SG_ID'"],
    "UserData": "'$(base64 -w 0 user-data.sh)'",
    "TagSpecifications": [{
      "ResourceType": "instance",
      "Tags": [{"Key": "Name", "Value": "Auto-Web-Server"}]
    }]
  }'
```

**Step 2: Create Auto Scaling Group**
```bash
# Create Auto Scaling Group
aws autoscaling create-auto-scaling-group \
  --auto-scaling-group-name web-asg \
  --launch-template LaunchTemplateName=web-server-template,Version='$Latest' \
  --min-size 1 \
  --max-size 5 \
  --desired-capacity 2 \
  --target-group-arns $TG_ARN \
  --vpc-zone-identifier "$PUBLIC_SUBNET_ID,subnet-another-public"

# Create scaling policies
aws autoscaling put-scaling-policy \
  --auto-scaling-group-name web-asg \
  --policy-name scale-up \
  --policy-type TargetTrackingScaling \
  --target-tracking-configuration '{
    "TargetValue": 70.0,
    "PredefinedMetricSpecification": {
      "PredefinedMetricType": "ASGAverageCPUUtilization"
    }
  }'
```

## 🧪 Azure Labs

### Lab 8: Azure Resource Deployment

#### Lab 8.1: Resource Group và Virtual Network

**Step 1: Create Resource Group**
```powershell
# Login to Azure
Connect-AzAccount

# Create resource group
New-AzResourceGroup -Name "ViettelIDC-RG" -Location "Southeast Asia"
```

**Step 2: Create Virtual Network**
```powershell
# Create virtual network
$subnet1 = New-AzVirtualNetworkSubnetConfig -Name "Web-Subnet" -AddressPrefix "10.0.1.0/24"
$subnet2 = New-AzVirtualNetworkSubnetConfig -Name "DB-Subnet" -AddressPrefix "10.0.2.0/24"

New-AzVirtualNetwork -Name "ViettelIDC-VNet" -ResourceGroupName "ViettelIDC-RG" -Location "Southeast Asia" -AddressPrefix "10.0.0.0/16" -Subnet $subnet1, $subnet2
```

#### Lab 8.2: Virtual Machine Deployment

**Step 1: Create Network Security Group**
```powershell
# Create NSG rules
$rule1 = New-AzNetworkSecurityRuleConfig -Name "Allow-HTTP" -Description "Allow HTTP" -Access Allow -Protocol Tcp -Direction Inbound -Priority 1000 -SourceAddressPrefix Internet -SourcePortRange * -DestinationAddressPrefix * -DestinationPortRange 80

$rule2 = New-AzNetworkSecurityRuleConfig -Name "Allow-SSH" -Description "Allow SSH" -Access Allow -Protocol Tcp -Direction Inbound -Priority 1001 -SourceAddressPrefix Internet -SourcePortRange * -DestinationAddressPrefix * -DestinationPortRange 22

# Create NSG
New-AzNetworkSecurityGroup -ResourceGroupName "ViettelIDC-RG" -Location "Southeast Asia" -Name "Web-NSG" -SecurityRules $rule1, $rule2
```

**Step 2: Deploy Virtual Machine**
```powershell
# Create VM configuration
$vmConfig = New-AzVMConfig -VMName "Web-VM-01" -VMSize "Standard_B2s"

# Set operating system
$vmConfig = Set-AzVMOperatingSystem -VM $vmConfig -Linux -ComputerName "web-vm-01" -Credential (Get-Credential)

# Set source image
$vmConfig = Set-AzVMSourceImage -VM $vmConfig -PublisherName "Canonical" -Offer "0001-com-ubuntu-server-focal" -Skus "20_04-lts-gen2" -Version "latest"

# Create network interface
$vnet = Get-AzVirtualNetwork -Name "ViettelIDC-VNet" -ResourceGroupName "ViettelIDC-RG"
$subnet = Get-AzVirtualNetworkSubnetConfig -Name "Web-Subnet" -VirtualNetwork $vnet
$nsg = Get-AzNetworkSecurityGroup -Name "Web-NSG" -ResourceGroupName "ViettelIDC-RG"

$pip = New-AzPublicIpAddress -Name "Web-VM-01-PIP" -ResourceGroupName "ViettelIDC-RG" -Location "Southeast Asia" -AllocationMethod Static

$nic = New-AzNetworkInterface -Name "Web-VM-01-NIC" -ResourceGroupName "ViettelIDC-RG" -Location "Southeast Asia" -SubnetId $subnet.Id -PublicIpAddressId $pip.Id -NetworkSecurityGroupId $nsg.Id

# Add NIC to VM configuration
$vmConfig = Add-AzVMNetworkInterface -VM $vmConfig -Id $nic.Id

# Create virtual machine
New-AzVM -ResourceGroupName "ViettelIDC-RG" -Location "Southeast Asia" -VM $vmConfig
```

#### Lab 8.3: Azure Resource Manager Templates

**Step 1: Create ARM Template**
```json
{
    "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
    "contentVersion": "1.0.0.0",
    "parameters": {
        "adminUsername": {
            "type": "string",
            "metadata": {
                "description": "Admin username for the Virtual Machine"
            }
        },
        "adminPassword": {
            "type": "securestring",
            "metadata": {
                "description": "Admin password for the Virtual Machine"
            }
        }
    },
    "variables": {
        "storageAccountName": "[concat('storage', uniqueString(resourceGroup().id))]",
        "vnetName": "ViettelIDC-VNet",
        "subnetName": "Web-Subnet",
        "publicIPName": "VM-PublicIP",
        "vmName": "WebServer-VM",
        "nicName": "VM-NetworkInterface"
    },
    "resources": [
        {
            "type": "Microsoft.Storage/storageAccounts",
            "apiVersion": "2021-04-01",
            "name": "[variables('storageAccountName')]",
            "location": "[resourceGroup().location]",
            "sku": {
                "name": "Standard_LRS"
            },
            "kind": "StorageV2"
        },
        {
            "type": "Microsoft.Network/virtualNetworks",
            "apiVersion": "2021-02-01",
            "name": "[variables('vnetName')]",
            "location": "[resourceGroup().location]",
            "properties": {
                "addressSpace": {
                    "addressPrefixes": [
                        "10.0.0.0/16"
                    ]
                },
                "subnets": [
                    {
                        "name": "[variables('subnetName')]",
                        "properties": {
                            "addressPrefix": "10.0.1.0/24"
                        }
                    }
                ]
            }
        }
    ],
    "outputs": {
        "storageAccountName": {
            "type": "string",
            "value": "[variables('storageAccountName')]"
        }
    }
}
```

**Step 2: Deploy Template**
```powershell
# Deploy ARM template
New-AzResourceGroupDeployment -ResourceGroupName "ViettelIDC-RG" -TemplateFile "azuredeploy.json" -adminUsername "azureuser" -adminPassword (ConvertTo-SecureString "P@ssw0rd123!" -AsPlainText -Force)
```

## 🎯 Lab Assessment Criteria

### Technical Skills Assessment
1. **Infrastructure Setup**: Proper configuration of virtualization infrastructure
2. **Resource Management**: Efficient use of compute, storage, và network resources
3. **Security Implementation**: Proper security group và firewall configurations
4. **Automation**: Use of templates và scripts for deployment
5. **Troubleshooting**: Ability to diagnose và resolve issues

### Best Practices Evaluation
1. **Documentation**: Proper documentation of procedures
2. **Naming Conventions**: Consistent resource naming
3. **Security Hardening**: Implementation of security best practices
4. **Monitoring**: Setup of appropriate monitoring và alerting
5. **Cost Optimization**: Efficient resource utilization

### Real-world Scenarios
1. **Disaster Recovery**: Test backup và recovery procedures
2. **Scaling**: Demonstrate auto-scaling capabilities
3. **Migration**: Migrate workloads between environments
4. **Integration**: Integrate multiple cloud services
5. **Compliance**: Ensure compliance với enterprise policies

---
*These hands-on labs provide practical experience với enterprise virtualization và cloud technologies essential for Viettel IDC engineers.*
