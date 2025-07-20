# Oracle Enterprise Theory
# Lý thuyết Oracle Doanh nghiệp

## 📚 Mục lục
1. [Kiến trúc Oracle Database](#1-kiến-trúc-oracle-database)
2. [Oracle Instance và Database](#2-oracle-instance-và-database)
3. [Memory Architecture](#3-memory-architecture)
4. [Storage Architecture](#4-storage-architecture)
5. [Oracle Processes](#5-oracle-processes)
6. [Transaction Management](#6-transaction-management)
7. [Backup và Recovery](#7-backup-và-recovery)
8. [Real Application Clusters (RAC)](#8-real-application-clusters-rac)
9. [Data Guard](#9-data-guard)
10. [Performance Tuning](#10-performance-tuning)

---

## 1. Kiến trúc Oracle Database

### 1.1 Tổng quan Kiến trúc

#### Oracle Database Architecture:
```
┌─────────────────────────────────────────────────────────┐
│                  Oracle Database                        │
│                                                         │
│  ┌─────────────────┐         ┌─────────────────────┐   │
│  │   Instance       │         │     Database        │   │
│  │                 │         │                     │   │
│  │  ┌─────────────┐│         │  ┌─────────────────┐│   │
│  │  │   Memory    ││         │  │   Data Files    ││   │
│  │  │ Structures  ││         │  │                 ││   │
│  │  └─────────────┘│         │  └─────────────────┘│   │
│  │                 │         │                     │   │
│  │  ┌─────────────┐│         │  ┌─────────────────┐│   │
│  │  │Background   ││         │  │  Control Files  ││   │
│  │  │Processes    ││         │  │                 ││   │
│  │  └─────────────┘│         │  └─────────────────┘│   │
│  │                 │         │                     │   │
│  └─────────────────┘         │  ┌─────────────────┐│   │
│                              │  │  Redo Log Files ││   │
│                              │  │                 ││   │
│                              │  └─────────────────┘│   │
│                              └─────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### 1.2 Thành phần Chính

#### Instance Components:
- **System Global Area (SGA)**: Vùng nhớ chia sẻ
- **Program Global Area (PGA)**: Vùng nhớ riêng của process
- **Background Processes**: Các tiến trình nền
- **Server Processes**: Tiến trình phục vụ user

#### Database Components:
- **Data Files**: Lưu trữ dữ liệu người dùng
- **Control Files**: Metadata về database
- **Redo Log Files**: Ghi lại transaction log

---

## 2. Oracle Instance và Database

### 2.1 Oracle Instance

#### Instance Startup Process:
```sql
-- Kiểm tra trạng thái instance
SELECT instance_name, status, database_status 
FROM v$instance;

-- Startup sequence
STARTUP NOMOUNT;  -- Đọc init.ora, tạo SGA
STARTUP MOUNT;    -- Đọc control files
STARTUP OPEN;     -- Mở data files

-- Manual startup process
STARTUP NOMOUNT;
ALTER DATABASE MOUNT;
ALTER DATABASE OPEN;
```

#### Initialization Parameters:
```sql
-- Xem các parameter quan trọng
SELECT name, value, isdefault 
FROM v$parameter 
WHERE name IN (
    'db_block_size',
    'sga_target',
    'pga_aggregate_target',
    'processes',
    'sessions'
);

-- Thay đổi parameter
ALTER SYSTEM SET sga_target = 2G SCOPE=BOTH;
ALTER SYSTEM SET pga_aggregate_target = 1G SCOPE=BOTH;
```

### 2.2 Database Startup States

#### Startup States Flow:
```
SHUTDOWN ──► NOMOUNT ──► MOUNT ──► OPEN
    ▲           │          │        │
    │           ▼          ▼        ▼
    └──── Parameters ── Control ── Data
              Only       Files     Files
```

---

## 3. Memory Architecture

### 3.1 System Global Area (SGA)

#### SGA Components:
```sql
-- Xem cấu trúc SGA
SELECT component, current_size/1024/1024 as size_mb
FROM v$sga_info;

-- Chi tiết các pool
SELECT pool, name, bytes/1024/1024 as size_mb
FROM v$sgastat
WHERE pool IS NOT NULL
ORDER BY pool, bytes DESC;
```

#### Shared Pool Structure:
```
┌─────────────────────────────────────────┐
│              Shared Pool                │
├─────────────────────────────────────────┤
│  ┌─────────────────┐ ┌───────────────┐ │
│  │ Library Cache   │ │ Data Dict     │ │
│  │ ┌─────────────┐ │ │ Cache         │ │
│  │ │SQL Area     │ │ │               │ │
│  │ │PL/SQL Area  │ │ └───────────────┘ │
│  │ │Control Str  │ │                   │
│  │ └─────────────┘ │                   │
│  └─────────────────┘                   │
├─────────────────────────────────────────┤
│              Result Cache               │
└─────────────────────────────────────────┘
```

#### Buffer Cache:
```sql
-- Buffer cache hit ratio
SELECT name, value
FROM v$sysstat
WHERE name IN (
    'db block gets',
    'consistent gets',
    'physical reads'
);

-- Calculate hit ratio
SELECT (1 - (phy.value / (cur.value + con.value))) * 100 as hit_ratio
FROM v$sysstat cur, v$sysstat con, v$sysstat phy
WHERE cur.name = 'db block gets'
  AND con.name = 'consistent gets'
  AND phy.name = 'physical reads';
```

### 3.2 Program Global Area (PGA)

#### PGA Components:
- **SQL Work Areas**: Sort, hash operations
- **Session Memory**: Cursor state, variables
- **Stack Space**: Local variables, parameters

```sql
-- PGA memory usage
SELECT name, value/1024/1024 as mb
FROM v$pgastat
WHERE name IN (
    'total PGA allocated',
    'total PGA used for auto workareas',
    'maximum PGA allocated'
);

-- PGA advice
SELECT pga_target_for_estimate/1024/1024 as target_mb,
       estd_pga_cache_hit_percentage,
       estd_overalloc_count
FROM v$pga_target_advice
ORDER BY pga_target_for_estimate;
```

---

## 4. Storage Architecture

### 4.1 Logical Storage

#### Tablespace Hierarchy:
```
Database
├── Tablespace (SYSTEM, SYSAUX, USERS, TEMP)
│   ├── Segment (Table, Index, Undo)
│   │   ├── Extent (Contiguous blocks)
│   │   │   └── Block (Smallest unit - 8KB default)
│   │   └── Extent
│   └── Segment
└── Tablespace
```

#### Tablespace Management:
```sql
-- Tạo tablespace
CREATE TABLESPACE data_ts
DATAFILE '/u01/oradata/orcl/data_ts01.dbf' SIZE 100M
AUTOEXTEND ON NEXT 10M MAXSIZE 1G
EXTENT MANAGEMENT LOCAL
SEGMENT SPACE MANAGEMENT AUTO;

-- Thêm datafile
ALTER TABLESPACE data_ts
ADD DATAFILE '/u01/oradata/orcl/data_ts02.dbf' SIZE 100M;

-- Resize datafile
ALTER DATABASE DATAFILE '/u01/oradata/orcl/data_ts01.dbf'
RESIZE 200M;

-- Kiểm tra tablespace usage
SELECT tablespace_name,
       bytes/1024/1024 as total_mb,
       maxbytes/1024/1024 as max_mb,
       (bytes-NVL(free_space,0))/1024/1024 as used_mb
FROM (
    SELECT tablespace_name, SUM(bytes) bytes, SUM(maxbytes) maxbytes
    FROM dba_data_files
    GROUP BY tablespace_name
) df
LEFT JOIN (
    SELECT tablespace_name, SUM(bytes) free_space
    FROM dba_free_space
    GROUP BY tablespace_name
) fs USING (tablespace_name);
```

### 4.2 Physical Storage

#### Control Files:
```sql
-- Xem location của control files
SELECT name FROM v$controlfile;

-- Backup control file
ALTER DATABASE BACKUP CONTROLFILE TO 
'/backup/control_backup.ctl';

-- Recreate control file script
ALTER DATABASE BACKUP CONTROLFILE TO TRACE AS
'/backup/recreate_controlfile.sql';
```

#### Redo Log Files:
```sql
-- Xem redo log groups
SELECT group#, thread#, sequence#, status, archived
FROM v$log;

-- Xem redo log members
SELECT group#, member, status
FROM v$logfile;

-- Add redo log group
ALTER DATABASE ADD LOGFILE GROUP 4
'/u01/oradata/orcl/redo04a.log' SIZE 50M;

-- Switch log file
ALTER SYSTEM SWITCH LOGFILE;

-- Check log switch frequency
SELECT TO_CHAR(first_time, 'YYYY-MM-DD HH24') as hour,
       COUNT(*) as switches
FROM v$log_history
WHERE first_time > SYSDATE - 7
GROUP BY TO_CHAR(first_time, 'YYYY-MM-DD HH24')
ORDER BY hour;
```

---

## 5. Oracle Processes

### 5.1 Background Processes

#### Core Background Processes:
```sql
-- Xem background processes
SELECT name, description
FROM v$bgprocess
WHERE paddr != '00'
ORDER BY name;
```

#### Process Details:

**Database Writer (DBW0-DBW9)**:
```sql
-- Check dirty buffers
SELECT dirty_buffers, db_block_gets, consistent_gets
FROM v$buffer_pool_statistics;

-- Monitor DBWR activity
SELECT name, value
FROM v$sysstat
WHERE name LIKE '%DBWR%';
```

**Log Writer (LGWR)**:
```sql
-- LGWR statistics
SELECT name, value
FROM v$sysstat
WHERE name LIKE '%redo%';

-- Redo generation rate
SELECT TO_CHAR(first_time, 'YYYY-MM-DD HH24:MI') as time,
       (blocks * block_size)/1024/1024 as mb_generated
FROM v$log_history
WHERE first_time > SYSDATE - 1
ORDER BY first_time;
```

**Checkpoint Process (CKPT)**:
```sql
-- Checkpoint information
SELECT checkpoint_change#, checkpoint_time
FROM v$database;

-- Incremental checkpoint target
SELECT name, value
FROM v$parameter
WHERE name = 'fast_start_mttr_target';
```

### 5.2 Server Processes

#### Dedicated vs Shared Server:
```sql
-- Check connection mode
SELECT server, COUNT(*) as connections
FROM v$session
WHERE username IS NOT NULL
GROUP BY server;

-- Shared server configuration
ALTER SYSTEM SET shared_servers = 5;
ALTER SYSTEM SET dispatchers = '(PROTOCOL=TCP)(DISPATCHERS=3)';
```

---

## 6. Transaction Management

### 6.1 ACID Properties trong Oracle

#### Atomicity - Tính Nguyên tử:
```sql
-- Transaction control
BEGIN
    INSERT INTO accounts (id, balance) VALUES (1, 1000);
    INSERT INTO accounts (id, balance) VALUES (2, 2000);
    
    -- Simulate error
    INSERT INTO accounts (id, balance) VALUES (1, 500); -- Duplicate key
EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        RAISE;
END;
/

-- Savepoint usage
SAVEPOINT before_update;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;

-- Rollback to savepoint if needed
ROLLBACK TO before_update;
```

#### Consistency - Tính Nhất quán:
```sql
-- Check constraint
ALTER TABLE accounts 
ADD CONSTRAINT chk_balance CHECK (balance >= 0);

-- Referential integrity
ALTER TABLE orders
ADD CONSTRAINT fk_customer
FOREIGN KEY (customer_id) REFERENCES customers(id);
```

#### Isolation - Tính Cô lập:
```sql
-- Set isolation level
ALTER SESSION SET ISOLATION_LEVEL = SERIALIZABLE;

-- Check lock information
SELECT object_name, oracle_username, locked_mode
FROM v$locked_object lo, dba_objects do, v$session s
WHERE lo.object_id = do.object_id
AND lo.session_id = s.sid;
```

#### Durability - Tính Bền vững:
```sql
-- Force commit to disk
COMMIT;

-- Check redo generation
SELECT name, value
FROM v$mystat ms, v$statname sn
WHERE ms.statistic# = sn.statistic#
AND sn.name = 'redo size';
```

### 6.2 Undo Management

#### Automatic Undo Management:
```sql
-- Create undo tablespace
CREATE UNDO TABLESPACE undotbs2
DATAFILE '/u01/oradata/orcl/undotbs02.dbf' SIZE 100M;

-- Switch undo tablespace
ALTER SYSTEM SET undo_tablespace = undotbs2;

-- Undo retention
ALTER SYSTEM SET undo_retention = 900; -- 15 minutes

-- Monitor undo usage
SELECT tablespace_name,
       status,
       (bytes/1024/1024) as size_mb,
       (maxbytes/1024/1024) as max_mb
FROM dba_data_files
WHERE tablespace_name LIKE 'UNDO%';

-- Check undo statistics
SELECT begin_time,
       end_time,
       undoblks,
       txncount,
       maxconcurrency
FROM v$undostat
WHERE begin_time > SYSDATE - 1
ORDER BY begin_time;
```

---

## 7. Backup và Recovery

### 7.1 RMAN (Recovery Manager)

#### RMAN Architecture:
```
┌─────────────────┐    ┌─────────────────┐
│   RMAN Client   │────│  Target DB      │
│                 │    │                 │
└─────────────────┘    └─────────────────┘
         │                       │
         │              ┌─────────────────┐
         └──────────────│  Recovery       │
                        │  Catalog DB     │
                        │  (Optional)     │
                        └─────────────────┘
```

#### RMAN Configuration:
```sql
-- Connect to RMAN
RMAN TARGET /

-- Configure retention policy
CONFIGURE RETENTION POLICY TO REDUNDANCY 2;
CONFIGURE RETENTION POLICY TO RECOVERY WINDOW OF 7 DAYS;

-- Configure backup optimization
CONFIGURE BACKUP OPTIMIZATION ON;
CONFIGURE CONTROLFILE AUTOBACKUP ON;

-- Configure channels
CONFIGURE DEVICE TYPE DISK PARALLELISM 2;
CONFIGURE CHANNEL DEVICE TYPE DISK FORMAT '/backup/rman/%U';

-- Show configuration
SHOW ALL;
```

#### Backup Strategies:
```sql
-- Full database backup
BACKUP DATABASE PLUS ARCHIVELOG;

-- Incremental backup level 0 (base)
BACKUP INCREMENTAL LEVEL 0 DATABASE;

-- Incremental backup level 1
BACKUP INCREMENTAL LEVEL 1 DATABASE;

-- Tablespace backup
BACKUP TABLESPACE users;

-- Backup specific datafile
BACKUP DATAFILE '/u01/oradata/orcl/users01.dbf';

-- Archive log backup
BACKUP ARCHIVELOG ALL DELETE INPUT;
```

#### Recovery Scenarios:
```sql
-- Complete database recovery
STARTUP MOUNT;
RESTORE DATABASE;
RECOVER DATABASE;
ALTER DATABASE OPEN;

-- Point-in-time recovery
STARTUP MOUNT;
RESTORE DATABASE UNTIL TIME "TO_DATE('2024-01-15 14:00:00','YYYY-MM-DD HH24:MI:SS')";
RECOVER DATABASE UNTIL TIME "TO_DATE('2024-01-15 14:00:00','YYYY-MM-DD HH24:MI:SS')";
ALTER DATABASE OPEN RESETLOGS;

-- Tablespace recovery
RESTORE TABLESPACE users;
RECOVER TABLESPACE users;

-- Block media recovery
RECOVER DATAFILE 4 BLOCK 123;
```

### 7.2 Data Pump

#### Export/Import Operations:
```bash
# Full database export
expdp system/password FULL=Y DIRECTORY=backup_dir DUMPFILE=full_db.dmp

# Schema export
expdp hr/password SCHEMAS=hr DIRECTORY=backup_dir DUMPFILE=hr_schema.dmp

# Table export
expdp hr/password TABLES=employees DIRECTORY=backup_dir DUMPFILE=employees.dmp

# Parallel export
expdp system/password FULL=Y PARALLEL=4 DIRECTORY=backup_dir DUMPFILE=full_db_%U.dmp

# Import with remap
impdp system/password DIRECTORY=backup_dir DUMPFILE=hr_schema.dmp \
      REMAP_SCHEMA=hr:hr_test REMAP_TABLESPACE=users:users_test
```

---

## 8. Real Application Clusters (RAC)

### 8.1 RAC Architecture

#### RAC Components:
```
┌─────────────────────────────────────────────────────────┐
│                    Oracle RAC                          │
│                                                         │
│  ┌─────────────┐              ┌─────────────────────┐   │
│  │   Node 1    │              │      Node 2         │   │
│  │             │              │                     │   │
│  │ ┌─────────┐ │              │ ┌─────────────────┐ │   │
│  │ │Instance1│ │◄────────────►│ │    Instance2    │ │   │
│  │ │         │ │              │ │                 │ │   │
│  │ └─────────┘ │              │ └─────────────────┘ │   │
│  └─────────────┘              └─────────────────────┘   │
│         │                              │               │
│         └──────────────┬───────────────┘               │
│                        │                               │
│              ┌─────────────────────┐                   │
│              │   Shared Storage    │                   │
│              │   (ASM/Raw Device)  │                   │
│              └─────────────────────┘                   │
└─────────────────────────────────────────────────────────┘
```

#### Cache Fusion:
```sql
-- Check cluster database status
SELECT name, value FROM v$parameter WHERE name = 'cluster_database';

-- View RAC instances
SELECT inst_id, instance_name, status, thread#
FROM gv$instance;

-- Global Cache statistics
SELECT name, value
FROM gv$sysstat
WHERE name LIKE '%gc%'
AND inst_id = 1;

-- Interconnect statistics
SELECT name, value
FROM gv$sysstat
WHERE name LIKE '%global%enqueue%'
ORDER BY inst_id;
```

### 8.2 Automatic Storage Management (ASM)

#### ASM Configuration:
```sql
-- Create ASM disk group
CREATE DISKGROUP data_dg EXTERNAL REDUNDANCY
DISK '/dev/raw/raw1', '/dev/raw/raw2', '/dev/raw/raw3';

-- Add disk to diskgroup
ALTER DISKGROUP data_dg ADD DISK '/dev/raw/raw4';

-- Check ASM diskgroup
SELECT name, state, type, total_mb, free_mb
FROM v$asm_diskgroup;

-- ASM disk information
SELECT group_number, disk_number, name, path, total_mb
FROM v$asm_disk;
```

---

## 9. Data Guard

### 9.1 Data Guard Architecture

#### Standby Database Types:
```
Primary Database ────► Physical Standby (Binary identical)
                 │
                 └───► Logical Standby (SQL Apply)
```

#### Data Guard Configuration:
```sql
-- Primary database setup
ALTER DATABASE FORCE LOGGING;
ALTER DATABASE ADD STANDBY LOGFILE GROUP 10 SIZE 50M;

-- Enable archiving
ALTER SYSTEM SET log_archive_dest_1 = 'location=/arch';
ALTER SYSTEM SET log_archive_dest_2 = 
'service=standby_db lgwr async valid_for=(online_logfiles,primary_role)';

-- Standby database creation
DUPLICATE TARGET DATABASE FOR STANDBY FROM ACTIVE DATABASE;

-- Start managed recovery
ALTER DATABASE RECOVER MANAGED STANDBY DATABASE DISCONNECT FROM SESSION;
```

### 9.2 Data Guard Monitoring:
```sql
-- Check data guard status
SELECT database_role, protection_mode, protection_level
FROM v$database;

-- Archive gap check
SELECT thread#, low_sequence#, high_sequence#
FROM v$archive_gap;

-- Apply lag
SELECT name, value, datum_time
FROM v$dataguard_stats
WHERE name = 'apply lag';

-- Switchover operation
-- On primary:
ALTER DATABASE COMMIT TO SWITCHOVER TO STANDBY;
SHUTDOWN IMMEDIATE;
STARTUP MOUNT;
ALTER DATABASE COMMIT TO SWITCHOVER TO PRIMARY;
ALTER DATABASE OPEN;

-- On standby:
ALTER DATABASE COMMIT TO SWITCHOVER TO PRIMARY;
ALTER DATABASE OPEN;
```

---

## 10. Performance Tuning

### 10.1 Performance Monitoring

#### Key Performance Views:
```sql
-- Active Session History
SELECT sql_id,
       COUNT(*) as samples,
       ROUND(COUNT(*) * 100 / SUM(COUNT(*)) OVER (), 2) as pct
FROM v$active_session_history
WHERE sample_time >= SYSDATE - 1/24  -- Last hour
GROUP BY sql_id
ORDER BY samples DESC;

-- Top SQL by execution time
SELECT sql_id, executions, elapsed_time/1000000 as elapsed_sec,
       elapsed_time/executions/1000000 as avg_sec
FROM v$sql
WHERE executions > 0
ORDER BY elapsed_time DESC;

-- Wait events analysis
SELECT event, count(*), 
       ROUND(count(*) * 100 / SUM(count(*)) OVER (), 2) as pct
FROM v$session_wait_history
GROUP BY event
ORDER BY count(*) DESC;
```

#### AWR (Automatic Workload Repository):
```sql
-- Generate AWR report
@$ORACLE_HOME/rdbms/admin/awrrpt.sql

-- AWR snapshot management
BEGIN
    DBMS_WORKLOAD_REPOSITORY.create_snapshot();
END;
/

-- Configure AWR retention
BEGIN
    DBMS_WORKLOAD_REPOSITORY.modify_snapshot_settings(
        retention => 43200,  -- 30 days
        interval  => 30      -- 30 minutes
    );
END;
/
```

### 10.2 SQL Tuning

#### Execution Plan Analysis:
```sql
-- Enable SQL trace
ALTER SESSION SET SQL_TRACE = TRUE;
ALTER SESSION SET TRACEFILE_IDENTIFIER = 'my_trace';

-- Explain plan
EXPLAIN PLAN FOR
SELECT * FROM employees e, departments d
WHERE e.department_id = d.department_id
AND d.location_id = 1700;

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);

-- SQL Tuning Advisor
DECLARE
    l_task_name VARCHAR2(30);
BEGIN
    l_task_name := DBMS_SQLTUNE.create_tuning_task(
        sql_id => '&sql_id',
        task_name => 'tune_sql_task'
    );
    
    DBMS_SQLTUNE.execute_tuning_task('tune_sql_task');
    
    DBMS_OUTPUT.put_line(DBMS_SQLTUNE.report_tuning_task('tune_sql_task'));
END;
/
```

#### Index Optimization:
```sql
-- Find missing indexes
SELECT * FROM TABLE(DBMS_SQLTUNE.report_auto_tuning_task);

-- Index usage monitoring
ALTER INDEX emp_name_idx MONITORING USAGE;

-- Check index usage
SELECT * FROM v$object_usage WHERE used = 'NO';

-- Rebuild fragmented indexes
SELECT index_name, blevel, leaf_blocks, distinct_keys
FROM user_indexes
WHERE blevel > 4;

ALTER INDEX emp_name_idx REBUILD ONLINE;
```

---

## 🔧 Thực hành Oracle

### Lab 1: Database Installation và Configuration
```bash
# Oracle Database 19c installation
./runInstaller -silent -responseFile /opt/oracle/db_install.rsp

# Database creation
dbca -silent -createDatabase \
     -templateName General_Purpose.dbc \
     -gdbname orcl \
     -sid orcl \
     -sysPassword welcome1 \
     -systemPassword welcome1
```

### Lab 2: Performance Tuning
```sql
-- Memory sizing
SELECT component, current_size/1024/1024 as current_mb,
       min_size/1024/1024 as min_mb,
       max_size/1024/1024 as max_mb
FROM v$sga_resize_ops
WHERE component IN ('DEFAULT buffer cache', 'Shared pool', 'Large pool');

-- Automatic Memory Management
ALTER SYSTEM SET memory_target = 2G;
ALTER SYSTEM SET memory_max_target = 4G;
```

### Lab 3: Backup Strategy
```sql
-- RMAN backup script
#!/bin/bash
rman target / << EOF
run {
    allocate channel c1 device type disk format '/backup/rman/%U';
    allocate channel c2 device type disk format '/backup/rman/%U';
    
    backup incremental level 0 database plus archivelog;
    
    backup current controlfile;
    
    delete noprompt obsolete;
    
    release channel c1;
    release channel c2;
}
exit;
EOF
```

## 📊 Monitoring Scripts

### Database Health Check:
```sql
-- Comprehensive health check
SELECT 'Tablespace Usage' as check_type,
       tablespace_name,
       ROUND((used_space/total_space)*100,2) as pct_used
FROM (
    SELECT df.tablespace_name,
           df.total_space,
           (df.total_space - NVL(fs.free_space,0)) as used_space
    FROM (SELECT tablespace_name, SUM(bytes) total_space
          FROM dba_data_files GROUP BY tablespace_name) df
    LEFT JOIN (SELECT tablespace_name, SUM(bytes) free_space
               FROM dba_free_space GROUP BY tablespace_name) fs
    ON df.tablespace_name = fs.tablespace_name
);

-- Session monitoring
SELECT username, status, machine, program, 
       logon_time, last_call_et
FROM v$session
WHERE username IS NOT NULL
ORDER BY last_call_et DESC;
```

## 📚 Tài liệu Tham khảo

### Oracle Documentation:
- Oracle Database Administrator's Guide 19c
- Oracle Database Performance Tuning Guide
- Oracle Real Application Clusters Administration Guide
- Oracle Data Guard Concepts and Administration

### Best Practices:
- Oracle Maximum Availability Architecture (MAA)
- Oracle Database Security Guide
- Oracle Backup and Recovery User's Guide

---

*Nội dung này được thiết kế cho Viettel IDC environment với focus vào enterprise-level Oracle deployment và management.*
