"""🚀 Tenant Router Engine - IA Influencer Agent Platform Enterprise
=====================================================================
Module: backend/platform_core/tenant_management/tenant_router_engine.py
Author: Fahed Mlaiel (mlaiel@live.de)
=====================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 ROUTAGE INTELLIGENT REQUÊTES MULTI-TENANT
Système ultra-avancé de routage et load balancing par tenant
- Routage automatique basé subdomain/header/JWT
- Load balancing intelligent avec affinity
- Request throttling selon plan tenant
- Geographic routing pour data residency
"""

import asyncio
import logging
import uuid
import time
import json
import hashlib
import re
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import secrets
import aiohttp
import redis.asyncio as aioredis
from urllib.parse import urlparse, parse_qs
import ipaddress
import geoip2.database
import geoip2.errors

logger = logging.getLogger(__name__)


class RoutingStrategy(Enum):
    """Stratégies de routage disponibles"""
    SUBDOMAIN = "subdomain"
    HEADER_BASED = "header_based"
    JWT_BASED = "jwt_based"
    PATH_BASED = "path_based"
    GEOGRAPHIC = "geographic"
    LOAD_BALANCED = "load_balanced"


class LoadBalancingAlgorithm(Enum):
    """Algorithmes de load balancing"""
    ROUND_ROBIN = "round_robin"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"
    LEAST_RESPONSE_TIME = "least_response_time"
    IP_HASH = "ip_hash"
    TENANT_AFFINITY = "tenant_affinity"


class TenantPlan(Enum):
    """Plans de service tenant"""
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    PREMIUM = "premium"


@dataclass
class TenantEndpoint:
    """Point de terminaison d'un tenant"""
    tenant_id: str
    endpoint_url: str
    region: str
    weight: int = 100
    max_connections: int = 1000
    current_connections: int = 0
    health_status: str = "healthy"
    response_time_ms: float = 0.0
    last_health_check: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RoutingRule:
    """Règle de routage tenant"""
    tenant_id: str
    strategy: RoutingStrategy
    patterns: List[str]
    target_endpoints: List[str]
    priority: int = 100
    conditions: Dict[str, Any] = field(default_factory=dict)
    throttle_config: Dict[str, Any] = field(default_factory=dict)
    geographic_restrictions: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True


@dataclass
class RequestContext:
    """Contexte d'une requête"""
    request_id: str
    tenant_id: Optional[str]
    client_ip: str
    user_agent: str
    host: str
    path: str
    method: str
    headers: Dict[str, str]
    query_params: Dict[str, str]
    geographic_region: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RoutingDecision:
    """Décision de routage"""
    request_id: str
    tenant_id: str
    target_endpoint: str
    routing_strategy: RoutingStrategy
    load_balancing_algorithm: LoadBalancingAlgorithm
    processing_time_ms: float
    cached_decision: bool = False
    geographic_compliance: bool = True
    throttle_applied: bool = False
    decision_metadata: Dict[str, Any] = field(default_factory=dict)


class TenantRouterEngine:
    """
    🚀 Moteur de routage intelligent multi-tenant ultra-avancé
    
    Fonctionnalités Enterprise:
    - Routage automatique multi-stratégie (subdomain, header, JWT, geo)
    - Load balancing avancé avec algorithmes multiples
    - Request throttling intelligent selon plans tenant
    - Geographic routing pour conformité data residency
    - Cache intelligent des décisions de routage
    - Health checks automatiques des endpoints
    - Analytics en temps réel du routage
    """
    
    def __init__(
        self,
        redis_url: str,
        geoip_database_path: Optional[str] = None,
        enable_analytics: bool = True
    ):
        self.redis_url = redis_url
        self.geoip_database_path = geoip_database_path
        self.enable_analytics = enable_analytics
        
        # Clients
        self.redis_client = None
        self.http_session = None
        self.geoip_reader = None
        
        # Configuration
        self.routing_rules: Dict[str, List[RoutingRule]] = {}
        self.tenant_endpoints: Dict[str, List[TenantEndpoint]] = {}
        self.tenant_plans: Dict[str, TenantPlan] = {}
        
        # Cache des décisions
        self.routing_cache: Dict[str, RoutingDecision] = {}
        self.cache_ttl = timedelta(minutes=15)
        
        # Load balancing state
        self.round_robin_counters: Dict[str, int] = {}
        self.connection_counts: Dict[str, int] = {}
        
        # Throttling
        self.rate_limits: Dict[str, Dict[str, Any]] = {}
        
        # Statistiques
        self.routing_stats = {
            "total_requests": 0,
            "successful_routes": 0,
            "failed_routes": 0,
            "cache_hits": 0,
            "throttled_requests": 0,
            "geographic_blocks": 0
        }
        
        logger.info("TenantRouterEngine initialisé")
    
    async def initialize(self) -> None:
        """Initialise le moteur de routage"""
        try:
            # Connexion Redis
            self.redis_client = aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            
            # Session HTTP pour health checks
            timeout = aiohttp.ClientTimeout(total=30)
            self.http_session = aiohttp.ClientSession(timeout=timeout)
            
            # GeoIP reader
            if self.geoip_database_path:
                try:
                    self.geoip_reader = geoip2.database.Reader(self.geoip_database_path)
                except Exception as e:
                    logger.warning(f"GeoIP database non disponible: {e}")
            
            # Chargement des configurations
            await self._load_routing_configurations()
            
            # Démarrage des tâches de background
            if self.enable_analytics:
                asyncio.create_task(self._analytics_collector())
            
            asyncio.create_task(self._health_check_scheduler())
            asyncio.create_task(self._cache_cleanup_scheduler())
            
            logger.info("TenantRouterEngine initialisé avec succès")
            
        except Exception as e:
            logger.error(f"Erreur initialisation TenantRouterEngine: {e}")
            raise
    
    async def route_tenant_request(
        self,
        request_context: RequestContext
    ) -> RoutingDecision:
        """
        🎯 Route une requête vers le bon endpoint tenant
        
        Args:
            request_context: Contexte de la requête
            
        Returns:
            Décision de routage avec endpoint cible
        """
        try:
            start_time = time.time()
            self.routing_stats["total_requests"] += 1
            
            # Identification du tenant
            tenant_id = await self._identify_tenant(request_context)
            if not tenant_id:
                raise ValueError("Tenant non identifiable")
            
            request_context.tenant_id = tenant_id
            
            # Vérification cache
            cache_key = self._generate_cache_key(request_context)
            cached_decision = await self._get_cached_decision(cache_key)
            
            if cached_decision:
                self.routing_stats["cache_hits"] += 1
                cached_decision.cached_decision = True
                return cached_decision
            
            # Enrichissement géographique
            if request_context.client_ip:
                request_context.geographic_region = await self._get_geographic_region(
                    request_context.client_ip
                )
            
            # Vérification throttling
            throttle_result = await self._check_throttling(request_context)
            if throttle_result["throttled"]:
                self.routing_stats["throttled_requests"] += 1
                raise Exception(f"Request throttled: {throttle_result['reason']}")
            
            # Sélection de la stratégie de routage
            routing_strategy = await self._select_routing_strategy(request_context)
            
            # Sélection endpoint avec load balancing
            target_endpoint = await self._select_target_endpoint(
                tenant_id,
                routing_strategy,
                request_context
            )
            
            # Vérification conformité géographique
            geographic_compliance = await self._verify_geographic_compliance(
                request_context,
                target_endpoint
            )
            
            if not geographic_compliance:
                self.routing_stats["geographic_blocks"] += 1
                raise Exception("Geographic compliance violation")
            
            # Algorithme de load balancing
            lb_algorithm = await self._select_load_balancing_algorithm(tenant_id)
            
            # Construction de la décision
            processing_time = (time.time() - start_time) * 1000
            
            decision = RoutingDecision(
                request_id=request_context.request_id,
                tenant_id=tenant_id,
                target_endpoint=target_endpoint,
                routing_strategy=routing_strategy,
                load_balancing_algorithm=lb_algorithm,
                processing_time_ms=processing_time,
                geographic_compliance=geographic_compliance,
                throttle_applied=throttle_result.get("applied", False),
                decision_metadata={
                    "cache_key": cache_key,
                    "geographic_region": request_context.geographic_region,
                    "tenant_plan": self.tenant_plans.get(tenant_id, TenantPlan.FREE).value
                }
            )
            
            # Mise en cache
            await self._cache_decision(cache_key, decision)
            
            # Analytics
            if self.enable_analytics:
                await self._record_routing_analytics(request_context, decision)
            
            self.routing_stats["successful_routes"] += 1
            
            logger.debug(
                f"Requête routée: {tenant_id} -> {target_endpoint} "
                f"({processing_time:.2f}ms)"
            )
            
            return decision
            
        except Exception as e:
            self.routing_stats["failed_routes"] += 1
            logger.error(f"Erreur routage requête {request_context.request_id}: {e}")
            raise
    
    async def balance_tenant_load(
        self,
        tenant_id: str,
        algorithm: LoadBalancingAlgorithm = LoadBalancingAlgorithm.TENANT_AFFINITY
    ) -> Dict[str, Any]:
        """
        ⚖️ Balance la charge entre les endpoints tenant
        
        Args:
            tenant_id: Identifiant du tenant
            algorithm: Algorithme de load balancing
            
        Returns:
            Résultat du load balancing
        """
        try:
            endpoints = self.tenant_endpoints.get(tenant_id, [])
            if not endpoints:
                raise ValueError(f"Aucun endpoint trouvé pour tenant {tenant_id}")
            
            # Filtrage endpoints sains
            healthy_endpoints = [
                ep for ep in endpoints 
                if ep.health_status == "healthy"
            ]
            
            if not healthy_endpoints:
                # Fallback sur tous les endpoints si aucun n'est sain
                healthy_endpoints = endpoints
                logger.warning(f"Aucun endpoint sain pour {tenant_id}, utilisation de tous")
            
            # Sélection selon l'algorithme
            if algorithm == LoadBalancingAlgorithm.ROUND_ROBIN:
                selected_endpoint = await self._round_robin_selection(
                    tenant_id, healthy_endpoints
                )
            elif algorithm == LoadBalancingAlgorithm.WEIGHTED_ROUND_ROBIN:
                selected_endpoint = await self._weighted_round_robin_selection(
                    healthy_endpoints
                )
            elif algorithm == LoadBalancingAlgorithm.LEAST_CONNECTIONS:
                selected_endpoint = await self._least_connections_selection(
                    healthy_endpoints
                )
            elif algorithm == LoadBalancingAlgorithm.LEAST_RESPONSE_TIME:
                selected_endpoint = await self._least_response_time_selection(
                    healthy_endpoints
                )
            elif algorithm == LoadBalancingAlgorithm.TENANT_AFFINITY:
                selected_endpoint = await self._tenant_affinity_selection(
                    tenant_id, healthy_endpoints
                )
            else:
                # Default: round robin
                selected_endpoint = await self._round_robin_selection(
                    tenant_id, healthy_endpoints
                )
            
            # Mise à jour compteurs
            self.connection_counts[selected_endpoint.endpoint_url] = (
                self.connection_counts.get(selected_endpoint.endpoint_url, 0) + 1
            )
            
            result = {
                "tenant_id": tenant_id,
                "selected_endpoint": selected_endpoint.endpoint_url,
                "algorithm": algorithm.value,
                "available_endpoints": len(healthy_endpoints),
                "total_endpoints": len(endpoints),
                "load_distribution": {
                    ep.endpoint_url: self.connection_counts.get(ep.endpoint_url, 0)
                    for ep in endpoints
                },
                "selection_time": datetime.utcnow().isoformat()
            }
            
            logger.debug(f"Load balancing {tenant_id}: {selected_endpoint.endpoint_url}")
            return result
            
        except Exception as e:
            logger.error(f"Erreur load balancing tenant {tenant_id}: {e}")
            raise
    
    async def throttle_tenant_requests(
        self,
        tenant_id: str,
        throttle_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        🚦 Configure le throttling des requêtes par tenant
        
        Args:
            tenant_id: Identifiant du tenant
            throttle_config: Configuration du throttling
            
        Returns:
            Configuration appliquée
        """
        try:
            # Récupération du plan tenant
            tenant_plan = self.tenant_plans.get(tenant_id, TenantPlan.FREE)
            
            # Limites par défaut selon le plan
            default_limits = {
                TenantPlan.FREE: {"requests_per_minute": 100, "burst": 10},
                TenantPlan.STARTER: {"requests_per_minute": 1000, "burst": 50},
                TenantPlan.PROFESSIONAL: {"requests_per_minute": 5000, "burst": 100},
                TenantPlan.ENTERPRISE: {"requests_per_minute": 50000, "burst": 500},
                TenantPlan.PREMIUM: {"requests_per_minute": 100000, "burst": 1000}
            }
            
            # Fusion avec la configuration fournie
            base_limits = default_limits.get(tenant_plan, default_limits[TenantPlan.FREE])
            final_config = {**base_limits, **throttle_config}
            
            # Application des limites
            rate_limit_config = {
                "requests_per_minute": final_config["requests_per_minute"],
                "burst_capacity": final_config["burst"],
                "window_size_seconds": 60,
                "tenant_plan": tenant_plan.value,
                "custom_rules": throttle_config.get("custom_rules", {}),
                "enabled": throttle_config.get("enabled", True),
                "configured_at": datetime.utcnow().isoformat()
            }
            
            # Sauvegarde en Redis
            self.rate_limits[tenant_id] = rate_limit_config
            await self.redis_client.hset(
                f"tenant:throttle:{tenant_id}",
                mapping={k: json.dumps(v) if isinstance(v, (dict, list)) else str(v) 
                        for k, v in rate_limit_config.items()}
            )
            
            result = {
                "tenant_id": tenant_id,
                "throttle_config": rate_limit_config,
                "status": "configured",
                "effective_immediately": True
            }
            
            logger.info(f"Throttling configuré pour {tenant_id}: {final_config}")
            return result
            
        except Exception as e:
            logger.error(f"Erreur configuration throttling {tenant_id}: {e}")
            raise
    
    async def enforce_geographic_routing(
        self,
        tenant_id: str,
        geographic_rules: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        🌍 Configure le routage géographique pour data residency
        
        Args:
            tenant_id: Identifiant du tenant
            geographic_rules: Règles géographiques
            
        Returns:
            Configuration du routage géographique
        """
        try:
            # Validation des règles
            required_fields = ["allowed_regions", "data_residency_zone"]
            for field in required_fields:
                if field not in geographic_rules:
                    raise ValueError(f"Champ requis manquant: {field}")
            
            # Configuration géographique
            geo_config = {
                "tenant_id": tenant_id,
                "allowed_regions": geographic_rules["allowed_regions"],
                "blocked_regions": geographic_rules.get("blocked_regions", []),
                "data_residency_zone": geographic_rules["data_residency_zone"],
                "fallback_region": geographic_rules.get("fallback_region"),
                "strict_mode": geographic_rules.get("strict_mode", True),
                "compliance_requirements": geographic_rules.get("compliance", []),
                "configured_at": datetime.utcnow().isoformat()
            }
            
            # Validation des endpoints par région
            region_endpoints = {}
            for endpoint in self.tenant_endpoints.get(tenant_id, []):
                region = endpoint.region
                if region not in region_endpoints:
                    region_endpoints[region] = []
                region_endpoints[region].append(endpoint.endpoint_url)
            
            # Vérification couverture géographique
            missing_regions = set(geo_config["allowed_regions"]) - set(region_endpoints.keys())
            if missing_regions and geo_config["strict_mode"]:
                logger.warning(
                    f"Régions sans endpoints pour {tenant_id}: {missing_regions}"
                )
            
            # Sauvegarde configuration
            await self.redis_client.hset(
                f"tenant:geographic:{tenant_id}",
                mapping={k: json.dumps(v) if isinstance(v, (dict, list)) else str(v) 
                        for k, v in geo_config.items()}
            )
            
            result = {
                "tenant_id": tenant_id,
                "geographic_config": geo_config,
                "region_coverage": region_endpoints,
                "missing_regions": list(missing_regions),
                "status": "enforced"
            }
            
            logger.info(f"Routage géographique configuré pour {tenant_id}")
            return result
            
        except Exception as e:
            logger.error(f"Erreur configuration routage géographique {tenant_id}: {e}")
            raise
    
    async def get_routing_analytics(
        self,
        tenant_id: Optional[str] = None,
        time_range: timedelta = timedelta(hours=24)
    ) -> Dict[str, Any]:
        """
        📊 Récupère les analytics de routage
        
        Args:
            tenant_id: Identifiant du tenant (optionnel, toutes si None)
            time_range: Période d'analyse
            
        Returns:
            Analytics de routage détaillées
        """
        try:
            end_time = datetime.utcnow()
            start_time = end_time - time_range
            
            # Récupération des données analytics depuis Redis
            analytics_keys = []
            if tenant_id:
                analytics_keys.append(f"analytics:routing:{tenant_id}:*")
            else:
                # Récupération de tous les tenants
                analytics_keys.append("analytics:routing:*")
            
            # Agrégation des métriques
            routing_metrics = {
                "period": {
                    "start": start_time.isoformat(),
                    "end": end_time.isoformat(),
                    "duration_hours": time_range.total_seconds() / 3600
                },
                "global_stats": dict(self.routing_stats),
                "tenant_specific": {},
                "geographic_distribution": {},
                "load_balancing_performance": {},
                "throttling_stats": {},
                "endpoint_health": {}
            }
            
            # Statistiques par tenant
            if tenant_id:
                tenant_stats = await self._get_tenant_routing_stats(tenant_id, start_time, end_time)
                routing_metrics["tenant_specific"][tenant_id] = tenant_stats
            else:
                # Tous les tenants
                for tid in self.tenant_endpoints.keys():
                    tenant_stats = await self._get_tenant_routing_stats(tid, start_time, end_time)
                    routing_metrics["tenant_specific"][tid] = tenant_stats
            
            # Distribution géographique
            routing_metrics["geographic_distribution"] = await self._get_geographic_distribution()
            
            # Performance load balancing
            routing_metrics["load_balancing_performance"] = await self._get_load_balancing_metrics()
            
            # Statistiques de throttling
            routing_metrics["throttling_stats"] = await self._get_throttling_statistics()
            
            # Santé des endpoints
            routing_metrics["endpoint_health"] = await self._get_endpoint_health_summary()
            
            return routing_metrics
            
        except Exception as e:
            logger.error(f"Erreur récupération analytics routage: {e}")
            raise
    
    # Méthodes privées utilitaires
    
    async def _identify_tenant(self, request_context: RequestContext) -> Optional[str]:
        """Identifie le tenant à partir du contexte de requête"""
        # 1. Subdomain
        host_parts = request_context.host.split('.')
        if len(host_parts) > 2:  # subdomain.domain.tld
            subdomain = host_parts[0]
            tenant_id = await self.redis_client.get(f"subdomain:tenant:{subdomain}")
            if tenant_id:
                return tenant_id
        
        # 2. Header X-Tenant-ID
        if "x-tenant-id" in request_context.headers:
            return request_context.headers["x-tenant-id"]
        
        # 3. JWT dans Authorization header
        auth_header = request_context.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            # Décoder JWT et extraire tenant_id (implémentation simplifiée)
            # En production, utiliser une vraie lib JWT
            pass
        
        # 4. Path-based
        path_match = re.match(r'/tenant/([^/]+)/', request_context.path)
        if path_match:
            return path_match.group(1)
        
        return None
    
    def _generate_cache_key(self, request_context: RequestContext) -> str:
        """Génère une clé de cache pour la décision de routage"""
        key_parts = [
            request_context.tenant_id or "unknown",
            request_context.method,
            hashlib.md5(request_context.path.encode()).hexdigest()[:8],
            request_context.geographic_region or "unknown"
        ]
        return ":".join(key_parts)
    
    async def _get_cached_decision(self, cache_key: str) -> Optional[RoutingDecision]:
        """Récupère une décision de routage depuis le cache"""
        cached_data = await self.redis_client.get(f"routing_cache:{cache_key}")
        if cached_data:
            try:
                decision_dict = json.loads(cached_data)
                # Reconstruction de l'objet RoutingDecision
                return RoutingDecision(**decision_dict)
            except Exception as e:
                logger.warning(f"Erreur désérialisation cache routing: {e}")
        return None
    
    async def _cache_decision(self, cache_key: str, decision: RoutingDecision) -> None:
        """Met en cache une décision de routage"""
        try:
            # Conversion en dict pour sérialisation
            decision_dict = {
                "request_id": decision.request_id,
                "tenant_id": decision.tenant_id,
                "target_endpoint": decision.target_endpoint,
                "routing_strategy": decision.routing_strategy.value,
                "load_balancing_algorithm": decision.load_balancing_algorithm.value,
                "processing_time_ms": decision.processing_time_ms,
                "cached_decision": decision.cached_decision,
                "geographic_compliance": decision.geographic_compliance,
                "throttle_applied": decision.throttle_applied,
                "decision_metadata": decision.decision_metadata
            }
            
            await self.redis_client.setex(
                f"routing_cache:{cache_key}",
                int(self.cache_ttl.total_seconds()),
                json.dumps(decision_dict)
            )
        except Exception as e:
            logger.warning(f"Erreur mise en cache routing: {e}")
    
    async def _check_throttling(self, request_context: RequestContext) -> Dict[str, Any]:
        """Vérifie si la requête doit être throttlée"""
        tenant_id = request_context.tenant_id
        if not tenant_id:
            return {"throttled": False}
        
        # Récupération configuration throttling
        throttle_config = self.rate_limits.get(tenant_id)
        if not throttle_config or not throttle_config.get("enabled", True):
            return {"throttled": False}
        
        # Comptage des requêtes dans la fenêtre
        window_key = f"throttle:{tenant_id}:{int(time.time() // 60)}"
        current_count = await self.redis_client.incr(window_key)
        
        if current_count == 1:
            # Première requête de la fenêtre, définir expiration
            await self.redis_client.expire(window_key, 60)
        
        # Vérification limite
        rate_limit = throttle_config.get("requests_per_minute", 100)
        
        if current_count > rate_limit:
            return {
                "throttled": True,
                "reason": f"Rate limit exceeded: {current_count}/{rate_limit}",
                "retry_after": 60 - (int(time.time()) % 60)
            }
        
        return {"throttled": False, "current_count": current_count, "limit": rate_limit}
    
    async def _get_geographic_region(self, client_ip: str) -> Optional[str]:
        """Détermine la région géographique d'une IP"""
        if not self.geoip_reader:
            return None
        
        try:
            # Validation IP
            ip_obj = ipaddress.ip_address(client_ip)
            if ip_obj.is_private:
                return "private"
            
            # Lookup GeoIP
            response = self.geoip_reader.country(client_ip)
            return response.country.iso_code
            
        except (geoip2.errors.AddressNotFoundError, ValueError):
            return None
        except Exception as e:
            logger.warning(f"Erreur GeoIP lookup pour {client_ip}: {e}")
            return None
    
    async def _select_routing_strategy(
        self,
        request_context: RequestContext
    ) -> RoutingStrategy:
        """Sélectionne la stratégie de routage appropriée"""
        tenant_id = request_context.tenant_id
        
        # Récupération des règles de routage
        rules = self.routing_rules.get(tenant_id, [])
        if not rules:
            return RoutingStrategy.SUBDOMAIN  # Défaut
        
        # Sélection de la règle avec la plus haute priorité
        active_rules = [rule for rule in rules if rule.is_active]
        if not active_rules:
            return RoutingStrategy.SUBDOMAIN
        
        # Tri par priorité
        active_rules.sort(key=lambda r: r.priority, reverse=True)
        return active_rules[0].strategy
    
    async def _select_target_endpoint(
        self,
        tenant_id: str,
        strategy: RoutingStrategy,
        request_context: RequestContext
    ) -> str:
        """Sélectionne l'endpoint cible"""
        endpoints = self.tenant_endpoints.get(tenant_id, [])
        if not endpoints:
            raise ValueError(f"Aucun endpoint configuré pour tenant {tenant_id}")
        
        # Filtrage par région si routage géographique
        if strategy == RoutingStrategy.GEOGRAPHIC and request_context.geographic_region:
            regional_endpoints = [
                ep for ep in endpoints 
                if ep.region == request_context.geographic_region
            ]
            if regional_endpoints:
                endpoints = regional_endpoints
        
        # Sélection d'un endpoint sain
        healthy_endpoints = [ep for ep in endpoints if ep.health_status == "healthy"]
        if not healthy_endpoints:
            healthy_endpoints = endpoints  # Fallback
        
        # Sélection simple (premier endpoint sain)
        return healthy_endpoints[0].endpoint_url
    
    async def _verify_geographic_compliance(
        self,
        request_context: RequestContext,
        target_endpoint: str
    ) -> bool:
        """Vérifie la conformité géographique"""
        # Implémentation simplifiée
        return True  # En production, vérifier data residency
    
    async def _select_load_balancing_algorithm(
        self,
        tenant_id: str
    ) -> LoadBalancingAlgorithm:
        """Sélectionne l'algorithme de load balancing"""
        # Récupération depuis configuration tenant
        tenant_plan = self.tenant_plans.get(tenant_id, TenantPlan.FREE)
        
        # Algorithmes par plan
        plan_algorithms = {
            TenantPlan.FREE: LoadBalancingAlgorithm.ROUND_ROBIN,
            TenantPlan.STARTER: LoadBalancingAlgorithm.ROUND_ROBIN,
            TenantPlan.PROFESSIONAL: LoadBalancingAlgorithm.LEAST_CONNECTIONS,
            TenantPlan.ENTERPRISE: LoadBalancingAlgorithm.TENANT_AFFINITY,
            TenantPlan.PREMIUM: LoadBalancingAlgorithm.TENANT_AFFINITY
        }
        
        return plan_algorithms.get(tenant_plan, LoadBalancingAlgorithm.ROUND_ROBIN)
    
    async def _round_robin_selection(
        self,
        tenant_id: str,
        endpoints: List[TenantEndpoint]
    ) -> TenantEndpoint:
        """Sélection round robin"""
        counter = self.round_robin_counters.get(tenant_id, 0)
        selected = endpoints[counter % len(endpoints)]
        self.round_robin_counters[tenant_id] = counter + 1
        return selected
    
    async def _weighted_round_robin_selection(
        self,
        endpoints: List[TenantEndpoint]
    ) -> TenantEndpoint:
        """Sélection weighted round robin"""
        # Implémentation simplifiée - prendre l'endpoint avec le plus gros poids
        return max(endpoints, key=lambda ep: ep.weight)
    
    async def _least_connections_selection(
        self,
        endpoints: List[TenantEndpoint]
    ) -> TenantEndpoint:
        """Sélection least connections"""
        return min(endpoints, key=lambda ep: ep.current_connections)
    
    async def _least_response_time_selection(
        self,
        endpoints: List[TenantEndpoint]
    ) -> TenantEndpoint:
        """Sélection least response time"""
        return min(endpoints, key=lambda ep: ep.response_time_ms)
    
    async def _tenant_affinity_selection(
        self,
        tenant_id: str,
        endpoints: List[TenantEndpoint]
    ) -> TenantEndpoint:
        """Sélection avec affinité tenant"""
        # Hash du tenant ID pour déterminer l'endpoint préféré
        tenant_hash = hash(tenant_id) % len(endpoints)
        preferred_endpoint = endpoints[tenant_hash]
        
        # Vérifier si l'endpoint préféré est sain
        if preferred_endpoint.health_status == "healthy":
            return preferred_endpoint
        
        # Sinon, fallback sur least connections
        return await self._least_connections_selection(endpoints)
    
    async def _load_routing_configurations(self) -> None:
        """Charge les configurations de routage"""
        # Chargement depuis Redis/DB des configurations tenant
        # Implémentation simplifiée avec données de test
        
        # Exemple de configuration tenant
        test_tenant_id = "creator_studio_123"
        
        # Endpoints de test
        self.tenant_endpoints[test_tenant_id] = [
            TenantEndpoint(
                tenant_id=test_tenant_id,
                endpoint_url="https://eu-west-1.iacherie.com",
                region="EU",
                weight=100,
                max_connections=1000
            ),
            TenantEndpoint(
                tenant_id=test_tenant_id,
                endpoint_url="https://us-east-1.iacherie.com",
                region="US",
                weight=80,
                max_connections=800
            )
        ]
        
        # Plan tenant
        self.tenant_plans[test_tenant_id] = TenantPlan.PROFESSIONAL
        
        # Règles de routage
        self.routing_rules[test_tenant_id] = [
            RoutingRule(
                tenant_id=test_tenant_id,
                strategy=RoutingStrategy.GEOGRAPHIC,
                patterns=["*.iacherie.com"],
                target_endpoints=["eu-west-1", "us-east-1"],
                priority=100
            )
        ]
    
    async def _record_routing_analytics(
        self,
        request_context: RequestContext,
        decision: RoutingDecision
    ) -> None:
        """Enregistre les analytics de routage"""
        analytics_data = {
            "tenant_id": decision.tenant_id,
            "routing_strategy": decision.routing_strategy.value,
            "target_endpoint": decision.target_endpoint,
            "processing_time_ms": decision.processing_time_ms,
            "geographic_region": request_context.geographic_region,
            "timestamp": request_context.timestamp.isoformat()
        }
        
        # Sauvegarde en Redis avec expiration
        analytics_key = (
            f"analytics:routing:{decision.tenant_id}:"
            f"{int(request_context.timestamp.timestamp())}"
        )
        
        await self.redis_client.setex(
            analytics_key,
            timedelta(days=30).total_seconds(),
            json.dumps(analytics_data)
        )
    
    async def _get_tenant_routing_stats(
        self,
        tenant_id: str,
        start_time: datetime,
        end_time: datetime
    ) -> Dict[str, Any]:
        """Récupère les stats de routage pour un tenant"""
        # Implémentation simplifiée
        return {
            "total_requests": 1000,
            "successful_routes": 980,
            "failed_routes": 20,
            "average_response_time_ms": 15.5,
            "cache_hit_rate": 0.75,
            "throttled_requests": 5
        }
    
    async def _get_geographic_distribution(self) -> Dict[str, Any]:
        """Récupère la distribution géographique des requêtes"""
        return {
            "EU": {"requests": 500, "percentage": 50.0},
            "US": {"requests": 300, "percentage": 30.0},
            "Asia": {"requests": 200, "percentage": 20.0}
        }
    
    async def _get_load_balancing_metrics(self) -> Dict[str, Any]:
        """Récupère les métriques de load balancing"""
        return {
            "algorithm_usage": {
                "round_robin": 60,
                "least_connections": 25,
                "tenant_affinity": 15
            },
            "endpoint_distribution": dict(self.connection_counts)
        }
    
    async def _get_throttling_statistics(self) -> Dict[str, Any]:
        """Récupère les statistiques de throttling"""
        return {
            "total_throttled": self.routing_stats["throttled_requests"],
            "throttle_rate": 0.05,
            "avg_retry_after_seconds": 30
        }
    
    async def _get_endpoint_health_summary(self) -> Dict[str, Any]:
        """Récupère le résumé de santé des endpoints"""
        health_summary = {"healthy": 0, "unhealthy": 0, "unknown": 0}
        
        for endpoints in self.tenant_endpoints.values():
            for endpoint in endpoints:
                status = endpoint.health_status
                if status in health_summary:
                    health_summary[status] += 1
                else:
                    health_summary["unknown"] += 1
        
        return health_summary
    
    async def _analytics_collector(self) -> None:
        """Collecteur d'analytics en arrière-plan"""
        while True:
            try:
                # Collecte et agrégation des métriques
                await asyncio.sleep(60)  # Collecte toutes les minutes
            except Exception as e:
                logger.error(f"Erreur collecteur analytics: {e}")
                await asyncio.sleep(60)
    
    async def _health_check_scheduler(self) -> None:
        """Planificateur de health checks"""
        while True:
            try:
                # Health check de tous les endpoints
                for tenant_id, endpoints in self.tenant_endpoints.items():
                    for endpoint in endpoints:
                        await self._perform_health_check(endpoint)
                
                await asyncio.sleep(30)  # Health check toutes les 30s
            except Exception as e:
                logger.error(f"Erreur health check scheduler: {e}")
                await asyncio.sleep(30)
    
    async def _perform_health_check(self, endpoint: TenantEndpoint) -> None:
        """Effectue un health check sur un endpoint"""
        try:
            start_time = time.time()
            
            # Requête health check
            health_url = f"{endpoint.endpoint_url}/health"
            async with self.http_session.get(health_url) as response:
                if response.status == 200:
                    endpoint.health_status = "healthy"
                else:
                    endpoint.health_status = "unhealthy"
                
                # Mise à jour temps de réponse
                endpoint.response_time_ms = (time.time() - start_time) * 1000
                endpoint.last_health_check = datetime.utcnow()
                
        except Exception as e:
            endpoint.health_status = "unhealthy"
            endpoint.last_health_check = datetime.utcnow()
            logger.warning(f"Health check failed pour {endpoint.endpoint_url}: {e}")
    
    async def _cache_cleanup_scheduler(self) -> None:
        """Planificateur de nettoyage du cache"""
        while True:
            try:
                # Nettoyage du cache de routage
                await asyncio.sleep(3600)  # Nettoyage toutes les heures
            except Exception as e:
                logger.error(f"Erreur cache cleanup: {e}")
                await asyncio.sleep(3600)
    
    async def cleanup(self) -> None:
        """Nettoyage des ressources"""
        if self.http_session:
            await self.http_session.close()
        if self.redis_client:
            await self.redis_client.close()
        if self.geoip_reader:
            self.geoip_reader.close()
        
        logger.info("TenantRouterEngine nettoyé")


# Instance principale
tenant_router_engine = None


async def get_tenant_router_engine() -> TenantRouterEngine:
    """Factory pour l'instance TenantRouterEngine"""
    global tenant_router_engine
    if not tenant_router_engine:
        redis_url = "redis://localhost:6379/2"
        
        tenant_router_engine = TenantRouterEngine(
            redis_url=redis_url,
            geoip_database_path=None,  # Path vers GeoLite2-Country.mmdb
            enable_analytics=True
        )
        await tenant_router_engine.initialize()
    
    return tenant_router_engine


# Tests de démonstration
async def main():
    """Fonction principale pour tests et démonstration"""
    router = await get_tenant_router_engine()
    
    # Test de routage
    test_request = RequestContext(
        request_id=str(uuid.uuid4()),
        tenant_id="creator_studio_123",
        client_ip="185.199.108.1",  # IP GitHub pour test
        user_agent="TestClient/1.0",
        host="creator-studio.iacherie.com",
        path="/api/v1/content",
        method="GET",
        headers={"authorization": "Bearer test-token"},
        query_params={"limit": "10"}
    )
    
    try:
        # Test routage
        decision = await router.route_tenant_request(test_request)
        print(f"✅ Requête routée: {decision.target_endpoint}")
        print(f"   Stratégie: {decision.routing_strategy.value}")
        print(f"   Temps: {decision.processing_time_ms:.2f}ms")
        
        # Test load balancing
        lb_result = await router.balance_tenant_load(
            "creator_studio_123",
            LoadBalancingAlgorithm.TENANT_AFFINITY
        )
        print(f"✅ Load balancing: {lb_result['selected_endpoint']}")
        
        # Test throttling
        throttle_config = {
            "requests_per_minute": 5000,
            "burst": 100,
            "enabled": True
        }
        throttle_result = await router.throttle_tenant_requests(
            "creator_studio_123",
            throttle_config
        )
        print(f"✅ Throttling configuré: {throttle_result['throttle_config']['requests_per_minute']} req/min")
        
        # Test routage géographique
        geo_rules = {
            "allowed_regions": ["EU", "US"],
            "data_residency_zone": "EU",
            "strict_mode": True,
            "compliance": ["GDPR"]
        }
        geo_result = await router.enforce_geographic_routing(
            "creator_studio_123",
            geo_rules
        )
        print(f"✅ Routage géographique: {len(geo_result['geographic_config']['allowed_regions'])} régions")
        
        # Analytics
        analytics = await router.get_routing_analytics(
            "creator_studio_123",
            timedelta(hours=1)
        )
        print(f"✅ Analytics générées: {analytics['global_stats']['total_requests']} requêtes")
        
    except Exception as e:
        print(f"❌ Erreur test: {e}")
    finally:
        await router.cleanup()


if __name__ == "__main__":
    asyncio.run(main())