# MongoDB and NoSQL Theory
# Lý thuyết MongoDB và NoSQL

## 📚 Mục lục
1. [NoSQL Database Theory](#1-nosql-database-theory)
2. [Document Database Model](#2-document-database-model)
3. [MongoDB Architecture](#3-mongodb-architecture)
4. [Storage Engine Theory](#4-storage-engine-theory)
5. [Indexing và Query Optimization](#5-indexing-và-query-optimization)
6. [Replication Theory](#6-replication-theory)
7. [Sharding và Horizontal Scaling](#7-sharding-và-horizontal-scaling)
8. [Consistency Models](#8-consistency-models)
9. [Aggregation Framework](#9-aggregation-framework)
10. [Performance và Monitoring](#10-performance-và-monitoring)

---

## 1. NoSQL Database Theory

### 1.1 NoSQL Classifications

#### CAP Theorem trong NoSQL:
```
NoSQL Database Types vs CAP:

┌─────────────────┬─────────────┬─────────────┬─────────────┐
│   Database      │ Consistency │ Availability│ Partition   │
│   Type          │     (C)     │     (A)     │ Tolerance(P)│
├─────────────────┼─────────────┼─────────────┼─────────────┤
│ Document        │     CP      │     AP      │    Always   │
│ (MongoDB)       │   (Strong)  │ (Eventual)  │             │
├─────────────────┼─────────────┼─────────────┼─────────────┤
│ Key-Value       │     AP      │     AP      │    Always   │
│ (Redis, DynamoDB│             │             │             │
├─────────────────┼─────────────┼─────────────┼─────────────┤
│ Column-Family   │     AP      │     AP      │    Always   │
│ (Cassandra)     │             │             │             │
├─────────────────┼─────────────┼─────────────┼─────────────┤
│ Graph           │     CP      │     CP      │   Variable  │
│ (Neo4j)         │             │             │             │
└─────────────────┴─────────────┴─────────────┴─────────────┘
```

#### NoSQL vs RDBMS Trade-offs:
```
RDBMS Strengths:
✓ ACID compliance
✓ Complex queries (joins)
✓ Data integrity constraints
✓ Mature ecosystem
✓ SQL standardization

NoSQL Strengths:
✓ Horizontal scalability
✓ Flexible schema
✓ High performance for simple queries
✓ Better suited for unstructured data
✓ Geographic distribution

Trade-off Analysis for Viettel IDC:
- User Profiles: NoSQL (flexible schema, scale)
- Financial Transactions: RDBMS (ACID compliance)
- Call Logs: NoSQL (high volume, simple queries)
- Billing Reports: RDBMS (complex aggregations)
```

### 1.2 Document Database Advantages

#### Schema Flexibility:
```javascript
// Traditional RDBMS: Rigid schema
CREATE TABLE subscribers (
    id BIGINT PRIMARY KEY,
    name VARCHAR(100),
    phone VARCHAR(15),
    address VARCHAR(200)
);

// NoSQL: Flexible document structure
// Subscriber with basic info
{
  "_id": ObjectId("507f1f77bcf86cd799439011"),
  "subscriber_id": "VT001234567",
  "name": "Nguyen Van A",
  "phone": "0987654321",
  "status": "active"
}

// Subscriber with extended profile (same collection)
{
  "_id": ObjectId("507f1f77bcf86cd799439012"),
  "subscriber_id": "VT001234568", 
  "name": "Tran Thi B",
  "phone": "0987654322",
  "status": "active",
  "preferences": {
    "language": "vi",
    "notifications": ["sms", "email"],
    "data_plan": "unlimited"
  },
  "devices": [
    {
      "imei": "123456789012345",
      "model": "iPhone 13",
      "registration_date": ISODate("2024-01-15")
    }
  ],
  "billing_history": [
    {
      "month": "2024-01",
      "amount": 200000,
      "paid": true,
      "payment_date": ISODate("2024-01-05")
    }
  ]
}
```

### 1.3 Use Cases tại Viettel IDC

#### IoT Device Data Collection:
```javascript
// Network equipment monitoring data
{
  "_id": ObjectId("507f1f77bcf86cd799439013"),
  "device_id": "BTS_HN_001",
  "device_type": "base_station",
  "location": {
    "type": "Point",
    "coordinates": [105.8342, 21.0278]  // [longitude, latitude]
  },
  "timestamp": ISODate("2024-01-15T10:30:00Z"),
  "metrics": {
    "signal_strength": -65,
    "active_connections": 1234,
    "data_throughput_mbps": 450.5,
    "error_rate": 0.001,
    "temperature": 35.2,
    "power_consumption": 2.4
  },
  "alerts": [
    {
      "type": "high_temperature", 
      "severity": "warning",
      "threshold": 35.0,
      "current_value": 35.2
    }
  ],
  "maintenance": {
    "last_service": ISODate("2023-12-01"),
    "next_service": ISODate("2024-03-01"),
    "technician": "Nguyen Van C"
  }
}
```

#### Customer 360 View:
```javascript
// Comprehensive customer profile
{
  "_id": ObjectId("507f1f77bcf86cd799439014"),
  "customer_id": "CUST_VT_001234",
  "personal_info": {
    "name": "Le Thi D",
    "id_number": "123456789",
    "email": "lethid@email.com",
    "address": {
      "street": "123 Nguyen Trai",
      "ward": "Phuong 1", 
      "district": "Quan 5",
      "city": "Ho Chi Minh",
      "postal_code": "70000"
    }
  },
  "subscriptions": [
    {
      "subscriber_id": "VT001234569",
      "phone": "0987654323",
      "plan": "postpaid_unlimited",
      "activation_date": ISODate("2023-01-15"),
      "status": "active"
    }
  ],
  "interaction_history": [
    {
      "date": ISODate("2024-01-10"),
      "channel": "call_center",
      "type": "complaint",
      "issue": "poor_signal_quality",
      "resolution": "tower_maintenance_scheduled",
      "agent_id": "AGENT_001"
    },
    {
      "date": ISODate("2024-01-05"),
      "channel": "web_portal", 
      "type": "plan_change",
      "details": "upgraded_to_unlimited_data"
    }
  ],
  "preferences": {
    "communication_language": "vi",
    "marketing_consent": true,
    "bill_delivery": "email",
    "data_usage_alerts": true
  }
}
```

---

## 2. Document Database Model

### 2.1 BSON (Binary JSON) Format

#### BSON Data Types:
```javascript
// MongoDB BSON types with examples
{
  // Basic types
  "string_field": "Viettel IDC",
  "integer_32": NumberInt(12345),
  "integer_64": NumberLong("9223372036854775807"),
  "double": 123.456,
  "decimal": NumberDecimal("99.99"),
  "boolean": true,
  "null_field": null,
  
  // Date and time
  "date": ISODate("2024-01-15T10:30:00Z"),
  "timestamp": Timestamp(1642244400, 1),
  
  // Complex types
  "object_id": ObjectId("507f1f77bcf86cd799439011"),
  "binary_data": BinData(0, "base64encodeddata"),
  "regex": /^VT\d{9}$/,
  
  // Arrays and embedded documents
  "array": [1, 2, 3, "mixed", true],
  "embedded_document": {
    "nested_field": "value",
    "another_field": 42
  },
  
  // Special types
  "javascript_code": Code("function() { return this.value * 2; }"),
  "min_key": MinKey(),
  "max_key": MaxKey()
}
```

#### BSON Size Limitations:
```
Document Size Limit: 16MB per document

Size Calculation Example:
{
  "_id": ObjectId(...),           // 12 bytes
  "subscriber_id": "VT001234567", // field name (13) + string (10) = 23 bytes
  "name": "Nguyen Van A",         // field name (4) + string (12) = 16 bytes
  "phone": "0987654321",          // field name (5) + string (10) = 15 bytes
  "created": ISODate(...),        // field name (7) + date (8) = 15 bytes
  "metadata": { ... }             // nested document size
}

Total: Header + Field sizes + Padding
```

### 2.2 Schema Design Patterns

#### Embedding vs Referencing:
```javascript
// EMBEDDING: One-to-Few relationships
// Subscriber with embedded call history (last 10 calls)
{
  "_id": ObjectId("..."),
  "subscriber_id": "VT001234567",
  "name": "Nguyen Van A",
  "recent_calls": [  // Embedded array (bounded size)
    {
      "to_number": "0987654322",
      "duration": 120,
      "cost": 5000,
      "date": ISODate("2024-01-15T10:30:00Z")
    },
    {
      "to_number": "0987654323", 
      "duration": 300,
      "cost": 12000,
      "date": ISODate("2024-01-15T09:15:00Z")
    }
    // ... up to 10 recent calls
  ]
}

// REFERENCING: One-to-Many relationships
// Subscriber document (main)
{
  "_id": ObjectId("507f1f77bcf86cd799439011"),
  "subscriber_id": "VT001234567",
  "name": "Nguyen Van A",
  "plan_id": "PLAN_UNLIMITED"
}

// Call records collection (referenced)
{
  "_id": ObjectId("507f1f77bcf86cd799439020"),
  "subscriber_id": "VT001234567",  // Reference to subscriber
  "to_number": "0987654322",
  "from_number": "0987654321",
  "duration": 120,
  "cost": 5000,
  "date": ISODate("2024-01-15T10:30:00Z"),
  "tower_id": "BTS_HN_001"
}
```

#### Polymorphic Pattern:
```javascript
// Different event types in same collection
// Call event
{
  "_id": ObjectId("..."),
  "event_type": "call",
  "subscriber_id": "VT001234567",
  "timestamp": ISODate("2024-01-15T10:30:00Z"),
  "duration": 120,
  "to_number": "0987654322",
  "cost": 5000
}

// SMS event  
{
  "_id": ObjectId("..."),
  "event_type": "sms",
  "subscriber_id": "VT001234567", 
  "timestamp": ISODate("2024-01-15T10:32:00Z"),
  "to_number": "0987654322",
  "message_length": 160,
  "cost": 1000
}

// Data usage event
{
  "_id": ObjectId("..."),
  "event_type": "data_usage",
  "subscriber_id": "VT001234567",
  "timestamp": ISODate("2024-01-15T10:35:00Z"),
  "bytes_consumed": 10485760,  // 10MB
  "session_duration": 1800,    // 30 minutes
  "cost": 15000
}
```

### 2.3 Data Modeling Best Practices

#### Rule of Thumb for Embedding:
```
Embed when:
✓ One-to-few relationships (< 100 sub-documents)
✓ Data doesn't change frequently
✓ Need to query parent and child together
✓ Child data doesn't exceed 16MB limit

Reference when:
✓ One-to-many relationships (> 100 references)
✓ Many-to-many relationships
✓ Child data changes frequently
✓ Child data queried independently
✓ Document size approaches 16MB
```

#### Viettel IDC Schema Examples:
```javascript
// Network Tower Configuration (Embedding)
{
  "_id": ObjectId("..."),
  "tower_id": "BTS_HN_001",
  "location": {
    "coordinates": [105.8342, 21.0278],
    "address": "123 Duong Lang, Hanoi"
  },
  "equipment": [  // Embedded (limited equipment per tower)
    {
      "equipment_id": "ANT_001",
      "type": "antenna",
      "model": "Huawei AAU5613",
      "frequency": "2.6GHz",
      "power": "40W",
      "installation_date": ISODate("2023-01-15")
    }
  ],
  "coverage_area": {
    "radius_meters": 2000,
    "sector_angles": [0, 120, 240]
  }
}

// Call Detail Records (Referencing)
{
  "_id": ObjectId("..."),
  "call_id": "CALL_20240115_001",
  "caller_id": "VT001234567",      // Reference to subscriber
  "callee_number": "0987654322",
  "start_time": ISODate("2024-01-15T10:30:00Z"),
  "end_time": ISODate("2024-01-15T10:32:00Z"),
  "duration_seconds": 120,
  "tower_id": "BTS_HN_001",        // Reference to tower
  "cost": 5000,
  "call_quality": {
    "signal_strength": -70,
    "dropped": false,
    "codec": "AMR-WB"
  }
}
```

---

## 3. MongoDB Architecture

### 3.1 MongoDB Process Architecture

#### Component Overview:
```
MongoDB Instance Architecture:

┌─────────────────────────────────────────────────────────┐
│                    MongoDB (mongod)                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐ │
│  │  Query      │  │  Storage    │  │   Replication   │ │
│  │  Engine     │  │  Engine     │  │   Module        │ │
│  └─────────────┘  └─────────────┘  └─────────────────┘ │
│         │               │                 │           │
│         ▼               ▼                 ▼           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐ │
│  │  Connection │  │  WiredTiger │  │  OpLog          │ │
│  │  Manager    │  │  Storage    │  │  (Replication   │ │
│  │             │  │  Engine     │  │   Log)          │ │
│  └─────────────┘  └─────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
                ┌─────────────────┐
                │   File System   │
                │   (Data Files)  │
                └─────────────────┘
```

#### Connection Handling:
```javascript
// MongoDB connection lifecycle
1. Client connects to mongod
2. Authentication (if enabled)
3. Connection pooling
4. Query processing
5. Result return
6. Connection reuse/close

// Connection pool configuration
// In application driver (Node.js example)
const mongoose = require('mongoose');

mongoose.connect('mongodb://localhost:27017/viettel_idc', {
  maxPoolSize: 10,          // Maximum connections in pool
  minPoolSize: 5,           // Minimum connections in pool
  maxIdleTimeMS: 30000,     // Close connections after 30s idle
  serverSelectionTimeoutMS: 5000,  // How long to try selecting server
  socketTimeoutMS: 45000,   // How long socket stays open
  bufferMaxEntries: 0       // Disable mongoose buffering
});
```

### 3.2 Memory Management

#### WiredTiger Cache:
```javascript
// WiredTiger cache configuration
// Default: 50% of (RAM - 1GB) or 256MB, whichever is larger

// For Viettel IDC production server (32GB RAM):
// Cache size = 50% of (32GB - 1GB) = 15.5GB

// Configure cache size
db.adminCommand({
  "setParameter": 1,
  "wiredTigerEngineRuntimeConfig": "cache_size=16GB"
});

// Monitor cache usage
db.serverStatus().wiredTiger.cache;
/*
Expected output:
{
  "bytes currently in the cache": 15032385536,
  "tracked dirty bytes in the cache": 104857600,
  "maximum bytes configured": 17179869184,
  "bytes read into cache": 1073741824000,
  "bytes written from cache": 536870912000,
  "eviction currently operating in aggressive mode": false
}
*/
```

### 3.3 Lock Management

#### Lock Hierarchy:
```
MongoDB Locking (WiredTiger Engine):

Global
  │
  ├── Database
  │     │
  │     ├── Collection
  │     │     │
  │     │     └── Document (Multi-version)
  │     │
  │     └── Index
  │
  └── GridFS

Lock Types:
- Intent Shared (IS)
- Intent Exclusive (IX) 
- Shared (S)
- Exclusive (X)
```

#### Lock Analysis:
```javascript
// Check current operations and locks
db.currentOp({
  "active": true,
  "secs_running": { "$gt": 5 },
  "ns": /^viettel_idc\./
});

// Sample output for long-running operation
{
  "inprog": [
    {
      "opid": 12345,
      "active": true,
      "secs_running": 15,
      "op": "update",
      "ns": "viettel_idc.subscribers",
      "query": { "status": "inactive" },
      "planSummary": "COLLSCAN",
      "numYields": 1000,
      "locks": {
        "Global": "w",
        "Database": "w", 
        "Collection": "w"
      },
      "waitingForLock": false,
      "lockStats": {
        "Global": {
          "acquireCount": { "r": 1001, "w": 1 },
          "acquireWaitCount": { "w": 1 },
          "timeAcquiringMicros": { "w": 50000 }
        }
      }
    }
  ]
}

// Kill long-running operation if needed
db.killOp(12345);
```

---

## 4. Storage Engine Theory

### 4.1 WiredTiger Storage Engine

#### B+ Tree Structure:
```
WiredTiger uses B+ trees for both collections and indexes:

Collection B+ Tree:
- Leaf pages contain documents
- Internal pages contain routing information
- Pages are typically 32KB
- Support compression (snappy, zlib, zstd)

Index B+ Tree:
- Leaf pages contain index keys + record IDs
- Internal pages contain routing keys
- Support prefix compression
- Multiple indexes per collection
```

#### Page Structure:
```c
// Simplified WiredTiger page structure
typedef struct {
    uint32_t page_size;           // Usually 32KB
    uint8_t  page_type;           // Leaf, internal, overflow
    uint64_t write_generation;    // For MVCC
    uint32_t key_count;          // Number of keys in page
    uint32_t compressed_size;    // If compression enabled
    
    // Variable length data:
    // - Page header
    // - Cell offsets array  
    // - Key/value pairs
    // - Deleted key list
} WiredTigerPage;
```

### 4.2 Compression

#### Storage Efficiency:
```javascript
// Enable compression for collection
db.createCollection("call_records", {
  storageEngine: {
    wiredTiger: {
      configString: "block_compressor=zstd"
    }
  }
});

// Compression options:
// - none: No compression
// - snappy: Fast compression/decompression (default)
// - zlib: Better compression ratio
// - zstd: Best compression ratio (MongoDB 4.2+)

// Check compression statistics
db.call_records.stats().wiredTiger.compression;
/*
{
  "compressed size": 524288000,      // 500MB compressed
  "uncompressed size": 1073741824,   // 1GB uncompressed  
  "compression ratio": 0.488         // ~51% space savings
}
*/
```

### 4.3 Journaling

#### Write Durability:
```
WiredTiger Journaling Process:

1. Write operations → In-memory cache
2. Background thread → Journal files (every 100ms)
3. Checkpoint process → Data files (every 60s)
4. Journal cleanup → After successful checkpoint

Journal Structure:
- Write-ahead log for durability
- Group commits for performance
- Compressed journal entries
- Recovery from journal on restart
```

#### Journaling Configuration:
```javascript
// Configure journal settings
db.adminCommand({
  "setParameter": 1,
  "wiredTigerEngineRuntimeConfig": 
    "journal=(enabled=true,compressor=snappy)"
});

// Monitor journal statistics  
db.serverStatus().wiredTiger.log;
/*
{
  "log bytes of payload data": 10737418240,
  "log bytes written": 8589934592,
  "log files in use": 3,
  "log flush operations": 123456,
  "log sync operations": 12345,
  "log write operations": 1234567
}
*/
```

---

## 5. Indexing và Query Optimization

### 5.1 Index Types

#### Single Field Index:
```javascript
// Create single field index
db.subscribers.createIndex({ "subscriber_id": 1 });

// Compound index (multiple fields)
db.call_records.createIndex({ 
  "caller_id": 1, 
  "call_date": -1,
  "duration": 1 
});

// Explain compound index usage
db.call_records.find({
  "caller_id": "VT001234567",
  "call_date": { $gte: ISODate("2024-01-01") }
}).explain("executionStats");
```

#### Text Index:
```javascript
// Create text index for search
db.subscribers.createIndex({
  "name": "text",
  "phone": "text",
  "email": "text"
}, {
  weights: {
    "name": 10,     // Higher weight for name
    "phone": 5,
    "email": 1
  },
  default_language: "vietnamese"
});

// Text search query
db.subscribers.find({
  $text: { 
    $search: "Nguyen Van",
    $language: "vietnamese"
  }
}, {
  score: { $meta: "textScore" }
}).sort({ score: { $meta: "textScore" } });
```

#### Geospatial Index:
```javascript
// 2dsphere index for geographic data
db.towers.createIndex({ "location": "2dsphere" });

// Find towers within 5km of point
db.towers.find({
  location: {
    $near: {
      $geometry: {
        type: "Point",
        coordinates: [105.8342, 21.0278]  // Hanoi center
      },
      $maxDistance: 5000  // 5km in meters
    }
  }
});

// Geospatial aggregation for coverage analysis
db.towers.aggregate([
  {
    $geoNear: {
      near: { type: "Point", coordinates: [105.8342, 21.0278] },
      distanceField: "distance",
      maxDistance: 10000,
      spherical: true
    }
  },
  {
    $group: {
      _id: null,
      total_towers: { $sum: 1 },
      avg_distance: { $avg: "$distance" },
      coverage_area: { 
        $sum: { $multiply: [3.14159, { $pow: ["$coverage_radius", 2] }] }
      }
    }
  }
]);
```

### 5.2 Query Planning

#### Index Selection Process:
```javascript
// MongoDB query planner process:
// 1. Parse query → Query tree
// 2. Generate candidate plans
// 3. Execute plans with small sample
// 4. Choose best plan (lowest work units)
// 5. Cache plan for similar queries

// Force specific index usage
db.call_records.find({
  "caller_id": "VT001234567",
  "call_date": { $gte: ISODate("2024-01-01") }
}).hint({ "caller_id": 1, "call_date": -1 });

// View cached query plans
db.runCommand({ planCacheClear: "call_records" });
db.call_records.getPlanCache().listQueryShapes();
```

#### Query Performance Analysis:
```javascript
// Detailed execution statistics
db.call_records.find({
  "caller_id": "VT001234567",
  "duration": { $gte: 300 }
}).explain("executionStats");

/*
Sample output analysis:
{
  "executionStats": {
    "totalDocsExamined": 1000,     // Documents scanned
    "totalDocsReturned": 50,       // Documents returned
    "executionTimeMillis": 25,     // Query execution time
    "stage": "IXSCAN",             // Index scan used
    "indexName": "caller_id_1",    // Index used
    "keysExamined": 1000,          // Index keys examined
    "docsExamined": 50,            // Documents examined after index
    "isMultiKey": false,           // Index on array field?
    "direction": "forward"         // Scan direction
  }
}

Performance indicators:
✓ keysExamined ≈ docsReturned (good selectivity)
✗ totalDocsExamined >> docsReturned (poor index)
✓ stage = "IXSCAN" (index used)
✗ stage = "COLLSCAN" (full collection scan)
*/
```

### 5.3 Index Optimization Strategies

#### ESR Rule (Equality, Sort, Range):
```javascript
// Optimal compound index order: Equality → Sort → Range
// Query pattern analysis:
db.call_records.find({
  "caller_id": "VT001234567",     // Equality
  "status": "completed",          // Equality  
  "duration": { $gte: 300 }       // Range
}).sort({ "call_date": -1 });     // Sort

// Optimal index (ESR order):
db.call_records.createIndex({
  "caller_id": 1,    // Equality (most selective)
  "status": 1,       // Equality
  "call_date": -1,   // Sort
  "duration": 1      // Range (least selective)
});
```

#### Covered Queries:
```javascript
// Create covering index
db.subscribers.createIndex({
  "subscriber_id": 1,
  "status": 1,
  "name": 1,        // Include projection fields
  "phone": 1
});

// Query that uses only index data (no document access)
db.subscribers.find(
  { "subscriber_id": "VT001234567", "status": "active" },
  { "name": 1, "phone": 1, "_id": 0 }  // Projection matches index
).explain("executionStats");

// Look for "stage": "PROJECTION_COVERED" in explain output
```

---

## 6. Replication Theory

### 6.1 Replica Set Architecture

#### Replica Set Components:
```
MongoDB Replica Set:

┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Primary   │────▶│  Secondary  │    │  Secondary  │
│             │     │             │    │  (Hidden)   │
│  Read/Write │     │ Read Only*  │    │Read/Backup  │
└─────────────┘     └─────────────┘     └─────────────┘
       │                    │                   │
       └────────────────────┼───────────────────┘
                            │
                    ┌─────────────┐
                    │   Arbiter   │
                    │ (Vote Only) │
                    └─────────────┘

* Read preference can be configured
```

#### Election Process:
```javascript
// Replica set configuration
rs.initiate({
  _id: "viettelRS",
  members: [
    { 
      _id: 0, 
      host: "mongo1.viettel.com:27017",
      priority: 2  // Higher priority = more likely to be primary
    },
    { 
      _id: 1, 
      host: "mongo2.viettel.com:27017",
      priority: 1
    },
    { 
      _id: 2, 
      host: "mongo3.viettel.com:27017",
      priority: 1
    }
  ]
});

// Election triggers:
// 1. Primary becomes unavailable
// 2. Primary steps down
// 3. Higher priority member available
// 4. Manual failover

// Monitor replica set status
rs.status();
```

### 6.2 Oplog (Operations Log)

#### Oplog Structure:
```javascript
// Oplog entry structure
{
  "ts": Timestamp(1642245000, 1),  // Timestamp
  "t": NumberLong(1),              // Term (election cycle)
  "h": NumberLong("12345678"),     // Hash
  "v": 2,                          // Oplog version
  "op": "i",                       // Operation type (i=insert, u=update, d=delete)
  "ns": "viettel_idc.subscribers", // Namespace
  "o": {                           // Operation document
    "_id": ObjectId("..."),
    "subscriber_id": "VT001234567",
    "name": "Nguyen Van A",
    "status": "active"
  }
}

// Query oplog
use local;
db.oplog.rs.find().sort({ $natural: -1 }).limit(10);

// Oplog size and retention
db.oplog.rs.stats();
/*
{
  "maxSize": 1073741824,    // 1GB oplog size
  "usedSize": 524288000,    // 500MB used
  "firstTs": Timestamp(...), // Oldest entry
  "lastTs": Timestamp(...)   // Newest entry
}
*/
```

### 6.3 Read Preferences

#### Read Preference Modes:
```javascript
// Primary (default): All reads from primary
db.subscribers.find().readPref("primary");

// Secondary: Read from secondary only
db.subscribers.find().readPref("secondary");

// PrimaryPreferred: Primary if available, else secondary
db.subscribers.find().readPref("primaryPreferred");

// SecondaryPreferred: Secondary if available, else primary
db.subscribers.find().readPref("secondaryPreferred");

// Nearest: Lowest latency member
db.subscribers.find().readPref("nearest");

// Read preference with tags
db.subscribers.find().readPref("secondary", [
  { "datacenter": "hanoi" },
  { "datacenter": "hcmc" }
]);
```

#### Tag-based Routing:
```javascript
// Configure replica set with tags
rs.reconfig({
  _id: "viettelRS",
  members: [
    { 
      _id: 0, 
      host: "mongo-hn-1:27017",
      tags: { "datacenter": "hanoi", "zone": "primary" }
    },
    { 
      _id: 1, 
      host: "mongo-hcm-1:27017", 
      tags: { "datacenter": "hcmc", "zone": "secondary" }
    },
    { 
      _id: 2, 
      host: "mongo-dn-1:27017",
      tags: { "datacenter": "danang", "zone": "backup" }
    }
  ]
});

// Application-level read routing
// Route analytics queries to backup nodes
db.call_records.aggregate([
  { $match: { call_date: { $gte: ISODate("2024-01-01") } } },
  { $group: { _id: "$caller_id", total_calls: { $sum: 1 } } }
]).readPref("secondary", [{ "zone": "backup" }]);
```

---

## 7. Sharding và Horizontal Scaling

### 7.1 Sharded Cluster Architecture

#### Cluster Components:
```
MongoDB Sharded Cluster:

Application
     │
     ▼
┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│   mongos    │   │   mongos    │   │   mongos    │
│  (Router)   │   │  (Router)   │   │  (Router)   │
└─────────────┘   └─────────────┘   └─────────────┘
     │                   │                   │
     └───────────────────┼───────────────────┘
                         │
    ┌────────────────────┼────────────────────┐
    │                    │                    │
    ▼                    ▼                    ▼
┌─────────┐         ┌─────────┐         ┌─────────┐
│ Shard 1 │         │ Shard 2 │         │ Shard 3 │
│(ReplicaSet)│      │(ReplicaSet)│      │(ReplicaSet)│
└─────────┘         └─────────┘         └─────────┘
    │                    │                    │
    ▼                    ▼                    ▼
┌─────────┐         ┌─────────┐         ┌─────────┐
│Config   │         │Config   │         │Config   │
│Server 1 │         │Server 2 │         │Server 3 │
└─────────┘         └─────────┘         └─────────┘
```

#### Shard Key Selection:
```javascript
// Good shard key characteristics:
// 1. High cardinality (many unique values)
// 2. Low frequency (values appear rarely)  
// 3. Non-monotonic (avoids hot spots)
// 4. Query-friendly (supports common queries)

// Example: Subscriber data sharding
// Poor choice: _id (monotonic, creates hot spots)
// Poor choice: status (low cardinality)
// Good choice: subscriber_id (high cardinality, random distribution)

// Enable sharding for database
sh.enableSharding("viettel_idc");

// Shard collection by subscriber_id
sh.shardCollection("viettel_idc.subscribers", { "subscriber_id": 1 });

// Compound shard key for time-series data  
sh.shardCollection("viettel_idc.call_records", { 
  "caller_id": 1, 
  "call_date": 1 
});
```

### 7.2 Data Distribution

#### Chunk Management:
```javascript
// Default chunk size: 64MB
// MongoDB automatically splits and migrates chunks

// View chunk distribution
sh.status();

// Check specific collection sharding info
db.subscribers.getShardDistribution();
/*
Shard viettel-shard-01 at viettel-shard-01/mongo1:27017,mongo2:27017,mongo3:27017
 data : 2.5GB docs : 5000000 chunks : 40
 estimated data per chunk : 64MB
 estimated docs per chunk : 125000

Shard viettel-shard-02 at viettel-shard-02/mongo4:27017,mongo5:27017,mongo6:27017  
 data : 2.3GB docs : 4600000 chunks : 36
 estimated data per chunk : 64MB
 estimated docs per chunk : 127777

Totals
 data : 4.8GB docs : 9600000 chunks : 76
*/

// Manual chunk operations (if needed)
sh.splitAt("viettel_idc.subscribers", { "subscriber_id": "VT005000000" });
sh.moveChunk("viettel_idc.subscribers", 
  { "subscriber_id": "VT003000000" }, 
  "viettel-shard-03"
);
```

### 7.3 Query Routing

#### Targeted vs Broadcast Queries:
```javascript
// TARGETED QUERY: Uses shard key in query
// Routes to specific shard(s)
db.subscribers.find({ "subscriber_id": "VT001234567" });

// BROADCAST QUERY: No shard key in query  
// Must query all shards
db.subscribers.find({ "name": "Nguyen Van A" });

// Query explain on sharded collection
db.subscribers.find({ "subscriber_id": "VT001234567" }).explain();
/*
{
  "queryPlanner": {
    "winningPlan": {
      "stage": "SINGLE_SHARD",  // Targeted query
      "shards": [
        {
          "shardName": "viettel-shard-01",
          "connectionString": "viettel-shard-01/mongo1:27017,mongo2:27017",
          "serverInfo": {...}
        }
      ]
    }
  }
}
*/
```

#### Aggregation on Sharded Collections:
```javascript
// Aggregation pipeline optimization for sharding
db.call_records.aggregate([
  // Stage 1: Match stage can be pushed to shards if uses shard key
  { $match: { 
    "caller_id": { $in: ["VT001234567", "VT001234568"] },
    "call_date": { $gte: ISODate("2024-01-01") }
  }},
  
  // Stage 2: Group stage - may require merge on mongos
  { $group: {
    _id: "$caller_id",
    total_calls: { $sum: 1 },
    total_duration: { $sum: "$duration" },
    avg_cost: { $avg: "$cost" }
  }},
  
  // Stage 3: Sort stage - performed on mongos after merge
  { $sort: { "total_duration": -1 } },
  
  // Stage 4: Limit stage - can be optimized
  { $limit: 100 }
]);

// Use allowDiskUse for large aggregations
db.call_records.aggregate([...], { allowDiskUse: true });
```

---

## 8. Consistency Models

### 8.1 Write Concerns

#### Write Concern Levels:
```javascript
// Write concern options:
// w: <number> - Number of members that must acknowledge
// j: <boolean> - Wait for journal commit
// wtimeout: <number> - Timeout in milliseconds

// Examples for Viettel IDC scenarios:

// Financial transactions: Maximum durability
db.billing_transactions.insertOne({
  transaction_id: "TXN_001",
  subscriber_id: "VT001234567", 
  amount: 100000,
  type: "charge",
  timestamp: new Date()
}, { 
  writeConcern: { 
    w: "majority",  // Wait for majority of replica set
    j: true,        // Wait for journal
    wtimeout: 5000  // Timeout after 5 seconds
  }
});

// Call logs: Performance over durability
db.call_records.insertMany([
  { /* call record 1 */ },
  { /* call record 2 */ }
], {
  writeConcern: { 
    w: 1,           // Only primary acknowledgment
    j: false        // Don't wait for journal
  }
});

// Critical updates: Ensure replication
db.subscribers.updateOne(
  { subscriber_id: "VT001234567" },
  { $set: { status: "suspended" } },
  { writeConcern: { w: 2, j: true, wtimeout: 3000 } }
);
```

### 8.2 Read Concerns

#### Read Concern Levels:
```javascript
// Read concern options for different consistency needs:

// local (default): Read from primary's local data
db.subscribers.find({ subscriber_id: "VT001234567" })
  .readConcern("local");

// available: Read from any available data (fastest)
db.call_records.find({ caller_id: "VT001234567" })
  .readConcern("available");

// majority: Read data acknowledged by majority
db.billing_transactions.find({ subscriber_id: "VT001234567" })
  .readConcern("majority");

// linearizable: Read own writes guarantee (strongest)
db.account_balances.findOne({ subscriber_id: "VT001234567" })
  .readConcern("linearizable");

// snapshot: Point-in-time consistent read (transactions)
session = db.getMongo().startSession();
session.startTransaction({
  readConcern: { level: "snapshot" },
  writeConcern: { w: "majority" }
});
```

### 8.3 Causal Consistency

#### Sessions and Causal Consistency:
```javascript
// Client session ensures causal consistency
const session = db.getMongo().startSession({
  causalConsistency: true
});

// Within session, reads see all writes that happened before
session.getDatabase("viettel_idc").subscribers.updateOne(
  { subscriber_id: "VT001234567" },
  { $set: { last_login: new Date() } }
);

// This read will see the update above
session.getDatabase("viettel_idc").subscribers.findOne(
  { subscriber_id: "VT001234567" }
);

session.endSession();

// Causal consistency across operations
const clusterTime = db.runCommand({ hello: 1 }).operationTime;

// Use cluster time for read-after-write consistency
db.subscribers.find({ status: "active" })
  .readConcern({ level: "majority", afterClusterTime: clusterTime });
```

---

## 9. Aggregation Framework

### 9.1 Pipeline Stages

#### Common Pipeline Stages:
```javascript
// Complex analytics pipeline for Viettel IDC
db.call_records.aggregate([
  // Stage 1: Filter data (pushed to shards)
  { $match: {
    call_date: { 
      $gte: ISODate("2024-01-01"),
      $lt: ISODate("2024-02-01")
    },
    duration: { $gte: 60 }  // Calls longer than 1 minute
  }},
  
  // Stage 2: Join with subscriber data
  { $lookup: {
    from: "subscribers",
    localField: "caller_id",
    foreignField: "subscriber_id", 
    as: "subscriber_info"
  }},
  
  // Stage 3: Unwind joined array
  { $unwind: "$subscriber_info" },
  
  // Stage 4: Add computed fields
  { $addFields: {
    cost_per_minute: { $divide: ["$cost", "$duration"] },
    call_hour: { $hour: "$call_date" },
    subscriber_plan: "$subscriber_info.plan_type"
  }},
  
  // Stage 5: Group and aggregate
  { $group: {
    _id: {
      plan_type: "$subscriber_plan",
      hour: "$call_hour"
    },
    total_calls: { $sum: 1 },
    total_duration: { $sum: "$duration" },
    total_revenue: { $sum: "$cost" },
    avg_cost_per_minute: { $avg: "$cost_per_minute" },
    unique_callers: { $addToSet: "$caller_id" }
  }},
  
  // Stage 6: Add computed group fields
  { $addFields: {
    unique_caller_count: { $size: "$unique_callers" },
    avg_call_duration: { $divide: ["$total_duration", "$total_calls"] }
  }},
  
  // Stage 7: Sort results
  { $sort: { 
    "_id.plan_type": 1,
    "_id.hour": 1 
  }},
  
  // Stage 8: Shape final output
  { $project: {
    plan_type: "$_id.plan_type",
    hour: "$_id.hour", 
    total_calls: 1,
    total_duration: 1,
    total_revenue: 1,
    avg_cost_per_minute: { $round: ["$avg_cost_per_minute", 4] },
    avg_call_duration: { $round: ["$avg_call_duration", 2] },
    unique_caller_count: 1,
    _id: 0
  }}
]);
```

### 9.2 Performance Optimization

#### Pipeline Optimization Rules:
```javascript
// Optimization 1: Move $match early
// BAD: Late filtering
db.call_records.aggregate([
  { $lookup: { from: "subscribers", ... } },
  { $unwind: "$subscribers" },
  { $match: { "subscribers.status": "active" } }  // Late filter
]);

// GOOD: Early filtering
db.call_records.aggregate([
  { $match: { 
    call_date: { $gte: ISODate("2024-01-01") },
    duration: { $gte: 60 }
  }},  // Early filter reduces documents
  { $lookup: { from: "subscribers", ... } },
  { $unwind: "$subscribers" },
  { $match: { "subscribers.status": "active" } }
]);

// Optimization 2: Use indexes
// Create supporting indexes
db.call_records.createIndex({ "call_date": 1, "duration": 1 });
db.subscribers.createIndex({ "subscriber_id": 1, "status": 1 });

// Optimization 3: Limit early when possible
db.call_records.aggregate([
  { $match: { call_date: { $gte: ISODate("2024-01-01") } } },
  { $sort: { call_date: -1 } },
  { $limit: 1000 },  // Limit early to reduce processing
  // ... other stages
]);
```

### 9.3 Map-Reduce Alternative

#### Aggregation vs Map-Reduce:
```javascript
// Map-Reduce (deprecated, avoid in new code)
db.call_records.mapReduce(
  function() {  // Map function
    emit(this.caller_id, { 
      calls: 1, 
      duration: this.duration,
      cost: this.cost 
    });
  },
  function(key, values) {  // Reduce function  
    var result = { calls: 0, duration: 0, cost: 0 };
    values.forEach(function(value) {
      result.calls += value.calls;
      result.duration += value.duration;
      result.cost += value.cost;
    });
    return result;
  },
  { 
    query: { call_date: { $gte: ISODate("2024-01-01") } },
    out: "call_summary"
  }
);

// Equivalent Aggregation (preferred)
db.call_records.aggregate([
  { $match: { call_date: { $gte: ISODate("2024-01-01") } } },
  { $group: {
    _id: "$caller_id",
    calls: { $sum: 1 },
    duration: { $sum: "$duration" },
    cost: { $sum: "$cost" }
  }},
  { $out: "call_summary" }
]);
```

---

## 10. Performance và Monitoring

### 10.1 Performance Metrics

#### Key Performance Indicators:
```javascript
// Server status overview
db.serverStatus();

// Key metrics to monitor:
const metrics = db.serverStatus();

// Operation counters
console.log("Operations:", {
  insert: metrics.opcounters.insert,
  query: metrics.opcounters.query, 
  update: metrics.opcounters.update,
  delete: metrics.opcounters.delete,
  command: metrics.opcounters.command
});

// Memory usage
console.log("Memory:", {
  resident: metrics.mem.resident + "MB",
  virtual: metrics.mem.virtual + "MB", 
  mapped: metrics.mem.mapped + "MB"
});

// WiredTiger cache
console.log("Cache:", {
  current_size: metrics.wiredTiger.cache["bytes currently in the cache"],
  max_size: metrics.wiredTiger.cache["maximum bytes configured"],
  dirty_bytes: metrics.wiredTiger.cache["tracked dirty bytes in the cache"]
});

// Connections
console.log("Connections:", {
  current: metrics.connections.current,
  available: metrics.connections.available,
  total_created: metrics.connections.totalCreated
});
```

### 10.2 Profiling

#### Database Profiler:
```javascript
// Enable profiling for slow operations (>100ms)
db.setProfilingLevel(1, { slowms: 100 });

// Profile all operations (development only)
db.setProfilingLevel(2);

// Check profiling status
db.getProfilingStatus();

// Query profiler collection
db.system.profile.find().limit(5).sort({ ts: -1 }).pretty();

/*
Sample profiler output:
{
  "op" : "query",
  "ns" : "viettel_idc.call_records",
  "command" : {
    "find" : "call_records",
    "filter" : { "caller_id" : "VT001234567" },
    "projection" : { }
  },
  "ts" : ISODate("2024-01-15T10:30:00.123Z"),
  "millis" : 150,
  "planSummary" : "IXSCAN { caller_id: 1 }",
  "keysExamined" : 100,
  "docsExamined" : 100,
  "cursorExhausted" : true,
  "numYield" : 0,
  "locks" : {
    "Global" : { "acquireCount" : { "r" : NumberLong(1) } },
    "Database" : { "acquireCount" : { "r" : NumberLong(1) } },
    "Collection" : { "acquireCount" : { "r" : NumberLong(1) } }
  },
  "user" : "admin@admin"
}
*/

// Disable profiling
db.setProfilingLevel(0);
```

### 10.3 Monitoring Best Practices

#### Production Monitoring Setup:
```javascript
// Custom monitoring script for Viettel IDC
function monitorMongoDB() {
  const status = db.serverStatus();
  const replStatus = rs.status();
  
  // Check replica set health
  const healthyMembers = replStatus.members.filter(m => m.health === 1);
  if (healthyMembers.length < 2) {
    alert("Replica set degraded: " + healthyMembers.length + " healthy members");
  }
  
  // Check replication lag
  const primary = replStatus.members.find(m => m.stateStr === "PRIMARY");
  const secondaries = replStatus.members.filter(m => m.stateStr === "SECONDARY");
  
  secondaries.forEach(secondary => {
    const lagMs = primary.optimeDate - secondary.optimeDate;
    if (lagMs > 5000) { // 5 second threshold
      alert("High replication lag: " + secondary.name + " " + lagMs + "ms");
    }
  });
  
  // Check connection usage
  const connUsage = status.connections.current / status.connections.available;
  if (connUsage > 0.8) {
    alert("High connection usage: " + Math.round(connUsage * 100) + "%");
  }
  
  // Check cache efficiency
  const cache = status.wiredTiger.cache;
  const cacheUsage = cache["bytes currently in the cache"] / cache["maximum bytes configured"];
  if (cacheUsage > 0.95) {
    alert("Cache nearly full: " + Math.round(cacheUsage * 100) + "%");
  }
  
  // Check slow operations
  const currentOps = db.currentOp({ "active": true, "secs_running": { "$gt": 5 } });
  if (currentOps.inprog.length > 0) {
    alert("Slow operations detected: " + currentOps.inprog.length);
  }
}

// Run monitoring every minute
setInterval(monitorMongoDB, 60000);
```

#### Performance Tuning Checklist:
```javascript
// 1. Index optimization
db.subscribers.getIndexes();
db.call_records.getIndexes();

// Check for unused indexes
db.runCommand({ collStats: "subscribers", indexDetails: true });

// 2. Query optimization
db.call_records.find({ caller_id: "VT001234567" }).explain("executionStats");

// 3. Connection pooling (application level)
const mongoose = require('mongoose');
mongoose.connect('mongodb://mongo1,mongo2,mongo3/viettel_idc', {
  maxPoolSize: 10,
  minPoolSize: 5,
  maxIdleTimeMS: 30000
});

// 4. Write concern optimization
// For high-throughput logging
db.call_records.insertMany(documents, { 
  writeConcern: { w: 1, j: false } 
});

// For critical data
db.billing_transactions.insertOne(document, {
  writeConcern: { w: "majority", j: true }
});

// 5. Read preference optimization
// Analytics queries to secondary
db.call_records.aggregate(pipeline).readPref("secondary");

// Real-time queries to primary
db.subscribers.findOne({ subscriber_id: id }).readPref("primary");
```

---

## 📚 Tham khảo Chuyên sâu

### Documentation:
1. **MongoDB Manual** - https://docs.mongodb.com/
2. **MongoDB University** - https://university.mongodb.com/
3. **MongoDB Community** - https://community.mongodb.com/

### Sách chuyên ngành:
1. **"MongoDB: The Definitive Guide"** - Shannon Bradshaw, Eoin Brazil, Kristina Chodorow
2. **"MongoDB Applied Design Patterns"** - Rick Copeland
3. **"50 Tips and Tricks for MongoDB Developers"** - Kristina Chodorow
4. **"Scaling MongoDB"** - Kristina Chodorow

### Tools và Utilities:
1. **MongoDB Compass** - GUI for MongoDB
2. **Studio 3T** - MongoDB IDE
3. **mongostat/mongotop** - Real-time monitoring
4. **MongoDB Ops Manager** - Enterprise monitoring
5. **Percona Monitoring** - Open-source monitoring

### Viettel IDC Applications:
- **Customer Data Platform**: 360-degree customer view
- **IoT Data Collection**: Network equipment monitoring  
- **Real-time Analytics**: Call patterns, usage trends
- **Content Management**: Flexible schema for diverse content
- **Session Storage**: High-performance user sessions
- **Geospatial Analysis**: Tower coverage optimization
