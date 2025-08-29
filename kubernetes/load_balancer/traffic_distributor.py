"""
Traffic Distributor for Load Balancer

Intelligent traffic distribution system for the IA Influencer Agent platform,
providing advanced load balancing algorithms, traffic shaping, and
dynamic routing capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ WARNING: This code is proprietary and confidential.
Unauthorized copying, distribution, or use without explicit written
permission from Fahed Mlaiel is strictly prohibited and may result
in legal action.
"""

import asyncio
import logging
import time
import hashlib
import random
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import threading
from collections import defaultdict, deque
import heapq

logger = logging.getLogger(__name__)


class LoadBalancingAlgorithm(Enum):
    """Load balancing algorithm types"""
    ROUND_ROBIN = "round_robin"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_LEAST_CONNECTIONS = "weighted_least_connections"
    LEAST_RESPONSE_TIME = "least_response_time"
    CONSISTENT_HASH = "consistent_hash"
    RESOURCE_BASED = "resource_based"
    ADAPTIVE = "adaptive"


class TrafficType(Enum):
    """Traffic classification types"""
    API_REQUEST = "api_request"
    FILE_UPLOAD = "file_upload"
    STREAMING = "streaming"
    BATCH_PROCESSING = "batch_processing"
    REALTIME = "realtime"


@dataclass
class ServerMetrics:
    """Server performance metrics"""
    active_connections: int = 0
    total_requests: int = 0
    failed_requests: int = 0
    avg_response_time: float = 0.0
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class TrafficServer:
    """Traffic server configuration and state"""
    id: str
    host: str
    port: int
    weight: int = 1
    max_connections: int = 1000
    is_healthy: bool = True
    is_backup: bool = False
    zone: str = "default"
    capabilities: List[str] = field(default_factory=list)
    metrics: ServerMetrics = field(default_factory=ServerMetrics)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        self.address = f"{self.host}:{self.port}"


@dataclass
class TrafficRequest:
    """Traffic request information"""
    id: str
    client_ip: str
    path: str
    method: str
    headers: Dict[str, str] = field(default_factory=dict)
    traffic_type: TrafficType = TrafficType.API_REQUEST
    priority: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class RoutingRule:
    """Traffic routing rule"""
    name: str
    conditions: Dict[str, Any]
    target_servers: List[str]
    algorithm: LoadBalancingAlgorithm = LoadBalancingAlgorithm.ROUND_ROBIN
    priority: int = 0
    enabled: bool = True


class ConsistentHashRing:
    """Consistent hashing implementation"""
    
    def __init__(self, replicas: int = 150):
        self.replicas = replicas
        self.ring: Dict[int, str] = {}
        self.sorted_keys: List[int] = []
        self.servers: Dict[str, TrafficServer] = {}
    
    def _hash(self, key: str) -> int:
        """Generate hash for key"""
        return int(hashlib.md5(key.encode()).hexdigest(), 16)
    
    def add_server(self, server: TrafficServer) -> None:
        """Add server to hash ring"""
        self.servers[server.id] = server
        
        for i in range(self.replicas):
            key = self._hash(f"{server.id}:{i}")
            self.ring[key] = server.id
            self.sorted_keys.append(key)
        
        self.sorted_keys.sort()
    
    def remove_server(self, server_id: str) -> None:
        """Remove server from hash ring"""
        if server_id not in self.servers:
            return
        
        del self.servers[server_id]
        
        for i in range(self.replicas):
            key = self._hash(f"{server_id}:{i}")
            if key in self.ring:
                del self.ring[key]
                self.sorted_keys.remove(key)
    
    def get_server(self, key: str) -> Optional[TrafficServer]:
        """Get server for given key"""
        if not self.ring:
            return None
        
        hash_key = self._hash(key)
        
        # Find the first server clockwise from the hash
        for ring_key in self.sorted_keys:
            if ring_key >= hash_key:
                server_id = self.ring[ring_key]
                return self.servers.get(server_id)
        
        # Wrap around to the first server
        server_id = self.ring[self.sorted_keys[0]]
        return self.servers.get(server_id)


class LoadBalancingStrategy:
    """Base class for load balancing strategies"""
    
    def __init__(self, servers: List[TrafficServer]):
        self.servers = {server.id: server for server in servers}
        self.lock = threading.RLock()
    
    def select_server(self, request: TrafficRequest) -> Optional[TrafficServer]:
        """Select server for request"""
        # Default implementation for load balancers without server selection
        logging.warning(f"Server selection not implemented for {self.__class__.__name__}")
        
        # Return first available server as fallback
        available_servers = [s for s in self.servers.values() if s.available]
        return available_servers[0] if available_servers else None
    
    def update_server_metrics(self, server_id: str, metrics: ServerMetrics) -> None:
        """Update server metrics"""
        with self.lock:
            if server_id in self.servers:
                self.servers[server_id].metrics = metrics
    
    def mark_server_unhealthy(self, server_id: str) -> None:
        """Mark server as unhealthy"""
        with self.lock:
            if server_id in self.servers:
                self.servers[server_id].is_healthy = False
    
    def mark_server_healthy(self, server_id: str) -> None:
        """Mark server as healthy"""
        with self.lock:
            if server_id in self.servers:
                self.servers[server_id].is_healthy = True
    
    def get_healthy_servers(self) -> List[TrafficServer]:
        """Get list of healthy servers"""
        with self.lock:
            return [server for server in self.servers.values() if server.is_healthy and not server.is_backup]


class RoundRobinStrategy(LoadBalancingStrategy):
    """Round Robin load balancing strategy"""
    
    def __init__(self, servers: List[TrafficServer]):
        super().__init__(servers)
        self.current_index = 0
    
    def select_server(self, request: TrafficRequest) -> Optional[TrafficServer]:
        healthy_servers = self.get_healthy_servers()
        if not healthy_servers:
            return None
        
        with self.lock:
            server = healthy_servers[self.current_index % len(healthy_servers)]
            self.current_index += 1
            return server


class WeightedRoundRobinStrategy(LoadBalancingStrategy):
    """Weighted Round Robin load balancing strategy"""
    
    def __init__(self, servers: List[TrafficServer]):
        super().__init__(servers)
        self.current_weights = {}
        self.reset_weights()
    
    def reset_weights(self):
        """Reset current weights to server weights"""
        with self.lock:
            for server in self.servers.values():
                self.current_weights[server.id] = server.weight
    
    def select_server(self, request: TrafficRequest) -> Optional[TrafficServer]:
        healthy_servers = self.get_healthy_servers()
        if not healthy_servers:
            return None
        
        with self.lock:
            # Find server with highest current weight
            selected_server = max(healthy_servers, key=lambda s: self.current_weights.get(s.id, 0))
            
            # Decrease selected server's current weight
            self.current_weights[selected_server.id] -= 1
            
            # If all weights are 0, reset them
            if all(weight <= 0 for weight in self.current_weights.values()):
                self.reset_weights()
            
            return selected_server


class LeastConnectionsStrategy(LoadBalancingStrategy):
    """Least Connections load balancing strategy"""
    
    def select_server(self, request: TrafficRequest) -> Optional[TrafficServer]:
        healthy_servers = self.get_healthy_servers()
        if not healthy_servers:
            return None
        
        with self.lock:
            return min(healthy_servers, key=lambda s: s.metrics.active_connections)


class WeightedLeastConnectionsStrategy(LoadBalancingStrategy):
    """Weighted Least Connections load balancing strategy"""
    
    def select_server(self, request: TrafficRequest) -> Optional[TrafficServer]:
        healthy_servers = self.get_healthy_servers()
        if not healthy_servers:
            return None
        
        with self.lock:
            def calculate_ratio(server):
                if server.weight == 0:
                    return float('inf')
                return server.metrics.active_connections / server.weight
            
            return min(healthy_servers, key=calculate_ratio)


class LeastResponseTimeStrategy(LoadBalancingStrategy):
    """Least Response Time load balancing strategy"""
    
    def select_server(self, request: TrafficRequest) -> Optional[TrafficServer]:
        healthy_servers = self.get_healthy_servers()
        if not healthy_servers:
            return None
        
        with self.lock:
            return min(healthy_servers, key=lambda s: s.metrics.avg_response_time)


class ConsistentHashStrategy(LoadBalancingStrategy):
    """Consistent Hash load balancing strategy"""
    
    def __init__(self, servers: List[TrafficServer]):
        super().__init__(servers)
        self.hash_ring = ConsistentHashRing()
        for server in servers:
            self.hash_ring.add_server(server)
    
    def select_server(self, request: TrafficRequest) -> Optional[TrafficServer]:
        # Use client IP and path for consistent hashing
        hash_key = f"{request.client_ip}:{request.path}"
        server = self.hash_ring.get_server(hash_key)
        
        if server and server.is_healthy:
            return server
        
        # Fallback to round robin if hash server is unhealthy
        healthy_servers = self.get_healthy_servers()
        return healthy_servers[0] if healthy_servers else None


class ResourceBasedStrategy(LoadBalancingStrategy):
    """Resource-based load balancing strategy"""
    
    def select_server(self, request: TrafficRequest) -> Optional[TrafficServer]:
        healthy_servers = self.get_healthy_servers()
        if not healthy_servers:
            return None
        
        with self.lock:
            def calculate_score(server):
                # Lower score is better
                cpu_score = server.metrics.cpu_usage
                memory_score = server.metrics.memory_usage
                connection_score = server.metrics.active_connections / server.max_connections
                response_time_score = server.metrics.avg_response_time / 1000  # Convert to seconds
                
                return cpu_score + memory_score + connection_score + response_time_score
            
            return min(healthy_servers, key=calculate_score)


class AdaptiveStrategy(LoadBalancingStrategy):
    """Adaptive load balancing strategy that switches algorithms based on conditions"""
    
    def __init__(self, servers: List[TrafficServer]):
        super().__init__(servers)
        self.strategies = {
            LoadBalancingAlgorithm.ROUND_ROBIN: RoundRobinStrategy(servers),
            LoadBalancingAlgorithm.LEAST_CONNECTIONS: LeastConnectionsStrategy(servers),
            LoadBalancingAlgorithm.LEAST_RESPONSE_TIME: LeastResponseTimeStrategy(servers),
            LoadBalancingAlgorithm.RESOURCE_BASED: ResourceBasedStrategy(servers)
        }
        self.current_algorithm = LoadBalancingAlgorithm.ROUND_ROBIN
        self.performance_history = deque(maxlen=100)
        self.last_adaptation = datetime.now()
    
    def select_server(self, request: TrafficRequest) -> Optional[TrafficServer]:
        # Adapt algorithm based on performance metrics
        self._adapt_algorithm()
        
        strategy = self.strategies[self.current_algorithm]
        return strategy.select_server(request)
    
    def _adapt_algorithm(self):
        """Adapt algorithm based on current conditions"""
        now = datetime.now()
        if now - self.last_adaptation < timedelta(minutes=5):
            return
        
        healthy_servers = self.get_healthy_servers()
        if not healthy_servers:
            return
        
        # Calculate average metrics
        avg_response_time = sum(s.metrics.avg_response_time for s in healthy_servers) / len(healthy_servers)
        avg_cpu_usage = sum(s.metrics.cpu_usage for s in healthy_servers) / len(healthy_servers)
        total_connections = sum(s.metrics.active_connections for s in healthy_servers)
        
        # Decision logic
        if avg_response_time > 1000:  # High response time
            self.current_algorithm = LoadBalancingAlgorithm.LEAST_RESPONSE_TIME
        elif avg_cpu_usage > 80:  # High CPU usage
            self.current_algorithm = LoadBalancingAlgorithm.RESOURCE_BASED
        elif total_connections > sum(s.max_connections for s in healthy_servers) * 0.8:  # High connection load
            self.current_algorithm = LoadBalancingAlgorithm.LEAST_CONNECTIONS
        else:
            self.current_algorithm = LoadBalancingAlgorithm.ROUND_ROBIN
        
        self.last_adaptation = now
        logger.info(f"Adapted load balancing algorithm to {self.current_algorithm.value}")


class TrafficDistributor:
    """Enterprise Traffic Distributor for Load Balancer"""
    
    def __init__(self):
        self.servers: Dict[str, TrafficServer] = {}
        self.routing_rules: List[RoutingRule] = []
        self.strategies: Dict[str, LoadBalancingStrategy] = {}
        self.default_algorithm = LoadBalancingAlgorithm.ROUND_ROBIN
        self.request_history = deque(maxlen=10000)
        self.traffic_stats = defaultdict(int)
        self.lock = threading.RLock()
    
    def add_server(self, server: TrafficServer) -> bool:
        """Add server to traffic distribution"""
        try:
            with self.lock:
                self.servers[server.id] = server
                self._rebuild_strategies()
            
            logger.info(f"Server {server.id} added to traffic distribution")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add server {server.id}: {e}")
            return False
    
    def remove_server(self, server_id: str) -> bool:
        """Remove server from traffic distribution"""
        try:
            with self.lock:
                if server_id in self.servers:
                    del self.servers[server_id]
                    self._rebuild_strategies()
                    logger.info(f"Server {server_id} removed from traffic distribution")
                    return True
                else:
                    logger.warning(f"Server {server_id} not found")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to remove server {server_id}: {e}")
            return False
    
    def add_routing_rule(self, rule: RoutingRule) -> bool:
        """Add traffic routing rule"""
        try:
            with self.lock:
                # Remove existing rule with same name
                self.routing_rules = [r for r in self.routing_rules if r.name != rule.name]
                self.routing_rules.append(rule)
                # Sort by priority (higher priority first)
                self.routing_rules.sort(key=lambda r: r.priority, reverse=True)
            
            logger.info(f"Routing rule {rule.name} added")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add routing rule {rule.name}: {e}")
            return False
    
    def _rebuild_strategies(self):
        """Rebuild load balancing strategies"""
        servers_list = list(self.servers.values())
        
        self.strategies = {
            LoadBalancingAlgorithm.ROUND_ROBIN.value: RoundRobinStrategy(servers_list),
            LoadBalancingAlgorithm.WEIGHTED_ROUND_ROBIN.value: WeightedRoundRobinStrategy(servers_list),
            LoadBalancingAlgorithm.LEAST_CONNECTIONS.value: LeastConnectionsStrategy(servers_list),
            LoadBalancingAlgorithm.WEIGHTED_LEAST_CONNECTIONS.value: WeightedLeastConnectionsStrategy(servers_list),
            LoadBalancingAlgorithm.LEAST_RESPONSE_TIME.value: LeastResponseTimeStrategy(servers_list),
            LoadBalancingAlgorithm.CONSISTENT_HASH.value: ConsistentHashStrategy(servers_list),
            LoadBalancingAlgorithm.RESOURCE_BASED.value: ResourceBasedStrategy(servers_list),
            LoadBalancingAlgorithm.ADAPTIVE.value: AdaptiveStrategy(servers_list)
        }
    
    def _match_routing_rule(self, request: TrafficRequest) -> Optional[RoutingRule]:
        """Find matching routing rule for request"""
        for rule in self.routing_rules:
            if not rule.enabled:
                continue
                
            match = True
            conditions = rule.conditions
            
            # Check path condition
            if 'path_prefix' in conditions and not request.path.startswith(conditions['path_prefix']):
                match = False
            
            if 'path_regex' in conditions:
                import re
                if not re.match(conditions['path_regex'], request.path):
                    match = False
            
            # Check method condition
            if 'method' in conditions and request.method != conditions['method']:
                match = False
            
            # Check header conditions
            if 'headers' in conditions:
                for header, value in conditions['headers'].items():
                    if request.headers.get(header) != value:
                        match = False
                        break
            
            # Check client IP condition
            if 'client_ip' in conditions and request.client_ip != conditions['client_ip']:
                match = False
            
            # Check traffic type condition
            if 'traffic_type' in conditions and request.traffic_type.value != conditions['traffic_type']:
                match = False
            
            if match:
                return rule
        
        return None
    
    def distribute_request(self, request: TrafficRequest) -> Optional[TrafficServer]:
        """Distribute request to appropriate server"""
        try:
            with self.lock:
                # Find matching routing rule
                rule = self._match_routing_rule(request)
                
                if rule:
                    # Use rule-specific servers and algorithm
                    rule_servers = [self.servers[sid] for sid in rule.target_servers if sid in self.servers]
                    if rule_servers:
                        strategy_key = rule.algorithm.value
                        if strategy_key in self.strategies:
                            # Create temporary strategy for rule servers
                            temp_strategy = self._create_strategy(rule.algorithm, rule_servers)
                            selected_server = temp_strategy.select_server(request)
                        else:
                            # Fallback to first available server
                            selected_server = next((s for s in rule_servers if s.is_healthy), None)
                    else:
                        selected_server = None
                else:
                    # Use default algorithm with all servers
                    strategy_key = self.default_algorithm.value
                    if strategy_key in self.strategies:
                        selected_server = self.strategies[strategy_key].select_server(request)
                    else:
                        # Fallback to round robin
                        strategy = RoundRobinStrategy(list(self.servers.values()))
                        selected_server = strategy.select_server(request)
                
                # Record request in history
                self.request_history.append({
                    'request_id': request.id,
                    'timestamp': request.timestamp,
                    'server_id': selected_server.id if selected_server else None,
                    'path': request.path,
                    'method': request.method,
                    'traffic_type': request.traffic_type.value
                })
                
                # Update traffic stats
                self.traffic_stats['total_requests'] += 1
                if selected_server:
                    self.traffic_stats[f'server_{selected_server.id}'] += 1
                    self.traffic_stats[f'traffic_type_{request.traffic_type.value}'] += 1
                else:
                    self.traffic_stats['failed_distributions'] += 1
                
                return selected_server
                
        except Exception as e:
            logger.error(f"Failed to distribute request {request.id}: {e}")
            return None
    
    def _create_strategy(self, algorithm: LoadBalancingAlgorithm, servers: List[TrafficServer]) -> LoadBalancingStrategy:
        """Create strategy instance for given algorithm and servers"""
        if algorithm == LoadBalancingAlgorithm.ROUND_ROBIN:
            return RoundRobinStrategy(servers)
        elif algorithm == LoadBalancingAlgorithm.WEIGHTED_ROUND_ROBIN:
            return WeightedRoundRobinStrategy(servers)
        elif algorithm == LoadBalancingAlgorithm.LEAST_CONNECTIONS:
            return LeastConnectionsStrategy(servers)
        elif algorithm == LoadBalancingAlgorithm.WEIGHTED_LEAST_CONNECTIONS:
            return WeightedLeastConnectionsStrategy(servers)
        elif algorithm == LoadBalancingAlgorithm.LEAST_RESPONSE_TIME:
            return LeastResponseTimeStrategy(servers)
        elif algorithm == LoadBalancingAlgorithm.CONSISTENT_HASH:
            return ConsistentHashStrategy(servers)
        elif algorithm == LoadBalancingAlgorithm.RESOURCE_BASED:
            return ResourceBasedStrategy(servers)
        elif algorithm == LoadBalancingAlgorithm.ADAPTIVE:
            return AdaptiveStrategy(servers)
        else:
            return RoundRobinStrategy(servers)
    
    def update_server_metrics(self, server_id: str, metrics: ServerMetrics) -> bool:
        """Update server metrics"""
        try:
            with self.lock:
                if server_id in self.servers:
                    self.servers[server_id].metrics = metrics
                    
                    # Update all strategies
                    for strategy in self.strategies.values():
                        strategy.update_server_metrics(server_id, metrics)
                    
                    return True
                else:
                    logger.warning(f"Server {server_id} not found for metrics update")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to update metrics for server {server_id}: {e}")
            return False
    
    def configure_platform_services(self) -> bool:
        """Configure traffic distribution for platform services"""
        try:
            # Configure servers for different services
            servers = [
                # Fingerprinting service servers
                TrafficServer(
                    id="fingerprinting-1",
                    host="fingerprint-service-1",
                    port=8001,
                    weight=3,
                    max_connections=500,
                    zone="fingerprinting",
                    capabilities=["audio_fingerprint", "video_fingerprint", "image_fingerprint"]
                ),
                TrafficServer(
                    id="fingerprinting-2",
                    host="fingerprint-service-2",
                    port=8001,
                    weight=2,
                    max_connections=400,
                    zone="fingerprinting",
                    capabilities=["audio_fingerprint", "video_fingerprint"]
                ),
                TrafficServer(
                    id="fingerprinting-3",
                    host="fingerprint-service-3",
                    port=8001,
                    weight=1,
                    max_connections=200,
                    zone="fingerprinting",
                    capabilities=["text_fingerprint"],
                    is_backup=True
                ),
                
                # Protection service servers
                TrafficServer(
                    id="protection-1",
                    host="protection-service-1",
                    port=8002,
                    weight=3,
                    max_connections=800,
                    zone="protection",
                    capabilities=["content_monitoring", "alert_processing"]
                ),
                TrafficServer(
                    id="protection-2",
                    host="protection-service-2",
                    port=8002,
                    weight=2,
                    max_connections=600,
                    zone="protection",
                    capabilities=["content_monitoring"]
                ),
                
                # Monetization service servers
                TrafficServer(
                    id="monetization-1",
                    host="monetization-service-1",
                    port=8003,
                    weight=2,
                    max_connections=300,
                    zone="monetization",
                    capabilities=["payment_processing", "revenue_tracking"]
                ),
                TrafficServer(
                    id="monetization-2",
                    host="monetization-service-2",
                    port=8003,
                    weight=2,
                    max_connections=300,
                    zone="monetization",
                    capabilities=["revenue_tracking", "analytics"]
                ),
                
                # AI Agent service servers
                TrafficServer(
                    id="ai-agent-1",
                    host="ai-agent-service-1",
                    port=8004,
                    weight=3,
                    max_connections=400,
                    zone="ai",
                    capabilities=["music_ai", "content_generation", "analytics"]
                ),
                TrafficServer(
                    id="ai-agent-2",
                    host="ai-agent-service-2",
                    port=8004,
                    weight=2,
                    max_connections=300,
                    zone="ai",
                    capabilities=["music_ai", "analytics"]
                ),
                
                # Crawler service servers
                TrafficServer(
                    id="crawler-1",
                    host="crawler-service-1",
                    port=8005,
                    weight=1,
                    max_connections=200,
                    zone="crawlers",
                    capabilities=["web_crawling", "platform_monitoring"]
                ),
                TrafficServer(
                    id="crawler-2",
                    host="crawler-service-2",
                    port=8005,
                    weight=1,
                    max_connections=200,
                    zone="crawlers",
                    capabilities=["web_crawling"]
                )
            ]
            
            # Add all servers
            for server in servers:
                self.add_server(server)
            
            # Configure routing rules
            routing_rules = [
                # High-priority rules for specific content types
                RoutingRule(
                    name="audio_fingerprinting",
                    conditions={
                        "path_prefix": "/api/v1/fingerprinting/audio",
                        "traffic_type": "file_upload"
                    },
                    target_servers=["fingerprinting-1", "fingerprinting-2"],
                    algorithm=LoadBalancingAlgorithm.LEAST_CONNECTIONS,
                    priority=100
                ),
                RoutingRule(
                    name="video_fingerprinting",
                    conditions={
                        "path_prefix": "/api/v1/fingerprinting/video",
                        "traffic_type": "file_upload"
                    },
                    target_servers=["fingerprinting-1", "fingerprinting-2"],
                    algorithm=LoadBalancingAlgorithm.RESOURCE_BASED,
                    priority=100
                ),
                RoutingRule(
                    name="text_fingerprinting",
                    conditions={
                        "path_prefix": "/api/v1/fingerprinting/text"
                    },
                    target_servers=["fingerprinting-1", "fingerprinting-2", "fingerprinting-3"],
                    algorithm=LoadBalancingAlgorithm.ROUND_ROBIN,
                    priority=90
                ),
                
                # Protection service rules
                RoutingRule(
                    name="protection_alerts",
                    conditions={
                        "path_prefix": "/api/v1/protection/alerts",
                        "traffic_type": "realtime"
                    },
                    target_servers=["protection-1", "protection-2"],
                    algorithm=LoadBalancingAlgorithm.LEAST_RESPONSE_TIME,
                    priority=95
                ),
                RoutingRule(
                    name="protection_monitoring",
                    conditions={
                        "path_prefix": "/api/v1/protection/"
                    },
                    target_servers=["protection-1", "protection-2"],
                    algorithm=LoadBalancingAlgorithm.WEIGHTED_ROUND_ROBIN,
                    priority=80
                ),
                
                # Monetization service rules (session affinity for payments)
                RoutingRule(
                    name="payment_processing",
                    conditions={
                        "path_prefix": "/api/v1/monetization/payment"
                    },
                    target_servers=["monetization-1", "monetization-2"],
                    algorithm=LoadBalancingAlgorithm.CONSISTENT_HASH,
                    priority=100
                ),
                RoutingRule(
                    name="revenue_analytics",
                    conditions={
                        "path_prefix": "/api/v1/monetization/analytics"
                    },
                    target_servers=["monetization-1", "monetization-2"],
                    algorithm=LoadBalancingAlgorithm.LEAST_CONNECTIONS,
                    priority=80
                ),
                
                # AI Agent service rules
                RoutingRule(
                    name="ai_music_generation",
                    conditions={
                        "path_prefix": "/api/v1/ai-agent/music",
                        "traffic_type": "batch_processing"
                    },
                    target_servers=["ai-agent-1", "ai-agent-2"],
                    algorithm=LoadBalancingAlgorithm.RESOURCE_BASED,
                    priority=90
                ),
                RoutingRule(
                    name="ai_analytics",
                    conditions={
                        "path_prefix": "/api/v1/ai-agent/analytics"
                    },
                    target_servers=["ai-agent-1", "ai-agent-2"],
                    algorithm=LoadBalancingAlgorithm.ADAPTIVE,
                    priority=70
                ),
                
                # Crawler service rules
                RoutingRule(
                    name="web_crawling",
                    conditions={
                        "path_prefix": "/api/v1/crawlers/"
                    },
                    target_servers=["crawler-1", "crawler-2"],
                    algorithm=LoadBalancingAlgorithm.ROUND_ROBIN,
                    priority=60
                )
            ]
            
            # Add all routing rules
            for rule in routing_rules:
                self.add_routing_rule(rule)
            
            # Set default algorithm
            self.default_algorithm = LoadBalancingAlgorithm.ADAPTIVE
            
            logger.info(f"Platform services configured: {len(servers)} servers, {len(routing_rules)} rules")
            return True
            
        except Exception as e:
            logger.error(f"Failed to configure platform services: {e}")
            return False
    
    def get_distribution_stats(self) -> Dict[str, Any]:
        """Get traffic distribution statistics"""
        with self.lock:
            # Calculate server utilization
            server_stats = {}
            for server_id, server in self.servers.items():
                utilization = (server.metrics.active_connections / server.max_connections) * 100
                server_stats[server_id] = {
                    "host": server.host,
                    "port": server.port,
                    "weight": server.weight,
                    "is_healthy": server.is_healthy,
                    "is_backup": server.is_backup,
                    "zone": server.zone,
                    "active_connections": server.metrics.active_connections,
                    "max_connections": server.max_connections,
                    "utilization_percent": round(utilization, 2),
                    "avg_response_time": server.metrics.avg_response_time,
                    "total_requests": server.metrics.total_requests,
                    "failed_requests": server.metrics.failed_requests,
                    "cpu_usage": server.metrics.cpu_usage,
                    "memory_usage": server.metrics.memory_usage
                }
            
            return {
                "servers": server_stats,
                "routing_rules": len(self.routing_rules),
                "default_algorithm": self.default_algorithm.value,
                "traffic_stats": dict(self.traffic_stats),
                "recent_requests": len(self.request_history),
                "timestamp": datetime.now().isoformat()
            }
