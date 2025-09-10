"""SEO API Gateway - Passerelle API SEO
===================================

Passerelle API unifiée pour tous les services SEO avec authentification,
rate limiting, monitoring et orchestration des microservices.

Auteur: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. Tous droits réservés.

VERSION: 2.0.0 - CONSOLIDATION MASSIVE
DATE: 2025-09-09
STATUS: ✅ NOUVEAU COMPOSANT API GATEWAY CONSOLIDÉ
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable
from enum import Enum
import asyncio
import logging
import json
import hashlib
import time
from dataclasses import dataclass, field
from collections import defaultdict
import random

# === ÉNUMÉRATIONS ===

class AuthenticationLevel(Enum):
    """Niveaux d'authentification"""
    PUBLIC = "public"
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"
    ADMIN = "admin"

class APIEndpointType(Enum):
    """Types d'endpoints API"""
    ANALYSIS = "analysis"
    OPTIMIZATION = "optimization"
    REPORTING = "reporting"
    INTELLIGENCE = "intelligence"
    MONITORING = "monitoring"
    ADMINISTRATION = "administration"

class RequestMethod(Enum):
    """Méthodes de requête HTTP"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"

class ResponseFormat(Enum):
    """Formats de réponse"""
    JSON = "json"
    XML = "xml"
    CSV = "csv"
    PDF = "pdf"
    HTML = "html"

class RateLimitType(Enum):
    """Types de limitation de débit"""
    PER_MINUTE = "per_minute"
    PER_HOUR = "per_hour"
    PER_DAY = "per_day"
    PER_MONTH = "per_month"

# === CLASSES DE DONNÉES ===

@dataclass
class SEOEndpoint:
    """Définition d'un endpoint SEO"""
    endpoint_id: str
    path: str
    method: RequestMethod
    endpoint_type: APIEndpointType
    auth_level: AuthenticationLevel
    rate_limit: Dict[str, int]
    description: str
    parameters: Dict[str, Any]
    response_schema: Dict[str, Any]
    examples: Dict[str, Any]
    deprecated: bool = False
    version: str = "2.0"
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class APIResponse:
    """Réponse API standardisée"""
    success: bool
    status_code: int
    message: str
    data: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    pagination: Optional[Dict[str, Any]] = None
    rate_limit_info: Optional[Dict[str, Any]] = None
    execution_time_ms: Optional[float] = None
    request_id: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class RateLimitConfig:
    """Configuration de limitation de débit"""
    limit_type: RateLimitType
    requests_per_period: int
    period_duration: int
    burst_allowance: int
    penalty_duration: int
    whitelist: List[str] = field(default_factory=list)
    blacklist: List[str] = field(default_factory=list)

@dataclass
class APIMetrics:
    """Métriques de l'API"""
    endpoint_id: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_response_time: float
    peak_rps: float
    error_rate: float
    rate_limit_hits: int
    unique_clients: int
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

# === CLASSE PRINCIPALE ===

class SEOAPIGateway:
    """
    Passerelle API SEO Consolidée
    
    Fournit une interface unifiée pour tous les services SEO avec
    gestion de l'authentification, du rate limiting et du monitoring.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialise la passerelle API SEO
        
        Args:
            config: Configuration personnalisée
        """
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Configuration par défaut
        self.default_config = {
            "enable_authentication": True,
            "enable_rate_limiting": True,
            "enable_monitoring": True,
            "enable_caching": True,
            "enable_compression": True,
            "enable_cors": True,
            "enable_analytics": True,
            "default_rate_limit": 1000,
            "cache_ttl_seconds": 300,
            "max_request_size_mb": 10,
            "timeout_seconds": 30,
            "enable_swagger_docs": True,
            "enable_health_checks": True
        }
        
        # Fusion des configurations
        self.active_config = {**self.default_config, **self.config}
        
        # Stockage des endpoints
        self.endpoints: Dict[str, SEOEndpoint] = {}
        
        # Gestion du rate limiting
        self.rate_limits: Dict[str, RateLimitConfig] = {}
        self.client_requests: Dict[str, List[float]] = defaultdict(list)
        
        # Cache des réponses
        self.response_cache: Dict[str, Dict[str, Any]] = {}
        
        # Métriques en temps réel
        self.api_metrics: Dict[str, APIMetrics] = {}
        
        # Authentification
        self.auth_tokens: Dict[str, Dict[str, Any]] = {}
        
        # Statistiques globales
        self.stats = {
            "total_requests": 0,
            "total_responses": 0,
            "total_errors": 0,
            "uptime_start": datetime.now(),
            "average_response_time": 0.0,
            "peak_concurrent_requests": 0,
            "cache_hit_rate": 0.0
        }
        
        # Initialisation des endpoints par défaut
        self._initialize_default_endpoints()
        
        self.logger.info("SEO API Gateway initialisé avec succès")
    
    def _initialize_default_endpoints(self):
        """Initialise les endpoints par défaut"""
        
        # Endpoints d'analyse
        self.register_endpoint(SEOEndpoint(
            endpoint_id="analyze_content",
            path="/api/v2/seo/analyze/content",
            method=RequestMethod.POST,
            endpoint_type=APIEndpointType.ANALYSIS,
            auth_level=AuthenticationLevel.BASIC,
            rate_limit={"per_hour": 100, "per_day": 1000},
            description="Analyse le contenu pour le SEO",
            parameters={
                "content": {"type": "string", "required": True},
                "keywords": {"type": "array", "required": False},
                "options": {"type": "object", "required": False}
            },
            response_schema={
                "type": "object",
                "properties": {
                    "analysis_id": {"type": "string"},
                    "seo_score": {"type": "number"},
                    "recommendations": {"type": "array"}
                }
            },
            examples={
                "request": {
                    "content": "Votre contenu ici...",
                    "keywords": ["seo", "optimisation"],
                    "options": {"include_technical": True}
                },
                "response": {
                    "analysis_id": "ana_123456",
                    "seo_score": 78.5,
                    "recommendations": ["Améliorer la densité des mots-clés"]
                }
            }
        ))
        
        # Endpoints d'optimisation
        self.register_endpoint(SEOEndpoint(
            endpoint_id="optimize_content",
            path="/api/v2/seo/optimize/content",
            method=RequestMethod.POST,
            endpoint_type=APIEndpointType.OPTIMIZATION,
            auth_level=AuthenticationLevel.PREMIUM,
            rate_limit={"per_hour": 50, "per_day": 500},
            description="Optimise le contenu pour le SEO",
            parameters={
                "content": {"type": "string", "required": True},
                "target_keywords": {"type": "array", "required": True},
                "optimization_level": {"type": "string", "required": False}
            },
            response_schema={
                "type": "object",
                "properties": {
                    "optimization_id": {"type": "string"},
                    "optimized_content": {"type": "string"},
                    "improvement_score": {"type": "number"}
                }
            },
            examples={
                "request": {
                    "content": "Contenu original...",
                    "target_keywords": ["marketing digital"],
                    "optimization_level": "advanced"
                }
            }
        ))
        
        # Endpoints de reporting
        self.register_endpoint(SEOEndpoint(
            endpoint_id="generate_report",
            path="/api/v2/seo/reports/generate",
            method=RequestMethod.POST,
            endpoint_type=APIEndpointType.REPORTING,
            auth_level=AuthenticationLevel.PREMIUM,
            rate_limit={"per_hour": 20, "per_day": 100},
            description="Génère un rapport SEO",
            parameters={
                "creator_id": {"type": "string", "required": True},
                "report_type": {"type": "string", "required": True},
                "period": {"type": "object", "required": True}
            },
            response_schema={
                "type": "object",
                "properties": {
                    "report_id": {"type": "string"},
                    "download_url": {"type": "string"},
                    "preview": {"type": "object"}
                }
            },
            examples={}
        ))
        
        # Endpoints d'intelligence
        self.register_endpoint(SEOEndpoint(
            endpoint_id="get_insights",
            path="/api/v2/seo/intelligence/insights",
            method=RequestMethod.GET,
            endpoint_type=APIEndpointType.INTELLIGENCE,
            auth_level=AuthenticationLevel.ENTERPRISE,
            rate_limit={"per_hour": 200, "per_day": 2000},
            description="Récupère les insights d'intelligence SEO",
            parameters={
                "creator_id": {"type": "string", "required": True},
                "insight_type": {"type": "string", "required": False},
                "limit": {"type": "integer", "required": False}
            },
            response_schema={
                "type": "object",
                "properties": {
                    "insights": {"type": "array"},
                    "total_count": {"type": "integer"},
                    "next_page": {"type": "string"}
                }
            },
            examples={}
        ))
        
        # Endpoints de monitoring
        self.register_endpoint(SEOEndpoint(
            endpoint_id="get_metrics",
            path="/api/v2/seo/monitoring/metrics",
            method=RequestMethod.GET,
            endpoint_type=APIEndpointType.MONITORING,
            auth_level=AuthenticationLevel.BASIC,
            rate_limit={"per_hour": 500, "per_day": 5000},
            description="Récupère les métriques de performance",
            parameters={
                "creator_id": {"type": "string", "required": True},
                "metric_type": {"type": "string", "required": False},
                "timeframe": {"type": "string", "required": False}
            },
            response_schema={
                "type": "object",
                "properties": {
                    "metrics": {"type": "object"},
                    "timestamp": {"type": "string"},
                    "period": {"type": "string"}
                }
            },
            examples={}
        ))
    
    def register_endpoint(self, endpoint: SEOEndpoint):
        """
        Enregistre un nouvel endpoint
        
        Args:
            endpoint: Définition de l'endpoint
        """
        self.endpoints[endpoint.endpoint_id] = endpoint
        
        # Initialise les métriques pour cet endpoint
        self.api_metrics[endpoint.endpoint_id] = APIMetrics(
            endpoint_id=endpoint.endpoint_id,
            total_requests=0,
            successful_requests=0,
            failed_requests=0,
            average_response_time=0.0,
            peak_rps=0.0,
            error_rate=0.0,
            rate_limit_hits=0,
            unique_clients=0
        )
        
        self.logger.info(f"Endpoint enregistré: {endpoint.endpoint_id}")
    
    async def handle_request(
        self,
        endpoint_id: str,
        client_id: str,
        request_data: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None
    ) -> APIResponse:
        """
        Traite une requête API
        
        Args:
            endpoint_id: ID de l'endpoint
            client_id: ID du client
            request_data: Données de la requête
            headers: Headers HTTP
            
        Returns:
            Réponse API standardisée
        """
        start_time = time.time()
        request_id = self._generate_request_id(client_id, endpoint_id)
        
        try:
            # Vérification de l'existence de l'endpoint
            if endpoint_id not in self.endpoints:
                return self._create_error_response(
                    404, "Endpoint not found", request_id, start_time
                )
            
            endpoint = self.endpoints[endpoint_id]
            
            # Authentification
            auth_result = await self._authenticate_request(client_id, endpoint.auth_level, headers)
            if not auth_result["success"]:
                return self._create_error_response(
                    401, auth_result["message"], request_id, start_time
                )
            
            # Rate limiting
            rate_limit_result = await self._check_rate_limit(client_id, endpoint_id)
            if not rate_limit_result["allowed"]:
                self._update_metrics(endpoint_id, "rate_limit_hit")
                return self._create_error_response(
                    429, "Rate limit exceeded", request_id, start_time,
                    additional_data={"rate_limit_info": rate_limit_result}
                )
            
            # Validation des paramètres
            validation_result = self._validate_request_parameters(endpoint, request_data)
            if not validation_result["valid"]:
                return self._create_error_response(
                    400, f"Invalid parameters: {validation_result['message']}", 
                    request_id, start_time
                )
            
            # Vérification du cache
            cache_key = self._generate_cache_key(endpoint_id, request_data)
            cached_response = await self._get_cached_response(cache_key)
            if cached_response:
                self._update_metrics(endpoint_id, "cache_hit")
                cached_response.request_id = request_id
                cached_response.execution_time_ms = (time.time() - start_time) * 1000
                return cached_response
            
            # Traitement de la requête
            response_data = await self._process_request(endpoint, request_data, auth_result["user_info"])
            
            # Création de la réponse
            response = APIResponse(
                success=True,
                status_code=200,
                message="Request processed successfully",
                data=response_data,
                rate_limit_info=rate_limit_result,
                execution_time_ms=(time.time() - start_time) * 1000,
                request_id=request_id
            )
            
            # Mise en cache si approprié
            if self._should_cache_response(endpoint, response):
                await self._cache_response(cache_key, response)
            
            # Mise à jour des métriques
            self._update_metrics(endpoint_id, "success", time.time() - start_time)
            
            return response
            
        except Exception as e:
            self.logger.error(f"Erreur traitement requête {request_id}: {str(e)}")
            self._update_metrics(endpoint_id, "error")
            return self._create_error_response(
                500, f"Internal server error: {str(e)}", request_id, start_time
            )
    
    async def _authenticate_request(
        self, client_id: str, required_level: AuthenticationLevel, headers: Optional[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Authentifie une requête
        
        Args:
            client_id: ID du client
            required_level: Niveau d'authentification requis
            headers: Headers HTTP
            
        Returns:
            Résultat de l'authentification
        """
        if not self.active_config["enable_authentication"]:
            return {"success": True, "user_info": {"client_id": client_id, "level": "public"}}
        
        if required_level == AuthenticationLevel.PUBLIC:
            return {"success": True, "user_info": {"client_id": client_id, "level": "public"}}
        
        # Vérification du token d'authentification
        auth_header = headers.get("Authorization") if headers else None
        if not auth_header or not auth_header.startswith("Bearer "):
            return {"success": False, "message": "Missing or invalid authorization header"}
        
        token = auth_header.replace("Bearer ", "")
        
        # Validation du token (simulation)
        if token in self.auth_tokens:
            user_info = self.auth_tokens[token]
            user_level = AuthenticationLevel(user_info["level"])
            
            # Vérification du niveau d'accès
            level_hierarchy = {
                AuthenticationLevel.PUBLIC: 0,
                AuthenticationLevel.BASIC: 1,
                AuthenticationLevel.PREMIUM: 2,
                AuthenticationLevel.ENTERPRISE: 3,
                AuthenticationLevel.ADMIN: 4
            }
            
            if level_hierarchy[user_level] >= level_hierarchy[required_level]:
                return {"success": True, "user_info": user_info}
            else:
                return {"success": False, "message": "Insufficient access level"}
        
        return {"success": False, "message": "Invalid authentication token"}
    
    async def _check_rate_limit(self, client_id: str, endpoint_id: str) -> Dict[str, Any]:
        """
        Vérifie les limites de débit
        
        Args:
            client_id: ID du client
            endpoint_id: ID de l'endpoint
            
        Returns:
            Résultat de la vérification
        """
        if not self.active_config["enable_rate_limiting"]:
            return {"allowed": True, "remaining": 999999, "reset_time": None}
        
        endpoint = self.endpoints[endpoint_id]
        current_time = time.time()
        
        # Nettoie les anciennes requêtes (plus d'une heure)
        cutoff_time = current_time - 3600
        self.client_requests[client_id] = [
            req_time for req_time in self.client_requests[client_id] 
            if req_time > cutoff_time
        ]
        
        # Vérifie la limite horaire
        hourly_limit = endpoint.rate_limit.get("per_hour", self.active_config["default_rate_limit"])
        recent_requests = [
            req_time for req_time in self.client_requests[client_id]
            if req_time > current_time - 3600
        ]
        
        if len(recent_requests) >= hourly_limit:
            return {
                "allowed": False,
                "remaining": 0,
                "reset_time": min(recent_requests) + 3600,
                "limit": hourly_limit,
                "window": "hour"
            }
        
        # Enregistre cette requête
        self.client_requests[client_id].append(current_time)
        
        return {
            "allowed": True,
            "remaining": hourly_limit - len(recent_requests) - 1,
            "reset_time": current_time + 3600,
            "limit": hourly_limit,
            "window": "hour"
        }
    
    def _validate_request_parameters(self, endpoint: SEOEndpoint, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valide les paramètres de la requête
        
        Args:
            endpoint: Définition de l'endpoint
            data: Données à valider
            
        Returns:
            Résultat de la validation
        """
        try:
            for param_name, param_config in endpoint.parameters.items():
                if param_config.get("required", False) and param_name not in data:
                    return {
                        "valid": False,
                        "message": f"Missing required parameter: {param_name}"
                    }
                
                if param_name in data:
                    param_type = param_config.get("type")
                    value = data[param_name]
                    
                    if param_type == "string" and not isinstance(value, str):
                        return {
                            "valid": False,
                            "message": f"Parameter {param_name} must be a string"
                        }
                    elif param_type == "integer" and not isinstance(value, int):
                        return {
                            "valid": False,
                            "message": f"Parameter {param_name} must be an integer"
                        }
                    elif param_type == "array" and not isinstance(value, list):
                        return {
                            "valid": False,
                            "message": f"Parameter {param_name} must be an array"
                        }
            
            return {"valid": True, "message": "All parameters valid"}
            
        except Exception as e:
            return {"valid": False, "message": f"Validation error: {str(e)}"}
    
    def _generate_cache_key(self, endpoint_id: str, data: Dict[str, Any]) -> str:
        """Génère une clé de cache pour la requête"""
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.md5(f"{endpoint_id}_{data_str}".encode()).hexdigest()
    
    async def _get_cached_response(self, cache_key: str) -> Optional[APIResponse]:
        """Récupère une réponse en cache"""
        if not self.active_config["enable_caching"]:
            return None
        
        if cache_key in self.response_cache:
            cached_data = self.response_cache[cache_key]
            cache_time = cached_data["timestamp"]
            ttl = self.active_config["cache_ttl_seconds"]
            
            if time.time() - cache_time < ttl:
                response_data = cached_data["response"]
                return APIResponse(**response_data)
        
        return None
    
    async def _cache_response(self, cache_key: str, response: APIResponse):
        """Met en cache une réponse"""
        if self.active_config["enable_caching"]:
            self.response_cache[cache_key] = {
                "timestamp": time.time(),
                "response": {
                    "success": response.success,
                    "status_code": response.status_code,
                    "message": response.message,
                    "data": response.data,
                    "metadata": response.metadata
                }
            }
    
    def _should_cache_response(self, endpoint: SEOEndpoint, response: APIResponse) -> bool:
        """Détermine si une réponse doit être mise en cache"""
        # Cache uniquement les réponses GET réussies
        return (
            endpoint.method == RequestMethod.GET and
            response.success and
            response.status_code == 200 and
            self.active_config["enable_caching"]
        )
    
    async def _process_request(
        self, endpoint: SEOEndpoint, data: Dict[str, Any], user_info: Dict[str, Any]
    ) -> Any:
        """
        Traite la requête en fonction de l'endpoint
        
        Args:
            endpoint: Définition de l'endpoint
            data: Données de la requête
            user_info: Informations utilisateur
            
        Returns:
            Données de réponse
        """
        # Simulation du traitement selon le type d'endpoint
        if endpoint.endpoint_type == APIEndpointType.ANALYSIS:
            return await self._process_analysis_request(endpoint, data, user_info)
        elif endpoint.endpoint_type == APIEndpointType.OPTIMIZATION:
            return await self._process_optimization_request(endpoint, data, user_info)
        elif endpoint.endpoint_type == APIEndpointType.REPORTING:
            return await self._process_reporting_request(endpoint, data, user_info)
        elif endpoint.endpoint_type == APIEndpointType.INTELLIGENCE:
            return await self._process_intelligence_request(endpoint, data, user_info)
        elif endpoint.endpoint_type == APIEndpointType.MONITORING:
            return await self._process_monitoring_request(endpoint, data, user_info)
        else:
            raise ValueError(f"Unsupported endpoint type: {endpoint.endpoint_type}")
    
    async def _process_analysis_request(
        self, endpoint: SEOEndpoint, data: Dict[str, Any], user_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Traite une requête d'analyse"""
        # Simulation d'analyse SEO
        await asyncio.sleep(random.uniform(0.1, 0.5))  # Simulation temps de traitement
        
        return {
            "analysis_id": f"ana_{int(time.time() * 1000)}",
            "seo_score": random.uniform(60, 95),
            "readability_score": random.uniform(50, 90),
            "keyword_density": {kw: random.uniform(0.5, 4.0) for kw in data.get("keywords", ["seo"])},
            "recommendations": [
                "Améliorer la densité des mots-clés",
                "Optimiser les méta-descriptions",
                "Ajouter des liens internes",
                "Améliorer la structure du contenu"
            ],
            "processing_time": random.uniform(100, 500),
            "confidence_score": random.uniform(0.8, 0.95)
        }
    
    async def _process_optimization_request(
        self, endpoint: SEOEndpoint, data: Dict[str, Any], user_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Traite une requête d'optimisation"""
        await asyncio.sleep(random.uniform(0.2, 0.8))
        
        original_content = data.get("content", "")
        
        return {
            "optimization_id": f"opt_{int(time.time() * 1000)}",
            "original_content_length": len(original_content),
            "optimized_content": f"[OPTIMIZED] {original_content}",
            "improvement_score": random.uniform(10, 30),
            "applied_optimizations": [
                "keyword_density_optimization",
                "readability_improvement",
                "structure_enhancement"
            ],
            "seo_score_before": random.uniform(50, 70),
            "seo_score_after": random.uniform(75, 95),
            "meta_suggestions": {
                "title": f"Titre optimisé pour {data.get('target_keywords', ['SEO'])[0]}",
                "description": "Description optimisée pour améliorer le CTR"
            }
        }
    
    async def _process_reporting_request(
        self, endpoint: SEOEndpoint, data: Dict[str, Any], user_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Traite une requête de reporting"""
        await asyncio.sleep(random.uniform(0.5, 2.0))
        
        return {
            "report_id": f"rep_{int(time.time() * 1000)}",
            "report_type": data.get("report_type", "standard"),
            "status": "generated",
            "download_url": f"/api/v2/reports/download/{int(time.time() * 1000)}",
            "preview": {
                "total_pages": random.randint(5, 20),
                "summary": "Rapport de performance SEO généré avec succès",
                "key_metrics": {
                    "traffic_growth": f"{random.uniform(5, 25):.1f}%",
                    "ranking_improvement": f"{random.randint(3, 15)} positions",
                    "conversion_boost": f"{random.uniform(2, 12):.1f}%"
                }
            },
            "generation_time": random.uniform(500, 2000),
            "expires_at": (datetime.now() + timedelta(days=7)).isoformat()
        }
    
    async def _process_intelligence_request(
        self, endpoint: SEOEndpoint, data: Dict[str, Any], user_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Traite une requête d'intelligence"""
        await asyncio.sleep(random.uniform(0.1, 0.3))
        
        insights = []
        for i in range(random.randint(3, 8)):
            insights.append({
                "insight_id": f"ins_{int(time.time() * 1000)}_{i}",
                "category": random.choice(["performance", "competitive", "trend", "opportunity"]),
                "priority": random.choice(["low", "medium", "high"]),
                "title": f"Insight #{i+1}",
                "description": f"Description de l'insight {i+1}",
                "confidence": random.uniform(0.7, 0.95),
                "impact_score": random.uniform(3, 9)
            })
        
        return {
            "insights": insights,
            "total_count": len(insights),
            "next_page": None,
            "filters_applied": data.get("filters", {}),
            "generation_time": random.uniform(50, 200)
        }
    
    async def _process_monitoring_request(
        self, endpoint: SEOEndpoint, data: Dict[str, Any], user_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Traite une requête de monitoring"""
        await asyncio.sleep(random.uniform(0.05, 0.2))
        
        return {
            "metrics": {
                "organic_traffic": random.uniform(1000, 50000),
                "keyword_rankings": random.uniform(10, 100),
                "conversion_rate": random.uniform(1, 8),
                "bounce_rate": random.uniform(25, 75),
                "page_load_speed": random.uniform(1, 4),
                "core_web_vitals_score": random.uniform(60, 95)
            },
            "timestamp": datetime.now().isoformat(),
            "period": data.get("timeframe", "last_30_days"),
            "data_freshness": "real_time",
            "next_update": (datetime.now() + timedelta(minutes=15)).isoformat()
        }
    
    def _generate_request_id(self, client_id: str, endpoint_id: str) -> str:
        """Génère un ID unique pour la requête"""
        timestamp = int(time.time() * 1000)
        return f"req_{client_id}_{endpoint_id}_{timestamp}"
    
    def _create_error_response(
        self, status_code: int, message: str, request_id: str, start_time: float,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> APIResponse:
        """Crée une réponse d'erreur standardisée"""
        return APIResponse(
            success=False,
            status_code=status_code,
            message=message,
            error={
                "code": status_code,
                "message": message,
                "additional_data": additional_data or {}
            },
            execution_time_ms=(time.time() - start_time) * 1000,
            request_id=request_id
        )
    
    def _update_metrics(self, endpoint_id: str, event_type: str, response_time: Optional[float] = None):
        """Met à jour les métriques de l'endpoint"""
        if endpoint_id not in self.api_metrics:
            return
        
        metrics = self.api_metrics[endpoint_id]
        
        if event_type == "success":
            metrics.total_requests += 1
            metrics.successful_requests += 1
            if response_time:
                # Calcul de la moyenne mobile
                total_time = metrics.average_response_time * (metrics.successful_requests - 1)
                metrics.average_response_time = (total_time + response_time) / metrics.successful_requests
        elif event_type == "error":
            metrics.total_requests += 1
            metrics.failed_requests += 1
        elif event_type == "rate_limit_hit":
            metrics.rate_limit_hits += 1
        elif event_type == "cache_hit":
            # Cache hit, pas de mise à jour des autres métriques
            pass
        
        # Calcul du taux d'erreur
        if metrics.total_requests > 0:
            metrics.error_rate = metrics.failed_requests / metrics.total_requests
        
        # Mise à jour des stats globales
        self.stats["total_requests"] += 1
        if event_type == "error":
            self.stats["total_errors"] += 1
    
    async def create_auth_token(
        self, client_id: str, auth_level: AuthenticationLevel, expires_in: int = 3600
    ) -> str:
        """
        Crée un token d'authentification
        
        Args:
            client_id: ID du client
            auth_level: Niveau d'authentification
            expires_in: Durée de validité en secondes
            
        Returns:
            Token d'authentification
        """
        token = hashlib.sha256(f"{client_id}_{auth_level.value}_{time.time()}".encode()).hexdigest()
        
        self.auth_tokens[token] = {
            "client_id": client_id,
            "level": auth_level.value,
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(seconds=expires_in)).isoformat()
        }
        
        self.logger.info(f"Token créé pour {client_id} avec niveau {auth_level.value}")
        return token
    
    def revoke_auth_token(self, token: str) -> bool:
        """
        Révoque un token d'authentification
        
        Args:
            token: Token à révoquer
            
        Returns:
            True si révoqué avec succès
        """
        if token in self.auth_tokens:
            del self.auth_tokens[token]
            self.logger.info(f"Token révoqué: {token}")
            return True
        return False
    
    def get_api_health(self) -> Dict[str, Any]:
        """Retourne l'état de santé de l'API"""
        uptime = datetime.now() - self.stats["uptime_start"]
        
        return {
            "status": "healthy",
            "version": "2.0.0",
            "uptime_seconds": uptime.total_seconds(),
            "total_requests": self.stats["total_requests"],
            "total_errors": self.stats["total_errors"],
            "error_rate": self.stats["total_errors"] / max(1, self.stats["total_requests"]),
            "average_response_time": self.stats["average_response_time"],
            "endpoints_count": len(self.endpoints),
            "active_tokens": len(self.auth_tokens),
            "cache_size": len(self.response_cache),
            "timestamp": datetime.now().isoformat()
        }
    
    def get_endpoint_metrics(self, endpoint_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Retourne les métriques des endpoints
        
        Args:
            endpoint_id: ID de l'endpoint spécifique (optionnel)
            
        Returns:
            Métriques des endpoints
        """
        if endpoint_id:
            if endpoint_id in self.api_metrics:
                return {endpoint_id: self.api_metrics[endpoint_id].__dict__}
            else:
                return {}
        
        return {
            endpoint_id: metrics.__dict__
            for endpoint_id, metrics in self.api_metrics.items()
        }
    
    def get_gateway_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques complètes de la passerelle"""
        return {
            "version": "2.0.0",
            "configuration": self.active_config,
            "statistics": self.stats,
            "endpoints": {
                "total": len(self.endpoints),
                "by_type": {
                    endpoint_type.value: sum(
                        1 for ep in self.endpoints.values() 
                        if ep.endpoint_type == endpoint_type
                    )
                    for endpoint_type in APIEndpointType
                },
                "by_auth_level": {
                    auth_level.value: sum(
                        1 for ep in self.endpoints.values()
                        if ep.auth_level == auth_level
                    )
                    for auth_level in AuthenticationLevel
                }
            },
            "authentication": {
                "active_tokens": len(self.auth_tokens),
                "enabled": self.active_config["enable_authentication"]
            },
            "caching": {
                "cached_responses": len(self.response_cache),
                "enabled": self.active_config["enable_caching"],
                "ttl_seconds": self.active_config["cache_ttl_seconds"]
            },
            "rate_limiting": {
                "enabled": self.active_config["enable_rate_limiting"],
                "active_limits": len(self.rate_limits)
            }
        }


# === EXPORTS ===
__all__ = [
    'SEOAPIGateway',
    'SEOEndpoint',
    'APIResponse', 
    'RateLimitConfig',
    'APIMetrics',
    'AuthenticationLevel',
    'APIEndpointType',
    'RequestMethod',
    'ResponseFormat',
    'RateLimitType'
]
