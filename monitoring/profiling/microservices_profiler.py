"""🏗️ Microservices Performance Profiler
=========================================

Advanced microservices architecture performance profiling system for the Ainflue Creator Economy platform.
Monitors service-to-service communication, load balancing, circuit breakers, and distributed transactions.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ INTELLECTUAL PROPERTY WARNING:
=====================================
This code is proprietary to Fahed Mlaiel <mlaiel@live.de>
- Commercial use FORBIDDEN without written authorization
- Reverse engineering STRICTLY PROHIBITED
- Distribution FORBIDDEN without explicit license
- Violation = Automatic legal prosecution

🏢 ENTERPRISE USAGE:
- Enterprise license available on request
- Technical support included with license
- Maintenance and updates assured
- Technical team training provided
"""

import asyncio
import logging
import time
import threading
from typing import Dict, List, Optional, Any, Callable, Union, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import statistics
from collections import defaultdict, deque
import uuid

from prometheus_client import Counter, Gauge, Histogram, Summary

logger = logging.getLogger(__name__)


class ServiceType(Enum):
    """Types of microservices"""
    API_GATEWAY = "api_gateway"
    AUTHENTICATION = "authentication"
    USER_MANAGEMENT = "user_management"
    CREATOR_PROFILES = "creator_profiles"
    CONTENT_MANAGEMENT = "content_management"
    AI_PROCESSING = "ai_processing"
    COLLABORATION = "collaboration"
    MONETIZATION = "monetization"
    ANALYTICS = "analytics"
    NOTIFICATION = "notification"
    SEARCH = "search"
    DISTRIBUTION = "distribution"
    LOAD_BALANCER = "load_balancer"
    MESSAGE_QUEUE = "message_queue"
    DATABASE = "database"
    CACHE = "cache"


class CommunicationPattern(Enum):
    """Microservice communication patterns"""
    SYNCHRONOUS = "synchronous"
    ASYNCHRONOUS = "asynchronous"
    EVENT_DRIVEN = "event_driven"
    REQUEST_RESPONSE = "request_response"
    PUBLISH_SUBSCRIBE = "publish_subscribe"
    SAGA = "saga"
    CHOREOGRAPHY = "choreography"
    ORCHESTRATION = "orchestration"


class CircuitBreakerState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class ServiceHealth(Enum):
    """Service health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class ServiceEndpoint:
    """Microservice endpoint information"""
    service_name: str
    service_type: ServiceType
    service_version: str
    host: str
    port: int
    health_check_url: str
    
    # Service metadata
    instance_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    region: Optional[str] = None
    cluster: Optional[str] = None
    namespace: str = "default"
    
    # Load balancing
    weight: float = 1.0
    max_connections: int = 1000
    current_connections: int = 0


@dataclass
class ServiceCommunicationMetadata:
    """Metadata for service-to-service communication"""
    request_id: str
    source_service: ServiceEndpoint
    destination_service: ServiceEndpoint
    communication_pattern: CommunicationPattern
    
    # Request details
    operation_name: str
    payload_size_bytes: int
    headers_count: int
    
    # Routing information
    load_balancer_used: bool = False
    selected_instance: Optional[str] = None
    routing_strategy: str = "round_robin"
    
    # Circuit breaker
    circuit_breaker_state: CircuitBreakerState = CircuitBreakerState.CLOSED
    
    # Tracing
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    parent_span_id: Optional[str] = None
    
    # Security
    authentication_method: str = "jwt"
    authorization_required: bool = True


@dataclass
class MicroservicesMetrics:
    """Microservices performance metrics"""
    request_id: str
    metadata: ServiceCommunicationMetadata
    
    # Performance metrics (all in milliseconds)
    total_time_ms: float
    service_discovery_time_ms: Optional[float] = None
    load_balancing_time_ms: Optional[float] = None
    circuit_breaker_time_ms: Optional[float] = None
    auth_time_ms: Optional[float] = None
    network_time_ms: Optional[float] = None
    processing_time_ms: Optional[float] = None
    serialization_time_ms: Optional[float] = None
    deserialization_time_ms: Optional[float] = None
    
    # Service mesh metrics
    sidecar_overhead_ms: Optional[float] = None
    proxy_time_ms: Optional[float] = None
    tls_handshake_time_ms: Optional[float] = None
    
    # Load balancing metrics
    instances_available: int = 1
    instance_selected: Optional[str] = None
    load_balancing_algorithm: str = "round_robin"
    
    # Circuit breaker metrics
    circuit_breaker_triggered: bool = False
    fallback_used: bool = False
    
    # Resource usage
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    
    # Quality metrics
    success: bool = True
    error_message: Optional[str] = None
    error_type: Optional[str] = None
    retry_count: int = 0
    
    # Response metrics
    response_size_bytes: int = 0
    status_code: Optional[int] = None
    
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class MicroservicesBottleneck:
    """Microservices performance bottleneck detection"""
    bottleneck_id: str
    source_service: str
    destination_service: str
    communication_pattern: CommunicationPattern
    
    # Bottleneck details
    bottleneck_type: str  # "high_latency", "circuit_breaker", "load_balancer", "service_discovery"
    severity: str  # "low", "medium", "high", "critical"
    description: str
    
    # Performance impact
    current_performance: Dict[str, float]
    expected_performance: Dict[str, float]
    impact_percentage: float
    
    # Affected services
    affected_services: List[str]
    affected_operations: List[str]
    
    # Service mesh analysis
    service_mesh_analysis: Dict[str, Any]
    load_balancing_analysis: Dict[str, Any]
    
    # Optimization recommendations
    recommendations: List[str]
    estimated_improvement: Dict[str, float]
    
    timestamp: datetime = field(default_factory=datetime.utcnow)


class MicroservicesProfiler:
    """Advanced microservices performance profiler"""
    
    def __init__(self,
                 monitoring_interval: float = 5.0,
                 max_history_size: int = 10000,
                 enable_distributed_tracing: bool = True,
                 enable_circuit_breaker_monitoring: bool = True,
                 service_timeout_threshold_ms: float = 5000.0):
        """
        Initialize microservices profiler
        
        Args:
            monitoring_interval: Monitoring interval in seconds
            max_history_size: Maximum number of metrics to store
            enable_distributed_tracing: Enable distributed tracing
            enable_circuit_breaker_monitoring: Enable circuit breaker monitoring
            service_timeout_threshold_ms: Threshold for service timeout detection
        """
        self.monitoring_interval = monitoring_interval
        self.max_history_size = max_history_size
        self.enable_distributed_tracing = enable_distributed_tracing
        self.enable_circuit_breaker_monitoring = enable_circuit_breaker_monitoring
        self.service_timeout_threshold_ms = service_timeout_threshold_ms
        
        # Storage for metrics
        self.metrics_history: deque = deque(maxlen=max_history_size)
        self.active_requests: Dict[str, MicroservicesMetrics] = {}
        self.bottlenecks: List[MicroservicesBottleneck] = []
        
        # Service registry and discovery
        self.service_registry: Dict[str, List[ServiceEndpoint]] = defaultdict(list)
        self.service_health: Dict[str, ServiceHealth] = {}
        
        # Circuit breaker states
        self.circuit_breakers: Dict[str, CircuitBreakerState] = defaultdict(lambda: CircuitBreakerState.CLOSED)
        self.circuit_breaker_counters: Dict[str, Dict[str, int]] = defaultdict(lambda: {"failures": 0, "successes": 0})
        
        # Load balancing metrics
        self.load_balancing_stats: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        
        # Communication patterns tracking
        self.service_communication_graph: Dict[str, Set[str]] = defaultdict(set)
        self.communication_patterns: Dict[str, List[float]] = defaultdict(list)
        
        # Performance thresholds
        self.thresholds = {
            'max_service_time_ms': service_timeout_threshold_ms,
            'max_circuit_breaker_failures': 5,
            'max_load_balancer_time_ms': 100.0,
            'max_service_discovery_time_ms': 500.0,
            'max_error_rate_percent': 5.0
        }
        
        # Monitoring state
        self.is_monitoring = False
        self.monitoring_task: Optional[asyncio.Task] = None
        self._lock = threading.Lock()
        
        # Prometheus metrics
        self._init_prometheus_metrics()
        
        logger.info("MicroservicesProfiler initialized for Creator Economy platform")
    
    def _init_prometheus_metrics(self):
        """Initialize Prometheus metrics"""
        self.prometheus_metrics = {
            'service_request_duration': Histogram(
                'ainflue_service_request_duration_seconds',
                'Duration of service-to-service requests',
                ['source_service', 'destination_service', 'operation', 'status']
            ),
            'service_communication_count': Counter(
                'ainflue_service_communication_total',
                'Total service communications',
                ['source_service', 'destination_service', 'pattern']
            ),
            'circuit_breaker_state': Gauge(
                'ainflue_circuit_breaker_state',
                'Circuit breaker state (0=closed, 1=open, 2=half-open)',
                ['source_service', 'destination_service']
            ),
            'service_discovery_duration': Histogram(
                'ainflue_service_discovery_duration_seconds',
                'Duration of service discovery',
                ['service_type', 'discovery_method']
            ),
            'load_balancer_requests': Counter(
                'ainflue_load_balancer_requests_total',
                'Total load balancer requests',
                ['algorithm', 'destination_service']
            ),
            'service_errors': Counter(
                'ainflue_service_errors_total',
                'Total service errors',
                ['source_service', 'destination_service', 'error_type']
            ),
            'service_instances': Gauge(
                'ainflue_service_instances_available',
                'Number of available service instances',
                ['service_name', 'service_type']
            ),
            'microservices_bottlenecks': Gauge(
                'ainflue_microservices_bottlenecks_active',
                'Number of active microservices bottlenecks',
                ['service', 'severity']
            )
        }
    
    async def start_monitoring(self):
        """Start continuous microservices monitoring"""
        if self.is_monitoring:
            logger.warning("Microservices monitoring already running")
            return
        
        self.is_monitoring = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Microservices monitoring started")
    
    async def stop_monitoring(self):
        """Stop microservices monitoring"""
        if not self.is_monitoring:
            return
        
        self.is_monitoring = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Microservices monitoring stopped")
    
    async def profile_service_communication(self,
                                          metadata: ServiceCommunicationMetadata,
                                          service_func: Callable,
                                          *args, **kwargs) -> MicroservicesMetrics:
        """
        Profile a service-to-service communication
        
        Args:
            metadata: Service communication metadata
            service_func: Function to execute and profile
            *args, **kwargs: Arguments for the service function
        
        Returns:
            MicroservicesMetrics: Detailed performance metrics
        """
        start_time = time.time()
        
        # Initialize metrics
        metrics = MicroservicesMetrics(
            request_id=metadata.request_id,
            metadata=metadata,
            total_time_ms=0.0
        )
        
        try:
            # Service discovery timing
            if self.enable_distributed_tracing:
                discovery_start = time.time()
                await self._perform_service_discovery(metadata.destination_service)
                discovery_end = time.time()
                metrics.service_discovery_time_ms = (discovery_end - discovery_start) * 1000
            
            # Load balancing timing
            if metadata.load_balancer_used:
                lb_start = time.time()
                selected_instance = await self._perform_load_balancing(metadata.destination_service)
                lb_end = time.time()
                metrics.load_balancing_time_ms = (lb_end - lb_start) * 1000
                metrics.instance_selected = selected_instance
                metadata.selected_instance = selected_instance
            
            # Circuit breaker check
            if self.enable_circuit_breaker_monitoring:
                cb_start = time.time()
                circuit_state = await self._check_circuit_breaker(metadata)
                cb_end = time.time()
                metrics.circuit_breaker_time_ms = (cb_end - cb_start) * 1000
                
                if circuit_state == CircuitBreakerState.OPEN:
                    metrics.circuit_breaker_triggered = True
                    metrics.fallback_used = True
                    # Execute fallback instead of actual service call
                    result = await self._execute_fallback(metadata, service_func, *args, **kwargs)
                else:
                    # Execute actual service call
                    processing_start = time.time()
                    result = await self._execute_service_operation(service_func, *args, **kwargs)
                    processing_end = time.time()
                    metrics.processing_time_ms = (processing_end - processing_start) * 1000
            else:
                # Execute service call without circuit breaker
                processing_start = time.time()
                result = await self._execute_service_operation(service_func, *args, **kwargs)
                processing_end = time.time()
                metrics.processing_time_ms = (processing_end - processing_start) * 1000
            
            # Calculate total time
            end_time = time.time()
            metrics.total_time_ms = (end_time - start_time) * 1000
            
            # Extract response metrics
            metrics = await self._extract_service_response_metrics(result, metrics)
            
            # Update circuit breaker state
            if self.enable_circuit_breaker_monitoring:
                await self._update_circuit_breaker(metadata, metrics.success)
            
            # Set success
            metrics.success = True
            
            # Store metrics
            await self._store_metrics(metrics)
            
            # Update service communication graph
            await self._update_communication_graph(metadata)
            
            # Update Prometheus metrics
            self._update_prometheus_metrics(metrics)
            
            # Track communication patterns
            await self._track_communication_patterns(metrics)
            
            # Check for bottlenecks
            await self._detect_bottlenecks(metrics)
            
            logger.debug(f"Service communication profiled: {metadata.request_id} - {metrics.total_time_ms:.2f}ms")
            return metrics
            
        except Exception as e:
            # Handle service failure
            end_time = time.time()
            metrics.total_time_ms = (end_time - start_time) * 1000
            metrics.success = False
            metrics.error_message = str(e)
            metrics.error_type = type(e).__name__
            
            # Update circuit breaker on failure
            if self.enable_circuit_breaker_monitoring:
                await self._update_circuit_breaker(metadata, False)
            
            await self._store_metrics(metrics)
            self.prometheus_metrics['service_errors'].labels(
                source_service=metadata.source_service.service_name,
                destination_service=metadata.destination_service.service_name,
                error_type=metrics.error_type
            ).inc()
            
            logger.error(f"Service communication failed: {metadata.request_id} - {e}")
            return metrics
    
    async def _perform_service_discovery(self, service: ServiceEndpoint):
        """Perform service discovery"""
        try:
            # Simulate service discovery
            await asyncio.sleep(0.001)  # Simulated discovery time
            
            # Update service registry
            service_key = f"{service.service_name}:{service.service_type.value}"
            with self._lock:
                if service not in self.service_registry[service_key]:
                    self.service_registry[service_key].append(service)
                    self.service_health[service.instance_id] = ServiceHealth.HEALTHY
        
        except Exception as e:
            logger.warning(f"Service discovery failed for {service.service_name}: {e}")
    
    async def _perform_load_balancing(self, service: ServiceEndpoint) -> str:
        """Perform load balancing to select service instance"""
        try:
            service_key = f"{service.service_name}:{service.service_type.value}"
            available_instances = self.service_registry.get(service_key, [service])
            
            # Simple round-robin load balancing
            if available_instances:
                # Find instance with lowest current connections
                selected = min(available_instances, key=lambda x: x.current_connections)
                selected.current_connections += 1
                
                # Update load balancing stats
                with self._lock:
                    self.load_balancing_stats[service_key][selected.instance_id] += 1
                
                return selected.instance_id
            
            return service.instance_id
        
        except Exception as e:
            logger.warning(f"Load balancing failed for {service.service_name}: {e}")
            return service.instance_id
    
    async def _check_circuit_breaker(self, metadata: ServiceCommunicationMetadata) -> CircuitBreakerState:
        """Check circuit breaker state"""
        service_key = f"{metadata.source_service.service_name}->{metadata.destination_service.service_name}"
        
        with self._lock:
            current_state = self.circuit_breakers[service_key]
            counters = self.circuit_breaker_counters[service_key]
            
            # Circuit breaker logic
            if current_state == CircuitBreakerState.CLOSED:
                if counters["failures"] >= self.thresholds['max_circuit_breaker_failures']:
                    self.circuit_breakers[service_key] = CircuitBreakerState.OPEN
                    logger.warning(f"Circuit breaker opened for {service_key}")
                    return CircuitBreakerState.OPEN
            
            elif current_state == CircuitBreakerState.OPEN:
                # Transition to half-open after timeout (simplified)
                self.circuit_breakers[service_key] = CircuitBreakerState.HALF_OPEN
                return CircuitBreakerState.HALF_OPEN
            
            elif current_state == CircuitBreakerState.HALF_OPEN:
                if counters["successes"] >= 3:  # Threshold for closing
                    self.circuit_breakers[service_key] = CircuitBreakerState.CLOSED
                    counters["failures"] = 0
                    return CircuitBreakerState.CLOSED
            
            return current_state
    
    async def _update_circuit_breaker(self, metadata: ServiceCommunicationMetadata, success: bool):
        """Update circuit breaker counters"""
        service_key = f"{metadata.source_service.service_name}->{metadata.destination_service.service_name}"
        
        with self._lock:
            counters = self.circuit_breaker_counters[service_key]
            
            if success:
                counters["successes"] += 1
                counters["failures"] = max(0, counters["failures"] - 1)  # Decay failures
            else:
                counters["failures"] += 1
                counters["successes"] = 0
    
    async def _execute_fallback(self, metadata: ServiceCommunicationMetadata, service_func: Callable, *args, **kwargs):
        """Execute fallback when circuit breaker is open"""
        # Simulate fallback response
        await asyncio.sleep(0.001)
        return {
            "status": "fallback",
            "message": "Circuit breaker open, using fallback",
            "data": None
        }
    
    async def _execute_service_operation(self, operation_func: Callable, *args, **kwargs):
        """Execute service operation with proper async handling"""
        if asyncio.iscoroutinefunction(operation_func):
            return await operation_func(*args, **kwargs)
        else:
            return operation_func(*args, **kwargs)
    
    async def _extract_service_response_metrics(self, result: Any, metrics: MicroservicesMetrics) -> MicroservicesMetrics:
        """Extract response metrics from service operation result"""
        if isinstance(result, dict):
            metrics.status_code = result.get('status_code', 200)
            metrics.response_size_bytes = len(json.dumps(result)) if result else 0
        else:
            metrics.response_size_bytes = len(str(result)) if result else 0
        
        return metrics
    
    async def _store_metrics(self, metrics: MicroservicesMetrics):
        """Store metrics in history"""
        with self._lock:
            self.metrics_history.append(metrics)
            self.active_requests[metrics.request_id] = metrics
    
    async def _update_communication_graph(self, metadata: ServiceCommunicationMetadata):
        """Update service communication graph"""
        with self._lock:
            source = metadata.source_service.service_name
            destination = metadata.destination_service.service_name
            self.service_communication_graph[source].add(destination)
    
    def _update_prometheus_metrics(self, metrics: MicroservicesMetrics):
        """Update Prometheus metrics"""
        source_service = metrics.metadata.source_service.service_name
        dest_service = metrics.metadata.destination_service.service_name
        operation = metrics.metadata.operation_name
        status = "success" if metrics.success else "error"
        
        # Update request duration
        self.prometheus_metrics['service_request_duration'].labels(
            source_service=source_service,
            destination_service=dest_service,
            operation=operation,
            status=status
        ).observe(metrics.total_time_ms / 1000)
        
        # Update communication count
        self.prometheus_metrics['service_communication_count'].labels(
            source_service=source_service,
            destination_service=dest_service,
            pattern=metrics.metadata.communication_pattern.value
        ).inc()
        
        # Update circuit breaker state
        cb_state_value = {
            CircuitBreakerState.CLOSED: 0,
            CircuitBreakerState.OPEN: 1,
            CircuitBreakerState.HALF_OPEN: 2
        }.get(metrics.metadata.circuit_breaker_state, 0)
        
        self.prometheus_metrics['circuit_breaker_state'].labels(
            source_service=source_service,
            destination_service=dest_service
        ).set(cb_state_value)
        
        # Update service discovery duration
        if metrics.service_discovery_time_ms is not None:
            self.prometheus_metrics['service_discovery_duration'].labels(
                service_type=metrics.metadata.destination_service.service_type.value,
                discovery_method="registry"
            ).observe(metrics.service_discovery_time_ms / 1000)
        
        # Update load balancer requests
        if metrics.load_balancing_time_ms is not None:
            self.prometheus_metrics['load_balancer_requests'].labels(
                algorithm=metrics.load_balancing_algorithm,
                destination_service=dest_service
            ).inc()
    
    async def _track_communication_patterns(self, metrics: MicroservicesMetrics):
        """Track communication patterns for optimization"""
        pattern_key = f"{metrics.metadata.source_service.service_name}->{metrics.metadata.destination_service.service_name}"
        
        with self._lock:
            self.communication_patterns[pattern_key].append(metrics.total_time_ms)
            
            # Keep only recent patterns
            if len(self.communication_patterns[pattern_key]) > 100:
                self.communication_patterns[pattern_key] = self.communication_patterns[pattern_key][-100:]
    
    async def _detect_bottlenecks(self, metrics: MicroservicesMetrics):
        """Detect microservices performance bottlenecks"""
        bottlenecks = []
        
        # High latency detection
        if metrics.total_time_ms > self.thresholds['max_service_time_ms']:
            bottleneck = MicroservicesBottleneck(
                bottleneck_id=f"high_latency_{int(time.time())}",
                source_service=metrics.metadata.source_service.service_name,
                destination_service=metrics.metadata.destination_service.service_name,
                communication_pattern=metrics.metadata.communication_pattern,
                bottleneck_type="high_latency",
                severity="high" if metrics.total_time_ms > self.thresholds['max_service_time_ms'] * 2 else "medium",
                description=f"High service communication latency: {metrics.total_time_ms:.2f}ms",
                current_performance={"latency_ms": metrics.total_time_ms},
                expected_performance={"latency_ms": self.thresholds['max_service_time_ms']},
                impact_percentage=(metrics.total_time_ms - self.thresholds['max_service_time_ms']) / self.thresholds['max_service_time_ms'] * 100,
                affected_services=[metrics.metadata.source_service.service_name, metrics.metadata.destination_service.service_name],
                affected_operations=[metrics.metadata.operation_name],
                service_mesh_analysis={"sidecar_overhead": metrics.sidecar_overhead_ms, "proxy_time": metrics.proxy_time_ms},
                load_balancing_analysis={"algorithm": metrics.load_balancing_algorithm, "instances": metrics.instances_available},
                recommendations=[
                    "Optimize service implementation and database queries",
                    "Consider caching frequently accessed data",
                    "Implement request batching where possible",
                    "Review service deployment and scaling policies",
                    "Optimize network communication and serialization"
                ],
                estimated_improvement={"latency_reduction_percent": 40.0}
            )
            bottlenecks.append(bottleneck)
        
        # Circuit breaker bottleneck
        if metrics.circuit_breaker_triggered:
            bottleneck = MicroservicesBottleneck(
                bottleneck_id=f"circuit_breaker_{int(time.time())}",
                source_service=metrics.metadata.source_service.service_name,
                destination_service=metrics.metadata.destination_service.service_name,
                communication_pattern=metrics.metadata.communication_pattern,
                bottleneck_type="circuit_breaker",
                severity="high",
                description="Circuit breaker triggered - service communication degraded",
                current_performance={"circuit_breaker_open": 1.0},
                expected_performance={"circuit_breaker_open": 0.0},
                impact_percentage=100.0,
                affected_services=[metrics.metadata.source_service.service_name, metrics.metadata.destination_service.service_name],
                affected_operations=[metrics.metadata.operation_name],
                service_mesh_analysis={"circuit_breaker_state": "open", "failure_threshold": self.thresholds['max_circuit_breaker_failures']},
                load_balancing_analysis={"healthy_instances": 0},
                recommendations=[
                    "Investigate destination service health and performance",
                    "Review error handling and retry logic",
                    "Implement proper fallback mechanisms",
                    "Monitor service dependencies and cascade failures",
                    "Consider gradual traffic ramp-up after recovery"
                ],
                estimated_improvement={"availability_improvement_percent": 80.0}
            )
            bottlenecks.append(bottleneck)
        
        # Load balancer bottleneck
        if (metrics.load_balancing_time_ms is not None and 
            metrics.load_balancing_time_ms > self.thresholds['max_load_balancer_time_ms']):
            bottleneck = MicroservicesBottleneck(
                bottleneck_id=f"load_balancer_{int(time.time())}",
                source_service=metrics.metadata.source_service.service_name,
                destination_service=metrics.metadata.destination_service.service_name,
                communication_pattern=metrics.metadata.communication_pattern,
                bottleneck_type="load_balancer",
                severity="medium",
                description=f"High load balancer overhead: {metrics.load_balancing_time_ms:.2f}ms",
                current_performance={"load_balancer_time_ms": metrics.load_balancing_time_ms},
                expected_performance={"load_balancer_time_ms": self.thresholds['max_load_balancer_time_ms']},
                impact_percentage=(metrics.load_balancing_time_ms - self.thresholds['max_load_balancer_time_ms']) / self.thresholds['max_load_balancer_time_ms'] * 100,
                affected_services=[metrics.metadata.source_service.service_name, metrics.metadata.destination_service.service_name],
                affected_operations=[metrics.metadata.operation_name],
                service_mesh_analysis={"load_balancer_algorithm": metrics.load_balancing_algorithm},
                load_balancing_analysis={"instances_available": metrics.instances_available, "selected_instance": metrics.instance_selected},
                recommendations=[
                    "Optimize load balancing algorithm selection",
                    "Implement connection pooling and keep-alive",
                    "Consider client-side load balancing",
                    "Review service instance health checks",
                    "Implement sticky sessions where appropriate"
                ],
                estimated_improvement={"load_balancer_overhead_reduction_percent": 50.0}
            )
            bottlenecks.append(bottleneck)
        
        # Store bottlenecks
        for bottleneck in bottlenecks:
            self.bottlenecks.append(bottleneck)
            self.prometheus_metrics['microservices_bottlenecks'].labels(
                service=bottleneck.destination_service,
                severity=bottleneck.severity
            ).inc()
    
    async def _monitoring_loop(self):
        """Background monitoring loop"""
        while self.is_monitoring:
            try:
                # Monitor service health
                await self._monitor_service_health()
                
                # Monitor communication patterns
                await self._monitor_communication_patterns()
                
                # Monitor circuit breakers
                await self._monitor_circuit_breakers()
                
                # Clean up old data
                await self._cleanup_old_data()
                
                await asyncio.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"Error in microservices monitoring loop: {e}")
                await asyncio.sleep(self.monitoring_interval)
    
    async def _monitor_service_health(self):
        """Monitor service health status"""
        try:
            # Update Prometheus metrics for service instances
            for service_key, instances in self.service_registry.items():
                healthy_instances = sum(1 for instance in instances 
                                      if self.service_health.get(instance.instance_id) == ServiceHealth.HEALTHY)
                
                service_name = service_key.split(':')[0]
                service_type = service_key.split(':')[1]
                
                self.prometheus_metrics['service_instances'].labels(
                    service_name=service_name,
                    service_type=service_type
                ).set(healthy_instances)
        
        except Exception as e:
            logger.error(f"Error monitoring service health: {e}")
    
    async def _monitor_communication_patterns(self):
        """Monitor service communication patterns"""
        try:
            with self._lock:
                for pattern, times in self.communication_patterns.items():
                    if len(times) > 10:  # Enough data points
                        avg_time = statistics.mean(times)
                        if avg_time > self.service_timeout_threshold_ms:
                            logger.warning(f"Slow service communication pattern: {pattern} - avg {avg_time:.2f}ms")
        
        except Exception as e:
            logger.error(f"Error monitoring communication patterns: {e}")
    
    async def _monitor_circuit_breakers(self):
        """Monitor circuit breaker states"""
        try:
            with self._lock:
                for service_key, state in self.circuit_breakers.items():
                    if state == CircuitBreakerState.OPEN:
                        logger.warning(f"Circuit breaker open for {service_key}")
        
        except Exception as e:
            logger.error(f"Error monitoring circuit breakers: {e}")
    
    async def _cleanup_old_data(self):
        """Clean up old monitoring data"""
        cutoff_time = datetime.utcnow() - timedelta(hours=1)
        
        # Clean up old bottlenecks
        self.bottlenecks = [b for b in self.bottlenecks if b.timestamp > cutoff_time]
        
        # Clean up old requests
        old_requests = [req_id for req_id, metrics in self.active_requests.items() 
                       if metrics.timestamp < cutoff_time]
        for req_id in old_requests:
            del self.active_requests[req_id]
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get microservices performance summary"""
        if not self.metrics_history:
            return {}
        
        recent_metrics = list(self.metrics_history)[-100:]  # Last 100 requests
        
        # Calculate averages
        avg_response_time = statistics.mean([m.total_time_ms for m in recent_metrics])
        success_rate = sum(1 for m in recent_metrics if m.success) / len(recent_metrics) * 100
        
        # Service breakdown
        service_breakdown = defaultdict(list)
        for metric in recent_metrics:
            service_pair = f"{metric.metadata.source_service.service_name}->{metric.metadata.destination_service.service_name}"
            service_breakdown[service_pair].append(metric)
        
        # Circuit breaker summary
        circuit_breaker_summary = {}
        with self._lock:
            for service_key, state in self.circuit_breakers.items():
                circuit_breaker_summary[service_key] = state.value
        
        return {
            "overall_performance": {
                "average_response_time_ms": avg_response_time,
                "success_rate_percent": success_rate,
                "total_communications": len(recent_metrics),
                "registered_services": len(self.service_registry)
            },
            "service_breakdown": {
                service_pair: {
                    "communication_count": len(metrics),
                    "avg_response_time_ms": statistics.mean([m.total_time_ms for m in metrics]),
                    "success_rate_percent": sum(1 for m in metrics if m.success) / len(metrics) * 100
                }
                for service_pair, metrics in service_breakdown.items()
            },
            "circuit_breakers": circuit_breaker_summary,
            "active_bottlenecks": len([b for b in self.bottlenecks if b.timestamp > datetime.utcnow() - timedelta(minutes=5)]),
            "service_health": dict(self.service_health),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_bottleneck_report(self) -> List[Dict[str, Any]]:
        """Get detailed bottleneck report"""
        return [
            {
                "bottleneck_id": b.bottleneck_id,
                "source_service": b.source_service,
                "destination_service": b.destination_service,
                "communication_pattern": b.communication_pattern.value,
                "type": b.bottleneck_type,
                "severity": b.severity,
                "description": b.description,
                "impact_percentage": b.impact_percentage,
                "affected_services": b.affected_services,
                "affected_operations": b.affected_operations,
                "service_mesh_analysis": b.service_mesh_analysis,
                "load_balancing_analysis": b.load_balancing_analysis,
                "recommendations": b.recommendations,
                "estimated_improvement": b.estimated_improvement,
                "timestamp": b.timestamp.isoformat()
            }
            for b in self.bottlenecks
        ]
    
    def register_service(self, service: ServiceEndpoint):
        """Register a service instance"""
        service_key = f"{service.service_name}:{service.service_type.value}"
        with self._lock:
            if service not in self.service_registry[service_key]:
                self.service_registry[service_key].append(service)
                self.service_health[service.instance_id] = ServiceHealth.HEALTHY
                logger.info(f"Service registered: {service.service_name} ({service.instance_id})")
    
    def unregister_service(self, service_name: str, instance_id: str):
        """Unregister a service instance"""
        with self._lock:
            for service_key, instances in self.service_registry.items():
                if service_name in service_key:
                    self.service_registry[service_key] = [
                        s for s in instances if s.instance_id != instance_id
                    ]
            
            if instance_id in self.service_health:
                del self.service_health[instance_id]
            
            logger.info(f"Service unregistered: {service_name} ({instance_id})")


def create_microservices_profiler(
    monitoring_interval: float = 5.0,
    enable_distributed_tracing: bool = True,
    enable_circuit_breaker_monitoring: bool = True,
    service_timeout_threshold_ms: float = 5000.0,
    start_monitoring: bool = False
) -> MicroservicesProfiler:
    """
    Factory function to create microservices profiler
    
    Args:
        monitoring_interval: Monitoring interval in seconds
        enable_distributed_tracing: Enable distributed tracing
        enable_circuit_breaker_monitoring: Enable circuit breaker monitoring
        service_timeout_threshold_ms: Threshold for service timeout detection
        start_monitoring: Start monitoring immediately
    
    Returns:
        MicroservicesProfiler: Configured microservices profiler instance
    """
    profiler = MicroservicesProfiler(
        monitoring_interval=monitoring_interval,
        enable_distributed_tracing=enable_distributed_tracing,
        enable_circuit_breaker_monitoring=enable_circuit_breaker_monitoring,
        service_timeout_threshold_ms=service_timeout_threshold_ms
    )
    
    if start_monitoring:
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            loop.create_task(profiler.start_monitoring())
        except RuntimeError:
            logger.warning("No event loop running, monitoring will need to be started manually")
    
    return profiler


# Example usage for Creator Economy platform
async def example_microservices_profiling():
    """Example of profiling Creator Economy microservices"""
    profiler = create_microservices_profiler(start_monitoring=True)
    
    # Register services
    creator_service = ServiceEndpoint(
        service_name="creator-profiles",
        service_type=ServiceType.CREATOR_PROFILES,
        service_version="v1.2.0",
        host="creator-profiles.ainflue.internal",
        port=8080,
        health_check_url="/health"
    )
    
    content_service = ServiceEndpoint(
        service_name="content-management",
        service_type=ServiceType.CONTENT_MANAGEMENT,
        service_version="v1.1.0",
        host="content-mgmt.ainflue.internal", 
        port=8081,
        health_check_url="/health"
    )
    
    profiler.register_service(creator_service)
    profiler.register_service(content_service)
    
    # Example: Profile service communication
    async def get_creator_content(creator_id: str):
        # Simulate service call
        await asyncio.sleep(0.05)
        return {
            "status_code": 200,
            "data": {
                "creator_id": creator_id,
                "content_count": 150,
                "categories": ["gaming", "tech"]
            }
        }
    
    metadata = ServiceCommunicationMetadata(
        request_id="req_123",
        source_service=creator_service,
        destination_service=content_service,
        communication_pattern=CommunicationPattern.REQUEST_RESPONSE,
        operation_name="get_creator_content",
        payload_size_bytes=256,
        headers_count=5,
        load_balancer_used=True,
        trace_id="trace_456"
    )
    
    metrics = await profiler.profile_service_communication(
        metadata,
        get_creator_content,
        "creator_789"
    )
    
    print(f"Microservice communication profiled:")
    print(f"- Total time: {metrics.total_time_ms:.2f}ms")
    print(f"- Service discovery: {metrics.service_discovery_time_ms:.2f}ms" if metrics.service_discovery_time_ms else "- No service discovery")
    print(f"- Load balancing: {metrics.load_balancing_time_ms:.2f}ms" if metrics.load_balancing_time_ms else "- No load balancing")
    print(f"- Processing: {metrics.processing_time_ms:.2f}ms" if metrics.processing_time_ms else "- No processing timing")
    print(f"- Success: {metrics.success}")
    
    # Get performance summary
    summary = profiler.get_performance_summary()
    print(f"Performance summary: {json.dumps(summary, indent=2)}")
    
    await profiler.stop_monitoring()


if __name__ == "__main__":
    asyncio.run(example_microservices_profiling())