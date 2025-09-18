#!/usr/bin/env python3
"""Service Catalog Template - Service discovery and documentation catalog"""

from typing import Dict, List

class ServiceCatalogTemplate:
    """Service catalog for microservices discovery"""
    
    def __init__(self):
        self.services: Dict[str, Dict] = {}
    
    def register_service(self, name: str, endpoint: str, version: str, description: str):
        """Register service in catalog"""
        self.services[name] = {
            "endpoint": endpoint,
            "version": version,
            "description": description,
            "status": "active"
        }
    
    def get_service_info(self, name: str) -> Dict:
        """Get service information"""
        return self.services.get(name, {})
    
    def list_services(self) -> List[str]:
        """List all registered services"""
        return list(self.services.keys())