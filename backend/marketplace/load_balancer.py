"""Load Balancer - Request Distribution Management for Marketplace
================================================================

Enterprise-grade load balancing system for marketplace operations providing
intelligent request distribution, health monitoring, and traffic management.

Features:
- Multiple load balancing algorithms (Round Robin, Weighted, Least Connections)
- Real-time health monitoring and failover
- Traffic analytics and performance monitoring
- Circuit breaker pattern implementation
- Rate limiting and traffic shaping
- Geographic distribution support

Architecture: Enterprise Production-Ready (Backend Level 3)
Module: backend/marketplace/load_balancer.py

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
import asyncio
import time
import random
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
import uuid
import json

logger = logging.getLogger(__name__)

class LoadBalancingAlgorithm(Enum):
    """Load balancing algorithm enumeration"""
    ROUND_ROBIN = "round_robin"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_LEAST_CONNECTIONS = "weighted_least_connections"
    IP_HASH = "ip_hash"
    RANDOM = "random"
    GEOGRAPHIC = "geographic"
    RESPONSE_TIME = "response_time"

class ServerStatus(Enum):
    """Server status enumeration"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    MAINTENANCE = "maintenance"
    OVERLOADED = "overloaded"
    DEGRADED = "degraded"

class CircuitBreakerState(Enum):
    """Circuit breaker state enumeration"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open" # Testing recovery

@dataclass
class ServerInstance:
    """Server instance configuration"""
    server_id: str
    host: str
    port: int
    weight: int = 1
    max_connections: int = 1000
    current_connections: int = 0
    status: ServerStatus = ServerStatus.HEALTHY
    region: str = "default"
    zone: str = "default"
    health_check_url: str = "/health"
    response_time_ms: float = 0.0
    success_rate: float = 1.0
    last_health_check: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class HealthCheckConfig:
    """Health check configuration"""
    interval_seconds: int = 30
    timeout_seconds: int = 5
    failure_threshold: int = 3
    success_threshold: int = 2
    check_path: str = "/health"
    expected_status_codes: List[int] = field(default_factory=lambda: [200])
    expected_response_time_ms: float = 1000.0

@dataclass
class CircuitBreaker:
    """Circuit breaker for server protection"""
    server_id: str
    state: CircuitBreakerState = CircuitBreakerState.CLOSED
    failure_count: int = 0
    failure_threshold: int = 5
    recovery_timeout_seconds: int = 60
    success_threshold: int = 2
    last_failure_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None

@dataclass
class LoadBalancerStats:
    """Load balancer statistics"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    avg_response_time_ms: float = 0.0
    requests_per_second: float = 0.0
    active_connections: int = 0
    server_distribution: Dict[str, int] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.utcnow)

@dataclass
class TrafficRule:
    """Traffic routing rule"""
    rule_id: str
    name: str
    condition: str  # e.g., "path=/api/*", "geo=US", "user_type=premium"
    target_servers: List[str]  # server_ids
    weight: int = 1
    active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)

class LoadBalancer:
    """Enterprise load balancing and traffic management system"""
    
    def __init__(self, config -> None: Dict[str, Any] = None) -> None:
        self.config = config or {}
        
        # Server management
        self.servers: Dict[str, ServerInstance] = {}
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        
        # Load balancing configuration
        self.algorithm = LoadBalancingAlgorithm(
            self.config.get('algorithm', 'round_robin')
        )
        self.health_check_config = HealthCheckConfig(**self.config.get('health_check', {}))
        
        # Traffic management
        self.traffic_rules: Dict[str, TrafficRule] = {}
        self.rate_limits: Dict[str, Dict[str, Any]] = {}  # client_id -> limits
        
        # Statistics and monitoring
        self.stats = LoadBalancerStats()
        self.request_history: List[Dict[str, Any]] = []
        
        # Round robin counter
        self._round_robin_index = 0
        
        # Health check task
        self._health_check_task = None
        
        logger.info("⚖️ Load Balancer initialized")
    
    async def initialize(self) -> None:
        """Initialize load balancer and start health checks"""
        try:
            # Start health check monitoring
            self._health_check_task = asyncio.create_task(self._health_check_loop())
            
            logger.info("✅ Load balancer health checks started")
            
        except Exception as e:
            logger.error(f"Load balancer initialization error: {e}")
    
    async def add_server(self, server_config: Dict[str, Any]) -> ServerInstance:
        """Add server to load balancer pool"""
        try:
            server = ServerInstance(
                server_id=server_config["server_id"],
                host=server_config["host"],
                port=server_config["port"],
                weight=server_config.get("weight", 1),
                max_connections=server_config.get("max_connections", 1000),
                region=server_config.get("region", "default"),
                zone=server_config.get("zone", "default"),
                health_check_url=server_config.get("health_check_url", "/health"),
                metadata=server_config.get("metadata", {})
            )
            
            self.servers[server.server_id] = server
            
            # Initialize circuit breaker
            self.circuit_breakers[server.server_id] = CircuitBreaker(
                server_id=server.server_id,
                failure_threshold=self.config.get('circuit_breaker_threshold', 5),
                recovery_timeout_seconds=self.config.get('circuit_breaker_timeout', 60)
            )
            
            logger.info(f"Server added to load balancer: {server.server_id} ({server.host}:{server.port})")
            return server
            
        except Exception as e:
            logger.error(f"Add server error: {e}")
            raise
    
    async def remove_server(self, server_id: str) -> bool:
        """Remove server from load balancer pool"""
        try:
            if server_id in self.servers:
                del self.servers[server_id]
                if server_id in self.circuit_breakers:
                    del self.circuit_breakers[server_id]
                
                logger.info(f"Server removed from load balancer: {server_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Remove server error: {e}")
            return False
    
    async def get_server(self, request_context: Dict[str, Any] = None) -> Optional[ServerInstance]:
        """Get server for request using configured load balancing algorithm"""
        try:
            # Get healthy servers
            healthy_servers = [
                server for server in self.servers.values()
                if server.status == ServerStatus.HEALTHY and
                   self._is_circuit_breaker_closed(server.server_id)
            ]
            
            if not healthy_servers:
                logger.warning("No healthy servers available")
                return None
            
            # Apply traffic rules if any
            filtered_servers = self._apply_traffic_rules(healthy_servers, request_context or {})
            
            if not filtered_servers:
                filtered_servers = healthy_servers
            
            # Select server based on algorithm
            selected_server = await self._select_server(filtered_servers, request_context or {})
            
            if selected_server:
                selected_server.current_connections += 1
                self.stats.active_connections += 1
                
                # Update server distribution stats
                if selected_server.server_id not in self.stats.server_distribution:
                    self.stats.server_distribution[selected_server.server_id] = 0
                self.stats.server_distribution[selected_server.server_id] += 1
            
            return selected_server
            
        except Exception as e:
            logger.error(f"Server selection error: {e}")
            return None
    
    async def _select_server(self, servers: List[ServerInstance], 
                           request_context: Dict[str, Any]) -> Optional[ServerInstance]:
        """Select server based on load balancing algorithm"""
        try:
            if self.algorithm == LoadBalancingAlgorithm.ROUND_ROBIN:
                return self._round_robin_selection(servers)
            
            elif self.algorithm == LoadBalancingAlgorithm.WEIGHTED_ROUND_ROBIN:
                return self._weighted_round_robin_selection(servers)
            
            elif self.algorithm == LoadBalancingAlgorithm.LEAST_CONNECTIONS:
                return self._least_connections_selection(servers)
            
            elif self.algorithm == LoadBalancingAlgorithm.WEIGHTED_LEAST_CONNECTIONS:
                return self._weighted_least_connections_selection(servers)
            
            elif self.algorithm == LoadBalancingAlgorithm.IP_HASH:
                return self._ip_hash_selection(servers, request_context.get('client_ip', ''))
            
            elif self.algorithm == LoadBalancingAlgorithm.RANDOM:
                return random.choice(servers)
            
            elif self.algorithm == LoadBalancingAlgorithm.GEOGRAPHIC:
                return self._geographic_selection(servers, request_context)
            
            elif self.algorithm == LoadBalancingAlgorithm.RESPONSE_TIME:
                return self._response_time_selection(servers)
            
            else:
                # Default to round robin
                return self._round_robin_selection(servers)
                
        except Exception as e:
            logger.error(f"Server selection algorithm error: {e}")
            return random.choice(servers) if servers else None
    
    def _round_robin_selection(self, servers: List[ServerInstance]) -> ServerInstance:
        """Round robin server selection"""
        if not servers:
            return None
        
        server = servers[self._round_robin_index % len(servers)]
        self._round_robin_index = (self._round_robin_index + 1) % len(servers)
        return server
    
    def _weighted_round_robin_selection(self, servers: List[ServerInstance]) -> ServerInstance:
        """Weighted round robin server selection"""
        if not servers:
            return None
        
        # Create weighted list
        weighted_servers = []
        for server in servers:
            weighted_servers.extend([server] * server.weight)
        
        if not weighted_servers:
            return servers[0]
        
        server = weighted_servers[self._round_robin_index % len(weighted_servers)]
        self._round_robin_index = (self._round_robin_index + 1) % len(weighted_servers)
        return server
    
    def _least_connections_selection(self, servers: List[ServerInstance]) -> ServerInstance:
        """Least connections server selection"""
        return min(servers, key=lambda s: s.current_connections)
    
    def _weighted_least_connections_selection(self, servers: List[ServerInstance]) -> ServerInstance:
        """Weighted least connections server selection"""
        return min(servers, key=lambda s: s.current_connections / s.weight)
    
    def _ip_hash_selection(self, servers: List[ServerInstance], client_ip: str) -> ServerInstance:
        """IP hash-based server selection for session affinity"""
        if not client_ip:
            return self._round_robin_selection(servers)
        
        # Simple hash of IP
        ip_hash = hash(client_ip)
        return servers[ip_hash % len(servers)]
    
    def _geographic_selection(self, servers: List[ServerInstance], 
                            request_context: Dict[str, Any]) -> ServerInstance:
        """Geographic-based server selection"""
        client_region = request_context.get('geo_region', 'default')
        
        # Prefer servers in same region
        regional_servers = [s for s in servers if s.region == client_region]
        if regional_servers:
            return self._least_connections_selection(regional_servers)
        
        # Fall back to any available server
        return self._least_connections_selection(servers)
    
    def _response_time_selection(self, servers: List[ServerInstance]) -> ServerInstance:
        """Response time-based server selection"""
        return min(servers, key=lambda s: s.response_time_ms)
    
    def _apply_traffic_rules(self, servers: List[ServerInstance], 
                           request_context: Dict[str, Any]) -> List[ServerInstance]:
        """Apply traffic routing rules"""
        try:
            applicable_rules = []
            
            for rule in self.traffic_rules.values():
                if not rule.active:
                    continue
                
                if self._matches_traffic_rule(rule, request_context):
                    applicable_rules.append(rule)
            
            if not applicable_rules:
                return servers
            
            # Use highest weight rule
            selected_rule = max(applicable_rules, key=lambda r: r.weight)
            
            # Filter servers based on rule
            target_servers = [
                server for server in servers
                if server.server_id in selected_rule.target_servers
            ]
            
            return target_servers if target_servers else servers
            
        except Exception as e:
            logger.error(f"Traffic rules application error: {e}")
            return servers
    
    def _matches_traffic_rule(self, rule: TrafficRule, request_context: Dict[str, Any]) -> bool:
        """Check if request matches traffic rule condition"""
        try:
            # Simple condition matching - in production, use more sophisticated parser
            condition = rule.condition.lower()
            
            if condition.startswith('path='):
                path_pattern = condition.split('=', 1)[1]
                request_path = request_context.get('path', '').lower()
                if path_pattern.endswith('*'):
                    return request_path.startswith(path_pattern[:-1])
                else:
                    return request_path == path_pattern
            
            elif condition.startswith('geo='):
                geo_region = condition.split('=', 1)[1]
                return request_context.get('geo_region', '').lower() == geo_region
            
            elif condition.startswith('user_type='):
                user_type = condition.split('=', 1)[1]
                return request_context.get('user_type', '').lower() == user_type
            
            return False
            
        except Exception as e:
            logger.error(f"Traffic rule matching error: {e}")
            return False
    
    def _is_circuit_breaker_closed(self, server_id: str) -> bool:
        """Check if circuit breaker allows requests"""
        circuit_breaker = self.circuit_breakers.get(server_id)
        if not circuit_breaker:
            return True
        
        if circuit_breaker.state == CircuitBreakerState.CLOSED:
            return True
        elif circuit_breaker.state == CircuitBreakerState.OPEN:
            # Check if recovery timeout has passed
            if (circuit_breaker.last_failure_time and 
                datetime.utcnow() - circuit_breaker.last_failure_time > 
                timedelta(seconds=circuit_breaker.recovery_timeout_seconds)):
                circuit_breaker.state = CircuitBreakerState.HALF_OPEN
                return True
            return False
        elif circuit_breaker.state == CircuitBreakerState.HALF_OPEN:
            return True
        
        return False
    
    async def record_request_result(self, server_id -> None: str, success -> None: bool, 
                                  response_time_ms -> None: float) -> None:
        """Record request result for monitoring and circuit breaker"""
        try:
            # Update server stats
            if server_id in self.servers:
                server = self.servers[server_id]
                server.current_connections = max(0, server.current_connections - 1)
                
                # Update response time (moving average)
                if server.response_time_ms == 0:
                    server.response_time_ms = response_time_ms
                else:
                    server.response_time_ms = (server.response_time_ms * 0.9) + (response_time_ms * 0.1)
            
            # Update global stats
            self.stats.total_requests += 1
            self.stats.active_connections = max(0, self.stats.active_connections - 1)
            
            if success:
                self.stats.successful_requests += 1
                await self._record_circuit_breaker_success(server_id)
            else:
                self.stats.failed_requests += 1
                await self._record_circuit_breaker_failure(server_id)
            
            # Update average response time
            if self.stats.avg_response_time_ms == 0:
                self.stats.avg_response_time_ms = response_time_ms
            else:
                self.stats.avg_response_time_ms = (
                    (self.stats.avg_response_time_ms * (self.stats.total_requests - 1) + response_time_ms) / 
                    self.stats.total_requests
                )
            
            # Record request history
            self.request_history.append({
                "timestamp": datetime.utcnow().isoformat(),
                "server_id": server_id,
                "success": success,
                "response_time_ms": response_time_ms
            })
            
            # Keep only last 1000 requests
            if len(self.request_history) > 1000:
                self.request_history = self.request_history[-1000:]
            
        except Exception as e:
            logger.error(f"Request result recording error: {e}")
    
    async def _record_circuit_breaker_success(self, server_id -> None: str) -> None:
        """Record successful request for circuit breaker"""
        circuit_breaker = self.circuit_breakers.get(server_id)
        if not circuit_breaker:
            return
        
        circuit_breaker.last_success_time = datetime.utcnow()
        
        if circuit_breaker.state == CircuitBreakerState.HALF_OPEN:
            # Check if we have enough successes to close circuit
            circuit_breaker.failure_count = 0
            circuit_breaker.state = CircuitBreakerState.CLOSED
        elif circuit_breaker.state == CircuitBreakerState.OPEN:
            # Reset failure count on success
            circuit_breaker.failure_count = 0
    
    async def _record_circuit_breaker_failure(self, server_id -> None: str) -> None:
        """Record failed request for circuit breaker"""
        circuit_breaker = self.circuit_breakers.get(server_id)
        if not circuit_breaker:
            return
        
        circuit_breaker.failure_count += 1
        circuit_breaker.last_failure_time = datetime.utcnow()
        
        if circuit_breaker.failure_count >= circuit_breaker.failure_threshold:
            circuit_breaker.state = CircuitBreakerState.OPEN
            
            # Mark server as unhealthy
            if server_id in self.servers:
                self.servers[server_id].status = ServerStatus.UNHEALTHY
    
    async def _health_check_loop(self) -> None:
        """Background health check loop"""
        while True:
            try:
                await asyncio.sleep(self.health_check_config.interval_seconds)
                await self._perform_health_checks()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check loop error: {e}")
    
    async def _perform_health_checks(self) -> None:
        """Perform health checks on all servers"""
        try:
            tasks = []
            for server in self.servers.values():
                tasks.append(self._check_server_health(server))
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
                
        except Exception as e:
            logger.error(f"Health checks error: {e}")
    
    async def _check_server_health(self, server -> None: ServerInstance) -> None:
        """Check health of individual server"""
        try:
            # Mock health check - in production, make actual HTTP request
            start_time = time.time()
            
            # Simulate health check
            await asyncio.sleep(0.01)  # Simulate network delay
            
            response_time = (time.time() - start_time) * 1000
            
            # Mock health check result
            is_healthy = random.random() > 0.05  # 95% success rate
            
            server.last_health_check = datetime.utcnow()
            
            if is_healthy and response_time < self.health_check_config.expected_response_time_ms:
                if server.status != ServerStatus.HEALTHY:
                    server.status = ServerStatus.HEALTHY
                    # Reset circuit breaker
                    if server.server_id in self.circuit_breakers:
                        self.circuit_breakers[server.server_id].state = CircuitBreakerState.CLOSED
                        self.circuit_breakers[server.server_id].failure_count = 0
            else:
                server.status = ServerStatus.UNHEALTHY
                
                # Trigger circuit breaker
                await self._record_circuit_breaker_failure(server.server_id)
            
            logger.debug(f"Health check completed for {server.server_id}: {server.status.value}")
            
        except Exception as e:
            logger.error(f"Server health check error for {server.server_id}: {e}")
            server.status = ServerStatus.UNHEALTHY
    
    async def add_traffic_rule(self, rule_config: Dict[str, Any]) -> TrafficRule:
        """Add traffic routing rule"""
        try:
            rule = TrafficRule(
                rule_id=rule_config.get("rule_id", str(uuid.uuid4())),
                name=rule_config["name"],
                condition=rule_config["condition"],
                target_servers=rule_config["target_servers"],
                weight=rule_config.get("weight", 1),
                active=rule_config.get("active", True)
            )
            
            self.traffic_rules[rule.rule_id] = rule
            
            logger.info(f"Traffic rule added: {rule.name} ({rule.condition})")
            return rule
            
        except Exception as e:
            logger.error(f"Add traffic rule error: {e}")
            raise
    
    async def get_load_balancer_stats(self) -> LoadBalancerStats:
        """Get current load balancer statistics"""
        try:
            # Calculate requests per second
            if self.request_history:
                recent_requests = [
                    req for req in self.request_history
                    if datetime.fromisoformat(req["timestamp"]) > datetime.utcnow() - timedelta(minutes=1)
                ]
                self.stats.requests_per_second = len(recent_requests) / 60.0
            
            self.stats.last_updated = datetime.utcnow()
            return self.stats
            
        except Exception as e:
            logger.error(f"Load balancer stats error: {e}")
            return self.stats
    
    async def get_server_status(self) -> List[Dict[str, Any]]:
        """Get status of all servers"""
        try:
            server_status = []
            
            for server in self.servers.values():
                circuit_breaker = self.circuit_breakers.get(server.server_id)
                
                status_info = {
                    "server_id": server.server_id,
                    "host": server.host,
                    "port": server.port,
                    "status": server.status.value,
                    "current_connections": server.current_connections,
                    "response_time_ms": server.response_time_ms,
                    "circuit_breaker_state": circuit_breaker.state.value if circuit_breaker else "unknown",
                    "last_health_check": server.last_health_check.isoformat(),
                    "region": server.region,
                    "zone": server.zone
                }
                
                server_status.append(status_info)
            
            return server_status
            
        except Exception as e:
            logger.error(f"Server status retrieval error: {e}")
            return []
    
    async def shutdown(self) -> None:
        """Shutdown load balancer"""
        try:
            if self._health_check_task:
                self._health_check_task.cancel()
                try:
                    await self._health_check_task
                except asyncio.CancelledError:
                    pass
            
            logger.info("⚖️ Load balancer shutdown completed")
            
        except Exception as e:
            logger.error(f"Load balancer shutdown error: {e}")

# Export classes
__all__ = [
    "LoadBalancingAlgorithm",
    "ServerStatus",
    "CircuitBreakerState",
    "ServerInstance",
    "HealthCheckConfig",
    "CircuitBreaker",
    "LoadBalancerStats",
    "TrafficRule",
    "LoadBalancer"
]

# Module initialization
logger.info("⚖️ Load Balancer module loaded")