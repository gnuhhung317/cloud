# Integration Labs - Ansible + Terraform + CI/CD

## 🎯 Mục tiêu Integration Labs
- Kết hợp Ansible và Terraform trong workflows thực tế
- Tích hợp automation tools với CI/CD pipelines
- Triển khai complete DevOps workflows
- Áp dụng GitOps principles

## Lab 1: Terraform + Ansible Integration

### Lab 1.1: Infrastructure Provisioning với Configuration Management

#### Project Structure
```bash
project/
├── terraform/
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   └── userdata.tf
├── ansible/
│   ├── inventory/
│   │   └── aws_ec2.yml
│   ├── playbooks/
│   │   ├── site.yml
│   │   └── configure-servers.yml
│   ├── roles/
│   │   ├── common/
│   │   ├── webserver/
│   │   └── database/
│   └── ansible.cfg
├── scripts/
│   ├── deploy.sh
│   └── destroy.sh
└── .github/
    └── workflows/
        └── deploy.yml
```

#### Terraform Configuration với Ansible Integration
```hcl
# terraform/main.tf
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    local = {
      source  = "hashicorp/local"
      version = "~> 2.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# VPC và networking
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "${var.project_name}-vpc"
  cidr = var.vpc_cidr

  azs             = data.aws_availability_zones.available.names
  public_subnets  = var.public_subnets
  private_subnets = var.private_subnets

  enable_nat_gateway = true
  enable_vpn_gateway = false
  enable_dns_hostnames = true

  tags = local.common_tags
}

# Security Groups
resource "aws_security_group" "web" {
  name_prefix = "${var.project_name}-web-"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # Restrict this in production
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-web-sg"
  })
}

resource "aws_security_group" "database" {
  name_prefix = "${var.project_name}-db-"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port       = 3306
    to_port         = 3306
    protocol        = "tcp"
    security_groups = [aws_security_group.web.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-db-sg"
  })
}

# Key Pair for SSH access
resource "aws_key_pair" "main" {
  key_name   = "${var.project_name}-key"
  public_key = file(var.public_key_path)

  tags = local.common_tags
}

# Web Servers
resource "aws_instance" "web" {
  count = var.web_instance_count

  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.web_instance_type
  subnet_id              = module.vpc.public_subnets[count.index % length(module.vpc.public_subnets)]
  vpc_security_group_ids = [aws_security_group.web.id]
  key_name               = aws_key_pair.main.key_name

  user_data = base64encode(templatefile("${path.module}/userdata.sh", {
    hostname = "${var.project_name}-web-${count.index + 1}"
  }))

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-web-${count.index + 1}"
    Type = "WebServer"
    AnsibleGroup = "webservers"
  })
}

# Database Server
resource "aws_instance" "database" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.db_instance_type
  subnet_id              = module.vpc.private_subnets[0]
  vpc_security_group_ids = [aws_security_group.database.id]
  key_name               = aws_key_pair.main.key_name

  user_data = base64encode(templatefile("${path.module}/userdata.sh", {
    hostname = "${var.project_name}-database"
  }))

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-database"
    Type = "Database"
    AnsibleGroup = "databases"
  })
}

# Load Balancer
resource "aws_lb" "main" {
  name               = "${var.project_name}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.web.id]
  subnets           = module.vpc.public_subnets

  tags = local.common_tags
}

resource "aws_lb_target_group" "web" {
  name     = "${var.project_name}-web-tg"
  port     = 80
  protocol = "HTTP"
  vpc_id   = module.vpc.vpc_id

  health_check {
    enabled             = true
    healthy_threshold   = 2
    interval            = 30
    matcher             = "200"
    path                = "/health"
    port                = "traffic-port"
    protocol            = "HTTP"
    timeout             = 5
    unhealthy_threshold = 2
  }

  tags = local.common_tags
}

resource "aws_lb_target_group_attachment" "web" {
  count = length(aws_instance.web)

  target_group_arn = aws_lb_target_group.web.arn
  target_id        = aws_instance.web[count.index].id
  port             = 80
}

resource "aws_lb_listener" "web" {
  load_balancer_arn = aws_lb.main.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.web.arn
  }
}

# Generate Ansible inventory
resource "local_file" "ansible_inventory" {
  content = templatefile("${path.module}/templates/inventory.yml.tpl", {
    web_servers = aws_instance.web
    db_servers  = [aws_instance.database]
    bastion_host = var.bastion_host
  })
  filename = "${path.module}/../ansible/inventory/hosts.yml"
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

locals {
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
    Owner       = var.owner
  }
}
```

#### Ansible Dynamic Inventory
```yaml
# ansible/inventory/aws_ec2.yml
---
plugin: amazon.aws.aws_ec2
regions:
  - us-west-2
hostnames:
  - tag:Name
filters:
  instance-state-name: running
  tag:Project: terraform-ansible-lab
keyed_groups:
  - prefix: tag
    key: tags
  - prefix: instance_type
    key: instance_type
  - prefix: placement
    key: placement.availability_zone
groups:
  webservers: "'webservers' in (tags.AnsibleGroup|default(''))"
  databases: "'databases' in (tags.AnsibleGroup|default(''))"
compose:
  ansible_host: public_ip_address | default(private_ip_address)
```

#### Ansible Playbooks
```yaml
# ansible/playbooks/site.yml
---
- name: Configure all servers
  hosts: all
  become: yes
  gather_facts: yes
  
  pre_tasks:
    - name: Update package cache
      apt:
        update_cache: yes
      when: ansible_os_family == "Debian"
  
  roles:
    - common

- name: Configure web servers
  hosts: webservers
  become: yes
  
  roles:
    - webserver
  
  vars:
    nginx_sites:
      - name: default
        server_name: "{{ ansible_default_ipv4.address }}"
        document_root: /var/www/html
        enable_ssl: false

- name: Configure database servers
  hosts: databases
  become: yes
  
  roles:
    - database
  
  vars:
    mysql_root_password: "{{ vault_mysql_root_password }}"
    mysql_databases:
      - name: webapp
        encoding: utf8
    mysql_users:
      - name: webapp
        password: "{{ vault_mysql_webapp_password }}"
        priv: "webapp.*:ALL"
        host: "%"
```

#### Common Role
```yaml
# ansible/roles/common/tasks/main.yml
---
- name: Install common packages
  package:
    name:
      - curl
      - wget
      - unzip
      - git
      - htop
      - vim
      - fail2ban
      - ufw
    state: present

- name: Configure timezone
  timezone:
    name: "{{ system_timezone | default('UTC') }}"

- name: Configure firewall
  ufw:
    state: enabled
    policy: deny
    direction: incoming

- name: Allow SSH
  ufw:
    rule: allow
    port: 22
    proto: tcp

- name: Configure fail2ban
  service:
    name: fail2ban
    state: started
    enabled: yes

- name: Create application user
  user:
    name: "{{ app_user }}"
    group: "{{ app_group }}"
    system: yes
    shell: /bin/bash
    home: "{{ app_home }}"
    create_home: yes

- name: Configure SSH keys
  authorized_key:
    user: "{{ app_user }}"
    key: "{{ item }}"
  loop: "{{ ssh_public_keys }}"
  when: ssh_public_keys is defined
```

#### WebServer Role
```yaml
# ansible/roles/webserver/tasks/main.yml
---
- name: Install nginx
  package:
    name: nginx
    state: present

- name: Install PHP and modules
  package:
    name:
      - php-fpm
      - php-mysql
      - php-json
      - php-curl
      - php-gd
      - php-xml
      - php-zip
    state: present

- name: Configure nginx main config
  template:
    src: nginx.conf.j2
    dest: /etc/nginx/nginx.conf
    backup: yes
  notify: restart nginx

- name: Configure virtual hosts
  template:
    src: vhost.conf.j2
    dest: "/etc/nginx/sites-available/{{ item.name }}"
  loop: "{{ nginx_sites }}"
  notify: restart nginx

- name: Enable virtual hosts
  file:
    src: "/etc/nginx/sites-available/{{ item.name }}"
    dest: "/etc/nginx/sites-enabled/{{ item.name }}"
    state: link
  loop: "{{ nginx_sites }}"
  notify: restart nginx

- name: Remove default site
  file:
    path: /etc/nginx/sites-enabled/default
    state: absent
  notify: restart nginx

- name: Create document roots
  file:
    path: "{{ item.document_root }}"
    state: directory
    owner: www-data
    group: www-data
    mode: '0755'
  loop: "{{ nginx_sites }}"

- name: Deploy application
  template:
    src: index.php.j2
    dest: "{{ item.document_root }}/index.php"
    owner: www-data
    group: www-data
    mode: '0644'
  loop: "{{ nginx_sites }}"

- name: Create health check endpoint
  copy:
    content: "OK"
    dest: "{{ item.document_root }}/health"
    owner: www-data
    group: www-data
    mode: '0644'
  loop: "{{ nginx_sites }}"

- name: Configure firewall for web services
  ufw:
    rule: allow
    port: "{{ item }}"
    proto: tcp
  loop:
    - 80
    - 443

- name: Start and enable services
  service:
    name: "{{ item }}"
    state: started
    enabled: yes
  loop:
    - nginx
    - php7.4-fpm
```

### Lab 1.2: Deployment Script
```bash
#!/bin/bash
# scripts/deploy.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TERRAFORM_DIR="${PROJECT_ROOT}/terraform"
ANSIBLE_DIR="${PROJECT_ROOT}/ansible"

# Default values
ENVIRONMENT="dev"
SKIP_TERRAFORM=false
SKIP_ANSIBLE=false
DESTROY=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        --skip-terraform)
            SKIP_TERRAFORM=true
            shift
            ;;
        --skip-ansible)
            SKIP_ANSIBLE=true
            shift
            ;;
        --destroy)
            DESTROY=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  -e, --environment ENV    Set environment (default: dev)"
            echo "  --skip-terraform        Skip Terraform deployment"
            echo "  --skip-ansible          Skip Ansible configuration"
            echo "  --destroy               Destroy infrastructure"
            echo "  -h, --help              Show this help message"
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

log_info "Starting deployment for environment: $ENVIRONMENT"

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if required tools are installed
    for tool in terraform ansible aws; do
        if ! command -v $tool &> /dev/null; then
            log_error "$tool is not installed or not in PATH"
            exit 1
        fi
    done
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS credentials not configured"
        exit 1
    fi
    
    log_info "Prerequisites check passed"
}

# Terraform deployment
deploy_terraform() {
    if [ "$SKIP_TERRAFORM" = true ]; then
        log_warn "Skipping Terraform deployment"
        return
    fi
    
    log_info "Deploying infrastructure with Terraform..."
    
    cd "$TERRAFORM_DIR"
    
    # Initialize Terraform
    log_info "Initializing Terraform..."
    terraform init
    
    # Validate configuration
    log_info "Validating Terraform configuration..."
    terraform validate
    
    if [ "$DESTROY" = true ]; then
        log_warn "Destroying infrastructure..."
        terraform destroy -auto-approve -var-file="environments/${ENVIRONMENT}.tfvars"
        return
    fi
    
    # Plan deployment
    log_info "Planning Terraform deployment..."
    terraform plan -var-file="environments/${ENVIRONMENT}.tfvars" -out=tfplan
    
    # Apply deployment
    log_info "Applying Terraform configuration..."
    terraform apply tfplan
    
    # Wait for instances to be ready
    log_info "Waiting for instances to be ready..."
    sleep 60
    
    log_info "Infrastructure deployment completed"
}

# Ansible configuration
configure_ansible() {
    if [ "$SKIP_ANSIBLE" = true ]; then
        log_warn "Skipping Ansible configuration"
        return
    fi
    
    if [ "$DESTROY" = true ]; then
        log_warn "Skipping Ansible configuration due to destroy mode"
        return
    fi
    
    log_info "Configuring servers with Ansible..."
    
    cd "$ANSIBLE_DIR"
    
    # Wait for inventory to be generated
    if [ ! -f "inventory/hosts.yml" ]; then
        log_error "Ansible inventory not found. Terraform might have failed."
        exit 1
    fi
    
    # Test connectivity
    log_info "Testing Ansible connectivity..."
    ansible all -i inventory/hosts.yml -m ping --ssh-common-args='-o StrictHostKeyChecking=no'
    
    # Run playbook
    log_info "Running Ansible playbook..."
    ansible-playbook -i inventory/hosts.yml playbooks/site.yml --ssh-common-args='-o StrictHostKeyChecking=no'
    
    log_info "Server configuration completed"
}

# Validate deployment
validate_deployment() {
    if [ "$DESTROY" = true ]; then
        log_info "Deployment destroyed successfully"
        return
    fi
    
    log_info "Validating deployment..."
    
    cd "$TERRAFORM_DIR"
    
    # Get load balancer DNS
    ALB_DNS=$(terraform output -raw alb_dns_name 2>/dev/null || echo "")
    
    if [ -n "$ALB_DNS" ]; then
        log_info "Testing load balancer endpoint: http://$ALB_DNS"
        
        # Wait for load balancer to be ready
        for i in {1..30}; do
            if curl -s --connect-timeout 5 "http://$ALB_DNS/health" > /dev/null; then
                log_info "✅ Load balancer is responding"
                break
            else
                log_warn "Waiting for load balancer... (attempt $i/30)"
                sleep 10
            fi
        done
        
        # Test main page
        if curl -s "http://$ALB_DNS" | grep -q "Hello"; then
            log_info "✅ Application is responding correctly"
        else
            log_warn "⚠️  Application might not be fully ready"
        fi
    else
        log_warn "Could not retrieve load balancer DNS"
    fi
}

# Main execution
main() {
    check_prerequisites
    deploy_terraform
    configure_ansible
    validate_deployment
    
    if [ "$DESTROY" = false ]; then
        log_info "🎉 Deployment completed successfully!"
        
        # Show important outputs
        cd "$TERRAFORM_DIR"
        echo ""
        log_info "Important endpoints:"
        terraform output -json | jq -r '
            to_entries[] | 
            select(.key | test("dns|ip|url")) | 
            "  \(.key): \(.value.value)"
        ' 2>/dev/null || true
    fi
}

# Run main function
main
```

## Lab 2: CI/CD Pipeline Integration

### Lab 2.1: GitHub Actions Workflow
```yaml
# .github/workflows/deploy.yml
name: 'Infrastructure Deployment'

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

env:
  TF_VERSION: 1.5.0
  ANSIBLE_VERSION: 6.0.0
  AWS_DEFAULT_REGION: us-west-2

jobs:
  validate:
    name: 'Validate Infrastructure Code'
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout
      uses: actions/checkout@v3
    
    - name: Setup Terraform
      uses: hashicorp/setup-terraform@v2
      with:
        terraform_version: ${{ env.TF_VERSION }}
    
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install Ansible
      run: |
        pip install ansible==${{ env.ANSIBLE_VERSION }}
        pip install boto3 botocore
    
    - name: Terraform Format Check
      run: terraform fmt -check -recursive
      working-directory: terraform
    
    - name: Terraform Init
      run: terraform init -backend=false
      working-directory: terraform
    
    - name: Terraform Validate
      run: terraform validate
      working-directory: terraform
    
    - name: Ansible Syntax Check
      run: |
        ansible-playbook --syntax-check playbooks/site.yml
      working-directory: ansible
    
    - name: Ansible Lint
      run: |
        pip install ansible-lint
        ansible-lint playbooks/site.yml
      working-directory: ansible
      continue-on-error: true

  security-scan:
    name: 'Security Scan'
    runs-on: ubuntu-latest
    needs: validate
    
    steps:
    - name: Checkout
      uses: actions/checkout@v3
    
    - name: Run Checkov
      uses: bridgecrewio/checkov-action@master
      with:
        directory: terraform
        framework: terraform
        output_format: sarif
        output_file_path: checkov.sarif
        soft_fail: true
    
    - name: Upload Checkov results
      uses: github/codeql-action/upload-sarif@v2
      if: always()
      with:
        sarif_file: checkov.sarif
    
    - name: Run tfsec
      uses: aquasecurity/tfsec-action@v1.0.0
      with:
        working_directory: terraform
        soft_fail: true

  plan:
    name: 'Terraform Plan'
    runs-on: ubuntu-latest
    needs: [validate, security-scan]
    if: github.event_name == 'pull_request'
    
    outputs:
      tfplan: ${{ steps.plan.outputs.stdout }}
    
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
      working-directory: terraform
    
    - name: Terraform Plan
      id: plan
      run: |
        terraform plan -var-file="environments/dev.tfvars" -no-color
      working-directory: terraform
      continue-on-error: true
    
    - name: Comment PR
      uses: actions/github-script@v6
      with:
        script: |
          const output = `#### Terraform Plan 📖
          <details><summary>Show Plan</summary>
          
          \`\`\`terraform
          ${{ steps.plan.outputs.stdout }}
          \`\`\`
          
          </details>
          
          *Pusher: @${{ github.actor }}, Action: \`${{ github.event_name }}\`*`;
          
          github.rest.issues.createComment({
            issue_number: context.issue.number,
            owner: context.repo.owner,
            repo: context.repo.repo,
            body: output
          })

  deploy-dev:
    name: 'Deploy to Development'
    runs-on: ubuntu-latest
    needs: validate
    if: github.ref == 'refs/heads/develop'
    environment: development
    
    steps:
    - name: Checkout
      uses: actions/checkout@v3
    
    - name: Setup Terraform
      uses: hashicorp/setup-terraform@v2
      with:
        terraform_version: ${{ env.TF_VERSION }}
    
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install Ansible
      run: |
        pip install ansible==${{ env.ANSIBLE_VERSION }}
        pip install boto3 botocore
    
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v2
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: ${{ env.AWS_DEFAULT_REGION }}
    
    - name: Deploy Infrastructure
      run: |
        chmod +x scripts/deploy.sh
        ./scripts/deploy.sh --environment dev
    
    - name: Run Integration Tests
      run: |
        python -m pytest tests/integration/ -v
      continue-on-error: true

  deploy-prod:
    name: 'Deploy to Production'
    runs-on: ubuntu-latest
    needs: validate
    if: github.ref == 'refs/heads/main'
    environment: production
    
    steps:
    - name: Checkout
      uses: actions/checkout@v3
    
    - name: Setup Terraform
      uses: hashicorp/setup-terraform@v2
      with:
        terraform_version: ${{ env.TF_VERSION }}
    
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install Ansible
      run: |
        pip install ansible==${{ env.ANSIBLE_VERSION }}
        pip install boto3 botocore
    
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v2
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: ${{ env.AWS_DEFAULT_REGION }}
    
    - name: Deploy Infrastructure
      run: |
        chmod +x scripts/deploy.sh
        ./scripts/deploy.sh --environment prod
    
    - name: Run Production Tests
      run: |
        python -m pytest tests/production/ -v
    
    - name: Notify Slack
      if: always()
      uses: 8398a7/action-slack@v3
      with:
        status: ${{ job.status }}
        channel: '#deployments'
        webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### Lab 2.2: GitLab CI Pipeline
```yaml
# .gitlab-ci.yml
stages:
  - validate
  - security
  - plan
  - deploy-dev
  - test
  - deploy-prod

variables:
  TF_ROOT: ${CI_PROJECT_DIR}/terraform
  ANSIBLE_ROOT: ${CI_PROJECT_DIR}/ansible
  TF_ADDRESS: ${CI_API_V4_URL}/projects/${CI_PROJECT_ID}/terraform/state/main

cache:
  paths:
    - ${TF_ROOT}/.terraform

before_script:
  - apt-get update -qq && apt-get install -y -qq git curl python3 python3-pip
  - pip3 install ansible boto3 botocore
  - curl -LO https://releases.hashicorp.com/terraform/1.5.0/terraform_1.5.0_linux_amd64.zip
  - unzip terraform_1.5.0_linux_amd64.zip
  - mv terraform /usr/local/bin/
  - terraform --version

# Validation Stage
validate:terraform:
  stage: validate
  script:
    - cd ${TF_ROOT}
    - terraform fmt -check=true -diff=true
    - terraform init -backend=false
    - terraform validate
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_COMMIT_BRANCH == "main"'
    - if: '$CI_COMMIT_BRANCH == "develop"'

validate:ansible:
  stage: validate
  script:
    - cd ${ANSIBLE_ROOT}
    - ansible-playbook --syntax-check playbooks/site.yml
    - pip3 install ansible-lint
    - ansible-lint playbooks/site.yml
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_COMMIT_BRANCH == "main"'
    - if: '$CI_COMMIT_BRANCH == "develop"'
  allow_failure: true

# Security Stage
security:checkov:
  stage: security
  image: bridgecrew/checkov:latest
  script:
    - checkov -d ${TF_ROOT} --framework terraform --output json
  artifacts:
    reports:
      sast: checkov-results.json
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_COMMIT_BRANCH == "main"'
  allow_failure: true

security:tfsec:
  stage: security
  script:
    - curl -s https://raw.githubusercontent.com/aquasecurity/tfsec/master/scripts/install_linux.sh | bash
    - tfsec ${TF_ROOT} --format json --out tfsec-results.json
  artifacts:
    paths:
      - tfsec-results.json
    expire_in: 1 week
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_COMMIT_BRANCH == "main"'
  allow_failure: true

# Plan Stage
plan:
  stage: plan
  script:
    - cd ${TF_ROOT}
    - terraform init
    - terraform plan -var-file="environments/dev.tfvars" -out=tfplan
    - terraform show -no-color tfplan
  artifacts:
    paths:
      - ${TF_ROOT}/tfplan
    expire_in: 1 week
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'

# Development Deployment
deploy:dev:
  stage: deploy-dev
  environment:
    name: development
    url: http://$ALB_DNS
  script:
    - cd ${CI_PROJECT_DIR}
    - chmod +x scripts/deploy.sh
    - ./scripts/deploy.sh --environment dev
    - cd ${TF_ROOT}
    - export ALB_DNS=$(terraform output -raw alb_dns_name)
    - echo "ALB_DNS=${ALB_DNS}" >> deploy.env
  artifacts:
    reports:
      dotenv: ${TF_ROOT}/deploy.env
  rules:
    - if: '$CI_COMMIT_BRANCH == "develop"'

# Integration Tests
test:integration:
  stage: test
  dependencies:
    - deploy:dev
  script:
    - pip3 install pytest requests
    - python -m pytest tests/integration/ -v --junit-xml=integration-results.xml
  artifacts:
    reports:
      junit: integration-results.xml
  rules:
    - if: '$CI_COMMIT_BRANCH == "develop"'

# Production Deployment
deploy:prod:
  stage: deploy-prod
  environment:
    name: production
    url: http://$ALB_DNS
  script:
    - cd ${CI_PROJECT_DIR}
    - chmod +x scripts/deploy.sh
    - ./scripts/deploy.sh --environment prod
    - cd ${TF_ROOT}
    - export ALB_DNS=$(terraform output -raw alb_dns_name)
  rules:
    - if: '$CI_COMMIT_BRANCH == "main"'
      when: manual
  before_script:
    - !reference [.before_script]
    - echo "Deploying to production requires manual approval"
```

## Lab 3: GitOps Workflow

### Lab 3.1: ArgoCD Integration
```yaml
# k8s/argocd-app.yml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: infrastructure-app
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/viettel-idc/infrastructure-repo.git
    targetRevision: HEAD
    path: k8s/manifests
  destination:
    server: https://kubernetes.default.svc
    namespace: default
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
    - CreateNamespace=true
```

### Lab 3.2: Helm Charts Integration
```yaml
# helm/infrastructure/Chart.yaml
apiVersion: v2
name: infrastructure
description: Infrastructure deployment chart
type: application
version: 1.0.0
appVersion: "1.0"

# helm/infrastructure/values.yaml
replicaCount: 3

image:
  repository: nginx
  pullPolicy: IfNotPresent
  tag: "latest"

service:
  type: LoadBalancer
  port: 80

ingress:
  enabled: true
  className: "nginx"
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
  hosts:
    - host: app.viettel-idc.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: app-tls
      hosts:
        - app.viettel-idc.com

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80

resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 250m
    memory: 256Mi

nodeSelector: {}

tolerations: []

affinity: {}
```

## Lab 4: Monitoring và Observability

### Lab 4.1: Prometheus + Grafana Setup
```yaml
# ansible/roles/monitoring/tasks/main.yml
---
- name: Create monitoring user
  user:
    name: prometheus
    system: yes
    shell: /bin/false
    home: /var/lib/prometheus
    create_home: no

- name: Create monitoring directories
  file:
    path: "{{ item }}"
    state: directory
    owner: prometheus
    group: prometheus
    mode: '0755'
  loop:
    - /etc/prometheus
    - /var/lib/prometheus
    - /var/log/prometheus

- name: Download and install Prometheus
  unarchive:
    src: "https://github.com/prometheus/prometheus/releases/download/v{{ prometheus_version }}/prometheus-{{ prometheus_version }}.linux-amd64.tar.gz"
    dest: /tmp
    remote_src: yes
    owner: prometheus
    group: prometheus
  notify: restart prometheus

- name: Copy Prometheus binaries
  copy:
    src: "/tmp/prometheus-{{ prometheus_version }}.linux-amd64/{{ item }}"
    dest: "/usr/local/bin/{{ item }}"
    owner: prometheus
    group: prometheus
    mode: '0755'
    remote_src: yes
  loop:
    - prometheus
    - promtool
  notify: restart prometheus

- name: Configure Prometheus
  template:
    src: prometheus.yml.j2
    dest: /etc/prometheus/prometheus.yml
    owner: prometheus
    group: prometheus
    mode: '0644'
  notify: restart prometheus

- name: Create Prometheus systemd service
  template:
    src: prometheus.service.j2
    dest: /etc/systemd/system/prometheus.service
  notify:
    - reload systemd
    - restart prometheus

- name: Start and enable Prometheus
  service:
    name: prometheus
    state: started
    enabled: yes

# Node Exporter
- name: Download and install Node Exporter
  unarchive:
    src: "https://github.com/prometheus/node_exporter/releases/download/v{{ node_exporter_version }}/node_exporter-{{ node_exporter_version }}.linux-amd64.tar.gz"
    dest: /tmp
    remote_src: yes
  notify: restart node_exporter

- name: Copy Node Exporter binary
  copy:
    src: "/tmp/node_exporter-{{ node_exporter_version }}.linux-amd64/node_exporter"
    dest: "/usr/local/bin/node_exporter"
    owner: prometheus
    group: prometheus
    mode: '0755'
    remote_src: yes
  notify: restart node_exporter

- name: Create Node Exporter systemd service
  template:
    src: node_exporter.service.j2
    dest: /etc/systemd/system/node_exporter.service
  notify:
    - reload systemd
    - restart node_exporter

- name: Start and enable Node Exporter
  service:
    name: node_exporter
    state: started
    enabled: yes
```

### Lab 4.2: Logging Stack
```yaml
# ansible/roles/logging/tasks/main.yml
---
- name: Install Java for Elasticsearch
  package:
    name: openjdk-11-jdk
    state: present

- name: Add Elastic repository key
  apt_key:
    url: https://artifacts.elastic.co/GPG-KEY-elasticsearch
    state: present

- name: Add Elastic repository
  apt_repository:
    repo: "deb https://artifacts.elastic.co/packages/7.x/apt stable main"
    state: present

- name: Install Elasticsearch
  package:
    name: elasticsearch
    state: present

- name: Configure Elasticsearch
  template:
    src: elasticsearch.yml.j2
    dest: /etc/elasticsearch/elasticsearch.yml
    backup: yes
  notify: restart elasticsearch

- name: Start and enable Elasticsearch
  service:
    name: elasticsearch
    state: started
    enabled: yes

- name: Install Logstash
  package:
    name: logstash
    state: present

- name: Configure Logstash
  template:
    src: "{{ item }}.j2"
    dest: "/etc/logstash/conf.d/{{ item }}"
  loop:
    - 01-input.conf
    - 02-filter.conf
    - 03-output.conf
  notify: restart logstash

- name: Start and enable Logstash
  service:
    name: logstash
    state: started
    enabled: yes

- name: Install Kibana
  package:
    name: kibana
    state: present

- name: Configure Kibana
  template:
    src: kibana.yml.j2
    dest: /etc/kibana/kibana.yml
    backup: yes
  notify: restart kibana

- name: Start and enable Kibana
  service:
    name: kibana
    state: started
    enabled: yes
```

## Lab 5: Security và Compliance

### Lab 5.1: Security Hardening Playbook
```yaml
# ansible/playbooks/security-hardening.yml
---
- name: Security Hardening
  hosts: all
  become: yes
  
  tasks:
    - name: Update all packages
      package:
        name: "*"
        state: latest
    
    - name: Install security packages
      package:
        name:
          - fail2ban
          - ufw
          - aide
          - chkrootkit
          - rkhunter
        state: present
    
    - name: Configure SSH hardening
      lineinfile:
        path: /etc/ssh/sshd_config
        regexp: "{{ item.regexp }}"
        line: "{{ item.line }}"
        backup: yes
      loop:
        - { regexp: '^#?PermitRootLogin', line: 'PermitRootLogin no' }
        - { regexp: '^#?PasswordAuthentication', line: 'PasswordAuthentication no' }
        - { regexp: '^#?X11Forwarding', line: 'X11Forwarding no' }
        - { regexp: '^#?MaxAuthTries', line: 'MaxAuthTries 3' }
        - { regexp: '^#?ClientAliveInterval', line: 'ClientAliveInterval 300' }
        - { regexp: '^#?ClientAliveCountMax', line: 'ClientAliveCountMax 2' }
      notify: restart ssh
    
    - name: Configure firewall
      ufw:
        rule: "{{ item.rule }}"
        port: "{{ item.port }}"
        proto: "{{ item.proto }}"
      loop:
        - { rule: 'allow', port: '22', proto: 'tcp' }
        - { rule: 'allow', port: '80', proto: 'tcp' }
        - { rule: 'allow', port: '443', proto: 'tcp' }
    
    - name: Enable firewall
      ufw:
        state: enabled
        policy: deny
        direction: incoming
    
    - name: Configure fail2ban
      template:
        src: jail.local.j2
        dest: /etc/fail2ban/jail.local
      notify: restart fail2ban
    
    - name: Set password policy
      lineinfile:
        path: /etc/login.defs
        regexp: "{{ item.regexp }}"
        line: "{{ item.line }}"
      loop:
        - { regexp: '^PASS_MAX_DAYS', line: 'PASS_MAX_DAYS 90' }
        - { regexp: '^PASS_MIN_DAYS', line: 'PASS_MIN_DAYS 1' }
        - { regexp: '^PASS_WARN_AGE', line: 'PASS_WARN_AGE 7' }
    
    - name: Configure kernel parameters
      sysctl:
        name: "{{ item.name }}"
        value: "{{ item.value }}"
        sysctl_file: /etc/sysctl.d/99-security.conf
        reload: yes
      loop:
        - { name: 'net.ipv4.ip_forward', value: '0' }
        - { name: 'net.ipv4.conf.all.send_redirects', value: '0' }
        - { name: 'net.ipv4.conf.all.accept_redirects', value: '0' }
        - { name: 'net.ipv4.conf.all.accept_source_route', value: '0' }
        - { name: 'net.ipv4.conf.all.log_martians', value: '1' }
        - { name: 'net.ipv4.icmp_echo_ignore_broadcasts', value: '1' }
        - { name: 'net.ipv4.icmp_ignore_bogus_error_responses', value: '1' }
    
    - name: Configure audit rules
      lineinfile:
        path: /etc/audit/rules.d/audit.rules
        line: "{{ item }}"
        create: yes
      loop:
        - '-w /etc/passwd -p wa -k identity'
        - '-w /etc/group -p wa -k identity'
        - '-w /etc/shadow -p wa -k identity'
        - '-w /etc/sudoers -p wa -k identity'
        - '-w /var/log/auth.log -p wa -k authentication'
        - '-w /var/log/secure -p wa -k authentication'
      notify: restart auditd
  
  handlers:
    - name: restart ssh
      service:
        name: ssh
        state: restarted
    
    - name: restart fail2ban
      service:
        name: fail2ban
        state: restarted
    
    - name: restart auditd
      service:
        name: auditd
        state: restarted
```

### Lab 5.2: Compliance Scanning
```python
# scripts/compliance_scan.py
#!/usr/bin/env python3

import subprocess
import json
import sys
from datetime import datetime

def run_command(command):
    """Run shell command and return output"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout, result.stderr, result.returncode
    except Exception as e:
        return "", str(e), 1

def check_cis_compliance():
    """Check CIS compliance"""
    checks = {
        "ssh_root_login": "grep '^PermitRootLogin no' /etc/ssh/sshd_config",
        "ssh_password_auth": "grep '^PasswordAuthentication no' /etc/ssh/sshd_config",
        "firewall_enabled": "ufw status | grep 'Status: active'",
        "fail2ban_running": "systemctl is-active fail2ban",
        "password_policy": "grep '^PASS_MAX_DAYS 90' /etc/login.defs"
    }
    
    results = {}
    for check_name, command in checks.items():
        stdout, stderr, returncode = run_command(command)
        results[check_name] = {
            "passed": returncode == 0,
            "output": stdout.strip(),
            "error": stderr.strip()
        }
    
    return results

def generate_report(results):
    """Generate compliance report"""
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_checks": len(results),
        "passed_checks": sum(1 for r in results.values() if r["passed"]),
        "failed_checks": sum(1 for r in results.values() if not r["passed"]),
        "details": results
    }
    
    return report

def main():
    print("Running CIS compliance scan...")
    
    # Run compliance checks
    results = check_cis_compliance()
    
    # Generate report
    report = generate_report(results)
    
    # Save report
    with open("compliance_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    print(f"Compliance scan completed:")
    print(f"  Total checks: {report['total_checks']}")
    print(f"  Passed: {report['passed_checks']}")
    print(f"  Failed: {report['failed_checks']}")
    
    # Exit with error if any checks failed
    if report['failed_checks'] > 0:
        print("\nFailed checks:")
        for check_name, result in results.items():
            if not result["passed"]:
                print(f"  - {check_name}: {result.get('error', 'Check failed')}")
        sys.exit(1)
    
    print("All compliance checks passed!")

if __name__ == "__main__":
    main()
```

## Lab Exercises

### Exercise 1: Complete DevOps Pipeline
Xây dựng complete DevOps pipeline với:
- Infrastructure as Code (Terraform)
- Configuration Management (Ansible)
- CI/CD automation
- Monitoring và logging
- Security scanning
- Compliance validation

### Exercise 2: Multi-Environment Management
Triển khai infrastructure cho multiple environments:
- Development, Staging, Production
- Environment-specific configurations
- Promotion workflows
- Blue-green deployments

### Exercise 3: Disaster Recovery Automation
Implement DR automation:
- Automated backups
- Cross-region replication
- Failover procedures
- Recovery testing

### Exercise 4: Cost Optimization
Develop cost optimization automation:
- Resource tagging
- Usage monitoring
- Automated scaling
- Cost alerting

## 📚 Additional Resources
- [GitOps Principles](https://www.gitops.tech/)
- [Infrastructure Testing](https://infrastructure-as-code.com/book/2021/01/02/testing-infra.html)
- [DevOps Handbook](https://itrevolution.com/the-devops-handbook/)
- [Site Reliability Engineering](https://sre.google/books/)

---
*Chú thích: Integration labs này cho phép học viên áp dụng kiến thức về automation trong môi trường thực tế hoàn chỉnh.*
