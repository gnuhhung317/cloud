# Database Fundamentals Theory
# Lý thuyết Cơ bản về Cơ sở Dữ liệu

## 📚 Mục lục
1. [Lý thuyết Cơ sở Dữ liệu Cơ bản](#1-lý-thuyết-cơ-sở-dữ-liệu-cơ-bản)
2. [Mô hình Dữ liệu](#2-mô-hình-dữ-liệu)
3. [ACID Properties](#3-acid-properties)
4. [CAP Theorem](#4-cap-theorem)
5. [Consistency Models](#5-consistency-models)
6. [Database Architecture](#6-database-architecture)
7. [Storage Engines](#7-storage-engines)
8. [Indexing Theory](#8-indexing-theory)
9. [Query Processing](#9-query-processing)
10. [Transaction Management](#10-transaction-management)

---

## 1. Lý thuyết Cơ sở Dữ liệu Cơ bản

### 1.1 Định nghĩa và Khái niệm
**Cơ sở dữ liệu (Database)** là một tập hợp có tổ chức các dữ liệu liên quan được lưu trữ và truy cập điện tử từ hệ thống máy tính.

#### Thành phần chính:
- **Data**: Thông tin thô được lưu trữ
- **Database Management System (DBMS)**: Phần mềm quản lý cơ sở dữ liệu
- **Database Schema**: Cấu trúc logic của cơ sở dữ liệu
- **Database Instance**: Dữ liệu thực tế tại một thời điểm cụ thể

### 1.2 Lịch sử Phát triển
```
1960s: Hierarchical & Network Models
├── IMS (IBM Information Management System)
└── CODASYL (Conference on Data Systems Languages)

1970s: Relational Model
├── Edgar F. Codd's 12 Rules
├── SQL (Structured Query Language)
└── First commercial RDBMS

1980s-1990s: Object-Oriented Databases
├── Object-Relational Mapping
└── Extended Relational Model

2000s-Present: NoSQL Movement
├── Document Databases (MongoDB)
├── Key-Value Stores (Redis)
├── Column-Family (Cassandra)
└── Graph Databases (Neo4j)
```

### 1.3 Tầm quan trọng trong Enterprise
**Tại Viettel IDC:**
- **Telecommunications Data**: Call Detail Records (CDR), subscriber data
- **Billing Systems**: Real-time charging, invoice generation
- **Network Management**: Configuration data, performance metrics
- **Customer Relationship Management**: User profiles, service history

---

## 2. Mô hình Dữ liệu

### 2.1 Relational Model (Mô hình Quan hệ)

#### Lý thuyết cốt lõi:
**Relation (Quan hệ)**: Tập hợp các tuple có cùng schema
- **Tuple**: Một hàng trong bảng
- **Attribute**: Một cột trong bảng
- **Domain**: Tập hợp các giá trị có thể của attribute

#### Codd's 12 Rules:
1. **Information Rule**: Tất cả thông tin được biểu diễn dưới dạng bảng
2. **Guaranteed Access Rule**: Mỗi giá trị có thể truy cập qua tên bảng + khóa chính + tên cột
3. **Systematic Treatment of Null Values**: Null values được xử lý nhất quán
4. **Dynamic Online Catalog**: Metadata được lưu trữ như dữ liệu thường
5. **Comprehensive Data Sublanguage**: Ngôn ngữ truy vấn hoàn chỉnh (SQL)

#### Normalization Theory:
```sql
-- First Normal Form (1NF): Atomic values
CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    customer_name VARCHAR(100),
    product_name VARCHAR(100),  -- Atomic, not comma-separated
    quantity INTEGER
);

-- Second Normal Form (2NF): Remove partial dependencies
CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    customer_name VARCHAR(100),
    customer_address TEXT
);

CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(customer_id),
    order_date DATE
);

-- Third Normal Form (3NF): Remove transitive dependencies
CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    product_name VARCHAR(100),
    category_id INTEGER REFERENCES categories(category_id)
);

-- Boyce-Codd Normal Form (BCNF): Every determinant is a candidate key
```

### 2.2 Document Model (Mô hình Tài liệu)

#### Lý thuyết Document Database:
**Document**: Cấu trúc dữ liệu self-contained (thường JSON/BSON)

```javascript
// Document structure example
{
  "_id": ObjectId("60d5ec49f1b2c8b1f8e4e1a1"),
  "customer": {
    "name": "Nguyen Van A",
    "email": "nguyenvana@viettel.com.vn",
    "address": {
      "street": "123 Duong Lang",
      "city": "Ha Noi",
      "country": "Vietnam"
    }
  },
  "orders": [
    {
      "order_id": "ORD-001",
      "products": [
        {"name": "iPhone 13", "price": 20000000, "quantity": 1}
      ],
      "total": 20000000,
      "order_date": ISODate("2021-06-25T10:30:00Z")
    }
  ],
  "tags": ["premium", "mobile", "individual"]
}
```

#### Ưu điểm Document Model:
- **Schema Flexibility**: Không cần định nghĩa cấu trúc trước
- **Natural Data Representation**: Phù hợp với object-oriented programming
- **Horizontal Scaling**: Dễ dàng sharding
- **Performance**: Ít join operations

### 2.3 Key-Value Model

#### Lý thuyết Key-Value Store:
**Abstraction**: Simple associative array (hash table)

```python
# Conceptual representation
database = {
    "user:1001": {
        "name": "Nguyen Van A",
        "last_login": "2024-01-15T08:30:00Z",
        "session_token": "abc123xyz"
    },
    "cart:user:1001": [
        {"product_id": "P001", "quantity": 2},
        {"product_id": "P002", "quantity": 1}
    ],
    "counter:page_views": 1523678
}
```

#### Use Cases at Viettel IDC:
- **Session Management**: User sessions, authentication tokens
- **Caching Layer**: Frequently accessed data (Redis)
- **Real-time Analytics**: Counter values, metrics
- **Configuration Storage**: System settings, feature flags

---

## 3. ACID Properties

### 3.1 Atomicity (Tính nguyên tử)

#### Định nghĩa:
**Atomicity** đảm bảo rằng một transaction được thực hiện hoàn toàn hoặc không thực hiện gì cả.

#### Cơ chế Implementation:
```sql
-- PostgreSQL Example: Transfer money between accounts
BEGIN;
    UPDATE accounts SET balance = balance - 1000000 WHERE account_id = 'A001';
    UPDATE accounts SET balance = balance + 1000000 WHERE account_id = 'A002';
    
    -- If any statement fails, entire transaction is rolled back
COMMIT;  -- Only commits if all statements succeed
```

#### Logging và Recovery:
- **Write-Ahead Logging (WAL)**: Ghi log trước khi thay đổi dữ liệu
- **Undo Logs**: Khôi phục trạng thái trước transaction
- **Checkpoint Mechanism**: Đồng bộ memory với disk

### 3.2 Consistency (Tính nhất quán)

#### Database Constraints:
```sql
-- Integrity constraints ensure consistency
CREATE TABLE telecom_subscribers (
    subscriber_id VARCHAR(20) PRIMARY KEY,
    phone_number VARCHAR(15) UNIQUE NOT NULL,
    balance DECIMAL(12,2) CHECK (balance >= 0),
    status VARCHAR(10) CHECK (status IN ('ACTIVE', 'SUSPENDED', 'TERMINATED')),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Referential integrity
CREATE TABLE call_records (
    call_id BIGSERIAL PRIMARY KEY,
    caller_id VARCHAR(20) REFERENCES telecom_subscribers(subscriber_id),
    callee_number VARCHAR(15) NOT NULL,
    duration_seconds INTEGER CHECK (duration_seconds >= 0),
    call_cost DECIMAL(8,2) CHECK (call_cost >= 0)
);
```

#### Application-level Consistency:
```python
# Business logic ensures consistency
def charge_subscriber(subscriber_id, amount):
    with database.transaction():
        subscriber = get_subscriber(subscriber_id)
        
        # Business rule: Can't charge inactive subscribers
        if subscriber.status != 'ACTIVE':
            raise ValueError("Cannot charge inactive subscriber")
        
        # Business rule: Can't overdraft beyond credit limit
        if subscriber.balance - amount < subscriber.credit_limit:
            raise ValueError("Insufficient balance")
        
        update_balance(subscriber_id, -amount)
        create_billing_record(subscriber_id, amount)
```

### 3.3 Isolation (Tính cô lập)

#### Isolation Levels:

##### Read Uncommitted:
```sql
-- PostgreSQL: Allows dirty reads
SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
BEGIN;
    SELECT balance FROM accounts WHERE account_id = 'A001';
    -- May see uncommitted changes from other transactions
COMMIT;
```

##### Read Committed (Default in most databases):
```sql
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;
BEGIN;
    SELECT balance FROM accounts WHERE account_id = 'A001';  -- Time T1
    -- Other transaction commits changes
    SELECT balance FROM accounts WHERE account_id = 'A001';  -- Time T2, different value
COMMIT;
```

##### Repeatable Read:
```sql
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
BEGIN;
    SELECT balance FROM accounts WHERE account_id = 'A001';  -- Returns X
    -- Other transactions modify the account
    SELECT balance FROM accounts WHERE account_id = 'A001';  -- Still returns X
COMMIT;
```

##### Serializable:
```sql
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;
-- Transactions execute as if they were run serially
-- Highest isolation, potential for serialization failures
```

#### Concurrency Control Mechanisms:

##### Two-Phase Locking (2PL):
```
Growing Phase: Acquire locks, cannot release
Shrinking Phase: Release locks, cannot acquire

Timeline:
T1: ──lock(A)──read(A)──lock(B)──write(B)──unlock(A)──unlock(B)──
T2: ────────────wait──────────────────────lock(A)──read(A)──unlock(A)──
```

##### Multiversion Concurrency Control (MVCC):
```
PostgreSQL MVCC Example:
- Each row has multiple versions with timestamps
- Readers see consistent snapshot without blocking writers
- Writers create new versions without overwriting old ones

Version Chain:
Row ID | Version | xmin | xmax | Data
-------|---------|------|------|----------
1001   | v1      | 100  | 150  | {old data}
1001   | v2      | 150  | ∞    | {new data}
```

### 3.4 Durability (Tính bền vững)

#### Write-Ahead Logging (WAL):
```
PostgreSQL WAL Process:
1. Transaction begins
2. Changes written to WAL buffer
3. WAL buffer flushed to disk (fsync)
4. Changes applied to data files
5. Checkpoint process periodically syncs all changes

WAL Record Format:
[LSN][Transaction ID][Operation][Table][Old Values][New Values][Checksum]
```

#### Recovery Mechanisms:
```sql
-- PostgreSQL Point-in-Time Recovery
-- 1. Restore from base backup
pg_basebackup -D /var/lib/postgresql/backup -Ft -z -P

-- 2. Configure recovery
echo "restore_command = 'cp /archive/%f %p'" > recovery.conf
echo "recovery_target_time = '2024-01-15 10:30:00'" >> recovery.conf

-- 3. Start recovery process
pg_ctl start -D /var/lib/postgresql/backup
```

---

## 4. CAP Theorem

### 4.1 Định lý CAP (Brewer's Theorem)

#### Phát biểu:
Trong một hệ thống phân tán, chỉ có thể đảm bảo tối đa 2 trong 3 tính chất:
- **Consistency (C)**: Tính nhất quán
- **Availability (A)**: Tính khả dụng  
- **Partition Tolerance (P)**: Khả năng chịu lỗi phân vùng

### 4.2 Trade-offs Analysis

#### CP Systems (Consistency + Partition Tolerance):
```
Examples: MongoDB (with strong consistency), Redis Cluster

Behavior during network partition:
┌─────────────┐    ╳ Network    ┌─────────────┐
│   Node A    │    ╳ Partition  │   Node B    │
│ (Primary)   │    ╳            │ (Secondary) │
└─────────────┘    ╳            └─────────────┘

- Node B becomes unavailable for writes
- Ensures data consistency
- Sacrifices availability during partition
```

#### AP Systems (Availability + Partition Tolerance):
```
Examples: Cassandra, DynamoDB

Behavior during network partition:
┌─────────────┐    ╳ Network    ┌─────────────┐
│   Node A    │    ╳ Partition  │   Node B    │
│ (Accept     │    ╳            │ (Accept     │
│  Writes)    │    ╳            │  Writes)    │
└─────────────┘    ╳            └─────────────┘

- Both nodes continue accepting writes
- May have temporary inconsistency
- Resolves conflicts when partition heals
```

### 4.3 Practical Implications at Viettel IDC

#### Telecommunications Billing System:
```python
# CP System for billing (strong consistency required)
class BillingTransaction:
    def process_charge(self, subscriber_id, amount):
        # Must ensure exactly-once charging
        with distributed_lock(subscriber_id):
            current_balance = get_balance(subscriber_id)
            if current_balance >= amount:
                new_balance = current_balance - amount
                update_balance(subscriber_id, new_balance)
                create_billing_record(subscriber_id, amount)
                return True
            else:
                raise InsufficientFundsError()

# AP System for call detail records (availability preferred)
class CallDetailRecord:
    def log_call(self, caller, callee, duration):
        # Best effort logging, eventual consistency acceptable
        try:
            primary_node.insert(call_record)
        except NetworkError:
            # Fallback to secondary node
            secondary_node.insert(call_record)
            # Will be reconciled later
```

---

## 5. Consistency Models

### 5.1 Strong Consistency

#### Linearizability:
```
Timeline view of operations:

Client A: ──write(x=1)──────────────read(x)→1──
Client B: ────────────read(x)→1──────────────────
Client C: ──────────────────read(x)→1────────────

All reads return the most recent write value
Operations appear to take effect atomically
```

#### Sequential Consistency:
```
Actual execution order may differ from real-time order
But all clients see operations in same order

Allowed execution:
T1: write(x=1)
T2: write(x=2)  
T3: read(x)→2
T4: read(x)→2

All clients see: x=1, then x=2
```

### 5.2 Eventual Consistency

#### Amazon's Dynamo Model:
```
Vector Clock Example:
Node A: [A:1, B:0, C:0] → write(key=value1)
Node B: [A:1, B:1, C:0] → write(key=value2)  
Node C: [A:1, B:1, C:1] → read(key) → conflict!

Conflict Resolution:
- Last Writer Wins (LWW)
- Application-specific resolution
- Multi-value return for client resolution
```

#### MongoDB Read Concerns:
```javascript
// Eventual consistency (default)
db.collection.find().readConcern("available");

// Strong consistency
db.collection.find().readConcern("linearizable");

// Causal consistency
session = db.getMongo().startSession();
session.withTransaction(() => {
    db.collection.find().readConcern("majority");
});
```

### 5.3 Causal Consistency

#### Happened-Before Relationship:
```
Events in causal order:

Alice posts: "Joining Viettel IDC!"  (Event A)
  ↓ (causally related)
Bob likes Alice's post             (Event B)
  ↓ (causally related)  
Charlie comments: "Congratulations!" (Event C)

All nodes must see events in order: A → B → C
But concurrent events can be seen in any order
```

---

## 6. Database Architecture

### 6.1 Centralized Architecture

#### Single-Node Database:
```
Application Layer
      ↓
┌─────────────────┐
│   Database      │
│   ┌─────────────┤
│   │ Query Proc. │
│   ├─────────────┤
│   │ Storage Mgr │
│   ├─────────────┤
│   │ Buffer Pool │
│   ├─────────────┤
│   │ Disk Storage│
│   └─────────────┤
└─────────────────┘
```

#### Components:
- **Query Processor**: SQL parsing, optimization, execution
- **Storage Manager**: Page management, file organization
- **Buffer Pool**: Memory management for data pages
- **Transaction Manager**: Concurrency control, recovery

### 6.2 Distributed Architecture

#### Shared-Nothing Architecture:
```
                Load Balancer
                      ↓
    ┌─────────┬─────────────┬─────────┐
    ↓         ↓             ↓         ↓
┌───────┐ ┌───────┐     ┌───────┐ ┌───────┐
│Node 1 │ │Node 2 │ ... │Node N │ │Coord. │
│CPU    │ │CPU    │     │CPU    │ │Node   │
│Memory │ │Memory │     │Memory │ │       │
│Disk   │ │Disk   │     │Disk   │ │       │
└───────┘ └───────┘     └───────┘ └───────┘
```

#### Horizontal Partitioning (Sharding):
```sql
-- Range-based sharding for telecom data
-- Shard 1: subscriber_id 0000000-3333333
-- Shard 2: subscriber_id 3333334-6666666  
-- Shard 3: subscriber_id 6666667-9999999

CREATE TABLE subscribers_shard1 (
    subscriber_id VARCHAR(20) CHECK (subscriber_id::integer BETWEEN 0 AND 3333333),
    -- other columns
);

-- Hash-based sharding
SELECT * FROM subscribers 
WHERE hash(subscriber_id) % 3 = 0;  -- Route to shard 1
```

### 6.3 Replication Architectures

#### Master-Slave Replication:
```
┌─────────────┐      Async/Sync      ┌─────────────┐
│   Master    │ ────── Replication ──→ │   Slave 1   │
│  (Writes)   │                       │   (Reads)   │
└─────────────┘                       └─────────────┘
       │                                      
       └────── Replication ────────────────────────────→ ┌─────────────┐
                                               │   Slave 2   │
                                               │   (Reads)   │
                                               └─────────────┘
```

#### Master-Master Replication:
```
┌─────────────┐ ←──── Bi-directional ────→ ┌─────────────┐
│  Master 1   │       Replication          │  Master 2   │  
│(Read/Write) │                            │(Read/Write) │
└─────────────┘                            └─────────────┘

Conflict Resolution:
- Timestamp-based (Last Writer Wins)
- Application-specific resolution  
- Manual conflict resolution
```

---

## 7. Storage Engines

### 7.1 B+ Tree Storage

#### Structure và Operations:
```
B+ Tree for index on subscriber_id:

                    [50 | 100]
                   /     |     \
              [25|35]  [75|85]  [125|150]
             /   |   \ /   |   \ /    |    \
          [10] [30] [40][60][80][90][110][130][160]
```

#### Advantages:
- **Sorted access**: Range queries efficient
- **Logarithmic complexity**: O(log n) search/insert/delete
- **Sequential access**: Good for range scans
- **Concurrent access**: Support for locking protocols

#### PostgreSQL B-Tree Implementation:
```sql
-- Create B-tree index (default)
CREATE INDEX idx_subscriber_phone ON subscribers(phone_number);

-- Index usage in query plans
EXPLAIN (ANALYZE, BUFFERS) 
SELECT * FROM subscribers WHERE phone_number = '0987654321';

-- Result shows Index Scan using idx_subscriber_phone
```

### 7.2 LSM-Trees (Log-Structured Merge Trees)

#### Structure:
```
Memory Component (MemTable):
  sorted in-memory structure

Disk Components (SSTables):
  Level 0: [SST1] [SST2] [SST3] (may overlap)
  Level 1: [SST4──────] [SST5──────] (no overlap)
  Level 2: [SST6────────────────] [SST7────────────────]

Compaction Process:
  Level 0 → Level 1: Merge overlapping SSTables
  Level 1 → Level 2: Size-based compaction
```

#### Write Path:
```
1. Write to Write-Ahead Log (durability)
2. Insert into MemTable (sorted structure)
3. When MemTable full → Flush to SSTable
4. Background compaction merges SSTables
```

#### Read Path:
```
1. Check MemTable first
2. Check Bloom filters for each SSTable
3. Binary search within SSTables
4. Merge results from multiple levels
```

#### MongoDB WiredTiger Engine:
```javascript
// Configure WiredTiger for write-heavy workload
db.adminCommand({
   "setParameter": 1,
   "wiredTigerEngineRuntimeConfig": 
     "cache_size=2GB,eviction_target=80,eviction_trigger=95"
});

// Optimize for LSM-like behavior
db.collection.createIndex(
   { "timestamp": 1 },
   { "background": true }
);
```

### 7.3 Column-Oriented Storage

#### Row vs Column Storage:
```
Row-oriented (traditional RDBMS):
Record 1: [ID=1][Name=Alice][Age=25][City=Hanoi]
Record 2: [ID=2][Name=Bob][Age=30][City=HCMC]
Record 3: [ID=3][Name=Charlie][Age=35][City=Danang]

Column-oriented:
ID Column:   [1][2][3]
Name Column: [Alice][Bob][Charlie]  
Age Column:  [25][30][35]
City Column: [Hanoi][HCMC][Danang]
```

#### Advantages for Analytics:
```sql
-- Analytical query on large telecom dataset
SELECT 
    city,
    AVG(call_duration),
    COUNT(*) as call_count
FROM call_records 
WHERE call_date >= '2024-01-01'
GROUP BY city;

-- Column storage benefits:
-- 1. Only read city and call_duration columns
-- 2. Better compression (similar values together)
-- 3. Vectorized processing
-- 4. Late materialization
```

---

## 8. Indexing Theory

### 8.1 Index Types

#### Primary Index (Clustered):
```sql
-- PostgreSQL: Primary key creates clustered index
CREATE TABLE subscribers (
    subscriber_id BIGSERIAL PRIMARY KEY,  -- Clustered index
    phone_number VARCHAR(15) UNIQUE,
    name VARCHAR(100),
    registration_date DATE
);

-- Data pages are physically ordered by subscriber_id
-- Page 1: [1001][1002][1003][1004]...
-- Page 2: [1101][1102][1103][1104]...
```

#### Secondary Index (Non-clustered):
```sql
-- Non-clustered index on phone_number
CREATE INDEX idx_phone ON subscribers(phone_number);

-- Index structure points to row locations:
-- Index: [0987654321] → Page 15, Slot 3
--        [0987654322] → Page 8, Slot 7  
--        [0987654323] → Page 22, Slot 1
```

#### Composite Index:
```sql
-- Multi-column index for complex queries
CREATE INDEX idx_subscriber_date_status 
ON call_records(subscriber_id, call_date, call_status);

-- Effective for queries:
SELECT * FROM call_records 
WHERE subscriber_id = 1001 AND call_date = '2024-01-15';

-- Index selectivity order matters:
-- subscriber_id (high selectivity) → call_date → call_status
```

### 8.2 Specialized Indexes

#### Partial Index:
```sql
-- Index only active subscribers
CREATE INDEX idx_active_subscribers 
ON subscribers(phone_number) 
WHERE status = 'ACTIVE';

-- Reduces index size and maintenance overhead
-- Only indexes relevant rows
```

#### Expression Index:
```sql
-- Index on computed expression
CREATE INDEX idx_subscriber_upper_name 
ON subscribers(UPPER(name));

-- Enables efficient case-insensitive searches
SELECT * FROM subscribers 
WHERE UPPER(name) = 'NGUYEN VAN A';
```

#### GIN Index (Generalized Inverted Index):
```sql
-- PostgreSQL: For array and full-text search
CREATE INDEX idx_subscriber_tags 
ON subscribers USING GIN(tags);

-- Efficient for containment queries
SELECT * FROM subscribers 
WHERE tags @> ARRAY['premium', 'business'];
```

### 8.3 Index Selection Strategy

#### Cardinality Analysis:
```sql
-- Analyze column cardinality for index decisions
SELECT 
    column_name,
    COUNT(DISTINCT column_name) as cardinality,
    COUNT(*) as total_rows,
    COUNT(DISTINCT column_name)::float / COUNT(*) as selectivity
FROM subscribers
GROUP BY column_name;

-- High selectivity (close to 1.0) = good index candidate
-- Low selectivity (close to 0.0) = poor index candidate
```

#### Query Pattern Analysis:
```sql
-- Analyze query patterns from pg_stat_statements
SELECT 
    query,
    calls,
    mean_time,
    rows,
    100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
FROM pg_stat_statements 
WHERE query LIKE '%subscribers%'
ORDER BY mean_time DESC;
```

---

## 9. Query Processing

### 9.1 Query Execution Pipeline

#### SQL Parsing:
```sql
-- Original query
SELECT s.name, COUNT(c.call_id) as call_count
FROM subscribers s
JOIN call_records c ON s.subscriber_id = c.caller_id  
WHERE s.status = 'ACTIVE' AND c.call_date >= '2024-01-01'
GROUP BY s.subscriber_id, s.name
HAVING COUNT(c.call_id) > 100;

-- Lexical analysis → Tokens
[SELECT] [s.name] [,] [COUNT] [(] [c.call_id] [)] [as] [call_count] ...

-- Syntactic analysis → Parse tree
Query
├── SELECT_LIST
│   ├── s.name
│   └── COUNT(c.call_id) AS call_count
├── FROM_CLAUSE
│   └── JOIN
│       ├── subscribers s
│       └── call_records c ON s.subscriber_id = c.caller_id
├── WHERE_CLAUSE
│   ├── s.status = 'ACTIVE'
│   └── c.call_date >= '2024-01-01'
└── GROUP_BY
    └── HAVING COUNT(c.call_id) > 100
```

### 9.2 Query Optimization

#### Cost-Based Optimization:
```sql
-- PostgreSQL query plan analysis
EXPLAIN (ANALYZE, BUFFERS, COSTS) 
SELECT s.name, COUNT(c.call_id) as call_count
FROM subscribers s
JOIN call_records c ON s.subscriber_id = c.caller_id  
WHERE s.status = 'ACTIVE' AND c.call_date >= '2024-01-01'
GROUP BY s.subscriber_id, s.name
HAVING COUNT(c.call_id) > 100;

-- Sample execution plan:
GroupAggregate  (cost=15000.00..16000.00 rows=100 width=64)
  Group Key: s.subscriber_id, s.name
  Filter: (count(c.call_id) > 100)
  ->  Nested Loop  (cost=0.00..14000.00 rows=5000 width=20)
        ->  Index Scan using idx_status on subscribers s
              Index Cond: (status = 'ACTIVE')
        ->  Index Scan using idx_caller_date on call_records c
              Index Cond: ((caller_id = s.subscriber_id) AND 
                          (call_date >= '2024-01-01'::date))
```

#### Join Algorithms:

##### Nested Loop Join:
```
for each row r1 in relation R1:
    for each row r2 in relation R2:
        if r1.join_key = r2.join_key:
            output (r1, r2)

Time Complexity: O(|R1| × |R2|)
Good for: Small inner relation, indexed join column
```

##### Hash Join:
```
Phase 1 (Build): Create hash table from smaller relation
hash_table = {}
for each row r1 in smaller_relation:
    hash_table[r1.join_key].append(r1)

Phase 2 (Probe): Probe with larger relation  
for each row r2 in larger_relation:
    matching_rows = hash_table.get(r2.join_key, [])
    for r1 in matching_rows:
        output (r1, r2)

Time Complexity: O(|R1| + |R2|)
Good for: Large relations, equi-joins
```

##### Sort-Merge Join:
```
1. Sort both relations on join key
2. Merge sorted relations

pointer1 = start of R1
pointer2 = start of R2
while pointer1 < end_R1 and pointer2 < end_R2:
    if R1[pointer1].key = R2[pointer2].key:
        output matching pairs
        advance both pointers
    elif R1[pointer1].key < R2[pointer2].key:
        advance pointer1
    else:
        advance pointer2

Time Complexity: O(|R1|log|R1| + |R2|log|R2|)
Good for: Large relations, already sorted data
```

### 9.3 Query Plan Caching

#### Plan Cache Management:
```sql
-- PostgreSQL: Prepared statements use plan cache
PREPARE subscriber_lookup AS
SELECT name, phone_number FROM subscribers 
WHERE subscriber_id = $1;

-- First execution: Plan created and cached
EXECUTE subscriber_lookup(1001);

-- Subsequent executions: Use cached plan
EXECUTE subscriber_lookup(1002);
EXECUTE subscriber_lookup(1003);

-- Generic vs custom plans based on parameter distribution
```

---

## 10. Transaction Management

### 10.1 Transaction Processing

#### Transaction States:
```
State Transition Diagram:

[ACTIVE] ──commit──→ [PARTIALLY COMMITTED] ──write complete──→ [COMMITTED]
    │                                                              ↑
    │                                                              │
    └──abort────→ [FAILED] ────undo complete────→ [ABORTED] ───────┘
```

#### Transaction Log Example:
```
LSN  | Transaction | Operation | Table    | Old Value | New Value | Status
-----|-------------|-----------|----------|-----------|-----------|--------
1001 | T1         | BEGIN     | -        | -         | -         | ACTIVE
1002 | T1         | UPDATE    | accounts | balance=5000 | balance=4000 | ACTIVE  
1003 | T2         | BEGIN     | -        | -         | -         | ACTIVE
1004 | T2         | INSERT    | transfers| -         | {id:101,amt:1000} | ACTIVE
1005 | T1         | UPDATE    | accounts | balance=3000 | balance=4000 | ACTIVE
1006 | T1         | COMMIT    | -        | -         | -         | COMMITTED
1007 | T2         | ABORT     | -        | -         | -         | ABORTED
```

### 10.2 Concurrency Control

#### Lock-Based Protocols:

##### Two-Phase Locking Implementation:
```python
class TwoPhaseLocker:
    def __init__(self):
        self.locks_held = set()
        self.growing_phase = True
    
    def acquire_lock(self, resource, lock_type):
        if not self.growing_phase:
            raise Exception("Cannot acquire lock in shrinking phase")
        
        lock = self.lock_manager.acquire(resource, lock_type)
        self.locks_held.add(lock)
        return lock
    
    def release_lock(self, lock):
        self.growing_phase = False  # Enter shrinking phase
        self.lock_manager.release(lock)
        self.locks_held.remove(lock)
    
    def commit(self):
        # Release all locks
        for lock in self.locks_held:
            self.lock_manager.release(lock)
        self.locks_held.clear()
```

#### Deadlock Detection:
```python
class DeadlockDetector:
    def build_wait_for_graph(self):
        """Build wait-for graph from current lock requests"""
        graph = {}
        
        for transaction_id, waiting_for in self.wait_for_relations:
            if transaction_id not in graph:
                graph[transaction_id] = []
            graph[transaction_id].append(waiting_for)
        
        return graph
    
    def detect_cycle(self, graph):
        """Detect cycles using DFS"""
        visited = set()
        rec_stack = set()
        
        for node in graph:
            if node not in visited:
                if self._has_cycle_util(graph, node, visited, rec_stack):
                    return True
        return False
    
    def resolve_deadlock(self, victim_transaction):
        """Abort victim transaction to break deadlock"""
        self.abort_transaction(victim_transaction)
        self.release_all_locks(victim_transaction)
```

### 10.3 Recovery Management

#### ARIES Recovery Algorithm:
```
ARIES (Algorithm for Recovery and Isolation Exploiting Semantics)

1. Analysis Phase:
   - Scan log forward from last checkpoint
   - Rebuild transaction table and dirty page table
   - Determine which transactions were active at crash

2. Redo Phase:  
   - Scan log forward from earliest LSN in dirty page table
   - Redo all operations (even for aborted transactions)
   - Restore database to state at time of crash

3. Undo Phase:
   - Scan log backward 
   - Undo operations of transactions that were active at crash
   - Write compensation log records (CLRs)
```

#### Checkpoint Implementation:
```sql
-- PostgreSQL checkpoint process
CHECKPOINT;

-- What happens during checkpoint:
-- 1. Flush all dirty buffers to disk
-- 2. Write checkpoint record to WAL
-- 3. Update control file with checkpoint location

-- Checkpoint frequency tuning
ALTER SYSTEM SET checkpoint_timeout = '5min';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET max_wal_size = '2GB';
```

---

## 📚 Tham khảo Lý thuyết

### Sách chuyên ngành:
1. **"Database System Concepts"** - Silberschatz, Galvin, Gagne
2. **"Fundamentals of Database Systems"** - Elmasri, Navathe  
3. **"Transaction Processing: Concepts and Techniques"** - Gray, Reuter
4. **"Designing Data-Intensive Applications"** - Martin Kleppmann

### Papers nghiên cứu:
1. **"A Relational Model of Data for Large Shared Data Banks"** - E.F. Codd (1970)
2. **"The Transaction Concept: Virtues and Limitations"** - Jim Gray (1981) 
3. **"ARIES: A Transaction Recovery Method"** - Mohan et al. (1992)
4. **"Bigtable: A Distributed Storage System"** - Google (2006)

### Standards:
- **SQL Standards**: ISO/IEC 9075 (SQL:2023)
- **ACID Properties**: ISO/IEC 10021-4
- **CAP Theorem**: Brewer's Conjecture and Lynch's Proof

---

## 🎯 Ứng dụng tại Viettel IDC

### Use Cases cụ thể:
1. **Billing System**: ACID transactions cho charging chính xác
2. **CDR Processing**: High-throughput insert với eventual consistency
3. **Subscriber Management**: Strong consistency cho account operations  
4. **Analytics Platform**: Column stores cho business intelligence
5. **Session Management**: Key-value stores cho real-time data

### Performance Requirements:
- **Billing**: 99.99% accuracy, sub-second response time
- **CDR**: 100,000+ inserts/second capacity
- **Analytics**: Complex queries on TB+ datasets
- **High Availability**: 99.99% uptime SLA
