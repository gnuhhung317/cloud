# Ansible Labs - Hands-on Practice

## 🎯 Mục tiêu Labs
- Thực hành cài đặt và cấu hình Ansible
- Viết playbooks và roles thực tế
- Triển khai automation workflows hoàn chỉnh

## Lab 1: Ansible Setup và Basic Commands

### Prerequisites
```bash
# Kiểm tra Python version
python3 --version

# Cài đặt Ansible (Ubuntu/Debian)
sudo apt update
sudo apt install ansible

# Hoặc sử dụng pip
pip3 install ansible

# Kiểm tra installation
ansible --version
```

### Lab 1.1: SSH Key Setup
```bash
# Generate SSH key pair
ssh-keygen -t ed25519 -C "ansible-lab@viettel.com" -f ~/.ssh/ansible_lab

# Copy key to managed nodes
ssh-copy-id -i ~/.ssh/ansible_lab.pub user@192.168.1.100
ssh-copy-id -i ~/.ssh/ansible_lab.pub user@192.168.1.101

# Test connection
ssh -i ~/.ssh/ansible_lab user@192.168.1.100
```

### Lab 1.2: Basic Inventory Setup
```ini
# inventory/hosts
[webservers]
web01 ansible_host=192.168.1.100
web02 ansible_host=192.168.1.101

[databases]
db01 ansible_host=192.168.1.200

[all:vars]
ansible_user=ansible
ansible_ssh_private_key_file=~/.ssh/ansible_lab
ansible_ssh_common_args='-o StrictHostKeyChecking=no'
```

### Lab 1.3: Basic Ad-hoc Commands
```bash
# Test connectivity
ansible all -i inventory/hosts -m ping

# Get system information
ansible all -i inventory/hosts -m setup

# Check disk space
ansible all -i inventory/hosts -m shell -a "df -h"

# Install package
ansible webservers -i inventory/hosts -m package -a "name=nginx state=present" --become

# Check service status
ansible webservers -i inventory/hosts -m service -a "name=nginx state=started" --become
```

## Lab 2: First Playbook

### Lab 2.1: Basic Web Server Playbook
```yaml
# playbooks/webserver-basic.yml
---
- name: Configure Basic Web Server
  hosts: webservers
  become: yes
  
  vars:
    http_port: 80
    server_name: "{{ inventory_hostname }}"
  
  tasks:
    - name: Update package cache
      package:
        name: "*"
        state: latest
        update_cache: yes
      when: ansible_os_family == "Debian"
    
    - name: Install nginx
      package:
        name: nginx
        state: present
    
    - name: Start and enable nginx
      service:
        name: nginx
        state: started
        enabled: yes
    
    - name: Create custom index page
      copy:
        content: |
          <!DOCTYPE html>
          <html>
          <head>
              <title>{{ server_name }}</title>
          </head>
          <body>
              <h1>Welcome to {{ server_name }}</h1>
              <p>Server managed by Ansible</p>
              <p>Date: {{ ansible_date_time.iso8601 }}</p>
          </body>
          </html>
        dest: /var/www/html/index.html
        owner: www-data
        group: www-data
        mode: '0644'
      notify: restart nginx
    
    - name: Configure firewall
      ufw:
        rule: allow
        port: "{{ http_port }}"
        proto: tcp
      when: ansible_os_family == "Debian"
  
  handlers:
    - name: restart nginx
      service:
        name: nginx
        state: restarted
```

### Lab 2.2: Run Playbook
```bash
# Syntax check
ansible-playbook --syntax-check playbooks/webserver-basic.yml

# Dry run
ansible-playbook -i inventory/hosts playbooks/webserver-basic.yml --check

# Execute playbook
ansible-playbook -i inventory/hosts playbooks/webserver-basic.yml

# Test result
curl http://192.168.1.100
curl http://192.168.1.101
```

## Lab 3: Advanced Playbook với Variables

### Lab 3.1: Variable Files
```yaml
# group_vars/webservers.yml
---
nginx_user: www-data
nginx_worker_processes: 2
nginx_worker_connections: 1024

sites:
  - name: default
    server_name: "{{ inventory_hostname }}"
    document_root: /var/www/html
  - name: api
    server_name: "api.{{ inventory_hostname }}"
    document_root: /var/www/api

ssl_certificate: /etc/ssl/certs/server.crt
ssl_private_key: /etc/ssl/private/server.key
```

```yaml
# host_vars/web01.yml
---
server_role: primary
nginx_worker_processes: 4
enable_ssl: true
```

```yaml
# host_vars/web02.yml
---
server_role: secondary
nginx_worker_processes: 2
enable_ssl: false
```

### Lab 3.2: Advanced Playbook với Templates
```yaml
# playbooks/webserver-advanced.yml
---
- name: Advanced Web Server Configuration
  hosts: webservers
  become: yes
  
  tasks:
    - name: Install nginx và dependencies
      package:
        name:
          - nginx
          - openssl
        state: present
    
    - name: Create nginx directories
      file:
        path: "{{ item }}"
        state: directory
        owner: root
        group: root
        mode: '0755'
      loop:
        - /etc/nginx/sites-available
        - /etc/nginx/sites-enabled
        - /var/log/nginx
    
    - name: Generate nginx main configuration
      template:
        src: nginx.conf.j2
        dest: /etc/nginx/nginx.conf
        owner: root
        group: root
        mode: '0644'
        backup: yes
      notify: reload nginx
    
    - name: Generate virtual host configurations
      template:
        src: vhost.conf.j2
        dest: "/etc/nginx/sites-available/{{ item.name }}"
        owner: root
        group: root
        mode: '0644'
      loop: "{{ sites }}"
      notify: reload nginx
    
    - name: Enable virtual hosts
      file:
        src: "/etc/nginx/sites-available/{{ item.name }}"
        dest: "/etc/nginx/sites-enabled/{{ item.name }}"
        state: link
      loop: "{{ sites }}"
      notify: reload nginx
    
    - name: Create document roots
      file:
        path: "{{ item.document_root }}"
        state: directory
        owner: "{{ nginx_user }}"
        group: "{{ nginx_user }}"
        mode: '0755'
      loop: "{{ sites }}"
    
    - name: Generate SSL certificate (self-signed)
      command: >
        openssl req -new -newkey rsa:2048 -days 365 -nodes -x509
        -keyout {{ ssl_private_key }}
        -out {{ ssl_certificate }}
        -subj "/C=VN/ST=HN/L=Hanoi/O=Viettel/CN={{ inventory_hostname }}"
      args:
        creates: "{{ ssl_certificate }}"
      when: enable_ssl | default(false)
    
    - name: Set SSL file permissions
      file:
        path: "{{ item.path }}"
        owner: root
        group: root
        mode: "{{ item.mode }}"
      loop:
        - { path: "{{ ssl_certificate }}", mode: "0644" }
        - { path: "{{ ssl_private_key }}", mode: "0600" }
      when: enable_ssl | default(false)
    
    - name: Start and enable nginx
      service:
        name: nginx
        state: started
        enabled: yes
  
  handlers:
    - name: reload nginx
      service:
        name: nginx
        state: reloaded
```

### Lab 3.3: Nginx Templates
```nginx
# templates/nginx.conf.j2
user {{ nginx_user }};
worker_processes {{ nginx_worker_processes }};
pid /run/nginx.pid;

events {
    worker_connections {{ nginx_worker_connections }};
    use epoll;
    multi_accept on;
}

http {
    # Basic Settings
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    server_tokens off;

    # MIME
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log;

    # Gzip
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript 
               application/javascript application/xml+rss application/json;

    # Virtual Host Configs
    include /etc/nginx/sites-enabled/*;
}
```

```nginx
# templates/vhost.conf.j2
server {
    listen 80;
    server_name {{ item.server_name }};
    root {{ item.document_root }};
    index index.html index.htm;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

{% if enable_ssl | default(false) %}
    # SSL Configuration
    listen 443 ssl http2;
    ssl_certificate {{ ssl_certificate }};
    ssl_certificate_key {{ ssl_private_key }};
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # Redirect HTTP to HTTPS
    if ($scheme != "https") {
        return 301 https://$server_name$request_uri;
    }
{% endif %}

    # Main location
    location / {
        try_files $uri $uri/ =404;
    }

    # Deny access to hidden files
    location ~ /\. {
        deny all;
    }

    # Security.txt
    location /.well-known/security.txt {
        return 301 https://{{ item.server_name }}/security.txt;
    }

    # Health check
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
```

## Lab 4: Roles Development

### Lab 4.1: Create Role Structure
```bash
# Create role using ansible-galaxy
ansible-galaxy init roles/webserver
ansible-galaxy init roles/common
ansible-galaxy init roles/monitoring

# Alternative: manual creation
mkdir -p roles/webserver/{tasks,handlers,templates,files,vars,defaults,meta}
```

### Lab 4.2: Common Role
```yaml
# roles/common/tasks/main.yml
---
- name: Update package cache
  package:
    name: "*"
    state: latest
    update_cache: yes
  when: update_packages | default(false)

- name: Install common packages
  package:
    name: "{{ common_packages }}"
    state: present

- name: Configure timezone
  timezone:
    name: "{{ system_timezone }}"

- name: Configure NTP
  template:
    src: ntp.conf.j2
    dest: /etc/ntp.conf
    backup: yes
  notify: restart ntp

- name: Create application user
  user:
    name: "{{ app_user }}"
    group: "{{ app_group }}"
    system: yes
    shell: /bin/bash
    home: "{{ app_home }}"
    create_home: yes

- name: Configure sudoers
  lineinfile:
    path: /etc/sudoers
    line: "{{ app_user }} ALL=(ALL) NOPASSWD: /bin/systemctl"
    validate: 'visudo -cf %s'
```

```yaml
# roles/common/defaults/main.yml
---
common_packages:
  - curl
  - wget
  - unzip
  - git
  - htop
  - vim

system_timezone: "Asia/Ho_Chi_Minh"
ntp_servers:
  - 0.pool.ntp.org
  - 1.pool.ntp.org

app_user: appuser
app_group: appuser
app_home: /opt/app

update_packages: false
```

### Lab 4.3: WebServer Role
```yaml
# roles/webserver/tasks/main.yml
---
- name: Include OS-specific variables
  include_vars: "{{ ansible_os_family }}.yml"

- name: Install web server packages
  include_tasks: install.yml

- name: Configure web server
  include_tasks: configure.yml

- name: Setup SSL certificates
  include_tasks: ssl.yml
  when: enable_ssl | default(false)

- name: Configure virtual hosts
  include_tasks: vhosts.yml

- name: Start web server service
  service:
    name: "{{ webserver_service }}"
    state: started
    enabled: yes
```

```yaml
# roles/webserver/tasks/install.yml
---
- name: Install web server
  package:
    name: "{{ webserver_packages }}"
    state: present

- name: Install SSL tools
  package:
    name: "{{ ssl_packages }}"
    state: present
  when: enable_ssl | default(false)
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
  loop: "{{ webserver_directories }}"

- name: Generate main configuration
  template:
    src: "{{ webserver_main_config_template }}"
    dest: "{{ webserver_main_config }}"
    owner: root
    group: root
    mode: '0644'
    backup: yes
  notify: restart webserver

- name: Remove default site
  file:
    path: "{{ webserver_default_site }}"
    state: absent
  notify: restart webserver
```

```yaml
# roles/webserver/vars/Debian.yml
---
webserver_packages:
  - nginx
  - nginx-extras

ssl_packages:
  - openssl

webserver_service: nginx
webserver_user: www-data
webserver_group: www-data

webserver_directories:
  - /etc/nginx/sites-available
  - /etc/nginx/sites-enabled
  - /var/log/nginx

webserver_main_config: /etc/nginx/nginx.conf
webserver_main_config_template: nginx.conf.j2
webserver_default_site: /etc/nginx/sites-enabled/default
```

### Lab 4.4: Site Playbook Using Roles
```yaml
# site.yml
---
- name: Configure all servers
  hosts: all
  become: yes
  
  roles:
    - common

- name: Configure web servers
  hosts: webservers
  become: yes
  
  roles:
    - webserver
  
  vars:
    enable_ssl: true
    virtual_hosts:
      - name: default
        server_name: "{{ inventory_hostname }}"
        document_root: /var/www/html
      - name: api
        server_name: "api.{{ inventory_hostname }}"
        document_root: /var/www/api

- name: Configure database servers
  hosts: databases
  become: yes
  
  roles:
    - common
    - database
```

## Lab 5: Error Handling và Testing

### Lab 5.1: Robust Playbook với Error Handling
```yaml
# playbooks/robust-deployment.yml
---
- name: Robust Application Deployment
  hosts: webservers
  become: yes
  serial: 1  # Rolling deployment
  
  vars:
    app_name: "myapp"
    app_version: "1.2.3"
    app_url: "https://releases.example.com/{{ app_name }}-{{ app_version }}.tar.gz"
    deploy_path: "/opt/{{ app_name }}"
    backup_path: "/backups"
  
  pre_tasks:
    - name: Validate required variables
      assert:
        that:
          - app_name is defined and app_name != ""
          - app_version is defined and app_version != ""
          - app_url is defined and app_url != ""
        fail_msg: "Required variables not defined"
    
    - name: Check disk space
      shell: df -h {{ deploy_path }} | tail -1 | awk '{print $5}' | sed 's/%//'
      register: disk_usage
      failed_when: disk_usage.stdout|int > 80
      tags: [pre-check]
    
    - name: Test connectivity to release server
      uri:
        url: "{{ app_url }}"
        method: HEAD
        status_code: 200
      tags: [pre-check]
  
  tasks:
    - name: Application deployment block
      block:
        - name: Create backup directory
          file:
            path: "{{ backup_path }}"
            state: directory
            mode: '0755'
        
        - name: Stop application service
          service:
            name: "{{ app_name }}"
            state: stopped
          ignore_errors: yes
        
        - name: Create application backup
          archive:
            path: "{{ deploy_path }}"
            dest: "{{ backup_path }}/{{ app_name }}-{{ ansible_date_time.epoch }}.tar.gz"
          when: ansible_stat.stat.exists
          vars:
            ansible_stat: "{{ ansible_check_path.stat }}"
        
        - name: Check if application directory exists
          stat:
            path: "{{ deploy_path }}"
          register: ansible_check_path
        
        - name: Download application package
          get_url:
            url: "{{ app_url }}"
            dest: "/tmp/{{ app_name }}-{{ app_version }}.tar.gz"
            timeout: 30
          register: download_result
        
        - name: Extract application
          unarchive:
            src: "/tmp/{{ app_name }}-{{ app_version }}.tar.gz"
            dest: "{{ deploy_path | dirname }}"
            remote_src: yes
            owner: "{{ app_user | default('root') }}"
            group: "{{ app_group | default('root') }}"
        
        - name: Update configuration
          template:
            src: app.conf.j2
            dest: "{{ deploy_path }}/config/app.conf"
          when: deploy_path is directory
        
        - name: Start application service
          service:
            name: "{{ app_name }}"
            state: started
        
        - name: Wait for application to be ready
          uri:
            url: "http://localhost:{{ app_port | default(8080) }}/health"
            method: GET
            status_code: 200
          register: health_check
          until: health_check.status == 200
          retries: 30
          delay: 10
      
      rescue:
        - name: Log deployment failure
          debug:
            msg: "Deployment failed: {{ ansible_failed_result.msg }}"
        
        - name: Stop failed application
          service:
            name: "{{ app_name }}"
            state: stopped
          ignore_errors: yes
        
        - name: Find latest backup
          shell: ls -t {{ backup_path }}/{{ app_name }}-*.tar.gz | head -1
          register: latest_backup
          ignore_errors: yes
        
        - name: Restore from backup
          unarchive:
            src: "{{ latest_backup.stdout }}"
            dest: "{{ deploy_path | dirname }}"
            remote_src: yes
          when: latest_backup.stdout is defined and latest_backup.stdout != ""
        
        - name: Start application with old version
          service:
            name: "{{ app_name }}"
            state: started
          ignore_errors: yes
        
        - name: Send failure notification
          mail:
            to: "ops-team@viettel.com"
            subject: "Deployment failed on {{ inventory_hostname }}"
            body: |
              Deployment of {{ app_name }} version {{ app_version }} failed on {{ inventory_hostname }}.
              System has been rolled back to previous version.
              
              Error details: {{ ansible_failed_result.msg }}
              Timestamp: {{ ansible_date_time.iso8601 }}
          delegate_to: localhost
          run_once: true
        
        - name: Fail the play
          fail:
            msg: "Deployment failed and rollback completed"
      
      always:
        - name: Cleanup temporary files
          file:
            path: "/tmp/{{ app_name }}-{{ app_version }}.tar.gz"
            state: absent
        
        - name: Log deployment attempt
          lineinfile:
            path: /var/log/deployments.log
            line: "{{ ansible_date_time.iso8601 }} - {{ app_name }} {{ app_version }} deployment {{ 'completed' if ansible_failed_task is not defined else 'failed' }} on {{ inventory_hostname }}"
            create: yes
```

### Lab 5.2: Testing với Molecule
```bash
# Install molecule
pip install molecule[docker]

# Initialize molecule in role
cd roles/webserver
molecule init scenario default --driver-name docker

# Run molecule tests
molecule test
```

```yaml
# roles/webserver/molecule/default/molecule.yml
---
dependency:
  name: galaxy
driver:
  name: docker
platforms:
  - name: instance
    image: ubuntu:20.04
    pre_build_image: true
    privileged: true
    command: /lib/systemd/systemd
    volumes:
      - /sys/fs/cgroup:/sys/fs/cgroup:ro
    capabilities:
      - SYS_ADMIN
provisioner:
  name: ansible
  inventory:
    host_vars:
      instance:
        enable_ssl: false
verifier:
  name: ansible
```

```yaml
# roles/webserver/molecule/default/converge.yml
---
- name: Converge
  hosts: all
  become: true
  
  pre_tasks:
    - name: Update apt cache
      apt:
        update_cache: yes
      when: ansible_os_family == "Debian"
  
  roles:
    - role: webserver
```

```yaml
# roles/webserver/molecule/default/verify.yml
---
- name: Verify
  hosts: all
  gather_facts: false
  
  tasks:
    - name: Check if nginx is installed
      package:
        name: nginx
        state: present
      check_mode: yes
      register: nginx_installed
      failed_when: nginx_installed.changed
    
    - name: Check if nginx service is running
      service:
        name: nginx
        state: started
      check_mode: yes
      register: nginx_service
      failed_when: nginx_service.changed
    
    - name: Test HTTP response
      uri:
        url: http://localhost
        method: GET
        status_code: 200
      register: http_response
    
    - name: Verify HTTP response content
      assert:
        that:
          - "'nginx' in http_response.content.lower() or 'welcome' in http_response.content.lower()"
        fail_msg: "HTTP response doesn't contain expected content"
```

## Lab 6: Ansible Vault

### Lab 6.1: Create Encrypted Variables
```bash
# Create vault file
ansible-vault create group_vars/production/vault.yml

# Edit vault file
ansible-vault edit group_vars/production/vault.yml

# Encrypt existing file
ansible-vault encrypt secrets.yml

# View encrypted file
ansible-vault view vault.yml
```

```yaml
# group_vars/production/vault.yml (sau khi decrypt)
---
vault_database_password: "super_secret_password_123"
vault_api_key: "abcd1234567890efghij"
vault_ssl_private_key: |
  -----BEGIN PRIVATE KEY-----
  MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC7...
  -----END PRIVATE KEY-----
```

### Lab 6.2: Use Vault Variables
```yaml
# group_vars/production/vars.yml (unencrypted)
---
database_host: "prod-db.internal"
database_user: "app_user"
database_password: "{{ vault_database_password }}"

api_endpoint: "https://api.production.com"
api_key: "{{ vault_api_key }}"

ssl_private_key_content: "{{ vault_ssl_private_key }}"
```

### Lab 6.3: Run Playbook với Vault
```bash
# Prompt for vault password
ansible-playbook -i inventory/production site.yml --ask-vault-pass

# Use password file
echo "vault_password" > .vault_pass
chmod 600 .vault_pass
ansible-playbook -i inventory/production site.yml --vault-password-file .vault_pass

# Use multiple vault passwords
ansible-playbook -i inventory/production site.yml --vault-id prod@prompt --vault-id dev@.vault_pass_dev
```

## Lab Exercises

### Exercise 1: Multi-tier Application Deployment
Triển khai một ứng dụng web 3-tier (web, app, database) sử dụng Ansible.

### Exercise 2: Rolling Updates
Implement rolling update strategy cho web servers với zero downtime.

### Exercise 3: Configuration Drift Detection
Tạo playbook để detect và fix configuration drift.

### Exercise 4: Disaster Recovery
Tạo automation cho backup và restore procedures.

## 📚 Additional Resources
- [Ansible Documentation](https://docs.ansible.com/)
- [Ansible Galaxy](https://galaxy.ansible.com/)
- [Molecule Testing Framework](https://molecule.readthedocs.io/)
- [Ansible Best Practices](https://docs.ansible.com/ansible/latest/user_guide/playbooks_best_practices.html)

---
*Chú thích: Các labs này được thiết kế để áp dụng trong môi trường thực tế, có thể điều chỉnh theo infrastructure hiện có.*
