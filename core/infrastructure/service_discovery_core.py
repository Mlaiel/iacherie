"""
Ainflue Core Infrastructure - Service Discovery Core
====================================================

Enterprise-grade service discovery and registry system with health checking,
load balancing integration, and multi-environment support. Provides service
mesh capabilities for distributed Ainflue architecture.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import json
import logging
import time
import uuid
from typing import Dict, List, Optional, Any, Union, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import socket
import threading
from collections import defaultdict

# Third-party imports (with fallbacks)
try:
    import consul
    CONSUL_AVAILABLE = True
except ImportError:
    CONSUL_AVAILABLE = False

try:
    import etcd3
    ETCD_AVAILABLE = True
except ImportError:
    ETCD_AVAILABLE = False

logger = logging.getLogger(__name__)

class ServiceStatus(str, Enum):
    """Service health status"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"
    STARTING = "starting"
    STOPPING = "stopping"
    MAINTENANCE = "maintenance"

class DiscoveryBackend(str, Enum):
    """Service discovery backends"""
    MEMORY = "memory"
    CONSUL = "consul"
    ETCD = "etcd"
    KUBERNETES = "kubernetes"
    DNS = "dns"

@dataclass
class ServiceEndpoint:
    """Service endpoint information"""
    host: str
    port: int
    scheme: str = "http"
    path: str = "/"
    weight: int = 100
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def url(self) -> str:
        """Get full URL for endpoint"""
        return f"{self.scheme}://{self.host}:{self.port}{self.path}"

    def __hash__(self):
        return hash((self.host, self.port, self.scheme, self.path))

@dataclass
class ServiceRegistration:
    """Service registration information"""
    service_id: str
    service_name: str
    version: str
    endpoints: List[ServiceEndpoint]
    status: ServiceStatus = ServiceStatus.STARTING
    tags: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)
    health_check_url: Optional[str] = None
    health_check_interval: int = 30
    last_heartbeat: Optional[datetime] = None
    registration_time: datetime = field(default_factory=datetime.utcnow)
    ttl_seconds: int = 300

@dataclass
class ServiceQuery:
    """Service discovery query"""
    service_name: str
    version: Optional[str] = None
    tags: Optional[Set[str]] = None
    healthy_only: bool = True
    max_results: Optional[int] = None

@dataclass
class DiscoveryMetrics:
    """Service discovery metrics"""
    total_services: int = 0
    healthy_services: int = 0
    unhealthy_services: int = 0
    registrations: int = 0
    deregistrations: int = 0
    queries: int = 0
    health_checks: int = 0
    failed_health_checks: int = 0

class ServiceWatcher:
    """Service change watcher"""
    
    def __init__(self, service_name: str, callback: Callable[[List[ServiceRegistration]], None]):
        self.service_name = service_name
        self.callback = callback
        self.last_services: List[ServiceRegistration] = []

    async def notify(self, services: List[ServiceRegistration]):
        """Notify of service changes"""
        if services != self.last_services:
            try:
                await asyncio.create_task(self._run_callback(services))
                self.last_services = services.copy()
            except Exception as e:
                logger.error(f"Service watcher callback error: {str(e)}")

    async def _run_callback(self, services: List[ServiceRegistration]):
        """Run callback (handle both sync and async)"""
        if asyncio.iscoroutinefunction(self.callback):
            await self.callback(services)
        else:
            self.callback(services)

class ServiceDiscoveryCore:
    """Enterprise service discovery system"""
    
    def __init__(self, level: str = "enterprise", backend: DiscoveryBackend = DiscoveryBackend.MEMORY):
        """Initialize service discovery core"""
        self.level = level
        self.backend = backend
        self.services: Dict[str, ServiceRegistration] = {}
        self.service_name_index: Dict[str, List[str]] = defaultdict(list)
        self.watchers: List[ServiceWatcher] = []
        self.metrics = DiscoveryMetrics()
        
        # Health checking
        self.health_check_enabled = True
        self.health_check_interval = 30
        self._health_check_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
        
        # External backends
        self.consul_client = None
        self.etcd_client = None
        
        # Thread safety
        self._lock = asyncio.Lock()
        
        # Service discovery configuration
        self.config = {
            "consul_host": "localhost",
            "consul_port": 8500,
            "etcd_host": "localhost", 
            "etcd_port": 2379,
            "default_ttl": 300,
            "health_check_timeout": 10,
            "max_retries": 3
        }
        
        # Initialize backend
        self._initialize_backend()
        
        # Start health checking
        if self.health_check_enabled:
            self._start_health_checking()
        
        logger.info(f"🔍 Service Discovery Core initialized - Backend: {backend.value}")

    def _initialize_backend(self):
        """Initialize discovery backend"""
        try:
            if self.backend == DiscoveryBackend.CONSUL and CONSUL_AVAILABLE:
                self._initialize_consul()
            elif self.backend == DiscoveryBackend.ETCD and ETCD_AVAILABLE:
                self._initialize_etcd()
            elif self.backend != DiscoveryBackend.MEMORY:
                logger.warning(f"Backend {self.backend.value} not available, falling back to memory")
                self.backend = DiscoveryBackend.MEMORY
            
        except Exception as e:
            logger.error(f"Failed to initialize backend {self.backend.value}: {str(e)}")
            self.backend = DiscoveryBackend.MEMORY

    def _initialize_consul(self):
        """Initialize Consul backend"""
        if not CONSUL_AVAILABLE:
            raise ImportError("Consul library not available")
        
        self.consul_client = consul.Consul(
            host=self.config["consul_host"],
            port=self.config["consul_port"]
        )
        logger.info("✅ Consul backend initialized")

    def _initialize_etcd(self):
        """Initialize etcd backend"""
        if not ETCD_AVAILABLE:
            raise ImportError("etcd3 library not available")
        
        self.etcd_client = etcd3.client(
            host=self.config["etcd_host"],
            port=self.config["etcd_port"]
        )
        logger.info("✅ etcd backend initialized")

    def _start_health_checking(self):
        """Start health check background task"""
        if self._health_check_task and not self._health_check_task.done():
            return
        
        self._health_check_task = asyncio.create_task(self._health_check_loop())
        logger.info("❤️ Health checking started")

    async def _health_check_loop(self):
        """Health check background loop"""
        while not self._shutdown_event.is_set():
            try:
                await self._perform_health_checks()
                await asyncio.sleep(self.health_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check loop error: {str(e)}")
                await asyncio.sleep(60)  # Wait longer on error

    async def _perform_health_checks(self):
        """Perform health checks on all services"""
        async with self._lock:
            for service_id, service in self.services.items():
                if service.health_check_url:
                    await self._check_service_health(service)

    async def _check_service_health(self, service: ServiceRegistration):
        """Check health of a specific service"""
        try:
            import aiohttp
            
            timeout = aiohttp.ClientTimeout(total=self.config["health_check_timeout"])
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(service.health_check_url) as response:
                    if response.status == 200:
                        await self._update_service_status(service.service_id, ServiceStatus.HEALTHY)
                    else:
                        await self._update_service_status(service.service_id, ServiceStatus.UNHEALTHY)
            
            self.metrics.health_checks += 1
            
        except ImportError:
            # Fallback health check without aiohttp
            await self._simple_health_check(service)
        except Exception as e:
            logger.warning(f"Health check failed for {service.service_name}: {str(e)}")
            await self._update_service_status(service.service_id, ServiceStatus.UNHEALTHY)
            self.metrics.failed_health_checks += 1

    async def _simple_health_check(self, service: ServiceRegistration):
        """Simple TCP health check without aiohttp"""
        try:
            for endpoint in service.endpoints:
                # Try to connect to each endpoint
                future = asyncio.open_connection(endpoint.host, endpoint.port)
                reader, writer = await asyncio.wait_for(future, timeout=5)
                writer.close()
                await writer.wait_closed()
            
            await self._update_service_status(service.service_id, ServiceStatus.HEALTHY)
            
        except Exception:
            await self._update_service_status(service.service_id, ServiceStatus.UNHEALTHY)

    async def register_service(
        self,
        service_name: str,
        endpoints: List[ServiceEndpoint],
        version: str = "1.0.0",
        tags: Optional[Set[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        health_check_url: Optional[str] = None,
        ttl_seconds: int = 300
    ) -> str:
        """Register a service"""
        
        service_id = f"{service_name}-{uuid.uuid4().hex[:8]}"
        
        service = ServiceRegistration(
            service_id=service_id,
            service_name=service_name,
            version=version,
            endpoints=endpoints,
            tags=tags or set(),
            metadata=metadata or {},
            health_check_url=health_check_url,
            ttl_seconds=ttl_seconds
        )
        
        async with self._lock:
            # Store in memory
            self.services[service_id] = service
            self.service_name_index[service_name].append(service_id)
            
            # Register with external backend
            await self._register_with_backend(service)
            
            # Update metrics
            self.metrics.registrations += 1
            self.metrics.total_services += 1
        
        # Notify watchers
        await self._notify_watchers(service_name)
        
        logger.info(f"📝 Registered service {service_name} with ID {service_id}")
        return service_id

    async def _register_with_backend(self, service: ServiceRegistration):
        """Register service with external backend"""
        try:
            if self.backend == DiscoveryBackend.CONSUL and self.consul_client:
                await self._register_with_consul(service)
            elif self.backend == DiscoveryBackend.ETCD and self.etcd_client:
                await self._register_with_etcd(service)
                
        except Exception as e:
            logger.error(f"Failed to register with backend: {str(e)}")

    async def _register_with_consul(self, service: ServiceRegistration):
        """Register with Consul"""
        if not self.consul_client:
            return
        
        # Convert endpoints to Consul format
        for i, endpoint in enumerate(service.endpoints):
            consul_service_id = f"{service.service_id}-{i}"
            
            check = None
            if service.health_check_url:
                check = consul.Check.http(
                    service.health_check_url,
                    interval=f"{service.health_check_interval}s"
                )
            
            self.consul_client.agent.service.register(
                name=service.service_name,
                service_id=consul_service_id,
                address=endpoint.host,
                port=endpoint.port,
                tags=list(service.tags),
                check=check,
                meta=service.metadata
            )

    async def _register_with_etcd(self, service: ServiceRegistration):
        """Register with etcd"""
        if not self.etcd_client:
            return
        
        key = f"/services/{service.service_name}/{service.service_id}"
        value = json.dumps({
            "service_id": service.service_id,
            "service_name": service.service_name,
            "version": service.version,
            "endpoints": [
                {
                    "host": ep.host,
                    "port": ep.port,
                    "scheme": ep.scheme,
                    "path": ep.path,
                    "weight": ep.weight
                } for ep in service.endpoints
            ],
            "tags": list(service.tags),
            "metadata": service.metadata,
            "registration_time": service.registration_time.isoformat()
        })
        
        # Set with TTL
        self.etcd_client.put(key, value, lease=self.etcd_client.lease(service.ttl_seconds))

    async def deregister_service(self, service_id: str):
        """Deregister a service"""
        
        async with self._lock:
            service = self.services.get(service_id)
            if not service:
                logger.warning(f"Service {service_id} not found for deregistration")
                return
            
            # Remove from memory
            del self.services[service_id]
            self.service_name_index[service.service_name].remove(service_id)
            
            # Deregister from external backend
            await self._deregister_with_backend(service)
            
            # Update metrics
            self.metrics.deregistrations += 1
            self.metrics.total_services -= 1
        
        # Notify watchers
        await self._notify_watchers(service.service_name)
        
        logger.info(f"🗑️ Deregistered service {service.service_name} with ID {service_id}")

    async def _deregister_with_backend(self, service: ServiceRegistration):
        """Deregister service from external backend"""
        try:
            if self.backend == DiscoveryBackend.CONSUL and self.consul_client:
                # Deregister all endpoint instances
                for i in range(len(service.endpoints)):
                    consul_service_id = f"{service.service_id}-{i}"
                    self.consul_client.agent.service.deregister(consul_service_id)
                    
            elif self.backend == DiscoveryBackend.ETCD and self.etcd_client:
                key = f"/services/{service.service_name}/{service.service_id}"
                self.etcd_client.delete(key)
                
        except Exception as e:
            logger.error(f"Failed to deregister from backend: {str(e)}")

    async def discover_services(self, query: ServiceQuery) -> List[ServiceRegistration]:
        """Discover services matching query"""
        
        self.metrics.queries += 1
        
        async with self._lock:
            # Get services by name
            service_ids = self.service_name_index.get(query.service_name, [])
            services = [self.services[sid] for sid in service_ids if sid in self.services]
            
            # Apply filters
            filtered_services = []
            for service in services:
                # Version filter
                if query.version and service.version != query.version:
                    continue
                
                # Tags filter
                if query.tags and not query.tags.issubset(service.tags):
                    continue
                
                # Health filter
                if query.healthy_only and service.status != ServiceStatus.HEALTHY:
                    continue
                
                filtered_services.append(service)
            
            # Limit results
            if query.max_results:
                filtered_services = filtered_services[:query.max_results]
            
            return filtered_services

    async def get_service_endpoints(self, service_name: str, healthy_only: bool = True) -> List[ServiceEndpoint]:
        """Get all endpoints for a service"""
        
        query = ServiceQuery(service_name=service_name, healthy_only=healthy_only)
        services = await self.discover_services(query)
        
        endpoints = []
        for service in services:
            endpoints.extend(service.endpoints)
        
        return endpoints

    async def _update_service_status(self, service_id: str, status: ServiceStatus):
        """Update service status"""
        async with self._lock:
            if service_id in self.services:
                old_status = self.services[service_id].status
                self.services[service_id].status = status
                self.services[service_id].last_heartbeat = datetime.utcnow()
                
                # Update metrics
                if old_status != status:
                    if status == ServiceStatus.HEALTHY:
                        self.metrics.healthy_services += 1
                        if old_status == ServiceStatus.UNHEALTHY:
                            self.metrics.unhealthy_services -= 1
                    elif status == ServiceStatus.UNHEALTHY:
                        self.metrics.unhealthy_services += 1
                        if old_status == ServiceStatus.HEALTHY:
                            self.metrics.healthy_services -= 1

    async def heartbeat(self, service_id: str):
        """Send heartbeat for service"""
        async with self._lock:
            if service_id in self.services:
                self.services[service_id].last_heartbeat = datetime.utcnow()
                logger.debug(f"💓 Heartbeat received for {service_id}")

    def add_watcher(self, service_name: str, callback: Callable[[List[ServiceRegistration]], None]) -> ServiceWatcher:
        """Add service change watcher"""
        watcher = ServiceWatcher(service_name, callback)
        self.watchers.append(watcher)
        logger.debug(f"👁️ Added watcher for {service_name}")
        return watcher

    def remove_watcher(self, watcher: ServiceWatcher):
        """Remove service watcher"""
        if watcher in self.watchers:
            self.watchers.remove(watcher)
            logger.debug(f"👁️ Removed watcher for {watcher.service_name}")

    async def _notify_watchers(self, service_name: str):
        """Notify watchers of service changes"""
        query = ServiceQuery(service_name=service_name, healthy_only=False)
        services = await self.discover_services(query)
        
        for watcher in self.watchers:
            if watcher.service_name == service_name:
                await watcher.notify(services)

    async def cleanup_expired_services(self):
        """Clean up expired services"""
        current_time = datetime.utcnow()
        expired_services = []
        
        async with self._lock:
            for service_id, service in self.services.items():
                if service.last_heartbeat:
                    expiry_time = service.last_heartbeat + timedelta(seconds=service.ttl_seconds)
                    if current_time > expiry_time:
                        expired_services.append(service_id)
                else:
                    # No heartbeat received, check registration time
                    expiry_time = service.registration_time + timedelta(seconds=service.ttl_seconds)
                    if current_time > expiry_time:
                        expired_services.append(service_id)
        
        # Deregister expired services
        for service_id in expired_services:
            await self.deregister_service(service_id)
            logger.info(f"🧹 Cleaned up expired service {service_id}")

    def get_service_by_id(self, service_id: str) -> Optional[ServiceRegistration]:
        """Get service by ID"""
        return self.services.get(service_id)

    def get_all_services(self) -> List[ServiceRegistration]:
        """Get all registered services"""
        return list(self.services.values())

    def get_service_names(self) -> List[str]:
        """Get list of all service names"""
        return list(self.service_name_index.keys())

    def get_metrics(self) -> DiscoveryMetrics:
        """Get discovery metrics"""
        # Update real-time metrics
        self.metrics.total_services = len(self.services)
        self.metrics.healthy_services = len([s for s in self.services.values() if s.status == ServiceStatus.HEALTHY])
        self.metrics.unhealthy_services = len([s for s in self.services.values() if s.status == ServiceStatus.UNHEALTHY])
        
        return self.metrics

    async def health_check(self) -> bool:
        """Health check for service discovery system"""
        try:
            # Test basic operations
            test_endpoints = [ServiceEndpoint(host="test", port=8080)]
            service_id = await self.register_service("health-test", test_endpoints)
            
            # Test discovery
            query = ServiceQuery(service_name="health-test")
            services = await self.discover_services(query)
            
            # Cleanup
            await self.deregister_service(service_id)
            
            return len(services) == 1
            
        except Exception as e:
            logger.error(f"Service discovery health check failed: {str(e)}")
            return False

    async def shutdown(self):
        """Shutdown service discovery"""
        logger.info("🛑 Shutting down service discovery")
        
        # Signal shutdown
        self._shutdown_event.set()
        
        # Cancel health check task
        if self._health_check_task and not self._health_check_task.done():
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
        
        # Deregister all services
        service_ids = list(self.services.keys())
        for service_id in service_ids:
            await self.deregister_service(service_id)

# Module exports
__all__ = [
    "ServiceDiscoveryCore", "ServiceRegistration", "ServiceEndpoint", 
    "ServiceQuery", "ServiceWatcher", "ServiceStatus", "DiscoveryBackend",
    "DiscoveryMetrics"
]

logger.info("🔍 Service Discovery Core module loaded")