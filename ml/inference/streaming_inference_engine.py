"""🚀 Streaming Inference Engine - IA Influencer Agent Platform Enterprise
========================================================================
Module: backend/ml/inference/streaming_inference_engine.py
Author: Fahed Mlaiel (mlaiel@live.de)
========================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 MOTEUR D'INFÉRENCE STREAMING
Engine de traitement temps réel pour flux continus
- Traitement de streams audio/video/text en temps réel
- Buffer circulaire avec fenêtrage temporel
- Back-pressure handling et flow control
- Agrégation de prédictions temporelles
"""

import asyncio
import logging
import time
import uuid
from typing import Dict, List, Optional, Any, Union, Tuple, Callable, AsyncIterator
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import pickle
import hashlib
from pathlib import Path
from collections import defaultdict, deque
import threading
from concurrent.futures import ThreadPoolExecutor
import queue
import math

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator

# Configuration
logger = logging.getLogger(__name__)

class StreamType(Enum):
    """Types de streams"""
    AUDIO = "audio"
    VIDEO = "video"
    TEXT = "text"
    SENSOR = "sensor"
    METRICS = "metrics"
    MIXED = "mixed"

class StreamStatus(Enum):
    """Statuts des streams"""
    CREATED = "created"
    CONNECTED = "connected"
    STREAMING = "streaming"
    PAUSED = "paused"
    DISCONNECTED = "disconnected"
    ERROR = "error"

class WindowType(Enum):
    """Types de fenêtrage"""
    TUMBLING = "tumbling"     # Non-overlapping windows
    SLIDING = "sliding"       # Overlapping windows
    SESSION = "session"       # Dynamic windows based on gaps
    HOPPING = "hopping"       # Fixed-size windows with fixed intervals

class AggregationType(Enum):
    """Types d'agrégation"""
    NONE = "none"
    AVERAGE = "average"
    MAJORITY_VOTE = "majority_vote"
    WEIGHTED_AVERAGE = "weighted_average"
    MAX_CONFIDENCE = "max_confidence"
    ENSEMBLE = "ensemble"

@dataclass
class StreamConfig:
    """Configuration d'un stream"""
    stream_id: str
    stream_type: StreamType
    window_size_ms: int = 1000
    window_type: WindowType = WindowType.TUMBLING
    overlap_ms: int = 0
    aggregation_type: AggregationType = AggregationType.AVERAGE
    buffer_size: int = 10000
    max_latency_ms: int = 100
    enable_back_pressure: bool = True
    quality_threshold: float = 0.0

@dataclass
class StreamSample:
    """Échantillon de stream"""
    sample_id: str
    stream_id: str
    timestamp: datetime
    data: Any
    metadata: Dict[str, Any] = field(default_factory=dict)
    sequence_number: int = 0

@dataclass
class StreamWindow:
    """Fenêtre de stream"""
    window_id: str
    stream_id: str
    start_time: datetime
    end_time: datetime
    samples: List[StreamSample]
    aggregated_data: Optional[Any] = None
    is_complete: bool = False

@dataclass
class StreamPrediction:
    """Prédiction sur stream"""
    prediction_id: str
    stream_id: str
    window_id: str
    timestamp: datetime
    prediction: Any
    confidence: Optional[float]
    latency_ms: float
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class StreamMetrics:
    """Métriques de streaming"""
    stream_id: str
    samples_received: int = 0
    samples_processed: int = 0
    samples_dropped: int = 0
    predictions_made: int = 0
    average_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    throughput_samples_per_second: float = 0.0
    buffer_utilization: float = 0.0
    back_pressure_events: int = 0
    last_update: datetime = field(default_factory=datetime.now)

class StreamingInferenceEngine:
    """Moteur d'inférence streaming enterprise"""
    
    def __init__(self,
                 max_concurrent_streams: int = 100,
                 global_buffer_size: int = 100000,
                 prediction_timeout_ms: int = 5000,
                 enable_adaptive_windowing: bool = True):
        
        self.max_concurrent_streams = max_concurrent_streams
        self.global_buffer_size = global_buffer_size
        self.prediction_timeout_ms = prediction_timeout_ms
        self.enable_adaptive_windowing = enable_adaptive_windowing
        
        # Streams actifs
        self.streams: Dict[str, StreamConfig] = {}
        self.stream_buffers: Dict[str, deque] = {}
        self.stream_windows: Dict[str, Dict[str, StreamWindow]] = defaultdict(dict)
        self.stream_status: Dict[str, StreamStatus] = {}
        
        # Modèles par type de stream
        self.models: Dict[str, Dict[StreamType, Any]] = {}  # model_id -> stream_type -> model
        self.model_locks: Dict[str, threading.Lock] = defaultdict(threading.Lock)
        
        # Processing
        self.worker_pool = ThreadPoolExecutor(max_workers=20)
        self.processing_queues: Dict[str, asyncio.Queue] = {}
        self.prediction_tasks: Dict[str, asyncio.Task] = {}
        
        # Métriques et monitoring
        self.stream_metrics: Dict[str, StreamMetrics] = {}
        self.global_metrics = {
            "active_streams": 0,
            "total_samples_processed": 0,
            "total_predictions": 0,
            "average_throughput": 0.0,
            "system_latency_ms": 0.0
        }
        
        # State management
        self.is_running = False
        self.shutdown_event = asyncio.Event()
        
        # Callbacks
        self.prediction_callbacks: Dict[str, List[Callable]] = defaultdict(list)
        self.window_callbacks: Dict[str, List[Callable]] = defaultdict(list)
        self.error_callbacks: List[Callable] = []
        
        # Adaptive windowing
        self.adaptive_configs: Dict[str, Dict[str, Any]] = {}
    
    async def start(self):
        """Démarre le moteur de streaming"""
        try:
            self.is_running = True
            logger.info("Démarrage du moteur d'inférence streaming")
            
            # Démarrer les tâches de gestion
            asyncio.create_task(self._monitoring_loop())
            asyncio.create_task(self._cleanup_loop())
            
            if self.enable_adaptive_windowing:
                asyncio.create_task(self._adaptive_windowing_loop())
            
            logger.info("Moteur de streaming démarré avec succès")
            
        except Exception as e:
            logger.error(f"Erreur démarrage moteur streaming: {e}")
            raise
    
    async def stop(self):
        """Arrête le moteur de streaming"""
        try:
            logger.info("Arrêt du moteur de streaming...")
            
            self.is_running = False
            self.shutdown_event.set()
            
            # Arrêter tous les streams
            for stream_id in list(self.streams.keys()):
                await self.stop_stream(stream_id)
            
            # Arrêter les tâches de prédiction
            for task in self.prediction_tasks.values():
                task.cancel()
            
            # Fermer le pool de workers
            self.worker_pool.shutdown(wait=True)
            
            logger.info("Moteur de streaming arrêté")
            
        except Exception as e:
            logger.error(f"Erreur arrêt moteur streaming: {e}")
    
    async def register_model(self, model_id: str, model: Any, stream_type: StreamType) -> bool:
        """Enregistre un modèle pour un type de stream"""
        try:
            with self.model_locks[model_id]:
                if model_id not in self.models:
                    self.models[model_id] = {}
                
                # Vérifier que le modèle est valide
                if not hasattr(model, 'predict'):
                    raise ValueError("Le modèle n'a pas de méthode predict")
                
                self.models[model_id][stream_type] = model
                logger.info(f"Modèle {model_id} enregistré pour {stream_type.value}")
                return True
                
        except Exception as e:
            logger.error(f"Erreur enregistrement modèle {model_id}: {e}")
            return False
    
    async def create_stream(self, config: StreamConfig) -> bool:
        """Crée un nouveau stream"""
        try:
            if len(self.streams) >= self.max_concurrent_streams:
                raise ValueError(f"Limite de streams atteinte: {self.max_concurrent_streams}")
            
            if config.stream_id in self.streams:
                raise ValueError(f"Stream {config.stream_id} existe déjà")
            
            # Créer le stream
            self.streams[config.stream_id] = config
            self.stream_buffers[config.stream_id] = deque(maxlen=config.buffer_size)
            self.stream_status[config.stream_id] = StreamStatus.CREATED
            self.stream_metrics[config.stream_id] = StreamMetrics(stream_id=config.stream_id)
            
            # Créer la queue de processing
            self.processing_queues[config.stream_id] = asyncio.Queue(maxsize=config.buffer_size)
            
            # Démarrer la tâche de traitement
            self.prediction_tasks[config.stream_id] = asyncio.create_task(
                self._process_stream(config.stream_id)
            )
            
            logger.info(f"Stream {config.stream_id} créé ({config.stream_type.value})")
            return True
            
        except Exception as e:
            logger.error(f"Erreur création stream {config.stream_id}: {e}")
            return False
    
    async def start_stream(self, stream_id: str) -> bool:
        """Démarre un stream"""
        try:
            if stream_id not in self.streams:
                raise ValueError(f"Stream {stream_id} n'existe pas")
            
            self.stream_status[stream_id] = StreamStatus.STREAMING
            logger.info(f"Stream {stream_id} démarré")
            return True
            
        except Exception as e:
            logger.error(f"Erreur démarrage stream {stream_id}: {e}")
            return False
    
    async def stop_stream(self, stream_id: str) -> bool:
        """Arrête un stream"""
        try:
            if stream_id not in self.streams:
                return True
            
            self.stream_status[stream_id] = StreamStatus.DISCONNECTED
            
            # Arrêter la tâche de traitement
            if stream_id in self.prediction_tasks:
                self.prediction_tasks[stream_id].cancel()
                del self.prediction_tasks[stream_id]
            
            # Nettoyer les données
            if stream_id in self.processing_queues:
                del self.processing_queues[stream_id]
            
            logger.info(f"Stream {stream_id} arrêté")
            return True
            
        except Exception as e:
            logger.error(f"Erreur arrêt stream {stream_id}: {e}")
            return False
    
    async def push_sample(self, stream_id: str, data: Any, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Pousse un échantillon dans le stream"""
        try:
            if stream_id not in self.streams:
                raise ValueError(f"Stream {stream_id} n'existe pas")
            
            if self.stream_status[stream_id] != StreamStatus.STREAMING:
                return False
            
            # Créer l'échantillon
            sample = StreamSample(
                sample_id=str(uuid.uuid4()),
                stream_id=stream_id,
                timestamp=datetime.now(),
                data=data,
                metadata=metadata or {},
                sequence_number=self.stream_metrics[stream_id].samples_received
            )
            
            # Vérifier back-pressure
            config = self.streams[stream_id]
            if config.enable_back_pressure:
                queue_size = self.processing_queues[stream_id].qsize()
                if queue_size > config.buffer_size * 0.8:
                    self.stream_metrics[stream_id].back_pressure_events += 1
                    self.stream_metrics[stream_id].samples_dropped += 1
                    logger.warning(f"Back-pressure sur stream {stream_id}, échantillon droppé")
                    return False
            
            # Ajouter à la queue de processing
            try:
                self.processing_queues[stream_id].put_nowait(sample)
                self.stream_metrics[stream_id].samples_received += 1
                return True
            except asyncio.QueueFull:
                self.stream_metrics[stream_id].samples_dropped += 1
                return False
                
        except Exception as e:
            logger.error(f"Erreur push échantillon stream {stream_id}: {e}")
            return False
    
    async def _process_stream(self, stream_id: str):
        """Traite un stream en continu"""
        config = self.streams[stream_id]
        current_window: Optional[StreamWindow] = None
        
        try:
            while self.is_running and not self.shutdown_event.is_set():
                if self.stream_status[stream_id] != StreamStatus.STREAMING:
                    await asyncio.sleep(0.1)
                    continue
                
                try:
                    # Récupérer un échantillon
                    sample = await asyncio.wait_for(
                        self.processing_queues[stream_id].get(),
                        timeout=1.0
                    )
                    
                    # Gérer le fenêtrage
                    windows_to_process = await self._handle_windowing(config, sample, current_window)
                    
                    for window in windows_to_process:
                        if window.is_complete:
                            # Traiter la fenêtre complète
                            await self._process_window(window)
                        else:
                            # Fenêtre encore en cours
                            current_window = window
                    
                    self.stream_metrics[stream_id].samples_processed += 1
                    
                except asyncio.TimeoutError:
                    # Timeout normal, continuer
                    continue
                except Exception as e:
                    logger.error(f"Erreur traitement stream {stream_id}: {e}")
                    await asyncio.sleep(1.0)
        
        except Exception as e:
            logger.error(f"Erreur fatale stream {stream_id}: {e}")
            self.stream_status[stream_id] = StreamStatus.ERROR
    
    async def _handle_windowing(self,
                               config: StreamConfig,
                               sample: StreamSample,
                               current_window: Optional[StreamWindow]) -> List[StreamWindow]:
        """Gère le fenêtrage des échantillons"""
        
        windows_to_return = []
        
        try:
            if config.window_type == WindowType.TUMBLING:
                windows_to_return = await self._handle_tumbling_window(config, sample, current_window)
                
            elif config.window_type == WindowType.SLIDING:
                windows_to_return = await self._handle_sliding_window(config, sample, current_window)
                
            elif config.window_type == WindowType.SESSION:
                windows_to_return = await self._handle_session_window(config, sample, current_window)
                
            elif config.window_type == WindowType.HOPPING:
                windows_to_return = await self._handle_hopping_window(config, sample, current_window)
            
            return windows_to_return
            
        except Exception as e:
            logger.error(f"Erreur fenêtrage: {e}")
            return []
    
    async def _handle_tumbling_window(self,
                                    config: StreamConfig,
                                    sample: StreamSample,
                                    current_window: Optional[StreamWindow]) -> List[StreamWindow]:
        """Gère les fenêtres tumbling (non-overlapping)"""
        
        windows = []
        
        # Si pas de fenêtre courante, en créer une
        if current_window is None:
            current_window = StreamWindow(
                window_id=f"{config.stream_id}_window_{int(time.time() * 1000)}",
                stream_id=config.stream_id,
                start_time=sample.timestamp,
                end_time=sample.timestamp + timedelta(milliseconds=config.window_size_ms),
                samples=[]
            )
        
        # Vérifier si l'échantillon appartient à la fenêtre courante
        if sample.timestamp <= current_window.end_time:
            current_window.samples.append(sample)
        else:
            # Fermer la fenêtre courante
            current_window.is_complete = True
            windows.append(current_window)
            
            # Créer une nouvelle fenêtre
            current_window = StreamWindow(
                window_id=f"{config.stream_id}_window_{int(time.time() * 1000)}",
                stream_id=config.stream_id,
                start_time=sample.timestamp,
                end_time=sample.timestamp + timedelta(milliseconds=config.window_size_ms),
                samples=[sample]
            )
            windows.append(current_window)
        
        return windows
    
    async def _handle_sliding_window(self,
                                   config: StreamConfig,
                                   sample: StreamSample,
                                   current_window: Optional[StreamWindow]) -> List[StreamWindow]:
        """Gère les fenêtres sliding (overlapping)"""
        
        windows = []
        
        # Pour les fenêtres sliding, on peut avoir plusieurs fenêtres actives
        # Implémentation simplifiée: créer une nouvelle fenêtre périodiquement
        
        if current_window is None:
            current_window = StreamWindow(
                window_id=f"{config.stream_id}_sliding_{int(time.time() * 1000)}",
                stream_id=config.stream_id,
                start_time=sample.timestamp,
                end_time=sample.timestamp + timedelta(milliseconds=config.window_size_ms),
                samples=[]
            )
        
        current_window.samples.append(sample)
        
        # Vérifier si on doit créer une nouvelle fenêtre (basé sur overlap)
        window_duration = (sample.timestamp - current_window.start_time).total_seconds() * 1000
        if window_duration >= config.overlap_ms and len(current_window.samples) > 0:
            # Créer une copie de la fenêtre pour traitement
            completed_window = StreamWindow(
                window_id=current_window.window_id,
                stream_id=current_window.stream_id,
                start_time=current_window.start_time,
                end_time=current_window.end_time,
                samples=current_window.samples.copy(),
                is_complete=True
            )
            windows.append(completed_window)
            
            # Commencer une nouvelle fenêtre
            current_window = StreamWindow(
                window_id=f"{config.stream_id}_sliding_{int(time.time() * 1000)}",
                stream_id=config.stream_id,
                start_time=sample.timestamp,
                end_time=sample.timestamp + timedelta(milliseconds=config.window_size_ms),
                samples=[sample]
            )
            windows.append(current_window)
        
        return windows
    
    async def _handle_session_window(self,
                                   config: StreamConfig,
                                   sample: StreamSample,
                                   current_window: Optional[StreamWindow]) -> List[StreamWindow]:
        """Gère les fenêtres de session (gap-based)"""
        
        windows = []
        gap_threshold_ms = config.window_size_ms  # Utiliser window_size comme gap threshold
        
        if current_window is None:
            current_window = StreamWindow(
                window_id=f"{config.stream_id}_session_{int(time.time() * 1000)}",
                stream_id=config.stream_id,
                start_time=sample.timestamp,
                end_time=sample.timestamp,
                samples=[]
            )
        
        # Calculer le gap depuis le dernier échantillon
        if current_window.samples:
            last_sample_time = current_window.samples[-1].timestamp
            gap_ms = (sample.timestamp - last_sample_time).total_seconds() * 1000
            
            if gap_ms > gap_threshold_ms:
                # Gap trop important, fermer la session courante
                current_window.is_complete = True
                current_window.end_time = last_sample_time
                windows.append(current_window)
                
                # Commencer une nouvelle session
                current_window = StreamWindow(
                    window_id=f"{config.stream_id}_session_{int(time.time() * 1000)}",
                    stream_id=config.stream_id,
                    start_time=sample.timestamp,
                    end_time=sample.timestamp,
                    samples=[]
                )
        
        current_window.samples.append(sample)
        current_window.end_time = sample.timestamp
        windows.append(current_window)
        
        return windows
    
    async def _handle_hopping_window(self,
                                   config: StreamConfig,
                                   sample: StreamSample,
                                   current_window: Optional[StreamWindow]) -> List[StreamWindow]:
        """Gère les fenêtres hopping (fixed intervals)"""
        
        # Implémentation similaire à tumbling mais avec intervalles fixes
        return await self._handle_tumbling_window(config, sample, current_window)
    
    async def _process_window(self, window: StreamWindow):
        """Traite une fenêtre complète"""
        try:
            config = self.streams[window.stream_id]
            start_time = time.time()
            
            # Agréger les données de la fenêtre
            aggregated_data = await self._aggregate_window_data(window, config.aggregation_type)
            window.aggregated_data = aggregated_data
            
            # Trouver le modèle approprié
            model = await self._get_model_for_stream(window.stream_id, config.stream_type)
            if model is None:
                logger.error(f"Aucun modèle disponible pour stream {window.stream_id}")
                return
            
            # Faire la prédiction
            prediction_result = await self._make_prediction(model, aggregated_data)
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Créer la prédiction
            prediction = StreamPrediction(
                prediction_id=str(uuid.uuid4()),
                stream_id=window.stream_id,
                window_id=window.window_id,
                timestamp=datetime.now(),
                prediction=prediction_result.get('prediction'),
                confidence=prediction_result.get('confidence'),
                latency_ms=latency_ms,
                metadata={
                    'window_size': len(window.samples),
                    'window_duration_ms': (window.end_time - window.start_time).total_seconds() * 1000,
                    'aggregation_type': config.aggregation_type.value
                }
            )
            
            # Mettre à jour les métriques
            metrics = self.stream_metrics[window.stream_id]
            metrics.predictions_made += 1
            metrics.average_latency_ms = (
                (metrics.average_latency_ms * (metrics.predictions_made - 1) + latency_ms) /
                metrics.predictions_made
            )
            
            # Appeler les callbacks
            for callback in self.prediction_callbacks[window.stream_id]:
                try:
                    await callback(prediction)
                except Exception as e:
                    logger.error(f"Erreur callback prédiction: {e}")
            
            for callback in self.window_callbacks[window.stream_id]:
                try:
                    await callback(window)
                except Exception as e:
                    logger.error(f"Erreur callback fenêtre: {e}")
            
            logger.debug(f"Fenêtre {window.window_id} traitée: {prediction.prediction} "
                        f"(confiance: {prediction.confidence}, latence: {latency_ms:.2f}ms)")
            
        except Exception as e:
            logger.error(f"Erreur traitement fenêtre {window.window_id}: {e}")
            for callback in self.error_callbacks:
                try:
                    await callback(e, window)
                except Exception as cb_error:
                    logger.error(f"Erreur callback erreur: {cb_error}")
    
    async def _aggregate_window_data(self, window: StreamWindow, aggregation_type: AggregationType) -> Any:
        """Agrège les données d'une fenêtre"""
        
        if not window.samples:
            return None
        
        try:
            if aggregation_type == AggregationType.NONE:
                # Retourner toutes les données
                return [sample.data for sample in window.samples]
            
            elif aggregation_type == AggregationType.AVERAGE:
                # Moyenne des données numériques
                data_arrays = []
                for sample in window.samples:
                    if isinstance(sample.data, (int, float)):
                        data_arrays.append(sample.data)
                    elif isinstance(sample.data, np.ndarray):
                        data_arrays.append(sample.data)
                    elif isinstance(sample.data, list):
                        data_arrays.append(np.array(sample.data))
                
                if data_arrays:
                    return np.mean(data_arrays, axis=0)
                else:
                    return window.samples[-1].data  # Fallback
            
            elif aggregation_type == AggregationType.MAJORITY_VOTE:
                # Vote majoritaire pour données catégorielles
                from collections import Counter
                data_values = [sample.data for sample in window.samples]
                counter = Counter(data_values)
                return counter.most_common(1)[0][0]
            
            elif aggregation_type == AggregationType.WEIGHTED_AVERAGE:
                # Moyenne pondérée par timestamp (plus récent = plus de poids)
                total_weight = 0
                weighted_sum = None
                
                for i, sample in enumerate(window.samples):
                    weight = i + 1  # Poids croissant
                    total_weight += weight
                    
                    if isinstance(sample.data, (int, float)):
                        if weighted_sum is None:
                            weighted_sum = sample.data * weight
                        else:
                            weighted_sum += sample.data * weight
                    elif isinstance(sample.data, np.ndarray):
                        if weighted_sum is None:
                            weighted_sum = sample.data * weight
                        else:
                            weighted_sum += sample.data * weight
                
                if weighted_sum is not None and total_weight > 0:
                    return weighted_sum / total_weight
                else:
                    return window.samples[-1].data
            
            else:
                # Fallback: dernière valeur
                return window.samples[-1].data
                
        except Exception as e:
            logger.error(f"Erreur agrégation données: {e}")
            return window.samples[-1].data if window.samples else None
    
    async def _get_model_for_stream(self, stream_id: str, stream_type: StreamType) -> Optional[Any]:
        """Récupère le modèle approprié pour un stream"""
        try:
            # Chercher un modèle pour le type de stream
            for model_id, model_dict in self.models.items():
                if stream_type in model_dict:
                    return model_dict[stream_type]
            
            # Chercher un modèle générique
            for model_id, model_dict in self.models.items():
                if model_dict:
                    return list(model_dict.values())[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Erreur récupération modèle: {e}")
            return None
    
    async def _make_prediction(self, model: Any, data: Any) -> Dict[str, Any]:
        """Fait une prédiction avec le modèle"""
        try:
            # Préparer les données pour le modèle
            if data is None:
                raise ValueError("Données nulles")
            
            # Reshaper si nécessaire
            if isinstance(data, np.ndarray) and data.ndim == 1:
                data = data.reshape(1, -1)
            elif isinstance(data, list) and not isinstance(data[0], (list, np.ndarray)):
                data = np.array(data).reshape(1, -1)
            
            # Faire la prédiction
            prediction = model.predict(data)
            
            # Calculer la confiance si possible
            confidence = None
            if hasattr(model, 'predict_proba'):
                try:
                    proba = model.predict_proba(data)
                    if proba is not None and len(proba) > 0:
                        confidence = float(np.max(proba))
                except Exception:
                    pass
            
            return {
                'prediction': prediction,
                'confidence': confidence
            }
            
        except Exception as e:
            logger.error(f"Erreur prédiction: {e}")
            return {
                'prediction': None,
                'confidence': None
            }
    
    async def _monitoring_loop(self):
        """Boucle de monitoring"""
        while self.is_running:
            try:
                await asyncio.sleep(30)  # Toutes les 30 secondes
                
                # Mettre à jour les métriques globales
                self.global_metrics["active_streams"] = len([
                    s for s in self.stream_status.values() 
                    if s == StreamStatus.STREAMING
                ])
                
                total_samples = sum(m.samples_processed for m in self.stream_metrics.values())
                total_predictions = sum(m.predictions_made for m in self.stream_metrics.values())
                
                self.global_metrics["total_samples_processed"] = total_samples
                self.global_metrics["total_predictions"] = total_predictions
                
                # Calculer le throughput moyen
                now = datetime.now()
                total_throughput = 0
                active_streams = 0
                
                for stream_id, metrics in self.stream_metrics.items():
                    if self.stream_status.get(stream_id) == StreamStatus.STREAMING:
                        time_diff = (now - metrics.last_update).total_seconds()
                        if time_diff > 0:
                            throughput = metrics.samples_processed / time_diff
                            metrics.throughput_samples_per_second = throughput
                            total_throughput += throughput
                            active_streams += 1
                        
                        # Buffer utilization
                        if stream_id in self.processing_queues:
                            config = self.streams[stream_id]
                            current_size = self.processing_queues[stream_id].qsize()
                            metrics.buffer_utilization = current_size / config.buffer_size
                        
                        metrics.last_update = now
                
                if active_streams > 0:
                    self.global_metrics["average_throughput"] = total_throughput / active_streams
                
                # Log des métriques
                logger.info(
                    f"Streaming metrics - "
                    f"Active streams: {self.global_metrics['active_streams']}, "
                    f"Samples processed: {total_samples}, "
                    f"Predictions: {total_predictions}, "
                    f"Avg throughput: {self.global_metrics['average_throughput']:.1f} samples/s"
                )
                
            except Exception as e:
                logger.error(f"Erreur boucle monitoring: {e}")
    
    async def _cleanup_loop(self):
        """Boucle de nettoyage"""
        while self.is_running:
            try:
                await asyncio.sleep(300)  # Toutes les 5 minutes
                
                # Nettoyer les anciennes fenêtres
                cutoff_time = datetime.now() - timedelta(hours=1)
                
                for stream_id in list(self.stream_windows.keys()):
                    windows_to_remove = []
                    for window_id, window in self.stream_windows[stream_id].items():
                        if window.end_time < cutoff_time:
                            windows_to_remove.append(window_id)
                    
                    for window_id in windows_to_remove:
                        del self.stream_windows[stream_id][window_id]
                
                logger.debug("Nettoyage périodique effectué")
                
            except Exception as e:
                logger.error(f"Erreur boucle nettoyage: {e}")
    
    async def _adaptive_windowing_loop(self):
        """Boucle d'ajustement adaptatif des fenêtres"""
        while self.is_running:
            try:
                await asyncio.sleep(60)  # Toutes les minutes
                
                for stream_id, config in self.streams.items():
                    if self.stream_status.get(stream_id) != StreamStatus.STREAMING:
                        continue
                    
                    metrics = self.stream_metrics[stream_id]
                    
                    # Ajuster la taille de fenêtre basé sur la latence
                    if metrics.average_latency_ms > config.max_latency_ms * 1.5:
                        # Latence trop élevée, réduire la taille de fenêtre
                        new_window_size = max(config.window_size_ms * 0.8, 100)
                        config.window_size_ms = int(new_window_size)
                        logger.info(f"Réduction taille fenêtre stream {stream_id}: {config.window_size_ms}ms")
                    
                    elif metrics.average_latency_ms < config.max_latency_ms * 0.5:
                        # Latence faible, on peut augmenter la taille
                        new_window_size = min(config.window_size_ms * 1.2, 10000)
                        config.window_size_ms = int(new_window_size)
                        logger.info(f"Augmentation taille fenêtre stream {stream_id}: {config.window_size_ms}ms")
                
            except Exception as e:
                logger.error(f"Erreur fenêtrage adaptatif: {e}")
    
    # API publique
    
    def add_prediction_callback(self, stream_id: str, callback: Callable[[StreamPrediction], None]):
        """Ajoute un callback pour les prédictions"""
        self.prediction_callbacks[stream_id].append(callback)
    
    def add_window_callback(self, stream_id: str, callback: Callable[[StreamWindow], None]):
        """Ajoute un callback pour les fenêtres"""
        self.window_callbacks[stream_id].append(callback)
    
    def add_error_callback(self, callback: Callable[[Exception, Any], None]):
        """Ajoute un callback pour les erreurs"""
        self.error_callbacks.append(callback)
    
    def get_stream_metrics(self, stream_id: str) -> Optional[StreamMetrics]:
        """Récupère les métriques d'un stream"""
        return self.stream_metrics.get(stream_id)
    
    def get_global_metrics(self) -> Dict[str, Any]:
        """Récupère les métriques globales"""
        return self.global_metrics.copy()
    
    def list_streams(self) -> List[str]:
        """Liste les streams actifs"""
        return list(self.streams.keys())
    
    def get_stream_status(self, stream_id: str) -> Optional[StreamStatus]:
        """Récupère le statut d'un stream"""
        return self.stream_status.get(stream_id)
    
    async def health_check(self) -> Dict[str, Any]:
        """Vérification de santé"""
        return {
            "status": "healthy" if self.is_running else "stopped",
            "active_streams": self.global_metrics["active_streams"],
            "total_streams": len(self.streams),
            "loaded_models": sum(len(models) for models in self.models.values()),
            "prediction_tasks": len(self.prediction_tasks),
            "global_metrics": self.global_metrics
        }


# Factory pour créer des moteurs spécialisés
class StreamingEngineFactory:
    """Factory pour créer des moteurs de streaming spécialisés"""
    
    @staticmethod
    def create_audio_streaming_engine() -> StreamingInferenceEngine:
        """Moteur optimisé pour streaming audio"""
        engine = StreamingInferenceEngine(
            max_concurrent_streams=50,
            global_buffer_size=200000,
            prediction_timeout_ms=50,
            enable_adaptive_windowing=True
        )
        return engine
    
    @staticmethod
    def create_video_streaming_engine() -> StreamingInferenceEngine:
        """Moteur optimisé pour streaming vidéo"""
        engine = StreamingInferenceEngine(
            max_concurrent_streams=20,
            global_buffer_size=50000,
            prediction_timeout_ms=100,
            enable_adaptive_windowing=True
        )
        return engine
    
    @staticmethod
    def create_text_streaming_engine() -> StreamingInferenceEngine:
        """Moteur optimisé pour streaming texte"""
        engine = StreamingInferenceEngine(
            max_concurrent_streams=100,
            global_buffer_size=500000,
            prediction_timeout_ms=20,
            enable_adaptive_windowing=True
        )
        return engine
    
    @staticmethod
    def create_development_engine() -> StreamingInferenceEngine:
        """Moteur pour développement"""
        engine = StreamingInferenceEngine(
            max_concurrent_streams=10,
            global_buffer_size=10000,
            prediction_timeout_ms=1000,
            enable_adaptive_windowing=False
        )
        return engine


# Exemple d'utilisation
async def example_usage():
    """Exemple d'utilisation du moteur de streaming"""
    
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.datasets import make_classification
    import numpy as np
    
    # Créer des données d'exemple
    X, y = make_classification(n_samples=1000, n_features=10, random_state=42)
    
    # Entraîner un modèle
    model = RandomForestClassifier(n_estimators=10, random_state=42)
    model.fit(X, y)
    
    # Créer le moteur de streaming
    engine = StreamingEngineFactory.create_development_engine()
    
    # Callbacks
    async def prediction_callback(prediction: StreamPrediction):
        print(f"Prédiction reçue: {prediction.prediction} "
              f"(confiance: {prediction.confidence}, latence: {prediction.latency_ms:.2f}ms)")
    
    async def window_callback(window: StreamWindow):
        print(f"Fenêtre traitée: {window.window_id} avec {len(window.samples)} échantillons")
    
    try:
        # Démarrer le moteur
        await engine.start()
        
        # Enregistrer le modèle
        await engine.register_model("test_model", model, StreamType.SENSOR)
        
        # Créer un stream
        config = StreamConfig(
            stream_id="test_stream",
            stream_type=StreamType.SENSOR,
            window_size_ms=1000,
            window_type=WindowType.TUMBLING,
            aggregation_type=AggregationType.AVERAGE,
            buffer_size=1000
        )
        
        await engine.create_stream(config)
        
        # Ajouter les callbacks
        engine.add_prediction_callback("test_stream", prediction_callback)
        engine.add_window_callback("test_stream", window_callback)
        
        # Démarrer le stream
        await engine.start_stream("test_stream")
        
        # Simuler des données de streaming
        print("Début simulation streaming...")
        
        for i in range(50):
            # Générer des données aléatoires
            sample_data = np.random.randn(10)
            
            # Pousser l'échantillon
            success = await engine.push_sample(
                "test_stream",
                sample_data,
                {"sample_index": i}
            )
            
            if not success:
                print(f"Échec push échantillon {i}")
            
            # Petite pause pour simuler le streaming
            await asyncio.sleep(0.1)
        
        # Attendre un peu pour le traitement final
        await asyncio.sleep(2.0)
        
        # Afficher les métriques
        metrics = engine.get_stream_metrics("test_stream")
        if metrics:
            print(f"\nMétriques stream:")
            print(f"- Échantillons reçus: {metrics.samples_received}")
            print(f"- Échantillons traités: {metrics.samples_processed}")
            print(f"- Prédictions: {metrics.predictions_made}")
            print(f"- Latence moyenne: {metrics.average_latency_ms:.2f}ms")
            print(f"- Throughput: {metrics.throughput_samples_per_second:.1f} samples/s")
            print(f"- Utilisation buffer: {metrics.buffer_utilization:.1%}")
        
        global_metrics = engine.get_global_metrics()
        print(f"\nMétriques globales: {global_metrics}")
        
        # Santé du système
        health = await engine.health_check()
        print(f"\nSanté système: {health}")
        
    finally:
        # Arrêter le moteur
        await engine.stop()


if __name__ == "__main__":
    asyncio.run(example_usage())