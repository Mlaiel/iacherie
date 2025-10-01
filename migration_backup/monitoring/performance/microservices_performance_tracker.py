"""
⚠️ CONFIDENTIEL - IA Chéries Creator Platform ⚠️

Microservices Performance Tracker - Enterprise Performance Monitoring
Advanced performance tracking for microservices architecture and service mesh

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques
"""

import time
import asyncio
import json
import statistics
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
import logging
from collections import defaultdict, deque
import threading
import uuid
from prometheus_client import Gauge, Counter, Histogram, Summary
import aiohttp
import httpx
from urllib.parse import urljoin
import networkx as nx
import yaml
import consul
import etcd3

logger = logging.getLogger(__name__)

@dataclass
class ServiceCallMetrics:
    """Service-to-service call metrics"""
    trace_id: str
    span_id: str
    source_service: str
    target_service: str
    endpoint: str
    method: str
    start_time: datetime
    end_time: datetime
    duration_ms: float
    status_code: int
    success: bool
    request_size_bytes: int
    response_size_bytes: int
    retries: int = 0
    circuit_breaker_state: Optional[str] = None
    load_balancer_backend: Optional[str] = None
    error_message: Optional[str] = None

@dataclass
class ServiceHealthMetrics:
    """Service health and resource metrics"""
    service_name: str
    instance_id: str
    cpu_usage_percent: float
    memory_usage_mb: float
    active_connections: int
    request_queue_size: int
    health_check_status: str  # healthy, degraded, unhealthy
    uptime_seconds: int
    error_rate_percent: float
    response_time_p95_ms: float
    timestamp: datetime
    version: Optional[str] = None
    replicas: int = 1

@dataclass
class CircuitBreakerMetrics:
    """Circuit breaker metrics"""
    service_name: str
    target_service: str
    state: str  # closed, open, half_open
    failure_count: int
    failure_threshold: int
    success_count: int
    last_failure_time: Optional[datetime]
    last_success_time: Optional[datetime]
    timeout_ms: int
    timestamp: datetime

@dataclass
class ServiceMeshMetrics:
    """Service mesh performance metrics"""
    mesh_name: str
    proxy_type: str  # envoy, istio, linkerd
    service_name: str
    inbound_rps: float
    outbound_rps: float
    inbound_latency_p99_ms: float
    outbound_latency_p99_ms: float
    ssl_handshake_time_ms: float
    connection_pool_utilization: float
    retry_rate_percent: float
    timestamp: datetime

@dataclass
class DistributedTransactionMetrics:
    """Distributed transaction performance metrics"""
    transaction_id: str
    transaction_type: str
    participating_services: List[str]
    start_time: datetime
    end_time: datetime
    total_duration_ms: float
    success: bool
    rollback_required: bool
    compensation_actions: int
    saga_steps: int
    error_service: Optional[str] = None
    error_message: Optional[str] = None

@dataclass
class ServiceDependencyMetrics:
    """Service dependency graph metrics"""
    service_name: str
    dependencies: List[str]
    dependents: List[str]
    dependency_health_score: float
    critical_path_length: int
    single_point_of_failure: bool
    timestamp: datetime

class MicroservicesPerformanceTracker:
    """
    Enterprise-grade microservices performance tracker
    Monitors service-to-service communication, circuit breakers, and distributed transactions
    """
    
    def __init__(self,
                 service_registry_url: Optional[str] = None,
                 consul_host: str = 'localhost',
                 consul_port: int = 8500,
                 etcd_host: str = 'localhost',
                 etcd_port: int = 2379,
                 enable_service_discovery: bool = True,
                 enable_distributed_tracing: bool = True):
        """
        Initialize microservices performance tracker
        
        Args:
            service_registry_url: Service registry URL (Consul, Eureka, etc.)
            consul_host: Consul host for service discovery
            consul_port: Consul port
            etcd_host: etcd host for configuration
            etcd_port: etcd port
            enable_service_discovery: Enable automatic service discovery
            enable_distributed_tracing: Enable distributed tracing
        """
        self.service_registry_url = service_registry_url
        self.consul_host = consul_host
        self.consul_port = consul_port
        self.etcd_host = etcd_host
        self.etcd_port = etcd_port
        self.enable_service_discovery = enable_service_discovery
        self.enable_distributed_tracing = enable_distributed_tracing
        
        # Service discovery clients
        self.consul_client = None
        self.etcd_client = None
        
        # Metrics storage
        self.service_calls: deque = deque(maxlen=50000)
        self.service_health: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.circuit_breaker_metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.service_mesh_metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.distributed_transactions: deque = deque(maxlen=10000)
        
        # Service tracking
        self.active_services: Dict[str, Dict] = {}
        self.service_dependencies: nx.DiGraph = nx.DiGraph()
        self.circuit_breakers: Dict[str, Dict] = defaultdict(lambda: {
            'state': 'closed',
            'failure_count': 0,
            'last_failure': None,
            'threshold': 5,
            'timeout_ms': 30000
        })
        
        # Distributed tracing
        self.active_traces: Dict[str, Dict] = {}
        self.trace_spans: Dict[str, List] = defaultdict(list)
        
        # Prometheus metrics
        self._init_prometheus_metrics()
        
        # Monitoring state
        self.monitoring_active = False
        self._monitoring_tasks = []
    
    def _init_prometheus_metrics(self):
        """Initialize Prometheus metrics"""
        self.service_call_duration_histogram = Histogram(
            'microservice_call_duration_seconds',
            'Service-to-service call duration',
            ['source_service', 'target_service', 'endpoint', 'status'],
            buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
        )
        
        self.service_health_score_gauge = Gauge(
            'microservice_health_score',
            'Service health score',
            ['service_name', 'instance_id']
        )
        
        self.circuit_breaker_state_gauge = Gauge(
            'microservice_circuit_breaker_state',
            'Circuit breaker state (0=closed, 1=open, 2=half_open)',
            ['source_service', 'target_service']
        )
        
        self.service_request_rate_gauge = Gauge(
            'microservice_request_rate_rps',
            'Service request rate per second',
            ['service_name', 'direction']  # inbound/outbound
        )
        
        self.service_error_rate_gauge = Gauge(
            'microservice_error_rate_percent',
            'Service error rate percentage',
            ['service_name']
        )
        
        self.distributed_transaction_duration_histogram = Histogram(
            'distributed_transaction_duration_seconds',
            'Distributed transaction duration',
            ['transaction_type', 'success'],
            buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0]
        )
        
        self.service_dependency_count_gauge = Gauge(
            'microservice_dependency_count',
            'Number of service dependencies',
            ['service_name', 'direction']  # upstream/downstream
        )
    
    async def initialize_service_discovery(self):
        """Initialize service discovery clients"""
        try:
            if self.enable_service_discovery:
                # Initialize Consul client
                try:
                    self.consul_client = consul.Consul(
                        host=self.consul_host,
                        port=self.consul_port
                    )
                    logger.info("Consul client initialized")
                except Exception as e:
                    logger.warning(f"Failed to initialize Consul client: {e}")
                
                # Initialize etcd client
                try:
                    self.etcd_client = etcd3.client(
                        host=self.etcd_host,
                        port=self.etcd_port
                    )
                    logger.info("etcd client initialized")
                except Exception as e:
                    logger.warning(f"Failed to initialize etcd client: {e}")
        
        except Exception as e:
            logger.error(f"Error initializing service discovery: {e}")
    
    def record_service_call(self,
                          source_service: str,
                          target_service: str,
                          endpoint: str,
                          method: str,
                          duration_ms: float,
                          status_code: int,
                          request_size: int = 0,
                          response_size: int = 0,
                          trace_id: Optional[str] = None) -> str:
        """Record a service-to-service call"""
        
        if not trace_id:
            trace_id = str(uuid.uuid4())
        
        span_id = str(uuid.uuid4())
        
        metrics = ServiceCallMetrics(
            trace_id=trace_id,
            span_id=span_id,
            source_service=source_service,
            target_service=target_service,
            endpoint=endpoint,
            method=method,
            start_time=datetime.utcnow() - timedelta(milliseconds=duration_ms),
            end_time=datetime.utcnow(),
            duration_ms=duration_ms,
            status_code=status_code,
            success=200 <= status_code < 400,
            request_size_bytes=request_size,
            response_size_bytes=response_size,
            circuit_breaker_state=self.circuit_breakers[f"{source_service}->{target_service}"]['state']
        )
        
        # Store metrics
        self.service_calls.append(metrics)
        
        # Update service dependency graph
        self.service_dependencies.add_edge(source_service, target_service)
        
        # Update circuit breaker state
        self._update_circuit_breaker(source_service, target_service, metrics.success)
        
        # Update Prometheus metrics
        self.service_call_duration_histogram.labels(
            source_service=source_service,
            target_service=target_service,
            endpoint=endpoint,
            status='success' if metrics.success else 'error'
        ).observe(duration_ms / 1000)
        
        # Add to distributed trace if enabled
        if self.enable_distributed_tracing:
            self._add_trace_span(trace_id, metrics)
        
        return trace_id
    
    def record_service_health(self,
                            service_name: str,
                            instance_id: str,
                            cpu_usage: float,
                            memory_usage: float,
                            active_connections: int,
                            request_queue_size: int,
                            health_status: str,
                            uptime_seconds: int,
                            error_rate: float,
                            p95_response_time: float):
        """Record service health metrics"""
        
        metrics = ServiceHealthMetrics(
            service_name=service_name,
            instance_id=instance_id,
            cpu_usage_percent=cpu_usage,
            memory_usage_mb=memory_usage,
            active_connections=active_connections,
            request_queue_size=request_queue_size,
            health_check_status=health_status,
            uptime_seconds=uptime_seconds,
            error_rate_percent=error_rate,
            response_time_p95_ms=p95_response_time,
            timestamp=datetime.utcnow()
        )
        
        self.service_health[service_name].append(metrics)
        
        # Calculate health score
        health_score = self._calculate_health_score(metrics)
        
        # Update Prometheus metrics
        self.service_health_score_gauge.labels(
            service_name=service_name,
            instance_id=instance_id
        ).set(health_score)
        
        self.service_error_rate_gauge.labels(
            service_name=service_name
        ).set(error_rate)
    
    def _calculate_health_score(self, metrics: ServiceHealthMetrics) -> float:
        """Calculate service health score (0-100)"""
        score = 100.0
        
        # CPU usage penalty
        if metrics.cpu_usage_percent > 80:
            score -= (metrics.cpu_usage_percent - 80) * 2
        
        # Memory usage penalty
        if metrics.memory_usage_mb > 1024:  # More than 1GB
            score -= min(20, (metrics.memory_usage_mb - 1024) / 1024 * 10)
        
        # Error rate penalty
        score -= metrics.error_rate_percent * 2
        
        # Response time penalty
        if metrics.response_time_p95_ms > 1000:  # More than 1 second
            score -= min(30, (metrics.response_time_p95_ms - 1000) / 1000 * 10)
        
        # Queue size penalty
        if metrics.request_queue_size > 100:
            score -= min(15, (metrics.request_queue_size - 100) / 100 * 5)
        
        # Health status penalty
        if metrics.health_check_status == 'degraded':
            score -= 20
        elif metrics.health_check_status == 'unhealthy':
            score -= 50
        
        return max(0.0, score)
    
    def _update_circuit_breaker(self, source_service: str, target_service: str, success: bool):
        """Update circuit breaker state"""
        key = f"{source_service}->{target_service}"
        cb = self.circuit_breakers[key]
        
        current_time = datetime.utcnow()
        
        if success:
            cb['success_count'] = cb.get('success_count', 0) + 1
            cb['last_success'] = current_time
            
            # If in half-open state and getting successes, close the circuit
            if cb['state'] == 'half_open' and cb['success_count'] >= 3:
                cb['state'] = 'closed'
                cb['failure_count'] = 0
        else:
            cb['failure_count'] += 1
            cb['last_failure'] = current_time
            cb['success_count'] = 0
            
            # Open circuit if failure threshold exceeded
            if cb['failure_count'] >= cb['threshold'] and cb['state'] == 'closed':
                cb['state'] = 'open'
        
        # Check if circuit should transition from open to half-open
        if cb['state'] == 'open' and cb['last_failure']:
            time_since_failure = (current_time - cb['last_failure']).total_seconds() * 1000
            if time_since_failure >= cb['timeout_ms']:
                cb['state'] = 'half_open'
                cb['success_count'] = 0
        
        # Record circuit breaker metrics
        cb_metrics = CircuitBreakerMetrics(
            service_name=source_service,
            target_service=target_service,
            state=cb['state'],
            failure_count=cb['failure_count'],
            failure_threshold=cb['threshold'],
            success_count=cb.get('success_count', 0),
            last_failure_time=cb['last_failure'],
            last_success_time=cb.get('last_success'),
            timeout_ms=cb['timeout_ms'],
            timestamp=current_time
        )
        
        self.circuit_breaker_metrics[key].append(cb_metrics)
        
        # Update Prometheus metrics
        state_value = {'closed': 0, 'open': 1, 'half_open': 2}[cb['state']]
        self.circuit_breaker_state_gauge.labels(
            source_service=source_service,
            target_service=target_service
        ).set(state_value)
    
    def start_distributed_transaction(self,
                                   transaction_type: str,
                                   participating_services: List[str]) -> str:
        """Start tracking a distributed transaction"""
        transaction_id = str(uuid.uuid4())
        
        self.active_traces[transaction_id] = {
            'transaction_type': transaction_type,
            'participating_services': participating_services,
            'start_time': datetime.utcnow(),
            'saga_steps': [],
            'compensation_actions': 0,
            'rollback_required': False
        }
        
        return transaction_id
    
    def complete_distributed_transaction(self,
                                       transaction_id: str,
                                       success: bool,
                                       error_service: Optional[str] = None,
                                       error_message: Optional[str] = None):
        """Complete a distributed transaction"""
        if transaction_id not in self.active_traces:
            logger.warning(f"Transaction {transaction_id} not found")
            return
        
        trace_data = self.active_traces[transaction_id]
        end_time = datetime.utcnow()
        duration_ms = (end_time - trace_data['start_time']).total_seconds() * 1000
        
        metrics = DistributedTransactionMetrics(
            transaction_id=transaction_id,
            transaction_type=trace_data['transaction_type'],
            participating_services=trace_data['participating_services'],
            start_time=trace_data['start_time'],
            end_time=end_time,
            total_duration_ms=duration_ms,
            success=success,
            rollback_required=trace_data['rollback_required'],
            compensation_actions=trace_data['compensation_actions'],
            saga_steps=len(trace_data['saga_steps']),
            error_service=error_service,
            error_message=error_message
        )
        
        self.distributed_transactions.append(metrics)
        
        # Update Prometheus metrics
        self.distributed_transaction_duration_histogram.labels(
            transaction_type=trace_data['transaction_type'],
            success=str(success)
        ).observe(duration_ms / 1000)
        
        # Clean up
        del self.active_traces[transaction_id]
    
    def _add_trace_span(self, trace_id: str, call_metrics: ServiceCallMetrics):
        """Add span to distributed trace"""
        self.trace_spans[trace_id].append(call_metrics)
        
        # Clean up old traces (keep only last 1000)
        if len(self.trace_spans) > 1000:
            oldest_traces = sorted(self.trace_spans.keys())[:100]
            for old_trace in oldest_traces:
                del self.trace_spans[old_trace]
    
    async def discover_services(self) -> Dict[str, List[Dict]]:
        """Discover services from service registry"""
        discovered_services = {}
        
        try:
            # Discover from Consul
            if self.consul_client:
                services = self.consul_client.catalog.services()[1]
                
                for service_name in services:
                    service_instances = self.consul_client.catalog.service(service_name)[1]
                    
                    instances = []
                    for instance in service_instances:
                        instances.append({
                            'id': instance.get('ServiceID'),
                            'name': instance.get('ServiceName'),
                            'address': instance.get('ServiceAddress'),
                            'port': instance.get('ServicePort'),
                            'tags': instance.get('ServiceTags', []),
                            'meta': instance.get('ServiceMeta', {}),
                            'health': 'unknown'  # Would need separate health check
                        })
                    
                    discovered_services[service_name] = instances
            
            # Update active services
            self.active_services.update(discovered_services)
            
        except Exception as e:
            logger.error(f"Error discovering services: {e}")
        
        return discovered_services
    
    def analyze_service_dependencies(self) -> Dict[str, ServiceDependencyMetrics]:
        """Analyze service dependency graph"""
        dependency_analysis = {}
        
        for service in self.service_dependencies.nodes():
            # Get direct dependencies (services this service calls)
            dependencies = list(self.service_dependencies.successors(service))
            
            # Get dependents (services that call this service)
            dependents = list(self.service_dependencies.predecessors(service))
            
            # Calculate dependency health score
            health_score = self._calculate_dependency_health_score(service, dependencies)
            
            # Calculate critical path length
            critical_path_length = self._calculate_critical_path_length(service)
            
            # Check if this is a single point of failure
            single_point_of_failure = self._is_single_point_of_failure(service)
            
            dependency_analysis[service] = ServiceDependencyMetrics(
                service_name=service,
                dependencies=dependencies,
                dependents=dependents,
                dependency_health_score=health_score,
                critical_path_length=critical_path_length,
                single_point_of_failure=single_point_of_failure,
                timestamp=datetime.utcnow()
            )
            
            # Update Prometheus metrics
            self.service_dependency_count_gauge.labels(
                service_name=service,
                direction='downstream'
            ).set(len(dependencies))
            
            self.service_dependency_count_gauge.labels(
                service_name=service,
                direction='upstream'
            ).set(len(dependents))
        
        return dependency_analysis
    
    def _calculate_dependency_health_score(self, service: str, dependencies: List[str]) -> float:
        """Calculate dependency health score"""
        if not dependencies:
            return 100.0
        
        total_score = 0.0
        for dependency in dependencies:
            # Get recent health metrics for dependency
            if dependency in self.service_health:
                recent_health = list(self.service_health[dependency])[-5:]  # Last 5 measurements
                if recent_health:
                    dependency_scores = [self._calculate_health_score(h) for h in recent_health]
                    total_score += statistics.mean(dependency_scores)
                else:
                    total_score += 50.0  # Unknown health
            else:
                total_score += 50.0  # Unknown service
        
        return total_score / len(dependencies)
    
    def _calculate_critical_path_length(self, service: str) -> int:
        """Calculate critical path length from service"""
        try:
            # Find longest path from this service
            longest_path = 0
            for target in self.service_dependencies.nodes():
                if service != target and nx.has_path(self.service_dependencies, service, target):
                    path_length = nx.shortest_path_length(self.service_dependencies, service, target)
                    longest_path = max(longest_path, path_length)
            return longest_path
        except:
            return 0
    
    def _is_single_point_of_failure(self, service: str) -> bool:
        """Check if service is a single point of failure"""
        # A service is a SPOF if removing it disconnects the graph
        temp_graph = self.service_dependencies.copy()
        temp_graph.remove_node(service)
        
        # Check if graph becomes disconnected
        original_components = nx.number_weakly_connected_components(self.service_dependencies)
        new_components = nx.number_weakly_connected_components(temp_graph)
        
        return new_components > original_components
    
    def get_service_performance_summary(self, service_name: Optional[str] = None) -> Dict[str, Any]:
        """Get service performance summary"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=15)
        
        if service_name:
            # Filter for specific service
            recent_calls = [c for c in self.service_calls 
                          if c.start_time >= cutoff_time and 
                          (c.source_service == service_name or c.target_service == service_name)]
        else:
            recent_calls = [c for c in self.service_calls if c.start_time >= cutoff_time]
        
        if not recent_calls:
            return {'message': 'No recent service call data available'}
        
        # Calculate metrics
        total_calls = len(recent_calls)
        successful_calls = len([c for c in recent_calls if c.success])
        success_rate = (successful_calls / total_calls) * 100
        
        durations = [c.duration_ms for c in recent_calls]
        avg_duration = statistics.mean(durations)
        p95_duration = statistics.quantiles(durations, n=20)[18] if len(durations) >= 20 else max(durations)
        
        # Group by service pairs
        service_pairs = defaultdict(list)
        for call in recent_calls:
            pair_key = f"{call.source_service} -> {call.target_service}"
            service_pairs[pair_key].append(call)
        
        pair_summary = {}
        for pair, calls in service_pairs.items():
            pair_durations = [c.duration_ms for c in calls]
            pair_success_rate = len([c for c in calls if c.success]) / len(calls) * 100
            
            pair_summary[pair] = {
                'call_count': len(calls),
                'success_rate': pair_success_rate,
                'avg_duration_ms': statistics.mean(pair_durations),
                'p95_duration_ms': statistics.quantiles(pair_durations, n=20)[18] if len(pair_durations) >= 20 else max(pair_durations)
            }
        
        return {
            'time_window_minutes': 15,
            'total_calls': total_calls,
            'success_rate': success_rate,
            'avg_duration_ms': avg_duration,
            'p95_duration_ms': p95_duration,
            'service_pairs': pair_summary,
            'circuit_breaker_open_count': len([cb for cb in self.circuit_breakers.values() if cb['state'] == 'open'])
        }
    
    async def start_monitoring(self):
        """Start continuous monitoring"""
        if self.monitoring_active:
            logger.warning("Microservices monitoring already active")
            return
        
        await self.initialize_service_discovery()
        self.monitoring_active = True
        
        # Start monitoring tasks
        tasks = [
            self._service_discovery_loop(),
            self._dependency_analysis_loop(),
            self._health_check_loop()
        ]
        
        self._monitoring_tasks = [asyncio.create_task(task) for task in tasks]
        logger.info("Microservices performance monitoring started")
    
    async def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring_active = False
        
        for task in self._monitoring_tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        self._monitoring_tasks.clear()
        logger.info("Microservices performance monitoring stopped")
    
    async def _service_discovery_loop(self):
        """Service discovery monitoring loop"""
        while self.monitoring_active:
            try:
                await self.discover_services()
                await asyncio.sleep(30)  # Discover services every 30 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in service discovery loop: {e}")
                await asyncio.sleep(30)
    
    async def _dependency_analysis_loop(self):
        """Dependency analysis loop"""
        while self.monitoring_active:
            try:
                self.analyze_service_dependencies()
                await asyncio.sleep(60)  # Analyze dependencies every minute
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in dependency analysis loop: {e}")
                await asyncio.sleep(60)
    
    async def _health_check_loop(self):
        """Health check monitoring loop"""
        while self.monitoring_active:
            try:
                # Perform health checks on discovered services
                for service_name, instances in self.active_services.items():
                    for instance in instances:
                        try:
                            # Simplified health check - would be more sophisticated in practice
                            health_url = f"http://{instance['address']}:{instance['port']}/health"
                            
                            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                                async with session.get(health_url) as response:
                                    health_status = 'healthy' if response.status == 200 else 'degraded'
                        except:
                            health_status = 'unhealthy'
                        
                        # Record simplified health metrics
                        self.record_service_health(
                            service_name=service_name,
                            instance_id=instance['id'],
                            cpu_usage=0.0,  # Would get from actual monitoring
                            memory_usage=0.0,
                            active_connections=0,
                            request_queue_size=0,
                            health_status=health_status,
                            uptime_seconds=0,
                            error_rate=0.0,
                            p95_response_time=0.0
                        )
                
                await asyncio.sleep(15)  # Health checks every 15 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health check loop: {e}")
                await asyncio.sleep(15)