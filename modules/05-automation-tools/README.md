# Module 5: Công cụ Tự động hóa (Ansible, Terraform)

## 🎯 Mục tiêu Module
Thành thạo Infrastructure as Code (IaC) và Configuration Management, tối ưu hóa quy trình triển khai và quản lý hạ tầng tại Viettel IDC.

## 📋 Nội dung Chính

### Ansible (60% trọng số)
#### 1. Ansible Fundamentals
- **Architecture**: control node, managed nodes, inventory
- **Installation**: pip, package managers, từ source
- **Configuration**: ansible.cfg, SSH key setup
- **Ad-hoc commands**: module usage, parallel execution

#### 2. Playbooks & Roles
- **Playbook structure**: YAML syntax, tasks, handlers
- **Variables**: group_vars, host_vars, vault encryption
- **Templates**: Jinja2 templating engine
- **Roles**: structure, dependencies, Galaxy

#### 3. Advanced Features
- **Dynamic inventory**: cloud providers, scripts
- **Custom modules**: Python development
- **Error handling**: failed_when, changed_when, ignore_errors
- **Testing**: molecule, ansible-lint

#### 4. Enterprise Patterns
- **AWX/Tower**: web interface, job templates
- **CI/CD integration**: GitLab, Jenkins pipelines
- **Security**: vault, become, privilege escalation
- **Performance**: forks, serial, async actions

### Terraform (40% trọng số)
#### 1. Infrastructure as Code
- **HCL syntax**: resources, variables, outputs
- **Providers**: AWS, Azure, VMware, OpenStack
- **State management**: remote backends, locking
- **Modules**: reusable infrastructure components

#### 2. Advanced Terraform
- **Workspaces**: environment separation
- **Data sources**: existing infrastructure integration
- **Provisioners**: local-exec, remote-exec, file
- **Import**: existing resources management

#### 3. Enterprise Features
- **Terraform Cloud**: remote state, collaboration
- **Sentinel**: policy as code
- **Version control**: Git workflows
- **CI/CD**: automated planning và applying

## 🛠️ Kỹ năng Thực hành

### Ansible Labs

#### 1. Basic Playbook Structure
```yaml
# site.yml
---
- name: Configure web servers
  hosts: webservers
  become: yes
  vars:
    http_port: 80
    max_clients: 200
  
  tasks:
    - name: Install Apache
      package:
        name: "{{ 'httpd' if ansible_os_family == 'RedHat' else 'apache2' }}"
        state: present
    
    - name: Start Apache service
      service:
        name: "{{ 'httpd' if ansible_os_family == 'RedHat' else 'apache2' }}"
        state: started
        enabled: yes
    
    - name: Configure Apache
      template:
        src: httpd.conf.j2
        dest: /etc/httpd/conf/httpd.conf
      notify: restart apache
  
  handlers:
    - name: restart apache
      service:
        name: "{{ 'httpd' if ansible_os_family == 'RedHat' else 'apache2' }}"
        state: restarted
```

#### 2. Role Structure
```bash
# Create role structure
ansible-galaxy init webserver

# roles/webserver/tasks/main.yml
---
- name: Install web server packages
  package:
    name: "{{ item }}"
    state: present
  loop: "{{ webserver_packages }}"

- name: Deploy application
  template:
    src: "{{ item.src }}"
    dest: "{{ item.dest }}"
    owner: "{{ webserver_user }}"
    group: "{{ webserver_group }}"
    mode: "{{ item.mode }}"
  loop: "{{ webserver_templates }}"
  notify: restart webserver

# roles/webserver/defaults/main.yml
---
webserver_packages:
  - nginx
  - php-fpm
webserver_user: www-data
webserver_group: www-data
```

#### 3. Advanced Inventory
```yaml
# inventory/group_vars/all.yml
---
ansible_user: centos
ansible_ssh_private_key_file: ~/.ssh/id_rsa

# Common variables
ntp_servers:
  - 0.pool.ntp.org
  - 1.pool.ntp.org

# inventory/group_vars/webservers.yml
---
apache_listen_port: 80
apache_document_root: /var/www/html

# inventory/host_vars/web01.yml
---
ansible_host: 192.168.1.10
server_role: primary

# Dynamic inventory script (AWS EC2)
#!/usr/bin/env python3
import boto3
import json

def get_inventory():
    ec2 = boto3.client('ec2')
    instances = ec2.describe_instances()
    
    inventory = {
        '_meta': {'hostvars': {}},
        'webservers': {'hosts': []},
        'databases': {'hosts': []}
    }
    
    for reservation in instances['Reservations']:
        for instance in reservation['Instances']:
            if instance['State']['Name'] == 'running':
                tags = {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
                if 'web' in tags.get('Role', ''):
                    inventory['webservers']['hosts'].append(instance['PrivateIpAddress'])
    
    return inventory

if __name__ == '__main__':
    print(json.dumps(get_inventory()))
```

#### 4. Complex Playbook Example
```yaml
# deploy-application.yml
---
- name: Deploy Application Infrastructure
  hosts: localhost
  gather_facts: no
  tasks:
    - name: Create AWS resources
      cloudformation:
        stack_name: "app-infrastructure"
        state: present
        template_body: "{{ lookup('file', 'templates/infrastructure.yml') }}"
        template_parameters:
          Environment: "{{ env }}"
          InstanceType: "{{ instance_type }}"

- name: Configure Application Servers
  hosts: tag_Role_webserver
  become: yes
  roles:
    - common
    - webserver
    - application
  
  pre_tasks:
    - name: Update system packages
      package:
        name: "*"
        state: latest
      when: ansible_os_family == "RedHat"
  
  post_tasks:
    - name: Verify application is running
      uri:
        url: "http://{{ ansible_default_ipv4.address }}:{{ app_port }}/health"
        method: GET
        status_code: 200
      retries: 5
      delay: 10
```

### Terraform Labs

#### 1. Basic Infrastructure
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
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"
}

# VPC
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = {
    Name        = "${var.environment}-vpc"
    Environment = var.environment
  }
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
  
  tags = {
    Name        = "${var.environment}-igw"
    Environment = var.environment
  }
}

# Subnets
resource "aws_subnet" "public" {
  count             = 2
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.${count.index + 1}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]
  
  map_public_ip_on_launch = true
  
  tags = {
    Name        = "${var.environment}-public-${count.index + 1}"
    Environment = var.environment
    Type        = "Public"
  }
}

# Security Group
resource "aws_security_group" "web" {
  name_prefix = "${var.environment}-web"
  vpc_id      = aws_vpc.main.id
  
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
  
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = {
    Name        = "${var.environment}-web-sg"
    Environment = var.environment
  }
}

# EC2 Instances
resource "aws_instance" "web" {
  count                  = 2
  ami                    = data.aws_ami.amazon_linux.id
  instance_type          = var.instance_type
  subnet_id              = aws_subnet.public[count.index].id
  vpc_security_group_ids = [aws_security_group.web.id]
  key_name               = aws_key_pair.main.key_name
  
  user_data = base64encode(templatefile("${path.module}/userdata.sh", {
    environment = var.environment
  }))
  
  tags = {
    Name        = "${var.environment}-web-${count.index + 1}"
    Environment = var.environment
    Role        = "webserver"
  }
}

# outputs.tf
output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "Public subnet IDs"
  value       = aws_subnet.public[*].id
}

output "web_instance_ips" {
  description = "Web server public IPs"
  value       = aws_instance.web[*].public_ip
}

# data.tf
data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]
  
  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
}
```

#### 2. Terraform Modules
```hcl
# modules/vpc/main.tf
resource "aws_vpc" "main" {
  cidr_block           = var.cidr_block
  enable_dns_hostnames = var.enable_dns_hostnames
  enable_dns_support   = var.enable_dns_support
  
  tags = merge(var.tags, {
    Name = "${var.name}-vpc"
  })
}

resource "aws_subnet" "public" {
  count             = length(var.public_subnets)
  vpc_id            = aws_vpc.main.id
  cidr_block        = var.public_subnets[count.index]
  availability_zone = var.availability_zones[count.index]
  
  map_public_ip_on_launch = true
  
  tags = merge(var.tags, {
    Name = "${var.name}-public-${count.index + 1}"
    Type = "Public"
  })
}

# modules/vpc/variables.tf
variable "name" {
  description = "Name prefix for resources"
  type        = string
}

variable "cidr_block" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnets" {
  description = "List of public subnet CIDR blocks"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "availability_zones" {
  description = "List of availability zones"
  type        = list(string)
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}

# modules/vpc/outputs.tf
output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "Public subnet IDs"
  value       = aws_subnet.public[*].id
}

# Root module usage
module "vpc" {
  source = "./modules/vpc"
  
  name               = var.environment
  availability_zones = data.aws_availability_zones.available.names
  
  tags = {
    Environment = var.environment
    Project     = "viettel-idc"
  }
}
```

## 📚 Tài liệu Tham khảo

### Ansible
- Ansible Official Documentation
- Ansible: Up and Running
- Ansible Best Practices Guide

### Terraform
- Terraform Official Documentation
- Terraform: Up & Running
- Infrastructure as Code Patterns

## 🎓 Chứng chỉ Liên quan
- **Ansible**: Red Hat Certified Specialist in Ansible Automation
- **Terraform**: HashiCorp Certified: Terraform Associate

## ⏱️ Thời gian Học: 2-3 tuần
- Tuần 1: Ansible fundamentals + playbooks
- Tuần 2: Terraform basics + IaC principles
- Tuần 3: Advanced automation + integration

## 🔗 Chuyển sang Module tiếp theo
Với kiến thức automation, bạn sẵn sàng cho **Module 6: Programming Languages**.
