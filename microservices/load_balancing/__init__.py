"""
Load Balancing Module for Ainflue Microservices
Implements various load balancing strategies for service distribution.

Author: Fahed Mlaiel <mlaiel@live.de>
"""

import random
import threading
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)

__all__ = ['LoadBalancer', 'RoundRobinBalancer', 'WeightedRoundRobinBalancer', 'RandomBalancer', 'HealthAwareBalancer']

class LoadBalancer(ABC):
    """Abstract base class for load balancers"""
    
    def __init__(self) -> None:
        self.servers: List[Dict[str, Any]] = []
        self._lock = threading.Lock()
    
    def add_server(self, server -> None: Dict[str, Any]) -> None:
        """Add a server to the pool"""
        with self._lock:
            self.servers.append(server)
            logger.info(f"Added server: {server.get('id', 'unknown')}")
    
    def remove_server(self, server_id -> None: str) -> None:
        """Remove a server from the pool"""
        with self._lock:
            self.servers = [s for s in self.servers if s.get('id') != server_id]
            logger.info(f"Removed server: {server_id}")
    
    @abstractmethod
    def select_server(self) -> Optional[Dict[str, Any]]:
        """Select a server based on balancing strategy"""
        pass

class RoundRobinBalancer(LoadBalancer):
    """Round-robin load balancer"""
    
    def __init__(self) -> None:
        super().__init__()
        self.current_index = 0
    
    def select_server(self) -> Optional[Dict[str, Any]]:
        """Select next server in round-robin fashion"""
        with self._lock:
            if not self.servers:
                return None
            
            server = self.servers[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.servers)
            return server

class WeightedRoundRobinBalancer(LoadBalancer):
    """Weighted round-robin load balancer"""
    
    def __init__(self) -> None:
        super().__init__()
        self.current_weights: Dict[str, int] = {}
    
    def select_server(self) -> Optional[Dict[str, Any]]:
        """Select server based on weights"""
        with self._lock:
            if not self.servers:
                return None
            
            # Initialize weights if needed
            for server in self.servers:
                server_id = server.get('id')
                if server_id not in self.current_weights:
                    self.current_weights[server_id] = 0
            
            # Find server with highest current weight
            best_server = None
            best_weight = -1
            
            for server in self.servers:
                server_id = server.get('id')
                weight = server.get('weight', 1)
                
                self.current_weights[server_id] += weight
                
                if self.current_weights[server_id] > best_weight:
                    best_weight = self.current_weights[server_id]
                    best_server = server
            
            # Reduce all weights by the selected server's original weight
            if best_server:
                selected_weight = best_server.get('weight', 1)
                for server_id in self.current_weights:
                    self.current_weights[server_id] -= selected_weight
            
            return best_server

class RandomBalancer(LoadBalancer):
    """Random load balancer"""
    
    def select_server(self) -> Optional[Dict[str, Any]]:
        """Select a random server"""
        with self._lock:
            if not self.servers:
                return None
            return random.choice(self.servers)

class HealthAwareBalancer(LoadBalancer):
    """Health-aware load balancer that only routes to healthy servers"""
    
    def __init__(self, base_balancer -> None: LoadBalancer = None) -> None:
        super().__init__()
        self.base_balancer = base_balancer or RoundRobinBalancer()
        self.health_status: Dict[str, bool] = {}
    
    def update_server_health(self, server_id -> None: str, is_healthy -> None: bool) -> None:
        """Update health status of a server"""
        with self._lock:
            self.health_status[server_id] = is_healthy
            logger.info(f"Server {server_id} health updated: {'healthy' if is_healthy else 'unhealthy'}")
    
    def select_server(self) -> Optional[Dict[str, Any]]:
        """Select a healthy server using base balancer strategy"""
        with self._lock:
            healthy_servers = [
                server for server in self.servers
                if self.health_status.get(server.get('id'), True)  # Default to healthy
            ]
            
            if not healthy_servers:
                logger.warning("No healthy servers available")
                return None
            
            # Temporarily update base balancer with healthy servers
            original_servers = self.base_balancer.servers
            self.base_balancer.servers = healthy_servers
            
            selected = self.base_balancer.select_server()
            
            # Restore original servers
            self.base_balancer.servers = original_servers
            
            return selected

def create_load_balancer(strategy: str = "round_robin", **kwargs) -> LoadBalancer:
    """Factory function to create load balancers"""
    if strategy == "round_robin":
        return RoundRobinBalancer()
    elif strategy == "weighted_round_robin":
        return WeightedRoundRobinBalancer()
    elif strategy == "random":
        return RandomBalancer()
    elif strategy == "health_aware":
        base_strategy = kwargs.get("base_strategy", "round_robin")
        base_balancer = create_load_balancer(base_strategy)
        return HealthAwareBalancer(base_balancer)
    else:
        raise ValueError(f"Unknown load balancing strategy: {strategy}")
