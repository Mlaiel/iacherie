"""
DNS Service for Ainflue Microservices
Service discovery and DNS management

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import socket
import json
import os
from dataclasses import dataclass
import aiofiles

logger = logging.getLogger(__name__)


@dataclass
class ServiceRecord:
    """DNS service record"""
    name: str
    host: str
    port: int
    service_type: str
    health_status: str = "healthy"
    ttl: int = 300
    metadata: Dict[str, Any] = None
    registered_at: datetime = None
    last_heartbeat: datetime = None

    def __post_init__(self):
        if self.registered_at is None:
            self.registered_at = datetime.utcnow()
        if self.last_heartbeat is None:
            self.last_heartbeat = datetime.utcnow()
        if self.metadata is None:
            self.metadata = {}


class DNSService:
    """Enterprise DNS service for microservices discovery"""

    def __init__(self):
        self.service_registry = {}
        self.dns_cache = {}
        self.dns_records_path = os.getenv("DNS_RECORDS_PATH", "/tmp/dns_records.json")
        self.cache_ttl = timedelta(minutes=5)
        self.heartbeat_timeout = timedelta(minutes=2)
        
    async def register_service(
        self, 
        name: str, 
        host: str, 
        port: int, 
        service_type: str,
        metadata: Dict[str, Any] = None
    ) -> bool:
        """Register a service in DNS"""
        try:
            service_key = f"{name}.{service_type}"
            
            service_record = ServiceRecord(
                name=name,
                host=host,
                port=port,
                service_type=service_type,
                metadata=metadata or {}
            )
            
            self.service_registry[service_key] = service_record
            
            # Persist to disk
            await self._persist_registry()
            
            logger.info(f"Service registered: {service_key} -> {host}:{port}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register service {name}: {str(e)}")
            return False

    async def unregister_service(self, name: str, service_type: str) -> bool:
        """Unregister a service from DNS"""
        try:
            service_key = f"{name}.{service_type}"
            
            if service_key in self.service_registry:
                del self.service_registry[service_key]
                await self._persist_registry()
                logger.info(f"Service unregistered: {service_key}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to unregister service {name}: {str(e)}")
            return False

    async def resolve_service(self, name: str, service_type: str) -> Optional[ServiceRecord]:
        """Resolve service by name and type"""
        try:
            service_key = f"{name}.{service_type}"
            
            # Check cache first
            cache_key = f"resolve_{service_key}"
            if cache_key in self.dns_cache:
                cached_result, cached_time = self.dns_cache[cache_key]
                if datetime.utcnow() - cached_time < self.cache_ttl:
                    return cached_result
            
            # Check registry
            if service_key in self.service_registry:
                service = self.service_registry[service_key]
                
                # Verify service is healthy and responsive
                if await self._check_service_health(service):
                    service.health_status = "healthy"
                    # Cache result
                    self.dns_cache[cache_key] = (service, datetime.utcnow())
                    return service
                else:
                    service.health_status = "unhealthy"
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to resolve service {name}.{service_type}: {str(e)}")
            return None

    async def resolve_all_services(self, service_type: str) -> List[ServiceRecord]:
        """Resolve all services of a given type"""
        try:
            services = []
            
            for service_key, service in self.service_registry.items():
                if service.service_type == service_type:
                    # Check health
                    if await self._check_service_health(service):
                        service.health_status = "healthy"
                        services.append(service)
                    else:
                        service.health_status = "unhealthy"
            
            return services
            
        except Exception as e:
            logger.error(f"Failed to resolve services of type {service_type}: {str(e)}")
            return []

    async def update_service_health(self, name: str, service_type: str, status: str) -> bool:
        """Update service health status"""
        try:
            service_key = f"{name}.{service_type}"
            
            if service_key in self.service_registry:
                service = self.service_registry[service_key]
                service.health_status = status
                service.last_heartbeat = datetime.utcnow()
                
                await self._persist_registry()
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to update service health {name}: {str(e)}")
            return False

    async def heartbeat(self, name: str, service_type: str) -> bool:
        """Service heartbeat"""
        try:
            service_key = f"{name}.{service_type}"
            
            if service_key in self.service_registry:
                service = self.service_registry[service_key]
                service.last_heartbeat = datetime.utcnow()
                service.health_status = "healthy"
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to process heartbeat for {name}: {str(e)}")
            return False

    async def cleanup_stale_services(self) -> int:
        """Remove stale services that haven't sent heartbeat"""
        try:
            stale_services = []
            cutoff_time = datetime.utcnow() - self.heartbeat_timeout
            
            for service_key, service in self.service_registry.items():
                if service.last_heartbeat < cutoff_time:
                    stale_services.append(service_key)
            
            for service_key in stale_services:
                del self.service_registry[service_key]
                logger.info(f"Removed stale service: {service_key}")
            
            if stale_services:
                await self._persist_registry()
            
            return len(stale_services)
            
        except Exception as e:
            logger.error(f"Failed to cleanup stale services: {str(e)}")
            return 0

    async def get_service_topology(self) -> Dict[str, Any]:
        """Get complete service topology"""
        try:
            topology = {
                "services": {},
                "service_types": {},
                "total_services": len(self.service_registry),
                "healthy_services": 0,
                "unhealthy_services": 0,
                "generated_at": datetime.utcnow().isoformat()
            }
            
            for service_key, service in self.service_registry.items():
                # Add to services
                topology["services"][service_key] = {
                    "name": service.name,
                    "host": service.host,
                    "port": service.port,
                    "type": service.service_type,
                    "health": service.health_status,
                    "registered_at": service.registered_at.isoformat(),
                    "last_heartbeat": service.last_heartbeat.isoformat(),
                    "metadata": service.metadata
                }
                
                # Group by type
                if service.service_type not in topology["service_types"]:
                    topology["service_types"][service.service_type] = []
                
                topology["service_types"][service.service_type].append({
                    "name": service.name,
                    "host": service.host,
                    "port": service.port,
                    "health": service.health_status
                })
                
                # Count health status
                if service.health_status == "healthy":
                    topology["healthy_services"] += 1
                else:
                    topology["unhealthy_services"] += 1
            
            return topology
            
        except Exception as e:
            logger.error(f"Failed to get service topology: {str(e)}")
            return {}

    async def _check_service_health(self, service: ServiceRecord) -> bool:
        """Check if service is reachable"""
        try:
            # Simple TCP connection test
            future = asyncio.open_connection(service.host, service.port)
            reader, writer = await asyncio.wait_for(future, timeout=5.0)
            writer.close()
            await writer.wait_closed()
            return True
            
        except Exception:
            return False

    async def _persist_registry(self):
        """Persist service registry to disk"""
        try:
            registry_data = {}
            
            for service_key, service in self.service_registry.items():
                registry_data[service_key] = {
                    "name": service.name,
                    "host": service.host,
                    "port": service.port,
                    "service_type": service.service_type,
                    "health_status": service.health_status,
                    "ttl": service.ttl,
                    "metadata": service.metadata,
                    "registered_at": service.registered_at.isoformat(),
                    "last_heartbeat": service.last_heartbeat.isoformat()
                }
            
            os.makedirs(os.path.dirname(self.dns_records_path), exist_ok=True)
            
            async with aiofiles.open(self.dns_records_path, 'w') as f:
                await f.write(json.dumps(registry_data, indent=2))
                
        except Exception as e:
            logger.error(f"Failed to persist registry: {str(e)}")

    async def _load_registry(self):
        """Load service registry from disk"""
        try:
            if os.path.exists(self.dns_records_path):
                async with aiofiles.open(self.dns_records_path, 'r') as f:
                    registry_data = json.loads(await f.read())
                
                for service_key, data in registry_data.items():
                    service = ServiceRecord(
                        name=data["name"],
                        host=data["host"],
                        port=data["port"],
                        service_type=data["service_type"],
                        health_status=data["health_status"],
                        ttl=data["ttl"],
                        metadata=data["metadata"],
                        registered_at=datetime.fromisoformat(data["registered_at"]),
                        last_heartbeat=datetime.fromisoformat(data["last_heartbeat"])
                    )
                    
                    self.service_registry[service_key] = service
                
                logger.info(f"Loaded {len(self.service_registry)} services from registry")
                
        except Exception as e:
            logger.error(f"Failed to load registry: {str(e)}")

    async def health_check(self) -> Dict[str, Any]:
        """DNS service health check"""
        try:
            # Cleanup stale services
            cleaned = await self.cleanup_stale_services()
            
            return {
                "status": "healthy",
                "total_services": len(self.service_registry),
                "cache_entries": len(self.dns_cache),
                "stale_services_cleaned": cleaned,
                "registry_path": self.dns_records_path,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"DNS health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }


# Global DNS service instance
dns_service = DNSService()


async def register_service(name: str, host: str, port: int, service_type: str, metadata: Dict[str, Any] = None) -> bool:
    """Register service in DNS"""
    return await dns_service.register_service(name, host, port, service_type, metadata)


async def resolve_service(name: str, service_type: str) -> Optional[ServiceRecord]:
    """Resolve service by name and type"""
    return await dns_service.resolve_service(name, service_type)


async def get_service_topology() -> Dict[str, Any]:
    """Get complete service topology"""
    return await dns_service.get_service_topology()


if __name__ == "__main__":
    async def test_dns():
        """Test DNS service functionality"""
        print("Testing DNS Service...")
        
        # Test registration
        result = await register_service(
            "api-gateway", "localhost", 8000, "gateway",
            {"version": "1.0", "environment": "test"}
        )
        print(f"Registration result: {result}")
        
        # Test resolution
        service = await resolve_service("api-gateway", "gateway")
        print(f"Resolved service: {service}")
        
        # Test topology
        topology = await get_service_topology()
        print(f"Topology: {topology}")
        
        # Test health
        health = await dns_service.health_check()
        print(f"Health: {health}")
    
    asyncio.run(test_dns())