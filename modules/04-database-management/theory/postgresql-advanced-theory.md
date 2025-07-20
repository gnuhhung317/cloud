# PostgreSQL Advanced Theory
# Lý thuyết PostgreSQL Nâng cao

## 📚 Mục lục
1. [Kiến trúc PostgreSQL](#1-kiến-trúc-postgresql)
2. [Storage System](#2-storage-system)
3. [Query Processing Engine](#3-query-processing-engine)
4. [Transaction Management](#4-transaction-management)
5. [Concurrency Control](#5-concurrency-control)
6. [Backup và Recovery](#6-backup-và-recovery)
7. [Replication Architecture](#7-replication-architecture)
8. [Performance Optimization](#8-performance-optimization)
9. [Extensions và Customization](#9-extensions-và-customization)
10. [Monitoring và Troubleshooting](#10-monitoring-và-troubleshooting)

---

## 1. Kiến trúc PostgreSQL

### 1.1 Process Architecture

#### PostgreSQL System Architecture:
```
Client Applications
        │
        ▼
┌─────────────────────────────────────────────────────────┐
│                    PostgreSQL                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐ │
│  │   Postmaster│  │  Background │  │   Shared Memory │ │
│  │   (Main)    │  │  Processes  │  │                 │ │
│  └─────────────┘  └─────────────┘  └─────────────────┘ │
│          │               │                 │           │
│          ▼               ▼                 ▼           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐ │
│  │  Backend    │  │  WAL Writer │  │  Buffer Pool    │ │
│  │  Processes  │  │  Checkpointer│  │  Lock Tables   │ │
│  │             │  │  Autovacuum  │  │  Proc Array    │ │
│  └─────────────┘  └─────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

#### Postmaster Process:
```c
// Simplified postmaster main loop
int PostmasterMain(int argc, char *argv[]) {
    // Initialize shared memory and semaphores
    CreateSharedMemoryAndSemaphores();
    
    // Start background processes
    StartupProcess();
    BgWriterProcess(); 
    CheckpointerProcess();
    WalWriterProcess();
    
    // Main connection handling loop
    for (;;) {
        // Listen for client connections
        port = ServerLoop();
        
        // Fork new backend process for each connection
        BackendStartup(port);
    }
}
```

#### Backend Process Lifecycle:
```
Client Connection Request
        │
        ▼
Postmaster forks Backend Process
        │
        ▼
Authentication & Authorization
        │
        ▼
Query Processing Loop:
├── Parse SQL → Parse Tree
├── Analyze → Query Tree  
├── Plan → Plan Tree
├── Execute → Result
└── Return to client
        │
        ▼
Connection Termination
```

### 1.2 Memory Architecture

#### Shared Memory Components:
```c
// Key shared memory structures
typedef struct SharedMemoryStruct {
    // Buffer pool for data pages
    BufferPool     *buffer_pool;
    
    // Lock manager hash tables  
    LockManager    *lock_mgr;
    
    // Process information array
    ProcessArray   *proc_array;
    
    // WAL insertion locks
    WALInsertLocks *wal_locks;
    
    // Predicate lock manager
    PredicateLocks *pred_locks;
    
    // Background worker slots
    BackgroundWorker *bg_workers;
} SharedMemoryStruct;
```

#### Buffer Pool Management:
```sql
-- Configure buffer pool size
ALTER SYSTEM SET shared_buffers = '2GB';

-- Monitor buffer pool efficiency
SELECT 
    blks_read,
    blks_hit,
    round(blks_hit::numeric / (blks_hit + blks_read) * 100, 2) as hit_ratio
FROM pg_stat_database 
WHERE datname = current_database();

-- Target hit ratio: > 95% for OLTP workloads
```

### 1.3 Background Processes

#### WAL Writer Process:
```c
// WAL Writer main loop (simplified)
void WalWriterMain(void) {
    for (;;) {
        // Check if WAL buffers need flushing
        if (XLogNeedsFlush()) {
            // Flush WAL buffers to disk
            XLogFlush(GetInsertRecPtr());
        }
        
        // Sleep for configured interval
        pg_usleep(wal_writer_delay * 1000L);
    }
}
```

#### Checkpointer Process:
```c
// Checkpointer process responsibilities
void CheckpointerMain(void) {
    for (;;) {
        // Wait for checkpoint request or timeout
        CheckpointerSleep();
        
        // Perform checkpoint
        CreateCheckPoint(CHECKPOINT_CAUSE_TIME);
        
        // Update statistics
        UpdateCheckpointStats();
    }
}

// Checkpoint operations:
// 1. Flush all dirty buffers to disk
// 2. Write checkpoint record to WAL  
// 3. Update control file
```

---

## 2. Storage System

### 2.1 Page Structure

#### PostgreSQL Page Layout:
```
Page (8KB default):
┌─────────────────────────────────┐ ← 0
│         Page Header             │
├─────────────────────────────────┤ ← 24 bytes
│       Item Pointers             │
├─────────────────────────────────┤
│           Free Space            │
├─────────────────────────────────┤
│           Tuples                │
├─────────────────────────────────┤
│         Special Space           │ (for indexes)
└─────────────────────────────────┘ ← 8192 bytes
```

#### Page Header Structure:
```c
typedef struct PageHeaderData {
    XLogRecPtr  pd_lsn;         // LSN of last change
    uint16      pd_checksum;    // Page checksum
    uint16      pd_flags;       // Flag bits
    LocationIndex pd_lower;     // Offset to start of free space
    LocationIndex pd_upper;     // Offset to end of free space  
    LocationIndex pd_special;   // Offset to start of special space
    uint16      pd_pagesize_version; // Page size and version
    TransactionId pd_prune_xid; // Oldest unpruned XMAX
} PageHeaderData;
```

#### Tuple Structure (MVCC):
```c
typedef struct HeapTupleHeaderData {
    TransactionId t_xmin;       // Inserting transaction ID
    TransactionId t_xmax;       // Deleting transaction ID
    CommandId     t_cid;        // Command ID within transaction
    ItemPointerData t_ctid;     // Current TID or new TID
    uint16        t_infomask2;  // Attribute count and flags
    uint16        t_infomask;   // Various flags
    uint8         t_hoff;       // Header length
    // Variable length attributes follow
} HeapTupleHeaderData;
```

### 2.2 MVCC Implementation

#### Transaction Visibility Rules:
```c
// Simplified visibility check
bool HeapTupleSatisfiesMVCC(HeapTuple tuple, Snapshot snapshot) {
    TransactionId xmin = tuple->t_xmin;
    TransactionId xmax = tuple->t_xmax;
    
    // Check if tuple was inserted by a committed transaction
    // that's visible to our snapshot
    if (!TransactionIdDidCommit(xmin) || 
        !XidInMVCCSnapshot(xmin, snapshot)) {
        return false;
    }
    
    // Check if tuple was deleted  
    if (TransactionIdIsValid(xmax)) {
        if (TransactionIdDidCommit(xmax) && 
            XidInMVCCSnapshot(xmax, snapshot)) {
            return false; // Tuple was deleted
        }
    }
    
    return true; // Tuple is visible
}
```

#### MVCC Example at Viettel IDC:
```sql
-- Session 1: Start transaction to update subscriber balance
BEGIN;
UPDATE subscribers SET balance = balance - 100000 
WHERE subscriber_id = 'VT001234567';
-- Don't commit yet

-- Session 2: Read subscriber balance (concurrent)
SELECT balance FROM subscribers WHERE subscriber_id = 'VT001234567';
-- Sees old balance (before update) due to MVCC

-- Session 1: Commit the transaction
COMMIT;

-- Session 2: Read again
SELECT balance FROM subscribers WHERE subscriber_id = 'VT001234567';  
-- Now sees new balance (after update)
```

### 2.3 VACUUM และ Autovacuum

#### VACUUM Theory:
```
MVCC creates tuple versions → Dead tuples accumulate → Need cleanup

Dead Tuple Cleanup Process:
1. Mark dead tuples as reusable space
2. Update visibility map
3. Update free space map  
4. Truncate relation if possible

Types of VACUUM:
- VACUUM: Basic cleanup, non-blocking
- VACUUM FULL: Rewrites entire table, exclusive lock
- VACUUM ANALYZE: Combines cleanup with statistics update
```

#### Autovacuum Configuration:
```sql
-- Global autovacuum settings
ALTER SYSTEM SET autovacuum = on;
ALTER SYSTEM SET autovacuum_max_workers = 3;
ALTER SYSTEM SET autovacuum_naptime = '1min';

-- Per-table autovacuum tuning for high-traffic tables
ALTER TABLE call_records SET (
    autovacuum_vacuum_threshold = 1000,
    autovacuum_vacuum_scale_factor = 0.1,
    autovacuum_analyze_threshold = 500,
    autovacuum_analyze_scale_factor = 0.05
);

-- Monitor autovacuum activity
SELECT 
    schemaname,
    tablename,
    last_vacuum,
    last_autovacuum,
    vacuum_count,
    autovacuum_count,
    n_dead_tup,
    n_live_tup
FROM pg_stat_user_tables 
WHERE n_dead_tup > 1000
ORDER BY n_dead_tup DESC;
```

---

## 3. Query Processing Engine

### 3.1 Parser và Analyzer

#### SQL Parsing Pipeline:
```
Raw SQL Query
     │
     ▼
┌─────────────┐
│   Lexer     │ → Tokens
└─────────────┘
     │
     ▼  
┌─────────────┐
│   Parser    │ → Parse Tree (Raw)
└─────────────┘
     │
     ▼
┌─────────────┐
│  Analyzer   │ → Query Tree (Analyzed)
└─────────────┘
     │
     ▼
┌─────────────┐
│  Rewriter   │ → Query Tree (Rewritten)
└─────────────┘
```

#### Parse Tree Example:
```sql
-- Query
SELECT s.name, COUNT(c.call_id) 
FROM subscribers s JOIN call_records c ON s.id = c.caller_id
WHERE s.status = 'ACTIVE';

-- Simplified Parse Tree Structure
SelectStmt {
    targetList: [
        ResTarget { name: "name", val: ColumnRef {fields: ["s", "name"]} },
        ResTarget { name: "count", val: FuncCall {funcname: ["count"], args: [ColumnRef]} }
    ],
    fromClause: [
        JoinExpr {
            jointype: JOIN_INNER,
            larg: RangeVar {relname: "subscribers", alias: "s"},
            rarg: RangeVar {relname: "call_records", alias: "c"},
            quals: A_Expr {op: "=", lexpr: ColumnRef, rexpr: ColumnRef}
        }
    ],
    whereClause: A_Expr {op: "=", lexpr: ColumnRef, rexpr: Const}
}
```

### 3.2 Query Planner

#### Plan Tree Generation:
```c
// Simplified planner flow
PlannedStmt *planner(Query *parse, int cursorOptions, ParamListInfo boundParams) {
    // Initialize planner context
    PlannerInfo *root = makeNode(PlannerInfo);
    root->parse = parse;
    
    // Generate base relation paths
    set_base_rel_sizes(root);
    set_base_rel_pathlists(root);
    
    // Generate join paths
    make_one_rel_by_joins(root, root->simple_rel_list);
    
    // Choose best path and create plan
    RelOptInfo *final_rel = fetch_upper_rel(root, UPPERREL_FINAL, NULL);
    Path *best_path = final_rel->cheapest_total_path;
    
    return create_plan(root, best_path);
}
```

#### Cost Model:
```c
// PostgreSQL cost model parameters
typedef struct CostParams {
    double seq_page_cost;      // 1.0 (sequential page read)
    double random_page_cost;   // 4.0 (random page read) 
    double cpu_tuple_cost;     // 0.01 (process one tuple)
    double cpu_index_tuple_cost; // 0.005 (process index tuple)
    double cpu_operator_cost;  // 0.0025 (evaluate operator)
    
    // For parallel operations
    double parallel_tuple_cost;   // 0.1
    double parallel_setup_cost;   // 1000.0
} CostParams;

// Index scan cost calculation
Cost cost_index_scan(IndexPath *path) {
    Cost startup_cost = 0;
    Cost run_cost = 0;
    
    // Startup cost: seek to first page
    startup_cost += random_page_cost;
    
    // Run cost: pages read + CPU cost
    run_cost += path->pages * random_page_cost;
    run_cost += path->tuples * cpu_index_tuple_cost;
    
    return startup_cost + run_cost;
}
```

### 3.3 Execution Engine

#### Executor Node Types:
```c
// Major executor node types
typedef enum NodeTag {
    T_SeqScan,          // Sequential scan
    T_IndexScan,        // Index scan
    T_IndexOnlyScan,    // Index-only scan
    T_BitmapHeapScan,   // Bitmap heap scan
    T_NestLoop,         // Nested loop join
    T_HashJoin,         // Hash join
    T_MergeJoin,        // Sort-merge join
    T_Sort,             // Sort operation
    T_Hash,             // Hash table build
    T_Agg,              // Aggregation
    T_WindowAgg,        // Window function
    T_Group,            // GROUP BY
    T_Limit             // LIMIT/OFFSET
} NodeTag;
```

#### Volcano Model Execution:
```c
// Iterator model - each node implements these functions
typedef struct PlanState {
    ExecInitNode();     // Initialize executor state
    ExecProcNode();     // Get next tuple
    ExecEndNode();      // Cleanup
} PlanState;

// Example: Nested Loop Join
TupleTableSlot *ExecNestLoop(NestLoopState *node) {
    PlanState *outerPlan = outerPlanState(node);
    PlanState *innerPlan = innerPlanState(node);
    
    for (;;) {
        // Get outer tuple if needed
        if (node->need_new_outer) {
            outerTuple = ExecProcNode(outerPlan);
            if (TupIsNull(outerTuple)) return NULL;
            node->need_new_outer = false;
        }
        
        // Get next inner tuple
        innerTuple = ExecProcNode(innerPlan);
        if (TupIsNull(innerTuple)) {
            // Rescan inner, get new outer
            ExecReScan(innerPlan);
            node->need_new_outer = true;
            continue;
        }
        
        // Test join condition
        if (ExecQual(node->join_qual, econtext)) {
            return ExecProject(node->projection_info);
        }
    }
}
```

---

## 4. Transaction Management

### 4.1 Transaction ID Management

#### XID Wraparound Problem:
```
PostgreSQL uses 32-bit transaction IDs:
- Valid XIDs: 1 to 4,294,967,295
- XID 0: Invalid/Bootstrap XID
- XIDs wrap around after ~4 billion transactions

Wraparound Prevention:
┌─────────────────────────────────────────────────────────┐
│  Past XIDs     │    Current XID    │    Future XIDs     │
│  (invisible)   │    (visible)      │    (invisible)     │
└─────────────────────────────────────────────────────────┘
        ↑                  ↑                    ↑
   XID - 2^31         Current XID          XID + 2^31

VACUUM FREEZE converts old XIDs to FrozenXID (2)
```

#### Vacuum Freeze Process:
```sql
-- Monitor transaction age
SELECT 
    datname,
    age(datfrozenxid) as xid_age,
    datfrozenxid
FROM pg_database
ORDER BY age(datfrozenxid) DESC;

-- Critical threshold: 200 million XIDs
-- Emergency threshold: 2 billion XIDs

-- Force freeze old tuples
VACUUM FREEZE subscribers;

-- Autovacuum freeze settings
ALTER SYSTEM SET vacuum_freeze_min_age = 50000000;
ALTER SYSTEM SET vacuum_freeze_table_age = 150000000;
ALTER SYSTEM SET autovacuum_freeze_max_age = 200000000;
```

### 4.2 Snapshot Management

#### MVCC Snapshot Structure:
```c
typedef struct SnapshotData {
    TransactionId xmin;     // Oldest XID still running
    TransactionId xmax;     // First XID not yet assigned
    uint32        xcnt;     // Number of XIDs in xip array
    TransactionId *xip;     // Array of running XIDs
    
    // Additional fields for different snapshot types
    CommandId     curcid;   // Current command ID
    bool          copied;   // Is snapshot copied?
} SnapshotData;
```

#### Isolation Level Implementation:
```sql
-- READ COMMITTED: New snapshot for each statement
BEGIN;
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;
SELECT balance FROM accounts WHERE id = 1; -- Snapshot S1
-- Other transaction commits changes
SELECT balance FROM accounts WHERE id = 1; -- Snapshot S2 (new)
COMMIT;

-- REPEATABLE READ: Single snapshot for entire transaction  
BEGIN;
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
SELECT balance FROM accounts WHERE id = 1; -- Snapshot S1
-- Other transaction commits changes  
SELECT balance FROM accounts WHERE id = 1; -- Same snapshot S1
COMMIT;

-- SERIALIZABLE: SSI (Serializable Snapshot Isolation)
BEGIN;
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;
-- Uses predicate locking to detect serialization conflicts
SELECT SUM(balance) FROM accounts WHERE branch = 'Hanoi';
-- If conflicting transaction detected, one will be aborted
COMMIT;
```

---

## 5. Concurrency Control

### 5.1 Lock Management

#### Lock Hierarchy:
```
Database Level
    │
    ├── Schema Level
    │       │
    │       ├── Table Level
    │       │       │
    │       │       ├── Page Level (rare)
    │       │       │
    │       │       └── Tuple Level
    │       │
    │       └── Index Level
    │
    └── Tablespace Level
```

#### Lock Modes:
```sql
-- PostgreSQL lock modes (weakest to strongest)
-- 1. AccessShareLock (SELECT)
SELECT * FROM subscribers;

-- 2. RowShareLock (SELECT FOR UPDATE/SHARE)
SELECT * FROM subscribers WHERE id = 1 FOR UPDATE;

-- 3. RowExclusiveLock (INSERT, UPDATE, DELETE)
UPDATE subscribers SET balance = balance - 100 WHERE id = 1;

-- 4. ShareUpdateExclusiveLock (VACUUM, ANALYZE)
VACUUM subscribers;

-- 5. ShareLock (CREATE INDEX)
CREATE INDEX CONCURRENTLY idx_phone ON subscribers(phone);

-- 6. ShareRowExclusiveLock (rare)

-- 7. ExclusiveLock (most operations requiring exclusive access)
LOCK TABLE subscribers IN EXCLUSIVE MODE;

-- 8. AccessExclusiveLock (ALTER TABLE, DROP TABLE)
DROP TABLE old_subscribers;
```

#### Lock Compatibility Matrix:
```
           AS  RS  RE  SU  S   SRE EX  AE
AS  (✓)    ✓   ✓   ✓   ✓   ✓   ✓   ✗   ✗
RS         ✓   ✓   ✓   ✓   ✓   ✗   ✗   ✗  
RE         ✓   ✓   ✓   ✗   ✗   ✗   ✗   ✗
SU         ✓   ✓   ✗   ✗   ✗   ✗   ✗   ✗
S          ✓   ✓   ✗   ✗   ✓   ✗   ✗   ✗
SRE        ✓   ✗   ✗   ✗   ✗   ✗   ✗   ✗
EX         ✗   ✗   ✗   ✗   ✗   ✗   ✗   ✗
AE         ✗   ✗   ✗   ✗   ✗   ✗   ✗   ✗

✓ = Compatible, ✗ = Conflicts
```

### 5.2 Deadlock Detection và Resolution

#### Deadlock Detection Algorithm:
```c
// Deadlock detector (simplified)
bool DeadLockCheck(PGPROC *proc) {
    // Build wait-for graph
    EDGE *edges = BuildWaitGraph();
    
    // DFS to detect cycles
    for (int i = 0; i < num_procs; i++) {
        if (HasCycle(edges, i)) {
            // Choose victim (youngest transaction)
            PGPROC *victim = ChooseDeadlockVictim(cycle);
            
            // Abort victim transaction
            AbortTransaction(victim);
            return true;
        }
    }
    return false;
}
```

#### Deadlock Example tại Viettel IDC:
```sql
-- Transaction T1: Transfer from Account A to Account B
BEGIN;
UPDATE accounts SET balance = balance - 1000000 WHERE account_id = 'A';
-- Wait for lock on account B

-- Transaction T2: Transfer from Account B to Account A  
BEGIN;
UPDATE accounts SET balance = balance - 500000 WHERE account_id = 'B';
-- Wait for lock on account A → DEADLOCK!

-- PostgreSQL detects deadlock and aborts one transaction:
-- ERROR: deadlock detected
-- DETAIL: Process 12345 waits for ShareLock on transaction 67890
-- HINT: See server log for query details.
```

### 5.3 Advisory Locks

#### Application-level Locking:
```sql
-- Acquire advisory lock for custom synchronization
SELECT pg_advisory_lock(12345);

-- Example: Prevent concurrent balance updates for same subscriber
CREATE OR REPLACE FUNCTION safe_balance_update(
    p_subscriber_id TEXT,
    p_amount NUMERIC
) RETURNS BOOLEAN AS $$
DECLARE
    lock_id BIGINT;
    current_balance NUMERIC;
BEGIN
    -- Generate consistent lock ID from subscriber_id
    lock_id := ('x' || substr(md5(p_subscriber_id), 1, 8))::bit(32)::bigint;
    
    -- Acquire advisory lock
    PERFORM pg_advisory_lock(lock_id);
    
    -- Safe balance update
    SELECT balance INTO current_balance 
    FROM subscribers WHERE subscriber_id = p_subscriber_id;
    
    IF current_balance >= p_amount THEN
        UPDATE subscribers 
        SET balance = balance - p_amount 
        WHERE subscriber_id = p_subscriber_id;
        
        -- Release lock
        PERFORM pg_advisory_unlock(lock_id);
        RETURN TRUE;
    ELSE
        -- Release lock  
        PERFORM pg_advisory_unlock(lock_id);
        RETURN FALSE;
    END IF;
END;
$$ LANGUAGE plpgsql;
```

---

## 6. Backup và Recovery

### 6.1 Write-Ahead Logging (WAL)

#### WAL Record Structure:
```c
typedef struct XLogRecord {
    uint32      xl_tot_len;     // Total length of record
    TransactionId xl_xid;       // Transaction ID
    XLogRecPtr  xl_prev;        // Pointer to previous record
    uint8       xl_info;        // Operation info
    RmgrId      xl_rmid;        // Resource manager ID
    pg_crc32c   xl_crc;         // CRC checksum
    // Variable length data follows
} XLogRecord;
```

#### WAL Operations:
```sql
-- Configure WAL settings for durability vs performance
ALTER SYSTEM SET wal_level = 'replica';           -- Enables replication
ALTER SYSTEM SET max_wal_size = '2GB';            -- WAL file size limit
ALTER SYSTEM SET checkpoint_completion_target = 0.9; -- Spread checkpoint I/O
ALTER SYSTEM SET synchronous_commit = on;         -- Wait for WAL flush

-- WAL archiving for PITR
ALTER SYSTEM SET archive_mode = on;
ALTER SYSTEM SET archive_command = 'cp %p /backup/archive/%f';

-- Monitor WAL generation
SELECT 
    pg_current_wal_lsn(),
    pg_walfile_name(pg_current_wal_lsn()),
    pg_wal_lsn_diff(pg_current_wal_lsn(), '0/0') as total_wal_bytes;
```

### 6.2 Point-in-Time Recovery (PITR)

#### PITR Setup Process:
```bash
# 1. Base backup
pg_basebackup -D /backup/base -Ft -z -P -U postgres

# 2. Continuous WAL archiving (already configured)
# archive_command = 'cp %p /backup/archive/%f'

# 3. Recovery scenario
# Stop PostgreSQL
systemctl stop postgresql

# 4. Restore base backup
cd /var/lib/postgresql
rm -rf 13/main/*
tar -xzf /backup/base/base.tar.gz -C 13/main/
tar -xzf /backup/base/pg_wal.tar.gz -C 13/main/pg_wal/

# 5. Create recovery.signal file
touch 13/main/recovery.signal

# 6. Configure recovery
cat > 13/main/postgresql.auto.conf << EOF
restore_command = 'cp /backup/archive/%f %p'
recovery_target_time = '2024-01-15 10:30:00'
recovery_target_action = 'promote'
EOF

# 7. Start recovery
systemctl start postgresql
```

#### Recovery Scenarios:
```sql
-- Recovery to specific time
recovery_target_time = '2024-01-15 10:30:00+07'

-- Recovery to specific transaction
recovery_target_xid = '12345678'

-- Recovery to specific LSN
recovery_target_lsn = '0/15000028'

-- Recovery to named restore point
SELECT pg_create_restore_point('before_major_update');
recovery_target_name = 'before_major_update'
```

### 6.3 Physical vs Logical Backup

#### pg_dump vs pg_basebackup:
```bash
# Logical backup with pg_dump
pg_dump -h localhost -U postgres \
        -d viettel_billing \
        -f billing_backup.sql \
        --verbose \
        --compress=9

# Parallel logical backup  
pg_dump -h localhost -U postgres \
        -d viettel_billing \
        -Fd \  # Directory format
        -j 4 \ # 4 parallel jobs
        -f billing_backup_dir

# Physical backup with pg_basebackup
pg_basebackup -D /backup/physical \
              -Ft \  # Tar format
              -z \   # Compress
              -P \   # Progress
              -U postgres \
              -h localhost

# Incremental backup simulation
pg_basebackup -D /backup/incremental \
              --wal-method=stream \
              -U postgres
```

---

## 7. Replication Architecture

### 7.1 Streaming Replication

#### Master-Slave Configuration:
```sql
-- Master configuration (postgresql.conf)
wal_level = replica
max_wal_senders = 3
archive_mode = on
archive_command = 'cp %p /archive/%f'

-- Master authentication (pg_hba.conf)
host replication replica 192.168.1.0/24 md5

-- Create replication user
CREATE USER replica REPLICATION LOGIN ENCRYPTED PASSWORD 'replica_password';
```

```bash
# Slave setup
# 1. Base backup from master
pg_basebackup -h master_ip -D /var/lib/postgresql/13/main -U replica -W

# 2. Slave configuration (postgresql.conf)
hot_standby = on
max_standby_streaming_delay = 30s
max_standby_archive_delay = 60s

# 3. Recovery configuration (postgresql.auto.conf)
primary_conninfo = 'host=master_ip port=5432 user=replica password=replica_password'
primary_slot_name = 'replica_slot'

# 4. Create recovery.signal
touch /var/lib/postgresql/13/main/recovery.signal

# 5. Start slave
systemctl start postgresql
```

#### Replication Slots:
```sql
-- Create replication slot on master
SELECT pg_create_physical_replication_slot('replica_slot');

-- Monitor replication slots
SELECT 
    slot_name,
    slot_type,
    active,
    xmin,
    restart_lsn,
    confirmed_flush_lsn
FROM pg_replication_slots;

-- Monitor replication lag
SELECT 
    client_addr,
    state,
    sent_lsn,
    write_lsn,
    flush_lsn,
    replay_lsn,
    pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn) as lag_bytes
FROM pg_stat_replication;
```

### 7.2 Logical Replication

#### Publication and Subscription:
```sql
-- Master: Create publication
CREATE PUBLICATION viettel_billing_pub FOR TABLE 
    subscribers, call_records, billing_transactions;

-- Slave: Create subscription
CREATE SUBSCRIPTION viettel_billing_sub 
CONNECTION 'host=master_ip dbname=viettel_billing user=replica password=replica_password'
PUBLICATION viettel_billing_pub;

-- Monitor logical replication
SELECT 
    subname,
    pid,
    received_lsn,
    latest_end_lsn,
    latest_end_time
FROM pg_stat_subscription;

-- Logical replication worker status
SELECT 
    subscription_name,
    worker_type,
    pid,
    leader_pid,
    relid,
    received_lsn,
    last_msg_send_time,
    last_msg_receipt_time,
    latest_end_lsn,
    latest_end_time
FROM pg_stat_subscription_workers;
```

### 7.3 High Availability Setup

#### Patroni + etcd Configuration:
```yaml
# Patroni configuration (patroni.yml)
scope: viettel-postgres-cluster
namespace: /db/
name: postgres01

restapi:
    listen: 0.0.0.0:8008
    connect_address: 192.168.1.10:8008

etcd:
    hosts: 192.168.1.20:2379,192.168.1.21:2379,192.168.1.22:2379

bootstrap:
    dcs:
        ttl: 30
        loop_wait: 10
        retry_timeout: 30
        maximum_lag_on_failover: 1048576
        postgresql:
            use_pg_rewind: true
            parameters:
                wal_level: replica
                hot_standby: "on"
                max_connections: 100
                max_wal_senders: 3
                wal_keep_segments: 8

    initdb:
        - encoding: UTF8
        - data-checksums

postgresql:
    listen: 0.0.0.0:5432
    connect_address: 192.168.1.10:5432
    data_dir: /var/lib/postgresql/13/main
    bin_dir: /usr/lib/postgresql/13/bin
    pgpass: /tmp/pgpass0
    authentication:
        replication:
            username: replica
            password: replica_password
        superuser:
            username: postgres
            password: postgres_password

tags:
    nofailover: false
    noloadbalance: false
    clonefrom: false
    nosync: false
```

---

## 8. Performance Optimization

### 8.1 Query Optimization

#### EXPLAIN Analysis:
```sql
-- Detailed query analysis
EXPLAIN (ANALYZE, BUFFERS, COSTS, VERBOSE) 
SELECT 
    s.subscriber_id,
    s.name,
    COUNT(c.call_id) as call_count,
    SUM(c.duration_seconds) as total_duration
FROM subscribers s
JOIN call_records c ON s.subscriber_id = c.caller_id
WHERE s.status = 'ACTIVE' 
  AND c.call_date >= '2024-01-01'
  AND c.call_date < '2024-02-01'
GROUP BY s.subscriber_id, s.name
HAVING COUNT(c.call_id) > 100
ORDER BY total_duration DESC
LIMIT 1000;

-- Sample output analysis:
/*
Limit  (cost=25000.00..25002.50 rows=1000 width=64) 
       (actual time=1250.123..1250.789 rows=1000 loops=1)
  Buffers: shared hit=15000 read=5000 dirtied=100
  ->  Sort  (cost=25000.00..25500.00 rows=200000 width=64) 
             (actual time=1248.456..1249.123 rows=1000 loops=1)
        Sort Key: (sum(c.duration_seconds)) DESC
        Sort Method: top-N heapsort  Memory: 25kB
        Buffers: shared hit=15000 read=5000 dirtied=100
        ->  HashAggregate  (cost=20000.00..22000.00 rows=200000 width=64) 
                          (actual time=1100.123..1200.456 rows=180000 loops=1)
              Group Key: s.subscriber_id, s.name
              Planned Partitions: 4  Batches: 1  Memory Usage: 32MB
              Buffers: shared hit=15000 read=5000 dirtied=100
              ->  Hash Join  (cost=5000.00..15000.00 rows=1000000 width=32) 
                            (actual time=50.123..800.456 rows=950000 loops=1)
                    Hash Cond: (c.caller_id = s.subscriber_id)
                    Buffers: shared hit=15000 read=5000 dirtied=100
                    ->  Bitmap Heap Scan on call_records c  
                        (cost=1000.00..8000.00 rows=1000000 width=24) 
                        (actual time=20.123..400.456 rows=950000 loops=1)
                          Recheck Cond: ((call_date >= '2024-01-01') AND (call_date < '2024-02-01'))
                          Heap Blocks: exact=5000
                          Buffers: shared hit=4000 read=1000
                          ->  Bitmap Index Scan on idx_call_date  
                              (cost=0.00..750.00 rows=1000000 width=0) 
                              (actual time=15.123..15.123 rows=950000 loops=1)
                                Index Cond: ((call_date >= '2024-01-01') AND (call_date < '2024-02-01'))
                                Buffers: shared hit=50
                    ->  Hash  (cost=3000.00..3000.00 rows=100000 width=32) 
                              (actual time=25.456..25.456 rows=95000 loops=1)
                          Buckets: 131072  Batches: 1  Memory Usage: 6MB
                          Buffers: shared hit=2000
                          ->  Index Scan using idx_subscriber_status on subscribers s  
                              (cost=0.00..3000.00 rows=100000 width=32) 
                              (actual time=0.123..20.456 rows=95000 loops=1)
                                Index Cond: (status = 'ACTIVE')
                                Buffers: shared hit=2000
Planning Time: 2.123 ms
Execution Time: 1252.456 ms
*/
```

#### Index Strategy:
```sql
-- Composite index for common query patterns
CREATE INDEX idx_call_records_optimized 
ON call_records(caller_id, call_date, call_status) 
INCLUDE (duration_seconds, call_cost);

-- Partial index for active subscribers only
CREATE INDEX idx_active_subscribers 
ON subscribers(subscriber_id) 
WHERE status = 'ACTIVE';

-- Expression index for case-insensitive searches
CREATE INDEX idx_subscriber_name_lower 
ON subscribers(LOWER(name));

-- GIN index for full-text search
CREATE INDEX idx_subscriber_search 
ON subscribers USING GIN(to_tsvector('english', name || ' ' || phone_number));
```

### 8.2 Configuration Tuning

#### Memory Configuration:
```sql
-- Memory settings for OLTP workload
ALTER SYSTEM SET shared_buffers = '8GB';           -- 25% of RAM
ALTER SYSTEM SET effective_cache_size = '24GB';    -- 75% of RAM  
ALTER SYSTEM SET work_mem = '256MB';                -- Per operation
ALTER SYSTEM SET maintenance_work_mem = '2GB';     -- VACUUM, CREATE INDEX
ALTER SYSTEM SET wal_buffers = '64MB';             -- WAL buffer size

-- Connection settings
ALTER SYSTEM SET max_connections = 200;
ALTER SYSTEM SET superuser_reserved_connections = 3;

-- Checkpoint settings  
ALTER SYSTEM SET checkpoint_timeout = '15min';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET max_wal_size = '4GB';
ALTER SYSTEM SET min_wal_size = '1GB';

-- Query planner settings
ALTER SYSTEM SET random_page_cost = 1.1;           -- SSD storage
ALTER SYSTEM SET effective_io_concurrency = 200;   -- SSD concurrency
ALTER SYSTEM SET default_statistics_target = 1000; -- Better statistics
```

### 8.3 Monitoring và Alerting

#### Performance Monitoring Queries:
```sql
-- Top slow queries
SELECT 
    query,
    calls,
    total_time / 1000 as total_time_seconds,
    mean_time / 1000 as mean_time_seconds,
    rows,
    100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
FROM pg_stat_statements 
ORDER BY total_time DESC 
LIMIT 20;

-- Index usage statistics
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_tup_read,
    idx_tup_fetch,
    idx_scan,
    idx_tup_read / NULLIF(idx_scan, 0) as avg_tuples_per_scan
FROM pg_stat_user_indexes 
ORDER BY idx_scan DESC;

-- Table bloat analysis
WITH table_stats AS (
    SELECT 
        schemaname,
        tablename,
        n_dead_tup,
        n_live_tup,
        round(100 * n_dead_tup / NULLIF(n_live_tup + n_dead_tup, 0), 2) as dead_tuple_percent
    FROM pg_stat_user_tables
)
SELECT * FROM table_stats 
WHERE dead_tuple_percent > 10 
ORDER BY dead_tuple_percent DESC;

-- Replication lag monitoring
SELECT 
    client_addr,
    application_name,
    state,
    pg_wal_lsn_diff(pg_current_wal_lsn(), sent_lsn) as send_lag,
    pg_wal_lsn_diff(sent_lsn, write_lsn) as write_lag,
    pg_wal_lsn_diff(write_lsn, flush_lsn) as flush_lag,
    pg_wal_lsn_diff(flush_lsn, replay_lsn) as replay_lag
FROM pg_stat_replication;
```

---

## 9. Extensions và Customization

### 9.1 Popular Extensions

#### pg_stat_statements:
```sql
-- Enable query statistics collection
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Configure tracking
ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';
ALTER SYSTEM SET pg_stat_statements.max = 10000;
ALTER SYSTEM SET pg_stat_statements.track = 'all';
ALTER SYSTEM SET pg_stat_statements.track_utility = on;

-- Query performance analysis
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    stddev_time,
    rows,
    100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
FROM pg_stat_statements 
WHERE calls > 100
ORDER BY mean_time DESC;
```

#### PostGIS for Geographic Data:
```sql
-- Install PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;

-- Viettel tower locations
CREATE TABLE tower_locations (
    tower_id VARCHAR(20) PRIMARY KEY,
    tower_name VARCHAR(100),
    location GEOMETRY(POINT, 4326),  -- WGS84 coordinate system
    coverage_radius INTEGER,        -- meters
    province VARCHAR(50),
    installation_date DATE
);

-- Add spatial index
CREATE INDEX idx_tower_location ON tower_locations USING GIST(location);

-- Find towers within 5km of Hanoi center
SELECT 
    tower_id,
    tower_name,
    ST_Distance(location, ST_GeomFromText('POINT(105.8342 21.0278)', 4326)) as distance_degrees,
    ST_Distance(
        ST_Transform(location, 3405),  -- Transform to meters
        ST_Transform(ST_GeomFromText('POINT(105.8342 21.0278)', 4326), 3405)
    ) as distance_meters
FROM tower_locations 
WHERE ST_DWithin(
    ST_Transform(location, 3405),
    ST_Transform(ST_GeomFromText('POINT(105.8342 21.0278)', 4326), 3405),
    5000  -- 5km in meters
)
ORDER BY distance_meters;
```

### 9.2 Custom Functions

#### PL/pgSQL for Business Logic:
```sql
-- Complex billing calculation function
CREATE OR REPLACE FUNCTION calculate_bill(
    p_subscriber_id VARCHAR(20),
    p_billing_month DATE
) RETURNS TABLE(
    subscriber_id VARCHAR(20),
    base_fee NUMERIC(10,2),
    call_charges NUMERIC(10,2),
    sms_charges NUMERIC(10,2),
    data_charges NUMERIC(10,2),
    total_bill NUMERIC(10,2)
) AS $$
DECLARE
    v_plan_id VARCHAR(20);
    v_base_fee NUMERIC(10,2);
    v_included_minutes INTEGER;
    v_included_sms INTEGER;
    v_included_data_mb INTEGER;
    v_overage_rate_voice NUMERIC(6,4);
    v_overage_rate_sms NUMERIC(6,4);
    v_overage_rate_data NUMERIC(6,4);
BEGIN
    -- Get subscriber plan details
    SELECT s.plan_id, p.base_fee, p.included_minutes, p.included_sms, 
           p.included_data_mb, p.overage_rate_voice, p.overage_rate_sms, p.overage_rate_data
    INTO v_plan_id, v_base_fee, v_included_minutes, v_included_sms, 
         v_included_data_mb, v_overage_rate_voice, v_overage_rate_sms, v_overage_rate_data
    FROM subscribers s
    JOIN service_plans p ON s.plan_id = p.plan_id
    WHERE s.subscriber_id = p_subscriber_id;
    
    -- Calculate call charges
    WITH call_usage AS (
        SELECT 
            COALESCE(SUM(duration_seconds), 0) / 60.0 as total_minutes
        FROM call_records 
        WHERE caller_id = p_subscriber_id 
          AND date_trunc('month', call_date) = date_trunc('month', p_billing_month)
    ),
    call_calc AS (
        SELECT 
            v_base_fee as base_fee,
            CASE 
                WHEN total_minutes <= v_included_minutes THEN 0
                ELSE (total_minutes - v_included_minutes) * v_overage_rate_voice
            END as call_charges
        FROM call_usage
    ),
    -- Calculate SMS charges
    sms_usage AS (
        SELECT 
            COALESCE(COUNT(*), 0) as total_sms
        FROM sms_records 
        WHERE sender_id = p_subscriber_id 
          AND date_trunc('month', sent_date) = date_trunc('month', p_billing_month)
    ),
    sms_calc AS (
        SELECT 
            CASE 
                WHEN total_sms <= v_included_sms THEN 0
                ELSE (total_sms - v_included_sms) * v_overage_rate_sms
            END as sms_charges
        FROM sms_usage
    ),
    -- Calculate data charges
    data_usage AS (
        SELECT 
            COALESCE(SUM(data_mb), 0) as total_data_mb
        FROM data_usage_records 
        WHERE subscriber_id = p_subscriber_id 
          AND date_trunc('month', usage_date) = date_trunc('month', p_billing_month)
    ),
    data_calc AS (
        SELECT 
            CASE 
                WHEN total_data_mb <= v_included_data_mb THEN 0
                ELSE (total_data_mb - v_included_data_mb) * v_overage_rate_data
            END as data_charges
        FROM data_usage
    )
    -- Return final calculation
    SELECT 
        p_subscriber_id,
        c.base_fee,
        c.call_charges,
        s.sms_charges,
        d.data_charges,
        c.base_fee + c.call_charges + s.sms_charges + d.data_charges as total_bill
    FROM call_calc c, sms_calc s, data_calc d;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Usage example
SELECT * FROM calculate_bill('VT001234567', '2024-01-01');
```

---

## 10. Monitoring và Troubleshooting

### 10.1 Performance Monitoring

#### Built-in Statistics Views:
```sql
-- Database-level statistics
SELECT 
    datname,
    numbackends as active_connections,
    xact_commit,
    xact_rollback,
    round(100.0 * xact_rollback / NULLIF(xact_commit + xact_rollback, 0), 2) as rollback_ratio,
    blks_read,
    blks_hit,
    round(100.0 * blks_hit / NULLIF(blks_hit + blks_read, 0), 2) as cache_hit_ratio,
    tup_returned,
    tup_fetched,
    tup_inserted,
    tup_updated,
    tup_deleted,
    conflicts,
    temp_files,
    temp_bytes,
    deadlocks
FROM pg_stat_database 
WHERE datname = current_database();

-- Table-level I/O statistics
SELECT 
    schemaname,
    tablename,
    heap_blks_read,
    heap_blks_hit,
    round(100.0 * heap_blks_hit / NULLIF(heap_blks_hit + heap_blks_read, 0), 2) as heap_hit_ratio,
    idx_blks_read,
    idx_blks_hit,
    round(100.0 * idx_blks_hit / NULLIF(idx_blks_hit + idx_blks_read, 0), 2) as idx_hit_ratio,
    toast_blks_read,
    toast_blks_hit,
    tidx_blks_read,
    tidx_blks_hit
FROM pg_statio_user_tables 
ORDER BY heap_blks_read + idx_blks_read DESC;
```

### 10.2 Lock Monitoring

#### Active Locks Analysis:
```sql
-- Current lock waits
SELECT 
    blocked_locks.pid AS blocked_pid,
    blocked_activity.usename AS blocked_user,
    blocking_locks.pid AS blocking_pid,
    blocking_activity.usename AS blocking_user,
    blocked_activity.query AS blocked_statement,
    blocking_activity.query AS current_statement_in_blocking_process,
    blocked_activity.application_name AS blocked_application,
    blocking_activity.application_name AS blocking_application,
    blocked_locks.mode AS blocked_mode,
    blocking_locks.mode AS blocking_mode,
    blocked_activity.query_start AS blocked_query_start,
    blocking_activity.query_start AS blocking_query_start
FROM pg_catalog.pg_locks blocked_locks
    JOIN pg_catalog.pg_stat_activity blocked_activity 
        ON blocked_activity.pid = blocked_locks.pid
    JOIN pg_catalog.pg_locks blocking_locks 
        ON blocking_locks.locktype = blocked_locks.locktype
        AND blocking_locks.DATABASE IS NOT DISTINCT FROM blocked_locks.DATABASE
        AND blocking_locks.relation IS NOT DISTINCT FROM blocked_locks.relation
        AND blocking_locks.page IS NOT DISTINCT FROM blocked_locks.page
        AND blocking_locks.tuple IS NOT DISTINCT FROM blocked_locks.tuple
        AND blocking_locks.virtualxid IS NOT DISTINCT FROM blocked_locks.virtualxid
        AND blocking_locks.transactionid IS NOT DISTINCT FROM blocked_locks.transactionid
        AND blocking_locks.classid IS NOT DISTINCT FROM blocked_locks.classid
        AND blocking_locks.objid IS NOT DISTINCT FROM blocked_locks.objid
        AND blocking_locks.objsubid IS NOT DISTINCT FROM blocked_locks.objsubid
        AND blocking_locks.pid != blocked_locks.pid
    JOIN pg_catalog.pg_stat_activity blocking_activity 
        ON blocking_activity.pid = blocking_locks.pid
WHERE NOT blocked_locks.GRANTED;
```

### 10.3 Troubleshooting Common Issues

#### Connection Exhaustion:
```sql
-- Check connection usage
SELECT 
    count(*) as total_connections,
    count(*) FILTER (WHERE state = 'active') as active_connections,
    count(*) FILTER (WHERE state = 'idle') as idle_connections,
    count(*) FILTER (WHERE state = 'idle in transaction') as idle_in_transaction
FROM pg_stat_activity;

-- Find long-running queries
SELECT 
    pid,
    user,
    application_name,
    client_addr,
    query_start,
    state_change,
    state,
    query
FROM pg_stat_activity 
WHERE state != 'idle' 
  AND query_start < NOW() - INTERVAL '5 minutes'
ORDER BY query_start;

-- Terminate problematic connections
SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE state = 'idle in transaction' 
  AND state_change < NOW() - INTERVAL '1 hour';
```

#### Bloat Management:
```sql
-- Check table bloat
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
    n_dead_tup,
    n_live_tup,
    round(100 * n_dead_tup / NULLIF(n_live_tup + n_dead_tup, 0), 2) as bloat_ratio
FROM pg_stat_user_tables 
WHERE n_dead_tup > 1000
ORDER BY n_dead_tup DESC;

-- Vacuum recommendations
SELECT 
    schemaname,
    tablename,
    last_vacuum,
    last_autovacuum,
    vacuum_count,
    autovacuum_count,
    CASE 
        WHEN last_autovacuum IS NULL AND last_vacuum IS NULL THEN 'NEVER VACUUMED'
        WHEN last_autovacuum < NOW() - INTERVAL '1 day' THEN 'VACUUM OVERDUE'
        ELSE 'OK'
    END as vacuum_status
FROM pg_stat_user_tables
ORDER BY 
    CASE 
        WHEN last_autovacuum IS NULL THEN '1900-01-01'::timestamp
        ELSE last_autovacuum 
    END;
```

---

## 📚 Tham khảo Chuyên sâu

### Documentation:
1. **PostgreSQL Official Documentation** - https://www.postgresql.org/docs/
2. **PostgreSQL Wiki** - https://wiki.postgresql.org/
3. **PostgreSQL Source Code** - https://git.postgresql.org/

### Sách chuyên ngành:
1. **"PostgreSQL: Up and Running"** - Regina Obe, Leo Hsu
2. **"PostgreSQL High Performance"** - Gregory Smith
3. **"PostgreSQL Administration Cookbook"** - Simon Riggs, Gianni Ciolli
4. **"Mastering PostgreSQL in Application Development"** - Dimitri Fontaine

### Công cụ Monitoring:
1. **pgAdmin** - Web-based administration
2. **pgBench** - Performance testing
3. **pg_stat_statements** - Query statistics  
4. **pg_badger** - Log analyzer
5. **Patroni** - High availability
6. **pgBouncer** - Connection pooling

### Viettel IDC Specific:
- **Subscriber Database**: 50M+ records, 24/7 availability
- **Call Detail Records**: 1B+ records/month, real-time ingestion
- **Billing System**: ACID compliance, sub-second response
- **Geographic Data**: Tower locations, coverage analysis with PostGIS
