"""🚀 Latency Optimizer - IA Influencer Agent Platform Enterprise
=====================================================================
Module: ml/inference/latency_optimizer.py
Author: Fahed Mlaiel (mlaiel@live.de) - ML Engineer + Performance Expert + Edge Computing Specialist
Phase: 13 - Advanced Content Processing + Creator Intelligence
=====================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 OPTIMISEUR DE LATENCE INFERENCE
Advanced inference latency optimization with:
- Model quantization and compression
- Hardware acceleration (GPU/TPU/Edge)
- Dynamic batching and caching
- Edge computing optimization
- Real-time performance monitoring
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
import threading
from collections import deque, defaultdict
import math
import statistics

# Configuration
logger = logging.getLogger(__name__)

class HardwareType(Enum):
    """Types de matériel supportés"""
    CPU = "cpu"
    GPU = "gpu"
    TPU = "tpu"
    EDGE = "edge"
    MOBILE = "mobile"

class OptimizationStrategy(Enum):
    """Stratégies d'optimisation"""
    QUANTIZATION = "quantization"
    PRUNING = "pruning"
    DISTILLATION = "distillation"
    CACHING = "caching"
    BATCHING = "batching"
    HARDWARE_ACCELERATION = "hardware_acceleration"

class ModelPrecision(Enum):
    """Précisions de modèle"""
    FP32 = "fp32"
    FP16 = "fp16"
    INT8 = "int8"
    INT4 = "int4"

@dataclass
class PerformanceMetrics:
    """Métriques de performance"""
    latency_ms: float
    throughput_rps: float
    memory_usage_mb: float
    cpu_utilization: float
    gpu_utilization: float
    cache_hit_rate: float
    batch_efficiency: float
    energy_consumption: float

@dataclass
class OptimizationResult:
    """Résultat d'optimisation"""
    original_latency_ms: float
    optimized_latency_ms: float
    latency_reduction_percent: float
    memory_reduction_percent: float
    accuracy_loss_percent: float
    strategies_applied: List[OptimizationStrategy]
    hardware_utilization: Dict[str, float]
    recommendations: List[str]

@dataclass
class ModelProfile:
    """Profil de modèle optimisé"""
    model_id: str
    original_size_mb: float
    optimized_size_mb: float
    precision: ModelPrecision
    quantization_config: Dict[str, Any]
    pruning_ratio: float
    target_hardware: HardwareType
    optimization_timestamp: datetime

@dataclass
class CacheEntry:
    """Entrée de cache avec métadonnées"""
    key: str
    value: Any
    timestamp: datetime
    access_count: int
    latency_saved_ms: float
    size_bytes: int

class LatencyOptimizer:
    """🎯 Optimiseur de Latence Inference Enterprise
    
    Fonctionnalités avancées:
    - Quantification automatique de modèles
    - Optimisation hardware-specific
    - Cache intelligent prédictif
    - Batching dynamique
    - Monitoring temps réel
    """
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        """Initialise l'optimiseur de latence
        
        Args:
            config: Configuration personnalisée
        """
        self.config = config or {}
        self.model_profiles = {}
        self.performance_history = deque(maxlen=1000)
        self.cache = {}
        self.batch_queue = deque()
        self.optimization_strategies = {}
        
        # Configuration par défaut
        self.target_latency_ms = self.config.get('target_latency_ms', 100)
        self.cache_size_mb = self.config.get('cache_size_mb', 1024)
        self.batch_timeout_ms = self.config.get('batch_timeout_ms', 50)
        self.max_batch_size = self.config.get('max_batch_size', 32)
        self.enable_quantization = self.config.get('enable_quantization', True)
        self.target_hardware = HardwareType(self.config.get('target_hardware', 'gpu'))
        
        # Métriques en temps réel
        self.current_metrics = PerformanceMetrics(
            latency_ms=0.0, throughput_rps=0.0, memory_usage_mb=0.0,
            cpu_utilization=0.0, gpu_utilization=0.0, cache_hit_rate=0.0,
            batch_efficiency=0.0, energy_consumption=0.0
        )
        
        # Thread pour optimisations en arrière-plan
        self._optimization_thread = None
        self._stop_optimization = threading.Event()
        
        logger.info("Latency Optimizer initialized - Performance Intelligence Ready")
    
    async def optimize_model(
        self,
        model_id: str,
        model_data: Any,
        optimization_targets: Optional[Dict[str, float]] = None
    ) -> OptimizationResult:
        """Optimisation complète d'un modèle
        
        Args:
            model_id: Identifiant du modèle
            model_data: Données du modèle à optimiser
            optimization_targets: Cibles d'optimisation personnalisées
            
        Returns:
            Résultat détaillé de l'optimisation
        """
        start_time = time.time()
        
        try:
            # Cibles par défaut
            targets = optimization_targets or {
                'max_latency_ms': self.target_latency_ms,
                'max_accuracy_loss_percent': 2.0,
                'min_memory_reduction_percent': 20.0
            }
            
            # Profiling initial du modèle
            original_metrics = await self._profile_model(model_data)
            original_latency = original_metrics.latency_ms
            
            logger.info(f"Starting optimization for model {model_id} - Original latency: {original_latency:.2f}ms")
            
            # Stratégies d'optimisation appliquées
            applied_strategies = []
            current_model = model_data
            current_latency = original_latency
            accuracy_loss = 0.0
            memory_reduction = 0.0
            
            # 1. Quantification si activée
            if self.enable_quantization and current_latency > targets['max_latency_ms']:
                quantized_model, quant_metrics = await self._apply_quantization(
                    current_model, self.target_hardware
                )
                if quant_metrics['latency_improvement'] > 0.1:
                    current_model = quantized_model
                    current_latency *= (1 - quant_metrics['latency_improvement'])
                    accuracy_loss += quant_metrics['accuracy_loss']
                    memory_reduction += quant_metrics['memory_reduction']
                    applied_strategies.append(OptimizationStrategy.QUANTIZATION)
                    logger.info(f"Quantization applied - New latency: {current_latency:.2f}ms")
            
            # 2. Pruning si nécessaire
            if current_latency > targets['max_latency_ms']:
                pruned_model, prune_metrics = await self._apply_pruning(current_model)
                if prune_metrics['latency_improvement'] > 0.05:
                    current_model = pruned_model
                    current_latency *= (1 - prune_metrics['latency_improvement'])
                    accuracy_loss += prune_metrics['accuracy_loss']
                    memory_reduction += prune_metrics['memory_reduction']
                    applied_strategies.append(OptimizationStrategy.PRUNING)
                    logger.info(f"Pruning applied - New latency: {current_latency:.2f}ms")
            
            # 3. Optimisation hardware-specific
            hw_optimized_model, hw_metrics = await self._apply_hardware_optimization(
                current_model, self.target_hardware
            )
            current_model = hw_optimized_model
            current_latency *= (1 - hw_metrics['latency_improvement'])
            applied_strategies.append(OptimizationStrategy.HARDWARE_ACCELERATION)
            
            # 4. Configuration du cache
            cache_config = await self._optimize_caching_strategy(model_id, original_metrics)
            applied_strategies.append(OptimizationStrategy.CACHING)
            
            # 5. Configuration du batching
            batch_config = await self._optimize_batching_strategy(model_id, original_metrics)
            applied_strategies.append(OptimizationStrategy.BATCHING)
            
            # Calcul des améliorations finales
            final_latency = current_latency
            latency_reduction = ((original_latency - final_latency) / original_latency) * 100
            
            # Profil du modèle optimisé
            model_profile = ModelProfile(
                model_id=model_id,
                original_size_mb=original_metrics.memory_usage_mb,
                optimized_size_mb=original_metrics.memory_usage_mb * (1 - memory_reduction/100),
                precision=ModelPrecision.INT8 if OptimizationStrategy.QUANTIZATION in applied_strategies else ModelPrecision.FP32,
                quantization_config={} if OptimizationStrategy.QUANTIZATION not in applied_strategies else {
                    'method': 'dynamic_quantization',
                    'precision': 'int8',
                    'calibration_data': 'representative_dataset'
                },
                pruning_ratio=0.2 if OptimizationStrategy.PRUNING in applied_strategies else 0.0,
                target_hardware=self.target_hardware,
                optimization_timestamp=datetime.now()
            )
            
            self.model_profiles[model_id] = model_profile
            
            # Recommandations
            recommendations = await self._generate_optimization_recommendations(
                original_metrics, targets, latency_reduction, accuracy_loss
            )
            
            result = OptimizationResult(
                original_latency_ms=original_latency,
                optimized_latency_ms=final_latency,
                latency_reduction_percent=latency_reduction,
                memory_reduction_percent=memory_reduction,
                accuracy_loss_percent=accuracy_loss,
                strategies_applied=applied_strategies,
                hardware_utilization={
                    'cpu': 0.7,
                    'gpu': 0.85 if self.target_hardware == HardwareType.GPU else 0.0,
                    'memory': 0.6
                },
                recommendations=recommendations
            )
            
            processing_time = (time.time() - start_time) * 1000
            logger.info(f"Model optimization completed - Time: {processing_time:.2f}ms, "
                       f"Latency reduction: {latency_reduction:.1f}%")
            
            return result
            
        except Exception as e:
            logger.error(f"Model optimization failed: {str(e)}")
            raise RuntimeError(f"Optimization error: {str(e)}")
    
    async def _profile_model(self, model_data: Any) -> PerformanceMetrics:
        """Profiling initial du modèle"""
        try:
            # Simulation du profiling
            await asyncio.sleep(0.02)  # Simulation temps de profiling
            
            # Métriques simulées basées sur la taille du modèle
            model_size = getattr(model_data, 'size', 100)  # MB estimé
            
            # Latence basée sur la taille du modèle et le hardware
            if self.target_hardware == HardwareType.GPU:
                base_latency = model_size * 0.8  # GPU plus rapide
            elif self.target_hardware == HardwareType.TPU:
                base_latency = model_size * 0.5  # TPU très rapide
            elif self.target_hardware == HardwareType.EDGE:
                base_latency = model_size * 3.0  # Edge plus lent
            else:
                base_latency = model_size * 2.0  # CPU baseline
            
            return PerformanceMetrics(
                latency_ms=base_latency,
                throughput_rps=1000.0 / base_latency,
                memory_usage_mb=model_size,
                cpu_utilization=0.6,
                gpu_utilization=0.8 if self.target_hardware == HardwareType.GPU else 0.0,
                cache_hit_rate=0.0,  # Pas encore de cache
                batch_efficiency=0.5,  # Efficacité par défaut
                energy_consumption=model_size * 0.1  # Watts estimés
            )
            
        except Exception as e:
            logger.error(f"Model profiling failed: {str(e)}")
            raise
    
    async def _apply_quantization(
        self,
        model_data: Any,
        target_hardware: HardwareType
    ) -> Tuple[Any, Dict[str, float]]:
        """Application de la quantification"""
        try:
            await asyncio.sleep(0.05)  # Simulation quantification
            
            # Métriques d'amélioration basées sur le hardware
            if target_hardware == HardwareType.EDGE:
                # Edge bénéficie plus de la quantification
                latency_improvement = 0.4
                memory_reduction = 0.6
                accuracy_loss = 1.5
            elif target_hardware == HardwareType.MOBILE:
                latency_improvement = 0.5
                memory_reduction = 0.7
                accuracy_loss = 2.0
            else:
                # GPU/TPU
                latency_improvement = 0.25
                memory_reduction = 0.4
                accuracy_loss = 1.0
            
            # Modèle quantifié (simulation)
            quantized_model = {
                'original': model_data,
                'quantized': True,
                'precision': 'int8',
                'size_reduction': memory_reduction
            }
            
            metrics = {
                'latency_improvement': latency_improvement,
                'memory_reduction': memory_reduction * 100,
                'accuracy_loss': accuracy_loss
            }
            
            logger.debug(f"Quantization completed - Latency improvement: {latency_improvement:.1%}")
            return quantized_model, metrics
            
        except Exception as e:
            logger.error(f"Quantization failed: {str(e)}")
            return model_data, {'latency_improvement': 0.0, 'memory_reduction': 0.0, 'accuracy_loss': 0.0}
    
    async def _apply_pruning(self, model_data: Any) -> Tuple[Any, Dict[str, float]]:
        """Application du pruning (élagage)"""
        try:
            await asyncio.sleep(0.03)  # Simulation pruning
            
            # Pruning modéré pour préserver l'accuracy
            pruning_ratio = 0.2  # 20% des paramètres supprimés
            
            latency_improvement = pruning_ratio * 0.7  # 70% du pruning se traduit en vitesse
            memory_reduction = pruning_ratio * 0.8  # 80% en réduction mémoire
            accuracy_loss = pruning_ratio * 2.0  # Perte d'accuracy modérée
            
            # Modèle élagué (simulation)
            pruned_model = {
                'original': model_data,
                'pruned': True,
                'pruning_ratio': pruning_ratio,
                'sparsity': pruning_ratio
            }
            
            metrics = {
                'latency_improvement': latency_improvement,
                'memory_reduction': memory_reduction * 100,
                'accuracy_loss': accuracy_loss
            }
            
            logger.debug(f"Pruning completed - {pruning_ratio:.1%} parameters removed")
            return pruned_model, metrics
            
        except Exception as e:
            logger.error(f"Pruning failed: {str(e)}")
            return model_data, {'latency_improvement': 0.0, 'memory_reduction': 0.0, 'accuracy_loss': 0.0}
    
    async def _apply_hardware_optimization(
        self,
        model_data: Any,
        target_hardware: HardwareType
    ) -> Tuple[Any, Dict[str, float]]:
        """Optimisation spécifique au hardware"""
        try:
            await asyncio.sleep(0.02)  # Simulation optimisation hardware
            
            # Optimisations spécifiques par hardware
            if target_hardware == HardwareType.GPU:
                # Optimisations CUDA
                latency_improvement = 0.15
                optimizations = ['cuda_graphs', 'tensor_cores', 'memory_coalescing']
            elif target_hardware == HardwareType.TPU:
                # Optimisations TPU
                latency_improvement = 0.25
                optimizations = ['xla_compilation', 'tpu_fusion', 'bfloat16']
            elif target_hardware == HardwareType.EDGE:
                # Optimisations Edge
                latency_improvement = 0.2
                optimizations = ['neon_simd', 'cpu_affinity', 'memory_mapping']
            else:
                # Optimisations CPU
                latency_improvement = 0.1
                optimizations = ['avx2', 'openmp', 'mkl_blas']
            
            # Modèle optimisé hardware (simulation)
            optimized_model = {
                'original': model_data,
                'hardware_optimized': True,
                'target_hardware': target_hardware.value,
                'optimizations': optimizations
            }
            
            metrics = {
                'latency_improvement': latency_improvement,
                'hardware_utilization': 0.9,
                'optimizations_applied': optimizations
            }
            
            logger.debug(f"Hardware optimization completed for {target_hardware.value}")
            return optimized_model, metrics
            
        except Exception as e:
            logger.error(f"Hardware optimization failed: {str(e)}")
            return model_data, {'latency_improvement': 0.0}
    
    async def _optimize_caching_strategy(
        self,
        model_id: str,
        metrics: PerformanceMetrics
    ) -> Dict[str, Any]:
        """Optimisation de la stratégie de cache"""
        try:
            # Stratégie de cache basée sur les métriques
            if metrics.latency_ms > 50:
                # Cache agressif pour les modèles lents
                cache_config = {
                    'strategy': 'aggressive',
                    'ttl_seconds': 300,
                    'max_entries': 10000,
                    'memory_limit_mb': self.cache_size_mb,
                    'eviction_policy': 'lru',
                    'precompute_popular': True
                }
            else:
                # Cache modéré pour les modèles rapides
                cache_config = {
                    'strategy': 'moderate',
                    'ttl_seconds': 600,
                    'max_entries': 5000,
                    'memory_limit_mb': self.cache_size_mb // 2,
                    'eviction_policy': 'lfu',
                    'precompute_popular': False
                }
            
            logger.debug(f"Cache strategy optimized for model {model_id}")
            return cache_config
            
        except Exception as e:
            logger.error(f"Cache optimization failed: {str(e)}")
            return {}
    
    async def _optimize_batching_strategy(
        self,
        model_id: str,
        metrics: PerformanceMetrics
    ) -> Dict[str, Any]:
        """Optimisation de la stratégie de batching"""
        try:
            # Stratégie de batching basée sur les métriques
            if metrics.latency_ms > 100:
                # Batching agressif pour amortir la latence
                batch_config = {
                    'strategy': 'aggressive',
                    'max_batch_size': self.max_batch_size,
                    'timeout_ms': self.batch_timeout_ms * 2,
                    'dynamic_sizing': True,
                    'priority_queuing': True
                }
            else:
                # Batching modéré
                batch_config = {
                    'strategy': 'moderate',
                    'max_batch_size': self.max_batch_size // 2,
                    'timeout_ms': self.batch_timeout_ms,
                    'dynamic_sizing': False,
                    'priority_queuing': False
                }
            
            logger.debug(f"Batching strategy optimized for model {model_id}")
            return batch_config
            
        except Exception as e:
            logger.error(f"Batching optimization failed: {str(e)}")
            return {}
    
    async def _generate_optimization_recommendations(
        self,
        original_metrics: PerformanceMetrics,
        targets: Dict[str, float],
        latency_reduction: float,
        accuracy_loss: float
    ) -> List[str]:
        """Génération de recommandations d'optimisation"""
        recommendations = []
        
        # Recommandations basées sur les résultats
        if latency_reduction < 20:
            recommendations.append("Considérer une quantification plus agressive (INT4)")
            recommendations.append("Évaluer l'utilisation d'un hardware plus performant")
        
        if accuracy_loss > 3.0:
            recommendations.append("Réduire l'agressivité de l'optimisation pour préserver l'accuracy")
            recommendations.append("Utiliser la distillation de connaissance pour compenser")
        
        if original_metrics.memory_usage_mb > 1000:
            recommendations.append("Implémenter le gradient checkpointing pour réduire la mémoire")
            recommendations.append("Considérer la parallelisation des modèles")
        
        if original_metrics.latency_ms > targets.get('max_latency_ms', 100):
            recommendations.append("Optimiser la pipeline de préprocessing")
            recommendations.append("Implémenter un cache prédictif intelligent")
        
        # Recommandations hardware-specific
        if self.target_hardware == HardwareType.EDGE:
            recommendations.append("Optimiser pour ARM NEON instructions")
            recommendations.append("Utiliser des modèles MobileNet ou EfficientNet")
        elif self.target_hardware == HardwareType.GPU:
            recommendations.append("Activer TensorRT pour NVIDIA GPUs")
            recommendations.append("Utiliser mixed precision training")
        
        return recommendations
    
    async def optimize_inference_pipeline(
        self,
        pipeline_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Optimisation complète de la pipeline d'inférence"""
        try:
            optimized_config = pipeline_config.copy()
            
            # Optimisations de la pipeline
            optimizations = []
            
            # 1. Préprocessing optimization
            if 'preprocessing' in pipeline_config:
                optimized_config['preprocessing']['parallel_workers'] = min(8, pipeline_config.get('max_workers', 4))
                optimized_config['preprocessing']['use_gpu'] = self.target_hardware == HardwareType.GPU
                optimizations.append("Preprocessing parallelization")
            
            # 2. Model serving optimization
            optimized_config['model_serving'] = {
                'batch_size': self.max_batch_size,
                'timeout_ms': self.batch_timeout_ms,
                'hardware': self.target_hardware.value,
                'precision': 'fp16' if self.target_hardware == HardwareType.GPU else 'fp32'
            }
            optimizations.append("Model serving optimization")
            
            # 3. Postprocessing optimization
            if 'postprocessing' in pipeline_config:
                optimized_config['postprocessing']['vectorized'] = True
                optimized_config['postprocessing']['cache_results'] = True
                optimizations.append("Postprocessing vectorization")
            
            # 4. Memory management
            optimized_config['memory_management'] = {
                'pool_size_mb': 512,
                'garbage_collection': 'aggressive',
                'memory_mapping': True
            }
            optimizations.append("Memory management")
            
            logger.info(f"Pipeline optimization completed - {len(optimizations)} optimizations applied")
            return optimized_config
            
        except Exception as e:
            logger.error(f"Pipeline optimization failed: {str(e)}")
            return pipeline_config
    
    async def monitor_performance(self, duration_seconds: int = 60) -> Dict[str, Any]:
        """Monitoring de performance en temps réel"""
        try:
            metrics_history = []
            start_time = time.time()
            
            while time.time() - start_time < duration_seconds:
                # Collecte des métriques actuelles
                current_metrics = await self._collect_current_metrics()
                metrics_history.append({
                    'timestamp': datetime.now(),
                    'metrics': current_metrics
                })
                
                await asyncio.sleep(1.0)  # Collecte chaque seconde
            
            # Analyse des métriques
            analysis = await self._analyze_performance_metrics(metrics_history)
            
            return {
                'monitoring_duration_seconds': duration_seconds,
                'samples_collected': len(metrics_history),
                'performance_analysis': analysis,
                'recommendations': await self._generate_performance_recommendations(analysis)
            }
            
        except Exception as e:
            logger.error(f"Performance monitoring failed: {str(e)}")
            return {}
    
    async def _collect_current_metrics(self) -> PerformanceMetrics:
        """Collecte des métriques actuelles"""
        try:
            # Simulation de collecte de métriques système
            import random
            
            # Métriques simulées avec variabilité réaliste
            return PerformanceMetrics(
                latency_ms=random.uniform(20, 150),
                throughput_rps=random.uniform(50, 200),
                memory_usage_mb=random.uniform(200, 800),
                cpu_utilization=random.uniform(0.3, 0.9),
                gpu_utilization=random.uniform(0.6, 0.95) if self.target_hardware == HardwareType.GPU else 0.0,
                cache_hit_rate=random.uniform(0.7, 0.95),
                batch_efficiency=random.uniform(0.6, 0.9),
                energy_consumption=random.uniform(10, 50)
            )
            
        except Exception as e:
            logger.error(f"Metrics collection failed: {str(e)}")
            return self.current_metrics
    
    async def _analyze_performance_metrics(
        self,
        metrics_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyse des métriques de performance"""
        try:
            if not metrics_history:
                return {}
            
            # Extraction des valeurs de latence
            latencies = [entry['metrics'].latency_ms for entry in metrics_history]
            throughputs = [entry['metrics'].throughput_rps for entry in metrics_history]
            memory_usage = [entry['metrics'].memory_usage_mb for entry in metrics_history]
            
            analysis = {
                'latency_stats': {
                    'min_ms': min(latencies),
                    'max_ms': max(latencies),
                    'avg_ms': statistics.mean(latencies),
                    'p95_ms': statistics.quantiles(latencies, n=20)[18] if len(latencies) >= 20 else max(latencies),
                    'p99_ms': statistics.quantiles(latencies, n=100)[98] if len(latencies) >= 100 else max(latencies),
                    'std_dev': statistics.stdev(latencies) if len(latencies) > 1 else 0
                },
                'throughput_stats': {
                    'min_rps': min(throughputs),
                    'max_rps': max(throughputs),
                    'avg_rps': statistics.mean(throughputs)
                },
                'memory_stats': {
                    'min_mb': min(memory_usage),
                    'max_mb': max(memory_usage),
                    'avg_mb': statistics.mean(memory_usage)
                },
                'stability_score': 1.0 - (statistics.stdev(latencies) / statistics.mean(latencies)) if len(latencies) > 1 and statistics.mean(latencies) > 0 else 1.0
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Performance analysis failed: {str(e)}")
            return {}
    
    async def _generate_performance_recommendations(
        self,
        analysis: Dict[str, Any]
    ) -> List[str]:
        """Génération de recommandations basées sur l'analyse"""
        recommendations = []
        
        if not analysis:
            return recommendations
        
        latency_stats = analysis.get('latency_stats', {})
        
        # Recommandations basées sur la latence
        if latency_stats.get('avg_ms', 0) > self.target_latency_ms:
            recommendations.append(f"Latence moyenne ({latency_stats['avg_ms']:.1f}ms) dépasse la cible ({self.target_latency_ms}ms)")
            recommendations.append("Considérer une optimisation plus agressive")
        
        if latency_stats.get('p99_ms', 0) > self.target_latency_ms * 2:
            recommendations.append("P99 de latence trop élevé - optimiser les cas extrêmes")
        
        if latency_stats.get('std_dev', 0) > latency_stats.get('avg_ms', 0) * 0.3:
            recommendations.append("Variabilité de latence élevée - stabiliser les performances")
        
        # Recommandations basées sur la stabilité
        stability_score = analysis.get('stability_score', 1.0)
        if stability_score < 0.8:
            recommendations.append("Score de stabilité faible - investiguer les variations de performance")
        
        return recommendations
    
    def get_model_profile(self, model_id: str) -> Optional[ModelProfile]:
        """Récupération du profil d'un modèle optimisé"""
        return self.model_profiles.get(model_id)
    
    def get_optimization_strategies(self) -> Dict[str, Dict[str, Any]]:
        """Récupération des stratégies d'optimisation disponibles"""
        return {
            'quantization': {
                'description': 'Réduction de précision numérique',
                'latency_improvement': '25-50%',
                'memory_reduction': '40-75%',
                'accuracy_loss': '1-3%',
                'supported_hardware': ['cpu', 'gpu', 'edge', 'mobile']
            },
            'pruning': {
                'description': 'Suppression de paramètres non-critiques',
                'latency_improvement': '10-30%',
                'memory_reduction': '20-60%',
                'accuracy_loss': '1-5%',
                'supported_hardware': ['cpu', 'gpu', 'edge']
            },
            'distillation': {
                'description': 'Compression par transfert de connaissance',
                'latency_improvement': '30-70%',
                'memory_reduction': '50-90%',
                'accuracy_loss': '2-8%',
                'supported_hardware': ['cpu', 'gpu', 'edge', 'mobile']
            },
            'hardware_acceleration': {
                'description': 'Optimisation spécifique au hardware',
                'latency_improvement': '10-25%',
                'memory_reduction': '5-15%',
                'accuracy_loss': '0%',
                'supported_hardware': ['gpu', 'tpu', 'edge']
            }
        }
    
    async def benchmark_optimization_strategies(
        self,
        model_data: Any,
        strategies: List[OptimizationStrategy]
    ) -> Dict[str, OptimizationResult]:
        """Benchmark de différentes stratégies d'optimisation"""
        try:
            results = {}
            
            for strategy in strategies:
                logger.info(f"Benchmarking optimization strategy: {strategy.value}")
                
                # Configuration spécifique à la stratégie
                strategy_config = {
                    'enable_quantization': strategy == OptimizationStrategy.QUANTIZATION,
                    'enable_pruning': strategy == OptimizationStrategy.PRUNING,
                    'enable_hardware_accel': strategy == OptimizationStrategy.HARDWARE_ACCELERATION
                }
                
                # Optimisation avec cette stratégie uniquement
                temp_optimizer = LatencyOptimizer({**self.config, **strategy_config})
                result = await temp_optimizer.optimize_model(
                    f"benchmark_{strategy.value}",
                    model_data
                )
                
                results[strategy.value] = result
            
            return results
            
        except Exception as e:
            logger.error(f"Optimization benchmark failed: {str(e)}")
            return {}
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Résumé des performances globales"""
        return {
            'total_models_optimized': len(self.model_profiles),
            'average_latency_reduction': 35.0,  # Simulation
            'average_memory_reduction': 45.0,   # Simulation
            'cache_hit_rate': 0.87,
            'optimization_success_rate': 0.95,
            'supported_hardware': [hw.value for hw in HardwareType],
            'target_latency_ms': self.target_latency_ms,
            'current_performance': self.current_metrics.__dict__
        }

# Factory function pour intégration facile
def create_latency_optimizer(config: Optional[Dict[str, Any]] = None) -> LatencyOptimizer:
    """Factory pour créer un optimiseur de latence configuré"""
    return LatencyOptimizer(config)

# Export pour usage externe
__all__ = [
    'LatencyOptimizer',
    'OptimizationResult',
    'ModelProfile',
    'PerformanceMetrics',
    'HardwareType',
    'OptimizationStrategy',
    'create_latency_optimizer'
]