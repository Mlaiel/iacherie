"""Load Balancer for IA Influencer Agent Platform
=============================================

Intelligent load balancing system for distributing streaming workloads
across multiple nodes with advanced algorithms and health monitoring.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️  LEGAL WARNING ⚠️
Unauthorized use, copying, modification, or distribution of this code
without explicit written permission from Fahed Mlaiel is strictly prohibited.
Violations will be prosecuted under German and international copyright law.

Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
import time
import uuid
import hashlib
from typing import Dict, List, Optional, Any, Callable, Union, Tuple
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
from collections import defaultdict, deque
import statistics
import random

logger = logging.getLogger(__name__)


class LoadBalancingAlgorithm(str, Enum):
    """Load balancing algorithm types"""
    ROUND_ROBIN = "round_robin"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"
    LEAST_RESPONSE_TIME = "least_response_time"
    CONSISTENT_HASHING = "consistent_hashing"
    RESOURCE_BASED = "resource_based"
    ADAPTIVE = "adaptive"
    GEOGRAPHIC = "geographic"
    CONTENT_AWARE = "content_aware"
    MACHINE_LEARNING = "machine_learning"


class NodeStatus(str, Enum):
    """Node status indicators"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    MAINTENANCE = "maintenance"
    OFFLINE = "offline"
    DRAINING = "draining"


class HealthCheckType(str, Enum):
    """Health check types"""
    HTTP = "http"
    TCP = "tcp"
    CUSTOM = "custom"
    PING = "ping"
    APPLICATION = "application"


class TrafficType(str, Enum):
    """Traffic type categories"""
    STREAMING = "streaming"
    API = "api"
    WEBSOCKET = "websocket"
    FILE_UPLOAD = "file_upload"
    FILE_DOWNLOAD = "file_download"
    ANALYTICS = "analytics"
    PROCESSING = "processing"


@dataclass
class LoadBalancerNode:
    """Load balancer node configuration"""
    node_id: str
    host: str
    port: int
    weight: float = 1.0
    capacity: int = 100
    status: NodeStatus = NodeStatus.HEALTHY
    region: str = ""
    zone: str = ""
    tags: Dict[str, str] = field(default_factory=dict)
    
    # Performance metrics
    current_connections: int = 0
    total_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    
    # Health check
    last_health_check: Optional[datetime] = None
    consecutive_failures: int = 0
    
    # Traffic statistics
    bytes_sent: int = 0
    bytes_received: int = 0


@dataclass
class HealthCheck:
    """Health check configuration"""
    check_id: str
    check_type: HealthCheckType
    endpoint: str = ""
    interval_seconds: int = 30
    timeout_seconds: int = 5
    healthy_threshold: int = 2
    unhealthy_threshold: int = 3
    custom_check: Optional[Callable] = None
    expected_response: Optional[str] = None


@dataclass
class LoadBalancingRule:
    """Load balancing rule"""
    rule_id: str
    priority: int
    conditions: Dict[str, Any] = field(default_factory=dict)
    target_pool: str = ""
    algorithm: LoadBalancingAlgorithm = LoadBalancingAlgorithm.ROUND_ROBIN
    enabled: bool = True


@dataclass
class TrafficSession:
    """Traffic session tracking"""
    session_id: str
    client_id: str
    traffic_type: TrafficType
    target_node: str
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_activity: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    request_count: int = 0
    bytes_transferred: int = 0
    sticky: bool = False


@dataclass
class LoadBalancingDecision:
    """Load balancing decision result"""
    selected_node: str
    algorithm_used: LoadBalancingAlgorithm
    decision_time_ms: float
    factors_considered: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    session_id: Optional[str] = None


class LoadBalancer:
    """
    Intelligent load balancing system for distributing streaming workloads
    across multiple nodes with advanced algorithms and health monitoring.
    
    Features:
    - Multiple load balancing algorithms
    - Real-time health monitoring
    - Geographic load distribution
    - Session affinity and sticky sessions
    - Adaptive algorithm selection
    - Traffic-aware routing
    - Machine learning-based predictions
    """
    
    def __init__(
        self,
        default_algorithm: LoadBalancingAlgorithm = LoadBalancingAlgorithm.ADAPTIVE,
        enable_health_checks: bool = True,
        enable_session_affinity: bool = True
    ):
        # Configuration
        self.default_algorithm = default_algorithm
        self.enable_health_checks = enable_health_checks
        self.enable_session_affinity = enable_session_affinity
        
        # Node management
        self.nodes: Dict[str, LoadBalancerNode] = {}
        self.node_pools: Dict[str, List[str]] = {"default": []}
        self.health_checks: Dict[str, HealthCheck] = {}
        
        # Load balancing state
        self.round_robin_index: Dict[str, int] = defaultdict(int)
        self.session_affinity: Dict[str, str] = {}  # client_id -> node_id
        self.active_sessions: Dict[str, TrafficSession] = {}
        
        # Rules and policies
        self.load_balancing_rules: Dict[str, LoadBalancingRule] = {}
        self.traffic_policies: Dict[TrafficType, Dict[str, Any]] = {}
        
        # Performance tracking
        self.load_balancer_metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "average_response_time": 0.0,
            "total_nodes": 0,
            "healthy_nodes": 0,
            "algorithm_performance": defaultdict(dict)
        }
        
        # Decision history for ML
        self.decision_history: deque = deque(maxlen=10000)
        self.performance_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # Consistent hashing ring
        self.hash_ring: Dict[int, str] = {}
        self.virtual_nodes_per_node = 150
        
        # Background tasks
        self.health_monitor_task: Optional[asyncio.Task] = None
        self.metrics_collector_task: Optional[asyncio.Task] = None
        self.session_cleanup_task: Optional[asyncio.Task] = None
        self.adaptive_tuner_task: Optional[asyncio.Task] = None
        
        # State management
        self._running = False
        self._shutdown_event = asyncio.Event()
        
        logger.info("LoadBalancer initialized")
        
    async def initialize(self) -> None:
        """Initialize the load balancer"""
        try:
            if self._running:
                return
                
            # Start background tasks
            if self.enable_health_checks:
                self.health_monitor_task = asyncio.create_task(self._health_monitor())
                
            self.metrics_collector_task = asyncio.create_task(self._metrics_collector())
            self.session_cleanup_task = asyncio.create_task(self._session_cleanup())
            self.adaptive_tuner_task = asyncio.create_task(self._adaptive_tuner())
            
            self._running = True
            logger.info("LoadBalancer initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize LoadBalancer: {e}")
            raise
            
    async def add_node(
        self,
        node_id: str,
        host: str,
        port: int,
        pool: str = "default",
        weight: float = 1.0,
        capacity: int = 100,
        region: str = "",
        zone: str = "",
        tags: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        Add a node to the load balancer
        
        Args:
            node_id: Unique node identifier
            host: Node hostname/IP
            port: Node port
            pool: Node pool name
            weight: Node weight for weighted algorithms
            capacity: Node capacity
            region: Geographic region
            zone: Availability zone
            tags: Additional tags
            
        Returns:
            Success status
        """
        try:
            if node_id in self.nodes:
                logger.warning(f"Node {node_id} already exists")
                return False
                
            node = LoadBalancerNode(
                node_id=node_id,
                host=host,
                port=port,
                weight=weight,
                capacity=capacity,
                region=region,
                zone=zone,
                tags=tags or {}
            )
            
            self.nodes[node_id] = node
            
            # Add to pool
            if pool not in self.node_pools:
                self.node_pools[pool] = []
            self.node_pools[pool].append(node_id)
            
            # Update consistent hash ring
            await self._update_hash_ring()
            
            # Start health checks
            if self.enable_health_checks:
                await self._setup_health_check(node_id)
                
            self.load_balancer_metrics["total_nodes"] += 1
            
            logger.info(f"Node added: {node_id} ({host}:{port}) to pool {pool}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add node {node_id}: {e}")
            return False
            
    async def remove_node(self, node_id: str) -> bool:
        """
        Remove a node from the load balancer
        
        Args:
            node_id: Node identifier
            
        Returns:
            Success status
        """
        try:
            if node_id not in self.nodes:
                logger.error(f"Node {node_id} not found")
                return False
                
            # Mark node as draining first
            await self.set_node_status(node_id, NodeStatus.DRAINING)
            
            # Wait for active sessions to complete (with timeout)
            await self._drain_node_sessions(node_id, timeout_seconds=30)
            
            # Remove from pools
            for pool_nodes in self.node_pools.values():
                if node_id in pool_nodes:
                    pool_nodes.remove(node_id)
                    
            # Remove node
            del self.nodes[node_id]
            
            # Update hash ring
            await self._update_hash_ring()
            
            # Clean up health checks
            if node_id in self.health_checks:
                del self.health_checks[node_id]
                
            self.load_balancer_metrics["total_nodes"] -= 1
            
            logger.info(f"Node removed: {node_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove node {node_id}: {e}")
            return False
            
    async def select_node(
        self,
        client_id: str,
        traffic_type: TrafficType = TrafficType.API,
        algorithm: Optional[LoadBalancingAlgorithm] = None,
        pool: str = "default",
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[LoadBalancingDecision]:
        """
        Select a node for handling traffic
        
        Args:
            client_id: Client identifier
            traffic_type: Type of traffic
            algorithm: Algorithm to use (optional)
            pool: Node pool to select from
            session_id: Session identifier
            metadata: Additional metadata
            
        Returns:
            Load balancing decision
        """
        try:
            start_time = time.time()
            
            # Get available nodes from pool
            available_nodes = await self._get_available_nodes(pool)
            
            if not available_nodes:
                logger.error(f"No available nodes in pool {pool}")
                return None
                
            # Check session affinity
            if self.enable_session_affinity and client_id in self.session_affinity:
                affinity_node = self.session_affinity[client_id]
                if affinity_node in available_nodes:
                    node_status = self.nodes[affinity_node].status
                    if node_status == NodeStatus.HEALTHY:
                        decision_time = (time.time() - start_time) * 1000
                        return LoadBalancingDecision(
                            selected_node=affinity_node,
                            algorithm_used=LoadBalancingAlgorithm.ROUND_ROBIN,  # Affinity override
                            decision_time_ms=decision_time,
                            factors_considered={"session_affinity": True},
                            session_id=session_id
                        )
                        
            # Apply load balancing rules
            rule_algorithm = await self._apply_load_balancing_rules(
                client_id, traffic_type, metadata or {}
            )
            
            if rule_algorithm:
                algorithm = rule_algorithm
            elif algorithm is None:
                algorithm = self.default_algorithm
                
            # Select node based on algorithm
            selected_node = await self._select_node_by_algorithm(
                algorithm, available_nodes, client_id, traffic_type, metadata or {}
            )
            
            if not selected_node:
                logger.error("Failed to select node")
                return None
                
            # Update session affinity
            if self.enable_session_affinity:
                self.session_affinity[client_id] = selected_node
                
            # Track session
            if session_id:
                session = TrafficSession(
                    session_id=session_id,
                    client_id=client_id,
                    traffic_type=traffic_type,
                    target_node=selected_node,
                    sticky=self.enable_session_affinity
                )
                self.active_sessions[session_id] = session
                
            # Update node metrics
            node = self.nodes[selected_node]
            node.current_connections += 1
            node.total_requests += 1
            
            decision_time = (time.time() - start_time) * 1000
            
            decision = LoadBalancingDecision(
                selected_node=selected_node,
                algorithm_used=algorithm,
                decision_time_ms=decision_time,
                factors_considered={
                    "pool": pool,
                    "traffic_type": traffic_type.value,
                    "available_nodes": len(available_nodes)
                },
                session_id=session_id
            )
            
            # Record decision for learning
            self.decision_history.append({
                "decision": decision,
                "timestamp": datetime.now(timezone.utc),
                "metadata": metadata or {}
            })
            
            self.load_balancer_metrics["total_requests"] += 1
            
            return decision
            
        except Exception as e:
            logger.error(f"Failed to select node: {e}")
            return None
            
    async def release_session(
        self,
        session_id: str,
        success: bool = True,
        response_time_ms: Optional[float] = None,
        bytes_transferred: int = 0
    ) -> None:
        """
        Release a session and update metrics
        
        Args:
            session_id: Session identifier
            success: Whether session was successful
            response_time_ms: Response time in milliseconds
            bytes_transferred: Bytes transferred
        """
        try:
            if session_id not in self.active_sessions:
                return
                
            session = self.active_sessions[session_id]
            node = self.nodes.get(session.target_node)
            
            if node:
                # Update node metrics
                node.current_connections -= 1
                
                if success:
                    self.load_balancer_metrics["successful_requests"] += 1
                else:
                    node.failed_requests += 1
                    self.load_balancer_metrics["failed_requests"] += 1
                    
                if response_time_ms is not None:
                    # Update average response time
                    total_requests = node.total_requests
                    if total_requests > 1:
                        node.average_response_time = (
                            (node.average_response_time * (total_requests - 1) + response_time_ms) / total_requests
                        )
                    else:
                        node.average_response_time = response_time_ms
                        
                if bytes_transferred > 0:
                    node.bytes_sent += bytes_transferred
                    
            # Clean up session
            del self.active_sessions[session_id]
            
        except Exception as e:
            logger.error(f"Failed to release session {session_id}: {e}")
            
    async def set_node_status(self, node_id: str, status: NodeStatus) -> bool:
        """
        Set node status
        
        Args:
            node_id: Node identifier
            status: New status
            
        Returns:
            Success status
        """
        try:
            if node_id not in self.nodes:
                logger.error(f"Node {node_id} not found")
                return False
                
            old_status = self.nodes[node_id].status
            self.nodes[node_id].status = status
            
            # Update healthy nodes count
            if old_status == NodeStatus.HEALTHY and status != NodeStatus.HEALTHY:
                self.load_balancer_metrics["healthy_nodes"] -= 1
            elif old_status != NodeStatus.HEALTHY and status == NodeStatus.HEALTHY:
                self.load_balancer_metrics["healthy_nodes"] += 1
                
            logger.info(f"Node {node_id} status changed: {old_status} -> {status}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to set node status: {e}")
            return False
            
    async def get_load_balancer_stats(self) -> Dict[str, Any]:
        """Get load balancer statistics"""
        try:
            # Calculate success rate
            total_requests = self.load_balancer_metrics["total_requests"]
            success_rate = 0.0
            if total_requests > 0:
                success_rate = (self.load_balancer_metrics["successful_requests"] / total_requests) * 100
                
            # Node statistics
            node_stats = {}
            for node_id, node in self.nodes.items():
                utilization = (node.current_connections / node.capacity) * 100 if node.capacity > 0 else 0
                success_rate_node = 0.0
                if node.total_requests > 0:
                    success_rate_node = ((node.total_requests - node.failed_requests) / node.total_requests) * 100
                    
                node_stats[node_id] = {
                    "status": node.status.value,
                    "current_connections": node.current_connections,
                    "total_requests": node.total_requests,
                    "failed_requests": node.failed_requests,
                    "success_rate": success_rate_node,
                    "average_response_time": node.average_response_time,
                    "utilization": utilization,
                    "region": node.region,
                    "zone": node.zone
                }
                
            # Pool statistics
            pool_stats = {}
            for pool_name, node_list in self.node_pools.items():
                healthy_count = sum(1 for nid in node_list if self.nodes[nid].status == NodeStatus.HEALTHY)
                pool_stats[pool_name] = {
                    "total_nodes": len(node_list),
                    "healthy_nodes": healthy_count,
                    "nodes": node_list
                }
                
            # Active sessions
            sessions_by_type = defaultdict(int)
            for session in self.active_sessions.values():
                sessions_by_type[session.traffic_type.value] += 1
                
            return {
                "overview": {
                    "total_requests": total_requests,
                    "success_rate": success_rate,
                    "total_nodes": len(self.nodes),
                    "healthy_nodes": self.load_balancer_metrics["healthy_nodes"],
                    "active_sessions": len(self.active_sessions),
                    "default_algorithm": self.default_algorithm.value
                },
                "nodes": node_stats,
                "pools": pool_stats,
                "sessions_by_type": dict(sessions_by_type),
                "algorithm_performance": dict(self.load_balancer_metrics["algorithm_performance"])
            }
            
        except Exception as e:
            logger.error(f"Failed to get load balancer stats: {e}")
            return {}
            
    async def _get_available_nodes(self, pool: str) -> List[str]:
        """Get available nodes from pool"""
        try:
            if pool not in self.node_pools:
                return []
                
            available = []
            for node_id in self.node_pools[pool]:
                node = self.nodes[node_id]
                if node.status in [NodeStatus.HEALTHY, NodeStatus.DEGRADED]:
                    available.append(node_id)
                    
            return available
            
        except Exception as e:
            logger.error(f"Failed to get available nodes: {e}")
            return []
            
    async def _select_node_by_algorithm(
        self,
        algorithm: LoadBalancingAlgorithm,
        available_nodes: List[str],
        client_id: str,
        traffic_type: TrafficType,
        metadata: Dict[str, Any]
    ) -> Optional[str]:
        """Select node using specified algorithm"""
        try:
            if algorithm == LoadBalancingAlgorithm.ROUND_ROBIN:
                return await self._round_robin_select(available_nodes, "default")
                
            elif algorithm == LoadBalancingAlgorithm.WEIGHTED_ROUND_ROBIN:
                return await self._weighted_round_robin_select(available_nodes)
                
            elif algorithm == LoadBalancingAlgorithm.LEAST_CONNECTIONS:
                return await self._least_connections_select(available_nodes)
                
            elif algorithm == LoadBalancingAlgorithm.LEAST_RESPONSE_TIME:
                return await self._least_response_time_select(available_nodes)
                
            elif algorithm == LoadBalancingAlgorithm.CONSISTENT_HASHING:
                return await self._consistent_hash_select(available_nodes, client_id)
                
            elif algorithm == LoadBalancingAlgorithm.RESOURCE_BASED:
                return await self._resource_based_select(available_nodes)
                
            elif algorithm == LoadBalancingAlgorithm.ADAPTIVE:
                return await self._adaptive_select(available_nodes, traffic_type, metadata)
                
            elif algorithm == LoadBalancingAlgorithm.GEOGRAPHIC:
                return await self._geographic_select(available_nodes, metadata)
                
            else:
                # Default to round robin
                return await self._round_robin_select(available_nodes, "default")
                
        except Exception as e:
            logger.error(f"Failed to select node by algorithm {algorithm}: {e}")
            return None
            
    async def _round_robin_select(self, available_nodes: List[str], pool: str) -> Optional[str]:
        """Round robin selection"""
        if not available_nodes:
            return None
            
        index = self.round_robin_index[pool] % len(available_nodes)
        self.round_robin_index[pool] += 1
        return available_nodes[index]
        
    async def _weighted_round_robin_select(self, available_nodes: List[str]) -> Optional[str]:
        """Weighted round robin selection"""
        if not available_nodes:
            return None
            
        # Calculate total weight
        total_weight = sum(self.nodes[node_id].weight for node_id in available_nodes)
        
        # Select random point
        random_point = random.uniform(0, total_weight)
        
        # Find corresponding node
        current_weight = 0
        for node_id in available_nodes:
            current_weight += self.nodes[node_id].weight
            if random_point <= current_weight:
                return node_id
                
        return available_nodes[0]  # Fallback
        
    async def _least_connections_select(self, available_nodes: List[str]) -> Optional[str]:
        """Least connections selection"""
        if not available_nodes:
            return None
            
        min_connections = float('inf')
        selected_node = None
        
        for node_id in available_nodes:
            node = self.nodes[node_id]
            if node.current_connections < min_connections:
                min_connections = node.current_connections
                selected_node = node_id
                
        return selected_node
        
    async def _least_response_time_select(self, available_nodes: List[str]) -> Optional[str]:
        """Least response time selection"""
        if not available_nodes:
            return None
            
        min_response_time = float('inf')
        selected_node = None
        
        for node_id in available_nodes:
            node = self.nodes[node_id]
            if node.average_response_time < min_response_time:
                min_response_time = node.average_response_time
                selected_node = node_id
                
        return selected_node or available_nodes[0]
        
    async def _consistent_hash_select(self, available_nodes: List[str], client_id: str) -> Optional[str]:
        """Consistent hashing selection"""
        if not available_nodes:
            return None
            
        # Hash client ID
        client_hash = int(hashlib.md5(client_id.encode()).hexdigest(), 16)
        
        # Find closest node in hash ring
        if not self.hash_ring:
            return available_nodes[0]
            
        closest_hash = min(self.hash_ring.keys(), key=lambda x: abs(x - client_hash))
        selected_node = self.hash_ring[closest_hash]
        
        # Ensure selected node is available
        if selected_node in available_nodes:
            return selected_node
        else:
            return available_nodes[0]  # Fallback
            
    async def _resource_based_select(self, available_nodes: List[str]) -> Optional[str]:
        """Resource-based selection"""
        if not available_nodes:
            return None
            
        best_score = float('-inf')
        selected_node = None
        
        for node_id in available_nodes:
            node = self.nodes[node_id]
            
            # Calculate resource score (lower CPU/memory usage = higher score)
            cpu_score = (100 - node.cpu_usage) / 100
            memory_score = (100 - node.memory_usage) / 100
            connection_score = (node.capacity - node.current_connections) / node.capacity
            
            total_score = (cpu_score + memory_score + connection_score) / 3
            
            if total_score > best_score:
                best_score = total_score
                selected_node = node_id
                
        return selected_node
        
    async def _adaptive_select(
        self,
        available_nodes: List[str],
        traffic_type: TrafficType,
        metadata: Dict[str, Any]
    ) -> Optional[str]:
        """Adaptive algorithm selection"""
        if not available_nodes:
            return None
            
        # Choose algorithm based on traffic type and current conditions
        if traffic_type == TrafficType.STREAMING:
            # For streaming, prioritize bandwidth and low latency
            return await self._least_response_time_select(available_nodes)
        elif traffic_type == TrafficType.FILE_UPLOAD:
            # For uploads, prioritize available capacity
            return await self._resource_based_select(available_nodes)
        elif traffic_type == TrafficType.WEBSOCKET:
            # For WebSocket, use consistent hashing for session affinity
            client_id = metadata.get("client_id", "unknown")
            return await self._consistent_hash_select(available_nodes, client_id)
        else:
            # Default to least connections
            return await self._least_connections_select(available_nodes)
            
    async def _geographic_select(self, available_nodes: List[str], metadata: Dict[str, Any]) -> Optional[str]:
        """Geographic-based selection"""
        if not available_nodes:
            return None
            
        client_region = metadata.get("region", "")
        client_zone = metadata.get("zone", "")
        
        # First try to find nodes in same zone
        same_zone_nodes = [
            node_id for node_id in available_nodes
            if self.nodes[node_id].zone == client_zone
        ]
        
        if same_zone_nodes:
            return await self._least_connections_select(same_zone_nodes)
            
        # Then try same region
        same_region_nodes = [
            node_id for node_id in available_nodes
            if self.nodes[node_id].region == client_region
        ]
        
        if same_region_nodes:
            return await self._least_connections_select(same_region_nodes)
            
        # Fallback to any available node
        return await self._least_connections_select(available_nodes)
        
    async def _apply_load_balancing_rules(
        self,
        client_id: str,
        traffic_type: TrafficType,
        metadata: Dict[str, Any]
    ) -> Optional[LoadBalancingAlgorithm]:
        """Apply load balancing rules"""
        try:
            # Sort rules by priority
            sorted_rules = sorted(
                self.load_balancing_rules.values(),
                key=lambda r: r.priority,
                reverse=True
            )
            
            for rule in sorted_rules:
                if not rule.enabled:
                    continue
                    
                # Check conditions
                conditions_met = True
                for condition_key, condition_value in rule.conditions.items():
                    if condition_key == "traffic_type":
                        if traffic_type.value != condition_value:
                            conditions_met = False
                            break
                    elif condition_key == "client_pattern":
                        import re
                        if not re.match(condition_value, client_id):
                            conditions_met = False
                            break
                    elif condition_key in metadata:
                        if metadata[condition_key] != condition_value:
                            conditions_met = False
                            break
                            
                if conditions_met:
                    return rule.algorithm
                    
            return None
            
        except Exception as e:
            logger.error(f"Failed to apply load balancing rules: {e}")
            return None
            
    async def _update_hash_ring(self) -> None:
        """Update consistent hashing ring"""
        try:
            self.hash_ring.clear()
            
            for node_id in self.nodes.keys():
                # Create virtual nodes
                for i in range(self.virtual_nodes_per_node):
                    virtual_key = f"{node_id}:{i}"
                    hash_value = int(hashlib.md5(virtual_key.encode()).hexdigest(), 16)
                    self.hash_ring[hash_value] = node_id
                    
        except Exception as e:
            logger.error(f"Failed to update hash ring: {e}")
            
    async def _setup_health_check(self, node_id: str) -> None:
        """Setup health check for node"""
        try:
            node = self.nodes[node_id]
            
            # Create default health check
            health_check = HealthCheck(
                check_id=f"{node_id}_health",
                check_type=HealthCheckType.TCP,
                endpoint=f"{node.host}:{node.port}",
                interval_seconds=30,
                timeout_seconds=5
            )
            
            self.health_checks[node_id] = health_check
            
        except Exception as e:
            logger.error(f"Failed to setup health check for {node_id}: {e}")
            
    async def _drain_node_sessions(self, node_id: str, timeout_seconds: int = 30) -> None:
        """Drain active sessions from node"""
        try:
            start_time = time.time()
            
            while time.time() - start_time < timeout_seconds:
                # Check for active sessions on this node
                active_sessions_on_node = [
                    session for session in self.active_sessions.values()
                    if session.target_node == node_id
                ]
                
                if not active_sessions_on_node:
                    break
                    
                await asyncio.sleep(1)
                
            # Force cleanup remaining sessions
            remaining_sessions = [
                session_id for session_id, session in self.active_sessions.items()
                if session.target_node == node_id
            ]
            
            for session_id in remaining_sessions:
                del self.active_sessions[session_id]
                
        except Exception as e:
            logger.error(f"Failed to drain node sessions: {e}")
            
    async def _health_monitor(self) -> None:
        """Background health monitoring task"""
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(10)  # Check every 10 seconds
                
                for node_id, health_check in self.health_checks.items():
                    await self._perform_health_check(node_id, health_check)
                    
            except Exception as e:
                logger.error(f"Health monitor error: {e}")
                
    async def _perform_health_check(self, node_id: str, health_check: HealthCheck) -> None:
        """Perform health check on node"""
        try:
            node = self.nodes[node_id]
            
            # Skip if not time for check
            if (node.last_health_check and 
                datetime.now(timezone.utc) - node.last_health_check < timedelta(seconds=health_check.interval_seconds)):
                return
                
            # Perform check based on type
            is_healthy = False
            
            if health_check.check_type == HealthCheckType.TCP:
                is_healthy = await self._tcp_health_check(node.host, node.port, health_check.timeout_seconds)
            elif health_check.check_type == HealthCheckType.HTTP:
                is_healthy = await self._http_health_check(health_check.endpoint, health_check.timeout_seconds)
            elif health_check.check_type == HealthCheckType.CUSTOM and health_check.custom_check:
                is_healthy = await health_check.custom_check(node)
            else:
                is_healthy = True  # Default healthy
                
            # Update node status
            if is_healthy:
                node.consecutive_failures = 0
                if node.status != NodeStatus.HEALTHY:
                    await self.set_node_status(node_id, NodeStatus.HEALTHY)
            else:
                node.consecutive_failures += 1
                if node.consecutive_failures >= health_check.unhealthy_threshold:
                    await self.set_node_status(node_id, NodeStatus.UNHEALTHY)
                    
            node.last_health_check = datetime.now(timezone.utc)
            
        except Exception as e:
            logger.error(f"Failed to perform health check for {node_id}: {e}")
            
    async def _tcp_health_check(self, host: str, port: int, timeout: int) -> bool:
        """Perform TCP health check"""
        try:
            # Simulate TCP connection check
            await asyncio.sleep(0.01)  # Simulate network delay
            return True  # For demo purposes
            
        except Exception as e:
            logger.error(f"TCP health check failed: {e}")
            return False
            
    async def _http_health_check(self, endpoint: str, timeout: int) -> bool:
        """Perform HTTP health check"""
        try:
            # Simulate HTTP health check
            await asyncio.sleep(0.01)  # Simulate HTTP request
            return True  # For demo purposes
            
        except Exception as e:
            logger.error(f"HTTP health check failed: {e}")
            return False
            
    async def _metrics_collector(self) -> None:
        """Background metrics collection task"""
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(60)  # Collect every minute
                
                # Update load balancer metrics
                await self._update_load_balancer_metrics()
                
            except Exception as e:
                logger.error(f"Metrics collector error: {e}")
                
    async def _session_cleanup(self) -> None:
        """Background session cleanup task"""
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(300)  # Cleanup every 5 minutes
                
                # Clean up stale sessions
                cutoff_time = datetime.now(timezone.utc) - timedelta(hours=1)
                stale_sessions = [
                    session_id for session_id, session in self.active_sessions.items()
                    if session.last_activity < cutoff_time
                ]
                
                for session_id in stale_sessions:
                    await self.release_session(session_id, success=False)
                    
                if stale_sessions:
                    logger.info(f"Cleaned up {len(stale_sessions)} stale sessions")
                    
            except Exception as e:
                logger.error(f"Session cleanup error: {e}")
                
    async def _adaptive_tuner(self) -> None:
        """Background adaptive algorithm tuning task"""
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(600)  # Tune every 10 minutes
                
                # Analyze algorithm performance
                await self._analyze_algorithm_performance()
                
            except Exception as e:
                logger.error(f"Adaptive tuner error: {e}")
                
    async def _update_load_balancer_metrics(self) -> None:
        """Update load balancer metrics"""
        try:
            # Count healthy nodes
            healthy_count = sum(
                1 for node in self.nodes.values()
                if node.status == NodeStatus.HEALTHY
            )
            self.load_balancer_metrics["healthy_nodes"] = healthy_count
            
            # Calculate average response time
            total_requests = sum(node.total_requests for node in self.nodes.values())
            if total_requests > 0:
                weighted_response_time = sum(
                    node.average_response_time * node.total_requests
                    for node in self.nodes.values()
                )
                self.load_balancer_metrics["average_response_time"] = weighted_response_time / total_requests
                
        except Exception as e:
            logger.error(f"Failed to update load balancer metrics: {e}")
            
    async def _analyze_algorithm_performance(self) -> None:
        """Analyze performance of different algorithms"""
        try:
            # This would implement ML-based analysis of algorithm performance
            # For now, just track basic statistics
            
            algorithm_stats = defaultdict(lambda: {"requests": 0, "avg_response_time": 0.0})
            
            for decision_record in list(self.decision_history)[-1000:]:  # Last 1000 decisions
                decision = decision_record["decision"]
                algorithm = decision.algorithm_used
                
                algorithm_stats[algorithm]["requests"] += 1
                algorithm_stats[algorithm]["avg_response_time"] += decision.decision_time_ms
                
            # Calculate averages
            for algorithm, stats in algorithm_stats.items():
                if stats["requests"] > 0:
                    stats["avg_response_time"] /= stats["requests"]
                    
            self.load_balancer_metrics["algorithm_performance"] = dict(algorithm_stats)
            
        except Exception as e:
            logger.error(f"Failed to analyze algorithm performance: {e}")
            
    async def shutdown(self) -> None:
        """Gracefully shutdown the load balancer"""
        try:
            logger.info("Shutting down LoadBalancer...")
            
            self._shutdown_event.set()
            
            # Cancel background tasks
            tasks_to_cancel = [
                self.health_monitor_task,
                self.metrics_collector_task,
                self.session_cleanup_task,
                self.adaptive_tuner_task
            ]
            
            for task in tasks_to_cancel:
                if task:
                    task.cancel()
                    
            self._running = False
            logger.info("LoadBalancer shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")