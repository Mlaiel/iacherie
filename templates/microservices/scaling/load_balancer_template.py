#!/usr/bin/env python3
"""Load Balancer Template - Advanced load balancing strategies"""

from typing import List
from enum import Enum

class LoadBalancingStrategy(Enum):
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED = "weighted"

class LoadBalancerTemplate:
    """Advanced load balancer template"""
    
    def __init__(self, strategy: LoadBalancingStrategy = LoadBalancingStrategy.ROUND_ROBIN):
        self.strategy = strategy
        self.backend_servers: List[str] = []
        self.current_index = 0
    
    def add_backend(self, server_url: str):
        """Add backend server"""
        self.backend_servers.append(server_url)
    
    def get_next_server(self) -> str:
        """Get next server based on strategy"""
        if not self.backend_servers:
            return ""
        
        if self.strategy == LoadBalancingStrategy.ROUND_ROBIN:
            server = self.backend_servers[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.backend_servers)
            return server
        
        return self.backend_servers[0]