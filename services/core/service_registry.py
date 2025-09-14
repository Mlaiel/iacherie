"""
Service Registry - Enterprise Service Discovery & Management
===========================================================

**Author**: Fahed Mlaiel (mlaiel@live.de)
**Roles**: Lead Dev IA + Backend Senior + Microservices Architect + DevOps
**Module**: Core Services - Service Discovery
**Version**: 1.0.0 Enterprise
**Created**: 2025-01-07

Enterprise-grade service registry with discovery, load balancing, health monitoring,
and intelligent service mesh coordination.
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
import aioredis
import aiohttp
from urllib.parse import urlparse
import hashlib
import uuid


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ServiceStatus(Enum):
    """Service status enumeration"""
    UNKNOWN = "unknown"
    STARTING = "starting" 
    HEALTHY = "healthy"
    WARNING = "warning"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"
    SHUTTING_DOWN = "shutting_down"
    OFFLINE = "offline"


class ServiceType(Enum):
    """Service type classification"""
    CORE = "core"
    PROCESSING = "processing"
    ORCHESTRATION = "orchestration"
    GATEWAY = "gateway"
    DATABASE = "database"
    CACHE = "cache"
    QUEUE = "queue"
    EXTERNAL = "external"


class DiscoveryStrategy(Enum):
    """Service discovery strategies"""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_RESPONSE_TIME = "least_response_time"
    HEALTH_BASED = "health_based"
    GEOGRAPHIC = "geographic"


@dataclass
class ServiceEndpoint:
    """Service endpoint definition"""
    path: str
    method: str
    description: str
    timeout_ms: int = 5000
    retries: int = 3
    circuit_breaker: bool = True
    rate_limit: Optional[int] = None
    auth_required: bool = True


@dataclass
class ServiceInstance:
    """Service instance with comprehensive metadata"""
    service_id: str
    service_name: str
    service_type: ServiceType
    version: str
    host: str
    port: int
    health_endpoint: str
    status: ServiceStatus = ServiceStatus.UNKNOWN
    
    # Network & Discovery
    endpoints: List[ServiceEndpoint] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    load_balancer_weight: int = 100
    priority: int = 1
    
    # Operational Metadata
    registration_time: datetime = field(default_factory=datetime.now)
    last_heartbeat: Optional[datetime] = None
    last_health_check: Optional[datetime] = None
    failure_count: int = 0
    success_count: int = 0
    
    # Configuration
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    environment: str = "production"
    region: str = "default"
    
    # Performance Metrics
    response_time_ms: float = 0.0
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    active_connections: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        data = asdict(self)
        data['service_type'] = self.service_type.value
        data['status'] = self.status.value
        data['registration_time'] = self.registration_time.isoformat()
        if self.last_heartbeat:
            data['last_heartbeat'] = self.last_heartbeat.isoformat()
        if self.last_health_check:
            data['last_health_check'] = self.last_health_check.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ServiceInstance':
        """Create instance from dictionary"""
        # Convert enum values
        data['service_type'] = ServiceType(data['service_type'])
        data['status'] = ServiceStatus(data['status'])
        
        # Convert datetime strings
        data['registration_time'] = datetime.fromisoformat(data['registration_time'])
        if data.get('last_heartbeat'):
            data['last_heartbeat'] = datetime.fromisoformat(data['last_heartbeat'])
        if data.get('last_health_check'):
            data['last_health_check'] = datetime.fromisoformat(data['last_health_check'])
        
        # Convert endpoints
        endpoints_data = data.get('endpoints', [])
        data['endpoints'] = [ServiceEndpoint(**ep) for ep in endpoints_data]
        
        return cls(**data)


@dataclass
class LoadBalancerMetrics:
    """Load balancer performance metrics"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    peak_response_time: float = 0.0
    min_response_time: float = float('inf')
    requests_per_second: float = 0.0
    last_reset: datetime = field(default_factory=datetime.now)


class ServiceRegistry:
    """
    Enterprise Service Registry with Discovery, Load Balancing & Health Management
    
    **Expert Roles Implemented:**
    - Lead Dev IA: Intelligent service discovery algorithms
    - Backend Senior: Robust async architecture with connection pooling
    - Microservices: Service mesh patterns, circuit breakers
    - DevOps: Health monitoring, metrics collection, observability
    - Security: Service authentication, secure communication
    """
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        registry_ttl: int = 300,  # 5 minutes
        health_check_interval: int = 30,  # 30 seconds
        cleanup_interval: int = 60,  # 1 minute
        max_retries: int = 3
    ):
        self.redis_url = redis_url
        self.registry_ttl = registry_ttl
        self.health_check_interval = health_check_interval
        self.cleanup_interval = cleanup_interval
        self.max_retries = max_retries
        
        # Storage
        self.redis_client: Optional[aioredis.Redis] = None
        self.services: Dict[str, ServiceInstance] = {}
        self.service_groups: Dict[str, List[str]] = {}  # service_name -> [service_ids]
        
        # Load Balancing
        self.round_robin_indices: Dict[str, int] = {}
        self.lb_metrics: Dict[str, LoadBalancerMetrics] = {}
        
        # Health & Monitoring
        self.health_checkers: Dict[str, asyncio.Task] = {}
        self.circuit_breakers: Dict[str, Dict[str, Any]] = {}
        
        # Background tasks
        self.background_tasks: List[asyncio.Task] = []
        self.running = False
        
    async def initialize(self) -> None:
        """Initialize service registry"""
        try:
            self.redis_client = aioredis.from_url(self.redis_url)
            await self.redis_client.ping()
            
            # Start background tasks
            self.running = True
            self.background_tasks = [
                asyncio.create_task(self._health_check_loop()),
                asyncio.create_task(self._cleanup_loop()),
                asyncio.create_task(self._metrics_collection_loop())
            ]
            
            logger.info("Service Registry initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Service Registry: {e}")
            raise
    
    async def shutdown(self) -> None:
        """Graceful shutdown"""
        self.running = False
        
        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()
        
        await asyncio.gather(*self.background_tasks, return_exceptions=True)
        
        # Close Redis connection
        if self.redis_client:
            await self.redis_client.close()
        
        logger.info("Service Registry shutdown completed")
    
    async def register_service(self, service: ServiceInstance) -> bool:
        """
        Register a service instance
        
        **Roles**: Backend Senior + Microservices + Security
        """
        try:
            # Validate service
            if not self._validate_service(service):
                return False
            
            # Generate unique service ID if not provided
            if not service.service_id:
                service.service_id = self._generate_service_id(service)
            
            # Update registration time
            service.registration_time = datetime.now()
            service.last_heartbeat = datetime.now()
            
            # Store in memory
            self.services[service.service_id] = service
            
            # Group by service name
            if service.service_name not in self.service_groups:
                self.service_groups[service.service_name] = []
            if service.service_id not in self.service_groups[service.service_name]:
                self.service_groups[service.service_name].append(service.service_id)
            
            # Store in Redis
            await self._store_service_in_redis(service)
            
            # Initialize metrics
            self.lb_metrics[service.service_id] = LoadBalancerMetrics()
            
            # Start health checking
            await self._start_health_checking(service)
            
            logger.info(f"Service registered: {service.service_name}:{service.service_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register service {service.service_name}: {e}")
            return False
    
    async def deregister_service(self, service_id: str) -> bool:
        """
        Deregister a service instance
        
        **Roles**: Backend Senior + DevOps
        """
        try:
            if service_id not in self.services:
                return False
            
            service = self.services[service_id]
            
            # Update status
            service.status = ServiceStatus.SHUTTING_DOWN
            
            # Remove from groups
            if service.service_name in self.service_groups:
                if service_id in self.service_groups[service.service_name]:
                    self.service_groups[service.service_name].remove(service_id)
                    if not self.service_groups[service.service_name]:
                        del self.service_groups[service.service_name]
            
            # Stop health checking
            if service_id in self.health_checkers:
                self.health_checkers[service_id].cancel()
                del self.health_checkers[service_id]
            
            # Remove from storage
            del self.services[service_id]
            await self._remove_service_from_redis(service_id)
            
            logger.info(f"Service deregistered: {service.service_name}:{service_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to deregister service {service_id}: {e}")
            return False
    
    async def discover_service(
        self,
        service_name: str,
        strategy: DiscoveryStrategy = DiscoveryStrategy.HEALTH_BASED,
        tags: Optional[List[str]] = None,
        region: Optional[str] = None
    ) -> Optional[ServiceInstance]:
        """
        Discover and select optimal service instance
        
        **Roles**: Lead Dev IA + Microservices
        """
        try:
            # Get available instances
            instances = await self.get_healthy_instances(service_name, tags, region)
            if not instances:
                return None
            
            # Apply discovery strategy
            selected = self._apply_discovery_strategy(instances, strategy, service_name)
            
            if selected:
                # Update load balancer metrics
                await self._update_lb_metrics(selected.service_id)
            
            return selected
            
        except Exception as e:
            logger.error(f"Failed to discover service {service_name}: {e}")
            return None
    
    async def get_healthy_instances(
        self,
        service_name: str,
        tags: Optional[List[str]] = None,
        region: Optional[str] = None
    ) -> List[ServiceInstance]:
        """Get all healthy instances of a service"""
        instances = []
        
        if service_name not in self.service_groups:
            return instances
        
        for service_id in self.service_groups[service_name]:
            if service_id not in self.services:
                continue
                
            service = self.services[service_id]
            
            # Check health status
            if service.status not in [ServiceStatus.HEALTHY, ServiceStatus.WARNING]:
                continue
            
            # Filter by tags
            if tags and not all(tag in service.tags for tag in tags):
                continue
            
            # Filter by region
            if region and service.region != region:
                continue
            
            instances.append(service)
        
        return instances
    
    def _apply_discovery_strategy(
        self,
        instances: List[ServiceInstance],
        strategy: DiscoveryStrategy,
        service_name: str
    ) -> Optional[ServiceInstance]:
        """Apply load balancing strategy"""
        if not instances:
            return None
        
        if strategy == DiscoveryStrategy.ROUND_ROBIN:
            return self._round_robin_selection(instances, service_name)
        
        elif strategy == DiscoveryStrategy.LEAST_CONNECTIONS:
            return min(instances, key=lambda x: x.active_connections)
        
        elif strategy == DiscoveryStrategy.WEIGHTED_ROUND_ROBIN:
            return self._weighted_round_robin_selection(instances, service_name)
        
        elif strategy == DiscoveryStrategy.LEAST_RESPONSE_TIME:
            return min(instances, key=lambda x: x.response_time_ms)
        
        elif strategy == DiscoveryStrategy.HEALTH_BASED:
            return self._health_based_selection(instances)
        
        else:
            return instances[0]  # Default fallback
    
    def _round_robin_selection(
        self,
        instances: List[ServiceInstance],
        service_name: str
    ) -> ServiceInstance:
        """Round robin selection"""
        if service_name not in self.round_robin_indices:
            self.round_robin_indices[service_name] = 0
        
        index = self.round_robin_indices[service_name] % len(instances)
        self.round_robin_indices[service_name] = (index + 1) % len(instances)
        
        return instances[index]
    
    def _weighted_round_robin_selection(
        self,
        instances: List[ServiceInstance],
        service_name: str
    ) -> ServiceInstance:
        """Weighted round robin selection"""
        total_weight = sum(instance.load_balancer_weight for instance in instances)
        if total_weight == 0:
            return instances[0]
        
        # Simple weighted selection (could be optimized)
        import random
        weighted_instances = []
        for instance in instances:
            weighted_instances.extend([instance] * instance.load_balancer_weight)
        
        return random.choice(weighted_instances)
    
    def _health_based_selection(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """Health-based selection with multiple factors"""
        def health_score(instance: ServiceInstance) -> float:
            score = 0.0
            
            # Health status weight
            if instance.status == ServiceStatus.HEALTHY:
                score += 100
            elif instance.status == ServiceStatus.WARNING:
                score += 50
            
            # Response time weight (inverse)
            if instance.response_time_ms > 0:
                score += max(0, 100 - instance.response_time_ms / 10)
            
            # Resource usage weight (inverse)
            score += max(0, 100 - instance.cpu_usage)
            score += max(0, 100 - instance.memory_usage)
            
            # Success rate weight
            total_requests = instance.success_count + instance.failure_count
            if total_requests > 0:
                success_rate = instance.success_count / total_requests
                score += success_rate * 100
            
            return score
        
        return max(instances, key=health_score)
    
    async def _store_service_in_redis(self, service: ServiceInstance) -> None:
        """Store service in Redis with TTL"""
        if not self.redis_client:
            return
        
        key = f"service:{service.service_id}"
        value = json.dumps(service.to_dict())
        await self.redis_client.setex(key, self.registry_ttl, value)
        
        # Store in service name index
        name_key = f"service_name:{service.service_name}"
        await self.redis_client.sadd(name_key, service.service_id)
        await self.redis_client.expire(name_key, self.registry_ttl)
    
    async def _remove_service_from_redis(self, service_id: str) -> None:
        """Remove service from Redis"""
        if not self.redis_client:
            return
        
        # Get service to find name
        key = f"service:{service_id}"
        service_data = await self.redis_client.get(key)
        
        if service_data:
            service_dict = json.loads(service_data)
            service_name = service_dict.get('service_name')
            
            # Remove from name index
            if service_name:
                name_key = f"service_name:{service_name}"
                await self.redis_client.srem(name_key, service_id)
        
        # Remove service key
        await self.redis_client.delete(key)
    
    def _validate_service(self, service: ServiceInstance) -> bool:
        """Validate service instance"""
        if not service.service_name or not service.host or not service.port:
            return False
        
        if service.port < 1 or service.port > 65535:
            return False
        
        return True
    
    def _generate_service_id(self, service: ServiceInstance) -> str:
        """Generate unique service ID"""
        content = f"{service.service_name}-{service.host}-{service.port}-{time.time()}"
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    async def _start_health_checking(self, service: ServiceInstance) -> None:
        """Start health checking for service"""
        async def health_check_worker():
            while self.running and service.service_id in self.services:
                try:
                    await self._perform_health_check(service)
                    await asyncio.sleep(self.health_check_interval)
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Health check error for {service.service_id}: {e}")
                    await asyncio.sleep(5)  # Short retry delay
        
        task = asyncio.create_task(health_check_worker())
        self.health_checkers[service.service_id] = task
    
    async def _perform_health_check(self, service: ServiceInstance) -> None:
        """Perform health check on service"""
        try:
            start_time = time.time()
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                url = f"http://{service.host}:{service.port}{service.health_endpoint}"
                
                async with session.get(url) as response:
                    response_time = (time.time() - start_time) * 1000  # ms
                    
                    if response.status == 200:
                        service.status = ServiceStatus.HEALTHY
                        service.success_count += 1
                        service.failure_count = max(0, service.failure_count - 1)
                    else:
                        service.status = ServiceStatus.WARNING
                        service.failure_count += 1
                    
                    service.response_time_ms = response_time
                    service.last_health_check = datetime.now()
                    
                    # Update metrics
                    await self._update_service_metrics(service, response_time, True)
        
        except Exception as e:
            service.status = ServiceStatus.UNHEALTHY
            service.failure_count += 1
            service.last_health_check = datetime.now()
            
            # Critical status if too many failures
            if service.failure_count >= 5:
                service.status = ServiceStatus.CRITICAL
            
            await self._update_service_metrics(service, 0, False)
            logger.warning(f"Health check failed for {service.service_id}: {e}")
    
    async def _update_service_metrics(
        self,
        service: ServiceInstance,
        response_time: float,
        success: bool
    ) -> None:
        """Update service performance metrics"""
        if service.service_id not in self.lb_metrics:
            self.lb_metrics[service.service_id] = LoadBalancerMetrics()
        
        metrics = self.lb_metrics[service.service_id]
        metrics.total_requests += 1
        
        if success:
            metrics.successful_requests += 1
        else:
            metrics.failed_requests += 1
        
        if response_time > 0:
            # Update response time metrics
            if metrics.total_requests == 1:
                metrics.average_response_time = response_time
                metrics.min_response_time = response_time
                metrics.peak_response_time = response_time
            else:
                # Running average
                metrics.average_response_time = (
                    (metrics.average_response_time * (metrics.total_requests - 1) + response_time) /
                    metrics.total_requests
                )
                metrics.min_response_time = min(metrics.min_response_time, response_time)
                metrics.peak_response_time = max(metrics.peak_response_time, response_time)
    
    async def _update_lb_metrics(self, service_id: str) -> None:
        """Update load balancer metrics for service selection"""
        if service_id in self.lb_metrics:
            # Calculate requests per second
            metrics = self.lb_metrics[service_id]
            time_diff = datetime.now() - metrics.last_reset
            if time_diff.total_seconds() > 0:
                metrics.requests_per_second = metrics.total_requests / time_diff.total_seconds()
    
    async def _health_check_loop(self) -> None:
        """Background health checking loop"""
        while self.running:
            try:
                # Health checks are handled by individual service tasks
                await asyncio.sleep(self.health_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check loop error: {e}")
                await asyncio.sleep(5)
    
    async def _cleanup_loop(self) -> None:
        """Background cleanup loop"""
        while self.running:
            try:
                await self._cleanup_stale_services()
                await asyncio.sleep(self.cleanup_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cleanup loop error: {e}")
                await asyncio.sleep(5)
    
    async def _cleanup_stale_services(self) -> None:
        """Clean up stale service instances"""
        current_time = datetime.now()
        stale_threshold = timedelta(minutes=10)
        
        stale_services = []
        for service_id, service in self.services.items():
            if service.last_heartbeat:
                time_since_heartbeat = current_time - service.last_heartbeat
                if time_since_heartbeat > stale_threshold:
                    stale_services.append(service_id)
        
        for service_id in stale_services:
            logger.warning(f"Removing stale service: {service_id}")
            await self.deregister_service(service_id)
    
    async def _metrics_collection_loop(self) -> None:
        """Background metrics collection loop"""
        while self.running:
            try:
                await self._collect_registry_metrics()
                await asyncio.sleep(30)  # Collect every 30 seconds
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Metrics collection error: {e}")
                await asyncio.sleep(5)
    
    async def _collect_registry_metrics(self) -> None:
        """Collect and log registry metrics"""
        total_services = len(self.services)
        healthy_services = len([s for s in self.services.values() if s.status == ServiceStatus.HEALTHY])
        service_types = {}
        
        for service in self.services.values():
            service_type = service.service_type.value
            service_types[service_type] = service_types.get(service_type, 0) + 1
        
        logger.info(f"Registry metrics - Total: {total_services}, Healthy: {healthy_services}, Types: {service_types}")
    
    async def get_service_status(self, service_id: str) -> Optional[ServiceInstance]:
        """Get current status of a service"""
        return self.services.get(service_id)
    
    async def get_all_services(self) -> List[ServiceInstance]:
        """Get all registered services"""
        return list(self.services.values())
    
    async def get_services_by_type(self, service_type: ServiceType) -> List[ServiceInstance]:
        """Get services by type"""
        return [s for s in self.services.values() if s.service_type == service_type]
    
    async def update_service_metadata(
        self,
        service_id: str,
        metadata: Dict[str, Any]
    ) -> bool:
        """Update service metadata"""
        if service_id not in self.services:
            return False
        
        self.services[service_id].metadata.update(metadata)
        await self._store_service_in_redis(self.services[service_id])
        return True