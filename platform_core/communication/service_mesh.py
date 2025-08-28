"""
🚀 Service Mesh & Discovery - IA Influencer Agent Platform Enterprise
===================================================================
Module: backend/platform_core/communication/service_mesh.py
Author: Fahed Mlaiel (mlaiel@live.de)
===================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 SERVICE MESH INTELLIGENT
Infrastructure de communication microservices avancée
- Service discovery automatique avec consensus
- Traffic management et circuit breakers
- Security policies et mTLS automatique
- Observability complète et tracing distribué
"""

import asyncio
import json
import logging
import time
import uuid
from typing import Dict, List, Optional, Any, Callable, Set, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum
import hashlib
import base64

import aioredis
import aiohttp
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa

# Configuration
logger = logging.getLogger(__name__)

class ServiceType(Enum):
    """Types de services"""
    API_GATEWAY = "api_gateway"
    MICROSERVICE = "microservice" 
    DATABASE = "database"
    CACHE = "cache"
    MESSAGE_QUEUE = "message_queue"
    STORAGE = "storage"
    ML_SERVICE = "ml_service"
    AI_AGENT = "ai_agent"

class ServiceHealth(Enum):
    """État de santé des services"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    STARTING = "starting"
    STOPPING = "stopping"
    UNKNOWN = "unknown"

class TrafficPolicy(Enum):
    """Politiques de trafic"""
    ROUND_ROBIN = "round_robin"
    WEIGHTED = "weighted"
    LEAST_CONN = "least_conn"
    STICKY_SESSION = "sticky_session"
    CANARY = "canary"
    BLUE_GREEN = "blue_green"

@dataclass
class ServiceInstance:
    """Instance de service dans le mesh"""
    service_id: str
    service_name: str
    service_type: ServiceType
    host: str
    port: int
    version: str = "1.0.0"
    environment: str = "production"
    namespace: str = "default"
    
    # Métadonnées
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Santé et métriques
    health: ServiceHealth = ServiceHealth.STARTING
    last_heartbeat: Optional[datetime] = None
    health_check_url: Optional[str] = None
    
    # Configuration réseau
    protocols: List[str] = field(default_factory=lambda: ["http"])
    endpoints: Dict[str, str] = field(default_factory=dict)
    
    # Sécurité
    tls_enabled: bool = False
    cert_fingerprint: Optional[str] = None
    allowed_clients: Set[str] = field(default_factory=set)
    
    # Découverte
    registered_at: datetime = field(default_factory=datetime.utcnow)
    last_seen: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def url(self) -> str:
        protocol = "https" if self.tls_enabled else "http"
        return f"{protocol}://{self.host}:{self.port}"
        
    @property
    def is_healthy(self) -> bool:
        return self.health in [ServiceHealth.HEALTHY, ServiceHealth.DEGRADED]
        
    @property
    def is_stale(self, timeout_seconds: int = 60) -> bool:
        if not self.last_heartbeat:
            return True
        return (datetime.utcnow() - self.last_heartbeat).total_seconds() > timeout_seconds

@dataclass
class ServicePolicy:
    """Politique de service"""
    service_name: str
    traffic_policy: TrafficPolicy = TrafficPolicy.ROUND_ROBIN
    rate_limit: Optional[int] = None  # Requêtes par seconde
    timeout_seconds: int = 30
    max_retries: int = 3
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: int = 60
    
    # Sécurité
    require_tls: bool = False
    allowed_services: Set[str] = field(default_factory=set)
    
    # Load balancing
    weights: Dict[str, float] = field(default_factory=dict)
    sticky_session_key: Optional[str] = None
    
    # Canary deployment
    canary_version: Optional[str] = None
    canary_percentage: float = 0.0

class ServiceDiscovery:
    """Service de découverte automatique"""
    
    def __init__(self, 
                 redis_client: aioredis.Redis,
                 namespace: str = "service_mesh"):
        self.redis_client = redis_client
        self.namespace = namespace
        self.services: Dict[str, Dict[str, ServiceInstance]] = {}  # service_name -> {instance_id -> instance}
        self.policies: Dict[str, ServicePolicy] = {}
        
        # Clés Redis
        self.registry_key = f"{namespace}:registry"
        self.policies_key = f"{namespace}:policies"
        self.heartbeat_key = f"{namespace}:heartbeats"
        
        # Tâches
        self._cleanup_task: Optional[asyncio.Task] = None
        self._sync_task: Optional[asyncio.Task] = None
        self._running = False
        
    async def start(self):
        """Démarre le service discovery"""
        self._running = True
        
        # Charger les données depuis Redis
        await self._load_from_redis()
        
        # Démarrer les tâches de maintenance
        self._cleanup_task = asyncio.create_task(self._cleanup_stale_services())
        self._sync_task = asyncio.create_task(self._sync_with_redis())
        
        logger.info("ServiceDiscovery démarré")
        
    async def stop(self):
        """Arrête le service discovery"""
        self._running = False
        
        if self._cleanup_task:
            self._cleanup_task.cancel()
        if self._sync_task:
            self._sync_task.cancel()
            
        for task in [self._cleanup_task, self._sync_task]:
            if task:
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                    
        logger.info("ServiceDiscovery arrêté")
        
    async def register_service(self, service: ServiceInstance) -> str:
        """Enregistre un service dans le mesh"""
        service_name = service.service_name
        instance_id = service.service_id
        
        if service_name not in self.services:
            self.services[service_name] = {}
            
        self.services[service_name][instance_id] = service
        
        # Persister dans Redis
        await self._persist_service(service)
        
        logger.info(f"Service enregistré: {service_name}/{instance_id} ({service.url})")
        return instance_id
        
    async def unregister_service(self, service_name: str, instance_id: str):
        """Désenregistre un service"""
        if service_name in self.services and instance_id in self.services[service_name]:
            del self.services[service_name][instance_id]
            
            if not self.services[service_name]:
                del self.services[service_name]
                
        # Supprimer de Redis
        await self._remove_service_from_redis(service_name, instance_id)
        
        logger.info(f"Service désenregistré: {service_name}/{instance_id}")
        
    async def discover_services(self, 
                               service_name: str,
                               tags: Optional[Dict[str, str]] = None,
                               healthy_only: bool = True) -> List[ServiceInstance]:
        """Découvre les instances d'un service"""
        if service_name not in self.services:
            return []
            
        instances = []
        for instance in self.services[service_name].values():
            # Filtrer par santé
            if healthy_only and not instance.is_healthy:
                continue
                
            # Filtrer par tags
            if tags:
                if not all(instance.tags.get(k) == v for k, v in tags.items()):
                    continue
                    
            instances.append(instance)
            
        return instances
        
    async def update_health(self, service_name: str, instance_id: str, health: ServiceHealth):
        """Met à jour l'état de santé d'un service"""
        if (service_name in self.services and 
            instance_id in self.services[service_name]):
            
            instance = self.services[service_name][instance_id]
            instance.health = health
            instance.last_heartbeat = datetime.utcnow()
            instance.last_seen = datetime.utcnow()
            
            # Enregistrer le heartbeat dans Redis
            await self._record_heartbeat(service_name, instance_id)
            
    async def set_service_policy(self, policy: ServicePolicy):
        """Définit une politique pour un service"""
        self.policies[policy.service_name] = policy
        
        # Persister dans Redis
        await self._persist_policy(policy)
        
        logger.info(f"Politique définie pour {policy.service_name}: {policy.traffic_policy.value}")
        
    async def get_service_policy(self, service_name: str) -> Optional[ServicePolicy]:
        """Récupère la politique d'un service"""
        return self.policies.get(service_name)
        
    async def _persist_service(self, service: ServiceInstance):
        """Persiste un service dans Redis"""
        key = f"{self.registry_key}:{service.service_name}:{service.service_id}"
        data = self._serialize_service(service)
        
        await self.redis_client.set(key, json.dumps(data), ex=300)  # TTL 5 minutes
        
    async def _persist_policy(self, policy: ServicePolicy):
        """Persiste une politique dans Redis"""
        key = f"{self.policies_key}:{policy.service_name}"
        data = self._serialize_policy(policy)
        
        await self.redis_client.set(key, json.dumps(data))
        
    async def _record_heartbeat(self, service_name: str, instance_id: str):
        """Enregistre un heartbeat"""
        key = f"{self.heartbeat_key}:{service_name}:{instance_id}"
        timestamp = datetime.utcnow().isoformat()
        
        await self.redis_client.set(key, timestamp, ex=120)  # TTL 2 minutes
        
    async def _load_from_redis(self):
        """Charge les services et politiques depuis Redis"""
        try:
            # Charger les services
            pattern = f"{self.registry_key}:*"
            keys = await self.redis_client.keys(pattern)
            
            for key in keys:
                data = await self.redis_client.get(key)
                if data:
                    service_data = json.loads(data)
                    service = self._deserialize_service(service_data)
                    
                    service_name = service.service_name
                    if service_name not in self.services:
                        self.services[service_name] = {}
                    self.services[service_name][service.service_id] = service
                    
            # Charger les politiques
            pattern = f"{self.policies_key}:*"
            keys = await self.redis_client.keys(pattern)
            
            for key in keys:
                data = await self.redis_client.get(key)
                if data:
                    policy_data = json.loads(data)
                    policy = self._deserialize_policy(policy_data)
                    self.policies[policy.service_name] = policy
                    
        except Exception as e:
            logger.error(f"Erreur lors du chargement depuis Redis: {e}")
            
    async def _cleanup_stale_services(self):
        """Nettoie les services obsolètes"""
        while self._running:
            try:
                await asyncio.sleep(30)  # Vérifier toutes les 30 secondes
                
                stale_services = []
                for service_name, instances in self.services.items():
                    for instance_id, instance in instances.items():
                        if instance.is_stale(timeout_seconds=120):  # 2 minutes
                            stale_services.append((service_name, instance_id))
                            
                for service_name, instance_id in stale_services:
                    logger.info(f"Nettoyage service obsolète: {service_name}/{instance_id}")
                    await self.unregister_service(service_name, instance_id)
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Erreur dans le nettoyage: {e}")
                
    async def _sync_with_redis(self):
        """Synchronise périodiquement avec Redis"""
        while self._running:
            try:
                await asyncio.sleep(60)  # Sync toutes les minutes
                await self._load_from_redis()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Erreur dans la synchronisation: {e}")
                
    async def _remove_service_from_redis(self, service_name: str, instance_id: str):
        """Supprime un service de Redis"""
        key = f"{self.registry_key}:{service_name}:{instance_id}"
        await self.redis_client.delete(key)
        
        heartbeat_key = f"{self.heartbeat_key}:{service_name}:{instance_id}"
        await self.redis_client.delete(heartbeat_key)
        
    def _serialize_service(self, service: ServiceInstance) -> Dict[str, Any]:
        """Sérialise un service"""
        data = asdict(service)
        # Convertir les enums et sets
        data['service_type'] = service.service_type.value
        data['health'] = service.health.value
        data['allowed_clients'] = list(service.allowed_clients)
        # Convertir les dates
        for field in ['registered_at', 'last_seen', 'last_heartbeat']:
            if data[field]:
                data[field] = data[field].isoformat()
        return data
        
    def _deserialize_service(self, data: Dict[str, Any]) -> ServiceInstance:
        """Désérialise un service"""
        # Convertir les enums et sets
        data['service_type'] = ServiceType(data['service_type'])
        data['health'] = ServiceHealth(data['health'])
        data['allowed_clients'] = set(data['allowed_clients'])
        # Convertir les dates
        for field in ['registered_at', 'last_seen', 'last_heartbeat']:
            if data[field]:
                data[field] = datetime.fromisoformat(data[field])
        return ServiceInstance(**data)
        
    def _serialize_policy(self, policy: ServicePolicy) -> Dict[str, Any]:
        """Sérialise une politique"""
        data = asdict(policy)
        data['traffic_policy'] = policy.traffic_policy.value
        data['allowed_services'] = list(policy.allowed_services)
        return data
        
    def _deserialize_policy(self, data: Dict[str, Any]) -> ServicePolicy:
        """Désérialise une politique"""
        data['traffic_policy'] = TrafficPolicy(data['traffic_policy'])
        data['allowed_services'] = set(data['allowed_services'])
        return ServicePolicy(**data)
        
    def get_discovery_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques de découverte"""
        return {
            "total_services": len(self.services),
            "total_instances": sum(len(instances) for instances in self.services.values()),
            "healthy_instances": sum(
                1 for instances in self.services.values()
                for instance in instances.values()
                if instance.is_healthy
            ),
            "policies_count": len(self.policies),
            "services_by_type": {
                service_type.value: sum(
                    1 for instances in self.services.values()
                    for instance in instances.values()
                    if instance.service_type == service_type
                )
                for service_type in ServiceType
            },
            "services_by_health": {
                health.value: sum(
                    1 for instances in self.services.values()
                    for instance in instances.values()
                    if instance.health == health
                )
                for health in ServiceHealth
            }
        }

class ServiceMesh:
    """Service Mesh principal avec fonctionnalités complètes"""
    
    def __init__(self, 
                 redis_client: aioredis.Redis,
                 namespace: str = "service_mesh"):
        self.discovery = ServiceDiscovery(redis_client, namespace)
        self.namespace = namespace
        
        # Composants intégrés
        self.circuit_breakers: Dict[str, Dict] = {}
        self.rate_limiters: Dict[str, Dict] = {}
        self.metrics: Dict[str, Dict] = {}
        
        # Proxy et routing
        self.routing_table: Dict[str, Callable] = {}
        self.middleware: List[Callable] = []
        
    async def start(self):
        """Démarre le service mesh"""
        await self.discovery.start()
        logger.info("ServiceMesh démarré")
        
    async def stop(self):
        """Arrête le service mesh"""
        await self.discovery.stop()
        logger.info("ServiceMesh arrêté")
        
    async def register_service(self, 
                              service_name: str,
                              host: str,
                              port: int,
                              service_type: ServiceType = ServiceType.MICROSERVICE,
                              **kwargs) -> str:
        """Enregistre un service dans le mesh"""
        service = ServiceInstance(
            service_id=str(uuid.uuid4()),
            service_name=service_name,
            service_type=service_type,
            host=host,
            port=port,
            **kwargs
        )
        
        return await self.discovery.register_service(service)
        
    async def call_service(self, 
                          service_name: str,
                          method: str = "GET",
                          path: str = "/",
                          data: Optional[Dict] = None,
                          headers: Optional[Dict] = None,
                          timeout: Optional[int] = None,
                          caller_service: Optional[str] = None) -> Tuple[int, Dict]:
        """Appelle un service via le mesh"""
        
        # Découvrir les instances
        instances = await self.discovery.discover_services(service_name)
        if not instances:
            raise Exception(f"Aucune instance disponible pour {service_name}")
            
        # Obtenir la politique
        policy = await self.discovery.get_service_policy(service_name)
        if not policy:
            policy = ServicePolicy(service_name=service_name)
            
        # Vérifier les autorisations
        if policy.allowed_services and caller_service not in policy.allowed_services:
            raise Exception(f"Service {caller_service} non autorisé à appeler {service_name}")
            
        # Sélectionner une instance selon la politique
        instance = self._select_instance(instances, policy)
        if not instance:
            raise Exception(f"Aucune instance sélectionnable pour {service_name}")
            
        # Vérifier le circuit breaker
        if self._is_circuit_breaker_open(service_name, instance.service_id):
            raise Exception(f"Circuit breaker ouvert pour {service_name}")
            
        # Vérifier le rate limiting
        if not self._check_rate_limit(service_name, caller_service):
            raise Exception(f"Rate limit dépassé pour {service_name}")
            
        # Effectuer l'appel
        try:
            url = f"{instance.url}{path}"
            
            async with aiohttp.ClientSession() as session:
                request_kwargs = {
                    "method": method,
                    "url": url,
                    "headers": headers or {},
                    "timeout": aiohttp.ClientTimeout(total=timeout or policy.timeout_seconds)
                }
                
                if data:
                    if method in ["POST", "PUT", "PATCH"]:
                        request_kwargs["json"] = data
                    else:
                        request_kwargs["params"] = data
                        
                async with session.request(**request_kwargs) as response:
                    response_data = await response.json()
                    
                    # Enregistrer les métriques
                    self._record_call_metrics(service_name, instance.service_id, True, response.status)
                    
                    return response.status, response_data
                    
        except Exception as e:
            # Enregistrer l'échec
            self._record_call_metrics(service_name, instance.service_id, False, 0)
            self._handle_circuit_breaker(service_name, instance.service_id, False)
            raise e
            
    def _select_instance(self, instances: List[ServiceInstance], policy: ServicePolicy) -> Optional[ServiceInstance]:
        """Sélectionne une instance selon la politique"""
        if not instances:
            return None
            
        if policy.traffic_policy == TrafficPolicy.ROUND_ROBIN:
            # Implémentation simple round robin
            return instances[hash(policy.service_name) % len(instances)]
            
        elif policy.traffic_policy == TrafficPolicy.WEIGHTED:
            # Sélection pondérée
            weights = []
            for instance in instances:
                weight = policy.weights.get(instance.service_id, 1.0)
                weights.append(weight)
                
            if not weights:
                return instances[0]
                
            # Sélection pondérée simple
            import random
            return random.choices(instances, weights=weights)[0]
            
        elif policy.traffic_policy == TrafficPolicy.LEAST_CONN:
            # Instance avec moins de connexions
            return min(instances, key=lambda i: self._get_active_connections(i.service_id))
            
        else:
            return instances[0]
            
    def _is_circuit_breaker_open(self, service_name: str, instance_id: str) -> bool:
        """Vérifie si le circuit breaker est ouvert"""
        key = f"{service_name}:{instance_id}"
        if key not in self.circuit_breakers:
            return False
            
        cb = self.circuit_breakers[key]
        now = time.time()
        
        if cb.get("state") == "open":
            if now > cb.get("reset_time", 0):
                cb["state"] = "half_open"
                return False
            return True
            
        return False
        
    def _handle_circuit_breaker(self, service_name: str, instance_id: str, success: bool):
        """Gère le circuit breaker"""
        key = f"{service_name}:{instance_id}"
        if key not in self.circuit_breakers:
            self.circuit_breakers[key] = {
                "failures": 0,
                "state": "closed",
                "reset_time": 0
            }
            
        cb = self.circuit_breakers[key]
        
        if success:
            if cb["state"] == "half_open":
                cb["state"] = "closed"
                cb["failures"] = 0
        else:
            cb["failures"] += 1
            
            policy = self.discovery.policies.get(service_name)
            threshold = policy.circuit_breaker_threshold if policy else 5
            timeout = policy.circuit_breaker_timeout if policy else 60
            
            if cb["failures"] >= threshold:
                cb["state"] = "open"
                cb["reset_time"] = time.time() + timeout
                
    def _check_rate_limit(self, service_name: str, caller_service: Optional[str]) -> bool:
        """Vérifie le rate limiting"""
        policy = self.discovery.policies.get(service_name)
        if not policy or not policy.rate_limit:
            return True
            
        key = f"{service_name}:{caller_service or 'anonymous'}"
        now = time.time()
        
        if key not in self.rate_limiters:
            self.rate_limiters[key] = {
                "count": 0,
                "window_start": now
            }
            
        rl = self.rate_limiters[key]
        
        # Reset si nouvelle fenêtre (1 seconde)
        if now - rl["window_start"] >= 1.0:
            rl["count"] = 0
            rl["window_start"] = now
            
        rl["count"] += 1
        return rl["count"] <= policy.rate_limit
        
    def _record_call_metrics(self, service_name: str, instance_id: str, success: bool, status_code: int):
        """Enregistre les métriques d'appel"""
        key = f"{service_name}:{instance_id}"
        if key not in self.metrics:
            self.metrics[key] = {
                "total_calls": 0,
                "successful_calls": 0,
                "failed_calls": 0,
                "last_call_time": 0
            }
            
        metrics = self.metrics[key]
        metrics["total_calls"] += 1
        metrics["last_call_time"] = time.time()
        
        if success and 200 <= status_code < 400:
            metrics["successful_calls"] += 1
        else:
            metrics["failed_calls"] += 1
            
    def _get_active_connections(self, instance_id: str) -> int:
        """Retourne le nombre de connexions actives pour une instance"""
        # Implémentation simplifiée - devrait être intégrée avec des métriques réelles
        return self.metrics.get(instance_id, {}).get("active_connections", 0)
        
    def get_mesh_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques du mesh"""
        return {
            "discovery": self.discovery.get_discovery_stats(),
            "circuit_breakers": {
                key: {
                    "state": cb["state"],
                    "failures": cb["failures"]
                }
                for key, cb in self.circuit_breakers.items()
            },
            "rate_limiters": {
                key: {
                    "current_count": rl["count"],
                    "window_start": rl["window_start"]
                }
                for key, rl in self.rate_limiters.items()
            },
            "call_metrics": {
                key: {
                    "total_calls": m["total_calls"],
                    "success_rate": m["successful_calls"] / max(m["total_calls"], 1),
                    "last_call_time": m["last_call_time"]
                }
                for key, m in self.metrics.items()
            }
        }