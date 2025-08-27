"""
Topology Manager - IA Influencer Agent Platform

Advanced topology management for multi-region database replication with
intelligent routing, failover detection, and performance optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is proprietary and confidential. Any unauthorized use, modification,
or distribution is strictly prohibited and may result in legal action.
Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, Set, Tuple
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import json
import aiohttp
from .config import ReplicationConfig


class NodeRole(Enum):
    """Database node roles in replication topology"""
    PRIMARY = "primary"
    SECONDARY = "secondary"
    STANDBY = "standby"
    WITNESS = "witness"
    ROUTER = "router"


class NodeStatus(Enum):
    """Database node status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"
    MAINTENANCE = "maintenance"
    UNKNOWN = "unknown"


@dataclass
class DatabaseNode:
    """Database node configuration and status"""
    id: str
    host: str
    port: int
    role: NodeRole
    database_type: str
    region: str
    zone: str
    status: NodeStatus = NodeStatus.UNKNOWN
    last_seen: Optional[datetime] = None
    latency_ms: float = 0.0
    load_percentage: float = 0.0
    replication_lag_ms: float = 0.0
    priority: int = 100
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ReplicationTopology:
    """Complete replication topology configuration"""
    primary_region: str
    secondary_regions: List[str]
    nodes: Dict[str, DatabaseNode] = field(default_factory=dict)
    routing_rules: Dict[str, Any] = field(default_factory=dict)
    failover_config: Dict[str, Any] = field(default_factory=dict)
    performance_targets: Dict[str, float] = field(default_factory=dict)


class TopologyManager:
    """
    Comprehensive topology manager for database replication.
    
    Manages multi-region database topologies with intelligent routing,
    automatic failover detection, and performance optimization for the
    content creator platform.
    """
    
    def __init__(self, config: ReplicationConfig):
        """
        Initialize topology manager.
        
        Args:
            config: Replication configuration
        """
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.TopologyManager")
        
        # Topology state
        self.topology: Optional[ReplicationTopology] = None
        self.active_nodes: Dict[str, DatabaseNode] = {}
        self.failed_nodes: Set[str] = set()
        self.maintenance_nodes: Set[str] = set()
        
        # Monitoring
        self.is_monitoring = False
        self.monitoring_task: Optional[asyncio.Task] = None
        self.health_check_interval = config.health_check_interval
        
        # Performance tracking
        self.performance_metrics: Dict[str, Dict[str, float]] = {}
        self.routing_cache: Dict[str, str] = {}
        
        # Failover detection
        self.failure_detection_threshold = 3
        self.consecutive_failures: Dict[str, int] = {}
        
        self.logger.info("TopologyManager initialized")
    
    async def initialize(self) -> bool:
        """
        Initialize topology manager.
        
        Returns:
            bool: True if initialization successful
        """
        try:
            self.logger.info("Initializing topology manager...")
            
            # Load topology configuration
            await self._load_topology_configuration()
            
            # Discover database nodes
            await self._discover_database_nodes()
            
            # Validate topology
            await self._validate_topology()
            
            # Start monitoring
            await self._start_monitoring()
            
            self.logger.info("Topology manager initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize topology manager: {e}")
            return False
    
    async def _load_topology_configuration(self) -> None:
        """Load topology configuration from config"""
        try:
            topology_config = self.config.get_topology_config()
            
            self.topology = ReplicationTopology(
                primary_region=topology_config.get("primary_region", "us-east-1"),
                secondary_regions=topology_config.get("secondary_regions", []),
                routing_rules=topology_config.get("routing_rules", {}),
                failover_config=topology_config.get("failover_config", {}),
                performance_targets={
                    "max_latency_ms": 100,
                    "max_replication_lag_ms": 1000,
                    "min_availability_percent": 99.9,
                    **topology_config.get("performance_targets", {})
                }
            )
            
            self.logger.info(f"Loaded topology: primary={self.topology.primary_region}, "
                           f"secondaries={self.topology.secondary_regions}")
            
        except Exception as e:
            self.logger.error(f"Failed to load topology configuration: {e}")
            raise
    
    async def _discover_database_nodes(self) -> None:
        """Discover and register database nodes"""
        try:
            # Get database configurations
            database_configs = {
                "postgresql": self.config.get_database_config("postgresql"),
                "redis": self.config.get_database_config("redis"),
                "mongodb": self.config.get_database_config("mongodb"),
                "elasticsearch": self.config.get_database_config("elasticsearch"),
                "vector_store": self.config.get_database_config("vector_store")
            }
            
            for db_type, db_config in database_configs.items():
                if not db_config or not db_config.get("enabled"):
                    continue
                
                # Register primary node
                primary_node = await self._create_node_from_config(db_type, db_config, NodeRole.PRIMARY)
                if primary_node:
                    self.topology.nodes[primary_node.id] = primary_node
                    self.active_nodes[primary_node.id] = primary_node
                
                # Register secondary nodes
                secondaries = db_config.get("secondaries", [])
                for idx, secondary_config in enumerate(secondaries):
                    secondary_node = await self._create_node_from_config(
                        db_type, secondary_config, NodeRole.SECONDARY, f"secondary_{idx}"
                    )
                    if secondary_node:
                        self.topology.nodes[secondary_node.id] = secondary_node
                        self.active_nodes[secondary_node.id] = secondary_node
            
            self.logger.info(f"Discovered {len(self.topology.nodes)} database nodes")
            
        except Exception as e:
            self.logger.error(f"Failed to discover database nodes: {e}")
            raise
    
    async def _create_node_from_config(
        self, 
        db_type: str, 
        config: Dict[str, Any], 
        role: NodeRole, 
        suffix: str = ""
    ) -> Optional[DatabaseNode]:
        """Create database node from configuration"""
        try:
            node_id = f"{db_type}_{role.value}"
            if suffix:
                node_id += f"_{suffix}"
            
            node = DatabaseNode(
                id=node_id,
                host=config.get("host", "localhost"),
                port=config.get("port", 5432),
                role=role,
                database_type=db_type,
                region=config.get("region", self.topology.primary_region),
                zone=config.get("zone", "a"),
                priority=config.get("priority", 100 if role == NodeRole.PRIMARY else 50),
                metadata={
                    "ssl_enabled": config.get("ssl_enabled", True),
                    "pool_size": config.get("pool_size", 20),
                    "version": config.get("version", "unknown")
                }
            )
            
            return node
            
        except Exception as e:
            self.logger.error(f"Failed to create node from config: {e}")
            return None
    
    async def _validate_topology(self) -> None:
        """Validate topology configuration"""
        try:
            issues = []
            
            # Check for primary nodes
            primary_nodes = [node for node in self.topology.nodes.values() 
                           if node.role == NodeRole.PRIMARY]
            
            if not primary_nodes:
                issues.append("No primary nodes found")
            
            # Check region distribution
            regions = set(node.region for node in self.topology.nodes.values())
            if len(regions) < 2:
                issues.append("Insufficient region distribution for high availability")
            
            # Check database type coverage
            db_types = set(node.database_type for node in self.topology.nodes.values())
            required_types = {"postgresql", "redis"}  # Minimum required
            
            for required_type in required_types:
                if required_type not in db_types:
                    issues.append(f"Missing required database type: {required_type}")
            
            if issues:
                self.logger.warning(f"Topology validation issues: {issues}")
            else:
                self.logger.info("Topology validation passed")
            
        except Exception as e:
            self.logger.error(f"Failed to validate topology: {e}")
    
    async def _start_monitoring(self) -> None:
        """Start topology monitoring"""
        self.is_monitoring = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        self.logger.info("Topology monitoring started")
    
    async def _monitoring_loop(self) -> None:
        """Main monitoring loop for topology health"""
        while self.is_monitoring:
            try:
                # Check health of all nodes
                await self._check_nodes_health()
                
                # Update performance metrics
                await self._update_performance_metrics()
                
                # Detect failures
                await self._detect_failures()
                
                # Update routing cache
                await self._update_routing_cache()
                
                # Log topology status
                await self._log_topology_status()
                
                await asyncio.sleep(self.health_check_interval)
                
            except Exception as e:
                self.logger.error(f"Error in topology monitoring loop: {e}")
                await asyncio.sleep(30)
    
    async def _check_nodes_health(self) -> None:
        """Check health of all nodes in topology"""
        health_tasks = []
        
        for node_id, node in self.active_nodes.items():
            health_tasks.append(self._check_node_health(node))
        
        if health_tasks:
            health_results = await asyncio.gather(*health_tasks, return_exceptions=True)
            
            for idx, (node_id, node) in enumerate(self.active_nodes.items()):
                result = health_results[idx]
                
                if isinstance(result, Exception):
                    self._handle_node_failure(node, str(result))
                else:
                    self._handle_node_health_update(node, result)
    
    async def _check_node_health(self, node: DatabaseNode) -> Dict[str, Any]:
        """Check health of a specific node"""
        try:
            health_data = {
                "node_id": node.id,
                "timestamp": datetime.utcnow().isoformat(),
                "healthy": False,
                "latency_ms": 0.0,
                "replication_lag_ms": 0.0,
                "load_percentage": 0.0
            }
            
            start_time = datetime.utcnow()
            
            if node.database_type == "postgresql":
                health_data.update(await self._check_postgresql_health(node))
            elif node.database_type == "redis":
                health_data.update(await self._check_redis_health(node))
            elif node.database_type == "mongodb":
                health_data.update(await self._check_mongodb_health(node))
            elif node.database_type == "elasticsearch":
                health_data.update(await self._check_elasticsearch_health(node))
            
            # Calculate latency
            latency = (datetime.utcnow() - start_time).total_seconds() * 1000
            health_data["latency_ms"] = latency
            
            return health_data
            
        except Exception as e:
            raise Exception(f"Health check failed for {node.id}: {e}")
    
    async def _check_postgresql_health(self, node: DatabaseNode) -> Dict[str, Any]:
        """Check PostgreSQL node health"""
        try:
            import asyncpg
            
            conn = await asyncpg.connect(
                host=node.host,
                port=node.port,
                database="postgres",
                user=self.config.get_database_config("postgresql").get("username"),
                password=self.config.get_database_config("postgresql").get("password"),
                timeout=5
            )
            
            # Basic health check
            result = await conn.fetchval("SELECT 1")
            
            # Get replication status if secondary
            replication_lag = 0.0
            if node.role == NodeRole.SECONDARY:
                lag_result = await conn.fetchval(
                    "SELECT EXTRACT(EPOCH FROM (now() - pg_last_xact_replay_timestamp())) * 1000"
                )
                replication_lag = float(lag_result or 0)
            
            # Get system load
            load_result = await conn.fetchval(
                "SELECT round((SELECT count(*) FROM pg_stat_activity WHERE state = 'active') * 100.0 / "
                "(SELECT setting::int FROM pg_settings WHERE name = 'max_connections'), 2)"
            )
            load_percentage = float(load_result or 0)
            
            await conn.close()
            
            return {
                "healthy": True,
                "replication_lag_ms": replication_lag,
                "load_percentage": load_percentage
            }
            
        except Exception as e:
            return {"healthy": False, "error": str(e)}
    
    async def _check_redis_health(self, node: DatabaseNode) -> Dict[str, Any]:
        """Check Redis node health"""
        try:
            import aioredis
            
            redis = aioredis.Redis(
                host=node.host,
                port=node.port,
                password=self.config.get_database_config("redis").get("password"),
                socket_timeout=5
            )
            
            # Basic ping
            pong = await redis.ping()
            
            # Get replication info
            info = await redis.info("replication")
            replication_lag = 0.0
            
            if node.role == NodeRole.SECONDARY and "master_last_io_seconds_ago" in info:
                replication_lag = info["master_last_io_seconds_ago"] * 1000
            
            # Get memory usage
            memory_info = await redis.info("memory")
            used_memory = memory_info.get("used_memory", 0)
            max_memory = memory_info.get("maxmemory", 1)
            load_percentage = (used_memory / max_memory) * 100 if max_memory > 0 else 0
            
            await redis.close()
            
            return {
                "healthy": True,
                "replication_lag_ms": replication_lag,
                "load_percentage": load_percentage
            }
            
        except Exception as e:
            return {"healthy": False, "error": str(e)}
    
    async def _check_mongodb_health(self, node: DatabaseNode) -> Dict[str, Any]:
        """Check MongoDB node health"""
        try:
            from motor.motor_asyncio import AsyncIOMotorClient
            
            client = AsyncIOMotorClient(
                host=node.host,
                port=node.port,
                username=self.config.get_database_config("mongodb").get("username"),
                password=self.config.get_database_config("mongodb").get("password"),
                serverSelectionTimeoutMS=5000
            )
            
            # Basic ping
            await client.admin.command("ping")
            
            # Get replica set status
            rs_status = await client.admin.command("replSetGetStatus")
            replication_lag = 0.0
            
            for member in rs_status.get("members", []):
                if member.get("name") == f"{node.host}:{node.port}":
                    if member.get("stateStr") == "SECONDARY":
                        primary_optime = rs_status.get("optimeDate")
                        member_optime = member.get("optimeDate")
                        if primary_optime and member_optime:
                            replication_lag = (primary_optime - member_optime).total_seconds() * 1000
            
            client.close()
            
            return {
                "healthy": True,
                "replication_lag_ms": replication_lag,
                "load_percentage": 0.0  # MongoDB load calculation is complex
            }
            
        except Exception as e:
            return {"healthy": False, "error": str(e)}
    
    async def _check_elasticsearch_health(self, node: DatabaseNode) -> Dict[str, Any]:
        """Check Elasticsearch node health"""
        try:
            from elasticsearch import AsyncElasticsearch
            
            client = AsyncElasticsearch(
                hosts=[{"host": node.host, "port": node.port}],
                timeout=5
            )
            
            # Basic health check
            health = await client.cluster.health()
            
            # Get node stats
            stats = await client.nodes.stats(node_id="_local")
            
            await client.close()
            
            return {
                "healthy": health["status"] in ["green", "yellow"],
                "replication_lag_ms": 0.0,  # ES doesn't have traditional replication lag
                "load_percentage": 0.0  # Simplified for now
            }
            
        except Exception as e:
            return {"healthy": False, "error": str(e)}
    
    def _handle_node_health_update(self, node: DatabaseNode, health_data: Dict[str, Any]) -> None:
        """Handle node health update"""
        try:
            node.last_seen = datetime.utcnow()
            node.latency_ms = health_data.get("latency_ms", 0.0)
            node.replication_lag_ms = health_data.get("replication_lag_ms", 0.0)
            node.load_percentage = health_data.get("load_percentage", 0.0)
            
            if health_data.get("healthy", False):
                node.status = NodeStatus.HEALTHY
                # Reset failure counter
                self.consecutive_failures.pop(node.id, None)
            else:
                node.status = NodeStatus.DEGRADED
                self._record_node_failure(node)
            
            # Update performance metrics
            self.performance_metrics.setdefault(node.id, {}).update({
                "latency_ms": node.latency_ms,
                "replication_lag_ms": node.replication_lag_ms,
                "load_percentage": node.load_percentage,
                "timestamp": datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            self.logger.error(f"Failed to handle health update for {node.id}: {e}")
    
    def _handle_node_failure(self, node: DatabaseNode, error: str) -> None:
        """Handle node failure"""
        try:
            node.status = NodeStatus.FAILED
            self._record_node_failure(node)
            
            self.logger.warning(f"Node {node.id} health check failed: {error}")
            
        except Exception as e:
            self.logger.error(f"Failed to handle node failure for {node.id}: {e}")
    
    def _record_node_failure(self, node: DatabaseNode) -> None:
        """Record node failure for failure detection"""
        self.consecutive_failures[node.id] = self.consecutive_failures.get(node.id, 0) + 1
        
        if self.consecutive_failures[node.id] >= self.failure_detection_threshold:
            self._mark_node_failed(node)
    
    def _mark_node_failed(self, node: DatabaseNode) -> None:
        """Mark node as failed and remove from active nodes"""
        if node.id in self.active_nodes:
            del self.active_nodes[node.id]
            self.failed_nodes.add(node.id)
            
            self.logger.error(f"Node {node.id} marked as FAILED after {self.consecutive_failures[node.id]} failures")
            
            # Trigger failover if this was a primary node
            if node.role == NodeRole.PRIMARY:
                asyncio.create_task(self._trigger_failover(node))
    
    async def _trigger_failover(self, failed_node: DatabaseNode) -> None:
        """Trigger failover for failed primary node"""
        try:
            self.logger.critical(f"Triggering failover for failed primary: {failed_node.id}")
            
            # Find best secondary to promote
            candidate = await self._find_failover_candidate(failed_node.database_type)
            
            if candidate:
                await self._promote_secondary_to_primary(candidate, failed_node)
            else:
                self.logger.error(f"No failover candidate found for {failed_node.database_type}")
            
        except Exception as e:
            self.logger.error(f"Failover failed for {failed_node.id}: {e}")
    
    async def _find_failover_candidate(self, database_type: str) -> Optional[DatabaseNode]:
        """Find best secondary node for failover"""
        candidates = [
            node for node in self.active_nodes.values()
            if (node.database_type == database_type and 
                node.role == NodeRole.SECONDARY and
                node.status == NodeStatus.HEALTHY)
        ]
        
        if not candidates:
            return None
        
        # Sort by priority and replication lag
        candidates.sort(key=lambda n: (n.priority, n.replication_lag_ms), reverse=True)
        
        return candidates[0]
    
    async def _promote_secondary_to_primary(self, candidate: DatabaseNode, failed_primary: DatabaseNode) -> None:
        """Promote secondary node to primary"""
        try:
            self.logger.info(f"Promoting {candidate.id} to primary for {failed_primary.database_type}")
            
            # Update node role
            candidate.role = NodeRole.PRIMARY
            candidate.priority = 100
            
            # Update routing cache
            await self._update_routing_cache()
            
            # Notify other systems about the change
            await self._notify_failover_complete(candidate, failed_primary)
            
            self.logger.info(f"Failover completed: {candidate.id} is now primary")
            
        except Exception as e:
            self.logger.error(f"Failed to promote {candidate.id} to primary: {e}")
    
    async def _notify_failover_complete(self, new_primary: DatabaseNode, old_primary: DatabaseNode) -> None:
        """Notify other systems about completed failover"""
        try:
            # This would integrate with the broader system notification mechanism
            notification = {
                "type": "failover_completed",
                "timestamp": datetime.utcnow().isoformat(),
                "database_type": new_primary.database_type,
                "old_primary": {
                    "id": old_primary.id,
                    "host": old_primary.host,
                    "port": old_primary.port
                },
                "new_primary": {
                    "id": new_primary.id,
                    "host": new_primary.host,
                    "port": new_primary.port
                }
            }
            
            self.logger.info(f"Failover notification: {json.dumps(notification)}")
            
        except Exception as e:
            self.logger.error(f"Failed to send failover notification: {e}")
    
    async def _update_performance_metrics(self) -> None:
        """Update topology performance metrics"""
        try:
            # Calculate aggregate metrics
            healthy_nodes = [node for node in self.active_nodes.values() 
                           if node.status == NodeStatus.HEALTHY]
            
            if healthy_nodes:
                avg_latency = sum(node.latency_ms for node in healthy_nodes) / len(healthy_nodes)
                max_replication_lag = max(node.replication_lag_ms for node in healthy_nodes)
                avg_load = sum(node.load_percentage for node in healthy_nodes) / len(healthy_nodes)
                
                # Store aggregate metrics
                self.performance_metrics["topology"] = {
                    "healthy_nodes": len(healthy_nodes),
                    "failed_nodes": len(self.failed_nodes),
                    "average_latency_ms": avg_latency,
                    "max_replication_lag_ms": max_replication_lag,
                    "average_load_percentage": avg_load,
                    "availability_percentage": (len(healthy_nodes) / len(self.topology.nodes)) * 100,
                    "timestamp": datetime.utcnow().isoformat()
                }
            
        except Exception as e:
            self.logger.error(f"Failed to update performance metrics: {e}")
    
    async def _detect_failures(self) -> None:
        """Detect and handle node failures"""
        try:
            current_time = datetime.utcnow()
            
            for node in self.active_nodes.values():
                if node.last_seen:
                    time_since_seen = current_time - node.last_seen
                    
                    # Mark as failed if not seen for too long
                    if time_since_seen > timedelta(minutes=5):
                        self.logger.warning(f"Node {node.id} not seen for {time_since_seen}")
                        self._record_node_failure(node)
            
        except Exception as e:
            self.logger.error(f"Failed to detect failures: {e}")
    
    async def _update_routing_cache(self) -> None:
        """Update routing cache for optimal node selection"""
        try:
            self.routing_cache.clear()
            
            # Build routing cache by database type
            for db_type in ["postgresql", "redis", "mongodb", "elasticsearch", "vector_store"]:
                primary_nodes = [
                    node for node in self.active_nodes.values()
                    if (node.database_type == db_type and 
                        node.role == NodeRole.PRIMARY and
                        node.status == NodeStatus.HEALTHY)
                ]
                
                if primary_nodes:
                    # Select best primary (lowest latency)
                    best_primary = min(primary_nodes, key=lambda n: n.latency_ms)
                    self.routing_cache[f"{db_type}_primary"] = best_primary.id
                
                # Cache read replicas
                read_replicas = [
                    node for node in self.active_nodes.values()
                    if (node.database_type == db_type and 
                        node.role == NodeRole.SECONDARY and
                        node.status == NodeStatus.HEALTHY)
                ]
                
                if read_replicas:
                    # Sort by replication lag and latency
                    read_replicas.sort(key=lambda n: (n.replication_lag_ms, n.latency_ms))
                    self.routing_cache[f"{db_type}_read"] = [n.id for n in read_replicas[:3]]
            
        except Exception as e:
            self.logger.error(f"Failed to update routing cache: {e}")
    
    async def _log_topology_status(self) -> None:
        """Log current topology status"""
        try:
            status_summary = {
                "total_nodes": len(self.topology.nodes),
                "active_nodes": len(self.active_nodes),
                "failed_nodes": len(self.failed_nodes),
                "maintenance_nodes": len(self.maintenance_nodes),
                "primary_regions": [self.topology.primary_region],
                "secondary_regions": self.topology.secondary_regions
            }
            
            # Log every 10 minutes
            if datetime.utcnow().minute % 10 == 0:
                self.logger.info(f"Topology status: {json.dumps(status_summary)}")
            
        except Exception as e:
            self.logger.error(f"Failed to log topology status: {e}")
    
    def get_primary_node(self, database_type: str) -> Optional[DatabaseNode]:
        """
        Get primary node for database type.
        
        Args:
            database_type: Type of database
            
        Returns:
            Primary node or None if not available
        """
        cache_key = f"{database_type}_primary"
        node_id = self.routing_cache.get(cache_key)
        
        if node_id and node_id in self.active_nodes:
            return self.active_nodes[node_id]
        
        return None
    
    def get_read_replica(self, database_type: str, region: Optional[str] = None) -> Optional[DatabaseNode]:
        """
        Get best read replica for database type.
        
        Args:
            database_type: Type of database
            region: Preferred region (optional)
            
        Returns:
            Best read replica node or None if not available
        """
        cache_key = f"{database_type}_read"
        replica_ids = self.routing_cache.get(cache_key, [])
        
        if not replica_ids:
            return None
        
        # Filter by region if specified
        if region:
            region_replicas = [
                self.active_nodes[node_id] for node_id in replica_ids
                if node_id in self.active_nodes and self.active_nodes[node_id].region == region
            ]
            if region_replicas:
                return region_replicas[0]
        
        # Return best available replica
        if replica_ids and replica_ids[0] in self.active_nodes:
            return self.active_nodes[replica_ids[0]]
        
        return None
    
    def get_node_by_id(self, node_id: str) -> Optional[DatabaseNode]:
        """
        Get node by ID.
        
        Args:
            node_id: Node identifier
            
        Returns:
            Database node or None if not found
        """
        return self.topology.nodes.get(node_id)
    
    def get_nodes_by_type(self, database_type: str) -> List[DatabaseNode]:
        """
        Get all nodes for database type.
        
        Args:
            database_type: Type of database
            
        Returns:
            List of database nodes
        """
        return [
            node for node in self.topology.nodes.values()
            if node.database_type == database_type
        ]
    
    def get_nodes_by_region(self, region: str) -> List[DatabaseNode]:
        """
        Get all nodes in region.
        
        Args:
            region: Region name
            
        Returns:
            List of database nodes in region
        """
        return [
            node for node in self.topology.nodes.values()
            if node.region == region
        ]
    
    def get_topology_metrics(self) -> Dict[str, Any]:
        """
        Get comprehensive topology metrics.
        
        Returns:
            Dict containing topology metrics
        """
        return {
            "topology_summary": {
                "total_nodes": len(self.topology.nodes),
                "active_nodes": len(self.active_nodes),
                "failed_nodes": len(self.failed_nodes),
                "maintenance_nodes": len(self.maintenance_nodes)
            },
            "performance_metrics": self.performance_metrics.get("topology", {}),
            "routing_cache": dict(self.routing_cache),
            "failure_counts": dict(self.consecutive_failures),
            "regions": {
                "primary": self.topology.primary_region,
                "secondary": self.topology.secondary_regions
            }
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Get topology health status.
        
        Returns:
            Dict containing health status
        """
        healthy_nodes = [node for node in self.active_nodes.values() 
                        if node.status == NodeStatus.HEALTHY]
        
        # Check if we have primary nodes for critical databases
        critical_primaries = []
        for db_type in ["postgresql", "redis"]:
            primary = self.get_primary_node(db_type)
            if primary:
                critical_primaries.append(db_type)
        
        availability = (len(healthy_nodes) / len(self.topology.nodes)) * 100 if self.topology.nodes else 0
        
        return {
            "healthy": len(critical_primaries) >= 2 and availability >= 80,
            "availability_percentage": availability,
            "healthy_nodes": len(healthy_nodes),
            "total_nodes": len(self.topology.nodes),
            "critical_primaries_available": critical_primaries,
            "failed_nodes": len(self.failed_nodes),
            "issues": self._get_topology_issues()
        }
    
    def _get_topology_issues(self) -> List[str]:
        """Get list of topology issues"""
        issues = []
        
        # Check for failed primary nodes
        for node in self.failed_nodes:
            if node in self.topology.nodes:
                db_node = self.topology.nodes[node]
                if db_node.role == NodeRole.PRIMARY:
                    issues.append(f"Primary node failed: {node}")
        
        # Check for high replication lag
        for node in self.active_nodes.values():
            if node.replication_lag_ms > self.topology.performance_targets.get("max_replication_lag_ms", 1000):
                issues.append(f"High replication lag on {node.id}: {node.replication_lag_ms}ms")
        
        # Check availability
        availability = (len(self.active_nodes) / len(self.topology.nodes)) * 100 if self.topology.nodes else 0
        min_availability = self.topology.performance_targets.get("min_availability_percent", 99.9)
        
        if availability < min_availability:
            issues.append(f"Low availability: {availability:.1f}% (target: {min_availability}%)")
        
        return issues
    
    async def shutdown(self) -> None:
        """Shutdown topology manager"""
        try:
            self.logger.info("Shutting down topology manager...")
            
            # Stop monitoring
            self.is_monitoring = False
            
            if self.monitoring_task:
                self.monitoring_task.cancel()
                try:
                    await self.monitoring_task
                except asyncio.CancelledError:
                    pass
            
            self.logger.info("Topology manager shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Error during topology manager shutdown: {e}")
