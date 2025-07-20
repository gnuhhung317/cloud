# Terraform Labs - Infrastructure as Code Practice

## 🎯 Mục tiêu Labs
- Thực hành Terraform fundamentals và advanced features
- Triển khai infrastructure trên nhiều cloud providers
- Áp dụng best practices trong real-world scenarios

## Lab 1: Terraform Setup và Basic Infrastructure

### Prerequisites
```bash
# Download và install Terraform
wget https://releases.hashicorp.com/terraform/1.5.0/terraform_1.5.0_linux_amd64.zip
unzip terraform_1.5.0_linux_amd64.zip
sudo mv terraform /usr/local/bin/

# Verify installation
terraform version

# Configure AWS credentials
aws configure
# hoặc export environment variables
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-west-2"
```

### Lab 1.1: First Terraform Configuration
```hcl
# main.tf
terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# Variables
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-west-2"
}

variable "project_name" {
  description = "Project name for tagging"
  type        = string
  default     = "terraform-lab"
}

# Data sources
data "aws_availability_zones" "available" {
  state = "available"
}

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

# Resources
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name    = "${var.project_name}-vpc"
    Project = var.project_name
  }
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name    = "${var.project_name}-igw"
    Project = var.project_name
  }
}

resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = data.aws_availability_zones.available.names[0]
  map_public_ip_on_launch = true

  tags = {
    Name    = "${var.project_name}-public-subnet"
    Project = var.project_name
    Type    = "Public"
  }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name    = "${var.project_name}-public-rt"
    Project = var.project_name
  }
}

resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

resource "aws_security_group" "web" {
  name_prefix = "${var.project_name}-web-"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name    = "${var.project_name}-web-sg"
    Project = var.project_name
  }
}

resource "aws_key_pair" "main" {
  key_name   = "${var.project_name}-key"
  public_key = file("~/.ssh/id_rsa.pub")

  tags = {
    Name    = "${var.project_name}-key"
    Project = var.project_name
  }
}

resource "aws_instance" "web" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = "t3.micro"
  subnet_id              = aws_subnet.public.id
  vpc_security_group_ids = [aws_security_group.web.id]
  key_name               = aws_key_pair.main.key_name

  user_data = base64encode(<<-EOF
              #!/bin/bash
              apt-get update
              apt-get install -y nginx
              systemctl start nginx
              systemctl enable nginx
              echo "<h1>Hello from Terraform!</h1>" > /var/www/html/index.html
              EOF
  )

  tags = {
    Name    = "${var.project_name}-web-server"
    Project = var.project_name
  }
}

# Outputs
output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

output "instance_public_ip" {
  description = "Public IP of the web server"
  value       = aws_instance.web.public_ip
}

output "instance_public_dns" {
  description = "Public DNS of the web server"
  value       = aws_instance.web.public_dns
}
```

### Lab 1.2: Run First Terraform
```bash
# Initialize Terraform
terraform init

# Format code
terraform fmt

# Validate configuration
terraform validate

# Plan deployment
terraform plan

# Apply configuration
terraform apply

# Test deployment
curl http://$(terraform output -raw instance_public_ip)

# Show current state
terraform show

# Destroy infrastructure
terraform destroy
```

## Lab 2: Variables và Outputs

### Lab 2.1: Comprehensive Variables
```hcl
# variables.tf
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-west-2"
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

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"
  
  validation {
    condition = can(regex("^t[23]\\.", var.instance_type))
    error_message = "Instance type must be a t2 or t3 instance."
  }
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
  
  validation {
    condition = can(cidrhost(var.vpc_cidr, 0))
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

variable "instance_config" {
  description = "Instance configuration"
  type = object({
    count         = number
    instance_type = string
    monitoring    = bool
  })
  default = {
    count         = 2
    instance_type = "t3.micro"
    monitoring    = false
  }
}

variable "tags" {
  description = "Common tags for all resources"
  type        = map(string)
  default = {
    Terraform   = "true"
    Environment = "dev"
  }
}
```

### Lab 2.2: Environment-specific Variables
```hcl
# terraform.tfvars
aws_region  = "us-west-2"
environment = "dev"

vpc_cidr        = "10.0.0.0/16"
public_subnets  = ["10.0.1.0/24", "10.0.2.0/24"]
private_subnets = ["10.0.10.0/24", "10.0.20.0/24"]

enable_nat_gateway = false

instance_config = {
  count         = 1
  instance_type = "t3.micro"
  monitoring    = false
}

tags = {
  Project     = "terraform-labs"
  Environment = "development"
  Owner       = "devops-team"
}
```

```hcl
# environments/production.tfvars
aws_region  = "us-west-2"
environment = "prod"

vpc_cidr        = "10.1.0.0/16"
public_subnets  = ["10.1.1.0/24", "10.1.2.0/24", "10.1.3.0/24"]
private_subnets = ["10.1.10.0/24", "10.1.20.0/24", "10.1.30.0/24"]

enable_nat_gateway = true

instance_config = {
  count         = 3
  instance_type = "t3.large"
  monitoring    = true
}

tags = {
  Project     = "terraform-labs"
  Environment = "production"
  Owner       = "platform-team"
  CostCenter  = "engineering"
}
```

### Lab 2.3: Advanced Outputs
```hcl
# outputs.tf
output "vpc_info" {
  description = "VPC information"
  value = {
    id         = aws_vpc.main.id
    cidr_block = aws_vpc.main.cidr_block
    region     = var.aws_region
  }
}

output "public_subnets" {
  description = "Public subnet information"
  value = {
    for idx, subnet in aws_subnet.public :
    subnet.availability_zone => {
      id         = subnet.id
      cidr_block = subnet.cidr_block
    }
  }
}

output "instance_details" {
  description = "Instance details"
  value = {
    for idx, instance in aws_instance.web :
    instance.tags["Name"] => {
      id              = instance.id
      public_ip       = instance.public_ip
      private_ip      = instance.private_ip
      availability_zone = instance.availability_zone
    }
  }
}

output "load_balancer_dns" {
  description = "Load balancer DNS name"
  value       = length(aws_lb.main) > 0 ? aws_lb.main[0].dns_name : null
}

output "database_endpoint" {
  description = "Database endpoint"
  value       = var.environment == "prod" ? aws_db_instance.main[0].endpoint : null
  sensitive   = true
}

# Output to file
resource "local_file" "inventory" {
  content = templatefile("${path.module}/templates/inventory.tpl", {
    web_servers = aws_instance.web
  })
  filename = "${path.module}/generated/inventory.ini"
}
```

## Lab 3: Modules Development

### Lab 3.1: VPC Module
```bash
# Create module structure
mkdir -p modules/vpc/{examples/complete,tests}
```

```hcl
# modules/vpc/main.tf
data "aws_availability_zones" "available" {
  state = "available"
}

locals {
  max_subnet_length = max(
    length(var.private_subnets),
    length(var.public_subnets)
  )
  
  nat_gateway_count = var.single_nat_gateway ? 1 : var.enable_nat_gateway ? local.max_subnet_length : 0
}

# VPC
resource "aws_vpc" "this" {
  cidr_block           = var.cidr
  enable_dns_hostnames = var.enable_dns_hostnames
  enable_dns_support   = var.enable_dns_support

  tags = merge(
    var.tags,
    var.vpc_tags,
    {
      Name = var.name
    }
  )
}

# Internet Gateway
resource "aws_internet_gateway" "this" {
  count = length(var.public_subnets) > 0 ? 1 : 0

  vpc_id = aws_vpc.this.id

  tags = merge(
    var.tags,
    {
      Name = "${var.name}-igw"
    }
  )
}

# Public subnets
resource "aws_subnet" "public" {
  count = length(var.public_subnets)

  vpc_id                  = aws_vpc.this.id
  cidr_block              = element(concat(var.public_subnets, [""]), count.index)
  availability_zone       = length(regexall("^[a-z]{2}-", element(data.aws_availability_zones.available.names, count.index))) > 0 ? element(data.aws_availability_zones.available.names, count.index) : null
  map_public_ip_on_launch = var.map_public_ip_on_launch

  tags = merge(
    var.tags,
    var.public_subnet_tags,
    {
      Name = format("${var.name}-public-%s", element(data.aws_availability_zones.available.names, count.index))
      Type = "Public"
    }
  )
}

# Private subnets
resource "aws_subnet" "private" {
  count = length(var.private_subnets)

  vpc_id            = aws_vpc.this.id
  cidr_block        = var.private_subnets[count.index]
  availability_zone = length(regexall("^[a-z]{2}-", element(data.aws_availability_zones.available.names, count.index))) > 0 ? element(data.aws_availability_zones.available.names, count.index) : null

  tags = merge(
    var.tags,
    var.private_subnet_tags,
    {
      Name = format("${var.name}-private-%s", element(data.aws_availability_zones.available.names, count.index))
      Type = "Private"
    }
  )
}

# Elastic IPs for NAT
resource "aws_eip" "nat" {
  count = local.nat_gateway_count

  domain = "vpc"

  tags = merge(
    var.tags,
    {
      Name = format("${var.name}-eip-%s", element(data.aws_availability_zones.available.names, var.single_nat_gateway ? 0 : count.index))
    }
  )

  depends_on = [aws_internet_gateway.this]
}

# NAT Gateway
resource "aws_nat_gateway" "this" {
  count = local.nat_gateway_count

  allocation_id = element(aws_eip.nat[*].id, var.single_nat_gateway ? 0 : count.index)
  subnet_id     = element(aws_subnet.public[*].id, var.single_nat_gateway ? 0 : count.index)

  tags = merge(
    var.tags,
    {
      Name = format("${var.name}-nat-%s", element(data.aws_availability_zones.available.names, var.single_nat_gateway ? 0 : count.index))
    }
  )

  depends_on = [aws_internet_gateway.this]
}

# Route table for public subnets
resource "aws_route_table" "public" {
  count = length(var.public_subnets) > 0 ? 1 : 0

  vpc_id = aws_vpc.this.id

  tags = merge(
    var.tags,
    {
      Name = "${var.name}-public"
    }
  )
}

resource "aws_route" "public_internet_gateway" {
  count = length(var.public_subnets) > 0 ? 1 : 0

  route_table_id         = aws_route_table.public[0].id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.this[0].id

  timeouts {
    create = "5m"
  }
}

# Route table associations for public subnets
resource "aws_route_table_association" "public" {
  count = length(var.public_subnets)

  subnet_id      = element(aws_subnet.public[*].id, count.index)
  route_table_id = aws_route_table.public[0].id
}

# Route tables for private subnets
resource "aws_route_table" "private" {
  count = local.max_subnet_length

  vpc_id = aws_vpc.this.id

  tags = merge(
    var.tags,
    {
      Name = var.single_nat_gateway ? "${var.name}-private" : format("${var.name}-private-%s", element(data.aws_availability_zones.available.names, count.index))
    }
  )
}

# Routes for private subnets
resource "aws_route" "private_nat_gateway" {
  count = var.enable_nat_gateway ? local.nat_gateway_count : 0

  route_table_id         = element(aws_route_table.private[*].id, var.single_nat_gateway ? 0 : count.index)
  destination_cidr_block = "0.0.0.0/0"
  nat_gateway_id         = element(aws_nat_gateway.this[*].id, count.index)

  timeouts {
    create = "5m"
  }
}

# Route table associations for private subnets
resource "aws_route_table_association" "private" {
  count = length(var.private_subnets)

  subnet_id      = element(aws_subnet.private[*].id, count.index)
  route_table_id = element(aws_route_table.private[*].id, var.single_nat_gateway ? 0 : count.index)
}
```

```hcl
# modules/vpc/variables.tf
variable "name" {
  description = "Name to be used on all the resources as identifier"
  type        = string
  default     = ""
}

variable "cidr" {
  description = "The CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnets" {
  description = "A list of public subnets inside the VPC"
  type        = list(string)
  default     = []
}

variable "private_subnets" {
  description = "A list of private subnets inside the VPC"
  type        = list(string)
  default     = []
}

variable "enable_nat_gateway" {
  description = "Should be true if you want to provision NAT Gateways for each of your private networks"
  type        = bool
  default     = false
}

variable "single_nat_gateway" {
  description = "Should be true if you want to provision a single shared NAT Gateway across all of your private networks"
  type        = bool
  default     = false
}

variable "enable_dns_hostnames" {
  description = "Should be true to enable DNS hostnames in the VPC"
  type        = bool
  default     = true
}

variable "enable_dns_support" {
  description = "Should be true to enable DNS support in the VPC"
  type        = bool
  default     = true
}

variable "map_public_ip_on_launch" {
  description = "Should be false if you do not want to auto-assign public IP on launch"
  type        = bool
  default     = true
}

variable "tags" {
  description = "A map of tags to assign to the resource"
  type        = map(string)
  default     = {}
}

variable "vpc_tags" {
  description = "Additional tags for the VPC"
  type        = map(string)
  default     = {}
}

variable "public_subnet_tags" {
  description = "Additional tags for the public subnets"
  type        = map(string)
  default     = {}
}

variable "private_subnet_tags" {
  description = "Additional tags for the private subnets"
  type        = map(string)
  default     = {}
}
```

```hcl
# modules/vpc/outputs.tf
output "vpc_id" {
  description = "The ID of the VPC"
  value       = aws_vpc.this.id
}

output "vpc_cidr_block" {
  description = "The CIDR block of the VPC"
  value       = aws_vpc.this.cidr_block
}

output "public_subnets" {
  description = "List of IDs of public subnets"
  value       = aws_subnet.public[*].id
}

output "private_subnets" {
  description = "List of IDs of private subnets"
  value       = aws_subnet.private[*].id
}

output "public_subnet_arns" {
  description = "List of ARNs of public subnets"
  value       = aws_subnet.public[*].arn
}

output "private_subnet_arns" {
  description = "List of ARNs of private subnets"
  value       = aws_subnet.private[*].arn
}

output "internet_gateway_id" {
  description = "The ID of the Internet Gateway"
  value       = try(aws_internet_gateway.this[0].id, null)
}

output "nat_gateway_ids" {
  description = "List of IDs of the NAT Gateways"
  value       = aws_nat_gateway.this[*].id
}

output "nat_public_ips" {
  description = "List of public Elastic IPs created for AWS NAT Gateway"
  value       = aws_eip.nat[*].public_ip
}

output "azs" {
  description = "A list of availability zones specified as argument to this module"
  value       = data.aws_availability_zones.available.names
}
```

### Lab 3.2: Security Group Module
```hcl
# modules/security-group/main.tf
resource "aws_security_group" "this" {
  name_prefix = var.name_prefix
  name        = var.name
  description = var.description
  vpc_id      = var.vpc_id

  tags = merge(
    var.tags,
    {
      Name = var.name
    }
  )

  lifecycle {
    create_before_destroy = true
  }
}

# Ingress rules
resource "aws_security_group_rule" "ingress_with_cidr_blocks" {
  count = length(var.ingress_with_cidr_blocks)

  security_group_id = aws_security_group.this.id
  type              = "ingress"

  cidr_blocks = var.ingress_with_cidr_blocks[count.index]["cidr_blocks"]
  description = var.ingress_with_cidr_blocks[count.index]["description"]
  from_port   = var.ingress_with_cidr_blocks[count.index]["from_port"]
  to_port     = var.ingress_with_cidr_blocks[count.index]["to_port"]
  protocol    = var.ingress_with_cidr_blocks[count.index]["protocol"]
}

resource "aws_security_group_rule" "ingress_with_source_security_group_id" {
  count = length(var.ingress_with_source_security_group_id)

  security_group_id = aws_security_group.this.id
  type              = "ingress"

  source_security_group_id = var.ingress_with_source_security_group_id[count.index]["source_security_group_id"]
  description              = var.ingress_with_source_security_group_id[count.index]["description"]
  from_port                = var.ingress_with_source_security_group_id[count.index]["from_port"]
  to_port                  = var.ingress_with_source_security_group_id[count.index]["to_port"]
  protocol                 = var.ingress_with_source_security_group_id[count.index]["protocol"]
}

# Egress rules
resource "aws_security_group_rule" "egress_with_cidr_blocks" {
  count = length(var.egress_with_cidr_blocks)

  security_group_id = aws_security_group.this.id
  type              = "egress"

  cidr_blocks = var.egress_with_cidr_blocks[count.index]["cidr_blocks"]
  description = var.egress_with_cidr_blocks[count.index]["description"]
  from_port   = var.egress_with_cidr_blocks[count.index]["from_port"]
  to_port     = var.egress_with_cidr_blocks[count.index]["to_port"]
  protocol    = var.egress_with_cidr_blocks[count.index]["protocol"]
}
```

### Lab 3.3: Using Modules
```hcl
# main.tf - Using custom modules
module "vpc" {
  source = "./modules/vpc"

  name = "${var.project_name}-vpc"
  cidr = var.vpc_cidr

  public_subnets  = var.public_subnets
  private_subnets = var.private_subnets

  enable_nat_gateway = var.enable_nat_gateway
  single_nat_gateway = var.single_nat_gateway

  tags = var.tags
}

module "web_security_group" {
  source = "./modules/security-group"

  name        = "${var.project_name}-web-sg"
  description = "Security group for web servers"
  vpc_id      = module.vpc.vpc_id

  ingress_with_cidr_blocks = [
    {
      from_port   = 80
      to_port     = 80
      protocol    = "tcp"
      cidr_blocks = ["0.0.0.0/0"]
      description = "HTTP"
    },
    {
      from_port   = 443
      to_port     = 443
      protocol    = "tcp"
      cidr_blocks = ["0.0.0.0/0"]
      description = "HTTPS"
    },
    {
      from_port   = 22
      to_port     = 22
      protocol    = "tcp"
      cidr_blocks = [var.vpc_cidr]
      description = "SSH from VPC"
    }
  ]

  egress_with_cidr_blocks = [
    {
      from_port   = 0
      to_port     = 0
      protocol    = "-1"
      cidr_blocks = ["0.0.0.0/0"]
      description = "All outbound traffic"
    }
  ]

  tags = var.tags
}

# Use registry modules
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 19.0"

  cluster_name    = "${var.project_name}-eks"
  cluster_version = "1.27"

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  # EKS Managed Node Groups
  eks_managed_node_groups = {
    main = {
      min_size     = 1
      max_size     = 3
      desired_size = 2

      instance_types = ["t3.medium"]
      capacity_type  = "ON_DEMAND"

      labels = {
        Environment = var.environment
        NodeGroup   = "main"
      }

      tags = var.tags
    }
  }

  tags = var.tags
}
```

## Lab 4: State Management

### Lab 4.1: Remote State Setup
```hcl
# backend.tf
terraform {
  backend "s3" {
    bucket         = "terraform-state-viettel-idc"
    key            = "labs/terraform.tfstate"
    region         = "us-west-2"
    encrypt        = true
    dynamodb_table = "terraform-locks"
  }
}

# Create S3 bucket and DynamoDB table for state
# bootstrap/main.tf
provider "aws" {
  region = "us-west-2"
}

resource "aws_s3_bucket" "terraform_state" {
  bucket = "terraform-state-viettel-idc"

  lifecycle {
    prevent_destroy = true
  }

  tags = {
    Name        = "Terraform State Store"
    Environment = "global"
  }
}

resource "aws_s3_bucket_versioning" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_encryption" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }
}

resource "aws_s3_bucket_public_access_block" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_dynamodb_table" "terraform_locks" {
  name           = "terraform-locks"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }

  tags = {
    Name        = "Terraform State Locks"
    Environment = "global"
  }
}
```

### Lab 4.2: Workspace Management
```bash
# Create workspaces
terraform workspace new development
terraform workspace new staging
terraform workspace new production

# List workspaces
terraform workspace list

# Switch workspace
terraform workspace select production

# Show current workspace
terraform workspace show
```

### Lab 4.3: Workspace-specific Configuration
```hcl
# main.tf với workspace logic
locals {
  environment = terraform.workspace

  # Environment-specific configurations
  config = {
    development = {
      instance_type        = "t3.micro"
      min_size            = 1
      max_size            = 2
      enable_monitoring   = false
      enable_backup       = false
    }
    staging = {
      instance_type        = "t3.small"
      min_size            = 1
      max_size            = 3
      enable_monitoring   = true
      enable_backup       = true
    }
    production = {
      instance_type        = "t3.large"
      min_size            = 2
      max_size            = 10
      enable_monitoring   = true
      enable_backup       = true
    }
  }

  current_config = local.config[local.environment]
}

# Backend configuration with workspace
terraform {
  backend "s3" {
    bucket = "terraform-state-viettel-idc"
    key    = "environments/terraform.tfstate"
    region = "us-west-2"
    
    # Use workspace in state key
    workspace_key_prefix = "workspaces"
  }
}

resource "aws_instance" "web" {
  count         = local.current_config.min_size
  ami           = data.aws_ami.ubuntu.id
  instance_type = local.current_config.instance_type

  monitoring = local.current_config.enable_monitoring

  tags = {
    Name        = "${local.environment}-web-${count.index + 1}"
    Environment = local.environment
    Workspace   = terraform.workspace
  }
}
```

## Lab 5: Multi-Cloud Infrastructure

### Lab 5.1: AWS + Azure Multi-Cloud
```hcl
# providers.tf
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
  }
}

provider "aws" {
  region = var.aws_region
}

provider "azurerm" {
  features {}
  subscription_id = var.azure_subscription_id
}

# AWS Infrastructure
module "aws_infrastructure" {
  source = "./modules/aws-infrastructure"

  project_name = var.project_name
  environment  = var.environment
  aws_region   = var.aws_region

  vpc_cidr        = "10.0.0.0/16"
  public_subnets  = ["10.0.1.0/24", "10.0.2.0/24"]
  private_subnets = ["10.0.10.0/24", "10.0.20.0/24"]

  tags = var.tags
}

# Azure Infrastructure
module "azure_infrastructure" {
  source = "./modules/azure-infrastructure"

  project_name = var.project_name
  environment  = var.environment
  location     = var.azure_location

  vnet_cidr           = "10.1.0.0/16"
  public_subnet_cidr  = "10.1.1.0/24"
  private_subnet_cidr = "10.1.10.0/24"

  tags = var.tags
}

# VPN Connection between AWS and Azure
resource "aws_vpn_gateway" "main" {
  vpc_id = module.aws_infrastructure.vpc_id

  tags = merge(var.tags, {
    Name = "${var.project_name}-vpn-gateway"
  })
}

resource "azurerm_virtual_network_gateway" "main" {
  name                = "${var.project_name}-vpn-gateway"
  location            = var.azure_location
  resource_group_name = module.azure_infrastructure.resource_group_name

  type     = "Vpn"
  vpn_type = "RouteBased"

  active_active = false
  enable_bgp    = false
  sku           = "Basic"

  ip_configuration {
    name                          = "vnetGatewayConfig"
    public_ip_address_id          = azurerm_public_ip.vpn.id
    private_ip_address_allocation = "Dynamic"
    subnet_id                     = module.azure_infrastructure.gateway_subnet_id
  }

  tags = var.tags
}

resource "azurerm_public_ip" "vpn" {
  name                = "${var.project_name}-vpn-pip"
  location            = var.azure_location
  resource_group_name = module.azure_infrastructure.resource_group_name

  allocation_method = "Dynamic"

  tags = var.tags
}
```

### Lab 5.2: Kubernetes Deployment across Clouds
```hcl
# kubernetes.tf
# AWS EKS
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 19.0"

  cluster_name    = "${var.project_name}-aws-eks"
  cluster_version = "1.27"

  vpc_id     = module.aws_infrastructure.vpc_id
  subnet_ids = module.aws_infrastructure.private_subnets

  eks_managed_node_groups = {
    main = {
      min_size     = 1
      max_size     = 3
      desired_size = 2

      instance_types = ["t3.medium"]
      capacity_type  = "ON_DEMAND"

      labels = {
        Environment = var.environment
        Cloud       = "aws"
      }
    }
  }

  tags = var.tags
}

# Azure AKS
resource "azurerm_kubernetes_cluster" "main" {
  name                = "${var.project_name}-azure-aks"
  location            = var.azure_location
  resource_group_name = module.azure_infrastructure.resource_group_name
  dns_prefix          = "${var.project_name}-aks"

  default_node_pool {
    name       = "default"
    node_count = 2
    vm_size    = "Standard_D2_v2"
    vnet_subnet_id = module.azure_infrastructure.private_subnet_id
  }

  identity {
    type = "SystemAssigned"
  }

  tags = var.tags
}

# Kubernetes provider configurations
provider "kubernetes" {
  alias = "aws"
  
  host                   = module.eks.cluster_endpoint
  cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)
  
  exec {
    api_version = "client.authentication.k8s.io/v1beta1"
    command     = "aws"
    args        = ["eks", "get-token", "--cluster-name", module.eks.cluster_id]
  }
}

provider "kubernetes" {
  alias = "azure"
  
  host                   = azurerm_kubernetes_cluster.main.kube_config.0.host
  username               = azurerm_kubernetes_cluster.main.kube_config.0.username
  password               = azurerm_kubernetes_cluster.main.kube_config.0.password
  client_certificate     = base64decode(azurerm_kubernetes_cluster.main.kube_config.0.client_certificate)
  client_key             = base64decode(azurerm_kubernetes_cluster.main.kube_config.0.client_key)
  cluster_ca_certificate = base64decode(azurerm_kubernetes_cluster.main.kube_config.0.cluster_ca_certificate)
}

# Deploy applications to both clusters
module "app_deployment_aws" {
  source = "./modules/k8s-app"
  
  providers = {
    kubernetes = kubernetes.aws
  }
  
  app_name      = var.project_name
  environment   = var.environment
  cloud_provider = "aws"
}

module "app_deployment_azure" {
  source = "./modules/k8s-app"
  
  providers = {
    kubernetes = kubernetes.azure
  }
  
  app_name      = var.project_name
  environment   = var.environment
  cloud_provider = "azure"
}
```

## Lab 6: Testing và Validation

### Lab 6.1: Terratest Implementation
```go
// test/terraform_test.go
package test

import (
    "testing"
    "github.com/gruntwork-io/terratest/modules/terraform"
    "github.com/gruntwork-io/terratest/modules/aws"
    "github.com/gruntwork-io/terratest/modules/http-helper"
    "github.com/stretchr/testify/assert"
    "time"
)

func TestTerraformVPCModule(t *testing.T) {
    t.Parallel()

    // Construct terraform options
    terraformOptions := terraform.WithDefaultRetryableErrors(t, &terraform.Options{
        TerraformDir: "../modules/vpc",
        
        Vars: map[string]interface{}{
            "name":               "test-vpc",
            "cidr":              "10.0.0.0/16",
            "public_subnets":    []string{"10.0.1.0/24", "10.0.2.0/24"},
            "private_subnets":   []string{"10.0.10.0/24", "10.0.20.0/24"},
            "enable_nat_gateway": true,
        },
        
        EnvVars: map[string]string{
            "AWS_DEFAULT_REGION": "us-west-2",
        },
    })

    defer terraform.Destroy(t, terraformOptions)
    terraform.InitAndApply(t, terraformOptions)

    // Verify outputs
    vpcId := terraform.Output(t, terraformOptions, "vpc_id")
    assert.NotEmpty(t, vpcId)

    publicSubnets := terraform.OutputList(t, terraformOptions, "public_subnets")
    assert.Len(t, publicSubnets, 2)

    privateSubnets := terraform.OutputList(t, terraformOptions, "private_subnets")
    assert.Len(t, privateSubnets, 2)

    // Verify VPC exists in AWS
    vpc := aws.GetVpcById(t, vpcId, "us-west-2")
    assert.Equal(t, "10.0.0.0/16", vpc.CidrBlock)

    // Verify subnets
    for _, subnetId := range publicSubnets {
        subnet := aws.GetSubnetById(t, subnetId, "us-west-2")
        assert.True(t, subnet.MapPublicIpOnLaunch)
    }
}

func TestTerraformWebServerDeployment(t *testing.T) {
    t.Parallel()

    terraformOptions := terraform.WithDefaultRetryableErrors(t, &terraform.Options{
        TerraformDir: "../",
        
        Vars: map[string]interface{}{
            "project_name":    "terratest",
            "environment":     "test",
            "instance_type":   "t3.micro",
        },
        
        EnvVars: map[string]string{
            "AWS_DEFAULT_REGION": "us-west-2",
        },
    })

    defer terraform.Destroy(t, terraformOptions)
    terraform.InitAndApply(t, terraformOptions)

    // Get instance public IP
    instanceIP := terraform.Output(t, terraformOptions, "instance_public_ip")
    
    // Test HTTP endpoint
    url := "http://" + instanceIP
    http_helper.HttpGetWithRetry(t, url, nil, 200, "Hello from Terraform!", 30, 5*time.Second)
}

func TestTerraformSecurityGroupRules(t *testing.T) {
    terraformOptions := terraform.WithDefaultRetryableErrors(t, &terraform.Options{
        TerraformDir: "../",
        
        Vars: map[string]interface{}{
            "project_name": "security-test",
        },
    })

    defer terraform.Destroy(t, terraformOptions)
    terraform.InitAndApply(t, terraformOptions)

    // Get security group ID
    sgId := terraform.Output(t, terraformOptions, "security_group_id")
    
    // Verify security group rules
    sg := aws.GetSecurityGroupById(t, sgId, "us-west-2")
    
    // Check for HTTP ingress rule
    httpRuleFound := false
    for _, rule := range sg.IngressRules {
        if rule.FromPort == 80 && rule.ToPort == 80 && rule.Protocol == "tcp" {
            httpRuleFound = true
            assert.Contains(t, rule.CidrBlocks, "0.0.0.0/0")
            break
        }
    }
    assert.True(t, httpRuleFound, "HTTP ingress rule should exist")
}
```

### Lab 6.2: Policy Testing với OPA/Conftest
```bash
# Install conftest
curl -L https://github.com/open-policy-agent/conftest/releases/download/v0.40.0/conftest_0.40.0_Linux_x86_64.tar.gz | tar xz
sudo mv conftest /usr/local/bin
```

```rego
# policies/security.rego
package main

import rego.v1

# Deny security groups with unrestricted SSH access
deny contains msg if {
    input.resource_changes[_].type == "aws_security_group"
    rule := input.resource_changes[_].change.after.ingress[_]
    rule.from_port == 22
    rule.to_port == 22
    "0.0.0.0/0" in rule.cidr_blocks
    msg := "Security group allows SSH access from 0.0.0.0/0"
}

# Deny unencrypted EBS volumes
deny contains msg if {
    input.resource_changes[_].type == "aws_ebs_volume"
    not input.resource_changes[_].change.after.encrypted
    msg := "EBS volume is not encrypted"
}

# Require specific tags
required_tags := ["Environment", "Project", "Owner"]

deny contains msg if {
    resource := input.resource_changes[_]
    resource.type in ["aws_instance", "aws_vpc", "aws_security_group"]
    tags := object.get(resource.change.after, "tags", {})
    missing_tag := required_tags[_]
    not tags[missing_tag]
    msg := sprintf("Resource %s is missing required tag: %s", [resource.address, missing_tag])
}

# Enforce instance type restrictions
allowed_instance_types := ["t3.micro", "t3.small", "t3.medium"]

deny contains msg if {
    resource := input.resource_changes[_]
    resource.type == "aws_instance"
    instance_type := resource.change.after.instance_type
    not instance_type in allowed_instance_types
    msg := sprintf("Instance type %s is not allowed", [instance_type])
}
```

```yaml
# .conftest.yaml
policy: policies
output: json
```

```bash
# Test policies
terraform plan -out=tfplan.binary
terraform show -json tfplan.binary > tfplan.json
conftest test tfplan.json
```

## Lab Exercises

### Exercise 1: Complete 3-Tier Architecture
Triển khai complete 3-tier web application với:
- Load Balancer (ALB)
- Auto Scaling Group
- RDS Database với Multi-AZ
- ElastiCache
- CloudFront CDN

### Exercise 2: Disaster Recovery Setup
Tạo DR infrastructure ở region khác với:
- Cross-region replication
- Automated failover
- Backup strategies

### Exercise 3: Multi-Environment Pipeline
Setup complete CI/CD pipeline với:
- Environment promotion
- Automated testing
- Policy validation
- Cost optimization

### Exercise 4: Hybrid Cloud Setup
Triển khai hybrid infrastructure:
- On-premises simulation với VMware
- VPN connectivity
- Consistent networking
- Centralized monitoring

## 📚 Additional Resources
- [Terraform Documentation](https://www.terraform.io/docs)
- [Terratest](https://terratest.gruntwork.io/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [Terraform Best Practices](https://www.terraform-best-practices.com/)

---
*Chú thích: Các labs này progressive từ basic đến advanced, có thể adapt cho các cloud providers khác nhau.*
