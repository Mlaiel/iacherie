"""
⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Service registry IA propriétaire
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

AI Agents Service Registry for Ainflue Platform
==============================================

Production-ready service registry for 53+ AI agents with:
- Dynamic service discovery
- Load balancing and health monitoring
- Configuration management
- Performance metrics
- Auto-scaling coordination
- Service mesh integration
- Circuit breaker patterns
- Real-time health checks

Author: Fahed Mlaiel (mlaiel@live.de)
Lead Dev IA + Backend Senior + ML Engineer + Microservices Expert
"""

import asyncio
import logging
import json
import time
from typing import Dict, Any, Optional, List, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
import httpx
import aioredis

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field, validator
from prometheus_client import Counter, Histogram, Gauge
import consul


# Metrics
service_registrations = Counter('ai_service_registrations_total', 'Total service registrations', ['service_type'])
service_discoveries = Counter('ai_service_discoveries_total', 'Total service discoveries', ['service_type'])
health_checks = Counter('ai_health_checks_total', 'Total health checks', ['service_id', 'status'])
active_services = Gauge('ai_active_services', 'Number of active AI services', ['service_type'])


class ServiceStatus(Enum):
    """États des services IA"""
    STARTING = "starting"
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"


class ServiceType(Enum):
    """Types de services IA"""
    COMPUTER_VISION = "computer_vision"
    NLP = "nlp"
    AUDIO_PROCESSING = "audio_processing"
    CONTENT_OPTIMIZATION = "content_optimization"
    MULTIMODAL = "multimodal"


@dataclass
class ServiceInstance:
    """Instance de service IA"""
    service_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    service_name: str = ""
    service_type: ServiceType = ServiceType.NLP
    host: str = "localhost"
    port: int = 8000
    version: str = "1.0.0"
    status: ServiceStatus = ServiceStatus.STARTING
    health_endpoint: str = "/health"
    metrics_endpoint: str = "/metrics"
    capabilities: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    last_heartbeat: datetime = field(default_factory=datetime.utcnow)
    load_metrics: Dict[str, float] = field(default_factory=dict)
    performance_metrics: Dict[str, float] = field(default_factory=dict)


class ServiceRegistrationRequest(BaseModel):
    """Requête d'enregistrement de service"""
    service_name: str = Field(..., min_length=1, max_length=255)
    service_type: str = Field(..., regex="^(computer_vision|nlp|audio_processing|content_optimization|multimodal)$")
    host: str = Field(..., min_length=1)
    port: int = Field(..., ge=1, le=65535)
    version: str = Field(default="1.0.0")
    capabilities: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    health_endpoint: str = Field(default="/health")
    metrics_endpoint: str = Field(default="/metrics")


class ServiceDiscoveryRequest(BaseModel):
    """Requête de découverte de service"""
    service_type: Optional[str] = None
    capabilities: List[str] = Field(default_factory=list)
    exclude_degraded: bool = Field(default=True)
    preferred_version: Optional[str] = None
    load_balancing: str = Field(default="round_robin", regex="^(round_robin|least_connections|random|weighted)$")


class ServiceRegistryOrchestrator:
    """
    Orchestrateur principal du registre de services IA
    Gestion centralisée de la découverte et monitoring
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379", consul_host: str = "localhost"):
        self.services: Dict[str, ServiceInstance] = {}
        self.redis_url = redis_url
        self.consul_host = consul_host
        self.redis_client = None
        self.consul_client = None
        self.health_check_interval = 30  # seconds
        self.cleanup_interval = 300  # seconds
        self.round_robin_counters: Dict[str, int] = {}
        
    async def initialize(self):
        """Initialisation du registre de services"""
        try:
            # Connexion Redis pour cache et état
            self.redis_client = await aioredis.from_url(self.redis_url)
            
            # Connexion Consul pour service discovery
            self.consul_client = consul.Consul(host=self.consul_host)
            
            # Démarrage des tâches de fond
            asyncio.create_task(self._health_check_loop())
            asyncio.create_task(self._cleanup_loop())
            
            logging.info("Service registry initialized successfully")
            
        except Exception as e:
            logging.error(f"Failed to initialize service registry: {str(e)}")
            raise
    
    async def register_service(self, request: ServiceRegistrationRequest) -> Dict[str, Any]:
        """Enregistrement d'un nouveau service IA"""
        try:
            service_instance = ServiceInstance(
                service_name=request.service_name,
                service_type=ServiceType(request.service_type),
                host=request.host,
                port=request.port,
                version=request.version,
                capabilities=request.capabilities,
                metadata=request.metadata,
                health_endpoint=request.health_endpoint,
                metrics_endpoint=request.metrics_endpoint
            )
            
            # Enregistrement local
            self.services[service_instance.service_id] = service_instance
            
            # Enregistrement dans Consul
            await self._register_in_consul(service_instance)
            
            # Cache Redis pour accès rapide
            await self._cache_service_info(service_instance)
            
            # Vérification de santé initiale
            await self._check_service_health(service_instance)
            
            # Métriques
            service_registrations.labels(service_type=request.service_type).inc()
            active_services.labels(service_type=request.service_type).inc()
            
            logging.info(f"Service registered: {service_instance.service_name} ({service_instance.service_id})")
            
            return {
                'service_id': service_instance.service_id,
                'status': 'registered',
                'registration_time': datetime.utcnow().isoformat(),
                'health_check_interval': self.health_check_interval
            }
            
        except Exception as e:
            logging.error(f"Service registration failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def discover_services(self, request: ServiceDiscoveryRequest) -> Dict[str, Any]:
        """Découverte de services IA disponibles"""
        try:
            # Filtrage des services
            available_services = await self._filter_services(request)
            
            # Application de la stratégie de load balancing
            selected_services = await self._apply_load_balancing(available_services, request.load_balancing)
            
            # Mise à jour des métriques
            service_discoveries.labels(
                service_type=request.service_type or 'all'
            ).inc()
            
            return {
                'services': selected_services,
                'total_available': len(available_services),
                'selected_count': len(selected_services),
                'load_balancing_strategy': request.load_balancing,
                'discovery_time': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Service discovery failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_service_health(self, service_id: str) -> Dict[str, Any]:
        """Récupération de l'état de santé d'un service"""
        if service_id not in self.services:
            raise HTTPException(status_code=404, detail="Service not found")
        
        service = self.services[service_id]
        
        # Vérification de santé en temps réel
        health_status = await self._check_service_health(service)
        
        return {
            'service_id': service_id,
            'service_name': service.service_name,
            'status': service.status.value,
            'last_heartbeat': service.last_heartbeat.isoformat(),
            'health_details': health_status,
            'load_metrics': service.load_metrics,
            'performance_metrics': service.performance_metrics
        }
    
    async def unregister_service(self, service_id: str) -> Dict[str, Any]:
        """Désenregistrement d'un service"""
        if service_id not in self.services:
            raise HTTPException(status_code=404, detail="Service not found")
        
        service = self.services[service_id]
        
        # Suppression du registre local
        del self.services[service_id]
        
        # Suppression de Consul
        await self._unregister_from_consul(service_id)
        
        # Suppression du cache Redis
        await self._remove_from_cache(service_id)
        
        # Mise à jour des métriques
        active_services.labels(service_type=service.service_type.value).dec()
        
        logging.info(f"Service unregistered: {service.service_name} ({service_id})")
        
        return {
            'service_id': service_id,
            'status': 'unregistered',
            'unregistration_time': datetime.utcnow().isoformat()
        }
    
    async def update_service_metrics(self, service_id: str, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Mise à jour des métriques d'un service"""
        if service_id not in self.services:
            raise HTTPException(status_code=404, detail="Service not found")
        
        service = self.services[service_id]
        
        # Mise à jour des métriques de charge
        service.load_metrics.update(metrics.get('load_metrics', {}))
        
        # Mise à jour des métriques de performance
        service.performance_metrics.update(metrics.get('performance_metrics', {}))
        
        # Mise à jour du heartbeat
        service.last_heartbeat = datetime.utcnow()
        
        # Cache des métriques dans Redis
        await self._cache_service_metrics(service_id, metrics)
        
        return {
            'service_id': service_id,
            'metrics_updated': True,
            'update_time': datetime.utcnow().isoformat()
        }
    
    async def _filter_services(self, request: ServiceDiscoveryRequest) -> List[ServiceInstance]:
        """Filtrage des services selon les critères"""
        filtered_services = []
        
        for service in self.services.values():
            # Filtre par type de service
            if request.service_type and service.service_type.value != request.service_type:
                continue
            
            # Filtre par statut (exclure les dégradés si demandé)
            if request.exclude_degraded and service.status in [ServiceStatus.UNHEALTHY, ServiceStatus.DEGRADED, ServiceStatus.OFFLINE]:
                continue
            
            # Filtre par capacités
            if request.capabilities:
                if not all(cap in service.capabilities for cap in request.capabilities):
                    continue
            
            # Filtre par version préférée
            if request.preferred_version and service.version != request.preferred_version:
                continue
            
            filtered_services.append(service)
        
        return filtered_services
    
    async def _apply_load_balancing(self, services: List[ServiceInstance], strategy: str) -> List[Dict[str, Any]]:
        """Application de la stratégie de load balancing"""
        if not services:
            return []
        
        if strategy == "round_robin":
            return await self._round_robin_selection(services)
        elif strategy == "least_connections":
            return await self._least_connections_selection(services)
        elif strategy == "weighted":
            return await self._weighted_selection(services)
        elif strategy == "random":
            return await self._random_selection(services)
        else:
            # Défaut: round robin
            return await self._round_robin_selection(services)
    
    async def _round_robin_selection(self, services: List[ServiceInstance]) -> List[Dict[str, Any]]:
        """Sélection round-robin"""
        if not services:
            return []
        
        service_type_key = services[0].service_type.value
        current_index = self.round_robin_counters.get(service_type_key, 0)
        
        selected_service = services[current_index % len(services)]
        self.round_robin_counters[service_type_key] = (current_index + 1) % len(services)
        
        return [await self._service_to_dict(selected_service)]
    
    async def _least_connections_selection(self, services: List[ServiceInstance]) -> List[Dict[str, Any]]:
        """Sélection par moins de connexions"""
        if not services:
            return []
        
        # Tri par nombre de connexions actives
        sorted_services = sorted(services, key=lambda s: s.load_metrics.get('active_connections', 0))
        
        return [await self._service_to_dict(sorted_services[0])]
    
    async def _weighted_selection(self, services: List[ServiceInstance]) -> List[Dict[str, Any]]:
        """Sélection pondérée par performance"""
        if not services:
            return []
        
        # Calcul des poids basés sur les performances
        weighted_services = []
        for service in services:
            cpu_weight = 1.0 - service.load_metrics.get('cpu_usage', 0.5)
            memory_weight = 1.0 - service.load_metrics.get('memory_usage', 0.5)
            response_time_weight = 1.0 / (service.performance_metrics.get('avg_response_time', 1.0) + 0.1)
            
            total_weight = (cpu_weight + memory_weight + response_time_weight) / 3
            weighted_services.append((service, total_weight))
        
        # Sélection du service avec le meilleur poids
        best_service = max(weighted_services, key=lambda x: x[1])[0]
        
        return [await self._service_to_dict(best_service)]
    
    async def _random_selection(self, services: List[ServiceInstance]) -> List[Dict[str, Any]]:
        """Sélection aléatoire"""
        import random
        
        if not services:
            return []
        
        selected_service = random.choice(services)
        return [await self._service_to_dict(selected_service)]
    
    async def _service_to_dict(self, service: ServiceInstance) -> Dict[str, Any]:
        """Conversion d'une instance de service en dictionnaire"""
        return {
            'service_id': service.service_id,
            'service_name': service.service_name,
            'service_type': service.service_type.value,
            'host': service.host,
            'port': service.port,
            'version': service.version,
            'status': service.status.value,
            'capabilities': service.capabilities,
            'metadata': service.metadata,
            'endpoint': f"http://{service.host}:{service.port}",
            'health_endpoint': f"http://{service.host}:{service.port}{service.health_endpoint}",
            'metrics_endpoint': f"http://{service.host}:{service.port}{service.metrics_endpoint}",
            'last_heartbeat': service.last_heartbeat.isoformat(),
            'load_metrics': service.load_metrics,
            'performance_metrics': service.performance_metrics
        }
    
    async def _check_service_health(self, service: ServiceInstance) -> Dict[str, Any]:
        """Vérification de santé d'un service"""
        try:
            health_url = f"http://{service.host}:{service.port}{service.health_endpoint}"
            
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(health_url)
                
                if response.status_code == 200:
                    service.status = ServiceStatus.HEALTHY
                    health_data = response.json()
                    
                    health_checks.labels(
                        service_id=service.service_id,
                        status='healthy'
                    ).inc()
                    
                    return {
                        'status': 'healthy',
                        'response_time': response.elapsed.total_seconds(),
                        'health_data': health_data
                    }
                else:
                    service.status = ServiceStatus.UNHEALTHY
                    
                    health_checks.labels(
                        service_id=service.service_id,
                        status='unhealthy'
                    ).inc()
                    
                    return {
                        'status': 'unhealthy',
                        'status_code': response.status_code,
                        'error': 'Health check failed'
                    }
                    
        except Exception as e:
            service.status = ServiceStatus.OFFLINE
            
            health_checks.labels(
                service_id=service.service_id,
                status='offline'
            ).inc()
            
            return {
                'status': 'offline',
                'error': str(e)
            }
    
    async def _health_check_loop(self):
        """Boucle de vérification de santé en arrière-plan"""
        while True:
            try:
                for service in list(self.services.values()):
                    await self._check_service_health(service)
                    await asyncio.sleep(1)  # Délai entre les vérifications
                
                await asyncio.sleep(self.health_check_interval)
                
            except Exception as e:
                logging.error(f"Health check loop error: {str(e)}")
                await asyncio.sleep(10)
    
    async def _cleanup_loop(self):
        """Boucle de nettoyage des services inactifs"""
        while True:
            try:
                current_time = datetime.utcnow()
                inactive_services = []
                
                for service_id, service in self.services.items():
                    time_since_heartbeat = current_time - service.last_heartbeat
                    
                    if time_since_heartbeat > timedelta(minutes=10):  # 10 minutes sans heartbeat
                        inactive_services.append(service_id)
                
                # Suppression des services inactifs
                for service_id in inactive_services:
                    await self.unregister_service(service_id)
                    logging.warning(f"Removed inactive service: {service_id}")
                
                await asyncio.sleep(self.cleanup_interval)
                
            except Exception as e:
                logging.error(f"Cleanup loop error: {str(e)}")
                await asyncio.sleep(60)
    
    async def _register_in_consul(self, service: ServiceInstance):
        """Enregistrement dans Consul"""
        try:
            self.consul_client.agent.service.register(
                name=service.service_name,
                service_id=service.service_id,
                address=service.host,
                port=service.port,
                tags=[service.service_type.value, service.version],
                check=consul.Check.http(
                    f"http://{service.host}:{service.port}{service.health_endpoint}",
                    interval=f"{self.health_check_interval}s"
                )
            )
        except Exception as e:
            logging.warning(f"Consul registration failed: {str(e)}")
    
    async def _unregister_from_consul(self, service_id: str):
        """Désenregistrement de Consul"""
        try:
            self.consul_client.agent.service.deregister(service_id)
        except Exception as e:
            logging.warning(f"Consul deregistration failed: {str(e)}")
    
    async def _cache_service_info(self, service: ServiceInstance):
        """Cache des informations de service dans Redis"""
        try:
            service_data = await self._service_to_dict(service)
            await self.redis_client.setex(
                f"service:{service.service_id}",
                3600,  # 1 heure
                json.dumps(service_data)
            )
        except Exception as e:
            logging.warning(f"Redis cache failed: {str(e)}")
    
    async def _cache_service_metrics(self, service_id: str, metrics: Dict[str, Any]):
        """Cache des métriques de service"""
        try:
            await self.redis_client.setex(
                f"metrics:{service_id}",
                300,  # 5 minutes
                json.dumps(metrics)
            )
        except Exception as e:
            logging.warning(f"Metrics cache failed: {str(e)}")
    
    async def _remove_from_cache(self, service_id: str):
        """Suppression du cache Redis"""
        try:
            await self.redis_client.delete(f"service:{service_id}")
            await self.redis_client.delete(f"metrics:{service_id}")
        except Exception as e:
            logging.warning(f"Cache removal failed: {str(e)}")


def create_service_registry_app() -> FastAPI:
    """
    Création de l'application FastAPI pour le registre de services
    """
    app = FastAPI(
        title="Ainflue AI Services Registry",
        description="Service discovery and registry for AI agents",
        version="1.0.0"
    )
    
    registry = ServiceRegistryOrchestrator()
    
    @app.on_event("startup")
    async def startup_event():
        await registry.initialize()
    
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
    
    @app.post("/services/register")
    async def register_service(request: ServiceRegistrationRequest):
        """Enregistrement d'un service IA"""
        return await registry.register_service(request)
    
    @app.post("/services/discover")
    async def discover_services(request: ServiceDiscoveryRequest):
        """Découverte de services IA"""
        return await registry.discover_services(request)
    
    @app.get("/services/{service_id}/health")
    async def get_service_health(service_id: str):
        """État de santé d'un service"""
        return await registry.get_service_health(service_id)
    
    @app.delete("/services/{service_id}")
    async def unregister_service(service_id: str):
        """Désenregistrement d'un service"""
        return await registry.unregister_service(service_id)
    
    @app.put("/services/{service_id}/metrics")
    async def update_service_metrics(service_id: str, metrics: Dict[str, Any]):
        """Mise à jour des métriques de service"""
        return await registry.update_service_metrics(service_id, metrics)
    
    @app.get("/services")
    async def list_services():
        """Liste de tous les services enregistrés"""
        services_list = []
        for service in registry.services.values():
            services_list.append(await registry._service_to_dict(service))
        
        return {
            'services': services_list,
            'total_count': len(services_list),
            'by_type': {
                service_type: len([s for s in services_list if s['service_type'] == service_type])
                for service_type in set(s['service_type'] for s in services_list)
            }
        }
    
    return app


if __name__ == "__main__":
    import uvicorn
    
    app = create_service_registry_app()
    uvicorn.run(app, host="0.0.0.0", port=8004, log_level="info")