# WARNING: Potential SQL injection risk - use parameterized queries
"""
Load Balancer - Enterprise Performance Module
=============================================

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

Enterprise-grade load balancing for Creator Economy platform.
Intelligent traffic distribution with creator-specific optimization.

Performance Targets: < 5ms routing decisions
Availability: 99.99% uptime
Load Distribution: Optimal across all nodes
"""

import asyncio
import logging
import time
import threading
import random
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import statistics

# Enterprise logging setup
logger = logging.getLogger(__name__)


class LoadBalancingAlgorithm(Enum):
    """Load balancing algorithms"""
    ROUND_ROBIN = "round_robin"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_LEAST_CONNECTIONS = "weighted_least_connections"
    IP_HASH = "ip_hash"
    LEAST_RESPONSE_TIME = "least_response_time"
    CREATOR_AWARE = "creator_aware"
    INTELLIGENT = "intelligent"


class HealthCheckType(Enum):
    """Health check types"""
    TCP = "tcp"
    HTTP = "http"
    HTTPS = "https"
    CUSTOM = "custom"
    PING = "ping"


class NodeStatus(Enum):
    """Node status states"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DRAINING = "draining"
    MAINTENANCE = "maintenance"
    OVERLOADED = "overloaded"


@dataclass
class BackendNode:
    """Backend node configuration"""
    node_id: str
    host: str
    port: int
    weight: int = 100
    max_connections: int = 1000
    current_connections: int = 0
    status: NodeStatus = NodeStatus.HEALTHY
    last_health_check: datetime = field(default_factory=datetime.now)
    response_times: deque = field(default_factory=lambda: deque(maxlen=100))
    failure_count: int = 0
    success_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LoadBalancerPool:
    """Load balancer pool configuration"""
    pool_name: str
    algorithm: LoadBalancingAlgorithm
    nodes: List[BackendNode] = field(default_factory=list)
    health_check_interval: int = 30
    health_check_type: HealthCheckType = HealthCheckType.HTTP
    health_check_path: str = "/health"
    sticky_sessions: bool = False
    session_affinity_timeout: int = 3600
    creator_context: str = ""
    circuit_breaker_enabled: bool = True


@dataclass
class RequestMetrics:
    """Request routing metrics"""
    timestamp: datetime = field(default_factory=datetime.now)
    client_ip: str = ""
    target_node_id: str = ""
    response_time_ms: float = 0.0
    status_code: int = 200
    bytes_transferred: int = 0
    creator_context: str = ""
    routing_algorithm: LoadBalancingAlgorithm = LoadBalancingAlgorithm.ROUND_ROBIN


@dataclass
class HealthCheckResult:
    """Health check result"""
    node_id: str
    check_type: HealthCheckType
    success: bool
    response_time_ms: float
    status_code: Optional[int] = None
    error_message: str = ""
    timestamp: datetime = field(default_factory=datetime.now)


class CreatorLoadBalancingProfile:
    """Creator-specific load balancing profiles"""
    
    def __init__(self, creator_type: str):
        self.creator_type = creator_type
        self.routing_preferences = {}
        self.performance_requirements = {}
        self.priority_settings = {}
        
    def get_musician_profile(self) -> Dict[str, Any]:
        """Load balancing profile for musicians"""
        return {
            "algorithm_preference": LoadBalancingAlgorithm.LEAST_RESPONSE_TIME,
            "priority_level": "real_time",
            "session_affinity": True,
            "circuit_breaker": {
                "failure_threshold": 3,
                "recovery_timeout": 30,
                "half_open_max_requests": 5
            },
            "health_check": {
                "interval_seconds": 10,
                "timeout_ms": 1000,
                "path": "/health/audio"
            },
            "routing_rules": {
                "audio_processing": "high_performance_nodes",
                "real_time_collaboration": "low_latency_nodes",
                "file_storage": "high_bandwidth_nodes",
                "backup_operations": "standard_nodes"
            },
            "performance_targets": {
                "max_response_time_ms": 50.0,
                "target_availability": 99.99,
                "max_concurrent_connections": 100
            }
        }
    
    def get_photographer_profile(self) -> Dict[str, Any]:
        """Load balancing profile for photographers"""
        return {
            "algorithm_preference": LoadBalancingAlgorithm.WEIGHTED_LEAST_CONNECTIONS,
            "priority_level": "high_throughput",
            "session_affinity": False,
            "circuit_breaker": {
                "failure_threshold": 5,
                "recovery_timeout": 60,
                "half_open_max_requests": 10
            },
            "health_check": {
                "interval_seconds": 20,
                "timeout_ms": 2000,
                "path": "/health/images"
            },
            "routing_rules": {
                "image_upload": "high_bandwidth_nodes",
                "image_processing": "gpu_enabled_nodes",
                "gallery_serving": "cdn_nodes",
                "backup_operations": "storage_nodes"
            },
            "performance_targets": {
                "max_response_time_ms": 200.0,
                "target_availability": 99.9,
                "max_concurrent_connections": 500
            }
        }
    
    def get_blogger_profile(self) -> Dict[str, Any]:
        """Load balancing profile for bloggers"""
        return {
            "algorithm_preference": LoadBalancingAlgorithm.ROUND_ROBIN,
            "priority_level": "balanced",
            "session_affinity": True,
            "circuit_breaker": {
                "failure_threshold": 5,
                "recovery_timeout": 45,
                "half_open_max_requests": 8
            },
            "health_check": {
                "interval_seconds": 30,
                "timeout_ms": 1500,
                "path": "/health/content"
            },
            "routing_rules": {
                "content_editing": "standard_nodes",
                "publishing": "high_availability_nodes",
                "analytics": "analytics_nodes",
                "media_serving": "cdn_nodes"
            },
            "performance_targets": {
                "max_response_time_ms": 500.0,
                "target_availability": 99.5,
                "max_concurrent_connections": 200
            }
        }


class LoadBalancer:
    """
    Enterprise Load Balancer for Creator Economy Platform
    
    Intelligent traffic distribution with advanced health monitoring.
    Specialized for content creator workloads requiring high availability.
    
    Features:
    - < 5ms routing decisions
    - 99.99% availability target
    - Creator-specific routing
    - Intelligent failover
    - Real-time health monitoring
    """
    
    def __init__(
        self,
        default_algorithm: LoadBalancingAlgorithm = LoadBalancingAlgorithm.ROUND_ROBIN,
        enable_health_checks: bool = True,
        enable_circuit_breaker: bool = True,
        enable_sticky_sessions: bool = False,
        monitoring_interval: int = 10
    ):
        self.default_algorithm = default_algorithm
        self.enable_health_checks = enable_health_checks
        self.enable_circuit_breaker = enable_circuit_breaker
        self.enable_sticky_sessions = enable_sticky_sessions
        self.monitoring_interval = monitoring_interval
        
        # Enterprise state management
        self._is_running = False
        self._balancing_lock = threading.Lock()
        self._pools: Dict[str, LoadBalancerPool] = {}
        self._creator_profiles: Dict[str, CreatorLoadBalancingProfile] = {}
        
        # Request tracking
        self._request_metrics: deque = deque(maxlen=10000)
        self._session_store: Dict[str, str] = {}  # session_id -> node_id
        self._session_timeouts: Dict[str, datetime] = {}
        
        # Health monitoring
        self._health_check_results: Dict[str, List[HealthCheckResult]] = defaultdict(list)
        self._circuit_breakers: Dict[str, Dict[str, Any]] = {}  # node_id -> circuit_breaker_state
        
        # Round robin counters
        self._round_robin_counters: Dict[str, int] = defaultdict(int)
        
        # Performance tracking
        self._balancing_stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "avg_response_time_ms": 0.0,
            "avg_routing_time_ms": 0.0,
            "node_utilization": {},
            "algorithm_usage": defaultdict(int),
            "last_routing": None
        }
        
        logger.info(f"LoadBalancer initialized - Algorithm: {default_algorithm.value}")
    
    async def start_monitoring(self) -> None:
        """Start load balancer monitoring and health checks"""
        if self._is_running:
            logger.warning("Load balancer monitoring already running")
            return
        
        self._is_running = True
        logger.info("Starting enterprise load balancer monitoring")
        
        try:
            while self._is_running:
                start_time = time.perf_counter()
                
                # Perform health checks
                if self.enable_health_checks:
                    await self.perform_health_checks()
                
                # Update circuit breaker states
                if self.enable_circuit_breaker:
                    await self.update_circuit_breakers()
                
                # Clean up expired sessions
                if self.enable_sticky_sessions:
                    await self.cleanup_expired_sessions()
                
                # Update load balancing statistics
                await self.update_balancing_statistics()
                
                # Sleep until next monitoring cycle
                monitoring_time = (time.perf_counter() - start_time) * 1000
                logger.debug(f"Monitoring cycle completed in {monitoring_time:.2f}ms")
                
                await asyncio.sleep(self.monitoring_interval)
                
        except Exception as e:
            logger.error(f"Error in load balancer monitoring: {e}")
        finally:
            self._is_running = False
            logger.info("Load balancer monitoring stopped")
    
    async def stop_monitoring(self) -> None:
        """Stop load balancer monitoring"""
        self._is_running = False
        logger.info("Stopping load balancer monitoring")
    
    async def route_request(self, pool_name: str, client_ip: str = "", 
                           session_id: str = "", creator_context: str = "",
                           request_metadata: Optional[Dict[str, Any]] = None) -> Optional[BackendNode]:
        """
        Route request to optimal backend node
        
        Performance Target: < 5ms routing decisions
        """
        start_time = time.perf_counter()
        
        try:
            if pool_name not in self._pools:
                logger.error(f"Pool '{pool_name}' not found")
                return None
            
            pool = self._pools[pool_name]
            
            # Filter healthy nodes
            healthy_nodes = [node for node in pool.nodes if node.status == NodeStatus.HEALTHY]
            
            if not healthy_nodes:
                logger.error(f"No healthy nodes available in pool '{pool_name}'")
                return None
            
            # Check for sticky session
            if self.enable_sticky_sessions and session_id:
                if session_id in self._session_store:
                    target_node_id = self._session_store[session_id]
                    target_node = next((n for n in healthy_nodes if n.node_id == target_node_id), None)
                    if target_node:
                        await self._track_request(target_node, client_ip, session_id, creator_context)
                        return target_node
            
            # Select algorithm based on creator profile or pool configuration
            algorithm = await self._select_routing_algorithm(pool, creator_context)
            
            # Route using selected algorithm
            selected_node = await self._route_with_algorithm(
                healthy_nodes, algorithm, pool_name, client_ip, request_metadata
            )
            
            if selected_node:
                # Update session store if sticky sessions enabled
                if self.enable_sticky_sessions and session_id:
                    self._session_store[session_id] = selected_node.node_id
                    self._session_timeouts[session_id] = datetime.now() + timedelta(seconds=pool.session_affinity_timeout)
                
                # Track the request
                await self._track_request(selected_node, client_ip, session_id, creator_context)
                
                # Update routing statistics
                routing_time = (time.perf_counter() - start_time) * 1000
                self._update_routing_stats(routing_time, algorithm)
                
                return selected_node
            
            return None
            
        except Exception as e:
            logger.error(f"Error routing request: {e}")
            return None
    
    async def _select_routing_algorithm(self, pool: LoadBalancerPool, 
                                       creator_context: str) -> LoadBalancingAlgorithm:
        """Select optimal routing algorithm based on context"""
        try:
            # Check creator-specific preferences
            if creator_context and creator_context in self._creator_profiles:
                profile = self._creator_profiles[creator_context]
                creator_prefs = profile.routing_preferences.get("algorithm_preference")
                if creator_prefs:
                    return creator_prefs
            
            # Use pool-specific algorithm
            return pool.algorithm
            
        except Exception as e:
            logger.error(f"Error selecting routing algorithm: {e}")
            return self.default_algorithm
    
    async def _route_with_algorithm(self, nodes: List[BackendNode], 
                                   algorithm: LoadBalancingAlgorithm,
                                   pool_name: str, client_ip: str,
                                   request_metadata: Optional[Dict[str, Any]]) -> Optional[BackendNode]:
        """Route request using specified algorithm"""
        try:
            if algorithm == LoadBalancingAlgorithm.ROUND_ROBIN:
                return await self._round_robin_routing(nodes, pool_name)
            
            elif algorithm == LoadBalancingAlgorithm.WEIGHTED_ROUND_ROBIN:
                return await self._weighted_round_robin_routing(nodes, pool_name)
            
            elif algorithm == LoadBalancingAlgorithm.LEAST_CONNECTIONS:
                return await self._least_connections_routing(nodes)
            
            elif algorithm == LoadBalancingAlgorithm.WEIGHTED_LEAST_CONNECTIONS:
                return await self._weighted_least_connections_routing(nodes)
            
            elif algorithm == LoadBalancingAlgorithm.IP_HASH:
                return await self._ip_hash_routing(nodes, client_ip)
            
            elif algorithm == LoadBalancingAlgorithm.LEAST_RESPONSE_TIME:
                return await self._least_response_time_routing(nodes)
            
            elif algorithm == LoadBalancingAlgorithm.CREATOR_AWARE:
                return await self._creator_aware_routing(nodes, request_metadata)
            
            elif algorithm == LoadBalancingAlgorithm.INTELLIGENT:
                return await self._intelligent_routing(nodes, request_metadata)
            
            else:
                # Fallback to round robin
                return await self._round_robin_routing(nodes, pool_name)
                
        except Exception as e:
            logger.error(f"Error in {algorithm.value} routing: {e}")
            return nodes[0] if nodes else None
    
    async def _round_robin_routing(self, nodes: List[BackendNode], pool_name: str) -> BackendNode:
        """Simple round robin routing"""
        counter = self._round_robin_counters[pool_name]
        selected_node = nodes[counter % len(nodes)]
        self._round_robin_counters[pool_name] = (counter + 1) % len(nodes)
        return selected_node
    
    async def _weighted_round_robin_routing(self, nodes: List[BackendNode], pool_name: str) -> BackendNode:
        """Weighted round robin routing"""
        # Create weighted list
        weighted_nodes = []
        for node in nodes:
            weighted_nodes.extend([node] * max(1, node.weight // 10))
        
        if not weighted_nodes:
            return nodes[0]
        
        counter = self._round_robin_counters[pool_name]
        selected_node = weighted_nodes[counter % len(weighted_nodes)]
        self._round_robin_counters[pool_name] = (counter + 1) % len(weighted_nodes)
        return selected_node
    
    async def _least_connections_routing(self, nodes: List[BackendNode]) -> BackendNode:
        """Least connections routing"""
        return min(nodes, key=lambda n: n.current_connections)
    
    async def _weighted_least_connections_routing(self, nodes: List[BackendNode]) -> BackendNode:
        """Weighted least connections routing"""
        def connection_ratio(node):
            if node.weight == 0:
                return float('inf')
            return node.current_connections / node.weight
        
        return min(nodes, key=connection_ratio)
    
    async def _ip_hash_routing(self, nodes: List[BackendNode], client_ip: str) -> BackendNode:
        """IP hash routing for session persistence"""
        if not client_ip:
            return nodes[0]
        
        hash_value = int(hashlib.md5(client_ip.encode()).hexdigest(), 16)
        return nodes[hash_value % len(nodes)]
    
    async def _least_response_time_routing(self, nodes: List[BackendNode]) -> BackendNode:
        """Least response time routing"""
        def avg_response_time(node):
            if not node.response_times:
                return 0.0
            return statistics.mean(node.response_times)
        
        return min(nodes, key=avg_response_time)
    
    async def _creator_aware_routing(self, nodes: List[BackendNode], 
                                   request_metadata: Optional[Dict[str, Any]]) -> BackendNode:
        """Creator-aware routing based on content type and creator needs"""
        try:
            if not request_metadata:
                return nodes[0]
            
            content_type = request_metadata.get("content_type", "")
            creator_type = request_metadata.get("creator_type", "")
            
            # Route based on content type and creator requirements
            if creator_type == "musician" and "audio" in content_type:
                # Prefer nodes with low latency for audio
                return min(nodes, key=lambda n: statistics.mean(n.response_times) if n.response_times else 0)
            
            elif creator_type == "photographer" and "image" in content_type:
                # Prefer nodes with high bandwidth for images
                return max(nodes, key=lambda n: n.weight)  # Higher weight = better capacity
            
            elif creator_type == "blogger" and "text" in content_type:
                # Balanced approach for text content
                return await self._least_connections_routing(nodes)
            
            # Default routing
            return await self._least_connections_routing(nodes)
            
        except Exception as e:
            logger.error(f"Error in creator-aware routing: {e}")
            return nodes[0]
    
    async def _intelligent_routing(self, nodes: List[BackendNode], 
                                 request_metadata: Optional[Dict[str, Any]]) -> BackendNode:
        """Intelligent routing combining multiple factors"""
        try:
            # Score each node based on multiple factors
            node_scores = []
            
            for node in nodes:
                score = 0.0
                
                # Connection load factor (lower is better)
                if node.max_connections > 0:
                    connection_ratio = node.current_connections / node.max_connections
                    score += (1.0 - connection_ratio) * 30  # 30% weight
                
                # Response time factor (lower is better)
                if node.response_times:
                    avg_response_time = statistics.mean(node.response_times)
                    # Normalize and invert (lower time = higher score)
                    normalized_time = max(0, 1.0 - (avg_response_time / 1000))  # Assume 1000ms baseline
                    score += normalized_time * 30  # 30% weight
                
                # Success rate factor
                total_requests = node.success_count + node.failure_count
                if total_requests > 0:
                    success_rate = node.success_count / total_requests
                    score += success_rate * 25  # 25% weight
                
                # Weight factor
                weight_factor = node.weight / 100.0  # Normalize weight
                score += weight_factor * 15  # 15% weight
                
                node_scores.append((node, score))
            
            # Select node with highest score
            if node_scores:
                return max(node_scores, key=lambda x: x[1])[0]
            
            return nodes[0]
            
        except Exception as e:
            logger.error(f"Error in intelligent routing: {e}")
            return nodes[0]
    
    async def perform_health_checks(self) -> None:
        """Perform health checks on all nodes"""
        try:
            for pool in self._pools.values():
                for node in pool.nodes:
                    # Skip if recently checked
                    time_since_check = datetime.now() - node.last_health_check
                    if time_since_check.total_seconds() < pool.health_check_interval:
                        continue
                    
                    # Perform health check
                    result = await self._check_node_health(node, pool)
                    
                    # Update node status based on result
                    await self._update_node_status(node, result)
                    
                    # Store health check result
                    self._health_check_results[node.node_id].append(result)
                    
                    # Keep only recent results
                    if len(self._health_check_results[node.node_id]) > 100:
                        self._health_check_results[node.node_id] = self._health_check_results[node.node_id][-100:]
        
        except Exception as e:
            logger.error(f"Error performing health checks: {e}")
    
    async def _check_node_health(self, node: BackendNode, pool: LoadBalancerPool) -> HealthCheckResult:
        """Check health of a specific node"""
        start_time = time.perf_counter()
        
        try:
            if pool.health_check_type == HealthCheckType.HTTP:
                # Simulate HTTP health check
                # In real implementation, this would make an actual HTTP request
                response_time = random.uniform(10, 100)  # Simulate response time
                success = random.random() > 0.05  # 95% success rate simulation
                status_code = 200 if success else 500
                
                return HealthCheckResult(
                    node_id=node.node_id,
                    check_type=pool.health_check_type,
                    success=success,
                    response_time_ms=response_time,
                    status_code=status_code
                )
            
            elif pool.health_check_type == HealthCheckType.TCP:
                # Simulate TCP health check
                response_time = random.uniform(1, 20)
                success = random.random() > 0.02  # 98% success rate simulation
                
                return HealthCheckResult(
                    node_id=node.node_id,
                    check_type=pool.health_check_type,
                    success=success,
                    response_time_ms=response_time
                )
            
            else:
                # Default success
                return HealthCheckResult(
                    node_id=node.node_id,
                    check_type=pool.health_check_type,
                    success=True,
                    response_time_ms=0.0
                )
                
        except Exception as e:
            response_time = (time.perf_counter() - start_time) * 1000
            return HealthCheckResult(
                node_id=node.node_id,
                check_type=pool.health_check_type,
                success=False,
                response_time_ms=response_time,
                error_message=str(e)
            )
    
    async def _update_node_status(self, node: BackendNode, result: HealthCheckResult) -> None:
        """Update node status based on health check result"""
        try:
            node.last_health_check = datetime.now()
            
            if result.success:
                node.success_count += 1
                node.failure_count = max(0, node.failure_count - 1)  # Gradual recovery
                node.response_times.append(result.response_time_ms)
                
                # Mark as healthy if it was unhealthy
                if node.status == NodeStatus.UNHEALTHY and node.failure_count == 0:
                    node.status = NodeStatus.HEALTHY
                    logger.info(f"Node {node.node_id} recovered and marked as healthy")
            
            else:
                node.failure_count += 1
                
                # Mark as unhealthy after multiple failures
                if node.failure_count >= 3 and node.status == NodeStatus.HEALTHY:
                    node.status = NodeStatus.UNHEALTHY
                    logger.warning(f"Node {node.node_id} marked as unhealthy after {node.failure_count} failures")
        
        except Exception as e:
            logger.error(f"Error updating node status: {e}")
    
    async def update_circuit_breakers(self) -> None:
        """Update circuit breaker states for all nodes"""
        try:
            if not self.enable_circuit_breaker:
                return
            
            for pool in self._pools.values():
                for node in pool.nodes:
                    await self._update_node_circuit_breaker(node)
        
        except Exception as e:
            logger.error(f"Error updating circuit breakers: {e}")
    
    async def _update_node_circuit_breaker(self, node: BackendNode) -> None:
        """Update circuit breaker state for a specific node"""
        try:
            if node.node_id not in self._circuit_breakers:
                self._circuit_breakers[node.node_id] = {
                    "state": "closed",  # closed, open, half_open
                    "failure_count": 0,
                    "last_failure": None,
                    "next_attempt": None
                }
            
            cb = self._circuit_breakers[node.node_id]
            
            # Update based on recent health checks
            recent_results = self._health_check_results.get(node.node_id, [])
            if recent_results:
                recent_failures = sum(1 for r in recent_results[-10:] if not r.success)
                
                if cb["state"] == "closed" and recent_failures >= 3:
                    # Open circuit breaker
                    cb["state"] = "open"
                    cb["failure_count"] = recent_failures
                    cb["last_failure"] = datetime.now()
                    cb["next_attempt"] = datetime.now() + timedelta(seconds=30)
                    node.status = NodeStatus.UNHEALTHY
                    logger.warning(f"Circuit breaker opened for node {node.node_id}")
                
                elif cb["state"] == "open" and datetime.now() > cb.get("next_attempt", datetime.now()):
                    # Try half-open state
                    cb["state"] = "half_open"
                    logger.info(f"Circuit breaker half-open for node {node.node_id}")
                
                elif cb["state"] == "half_open" and recent_failures == 0:
                    # Close circuit breaker
                    cb["state"] = "closed"
                    cb["failure_count"] = 0
                    if node.status == NodeStatus.UNHEALTHY:
                        node.status = NodeStatus.HEALTHY
                    logger.info(f"Circuit breaker closed for node {node.node_id}")
        
        except Exception as e:
            logger.error(f"Error updating circuit breaker for node {node.node_id}: {e}")
    
    async def cleanup_expired_sessions(self) -> None:
        """Clean up expired sticky sessions"""
        try:
            current_time = datetime.now()
            expired_sessions = [
                session_id for session_id, timeout_time in self._session_timeouts.items()
                if current_time > timeout_time
            ]
            
            for session_id in expired_sessions:
                self._session_store.pop(session_id, None)
                self._session_timeouts.pop(session_id, None)
            
            if expired_sessions:
                logger.debug(f"Cleaned up {len(expired_sessions)} expired sessions")
        
        except Exception as e:
            logger.error(f"Error cleaning up expired sessions: {e}")
    
    async def _track_request(self, node: BackendNode, client_ip: str, 
                           session_id: str, creator_context: str) -> None:
        """Track request routing for analytics"""
        try:
            # Update node connection count
            node.current_connections += 1
            
            # Create request metrics
            metrics = RequestMetrics(
                client_ip=client_ip,
                target_node_id=node.node_id,
                creator_context=creator_context,
                routing_algorithm=self.default_algorithm  # This would be the actual algorithm used
            )
            
            self._request_metrics.append(metrics)
            
        except Exception as e:
            logger.error(f"Error tracking request: {e}")
    
    async def update_balancing_statistics(self) -> None:
        """Update load balancing statistics"""
        try:
            # Calculate node utilization
            for pool in self._pools.values():
                for node in pool.nodes:
                    if node.max_connections > 0:
                        utilization = (node.current_connections / node.max_connections) * 100
                        self._balancing_stats["node_utilization"][node.node_id] = utilization
            
            # Update request statistics
            if self._request_metrics:
                recent_requests = list(self._request_metrics)[-1000:]  # Last 1000 requests
                
                total_requests = len(recent_requests)
                successful_requests = sum(1 for r in recent_requests if 200 <= r.status_code < 400)
                
                self._balancing_stats["total_requests"] = total_requests
                self._balancing_stats["successful_requests"] = successful_requests
                self._balancing_stats["failed_requests"] = total_requests - successful_requests
                
                if recent_requests:
                    avg_response_time = statistics.mean([r.response_time_ms for r in recent_requests if r.response_time_ms > 0])
                    self._balancing_stats["avg_response_time_ms"] = avg_response_time
        
        except Exception as e:
            logger.error(f"Error updating balancing statistics: {e}")
    
    def _update_routing_stats(self, routing_time_ms: float, algorithm: LoadBalancingAlgorithm) -> None:
        """Update routing performance statistics"""
        try:
            # Update average routing time
            current_avg = self._balancing_stats["avg_routing_time_ms"]
            total_requests = self._balancing_stats["total_requests"]
            
            if total_requests > 0:
                new_avg = ((current_avg * total_requests) + routing_time_ms) / (total_requests + 1)
                self._balancing_stats["avg_routing_time_ms"] = new_avg
            else:
                self._balancing_stats["avg_routing_time_ms"] = routing_time_ms
            
            # Update algorithm usage
            self._balancing_stats["algorithm_usage"][algorithm.value] += 1
            self._balancing_stats["last_routing"] = datetime.now()
            
        except Exception as e:
            logger.error(f"Error updating routing stats: {e}")
    
    async def add_pool(self, pool_name: str, algorithm: LoadBalancingAlgorithm = None) -> LoadBalancerPool:
        """Add a new load balancer pool"""
        try:
            algorithm = algorithm or self.default_algorithm
            
            pool = LoadBalancerPool(
                pool_name=pool_name,
                algorithm=algorithm
            )
            
            self._pools[pool_name] = pool
            logger.info(f"Added load balancer pool: {pool_name}")
            
            return pool
            
        except Exception as e:
            logger.error(f"Error adding pool: {e}")
            raise
    
    async def add_node_to_pool(self, pool_name: str, node_id: str, host: str, port: int, 
                              weight: int = 100, max_connections: int = 1000) -> BackendNode:
        """Add a backend node to a pool"""
        try:
            if pool_name not in self._pools:
                raise ValueError(f"Pool '{pool_name}' does not exist")
            
            node = BackendNode(
                node_id=node_id,
                host=host,
                port=port,
                weight=weight,
                max_connections=max_connections
            )
            
            self._pools[pool_name].nodes.append(node)
            logger.info(f"Added node {node_id} to pool {pool_name}")
            
            return node
            
        except Exception as e:
            logger.error(f"Error adding node to pool: {e}")
            raise
    
    async def remove_node_from_pool(self, pool_name: str, node_id: str) -> bool:
        """Remove a backend node from a pool"""
        try:
            if pool_name not in self._pools:
                return False
            
            pool = self._pools[pool_name]
            original_count = len(pool.nodes)
            pool.nodes = [node for node in pool.nodes if node.node_id != node_id]
            
            removed = len(pool.nodes) < original_count
            if removed:
                logger.info(f"Removed node {node_id} from pool {pool_name}")
                # Clean up associated data
                self._health_check_results.pop(node_id, None)
                self._circuit_breakers.pop(node_id, None)
            
            return removed
            
        except Exception as e:
            logger.error(f"Error removing node from pool: {e}")
            return False
    
    async def add_creator_profile(self, creator_id: str, creator_type: str) -> None:
        """Add creator-specific load balancing profile"""
        try:
            profile = CreatorLoadBalancingProfile(creator_type)
            self._creator_profiles[creator_id] = profile
            logger.info(f"Added creator load balancing profile: {creator_id} ({creator_type})")
        except Exception as e:
            logger.error(f"Error adding creator profile: {e}")
    
    async def get_balancing_stats(self) -> Dict[str, Any]:
        """Get current load balancing statistics"""
        return {
            **self._balancing_stats,
            "pools": {
                pool_name: {
                    "algorithm": pool.algorithm.value,
                    "node_count": len(pool.nodes),
                    "healthy_nodes": len([n for n in pool.nodes if n.status == NodeStatus.HEALTHY]),
                    "total_connections": sum(n.current_connections for n in pool.nodes)
                }
                for pool_name, pool in self._pools.items()
            },
            "creator_profiles": len(self._creator_profiles),
            "active_sessions": len(self._session_store),
            "circuit_breakers": {
                node_id: cb["state"] for node_id, cb in self._circuit_breakers.items()
            },
            "is_running": self._is_running
        }


# Factory function for enterprise instantiation
def create_load_balancer(
    default_algorithm: str = "round_robin",
    enable_health_checks: bool = True,
    enable_sticky_sessions: bool = False
) -> LoadBalancer:
    """
    Factory function to create LoadBalancer instance
    
    Args:
        default_algorithm: Default load balancing algorithm
        enable_health_checks: Enable health checking
        enable_sticky_sessions: Enable sticky session support
    
    Returns:
        Configured LoadBalancer instance
    """
    algorithm_map = {
        "round_robin": LoadBalancingAlgorithm.ROUND_ROBIN,
        "weighted_round_robin": LoadBalancingAlgorithm.WEIGHTED_ROUND_ROBIN,
        "least_connections": LoadBalancingAlgorithm.LEAST_CONNECTIONS,
        "weighted_least_connections": LoadBalancingAlgorithm.WEIGHTED_LEAST_CONNECTIONS,
        "ip_hash": LoadBalancingAlgorithm.IP_HASH,
        "least_response_time": LoadBalancingAlgorithm.LEAST_RESPONSE_TIME,
        "creator_aware": LoadBalancingAlgorithm.CREATOR_AWARE,
        "intelligent": LoadBalancingAlgorithm.INTELLIGENT
    }
    
    algorithm = algorithm_map.get(default_algorithm, LoadBalancingAlgorithm.ROUND_ROBIN)
    
    return LoadBalancer(
        default_algorithm=algorithm,
        enable_health_checks=enable_health_checks,
        enable_sticky_sessions=enable_sticky_sessions
    )


# Export for enterprise usage
__all__ = [
    "LoadBalancer",
    "LoadBalancingAlgorithm",
    "HealthCheckType",
    "NodeStatus",
    "BackendNode",
    "LoadBalancerPool",
    "RequestMetrics",
    "HealthCheckResult",
    "CreatorLoadBalancingProfile",
    "create_load_balancer"
]