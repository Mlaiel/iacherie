#!/usr/bin/env python3
"""
🏗️ ENTERPRISE ORCHESTRATION SERVICE
====================================

Unified service combining enterprise master orchestration and microservices orchestration.
Provides comprehensive orchestration for enterprise modules, microservices management,
service discovery, and inter-service communication.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️ STRICT COPYRIGHT WARNING ⚠️
This code is proprietary and confidential. Unauthorized use, reproduction,
distribution, or modification is strictly prohibited and will be prosecuted
to the full extent of the law.
"""

import asyncio
import logging
import time
import json
import uuid
import statistics
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, Set, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import concurrent.futures
import yaml

# Optional imports with graceful fallbacks
try:
    import aiohttp
    from aiohttp import web, ClientSession
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False

try:
    import consul
    CONSUL_AVAILABLE = True
except ImportError:
    CONSUL_AVAILABLE = False

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    from prometheus_client import Counter, Histogram, Gauge
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ===== ENUMS =====
class OrchestrationStatus(Enum):
    """Orchestration status enumeration"""
    INITIALIZING = "initializing"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    OFFLINE = "offline"

class ServiceHealthStatus(Enum):
    """Service health status enumeration"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"
    STARTING = "starting"
    STOPPING = "stopping"

class ServiceType(Enum):
    """Service type enumeration"""
    API_GATEWAY = "api_gateway"
    MICROSERVICE = "microservice"
    DATABASE = "database"
    MESSAGE_QUEUE = "message_queue"
    CACHE = "cache"
    STORAGE = "storage"
    MONITORING = "monitoring"

class LoadBalancingStrategy(Enum):
    """Load balancing strategy enumeration"""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    IP_HASH = "ip_hash"
    LEAST_RESPONSE_TIME = "least_response_time"

class CircuitState(Enum):
    """Circuit breaker state"""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

# ===== DATA CLASSES =====
@dataclass
class ServiceMetrics:
    """Service performance metrics"""
    service_name: str
    request_count: int = 0
    response_time_avg: float = 0.0
    error_rate: float = 0.0
    last_health_check: Optional[datetime] = None
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    uptime: float = 0.0

@dataclass
class ServiceInstance:
    """Service instance definition"""
    service_id: str
    service_name: str
    host: str
    port: int
    service_type: ServiceType
    health_status: ServiceHealthStatus = ServiceHealthStatus.UNKNOWN
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    version: str = "1.0.0"
    weight: int = 100
    last_heartbeat: Optional[datetime] = None

@dataclass
class OrchestrationModule:
    """Enterprise module definition"""
    module_id: str
    module_name: str
    services: List[ServiceInstance] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    status: OrchestrationStatus = OrchestrationStatus.INITIALIZING
    configuration: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CircuitBreaker:
    """Circuit breaker for service resilience"""
    service_name: str
    failure_threshold: int = 5
    timeout: int = 60
    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    last_failure_time: Optional[datetime] = None
    success_threshold: int = 3
    success_count: int = 0

@dataclass
class ServiceRoute:
    """Service routing configuration"""
    route_id: str
    path: str
    service_name: str
    methods: List[str] = field(default_factory=lambda: ["GET"])
    middleware: List[str] = field(default_factory=list)
    rate_limit: Optional[int] = None
    timeout: int = 30

@dataclass
class MessageEvent:
    """Event for inter-service communication"""
    event_id: str
    event_type: str
    source_service: str
    target_service: Optional[str] = None
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    priority: int = 0
    ttl: Optional[int] = None

class EnterpriseOrchestrationService:
    """Unified Enterprise Orchestration Service"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the orchestration service"""
        self.config = config
        self.modules: Dict[str, OrchestrationModule] = {}
        self.services: Dict[str, ServiceInstance] = {}
        self.service_registry: Dict[str, List[ServiceInstance]] = defaultdict(list)
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.routes: Dict[str, ServiceRoute] = {}
        self.message_queue: deque = deque()
        self.event_handlers: Dict[str, List[Callable]] = defaultdict(list)
        
        # Metrics
        self.metrics: Dict[str, ServiceMetrics] = {}
        self.global_metrics = {
            'total_requests': 0,
            'total_errors': 0,
            'average_response_time': 0.0,
            'active_services': 0
        }
        
        # Initialize components
        self._init_service_discovery()
        self._init_load_balancer()
        self._init_monitoring()
        self._init_message_system()
        
        # State management
        self.is_running = False
        self.health_check_interval = config.get('health_check_interval', 30)
        self.metrics_collection_interval = config.get('metrics_interval', 60)
        
        logger.info("Enterprise Orchestration Service initialized")

    def _init_service_discovery(self):
        """Initialize service discovery"""
        if CONSUL_AVAILABLE and self.config.get('consul_enabled', False):
            try:
                self.consul = consul.Consul(
                    host=self.config.get('consul_host', 'localhost'),
                    port=self.config.get('consul_port', 8500)
                )
                logger.info("Consul service discovery initialized")
            except Exception as e:
                logger.warning(f"Consul initialization failed: {e}")
                self.consul = None
        else:
            self.consul = None

    def _init_load_balancer(self):
        """Initialize load balancer"""
        self.load_balancing_strategy = LoadBalancingStrategy(
            self.config.get('load_balancing_strategy', 'round_robin')
        )
        self.load_balancer_state = defaultdict(int)
        
    def _init_monitoring(self):
        """Initialize monitoring"""
        if PROMETHEUS_AVAILABLE:
            # Prometheus metrics
            self.request_counter = Counter('orchestrator_requests_total', 
                                         'Total requests', ['service'])
            self.response_time_histogram = Histogram('orchestrator_response_time_seconds',
                                                   'Response time', ['service'])
            self.service_health_gauge = Gauge('orchestrator_service_health',
                                            'Service health status', ['service'])
        
        if REDIS_AVAILABLE:
            try:
                self.redis_client = redis.Redis(
                    host=self.config.get('redis_host', 'localhost'),
                    port=self.config.get('redis_port', 6379),
                    db=self.config.get('redis_db', 0)
                )
                logger.info("Redis monitoring storage initialized")
            except Exception as e:
                logger.warning(f"Redis initialization failed: {e}")
                self.redis_client = None
        else:
            self.redis_client = None

    def _init_message_system(self):
        """Initialize message system for inter-service communication"""
        self.message_subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self.message_processors = []

    # ===== MODULE MANAGEMENT =====
    async def register_module(self, module: OrchestrationModule):
        """Register an enterprise module"""
        try:
            self.modules[module.module_id] = module
            
            # Register all services in the module
            for service in module.services:
                await self.register_service(service)
            
            logger.info(f"Module registered: {module.module_name}")
            
        except Exception as e:
            logger.error(f"Module registration failed: {e}")
            raise

    async def unregister_module(self, module_id: str):
        """Unregister an enterprise module"""
        try:
            if module_id in self.modules:
                module = self.modules[module_id]
                
                # Unregister all services
                for service in module.services:
                    await self.unregister_service(service.service_id)
                
                del self.modules[module_id]
                logger.info(f"Module unregistered: {module_id}")
                
        except Exception as e:
            logger.error(f"Module unregistration failed: {e}")

    # ===== SERVICE MANAGEMENT =====
    async def register_service(self, service: ServiceInstance):
        """Register a service instance"""
        try:
            # Add to service registry
            self.services[service.service_id] = service
            self.service_registry[service.service_name].append(service)
            
            # Initialize metrics
            if service.service_name not in self.metrics:
                self.metrics[service.service_name] = ServiceMetrics(service.service_name)
            
            # Initialize circuit breaker
            if service.service_name not in self.circuit_breakers:
                self.circuit_breakers[service.service_name] = CircuitBreaker(service.service_name)
            
            # Register with external service discovery
            if self.consul:
                await self._register_with_consul(service)
            
            # Update metrics
            self.global_metrics['active_services'] = len(self.services)
            
            logger.info(f"Service registered: {service.service_name}@{service.host}:{service.port}")
            
        except Exception as e:
            logger.error(f"Service registration failed: {e}")
            raise

    async def unregister_service(self, service_id: str):
        """Unregister a service instance"""
        try:
            if service_id in self.services:
                service = self.services[service_id]
                
                # Remove from registry
                if service.service_name in self.service_registry:
                    self.service_registry[service.service_name] = [
                        s for s in self.service_registry[service.service_name]
                        if s.service_id != service_id
                    ]
                
                # Deregister from external service discovery
                if self.consul:
                    await self._deregister_from_consul(service)
                
                del self.services[service_id]
                self.global_metrics['active_services'] = len(self.services)
                
                logger.info(f"Service unregistered: {service_id}")
                
        except Exception as e:
            logger.error(f"Service unregistration failed: {e}")

    async def _register_with_consul(self, service: ServiceInstance):
        """Register service with Consul"""
        try:
            self.consul.agent.service.register(
                name=service.service_name,
                service_id=service.service_id,
                address=service.host,
                port=service.port,
                tags=service.tags,
                meta=service.metadata,
                check=consul.Check.http(
                    url=f"http://{service.host}:{service.port}/health",
                    interval="30s"
                )
            )
        except Exception as e:
            logger.error(f"Consul registration failed: {e}")

    async def _deregister_from_consul(self, service: ServiceInstance):
        """Deregister service from Consul"""
        try:
            self.consul.agent.service.deregister(service.service_id)
        except Exception as e:
            logger.error(f"Consul deregistration failed: {e}")

    # ===== SERVICE DISCOVERY =====
    async def discover_service(self, service_name: str) -> Optional[ServiceInstance]:
        """Discover a service instance using load balancing"""
        try:
            instances = self.service_registry.get(service_name, [])
            healthy_instances = [
                s for s in instances 
                if s.health_status == ServiceHealthStatus.HEALTHY
            ]
            
            if not healthy_instances:
                logger.warning(f"No healthy instances found for service: {service_name}")
                return None
            
            return await self._select_instance(service_name, healthy_instances)
            
        except Exception as e:
            logger.error(f"Service discovery failed: {e}")
            return None

    async def _select_instance(self, service_name: str, 
                             instances: List[ServiceInstance]) -> ServiceInstance:
        """Select service instance based on load balancing strategy"""
        if self.load_balancing_strategy == LoadBalancingStrategy.ROUND_ROBIN:
            index = self.load_balancer_state[service_name] % len(instances)
            self.load_balancer_state[service_name] += 1
            return instances[index]
        
        elif self.load_balancing_strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
            # Select instance with least connections (simplified)
            return min(instances, key=lambda x: x.metadata.get('connections', 0))
        
        elif self.load_balancing_strategy == LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN:
            # Weighted selection based on instance weight
            total_weight = sum(instance.weight for instance in instances)
            target = self.load_balancer_state[service_name] % total_weight
            self.load_balancer_state[service_name] += 1
            
            current_weight = 0
            for instance in instances:
                current_weight += instance.weight
                if current_weight > target:
                    return instance
            
            return instances[0]  # Fallback
        
        else:
            # Default to first available
            return instances[0]

    # ===== HEALTH MONITORING =====
    async def start_health_monitoring(self):
        """Start health monitoring for all services"""
        if not self.is_running:
            self.is_running = True
            asyncio.create_task(self._health_monitoring_loop())
            asyncio.create_task(self._metrics_collection_loop())
            logger.info("Health monitoring started")

    async def stop_health_monitoring(self):
        """Stop health monitoring"""
        self.is_running = False
        logger.info("Health monitoring stopped")

    async def _health_monitoring_loop(self):
        """Main health monitoring loop"""
        while self.is_running:
            try:
                await self._check_all_services_health()
                await asyncio.sleep(self.health_check_interval)
            except Exception as e:
                logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(5)

    async def _check_all_services_health(self):
        """Check health of all registered services"""
        tasks = []
        for service in self.services.values():
            task = asyncio.create_task(self._check_service_health(service))
            tasks.append(task)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _check_service_health(self, service: ServiceInstance):
        """Check health of a specific service"""
        try:
            if not AIOHTTP_AVAILABLE:
                service.health_status = ServiceHealthStatus.UNKNOWN
                return
            
            health_url = f"http://{service.host}:{service.port}/health"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(health_url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    if response.status == 200:
                        service.health_status = ServiceHealthStatus.HEALTHY
                        service.last_heartbeat = datetime.now()
                        
                        # Reset circuit breaker on successful health check
                        if service.service_name in self.circuit_breakers:
                            cb = self.circuit_breakers[service.service_name]
                            if cb.state == CircuitState.HALF_OPEN:
                                cb.success_count += 1
                                if cb.success_count >= cb.success_threshold:
                                    cb.state = CircuitState.CLOSED
                                    cb.failure_count = 0
                    else:
                        service.health_status = ServiceHealthStatus.WARNING
                        
        except Exception as e:
            service.health_status = ServiceHealthStatus.CRITICAL
            logger.warning(f"Health check failed for {service.service_name}: {e}")
            
            # Update circuit breaker
            await self._update_circuit_breaker(service.service_name, failed=True)

    # ===== CIRCUIT BREAKER =====
    async def _update_circuit_breaker(self, service_name: str, failed: bool = False):
        """Update circuit breaker state"""
        if service_name not in self.circuit_breakers:
            return
        
        cb = self.circuit_breakers[service_name]
        
        if failed:
            cb.failure_count += 1
            cb.last_failure_time = datetime.now()
            
            if cb.state == CircuitState.CLOSED and cb.failure_count >= cb.failure_threshold:
                cb.state = CircuitState.OPEN
                logger.warning(f"Circuit breaker opened for service: {service_name}")
        
        elif cb.state == CircuitState.OPEN:
            # Check if timeout has passed
            if (datetime.now() - cb.last_failure_time).seconds > cb.timeout:
                cb.state = CircuitState.HALF_OPEN
                cb.success_count = 0
                logger.info(f"Circuit breaker half-opened for service: {service_name}")

    def is_circuit_breaker_open(self, service_name: str) -> bool:
        """Check if circuit breaker is open for a service"""
        if service_name not in self.circuit_breakers:
            return False
        
        cb = self.circuit_breakers[service_name]
        return cb.state == CircuitState.OPEN

    # ===== METRICS COLLECTION =====
    async def _metrics_collection_loop(self):
        """Collect and aggregate metrics"""
        while self.is_running:
            try:
                await self._collect_service_metrics()
                await self._update_global_metrics()
                await asyncio.sleep(self.metrics_collection_interval)
            except Exception as e:
                logger.error(f"Metrics collection error: {e}")
                await asyncio.sleep(10)

    async def _collect_service_metrics(self):
        """Collect metrics from all services"""
        for service_name, instances in self.service_registry.items():
            if service_name in self.metrics:
                metrics = self.metrics[service_name]
                
                # Update metrics with current data
                healthy_count = sum(1 for instance in instances 
                                  if instance.health_status == ServiceHealthStatus.HEALTHY)
                
                metrics.last_health_check = datetime.now()
                
                # Store metrics in Redis if available
                if self.redis_client:
                    await self._store_metrics_in_redis(service_name, metrics)

    async def _update_global_metrics(self):
        """Update global orchestration metrics"""
        self.global_metrics.update({
            'active_services': len(self.services),
            'healthy_services': sum(1 for s in self.services.values() 
                                  if s.health_status == ServiceHealthStatus.HEALTHY),
            'modules_count': len(self.modules),
            'timestamp': datetime.now().isoformat()
        })

    async def _store_metrics_in_redis(self, service_name: str, metrics: ServiceMetrics):
        """Store metrics in Redis"""
        try:
            metrics_data = {
                'service_name': metrics.service_name,
                'request_count': metrics.request_count,
                'response_time_avg': metrics.response_time_avg,
                'error_rate': metrics.error_rate,
                'last_health_check': metrics.last_health_check.isoformat() if metrics.last_health_check else None,
                'timestamp': datetime.now().isoformat()
            }
            
            await self.redis_client.hset(
                f"orchestrator:metrics:{service_name}",
                mapping=metrics_data
            )
            
        except Exception as e:
            logger.error(f"Metrics storage failed: {e}")

    # ===== MESSAGING SYSTEM =====
    async def publish_event(self, event: MessageEvent):
        """Publish an event to the message system"""
        try:
            self.message_queue.append(event)
            
            # Process event immediately if handlers exist
            if event.event_type in self.event_handlers:
                for handler in self.event_handlers[event.event_type]:
                    try:
                        await handler(event)
                    except Exception as e:
                        logger.error(f"Event handler failed: {e}")
            
            logger.debug(f"Event published: {event.event_type}")
            
        except Exception as e:
            logger.error(f"Event publishing failed: {e}")

    def subscribe_to_event(self, event_type: str, handler: Callable):
        """Subscribe to an event type"""
        self.event_handlers[event_type].append(handler)
        logger.info(f"Handler subscribed to event: {event_type}")

    async def send_message(self, source_service: str, target_service: str, 
                         message_type: str, payload: Dict[str, Any]):
        """Send a direct message between services"""
        event = MessageEvent(
            event_id=str(uuid.uuid4()),
            event_type=message_type,
            source_service=source_service,
            target_service=target_service,
            payload=payload
        )
        
        await self.publish_event(event)

    # ===== ROUTING MANAGEMENT =====
    def register_route(self, route: ServiceRoute):
        """Register a service route"""
        self.routes[route.route_id] = route
        logger.info(f"Route registered: {route.path} -> {route.service_name}")

    def unregister_route(self, route_id: str):
        """Unregister a service route"""
        if route_id in self.routes:
            del self.routes[route_id]
            logger.info(f"Route unregistered: {route_id}")

    async def route_request(self, path: str, method: str = "GET") -> Optional[ServiceInstance]:
        """Route a request to appropriate service"""
        for route in self.routes.values():
            if route.path == path and method in route.methods:
                if not self.is_circuit_breaker_open(route.service_name):
                    return await self.discover_service(route.service_name)
                else:
                    logger.warning(f"Circuit breaker open for service: {route.service_name}")
                    return None
        
        return None

    # ===== STATUS AND REPORTING =====
    async def get_orchestration_status(self) -> Dict[str, Any]:
        """Get overall orchestration status"""
        healthy_services = sum(1 for s in self.services.values() 
                             if s.health_status == ServiceHealthStatus.HEALTHY)
        total_services = len(self.services)
        
        if total_services == 0:
            status = OrchestrationStatus.OFFLINE
        elif healthy_services == total_services:
            status = OrchestrationStatus.HEALTHY
        elif healthy_services > total_services * 0.7:
            status = OrchestrationStatus.DEGRADED
        else:
            status = OrchestrationStatus.CRITICAL
        
        return {
            'status': status.value,
            'total_services': total_services,
            'healthy_services': healthy_services,
            'modules_count': len(self.modules),
            'active_circuit_breakers': len([cb for cb in self.circuit_breakers.values() 
                                          if cb.state != CircuitState.CLOSED]),
            'routes_count': len(self.routes),
            'global_metrics': self.global_metrics,
            'timestamp': datetime.now().isoformat()
        }

    async def get_service_details(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a service"""
        instances = self.service_registry.get(service_name, [])
        if not instances:
            return None
        
        metrics = self.metrics.get(service_name)
        circuit_breaker = self.circuit_breakers.get(service_name)
        
        return {
            'service_name': service_name,
            'instances': [
                {
                    'service_id': instance.service_id,
                    'host': instance.host,
                    'port': instance.port,
                    'health_status': instance.health_status.value,
                    'version': instance.version,
                    'weight': instance.weight,
                    'last_heartbeat': instance.last_heartbeat.isoformat() if instance.last_heartbeat else None
                }
                for instance in instances
            ],
            'metrics': {
                'request_count': metrics.request_count if metrics else 0,
                'response_time_avg': metrics.response_time_avg if metrics else 0.0,
                'error_rate': metrics.error_rate if metrics else 0.0
            } if metrics else {},
            'circuit_breaker': {
                'state': circuit_breaker.state.value,
                'failure_count': circuit_breaker.failure_count,
                'success_count': circuit_breaker.success_count
            } if circuit_breaker else {}
        }

    async def list_services(self) -> List[Dict[str, Any]]:
        """List all registered services"""
        return [
            {
                'service_id': service.service_id,
                'service_name': service.service_name,
                'host': service.host,
                'port': service.port,
                'service_type': service.service_type.value,
                'health_status': service.health_status.value,
                'version': service.version
            }
            for service in self.services.values()
        ]

    async def shutdown(self):
        """Gracefully shutdown the orchestration service"""
        logger.info("Starting orchestration service shutdown")
        
        await self.stop_health_monitoring()
        
        # Deregister all services from external discovery
        if self.consul:
            for service in self.services.values():
                await self._deregister_from_consul(service)
        
        # Clear all data
        self.services.clear()
        self.service_registry.clear()
        self.modules.clear()
        
        logger.info("Orchestration service shutdown completed")

# ===== SERVICE FACTORY =====
def create_enterprise_orchestration_service(config: Dict[str, Any]) -> EnterpriseOrchestrationService:
    """Factory function to create enterprise orchestration service"""
    return EnterpriseOrchestrationService(config)

# Example usage and testing
if __name__ == "__main__":
    async def main():
        config = {
            'consul_enabled': False,
            'redis_host': 'localhost',
            'redis_port': 6379,
            'health_check_interval': 30,
            'metrics_interval': 60,
            'load_balancing_strategy': 'round_robin'
        }
        
        orchestrator = create_enterprise_orchestration_service(config)
        
        # Register a test service
        test_service = ServiceInstance(
            service_id="test-service-1",
            service_name="test-service",
            host="localhost",
            port=8080,
            service_type=ServiceType.MICROSERVICE,
            tags=["api", "test"]
        )
        
        await orchestrator.register_service(test_service)
        
        # Start monitoring
        await orchestrator.start_health_monitoring()
        
        # Get status
        status = await orchestrator.get_orchestration_status()
        print(f"Orchestration Status: {status}")
        
        # Keep running for a short while
        await asyncio.sleep(10)
        
        await orchestrator.shutdown()
    
    asyncio.run(main())