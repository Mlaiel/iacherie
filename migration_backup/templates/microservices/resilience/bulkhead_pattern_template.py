#!/usr/bin/env python3
"""Bulkhead Pattern Template - Resource isolation and compartmentalization"""

import asyncio
from typing import Dict

class BulkheadPatternTemplate:
    """Bulkhead pattern for resource isolation"""
    
    def __init__(self):
        self.resource_pools: Dict[str, asyncio.Semaphore] = {}
    
    def create_resource_pool(self, pool_name: str, max_concurrent: int):
        """Create isolated resource pool"""
        self.resource_pools[pool_name] = asyncio.Semaphore(max_concurrent)
    
    async def execute_in_pool(self, pool_name: str, func, *args, **kwargs):
        """Execute function in isolated resource pool"""
        if pool_name not in self.resource_pools:
            raise ValueError(f"Resource pool {pool_name} not found")
        
        semaphore = self.resource_pools[pool_name]
        
        async with semaphore:
            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            else:
                return func(*args, **kwargs)