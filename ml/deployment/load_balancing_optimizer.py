"""⚖️ Load Balancing Optimizer - ML-Aware Intelligent Load Distribution
====================================================================
Module: ml/deployment/load_balancing_optimizer.py
Author: Fahed Mlaiel (mlaiel@live.de)
====================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

⚖️ ML-AWARE LOAD BALANCING
Intelligent load balancing with ML workload awareness and optimization
- Creator-specific load balancing strategies
- Model complexity-aware routing
- GPU/CPU resource optimization
- Predictive load distribution
- Real-time performance monitoring
"""

import asyncio
import logging
import json
import hashlib
import uuid
import time
import numpy as np
from typing import Dict, List, Optional, Any, Tuple, Callable, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import heapq
import statistics
import random

logger = logging.getLogger(__name__)

class LoadBalancingAlgorithm(Enum):
    """Load balancing algorithms"""
    ROUND_ROBIN = "round_robin"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"
    LEAST_RESPONSE_TIME = "least_response_time"
    IP_HASH = "ip_hash"
    CONSISTENT_HASH = "consistent_hash"
    ML_AWARE = "ml_aware"
    CREATOR_AFFINITY = "creator_affinity"
    PREDICTIVE = "predictive"
    ADAPTIVE = "adaptive"

class RoutingStrategy(Enum):
    """Request routing strategies"""
    PERFORMANCE_FIRST = "performance_first"
    COST_OPTIMIZED = "cost_optimized"
    RESOURCE_BALANCED = "resource_balanced"
    LATENCY_SENSITIVE = "latency_sensitive"
    THROUGHPUT_MAXIMIZED = "throughput_maximized"
    CREATOR_OPTIMIZED = "creator_optimized"

class HealthStatus(Enum):
    """Backend health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    DRAINING = "draining"
    MAINTENANCE = "maintenance"

class RequestType(Enum):
    """ML request types"""
    INFERENCE = "inference"
    TRAINING = "training"
    FEATURE_EXTRACTION = "feature_extraction"
    MODEL_UPLOAD = "model_upload"
    BATCH_PROCESSING = "batch_processing"
    STREAMING = "streaming"
    HEALTH_CHECK = "health_check"

@dataclass
class BackendNode:
    """Backend node configuration"""
    node_id: str
    endpoint: str
    port: int = 8000
    weight: float = 1.0
    max_connections: int = 1000
    current_connections: int = 0
    health_status: HealthStatus = HealthStatus.HEALTHY
    capabilities: Set[str] = field(default_factory=set)
    resources: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    creator_affinity: List[str] = field(default_factory=list)
    last_health_check: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RequestContext:
    """Request context for routing decisions"""
    request_id: str
    request_type: RequestType = RequestType.INFERENCE
    creator_id: Optional[str] = None
    creator_type: Optional[str] = None
    model_complexity: float = 1.0  # 0.1-10.0 scale
    expected_latency: float = 100.0  # milliseconds
    resource_requirements: Dict[str, float] = field(default_factory=dict)
    priority: int = 5  # 1-10 scale
    client_ip: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RoutingDecision:
    """Load balancing routing decision"""
    decision_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    selected_node: Optional[BackendNode] = None
    algorithm_used: LoadBalancingAlgorithm = LoadBalancingAlgorithm.ROUND_ROBIN
    routing_strategy: RoutingStrategy = RoutingStrategy.PERFORMANCE_FIRST
    confidence_score: float = 1.0
    alternative_nodes: List[BackendNode] = field(default_factory=list)
    decision_factors: Dict[str, float] = field(default_factory=dict)
    execution_time: float = 0.0  # milliseconds

@dataclass
class PerformanceMetrics:
    """Node performance metrics"""
    node_id: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    response_time: float = 0.0  # milliseconds
    cpu_utilization: float = 0.0  # percentage
    gpu_utilization: float = 0.0  # percentage
    memory_utilization: float = 0.0  # percentage
    active_connections: int = 0
    requests_per_second: float = 0.0
    error_rate: float = 0.0  # percentage
    queue_length: int = 0
    throughput: float = 0.0  # requests/minute

@dataclass
class LoadBalancingStats:
    """Load balancing statistics"""
    total_requests: int = 0
    successful_routings: int = 0
    failed_routings: int = 0
    avg_response_time: float = 0.0
    algorithm_usage: Dict[LoadBalancingAlgorithm, int] = field(default_factory=dict)
    node_utilization: Dict[str, float] = field(default_factory=dict)
    creator_routing_stats: Dict[str, Dict[str, int]] = field(default_factory=dict)

class LoadBalancingOptimizer:
    """⚖️ ML-Aware Load Balancing Optimizer
    
    **MICROSERVICES + BACKEND SENIOR EXPERT IMPLEMENTATION**
    - Creator-specific load balancing strategies
    - Model complexity-aware intelligent routing
    - GPU/CPU resource optimization
    - Predictive load distribution with ML
    - Real-time performance monitoring and adaptation
    """
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        """Initialize load balancing optimizer"""
        self.config = config or {}
        
        # Core configuration
        self.default_algorithm = LoadBalancingAlgorithm(
            self.config.get("default_algorithm", "ml_aware")
        )
        self.default_strategy = RoutingStrategy(
            self.config.get("default_strategy", "performance_first")
        )
        self.health_check_interval = self.config.get("health_check_interval", 30)  # seconds
        self.adaptive_learning = self.config.get("adaptive_learning", True)
        
        # Backend nodes
        self.backend_nodes: Dict[str, BackendNode] = {}
        self.active_nodes: Set[str] = set()
        
        # Routing state
        self.round_robin_index = 0
        self.consistent_hash_ring: List[Tuple[int, str]] = []
        self.creator_affinity_map: Dict[str, str] = {}  # creator_id -> preferred_node_id
        
        # Performance tracking
        self.performance_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.routing_decisions: deque = deque(maxlen=1000)
        self.stats = LoadBalancingStats()
        
        # ML models for predictive routing
        self.latency_predictor: Optional[Dict[str, Any]] = None
        self.load_predictor: Optional[Dict[str, Any]] = None
        
        # Real-time monitoring
        self.monitoring_enabled = True
        self.last_health_check = datetime.utcnow()
        
        logger.info("⚖️ ML-Aware Load Balancing Optimizer initialized")

    async def add_backend_node(self, node -> None: BackendNode) -> None:
        """Add backend node to load balancer"""
        self.backend_nodes[node.node_id] = node
        
        # Initialize node in consistent hash ring
        await self._rebuild_consistent_hash_ring()
        
        # Add to active nodes if healthy
        if node.health_status == HealthStatus.HEALTHY:
            self.active_nodes.add(node.node_id)
        
        logger.info(f"⚖️ Added backend node: {node.node_id} ({node.endpoint}:{node.port})")

    async def remove_backend_node(self, node_id -> None: str) -> None:
        """Remove backend node from load balancer"""
        if node_id in self.backend_nodes:
            del self.backend_nodes[node_id]
            self.active_nodes.discard(node_id)
            await self._rebuild_consistent_hash_ring()
            logger.info(f"⚖️ Removed backend node: {node_id}")

    async def route_request(self, request_context: RequestContext, 
                          algorithm: Optional[LoadBalancingAlgorithm] = None,
                          strategy: Optional[RoutingStrategy] = None) -> RoutingDecision:
        """🎯 Route request to optimal backend node"""
        try:
            routing_start = time.perf_counter()
            
            # Use provided algorithm or default
            routing_algorithm = algorithm or self.default_algorithm
            routing_strategy = strategy or self.default_strategy
            
            # Get available nodes
            available_nodes = await self._get_available_nodes(request_context)
            
            if not available_nodes:
                logger.error("⚖️ No available backend nodes")
                return RoutingDecision(
                    algorithm_used=routing_algorithm,
                    routing_strategy=routing_strategy,
                    confidence_score=0.0
                )
            
            # Apply routing algorithm
            selected_node, decision_factors = await self._apply_routing_algorithm(
                routing_algorithm, available_nodes, request_context
            )
            
            # Apply routing strategy optimizations
            selected_node, strategy_factors = await self._apply_routing_strategy(
                routing_strategy, selected_node, available_nodes, request_context
            )
            
            # Combine decision factors
            decision_factors.update(strategy_factors)
            
            # Calculate confidence score
            confidence_score = await self._calculate_confidence_score(
                selected_node, available_nodes, decision_factors
            )
            
            # Create routing decision
            routing_time = (time.perf_counter() - routing_start) * 1000  # milliseconds
            
            decision = RoutingDecision(
                selected_node=selected_node,
                algorithm_used=routing_algorithm,
                routing_strategy=routing_strategy,
                confidence_score=confidence_score,
                alternative_nodes=available_nodes[:3],  # Top 3 alternatives
                decision_factors=decision_factors,
                execution_time=routing_time
            )
            
            # Update statistics
            await self._update_routing_stats(decision, request_context)
            
            # Store decision for learning
            self.routing_decisions.append(decision)
            
            # Update node connection count
            if selected_node:
                selected_node.current_connections += 1
            
            logger.debug(f"⚖️ Request routed to {selected_node.node_id if selected_node else 'None'} "
                        f"(algorithm: {routing_algorithm.value}, confidence: {confidence_score:.3f})")
            
            return decision
            
        except Exception as e:
            logger.error(f"⚖️ Request routing failed: {str(e)}")
            return RoutingDecision(
                algorithm_used=routing_algorithm or self.default_algorithm,
                routing_strategy=routing_strategy or self.default_strategy,
                confidence_score=0.0
            )

    async def _get_available_nodes(self, request_context: RequestContext) -> List[BackendNode]:
        """Get available backend nodes for request"""
        available_nodes = []
        
        for node_id in self.active_nodes:
            node = self.backend_nodes[node_id]
            
            # Check health status
            if node.health_status not in [HealthStatus.HEALTHY, HealthStatus.DEGRADED]:
                continue
            
            # Check connection capacity
            if node.current_connections >= node.max_connections:
                continue
            
            # Check capabilities if specified
            if request_context.request_type == RequestType.TRAINING:
                if "training" not in node.capabilities:
                    continue
            elif request_context.request_type == RequestType.INFERENCE:
                if "inference" not in node.capabilities:
                    continue
            
            # Check resource requirements
            if await self._check_resource_requirements(node, request_context):
                available_nodes.append(node)
        
        # Sort by current performance
        available_nodes.sort(key=lambda n: self._get_node_score(n), reverse=True)
        
        return available_nodes

    async def _check_resource_requirements(self, node: BackendNode, 
                                         request_context: RequestContext) -> bool:
        """Check if node meets resource requirements"""
        
        # Check GPU requirements
        gpu_required = request_context.resource_requirements.get("gpu", 0)
        if gpu_required > 0:
            node_gpu = node.resources.get("gpu_count", 0)
            if node_gpu == 0:
                return False
            
            # Check GPU utilization
            gpu_util = node.performance_metrics.get("gpu_utilization", 0)
            if gpu_util > 85:  # 85% threshold
                return False
        
        # Check memory requirements
        memory_required = request_context.resource_requirements.get("memory_gb", 0)
        if memory_required > 0:
            node_memory = node.resources.get("memory_gb", 0)
            memory_util = node.performance_metrics.get("memory_utilization", 0)
            available_memory = node_memory * (1 - memory_util / 100)
            
            if available_memory < memory_required:
                return False
        
        # Check model complexity support
        if request_context.model_complexity > 5.0:  # High complexity models
            if "high_compute" not in node.capabilities:
                return False
        
        return True

    def _get_node_score(self, node: BackendNode) -> float:
        """Calculate node performance score"""
        
        # Base score from weight
        score = node.weight
        
        # Adjust for current load
        load_factor = 1.0 - (node.current_connections / max(node.max_connections, 1))
        score *= load_factor
        
        # Adjust for performance metrics
        metrics = node.performance_metrics
        
        # CPU utilization (lower is better)
        cpu_util = metrics.get("cpu_utilization", 50)
        score *= (1.0 - cpu_util / 100) * 0.3 + 0.7
        
        # Response time (lower is better)
        response_time = metrics.get("response_time", 100)
        score *= max(0.1, 1.0 - response_time / 1000)  # Normalize to 1 second
        
        # Error rate (lower is better)
        error_rate = metrics.get("error_rate", 0)
        score *= max(0.1, 1.0 - error_rate / 100)
        
        # Health status adjustment
        if node.health_status == HealthStatus.DEGRADED:
            score *= 0.5
        elif node.health_status != HealthStatus.HEALTHY:
            score = 0
        
        return max(0, score)

    async def _apply_routing_algorithm(self, algorithm: LoadBalancingAlgorithm,
                                     available_nodes: List[BackendNode],
                                     request_context: RequestContext) -> Tuple[BackendNode, Dict[str, float]]:
        """Apply specific routing algorithm"""
        
        if not available_nodes:
            return None, {}
        
        decision_factors = {"algorithm": algorithm.value}
        
        if algorithm == LoadBalancingAlgorithm.ROUND_ROBIN:
            selected_node = await self._round_robin_selection(available_nodes)
            decision_factors["selection_index"] = self.round_robin_index
            
        elif algorithm == LoadBalancingAlgorithm.WEIGHTED_ROUND_ROBIN:
            selected_node = await self._weighted_round_robin_selection(available_nodes)
            decision_factors["weight_factor"] = selected_node.weight if selected_node else 0
            
        elif algorithm == LoadBalancingAlgorithm.LEAST_CONNECTIONS:
            selected_node = min(available_nodes, key=lambda n: n.current_connections)
            decision_factors["connections"] = selected_node.current_connections
            
        elif algorithm == LoadBalancingAlgorithm.LEAST_RESPONSE_TIME:
            selected_node = min(available_nodes, 
                              key=lambda n: n.performance_metrics.get("response_time", float('inf')))
            decision_factors["response_time"] = selected_node.performance_metrics.get("response_time", 0)
            
        elif algorithm == LoadBalancingAlgorithm.IP_HASH:
            selected_node = await self._ip_hash_selection(available_nodes, request_context)
            decision_factors["hash_bucket"] = hash(request_context.client_ip or "") % len(available_nodes)
            
        elif algorithm == LoadBalancingAlgorithm.CONSISTENT_HASH:
            selected_node = await self._consistent_hash_selection(available_nodes, request_context)
            decision_factors["hash_key"] = request_context.session_id or request_context.creator_id or ""
            
        elif algorithm == LoadBalancingAlgorithm.ML_AWARE:
            selected_node, ml_factors = await self._ml_aware_selection(available_nodes, request_context)
            decision_factors.update(ml_factors)
            
        elif algorithm == LoadBalancingAlgorithm.CREATOR_AFFINITY:
            selected_node = await self._creator_affinity_selection(available_nodes, request_context)
            decision_factors["creator_affinity"] = bool(request_context.creator_id)
            
        elif algorithm == LoadBalancingAlgorithm.PREDICTIVE:
            selected_node, pred_factors = await self._predictive_selection(available_nodes, request_context)
            decision_factors.update(pred_factors)
            
        elif algorithm == LoadBalancingAlgorithm.ADAPTIVE:
            selected_node, adaptive_factors = await self._adaptive_selection(available_nodes, request_context)
            decision_factors.update(adaptive_factors)
            
        else:
            # Fallback to round robin
            selected_node = await self._round_robin_selection(available_nodes)
            decision_factors["fallback"] = True
        
        return selected_node, decision_factors

    async def _round_robin_selection(self, nodes: List[BackendNode]) -> BackendNode:
        """Round robin node selection"""
        if not nodes:
            return None
        
        selected = nodes[self.round_robin_index % len(nodes)]
        self.round_robin_index = (self.round_robin_index + 1) % len(nodes)
        return selected

    async def _weighted_round_robin_selection(self, nodes: List[BackendNode]) -> BackendNode:
        """Weighted round robin selection"""
        if not nodes:
            return None
        
        # Create weighted list
        weighted_nodes = []
        for node in nodes:
            weight = max(1, int(node.weight * 10))  # Scale weight
            weighted_nodes.extend([node] * weight)
        
        if not weighted_nodes:
            return nodes[0]
        
        selected = weighted_nodes[self.round_robin_index % len(weighted_nodes)]
        self.round_robin_index = (self.round_robin_index + 1) % len(weighted_nodes)
        return selected

    async def _ip_hash_selection(self, nodes: List[BackendNode], 
                                request_context: RequestContext) -> BackendNode:
        """IP hash-based selection for session affinity"""
        if not nodes or not request_context.client_ip:
            return nodes[0] if nodes else None
        
        hash_value = hash(request_context.client_ip)
        index = hash_value % len(nodes)
        return nodes[index]

    async def _consistent_hash_selection(self, nodes: List[BackendNode], 
                                       request_context: RequestContext) -> BackendNode:
        """Consistent hash selection"""
        if not self.consistent_hash_ring or not nodes:
            return nodes[0] if nodes else None
        
        # Use session_id or creator_id for consistent routing
        key = request_context.session_id or request_context.creator_id or request_context.client_ip or ""
        hash_value = hash(key)
        
        # Find the first node in the ring with hash >= hash_value
        for ring_hash, node_id in self.consistent_hash_ring:
            if ring_hash >= hash_value and node_id in [n.node_id for n in nodes]:
                return next(n for n in nodes if n.node_id == node_id)
        
        # Wrap around to first node
        for ring_hash, node_id in self.consistent_hash_ring:
            if node_id in [n.node_id for n in nodes]:
                return next(n for n in nodes if n.node_id == node_id)
        
        return nodes[0]

    async def _ml_aware_selection(self, nodes: List[BackendNode], 
                                request_context: RequestContext) -> Tuple[BackendNode, Dict[str, float]]:
        """ML-aware intelligent selection"""
        
        if not nodes:
            return None, {}
        
        # Score each node based on ML factors
        node_scores = {}
        factors = {}
        
        for node in nodes:
            score = 0.0
            
            # Model complexity matching
            complexity_score = self._calculate_complexity_score(node, request_context.model_complexity)
            score += complexity_score * 0.3
            
            # Resource efficiency
            resource_score = self._calculate_resource_efficiency(node, request_context)
            score += resource_score * 0.3
            
            # Historical performance
            perf_score = self._calculate_performance_score(node, request_context)
            score += perf_score * 0.4
            
            node_scores[node.node_id] = score
        
        # Select node with highest score
        best_node_id = max(node_scores, key=node_scores.get)
        selected_node = next(n for n in nodes if n.node_id == best_node_id)
        
        factors.update({
            "ml_score": node_scores[best_node_id],
            "complexity_match": request_context.model_complexity,
            "resource_efficiency": self._calculate_resource_efficiency(selected_node, request_context)
        })
        
        return selected_node, factors

    def _calculate_complexity_score(self, node: BackendNode, model_complexity: float) -> float:
        """Calculate how well node matches model complexity"""
        
        # Check if node has appropriate capabilities
        if model_complexity > 7.0:  # Very high complexity
            if "gpu" in node.capabilities and "high_compute" in node.capabilities:
                return 1.0
            else:
                return 0.2
        elif model_complexity > 4.0:  # High complexity
            if "gpu" in node.capabilities:
                return 1.0
            else:
                return 0.5
        else:  # Low-medium complexity
            return 0.8 if "cpu" in node.capabilities else 1.0

    def _calculate_resource_efficiency(self, node: BackendNode, request_context: RequestContext) -> float:
        """Calculate resource utilization efficiency"""
        
        efficiency = 1.0
        
        # CPU efficiency
        cpu_util = node.performance_metrics.get("cpu_utilization", 50)
        if 30 <= cpu_util <= 70:  # Sweet spot
            efficiency *= 1.0
        elif cpu_util < 30:  # Under-utilized
            efficiency *= 0.8
        else:  # Over-utilized
            efficiency *= max(0.2, 1.0 - (cpu_util - 70) / 30)
        
        # GPU efficiency (if GPU workload)
        gpu_required = request_context.resource_requirements.get("gpu", 0)
        if gpu_required > 0:
            gpu_util = node.performance_metrics.get("gpu_utilization", 0)
            if gpu_util < 20:  # GPU under-utilized
                efficiency *= 0.6
            elif gpu_util > 90:  # GPU over-utilized
                efficiency *= 0.3
        
        # Memory efficiency
        memory_util = node.performance_metrics.get("memory_utilization", 50)
        if memory_util > 85:  # High memory usage
            efficiency *= 0.5
        
        return max(0.1, efficiency)

    def _calculate_performance_score(self, node: BackendNode, request_context: RequestContext) -> float:
        """Calculate performance score based on historical data"""
        
        # Base performance metrics
        response_time = node.performance_metrics.get("response_time", 100)
        error_rate = node.performance_metrics.get("error_rate", 0)
        throughput = node.performance_metrics.get("throughput", 10)
        
        # Normalize metrics
        response_score = max(0.1, 1.0 - response_time / 500)  # 500ms baseline
        error_score = max(0.1, 1.0 - error_rate / 100)
        throughput_score = min(1.0, throughput / 100)  # 100 req/min baseline
        
        # Weighted combination
        performance_score = (response_score * 0.4 + error_score * 0.3 + throughput_score * 0.3)
        
        # Adjust for request type
        if request_context.request_type == RequestType.TRAINING:
            # Training jobs are less latency-sensitive
            performance_score = (response_score * 0.2 + error_score * 0.4 + throughput_score * 0.4)
        elif request_context.request_type == RequestType.INFERENCE:
            # Inference is latency-sensitive
            performance_score = (response_score * 0.6 + error_score * 0.3 + throughput_score * 0.1)
        
        return performance_score

    async def _creator_affinity_selection(self, nodes: List[BackendNode], 
                                        request_context: RequestContext) -> BackendNode:
        """Creator affinity-based selection"""
        
        if not request_context.creator_id:
            return await self._round_robin_selection(nodes)
        
        # Check if creator has affinity to a specific node
        if request_context.creator_id in self.creator_affinity_map:
            preferred_node_id = self.creator_affinity_map[request_context.creator_id]
            preferred_node = next((n for n in nodes if n.node_id == preferred_node_id), None)
            
            if preferred_node:
                return preferred_node
        
        # Find node with creator type affinity
        creator_type = request_context.creator_type
        if creator_type:
            affinity_nodes = [n for n in nodes if creator_type in n.creator_affinity]
            if affinity_nodes:
                return min(affinity_nodes, key=lambda n: n.current_connections)
        
        # Fallback to least connections
        return min(nodes, key=lambda n: n.current_connections)

    async def _predictive_selection(self, nodes: List[BackendNode], 
                                  request_context: RequestContext) -> Tuple[BackendNode, Dict[str, float]]:
        """Predictive load-based selection"""
        
        if not nodes:
            return None, {}
        
        predictions = {}
        
        for node in nodes:
            # Predict future load for this node
            predicted_load = await self._predict_node_load(node, request_context)
            predicted_latency = await self._predict_response_latency(node, request_context)
            
            # Combined prediction score (lower is better)
            prediction_score = predicted_load * 0.6 + predicted_latency * 0.4
            predictions[node.node_id] = prediction_score
        
        # Select node with lowest predicted score
        best_node_id = min(predictions, key=predictions.get)
        selected_node = next(n for n in nodes if n.node_id == best_node_id)
        
        factors = {
            "predicted_load": predictions[best_node_id],
            "prediction_confidence": 0.8  # Placeholder confidence
        }
        
        return selected_node, factors

    async def _predict_node_load(self, node: BackendNode, request_context: RequestContext) -> float:
        """Predict future load on node"""
        
        # Simple time-series prediction based on recent history
        node_history = self.performance_history.get(node.node_id, deque())
        
        if len(node_history) < 5:
            # Not enough history, use current metrics
            return node.performance_metrics.get("cpu_utilization", 50) / 100
        
        # Extract CPU utilization trend
        recent_cpu = [metrics.cpu_utilization for metrics in list(node_history)[-10:]]
        
        if recent_cpu:
            # Simple linear trend prediction
            trend = (recent_cpu[-1] - recent_cpu[0]) / len(recent_cpu)
            predicted_cpu = recent_cpu[-1] + trend * 2  # Predict 2 time steps ahead
            
            return max(0, min(1, predicted_cpu / 100))
        
        return 0.5  # Default moderate load

    async def _predict_response_latency(self, node: BackendNode, request_context: RequestContext) -> float:
        """Predict response latency for request on node"""
        
        # Base latency from node performance
        base_latency = node.performance_metrics.get("response_time", 100)
        
        # Adjust for current load
        cpu_util = node.performance_metrics.get("cpu_utilization", 50)
        load_factor = 1 + (cpu_util - 50) / 100  # Increase latency with load
        
        # Adjust for model complexity
        complexity_factor = 1 + (request_context.model_complexity - 1) * 0.2
        
        # Adjust for connection count
        connection_factor = 1 + (node.current_connections / node.max_connections) * 0.5
        
        predicted_latency = base_latency * load_factor * complexity_factor * connection_factor
        
        return predicted_latency / 1000  # Normalize to 0-1 scale

    async def _adaptive_selection(self, nodes: List[BackendNode], 
                                request_context: RequestContext) -> Tuple[BackendNode, Dict[str, float]]:
        """Adaptive selection based on recent performance"""
        
        if not nodes:
            return None, {}
        
        # Analyze recent routing decisions for this request type
        recent_decisions = [
            d for d in list(self.routing_decisions)[-50:]
            if hasattr(d, 'metadata') and d.metadata.get('request_type') == request_context.request_type
        ]
        
        if len(recent_decisions) < 10:
            # Not enough data, fall back to ML-aware selection
            return await self._ml_aware_selection(nodes, request_context)
        
        # Calculate success rates for each node
        node_success_rates = {}
        for node in nodes:
            node_decisions = [d for d in recent_decisions if d.selected_node and d.selected_node.node_id == node.node_id]
            
            if node_decisions:
                # Success rate based on confidence scores (proxy for actual success)
                avg_confidence = statistics.mean(d.confidence_score for d in node_decisions)
                node_success_rates[node.node_id] = avg_confidence
            else:
                node_success_rates[node.node_id] = 0.5  # Unknown, moderate score
        
        # Select node with highest success rate
        best_node_id = max(node_success_rates, key=node_success_rates.get)
        selected_node = next(n for n in nodes if n.node_id == best_node_id)
        
        factors = {
            "adaptive_score": node_success_rates[best_node_id],
            "learning_data_points": len(recent_decisions)
        }
        
        return selected_node, factors

    async def _apply_routing_strategy(self, strategy: RoutingStrategy,
                                    selected_node: BackendNode,
                                    available_nodes: List[BackendNode],
                                    request_context: RequestContext) -> Tuple[BackendNode, Dict[str, float]]:
        """Apply routing strategy optimizations"""
        
        strategy_factors = {"strategy": strategy.value}
        
        if strategy == RoutingStrategy.PERFORMANCE_FIRST:
            # Already optimized for performance, no change needed
            return selected_node, strategy_factors
        
        elif strategy == RoutingStrategy.COST_OPTIMIZED:
            # Prefer CPU-only nodes for simple models
            if request_context.model_complexity < 3.0:
                cpu_nodes = [n for n in available_nodes if "gpu" not in n.capabilities]
                if cpu_nodes:
                    selected_node = min(cpu_nodes, key=lambda n: n.current_connections)
                    strategy_factors["cost_optimization"] = True
        
        elif strategy == RoutingStrategy.LATENCY_SENSITIVE:
            # Select node with lowest response time
            if available_nodes:
                selected_node = min(available_nodes, 
                                  key=lambda n: n.performance_metrics.get("response_time", float('inf')))
                strategy_factors["optimized_for_latency"] = True
        
        elif strategy == RoutingStrategy.THROUGHPUT_MAXIMIZED:
            # Select node with highest throughput capacity
            if available_nodes:
                selected_node = max(available_nodes,
                                  key=lambda n: n.performance_metrics.get("throughput", 0))
                strategy_factors["optimized_for_throughput"] = True
        
        elif strategy == RoutingStrategy.RESOURCE_BALANCED:
            # Select node with most balanced resource utilization
            if available_nodes:
                def balance_score(node) -> None:
                    cpu = node.performance_metrics.get("cpu_utilization", 50)
                    memory = node.performance_metrics.get("memory_utilization", 50)
                    gpu = node.performance_metrics.get("gpu_utilization", 0)
                    
                    # Calculate variance (lower is more balanced)
                    resources = [cpu, memory] + ([gpu] if gpu > 0 else [])
                    return -np.var(resources) if len(resources) > 1 else -cpu
                
                selected_node = max(available_nodes, key=balance_score)
                strategy_factors["resource_balanced"] = True
        
        elif strategy == RoutingStrategy.CREATOR_OPTIMIZED:
            # Already handled in creator affinity selection
            strategy_factors["creator_optimized"] = bool(request_context.creator_id)
        
        return selected_node, strategy_factors

    async def _calculate_confidence_score(self, selected_node: Optional[BackendNode],
                                        available_nodes: List[BackendNode],
                                        decision_factors: Dict[str, float]) -> float:
        """Calculate confidence score for routing decision"""
        
        if not selected_node:
            return 0.0
        
        confidence = 1.0
        
        # Reduce confidence if node is under stress
        cpu_util = selected_node.performance_metrics.get("cpu_utilization", 50)
        if cpu_util > 80:
            confidence *= 0.7
        elif cpu_util > 90:
            confidence *= 0.4
        
        # Reduce confidence if node has high error rate
        error_rate = selected_node.performance_metrics.get("error_rate", 0)
        confidence *= max(0.2, 1.0 - error_rate / 100)
        
        # Reduce confidence if limited alternatives
        if len(available_nodes) < 2:
            confidence *= 0.8
        
        # Adjust based on health status
        if selected_node.health_status == HealthStatus.DEGRADED:
            confidence *= 0.6
        
        # Adjust based on connection load
        load_ratio = selected_node.current_connections / selected_node.max_connections
        if load_ratio > 0.8:
            confidence *= 0.7
        
        return max(0.1, min(1.0, confidence))

    async def _update_routing_stats(self, decision -> None: RoutingDecision, request_context -> None: RequestContext) -> None:
        """Update routing statistics"""
        
        self.stats.total_requests += 1
        
        if decision.selected_node:
            self.stats.successful_routings += 1
            
            # Update algorithm usage
            algorithm = decision.algorithm_used
            self.stats.algorithm_usage[algorithm] = self.stats.algorithm_usage.get(algorithm, 0) + 1
            
            # Update node utilization
            node_id = decision.selected_node.node_id
            self.stats.node_utilization[node_id] = self.stats.node_utilization.get(node_id, 0) + 1
            
            # Update creator routing stats
            if request_context.creator_id:
                creator_id = request_context.creator_id
                if creator_id not in self.stats.creator_routing_stats:
                    self.stats.creator_routing_stats[creator_id] = {}
                
                self.stats.creator_routing_stats[creator_id][node_id] = (
                    self.stats.creator_routing_stats[creator_id].get(node_id, 0) + 1
                )
        else:
            self.stats.failed_routings += 1

    async def _rebuild_consistent_hash_ring(self) -> None:
        """Rebuild consistent hash ring for consistent hashing"""
        
        self.consistent_hash_ring = []
        
        for node_id, node in self.backend_nodes.items():
            # Create multiple hash points for better distribution
            for i in range(100):  # 100 virtual nodes per physical node
                hash_key = f"{node_id}:{i}"
                hash_value = hash(hash_key) % (2**32)
                self.consistent_hash_ring.append((hash_value, node_id))
        
        # Sort by hash value
        self.consistent_hash_ring.sort()

    async def update_node_metrics(self, node_id -> None: str, metrics -> None: PerformanceMetrics) -> None:
        """Update performance metrics for a node"""
        
        if node_id not in self.backend_nodes:
            return
        
        node = self.backend_nodes[node_id]
        
        # Update performance metrics
        node.performance_metrics.update({
            "response_time": metrics.response_time,
            "cpu_utilization": metrics.cpu_utilization,
            "gpu_utilization": metrics.gpu_utilization,
            "memory_utilization": metrics.memory_utilization,
            "requests_per_second": metrics.requests_per_second,
            "error_rate": metrics.error_rate,
            "throughput": metrics.throughput
        })
        
        # Update connection count
        node.current_connections = metrics.active_connections
        
        # Store metrics history
        self.performance_history[node_id].append(metrics)
        
        # Update health status based on metrics
        await self._update_node_health_status(node_id, metrics)

    async def _update_node_health_status(self, node_id -> None: str, metrics -> None: PerformanceMetrics) -> None:
        """Update node health status based on metrics"""
        
        node = self.backend_nodes[node_id]
        
        # Determine health status
        if (metrics.error_rate > 10 or 
            metrics.cpu_utilization > 95 or 
            metrics.response_time > 2000):
            new_status = HealthStatus.UNHEALTHY
        elif (metrics.error_rate > 5 or 
              metrics.cpu_utilization > 85 or 
              metrics.response_time > 1000):
            new_status = HealthStatus.DEGRADED
        else:
            new_status = HealthStatus.HEALTHY
        
        # Update status if changed
        if node.health_status != new_status:
            old_status = node.health_status
            node.health_status = new_status
            node.last_health_check = datetime.utcnow()
            
            # Update active nodes set
            if new_status in [HealthStatus.HEALTHY, HealthStatus.DEGRADED]:
                self.active_nodes.add(node_id)
            else:
                self.active_nodes.discard(node_id)
            
            logger.info(f"⚖️ Node {node_id} health status changed: {old_status.value} → {new_status.value}")

    async def get_load_balancing_dashboard(self) -> Dict[str, Any]:
        """📊 Generate load balancing dashboard"""
        
        # Current status
        total_nodes = len(self.backend_nodes)
        active_nodes = len(self.active_nodes)
        total_connections = sum(node.current_connections for node in self.backend_nodes.values())
        
        current_status = {
            "total_nodes": total_nodes,
            "active_nodes": active_nodes,
            "total_connections": total_connections,
            "default_algorithm": self.default_algorithm.value,
            "default_strategy": self.default_strategy.value
        }
        
        # Node status breakdown
        node_status = {
            "healthy": len([n for n in self.backend_nodes.values() if n.health_status == HealthStatus.HEALTHY]),
            "degraded": len([n for n in self.backend_nodes.values() if n.health_status == HealthStatus.DEGRADED]),
            "unhealthy": len([n for n in self.backend_nodes.values() if n.health_status == HealthStatus.UNHEALTHY]),
            "maintenance": len([n for n in self.backend_nodes.values() if n.health_status == HealthStatus.MAINTENANCE])
        }
        
        # Performance metrics
        if self.backend_nodes:
            avg_response_time = statistics.mean(
                node.performance_metrics.get("response_time", 0) 
                for node in self.backend_nodes.values()
            )
            avg_cpu_utilization = statistics.mean(
                node.performance_metrics.get("cpu_utilization", 0) 
                for node in self.backend_nodes.values()
            )
            total_throughput = sum(
                node.performance_metrics.get("throughput", 0) 
                for node in self.backend_nodes.values()
            )
        else:
            avg_response_time = 0
            avg_cpu_utilization = 0
            total_throughput = 0
        
        performance_metrics = {
            "avg_response_time": round(avg_response_time, 2),
            "avg_cpu_utilization": round(avg_cpu_utilization, 2),
            "total_throughput": round(total_throughput, 2),
            "success_rate": (self.stats.successful_routings / max(self.stats.total_requests, 1)) * 100
        }
        
        # Algorithm usage statistics
        algorithm_stats = {
            algorithm.value: count 
            for algorithm, count in self.stats.algorithm_usage.items()
        }
        
        # Node utilization distribution
        node_utilization = {
            node_id: {
                "requests_routed": count,
                "current_connections": self.backend_nodes[node_id].current_connections,
                "health_status": self.backend_nodes[node_id].health_status.value,
                "utilization_percentage": round((count / max(self.stats.total_requests, 1)) * 100, 2)
            }
            for node_id, count in self.stats.node_utilization.items()
            if node_id in self.backend_nodes
        }
        
        # Recent routing decisions
        recent_decisions = list(self.routing_decisions)[-10:]
        decision_summary = [
            {
                "timestamp": decision.timestamp.isoformat(),
                "algorithm": decision.algorithm_used.value,
                "strategy": decision.routing_strategy.value,
                "selected_node": decision.selected_node.node_id if decision.selected_node else None,
                "confidence": round(decision.confidence_score, 3),
                "execution_time": round(decision.execution_time, 2)
            }
            for decision in recent_decisions
        ]
        
        return {
            "current_status": current_status,
            "node_status": node_status,
            "performance_metrics": performance_metrics,
            "algorithm_usage": algorithm_stats,
            "node_utilization": node_utilization,
            "recent_decisions": decision_summary,
            "creator_routing_stats": dict(self.stats.creator_routing_stats)
        }

    def __repr__(self) -> str:
        return f"LoadBalancingOptimizer(nodes={len(self.backend_nodes)}, active={len(self.active_nodes)}, algorithm={self.default_algorithm.value})"

# ⚖️ MICROSERVICES + BACKEND SENIOR EXPERT - ML-Aware Load Balancing Complete
# Creator-specific routing, predictive load distribution, and intelligent performance optimization