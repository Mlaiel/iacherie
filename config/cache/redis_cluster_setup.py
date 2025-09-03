#!/usr/bin/env python3
"""
Redis Cluster Setup Implementation
Complete Redis cluster configuration with monitoring and health checks
"""
import os
import json
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import redis
from redis.sentinel import Sentinel
import asyncio
import time

logger = logging.getLogger(__name__)

class RedisDeploymentType(Enum):
    """Redis deployment types"""
    STANDALONE = "standalone"
    CLUSTER = "cluster"
    SENTINEL = "sentinel"

@dataclass
class RedisClusterConfig:
    """Redis cluster configuration"""
    startup_nodes: List[Dict[str, Union[str, int]]] = field(default_factory=list)
    decode_responses: bool = True
    skip_full_coverage_check: bool = False
    max_connections_per_node: int = 50
    readonly_mode: bool = False
    health_check_interval: int = 30
    password: Optional[str] = None
    ssl: bool = False
    socket_timeout: float = 5.0
    socket_connect_timeout: float = 5.0
    retry_on_timeout: bool = True

@dataclass
class RedisCredentials:
    """Redis connection credentials"""
    password: Optional[str] = None
    username: Optional[str] = None
    ssl_cert_file: Optional[str] = None
    ssl_key_file: Optional[str] = None
    ssl_ca_file: Optional[str] = None
    sentinel_hosts: List[str] = field(default_factory=list)
    sentinel_service_name: str = "mymaster"

class RedisClusterManager:
    """
    Redis Cluster Setup and Management
    
    Features:
    - Automatic cluster discovery
    - Health monitoring
    - Failover handling
    - Connection pooling
    - Performance metrics
    """
    
    def __init__(self, config: RedisClusterConfig, credentials: RedisCredentials):
        self.config = config
        self.credentials = credentials
        self.logger = logging.getLogger(f"{__name__}.RedisClusterManager")
        self.cluster_client = None
        self.monitoring_task = None
        self.health_stats = {
            "total_requests": 0,
            "failed_requests": 0,
            "avg_latency": 0.0,
            "last_health_check": None
        }
    
    async def initialize(self) -> bool:
        """Initialize Redis cluster connection"""
        try:
            self.logger.info("🔧 Initializing Redis cluster...")
            
            # Create cluster client
            self.cluster_client = await self._create_cluster_client()
            
            # Test connection
            await self._test_connection()
            
            # Setup monitoring
            await self._setup_monitoring()
            
            self.logger.info("✅ Redis cluster initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Redis cluster: {e}")
            return False
    
    async def _create_cluster_client(self):
        """Create Redis cluster client"""
        try:
            # Use redis-py cluster support
            from redis.cluster import RedisCluster
            
            return RedisCluster(
                startup_nodes=self.config.startup_nodes,
                decode_responses=self.config.decode_responses,
                skip_full_coverage_check=self.config.skip_full_coverage_check,
                max_connections_per_node=self.config.max_connections_per_node,
                readonly_mode=self.config.readonly_mode,
                health_check_interval=self.config.health_check_interval,
                password=self.credentials.password,
                socket_timeout=self.config.socket_timeout,
                socket_connect_timeout=self.config.socket_connect_timeout,
                retry_on_timeout=self.config.retry_on_timeout
            )
            
        except ImportError:
            self.logger.error("redis-py-cluster not available. Using standard Redis client.")
            # Fallback to standard Redis client
            if self.config.startup_nodes:
                node = self.config.startup_nodes[0]
                return redis.Redis(
                    host=node.get('host', 'localhost'),
                    port=node.get('port', 6379),
                    password=self.credentials.password,
                    socket_timeout=self.config.socket_timeout,
                    socket_connect_timeout=self.config.socket_connect_timeout,
                    decode_responses=self.config.decode_responses
                )
            else:
                raise ValueError("No startup nodes configured")
    
    async def _test_connection(self):
        """Test cluster connection"""
        try:
            # Test ping
            result = self.cluster_client.ping()
            if not result:
                raise ConnectionError("Ping failed")
            
            # Test basic operations
            test_key = "cluster_test_key"
            self.cluster_client.set(test_key, "test", ex=10)
            value = self.cluster_client.get(test_key)
            
            if value != "test":
                raise ValueError("Basic read/write test failed")
            
            self.cluster_client.delete(test_key)
            self.logger.info("✅ Cluster connection test passed")
            
        except Exception as e:
            self.logger.error(f"❌ Cluster connection test failed: {e}")
            raise
    
    async def _setup_monitoring(self):
        """Setup cluster health monitoring"""
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
    
    async def _monitoring_loop(self):
        """Continuous cluster monitoring"""
        while True:
            try:
                await asyncio.sleep(self.config.health_check_interval)
                await self._check_cluster_health()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"❌ Monitoring error: {e}")
    
    async def _check_cluster_health(self):
        """Check cluster health and update stats"""
        try:
            start_time = time.time()
            
            # Check cluster info
            try:
                info = self.cluster_client.cluster_info()
                cluster_state = info.get('cluster_state', 'unknown')
                
                if cluster_state != 'ok':
                    self.logger.warning(f"⚠️ Cluster state: {cluster_state}")
                
            except AttributeError:
                # Not a cluster client - check regular info
                info = self.cluster_client.info()
                
            # Test basic operation
            self.cluster_client.ping()
            
            # Update stats
            latency = (time.time() - start_time) * 1000  # Convert to ms
            self._update_health_stats(latency, success=True)
            
            self.logger.debug(f"✅ Health check passed - latency: {latency:.2f}ms")
            
        except Exception as e:
            self._update_health_stats(0, success=False)
            self.logger.error(f"❌ Health check failed: {e}")
    
    def _update_health_stats(self, latency: float, success: bool):
        """Update health statistics"""
        self.health_stats["total_requests"] += 1
        self.health_stats["last_health_check"] = time.time()
        
        if success:
            # Update rolling average latency
            current_avg = self.health_stats["avg_latency"]
            total = self.health_stats["total_requests"]
            self.health_stats["avg_latency"] = ((current_avg * (total - 1)) + latency) / total
        else:
            self.health_stats["failed_requests"] += 1
    
    def get_health_stats(self) -> Dict[str, Any]:
        """Get current health statistics"""
        total = self.health_stats["total_requests"]
        failed = self.health_stats["failed_requests"]
        success_rate = ((total - failed) / total * 100) if total > 0 else 0
        
        return {
            **self.health_stats,
            "success_rate": success_rate,
            "is_healthy": success_rate > 95.0 and self.health_stats["avg_latency"] < 50.0
        }
    
    async def close(self):
        """Close cluster connections"""
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        if self.cluster_client:
            try:
                if hasattr(self.cluster_client, 'close'):
                    self.cluster_client.close()
            except Exception as e:
                self.logger.error(f"Error closing cluster client: {e}")

# Factory function to create cluster manager from environment
def create_cluster_manager_from_env() -> RedisClusterManager:
    """Create Redis cluster manager from environment variables"""
    
    # Parse startup nodes from environment
    startup_nodes = []
    nodes_str = os.getenv("REDIS_CLUSTER_NODES", "localhost:6379")
    
    for node_str in nodes_str.split(","):
        if ":" in node_str:
            host, port = node_str.strip().split(":", 1)
            startup_nodes.append({"host": host, "port": int(port)})
        else:
            startup_nodes.append({"host": node_str.strip(), "port": 6379})
    
    # Create configuration
    config = RedisClusterConfig(
        startup_nodes=startup_nodes,
        max_connections_per_node=int(os.getenv("REDIS_CLUSTER_MAX_CONNECTIONS", "50")),
        readonly_mode=os.getenv("REDIS_CLUSTER_READONLY", "false").lower() == "true",
        health_check_interval=int(os.getenv("REDIS_CLUSTER_HEALTH_INTERVAL", "30")),
        socket_timeout=float(os.getenv("REDIS_SOCKET_TIMEOUT", "5.0")),
        socket_connect_timeout=float(os.getenv("REDIS_SOCKET_CONNECT_TIMEOUT", "5.0"))
    )
    
    # Create credentials
    credentials = RedisCredentials(
        password=os.getenv("REDIS_PASSWORD"),
        username=os.getenv("REDIS_USERNAME")
    )
    
    return RedisClusterManager(config, credentials)

# Export main components
__all__ = [
    'RedisClusterManager',
    'RedisClusterConfig', 
    'RedisCredentials',
    'RedisDeploymentType',
    'create_cluster_manager_from_env'
]