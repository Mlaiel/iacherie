"""gRPC Load Balancing Template for IA Chéries Platform

⚠️  AVERTISSEMENT LÉGAL:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

Author: Fahed Mlaiel (mlaiel@live.de)
Created: 2025-01-18
Version: 1.0.0
"""

import grpc
import time
import random
import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
import threading
from collections import defaultdict, deque
import statistics
from enum import Enum
import hashlib

logger = logging.getLogger(__name__)

class LoadBalancingStrategy(Enum):
    """Load balancing strategies for gRPC services"""
    ROUND_ROBIN = "round_robin"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"
    LEAST_RESPONSE_TIME = "least_response_time"
    IP_HASH = "ip_hash"
    RANDOM = "random"
    HEALTH_AWARE = "health_aware"

@dataclass
class ServerMetrics:
    """Metrics for server health and performance"""
    server_id: str
    address: str
    port: int
    active_connections: int = 0
    total_requests: int = 0
    failed_requests: int = 0
    response_times: deque = field(default_factory=lambda: deque(maxlen=100))
    last_health_check: float = field(default_factory=time.time)
    is_healthy: bool = True
    weight: int = 1
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage"""
        if self.total_requests == 0:
            return 100.0
        return ((self.total_requests - self.failed_requests) / self.total_requests) * 100
    
    @property
    def average_response_time(self) -> float:
        """Calculate average response time in milliseconds"""
        if not self.response_times:
            return 0.0
        return statistics.mean(self.response_times)

class HealthChecker:
    """Health checker for gRPC servers"""
    
    def __init__(self, check_interval: int = 30):
        self.check_interval = check_interval
        self.running = False
        self._thread: Optional[threading.Thread] = None
    
    async def check_server_health(self, address: str, port: int) -> bool:
        """Check if server is healthy"""
        try:
            # Create health check channel
            channel = grpc.aio.insecure_channel(f"{address}:{port}")
            
            # Perform health check (using grpc_health_v1)
            from grpc_health.v1 import health_pb2, health_pb2_grpc
            
            stub = health_pb2_grpc.HealthStub(channel)
            request = health_pb2.HealthCheckRequest(service="")
            
            response = await stub.Check(request, timeout=5.0)
            await channel.close()
            
            return response.status == health_pb2.HealthCheckResponse.SERVING
            
        except Exception as e:
            logger.warning(f"Health check failed for {address}:{port}: {e}")
            return False
    
    def start_monitoring(self, servers: List[ServerMetrics], callback: Callable):
        """Start health monitoring in background"""
        self.running = True
        self._thread = threading.Thread(
            target=self._monitor_loop,
            args=(servers, callback),
            daemon=True
        )
        self._thread.start()
    
    def stop_monitoring(self):
        """Stop health monitoring"""
        self.running = False
        if self._thread:
            self._thread.join()
    
    def _monitor_loop(self, servers: List[ServerMetrics], callback: Callable):
        """Background monitoring loop"""
        while self.running:
            for server in servers:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                is_healthy = loop.run_until_complete(
                    self.check_server_health(server.address, server.port)
                )
                
                if server.is_healthy != is_healthy:
                    server.is_healthy = is_healthy
                    callback(server, is_healthy)
                
                server.last_health_check = time.time()
                loop.close()
            
            time.sleep(self.check_interval)

class LoadBalancerBase(ABC):
    """Base class for load balancing strategies"""
    
    def __init__(self, servers: List[ServerMetrics]):
        self.servers = servers
        self.current_index = 0
        self._lock = threading.Lock()
    
    @abstractmethod
    def select_server(self, client_ip: Optional[str] = None) -> Optional[ServerMetrics]:
        """Select next server based on strategy"""
        pass
    
    def get_healthy_servers(self) -> List[ServerMetrics]:
        """Get list of healthy servers"""
        return [server for server in self.servers if server.is_healthy]
    
    def update_server_metrics(self, server_id: str, response_time: float, success: bool):
        """Update server metrics after request"""
        for server in self.servers:
            if server.server_id == server_id:
                server.total_requests += 1
                if not success:
                    server.failed_requests += 1
                server.response_times.append(response_time)
                break

class RoundRobinBalancer(LoadBalancerBase):
    """Round-robin load balancer"""
    
    def select_server(self, client_ip: Optional[str] = None) -> Optional[ServerMetrics]:
        healthy_servers = self.get_healthy_servers()
        if not healthy_servers:
            return None
        
        with self._lock:
            server = healthy_servers[self.current_index % len(healthy_servers)]
            self.current_index += 1
            return server

class WeightedRoundRobinBalancer(LoadBalancerBase):
    """Weighted round-robin load balancer"""
    
    def __init__(self, servers: List[ServerMetrics]):
        super().__init__(servers)
        self.weights = {server.server_id: server.weight for server in servers}
        self.current_weights = self.weights.copy()
    
    def select_server(self, client_ip: Optional[str] = None) -> Optional[ServerMetrics]:
        healthy_servers = self.get_healthy_servers()
        if not healthy_servers:
            return None
        
        with self._lock:
            # Find server with highest current weight
            selected_server = max(
                healthy_servers,
                key=lambda s: self.current_weights.get(s.server_id, 0)
            )
            
            # Decrease current weight and reset if needed
            self.current_weights[selected_server.server_id] -= 1
            if all(weight <= 0 for weight in self.current_weights.values()):
                self.current_weights = self.weights.copy()
            
            return selected_server

class LeastConnectionsBalancer(LoadBalancerBase):
    """Least connections load balancer"""
    
    def select_server(self, client_ip: Optional[str] = None) -> Optional[ServerMetrics]:
        healthy_servers = self.get_healthy_servers()
        if not healthy_servers:
            return None
        
        return min(healthy_servers, key=lambda s: s.active_connections)

class LeastResponseTimeBalancer(LoadBalancerBase):
    """Least response time load balancer"""
    
    def select_server(self, client_ip: Optional[str] = None) -> Optional[ServerMetrics]:
        healthy_servers = self.get_healthy_servers()
        if not healthy_servers:
            return None
        
        return min(healthy_servers, key=lambda s: s.average_response_time)

class IPHashBalancer(LoadBalancerBase):
    """IP hash-based load balancer for session affinity"""
    
    def select_server(self, client_ip: Optional[str] = None) -> Optional[ServerMetrics]:
        healthy_servers = self.get_healthy_servers()
        if not healthy_servers or not client_ip:
            return None
        
        # Hash client IP to select consistent server
        hash_value = int(hashlib.md5(client_ip.encode()).hexdigest(), 16)
        index = hash_value % len(healthy_servers)
        return healthy_servers[index]

class RandomBalancer(LoadBalancerBase):
    """Random load balancer"""
    
    def select_server(self, client_ip: Optional[str] = None) -> Optional[ServerMetrics]:
        healthy_servers = self.get_healthy_servers()
        if not healthy_servers:
            return None
        
        return random.choice(healthy_servers)

class HealthAwareBalancer(LoadBalancerBase):
    """Health-aware load balancer considering multiple factors"""
    
    def select_server(self, client_ip: Optional[str] = None) -> Optional[ServerMetrics]:
        healthy_servers = self.get_healthy_servers()
        if not healthy_servers:
            return None
        
        # Score servers based on multiple factors
        def calculate_score(server: ServerMetrics) -> float:
            # Lower score is better
            connection_score = server.active_connections * 0.3
            response_time_score = server.average_response_time * 0.4
            error_rate_score = (100 - server.success_rate) * 0.2
            load_score = (server.cpu_usage + server.memory_usage) * 0.1
            
            return connection_score + response_time_score + error_rate_score + load_score
        
        return min(healthy_servers, key=calculate_score)

class gRPCLoadBalancer:
    """Main gRPC Load Balancer class"""
    
    def __init__(
        self,
        servers: List[Dict[str, Any]],
        strategy: LoadBalancingStrategy = LoadBalancingStrategy.ROUND_ROBIN,
        health_check_interval: int = 30,
        enable_circuit_breaker: bool = True
    ):
        # Initialize server metrics
        self.servers = [
            ServerMetrics(
                server_id=f"{server['host']}:{server['port']}",
                address=server['host'],
                port=server['port'],
                weight=server.get('weight', 1)
            )
            for server in servers
        ]
        
        # Initialize load balancer strategy
        self.strategy = strategy
        self.balancer = self._create_balancer(strategy)
        
        # Initialize health checker
        self.health_checker = HealthChecker(health_check_interval)
        self.health_checker.start_monitoring(
            self.servers,
            self._on_health_change
        )
        
        # Circuit breaker settings
        self.enable_circuit_breaker = enable_circuit_breaker
        self.circuit_breaker_threshold = 5  # failures
        self.circuit_breaker_timeout = 60  # seconds
        self.circuit_breaker_state = defaultdict(lambda: {
            'failures': 0,
            'last_failure': 0,
            'state': 'closed'  # closed, open, half-open
        })
        
        # Connection pools
        self.channels: Dict[str, grpc.Channel] = {}
        self.channel_lock = threading.Lock()
        
        # Metrics
        self.total_requests = 0
        self.failed_requests = 0
        self.start_time = time.time()
        
        logger.info(f"gRPC Load Balancer initialized with {len(self.servers)} servers using {strategy.value} strategy")
    
    def _create_balancer(self, strategy: LoadBalancingStrategy) -> LoadBalancerBase:
        """Create load balancer based on strategy"""
        balancer_map = {
            LoadBalancingStrategy.ROUND_ROBIN: RoundRobinBalancer,
            LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN: WeightedRoundRobinBalancer,
            LoadBalancingStrategy.LEAST_CONNECTIONS: LeastConnectionsBalancer,
            LoadBalancingStrategy.LEAST_RESPONSE_TIME: LeastResponseTimeBalancer,
            LoadBalancingStrategy.IP_HASH: IPHashBalancer,
            LoadBalancingStrategy.RANDOM: RandomBalancer,
            LoadBalancingStrategy.HEALTH_AWARE: HealthAwareBalancer
        }
        
        return balancer_map[strategy](self.servers)
    
    def _on_health_change(self, server: ServerMetrics, is_healthy: bool):
        """Callback for health status changes"""
        status = "healthy" if is_healthy else "unhealthy"
        logger.info(f"Server {server.server_id} is now {status}")
        
        if not is_healthy:
            # Close connection to unhealthy server
            self._close_channel(server.server_id)
    
    def _get_channel(self, server: ServerMetrics) -> grpc.Channel:
        """Get or create gRPC channel for server"""
        server_id = server.server_id
        
        with self.channel_lock:
            if server_id not in self.channels:
                address = f"{server.address}:{server.port}"
                self.channels[server_id] = grpc.insecure_channel(address)
                logger.debug(f"Created new channel for {address}")
            
            return self.channels[server_id]
    
    def _close_channel(self, server_id: str):
        """Close channel to specific server"""
        with self.channel_lock:
            if server_id in self.channels:
                self.channels[server_id].close()
                del self.channels[server_id]
                logger.debug(f"Closed channel for {server_id}")
    
    def _check_circuit_breaker(self, server: ServerMetrics) -> bool:
        """Check if circuit breaker allows request"""
        if not self.enable_circuit_breaker:
            return True
        
        server_id = server.server_id
        breaker = self.circuit_breaker_state[server_id]
        current_time = time.time()
        
        if breaker['state'] == 'open':
            # Check if timeout period has passed
            if current_time - breaker['last_failure'] > self.circuit_breaker_timeout:
                breaker['state'] = 'half-open'
                logger.info(f"Circuit breaker for {server_id} is now half-open")
            else:
                return False
        
        return True
    
    def _update_circuit_breaker(self, server: ServerMetrics, success: bool):
        """Update circuit breaker state"""
        if not self.enable_circuit_breaker:
            return
        
        server_id = server.server_id
        breaker = self.circuit_breaker_state[server_id]
        
        if success:
            if breaker['state'] == 'half-open':
                breaker['state'] = 'closed'
                breaker['failures'] = 0
                logger.info(f"Circuit breaker for {server_id} is now closed")
        else:
            breaker['failures'] += 1
            breaker['last_failure'] = time.time()
            
            if breaker['failures'] >= self.circuit_breaker_threshold:
                breaker['state'] = 'open'
                logger.warning(f"Circuit breaker for {server_id} is now open")
    
    def get_channel(self, client_ip: Optional[str] = None) -> Optional[grpc.Channel]:
        """Get channel to best available server"""
        server = self.balancer.select_server(client_ip)
        
        if not server:
            logger.error("No healthy servers available")
            return None
        
        # Check circuit breaker
        if not self._check_circuit_breaker(server):
            logger.debug(f"Circuit breaker open for {server.server_id}")
            return None
        
        # Update connection count
        server.active_connections += 1
        
        try:
            return self._get_channel(server)
        except Exception as e:
            logger.error(f"Failed to get channel for {server.server_id}: {e}")
            server.active_connections -= 1
            return None
    
    def record_request(
        self,
        server_channel: grpc.Channel,
        response_time: float,
        success: bool,
        client_ip: Optional[str] = None
    ):
        """Record request metrics"""
        # Find server by channel
        server = None
        for s in self.servers:
            if self.channels.get(s.server_id) == server_channel:
                server = s
                break
        
        if server:
            # Update server metrics
            server.active_connections = max(0, server.active_connections - 1)
            self.balancer.update_server_metrics(server.server_id, response_time, success)
            
            # Update circuit breaker
            self._update_circuit_breaker(server, success)
        
        # Update global metrics
        self.total_requests += 1
        if not success:
            self.failed_requests += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get load balancer statistics"""
        uptime = time.time() - self.start_time
        success_rate = 0.0
        if self.total_requests > 0:
            success_rate = ((self.total_requests - self.failed_requests) / self.total_requests) * 100
        
        healthy_servers = len([s for s in self.servers if s.is_healthy])
        
        server_stats = []
        for server in self.servers:
            server_stats.append({
                'server_id': server.server_id,
                'address': f"{server.address}:{server.port}",
                'is_healthy': server.is_healthy,
                'active_connections': server.active_connections,
                'total_requests': server.total_requests,
                'failed_requests': server.failed_requests,
                'success_rate': server.success_rate,
                'average_response_time': server.average_response_time,
                'weight': server.weight,
                'circuit_breaker_state': self.circuit_breaker_state[server.server_id]['state']
            })
        
        return {
            'load_balancer': {
                'strategy': self.strategy.value,
                'uptime_seconds': uptime,
                'total_requests': self.total_requests,
                'failed_requests': self.failed_requests,
                'success_rate': success_rate,
                'total_servers': len(self.servers),
                'healthy_servers': healthy_servers
            },
            'servers': server_stats
        }
    
    def add_server(
        self,
        host: str,
        port: int,
        weight: int = 1
    ):
        """Add new server to load balancer"""
        server_id = f"{host}:{port}"
        
        # Check if server already exists
        for server in self.servers:
            if server.server_id == server_id:
                logger.warning(f"Server {server_id} already exists")
                return
        
        # Add new server
        new_server = ServerMetrics(
            server_id=server_id,
            address=host,
            port=port,
            weight=weight
        )
        
        self.servers.append(new_server)
        logger.info(f"Added new server: {server_id}")
    
    def remove_server(self, host: str, port: int):
        """Remove server from load balancer"""
        server_id = f"{host}:{port}"
        
        # Find and remove server
        for i, server in enumerate(self.servers):
            if server.server_id == server_id:
                # Close channel
                self._close_channel(server_id)
                
                # Remove from list
                del self.servers[i]
                
                # Clean up circuit breaker state
                if server_id in self.circuit_breaker_state:
                    del self.circuit_breaker_state[server_id]
                
                logger.info(f"Removed server: {server_id}")
                return
        
        logger.warning(f"Server {server_id} not found")
    
    def shutdown(self):
        """Shutdown load balancer"""
        logger.info("Shutting down gRPC Load Balancer")
        
        # Stop health monitoring
        self.health_checker.stop_monitoring()
        
        # Close all channels
        with self.channel_lock:
            for channel in self.channels.values():
                channel.close()
            self.channels.clear()

# Load balancer interceptor
class LoadBalancerInterceptor(grpc.UnaryUnaryClientInterceptor):
    """gRPC interceptor for load balancing"""
    
    def __init__(self, load_balancer: gRPCLoadBalancer):
        self.load_balancer = load_balancer
    
    def intercept_unary_unary(self, continuation, client_call_details, request):
        """Intercept unary-unary calls"""
        start_time = time.time()
        
        # Get channel from load balancer
        channel = self.load_balancer.get_channel()
        if not channel:
            raise grpc.RpcError("No healthy servers available")
        
        try:
            # Make the call
            response = continuation(client_call_details, request)
            
            # Record successful request
            response_time = (time.time() - start_time) * 1000  # ms
            self.load_balancer.record_request(channel, response_time, True)
            
            return response
            
        except Exception as e:
            # Record failed request
            response_time = (time.time() - start_time) * 1000  # ms
            self.load_balancer.record_request(channel, response_time, False)
            raise e

# Usage example
def create_load_balanced_channel(
    servers: List[Dict[str, Any]],
    strategy: LoadBalancingStrategy = LoadBalancingStrategy.ROUND_ROBIN
) -> grpc.Channel:
    """Create a load-balanced gRPC channel"""
    
    # Create load balancer
    load_balancer = gRPCLoadBalancer(servers, strategy)
    
    # Create interceptor
    interceptor = LoadBalancerInterceptor(load_balancer)
    
    # Return intercepted channel (this is a simplified example)
    # In practice, you'd need to implement a custom channel that uses the load balancer
    base_channel = load_balancer.get_channel()
    return grpc.intercept_channel(base_channel, interceptor)

# Configuration template
GRPC_LOAD_BALANCER_CONFIG = {
    "servers": [
        {"host": "localhost", "port": 50051, "weight": 2},
        {"host": "localhost", "port": 50052, "weight": 1},
        {"host": "localhost", "port": 50053, "weight": 1}
    ],
    "strategy": "round_robin",
    "health_check_interval": 30,
    "circuit_breaker": {
        "enabled": True,
        "failure_threshold": 5,
        "timeout": 60
    },
    "connection_pool": {
        "max_connections_per_server": 100,
        "idle_timeout": 300
    }
}

if __name__ == "__main__":
    # Example usage
    servers = [
        {"host": "localhost", "port": 50051, "weight": 2},
        {"host": "localhost", "port": 50052, "weight": 1},
        {"host": "localhost", "port": 50053, "weight": 1}
    ]
    
    # Create load balancer
    lb = gRPCLoadBalancer(
        servers,
        LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN,
        health_check_interval=10
    )
    
    try:
        # Simulate requests
        for i in range(10):
            channel = lb.get_channel()
            if channel:
                print(f"Request {i+1}: Using channel to server")
                # Simulate request completion
                time.sleep(0.1)
                lb.record_request(channel, 50.0, True)
        
        # Print statistics
        stats = lb.get_stats()
        print("\\nLoad Balancer Statistics:")
        print(f"Strategy: {stats['load_balancer']['strategy']}")
        print(f"Total Requests: {stats['load_balancer']['total_requests']}")
        print(f"Success Rate: {stats['load_balancer']['success_rate']:.1f}%")
        print(f"Healthy Servers: {stats['load_balancer']['healthy_servers']}/{stats['load_balancer']['total_servers']}")
        
    finally:
        lb.shutdown()