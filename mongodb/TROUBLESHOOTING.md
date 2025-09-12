# MongoDB Troubleshooting Guide
# Ainflue Platform Database Layer

## 📋 PROJECT INFORMATION
**Project:** Ainflue - AI-Powered Influencer Agent Platform  
**Module:** MongoDB Troubleshooting Guide  
**Version:** 1.0.0  
**Last Updated:** September 12, 2025  

## 👥 TEAM SPECIALTIES
- **Lead Support Engineer:** Fahed Mlaiel (mlaiel@live.de)
- **Database Troubleshooting Specialist:** Fahed Mlaiel (mlaiel@live.de)
- **Performance Analysis Expert:** Fahed Mlaiel (mlaiel@live.de)
- **Infrastructure Diagnostics Expert:** Fahed Mlaiel (mlaiel@live.de)

## ⚠️ INTELLECTUAL PROPERTY WARNING
**CRITICAL NOTICE:** This troubleshooting guide and all related intellectual property are the exclusive property of **Fahed Mlaiel**. Any unauthorized use, reproduction, or distribution is strictly prohibited.

**Contact for Authorization:** mlaiel@live.de

---

# 🔧 COMPREHENSIVE TROUBLESHOOTING GUIDE

## 🎯 Quick Diagnosis Commands

### 🔍 Health Check Commands
```bash
# Quick MongoDB health check
mongo --eval "db.adminCommand('ping')"

# Check replica set status
mongo --eval "rs.status()"

# Check server status
mongo --eval "db.serverStatus()"

# Check database statistics
mongo --eval "db.stats()"

# Check current operations
mongo --eval "db.currentOp()"

# Check profiler data
mongo --eval "db.system.profile.find().limit(5).sort({ts:-1}).pretty()"
```

### 📊 Performance Monitoring Commands
```bash
# Monitor real-time operations
mongostat --host localhost:27017

# Monitor I/O statistics
mongotop --host localhost:27017

# Check index usage
mongo --eval "db.collection.getIndexes()"

# Check slow queries
mongo --eval "db.getProfilingStatus()"
```

---

## 🚨 COMMON ISSUES & SOLUTIONS

### ❌ Connection Issues

#### 1. Connection Refused
**Symptoms:**
- Unable to connect to MongoDB
- Error: "Connection refused"
- Timeout errors

**Diagnosis:**
```bash
# Check if MongoDB is running
ps aux | grep mongod

# Check MongoDB status
systemctl status mongod

# Check port availability
netstat -tuln | grep 27017

# Test connection
telnet localhost 27017
```

**Solutions:**
```bash
# Start MongoDB service
sudo systemctl start mongod

# Enable MongoDB to start on boot
sudo systemctl enable mongod

# Check MongoDB configuration
sudo nano /etc/mongod.conf

# Verify bind IP configuration
# Change bindIp from 127.0.0.1 to 0.0.0.0 for external access
net:
  port: 27017
  bindIp: 0.0.0.0  # Allow connections from any IP

# Restart MongoDB
sudo systemctl restart mongod
```

#### 2. Authentication Failures
**Symptoms:**
- Authentication failed error
- Access denied messages
- Invalid credentials

**Diagnosis:**
```javascript
// Check authentication status
db.runCommand({connectionStatus: 1})

// List users
db.getUsers()

// Check roles
db.getRoles({showBuiltinRoles: true})
```

**Solutions:**
```javascript
// Create admin user
use admin
db.createUser({
  user: "admin",
  pwd: "secure_password",
  roles: [{role: "userAdminAnyDatabase", db: "admin"}]
})

// Create database user
use ainflue
db.createUser({
  user: "ainflue_user",
  pwd: "user_password",
  roles: [{role: "readWrite", db: "ainflue"}]
})

// Update user password
db.changeUserPassword("username", "new_password")

// Grant additional roles
db.grantRolesToUser("username", [{role: "dbAdmin", db: "ainflue"}])
```

### 🐌 Performance Issues

#### 1. Slow Queries
**Symptoms:**
- High response times
- Query timeouts
- Poor application performance

**Diagnosis:**
```javascript
// Enable profiling for slow operations
db.setProfilingLevel(1, {slowms: 100})

// Check slow queries
db.system.profile.find({millis: {$gt: 100}}).sort({ts: -1}).limit(10)

// Explain query execution
db.collection.find({field: "value"}).explain("executionStats")

// Check index usage
db.collection.getIndexes()
db.collection.stats({indexDetails: true})
```

**Solutions:**
```javascript
// Create appropriate indexes
db.collection.createIndex({field1: 1, field2: -1})

// Create compound indexes for complex queries
db.collection.createIndex({
  "user_id": 1,
  "created_at": -1,
  "status": 1
})

// Create text indexes for search
db.collection.createIndex({
  "title": "text",
  "description": "text"
})

// Use projection to limit returned fields
db.collection.find({}, {title: 1, summary: 1})

// Use pagination instead of large result sets
db.collection.find().skip(0).limit(20)
```

#### 2. High Memory Usage
**Symptoms:**
- MongoDB consuming excessive memory
- System becomes unresponsive
- Out of memory errors

**Diagnosis:**
```javascript
// Check memory usage
db.serverStatus().mem

// Check collection statistics
db.stats()

// Check index sizes
db.collection.stats().indexSizes

// Monitor memory with system tools
top -p $(pgrep mongod)
htop
```

**Solutions:**
```bash
# Configure WiredTiger cache size (50-60% of RAM)
# In /etc/mongod.conf
storage:
  engine: wiredTiger
  wiredTiger:
    engineConfig:
      cacheSizeGB: 4  # Adjust based on available RAM

# Enable compression
storage:
  wiredTiger:
    collectionConfig:
      blockCompressor: snappy
    indexConfig:
      prefixCompression: true

# Restart MongoDB to apply changes
sudo systemctl restart mongod
```

### 💾 Storage Issues

#### 1. Disk Space Full
**Symptoms:**
- Write operations failing
- "No space left on device" errors
- MongoDB crashes

**Diagnosis:**
```bash
# Check disk usage
df -h
du -sh /var/lib/mongodb/*

# Check MongoDB logs for disk space errors
tail -f /var/log/mongodb/mongod.log | grep -i "space"

# Check database sizes
mongo --eval "db.adminCommand('listCollections').cursor.firstBatch.forEach(function(collection){print(collection.name + ': ' + tojson(db.getCollection(collection.name).stats().size))})"
```

**Solutions:**
```bash
# Clean up old log files
sudo logrotate -f /etc/logrotate.d/mongodb

# Compact collections to reclaim space
mongo --eval "db.runCommand({compact: 'collection_name'})"

# Drop unnecessary indexes
mongo --eval "db.collection.dropIndex('index_name')"

# Archive old data
mongo --eval "db.old_collection.drop()"

# Add more disk space or move to larger volume
# Create new mount point
sudo mkdir /data/mongodb
sudo mount /dev/sdb1 /data/mongodb

# Update MongoDB configuration
# In /etc/mongod.conf
storage:
  dbPath: /data/mongodb
```

#### 2. Corrupted Data Files
**Symptoms:**
- MongoDB fails to start
- Assertion failures
- Data corruption errors

**Diagnosis:**
```bash
# Check MongoDB logs for corruption
grep -i corrupt /var/log/mongodb/mongod.log

# Run repair in standalone mode
mongod --dbpath /var/lib/mongodb --repair

# Check file system errors
sudo fsck /dev/sdb1
```

**Solutions:**
```bash
# Stop MongoDB
sudo systemctl stop mongod

# Repair database
mongod --dbpath /var/lib/mongodb --repair --repairpath /tmp/repair

# If repair fails, restore from backup
mongorestore --host localhost:27017 --db ainflue /backup/path

# Validate collections after repair
mongo --eval "db.collection.validate({full: true})"
```

### 🔄 Replication Issues

#### 1. Replica Set Not Initializing
**Symptoms:**
- Nodes not joining replica set
- Primary election failures
- Replica set configuration errors

**Diagnosis:**
```javascript
// Check replica set status
rs.status()

// Check replica set configuration
rs.conf()

// Check node connectivity
rs.isMaster()

// Check election process
db.adminCommand({replSetGetStatus: 1})
```

**Solutions:**
```javascript
// Initialize replica set
rs.initiate({
  _id: "rs0",
  members: [
    {_id: 0, host: "mongo1:27017"},
    {_id: 1, host: "mongo2:27017"},
    {_id: 2, host: "mongo3:27017"}
  ]
})

// Add member to replica set
rs.add("mongo4:27017")

// Remove member from replica set
rs.remove("mongo4:27017")

// Force reconfiguration
rs.reconfig(config, {force: true})

// Step down primary to trigger election
rs.stepDown()
```

#### 2. Replication Lag
**Symptoms:**
- Secondary nodes falling behind
- Read inconsistencies
- High replication lag

**Diagnosis:**
```javascript
// Check replication lag
rs.printReplicationInfo()
rs.printSecondaryReplicationInfo()

// Monitor oplog
db.oplog.rs.find().sort({$natural: -1}).limit(5)

// Check oplog size
db.oplog.rs.stats()
```

**Solutions:**
```javascript
// Increase oplog size
db.adminCommand({replSetResizeOplog: 1, size: 2000}) // 2GB

// Check network connectivity between nodes
// On each node, test connectivity to others
ping mongo2
telnet mongo2 27017

// Optimize write concern
db.collection.insertOne(doc, {writeConcern: {w: 1, j: false}})

// Use read preference to avoid reading from lagged secondaries
db.collection.find().readPref("primaryPreferred")
```

### ⚖️ Sharding Issues

#### 1. Shard Key Selection Problems
**Symptoms:**
- Uneven data distribution
- Hot spotting on specific shards
- Poor query performance

**Diagnosis:**
```javascript
// Check shard distribution
sh.status()

// Check chunk distribution
db.printShardingStatus()

// Check shard key statistics
db.collection.getShardDistribution()

// Analyze queries hitting multiple shards
db.collection.find({}).explain()
```

**Solutions:**
```javascript
// Choose better shard key (compound key example)
sh.shardCollection("ainflue.content", {
  "user_id": 1,
  "created_at": 1
})

// Enable balancer if disabled
sh.enableBalancing("ainflue.content")

// Split chunks manually if needed
sh.splitAt("ainflue.content", {"user_id": "middle_value"})

// Move chunks manually for better distribution
sh.moveChunk("ainflue.content", 
  {"user_id": "value"}, 
  "shard02"
)
```

#### 2. Config Server Issues
**Symptoms:**
- Metadata inconsistencies
- Sharding operations failing
- Config server not reachable

**Diagnosis:**
```javascript
// Check config server status
use config
db.shards.find()
db.databases.find()
db.collections.find()

// Check mongos connection to config servers
db.adminCommand("connPoolStats")
```

**Solutions:**
```javascript
// Restart config servers in proper order
// 1. Stop all mongos
// 2. Stop all config servers
// 3. Start config servers
// 4. Start mongos

// Fix config server replica set if needed
rs.initiate({
  _id: "configReplSet",
  configsvr: true,
  members: [
    {_id: 0, host: "config1:27019"},
    {_id: 1, host: "config2:27019"},
    {_id: 2, host: "config3:27019"}
  ]
})
```

---

## 🔧 DIAGNOSTIC TOOLS & SCRIPTS

### 📊 MongoDB Diagnostic Script
```python
#!/usr/bin/env python3
"""
MongoDB Diagnostic Tool for Ainflue Platform
Comprehensive health check and performance analysis
"""

import pymongo
import json
import time
from datetime import datetime, timedelta
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

class MongoDBDiagnostic:
    def __init__(self, connection_string):
        self.client = pymongo.MongoClient(connection_string)
        self.report = {
            "timestamp": datetime.utcnow().isoformat(),
            "connection": {},
            "server_status": {},
            "replication": {},
            "performance": {},
            "storage": {},
            "indexes": {},
            "recommendations": []
        }
    
    def run_diagnosis(self):
        """Run comprehensive diagnosis"""
        print("🔍 Starting MongoDB Diagnostic...")
        
        # Test connectivity
        self.check_connectivity()
        
        # Check server status
        self.check_server_status()
        
        # Check replication
        self.check_replication()
        
        # Check performance
        self.check_performance()
        
        # Check storage
        self.check_storage()
        
        # Check indexes
        self.check_indexes()
        
        # Generate recommendations
        self.generate_recommendations()
        
        return self.report
    
    def check_connectivity(self):
        """Test MongoDB connectivity"""
        try:
            self.client.admin.command('ping')
            self.report["connection"]["status"] = "connected"
            self.report["connection"]["server_info"] = self.client.server_info()
            print("✅ Connection successful")
        except Exception as e:
            self.report["connection"]["status"] = "failed"
            self.report["connection"]["error"] = str(e)
            print(f"❌ Connection failed: {e}")
    
    def check_server_status(self):
        """Check MongoDB server status"""
        try:
            status = self.client.admin.command('serverStatus')
            self.report["server_status"] = {
                "version": status.get("version"),
                "uptime": status.get("uptimeMillis"),
                "connections": status.get("connections"),
                "memory": status.get("mem"),
                "network": status.get("network"),
                "operations": status.get("opcounters")
            }
            print("✅ Server status collected")
        except Exception as e:
            print(f"❌ Failed to get server status: {e}")
    
    def check_replication(self):
        """Check replication status"""
        try:
            # Check if this is a replica set
            is_master = self.client.admin.command('isMaster')
            
            if is_master.get('ismaster') or is_master.get('secondary'):
                rs_status = self.client.admin.command('replSetGetStatus')
                self.report["replication"] = {
                    "is_replica_set": True,
                    "set_name": rs_status.get("set"),
                    "members": rs_status.get("members"),
                    "primary": None,
                    "secondaries": [],
                    "lag_seconds": 0
                }
                
                # Find primary and calculate lag
                primary_optime = None
                for member in rs_status.get("members", []):
                    if member.get("stateStr") == "PRIMARY":
                        self.report["replication"]["primary"] = member["name"]
                        primary_optime = member.get("optimeDate")
                    elif member.get("stateStr") == "SECONDARY":
                        self.report["replication"]["secondaries"].append({
                            "name": member["name"],
                            "lag_seconds": 0 if not primary_optime else 
                                (primary_optime - member.get("optimeDate")).total_seconds()
                        })
                
                print("✅ Replication status collected")
            else:
                self.report["replication"]["is_replica_set"] = False
                print("ℹ️ Not a replica set")
                
        except Exception as e:
            print(f"❌ Failed to check replication: {e}")
    
    def check_performance(self):
        """Check performance metrics"""
        try:
            # Get profiler data for slow operations
            profiler_data = list(self.client.admin.system.profile.find(
                {"millis": {"$gt": 100}}
            ).sort("ts", -1).limit(10))
            
            self.report["performance"] = {
                "slow_operations": len(profiler_data),
                "slow_ops_sample": profiler_data[:5],
                "current_operations": len(list(self.client.admin.current_op()["inprog"]))
            }
            
            print("✅ Performance metrics collected")
        except Exception as e:
            print(f"❌ Failed to check performance: {e}")
    
    def check_storage(self):
        """Check storage statistics"""
        try:
            databases = self.client.list_database_names()
            storage_info = {}
            
            for db_name in databases:
                if db_name not in ["admin", "local", "config"]:
                    db = self.client[db_name]
                    stats = db.command("dbStats")
                    storage_info[db_name] = {
                        "size_mb": round(stats.get("dataSize", 0) / 1024 / 1024, 2),
                        "index_size_mb": round(stats.get("indexSize", 0) / 1024 / 1024, 2),
                        "collections": stats.get("collections", 0),
                        "indexes": stats.get("indexes", 0)
                    }
            
            self.report["storage"] = storage_info
            print("✅ Storage statistics collected")
        except Exception as e:
            print(f"❌ Failed to check storage: {e}")
    
    def check_indexes(self):
        """Check index usage and efficiency"""
        try:
            databases = self.client.list_database_names()
            index_info = {}
            
            for db_name in databases:
                if db_name not in ["admin", "local", "config"]:
                    db = self.client[db_name]
                    collections = db.list_collection_names()
                    
                    for collection_name in collections:
                        collection = db[collection_name]
                        indexes = collection.list_indexes()
                        
                        collection_indexes = []
                        for index in indexes:
                            index_stats = collection.index_information()
                            collection_indexes.append({
                                "name": index["name"],
                                "key": index["key"],
                                "size_bytes": index_stats.get(index["name"], {}).get("size", 0)
                            })
                        
                        if collection_indexes:
                            if db_name not in index_info:
                                index_info[db_name] = {}
                            index_info[db_name][collection_name] = collection_indexes
            
            self.report["indexes"] = index_info
            print("✅ Index information collected")
        except Exception as e:
            print(f"❌ Failed to check indexes: {e}")
    
    def generate_recommendations(self):
        """Generate optimization recommendations"""
        recommendations = []
        
        # Check connection count
        connections = self.report.get("server_status", {}).get("connections", {})
        if connections.get("current", 0) > connections.get("available", 1000) * 0.8:
            recommendations.append({
                "type": "performance",
                "severity": "high",
                "issue": "High connection usage",
                "recommendation": "Consider connection pooling optimization or scaling"
            })
        
        # Check memory usage
        memory = self.report.get("server_status", {}).get("memory", {})
        if memory.get("resident", 0) > 8000:  # 8GB
            recommendations.append({
                "type": "performance",
                "severity": "medium",
                "issue": "High memory usage",
                "recommendation": "Monitor memory usage and consider caching optimization"
            })
        
        # Check replication lag
        replication = self.report.get("replication", {})
        if replication.get("is_replica_set"):
            for secondary in replication.get("secondaries", []):
                if secondary.get("lag_seconds", 0) > 60:
                    recommendations.append({
                        "type": "replication",
                        "severity": "high",
                        "issue": f"High replication lag on {secondary['name']}",
                        "recommendation": "Check network connectivity and oplog size"
                    })
        
        # Check slow operations
        performance = self.report.get("performance", {})
        if performance.get("slow_operations", 0) > 10:
            recommendations.append({
                "type": "performance",
                "severity": "medium",
                "issue": "Multiple slow operations detected",
                "recommendation": "Review queries and add appropriate indexes"
            })
        
        self.report["recommendations"] = recommendations
        print(f"✅ Generated {len(recommendations)} recommendations")
    
    def export_report(self, filename="mongodb_diagnostic_report.json"):
        """Export diagnostic report to file"""
        with open(filename, 'w') as f:
            json.dump(self.report, f, indent=2, default=str)
        print(f"📊 Report exported to {filename}")

# Usage example
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python mongodb_diagnostic.py <connection_string>")
        sys.exit(1)
    
    connection_string = sys.argv[1]
    diagnostic = MongoDBDiagnostic(connection_string)
    
    try:
        report = diagnostic.run_diagnosis()
        diagnostic.export_report()
        
        # Print summary
        print("\n📋 DIAGNOSTIC SUMMARY")
        print("=" * 50)
        print(f"Connection Status: {report['connection'].get('status', 'unknown')}")
        print(f"Server Version: {report.get('server_status', {}).get('version', 'unknown')}")
        print(f"Is Replica Set: {report.get('replication', {}).get('is_replica_set', False)}")
        print(f"Slow Operations: {report.get('performance', {}).get('slow_operations', 0)}")
        print(f"Recommendations: {len(report.get('recommendations', []))}")
        
        if report.get('recommendations'):
            print("\n⚠️ RECOMMENDATIONS:")
            for rec in report['recommendations']:
                print(f"  {rec['severity'].upper()}: {rec['issue']} - {rec['recommendation']}")
        
    except Exception as e:
        print(f"❌ Diagnostic failed: {e}")
        sys.exit(1)
```

### 🔧 Quick Fix Scripts

#### 1. Connection Pool Optimizer
```bash
#!/bin/bash
# connection_optimizer.sh
# Optimize MongoDB connection pool settings

echo "🔧 MongoDB Connection Pool Optimizer"

# Check current connections
echo "Current connections:"
mongo --eval "db.serverStatus().connections"

# Check connection pool configuration
echo "Checking connection pool settings..."

# Update mongod.conf with optimized settings
cat << EOF >> /etc/mongod.conf.optimized
# Optimized connection settings
net:
  maxIncomingConnections: 1000
  compression:
    compressors: "snappy,zlib,zstd"

# WiredTiger settings
storage:
  wiredTiger:
    engineConfig:
      cacheSizeGB: 4
      maxCacheOverflowFileSizeGB: 0
      statisticsLogDelaySecs: 0
    collectionConfig:
      blockCompressor: snappy
    indexConfig:
      prefixCompression: true

# Operation profiling
operationProfiling:
  mode: slowOp
  slowOpThresholdMs: 100

setParameter:
  maxLogSizeKB: 10
  logComponentVerbosity:
    command: 0
EOF

echo "✅ Optimized configuration created in /etc/mongod.conf.optimized"
echo "Review and replace /etc/mongod.conf, then restart MongoDB"
```

#### 2. Index Optimizer
```python
#!/usr/bin/env python3
# index_optimizer.py
# Analyze and optimize MongoDB indexes

import pymongo
import json
from collections import defaultdict

def analyze_indexes(connection_string, database_name):
    """Analyze index usage and recommend optimizations"""
    
    client = pymongo.MongoClient(connection_string)
    db = client[database_name]
    
    print(f"🔍 Analyzing indexes for database: {database_name}")
    
    # Get all collections
    collections = db.list_collection_names()
    
    analysis = {
        "unused_indexes": [],
        "redundant_indexes": [],
        "missing_indexes": [],
        "oversized_indexes": []
    }
    
    for collection_name in collections:
        collection = db[collection_name]
        
        # Get index statistics
        try:
            index_stats = db.command("collStats", collection_name, indexDetails=True)
            indexes = collection.list_indexes()
            
            for index in indexes:
                index_name = index["name"]
                
                # Skip default _id index
                if index_name == "_id_":
                    continue
                
                # Check for unused indexes (requires MongoDB 3.2+)
                try:
                    usage_stats = collection.index_stats()
                    for stat in usage_stats:
                        if stat["name"] == index_name:
                            if stat["accesses"]["ops"] == 0:
                                analysis["unused_indexes"].append({
                                    "collection": collection_name,
                                    "index": index_name,
                                    "key": index["key"]
                                })
                except:
                    pass
                
                # Check for oversized indexes
                index_size = index_stats.get("indexSizes", {}).get(index_name, 0)
                if index_size > 100 * 1024 * 1024:  # 100MB
                    analysis["oversized_indexes"].append({
                        "collection": collection_name,
                        "index": index_name,
                        "size_mb": round(index_size / 1024 / 1024, 2)
                    })
            
        except Exception as e:
            print(f"❌ Error analyzing collection {collection_name}: {e}")
    
    # Print analysis results
    print("\n📊 INDEX ANALYSIS RESULTS")
    print("=" * 40)
    
    if analysis["unused_indexes"]:
        print("\n🗑️ UNUSED INDEXES:")
        for idx in analysis["unused_indexes"]:
            print(f"  {idx['collection']}.{idx['index']} - {idx['key']}")
            print(f"    Command to drop: db.{idx['collection']}.dropIndex('{idx['index']}')")
    
    if analysis["oversized_indexes"]:
        print("\n📈 OVERSIZED INDEXES:")
        for idx in analysis["oversized_indexes"]:
            print(f"  {idx['collection']}.{idx['index']} - {idx['size_mb']}MB")
    
    if not any(analysis.values()):
        print("✅ No major index issues found!")
    
    return analysis

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 3:
        print("Usage: python index_optimizer.py <connection_string> <database_name>")
        sys.exit(1)
    
    connection_string = sys.argv[1]
    database_name = sys.argv[2]
    
    try:
        analyze_indexes(connection_string, database_name)
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        sys.exit(1)
```

---

## 📞 SUPPORT & CONTACT

**Support Engineering:** Fahed Mlaiel (mlaiel@live.de)  
**Project:** Ainflue Platform  
**Module:** MongoDB Troubleshooting Guide  
**Documentation Version:** 1.0.0  

---

**© 2025 Fahed Mlaiel - All Rights Reserved**  
**Contact:** mlaiel@live.de  
**Unauthorized use prohibited - Legal action will be taken**