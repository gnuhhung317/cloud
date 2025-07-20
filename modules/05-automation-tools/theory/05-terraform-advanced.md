# Terraform Advanced Features - Enterprise Infrastructure Management

## 🎯 Mục tiêu Học tập
- Thành thạo advanced Terraform features
- Hiểu rõ Enterprise patterns và best practices
- Nắm vững CI/CD integration và automation workflows
- Áp dụng security và compliance trong Infrastructure as Code

## 1. Advanced State Management

### 1.1 State Locking và Concurrent Access

#### DynamoDB State Locking (AWS)
```hcl
# Backend configuration with locking
terraform {
  backend "s3" {
    bucket         = "terraform-state-bucket"
    key            = "production/terraform.tfstate"
    region         = "us-west-2"
    encrypt        = true
    dynamodb_table = "terraform-locks"
    
    # Additional security
    kms_key_id     = "arn:aws:kms:us-west-2:123456789012:key/12345678-1234-1234-1234-123456789012"
    
    # Role-based access
    role_arn = "arn:aws:iam::123456789012:role/TerraformStateRole"
  }
}

# DynamoDB table for state locking
resource "aws_dynamodb_table" "terraform_locks" {
  name           = "terraform-locks"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "LockID"
  
  attribute {
    name = "LockID"
    type = "S"
  }
  
  server_side_encryption {
    enabled = true
  }
  
  point_in_time_recovery {
    enabled = true
  }
  
  tags = {
    Name        = "TerraformStateLocks"
    Environment = "global"
  }
}
```

#### Azure State Locking
```hcl
terraform {
  backend "azurerm" {
    resource_group_name  = "terraform-state"
    storage_account_name = "terraformstatestorage"
    container_name       = "tfstate"
    key                  = "production.terraform.tfstate"
    
    # Enable state locking
    use_msi = true
  }
}

# Azure resources for state storage
resource "azurerm_resource_group" "terraform_state" {
  name     = "terraform-state"
  location = "East US"
}

resource "azurerm_storage_account" "terraform_state" {
  name                     = "terraformstatestorage"
  resource_group_name      = azurerm_resource_group.terraform_state.name
  location                 = azurerm_resource_group.terraform_state.location
  account_tier             = "Standard"
  account_replication_type = "GRS"
  
  blob_properties {
    versioning_enabled = true
  }
}

resource "azurerm_storage_container" "terraform_state" {
  name                  = "tfstate"
  storage_account_name  = azurerm_storage_account.terraform_state.name
  container_access_type = "private"
}
```

### 1.2 State Migration và Refactoring

#### Moving Resources Between States
```bash
#!/bin/bash
# state-migration.sh

# 1. Export resource from source state
terraform state mv aws_instance.old_server module.servers.aws_instance.web[0]

# 2. Import resource to new configuration
terraform import module.new_infrastructure.aws_instance.web i-1234567890abcdef0

# 3. Remove from old state file
terraform state rm aws_instance.old_server

# 4. Verify migration
terraform plan
```

#### State Refactoring Script
```python
#!/usr/bin/env python3
# terraform-state-refactor.py

import json
import subprocess
import sys

def run_terraform_command(cmd):
    """Run terraform command and return output"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        sys.exit(1)
    return result.stdout

def get_state_resources():
    """Get all resources from state"""
    output = run_terraform_command("terraform state list")
    return output.strip().split('\n')

def move_resources_to_modules():
    """Move standalone resources to modules"""
    resources = get_state_resources()
    
    moves = [
        ("aws_instance.web", "module.web_servers.aws_instance.main[0]"),
        ("aws_security_group.web", "module.web_servers.aws_security_group.main"),
        ("aws_lb.main", "module.load_balancer.aws_lb.main"),
    ]
    
    for old_name, new_name in moves:
        if old_name in resources:
            print(f"Moving {old_name} to {new_name}")
            run_terraform_command(f"terraform state mv {old_name} {new_name}")

if __name__ == "__main__":
    move_resources_to_modules()
    print("State refactoring completed")
```

### 1.3 State Encryption và Security

```hcl
# Encrypted state with customer-managed keys
terraform {
  backend "s3" {
    bucket     = "terraform-state-bucket"
    key        = "production/terraform.tfstate"
    region     = "us-west-2"
    encrypt    = true
    kms_key_id = "arn:aws:kms:us-west-2:123456789012:key/12345678-1234-1234-1234-123456789012"
    
    # Additional security options
    server_side_encryption_configuration {
      rule {
        apply_server_side_encryption_by_default {
          kms_master_key_id = "arn:aws:kms:us-west-2:123456789012:key/12345678-1234-1234-1234-123456789012"
          sse_algorithm     = "aws:kms"
        }
      }
    }
    
    # Bucket policy for secure access
    policy = jsonencode({
      Version = "2012-10-17"
      Statement = [
        {
          Sid    = "DenyInsecureConnections"
          Effect = "Deny"
          Principal = "*"
          Action = "s3:*"
          Resource = [
            "arn:aws:s3:::terraform-state-bucket/*",
            "arn:aws:s3:::terraform-state-bucket"
          ]
          Condition = {
            Bool = {
              "aws:SecureTransport" = "false"
            }
          }
        }
      ]
    })
  }
}
```

## 2. Advanced Module Patterns

### 2.1 Composition Modules

#### Infrastructure Composition
```hcl
# modules/infrastructure/main.tf
module "networking" {
  source = "../networking"
  
  name               = var.name
  cidr_block         = var.vpc_cidr
  availability_zones = var.availability_zones
  
  public_subnets  = var.public_subnets
  private_subnets = var.private_subnets
  
  enable_nat_gateway = var.enable_nat_gateway
  enable_vpn_gateway = var.enable_vpn_gateway
  
  tags = local.common_tags
}

module "security" {
  source = "../security"
  
  vpc_id = module.networking.vpc_id
  
  security_groups = var.security_groups
  nacl_rules      = var.nacl_rules
  
  enable_flow_logs = var.enable_flow_logs
  
  tags = local.common_tags
}

module "compute" {
  source = "../compute"
  
  vpc_id             = module.networking.vpc_id
  public_subnet_ids  = module.networking.public_subnet_ids
  private_subnet_ids = module.networking.private_subnet_ids
  security_group_ids = module.security.security_group_ids
  
  instance_configurations = var.instance_configurations
  load_balancer_config    = var.load_balancer_config
  
  tags = local.common_tags
}

module "database" {
  source = "../database"
  
  vpc_id            = module.networking.vpc_id
  subnet_ids        = module.networking.private_subnet_ids
  security_group_id = module.security.database_security_group_id
  
  database_config = var.database_config
  backup_config   = var.backup_config
  
  tags = local.common_tags
}

module "monitoring" {
  source = "../monitoring"
  
  vpc_id = module.networking.vpc_id
  
  instance_ids    = module.compute.instance_ids
  database_id     = module.database.database_id
  load_balancer_arn = module.compute.load_balancer_arn
  
  monitoring_config = var.monitoring_config
  alerting_config   = var.alerting_config
  
  tags = local.common_tags
}

# Local values for common configuration
locals {
  common_tags = merge(
    var.tags,
    {
      Environment   = var.environment
      Project       = var.project_name
      ManagedBy     = "Terraform"
      CreatedBy     = "infrastructure-module"
      LastModified  = timestamp()
    }
  )
}
```

### 2.2 Feature Toggle Modules

```hcl
# modules/feature-toggles/main.tf
variable "features" {
  description = "Feature toggle configuration"
  type = object({
    enable_monitoring     = bool
    enable_backup        = bool
    enable_auto_scaling  = bool
    enable_load_balancer = bool
    enable_cdn           = bool
    enable_waf           = bool
  })
  default = {
    enable_monitoring     = true
    enable_backup        = true
    enable_auto_scaling  = false
    enable_load_balancer = false
    enable_cdn           = false
    enable_waf           = false
  }
}

# Conditional resource creation based on feature flags
module "monitoring" {
  count  = var.features.enable_monitoring ? 1 : 0
  source = "./modules/monitoring"
  
  # Configuration
}

module "backup" {
  count  = var.features.enable_backup ? 1 : 0
  source = "./modules/backup"
  
  # Configuration
}

module "auto_scaling" {
  count  = var.features.enable_auto_scaling ? 1 : 0
  source = "./modules/auto-scaling"
  
  # Configuration
}

# Dynamic resource creation
resource "aws_cloudfront_distribution" "main" {
  count = var.features.enable_cdn ? 1 : 0
  
  origin {
    domain_name = var.features.enable_load_balancer ? aws_lb.main[0].dns_name : aws_instance.web[0].public_dns
    origin_id   = "S3-${var.bucket_name}"
    
    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "https-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }
  }
  
  # CDN configuration
}

resource "aws_wafv2_web_acl" "main" {
  count = var.features.enable_waf ? 1 : 0
  
  name  = "${var.name}-waf"
  scope = "CLOUDFRONT"
  
  default_action {
    allow {}
  }
  
  # WAF rules
}
```

### 2.3 Multi-Environment Module Pattern

```hcl
# modules/environment/main.tf
locals {
  environment_config = {
    development = {
      instance_type        = "t3.micro"
      min_capacity         = 1
      max_capacity         = 2
      enable_monitoring    = false
      enable_backup        = false
      database_class       = "db.t3.micro"
      multi_az            = false
    }
    staging = {
      instance_type        = "t3.small"
      min_capacity         = 1
      max_capacity         = 3
      enable_monitoring    = true
      enable_backup        = true
      database_class       = "db.t3.small"
      multi_az            = false
    }
    production = {
      instance_type        = "t3.large"
      min_capacity         = 2
      max_capacity         = 10
      enable_monitoring    = true
      enable_backup        = true
      database_class       = "db.r5.large"
      multi_az            = true
    }
  }
  
  current_config = local.environment_config[var.environment]
}

# Environment-specific resource configuration
resource "aws_instance" "web" {
  count         = local.current_config.min_capacity
  ami           = data.aws_ami.ubuntu.id
  instance_type = local.current_config.instance_type
  
  monitoring = local.current_config.enable_monitoring
  
  tags = {
    Name        = "${var.environment}-web-${count.index + 1}"
    Environment = var.environment
  }
}

resource "aws_db_instance" "main" {
  allocated_storage = var.environment == "production" ? 100 : 20
  engine            = "postgres"
  engine_version    = "13.7"
  instance_class    = local.current_config.database_class
  
  multi_az = local.current_config.multi_az
  
  backup_retention_period = local.current_config.enable_backup ? 7 : 0
  backup_window          = local.current_config.enable_backup ? "03:00-04:00" : null
  
  tags = {
    Name        = "${var.environment}-database"
    Environment = var.environment
  }
}
```

## 3. Data Sources và External Integration

### 3.1 Advanced Data Sources

```hcl
# Complex data source queries
data "aws_instances" "web_servers" {
  instance_tags = {
    Type = "WebServer"
    Environment = var.environment
  }
  
  instance_state_names = ["running"]
  
  filter {
    name   = "vpc-id"
    values = [var.vpc_id]
  }
  
  filter {
    name   = "subnet-id"
    values = var.subnet_ids
  }
}

# Use data source outputs
resource "aws_lb_target_group_attachment" "web" {
  count            = length(data.aws_instances.web_servers.ids)
  target_group_arn = aws_lb_target_group.web.arn
  target_id        = data.aws_instances.web_servers.ids[count.index]
  port             = 80
}

# External API data source
data "http" "my_ip" {
  url = "https://ipv4.icanhazip.com"
}

# Use external data in security group
resource "aws_security_group_rule" "admin_access" {
  type              = "ingress"
  from_port         = 22
  to_port           = 22
  protocol          = "tcp"
  cidr_blocks       = ["${chomp(data.http.my_ip.body)}/32"]
  security_group_id = aws_security_group.web.id
}

# Template data source
data "template_file" "user_data" {
  template = file("${path.module}/scripts/user-data.sh")
  
  vars = {
    environment     = var.environment
    application_url = "https://${var.domain_name}"
    database_host   = aws_db_instance.main.endpoint
    redis_host      = aws_elasticache_cluster.main.cache_nodes[0].address
  }
}

# CloudFormation stack data source
data "aws_cloudformation_stack" "shared_resources" {
  name = "shared-infrastructure-${var.environment}"
}

# Use CloudFormation outputs
locals {
  shared_vpc_id = data.aws_cloudformation_stack.shared_resources.outputs["VpcId"]
  shared_subnets = split(",", data.aws_cloudformation_stack.shared_resources.outputs["PrivateSubnets"])
}
```

### 3.2 External Data Provider

```hcl
# External data provider for custom scripts
data "external" "database_info" {
  program = ["python3", "${path.module}/scripts/get_database_info.py"]
  
  query = {
    region      = var.aws_region
    environment = var.environment
    db_name     = var.database_name
  }
}

# Use external data
resource "aws_db_parameter_group" "main" {
  family = "postgres13"
  name   = "${var.environment}-postgres-params"
  
  dynamic "parameter" {
    for_each = jsondecode(data.external.database_info.result.parameters)
    content {
      name  = parameter.value.name
      value = parameter.value.value
    }
  }
}
```

```python
#!/usr/bin/env python3
# scripts/get_database_info.py

import json
import sys
import boto3

def main():
    # Read input from stdin
    input_data = json.loads(sys.stdin.read())
    
    region = input_data['region']
    environment = input_data['environment']
    db_name = input_data['db_name']
    
    # Initialize AWS client
    rds = boto3.client('rds', region_name=region)
    
    try:
        # Get database information
        response = rds.describe_db_instances(
            DBInstanceIdentifier=f"{environment}-{db_name}"
        )
        
        db_instance = response['DBInstances'][0]
        
        # Extract relevant information
        result = {
            "endpoint": db_instance['Endpoint']['Address'],
            "port": str(db_instance['Endpoint']['Port']),
            "engine_version": db_instance['EngineVersion'],
            "parameters": json.dumps([
                {"name": "shared_preload_libraries", "value": "pg_stat_statements"},
                {"name": "log_statement", "value": "all"}
            ])
        }
        
        print(json.dumps(result))
        
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
```

## 4. Terraform Cloud và Enterprise Features

### 4.1 Terraform Cloud Configuration

```hcl
# .terraform.lock.hcl
terraform {
  cloud {
    organization = "viettel-idc"
    
    workspaces {
      tags = ["production", "infrastructure"]
    }
  }
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# Workspace-specific configuration
variable "tfc_workspace_name" {
  type        = string
  description = "Terraform Cloud workspace name"
  default     = ""
}

locals {
  workspace_config = {
    "viettel-prod-infrastructure" = {
      environment    = "production"
      instance_type  = "t3.large"
      min_capacity   = 3
      max_capacity   = 10
    }
    "viettel-staging-infrastructure" = {
      environment    = "staging"
      instance_type  = "t3.medium"
      min_capacity   = 2
      max_capacity   = 5
    }
  }
  
  current_workspace = local.workspace_config[var.tfc_workspace_name]
}
```

### 4.2 Policy as Code với Sentinel

```python
# sentinel/policies/enforce-tagging.sentinel
import "tfplan/v2" as tfplan

# Required tags
required_tags = ["Environment", "Project", "Owner", "CostCenter"]

# Main rule
main = rule {
  all tfplan.resource_changes as _, changes {
    all required_tags as tag {
      changes.change.after.tags[tag] else false
    }
  }
}

# Helper function to check specific resource types
resource_types_with_tags = [
  "aws_instance",
  "aws_vpc",
  "aws_subnet",
  "aws_security_group",
  "aws_rds_instance",
  "aws_s3_bucket"
]

resource_has_required_tags = func(resource) {
  return all required_tags as tag {
    resource.tags[tag] else false
  }
}

# Enforce tagging on specific resources
enforce_tagging = rule {
  all tfplan.resource_changes as _, rc {
    rc.type in resource_types_with_tags implies
      resource_has_required_tags(rc.change.after)
  }
}
```

```python
# sentinel/policies/cost-control.sentinel
import "tfplan/v2" as tfplan
import "decimal"

# Define cost limits per environment
cost_limits = {
  "development": 500,
  "staging": 1000,
  "production": 5000
}

# Instance type costs (hourly in USD)
instance_costs = {
  "t3.nano": 0.0052,
  "t3.micro": 0.0104,
  "t3.small": 0.0208,
  "t3.medium": 0.0416,
  "t3.large": 0.0832,
  "t3.xlarge": 0.1664,
  "t3.2xlarge": 0.3328
}

# Calculate monthly cost
calculate_monthly_cost = func(instance_type, count) {
  hourly_cost = instance_costs[instance_type] else 0
  return decimal.new(hourly_cost) * decimal.new(count) * decimal.new(24) * decimal.new(30)
}

# Main cost control rule
main = rule {
  all tfplan.resource_changes as _, rc {
    rc.type is "aws_instance" implies (
      calculate_monthly_cost(rc.change.after.instance_type, 1) <
      decimal.new(cost_limits["production"])
    )
  }
}
```

### 4.3 Workspace Automation

```bash
#!/bin/bash
# scripts/manage-workspaces.sh

# Terraform Cloud API configuration
TFC_TOKEN="your-terraform-cloud-token"
TFC_ORG="viettel-idc"
TFC_API_URL="https://app.terraform.io/api/v2"

# Create workspace
create_workspace() {
    local workspace_name=$1
    local environment=$2
    
    curl \
      --header "Authorization: Bearer $TFC_TOKEN" \
      --header "Content-Type: application/vnd.api+json" \
      --request POST \
      --data @- \
      "$TFC_API_URL/organizations/$TFC_ORG/workspaces" <<EOF
{
  "data": {
    "type": "workspaces",
    "attributes": {
      "name": "$workspace_name",
      "environment": "$environment",
      "auto-apply": false,
      "terraform-version": "1.5.0",
      "working-directory": "environments/$environment",
      "execution-mode": "remote"
    }
  }
}
EOF
}

# Set workspace variables
set_workspace_variables() {
    local workspace_id=$1
    local environment=$2
    
    # Environment variable
    curl \
      --header "Authorization: Bearer $TFC_TOKEN" \
      --header "Content-Type: application/vnd.api+json" \
      --request POST \
      --data @- \
      "$TFC_API_URL/workspaces/$workspace_id/vars" <<EOF
{
  "data": {
    "type": "vars",
    "attributes": {
      "key": "environment",
      "value": "$environment",
      "category": "terraform",
      "hcl": false,
      "sensitive": false
    }
  }
}
EOF

    # AWS credentials (sensitive)
    curl \
      --header "Authorization: Bearer $TFC_TOKEN" \
      --header "Content-Type: application/vnd.api+json" \
      --request POST \
      --data @- \
      "$TFC_API_URL/workspaces/$workspace_id/vars" <<EOF
{
  "data": {
    "type": "vars",
    "attributes": {
      "key": "AWS_ACCESS_KEY_ID",
      "value": "$AWS_ACCESS_KEY_ID",
      "category": "env",
      "hcl": false,
      "sensitive": true
    }
  }
}
EOF
}

# Usage
create_workspace "viettel-prod-infrastructure" "production"
create_workspace "viettel-staging-infrastructure" "staging"
```

## 5. CI/CD Integration

### 5.1 GitLab CI Pipeline

```yaml
# .gitlab-ci.yml
stages:
  - validate
  - plan
  - security-scan
  - apply
  - test

variables:
  TF_ROOT: ${CI_PROJECT_DIR}
  TF_ADDRESS: ${CI_API_V4_URL}/projects/${CI_PROJECT_ID}/terraform/state/${CI_ENVIRONMENT_NAME}
  TF_IN_AUTOMATION: "true"

cache:
  key: "$CI_COMMIT_REF_NAME"
  paths:
    - ${TF_ROOT}/.terraform

before_script:
  - cd ${TF_ROOT}
  - terraform --version
  - terraform init

# Validation stage
validate:
  stage: validate
  script:
    - terraform validate
    - terraform fmt -check=true -diff=true
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_COMMIT_BRANCH == "main"'

# Planning stage
plan:
  stage: plan
  script:
    - terraform plan -out="planfile" -var="environment=${CI_ENVIRONMENT_NAME}"
  artifacts:
    name: plan
    paths:
      - ${TF_ROOT}/planfile
    expire_in: 1 week
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'

# Security scanning
security-scan:
  stage: security-scan
  image: 
    name: aquasec/tfsec:latest
    entrypoint: [""]
  script:
    - tfsec . --format json --out tfsec-report.json
    - tfsec . --format junit --out tfsec-report.xml
  artifacts:
    reports:
      junit: tfsec-report.xml
    paths:
      - tfsec-report.json
    expire_in: 1 week
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_COMMIT_BRANCH == "main"'

# Apply stage (production)
apply:production:
  stage: apply
  script:
    - terraform apply -auto-approve planfile
  environment:
    name: production
  dependencies:
    - plan
  rules:
    - if: '$CI_COMMIT_BRANCH == "main"'
      when: manual
  only:
    - main

# Infrastructure testing
test:
  stage: test
  image: python:3.9
  script:
    - pip install pytest boto3 requests
    - python -m pytest tests/ -v
  dependencies:
    - apply:production
  rules:
    - if: '$CI_COMMIT_BRANCH == "main"'
```

### 5.2 GitHub Actions Workflow

```yaml
# .github/workflows/terraform.yml
name: 'Terraform CI/CD'

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

env:
  TF_VERSION: 1.5.0
  AWS_DEFAULT_REGION: us-west-2

jobs:
  terraform-validate:
    name: 'Validate'
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout
      uses: actions/checkout@v3
    
    - name: Setup Terraform
      uses: hashicorp/setup-terraform@v2
      with:
        terraform_version: ${{ env.TF_VERSION }}
    
    - name: Terraform Format Check
      run: terraform fmt -check -recursive
    
    - name: Terraform Init
      run: terraform init -backend=false
    
    - name: Terraform Validate
      run: terraform validate

  terraform-security:
    name: 'Security Scan'
    runs-on: ubuntu-latest
    needs: terraform-validate
    
    steps:
    - name: Checkout
      uses: actions/checkout@v3
    
    - name: Run tfsec
      uses: aquasecurity/tfsec-action@v1.0.0
      with:
        soft_fail: true
        format: sarif
        output: tfsec.sarif
    
    - name: Upload SARIF file
      uses: github/codeql-action/upload-sarif@v2
      if: always()
      with:
        sarif_file: tfsec.sarif

  terraform-plan:
    name: 'Plan'
    runs-on: ubuntu-latest
    needs: [terraform-validate, terraform-security]
    if: github.event_name == 'pull_request'
    
    steps:
    - name: Checkout
      uses: actions/checkout@v3
    
    - name: Setup Terraform
      uses: hashicorp/setup-terraform@v2
      with:
        terraform_version: ${{ env.TF_VERSION }}
    
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v2
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: ${{ env.AWS_DEFAULT_REGION }}
    
    - name: Terraform Init
      run: terraform init
    
    - name: Terraform Plan
      id: plan
      run: |
        terraform plan -no-color -out=tfplan
        terraform show -no-color tfplan > tfplan.txt
      continue-on-error: true
    
    - name: Comment PR
      uses: actions/github-script@v6
      with:
        script: |
          const fs = require('fs');
          const plan = fs.readFileSync('tfplan.txt', 'utf8');
          const maxGitHubBodyCharacters = 65536;
          
          function chunkSubstr(str, size) {
            const numChunks = Math.ceil(str.length / size)
            const chunks = new Array(numChunks)
            for (let i = 0, o = 0; i < numChunks; ++i, o += size) {
              chunks[i] = str.substr(o, size)
            }
            return chunks
          }
          
          const planChunks = chunkSubstr(plan, maxGitHubBodyCharacters);
          
          for (let i = 0; i < planChunks.length; i++) {
            const output = `### Terraform Plan Output (Part ${i + 1}/${planChunks.length})
            
            \`\`\`terraform
            ${planChunks[i]}
            \`\`\``;
            
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: output
            });
          }

  terraform-apply:
    name: 'Apply'
    runs-on: ubuntu-latest
    needs: terraform-validate
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    environment: production
    
    steps:
    - name: Checkout
      uses: actions/checkout@v3
    
    - name: Setup Terraform
      uses: hashicorp/setup-terraform@v2
      with:
        terraform_version: ${{ env.TF_VERSION }}
    
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v2
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: ${{ env.AWS_DEFAULT_REGION }}
    
    - name: Terraform Init
      run: terraform init
    
    - name: Terraform Apply
      run: terraform apply -auto-approve
    
    - name: Output Summary
      run: |
        echo "### Terraform Apply Summary" >> $GITHUB_STEP_SUMMARY
        terraform output -json | jq -r 'to_entries[] | "- **\(.key)**: \(.value.value)"' >> $GITHUB_STEP_SUMMARY
```

## 6. Testing và Validation

### 6.1 Infrastructure Testing với Terratest

```go
// test/terraform_test.go
package test

import (
    "testing"
    "github.com/gruntwork-io/terratest/modules/terraform"
    "github.com/gruntwork-io/terratest/modules/aws"
    "github.com/stretchr/testify/assert"
)

func TestTerraformInfrastructure(t *testing.T) {
    t.Parallel()

    // Construct the terraform options with default retryable errors to handle
    terraformOptions := terraform.WithDefaultRetryableErrors(t, &terraform.Options{
        TerraformDir: "../",
        
        Vars: map[string]interface{}{
            "environment":    "test",
            "instance_type":  "t3.micro",
            "instance_count": 2,
        },
        
        EnvVars: map[string]string{
            "AWS_DEFAULT_REGION": "us-west-2",
        },
    })

    // Clean up resources with "terraform destroy" at the end of the test
    defer terraform.Destroy(t, terraformOptions)

    // Run "terraform init" and "terraform apply"
    terraform.InitAndApply(t, terraformOptions)

    // Get the outputs
    vpcId := terraform.Output(t, terraformOptions, "vpc_id")
    instanceIds := terraform.OutputList(t, terraformOptions, "instance_ids")
    
    // Verify VPC exists
    vpc := aws.GetVpcById(t, vpcId, "us-west-2")
    assert.Equal(t, "10.0.0.0/16", vpc.CidrBlock)
    
    // Verify instances are running
    for _, instanceId := range instanceIds {
        instance := aws.GetEc2Instance(t, "us-west-2", instanceId)
        assert.Equal(t, "running", instance.State)
        assert.Equal(t, "t3.micro", instance.InstanceType)
    }
    
    // Test security group rules
    sgId := terraform.Output(t, terraformOptions, "security_group_id")
    sg := aws.GetSecurityGroupById(t, sgId, "us-west-2")
    
    // Verify SSH access is allowed
    sshRuleFound := false
    for _, rule := range sg.IngressRules {
        if rule.FromPort == 22 && rule.ToPort == 22 {
            sshRuleFound = true
            break
        }
    }
    assert.True(t, sshRuleFound, "SSH access should be allowed")
}

func TestTerraformValidation(t *testing.T) {
    terraformOptions := &terraform.Options{
        TerraformDir: "../",
    }
    
    // Validate terraform configuration
    terraform.Validate(t, terraformOptions)
}
```

### 6.2 Policy Testing

```python
# tests/test_policies.py
import json
import pytest
import subprocess

def run_terraform_plan():
    """Run terraform plan and return JSON output"""
    result = subprocess.run(
        ["terraform", "plan", "-out=tfplan.binary"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        pytest.fail(f"Terraform plan failed: {result.stderr}")
    
    # Convert binary plan to JSON
    result = subprocess.run(
        ["terraform", "show", "-json", "tfplan.binary"],
        capture_output=True,
        text=True
    )
    
    return json.loads(result.stdout)

def test_required_tags():
    """Test that all resources have required tags"""
    plan = run_terraform_plan()
    required_tags = ["Environment", "Project", "Owner"]
    
    for resource in plan["planned_values"]["root_module"]["resources"]:
        if "tags" in resource["values"]:
            tags = resource["values"]["tags"]
            for required_tag in required_tags:
                assert required_tag in tags, f"Resource {resource['address']} missing tag {required_tag}"

def test_security_group_rules():
    """Test that security groups don't allow unrestricted access"""
    plan = run_terraform_plan()
    
    for resource in plan["planned_values"]["root_module"]["resources"]:
        if resource["type"] == "aws_security_group":
            for rule in resource["values"].get("ingress", []):
                cidr_blocks = rule.get("cidr_blocks", [])
                if "0.0.0.0/0" in cidr_blocks:
                    allowed_ports = [80, 443]  # Only allow HTTP/HTTPS from anywhere
                    assert rule["from_port"] in allowed_ports, f"Port {rule['from_port']} should not be open to 0.0.0.0/0"

def test_instance_types():
    """Test that only approved instance types are used"""
    plan = run_terraform_plan()
    approved_types = ["t3.micro", "t3.small", "t3.medium", "t3.large"]
    
    for resource in plan["planned_values"]["root_module"]["resources"]:
        if resource["type"] == "aws_instance":
            instance_type = resource["values"]["instance_type"]
            assert instance_type in approved_types, f"Instance type {instance_type} not approved"

def test_encryption_enabled():
    """Test that encryption is enabled for storage resources"""
    plan = run_terraform_plan()
    
    for resource in plan["planned_values"]["root_module"]["resources"]:
        if resource["type"] == "aws_ebs_volume":
            assert resource["values"]["encrypted"] == True, "EBS volumes must be encrypted"
        
        if resource["type"] == "aws_s3_bucket":
            # Check for encryption configuration
            # This would need additional logic to verify encryption is properly configured
            pass
```

## 📚 Tài liệu Tham khảo
- [Terraform Enterprise Documentation](https://www.terraform.io/docs/enterprise)
- [Terraform Cloud Documentation](https://www.terraform.io/docs/cloud)
- [Sentinel Documentation](https://docs.hashicorp.com/sentinel)
- [Terratest Documentation](https://terratest.gruntwork.io/)

## 🔍 Câu hỏi Ôn tập
1. Làm thế nào để implement state locking trong môi trường team?
2. Best practices cho Terraform module versioning và distribution?
3. Cách integrate Terraform với CI/CD pipelines một cách an toàn?
4. Strategies để test Infrastructure as Code?
5. Làm thế nào để implement policy as code với Sentinel?

---
*Chú thích: Advanced Terraform features giúp tối ưu hóa workflows và đảm bảo governance trong enterprise environments.*
