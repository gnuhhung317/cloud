# Real-World Automation Projects

## 🎯 Project Overview
Đây là collection của các real-world automation projects được thiết kế để mô phỏng các scenarios thực tế trong enterprise environments, đặc biệt phù hợp với môi trường Viettel IDC.

## Project 1: Enterprise Multi-Tier Application Deployment

### 📋 Project Description
Triển khai complete 3-tier application với automated infrastructure provisioning, configuration management, và continuous deployment pipeline.

### 🏗️ Architecture Overview
```
Internet Gateway
    ↓
Application Load Balancer
    ↓
Web Tier (Auto Scaling Group)
    ↓
Application Tier (Private Subnets)
    ↓
Database Tier (RDS Multi-AZ)
```

### 🔧 Technical Requirements

#### Infrastructure Components
- **VPC**: Multi-AZ setup với public/private subnets
- **Security Groups**: Layered security model
- **Auto Scaling**: Dynamic scaling based on metrics
- **RDS**: Multi-AZ database với automated backups
- **CloudFront**: CDN for static content
- **Route 53**: DNS management

#### Application Stack
- **Frontend**: React.js application
- **Backend**: Node.js API server
- **Database**: PostgreSQL với replication
- **Cache**: Redis cluster
- **Monitoring**: Prometheus + Grafana
- **Logging**: ELK Stack

### 📁 Project Structure
```
project-enterprise-app/
├── terraform/
│   ├── environments/
│   │   ├── dev/
│   │   ├── staging/
│   │   └── prod/
│   ├── modules/
│   │   ├── vpc/
│   │   ├── security/
│   │   ├── compute/
│   │   ├── database/
│   │   └── monitoring/
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
├── ansible/
│   ├── inventories/
│   │   ├── dev/
│   │   ├── staging/
│   │   └── prod/
│   ├── playbooks/
│   │   ├── site.yml
│   │   ├── webservers.yml
│   │   ├── appservers.yml
│   │   └── monitoring.yml
│   ├── roles/
│   │   ├── common/
│   │   ├── nginx/
│   │   ├── nodejs/
│   │   ├── postgresql/
│   │   ├── redis/
│   │   └── monitoring/
│   └── group_vars/
├── docker/
│   ├── frontend/
│   ├── backend/
│   └── monitoring/
├── k8s/
│   ├── namespaces/
│   ├── deployments/
│   ├── services/
│   └── ingress/
├── scripts/
│   ├── deploy.sh
│   ├── rollback.sh
│   ├── backup.sh
│   └── monitoring.sh
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
└── docs/
    ├── architecture.md
    ├── deployment.md
    └── troubleshooting.md
```

### 🚀 Implementation Details

#### Terraform Modules

##### VPC Module
```hcl
# terraform/modules/vpc/main.tf
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = merge(var.common_tags, {
    Name = "${var.project_name}-vpc"
  })
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = merge(var.common_tags, {
    Name = "${var.project_name}-igw"
  })
}

resource "aws_nat_gateway" "main" {
  count = length(var.availability_zones)

  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[count.index].id

  tags = merge(var.common_tags, {
    Name = "${var.project_name}-nat-${var.availability_zones[count.index]}"
  })

  depends_on = [aws_internet_gateway.main]
}

resource "aws_eip" "nat" {
  count = length(var.availability_zones)

  domain = "vpc"

  tags = merge(var.common_tags, {
    Name = "${var.project_name}-eip-${var.availability_zones[count.index]}"
  })
}

# Public Subnets
resource "aws_subnet" "public" {
  count = length(var.availability_zones)

  vpc_id                  = aws_vpc.main.id
  cidr_block              = cidrsubnet(var.vpc_cidr, 8, count.index)
  availability_zone       = var.availability_zones[count.index]
  map_public_ip_on_launch = true

  tags = merge(var.common_tags, {
    Name = "${var.project_name}-public-${var.availability_zones[count.index]}"
    Type = "public"
  })
}

# Private Subnets for Application Tier
resource "aws_subnet" "private_app" {
  count = length(var.availability_zones)

  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index + 10)
  availability_zone = var.availability_zones[count.index]

  tags = merge(var.common_tags, {
    Name = "${var.project_name}-private-app-${var.availability_zones[count.index]}"
    Type = "private"
    Tier = "application"
  })
}

# Private Subnets for Database Tier
resource "aws_subnet" "private_db" {
  count = length(var.availability_zones)

  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index + 20)
  availability_zone = var.availability_zones[count.index]

  tags = merge(var.common_tags, {
    Name = "${var.project_name}-private-db-${var.availability_zones[count.index]}"
    Type = "private"
    Tier = "database"
  })
}

# Route Tables
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = merge(var.common_tags, {
    Name = "${var.project_name}-public-rt"
  })
}

resource "aws_route_table" "private" {
  count = length(var.availability_zones)

  vpc_id = aws_vpc.main.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.main[count.index].id
  }

  tags = merge(var.common_tags, {
    Name = "${var.project_name}-private-rt-${var.availability_zones[count.index]}"
  })
}

# Route Table Associations
resource "aws_route_table_association" "public" {
  count = length(var.availability_zones)

  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "private_app" {
  count = length(var.availability_zones)

  subnet_id      = aws_subnet.private_app[count.index].id
  route_table_id = aws_route_table.private[count.index].id
}

resource "aws_route_table_association" "private_db" {
  count = length(var.availability_zones)

  subnet_id      = aws_subnet.private_db[count.index].id
  route_table_id = aws_route_table.private[count.index].id
}
```

##### Compute Module with Auto Scaling
```hcl
# terraform/modules/compute/main.tf
# Launch Template for Web Servers
resource "aws_launch_template" "web" {
  name_prefix   = "${var.project_name}-web-"
  image_id      = data.aws_ami.amazon_linux.id
  instance_type = var.web_instance_type
  key_name      = var.key_name

  vpc_security_group_ids = [aws_security_group.web.id]

  user_data = base64encode(templatefile("${path.module}/templates/web_userdata.sh", {
    environment = var.environment
    project_name = var.project_name
  }))

  block_device_mappings {
    device_name = "/dev/xvda"
    ebs {
      volume_size = 20
      volume_type = "gp3"
      encrypted   = true
    }
  }

  monitoring {
    enabled = true
  }

  tag_specifications {
    resource_type = "instance"
    tags = merge(var.common_tags, {
      Name = "${var.project_name}-web"
      Tier = "web"
    })
  }

  lifecycle {
    create_before_destroy = true
  }
}

# Auto Scaling Group for Web Tier
resource "aws_autoscaling_group" "web" {
  name                = "${var.project_name}-web-asg"
  vpc_zone_identifier = var.public_subnet_ids
  target_group_arns   = [aws_lb_target_group.web.arn]
  health_check_type   = "ELB"
  health_check_grace_period = 300

  min_size         = var.web_min_size
  max_size         = var.web_max_size
  desired_capacity = var.web_desired_capacity

  launch_template {
    id      = aws_launch_template.web.id
    version = "$Latest"
  }

  enabled_metrics = [
    "GroupMinSize",
    "GroupMaxSize",
    "GroupDesiredCapacity",
    "GroupInServiceInstances",
    "GroupTotalInstances"
  ]

  tag {
    key                 = "Name"
    value               = "${var.project_name}-web-asg"
    propagate_at_launch = false
  }

  dynamic "tag" {
    for_each = var.common_tags
    content {
      key                 = tag.key
      value               = tag.value
      propagate_at_launch = true
    }
  }

  instance_refresh {
    strategy = "Rolling"
    preferences {
      min_healthy_percentage = 50
    }
  }
}

# Auto Scaling Policies
resource "aws_autoscaling_policy" "web_scale_up" {
  name                   = "${var.project_name}-web-scale-up"
  scaling_adjustment     = 1
  adjustment_type        = "ChangeInCapacity"
  cooldown               = 300
  autoscaling_group_name = aws_autoscaling_group.web.name
}

resource "aws_autoscaling_policy" "web_scale_down" {
  name                   = "${var.project_name}-web-scale-down"
  scaling_adjustment     = -1
  adjustment_type        = "ChangeInCapacity"
  cooldown               = 300
  autoscaling_group_name = aws_autoscaling_group.web.name
}

# CloudWatch Alarms
resource "aws_cloudwatch_metric_alarm" "web_cpu_high" {
  alarm_name          = "${var.project_name}-web-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = "120"
  statistic           = "Average"
  threshold           = "70"
  alarm_description   = "This metric monitors ec2 cpu utilization"
  alarm_actions       = [aws_autoscaling_policy.web_scale_up.arn]

  dimensions = {
    AutoScalingGroupName = aws_autoscaling_group.web.name
  }
}

resource "aws_cloudwatch_metric_alarm" "web_cpu_low" {
  alarm_name          = "${var.project_name}-web-cpu-low"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = "120"
  statistic           = "Average"
  threshold           = "30"
  alarm_description   = "This metric monitors ec2 cpu utilization"
  alarm_actions       = [aws_autoscaling_policy.web_scale_down.arn]

  dimensions = {
    AutoScalingGroupName = aws_autoscaling_group.web.name
  }
}

# Application Load Balancer
resource "aws_lb" "main" {
  name               = "${var.project_name}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = var.public_subnet_ids

  enable_deletion_protection = var.environment == "prod" ? true : false

  tags = var.common_tags
}

resource "aws_lb_target_group" "web" {
  name     = "${var.project_name}-web-tg"
  port     = 80
  protocol = "HTTP"
  vpc_id   = var.vpc_id

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

  tags = var.common_tags
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
```

#### Ansible Automation

##### Site Playbook
```yaml
# ansible/playbooks/site.yml
---
- name: Configure all servers
  hosts: all
  become: yes
  gather_facts: yes
  
  pre_tasks:
    - name: Wait for system to be ready
      wait_for_connection:
        delay: 10
        timeout: 300
    
    - name: Update package cache
      package:
        update_cache: yes
      when: ansible_os_family in ["Debian", "RedHat"]
  
  roles:
    - common

- name: Configure load balancers
  hosts: loadbalancers
  become: yes
  
  roles:
    - nginx
    - monitoring.node_exporter
  
  vars:
    nginx_sites:
      - name: "{{ project_name }}"
        server_name: "{{ ansible_default_ipv4.address }}"
        upstream_servers: "{{ groups['webservers'] }}"
        enable_ssl: "{{ ssl_enabled | default(false) }}"

- name: Configure web servers
  hosts: webservers
  become: yes
  
  roles:
    - nginx
    - nodejs
    - monitoring.node_exporter
  
  vars:
    nodejs_version: "16.x"
    nginx_sites:
      - name: frontend
        server_name: "{{ ansible_default_ipv4.address }}"
        document_root: /var/www/html
        proxy_pass: "http://127.0.0.1:3000"
        enable_ssl: false

- name: Configure application servers
  hosts: appservers
  become: yes
  
  roles:
    - nodejs
    - redis
    - monitoring.node_exporter
  
  vars:
    nodejs_version: "16.x"
    redis_bind: "127.0.0.1"
    redis_maxmemory: "512mb"
    redis_maxmemory_policy: "allkeys-lru"

- name: Configure database servers
  hosts: dbservers
  become: yes
  
  roles:
    - postgresql
    - monitoring.node_exporter
    - monitoring.postgres_exporter
  
  vars:
    postgresql_version: "13"
    postgresql_databases:
      - name: "{{ app_database_name }}"
        owner: "{{ app_database_user }}"
        encoding: "UTF8"
    postgresql_users:
      - name: "{{ app_database_user }}"
        password: "{{ app_database_password }}"
        privileges: "ALL"
        database: "{{ app_database_name }}"

- name: Configure monitoring servers
  hosts: monitoring
  become: yes
  
  roles:
    - prometheus
    - grafana
    - alertmanager
  
  vars:
    prometheus_targets:
      node:
        - targets: "{{ groups['all'] | map('extract', hostvars, 'ansible_default_ipv4') | map(attribute='address') | map('regex_replace', '^(.*)$', '\\1:9100') | list }}"
      postgres:
        - targets: "{{ groups['dbservers'] | map('extract', hostvars, 'ansible_default_ipv4') | map(attribute='address') | map('regex_replace', '^(.*)$', '\\1:9187') | list }}"
      nginx:
        - targets: "{{ groups['webservers'] | map('extract', hostvars, 'ansible_default_ipv4') | map(attribute='address') | map('regex_replace', '^(.*)$', '\\1:9113') | list }}"
```

##### Node.js Application Role
```yaml
# ansible/roles/nodejs/tasks/main.yml
---
- name: Install Node.js repository
  shell: curl -fsSL https://deb.nodesource.com/setup_{{ nodejs_version }}.sh | bash -
  when: ansible_os_family == "Debian"

- name: Install Node.js
  package:
    name: nodejs
    state: present

- name: Install PM2 globally
  npm:
    name: pm2
    global: yes
    state: present

- name: Create application user
  user:
    name: "{{ app_user }}"
    group: "{{ app_group }}"
    system: yes
    shell: /bin/bash
    home: "{{ app_home }}"
    create_home: yes

- name: Create application directories
  file:
    path: "{{ item }}"
    state: directory
    owner: "{{ app_user }}"
    group: "{{ app_group }}"
    mode: '0755'
  loop:
    - "{{ app_home }}/current"
    - "{{ app_home }}/shared"
    - "{{ app_home }}/shared/logs"
    - "{{ app_home }}/shared/config"

- name: Deploy application code
  synchronize:
    src: "{{ app_source_path }}/"
    dest: "{{ app_home }}/current/"
    delete: yes
    rsync_opts:
      - "--exclude=node_modules"
      - "--exclude=.git"
  become_user: "{{ app_user }}"
  notify: restart application

- name: Install application dependencies
  npm:
    path: "{{ app_home }}/current"
    state: present
  become_user: "{{ app_user }}"

- name: Generate application configuration
  template:
    src: "{{ item.src }}"
    dest: "{{ item.dest }}"
    owner: "{{ app_user }}"
    group: "{{ app_group }}"
    mode: '0640'
  loop:
    - src: app.env.j2
      dest: "{{ app_home }}/shared/config/.env"
    - src: ecosystem.config.js.j2
      dest: "{{ app_home }}/current/ecosystem.config.js"
  notify: restart application

- name: Start application with PM2
  shell: |
    cd {{ app_home }}/current
    pm2 start ecosystem.config.js --env {{ environment }}
    pm2 save
  become_user: "{{ app_user }}"
  environment:
    PM2_HOME: "{{ app_home }}/.pm2"

- name: Setup PM2 startup script
  shell: |
    env PATH=$PATH:/usr/bin pm2 startup systemd -u {{ app_user }} --hp {{ app_home }}
    systemctl enable pm2-{{ app_user }}
  when: ansible_service_mgr == "systemd"

- name: Configure log rotation
  template:
    src: app-logrotate.j2
    dest: /etc/logrotate.d/{{ app_user }}
    mode: '0644'

- name: Setup application monitoring
  template:
    src: app-health-check.sh.j2
    dest: "{{ app_home }}/shared/health-check.sh"
    owner: "{{ app_user }}"
    group: "{{ app_group }}"
    mode: '0755'

- name: Configure health check cron
  cron:
    name: "Application health check"
    minute: "*/5"
    job: "{{ app_home }}/shared/health-check.sh"
    user: "{{ app_user }}"
```

#### Continuous Integration Pipeline

##### GitHub Actions Workflow
```yaml
# .github/workflows/deploy.yml
name: 'Enterprise Application Deployment'

on:
  push:
    branches: [ main, develop, 'feature/*' ]
  pull_request:
    branches: [ main, develop ]

env:
  TF_VERSION: 1.5.0
  ANSIBLE_VERSION: 6.0.0
  NODE_VERSION: 18.x
  AWS_DEFAULT_REGION: us-west-2

jobs:
  # Test Application Code
  test-application:
    name: 'Test Application'
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout
      uses: actions/checkout@v3
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: ${{ env.NODE_VERSION }}
        cache: 'npm'
    
    - name: Install dependencies
      run: |
        cd app/frontend && npm ci
        cd ../backend && npm ci
    
    - name: Run frontend tests
      run: cd app/frontend && npm test
    
    - name: Run backend tests
      run: cd app/backend && npm test
    
    - name: Run integration tests
      run: |
        cd app
        docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit
        docker-compose -f docker-compose.test.yml down

  # Validate Infrastructure Code
  validate-infrastructure:
    name: 'Validate Infrastructure'
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
        pip install ansible-lint molecule docker
    
    - name: Terraform Format Check
      run: terraform fmt -check -recursive
      working-directory: terraform
    
    - name: Terraform Validate
      run: |
        for env in dev staging prod; do
          cd environments/$env
          terraform init -backend=false
          terraform validate
          cd ../..
        done
      working-directory: terraform
    
    - name: Ansible Syntax Check
      run: |
        ansible-playbook --syntax-check playbooks/site.yml
        ansible-lint playbooks/
      working-directory: ansible
    
    - name: Test Ansible Roles with Molecule
      run: |
        cd ansible/roles/nodejs
        molecule test
      continue-on-error: true

  # Security Scanning
  security-scan:
    name: 'Security Scan'
    runs-on: ubuntu-latest
    needs: [test-application, validate-infrastructure]
    
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
    
    - name: Run tfsec
      uses: aquasecurity/tfsec-action@v1.0.0
      with:
        working_directory: terraform
    
    - name: Run npm audit
      run: |
        cd app/frontend && npm audit --audit-level moderate
        cd ../backend && npm audit --audit-level moderate
      continue-on-error: true
    
    - name: Run Semgrep
      uses: returntocorp/semgrep-action@v1
      with:
        config: auto

  # Deploy to Development
  deploy-dev:
    name: 'Deploy to Development'
    runs-on: ubuntu-latest
    needs: [test-application, validate-infrastructure, security-scan]
    if: github.ref == 'refs/heads/develop'
    environment: development
    
    steps:
    - name: Checkout
      uses: actions/checkout@v3
    
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v2
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: ${{ env.AWS_DEFAULT_REGION }}
    
    - name: Setup deployment tools
      run: |
        # Install Terraform
        curl -LO https://releases.hashicorp.com/terraform/${{ env.TF_VERSION }}/terraform_${{ env.TF_VERSION }}_linux_amd64.zip
        unzip terraform_${{ env.TF_VERSION }}_linux_amd64.zip
        sudo mv terraform /usr/local/bin/
        
        # Install Ansible
        pip install ansible==${{ env.ANSIBLE_VERSION }} boto3 botocore
    
    - name: Deploy infrastructure
      run: |
        cd terraform/environments/dev
        terraform init
        terraform plan -out=tfplan
        terraform apply tfplan
        
        # Generate Ansible inventory
        terraform output -json > ../../../ansible/inventories/dev/terraform_outputs.json
      
    - name: Configure servers
      run: |
        cd ansible
        # Wait for instances to be ready
        sleep 120
        
        # Run Ansible playbook
        ansible-playbook -i inventories/dev/aws_ec2.yml playbooks/site.yml \
          --extra-vars "environment=dev" \
          --ssh-common-args='-o StrictHostKeyChecking=no'
    
    - name: Deploy application
      run: |
        cd ansible
        ansible-playbook -i inventories/dev/aws_ec2.yml playbooks/deploy-app.yml \
          --extra-vars "app_version=${{ github.sha }}" \
          --ssh-common-args='-o StrictHostKeyChecking=no'
    
    - name: Run smoke tests
      run: |
        cd tests
        python -m pytest smoke/ -v --junit-xml=smoke-results.xml
      continue-on-error: true
    
    - name: Upload test results
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: test-results
        path: tests/smoke-results.xml

  # Deploy to Production
  deploy-prod:
    name: 'Deploy to Production'
    runs-on: ubuntu-latest
    needs: [test-application, validate-infrastructure, security-scan]
    if: github.ref == 'refs/heads/main'
    environment: production
    
    steps:
    - name: Checkout
      uses: actions/checkout@v3
    
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v2
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID_PROD }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY_PROD }}
        aws-region: ${{ env.AWS_DEFAULT_REGION }}
    
    - name: Setup deployment tools
      run: |
        curl -LO https://releases.hashicorp.com/terraform/${{ env.TF_VERSION }}/terraform_${{ env.TF_VERSION }}_linux_amd64.zip
        unzip terraform_${{ env.TF_VERSION }}_linux_amd64.zip
        sudo mv terraform /usr/local/bin/
        pip install ansible==${{ env.ANSIBLE_VERSION }} boto3 botocore
    
    - name: Deploy infrastructure
      run: |
        cd terraform/environments/prod
        terraform init
        terraform plan -out=tfplan
        terraform apply tfplan
    
    - name: Blue-Green Deployment
      run: |
        cd scripts
        ./blue-green-deploy.sh --environment prod --version ${{ github.sha }}
    
    - name: Run production tests
      run: |
        cd tests
        python -m pytest production/ -v --junit-xml=prod-results.xml
    
    - name: Notify teams
      if: always()
      uses: 8398a7/action-slack@v3
      with:
        status: ${{ job.status }}
        channel: '#deployments'
        webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### 📊 Monitoring và Alerting

#### Prometheus Configuration
```yaml
# ansible/roles/prometheus/templates/prometheus.yml.j2
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "rules/*.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - localhost:9093

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'node-exporter'
    static_configs:
      - targets:
{% for host in groups['all'] %}
        - '{{ hostvars[host]['ansible_default_ipv4']['address'] }}:9100'
{% endfor %}

  - job_name: 'nginx-exporter'
    static_configs:
      - targets:
{% for host in groups['webservers'] %}
        - '{{ hostvars[host]['ansible_default_ipv4']['address'] }}:9113'
{% endfor %}

  - job_name: 'postgres-exporter'
    static_configs:
      - targets:
{% for host in groups['dbservers'] %}
        - '{{ hostvars[host]['ansible_default_ipv4']['address'] }}:9187'
{% endfor %}

  - job_name: 'application'
    static_configs:
      - targets:
{% for host in groups['appservers'] %}
        - '{{ hostvars[host]['ansible_default_ipv4']['address'] }}:3000'
{% endfor %}
    scrape_interval: 5s
    metrics_path: /metrics

  - job_name: 'aws-cloudwatch'
    ec2_sd_configs:
      - region: {{ aws_region }}
        port: 9100
        filters:
          - name: tag:Project
            values: 
              - {{ project_name }}
    relabel_configs:
      - source_labels: [__meta_ec2_tag_Name]
        target_label: instance
```

#### Grafana Dashboards
```json
{
  "dashboard": {
    "id": null,
    "title": "Enterprise Application Dashboard",
    "tags": ["enterprise", "application"],
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "Application Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          },
          {
            "expr": "histogram_quantile(0.50, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "50th percentile"
          }
        ],
        "yAxes": [
          {
            "label": "Response Time (seconds)"
          }
        ]
      },
      {
        "id": 2,
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{ instance }} - {{ method }} {{ status }}"
          }
        ]
      },
      {
        "id": 3,
        "title": "Error Rate",
        "type": "singlestat",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~\"5..\"}[5m]) / rate(http_requests_total[5m]) * 100",
            "legendFormat": "Error Rate %"
          }
        ],
        "thresholds": "1,5",
        "colorBackground": true
      },
      {
        "id": 4,
        "title": "Database Connections",
        "type": "graph",
        "targets": [
          {
            "expr": "pg_stat_database_numbackends",
            "legendFormat": "{{ datname }}"
          }
        ]
      },
      {
        "id": 5,
        "title": "System Resources",
        "type": "graph",
        "targets": [
          {
            "expr": "100 - (avg by (instance) (rate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)",
            "legendFormat": "CPU Usage %"
          },
          {
            "expr": "(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100",
            "legendFormat": "Memory Usage %"
          }
        ]
      }
    ],
    "time": {
      "from": "now-1h",
      "to": "now"
    },
    "refresh": "30s"
  }
}
```

### 🧪 Testing Strategy

#### Integration Tests
```python
# tests/integration/test_application.py
import pytest
import requests
import time
import psycopg2
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

class TestApplicationIntegration:
    
    @pytest.fixture(scope="class")
    def app_url(self):
        return "http://test-lb-12345.us-west-2.elb.amazonaws.com"
    
    @pytest.fixture(scope="class")
    def db_connection(self):
        conn = psycopg2.connect(
            host="test-db.cluster-xyz.us-west-2.rds.amazonaws.com",
            database="webapp",
            user="webapp_user",
            password="secure_password"
        )
        yield conn
        conn.close()
    
    def test_health_endpoint(self, app_url):
        """Test application health endpoint"""
        response = requests.get(f"{app_url}/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_api_endpoints(self, app_url):
        """Test critical API endpoints"""
        endpoints = [
            "/api/users",
            "/api/products",
            "/api/orders"
        ]
        
        for endpoint in endpoints:
            response = requests.get(f"{app_url}{endpoint}")
            assert response.status_code in [200, 401]  # 401 for auth required
    
    def test_database_connectivity(self, db_connection):
        """Test database connectivity and basic queries"""
        cursor = db_connection.cursor()
        
        # Test basic connectivity
        cursor.execute("SELECT 1")
        assert cursor.fetchone()[0] == 1
        
        # Test application tables exist
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = [row[0] for row in cursor.fetchall()]
        required_tables = ["users", "products", "orders"]
        
        for table in required_tables:
            assert table in tables
        
        cursor.close()
    
    def test_load_balancer_distribution(self, app_url):
        """Test load balancer distributes requests"""
        servers = set()
        
        for _ in range(10):
            response = requests.get(f"{app_url}/api/server-info")
            if response.status_code == 200:
                servers.add(response.json().get("server_id"))
        
        # Should hit multiple servers
        assert len(servers) > 1
    
    def test_auto_scaling(self, app_url):
        """Test auto scaling under load"""
        # Generate load
        import concurrent.futures
        import threading
        
        def make_request():
            try:
                requests.get(f"{app_url}/api/heavy-operation", timeout=30)
            except:
                pass
        
        # Launch concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(make_request) for _ in range(100)]
            concurrent.futures.wait(futures, timeout=60)
        
        # Wait for scaling to take effect
        time.sleep(300)
        
        # Check if new instances were launched
        # This would require AWS API calls to verify ASG scaling
        # For demo purposes, we'll check if the service is still responsive
        response = requests.get(f"{app_url}/health")
        assert response.status_code == 200
    
    def test_frontend_functionality(self, app_url):
        """Test frontend using Selenium"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(options=chrome_options)
        
        try:
            driver.get(app_url)
            
            # Check page title
            assert "Enterprise App" in driver.title
            
            # Test navigation
            nav_links = driver.find_elements("css selector", "nav a")
            assert len(nav_links) > 0
            
            # Test form submission
            if driver.find_elements("css selector", "form"):
                # Test would depend on specific form implementation
                pass
                
        finally:
            driver.quit()

class TestSecurityIntegration:
    
    def test_ssl_configuration(self, app_url):
        """Test SSL/TLS configuration"""
        if app_url.startswith("https://"):
            response = requests.get(app_url)
            assert response.status_code == 200
    
    def test_security_headers(self, app_url):
        """Test security headers are present"""
        response = requests.get(app_url)
        
        security_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options",
            "X-XSS-Protection",
            "Strict-Transport-Security"
        ]
        
        for header in security_headers:
            assert header in response.headers
    
    def test_sql_injection_protection(self, app_url):
        """Test SQL injection protection"""
        malicious_payloads = [
            "' OR 1=1--",
            "'; DROP TABLE users;--",
            "1' UNION SELECT * FROM users--"
        ]
        
        for payload in malicious_payloads:
            response = requests.get(f"{app_url}/api/users", params={"id": payload})
            # Should not return sensitive data or cause errors
            assert response.status_code in [400, 404, 422]

class TestPerformanceIntegration:
    
    def test_response_times(self, app_url):
        """Test response time requirements"""
        endpoints = [
            "/",
            "/api/users",
            "/api/products"
        ]
        
        for endpoint in endpoints:
            start_time = time.time()
            response = requests.get(f"{app_url}{endpoint}")
            end_time = time.time()
            
            response_time = end_time - start_time
            assert response_time < 2.0  # 2 second SLA
    
    def test_concurrent_users(self, app_url):
        """Test system under concurrent load"""
        import concurrent.futures
        
        def user_session():
            session = requests.Session()
            
            # Simulate user workflow
            session.get(f"{app_url}/")
            session.get(f"{app_url}/api/products")
            session.get(f"{app_url}/api/users/profile")
            
            return session.get(f"{app_url}/health").status_code == 200
        
        # Simulate 20 concurrent users
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(user_session) for _ in range(20)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # At least 95% success rate
        success_rate = sum(results) / len(results)
        assert success_rate >= 0.95
```

### 📋 Project Deliverables

#### Documentation Requirements
1. **Architecture Documentation**
   - System architecture diagrams
   - Network topology
   - Security model
   - Data flow diagrams

2. **Deployment Documentation**
   - Step-by-step deployment guide
   - Environment configuration
   - Rollback procedures
   - Troubleshooting guide

3. **Operations Documentation**
   - Monitoring runbooks
   - Alerting procedures
   - Backup and recovery
   - Disaster recovery plan

#### Code Deliverables
1. **Infrastructure Code**
   - Terraform modules và configurations
   - Ansible playbooks và roles
   - CI/CD pipeline definitions

2. **Application Code**
   - Frontend application
   - Backend API services
   - Database schemas và migrations

3. **Testing Code**
   - Unit tests
   - Integration tests
   - Performance tests
   - Security tests

## Project 2: Kubernetes Cluster Automation

### 📋 Project Description
Triển khai và quản lý Kubernetes cluster với complete automation cho provisioning, configuration, application deployment, và day-2 operations.

### 🏗️ Architecture Overview
```
Control Plane (HA)
├── 3x Master Nodes
├── External ETCD Cluster
└── Load Balancer

Worker Nodes
├── Auto Scaling Groups
├── Mixed Instance Types
└── Spot Instance Integration

Networking
├── Calico CNI
├── Network Policies
└── Ingress Controllers

Storage
├── EBS CSI Driver
├── EFS CSI Driver
└── Persistent Volumes

Monitoring
├── Prometheus Operator
├── Grafana
├── Alertmanager
└── Jaeger Tracing
```

### 🔧 Implementation Highlights

#### Terraform for Cluster Infrastructure
```hcl
# terraform/modules/eks/main.tf
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "19.15.3"

  cluster_name    = var.cluster_name
  cluster_version = var.kubernetes_version

  vpc_id                         = var.vpc_id
  subnet_ids                     = var.subnet_ids
  cluster_endpoint_public_access = true

  # EKS Managed Node Groups
  eks_managed_node_groups = {
    main = {
      name = "main"

      instance_types = ["m5.large", "m5a.large", "m4.large"]
      capacity_type  = "SPOT"

      min_size     = 3
      max_size     = 10
      desired_size = 5

      k8s_labels = {
        Environment = var.environment
        NodeGroup   = "main"
      }

      tags = {
        ExtraTag = "EKS managed node group"
      }
    }
  }

  # aws-auth configmap
  manage_aws_auth_configmap = true

  aws_auth_roles = [
    {
      rolearn  = aws_iam_role.eks_admin.arn
      username = "eks-admin"
      groups   = ["system:masters"]
    },
  ]

  tags = var.common_tags
}
```

#### Ansible for Kubernetes Application Deployment
```yaml
# ansible/playbooks/k8s-apps.yml
---
- name: Deploy Kubernetes Applications
  hosts: localhost
  connection: local
  gather_facts: no
  
  tasks:
    - name: Create namespaces
      kubernetes.core.k8s:
        name: "{{ item }}"
        api_version: v1
        kind: Namespace
        state: present
      loop:
        - monitoring
        - logging
        - ingress-nginx
        - cert-manager
        - argocd

    - name: Deploy Prometheus Operator
      kubernetes.core.helm:
        name: prometheus-operator
        chart_ref: prometheus-community/kube-prometheus-stack
        release_namespace: monitoring
        create_namespace: true
        values:
          grafana:
            enabled: true
            adminPassword: "{{ grafana_admin_password }}"
          prometheus:
            prometheusSpec:
              retention: 30d
              storageSpec:
                volumeClaimTemplate:
                  spec:
                    storageClassName: gp3
                    accessModes: ["ReadWriteOnce"]
                    resources:
                      requests:
                        storage: 50Gi

    - name: Deploy ArgoCD
      kubernetes.core.helm:
        name: argocd
        chart_ref: argo/argo-cd
        release_namespace: argocd
        create_namespace: true
        values:
          server:
            service:
              type: LoadBalancer
            config:
              repositories: |
                - type: git
                  url: https://github.com/viettel-idc/k8s-apps
                  name: k8s-apps
```

### 📊 Key Features
- **High Availability**: Multi-AZ master nodes với external ETCD
- **Auto Scaling**: Cluster Autoscaler và HPA integration
- **Security**: RBAC, Network Policies, Pod Security Standards
- **Monitoring**: Complete observability stack
- **GitOps**: ArgoCD for application deployment
- **Backup**: Velero for cluster backups

## Project 3: Multi-Cloud Infrastructure Management

### 📋 Project Description
Triển khai identical infrastructure across multiple cloud providers (AWS, Azure, GCP) với unified management và cross-cloud networking.

### 🏗️ Multi-Cloud Architecture
```
Global Load Balancer (Cloudflare)
├── AWS Region (us-west-2)
│   ├── VPC + Subnets
│   ├── EKS Cluster
│   └── RDS Database
├── Azure Region (West US 2)
│   ├── VNet + Subnets
│   ├── AKS Cluster
│   └── PostgreSQL Database
└── GCP Region (us-west1)
    ├── VPC + Subnets
    ├── GKE Cluster
    └── Cloud SQL Database

Cross-Cloud Networking
├── VPN Connections
├── Private Connectivity
└── DNS Resolution
```

### 🔧 Implementation Strategy

#### Terraform with Multiple Providers
```hcl
# terraform/main.tf
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

# AWS Resources
module "aws_infrastructure" {
  source = "./modules/aws"
  
  providers = {
    aws = aws.us_west_2
  }
  
  region          = "us-west-2"
  environment     = var.environment
  project_name    = var.project_name
}

# Azure Resources
module "azure_infrastructure" {
  source = "./modules/azure"
  
  providers = {
    azurerm = azurerm.west_us_2
  }
  
  location        = "West US 2"
  environment     = var.environment
  project_name    = var.project_name
}

# GCP Resources
module "gcp_infrastructure" {
  source = "./modules/gcp"
  
  providers = {
    google = google.us_west1
  }
  
  region          = "us-west1"
  environment     = var.environment
  project_name    = var.project_name
}
```

### 📊 Key Features
- **Cloud Agnostic**: Identical infrastructure patterns
- **Cross-Cloud Networking**: Secure inter-cloud communication
- **Unified Monitoring**: Centralized observability
- **Disaster Recovery**: Cross-cloud failover
- **Cost Optimization**: Multi-cloud cost analysis

## Project 4: Infrastructure Security Automation

### 📋 Project Description
Implement comprehensive security automation covering compliance scanning, vulnerability assessment, security hardening, và incident response.

### 🔐 Security Components
```
Security Automation Pipeline
├── Compliance Scanning
│   ├── CIS Benchmarks
│   ├── SOC 2 Controls
│   └── Custom Policies
├── Vulnerability Assessment
│   ├── Container Scanning
│   ├── Infrastructure Scanning
│   └── Application Scanning
├── Security Hardening
│   ├── OS Hardening
│   ├── Network Security
│   └── Application Security
└── Incident Response
    ├── Automated Detection
    ├── Response Automation
    └── Forensic Collection
```

### 🛡️ Implementation Details

#### Security Scanning Pipeline
```yaml
# .github/workflows/security-scan.yml
name: 'Security Scanning Pipeline'

on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM
  push:
    branches: [ main ]

jobs:
  infrastructure-scan:
    name: 'Infrastructure Security Scan'
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout
      uses: actions/checkout@v3
    
    - name: Run Checkov
      uses: bridgecrewio/checkov-action@master
      with:
        directory: terraform
        framework: terraform,dockerfile,kubernetes
        output_format: sarif
        output_file_path: checkov.sarif
    
    - name: Run Trivy
      uses: aquasecurity/trivy-action@master
      with:
        scan-type: 'config'
        scan-ref: 'terraform/'
        format: 'sarif'
        output: 'trivy.sarif'
    
    - name: Upload results to Security Hub
      run: |
        aws securityhub batch-import-findings \
          --findings file://checkov.sarif \
          --region us-west-2
```

#### Ansible Security Hardening
```yaml
# ansible/playbooks/security-hardening.yml
---
- name: Comprehensive Security Hardening
  hosts: all
  become: yes
  
  roles:
    - cis_compliance
    - vulnerability_scanner
    - intrusion_detection
    - log_monitoring
  
  tasks:
    - name: Configure auditd
      template:
        src: audit.rules.j2
        dest: /etc/audit/rules.d/audit.rules
      notify: restart auditd
    
    - name: Setup AIDE integrity checking
      block:
        - name: Initialize AIDE database
          shell: aide --init
          creates: /var/lib/aide/aide.db.new
        
        - name: Move AIDE database
          shell: mv /var/lib/aide/aide.db.new /var/lib/aide/aide.db
          creates: /var/lib/aide/aide.db
        
        - name: Setup AIDE cron job
          cron:
            name: "AIDE integrity check"
            minute: "0"
            hour: "3"
            job: "/usr/bin/aide --check | mail -s 'AIDE Report' security@company.com"
```

### 📊 Key Features
- **Automated Compliance**: CIS, SOX, PCI-DSS compliance checking
- **Vulnerability Management**: Automated scanning và remediation
- **Incident Response**: Automated threat detection và response
- **Forensic Readiness**: Log collection và analysis automation
- **Security Monitoring**: Real-time security event monitoring

## 🎯 Project Assessment Criteria

### Technical Excellence (40%)
- **Code Quality**: Clean, maintainable, well-documented code
- **Architecture**: Scalable, resilient, secure design
- **Automation**: Comprehensive automation coverage
- **Testing**: Robust testing strategy implementation

### Operational Excellence (30%)
- **Monitoring**: Comprehensive observability
- **Reliability**: High availability và disaster recovery
- **Performance**: Optimized resource utilization
- **Security**: Security best practices implementation

### Business Impact (30%)
- **Cost Optimization**: Efficient resource usage
- **Time to Market**: Faster deployment cycles
- **Risk Reduction**: Improved security và compliance
- **Scalability**: Ability to handle growth

## 📚 Learning Outcomes

Sau khi hoàn thành các projects này, học viên sẽ:

### Technical Skills
- **Infrastructure as Code**: Expertise in Terraform và Ansible
- **Cloud Platforms**: Multi-cloud management capabilities
- **Container Orchestration**: Kubernetes administration
- **Security**: Comprehensive security automation
- **Monitoring**: Observability và performance optimization

### Operational Skills
- **DevOps Practices**: CI/CD pipeline implementation
- **Incident Management**: Automated incident response
- **Capacity Planning**: Resource optimization strategies
- **Compliance**: Automated compliance management

### Business Skills
- **Cost Management**: Cloud cost optimization
- **Risk Assessment**: Security risk evaluation
- **Project Management**: Complex project delivery
- **Documentation**: Technical documentation creation

---

*Lưu ý: Các projects này được thiết kế để cung cấp hands-on experience với real-world scenarios, giúp học viên phát triển skills cần thiết cho senior automation engineer roles.*
