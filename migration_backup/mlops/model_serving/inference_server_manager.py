#!/usr/bin/env python3
"""
🚀 Inference Server Manager - Enterprise MLOps Platform
Lead Dev IA Expertise: Manager de serveurs d'inférence avec auto-scaling et load balancing

Créateur: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. Tous droits réservés.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
import threading
import time
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import psutil
import socket

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ServerStatus(Enum):
    """Status des serveurs d'inférence"""
    STARTING = "starting"
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    OVERLOADED = "overloaded"
    MAINTENANCE = "maintenance"
    STOPPED = "stopped"

class LoadBalancingStrategy(Enum):
    """Stratégies de load balancing"""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_RESPONSE_TIME = "least_response_time"
    RESOURCE_BASED = "resource_based"
    AI_OPTIMIZED = "ai_optimized"

class AutoScalingTrigger(Enum):
    """Déclencheurs d'auto-scaling"""
    CPU_UTILIZATION = "cpu_utilization"
    MEMORY_UTILIZATION = "memory_utilization"
    REQUEST_QUEUE_LENGTH = "request_queue_length"
    RESPONSE_TIME = "response_time"
    ERROR_RATE = "error_rate"
    CUSTOM_METRIC = "custom_metric"

@dataclass
class ServerConfig:
    """Configuration d'un serveur d'inférence"""
    server_id: str
    host: str
    port: int
    model_path: str
    model_type: str
    max_batch_size: int
    max_concurrent_requests: int
    memory_limit_mb: int
    cpu_cores: int
    gpu_memory_mb: Optional[int] = None
    environment_variables: Dict[str, str] = field(default_factory=dict)
    health_check_endpoint: str = "/health"
    inference_endpoint: str = "/predict"
    weight: float = 1.0
    tags: List[str] = field(default_factory=list)

@dataclass
class ServerMetrics:
    """Métriques d'un serveur d'inférence"""
    server_id: str
    timestamp: datetime
    cpu_utilization: float
    memory_utilization: float
    gpu_utilization: float
    active_connections: int
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_response_time: float
    current_queue_length: int
    throughput_rps: float
    error_rate: float
    status: ServerStatus

@dataclass
class InferenceRequest:
    """Requête d'inférence"""
    request_id: str
    model_type: str
    input_data: Any
    priority: int = 1
    timeout: float = 30.0
    callback: Optional[Callable] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class InferenceResponse:
    """Réponse d'inférence"""
    request_id: str
    result: Any
    server_id: str
    processing_time: float
    queue_time: float
    total_time: float
    status_code: int
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class InferenceServer:
    """Serveur d'inférence individuel"""
    
    def __init__(self, config: ServerConfig):
        self.config = config
        self.status = ServerStatus.STARTING
        self.metrics = ServerMetrics(
            server_id=config.server_id,
            timestamp=datetime.now(),
            cpu_utilization=0.0,
            memory_utilization=0.0,
            gpu_utilization=0.0,
            active_connections=0,
            total_requests=0,
            successful_requests=0,
            failed_requests=0,
            average_response_time=0.0,
            current_queue_length=0,
            throughput_rps=0.0,
            error_rate=0.0,
            status=ServerStatus.STARTING
        )
        self.request_queue = asyncio.Queue(maxsize=1000)
        self.active_requests: Dict[str, InferenceRequest] = {}
        self.response_times: List[float] = []
        self.model = None
        self.is_running = False
        self.executor = ThreadPoolExecutor(max_workers=config.max_concurrent_requests)
        
    async def start(self):
        """Démarre le serveur d'inférence"""
        try:
            logger.info(f"Démarrage serveur {self.config.server_id}")
            
            # Chargement du modèle
            await self._load_model()
            
            # Démarrage des workers
            self.is_running = True
            asyncio.create_task(self._request_processor())
            asyncio.create_task(self._metrics_collector())
            
            self.status = ServerStatus.HEALTHY
            logger.info(f"Serveur {self.config.server_id} démarré avec succès")
            
        except Exception as e:
            logger.error(f"Erreur démarrage serveur {self.config.server_id}: {e}")
            self.status = ServerStatus.UNHEALTHY
            raise
    
    async def stop(self):
        """Arrête le serveur d'inférence"""
        logger.info(f"Arrêt serveur {self.config.server_id}")
        self.is_running = False
        self.status = ServerStatus.STOPPED
        self.executor.shutdown(wait=True)
    
    async def _load_model(self):
        """Charge le modèle ML"""
        try:
            # Simulation du chargement de modèle
            # En production, ceci chargerait le modèle réel (TensorFlow, PyTorch, etc.)
            await asyncio.sleep(2)  # Simulation du temps de chargement
            self.model = f"model_{self.config.model_type}"
            logger.info(f"Modèle chargé: {self.config.model_path}")
        except Exception as e:
            logger.error(f"Erreur chargement modèle: {e}")
            raise
    
    async def _request_processor(self):
        """Processeur de requêtes d'inférence"""
        while self.is_running:
            try:
                # Récupération de la requête
                request = await asyncio.wait_for(
                    self.request_queue.get(), 
                    timeout=1.0
                )
                
                # Traitement de la requête
                asyncio.create_task(self._process_request(request))
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Erreur processeur requêtes: {e}")
    
    async def _process_request(self, request: InferenceRequest):
        """Traite une requête d'inférence"""
        start_time = time.time()
        self.active_requests[request.request_id] = request
        
        try:
            # Simulation du traitement d'inférence
            processing_start = time.time()
            
            # En production, ceci appellerait le modèle réel
            result = await self._run_inference(request.input_data)
            
            processing_time = time.time() - processing_start
            total_time = time.time() - start_time
            queue_time = processing_start - start_time
            
            # Création de la réponse
            response = InferenceResponse(
                request_id=request.request_id,
                result=result,
                server_id=self.config.server_id,
                processing_time=processing_time,
                queue_time=queue_time,
                total_time=total_time,
                status_code=200
            )
            
            # Mise à jour des métriques
            self.response_times.append(total_time)
            self.metrics.successful_requests += 1
            self.metrics.total_requests += 1
            
            # Callback si fourni
            if request.callback:
                await request.callback(response)
                
        except Exception as e:
            logger.error(f"Erreur traitement requête {request.request_id}: {e}")
            
            response = InferenceResponse(
                request_id=request.request_id,
                result=None,
                server_id=self.config.server_id,
                processing_time=0.0,
                queue_time=time.time() - start_time,
                total_time=time.time() - start_time,
                status_code=500,
                error_message=str(e)
            )
            
            self.metrics.failed_requests += 1
            self.metrics.total_requests += 1
            
        finally:
            # Nettoyage
            if request.request_id in self.active_requests:
                del self.active_requests[request.request_id]
    
    async def _run_inference(self, input_data: Any) -> Any:
        """Exécute l'inférence sur le modèle"""
        try:
            # Simulation d'inférence
            # En production, ceci appellerait le modèle réel
            await asyncio.sleep(np.random.uniform(0.01, 0.1))  # Simulation de traitement
            
            if self.config.model_type == "text":
                return {"output": f"Processed text: {input_data}"}
            elif self.config.model_type == "image":
                return {"classifications": ["cat", "dog"], "confidence": [0.8, 0.2]}
            elif self.config.model_type == "audio":
                return {"transcription": "Hello world", "confidence": 0.95}
            else:
                return {"result": "Generic result"}
                
        except Exception as e:
            logger.error(f"Erreur inférence: {e}")
            raise
    
    async def _metrics_collector(self):
        """Collecte les métriques du serveur"""
        while self.is_running:
            try:
                # Collecte des métriques système
                self.metrics.cpu_utilization = psutil.cpu_percent()
                self.metrics.memory_utilization = psutil.virtual_memory().percent
                self.metrics.active_connections = len(self.active_requests)
                self.metrics.current_queue_length = self.request_queue.qsize()
                
                # Calcul des métriques d'inférence
                if self.response_times:
                    self.metrics.average_response_time = np.mean(self.response_times[-100:])
                    self.metrics.throughput_rps = len(self.response_times[-60:])  # Dernière minute
                
                if self.metrics.total_requests > 0:
                    self.metrics.error_rate = (self.metrics.failed_requests / self.metrics.total_requests) * 100
                
                # Mise à jour du statut
                self._update_status()
                
                self.metrics.timestamp = datetime.now()
                
                # Nettoyage des anciennes métriques
                if len(self.response_times) > 1000:
                    self.response_times = self.response_times[-500:]
                
                await asyncio.sleep(5)  # Collecte toutes les 5 secondes
                
            except Exception as e:
                logger.error(f"Erreur collecte métriques: {e}")
                await asyncio.sleep(5)
    
    def _update_status(self):
        """Met à jour le statut du serveur"""
        if not self.is_running:
            self.status = ServerStatus.STOPPED
        elif self.metrics.error_rate > 10:
            self.status = ServerStatus.UNHEALTHY
        elif self.metrics.cpu_utilization > 90 or self.metrics.memory_utilization > 90:
            self.status = ServerStatus.OVERLOADED
        else:
            self.status = ServerStatus.HEALTHY
        
        self.metrics.status = self.status
    
    async def submit_request(self, request: InferenceRequest) -> bool:
        """Soumet une requête d'inférence"""
        try:
            if self.status != ServerStatus.HEALTHY:
                return False
            
            await self.request_queue.put(request)
            return True
            
        except asyncio.QueueFull:
            logger.warning(f"Queue pleine sur serveur {self.config.server_id}")
            return False
    
    def get_load_score(self) -> float:
        """Calcule un score de charge pour le load balancing"""
        cpu_score = self.metrics.cpu_utilization / 100.0
        memory_score = self.metrics.memory_utilization / 100.0
        queue_score = self.metrics.current_queue_length / 100.0
        response_time_score = min(self.metrics.average_response_time / 1.0, 1.0)
        
        # Score pondéré (plus le score est bas, moins le serveur est chargé)
        return (cpu_score * 0.3 + memory_score * 0.3 + queue_score * 0.2 + response_time_score * 0.2)

class LoadBalancer:
    """Load balancer intelligent pour serveurs d'inférence"""
    
    def __init__(self, strategy: LoadBalancingStrategy = LoadBalancingStrategy.AI_OPTIMIZED):
        self.strategy = strategy
        self.servers: Dict[str, InferenceServer] = {}
        self.current_index = 0
        self.request_history: List[Dict[str, Any]] = []
        
    def add_server(self, server: InferenceServer):
        """Ajoute un serveur au pool"""
        self.servers[server.config.server_id] = server
        logger.info(f"Serveur ajouté au pool: {server.config.server_id}")
    
    def remove_server(self, server_id: str):
        """Retire un serveur du pool"""
        if server_id in self.servers:
            del self.servers[server_id]
            logger.info(f"Serveur retiré du pool: {server_id}")
    
    def select_server(self, request: InferenceRequest) -> Optional[InferenceServer]:
        """Sélectionne le meilleur serveur pour une requête"""
        healthy_servers = [
            server for server in self.servers.values()
            if server.status == ServerStatus.HEALTHY
        ]
        
        if not healthy_servers:
            return None
        
        if self.strategy == LoadBalancingStrategy.ROUND_ROBIN:
            return self._round_robin_selection(healthy_servers)
        elif self.strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
            return self._least_connections_selection(healthy_servers)
        elif self.strategy == LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN:
            return self._weighted_round_robin_selection(healthy_servers)
        elif self.strategy == LoadBalancingStrategy.LEAST_RESPONSE_TIME:
            return self._least_response_time_selection(healthy_servers)
        elif self.strategy == LoadBalancingStrategy.RESOURCE_BASED:
            return self._resource_based_selection(healthy_servers)
        elif self.strategy == LoadBalancingStrategy.AI_OPTIMIZED:
            return self._ai_optimized_selection(healthy_servers, request)
        else:
            return healthy_servers[0]
    
    def _round_robin_selection(self, servers: List[InferenceServer]) -> InferenceServer:
        """Sélection round-robin"""
        server = servers[self.current_index % len(servers)]
        self.current_index += 1
        return server
    
    def _least_connections_selection(self, servers: List[InferenceServer]) -> InferenceServer:
        """Sélection par nombre de connexions minimal"""
        return min(servers, key=lambda s: s.metrics.active_connections)
    
    def _weighted_round_robin_selection(self, servers: List[InferenceServer]) -> InferenceServer:
        """Sélection round-robin pondérée"""
        weights = [server.config.weight for server in servers]
        total_weight = sum(weights)
        
        if total_weight == 0:
            return servers[0]
        
        # Sélection basée sur le poids
        selection_point = (self.current_index % total_weight)
        cumulative_weight = 0
        
        for i, server in enumerate(servers):
            cumulative_weight += server.config.weight
            if selection_point < cumulative_weight:
                self.current_index += 1
                return server
        
        return servers[0]
    
    def _least_response_time_selection(self, servers: List[InferenceServer]) -> InferenceServer:
        """Sélection par temps de réponse minimal"""
        return min(servers, key=lambda s: s.metrics.average_response_time)
    
    def _resource_based_selection(self, servers: List[InferenceServer]) -> InferenceServer:
        """Sélection basée sur les ressources disponibles"""
        return min(servers, key=lambda s: s.get_load_score())
    
    def _ai_optimized_selection(
        self, 
        servers: List[InferenceServer], 
        request: InferenceRequest
    ) -> InferenceServer:
        """Sélection optimisée par IA"""
        # Calcul du score pour chaque serveur
        scores = []
        
        for server in servers:
            # Facteurs multiples pour la sélection
            load_score = server.get_load_score()
            model_affinity = 1.0 if server.config.model_type == request.model_type else 0.8
            priority_factor = request.priority / 10.0
            
            # Score composite (plus bas = meilleur)
            composite_score = load_score / model_affinity / priority_factor
            scores.append((composite_score, server))
        
        # Sélection du serveur avec le meilleur score
        scores.sort(key=lambda x: x[0])
        return scores[0][1]

class AutoScaler:
    """Auto-scaler pour serveurs d'inférence"""
    
    def __init__(self, min_servers: int = 2, max_servers: int = 20):
        self.min_servers = min_servers
        self.max_servers = max_servers
        self.scaling_history: List[Dict[str, Any]] = []
        self.cooldown_period = timedelta(minutes=5)
        self.last_scaling_action = datetime.now() - self.cooldown_period
        
    def should_scale_up(self, servers: Dict[str, InferenceServer]) -> bool:
        """Détermine si un scale-up est nécessaire"""
        if len(servers) >= self.max_servers:
            return False
        
        if datetime.now() - self.last_scaling_action < self.cooldown_period:
            return False
        
        healthy_servers = [s for s in servers.values() if s.status == ServerStatus.HEALTHY]
        
        if not healthy_servers:
            return True
        
        # Critères de scale-up
        avg_cpu = sum(s.metrics.cpu_utilization for s in healthy_servers) / len(healthy_servers)
        avg_queue = sum(s.metrics.current_queue_length for s in healthy_servers) / len(healthy_servers)
        avg_response_time = sum(s.metrics.average_response_time for s in healthy_servers) / len(healthy_servers)
        
        return (
            avg_cpu > 80 or 
            avg_queue > 50 or 
            avg_response_time > 1.0
        )
    
    def should_scale_down(self, servers: Dict[str, InferenceServer]) -> bool:
        """Détermine si un scale-down est nécessaire"""
        if len(servers) <= self.min_servers:
            return False
        
        if datetime.now() - self.last_scaling_action < self.cooldown_period:
            return False
        
        healthy_servers = [s for s in servers.values() if s.status == ServerStatus.HEALTHY]
        
        if len(healthy_servers) <= self.min_servers:
            return False
        
        # Critères de scale-down
        avg_cpu = sum(s.metrics.cpu_utilization for s in healthy_servers) / len(healthy_servers)
        avg_queue = sum(s.metrics.current_queue_length for s in healthy_servers) / len(healthy_servers)
        
        return (
            avg_cpu < 30 and 
            avg_queue < 10 and 
            len(healthy_servers) > self.min_servers
        )
    
    def get_server_to_remove(self, servers: Dict[str, InferenceServer]) -> Optional[str]:
        """Sélectionne le serveur à retirer lors d'un scale-down"""
        healthy_servers = [s for s in servers.values() if s.status == ServerStatus.HEALTHY]
        
        if len(healthy_servers) <= self.min_servers:
            return None
        
        # Retire le serveur le moins utilisé
        least_used = min(healthy_servers, key=lambda s: s.metrics.active_connections)
        return least_used.config.server_id

class InferenceServerManager:
    """Manager principal des serveurs d'inférence avec auto-scaling et load balancing"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.servers: Dict[str, InferenceServer] = {}
        self.load_balancer = LoadBalancer(
            strategy=LoadBalancingStrategy(config.get('load_balancing_strategy', 'ai_optimized'))
        )
        self.auto_scaler = AutoScaler(
            min_servers=config.get('min_servers', 2),
            max_servers=config.get('max_servers', 20)
        )
        self.request_queue = asyncio.Queue()
        self.is_running = False
        self.metrics_history: List[Dict[str, Any]] = []
        
    async def start(self):
        """Démarre le manager de serveurs d'inférence"""
        try:
            logger.info("Démarrage du manager de serveurs d'inférence")
            
            # Démarrage des serveurs initiaux
            initial_servers = self.config.get('initial_servers', [])
            for server_config in initial_servers:
                await self.add_server(ServerConfig(**server_config))
            
            # Démarrage des tâches de fond
            self.is_running = True
            asyncio.create_task(self._request_dispatcher())
            asyncio.create_task(self._health_monitor())
            asyncio.create_task(self._auto_scaling_monitor())
            asyncio.create_task(self._metrics_aggregator())
            
            logger.info("Manager de serveurs d'inférence démarré avec succès")
            
        except Exception as e:
            logger.error(f"Erreur démarrage manager: {e}")
            raise
    
    async def stop(self):
        """Arrête le manager et tous les serveurs"""
        logger.info("Arrêt du manager de serveurs d'inférence")
        
        self.is_running = False
        
        # Arrêt de tous les serveurs
        for server in self.servers.values():
            await server.stop()
        
        self.servers.clear()
        logger.info("Manager arrêté")
    
    async def add_server(self, config: ServerConfig) -> InferenceServer:
        """Ajoute un nouveau serveur d'inférence"""
        try:
            server = InferenceServer(config)
            await server.start()
            
            self.servers[config.server_id] = server
            self.load_balancer.add_server(server)
            
            logger.info(f"Serveur ajouté: {config.server_id}")
            return server
            
        except Exception as e:
            logger.error(f"Erreur ajout serveur {config.server_id}: {e}")
            raise
    
    async def remove_server(self, server_id: str):
        """Retire un serveur d'inférence"""
        if server_id in self.servers:
            server = self.servers[server_id]
            await server.stop()
            
            del self.servers[server_id]
            self.load_balancer.remove_server(server_id)
            
            logger.info(f"Serveur retiré: {server_id}")
    
    async def submit_inference_request(self, request: InferenceRequest) -> InferenceResponse:
        """Soumet une requête d'inférence"""
        try:
            # Sélection du serveur optimal
            server = self.load_balancer.select_server(request)
            
            if not server:
                raise Exception("Aucun serveur disponible")
            
            # Soumission de la requête
            success = await server.submit_request(request)
            
            if not success:
                raise Exception(f"Impossible de soumettre la requête au serveur {server.config.server_id}")
            
            # Attente de la réponse (simulée)
            # En production, ceci utiliserait un mécanisme de callback ou de queue
            await asyncio.sleep(0.1)
            
            # Création de la réponse simulée
            response = InferenceResponse(
                request_id=request.request_id,
                result={"status": "processed"},
                server_id=server.config.server_id,
                processing_time=0.05,
                queue_time=0.02,
                total_time=0.07,
                status_code=200
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Erreur traitement requête {request.request_id}: {e}")
            
            return InferenceResponse(
                request_id=request.request_id,
                result=None,
                server_id="unknown",
                processing_time=0.0,
                queue_time=0.0,
                total_time=0.0,
                status_code=500,
                error_message=str(e)
            )
    
    async def _request_dispatcher(self):
        """Dispatcher des requêtes d'inférence"""
        while self.is_running:
            try:
                # En production, ceci récupérerait les requêtes d'une queue externe
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Erreur dispatcher requêtes: {e}")
    
    async def _health_monitor(self):
        """Monitor de santé des serveurs"""
        while self.is_running:
            try:
                unhealthy_servers = []
                
                for server_id, server in self.servers.items():
                    if server.status in [ServerStatus.UNHEALTHY, ServerStatus.STOPPED]:
                        unhealthy_servers.append(server_id)
                
                # Restart des serveurs non sains
                for server_id in unhealthy_servers:
                    logger.warning(f"Redémarrage serveur non sain: {server_id}")
                    server = self.servers[server_id]
                    try:
                        await server.stop()
                        await server.start()
                    except Exception as e:
                        logger.error(f"Erreur redémarrage {server_id}: {e}")
                
                await asyncio.sleep(30)  # Vérification toutes les 30 secondes
                
            except Exception as e:
                logger.error(f"Erreur monitor santé: {e}")
                await asyncio.sleep(30)
    
    async def _auto_scaling_monitor(self):
        """Monitor d'auto-scaling"""
        while self.is_running:
            try:
                # Vérification scale-up
                if self.auto_scaler.should_scale_up(self.servers):
                    await self._scale_up()
                
                # Vérification scale-down
                elif self.auto_scaler.should_scale_down(self.servers):
                    await self._scale_down()
                
                await asyncio.sleep(60)  # Vérification toutes les minutes
                
            except Exception as e:
                logger.error(f"Erreur monitor auto-scaling: {e}")
                await asyncio.sleep(60)
    
    async def _scale_up(self):
        """Exécute un scale-up"""
        try:
            # Configuration du nouveau serveur
            server_id = f"server-{uuid.uuid4().hex[:8]}"
            port = 8080 + len(self.servers)
            
            config = ServerConfig(
                server_id=server_id,
                host="localhost",
                port=port,
                model_path=f"/models/default",
                model_type="general",
                max_batch_size=32,
                max_concurrent_requests=10,
                memory_limit_mb=2048,
                cpu_cores=2
            )
            
            await self.add_server(config)
            self.auto_scaler.last_scaling_action = datetime.now()
            
            logger.info(f"Scale-up exécuté: nouveau serveur {server_id}")
            
        except Exception as e:
            logger.error(f"Erreur scale-up: {e}")
    
    async def _scale_down(self):
        """Exécute un scale-down"""
        try:
            server_to_remove = self.auto_scaler.get_server_to_remove(self.servers)
            
            if server_to_remove:
                await self.remove_server(server_to_remove)
                self.auto_scaler.last_scaling_action = datetime.now()
                
                logger.info(f"Scale-down exécuté: serveur retiré {server_to_remove}")
            
        except Exception as e:
            logger.error(f"Erreur scale-down: {e}")
    
    async def _metrics_aggregator(self):
        """Agrégateur de métriques globales"""
        while self.is_running:
            try:
                if not self.servers:
                    await asyncio.sleep(10)
                    continue
                
                # Agrégation des métriques
                total_requests = sum(s.metrics.total_requests for s in self.servers.values())
                total_successful = sum(s.metrics.successful_requests for s in self.servers.values())
                total_failed = sum(s.metrics.failed_requests for s in self.servers.values())
                avg_response_time = np.mean([s.metrics.average_response_time for s in self.servers.values()])
                total_throughput = sum(s.metrics.throughput_rps for s in self.servers.values())
                
                global_metrics = {
                    'timestamp': datetime.now().isoformat(),
                    'total_servers': len(self.servers),
                    'healthy_servers': len([s for s in self.servers.values() if s.status == ServerStatus.HEALTHY]),
                    'total_requests': total_requests,
                    'successful_requests': total_successful,
                    'failed_requests': total_failed,
                    'success_rate': (total_successful / total_requests * 100) if total_requests > 0 else 0,
                    'average_response_time': avg_response_time,
                    'total_throughput_rps': total_throughput
                }
                
                self.metrics_history.append(global_metrics)
                
                # Nettoyage de l'historique
                if len(self.metrics_history) > 1000:
                    self.metrics_history = self.metrics_history[-500:]
                
                await asyncio.sleep(10)  # Agrégation toutes les 10 secondes
                
            except Exception as e:
                logger.error(f"Erreur agrégation métriques: {e}")
                await asyncio.sleep(10)
    
    def get_status(self) -> Dict[str, Any]:
        """Récupère le statut global du manager"""
        if not self.servers:
            return {
                'status': 'no_servers',
                'total_servers': 0,
                'healthy_servers': 0
            }
        
        healthy_servers = [s for s in self.servers.values() if s.status == ServerStatus.HEALTHY]
        
        return {
            'status': 'healthy' if healthy_servers else 'unhealthy',
            'total_servers': len(self.servers),
            'healthy_servers': len(healthy_servers),
            'load_balancing_strategy': self.load_balancer.strategy.value,
            'auto_scaling': {
                'min_servers': self.auto_scaler.min_servers,
                'max_servers': self.auto_scaler.max_servers,
                'last_scaling_action': self.auto_scaler.last_scaling_action.isoformat()
            },
            'servers': {
                server_id: {
                    'status': server.status.value,
                    'cpu_utilization': server.metrics.cpu_utilization,
                    'memory_utilization': server.metrics.memory_utilization,
                    'active_connections': server.metrics.active_connections,
                    'total_requests': server.metrics.total_requests,
                    'error_rate': server.metrics.error_rate
                }
                for server_id, server in self.servers.items()
            }
        }

# Factory pour la création du manager
def create_inference_server_manager(config: Dict[str, Any]) -> InferenceServerManager:
    """Factory pour créer un manager de serveurs d'inférence configuré"""
    return InferenceServerManager(config)

# Exemple d'utilisation
async def main():
    """Exemple d'utilisation du manager de serveurs d'inférence"""
    
    # Configuration
    config = {
        'load_balancing_strategy': 'ai_optimized',
        'min_servers': 2,
        'max_servers': 10,
        'initial_servers': [
            {
                'server_id': 'server-1',
                'host': 'localhost',
                'port': 8081,
                'model_path': '/models/text-model',
                'model_type': 'text',
                'max_batch_size': 32,
                'max_concurrent_requests': 10,
                'memory_limit_mb': 2048,
                'cpu_cores': 2
            },
            {
                'server_id': 'server-2',
                'host': 'localhost',
                'port': 8082,
                'model_path': '/models/image-model',
                'model_type': 'image',
                'max_batch_size': 16,
                'max_concurrent_requests': 5,
                'memory_limit_mb': 4096,
                'cpu_cores': 4
            }
        ]
    }
    
    # Création du manager
    manager = create_inference_server_manager(config)
    
    try:
        # Démarrage du manager
        await manager.start()
        
        # Simulation de requêtes
        for i in range(5):
            request = InferenceRequest(
                request_id=f"req-{i}",
                model_type="text",
                input_data=f"Test input {i}",
                priority=1
            )
            
            response = await manager.submit_inference_request(request)
            print(f"Réponse {i}: {response.status_code} - {response.server_id}")
        
        # Affichage du statut
        status = manager.get_status()
        print(f"Statut manager: {status}")
        
        # Attente pour observer l'auto-scaling
        await asyncio.sleep(30)
        
    finally:
        # Arrêt du manager
        await manager.stop()

if __name__ == "__main__":
    asyncio.run(main())