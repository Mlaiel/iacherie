#!/usr/bin/env python3
"""
🔄 Gateway Load Balancer - Enterprise API Gateway Service
=========================================================

Advanced load balancing service for enterprise API gateway.
Provides intelligent traffic distribution, health-aware routing,
and high availability load balancing strategies.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from enum import Enum
import random
import hashlib
import json

logger = logging.getLogger(__name__)


class LoadBalancingStrategy(Enum):
    """Load balancing strategy types."""
    ROUND_ROBIN = "round_robin"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_LEAST_CONNECTIONS = "weighted_least_connections"
    IP_HASH = "ip_hash"
    LEAST_RESPONSE_TIME = "least_response_time"
    RANDOM = "random"
    WEIGHTED_RANDOM = "weighted_random"
    HEALTH_AWARE = "health_aware"


@dataclass
class BackendServer:
    """Backend server configuration."""
    id: str
    host: str
    port: int
    weight: int = 1
    max_connections: int = 1000
    current_connections: int = 0
    health_status: str = "unknown"
    last_health_check: Optional[datetime] = None
    response_times: List[float] = field(default_factory=list)
    success_rate: float = 1.0
    total_requests: int = 0
    failed_requests: int = 0
    is_available: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def url(self) -> str:
        """Get server URL."""
        return f"http://{self.host}:{self.port}"

    @property
    def avg_response_time(self) -> float:
        """Get average response time."""
        if not self.response_times:
            return 0.0
        return sum(self.response_times[-100:]) / len(self.response_times[-100:])

    @property
    def connection_utilization(self) -> float:
        """Get connection utilization percentage."""
        if self.max_connections == 0:
            return 0.0
        return (self.current_connections / self.max_connections) * 100

    def add_response_time(self, response_time: float):
        """Add response time measurement."""
        self.response_times.append(response_time)
        # Keep only last 1000 measurements
        if len(self.response_times) > 1000:
            self.response_times = self.response_times[-1000:]

    def increment_connections(self):
        """Increment active connections."""
        self.current_connections += 1

    def decrement_connections(self):
        """Decrement active connections."""
        self.current_connections = max(0, self.current_connections - 1)

    def record_request(self, success: bool = True):
        """Record request result."""
        self.total_requests += 1
        if not success:
            self.failed_requests += 1
        
        # Update success rate
        if self.total_requests > 0:
            self.success_rate = 1.0 - (self.failed_requests / self.total_requests)


@dataclass
class LoadBalancerConfig:
    """Load balancer configuration."""
    strategy: LoadBalancingStrategy = LoadBalancingStrategy.ROUND_ROBIN
    health_check_interval: int = 30
    health_check_timeout: int = 5
    health_check_retries: int = 3
    unhealthy_threshold: int = 3
    healthy_threshold: int = 2
    connection_timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    sticky_sessions: bool = False
    session_cookie_name: str = "GATEWAY_SESSION"


class GatewayLoadBalancer:
    """
    🔄 Enterprise Gateway Load Balancer
    
    Provides intelligent load balancing with multiple strategies,
    health monitoring, and automatic failover capabilities.
    """

    def __init__(self, config: LoadBalancerConfig):
        """Initialize the load balancer."""
        self.config = config
        self.servers: Dict[str, BackendServer] = {}
        self.round_robin_index = 0
        self.session_affinity: Dict[str, str] = {}  # session_id -> server_id
        self.health_check_task: Optional[asyncio.Task] = None
        self.metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'load_balancer_errors': 0,
            'avg_response_time': 0.0,
            'server_failures': 0
        }
        
        logger.info("🔄 Gateway Load Balancer initialized")

    async def start(self):
        """Start the load balancer."""
        logger.info("🚀 Starting Gateway Load Balancer")
        
        # Start health check loop
        self.health_check_task = asyncio.create_task(self._health_check_loop())
        
        logger.info("✅ Gateway Load Balancer started")

    async def stop(self):
        """Stop the load balancer."""
        logger.info("🛑 Stopping Gateway Load Balancer")
        
        if self.health_check_task:
            self.health_check_task.cancel()
            try:
                await self.health_check_task
            except asyncio.CancelledError:
                pass
        
        logger.info("✅ Gateway Load Balancer stopped")

    def add_server(self, server: BackendServer):
        """Add a backend server."""
        self.servers[server.id] = server
        logger.info(f"➕ Added server: {server.id} ({server.url})")

    def remove_server(self, server_id: str):
        """Remove a backend server."""
        if server_id in self.servers:
            del self.servers[server_id]
            # Clean up session affinity
            self.session_affinity = {
                session: srv_id for session, srv_id in self.session_affinity.items()
                if srv_id != server_id
            }
            logger.info(f"➖ Removed server: {server_id}")

    def get_server_status(self) -> Dict[str, Any]:
        """Get comprehensive server status."""
        return {
            'total_servers': len(self.servers),
            'healthy_servers': len([s for s in self.servers.values() if s.health_status == 'healthy']),
            'unhealthy_servers': len([s for s in self.servers.values() if s.health_status == 'unhealthy']),
            'servers': {
                server_id: {
                    'url': server.url,
                    'health_status': server.health_status,
                    'current_connections': server.current_connections,
                    'connection_utilization': server.connection_utilization,
                    'avg_response_time': server.avg_response_time,
                    'success_rate': server.success_rate,
                    'total_requests': server.total_requests,
                    'is_available': server.is_available
                }
                for server_id, server in self.servers.items()
            },
            'metrics': self.metrics.copy()
        }

    async def select_server(self, request_data: Dict[str, Any]) -> Optional[BackendServer]:
        """Select the best server using configured strategy."""
        available_servers = [s for s in self.servers.values() if s.is_available and s.health_status in ['healthy', 'unknown']]
        
        if not available_servers:
            logger.error("❌ No available servers for load balancing")
            return None

        # Check for sticky sessions
        if self.config.sticky_sessions:
            session_id = request_data.get('session_id') or request_data.get('cookies', {}).get(self.config.session_cookie_name)
            if session_id and session_id in self.session_affinity:
                server_id = self.session_affinity[session_id]
                if server_id in self.servers and self.servers[server_id].is_available:
                    return self.servers[server_id]

        # Apply load balancing strategy
        selected_server = await self._apply_strategy(available_servers, request_data)
        
        # Update session affinity if needed
        if self.config.sticky_sessions and selected_server:
            session_id = request_data.get('session_id') or request_data.get('cookies', {}).get(self.config.session_cookie_name)
            if session_id:
                self.session_affinity[session_id] = selected_server.id

        return selected_server

    async def _apply_strategy(self, servers: List[BackendServer], request_data: Dict[str, Any]) -> Optional[BackendServer]:
        """Apply the configured load balancing strategy."""
        if not servers:
            return None

        strategy = self.config.strategy

        if strategy == LoadBalancingStrategy.ROUND_ROBIN:
            return self._round_robin(servers)
        elif strategy == LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN:
            return self._weighted_round_robin(servers)
        elif strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
            return self._least_connections(servers)
        elif strategy == LoadBalancingStrategy.WEIGHTED_LEAST_CONNECTIONS:
            return self._weighted_least_connections(servers)
        elif strategy == LoadBalancingStrategy.IP_HASH:
            return self._ip_hash(servers, request_data)
        elif strategy == LoadBalancingStrategy.LEAST_RESPONSE_TIME:
            return self._least_response_time(servers)
        elif strategy == LoadBalancingStrategy.RANDOM:
            return self._random(servers)
        elif strategy == LoadBalancingStrategy.WEIGHTED_RANDOM:
            return self._weighted_random(servers)
        elif strategy == LoadBalancingStrategy.HEALTH_AWARE:
            return self._health_aware(servers)
        else:
            return self._round_robin(servers)

    def _round_robin(self, servers: List[BackendServer]) -> BackendServer:
        """Round robin selection."""
        server = servers[self.round_robin_index % len(servers)]
        self.round_robin_index += 1
        return server

    def _weighted_round_robin(self, servers: List[BackendServer]) -> BackendServer:
        """Weighted round robin selection."""
        # Create weighted list
        weighted_servers = []
        for server in servers:
            weighted_servers.extend([server] * server.weight)
        
        if not weighted_servers:
            return servers[0]
        
        server = weighted_servers[self.round_robin_index % len(weighted_servers)]
        self.round_robin_index += 1
        return server

    def _least_connections(self, servers: List[BackendServer]) -> BackendServer:
        """Least connections selection."""
        return min(servers, key=lambda s: s.current_connections)

    def _weighted_least_connections(self, servers: List[BackendServer]) -> BackendServer:
        """Weighted least connections selection."""
        return min(servers, key=lambda s: s.current_connections / max(s.weight, 1))

    def _ip_hash(self, servers: List[BackendServer], request_data: Dict[str, Any]) -> BackendServer:
        """IP hash-based selection."""
        client_ip = request_data.get('client_ip', '127.0.0.1')
        hash_value = int(hashlib.md5(client_ip.encode()).hexdigest(), 16)
        return servers[hash_value % len(servers)]

    def _least_response_time(self, servers: List[BackendServer]) -> BackendServer:
        """Least response time selection."""
        return min(servers, key=lambda s: s.avg_response_time)

    def _random(self, servers: List[BackendServer]) -> BackendServer:
        """Random selection."""
        return random.choice(servers)

    def _weighted_random(self, servers: List[BackendServer]) -> BackendServer:
        """Weighted random selection."""
        total_weight = sum(s.weight for s in servers)
        if total_weight == 0:
            return random.choice(servers)
        
        random_value = random.uniform(0, total_weight)
        weight_sum = 0
        
        for server in servers:
            weight_sum += server.weight
            if random_value <= weight_sum:
                return server
        
        return servers[-1]

    def _health_aware(self, servers: List[BackendServer]) -> BackendServer:
        """Health-aware selection combining multiple factors."""
        def score_server(server: BackendServer) -> float:
            """Calculate server score (lower is better)."""
            health_score = 0 if server.health_status == 'healthy' else 1000
            connection_score = server.connection_utilization
            response_time_score = server.avg_response_time * 100
            success_rate_score = (1.0 - server.success_rate) * 1000
            
            return health_score + connection_score + response_time_score + success_rate_score
        
        return min(servers, key=score_server)

    async def _health_check_loop(self):
        """Background health check loop."""
        while True:
            try:
                await self._perform_health_checks()
                await asyncio.sleep(self.config.health_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"⚠️ Health check error: {e}")
                await asyncio.sleep(self.config.health_check_interval)

    async def _perform_health_checks(self):
        """Perform health checks on all servers."""
        health_check_tasks = []
        
        for server in self.servers.values():
            task = asyncio.create_task(self._check_server_health(server))
            health_check_tasks.append(task)
        
        if health_check_tasks:
            await asyncio.gather(*health_check_tasks, return_exceptions=True)

    async def _check_server_health(self, server: BackendServer):
        """Check health of a specific server."""
        try:
            # Simulate health check (in real implementation, this would be an HTTP request)
            start_time = time.time()
            
            # Simulate health check logic
            await asyncio.sleep(0.1)  # Simulate network delay
            
            response_time = time.time() - start_time
            server.add_response_time(response_time)
            
            # Update health status
            if server.health_status != 'healthy':
                logger.info(f"✅ Server {server.id} is now healthy")
            
            server.health_status = 'healthy'
            server.last_health_check = datetime.now()
            server.is_available = True
            
        except Exception as e:
            logger.warning(f"⚠️ Health check failed for server {server.id}: {e}")
            
            # Update health status
            if server.health_status == 'healthy':
                logger.warning(f"⚠️ Server {server.id} is now unhealthy")
                self.metrics['server_failures'] += 1
            
            server.health_status = 'unhealthy'
            server.last_health_check = datetime.now()
            
            # Disable server if unhealthy for too long
            if server.failed_requests >= self.config.unhealthy_threshold:
                server.is_available = False

    async def handle_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle load-balanced request."""
        start_time = time.time()
        self.metrics['total_requests'] += 1
        
        try:
            # Select server
            server = await self.select_server(request_data)
            if not server:
                self.metrics['load_balancer_errors'] += 1
                return {
                    'success': False,
                    'error': 'No available servers',
                    'status_code': 503
                }
            
            # Track connection
            server.increment_connections()
            
            try:
                # Simulate request processing
                response = await self._forward_request(server, request_data)
                
                # Record metrics
                response_time = time.time() - start_time
                server.add_response_time(response_time)
                server.record_request(success=response.get('success', True))
                
                if response.get('success', True):
                    self.metrics['successful_requests'] += 1
                else:
                    self.metrics['failed_requests'] += 1
                
                # Update average response time
                self._update_avg_response_time(response_time)
                
                return {
                    'success': True,
                    'response': response,
                    'server_id': server.id,
                    'response_time': response_time
                }
                
            finally:
                server.decrement_connections()
        
        except Exception as e:
            self.metrics['failed_requests'] += 1
            self.metrics['load_balancer_errors'] += 1
            logger.error(f"❌ Load balancer error: {e}")
            
            return {
                'success': False,
                'error': str(e),
                'status_code': 500
            }

    async def _forward_request(self, server: BackendServer, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Forward request to selected server."""
        # Simulate request forwarding
        await asyncio.sleep(0.1)  # Simulate network delay
        
        # Simulate server response
        return {
            'success': True,
            'data': request_data,
            'processed_by': server.id,
            'timestamp': datetime.now().isoformat()
        }

    def _update_avg_response_time(self, response_time: float):
        """Update average response time metric."""
        if self.metrics['total_requests'] == 1:
            self.metrics['avg_response_time'] = response_time
        else:
            # Exponential moving average
            alpha = 0.1
            self.metrics['avg_response_time'] = (
                alpha * response_time + (1 - alpha) * self.metrics['avg_response_time']
            )


async def main():
    """Example usage of the Gateway Load Balancer."""
    print("🔄 Gateway Load Balancer Example")
    print("=" * 40)
    
    # Create load balancer
    config = LoadBalancerConfig(
        strategy=LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN,
        health_check_interval=10
    )
    load_balancer = GatewayLoadBalancer(config)
    
    # Add servers
    servers = [
        BackendServer("server1", "api1.ainflue.com", 8001, weight=3),
        BackendServer("server2", "api2.ainflue.com", 8002, weight=2),
        BackendServer("server3", "api3.ainflue.com", 8003, weight=1)
    ]
    
    for server in servers:
        load_balancer.add_server(server)
    
    # Start load balancer
    await load_balancer.start()
    
    # Simulate requests
    print("\n🚀 Simulating requests...")
    for i in range(10):
        request_data = {
            'request_id': f'req_{i}',
            'client_ip': f'192.168.1.{i % 5 + 1}',
            'path': f'/api/test/{i}'
        }
        
        result = await load_balancer.handle_request(request_data)
        if result['success']:
            print(f"✅ Request {i}: routed to {result['server_id']} ({result['response_time']:.3f}s)")
        else:
            print(f"❌ Request {i}: {result['error']}")
    
    # Show status
    status = load_balancer.get_server_status()
    print(f"\n📊 Load Balancer Status:")
    print(f"   Healthy servers: {status['healthy_servers']}/{status['total_servers']}")
    print(f"   Total requests: {status['metrics']['total_requests']}")
    print(f"   Success rate: {status['metrics']['successful_requests']/status['metrics']['total_requests']*100:.1f}%")
    
    # Stop load balancer
    await load_balancer.stop()
    print("\n🛑 Load balancer stopped")


if __name__ == "__main__":
    asyncio.run(main())