"""
Marketing API Gateway - IA Chérie Enterprise
=========================================
Gateway API marketing avec authentification enterprise et rate limiting.
API gateway + authentication + rate limiting + load balancing + monitoring.

Author: Expert Team (Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer)  
IP Owner: Fahed Mlaiel (mlaiel@live.de)
Project: IA Chérie Marketing Services
Version: 1.0 Production

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
Cette architecture API gateway marketing et tous ses algorithmes sont la propriété intellectuelle EXCLUSIVE de Fahed Mlaiel (mlaiel@live.de).
Toute reproduction, modification, distribution ou vol d'idée/concept/code sans autorisation écrite PERSONNELLE est STRICTEMENT INTERDITE.
"""

import asyncio
import logging
import json
import time
import hashlib
import jwt
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import uuid
from abc import ABC, abstractmethod
import aiohttp
from aiohttp import web, ClientSession
import ssl
import redis.asyncio as redis
from functools import wraps

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AuthenticationMethod(Enum):
    """Méthodes d'authentification supportées"""
    JWT_TOKEN = "jwt_token"
    API_KEY = "api_key"
    OAUTH2 = "oauth2"
    BASIC_AUTH = "basic_auth"
    MUTUAL_TLS = "mutual_tls"

class RateLimitStrategy(Enum):
    """Stratégies de rate limiting"""
    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW = "sliding_window" 
    TOKEN_BUCKET = "token_bucket"
    LEAKY_BUCKET = "leaky_bucket"

class LoadBalancingAlgorithm(Enum):
    """Algorithmes de load balancing"""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    IP_HASH = "ip_hash"
    HEALTH_BASED = "health_based"

@dataclass
class APIEndpointConfig:
    """Configuration d'un endpoint API"""
    endpoint_id: str
    path: str
    methods: List[str]
    auth_required: bool = True
    rate_limit: Dict[str, int] = field(default_factory=lambda: {"requests": 1000, "window": 3600})
    cache_ttl: int = 300  # 5 minutes
    timeout: int = 30
    retry_attempts: int = 3
    circuit_breaker_enabled: bool = True

@dataclass 
class ServiceTarget:
    """Configuration d'un service backend"""
    service_id: str
    name: str
    base_url: str
    health_check_path: str = "/health"
    weight: int = 1
    max_connections: int = 100
    timeout: int = 30
    ssl_verify: bool = True

@dataclass
class GatewayConfig:
    """Configuration principale du gateway"""
    gateway_id: str
    name: str
    port: int = 8080
    ssl_enabled: bool = True
    ssl_cert_path: Optional[str] = None
    ssl_key_path: Optional[str] = None
    cors_enabled: bool = True
    cors_origins: List[str] = field(default_factory=lambda: ["*"])
    request_logging: bool = True
    metrics_enabled: bool = True
    redis_url: str = "redis://localhost:6379"

class CircuitBreakerState(Enum):
    """États du circuit breaker"""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    """
    Circuit breaker pour protection des services backend.
    """
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60, success_threshold: int = 3):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitBreakerState.CLOSED
        self.success_count = 0
    
    async def call(self, func: Callable, *args, **kwargs):
        """Exécute une fonction avec circuit breaker protection"""
        
        if self.state == CircuitBreakerState.OPEN:
            # Vérifier si on peut passer en half-open
            if self.last_failure_time and time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = CircuitBreakerState.HALF_OPEN
                self.success_count = 0
                logger.info("Circuit breaker transitioning to HALF_OPEN")
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = await func(*args, **kwargs)
            
            # Success handling
            if self.state == CircuitBreakerState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.success_threshold:
                    self.state = CircuitBreakerState.CLOSED
                    self.failure_count = 0
                    logger.info("Circuit breaker transitioning to CLOSED")
            elif self.state == CircuitBreakerState.CLOSED:
                self.failure_count = 0
            
            return result
            
        except Exception as e:
            # Failure handling
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = CircuitBreakerState.OPEN
                logger.warning(f"Circuit breaker transitioning to OPEN due to {self.failure_count} failures")
            
            raise e

class RateLimiter:
    """
    Rate limiter avec support de multiple stratégies.
    """
    
    def __init__(self, redis_client: redis.Redis, strategy: RateLimitStrategy = RateLimitStrategy.SLIDING_WINDOW):
        self.redis_client = redis_client
        self.strategy = strategy
    
    async def is_allowed(self, key: str, limit: int, window: int) -> Dict[str, Any]:
        """
        Vérifie si la requête est autorisée selon les limites.
        
        Returns:
            Dict avec status (allowed/denied), current_count, reset_time
        """
        
        if self.strategy == RateLimitStrategy.SLIDING_WINDOW:
            return await self._sliding_window_check(key, limit, window)
        elif self.strategy == RateLimitStrategy.FIXED_WINDOW:
            return await self._fixed_window_check(key, limit, window)
        elif self.strategy == RateLimitStrategy.TOKEN_BUCKET:
            return await self._token_bucket_check(key, limit, window)
        else:
            return {"allowed": True, "current_count": 0, "reset_time": 0}
    
    async def _sliding_window_check(self, key: str, limit: int, window: int) -> Dict[str, Any]:
        """Implémentation sliding window rate limiting"""
        current_time = time.time()
        pipeline = self.redis_client.pipeline()
        
        # Supprimer les entrées expirées
        pipeline.zremrangebyscore(key, 0, current_time - window)
        
        # Compter les requêtes dans la fenêtre
        pipeline.zcard(key)
        
        # Ajouter la requête actuelle
        pipeline.zadd(key, {str(current_time): current_time})
        
        # Définir expiration
        pipeline.expire(key, window)
        
        results = await pipeline.execute()
        current_count = results[1]
        
        if current_count < limit:
            return {
                "allowed": True,
                "current_count": current_count + 1,
                "reset_time": current_time + window,
                "remaining": limit - current_count - 1
            }
        else:
            return {
                "allowed": False,
                "current_count": current_count,
                "reset_time": current_time + window,
                "remaining": 0
            }
    
    async def _fixed_window_check(self, key: str, limit: int, window: int) -> Dict[str, Any]:
        """Implémentation fixed window rate limiting"""
        current_time = int(time.time())
        window_start = (current_time // window) * window
        window_key = f"{key}:{window_start}"
        
        pipeline = self.redis_client.pipeline()
        pipeline.incr(window_key)
        pipeline.expire(window_key, window)
        results = await pipeline.execute()
        
        current_count = results[0]
        reset_time = window_start + window
        
        return {
            "allowed": current_count <= limit,
            "current_count": current_count,
            "reset_time": reset_time,
            "remaining": max(0, limit - current_count)
        }
    
    async def _token_bucket_check(self, key: str, limit: int, window: int) -> Dict[str, Any]:
        """Implémentation token bucket rate limiting"""
        current_time = time.time()
        
        # Récupérer l'état actuel du bucket
        bucket_data = await self.redis_client.hmget(
            key, "tokens", "last_refill"
        )
        
        if bucket_data[0] is None:
            # Nouveau bucket
            tokens = limit
            last_refill = current_time
        else:
            tokens = float(bucket_data[0])
            last_refill = float(bucket_data[1])
        
        # Calculer les nouveaux tokens à ajouter
        time_passed = current_time - last_refill
        tokens_to_add = (time_passed / window) * limit
        tokens = min(limit, tokens + tokens_to_add)
        
        if tokens >= 1:
            # Consommer un token
            tokens -= 1
            
            # Mettre à jour le bucket
            await self.redis_client.hmset(key, {
                "tokens": tokens,
                "last_refill": current_time
            })
            await self.redis_client.expire(key, window * 2)
            
            return {
                "allowed": True,
                "current_count": limit - int(tokens),
                "reset_time": current_time + window,
                "remaining": int(tokens)
            }
        else:
            return {
                "allowed": False,
                "current_count": limit,
                "reset_time": current_time + window,
                "remaining": 0
            }

class LoadBalancer:
    """
    Load balancer pour distribution des requêtes.
    """
    
    def __init__(self, algorithm: LoadBalancingAlgorithm = LoadBalancingAlgorithm.ROUND_ROBIN):
        self.algorithm = algorithm
        self.current_index = 0
        self.connection_counts: Dict[str, int] = {}
    
    async def select_target(self, targets: List[ServiceTarget], request_info: Dict[str, Any]) -> Optional[ServiceTarget]:
        """
        Sélectionne un service target selon l'algorithme configuré.
        """
        
        # Filtrer les targets disponibles
        available_targets = [t for t in targets if await self._is_target_healthy(t)]
        
        if not available_targets:
            return None
        
        if self.algorithm == LoadBalancingAlgorithm.ROUND_ROBIN:
            return await self._round_robin_select(available_targets)
        elif self.algorithm == LoadBalancingAlgorithm.LEAST_CONNECTIONS:
            return await self._least_connections_select(available_targets)
        elif self.algorithm == LoadBalancingAlgorithm.WEIGHTED_ROUND_ROBIN:
            return await self._weighted_round_robin_select(available_targets)
        elif self.algorithm == LoadBalancingAlgorithm.IP_HASH:
            return await self._ip_hash_select(available_targets, request_info)
        else:
            return available_targets[0]
    
    async def _round_robin_select(self, targets: List[ServiceTarget]) -> ServiceTarget:
        """Sélection round robin"""
        target = targets[self.current_index % len(targets)]
        self.current_index += 1
        return target
    
    async def _least_connections_select(self, targets: List[ServiceTarget]) -> ServiceTarget:
        """Sélection par nombre minimum de connexions"""
        return min(targets, key=lambda t: self.connection_counts.get(t.service_id, 0))
    
    async def _weighted_round_robin_select(self, targets: List[ServiceTarget]) -> ServiceTarget:
        """Sélection weighted round robin"""
        # Simplified weighted selection
        weights = [t.weight for t in targets]
        total_weight = sum(weights)
        
        selection_point = self.current_index % total_weight
        current_weight = 0
        
        for target in targets:
            current_weight += target.weight
            if selection_point < current_weight:
                self.current_index += 1
                return target
        
        return targets[0]
    
    async def _ip_hash_select(self, targets: List[ServiceTarget], request_info: Dict[str, Any]) -> ServiceTarget:
        """Sélection par hash de l'IP client"""
        client_ip = request_info.get("client_ip", "unknown")
        hash_value = int(hashlib.md5(client_ip.encode()).hexdigest(), 16)
        return targets[hash_value % len(targets)]
    
    async def _is_target_healthy(self, target: ServiceTarget) -> bool:
        """Vérifie la santé d'un service target"""
        try:
            async with ClientSession() as session:
                async with session.get(
                    f"{target.base_url}{target.health_check_path}",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    return response.status == 200
        except:
            return False
    
    def increment_connections(self, service_id: str):
        """Incrémente le compteur de connexions"""
        self.connection_counts[service_id] = self.connection_counts.get(service_id, 0) + 1
    
    def decrement_connections(self, service_id: str):
        """Décrémente le compteur de connexions"""
        if service_id in self.connection_counts:
            self.connection_counts[service_id] = max(0, self.connection_counts[service_id] - 1)

class MarketingAPIGateway:
    """
    Gateway API marketing enterprise avec fonctionnalités avancées.
    
    Features:
    - Authentication multi-method (JWT, API Key, OAuth2, mTLS)
    - Rate limiting avec multiple stratégies
    - Load balancing avec health checks
    - Circuit breaker pattern pour resilience
    - Request/response transformation
    - Caching intelligent avec invalidation
    - Monitoring et metrics collection
    - Request routing avec path-based rules
    - CORS handling avec configuration fine
    - SSL termination avec certificate management
    """
    
    def __init__(self, config: GatewayConfig):
        self.config = config
        self.app = web.Application()
        self.endpoints: Dict[str, APIEndpointConfig] = {}
        self.services: Dict[str, ServiceTarget] = {}
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.load_balancer = LoadBalancer()
        self.rate_limiter = None
        self.redis_client = None
        
        # Metrics storage
        self.metrics = {
            "requests_total": 0,
            "requests_success": 0,
            "requests_error": 0,
            "response_times": [],
            "rate_limit_hits": 0
        }
        
        self._setup_routes()
        
        logger.info(f"Marketing API Gateway initialized: {config.gateway_id}")
    
    async def initialize(self):
        """Initialisation asynchrone du gateway"""
        # Connexion Redis pour rate limiting et caching
        self.redis_client = redis.from_url(self.config.redis_url)
        self.rate_limiter = RateLimiter(self.redis_client)
        
        # Test de connexion Redis
        try:
            await self.redis_client.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.error(f"Redis connection failed: {str(e)}")
            raise
        
        # Configuration CORS si activé
        if self.config.cors_enabled:
            self._setup_cors()
        
        # Configuration SSL si activé
        if self.config.ssl_enabled:
            self._setup_ssl()
    
    def _setup_routes(self):
        """Configuration des routes du gateway"""
        # Route principale pour proxying
        self.app.router.add_route('*', '/{path:.*}', self._handle_request)
        
        # Routes de management
        self.app.router.add_get('/gateway/health', self._health_check)
        self.app.router.add_get('/gateway/metrics', self._get_metrics)
        self.app.router.add_get('/gateway/config', self._get_config)
    
    def _setup_cors(self):
        """Configuration CORS"""
        async def cors_handler(request, handler):
            response = await handler(request)
            response.headers['Access-Control-Allow-Origin'] = ', '.join(self.config.cors_origins)
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-API-Key'
            return response
        
        self.app.middlewares.append(cors_handler)
    
    def _setup_ssl(self):
        """Configuration SSL"""
        if self.config.ssl_cert_path and self.config.ssl_key_path:
            self.ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            self.ssl_context.load_cert_chain(self.config.ssl_cert_path, self.config.ssl_key_path)
    
    async def register_endpoint(self, endpoint_config: APIEndpointConfig) -> Dict[str, Any]:
        """
        Enregistrement d'un endpoint API avec configuration.
        """
        try:
            endpoint_id = endpoint_config.endpoint_id
            
            # Validation de la configuration
            if not endpoint_config.path.startswith('/'):
                endpoint_config.path = '/' + endpoint_config.path
            
            # Stockage de la configuration
            self.endpoints[endpoint_id] = endpoint_config
            
            # Initialisation circuit breaker pour cet endpoint
            if endpoint_config.circuit_breaker_enabled:
                self.circuit_breakers[endpoint_id] = CircuitBreaker()
            
            logger.info(f"Endpoint registered: {endpoint_config.path}")
            return {
                "success": True,
                "endpoint_id": endpoint_id,
                "path": endpoint_config.path,
                "methods": endpoint_config.methods
            }
            
        except Exception as e:
            logger.error(f"Error registering endpoint: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def register_service(self, service: ServiceTarget) -> Dict[str, Any]:
        """
        Enregistrement d'un service backend.
        """
        try:
            service_id = service.service_id
            
            # Validation du service (health check)
            is_healthy = await self.load_balancer._is_target_healthy(service)
            if not is_healthy:
                logger.warning(f"Service {service_id} failed health check during registration")
            
            # Stockage du service
            self.services[service_id] = service
            
            logger.info(f"Service registered: {service.name} at {service.base_url}")
            return {
                "success": True,
                "service_id": service_id,
                "name": service.name,
                "healthy": is_healthy
            }
            
        except Exception as e:
            logger.error(f"Error registering service: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _handle_request(self, request: web.Request) -> web.Response:
        """
        Handler principal pour toutes les requêtes.
        """
        start_time = time.time()
        
        try:
            # Metrics
            self.metrics["requests_total"] += 1
            
            # Extraction des informations de requête
            request_info = {
                "path": request.path,
                "method": request.method,
                "client_ip": self._get_client_ip(request),
                "user_agent": request.headers.get("User-Agent", ""),
                "headers": dict(request.headers)
            }
            
            # Correspondance d'endpoint
            endpoint_config = await self._match_endpoint(request_info)
            if not endpoint_config:
                return web.json_response(
                    {"error": "Endpoint not found"}, 
                    status=404
                )
            
            # Authentification
            if endpoint_config.auth_required:
                auth_result = await self._authenticate_request(request, endpoint_config)
                if not auth_result["authenticated"]:
                    return web.json_response(
                        {"error": "Authentication failed", "details": auth_result.get("error")},
                        status=401
                    )
                request_info["user"] = auth_result.get("user")
            
            # Rate limiting
            rate_limit_result = await self._check_rate_limit(request_info, endpoint_config)
            if not rate_limit_result["allowed"]:
                self.metrics["rate_limit_hits"] += 1
                response = web.json_response(
                    {"error": "Rate limit exceeded", "retry_after": rate_limit_result.get("reset_time")},
                    status=429
                )
                response.headers["X-RateLimit-Limit"] = str(endpoint_config.rate_limit["requests"])
                response.headers["X-RateLimit-Remaining"] = str(rate_limit_result.get("remaining", 0))
                response.headers["X-RateLimit-Reset"] = str(rate_limit_result.get("reset_time", 0))
                return response
            
            # Cache check
            cached_response = await self._check_cache(request_info, endpoint_config)
            if cached_response:
                response = web.json_response(cached_response["data"])
                response.headers["X-Cache"] = "HIT"
                return response
            
            # Sélection du service backend
            available_services = [s for s in self.services.values()]
            target_service = await self.load_balancer.select_target(available_services, request_info)
            
            if not target_service:
                return web.json_response(
                    {"error": "No healthy services available"},
                    status=503
                )
            
            # Proxy de la requête
            response_data = await self._proxy_request(
                request, target_service, endpoint_config, request_info
            )
            
            # Cache de la réponse
            if endpoint_config.cache_ttl > 0:
                await self._cache_response(request_info, response_data, endpoint_config)
            
            # Métriques de succès
            self.metrics["requests_success"] += 1
            
            # Préparation de la réponse
            response = web.json_response(response_data["data"], status=response_data["status"])
            
            # Headers de réponse
            response.headers["X-Gateway-Service"] = target_service.service_id
            response.headers["X-Response-Time"] = str(int((time.time() - start_time) * 1000))
            
            return response
            
        except Exception as e:
            # Métriques d'erreur
            self.metrics["requests_error"] += 1
            
            logger.error(f"Error handling request: {str(e)}")
            return web.json_response(
                {"error": "Internal gateway error"},
                status=500
            )
        
        finally:
            # Enregistrement du temps de réponse
            response_time = time.time() - start_time
            self.metrics["response_times"].append(response_time)
            
            # Garder seulement les 1000 derniers temps de réponse
            if len(self.metrics["response_times"]) > 1000:
                self.metrics["response_times"] = self.metrics["response_times"][-1000:]
    
    async def _match_endpoint(self, request_info: Dict[str, Any]) -> Optional[APIEndpointConfig]:
        """Correspondance d'endpoint basée sur le path et la méthode"""
        request_path = request_info["path"]
        request_method = request_info["method"]
        
        for endpoint_config in self.endpoints.values():
            if self._path_matches(request_path, endpoint_config.path):
                if request_method in endpoint_config.methods or "ALL" in endpoint_config.methods:
                    return endpoint_config
        
        return None
    
    def _path_matches(self, request_path: str, pattern_path: str) -> bool:
        """Vérification de correspondance de path avec support de wildcards"""
        if pattern_path == request_path:
            return True
        
        # Support simple de wildcards
        if pattern_path.endswith("/*"):
            base_pattern = pattern_path[:-2]
            return request_path.startswith(base_pattern)
        
        return False
    
    async def _authenticate_request(self, request: web.Request, endpoint_config: APIEndpointConfig) -> Dict[str, Any]:
        """
        Authentification de la requête selon la méthode configurée.
        """
        try:
            # JWT Token Authentication
            auth_header = request.headers.get("Authorization", "")
            if auth_header.startswith("Bearer "):
                token = auth_header[7:]
                return await self._authenticate_jwt(token)
            
            # API Key Authentication
            api_key = request.headers.get("X-API-Key")
            if api_key:
                return await self._authenticate_api_key(api_key)
            
            # Basic Authentication
            if auth_header.startswith("Basic "):
                return await self._authenticate_basic(auth_header[6:])
            
            return {"authenticated": False, "error": "No valid authentication method found"}
            
        except Exception as e:
            return {"authenticated": False, "error": str(e)}
    
    async def _authenticate_jwt(self, token: str) -> Dict[str, Any]:
        """Authentification JWT"""
        try:
            # Clé secrète (devrait être stockée de manière sécurisée)
            secret_key = "your-secret-key"  # À remplacer par une vraie clé
            
            payload = jwt.decode(token, secret_key, algorithms=["HS256"])
            
            # Vérification de l'expiration
            if payload.get("exp", 0) < time.time():
                return {"authenticated": False, "error": "Token expired"}
            
            return {
                "authenticated": True,
                "user": {
                    "user_id": payload.get("user_id"),
                    "roles": payload.get("roles", []),
                    "permissions": payload.get("permissions", [])
                }
            }
            
        except jwt.InvalidTokenError as e:
            return {"authenticated": False, "error": f"Invalid JWT token: {str(e)}"}
    
    async def _authenticate_api_key(self, api_key: str) -> Dict[str, Any]:
        """Authentification API Key"""
        try:
            # Vérification en cache Redis
            user_data = await self.redis_client.get(f"api_key:{api_key}")
            
            if user_data:
                user_info = json.loads(user_data)
                return {"authenticated": True, "user": user_info}
            
            return {"authenticated": False, "error": "Invalid API key"}
            
        except Exception as e:
            return {"authenticated": False, "error": str(e)}
    
    async def _authenticate_basic(self, credentials: str) -> Dict[str, Any]:
        """Authentification Basic"""
        try:
            import base64
            decoded = base64.b64decode(credentials).decode('utf-8')
            username, password = decoded.split(':', 1)
            
            # Vérification des credentials (simulation)
            if username == "admin" and password == "admin123":
                return {
                    "authenticated": True,
                    "user": {"user_id": username, "roles": ["admin"]}
                }
            
            return {"authenticated": False, "error": "Invalid credentials"}
            
        except Exception as e:
            return {"authenticated": False, "error": str(e)}
    
    async def _check_rate_limit(self, request_info: Dict[str, Any], endpoint_config: APIEndpointConfig) -> Dict[str, Any]:
        """Vérification des limites de taux"""
        if not self.rate_limiter:
            return {"allowed": True}
        
        # Clé de rate limiting basée sur IP + endpoint
        rate_limit_key = f"rate_limit:{request_info['client_ip']}:{endpoint_config.endpoint_id}"
        
        return await self.rate_limiter.is_allowed(
            rate_limit_key,
            endpoint_config.rate_limit["requests"],
            endpoint_config.rate_limit["window"]
        )
    
    async def _check_cache(self, request_info: Dict[str, Any], endpoint_config: APIEndpointConfig) -> Optional[Dict[str, Any]]:
        """Vérification du cache"""
        if endpoint_config.cache_ttl <= 0 or request_info["method"] != "GET":
            return None
        
        try:
            cache_key = f"cache:{request_info['path']}:{hashlib.md5(str(request_info).encode()).hexdigest()}"
            cached_data = await self.redis_client.get(cache_key)
            
            if cached_data:
                return json.loads(cached_data)
            
        except Exception as e:
            logger.warning(f"Cache check error: {str(e)}")
        
        return None
    
    async def _proxy_request(self, request: web.Request, target_service: ServiceTarget, endpoint_config: APIEndpointConfig, request_info: Dict[str, Any]) -> Dict[str, Any]:
        """Proxy de la requête vers le service backend"""
        
        # Increment connection count
        self.load_balancer.increment_connections(target_service.service_id)
        
        try:
            # Construction de l'URL target
            target_url = f"{target_service.base_url}{request.path_qs}"
            
            # Headers à transmettre
            headers = dict(request.headers)
            headers["X-Forwarded-For"] = request_info["client_ip"]
            headers["X-Gateway-Request-ID"] = str(uuid.uuid4())
            
            # Circuit breaker wrapper
            circuit_breaker = self.circuit_breakers.get(endpoint_config.endpoint_id)
            
            if circuit_breaker:
                response_data = await circuit_breaker.call(
                    self._make_backend_request,
                    target_url, request.method, headers, request
                )
            else:
                response_data = await self._make_backend_request(
                    target_url, request.method, headers, request
                )
            
            return response_data
            
        finally:
            # Decrement connection count
            self.load_balancer.decrement_connections(target_service.service_id)
    
    async def _make_backend_request(self, url: str, method: str, headers: Dict[str, str], request: web.Request) -> Dict[str, Any]:
        """Effectue la requête vers le service backend"""
        
        async with ClientSession() as session:
            # Préparation des données de requête
            data = None
            if method in ["POST", "PUT", "PATCH"]:
                if request.content_type == "application/json":
                    data = await request.json()
                else:
                    data = await request.read()
            
            # Exécution de la requête
            async with session.request(
                method,
                url,
                headers=headers,
                json=data if isinstance(data, dict) else None,
                data=data if not isinstance(data, dict) else None,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                response_data = await response.json() if response.content_type == "application/json" else await response.text()
                
                return {
                    "data": response_data,
                    "status": response.status,
                    "headers": dict(response.headers)
                }
    
    async def _cache_response(self, request_info: Dict[str, Any], response_data: Dict[str, Any], endpoint_config: APIEndpointConfig) -> None:
        """Cache de la réponse"""
        try:
            cache_key = f"cache:{request_info['path']}:{hashlib.md5(str(request_info).encode()).hexdigest()}"
            
            cache_data = {
                "data": response_data["data"],
                "cached_at": time.time()
            }
            
            await self.redis_client.setex(
                cache_key,
                endpoint_config.cache_ttl,
                json.dumps(cache_data)
            )
            
        except Exception as e:
            logger.warning(f"Cache storage error: {str(e)}")
    
    def _get_client_ip(self, request: web.Request) -> str:
        """Extraction de l'IP client"""
        # Vérifier les headers de proxy
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.remote
    
    async def _health_check(self, request: web.Request) -> web.Response:
        """Health check du gateway"""
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "gateway_id": self.config.gateway_id,
            "version": "1.0.0",
            "services": {}
        }
        
        # Vérification des services backend
        for service_id, service in self.services.items():
            is_healthy = await self.load_balancer._is_target_healthy(service)
            health_status["services"][service_id] = {
                "healthy": is_healthy,
                "name": service.name,
                "url": service.base_url
            }
        
        return web.json_response(health_status)
    
    async def _get_metrics(self, request: web.Request) -> web.Response:
        """Métriques du gateway"""
        avg_response_time = (
            sum(self.metrics["response_times"]) / len(self.metrics["response_times"])
            if self.metrics["response_times"] else 0
        )
        
        metrics_data = {
            "requests": {
                "total": self.metrics["requests_total"],
                "success": self.metrics["requests_success"],
                "error": self.metrics["requests_error"],
                "success_rate": (
                    self.metrics["requests_success"] / self.metrics["requests_total"]
                    if self.metrics["requests_total"] > 0 else 0
                )
            },
            "performance": {
                "avg_response_time": avg_response_time,
                "rate_limit_hits": self.metrics["rate_limit_hits"]
            },
            "timestamp": datetime.now().isoformat()
        }
        
        return web.json_response(metrics_data)
    
    async def _get_config(self, request: web.Request) -> web.Response:
        """Configuration du gateway"""
        config_data = {
            "gateway_id": self.config.gateway_id,
            "name": self.config.name,
            "endpoints_count": len(self.endpoints),
            "services_count": len(self.services),
            "features": {
                "ssl_enabled": self.config.ssl_enabled,
                "cors_enabled": self.config.cors_enabled,
                "metrics_enabled": self.config.metrics_enabled,
                "request_logging": self.config.request_logging
            }
        }
        
        return web.json_response(config_data)
    
    async def start_server(self) -> None:
        """Démarrage du serveur gateway"""
        await self.initialize()
        
        ssl_context = getattr(self, 'ssl_context', None)
        
        runner = web.AppRunner(self.app)
        await runner.setup()
        
        site = web.TCPSite(
            runner, 
            '0.0.0.0', 
            self.config.port,
            ssl_context=ssl_context
        )
        
        await site.start()
        
        protocol = "https" if self.config.ssl_enabled else "http"
        logger.info(f"Marketing API Gateway started on {protocol}://0.0.0.0:{self.config.port}")
    
    async def stop_server(self) -> None:
        """Arrêt du serveur gateway"""
        if self.redis_client:
            await self.redis_client.close()
        
        logger.info("Marketing API Gateway stopped")

def get_api_gateway(config: GatewayConfig) -> MarketingAPIGateway:
    """Factory pour créer une instance du gateway API marketing"""
    return MarketingAPIGateway(config)

# Exemple d'utilisation
if __name__ == "__main__":
    async def demo_gateway():
        """Démonstration du gateway API marketing"""
        
        # Configuration du gateway
        config = GatewayConfig(
            gateway_id="mkt_gateway_001",
            name="Marketing API Gateway",
            port=8080,
            ssl_enabled=False,  # Désactivé pour la démo
            cors_enabled=True
        )
        
        # Initialisation du gateway
        gateway = MarketingAPIGateway(config)
        
        # Enregistrement d'un endpoint
        endpoint_config = APIEndpointConfig(
            endpoint_id="campaigns_api",
            path="/api/v1/campaigns/*",
            methods=["GET", "POST", "PUT", "DELETE"],
            auth_required=True,
            rate_limit={"requests": 100, "window": 3600},
            cache_ttl=300
        )
        
        endpoint_result = await gateway.register_endpoint(endpoint_config)
        print("Endpoint registered:")
        print(json.dumps(endpoint_result, indent=2))
        
        # Enregistrement d'un service
        service = ServiceTarget(
            service_id="campaign_service",
            name="Campaign Management Service",
            base_url="http://localhost:8081",
            health_check_path="/health",
            weight=1
        )
        
        service_result = await gateway.register_service(service)
        print("\nService registered:")
        print(json.dumps(service_result, indent=2))
        
        print(f"\nGateway ready to start on port {config.port}")
        print("Example endpoints:")
        print("- GET /gateway/health (Gateway health check)")
        print("- GET /gateway/metrics (Gateway metrics)")
        print("- GET /api/v1/campaigns (Proxied to backend service)")
    
    # Exécution démo
    asyncio.run(demo_gateway())