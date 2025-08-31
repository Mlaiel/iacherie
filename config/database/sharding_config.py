"""
Database Sharding Configuration Module for IA-Influencer Agent Platform
======================================================================

Professional database sharding configuration for horizontal scaling,
multi-tenant data distribution, and performance optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel. 
Any unauthorized use, reproduction, or distribution of this code 
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""

import os
import logging
import hashlib
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import asyncio
from datetime import datetime
import json
import asyncpg
from sqlalchemy import create_engine
import redis.asyncio as redis

logger = logging.getLogger(__name__)


class ShardingStrategy(Enum):
    """Database sharding strategies"""
    HASH_BASED = "hash_based"
    RANGE_BASED = "range_based"
    DIRECTORY_BASED = "directory_based"
    GEOGRAPHIC = "geographic"
    TENANT_BASED = "tenant_based"
    CONTENT_TYPE_BASED = "content_type_based"


class ShardingKey(Enum):
    """Keys used for sharding decisions"""
    USER_ID = "user_id"
    TENANT_ID = "tenant_id"
    CONTENT_ID = "content_id"
    TIMESTAMP = "timestamp"
    GEOGRAPHIC_REGION = "geographic_region"
    CONTENT_TYPE = "content_type"


class DataType(Enum):
    """Data types for different sharding strategies"""
    USER_DATA = "user_data"
    CONTENT_DATA = "content_data"
    ANALYTICS_DATA = "analytics_data"
    PROTECTION_DATA = "protection_data"
    REVENUE_DATA = "revenue_data"
    COLLABORATION_DATA = "collaboration_data"


@dataclass
class ShardConfig:
    """Configuration for individual shard"""
    shard_id: str
    shard_name: str
    database_url: str
    weight: float = 1.0  # Load balancing weight
    is_active: bool = True
    is_read_only: bool = False
    max_connections: int = 100
    preferred_data_types: List[DataType] = field(default_factory=list)
    geographic_region: Optional[str] = None
    
    # Range-based sharding
    range_start: Optional[Any] = None
    range_end: Optional[Any] = None
    
    # Custom sharding criteria
    tenant_ids: List[str] = field(default_factory=list)
    content_types: List[str] = field(default_factory=list)


@dataclass
class ShardingRule:
    """Rules for data distribution across shards"""
    rule_id: str
    data_type: DataType
    sharding_strategy: ShardingStrategy
    sharding_key: ShardingKey
    target_shards: List[str] = field(default_factory=list)
    conditions: Dict[str, Any] = field(default_factory=dict)
    priority: int = 0  # Higher priority rules are evaluated first


@dataclass
class DatabaseShardingConfig:
    """Professional database sharding configuration"""
    # Global sharding settings
    sharding_enabled: bool = True
    default_strategy: ShardingStrategy = ShardingStrategy.HASH_BASED
    default_sharding_key: ShardingKey = ShardingKey.USER_ID
    
    # Shard definitions
    shards: Dict[str, ShardConfig] = field(default_factory=dict)
    
    # Sharding rules for different data types
    sharding_rules: List[ShardingRule] = field(default_factory=list)
    
    # Connection pooling
    connection_pool_size: int = 20
    connection_timeout: int = 30
    query_timeout: int = 60
    
    # Rebalancing and migration
    auto_rebalancing_enabled: bool = True
    rebalancing_threshold: float = 0.8  # Trigger rebalancing at 80% capacity
    migration_batch_size: int = 1000
    
    # Monitoring and health checks
    health_check_interval: int = 60  # seconds
    performance_monitoring: bool = True
    slow_query_threshold_ms: int = 1000
    
    # Cross-shard operations
    enable_cross_shard_queries: bool = True
    cross_shard_timeout: int = 120
    
    # Backup and recovery
    shard_backup_enabled: bool = True
    backup_schedule: str = "0 2 * * *"  # Daily at 2 AM


class ShardingManager:
    """Professional database sharding management system"""
    
    def __init__(self, config: DatabaseShardingConfig):
        self.config = config
        self.shard_connections: Dict[str, Any] = {}
        self.shard_health: Dict[str, bool] = {}
        self.routing_cache = {}
        self.performance_stats: Dict[str, Dict] = {}
        
    async def initialize(self) -> bool:
        """Initialize sharding manager and connections"""



        try:
            # Initialize connections to all shards
            for shard_id, shard_config in self.config.shards.items():
                if await self._initialize_shard_connection(shard_id, shard_config):
                    self.shard_health[shard_id] = True
                    logger.info(f"Shard {shard_id} initialized successfully")
                else:
                    self.shard_health[shard_id] = False
                    logger.error(f"Failed to initialize shard {shard_id}")
                    
            # Start health monitoring
            if self.config.performance_monitoring:
                asyncio.create_task(self._monitor_shard_health())
                
            logger.info("Sharding manager initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize sharding manager: {e}")
            return False
            
    async def _initialize_shard_connection(
        self,
        shard_id: str,
        shard_config: ShardConfig
    ) -> bool:
        """Initialize connection to specific shard"""



        try:
            # Create connection pool for PostgreSQL shards
            if "postgresql" in shard_config.database_url:
                pool = await asyncpg.create_pool(
                    shard_config.database_url,
                    max_size=shard_config.max_connections,
                    command_timeout=self.config.connection_timeout
                )
                self.shard_connections[shard_id] = pool
                
                # Test connection
                async with pool.acquire() as conn:
                    await conn.fetchval("SELECT 1")
                    
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize shard {shard_id}: {e}")
            return False
            
    def get_shard_for_key(
        self,
        sharding_key: str,
        data_type: DataType,
        key_value: Any
    ) -> Optional[str]:
        """Determine which shard should handle the data"""



        try:
            # Check cache first
            cache_key = f"{data_type.value}:{sharding_key}:{key_value}"
            if cache_key in self.routing_cache:
                return self.routing_cache[cache_key]
                
            # Find applicable sharding rule
            applicable_rule = None
            for rule in sorted(self.config.sharding_rules, key=lambda r: r.priority, reverse=True):
                if rule.data_type == data_type:
                    applicable_rule = rule
                    break
                    
            if not applicable_rule:
                # Use default strategy
                shard_id = self._apply_default_sharding(key_value)
            else:
                shard_id = self._apply_sharding_rule(applicable_rule, key_value)
                
            # Cache the result
            self.routing_cache[cache_key] = shard_id
            
            return shard_id
            
        except Exception as e:
            logger.error(f"Error determining shard for key {sharding_key}={key_value}: {e}")
            return None
            
    def _apply_default_sharding(self, key_value: Any) -> str:
        """Apply default hash-based sharding"""
        # Get active shards
        active_shards = [
            shard_id for shard_id, config in self.config.shards.items()
            if config.is_active
        ]
        
        if not active_shards:
            raise RuntimeError("No active shards available")
            
        # Hash-based distribution
        hash_value = hashlib.md5(str(key_value).encode()).hexdigest()
        shard_index = int(hash_value, 16) % len(active_shards)
        
        return active_shards[shard_index]
        
    def _apply_sharding_rule(self, rule: ShardingRule, key_value: Any) -> str:
        """Apply specific sharding rule"""
        if rule.sharding_strategy == ShardingStrategy.HASH_BASED:
            return self._hash_based_sharding(rule.target_shards, key_value)
        elif rule.sharding_strategy == ShardingStrategy.RANGE_BASED:
            return self._range_based_sharding(rule.target_shards, key_value)
        elif rule.sharding_strategy == ShardingStrategy.TENANT_BASED:
            return self._tenant_based_sharding(rule.target_shards, key_value)
        else:
            # Fallback to default
            return self._apply_default_sharding(key_value)
            
    def _hash_based_sharding(self, target_shards: List[str], key_value: Any) -> str:
        """Hash-based sharding across target shards"""
        active_targets = [
            shard_id for shard_id in target_shards
            if shard_id in self.config.shards and self.config.shards[shard_id].is_active
        ]
        
        hash_value = hashlib.md5(str(key_value).encode()).hexdigest()
        shard_index = int(hash_value, 16) % len(active_targets)
        
        return active_targets[shard_index]
        
    def _range_based_sharding(self, target_shards: List[str], key_value: Any) -> str:
        """Range-based sharding"""
        for shard_id in target_shards:
            shard_config = self.config.shards.get(shard_id)
            if (shard_config and shard_config.is_active and
                shard_config.range_start is not None and
                shard_config.range_end is not None):
                
                if shard_config.range_start <= key_value < shard_config.range_end:
                    return shard_id
                    
        # Fallback to first active shard
        for shard_id in target_shards:
            if (shard_id in self.config.shards and 
                self.config.shards[shard_id].is_active):
                return shard_id
                
        raise RuntimeError("No suitable shard found for range-based sharding")
        
    def _tenant_based_sharding(self, target_shards: List[str], key_value: Any) -> str:
        """Tenant-based sharding"""
        # Find shard that handles this tenant
        for shard_id in target_shards:
            shard_config = self.config.shards.get(shard_id)
            if (shard_config and shard_config.is_active and
                str(key_value) in shard_config.tenant_ids):
                return shard_id
                
        # Fallback to hash-based for new tenants
        return self._hash_based_sharding(target_shards, key_value)
        
    async def execute_query(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None,
        sharding_key: Optional[str] = None,
        data_type: DataType = DataType.USER_DATA,
        key_value: Optional[Any] = None
    ) -> List[Dict[str, Any]]:
        """Execute query on appropriate shard"""



        try:
            # Determine target shard
            if sharding_key and key_value is not None:
                shard_id = self.get_shard_for_key(sharding_key, data_type, key_value)
            else:
                # Use first active shard for non-sharded queries
                shard_id = next(
                    (sid for sid, config in self.config.shards.items() if config.is_active),
                    None
                )
                
            if not shard_id:
                raise RuntimeError("No active shard available for query")
                
            # Execute query
            start_time = datetime.now()
            result = await self._execute_on_shard(shard_id, query, params or {})
            
            # Record performance metrics
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            self._record_query_performance(shard_id, execution_time)
            
            return result
            
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            return []
            
    async def _execute_on_shard(
        self,
        shard_id: str,
        query: str,
        params: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Execute query on specific shard"""
        if shard_id not in self.shard_connections:
            raise RuntimeError(f"No connection to shard {shard_id}")
            
        pool = self.shard_connections[shard_id]
        
        async with pool.acquire() as conn:
            # Replace named parameters with positional ones for asyncpg
            query_parts = query.split()
            param_values = []
            
            for i, (key, value) in enumerate(params.items(), 1):
                query = query.replace(f":{key}", f"${i}")
                param_values.append(value)
                
            # Execute query
            if query.strip().upper().startswith("SELECT"):
                rows = await conn.fetch(query, *param_values)
                return [dict(row) for row in rows]
            else:
                await conn.execute(query, *param_values)
                return []
                
    async def execute_cross_shard_query(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None,
        target_shards: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Execute query across multiple shards and merge results"""
        if not self.config.enable_cross_shard_queries:
            raise RuntimeError("Cross-shard queries are disabled")
            
        try:
            # Determine target shards
            if target_shards is None:
                target_shards = [
                    shard_id for shard_id, config in self.config.shards.items()
                    if config.is_active and not config.is_read_only
                ]
                
            # Execute query on all target shards
            tasks = []
            for shard_id in target_shards:
                if shard_id in self.shard_connections:
                    task = self._execute_on_shard(shard_id, query, params or {})
                    tasks.append(task)
                    
            # Wait for all queries to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Merge results
            merged_results = []
            for result in results:
                if isinstance(result, Exception):
                    logger.warning(f"Cross-shard query failed on one shard: {result}")
                    continue
                    
                if isinstance(result, list):
                    merged_results.extend(result)
                    
            return merged_results
            
        except Exception as e:
            logger.error(f"Cross-shard query execution failed: {e}")
            return []
            
    def _record_query_performance(self, shard_id: str, execution_time_ms: float):
        """Record query performance metrics"""
        if shard_id not in self.performance_stats:
            self.performance_stats[shard_id] = {
                "query_count": 0,
                "total_time_ms": 0,
                "avg_time_ms": 0,
                "slow_queries": 0
            }
            
        stats = self.performance_stats[shard_id]
        stats["query_count"] += 1
        stats["total_time_ms"] += execution_time_ms
        stats["avg_time_ms"] = stats["total_time_ms"] / stats["query_count"]
        
        if execution_time_ms > self.config.slow_query_threshold_ms:
            stats["slow_queries"] += 1
            
    async def _monitor_shard_health(self):
        """Monitor health of all shards"""
        while True:
            try:
                for shard_id, pool in self.shard_connections.items():
                    try:
                        async with pool.acquire() as conn:
                            await conn.fetchval("SELECT 1")
                            self.shard_health[shard_id] = True
                    except Exception as e:
                        logger.warning(f"Health check failed for shard {shard_id}: {e}")
                        self.shard_health[shard_id] = False
                        
                await asyncio.sleep(self.config.health_check_interval)
                
            except Exception as e:
                logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(self.config.health_check_interval)
                
    async def get_sharding_statistics(self) -> Dict[str, Any]:
        """Get comprehensive sharding statistics"""



        try:
            total_shards = len(self.config.shards)
            active_shards = sum(1 for config in self.config.shards.values() if config.is_active)
            healthy_shards = sum(1 for health in self.shard_health.values() if health)
            
            # Calculate load distribution
            total_queries = sum(
                stats.get("query_count", 0) 
                for stats in self.performance_stats.values()
            )
            
            shard_load_distribution = {}
            for shard_id, stats in self.performance_stats.items():
                query_count = stats.get("query_count", 0)
                load_percentage = (query_count / total_queries * 100) if total_queries > 0 else 0
                shard_load_distribution[shard_id] = {
                    "query_count": query_count,
                    "load_percentage": round(load_percentage, 2),
                    "avg_response_time_ms": round(stats.get("avg_time_ms", 0), 2),
                    "slow_queries": stats.get("slow_queries", 0)
                }
                
            return {
                "total_shards": total_shards,
                "active_shards": active_shards,
                "healthy_shards": healthy_shards,
                "health_ratio": healthy_shards / total_shards if total_shards > 0 else 0,
                "total_queries_executed": total_queries,
                "load_distribution": shard_load_distribution,
                "routing_cache_size": len(self.routing_cache),
                "cross_shard_queries_enabled": self.config.enable_cross_shard_queries
            }
            
        except Exception as e:
            logger.error(f"Error getting sharding statistics: {e}")
            return {"error": str(e)}
            
    async def close(self):
        """Close all shard connections"""



        try:
            for shard_id, pool in self.shard_connections.items():
                if hasattr(pool, 'close'):
                    await pool.close()
                    logger.info(f"Closed connection to shard {shard_id}")
                    
            self.shard_connections.clear()
            self.shard_health.clear()
            
        except Exception as e:
            logger.error(f"Error closing shard connections: {e}")


def create_sharding_config(
    environment: str = "development",
    custom_settings: Optional[Dict[str, Any]] = None
) -> DatabaseShardingConfig:
    """Factory function to create sharding configuration"""
    
    # Environment-specific shard configurations
    if environment == "development":
        shards = {
            "shard_01": ShardConfig(
                shard_id="shard_01",
                shard_name="Development Primary",
                database_url=os.getenv("DEV_DB_SHARD_01", "postgresql://user:pass@localhost:5432/shard_01"),
                weight=1.0,
                preferred_data_types=[DataType.USER_DATA, DataType.CONTENT_DATA]
            )
        }
    elif environment == "staging":
        shards = {
            "shard_01": ShardConfig(
                shard_id="shard_01",
                shard_name="Staging Users",
                database_url=os.getenv("STAGING_DB_SHARD_01", "postgresql://user:pass@staging-db-01:5432/shard_01"),
                weight=1.0,
                preferred_data_types=[DataType.USER_DATA, DataType.COLLABORATION_DATA]
            ),
            "shard_02": ShardConfig(
                shard_id="shard_02",
                shard_name="Staging Content",
                database_url=os.getenv("STAGING_DB_SHARD_02", "postgresql://user:pass@staging-db-02:5432/shard_02"),
                weight=1.0,
                preferred_data_types=[DataType.CONTENT_DATA, DataType.PROTECTION_DATA]
            )
        }
    else:  # production
        shards = {
            "shard_01": ShardConfig(
                shard_id="shard_01",
                shard_name="Production Users Primary",
                database_url=os.getenv("PROD_DB_SHARD_01", "postgresql://user:pass@prod-db-01:5432/shard_01"),
                weight=1.0,
                preferred_data_types=[DataType.USER_DATA],
                geographic_region="us-east-1"
            ),
            "shard_02": ShardConfig(
                shard_id="shard_02",
                shard_name="Production Content Primary",
                database_url=os.getenv("PROD_DB_SHARD_02", "postgresql://user:pass@prod-db-02:5432/shard_02"),
                weight=1.0,
                preferred_data_types=[DataType.CONTENT_DATA, DataType.PROTECTION_DATA],
                geographic_region="us-east-1"
            ),
            "shard_03": ShardConfig(
                shard_id="shard_03",
                shard_name="Production Analytics",
                database_url=os.getenv("PROD_DB_SHARD_03", "postgresql://user:pass@prod-db-03:5432/shard_03"),
                weight=0.8,
                preferred_data_types=[DataType.ANALYTICS_DATA, DataType.REVENUE_DATA],
                geographic_region="us-west-2"
            )
        }
    
    # Default sharding rules
    sharding_rules = [
        ShardingRule(
            rule_id="user_data_by_user_id",
            data_type=DataType.USER_DATA,
            sharding_strategy=ShardingStrategy.HASH_BASED,
            sharding_key=ShardingKey.USER_ID,
            priority=10
        ),
        ShardingRule(
            rule_id="content_data_by_content_id",
            data_type=DataType.CONTENT_DATA,
            sharding_strategy=ShardingStrategy.HASH_BASED,
            sharding_key=ShardingKey.CONTENT_ID,
            priority=10
        ),
        ShardingRule(
            rule_id="analytics_by_timestamp",
            data_type=DataType.ANALYTICS_DATA,
            sharding_strategy=ShardingStrategy.RANGE_BASED,
            sharding_key=ShardingKey.TIMESTAMP,
            priority=5
        )
    ]
    
    config = DatabaseShardingConfig(
        shards=shards,
        sharding_rules=sharding_rules
    )
    
    # Apply custom settings
    if custom_settings:
        for key, value in custom_settings.items():
            if hasattr(config, key):
                setattr(config, key, value)
    
    return config
