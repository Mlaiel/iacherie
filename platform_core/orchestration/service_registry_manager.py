#!/usr/bin/env python3
"""
Service Registry Manager - Enterprise Core Component
Dynamic service discovery and registration system

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
Licensed under Enterprise Commercial License.

This module provides comprehensive service registry capabilities including:
- Dynamic service discovery and registration
- Service health monitoring and status tracking
- Load balancing and failover coordination
- Service mesh integration and management
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import hashlib
import random
from urllib.parse import urlparse

try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False
    aiohttp = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ServiceState(Enum):
    """Service state enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DRAINING = "draining"
    MAINTENANCE = "maintenance"
    FAILED = "failed"


class LoadBalanceStrategy(Enum):
    """Load balancing strategy"""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    HASH_BASED = "hash_based"
    RANDOM = "random"


@dataclass
class ServiceEndpoint:
    """Service endpoint definition"""
    url: str
    weight: int = 100
    max_connections: int = 1000
    current_connections: int = 0
    response_time_ms: float = 0.0
    error_count: int = 0
    last_error: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ServiceInstance:
    """Complete service instance information"""
    service_id: str
    instance_id: str
    name: str
    version: str
    state: ServiceState
    endpoints: List[ServiceEndpoint]
    tags: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)
    health_check_url: Optional[str] = None
    health_check_interval: int = 30
    last_heartbeat: Optional[datetime] = None
    registration_time: datetime = field(default_factory=datetime.utcnow)
    ttl: int = 300  # Time to live in seconds


@dataclass
class ServiceQuery:
    """Service discovery query"""
    service_name: Optional[str] = None
    tags: Set[str] = field(default_factory=set)
    version: Optional[str] = None
    state: Optional[ServiceState] = None
    metadata_filters: Dict[str, Any] = field(default_factory=dict)


class ServiceRegistryManager:
    """
    Enterprise Service Registry Manager
    
    Provides dynamic service discovery, registration, health monitoring,
    and load balancing coordination for distributed services with
    enterprise-grade reliability and performance.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.services: Dict[str, ServiceInstance] = {}  # instance_id -> ServiceInstance
        self.service_index: Dict[str, Set[str]] = {}  # service_name -> Set[instance_id]
        self.tag_index: Dict[str, Set[str]] = {}  # tag -> Set[instance_id]
        self.load_balancers: Dict[str, int] = {}  # service_name -> round_robin_index
        self._health_check_interval = self.config.get('health_check_interval', 30)
        self._cleanup_interval = self.config.get('cleanup_interval', 60)
        self._health_check_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
        self._session: Optional[aiohttp.ClientSession] = None
        
        logger.info("Service Registry Manager initialized")
    
    async def start(self) -> None:
        """Start the service registry manager"""
        try:
            logger.info("Starting Service Registry Manager...")
            
            # Initialize HTTP session
            if AIOHTTP_AVAILABLE:
                timeout = aiohttp.ClientTimeout(total=10)
                self._session = aiohttp.ClientSession(timeout=timeout)
            else:
                logger.warning("aiohttp not available, HTTP health checks disabled")
            
            # Start background tasks
            self._health_check_task = asyncio.create_task(self._health_check_loop())
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
            
            logger.info("Service Registry Manager started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start Service Registry Manager: {e}")
            raise
    
    async def stop(self) -> None:
        """Stop the service registry manager"""
        try:
            logger.info("Stopping Service Registry Manager...")
            
            # Signal shutdown
            self._shutdown_event.set()
            
            # Cancel background tasks
            if self._health_check_task:
                self._health_check_task.cancel()
            if self._cleanup_task:
                self._cleanup_task.cancel()
            
            # Close HTTP session
            if self._session:
                await self._session.close()
            
            logger.info("Service Registry Manager stopped")
            
        except Exception as e:
            logger.error(f"Error stopping Service Registry Manager: {e}")
    
    # Service Registration
    async def register_service(self, service: ServiceInstance) -> bool:
        """Register a new service instance"""
        try:
            # Validate service instance
            if not service.service_id or not service.instance_id:
                raise ValueError("Service ID and instance ID are required")
            
            if not service.endpoints:
                raise ValueError("At least one endpoint is required")
            
            # Validate endpoints
            for endpoint in service.endpoints:
                if not self._is_valid_url(endpoint.url):
                    raise ValueError(f"Invalid endpoint URL: {endpoint.url}")
            
            # Check for conflicts
            if service.instance_id in self.services:
                logger.warning(f"Service instance {service.instance_id} already registered, updating...")
            
            # Register service
            self.services[service.instance_id] = service
            
            # Update indexes
            self._update_service_index(service)
            self._update_tag_index(service)
            
            # Perform initial health check
            await self._check_service_health(service.instance_id)
            
            logger.info(f"Service instance {service.instance_id} ({service.name}) registered successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register service {service.instance_id}: {e}")
            return False
    
    async def unregister_service(self, instance_id: str) -> bool:
        """Unregister a service instance"""
        try:
            if instance_id not in self.services:
                logger.warning(f"Service instance {instance_id} not found for unregistration")
                return False
            
            service = self.services.pop(instance_id)
            
            # Update indexes
            self._remove_from_service_index(service)
            self._remove_from_tag_index(service)
            
            logger.info(f"Service instance {instance_id} ({service.name}) unregistered successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unregister service {instance_id}: {e}")
            return False
    
    async def heartbeat(self, instance_id: str) -> bool:
        """Update service heartbeat"""
        try:
            if instance_id not in self.services:
                logger.warning(f"Heartbeat for unknown service instance: {instance_id}")
                return False
            
            service = self.services[instance_id]
            service.last_heartbeat = datetime.utcnow()
            
            # If service was failed, mark as active
            if service.state == ServiceState.FAILED:
                service.state = ServiceState.ACTIVE
                logger.info(f"Service instance {instance_id} recovered from failure")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update heartbeat for {instance_id}: {e}")
            return False
    
    # Service Discovery
    async def discover_services(self, query: ServiceQuery) -> List[ServiceInstance]:
        """Discover services based on query criteria"""
        try:
            matching_instances = []
            
            # Start with all services if no specific criteria
            candidate_instances = set(self.services.keys())
            
            # Filter by service name
            if query.service_name:
                if query.service_name in self.service_index:
                    candidate_instances &= self.service_index[query.service_name]
                else:
                    return []  # No services with this name
            
            # Filter by tags
            if query.tags:
                for tag in query.tags:
                    if tag in self.tag_index:
                        candidate_instances &= self.tag_index[tag]
                    else:
                        return []  # Tag not found
            
            # Apply remaining filters
            for instance_id in candidate_instances:
                service = self.services[instance_id]
                
                # Filter by version
                if query.version and service.version != query.version:
                    continue
                
                # Filter by state
                if query.state and service.state != query.state:
                    continue
                
                # Filter by metadata
                if query.metadata_filters:
                    match = True
                    for key, value in query.metadata_filters.items():
                        if key not in service.metadata or service.metadata[key] != value:
                            match = False
                            break
                    if not match:
                        continue
                
                matching_instances.append(service)
            
            return matching_instances
            
        except Exception as e:
            logger.error(f"Failed to discover services: {e}")
            return []
    
    async def get_service_instance(self, instance_id: str) -> Optional[ServiceInstance]:
        """Get specific service instance"""
        return self.services.get(instance_id)
    
    async def get_healthy_instances(self, service_name: str) -> List[ServiceInstance]:
        """Get all healthy instances of a service"""
        query = ServiceQuery(service_name=service_name, state=ServiceState.ACTIVE)
        return await self.discover_services(query)
    
    # Load Balancing
    async def get_endpoint(self, service_name: str, strategy: LoadBalanceStrategy = LoadBalanceStrategy.ROUND_ROBIN, key: Optional[str] = None) -> Optional[ServiceEndpoint]:
        """Get service endpoint using specified load balancing strategy"""
        try:
            healthy_instances = await self.get_healthy_instances(service_name)
            
            if not healthy_instances:
                logger.warning(f"No healthy instances found for service: {service_name}")
                return None
            
            # Collect all endpoints from healthy instances
            all_endpoints = []
            for instance in healthy_instances:
                for endpoint in instance.endpoints:
                    all_endpoints.append(endpoint)
            
            if not all_endpoints:
                return None
            
            # Apply load balancing strategy
            if strategy == LoadBalanceStrategy.ROUND_ROBIN:
                return self._round_robin_selection(service_name, all_endpoints)
            elif strategy == LoadBalanceStrategy.LEAST_CONNECTIONS:
                return self._least_connections_selection(all_endpoints)
            elif strategy == LoadBalanceStrategy.WEIGHTED_ROUND_ROBIN:
                return self._weighted_round_robin_selection(service_name, all_endpoints)
            elif strategy == LoadBalanceStrategy.HASH_BASED:
                return self._hash_based_selection(all_endpoints, key or "")
            elif strategy == LoadBalanceStrategy.RANDOM:
                return self._random_selection(all_endpoints)
            else:
                return all_endpoints[0]  # Fallback to first endpoint
            
        except Exception as e:
            logger.error(f"Failed to get endpoint for {service_name}: {e}")
            return None
    
    # Health Monitoring
    async def get_service_health(self, instance_id: str) -> Dict[str, Any]:
        """Get health information for a service instance"""
        try:
            service = self.services.get(instance_id)
            if not service:
                return {"status": "not_found"}
            
            return {
                "instance_id": instance_id,
                "service_name": service.name,
                "state": service.state.value,
                "last_heartbeat": service.last_heartbeat.isoformat() if service.last_heartbeat else None,
                "endpoints": [
                    {
                        "url": ep.url,
                        "response_time_ms": ep.response_time_ms,
                        "error_count": ep.error_count,
                        "current_connections": ep.current_connections
                    }
                    for ep in service.endpoints
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to get health for {instance_id}: {e}")
            return {"status": "error", "message": str(e)}
    
    async def get_registry_stats(self) -> Dict[str, Any]:
        """Get registry statistics"""
        try:
            stats = {
                "total_services": len(self.services),
                "active_services": len([s for s in self.services.values() if s.state == ServiceState.ACTIVE]),
                "failed_services": len([s for s in self.services.values() if s.state == ServiceState.FAILED]),
                "service_types": len(self.service_index),
                "total_endpoints": sum(len(s.endpoints) for s in self.services.values()),
                "services_by_name": {name: len(instances) for name, instances in self.service_index.items()},
                "services_by_state": {}
            }
            
            # Count by state
            for state in ServiceState:
                count = len([s for s in self.services.values() if s.state == state])
                stats["services_by_state"][state.value] = count
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get registry stats: {e}")
            return {}
    
    # Internal Methods
    def _is_valid_url(self, url: str) -> bool:
        """Validate URL format"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    def _update_service_index(self, service: ServiceInstance) -> None:
        """Update service name index"""
        if service.name not in self.service_index:
            self.service_index[service.name] = set()
        self.service_index[service.name].add(service.instance_id)
    
    def _update_tag_index(self, service: ServiceInstance) -> None:
        """Update tag index"""
        for tag in service.tags:
            if tag not in self.tag_index:
                self.tag_index[tag] = set()
            self.tag_index[tag].add(service.instance_id)
    
    def _remove_from_service_index(self, service: ServiceInstance) -> None:
        """Remove from service name index"""
        if service.name in self.service_index:
            self.service_index[service.name].discard(service.instance_id)
            if not self.service_index[service.name]:
                del self.service_index[service.name]
    
    def _remove_from_tag_index(self, service: ServiceInstance) -> None:
        """Remove from tag index"""
        for tag in service.tags:
            if tag in self.tag_index:
                self.tag_index[tag].discard(service.instance_id)
                if not self.tag_index[tag]:
                    del self.tag_index[tag]
    
    # Load Balancing Algorithms
    def _round_robin_selection(self, service_name: str, endpoints: List[ServiceEndpoint]) -> ServiceEndpoint:
        """Round robin load balancing"""
        if service_name not in self.load_balancers:
            self.load_balancers[service_name] = 0
        
        index = self.load_balancers[service_name]
        endpoint = endpoints[index % len(endpoints)]
        self.load_balancers[service_name] = (index + 1) % len(endpoints)
        
        return endpoint
    
    def _least_connections_selection(self, endpoints: List[ServiceEndpoint]) -> ServiceEndpoint:
        """Least connections load balancing"""
        return min(endpoints, key=lambda ep: ep.current_connections)
    
    def _weighted_round_robin_selection(self, service_name: str, endpoints: List[ServiceEndpoint]) -> ServiceEndpoint:
        """Weighted round robin load balancing"""
        # Create weighted list
        weighted_endpoints = []
        for endpoint in endpoints:
            weighted_endpoints.extend([endpoint] * endpoint.weight)
        
        if not weighted_endpoints:
            return endpoints[0]
        
        if service_name not in self.load_balancers:
            self.load_balancers[service_name] = 0
        
        index = self.load_balancers[service_name]
        endpoint = weighted_endpoints[index % len(weighted_endpoints)]
        self.load_balancers[service_name] = (index + 1) % len(weighted_endpoints)
        
        return endpoint
    
    def _hash_based_selection(self, endpoints: List[ServiceEndpoint], key: str) -> ServiceEndpoint:
        """Hash-based load balancing"""
        hash_value = int(hashlib.md5(key.encode()).hexdigest(), 16)
        index = hash_value % len(endpoints)
        return endpoints[index]
    
    def _random_selection(self, endpoints: List[ServiceEndpoint]) -> ServiceEndpoint:
        """Random load balancing"""
        return random.choice(endpoints)
    
    # Health Check Logic
    async def _check_service_health(self, instance_id: str) -> None:
        """Check health of a specific service instance"""
        try:
            service = self.services.get(instance_id)
            if not service:
                return
            
            # Check TTL-based health
            if service.last_heartbeat:
                time_since_heartbeat = (datetime.utcnow() - service.last_heartbeat).total_seconds()
                if time_since_heartbeat > service.ttl:
                    service.state = ServiceState.FAILED
                    logger.warning(f"Service {instance_id} marked as failed due to TTL expiry")
                    return
            
            # Perform HTTP health checks if configured
            if service.health_check_url and self._session and AIOHTTP_AVAILABLE:
                try:
                    start_time = datetime.utcnow()
                    async with self._session.get(service.health_check_url) as response:
                        end_time = datetime.utcnow()
                        response_time = (end_time - start_time).total_seconds() * 1000
                        
                        if response.status == 200:
                            service.state = ServiceState.ACTIVE
                            # Update endpoint response times
                            for endpoint in service.endpoints:
                                endpoint.response_time_ms = response_time
                                endpoint.error_count = 0
                        else:
                            service.state = ServiceState.FAILED
                            for endpoint in service.endpoints:
                                endpoint.error_count += 1
                                endpoint.last_error = datetime.utcnow()
                            
                            logger.warning(f"Service {instance_id} health check failed with status {response.status}")
                
                except Exception as e:
                    service.state = ServiceState.FAILED
                    for endpoint in service.endpoints:
                        endpoint.error_count += 1
                        endpoint.last_error = datetime.utcnow()
                    
                    logger.error(f"Health check failed for service {instance_id}: {e}")
            
        except Exception as e:
            logger.error(f"Health check error for service {instance_id}: {e}")
    
    async def _health_check_loop(self) -> None:
        """Background health check loop"""
        while not self._shutdown_event.is_set():
            try:
                # Check all registered services
                tasks = []
                for instance_id in list(self.services.keys()):
                    task = asyncio.create_task(self._check_service_health(instance_id))
                    tasks.append(task)
                
                if tasks:
                    await asyncio.gather(*tasks, return_exceptions=True)
                
                # Wait for next check
                await asyncio.sleep(self._health_check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check loop error: {e}")
                await asyncio.sleep(5)
    
    async def _cleanup_loop(self) -> None:
        """Background cleanup loop for expired services"""
        while not self._shutdown_event.is_set():
            try:
                current_time = datetime.utcnow()
                
                # Find expired services
                to_remove = []
                for instance_id, service in self.services.items():
                    # Remove services that have been failed for too long
                    if (service.state == ServiceState.FAILED 
                        and service.last_heartbeat
                        and (current_time - service.last_heartbeat).total_seconds() > service.ttl * 3):
                        to_remove.append(instance_id)
                
                # Remove expired services
                for instance_id in to_remove:
                    await self.unregister_service(instance_id)
                    logger.info(f"Cleaned up expired service: {instance_id}")
                
                # Wait for next cleanup
                await asyncio.sleep(self._cleanup_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cleanup loop error: {e}")
                await asyncio.sleep(30)
    
    # Context Manager Support
    async def __aenter__(self):
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()


# Factory function
def create_service_registry(config: Optional[Dict[str, Any]] = None) -> ServiceRegistryManager:
    """Factory function to create a Service Registry Manager"""
    return ServiceRegistryManager(config)


# Example usage
async def main():
    """Example usage of Service Registry Manager"""
    async with create_service_registry() as registry:
        # Register a service instance
        content_service = ServiceInstance(
            service_id="content_service",
            instance_id="content_service_1",
            name="content_service",
            version="1.0.0",
            state=ServiceState.ACTIVE,
            endpoints=[
                ServiceEndpoint(url="http://content-service-1:8080", weight=100),
                ServiceEndpoint(url="http://content-service-1:8081", weight=50)
            ],
            tags={"content", "production"},
            health_check_url="http://content-service-1:8080/health"
        )
        
        await registry.register_service(content_service)
        
        # Discover services
        query = ServiceQuery(service_name="content_service", tags={"production"})
        services = await registry.discover_services(query)
        print(f"Found {len(services)} content services")
        
        # Get load balanced endpoint
        endpoint = await registry.get_endpoint("content_service", LoadBalanceStrategy.ROUND_ROBIN)
        if endpoint:
            print(f"Selected endpoint: {endpoint.url}")
        
        # Get registry stats
        stats = await registry.get_registry_stats()
        print(f"Registry stats: {stats}")


if __name__ == "__main__":
    asyncio.run(main())