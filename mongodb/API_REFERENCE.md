# MongoDB API Reference
# Ainflue Platform Database Layer

## 📋 PROJECT INFORMATION
**Project:** Ainflue - AI-Powered Influencer Agent Platform  
**Module:** MongoDB Database Layer API Reference  
**Version:** 1.0.0  
**Last Updated:** September 12, 2025  

## 👥 TEAM SPECIALTIES
- **Lead AI Engineer & API Architect:** Fahed Mlaiel (mlaiel@live.de)
- **Database API Specialist:** Fahed Mlaiel (mlaiel@live.de)
- **Backend Systems Engineer:** Fahed Mlaiel (mlaiel@live.de)
- **Security & Compliance Expert:** Fahed Mlaiel (mlaiel@live.de)

## ⚠️ INTELLECTUAL PROPERTY WARNING
**CRITICAL NOTICE:** This API documentation and all related intellectual property are the exclusive property of **Fahed Mlaiel**. Any unauthorized use, reproduction, distribution, or commercialization is strictly prohibited.

**Contact for Authorization:** mlaiel@live.de

---

# 📚 API REFERENCE GUIDE

## 🔌 Core Connection API

### MongoDBConnection Class

#### Initialization
```python
from mongodb.connection import MongoDBConnection

# Basic connection
connection = MongoDBConnection(
    connection_string="mongodb://localhost:27017",
    database_name="ainflue"
)

# Advanced connection with options
connection = MongoDBConnection(
    connection_string="mongodb+srv://user:pass@cluster.mongodb.net",
    database_name="ainflue_prod",
    connection_options={
        "maxPoolSize": 100,
        "minPoolSize": 10,
        "maxIdleTimeMS": 30000,
        "serverSelectionTimeoutMS": 5000,
        "ssl": True,
        "replicaSet": "rs0"
    }
)
```

#### Core Methods

##### async connect()
Establishes connection to MongoDB cluster.

```python
await connection.connect()
```

**Returns:** `bool` - True if connection successful

**Raises:** 
- `ConnectionFailure` - If unable to connect
- `ServerSelectionTimeoutError` - If server selection times out

##### async disconnect()
Closes all connections and cleans up resources.

```python
await connection.disconnect()
```

**Returns:** `None`

##### async get_database()
Returns the database instance.

```python
db = await connection.get_database()
```

**Returns:** `AsyncIOMotorDatabase` - Database instance

##### async health_check()
Performs comprehensive health check.

```python
health_status = await connection.health_check()
```

**Returns:** `Dict[str, Any]` - Health status information
```python
{
    "status": "healthy",
    "connection_status": "connected",
    "replica_set_status": "primary",
    "database_stats": {...},
    "performance_metrics": {...}
}
```

---

## 📊 Collection Management API

### MongoDBCollectionManager Class

#### Initialization
```python
from mongodb.collections import MongoDBCollectionManager

manager = MongoDBCollectionManager(connection)
```

#### Core Methods

##### async create_collection(name, schema=None, indexes=None)
Creates a new collection with optional schema validation.

```python
# Basic collection
await manager.create_collection("users")

# Collection with schema validation
user_schema = {
    "bsonType": "object",
    "required": ["email", "username"],
    "properties": {
        "email": {"bsonType": "string", "pattern": "^.+@.+$"},
        "username": {"bsonType": "string", "minLength": 3}
    }
}

await manager.create_collection(
    name="users",
    schema=user_schema,
    indexes=[
        {"key": {"email": 1}, "unique": True},
        {"key": {"username": 1}, "unique": True}
    ]
)
```

**Parameters:**
- `name` (str): Collection name
- `schema` (Dict, optional): JSON schema for validation
- `indexes` (List[Dict], optional): Initial indexes to create

**Returns:** `bool` - True if collection created successfully

##### async get_collection(name)
Retrieves a collection instance.

```python
users_collection = await manager.get_collection("users")
```

**Returns:** `AsyncIOMotorCollection` - Collection instance

##### async insert_document(collection_name, document)
Inserts a single document with validation.

```python
user_doc = {
    "email": "user@example.com",
    "username": "john_doe",
    "created_at": datetime.utcnow()
}

result = await manager.insert_document("users", user_doc)
```

**Returns:** `InsertOneResult` - Insert operation result

##### async insert_many_documents(collection_name, documents)
Inserts multiple documents efficiently.

```python
documents = [
    {"email": "user1@example.com", "username": "user1"},
    {"email": "user2@example.com", "username": "user2"}
]

result = await manager.insert_many_documents("users", documents)
```

**Returns:** `InsertManyResult` - Bulk insert operation result

##### async find_documents(collection_name, filter=None, projection=None, sort=None, limit=None)
Finds documents with advanced filtering.

```python
# Find all users
users = await manager.find_documents("users")

# Find with filtering and projection
active_users = await manager.find_documents(
    collection_name="users",
    filter={"status": "active"},
    projection={"email": 1, "username": 1},
    sort=[("created_at", -1)],
    limit=10
)
```

**Parameters:**
- `collection_name` (str): Target collection
- `filter` (Dict, optional): Query filter
- `projection` (Dict, optional): Field projection
- `sort` (List[Tuple], optional): Sort specification
- `limit` (int, optional): Result limit

**Returns:** `List[Dict]` - List of matching documents

##### async update_document(collection_name, filter, update, upsert=False)
Updates a single document.

```python
result = await manager.update_document(
    collection_name="users",
    filter={"email": "user@example.com"},
    update={"$set": {"last_login": datetime.utcnow()}},
    upsert=False
)
```

**Returns:** `UpdateResult` - Update operation result

##### async delete_document(collection_name, filter)
Deletes a single document.

```python
result = await manager.delete_document(
    collection_name="users",
    filter={"email": "user@example.com"}
)
```

**Returns:** `DeleteResult` - Delete operation result

---

## 🏗️ Data Models API

### MongoDBModels Class

#### User Model Example
```python
from mongodb.models import MongoDBModels
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserModel(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    is_active: bool = True
    created_at: datetime = datetime.utcnow()
    
    class Config:
        # MongoDB ObjectId handling
        allow_population_by_field_name = True
        arbitrary_types_allowed = True

models = MongoDBModels()
```

#### Core Methods

##### async save_model(collection_name, model_instance)
Saves a Pydantic model to MongoDB.

```python
user = UserModel(
    email="user@example.com",
    username="john_doe",
    full_name="John Doe"
)

result = await models.save_model("users", user)
```

**Returns:** `str` - Document ObjectId

##### async get_model(collection_name, model_class, filter)
Retrieves and validates documents as Pydantic models.

```python
user = await models.get_model(
    collection_name="users",
    model_class=UserModel,
    filter={"email": "user@example.com"}
)
```

**Returns:** `UserModel` - Validated model instance

##### async update_model(collection_name, filter, model_instance)
Updates a document using a Pydantic model.

```python
user.full_name = "John Smith"
result = await models.update_model(
    collection_name="users",
    filter={"email": user.email},
    model_instance=user
)
```

**Returns:** `UpdateResult` - Update operation result

---

## 🔍 Search API

### TextSearchEngine Class

```python
from mongodb.search import TextSearchEngine

search_engine = TextSearchEngine(connection)
```

#### Core Methods

##### async create_text_index(collection_name, fields, weights=None)
Creates a full-text search index.

```python
await search_engine.create_text_index(
    collection_name="content",
    fields=["title", "description", "tags"],
    weights={"title": 10, "description": 5, "tags": 3}
)
```

##### async search_text(collection_name, query, limit=10)
Performs full-text search.

```python
results = await search_engine.search_text(
    collection_name="content",
    query="AI influencer marketing",
    limit=20
)
```

**Returns:** `List[Dict]` - Search results with relevance scores

##### async autocomplete(collection_name, field, query, limit=5)
Provides autocomplete suggestions.

```python
suggestions = await search_engine.autocomplete(
    collection_name="content",
    field="title",
    query="AI market",
    limit=5
)
```

**Returns:** `List[str]` - Autocomplete suggestions

---

## 📊 Aggregation API

### PipelineBuilder Class

```python
from mongodb.aggregation import PipelineBuilder

pipeline = PipelineBuilder()
```

#### Core Methods

##### match(filter)
Adds a $match stage to the pipeline.

```python
pipeline.match({"status": "active", "created_at": {"$gte": datetime.now() - timedelta(days=30)}})
```

##### group(id_field, operations)
Adds a $group stage for aggregation.

```python
pipeline.group(
    id_field="$category",
    operations={
        "count": {"$sum": 1},
        "avg_score": {"$avg": "$score"},
        "total_views": {"$sum": "$views"}
    }
)
```

##### sort(sort_spec)
Adds a $sort stage.

```python
pipeline.sort({"count": -1, "avg_score": -1})
```

##### limit(count)
Adds a $limit stage.

```python
pipeline.limit(10)
```

##### project(projection)
Adds a $project stage for field selection.

```python
pipeline.project({
    "category": 1,
    "count": 1,
    "avg_score": {"$round": ["$avg_score", 2]}
})
```

##### async execute(collection_name)
Executes the aggregation pipeline.

```python
results = await pipeline.execute("content")
```

**Returns:** `List[Dict]` - Aggregation results

#### Content Analytics Example
```python
from mongodb.aggregation import ContentAnalytics

analytics = ContentAnalytics(connection)

# Get content performance metrics
metrics = await analytics.get_content_performance(
    date_range={"start": "2025-01-01", "end": "2025-01-31"},
    category="ai-content",
    limit=50
)
```

---

## 🔐 Security API

### EncryptionManager Class

```python
from mongodb.security import EncryptionManager

encryption = EncryptionManager(connection)
```

#### Core Methods

##### async encrypt_field(collection_name, field_name, encryption_key)
Encrypts a specific field in all documents.

```python
await encryption.encrypt_field(
    collection_name="users",
    field_name="email",
    encryption_key="user_email_key"
)
```

##### async decrypt_field(collection_name, field_name, encryption_key)
Decrypts a specific field in all documents.

```python
await encryption.decrypt_field(
    collection_name="users",
    field_name="email",
    encryption_key="user_email_key"
)
```

##### generate_encryption_key()
Generates a new encryption key.

```python
new_key = encryption.generate_encryption_key()
```

**Returns:** `str` - Base64 encoded encryption key

### AccessControlManager Class

```python
from mongodb.security import AccessControlManager

access_control = AccessControlManager(connection)
```

#### Core Methods

##### async create_role(role_name, permissions)
Creates a new role with specific permissions.

```python
await access_control.create_role(
    role_name="content_editor",
    permissions={
        "collections": {
            "content": ["read", "write"],
            "users": ["read"]
        },
        "operations": ["aggregate", "search"]
    }
)
```

##### async assign_role(user_id, role_name)
Assigns a role to a user.

```python
await access_control.assign_role(
    user_id="64f123abc456def789012345",
    role_name="content_editor"
)
```

##### async check_permission(user_id, collection_name, operation)
Checks if a user has permission for an operation.

```python
has_permission = await access_control.check_permission(
    user_id="64f123abc456def789012345",
    collection_name="content",
    operation="write"
)
```

**Returns:** `bool` - True if user has permission

---

## ⚡ Performance API

### QueryOptimizer Class

```python
from mongodb.performance import QueryOptimizer

optimizer = QueryOptimizer(connection)
```

#### Core Methods

##### async analyze_query(collection_name, query)
Analyzes query performance and suggests optimizations.

```python
analysis = await optimizer.analyze_query(
    collection_name="content",
    query={"category": "ai", "status": "published"}
)
```

**Returns:** `Dict[str, Any]` - Query analysis with optimization suggestions

##### async create_optimal_index(collection_name, query)
Creates an optimal index for a specific query.

```python
index_result = await optimizer.create_optimal_index(
    collection_name="content",
    query={"category": 1, "created_at": -1}
)
```

##### async get_slow_queries(threshold_ms=100)
Retrieves slow queries for analysis.

```python
slow_queries = await optimizer.get_slow_queries(threshold_ms=500)
```

**Returns:** `List[Dict]` - List of slow queries with execution stats

### CacheManager Class

```python
from mongodb.performance import CacheManager

cache = CacheManager(connection)
```

#### Core Methods

##### async cache_query_result(cache_key, result, ttl=300)
Caches a query result.

```python
await cache.cache_query_result(
    cache_key="popular_content_24h",
    result=query_results,
    ttl=3600  # 1 hour
)
```

##### async get_cached_result(cache_key)
Retrieves a cached result.

```python
cached_result = await cache.get_cached_result("popular_content_24h")
```

**Returns:** `Any` - Cached result or None if not found

##### async invalidate_cache(pattern)
Invalidates cache entries matching a pattern.

```python
await cache.invalidate_cache("content_*")
```

---

## 📈 Monitoring API

### MongoDBMonitor Class

```python
from mongodb.monitoring import MongoDBMonitor

monitor = MongoDBMonitor(connection)
```

#### Core Methods

##### async get_performance_metrics()
Retrieves real-time performance metrics.

```python
metrics = await monitor.get_performance_metrics()
```

**Returns:** `Dict[str, Any]` - Performance metrics
```python
{
    "connections": {"current": 45, "available": 155},
    "operations": {"queries_per_second": 1250, "writes_per_second": 300},
    "memory": {"resident_mb": 2048, "virtual_mb": 4096},
    "replication": {"lag_seconds": 0.1, "oplog_size_mb": 1024},
    "indexes": {"total_index_size_mb": 512, "total_indexes": 150}
}
```

##### async get_health_status()
Gets comprehensive health status.

```python
health = await monitor.get_health_status()
```

**Returns:** `Dict[str, Any]` - Health status information

##### async set_alert_threshold(metric_name, threshold, operator="gt")
Sets up performance alerts.

```python
await monitor.set_alert_threshold(
    metric_name="queries_per_second",
    threshold=5000,
    operator="gt"
)
```

##### async get_collection_stats(collection_name)
Gets detailed statistics for a collection.

```python
stats = await monitor.get_collection_stats("users")
```

**Returns:** `Dict[str, Any]` - Collection statistics

---

## 🚀 Deployment API

### ClusterDeployer Class

```python
from mongodb.deployment import ClusterDeployer

deployer = ClusterDeployer()
```

#### Core Methods

##### async deploy_replica_set(config)
Deploys a MongoDB replica set.

```python
replica_config = {
    "cluster_name": "ainflue-prod",
    "nodes": [
        {"host": "mongo1.example.com", "port": 27017, "role": "primary"},
        {"host": "mongo2.example.com", "port": 27017, "role": "secondary"},
        {"host": "mongo3.example.com", "port": 27017, "role": "secondary"}
    ],
    "auth": {"username": "admin", "password": "secure_password"},
    "ssl": True
}

deployment = await deployer.deploy_replica_set(replica_config)
```

##### async setup_sharding(shard_config)
Sets up MongoDB sharding.

```python
shard_config = {
    "config_servers": ["config1:27019", "config2:27019", "config3:27019"],
    "shards": [
        {"name": "shard1", "members": ["shard1a:27018", "shard1b:27018"]},
        {"name": "shard2", "members": ["shard2a:27018", "shard2b:27018"]}
    ],
    "mongos": ["mongos1:27017", "mongos2:27017"]
}

sharding = await deployer.setup_sharding(shard_config)
```

---

## 🔄 Backup & Restore API

### BackupManager Class

```python
from mongodb.backup import BackupManager

backup_manager = BackupManager(connection)
```

#### Core Methods

##### async create_backup(backup_name, collections=None)
Creates a database backup.

```python
backup_result = await backup_manager.create_backup(
    backup_name="daily_backup_2025_01_12",
    collections=["users", "content", "analytics"]  # None for all collections
)
```

##### async restore_backup(backup_name, target_database=None)
Restores from a backup.

```python
restore_result = await backup_manager.restore_backup(
    backup_name="daily_backup_2025_01_12",
    target_database="ainflue_restored"
)
```

##### async schedule_backup(schedule, backup_config)
Schedules automatic backups.

```python
await backup_manager.schedule_backup(
    schedule="0 2 * * *",  # Daily at 2 AM
    backup_config={
        "name_pattern": "auto_backup_{timestamp}",
        "retention_days": 30,
        "compress": True,
        "encrypt": True
    }
)
```

---

## 🎮 Gamification API

### AchievementManager Class

```python
from mongodb.gamification import AchievementManager

achievements = AchievementManager(connection)
```

#### Core Methods

##### async create_achievement(achievement_data)
Creates a new achievement.

```python
achievement = await achievements.create_achievement({
    "name": "Content Creator Pro",
    "description": "Upload 100 pieces of content",
    "criteria": {"content_uploads": 100},
    "reward_points": 1000,
    "badge_url": "/badges/content-creator-pro.png"
})
```

##### async check_achievements(user_id)
Checks and unlocks achievements for a user.

```python
unlocked = await achievements.check_achievements(user_id="64f123...")
```

**Returns:** `List[Dict]` - Newly unlocked achievements

##### async get_leaderboard(category="overall", limit=10)
Gets leaderboard rankings.

```python
leaderboard = await achievements.get_leaderboard(
    category="content_creation",
    limit=25
)
```

**Returns:** `List[Dict]` - Ranked user list with scores

---

## 📱 Multi-Platform API

### PlatformManager Class

```python
from mongodb.platforms import PlatformManager

platform_manager = PlatformManager(connection)
```

#### Core Methods

##### async sync_content(platform_name, content_id)
Syncs content to a specific platform.

```python
sync_result = await platform_manager.sync_content(
    platform_name="instagram",
    content_id="64f123abc456def789012345"
)
```

##### async get_platform_analytics(platform_name, date_range)
Gets analytics from a platform.

```python
analytics = await platform_manager.get_platform_analytics(
    platform_name="youtube",
    date_range={"start": "2025-01-01", "end": "2025-01-31"}
)
```

##### async resolve_conflict(conflict_id, resolution_strategy)
Resolves cross-platform conflicts.

```python
resolution = await platform_manager.resolve_conflict(
    conflict_id="conflict_123",
    resolution_strategy="prefer_latest"
)
```

---

## 🧪 Error Handling

### Common Exception Types

```python
from mongodb.exceptions import (
    MongoDBConnectionError,
    ValidationError,
    SecurityError,
    PerformanceError,
    BackupError
)

try:
    await connection.connect()
except MongoDBConnectionError as e:
    logger.error(f"Failed to connect: {e}")
    
try:
    await manager.insert_document("users", invalid_doc)
except ValidationError as e:
    logger.error(f"Validation failed: {e}")
```

### Error Response Format
```python
{
    "error": {
        "type": "ValidationError",
        "message": "Document validation failed",
        "details": {
            "field": "email",
            "constraint": "required"
        },
        "timestamp": "2025-01-12T10:30:00Z"
    }
}
```

---

## 📊 Response Formats

### Standard Success Response
```python
{
    "success": True,
    "data": {...},
    "metadata": {
        "operation": "insert_document",
        "collection": "users",
        "timestamp": "2025-01-12T10:30:00Z",
        "execution_time_ms": 15
    }
}
```

### Paginated Response
```python
{
    "success": True,
    "data": [...],
    "pagination": {
        "page": 1,
        "per_page": 20,
        "total_pages": 5,
        "total_count": 100,
        "has_next": True,
        "has_prev": False
    }
}
```

---

## 📞 SUPPORT & CONTACT

**Technical Leadership:** Fahed Mlaiel (mlaiel@live.de)  
**Project:** Ainflue Platform  
**Module:** MongoDB API Reference  
**Documentation Version:** 1.0.0  

---

**© 2025 Fahed Mlaiel - All Rights Reserved**  
**Contact:** mlaiel@live.de  
**Unauthorized use prohibited - Legal action will be taken**