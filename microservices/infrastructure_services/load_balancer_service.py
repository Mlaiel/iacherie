#!/usr/bin/env python3
"""
⚖️ Load Balancer Service - Infrastructure Services Module
========================================================

Enterprise load balancing and traffic distribution service.

Author: Fahed Mlaiel (mlaiel@live.de)
Infrastructure Services Module
"""

import asyncio
import logging
import random
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class LoadBalancingAlgorithm(Enum):
    """Load balancing algorithms"""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    IP_HASH = "ip_hash"
    RANDOM = "random"

class ServerStatus(Enum):
    """Server status states"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    MAINTENANCE = "maintenance"
    OVERLOADED = "overloaded"

@dataclass
class BackendServer:
    """Backend server configuration"""
    server_id: str
    host: str
    port: int
    weight: int = 1
    max_connections: int = 1000
    current_connections: int = 0
    status: ServerStatus = ServerStatus.HEALTHY
    response_time: float = 0.0
    last_health_check: Optional[datetime] = None

class LoadBalancerService:
    """Enterprise Load Balancer Service"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.backend_servers = []
        self.algorithm = LoadBalancingAlgorithm.ROUND_ROBIN
        self.current_index = 0
        self.health_check_interval = 30
        self.enabled = True
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "last_reset": datetime.now(timezone.utc)
        }
        
        # Initialize load balancer
        self._initialize_backend_servers()
        
        self.logger.info("✅ LoadBalancerService initialized")
        
    def _initialize_backend_servers(self):
        """Initialize backend server pool"""
        try:
            # Add default backend servers
            default_servers = [
                BackendServer("server_001", "localhost", 8001, weight=2),
                BackendServer("server_002", "localhost", 8002, weight=1),
                BackendServer("server_003", "localhost", 8003, weight=1),
                BackendServer("server_004", "localhost", 8004, weight=3),
            ]
            
            self.backend_servers = default_servers
            
        except Exception as e:
            self.logger.error(f"Failed to initialize backend servers: {e}")
    
    def add_server(self, server: BackendServer) -> bool:
        """Add a new backend server"""
        try:
            # Check if server already exists
            if any(s.server_id == server.server_id for s in self.backend_servers):
                self.logger.warning(f"Server {server.server_id} already exists")
                return False
            
            self.backend_servers.append(server)
            self.logger.info(f"Added server {server.server_id} ({server.host}:{server.port})")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add server: {e}")
            return False
    
    def remove_server(self, server_id: str) -> bool:
        """Remove a backend server"""
        try:
            self.backend_servers = [s for s in self.backend_servers if s.server_id != server_id]
            self.logger.info(f"Removed server {server_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to remove server {server_id}: {e}")
            return False
    
    def get_next_server(self, client_ip: Optional[str] = None) -> Optional[BackendServer]:
        """Get next available server based on load balancing algorithm"""
        try:
            healthy_servers = [s for s in self.backend_servers if s.status == ServerStatus.HEALTHY]
            
            if not healthy_servers:
                self.logger.warning("No healthy servers available")
                return None
            
            if self.algorithm == LoadBalancingAlgorithm.ROUND_ROBIN:
                server = healthy_servers[self.current_index % len(healthy_servers)]
                self.current_index += 1
                return server
                
            elif self.algorithm == LoadBalancingAlgorithm.LEAST_CONNECTIONS:
                return min(healthy_servers, key=lambda s: s.current_connections)
                
            elif self.algorithm == LoadBalancingAlgorithm.WEIGHTED_ROUND_ROBIN:
                # Simple weighted implementation
                weights = [s.weight for s in healthy_servers]
                total_weight = sum(weights)
                random_weight = random.randint(1, total_weight)
                
                current_weight = 0
                for server in healthy_servers:
                    current_weight += server.weight
                    if random_weight <= current_weight:
                        return server
                        
            elif self.algorithm == LoadBalancingAlgorithm.IP_HASH:
                if client_ip:
                    hash_value = hash(client_ip) % len(healthy_servers)
                    return healthy_servers[hash_value]
                else:
                    # Fallback to round robin if no IP
                    return healthy_servers[self.current_index % len(healthy_servers)]
                    
            elif self.algorithm == LoadBalancingAlgorithm.RANDOM:
                return random.choice(healthy_servers)
            
            # Default fallback
            return healthy_servers[0]
            
        except Exception as e:
            self.logger.error(f"Failed to get next server: {e}")
            return None
    
    async def health_check_server(self, server: BackendServer) -> bool:
        """Perform health check on a specific server"""
        try:
            # Simulate health check
            await asyncio.sleep(0.1)  # Mock network delay
            
            # Mock health check result (90% success rate)
            is_healthy = random.random() > 0.1
            
            if is_healthy:
                server.status = ServerStatus.HEALTHY
                server.response_time = random.uniform(0.05, 0.3)  # Mock response time
            else:
                server.status = ServerStatus.UNHEALTHY
                server.response_time = 5.0  # High response time for unhealthy
            
            server.last_health_check = datetime.now(timezone.utc)
            
            return is_healthy
            
        except Exception as e:
            self.logger.error(f"Health check failed for server {server.server_id}: {e}")
            server.status = ServerStatus.UNHEALTHY
            return False
    
    async def health_check_all_servers(self):
        """Perform health check on all servers"""
        try:
            tasks = [self.health_check_server(server) for server in self.backend_servers]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            healthy_count = sum(1 for result in results if result is True)
            
            self.logger.info(f"Health check completed: {healthy_count}/{len(self.backend_servers)} servers healthy")
            
        except Exception as e:
            self.logger.error(f"Health check all servers failed: {e}")
    
    def get_load_balancer_stats(self) -> Dict[str, Any]:
        """Get load balancer statistics"""
        try:
            healthy_servers = [s for s in self.backend_servers if s.status == ServerStatus.HEALTHY]
            
            return {
                "total_servers": len(self.backend_servers),
                "healthy_servers": len(healthy_servers),
                "unhealthy_servers": len(self.backend_servers) - len(healthy_servers),
                "algorithm": self.algorithm.value,
                "total_requests": self.stats["total_requests"],
                "successful_requests": self.stats["successful_requests"],
                "failed_requests": self.stats["failed_requests"],
                "success_rate": (self.stats["successful_requests"] / max(1, self.stats["total_requests"])) * 100,
                "servers": [
                    {
                        "server_id": server.server_id,
                        "host": server.host,
                        "port": server.port,
                        "status": server.status.value,
                        "current_connections": server.current_connections,
                        "response_time": server.response_time,
                        "weight": server.weight
                    }
                    for server in self.backend_servers
                ],
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get load balancer stats: {e}")
            return {"error": str(e)}
    
    def set_algorithm(self, algorithm: LoadBalancingAlgorithm):
        """Set load balancing algorithm"""
        try:
            self.algorithm = algorithm
            self.logger.info(f"Load balancing algorithm set to: {algorithm.value}")
            
        except Exception as e:
            self.logger.error(f"Failed to set algorithm: {e}")
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get load balancer service health status"""
        try:
            healthy_servers = sum(1 for s in self.backend_servers if s.status == ServerStatus.HEALTHY)
            
            return {
                "status": "healthy" if healthy_servers > 0 else "unhealthy",
                "service": "LoadBalancerService", 
                "version": "1.0.0",
                "enabled": self.enabled,
                "algorithm": self.algorithm.value,
                "servers_total": len(self.backend_servers),
                "servers_healthy": healthy_servers,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "service": "LoadBalancerService"
            }
    
    async def start_monitoring(self):
        """Start continuous health monitoring"""
        try:
            self.logger.info("Starting load balancer monitoring...")
            
            while self.enabled:
                try:
                    await self.health_check_all_servers()
                    await asyncio.sleep(self.health_check_interval)
                    
                except Exception as e:
                    self.logger.error(f"Error in monitoring loop: {e}")
                    await asyncio.sleep(10)
                    
        except Exception as e:
            self.logger.error(f"Failed to start monitoring: {e}")

# Create default instance
load_balancer_service = LoadBalancerService()

__all__ = [
    'LoadBalancerService',
    'BackendServer',
    'LoadBalancingAlgorithm',
    'ServerStatus', 
    'load_balancer_service'
]