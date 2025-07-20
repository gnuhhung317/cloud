# Terraform Fundamentals - Infrastructure as Code

## 🎯 Mục tiêu Học tập
- Hiểu rõ kiến trúc và nguyên lý hoạt động của Terraform
- Thành thạo HCL (HashiCorp Configuration Language)
- Nắm vững State Management và Provider concepts
- Áp dụng Terraform trong môi trường enterprise

## 1. Terraform Architecture và Core Concepts

### 1.1 Terraform Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Terraform CLI  │    │   Terraform    │    │   Providers     │
│                 │───▶│     Core        │───▶│                 │
│ • Plan          │    │                 │    │ • AWS          │
│ • Apply         │    │ • Graph Engine  │    │ • Azure        │
│ • Destroy       │    │ • State Manager │    │ • GCP          │
└─────────────────┘    │ • Resource      │    │ • VMware       │
                       │   Manager       │    └─────────────────┘
                       └─────────────────┘              │
                                 │                      │
                       ┌─────────────────┐    ┌─────────────────┐
                       │  Configuration  │    │   Target        │
                       │     Files       │    │ Infrastructure  │
                       │                 │    │                 │
                       │ • .tf files     │    │ • Servers       │
                       │ • Variables     │    │ • Networks      │
                       │ • Outputs       │    │ • Storage       │
                       └─────────────────┘    └─────────────────┘
```

### 1.2 Core Components

#### Terraform Core
- **Resource Graph**: Quản lý dependencies giữa resources
- **State Manager**: Tracking trạng thái hiện tại của infrastructure
- **Plan Engine**: Tính toán changes cần thiết
- **Apply Engine**: Thực thi changes

#### Providers
- **Resource Providers**: AWS, Azure, GCP, VMware
- **Data Providers**: External APIs, databases
- **Utility Providers**: Random, template, local

#### Configuration Files
- **Resource Definitions**: Infrastructure components
- **Variables**: Input parameters
- **Outputs**: Return values
- **Modules**: Reusable components

### 1.3 Terraform Workflow

```
1. Write Configuration (.tf files)
        ↓
2. Initialize (terraform init)
        ↓
3. Plan (terraform plan)
        ↓
4. Apply (terraform apply)
        ↓
5. Manage State (terraform.tfstate)
```

## 2. HCL (HashiCorp Configuration Language)

### 2.1 Basic Syntax và Structure

#### Resource Declaration
```hcl
# Basic resource syntax
resource "provider_type" "resource_name" {
  argument_name = argument_value
  
  # Nested blocks
  nested_block {
    nested_argument = value
  }
}

# Example: AWS EC2 Instance
resource "aws_instance" "web_server" {
  ami           = "ami-0c02fb55956c7d316"
  instance_type = "t3.micro"
  
  # Tags block
  tags = {
    Name        = "WebServer"
    Environment = "Production"
  }
}
```

#### Data Sources
```hcl
# Data source to query existing resources
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

# Using data source in resource
resource "aws_instance" "example" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = "t3.micro"
}
```

#### Variables
```hcl
# Variable definitions
variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"
  
  validation {
    condition = can(regex("^t[23]\\.", var.instance_type))
    error_message = "Instance type must be a t2 or t3 instance."
  }
}

variable "environment" {
  description = "Environment name"
  type        = string
  
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "availability_zones" {
  description = "List of availability zones"
  type        = list(string)
  default     = ["us-west-2a", "us-west-2b"]
}

variable "instance_configuration" {
  description = "Instance configuration object"
  type = object({
    instance_type = string
    monitoring    = bool
    tags          = map(string)
  })
  default = {
    instance_type = "t3.micro"
    monitoring    = true
    tags = {
      Project = "Default"
    }
  }
}

# Using variables
resource "aws_instance" "example" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = var.instance_type
  
  tags = merge(
    var.instance_configuration.tags,
    {
      Environment = var.environment
    }
  )
}
```

#### Outputs
```hcl
# Output values
output "instance_id" {
  description = "ID of the EC2 instance"
  value       = aws_instance.example.id
}

output "instance_public_ip" {
  description = "Public IP address of the EC2 instance"
  value       = aws_instance.example.public_ip
  sensitive   = false
}

output "database_password" {
  description = "Database administrator password"
  value       = aws_db_instance.example.password
  sensitive   = true
}

# Complex output with conditional logic
output "load_balancer_dns" {
  description = "DNS name of the load balancer"
  value = var.create_load_balancer ? aws_lb.example[0].dns_name : null
}
```

### 2.2 Advanced HCL Features

#### Conditional Expressions
```hcl
# Conditional expressions
resource "aws_instance" "example" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = var.environment == "prod" ? "t3.large" : "t3.micro"
  
  # Conditional resource creation
  count = var.create_instance ? 1 : 0
  
  # Complex conditional logic
  monitoring = var.environment == "prod" || var.enable_detailed_monitoring ? true : false
  
  # Conditional blocks
  dynamic "ebs_block_device" {
    for_each = var.environment == "prod" ? var.additional_disks : []
    content {
      device_name = ebs_block_device.value.device_name
      volume_size = ebs_block_device.value.volume_size
      volume_type = ebs_block_device.value.volume_type
    }
  }
}
```

#### Functions và Expressions
```hcl
locals {
  # String manipulation
  instance_name = "${var.project_name}-${var.environment}-web"
  
  # List operations
  availability_zones = slice(data.aws_availability_zones.available.names, 0, 2)
  
  # Map operations
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
    CreatedOn   = formatdate("YYYY-MM-DD", timestamp())
  }
  
  # Conditional logic
  instance_count = var.environment == "prod" ? 3 : 1
  
  # Type conversion
  port_list = [for port in split(",", var.allowed_ports) : tonumber(port)]
  
  # Complex data transformation
  subnet_configuration = {
    for idx, cidr in var.subnet_cidrs : 
    "subnet-${idx}" => {
      cidr_block        = cidr
      availability_zone = data.aws_availability_zones.available.names[idx % length(data.aws_availability_zones.available.names)]
    }
  }
}

# Using local values
resource "aws_instance" "web" {
  count             = local.instance_count
  ami               = data.aws_ami.ubuntu.id
  instance_type     = var.instance_type
  availability_zone = local.availability_zones[count.index % length(local.availability_zones)]
  
  tags = merge(
    local.common_tags,
    {
      Name = "${local.instance_name}-${count.index + 1}"
    }
  )
}
```

#### Dynamic Blocks
```hcl
# Dynamic blocks for repetitive nested blocks
resource "aws_security_group" "example" {
  name        = "${var.name_prefix}-sg"
  description = "Security group for ${var.name_prefix}"
  vpc_id      = var.vpc_id
  
  # Dynamic ingress rules
  dynamic "ingress" {
    for_each = var.ingress_rules
    content {
      description = ingress.value.description
      from_port   = ingress.value.from_port
      to_port     = ingress.value.to_port
      protocol    = ingress.value.protocol
      cidr_blocks = ingress.value.cidr_blocks
      
      # Conditional security group rules
      security_groups = lookup(ingress.value, "security_groups", null)
    }
  }
  
  # Dynamic egress rules
  dynamic "egress" {
    for_each = var.egress_rules
    content {
      description = egress.value.description
      from_port   = egress.value.from_port
      to_port     = egress.value.to_port
      protocol    = egress.value.protocol
      cidr_blocks = egress.value.cidr_blocks
    }
  }
  
  tags = local.common_tags
}

# Variable definition for dynamic blocks
variable "ingress_rules" {
  description = "List of ingress rules"
  type = list(object({
    description     = string
    from_port       = number
    to_port         = number
    protocol        = string
    cidr_blocks     = list(string)
    security_groups = optional(list(string))
  }))
  default = [
    {
      description = "HTTP"
      from_port   = 80
      to_port     = 80
      protocol    = "tcp"
      cidr_blocks = ["0.0.0.0/0"]
    },
    {
      description = "HTTPS"
      from_port   = 443
      to_port     = 443
      protocol    = "tcp"
      cidr_blocks = ["0.0.0.0/0"]
    }
  ]
}
```

## 3. Providers và Resources

### 3.1 Provider Configuration

#### AWS Provider
```hcl
# terraform.tf - Terraform configuration
terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.1"
    }
  }
  
  # Remote state backend
  backend "s3" {
    bucket         = "terraform-state-bucket"
    key            = "infrastructure/terraform.tfstate"
    region         = "us-west-2"
    encrypt        = true
    dynamodb_table = "terraform-locks"
  }
}

# Provider configuration
provider "aws" {
  region = var.aws_region
  
  # Default tags for all resources
  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# Multiple provider configurations
provider "aws" {
  alias  = "us_east_1"
  region = "us-east-1"
}

provider "aws" {
  alias  = "eu_west_1"
  region = "eu-west-1"
}

# Using aliased providers
resource "aws_s3_bucket" "us_bucket" {
  provider = aws.us_east_1
  bucket   = "my-app-us-bucket"
}

resource "aws_s3_bucket" "eu_bucket" {
  provider = aws.eu_west_1
  bucket   = "my-app-eu-bucket"
}
```

#### Multi-Cloud Provider Setup
```hcl
# Multi-cloud configuration
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
  }
}

provider "aws" {
  region = "us-west-2"
}

provider "azurerm" {
  features {}
  subscription_id = var.azure_subscription_id
}

provider "google" {
  project = var.gcp_project_id
  region  = "us-central1"
}
```

### 3.2 Complex Resource Examples

#### VPC with Multiple Subnets
```hcl
# Data sources
data "aws_availability_zones" "available" {
  state = "available"
}

# VPC
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = {
    Name = "${var.name_prefix}-vpc"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
  
  tags = {
    Name = "${var.name_prefix}-igw"
  }
}

# Public Subnets
resource "aws_subnet" "public" {
  count             = length(var.public_subnet_cidrs)
  vpc_id            = aws_vpc.main.id
  cidr_block        = var.public_subnet_cidrs[count.index]
  availability_zone = data.aws_availability_zones.available.names[count.index]
  
  map_public_ip_on_launch = true
  
  tags = {
    Name = "${var.name_prefix}-public-${count.index + 1}"
    Type = "Public"
  }
}

# Private Subnets
resource "aws_subnet" "private" {
  count             = length(var.private_subnet_cidrs)
  vpc_id            = aws_vpc.main.id
  cidr_block        = var.private_subnet_cidrs[count.index]
  availability_zone = data.aws_availability_zones.available.names[count.index]
  
  tags = {
    Name = "${var.name_prefix}-private-${count.index + 1}"
    Type = "Private"
  }
}

# Elastic IPs for NAT Gateways
resource "aws_eip" "nat" {
  count  = length(aws_subnet.public)
  domain = "vpc"
  
  depends_on = [aws_internet_gateway.main]
  
  tags = {
    Name = "${var.name_prefix}-eip-${count.index + 1}"
  }
}

# NAT Gateways
resource "aws_nat_gateway" "main" {
  count         = length(aws_subnet.public)
  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[count.index].id
  
  depends_on = [aws_internet_gateway.main]
  
  tags = {
    Name = "${var.name_prefix}-nat-${count.index + 1}"
  }
}

# Route Tables
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }
  
  tags = {
    Name = "${var.name_prefix}-public-rt"
  }
}

resource "aws_route_table" "private" {
  count  = length(aws_nat_gateway.main)
  vpc_id = aws_vpc.main.id
  
  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.main[count.index].id
  }
  
  tags = {
    Name = "${var.name_prefix}-private-rt-${count.index + 1}"
  }
}

# Route Table Associations
resource "aws_route_table_association" "public" {
  count          = length(aws_subnet.public)
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "private" {
  count          = length(aws_subnet.private)
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private[count.index].id
}
```

### 3.3 Resource Dependencies

#### Explicit Dependencies
```hcl
resource "aws_security_group" "web" {
  name_prefix = "${var.name_prefix}-web"
  vpc_id      = aws_vpc.main.id
  
  # Explicit dependency
  depends_on = [aws_vpc.main]
}

resource "aws_instance" "web" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.instance_type
  subnet_id              = aws_subnet.public[0].id
  vpc_security_group_ids = [aws_security_group.web.id]
  
  # Multiple explicit dependencies
  depends_on = [
    aws_security_group.web,
    aws_internet_gateway.main
  ]
}
```

#### Implicit Dependencies
```hcl
# Implicit dependencies through resource attributes
resource "aws_instance" "database" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.database_instance_type
  subnet_id              = aws_subnet.private[0].id  # Implicit dependency
  vpc_security_group_ids = [aws_security_group.database.id]  # Implicit dependency
  
  user_data = base64encode(templatefile("${path.module}/scripts/database-setup.sh", {
    db_password = random_password.database.result  # Implicit dependency
  }))
}

resource "random_password" "database" {
  length  = 16
  special = true
}
```

## 4. State Management

### 4.1 Terraform State Fundamentals

#### Local State
```bash
# Default local state file
terraform.tfstate
terraform.tfstate.backup

# State commands
terraform show                    # Show current state
terraform state list             # List resources in state
terraform state show aws_instance.web  # Show specific resource
terraform refresh                # Refresh state from real infrastructure
```

#### Remote State Configuration
```hcl
# S3 Backend with DynamoDB locking
terraform {
  backend "s3" {
    bucket         = "terraform-state-bucket"
    key            = "environments/production/terraform.tfstate"
    region         = "us-west-2"
    encrypt        = true
    dynamodb_table = "terraform-locks"
    
    # Additional security
    kms_key_id = "arn:aws:kms:us-west-2:123456789012:key/12345678-1234-1234-1234-123456789012"
  }
}

# Alternative: Azure Backend
terraform {
  backend "azurerm" {
    resource_group_name  = "terraform-state"
    storage_account_name = "terraformstate"
    container_name       = "tfstate"
    key                  = "production.terraform.tfstate"
  }
}

# Alternative: Terraform Cloud
terraform {
  cloud {
    organization = "viettel-idc"
    
    workspaces {
      name = "production-infrastructure"
    }
  }
}
```

### 4.2 State Operations

#### State Import
```bash
# Import existing AWS EC2 instance
terraform import aws_instance.web i-1234567890abcdef0

# Import with specific provider
terraform import aws_instance.web i-1234567890abcdef0

# Bulk import script
#!/bin/bash
# import-existing-resources.sh

# Import VPC
terraform import aws_vpc.main vpc-12345678

# Import subnets
terraform import aws_subnet.public[0] subnet-12345678
terraform import aws_subnet.public[1] subnet-23456789

# Import security groups
terraform import aws_security_group.web sg-12345678
```

#### State Manipulation
```bash
# Move resource in state
terraform state mv aws_instance.web aws_instance.web_server

# Remove resource from state (without destroying)
terraform state rm aws_instance.old_server

# Replace resource
terraform state replace-provider hashicorp/aws registry.terraform.io/hashicorp/aws

# Show state file location
terraform state pull > current-state.json

# Push state file (dangerous!)
terraform state push terraform.tfstate
```

### 4.3 Workspace Management

```bash
# List workspaces
terraform workspace list

# Create new workspace
terraform workspace new development
terraform workspace new staging
terraform workspace new production

# Switch workspace
terraform workspace select production

# Show current workspace
terraform workspace show

# Delete workspace
terraform workspace delete development
```

#### Workspace-specific Configuration
```hcl
# Using workspace in configuration
locals {
  environment = terraform.workspace
  
  instance_counts = {
    development = 1
    staging     = 2
    production  = 3
  }
  
  instance_types = {
    development = "t3.micro"
    staging     = "t3.small"
    production  = "t3.large"
  }
}

resource "aws_instance" "web" {
  count         = local.instance_counts[local.environment]
  ami           = data.aws_ami.ubuntu.id
  instance_type = local.instance_types[local.environment]
  
  tags = {
    Name        = "${local.environment}-web-${count.index + 1}"
    Environment = local.environment
  }
}

# Workspace-specific backend configuration
terraform {
  backend "s3" {
    bucket = "terraform-state-bucket"
    key    = "environments/${terraform.workspace}/terraform.tfstate"
    region = "us-west-2"
  }
}
```

## 5. Modules

### 5.1 Module Structure

#### Basic Module Structure
```bash
modules/
└── vpc/
    ├── main.tf          # Primary resource definitions
    ├── variables.tf     # Input variable definitions
    ├── outputs.tf       # Output value definitions
    ├── versions.tf      # Provider requirements
    ├── README.md        # Module documentation
    └── examples/        # Usage examples
        └── complete/
            ├── main.tf
            └── variables.tf
```

#### Module Implementation
```hcl
# modules/vpc/variables.tf
variable "name" {
  description = "Name prefix for all resources"
  type        = string
}

variable "cidr_block" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
  
  validation {
    condition = can(cidrhost(var.cidr_block, 0))
    error_message = "Must be a valid IPv4 CIDR block."
  }
}

variable "public_subnets" {
  description = "List of public subnet CIDR blocks"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnets" {
  description = "List of private subnet CIDR blocks"
  type        = list(string)
  default     = ["10.0.10.0/24", "10.0.20.0/24"]
}

variable "enable_nat_gateway" {
  description = "Enable NAT Gateway for private subnets"
  type        = bool
  default     = true
}

variable "enable_dns_hostnames" {
  description = "Enable DNS hostnames in the VPC"
  type        = bool
  default     = true
}

variable "tags" {
  description = "Additional tags for all resources"
  type        = map(string)
  default     = {}
}
```

```hcl
# modules/vpc/main.tf
data "aws_availability_zones" "available" {
  state = "available"
}

# VPC
resource "aws_vpc" "this" {
  cidr_block           = var.cidr_block
  enable_dns_hostnames = var.enable_dns_hostnames
  enable_dns_support   = true
  
  tags = merge(
    var.tags,
    {
      Name = "${var.name}-vpc"
    }
  )
}

# Internet Gateway
resource "aws_internet_gateway" "this" {
  vpc_id = aws_vpc.this.id
  
  tags = merge(
    var.tags,
    {
      Name = "${var.name}-igw"
    }
  )
}

# Public Subnets
resource "aws_subnet" "public" {
  count             = length(var.public_subnets)
  vpc_id            = aws_vpc.this.id
  cidr_block        = var.public_subnets[count.index]
  availability_zone = data.aws_availability_zones.available.names[count.index]
  
  map_public_ip_on_launch = true
  
  tags = merge(
    var.tags,
    {
      Name = "${var.name}-public-${count.index + 1}"
      Type = "Public"
    }
  )
}

# Private Subnets
resource "aws_subnet" "private" {
  count             = length(var.private_subnets)
  vpc_id            = aws_vpc.this.id
  cidr_block        = var.private_subnets[count.index]
  availability_zone = data.aws_availability_zones.available.names[count.index]
  
  tags = merge(
    var.tags,
    {
      Name = "${var.name}-private-${count.index + 1}"
      Type = "Private"
    }
  )
}

# NAT Gateway (conditional)
resource "aws_eip" "nat" {
  count  = var.enable_nat_gateway ? length(aws_subnet.public) : 0
  domain = "vpc"
  
  depends_on = [aws_internet_gateway.this]
  
  tags = merge(
    var.tags,
    {
      Name = "${var.name}-nat-eip-${count.index + 1}"
    }
  )
}

resource "aws_nat_gateway" "this" {
  count         = var.enable_nat_gateway ? length(aws_subnet.public) : 0
  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[count.index].id
  
  depends_on = [aws_internet_gateway.this]
  
  tags = merge(
    var.tags,
    {
      Name = "${var.name}-nat-${count.index + 1}"
    }
  )
}
```

```hcl
# modules/vpc/outputs.tf
output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.this.id
}

output "vpc_cidr_block" {
  description = "CIDR block of the VPC"
  value       = aws_vpc.this.cidr_block
}

output "public_subnet_ids" {
  description = "List of IDs of the public subnets"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "List of IDs of the private subnets"
  value       = aws_subnet.private[*].id
}

output "internet_gateway_id" {
  description = "ID of the Internet Gateway"
  value       = aws_internet_gateway.this.id
}

output "nat_gateway_ids" {
  description = "List of IDs of the NAT Gateways"
  value       = aws_nat_gateway.this[*].id
}
```

### 5.2 Using Modules

#### Local Module Usage
```hcl
# main.tf
module "vpc" {
  source = "./modules/vpc"
  
  name            = "production"
  cidr_block      = "10.0.0.0/16"
  public_subnets  = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  private_subnets = ["10.0.10.0/24", "10.0.20.0/24", "10.0.30.0/24"]
  
  enable_nat_gateway = true
  
  tags = {
    Environment = "production"
    Project     = "viettel-idc"
  }
}

# Use module outputs
resource "aws_instance" "web" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = "t3.micro"
  subnet_id     = module.vpc.public_subnet_ids[0]
  
  tags = {
    Name = "web-server"
  }
}
```

#### Registry Module Usage
```hcl
# Using modules from Terraform Registry
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 19.0"
  
  cluster_name    = "viettel-eks"
  cluster_version = "1.27"
  
  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnet_ids
  
  # EKS Managed Node Groups
  eks_managed_node_groups = {
    main = {
      min_size     = 1
      max_size     = 3
      desired_size = 2
      
      instance_types = ["t3.medium"]
      capacity_type  = "ON_DEMAND"
    }
  }
  
  tags = {
    Environment = "production"
    Terraform   = "true"
  }
}
```

## 6. Advanced Terraform Patterns

### 6.1 For Expressions và Complex Data Manipulation

```hcl
# Complex data transformation
locals {
  # Transform list to map
  subnet_map = {
    for idx, subnet in var.subnets :
    subnet.name => {
      cidr_block        = subnet.cidr
      availability_zone = data.aws_availability_zones.available.names[idx % length(data.aws_availability_zones.available.names)]
    }
  }
  
  # Filter and transform
  production_instances = {
    for name, config in var.instances :
    name => config
    if config.environment == "production"
  }
  
  # Nested for expressions
  security_group_rules = flatten([
    for group_name, group_config in var.security_groups : [
      for rule in group_config.ingress_rules : {
        group_name  = group_name
        type        = "ingress"
        from_port   = rule.from_port
        to_port     = rule.to_port
        protocol    = rule.protocol
        cidr_blocks = rule.cidr_blocks
      }
    ]
  ])
}

# Use transformed data
resource "aws_subnet" "main" {
  for_each = local.subnet_map
  
  vpc_id            = aws_vpc.main.id
  cidr_block        = each.value.cidr_block
  availability_zone = each.value.availability_zone
  
  tags = {
    Name = each.key
  }
}

resource "aws_instance" "production" {
  for_each = local.production_instances
  
  ami           = each.value.ami
  instance_type = each.value.instance_type
  subnet_id     = aws_subnet.main[each.value.subnet_name].id
  
  tags = {
    Name        = each.key
    Environment = each.value.environment
  }
}
```

### 6.2 Lifecycle Management

```hcl
resource "aws_instance" "web" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = var.instance_type
  
  # Lifecycle rules
  lifecycle {
    # Prevent accidental deletion
    prevent_destroy = true
    
    # Create new resource before destroying old one
    create_before_destroy = true
    
    # Ignore changes to specific attributes
    ignore_changes = [
      ami,
      user_data,
      tags["LastModified"]
    ]
    
    # Replace resource when specific attributes change
    replace_triggered_by = [
      aws_security_group.web
    ]
  }
  
  tags = {
    Name         = "web-server"
    LastModified = timestamp()
  }
}

# Lifecycle with precondition and postcondition
resource "aws_s3_bucket" "example" {
  bucket = var.bucket_name
  
  lifecycle {
    precondition {
      condition     = length(var.bucket_name) > 3
      error_message = "Bucket name must be more than 3 characters."
    }
    
    postcondition {
      condition     = self.arn != ""
      error_message = "Bucket ARN must be set."
    }
  }
}
```

## 📚 Tài liệu Tham khảo
- [Terraform Official Documentation](https://www.terraform.io/docs)
- [HCL Configuration Language](https://www.terraform.io/docs/language/index.html)
- [Terraform Registry](https://registry.terraform.io/)
- [AWS Provider Documentation](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)

## 🔍 Câu hỏi Ôn tập
1. Sự khác biệt giữa Terraform và các Infrastructure as Code tools khác?
2. Khi nào nên sử dụng local state vs remote state?
3. Best practices cho Terraform module design?
4. Cách handle sensitive data trong Terraform?
5. Strategies để manage Terraform state trong team environments?

---
*Chú thích: Terraform fundamentals là nền tảng để xây dựng infrastructure automation scalable và maintainable.*
