# Module 4: Quản lý Cơ sở Dữ liệu (PostgreSQL, MongoDB, Oracle, MySQL)

## 🎯 Mục tiêu Module
Nắm vững kỹ năng quản trị cơ sở dữ liệu quan hệ và NoSQL, đảm bảo hệ thống hoạt động ổn định, hiệu quả và bảo mật tại Viettel IDC.

## 📋 Nội dung Chính

### PostgreSQL (30% trọng số)
#### 1. Installation & Configuration
- **Installation**: từ package và source code
- **Configuration**: postgresql.conf, pg_hba.conf
- **Memory tuning**: shared_buffers, work_mem
- **Connection management**: max_connections, pooling

#### 2. Database Administration
- **User management**: roles, privileges, security
- **Backup & Recovery**: pg_dump, pg_restore, PITR
- **Replication**: streaming, logical replication
- **Monitoring**: pg_stat_*, log analysis

#### 3. Performance Optimization
- **Query optimization**: EXPLAIN, indexing strategies
- **Maintenance**: VACUUM, ANALYZE, REINDEX
- **Partitioning**: table partitioning strategies
- **Extensions**: PostGIS, pg_stat_statements

### MySQL/MariaDB (25% trọng số)
#### 1. Installation & Setup
- **Installation**: MySQL 8.0, MariaDB 10.x
- **Configuration**: my.cnf tuning
- **Storage engines**: InnoDB optimization
- **Security**: user management, SSL

#### 2. Operations
- **Backup strategies**: mysqldump, Percona XtraBackup
- **Replication**: master-slave, master-master
- **High availability**: MySQL Cluster, Galera
- **Monitoring**: performance_schema, slow query log

### MongoDB (25% trọng số)
#### 1. NoSQL Fundamentals
- **Document model**: collections, documents, BSON
- **Installation**: standalone, replica sets
- **Configuration**: mongod.conf, security
- **Indexing**: single field, compound, text indexes

#### 2. Operations & Scaling
- **Backup & Restore**: mongodump, mongorestore
- **Replica sets**: primary-secondary setup
- **Sharding**: horizontal scaling strategies
- **Monitoring**: mongostat, profiler, MongoDB Compass

### Oracle (20% trọng số)
#### 1. Basic Administration
- **Installation**: Oracle Database 19c
- **Instance management**: startup, shutdown, initialization
- **Tablespace management**: creation, resizing
- **User management**: schemas, privileges

#### 2. Backup & Recovery
- **RMAN**: backup strategies, recovery scenarios
- **Data Guard**: standby database setup
- **Export/Import**: expdp, impdp utilities
- **Flashback**: technologies và use cases

## 🛠️ Kỹ năng Thực hành

### PostgreSQL Labs
1. **Database Setup & Configuration**
   ```sql
   -- Create database and user
   CREATE DATABASE production_db;
   CREATE USER app_user WITH ENCRYPTED PASSWORD 'secure_password';
   GRANT ALL PRIVILEGES ON DATABASE production_db TO app_user;
   
   -- Performance tuning
   ALTER SYSTEM SET shared_buffers = '256MB';
   ALTER SYSTEM SET effective_cache_size = '1GB';
   ALTER SYSTEM SET maintenance_work_mem = '64MB';
   SELECT pg_reload_conf();
   ```

2. **Backup & Recovery**
   ```bash
   # Full backup
   pg_dump -h localhost -U postgres -d production_db -f backup.sql
   
   # Restore
   psql -h localhost -U postgres -d production_db -f backup.sql
   
   # Point-in-time recovery setup
   # Enable WAL archiving in postgresql.conf
   archive_mode = on
   archive_command = 'cp %p /backup/archive/%f'
   ```

3. **Replication Setup**
   ```bash
   # Master configuration
   echo "wal_level = replica" >> postgresql.conf
   echo "max_wal_senders = 3" >> postgresql.conf
   echo "host replication replica 192.168.1.100/32 md5" >> pg_hba.conf
   
   # Slave setup
   pg_basebackup -h master_ip -D /var/lib/postgresql/data -U replica -W
   ```

### MySQL Labs
1. **Performance Optimization**
   ```sql
   -- InnoDB configuration
   SET GLOBAL innodb_buffer_pool_size = 1073741824; -- 1GB
   SET GLOBAL innodb_log_file_size = 268435456; -- 256MB
   
   -- Query optimization
   EXPLAIN SELECT * FROM orders WHERE customer_id = 12345;
   CREATE INDEX idx_customer_id ON orders(customer_id);
   
   -- Slow query analysis
   SET GLOBAL slow_query_log = 'ON';
   SET GLOBAL long_query_time = 2;
   ```

2. **Replication Setup**
   ```sql
   -- Master configuration
   [mysqld]
   server-id = 1
   log-bin = mysql-bin
   binlog-format = ROW
   
   -- Create replication user
   CREATE USER 'replica'@'%' IDENTIFIED BY 'password';
   GRANT REPLICATION SLAVE ON *.* TO 'replica'@'%';
   FLUSH PRIVILEGES;
   
   -- Slave setup
   CHANGE MASTER TO
     MASTER_HOST='master_ip',
     MASTER_USER='replica',
     MASTER_PASSWORD='password',
     MASTER_LOG_FILE='mysql-bin.000001',
     MASTER_LOG_POS=154;
   START SLAVE;
   ```

### MongoDB Labs
1. **Replica Set Configuration**
   ```javascript
   // Initialize replica set
   rs.initiate({
     _id: "rs0",
     members: [
       { _id: 0, host: "mongo1:27017" },
       { _id: 1, host: "mongo2:27017" },
       { _id: 2, host: "mongo3:27017" }
     ]
   });
   
   // Check status
   rs.status();
   ```

2. **Indexing và Performance**
   ```javascript
   // Create indexes
   db.users.createIndex({ "email": 1 }, { unique: true });
   db.orders.createIndex({ "customer_id": 1, "order_date": -1 });
   
   // Query optimization
   db.orders.find({ customer_id: 12345 }).explain("executionStats");
   
   // Aggregation pipeline
   db.orders.aggregate([
     { $match: { status: "completed" } },
     { $group: { _id: "$customer_id", total: { $sum: "$amount" } } },
     { $sort: { total: -1 } }
   ]);
   ```

### Oracle Labs
1. **RMAN Backup Strategy**
   ```sql
   -- Configure RMAN
   RMAN TARGET /
   CONFIGURE RETENTION POLICY TO REDUNDANCY 2;
   CONFIGURE DEFAULT DEVICE TYPE TO DISK;
   
   -- Full backup
   BACKUP DATABASE PLUS ARCHIVELOG;
   
   -- Incremental backup
   BACKUP INCREMENTAL LEVEL 1 DATABASE;
   
   -- Recovery scenario
   RESTORE DATABASE;
   RECOVER DATABASE;
   ALTER DATABASE OPEN;
   ```

## 📊 Monitoring Scripts

### PostgreSQL Monitoring
```sql
-- Active connections
SELECT count(*) as active_connections 
FROM pg_stat_activity 
WHERE state = 'active';

-- Database size
SELECT pg_size_pretty(pg_database_size('production_db'));

-- Top queries by execution time
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;
```

### MySQL Monitoring
```sql
-- Connection status
SHOW STATUS LIKE 'Threads_connected';

-- InnoDB status
SHOW ENGINE INNODB STATUS;

-- Slow queries
SELECT * FROM mysql.slow_log 
WHERE start_time > DATE_SUB(NOW(), INTERVAL 1 HOUR);
```

### MongoDB Monitoring
```javascript
// Database stats
db.stats();

// Collection stats
db.orders.stats();

// Current operations
db.currentOp();

// Profiler analysis
db.setProfilingLevel(2);
db.system.profile.find().limit(5).sort({ ts: -1 }).pretty();
```

## 📚 Tài liệu Tham khảo

### PostgreSQL
- PostgreSQL Official Documentation
- PostgreSQL Administration Cookbook
- High Performance PostgreSQL

### MySQL
- MySQL Official Documentation
- High Performance MySQL
- MySQL Troubleshooting Guide

### MongoDB
- MongoDB Manual
- MongoDB: The Definitive Guide
- MongoDB Performance Best Practices

### Oracle
- Oracle Database Administrator's Guide
- Oracle RMAN Backup and Recovery
- Oracle Performance Tuning Guide

## 🎓 Chứng chỉ Liên quan
- **PostgreSQL**: PostgreSQL Certified Professional
- **MySQL**: Oracle MySQL Database Administrator
- **MongoDB**: MongoDB Certified Developer/DBA
- **Oracle**: Oracle Certified Professional (OCP)

## ⏱️ Thời gian Học: 2-3 tuần
- Tuần 1: PostgreSQL + MySQL administration
- Tuần 2: MongoDB + NoSQL concepts
- Tuần 3: Oracle basics + integration scenarios

## 🔗 Chuyển sang Module tiếp theo
Với kiến thức database administration, bạn sẵn sàng cho **Module 5: Automation Tools**.
