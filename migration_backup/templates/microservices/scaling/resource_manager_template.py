#!/usr/bin/env python3
"""Resource Manager Template - Resource allocation and monitoring"""

from typing import Dict

class ResourceManagerTemplate:
    """Resource management template"""
    
    def __init__(self):
        self.resource_allocations: Dict[str, Dict] = {}
    
    def allocate_resources(self, service_name: str, cpu: str, memory: str, storage: str):
        """Allocate resources to service"""
        self.resource_allocations[service_name] = {
            "cpu": cpu,
            "memory": memory,
            "storage": storage
        }
        print(f"Allocated resources to {service_name}: CPU={cpu}, Memory={memory}, Storage={storage}")
    
    def get_resource_usage(self) -> Dict[str, Dict]:
        """Get current resource usage"""
        return self.resource_allocations
    
    def deallocate_resources(self, service_name: str):
        """Deallocate resources from service"""
        if service_name in self.resource_allocations:
            del self.resource_allocations[service_name]
            print(f"Deallocated resources from {service_name}")