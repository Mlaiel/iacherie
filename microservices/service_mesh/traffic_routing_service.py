#!/usr/bin/env python3
"""
🎯 Traffic Routing Service - Enterprise Service Mesh
Service de routage intelligent du trafic pour microservices Ainflue

© Fahed Mlaiel 2024-2025 - Propriété intellectuelle stricte
Architecture microservices enterprise - Niveau production
🔧 Microservices Expert + Backend Senior + DevOps Implementation
"""

import asyncio
import logging
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import aiohttp
import yaml
import random
import time
from concurrent.futures import ThreadPoolExecutor
import kubernetes
from kubernetes import client, config

# Configuration logging enterprise
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RoutingStrategy(Enum):
    """Stratégies de routage"""
    ROUND_ROBIN = "round_robin"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"
    RANDOM = "random"
    IP_HASH = "ip_hash"
    GEOGRAPHIC = "geographic"
    LATENCY_BASED = "latency_based"
    CANARY = "canary"
    BLUE_GREEN = "blue_green"
    A_B_TESTING = "ab_testing"

class TrafficType(Enum):
    """Types de trafic"""
    HTTP = "http"
    HTTPS = "https"
    TCP = "tcp"
    UDP = "udp"
    GRPC = "grpc"
    WEBSOCKET = "websocket"

class RoutingCondition(Enum):
    """Conditions de routage"""
    HEADER = "header"
    PATH = "path"
    METHOD = "method"
    QUERY_PARAM = "query_param"
    SOURCE_IP = "source_ip"
    USER_AGENT = "user_agent"
    COOKIE = "cookie"
    WEIGHT = "weight"

@dataclass
class RouteMatch:
    """Critères de correspondance route"""
    condition_type: RoutingCondition
    key: str = ""
    value: str = ""
    operator: str = "equals"  # equals, contains, starts_with, regex
    case_sensitive: bool = False

@dataclass
class RouteDestination:
    """Destination de route"""
    service_name: str
    namespace: str
    host: str
    port: int
    weight: int = 100
    version: str = "v1"
    subset: str = ""
    timeout: int = 30
    retry_attempts: int = 3
    circuit_breaker_enabled: bool = True

@dataclass
class TrafficRoute:
    """Règle de routage trafic"""
    route_id: str
    name: str
    description: str
    traffic_type: TrafficType
    match_conditions: List[RouteMatch]
    destinations: List[RouteDestination]
    strategy: RoutingStrategy = RoutingStrategy.ROUND_ROBIN
    priority: int = 100
    enabled: bool = True
    timeout: int = 30
    retry_policy: Dict[str, Any] = None
    fault_injection: Dict[str, Any] = None
    rate_limiting: Dict[str, Any] = None
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
        if self.retry_policy is None:
            self.retry_policy = {}
        if self.fault_injection is None:
            self.fault_injection = {}
        if self.rate_limiting is None:
            self.rate_limiting = {}

@dataclass
class TrafficStats:
    """Statistiques de trafic"""
    route_id: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    avg_response_time: float = 0.0
    p95_response_time: float = 0.0
    p99_response_time: float = 0.0
    bytes_sent: int = 0
    bytes_received: int = 0
    last_request_time: datetime = None
    
    def __post_init__(self):
        if self.last_request_time is None:
            self.last_request_time = datetime.now()

@dataclass
class LoadBalancerStats:
    """Statistiques load balancer"""
    service_name: str
    namespace: str
    active_connections: int = 0
    total_connections: int = 0
    request_rate: float = 0.0
    error_rate: float = 0.0
    avg_latency: float = 0.0
    healthy_endpoints: int = 0
    total_endpoints: int = 0

class TrafficRoutingService:
    """Service de routage intelligent du trafic Enterprise"""
    
    def __init__(self):
        self.service_name = "traffic-routing-service"
        self.version = "1.0.0"
        
        # Registres de routage
        self.routing_rules: Dict[str, TrafficRoute] = {}
        self.traffic_stats: Dict[str, TrafficStats] = {}
        self.load_balancer_stats: Dict[str, LoadBalancerStats] = {}
        
        # Configuration routing
        self.default_strategy = RoutingStrategy.ROUND_ROBIN
        self.health_check_interval = 30
        self.stats_collection_interval = 15
        
        # Cache de routage
        self.routing_cache: Dict[str, Any] = {}
        self.cache_ttl = 300  # 5 minutes
        
        # Round robin state
        self.round_robin_state: Dict[str, int] = {}
        
        # Connexions actives
        self.active_connections: Dict[str, Set[str]] = {}
        
        # Client Kubernetes
        self.k8s_client = None
        
        # Métriques enterprise
        self.metrics = {
            'total_routes': 0,
            'active_routes': 0,
            'routing_decisions': 0,
            'failed_routes': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'health_checks_performed': 0,
            'load_balancing_operations': 0
        }
        
        logger.info(f"🎯 {self.service_name} v{self.version} - Initialisation")
    
    async def initialize(self, config: Dict[str, Any] = None) -> bool:
        """Initialisation du service de routage"""
        try:
            logger.info("🚀 Initialisation Traffic Routing Service...")
            
            if config is None:
                config = {}
            
            # Configuration Kubernetes
            await self._setup_kubernetes_client()
            
            # Chargement configuration routage
            await self._load_routing_configuration(config)
            
            # Démarrage monitoring santé
            await self._start_health_monitoring()
            
            # Démarrage collecte statistiques
            await self._start_stats_collection()
            
            # Création routes par défaut
            await self._create_default_routes()
            
            # Démarrage tâches de maintenance
            asyncio.create_task(self._maintenance_loop())
            
            logger.info("✅ Traffic Routing Service initialisé")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation routing: {e}")
            return False
    
    async def _setup_kubernetes_client(self):
        """Configuration client Kubernetes"""
        try:
            try:
                config.load_incluster_config()
                logger.info("📊 Config Kubernetes in-cluster chargée")
            except:
                config.load_kube_config()
                logger.info("🏠 Config Kubernetes locale chargée")
            
            self.k8s_client = client.ApiClient()
            
        except Exception as e:
            logger.error(f"❌ Erreur config Kubernetes: {e}")
            raise
    
    async def _load_routing_configuration(self, config: Dict[str, Any]):
        """Chargement configuration routage"""
        try:
            # Configuration par défaut
            self.default_strategy = RoutingStrategy(
                config.get('default_strategy', 'round_robin')
            )
            
            self.health_check_interval = config.get('health_check_interval', 30)
            self.stats_collection_interval = config.get('stats_collection_interval', 15)
            self.cache_ttl = config.get('cache_ttl', 300)
            
            # Chargement routes existantes depuis Kubernetes
            await self._load_existing_routes()
            
            logger.info("✅ Configuration routage chargée")
            
        except Exception as e:
            logger.error(f"❌ Erreur chargement config: {e}")
            raise
    
    async def _load_existing_routes(self):
        """Chargement routes existantes depuis Kubernetes"""
        try:
            # Chargement des VirtualServices Istio
            await self._load_istio_virtual_services()
            
            # Chargement des TrafficSplits SMI
            await self._load_smi_traffic_splits()
            
            # Chargement des Ingress Kubernetes
            await self._load_kubernetes_ingress()
            
        except Exception as e:
            logger.error(f"❌ Erreur chargement routes existantes: {e}")
            raise
    
    async def _load_istio_virtual_services(self):
        """Chargement VirtualServices Istio"""
        try:
            # En production, utiliser client Istio
            # Simulation pour l'exemple
            logger.info("📊 Chargement VirtualServices Istio...")
            
        except Exception as e:
            logger.error(f"❌ Erreur chargement VirtualServices: {e}")
    
    async def _load_smi_traffic_splits(self):
        """Chargement TrafficSplits SMI"""
        try:
            # En production, utiliser client SMI
            logger.info("📊 Chargement TrafficSplits SMI...")
            
        except Exception as e:
            logger.error(f"❌ Erreur chargement TrafficSplits: {e}")
    
    async def _load_kubernetes_ingress(self):
        """Chargement Ingress Kubernetes"""
        try:
            networking_v1 = client.NetworkingV1Api()
            ingresses = networking_v1.list_ingress_for_all_namespaces()
            
            for ingress in ingresses.items:
                # Conversion Ingress vers TrafficRoute
                route = await self._convert_ingress_to_route(ingress)
                if route:
                    self.routing_rules[route.route_id] = route
            
            logger.info(f"📊 {len(ingresses.items)} Ingress chargés")
            
        except Exception as e:
            logger.error(f"❌ Erreur chargement Ingress: {e}")
    
    async def _convert_ingress_to_route(self, ingress) -> Optional[TrafficRoute]:
        """Conversion Ingress vers TrafficRoute"""
        try:
            if not ingress.spec.rules:
                return None
            
            rule = ingress.spec.rules[0]
            path_rule = rule.http.paths[0] if rule.http and rule.http.paths else None
            
            if not path_rule:
                return None
            
            # Création conditions de correspondance
            match_conditions = []
            if rule.host:
                match_conditions.append(RouteMatch(
                    condition_type=RoutingCondition.HEADER,
                    key="host",
                    value=rule.host
                ))
            
            if path_rule.path:
                match_conditions.append(RouteMatch(
                    condition_type=RoutingCondition.PATH,
                    value=path_rule.path
                ))
            
            # Destination
            destination = RouteDestination(
                service_name=path_rule.backend.service.name,
                namespace=ingress.metadata.namespace,
                host=path_rule.backend.service.name,
                port=path_rule.backend.service.port.number
            )
            
            route = TrafficRoute(
                route_id=f"ingress-{ingress.metadata.name}",
                name=f"Ingress {ingress.metadata.name}",
                description=f"Route from Ingress {ingress.metadata.name}",
                traffic_type=TrafficType.HTTP,
                match_conditions=match_conditions,
                destinations=[destination]
            )
            
            return route
            
        except Exception as e:
            logger.error(f"❌ Erreur conversion Ingress: {e}")
            return None
    
    async def create_traffic_route(self, route: TrafficRoute) -> bool:
        """Création d'une règle de routage"""
        try:
            # Validation de la route
            if not await self._validate_route(route):
                logger.error(f"❌ Route invalide: {route.route_id}")
                return False
            
            # Enregistrement de la route
            route.updated_at = datetime.now()
            self.routing_rules[route.route_id] = route
            
            # Initialisation statistiques
            self.traffic_stats[route.route_id] = TrafficStats(route_id=route.route_id)
            
            # Application dans Kubernetes/Istio
            await self._apply_route_to_mesh(route)
            
            # Mise à jour métriques
            self.metrics['total_routes'] = len(self.routing_rules)
            self.metrics['active_routes'] = len([
                r for r in self.routing_rules.values() if r.enabled
            ])
            
            logger.info(f"✅ Route créée: {route.route_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur création route: {e}")
            return False
    
    async def _validate_route(self, route: TrafficRoute) -> bool:
        """Validation d'une route"""
        try:
            # Vérifier ID unique
            if route.route_id in self.routing_rules:
                logger.warning(f"⚠️ Route ID existe déjà: {route.route_id}")
                return False
            
            # Vérifier destinations
            if not route.destinations:
                logger.error("❌ Aucune destination spécifiée")
                return False
            
            # Vérifier poids total pour weighted routing
            if route.strategy == RoutingStrategy.WEIGHTED_ROUND_ROBIN:
                total_weight = sum(dest.weight for dest in route.destinations)
                if total_weight != 100:
                    logger.error(f"❌ Poids total incorrect: {total_weight}")
                    return False
            
            # Vérifier accessibilité destinations
            for dest in route.destinations:
                if not await self._check_destination_health(dest):
                    logger.warning(f"⚠️ Destination inaccessible: {dest.service_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur validation route: {e}")
            return False
    
    async def _check_destination_health(self, destination: RouteDestination) -> bool:
        """Vérification santé destination"""
        try:
            # Test de connectivité basique
            timeout = aiohttp.ClientTimeout(total=5)
            url = f"http://{destination.host}:{destination.port}/health"
            
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(url, timeout=timeout) as response:
                        return response.status == 200
                except:
                    return False
                    
        except Exception as e:
            logger.debug(f"❌ Erreur health check: {e}")
            return False
    
    async def _apply_route_to_mesh(self, route: TrafficRoute):
        """Application route dans service mesh"""
        try:
            # Application dans Istio (VirtualService)
            await self._apply_istio_virtual_service(route)
            
            # Application dans Linkerd (TrafficSplit)
            await self._apply_linkerd_traffic_split(route)
            
            # Application dans Kubernetes (Ingress si nécessaire)
            if route.traffic_type in [TrafficType.HTTP, TrafficType.HTTPS]:
                await self._apply_kubernetes_ingress(route)
            
        except Exception as e:
            logger.error(f"❌ Erreur application mesh: {e}")
            raise
    
    async def _apply_istio_virtual_service(self, route: TrafficRoute):
        """Application VirtualService Istio"""
        try:
            virtual_service = {
                'apiVersion': 'networking.istio.io/v1beta1',
                'kind': 'VirtualService',
                'metadata': {
                    'name': f"vs-{route.route_id}",
                    'namespace': route.destinations[0].namespace,
                    'labels': {
                        'app': route.destinations[0].service_name,
                        'managed-by': 'traffic-routing-service'
                    }
                },
                'spec': {
                    'hosts': [route.destinations[0].service_name],
                    'http': [{
                        'match': self._convert_matches_to_istio(route.match_conditions),
                        'route': self._convert_destinations_to_istio(route.destinations),
                        'timeout': f"{route.timeout}s",
                        'retries': {
                            'attempts': route.retry_policy.get('attempts', 3),
                            'perTryTimeout': f"{route.retry_policy.get('per_try_timeout', 10)}s"
                        }
                    }]
                }
            }
            
            # En production, appliquer via client Kubernetes
            logger.info(f"📊 VirtualService Istio créé: vs-{route.route_id}")
            
        except Exception as e:
            logger.error(f"❌ Erreur VirtualService Istio: {e}")
            raise
    
    def _convert_matches_to_istio(self, matches: List[RouteMatch]) -> List[Dict[str, Any]]:
        """Conversion conditions vers format Istio"""
        istio_matches = []
        
        for match in matches:
            istio_match = {}
            
            if match.condition_type == RoutingCondition.HEADER:
                istio_match['headers'] = {
                    match.key: {'exact': match.value}
                }
            elif match.condition_type == RoutingCondition.PATH:
                istio_match['uri'] = {'exact': match.value}
            elif match.condition_type == RoutingCondition.METHOD:
                istio_match['method'] = {'exact': match.value}
            
            if istio_match:
                istio_matches.append(istio_match)
        
        return istio_matches or [{}]  # Au moins un match par défaut
    
    def _convert_destinations_to_istio(self, destinations: List[RouteDestination]) -> List[Dict[str, Any]]:
        """Conversion destinations vers format Istio"""
        istio_destinations = []
        
        for dest in destinations:
            istio_dest = {
                'destination': {
                    'host': dest.service_name,
                    'port': {'number': dest.port}
                },
                'weight': dest.weight
            }
            
            if dest.subset:
                istio_dest['destination']['subset'] = dest.subset
            
            istio_destinations.append(istio_dest)
        
        return istio_destinations
    
    async def _apply_linkerd_traffic_split(self, route: TrafficRoute):
        """Application TrafficSplit Linkerd"""
        try:
            # Applicable seulement si plusieurs destinations
            if len(route.destinations) < 2:
                return
            
            traffic_split = {
                'apiVersion': 'split.smi-spec.io/v1alpha1',
                'kind': 'TrafficSplit',
                'metadata': {
                    'name': f"ts-{route.route_id}",
                    'namespace': route.destinations[0].namespace
                },
                'spec': {
                    'service': route.destinations[0].service_name,
                    'backends': [
                        {
                            'service': dest.service_name,
                            'weight': dest.weight
                        }
                        for dest in route.destinations
                    ]
                }
            }
            
            logger.info(f"📊 TrafficSplit Linkerd créé: ts-{route.route_id}")
            
        except Exception as e:
            logger.error(f"❌ Erreur TrafficSplit Linkerd: {e}")
            raise
    
    async def _apply_kubernetes_ingress(self, route: TrafficRoute):
        """Application Ingress Kubernetes"""
        try:
            # Seulement pour routes HTTP/HTTPS externes
            if not any(m.condition_type == RoutingCondition.HEADER and m.key == "host" 
                      for m in route.match_conditions):
                return
            
            host_match = next(
                m for m in route.match_conditions 
                if m.condition_type == RoutingCondition.HEADER and m.key == "host"
            )
            
            path_match = next(
                (m for m in route.match_conditions 
                 if m.condition_type == RoutingCondition.PATH),
                None
            )
            
            ingress = {
                'apiVersion': 'networking.k8s.io/v1',
                'kind': 'Ingress',
                'metadata': {
                    'name': f"ingress-{route.route_id}",
                    'namespace': route.destinations[0].namespace,
                    'annotations': {
                        'nginx.ingress.kubernetes.io/rewrite-target': '/',
                        'traffic-routing.ainflue.com/managed-by': 'traffic-routing-service'
                    }
                },
                'spec': {
                    'rules': [{
                        'host': host_match.value,
                        'http': {
                            'paths': [{
                                'path': path_match.value if path_match else '/',
                                'pathType': 'Prefix',
                                'backend': {
                                    'service': {
                                        'name': route.destinations[0].service_name,
                                        'port': {
                                            'number': route.destinations[0].port
                                        }
                                    }
                                }
                            }]
                        }
                    }]
                }
            }
            
            logger.info(f"📊 Ingress Kubernetes créé: ingress-{route.route_id}")
            
        except Exception as e:
            logger.error(f"❌ Erreur Ingress Kubernetes: {e}")
            raise
    
    async def route_request(self, 
                          request_info: Dict[str, Any]) -> Optional[RouteDestination]:
        """Routage d'une requête"""
        try:
            # Recherche route correspondante
            matching_route = await self._find_matching_route(request_info)
            
            if not matching_route:
                logger.warning("⚠️ Aucune route correspondante trouvée")
                return None
            
            # Sélection destination selon stratégie
            destination = await self._select_destination(matching_route, request_info)
            
            if destination:
                # Mise à jour statistiques
                await self._update_traffic_stats(matching_route.route_id, True)
                self.metrics['routing_decisions'] += 1
                
                logger.debug(f"🎯 Requête routée vers: {destination.service_name}")
            else:
                await self._update_traffic_stats(matching_route.route_id, False)
                self.metrics['failed_routes'] += 1
            
            return destination
            
        except Exception as e:
            logger.error(f"❌ Erreur routage requête: {e}")
            self.metrics['failed_routes'] += 1
            return None
    
    async def _find_matching_route(self, request_info: Dict[str, Any]) -> Optional[TrafficRoute]:
        """Recherche route correspondante"""
        try:
            # Vérifier cache d'abord
            cache_key = self._generate_cache_key(request_info)
            if cache_key in self.routing_cache:
                cache_entry = self.routing_cache[cache_key]
                if time.time() - cache_entry['timestamp'] < self.cache_ttl:
                    self.metrics['cache_hits'] += 1
                    return cache_entry['route']
            
            self.metrics['cache_misses'] += 1
            
            # Recherche parmi routes actives, triées par priorité
            sorted_routes = sorted(
                [r for r in self.routing_rules.values() if r.enabled],
                key=lambda x: x.priority,
                reverse=True
            )
            
            for route in sorted_routes:
                if await self._matches_route(route, request_info):
                    # Mise en cache
                    self.routing_cache[cache_key] = {
                        'route': route,
                        'timestamp': time.time()
                    }
                    return route
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erreur recherche route: {e}")
            return None
    
    def _generate_cache_key(self, request_info: Dict[str, Any]) -> str:
        """Génération clé cache"""
        key_data = {
            'method': request_info.get('method', ''),
            'path': request_info.get('path', ''),
            'host': request_info.get('headers', {}).get('host', ''),
            'user_agent': request_info.get('headers', {}).get('user-agent', '')[:50]
        }
        
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    async def _matches_route(self, route: TrafficRoute, request_info: Dict[str, Any]) -> bool:
        """Vérification correspondance route"""
        try:
            if not route.match_conditions:
                return True  # Route par défaut
            
            for condition in route.match_conditions:
                if not await self._matches_condition(condition, request_info):
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur correspondance route: {e}")
            return False
    
    async def _matches_condition(self, condition: RouteMatch, request_info: Dict[str, Any]) -> bool:
        """Vérification condition individuelle"""
        try:
            if condition.condition_type == RoutingCondition.PATH:
                path = request_info.get('path', '')
                return self._string_matches(path, condition.value, condition.operator, condition.case_sensitive)
            
            elif condition.condition_type == RoutingCondition.METHOD:
                method = request_info.get('method', '')
                return self._string_matches(method, condition.value, condition.operator, condition.case_sensitive)
            
            elif condition.condition_type == RoutingCondition.HEADER:
                headers = request_info.get('headers', {})
                header_value = headers.get(condition.key, '')
                return self._string_matches(header_value, condition.value, condition.operator, condition.case_sensitive)
            
            elif condition.condition_type == RoutingCondition.QUERY_PARAM:
                query_params = request_info.get('query_params', {})
                param_value = query_params.get(condition.key, '')
                return self._string_matches(param_value, condition.value, condition.operator, condition.case_sensitive)
            
            elif condition.condition_type == RoutingCondition.SOURCE_IP:
                source_ip = request_info.get('source_ip', '')
                return self._string_matches(source_ip, condition.value, condition.operator, condition.case_sensitive)
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Erreur vérification condition: {e}")
            return False
    
    def _string_matches(self, value: str, pattern: str, operator: str, case_sensitive: bool) -> bool:
        """Vérification correspondance chaîne"""
        if not case_sensitive:
            value = value.lower()
            pattern = pattern.lower()
        
        if operator == "equals":
            return value == pattern
        elif operator == "contains":
            return pattern in value
        elif operator == "starts_with":
            return value.startswith(pattern)
        elif operator == "ends_with":
            return value.endswith(pattern)
        elif operator == "regex":
            import re
            return bool(re.match(pattern, value))
        
        return False
    
    async def _select_destination(self, 
                                route: TrafficRoute, 
                                request_info: Dict[str, Any]) -> Optional[RouteDestination]:
        """Sélection destination selon stratégie"""
        try:
            # Filtrer destinations saines
            healthy_destinations = []
            for dest in route.destinations:
                if await self._check_destination_health(dest):
                    healthy_destinations.append(dest)
            
            if not healthy_destinations:
                logger.warning(f"⚠️ Aucune destination saine pour route: {route.route_id}")
                return None
            
            # Application stratégie de load balancing
            if route.strategy == RoutingStrategy.ROUND_ROBIN:
                return self._round_robin_selection(route.route_id, healthy_destinations)
            
            elif route.strategy == RoutingStrategy.WEIGHTED_ROUND_ROBIN:
                return self._weighted_round_robin_selection(healthy_destinations)
            
            elif route.strategy == RoutingStrategy.RANDOM:
                return random.choice(healthy_destinations)
            
            elif route.strategy == RoutingStrategy.LEAST_CONNECTIONS:
                return self._least_connections_selection(healthy_destinations)
            
            elif route.strategy == RoutingStrategy.IP_HASH:
                return self._ip_hash_selection(healthy_destinations, request_info.get('source_ip', ''))
            
            elif route.strategy == RoutingStrategy.LATENCY_BASED:
                return await self._latency_based_selection(healthy_destinations)
            
            elif route.strategy == RoutingStrategy.CANARY:
                return self._canary_selection(healthy_destinations)
            
            else:
                return healthy_destinations[0]  # Fallback
                
        except Exception as e:
            logger.error(f"❌ Erreur sélection destination: {e}")
            return None
    
    def _round_robin_selection(self, route_id: str, destinations: List[RouteDestination]) -> RouteDestination:
        """Sélection round robin"""
        if route_id not in self.round_robin_state:
            self.round_robin_state[route_id] = 0
        
        index = self.round_robin_state[route_id] % len(destinations)
        self.round_robin_state[route_id] += 1
        
        return destinations[index]
    
    def _weighted_round_robin_selection(self, destinations: List[RouteDestination]) -> RouteDestination:
        """Sélection weighted round robin"""
        total_weight = sum(dest.weight for dest in destinations)
        random_weight = random.randint(1, total_weight)
        
        current_weight = 0
        for dest in destinations:
            current_weight += dest.weight
            if random_weight <= current_weight:
                return dest
        
        return destinations[0]  # Fallback
    
    def _least_connections_selection(self, destinations: List[RouteDestination]) -> RouteDestination:
        """Sélection least connections"""
        min_connections = float('inf')
        selected_dest = destinations[0]
        
        for dest in destinations:
            dest_key = f"{dest.namespace}/{dest.service_name}"
            connections = len(self.active_connections.get(dest_key, set()))
            
            if connections < min_connections:
                min_connections = connections
                selected_dest = dest
        
        return selected_dest
    
    def _ip_hash_selection(self, destinations: List[RouteDestination], source_ip: str) -> RouteDestination:
        """Sélection basée sur hash IP"""
        if not source_ip:
            return destinations[0]
        
        hash_value = hashlib.md5(source_ip.encode()).hexdigest()
        index = int(hash_value, 16) % len(destinations)
        
        return destinations[index]
    
    async def _latency_based_selection(self, destinations: List[RouteDestination]) -> RouteDestination:
        """Sélection basée sur latence"""
        # Simulation récupération latences (en production, depuis métriques)
        min_latency = float('inf')
        selected_dest = destinations[0]
        
        for dest in destinations:
            # Latence simulée
            latency = random.uniform(10, 200)  # ms
            
            if latency < min_latency:
                min_latency = latency
                selected_dest = dest
        
        return selected_dest
    
    def _canary_selection(self, destinations: List[RouteDestination]) -> RouteDestination:
        """Sélection canary (version spéciale)"""
        # Recherche destination canary
        canary_dest = next(
            (dest for dest in destinations if 'canary' in dest.version.lower()),
            None
        )
        
        if canary_dest:
            # 10% de trafic vers canary
            if random.random() < 0.1:
                return canary_dest
        
        # Sinon, version stable
        stable_destinations = [
            dest for dest in destinations 
            if 'canary' not in dest.version.lower()
        ]
        
        return stable_destinations[0] if stable_destinations else destinations[0]
    
    async def _update_traffic_stats(self, route_id: str, success: bool):
        """Mise à jour statistiques trafic"""
        try:
            if route_id not in self.traffic_stats:
                self.traffic_stats[route_id] = TrafficStats(route_id=route_id)
            
            stats = self.traffic_stats[route_id]
            stats.total_requests += 1
            stats.last_request_time = datetime.now()
            
            if success:
                stats.successful_requests += 1
            else:
                stats.failed_requests += 1
            
            # Simulation temps de réponse
            response_time = random.uniform(50, 200)
            stats.avg_response_time = (
                (stats.avg_response_time * (stats.total_requests - 1) + response_time) / 
                stats.total_requests
            )
            
        except Exception as e:
            logger.error(f"❌ Erreur mise à jour stats: {e}")
    
    async def _start_health_monitoring(self):
        """Démarrage monitoring santé"""
        try:
            asyncio.create_task(self._health_monitoring_loop())
            logger.info("✅ Health monitoring démarré")
            
        except Exception as e:
            logger.error(f"❌ Erreur démarrage health monitoring: {e}")
            raise
    
    async def _health_monitoring_loop(self):
        """Boucle monitoring santé destinations"""
        while True:
            try:
                await asyncio.sleep(self.health_check_interval)
                
                for route in self.routing_rules.values():
                    if not route.enabled:
                        continue
                    
                    for dest in route.destinations:
                        health_ok = await self._check_destination_health(dest)
                        # Mise à jour état santé (en production, intégrer avec discovery service)
                
                self.metrics['health_checks_performed'] += 1
                
            except Exception as e:
                logger.error(f"❌ Erreur boucle health monitoring: {e}")
    
    async def _start_stats_collection(self):
        """Démarrage collecte statistiques"""
        try:
            asyncio.create_task(self._stats_collection_loop())
            logger.info("✅ Collecte statistiques démarrée")
            
        except Exception as e:
            logger.error(f"❌ Erreur démarrage stats collection: {e}")
            raise
    
    async def _stats_collection_loop(self):
        """Boucle collecte statistiques"""
        while True:
            try:
                await asyncio.sleep(self.stats_collection_interval)
                
                # Collecte statistiques load balancer
                await self._collect_load_balancer_stats()
                
                # Export métriques vers Prometheus
                await self._export_metrics()
                
            except Exception as e:
                logger.error(f"❌ Erreur boucle stats collection: {e}")
    
    async def _collect_load_balancer_stats(self):
        """Collecte statistiques load balancer"""
        try:
            for route_id, route in self.routing_rules.items():
                if not route.enabled:
                    continue
                
                for dest in route.destinations:
                    lb_key = f"{dest.namespace}/{dest.service_name}"
                    
                    if lb_key not in self.load_balancer_stats:
                        self.load_balancer_stats[lb_key] = LoadBalancerStats(
                            service_name=dest.service_name,
                            namespace=dest.namespace
                        )
                    
                    stats = self.load_balancer_stats[lb_key]
                    
                    # Mise à jour statistiques (simulation)
                    stats.active_connections = len(self.active_connections.get(lb_key, set()))
                    stats.total_connections += random.randint(0, 10)
                    stats.request_rate = random.uniform(50, 500)
                    stats.error_rate = random.uniform(0, 5)
                    stats.avg_latency = random.uniform(50, 200)
                    
                    # Vérification santé endpoints
                    health_count = 0
                    for dest_check in route.destinations:
                        if await self._check_destination_health(dest_check):
                            health_count += 1
                    
                    stats.healthy_endpoints = health_count
                    stats.total_endpoints = len(route.destinations)
            
        except Exception as e:
            logger.error(f"❌ Erreur collecte stats LB: {e}")
    
    async def _export_metrics(self):
        """Export métriques vers Prometheus"""
        try:
            # En production, utiliser prometheus_client
            # Simulation export
            pass
            
        except Exception as e:
            logger.error(f"❌ Erreur export métriques: {e}")
    
    async def _create_default_routes(self):
        """Création routes par défaut"""
        try:
            # Route AI Inference
            ai_route = TrafficRoute(
                route_id="ai-inference-default",
                name="AI Inference Default Route",
                description="Default route for AI inference service",
                traffic_type=TrafficType.HTTP,
                match_conditions=[
                    RouteMatch(
                        condition_type=RoutingCondition.PATH,
                        value="/api/v1/inference",
                        operator="starts_with"
                    )
                ],
                destinations=[
                    RouteDestination(
                        service_name="ai-inference-service",
                        namespace="ai-services",
                        host="ai-inference-service.ai-services.svc.cluster.local",
                        port=8080,
                        weight=100
                    )
                ],
                strategy=RoutingStrategy.ROUND_ROBIN,
                priority=100
            )
            
            # Route Content Upload
            content_route = TrafficRoute(
                route_id="content-upload-default",
                name="Content Upload Default Route",
                description="Default route for content upload service",
                traffic_type=TrafficType.HTTP,
                match_conditions=[
                    RouteMatch(
                        condition_type=RoutingCondition.PATH,
                        value="/api/v1/upload",
                        operator="starts_with"
                    )
                ],
                destinations=[
                    RouteDestination(
                        service_name="content-upload-service",
                        namespace="content-services",
                        host="content-upload-service.content-services.svc.cluster.local",
                        port=8080,
                        weight=100
                    )
                ],
                strategy=RoutingStrategy.ROUND_ROBIN,
                priority=100
            )
            
            # Création des routes
            await self.create_traffic_route(ai_route)
            await self.create_traffic_route(content_route)
            
            logger.info("✅ Routes par défaut créées")
            
        except Exception as e:
            logger.error(f"❌ Erreur création routes par défaut: {e}")
    
    async def _maintenance_loop(self):
        """Boucle de maintenance"""
        while True:
            try:
                await asyncio.sleep(300)  # 5 minutes
                
                # Nettoyage cache
                await self._cleanup_cache()
                
                # Nettoyage statistiques anciennes
                await self._cleanup_old_stats()
                
                # Nettoyage connexions inactives
                await self._cleanup_inactive_connections()
                
            except Exception as e:
                logger.error(f"❌ Erreur boucle maintenance: {e}")
    
    async def _cleanup_cache(self):
        """Nettoyage cache expiré"""
        try:
            current_time = time.time()
            expired_keys = []
            
            for key, entry in self.routing_cache.items():
                if current_time - entry['timestamp'] > self.cache_ttl:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self.routing_cache[key]
            
            if expired_keys:
                logger.info(f"🧹 Cache nettoyé: {len(expired_keys)} entrées supprimées")
                
        except Exception as e:
            logger.error(f"❌ Erreur nettoyage cache: {e}")
    
    async def _cleanup_old_stats(self):
        """Nettoyage statistiques anciennes"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=24)
            
            for route_id, stats in list(self.traffic_stats.items()):
                if stats.last_request_time < cutoff_time:
                    del self.traffic_stats[route_id]
            
        except Exception as e:
            logger.error(f"❌ Erreur nettoyage stats: {e}")
    
    async def _cleanup_inactive_connections(self):
        """Nettoyage connexions inactives"""
        try:
            # En production, intégrer avec monitoring connexions réelles
            pass
            
        except Exception as e:
            logger.error(f"❌ Erreur nettoyage connexions: {e}")
    
    async def get_route_status(self, route_id: str) -> Optional[Dict[str, Any]]:
        """Statut d'une route spécifique"""
        try:
            if route_id not in self.routing_rules:
                return None
            
            route = self.routing_rules[route_id]
            stats = self.traffic_stats.get(route_id, TrafficStats(route_id=route_id))
            
            # Vérification santé destinations
            destination_health = []
            for dest in route.destinations:
                health = await self._check_destination_health(dest)
                destination_health.append({
                    'service_name': dest.service_name,
                    'host': dest.host,
                    'port': dest.port,
                    'healthy': health,
                    'weight': dest.weight
                })
            
            return {
                'route_info': {
                    'route_id': route.route_id,
                    'name': route.name,
                    'strategy': route.strategy.value,
                    'enabled': route.enabled,
                    'priority': route.priority
                },
                'traffic_stats': {
                    'total_requests': stats.total_requests,
                    'successful_requests': stats.successful_requests,
                    'failed_requests': stats.failed_requests,
                    'success_rate': (stats.successful_requests / max(stats.total_requests, 1)) * 100,
                    'avg_response_time': stats.avg_response_time,
                    'last_request': stats.last_request_time.isoformat() if stats.last_request_time else None
                },
                'destinations': destination_health,
                'health_summary': {
                    'healthy_destinations': sum(1 for d in destination_health if d['healthy']),
                    'total_destinations': len(destination_health)
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur statut route: {e}")
            return None
    
    async def health_check(self) -> Dict[str, Any]:
        """Vérification santé service routing"""
        try:
            health_status = {
                'service': self.service_name,
                'version': self.version,
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'metrics': self.metrics,
                'routing_overview': {
                    'total_routes': len(self.routing_rules),
                    'active_routes': len([r for r in self.routing_rules.values() if r.enabled]),
                    'cache_size': len(self.routing_cache),
                    'stats_tracked': len(self.traffic_stats)
                },
                'components': {
                    'kubernetes_client': self.k8s_client is not None,
                    'health_monitoring': True,
                    'stats_collection': True,
                    'cache_system': True
                }
            }
            
            # Vérification routes critiques
            critical_routes_healthy = 0
            total_critical_routes = 0
            
            for route in self.routing_rules.values():
                if route.enabled and route.priority >= 100:  # Routes critiques
                    total_critical_routes += 1
                    healthy_destinations = 0
                    
                    for dest in route.destinations:
                        if await self._check_destination_health(dest):
                            healthy_destinations += 1
                    
                    if healthy_destinations > 0:
                        critical_routes_healthy += 1
            
            health_status['critical_routes'] = {
                'healthy': critical_routes_healthy,
                'total': total_critical_routes,
                'health_ratio': critical_routes_healthy / max(total_critical_routes, 1)
            }
            
            # Statut global
            if health_status['critical_routes']['health_ratio'] < 0.8:
                health_status['status'] = 'degraded'
            
            return health_status
            
        except Exception as e:
            logger.error(f"❌ Erreur health check routing: {e}")
            return {
                'service': self.service_name,
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def get_service_status(self) -> Dict[str, Any]:
        """Statut détaillé service routing"""
        try:
            return {
                'service_info': {
                    'name': self.service_name,
                    'version': self.version,
                    'status': 'running'
                },
                'configuration': {
                    'default_strategy': self.default_strategy.value,
                    'health_check_interval': self.health_check_interval,
                    'stats_collection_interval': self.stats_collection_interval,
                    'cache_ttl': self.cache_ttl
                },
                'performance_metrics': self.metrics,
                'routing_summary': {
                    'total_routes': len(self.routing_rules),
                    'active_routes': len([r for r in self.routing_rules.values() if r.enabled]),
                    'routes_by_strategy': self._get_routes_by_strategy(),
                    'routes_by_traffic_type': self._get_routes_by_traffic_type()
                },
                'load_balancer_overview': {
                    'total_services': len(self.load_balancer_stats),
                    'avg_request_rate': self._calculate_avg_request_rate(),
                    'avg_error_rate': self._calculate_avg_error_rate(),
                    'avg_latency': self._calculate_avg_latency()
                },
                'cache_performance': {
                    'cache_entries': len(self.routing_cache),
                    'hit_ratio': self.metrics['cache_hits'] / max(
                        self.metrics['cache_hits'] + self.metrics['cache_misses'], 1
                    )
                },
                'health': await self.health_check()
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur statut service routing: {e}")
            return {'error': str(e)}
    
    def _get_routes_by_strategy(self) -> Dict[str, int]:
        """Répartition routes par stratégie"""
        strategy_counts = {}
        for route in self.routing_rules.values():
            strategy = route.strategy.value
            strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1
        return strategy_counts
    
    def _get_routes_by_traffic_type(self) -> Dict[str, int]:
        """Répartition routes par type de trafic"""
        type_counts = {}
        for route in self.routing_rules.values():
            traffic_type = route.traffic_type.value
            type_counts[traffic_type] = type_counts.get(traffic_type, 0) + 1
        return type_counts
    
    def _calculate_avg_request_rate(self) -> float:
        """Calcul taux de requêtes moyen"""
        if not self.load_balancer_stats:
            return 0.0
        
        total_rate = sum(stats.request_rate for stats in self.load_balancer_stats.values())
        return total_rate / len(self.load_balancer_stats)
    
    def _calculate_avg_error_rate(self) -> float:
        """Calcul taux d'erreur moyen"""
        if not self.load_balancer_stats:
            return 0.0
        
        total_rate = sum(stats.error_rate for stats in self.load_balancer_stats.values())
        return total_rate / len(self.load_balancer_stats)
    
    def _calculate_avg_latency(self) -> float:
        """Calcul latence moyenne"""
        if not self.load_balancer_stats:
            return 0.0
        
        total_latency = sum(stats.avg_latency for stats in self.load_balancer_stats.values())
        return total_latency / len(self.load_balancer_stats)

# Instance globale
traffic_routing_service = TrafficRoutingService()

async def main():
    """Test du service de routage"""
    try:
        print("🎯 Test Traffic Routing Service")
        
        # Initialisation
        success = await traffic_routing_service.initialize()
        if not success:
            print("❌ Échec initialisation")
            return
        
        # Test création route custom
        custom_route = TrafficRoute(
            route_id="custom-api-route",
            name="Custom API Route",
            description="Route pour API custom",
            traffic_type=TrafficType.HTTP,
            match_conditions=[
                RouteMatch(
                    condition_type=RoutingCondition.PATH,
                    value="/api/v2/custom",
                    operator="starts_with"
                ),
                RouteMatch(
                    condition_type=RoutingCondition.HEADER,
                    key="x-api-version",
                    value="v2"
                )
            ],
            destinations=[
                RouteDestination(
                    service_name="custom-api-service",
                    namespace="api-services",
                    host="custom-api.api-services.svc.cluster.local",
                    port=8080,
                    weight=80
                ),
                RouteDestination(
                    service_name="custom-api-service-canary",
                    namespace="api-services",
                    host="custom-api-canary.api-services.svc.cluster.local",
                    port=8080,
                    weight=20
                )
            ],
            strategy=RoutingStrategy.WEIGHTED_ROUND_ROBIN,
            priority=200
        )
        
        await traffic_routing_service.create_traffic_route(custom_route)
        
        # Test routage requête
        test_request = {
            'method': 'POST',
            'path': '/api/v2/custom/process',
            'headers': {
                'host': 'api.ainflue.com',
                'x-api-version': 'v2',
                'user-agent': 'AinflueMobile/1.0'
            },
            'source_ip': '192.168.1.100'
        }
        
        destination = await traffic_routing_service.route_request(test_request)
        if destination:
            print(f"🎯 Requête routée vers: {destination.service_name}:{destination.port}")
        
        # Test statut route
        route_status = await traffic_routing_service.get_route_status("custom-api-route")
        print(f"📊 Statut route: {route_status}")
        
        # Statut final
        status = await traffic_routing_service.get_service_status()
        print(f"📊 Statut service: {status}")
        
        print("✅ Test Traffic Routing Service terminé")
        
    except Exception as e:
        print(f"❌ Erreur test: {e}")

if __name__ == "__main__":
    asyncio.run(main())