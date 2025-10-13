"""
Content Processing Retry - IA Chérie
==================================
Retry spécialisé pour processing contenu IA Chérie.
Media processing + AI analysis + upload retry patterns.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: IA Chérie Retry Mechanisms
Version: 1.0 Production

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
Cette architecture retry mechanisms et tous ses algorithmes sont la propriété intellectuelle 
EXCLUSIVE de Fahed Mlaiel (mlaiel@live.de). Toute reproduction, modification, distribution 
ou vol d'idée/concept/code sans autorisation écrite PERSONNELLE est STRICTEMENT INTERDITE.

Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer
"""

import asyncio
import time
import hashlib
import math
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class MediaType(Enum):
    """Types de média supportés"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    MIXED = "mixed"

class ProcessingStage(Enum):
    """Étapes processing contenu"""
    UPLOAD = "upload"
    VALIDATION = "validation"
    TRANSCODING = "transcoding"
    ENHANCEMENT = "enhancement"
    ANALYSIS = "analysis"
    THUMBNAIL_GENERATION = "thumbnail_generation"
    METADATA_EXTRACTION = "metadata_extraction"
    QUALITY_CHECK = "quality_check"
    STORAGE = "storage"
    INDEXING = "indexing"

class ContentQuality(Enum):
    """Niveaux qualité contenu"""
    ULTRA_HD = "ultra_hd"      # 4K+
    HD = "hd"                  # 1080p
    STANDARD = "standard"      # 720p
    BASIC = "basic"            # 480p
    LOW = "low"                # 360p

@dataclass
class ContentRequest:
    """Requête processing contenu"""
    content_id: str
    media_type: MediaType
    processing_stage: ProcessingStage
    file_size: int  # bytes
    content_duration: Optional[float] = None  # seconds for audio/video
    target_quality: ContentQuality = ContentQuality.HD
    creator_id: str = ""
    priority: int = 3  # 1=low, 5=critical
    metadata: Dict = field(default_factory=dict)
    upload_session_id: Optional[str] = None
    chunk_info: Dict = field(default_factory=dict)  # For chunked uploads

@dataclass
class ProcessingResult:
    """Résultat processing contenu"""
    content_id: str
    success: bool
    processing_stage: ProcessingStage
    processed_file_path: Optional[str] = None
    processing_duration: float = 0.0
    quality_metrics: Dict = field(default_factory=dict)
    error_message: Optional[str] = None
    retry_recommendation: Optional[str] = None
    fallback_applied: bool = False
    cost_estimation: float = 0.0

class ContentProcessingRetry:
    """
    Retry spécialisé pour processing contenu IA Chérie.
    Media processing + AI analysis + upload retry patterns.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Stratégies retry par type média et étape
        self.content_retry_strategies = {
            'audio_processing': {
                'max_retries': 3,
                'timeout_progression': [30, 60, 120],  # seconds
                'error_classification': ['encoding_error', 'format_error', 'quality_error'],
                'quality_fallback_enabled': True,
                'chunk_retry_enabled': False,
                'ai_enhancement_fallback': True
            },
            'video_processing': {
                'max_retries': 5,
                'timeout_progression': [60, 120, 300, 600, 900],  # seconds
                'error_classification': ['encoding_error', 'format_error', 'quality_error', 'memory_error'],
                'quality_fallback_enabled': True,
                'chunk_retry_enabled': True,
                'ai_enhancement_fallback': True,
                'segment_processing': True
            },
            'image_processing': {
                'max_retries': 2,
                'timeout_progression': [15, 30],  # seconds
                'error_classification': ['format_error', 'quality_error', 'corruption_error'],
                'quality_fallback_enabled': True,
                'chunk_retry_enabled': False,
                'ai_enhancement_fallback': False
            },
            'text_processing': {
                'max_retries': 2,
                'timeout_progression': [10, 20],  # seconds
                'error_classification': ['encoding_error', 'language_error', 'parsing_error'],
                'quality_fallback_enabled': False,
                'chunk_retry_enabled': False,
                'ai_enhancement_fallback': True
            },
            'mixed_processing': {
                'max_retries': 4,
                'timeout_progression': [45, 90, 180, 360],  # seconds
                'error_classification': ['encoding_error', 'format_error', 'synchronization_error'],
                'quality_fallback_enabled': True,
                'chunk_retry_enabled': True,
                'ai_enhancement_fallback': True
            }
        }
        
        # Métriques processing
        self.processing_metrics = {
            'total_requests': 0,
            'successful_processing': 0,
            'failed_processing': 0,
            'quality_fallbacks': 0,
            'chunk_retries': 0,
            'ai_fallbacks': 0,
            'average_processing_time': 0.0,
            'cost_total': 0.0
        }
        
        # Cache résultats processing
        self.processing_cache = {}
        self.cache_ttl = 1800  # 30 minutes
        
        # Configuration optimisations
        self.optimization_config = {
            'parallel_processing_enabled': True,
            'gpu_acceleration_enabled': True,
            'cdn_upload_enabled': True,
            'smart_compression_enabled': True,
            'adaptive_quality_enabled': True
        }
    
    async def retry_content_processing(self, content_request: ContentRequest) -> ProcessingResult:
        """Retry spécialisé pour processing contenu avec media awareness."""
        
        self.processing_metrics['total_requests'] += 1
        start_time = time.time()
        
        try:
            # Vérification cache
            cache_key = self._generate_cache_key(content_request)
            cached_result = self._get_cached_result(cache_key)
            
            if cached_result:
                self.logger.info(f"Using cached result for content {content_request.content_id}")
                return cached_result
            
            # Sélection stratégie retry basée sur média et étape
            strategy = self._select_retry_strategy(content_request)
            
            # Processing avec retry adaptatif
            result = await self._execute_content_processing_with_retry(content_request, strategy)
            
            # Cache résultat si succès
            if result.success:
                self._cache_result(cache_key, result)
                self.processing_metrics['successful_processing'] += 1
            else:
                self.processing_metrics['failed_processing'] += 1
            
            # Mise à jour métriques
            processing_duration = time.time() - start_time
            self._update_processing_metrics(processing_duration, result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in content processing retry for {content_request.content_id}: {str(e)}")
            self.processing_metrics['failed_processing'] += 1
            
            return ProcessingResult(
                content_id=content_request.content_id,
                success=False,
                processing_stage=content_request.processing_stage,
                error_message=str(e),
                retry_recommendation="manual_review"
            )
    
    def _select_retry_strategy(self, content_request: ContentRequest) -> Dict:
        """Sélection stratégie retry basée sur contenu"""
        
        # Mapping type média vers stratégie
        media_strategy_map = {
            MediaType.AUDIO: 'audio_processing',
            MediaType.VIDEO: 'video_processing', 
            MediaType.IMAGE: 'image_processing',
            MediaType.TEXT: 'text_processing',
            MediaType.MIXED: 'mixed_processing'
        }
        
        strategy_name = media_strategy_map.get(content_request.media_type, 'mixed_processing')
        base_strategy = self.content_retry_strategies[strategy_name].copy()
        
        # Ajustements basés sur taille fichier
        if content_request.file_size > 100 * 1024 * 1024:  # > 100MB
            base_strategy['max_retries'] += 1
            base_strategy['timeout_progression'] = [t * 1.5 for t in base_strategy['timeout_progression']]
        
        # Ajustements basés sur priorité
        if content_request.priority >= 4:  # High priority
            base_strategy['max_retries'] += 1
        elif content_request.priority <= 2:  # Low priority
            base_strategy['max_retries'] = max(1, base_strategy['max_retries'] - 1)
        
        # Ajustements basés sur qualité cible
        if content_request.target_quality in [ContentQuality.ULTRA_HD, ContentQuality.HD]:
            base_strategy['timeout_progression'] = [t * 1.3 for t in base_strategy['timeout_progression']]
        
        return base_strategy
    
    async def _execute_content_processing_with_retry(self, content_request: ContentRequest, strategy: Dict) -> ProcessingResult:
        """Exécution processing avec retry adaptatif"""
        
        max_retries = strategy['max_retries']
        timeout_progression = strategy['timeout_progression']
        last_error = None
        quality_level = content_request.target_quality
        
        for attempt in range(max_retries + 1):
            try:
                # Timeout adaptatif
                timeout = timeout_progression[min(attempt, len(timeout_progression) - 1)]
                
                # Ajustement qualité si retry
                if attempt > 0 and strategy.get('quality_fallback_enabled', False):
                    quality_level = self._get_fallback_quality(quality_level)
                    self.logger.info(f"Quality fallback to {quality_level.value} for attempt {attempt + 1}")
                
                # Processing principal
                result = await self._process_content(content_request, quality_level, timeout, attempt)
                
                if result.success:
                    result.fallback_applied = (quality_level != content_request.target_quality)
                    return result
                else:
                    last_error = result.error_message
                    
                    # Vérification si erreur retriable
                    if not self._is_retriable_error(result.error_message, strategy):
                        break
                        
                    # Attente avant retry avec backoff
                    if attempt < max_retries:
                        backoff_delay = self._calculate_processing_backoff(attempt, content_request)
                        await asyncio.sleep(backoff_delay)
                        
            except asyncio.TimeoutError:
                last_error = f"Processing timeout after {timeout}s"
                self.logger.warning(f"Processing timeout for {content_request.content_id} on attempt {attempt + 1}")
                continue
                
            except Exception as e:
                last_error = str(e)
                self.logger.error(f"Processing error for {content_request.content_id}: {str(e)}")
                continue
        
        # Tous les retry ont échoué - tentative fallback
        if strategy.get('ai_enhancement_fallback', False):
            fallback_result = await self._try_ai_fallback(content_request, last_error)
            if fallback_result.success:
                self.processing_metrics['ai_fallbacks'] += 1
                return fallback_result
        
        # Échec final
        return ProcessingResult(
            content_id=content_request.content_id,
            success=False,
            processing_stage=content_request.processing_stage,
            error_message=last_error,
            retry_recommendation=self._generate_retry_recommendation(last_error, strategy)
        )
    
    async def _process_content(self, content_request: ContentRequest, quality_level: ContentQuality, timeout: float, attempt: int) -> ProcessingResult:
        """Processing principal du contenu"""
        
        start_time = time.time()
        
        # Simulation processing basée sur étape et type média
        processing_complexity = self._calculate_processing_complexity(content_request, quality_level)
        
        # Simulation durée processing
        base_duration = processing_complexity * (content_request.file_size / (1024 * 1024))  # MB-based
        
        # Facteur qualité
        quality_factors = {
            ContentQuality.ULTRA_HD: 2.5,
            ContentQuality.HD: 1.5,
            ContentQuality.STANDARD: 1.0,
            ContentQuality.BASIC: 0.7,
            ContentQuality.LOW: 0.5
        }
        
        processing_duration = base_duration * quality_factors.get(quality_level, 1.0)
        
        # Simulation avec timeout
        try:
            await asyncio.wait_for(
                self._simulate_processing_operation(content_request, processing_duration),
                timeout=timeout
            )
            
            # Calcul coût estimé
            cost = self._calculate_processing_cost(content_request, quality_level, processing_duration)
            
            # Métriques qualité simulées
            quality_metrics = self._generate_quality_metrics(content_request, quality_level)
            
            return ProcessingResult(
                content_id=content_request.content_id,
                success=True,
                processing_stage=content_request.processing_stage,
                processed_file_path=f"/processed/{content_request.content_id}_{quality_level.value}",
                processing_duration=time.time() - start_time,
                quality_metrics=quality_metrics,
                cost_estimation=cost
            )
            
        except asyncio.TimeoutError:
            raise asyncio.TimeoutError(f"Processing exceeded {timeout}s timeout")
        
        except Exception as e:
            # Simulation échecs possibles
            error_types = [
                "encoding_error", "format_error", "quality_error", 
                "memory_error", "corruption_error", "disk_space_error"
            ]
            
            # Probabilité échec basée sur complexité et attempt
            failure_probability = min(0.3, processing_complexity * 0.1 + attempt * 0.05)
            
            if time.time() % 1 < failure_probability:
                import random
                error_type = random.choice(error_types)
                raise Exception(f"Processing failed: {error_type}")
                
            return ProcessingResult(
                content_id=content_request.content_id,
                success=True,
                processing_stage=content_request.processing_stage,
                processed_file_path=f"/processed/{content_request.content_id}_{quality_level.value}",
                processing_duration=time.time() - start_time,
                quality_metrics=self._generate_quality_metrics(content_request, quality_level),
                cost_estimation=self._calculate_processing_cost(content_request, quality_level, processing_duration)
            )
    
    async def _simulate_processing_operation(self, content_request: ContentRequest, duration: float):
        """Simulation opération processing"""
        
        # Simulation processing par étape
        stage_durations = {
            ProcessingStage.UPLOAD: 0.2,
            ProcessingStage.VALIDATION: 0.1,
            ProcessingStage.TRANSCODING: 0.4,
            ProcessingStage.ENHANCEMENT: 0.3,
            ProcessingStage.ANALYSIS: 0.2,
            ProcessingStage.THUMBNAIL_GENERATION: 0.1,
            ProcessingStage.METADATA_EXTRACTION: 0.1,
            ProcessingStage.QUALITY_CHECK: 0.1,
            ProcessingStage.STORAGE: 0.2,
            ProcessingStage.INDEXING: 0.1
        }
        
        stage_duration = duration * stage_durations.get(content_request.processing_stage, 0.3)
        await asyncio.sleep(min(stage_duration, 2.0))  # Cap simulation time
    
    def _calculate_processing_complexity(self, content_request: ContentRequest, quality_level: ContentQuality) -> float:
        """Calcul complexité processing"""
        
        # Complexité de base par type média
        base_complexity = {
            MediaType.AUDIO: 1.0,
            MediaType.VIDEO: 3.0,
            MediaType.IMAGE: 0.5,
            MediaType.TEXT: 0.2,
            MediaType.MIXED: 2.5
        }
        
        complexity = base_complexity.get(content_request.media_type, 1.0)
        
        # Ajustement par étape processing
        stage_complexity = {
            ProcessingStage.UPLOAD: 0.5,
            ProcessingStage.VALIDATION: 0.3,
            ProcessingStage.TRANSCODING: 2.0,
            ProcessingStage.ENHANCEMENT: 1.5,
            ProcessingStage.ANALYSIS: 1.8,
            ProcessingStage.THUMBNAIL_GENERATION: 0.7,
            ProcessingStage.METADATA_EXTRACTION: 0.4,
            ProcessingStage.QUALITY_CHECK: 0.6,
            ProcessingStage.STORAGE: 0.3,
            ProcessingStage.INDEXING: 0.4
        }
        
        complexity *= stage_complexity.get(content_request.processing_stage, 1.0)
        
        # Ajustement par qualité
        quality_complexity = {
            ContentQuality.ULTRA_HD: 2.0,
            ContentQuality.HD: 1.5,
            ContentQuality.STANDARD: 1.0,
            ContentQuality.BASIC: 0.7,
            ContentQuality.LOW: 0.5
        }
        
        complexity *= quality_complexity.get(quality_level, 1.0)
        
        return complexity
    
    def _get_fallback_quality(self, current_quality: ContentQuality) -> ContentQuality:
        """Récupération qualité fallback"""
        
        quality_hierarchy = [
            ContentQuality.ULTRA_HD,
            ContentQuality.HD,
            ContentQuality.STANDARD,
            ContentQuality.BASIC,
            ContentQuality.LOW
        ]
        
        try:
            current_index = quality_hierarchy.index(current_quality)
            if current_index < len(quality_hierarchy) - 1:
                return quality_hierarchy[current_index + 1]
        except ValueError:
            pass
        
        return ContentQuality.STANDARD  # Fallback par défaut
    
    def _is_retriable_error(self, error_message: str, strategy: Dict) -> bool:
        """Vérification si erreur est retriable"""
        
        if not error_message:
            return True
        
        error_message_lower = error_message.lower()
        
        # Erreurs non retriables
        non_retriable_errors = [
            'corruption_error', 'format_not_supported', 'invalid_content',
            'copyright_violation', 'malicious_content'
        ]
        
        for non_retriable in non_retriable_errors:
            if non_retriable in error_message_lower:
                return False
        
        # Erreurs retriables selon classification
        error_classification = strategy.get('error_classification', [])
        for retriable_error in error_classification:
            if retriable_error in error_message_lower:
                return True
        
        # Par défaut, considérer comme retriable
        return True
    
    def _calculate_processing_backoff(self, attempt: int, content_request: ContentRequest) -> float:
        """Calcul backoff adaptatif pour processing"""
        
        # Backoff de base avec jitter
        base_delay = 2.0 ** attempt  # Exponential backoff
        
        # Ajustement par taille fichier
        if content_request.file_size > 50 * 1024 * 1024:  # > 50MB
            base_delay *= 1.5
        
        # Ajustement par type média
        media_factors = {
            MediaType.VIDEO: 1.5,
            MediaType.AUDIO: 1.2,
            MediaType.MIXED: 1.4,
            MediaType.IMAGE: 0.8,
            MediaType.TEXT: 0.5
        }
        
        base_delay *= media_factors.get(content_request.media_type, 1.0)
        
        # Jitter pour éviter thundering herd
        import random
        jitter = random.uniform(0.8, 1.2)
        
        return base_delay * jitter
    
    async def _try_ai_fallback(self, content_request: ContentRequest, original_error: str) -> ProcessingResult:
        """Tentative fallback avec IA"""
        
        self.logger.info(f"Attempting AI fallback for {content_request.content_id}")
        
        # Simulation traitement IA simplifié
        try:
            await asyncio.sleep(1.0)  # Simulation processing IA
            
            # Probabilité succès IA
            ai_success_probability = 0.7
            
            if time.time() % 1 < ai_success_probability:
                return ProcessingResult(
                    content_id=content_request.content_id,
                    success=True,
                    processing_stage=content_request.processing_stage,
                    processed_file_path=f"/processed/{content_request.content_id}_ai_fallback",
                    processing_duration=1.0,
                    quality_metrics={'ai_enhanced': True, 'quality_score': 0.75},
                    fallback_applied=True,
                    cost_estimation=5.0  # IA plus coûteuse
                )
            else:
                return ProcessingResult(
                    content_id=content_request.content_id,
                    success=False,
                    processing_stage=content_request.processing_stage,
                    error_message=f"AI fallback failed: {original_error}"
                )
                
        except Exception as e:
            return ProcessingResult(
                content_id=content_request.content_id,
                success=False,
                processing_stage=content_request.processing_stage,
                error_message=f"AI fallback error: {str(e)}"
            )
    
    def _generate_retry_recommendation(self, error_message: str, strategy: Dict) -> str:
        """Génération recommandation retry"""
        
        if not error_message:
            return "manual_review"
        
        error_lower = error_message.lower()
        
        if 'memory' in error_lower or 'resource' in error_lower:
            return "scale_up_resources"
        elif 'timeout' in error_lower:
            return "increase_timeout"
        elif 'format' in error_lower or 'encoding' in error_lower:
            return "format_conversion"
        elif 'quality' in error_lower:
            return "reduce_quality"
        elif 'corruption' in error_lower:
            return "re_upload_content"
        else:
            return "manual_review"
    
    def _calculate_processing_cost(self, content_request: ContentRequest, quality_level: ContentQuality, duration: float) -> float:
        """Calcul coût processing"""
        
        # Coûts de base par type média (par MB)
        base_costs = {
            MediaType.VIDEO: 0.10,
            MediaType.AUDIO: 0.05,
            MediaType.IMAGE: 0.02,
            MediaType.TEXT: 0.01,
            MediaType.MIXED: 0.08
        }
        
        # Coût par qualité
        quality_multipliers = {
            ContentQuality.ULTRA_HD: 3.0,
            ContentQuality.HD: 2.0,
            ContentQuality.STANDARD: 1.0,
            ContentQuality.BASIC: 0.7,
            ContentQuality.LOW: 0.5
        }
        
        file_size_mb = content_request.file_size / (1024 * 1024)
        base_cost = base_costs.get(content_request.media_type, 0.05)
        quality_multiplier = quality_multipliers.get(quality_level, 1.0)
        
        # Coût basé sur durée processing
        time_cost = duration * 0.01  # $0.01 per second
        
        total_cost = (file_size_mb * base_cost * quality_multiplier) + time_cost
        
        return round(total_cost, 4)
    
    def _generate_quality_metrics(self, content_request: ContentRequest, quality_level: ContentQuality) -> Dict:
        """Génération métriques qualité"""
        
        # Scores qualité simulés
        quality_scores = {
            ContentQuality.ULTRA_HD: 0.95,
            ContentQuality.HD: 0.85,
            ContentQuality.STANDARD: 0.75,
            ContentQuality.BASIC: 0.65,
            ContentQuality.LOW: 0.45
        }
        
        base_score = quality_scores.get(quality_level, 0.75)
        
        metrics = {
            'quality_score': base_score,
            'processing_efficiency': min(1.0, base_score + 0.1),
            'compression_ratio': 0.3 + (0.5 * (1 - base_score)),
            'target_quality': quality_level.value
        }
        
        # Métriques spécifiques par type média
        if content_request.media_type == MediaType.VIDEO:
            metrics.update({
                'video_bitrate': int(5000 * base_score),  # kbps
                'frame_rate': 30 if quality_level in [ContentQuality.HD, ContentQuality.ULTRA_HD] else 24,
                'resolution_maintained': base_score > 0.8
            })
        elif content_request.media_type == MediaType.AUDIO:
            metrics.update({
                'audio_bitrate': int(320 * base_score),  # kbps
                'sample_rate': 48000 if base_score > 0.8 else 44100,
                'noise_reduction': base_score
            })
        
        return metrics
    
    def _generate_cache_key(self, content_request: ContentRequest) -> str:
        """Génération clé cache"""
        key_components = [
            content_request.content_id,
            content_request.media_type.value,
            content_request.processing_stage.value,
            content_request.target_quality.value,
            str(content_request.file_size)
        ]
        
        key_string = ":".join(key_components)
        return hashlib.md5(key_string.encode()).hexdigest()[:16]
    
    def _get_cached_result(self, cache_key: str) -> Optional[ProcessingResult]:
        """Récupération résultat caché"""
        if cache_key in self.processing_cache:
            cached_entry = self.processing_cache[cache_key]
            if time.time() - cached_entry['timestamp'] < self.cache_ttl:
                return cached_entry['result']
            else:
                del self.processing_cache[cache_key]
        return None
    
    def _cache_result(self, cache_key: str, result: ProcessingResult):
        """Mise en cache résultat"""
        self.processing_cache[cache_key] = {
            'result': result,
            'timestamp': time.time()
        }
    
    def _update_processing_metrics(self, duration: float, result: ProcessingResult):
        """Mise à jour métriques processing"""
        
        # Moyenne mobile pour processing time
        alpha = 0.1
        self.processing_metrics['average_processing_time'] = (
            self.processing_metrics['average_processing_time'] * (1 - alpha) + 
            duration * alpha
        )
        
        # Ajout coût
        self.processing_metrics['cost_total'] += result.cost_estimation
        
        # Compteurs fallback
        if result.fallback_applied:
            self.processing_metrics['quality_fallbacks'] += 1
    
    async def get_processing_metrics(self) -> Dict:
        """Récupération métriques processing"""
        
        return {
            **self.processing_metrics,
            'success_rate': (
                self.processing_metrics['successful_processing'] / 
                max(1, self.processing_metrics['total_requests'])
            ),
            'average_cost_per_request': (
                self.processing_metrics['cost_total'] / 
                max(1, self.processing_metrics['total_requests'])
            ),
            'cache_size': len(self.processing_cache),
            'optimization_config': self.optimization_config
        }
    
    async def health_check(self) -> Dict:
        """Vérification santé processing retry"""
        
        return {
            'status': 'healthy',
            'total_requests_processed': self.processing_metrics['total_requests'],
            'current_success_rate': (
                self.processing_metrics['successful_processing'] / 
                max(1, self.processing_metrics['total_requests'])
            ),
            'cache_health': {
                'entries': len(self.processing_cache),
                'utilization': len(self.processing_cache) / 1000.0  # Assuming max 1000 entries
            },
            'strategies_available': len(self.content_retry_strategies),
            'optimizations_enabled': sum(1 for enabled in self.optimization_config.values() if enabled)
        }

# Factory functions
def create_content_processing_retry() -> ContentProcessingRetry:
    """Factory pour création retry processing contenu"""
    return ContentProcessingRetry()

# Configuration prédéfinies IA Chérie
IACHERIE_CONTENT_CONFIGS = {
    'creator_upload': {
        'priority_boost': True,
        'quality_preservation': True,
        'fast_processing': True,
        'ai_enhancement': True
    },
    'bulk_processing': {
        'cost_optimization': True,
        'quality_fallback_aggressive': True,
        'parallel_processing': True,
        'ai_enhancement': False
    },
    'live_streaming': {
        'real_time_processing': True,
        'quality_adaptive': True,
        'low_latency': True,
        'ai_enhancement': False
    }
}

__all__ = [
    'ContentProcessingRetry',
    'ContentRequest',
    'ProcessingResult',
    'MediaType',
    'ProcessingStage',
    'ContentQuality',
    'create_content_processing_retry',
    'IACHERIE_CONTENT_CONFIGS'
]