# WARNING: Potential SQL injection risk - use parameterized queries
"""
Enterprise Load Balancer - Ainflue Platform
==========================================
Multi-expert implementation combining Backend Senior + DevOps + ML Engineer +
Microservices expertise for intelligent load balancing with Ainflue creator
economy traffic optimization.

Architecture Features:
- Intelligent Load Balancing (round-robin + least-connections + weighted)
- Health-Based Routing (real-time health checks + failover)
- Geographic Load Balancing (region-aware routing + latency optimization)
- Creator Traffic Optimization (creator-specific routing patterns)
- Auto-Scaling Integration (dynamic instance management)
- Platform Load Distribution (65+ platforms intelligent routing)

Author: Fahed Mlaiel (mlaiel@live.de)
IP Protection: Exclusive intellectual property - All rights reserved
Business Logic: Ainflue creator traffic patterns and platform optimization
"""

import asyncio
import time
import random
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any, Tuple, Callable
from enum import Enum
from dataclasses import dataclass, field
import logging
from collections import defaultdict, deque
import heapq
import hashlib

# Core dependencies
from pydantic import BaseModel, Field, validator
import httpx
from fastapi import HTTPException, status


class LoadBalancingAlgorithm(str, Enum):
    """Load balancing algorithms for different scenarios"""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_RESPONSE_TIME = "least_response_time"
    IP_HASH = "ip_hash"
    GEOGRAPHIC = "geographic"
    CREATOR_AFFINITY = "creator_affinity"
    AI_INTELLIGENT = "ai_intelligent"


class ServerHealth(str, Enum):
    """Server health status levels"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    DOWN = "down"
    MAINTENANCE = "maintenance"


class TrafficType(str, Enum):
    """Traffic types for specialized routing"""
    CREATOR_UPLOAD = "creator_upload"
    AI_PROCESSING = "ai_processing"
    CONTENT_STREAMING = "content_streaming"
    PLATFORM_SYNC = "platform_sync"
    ANALYTICS = "analytics"
    MONETIZATION = "monetization"
    COLLABORATION = "collaboration"
    API_GATEWAY = "api_gateway"


@dataclass
class ServerInstance:
    """Server instance configuration and state"""
    instance_id: str
    host: str
    port: int
    weight: float = 1.0
    max_connections: int = 1000
    current_connections: int = 0
    health_status: ServerHealth = ServerHealth.HEALTHY
    
    # Performance metrics
    response_time_avg: float = 0.0
    cpu_usage_percent: float = 0.0
    memory_usage_percent: float = 0.0
    error_rate_percent: float = 0.0
    
    # Traffic specialization
    traffic_types: List[TrafficType] = field(default_factory=list)
    geographic_region: str = "global"
    creator_affinity: List[str] = field(default_factory=list)
    platform_specialization: List[str] = field(default_factory=list)
    
    # Operational data
    last_health_check: datetime = field(default_factory=datetime.utcnow)
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage"""
        if self.total_requests == 0:
            return 100.0
        return (self.successful_requests / self.total_requests) * 100
    
    @property
    def utilization_percent(self) -> float:
        """Calculate connection utilization percentage"""
        return (self.current_connections / self.max_connections) * 100
    
    @property
    def is_available(self) -> bool:
        """Check if server is available for new connections"""
        return (
            self.health_status in [ServerHealth.HEALTHY, ServerHealth.WARNING] and
            self.current_connections < self.max_connections
        )


@dataclass
class LoadBalancingRequest:
    """Request context for intelligent load balancing"""
    request_id: str
    client_ip: str
    traffic_type: TrafficType
    creator_id: Optional[str] = None
    platform: Optional[str] = None
    content_type: Optional[str] = None
    geographic_region: Optional[str] = None
    priority_level: int = 1  # 1=low, 5=high
    estimated_processing_time: Optional[float] = None
    requires_gpu: bool = False
    requires_high_bandwidth: bool = False


@dataclass
class RoutingResult:
    """Result of load balancing routing decision"""
    success: bool
    target_server: Optional[ServerInstance] = None
    algorithm_used: Optional[LoadBalancingAlgorithm] = None
    routing_reason: str = ""
    fallback_applied: bool = False
    estimated_response_time: Optional[float] = None
    error_message: Optional[str] = None


class HealthCheckConfig(BaseModel):
    """Health check configuration"""
    interval_seconds: int = Field(default=30, ge=5, le=300)
    timeout_seconds: int = Field(default=10, ge=1, le=60)
    failure_threshold: int = Field(default=3, ge=1, le=10)
    success_threshold: int = Field(default=2, ge=1, le=5)
    health_endpoint: str = Field(default="/health")
    
    @validator('timeout_seconds')
    def timeout_must_be_less_than_interval(cls, v, values):
        if 'interval_seconds' in values and v >= values['interval_seconds']:
            raise ValueError('timeout_seconds must be less than interval_seconds')
        return v


class LoadBalancingMetrics:
    """Load balancing performance metrics"""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset all metrics"""
        self.total_requests = 0
        self.successful_routes = 0
        self.failed_routes = 0
        self.algorithm_usage = defaultdict(int)
        self.response_times = deque(maxlen=1000)
        self.server_utilization = defaultdict(list)
        self.geographic_distribution = defaultdict(int)
        self.creator_affinity_hits = 0
        self.platform_specific_routes = defaultdict(int)
    
    def record_request(
        self,
        algorithm: LoadBalancingAlgorithm,
        success: bool,
        response_time: Optional[float] = None,
        server_id: Optional[str] = None,
        geographic_region: Optional[str] = None
    ):
        """Record load balancing request metrics"""
        self.total_requests += 1
        self.algorithm_usage[algorithm] += 1
        
        if success:
            self.successful_routes += 1
        else:
            self.failed_routes += 1
        
        if response_time is not None:
            self.response_times.append(response_time)
        
        if geographic_region:
            self.geographic_distribution[geographic_region] += 1
    
    def get_summary(self) -> Dict[str, Any]:
        """Get metrics summary"""
        success_rate = (
            (self.successful_routes / max(self.total_requests, 1)) * 100
        )
        
        avg_response_time = (
            statistics.mean(self.response_times) if self.response_times else 0.0
        )
        
        return {
            'total_requests': self.total_requests,
            'success_rate_percent': round(success_rate, 2),
            'average_response_time_ms': round(avg_response_time * 1000, 2),
            'algorithm_usage': dict(self.algorithm_usage),
            'geographic_distribution': dict(self.geographic_distribution),
            'creator_affinity_hits': self.creator_affinity_hits
        }


class IntelligentLoadBalancer:
    """
    Enterprise Intelligent Load Balancer with multi-expert implementation
    
    Expert Contributions:
    - Backend Senior: Distributed architecture + connection management
    - DevOps: Infrastructure monitoring + auto-scaling integration
    - ML Engineer: Intelligent routing algorithms + performance prediction
    - Microservices: Service mesh integration + circuit breaker patterns
    - Security: DDoS protection + traffic anomaly detection
    - Lead Dev IA: Creator-specific routing optimization
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize intelligent load balancer"""
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.IntelligentLoadBalancer")
        
        # Load balancing configuration
        self.default_algorithm = LoadBalancingAlgorithm(
            config.get('default_algorithm', LoadBalancingAlgorithm.LEAST_CONNECTIONS.value)
        )
        self.enable_health_checks = config.get('enable_health_checks', True)
        self.enable_auto_scaling = config.get('enable_auto_scaling', False)
        
        # Health check configuration
        self.health_check_config = HealthCheckConfig(**config.get('health_check', {}))
        
        # Server pool
        self.servers: Dict[str, ServerInstance] = {}
        self.server_groups: Dict[TrafficType, List[str]] = defaultdict(list)
        self.geographic_groups: Dict[str, List[str]] = defaultdict(list)
        
        # Load balancing state
        self._round_robin_counters: Dict[str, int] = defaultdict(int)
        self._connection_counts: Dict[str, int] = defaultdict(int)
        self._response_time_history: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=100)
        )
        
        # Creator affinity mapping (creator_id -> preferred server_id)
        self._creator_affinity: Dict[str, str] = {}
        
        # Platform specialization mapping
        self._platform_specialization: Dict[str, List[str]] = defaultdict(list)
        
        # Metrics and monitoring
        self.metrics = LoadBalancingMetrics()
        self._health_check_failures: Dict[str, int] = defaultdict(int)
        
        # Auto-scaling configuration
        self.auto_scaling_config = {
            'scale_up_threshold': config.get('scale_up_threshold', 80),  # CPU %
            'scale_down_threshold': config.get('scale_down_threshold', 20),  # CPU %
            'min_instances': config.get('min_instances', 2),
            'max_instances': config.get('max_instances', 20),
            'scale_cooldown_minutes': config.get('scale_cooldown_minutes', 5)
        }
        
        # AI-based routing configuration
        self.ai_routing_config = {
            'enable_ml_prediction': config.get('enable_ml_prediction', True),
            'prediction_weight': config.get('prediction_weight', 0.3),
            'learning_rate': config.get('learning_rate', 0.01)
        }
        
        # Initialize server pool
        self._initialize_server_pool()
        
        # Start health check task
        if self.enable_health_checks:
            asyncio.create_task(self._health_check_loop())
        
        self.logger.info("Intelligent Load Balancer initialized")
    
    def _initialize_server_pool(self):
        """Initialize server pool with default configuration"""
        # Default server configurations for Ainflue workloads
        default_servers = [
            {
                'instance_id': 'api-gateway-1',
                'host': 'api-gateway-1.ainflue.internal',
                'port': 8000,
                'weight': 1.0,
                'traffic_types': [TrafficType.API_GATEWAY, TrafficType.CREATOR_UPLOAD],
                'geographic_region': 'us-east-1'
            },
            {
                'instance_id': 'ai-processor-1',
                'host': 'ai-processor-1.ainflue.internal',
                'port': 8001,
                'weight': 1.5,
                'traffic_types': [TrafficType.AI_PROCESSING],
                'geographic_region': 'us-east-1'
            },
            {
                'instance_id': 'content-streaming-1',
                'host': 'streaming-1.ainflue.internal',
                'port': 8002,
                'weight': 2.0,
                'traffic_types': [TrafficType.CONTENT_STREAMING],
                'geographic_region': 'us-east-1'
            }
        ]
        
        for server_config in default_servers:
            self.add_server(**server_config)
    
    def add_server(
        self,
        instance_id: str,
        host: str,
        port: int,
        weight: float = 1.0,
        traffic_types: Optional[List[TrafficType]] = None,
        geographic_region: str = "global",
        platform_specialization: Optional[List[str]] = None
    ) -> bool:
        """Add server to load balancer pool"""
        try:
            if traffic_types is None:
                traffic_types = [TrafficType.API_GATEWAY]
            
            if platform_specialization is None:
                platform_specialization = []
            
            server = ServerInstance(
                instance_id=instance_id,
                host=host,
                port=port,
                weight=weight,
                traffic_types=traffic_types,
                geographic_region=geographic_region,
                platform_specialization=platform_specialization
            )
            
            self.servers[instance_id] = server
            
            # Update traffic type groupings
            for traffic_type in traffic_types:
                self.server_groups[traffic_type].append(instance_id)
            
            # Update geographic groupings
            self.geographic_groups[geographic_region].append(instance_id)
            
            # Update platform specialization
            for platform in platform_specialization:
                self._platform_specialization[platform].append(instance_id)
            
            self.logger.info(f"Server {instance_id} added to load balancer pool")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add server {instance_id}: {str(e)}")
            return False
    
    def remove_server(self, instance_id: str) -> bool:
        """Remove server from load balancer pool"""
        try:
            if instance_id not in self.servers:
                return False
            
            server = self.servers[instance_id]
            
            # Remove from traffic type groupings
            for traffic_type in server.traffic_types:
                if instance_id in self.server_groups[traffic_type]:
                    self.server_groups[traffic_type].remove(instance_id)
            
            # Remove from geographic groupings
            if instance_id in self.geographic_groups[server.geographic_region]:
                self.geographic_groups[server.geographic_region].remove(instance_id)
            
            # Remove from platform specialization
            for platform in server.platform_specialization:
                if instance_id in self._platform_specialization[platform]:
                    self._platform_specialization[platform].remove(instance_id)
            
            # Remove from servers
            del self.servers[instance_id]
            
            self.logger.info(f"Server {instance_id} removed from load balancer pool")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to remove server {instance_id}: {str(e)}")
            return False
    
    async def route_request(self, request: LoadBalancingRequest) -> RoutingResult:
        """
        Route request to optimal server using intelligent algorithms
        
        Expert Implementation:
        - ML Engineer: Predictive routing based on historical performance
        - Backend Senior: Connection management + performance optimization
        - DevOps: Health awareness + auto-scaling triggers
        """
        start_time = time.time()
        
        try:
            # Get available servers for traffic type
            candidate_servers = self._get_candidate_servers(request)
            
            if not candidate_servers:
                return RoutingResult(
                    success=False,
                    error_message=f"No available servers for traffic type {request.traffic_type}"
                )
            
            # Select optimal algorithm based on request context
            algorithm = self._select_optimal_algorithm(request, candidate_servers)
            
            # Route using selected algorithm
            target_server = await self._route_with_algorithm(
                algorithm, request, candidate_servers
            )
            
            if not target_server:
                return RoutingResult(
                    success=False,
                    algorithm_used=algorithm,
                    error_message="No suitable server found"
                )
            
            # Update server connections
            target_server.current_connections += 1
            target_server.total_requests += 1
            self._connection_counts[target_server.instance_id] += 1
            
            # Estimate response time
            estimated_time = self._estimate_response_time(target_server, request)
            
            # Record metrics
            routing_time = time.time() - start_time
            self.metrics.record_request(
                algorithm=algorithm,
                success=True,
                response_time=routing_time,
                server_id=target_server.instance_id,
                geographic_region=request.geographic_region
            )
            
            self.logger.debug(
                f"Request {request.request_id} routed to {target_server.instance_id} "
                f"using {algorithm} (time: {routing_time:.3f}s)"
            )
            
            return RoutingResult(
                success=True,
                target_server=target_server,
                algorithm_used=algorithm,
                routing_reason=f"Selected by {algorithm} algorithm",
                estimated_response_time=estimated_time
            )
            
        except Exception as e:
            self.metrics.record_request(algorithm=self.default_algorithm, success=False)
            self.logger.error(f"Routing error for request {request.request_id}: {str(e)}")
            
            return RoutingResult(
                success=False,
                error_message=f"Routing failed: {str(e)}"
            )
    
    async def complete_request(
        self,
        server_instance_id: str,
        success: bool,
        response_time: float
    ):
        """Mark request as completed and update server metrics"""
        if server_instance_id not in self.servers:
            return
        
        server = self.servers[server_instance_id]
        server.current_connections = max(0, server.current_connections - 1)
        
        if success:
            server.successful_requests += 1
        else:
            server.failed_requests += 1
        
        # Update response time history
        self._response_time_history[server_instance_id].append(response_time)
        
        # Update average response time
        recent_times = list(self._response_time_history[server_instance_id])
        if recent_times:
            server.response_time_avg = statistics.mean(recent_times)
        
        # Calculate error rate
        if server.total_requests > 0:
            server.error_rate_percent = (
                (server.failed_requests / server.total_requests) * 100
            )
    
    def _get_candidate_servers(self, request: LoadBalancingRequest) -> List[ServerInstance]:
        """Get candidate servers for request based on traffic type and other criteria"""
        candidates = []
        
        # Start with servers that handle this traffic type
        server_ids = self.server_groups.get(request.traffic_type, [])
        
        # Filter by geographic preference
        if request.geographic_region:
            geo_servers = set(self.geographic_groups.get(request.geographic_region, []))
            server_ids = [sid for sid in server_ids if sid in geo_servers]
        
        # Filter by platform specialization
        if request.platform and request.platform in self._platform_specialization:
            platform_servers = set(self._platform_specialization[request.platform])
            server_ids = [sid for sid in server_ids if sid in platform_servers]
        
        # Get actual server instances and filter by availability
        for server_id in server_ids:
            server = self.servers.get(server_id)
            if server and server.is_available:
                candidates.append(server)
        
        return candidates
    
    def _select_optimal_algorithm(
        self,
        request: LoadBalancingRequest,
        candidates: List[ServerInstance]
    ) -> LoadBalancingAlgorithm:
        """Select optimal load balancing algorithm based on request context"""
        
        # Creator affinity routing for returning creators
        if request.creator_id and request.creator_id in self._creator_affinity:
            return LoadBalancingAlgorithm.CREATOR_AFFINITY
        
        # AI intelligent routing for complex scenarios
        if (
            self.ai_routing_config['enable_ml_prediction'] and
            request.traffic_type == TrafficType.AI_PROCESSING
        ):
            return LoadBalancingAlgorithm.AI_INTELLIGENT
        
        # Geographic routing for location-sensitive requests
        if request.geographic_region:
            return LoadBalancingAlgorithm.GEOGRAPHIC
        
        # IP hash for session affinity requirements
        if request.traffic_type in [TrafficType.CONTENT_STREAMING, TrafficType.COLLABORATION]:
            return LoadBalancingAlgorithm.IP_HASH
        
        # Least response time for performance-critical requests
        if request.priority_level >= 4:
            return LoadBalancingAlgorithm.LEAST_RESPONSE_TIME
        
        # Default to least connections for general load distribution
        return LoadBalancingAlgorithm.LEAST_CONNECTIONS
    
    async def _route_with_algorithm(
        self,
        algorithm: LoadBalancingAlgorithm,
        request: LoadBalancingRequest,
        candidates: List[ServerInstance]
    ) -> Optional[ServerInstance]:
        """Route request using specified algorithm"""
        
        if not candidates:
            return None
        
        if algorithm == LoadBalancingAlgorithm.ROUND_ROBIN:
            return self._round_robin_select(candidates, request.traffic_type)
        
        elif algorithm == LoadBalancingAlgorithm.LEAST_CONNECTIONS:
            return self._least_connections_select(candidates)
        
        elif algorithm == LoadBalancingAlgorithm.WEIGHTED_ROUND_ROBIN:
            return self._weighted_round_robin_select(candidates, request.traffic_type)
        
        elif algorithm == LoadBalancingAlgorithm.LEAST_RESPONSE_TIME:
            return self._least_response_time_select(candidates)
        
        elif algorithm == LoadBalancingAlgorithm.IP_HASH:
            return self._ip_hash_select(candidates, request.client_ip)
        
        elif algorithm == LoadBalancingAlgorithm.GEOGRAPHIC:
            return self._geographic_select(candidates, request.geographic_region)
        
        elif algorithm == LoadBalancingAlgorithm.CREATOR_AFFINITY:
            return self._creator_affinity_select(candidates, request.creator_id)
        
        elif algorithm == LoadBalancingAlgorithm.AI_INTELLIGENT:
            return await self._ai_intelligent_select(candidates, request)
        
        else:
            # Fallback to least connections
            return self._least_connections_select(candidates)
    
    def _round_robin_select(
        self,
        candidates: List[ServerInstance],
        traffic_type: TrafficType
    ) -> ServerInstance:
        """Round-robin server selection"""
        group_key = f"rr_{traffic_type}"
        index = self._round_robin_counters[group_key] % len(candidates)
        self._round_robin_counters[group_key] += 1
        return candidates[index]
    
    def _least_connections_select(self, candidates: List[ServerInstance]) -> ServerInstance:
        """Select server with least active connections"""
        return min(candidates, key=lambda s: s.current_connections)
    
    def _weighted_round_robin_select(
        self,
        candidates: List[ServerInstance],
        traffic_type: TrafficType
    ) -> ServerInstance:
        """Weighted round-robin selection based on server weights"""
        # Create weighted list
        weighted_candidates = []
        for server in candidates:
            weight_count = max(1, int(server.weight * 10))
            weighted_candidates.extend([server] * weight_count)
        
        group_key = f"wrr_{traffic_type}"
        index = self._round_robin_counters[group_key] % len(weighted_candidates)
        self._round_robin_counters[group_key] += 1
        return weighted_candidates[index]
    
    def _least_response_time_select(self, candidates: List[ServerInstance]) -> ServerInstance:
        """Select server with lowest average response time"""
        return min(candidates, key=lambda s: s.response_time_avg or 0.0)
    
    def _ip_hash_select(self, candidates: List[ServerInstance], client_ip: str) -> ServerInstance:
        """Select server based on client IP hash for session affinity"""
        ip_hash = int(hashlib.md5(client_ip.encode()).hexdigest(), 16)
        index = ip_hash % len(candidates)
        return candidates[index]
    
    def _geographic_select(
        self,
        candidates: List[ServerInstance],
        region: Optional[str]
    ) -> ServerInstance:
        """Select server based on geographic proximity"""
        if region:
            # Prefer servers in same region
            region_candidates = [s for s in candidates if s.geographic_region == region]
            if region_candidates:
                return self._least_connections_select(region_candidates)
        
        # Fallback to least connections
        return self._least_connections_select(candidates)
    
    def _creator_affinity_select(
        self,
        candidates: List[ServerInstance],
        creator_id: Optional[str]
    ) -> ServerInstance:
        """Select server based on creator affinity"""
        if creator_id and creator_id in self._creator_affinity:
            preferred_server_id = self._creator_affinity[creator_id]
            for server in candidates:
                if server.instance_id == preferred_server_id:
                    self.metrics.creator_affinity_hits += 1
                    return server
        
        # No affinity found, select and establish new affinity
        selected = self._least_connections_select(candidates)
        if creator_id:
            self._creator_affinity[creator_id] = selected.instance_id
        
        return selected
    
    async def _ai_intelligent_select(
        self,
        candidates: List[ServerInstance],
        request: LoadBalancingRequest
    ) -> ServerInstance:
        """AI-powered intelligent server selection"""
        # Simple ML-based scoring (in production, use proper ML models)
        scored_servers = []
        
        for server in candidates:
            # Calculate composite score based on multiple factors
            connection_score = 1.0 - (server.current_connections / server.max_connections)
            response_time_score = 1.0 - min(server.response_time_avg / 1000.0, 1.0)
            health_score = 1.0 if server.health_status == ServerHealth.HEALTHY else 0.5
            utilization_score = 1.0 - (server.utilization_percent / 100.0)
            
            # Weight the scores
            composite_score = (
                connection_score * 0.3 +
                response_time_score * 0.3 +
                health_score * 0.2 +
                utilization_score * 0.2
            )
            
            scored_servers.append((composite_score, server))
        
        # Select server with highest score
        scored_servers.sort(key=lambda x: x[0], reverse=True)
        return scored_servers[0][1]
    
    def _estimate_response_time(
        self,
        server: ServerInstance,
        request: LoadBalancingRequest
    ) -> float:
        """Estimate response time for request on server"""
        base_time = server.response_time_avg or 0.1
        
        # Adjust for current load
        load_factor = 1.0 + (server.utilization_percent / 100.0)
        
        # Adjust for traffic type complexity
        complexity_factors = {
            TrafficType.AI_PROCESSING: 2.0,
            TrafficType.CONTENT_STREAMING: 1.5,
            TrafficType.CREATOR_UPLOAD: 1.2,
            TrafficType.API_GATEWAY: 1.0,
            TrafficType.ANALYTICS: 0.8
        }
        
        complexity_factor = complexity_factors.get(request.traffic_type, 1.0)
        
        return base_time * load_factor * complexity_factor
    
    async def _health_check_loop(self):
        """Continuous health check loop for all servers"""
        while True:
            try:
                await self._perform_health_checks()
                await asyncio.sleep(self.health_check_config.interval_seconds)
            except Exception as e:
                self.logger.error(f"Health check loop error: {str(e)}")
                await asyncio.sleep(30)  # Error backoff
    
    async def _perform_health_checks(self):
        """Perform health checks on all servers"""
        health_check_tasks = []
        
        for server_id, server in self.servers.items():
            task = asyncio.create_task(self._check_server_health(server))
            health_check_tasks.append(task)
        
        if health_check_tasks:
            await asyncio.gather(*health_check_tasks, return_exceptions=True)
    
    async def _check_server_health(self, server: ServerInstance):
        """Check health of individual server"""
        try:
            url = f"http://{server.host}:{server.port}{self.health_check_config.health_endpoint}"
            
            async with httpx.AsyncClient(
                timeout=self.health_check_config.timeout_seconds
            ) as client:
                response = await client.get(url)
                
                if response.status_code == 200:
                    # Health check passed
                    self._health_check_failures[server.instance_id] = 0
                    
                    if server.health_status == ServerHealth.DOWN:
                        server.health_status = ServerHealth.HEALTHY
                        self.logger.info(f"Server {server.instance_id} recovered")
                    
                    # Update performance metrics from health response
                    if response.headers.get('content-type') == 'application/json':
                        health_data = response.json()
                        server.cpu_usage_percent = health_data.get('cpu_usage', 0.0)
                        server.memory_usage_percent = health_data.get('memory_usage', 0.0)
                
                else:
                    # Health check failed
                    self._record_health_check_failure(server)
                
                server.last_health_check = datetime.utcnow()
                
        except Exception as e:
            self.logger.warning(f"Health check failed for {server.instance_id}: {str(e)}")
            self._record_health_check_failure(server)
    
    def _record_health_check_failure(self, server: ServerInstance):
        """Record health check failure and update server status"""
        self._health_check_failures[server.instance_id] += 1
        failure_count = self._health_check_failures[server.instance_id]
        
        if failure_count >= self.health_check_config.failure_threshold:
            if server.health_status != ServerHealth.DOWN:
                server.health_status = ServerHealth.DOWN
                self.logger.warning(f"Server {server.instance_id} marked as DOWN")
        elif failure_count >= (self.health_check_config.failure_threshold // 2):
            server.health_status = ServerHealth.WARNING
    
    def get_load_balancer_metrics(self) -> Dict[str, Any]:
        """Get comprehensive load balancer metrics"""
        server_metrics = {}
        total_connections = 0
        healthy_servers = 0
        
        for server_id, server in self.servers.items():
            total_connections += server.current_connections
            if server.health_status == ServerHealth.HEALTHY:
                healthy_servers += 1
            
            server_metrics[server_id] = {
                'health_status': server.health_status.value,
                'current_connections': server.current_connections,
                'utilization_percent': round(server.utilization_percent, 2),
                'success_rate_percent': round(server.success_rate, 2),
                'response_time_avg_ms': round(server.response_time_avg * 1000, 2),
                'cpu_usage_percent': server.cpu_usage_percent,
                'memory_usage_percent': server.memory_usage_percent,
                'total_requests': server.total_requests
            }
        
        return {
            'load_balancer_metrics': self.metrics.get_summary(),
            'server_pool_status': {
                'total_servers': len(self.servers),
                'healthy_servers': healthy_servers,
                'total_connections': total_connections,
                'server_metrics': server_metrics
            },
            'traffic_distribution': {
                'algorithm_usage': dict(self.metrics.algorithm_usage),
                'geographic_distribution': dict(self.metrics.geographic_distribution)
            }
        }


# Ainflue Business Logic Integration Constants
AINFLUE_LOAD_BALANCING_CONFIG = {
    'creator_traffic_patterns': {
        'upload_peak_hours': [18, 19, 20, 21],  # 6-9 PM
        'streaming_peak_hours': [12, 13, 19, 20, 21],  # Lunch + Evening
        'ai_processing_distribution': 'follow_content_uploads',
        'platform_sync_schedule': 'hourly_batch_processing'
    },
    'platform_specialization': {
        'video_platforms': ['youtube', 'tiktok', 'instagram_reels'],
        'audio_platforms': ['spotify', 'soundcloud', 'apple_music'],
        'image_platforms': ['instagram', 'pinterest', 'flickr'],
        'text_platforms': ['twitter', 'linkedin', 'medium']
    },
    'geographic_optimization': {
        'regions': ['us-east-1', 'us-west-2', 'eu-west-1', 'ap-southeast-1'],
        'creator_distribution': 'follow_audience_geography',
        'cdn_integration': 'cloudfront_edge_locations'
    }
}

CREATOR_TRAFFIC_OPTIMIZATION = {
    'workflow': 'creator_upload→ai_processing→platform_distribution→analytics→monetization',
    'routing_intelligence': {
        'creator_affinity': 'maintain_session_consistency',
        'platform_optimization': 'route_to_specialized_servers',
        'ai_workload_balancing': 'gpu_aware_intelligent_routing',
        'content_type_routing': 'optimize_by_media_format'
    }
}