"""
Enterprise Architecture Manager - Microservices & Backend Senior Implementation
Author: Fahed Mlaiel (mlaiel@live.de)
Role: Backend Senior + Microservices + DevOps Engineer
Version: 2.0 Enterprise Production
"""

import asyncio
import logging
import json
import time
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import aiohttp
import asyncpg
import redis.asyncio as redis
from contextlib import asynccontextmanager
import circuit_breaker
from prometheus_client import Counter, Histogram, Gauge
import structlog

# Enterprise Configuration
@dataclass
class ServiceConfig:
    """Configuration for microservices"""
    service_id: str
    service_name: str
    version: str
    endpoints: List[str]
    dependencies: List[str] = field(default_factory=list)
    health_check_url: str = ""
    metrics_endpoint: str = ""
    circuit_breaker_config: Dict[str, Any] = field(default_factory=dict)
    rate_limit: int = 1000
    timeout: int = 30
    retry_attempts: int = 3
    load_balancer_strategy: str = "round_robin"

class ServiceStatus(Enum):
    """Service status enumeration"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    MAINTENANCE = "maintenance"
    UNKNOWN = "unknown"

class LoadBalancerStrategy(Enum):
    """Load balancer strategy enumeration"""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    IP_HASH = "ip_hash"
    RANDOM = "random"

@dataclass
class ServiceMetrics:
    """Service performance metrics"""
    requests_total: int = 0
    requests_successful: int = 0
    requests_failed: int = 0
    average_response_time: float = 0.0
    current_connections: int = 0
    peak_connections: int = 0
    uptime_percentage: float = 100.0
    last_health_check: Optional[datetime] = None
    error_rate: float = 0.0
    throughput: float = 0.0

class CircuitBreakerManager:
    """Enterprise Circuit Breaker Implementation"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.circuit_breakers: Dict[str, circuit_breaker.CircuitBreaker] = {}
        
    def get_circuit_breaker(self, service_id: str) -> circuit_breaker.CircuitBreaker:
        """Get or create circuit breaker for service"""
        if service_id not in self.circuit_breakers:
            self.circuit_breakers[service_id] = circuit_breaker.CircuitBreaker(
                failure_threshold=self.failure_threshold,
                recovery_timeout=self.recovery_timeout
            )
        return self.circuit_breakers[service_id]
    
    async def call_with_circuit_breaker(self, service_id: str, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        cb = self.get_circuit_breaker(service_id)
        return await cb.call(func, *args, **kwargs)

class ConnectionPool:
    """Enterprise Connection Pool Manager"""
    
    def __init__(self, max_connections: int = 100):
        self.max_connections = max_connections
        self.pools: Dict[str, Any] = {}
        self.connection_counts: Dict[str, int] = {}
        
    async def get_db_pool(self, database_url: str, pool_name: str = "default") -> asyncpg.Pool:
        """Get database connection pool"""
        if pool_name not in self.pools:
            self.pools[pool_name] = await asyncpg.create_pool(
                database_url,
                min_size=10,
                max_size=self.max_connections,
                command_timeout=60
            )
            self.connection_counts[pool_name] = 0
        return self.pools[pool_name]
    
    async def get_redis_pool(self, redis_url: str, pool_name: str = "default") -> redis.Redis:
        """Get Redis connection pool"""
        if pool_name not in self.pools:
            self.pools[pool_name] = redis.from_url(
                redis_url,
                max_connections=self.max_connections,
                retry_on_timeout=True
            )
            self.connection_counts[pool_name] = 0
        return self.pools[pool_name]
    
    @asynccontextmanager
    async def get_connection(self, pool_name: str = "default"):
        """Get connection from pool with context manager"""
        if pool_name not in self.pools:
            raise ValueError(f"Pool '{pool_name}' not found")
        
        pool = self.pools[pool_name]
        self.connection_counts[pool_name] += 1
        
        try:
            if isinstance(pool, asyncpg.Pool):
                async with pool.acquire() as connection:
                    yield connection
            else:
                yield pool
        finally:
            self.connection_counts[pool_name] -= 1

class LoadBalancer:
    """Enterprise Load Balancer Implementation"""
    
    def __init__(self, strategy: LoadBalancerStrategy = LoadBalancerStrategy.ROUND_ROBIN):
        self.strategy = strategy
        self.service_instances: Dict[str, List[Dict[str, Any]]] = {}
        self.current_index: Dict[str, int] = {}
        self.weights: Dict[str, Dict[str, int]] = {}
        
    def register_service_instance(self, service_id: str, instance_info: Dict[str, Any]):
        """Register a service instance"""
        if service_id not in self.service_instances:
            self.service_instances[service_id] = []
            self.current_index[service_id] = 0
            self.weights[service_id] = {}
        
        self.service_instances[service_id].append(instance_info)
        instance_url = instance_info['url']
        self.weights[service_id][instance_url] = instance_info.get('weight', 1)
    
    def get_next_instance(self, service_id: str) -> Optional[Dict[str, Any]]:
        """Get next service instance based on load balancing strategy"""
        if service_id not in self.service_instances or not self.service_instances[service_id]:
            return None
        
        instances = self.service_instances[service_id]
        
        if self.strategy == LoadBalancerStrategy.ROUND_ROBIN:
            return self._round_robin_selection(service_id, instances)
        elif self.strategy == LoadBalancerStrategy.LEAST_CONNECTIONS:
            return self._least_connections_selection(instances)
        elif self.strategy == LoadBalancerStrategy.RANDOM:
            return self._random_selection(instances)
        elif self.strategy == LoadBalancerStrategy.WEIGHTED_ROUND_ROBIN:
            return self._weighted_round_robin_selection(service_id, instances)
        else:
            return instances[0]  # Default fallback
    
    def _round_robin_selection(self, service_id: str, instances: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Round robin selection"""
        index = self.current_index[service_id]
        instance = instances[index]
        self.current_index[service_id] = (index + 1) % len(instances)
        return instance
    
    def _least_connections_selection(self, instances: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Least connections selection"""
        return min(instances, key=lambda x: x.get('current_connections', 0))
    
    def _random_selection(self, instances: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Random selection"""
        import random
        return random.choice(instances)
    
    def _weighted_round_robin_selection(self, service_id: str, instances: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Weighted round robin selection"""
        # Simplified implementation
        return self._round_robin_selection(service_id, instances)

class ServiceRegistry:
    """Enterprise Service Registry and Discovery"""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis_client = redis_client
        self.services: Dict[str, ServiceConfig] = {}
        self.service_instances: Dict[str, List[Dict[str, Any]]] = {}
        self.service_metrics: Dict[str, ServiceMetrics] = {}
        self.logger = structlog.get_logger()
        
    async def register_service(self, config: ServiceConfig):
        """Register a service in the registry"""
        self.services[config.service_id] = config
        self.service_metrics[config.service_id] = ServiceMetrics()
        
        if self.redis_client:
            await self.redis_client.hset(
                "services",
                config.service_id,
                json.dumps({
                    'service_name': config.service_name,
                    'version': config.version,
                    'endpoints': config.endpoints,
                    'registered_at': datetime.utcnow().isoformat()
                })
            )
        
        self.logger.info("Service registered", service_id=config.service_id)
    
    async def deregister_service(self, service_id: str):
        """Deregister a service from the registry"""
        if service_id in self.services:
            del self.services[service_id]
        
        if service_id in self.service_metrics:
            del self.service_metrics[service_id]
        
        if self.redis_client:
            await self.redis_client.hdel("services", service_id)
        
        self.logger.info("Service deregistered", service_id=service_id)
    
    async def discover_service(self, service_name: str) -> List[ServiceConfig]:
        """Discover services by name"""
        matching_services = []
        
        for service_id, config in self.services.items():
            if config.service_name == service_name:
                matching_services.append(config)
        
        return matching_services
    
    async def get_service_health(self, service_id: str) -> ServiceStatus:
        """Get service health status"""
        if service_id not in self.services:
            return ServiceStatus.UNKNOWN
        
        config = self.services[service_id]
        
        try:
            # Perform health check
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    config.health_check_url,
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        return ServiceStatus.HEALTHY
                    else:
                        return ServiceStatus.DEGRADED
        except Exception:
            return ServiceStatus.UNHEALTHY
    
    async def update_service_metrics(self, service_id: str, metrics_update: Dict[str, Any]):
        """Update service metrics"""
        if service_id in self.service_metrics:
            current_metrics = self.service_metrics[service_id]
            
            for key, value in metrics_update.items():
                if hasattr(current_metrics, key):
                    setattr(current_metrics, key, value)
            
            current_metrics.last_health_check = datetime.utcnow()

class APIGateway:
    """Enterprise API Gateway Implementation"""
    
    def __init__(self, service_registry: ServiceRegistry, load_balancer: LoadBalancer):
        self.service_registry = service_registry
        self.load_balancer = load_balancer
        self.circuit_breaker_manager = CircuitBreakerManager()
        self.rate_limiters: Dict[str, Dict[str, Any]] = {}
        self.logger = structlog.get_logger()
        
        # Prometheus metrics
        self.request_counter = Counter('gateway_requests_total', 'Total gateway requests', ['service', 'method', 'status'])
        self.request_histogram = Histogram('gateway_request_duration_seconds', 'Request duration', ['service'])
        self.active_connections = Gauge('gateway_active_connections', 'Active connections', ['service'])
    
    async def route_request(self, service_name: str, path: str, method: str, headers: Dict[str, str], body: Any = None) -> Dict[str, Any]:
        """Route request to appropriate service instance"""
        start_time = time.time()
        
        try:
            # Discover service
            services = await self.service_registry.discover_service(service_name)
            if not services:
                self.request_counter.labels(service=service_name, method=method, status='404').inc()
                return {
                    'status': 404,
                    'error': f"Service '{service_name}' not found"
                }
            
            # Get service instance via load balancer
            service_config = services[0]  # Use first available service for simplicity
            instance = self.load_balancer.get_next_instance(service_config.service_id)
            
            if not instance:
                self.request_counter.labels(service=service_name, method=method, status='503').inc()
                return {
                    'status': 503,
                    'error': f"No healthy instances available for service '{service_name}'"
                }
            
            # Check rate limiting
            if not await self._check_rate_limit(service_name, headers.get('X-Client-IP', 'unknown')):
                self.request_counter.labels(service=service_name, method=method, status='429').inc()
                return {
                    'status': 429,
                    'error': 'Rate limit exceeded'
                }
            
            # Route request with circuit breaker
            response = await self.circuit_breaker_manager.call_with_circuit_breaker(
                service_config.service_id,
                self._forward_request,
                instance['url'] + path,
                method,
                headers,
                body
            )
            
            # Record metrics
            execution_time = time.time() - start_time
            self.request_histogram.labels(service=service_name).observe(execution_time)
            self.request_counter.labels(service=service_name, method=method, status=str(response.get('status', 200))).inc()
            
            return response
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.request_counter.labels(service=service_name, method=method, status='500').inc()
            self.logger.error("Request routing failed", service=service_name, error=str(e))
            
            return {
                'status': 500,
                'error': f"Internal gateway error: {str(e)}",
                'execution_time': execution_time
            }
    
    async def _forward_request(self, url: str, method: str, headers: Dict[str, str], body: Any = None) -> Dict[str, Any]:
        """Forward request to service instance"""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=body if body else None,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    response_data = await response.text()
                    
                    return {
                        'status': response.status,
                        'headers': dict(response.headers),
                        'data': response_data
                    }
            except asyncio.TimeoutError:
                return {
                    'status': 504,
                    'error': 'Gateway timeout'
                }
            except Exception as e:
                return {
                    'status': 502,
                    'error': f"Bad gateway: {str(e)}"
                }
    
    async def _check_rate_limit(self, service_name: str, client_ip: str) -> bool:
        """Check if request is within rate limits"""
        current_time = time.time()
        window_size = 60  # 1 minute window
        
        key = f"{service_name}:{client_ip}"
        
        if key not in self.rate_limiters:
            self.rate_limiters[key] = {
                'requests': [],
                'limit': 100  # Default limit
            }
        
        rate_limiter = self.rate_limiters[key]
        
        # Remove old requests outside the window
        rate_limiter['requests'] = [
            req_time for req_time in rate_limiter['requests']
            if current_time - req_time < window_size
        ]
        
        # Check if within limit
        if len(rate_limiter['requests']) < rate_limiter['limit']:
            rate_limiter['requests'].append(current_time)
            return True
        
        return False

class EnterpriseArchitectureManager:
    """Central Enterprise Architecture Management System"""
    
    def __init__(self, redis_url: str = None, database_url: str = None):
        self.redis_url = redis_url
        self.database_url = database_url
        
        # Core components
        self.connection_pool = ConnectionPool()
        self.service_registry = ServiceRegistry()
        self.load_balancer = LoadBalancer()
        self.api_gateway = APIGateway(self.service_registry, self.load_balancer)
        
        # System metrics
        self.system_metrics = {
            'total_services': 0,
            'healthy_services': 0,
            'total_requests': 0,
            'failed_requests': 0,
            'average_response_time': 0.0,
            'uptime_start': datetime.utcnow()
        }
        
        # Background tasks
        self.background_tasks: List[asyncio.Task] = []
        
        self.logger = structlog.get_logger()
    
    async def initialize(self):
        """Initialize the architecture manager"""
        try:
            # Initialize Redis connection if URL provided
            if self.redis_url:
                redis_client = await self.connection_pool.get_redis_pool(self.redis_url)
                self.service_registry.redis_client = redis_client
            
            # Initialize database connection if URL provided
            if self.database_url:
                await self.connection_pool.get_db_pool(self.database_url)
            
            # Start background monitoring tasks
            self.background_tasks.append(
                asyncio.create_task(self._health_check_loop())
            )
            self.background_tasks.append(
                asyncio.create_task(self._metrics_collection_loop())
            )
            
            self.logger.info("Enterprise Architecture Manager initialized")
            
        except Exception as e:
            self.logger.error("Failed to initialize Architecture Manager", error=str(e))
            raise
    
    async def register_microservice(self, config: ServiceConfig):
        """Register a microservice with the architecture"""
        await self.service_registry.register_service(config)
        
        # Register instances with load balancer
        for endpoint in config.endpoints:
            instance_info = {
                'url': endpoint,
                'service_id': config.service_id,
                'weight': 1,
                'current_connections': 0
            }
            self.load_balancer.register_service_instance(config.service_id, instance_info)
        
        self.system_metrics['total_services'] += 1
        self.logger.info("Microservice registered", service_id=config.service_id)
    
    async def process_request(self, service_name: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process request through the enterprise architecture"""
        start_time = datetime.utcnow()
        
        try:
            # Extract request details
            path = request_data.get('path', '/')
            method = request_data.get('method', 'GET')
            headers = request_data.get('headers', {})
            body = request_data.get('body')
            
            # Route through API Gateway
            response = await self.api_gateway.route_request(
                service_name, path, method, headers, body
            )
            
            # Update system metrics
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            self.system_metrics['total_requests'] += 1
            
            if response.get('status', 200) >= 400:
                self.system_metrics['failed_requests'] += 1
            
            # Update average response time
            current_avg = self.system_metrics['average_response_time']
            total_requests = self.system_metrics['total_requests']
            self.system_metrics['average_response_time'] = (
                (current_avg * (total_requests - 1) + execution_time) / total_requests
            )
            
            response['execution_time'] = execution_time
            return response
            
        except Exception as e:
            self.system_metrics['failed_requests'] += 1
            self.logger.error("Request processing failed", error=str(e))
            
            return {
                'status': 500,
                'error': f"Architecture processing error: {str(e)}",
                'execution_time': (datetime.utcnow() - start_time).total_seconds()
            }
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        # Count healthy services
        healthy_count = 0
        service_statuses = {}
        
        for service_id in self.service_registry.services.keys():
            status = await self.service_registry.get_service_health(service_id)
            service_statuses[service_id] = status.value
            if status == ServiceStatus.HEALTHY:
                healthy_count += 1
        
        self.system_metrics['healthy_services'] = healthy_count
        
        # Calculate uptime
        uptime_duration = datetime.utcnow() - self.system_metrics['uptime_start']
        uptime_hours = uptime_duration.total_seconds() / 3600
        
        return {
            'system_metrics': self.system_metrics,
            'service_statuses': service_statuses,
            'uptime_hours': uptime_hours,
            'connection_pools': {
                pool_name: count for pool_name, count in self.connection_pool.connection_counts.items()
            },
            'load_balancer_status': {
                'strategy': self.load_balancer.strategy.value,
                'registered_services': len(self.load_balancer.service_instances)
            },
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def scale_service(self, service_id: str, target_instances: int):
        """Scale service instances"""
        if service_id not in self.service_registry.services:
            raise ValueError(f"Service '{service_id}' not found")
        
        config = self.service_registry.services[service_id]
        current_instances = len(self.load_balancer.service_instances.get(service_id, []))
        
        if target_instances > current_instances:
            # Scale up
            for i in range(current_instances, target_instances):
                instance_info = {
                    'url': f"{config.endpoints[0]}_{i}",  # Simplified
                    'service_id': service_id,
                    'weight': 1,
                    'current_connections': 0
                }
                self.load_balancer.register_service_instance(service_id, instance_info)
        
        elif target_instances < current_instances:
            # Scale down
            instances = self.load_balancer.service_instances[service_id]
            self.load_balancer.service_instances[service_id] = instances[:target_instances]
        
        self.logger.info("Service scaled", service_id=service_id, target_instances=target_instances)
    
    async def _health_check_loop(self):
        """Background health check loop"""
        while True:
            try:
                for service_id in self.service_registry.services.keys():
                    status = await self.service_registry.get_service_health(service_id)
                    
                    # Update metrics based on health status
                    metrics_update = {
                        'last_health_check': datetime.utcnow()
                    }
                    
                    if status == ServiceStatus.HEALTHY:
                        metrics_update['uptime_percentage'] = min(100.0, 
                            self.service_registry.service_metrics[service_id].uptime_percentage + 0.1
                        )
                    else:
                        metrics_update['uptime_percentage'] = max(0.0,
                            self.service_registry.service_metrics[service_id].uptime_percentage - 1.0
                        )
                    
                    await self.service_registry.update_service_metrics(service_id, metrics_update)
                
                await asyncio.sleep(30)  # Health check every 30 seconds
                
            except Exception as e:
                self.logger.error("Health check loop error", error=str(e))
                await asyncio.sleep(30)
    
    async def _metrics_collection_loop(self):
        """Background metrics collection loop"""
        while True:
            try:
                # Collect and aggregate metrics from all services
                for service_id, metrics in self.service_registry.service_metrics.items():
                    # Calculate error rate
                    total_requests = metrics.requests_total
                    if total_requests > 0:
                        metrics.error_rate = (metrics.requests_failed / total_requests) * 100
                    
                    # Calculate throughput (requests per minute)
                    # Simplified calculation
                    metrics.throughput = total_requests / max(1, 
                        (datetime.utcnow() - self.system_metrics['uptime_start']).total_seconds() / 60
                    )
                
                await asyncio.sleep(60)  # Collect metrics every minute
                
            except Exception as e:
                self.logger.error("Metrics collection loop error", error=str(e))
                await asyncio.sleep(60)
    
    async def shutdown(self):
        """Gracefully shutdown the architecture manager"""
        self.logger.info("Shutting down Enterprise Architecture Manager")
        
        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()
        
        # Close connection pools
        for pool_name, pool in self.connection_pool.pools.items():
            if hasattr(pool, 'close'):
                await pool.close()
        
        self.logger.info("Enterprise Architecture Manager shutdown complete")

# Factory function
async def create_enterprise_architecture_manager(
    redis_url: Optional[str] = None,
    database_url: Optional[str] = None
) -> EnterpriseArchitectureManager:
    """Factory function to create and initialize Enterprise Architecture Manager"""
    manager = EnterpriseArchitectureManager(redis_url, database_url)
    await manager.initialize()
    return manager

# Export main components
__all__ = [
    'EnterpriseArchitectureManager',
    'ServiceConfig',
    'ServiceStatus',
    'ServiceMetrics',
    'APIGateway',
    'LoadBalancer',
    'ServiceRegistry',
    'CircuitBreakerManager',
    'ConnectionPool',
    'create_enterprise_architecture_manager'
]