"""
Load Balancer Configuration for IA-Influencer Agent Platform
===========================================================

Professional load balancing configuration management for microservices.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution of this code
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""

import os
import random
import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from pydantic import BaseSettings, Field, validator
import hashlib
import threading
from collections import defaultdict


class LoadBalancingStrategy(str, Enum):
    """Load balancing strategy types."""
    ROUND_ROBIN = "round_robin"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_LEAST_CONNECTIONS = "weighted_least_connections"
    IP_HASH = "ip_hash"
    RANDOM = "random"
    WEIGHTED_RANDOM = "weighted_random"
    CONSISTENT_HASH = "consistent_hash"
    LEAST_RESPONSE_TIME = "least_response_time"
    HEALTH_BASED = "health_based"


class HealthStatus(str, Enum):
    """Health status for backend servers."""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"


@dataclass
class BackendServer:
    """Backend server configuration."""
    id: str
    host: str
    port: int
    weight: int = 100
    max_connections: int = 1000
    current_connections: int = 0
    response_time: float = 0.0
    health_status: HealthStatus = HealthStatus.HEALTHY
    last_health_check: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def endpoint(self) -> str:
        """Get server endpoint."""
        return f"{self.host}:{self.port}"
    
    @property
    def is_available(self) -> bool:
        """Check if server is available for requests."""
        return (
            self.health_status == HealthStatus.HEALTHY and
            self.current_connections < self.max_connections
        )


@dataclass
class UpstreamConfig:
    """Upstream configuration for a group of backend servers."""
    name: str
    servers: List[BackendServer]
    strategy: LoadBalancingStrategy = LoadBalancingStrategy.ROUND_ROBIN
    health_check_enabled: bool = True
    health_check_interval: int = 30
    health_check_timeout: int = 5
    health_check_path: str = "/health"
    fail_timeout: int = 10
    max_fails: int = 3
    backup_servers: List[BackendServer] = field(default_factory=list)


class LoadBalancerConfig(BaseSettings):
    """
    Centralized load balancer configuration for microservices architecture.
    Supports multiple load balancing strategies and health checking.
    """
    
    # Global load balancing settings
    default_strategy: LoadBalancingStrategy = Field(
        LoadBalancingStrategy.ROUND_ROBIN, 
        env="LB_DEFAULT_STRATEGY"
    )
    
    # Connection settings
    max_connections_per_server: int = Field(1000, env="LB_MAX_CONNECTIONS_PER_SERVER")
    connection_timeout: int = Field(30, env="LB_CONNECTION_TIMEOUT")
    read_timeout: int = Field(60, env="LB_READ_TIMEOUT")
    keepalive_timeout: int = Field(75, env="LB_KEEPALIVE_TIMEOUT")
    
    # Health check settings
    health_check_enabled: bool = Field(True, env="LB_HEALTH_CHECK_ENABLED")
    health_check_interval: int = Field(30, env="LB_HEALTH_CHECK_INTERVAL")
    health_check_timeout: int = Field(5, env="LB_HEALTH_CHECK_TIMEOUT")
    health_check_retries: int = Field(3, env="LB_HEALTH_CHECK_RETRIES")
    health_check_path: str = Field("/health", env="LB_HEALTH_CHECK_PATH")
    
    # Failure handling
    max_fails: int = Field(3, env="LB_MAX_FAILS")
    fail_timeout: int = Field(10, env="LB_FAIL_TIMEOUT")
    retry_attempts: int = Field(3, env="LB_RETRY_ATTEMPTS")
    retry_delay: float = Field(1.0, env="LB_RETRY_DELAY")
    
    # Session persistence
    session_persistence_enabled: bool = Field(False, env="LB_SESSION_PERSISTENCE")
    session_cookie_name: str = Field("lb_session", env="LB_SESSION_COOKIE_NAME")
    session_timeout: int = Field(3600, env="LB_SESSION_TIMEOUT")
    
    # SSL/TLS settings
    ssl_enabled: bool = Field(False, env="LB_SSL_ENABLED")
    ssl_cert_path: Optional[str] = Field(None, env="LB_SSL_CERT_PATH")
    ssl_key_path: Optional[str] = Field(None, env="LB_SSL_KEY_PATH")
    ssl_ca_path: Optional[str] = Field(None, env="LB_SSL_CA_PATH")
    ssl_verify: bool = Field(True, env="LB_SSL_VERIFY")
    
    # Rate limiting
    rate_limiting_enabled: bool = Field(True, env="LB_RATE_LIMITING_ENABLED")
    rate_limit_requests: int = Field(1000, env="LB_RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(60, env="LB_RATE_LIMIT_WINDOW")
    
    # Monitoring and metrics
    metrics_enabled: bool = Field(True, env="LB_METRICS_ENABLED")
    metrics_path: str = Field("/metrics", env="LB_METRICS_PATH")
    access_log_enabled: bool = Field(True, env="LB_ACCESS_LOG_ENABLED")
    access_log_format: str = Field(
        "combined", 
        env="LB_ACCESS_LOG_FORMAT"
    )
    
    class Config:
        env_prefix = "LOAD_BALANCER_"
        case_sensitive = False


class LoadBalancer:
    """
    Production-ready load balancer implementation with multiple strategies.
    """
    
    def __init__(self, config: LoadBalancerConfig):
        self.config = config
        self.upstreams: Dict[str, UpstreamConfig] = {}
        self.counters: Dict[str, int] = defaultdict(int)
        self.session_store: Dict[str, str] = {}
        self.rate_limiter: Dict[str, List[float]] = defaultdict(list)
        self._lock = threading.Lock()
    
    def add_upstream(self, upstream: UpstreamConfig):
        """Add upstream configuration."""
        with self._lock:
            self.upstreams[upstream.name] = upstream
    
    def remove_upstream(self, name: str):
        """Remove upstream configuration."""
        with self._lock:
            if name in self.upstreams:
                del self.upstreams[name]
    
    def get_upstream(self, name: str) -> Optional[UpstreamConfig]:
        """Get upstream configuration."""
        return self.upstreams.get(name)
    
    def select_server(
        self, 
        upstream_name: str, 
        client_ip: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> Optional[BackendServer]:
        """
        Select backend server using configured load balancing strategy.
        """
        upstream = self.get_upstream(upstream_name)
        if not upstream:
            return None
        
        # Get healthy servers
        healthy_servers = [
            server for server in upstream.servers 
            if server.is_available
        ]
        
        if not healthy_servers:
            # Try backup servers if available
            healthy_servers = [
                server for server in upstream.backup_servers
                if server.is_available
            ]
        
        if not healthy_servers:
            return None
        
        # Apply load balancing strategy
        strategy_method = self._get_strategy_method(upstream.strategy)
        return strategy_method(upstream_name, healthy_servers, client_ip, session_id)
    
    def _get_strategy_method(self, strategy: LoadBalancingStrategy) -> Callable:
        """Get load balancing strategy method."""
        strategy_map = {
            LoadBalancingStrategy.ROUND_ROBIN: self._round_robin,
            LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN: self._weighted_round_robin,
            LoadBalancingStrategy.LEAST_CONNECTIONS: self._least_connections,
            LoadBalancingStrategy.WEIGHTED_LEAST_CONNECTIONS: self._weighted_least_connections,
            LoadBalancingStrategy.IP_HASH: self._ip_hash,
            LoadBalancingStrategy.RANDOM: self._random,
            LoadBalancingStrategy.WEIGHTED_RANDOM: self._weighted_random,
            LoadBalancingStrategy.CONSISTENT_HASH: self._consistent_hash,
            LoadBalancingStrategy.LEAST_RESPONSE_TIME: self._least_response_time,
            LoadBalancingStrategy.HEALTH_BASED: self._health_based,
        }
        return strategy_map.get(strategy, self._round_robin)
    
    def _round_robin(
        self, 
        upstream_name: str, 
        servers: List[BackendServer],
        client_ip: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> BackendServer:
        """Round robin load balancing."""
        with self._lock:
            counter = self.counters[upstream_name]
            server = servers[counter % len(servers)]
            self.counters[upstream_name] = (counter + 1) % len(servers)
            return server
    
    def _weighted_round_robin(
        self, 
        upstream_name: str, 
        servers: List[BackendServer],
        client_ip: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> BackendServer:
        """Weighted round robin load balancing."""
        total_weight = sum(server.weight for server in servers)
        with self._lock:
            counter = self.counters[upstream_name]
            current_weight = counter % total_weight
            self.counters[upstream_name] = counter + 1
        
        accumulated_weight = 0
        for server in servers:
            accumulated_weight += server.weight
            if current_weight < accumulated_weight:
                return server
        
        return servers[0]  # Fallback
    
    def _least_connections(
        self, 
        upstream_name: str, 
        servers: List[BackendServer],
        client_ip: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> BackendServer:
        """Least connections load balancing."""
        return min(servers, key=lambda s: s.current_connections)
    
    def _weighted_least_connections(
        self, 
        upstream_name: str, 
        servers: List[BackendServer],
        client_ip: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> BackendServer:
        """Weighted least connections load balancing."""
        return min(
            servers, 
            key=lambda s: s.current_connections / (s.weight or 1)
        )
    
    def _ip_hash(
        self, 
        upstream_name: str, 
        servers: List[BackendServer],
        client_ip: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> BackendServer:
        """IP hash load balancing."""
        if not client_ip:
            return self._round_robin(upstream_name, servers)
        
        hash_value = int(hashlib.md5(client_ip.encode()).hexdigest(), 16)
        return servers[hash_value % len(servers)]
    
    def _random(
        self, 
        upstream_name: str, 
        servers: List[BackendServer],
        client_ip: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> BackendServer:
        """Random load balancing."""
        return random.choice(servers)
    
    def _weighted_random(
        self, 
        upstream_name: str, 
        servers: List[BackendServer],
        client_ip: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> BackendServer:
        """Weighted random load balancing."""
        total_weight = sum(server.weight for server in servers)
        random_weight = random.randint(1, total_weight)
        
        accumulated_weight = 0
        for server in servers:
            accumulated_weight += server.weight
            if random_weight <= accumulated_weight:
                return server
        
        return servers[0]  # Fallback
    
    def _consistent_hash(
        self, 
        upstream_name: str, 
        servers: List[BackendServer],
        client_ip: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> BackendServer:
        """Consistent hash load balancing."""
        key = session_id or client_ip or str(time.time())
        if not key:
            return self._round_robin(upstream_name, servers)
        
        hash_value = int(hashlib.sha256(key.encode()).hexdigest(), 16)
        return servers[hash_value % len(servers)]
    
    def _least_response_time(
        self, 
        upstream_name: str, 
        servers: List[BackendServer],
        client_ip: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> BackendServer:
        """Least response time load balancing."""
        return min(servers, key=lambda s: s.response_time)
    
    def _health_based(
        self, 
        upstream_name: str, 
        servers: List[BackendServer],
        client_ip: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> BackendServer:
        """Health-based load balancing (prefer healthiest servers)."""
        healthy_servers = [s for s in servers if s.health_status == HealthStatus.HEALTHY]
        if healthy_servers:
            return self._least_response_time(upstream_name, healthy_servers)
        return servers[0]  # Fallback to any available server
    
    def update_server_stats(
        self, 
        server: BackendServer, 
        response_time: float, 
        success: bool
    ):
        """Update server statistics after request."""
        server.response_time = (server.response_time + response_time) / 2
        if success:
            server.health_status = HealthStatus.HEALTHY
        else:
            server.health_status = HealthStatus.DEGRADED
    
    def check_rate_limit(self, client_ip: str) -> bool:
        """Check if client is within rate limits."""
        if not self.config.rate_limiting_enabled:
            return True
        
        now = time.time()
        window_start = now - self.config.rate_limit_window
        
        with self._lock:
            # Clean old entries
            self.rate_limiter[client_ip] = [
                timestamp for timestamp in self.rate_limiter[client_ip]
                if timestamp > window_start
            ]
            
            # Check limit
            if len(self.rate_limiter[client_ip]) >= self.config.rate_limit_requests:
                return False
            
            # Record request
            self.rate_limiter[client_ip].append(now)
            return True


# Pre-configured upstreams for IA-Influencer Agent microservices
MICROSERVICE_UPSTREAMS = {
    "api-gateway": UpstreamConfig(
        name="api-gateway",
        servers=[
            BackendServer("api-gateway-1", "localhost", 8000, weight=100),
            BackendServer("api-gateway-2", "localhost", 8080, weight=100),
        ],
        strategy=LoadBalancingStrategy.ROUND_ROBIN
    ),
    "spotify-agent": UpstreamConfig(
        name="spotify-agent",
        servers=[
            BackendServer("spotify-agent-1", "localhost", 8001, weight=100),
            BackendServer("spotify-agent-2", "localhost", 8081, weight=100),
        ],
        strategy=LoadBalancingStrategy.LEAST_CONNECTIONS
    ),
    "content-protection": UpstreamConfig(
        name="content-protection",
        servers=[
            BackendServer("protection-1", "localhost", 8002, weight=150),
            BackendServer("protection-2", "localhost", 8082, weight=100),
        ],
        strategy=LoadBalancingStrategy.WEIGHTED_LEAST_CONNECTIONS
    ),
    "fingerprinting-engine": UpstreamConfig(
        name="fingerprinting-engine",
        servers=[
            BackendServer("fingerprint-1", "localhost", 8003, weight=200),
            BackendServer("fingerprint-2", "localhost", 8083, weight=150),
            BackendServer("fingerprint-3", "localhost", 8084, weight=100),
        ],
        strategy=LoadBalancingStrategy.LEAST_RESPONSE_TIME
    ),
    "web-crawler": UpstreamConfig(
        name="web-crawler",
        servers=[
            BackendServer("crawler-1", "localhost", 8004, weight=100),
            BackendServer("crawler-2", "localhost", 8085, weight=100),
        ],
        strategy=LoadBalancingStrategy.IP_HASH
    ),
    "monetization-engine": UpstreamConfig(
        name="monetization-engine",
        servers=[
            BackendServer("monetization-1", "localhost", 8005, weight=100),
        ],
        strategy=LoadBalancingStrategy.ROUND_ROBIN
    ),
    "notification-service": UpstreamConfig(
        name="notification-service",
        servers=[
            BackendServer("notification-1", "localhost", 8006, weight=100),
            BackendServer("notification-2", "localhost", 8086, weight=100),
        ],
        strategy=LoadBalancingStrategy.RANDOM
    ),
    "analytics-engine": UpstreamConfig(
        name="analytics-engine",
        servers=[
            BackendServer("analytics-1", "localhost", 8007, weight=100),
            BackendServer("analytics-2", "localhost", 8087, weight=100),
        ],
        strategy=LoadBalancingStrategy.CONSISTENT_HASH
    )
}


# Export configuration instance
load_balancer_config = LoadBalancerConfig()
