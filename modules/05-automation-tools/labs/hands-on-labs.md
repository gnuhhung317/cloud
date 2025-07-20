# Consolidated Hands-On Labs - Module 5: Automation Tools

## 🎯 Lab Overview
Đây là collection tổng hợp của tất cả hands-on labs cho Module 5, được tổ chức theo progressive difficulty và practical applications. Các labs này được thiết kế để học viên có thể practice từ basic concepts đến advanced enterprise scenarios.

## 📚 Lab Categories

### Foundation Labs (Week 1)
- **Lab 1**: Ansible Basics và First Playbook
- **Lab 2**: Terraform Fundamentals và State Management
- **Lab 3**: Infrastructure Provisioning với Terraform
- **Lab 4**: Configuration Management với Ansible

### Intermediate Labs (Week 2)
- **Lab 5**: Advanced Ansible với Roles và Vault
- **Lab 6**: Terraform Modules và Testing
- **Lab 7**: CI/CD Integration với Infrastructure Code
- **Lab 8**: Multi-Environment Management

### Advanced Labs (Week 3)
- **Lab 9**: Ansible + Terraform Integration
- **Lab 10**: Kubernetes Automation
- **Lab 11**: Multi-Cloud Infrastructure
- **Lab 12**: Security Automation

## 🚀 Getting Started

### Prerequisites Checklist
```bash
# System Requirements
- [ ] Linux/macOS/WSL2 environment
- [ ] Python 3.8+ installed
- [ ] Git configured
- [ ] SSH key pair generated
- [ ] Cloud provider accounts (AWS/Azure)

# Tool Installation
- [ ] Ansible 6.0+ installed
- [ ] Terraform 1.5+ installed
- [ ] Docker installed và running
- [ ] kubectl installed
- [ ] AWS CLI configured
- [ ] Azure CLI configured

# Verification Commands
ansible --version
terraform --version
docker --version
kubectl version --client
aws sts get-caller-identity
az account show
```

### Lab Environment Setup
```bash
# Clone lab repository
git clone https://github.com/viettel-idc/automation-labs.git
cd automation-labs

# Setup Python virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate.ps1  # Windows PowerShell

# Install Python dependencies
pip install -r requirements.txt

# Verify setup
ansible-playbook --version
terraform version
```

## 📖 Detailed Lab Instructions

### Lab 1: Ansible Basics và First Playbook
**Duration**: 2-3 hours  
**Difficulty**: Beginner  
**Objective**: Hiểu Ansible fundamentals và viết first playbook

#### Lab Setup
```bash
# Create lab directory
mkdir -p labs/lab1-ansible-basics
cd labs/lab1-ansible-basics

# Create inventory file
cat > inventory.ini << EOF
[webservers]
web1 ansible_host=192.168.1.10 ansible_user=ubuntu
web2 ansible_host=192.168.1.11 ansible_user=ubuntu

[databases]
db1 ansible_host=192.168.1.20 ansible_user=ubuntu

[all:vars]
ansible_ssh_private_key_file=~/.ssh/id_rsa
EOF
```

#### First Playbook
```yaml
# playbook.yml
---
- name: Basic Server Configuration
  hosts: all
  become: yes
  gather_facts: yes
  
  vars:
    packages_to_install:
      - curl
      - wget
      - git
      - htop
      - vim
    
    users_to_create:
      - name: devops
        groups: sudo
        shell: /bin/bash
  
  tasks:
    - name: Display system information
      debug:
        msg: |
          Hostname: {{ ansible_hostname }}
          OS: {{ ansible_distribution }} {{ ansible_distribution_version }}
          Architecture: {{ ansible_architecture }}
          IP Address: {{ ansible_default_ipv4.address }}
    
    - name: Update package cache
      apt:
        update_cache: yes
        cache_valid_time: 3600
      when: ansible_os_family == "Debian"
    
    - name: Install essential packages
      package:
        name: "{{ packages_to_install }}"
        state: present
    
    - name: Create users
      user:
        name: "{{ item.name }}"
        groups: "{{ item.groups }}"
        shell: "{{ item.shell }}"
        create_home: yes
        append: yes
      loop: "{{ users_to_create }}"
    
    - name: Configure timezone
      timezone:
        name: Asia/Ho_Chi_Minh
    
    - name: Setup basic firewall
      ufw:
        state: enabled
        policy: deny
        direction: incoming
    
    - name: Allow SSH
      ufw:
        rule: allow
        port: 22
        proto: tcp

- name: Configure Web Servers
  hosts: webservers
  become: yes
  
  tasks:
    - name: Install nginx
      package:
        name: nginx
        state: present
    
    - name: Start và enable nginx
      service:
        name: nginx
        state: started
        enabled: yes
    
    - name: Allow HTTP traffic
      ufw:
        rule: allow
        port: 80
        proto: tcp
    
    - name: Create custom index page
      copy:
        content: |
          <html>
            <head><title>{{ ansible_hostname }}</title></head>
            <body>
              <h1>Welcome to {{ ansible_hostname }}</h1>
              <p>Server IP: {{ ansible_default_ipv4.address }}</p>
              <p>Managed by Ansible</p>
            </body>
          </html>
        dest: /var/www/html/index.html
        owner: www-data
        group: www-data
        mode: '0644'
      notify: restart nginx

- name: Configure Database Servers
  hosts: databases
  become: yes
  
  tasks:
    - name: Install PostgreSQL
      package:
        name:
          - postgresql
          - postgresql-contrib
          - python3-psycopg2
        state: present
    
    - name: Start và enable PostgreSQL
      service:
        name: postgresql
        state: started
        enabled: yes
    
    - name: Create application database
      postgresql_db:
        name: webapp
        encoding: UTF-8
      become_user: postgres
    
    - name: Create database user
      postgresql_user:
        name: webapp_user
        password: secure_password
        db: webapp
        priv: ALL
      become_user: postgres
  
  handlers:
    - name: restart nginx
      service:
        name: nginx
        state: restarted
```

#### Lab Exercises
```bash
# Exercise 1: Run the playbook
ansible-playbook -i inventory.ini playbook.yml

# Exercise 2: Check specific facts
ansible all -i inventory.ini -m setup -a "filter=ansible_distribution*"

# Exercise 3: Ad-hoc commands
ansible webservers -i inventory.ini -m service -a "name=nginx state=restarted" --become

# Exercise 4: Test connectivity
ansible all -i inventory.ini -m ping

# Exercise 5: Check disk space
ansible all -i inventory.ini -m shell -a "df -h /" --become
```

### Lab 2: Terraform Fundamentals và State Management
**Duration**: 3-4 hours  
**Difficulty**: Beginner  
**Objective**: Học Terraform basics, HCL syntax, và state management

#### Lab Setup
```bash
# Create lab directory
mkdir -p labs/lab2-terraform-basics
cd labs/lab2-terraform-basics

# Create provider configuration
cat > versions.tf << EOF
terraform {
  required_version = ">= 1.5"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Environment = var.environment
      Project     = var.project_name
      ManagedBy   = "Terraform"
      Owner       = var.owner
    }
  }
}
EOF
```

#### Variables Configuration
```hcl
# variables.tf
variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-west-2"
  
  validation {
    condition     = contains(["us-west-2", "us-east-1", "eu-west-1"], var.aws_region)
    error_message = "AWS region must be one of: us-west-2, us-east-1, eu-west-1."
  }
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
  
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "terraform-lab"
}

variable "owner" {
  description = "Resource owner"
  type        = string
  default     = "devops-team"
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "List of availability zones"
  type        = list(string)
  default     = ["us-west-2a", "us-west-2b", "us-west-2c"]
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"
}

variable "key_name" {
  description = "AWS Key Pair name"
  type        = string
  default     = ""
}

# Complex variable examples
variable "database_config" {
  description = "Database configuration"
  type = object({
    engine         = string
    engine_version = string
    instance_class = string
    allocated_storage = number
    max_allocated_storage = number
    backup_retention_period = number
    multi_az = bool
  })
  
  default = {
    engine         = "postgres"
    engine_version = "13.7"
    instance_class = "db.t3.micro"
    allocated_storage = 20
    max_allocated_storage = 100
    backup_retention_period = 7
    multi_az = false
  }
}

variable "tags" {
  description = "Additional tags for resources"
  type        = map(string)
  default     = {}
}
```

#### Main Infrastructure
```hcl
# main.tf
# Random ID for unique naming
resource "random_id" "suffix" {
  byte_length = 4
}

# Local values
locals {
  common_tags = merge({
    Environment = var.environment
    Project     = var.project_name
    ManagedBy   = "Terraform"
    Owner       = var.owner
    CreatedAt   = timestamp()
  }, var.tags)
  
  name_prefix = "${var.project_name}-${var.environment}"
  
  # Calculate subnets
  public_subnets = [
    for i, az in var.availability_zones :
    cidrsubnet(var.vpc_cidr, 8, i)
  ]
  
  private_subnets = [
    for i, az in var.availability_zones :
    cidrsubnet(var.vpc_cidr, 8, i + 100)
  ]
}

# Data sources
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical
  
  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*"]
  }
  
  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

data "aws_caller_identity" "current" {}

# VPC
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-vpc"
  })
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
  
  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-igw"
  })
}

# Public Subnets
resource "aws_subnet" "public" {
  count = length(var.availability_zones)
  
  vpc_id                  = aws_vpc.main.id
  cidr_block              = local.public_subnets[count.index]
  availability_zone       = var.availability_zones[count.index]
  map_public_ip_on_launch = true
  
  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-public-${count.index + 1}"
    Type = "public"
  })
}

# Private Subnets
resource "aws_subnet" "private" {
  count = length(var.availability_zones)
  
  vpc_id            = aws_vpc.main.id
  cidr_block        = local.private_subnets[count.index]
  availability_zone = var.availability_zones[count.index]
  
  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-private-${count.index + 1}"
    Type = "private"
  })
}

# NAT Gateway
resource "aws_eip" "nat" {
  count = length(var.availability_zones)
  
  domain = "vpc"
  
  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-eip-${count.index + 1}"
  })
  
  depends_on = [aws_internet_gateway.main]
}

resource "aws_nat_gateway" "main" {
  count = length(var.availability_zones)
  
  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[count.index].id
  
  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-nat-${count.index + 1}"
  })
}

# Route Tables
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }
  
  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-public-rt"
  })
}

resource "aws_route_table" "private" {
  count = length(var.availability_zones)
  
  vpc_id = aws_vpc.main.id
  
  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.main[count.index].id
  }
  
  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-private-rt-${count.index + 1}"
  })
}

# Route Table Associations
resource "aws_route_table_association" "public" {
  count = length(var.availability_zones)
  
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "private" {
  count = length(var.availability_zones)
  
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private[count.index].id
}

# Security Groups
resource "aws_security_group" "web" {
  name_prefix = "${local.name_prefix}-web-"
  vpc_id      = aws_vpc.main.id
  description = "Security group for web servers"
  
  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  ingress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
  }
  
  egress {
    description = "All outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-web-sg"
  })
  
  lifecycle {
    create_before_destroy = true
  }
}

# EC2 Instances
resource "aws_instance" "web" {
  count = 2
  
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.instance_type
  key_name               = var.key_name != "" ? var.key_name : null
  subnet_id              = aws_subnet.public[count.index % length(aws_subnet.public)].id
  vpc_security_group_ids = [aws_security_group.web.id]
  
  user_data = base64encode(templatefile("${path.module}/user_data.sh", {
    hostname = "${local.name_prefix}-web-${count.index + 1}"
    environment = var.environment
  }))
  
  root_block_device {
    volume_type = "gp3"
    volume_size = 20
    encrypted   = true
    
    tags = merge(local.common_tags, {
      Name = "${local.name_prefix}-web-${count.index + 1}-root"
    })
  }
  
  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-web-${count.index + 1}"
    Type = "WebServer"
  })
  
  lifecycle {
    create_before_destroy = true
  }
}

# RDS Database
resource "aws_db_subnet_group" "main" {
  name       = "${local.name_prefix}-db-subnet-group"
  subnet_ids = aws_subnet.private[*].id
  
  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-db-subnet-group"
  })
}

resource "aws_security_group" "database" {
  name_prefix = "${local.name_prefix}-db-"
  vpc_id      = aws_vpc.main.id
  description = "Security group for database"
  
  ingress {
    description     = "PostgreSQL"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.web.id]
  }
  
  egress {
    description = "All outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-db-sg"
  })
  
  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_db_instance" "main" {
  identifier = "${local.name_prefix}-db-${random_id.suffix.hex}"
  
  engine         = var.database_config.engine
  engine_version = var.database_config.engine_version
  instance_class = var.database_config.instance_class
  
  allocated_storage     = var.database_config.allocated_storage
  max_allocated_storage = var.database_config.max_allocated_storage
  storage_type          = "gp3"
  storage_encrypted     = true
  
  db_name  = "webapp"
  username = "admin"
  password = random_password.db_password.result
  
  vpc_security_group_ids = [aws_security_group.database.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name
  
  backup_retention_period = var.database_config.backup_retention_period
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
  
  multi_az = var.database_config.multi_az
  
  skip_final_snapshot = var.environment != "prod"
  deletion_protection = var.environment == "prod"
  
  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-database"
  })
}

resource "random_password" "db_password" {
  length  = 16
  special = true
}
```

#### User Data Script
```bash
# user_data.sh
#!/bin/bash

# Update system
apt-get update -y
apt-get upgrade -y

# Set hostname
hostnamectl set-hostname ${hostname}
echo "127.0.0.1 ${hostname}" >> /etc/hosts

# Install basic packages
apt-get install -y \
    curl \
    wget \
    unzip \
    git \
    htop \
    nginx \
    awscli

# Configure nginx
systemctl start nginx
systemctl enable nginx

# Create custom index page
cat > /var/www/html/index.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>${hostname}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .info { background: #f0f0f0; padding: 20px; border-radius: 5px; }
    </style>
</head>
<body>
    <h1>Welcome to ${hostname}</h1>
    <div class="info">
        <h2>Server Information</h2>
        <p><strong>Environment:</strong> ${environment}</p>
        <p><strong>Hostname:</strong> ${hostname}</p>
        <p><strong>Instance ID:</strong> $(curl -s http://169.254.169.254/latest/meta-data/instance-id)</p>
        <p><strong>Instance Type:</strong> $(curl -s http://169.254.169.254/latest/meta-data/instance-type)</p>
        <p><strong>Public IP:</strong> $(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)</p>
        <p><strong>Private IP:</strong> $(curl -s http://169.254.169.254/latest/meta-data/local-ipv4)</p>
        <p><strong>Managed by:</strong> Terraform</p>
    </div>
</body>
</html>
EOF

# Setup CloudWatch agent (optional)
if command -v aws &> /dev/null; then
    wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
    dpkg -i amazon-cloudwatch-agent.deb
fi

# Create health check endpoint
echo "OK" > /var/www/html/health

# Log completion
echo "User data script completed at $(date)" >> /var/log/user-data.log
```

#### Outputs
```hcl
# outputs.tf
output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

output "vpc_cidr" {
  description = "VPC CIDR block"
  value       = aws_vpc.main.cidr_block
}

output "public_subnet_ids" {
  description = "Public subnet IDs"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "Private subnet IDs"
  value       = aws_subnet.private[*].id
}

output "web_instance_ids" {
  description = "Web server instance IDs"
  value       = aws_instance.web[*].id
}

output "web_instance_public_ips" {
  description = "Web server public IP addresses"
  value       = aws_instance.web[*].public_ip
}

output "web_instance_private_ips" {
  description = "Web server private IP addresses"
  value       = aws_instance.web[*].private_ip
}

output "database_endpoint" {
  description = "Database endpoint"
  value       = aws_db_instance.main.endpoint
  sensitive   = true
}

output "database_port" {
  description = "Database port"
  value       = aws_db_instance.main.port
}

# Complex outputs
output "instance_details" {
  description = "Detailed information about web instances"
  value = {
    for i, instance in aws_instance.web : 
    "web-${i + 1}" => {
      id         = instance.id
      public_ip  = instance.public_ip
      private_ip = instance.private_ip
      az         = instance.availability_zone
      subnet_id  = instance.subnet_id
    }
  }
}

output "infrastructure_summary" {
  description = "Infrastructure summary"
  value = {
    project_name    = var.project_name
    environment     = var.environment
    aws_region      = var.aws_region
    vpc_cidr        = var.vpc_cidr
    public_subnets  = length(aws_subnet.public)
    private_subnets = length(aws_subnet.private)
    web_instances   = length(aws_instance.web)
    database_engine = aws_db_instance.main.engine
    created_at      = timestamp()
  }
}
```

#### Lab Exercises
```bash
# Exercise 1: Initialize và plan
terraform init
terraform plan -out=tfplan

# Exercise 2: Apply infrastructure
terraform apply tfplan

# Exercise 3: Check state
terraform state list
terraform state show aws_vpc.main

# Exercise 4: Update variables
echo 'instance_type = "t3.small"' >> terraform.tfvars
terraform plan

# Exercise 5: Import existing resource (advanced)
terraform import aws_s3_bucket.example my-existing-bucket

# Exercise 6: Workspace management
terraform workspace new dev
terraform workspace new staging
terraform workspace select dev

# Exercise 7: State manipulation
terraform state mv aws_instance.web[0] aws_instance.web_primary
terraform state rm aws_instance.web[1]

# Exercise 8: Destroy specific resource
terraform destroy -target=aws_instance.web[1]

# Exercise 9: Complete cleanup
terraform destroy
```

### Lab 3-12: [Subsequent Labs]
*[Due to length constraints, I'll provide the structure for remaining labs]*

#### Lab 3: Infrastructure Provisioning với Terraform
- Advanced Terraform patterns
- Module development
- Remote state management
- Terraform Cloud integration

#### Lab 4: Configuration Management với Ansible
- Complex playbook development
- Role composition
- Variable precedence
- Error handling strategies

#### Lab 5: Advanced Ansible với Roles và Vault
- Custom role development
- Ansible Vault encryption
- Dynamic inventory
- Testing với Molecule

#### Lab 6: Terraform Modules và Testing
- Module development best practices
- Testing với Terratest
- Module publishing
- Version management

#### Lab 7: CI/CD Integration với Infrastructure Code
- GitHub Actions workflows
- GitLab CI pipelines
- Azure DevOps integration
- Security scanning integration

#### Lab 8: Multi-Environment Management
- Environment-specific configurations
- Promotion workflows
- Blue-green deployments
- Canary releases

#### Lab 9: Ansible + Terraform Integration
- Combined workflows
- State sharing strategies
- Dynamic inventory generation
- Complete automation pipelines

#### Lab 10: Kubernetes Automation
- EKS/AKS/GKE provisioning
- Kubernetes resource management
- Helm chart deployment
- GitOps workflows

#### Lab 11: Multi-Cloud Infrastructure
- Cross-cloud networking
- Unified management
- Cost optimization
- Disaster recovery

#### Lab 12: Security Automation
- Compliance scanning
- Vulnerability assessment
- Security hardening
- Incident response automation

## 🎯 Lab Assessment

### Individual Lab Assessment
Each lab includes:
- **Practical Tasks** (60%): Hands-on implementation
- **Documentation** (20%): Lab documentation và troubleshooting
- **Code Quality** (20%): Clean, maintainable code

### Final Lab Portfolio
Students must submit:
- **Complete Lab Solutions**: All 12 labs implemented
- **Integration Project**: Combining multiple labs
- **Documentation Portfolio**: Comprehensive documentation
- **Presentation**: Demo và knowledge transfer

## 📚 Additional Resources

### Documentation Links
- [Ansible Documentation](https://docs.ansible.com/)
- [Terraform Documentation](https://www.terraform.io/docs)
- [AWS Provider Documentation](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [Ansible Galaxy](https://galaxy.ansible.com/)

### Community Resources
- [Terraform Modules Registry](https://registry.terraform.io/)
- [Ansible Collections](https://galaxy.ansible.com/)
- [Infrastructure as Code Best Practices](https://www.terraform.io/docs/cloud/guides/recommended-practices/)

### Certification Preparation
- [HashiCorp Certified: Terraform Associate](https://www.hashicorp.com/certification/terraform-associate)
- [Red Hat Certified Specialist in Ansible Automation](https://www.redhat.com/en/services/certification/rhcs-ansible-automation)

---

*Lưu ý: Tất cả labs được thiết kế để progressive learning, mỗi lab builds upon previous knowledge và introduces new concepts systematically.*
