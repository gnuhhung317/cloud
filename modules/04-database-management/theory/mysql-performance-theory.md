# MySQL Performance Theory
# Lý thuyết Hiệu năng MySQL

## 📚 Mục lục
1. [MySQL Architecture Theory](#1-mysql-architecture-theory)
2. [Storage Engine Comparison](#2-storage-engine-comparison)
3. [Query Optimization Theory](#3-query-optimization-theory)
4. [Indexing Strategy](#4-indexing-strategy)
5. [Transaction Management](#5-transaction-management)
6. [Replication Theory](#6-replication-theory)
7. [Performance Tuning](#7-performance-tuning)
8. [High Availability Solutions](#8-high-availability-solutions)
9. [Monitoring và Troubleshooting](#9-monitoring-và-troubleshooting)
10. [Security và Best Practices](#10-security-và-best-practices)

---

## 1. MySQL Architecture Theory

### 1.1 MySQL Layered Architecture

#### Three-Layer Architecture:
```
MySQL Server Architecture:

┌─────────────────────────────────────────────────────────┐
│                Connection Layer                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐ │
│  │ Connection  │  │ Thread      │  │ Authentication  │ │
│  │ Handler     │  │ Manager     │  │ & Authorization │ │
│  └─────────────┘  └─────────────┘  └─────────────────┘ │
├─────────────────────────────────────────────────────────┤
│                    SQL Layer                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐ │
│  │   Parser    │  │  Optimizer  │  │     Cache       │ │
│  │             │  │             │  │   (Query)       │ │
│  └─────────────┘  └─────────────┘  └─────────────────┘ │
├─────────────────────────────────────────────────────────┤
│                  Storage Engine Layer                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐ │
│  │   InnoDB    │  │    MyISAM   │  │     Memory      │ │
│  │             │  │             │  │                 │ │
│  └─────────────┘  └─────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
                ┌─────────────────┐
                │   File System   │
                │   (Data Files)  │
                └─────────────────┘
```

#### Connection Management:
```sql
-- Check connection statistics
SHOW STATUS LIKE 'Threads%';
/*
Threads_cached    : 8    (idle connections in cache)
Threads_connected : 50   (currently connected)
Threads_created   : 1250 (total threads created)
Threads_running   : 5    (actively executing queries)
*/

-- Connection pool configuration
SET GLOBAL max_connections = 500;
SET GLOBAL thread_cache_size = 50;
SET GLOBAL connect_timeout = 10;
SET GLOBAL wait_timeout = 28800;      -- 8 hours
SET GLOBAL interactive_timeout = 28800;

-- Monitor connection usage
SELECT 
    USER,
    HOST,
    DB,
    COMMAND,
    TIME,
    STATE,
    INFO
FROM INFORMATION_SCHEMA.PROCESSLIST
WHERE TIME > 60  -- Connections running > 1 minute
ORDER BY TIME DESC;
```

### 1.2 Query Processing Flow

#### SQL Execution Pipeline:
```
Query Execution Flow:

Client Query
     │
     ▼
┌─────────────┐
│ Connection  │ → Authentication, Permission Check
│ Handler     │
└─────────────┘
     │
     ▼
┌─────────────┐
│ Query Cache │ → Check if identical query exists
│ (Deprecated)│   (MySQL 8.0 removed this)
└─────────────┘
     │
     ▼
┌─────────────┐
│   Parser    │ → Lexical/Syntactic Analysis
│             │   Create Parse Tree
└─────────────┘
     │
     ▼
┌─────────────┐
│ Preprocessor│ → Resolve table/column names
│             │   Check permissions
└─────────────┘
     │
     ▼
┌─────────────┐
│  Optimizer  │ → Choose execution plan
│             │   Cost-based optimization
└─────────────┘
     │
     ▼
┌─────────────┐
│ Execution   │ → Call storage engine APIs
│ Engine      │   Return results
└─────────────┘
```

#### Query Cache (MySQL 5.7 and earlier):
```sql
-- Query cache was deprecated in MySQL 5.7, removed in 8.0
-- Understanding for legacy systems

-- Enable query cache (MySQL 5.7)
SET GLOBAL query_cache_type = ON;
SET GLOBAL query_cache_size = 268435456;  -- 256MB

-- Monitor query cache effectiveness
SHOW STATUS LIKE 'Qcache%';
/*
Qcache_free_blocks     : 1158
Qcache_free_memory     : 3981312
Qcache_hits           : 7890234   -- Cache hits
Qcache_inserts        : 1234567   -- New queries cached
Qcache_lowmem_prunes  : 123       -- Queries removed due to memory
Qcache_not_cached     : 456789    -- Queries not cacheable
Qcache_queries_in_cache: 5678     -- Currently cached queries
Qcache_total_blocks   : 12345
*/

-- Query cache hit ratio calculation
-- Hit Ratio = Qcache_hits / (Qcache_hits + Com_select)
-- Target: > 80% for repetitive query workloads
```

### 1.3 Thread Model

#### Connection Threading:
```sql
-- Thread model configuration
SHOW VARIABLES LIKE 'thread%';
/*
thread_cache_size     : 50    (threads kept for reuse)
thread_handling       : one-thread-per-connection
thread_stack         : 262144 (stack size per thread)
*/

-- Monitor thread efficiency
SELECT 
    (Threads_created / Connections) * 100 as thread_cache_miss_rate
FROM 
    (SELECT VARIABLE_VALUE as Threads_created 
     FROM performance_schema.global_status 
     WHERE VARIABLE_NAME = 'Threads_created') tc,
    (SELECT VARIABLE_VALUE as Connections 
     FROM performance_schema.global_status 
     WHERE VARIABLE_NAME = 'Connections') c;

-- Target thread cache miss rate: < 10%
```

---

## 2. Storage Engine Comparison

### 2.1 InnoDB Architecture

#### InnoDB Internal Structure:
```
InnoDB Storage Engine:

┌─────────────────────────────────────────────────────────┐
│                    InnoDB Buffer Pool                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐ │
│  │ Data Pages  │  │ Index Pages │  │ Insert Buffer   │ │
│  │             │  │             │  │                 │ │
│  └─────────────┘  └─────────────┘  └─────────────────┘ │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐ │
│  │ Redo Log    │  │ Undo Log    │  │ Doublewrite     │ │
│  │ Buffer      │  │ Buffer      │  │ Buffer          │ │
│  └─────────────┘  └─────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                   Disk Storage                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐ │
│  │ Data Files  │  │ Redo Logs   │  │ Undo Tablespace│ │
│  │ (.ibd)      │  │ (ib_logfile)│  │                 │ │
│  └─────────────┘  └─────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

#### InnoDB Buffer Pool:
```sql
-- Buffer pool configuration
SET GLOBAL innodb_buffer_pool_size = 4294967296;  -- 4GB
SET GLOBAL innodb_buffer_pool_instances = 4;       -- Multiple instances

-- Monitor buffer pool efficiency
SELECT 
    VARIABLE_NAME,
    VARIABLE_VALUE
FROM performance_schema.global_status 
WHERE VARIABLE_NAME IN (
    'Innodb_buffer_pool_reads',
    'Innodb_buffer_pool_read_requests',
    'Innodb_buffer_pool_pages_data',
    'Innodb_buffer_pool_pages_free',
    'Innodb_buffer_pool_pages_dirty'
);

-- Calculate buffer pool hit ratio
SELECT 
    (1 - (Innodb_buffer_pool_reads / Innodb_buffer_pool_read_requests)) * 100 
    AS buffer_pool_hit_ratio
FROM performance_schema.global_status 
WHERE VARIABLE_NAME IN ('Innodb_buffer_pool_reads', 'Innodb_buffer_pool_read_requests');
-- Target: > 99% for OLTP workloads
```

#### MVCC Implementation:
```sql
-- InnoDB MVCC with Undo Logs
-- Example scenario at Viettel IDC

-- Session 1: Start transaction
START TRANSACTION;
SELECT balance FROM subscriber_accounts WHERE subscriber_id = 'VT001234567';
-- Returns: 100000 (current balance)

-- Session 2: Update balance (concurrent)
START TRANSACTION;
UPDATE subscriber_accounts 
SET balance = balance - 50000 
WHERE subscriber_id = 'VT001234567';
COMMIT;

-- Session 1: Read again (still in transaction)
SELECT balance FROM subscriber_accounts WHERE subscriber_id = 'VT001234567';
-- Returns: 100000 (unchanged due to MVCC - reads from undo log)

-- Session 1: Commit and read
COMMIT;
SELECT balance FROM subscriber_accounts WHERE subscriber_id = 'VT001234567';
-- Returns: 50000 (sees committed changes)

-- Check undo log usage
SELECT 
    COUNT(*) as active_transactions,
    MAX(trx_started) as oldest_transaction
FROM information_schema.innodb_trx;
```

### 2.2 MyISAM vs InnoDB

#### Feature Comparison:
```sql
-- Feature comparison table
/*
┌─────────────────┬──────────────┬──────────────┐
│    Feature      │    InnoDB    │    MyISAM    │
├─────────────────┼──────────────┼──────────────┤
│ ACID Support    │      ✓       │      ✗       │
│ Row-level Lock  │      ✓       │      ✗       │
│ Table-level Lock│      ✗       │      ✓       │
│ Foreign Keys    │      ✓       │      ✗       │
│ Crash Recovery  │      ✓       │      ✗       │
│ MVCC           │      ✓       │      ✗       │
│ Full-text Index │    ✓(5.6+)   │      ✓       │
│ Compression    │      ✓       │      ✓       │
│ Memory Usage   │    Higher    │    Lower     │
│ Storage Size   │    Larger    │   Smaller    │
└─────────────────┴──────────────┴──────────────┘
*/

-- Create tables with different engines
CREATE TABLE call_records_innodb (
    call_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    caller_id VARCHAR(20) NOT NULL,
    callee_number VARCHAR(15) NOT NULL,
    duration_seconds INT NOT NULL,
    call_cost DECIMAL(8,2) NOT NULL,
    INDEX idx_caller_id (caller_id),
    INDEX idx_call_date (call_date)
) ENGINE=InnoDB;

CREATE TABLE static_config_myisam (
    config_id INT PRIMARY KEY,
    config_name VARCHAR(100) NOT NULL,
    config_value TEXT,
    description TEXT,
    FULLTEXT(config_name, description)
) ENGINE=MyISAM;
```

### 2.3 Memory Storage Engine

#### Use Cases for Memory Engine:
```sql
-- Memory engine for session storage
CREATE TABLE user_sessions (
    session_id VARCHAR(128) PRIMARY KEY,
    subscriber_id VARCHAR(20) NOT NULL,
    login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    user_agent TEXT,
    INDEX idx_subscriber (subscriber_id),
    INDEX idx_activity (last_activity)
) ENGINE=MEMORY MAX_ROWS=1000000;

-- Memory engine limitations
/*
- Data lost on server restart
- No BLOB/TEXT columns
- Fixed-length rows only
- Limited indexes (HASH and BTREE)
- No foreign keys
- Good for: temporary data, session storage, caching
*/

-- Monitor memory engine usage
SELECT 
    TABLE_NAME,
    TABLE_ROWS,
    DATA_LENGTH,
    INDEX_LENGTH,
    DATA_FREE
FROM information_schema.tables 
WHERE ENGINE = 'MEMORY';
```

---

## 3. Query Optimization Theory

### 3.1 MySQL Optimizer

#### Cost-Based Optimization:
```sql
-- MySQL Optimizer components:
-- 1. Statistics collector
-- 2. Cost model
-- 3. Plan generator
-- 4. Plan selector

-- Update table statistics
ANALYZE TABLE subscribers, call_records, billing_transactions;

-- Check table statistics
SELECT 
    TABLE_NAME,
    TABLE_ROWS,
    AVG_ROW_LENGTH,
    DATA_LENGTH,
    INDEX_LENGTH,
    UPDATE_TIME
FROM information_schema.tables 
WHERE TABLE_SCHEMA = 'viettel_idc';

-- Optimizer cost constants (MySQL 8.0)
SELECT * FROM mysql.server_cost;
SELECT * FROM mysql.engine_cost;
```

#### Execution Plan Analysis:
```sql
-- Complex query for Viettel IDC billing analysis
EXPLAIN FORMAT=JSON
SELECT 
    s.subscriber_id,
    s.name,
    s.plan_type,
    COUNT(c.call_id) as total_calls,
    SUM(c.duration_seconds) as total_duration,
    SUM(c.call_cost) as total_cost,
    AVG(c.call_cost) as avg_cost_per_call
FROM subscribers s
JOIN call_records c ON s.subscriber_id = c.caller_id
WHERE s.status = 'ACTIVE'
  AND c.call_date >= '2024-01-01'
  AND c.call_date < '2024-02-01'
  AND c.duration_seconds >= 60
GROUP BY s.subscriber_id, s.name, s.plan_type
HAVING total_calls > 100
ORDER BY total_cost DESC
LIMIT 1000;

/*
Sample execution plan analysis:
{
  "query_block": {
    "select_id": 1,
    "cost_info": {
      "query_cost": "25847.65"
    },
    "ordering_operation": {
      "using_filesort": true,
      "cost_info": {
        "sort_cost": "1000.00"
      },
      "grouping_operation": {
        "using_temporary_table": true,
        "using_filesort": false,
        "cost_info": {
          "query_cost": "24847.65"
        },
        "nested_loop": [
          {
            "table": {
              "table_name": "s",
              "access_type": "ref",
              "possible_keys": ["idx_status"],
              "key": "idx_status",
              "used_key_parts": ["status"],
              "key_length": "33",
              "ref": ["const"],
              "rows_examined_per_scan": 95000,
              "rows_produced_per_join": 95000,
              "filtered": "100.00",
              "cost_info": {
                "read_cost": "1900.00",
                "eval_cost": "9500.00",
                "prefix_cost": "11400.00",
                "data_read_per_join": "7M"
              }
            }
          },
          {
            "table": {
              "table_name": "c",
              "access_type": "ref", 
              "possible_keys": ["idx_caller_date", "idx_duration"],
              "key": "idx_caller_date",
              "used_key_parts": ["caller_id"],
              "key_length": "83",
              "ref": ["viettel_idc.s.subscriber_id"],
              "rows_examined_per_scan": 12,
              "rows_produced_per_join": 1140000,
              "filtered": "11.11",
              "cost_info": {
                "read_cost": "2347.65",
                "eval_cost": "114000.00",
                "prefix_cost": "127747.65",
                "data_read_per_join": "54M"
              }
            }
          }
        ]
      }
    }
  }
}
*/
```

### 3.2 Join Algorithms

#### Nested Loop Join:
```sql
-- Simple nested loop join
-- For each row in outer table, scan inner table

EXPLAIN FORMAT=TREE
SELECT s.name, c.duration_seconds
FROM subscribers s
JOIN call_records c ON s.subscriber_id = c.caller_id
WHERE s.subscriber_id = 'VT001234567';

/*
-> Nested loop inner join  (cost=5.50 rows=10)
    -> Const row from s where subscriber_id='VT001234567'  (cost=1.00 rows=1)
    -> Index lookup on c using idx_caller_id (caller_id='VT001234567')  (cost=4.50 rows=10)
*/
```

#### Block Nested Loop:
```sql
-- When no suitable index exists
-- Uses join buffer to reduce I/O

SET SESSION join_buffer_size = 262144;  -- 256KB

-- Query that might use block nested loop
EXPLAIN FORMAT=TREE
SELECT s.name, c.duration_seconds
FROM subscribers s
JOIN call_records c ON s.registration_date = c.call_date  -- No index on call_date
WHERE s.status = 'ACTIVE';

/*
-> Filter: (s.status = 'ACTIVE')  (cost=1234567.89 rows=1140000)
    -> Inner hash join (s.registration_date = c.call_date)  (cost=1234567.89 rows=1140000)
        -> Table scan on c  (cost=10285.40 rows=95000)
        -> Hash
            -> Table scan on s  (cost=9500.00 rows=95000)
*/
```

#### Hash Join (MySQL 8.0.18+):
```sql
-- Hash join for better performance on large datasets
-- Automatically used when optimizer determines it's better

EXPLAIN FORMAT=TREE
SELECT s.name, COUNT(c.call_id)
FROM subscribers s
JOIN call_records c ON s.subscriber_id = c.caller_id
GROUP BY s.subscriber_id;

/*
-> Aggregate: count(c.call_id)  (cost=1234567.89 rows=95000)
    -> Inner hash join (s.subscriber_id = c.caller_id)  (cost=1234567.89 rows=1140000)
        -> Table scan on s  (cost=9500.00 rows=95000)
        -> Hash
            -> Table scan on c  (cost=10285.40 rows=1140000)
*/
```

### 3.3 Subquery Optimization

#### Subquery Transformation:
```sql
-- Correlated subquery (inefficient)
SELECT s.subscriber_id, s.name
FROM subscribers s
WHERE EXISTS (
    SELECT 1 FROM call_records c 
    WHERE c.caller_id = s.subscriber_id 
      AND c.call_date >= '2024-01-01'
      AND c.duration_seconds > 300
);

-- Semi-join optimization (MySQL 5.6+)
-- Optimizer automatically transforms to semi-join
EXPLAIN FORMAT=TREE
SELECT s.subscriber_id, s.name
FROM subscribers s
WHERE s.subscriber_id IN (
    SELECT c.caller_id FROM call_records c 
    WHERE c.call_date >= '2024-01-01'
      AND c.duration_seconds > 300
);

/*
-> Nested loop semijoin  (cost=15623.45 rows=1140)
    -> Filter: ((c.call_date >= DATE'2024-01-01') and (c.duration_seconds > 300))  (cost=10285.40 rows=1140)
        -> Table scan on c  (cost=10285.40 rows=1140000)
    -> Single-row index lookup on s using PRIMARY (subscriber_id=c.caller_id)  (cost=0.25 rows=1)
*/
```

---

## 4. Indexing Strategy

### 4.1 Index Types

#### B-Tree Indexes (Default):
```sql
-- Single column index
CREATE INDEX idx_subscriber_phone ON subscribers(phone_number);

-- Composite index (column order matters)
CREATE INDEX idx_call_comprehensive ON call_records(
    caller_id,           -- High selectivity first
    call_date,           -- Range queries
    duration_seconds     -- Additional filtering
);

-- Covering index (includes all needed columns)
CREATE INDEX idx_subscriber_covering ON subscribers(
    status,              -- WHERE condition
    plan_type,           -- GROUP BY
    registration_date    -- ORDER BY
) INCLUDE (name, phone_number);  -- MySQL 8.0 syntax
```

#### Index Usage Analysis:
```sql
-- Check index usage statistics
SELECT 
    OBJECT_SCHEMA,
    OBJECT_NAME,
    INDEX_NAME,
    COUNT_FETCH,
    COUNT_INSERT,
    COUNT_UPDATE,
    COUNT_DELETE
FROM performance_schema.table_io_waits_summary_by_index_usage
WHERE OBJECT_SCHEMA = 'viettel_idc'
ORDER BY COUNT_FETCH DESC;

-- Find unused indexes
SELECT 
    OBJECT_SCHEMA,
    OBJECT_NAME, 
    INDEX_NAME
FROM performance_schema.table_io_waits_summary_by_index_usage 
WHERE INDEX_NAME IS NOT NULL
  AND COUNT_STAR = 0
  AND OBJECT_SCHEMA = 'viettel_idc';
```

### 4.2 Index Optimization

#### Prefix Indexes:
```sql
-- Analyze column value distribution
SELECT 
    LENGTH(phone_number) as length,
    COUNT(*) as count
FROM subscribers 
GROUP BY LENGTH(phone_number)
ORDER BY length;

-- Create prefix index for long text columns
CREATE INDEX idx_subscriber_name_prefix ON subscribers(name(10));

-- Test prefix selectivity
SELECT 
    COUNT(DISTINCT LEFT(name, 5)) / COUNT(*) as selectivity_5,
    COUNT(DISTINCT LEFT(name, 10)) / COUNT(*) as selectivity_10,
    COUNT(DISTINCT LEFT(name, 15)) / COUNT(*) as selectivity_15
FROM subscribers;
```

#### Functional Indexes (MySQL 8.0):
```sql
-- Index on expression
CREATE INDEX idx_subscriber_upper_name 
ON subscribers((UPPER(name)));

-- Index on JSON fields
CREATE INDEX idx_subscriber_prefs_lang 
ON subscribers((CAST(preferences->>'$.language' AS CHAR(10))));

-- Use the functional index
SELECT * FROM subscribers 
WHERE UPPER(name) = 'NGUYEN VAN A';

SELECT * FROM subscribers 
WHERE preferences->>'$.language' = 'vi';
```

### 4.3 Index Maintenance

#### Index Statistics:
```sql
-- Check index cardinality
SELECT 
    TABLE_NAME,
    INDEX_NAME,
    COLUMN_NAME,
    CARDINALITY,
    SUB_PART
FROM information_schema.statistics 
WHERE TABLE_SCHEMA = 'viettel_idc'
ORDER BY TABLE_NAME, INDEX_NAME, SEQ_IN_INDEX;

-- Update index statistics
ANALYZE TABLE subscribers, call_records;

-- Check index fragmentation
SELECT 
    TABLE_SCHEMA,
    TABLE_NAME,
    DATA_FREE,
    (DATA_FREE / (DATA_LENGTH + INDEX_LENGTH)) * 100 as fragmentation_pct
FROM information_schema.tables 
WHERE TABLE_SCHEMA = 'viettel_idc'
  AND DATA_FREE > 0;

-- Rebuild fragmented indexes
ALTER TABLE call_records ENGINE=InnoDB;
```

---

## 5. Transaction Management

### 5.1 InnoDB Transaction Model

#### Isolation Levels:
```sql
-- Set transaction isolation level
SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;

-- Check current isolation level
SELECT @@transaction_isolation;

-- Isolation level demonstrations
-- READ UNCOMMITTED (dirty reads possible)
SET SESSION TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
START TRANSACTION;
SELECT balance FROM subscriber_accounts WHERE subscriber_id = 'VT001234567';
-- Can see uncommitted changes from other transactions

-- READ COMMITTED (default, prevents dirty reads)
SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;
START TRANSACTION;
SELECT balance FROM subscriber_accounts WHERE subscriber_id = 'VT001234567';
-- Time T1: Returns 100000
-- Other transaction updates balance to 80000 and commits
SELECT balance FROM subscriber_accounts WHERE subscriber_id = 'VT001234567';
-- Time T2: Returns 80000 (non-repeatable read)

-- REPEATABLE READ (InnoDB default, prevents non-repeatable reads)
SET SESSION TRANSACTION ISOLATION LEVEL REPEATABLE READ;
START TRANSACTION;
SELECT balance FROM subscriber_accounts WHERE subscriber_id = 'VT001234567';
-- Time T1: Returns 100000
-- Other transaction updates balance to 80000 and commits
SELECT balance FROM subscriber_accounts WHERE subscriber_id = 'VT001234567';
-- Time T2: Still returns 100000 (repeatable read via MVCC)

-- SERIALIZABLE (strictest, table-level locking)
SET SESSION TRANSACTION ISOLATION LEVEL SERIALIZABLE;
START TRANSACTION;
SELECT * FROM subscriber_accounts WHERE plan_type = 'premium';
-- Prevents phantom reads, but may cause deadlocks
```

### 5.2 Lock Management

#### InnoDB Locking:
```sql
-- Check current locks
SELECT 
    ENGINE_LOCK_ID,
    ENGINE_TRANSACTION_ID,
    THREAD_ID,
    OBJECT_SCHEMA,
    OBJECT_NAME,
    LOCK_TYPE,
    LOCK_MODE,
    LOCK_STATUS,
    LOCK_DATA
FROM performance_schema.data_locks
WHERE OBJECT_SCHEMA = 'viettel_idc';

-- Check lock waits
SELECT 
    REQUESTING_ENGINE_LOCK_ID,
    REQUESTING_ENGINE_TRANSACTION_ID,
    REQUESTING_THREAD_ID,
    BLOCKING_ENGINE_LOCK_ID,
    BLOCKING_ENGINE_TRANSACTION_ID,
    BLOCKING_THREAD_ID
FROM performance_schema.data_lock_waits;

-- Row-level locking examples
-- Shared lock (SELECT ... FOR SHARE)
START TRANSACTION;
SELECT * FROM subscriber_accounts 
WHERE subscriber_id = 'VT001234567' 
FOR SHARE;  -- S lock, allows other S locks, blocks X locks

-- Exclusive lock (SELECT ... FOR UPDATE)
START TRANSACTION;
SELECT * FROM subscriber_accounts 
WHERE subscriber_id = 'VT001234567' 
FOR UPDATE;  -- X lock, blocks all other locks
```

### 5.3 Deadlock Detection

#### Deadlock Analysis:
```sql
-- Enable InnoDB deadlock logging
SET GLOBAL innodb_print_all_deadlocks = ON;

-- View deadlock information
SHOW ENGINE INNODB STATUS\G

/*
Sample deadlock output:
------------------------
LATEST DETECTED DEADLOCK
------------------------
2024-01-15 10:30:00 0x7f8b8c000700
*** (1) TRANSACTION:
TRANSACTION 421394821, ACTIVE 10 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1136, 2 row lock(s)
MySQL thread id 123, OS thread handle 140242392000256, query id 12345678 localhost viettel updating
UPDATE subscriber_accounts SET balance = balance - 10000 WHERE subscriber_id = 'VT001234567'

*** (1) HOLDS THE LOCK(S):
RECORD LOCKS space id 25 page no 3 n bits 72 index PRIMARY of table `viettel_idc`.`subscriber_accounts`
trx id 421394821 lock_mode X locks rec but not gap
Record lock, heap no 2 PHYSICAL RECORD: n_fields 5; compact format; info bits 0
 0: len 11; hex 565430303132333435363738; asc VT001234567;;

*** (1) WAITING FOR THIS LOCK TO BE GRANTED:
RECORD LOCKS space id 25 page no 4 n bits 72 index PRIMARY of table `viettel_idc`.`subscriber_accounts`
trx id 421394821 lock_mode X locks rec but not gap waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 5; compact format; info bits 0
 0: len 11; hex 565430303132333435363739; asc VT001234568;;

*** (2) TRANSACTION:
TRANSACTION 421394822, ACTIVE 8 sec starting index read
mysql tables in use 1, locked 1
4 lock struct(s), heap size 1136, 3 row lock(s)
MySQL thread id 124, OS thread handle 140242392000512, query id 12345679 localhost viettel updating
UPDATE subscriber_accounts SET balance = balance - 5000 WHERE subscriber_id = 'VT001234568'

*** (2) HOLDS THE LOCK(S):
RECORD LOCKS space id 25 page no 4 n bits 72 index PRIMARY of table `viettel_idc`.`subscriber_accounts`
trx id 421394822 lock_mode X locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 5; compact format; info bits 0
 0: len 11; hex 565430303132333435363739; asc VT001234568;;

*** (2) WAITING FOR THIS LOCK TO BE GRANTED:
RECORD LOCKS space id 25 page no 3 n bits 72 index PRIMARY of table `viettel_idc`.`subscriber_accounts`
trx id 421394822 lock_mode X locks rec but not gap waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 5; compact format; info bits 0
 0: len 11; hex 565430303132333435363738; asc VT001234567;;

*** WE ROLL BACK TRANSACTION (1)
*/

-- Deadlock prevention strategies
-- 1. Access tables in consistent order
-- 2. Keep transactions short
-- 3. Use appropriate isolation levels
-- 4. Consider advisory locks for complex workflows
```

---

## 6. Replication Theory

### 6.1 Binary Log Replication

#### Replication Architecture:
```
MySQL Replication:

┌─────────────────┐      Binary Log      ┌─────────────────┐
│     Master      │ ─────────────────────▶│     Slave       │
│                 │                       │                 │
│ ┌─────────────┐ │      I/O Thread       │ ┌─────────────┐ │
│ │ Binary Log  │ │ ◀─────────────────────┤ │ Relay Log   │ │
│ │ (binlog)    │ │                       │ │             │ │
│ └─────────────┘ │      SQL Thread       │ └─────────────┘ │
│                 │ ─────────────────────▶│                 │
│ Applications    │                       │ Read-only       │
│ (Read/Write)    │                       │ Applications    │
└─────────────────┘                       └─────────────────┘
```

#### Binary Log Formats:
```sql
-- Configure binary logging
SET GLOBAL log_bin = ON;
SET GLOBAL binlog_format = 'ROW';  -- ROW, STATEMENT, or MIXED
SET GLOBAL binlog_row_image = 'FULL';  -- FULL, MINIMAL, NOBLOB

-- Check binary log settings
SHOW VARIABLES LIKE 'binlog%';
SHOW VARIABLES LIKE 'log_bin%';

-- View binary logs
SHOW BINARY LOGS;
SHOW BINLOG EVENTS IN 'mysql-bin.000001' LIMIT 10;

-- Binary log format comparison:
/*
STATEMENT format:
- Logs SQL statements
- Smaller log files
- May cause inconsistencies with non-deterministic functions

ROW format:
- Logs actual row changes
- Larger log files  
- Consistent replication
- Better for complex statements

MIXED format:
- Uses STATEMENT when safe
- Falls back to ROW when necessary
- Balance between size and safety
*/
```

### 6.2 Replication Configuration

#### Master Configuration:
```sql
-- Master server configuration (my.cnf)
[mysqld]
server-id = 1
log-bin = mysql-bin
binlog-format = ROW
binlog-do-db = viettel_idc
sync_binlog = 1                    -- Sync binlog to disk after each write
innodb_flush_log_at_trx_commit = 1 -- Flush redo log at commit

-- Create replication user
CREATE USER 'repl_user'@'%' IDENTIFIED BY 'strong_password';
GRANT REPLICATION SLAVE ON *.* TO 'repl_user'@'%';
FLUSH PRIVILEGES;

-- Get master status
SHOW MASTER STATUS;
/*
+------------------+----------+--------------+------------------+-------------------+
| File             | Position | Binlog_Do_DB | Binlog_Ignore_DB | Executed_Gtid_Set |
+------------------+----------+--------------+------------------+-------------------+
| mysql-bin.000001 |      154 | viettel_idc  |                  |                   |
+------------------+----------+--------------+------------------+-------------------+
*/
```

#### Slave Configuration:
```sql
-- Slave server configuration (my.cnf)
[mysqld]
server-id = 2
relay-log = relay-bin
read_only = 1                      -- Prevent writes on slave
log_slave_updates = 1              -- Log replicated events to binlog
relay_log_recovery = 1             -- Auto-recover relay logs

-- Configure slave connection
CHANGE MASTER TO
    MASTER_HOST='master.viettel.com',
    MASTER_USER='repl_user',
    MASTER_PASSWORD='strong_password',
    MASTER_LOG_FILE='mysql-bin.000001',
    MASTER_LOG_POS=154;

-- Start replication
START SLAVE;

-- Check slave status
SHOW SLAVE STATUS\G
/*
Key fields to monitor:
- Slave_IO_Running: Yes
- Slave_SQL_Running: Yes  
- Seconds_Behind_Master: 0
- Last_Error: (empty)
- Master_Log_File: mysql-bin.000001
- Read_Master_Log_Pos: 154
- Exec_Master_Log_Pos: 154
*/
```

### 6.3 GTID Replication

#### Global Transaction Identifiers:
```sql
-- Enable GTID (MySQL 5.6+)
-- Master configuration
[mysqld]
gtid_mode = ON
enforce_gtid_consistency = ON
log_slave_updates = ON

-- Check GTID status
SHOW VARIABLES LIKE 'gtid%';
SELECT @@gtid_executed;

-- GTID-based slave setup
CHANGE MASTER TO
    MASTER_HOST='master.viettel.com',
    MASTER_USER='repl_user', 
    MASTER_PASSWORD='strong_password',
    MASTER_AUTO_POSITION=1;  -- Use GTID auto-positioning

-- Monitor GTID gaps
SELECT 
    GTID_SUBTRACT(@@global.gtid_executed, @@global.gtid_purged) 
    AS available_gtids;
```

---

## 7. Performance Tuning

### 7.1 Configuration Optimization

#### Memory Configuration:
```sql
-- InnoDB memory settings (for 32GB RAM server)
[mysqld]
innodb_buffer_pool_size = 24G      -- 75% of RAM
innodb_buffer_pool_instances = 8   -- 1 instance per 1GB
innodb_log_buffer_size = 64M       -- Log buffer
innodb_sort_buffer_size = 2M       -- Sort operations

-- Query cache (MySQL 5.7 and earlier)
query_cache_size = 256M
query_cache_type = 1

-- Connection settings
max_connections = 500
thread_cache_size = 50
table_open_cache = 4000
table_definition_cache = 2000

-- Temporary tables
tmp_table_size = 256M
max_heap_table_size = 256M

-- MyISAM settings (if used)
key_buffer_size = 1G
myisam_sort_buffer_size = 128M
```

#### I/O Configuration:
```sql
-- InnoDB I/O settings
[mysqld]
innodb_io_capacity = 2000         -- IOPS capacity (SSD)
innodb_io_capacity_max = 4000     -- Max IOPS for background tasks
innodb_read_io_threads = 8        -- Read threads
innodb_write_io_threads = 8       -- Write threads
innodb_flush_method = O_DIRECT    -- Bypass OS cache
innodb_file_per_table = 1         -- Separate file per table

-- Binary log settings
sync_binlog = 1                   -- Sync frequency (1=every commit)
binlog_cache_size = 1M            -- Binlog cache per session
max_binlog_size = 1G              -- Max binlog file size
expire_logs_days = 7              -- Auto-purge old binlogs
```

### 7.2 Query Performance

#### Slow Query Analysis:
```sql
-- Enable slow query log
[mysqld]
slow_query_log = 1
slow_query_log_file = /var/log/mysql/mysql-slow.log
long_query_time = 1               -- Log queries > 1 second
log_queries_not_using_indexes = 1

-- Analyze slow queries
SELECT 
    SCHEMA_NAME,
    DIGEST_TEXT,
    COUNT_STAR,
    SUM_TIMER_WAIT/1000000000000 as total_time_sec,
    AVG_TIMER_WAIT/1000000000000 as avg_time_sec,
    SUM_ROWS_EXAMINED,
    SUM_ROWS_SENT
FROM performance_schema.events_statements_summary_by_digest 
WHERE SCHEMA_NAME = 'viettel_idc'
ORDER BY SUM_TIMER_WAIT DESC 
LIMIT 10;

-- Use pt-query-digest for log analysis
-- pt-query-digest /var/log/mysql/mysql-slow.log
```

#### Index Usage Monitoring:
```sql
-- Track index effectiveness
SELECT 
    OBJECT_SCHEMA,
    OBJECT_NAME,
    INDEX_NAME,
    COUNT_FETCH,
    COUNT_INSERT,
    COUNT_UPDATE,
    COUNT_DELETE,
    SUM_TIMER_FETCH/1000000000000 as fetch_time_sec
FROM performance_schema.table_io_waits_summary_by_index_usage 
WHERE OBJECT_SCHEMA = 'viettel_idc'
  AND COUNT_FETCH > 0
ORDER BY COUNT_FETCH DESC;

-- Monitor table scans vs index usage
SELECT 
    OBJECT_SCHEMA,
    OBJECT_NAME,
    COUNT_READ,
    SUM_TIMER_READ/1000000000000 as read_time_sec,
    COUNT_FETCH,
    SUM_TIMER_FETCH/1000000000000 as fetch_time_sec
FROM performance_schema.table_io_waits_summary_by_table 
WHERE OBJECT_SCHEMA = 'viettel_idc'
ORDER BY COUNT_READ DESC;
```

### 7.3 Connection Optimization

#### Connection Pool Tuning:
```sql
-- Monitor connection usage
SELECT 
    VARIABLE_NAME,
    VARIABLE_VALUE
FROM performance_schema.global_status 
WHERE VARIABLE_NAME IN (
    'Threads_connected',
    'Threads_running', 
    'Threads_created',
    'Threads_cached',
    'Connections',
    'Max_used_connections'
);

-- Connection efficiency metrics
SELECT 
    (Threads_created / Connections) * 100 as thread_cache_miss_rate,
    (Max_used_connections / max_connections) * 100 as connection_usage_pct
FROM 
    (SELECT VARIABLE_VALUE as Threads_created FROM performance_schema.global_status WHERE VARIABLE_NAME = 'Threads_created') tc,
    (SELECT VARIABLE_VALUE as Connections FROM performance_schema.global_status WHERE VARIABLE_NAME = 'Connections') c,
    (SELECT VARIABLE_VALUE as Max_used_connections FROM performance_schema.global_status WHERE VARIABLE_NAME = 'Max_used_connections') muc,
    (SELECT @@max_connections as max_connections) mc;

-- Optimize connection settings
[mysqld]
max_connections = 500              -- Based on workload
thread_cache_size = 50            -- Keep threads for reuse
connect_timeout = 10              -- Connection establishment timeout
wait_timeout = 28800              -- Idle connection timeout (8 hours)
interactive_timeout = 28800       -- Interactive session timeout
```

---

## 8. High Availability Solutions

### 8.1 MySQL Cluster (NDB)

#### NDB Cluster Architecture:
```
MySQL Cluster (NDB):

           Application Layer
    ┌─────────────┬─────────────┬─────────────┐
    │   MySQL     │   MySQL     │   MySQL     │
    │  Server 1   │  Server 2   │  Server 3   │
    │  (SQL Node) │  (SQL Node) │  (SQL Node) │
    └─────────────┴─────────────┴─────────────┘
                        │
              ┌─────────────────────┐
              │    NDB Storage      │
              │      Cluster        │
    ┌─────────────┬─────────────┬─────────────┐
    │ Data Node 1 │ Data Node 2 │ Data Node 3 │
    │  (ndbd)     │  (ndbd)     │  (ndbd)     │
    └─────────────┴─────────────┴─────────────┘
                        │
    ┌─────────────┬─────────────┬─────────────┐
    │Management   │Management   │             │
    │   Node 1    │   Node 2    │             │
    │  (ndb_mgmd) │  (ndb_mgmd) │             │
    └─────────────┴─────────────┴─────────────┘
```

#### NDB Configuration:
```ini
# config.ini for NDB management node
[ndbd default]
NoOfReplicas=2
DataMemory=80M
IndexMemory=18M

[ndbd]
hostname=ndb1.viettel.com
datadir=/var/lib/mysql-cluster

[ndbd]  
hostname=ndb2.viettel.com
datadir=/var/lib/mysql-cluster

[mysqld]
hostname=sql1.viettel.com

[mysqld]
hostname=sql2.viettel.com

[ndb_mgmd]
hostname=mgm1.viettel.com
datadir=/var/lib/mysql-cluster
```

### 8.2 MySQL InnoDB Cluster

#### InnoDB Cluster Setup:
```javascript
// MySQL Shell setup for InnoDB Cluster
// Primary node setup
dba.configureInstance('root@mysql1.viettel.com:3306');

// Create cluster
var cluster = dba.createCluster('ViettelCluster');

// Add instances
cluster.addInstance('root@mysql2.viettel.com:3306');
cluster.addInstance('root@mysql3.viettel.com:3306');

// Check cluster status
cluster.status();

/*
{
    "clusterName": "ViettelCluster", 
    "defaultReplicaSet": {
        "name": "default", 
        "primary": "mysql1.viettel.com:3306", 
        "ssl": "REQUIRED", 
        "status": "OK", 
        "statusText": "Cluster is ONLINE and can tolerate up to ONE failure.", 
        "topology": {
            "mysql1.viettel.com:3306": {
                "address": "mysql1.viettel.com:3306", 
                "mode": "R/W", 
                "readReplicas": {}, 
                "role": "HA", 
                "status": "ONLINE"
            }, 
            "mysql2.viettel.com:3306": {
                "address": "mysql2.viettel.com:3306", 
                "mode": "R/O", 
                "readReplicas": {}, 
                "role": "HA", 
                "status": "ONLINE"
            }, 
            "mysql3.viettel.com:3306": {
                "address": "mysql3.viettel.com:3306", 
                "mode": "R/O", 
                "readReplicas": {}, 
                "role": "HA", 
                "status": "ONLINE"
            }
        }
    }
}
*/
```

### 8.3 ProxySQL for Load Balancing

#### ProxySQL Configuration:
```sql
-- ProxySQL admin interface
mysql -u admin -p -h 127.0.0.1 -P 6032

-- Configure backend servers
INSERT INTO mysql_servers(hostgroup_id, hostname, port, weight) VALUES
(0, 'mysql1.viettel.com', 3306, 1000),  -- Writer group
(1, 'mysql2.viettel.com', 3306, 900),   -- Reader group
(1, 'mysql3.viettel.com', 3306, 900);   -- Reader group

-- Configure users
INSERT INTO mysql_users(username, password, default_hostgroup) VALUES
('app_user', 'password', 0);

-- Query routing rules
INSERT INTO mysql_query_rules(rule_id, active, match_pattern, destination_hostgroup, apply) VALUES
(1, 1, '^SELECT.*', 1, 1),              -- Route SELECTs to readers
(2, 1, '^INSERT|UPDATE|DELETE.*', 0, 1); -- Route writes to writer

-- Load configuration
LOAD MYSQL SERVERS TO RUNTIME;
LOAD MYSQL USERS TO RUNTIME;
LOAD MYSQL QUERY RULES TO RUNTIME;
SAVE MYSQL SERVERS TO DISK;
SAVE MYSQL USERS TO DISK;
SAVE MYSQL QUERY RULES TO DISK;
```

---

## 9. Monitoring và Troubleshooting

### 9.1 Performance Schema

#### Key Performance Schema Tables:
```sql
-- Enable performance schema (MySQL 5.6+)
[mysqld]
performance_schema = ON
performance-schema-instrument='statement/%=ON'
performance-schema-consumer-events-statements-current=ON
performance-schema-consumer-events-statements-history=ON

-- Top time-consuming queries
SELECT 
    DIGEST_TEXT,
    COUNT_STAR as exec_count,
    ROUND(AVG_TIMER_WAIT/1000000000000, 3) as avg_time_sec,
    ROUND(SUM_TIMER_WAIT/1000000000000, 3) as total_time_sec,
    ROUND(AVG_ROWS_EXAMINED, 0) as avg_rows_examined,
    ROUND(AVG_ROWS_SENT, 0) as avg_rows_sent
FROM performance_schema.events_statements_summary_by_digest 
WHERE SCHEMA_NAME = 'viettel_idc'
ORDER BY SUM_TIMER_WAIT DESC 
LIMIT 10;

-- I/O statistics by table
SELECT 
    OBJECT_SCHEMA,
    OBJECT_NAME,
    COUNT_READ,
    SUM_TIMER_READ/1000000000000 as read_time_sec,
    COUNT_WRITE, 
    SUM_TIMER_WRITE/1000000000000 as write_time_sec,
    COUNT_FETCH,
    SUM_TIMER_FETCH/1000000000000 as fetch_time_sec
FROM performance_schema.table_io_waits_summary_by_table 
WHERE OBJECT_SCHEMA = 'viettel_idc'
ORDER BY SUM_TIMER_READ + SUM_TIMER_WRITE DESC;
```

### 9.2 System Monitoring

#### Key Metrics to Monitor:
```sql
-- Database connections
SELECT 
    VARIABLE_NAME,
    VARIABLE_VALUE
FROM performance_schema.global_status 
WHERE VARIABLE_NAME IN (
    'Threads_connected',
    'Threads_running',
    'Max_used_connections',
    'Connection_errors_max_connections'
);

-- Buffer pool efficiency
SELECT 
    VARIABLE_NAME,
    VARIABLE_VALUE,
    CASE VARIABLE_NAME
        WHEN 'Innodb_buffer_pool_read_requests' THEN 'Read Requests'
        WHEN 'Innodb_buffer_pool_reads' THEN 'Physical Reads'
        WHEN 'Innodb_buffer_pool_pages_total' THEN 'Total Pages'
        WHEN 'Innodb_buffer_pool_pages_free' THEN 'Free Pages'
        WHEN 'Innodb_buffer_pool_pages_dirty' THEN 'Dirty Pages'
    END as description
FROM performance_schema.global_status 
WHERE VARIABLE_NAME IN (
    'Innodb_buffer_pool_read_requests',
    'Innodb_buffer_pool_reads',
    'Innodb_buffer_pool_pages_total',
    'Innodb_buffer_pool_pages_free', 
    'Innodb_buffer_pool_pages_dirty'
);

-- Calculate buffer pool hit ratio
SELECT 
    ROUND(
        (1 - (
            (SELECT VARIABLE_VALUE FROM performance_schema.global_status WHERE VARIABLE_NAME = 'Innodb_buffer_pool_reads') /
            (SELECT VARIABLE_VALUE FROM performance_schema.global_status WHERE VARIABLE_NAME = 'Innodb_buffer_pool_read_requests')
        )) * 100, 
        2
    ) as buffer_pool_hit_ratio_pct;
```

### 9.3 Troubleshooting Common Issues

#### Long-Running Queries:
```sql
-- Find long-running queries
SELECT 
    ID,
    USER,
    HOST,
    DB,
    COMMAND,
    TIME,
    STATE,
    LEFT(INFO, 100) as QUERY_START
FROM information_schema.processlist 
WHERE TIME > 60  -- Running more than 60 seconds
  AND COMMAND != 'Sleep'
ORDER BY TIME DESC;

-- Kill problematic queries
-- KILL 12345;  -- Replace with actual process ID

-- Check for locking issues
SELECT 
    r.trx_id waiting_trx_id,
    r.trx_mysql_thread_id waiting_thread,
    r.trx_query waiting_query,
    b.trx_id blocking_trx_id,
    b.trx_mysql_thread_id blocking_thread,
    b.trx_query blocking_query
FROM information_schema.innodb_lock_waits w
INNER JOIN information_schema.innodb_trx b ON b.trx_id = w.blocking_trx_id
INNER JOIN information_schema.innodb_trx r ON r.trx_id = w.requesting_trx_id;
```

#### Replication Issues:
```sql
-- Check replication status
SHOW SLAVE STATUS\G

-- Common replication problems and solutions:
/*
1. Slave_IO_Running: No
   - Check network connectivity
   - Verify master log file and position
   - Check replication user privileges

2. Slave_SQL_Running: No  
   - Check Last_SQL_Error field
   - Skip problematic statement: SET GLOBAL sql_slave_skip_counter = 1;
   - Or reset slave position

3. Seconds_Behind_Master: Large number
   - Check slave hardware performance
   - Optimize slow queries on slave
   - Consider parallel replication
*/

-- Reset replication (last resort)
STOP SLAVE;
RESET SLAVE;
-- Reconfigure master connection
START SLAVE;
```

---

## 10. Security và Best Practices

### 10.1 Authentication và Authorization

#### User Management:
```sql
-- Create users with specific privileges
CREATE USER 'viettel_app'@'%' IDENTIFIED BY 'strong_password';
CREATE USER 'viettel_readonly'@'%' IDENTIFIED BY 'readonly_password';
CREATE USER 'viettel_backup'@'localhost' IDENTIFIED BY 'backup_password';

-- Grant appropriate privileges
GRANT SELECT, INSERT, UPDATE, DELETE ON viettel_idc.* TO 'viettel_app'@'%';
GRANT SELECT ON viettel_idc.* TO 'viettel_readonly'@'%';
GRANT RELOAD, LOCK TABLES, REPLICATION CLIENT ON *.* TO 'viettel_backup'@'localhost';

-- Use roles (MySQL 8.0+)
CREATE ROLE 'app_developer', 'data_analyst', 'dba';

GRANT SELECT, INSERT, UPDATE, DELETE ON viettel_idc.* TO 'app_developer';
GRANT SELECT ON viettel_idc.* TO 'data_analyst';
GRANT ALL PRIVILEGES ON *.* TO 'dba' WITH GRANT OPTION;

-- Assign roles to users
GRANT 'app_developer' TO 'john@viettel.com';
GRANT 'data_analyst' TO 'mary@viettel.com';
SET DEFAULT ROLE 'app_developer' TO 'john@viettel.com';
```

#### Password Policies:
```sql
-- Configure password validation (MySQL 8.0)
INSTALL COMPONENT 'file://component_validate_password';

SET GLOBAL validate_password.policy = STRONG;
SET GLOBAL validate_password.length = 12;
SET GLOBAL validate_password.mixed_case_count = 1;
SET GLOBAL validate_password.number_count = 1;
SET GLOBAL validate_password.special_char_count = 1;

-- Check password strength
SELECT VALIDATE_PASSWORD_STRENGTH('Viettel123!');
```

### 10.2 Encryption

#### Data-at-Rest Encryption:
```sql
-- Enable encryption for tablespace (MySQL 8.0)
CREATE TABLESPACE encrypted_ts 
    ADD DATAFILE 'encrypted_ts.ibd' 
    ENCRYPTION = 'Y';

-- Create encrypted table
CREATE TABLE sensitive_data (
    id INT PRIMARY KEY,
    subscriber_id VARCHAR(20),
    credit_card_number VARCHAR(20),
    ssn VARCHAR(11)
) TABLESPACE = encrypted_ts;

-- Configure keyring plugin
[mysqld]
early-plugin-load = keyring_file.so
keyring_file_data = /var/lib/mysql-keyring/keyring
```

#### SSL/TLS Configuration:
```sql
-- Enable SSL connections
[mysqld]
ssl-ca = /etc/mysql/ssl/ca-cert.pem
ssl-cert = /etc/mysql/ssl/server-cert.pem  
ssl-key = /etc/mysql/ssl/server-key.pem
require_secure_transport = ON

-- Require SSL for specific users
ALTER USER 'viettel_app'@'%' REQUIRE SSL;

-- Check SSL status
SHOW STATUS LIKE 'Ssl%';
\s  -- Check connection SSL info
```

### 10.3 Audit Logging

#### MySQL Enterprise Audit:
```sql
-- Enable audit plugin (MySQL Enterprise)
INSTALL PLUGIN audit_log SONAME 'audit_log.so';

-- Configure audit settings
SET GLOBAL audit_log_policy = ALL;
SET GLOBAL audit_log_format = JSON;

-- Create audit rules
SELECT audit_log_filter_set_filter('log_all', '{ "filter": { "log": true } }');
SELECT audit_log_filter_set_user('viettel_app', 'log_all');

-- View audit events
SELECT 
    TIMESTAMP,
    ACCOUNT,
    CONNECTION_TYPE,
    SQL_COMMAND,
    GENERAL_COMMAND
FROM mysql.audit_log 
WHERE TIMESTAMP >= DATE_SUB(NOW(), INTERVAL 1 DAY)
ORDER BY TIMESTAMP DESC;
```

### 10.4 Backup Security

#### Secure Backup Practices:
```sql
-- Encrypted backup using mysqldump
mysqldump --single-transaction \
          --routines \
          --triggers \
          --all-databases \
          --host=localhost \
          --user=backup_user \
          --password | \
openssl enc -aes-256-cbc -salt -out backup_$(date +%Y%m%d).sql.enc

-- Secure binary log backups
mysqlbinlog --read-from-remote-server \
            --host=master.viettel.com \
            --user=repl_user \
            --password \
            --raw \
            mysql-bin.000001 | \
openssl enc -aes-256-cbc -salt -out binlog_backup.enc

-- Point-in-time recovery with encrypted backups
openssl enc -aes-256-cbc -d -in backup_20240115.sql.enc | \
mysql --user=root --password viettel_idc
```

---

## 📚 Tham khảo Chuyên sâu

### Documentation:
1. **MySQL Reference Manual** - https://dev.mysql.com/doc/
2. **MySQL Performance Blog** - https://www.percona.com/blog/
3. **High Performance MySQL** - Baron Schwartz, Peter Zaitsev

### Sách chuyên ngành:
1. **"High Performance MySQL"** - Baron Schwartz, Peter Zaitsev, Vadim Tkachenko
2. **"MySQL Troubleshooting"** - Sveta Smirnova
3. **"Effective MySQL series"** - Ronald Bradford
4. **"MySQL Admin Cookbook"** - Daniel Schneller

### Tools và Utilities:
1. **Percona Toolkit** - pt-query-digest, pt-online-schema-change
2. **MySQL Workbench** - GUI administration tool
3. **Percona Monitoring and Management** - Comprehensive monitoring
4. **ProxySQL** - Advanced MySQL proxy
5. **MySQL Shell** - Modern MySQL client

### Viettel IDC Applications:
- **Billing System**: High-consistency financial transactions
- **Customer Database**: User profiles and service plans  
- **Call Detail Records**: High-volume transactional data
- **Network Configuration**: Critical infrastructure settings
- **Reporting System**: Complex analytical queries
- **Session Management**: High-performance temporary data
