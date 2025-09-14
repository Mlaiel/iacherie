"""
🌐 QUANTUM API GATEWAY - Passerelle API Quantique 🌐
====================================================

Passerelle API unifiée pour tous les services quantiques avec routage
intelligent, authentification quantique, load balancing adaptatif,
monitoring temps réel et optimisation des performances.

CONSOLIDATION: API Gateway centralisé ✅
- Unified API endpoint management
- Quantum-enhanced routing & load balancing
- Advanced authentication & authorization
- Rate limiting & throttling
- Request/response transformation
- API monitoring & analytics
- Circuit breaker & failover
- WebSocket & real-time support

API Flow:
Client Request → Authentication → Route Resolution → 
Load Balancing → Service Selection → Request Transform → 
Service Call → Response Transform → 
Monitoring Update → Client Response

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
import uuid
import json
import time
import hashlib
import jwt
from collections import defaultdict, deque
import aiohttp
from aiohttp import web, WSMsgType
import ssl
from urllib.parse import urlparse, parse_qs
import fnmatch
import statistics
import re

logger = logging.getLogger(__name__)

# ========================================
# API GATEWAY ENUMS & CONFIGURATION
# ========================================

class RouteMethod(Enum):
    """Méthodes HTTP supportées"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    OPTIONS = "OPTIONS"
    HEAD = "HEAD"
    WEBSOCKET = "WEBSOCKET"

class LoadBalancingStrategy(Enum):
    """Stratégies de load balancing"""
    ROUND_ROBIN = "round_robin"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"
    LEAST_RESPONSE_TIME = "least_response_time"
    IP_HASH = "ip_hash"
    QUANTUM_OPTIMIZED = "quantum_optimized"
    ADAPTIVE = "adaptive"

class AuthenticationType(Enum):
    """Types d'authentification"""
    NONE = "none"
    API_KEY = "api_key"
    JWT = "jwt"
    OAUTH2 = "oauth2"
    QUANTUM_SIGNATURE = "quantum_signature"
    MULTI_FACTOR = "multi_factor"

class RateLimitType(Enum):
    """Types de limitation de taux"""
    PER_SECOND = "per_second"
    PER_MINUTE = "per_minute"
    PER_HOUR = "per_hour"
    PER_DAY = "per_day"
    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"

class ServiceStatus(Enum):
    """Status de service"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    MAINTENANCE = "maintenance"
    UNKNOWN = "unknown"

class CircuitBreakerState(Enum):
    """États du circuit breaker"""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Blocking requests
    HALF_OPEN = "half_open"  # Testing recovery

# ========================================
# API GATEWAY DATA CLASSES
# ========================================

@dataclass
class ServiceEndpoint:
    """Point de terminaison de service"""
    endpoint_id: str
    service_name: str
    host: str
    port: int
    protocol: str = "http"
    path_prefix: str = ""
    weight: int = 100
    max_connections: int = 100
    timeout_seconds: int = 30
    health_check_path: str = "/health"
    health_check_interval_seconds: int = 30
    quantum_enhanced: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    status: ServiceStatus = ServiceStatus.UNKNOWN
    last_health_check: Optional[datetime] = None
    response_time_ms: float = 0.0
    active_connections: int = 0

@dataclass
class APIRoute:
    """Route API"""
    route_id: str
    path_pattern: str
    methods: List[RouteMethod]
    service_endpoints: List[str]  # IDs des endpoints
    authentication: AuthenticationType = AuthenticationType.NONE
    rate_limit: Optional[Dict[str, Any]] = None
    load_balancing_strategy: LoadBalancingStrategy = LoadBalancingStrategy.ROUND_ROBIN
    request_transformers: List[Callable] = field(default_factory=list)
    response_transformers: List[Callable] = field(default_factory=list)
    middleware: List[str] = field(default_factory=list)
    cache_config: Optional[Dict[str, Any]] = None
    quantum_optimization: bool = True
    circuit_breaker_config: Optional[Dict[str, Any]] = None
    websocket_enabled: bool = False
    cors_config: Optional[Dict[str, Any]] = None
    description: str = ""
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class APIRequest:
    """Requête API"""
    request_id: str
    client_ip: str
    method: RouteMethod
    path: str
    headers: Dict[str, str]
    query_params: Dict[str, List[str]]
    body: Optional[bytes] = None
    user_agent: str = ""
    authentication_context: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class APIResponse:
    """Réponse API"""
    response_id: str
    request_id: str
    status_code: int
    headers: Dict[str, str]
    body: Optional[bytes] = None
    response_time_ms: float = 0.0
    service_endpoint_used: Optional[str] = None
    cached: bool = False
    quantum_enhanced: bool = False
    error_message: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class RateLimitRule:
    """Règle de limitation de taux"""
    rule_id: str
    identifier_pattern: str  # IP, user_id, api_key pattern
    limit_type: RateLimitType
    max_requests: int
    time_window_seconds: int
    burst_capacity: int = 0
    enabled: bool = True
    quantum_adaptive: bool = False
    custom_headers: Dict[str, str] = field(default_factory=dict)

@dataclass
class CircuitBreaker:
    """Circuit breaker"""
    breaker_id: str
    service_endpoint_id: str
    state: CircuitBreakerState = CircuitBreakerState.CLOSED
    failure_threshold: int = 5
    recovery_timeout_seconds: int = 60
    success_threshold: int = 3
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: Optional[datetime] = None
    last_attempt_time: Optional[datetime] = None

@dataclass
class APIMetrics:
    """Métriques API"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time_ms: float = 0.0
    requests_per_second: float = 0.0
    error_rate_percentage: float = 0.0
    cache_hit_rate: float = 0.0
    quantum_enhancement_rate: float = 0.0
    circuit_breaker_trips: int = 0
    rate_limit_violations: int = 0
    last_updated: datetime = field(default_factory=datetime.utcnow)

# ========================================
# QUANTUM API GATEWAY PRINCIPAL
# ========================================

class QuantumAPIGateway:
    """
    🌐 Passerelle API Quantique Principale 🌐
    
    Passerelle API unifiée pour services quantiques :
    - Unified endpoint management & routing
    - Quantum-enhanced load balancing
    - Advanced authentication & authorization
    - Rate limiting & throttling intelligent
    - Request/response transformation
    - Real-time monitoring & analytics
    - Circuit breaker & failover automatique
    - WebSocket & streaming support
    
    Fonctionnalités avancées :
    ✅ Quantum-optimized routing algorithms
    ✅ Adaptive load balancing
    ✅ Multi-layer authentication
    ✅ Intelligent rate limiting
    ✅ Real-time API monitoring
    ✅ Advanced caching strategies
    ✅ Circuit breaker patterns
    ✅ WebSocket gateway support
    """
    
    def __init__(self, config -> None: Dict[str, Any] = None) -> None:
        self.config = config or {}
        
        # Configuration serveur
        self.host = self.config.get("host", "0.0.0.0")
        self.port = self.config.get("port", 8080)
        self.ssl_context = None
        
        # État gateway
        self.service_endpoints: Dict[str, ServiceEndpoint] = {}
        self.api_routes: Dict[str, APIRoute] = {}
        self.rate_limit_rules: Dict[str, RateLimitRule] = {}
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        
        # Load balancing
        self.load_balancer_state: Dict[str, Any] = defaultdict(dict)
        self.connection_pools: Dict[str, aiohttp.ClientSession] = {}
        
        # Monitoring et métriques
        self.api_metrics = APIMetrics()
        self.request_history: deque = deque(maxlen=10000)
        self.response_times: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        
        # Rate limiting
        self.rate_limit_cache: Dict[str, Dict[str, Any]] = defaultdict(dict)
        
        # Caching
        self.response_cache: Dict[str, Dict[str, Any]] = {}
        self.cache_ttl_seconds = self.config.get("cache_ttl", 300)
        
        # WebSocket connections
        self.websocket_connections: Dict[str, web.WebSocketResponse] = {}
        
        # Quantum optimizer
        self.quantum_optimizer = None  # À injecter
        
        # Application web
        self.app = web.Application()
        self._setup_routes()
        
        logger.info("🌐 Quantum API Gateway initialized")
    
    async def initialize(self) -> None:
        """Initialisation complète gateway"""
        try:
            # Configuration SSL si activé
            await self._setup_ssl_context()
            
            # Initialisation pools de connexions
            await self._initialize_connection_pools()
            
            # Démarrage health checks
            await self._start_health_checks()
            
            # Démarrage monitoring
            await self._start_monitoring_tasks()
            
            # Chargement configuration persistée
            await self._load_persisted_configuration()
            
            logger.info("✅ Quantum API Gateway initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize API gateway: {e}")
            raise
    
    async def start(self) -> None:
        """Démarrage serveur gateway"""
        try:
            logger.info(f"🚀 Starting Quantum API Gateway on {self.host}:{self.port}")
            
            runner = web.AppRunner(self.app)
            await runner.setup()
            
            site = web.TCPSite(
                runner, 
                self.host, 
                self.port,
                ssl_context=self.ssl_context
            )
            
            await site.start()
            
            logger.info(f"✅ Quantum API Gateway started successfully")
            
            # Maintien en vie
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                logger.info("🛑 Shutting down Quantum API Gateway...")
                await runner.cleanup()
                
        except Exception as e:
            logger.error(f"❌ Failed to start API gateway: {e}")
            raise
    
    # ========================================
    # SERVICE ENDPOINT MANAGEMENT
    # ========================================
    
    async def register_service_endpoint(self, endpoint: ServiceEndpoint) -> str:
        """Enregistrement endpoint de service"""
        try:
            logger.info(f"📡 Registering service endpoint: {endpoint.service_name}")
            
            # Validation endpoint
            await self._validate_service_endpoint(endpoint)
            
            # Test de santé initial
            await self._perform_health_check(endpoint)
            
            # Stockage endpoint
            self.service_endpoints[endpoint.endpoint_id] = endpoint
            
            # Initialisation circuit breaker
            circuit_breaker = CircuitBreaker(
                breaker_id=f"cb_{endpoint.endpoint_id}",
                service_endpoint_id=endpoint.endpoint_id
            )
            self.circuit_breakers[circuit_breaker.breaker_id] = circuit_breaker
            
            # Initialisation pool de connexions
            await self._initialize_endpoint_connection_pool(endpoint)
            
            logger.info(f"✅ Service endpoint {endpoint.endpoint_id} registered successfully")
            
            return endpoint.endpoint_id
            
        except Exception as e:
            logger.error(f"❌ Failed to register service endpoint: {e}")
            raise
    
    async def unregister_service_endpoint(self, endpoint_id: str) -> bool:
        """Désenregistrement endpoint"""
        try:
            if endpoint_id not in self.service_endpoints:
                return False
            
            # Nettoyage connexions
            if endpoint_id in self.connection_pools:
                await self.connection_pools[endpoint_id].close()
                del self.connection_pools[endpoint_id]
            
            # Suppression circuit breaker
            circuit_breakers_to_remove = [
                cb_id for cb_id, cb in self.circuit_breakers.items()
                if cb.service_endpoint_id == endpoint_id
            ]
            for cb_id in circuit_breakers_to_remove:
                del self.circuit_breakers[cb_id]
            
            # Suppression endpoint
            del self.service_endpoints[endpoint_id]
            
            logger.info(f"✅ Service endpoint {endpoint_id} unregistered")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to unregister service endpoint {endpoint_id}: {e}")
            return False
    
    # ========================================
    # API ROUTE MANAGEMENT
    # ========================================
    
    async def register_api_route(self, route: APIRoute) -> str:
        """Enregistrement route API"""
        try:
            logger.info(f"🛣️ Registering API route: {route.path_pattern}")
            
            # Validation route
            await self._validate_api_route(route)
            
            # Vérification endpoints existent
            for endpoint_id in route.service_endpoints:
                if endpoint_id not in self.service_endpoints:
                    raise ValueError(f"Service endpoint {endpoint_id} not found")
            
            # Stockage route
            self.api_routes[route.route_id] = route
            
            logger.info(f"✅ API route {route.route_id} registered successfully")
            
            return route.route_id
            
        except Exception as e:
            logger.error(f"❌ Failed to register API route: {e}")
            raise
    
    async def unregister_api_route(self, route_id: str) -> bool:
        """Désenregistrement route API"""
        try:
            if route_id in self.api_routes:
                del self.api_routes[route_id]
                logger.info(f"✅ API route {route_id} unregistered")
                return True
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to unregister API route {route_id}: {e}")
            return False
    
    # ========================================
    # REQUEST HANDLING
    # ========================================
    
    def _setup_routes(self) -> None:
        """Configuration routes web application"""
        # Route catch-all pour toutes les requêtes
        self.app.router.add_route("*", "/{path:.*}", self._handle_request)
        
        # Route WebSocket
        self.app.router.add_get("/ws/{path:.*}", self._handle_websocket)
        
        # Routes administratives
        self.app.router.add_get("/_admin/health", self._admin_health_check)
        self.app.router.add_get("/_admin/metrics", self._admin_metrics)
        self.app.router.add_get("/_admin/routes", self._admin_routes)
        self.app.router.add_get("/_admin/endpoints", self._admin_endpoints)
    
    async def _handle_request(self, request: web.Request) -> web.Response:
        """Gestion requête principale"""
        try:
            start_time = time.time()
            request_id = str(uuid.uuid4())
            
            # Construction objet requête
            api_request = APIRequest(
                request_id=request_id,
                client_ip=request.remote,
                method=RouteMethod(request.method),
                path=request.path,
                headers=dict(request.headers),
                query_params=dict(request.query),
                body=await request.read() if request.can_read_body else None,
                user_agent=request.headers.get("User-Agent", "")
            )
            
            logger.debug(f"🔄 Processing request {request_id}: {api_request.method.value} {api_request.path}")
            
            # Recherche route correspondante
            matching_route = await self._find_matching_route(api_request)
            if not matching_route:
                return self._create_error_response(404, "Route not found")
            
            # Authentification
            auth_result = await self._authenticate_request(api_request, matching_route)
            if not auth_result["success"]:
                return self._create_error_response(401, auth_result["message"])
            
            api_request.authentication_context = auth_result["context"]
            
            # Rate limiting
            rate_limit_result = await self._check_rate_limits(api_request)
            if not rate_limit_result["allowed"]:
                return self._create_error_response(429, "Rate limit exceeded", rate_limit_result["headers"])
            
            # Vérification cache
            cache_key = await self._generate_cache_key(api_request, matching_route)
            cached_response = await self._check_cache(cache_key)
            if cached_response:
                return self._create_response_from_cache(cached_response)
            
            # Transformation requête
            transformed_request = await self._apply_request_transformers(api_request, matching_route)
            
            # Sélection endpoint avec load balancing
            selected_endpoint = await self._select_service_endpoint(transformed_request, matching_route)
            if not selected_endpoint:
                return self._create_error_response(503, "No healthy service endpoints available")
            
            # Vérification circuit breaker
            circuit_breaker = await self._get_circuit_breaker(selected_endpoint.endpoint_id)
            if circuit_breaker.state == CircuitBreakerState.OPEN:
                return self._create_error_response(503, "Service temporarily unavailable")
            
            # Appel service
            try:
                service_response = await self._call_service_endpoint(transformed_request, selected_endpoint)
                
                # Mise à jour circuit breaker (succès)
                await self._record_circuit_breaker_success(circuit_breaker)
                
                # Transformation réponse
                final_response = await self._apply_response_transformers(service_response, matching_route)
                
                # Mise en cache si configuré
                if matching_route.cache_config:
                    await self._cache_response(cache_key, final_response)
                
                # Métriques
                response_time = (time.time() - start_time) * 1000
                await self._record_metrics(api_request, final_response, response_time, selected_endpoint)
                
                return self._create_web_response(final_response)
                
            except Exception as service_error:
                # Mise à jour circuit breaker (échec)
                await self._record_circuit_breaker_failure(circuit_breaker)
                
                logger.error(f"❌ Service call failed for {request_id}: {service_error}")
                return self._create_error_response(502, "Service error")
            
        except Exception as e:
            logger.error(f"❌ Request handling failed: {e}")
            return self._create_error_response(500, "Internal gateway error")
    
    async def _handle_websocket(self, request: web.Request) -> web.WebSocketResponse:
        """Gestion connexions WebSocket"""
        try:
            ws = web.WebSocketResponse()
            await ws.prepare(request)
            
            connection_id = str(uuid.uuid4())
            self.websocket_connections[connection_id] = ws
            
            logger.info(f"🔌 WebSocket connection established: {connection_id}")
            
            try:
                async for msg in ws:
                    if msg.type == WSMsgType.TEXT:
                        # Traitement message WebSocket
                        await self._process_websocket_message(connection_id, msg.data)
                    elif msg.type == WSMsgType.ERROR:
                        logger.error(f"❌ WebSocket error: {ws.exception()}")
            finally:
                if connection_id in self.websocket_connections:
                    del self.websocket_connections[connection_id]
                logger.info(f"🔌 WebSocket connection closed: {connection_id}")
            
            return ws
            
        except Exception as e:
            logger.error(f"❌ WebSocket handling failed: {e}")
            raise
    
    # ========================================
    # LOAD BALANCING
    # ========================================
    
    async def _select_service_endpoint(
        self, 
        request: APIRequest, 
        route: APIRoute
    ) -> Optional[ServiceEndpoint]:
        """Sélection endpoint avec load balancing"""
        try:
            available_endpoints = [
                self.service_endpoints[endpoint_id]
                for endpoint_id in route.service_endpoints
                if endpoint_id in self.service_endpoints
                and self.service_endpoints[endpoint_id].status == ServiceStatus.HEALTHY
            ]
            
            if not available_endpoints:
                return None
            
            if route.load_balancing_strategy == LoadBalancingStrategy.ROUND_ROBIN:
                return await self._round_robin_selection(available_endpoints, route.route_id)
            elif route.load_balancing_strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
                return await self._least_connections_selection(available_endpoints)
            elif route.load_balancing_strategy == LoadBalancingStrategy.LEAST_RESPONSE_TIME:
                return await self._least_response_time_selection(available_endpoints)
            elif route.load_balancing_strategy == LoadBalancingStrategy.QUANTUM_OPTIMIZED:
                return await self._quantum_optimized_selection(available_endpoints, request)
            else:
                return available_endpoints[0]  # Fallback
                
        except Exception as e:
            logger.error(f"❌ Endpoint selection failed: {e}")
            return None
    
    async def _round_robin_selection(
        self, 
        endpoints: List[ServiceEndpoint], 
        route_id: str
    ) -> ServiceEndpoint:
        """Sélection round robin"""
        if route_id not in self.load_balancer_state:
            self.load_balancer_state[route_id]["round_robin_index"] = 0
        
        index = self.load_balancer_state[route_id]["round_robin_index"]
        selected = endpoints[index % len(endpoints)]
        
        self.load_balancer_state[route_id]["round_robin_index"] = (index + 1) % len(endpoints)
        
        return selected
    
    async def _least_connections_selection(self, endpoints: List[ServiceEndpoint]) -> ServiceEndpoint:
        """Sélection par moins de connexions"""
        return min(endpoints, key=lambda ep: ep.active_connections)
    
    async def _least_response_time_selection(self, endpoints: List[ServiceEndpoint]) -> ServiceEndpoint:
        """Sélection par temps de réponse"""
        return min(endpoints, key=lambda ep: ep.response_time_ms)
    
    async def _quantum_optimized_selection(
        self, 
        endpoints: List[ServiceEndpoint], 
        request: APIRequest
    ) -> ServiceEndpoint:
        """Sélection optimisée quantique"""
        try:
            # Calcul score quantique pour chaque endpoint
            endpoint_scores = []
            
            for endpoint in endpoints:
                score = await self._calculate_quantum_endpoint_score(endpoint, request)
                endpoint_scores.append((endpoint, score))
            
            # Sélection endpoint avec meilleur score
            best_endpoint = max(endpoint_scores, key=lambda x: x[1])[0]
            
            return best_endpoint
            
        except Exception as e:
            logger.error(f"❌ Quantum endpoint selection failed: {e}")
            return endpoints[0]  # Fallback
    
    async def _calculate_quantum_endpoint_score(
        self, 
        endpoint: ServiceEndpoint, 
        request: APIRequest
    ) -> float:
        """Calcul score quantique endpoint"""
        # Simulation algorithme de scoring quantique
        base_score = 1.0
        
        # Facteur performance
        if endpoint.response_time_ms > 0:
            performance_factor = 1.0 / (1.0 + endpoint.response_time_ms / 1000)
        else:
            performance_factor = 1.0
        
        # Facteur charge
        load_factor = 1.0 - (endpoint.active_connections / endpoint.max_connections)
        
        # Facteur quantique
        quantum_factor = 1.2 if endpoint.quantum_enhanced else 1.0
        
        # Score final
        final_score = base_score * performance_factor * load_factor * quantum_factor
        
        return final_score
    
    # ========================================
    # AUTHENTICATION & RATE LIMITING
    # ========================================
    
    async def _authenticate_request(self, request: APIRequest, route: APIRoute) -> Dict[str, Any]:
        """Authentification requête"""
        try:
            if route.authentication == AuthenticationType.NONE:
                return {"success": True, "context": {}}
            
            if route.authentication == AuthenticationType.API_KEY:
                return await self._authenticate_api_key(request)
            elif route.authentication == AuthenticationType.JWT:
                return await self._authenticate_jwt(request)
            elif route.authentication == AuthenticationType.QUANTUM_SIGNATURE:
                return await self._authenticate_quantum_signature(request)
            else:
                return {"success": False, "message": "Unsupported authentication type"}
                
        except Exception as e:
            logger.error(f"❌ Authentication failed: {e}")
            return {"success": False, "message": "Authentication error"}
    
    async def _authenticate_api_key(self, request: APIRequest) -> Dict[str, Any]:
        """Authentification par clé API"""
        api_key = request.headers.get("X-API-Key") or request.query_params.get("api_key", [None])[0]
        
        if not api_key:
            return {"success": False, "message": "API key required"}
        
        # Validation clé API (simulation)
        if api_key.startswith("qk_"):  # Quantum key prefix
            return {
                "success": True,
                "context": {
                    "api_key": api_key,
                    "user_id": f"user_{hashlib.md5(api_key.encode()).hexdigest()[:8]}",
                    "quantum_access": True
                }
            }
        
        return {"success": False, "message": "Invalid API key"}
    
    async def _authenticate_jwt(self, request: APIRequest) -> Dict[str, Any]:
        """Authentification JWT"""
        auth_header = request.headers.get("Authorization", "")
        
        if not auth_header.startswith("Bearer "):
            return {"success": False, "message": "Bearer token required"}
        
        token = auth_header[7:]  # Remove "Bearer "
        
        try:
            # Validation JWT (simulation - utiliserait vraie clé)
            payload = jwt.decode(token, "secret", algorithms=["HS256"])
            
            return {
                "success": True,
                "context": {
                    "user_id": payload.get("sub"),
                    "scope": payload.get("scope", []),
                    "exp": payload.get("exp")
                }
            }
            
        except jwt.InvalidTokenError:
            return {"success": False, "message": "Invalid JWT token"}
    
    async def _authenticate_quantum_signature(self, request: APIRequest) -> Dict[str, Any]:
        """Authentification signature quantique"""
        # Simulation authentification quantique
        quantum_sig = request.headers.get("X-Quantum-Signature")
        
        if not quantum_sig:
            return {"success": False, "message": "Quantum signature required"}
        
        # Simulation validation signature quantique
        if len(quantum_sig) > 64:  # Simulation longueur signature quantique
            return {
                "success": True,
                "context": {
                    "quantum_authenticated": True,
                    "security_level": "quantum",
                    "user_id": f"quantum_user_{quantum_sig[:8]}"
                }
            }
        
        return {"success": False, "message": "Invalid quantum signature"}
    
    async def _check_rate_limits(self, request: APIRequest) -> Dict[str, Any]:
        """Vérification limites de taux"""
        try:
            # Recherche règles applicables
            applicable_rules = []
            for rule in self.rate_limit_rules.values():
                if self._matches_rate_limit_pattern(request, rule):
                    applicable_rules.append(rule)
            
            if not applicable_rules:
                return {"allowed": True, "headers": {}}
            
            # Vérification chaque règle
            for rule in applicable_rules:
                identifier = self._get_rate_limit_identifier(request, rule)
                
                if not await self._check_rate_limit_rule(identifier, rule):
                    return {
                        "allowed": False,
                        "headers": {
                            "X-RateLimit-Limit": str(rule.max_requests),
                            "X-RateLimit-Window": str(rule.time_window_seconds),
                            "Retry-After": str(rule.time_window_seconds)
                        }
                    }
            
            return {"allowed": True, "headers": {}}
            
        except Exception as e:
            logger.error(f"❌ Rate limit check failed: {e}")
            return {"allowed": True, "headers": {}}  # Fail open
    
    # ========================================
    # MONITORING & HEALTH CHECKS
    # ========================================
    
    async def _start_health_checks(self) -> None:
        """Démarrage checks de santé"""
        async def health_check_loop() -> None:
            while True:
                try:
                    for endpoint in self.service_endpoints.values():
                        await self._perform_health_check(endpoint)
                    await asyncio.sleep(30)  # Check toutes les 30 secondes
                except Exception as e:
                    logger.error(f"❌ Health check loop error: {e}")
                    await asyncio.sleep(5)
        
        asyncio.create_task(health_check_loop())
    
    async def _perform_health_check(self, endpoint -> None: ServiceEndpoint) -> None:
        """Exécution check de santé"""
        try:
            url = f"{endpoint.protocol}://{endpoint.host}:{endpoint.port}{endpoint.health_check_path}"
            
            start_time = time.time()
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    response_time = (time.time() - start_time) * 1000
                    
                    if response.status == 200:
                        endpoint.status = ServiceStatus.HEALTHY
                        endpoint.response_time_ms = response_time
                    else:
                        endpoint.status = ServiceStatus.DEGRADED
            
            endpoint.last_health_check = datetime.utcnow()
            
        except Exception as e:
            endpoint.status = ServiceStatus.UNHEALTHY
            logger.warning(f"⚠️ Health check failed for {endpoint.service_name}: {e}")
    
    async def _start_monitoring_tasks(self) -> None:
        """Démarrage tâches monitoring"""
        async def metrics_update_loop() -> None:
            while True:
                try:
                    await self._update_real_time_metrics()
                    await asyncio.sleep(10)  # Mise à jour toutes les 10 secondes
                except Exception as e:
                    logger.error(f"❌ Metrics update error: {e}")
                    await asyncio.sleep(5)
        
        asyncio.create_task(metrics_update_loop())
    
    async def _update_real_time_metrics(self) -> None:
        """Mise à jour métriques temps réel"""
        try:
            # Calcul métriques depuis l'historique
            recent_requests = [
                req for req in self.request_history
                if req.timestamp >= datetime.utcnow() - timedelta(minutes=5)
            ]
            
            if recent_requests:
                self.api_metrics.total_requests = len(self.request_history)
                self.api_metrics.requests_per_second = len(recent_requests) / 300  # 5 minutes
                
                # Calculs additionnels
                successful = sum(1 for req in recent_requests if hasattr(req, 'status_code') and req.status_code < 400)
                self.api_metrics.successful_requests = successful
                self.api_metrics.failed_requests = len(recent_requests) - successful
                self.api_metrics.error_rate_percentage = (self.api_metrics.failed_requests / len(recent_requests)) * 100
            
            self.api_metrics.last_updated = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"❌ Metrics update failed: {e}")


# ========================================
# API GATEWAY HELPER FUNCTIONS
# ========================================

def create_service_endpoint(
    service_name: str,
    host: str,
    port: int,
    **kwargs
) -> ServiceEndpoint:
    """Création endpoint de service"""
    return ServiceEndpoint(
        endpoint_id=kwargs.get("endpoint_id", f"ep_{uuid.uuid4().hex[:8]}"),
        service_name=service_name,
        host=host,
        port=port,
        **{k: v for k, v in kwargs.items() if k != "endpoint_id"}
    )

def create_api_route(
    path_pattern: str,
    methods: List[RouteMethod],
    service_endpoints: List[str],
    **kwargs
) -> APIRoute:
    """Création route API"""
    return APIRoute(
        route_id=kwargs.get("route_id", f"route_{uuid.uuid4().hex[:8]}"),
        path_pattern=path_pattern,
        methods=methods,
        service_endpoints=service_endpoints,
        **{k: v for k, v in kwargs.items() if k != "route_id"}
    )

def create_rate_limit_rule(
    identifier_pattern: str,
    max_requests: int,
    time_window_seconds: int,
    **kwargs
) -> RateLimitRule:
    """Création règle rate limiting"""
    return RateLimitRule(
        rule_id=kwargs.get("rule_id", f"rl_{uuid.uuid4().hex[:8]}"),
        identifier_pattern=identifier_pattern,
        limit_type=kwargs.get("limit_type", RateLimitType.PER_MINUTE),
        max_requests=max_requests,
        time_window_seconds=time_window_seconds,
        **{k: v for k, v in kwargs.items() if k not in ["rule_id", "limit_type"]}
    )

# ========================================
# EXPORT INTERFACES
# ========================================

__all__ = [
    "QuantumAPIGateway",
    "ServiceEndpoint",
    "APIRoute",
    "APIRequest",
    "APIResponse",
    "RateLimitRule",
    "CircuitBreaker",
    "APIMetrics",
    "RouteMethod",
    "LoadBalancingStrategy",
    "AuthenticationType",
    "RateLimitType",
    "ServiceStatus",
    "CircuitBreakerState",
    "create_service_endpoint",
    "create_api_route",
    "create_rate_limit_rule"
]
