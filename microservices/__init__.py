"""
Microservices Module for Ainflue Platform
Provides distributed system infrastructure components for microservices architecture.

Author: Fahed Mlaiel <mlaiel@live.de>
"""

from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

__all__ = [
    'MicroserviceBase',
    'ServiceRegistry',
    'get_service_registry',
    'register_service',
    'discover_service'
]

class MicroserviceBase:
    """Base class for all microservices in the Ainflue platform"""
    
    def __init__(self, service_name -> None: str, service_id -> None: str = None) -> None:
        self.service_name = service_name
        self.service_id = service_id or f"{service_name}-{id(self)}"
        self.status = "initializing"
        self.health_status = "unknown"
        
    def start(self) -> bool:
        """Start the microservice"""
        self.status = "running"
        logger.info(f"Started microservice: {self.service_name}")
        return True
        
    def stop(self) -> bool:
        """Stop the microservice"""
        self.status = "stopped"
        logger.info(f"Stopped microservice: {self.service_name}")
        return True
        
    def health_check(self) -> Dict[str, Any]:
        """Perform health check"""
        return {
            'service_name': self.service_name,
            'service_id': self.service_id,
            'status': self.status,
            'health': self.health_status
        }

class ServiceRegistry:
    """Central registry for managing microservices"""
    
    def __init__(self) -> None:
        self._services: Dict[str, Dict[str, Any]] = {}
        
    def register(self, service_name: str, service_info: Dict[str, Any]) -> bool:
        """Register a service"""
        self._services[service_name] = service_info
        logger.info(f"Registered service: {service_name}")
        return True
        
    def unregister(self, service_name: str) -> bool:
        """Unregister a service"""
        if service_name in self._services:
            del self._services[service_name]
            logger.info(f"Unregistered service: {service_name}")
            return True
        return False
        
    def discover(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Discover a service by name"""
        return self._services.get(service_name)
        
    def list_services(self) -> List[str]:
        """List all registered services"""
        return list(self._services.keys())

# Global service registry instance
_service_registry = ServiceRegistry()

def get_service_registry() -> ServiceRegistry:
    """Get the global service registry instance"""
    return _service_registry

def register_service(service_name: str, service_info: Dict[str, Any]) -> bool:
    """Register a service in the global registry"""
    return _service_registry.register(service_name, service_info)

def discover_service(service_name: str) -> Optional[Dict[str, Any]]:
    """Discover a service from the global registry"""
    return _service_registry.discover(service_name)