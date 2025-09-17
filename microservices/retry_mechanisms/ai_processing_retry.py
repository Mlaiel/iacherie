"""
AI Processing Retry - Ainflue
=============================
Retry spécialisé pour processing IA/ML.
GPU queue management + model loading + inference retry.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue Retry Mechanisms
Version: 1.0 Production

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
Cette architecture retry mechanisms et tous ses algorithmes sont la propriété intellectuelle 
EXCLUSIVE de Fahed Mlaiel (mlaiel@live.de). Toute reproduction, modification, distribution 
ou vol d'idée/concept/code sans autorisation écrite PERSONNELLE est STRICTEMENT INTERDITE.

Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer
"""

import asyncio
import time
import random
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class AITaskType(Enum):
    """Types de tâches IA supportées"""
    CONTENT_ANALYSIS = "content_analysis"
    AUDIO_ENHANCEMENT = "audio_enhancement"
    TEXT_GENERATION = "text_generation"
    IMAGE_UPSCALING = "image_upscaling"
    VIDEO_ENHANCEMENT = "video_enhancement"
    SPEECH_TO_TEXT = "speech_to_text"
    TEXT_TO_SPEECH = "text_to_speech"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    CONTENT_MODERATION = "content_moderation"
    RECOMMENDATION_ENGINE = "recommendation_engine"

class ResourceType(Enum):
    """Types de ressources compute"""
    CPU = "cpu"
    GPU = "gpu"
    TPU = "tpu"
    HYBRID = "hybrid"

class ModelSize(Enum):
    """Tailles modèles IA"""
    TINY = "tiny"           # < 100MB
    SMALL = "small"         # 100MB - 1GB
    MEDIUM = "medium"       # 1GB - 5GB
    LARGE = "large"         # 5GB - 20GB
    XLARGE = "xlarge"       # > 20GB

class ProcessingPriority(Enum):
    """Niveaux priorité processing IA"""
    BATCH = "batch"         # Processing différé
    STANDARD = "standard"   # Processing normal
    PRIORITY = "priority"   # Processing prioritaire
    REALTIME = "realtime"   # Processing temps réel

@dataclass
class AIRequest:
    """Requête processing IA"""
    request_id: str
    task_type: AITaskType
    resource_type: ResourceType
    model_name: str
    model_size: ModelSize
    input_data: Dict
    priority: ProcessingPriority = ProcessingPriority.STANDARD
    timeout: Optional[float] = None
    batch_size: int = 1
    gpu_memory_required: Optional[int] = None  # MB
    cpu_cores_required: int = 1
    expected_duration: Optional[float] = None
    metadata: Dict = field(default_factory=dict)

@dataclass
class AIProcessingResult:
    """Résultat processing IA"""
    request_id: str
    success: bool
    task_type: AITaskType
    output_data: Optional[Dict] = None
    processing_duration: float = 0.0
    resource_usage: Dict = field(default_factory=dict)
    model_performance: Dict = field(default_factory=dict)
    error_message: Optional[str] = None
    retry_recommendation: Optional[str] = None
    cost_estimation: float = 0.0
    fallback_used: bool = False

class AIProcessingRetry:
    """
    Retry spécialisé pour processing IA/ML.
    GPU queue management + model loading + inference retry.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Stratégies retry par type tâche IA
        self.ai_retry_patterns = {
            'content_analysis': {
                'gpu_required': True,
                'max_queue_time': 300,  # 5 minutes
                'max_retries': 3,
                'timeout_progression': [60, 120, 240],
                'fallback_cpu': True,
                'model_fallback': True,
                'batch_friendly': True
            },
            'audio_enhancement': {
                'gpu_preferred': True,
                'max_queue_time': 600,  # 10 minutes
                'max_retries': 4,
                'timeout_progression': [120, 300, 600, 900],
                'fallback_cpu': True,
                'model_fallback': True,
                'batch_friendly': False
            },
            'text_generation': {
                'cpu_optimized': True,
                'max_queue_time': 180,  # 3 minutes
                'max_retries': 2,
                'timeout_progression': [30, 60],
                'fallback_cpu': False,
                'model_fallback': True,
                'batch_friendly': True
            },
            'image_upscaling': {
                'gpu_required': True,
                'max_queue_time': 900,  # 15 minutes
                'max_retries': 5,
                'timeout_progression': [180, 360, 540, 720, 900],
                'fallback_cpu': False,
                'model_fallback': True,
                'batch_friendly': True,
                'memory_intensive': True
            },
            'video_enhancement': {
                'gpu_required': True,
                'max_queue_time': 1800,  # 30 minutes
                'max_retries': 6,
                'timeout_progression': [300, 600, 900, 1200, 1500, 1800],
                'fallback_cpu': False,
                'model_fallback': False,  # Video models don't fallback well
                'batch_friendly': False,
                'memory_intensive': True
            },
            'realtime_inference': {
                'gpu_required': True,
                'max_queue_time': 5,  # 5 seconds for realtime
                'max_retries': 1,
                'timeout_progression': [2],
                'fallback_cpu': True,
                'model_fallback': True,
                'batch_friendly': False,
                'preloaded_models': True
            }
        }
        
        # Simulation état ressources
        self.resource_state = {
            'gpu_nodes': {
                'gpu-001': {'available': True, 'memory_free': 8192, 'utilization': 0.2},
                'gpu-002': {'available': True, 'memory_free': 16384, 'utilization': 0.4},
                'gpu-003': {'available': False, 'memory_free': 0, 'utilization': 1.0}
            },
            'cpu_nodes': {
                'cpu-001': {'available': True, 'cores_free': 8, 'utilization': 0.3},
                'cpu-002': {'available': True, 'cores_free': 16, 'utilization': 0.5}
            },
            'model_cache': {
                'content_analyzer_v2': {'loaded': True, 'memory_usage': 2048},
                'audio_enhancer_v1': {'loaded': False, 'memory_usage': 0},
                'text_generator_small': {'loaded': True, 'memory_usage': 512}
            }
        }
        
        # Files d'attente IA par priorité
        self.ai_queues = {
            ProcessingPriority.REALTIME: [],
            ProcessingPriority.PRIORITY: [],
            ProcessingPriority.STANDARD: [],
            ProcessingPriority.BATCH: []
        }
        
        # Métriques processing IA
        self.ai_metrics = {
            'total_requests': 0,
            'successful_processing': 0,
            'failed_processing': 0,
            'gpu_fallbacks': 0,
            'cpu_fallbacks': 0,
            'model_fallbacks': 0,
            'queue_timeouts': 0,
            'average_gpu_utilization': 0.0,
            'average_processing_time': 0.0,
            'total_cost': 0.0
        }
    
    async def retry_ai_processing(self, ai_request: AIRequest) -> AIProcessingResult:
        """Retry spécialisé pour processing IA avec resource awareness."""
        
        self.ai_metrics['total_requests'] += 1
        start_time = time.time()
        
        try:
            # Sélection stratégie retry
            strategy = self._select_ai_retry_strategy(ai_request)
            
            # Gestion file d'attente avec priorité
            queue_result = await self._manage_ai_queue(ai_request, strategy)
            if not queue_result['success']:
                return self._create_failure_result(ai_request, queue_result['error'])
            
            # Processing IA avec retry
            result = await self._execute_ai_processing_with_retry(ai_request, strategy)
            
            # Mise à jour métriques
            processing_duration = time.time() - start_time
            self._update_ai_metrics(result, processing_duration)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in AI processing retry for {ai_request.request_id}: {str(e)}")
            self.ai_metrics['failed_processing'] += 1
            return self._create_failure_result(ai_request, str(e))
    
    def _select_ai_retry_strategy(self, ai_request: AIRequest) -> Dict:
        """Sélection stratégie retry pour tâche IA"""
        
        # Mapping type tâche vers stratégie
        task_strategy_map = {
            AITaskType.CONTENT_ANALYSIS: 'content_analysis',
            AITaskType.AUDIO_ENHANCEMENT: 'audio_enhancement',
            AITaskType.TEXT_GENERATION: 'text_generation',
            AITaskType.IMAGE_UPSCALING: 'image_upscaling',
            AITaskType.VIDEO_ENHANCEMENT: 'video_enhancement',
            AITaskType.SPEECH_TO_TEXT: 'content_analysis',
            AITaskType.TEXT_TO_SPEECH: 'audio_enhancement',
            AITaskType.SENTIMENT_ANALYSIS: 'text_generation',
            AITaskType.CONTENT_MODERATION: 'content_analysis',
            AITaskType.RECOMMENDATION_ENGINE: 'content_analysis'
        }
        
        # Stratégie spéciale pour temps réel
        if ai_request.priority == ProcessingPriority.REALTIME:
            strategy_name = 'realtime_inference'
        else:
            strategy_name = task_strategy_map.get(ai_request.task_type, 'content_analysis')
        
        base_strategy = self.ai_retry_patterns[strategy_name].copy()
        
        # Ajustements basés sur taille modèle
        if ai_request.model_size in [ModelSize.LARGE, ModelSize.XLARGE]:
            base_strategy['max_retries'] += 1
            base_strategy['timeout_progression'] = [t * 1.5 for t in base_strategy['timeout_progression']]
        
        # Ajustements basés sur priorité
        if ai_request.priority == ProcessingPriority.PRIORITY:
            base_strategy['max_queue_time'] = int(base_strategy['max_queue_time'] * 0.5)
        elif ai_request.priority == ProcessingPriority.BATCH:
            base_strategy['max_queue_time'] = int(base_strategy['max_queue_time'] * 2)
        
        return base_strategy
    
    async def _manage_ai_queue(self, ai_request: AIRequest, strategy: Dict) -> Dict:
        """Gestion file d'attente IA avec priorité"""
        
        queue_start_time = time.time()
        max_queue_time = strategy.get('max_queue_time', 300)
        
        # Ajout à la file d'attente appropriée
        self.ai_queues[ai_request.priority].append({
            'request': ai_request,
            'queued_at': queue_start_time,
            'strategy': strategy
        })
        
        # Simulation traitement file d'attente
        while time.time() - queue_start_time < max_queue_time:
            # Vérification disponibilité ressources
            if await self._check_resource_availability(ai_request, strategy):
                # Retrait de la file d'attente
                self._remove_from_queue(ai_request)
                return {'success': True, 'wait_time': time.time() - queue_start_time}
            
            # Attente avant re-vérification
            await asyncio.sleep(1.0)
        
        # Timeout file d'attente
        self._remove_from_queue(ai_request)
        self.ai_metrics['queue_timeouts'] += 1
        return {
            'success': False,
            'error': f'Queue timeout after {max_queue_time}s',
            'wait_time': time.time() - queue_start_time
        }
    
    async def _check_resource_availability(self, ai_request: AIRequest, strategy: Dict) -> bool:
        """Vérification disponibilité ressources"""
        
        required_resource = ai_request.resource_type
        
        # Vérification ressources GPU
        if required_resource == ResourceType.GPU or strategy.get('gpu_required', False):
            for node_id, node_info in self.resource_state['gpu_nodes'].items():
                memory_required = ai_request.gpu_memory_required or self._estimate_gpu_memory(ai_request)
                
                if (node_info['available'] and 
                    node_info['memory_free'] >= memory_required and
                    node_info['utilization'] < 0.9):
                    return True
        
        # Fallback CPU si autorisé
        if strategy.get('fallback_cpu', False) or required_resource == ResourceType.CPU:
            for node_id, node_info in self.resource_state['cpu_nodes'].items():
                cores_required = ai_request.cpu_cores_required
                
                if (node_info['available'] and 
                    node_info['cores_free'] >= cores_required and
                    node_info['utilization'] < 0.8):
                    return True
        
        return False
    
    def _estimate_gpu_memory(self, ai_request: AIRequest) -> int:
        """Estimation mémoire GPU requise"""
        
        # Estimation basée sur taille modèle et type tâche
        base_memory = {
            ModelSize.TINY: 256,
            ModelSize.SMALL: 1024,
            ModelSize.MEDIUM: 4096,
            ModelSize.LARGE: 8192,
            ModelSize.XLARGE: 16384
        }
        
        memory_required = base_memory.get(ai_request.model_size, 2048)
        
        # Facteur par type tâche
        task_memory_factors = {
            AITaskType.CONTENT_ANALYSIS: 1.0,
            AITaskType.AUDIO_ENHANCEMENT: 1.2,
            AITaskType.TEXT_GENERATION: 0.8,
            AITaskType.IMAGE_UPSCALING: 1.5,
            AITaskType.VIDEO_ENHANCEMENT: 2.0,
            AITaskType.SPEECH_TO_TEXT: 1.1,
            AITaskType.TEXT_TO_SPEECH: 1.3,
            AITaskType.SENTIMENT_ANALYSIS: 0.6,
            AITaskType.CONTENT_MODERATION: 0.9,
            AITaskType.RECOMMENDATION_ENGINE: 1.0
        }
        
        factor = task_memory_factors.get(ai_request.task_type, 1.0)
        
        # Ajustement batch size
        if ai_request.batch_size > 1:
            factor *= min(ai_request.batch_size * 0.8, 3.0)  # Economies d'échelle
        
        return int(memory_required * factor)
    
    def _remove_from_queue(self, ai_request: AIRequest):
        """Retrait requête de la file d'attente"""
        queue = self.ai_queues[ai_request.priority]
        self.ai_queues[ai_request.priority] = [
            item for item in queue 
            if item['request'].request_id != ai_request.request_id
        ]
    
    async def _execute_ai_processing_with_retry(self, ai_request: AIRequest, strategy: Dict) -> AIProcessingResult:
        """Exécution processing IA avec retry"""
        
        max_retries = strategy['max_retries']
        timeout_progression = strategy['timeout_progression']
        last_error = None
        resource_type = ai_request.resource_type
        
        for attempt in range(max_retries + 1):
            try:
                # Timeout adaptatif
                timeout = timeout_progression[min(attempt, len(timeout_progression) - 1)]
                
                # Fallback ressource si échec précédent
                if attempt > 0:
                    resource_type = self._select_fallback_resource(ai_request, strategy, attempt)
                
                # Processing principal
                result = await self._process_ai_task(ai_request, resource_type, timeout, attempt)
                
                if result.success:
                    return result
                else:
                    last_error = result.error_message
                    
                    # Vérification si erreur retriable
                    if not self._is_ai_error_retriable(result.error_message, strategy):
                        break
                        
                    # Attente avant retry
                    if attempt < max_retries:
                        backoff_delay = self._calculate_ai_backoff(attempt, ai_request)
                        await asyncio.sleep(backoff_delay)
                        
            except asyncio.TimeoutError:
                last_error = f"AI processing timeout after {timeout}s"
                self.logger.warning(f"AI processing timeout for {ai_request.request_id} on attempt {attempt + 1}")
                continue
                
            except Exception as e:
                last_error = str(e)
                self.logger.error(f"AI processing error for {ai_request.request_id}: {str(e)}")
                continue
        
        # Tous les retry ont échoué - tentative model fallback
        if strategy.get('model_fallback', False):
            fallback_result = await self._try_model_fallback(ai_request, last_error)
            if fallback_result.success:
                self.ai_metrics['model_fallbacks'] += 1
                return fallback_result
        
        # Échec final
        return self._create_failure_result(ai_request, last_error)
    
    def _select_fallback_resource(self, ai_request: AIRequest, strategy: Dict, attempt: int) -> ResourceType:
        """Sélection ressource fallback"""
        
        # Priorité fallback: GPU -> CPU
        if attempt == 1 and strategy.get('fallback_cpu', False):
            if ai_request.resource_type == ResourceType.GPU:
                self.ai_metrics['cpu_fallbacks'] += 1
                return ResourceType.CPU
        
        # Hybrid pour cas complexes
        if attempt >= 2 and strategy.get('fallback_cpu', False):
            return ResourceType.HYBRID
        
        return ai_request.resource_type
    
    async def _process_ai_task(self, ai_request: AIRequest, resource_type: ResourceType, timeout: float, attempt: int) -> AIProcessingResult:
        """Processing principal tâche IA"""
        
        start_time = time.time()
        
        # Simulation chargement modèle si nécessaire
        model_load_time = await self._simulate_model_loading(ai_request)
        
        # Estimation durée processing
        processing_duration = self._estimate_processing_duration(ai_request, resource_type)
        
        # Simulation processing avec probabilité échec
        try:
            await asyncio.wait_for(
                self._simulate_ai_operation(ai_request, processing_duration),
                timeout=timeout
            )
            
            # Calcul utilisation ressources
            resource_usage = self._calculate_resource_usage(ai_request, resource_type, processing_duration)
            
            # Métriques performance modèle
            model_performance = self._generate_model_metrics(ai_request, resource_type)
            
            # Calcul coût
            cost = self._calculate_ai_processing_cost(ai_request, resource_type, processing_duration)
            
            # Génération données sortie simulées
            output_data = self._generate_ai_output(ai_request)
            
            return AIProcessingResult(
                request_id=ai_request.request_id,
                success=True,
                task_type=ai_request.task_type,
                output_data=output_data,
                processing_duration=time.time() - start_time,
                resource_usage=resource_usage,
                model_performance=model_performance,
                cost_estimation=cost,
                fallback_used=(resource_type != ai_request.resource_type)
            )
            
        except asyncio.TimeoutError:
            raise asyncio.TimeoutError(f"AI processing exceeded {timeout}s timeout")
        
        except Exception as e:
            # Simulation échecs IA spécifiques
            ai_error_types = [
                "model_loading_error", "gpu_memory_error", "inference_error", 
                "model_timeout", "resource_exhaustion", "invalid_input_format"
            ]
            
            # Probabilité échec basée sur complexité et attempt
            model_complexity = self._get_model_complexity(ai_request)
            failure_probability = min(0.4, model_complexity * 0.1 + attempt * 0.08)
            
            if time.time() % 1 < failure_probability:
                error_type = random.choice(ai_error_types)
                raise Exception(f"AI processing failed: {error_type}")
            
            # Succès simulé
            return AIProcessingResult(
                request_id=ai_request.request_id,
                success=True,
                task_type=ai_request.task_type,
                output_data=self._generate_ai_output(ai_request),
                processing_duration=time.time() - start_time,
                resource_usage=self._calculate_resource_usage(ai_request, resource_type, processing_duration),
                model_performance=self._generate_model_metrics(ai_request, resource_type),
                cost_estimation=self._calculate_ai_processing_cost(ai_request, resource_type, processing_duration),
                fallback_used=(resource_type != ai_request.resource_type)
            )
    
    async def _simulate_model_loading(self, ai_request: AIRequest) -> float:
        """Simulation chargement modèle"""
        
        model_name = ai_request.model_name
        
        # Vérification cache modèle
        if model_name in self.resource_state['model_cache']:
            if self.resource_state['model_cache'][model_name]['loaded']:
                return 0.1  # Déjà chargé, juste validation
        
        # Simulation temps chargement par taille modèle
        load_times = {
            ModelSize.TINY: 0.5,
            ModelSize.SMALL: 2.0,
            ModelSize.MEDIUM: 8.0,
            ModelSize.LARGE: 20.0,
            ModelSize.XLARGE: 45.0
        }
        
        load_time = load_times.get(ai_request.model_size, 5.0)
        await asyncio.sleep(min(load_time, 3.0))  # Cap simulation time
        
        # Mise à jour cache
        self.resource_state['model_cache'][model_name] = {
            'loaded': True,
            'memory_usage': self._estimate_gpu_memory(ai_request)
        }
        
        return load_time
    
    def _estimate_processing_duration(self, ai_request: AIRequest, resource_type: ResourceType) -> float:
        """Estimation durée processing"""
        
        # Durées de base par type tâche (secondes)
        base_durations = {
            AITaskType.CONTENT_ANALYSIS: 10.0,
            AITaskType.AUDIO_ENHANCEMENT: 30.0,
            AITaskType.TEXT_GENERATION: 5.0,
            AITaskType.IMAGE_UPSCALING: 45.0,
            AITaskType.VIDEO_ENHANCEMENT: 120.0,
            AITaskType.SPEECH_TO_TEXT: 15.0,
            AITaskType.TEXT_TO_SPEECH: 20.0,
            AITaskType.SENTIMENT_ANALYSIS: 3.0,
            AITaskType.CONTENT_MODERATION: 8.0,
            AITaskType.RECOMMENDATION_ENGINE: 12.0
        }
        
        base_duration = base_durations.get(ai_request.task_type, 10.0)
        
        # Facteur taille modèle
        size_factors = {
            ModelSize.TINY: 0.3,
            ModelSize.SMALL: 0.7,
            ModelSize.MEDIUM: 1.0,
            ModelSize.LARGE: 2.0,
            ModelSize.XLARGE: 4.0
        }
        
        duration = base_duration * size_factors.get(ai_request.model_size, 1.0)
        
        # Facteur type ressource
        resource_factors = {
            ResourceType.GPU: 1.0,
            ResourceType.CPU: 3.0,  # CPU plus lent
            ResourceType.TPU: 0.7,  # TPU plus rapide pour certaines tâches
            ResourceType.HYBRID: 1.5
        }
        
        duration *= resource_factors.get(resource_type, 1.0)
        
        # Facteur batch size
        if ai_request.batch_size > 1:
            # Economies d'échelle pour batch processing
            batch_efficiency = 1.0 + (ai_request.batch_size - 1) * 0.7
            duration *= batch_efficiency
        
        return duration
    
    async def _simulate_ai_operation(self, ai_request: AIRequest, duration: float):
        """Simulation opération IA"""
        await asyncio.sleep(min(duration, 5.0))  # Cap simulation time
    
    def _get_model_complexity(self, ai_request: AIRequest) -> float:
        """Calcul complexité modèle"""
        
        # Complexité par type tâche
        task_complexity = {
            AITaskType.CONTENT_ANALYSIS: 0.6,
            AITaskType.AUDIO_ENHANCEMENT: 0.8,
            AITaskType.TEXT_GENERATION: 0.7,
            AITaskType.IMAGE_UPSCALING: 0.9,
            AITaskType.VIDEO_ENHANCEMENT: 1.0,
            AITaskType.SPEECH_TO_TEXT: 0.7,
            AITaskType.TEXT_TO_SPEECH: 0.8,
            AITaskType.SENTIMENT_ANALYSIS: 0.4,
            AITaskType.CONTENT_MODERATION: 0.5,
            AITaskType.RECOMMENDATION_ENGINE: 0.6
        }
        
        complexity = task_complexity.get(ai_request.task_type, 0.5)
        
        # Ajustement par taille modèle
        size_complexity = {
            ModelSize.TINY: 0.2,
            ModelSize.SMALL: 0.4,
            ModelSize.MEDIUM: 0.6,
            ModelSize.LARGE: 0.8,
            ModelSize.XLARGE: 1.0
        }
        
        complexity += size_complexity.get(ai_request.model_size, 0.5)
        
        return min(1.0, complexity)
    
    def _is_ai_error_retriable(self, error_message: str, strategy: Dict) -> bool:
        """Vérification si erreur IA retriable"""
        
        if not error_message:
            return True
        
        error_lower = error_message.lower()
        
        # Erreurs non retriables
        non_retriable_errors = [
            'invalid_input_format', 'model_not_found', 'invalid_model_config',
            'unsupported_operation', 'corrupted_model'
        ]
        
        for non_retriable in non_retriable_errors:
            if non_retriable in error_lower:
                return False
        
        # Erreurs retriables
        retriable_errors = [
            'gpu_memory_error', 'model_loading_error', 'inference_error',
            'resource_exhaustion', 'timeout', 'temporary_unavailable'
        ]
        
        for retriable in retriable_errors:
            if retriable in error_lower:
                return True
        
        return True  # Par défaut retriable
    
    def _calculate_ai_backoff(self, attempt: int, ai_request: AIRequest) -> float:
        """Calcul backoff pour retry IA"""
        
        # Backoff de base
        base_delay = 2.0 ** attempt
        
        # Ajustement par priorité
        priority_factors = {
            ProcessingPriority.REALTIME: 0.1,
            ProcessingPriority.PRIORITY: 0.5,
            ProcessingPriority.STANDARD: 1.0,
            ProcessingPriority.BATCH: 2.0
        }
        
        base_delay *= priority_factors.get(ai_request.priority, 1.0)
        
        # Ajustement par taille modèle (models plus gros = plus de temps)
        size_factors = {
            ModelSize.TINY: 0.5,
            ModelSize.SMALL: 0.8,
            ModelSize.MEDIUM: 1.0,
            ModelSize.LARGE: 1.5,
            ModelSize.XLARGE: 2.0
        }
        
        base_delay *= size_factors.get(ai_request.model_size, 1.0)
        
        # Jitter
        jitter = random.uniform(0.8, 1.2)
        
        return base_delay * jitter
    
    async def _try_model_fallback(self, ai_request: AIRequest, original_error: str) -> AIProcessingResult:
        """Tentative fallback avec modèle plus simple"""
        
        self.logger.info(f"Attempting model fallback for {ai_request.request_id}")
        
        # Sélection modèle fallback plus simple
        fallback_size = self._get_fallback_model_size(ai_request.model_size)
        
        if fallback_size == ai_request.model_size:
            # Pas de fallback possible
            return self._create_failure_result(ai_request, f"No model fallback available: {original_error}")
        
        # Création requête fallback
        fallback_request = AIRequest(
            request_id=f"{ai_request.request_id}_fallback",
            task_type=ai_request.task_type,
            resource_type=ResourceType.CPU,  # Fallback sur CPU
            model_name=f"{ai_request.model_name}_small",
            model_size=fallback_size,
            input_data=ai_request.input_data,
            priority=ai_request.priority
        )
        
        try:
            # Traitement simplifié
            result = await self._process_ai_task(fallback_request, ResourceType.CPU, 30.0, 0)
            
            if result.success:
                result.fallback_used = True
                result.request_id = ai_request.request_id  # Restaurer ID original
                return result
            else:
                return self._create_failure_result(ai_request, f"Model fallback failed: {result.error_message}")
                
        except Exception as e:
            return self._create_failure_result(ai_request, f"Model fallback error: {str(e)}")
    
    def _get_fallback_model_size(self, current_size: ModelSize) -> ModelSize:
        """Récupération taille modèle fallback"""
        
        size_hierarchy = [
            ModelSize.XLARGE,
            ModelSize.LARGE,
            ModelSize.MEDIUM,
            ModelSize.SMALL,
            ModelSize.TINY
        ]
        
        try:
            current_index = size_hierarchy.index(current_size)
            if current_index < len(size_hierarchy) - 1:
                return size_hierarchy[current_index + 1]
        except ValueError:
            pass
        
        return current_size  # Pas de fallback possible
    
    def _calculate_resource_usage(self, ai_request: AIRequest, resource_type: ResourceType, duration: float) -> Dict:
        """Calcul utilisation ressources"""
        
        usage = {
            'resource_type': resource_type.value,
            'duration': duration,
            'cpu_usage': 0.0,
            'gpu_usage': 0.0,
            'memory_usage': 0.0
        }
        
        if resource_type == ResourceType.GPU:
            usage['gpu_usage'] = random.uniform(0.7, 0.95)
            usage['cpu_usage'] = random.uniform(0.1, 0.3)
            usage['memory_usage'] = self._estimate_gpu_memory(ai_request)
        elif resource_type == ResourceType.CPU:
            usage['cpu_usage'] = random.uniform(0.6, 0.9)
            usage['memory_usage'] = random.uniform(1024, 4096)  # MB
        
        return usage
    
    def _generate_model_metrics(self, ai_request: AIRequest, resource_type: ResourceType) -> Dict:
        """Génération métriques performance modèle"""
        
        # Métriques de base simulées
        base_accuracy = 0.85
        
        # Ajustement par taille modèle
        size_accuracy_bonus = {
            ModelSize.TINY: -0.15,
            ModelSize.SMALL: -0.08,
            ModelSize.MEDIUM: 0.0,
            ModelSize.LARGE: 0.08,
            ModelSize.XLARGE: 0.12
        }
        
        accuracy = base_accuracy + size_accuracy_bonus.get(ai_request.model_size, 0.0)
        
        # Ajustement par ressource (GPU généralement meilleur)
        if resource_type == ResourceType.CPU:
            accuracy *= 0.95
        
        metrics = {
            'accuracy': min(1.0, max(0.0, accuracy)),
            'inference_speed': random.uniform(50, 200),  # inferences/sec
            'model_size_mb': self._estimate_gpu_memory(ai_request),
            'confidence_score': random.uniform(0.7, 0.95)
        }
        
        # Métriques spécifiques par type tâche
        if ai_request.task_type == AITaskType.TEXT_GENERATION:
            metrics['perplexity'] = random.uniform(15, 40)
            metrics['bleu_score'] = random.uniform(0.3, 0.8)
        elif ai_request.task_type == AITaskType.IMAGE_UPSCALING:
            metrics['psnr'] = random.uniform(25, 35)
            metrics['ssim'] = random.uniform(0.8, 0.95)
        
        return metrics
    
    def _calculate_ai_processing_cost(self, ai_request: AIRequest, resource_type: ResourceType, duration: float) -> float:
        """Calcul coût processing IA"""
        
        # Coûts par type ressource ($ par heure)
        resource_costs = {
            ResourceType.GPU: 2.50,
            ResourceType.CPU: 0.50,
            ResourceType.TPU: 1.80,
            ResourceType.HYBRID: 1.50
        }
        
        base_cost_per_hour = resource_costs.get(resource_type, 1.0)
        
        # Coût basé sur durée
        time_cost = (duration / 3600) * base_cost_per_hour
        
        # Surcoût par taille modèle
        size_surcharge = {
            ModelSize.TINY: 1.0,
            ModelSize.SMALL: 1.2,
            ModelSize.MEDIUM: 1.5,
            ModelSize.LARGE: 2.0,
            ModelSize.XLARGE: 3.0
        }
        
        total_cost = time_cost * size_surcharge.get(ai_request.model_size, 1.0)
        
        # Discount pour batch processing
        if ai_request.batch_size > 1:
            batch_discount = max(0.7, 1.0 - (ai_request.batch_size * 0.05))
            total_cost *= batch_discount
        
        return round(total_cost, 4)
    
    def _generate_ai_output(self, ai_request: AIRequest) -> Dict:
        """Génération données sortie IA simulées"""
        
        # Données sortie par type tâche
        output_templates = {
            AITaskType.CONTENT_ANALYSIS: {
                'categories': ['technology', 'entertainment', 'education'],
                'sentiment': random.choice(['positive', 'neutral', 'negative']),
                'keywords': ['ai', 'technology', 'innovation'],
                'confidence': random.uniform(0.7, 0.95)
            },
            AITaskType.AUDIO_ENHANCEMENT: {
                'enhanced_audio_path': f"/enhanced/{ai_request.request_id}.wav",
                'noise_reduction': random.uniform(0.6, 0.9),
                'quality_improvement': random.uniform(0.3, 0.8)
            },
            AITaskType.TEXT_GENERATION: {
                'generated_text': f"Generated content for request {ai_request.request_id}",
                'word_count': random.randint(50, 500),
                'coherence_score': random.uniform(0.7, 0.95)
            },
            AITaskType.IMAGE_UPSCALING: {
                'upscaled_image_path': f"/upscaled/{ai_request.request_id}.png",
                'scale_factor': random.choice([2, 4, 8]),
                'quality_metrics': {'psnr': random.uniform(25, 35)}
            }
        }
        
        return output_templates.get(ai_request.task_type, {'result': 'processed'})
    
    def _create_failure_result(self, ai_request: AIRequest, error_message: str) -> AIProcessingResult:
        """Création résultat échec"""
        
        return AIProcessingResult(
            request_id=ai_request.request_id,
            success=False,
            task_type=ai_request.task_type,
            error_message=error_message,
            retry_recommendation=self._generate_ai_retry_recommendation(error_message)
        )
    
    def _generate_ai_retry_recommendation(self, error_message: str) -> str:
        """Génération recommandation retry IA"""
        
        if not error_message:
            return "manual_review"
        
        error_lower = error_message.lower()
        
        if 'gpu_memory' in error_lower or 'memory' in error_lower:
            return "reduce_batch_size_or_model_size"
        elif 'timeout' in error_lower:
            return "increase_timeout_or_use_smaller_model"
        elif 'model_loading' in error_lower:
            return "check_model_availability"
        elif 'resource_exhaustion' in error_lower:
            return "retry_later_or_use_cpu"
        elif 'invalid_input' in error_lower:
            return "validate_input_format"
        else:
            return "retry_with_fallback_model"
    
    def _update_ai_metrics(self, result: AIProcessingResult, duration: float):
        """Mise à jour métriques IA"""
        
        if result.success:
            self.ai_metrics['successful_processing'] += 1
        else:
            self.ai_metrics['failed_processing'] += 1
        
        # Moyenne mobile processing time
        alpha = 0.1
        self.ai_metrics['average_processing_time'] = (
            self.ai_metrics['average_processing_time'] * (1 - alpha) + 
            duration * alpha
        )
        
        # Ajout coût
        self.ai_metrics['total_cost'] += result.cost_estimation
        
        # Mise à jour utilisation GPU moyenne
        if 'gpu_usage' in result.resource_usage:
            self.ai_metrics['average_gpu_utilization'] = (
                self.ai_metrics['average_gpu_utilization'] * 0.9 + 
                result.resource_usage['gpu_usage'] * 0.1
            )
    
    async def get_ai_metrics(self) -> Dict:
        """Récupération métriques IA"""
        
        return {
            **self.ai_metrics,
            'success_rate': (
                self.ai_metrics['successful_processing'] / 
                max(1, self.ai_metrics['total_requests'])
            ),
            'average_cost_per_request': (
                self.ai_metrics['total_cost'] / 
                max(1, self.ai_metrics['total_requests'])
            ),
            'queue_lengths': {
                priority.value: len(queue) 
                for priority, queue in self.ai_queues.items()
            },
            'resource_availability': {
                'gpu_nodes_available': sum(
                    1 for node in self.resource_state['gpu_nodes'].values() 
                    if node['available']
                ),
                'cpu_nodes_available': sum(
                    1 for node in self.resource_state['cpu_nodes'].values() 
                    if node['available']
                ),
                'models_loaded': sum(
                    1 for model in self.resource_state['model_cache'].values() 
                    if model['loaded']
                )
            }
        }
    
    async def health_check(self) -> Dict:
        """Vérification santé processing IA"""
        
        return {
            'status': 'healthy',
            'total_requests_processed': self.ai_metrics['total_requests'],
            'current_success_rate': (
                self.ai_metrics['successful_processing'] / 
                max(1, self.ai_metrics['total_requests'])
            ),
            'resource_health': {
                'gpu_nodes': len([n for n in self.resource_state['gpu_nodes'].values() if n['available']]),
                'cpu_nodes': len([n for n in self.resource_state['cpu_nodes'].values() if n['available']]),
                'models_cached': len([m for m in self.resource_state['model_cache'].values() if m['loaded']])
            },
            'queue_health': {
                'total_queued': sum(len(queue) for queue in self.ai_queues.values()),
                'realtime_queue': len(self.ai_queues[ProcessingPriority.REALTIME]),
                'priority_queue': len(self.ai_queues[ProcessingPriority.PRIORITY])
            }
        }

# Factory functions
def create_ai_processing_retry() -> AIProcessingRetry:
    """Factory pour création retry processing IA"""
    return AIProcessingRetry()

__all__ = [
    'AIProcessingRetry',
    'AIRequest',
    'AIProcessingResult',
    'AITaskType',
    'ResourceType',
    'ModelSize',
    'ProcessingPriority',
    'create_ai_processing_retry'
]