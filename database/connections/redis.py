"""
Redis Connection Handler - IA Influencer Agent Platform

Manages Redis connections for caching, sessions, and real-time operations:
- User sessions and authentication tokens
- Content processing queues and caching
- Real-time fingerprinting results
- Platform API rate limiting
- Collaboration matching cache
- Revenue calculation cache

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, Union, Set
from dataclasses import dataclass
from datetime import datetime, timedelta
import json

import redis.asyncio as redis
from redis.asyncio import Redis, ConnectionPool
from redis.asyncio.sentinel import Sentinel


@dataclass
class RedisConfig:
    """Redis connection configuration"""
    host: str = "localhost"
    port: int = 6379
    database: int = 0
    password: Optional[str] = None
    ssl: bool = False
    pool_max_connections: int = 50
    socket_timeout: int = 30
    socket_connect_timeout: int = 10
    retry_on_timeout: bool = True
    health_check_interval: int = 30
    # Sentinel configuration for high availability
    sentinel_hosts: Optional[List[Dict[str, Any]]] = None
    sentinel_service_name: Optional[str] = None
    # Tenant isolation
    tenant_database_offset: int = 1  # Tenants use DB 1, 2, 3, etc.


class RedisConnectionHandler:
    """
    Redis connection handler for IA Influencer platform.
    
    Manages Redis for:
    - Session management and authentication
    - Content fingerprinting cache
    - Real-time protection alerts
    - API rate limiting and throttling
    - Queue management for AI processing
    - Revenue tracking cache
    - Collaboration matching cache
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = RedisConfig(**config)
        self.logger = logging.getLogger(__name__)
        
        self.redis_client: Optional[Redis] = None
        self.connection_pool: Optional[ConnectionPool] = None
        self.sentinel: Optional[Sentinel] = None
        
        # Tenant connections
        self.tenant_clients: Dict[str, Redis] = {}
        
        # Connection metrics
        self.connection_count = 0
        self.command_count = 0
        self.error_count = 0
        self.last_health_check = None
    
    async def initialize(self) -> None:
        """Initialize Redis connection"""
        try:
            self.logger.info("Initializing Redis connection...")
            
            if self.config.sentinel_hosts:
                await self._initialize_sentinel()
            else:
                await self._initialize_direct()
            
            # Verify connection
            await self.health_check()
            
            self.logger.info("Redis connection initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Redis connection: {e}")
            raise
    
    async def _initialize_direct(self) -> None:
        """Initialize direct Redis connection"""
        self.connection_pool = ConnectionPool(
            host=self.config.host,
            port=self.config.port,
            db=self.config.database,
            password=self.config.password,
            ssl=self.config.ssl,
            max_connections=self.config.pool_max_connections,
            socket_timeout=self.config.socket_timeout,
            socket_connect_timeout=self.config.socket_connect_timeout,
            retry_on_timeout=self.config.retry_on_timeout,
            health_check_interval=self.config.health_check_interval
        )
        
        self.redis_client = Redis(connection_pool=self.connection_pool)
    
    async def _initialize_sentinel(self) -> None:
        """Initialize Redis Sentinel for high availability"""
        if not self.config.sentinel_hosts or not self.config.sentinel_service_name:
            raise ValueError("Sentinel configuration incomplete")
        
        sentinel_list = [(host['host'], host['port']) for host in self.config.sentinel_hosts]
        
        self.sentinel = Sentinel(
            sentinel_list,
            socket_timeout=self.config.socket_timeout,
            password=self.config.password
        )
        
        self.redis_client = self.sentinel.master_for(
            self.config.sentinel_service_name,
            socket_timeout=self.config.socket_timeout,
            password=self.config.password,
            db=self.config.database
        )
    
    async def get_connection(self) -> Redis:
        """Get Redis connection"""
        if not self.redis_client:
            raise RuntimeError("Redis client not initialized")
        
        self.connection_count += 1
        return self.redis_client
    
    async def get_tenant_connection(self, tenant_id: str) -> Redis:
        """Get tenant-specific Redis connection"""
        if tenant_id not in self.tenant_clients:
            await self._create_tenant_client(tenant_id)
        
        return self.tenant_clients[tenant_id]
    
    async def _create_tenant_client(self, tenant_id: str) -> None:
        """Create Redis client for specific tenant"""
        # Calculate tenant database number
        tenant_db = self.config.tenant_database_offset + hash(tenant_id) % 14  # Redis has 16 DBs by default
        
        if self.sentinel:
            client = self.sentinel.master_for(
                self.config.sentinel_service_name,
                socket_timeout=self.config.socket_timeout,
                password=self.config.password,
                db=tenant_db
            )
        else:
            pool = ConnectionPool(
                host=self.config.host,
                port=self.config.port,
                db=tenant_db,
                password=self.config.password,
                ssl=self.config.ssl,
                max_connections=max(5, self.config.pool_max_connections // 10),
                socket_timeout=self.config.socket_timeout,
                socket_connect_timeout=self.config.socket_connect_timeout,
                retry_on_timeout=self.config.retry_on_timeout
            )
            client = Redis(connection_pool=pool)
        
        self.tenant_clients[tenant_id] = client
    
    # Core Redis operations
    async def get(self, key: str, tenant_id: Optional[str] = None) -> Optional[str]:
        """Get value by key"""
        try:
            client = await self.get_tenant_connection(tenant_id) if tenant_id else await self.get_connection()
            result = await client.get(key)
            self.command_count += 1
            return result.decode('utf-8') if result else None
            
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"Redis GET failed for key {key}: {e}")
            raise
    
    async def set(self, 
                 key: str, 
                 value: Union[str, bytes, int, float], 
                 ex: Optional[int] = None,
                 px: Optional[int] = None,
                 nx: bool = False,
                 xx: bool = False,
                 tenant_id: Optional[str] = None) -> bool:
        """Set value with optional expiration"""
        try:
            client = await self.get_tenant_connection(tenant_id) if tenant_id else await self.get_connection()
            result = await client.set(key, value, ex=ex, px=px, nx=nx, xx=xx)
            self.command_count += 1
            return result
            
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"Redis SET failed for key {key}: {e}")
            raise
    
    async def delete(self, *keys: str, tenant_id: Optional[str] = None) -> int:
        """Delete keys"""
        try:
            client = await self.get_tenant_connection(tenant_id) if tenant_id else await self.get_connection()
            result = await client.delete(*keys)
            self.command_count += 1
            return result
            
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"Redis DELETE failed for keys {keys}: {e}")
            raise
    
    async def exists(self, *keys: str, tenant_id: Optional[str] = None) -> int:
        """Check if keys exist"""
        try:
            client = await self.get_tenant_connection(tenant_id) if tenant_id else await self.get_connection()
            result = await client.exists(*keys)
            self.command_count += 1
            return result
            
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"Redis EXISTS failed for keys {keys}: {e}")
            raise
    
    async def expire(self, key: str, seconds: int, tenant_id: Optional[str] = None) -> bool:
        """Set expiration on key"""
        try:
            client = await self.get_tenant_connection(tenant_id) if tenant_id else await self.get_connection()
            result = await client.expire(key, seconds)
            self.command_count += 1
            return result
            
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"Redis EXPIRE failed for key {key}: {e}")
            raise
    
    # JSON operations for complex data
    async def set_json(self, 
                      key: str, 
                      value: Dict[str, Any], 
                      ex: Optional[int] = None,
                      tenant_id: Optional[str] = None) -> bool:
        """Set JSON value"""
        json_value = json.dumps(value)
        return await self.set(key, json_value, ex=ex, tenant_id=tenant_id)
    
    async def get_json(self, key: str, tenant_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get JSON value"""
        value = await self.get(key, tenant_id)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                self.logger.error(f"Failed to decode JSON for key {key}")
        return None
    
    # Hash operations
    async def hset(self, 
                  name: str, 
                  mapping: Dict[str, Any], 
                  tenant_id: Optional[str] = None) -> int:
        """Set hash field(s)"""
        try:
            client = await self.get_tenant_connection(tenant_id) if tenant_id else await self.get_connection()
            result = await client.hset(name, mapping=mapping)
            self.command_count += 1
            return result
            
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"Redis HSET failed for hash {name}: {e}")
            raise
    
    async def hget(self, name: str, key: str, tenant_id: Optional[str] = None) -> Optional[str]:
        """Get hash field value"""
        try:
            client = await self.get_tenant_connection(tenant_id) if tenant_id else await self.get_connection()
            result = await client.hget(name, key)
            self.command_count += 1
            return result.decode('utf-8') if result else None
            
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"Redis HGET failed for hash {name}, key {key}: {e}")
            raise
    
    async def hgetall(self, name: str, tenant_id: Optional[str] = None) -> Dict[str, str]:
        """Get all hash fields"""
        try:
            client = await self.get_tenant_connection(tenant_id) if tenant_id else await self.get_connection()
            result = await client.hgetall(name)
            self.command_count += 1
            return {k.decode('utf-8'): v.decode('utf-8') for k, v in result.items()}
            
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"Redis HGETALL failed for hash {name}: {e}")
            raise
    
    # List operations
    async def lpush(self, name: str, *values, tenant_id: Optional[str] = None) -> int:
        """Push values to left of list"""
        try:
            client = await self.get_tenant_connection(tenant_id) if tenant_id else await self.get_connection()
            result = await client.lpush(name, *values)
            self.command_count += 1
            return result
            
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"Redis LPUSH failed for list {name}: {e}")
            raise
    
    async def rpop(self, name: str, tenant_id: Optional[str] = None) -> Optional[str]:
        """Pop value from right of list"""
        try:
            client = await self.get_tenant_connection(tenant_id) if tenant_id else await self.get_connection()
            result = await client.rpop(name)
            self.command_count += 1
            return result.decode('utf-8') if result else None
            
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"Redis RPOP failed for list {name}: {e}")
            raise
    
    async def llen(self, name: str, tenant_id: Optional[str] = None) -> int:
        """Get list length"""
        try:
            client = await self.get_tenant_connection(tenant_id) if tenant_id else await self.get_connection()
            result = await client.llen(name)
            self.command_count += 1
            return result
            
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"Redis LLEN failed for list {name}: {e}")
            raise
    
    # Set operations
    async def sadd(self, name: str, *values, tenant_id: Optional[str] = None) -> int:
        """Add values to set"""
        try:
            client = await self.get_tenant_connection(tenant_id) if tenant_id else await self.get_connection()
            result = await client.sadd(name, *values)
            self.command_count += 1
            return result
            
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"Redis SADD failed for set {name}: {e}")
            raise
    
    async def smembers(self, name: str, tenant_id: Optional[str] = None) -> Set[str]:
        """Get all set members"""
        try:
            client = await self.get_tenant_connection(tenant_id) if tenant_id else await self.get_connection()
            result = await client.smembers(name)
            self.command_count += 1
            return {member.decode('utf-8') for member in result}
            
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"Redis SMEMBERS failed for set {name}: {e}")
            raise
    
    # Pub/Sub operations
    async def publish(self, channel: str, message: str, tenant_id: Optional[str] = None) -> int:
        """Publish message to channel"""
        try:
            client = await self.get_tenant_connection(tenant_id) if tenant_id else await self.get_connection()
            result = await client.publish(channel, message)
            self.command_count += 1
            return result
            
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"Redis PUBLISH failed for channel {channel}: {e}")
            raise
    
    async def health_check(self) -> Dict[str, Any]:
        """Check Redis connection health"""
        try:
            start_time = datetime.utcnow()
            
            client = await self.get_connection()
            
            # Test basic connectivity
            await client.ping()
            
            # Get Redis info
            info = await client.info()
            
            response_time = (datetime.utcnow() - start_time).total_seconds()
            self.last_health_check = datetime.utcnow()
            
            return {
                "status": "healthy",
                "response_time": response_time,
                "redis_version": info.get("redis_version"),
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory_human"),
                "used_memory_peak": info.get("used_memory_peak_human"),
                "keyspace": {k: v for k, v in info.items() if k.startswith("db")},
                "metrics": {
                    "connection_count": self.connection_count,
                    "command_count": self.command_count,
                    "error_count": self.error_count
                },
                "tenant_clients": len(self.tenant_clients),
                "last_check": self.last_health_check.isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Redis health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "last_check": datetime.utcnow().isoformat()
            }
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get detailed Redis metrics"""
        try:
            client = await self.get_connection()
            info = await client.info()
            
            return {
                "server": {
                    "redis_version": info.get("redis_version"),
                    "uptime_in_seconds": info.get("uptime_in_seconds"),
                    "uptime_in_days": info.get("uptime_in_days")
                },
                "clients": {
                    "connected_clients": info.get("connected_clients"),
                    "client_recent_max_input_buffer": info.get("client_recent_max_input_buffer"),
                    "client_recent_max_output_buffer": info.get("client_recent_max_output_buffer")
                },
                "memory": {
                    "used_memory": info.get("used_memory"),
                    "used_memory_human": info.get("used_memory_human"),
                    "used_memory_peak": info.get("used_memory_peak"),
                    "used_memory_peak_human": info.get("used_memory_peak_human"),
                    "used_memory_overhead": info.get("used_memory_overhead")
                },
                "stats": {
                    "total_connections_received": info.get("total_connections_received"),
                    "total_commands_processed": info.get("total_commands_processed"),
                    "instantaneous_ops_per_sec": info.get("instantaneous_ops_per_sec"),
                    "total_net_input_bytes": info.get("total_net_input_bytes"),
                    "total_net_output_bytes": info.get("total_net_output_bytes"),
                    "rejected_connections": info.get("rejected_connections")
                },
                "keyspace": {k: v for k, v in info.items() if k.startswith("db")},
                "tenant_metrics": {
                    "tenant_clients": len(self.tenant_clients),
                    "connection_count": self.connection_count,
                    "command_count": self.command_count,
                    "error_count": self.error_count
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get Redis metrics: {e}")
            return {"error": str(e)}
    
    async def shutdown(self) -> None:
        """Shutdown Redis connections"""
        self.logger.info("Shutting down Redis connections...")
        
        # Close tenant clients
        for tenant_id, client in self.tenant_clients.items():
            await client.close()
            self.logger.info(f"Closed Redis client for tenant {tenant_id}")
        
        # Close main client
        if self.redis_client:
            await self.redis_client.close()
            self.logger.info("Closed main Redis client")
        
        # Close connection pool
        if self.connection_pool:
            await self.connection_pool.disconnect()
            self.logger.info("Disconnected Redis connection pool")
        
        self.redis_client = None
        self.connection_pool = None
        self.tenant_clients.clear()
        
        self.logger.info("Redis connections shutdown completed")
