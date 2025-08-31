"""Failover Manager for Load Balancer - IA Influencer Agent Platform

Advanced failover management system providing automatic failover detection,
orchestration, and recovery for high availability across all services.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ WARNING: This code is proprietary and confidential.
Unauthorized copying, distribution, or use without explicit written
permission from Fahed Mlaiel is strictly prohibited and may result
in legal action.
"""import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import socket
import subprocess
import psutil
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class FailoverTrigger(Enum):
    """Failover trigger types"""    HEALTH_CHECK_FAILURE = "health_check_failure"
    HIGH_ERROR_RATE = "high_error_rate"
    HIGH_RESPONSE_TIME = "high_response_time"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    MANUAL_TRIGGER = "manual_trigger"
    CASCADING_FAILURE = "cascading_failure"
    MAINTENANCE_MODE = "maintenance_mode"


class FailoverStrategy(Enum):
    """Failover strategies"""    IMMEDIATE = "immediate"
    GRADUAL = "gradual"
    CIRCUIT_BREAKER = "circuit_breaker"
    ROLLING = "rolling"
    BLUE_GREEN = "blue_green"


class NodeStatus(Enum):
    """Node status enumeration"""    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    FAILED = "failed"
    MAINTENANCE = "maintenance"
    RECOVERING = "recovering"


@dataclass
class ServiceNode:
    """Service node configuration"""    id: str
    service_name: str
    host: str
    port: int
    weight: float = 1.0
    status: NodeStatus = NodeStatus.HEALTHY
    health_score: float = 1.0
    last_health_check: Optional[datetime] = None
    consecutive_failures: int = 0
    failure_threshold: int = 3
    recovery_threshold: int = 2
    consecutive_successes: int = 0
    total_requests: int = 0
    failed_requests: int = 0
    avg_response_time: float = 0.0
    last_failure_time: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FailoverEvent:
    """Failover event record"""    id: str
    trigger: FailoverTrigger
    strategy: FailoverStrategy
    source_node: str
    target_nodes: List[str]
    service_name: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    success: bool = False
    error_message: Optional[str] = None
    affected_users: int = 0
    recovery_time_seconds: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class FailoverManager:
    """    Enterprise Failover Manager for Load Balancer
    
    Provides comprehensive failover management with automatic detection,
    intelligent failover strategies, and recovery orchestration for the
    IA Influencer Agent platform's microservices.
    """    
    def __init__(self, check_interval: int = 30):
        self.check_interval = check_interval
        
        # Node management
        self.service_nodes: Dict[str, ServiceNode] = {}
        self.service_groups: Dict[str, List[str]] = defaultdict(list)
        self.primary_nodes: Dict[str, str] = {}  # service -> primary node
        
        # Failover state
        self.active_failovers: Dict[str, FailoverEvent] = {}
        self.failover_history: deque = deque(maxlen=1000)
        self.blacklisted_nodes: Set[str] = set()
        self.maintenance_nodes: Set[str] = set()
        
        # Configuration
        self.global_failure_threshold = 5
        self.recovery_timeout = 300  # 5 minutes
        self.cascade_detection_window = 60  # 1 minute
        self.max_concurrent_failovers = 3
        
        # Monitoring
        self.is_monitoring = False
        self.monitor_task = None
        self.cascade_detector_task = None
        
        # Metrics
        self.total_failovers = 0
        self.successful_failovers = 0
        self.failed_failovers = 0
        self.avg_recovery_time = 0.0
        
        logger.info("Failover Manager initialized")
    
    async def initialize(self) -> None:
        """Initialize failover manager"""        try:
            logger.info("Initializing Failover Manager...")
            
            # Initialize service nodes
            await self._initialize_service_nodes()
            
            # Configure failover strategies
            await self._configure_failover_strategies()
            
            # Load historical data
            await self._load_historical_data()
            
            logger.info("Failover Manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Failover Manager: {e}")
            raise
    
    async def _initialize_service_nodes(self) -> None:
        """Initialize service nodes for IA Influencer platform"""        services_config = {
            "fingerprinting": {"instances": 3, "port_base": 8001},
            "protection": {"instances": 2, "port_base": 8002},
            "monetization": {"instances": 2, "port_base": 8003},
            "ai_agent": {"instances": 2, "port_base": 8004},
            "crawlers": {"instances": 2, "port_base": 8005}
        }
        
        for service_name, config in services_config.items():
            for i in range(config["instances"]):
                node_id = f"{service_name}_{i+1}"
                port = config["port_base"] + i
                
                node = ServiceNode(
                    id=node_id,
                    service_name=service_name,
                    host="localhost",
                    port=port,
                    weight=1.0,
                    failure_threshold=3 if service_name != "fingerprinting" else 5,  # Higher threshold for intensive service
                    recovery_threshold=2
                )
                
                self.service_nodes[node_id] = node
                self.service_groups[service_name].append(node_id)
                
                # Set primary node (first instance)
                if i == 0:
                    self.primary_nodes[service_name] = node_id
        
        logger.info(f"Initialized {len(self.service_nodes)} service nodes across {len(services_config)} services")
    
    async def _configure_failover_strategies(self) -> None:
        """Configure failover strategies per service"""        # Service-specific failover strategies
        self.service_strategies = {
            "fingerprinting": FailoverStrategy.GRADUAL,  # CPU intensive, gradual failover
            "protection": FailoverStrategy.IMMEDIATE,   # Critical for security
            "monetization": FailoverStrategy.CIRCUIT_BREAKER,  # Financial transactions
            "ai_agent": FailoverStrategy.ROLLING,       # Maintain user context
            "crawlers": FailoverStrategy.IMMEDIATE      # Can handle quick switches
        }
        
        logger.info("Failover strategies configured")
    
    async def _load_historical_data(self) -> None:
        """Load historical failover data"""        try:
            # Try to load from file
            data_file = "/var/lib/ia-influencer/failover_history.json"
            try:
                with open(data_file, 'r') as f:
                    data = json.load(f)
                
                # Load metrics
                self.total_failovers = data.get("total_failovers", 0)
                self.successful_failovers = data.get("successful_failovers", 0)
                self.failed_failovers = data.get("failed_failovers", 0)
                self.avg_recovery_time = data.get("avg_recovery_time", 0.0)
                
                logger.info("Loaded historical failover data")
                
            except FileNotFoundError:
                logger.info("No historical data found, starting fresh")
            except Exception as e:
                logger.warning(f"Failed to load historical data: {e}")
                
        except Exception as e:
            logger.error(f"Error loading historical data: {e}")
    
    async def start_monitoring(self) -> None:
        """Start failover monitoring"""        if self.is_monitoring:
            logger.warning("Failover monitoring already running")
            return
        
        self.is_monitoring = True
        self.monitor_task = asyncio.create_task(self._monitoring_loop())
        self.cascade_detector_task = asyncio.create_task(self._cascade_detection_loop())
        
        logger.info("Failover monitoring started")
    
    async def stop_monitoring(self) -> None:
        """Stop failover monitoring"""        self.is_monitoring = False
        
        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass
        
        if self.cascade_detector_task:
            self.cascade_detector_task.cancel()
            try:
                await self.cascade_detector_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Failover monitoring stopped")
    
    async def _monitoring_loop(self) -> None:
        """Main monitoring loop"""        while self.is_monitoring:
            try:
                # Check health of all nodes
                await self._check_all_nodes_health()
                
                # Detect and trigger failovers
                await self._detect_and_trigger_failovers()
                
                # Check for node recovery
                await self._check_node_recovery()
                
                # Update failover events
                await self._update_active_failovers()
                
                # Sleep for check interval
                await asyncio.sleep(self.check_interval)
                
            except Exception as e:
                logger.error(f"Error in failover monitoring loop: {e}")
                await asyncio.sleep(self.check_interval)
    
    async def _cascade_detection_loop(self) -> None:
        """Cascade failure detection loop"""        while self.is_monitoring:
            try:
                await self._detect_cascade_failures()
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in cascade detection loop: {e}")
                await asyncio.sleep(30)
    
    async def _check_all_nodes_health(self) -> None:
        """Check health of all service nodes"""        for node_id, node in self.service_nodes.items():
            if node_id in self.maintenance_nodes:
                continue
            
            try:
                is_healthy = await self._check_node_health(node)
                await self._update_node_status(node, is_healthy)
                
            except Exception as e:
                logger.error(f"Health check failed for node {node_id}: {e}")
                await self._update_node_status(node, False)
    
    async def _check_node_health(self, node: ServiceNode) -> bool:
        """Check health of a single node"""        try:
            # TCP connection test
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((node.host, node.port))
            sock.close()
            
            if result != 0:
                return False
            
            # HTTP health check (if available)
            try:
                import aiohttp
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                    url = f"http://{node.host}:{node.port}/health"
                    async with session.get(url) as response:
                        if response.status == 200:
                            # Update response time
                            node.avg_response_time = response.headers.get('X-Response-Time', 0.0)
                            return True
                        else:
                            return False
            except Exception:
                # If HTTP check fails but TCP works, consider it degraded but functional
                return True
            
        except Exception as e:
            logger.debug(f"Health check error for {node.id}: {e}")
            return False
    
    async def _update_node_status(self, node: ServiceNode, is_healthy: bool) -> None:
        """Update node status based on health check"""        node.last_health_check = datetime.now()
        
        if is_healthy:
            node.consecutive_successes += 1
            node.consecutive_failures = 0
            
            # Check for recovery
            if (node.status in [NodeStatus.UNHEALTHY, NodeStatus.FAILED, NodeStatus.DEGRADED] and
                node.consecutive_successes >= node.recovery_threshold):
                
                old_status = node.status
                node.status = NodeStatus.HEALTHY
                node.health_score = 1.0
                
                # Remove from blacklist
                self.blacklisted_nodes.discard(node.id)
                
                logger.info(f"Node {node.id} recovered: {old_status.value} -> {node.status.value}")
        else:
            node.consecutive_failures += 1
            node.consecutive_successes = 0
            node.failed_requests += 1
            node.last_failure_time = datetime.now()
            
            # Update status based on failure count
            if node.consecutive_failures >= node.failure_threshold:
                if node.status != NodeStatus.FAILED:
                    old_status = node.status
                    node.status = NodeStatus.FAILED
                    node.health_score = 0.0
                    
                    # Add to blacklist
                    self.blacklisted_nodes.add(node.id)
                    
                    logger.warning(f"Node {node.id} marked as failed: {old_status.value} -> {node.status.value}")
            elif node.consecutive_failures >= 1:
                if node.status == NodeStatus.HEALTHY:
                    node.status = NodeStatus.DEGRADED
                    node.health_score = 0.5
                    logger.info(f"Node {node.id} marked as degraded")
    
    async def _detect_and_trigger_failovers(self) -> None:
        """Detect conditions requiring failover and trigger them"""        for service_name, node_ids in self.service_groups.items():
            # Count healthy nodes
            healthy_nodes = [
                node_id for node_id in node_ids
                if (self.service_nodes[node_id].status == NodeStatus.HEALTHY and
                    node_id not in self.blacklisted_nodes)
            ]
            
            failed_nodes = [
                node_id for node_id in node_ids
                if self.service_nodes[node_id].status == NodeStatus.FAILED
            ]
            
            # Check if primary node failed
            primary_node_id = self.primary_nodes.get(service_name)
            if primary_node_id and primary_node_id in failed_nodes:
                await self._trigger_failover(
                    service_name=service_name,
                    failed_node=primary_node_id,
                    trigger=FailoverTrigger.HEALTH_CHECK_FAILURE,
                    available_nodes=healthy_nodes
                )
            
            # Check for service degradation (less than 50% nodes healthy)
            total_nodes = len(node_ids)
            healthy_ratio = len(healthy_nodes) / total_nodes if total_nodes > 0 else 0
            
            if healthy_ratio < 0.5 and len(failed_nodes) > 0:
                logger.warning(f"Service {service_name} degraded: {len(healthy_nodes)}/{total_nodes} nodes healthy")
                
                # Trigger failover for failed nodes
                for failed_node in failed_nodes:
                    if failed_node not in self.active_failovers:
                        await self._trigger_failover(
                            service_name=service_name,
                            failed_node=failed_node,
                            trigger=FailoverTrigger.CASCADING_FAILURE,
                            available_nodes=healthy_nodes
                        )
    
    async def _trigger_failover(self, service_name: str, failed_node: str,
                              trigger: FailoverTrigger, available_nodes: List[str]) -> bool:
        """Trigger failover for a failed node"""        try:
            # Check if we can handle more failovers
            if len(self.active_failovers) >= self.max_concurrent_failovers:
                logger.warning("Maximum concurrent failovers reached, queuing...")
                return False
            
            # Select target nodes for failover
            target_nodes = await self._select_target_nodes(service_name, available_nodes)
            
            if not target_nodes:
                logger.error(f"No available target nodes for failover of {failed_node}")
                return False
            
            # Get failover strategy
            strategy = self.service_strategies.get(service_name, FailoverStrategy.IMMEDIATE)
            
            # Create failover event
            failover_event = FailoverEvent(
                id=f"failover_{int(time.time())}_{failed_node}",
                trigger=trigger,
                strategy=strategy,
                source_node=failed_node,
                target_nodes=target_nodes,
                service_name=service_name,
                started_at=datetime.now()
            )
            
            # Execute failover
            success = await self._execute_failover(failover_event)
            
            # Update event
            failover_event.completed_at = datetime.now()
            failover_event.success = success
            failover_event.recovery_time_seconds = (
                failover_event.completed_at - failover_event.started_at
            ).total_seconds()
            
            # Store event
            self.active_failovers[failover_event.id] = failover_event
            self.failover_history.append(failover_event)
            
            # Update metrics
            self.total_failovers += 1
            if success:
                self.successful_failovers += 1
                
                # Update primary node if needed
                if failed_node == self.primary_nodes.get(service_name):
                    self.primary_nodes[service_name] = target_nodes[0]
                    logger.info(f"Primary node for {service_name} changed to {target_nodes[0]}")
            else:
                self.failed_failovers += 1
            
            # Update average recovery time
            if self.total_failovers > 0:
                total_time = sum(
                    event.recovery_time_seconds for event in self.failover_history
                    if event.success and event.recovery_time_seconds > 0
                )
                self.avg_recovery_time = total_time / self.successful_failovers if self.successful_failovers > 0 else 0
            
            logger.info(f"Failover {'succeeded' if success else 'failed'} for {failed_node} -> {target_nodes}")
            return success
            
        except Exception as e:
            logger.error(f"Failed to trigger failover for {failed_node}: {e}")
            return False
    
    async def _select_target_nodes(self, service_name: str, available_nodes: List[str]) -> List[str]:
        """Select target nodes for failover"""        if not available_nodes:
            return []
        
        # Sort nodes by health score and load
        node_scores = []
        for node_id in available_nodes:
            node = self.service_nodes[node_id]
            
            # Calculate score based on health, load, and response time
            load_factor = 1.0 - (node.total_requests / max(node.total_requests + 1, 1000))
            response_factor = 1.0 / max(node.avg_response_time, 0.1)
            
            score = node.health_score * load_factor * response_factor
            node_scores.append((node_id, score))
        
        # Sort by score (highest first)
        node_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Return top nodes (at least 1, up to 2 for redundancy)
        return [node_id for node_id, _ in node_scores[:min(2, len(node_scores))]]
    
    async def _execute_failover(self, failover_event: FailoverEvent) -> bool:
        """Execute the actual failover"""        try:
            strategy = failover_event.strategy
            
            if strategy == FailoverStrategy.IMMEDIATE:
                return await self._execute_immediate_failover(failover_event)
            elif strategy == FailoverStrategy.GRADUAL:
                return await self._execute_gradual_failover(failover_event)
            elif strategy == FailoverStrategy.CIRCUIT_BREAKER:
                return await self._execute_circuit_breaker_failover(failover_event)
            elif strategy == FailoverStrategy.ROLLING:
                return await self._execute_rolling_failover(failover_event)
            else:
                # Default to immediate
                return await self._execute_immediate_failover(failover_event)
                
        except Exception as e:
            logger.error(f"Failed to execute failover {failover_event.id}: {e}")
            failover_event.error_message = str(e)
            return False
    
    async def _execute_immediate_failover(self, failover_event: FailoverEvent) -> bool:
        """Execute immediate failover"""        try:
            # Immediately redirect traffic to target nodes
            # This would integrate with load balancer configuration
            
            logger.info(f"Executing immediate failover: {failover_event.source_node} -> {failover_event.target_nodes}")
            
            # Simulate configuration update
            await asyncio.sleep(0.1)
            
            # Update node weights (simulation)
            source_node = self.service_nodes.get(failover_event.source_node)
            if source_node:
                source_node.weight = 0.0  # Remove from rotation
            
            for target_node_id in failover_event.target_nodes:
                target_node = self.service_nodes.get(target_node_id)
                if target_node:
                    target_node.weight = min(target_node.weight * 1.5, 2.0)  # Increase weight
            
            return True
            
        except Exception as e:
            logger.error(f"Immediate failover failed: {e}")
            return False
    
    async def _execute_gradual_failover(self, failover_event: FailoverEvent) -> bool:
        """Execute gradual failover (drain connections)"""        try:
            logger.info(f"Executing gradual failover: {failover_event.source_node} -> {failover_event.target_nodes}")
            
            # Gradually reduce weight of failed node
            source_node = self.service_nodes.get(failover_event.source_node)
            if source_node:
                for i in range(10):  # 10 steps
                    source_node.weight = max(0.0, source_node.weight - 0.1)
                    await asyncio.sleep(0.5)  # 5 second drain period
                
                source_node.weight = 0.0
            
            # Gradually increase weight of target nodes
            for target_node_id in failover_event.target_nodes:
                target_node = self.service_nodes.get(target_node_id)
                if target_node:
                    target_node.weight = min(target_node.weight * 1.3, 2.0)
            
            return True
            
        except Exception as e:
            logger.error(f"Gradual failover failed: {e}")
            return False
    
    async def _execute_circuit_breaker_failover(self, failover_event: FailoverEvent) -> bool:
        """Execute circuit breaker style failover"""        try:
            logger.info(f"Executing circuit breaker failover: {failover_event.source_node}")
            
            # Open circuit for failed node
            source_node = self.service_nodes.get(failover_event.source_node)
            if source_node:
                source_node.weight = 0.0
                source_node.metadata["circuit_open"] = True
                source_node.metadata["circuit_open_time"] = datetime.now()
            
            # Distribute load to target nodes
            for target_node_id in failover_event.target_nodes:
                target_node = self.service_nodes.get(target_node_id)
                if target_node:
                    target_node.weight = min(target_node.weight * 1.2, 2.0)
            
            return True
            
        except Exception as e:
            logger.error(f"Circuit breaker failover failed: {e}")
            return False
    
    async def _execute_rolling_failover(self, failover_event: FailoverEvent) -> bool:
        """Execute rolling failover (for maintaining state)"""        try:
            logger.info(f"Executing rolling failover: {failover_event.source_node}")
            
            # Mark node for rolling replacement
            source_node = self.service_nodes.get(failover_event.source_node)
            if source_node:
                source_node.metadata["rolling_replacement"] = True
                # Gradually reduce weight but don't immediately drop to 0
                source_node.weight = max(0.1, source_node.weight * 0.5)
            
            # Prepare target nodes
            for target_node_id in failover_event.target_nodes:
                target_node = self.service_nodes.get(target_node_id)
                if target_node:
                    target_node.weight = min(target_node.weight * 1.1, 2.0)
            
            return True
            
        except Exception as e:
            logger.error(f"Rolling failover failed: {e}")
            return False
    
    async def _check_node_recovery(self) -> None:
        """Check for node recovery and restore them"""        for node_id in list(self.blacklisted_nodes):
            node = self.service_nodes.get(node_id)
            if not node:
                continue
            
            if node.status == NodeStatus.HEALTHY:
                # Node has recovered, restore it
                await self._restore_node(node)
    
    async def _restore_node(self, node: ServiceNode) -> None:
        """Restore a recovered node to service"""        try:
            logger.info(f"Restoring node {node.id} to service")
            
            # Remove from blacklist
            self.blacklisted_nodes.discard(node.id)
            
            # Restore weight gradually
            node.weight = 0.5  # Start with reduced load
            
            # Reset failure counters
            node.consecutive_failures = 0
            node.consecutive_successes = 0
            
            # Mark recovery metadata
            node.metadata["last_recovery"] = datetime.now()
            
            logger.info(f"Node {node.id} restored to service")
            
        except Exception as e:
            logger.error(f"Failed to restore node {node.id}: {e}")
    
    async def _update_active_failovers(self) -> None:
        """Update and cleanup active failover events"""        completed_failovers = []
        
        for failover_id, failover_event in self.active_failovers.items():
            # Check if failover has timed out
            if failover_event.completed_at is None:
                duration = (datetime.now() - failover_event.started_at).total_seconds()
                if duration > self.recovery_timeout:
                    failover_event.completed_at = datetime.now()
                    failover_event.success = False
                    failover_event.error_message = "Failover timed out"
                    completed_failovers.append(failover_id)
            else:
                # Remove completed failovers after some time
                if (datetime.now() - failover_event.completed_at).total_seconds() > 300:  # 5 minutes
                    completed_failovers.append(failover_id)
        
        # Remove completed failovers
        for failover_id in completed_failovers:
            self.active_failovers.pop(failover_id, None)
    
    async def _detect_cascade_failures(self) -> None:
        """Detect potential cascade failures"""        try:
            # Look for multiple failures in short time window
            recent_failures = [
                event for event in self.failover_history
                if (datetime.now() - event.started_at).total_seconds() < self.cascade_detection_window
            ]
            
            if len(recent_failures) >= 3:  # 3 or more failures in 1 minute
                logger.warning(f"Potential cascade failure detected: {len(recent_failures)} failures in {self.cascade_detection_window}s")
                
                # Implement cascade prevention measures
                await self._prevent_cascade_failure()
            
        except Exception as e:
            logger.error(f"Error in cascade detection: {e}")
    
    async def _prevent_cascade_failure(self) -> None:
        """Implement cascade failure prevention measures"""        try:
            logger.info("Implementing cascade failure prevention measures")
            
            # Temporarily increase failure thresholds
            for node in self.service_nodes.values():
                if node.failure_threshold < 10:
                    node.failure_threshold += 2
            
            # Reduce check frequency temporarily
            original_interval = self.check_interval
            self.check_interval = min(self.check_interval * 2, 120)  # Max 2 minutes
            
            # Reset after 10 minutes
            async def reset_cascade_prevention():
                await asyncio.sleep(600)  # 10 minutes
                for node in self.service_nodes.values():
                    node.failure_threshold = max(node.failure_threshold - 2, 3)
                self.check_interval = original_interval
                logger.info("Cascade prevention measures reset")
            
            asyncio.create_task(reset_cascade_prevention())
            
        except Exception as e:
            logger.error(f"Failed to prevent cascade failure: {e}")
    
    async def manual_failover(self, source_node: str, target_nodes: List[str] = None) -> bool:
        """Manually trigger failover"""        try:
            node = self.service_nodes.get(source_node)
            if not node:
                logger.error(f"Node {source_node} not found")
                return False
            
            # Get available nodes if not specified
            if not target_nodes:
                available_nodes = [
                    node_id for node_id in self.service_groups[node.service_name]
                    if (self.service_nodes[node_id].status == NodeStatus.HEALTHY and
                        node_id != source_node and
                        node_id not in self.blacklisted_nodes)
                ]
                target_nodes = await self._select_target_nodes(node.service_name, available_nodes)
            
            return await self._trigger_failover(
                service_name=node.service_name,
                failed_node=source_node,
                trigger=FailoverTrigger.MANUAL_TRIGGER,
                available_nodes=target_nodes
            )
            
        except Exception as e:
            logger.error(f"Manual failover failed: {e}")
            return False
    
    async def set_maintenance_mode(self, node_id: str, maintenance: bool = True) -> bool:
        """Set node maintenance mode"""        try:
            node = self.service_nodes.get(node_id)
            if not node:
                return False
            
            if maintenance:
                self.maintenance_nodes.add(node_id)
                node.status = NodeStatus.MAINTENANCE
                node.weight = 0.0
                logger.info(f"Node {node_id} set to maintenance mode")
            else:
                self.maintenance_nodes.discard(node_id)
                node.status = NodeStatus.HEALTHY
                node.weight = 1.0
                logger.info(f"Node {node_id} removed from maintenance mode")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to set maintenance mode for {node_id}: {e}")
            return False
    
    async def get_failover_status(self) -> Dict[str, Any]:
        """Get comprehensive failover status"""        try:
            # Service health summary
            service_health = {}
            for service_name, node_ids in self.service_groups.items():
                healthy_count = sum(
                    1 for node_id in node_ids
                    if self.service_nodes[node_id].status == NodeStatus.HEALTHY
                )
                total_count = len(node_ids)
                
                service_health[service_name] = {
                    "healthy_nodes": healthy_count,
                    "total_nodes": total_count,
                    "health_ratio": healthy_count / total_count if total_count > 0 else 0,
                    "primary_node": self.primary_nodes.get(service_name),
                    "status": "healthy" if healthy_count > 0 else "critical"
                }
            
            # Node status summary
            node_status_counts = {}
            for status in NodeStatus:
                node_status_counts[status.value] = sum(
                    1 for node in self.service_nodes.values()
                    if node.status == status
                )
            
            return {
                "is_monitoring": self.is_monitoring,
                "total_nodes": len(self.service_nodes),
                "blacklisted_nodes": len(self.blacklisted_nodes),
                "maintenance_nodes": len(self.maintenance_nodes),
                "active_failovers": len(self.active_failovers),
                "service_health": service_health,
                "node_status_counts": node_status_counts,
                "failover_metrics": {
                    "total_failovers": self.total_failovers,
                    "successful_failovers": self.successful_failovers,
                    "failed_failovers": self.failed_failovers,
                    "success_rate": (self.successful_failovers / self.total_failovers * 100) if self.total_failovers > 0 else 0,
                    "avg_recovery_time_seconds": self.avg_recovery_time
                },
                "recent_events": [
                    {
                        "id": event.id,
                        "trigger": event.trigger.value,
                        "service": event.service_name,
                        "source_node": event.source_node,
                        "target_nodes": event.target_nodes,
                        "success": event.success,
                        "started_at": event.started_at.isoformat(),
                        "recovery_time": event.recovery_time_seconds
                    } for event in list(self.failover_history)[-10:]  # Last 10 events
                ],
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get failover status: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}
    
    async def shutdown(self) -> None:
        """Shutdown failover manager"""        try:
            logger.info("Shutting down Failover Manager...")
            
            await self.stop_monitoring()
            
            # Save historical data
            await self._save_historical_data()
            
            logger.info("Failover Manager shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during Failover Manager shutdown: {e}")
    
    async def _save_historical_data(self) -> None:
        """Save historical failover data"""        try:
            data = {
                "total_failovers": self.total_failovers,
                "successful_failovers": self.successful_failovers,
                "failed_failovers": self.failed_failovers,
                "avg_recovery_time": self.avg_recovery_time,
                "last_updated": datetime.now().isoformat()
            }
            
            data_file = "/var/lib/ia-influencer/failover_history.json"
            with open(data_file, 'w') as f:
                json.dump(data, f)
                
        except Exception as e:
            logger.error(f"Failed to save historical data: {e}")
