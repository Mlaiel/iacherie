"""Edge Load Balancer
==================

Advanced load balancing for edge computing infrastructure,
providing intelligent traffic distribution and health monitoring.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass, field
import aiohttp
import random
import hashlib

logger = logging.getLogger(__name__)


class LoadBalancingAlgorithm(str, Enum):
    """Load balancing algorithms."""
    ROUND_ROBIN = "round_robin"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"
    LEAST_RESPONSE_TIME = "least_response_time"
    IP_HASH = "ip_hash"
    RANDOM = "random"
    ADAPTIVE = "adaptive"


class ServerStatus(str, Enum):
    """Backend server status."""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    MAINTENANCE = "maintenance"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckConfig:
    """Health check configuration."""
    enabled: bool = True
    interval: int = 10  # seconds
    timeout: int = 5    # seconds
    retries: int = 3
    path: str = "/health"
    expected_status: int = 200
    expected_body: Optional[str] = None


@dataclass
class BackendServer:
    """Backend server configuration."""
    server_id: str
    host: str
    port: int
    weight: int = 1
    max_connections: int = 1000
    protocol: str = "http"
    health_check: HealthCheckConfig = field(default_factory=HealthCheckConfig)
    metadata: Dict[str, Any] = field(default_factory=dict)


class EdgeLoadBalancer:
    """Advanced load balancer for edge computing."""
    
    def __init__(self,
                 algorithm: LoadBalancingAlgorithm = LoadBalancingAlgorithm.ROUND_ROBIN,
                 session_affinity: bool = False,
                 health_check_enabled: bool = True):
        
        self.algorithm = algorithm
        self.session_affinity = session_affinity
        self.health_check_enabled = health_check_enabled
        
        # Server management
        self.servers: Dict[str, BackendServer] = {}
        self.server_status: Dict[str, ServerStatus] = {}
        self.server_stats: Dict[str, Dict[str, Any]] = {}
        self.server_connections: Dict[str, int] = {}
        
        # Load balancing state
        self.round_robin_index = 0
        self.session_map: Dict[str, str] = {}  # session_id -> server_id
        
        # Health checking
        self.health_check_tasks: Dict[str, asyncio.Task] = {}
        
        # Analytics
        self.request_count = 0
        self.total_response_time = 0.0
        self.algorithm_stats: Dict[str, int] = {}
        
        # Control flags
        self.running = False
        
        logger.info(f"EdgeLoadBalancer initialized with {algorithm.value} algorithm")
    
    async def start(self):
        """Start the load balancer."""
        if self.running:
            logger.warning("Load balancer already running")
            return
        
        self.running = True
        
        # Start health checks for existing servers
        if self.health_check_enabled:
            for server_id in self.servers.keys():
                await self._start_health_check(server_id)
        
        logger.info("Edge load balancer started")
    
    async def stop(self):
        """Stop the load balancer."""
        self.running = False
        
        # Cancel health check tasks
        for task in self.health_check_tasks.values():
            task.cancel()
        
        # Wait for health check tasks to complete
        if self.health_check_tasks:
            await asyncio.gather(*self.health_check_tasks.values(), return_exceptions=True)
        
        self.health_check_tasks.clear()
        
        logger.info("Edge load balancer stopped")
    
    async def add_server(self, server: BackendServer) -> bool:
        """Add a backend server."""
        try:
            self.servers[server.server_id] = server
            self.server_status[server.server_id] = ServerStatus.UNKNOWN
            self.server_stats[server.server_id] = {
                'requests': 0,
                'response_time_total': 0.0,
                'response_time_avg': 0.0,
                'errors': 0,
                'last_request': None
            }
            self.server_connections[server.server_id] = 0
            
            # Start health check if running
            if self.running and self.health_check_enabled:
                await self._start_health_check(server.server_id)
            
            logger.info(f"Added backend server: {server.host}:{server.port}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add server {server.server_id}: {e}")
            return False
    
    async def remove_server(self, server_id: str) -> bool:
        """Remove a backend server."""
        try:
            if server_id not in self.servers:
                return False
            
            # Cancel health check
            if server_id in self.health_check_tasks:
                self.health_check_tasks[server_id].cancel()
                del self.health_check_tasks[server_id]
            
            # Remove from all data structures
            del self.servers[server_id]
            del self.server_status[server_id]
            del self.server_stats[server_id]
            del self.server_connections[server_id]
            
            # Remove session mappings
            sessions_to_remove = [
                session_id for session_id, mapped_server_id in self.session_map.items()
                if mapped_server_id == server_id
            ]
            for session_id in sessions_to_remove:
                del self.session_map[session_id]
            
            logger.info(f"Removed backend server: {server_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove server {server_id}: {e}")
            return False
    
    async def select_server(self, 
                           client_ip: Optional[str] = None,
                           session_id: Optional[str] = None,
                           headers: Optional[Dict[str, str]] = None) -> Optional[BackendServer]:
        """Select a backend server using the configured algorithm."""
        
        # Get healthy servers
        healthy_servers = [
            server_id for server_id, status in self.server_status.items()
            if status == ServerStatus.HEALTHY
        ]
        
        if not healthy_servers:
            logger.warning("No healthy servers available")
            return None
        
        # Check session affinity
        if self.session_affinity and session_id and session_id in self.session_map:
            server_id = self.session_map[session_id]
            if server_id in healthy_servers:
                return self.servers[server_id]
        
        # Apply load balancing algorithm
        selected_server_id = None
        
        if self.algorithm == LoadBalancingAlgorithm.ROUND_ROBIN:
            selected_server_id = await self._round_robin_select(healthy_servers)
        elif self.algorithm == LoadBalancingAlgorithm.WEIGHTED_ROUND_ROBIN:
            selected_server_id = await self._weighted_round_robin_select(healthy_servers)
        elif self.algorithm == LoadBalancingAlgorithm.LEAST_CONNECTIONS:
            selected_server_id = await self._least_connections_select(healthy_servers)
        elif self.algorithm == LoadBalancingAlgorithm.LEAST_RESPONSE_TIME:
            selected_server_id = await self._least_response_time_select(healthy_servers)
        elif self.algorithm == LoadBalancingAlgorithm.IP_HASH:
            selected_server_id = await self._ip_hash_select(healthy_servers, client_ip)
        elif self.algorithm == LoadBalancingAlgorithm.RANDOM:
            selected_server_id = await self._random_select(healthy_servers)
        elif self.algorithm == LoadBalancingAlgorithm.ADAPTIVE:
            selected_server_id = await self._adaptive_select(healthy_servers)
        
        if selected_server_id:
            # Update session mapping
            if self.session_affinity and session_id:
                self.session_map[session_id] = selected_server_id
            
            # Update algorithm stats
            self.algorithm_stats[self.algorithm.value] = self.algorithm_stats.get(self.algorithm.value, 0) + 1
            
            return self.servers[selected_server_id]
        
        return None
    
    async def record_request(self, 
                           server_id: str,
                           response_time: float,
                           success: bool = True):
        """Record request statistics for a server."""
        
        if server_id not in self.server_stats:
            return
        
        stats = self.server_stats[server_id]
        stats['requests'] += 1
        stats['response_time_total'] += response_time
        stats['response_time_avg'] = stats['response_time_total'] / stats['requests']
        stats['last_request'] = datetime.now()
        
        if not success:
            stats['errors'] += 1
        
        # Update global stats
        self.request_count += 1
        self.total_response_time += response_time
    
    async def get_server_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all backend servers."""
        
        status_info = {}
        
        for server_id, server in self.servers.items():
            stats = self.server_stats[server_id]
            
            status_info[server_id] = {
                'server': {
                    'host': server.host,
                    'port': server.port,
                    'weight': server.weight,
                    'max_connections': server.max_connections
                },
                'status': self.server_status[server_id].value,
                'current_connections': self.server_connections[server_id],
                'statistics': stats.copy(),
                'health_check': {
                    'enabled': server.health_check.enabled,
                    'interval': server.health_check.interval,
                    'last_check': stats.get('last_health_check')
                }
            }
        
        return status_info
    
    async def get_load_balancer_stats(self) -> Dict[str, Any]:
        """Get load balancer statistics."""
        
        avg_response_time = (self.total_response_time / self.request_count) if self.request_count > 0 else 0
        
        # Calculate server distribution
        total_requests = sum(stats['requests'] for stats in self.server_stats.values())
        server_distribution = {}
        
        for server_id, stats in self.server_stats.items():
            if total_requests > 0:
                server_distribution[server_id] = (stats['requests'] / total_requests) * 100
            else:
                server_distribution[server_id] = 0
        
        return {
            'algorithm': self.algorithm.value,
            'session_affinity': self.session_affinity,
            'total_requests': self.request_count,
            'average_response_time': avg_response_time,
            'healthy_servers': len([s for s in self.server_status.values() if s == ServerStatus.HEALTHY]),
            'total_servers': len(self.servers),
            'server_distribution': server_distribution,
            'algorithm_usage': self.algorithm_stats.copy(),
            'active_sessions': len(self.session_map)
        }
    
    # Load balancing algorithm implementations
    
    async def _round_robin_select(self, healthy_servers: List[str]) -> str:
        """Round-robin server selection."""
        if not healthy_servers:
            return None
        
        server_id = healthy_servers[self.round_robin_index % len(healthy_servers)]
        self.round_robin_index += 1
        
        return server_id
    
    async def _weighted_round_robin_select(self, healthy_servers: List[str]) -> str:
        """Weighted round-robin server selection."""
        if not healthy_servers:
            return None
        
        # Create weighted list
        weighted_servers = []
        for server_id in healthy_servers:
            server = self.servers[server_id]
            weighted_servers.extend([server_id] * server.weight)
        
        if not weighted_servers:
            return healthy_servers[0]
        
        server_id = weighted_servers[self.round_robin_index % len(weighted_servers)]
        self.round_robin_index += 1
        
        return server_id
    
    async def _least_connections_select(self, healthy_servers: List[str]) -> str:
        """Least connections server selection."""
        if not healthy_servers:
            return None
        
        min_connections = float('inf')
        selected_server = None
        
        for server_id in healthy_servers:
            connections = self.server_connections[server_id]
            if connections < min_connections:
                min_connections = connections
                selected_server = server_id
        
        return selected_server
    
    async def _least_response_time_select(self, healthy_servers: List[str]) -> str:
        """Least response time server selection."""
        if not healthy_servers:
            return None
        
        min_response_time = float('inf')
        selected_server = None
        
        for server_id in healthy_servers:
            stats = self.server_stats[server_id]
            response_time = stats['response_time_avg']
            
            if response_time < min_response_time:
                min_response_time = response_time
                selected_server = server_id
        
        # Fallback to first server if no stats available
        return selected_server or healthy_servers[0]
    
    async def _ip_hash_select(self, healthy_servers: List[str], client_ip: Optional[str]) -> str:
        """IP hash server selection."""
        if not healthy_servers:
            return None
        
        if not client_ip:
            # Fallback to round-robin
            return await self._round_robin_select(healthy_servers)
        
        # Hash the IP address
        hash_value = hashlib.md5(client_ip.encode()).hexdigest()
        index = int(hash_value, 16) % len(healthy_servers)
        
        return healthy_servers[index]
    
    async def _random_select(self, healthy_servers: List[str]) -> str:
        """Random server selection."""
        if not healthy_servers:
            return None
        
        return random.choice(healthy_servers)
    
    async def _adaptive_select(self, healthy_servers: List[str]) -> str:
        """Adaptive server selection based on current load."""
        if not healthy_servers:
            return None
        
        # Score servers based on multiple factors
        server_scores = {}
        
        for server_id in healthy_servers:
            server = self.servers[server_id]
            stats = self.server_stats[server_id]
            connections = self.server_connections[server_id]
            
            # Calculate score (lower is better)
            score = 0
            
            # Connection load factor
            connection_ratio = connections / server.max_connections
            score += connection_ratio * 100
            
            # Response time factor
            if stats['response_time_avg'] > 0:
                score += stats['response_time_avg'] * 10
            
            # Error rate factor
            if stats['requests'] > 0:
                error_rate = stats['errors'] / stats['requests']
                score += error_rate * 50
            
            # Weight factor (inverse)
            score += (1.0 / server.weight) * 10
            
            server_scores[server_id] = score
        
        # Select server with lowest score
        selected_server = min(server_scores.keys(), key=lambda x: server_scores[x])
        return selected_server
    
    # Health checking
    
    async def _start_health_check(self, server_id: str):
        """Start health check task for a server."""
        if server_id in self.health_check_tasks:
            return
        
        server = self.servers[server_id]
        if not server.health_check.enabled:
            self.server_status[server_id] = ServerStatus.HEALTHY  # Assume healthy if no check
            return
        
        task = asyncio.create_task(self._health_check_loop(server_id))
        self.health_check_tasks[server_id] = task
    
    async def _health_check_loop(self, server_id: str):
        """Health check loop for a server."""
        server = self.servers[server_id]
        health_config = server.health_check
        
        while self.running and server_id in self.servers:
            try:
                is_healthy = await self._perform_health_check(server, health_config)
                
                # Update status
                new_status = ServerStatus.HEALTHY if is_healthy else ServerStatus.UNHEALTHY
                old_status = self.server_status.get(server_id, ServerStatus.UNKNOWN)
                
                if new_status != old_status:
                    self.server_status[server_id] = new_status
                    logger.info(f"Server {server_id} status changed: {old_status.value} -> {new_status.value}")
                
                # Update stats
                self.server_stats[server_id]['last_health_check'] = datetime.now()
                
                await asyncio.sleep(health_config.interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check error for server {server_id}: {e}")
                self.server_status[server_id] = ServerStatus.UNHEALTHY
                await asyncio.sleep(health_config.interval)
    
    async def _perform_health_check(self, server: BackendServer, health_config: HealthCheckConfig) -> bool:
        """Perform health check on a server."""
        
        url = f"{server.protocol}://{server.host}:{server.port}{health_config.path}"
        
        for attempt in range(health_config.retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        url, 
                        timeout=aiohttp.ClientTimeout(total=health_config.timeout)
                    ) as response:
                        
                        # Check status code
                        if response.status != health_config.expected_status:
                            continue
                        
                        # Check response body if specified
                        if health_config.expected_body:
                            body = await response.text()
                            if health_config.expected_body not in body:
                                continue
                        
                        return True
                        
            except Exception as e:
                logger.debug(f"Health check attempt {attempt + 1} failed for {server.host}:{server.port}: {e}")
                if attempt < health_config.retries - 1:
                    await asyncio.sleep(1)  # Brief delay between retries
        
        return False


def create_load_balancer(
    algorithm: LoadBalancingAlgorithm = LoadBalancingAlgorithm.ROUND_ROBIN,
    session_affinity: bool = False,
    health_check_enabled: bool = True
) -> EdgeLoadBalancer:
    """Create and configure a load balancer instance."""
    return EdgeLoadBalancer(
        algorithm=algorithm,
        session_affinity=session_affinity,
        health_check_enabled=health_check_enabled
    )


# Example usage and testing
if __name__ == "__main__":
    async def test_load_balancer():
        """Test the load balancer."""
        lb = create_load_balancer(LoadBalancingAlgorithm.LEAST_CONNECTIONS)
        
        # Add test servers
        servers = [
            BackendServer(
                server_id="server1",
                host="localhost",
                port=8001,
                weight=2
            ),
            BackendServer(
                server_id="server2", 
                host="localhost",
                port=8002,
                weight=1
            ),
            BackendServer(
                server_id="server3",
                host="localhost", 
                port=8003,
                weight=3
            )
        ]
        
        for server in servers:
            await lb.add_server(server)
        
        # Start load balancer
        await lb.start()
        
        # Simulate some requests
        for i in range(10):
            server = await lb.select_server(client_ip=f"192.168.1.{i}", session_id=f"session_{i}")
            if server:
                # Simulate request processing
                response_time = 0.1 + (i % 3) * 0.05  # Varying response times
                await lb.record_request(server.server_id, response_time, success=True)
                print(f"Request {i}: routed to {server.host}:{server.port}")
        
        # Get statistics
        status = await lb.get_server_status()
        stats = await lb.get_load_balancer_stats()
        
        print(f"Load balancer stats: {stats}")
        print(f"Server status: {status}")
        
        # Stop load balancer
        await lb.stop()
    
    # Run test
    asyncio.run(test_load_balancer())