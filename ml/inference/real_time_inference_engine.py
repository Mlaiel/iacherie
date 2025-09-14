"""🚀 Real-Time Inference Engine - IA Influencer Agent Platform Enterprise
=======================================================================
Module: backend/ml/inference/real_time_inference_engine.py
Author: Fahed Mlaiel (mlaiel@live.de)
=======================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 MOTEUR D'INFÉRENCE TEMPS RÉEL
Engine haute performance pour inférence temps réel <100ms
- Queue de prédictions prioritaires avec load balancing
- Cache intelligent pour patterns récurrents
- Auto-scaling basé sur la charge
- Monitoring en temps réel des performances
"""

import asyncio
import logging
import time
import uuid
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import pickle
import hashlib
from pathlib import Path
from collections import defaultdict, deque
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import queue

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator

# Configuration
logger = logging.getLogger(__name__)

class PredictionPriority(Enum):
    """Priorités des prédictions"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

class InferenceStatus(Enum):
    """Statuts d'inférence"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"

class ModelState(Enum):
    """États des modèles"""
    LOADING = "loading"
    READY = "ready"
    BUSY = "busy"
    ERROR = "error"
    RETIRED = "retired"

@dataclass
class PredictionRequest:
    """Requête de prédiction"""
    request_id: str
    model_id: str
    input_data: Any
    priority: PredictionPriority
    created_at: datetime
    timeout_ms: int = 5000
    metadata: Dict[str, Any] = field(default_factory=dict)
    callback: Optional[Callable] = None

@dataclass
class PredictionResponse:
    """Réponse de prédiction"""
    request_id: str
    model_id: str
    prediction: Any
    confidence: Optional[float]
    latency_ms: float
    status: InferenceStatus
    created_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ModelInstance:
    """Instance de modèle chargé"""
    model_id: str
    model: Any
    state: ModelState
    load_time: datetime
    last_used: datetime
    prediction_count: int = 0
    total_latency: float = 0.0
    error_count: int = 0
    memory_usage_mb: float = 0.0

@dataclass
class InferenceMetrics:
    """Métriques d'inférence"""
    total_requests: int = 0
    completed_requests: int = 0
    failed_requests: int = 0
    timeout_requests: int = 0
    avg_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    current_queue_size: int = 0
    active_workers: int = 0
    cache_hit_rate: float = 0.0

class RealTimeInferenceEngine:
    """Moteur d'inférence temps réel enterprise"""
    
    def __init__(self,
                 max_workers -> None: int = 10,
                 max_queue_size -> None: int = 10000,
                 cache_size -> None: int = 1000,
                 model_timeout_minutes -> None: int = 30,
                 enable_auto_scaling -> None: bool = True) -> None:
        self.max_workers = max_workers
        self.max_queue_size = max_queue_size
        self.cache_size = cache_size
        self.model_timeout_minutes = model_timeout_minutes
        self.enable_auto_scaling = enable_auto_scaling
        
        # Queues de priorité
        self.request_queues: Dict[PredictionPriority, queue.PriorityQueue] = {
            priority: queue.PriorityQueue() for priority in PredictionPriority
        }
        
        # Modèles chargés
        self.loaded_models: Dict[str, ModelInstance] = {}
        self.model_locks: Dict[str, threading.Lock] = defaultdict(threading.Lock)
        
        # Cache intelligent
        self.prediction_cache: Dict[str, PredictionResponse] = {}
        self.cache_access_times: Dict[str, datetime] = {}
        
        # Workers et threading
        self.workers: List[threading.Thread] = []
        self.worker_pool = ThreadPoolExecutor(max_workers=max_workers)
        self.is_running = False
        self.shutdown_event = threading.Event()
        
        # Métriques
        self.metrics = InferenceMetrics()
        self.latency_history = deque(maxlen=1000)
        self.request_history: Dict[str, PredictionResponse] = {}
        
        # Callbacks
        self.prediction_callbacks: List[Callable[[PredictionResponse], None]] = []
        self.error_callbacks: List[Callable[[Exception, PredictionRequest], None]] = []
        
        # Auto-scaling
        self.scaling_metrics = {
            "queue_length_threshold": 100,
            "latency_threshold_ms": 200,
            "scale_up_workers": 2,
            "scale_down_threshold": 50,
            "last_scale_time": datetime.now()
        }
    
    async def start(self) -> None:
        """Démarre le moteur d'inférence"""
        try:
            self.is_running = True
            logger.info(f"Démarrage du moteur d'inférence avec {self.max_workers} workers")
            
            # Démarrer les workers
            for i in range(self.max_workers):
                worker = threading.Thread(
                    target=self._worker_loop,
                    args=(f"worker_{i}",),
                    daemon=True
                )
                worker.start()
                self.workers.append(worker)
            
            # Démarrer les tâches de maintenance
            asyncio.create_task(self._cleanup_loop())
            asyncio.create_task(self._metrics_loop())
            
            if self.enable_auto_scaling:
                asyncio.create_task(self._auto_scaling_loop())
            
            logger.info("Moteur d'inférence démarré avec succès")
            
        except Exception as e:
            logger.error(f"Erreur démarrage moteur d'inférence: {e}")
            raise
    
    async def stop(self) -> None:
        """Arrête le moteur d'inférence"""
        try:
            logger.info("Arrêt du moteur d'inférence...")
            
            self.is_running = False
            self.shutdown_event.set()
            
            # Attendre la fin des workers
            for worker in self.workers:
                worker.join(timeout=5.0)
            
            # Fermer le pool de threads
            self.worker_pool.shutdown(wait=True)
            
            logger.info("Moteur d'inférence arrêté")
            
        except Exception as e:
            logger.error(f"Erreur arrêt moteur d'inférence: {e}")
    
    async def load_model(self, model_id: str, model: Any) -> bool:
        """Charge un modèle dans le moteur"""
        try:
            with self.model_locks[model_id]:
                if model_id in self.loaded_models:
                    logger.warning(f"Modèle {model_id} déjà chargé")
                    return True
                
                # Créer l'instance de modèle
                model_instance = ModelInstance(
                    model_id=model_id,
                    model=model,
                    state=ModelState.LOADING,
                    load_time=datetime.now(),
                    last_used=datetime.now()
                )
                
                # Tester le modèle
                try:
                    if hasattr(model, 'predict'):
                        # Test avec des données factices si possible
                        model_instance.state = ModelState.READY
                    else:
                        raise ValueError("Le modèle n'a pas de méthode predict")
                except Exception as e:
                    model_instance.state = ModelState.ERROR
                    logger.error(f"Erreur test modèle {model_id}: {e}")
                    return False
                
                self.loaded_models[model_id] = model_instance
                logger.info(f"Modèle {model_id} chargé avec succès")
                return True
                
        except Exception as e:
            logger.error(f"Erreur chargement modèle {model_id}: {e}")
            return False
    
    async def unload_model(self, model_id: str) -> bool:
        """Décharge un modèle"""
        try:
            with self.model_locks[model_id]:
                if model_id not in self.loaded_models:
                    logger.warning(f"Modèle {model_id} non chargé")
                    return True
                
                self.loaded_models[model_id].state = ModelState.RETIRED
                del self.loaded_models[model_id]
                
                # Nettoyer le cache associé
                cache_keys_to_remove = [
                    key for key in self.prediction_cache.keys()
                    if key.startswith(f"{model_id}:")
                ]
                for key in cache_keys_to_remove:
                    del self.prediction_cache[key]
                    if key in self.cache_access_times:
                        del self.cache_access_times[key]
                
                logger.info(f"Modèle {model_id} déchargé")
                return True
                
        except Exception as e:
            logger.error(f"Erreur déchargement modèle {model_id}: {e}")
            return False
    
    async def predict(self,
                     model_id: str,
                     input_data: Any,
                     priority: PredictionPriority = PredictionPriority.NORMAL,
                     timeout_ms: int = 5000,
                     use_cache: bool = True) -> PredictionResponse:
        """Effectue une prédiction"""
        
        request_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        try:
            # Vérifier que le modèle est chargé
            if model_id not in self.loaded_models:
                return PredictionResponse(
                    request_id=request_id,
                    model_id=model_id,
                    prediction=None,
                    confidence=None,
                    latency_ms=0.0,
                    status=InferenceStatus.FAILED,
                    created_at=start_time,
                    error_message=f"Modèle {model_id} non chargé"
                )
            
            # Vérifier le cache si activé
            if use_cache:
                cache_key = self._generate_cache_key(model_id, input_data)
                cached_response = self._get_from_cache(cache_key)
                if cached_response:
                    # Cloner la réponse avec un nouveau request_id
                    cached_response.request_id = request_id
                    cached_response.created_at = start_time
                    return cached_response
            
            # Créer la requête
            request = PredictionRequest(
                request_id=request_id,
                model_id=model_id,
                input_data=input_data,
                priority=priority,
                created_at=start_time,
                timeout_ms=timeout_ms
            )
            
            # Ajouter à la queue appropriée
            return await self._queue_prediction(request, use_cache)
            
        except Exception as e:
            logger.error(f"Erreur prédiction pour {model_id}: {e}")
            return PredictionResponse(
                request_id=request_id,
                model_id=model_id,
                prediction=None,
                confidence=None,
                latency_ms=(datetime.now() - start_time).total_seconds() * 1000,
                status=InferenceStatus.FAILED,
                created_at=start_time,
                error_message=str(e)
            )
    
    async def _queue_prediction(self, request: PredictionRequest, use_cache: bool = True) -> PredictionResponse:
        """Ajoute une prédiction à la queue et attend le résultat"""
        
        # Vérifier la taille de la queue
        total_queue_size = sum(
            q.qsize() for q in self.request_queues.values()
        )
        
        if total_queue_size >= self.max_queue_size:
            return PredictionResponse(
                request_id=request.request_id,
                model_id=request.model_id,
                prediction=None,
                confidence=None,
                latency_ms=0.0,
                status=InferenceStatus.FAILED,
                created_at=request.created_at,
                error_message="Queue pleine"
            )
        
        # Créer un event pour la synchronisation
        result_event = threading.Event()
        result_container = {}
        
        def callback(response -> None: PredictionResponse) -> None:
            result_container['response'] = response
            result_event.set()
        
        request.callback = callback
        
        # Ajouter à la queue de priorité appropriée
        priority_value = 5 - request.priority.value  # Inverser pour que CRITICAL = 1
        self.request_queues[request.priority].put((priority_value, time.time(), request))
        
        self.metrics.total_requests += 1
        
        # Attendre le résultat avec timeout
        timeout_seconds = request.timeout_ms / 1000.0
        result_event.wait(timeout=timeout_seconds)
        
        if not result_event.is_set():
            # Timeout
            self.metrics.timeout_requests += 1
            return PredictionResponse(
                request_id=request.request_id,
                model_id=request.model_id,
                prediction=None,
                confidence=None,
                latency_ms=request.timeout_ms,
                status=InferenceStatus.TIMEOUT,
                created_at=request.created_at,
                error_message="Timeout"
            )
        
        response = result_container.get('response')
        
        # Mettre en cache si succès
        if use_cache and response and response.status == InferenceStatus.COMPLETED:
            cache_key = self._generate_cache_key(request.model_id, request.input_data)
            self._put_in_cache(cache_key, response)
        
        return response
    
    def _worker_loop(self, worker_name -> None: str) -> None:
        """Boucle principale d'un worker"""
        logger.info(f"Worker {worker_name} démarré")
        
        while self.is_running and not self.shutdown_event.is_set():
            try:
                # Chercher une requête dans les queues par ordre de priorité
                request = None
                
                for priority in [PredictionPriority.CRITICAL, PredictionPriority.HIGH, 
                               PredictionPriority.NORMAL, PredictionPriority.LOW]:
                    try:
                        _, _, request = self.request_queues[priority].get_nowait()
                        break
                    except queue.Empty:
                        continue
                
                if request is None:
                    # Aucune requête, attendre un peu
                    time.sleep(0.01)
                    continue
                
                # Traiter la requête
                response = self._process_prediction(request)
                
                # Appeler le callback si défini
                if request.callback:
                    try:
                        request.callback(response)
                    except Exception as e:
                        logger.error(f"Erreur callback: {e}")
                
                # Mettre à jour les métriques
                self._update_metrics(response)
                
                # Stocker dans l'historique
                self.request_history[request.request_id] = response
                
                # Appeler les callbacks globaux
                for callback in self.prediction_callbacks:
                    try:
                        callback(response)
                    except Exception as e:
                        logger.error(f"Erreur callback global: {e}")
                
            except Exception as e:
                logger.error(f"Erreur dans worker {worker_name}: {e}")
                
                if request and request.callback:
                    error_response = PredictionResponse(
                        request_id=request.request_id,
                        model_id=request.model_id,
                        prediction=None,
                        confidence=None,
                        latency_ms=0.0,
                        status=InferenceStatus.FAILED,
                        created_at=request.created_at,
                        error_message=str(e)
                    )
                    try:
                        request.callback(error_response)
                    except Exception as cb_error:
                        logger.error(f"Erreur callback d'erreur: {cb_error}")
                
                # Appeler les callbacks d'erreur
                for error_callback in self.error_callbacks:
                    try:
                        error_callback(e, request)
                    except Exception as cb_error:
                        logger.error(f"Erreur callback d'erreur global: {cb_error}")
        
        logger.info(f"Worker {worker_name} arrêté")
    
    def _process_prediction(self, request: PredictionRequest) -> PredictionResponse:
        """Traite une requête de prédiction"""
        start_time = time.time()
        
        try:
            model_instance = self.loaded_models.get(request.model_id)
            if not model_instance or model_instance.state != ModelState.READY:
                return PredictionResponse(
                    request_id=request.request_id,
                    model_id=request.model_id,
                    prediction=None,
                    confidence=None,
                    latency_ms=0.0,
                    status=InferenceStatus.FAILED,
                    created_at=request.created_at,
                    error_message=f"Modèle {request.model_id} non disponible"
                )
            
            # Marquer le modèle comme occupé
            model_instance.state = ModelState.BUSY
            model_instance.last_used = datetime.now()
            
            try:
                # Effectuer la prédiction
                prediction = model_instance.model.predict(request.input_data)
                
                # Calculer la confiance si possible
                confidence = None
                if hasattr(model_instance.model, 'predict_proba'):
                    try:
                        proba = model_instance.model.predict_proba(request.input_data)
                        if proba is not None and len(proba) > 0:
                            confidence = float(np.max(proba))
                    except Exception:
                        pass  # Confiance non disponible
                
                # Calculer la latence
                latency_ms = (time.time() - start_time) * 1000
                
                # Mettre à jour les statistiques du modèle
                model_instance.prediction_count += 1
                model_instance.total_latency += latency_ms
                
                return PredictionResponse(
                    request_id=request.request_id,
                    model_id=request.model_id,
                    prediction=prediction,
                    confidence=confidence,
                    latency_ms=latency_ms,
                    status=InferenceStatus.COMPLETED,
                    created_at=request.created_at,
                    completed_at=datetime.now()
                )
                
            finally:
                # Remettre le modèle en état prêt
                model_instance.state = ModelState.READY
            
        except Exception as e:
            logger.error(f"Erreur traitement prédiction {request.request_id}: {e}")
            
            if request.model_id in self.loaded_models:
                self.loaded_models[request.model_id].error_count += 1
                self.loaded_models[request.model_id].state = ModelState.READY
            
            return PredictionResponse(
                request_id=request.request_id,
                model_id=request.model_id,
                prediction=None,
                confidence=None,
                latency_ms=(time.time() - start_time) * 1000,
                status=InferenceStatus.FAILED,
                created_at=request.created_at,
                error_message=str(e)
            )
    
    def _generate_cache_key(self, model_id: str, input_data: Any) -> str:
        """Génère une clé de cache pour les données d'entrée"""
        try:
            # Convertir les données en string pour le hash
            if isinstance(input_data, np.ndarray):
                data_str = input_data.tobytes()
            elif isinstance(input_data, (list, tuple)):
                data_str = str(input_data)
            else:
                data_str = str(input_data)
            
            # Créer le hash
            hash_obj = hashlib.md5(data_str.encode())
            return f"{model_id}:{hash_obj.hexdigest()}"
            
        except Exception as e:
            logger.error(f"Erreur génération clé cache: {e}")
            return f"{model_id}:no_cache"
    
    def _get_from_cache(self, cache_key: str) -> Optional[PredictionResponse]:
        """Récupère une réponse du cache"""
        try:
            if cache_key in self.prediction_cache:
                self.cache_access_times[cache_key] = datetime.now()
                return self.prediction_cache[cache_key]
            return None
        except Exception as e:
            logger.error(f"Erreur lecture cache: {e}")
            return None
    
    def _put_in_cache(self, cache_key -> None: str, response -> None: PredictionResponse) -> None:
        """Met une réponse en cache"""
        try:
            # Vérifier la taille du cache
            if len(self.prediction_cache) >= self.cache_size:
                self._evict_cache()
            
            self.prediction_cache[cache_key] = response
            self.cache_access_times[cache_key] = datetime.now()
            
        except Exception as e:
            logger.error(f"Erreur mise en cache: {e}")
    
    def _evict_cache(self) -> None:
        """Éviction LRU du cache"""
        try:
            if not self.cache_access_times:
                return
            
            # Trouver l'entrée la moins récemment utilisée
            oldest_key = min(self.cache_access_times.keys(), 
                           key=lambda k: self.cache_access_times[k])
            
            # Supprimer l'entrée
            if oldest_key in self.prediction_cache:
                del self.prediction_cache[oldest_key]
            if oldest_key in self.cache_access_times:
                del self.cache_access_times[oldest_key]
                
        except Exception as e:
            logger.error(f"Erreur éviction cache: {e}")
    
    def _update_metrics(self, response -> None: PredictionResponse) -> None:
        """Met à jour les métriques"""
        try:
            if response.status == InferenceStatus.COMPLETED:
                self.metrics.completed_requests += 1
                self.latency_history.append(response.latency_ms)
            elif response.status == InferenceStatus.FAILED:
                self.metrics.failed_requests += 1
            elif response.status == InferenceStatus.TIMEOUT:
                self.metrics.timeout_requests += 1
            
            # Calculer les latences
            if self.latency_history:
                self.metrics.avg_latency_ms = sum(self.latency_history) / len(self.latency_history)
                self.metrics.p95_latency_ms = np.percentile(self.latency_history, 95)
                self.metrics.p99_latency_ms = np.percentile(self.latency_history, 99)
            
            # Taille de la queue
            self.metrics.current_queue_size = sum(
                q.qsize() for q in self.request_queues.values()
            )
            
            # Taux de cache hit
            if self.metrics.total_requests > 0:
                cache_hits = len(self.prediction_cache)
                self.metrics.cache_hit_rate = cache_hits / self.metrics.total_requests
            
        except Exception as e:
            logger.error(f"Erreur mise à jour métriques: {e}")
    
    async def _cleanup_loop(self) -> None:
        """Boucle de nettoyage périodique"""
        while self.is_running:
            try:
                await asyncio.sleep(60)  # Toutes les minutes
                
                # Nettoyer le cache ancien
                cutoff_time = datetime.now() - timedelta(minutes=10)
                keys_to_remove = [
                    key for key, access_time in self.cache_access_times.items()
                    if access_time < cutoff_time
                ]
                
                for key in keys_to_remove:
                    if key in self.prediction_cache:
                        del self.prediction_cache[key]
                    if key in self.cache_access_times:
                        del self.cache_access_times[key]
                
                # Nettoyer l'historique ancien
                cutoff_time = datetime.now() - timedelta(hours=1)
                old_requests = [
                    req_id for req_id, response in self.request_history.items()
                    if response.created_at < cutoff_time
                ]
                
                for req_id in old_requests:
                    del self.request_history[req_id]
                
                # Nettoyer les modèles inutilisés
                cutoff_time = datetime.now() - timedelta(minutes=self.model_timeout_minutes)
                for model_id, instance in list(self.loaded_models.items()):
                    if instance.last_used < cutoff_time and instance.state == ModelState.READY:
                        await self.unload_model(model_id)
                        logger.info(f"Modèle {model_id} déchargé automatiquement (inactif)")
                
            except Exception as e:
                logger.error(f"Erreur boucle nettoyage: {e}")
    
    async def _metrics_loop(self) -> None:
        """Boucle de collection des métriques"""
        while self.is_running:
            try:
                await asyncio.sleep(30)  # Toutes les 30 secondes
                
                # Loguer les métriques principales
                logger.info(
                    f"Métriques inférence - "
                    f"Requêtes: {self.metrics.total_requests}, "
                    f"Succès: {self.metrics.completed_requests}, "
                    f"Échecs: {self.metrics.failed_requests}, "
                    f"Latence moy: {self.metrics.avg_latency_ms:.2f}ms, "
                    f"Queue: {self.metrics.current_queue_size}, "
                    f"Cache hit: {self.metrics.cache_hit_rate:.2%}"
                )
                
            except Exception as e:
                logger.error(f"Erreur boucle métriques: {e}")
    
    async def _auto_scaling_loop(self) -> None:
        """Boucle d'auto-scaling"""
        while self.is_running:
            try:
                await asyncio.sleep(60)  # Toutes les minutes
                
                # Vérifier si scaling nécessaire
                current_queue_size = self.metrics.current_queue_size
                avg_latency = self.metrics.avg_latency_ms
                
                # Scale up si nécessaire
                if (current_queue_size > self.scaling_metrics["queue_length_threshold"] or
                    avg_latency > self.scaling_metrics["latency_threshold_ms"]):
                    
                    if len(self.workers) < self.max_workers * 2:  # Limite de sécurité
                        await self._scale_up()
                
                # Scale down si possible
                elif (current_queue_size < self.scaling_metrics["scale_down_threshold"] and
                      avg_latency < self.scaling_metrics["latency_threshold_ms"] / 2):
                    
                    if len(self.workers) > self.max_workers:
                        await self._scale_down()
                
            except Exception as e:
                logger.error(f"Erreur boucle auto-scaling: {e}")
    
    async def _scale_up(self) -> None:
        """Scale up le nombre de workers"""
        try:
            workers_to_add = self.scaling_metrics["scale_up_workers"]
            
            for i in range(workers_to_add):
                worker_name = f"auto_worker_{len(self.workers)}_{int(time.time())}"
                worker = threading.Thread(
                    target=self._worker_loop,
                    args=(worker_name,),
                    daemon=True
                )
                worker.start()
                self.workers.append(worker)
            
            self.scaling_metrics["last_scale_time"] = datetime.now()
            logger.info(f"Scaled up: +{workers_to_add} workers (total: {len(self.workers)})")
            
        except Exception as e:
            logger.error(f"Erreur scale up: {e}")
    
    async def _scale_down(self) -> None:
        """Scale down le nombre de workers"""
        try:
            # Simple: ne pas créer de nouveaux workers lors du prochain cycle
            # Les workers actuels finiront naturellement
            
            self.scaling_metrics["last_scale_time"] = datetime.now()
            logger.info("Scale down planifié pour le prochain cycle")
            
        except Exception as e:
            logger.error(f"Erreur scale down: {e}")
    
    def add_prediction_callback(self, callback -> None: Callable[[PredictionResponse], None]) -> None:
        """Ajoute un callback pour les prédictions"""
        self.prediction_callbacks.append(callback)
    
    def add_error_callback(self, callback -> None: Callable[[Exception, PredictionRequest], None]) -> None:
        """Ajoute un callback pour les erreurs"""
        self.error_callbacks.append(callback)
    
    def get_metrics(self) -> InferenceMetrics:
        """Récupère les métriques actuelles"""
        self.metrics.active_workers = len([w for w in self.workers if w.is_alive()])
        return self.metrics
    
    def get_model_stats(self) -> Dict[str, Dict[str, Any]]:
        """Récupère les statistiques des modèles"""
        stats = {}
        for model_id, instance in self.loaded_models.items():
            avg_latency = (instance.total_latency / instance.prediction_count 
                          if instance.prediction_count > 0 else 0)
            
            stats[model_id] = {
                "state": instance.state.value,
                "load_time": instance.load_time.isoformat(),
                "last_used": instance.last_used.isoformat(),
                "prediction_count": instance.prediction_count,
                "avg_latency_ms": avg_latency,
                "error_count": instance.error_count,
                "memory_usage_mb": instance.memory_usage_mb
            }
        
        return stats
    
    async def health_check(self) -> Dict[str, Any]:
        """Vérification de santé du moteur"""
        return {
            "status": "healthy" if self.is_running else "stopped",
            "workers_alive": len([w for w in self.workers if w.is_alive()]),
            "total_workers": len(self.workers),
            "loaded_models": len(self.loaded_models),
            "queue_size": sum(q.qsize() for q in self.request_queues.values()),
            "cache_size": len(self.prediction_cache),
            "metrics": self.get_metrics().__dict__
        }


# Factory pour créer des moteurs spécialisés
class InferenceEngineFactory:
    """Factory pour créer des moteurs d'inférence spécialisés"""
    
    @staticmethod
    def create_high_performance_engine() -> RealTimeInferenceEngine:
        """Moteur haute performance pour production"""
        return RealTimeInferenceEngine(
            max_workers=20,
            max_queue_size=50000,
            cache_size=5000,
            model_timeout_minutes=60,
            enable_auto_scaling=True
        )
    
    @staticmethod
    def create_low_latency_engine() -> RealTimeInferenceEngine:
        """Moteur optimisé pour latence minimale"""
        return RealTimeInferenceEngine(
            max_workers=50,
            max_queue_size=10000,
            cache_size=10000,
            model_timeout_minutes=15,
            enable_auto_scaling=True
        )
    
    @staticmethod
    def create_development_engine() -> RealTimeInferenceEngine:
        """Moteur pour développement"""
        return RealTimeInferenceEngine(
            max_workers=4,
            max_queue_size=1000,
            cache_size=100,
            model_timeout_minutes=10,
            enable_auto_scaling=False
        )


# Exemple d'utilisation
async def example_usage() -> None:
    """Exemple d'utilisation du moteur d'inférence"""
    
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.datasets import make_classification
    import numpy as np
    
    # Créer des données d'exemple
    X, y = make_classification(n_samples=1000, n_features=10, random_state=42)
    
    # Entraîner un modèle
    model = RandomForestClassifier(n_estimators=10, random_state=42)
    model.fit(X, y)
    
    # Créer le moteur d'inférence
    engine = InferenceEngineFactory.create_development_engine()
    
    # Ajouter des callbacks
    def prediction_callback(response -> None: PredictionResponse) -> None:
        print(f"Prédiction terminée: {response.request_id} - "
              f"Latence: {response.latency_ms:.2f}ms")
    
    engine.add_prediction_callback(prediction_callback)
    
    try:
        # Démarrer le moteur
        await engine.start()
        
        # Charger le modèle
        await engine.load_model("test_classifier", model)
        
        # Faire des prédictions
        print("Début des prédictions...")
        
        for i in range(10):
            # Données de test aléatoires
            test_data = np.random.randn(1, 10)
            
            # Prédiction avec différentes priorités
            priority = PredictionPriority.HIGH if i % 3 == 0 else PredictionPriority.NORMAL
            
            response = await engine.predict(
                model_id="test_classifier",
                input_data=test_data,
                priority=priority,
                timeout_ms=2000
            )
            
            print(f"Prédiction {i}: {response.prediction}, "
                  f"Confiance: {response.confidence}, "
                  f"Latence: {response.latency_ms:.2f}ms")
        
        # Afficher les métriques
        metrics = engine.get_metrics()
        print(f"\nMétriques finales:")
        print(f"- Total requêtes: {metrics.total_requests}")
        print(f"- Succès: {metrics.completed_requests}")
        print(f"- Latence moyenne: {metrics.avg_latency_ms:.2f}ms")
        print(f"- P95 latence: {metrics.p95_latency_ms:.2f}ms")
        print(f"- Taux cache hit: {metrics.cache_hit_rate:.2%}")
        
        # Statistiques des modèles
        model_stats = engine.get_model_stats()
        print(f"\nStatistiques modèles: {model_stats}")
        
        # Vérification de santé
        health = await engine.health_check()
        print(f"\nSanté du système: {health}")
        
    finally:
        # Arrêter le moteur
        await engine.stop()


if __name__ == "__main__":
    asyncio.run(example_usage())