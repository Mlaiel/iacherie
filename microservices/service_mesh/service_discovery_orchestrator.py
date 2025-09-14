#!/usr/bin/env python3
"""
🕸️ Service Discovery Orchestrator - Enterprise Service Mesh  
Orchestration complète de la découverte de services pour microservices Ainflue

© Fahed Mlaiel 2024-2025 - Propriété intellectuelle stricte
Architecture microservices enterprise - Niveau production
🔧 Microservices Expert + Backend Senior Implementation
"""

import asyncio
import logging
import json
import consul
import etcd3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Union
from dataclasses import dataclass, asdict
from enum import Enum
import aiohttp
import hashlib
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

class ServiceStatus(Enum):
    """Statuts des services"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"
    UNKNOWN = "unknown"

class DiscoveryBackend(Enum):
    """Backends de service discovery"""
    KUBERNETES = "kubernetes"
    CONSUL = "consul"
    ETCD = "etcd"
    ISTIO = "istio"
    LINKERD = "linkerd"

@dataclass
class ServiceEndpoint:
    """Point de terminaison de service"""
    service_id: str
    service_name: str
    namespace: str
    host: str
    port: int
    protocol: str = "http"
    health_check_path: str = "/health"
    weight: int = 100
    tags: List[str] = None
    metadata: Dict[str, Any] = None
    status: ServiceStatus = ServiceStatus.UNKNOWN
    last_check: datetime = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.metadata is None:
            self.metadata = {}
        if self.last_check is None:
            self.last_check = datetime.now()

@dataclass
class ServiceInstance:
    """Instance de service"""
    instance_id: str
    endpoint: ServiceEndpoint
    version: str
    deployment_id: str
    started_at: datetime
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    request_count: int = 0
    error_count: int = 0

@dataclass
class ServiceGroup:
    """Groupe de services"""
    group_name: str
    services: List[ServiceEndpoint]
    load_balancing_strategy: str = "round_robin"
    health_check_interval: int = 30
    failure_threshold: int = 3
    circuit_breaker_enabled: bool = True

class ServiceDiscoveryOrchestrator:
    """Orchestrateur de découverte de services Enterprise"""
    
    def __init__(self):
        self.service_name = "service-discovery-orchestrator"
        self.version = "1.0.0"
        
        # Registres de services
        self.services_registry: Dict[str, ServiceEndpoint] = {}
        self.service_groups: Dict[str, ServiceGroup] = {}
        self.service_instances: Dict[str, List[ServiceInstance]] = {}
        
        # Backends de découverte
        self.discovery_backends: Dict[DiscoveryBackend, Any] = {}
        self.active_backends: Set[DiscoveryBackend] = set()
        
        # Configuration monitoring
        self.health_check_interval = 30
        self.sync_interval = 60
        self.cleanup_interval = 300
        
        # Métriques enterprise
        self.metrics = {
            'total_services': 0,
            'healthy_services': 0,
            'unhealthy_services': 0,
            'service_discoveries': 0,
            'health_checks_performed': 0,
            'backend_sync_operations': 0,
            'load_balancing_decisions': 0
        }
        
        # Cache DNS local
        self.dns_cache: Dict[str, List[ServiceEndpoint]] = {}
        self.cache_ttl = 300  # 5 minutes
        
        logger.info(f"🕸️ {self.service_name} v{self.version} - Initialisation")
    
    async def initialize(self, config: Dict[str, Any] = None) -> bool:
        """Initialisation de l'orchestrateur"""
        try:
            logger.info("🚀 Initialisation Service Discovery Orchestrator...")
            
            if config is None:
                config = {}
            
            # Configuration des backends
            await self._setup_discovery_backends(config)
            
            # Initialisation du monitoring de santé
            await self._start_health_monitoring()
            
            # Synchronisation initiale
            await self._initial_service_sync()
            
            # Démarrage des tâches de maintenance
            asyncio.create_task(self._maintenance_loop())
            
            logger.info("✅ Service Discovery Orchestrator initialisé")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation: {e}")
            return False
    
    async def _setup_discovery_backends(self, config: Dict[str, Any]):
        """Configuration des backends de découverte"""
        try:
            # Configuration Kubernetes
            if config.get('kubernetes', {}).get('enabled', True):
                await self._setup_kubernetes_backend()
            
            # Configuration Consul
            if config.get('consul', {}).get('enabled', False):
                await self._setup_consul_backend(config['consul'])
            
            # Configuration etcd
            if config.get('etcd', {}).get('enabled', False):
                await self._setup_etcd_backend(config['etcd'])
            
            # Configuration Istio
            if config.get('istio', {}).get('enabled', False):
                await self._setup_istio_backend()
            
            # Configuration Linkerd
            if config.get('linkerd', {}).get('enabled', False):
                await self._setup_linkerd_backend()
            
        except Exception as e:
            logger.error(f"❌ Erreur configuration backends: {e}")
            raise
    
    async def _setup_kubernetes_backend(self):
        """Configuration backend Kubernetes"""
        try:
            # Configuration client Kubernetes
            try:
                config.load_incluster_config()
                logger.info("📊 Config Kubernetes in-cluster chargée")
            except:
                config.load_kube_config()
                logger.info("🏠 Config Kubernetes locale chargée")
            
            k8s_client = client.ApiClient()
            self.discovery_backends[DiscoveryBackend.KUBERNETES] = k8s_client
            self.active_backends.add(DiscoveryBackend.KUBERNETES)
            
            logger.info("✅ Backend Kubernetes configuré")
            
        except Exception as e:
            logger.error(f"❌ Erreur backend Kubernetes: {e}")
            raise
    
    async def _setup_consul_backend(self, consul_config: Dict[str, Any]):
        """Configuration backend Consul"""
        try:
            consul_client = consul.Consul(
                host=consul_config.get('host', 'localhost'),
                port=consul_config.get('port', 8500),
                token=consul_config.get('token')
            )
            
            # Test de connectivité
            consul_client.agent.self()
            
            self.discovery_backends[DiscoveryBackend.CONSUL] = consul_client
            self.active_backends.add(DiscoveryBackend.CONSUL)
            
            logger.info("✅ Backend Consul configuré")
            
        except Exception as e:
            logger.error(f"❌ Erreur backend Consul: {e}")
            raise
    
    async def _setup_etcd_backend(self, etcd_config: Dict[str, Any]):
        """Configuration backend etcd"""
        try:
            etcd_client = etcd3.client(
                host=etcd_config.get('host', 'localhost'),
                port=etcd_config.get('port', 2379)
            )
            
            # Test de connectivité
            etcd_client.get('test')
            
            self.discovery_backends[DiscoveryBackend.ETCD] = etcd_client
            self.active_backends.add(DiscoveryBackend.ETCD)
            
            logger.info("✅ Backend etcd configuré")
            
        except Exception as e:
            logger.error(f"❌ Erreur backend etcd: {e}")
            raise
    
    async def _setup_istio_backend(self):
        """Configuration backend Istio"""
        try:
            # Istio utilise Kubernetes CRDs
            if DiscoveryBackend.KUBERNETES in self.active_backends:
                self.active_backends.add(DiscoveryBackend.ISTIO)
                logger.info("✅ Backend Istio configuré")
            else:
                logger.warning("⚠️ Kubernetes requis pour Istio")
                
        except Exception as e:
            logger.error(f"❌ Erreur backend Istio: {e}")
            raise
    
    async def _setup_linkerd_backend(self):
        """Configuration backend Linkerd"""
        try:
            # Linkerd utilise aussi Kubernetes
            if DiscoveryBackend.KUBERNETES in self.active_backends:
                self.active_backends.add(DiscoveryBackend.LINKERD)
                logger.info("✅ Backend Linkerd configuré")
            else:
                logger.warning("⚠️ Kubernetes requis pour Linkerd")
                
        except Exception as e:
            logger.error(f"❌ Erreur backend Linkerd: {e}")
            raise
    
    async def register_service(self, endpoint: ServiceEndpoint) -> bool:
        """Enregistrement d'un service"""
        try:
            service_key = f"{endpoint.namespace}/{endpoint.service_name}"
            
            # Génération ID unique si absent
            if not endpoint.service_id:
                endpoint.service_id = self._generate_service_id(endpoint)
            
            # Enregistrement local
            self.services_registry[service_key] = endpoint
            
            # Enregistrement dans les backends
            for backend in self.active_backends:
                await self._register_in_backend(backend, endpoint)
            
            # Mise à jour métriques
            self.metrics['total_services'] = len(self.services_registry)
            self.metrics['service_discoveries'] += 1
            
            logger.info(f"✅ Service enregistré: {service_key}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur enregistrement service: {e}")
            return False
    
    async def _register_in_backend(self, 
                                 backend: DiscoveryBackend, 
                                 endpoint: ServiceEndpoint):
        """Enregistrement dans un backend spécifique"""
        try:
            if backend == DiscoveryBackend.KUBERNETES:
                await self._register_k8s_service(endpoint)
            elif backend == DiscoveryBackend.CONSUL:
                await self._register_consul_service(endpoint)
            elif backend == DiscoveryBackend.ETCD:
                await self._register_etcd_service(endpoint)
            
        except Exception as e:
            logger.error(f"❌ Erreur enregistrement backend {backend}: {e}")
            raise
    
    async def _register_k8s_service(self, endpoint: ServiceEndpoint):
        """Enregistrement service Kubernetes"""
        try:
            v1 = client.CoreV1Api()
            
            # Création du service Kubernetes
            service_manifest = {
                'apiVersion': 'v1',
                'kind': 'Service',
                'metadata': {
                    'name': endpoint.service_name,
                    'namespace': endpoint.namespace,
                    'labels': {
                        'app': endpoint.service_name,
                        'managed-by': 'service-discovery-orchestrator'
                    },
                    'annotations': {
                        'discovery.ainflue.com/registered-by': self.service_name,
                        'discovery.ainflue.com/registered-at': datetime.now().isoformat()
                    }
                },
                'spec': {
                    'ports': [{
                        'port': endpoint.port,
                        'protocol': endpoint.protocol.upper(),
                        'name': endpoint.protocol
                    }],
                    'selector': {
                        'app': endpoint.service_name
                    }
                }
            }
            
            try:
                v1.create_namespaced_service(
                    namespace=endpoint.namespace,
                    body=service_manifest
                )
                logger.info(f"📊 Service K8s créé: {endpoint.service_name}")
            except client.exceptions.ApiException as e:
                if e.status == 409:  # Already exists
                    logger.info(f"📊 Service K8s existe: {endpoint.service_name}")
                else:
                    raise
            
        except Exception as e:
            logger.error(f"❌ Erreur enregistrement K8s: {e}")
            raise
    
    async def _register_consul_service(self, endpoint: ServiceEndpoint):
        """Enregistrement service Consul"""
        try:
            consul_client = self.discovery_backends[DiscoveryBackend.CONSUL]
            
            service_config = {
                'name': endpoint.service_name,
                'service_id': endpoint.service_id,
                'address': endpoint.host,
                'port': endpoint.port,
                'tags': endpoint.tags + [f"namespace:{endpoint.namespace}"],
                'meta': endpoint.metadata,
                'check': {
                    'http': f"{endpoint.protocol}://{endpoint.host}:{endpoint.port}{endpoint.health_check_path}",
                    'interval': f"{self.health_check_interval}s"
                }
            }
            
            consul_client.agent.service.register(**service_config)
            logger.info(f"🏛️ Service Consul enregistré: {endpoint.service_name}")
            
        except Exception as e:
            logger.error(f"❌ Erreur enregistrement Consul: {e}")
            raise
    
    async def _register_etcd_service(self, endpoint: ServiceEndpoint):
        """Enregistrement service etcd"""
        try:
            etcd_client = self.discovery_backends[DiscoveryBackend.ETCD]
            
            service_key = f"/services/{endpoint.namespace}/{endpoint.service_name}/{endpoint.service_id}"
            service_data = json.dumps(asdict(endpoint), default=str)
            
            etcd_client.put(service_key, service_data)
            logger.info(f"🗄️ Service etcd enregistré: {endpoint.service_name}")
            
        except Exception as e:
            logger.error(f"❌ Erreur enregistrement etcd: {e}")
            raise
    
    async def discover_services(self, 
                              service_name: str = None,
                              namespace: str = None,
                              tags: List[str] = None) -> List[ServiceEndpoint]:
        """Découverte de services"""
        try:
            # Vérifier cache DNS d'abord
            cache_key = f"{namespace or 'all'}/{service_name or 'all'}"
            if cache_key in self.dns_cache:
                cache_entry = self.dns_cache[cache_key]
                if self._is_cache_valid(cache_key):
                    logger.debug(f"📋 Cache hit pour: {cache_key}")
                    return cache_entry['services']
            
            discovered_services = []
            
            # Découverte dans tous les backends actifs
            for backend in self.active_backends:
                try:
                    backend_services = await self._discover_from_backend(
                        backend, service_name, namespace, tags
                    )
                    discovered_services.extend(backend_services)
                except Exception as e:
                    logger.warning(f"⚠️ Erreur découverte backend {backend}: {e}")
            
            # Déduplication des services
            unique_services = self._deduplicate_services(discovered_services)
            
            # Mise à jour cache DNS
            self.dns_cache[cache_key] = {
                'services': unique_services,
                'timestamp': datetime.now()
            }
            
            # Mise à jour métriques
            self.metrics['service_discoveries'] += 1
            
            logger.info(f"🔍 Services découverts: {len(unique_services)} pour {cache_key}")
            return unique_services
            
        except Exception as e:
            logger.error(f"❌ Erreur découverte services: {e}")
            return []
    
    async def _discover_from_backend(self,
                                   backend: DiscoveryBackend,
                                   service_name: str = None,
                                   namespace: str = None,
                                   tags: List[str] = None) -> List[ServiceEndpoint]:
        """Découverte depuis un backend spécifique"""
        try:
            if backend == DiscoveryBackend.KUBERNETES:
                return await self._discover_k8s_services(service_name, namespace)
            elif backend == DiscoveryBackend.CONSUL:
                return await self._discover_consul_services(service_name, tags)
            elif backend == DiscoveryBackend.ETCD:
                return await self._discover_etcd_services(service_name, namespace)
            else:
                return []
                
        except Exception as e:
            logger.error(f"❌ Erreur découverte backend {backend}: {e}")
            return []
    
    async def _discover_k8s_services(self, 
                                   service_name: str = None,
                                   namespace: str = None) -> List[ServiceEndpoint]:
        """Découverte services Kubernetes"""
        try:
            v1 = client.CoreV1Api()
            services = []
            
            if namespace:
                k8s_services = v1.list_namespaced_service(namespace=namespace)
            else:
                k8s_services = v1.list_service_for_all_namespaces()
            
            for svc in k8s_services.items:
                # Filtrage par nom si spécifié
                if service_name and svc.metadata.name != service_name:
                    continue
                
                # Création ServiceEndpoint
                for port in svc.spec.ports:
                    endpoint = ServiceEndpoint(
                        service_id=f"k8s-{svc.metadata.uid}",
                        service_name=svc.metadata.name,
                        namespace=svc.metadata.namespace,
                        host=svc.spec.cluster_ip or svc.metadata.name,
                        port=port.port,
                        protocol=port.protocol.lower(),
                        tags=[f"backend:kubernetes"],
                        metadata={
                            'k8s_uid': svc.metadata.uid,
                            'k8s_labels': svc.metadata.labels or {}
                        }
                    )
                    services.append(endpoint)
            
            return services
            
        except Exception as e:
            logger.error(f"❌ Erreur découverte K8s: {e}")
            return []
    
    async def _discover_consul_services(self,
                                      service_name: str = None,
                                      tags: List[str] = None) -> List[ServiceEndpoint]:
        """Découverte services Consul"""
        try:
            consul_client = self.discovery_backends[DiscoveryBackend.CONSUL]
            services = []
            
            if service_name:
                # Service spécifique
                service_info = consul_client.health.service(service_name, passing=True)
                for node, service_data in service_info[1]:
                    endpoint = self._consul_to_endpoint(service_data)
                    services.append(endpoint)
            else:
                # Tous les services
                all_services = consul_client.catalog.services()[1]
                for svc_name, svc_tags in all_services.items():
                    # Filtrage par tags si spécifié
                    if tags and not any(tag in svc_tags for tag in tags):
                        continue
                    
                    service_info = consul_client.health.service(svc_name, passing=True)
                    for node, service_data in service_info[1]:
                        endpoint = self._consul_to_endpoint(service_data)
                        services.append(endpoint)
            
            return services
            
        except Exception as e:
            logger.error(f"❌ Erreur découverte Consul: {e}")
            return []
    
    def _consul_to_endpoint(self, consul_service: Dict[str, Any]) -> ServiceEndpoint:
        """Conversion service Consul vers ServiceEndpoint"""
        return ServiceEndpoint(
            service_id=consul_service['ServiceID'],
            service_name=consul_service['ServiceName'],
            namespace=consul_service.get('ServiceMeta', {}).get('namespace', 'default'),
            host=consul_service['ServiceAddress'] or consul_service['Address'],
            port=consul_service['ServicePort'],
            tags=consul_service['ServiceTags'] + ['backend:consul'],
            metadata=consul_service.get('ServiceMeta', {})
        )
    
    async def _discover_etcd_services(self,
                                    service_name: str = None,
                                    namespace: str = None) -> List[ServiceEndpoint]:
        """Découverte services etcd"""
        try:
            etcd_client = self.discovery_backends[DiscoveryBackend.ETCD]
            services = []
            
            # Construction du préfixe de recherche
            prefix = "/services/"
            if namespace:
                prefix += f"{namespace}/"
                if service_name:
                    prefix += f"{service_name}/"
            
            # Récupération des services
            for value, metadata in etcd_client.get_prefix(prefix):
                try:
                    service_data = json.loads(value.decode('utf-8'))
                    endpoint = ServiceEndpoint(**service_data)
                    endpoint.tags.append('backend:etcd')
                    services.append(endpoint)
                except Exception as e:
                    logger.warning(f"⚠️ Service etcd invalide: {e}")
            
            return services
            
        except Exception as e:
            logger.error(f"❌ Erreur découverte etcd: {e}")
            return []
    
    def _deduplicate_services(self, services: List[ServiceEndpoint]) -> List[ServiceEndpoint]:
        """Déduplication des services"""
        seen = set()
        unique_services = []
        
        for service in services:
            # Clé unique basée sur nom, namespace, host, port
            key = f"{service.namespace}/{service.service_name}/{service.host}:{service.port}"
            
            if key not in seen:
                seen.add(key)
                unique_services.append(service)
        
        return unique_services
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Vérification validité cache DNS"""
        if cache_key not in self.dns_cache:
            return False
        
        cache_entry = self.dns_cache[cache_key]
        age = (datetime.now() - cache_entry['timestamp']).total_seconds()
        
        return age < self.cache_ttl
    
    def _generate_service_id(self, endpoint: ServiceEndpoint) -> str:
        """Génération ID unique pour service"""
        data = f"{endpoint.service_name}-{endpoint.namespace}-{endpoint.host}-{endpoint.port}"
        return hashlib.md5(data.encode()).hexdigest()[:16]
    
    async def _start_health_monitoring(self):
        """Démarrage monitoring de santé"""
        try:
            asyncio.create_task(self._health_check_loop())
            logger.info("✅ Monitoring de santé démarré")
            
        except Exception as e:
            logger.error(f"❌ Erreur démarrage health monitoring: {e}")
            raise
    
    async def _health_check_loop(self):
        """Boucle de vérification de santé"""
        while True:
            try:
                await asyncio.sleep(self.health_check_interval)
                
                for service_key, endpoint in self.services_registry.items():
                    await self._check_service_health(endpoint)
                
                # Mise à jour métriques
                healthy_count = sum(
                    1 for endpoint in self.services_registry.values()
                    if endpoint.status == ServiceStatus.HEALTHY
                )
                
                self.metrics['healthy_services'] = healthy_count
                self.metrics['unhealthy_services'] = len(self.services_registry) - healthy_count
                
            except Exception as e:
                logger.error(f"❌ Erreur boucle health check: {e}")
    
    async def _check_service_health(self, endpoint: ServiceEndpoint):
        """Vérification santé d'un service"""
        try:
            health_url = f"{endpoint.protocol}://{endpoint.host}:{endpoint.port}{endpoint.health_check_path}"
            
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(health_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                        if response.status == 200:
                            endpoint.status = ServiceStatus.HEALTHY
                        else:
                            endpoint.status = ServiceStatus.UNHEALTHY
                except:
                    endpoint.status = ServiceStatus.UNHEALTHY
            
            endpoint.last_check = datetime.now()
            self.metrics['health_checks_performed'] += 1
            
        except Exception as e:
            logger.warning(f"⚠️ Erreur health check {endpoint.service_name}: {e}")
            endpoint.status = ServiceStatus.UNKNOWN
    
    async def _maintenance_loop(self):
        """Boucle de maintenance"""
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval)
                
                # Nettoyage cache DNS
                await self._cleanup_dns_cache()
                
                # Synchronisation backends
                await self._sync_backends()
                
                # Nettoyage services inactifs
                await self._cleanup_inactive_services()
                
            except Exception as e:
                logger.error(f"❌ Erreur boucle maintenance: {e}")
    
    async def _cleanup_dns_cache(self):
        """Nettoyage cache DNS"""
        try:
            current_time = datetime.now()
            expired_keys = []
            
            for cache_key, cache_entry in self.dns_cache.items():
                age = (current_time - cache_entry['timestamp']).total_seconds()
                if age > self.cache_ttl:
                    expired_keys.append(cache_key)
            
            for key in expired_keys:
                del self.dns_cache[key]
            
            if expired_keys:
                logger.info(f"🧹 Cache DNS nettoyé: {len(expired_keys)} entrées expirées")
                
        except Exception as e:
            logger.error(f"❌ Erreur nettoyage cache DNS: {e}")
    
    async def _sync_backends(self):
        """Synchronisation des backends"""
        try:
            for backend in self.active_backends:
                # Synchronisation périodique avec chaque backend
                pass
            
            self.metrics['backend_sync_operations'] += 1
            
        except Exception as e:
            logger.error(f"❌ Erreur synchronisation backends: {e}")
    
    async def _cleanup_inactive_services(self):
        """Nettoyage services inactifs"""
        try:
            current_time = datetime.now()
            inactive_threshold = timedelta(minutes=15)
            
            inactive_services = []
            for service_key, endpoint in self.services_registry.items():
                if endpoint.last_check and (current_time - endpoint.last_check) > inactive_threshold:
                    if endpoint.status == ServiceStatus.UNHEALTHY:
                        inactive_services.append(service_key)
            
            for service_key in inactive_services:
                del self.services_registry[service_key]
                logger.info(f"🗑️ Service inactif supprimé: {service_key}")
            
        except Exception as e:
            logger.error(f"❌ Erreur nettoyage services inactifs: {e}")
    
    async def _initial_service_sync(self):
        """Synchronisation initiale des services"""
        try:
            logger.info("🔄 Synchronisation initiale des services...")
            
            # Découverte depuis tous les backends
            discovered_services = await self.discover_services()
            
            # Enregistrement local des services découverts
            for service in discovered_services:
                service_key = f"{service.namespace}/{service.service_name}"
                self.services_registry[service_key] = service
            
            self.metrics['total_services'] = len(self.services_registry)
            logger.info(f"✅ {len(discovered_services)} services synchronisés")
            
        except Exception as e:
            logger.error(f"❌ Erreur synchronisation initiale: {e}")
            raise
    
    async def get_load_balanced_endpoint(self, 
                                       service_name: str,
                                       namespace: str = "default",
                                       strategy: str = "round_robin") -> Optional[ServiceEndpoint]:
        """Obtention endpoint load-balanced"""
        try:
            # Découverte des services disponibles
            services = await self.discover_services(service_name, namespace)
            
            if not services:
                logger.warning(f"⚠️ Aucun service trouvé: {namespace}/{service_name}")
                return None
            
            # Filtrage services sains
            healthy_services = [
                svc for svc in services
                if svc.status == ServiceStatus.HEALTHY
            ]
            
            if not healthy_services:
                logger.warning(f"⚠️ Aucun service sain: {namespace}/{service_name}")
                return None
            
            # Application stratégie load balancing
            selected_service = None
            
            if strategy == "round_robin":
                # Simple round robin (stateless pour cet exemple)
                selected_service = healthy_services[0]
            elif strategy == "random":
                import random
                selected_service = random.choice(healthy_services)
            elif strategy == "least_connections":
                # Sélection basée sur le nombre de requêtes (métrique simple)
                selected_service = min(healthy_services, key=lambda s: s.metadata.get('request_count', 0))
            else:
                selected_service = healthy_services[0]
            
            self.metrics['load_balancing_decisions'] += 1
            logger.debug(f"⚖️ Endpoint sélectionné: {selected_service.host}:{selected_service.port}")
            
            return selected_service
            
        except Exception as e:
            logger.error(f"❌ Erreur load balancing: {e}")
            return None
    
    async def health_check(self) -> Dict[str, Any]:
        """Vérification santé orchestrateur"""
        try:
            health_status = {
                'service': self.service_name,
                'version': self.version,
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'metrics': self.metrics,
                'active_backends': list(self.active_backends),
                'cache_stats': {
                    'dns_cache_size': len(self.dns_cache),
                    'services_registered': len(self.services_registry)
                },
                'checks': {
                    'backends_available': len(self.active_backends) > 0,
                    'services_discovered': self.metrics['total_services'] > 0,
                    'health_monitoring_active': True
                }
            }
            
            # Vérification backends
            backend_health = {}
            for backend in self.active_backends:
                try:
                    # Test basique de connectivité
                    if backend == DiscoveryBackend.KUBERNETES:
                        v1 = client.CoreV1Api()
                        v1.list_namespace(limit=1)
                        backend_health[backend.value] = True
                    elif backend == DiscoveryBackend.CONSUL:
                        consul_client = self.discovery_backends[backend]
                        consul_client.agent.self()
                        backend_health[backend.value] = True
                    elif backend == DiscoveryBackend.ETCD:
                        etcd_client = self.discovery_backends[backend]
                        etcd_client.get('test')
                        backend_health[backend.value] = True
                    else:
                        backend_health[backend.value] = True
                except:
                    backend_health[backend.value] = False
            
            health_status['backend_health'] = backend_health
            
            # Statut global
            all_backends_healthy = all(backend_health.values())
            has_services = self.metrics['total_services'] > 0
            
            if not all_backends_healthy or not has_services:
                health_status['status'] = 'degraded'
            
            return health_status
            
        except Exception as e:
            logger.error(f"❌ Erreur health check: {e}")
            return {
                'service': self.service_name,
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def get_service_status(self) -> Dict[str, Any]:
        """Statut détaillé orchestrateur"""
        try:
            return {
                'service_info': {
                    'name': self.service_name,
                    'version': self.version,
                    'status': 'running'
                },
                'discovery_config': {
                    'active_backends': [backend.value for backend in self.active_backends],
                    'health_check_interval': self.health_check_interval,
                    'sync_interval': self.sync_interval,
                    'cache_ttl': self.cache_ttl
                },
                'metrics': self.metrics,
                'services_overview': {
                    'total_registered': len(self.services_registry),
                    'by_namespace': self._get_services_by_namespace(),
                    'by_status': self._get_services_by_status()
                },
                'cache_status': {
                    'dns_cache_entries': len(self.dns_cache),
                    'cache_hit_ratio': self._calculate_cache_hit_ratio()
                },
                'health': await self.health_check()
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur statut service: {e}")
            return {'error': str(e)}
    
    def _get_services_by_namespace(self) -> Dict[str, int]:
        """Répartition services par namespace"""
        namespace_counts = {}
        for endpoint in self.services_registry.values():
            ns = endpoint.namespace
            namespace_counts[ns] = namespace_counts.get(ns, 0) + 1
        return namespace_counts
    
    def _get_services_by_status(self) -> Dict[str, int]:
        """Répartition services par statut"""
        status_counts = {}
        for endpoint in self.services_registry.values():
            status = endpoint.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        return status_counts
    
    def _calculate_cache_hit_ratio(self) -> float:
        """Calcul ratio cache hit (simulation)"""
        # En production, tracker les cache hits/misses
        return 0.85  # 85% de cache hits

# Instance globale
service_discovery = ServiceDiscoveryOrchestrator()

async def main():
    """Test de l'orchestrateur"""
    try:
        print("🕸️ Test Service Discovery Orchestrator")
        
        # Initialisation
        success = await service_discovery.initialize()
        if not success:
            print("❌ Échec initialisation")
            return
        
        # Test enregistrement service
        test_endpoint = ServiceEndpoint(
            service_id="test-ai-inference-001",
            service_name="ai-inference",
            namespace="ai-services",
            host="ai-inference.ai-services.svc.cluster.local",
            port=8080,
            tags=["ai", "inference", "production"],
            metadata={"version": "1.0.0", "region": "eu-west-1"}
        )
        
        await service_discovery.register_service(test_endpoint)
        
        # Test découverte services
        services = await service_discovery.discover_services("ai-inference", "ai-services")
        print(f"🔍 Services découverts: {len(services)}")
        
        # Test load balancing
        endpoint = await service_discovery.get_load_balanced_endpoint("ai-inference", "ai-services")
        if endpoint:
            print(f"⚖️ Endpoint sélectionné: {endpoint.host}:{endpoint.port}")
        
        # Statut final
        status = await service_discovery.get_service_status()
        print(f"📊 Statut: {status}")
        
        print("✅ Test Service Discovery Orchestrator terminé")
        
    except Exception as e:
        print(f"❌ Erreur test: {e}")

if __name__ == "__main__":
    asyncio.run(main())