#!/usr/bin/env python3
"""Failover Template - Automatic failover to backup systems"""

import asyncio
from typing import List, Dict

class FailoverTemplate:
    """Automatic failover management"""
    
    def __init__(self, primary_endpoint: str):
        self.primary_endpoint = primary_endpoint
        self.backup_endpoints: List[str] = []
        self.current_endpoint = primary_endpoint
        self.health_status: Dict[str, bool] = {}
    
    def add_backup_endpoint(self, endpoint: str):
        """Add backup endpoint"""
        self.backup_endpoints.append(endpoint)
        self.health_status[endpoint] = True
    
    async def check_health(self, endpoint: str) -> bool:
        """Check endpoint health"""
        # Simulate health check
        await asyncio.sleep(0.1)
        return self.health_status.get(endpoint, False)
    
    async def execute_failover(self) -> str:
        """Execute failover to healthy endpoint"""
        # Check primary first
        if await self.check_health(self.primary_endpoint):
            self.current_endpoint = self.primary_endpoint
            return self.primary_endpoint
        
        # Try backup endpoints
        for endpoint in self.backup_endpoints:
            if await self.check_health(endpoint):
                self.current_endpoint = endpoint
                print(f"🔄 Failed over to {endpoint}")
                return endpoint
        
        raise Exception("No healthy endpoints available")
    
    def get_current_endpoint(self) -> str:
        """Get current active endpoint"""
        return self.current_endpoint