# Automation Fundamentals - Lý thuyết Cơ bản về Tự động hóa

## 🎯 Mục tiêu Học tập
- Hiểu rõ các khái niệm cơ bản về tự động hóa hạ tầng
- Nắm vững Infrastructure as Code (IaC) và Configuration Management
- Phân biệt được các loại automation tools và ứng dụng

## 1. Tổng quan về Infrastructure Automation

### 1.1 Khái niệm Infrastructure as Code (IaC)
Infrastructure as Code là phương pháp quản lý và cung cấp hạ tầng thông qua các file định nghĩa có thể đọc được bởi máy, thay vì cấu hình thủ công hoặc các công cụ tương tác.

#### Nguyên tắc cốt lõi của IaC:
1. **Declarative vs Imperative**
   - **Declarative**: Định nghĩa trạng thái mong muốn của hệ thống
   - **Imperative**: Định nghĩa các bước để đạt được trạng thái đó

2. **Idempotency**
   - Thực hiện nhiều lần cùng một thao tác sẽ cho cùng một kết quả
   - Không gây ra thay đổi ngoài ý muốn

3. **Version Control**
   - Tất cả infrastructure code được lưu trữ trong version control
   - Có thể tracking, rollback và collaboration

#### Lợi ích của IaC:
- **Consistency (Tính nhất quán)**: Loại bỏ sai sót do cấu hình thủ công
- **Reproducibility (Tái tạo được)**: Có thể tạo lại môi trường giống hệt nhau
- **Scalability (Khả năng mở rộng)**: Dễ dàng mở rộng và quản lý nhiều môi trường
- **Documentation (Tài liệu hóa)**: Code chính là tài liệu về hạ tầng

### 1.2 Configuration Management vs Provisioning

#### Configuration Management (Quản lý Cấu hình)
- **Mục đích**: Quản lý và duy trì cấu hình của các server đã tồn tại
- **Công cụ**: Ansible, Chef, Puppet, SaltStack
- **Đặc điểm**: 
  - Mutable infrastructure (có thể thay đổi)
  - Focus on maintaining desired state
  - Good for complex configuration management

#### Infrastructure Provisioning (Cung cấp Hạ tầng)
- **Mục đích**: Tạo mới và quản lý lifecycle của infrastructure resources
- **Công cụ**: Terraform, CloudFormation, Azure ARM Templates
- **Đặc điểm**:
  - Immutable infrastructure (không thay đổi)
  - Focus on resource creation and management
  - Infrastructure lifecycle management

### 1.3 Push vs Pull Models

#### Push Model (Ansible)
```
Control Node ----push----> Managed Nodes
     |                           |
   Playbooks              Execute tasks
```

**Ưu điểm:**
- Immediate execution
- No agents required
- Simple architecture
- Better for ad-hoc tasks

**Nhược điểm:**
- Network dependency
- Limited scalability for large environments
- No automatic remediation

#### Pull Model (Puppet, Chef)
```
Managed Nodes ----pull----> Configuration Server
     |                           |
   Agents                   Configurations
```

**Ưu điểm:**
- Better scalability
- Automatic remediation
- Works with intermittent connectivity
- Distributed execution

**Nhược điểm:**
- Agent management overhead
- More complex architecture
- Delayed configuration updates

## 2. Automation Strategy và Best Practices

### 2.1 Automation Maturity Model

#### Level 0: Manual Processes
- Tất cả các task được thực hiện thủ công
- High error rate và inconsistency
- Slow deployment cycles

#### Level 1: Script-based Automation
- Basic shell scripts cho repetitive tasks
- Improved consistency nhưng vẫn có limitations
- Limited error handling

#### Level 2: Tool-based Automation
- Sử dụng automation tools như Ansible, Terraform
- Standardized approaches
- Better error handling và logging

#### Level 3: Pipeline Automation
- Full CI/CD pipeline integration
- Automated testing và validation
- Infrastructure và application deployment

#### Level 4: Self-healing Systems
- Automated monitoring và remediation
- Predictive automation
- Machine learning-driven optimizations

### 2.2 Automation Design Principles

#### 1. Start Small, Think Big
```yaml
# Bad: Trying to automate everything at once
- name: Automate entire datacenter
  tasks:
    - include: networking.yml
    - include: storage.yml
    - include: compute.yml
    - include: applications.yml
    - include: monitoring.yml

# Good: Start with one component
- name: Automate web server deployment
  tasks:
    - name: Install nginx
      package:
        name: nginx
        state: present
```

#### 2. Fail Fast, Fail Safe
```yaml
# Good: Early validation
- name: Validate required variables
  assert:
    that:
      - app_name is defined
      - app_version is defined
      - target_environment in ['dev', 'staging', 'prod']
    fail_msg: "Required variables not properly defined"

- name: Check disk space before deployment
  shell: df -h {{ deploy_path }} | tail -1 | awk '{print $5}' | sed 's/%//'
  register: disk_usage
  failed_when: disk_usage.stdout|int > 80
```

#### 3. Make it Observable
```yaml
- name: Deploy application with logging
  copy:
    src: "{{ app_package }}"
    dest: "{{ deploy_path }}"
  register: deploy_result
  
- name: Log deployment status
  lineinfile:
    path: /var/log/deployments.log
    line: "{{ ansible_date_time.iso8601 }} - {{ app_name }} {{ app_version }} deployed to {{ target_environment }} - Status: {{ 'SUCCESS' if deploy_result.changed else 'UNCHANGED' }}"
```

### 2.3 Security trong Automation

#### Secret Management
```yaml
# Bad: Hardcoded secrets
- name: Connect to database
  mysql_user:
    name: app_user
    password: "supersecretpassword123"  # DON'T DO THIS!

# Good: Using Ansible Vault
- name: Connect to database
  mysql_user:
    name: app_user
    password: "{{ vault_db_password }}"

# Good: Using external secret management
- name: Get database password from AWS Secrets Manager
  set_fact:
    db_password: "{{ lookup('aws_secret', 'prod/database/password') }}"
```

#### Principle of Least Privilege
```yaml
# Good: Specific permissions
- name: Create service user
  user:
    name: "{{ service_name }}"
    shell: /sbin/nologin
    home: "{{ service_home }}"
    create_home: no
    system: yes

- name: Set specific file permissions
  file:
    path: "{{ item }}"
    owner: "{{ service_name }}"
    group: "{{ service_name }}"
    mode: '0644'
  loop:
    - "{{ config_file }}"
    - "{{ log_file }}"
```

## 3. Automation Testing và Validation

### 3.1 Testing Pyramid cho Infrastructure

```
    Unit Tests (Syntax, Lint)
         |
    Integration Tests (Modules)
         |
    System Tests (Full Infrastructure)
         |
    Acceptance Tests (End-to-end)
```

#### Unit Testing
```bash
# Ansible syntax check
ansible-playbook --syntax-check playbook.yml

# Ansible lint
ansible-lint playbook.yml

# Terraform syntax check
terraform validate

# Terraform security scan
tfsec .
```

#### Integration Testing
```yaml
# Test individual roles
- name: Test web server role
  hosts: test_servers
  roles:
    - webserver
  post_tasks:
    - name: Verify nginx is running
      service:
        name: nginx
        state: started
      check_mode: yes
      register: nginx_status
      failed_when: nginx_status.changed
```

### 3.2 Infrastructure Testing với Molecule

```yaml
# molecule/default/molecule.yml
---
dependency:
  name: galaxy
driver:
  name: docker
platforms:
  - name: instance
    image: centos:8
    pre_build_image: true
provisioner:
  name: ansible
verifier:
  name: ansible
```

```yaml
# molecule/default/verify.yml
---
- name: Verify
  hosts: all
  gather_facts: false
  tasks:
    - name: Example assertion
      assert:
        that:
          - true
```

## 4. Performance và Optimization

### 4.1 Ansible Performance Tuning

#### Parallel Execution
```ini
# ansible.cfg
[defaults]
forks = 50
host_key_checking = False
pipelining = True

[ssh_connection]
ssh_args = -o ControlMaster=auto -o ControlPersist=60s
control_path_dir = ~/.ansible/cp
```

#### Task Optimization
```yaml
# Bad: Sequential package installation
- name: Install packages
  package:
    name: "{{ item }}"
    state: present
  loop:
    - nginx
    - mysql
    - php

# Good: Batch package installation
- name: Install packages
  package:
    name:
      - nginx
      - mysql
      - php
    state: present
```

### 4.2 Terraform Performance

#### State Management
```hcl
# terraform.tf
terraform {
  backend "s3" {
    bucket         = "terraform-state-bucket"
    key            = "prod/infrastructure.tfstate"
    region         = "us-west-2"
    encrypt        = true
    dynamodb_table = "terraform-locks"
  }
}
```

#### Resource Targeting
```bash
# Deploy specific resources
terraform apply -target=aws_instance.web

# Parallel resource creation
terraform apply -parallelism=10
```

## 5. Monitoring và Observability

### 5.1 Automation Metrics

#### Key Performance Indicators (KPIs)
- **Deployment Frequency**: Số lần deploy trên một khoảng thời gian
- **Lead Time**: Thời gian từ commit đến production
- **Mean Time to Recovery (MTTR)**: Thời gian trung bình để recover từ failure
- **Change Failure Rate**: Tỷ lệ deployment gây ra failure

#### Monitoring Implementation
```yaml
- name: Record deployment metrics
  uri:
    url: "{{ metrics_endpoint }}"
    method: POST
    body_format: json
    body:
      timestamp: "{{ ansible_date_time.epoch }}"
      deployment_id: "{{ deployment_id }}"
      environment: "{{ target_environment }}"
      status: "{{ deployment_status }}"
      duration: "{{ deployment_duration }}"
```

### 5.2 Logging và Auditing

```yaml
- name: Configure audit logging
  lineinfile:
    path: /etc/audit/auditd.conf
    regexp: '^log_file'
    line: 'log_file = /var/log/audit/audit.log'
  notify: restart auditd

- name: Track configuration changes
  shell: |
    echo "{{ ansible_date_time.iso8601 }} - Configuration changed by {{ ansible_user_id }} on {{ inventory_hostname }}" 
    >> /var/log/config-changes.log
```

## 6. Disaster Recovery và Business Continuity

### 6.1 Backup Automation
```yaml
- name: Automated infrastructure backup
  cron:
    name: "Terraform state backup"
    minute: "0"
    hour: "2"
    job: "terraform-backup.sh"
    user: terraform

- name: Database backup automation
  cron:
    name: "Database backup"
    minute: "30"
    hour: "1"
    job: "pg_dump {{ db_name }} | gzip > /backups/{{ db_name }}_$(date +%Y%m%d).sql.gz"
```

### 6.2 Recovery Procedures
```yaml
- name: Infrastructure recovery playbook
  hosts: disaster_recovery
  tasks:
    - name: Restore from backup
      terraform:
        project_path: "{{ recovery_path }}"
        state: present
        variables:
          backup_source: "{{ backup_location }}"
          recovery_timestamp: "{{ recovery_point }}"
```

## 📚 Tài liệu Tham khảo
- [Infrastructure as Code Principles](https://infrastructure-as-code.com/)
- [Automation Best Practices](https://docs.ansible.com/ansible/latest/user_guide/playbooks_best_practices.html)
- [The Phoenix Project - DevOps Novel](https://itrevolution.com/the-phoenix-project/)
- [Site Reliability Engineering - Google](https://sre.google/books/)

## 🔍 Câu hỏi Ôn tập
1. Phân biệt giữa Configuration Management và Infrastructure Provisioning?
2. Khi nào nên sử dụng Push model và khi nào nên sử dụng Pull model?
3. Các nguyên tắc bảo mật quan trọng khi triển khai automation?
4. Làm thế nào để đo lường hiệu quả của automation strategy?
5. Strategies nào để handle failures trong automated processes?

---
*Chú thích: Nội dung này tập trung vào việc xây dựng nền tảng lý thuyết vững chắc về automation, chuẩn bị cho việc học sâu về Ansible và Terraform trong các phần tiếp theo.*
