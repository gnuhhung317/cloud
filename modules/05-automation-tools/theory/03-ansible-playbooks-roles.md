# Ansible Playbooks và Roles - Quản lý Cấu hình Nâng cao

## 🎯 Mục tiêu Học tập
- Thành thạo viết và tổ chức Ansible Playbooks
- Hiểu rõ Roles và cách sử dụng hiệu quả
- Nắm vững Variables, Templates và Handlers
- Áp dụng best practices trong automation workflows

## 1. Playbook Fundamentals

### 1.1 Cấu trúc Playbook YAML

#### Basic Playbook Structure
```yaml
---
- name: Web Server Configuration Playbook
  hosts: webservers
  become: yes
  gather_facts: yes
  
  vars:
    http_port: 80
    https_port: 443
    server_admin: admin@company.com
  
  tasks:
    - name: Install web server
      package:
        name: nginx
        state: present
    
    - name: Start and enable nginx
      service:
        name: nginx
        state: started
        enabled: yes
  
  handlers:
    - name: restart nginx
      service:
        name: nginx
        state: restarted
```

#### Multiple Plays trong Single Playbook
```yaml
---
# Play 1: Configure load balancers
- name: Configure Load Balancers
  hosts: loadbalancers
  become: yes
  roles:
    - common
    - loadbalancer

# Play 2: Configure web servers  
- name: Configure Web Servers
  hosts: webservers
  become: yes
  serial: 2  # Rolling deployment
  roles:
    - common
    - webserver
    - application

# Play 3: Configure databases
- name: Configure Database Servers
  hosts: databases
  become: yes
  roles:
    - common
    - database
    - backup
```

### 1.2 Task Organization và Control

#### Task Blocks và Error Handling
```yaml
---
- name: Complex deployment with error handling
  hosts: webservers
  tasks:
    - name: Application deployment block
      block:
        - name: Stop application service
          service:
            name: myapp
            state: stopped
        
        - name: Deploy new application version
          unarchive:
            src: "{{ app_package_url }}"
            dest: /opt/myapp
            remote_src: yes
            owner: myapp
            group: myapp
        
        - name: Update configuration
          template:
            src: app.conf.j2
            dest: /etc/myapp/app.conf
          notify: restart myapp
        
        - name: Start application service
          service:
            name: myapp
            state: started
      
      rescue:
        - name: Rollback to previous version
          command: /opt/myapp/scripts/rollback.sh
        
        - name: Start application with old version
          service:
            name: myapp
            state: started
        
        - name: Send failure notification
          mail:
            to: "{{ ops_team_email }}"
            subject: "Deployment failed on {{ inventory_hostname }}"
            body: "Application deployment failed, rolled back to previous version"
      
      always:
        - name: Cleanup temporary files
          file:
            path: /tmp/deployment_*
            state: absent
        
        - name: Log deployment attempt
          lineinfile:
            path: /var/log/deployments.log
            line: "{{ ansible_date_time.iso8601 }} - Deployment {{ 'completed' if ansible_failed_task is not defined else 'failed' }}"
```

#### Conditional Execution
```yaml
---
- name: OS-specific package installation
  hosts: all
  tasks:
    - name: Install web server on RedHat family
      yum:
        name: httpd
        state: present
      when: ansible_os_family == "RedHat"
    
    - name: Install web server on Debian family
      apt:
        name: apache2
        state: present
      when: ansible_os_family == "Debian"
    
    - name: Complex conditional logic
      package:
        name: "{{ item }}"
        state: present
      loop:
        - nginx
        - php-fpm
      when: 
        - ansible_distribution_major_version|int >= 8
        - server_role == "webserver"
        - enable_php is defined and enable_php|bool
    
    - name: Environment-specific configuration
      template:
        src: "{{ app_config_template }}"
        dest: /etc/myapp/config.yml
      vars:
        app_config_template: >-
          {%- if environment == 'production' -%}
          production.yml.j2
          {%- elif environment == 'staging' -%}
          staging.yml.j2
          {%- else -%}
          development.yml.j2
          {%- endif -%}
```

#### Loops và Iteration
```yaml
---
- name: Advanced looping examples
  hosts: all
  tasks:
    # Simple list loop
    - name: Install multiple packages
      package:
        name: "{{ item }}"
        state: present
      loop:
        - vim
        - git
        - htop
        - curl
    
    # Dictionary loop
    - name: Create multiple users
      user:
        name: "{{ item.name }}"
        groups: "{{ item.groups }}"
        shell: "{{ item.shell | default('/bin/bash') }}"
        create_home: yes
      loop:
        - { name: alice, groups: "wheel,docker", shell: "/bin/zsh" }
        - { name: bob, groups: "developers" }
        - { name: charlie, groups: "wheel" }
    
    # Loop with conditional
    - name: Configure services
      service:
        name: "{{ item.name }}"
        state: "{{ item.state }}"
        enabled: "{{ item.enabled }}"
      loop:
        - { name: nginx, state: started, enabled: yes }
        - { name: apache2, state: stopped, enabled: no }
        - { name: mysql, state: started, enabled: yes }
      when: item.name in ansible_facts.packages
    
    # Loop over file contents
    - name: Add SSH keys from file
      authorized_key:
        user: "{{ item.split()[2] }}"
        key: "{{ item }}"
      loop: "{{ lookup('file', 'ssh_keys.txt').splitlines() }}"
      when: item | length > 0 and not item.startswith('#')
    
    # Nested loops
    - name: Configure firewall rules
      firewalld:
        port: "{{ item.1 }}/tcp"
        permanent: yes
        state: enabled
        zone: "{{ item.0.zone }}"
      loop: "{{ environments | subelements('ports') }}"
      vars:
        environments:
          - zone: public
            ports: [80, 443]
          - zone: internal  
            ports: [22, 3306, 5432]
```

## 2. Variables Management

### 2.1 Variable Precedence và Scope

#### Variable Precedence (Thứ tự ưu tiên từ thấp đến cao)
1. role defaults
2. inventory file or script group vars
3. inventory group_vars/all
4. playbook group_vars/all
5. inventory group_vars/*
6. playbook group_vars/*
7. inventory file or script host vars
8. inventory host_vars/*
9. playbook host_vars/*
10. host facts / cached set_facts
11. play vars
12. play vars_prompt
13. play vars_files
14. role vars
15. block vars
16. task vars
17. include_vars
18. set_facts / registered vars
19. role (and include_role) params
20. include params
21. extra vars (always win precedence)

#### Group Variables Organization
```bash
# Directory structure
inventory/
├── group_vars/
│   ├── all.yml                 # Variables for all hosts
│   ├── webservers.yml         # Variables for webservers group
│   ├── databases.yml          # Variables for databases group
│   └── production/            # Environment-specific variables
│       ├── all.yml
│       ├── webservers.yml
│       └── databases.yml
└── host_vars/
    ├── web01.example.com.yml  # Host-specific variables
    └── db01.example.com.yml
```

```yaml
# group_vars/all.yml
---
# Global configuration
company_name: "Viettel IDC"
timezone: "Asia/Ho_Chi_Minh"
ntp_servers:
  - 0.pool.ntp.org
  - 1.pool.ntp.org

# Security settings
security_updates_enabled: true
firewall_enabled: true

# Monitoring
monitoring_enabled: true
log_level: "INFO"

# Backup configuration
backup_enabled: true
backup_retention_days: 30
```

```yaml
# group_vars/webservers.yml
---
# Web server specific configuration
web_server: nginx
web_port: 80
ssl_port: 443
document_root: /var/www/html

# SSL configuration
ssl_enabled: true
ssl_certificate_path: /etc/ssl/certs/server.crt
ssl_private_key_path: /etc/ssl/private/server.key

# Performance tuning
worker_processes: "{{ ansible_processor_vcpus }}"
worker_connections: 1024
keepalive_timeout: 65

# Application settings
app_name: "web-application"
app_version: "1.2.3"
app_user: "webapp"
app_group: "webapp"
```

### 2.2 Advanced Variable Techniques

#### Ansible Vault for Sensitive Data
```bash
# Create encrypted variable file
ansible-vault create group_vars/production/vault.yml

# Edit encrypted file
ansible-vault edit group_vars/production/vault.yml

# View encrypted file
ansible-vault view group_vars/production/vault.yml

# Encrypt existing file
ansible-vault encrypt secrets.yml

# Decrypt file
ansible-vault decrypt secrets.yml
```

```yaml
# group_vars/production/vault.yml (encrypted)
---
vault_database_password: "super_secret_password"
vault_api_key: "abcd1234567890"
vault_ssl_private_key: |
  -----BEGIN PRIVATE KEY-----
  MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC...
  -----END PRIVATE KEY-----
```

```yaml
# group_vars/production/vars.yml (unencrypted)
---
database_user: "app_user"
database_password: "{{ vault_database_password }}"
api_endpoint: "https://api.production.com"
api_key: "{{ vault_api_key }}"
ssl_private_key: "{{ vault_ssl_private_key }}"
```

#### Dynamic Variables và Fact Gathering
```yaml
---
- name: Dynamic variable example
  hosts: all
  vars:
    base_packages:
      - vim
      - git
      - htop
    
    # OS-specific packages
    os_packages: >-
      {%- if ansible_os_family == 'RedHat' -%}
      ['yum-utils', 'epel-release']
      {%- elif ansible_os_family == 'Debian' -%}
      ['apt-transport-https', 'software-properties-common']
      {%- else -%}
      []
      {%- endif -%}
    
    # Environment-specific settings
    app_config:
      development:
        debug: true
        log_level: DEBUG
        database_pool_size: 5
      staging:
        debug: false
        log_level: INFO
        database_pool_size: 10
      production:
        debug: false
        log_level: WARNING
        database_pool_size: 20
  
  tasks:
    - name: Set environment-specific variables
      set_fact:
        current_config: "{{ app_config[environment] }}"
    
    - name: Install base and OS-specific packages
      package:
        name: "{{ base_packages + os_packages }}"
        state: present
    
    - name: Register custom facts
      set_fact:
        server_facts:
          memory_gb: "{{ (ansible_memtotal_mb / 1024) | round(1) }}"
          cpu_count: "{{ ansible_processor_vcpus }}"
          disk_size_gb: "{{ (ansible_mounts | selectattr('mount', 'equalto', '/') | map(attribute='size_total') | first / 1024**3) | round(1) }}"
          uptime_days: "{{ (ansible_uptime_seconds / 86400) | round(1) }}"
```

## 3. Templates và Jinja2

### 3.1 Jinja2 Template Engine

#### Basic Template Usage
```yaml
# playbook task
- name: Configure nginx virtual host
  template:
    src: nginx_vhost.j2
    dest: "/etc/nginx/sites-available/{{ site_name }}"
    owner: root
    group: root
    mode: '0644'
  notify: reload nginx
```

```nginx
# templates/nginx_vhost.j2
server {
    listen {{ web_port }};
    server_name {{ server_name }};
    root {{ document_root }};
    index index.html index.php;
    
    # SSL configuration
    {% if ssl_enabled %}
    listen {{ ssl_port }} ssl;
    ssl_certificate {{ ssl_certificate_path }};
    ssl_certificate_key {{ ssl_private_key_path }};
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
    {% endif %}
    
    # Performance settings
    client_max_body_size {{ max_upload_size | default('10M') }};
    
    # Logging
    access_log /var/log/nginx/{{ site_name }}_access.log;
    error_log /var/log/nginx/{{ site_name }}_error.log;
    
    # Location blocks
    location / {
        try_files $uri $uri/ =404;
    }
    
    {% if php_enabled | default(false) %}
    location ~ \.php$ {
        fastcgi_pass unix:/var/run/php/php{{ php_version }}-fpm.sock;
        fastcgi_index index.php;
        include fastcgi_params;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
    }
    {% endif %}
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    {% if environment == 'production' %}
    # Production-only security
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    {% endif %}
}
```

#### Advanced Template Features
```yaml
# Complex configuration template
# templates/app_config.yml.j2
---
application:
  name: "{{ app_name }}"
  version: "{{ app_version }}"
  environment: "{{ environment }}"
  
  # Database configuration with conditional logic
  database:
    {% if environment == 'production' %}
    host: "{{ production_db_host }}"
    port: {{ production_db_port }}
    {% else %}
    host: "{{ dev_db_host | default('localhost') }}"
    port: {{ dev_db_port | default(5432) }}
    {% endif %}
    
    name: "{{ database_name }}"
    username: "{{ database_user }}"
    password: "{{ database_password }}"
    
    # Connection pool settings based on server specs
    pool_size: >-
      {%- if ansible_memtotal_mb > 8192 -%}
      {{ 20 }}
      {%- elif ansible_memtotal_mb > 4096 -%}
      {{ 10 }}
      {%- else -%}
      {{ 5 }}
      {%- endif -%}

  # Server configuration
  server:
    host: "{{ ansible_default_ipv4.address }}"
    port: {{ app_port }}
    workers: {{ ansible_processor_vcpus * 2 }}
    
    # Feature flags
    features:
      {% for feature, enabled in feature_flags.items() %}
      {{ feature }}: {{ enabled | lower }}
      {% endfor %}

  # Logging configuration
  logging:
    level: "{{ log_level }}"
    file: "/var/log/{{ app_name }}/application.log"
    max_size: "{{ log_max_size | default('100MB') }}"
    backup_count: {{ log_backup_count | default(5) }}
    
    # Format based on environment
    format: >-
      {%- if environment == 'development' -%}
      "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
      {%- else -%}
      "%(asctime)s - %(levelname)s - %(message)s"
      {%- endif -%}

  # Environment-specific services
  services:
    {% if enable_redis | default(false) %}
    redis:
      host: "{{ redis_host | default('localhost') }}"
      port: {{ redis_port | default(6379) }}
      db: {{ redis_db | default(0) }}
    {% endif %}
    
    {% if enable_elasticsearch | default(false) %}
    elasticsearch:
      hosts:
        {% for host in elasticsearch_hosts %}
        - "{{ host }}"
        {% endfor %}
      index_prefix: "{{ app_name }}_{{ environment }}"
    {% endif %}

# Macro definitions for reusable template logic
{% macro render_service_config(service_name, config) %}
{{ service_name }}:
  {% for key, value in config.items() %}
  {{ key }}: {{ value }}
  {% endfor %}
{% endmacro %}

# Use macro
monitoring:
  {{ render_service_config('prometheus', prometheus_config) }}
  {{ render_service_config('grafana', grafana_config) }}
```

### 3.2 Template Testing và Validation

```yaml
---
- name: Template validation example
  hosts: localhost
  vars:
    test_variables:
      app_name: "test-app"
      environment: "development"
      database_host: "localhost"
  
  tasks:
    - name: Generate test configuration
      template:
        src: app_config.yml.j2
        dest: /tmp/test_config.yml
      vars: "{{ test_variables }}"
    
    - name: Validate generated configuration
      shell: python -c "import yaml; yaml.safe_load(open('/tmp/test_config.yml'))"
      register: yaml_validation
      failed_when: yaml_validation.rc != 0
    
    - name: Check required configuration keys
      shell: |
        python -c "
        import yaml
        config = yaml.safe_load(open('/tmp/test_config.yml'))
        required_keys = ['application.name', 'application.database.host']
        for key in required_keys:
            if not any(key in str(config).replace(':', '.') for key in required_keys):
                exit(1)
        "
      register: key_validation
      failed_when: key_validation.rc != 0
```

## 4. Handlers và Notifications

### 4.1 Handler Basics

```yaml
---
- name: Web server configuration with handlers
  hosts: webservers
  tasks:
    - name: Install nginx
      package:
        name: nginx
        state: present
      notify: 
        - start nginx
        - enable nginx
    
    - name: Configure nginx main config
      template:
        src: nginx.conf.j2
        dest: /etc/nginx/nginx.conf
        backup: yes
      notify: reload nginx
    
    - name: Configure virtual hosts
      template:
        src: vhost.conf.j2
        dest: "/etc/nginx/sites-available/{{ item.name }}"
      loop: "{{ virtual_hosts }}"
      notify: reload nginx
    
    - name: Enable virtual hosts
      file:
        src: "/etc/nginx/sites-available/{{ item.name }}"
        dest: "/etc/nginx/sites-enabled/{{ item.name }}"
        state: link
      loop: "{{ virtual_hosts }}"
      notify: reload nginx
  
  handlers:
    - name: start nginx
      service:
        name: nginx
        state: started
    
    - name: enable nginx
      service:
        name: nginx
        enabled: yes
    
    - name: reload nginx
      service:
        name: nginx
        state: reloaded
      # Only reload if nginx is already running
      when: ansible_facts.services['nginx.service']['state'] == 'running'
```

### 4.2 Advanced Handler Patterns

#### Handler Chains
```yaml
handlers:
  - name: restart application stack
    debug:
      msg: "Restarting application stack"
    notify:
      - stop application
      - clear cache
      - start application
      - verify application
  
  - name: stop application
    service:
      name: "{{ app_service_name }}"
      state: stopped
  
  - name: clear cache
    file:
      path: "{{ app_cache_dir }}"
      state: absent
  
  - name: start application
    service:
      name: "{{ app_service_name }}"
      state: started
  
  - name: verify application
    uri:
      url: "http://localhost:{{ app_port }}/health"
      method: GET
      status_code: 200
    retries: 5
    delay: 10
```

#### Conditional Handlers
```yaml
handlers:
  - name: restart nginx
    service:
      name: nginx
      state: restarted
    when: 
      - nginx_restart_allowed | default(true)
      - not maintenance_mode | default(false)
    listen: "restart web services"
  
  - name: restart php-fpm
    service:
      name: php-fpm
      state: restarted
    when: php_enabled | default(false)
    listen: "restart web services"
  
  - name: clear opcache
    uri:
      url: "http://localhost/opcache-reset.php"
      method: POST
    when: php_opcache_enabled | default(false)
    listen: "restart web services"
```

## 5. Roles - Modular Automation

### 5.1 Role Structure và Organization

#### Standard Role Directory Structure
```bash
roles/
└── webserver/
    ├── defaults/
    │   └── main.yml          # Default variables (lowest precedence)
    ├── files/
    │   ├── ssl-cert.crt      # Static files to copy
    │   └── index.html
    ├── handlers/
    │   └── main.yml          # Handler definitions
    ├── meta/
    │   └── main.yml          # Role metadata và dependencies
    ├── tasks/
    │   ├── main.yml          # Main task file
    │   ├── install.yml       # Installation tasks
    │   ├── configure.yml     # Configuration tasks
    │   └── security.yml      # Security-related tasks
    ├── templates/
    │   ├── nginx.conf.j2     # Jinja2 templates
    │   └── vhost.conf.j2
    ├── tests/
    │   ├── inventory         # Test inventory
    │   └── test.yml          # Test playbook
    └── vars/
        └── main.yml          # Role variables (high precedence)
```

#### Role Creation
```bash
# Create role structure using ansible-galaxy
ansible-galaxy init webserver
ansible-galaxy init database
ansible-galaxy init monitoring

# Create role with custom template
ansible-galaxy init --role-skeleton=custom-skeleton webserver
```

### 5.2 Role Implementation Examples

#### Complete Webserver Role
```yaml
# roles/webserver/defaults/main.yml
---
webserver_package: nginx
webserver_service: nginx
webserver_user: www-data
webserver_group: www-data

# Port configuration
http_port: 80
https_port: 443

# SSL configuration
ssl_enabled: false
ssl_certificate_path: /etc/ssl/certs/server.crt
ssl_private_key_path: /etc/ssl/private/server.key

# Performance settings
worker_processes: auto
worker_connections: 1024
keepalive_timeout: 65
client_max_body_size: 1M

# Security settings
server_tokens: off
add_security_headers: true

# Virtual hosts
virtual_hosts: []
```

```yaml
# roles/webserver/vars/main.yml
---
# OS-specific variables
webserver_config_path:
  RedHat: /etc/nginx
  Debian: /etc/nginx

webserver_service_name:
  RedHat: nginx
  Debian: nginx

webserver_packages:
  RedHat:
    - nginx
    - nginx-mod-http-ssl
  Debian:
    - nginx
    - nginx-extras
```

```yaml
# roles/webserver/tasks/main.yml
---
- name: Include OS-specific variables
  include_vars: "{{ ansible_os_family }}.yml"
  when: ansible_os_family in ['RedHat', 'Debian']

- name: Install webserver packages
  include_tasks: install.yml

- name: Configure webserver
  include_tasks: configure.yml

- name: Setup SSL if enabled
  include_tasks: ssl.yml
  when: ssl_enabled | bool

- name: Configure virtual hosts
  include_tasks: vhosts.yml
  when: virtual_hosts | length > 0

- name: Apply security hardening
  include_tasks: security.yml
  when: security_hardening_enabled | default(true)

- name: Start and enable webserver service
  service:
    name: "{{ webserver_service }}"
    state: started
    enabled: yes
```

```yaml
# roles/webserver/tasks/install.yml
---
- name: Update package cache
  package:
    name: "*"
    state: latest
    update_cache: yes
  when: update_packages | default(false)

- name: Install webserver packages
  package:
    name: "{{ webserver_packages[ansible_os_family] }}"
    state: present

- name: Create webserver user
  user:
    name: "{{ webserver_user }}"
    group: "{{ webserver_group }}"
    system: yes
    home: /var/www
    shell: /sbin/nologin
    create_home: no
```

```yaml
# roles/webserver/tasks/configure.yml
---
- name: Create configuration directories
  file:
    path: "{{ item }}"
    state: directory
    owner: root
    group: root
    mode: '0755'
  loop:
    - "{{ webserver_config_path[ansible_os_family] }}/sites-available"
    - "{{ webserver_config_path[ansible_os_family] }}/sites-enabled"
    - /var/log/nginx

- name: Configure main nginx config
  template:
    src: nginx.conf.j2
    dest: "{{ webserver_config_path[ansible_os_family] }}/nginx.conf"
    owner: root
    group: root
    mode: '0644'
    backup: yes
  notify: reload nginx

- name: Remove default site
  file:
    path: "{{ webserver_config_path[ansible_os_family] }}/sites-enabled/default"
    state: absent
  notify: reload nginx
```

```yaml
# roles/webserver/meta/main.yml
---
galaxy_info:
  author: Viettel IDC Team
  description: Nginx web server configuration role
  company: Viettel IDC
  license: MIT
  min_ansible_version: 2.9
  
  platforms:
    - name: EL
      versions:
        - 7
        - 8
        - 9
    - name: Ubuntu
      versions:
        - 18.04
        - 20.04
        - 22.04
    - name: Debian
      versions:
        - 10
        - 11

  galaxy_tags:
    - webserver
    - nginx
    - web
    - http

dependencies:
  - role: common
    vars:
      firewall_rules:
        - port: "{{ http_port }}"
          protocol: tcp
        - port: "{{ https_port }}"
          protocol: tcp
          when: ssl_enabled
  
  - role: ssl-certificates
    when: ssl_enabled | bool
```

### 5.3 Role Dependencies và Composition

#### Complex Role Dependencies
```yaml
# roles/application/meta/main.yml
---
dependencies:
  # Order matters - dependencies run first
  - role: common
    vars:
      common_packages:
        - curl
        - wget
        - unzip
  
  - role: database
    vars:
      db_name: "{{ app_database_name }}"
      db_user: "{{ app_database_user }}"
      db_password: "{{ app_database_password }}"
    when: database_required | default(true)
  
  - role: webserver
    vars:
      virtual_hosts:
        - name: "{{ app_name }}"
          server_name: "{{ app_domain }}"
          document_root: "{{ app_install_path }}/public"
    when: webserver_required | default(true)
  
  - role: ssl-certificates
    vars:
      ssl_domain: "{{ app_domain }}"
    when: ssl_required | default(false)
```

#### Role Composition Pattern
```yaml
# site.yml - Orchestrating multiple roles
---
- name: Deploy complete application stack
  hosts: application_servers
  become: yes
  
  roles:
    # Infrastructure roles
    - role: common
      tags: [common, infrastructure]
    
    - role: security
      tags: [security, infrastructure]
    
    - role: monitoring
      tags: [monitoring, infrastructure]
    
    # Application platform roles
    - role: database
      tags: [database, platform]
      when: "'database' in group_names"
    
    - role: webserver
      tags: [webserver, platform]
      when: "'webserver' in group_names"
    
    - role: loadbalancer
      tags: [loadbalancer, platform]
      when: "'loadbalancer' in group_names"
    
    # Application-specific roles
    - role: application
      tags: [application, deployment]
    
    - role: backup
      tags: [backup, maintenance]
```

## 6. Best Practices và Advanced Patterns

### 6.1 Playbook Organization

#### Directory Structure cho Large Projects
```bash
ansible-project/
├── ansible.cfg
├── site.yml                    # Master playbook
├── webservers.yml             # Webserver-specific playbook
├── databases.yml              # Database-specific playbook
├── inventories/
│   ├── production/
│   │   ├── hosts.yml
│   │   └── group_vars/
│   ├── staging/
│   │   ├── hosts.yml
│   │   └── group_vars/
│   └── development/
│       ├── hosts.yml
│       └── group_vars/
├── group_vars/
│   ├── all/
│   │   ├── main.yml
│   │   └── vault.yml
│   └── webservers/
│       ├── main.yml
│       └── vault.yml
├── host_vars/
├── roles/
│   ├── common/
│   ├── webserver/
│   ├── database/
│   └── monitoring/
├── playbooks/
│   ├── maintenance/
│   ├── deployment/
│   └── troubleshooting/
└── scripts/
    ├── deploy.sh
    └── rollback.sh
```

### 6.2 Error Handling và Recovery

```yaml
---
- name: Robust deployment with error handling
  hosts: webservers
  serial: 1  # Rolling deployment
  max_fail_percentage: 20
  
  pre_tasks:
    - name: Verify prerequisites
      assert:
        that:
          - ansible_version.full is version('2.9', '>=')
          - app_version is defined
          - app_package_url is defined
        fail_msg: "Prerequisites not met"
    
    - name: Check available disk space
      shell: df -h {{ app_install_path }} | tail -1 | awk '{print $5}' | sed 's/%//'
      register: disk_usage
      failed_when: disk_usage.stdout|int > 90
      tags: [pre-check]
  
  tasks:
    - name: Create backup before deployment
      block:
        - name: Stop application
          service:
            name: "{{ app_service }}"
            state: stopped
        
        - name: Create application backup
          archive:
            path: "{{ app_install_path }}"
            dest: "/backups/{{ app_name }}-{{ ansible_date_time.epoch }}.tar.gz"
        
        - name: Deploy new version
          unarchive:
            src: "{{ app_package_url }}"
            dest: "{{ app_install_path }}"
            remote_src: yes
            backup: yes
        
        - name: Update configuration
          template:
            src: app.conf.j2
            dest: "{{ app_config_path }}"
          notify: restart application
        
        - name: Start application
          service:
            name: "{{ app_service }}"
            state: started
        
        - name: Wait for application to be ready
          uri:
            url: "http://localhost:{{ app_port }}/health"
            method: GET
            status_code: 200
          register: health_check
          until: health_check.status == 200
          retries: 30
          delay: 10
      
      rescue:
        - name: Rollback on failure
          block:
            - name: Stop failed application
              service:
                name: "{{ app_service }}"
                state: stopped
              ignore_errors: yes
            
            - name: Restore from backup
              unarchive:
                src: "/backups/{{ app_name }}-{{ ansible_date_time.epoch }}.tar.gz"
                dest: "{{ app_install_path | dirname }}"
                remote_src: yes
            
            - name: Start application
              service:
                name: "{{ app_service }}"
                state: started
            
            - name: Verify rollback success
              uri:
                url: "http://localhost:{{ app_port }}/health"
                method: GET
                status_code: 200
              retries: 10
              delay: 5
        
        - name: Send failure notification
          mail:
            to: "{{ ops_team_email }}"
            subject: "Deployment failed on {{ inventory_hostname }}"
            body: |
              Deployment of {{ app_name }} version {{ app_version }} failed.
              System has been rolled back to previous version.
              
              Error details: {{ ansible_failed_result.msg }}
              Host: {{ inventory_hostname }}
              Time: {{ ansible_date_time.iso8601 }}
        
        - name: Fail the play
          fail:
            msg: "Deployment failed and rollback completed"
```

## 📚 Tài liệu Tham khảo
- [Ansible Playbooks Guide](https://docs.ansible.com/ansible/latest/user_guide/playbooks.html)
- [Ansible Roles Guide](https://docs.ansible.com/ansible/latest/user_guide/playbooks_reuse_roles.html)
- [Jinja2 Template Documentation](https://jinja.palletsprojects.com/)
- [Ansible Galaxy](https://galaxy.ansible.com/)

## 🔍 Câu hỏi Ôn tập
1. Thứ tự precedence của variables trong Ansible?
2. Khi nào nên sử dụng Roles thay vì Playbooks?
3. Cách handle errors và rollback trong deployments?
4. Best practices cho organization của large Ansible projects?
5. Strategies để test và validate Ansible playbooks?

---
*Chú thích: Mastering playbooks và roles là chìa khóa để xây dựng automation workflows mạnh mẽ và maintainable.*
