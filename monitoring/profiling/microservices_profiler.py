"""⚡ Microservices Profiling System
=================================

Advanced microservices architecture performance monitoring for the Ainflue Creator Platform.
Provides comprehensive profiling for service-to-service communication, load balancing, and distributed systems.

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
from typing import Dict, List, Optional, Any, Union, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import statistics
from collections import defaultdict, deque
import uuid

logger = logging.getLogger(__name__)

# Try to import distributed tracing libraries
try:
    import opentracing
    HAS_OPENTRACING = True
except ImportError:
    HAS_OPENTRACING = False

try:
    from jaeger_client import Config as JaegerConfig
    HAS_JAEGER = True
except ImportError:
    HAS_JAEGER = False


class ServiceType(Enum):
    """Types of microservices"""
    API_GATEWAY = "api_gateway"
    AUTH_SERVICE = "auth_service"
    USER_SERVICE = "user_service"
    CONTENT_SERVICE = "content_service"
    UPLOAD_SERVICE = "upload_service"
    PROCESSING_SERVICE = "processing_service"
    NOTIFICATION_SERVICE = "notification_service"
    ANALYTICS_SERVICE = "analytics_service"
    PAYMENT_SERVICE = "payment_service"
    SEARCH_SERVICE = "search_service"
    COLLABORATION_SERVICE = "collaboration_service"
    SEO_SERVICE = "seo_service"


class CommunicationType(Enum):
    """Types of service communication"""
    SYNCHRONOUS = "synchronous"
    ASYNCHRONOUS = "asynchronous"
    MESSAGE_QUEUE = "message_queue"
    EVENT_STREAM = "event_stream"
    RPC = "rpc"
    REST_API = "rest_api"
    GRAPHQL = "graphql"


class LoadBalancerType(Enum):
    """Load balancer types"""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED = "weighted"
    IP_HASH = "ip_hash"
    GEOGRAPHIC = "geographic"


@dataclass
class ServiceMetadata:
    """Metadata for microservice operations"""
    service_name: str
    service_version: str
    service_type: ServiceType
    instance_id: str
    communication_type: CommunicationType
    operation_name: str
    caller_service: Optional[str] = None
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    correlation_id: Optional[str] = None
    user_id: Optional[str] = None


@dataclass
class MicroserviceMetrics:
    """Microservice performance metrics"""
    operation_id: str
    service_name: str
    service_type: ServiceType
    communication_type: CommunicationType
    operation_name: str
    request_time_ms: float
    response_time_ms: float
    total_time_ms: float
    payload_size_bytes: int
    response_size_bytes: int
    status_code: int
    circuit_breaker_state: str
    load_balancer_used: bool
    service_instance: str
    retry_count: int
    cache_hit: bool
    error_type: Optional[str]
    downstream_calls: int
    cpu_usage: float
    memory_usage_mb: float
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ServiceBottleneck:
    """Microservice bottleneck information"""
    bottleneck_type: str
    severity: str
    service_name: str
    service_type: ServiceType
    description: str
    impact: str
    recommendations: List[str]
    detected_at: datetime
    metrics: Dict[str, float] = field(default_factory=dict)


class MicroservicesProfiler:
    """
    Microservices architecture performance profiler for Creator Economy platform
    """
    
    def __init__(self, 
                 monitoring_interval: float = 3.0,
                 max_history_size: int = 25000):
        self.monitoring_interval = monitoring_interval
        self.max_history_size = max_history_size
        self.is_monitoring = False
        self.monitoring_thread = None
        
        # Metrics storage
        self.service_metrics_history: deque = deque(maxlen=max_history_size)
        self.bottlenecks_history: deque = deque(maxlen=1000)
        self.active_requests: Dict[str, Dict] = {}
        
        # Service topology
        self.service_topology: Dict[str, Set[str]] = defaultdict(set)
        self.service_instances: Dict[str, List[str]] = defaultdict(list)
        self.load_balancer_configs: Dict[str, Dict] = {}
        
        # Performance thresholds
        self.thresholds = {
            'slow_service_threshold': 1000.0,     # 1 second
            'very_slow_service_threshold': 5000.0, # 5 seconds
            'high_error_rate_threshold': 5.0,     # 5%
            'circuit_breaker_threshold': 50.0,    # 50% errors
            'memory_usage_threshold': 1024.0,     # 1GB
            'cpu_usage_threshold': 80.0,          # 80%
            'cascade_failure_threshold': 3        # 3 downstream failures
        }
        
        # Distributed tracing
        self.tracer = None
        self._init_distributed_tracing()
        
        logger.info("MicroservicesProfiler initialized")

    def _init_distributed_tracing(self):
        """Initialize distributed tracing"""
        try:
            if HAS_JAEGER and HAS_OPENTRACING:
                config = JaegerConfig(
                    config={
                        'sampler': {'type': 'const', 'param': 1},
                        'logging': True,
                    },
                    service_name='ainflue-microservices-profiler'
                )
                self.tracer = config.initialize_tracer()
                logger.info("Distributed tracing initialized with Jaeger")
        except Exception as e:
            logger.warning(f"Error initializing distributed tracing: {e}")

    def start_monitoring(self):
        """Start background microservices monitoring"""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitoring_thread = threading.Thread(
                target=self._monitoring_loop,
                daemon=True
            )
            self.monitoring_thread.start()
            logger.info("Microservices monitoring started")

    def stop_monitoring(self):
        """Stop background monitoring"""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5.0)
        logger.info("Microservices monitoring stopped")

    def _monitoring_loop(self):
        """Background monitoring loop"""
        while self.is_monitoring:
            try:
                self._collect_service_health_metrics()
                self._analyze_service_topology()
                self._cleanup_stale_requests()
                time.sleep(self.monitoring_interval)
            except Exception as e:
                logger.error(f"Error in microservices monitoring loop: {e}")

    def _collect_service_health_metrics(self):
        """Collect overall service health metrics"""
        try:
            # Analyze recent service calls
            now = datetime.utcnow()
            recent_metrics = [
                m for m in list(self.service_metrics_history)[-1000:]
                if (now - m.timestamp).total_seconds() < 300  # Last 5 minutes
            ]
            
            if recent_metrics:
                # Group by service
                service_stats = defaultdict(list)
                for metrics in recent_metrics:
                    service_stats[metrics.service_name].append(metrics)
                
                # Create health metrics for each service
                for service_name, metrics_list in service_stats.items():
                    avg_response_time = statistics.mean([m.response_time_ms for m in metrics_list])
                    error_rate = (sum(1 for m in metrics_list if m.status_code >= 400) / len(metrics_list)) * 100
                    
                    # Create service health metric
                    health_metrics = MicroserviceMetrics(
                        operation_id=f"health_{service_name}_{int(time.time())}",
                        service_name=service_name,
                        service_type=metrics_list[0].service_type,
                        communication_type=CommunicationType.REST_API,
                        operation_name="health_check",
                        request_time_ms=0.0,
                        response_time_ms=avg_response_time,
                        total_time_ms=avg_response_time,
                        payload_size_bytes=0,
                        response_size_bytes=0,
                        status_code=200 if error_rate < 5 else 500,
                        circuit_breaker_state="CLOSED" if error_rate < 10 else "OPEN",
                        load_balancer_used=True,
                        service_instance="health_monitor",
                        retry_count=0,
                        cache_hit=False,
                        error_type=None,
                        downstream_calls=0,
                        cpu_usage=0.0,
                        memory_usage_mb=0.0,
                        timestamp=now,
                        metadata={
                            'health_check': True,
                            'service_calls': len(metrics_list),
                            'error_rate': error_rate,
                            'active_instances': len(self.service_instances.get(service_name, []))
                        }
                    )
                    
                    # Don't add to history to avoid skewing metrics
                    # Analyze for bottlenecks only
                    self._analyze_service_bottlenecks(health_metrics)
                
        except Exception as e:
            logger.error(f"Error collecting service health metrics: {e}")

    def _analyze_service_topology(self):
        """Analyze service communication topology"""
        try:
            # Update topology based on recent calls
            recent_metrics = list(self.service_metrics_history)[-500:]  # Last 500 calls
            
            for metrics in recent_metrics:
                caller = metrics.metadata.get('caller_service')
                if caller:
                    self.service_topology[caller].add(metrics.service_name)
                    
        except Exception as e:
            logger.error(f"Error analyzing service topology: {e}")

    def _cleanup_stale_requests(self):
        """Clean up stale active requests"""
        now = time.time()
        stale_threshold = 300  # 5 minutes
        
        stale_requests = [
            req_id for req_id, req_data in self.active_requests.items()
            if now - req_data.get('start_time', now) > stale_threshold
        ]
        
        for req_id in stale_requests:
            self.active_requests.pop(req_id, None)

    def register_service(self,
                        service_name: str,
                        service_type: ServiceType,
                        instance_id: str,
                        version: str = "1.0.0"):
        """
        Register a microservice instance
        
        Args:
            service_name: Name of the service
            service_type: Type of service
            instance_id: Unique instance identifier
            version: Service version
        """
        if instance_id not in self.service_instances[service_name]:
            self.service_instances[service_name].append(instance_id)
            logger.info(f"Registered service instance: {service_name}:{instance_id}")

    def profile_service_call(self,
                           service_name: str,
                           service_type: ServiceType,
                           operation_name: str,
                           communication_type: CommunicationType = CommunicationType.REST_API,
                           caller_service: Optional[str] = None,
                           trace_id: Optional[str] = None,
                           **kwargs) -> str:
        """
        Start profiling a microservice call
        
        Args:
            service_name: Target service name
            service_type: Type of service
            operation_name: Operation being called
            communication_type: Type of communication
            caller_service: Calling service name
            trace_id: Distributed trace ID
            **kwargs: Additional metadata
            
        Returns:
            Request ID for tracking
        """
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Generate trace ID if not provided
        if not trace_id and self.tracer:
            span = self.tracer.start_span(f"{service_name}.{operation_name}")
            trace_id = str(span.context.trace_id)
            span.finish()
        
        # Store request start info
        self.active_requests[request_id] = {
            'start_time': start_time,
            'service_name': service_name,
            'service_type': service_type,
            'operation_name': operation_name,
            'communication_type': communication_type,
            'caller_service': caller_service,
            'trace_id': trace_id,
            'metadata': kwargs
        }
        
        return request_id

    def complete_service_call(self,
                            request_id: str,
                            status_code: int,
                            response_size_bytes: int = 0,
                            service_instance: str = "unknown",
                            circuit_breaker_state: str = "CLOSED",
                            load_balancer_used: bool = False,
                            retry_count: int = 0,
                            cache_hit: bool = False,
                            error_type: Optional[str] = None,
                            downstream_calls: int = 0,
                            cpu_usage: float = 0.0,
                            memory_usage_mb: float = 0.0,
                            **kwargs) -> MicroserviceMetrics:
        """
        Complete profiling a microservice call
        
        Args:
            request_id: Request ID from profile_service_call
            status_code: Response status code
            response_size_bytes: Size of response
            service_instance: Service instance identifier
            circuit_breaker_state: Circuit breaker state
            load_balancer_used: Whether load balancer was used
            retry_count: Number of retries
            cache_hit: Whether response was cached
            error_type: Type of error if any
            downstream_calls: Number of downstream service calls
            cpu_usage: CPU usage percentage
            memory_usage_mb: Memory usage in MB
            **kwargs: Additional response metadata
            
        Returns:
            MicroserviceMetrics with profiling results
        """
        end_time = time.time()
        
        # Get request info
        request_info = self.active_requests.get(request_id)
        if not request_info:
            raise ValueError(f"Request ID {request_id} not found")
        
        start_time = request_info['start_time']
        total_time_ms = (end_time - start_time) * 1000
        
        # Create metrics
        metrics = MicroserviceMetrics(
            operation_id=request_id,
            service_name=request_info['service_name'],
            service_type=request_info['service_type'],
            communication_type=request_info['communication_type'],
            operation_name=request_info['operation_name'],
            request_time_ms=0.0,  # Would need more detailed timing
            response_time_ms=total_time_ms,
            total_time_ms=total_time_ms,
            payload_size_bytes=request_info['metadata'].get('payload_size', 0),
            response_size_bytes=response_size_bytes,
            status_code=status_code,
            circuit_breaker_state=circuit_breaker_state,
            load_balancer_used=load_balancer_used,
            service_instance=service_instance,
            retry_count=retry_count,
            cache_hit=cache_hit,
            error_type=error_type,
            downstream_calls=downstream_calls,
            cpu_usage=cpu_usage,
            memory_usage_mb=memory_usage_mb,
            timestamp=datetime.utcnow(),
            metadata={
                **request_info['metadata'],
                **kwargs,
                'caller_service': request_info.get('caller_service'),
                'trace_id': request_info.get('trace_id'),
                'correlation_id': kwargs.get('correlation_id')
            }
        )
        
        # Store metrics
        self.service_metrics_history.append(metrics)
        
        # Remove from active requests
        self.active_requests.pop(request_id, None)
        
        # Check for bottlenecks
        self._analyze_service_bottlenecks(metrics)
        
        return metrics

    def _analyze_service_bottlenecks(self, metrics: MicroserviceMetrics):
        """Analyze microservice bottlenecks"""
        bottlenecks = []
        
        # Check response time
        if metrics.response_time_ms > self.thresholds['very_slow_service_threshold']:
            severity = "critical"
        elif metrics.response_time_ms > self.thresholds['slow_service_threshold']:
            severity = "high"
        else:
            severity = None
        
        if severity:
            bottlenecks.append(ServiceBottleneck(
                bottleneck_type="slow_service",
                severity=severity,
                service_name=metrics.service_name,
                service_type=metrics.service_type,
                description=f"Service response too slow: {metrics.response_time_ms:.1f}ms",
                impact="Poor user experience, potential cascading failures",
                recommendations=[
                    "Optimize service logic",
                    "Scale service instances",
                    "Implement caching",
                    "Review database queries"
                ],
                detected_at=datetime.utcnow(),
                metrics={'response_time_ms': metrics.response_time_ms}
            ))
        
        # Check circuit breaker state
        if metrics.circuit_breaker_state == "OPEN":
            bottlenecks.append(ServiceBottleneck(
                bottleneck_type="circuit_breaker_open",
                severity="critical",
                service_name=metrics.service_name,
                service_type=metrics.service_type,
                description="Circuit breaker is open - service failing",
                impact="Service unavailable, requests failing",
                recommendations=[
                    "Investigate service health",
                    "Check dependencies",
                    "Review error logs",
                    "Implement fallback mechanisms"
                ],
                detected_at=datetime.utcnow(),
                metrics={'circuit_breaker_state': 1}
            ))
        
        # Check memory usage
        if metrics.memory_usage_mb > self.thresholds['memory_usage_threshold']:
            bottlenecks.append(ServiceBottleneck(
                bottleneck_type="high_memory_usage",
                severity="high",
                service_name=metrics.service_name,
                service_type=metrics.service_type,
                description=f"High memory usage: {metrics.memory_usage_mb:.1f}MB",
                impact="Performance degradation, potential OOM",
                recommendations=[
                    "Optimize memory usage",
                    "Implement memory pooling",
                    "Check for memory leaks",
                    "Scale service instances"
                ],
                detected_at=datetime.utcnow(),
                metrics={'memory_usage_mb': metrics.memory_usage_mb}
            ))
        
        # Check CPU usage
        if metrics.cpu_usage > self.thresholds['cpu_usage_threshold']:
            bottlenecks.append(ServiceBottleneck(
                bottleneck_type="high_cpu_usage",
                severity="medium",
                service_name=metrics.service_name,
                service_type=metrics.service_type,
                description=f"High CPU usage: {metrics.cpu_usage:.1f}%",
                impact="Performance degradation, slow responses",
                recommendations=[
                    "Optimize CPU-intensive operations",
                    "Implement async processing",
                    "Scale service instances",
                    "Profile CPU usage patterns"
                ],
                detected_at=datetime.utcnow(),
                metrics={'cpu_usage': metrics.cpu_usage}
            ))
        
        # Check retry count
        if metrics.retry_count > 0:
            bottlenecks.append(ServiceBottleneck(
                bottleneck_type="high_retry_count",
                severity="medium",
                service_name=metrics.service_name,
                service_type=metrics.service_type,
                description=f"High retry count: {metrics.retry_count}",
                impact="Increased latency, resource usage",
                recommendations=[
                    "Investigate intermittent failures",
                    "Optimize retry policies",
                    "Implement exponential backoff",
                    "Check network stability"
                ],
                detected_at=datetime.utcnow(),
                metrics={'retry_count': metrics.retry_count}
            ))
        
        # Check for service errors
        if metrics.status_code >= 500:
            bottlenecks.append(ServiceBottleneck(
                bottleneck_type="service_error",
                severity="critical",
                service_name=metrics.service_name,
                service_type=metrics.service_type,
                description=f"Service error: {metrics.status_code}",
                impact="Service functionality disrupted",
                recommendations=[
                    "Check service logs",
                    "Monitor dependencies",
                    "Implement health checks",
                    "Add error handling"
                ],
                detected_at=datetime.utcnow(),
                metrics={'status_code': metrics.status_code}
            ))
        
        # Store bottlenecks
        for bottleneck in bottlenecks:
            self.bottlenecks_history.append(bottleneck)

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get microservices performance summary"""
        if not self.service_metrics_history:
            return {"error": "No metrics available"}
        
        recent_metrics = list(self.service_metrics_history)[-2000:]  # Last 2000 calls
        
        # Calculate statistics
        response_times = [m.response_time_ms for m in recent_metrics]
        error_count = sum(1 for m in recent_metrics if m.status_code >= 400)
        circuit_breaker_open = sum(1 for m in recent_metrics if m.circuit_breaker_state == "OPEN")
        cache_hits = sum(1 for m in recent_metrics if m.cache_hit)
        retries = sum(m.retry_count for m in recent_metrics)
        
        return {
            "summary": {
                "total_service_calls": len(recent_metrics),
                "avg_response_time_ms": statistics.mean(response_times) if response_times else 0,
                "p50_response_time_ms": statistics.median(response_times) if response_times else 0,
                "p95_response_time_ms": statistics.quantiles(response_times, n=20)[18] if len(response_times) > 20 else 0,
                "p99_response_time_ms": statistics.quantiles(response_times, n=100)[98] if len(response_times) > 100 else 0,
                "error_rate": (error_count / len(recent_metrics)) * 100,
                "circuit_breaker_failures": circuit_breaker_open,
                "cache_hit_rate": (cache_hits / len(recent_metrics)) * 100,
                "total_retries": retries,
                "active_requests": len(self.active_requests),
                "registered_services": len(self.service_instances)
            },
            "by_service": self._get_metrics_by_service(),
            "by_service_type": self._get_metrics_by_service_type(),
            "by_communication_type": self._get_metrics_by_communication_type(),
            "service_topology": self._get_service_topology(),
            "bottlenecks": len(self.bottlenecks_history),
            "recommendations": self._get_microservices_optimization_recommendations()
        }

    def _get_metrics_by_service(self) -> Dict[str, Dict]:
        """Get metrics grouped by service"""
        metrics_by_service = defaultdict(list)
        
        for metrics in list(self.service_metrics_history)[-1000:]:
            metrics_by_service[metrics.service_name].append(metrics)
        
        result = {}
        for service_name, metrics_list in metrics_by_service.items():
            response_times = [m.response_time_ms for m in metrics_list]
            error_count = sum(1 for m in metrics_list if m.status_code >= 400)
            
            result[service_name] = {
                "calls": len(metrics_list),
                "avg_response_time_ms": statistics.mean(response_times) if response_times else 0,
                "error_rate": (error_count / len(metrics_list)) * 100,
                "cache_hit_rate": (sum(1 for m in metrics_list if m.cache_hit) / len(metrics_list)) * 100,
                "circuit_breaker_failures": sum(1 for m in metrics_list if m.circuit_breaker_state == "OPEN"),
                "instances": len(self.service_instances.get(service_name, []))
            }
        
        return dict(sorted(result.items(), key=lambda x: x[1]['calls'], reverse=True)[:10])

    def _get_metrics_by_service_type(self) -> Dict[str, Dict]:
        """Get metrics grouped by service type"""
        metrics_by_type = defaultdict(list)
        
        for metrics in list(self.service_metrics_history)[-1000:]:
            metrics_by_type[metrics.service_type.value].append(metrics)
        
        result = {}
        for service_type, metrics_list in metrics_by_type.items():
            response_times = [m.response_time_ms for m in metrics_list]
            error_count = sum(1 for m in metrics_list if m.status_code >= 400)
            
            result[service_type] = {
                "calls": len(metrics_list),
                "avg_response_time_ms": statistics.mean(response_times) if response_times else 0,
                "error_rate": (error_count / len(metrics_list)) * 100
            }
        
        return result

    def _get_metrics_by_communication_type(self) -> Dict[str, Dict]:
        """Get metrics grouped by communication type"""
        metrics_by_comm = defaultdict(list)
        
        for metrics in list(self.service_metrics_history)[-1000:]:
            metrics_by_comm[metrics.communication_type.value].append(metrics)
        
        result = {}
        for comm_type, metrics_list in metrics_by_comm.items():
            response_times = [m.response_time_ms for m in metrics_list]
            
            result[comm_type] = {
                "calls": len(metrics_list),
                "avg_response_time_ms": statistics.mean(response_times) if response_times else 0,
                "error_rate": (sum(1 for m in metrics_list if m.status_code >= 400) / len(metrics_list)) * 100
            }
        
        return result

    def _get_service_topology(self) -> Dict[str, List[str]]:
        """Get service communication topology"""
        return {caller: list(called_services) for caller, called_services in self.service_topology.items()}

    def _get_microservices_optimization_recommendations(self) -> List[str]:
        """Get microservices optimization recommendations"""
        recommendations = []
        
        if not self.service_metrics_history:
            return ["Start profiling service calls to get recommendations"]
        
        recent_metrics = list(self.service_metrics_history)[-1000:]
        
        # Calculate key metrics
        avg_response_time = statistics.mean([m.response_time_ms for m in recent_metrics])
        error_rate = (sum(1 for m in recent_metrics if m.status_code >= 400) / len(recent_metrics)) * 100
        cache_hit_rate = (sum(1 for m in recent_metrics if m.cache_hit) / len(recent_metrics)) * 100
        circuit_breaker_failures = sum(1 for m in recent_metrics if m.circuit_breaker_state == "OPEN")
        avg_retries = statistics.mean([m.retry_count for m in recent_metrics])
        
        if avg_response_time > 1000:
            recommendations.append("High service response times - optimize slow services")
        if error_rate > 5:
            recommendations.append("High error rate - investigate service failures")
        if cache_hit_rate < 50:
            recommendations.append("Low cache hit rate - improve caching strategy")
        if circuit_breaker_failures > 0:
            recommendations.append("Circuit breaker failures detected - check service health")
        if avg_retries > 0.5:
            recommendations.append("High retry rate - investigate intermittent failures")
        if len(self.active_requests) > 200:
            recommendations.append("High concurrent requests - consider scaling services")
        
        # Service-specific recommendations
        service_metrics = self._get_metrics_by_service()
        slow_services = [svc for svc, data in service_metrics.items() if data['avg_response_time_ms'] > 2000]
        if slow_services:
            recommendations.append(f"Slow services detected: {', '.join(slow_services[:3])}")
        
        error_prone_services = [svc for svc, data in service_metrics.items() if data['error_rate'] > 10]
        if error_prone_services:
            recommendations.append(f"Error-prone services: {', '.join(error_prone_services[:3])}")
        
        if not recommendations:
            recommendations.append("Microservices performance is optimal")
        
        return recommendations

    def get_recent_bottlenecks(self, limit: int = 10) -> List[ServiceBottleneck]:
        """Get recent service bottlenecks"""
        return list(self.bottlenecks_history)[-limit:]

    def get_service_topology_graph(self) -> Dict[str, Any]:
        """Get service topology as a graph structure"""
        nodes = []
        edges = []
        
        # Create nodes for all services
        all_services = set()
        for caller, called_services in self.service_topology.items():
            all_services.add(caller)
            all_services.update(called_services)
        
        for service in all_services:
            instances = len(self.service_instances.get(service, []))
            nodes.append({
                "id": service,
                "label": service,
                "instances": instances,
                "type": "service"
            })
        
        # Create edges for service calls
        for caller, called_services in self.service_topology.items():
            for called_service in called_services:
                edges.append({
                    "from": caller,
                    "to": called_service,
                    "type": "service_call"
                })
        
        return {
            "nodes": nodes,
            "edges": edges,
            "metrics": {
                "total_services": len(all_services),
                "total_connections": len(edges),
                "max_depth": self._calculate_topology_depth()
            }
        }

    def _calculate_topology_depth(self) -> int:
        """Calculate maximum depth of service call chain"""
        # Simple DFS to find maximum depth
        max_depth = 0
        
        def dfs(service: str, depth: int, visited: Set[str]):
            nonlocal max_depth
            if service in visited:
                return
            
            visited.add(service)
            max_depth = max(max_depth, depth)
            
            for called_service in self.service_topology.get(service, []):
                dfs(called_service, depth + 1, visited.copy())
        
        for root_service in self.service_topology.keys():
            dfs(root_service, 0, set())
        
        return max_depth

    def export_metrics(self, format: str = "json") -> str:
        """Export microservices metrics"""
        data = {
            "microservice_metrics": [
                {
                    "operation_id": m.operation_id,
                    "service_name": m.service_name,
                    "service_type": m.service_type.value,
                    "operation_name": m.operation_name,
                    "response_time_ms": m.response_time_ms,
                    "status_code": m.status_code,
                    "circuit_breaker_state": m.circuit_breaker_state,
                    "timestamp": m.timestamp.isoformat()
                }
                for m in list(self.service_metrics_history)[-1000:]
            ],
            "bottlenecks": [
                {
                    "type": b.bottleneck_type,
                    "severity": b.severity,
                    "service_name": b.service_name,
                    "service_type": b.service_type.value,
                    "description": b.description,
                    "detected_at": b.detected_at.isoformat()
                }
                for b in list(self.bottlenecks_history)[-100:]
            ],
            "topology": self._get_service_topology()
        }
        
        if format == "json":
            return json.dumps(data, indent=2)
        else:
            return str(data)


# Factory function
def create_microservices_profiler(monitoring_interval: float = 3.0,
                                max_history_size: int = 25000,
                                start_monitoring: bool = True) -> MicroservicesProfiler:
    """
    Create and configure a microservices profiler
    
    Args:
        monitoring_interval: Monitoring interval in seconds
        max_history_size: Maximum number of metrics to store
        start_monitoring: Start background monitoring
        
    Returns:
        Configured MicroservicesProfiler instance
    """
    profiler = MicroservicesProfiler(
        monitoring_interval=monitoring_interval,
        max_history_size=max_history_size
    )
    
    if start_monitoring:
        profiler.start_monitoring()
    
    return profiler


# Main execution
if __name__ == "__main__":
    # Example usage
    profiler = create_microservices_profiler()
    
    try:
        # Register services
        profiler.register_service("auth-service", ServiceType.AUTH_SERVICE, "auth-001")
        profiler.register_service("content-service", ServiceType.CONTENT_SERVICE, "content-001")
        
        # Example: Profile a service call
        request_id = profiler.profile_service_call(
            service_name="content-service",
            service_type=ServiceType.CONTENT_SERVICE,
            operation_name="upload_content",
            communication_type=CommunicationType.REST_API,
            caller_service="api-gateway",
            payload_size=1024 * 1024  # 1MB
        )
        
        # Simulate some processing time
        time.sleep(0.1)
        
        # Complete the service call
        metrics = profiler.complete_service_call(
            request_id=request_id,
            status_code=201,
            response_size_bytes=256,
            service_instance="content-001",
            circuit_breaker_state="CLOSED",
            load_balancer_used=True,
            cache_hit=False,
            downstream_calls=2,
            cpu_usage=45.0,
            memory_usage_mb=512.0
        )
        
        print(f"Service call response time: {metrics.response_time_ms:.2f}ms")
        print(f"Status code: {metrics.status_code}")
        print(f"Circuit breaker state: {metrics.circuit_breaker_state}")
        
        # Get performance summary
        summary = profiler.get_performance_summary()
        print(f"Microservices performance summary: {json.dumps(summary, indent=2)}")
        
        # Get service topology
        topology = profiler.get_service_topology_graph()
        print(f"Service topology: {json.dumps(topology, indent=2)}")
        
    finally:
        profiler.stop_monitoring()