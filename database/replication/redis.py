"""Redis Replication Handler - IA Influencer Agent Platform

Advanced Redis replication management for cache, session data, and real-time features.
Supports Sentinel, Cluster, and Master-Slave configurations with automated failover
and load balancing for the content creator platform.

Handles:
- User session data replication
- Cache synchronization across regions
- Real-time notification channels
- AI processing queue replication

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""import asyncio
import logging
import redis.asyncio as redis
from redis.asyncio.sentinel import Sentinel
from redis.asyncio.cluster import RedisCluster
from typing import Dict, Any, Optional, List, Set
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import json


class RedisReplicationMode(Enum):
    """Redis replication modes"""    MASTER_SLAVE = "master_slave"
    SENTINEL = "sentinel"
    CLUSTER = "cluster"


class RedisNodeRole(Enum):
    """Redis node roles"""    MASTER = "master"
    SLAVE = "slave"
    SENTINEL = "sentinel"


@dataclass
class RedisNode:
    """Redis node configuration"""    host: str
    port: int
    role: RedisNodeRole
    name: str
    password: Optional[str] = None
    db: int = 0
    ssl: bool = False
    health_status: str = "unknown"
    last_seen: Optional[datetime] = None


@dataclass
class RedisReplicationMetrics:
    """Redis replication metrics"""    connected_slaves: int = 0
    master_repl_offset: int = 0
    repl_backlog_size: int = 0
    repl_backlog_first_byte_offset: int = 0
    repl_backlog_histlen: int = 0
    master_last_io_seconds_ago: int = -1
    master_sync_in_progress: bool = False
    slave_repl_offset: int = 0
    slave_lag: float = 0.0
    keyspace_hits: int = 0
    keyspace_misses: int = 0
    used_memory: int = 0
    total_commands_processed: int = 0


class RedisReplicationHandler:
    """    Advanced Redis replication handler for the IA Influencer Agent platform.
    
    Manages Redis replication for caching, session management, real-time features,
    and AI processing queues with high availability and performance optimization.
    """    
    def __init__(self, config: Dict[str, Any], global_config: Any):
        """Initialize Redis replication handler"""        self.config = config
        self.global_config = global_config
        self.logger = logging.getLogger(f"{__name__}.RedisReplicationHandler")
        
        # Configuration
        self.replication_mode = RedisReplicationMode(config.get("replication_type", "sentinel"))
        self.nodes: List[RedisNode] = []
        self.sentinel_config = config.get("sentinel", {})
        self.cluster_config = config.get("cluster", {})
        
        # Connection objects
        self.master_client: Optional[redis.Redis] = None
        self.slave_clients: Dict[str, redis.Redis] = {}
        self.sentinel_client: Optional[Sentinel] = None
        self.cluster_client: Optional[RedisCluster] = None
        
        # Monitoring
        self.is_monitoring = False
        self.last_metrics: Dict[str, RedisReplicationMetrics] = {}
        self.failover_history: List[Dict[str, Any]] = []
        
        # State tracking
        self.current_master: Optional[RedisNode] = None
        self.active_slaves: Set[str] = set()
        
        self.logger.info(f"Redis replication handler initialized (mode: {self.replication_mode.value})")
    
    async def initialize(self) -> bool:
        """        Initialize Redis replication infrastructure.
        
        Returns:
            bool: True if initialization successful
        """        try:
            self.logger.info("Initializing Redis replication handler...")
            
            # Parse node configurations
            await self._parse_node_configurations()
            
            # Initialize based on replication mode
            if self.replication_mode == RedisReplicationMode.SENTINEL:
                await self._initialize_sentinel_replication()
            elif self.replication_mode == RedisReplicationMode.CLUSTER:
                await self._initialize_cluster_replication()
            else:
                await self._initialize_master_slave_replication()
            
            # Start monitoring
            await self._start_monitoring()
            
            self.logger.info("Redis replication handler initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Redis replication handler: {e}")
            return False
    
    async def _parse_node_configurations(self) -> None:
        """Parse Redis node configurations"""        # Master configuration
        master_config = self.config.get("master", {})
        if master_config:
            master_node = RedisNode(
                host=master_config["host"],
                port=master_config["port"],
                role=RedisNodeRole.MASTER,
                name="master",
                password=master_config.get("password"),
                db=master_config.get("database", 0),
                ssl=master_config.get("ssl_enabled", False)
            )
            self.nodes.append(master_node)
            self.current_master = master_node
        
        # Slave configurations
        slaves_config = self.config.get("slaves", [])
        for i, slave_config in enumerate(slaves_config):
            slave_node = RedisNode(
                host=slave_config["host"],
                port=slave_config["port"],
                role=RedisNodeRole.SLAVE,
                name=slave_config.get("name", f"slave_{i}"),
                password=slave_config.get("password"),
                db=slave_config.get("database", 0),
                ssl=slave_config.get("ssl_enabled", False)
            )
            self.nodes.append(slave_node)
            self.active_slaves.add(slave_node.name)
        
        # Sentinel configurations
        sentinel_nodes = self.sentinel_config.get("nodes", [])
        for i, sentinel_config in enumerate(sentinel_nodes):
            sentinel_node = RedisNode(
                host=sentinel_config["host"],
                port=sentinel_config["port"],
                role=RedisNodeRole.SENTINEL,
                name=f"sentinel_{i}",
                password=sentinel_config.get("password")
            )
            self.nodes.append(sentinel_node)
        
        self.logger.debug(f"Parsed {len(self.nodes)} Redis nodes")
    
    async def _initialize_sentinel_replication(self) -> None:
        """Initialize Redis Sentinel replication"""        self.logger.info("Initializing Redis Sentinel replication...")
        
        sentinel_nodes = [
            (node.host, node.port) 
            for node in self.nodes 
            if node.role == RedisNodeRole.SENTINEL
        ]
        
        if not sentinel_nodes:
            raise ValueError("No Sentinel nodes configured")
        
        # Initialize Sentinel client
        self.sentinel_client = Sentinel(
            sentinel_nodes,
            socket_timeout=self.config.get("timeout", 5),
            password=self.sentinel_config.get("password")
        )
        
        # Get master service name
        master_service = self.sentinel_config.get("master_service", "mymaster")
        
        # Get master and slave connections through Sentinel
        try:
            self.master_client = self.sentinel_client.master_for(
                master_service,
                socket_timeout=self.config.get("timeout", 5),
                password=self.config.get("password")
            )
            
            slave_client = self.sentinel_client.slave_for(
                master_service,
                socket_timeout=self.config.get("timeout", 5),
                password=self.config.get("password")
            )
            
            self.slave_clients["sentinel_slave"] = slave_client
            
            # Test connections
            await self.master_client.ping()
            await slave_client.ping()
            
            self.logger.info("Redis Sentinel replication initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Sentinel connections: {e}")
            raise
    
    async def _initialize_cluster_replication(self) -> None:
        """Initialize Redis Cluster replication"""        self.logger.info("Initializing Redis Cluster replication...")
        
        cluster_nodes = [
            {"host": node.host, "port": node.port}
            for node in self.nodes
            if node.role in [RedisNodeRole.MASTER, RedisNodeRole.SLAVE]
        ]
        
        if not cluster_nodes:
            raise ValueError("No cluster nodes configured")
        
        # Initialize cluster client
        self.cluster_client = RedisCluster(
            startup_nodes=cluster_nodes,
            decode_responses=True,
            skip_full_coverage_check=True,
            password=self.cluster_config.get("password")
        )
        
        try:
            # Test cluster connection
            await self.cluster_client.ping()
            
            # Get cluster info
            cluster_info = await self.cluster_client.cluster_info()
            self.logger.debug(f"Cluster info: {cluster_info}")
            
            self.logger.info("Redis Cluster replication initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize cluster connection: {e}")
            raise
    
    async def _initialize_master_slave_replication(self) -> None:
        """Initialize traditional master-slave replication"""        self.logger.info("Initializing Redis master-slave replication...")
        
        # Initialize master connection
        if self.current_master:
            self.master_client = redis.Redis(
                host=self.current_master.host,
                port=self.current_master.port,
                password=self.current_master.password,
                db=self.current_master.db,
                ssl=self.current_master.ssl,
                decode_responses=True,
                socket_timeout=self.config.get("timeout", 5)
            )
            
            try:
                await self.master_client.ping()
                self.logger.debug("Master connection established")
            except Exception as e:
                self.logger.error(f"Failed to connect to master: {e}")
                raise
        
        # Initialize slave connections
        for node in self.nodes:
            if node.role == RedisNodeRole.SLAVE:
                slave_client = redis.Redis(
                    host=node.host,
                    port=node.port,
                    password=node.password,
                    db=node.db,
                    ssl=node.ssl,
                    decode_responses=True,
                    socket_timeout=self.config.get("timeout", 5)
                )
                
                try:
                    await slave_client.ping()
                    self.slave_clients[node.name] = slave_client
                    self.logger.debug(f"Slave connection established: {node.name}")
                    
                    # Configure slave replication
                    await self._configure_slave_replication(slave_client, self.current_master)
                    
                except Exception as e:
                    self.logger.error(f"Failed to connect to slave {node.name}: {e}")
                    # Continue with other slaves
        
        self.logger.info("Redis master-slave replication initialized successfully")
    
    async def _configure_slave_replication(self, slave_client: redis.Redis, master: RedisNode) -> None:
        """Configure slave to replicate from master"""        try:
            # Configure slave replication
            await slave_client.slaveof(master.host, master.port)
            
            if master.password:
                await slave_client.config_set("masterauth", master.password)
            
            # Set slave to read-only
            await slave_client.config_set("slave-read-only", "yes")
            
            self.logger.debug(f"Slave replication configured for master {master.host}:{master.port}")
            
        except Exception as e:
            self.logger.error(f"Failed to configure slave replication: {e}")
            raise
    
    async def _start_monitoring(self) -> None:
        """Start Redis replication monitoring"""        self.is_monitoring = True
        asyncio.create_task(self._monitoring_loop())
        self.logger.info("Redis replication monitoring started")
    
    async def _monitoring_loop(self) -> None:
        """Main monitoring loop for Redis replication"""        while self.is_monitoring:
            try:
                await self._collect_replication_metrics()
                await self._check_node_health()
                await asyncio.sleep(self.global_config.monitoring_interval)
            except Exception as e:
                self.logger.error(f"Error in Redis monitoring loop: {e}")
                await asyncio.sleep(30)
    
    async def _collect_replication_metrics(self) -> None:
        """Collect Redis replication metrics"""        # Collect master metrics
        if self.master_client:
            try:
                info = await self.master_client.info("replication")
                stats = await self.master_client.info("stats")
                memory = await self.master_client.info("memory")
                
                master_metrics = RedisReplicationMetrics(
                    connected_slaves=info.get("connected_slaves", 0),
                    master_repl_offset=info.get("master_repl_offset", 0),
                    repl_backlog_size=info.get("repl_backlog_size", 0),
                    keyspace_hits=stats.get("keyspace_hits", 0),
                    keyspace_misses=stats.get("keyspace_misses", 0),
                    used_memory=memory.get("used_memory", 0),
                    total_commands_processed=stats.get("total_commands_processed", 0)
                )
                
                self.last_metrics["master"] = master_metrics
                
            except Exception as e:
                self.logger.error(f"Failed to collect master metrics: {e}")
        
        # Collect slave metrics
        for slave_name, slave_client in self.slave_clients.items():
            try:
                info = await slave_client.info("replication")
                stats = await slave_client.info("stats")
                
                slave_metrics = RedisReplicationMetrics(
                    slave_repl_offset=info.get("slave_repl_offset", 0),
                    master_last_io_seconds_ago=info.get("master_last_io_seconds_ago", -1),
                    master_sync_in_progress=info.get("master_sync_in_progress", False),
                    keyspace_hits=stats.get("keyspace_hits", 0),
                    keyspace_misses=stats.get("keyspace_misses", 0),
                    total_commands_processed=stats.get("total_commands_processed", 0)
                )
                
                # Calculate lag
                if "master" in self.last_metrics:
                    master_offset = self.last_metrics["master"].master_repl_offset
                    slave_offset = slave_metrics.slave_repl_offset
                    slave_metrics.slave_lag = max(0, master_offset - slave_offset)
                
                self.last_metrics[slave_name] = slave_metrics
                
                # Check for high lag
                if slave_metrics.slave_lag > self.global_config.lag_threshold:
                    self.logger.warning(f"High replication lag for {slave_name}: {slave_metrics.slave_lag}")
                
            except Exception as e:
                self.logger.error(f"Failed to collect metrics for slave {slave_name}: {e}")
    
    async def _check_node_health(self) -> None:
        """Check health of all Redis nodes"""        for node in self.nodes:
            try:
                # Create temporary client for health check
                client = redis.Redis(
                    host=node.host,
                    port=node.port,
                    password=node.password,
                    db=node.db,
                    ssl=node.ssl,
                    socket_timeout=5
                )
                
                # Ping test
                await client.ping()
                node.health_status = "healthy"
                node.last_seen = datetime.utcnow()
                
                await client.close()
                
            except Exception as e:
                node.health_status = "unhealthy"
                self.logger.warning(f"Health check failed for {node.name}: {e}")
                
                # Trigger failover if master is unhealthy
                if node.role == RedisNodeRole.MASTER and self.replication_mode == RedisReplicationMode.SENTINEL:
                    await self._handle_master_failure()
    
    async def _handle_master_failure(self) -> None:
        """Handle Redis master failure with Sentinel"""        try:
            self.logger.warning("Handling Redis master failure...")
            
            if self.sentinel_client:
                # Get current master from Sentinel
                master_service = self.sentinel_config.get("master_service", "mymaster")
                
                try:
                    master_info = await self.sentinel_client.discover_master(master_service)
                    new_master_host, new_master_port = master_info
                    
                    # Update current master
                    for node in self.nodes:
                        if node.host == new_master_host and node.port == new_master_port:
                            old_master = self.current_master
                            self.current_master = node
                            node.role = RedisNodeRole.MASTER
                            
                            # Record failover
                            failover_event = {
                                "timestamp": datetime.utcnow().isoformat(),
                                "old_master": f"{old_master.host}:{old_master.port}" if old_master else "unknown",
                                "new_master": f"{node.host}:{node.port}",
                                "reason": "master_failure"
                            }
                            self.failover_history.append(failover_event)
                            
                            self.logger.info(f"Failover completed: new master is {node.host}:{node.port}")
                            break
                    
                    # Reinitialize master client
                    await self._reinitialize_master_client()
                    
                except Exception as e:
                    self.logger.error(f"Failed to discover new master: {e}")
            
        except Exception as e:
            self.logger.error(f"Error handling master failure: {e}")
    
    async def _reinitialize_master_client(self) -> None:
        """Reinitialize master client after failover"""        try:
            if self.master_client:
                await self.master_client.close()
            
            if self.replication_mode == RedisReplicationMode.SENTINEL and self.sentinel_client:
                master_service = self.sentinel_config.get("master_service", "mymaster")
                self.master_client = self.sentinel_client.master_for(
                    master_service,
                    socket_timeout=self.config.get("timeout", 5),
                    password=self.config.get("password")
                )
            elif self.current_master:
                self.master_client = redis.Redis(
                    host=self.current_master.host,
                    port=self.current_master.port,
                    password=self.current_master.password,
                    db=self.current_master.db,
                    ssl=self.current_master.ssl,
                    decode_responses=True,
                    socket_timeout=self.config.get("timeout", 5)
                )
            
            # Test new connection
            if self.master_client:
                await self.master_client.ping()
                self.logger.info("Master client reinitialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to reinitialize master client: {e}")
            raise
    
    async def start_replication(
        self, 
        source_config: Dict[str, Any], 
        target_config: Dict[str, Any], 
        mode: str
    ) -> bool:
        """Start Redis replication"""        try:
            self.logger.info(f"Starting Redis replication in {mode} mode")
            
            # Update configuration and reinitialize if needed
            self.config.update(source_config)
            
            if not self.master_client:
                await self.initialize()
            
            self.logger.info("Redis replication started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start Redis replication: {e}")
            return False
    
    async def stop_replication(self, graceful: bool = True) -> bool:
        """Stop Redis replication"""        try:
            self.logger.info(f"Stopping Redis replication (graceful={graceful})")
            
            # Stop monitoring
            self.is_monitoring = False
            
            if graceful:
                # Disable slave replication
                for slave_client in self.slave_clients.values():
                    try:
                        await slave_client.slaveof("NO", "ONE")
                    except Exception as e:
                        self.logger.error(f"Failed to disable slave replication: {e}")
            
            # Close connections
            if self.master_client:
                await self.master_client.close()
                self.master_client = None
            
            for slave_client in self.slave_clients.values():
                await slave_client.close()
            self.slave_clients.clear()
            
            if self.cluster_client:
                await self.cluster_client.close()
                self.cluster_client = None
            
            # Clear state
            self.last_metrics.clear()
            self.active_slaves.clear()
            
            self.logger.info("Redis replication stopped successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop Redis replication: {e}")
            return False
    
    async def pause_replication(self) -> bool:
        """Pause Redis replication"""        try:
            self.logger.info("Pausing Redis replication")
            
            # Pause slave replication
            for slave_client in self.slave_clients.values():
                await slave_client.slaveof("NO", "ONE")
            
            self.logger.info("Redis replication paused")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to pause Redis replication: {e}")
            return False
    
    async def resume_replication(self) -> bool:
        """Resume paused Redis replication"""        try:
            self.logger.info("Resuming Redis replication")
            
            # Resume slave replication
            if self.current_master:
                for slave_client in self.slave_clients.values():
                    await slave_client.slaveof(self.current_master.host, self.current_master.port)
            
            self.logger.info("Redis replication resumed")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to resume Redis replication: {e}")
            return False
    
    async def trigger_sync(self, force: bool = False) -> bool:
        """Trigger manual Redis synchronization"""        try:
            self.logger.info(f"Triggering Redis sync (force={force})")
            
            if force:
                # Force full resynchronization
                for slave_client in self.slave_clients.values():
                    await slave_client.debug_restart()
            else:
                # Trigger BGSAVE on master to ensure data consistency
                if self.master_client:
                    await self.master_client.bgsave()
            
            self.logger.info("Redis sync triggered successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to trigger Redis sync: {e}")
            return False
    
    async def prepare_maintenance(self, duration: timedelta) -> bool:
        """Prepare Redis for maintenance mode"""        try:
            self.logger.info(f"Preparing Redis for maintenance (duration: {duration})")
            
            # Create backup snapshot
            if self.master_client:
                await self.master_client.bgsave()
            
            # Disable automatic failover during maintenance
            if self.sentinel_client:
                master_service = self.sentinel_config.get("master_service", "mymaster")
                # Note: In production, you might want to temporarily disable failover
                # This depends on your Sentinel configuration
            
            self.logger.info("Redis maintenance preparation completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to prepare Redis for maintenance: {e}")
            return False
    
    async def exit_maintenance(self) -> bool:
        """Exit Redis maintenance mode"""        try:
            self.logger.info("Exiting Redis maintenance mode")
            
            # Re-enable automatic failover
            if self.sentinel_client:
                # Restore normal Sentinel operation
                pass
            
            # Ensure replication is working
            await self.resume_replication()
            
            self.logger.info("Redis maintenance mode exited")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to exit Redis maintenance mode: {e}")
            return False
    
    async def check_health(self) -> Dict[str, Any]:
        """Check Redis replication health"""        health = {
            "healthy": True,
            "issues": [],
            "metrics": {},
            "nodes": {}
        }
        
        try:
            # Check node health
            unhealthy_nodes = [
                node.name for node in self.nodes 
                if node.health_status != "healthy"
            ]
            
            if unhealthy_nodes:
                health["healthy"] = False
                health["issues"].extend([f"Unhealthy node: {node}" for node in unhealthy_nodes])
            
            # Check replication lag
            for node_name, metrics in self.last_metrics.items():
                if hasattr(metrics, 'slave_lag') and metrics.slave_lag > self.global_config.lag_threshold:
                    health["healthy"] = False
                    health["issues"].append(f"High lag for {node_name}: {metrics.slave_lag}")
            
            # Add node status
            for node in self.nodes:
                health["nodes"][node.name] = {
                    "role": node.role.value,
                    "host": node.host,
                    "port": node.port,
                    "health": node.health_status,
                    "last_seen": node.last_seen.isoformat() if node.last_seen else None
                }
            
            health["metrics"] = {
                name: {
                    "connected_slaves": getattr(metrics, 'connected_slaves', 0),
                    "slave_lag": getattr(metrics, 'slave_lag', 0),
                    "used_memory": getattr(metrics, 'used_memory', 0)
                }
                for name, metrics in self.last_metrics.items()
            }
            
        except Exception as e:
            health["healthy"] = False
            health["issues"].append(f"Health check failed: {e}")
        
        return health
    
    async def get_replication_metrics(self) -> Dict[str, Any]:
        """Get current Redis replication metrics"""        metrics = {
            "replication_mode": self.replication_mode.value,
            "total_nodes": len(self.nodes),
            "healthy_nodes": len([n for n in self.nodes if n.health_status == "healthy"]),
            "current_master": f"{self.current_master.host}:{self.current_master.port}" if self.current_master else None,
            "active_slaves": len(self.active_slaves),
            "failover_count": len(self.failover_history),
            "node_metrics": {},
            "errors": 0
        }
        
        # Add detailed metrics for each node
        for name, repl_metrics in self.last_metrics.items():
            metrics["node_metrics"][name] = {
                "connected_slaves": getattr(repl_metrics, 'connected_slaves', 0),
                "slave_lag": getattr(repl_metrics, 'slave_lag', 0),
                "used_memory": getattr(repl_metrics, 'used_memory', 0),
                "keyspace_hits": getattr(repl_metrics, 'keyspace_hits', 0),
                "keyspace_misses": getattr(repl_metrics, 'keyspace_misses', 0)
            }
        
        return metrics
    
    async def get_status(self) -> Dict[str, Any]:
        """Get comprehensive Redis handler status"""        return {
            "handler_type": "redis",
            "replication_mode": self.replication_mode.value,
            "initialized": self.master_client is not None,
            "monitoring": self.is_monitoring,
            "nodes_configured": len(self.nodes),
            "current_master": f"{self.current_master.host}:{self.current_master.port}" if self.current_master else None,
            "active_slaves": list(self.active_slaves),
            "failover_history": self.failover_history[-5:],  # Last 5 failovers
            "last_metrics_count": len(self.last_metrics)
        }
    
    async def shutdown(self) -> None:
        """Shutdown Redis replication handler"""        try:
            self.logger.info("Shutting down Redis replication handler")
            await self.stop_replication(graceful=True)
            self.logger.info("Redis replication handler shutdown completed")
        except Exception as e:
            self.logger.error(f"Error during Redis handler shutdown: {e}")
            raise
