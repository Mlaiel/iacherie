"""
⚠️ AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

Database Service Template for iacherie Creator Economy Platform
Enterprise database service with multi-provider support, connection pooling, and advanced monitoring
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, AsyncGenerator
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import secrets

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, validator
import asyncpg
import aiomysql
import motor.motor_asyncio
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker
from databases import Database
from redis import Redis
import logging
from prometheus_client import Counter, Histogram, Gauge


class DatabaseProvider(str, Enum):
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MONGODB = "mongodb"
    REDIS = "redis"
    CASSANDRA = "cassandra"
    ELASTICSEARCH = "elasticsearch"
    CLICKHOUSE = "clickhouse"


class QueryType(str, Enum):
    SELECT = "select"
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"
    AGGREGATE = "aggregate"
    TRANSACTION = "transaction"


class ConnectionStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    MAINTENANCE = "maintenance"


@dataclass
class DatabaseConfig:
    """Configuration du service de base de données"""
    # Connection settings
    primary_provider: DatabaseProvider = DatabaseProvider.POSTGRESQL
    read_replicas: List[str] = field(default_factory=list)
    write_primary: str = "postgresql://user:pass@localhost:5432/iacherie"
    
    # Connection pooling
    pool_size: int = 20
    max_overflow: int = 30
    pool_timeout: int = 30
    pool_recycle: int = 3600
    
    # Query optimization
    slow_query_threshold_ms: int = 1000
    enable_query_cache: bool = True
    cache_ttl_seconds: int = 300
    
    # Monitoring
    enable_metrics: bool = True
    enable_query_logging: bool = True
    enable_performance_insights: bool = True
    
    # High availability
    enable_read_write_split: bool = True
    enable_automatic_failover: bool = True
    health_check_interval: int = 30
    
    # Security
    enable_ssl: bool = True
    enable_query_validation: bool = True
    max_query_complexity: int = 1000


class DatabaseQuery(BaseModel):
    """Requête de base de données"""
    query_id: Optional[str] = None
    query: str
    parameters: Dict[str, Any] = {}
    query_type: QueryType = QueryType.SELECT
    use_cache: bool = True
    timeout_seconds: int = 30
    read_preference: str = "primary"  # primary, secondary, nearest


class QueryResult(BaseModel):
    """Résultat de requête"""
    query_id: str
    success: bool
    data: List[Dict[str, Any]] = []
    affected_rows: int = 0
    execution_time_ms: float
    from_cache: bool = False
    metadata: Dict[str, Any] = {}


class ConnectionHealth(BaseModel):
    """Santé de connexion"""
    provider: DatabaseProvider
    connection_id: str
    status: ConnectionStatus
    response_time_ms: float
    active_connections: int
    idle_connections: int
    last_check: datetime
    error_count: int = 0


class DatabaseServiceTemplate:
    """
    Template de service de base de données enterprise pour iacherie
    
    Fonctionnalités:
    - Multi-provider support (PostgreSQL, MySQL, MongoDB, Redis, etc.)
    - Connection pooling avancé avec monitoring
    - Read/Write splitting automatique
    - Query caching intelligent
    - Performance monitoring et optimization
    - High availability avec failover automatique
    - Security et validation des requêtes
    - Métriques et observabilité complètes
    """
    
    def __init__(self, config: DatabaseConfig = None):
        self.config = config or DatabaseConfig()
        self.app = FastAPI(
            title="iacherie Database Service",
            description="Enterprise database service with multi-provider support",
            version="1.0.0"
        )
        
        # Connection pools
        self.connection_pools: Dict[str, Any] = {}
        self.read_pools: Dict[str, Any] = {}
        
        # Redis pour cache
        self.redis = Redis(host='localhost', port=6379, db=8, decode_responses=True)
        
        # Query cache
        self.query_cache: Dict[str, Any] = {}
        
        # Health tracking
        self.connection_health: Dict[str, ConnectionHealth] = {}
        
        # Métriques Prometheus
        self.query_count = Counter('database_queries_total', ['provider', 'query_type', 'status'])
        self.query_duration = Histogram('database_query_duration_seconds', ['provider', 'query_type'])
        self.connection_pool_size = Gauge('database_connection_pool_size', ['provider', 'pool_type'])
        self.active_connections = Gauge('database_active_connections', ['provider'])
        self.query_cache_hits = Counter('database_cache_hits_total', ['provider'])
        self.query_cache_misses = Counter('database_cache_misses_total', ['provider'])
        
        # Setup
        asyncio.create_task(self._initialize_connections())
        self._setup_routes()
        self._start_health_monitoring()
        
        # Logger
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    async def _initialize_connections(self):
        """Initialisation des connexions aux bases de données"""
        try:
            # PostgreSQL primary
            if self.config.primary_provider == DatabaseProvider.POSTGRESQL:
                self.connection_pools["primary"] = await self._create_postgresql_pool(
                    self.config.write_primary, "primary"
                )
            
            # MySQL primary
            elif self.config.primary_provider == DatabaseProvider.MYSQL:
                self.connection_pools["primary"] = await self._create_mysql_pool(
                    self.config.write_primary, "primary"
                )
            
            # MongoDB primary
            elif self.config.primary_provider == DatabaseProvider.MONGODB:
                self.connection_pools["primary"] = await self._create_mongodb_connection(
                    self.config.write_primary, "primary"
                )
            
            # Read replicas
            for i, replica_url in enumerate(self.config.read_replicas):
                replica_id = f"replica_{i}"
                
                if self.config.primary_provider == DatabaseProvider.POSTGRESQL:
                    self.read_pools[replica_id] = await self._create_postgresql_pool(replica_url, replica_id)
                elif self.config.primary_provider == DatabaseProvider.MYSQL:
                    self.read_pools[replica_id] = await self._create_mysql_pool(replica_url, replica_id)
                elif self.config.primary_provider == DatabaseProvider.MONGODB:
                    self.read_pools[replica_id] = await self._create_mongodb_connection(replica_url, replica_id)
            
            self.logger.info(f"Database connections initialized: {len(self.connection_pools)} primary, {len(self.read_pools)} replicas")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize database connections: {str(e)}")
            raise

    async def _create_postgresql_pool(self, url: str, pool_id: str):
        """Créer pool de connexions PostgreSQL"""
        try:
            pool = await asyncpg.create_pool(
                url,
                min_size=self.config.pool_size // 2,
                max_size=self.config.pool_size,
                max_queries=50000,
                max_inactive_connection_lifetime=self.config.pool_recycle,
                server_settings={
                    'jit': 'off',
                    'application_name': f'iacherie_db_service_{pool_id}'
                }
            )
            
            # Test connection
            async with pool.acquire() as conn:
                await conn.fetchval('SELECT 1')
            
            self.logger.info(f"PostgreSQL pool created: {pool_id}")
            return pool
            
        except Exception as e:
            self.logger.error(f"Failed to create PostgreSQL pool {pool_id}: {str(e)}")
            raise

    async def _create_mysql_pool(self, url: str, pool_id: str):
        """Créer pool de connexions MySQL"""
        try:
            # Parse URL
            import urllib.parse
            parsed = urllib.parse.urlparse(url)
            
            pool = await aiomysql.create_pool(
                host=parsed.hostname,
                port=parsed.port or 3306,
                user=parsed.username,
                password=parsed.password,
                db=parsed.path.lstrip('/'),
                minsize=self.config.pool_size // 2,
                maxsize=self.config.pool_size,
                autocommit=True,
                charset='utf8mb4'
            )
            
            # Test connection
            async with pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute('SELECT 1')
            
            self.logger.info(f"MySQL pool created: {pool_id}")
            return pool
            
        except Exception as e:
            self.logger.error(f"Failed to create MySQL pool {pool_id}: {str(e)}")
            raise

    async def _create_mongodb_connection(self, url: str, connection_id: str):
        """Créer connexion MongoDB"""
        try:
            client = motor.motor_asyncio.AsyncIOMotorClient(
                url,
                maxPoolSize=self.config.pool_size,
                minPoolSize=self.config.pool_size // 2,
                maxIdleTimeMS=self.config.pool_recycle * 1000,
                serverSelectionTimeoutMS=self.config.pool_timeout * 1000
            )
            
            # Test connection
            await client.admin.command('ismaster')
            
            self.logger.info(f"MongoDB connection created: {connection_id}")
            return client
            
        except Exception as e:
            self.logger.error(f"Failed to create MongoDB connection {connection_id}: {str(e)}")
            raise

    def _start_health_monitoring(self):
        """Démarre le monitoring de santé des connexions"""
        async def health_check_loop():
            while True:
                try:
                    await self._check_all_connections_health()
                    await asyncio.sleep(self.config.health_check_interval)
                except Exception as e:
                    self.logger.error(f"Health check loop error: {str(e)}")
                    await asyncio.sleep(5)
        
        asyncio.create_task(health_check_loop())

    def _setup_routes(self):
        """Configuration des routes du service"""
        
        @self.app.post("/database/query", response_model=QueryResult)
        async def execute_query(query_request: DatabaseQuery, background_tasks: BackgroundTasks):
            """Exécuter une requête de base de données"""
            query_id = query_request.query_id or f"query_{int(time.time())}_{secrets.token_hex(4)}"
            
            with self.query_duration.labels(
                provider=self.config.primary_provider.value,
                query_type=query_request.query_type.value
            ).time():
                
                start_time = time.time()
                
                try:
                    # Validation de sécurité
                    if self.config.enable_query_validation:
                        await self._validate_query_security(query_request.query)
                    
                    # Vérifier cache
                    cached_result = None
                    if query_request.use_cache and query_request.query_type == QueryType.SELECT:
                        cached_result = await self._get_cached_result(query_request)
                        if cached_result:
                            self.query_cache_hits.labels(provider=self.config.primary_provider.value).inc()
                            execution_time = (time.time() - start_time) * 1000
                            
                            return QueryResult(
                                query_id=query_id,
                                success=True,
                                data=cached_result["data"],
                                execution_time_ms=execution_time,
                                from_cache=True,
                                metadata={"cache_hit": True}
                            )
                        else:
                            self.query_cache_misses.labels(provider=self.config.primary_provider.value).inc()
                    
                    # Sélectionner pool de connexions
                    pool = await self._select_connection_pool(query_request)
                    
                    # Exécuter requête
                    result = await self._execute_query_on_pool(pool, query_request)
                    
                    execution_time = (time.time() - start_time) * 1000
                    
                    # Cache le résultat si applicable
                    if (query_request.use_cache and 
                        query_request.query_type == QueryType.SELECT and 
                        len(result["data"]) > 0):
                        background_tasks.add_task(self._cache_query_result, query_request, result)
                    
                    # Métriques
                    self.query_count.labels(
                        provider=self.config.primary_provider.value,
                        query_type=query_request.query_type.value,
                        status="success"
                    ).inc()
                    
                    # Log slow queries
                    if execution_time > self.config.slow_query_threshold_ms:
                        self.logger.warning(f"Slow query detected: {execution_time:.2f}ms - {query_request.query[:100]}")
                    
                    return QueryResult(
                        query_id=query_id,
                        success=True,
                        data=result["data"],
                        affected_rows=result.get("affected_rows", 0),
                        execution_time_ms=execution_time,
                        from_cache=False,
                        metadata={"pool_used": result.get("pool_id")}
                    )
                    
                except Exception as e:
                    execution_time = (time.time() - start_time) * 1000
                    
                    self.query_count.labels(
                        provider=self.config.primary_provider.value,
                        query_type=query_request.query_type.value,
                        status="error"
                    ).inc()
                    
                    self.logger.error(f"Query execution failed: {str(e)} - Query: {query_request.query[:100]}")
                    
                    return QueryResult(
                        query_id=query_id,
                        success=False,
                        execution_time_ms=execution_time,
                        metadata={"error": str(e)}
                    )

        @self.app.post("/database/transaction")
        async def execute_transaction(queries: List[DatabaseQuery]):
            """Exécuter une transaction avec plusieurs requêtes"""
            transaction_id = f"txn_{int(time.time())}_{secrets.token_hex(4)}"
            
            try:
                # Toutes les requêtes en transaction doivent utiliser le primary
                pool = self.connection_pools["primary"]
                
                if self.config.primary_provider == DatabaseProvider.POSTGRESQL:
                    result = await self._execute_postgresql_transaction(pool, queries)
                elif self.config.primary_provider == DatabaseProvider.MYSQL:
                    result = await self._execute_mysql_transaction(pool, queries)
                else:
                    raise HTTPException(status_code=400, detail="Transactions not supported for this provider")
                
                return {
                    "transaction_id": transaction_id,
                    "success": True,
                    "results": result
                }
                
            except Exception as e:
                self.logger.error(f"Transaction failed: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Transaction failed: {str(e)}")

        @self.app.get("/database/health")
        async def get_database_health():
            """Statut de santé des connexions de base de données"""
            try:
                health_status = {}
                
                for connection_id, health in self.connection_health.items():
                    health_status[connection_id] = {
                        "status": health.status.value,
                        "response_time_ms": health.response_time_ms,
                        "active_connections": health.active_connections,
                        "idle_connections": health.idle_connections,
                        "last_check": health.last_check.isoformat(),
                        "error_count": health.error_count
                    }
                
                overall_status = "healthy"
                if any(h.status == ConnectionStatus.UNHEALTHY for h in self.connection_health.values()):
                    overall_status = "unhealthy"
                elif any(h.status == ConnectionStatus.DEGRADED for h in self.connection_health.values()):
                    overall_status = "degraded"
                
                return {
                    "overall_status": overall_status,
                    "connections": health_status,
                    "metrics": {
                        "total_pools": len(self.connection_pools) + len(self.read_pools),
                        "primary_pools": len(self.connection_pools),
                        "replica_pools": len(self.read_pools)
                    }
                }
                
            except Exception as e:
                self.logger.error(f"Health check failed: {str(e)}")
                return {
                    "overall_status": "unhealthy",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }

        @self.app.get("/database/metrics")
        async def get_database_metrics():
            """Métriques de performance de la base de données"""
            try:
                metrics = {
                    "connection_pools": {},
                    "query_stats": await self._get_query_statistics(),
                    "cache_stats": await self._get_cache_statistics(),
                    "performance": await self._get_performance_metrics()
                }
                
                # Métriques des pools
                for pool_id, pool in {**self.connection_pools, **self.read_pools}.items():
                    if hasattr(pool, 'get_stats'):
                        pool_stats = pool.get_stats()
                        metrics["connection_pools"][pool_id] = pool_stats
                
                return metrics
                
            except Exception as e:
                self.logger.error(f"Metrics collection failed: {str(e)}")
                raise HTTPException(status_code=500, detail="Failed to collect metrics")

        @self.app.post("/database/cache/invalidate")
        async def invalidate_cache(pattern: str = "*"):
            """Invalider le cache de requêtes"""
            try:
                if pattern == "*":
                    # Vider tout le cache
                    keys = await self.redis.keys("query_cache:*")
                    if keys:
                        await self.redis.delete(*keys)
                    self.query_cache.clear()
                    invalidated = len(keys)
                else:
                    # Invalider pattern spécifique
                    keys = await self.redis.keys(f"query_cache:*{pattern}*")
                    if keys:
                        await self.redis.delete(*keys)
                    invalidated = len(keys)
                
                return {
                    "message": "Cache invalidated successfully",
                    "invalidated_keys": invalidated
                }
                
            except Exception as e:
                self.logger.error(f"Cache invalidation failed: {str(e)}")
                raise HTTPException(status_code=500, detail="Cache invalidation failed")

    async def _select_connection_pool(self, query_request: DatabaseQuery):
        """Sélectionner le pool de connexions approprié"""
        # Pour les écritures, utiliser toujours le primary
        if query_request.query_type in [QueryType.INSERT, QueryType.UPDATE, QueryType.DELETE, QueryType.TRANSACTION]:
            return self.connection_pools["primary"]
        
        # Pour les lectures avec read/write splitting activé
        if self.config.enable_read_write_split and query_request.read_preference != "primary":
            if self.read_pools:
                # Sélection round-robin des replicas
                pool_ids = list(self.read_pools.keys())
                selected_pool_id = pool_ids[hash(query_request.query_id or query_request.query) % len(pool_ids)]
                
                # Vérifier santé du replica
                if (selected_pool_id in self.connection_health and 
                    self.connection_health[selected_pool_id].status == ConnectionStatus.HEALTHY):
                    return self.read_pools[selected_pool_id]
        
        # Fallback sur primary
        return self.connection_pools["primary"]

    async def _execute_query_on_pool(self, pool, query_request: DatabaseQuery) -> Dict[str, Any]:
        """Exécuter requête sur un pool spécifique"""
        if self.config.primary_provider == DatabaseProvider.POSTGRESQL:
            return await self._execute_postgresql_query(pool, query_request)
        elif self.config.primary_provider == DatabaseProvider.MYSQL:
            return await self._execute_mysql_query(pool, query_request)
        elif self.config.primary_provider == DatabaseProvider.MONGODB:
            return await self._execute_mongodb_query(pool, query_request)
        else:
            raise ValueError(f"Unsupported provider: {self.config.primary_provider}")

    async def _execute_postgresql_query(self, pool, query_request: DatabaseQuery) -> Dict[str, Any]:
        """Exécuter requête PostgreSQL"""
        async with pool.acquire() as conn:
            try:
                if query_request.query_type == QueryType.SELECT:
                    if query_request.parameters:
                        rows = await conn.fetch(query_request.query, *query_request.parameters.values())
                    else:
                        rows = await conn.fetch(query_request.query)
                    
                    return {
                        "data": [dict(row) for row in rows],
                        "affected_rows": len(rows)
                    }
                
                else:
                    if query_request.parameters:
                        result = await conn.execute(query_request.query, *query_request.parameters.values())
                    else:
                        result = await conn.execute(query_request.query)
                    
                    # Extraire nombre de lignes affectées
                    affected_rows = 0
                    if isinstance(result, str) and result.startswith(('INSERT', 'UPDATE', 'DELETE')):
                        parts = result.split()
                        if len(parts) >= 3:
                            try:
                                affected_rows = int(parts[-1])
                            except ValueError:
                                pass
                    
                    return {
                        "data": [],
                        "affected_rows": affected_rows
                    }
                    
            except Exception as e:
                self.logger.error(f"PostgreSQL query execution failed: {str(e)}")
                raise

    async def _execute_mysql_query(self, pool, query_request: DatabaseQuery) -> Dict[str, Any]:
        """Exécuter requête MySQL"""
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                try:
                    if query_request.parameters:
                        await cursor.execute(query_request.query, query_request.parameters)
                    else:
                        await cursor.execute(query_request.query)
                    
                    if query_request.query_type == QueryType.SELECT:
                        rows = await cursor.fetchall()
                        return {
                            "data": list(rows),
                            "affected_rows": len(rows)
                        }
                    else:
                        return {
                            "data": [],
                            "affected_rows": cursor.rowcount
                        }
                        
                except Exception as e:
                    self.logger.error(f"MySQL query execution failed: {str(e)}")
                    raise

    async def _execute_mongodb_query(self, client, query_request: DatabaseQuery) -> Dict[str, Any]:
        """Exécuter requête MongoDB"""
        try:
            # MongoDB queries should be in JSON format
            query_data = json.loads(query_request.query)
            
            db_name = query_data.get("database", "iacherie")
            collection_name = query_data.get("collection")
            operation = query_data.get("operation", "find")
            
            if not collection_name:
                raise ValueError("Collection name required for MongoDB queries")
            
            db = client[db_name]
            collection = db[collection_name]
            
            if operation == "find":
                filter_query = query_data.get("filter", {})
                projection = query_data.get("projection")
                limit = query_data.get("limit", 0)
                
                cursor = collection.find(filter_query, projection)
                if limit:
                    cursor = cursor.limit(limit)
                
                results = await cursor.to_list(length=None)
                
                # Convertir ObjectId en string
                for result in results:
                    if "_id" in result:
                        result["_id"] = str(result["_id"])
                
                return {
                    "data": results,
                    "affected_rows": len(results)
                }
            
            elif operation == "insertOne":
                document = query_data.get("document", {})
                result = await collection.insert_one(document)
                
                return {
                    "data": [{"inserted_id": str(result.inserted_id)}],
                    "affected_rows": 1
                }
            
            elif operation == "updateMany":
                filter_query = query_data.get("filter", {})
                update_query = query_data.get("update", {})
                result = await collection.update_many(filter_query, update_query)
                
                return {
                    "data": [{"matched_count": result.matched_count, "modified_count": result.modified_count}],
                    "affected_rows": result.modified_count
                }
            
            else:
                raise ValueError(f"Unsupported MongoDB operation: {operation}")
                
        except Exception as e:
            self.logger.error(f"MongoDB query execution failed: {str(e)}")
            raise

    async def _validate_query_security(self, query: str):
        """Validation de sécurité des requêtes"""
        # Patterns dangereux
        dangerous_patterns = [
            r"DROP\s+TABLE",
            r"DROP\s+DATABASE",
            r"TRUNCATE\s+TABLE",
            r"DELETE\s+FROM\s+\w+\s*;?\s*$",  # DELETE sans WHERE
            r"--",  # Commentaires SQL
            r"/\*.*\*/",  # Commentaires multi-lignes
            r"EXEC\s*\(",
            r"EXECUTE\s*\(",
            r"xp_cmdshell",
            r"sp_executesql"
        ]
        
        import re
        query_upper = query.upper()
        
        for pattern in dangerous_patterns:
            if re.search(pattern, query_upper, re.IGNORECASE):
                raise HTTPException(
                    status_code=400, 
                    detail=f"Query contains potentially dangerous pattern: {pattern}"
                )

    async def _get_cached_result(self, query_request: DatabaseQuery) -> Optional[Dict]:
        """Récupérer résultat depuis le cache"""
        try:
            cache_key = self._generate_cache_key(query_request)
            
            # Vérifier cache Redis
            cached_data = await self.redis.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
            
            # Vérifier cache mémoire
            return self.query_cache.get(cache_key)
            
        except Exception as e:
            self.logger.error(f"Cache retrieval failed: {str(e)}")
            return None

    async def _cache_query_result(self, query_request: DatabaseQuery, result: Dict):
        """Mettre en cache le résultat d'une requête"""
        try:
            cache_key = self._generate_cache_key(query_request)
            cache_data = {
                "data": result["data"],
                "cached_at": datetime.utcnow().isoformat()
            }
            
            # Cache Redis avec TTL
            await self.redis.setex(
                cache_key,
                self.config.cache_ttl_seconds,
                json.dumps(cache_data, default=str)
            )
            
            # Cache mémoire limité
            if len(self.query_cache) < 1000:  # Limite de 1000 entrées
                self.query_cache[cache_key] = cache_data
            
        except Exception as e:
            self.logger.error(f"Cache storage failed: {str(e)}")

    def _generate_cache_key(self, query_request: DatabaseQuery) -> str:
        """Générer clé de cache pour une requête"""
        cache_content = f"{query_request.query}:{json.dumps(query_request.parameters, sort_keys=True)}"
        cache_hash = hashlib.md5(cache_content.encode()).hexdigest()
        return f"query_cache:{cache_hash}"

    async def _check_all_connections_health(self):
        """Vérifier santé de toutes les connexions"""
        all_pools = {**self.connection_pools, **self.read_pools}
        
        for pool_id, pool in all_pools.items():
            try:
                start_time = time.time()
                
                if self.config.primary_provider == DatabaseProvider.POSTGRESQL:
                    await self._check_postgresql_health(pool)
                elif self.config.primary_provider == DatabaseProvider.MYSQL:
                    await self._check_mysql_health(pool)
                elif self.config.primary_provider == DatabaseProvider.MONGODB:
                    await self._check_mongodb_health(pool)
                
                response_time = (time.time() - start_time) * 1000
                
                # Mettre à jour santé
                self.connection_health[pool_id] = ConnectionHealth(
                    provider=self.config.primary_provider,
                    connection_id=pool_id,
                    status=ConnectionStatus.HEALTHY,
                    response_time_ms=response_time,
                    active_connections=getattr(pool, '_holders', []),
                    idle_connections=getattr(pool, '_queue', []),
                    last_check=datetime.utcnow(),
                    error_count=0
                )
                
            except Exception as e:
                # Mettre à jour avec erreur
                previous_health = self.connection_health.get(pool_id)
                error_count = (previous_health.error_count + 1) if previous_health else 1
                
                self.connection_health[pool_id] = ConnectionHealth(
                    provider=self.config.primary_provider,
                    connection_id=pool_id,
                    status=ConnectionStatus.UNHEALTHY if error_count >= 3 else ConnectionStatus.DEGRADED,
                    response_time_ms=0,
                    active_connections=0,
                    idle_connections=0,
                    last_check=datetime.utcnow(),
                    error_count=error_count
                )
                
                self.logger.error(f"Health check failed for {pool_id}: {str(e)}")

    async def _check_postgresql_health(self, pool):
        """Vérifier santé PostgreSQL"""
        async with pool.acquire() as conn:
            await conn.fetchval('SELECT 1')

    async def _check_mysql_health(self, pool):
        """Vérifier santé MySQL"""
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute('SELECT 1')

    async def _check_mongodb_health(self, client):
        """Vérifier santé MongoDB"""
        await client.admin.command('ismaster')

    def get_app(self) -> FastAPI:
        """Retourne instance FastAPI"""
        return self.app


def create_database_service(config: DatabaseConfig = None) -> FastAPI:
    """
    Factory pour créer service de base de données
    
    Args:
        config: Configuration personnalisée
        
    Returns:
        FastAPI: Instance du service configuré
    """
    db_service = DatabaseServiceTemplate(config)
    return db_service.get_app()


if __name__ == "__main__":
    import uvicorn
    
    config = DatabaseConfig(
        primary_provider=DatabaseProvider.POSTGRESQL,
        pool_size=20,
        enable_read_write_split=True,
        enable_query_cache=True
    )
    
    app = create_database_service(config)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )