"""Load Balancer - IA Influencer Agent Platform

Advanced load balancing for database connections:
- Multiple load balancing algorithms
- Real-time performance monitoring
- Adaptive weight adjustment
- Circuit breaker integration
- Geographic awareness
- Connection affinity management

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""import asyncio
import logging
import time
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import random
import hashlib
import statistics


class LoadBalancingAlgorithm(Enum):
    """Load balancing algorithms"""    ROUND_ROBIN = "round_robin"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_LEAST_CONNECTIONS = "weighted_least_connections"
    LEAST_RESPONSE_TIME = "least_response_time"
    WEIGHTED_RESPONSE_TIME = "weighted_response_time"
    HASH_BASED = "hash_based"
    RANDOM = "random"
    GEOGRAPHIC = "geographic"


class ServerStatus(Enum):
    """Server status for load balancing"""    ACTIVE = "active"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"
    FAILED = "failed"


@dataclass
class ServerMetrics:
    """Server performance metrics"""    active_connections: int = 0
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    last_response_time: float = 0.0
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    last_updated: datetime = field(default_factory=datetime.utcnow)
    
    def success_rate(self) -> float:
        """Calculate success rate"""        if self.total_requests == 0:
            return 1.0
        return self.successful_requests / self.total_requests
    
    def error_rate(self) -> float:
        """Calculate error rate"""        return 1.0 - self.success_rate()


@dataclass
class DatabaseServer:
    """Database server configuration"""    server_id: str
    host: str
    port: int
    weight: float = 1.0  # Static weight
    dynamic_weight: float = 1.0  # Dynamically adjusted weight
    max_connections: int = 100
    status: ServerStatus = ServerStatus.ACTIVE
    region: str = "default"
    zone: str = "default"
    
    # Performance metrics
    metrics: ServerMetrics = field(default_factory=ServerMetrics)
    
    # Circuit breaker state
    circuit_breaker_failures: int = 0
    circuit_breaker_last_failure: Optional[datetime] = None
    circuit_breaker_open: bool = False
    
    def is_available(self) -> bool:
        """Check if server is available for load balancing"""        return (
            self.status in [ServerStatus.ACTIVE, ServerStatus.DEGRADED] and
            not self.circuit_breaker_open and
            self.metrics.active_connections < self.max_connections
        )
    
    def load_factor(self) -> float:
        """Calculate current load factor (0.0 = no load, 1.0 = full load)"""        if self.max_connections == 0:
            return 0.0
        return self.metrics.active_connections / self.max_connections


class DatabaseLoadBalancer:
    """    Advanced database load balancer.
    
    Provides:
    - Multiple load balancing algorithms
    - Real-time performance monitoring
    - Adaptive weight adjustment
    - Circuit breaker protection
    - Connection affinity
    - Geographic load distribution
    """    
    def __init__(self, algorithm: LoadBalancingAlgorithm = LoadBalancingAlgorithm.WEIGHTED_ROUND_ROBIN):
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.algorithm = algorithm
        self.servers: Dict[str, DatabaseServer] = {}
        self.server_groups: Dict[str, List[str]] = {}  # Group servers by type/role
        
        # Round robin state
        self.round_robin_index: Dict[str, int] = {}
        
        # Hash-based routing
        self.hash_ring: Dict[str, List[Tuple[int, str]]] = {}
        
        # Performance monitoring
        self.monitoring_enabled = True
        self.metrics_collection_interval = 60  # seconds
        self.metrics_tasks: Dict[str, asyncio.Task] = {}
        
        # Circuit breaker configuration
        self.circuit_breaker_threshold = 5  # failures
        self.circuit_breaker_timeout = 60  # seconds
        self.circuit_breaker_reset_timeout = 300  # seconds
        
        # Adaptive weight adjustment
        self.adaptive_weights = True
        self.weight_adjustment_interval = 120  # seconds
        self.weight_adjustment_factor = 0.1
        
        # Connection affinity
        self.affinity_sessions: Dict[str, str] = {}  # session_id -> server_id
        self.affinity_timeout = 3600  # seconds
        
        # Statistics
        self.stats = {
            "total_requests": 0,
            "successful_routes": 0,
            "failed_routes": 0,
            "circuit_breaker_trips": 0,
            "weight_adjustments": 0
        }
    
    async def initialize(self, server_configs: Dict[str, List[Dict[str, Any]]]) -> None:
        """Initialize load balancer with server configurations"""        
        # Configure servers
        for group_name, configs in server_configs.items():
            self.server_groups[group_name] = []
            
            for config in configs:
                server = DatabaseServer(**config)
                self.servers[server.server_id] = server
                self.server_groups[group_name].append(server.server_id)
            
            # Initialize round robin index
            self.round_robin_index[group_name] = 0
            
            # Build hash ring for consistent hashing
            self._build_hash_ring(group_name)
        
        # Start monitoring
        if self.monitoring_enabled:
            await self.start_monitoring()
        
        self.logger.info(f"Load balancer initialized with {len(self.servers)} servers")
    
    def _build_hash_ring(self, group_name: str) -> None:
        """Build consistent hash ring for hash-based load balancing"""        if group_name not in self.server_groups:
            return
        
        ring = []
        for server_id in self.server_groups[group_name]:
            server = self.servers[server_id]
            # Create multiple virtual nodes for better distribution
            virtual_nodes = max(1, int(server.weight * 100))
            
            for i in range(virtual_nodes):
                hash_key = hashlib.md5(f"{server_id}:{i}".encode()).hexdigest()
                hash_value = int(hash_key[:8], 16)
                ring.append((hash_value, server_id))
        
        # Sort by hash value
        ring.sort(key=lambda x: x[0])
        self.hash_ring[group_name] = ring
    
    async def start_monitoring(self) -> None:
        """Start performance monitoring"""        for group_name in self.server_groups.keys():
            task = asyncio.create_task(self._monitoring_loop(group_name))
            self.metrics_tasks[group_name] = task
        
        # Start weight adjustment task
        if self.adaptive_weights:
            task = asyncio.create_task(self._weight_adjustment_loop())
            self.metrics_tasks["weight_adjustment"] = task
        
        self.logger.info("Started load balancer monitoring")
    
    async def stop_monitoring(self) -> None:
        """Stop performance monitoring"""        for task in self.metrics_tasks.values():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        self.metrics_tasks.clear()
        self.logger.info("Stopped load balancer monitoring")
    
    async def _monitoring_loop(self, group_name: str) -> None:
        """Performance monitoring loop for server group"""        while True:
            try:
                await self._collect_metrics(group_name)
                await asyncio.sleep(self.metrics_collection_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Monitoring error for group {group_name}: {e}")
                await asyncio.sleep(self.metrics_collection_interval)
    
    async def _collect_metrics(self, group_name: str) -> None:
        """Collect performance metrics for server group"""        if group_name not in self.server_groups:
            return
        
        for server_id in self.server_groups[group_name]:
            server = self.servers[server_id]
            
            try:
                # Update metrics (simplified - in real implementation, would query actual servers)
                await self._update_server_metrics(server)
                
                # Check circuit breaker
                self._check_circuit_breaker(server)
                
            except Exception as e:
                self.logger.warning(f"Failed to collect metrics for {server_id}: {e}")
    
    async def _update_server_metrics(self, server: DatabaseServer) -> None:
        """Update server metrics (simplified implementation)"""        # In real implementation, this would query the actual database server
        # For now, simulate some metrics
        
        # Simulate varying response times and load
        base_response_time = 0.1 + (server.metrics.active_connections / server.max_connections) * 0.5
        server.metrics.last_response_time = base_response_time + random.uniform(-0.05, 0.05)
        
        # Update average response time
        if server.metrics.total_requests > 0:
            alpha = 0.1  # Exponential moving average factor
            server.metrics.average_response_time = (
                alpha * server.metrics.last_response_time +
                (1 - alpha) * server.metrics.average_response_time
            )
        else:
            server.metrics.average_response_time = server.metrics.last_response_time
        
        # Simulate CPU and memory usage
        load_factor = server.load_factor()
        server.metrics.cpu_usage = min(100.0, load_factor * 80 + random.uniform(0, 20))
        server.metrics.memory_usage = min(100.0, load_factor * 70 + random.uniform(0, 30))
        
        server.metrics.last_updated = datetime.utcnow()
    
    def _check_circuit_breaker(self, server: DatabaseServer) -> None:
        """Check and update circuit breaker status"""        now = datetime.utcnow()
        
        # Reset circuit breaker if timeout exceeded
        if (server.circuit_breaker_open and 
            server.circuit_breaker_last_failure and
            now - server.circuit_breaker_last_failure > timedelta(seconds=self.circuit_breaker_reset_timeout)):
            
            server.circuit_breaker_open = False
            server.circuit_breaker_failures = 0
            self.logger.info(f"Circuit breaker reset for server {server.server_id}")
        
        # Check if circuit breaker should trip
        if (not server.circuit_breaker_open and
            server.circuit_breaker_failures >= self.circuit_breaker_threshold and
            server.circuit_breaker_last_failure and
            now - server.circuit_breaker_last_failure < timedelta(seconds=self.circuit_breaker_timeout)):
            
            server.circuit_breaker_open = True
            self.stats["circuit_breaker_trips"] += 1
            self.logger.warning(f"Circuit breaker tripped for server {server.server_id}")
    
    async def _weight_adjustment_loop(self) -> None:
        """Adaptive weight adjustment loop"""        while True:
            try:
                await self._adjust_weights()
                await asyncio.sleep(self.weight_adjustment_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Weight adjustment error: {e}")
                await asyncio.sleep(self.weight_adjustment_interval)
    
    async def _adjust_weights(self) -> None:
        """Adjust server weights based on performance"""        for group_name, server_ids in self.server_groups.items():
            if len(server_ids) < 2:
                continue
            
            # Collect performance data
            servers_data = []
            for server_id in server_ids:
                server = self.servers[server_id]
                if server.is_available():
                    servers_data.append({
                        "server": server,
                        "performance_score": self._calculate_performance_score(server)
                    })
            
            if len(servers_data) < 2:
                continue
            
            # Calculate average performance
            avg_performance = statistics.mean([data["performance_score"] for data in servers_data])
            
            # Adjust weights
            for data in servers_data:
                server = data["server"]
                performance_score = data["performance_score"]
                
                # Calculate weight adjustment
                performance_ratio = performance_score / avg_performance if avg_performance > 0 else 1.0
                adjustment = (performance_ratio - 1.0) * self.weight_adjustment_factor
                
                # Apply adjustment
                new_weight = max(0.1, min(10.0, server.dynamic_weight * (1.0 + adjustment)))
                
                if abs(new_weight - server.dynamic_weight) > 0.05:
                    server.dynamic_weight = new_weight
                    self.stats["weight_adjustments"] += 1
                    
                    self.logger.debug(
                        f"Adjusted weight for {server.server_id}: "
                        f"{server.dynamic_weight:.2f} (performance: {performance_score:.2f})"
                    )
            
            # Rebuild hash ring with new weights
            self._build_hash_ring(group_name)
    
    def _calculate_performance_score(self, server: DatabaseServer) -> float:
        """Calculate performance score for a server (higher = better)"""        # Base score from success rate
        success_rate = server.metrics.success_rate()
        
        # Response time factor (lower is better)
        response_time_factor = 1.0 / (1.0 + server.metrics.average_response_time)
        
        # Load factor (lower is better)
        load_factor = 1.0 - server.load_factor()
        
        # CPU usage factor (lower is better)
        cpu_factor = 1.0 - (server.metrics.cpu_usage / 100.0)
        
        # Combine factors
        score = (
            success_rate * 0.4 +
            response_time_factor * 0.3 +
            load_factor * 0.2 +
            cpu_factor * 0.1
        )
        
        return max(0.0, min(1.0, score))
    
    async def select_server(self, 
                          group_name: str, 
                          session_id: Optional[str] = None,
                          routing_key: Optional[str] = None,
                          preferred_region: Optional[str] = None) -> Optional[DatabaseServer]:
        """Select best server using configured algorithm"""        
        if group_name not in self.server_groups:
            return None
        
        # Check session affinity first
        if session_id and session_id in self.affinity_sessions:
            server_id = self.affinity_sessions[session_id]
            server = self.servers.get(server_id)
            if server and server.is_available():
                return server
            else:
                # Remove stale affinity
                del self.affinity_sessions[session_id]
        
        # Get available servers
        available_servers = [
            self.servers[server_id] 
            for server_id in self.server_groups[group_name]
            if self.servers[server_id].is_available()
        ]
        
        if not available_servers:
            return None
        
        # Filter by region if specified
        if preferred_region:
            region_servers = [s for s in available_servers if s.region == preferred_region]
            if region_servers:
                available_servers = region_servers
        
        # Apply load balancing algorithm
        selected_server = None
        
        if self.algorithm == LoadBalancingAlgorithm.ROUND_ROBIN:
            selected_server = self._round_robin_select(group_name, available_servers)
            
        elif self.algorithm == LoadBalancingAlgorithm.WEIGHTED_ROUND_ROBIN:
            selected_server = self._weighted_round_robin_select(group_name, available_servers)
            
        elif self.algorithm == LoadBalancingAlgorithm.LEAST_CONNECTIONS:
            selected_server = min(available_servers, key=lambda s: s.metrics.active_connections)
            
        elif self.algorithm == LoadBalancingAlgorithm.WEIGHTED_LEAST_CONNECTIONS:
            selected_server = min(
                available_servers, 
                key=lambda s: s.metrics.active_connections / s.dynamic_weight
            )
            
        elif self.algorithm == LoadBalancingAlgorithm.LEAST_RESPONSE_TIME:
            selected_server = min(available_servers, key=lambda s: s.metrics.average_response_time)
            
        elif self.algorithm == LoadBalancingAlgorithm.WEIGHTED_RESPONSE_TIME:
            selected_server = min(
                available_servers,
                key=lambda s: s.metrics.average_response_time / s.dynamic_weight
            )
            
        elif self.algorithm == LoadBalancingAlgorithm.HASH_BASED:
            selected_server = self._hash_based_select(group_name, routing_key or session_id or "default")
            
        elif self.algorithm == LoadBalancingAlgorithm.RANDOM:
            selected_server = random.choice(available_servers)
            
        elif self.algorithm == LoadBalancingAlgorithm.GEOGRAPHIC:
            selected_server = self._geographic_select(available_servers, preferred_region)
        
        # Set session affinity
        if selected_server and session_id:
            self.affinity_sessions[session_id] = selected_server.server_id
        
        # Update statistics
        self.stats["total_requests"] += 1
        if selected_server:
            self.stats["successful_routes"] += 1
        else:
            self.stats["failed_routes"] += 1
        
        return selected_server
    
    def _round_robin_select(self, group_name: str, servers: List[DatabaseServer]) -> DatabaseServer:
        """Round robin server selection"""        if not servers:
            return None
        
        index = self.round_robin_index[group_name] % len(servers)
        self.round_robin_index[group_name] = (index + 1) % len(servers)
        
        return servers[index]
    
    def _weighted_round_robin_select(self, group_name: str, servers: List[DatabaseServer]) -> DatabaseServer:
        """Weighted round robin server selection"""        if not servers:
            return None
        
        # Create weighted list
        weighted_servers = []
        for server in servers:
            weight = max(1, int(server.dynamic_weight * 10))
            weighted_servers.extend([server] * weight)
        
        if not weighted_servers:
            return servers[0]
        
        index = self.round_robin_index[group_name] % len(weighted_servers)
        self.round_robin_index[group_name] = (index + 1) % len(weighted_servers)
        
        return weighted_servers[index]
    
    def _hash_based_select(self, group_name: str, key: str) -> Optional[DatabaseServer]:
        """Consistent hash-based server selection"""        if group_name not in self.hash_ring or not self.hash_ring[group_name]:
            return None
        
        # Calculate hash of the key
        hash_value = int(hashlib.md5(key.encode()).hexdigest()[:8], 16)
        
        # Find first server with hash >= key hash
        ring = self.hash_ring[group_name]
        for ring_hash, server_id in ring:
            if ring_hash >= hash_value:
                server = self.servers.get(server_id)
                if server and server.is_available():
                    return server
        
        # Wrap around to first server
        server_id = ring[0][1]
        server = self.servers.get(server_id)
        return server if server and server.is_available() else None
    
    def _geographic_select(self, servers: List[DatabaseServer], preferred_region: Optional[str]) -> DatabaseServer:
        """Geographic-aware server selection"""        if preferred_region:
            # First try servers in preferred region
            region_servers = [s for s in servers if s.region == preferred_region]
            if region_servers:
                # Use least connections within region
                return min(region_servers, key=lambda s: s.metrics.active_connections)
        
        # Fallback to overall least connections
        return min(servers, key=lambda s: s.metrics.active_connections)
    
    async def report_connection_start(self, server_id: str) -> None:
        """Report that a connection has started to a server"""        server = self.servers.get(server_id)
        if server:
            server.metrics.active_connections += 1
            server.metrics.total_requests += 1
    
    async def report_connection_end(self, 
                                  server_id: str, 
                                  success: bool, 
                                  response_time: float) -> None:
        """Report that a connection has ended"""        server = self.servers.get(server_id)
        if not server:
            return
        
        # Update connection count
        server.metrics.active_connections = max(0, server.metrics.active_connections - 1)
        
        # Update request statistics
        if success:
            server.metrics.successful_requests += 1
        else:
            server.metrics.failed_requests += 1
            server.circuit_breaker_failures += 1
            server.circuit_breaker_last_failure = datetime.utcnow()
        
        # Update response time
        server.metrics.last_response_time = response_time
        
        # Update average response time
        if server.metrics.total_requests > 0:
            alpha = 0.1
            server.metrics.average_response_time = (
                alpha * response_time +
                (1 - alpha) * server.metrics.average_response_time
            )
    
    def add_server(self, group_name: str, server_config: Dict[str, Any]) -> bool:
        """Add a new server to the load balancer"""        try:
            server = DatabaseServer(**server_config)
            
            # Add to servers
            self.servers[server.server_id] = server
            
            # Add to group
            if group_name not in self.server_groups:
                self.server_groups[group_name] = []
                self.round_robin_index[group_name] = 0
            
            self.server_groups[group_name].append(server.server_id)
            
            # Rebuild hash ring
            self._build_hash_ring(group_name)
            
            self.logger.info(f"Added server {server.server_id} to group {group_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add server: {e}")
            return False
    
    def remove_server(self, server_id: str) -> bool:
        """Remove a server from the load balancer"""        try:
            if server_id not in self.servers:
                return False
            
            # Remove from groups
            for group_name, server_ids in self.server_groups.items():
                if server_id in server_ids:
                    server_ids.remove(server_id)
                    self._build_hash_ring(group_name)
            
            # Remove from servers
            del self.servers[server_id]
            
            # Clean up affinity sessions
            self.affinity_sessions = {
                session: sid for session, sid in self.affinity_sessions.items() 
                if sid != server_id
            }
            
            self.logger.info(f"Removed server {server_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to remove server {server_id}: {e}")
            return False
    
    def set_server_status(self, server_id: str, status: ServerStatus) -> bool:
        """Set server status"""        server = self.servers.get(server_id)
        if server:
            server.status = status
            self.logger.info(f"Set server {server_id} status to {status.value}")
            return True
        return False
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive load balancer metrics"""        group_stats = {}
        
        for group_name, server_ids in self.server_groups.items():
            servers_info = []
            total_connections = 0
            total_requests = 0
            
            for server_id in server_ids:
                server = self.servers[server_id]
                total_connections += server.metrics.active_connections
                total_requests += server.metrics.total_requests
                
                servers_info.append({
                    "server_id": server.server_id,
                    "host": f"{server.host}:{server.port}",
                    "status": server.status.value,
                    "weight": server.weight,
                    "dynamic_weight": server.dynamic_weight,
                    "active_connections": server.metrics.active_connections,
                    "success_rate": server.metrics.success_rate(),
                    "average_response_time": server.metrics.average_response_time,
                    "load_factor": server.load_factor(),
                    "circuit_breaker_open": server.circuit_breaker_open,
                    "available": server.is_available()
                })
            
            group_stats[group_name] = {
                "total_servers": len(server_ids),
                "available_servers": len([s for s in servers_info if s["available"]]),
                "total_connections": total_connections,
                "total_requests": total_requests,
                "servers": servers_info
            }
        
        return {
            "algorithm": self.algorithm.value,
            "statistics": self.stats,
            "group_statistics": group_stats,
            "configuration": {
                "monitoring_enabled": self.monitoring_enabled,
                "adaptive_weights": self.adaptive_weights,
                "circuit_breaker_threshold": self.circuit_breaker_threshold,
                "affinity_timeout": self.affinity_timeout
            },
            "active_affinity_sessions": len(self.affinity_sessions)
        }
    
    async def shutdown(self) -> None:
        """Shutdown load balancer"""        self.logger.info("Shutting down load balancer...")
        
        await self.stop_monitoring()
        
        # Clear data structures
        self.servers.clear()
        self.server_groups.clear()
        self.round_robin_index.clear()
        self.hash_ring.clear()
        self.affinity_sessions.clear()
        
        self.logger.info("Load balancer shutdown completed")
