"""Advanced Request Router for IA Influencer Agent Platform

Provides intelligent request routing with microservices orchestration,
service mesh integration, and adaptive load distribution for content
protection, fingerprinting, and monetization services.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

# [EMOJI_REMOVED] WARNING: This code is proprietary and confidential.
Unauthorized copying, distribution, or use without explicit written
permission from Fahed Mlaiel is strictly prohibited and may result
in legal action.
"""

import asyncio
import logging
import json
import time
import hashlib
import hmac
from typing import Dict, List, Optional, Any, Tuple, Union, Callable
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from enum import Enum
import aiohttp
import aioredis
from urllib.parse import urlparse, parse_qs
import re
from ipaddress import ip_address, ip_network
import jwt
from pathlib import Path
import yaml
import consul
import etcd3
from prometheus_client import Counter, Histogram, Gauge

logger = logging.getLogger(__name__)

# Prometheus metrics for request routing
REQUESTS_ROUTED_TOTAL = Counter('requests_routed_total', 'Total requests routed', ['service', 'method', 'status'])
ROUTING_LATENCY = Histogram('routing_latency_seconds', 'Request routing latency')
SERVICE_INSTANCES_AVAILABLE = Gauge('service_instances_available', 'Available service instances', ['service'])
ROUTING_ERRORS_TOTAL = Counter('routing_errors_total', 'Total routing errors', ['error_type', 'service'])
CIRCUIT_BREAKER_STATE = Gauge('circuit_breaker_state', 'Circuit breaker state', ['service'])


class RoutingStrategy(Enum):
    """
Request routing strategies"""

    ROUND_ROBIN = "round_robin"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"
    LEAST_RESPONSE_TIME = "least_response_time"
    IP_HASH = "ip_hash"
    GEOGRAPHIC = "geographic"
    SERVICE_MESH = "service_mesh"
    AI_OPTIMIZED = "ai_optimized"


class ServiceType(Enum):
    """Platform service types"""

    FINGERPRINTING = "fingerprinting"
    PROTECTION = "protection"
    MONETIZATION = "monetization"
    AI_AGENT = "ai_agent"
    CRAWLERS = "crawlers"
    LICENSING = "licensing"
    ANALYTICS = "analytics"
    AUTHENTICATION = "authentication"


class HealthStatus(Enum):
    """Service health status"""

    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"
    UNKNOWN = "unknown"


@dataclass
class ServiceInstance:
    """Service instance configuration"""
    id: str
    service_name: str
    host: str
    port: int
    protocol: str = "https"
    weight: float = 1.0
    health_status: HealthStatus = HealthStatus.UNKNOWN
    last_health_check: Optional[datetime] = None
    response_time_ms: float = 0.0
    active_connections: int = 0
    
    # Capacity and performance
    max_connections: int = 1000
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    requests_per_second: float = 0.0
    
    # Geographic and network info
    region: str = "default"
    datacenter: str = "default"
    availability_zone: str = "default"
    
    # Service mesh integration
    service_mesh_enabled: bool = False
    sidecar_proxy_port: Optional[int] = None
    
    # Security and compliance
    tls_enabled: bool = True
    security_level: str = "standard"
    compliance_tags: List[str] = field(default_factory=list)
    
    # Metadata
    version: str = "1.0.0"
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def endpoint_url(self) -> str:
        try:
            logger.info(f"Executing endpoint_url")
            
            # Implementation for endpoint_url
            # TODO: Add specific business logic here
        try:
            logger.info(f"Executing is_healthy")
            
            # Implementation for is_healthy
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"is_healthy completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"is_healthy failed: {e}")
            raise
            result = None  # Replace with actual implementation
            
            logger.info(f"endpoint_url completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"endpoint_url failed: {e}")
            raise
    @property
    def is_healthy(self) -> bool:
        return self.health_status == HealthStatus.HEALTHY
    
    @property
    def load_score(self) -> float:
        """Calculate load score (lower is better)"""
        connection_load = self.active_connections / self.max_connections
        cpu_load = self.cpu_usage / 100.0
        memory_load = self.memory_usage / 100.0
        return (connection_load + cpu_load + memory_load) / 3.0


@dataclass
class RoutingRule:
    """
Request routing rule configuration"""
    name: str
    description: str
    enabled: bool = True
    priority: int = 100
    
    # Matching criteria
    path_patterns: List[str] = field(default_factory=list)
    methods: List[str] = field(default_factory=list)
    headers: Dict[str, str] = field(default_factory=dict)
    query_params: Dict[str, str] = field(default_factory=dict)
    source_networks: List[str] = field(default_factory=list)
    
    # Service targeting
    target_service: str = ""
    target_version: Optional[str] = None
    target_region: Optional[str] = None
    
    # Routing behavior
    routing_strategy: RoutingStrategy = RoutingStrategy.ROUND_ROBIN
    timeout_seconds: int = 30
    retries: int = 3
    retry_delay_ms: int = 100
    
    # Load balancing
    sticky_sessions: bool = False
    session_affinity_key: Optional[str] = None
    
    # Security
    authentication_required: bool = False
    authorization_rules: List[str] = field(default_factory=list)
    rate_limit: Optional[str] = None
    
    # Transformations
    request_transformations: List[Dict[str, Any]] = field(default_factory=list)
    response_transformations: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class RoutingContext:
    """Request routing context"""
    request_id: str
    client_ip: str
    user_agent: str
    method: str
    path: str
    headers: Dict[str, str]
    query_params: Dict[str, str]
    
    # Authentication context
    user_id: Optional[str] = None
    tenant_id: Optional[str] = None
    api_key: Optional[str] = None
    jwt_token: Optional[str] = None
    
    # Geographic context
    country_code: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    
    # Service context
    service_type: Optional[ServiceType] = None
    service_version: Optional[str] = None
    priority: int = 100
    
    # Performance context
    max_latency_ms: Optional[int] = None
    retry_budget: int = 3
    timeout_seconds: int = 30
    
    # Session context
    session_id: Optional[str] = None
    sticky_session_key: Optional[str] = None


class RequestRouter:
    """
    Advanced Request Router for IA Influencer Agent Platform
    
    Provides intelligent request routing with:
    - Microservices orchestration and service discovery
    - Geographic and performance-aware routing
    - Circuit breaker patterns and fault tolerance
    - Multi-tenant request isolation
    - Service mesh integration
    """
    
    def __init__(
        self,
        config_file -> None: Optional[str] = None,
        redis_client -> None: Optional[aioredis.Redis] = None,
        consul_client -> None: Optional[consul.Consul] = None,
        enable_service_discovery -> None: bool = True
    ) -> None:
        self.config_file = config_file
        self.redis_client = redis_client
        self.consul_client = consul_client
        self.enable_service_discovery = enable_service_discovery
        
        # Routing components
        self.service_instances: Dict[str, List[ServiceInstance]] = {}
        self.routing_rules: List[RoutingRule] = []
        self.routing_strategies: Dict[str, Callable] = {}
        
        # State management
        self.round_robin_counters: Dict[str, int] = {}
        self.session_affinity: Dict[str, str] = {}
        self.circuit_breakers: Dict[str, Dict[str, Any]] = {}
        
        # Performance tracking
        self.response_times: Dict[str, List[float]] = {}
        self.connection_counts: Dict[str, int] = {}
        self.health_check_results: Dict[str, Dict[str, Any]] = {}
        
        # Configuration
        self.config = {
            "default_timeout": 30,
            "default_retries": 3,
            "health_check_interval": 30,
            "circuit_breaker_threshold": 5,
            "circuit_breaker_timeout": 60,
            "session_affinity_ttl": 3600,
            "service_discovery_interval": 10,
            "enable_metrics": True,
            "enable_tracing": True
        }
        
        # Runtime state
        self._monitoring_active = False
        self._discovery_active = False
        
        logger.info("Request Router initialized for IA Influencer Agent platform")
    
    async def initialize(self) -> bool:
        """Initialize request router with platform configuration"""
        try:
            # Load configuration
            await self._load_configuration()
            
            # Initialize routing strategies
            await self._initialize_routing_strategies()
            
            # Configure platform services
            await self._configure_platform_services()
            
            # Setup routing rules
            await self._configure_routing_rules()
            
            # Start service discovery
            if self.enable_service_discovery:
                await self._start_service_discovery()
            
            # Initialize health monitoring
            await self._start_health_monitoring()
            
            # Initialize circuit breakers
            await self._initialize_circuit_breakers()
            
            logger.info("Request router initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize request router: {e}")
            return False
    
    async def _load_configuration(self) -> None:
        """Load router configuration"""
        try:
            if self.config_file and Path(self.config_file).exists():
                with open(self.config_file, 'r') as f:
                    file_config = yaml.safe_load(f)
                    self.config.update(file_config)
                logger.info(f"Configuration loaded from {self.config_file}")
            else:
                logger.info("Using default router configuration")
                
        except Exception as e:
            logger.warning(f"Failed to load configuration: {e}, using defaults")
    
    async def _initialize_routing_strategies(self) -> None:
        """Initialize routing strategy implementations"""
        try:
            self.routing_strategies = {
                RoutingStrategy.ROUND_ROBIN.value: self._route_round_robin,
                RoutingStrategy.WEIGHTED_ROUND_ROBIN.value: self._route_weighted_round_robin,
                RoutingStrategy.LEAST_CONNECTIONS.value: self._route_least_connections,
                RoutingStrategy.LEAST_RESPONSE_TIME.value: self._route_least_response_time,
                RoutingStrategy.IP_HASH.value: self._route_ip_hash,
                RoutingStrategy.GEOGRAPHIC.value: self._route_geographic,
                RoutingStrategy.SERVICE_MESH.value: self._route_service_mesh,
                RoutingStrategy.AI_OPTIMIZED.value: self._route_ai_optimized
            }
            
            logger.info("Routing strategies initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize routing strategies: {e}")
            raise
    
    async def _configure_platform_services(self) -> None:
        """Configure service instances for IA Influencer Agent platform"""
        try:
            # Fingerprinting service instances
            fingerprinting_instances = [
                ServiceInstance(
                    id="fingerprinting-1",
                    service_name="fingerprinting",
                    host="fingerprinting-1.ia-influencer.internal",
                    port=8001,
                    weight=1.0,
                    max_connections=500,
                    region="europe",
                    datacenter="eu-central-1",
                    service_mesh_enabled=True,
                    compliance_tags=["GDPR", "ISO27001"],
                    tags={"type": "audio", "ml_accelerated": "true"}
                ),
                ServiceInstance(
                    id="fingerprinting-2",
                    service_name="fingerprinting",
                    host="fingerprinting-2.ia-influencer.internal",
                    port=8001,
                    weight=1.0,
                    max_connections=500,
                    region="north_america",
                    datacenter="us-east-1",
                    service_mesh_enabled=True,
                    compliance_tags=["SOC2", "HIPAA"],
                    tags={"type": "video", "ml_accelerated": "true"}
                ),
                ServiceInstance(
                    id="fingerprinting-3",
                    service_name="fingerprinting",
                    host="fingerprinting-3.ia-influencer.internal",
                    port=8001,
                    weight=0.8,
                    max_connections=300,
                    region="asia_pacific",
                    datacenter="ap-northeast-1",
                    service_mesh_enabled=True,
                    compliance_tags=["PDPA"],
                    tags={"type": "image", "ml_accelerated": "false"}
                )
            ]
            
            # Protection service instances
            protection_instances = [
                ServiceInstance(
                    id="protection-1",
                    service_name="protection",
                    host="protection-1.ia-influencer.internal",
                    port=8002,
                    weight=1.2,
                    max_connections=800,
                    region="europe",
                    datacenter="eu-central-1",
                    service_mesh_enabled=True,
                    compliance_tags=["GDPR", "ISO27001"],
                    tags={"monitoring": "realtime", "alerts": "enabled"}
                ),
                ServiceInstance(
                    id="protection-2",
                    service_name="protection",
                    host="protection-2.ia-influencer.internal",
                    port=8002,
                    weight=1.0,
                    max_connections=600,
                    region="north_america",
                    datacenter="us-east-1",
                    service_mesh_enabled=True,
                    compliance_tags=["SOC2"],
                    tags={"monitoring": "batch", "alerts": "enabled"}
                )
            ]
            
            # Monetization service instances
            monetization_instances = [
                ServiceInstance(
                    id="monetization-1",
                    service_name="monetization",
                    host="monetization-1.ia-influencer.internal",
                    port=8003,
                    weight=1.0,
                    max_connections=1000,
                    region="europe",
                    datacenter="eu-central-1",
                    service_mesh_enabled=True,
                    security_level="high",
                    compliance_tags=["GDPR", "PSD2", "PCI_DSS"],
                    tags={"payments": "stripe", "currencies": "EUR,USD,GBP"}
                ),
                ServiceInstance(
                    id="monetization-2",
                    service_name="monetization",
                    host="monetization-2.ia-influencer.internal",
                    port=8003,
                    weight=1.0,
                    max_connections=1000,
                    region="north_america",
                    datacenter="us-east-1",
                    service_mesh_enabled=True,
                    security_level="high",
                    compliance_tags=["SOC2", "PCI_DSS"],
                    tags={"payments": "stripe,paypal", "currencies": "USD,CAD"}
                )
            ]
            
            # AI Agent service instances
            ai_agent_instances = [
                ServiceInstance(
                    id="ai-agent-1",
                    service_name="ai_agent",
                    host="ai-agent-1.ia-influencer.internal",
                    port=8004,
                    weight=1.5,
                    max_connections=2000,
                    region="europe",
                    datacenter="eu-central-1",
                    service_mesh_enabled=True,
                    tags={"ml_model": "gpt-4", "spotify_integration": "enabled", "real_time": "true"}
                ),
                ServiceInstance(
                    id="ai-agent-2",
                    service_name="ai_agent",
                    host="ai-agent-2.ia-influencer.internal",
                    port=8004,
                    weight=1.0,
                    max_connections=1500,
                    region="north_america",
                    datacenter="us-east-1",
                    service_mesh_enabled=True,
                    tags={"ml_model": "claude-3", "spotify_integration": "enabled", "real_time": "true"}
                )
            ]
            
            # Crawlers service instances
            crawler_instances = [
                ServiceInstance(
                    id="crawlers-1",
                    service_name="crawlers",
                    host="crawlers-1.ia-influencer.internal",
                    port=8005,
                    weight=1.0,
                    max_connections=200,
                    region="europe",
                    datacenter="eu-central-1",
                    tags={"platforms": "youtube,instagram", "rate_limited": "true"}
                ),
                ServiceInstance(
                    id="crawlers-2",
                    service_name="crawlers",
                    host="crawlers-2.ia-influencer.internal",
                    port=8005,
                    weight=1.0,
                    max_connections=200,
                    region="north_america",
                    datacenter="us-east-1",
                    tags={"platforms": "tiktok,twitter", "rate_limited": "true"}
                )
            ]
            
            # Licensing service instances
            licensing_instances = [
                ServiceInstance(
                    id="licensing-1",
                    service_name="licensing",
                    host="licensing-1.ia-influencer.internal",
                    port=8006,
                    weight=1.0,
                    max_connections=500,
                    region="europe",
                    datacenter="eu-central-1",
                    service_mesh_enabled=True,
                    security_level="high",
                    compliance_tags=["GDPR", "COPYRIGHT_LAW"],
                    tags={"contracts": "automated", "royalties": "realtime"}
                )
            ]
            
            self.service_instances = {
                "fingerprinting": fingerprinting_instances,
                "protection": protection_instances,
                "monetization": monetization_instances,
                "ai_agent": ai_agent_instances,
                "crawlers": crawler_instances,
                "licensing": licensing_instances
            }
            
            logger.info("Platform service instances configured")
            
        except Exception as e:
            logger.error(f"Failed to configure platform services: {e}")
            raise
    
    async def _configure_routing_rules(self) -> None:
        """Configure routing rules for platform endpoints"""
        try:
            # Fingerprinting API routes
            fingerprinting_rule = RoutingRule(
                name="fingerprinting_api",
                description="Route fingerprinting API requests",
                priority=90,
                path_patterns=["/api/v1/fingerprint/*", "/api/v1/audio/*", "/api/v1/video/*", "/api/v1/image/*"],
                methods=["POST", "PUT", "GET"],
                target_service="fingerprinting",
                routing_strategy=RoutingStrategy.LEAST_RESPONSE_TIME,
                timeout_seconds=60,
                retries=2,
                authentication_required=True,
                rate_limit="100r/m"
            )
            
            # AI Agent API routes - highest priority for real-time
            ai_agent_rule = RoutingRule(
                name="ai_agent_api",
                description="Route AI agent API requests with priority",
                priority=100,
                path_patterns=["/api/v1/agent/*", "/api/v1/recommendations/*", "/api/v1/spotify/*"],
                methods=["POST", "GET", "WebSocket"],
                target_service="ai_agent",
                routing_strategy=RoutingStrategy.LEAST_RESPONSE_TIME,
                timeout_seconds=15,
                retries=3,
                authentication_required=True,
                sticky_sessions=True,
                session_affinity_key="user_id"
            )
            
            # Protection API routes
            protection_rule = RoutingRule(
                name="protection_api",
                description="Route content protection API requests",
                priority=85,
                path_patterns=["/api/v1/protect/*", "/api/v1/monitor/*", "/api/v1/alerts/*"],
                methods=["POST", "GET", "PUT"],
                target_service="protection",
                routing_strategy=RoutingStrategy.GEOGRAPHIC,
                timeout_seconds=30,
                retries=2,
                authentication_required=True
            )
            
            # Monetization API routes - high security
            monetization_rule = RoutingRule(
                name="monetization_api",
                description="Route monetization API requests with security",
                priority=95,
                path_patterns=["/api/v1/revenue/*", "/api/v1/payments/*", "/api/v1/analytics/*"],
                methods=["POST", "GET", "PUT"],
                target_service="monetization",
                routing_strategy=RoutingStrategy.WEIGHTED_ROUND_ROBIN,
                timeout_seconds=45,
                retries=3,
                authentication_required=True,
                authorization_rules=["payment_access", "revenue_read"],
                rate_limit="50r/m"
            )
            
            # Crawler API routes - background priority
            crawler_rule = RoutingRule(
                name="crawler_api",
                description="Route crawler API requests",
                priority=70,
                path_patterns=["/api/v1/crawl/*", "/api/v1/youtube/*", "/api/v1/instagram/*"],
                methods=["POST", "GET"],
                target_service="crawlers",
                routing_strategy=RoutingStrategy.ROUND_ROBIN,
                timeout_seconds=120,
                retries=1,
                authentication_required=True,
                rate_limit="20r/m"
            )
            
            # Licensing API routes
            licensing_rule = RoutingRule(
                name="licensing_api",
                description="Route licensing API requests",
                priority=80,
                path_patterns=["/api/v1/license/*", "/api/v1/contracts/*", "/api/v1/royalties/*"],
                methods=["POST", "GET", "PUT"],
                target_service="licensing",
                routing_strategy=RoutingStrategy.LEAST_CONNECTIONS,
                timeout_seconds=30,
                retries=2,
                authentication_required=True,
                authorization_rules=["license_management"]
            )
            
            # Health check routes - no auth required
            health_rule = RoutingRule(
                name="health_checks",
                description="Route health check requests",
                priority=50,
                path_patterns=["/health", "/health/*", "/api/health", "/api/*/health"],
                methods=["GET"],
                routing_strategy=RoutingStrategy.ROUND_ROBIN,
                timeout_seconds=5,
                retries=1,
                authentication_required=False
            )
            
            self.routing_rules = [
                ai_agent_rule,
                monetization_rule,
                fingerprinting_rule,
                protection_rule,
                licensing_rule,
                crawler_rule,
                health_rule
            ]
            
            # Sort rules by priority (highest first)
            self.routing_rules.sort(key=lambda r: r.priority, reverse=True)
            
            logger.info("Routing rules configured")
            
        except Exception as e:
            logger.error(f"Failed to configure routing rules: {e}")
            raise
    
    async def route_request(self, context: RoutingContext) -> Optional[ServiceInstance]:
        """
        Route request to optimal service instance
        Returns the selected service instance or None if routing fails
        """
        try:
            start_time = time.time()
            
            # Find matching routing rule
            routing_rule = await self._find_matching_rule(context)
            if not routing_rule:
                logger.warning(f"No routing rule found for path: {context.path}")
                return None
            
            # Get target service instances
            service_instances = self.service_instances.get(routing_rule.target_service, [])
            if not service_instances:
                logger.error(f"No instances available for service: {routing_rule.target_service}")
                ROUTING_ERRORS_TOTAL.labels(
                    error_type="no_instances",
                    service=routing_rule.target_service
                ).inc()
                return None
            
            # Filter healthy instances
            healthy_instances = [
                instance for instance in service_instances
                if self._is_instance_healthy(instance)
            ]
            
            if not healthy_instances:
                logger.warning(f"No healthy instances for service: {routing_rule.target_service}")
                # Fall back to all instances if none are healthy
                healthy_instances = service_instances
            
            # Apply geographic filtering if needed
            if routing_rule.target_region:
                region_instances = [
                    instance for instance in healthy_instances
                    if instance.region == routing_rule.target_region
                ]
                if region_instances:
                    healthy_instances = region_instances
            
            # Check for session affinity
            if routing_rule.sticky_sessions and context.session_id:
                affinity_instance = await self._get_affinity_instance(
                    context.session_id,
                    routing_rule.session_affinity_key,
                    healthy_instances
                )
                if affinity_instance:
                    await self._update_routing_metrics(routing_rule.target_service, affinity_instance, start_time)
                    return affinity_instance
            
            # Apply routing strategy
            strategy_func = self.routing_strategies.get(routing_rule.routing_strategy.value)
            if not strategy_func:
                logger.warning(f"Unknown routing strategy: {routing_rule.routing_strategy}")
                strategy_func = self.routing_strategies[RoutingStrategy.ROUND_ROBIN.value]
            
            selected_instance = await strategy_func(
                healthy_instances,
                context,
                routing_rule
            )
            
            if selected_instance:
                # Update session affinity if needed
                if routing_rule.sticky_sessions and context.session_id:
                    await self._set_session_affinity(
                        context.session_id,
                        selected_instance.id
                    )
                
                # Update metrics
                await self._update_routing_metrics(routing_rule.target_service, selected_instance, start_time)
                
                logger.debug(f"Routed request to {selected_instance.id} for service {routing_rule.target_service}")
                
            return selected_instance
            
        except Exception as e:
            logger.error(f"Failed to route request: {e}")
            ROUTING_ERRORS_TOTAL.labels(
                error_type="routing_exception",
                service="unknown"
            ).inc()
            return None
    
    async def _find_matching_rule(self, context: RoutingContext) -> Optional[RoutingRule]:
        """Find the best matching routing rule for the request"""
        try:
            for rule in self.routing_rules:
                if not rule.enabled:
                    continue
                
                # Check method
                if rule.methods and context.method not in rule.methods:
                    continue
                
                # Check path patterns
                if rule.path_patterns:
                    path_matches = False
                    for pattern in rule.path_patterns:
                        if self._match_path_pattern(context.path, pattern):
                            path_matches = True
                            break
                    if not path_matches:
                        continue
                
                # Check headers
                if rule.headers:
                    headers_match = all(
                        context.headers.get(key) == value
                        for key, value in rule.headers.items()
                    )
                    if not headers_match:
                        continue
                
                # Check query parameters
                if rule.query_params:
                    params_match = all(
                        context.query_params.get(key) == value
                        for key, value in rule.query_params.items()
                    )
                    if not params_match:
                        continue
                
                # Check source networks
                if rule.source_networks:
                    network_matches = False
                    for network in rule.source_networks:
                        if self._ip_in_network(context.client_ip, network):
                            network_matches = True
                            break
                    if not network_matches:
                        continue
                
                # All conditions match
                return rule
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to find matching rule: {e}")
            return None
    
    def _match_path_pattern(self, path: str, pattern: str) -> bool:
        """Check if path matches pattern (supports wildcards)"""
        try:
            # Convert pattern to regex
            regex_pattern = pattern.replace("*", ".*").replace("?", ".")
            return re.match(f"^{regex_pattern}$", path) is not None
            
        except Exception as e:
            logger.error(f"Failed to match path pattern: {e}")
            return False
    
    def _ip_in_network(self, ip_str: str, network_str: str) -> bool:
        """Check if IP is in network"""
        try:
            ip = ip_address(ip_str)
            network = ip_network(network_str, strict=False)
            return ip in network
            
        except Exception as e:
            logger.error(f"Failed to check IP in network: {e}")
            return False
    
    def _is_instance_healthy(self, instance: ServiceInstance) -> bool:
        """Check if service instance is healthy"""
        try:
            # Check basic health status
            if instance.health_status != HealthStatus.HEALTHY:
                return False
            
            # Check circuit breaker
            circuit_state = self.circuit_breakers.get(instance.id, {})
            if circuit_state.get("state") == "open":
                # Check if circuit breaker should be reset
                if time.time() - circuit_state.get("last_failure", 0) > self.config["circuit_breaker_timeout"]:
                    circuit_state["state"] = "half_open"
                    return True
                return False
            
            # Check connection limits
            if instance.active_connections >= instance.max_connections:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to check instance health: {e}")
            return False
    
    async def _get_affinity_instance(
        self,
        session_id: str,
        affinity_key: Optional[str],
        instances: List[ServiceInstance]
    ) -> Optional[ServiceInstance]:
        """Get instance based on session affinity"""
        try:
            cache_key = f"affinity:{session_id}"
            if affinity_key:
                cache_key += f":{affinity_key}"
            
            if self.redis_client:
                instance_id = await self.redis_client.get(cache_key)
                if instance_id:
                    instance_id = instance_id.decode()
                    for instance in instances:
                        if instance.id == instance_id:
                            return instance
            
            # Check local cache
            return None
            
        except Exception as e:
            logger.error(f"Failed to get affinity instance: {e}")
            return None
    
    async def _set_session_affinity(self, session_id: str, instance_id: str) -> None:
        """Set session affinity for future requests"""
        try:
            cache_key = f"affinity:{session_id}"
            
            if self.redis_client:
                await self.redis_client.setex(
                    cache_key,
                    self.config["session_affinity_ttl"],
                    instance_id
                )
            
            # Update local cache
            self.session_affinity[session_id] = instance_id
            
        except Exception as e:
            logger.error(f"Failed to set session affinity: {e}")
    
    # Routing strategy implementations
    async def _route_round_robin(
        self,
        instances: List[ServiceInstance],
        context: RoutingContext,
        rule: RoutingRule
    ) -> Optional[ServiceInstance]:
        """Round robin routing strategy"""
        try:
            if not instances:
                return None
            
            service_key = f"{rule.target_service}:round_robin"
            counter = self.round_robin_counters.get(service_key, 0)
            
            selected_instance = instances[counter % len(instances)]
            self.round_robin_counters[service_key] = counter + 1
            
            return selected_instance
            
        except Exception as e:
            logger.error(f"Failed round robin routing: {e}")
            return instances[0] if instances else None
    
    async def _route_weighted_round_robin(
        self,
        instances: List[ServiceInstance],
        context: RoutingContext,
        rule: RoutingRule
    ) -> Optional[ServiceInstance]:
        """Weighted round robin routing strategy"""
        try:
            if not instances:
                return None
            
            # Calculate total weight
            total_weight = sum(instance.weight for instance in instances)
            if total_weight <= 0:
                return await self._route_round_robin(instances, context, rule)
            
            # Generate weighted list
            weighted_instances = []
            for instance in instances:
                weight_count = max(1, int(instance.weight * 10))
                weighted_instances.extend([instance] * weight_count)
            
            # Use round robin on weighted list
            service_key = f"{rule.target_service}:weighted_round_robin"
            counter = self.round_robin_counters.get(service_key, 0)
            
            selected_instance = weighted_instances[counter % len(weighted_instances)]
            self.round_robin_counters[service_key] = counter + 1
            
            return selected_instance
            
        except Exception as e:
            logger.error(f"Failed weighted round robin routing: {e}")
            return instances[0] if instances else None
    
    async def _route_least_connections(
        self,
        instances: List[ServiceInstance],
        context: RoutingContext,
        rule: RoutingRule
    ) -> Optional[ServiceInstance]:
        """Least connections routing strategy"""
        try:
            if not instances:
                return None
            
            # Sort by active connections (ascending)
            sorted_instances = sorted(instances, key=lambda x: x.active_connections)
            return sorted_instances[0]
            
        except Exception as e:
            logger.error(f"Failed least connections routing: {e}")
            return instances[0] if instances else None
    
    async def _route_least_response_time(
        self,
        instances: List[ServiceInstance],
        context: RoutingContext,
        rule: RoutingRule
    ) -> Optional[ServiceInstance]:
        """Least response time routing strategy"""
        try:
            if not instances:
                return None
            
            # Sort by response time (ascending)
            sorted_instances = sorted(instances, key=lambda x: x.response_time_ms)
            return sorted_instances[0]
            
        except Exception as e:
            logger.error(f"Failed least response time routing: {e}")
            return instances[0] if instances else None
    
    async def _route_ip_hash(
        self,
        instances: List[ServiceInstance],
        context: RoutingContext,
        rule: RoutingRule
    ) -> Optional[ServiceInstance]:
        """IP hash routing strategy"""
        try:
            if not instances:
                return None
            
            # Hash client IP to select instance
            ip_hash = hashlib.md5(context.client_ip.encode()).hexdigest()
            hash_value = int(ip_hash[:8], 16)
            
            selected_instance = instances[hash_value % len(instances)]
            return selected_instance
            
        except Exception as e:
            logger.error(f"Failed IP hash routing: {e}")
            return instances[0] if instances else None
    
    async def _route_geographic(
        self,
        instances: List[ServiceInstance],
        context: RoutingContext,
        rule: RoutingRule
    ) -> Optional[ServiceInstance]:
        """Geographic routing strategy"""
        try:
            if not instances:
                return None
            
            # Prefer instances in client's region
            if context.region:
                regional_instances = [
                    instance for instance in instances
                    if instance.region == context.region
                ]
                if regional_instances:
                    return await self._route_least_response_time(regional_instances, context, rule)
            
            # Fall back to least response time
            return await self._route_least_response_time(instances, context, rule)
            
        except Exception as e:
            logger.error(f"Failed geographic routing: {e}")
            return instances[0] if instances else None
    
    async def _route_service_mesh(
        self,
        instances: List[ServiceInstance],
        context: RoutingContext,
        rule: RoutingRule
    ) -> Optional[ServiceInstance]:
        """Service mesh routing strategy"""
        try:
            if not instances:
                return None
            
            # Prefer service mesh enabled instances
            mesh_instances = [
                instance for instance in instances
                if instance.service_mesh_enabled
            ]
            
            if mesh_instances:
                return await self._route_least_response_time(mesh_instances, context, rule)
            
            # Fall back to regular routing
            return await self._route_least_response_time(instances, context, rule)
            
        except Exception as e:
            logger.error(f"Failed service mesh routing: {e}")
            return instances[0] if instances else None
    
    async def _route_ai_optimized(
        self,
        instances: List[ServiceInstance],
        context: RoutingContext,
        rule: RoutingRule
    ) -> Optional[ServiceInstance]:
        """AI-optimized routing strategy combining multiple factors"""
        try:
            if not instances:
                return None
            
            # Score instances based on multiple factors
            scored_instances = []
            
            for instance in instances:
                score = 0.0
                
                # Response time score (40% weight)
                max_response_time = max(i.response_time_ms for i in instances) or 1
                response_score = 1.0 - (instance.response_time_ms / max_response_time)
                score += response_score * 0.40
                
                # Load score (30% weight)
                load_score = 1.0 - instance.load_score
                score += load_score * 0.30
                
                # Weight score (20% weight)
                max_weight = max(i.weight for i in instances) or 1
                weight_score = instance.weight / max_weight
                score += weight_score * 0.20
                
                # Health score (10% weight)
                health_score = 1.0 if instance.is_healthy else 0.0
                score += health_score * 0.10
                
                scored_instances.append((instance, score))
            
            # Sort by score (highest first)
            scored_instances.sort(key=lambda x: x[1], reverse=True)
        try:
            logger.info(f"Executing discover_services")
            
            # Implementation for discover_services
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"discover_services completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"discover_services failed: {e}")
            raise
                weight_score = instance.weight / max_weight
                score += weight_score * 0.20
                
                # Health score (10% weight)
                health_score = 1.0 if instance.is_healthy else 0.0
                score += health_score * 0.10
                
                scored_instances.append((instance, score))
            
            # Sort by score (highest first)
            scored_instances.sort(key=lambda x: x[1], reverse=True)
            
            return scored_instances[0][0]
            
        except Exception as e:
            logger.error(f"Failed AI optimized routing: {e}")
            return instances[0] if instances else None
    
    async def _start_service_discovery(self) -> None:
        """Start service discovery monitoring"""
        try:
            self._discovery_active = True
            
            async def discover_services() -> None:
                while self._discovery_active:
                    try:
                        if self.consul_client:
                            await self._update_from_consul()
                        
                        await asyncio.sleep(self.config["service_discovery_interval"])
                        
                    except Exception as e:
                        logger.error(f"Error in service discovery: {e}")
                        await asyncio.sleep(30)
            
            asyncio.create_task(discover_services())
            logger.info("Service discovery started")
            
        except Exception as e:
            logger.error(f"Failed to start service discovery: {e}")
    
    async def _update_from_consul(self) -> None:
        """Update service instances from Consul"""
        try:
            # Get services from Consul
            services = self.consul_client.health.service(
                service="ia-influencer-*",
                passing=True
            )[1]
            
            # Update service instances
            for service in services:
        try:
                    # Collect metrics
                    metrics = {
                        "timestamp": datetime.utcnow(),
                        "metric_name": "monitor_health",
                        "value": data if data else 0,
                        "tags": self._get_metric_tags()
                    }
            
                    # Store metrics
                    await self._store_metric(metrics)
            
                    # Send to monitoring system
                    if hasattr(self, 'metrics_client'):
                        await self.metrics_client.send(metrics)
            
                    logger.info(f"Metric monitor_health collected")
                    return metrics
            
                except Exception as e:
                    logger.error(f"Metric collection monitor_health failed: {e}")
                    return None
                service="ia-influencer-*",
                passing=True
            )[1]
            
            # Update service instances
            for service in services:
                service_name = service["Service"]["Service"]
                if service_name.startswith("ia-influencer-"):
                    # Extract actual service name
                    actual_service = service_name.replace("ia-influencer-", "")
                    
                    # Create or update service instance
                    instance = ServiceInstance(
                        id=service["Service"]["ID"],
                        service_name=actual_service,
                        host=service["Service"]["Address"],
                        port=service["Service"]["Port"],
                        health_status=HealthStatus.HEALTHY,
                        tags=service["Service"]["Tags"] or {},
                        metadata=service["Service"]["Meta"] or {}
                    )
                    
                    # Add to service instances
                    if actual_service not in self.service_instances:
                        self.service_instances[actual_service] = []
                    
                    # Update existing or add new
                    existing_instance = None
                    for i, existing in enumerate(self.service_instances[actual_service]):
                        if existing.id == instance.id:
                            existing_instance = i
                            break
                    
                    if existing_instance is not None:
                        self.service_instances[actual_service][existing_instance] = instance
                    else:
                        self.service_instances[actual_service].append(instance)
            
            logger.debug("Service instances updated from Consul")
            
        except Exception as e:
            logger.error(f"Failed to update from Consul: {e}")
    
    async def _start_health_monitoring(self) -> None:
        """Start health monitoring for service instances"""
        try:
            self._monitoring_active = True
            
            async def monitor_health() -> None:
                while self._monitoring_active:
                    try:
                        await self._check_all_instances_health()
                        await asyncio.sleep(self.config["health_check_interval"])
                        
                    except Exception as e:
                        logger.error(f"Error in health monitoring: {e}")
                        await asyncio.sleep(60)
            
            asyncio.create_task(monitor_health())
            logger.info("Health monitoring started")
            
        except Exception as e:
            logger.error(f"Failed to start health monitoring: {e}")
    
    async def _check_all_instances_health(self) -> None:
        """Check health of all service instances"""
        try:
            tasks = []
            
            for service_name, instances in self.service_instances.items():
                for instance in instances:
                    task = self._check_instance_health(instance)
                    tasks.append(task)
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
                
        except Exception as e:
            logger.error(f"Failed to check all instances health: {e}")
    
    async def _check_instance_health(self, instance: ServiceInstance) -> None:
        """Check health of a specific service instance"""
        try:
            start_time = time.time()
            
            health_url = f"{instance.endpoint_url}/health"
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get(health_url) as response:
                    if response.status == 200:
                        instance.health_status = HealthStatus.HEALTHY
                    else:
                        instance.health_status = HealthStatus.UNHEALTHY
            
            # Update response time
            response_time = (time.time() - start_time) * 1000
            instance.response_time_ms = response_time
            instance.last_health_check = datetime.now()
            
            # Update metrics
            SERVICE_INSTANCES_AVAILABLE.labels(service=instance.service_name).set(
                1 if instance.is_healthy else 0
            )
            
        except Exception as e:
            logger.warning(f"Health check failed for {instance.id}: {e}")
            instance.health_status = HealthStatus.UNHEALTHY
            instance.last_health_check = datetime.now()
            
            SERVICE_INSTANCES_AVAILABLE.labels(service=instance.service_name).set(0)
    
    async def _initialize_circuit_breakers(self) -> None:
        """Initialize circuit breakers for service instances"""
        try:
            for service_name, instances in self.service_instances.items():
                for instance in instances:
                    self.circuit_breakers[instance.id] = {
                        "state": "closed",
                        "failure_count": 0,
                        "last_failure": 0,
                        "last_success": time.time()
                    }
            
            logger.info("Circuit breakers initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize circuit breakers: {e}")
    
    async def _update_routing_metrics(
        self,
        service_name: str,
        instance: ServiceInstance,
        start_time: float
    ) -> None:
        """Update routing performance metrics"""
        try:
            routing_latency = time.time() - start_time
            
            ROUTING_LATENCY.observe(routing_latency)
            REQUESTS_ROUTED_TOTAL.labels(
                service=service_name,
                method="route",
                status="success"
            ).inc()
            
            # Update connection count
            instance.active_connections += 1
            
        except Exception as e:
            logger.error(f"Failed to update routing metrics: {e}")
    
    async def get_status(self) -> Dict[str, Any]:
        """Get comprehensive status of request router"""
        try:
            # Service instance statistics
            total_instances = sum(len(instances) for instances in self.service_instances.values())
            healthy_instances = sum(
                1 for instances in self.service_instances.values()
                for instance in instances
                if instance.is_healthy
            )
            
            # Service breakdown
            service_status = {}
            for service_name, instances in self.service_instances.items():
                healthy_count = sum(1 for instance in instances if instance.is_healthy)
                service_status[service_name] = {
                    "total_instances": len(instances),
                    "healthy_instances": healthy_count,
                    "health_percentage": (healthy_count / len(instances) * 100) if instances else 0,
                    "instances": [
                        {
                            "id": instance.id,
                            "host": instance.host,
                            "port": instance.port,
                            "healthy": instance.is_healthy,
                            "response_time_ms": instance.response_time_ms,
                            "active_connections": instance.active_connections,
                            "region": instance.region
                        }
                        for instance in instances
                    ]
                }
            
            # Circuit breaker status
            circuit_breaker_status = {}
            for instance_id, circuit_state in self.circuit_breakers.items():
                circuit_breaker_status[instance_id] = circuit_state["state"]
            
            return {
                "router_active": True,
                "service_discovery_active": self._discovery_active,
                "health_monitoring_active": self._monitoring_active,
                "total_instances": total_instances,
                "healthy_instances": healthy_instances,
                "overall_health_percentage": (healthy_instances / total_instances * 100) if total_instances > 0 else 0,
                "routing_rules_configured": len(self.routing_rules),
                "routing_strategies_available": len(self.routing_strategies),
                "services": service_status,
                "circuit_breakers": circuit_breaker_status,
                "session_affinity_entries": len(self.session_affinity),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get router status: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}
    
    async def shutdown(self) -> None:
        """Shutdown request router"""
        try:
            logger.info("Shutting down Request Router...")
            
            self._monitoring_active = False
            self._discovery_active = False
            
            # Clear state
            self.service_instances.clear()
            self.session_affinity.clear()
            self.circuit_breakers.clear()
            
            logger.info("Request Router shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during router shutdown: {e}")


# Platform-specific routing functions
async def route_fingerprinting_request(
    router: RequestRouter,
    client_ip: str,
    content_type: str,
    file_size_mb: float,
    user_id: str
) -> Optional[ServiceInstance]:
    """Route fingerprinting request with content-type optimization"""
    try:
        context = RoutingContext(
            request_id=f"fingerprint_{int(time.time())}",
            client_ip=client_ip,
            user_agent="IA-Influencer-Agent/1.0",
            method="POST",
            path=f"/api/v1/fingerprint/{content_type}",
            headers={"Content-Type": "multipart/form-data"},
            query_params={"type": content_type, "size": str(file_size_mb)},
            user_id=user_id,
            service_type=ServiceType.FINGERPRINTING,
            max_latency_ms=30000,  # 30s max for large files
            timeout_seconds=60
        )
        
        return await router.route_request(context)
        
    except Exception as e:
        logger.error(f"Failed to route fingerprinting request: {e}")
        return None


async def route_ai_agent_request(
    router: RequestRouter,
    client_ip: str,
    user_id: str,
    request_type: str = "recommendation",
    session_id: Optional[str] = None
) -> Optional[ServiceInstance]:
    """Route AI agent request with session affinity and low latency"""
    try:
        context = RoutingContext(
            request_id=f"ai_agent_{int(time.time())}",
            client_ip=client_ip,
            user_agent="IA-Influencer-Agent/1.0",
            method="POST",
            path=f"/api/v1/agent/{request_type}",
            headers={"Content-Type": "application/json"},
            query_params={"type": request_type},
            user_id=user_id,
            session_id=session_id,
            service_type=ServiceType.AI_AGENT,
            max_latency_ms=5000,  # 5s max for real-time
            timeout_seconds=15,
            priority=100  # Highest priority
        )
        
        return await router.route_request(context)
        
    except Exception as e:
        logger.error(f"Failed to route AI agent request: {e}")
        return None


async def route_monetization_request(
    router: RequestRouter,
    client_ip: str,
    user_id: str,
    operation: str = "payment",
    region: Optional[str] = None
) -> Optional[ServiceInstance]:
    """Route monetization request with security and compliance"""
    try:
        context = RoutingContext(
            request_id=f"monetization_{int(time.time())}",
            client_ip=client_ip,
            user_agent="IA-Influencer-Agent/1.0",
            method="POST",
            path=f"/api/v1/{operation}",
            headers={"Content-Type": "application/json"},
            query_params={"operation": operation},
            user_id=user_id,
            region=region,
            service_type=ServiceType.MONETIZATION,
            max_latency_ms=10000,  # 10s max for payments
            timeout_seconds=45,
            priority=95  # High priority for payments
        )
        
        return await router.route_request(context)
        
    except Exception as e:
        logger.error(f"Failed to route monetization request: {e}")
        return None

# File has syntax issues - needs manual review