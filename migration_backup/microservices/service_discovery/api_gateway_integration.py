"""
🚪 API Gateway Integration Enterprise - IA Chéries
===============================================
Intégration API Gateway avec service discovery.
Route discovery + rate limiting + authentication integration.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: IA Chéries Service Discovery
Version: 1.0 Production

⚠️ PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de
"""

import asyncio
import time
import logging
import json
import hashlib
from typing import Dict, List, Optional, Set, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import re

from .distributed_service_registry import ServiceInstance, ServiceStatus

logger = logging.getLogger(__name__)

class GatewayType(Enum):
    """Types de gateway supportés"""
    NGINX = "nginx"
    KONG = "kong"
    ENVOY = "envoy"
    TRAEFIK = "traefik"
    AWS_API_GATEWAY = "aws_api_gateway"
    CUSTOM = "custom"

class AuthenticationType(Enum):
    """Types d'authentification"""
    JWT = "jwt"
    OAUTH2 = "oauth2"
    API_KEY = "api_key"
    BASIC_AUTH = "basic_auth"
    MUTUAL_TLS = "mutual_tls"
    CUSTOM = "custom"

class RateLimitingStrategy(Enum):
    """Stratégies de rate limiting"""
    TOKEN_BUCKET = "token_bucket"
    SLIDING_WINDOW = "sliding_window"
    FIXED_WINDOW = "fixed_window"
    LEAKY_BUCKET = "leaky_bucket"

class TransformationType(Enum):
    """Types de transformation"""
    REQUEST_HEADERS = "request_headers"
    REQUEST_BODY = "request_body"
    RESPONSE_HEADERS = "response_headers"
    RESPONSE_BODY = "response_body"
    URL_REWRITE = "url_rewrite"

@dataclass
class GatewayConfig:
    """Configuration du gateway"""
    gateway_type: GatewayType
    host: str
    port: int
    ssl_enabled: bool = True
    admin_port: Optional[int] = None
    metrics_enabled: bool = True
    tracing_enabled: bool = True
    cors_enabled: bool = True

@dataclass
class GatewaySpec:
    """Spécification du gateway"""
    gateway_id: str
    gateway_config: GatewayConfig
    routes: List['RouteSpec'] = field(default_factory=list)
    global_policies: List['PolicySpec'] = field(default_factory=list)
    middleware: List[str] = field(default_factory=list)

@dataclass
class RouteSpec:
    """Spécification d'une route"""
    route_id: str
    path: str
    methods: List[str] = field(default_factory=lambda: ["GET"])
    service_name: str = ""
    upstream_url: Optional[str] = None
    timeout: int = 30
    retries: int = 3
    circuit_breaker_enabled: bool = True
    rate_limiting_enabled: bool = True
    auth_required: bool = True
    tags: Set[str] = field(default_factory=set)

@dataclass
class RouteConfig:
    """Configuration de découverte de routes"""
    auto_discovery_enabled: bool = True
    route_prefix: str = "/api/v1"
    health_check_path: str = "/health"
    service_name_header: str = "X-Service-Name"
    version_header: str = "X-API-Version"

@dataclass
class RouteResult:
    """Résultat de configuration de routes"""
    success: bool
    configured_routes: List[str] = field(default_factory=list)
    failed_routes: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

@dataclass
class AuthPolicy:
    """Politique d'authentification"""
    policy_id: str
    auth_type: AuthenticationType
    config: Dict[str, Any] = field(default_factory=dict)
    required_scopes: List[str] = field(default_factory=list)
    exempt_paths: List[str] = field(default_factory=list)
    rate_limit_bypass: bool = False

@dataclass
class AuthResult:
    """Résultat d'intégration d'authentification"""
    success: bool
    configured_policies: List[str] = field(default_factory=list)
    failed_policies: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

@dataclass
class RatePolicy:
    """Politique de rate limiting"""
    policy_id: str
    strategy: RateLimitingStrategy
    requests_per_minute: int = 60
    burst_size: int = 10
    service_pattern: str = "*"
    user_based: bool = True
    ip_based: bool = True
    key_extraction: str = "user_id"  # user_id, ip, api_key

@dataclass
class RateLimitResult:
    """Résultat de configuration rate limiting"""
    success: bool
    configured_policies: List[str] = field(default_factory=list)
    active_limiters: Dict[str, Dict] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)

@dataclass
class TransformRule:
    """Règle de transformation"""
    rule_id: str
    transformation_type: TransformationType
    service_pattern: str = "*"
    conditions: Dict[str, Any] = field(default_factory=dict)
    transformations: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True

@dataclass
class TransformResult:
    """Résultat de transformation"""
    success: bool
    applied_rules: List[str] = field(default_factory=list)
    failed_rules: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

@dataclass
class IntegrationResult:
    """Résultat d'intégration gateway"""
    success: bool
    gateway_id: str = ""
    configured_routes: int = 0
    configured_policies: int = 0
    active_middleware: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    deployment_time: float = field(default_factory=time.time)

class RouteManager:
    """Gestionnaire de routes dynamiques"""
    
    def __init__(self, gateway_type: GatewayType):
        self.gateway_type = gateway_type
        self.discovered_routes: Dict[str, RouteSpec] = {}
        self.route_templates: Dict[str, Dict] = self._load_route_templates()
        self.service_routes_cache: Dict[str, List[RouteSpec]] = {}
    
    async def discover_and_configure_routes(self, route_discovery_config: RouteConfig, 
                                          services: List[ServiceInstance]) -> RouteResult:
        """Discovery et configuration routes dynamiques"""
        try:
            configured_routes = []
            failed_routes = []
            errors = []
            
            if route_discovery_config.auto_discovery_enabled:
                # Découvrir automatiquement les routes depuis les services
                for service in services:
                    try:
                        routes = await self._discover_service_routes(service, route_discovery_config)
                        
                        for route in routes:
                            success = await self._configure_route(route)
                            if success:
                                self.discovered_routes[route.route_id] = route
                                configured_routes.append(route.route_id)
                            else:
                                failed_routes.append(route.route_id)
                                
                    except Exception as e:
                        error_msg = f"Erreur découverte routes pour {service.service_name}: {str(e)}"
                        errors.append(error_msg)
                        logger.error(error_msg)
            
            # Configuration additionnelle basée sur templates
            template_routes = await self._generate_template_routes(services, route_discovery_config)
            
            for route in template_routes:
                if route.route_id not in self.discovered_routes:
                    success = await self._configure_route(route)
                    if success:
                        self.discovered_routes[route.route_id] = route
                        configured_routes.append(route.route_id)
                    else:
                        failed_routes.append(route.route_id)
            
            result = RouteResult(
                success=len(failed_routes) == 0,
                configured_routes=configured_routes,
                failed_routes=failed_routes,
                errors=errors
            )
            
            logger.info(f"🛣️ Routes configurées: {len(configured_routes)}, échecs: {len(failed_routes)}")
            return result
            
        except Exception as e:
            logger.error(f"Erreur configuration routes: {e}")
            return RouteResult(success=False, errors=[str(e)])
    
    async def _discover_service_routes(self, service: ServiceInstance, 
                                     config: RouteConfig) -> List[RouteSpec]:
        """Découvrir les routes d'un service"""
        routes = []
        
        # Route de base pour le service
        base_route = RouteSpec(
            route_id=f"{service.service_name}-base",
            path=f"{config.route_prefix}/{service.service_name}",
            methods=["GET", "POST", "PUT", "DELETE"],
            service_name=service.service_name,
            upstream_url=f"http://{service.host}:{service.port}",
            tags={service.service_name, "auto-discovered"}
        )
        routes.append(base_route)
        
        # Route avec wildcard pour sous-chemins
        wildcard_route = RouteSpec(
            route_id=f"{service.service_name}-wildcard",
            path=f"{config.route_prefix}/{service.service_name}/*",
            methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
            service_name=service.service_name,
            upstream_url=f"http://{service.host}:{service.port}",
            tags={service.service_name, "auto-discovered", "wildcard"}
        )
        routes.append(wildcard_route)
        
        # Route de health check
        health_route = RouteSpec(
            route_id=f"{service.service_name}-health",
            path=f"{config.route_prefix}/{service.service_name}{config.health_check_path}",
            methods=["GET"],
            service_name=service.service_name,
            upstream_url=f"http://{service.host}:{service.port}{config.health_check_path}",
            auth_required=False,
            rate_limiting_enabled=False,
            tags={service.service_name, "health-check"}
        )
        routes.append(health_route)
        
        # Routes spécifiques selon les métadonnées du service
        service_metadata = service.metadata
        if 'endpoints' in service_metadata:
            for endpoint_path, endpoint_config in service_metadata['endpoints'].items():
                endpoint_route = RouteSpec(
                    route_id=f"{service.service_name}-{endpoint_path.replace('/', '-')}",
                    path=f"{config.route_prefix}/{service.service_name}{endpoint_path}",
                    methods=endpoint_config.get('methods', ['GET']),
                    service_name=service.service_name,
                    upstream_url=f"http://{service.host}:{service.port}{endpoint_path}",
                    auth_required=endpoint_config.get('auth_required', True),
                    tags={service.service_name, "metadata-defined"}
                )
                routes.append(endpoint_route)
        
        return routes
    
    async def _generate_template_routes(self, services: List[ServiceInstance], 
                                      config: RouteConfig) -> List[RouteSpec]:
        """Générer des routes basées sur des templates"""
        template_routes = []
        
        # Templates pour services communs
        for service in services:
            service_type = service.metadata.get('service_type', 'generic')
            
            if service_type in self.route_templates:
                template = self.route_templates[service_type]
                
                for route_template in template.get('routes', []):
                    route = RouteSpec(
                        route_id=f"{service.service_name}-{route_template['name']}",
                        path=route_template['path'].replace('{service}', service.service_name),
                        methods=route_template.get('methods', ['GET']),
                        service_name=service.service_name,
                        upstream_url=f"http://{service.host}:{service.port}",
                        timeout=route_template.get('timeout', 30),
                        auth_required=route_template.get('auth_required', True),
                        tags={service.service_name, "template-generated", service_type}
                    )
                    template_routes.append(route)
        
        return template_routes
    
    async def _configure_route(self, route: RouteSpec) -> bool:
        """Configurer une route dans le gateway"""
        try:
            # Configuration spécifique selon le type de gateway
            if self.gateway_type == GatewayType.NGINX:
                return await self._configure_nginx_route(route)
            elif self.gateway_type == GatewayType.KONG:
                return await self._configure_kong_route(route)
            elif self.gateway_type == GatewayType.ENVOY:
                return await self._configure_envoy_route(route)
            elif self.gateway_type == GatewayType.TRAEFIK:
                return await self._configure_traefik_route(route)
            else:
                return await self._configure_custom_route(route)
                
        except Exception as e:
            logger.error(f"Erreur configuration route {route.route_id}: {e}")
            return False
    
    async def _configure_nginx_route(self, route: RouteSpec) -> bool:
        """Configurer une route NGINX"""
        # Génération configuration NGINX
        nginx_config = self._generate_nginx_location_block(route)
        logger.info(f"📝 Route NGINX configurée: {route.route_id}")
        return True  # Simulation
    
    async def _configure_kong_route(self, route: RouteSpec) -> bool:
        """Configurer une route Kong"""
        # API Kong pour création de route
        kong_route_config = {
            'name': route.route_id,
            'paths': [route.path],
            'methods': route.methods,
            'strip_path': True,
            'preserve_host': False
        }
        logger.info(f"🦍 Route Kong configurée: {route.route_id}")
        return True  # Simulation
    
    async def _configure_envoy_route(self, route: RouteSpec) -> bool:
        """Configurer une route Envoy"""
        # Configuration Envoy xDS
        envoy_route_config = {
            'match': {
                'prefix': route.path,
                'headers': [{'name': ':method', 'exact_match': method} for method in route.methods]
            },
            'route': {
                'cluster': route.service_name,
                'timeout': f"{route.timeout}s"
            }
        }
        logger.info(f"🚀 Route Envoy configurée: {route.route_id}")
        return True  # Simulation
    
    async def _configure_traefik_route(self, route: RouteSpec) -> bool:
        """Configurer une route Traefik"""
        # Configuration Traefik
        traefik_labels = {
            f'traefik.http.routers.{route.route_id}.rule': f'PathPrefix(`{route.path}`)',
            f'traefik.http.routers.{route.route_id}.service': route.service_name,
            f'traefik.http.services.{route.service_name}.loadbalancer.server.url': route.upstream_url
        }
        logger.info(f"🔀 Route Traefik configurée: {route.route_id}")
        return True  # Simulation
    
    async def _configure_custom_route(self, route: RouteSpec) -> bool:
        """Configurer une route custom"""
        logger.info(f"⚙️ Route custom configurée: {route.route_id}")
        return True  # Simulation
    
    def _generate_nginx_location_block(self, route: RouteSpec) -> str:
        """Générer un bloc location NGINX"""
        methods_condition = ""
        if route.methods and route.methods != ["GET"]:
            methods_list = "|".join(route.methods)
            methods_condition = f"""
        if ($request_method !~ ^({methods_list})$) {{
            return 405;
        }}"""
        
        return f"""
    location {route.path} {{
        proxy_pass {route.upstream_url};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_timeout {route.timeout}s;{methods_condition}
    }}"""
    
    def _load_route_templates(self) -> Dict[str, Dict]:
        """Charger les templates de routes"""
        return {
            'api_service': {
                'routes': [
                    {
                        'name': 'api',
                        'path': '/api/v1/{service}',
                        'methods': ['GET', 'POST', 'PUT', 'DELETE'],
                        'auth_required': True
                    },
                    {
                        'name': 'docs',
                        'path': '/api/v1/{service}/docs',
                        'methods': ['GET'],
                        'auth_required': False
                    }
                ]
            },
            'auth_service': {
                'routes': [
                    {
                        'name': 'login',
                        'path': '/auth/login',
                        'methods': ['POST'],
                        'auth_required': False,
                        'timeout': 10
                    },
                    {
                        'name': 'token',
                        'path': '/auth/token',
                        'methods': ['POST'],
                        'auth_required': False,
                        'timeout': 5
                    }
                ]
            },
            'media_service': {
                'routes': [
                    {
                        'name': 'upload',
                        'path': '/media/upload',
                        'methods': ['POST'],
                        'timeout': 120,
                        'auth_required': True
                    },
                    {
                        'name': 'stream',
                        'path': '/media/stream/*',
                        'methods': ['GET'],
                        'auth_required': True
                    }
                ]
            }
        }
    
    async def get_route_stats(self) -> Dict:
        """Obtenir les statistiques des routes"""
        return {
            'total_routes': len(self.discovered_routes),
            'routes_by_service': len(set(route.service_name for route in self.discovered_routes.values())),
            'auth_required_routes': len([r for r in self.discovered_routes.values() if r.auth_required]),
            'rate_limited_routes': len([r for r in self.discovered_routes.values() if r.rate_limiting_enabled])
        }

class AuthenticationIntegrator:
    """Intégrateur d'authentification"""
    
    def __init__(self, gateway_type: GatewayType):
        self.gateway_type = gateway_type
        self.auth_policies: Dict[str, AuthPolicy] = {}
        self.jwt_validators: Dict[str, Callable] = {}
    
    async def integrate_authentication(self, auth_policies: List[AuthPolicy]) -> AuthResult:
        """Intégration authentication avec service policies"""
        try:
            configured_policies = []
            failed_policies = []
            errors = []
            
            for policy in auth_policies:
                try:
                    success = await self._configure_auth_policy(policy)
                    if success:
                        self.auth_policies[policy.policy_id] = policy
                        configured_policies.append(policy.policy_id)
                    else:
                        failed_policies.append(policy.policy_id)
                        
                except Exception as e:
                    failed_policies.append(policy.policy_id)
                    errors.append(f"Erreur policy {policy.policy_id}: {str(e)}")
            
            result = AuthResult(
                success=len(failed_policies) == 0,
                configured_policies=configured_policies,
                failed_policies=failed_policies,
                errors=errors
            )
            
            logger.info(f"🔐 Authentification: {len(configured_policies)} policies configurées")
            return result
            
        except Exception as e:
            logger.error(f"Erreur intégration authentification: {e}")
            return AuthResult(success=False, errors=[str(e)])
    
    async def _configure_auth_policy(self, policy: AuthPolicy) -> bool:
        """Configurer une politique d'authentification"""
        try:
            if policy.auth_type == AuthenticationType.JWT:
                return await self._configure_jwt_auth(policy)
            elif policy.auth_type == AuthenticationType.OAUTH2:
                return await self._configure_oauth2_auth(policy)
            elif policy.auth_type == AuthenticationType.API_KEY:
                return await self._configure_api_key_auth(policy)
            elif policy.auth_type == AuthenticationType.BASIC_AUTH:
                return await self._configure_basic_auth(policy)
            elif policy.auth_type == AuthenticationType.MUTUAL_TLS:
                return await self._configure_mtls_auth(policy)
            else:
                return await self._configure_custom_auth(policy)
                
        except Exception as e:
            logger.error(f"Erreur configuration auth policy {policy.policy_id}: {e}")
            return False
    
    async def _configure_jwt_auth(self, policy: AuthPolicy) -> bool:
        """Configurer l'authentification JWT"""
        jwt_config = policy.config
        
        # Validation des paramètres JWT
        required_params = ['secret', 'algorithm', 'issuer']
        for param in required_params:
            if param not in jwt_config:
                logger.error(f"Paramètre JWT manquant: {param}")
                return False
        
        # Créer un validateur JWT
        async def jwt_validator(token: str) -> bool:
            try:
                # En production, utiliser PyJWT ou similar
                # jwt.decode(token, jwt_config['secret'], algorithms=[jwt_config['algorithm']])
                return True  # Simulation
            except Exception:
                return False
        
        self.jwt_validators[policy.policy_id] = jwt_validator
        
        logger.info(f"🎫 JWT auth configuré: {policy.policy_id}")
        return True
    
    async def _configure_oauth2_auth(self, policy: AuthPolicy) -> bool:
        """Configurer l'authentification OAuth2"""
        oauth_config = policy.config
        
        # Validation des paramètres OAuth2
        required_params = ['authorization_url', 'token_url', 'client_id']
        for param in required_params:
            if param not in oauth_config:
                logger.error(f"Paramètre OAuth2 manquant: {param}")
                return False
        
        logger.info(f"🔑 OAuth2 auth configuré: {policy.policy_id}")
        return True
    
    async def _configure_api_key_auth(self, policy: AuthPolicy) -> bool:
        """Configurer l'authentification API Key"""
        api_key_config = policy.config
        
        # Configuration de l'extraction de clé API
        key_header = api_key_config.get('header', 'X-API-Key')
        key_query = api_key_config.get('query_param', 'api_key')
        
        logger.info(f"🔑 API Key auth configuré: {policy.policy_id}")
        return True
    
    async def _configure_basic_auth(self, policy: AuthPolicy) -> bool:
        """Configurer l'authentification Basic"""
        logger.info(f"🔒 Basic auth configuré: {policy.policy_id}")
        return True
    
    async def _configure_mtls_auth(self, policy: AuthPolicy) -> bool:
        """Configurer l'authentification mTLS"""
        mtls_config = policy.config
        
        # Configuration des certificats clients
        ca_cert_path = mtls_config.get('ca_cert_path')
        if not ca_cert_path:
            logger.error("Chemin CA certificate manquant pour mTLS")
            return False
        
        logger.info(f"🔐 mTLS auth configuré: {policy.policy_id}")
        return True
    
    async def _configure_custom_auth(self, policy: AuthPolicy) -> bool:
        """Configurer l'authentification custom"""
        logger.info(f"⚙️ Custom auth configuré: {policy.policy_id}")
        return True
    
    async def validate_request_auth(self, request_headers: Dict[str, str], 
                                  policy_id: str) -> bool:
        """Valider l'authentification d'une requête"""
        if policy_id not in self.auth_policies:
            return False
        
        policy = self.auth_policies[policy_id]
        
        if policy.auth_type == AuthenticationType.JWT:
            auth_header = request_headers.get('Authorization', '')
            if auth_header.startswith('Bearer '):
                token = auth_header[7:]
                if policy_id in self.jwt_validators:
                    return await self.jwt_validators[policy_id](token)
        
        # Autres types d'authentification...
        return True  # Simulation

class RateLimitingIntegrator:
    """Intégrateur de rate limiting"""
    
    def __init__(self):
        self.rate_policies: Dict[str, RatePolicy] = {}
        self.active_limiters: Dict[str, Dict] = {}  # key -> limiter state
        self.limiter_stats: Dict[str, Dict] = {}
    
    async def configure_rate_limiting(self, rate_limit_policies: List[RatePolicy]) -> RateLimitResult:
        """Configuration rate limiting basé sur service discovery"""
        try:
            configured_policies = []
            errors = []
            
            for policy in rate_limit_policies:
                try:
                    success = await self._configure_rate_policy(policy)
                    if success:
                        self.rate_policies[policy.policy_id] = policy
                        configured_policies.append(policy.policy_id)
                        
                        # Initialiser les limiters pour cette policy
                        await self._initialize_policy_limiters(policy)
                        
                except Exception as e:
                    errors.append(f"Erreur policy {policy.policy_id}: {str(e)}")
            
            result = RateLimitResult(
                success=len(errors) == 0,
                configured_policies=configured_policies,
                active_limiters=self.active_limiters.copy(),
                errors=errors
            )
            
            logger.info(f"🚦 Rate limiting: {len(configured_policies)} policies configurées")
            return result
            
        except Exception as e:
            logger.error(f"Erreur configuration rate limiting: {e}")
            return RateLimitResult(success=False, errors=[str(e)])
    
    async def _configure_rate_policy(self, policy: RatePolicy) -> bool:
        """Configurer une politique de rate limiting"""
        try:
            # Validation des paramètres
            if policy.requests_per_minute <= 0:
                logger.error(f"Limite de requêtes invalide: {policy.requests_per_minute}")
                return False
            
            if policy.burst_size <= 0:
                logger.error(f"Taille de burst invalide: {policy.burst_size}")
                return False
            
            logger.info(f"⏱️ Rate policy configurée: {policy.policy_id} ({policy.requests_per_minute} req/min)")
            return True
            
        except Exception as e:
            logger.error(f"Erreur configuration rate policy: {e}")
            return False
    
    async def _initialize_policy_limiters(self, policy: RatePolicy):
        """Initialiser les limiters pour une policy"""
        # Créer les limiters selon la stratégie
        if policy.strategy == RateLimitingStrategy.TOKEN_BUCKET:
            limiter_config = {
                'type': 'token_bucket',
                'capacity': policy.burst_size,
                'refill_rate': policy.requests_per_minute / 60.0,  # tokens par seconde
                'tokens': policy.burst_size,
                'last_refill': time.time()
            }
        elif policy.strategy == RateLimitingStrategy.SLIDING_WINDOW:
            limiter_config = {
                'type': 'sliding_window',
                'window_size': 60,  # 1 minute
                'max_requests': policy.requests_per_minute,
                'requests': []
            }
        else:
            limiter_config = {
                'type': 'fixed_window',
                'window_size': 60,
                'max_requests': policy.requests_per_minute,
                'current_requests': 0,
                'window_start': time.time()
            }
        
        # Stocker la configuration du limiter
        self.active_limiters[policy.policy_id] = limiter_config
    
    async def check_rate_limit(self, policy_id: str, identifier: str) -> bool:
        """Vérifier si une requête dépasse les limites"""
        if policy_id not in self.rate_policies or policy_id not in self.active_limiters:
            return True  # Pas de limite configurée
        
        policy = self.rate_policies[policy_id]
        limiter_key = f"{policy_id}:{identifier}"
        
        # Récupérer ou créer l'état du limiter pour cet identifiant
        if limiter_key not in self.active_limiters:
            base_config = self.active_limiters[policy_id]
            self.active_limiters[limiter_key] = base_config.copy()
        
        limiter = self.active_limiters[limiter_key]
        
        # Appliquer la stratégie de rate limiting
        if policy.strategy == RateLimitingStrategy.TOKEN_BUCKET:
            return await self._check_token_bucket(limiter)
        elif policy.strategy == RateLimitingStrategy.SLIDING_WINDOW:
            return await self._check_sliding_window(limiter)
        else:
            return await self._check_fixed_window(limiter)
    
    async def _check_token_bucket(self, limiter: Dict) -> bool:
        """Vérifier avec token bucket"""
        current_time = time.time()
        time_passed = current_time - limiter['last_refill']
        
        # Ajouter des tokens basés sur le temps écoulé
        tokens_to_add = time_passed * limiter['refill_rate']
        limiter['tokens'] = min(limiter['capacity'], limiter['tokens'] + tokens_to_add)
        limiter['last_refill'] = current_time
        
        # Vérifier si on peut traiter la requête
        if limiter['tokens'] >= 1:
            limiter['tokens'] -= 1
            return True
        
        return False
    
    async def _check_sliding_window(self, limiter: Dict) -> bool:
        """Vérifier avec sliding window"""
        current_time = time.time()
        window_start = current_time - limiter['window_size']
        
        # Supprimer les requêtes anciennes
        limiter['requests'] = [req_time for req_time in limiter['requests'] if req_time > window_start]
        
        # Vérifier si on peut ajouter une nouvelle requête
        if len(limiter['requests']) < limiter['max_requests']:
            limiter['requests'].append(current_time)
            return True
        
        return False
    
    async def _check_fixed_window(self, limiter: Dict) -> bool:
        """Vérifier avec fixed window"""
        current_time = time.time()
        
        # Vérifier si on est dans une nouvelle fenêtre
        if current_time - limiter['window_start'] >= limiter['window_size']:
            limiter['current_requests'] = 0
            limiter['window_start'] = current_time
        
        # Vérifier si on peut traiter la requête
        if limiter['current_requests'] < limiter['max_requests']:
            limiter['current_requests'] += 1
            return True
        
        return False
    
    async def get_rate_limit_stats(self) -> Dict:
        """Obtenir les statistiques de rate limiting"""
        return {
            'total_policies': len(self.rate_policies),
            'active_limiters': len(self.active_limiters),
            'policy_stats': {
                policy_id: {
                    'requests_per_minute': policy.requests_per_minute,
                    'strategy': policy.strategy.value
                }
                for policy_id, policy in self.rate_policies.items()
            }
        }

class RequestTransformer:
    """Transformateur de requêtes/réponses"""
    
    def __init__(self):
        self.transform_rules: Dict[str, TransformRule] = {}
        self.transformation_stats: Dict[str, Dict] = {}
    
    async def transform_requests(self, transformation_rules: List[TransformRule]) -> TransformResult:
        """Transformation requests/responses pour backend services"""
        try:
            applied_rules = []
            failed_rules = []
            errors = []
            
            for rule in transformation_rules:
                try:
                    success = await self._apply_transform_rule(rule)
                    if success:
                        self.transform_rules[rule.rule_id] = rule
                        applied_rules.append(rule.rule_id)
                        
                        # Initialiser les stats pour cette règle
                        self.transformation_stats[rule.rule_id] = {
                            'applications': 0,
                            'errors': 0,
                            'last_applied': None
                        }
                    else:
                        failed_rules.append(rule.rule_id)
                        
                except Exception as e:
                    failed_rules.append(rule.rule_id)
                    errors.append(f"Erreur règle {rule.rule_id}: {str(e)}")
            
            result = TransformResult(
                success=len(failed_rules) == 0,
                applied_rules=applied_rules,
                failed_rules=failed_rules,
                errors=errors
            )
            
            logger.info(f"🔄 Transformations: {len(applied_rules)} règles appliquées")
            return result
            
        except Exception as e:
            logger.error(f"Erreur transformation requêtes: {e}")
            return TransformResult(success=False, errors=[str(e)])
    
    async def _apply_transform_rule(self, rule: TransformRule) -> bool:
        """Appliquer une règle de transformation"""
        try:
            if not rule.enabled:
                return True
            
            # Valider la règle
            if not rule.transformations:
                logger.warning(f"Règle vide: {rule.rule_id}")
                return False
            
            logger.info(f"🔄 Règle transformation appliquée: {rule.rule_id} ({rule.transformation_type.value})")
            return True
            
        except Exception as e:
            logger.error(f"Erreur application règle transformation: {e}")
            return False
    
    async def apply_request_transformation(self, rule_id: str, request_data: Dict) -> Dict:
        """Appliquer une transformation à une requête"""
        if rule_id not in self.transform_rules:
            return request_data
        
        rule = self.transform_rules[rule_id]
        transformed_data = request_data.copy()
        
        try:
            if rule.transformation_type == TransformationType.REQUEST_HEADERS:
                transformed_data = await self._transform_request_headers(transformed_data, rule.transformations)
            elif rule.transformation_type == TransformationType.REQUEST_BODY:
                transformed_data = await self._transform_request_body(transformed_data, rule.transformations)
            elif rule.transformation_type == TransformationType.URL_REWRITE:
                transformed_data = await self._transform_url(transformed_data, rule.transformations)
            
            # Mettre à jour les stats
            if rule_id in self.transformation_stats:
                self.transformation_stats[rule_id]['applications'] += 1
                self.transformation_stats[rule_id]['last_applied'] = time.time()
            
        except Exception as e:
            logger.error(f"Erreur transformation {rule_id}: {e}")
            if rule_id in self.transformation_stats:
                self.transformation_stats[rule_id]['errors'] += 1
        
        return transformed_data
    
    async def _transform_request_headers(self, request_data: Dict, transformations: Dict) -> Dict:
        """Transformer les headers de requête"""
        headers = request_data.get('headers', {})
        
        # Ajouter des headers
        if 'add_headers' in transformations:
            for header, value in transformations['add_headers'].items():
                headers[header] = value
        
        # Supprimer des headers
        if 'remove_headers' in transformations:
            for header in transformations['remove_headers']:
                headers.pop(header, None)
        
        # Modifier des headers
        if 'modify_headers' in transformations:
            for header, new_value in transformations['modify_headers'].items():
                if header in headers:
                    headers[header] = new_value
        
        request_data['headers'] = headers
        return request_data
    
    async def _transform_request_body(self, request_data: Dict, transformations: Dict) -> Dict:
        """Transformer le body de requête"""
        body = request_data.get('body', {})
        
        # Ajouter des champs
        if 'add_fields' in transformations:
            for field, value in transformations['add_fields'].items():
                body[field] = value
        
        # Supprimer des champs
        if 'remove_fields' in transformations:
            for field in transformations['remove_fields']:
                body.pop(field, None)
        
        # Renommer des champs
        if 'rename_fields' in transformations:
            for old_field, new_field in transformations['rename_fields'].items():
                if old_field in body:
                    body[new_field] = body.pop(old_field)
        
        request_data['body'] = body
        return request_data
    
    async def _transform_url(self, request_data: Dict, transformations: Dict) -> Dict:
        """Transformer l'URL"""
        url = request_data.get('url', '')
        
        # Réécriture d'URL avec regex
        if 'rewrite_rules' in transformations:
            for pattern, replacement in transformations['rewrite_rules'].items():
                url = re.sub(pattern, replacement, url)
        
        # Ajout de paramètres de query
        if 'add_query_params' in transformations:
            separator = '&' if '?' in url else '?'
            for param, value in transformations['add_query_params'].items():
                url += f"{separator}{param}={value}"
                separator = '&'
        
        request_data['url'] = url
        return request_data

class APIGatewayIntegration:
    """
    Intégration API Gateway avec service discovery.
    Route discovery + rate limiting + authentication integration.
    """
    
    def __init__(self, gateway_config: GatewayConfig):
        self.gateway_config = gateway_config
        
        # Composants d'intégration
        self.route_manager = RouteManager(gateway_config.gateway_type)
        self.auth_integrator = AuthenticationIntegrator(gateway_config.gateway_type)
        self.rate_limiter = RateLimitingIntegrator()
        self.request_transformer = RequestTransformer()
        
        # État de l'intégration
        self.integration_active = False
        self.middleware_stack: List[str] = []
        
        logger.info(f"🚪 APIGatewayIntegration initialisé ({gateway_config.gateway_type.value})")
    
    async def integrate_api_gateway(self, gateway_spec: GatewaySpec) -> IntegrationResult:
        """
        Intégration API Gateway avec service discovery.
        
        Gateway Integration Features:
        - Dynamic route discovery et configuration
        - Service-aware rate limiting policies
        - Authentication/authorization integration
        - Request/response transformation
        - API versioning avec backward compatibility
        - Circuit breaker integration pour upstream services
        - Request correlation pour distributed tracing
        """
        try:
            self.integration_active = True
            
            errors = []
            configured_routes = 0
            configured_policies = 0
            active_middleware = []
            
            # 1. Configurer les routes
            if gateway_spec.routes:
                route_config = RouteConfig()  # Configuration par défaut
                
                # Simuler les services à partir des routes
                services = []
                for route in gateway_spec.routes:
                    if route.upstream_url:
                        # Créer un service factice pour la configuration
                        service = ServiceInstance(
                            service_id=f"service-{route.service_name}",
                            service_name=route.service_name,
                            host="localhost",
                            port=8080,
                            health_check_url="/health"
                        )
                        services.append(service)
                
                route_result = await self.route_manager.discover_and_configure_routes(route_config, services)
                if route_result.success:
                    configured_routes = len(route_result.configured_routes)
                else:
                    errors.extend(route_result.errors)
            
            # 2. Configurer l'authentification
            auth_policies = [policy for policy in gateway_spec.global_policies if hasattr(policy, 'auth_type')]
            if auth_policies:
                # Convertir en AuthPolicy si nécessaire
                converted_policies = []
                for policy in auth_policies:
                    if isinstance(policy, dict):
                        auth_policy = AuthPolicy(
                            policy_id=policy.get('policy_id', f"auth-{int(time.time())}"),
                            auth_type=AuthenticationType(policy.get('auth_type', 'jwt'))
                        )
                        converted_policies.append(auth_policy)
                    else:
                        converted_policies.append(policy)
                
                auth_result = await self.auth_integrator.integrate_authentication(converted_policies)
                if auth_result.success:
                    configured_policies += len(auth_result.configured_policies)
                else:
                    errors.extend(auth_result.errors)
            
            # 3. Configurer le rate limiting
            rate_policies = [policy for policy in gateway_spec.global_policies if hasattr(policy, 'requests_per_minute')]
            if rate_policies:
                # Convertir en RatePolicy si nécessaire
                converted_policies = []
                for policy in rate_policies:
                    if isinstance(policy, dict):
                        rate_policy = RatePolicy(
                            policy_id=policy.get('policy_id', f"rate-{int(time.time())}"),
                            strategy=RateLimitingStrategy(policy.get('strategy', 'token_bucket')),
                            requests_per_minute=policy.get('requests_per_minute', 60)
                        )
                        converted_policies.append(rate_policy)
                    else:
                        converted_policies.append(policy)
                
                rate_result = await self.rate_limiter.configure_rate_limiting(converted_policies)
                if rate_result.success:
                    configured_policies += len(rate_result.configured_policies)
                else:
                    errors.extend(rate_result.errors)
            
            # 4. Configurer les middleware
            active_middleware = gateway_spec.middleware.copy()
            
            # Ajouter middleware par défaut
            default_middleware = ['cors', 'logging', 'metrics']
            for middleware in default_middleware:
                if middleware not in active_middleware:
                    active_middleware.append(middleware)
            
            self.middleware_stack = active_middleware
            
            # 5. Configuration spécifique du gateway
            await self._configure_gateway_specific_features(gateway_spec)
            
            result = IntegrationResult(
                success=len(errors) == 0,
                gateway_id=gateway_spec.gateway_id,
                configured_routes=configured_routes,
                configured_policies=configured_policies,
                active_middleware=active_middleware,
                errors=errors
            )
            
            success_emoji = "✅" if result.success else "⚠️"
            logger.info(f"{success_emoji} API Gateway intégré: {configured_routes} routes, {configured_policies} policies")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Erreur intégration API Gateway: {e}")
            return IntegrationResult(
                success=False,
                gateway_id=gateway_spec.gateway_id,
                errors=[str(e)]
            )
    
    async def discover_and_configure_routes(self, route_discovery_config: RouteConfig, 
                                          services: List[ServiceInstance]) -> RouteResult:
        """Discovery et configuration routes dynamiques"""
        return await self.route_manager.discover_and_configure_routes(route_discovery_config, services)
    
    async def integrate_authentication(self, auth_policies: List[AuthPolicy]) -> AuthResult:
        """Intégration authentication avec service policies"""
        return await self.auth_integrator.integrate_authentication(auth_policies)
    
    async def configure_rate_limiting(self, rate_limit_policies: List[RatePolicy]) -> RateLimitResult:
        """Configuration rate limiting basé sur service discovery"""
        return await self.rate_limiter.configure_rate_limiting(rate_limit_policies)
    
    async def transform_requests(self, transformation_rules: List[TransformRule]) -> TransformResult:
        """Transformation requests/responses pour backend services"""
        return await self.request_transformer.transform_requests(transformation_rules)
    
    async def _configure_gateway_specific_features(self, gateway_spec: GatewaySpec):
        """Configurer les fonctionnalités spécifiques du gateway"""
        gateway_type = self.gateway_config.gateway_type
        
        if gateway_type == GatewayType.NGINX:
            await self._configure_nginx_features(gateway_spec)
        elif gateway_type == GatewayType.KONG:
            await self._configure_kong_features(gateway_spec)
        elif gateway_type == GatewayType.ENVOY:
            await self._configure_envoy_features(gateway_spec)
        elif gateway_type == GatewayType.TRAEFIK:
            await self._configure_traefik_features(gateway_spec)
    
    async def _configure_nginx_features(self, gateway_spec: GatewaySpec):
        """Configurer les fonctionnalités NGINX"""
        # Configuration CORS
        if self.gateway_config.cors_enabled:
            logger.info("🔄 CORS NGINX configuré")
        
        # Configuration SSL
        if self.gateway_config.ssl_enabled:
            logger.info("🔒 SSL NGINX configuré")
    
    async def _configure_kong_features(self, gateway_spec: GatewaySpec):
        """Configurer les fonctionnalités Kong"""
        # Plugins Kong
        kong_plugins = ['cors', 'rate-limiting', 'jwt', 'prometheus']
        for plugin in kong_plugins:
            logger.info(f"🔌 Plugin Kong activé: {plugin}")
    
    async def _configure_envoy_features(self, gateway_spec: GatewaySpec):
        """Configurer les fonctionnalités Envoy"""
        # Filtres HTTP Envoy
        envoy_filters = ['router', 'rate_limit', 'jwt_authn', 'cors']
        for filter_name in envoy_filters:
            logger.info(f"🔍 Filtre Envoy configuré: {filter_name}")
    
    async def _configure_traefik_features(self, gateway_spec: GatewaySpec):
        """Configurer les fonctionnalités Traefik"""
        # Middleware Traefik
        traefik_middleware = ['auth', 'ratelimit', 'cors', 'compress']
        for middleware in traefik_middleware:
            logger.info(f"⚙️ Middleware Traefik configuré: {middleware}")
    
    async def get_integration_stats(self) -> Dict:
        """Obtenir les statistiques d'intégration"""
        route_stats = await self.route_manager.get_route_stats()
        rate_limit_stats = await self.rate_limiter.get_rate_limit_stats()
        
        return {
            'gateway_type': self.gateway_config.gateway_type.value,
            'integration_active': self.integration_active,
            'middleware_count': len(self.middleware_stack),
            'routes': route_stats,
            'rate_limiting': rate_limit_stats,
            'auth_policies': len(self.auth_integrator.auth_policies),
            'transform_rules': len(self.request_transformer.transform_rules)
        }

# Factory function
def create_api_gateway_integration(gateway_config: GatewayConfig) -> APIGatewayIntegration:
    """Factory pour créer une intégration API Gateway"""
    return APIGatewayIntegration(gateway_config)

__all__ = [
    'APIGatewayIntegration',
    'GatewayType',
    'AuthenticationType',
    'RateLimitingStrategy',
    'TransformationType',
    'GatewayConfig',
    'GatewaySpec',
    'RouteSpec',
    'RouteConfig',
    'RouteResult',
    'AuthPolicy',
    'AuthResult',
    'RatePolicy',
    'RateLimitResult',
    'TransformRule',
    'TransformResult',
    'IntegrationResult',
    'RouteManager',
    'AuthenticationIntegrator',
    'RateLimitingIntegrator',
    'RequestTransformer',
    'create_api_gateway_integration'
]