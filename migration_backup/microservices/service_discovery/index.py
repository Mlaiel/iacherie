"""
Service Discovery Index
Microservices Service Discovery and Registry

This module provides service discovery capabilities for microservices
to find and connect to each other dynamically.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class ServiceDiscoveryService:
    """Service discovery and registry"""
    
    def __init__(self):
        self.services: Dict[str, List[Dict[str, Any]]] = {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def register_service(self, service_name: str, host: str, port: int, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Register a service instance"""
        try:
            if service_name not in self.services:
                self.services[service_name] = []
            
            service_info = {
                'host': host,
                'port': port,
                'metadata': metadata or {},
                'registered_at': datetime.now(),
                'last_heartbeat': datetime.now()
            }
            
            self.services[service_name].append(service_info)
            self.logger.info(f"Service registered: {service_name} at {host}:{port}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register service {service_name}: {str(e)}")
            return False
    
    async def discover_service(self, service_name: str) -> List[Dict[str, Any]]:
        """Discover service instances"""
        return self.services.get(service_name, [])
    
    async def deregister_service(self, service_name: str, host: str, port: int) -> bool:
        """Deregister a service instance"""
        try:
            if service_name in self.services:
                self.services[service_name] = [
                    service for service in self.services[service_name]
                    if not (service['host'] == host and service['port'] == port)
                ]
                self.logger.info(f"Service deregistered: {service_name} at {host}:{port}")
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to deregister service {service_name}: {str(e)}")
            return False

# Global service discovery instance
service_discovery = ServiceDiscoveryService()

__all__ = ['ServiceDiscoveryService', 'service_discovery']