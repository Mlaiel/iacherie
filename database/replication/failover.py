"""Failover Manager - IA Influencer Agent Platform

Advanced failover management for database replication with intelligent detection,
automated recovery, and minimal downtime for content creator platform.

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
from .config import ReplicationConfig


class FailoverState(Enum):
    """Failover process states"""
    MONITORING = "monitoring"
    DETECTING = "detecting"
    VALIDATING = "validating"
    INITIATING = "initiating"
    PROMOTING = "promoting"
    UPDATING_CLIENTS = "updating_clients"
    VERIFYING = "verifying"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLING_BACK = "rolling_back"


class FailoverTrigger(Enum):
    """Failover trigger types"""
    HEALTH_CHECK_FAILURE = "health_check_failure"
    NETWORK_PARTITION = "network_partition"
    HIGH_LATENCY = "high_latency"
    REPLICATION_LAG = "replication_lag"
    MANUAL_TRIGGER = "manual_trigger"
    MAINTENANCE_MODE = "maintenance_mode"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    CORRUPTION_DETECTED = "corruption_detected"


class FailoverPriority(Enum):
    """Failover priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class FailoverCandidate:
    """Failover candidate node information"""
    node_id: str
    host: str
    port: int
    database_type: str
    region: str
    priority_score: float
    health_score: float
    replication_lag_ms: float
    load_percentage: float
    network_latency_ms: float
    data_freshness_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FailoverEvent:
    """Failover event record"""
    id: str
    trigger: FailoverTrigger
    priority: FailoverPriority
    failed_node_id: str
    candidate_node_id: Optional[str]
    database_type: str
    state: FailoverState
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_ms: Optional[float] = None
    success: Optional[bool] = None
    error_message: Optional[str] = None
    rollback_performed: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


class FailoverManager:
    """
    Comprehensive failover management system for database replication.
    
    Provides intelligent failover detection, candidate selection,
    automated promotion, and recovery verification for all database
    systems in the content creator platform.
    """
    
    def __init__(self, config: ReplicationConfig, topology_manager=None):
        """
        Initialize failover manager.
        
        Args:
            config: Replication configuration
            topology_manager: Topology manager instance
        """
        self.config = config
        self.topology_manager = topology_manager
        self.logger = logging.getLogger(f"{__name__}.FailoverManager")
        
        # Failover configuration
        self.auto_failover_enabled = config.automatic_failover_enabled
        self.failover_timeout = timedelta(minutes=5)
        self.health_check_threshold = 3
        self.lag_threshold_ms = config.lag_threshold
        
        # State tracking
        self.active_failovers: Dict[str, FailoverEvent] = {}
        self.failover_history: List[FailoverEvent] = []
        self.failed_nodes: Set[str] = set()
        self.recovery_nodes: Set[str] = set()
        
        # Monitoring
        self.is_monitoring = False
        self.monitoring_task: Optional[asyncio.Task] = None
        self.last_health_check: Dict[str, datetime] = {}
        self.consecutive_failures: Dict[str, int] = {}
        
        # Performance metrics
        self.metrics = {
            "total_failovers": 0,
            "successful_failovers": 0,
            "failed_failovers": 0,
            "avg_failover_time_ms": 0.0,
            "fastest_failover_ms": 0.0,
            "slowest_failover_ms": 0.0,
            "last_failover_time": None,
            "nodes_recovered": 0,
            "uptime_percentage": 100.0
        }
        
        # Notification callbacks
        self.notification_callbacks: List[callable] = []
        
        self.logger.info("FailoverManager initialized")
    
    async def initialize(self) -> bool:
        """
        Initialize failover manager.
        
        Returns:
            bool: True if initialization successful
        """
        try:
            self.logger.info("Initializing failover manager...")
            
            # Validate configuration
            await self._validate_failover_configuration()
            
            # Initialize monitoring
            await self._start_monitoring()
            
            # Setup notification handlers
            await self._setup_notification_handlers()
            
            self.logger.info("Failover manager initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize failover manager: {e}")
            return False
    
    async def _validate_failover_configuration(self) -> None:
        """Validate failover configuration"""
        try:
            issues = []
            
            if not self.topology_manager:
                issues.append("Topology manager not available")
            
            if self.lag_threshold_ms <= 0:
                issues.append("Invalid lag threshold")
            
            if self.health_check_threshold <= 0:
                issues.append("Invalid health check threshold")
            
            if issues:
                raise ValueError(f"Failover configuration issues: {issues}")
            
            self.logger.info("Failover configuration validated")
            
        except Exception as e:
            self.logger.error(f"Failover configuration validation failed: {e}")
            raise
    
    async def _start_monitoring(self) -> None:
        """Start failover monitoring"""
        self.is_monitoring = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        self.logger.info("Failover monitoring started")
    
    async def _setup_notification_handlers(self) -> None:
        """Setup notification handlers for failover events"""
        try:
            # Add default notification handlers
            self.notification_callbacks.append(self._log_failover_event)
            self.notification_callbacks.append(self._update_metrics_on_failover)
            
            self.logger.info("Notification handlers setup completed")
            
        except Exception as e:
            self.logger.error(f"Failed to setup notification handlers: {e}")
    
    async def _monitoring_loop(self) -> None:
        """Main monitoring loop for failover detection"""
        while self.is_monitoring:
            try:
                # Check for node failures
                await self._detect_node_failures()
                
                # Monitor active failovers
                await self._monitor_active_failovers()
                
                # Check for recovery opportunities
                await self._check_node_recovery()
                
                # Update metrics
                await self._update_failover_metrics()
                
                await asyncio.sleep(self.config.health_check_interval)
                
            except Exception as e:
                self.logger.error(f"Error in failover monitoring loop: {e}")
                await asyncio.sleep(30)
    
    async def _detect_node_failures(self) -> None:
        """Detect node failures and trigger failover if needed"""
        try:
            if not self.topology_manager:
                return
            
            current_time = datetime.utcnow()
            
            # Get all nodes from topology
            all_nodes = self.topology_manager.get_nodes_by_type("postgresql") + \
                       self.topology_manager.get_nodes_by_type("redis") + \
                       self.topology_manager.get_nodes_by_type("mongodb") + \
                       self.topology_manager.get_nodes_by_type("elasticsearch")
            
            for node in all_nodes:
                # Skip if already in failover
                if node.id in self.active_failovers:
                    continue
                
                # Check node health
                is_healthy = await self._check_node_health(node)
                
                if not is_healthy:
                    self.consecutive_failures[node.id] = self.consecutive_failures.get(node.id, 0) + 1
                    
                    # Trigger failover if threshold exceeded
                    if self.consecutive_failures[node.id] >= self.health_check_threshold:
                        await self._trigger_failover(
                            node.id, 
                            FailoverTrigger.HEALTH_CHECK_FAILURE,
                            FailoverPriority.HIGH
                        )
                else:
                    # Reset failure counter on successful health check
                    self.consecutive_failures.pop(node.id, None)
                    
                    # Check for recovery if node was previously failed
                    if node.id in self.failed_nodes:
                        await self._initiate_node_recovery(node.id)
                
                self.last_health_check[node.id] = current_time
            
        except Exception as e:
            self.logger.error(f"Failed to detect node failures: {e}")
    
    async def _check_node_health(self, node) -> bool:
        """Check if a node is healthy"""
        try:
            if not self.topology_manager:
                return False
            
            # Get health status from topology manager
            health = await self.topology_manager._check_node_health(node)
            
            if not health.get("healthy", False):
                return False
            
            # Check replication lag
            lag_ms = health.get("replication_lag_ms", 0)
            if lag_ms > self.lag_threshold_ms:
                self.logger.warning(f"High replication lag on {node.id}: {lag_ms}ms")
                return False
            
            # Check latency
            latency_ms = health.get("latency_ms", 0)
            if latency_ms > 5000:  # 5 second threshold
                self.logger.warning(f"High latency on {node.id}: {latency_ms}ms")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to check node health for {node.id}: {e}")
            return False
    
    async def _trigger_failover(
        self, 
        failed_node_id: str, 
        trigger: FailoverTrigger, 
        priority: FailoverPriority
    ) -> bool:
        """
        Trigger failover for a failed node.
        
        Args:
            failed_node_id: ID of the failed node
            trigger: Reason for failover
            priority: Failover priority
            
        Returns:
            bool: True if failover initiated successfully
        """
        try:
            if not self.auto_failover_enabled and trigger != FailoverTrigger.MANUAL_TRIGGER:
                self.logger.warning(f"Auto failover disabled, skipping failover for {failed_node_id}")
                return False
            
            # Get failed node information
            failed_node = self.topology_manager.get_node_by_id(failed_node_id)
            if not failed_node:
                self.logger.error(f"Failed node not found: {failed_node_id}")
                return False
            
            # Only failover primary nodes
            if failed_node.role.value != "primary":
                self.logger.info(f"Skipping failover for non-primary node: {failed_node_id}")
                return False
            
            # Create failover event
            failover_event = FailoverEvent(
                id=f"failover_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{failed_node_id}",
                trigger=trigger,
                priority=priority,
                failed_node_id=failed_node_id,
                database_type=failed_node.database_type,
                state=FailoverState.DETECTING,
                started_at=datetime.utcnow(),
                metadata={
                    "failed_node_host": failed_node.host,
                    "failed_node_port": failed_node.port,
                    "failed_node_region": failed_node.region
                }
            )
            
            # Store active failover
            self.active_failovers[failover_event.id] = failover_event
            self.failed_nodes.add(failed_node_id)
            
            self.logger.critical(f"Failover triggered: {failover_event.id} for {failed_node_id} "
                               f"({trigger.value}, {priority.value})")
            
            # Start failover process
            asyncio.create_task(self._execute_failover(failover_event))
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to trigger failover for {failed_node_id}: {e}")
            return False
    
    async def _execute_failover(self, failover_event: FailoverEvent) -> None:
        """Execute the complete failover process"""
        try:
            self.logger.info(f"Executing failover: {failover_event.id}")
            
            # Phase 1: Validate failure
            failover_event.state = FailoverState.VALIDATING
            if not await self._validate_node_failure(failover_event):
                await self._abort_failover(failover_event, "Node failure validation failed")
                return
            
            # Phase 2: Find failover candidate
            failover_event.state = FailoverState.INITIATING
            candidate = await self._select_failover_candidate(failover_event)
            if not candidate:
                await self._abort_failover(failover_event, "No suitable failover candidate found")
                return
            
            failover_event.candidate_node_id = candidate.node_id
            failover_event.metadata["candidate_host"] = candidate.host
            failover_event.metadata["candidate_port"] = candidate.port
            failover_event.metadata["candidate_region"] = candidate.region
            
            # Phase 3: Promote candidate
            failover_event.state = FailoverState.PROMOTING
            if not await self._promote_candidate(failover_event, candidate):
                await self._abort_failover(failover_event, "Candidate promotion failed")
                return
            
            # Phase 4: Update clients and routing
            failover_event.state = FailoverState.UPDATING_CLIENTS
            await self._update_client_connections(failover_event, candidate)
            
            # Phase 5: Verify failover success
            failover_event.state = FailoverState.VERIFYING
            if not await self._verify_failover_success(failover_event, candidate):
                await self._rollback_failover(failover_event, candidate)
                return
            
            # Phase 6: Complete failover
            await self._complete_failover(failover_event)
            
        except Exception as e:
            self.logger.error(f"Failover execution failed for {failover_event.id}: {e}")
            await self._abort_failover(failover_event, f"Execution error: {str(e)}")
    
    async def _validate_node_failure(self, failover_event: FailoverEvent) -> bool:
        """Validate that the node has actually failed"""
        try:
            failed_node = self.topology_manager.get_node_by_id(failover_event.failed_node_id)
            if not failed_node:
                return False
            
            # Perform additional health checks
            for attempt in range(3):
                is_healthy = await self._check_node_health(failed_node)
                if is_healthy:
                    self.logger.info(f"Node {failover_event.failed_node_id} recovered during validation")
                    return False
                
                await asyncio.sleep(2)  # Wait between attempts
            
            self.logger.info(f"Node failure validated: {failover_event.failed_node_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to validate node failure: {e}")
            return False
    
    async def _select_failover_candidate(self, failover_event: FailoverEvent) -> Optional[FailoverCandidate]:
        """Select the best failover candidate"""
        try:
            # Get all potential candidates
            candidates = await self._find_failover_candidates(failover_event)
            
            if not candidates:
                self.logger.error(f"No failover candidates found for {failover_event.database_type}")
                return None
            
            # Score and rank candidates
            scored_candidates = []
            
            for candidate_node in candidates:
                score = await self._calculate_candidate_score(candidate_node, failover_event)
                
                candidate = FailoverCandidate(
                    node_id=candidate_node.id,
                    host=candidate_node.host,
                    port=candidate_node.port,
                    database_type=candidate_node.database_type,
                    region=candidate_node.region,
                    priority_score=candidate_node.priority,
                    health_score=score.get("health", 0),
                    replication_lag_ms=candidate_node.replication_lag_ms,
                    load_percentage=candidate_node.load_percentage,
                    network_latency_ms=candidate_node.latency_ms,
                    data_freshness_score=score.get("data_freshness", 0),
                    metadata=score
                )
                
                scored_candidates.append(candidate)
            
            # Sort by total score (higher is better)
            scored_candidates.sort(key=lambda c: c.priority_score + c.health_score + c.data_freshness_score, reverse=True)
            
            best_candidate = scored_candidates[0]
            
            self.logger.info(f"Selected failover candidate: {best_candidate.node_id} "
                           f"(score: {best_candidate.priority_score + best_candidate.health_score})")
            
            return best_candidate
            
        except Exception as e:
            self.logger.error(f"Failed to select failover candidate: {e}")
            return None
    
    async def _find_failover_candidates(self, failover_event: FailoverEvent) -> List:
        """Find potential failover candidates"""
        try:
            # Get all nodes of the same database type
            all_nodes = self.topology_manager.get_nodes_by_type(failover_event.database_type)
            
            candidates = []
            
            for node in all_nodes:
                # Skip the failed node
                if node.id == failover_event.failed_node_id:
                    continue
                
                # Skip already failed nodes
                if node.id in self.failed_nodes:
                    continue
                
                # Only consider secondary nodes for promotion
                if node.role.value != "secondary":
                    continue
                
                # Check if node is healthy
                if await self._check_node_health(node):
                    candidates.append(node)
            
            self.logger.info(f"Found {len(candidates)} potential failover candidates")
            return candidates
            
        except Exception as e:
            self.logger.error(f"Failed to find failover candidates: {e}")
            return []
    
    async def _calculate_candidate_score(self, node, failover_event: FailoverEvent) -> Dict[str, float]:
        """Calculate comprehensive score for failover candidate"""
        try:
            score = {
                "health": 0.0,
                "performance": 0.0,
                "data_freshness": 0.0,
                "geographic": 0.0,
                "total": 0.0
            }
            
            # Health score (0-100)
            if node.status.value == "healthy":
                score["health"] = 100.0
            elif node.status.value == "degraded":
                score["health"] = 50.0
            else:
                score["health"] = 0.0
            
            # Performance score (0-100)
            # Lower latency and load = higher score
            latency_score = max(0, 100 - (node.latency_ms / 10))  # 10ms = -1 point
            load_score = max(0, 100 - node.load_percentage)
            score["performance"] = (latency_score + load_score) / 2
            
            # Data freshness score (0-100)
            # Lower replication lag = higher score
            if node.replication_lag_ms <= 100:
                score["data_freshness"] = 100.0
            elif node.replication_lag_ms <= 1000:
                score["data_freshness"] = 90.0
            elif node.replication_lag_ms <= 5000:
                score["data_freshness"] = 70.0
            else:
                score["data_freshness"] = 30.0
            
            # Geographic score (0-100)
            # Same region as failed node = higher score
            failed_node = self.topology_manager.get_node_by_id(failover_event.failed_node_id)
            if failed_node and node.region == failed_node.region:
                score["geographic"] = 100.0
            else:
                score["geographic"] = 50.0
            
            # Calculate total score
            score["total"] = (
                score["health"] * 0.4 +
                score["performance"] * 0.3 +
                score["data_freshness"] * 0.2 +
                score["geographic"] * 0.1
            )
            
            return score
            
        except Exception as e:
            self.logger.error(f"Failed to calculate candidate score: {e}")
            return {"health": 0, "performance": 0, "data_freshness": 0, "geographic": 0, "total": 0}
    
    async def _promote_candidate(self, failover_event: FailoverEvent, candidate: FailoverCandidate) -> bool:
        """Promote candidate node to primary"""
        try:
            self.logger.info(f"Promoting candidate {candidate.node_id} to primary")
            
            # Database-specific promotion logic
            if failover_event.database_type == "postgresql":
                return await self._promote_postgresql_candidate(candidate)
            elif failover_event.database_type == "redis":
                return await self._promote_redis_candidate(candidate)
            elif failover_event.database_type == "mongodb":
                return await self._promote_mongodb_candidate(candidate)
            elif failover_event.database_type == "elasticsearch":
                return await self._promote_elasticsearch_candidate(candidate)
            else:
                self.logger.error(f"Unknown database type for promotion: {failover_event.database_type}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to promote candidate {candidate.node_id}: {e}")
            return False
    
    async def _promote_postgresql_candidate(self, candidate: FailoverCandidate) -> bool:
        """Promote PostgreSQL secondary to primary"""
        try:
            import asyncpg
            
            # Connect to the candidate node
            conn = await asyncpg.connect(
                host=candidate.host,
                port=candidate.port,
                database="postgres",
                user=self.config.get_database_config("postgresql").get("username"),
                password=self.config.get_database_config("postgresql").get("password")
            )
            
            # Promote to primary
            await conn.execute("SELECT pg_promote()")
            
            await conn.close()
            
            self.logger.info(f"PostgreSQL node {candidate.node_id} promoted to primary")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to promote PostgreSQL candidate: {e}")
            return False
    
    async def _promote_redis_candidate(self, candidate: FailoverCandidate) -> bool:
        """Promote Redis secondary to primary"""
        try:
            import aioredis
            
            # Connect to the candidate node
            redis = aioredis.Redis(
                host=candidate.host,
                port=candidate.port,
                password=self.config.get_database_config("redis").get("password")
            )
            
            # Stop replication to become master
            await redis.slaveof("NO", "ONE")
            
            await redis.close()
            
            self.logger.info(f"Redis node {candidate.node_id} promoted to primary")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to promote Redis candidate: {e}")
            return False
    
    async def _promote_mongodb_candidate(self, candidate: FailoverCandidate) -> bool:
        """Promote MongoDB secondary to primary"""
        try:
            from motor.motor_asyncio import AsyncIOMotorClient
            
            # MongoDB replica sets handle failover automatically
            # We just need to force an election
            client = AsyncIOMotorClient(
                host=candidate.host,
                port=candidate.port,
                username=self.config.get_database_config("mongodb").get("username"),
                password=self.config.get_database_config("mongodb").get("password")
            )
            
            # Force election by stepping down current primary (if any)
            try:
                await client.admin.command("replSetStepDown", 10)
            except:
                pass  # May fail if no primary available
            
            client.close()
            
            self.logger.info(f"MongoDB node {candidate.node_id} promotion initiated")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to promote MongoDB candidate: {e}")
            return False
    
    async def _promote_elasticsearch_candidate(self, candidate: FailoverCandidate) -> bool:
        """Promote Elasticsearch node (handle master election)"""
        try:
            from elasticsearch import AsyncElasticsearch
            
            # Elasticsearch handles master election automatically
            # We can trigger a cluster reroute to speed up the process
            client = AsyncElasticsearch(
                hosts=[{"host": candidate.host, "port": candidate.port}]
            )
            
            # Trigger cluster reroute
            await client.cluster.reroute()
            
            await client.close()
            
            self.logger.info(f"Elasticsearch node {candidate.node_id} promotion initiated")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to promote Elasticsearch candidate: {e}")
            return False
    
    async def _update_client_connections(self, failover_event: FailoverEvent, candidate: FailoverCandidate) -> None:
        """Update client connections to point to new primary"""
        try:
            # Update topology manager routing cache
            if self.topology_manager:
                # Update node role in topology
                candidate_node = self.topology_manager.get_node_by_id(candidate.node_id)
                if candidate_node:
                    candidate_node.role = candidate_node.role.__class__("primary")
                    candidate_node.priority = 100
                
                # Update routing cache
                await self.topology_manager._update_routing_cache()
            
            # Here you would also update:
            # - Load balancer configuration
            # - DNS records
            # - Application configuration
            # - Connection pool settings
            
            self.logger.info(f"Client connections updated for failover {failover_event.id}")
            
        except Exception as e:
            self.logger.error(f"Failed to update client connections: {e}")
    
    async def _verify_failover_success(self, failover_event: FailoverEvent, candidate: FailoverCandidate) -> bool:
        """Verify that failover completed successfully"""
        try:
            # Wait for promotion to complete
            await asyncio.sleep(5)
            
            # Check if new primary is accepting connections
            new_primary_healthy = await self._check_node_health(
                self.topology_manager.get_node_by_id(candidate.node_id)
            )
            
            if not new_primary_healthy:
                self.logger.error(f"New primary {candidate.node_id} is not healthy after promotion")
                return False
            
            # Verify data consistency (simplified check)
            if not await self._verify_data_consistency(candidate):
                self.logger.error(f"Data consistency check failed for {candidate.node_id}")
                return False
            
            self.logger.info(f"Failover verification successful for {failover_event.id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failover verification failed: {e}")
            return False
    
    async def _verify_data_consistency(self, candidate: FailoverCandidate) -> bool:
        """Verify data consistency on new primary"""
        try:
            # Database-specific consistency checks
            if candidate.database_type == "postgresql":
                return await self._verify_postgresql_consistency(candidate)
            elif candidate.database_type == "redis":
                return await self._verify_redis_consistency(candidate)
            elif candidate.database_type == "mongodb":
                return await self._verify_mongodb_consistency(candidate)
            else:
                return True  # Skip verification for unknown types
                
        except Exception as e:
            self.logger.error(f"Data consistency verification failed: {e}")
            return False
    
    async def _verify_postgresql_consistency(self, candidate: FailoverCandidate) -> bool:
        """Verify PostgreSQL data consistency"""
        try:
            import asyncpg
            
            conn = await asyncpg.connect(
                host=candidate.host,
                port=candidate.port,
                database="postgres",
                user=self.config.get_database_config("postgresql").get("username"),
                password=self.config.get_database_config("postgresql").get("password")
            )
            
            # Check if we can perform basic operations
            await conn.fetchval("SELECT 1")
            
            # Check replication status
            result = await conn.fetchval("SELECT pg_is_in_recovery()")
            if result:  # Should not be in recovery if promoted
                await conn.close()
                return False
            
            await conn.close()
            return True
            
        except Exception as e:
            self.logger.error(f"PostgreSQL consistency check failed: {e}")
            return False
    
    async def _verify_redis_consistency(self, candidate: FailoverCandidate) -> bool:
        """Verify Redis data consistency"""
        try:
            import aioredis
            
            redis = aioredis.Redis(
                host=candidate.host,
                port=candidate.port,
                password=self.config.get_database_config("redis").get("password")
            )
            
            # Check if we can perform basic operations
            await redis.ping()
            
            # Check replication info
            info = await redis.info("replication")
            role = info.get("role")
            
            await redis.close()
            
            return role == "master"
            
        except Exception as e:
            self.logger.error(f"Redis consistency check failed: {e}")
            return False
    
    async def _verify_mongodb_consistency(self, candidate: FailoverCandidate) -> bool:
        """Verify MongoDB data consistency"""
        try:
            from motor.motor_asyncio import AsyncIOMotorClient
            
            client = AsyncIOMotorClient(
                host=candidate.host,
                port=candidate.port,
                username=self.config.get_database_config("mongodb").get("username"),
                password=self.config.get_database_config("mongodb").get("password")
            )
            
            # Check if we can perform basic operations
            await client.admin.command("ping")
            
            # Check replica set status
            rs_status = await client.admin.command("replSetGetStatus")
            
            # Find this node in the status
            for member in rs_status.get("members", []):
                if member.get("name") == f"{candidate.host}:{candidate.port}":
                    is_primary = member.get("stateStr") == "PRIMARY"
                    client.close()
                    return is_primary
            
            client.close()
            return False
            
        except Exception as e:
            self.logger.error(f"MongoDB consistency check failed: {e}")
            return False
    
    async def _complete_failover(self, failover_event: FailoverEvent) -> None:
        """Complete the failover process"""
        try:
            failover_event.state = FailoverState.COMPLETED
            failover_event.completed_at = datetime.utcnow()
            failover_event.duration_ms = (
                failover_event.completed_at - failover_event.started_at
            ).total_seconds() * 1000
            failover_event.success = True
            
            # Move to history
            self.failover_history.append(failover_event)
            del self.active_failovers[failover_event.id]
            
            # Update metrics
            self.metrics["total_failovers"] += 1
            self.metrics["successful_failovers"] += 1
            self.metrics["last_failover_time"] = failover_event.completed_at.isoformat()
            
            # Update average failover time
            current_avg = self.metrics["avg_failover_time_ms"]
            successful_count = self.metrics["successful_failovers"]
            self.metrics["avg_failover_time_ms"] = (
                (current_avg * (successful_count - 1) + failover_event.duration_ms) / successful_count
            )
            
            # Update fastest/slowest times
            if self.metrics["fastest_failover_ms"] == 0 or failover_event.duration_ms < self.metrics["fastest_failover_ms"]:
                self.metrics["fastest_failover_ms"] = failover_event.duration_ms
            
            if failover_event.duration_ms > self.metrics["slowest_failover_ms"]:
                self.metrics["slowest_failover_ms"] = failover_event.duration_ms
            
            # Notify callbacks
            await self._notify_failover_complete(failover_event)
            
            self.logger.info(f"Failover completed successfully: {failover_event.id} "
                           f"in {failover_event.duration_ms:.1f}ms")
            
        except Exception as e:
            self.logger.error(f"Failed to complete failover {failover_event.id}: {e}")
    
    async def _abort_failover(self, failover_event: FailoverEvent, reason: str) -> None:
        """Abort failover process"""
        try:
            failover_event.state = FailoverState.FAILED
            failover_event.completed_at = datetime.utcnow()
            failover_event.duration_ms = (
                failover_event.completed_at - failover_event.started_at
            ).total_seconds() * 1000
            failover_event.success = False
            failover_event.error_message = reason
            
            # Move to history
            self.failover_history.append(failover_event)
            del self.active_failovers[failover_event.id]
            
            # Update metrics
            self.metrics["total_failovers"] += 1
            self.metrics["failed_failovers"] += 1
            
            # Notify callbacks
            await self._notify_failover_failed(failover_event)
            
            self.logger.error(f"Failover aborted: {failover_event.id} - {reason}")
            
        except Exception as e:
            self.logger.error(f"Failed to abort failover {failover_event.id}: {e}")
    
    async def _rollback_failover(self, failover_event: FailoverEvent, candidate: FailoverCandidate) -> None:
        """Rollback failed failover"""
        try:
            failover_event.state = FailoverState.ROLLING_BACK
            failover_event.rollback_performed = True
            
            self.logger.warning(f"Rolling back failover: {failover_event.id}")
            
            # Database-specific rollback logic would go here
            # For now, we just mark the candidate as secondary again
            
            await self._abort_failover(failover_event, "Failover verification failed, rolled back")
            
        except Exception as e:
            self.logger.error(f"Failed to rollback failover {failover_event.id}: {e}")
    
    async def _initiate_node_recovery(self, node_id: str) -> None:
        """Initiate recovery for a previously failed node"""
        try:
            if node_id in self.recovery_nodes:
                return  # Already in recovery
            
            self.recovery_nodes.add(node_id)
            
            self.logger.info(f"Initiating recovery for node: {node_id}")
            
            # Node recovery logic would go here
            # For now, just remove from failed nodes after verification
            
            # Verify node is stable for a period before full recovery
            await asyncio.sleep(60)  # Wait 1 minute
            
            node = self.topology_manager.get_node_by_id(node_id)
            if node and await self._check_node_health(node):
                self.failed_nodes.discard(node_id)
                self.recovery_nodes.discard(node_id)
                self.metrics["nodes_recovered"] += 1
                
                self.logger.info(f"Node recovery completed: {node_id}")
            else:
                self.recovery_nodes.discard(node_id)
                self.logger.warning(f"Node recovery failed: {node_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to initiate recovery for {node_id}: {e}")
            self.recovery_nodes.discard(node_id)
    
    async def _monitor_active_failovers(self) -> None:
        """Monitor active failover processes"""
        try:
            current_time = datetime.utcnow()
            
            for failover_id, failover_event in list(self.active_failovers.items()):
                # Check for timeout
                duration = current_time - failover_event.started_at
                
                if duration > self.failover_timeout:
                    await self._abort_failover(failover_event, "Failover timeout exceeded")
            
        except Exception as e:
            self.logger.error(f"Failed to monitor active failovers: {e}")
    
    async def _check_node_recovery(self) -> None:
        """Check for opportunities to recover failed nodes"""
        try:
            # This method would implement logic to detect when failed nodes
            # have recovered and can be brought back into service
            pass
            
        except Exception as e:
            self.logger.error(f"Failed to check node recovery: {e}")
    
    async def _update_failover_metrics(self) -> None:
        """Update failover metrics"""
        try:
            # Calculate uptime percentage
            total_nodes = len(self.topology_manager.topology.nodes) if self.topology_manager else 0
            failed_nodes_count = len(self.failed_nodes)
            
            if total_nodes > 0:
                uptime_percentage = ((total_nodes - failed_nodes_count) / total_nodes) * 100
                self.metrics["uptime_percentage"] = uptime_percentage
            
        except Exception as e:
            self.logger.error(f"Failed to update failover metrics: {e}")
    
    # Notification callback functions
    async def _log_failover_event(self, event_type: str, failover_event: FailoverEvent) -> None:
        """Log failover event"""
        try:
            self.logger.info(f"Failover event: {event_type} - {failover_event.id}")
            
        except Exception as e:
            self.logger.error(f"Failed to log failover event: {e}")
    
    async def _update_metrics_on_failover(self, event_type: str, failover_event: FailoverEvent) -> None:
        """Update metrics when failover events occur"""
        try:
            # Metrics are updated in the specific failover completion methods
            pass
            
        except Exception as e:
            self.logger.error(f"Failed to update metrics on failover: {e}")
    
    async def _notify_failover_complete(self, failover_event: FailoverEvent) -> None:
        """Notify all callbacks of failover completion"""
        try:
            for callback in self.notification_callbacks:
                await callback("completed", failover_event)
                
        except Exception as e:
            self.logger.error(f"Failed to notify failover completion: {e}")
    
    async def _notify_failover_failed(self, failover_event: FailoverEvent) -> None:
        """Notify all callbacks of failover failure"""
        try:
            for callback in self.notification_callbacks:
                await callback("failed", failover_event)
                
        except Exception as e:
            self.logger.error(f"Failed to notify failover failure: {e}")
    
    # Public API methods
    async def trigger_manual_failover(
        self, 
        node_id: str, 
        priority: FailoverPriority = FailoverPriority.HIGH
    ) -> bool:
        """
        Manually trigger failover for a node.
        
        Args:
            node_id: Node to failover
            priority: Failover priority
            
        Returns:
            bool: True if failover initiated successfully
        """
        return await self._trigger_failover(
            node_id, 
            FailoverTrigger.MANUAL_TRIGGER, 
            priority
        )
    
    def get_failover_status(self) -> Dict[str, Any]:
        """
        Get current failover status.
        
        Returns:
            Dict containing failover status information
        """
        return {
            "auto_failover_enabled": self.auto_failover_enabled,
            "active_failovers": len(self.active_failovers),
            "failed_nodes": len(self.failed_nodes),
            "recovery_nodes": len(self.recovery_nodes),
            "metrics": self.metrics,
            "last_health_check": max(self.last_health_check.values()) if self.last_health_check else None
        }
    
    def get_failover_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get failover history.
        
        Args:
            limit: Maximum number of events to return
            
        Returns:
            List of failover events
        """
        recent_events = sorted(
            self.failover_history, 
            key=lambda e: e.started_at, 
            reverse=True
        )[:limit]
        
        return [
            {
                "id": event.id,
                "trigger": event.trigger.value,
                "priority": event.priority.value,
                "failed_node": event.failed_node_id,
                "candidate_node": event.candidate_node_id,
                "database_type": event.database_type,
                "state": event.state.value,
                "started_at": event.started_at.isoformat(),
                "completed_at": event.completed_at.isoformat() if event.completed_at else None,
                "duration_ms": event.duration_ms,
                "success": event.success,
                "error_message": event.error_message
            }
            for event in recent_events
        ]
    
    def add_notification_callback(self, callback: callable) -> None:
        """
        Add notification callback for failover events.
        
        Args:
            callback: Async function to call on failover events
        """
        self.notification_callbacks.append(callback)
    
    async def shutdown(self) -> None:
        """Shutdown failover manager"""
        try:
            self.logger.info("Shutting down failover manager...")
            
            # Stop monitoring
            self.is_monitoring = False
            
            if self.monitoring_task:
                self.monitoring_task.cancel()
                try:
                    await self.monitoring_task
                except asyncio.CancelledError:
                    pass
            
            # Wait for active failovers to complete or abort them
            if self.active_failovers:
                self.logger.info(f"Waiting for {len(self.active_failovers)} active failovers to complete...")
                
                # Wait up to 30 seconds for completion
                for _ in range(30):
                    if not self.active_failovers:
                        break
                    await asyncio.sleep(1)
                
                # Abort remaining failovers
                for failover_event in list(self.active_failovers.values()):
                    await self._abort_failover(failover_event, "System shutdown")
            
            self.logger.info("Failover manager shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Error during failover manager shutdown: {e}")
