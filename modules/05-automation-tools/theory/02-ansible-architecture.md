# Ansible Architecture và Fundamentals

## 🎯 Mục tiêu Học tập
- Hiểu rõ kiến trúc và các thành phần cốt lõi của Ansible
- Nắm vững cách thức hoạt động của Ansible
- Thành thạo cài đặt và cấu hình Ansible

## 1. Ansible Architecture Overview

### 1.1 Kiến trúc Tổng quan

```
┌─────────────────┐    SSH/WinRM    ┌──────────────────┐
│  Control Node   │ ──────────────► │  Managed Nodes   │
│                 │                 │                  │
│ ┌─────────────┐ │                 │ ┌──────────────┐ │
│ │  Ansible    │ │                 │ │    Python    │ │
│ │  Playbooks  │ │                 │ │   Modules    │ │
│ │             │ │                 │ │              │ │
│ └─────────────┘ │                 │ └──────────────┘ │
│ ┌─────────────┐ │                 │                  │
│ │ Inventory   │ │                 │                  │
│ │   Files     │ │                 │                  │
│ └─────────────┘ │                 │                  │
└─────────────────┘                 └──────────────────┘
```

### 1.2 Core Components (Thành phần Cốt lõi)

#### Control Node (Node Điều khiển)
- **Vai trò**: Máy chủ từ đó chạy Ansible commands và playbooks
- **Yêu cầu**: 
  - Python 3.8+ (recommended)
  - SSH client
  - Không thể là Windows (chỉ Linux/macOS)

#### Managed Nodes (Node được Quản lý)
- **Vai trò**: Servers được quản lý bởi Ansible
- **Yêu cầu**:
  - SSH server (Linux/Unix)
  - WinRM (Windows)
  - Python 2.7+ hoặc Python 3.5+

#### Inventory (Danh sách Máy chủ)
- **Mục đích**: Định nghĩa managed nodes và grouping
- **Formats**: INI, YAML, dynamic scripts
- **Location**: `/etc/ansible/hosts` (default)

#### Modules (Modules)
- **Định nghĩa**: Units của code được execute trên managed nodes
- **Types**: Core modules, extras modules, custom modules
- **Languages**: Chủ yếu Python, có thể viết bằng bất kỳ ngôn ngữ nào

#### Playbooks (Sách hướng dẫn)
- **Format**: YAML files
- **Contents**: Tasks, handlers, variables, templates
- **Purpose**: Define automation workflows

#### Plugins
- **Action Plugins**: Control execution flow
- **Cache Plugins**: Store gathered facts
- **Callback Plugins**: Control output và logging
- **Connection Plugins**: Connect to managed nodes

## 2. Ansible Execution Flow

### 2.1 Command Execution Process

```
1. User runs ansible command/playbook
        ↓
2. Ansible reads inventory và configuration
        ↓
3. Ansible connects to managed nodes (SSH/WinRM)
        ↓
4. Ansible transfers module code to nodes
        ↓
5. Module executes on managed nodes
        ↓
6. Results returned to control node
        ↓
7. Ansible processes và displays results
```

### 2.2 Module Execution Details

#### Standard Module Execution
```python
# Module được transfer như Python script
#!/usr/bin/python3

# Module code here
def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(required=True),
            state=dict(default='present', choices=['present', 'absent'])
        )
    )
    
    # Module logic here
    result = dict(changed=False, msg='')
    
    module.exit_json(**result)

if __name__ == '__main__':
    main()
```

#### Raw Module Execution
```bash
# Raw commands execute directly
ansible servers -m raw -a "uptime"
# No Python required on managed nodes
```

## 3. Installation và Setup

### 3.1 Control Node Installation

#### Using Package Manager (Recommended)
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install ansible

# CentOS/RHEL/Fedora
sudo dnf install ansible
# hoặc
sudo yum install ansible

# macOS
brew install ansible
```

#### Using pip (Python Package Manager)
```bash
# Install latest version
pip install ansible

# Install specific version
pip install ansible==6.7.0

# Install with additional collections
pip install ansible[azure,aws,gcp]

# Virtual environment (recommended)
python3 -m venv ansible-env
source ansible-env/bin/activate
pip install ansible
```

#### From Source (Development)
```bash
git clone https://github.com/ansible/ansible.git
cd ansible
source ./hacking/env-setup
sudo make install
```

### 3.2 Configuration Files

#### Primary Configuration File
```ini
# /etc/ansible/ansible.cfg hoặc ~/.ansible.cfg
[defaults]
# Inventory file location
inventory = ./inventory

# SSH settings
host_key_checking = False
timeout = 30
ansible_ssh_common_args = -o ControlMaster=auto -o ControlPersist=300s

# Privilege escalation
become = True
become_method = sudo
become_user = root
become_ask_pass = False

# Performance tuning
forks = 20
gathering = smart
fact_caching = memory
fact_caching_timeout = 86400

# Logging
log_path = /var/log/ansible.log
display_skipped_hosts = False
display_ok_hosts = False

[inventory]
# Enable advanced inventory features
enable_plugins = host_list, script, auto, yaml, ini, toml

[ssh_connection]
# SSH optimization
pipelining = True
ssh_args = -o ControlMaster=auto -o ControlPersist=300s -o PreferredAuthentications=publickey
control_path_dir = ~/.ansible/cp
retries = 3
```

#### Configuration Precedence (Thứ tự Ưu tiên)
1. Environment variables (`ANSIBLE_*`)
2. Command line options
3. Current directory `ansible.cfg`
4. Home directory `~/.ansible.cfg`
5. System-wide `/etc/ansible/ansible.cfg`

### 3.3 SSH Key Setup

#### Generate SSH Key Pair
```bash
# Generate new SSH key
ssh-keygen -t ed25519 -C "ansible-control@company.com"

# Copy public key to managed nodes
ssh-copy-id -i ~/.ssh/id_ed25519.pub user@managed-node

# Test connection
ssh -i ~/.ssh/id_ed25519 user@managed-node
```

#### SSH Agent Configuration
```bash
# Start SSH agent
eval $(ssh-agent -s)

# Add private key to agent
ssh-add ~/.ssh/id_ed25519

# Verify keys loaded
ssh-add -l
```

#### Advanced SSH Configuration
```bash
# ~/.ssh/config
Host ansible-managed-*
    User ansible
    IdentityFile ~/.ssh/ansible_key
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
    ControlMaster auto
    ControlPath ~/.ssh/cp/%h-%p-%r
    ControlPersist 300

Host prod-servers
    User root
    IdentityFile ~/.ssh/prod_key
    ProxyJump jump-server.company.com
```

## 4. Inventory Management

### 4.1 Static Inventory Formats

#### INI Format
```ini
# inventory/hosts
[webservers]
web01.example.com ansible_host=192.168.1.10
web02.example.com ansible_host=192.168.1.11

[databases]
db01.example.com ansible_host=192.168.1.20
db02.example.com ansible_host=192.168.1.21

[loadbalancers]
lb01.example.com ansible_host=192.168.1.30

# Group of groups
[production:children]
webservers
databases
loadbalancers

# Group variables
[webservers:vars]
http_port=80
https_port=443
ansible_user=webadmin

[databases:vars]
db_port=5432
ansible_user=dbadmin
```

#### YAML Format
```yaml
# inventory/hosts.yml
all:
  children:
    webservers:
      hosts:
        web01.example.com:
          ansible_host: 192.168.1.10
          server_role: primary
        web02.example.com:
          ansible_host: 192.168.1.11
          server_role: secondary
      vars:
        http_port: 80
        https_port: 443
        ansible_user: webadmin
    
    databases:
      hosts:
        db01.example.com:
          ansible_host: 192.168.1.20
          db_role: master
        db02.example.com:
          ansible_host: 192.168.1.21
          db_role: slave
      vars:
        db_port: 5432
        ansible_user: dbadmin
    
    production:
      children:
        webservers:
        databases:
        loadbalancers:
```

### 4.2 Dynamic Inventory

#### AWS EC2 Dynamic Inventory
```python
#!/usr/bin/env python3
# inventory/ec2.py
import boto3
import json
import sys

def get_inventory():
    ec2 = boto3.client('ec2', region_name='us-west-2')
    
    inventory = {
        '_meta': {
            'hostvars': {}
        }
    }
    
    # Get all running instances
    reservations = ec2.describe_instances(
        Filters=[
            {'Name': 'instance-state-name', 'Values': ['running']}
        ]
    )
    
    for reservation in reservations['Reservations']:
        for instance in reservation['Instances']:
            # Get instance tags
            tags = {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
            instance_name = tags.get('Name', instance['InstanceId'])
            
            # Group by environment
            environment = tags.get('Environment', 'untagged')
            if environment not in inventory:
                inventory[environment] = {'hosts': []}
            inventory[environment]['hosts'].append(instance_name)
            
            # Group by role
            role = tags.get('Role', 'untagged')
            if role not in inventory:
                inventory[role] = {'hosts': []}
            inventory[role]['hosts'].append(instance_name)
            
            # Host variables
            inventory['_meta']['hostvars'][instance_name] = {
                'ansible_host': instance.get('PublicIpAddress', instance.get('PrivateIpAddress')),
                'instance_id': instance['InstanceId'],
                'instance_type': instance['InstanceType'],
                'availability_zone': instance['Placement']['AvailabilityZone'],
                'tags': tags
            }
    
    return inventory

if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == '--list':
        print(json.dumps(get_inventory(), indent=2))
    elif len(sys.argv) == 3 and sys.argv[1] == '--host':
        print(json.dumps({}))
    else:
        print("Usage: {} --list or {} --host <hostname>".format(sys.argv[0], sys.argv[0]))
```

#### Inventory Plugin Configuration
```yaml
# inventory/aws_ec2.yml
plugin: amazon.aws.aws_ec2
regions:
  - us-east-1
  - us-west-2
keyed_groups:
  - prefix: arch
    key: architecture
  - prefix: instance_type
    key: instance_type
  - prefix: tag
    key: tags
hostnames:
  - network-interface.association.public-ip
  - dns-name
  - name
filters:
  instance-state-name: running
```

### 4.3 Inventory Testing và Validation

```bash
# List all hosts
ansible-inventory --list

# List specific group
ansible-inventory --list webservers

# Get host details
ansible-inventory --host web01.example.com

# Validate inventory syntax
ansible-inventory --list --check

# Test connectivity
ansible all -m ping

# Test with specific inventory
ansible -i inventory/production all -m ping
```

## 5. Ad-hoc Commands

### 5.1 Basic Command Structure
```bash
ansible <pattern> -m <module> -a "<arguments>" [options]
```

### 5.2 Common Ad-hoc Examples

#### System Information
```bash
# Check uptime
ansible all -m command -a "uptime"

# Get disk usage
ansible all -m shell -a "df -h"

# Check memory usage
ansible all -m shell -a "free -m"

# Get OS information
ansible all -m setup -a "filter=ansible_distribution*"

# Check service status
ansible webservers -m service -a "name=nginx state=started"
```

#### File Operations
```bash
# Copy file
ansible all -m copy -a "src=/local/file dest=/remote/file mode=644"

# Create directory
ansible all -m file -a "path=/opt/app state=directory mode=755"

# Download file
ansible all -m get_url -a "url=https://example.com/file.tar.gz dest=/tmp/"

# Change ownership
ansible all -m file -a "path=/opt/app owner=app group=app recurse=yes"
```

#### Package Management
```bash
# Install package
ansible all -m package -a "name=nginx state=present"

# Update all packages
ansible all -m package -a "name=* state=latest"

# Remove package
ansible all -m package -a "name=apache2 state=absent"

# Install from specific repository
ansible all -m yum -a "name=docker-ce enablerepo=docker-ce-stable"
```

#### User Management
```bash
# Create user
ansible all -m user -a "name=deploy shell=/bin/bash groups=wheel"

# Set password
ansible all -m user -a "name=deploy password={{ 'password123' | password_hash('sha512') }}"

# Add SSH key
ansible all -m authorized_key -a "user=deploy key='{{ lookup('file', '~/.ssh/id_rsa.pub') }}'"
```

## 6. Facts và Variables

### 6.1 Gathering Facts
```bash
# Gather all facts
ansible hostname -m setup

# Filter specific facts
ansible hostname -m setup -a "filter=ansible_mem*"

# Disable fact gathering
ansible hostname -m ping --gather-facts=no
```

### 6.2 Custom Facts
```bash
# Create custom fact directory
ansible all -m file -a "path=/etc/ansible/facts.d state=directory"

# Deploy custom fact
ansible all -m copy -a "src=custom.fact dest=/etc/ansible/facts.d/custom.fact mode=755"
```

```json
// custom.fact (JSON format)
{
    "application": {
        "name": "webapp",
        "version": "1.2.3",
        "environment": "production"
    }
}
```

```ini
# custom.fact (INI format)
[application]
name=webapp
version=1.2.3
environment=production
```

## 7. Ansible Modules Deep Dive

### 7.1 Module Categories

#### System Modules
- `service`: Manage services
- `user`: Manage users
- `group`: Manage groups
- `cron`: Manage cron jobs
- `mount`: Manage filesystems

#### File Modules
- `copy`: Copy files
- `template`: Template files
- `file`: Manage files và directories
- `lineinfile`: Manage lines in files
- `replace`: Replace text in files

#### Package Modules
- `package`: Generic package manager
- `yum`: Red Hat family
- `apt`: Debian family
- `pip`: Python packages

#### Network Modules
- `uri`: HTTP requests
- `get_url`: Download files
- `firewalld`: Manage firewall

### 7.2 Module Development

#### Simple Custom Module
```python
#!/usr/bin/python3
# library/custom_service.py

from ansible.module_utils.basic import AnsibleModule
import subprocess

def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(required=True, type='str'),
            state=dict(default='started', choices=['started', 'stopped', 'restarted']),
            enabled=dict(default=True, type='bool')
        ),
        supports_check_mode=True
    )
    
    service_name = module.params['name']
    desired_state = module.params['state']
    enabled = module.params['enabled']
    
    result = dict(
        changed=False,
        name=service_name,
        state=desired_state
    )
    
    if module.check_mode:
        module.exit_json(**result)
    
    # Implementation logic here
    try:
        if desired_state == 'started':
            subprocess.run(['systemctl', 'start', service_name], check=True)
            result['changed'] = True
        elif desired_state == 'stopped':
            subprocess.run(['systemctl', 'stop', service_name], check=True)
            result['changed'] = True
    except subprocess.CalledProcessError as e:
        module.fail_json(msg=f"Failed to manage service {service_name}: {str(e)}")
    
    module.exit_json(**result)

if __name__ == '__main__':
    main()
```

## 8. Performance Tuning

### 8.1 Ansible Configuration Optimization
```ini
[defaults]
# Increase parallel execution
forks = 50

# Enable pipelining
pipelining = True

# Optimize fact gathering
gathering = smart
fact_caching = memory
fact_caching_timeout = 86400

# SSH optimization
host_key_checking = False
ssh_args = -o ControlMaster=auto -o ControlPersist=300s

[ssh_connection]
# Enable pipelining
pipelining = True

# Control path for connection sharing
control_path_dir = ~/.ansible/cp
```

### 8.2 Playbook Optimization

#### Efficient Task Writing
```yaml
# Bad: Sequential execution
- name: Install packages individually
  package:
    name: "{{ item }}"
    state: present
  loop:
    - nginx
    - mysql
    - php

# Good: Batch execution
- name: Install packages in batch
  package:
    name:
      - nginx
      - mysql
      - php
    state: present
```

#### Strategic Fact Gathering
```yaml
---
- name: Optimized playbook
  hosts: all
  gather_facts: no  # Disable automatic fact gathering
  
  tasks:
    - name: Gather minimal facts
      setup:
        filter: 
          - 'ansible_distribution*'
          - 'ansible_os_family'
      when: ansible_facts is not defined
```

## 📚 Tài liệu Tham khảo
- [Ansible Official Documentation](https://docs.ansible.com/)
- [Ansible Best Practices](https://docs.ansible.com/ansible/latest/user_guide/playbooks_best_practices.html)
- [Ansible Module Development](https://docs.ansible.com/ansible/latest/dev_guide/developing_modules.html)

## 🔍 Câu hỏi Ôn tập
1. Giải thích kiến trúc agentless của Ansible và ưu/nhược điểm?
2. Sự khác biệt giữa `command` và `shell` module?
3. Làm thế nào để tối ưu hóa performance của Ansible?
4. Khi nào nên sử dụng dynamic inventory?
5. Cách debug và troubleshoot Ansible execution?

---
*Chú thích: Hiểu rõ architecture và fundamentals là nền tảng quan trọng để thành thạo Ansible trong các use case phức tạp.*
