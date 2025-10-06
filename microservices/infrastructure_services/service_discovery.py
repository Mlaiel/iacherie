"""
🔍 Service Discovery Infrastructure
Microservice discovery and registry management

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import asyncio
import json
import logging
import uuid
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class ServiceStatus(str, Enum):
    """Service status enumeration"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    STARTING = "starting"
    STOPPING = "stopping"
    UNKNOWN = "unknown"


class ServiceType(str, Enum):
    """Service type enumeration"""
    WEB = "web"
    API = "api"
    WORKER = "worker"
    DATABASE = "database"
    CACHE = "cache"
    QUEUE = "queue"
    STORAGE = "storage"
    AI_SERVICE = "ai_service"
    CONTENT_SERVICE = "content_service"
    ANALYTICS = "analytics"


@dataclass
class ServiceEndpoint:
    """Service endpoint definition"""
    protocol: str = "http"
    host: str = "localhost"
    port: int = 8000
    path: str = "/"
    health_check_path: str = "/health"
    
    def get_url(self) -> str:
        """Get complete service URL"""
        return f"{self.protocol}://{self.host}:{self.port}{self.path}"
    
    def get_health_url(self) -> str:
        """Get health check URL"""
        return f"{self.protocol}://{self.host}:{self.port}{self.health_check_path}"


@dataclass
class ServiceInfo:
    """Service information structure"""
    service_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    version: str = "1.0.0"
    service_type: ServiceType = ServiceType.API
    endpoint: ServiceEndpoint = field(default_factory=ServiceEndpoint)
    status: ServiceStatus = ServiceStatus.UNKNOWN
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: Set[str] = field(default_factory=set)
    registered_at: datetime = field(default_factory=datetime.utcnow)
    last_heartbeat: datetime = field(default_factory=datetime.utcnow)
    dependencies: List[str] = field(default_factory=list)
    health_check_interval: int = 30  # seconds
    
    def is_healthy(self, timeout_seconds: int = 90) -> bool:
        """Check if service is considered healthy"""
        if self.status != ServiceStatus.HEALTHY:
            return False
        
        time_since_heartbeat = (datetime.utcnow() - self.last_heartbeat).total_seconds()
        return time_since_heartbeat < timeout_seconds


class ServiceRegistry(ABC):
    """Abstract base class for service registries"""
    
    @abstractmethod
    async def register_service(self, service: ServiceInfo) -> bool:
        """Register a new service"""
        pass
    
    @abstractmethod
    async def deregister_service(self, service_id: str) -> bool:
        """Deregister a service"""
        pass
    
    @abstractmethod
    async def get_service(self, service_id: str) -> Optional[ServiceInfo]:
        """Get service by ID"""
        pass
    
    @abstractmethod
    async def get_services_by_name(self, name: str) -> List[ServiceInfo]:
        """Get services by name"""
        pass
    
    @abstractmethod
    async def get_services_by_type(self, service_type: ServiceType) -> List[ServiceInfo]:
        """Get services by type"""
        pass
    
    @abstractmethod
    async def update_service_status(self, service_id: str, status: ServiceStatus) -> bool:
        """Update service status"""
        pass
    
    @abstractmethod
    async def heartbeat(self, service_id: str) -> bool:
        """Send service heartbeat"""
        pass


class InMemoryServiceRegistry(ServiceRegistry):
    """In-memory implementation of service registry"""
    
    def __init__(self):
        self.services: Dict[str, ServiceInfo] = {}
        self.name_index: Dict[str, Set[str]] = {}
        self.type_index: Dict[ServiceType, Set[str]] = {}
        self.logger = logging.getLogger(f"{__name__}.InMemoryServiceRegistry")
    
    async def register_service(self, service: ServiceInfo) -> bool:
        """Register a new service"""
        try:
            service_id = service.service_id
            
            # Store service
            self.services[service_id] = service
            
            # Update indexes
            if service.name not in self.name_index:
                self.name_index[service.name] = set()
            self.name_index[service.name].add(service_id)
            
            if service.service_type not in self.type_index:
                self.type_index[service.service_type] = set()
            self.type_index[service.service_type].add(service_id)
            
            self.logger.info(f"Registered service {service.name} ({service_id})")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register service {service.name}: {str(e)}")
            return False
    
    async def deregister_service(self, service_id: str) -> bool:
        """Deregister a service"""
        try:
            if service_id not in self.services:
                return False
            
            service = self.services[service_id]
            
            # Remove from indexes
            if service.name in self.name_index:
                self.name_index[service.name].discard(service_id)
                if not self.name_index[service.name]:
                    del self.name_index[service.name]
            
            if service.service_type in self.type_index:
                self.type_index[service.service_type].discard(service_id)
                if not self.type_index[service.service_type]:
                    del self.type_index[service.service_type]
            
            # Remove service
            del self.services[service_id]
            
            self.logger.info(f"Deregistered service {service.name} ({service_id})")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to deregister service {service_id}: {str(e)}")
            return False
    
    async def get_service(self, service_id: str) -> Optional[ServiceInfo]:
        """Get service by ID"""
        return self.services.get(service_id)
    
    async def get_services_by_name(self, name: str) -> List[ServiceInfo]:
        """Get services by name"""
        service_ids = self.name_index.get(name, set())
        return [self.services[sid] for sid in service_ids if sid in self.services]
    
    async def get_services_by_type(self, service_type: ServiceType) -> List[ServiceInfo]:
        """Get services by type"""
        service_ids = self.type_index.get(service_type, set())
        return [self.services[sid] for sid in service_ids if sid in self.services]
    
    async def update_service_status(self, service_id: str, status: ServiceStatus) -> bool:
        """Update service status"""
        if service_id in self.services:
            self.services[service_id].status = status
            self.services[service_id].last_heartbeat = datetime.utcnow()
            return True
        return False
    
    async def heartbeat(self, service_id: str) -> bool:
        """Send service heartbeat"""
        if service_id in self.services:
            self.services[service_id].last_heartbeat = datetime.utcnow()
            return True
        return False
    
    async def get_all_services(self) -> List[ServiceInfo]:
        """Get all registered services"""
        return list(self.services.values())
    
    async def cleanup_stale_services(self, timeout_seconds: int = 120):
        """Remove services that haven't sent heartbeat"""
        current_time = datetime.utcnow()
        stale_services = []
        
        for service_id, service in self.services.items():
            time_since_heartbeat = (current_time - service.last_heartbeat).total_seconds()
            if time_since_heartbeat > timeout_seconds:
                stale_services.append(service_id)
        
        for service_id in stale_services:
            await self.deregister_service(service_id)
            self.logger.warning(f"Removed stale service: {service_id}")


class ServiceDiscovery:
    """Main service discovery coordinator"""
    
    def __init__(self, registry: Optional[ServiceRegistry] = None):
        self.registry = registry or InMemoryServiceRegistry()
        self.local_services: Dict[str, ServiceInfo] = {}
        self.health_check_tasks: Dict[str, asyncio.Task] = {}
        self.cleanup_task: Optional[asyncio.Task] = None
        self.logger = logging.getLogger(f"{__name__}.ServiceDiscovery")
    
    async def ensure_initialized(self):
        """Ensure async components are initialized"""
        if self.cleanup_task is None:
            self.cleanup_task = asyncio.create_task(self._periodic_cleanup())
    
    async def register_local_service(
        self, 
        name: str,
        endpoint: ServiceEndpoint,
        service_type: ServiceType = ServiceType.API,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[Set[str]] = None
    ) -> str:
        """Register a local service"""
        
        service = ServiceInfo(
            name=name,
            service_type=service_type,
            endpoint=endpoint,
            status=ServiceStatus.STARTING,
            metadata=metadata or {},
            tags=tags or set()
        )
        
        # Register with registry
        success = await self.registry.register_service(service)
        if success:
            self.local_services[service.service_id] = service
            
            # Start health checking
            self.health_check_tasks[service.service_id] = asyncio.create_task(
                self._health_check_loop(service)
            )
            
            self.logger.info(f"Registered local service {name} with ID {service.service_id}")
            return service.service_id
        else:
            raise RuntimeError(f"Failed to register service {name}")
    
    async def deregister_local_service(self, service_id: str) -> bool:
        """Deregister a local service"""
        
        if service_id not in self.local_services:
            return False
        
        # Stop health checking
        if service_id in self.health_check_tasks:
            self.health_check_tasks[service_id].cancel()
            del self.health_check_tasks[service_id]
        
        # Update status to stopping
        await self.registry.update_service_status(service_id, ServiceStatus.STOPPING)
        
        # Deregister from registry
        success = await self.registry.deregister_service(service_id)
        if success:
            del self.local_services[service_id]
            self.logger.info(f"Deregistered local service {service_id}")
        
        return success
    
    async def discover_services(
        self, 
        name: Optional[str] = None,
        service_type: Optional[ServiceType] = None,
        healthy_only: bool = True
    ) -> List[ServiceInfo]:
        """Discover services by name or type"""
        
        if name:
            services = await self.registry.get_services_by_name(name)
        elif service_type:
            services = await self.registry.get_services_by_type(service_type)
        else:
            # Get all services if no filter specified
            if hasattr(self.registry, 'get_all_services'):
                services = await self.registry.get_all_services()
            else:
                services = []
        
        # Filter healthy services if requested
        if healthy_only:
            services = [s for s in services if s.is_healthy()]
        
        return services
    
    async def get_service_endpoint(self, name: str) -> Optional[ServiceEndpoint]:
        """Get endpoint for a service by name (load balanced)"""
        
        services = await self.discover_services(name=name, healthy_only=True)
        if not services:
            return None
        
        # Simple round-robin load balancing
        # In production, this could be more sophisticated
        import random
        service = random.choice(services)
        return service.endpoint
    
    async def _health_check_loop(self, service: ServiceInfo):
        """Background health checking for a service"""
        
        while service.service_id in self.local_services:
            try:
                # Perform health check
                is_healthy = await self._perform_health_check(service)
                
                new_status = ServiceStatus.HEALTHY if is_healthy else ServiceStatus.UNHEALTHY
                
                # Update status if changed
                if service.status != new_status:
                    await self.registry.update_service_status(service.service_id, new_status)
                    service.status = new_status
                    self.logger.info(f"Service {service.name} status changed to {new_status}")
                
                # Send heartbeat
                await self.registry.heartbeat(service.service_id)
                
                # Wait for next check
                await asyncio.sleep(service.health_check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Health check failed for {service.name}: {str(e)}")
                await self.registry.update_service_status(service.service_id, ServiceStatus.UNHEALTHY)
                await asyncio.sleep(10)  # Wait before retrying
    
    async def _perform_health_check(self, service: ServiceInfo) -> bool:
        """Perform actual health check on service"""
        
        try:
            import aiohttp
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                health_url = service.endpoint.get_health_url()
                async with session.get(health_url) as response:
                    return response.status == 200
                    
        except Exception:
            # If aiohttp not available or request fails, assume unhealthy
            return False
    
    async def _periodic_cleanup(self):
        """Periodically clean up stale services"""
        
        while True:
            try:
                if hasattr(self.registry, 'cleanup_stale_services'):
                    await self.registry.cleanup_stale_services()
                
                await asyncio.sleep(60)  # Cleanup every minute
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Cleanup task error: {str(e)}")
                await asyncio.sleep(60)
    
    async def get_registry_stats(self) -> Dict[str, Any]:
        """Get registry statistics"""
        
        if hasattr(self.registry, 'get_all_services'):
            all_services = await self.registry.get_all_services()
        else:
            all_services = []
        
        healthy_count = len([s for s in all_services if s.is_healthy()])
        
        type_counts = {}
        for service in all_services:
            service_type = service.service_type
            type_counts[service_type] = type_counts.get(service_type, 0) + 1
        
        return {
            "total_services": len(all_services),
            "healthy_services": healthy_count,
            "unhealthy_services": len(all_services) - healthy_count,
            "local_services": len(self.local_services),
            "services_by_type": type_counts,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def shutdown(self):
        """Gracefully shutdown service discovery"""
        
        # Cancel cleanup task
        if self.cleanup_task:
            self.cleanup_task.cancel()
        
        # Deregister all local services
        for service_id in list(self.local_services.keys()):
            await self.deregister_local_service(service_id)
        
        self.logger.info("Service discovery shutdown complete")


# Global service discovery instance
_service_discovery = None

def get_service_discovery() -> ServiceDiscovery:
    """Get global service discovery instance"""
    global _service_discovery
    if _service_discovery is None:
        _service_discovery = ServiceDiscovery()
    return _service_discovery


# Alias for compatibility
ServiceDiscoveryService = ServiceDiscovery

# Export main classes
__all__ = [
    'ServiceStatus',
    'ServiceType', 
    'ServiceEndpoint',
    'ServiceInfo',
    'ServiceRegistry',
    'InMemoryServiceRegistry',
    'ServiceDiscovery',
    'ServiceDiscoveryService',
    'get_service_discovery'
]