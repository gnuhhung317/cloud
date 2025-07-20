# Database Security và Compliance Theory
# Lý thuyết Bảo mật và Tuân thủ Cơ sở Dữ liệu

## 📚 Mục lục
1. [Database Security Fundamentals](#1-database-security-fundamentals)
2. [Authentication và Authorization](#2-authentication-và-authorization)
3. [Encryption và Data Protection](#3-encryption-và-data-protection)
4. [Auditing và Monitoring](#4-auditing-và-monitoring)
5. [Data Masking và Anonymization](#5-data-masking-và-anonymization)
6. [Compliance Frameworks](#6-compliance-frameworks)
7. [Network Security](#7-network-security)
8. [Backup Security](#8-backup-security)
9. [Database Hardening](#9-database-hardening)
10. [Incident Response](#10-incident-response)

---

## 1. Database Security Fundamentals

### 1.1 CIA Triad trong Database Security

#### Confidentiality (Tính Bảo mật):
```
┌─────────────────────────────────────────┐
│           Confidentiality               │
├─────────────────────────────────────────┤
│ • Access Controls                       │
│ • Encryption at Rest                    │
│ • Encryption in Transit                 │
│ • Data Masking                          │
│ • User Authentication                   │
│ • Role-based Access Control (RBAC)      │
└─────────────────────────────────────────┘
```

#### Integrity (Tính Toàn vẹn):
```sql
-- PostgreSQL data integrity
-- Check constraints
ALTER TABLE employees 
ADD CONSTRAINT chk_salary CHECK (salary > 0);

-- Foreign key constraints
ALTER TABLE orders 
ADD CONSTRAINT fk_customer_id 
FOREIGN KEY (customer_id) REFERENCES customers(id);

-- Unique constraints
ALTER TABLE users 
ADD CONSTRAINT uk_email UNIQUE (email);

-- Triggers for audit trail
CREATE OR REPLACE FUNCTION audit_trigger()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO audit_log (table_name, operation, old_values, new_values, timestamp)
    VALUES (TG_TABLE_NAME, TG_OP, row_to_json(OLD), row_to_json(NEW), NOW());
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER audit_employees
AFTER INSERT OR UPDATE OR DELETE ON employees
FOR EACH ROW EXECUTE FUNCTION audit_trigger();
```

#### Availability (Tính Khả dụng):
```bash
# PostgreSQL High Availability setup
# Master-Slave replication configuration

# Master server postgresql.conf
wal_level = replica
max_wal_senders = 3
checkpoint_segments = 8
wal_keep_segments = 8

# Slave server recovery.conf
standby_mode = 'on'
primary_conninfo = 'host=master_ip port=5432 user=replicator'
trigger_file = '/tmp/postgresql.trigger'
```

### 1.2 Threat Modeling cho Database

#### Common Database Threats:
```
┌─────────────────────────────────────────┐
│             Threat Landscape            │
├─────────────────────────────────────────┤
│ 1. SQL Injection                        │
│ 2. Privilege Escalation                 │
│ 3. Data Breach                          │
│ 4. Insider Threats                      │
│ 5. Denial of Service (DoS)              │
│ 6. Weak Authentication                  │
│ 7. Unencrypted Communications           │
│ 8. Backup Theft                         │
│ 9. Configuration Weaknesses             │
│ 10. Social Engineering                  │
└─────────────────────────────────────────┘
```

---

## 2. Authentication và Authorization

### 2.1 Authentication Methods

#### PostgreSQL Authentication:
```bash
# pg_hba.conf configuration
# TYPE  DATABASE        USER            ADDRESS                 METHOD

# Local connections
local   all             postgres                                peer
local   all             all                                     md5

# IPv4 local connections
host    all             all             127.0.0.1/32            md5
host    all             all             0.0.0.0/0               md5

# SSL connections
hostssl all             all             0.0.0.0/0               md5

# LDAP authentication
host    all             all             0.0.0.0/0               ldap ldapserver=ldap.company.com ldapbasedn="dc=company,dc=com"

# Certificate authentication
hostssl all             all             0.0.0.0/0               cert clientcert=1
```

#### MySQL Authentication:
```sql
-- Create user with strong authentication
CREATE USER 'app_user'@'%' IDENTIFIED WITH caching_sha2_password BY 'StrongP@ssw0rd123';

-- Multi-factor authentication
ALTER USER 'admin'@'%' ADD FACTOR IDENTIFIED WITH authentication_fido BY 'fido_token';

-- Account locking after failed attempts
CREATE USER 'limited_user'@'%' 
IDENTIFIED BY 'password'
FAILED_LOGIN_ATTEMPTS 3 
PASSWORD_LOCK_TIME 2;

-- SSL requirement
ALTER USER 'secure_user'@'%' REQUIRE SSL;
```

#### MongoDB Authentication:
```javascript
// Enable authentication in mongod.conf
security:
  authorization: enabled

// Create admin user
use admin
db.createUser({
  user: "admin",
  pwd: "strongpassword",
  roles: [
    { role: "userAdminAnyDatabase", db: "admin" },
    { role: "readWriteAnyDatabase", db: "admin" }
  ]
})

// LDAP authentication
security:
  authorization: enabled
  ldap:
    servers: "ldap.company.com"
    bind:
      method: "simple"
      saslAuthd: false
    transportSecurity: "tls"
    userToDNMapping: '[{match: "(.+)", ldapQuery: "ou=users,dc=company,dc=com??sub?(uid={0})"}]'
```

### 2.2 Role-Based Access Control (RBAC)

#### PostgreSQL RBAC:
```sql
-- Create roles hierarchy
CREATE ROLE db_readonly;
CREATE ROLE db_readwrite;
CREATE ROLE db_admin;

-- Grant permissions to roles
GRANT SELECT ON ALL TABLES IN SCHEMA public TO db_readonly;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO db_readwrite;
GRANT ALL PRIVILEGES ON DATABASE production TO db_admin;

-- Create users and assign roles
CREATE USER analyst PASSWORD 'secure_pass';
GRANT db_readonly TO analyst;

CREATE USER developer PASSWORD 'secure_pass';
GRANT db_readwrite TO developer;

-- Row Level Security (RLS)
ALTER TABLE sensitive_data ENABLE ROW LEVEL SECURITY;

CREATE POLICY user_data_policy ON sensitive_data
    FOR ALL TO app_user
    USING (user_id = current_setting('app.current_user_id')::integer);
```

#### Oracle RBAC:
```sql
-- Create roles
CREATE ROLE app_read_role;
CREATE ROLE app_write_role;
CREATE ROLE app_admin_role;

-- Grant system privileges
GRANT CREATE SESSION TO app_read_role;
GRANT CREATE SESSION, CREATE TABLE, CREATE PROCEDURE TO app_write_role;

-- Grant object privileges
GRANT SELECT ON hr.employees TO app_read_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON hr.employees TO app_write_role;

-- Create users and assign roles
CREATE USER app_user IDENTIFIED BY "Complex_Pass123";
GRANT app_read_role TO app_user;

-- Virtual Private Database (VPD)
CREATE OR REPLACE FUNCTION hr_security_policy(
    schema_var IN VARCHAR2,
    table_var IN VARCHAR2
) RETURN VARCHAR2 IS
BEGIN
    RETURN 'department_id = SYS_CONTEXT(''USERENV'', ''CLIENT_IDENTIFIER'')';
END;
/

BEGIN
    DBMS_RLS.ADD_POLICY(
        object_schema => 'HR',
        object_name => 'EMPLOYEES',
        policy_name => 'HR_POLICY',
        function_schema => 'HR',
        policy_function => 'HR_SECURITY_POLICY'
    );
END;
/
```

---

## 3. Encryption và Data Protection

### 3.1 Encryption at Rest

#### PostgreSQL Transparent Data Encryption:
```bash
# Initialize encrypted cluster
initdb -D /var/lib/postgresql/data --data-checksums --auth-local=peer --auth-host=md5 --encryption

# File-level encryption using dm-crypt
cryptsetup luksFormat /dev/sdb
cryptsetup luksOpen /dev/sdb encrypted_disk
mkfs.ext4 /dev/mapper/encrypted_disk
mount /dev/mapper/encrypted_disk /var/lib/postgresql/data
```

#### MySQL Encryption:
```sql
-- Enable encryption at rest
SET GLOBAL innodb_file_per_table = ON;

-- Create encrypted table
CREATE TABLE sensitive_data (
    id INT PRIMARY KEY,
    ssn VARCHAR(11),
    credit_card VARCHAR(16)
) ENCRYPTION='Y';

-- Encrypt existing table
ALTER TABLE existing_table ENCRYPTION='Y';

-- Keyring plugin configuration
[mysqld]
early-plugin-load=keyring_file.so
keyring_file_data=/var/lib/mysql-keyring/keyring
```

#### MongoDB Encryption:
```yaml
# mongod.conf with encryption
security:
  enableEncryption: true
  encryptionCipherMode: AES256-CBC
  encryptionKeyFile: /path/to/encryption/key

# Field-level encryption
const clientEncryption = new ClientEncryption(keyVault, {
  keyVaultNamespace: 'encryption.__keyVault',
  kmsProviders: {
    local: {
      key: localMasterKey
    }
  }
});

// Encrypt field
const encryptedSSN = await clientEncryption.encrypt(ssn, {
  algorithm: 'AEAD_AES_256_CBC_HMAC_SHA_512-Deterministic',
  keyId: dataEncryptionKey
});
```

### 3.2 Encryption in Transit

#### SSL/TLS Configuration:
```bash
# PostgreSQL SSL setup
# Generate certificates
openssl genrsa -des3 -out server.key 1024
openssl rsa -in server.key -out server.key
openssl req -new -key server.key -days 3650 -out server.crt -x509

# postgresql.conf
ssl = on
ssl_cert_file = 'server.crt'
ssl_key_file = 'server.key'
ssl_ca_file = 'ca.crt'
ssl_crl_file = 'ca.crl'

# Force SSL connections
# pg_hba.conf
hostssl all all 0.0.0.0/0 md5
```

```sql
-- MySQL SSL configuration
[mysqld]
ssl-ca=/path/to/ca.pem
ssl-cert=/path/to/server-cert.pem
ssl-key=/path/to/server-key.pem

-- Require SSL for user
ALTER USER 'secure_user'@'%' REQUIRE SSL;

-- Check SSL status
SHOW STATUS LIKE 'Ssl_cipher';
```

---

## 4. Auditing và Monitoring

### 4.1 Database Auditing

#### PostgreSQL Auditing với pgAudit:
```sql
-- Install pgAudit extension
CREATE EXTENSION pgaudit;

-- Configure auditing
SET pgaudit.log = 'write, ddl';
SET pgaudit.log_catalog = off;
SET pgaudit.log_client = on;
SET pgaudit.log_level = log;
SET pgaudit.log_parameter = on;
SET pgaudit.log_statement_once = off;

-- Audit specific operations
SET pgaudit.log = 'read, write';
SELECT * FROM sensitive_table;
INSERT INTO audit_table VALUES (1, 'test');
```

#### MySQL Audit:
```sql
-- Enable audit log plugin
INSTALL PLUGIN audit_log SONAME 'audit_log.so';

-- Configure audit logging
SET GLOBAL audit_log_file = '/var/log/mysql/audit.log';
SET GLOBAL audit_log_format = 'JSON';
SET GLOBAL audit_log_policy = 'ALL';

-- Audit specific users
SET GLOBAL audit_log_include_accounts = 'admin@%,app_user@%';

-- Check audit log status
SHOW STATUS LIKE 'audit_log%';
```

#### Oracle Unified Auditing:
```sql
-- Enable unified auditing
AUDIT ALL STATEMENTS;
AUDIT ALL PRIVILEGES;

-- Create audit policy
CREATE AUDIT POLICY sensitive_data_policy
ACTIONS SELECT, INSERT, UPDATE, DELETE
ON hr.employees
WHEN 'SYS_CONTEXT(''USERENV'', ''IP_ADDRESS'') NOT LIKE ''192.168.%''';

-- Enable audit policy
AUDIT POLICY sensitive_data_policy;

-- Query audit records
SELECT dbusername, action_name, object_name, event_timestamp
FROM unified_audit_trail
WHERE event_timestamp > SYSDATE - 1;
```

### 4.2 Real-time Monitoring

#### Security Monitoring Scripts:
```bash
#!/bin/bash
# PostgreSQL security monitoring

# Check for suspicious login attempts
psql -c "
SELECT usename, address, state, backend_start 
FROM pg_stat_activity 
WHERE state = 'active' 
AND backend_start > NOW() - INTERVAL '1 hour';"

# Monitor failed authentication attempts
grep "FATAL:.*authentication failed" /var/log/postgresql/postgresql.log | tail -20

# Check for privilege escalation
psql -c "
SELECT grantee, privilege_type, table_name 
FROM information_schema.role_table_grants 
WHERE privilege_type = 'ALL PRIVILEGES';"
```

```python
# MongoDB security monitoring
import pymongo
from datetime import datetime, timedelta

def monitor_mongodb_security():
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    
    # Check for failed authentication
    admin_db = client.admin
    
    # Monitor slow operations
    for db_name in client.list_database_names():
        db = client[db_name]
        db.set_profiling_level(2, slow_ms=100)
        
        # Get recent slow operations
        profile_data = db.system.profile.find({
            'ts': {'$gte': datetime.now() - timedelta(hours=1)}
        }).sort('ts', -1).limit(10)
        
        for operation in profile_data:
            print(f"Slow operation: {operation}")

if __name__ == "__main__":
    monitor_mongodb_security()
```

---

## 5. Data Masking và Anonymization

### 5.1 Static Data Masking

#### PostgreSQL Data Masking:
```sql
-- Install anonymizer extension
CREATE EXTENSION anon CASCADE;

-- Initialize extension
SELECT anon.init();

-- Define masking rules
SECURITY LABEL FOR anon ON COLUMN customers.name 
IS 'MASKED WITH FUNCTION anon.fake_first_name()';

SECURITY LABEL FOR anon ON COLUMN customers.email 
IS 'MASKED WITH FUNCTION anon.fake_email()';

SECURITY LABEL FOR anon ON COLUMN customers.ssn 
IS 'MASKED WITH FUNCTION anon.random_string(11)';

-- Create masked view
CREATE MATERIALIZED VIEW customers_masked AS 
SELECT anon.anonymize_table('customers');

-- Custom masking functions
CREATE OR REPLACE FUNCTION mask_credit_card(original_value TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN 'XXXX-XXXX-XXXX-' || RIGHT(original_value, 4);
END;
$$ LANGUAGE plpgsql;
```

#### MySQL Data Masking:
```sql
-- Create masking functions
DELIMITER $$
CREATE FUNCTION mask_ssn(ssn VARCHAR(11))
RETURNS VARCHAR(11)
READS SQL DATA
DETERMINISTIC
BEGIN
    RETURN CONCAT('XXX-XX-', SUBSTRING(ssn, -4));
END$$

CREATE FUNCTION mask_email(email VARCHAR(255))
RETURNS VARCHAR(255)
READS SQL DATA
DETERMINISTIC
BEGIN
    RETURN CONCAT(
        SUBSTRING(email, 1, 2),
        '***@',
        SUBSTRING_INDEX(email, '@', -1)
    );
END$$
DELIMITER ;

-- Create masked view
CREATE VIEW customers_masked AS
SELECT 
    id,
    mask_ssn(ssn) AS ssn,
    mask_email(email) AS email,
    CASE 
        WHEN LENGTH(name) > 2 THEN CONCAT(LEFT(name, 2), REPEAT('*', LENGTH(name)-2))
        ELSE REPEAT('*', LENGTH(name))
    END AS name
FROM customers;
```

### 5.2 Dynamic Data Masking

#### Oracle Data Redaction:
```sql
-- Create redaction policy for credit card
BEGIN
    DBMS_REDACT.ADD_POLICY(
        object_schema => 'HR',
        object_name => 'EMPLOYEES',
        column_name => 'CREDIT_CARD',
        policy_name => 'CC_REDACTION',
        function_type => DBMS_REDACT.PARTIAL,
        function_parameters => 'VVVVFVVVVFVVVVFVVVV,VVVV-VVVV-VVVV-,*,1,12',
        expression => 'SYS_CONTEXT(''USERENV'',''SESSION_USER'') != ''ADMIN'''
    );
END;
/

-- Redact SSN
BEGIN
    DBMS_REDACT.ADD_POLICY(
        object_schema => 'HR',
        object_name => 'EMPLOYEES',
        column_name => 'SSN',
        policy_name => 'SSN_REDACTION',
        function_type => DBMS_REDACT.REGEXP,
        regexp_pattern => '(\d{3})-(\d{2})-(\d{4})',
        regexp_replace_string => 'XXX-XX-\3',
        expression => 'SYS_CONTEXT(''USERENV'',''SESSION_USER'') NOT IN (''HR_ADMIN'', ''PAYROLL'')'
    );
END;
/
```

---

## 6. Compliance Frameworks

### 6.1 GDPR Compliance

#### Data Subject Rights Implementation:
```sql
-- Right to Access (Data Portability)
CREATE OR REPLACE FUNCTION get_user_data(user_email VARCHAR)
RETURNS JSON AS $$
DECLARE
    user_data JSON;
BEGIN
    SELECT json_build_object(
        'personal_info', (SELECT row_to_json(t) FROM (
            SELECT name, email, phone FROM users WHERE email = user_email
        ) t),
        'orders', (SELECT json_agg(row_to_json(t)) FROM (
            SELECT order_id, order_date, amount FROM orders 
            WHERE customer_email = user_email
        ) t),
        'preferences', (SELECT row_to_json(t) FROM (
            SELECT * FROM user_preferences WHERE email = user_email
        ) t)
    ) INTO user_data;
    
    RETURN user_data;
END;
$$ LANGUAGE plpgsql;

-- Right to Erasure (Right to be Forgotten)
CREATE OR REPLACE FUNCTION anonymize_user_data(user_email VARCHAR)
RETURNS BOOLEAN AS $$
BEGIN
    -- Anonymize personal data instead of deletion for referential integrity
    UPDATE users SET 
        name = 'ANONYMIZED_' || id,
        email = 'anonymized_' || id || '@deleted.com',
        phone = NULL,
        address = NULL,
        updated_at = NOW()
    WHERE email = user_email;
    
    -- Log the anonymization
    INSERT INTO gdpr_actions (action_type, user_email, timestamp)
    VALUES ('ANONYMIZATION', user_email, NOW());
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- Data Retention Policy
CREATE OR REPLACE FUNCTION enforce_retention_policy()
RETURNS VOID AS $$
BEGIN
    -- Delete old log entries (7 years retention)
    DELETE FROM audit_logs 
    WHERE created_at < NOW() - INTERVAL '7 years';
    
    -- Anonymize old user sessions (2 years retention)
    UPDATE user_sessions SET
        ip_address = '0.0.0.0',
        user_agent = 'ANONYMIZED'
    WHERE created_at < NOW() - INTERVAL '2 years';
END;
$$ LANGUAGE plpgsql;
```

### 6.2 SOX Compliance

#### Segregation of Duties:
```sql
-- Oracle SOX compliance setup
-- Create segregated roles
CREATE ROLE sox_developer;
CREATE ROLE sox_dba;
CREATE ROLE sox_auditor;
CREATE ROLE sox_business_user;

-- Developer permissions (no production access)
GRANT CREATE SESSION TO sox_developer;
GRANT SELECT, INSERT, UPDATE, DELETE ON dev_schema.* TO sox_developer;

-- DBA permissions (infrastructure only)
GRANT DBA TO sox_dba;
REVOKE SELECT, INSERT, UPDATE, DELETE ON financial_data FROM sox_dba;

-- Auditor permissions (read-only)
GRANT SELECT ON ALL TABLES IN SCHEMA audit TO sox_auditor;
GRANT SELECT ON dba_audit_trail TO sox_auditor;

-- Change management procedure
CREATE OR REPLACE PROCEDURE submit_change_request(
    p_change_description VARCHAR2,
    p_sql_statements CLOB,
    p_requested_by VARCHAR2
) IS
BEGIN
    INSERT INTO change_requests (
        id, description, sql_code, requested_by, 
        status, created_date
    ) VALUES (
        change_req_seq.NEXTVAL, p_change_description, 
        p_sql_statements, p_requested_by, 
        'PENDING_APPROVAL', SYSDATE
    );
    
    -- Send notification to approvers
    send_approval_notification(change_req_seq.CURRVAL);
END;
/
```

### 6.3 PCI DSS Compliance

#### Cardholder Data Protection:
```sql
-- PostgreSQL PCI DSS implementation
-- Encrypt cardholder data
CREATE EXTENSION pgcrypto;

-- Create function to encrypt credit card data
CREATE OR REPLACE FUNCTION encrypt_cc(cc_number TEXT, key_id TEXT)
RETURNS BYTEA AS $$
BEGIN
    RETURN pgp_sym_encrypt(cc_number, key_id);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create function to decrypt credit card data
CREATE OR REPLACE FUNCTION decrypt_cc(encrypted_cc BYTEA, key_id TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN pgp_sym_decrypt(encrypted_cc, key_id);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Store encrypted credit card data
CREATE TABLE payment_cards (
    id SERIAL PRIMARY KEY,
    cardholder_name VARCHAR(100),
    encrypted_cc_number BYTEA,
    cc_last_four CHAR(4), -- For display purposes
    expiry_date DATE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Insert encrypted data
INSERT INTO payment_cards (cardholder_name, encrypted_cc_number, cc_last_four)
VALUES (
    'John Doe',
    encrypt_cc('4532123456789012', 'encryption_key'),
    '9012'
);

-- Access control for cardholder data
CREATE ROLE pci_authorized_user;
GRANT SELECT (id, cardholder_name, cc_last_four, expiry_date) ON payment_cards TO pci_authorized_user;
GRANT EXECUTE ON FUNCTION decrypt_cc(BYTEA, TEXT) TO pci_authorized_user;

-- Audit trail for cardholder data access
CREATE OR REPLACE FUNCTION audit_cc_access()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO cardholder_data_access_log (
        user_name, table_name, operation, timestamp, ip_address
    ) VALUES (
        current_user, TG_TABLE_NAME, TG_OP, NOW(), 
        inet_client_addr()
    );
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER cc_access_audit
AFTER SELECT ON payment_cards
FOR EACH STATEMENT EXECUTE FUNCTION audit_cc_access();
```

---

## 7. Network Security

### 7.1 Database Firewall

#### PostgreSQL Network Security:
```bash
# pg_hba.conf - restrictive configuration
# TYPE  DATABASE        USER            ADDRESS                 METHOD

# Local connections only for admin
local   all             postgres                                peer

# Application servers only
host    app_db          app_user        192.168.1.10/32         md5
host    app_db          app_user        192.168.1.11/32         md5

# Read-only access from reporting server
host    app_db          readonly_user   192.168.1.20/32         md5

# SSL required for remote admin
hostssl all             dba_user        10.0.0.0/8              cert clientcert=1

# Reject all other connections
host    all             all             0.0.0.0/0               reject
```

#### Database Proxy/Firewall Implementation:
```python
# Python database firewall proxy
import socket
import threading
import re
import logging

class DatabaseFirewall:
    def __init__(self, listen_port, target_host, target_port):
        self.listen_port = listen_port
        self.target_host = target_host
        self.target_port = target_port
        self.blocked_patterns = [
            r'DROP\s+TABLE',
            r'DELETE\s+FROM\s+\w+\s*;',  # Delete without WHERE
            r'UPDATE\s+\w+\s+SET.*\s*;', # Update without WHERE
            r'UNION\s+SELECT',           # SQL injection pattern
            r'OR\s+1\s*=\s*1',          # SQL injection pattern
        ]
    
    def is_query_allowed(self, query):
        """Check if SQL query is allowed"""
        query_upper = query.upper()
        
        for pattern in self.blocked_patterns:
            if re.search(pattern, query_upper, re.IGNORECASE):
                logging.warning(f"Blocked malicious query: {query}")
                return False
        
        return True
    
    def handle_client(self, client_socket):
        """Handle client connection"""
        try:
            # Connect to actual database
            db_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            db_socket.connect((self.target_host, self.target_port))
            
            while True:
                # Receive data from client
                data = client_socket.recv(4096)
                if not data:
                    break
                
                # Analyze SQL query (simplified)
                query = data.decode('utf-8', errors='ignore')
                
                if self.is_query_allowed(query):
                    # Forward to database
                    db_socket.send(data)
                    
                    # Get response from database
                    response = db_socket.recv(4096)
                    client_socket.send(response)
                else:
                    # Send error response
                    error_msg = "Query blocked by security policy"
                    client_socket.send(error_msg.encode())
                    
        except Exception as e:
            logging.error(f"Connection error: {e}")
        finally:
            client_socket.close()
            db_socket.close()
    
    def start(self):
        """Start the firewall proxy"""
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('0.0.0.0', self.listen_port))
        server.listen(5)
        
        logging.info(f"Database firewall listening on port {self.listen_port}")
        
        while True:
            client_socket, addr = server.accept()
            logging.info(f"Connection from {addr}")
            
            client_thread = threading.Thread(
                target=self.handle_client,
                args=(client_socket,)
            )
            client_thread.start()

# Usage
if __name__ == "__main__":
    firewall = DatabaseFirewall(5433, 'localhost', 5432)
    firewall.start()
```

### 7.2 VPN và Private Networks

#### Database Access through VPN:
```bash
# OpenVPN configuration for database access
# server.conf
port 1194
proto udp
dev tun
ca ca.crt
cert server.crt
key server.key
dh dh2048.pem

# Push routes for database subnets
push "route 192.168.10.0 255.255.255.0"  # Database subnet
push "route 192.168.20.0 255.255.255.0"  # Backup subnet

# Client specific configuration
client-config-dir ccd

# Database admin access only
# ccd/db_admin
iroute 192.168.10.0 255.255.255.0
ifconfig-push 10.8.0.10 10.8.0.11
```

---

## 8. Backup Security

### 8.1 Encrypted Backups

#### PostgreSQL Encrypted Backup:
```bash
#!/bin/bash
# Secure PostgreSQL backup script

DB_NAME="production"
BACKUP_DIR="/secure_backup"
ENCRYPTION_KEY="/keys/backup.key"
DATE=$(date +%Y%m%d_%H%M%S)

# Create encrypted backup
pg_dump $DB_NAME | \
gpg --cipher-algo AES256 --compress-algo 2 --symmetric \
    --passphrase-file $ENCRYPTION_KEY \
    --output $BACKUP_DIR/backup_${DATE}.sql.gpg

# Verify backup integrity
if [ $? -eq 0 ]; then
    echo "Backup completed successfully: backup_${DATE}.sql.gpg"
    
    # Calculate checksum
    sha256sum $BACKUP_DIR/backup_${DATE}.sql.gpg > $BACKUP_DIR/backup_${DATE}.sha256
    
    # Send to secure remote location
    rsync -avz --delete $BACKUP_DIR/ backup_server:/secure_backups/
else
    echo "Backup failed!" >&2
    exit 1
fi

# Clean up old backups (keep 30 days)
find $BACKUP_DIR -name "backup_*.sql.gpg" -mtime +30 -delete
```

#### MySQL Encrypted Backup:
```bash
#!/bin/bash
# MySQL encrypted backup with Percona XtraBackup

BACKUP_DIR="/encrypted_backups"
MYSQL_USER="backup_user"
MYSQL_PASSWORD="secure_password"
ENCRYPTION_KEY="MySecretKey123456"

# Create encrypted backup
xtrabackup --backup \
    --user=$MYSQL_USER \
    --password=$MYSQL_PASSWORD \
    --target-dir=$BACKUP_DIR/$(date +%Y%m%d) \
    --encrypt=AES256 \
    --encrypt-key=$ENCRYPTION_KEY \
    --compress

# Prepare backup for restore
xtrabackup --prepare \
    --target-dir=$BACKUP_DIR/$(date +%Y%m%d) \
    --decrypt=AES256 \
    --encrypt-key=$ENCRYPTION_KEY \
    --decompress
```

### 8.2 Backup Access Control

#### Backup Storage Security:
```bash
# Create dedicated backup user
sudo useradd -r -s /bin/false backup_service

# Set secure permissions on backup directory
sudo chown backup_service:backup_service /secure_backup
sudo chmod 700 /secure_backup

# SELinux contexts for backup security
sudo semanage fcontext -a -t admin_home_t "/secure_backup(/.*)?"
sudo restorecon -R /secure_backup

# Backup rotation with access logging
#!/bin/bash
LOG_FILE="/var/log/backup_access.log"

log_access() {
    echo "$(date): $1 accessed backup by $(whoami) from $(who am i | awk '{print $NF}')" >> $LOG_FILE
}

# Function to restore from backup
restore_backup() {
    local backup_file=$1
    local requester=$(whoami)
    
    # Log access attempt
    log_access "RESTORE_REQUEST: $backup_file"
    
    # Verify authorization
    if [[ "$requester" != "dba" && "$requester" != "backup_admin" ]]; then
        echo "Unauthorized restore attempt by $requester" >> $LOG_FILE
        exit 1
    fi
    
    # Decrypt and restore
    gpg --decrypt --passphrase-file /keys/backup.key $backup_file | psql production
    
    log_access "RESTORE_COMPLETED: $backup_file"
}
```

---

## 9. Database Hardening

### 9.1 Installation Hardening

#### PostgreSQL Hardening Checklist:
```bash
# 1. Secure installation
# Remove default databases and users
psql -c "DROP DATABASE IF EXISTS template0;"
psql -c "DROP USER IF EXISTS postgres;" # After creating admin user

# 2. File system permissions
chmod 700 /var/lib/postgresql/data
chown postgres:postgres /var/lib/postgresql/data

# 3. Network configuration
# postgresql.conf
listen_addresses = '192.168.1.10'  # Specific IP only
port = 5433  # Non-default port
ssl = on
ssl_ciphers = 'HIGH:!aNULL'
ssl_prefer_server_ciphers = on

# 4. Connection limits
max_connections = 100
superuser_reserved_connections = 3

# 5. Logging configuration
log_destination = 'stderr'
logging_collector = on
log_directory = '/var/log/postgresql'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_connections = on
log_disconnections = on
log_line_prefix = '%t [%p-%l] %q%u@%d '
log_statement = 'all'
```

#### MySQL Hardening:
```bash
# Run mysql_secure_installation
mysql_secure_installation

# Additional hardening in my.cnf
[mysqld]
# Network security
bind-address = 192.168.1.10
port = 3307
skip-networking = false
skip-show-database

# Access control
local-infile = 0
secure-file-priv = "/var/lib/mysql-files/"

# Logging
general_log = ON
general_log_file = /var/log/mysql/general.log
log_error = /var/log/mysql/error.log
slow_query_log = ON
slow_query_log_file = /var/log/mysql/slow.log

# Password validation
validate_password.policy = STRONG
validate_password.length = 12
validate_password.mixed_case_count = 1
validate_password.number_count = 1
validate_password.special_char_count = 1
```

### 9.2 Runtime Security

#### Database Parameter Security:
```sql
-- PostgreSQL security parameters
-- Prevent function creation
SET default_transaction_read_only = on; -- For read-only users

-- Control statement timeout
SET statement_timeout = '30s';

-- Log all DDL statements
SET log_statement = 'ddl';

-- Prevent loading external libraries
SET shared_preload_libraries = '';
```

```sql
-- MySQL security settings
-- Disable dangerous functions
SET GLOBAL general_log = 'ON';

-- Control query execution time
SET GLOBAL max_execution_time = 30000; -- 30 seconds

-- Disable local file loading
SET GLOBAL local_infile = 0;

-- Control resource usage
SET GLOBAL max_user_connections = 10;
SET GLOBAL max_connections = 200;
```

---

## 10. Incident Response

### 10.1 Security Incident Detection

#### Automated Alert System:
```python
# Database security monitoring system
import psycopg2
import smtplib
from email.mime.text import MIMEText
import time
import logging

class DatabaseSecurityMonitor:
    def __init__(self, db_config, alert_config):
        self.db_config = db_config
        self.alert_config = alert_config
        self.setup_logging()
    
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('/var/log/db_security.log'),
                logging.StreamHandler()
            ]
        )
    
    def check_failed_logins(self):
        """Monitor failed login attempts"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COUNT(*) as failed_attempts
                FROM pg_stat_activity 
                WHERE state = 'authentication failed'
                AND backend_start > NOW() - INTERVAL '5 minutes'
            """)
            
            failed_count = cursor.fetchone()[0]
            
            if failed_count > 5:  # Threshold
                self.send_alert(
                    f"HIGH: {failed_count} failed login attempts in last 5 minutes",
                    "multiple_failed_logins"
                )
            
            conn.close()
            
        except Exception as e:
            logging.error(f"Error checking failed logins: {e}")
    
    def check_privilege_escalation(self):
        """Monitor privilege changes"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT grantee, privilege_type, table_name
                FROM information_schema.role_table_grants 
                WHERE grantor != grantee
                AND is_grantable = 'YES'
            """)
            
            grants = cursor.fetchall()
            
            # Check for new SUPERUSER grants
            cursor.execute("""
                SELECT rolname FROM pg_roles 
                WHERE rolsuper = true 
                AND rolname NOT IN ('postgres', 'rds_superuser')
            """)
            
            superusers = cursor.fetchall()
            
            if len(superusers) > 1:  # More than expected
                self.send_alert(
                    f"WARNING: Unexpected superuser accounts: {superusers}",
                    "privilege_escalation"
                )
            
            conn.close()
            
        except Exception as e:
            logging.error(f"Error checking privileges: {e}")
    
    def check_suspicious_queries(self):
        """Monitor for suspicious SQL patterns"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            suspicious_patterns = [
                "UNION.*SELECT",
                "DROP.*TABLE",
                "DELETE.*FROM.*WHERE.*1=1",
                "OR.*1=1"
            ]
            
            for pattern in suspicious_patterns:
                cursor.execute(f"""
                    SELECT query, usename, client_addr, query_start
                    FROM pg_stat_activity 
                    WHERE query ~* '{pattern}'
                    AND query_start > NOW() - INTERVAL '1 minute'
                """)
                
                suspicious_queries = cursor.fetchall()
                
                if suspicious_queries:
                    self.send_alert(
                        f"CRITICAL: Suspicious SQL detected: {suspicious_queries}",
                        "sql_injection_attempt"
                    )
            
            conn.close()
            
        except Exception as e:
            logging.error(f"Error checking queries: {e}")
    
    def send_alert(self, message, alert_type):
        """Send security alert"""
        try:
            msg = MIMEText(f"""
            Database Security Alert
            
            Type: {alert_type}
            Time: {time.strftime('%Y-%m-%d %H:%M:%S')}
            Message: {message}
            
            Please investigate immediately.
            """)
            
            msg['Subject'] = f'DB Security Alert: {alert_type}'
            msg['From'] = self.alert_config['from_email']
            msg['To'] = self.alert_config['to_email']
            
            server = smtplib.SMTP(self.alert_config['smtp_server'])
            server.starttls()
            server.login(
                self.alert_config['smtp_user'],
                self.alert_config['smtp_password']
            )
            server.send_message(msg)
            server.quit()
            
            logging.warning(f"Security alert sent: {alert_type}")
            
        except Exception as e:
            logging.error(f"Failed to send alert: {e}")
    
    def run_monitoring(self):
        """Main monitoring loop"""
        while True:
            try:
                self.check_failed_logins()
                self.check_privilege_escalation()
                self.check_suspicious_queries()
                
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                logging.error(f"Monitoring error: {e}")
                time.sleep(60)

# Configuration
db_config = {
    'host': 'localhost',
    'database': 'production',
    'user': 'monitor_user',
    'password': 'monitor_password'
}

alert_config = {
    'smtp_server': 'smtp.company.com',
    'smtp_user': 'alerts@company.com',
    'smtp_password': 'smtp_password',
    'from_email': 'db-security@company.com',
    'to_email': 'security-team@company.com'
}

# Start monitoring
if __name__ == "__main__":
    monitor = DatabaseSecurityMonitor(db_config, alert_config)
    monitor.run_monitoring()
```

### 10.2 Incident Response Procedures

#### Database Security Incident Playbook:
```bash
#!/bin/bash
# Database incident response script

INCIDENT_ID=$(date +%Y%m%d_%H%M%S)
LOG_DIR="/var/log/incidents"
INCIDENT_LOG="$LOG_DIR/incident_$INCIDENT_ID.log"

log_action() {
    echo "$(date): $1" >> $INCIDENT_LOG
    echo "$1"
}

# Function 1: Isolate compromised database
isolate_database() {
    local db_name=$1
    
    log_action "ISOLATION: Starting isolation of database $db_name"
    
    # Block new connections
    psql -d $db_name -c "
        ALTER DATABASE $db_name 
        SET default_transaction_read_only = true;
        
        SELECT pg_terminate_backend(pg_stat_activity.pid)
        FROM pg_stat_activity
        WHERE datname = '$db_name'
        AND pid <> pg_backend_pid();
    "
    
    # Update pg_hba.conf to block access
    sed -i "s/host.*$db_name.*allow/host $db_name all 0.0.0.0\/0 reject/g" /etc/postgresql/*/main/pg_hba.conf
    systemctl reload postgresql
    
    log_action "ISOLATION: Database $db_name isolated successfully"
}

# Function 2: Collect forensic evidence
collect_evidence() {
    local evidence_dir="/forensics/incident_$INCIDENT_ID"
    mkdir -p $evidence_dir
    
    log_action "EVIDENCE: Starting evidence collection"
    
    # Database logs
    cp /var/log/postgresql/*.log $evidence_dir/
    
    # Configuration files
    cp /etc/postgresql/*/main/*.conf $evidence_dir/
    
    # Current connections
    psql -c "SELECT * FROM pg_stat_activity" > $evidence_dir/active_connections.txt
    
    # Recent queries
    psql -c "SELECT * FROM pg_stat_statements ORDER BY last_exec DESC LIMIT 100" > $evidence_dir/recent_queries.txt
    
    # System information
    ps aux > $evidence_dir/processes.txt
    netstat -tulpn > $evidence_dir/network_connections.txt
    
    # Create evidence hash
    find $evidence_dir -type f -exec sha256sum {} \; > $evidence_dir/evidence_hashes.txt
    
    log_action "EVIDENCE: Evidence collected in $evidence_dir"
}

# Function 3: Restore from backup
restore_clean_backup() {
    local backup_date=$1
    local db_name=$2
    
    log_action "RESTORE: Starting restore from backup dated $backup_date"
    
    # Stop database
    systemctl stop postgresql
    
    # Backup current data (for forensics)
    mv /var/lib/postgresql/*/main /var/lib/postgresql/forensics_$INCIDENT_ID
    
    # Restore from clean backup
    pg_restore -C -d template1 /backups/backup_$backup_date.dump
    
    # Start database
    systemctl start postgresql
    
    log_action "RESTORE: Database restored from backup"
}

# Function 4: Security hardening post-incident
post_incident_hardening() {
    log_action "HARDENING: Applying post-incident security measures"
    
    # Force password reset for all users
    psql -c "
        UPDATE pg_authid 
        SET rolpassword = NULL 
        WHERE rolname NOT IN ('postgres', 'replication');
    "
    
    # Enable additional logging
    psql -c "
        ALTER SYSTEM SET log_statement = 'all';
        ALTER SYSTEM SET log_connections = on;
        ALTER SYSTEM SET log_disconnections = on;
        SELECT pg_reload_conf();
    "
    
    # Update firewall rules
    iptables -I INPUT -p tcp --dport 5432 -j LOG --log-prefix "PostgreSQL: "
    
    log_action "HARDENING: Security hardening completed"
}

# Main incident response flow
case "$1" in
    "isolate")
        isolate_database $2
        ;;
    "evidence")
        collect_evidence
        ;;
    "restore")
        restore_clean_backup $2 $3
        ;;
    "harden")
        post_incident_hardening
        ;;
    "full_response")
        isolate_database $2
        collect_evidence
        post_incident_hardening
        ;;
    *)
        echo "Usage: $0 {isolate|evidence|restore|harden|full_response} [parameters]"
        exit 1
        ;;
esac

log_action "INCIDENT: Response action '$1' completed for incident $INCIDENT_ID"
```

---

## 📊 Security Monitoring Dashboard

### Database Security Metrics:
```sql
-- PostgreSQL security dashboard queries
-- 1. Connection monitoring
SELECT 
    client_addr,
    COUNT(*) as connection_count,
    COUNT(DISTINCT usename) as unique_users
FROM pg_stat_activity 
WHERE state = 'active'
GROUP BY client_addr
ORDER BY connection_count DESC;

-- 2. Failed authentication attempts
SELECT 
    DATE_TRUNC('hour', log_time) as hour,
    COUNT(*) as failed_attempts
FROM pg_log 
WHERE message LIKE '%authentication failed%'
AND log_time > NOW() - INTERVAL '24 hours'
GROUP BY hour
ORDER BY hour;

-- 3. Privilege usage
SELECT 
    schemaname,
    tablename,
    n_tup_ins + n_tup_upd + n_tup_del as total_changes
FROM pg_stat_user_tables 
WHERE n_tup_ins + n_tup_upd + n_tup_del > 0
ORDER BY total_changes DESC;

-- 4. Query performance anomalies
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    stddev_time
FROM pg_stat_statements 
WHERE stddev_time > mean_time * 2  -- High variance
ORDER BY stddev_time DESC;
```

## 📚 Tài liệu Tham khảo

### Security Standards:
- OWASP Database Security Cheat Sheet
- NIST Cybersecurity Framework
- ISO 27001 Database Security Controls
- CIS Database Security Benchmarks

### Compliance Frameworks:
- GDPR Technical and Organisational Measures
- SOX IT General Controls
- PCI DSS Data Protection Requirements
- HIPAA Security Rule

### Tools và Solutions:
- Database Activity Monitoring (DAM)
- Database Firewalls
- Data Loss Prevention (DLP)
- Security Information and Event Management (SIEM)

---

*Tài liệu này được thiết kế để đáp ứng các yêu cầu bảo mật database tại Viettel IDC với tiêu chuẩn enterprise và compliance quốc tế.*
