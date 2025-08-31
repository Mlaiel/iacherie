"""🚀 REST Client & Service Registry - IA Influencer Agent Platform Enterprise
=========================================================================
Module: backend/platform_core/communication/rest_client.py
Author: Fahed Mlaiel (mlaiel@live.de)
=========================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 CLIENT REST & REGISTRE DE SERVICES
Client HTTP intelligent avec découverte de services automatique
- Pool de connexions optimisé avec circuit breaker
- Load balancing intelligent et failover
- Retry automatique avec backoff exponentiel
- Authentification centralisée et cache des tokens
"""
import asyncio
import json
import logging
import time
import uuid
from typing import Dict, List, Optional, Any, Union, Callable, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import weakref
import urllib.parse

import aiohttp
import aioredis
from pydantic import BaseModel, Field, validator
import jwt
from cryptography.fernet import Fernet

# Configuration
logger = logging.getLogger(__name__)

class ServiceStatus(Enum):
    """États des services"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    MAINTENANCE = "maintenance"
    UNKNOWN = "unknown"

class RequestMethod(Enum):
    """Méthodes HTTP supportées"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"

@dataclass
class ServiceEndpoint:
    """Définition d'un endpoint de service"""
    service_id: str
    name: str
    url: str
    health_check_url: Optional[str] = None
    weight: float = 1.0  # Pour load balancing
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    last_health_check: Optional[datetime] = None
    status: ServiceStatus = ServiceStatus.UNKNOWN
    response_time_avg: float = 0.0
    error_rate: float = 0.0
    version: str = "1.0.0"
    
    def is_available(self) -> bool:
        """Vérifie si le service est disponible"""
        return self.status in [ServiceStatus.HEALTHY, ServiceStatus.DEGRADED]

@dataclass 
class CircuitBreakerState:
    """État du circuit breaker"""
    failures: int = 0
    last_failure_time: Optional[datetime] = None
    state: str = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    next_attempt_time: Optional[datetime] = None
    success_count: int = 0

@dataclass
class RequestStats:
    """Statistiques de requêtes"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_response_time: float = 0.0
    last_request_time: Optional[datetime] = None
    
    @property
    def success_rate(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return self.successful_requests / self.total_requests
        
    @property
    def average_response_time(self) -> float:
        if self.successful_requests == 0:
            return 0.0
        return self.total_response_time / self.successful_requests

class ServiceRegistry:
    """Registre de services avec découverte automatique"""
    
    def __init__(self, redis_client: Optional[aioredis.Redis] = None):
        self.services: Dict[str, List[ServiceEndpoint]] = {}
        self.circuit_breakers: Dict[str, CircuitBreakerState] = {}
        self.stats: Dict[str, RequestStats] = {}
        self.redis_client = redis_client
        self.health_check_interval = 30  # secondes
        self.circuit_breaker_threshold = 5  # failures avant ouverture
        self.circuit_breaker_timeout = 60  # secondes
        self._health_check_task: Optional[asyncio.Task] = None
        
    async def start(self):
        """Démarre le registre de services"""
        logger.info("Démarrage du registre de services")
        self._health_check_task = asyncio.create_task(self._health_check_loop())
        
    async def stop(self):
        """Arrête le registre de services"""
        logger.info("Arrêt du registre de services")
        if self._health_check_task:
            self._health_check_task.cancel()
            
    async def register_service(self, endpoint: ServiceEndpoint):
        """Enregistre un nouveau service"""
        service_name = endpoint.name
        
        if service_name not in self.services:
            self.services[service_name] = []
            
        # Éviter les doublons
        existing = next((s for s in self.services[service_name] 
                        if s.service_id == endpoint.service_id), None)
        if existing:
            # Mettre à jour l'endpoint existant
            existing.url = endpoint.url
            existing.weight = endpoint.weight
            existing.tags = endpoint.tags
            existing.metadata = endpoint.metadata
            existing.version = endpoint.version
        else:
            self.services[service_name].append(endpoint)
            
        # Initialiser les statistiques
        if endpoint.service_id not in self.stats:
            self.stats[endpoint.service_id] = RequestStats()
            self.circuit_breakers[endpoint.service_id] = CircuitBreakerState()
            
        # Persister dans Redis si disponible
        if self.redis_client:
            await self._persist_service(endpoint)
            
        logger.info(f"Service enregistré: {service_name} ({endpoint.service_id})")
        
    async def unregister_service(self, service_name: str, service_id: str):
        """Désenregistre un service"""
        if service_name in self.services:
            self.services[service_name] = [
                s for s in self.services[service_name] 
                if s.service_id != service_id
            ]
            if not self.services[service_name]:
                del self.services[service_name]
                
        # Nettoyer les statistiques
        if service_id in self.stats:
            del self.stats[service_id]
        if service_id in self.circuit_breakers:
            del self.circuit_breakers[service_id]
            
        logger.info(f"Service désenregistré: {service_name} ({service_id})")
        
    async def discover_service(self, service_name: str, 
                             tags: Optional[List[str]] = None) -> Optional[ServiceEndpoint]:
        """Découvre un service disponible avec load balancing"""
        if service_name not in self.services:
            return None
            
        candidates = []
        for endpoint in self.services[service_name]:
            # Vérifier les tags si spécifiés
            if tags and not any(tag in endpoint.tags for tag in tags):
                continue
                
            # Vérifier la disponibilité
            if not endpoint.is_available():
                continue
                
            # Vérifier le circuit breaker
            circuit_breaker = self.circuit_breakers.get(endpoint.service_id)
            if circuit_breaker and not self._is_circuit_breaker_closed(circuit_breaker):
                continue
                
            candidates.append(endpoint)
            
        if not candidates:
            return None
            
        # Load balancing basé sur le poids et les performances
        return self._select_best_endpoint(candidates)
        
    def _select_best_endpoint(self, candidates: List[ServiceEndpoint]) -> ServiceEndpoint:
        """Sélectionne le meilleur endpoint selon l'algorithme de load balancing"""
        if len(candidates) == 1:
            return candidates[0]
            
        # Calculer les scores basés sur poids, temps de réponse et taux d'erreur
        scored_candidates = []
        for endpoint in candidates:
            stats = self.stats.get(endpoint.service_id, RequestStats())
            
            # Score = poids * (1 - erreur_rate) * (1 / temps_réponse_normalisé)
            error_penalty = 1 - min(stats.success_rate, 1.0)
            response_time_penalty = min(endpoint.response_time_avg / 1000, 1.0)  # normaliser à 1s
            
            score = endpoint.weight * (1 - error_penalty) * (1 - response_time_penalty)
            scored_candidates.append((score, endpoint))
            
        # Retourner le candidat avec le meilleur score
        scored_candidates.sort(key=lambda x: x[0], reverse=True)
        return scored_candidates[0][1]
        
    def _is_circuit_breaker_closed(self, circuit_breaker: CircuitBreakerState) -> bool:
        """Vérifie si le circuit breaker permet les requêtes"""
        now = datetime.utcnow()
        
        if circuit_breaker.state == "CLOSED":
            return True
        elif circuit_breaker.state == "OPEN":
            if (circuit_breaker.next_attempt_time and 
                now >= circuit_breaker.next_attempt_time):
                circuit_breaker.state = "HALF_OPEN"
                circuit_breaker.success_count = 0
                return True
            return False
        elif circuit_breaker.state == "HALF_OPEN":
            return True
            
        return False
        
    async def _health_check_loop(self):
        """Boucle de vérification de santé des services"""
        while True:
            try:
                await asyncio.sleep(self.health_check_interval)
                await self._check_all_services_health()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Erreur dans la vérification de santé: {e}")
                
    async def _check_all_services_health(self):
        """Vérifie la santé de tous les services"""
        health_check_tasks = []
        
        for service_name, endpoints in self.services.items():
            for endpoint in endpoints:
                if endpoint.health_check_url:
                    task = asyncio.create_task(
                        self._check_service_health(endpoint)
                    )
                    health_check_tasks.append(task)
                    
        if health_check_tasks:
            await asyncio.gather(*health_check_tasks, return_exceptions=True)
            
    async def _check_service_health(self, endpoint: ServiceEndpoint):
        """Vérifie la santé d'un service spécifique"""
        try:
            start_time = time.time()
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    endpoint.health_check_url,
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        endpoint.status = ServiceStatus.HEALTHY
                        endpoint.response_time_avg = (
                            endpoint.response_time_avg * 0.9 + response_time * 0.1
                        )
                    else:
                        endpoint.status = ServiceStatus.DEGRADED
                        
        except Exception as e:
            logger.warning(f"Health check failed for {endpoint.service_id}: {e}")
            endpoint.status = ServiceStatus.UNHEALTHY
            
        endpoint.last_health_check = datetime.utcnow()
        
    async def _persist_service(self, endpoint: ServiceEndpoint):
        """Persiste les informations du service dans Redis"""
        if not self.redis_client:
            return
            
        key = f"service_registry:{endpoint.name}:{endpoint.service_id}"
        data = {
            "service_id": endpoint.service_id,
            "name": endpoint.name,
            "url": endpoint.url,
            "health_check_url": endpoint.health_check_url,
            "weight": endpoint.weight,
            "tags": endpoint.tags,
            "metadata": endpoint.metadata,
            "status": endpoint.status.value,
            "version": endpoint.version,
            "registered_at": datetime.utcnow().isoformat()
        }
        
        await self.redis_client.set(key, json.dumps(data), ex=3600)  # TTL 1h
        
    def get_service_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques des services"""
        return {
            "total_services": sum(len(endpoints) for endpoints in self.services.values()),
            "services_by_status": {
                status.value: sum(
                    1 for endpoints in self.services.values()
                    for endpoint in endpoints
                    if endpoint.status == status
                )
                for status in ServiceStatus
            },
            "circuit_breakers": {
                service_id: {
                    "state": cb.state,
                    "failures": cb.failures,
                    "last_failure": cb.last_failure_time.isoformat() if cb.last_failure_time else None
                }
                for service_id, cb in self.circuit_breakers.items()
            }
        }

class RestClient:
    """Client REST intelligent avec fonctionnalités avancées"""
    
    def __init__(self, service_registry: ServiceRegistry, 
                 default_timeout: int = 30, 
                 max_retries: int = 3,
                 base_headers: Optional[Dict[str, str]] = None):
        self.service_registry = service_registry
        self.default_timeout = default_timeout
        self.max_retries = max_retries
        self.base_headers = base_headers or {}
        self.session: Optional[aiohttp.ClientSession] = None
        self.auth_tokens: Dict[str, str] = {}  # service_name -> token
        self.token_expiry: Dict[str, datetime] = {}
        
    async def start(self):
        """Démarre le client REST"""
        connector = aiohttp.TCPConnector(
            limit=100,  # Pool de connexions
            limit_per_host=30,
            keepalive_timeout=30,
            enable_cleanup_closed=True
        )
        
        timeout = aiohttp.ClientTimeout(total=self.default_timeout)
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers=self.base_headers
        )
        
        logger.info("RestClient démarré")
        
    async def stop(self):
        """Arrête le client REST"""
        if self.session:
            await self.session.close()
        logger.info("RestClient arrêté")
        
    async def request(self, 
                     service_name: str,
                     method: RequestMethod,
                     path: str,
                     data: Optional[Dict[str, Any]] = None,
                     json_data: Optional[Dict[str, Any]] = None,
                     headers: Optional[Dict[str, str]] = None,
                     params: Optional[Dict[str, Any]] = None,
                     timeout: Optional[int] = None,
                     auth_required: bool = False,
                     tags: Optional[List[str]] = None) -> Tuple[int, Dict[str, Any]]:
        """Effectue une requête HTTP vers un service"""
        
        # Découvrir le service
        endpoint = await self.service_registry.discover_service(service_name, tags)
        if not endpoint:
            raise ValueError(f"Service non disponible: {service_name}")
            
        # Construire l'URL complète
        base_url = endpoint.url.rstrip('/')
        full_path = path.lstrip('/')
        url = f"{base_url}/{full_path}"
        
        # Préparer les headers
        request_headers = self.base_headers.copy()
        if headers:
            request_headers.update(headers)
            
        # Gestion de l'authentification
        if auth_required:
            token = await self._get_auth_token(service_name, endpoint)
            if token:
                request_headers["Authorization"] = f"Bearer {token}"
                
        # Préparer les données
        request_kwargs = {
            "method": method.value,
            "url": url,
            "headers": request_headers,
            "timeout": aiohttp.ClientTimeout(total=timeout or self.default_timeout)
        }
        
        if params:
            request_kwargs["params"] = params
        if json_data:
            request_kwargs["json"] = json_data
        elif data:
            request_kwargs["data"] = data
            
        # Effectuer la requête avec retry
        return await self._execute_request_with_retry(endpoint, **request_kwargs)
        
    async def get(self, service_name: str, path: str, **kwargs) -> Tuple[int, Dict[str, Any]]:
        """Requête GET"""
        return await self.request(service_name, RequestMethod.GET, path, **kwargs)
        
    async def post(self, service_name: str, path: str, **kwargs) -> Tuple[int, Dict[str, Any]]:
        """Requête POST"""
        return await self.request(service_name, RequestMethod.POST, path, **kwargs)
        
    async def put(self, service_name: str, path: str, **kwargs) -> Tuple[int, Dict[str, Any]]:
        """Requête PUT"""
        return await self.request(service_name, RequestMethod.PUT, path, **kwargs)
        
    async def patch(self, service_name: str, path: str, **kwargs) -> Tuple[int, Dict[str, Any]]:
        """Requête PATCH"""
        return await self.request(service_name, RequestMethod.PATCH, path, **kwargs)
        
    async def delete(self, service_name: str, path: str, **kwargs) -> Tuple[int, Dict[str, Any]]:
        """Requête DELETE"""
        return await self.request(service_name, RequestMethod.DELETE, path, **kwargs)
        
    async def _execute_request_with_retry(self, endpoint: ServiceEndpoint, **request_kwargs) -> Tuple[int, Dict[str, Any]]:
        """Exécute une requête avec retry automatique"""
        circuit_breaker = self.service_registry.circuit_breakers.get(endpoint.service_id)
        stats = self.service_registry.stats.get(endpoint.service_id)
        
        if not circuit_breaker or not stats:
            raise ValueError(f"Service non initialisé: {endpoint.service_id}")
            
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                start_time = time.time()
                
                async with self.session.request(**request_kwargs) as response:
                    response_time = time.time() - start_time
                    
                    # Mettre à jour les statistiques
                    stats.total_requests += 1
                    stats.total_response_time += response_time
                    stats.last_request_time = datetime.utcnow()
                    
                    if response.status < 500:  # Succès ou erreur client
                        stats.successful_requests += 1
                        self._reset_circuit_breaker(circuit_breaker)
                        
                        try:
                            response_data = await response.json()
                        except:
                            response_data = {"text": await response.text()}
                            
                        return response.status, response_data
                    else:
                        # Erreur serveur
                        stats.failed_requests += 1
                        self._record_failure(circuit_breaker)
                        
                        if attempt < self.max_retries:
                            await asyncio.sleep(2 ** attempt)  # Backoff exponentiel
                            continue
                        else:
                            response_data = {"error": f"Server error: {response.status}"}
                            return response.status, response_data
                            
            except Exception as e:
                last_exception = e
                stats.total_requests += 1
                stats.failed_requests += 1
                self._record_failure(circuit_breaker)
                
                if attempt < self.max_retries:
                    logger.warning(f"Retry {attempt + 1}/{self.max_retries} for {request_kwargs['url']}: {e}")
                    await asyncio.sleep(2 ** attempt)
                else:
                    logger.error(f"Request failed after {self.max_retries} retries: {e}")
                    
        # Toutes les tentatives ont échoué
        if last_exception:
            raise last_exception
        else:
            raise Exception("Request failed after all retries")
            
    def _reset_circuit_breaker(self, circuit_breaker: CircuitBreakerState):
        """Remet à zéro le circuit breaker après un succès"""
        if circuit_breaker.state == "HALF_OPEN":
            circuit_breaker.success_count += 1
            if circuit_breaker.success_count >= 3:  # 3 succès pour fermer
                circuit_breaker.state = "CLOSED"
                circuit_breaker.failures = 0
        elif circuit_breaker.state == "CLOSED":
            circuit_breaker.failures = max(0, circuit_breaker.failures - 1)
            
    def _record_failure(self, circuit_breaker: CircuitBreakerState):
        """Enregistre un échec et met à jour le circuit breaker"""
        circuit_breaker.failures += 1
        circuit_breaker.last_failure_time = datetime.utcnow()
        
        if (circuit_breaker.state == "CLOSED" and 
            circuit_breaker.failures >= self.service_registry.circuit_breaker_threshold):
            circuit_breaker.state = "OPEN"
            circuit_breaker.next_attempt_time = (
                datetime.utcnow() + timedelta(seconds=self.service_registry.circuit_breaker_timeout)
            )
            logger.warning(f"Circuit breaker opened for service")
            
    async def _get_auth_token(self, service_name: str, endpoint: ServiceEndpoint) -> Optional[str]:
        """Obtient un token d'authentification pour le service"""
        # Vérifier si on a déjà un token valide
        if service_name in self.auth_tokens:
            expiry = self.token_expiry.get(service_name)
            if expiry and datetime.utcnow() < expiry:
                return self.auth_tokens[service_name]
                
        # Demander un nouveau token (implémentation simplifiée)
        try:
            auth_url = endpoint.metadata.get("auth_url")
            if not auth_url:
                return None
                
            auth_data = {
                "client_id": endpoint.metadata.get("client_id"),
                "client_secret": endpoint.metadata.get("client_secret"),
                "grant_type": "client_credentials"
            }
            
            async with self.session.post(auth_url, json=auth_data) as response:
                if response.status == 200:
                    token_data = await response.json()
                    access_token = token_data.get("access_token")
                    expires_in = token_data.get("expires_in", 3600)
                    
                    if access_token:
                        self.auth_tokens[service_name] = access_token
                        self.token_expiry[service_name] = (
                            datetime.utcnow() + timedelta(seconds=expires_in - 60)
                        )
                        return access_token
                        
        except Exception as e:
            logger.error(f"Erreur lors de l'obtention du token pour {service_name}: {e}")
            
        return None
        
    def get_client_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques du client"""
        return {
            "auth_tokens_cached": len(self.auth_tokens),
            "session_active": self.session is not None,
            "default_timeout": self.default_timeout,
            "max_retries": self.max_retries
        }