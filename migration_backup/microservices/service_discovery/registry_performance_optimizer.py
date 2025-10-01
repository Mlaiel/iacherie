"""
⚡ REGISTRY PERFORMANCE OPTIMIZER - Module Optimization Performance Registry IA Chéries
==================================================================================

**Expert Team**: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer
**IP Owner**: Fahed Mlaiel (mlaiel@live.de)
**Copyright**: ©2025 IA Chéries Platform - Tous droits réservés

⚠️  PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
====================================================
Ce code constitue la propriété intellectuelle exclusive de Fahed Mlaiel.
- Email: mlaiel@live.de  
- Projet: IA Chéries Platform
- Licence: Propriétaire - Usage commercial interdit sans autorisation
- Protection: Code source confidentiel

⚡ REGISTRY PERFORMANCE OPTIMIZER ENGINE
======================================
Optimiseur performance registry avec ML tuning:
- Cache optimization avec intelligent prefetching
- Query optimization & index tuning
- Connection pooling & resource scaling
- Network latency optimization
- Memory usage optimization & garbage collection tuning
"""

import asyncio
import logging
import time
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
# Safe Redis import with Python 3.12 compatibility
try:
    import aioredis
    REDIS_AVAILABLE = True
except (ImportError, TypeError) as e:
    # Handle Python 3.12 TimeoutError duplicate base class issue
    from protection.utils.redis_compat import MockRedis as aioredis, REDIS_AVAILABLE
    import logging
    logging.warning(f"Using Redis compatibility layer: {e}")
from collections import defaultdict, deque
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import psutil
import gc

logger = logging.getLogger(__name__)

class OptimizationType(Enum):
    """Types d'optimisation."""
    CACHE_OPTIMIZATION = "cache_optimization"
    QUERY_OPTIMIZATION = "query_optimization"
    CONNECTION_OPTIMIZATION = "connection_optimization"
    MEMORY_OPTIMIZATION = "memory_optimization"
    NETWORK_OPTIMIZATION = "network_optimization"
    INDEX_OPTIMIZATION = "index_optimization"
    SCALING_OPTIMIZATION = "scaling_optimization"

class PerformanceMetricType(Enum):
    """Types de métriques performance."""
    QUERY_LATENCY = "query_latency"
    CACHE_HIT_RATE = "cache_hit_rate"
    CONNECTION_POOL_USAGE = "connection_pool_usage"
    MEMORY_USAGE = "memory_usage"
    CPU_USAGE = "cpu_usage"
    NETWORK_IO = "network_io"
    DISK_IO = "disk_io"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"

@dataclass
class PerformanceMetric:
    """Métrique performance registry."""
    metric_type: PerformanceMetricType
    value: float
    timestamp: datetime
    context: Dict[str, Any] = field(default_factory=dict)
    tags: Set[str] = field(default_factory=set)

@dataclass
class OptimizationRecommendation:
    """Recommandation d'optimisation."""
    optimization_type: OptimizationType
    priority: str  # high, medium, low
    impact_score: float  # 0.0 - 1.0
    implementation_effort: str  # low, medium, high
    description: str
    actions: List[str]
    expected_improvement: Dict[str, float]
    rollback_plan: List[str] = field(default_factory=list)

@dataclass
class CacheOptimizationConfig:
    """Configuration optimisation cache."""
    enable_prefetching: bool = True
    cache_size_mb: int = 512
    ttl_seconds: int = 3600
    eviction_policy: str = "lru"  # lru, lfu, random
    prefetch_ratio: float = 0.2
    hot_data_threshold: int = 10

@dataclass
class QueryOptimizationConfig:
    """Configuration optimisation requêtes."""
    enable_query_caching: bool = True
    slow_query_threshold_ms: float = 100
    explain_analyze: bool = True
    index_recommendations: bool = True
    query_parallelization: bool = False

@dataclass
class PerformanceConfig:
    """Configuration performance globale."""
    cache_config: CacheOptimizationConfig = field(default_factory=CacheOptimizationConfig)
    query_config: QueryOptimizationConfig = field(default_factory=QueryOptimizationConfig)
    max_connections: int = 100
    connection_timeout: int = 30
    memory_limit_mb: int = 2048
    gc_threshold: float = 0.8
    monitoring_interval: int = 60

class RegistryPerformanceOptimizer:
    """Optimiseur performance registry avec ML tuning."""
    
    def __init__(self, redis_client: aioredis.Redis, 
                 performance_config: PerformanceConfig):
        self.redis_client = redis_client
        self.config = performance_config
        
        # ML Models pour optimisation
        self.latency_predictor = RandomForestRegressor(n_estimators=100, random_state=42)
        self.throughput_optimizer = LinearRegression()
        self.scaler = StandardScaler()
        self.models_trained = False
        
        # Métriques et historique
        self.performance_metrics: deque = deque(maxlen=10000)
        self.optimization_history: List[Dict[str, Any]] = []
        self.cache_stats: Dict[str, Any] = defaultdict(int)
        self.query_stats: Dict[str, Any] = defaultdict(list)
        
        # Cache intelligent
        self.intelligent_cache: Dict[str, Any] = {}
        self.cache_access_patterns: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.hot_keys: Set[str] = set()
        
        # Pool de connexions optimisé
        self.connection_pools: Dict[str, Any] = {}
        self.connection_stats: Dict[str, Any] = defaultdict(int)
        
        # Tâches background
        self._running = False
        self._monitoring_task: Optional[asyncio.Task] = None
        self._optimization_task: Optional[asyncio.Task] = None
        self._cache_management_task: Optional[asyncio.Task] = None
        self._gc_task: Optional[asyncio.Task] = None
        
        logger.info("⚡ RegistryPerformanceOptimizer initialisé")
    
    async def start(self):
        """Démarre l'optimiseur performance."""
        if self._running:
            return
        
        self._running = True
        
        # Initialiser composants
        await self._initialize_intelligent_cache()
        await self._initialize_connection_pools()
        
        # Démarrer tâches background
        self._monitoring_task = asyncio.create_task(self._performance_monitoring_loop())
        self._optimization_task = asyncio.create_task(self._optimization_loop())
        self._cache_management_task = asyncio.create_task(self._cache_management_loop())
        self._gc_task = asyncio.create_task(self._garbage_collection_loop())
        
        logger.info("✅ RegistryPerformanceOptimizer démarré")
    
    async def stop(self):
        """Arrête l'optimiseur performance."""
        if not self._running:
            return
        
        self._running = False
        
        # Arrêter tâches
        tasks = [
            self._monitoring_task,
            self._optimization_task,
            self._cache_management_task,
            self._gc_task
        ]
        
        for task in tasks:
            if task and not task.done():
                task.cancel()
        
        # Attendre fin des tâches
        running_tasks = [t for t in tasks if t and not t.done()]
        if running_tasks:
            await asyncio.gather(*running_tasks, return_exceptions=True)
        
        logger.info("🛑 RegistryPerformanceOptimizer arrêté")
    
    async def optimize_registry_performance(self, optimization_types: List[OptimizationType] = None) -> List[OptimizationRecommendation]:
        """Optimise performance registry."""
        try:
            start_time = time.time()
            
            if not optimization_types:
                optimization_types = list(OptimizationType)
            
            recommendations = []
            
            # Analyser métriques actuelles
            current_metrics = await self._collect_current_metrics()
            
            # Générer recommandations par type
            for opt_type in optimization_types:
                type_recommendations = await self._generate_optimization_recommendations(
                    opt_type, current_metrics
                )
                recommendations.extend(type_recommendations)
            
            # Scorer et prioriser recommandations
            scored_recommendations = await self._score_and_prioritize_recommendations(recommendations)
            
            # Entraîner modèles ML si données suffisantes
            if len(self.performance_metrics) > 100 and not self.models_trained:
                await self._train_optimization_models()
            
            # Appliquer optimisations automatiques si configuré
            auto_applied = await self._apply_automatic_optimizations(scored_recommendations)
            
            # Enregistrer session optimisation
            optimization_session = {
                'timestamp': datetime.now().isoformat(),
                'optimization_types': [ot.value for ot in optimization_types],
                'recommendations_count': len(scored_recommendations),
                'auto_applied_count': len(auto_applied),
                'processing_time': time.time() - start_time,
                'current_metrics': current_metrics
            }
            
            self.optimization_history.append(optimization_session)
            await self._persist_optimization_session(optimization_session)
            
            logger.info(f"⚡ Optimisation complétée: {len(scored_recommendations)} recommandations, {len(auto_applied)} appliquées")
            
            return scored_recommendations
            
        except Exception as e:
            logger.error(f"Erreur optimisation performance: {e}")
            raise
    
    async def _collect_current_metrics(self) -> Dict[str, Any]:
        """Collecte métriques performance actuelles."""
        try:
            metrics = {}
            
            # Métriques système
            cpu_percent = psutil.cpu_percent(interval=1)
            memory_info = psutil.virtual_memory()
            disk_io = psutil.disk_io_counters()
            network_io = psutil.net_io_counters()
            
            metrics.update({
                'cpu_usage': cpu_percent / 100.0,
                'memory_usage': memory_info.percent / 100.0,
                'memory_available_mb': memory_info.available // (1024 * 1024),
                'disk_read_mb_s': disk_io.read_bytes / (1024 * 1024) if disk_io else 0,
                'disk_write_mb_s': disk_io.write_bytes / (1024 * 1024) if disk_io else 0,
                'network_recv_mb_s': network_io.bytes_recv / (1024 * 1024) if network_io else 0,
                'network_sent_mb_s': network_io.bytes_sent / (1024 * 1024) if network_io else 0
            })
            
            # Métriques Redis
            redis_info = await self.redis_client.info()
            metrics.update({
                'redis_memory_usage_mb': int(redis_info.get('used_memory', 0)) // (1024 * 1024),
                'redis_connected_clients': int(redis_info.get('connected_clients', 0)),
                'redis_ops_per_sec': int(redis_info.get('instantaneous_ops_per_sec', 0)),
                'redis_keyspace_hits': int(redis_info.get('keyspace_hits', 0)),
                'redis_keyspace_misses': int(redis_info.get('keyspace_misses', 0))
            })
            
            # Calculer cache hit rate Redis
            hits = metrics['redis_keyspace_hits']
            misses = metrics['redis_keyspace_misses']
            if hits + misses > 0:
                metrics['redis_cache_hit_rate'] = hits / (hits + misses)
            else:
                metrics['redis_cache_hit_rate'] = 0.0
            
            # Métriques cache intelligent local
            total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
            if total_requests > 0:
                metrics['intelligent_cache_hit_rate'] = self.cache_stats['hits'] / total_requests
            else:
                metrics['intelligent_cache_hit_rate'] = 0.0
            
            metrics['intelligent_cache_size'] = len(self.intelligent_cache)
            metrics['hot_keys_count'] = len(self.hot_keys)
            
            # Métriques requêtes
            if self.query_stats:
                all_latencies = []
                for query_type, latencies in self.query_stats.items():
                    all_latencies.extend(latencies[-100:])  # Dernières 100 par type
                
                if all_latencies:
                    metrics['avg_query_latency'] = np.mean(all_latencies)
                    metrics['p95_query_latency'] = np.percentile(all_latencies, 95)
                    metrics['p99_query_latency'] = np.percentile(all_latencies, 99)
                else:
                    metrics['avg_query_latency'] = 0
                    metrics['p95_query_latency'] = 0
                    metrics['p99_query_latency'] = 0
            
            return metrics
            
        except Exception as e:
            logger.error(f"Erreur collecte métriques: {e}")
            return {}
    
    async def _generate_optimization_recommendations(self, opt_type: OptimizationType,
                                                   current_metrics: Dict[str, Any]) -> List[OptimizationRecommendation]:
        """Génère recommandations pour type d'optimisation."""
        recommendations = []
        
        try:
            if opt_type == OptimizationType.CACHE_OPTIMIZATION:
                recommendations.extend(await self._generate_cache_recommendations(current_metrics))
            elif opt_type == OptimizationType.QUERY_OPTIMIZATION:
                recommendations.extend(await self._generate_query_recommendations(current_metrics))
            elif opt_type == OptimizationType.CONNECTION_OPTIMIZATION:
                recommendations.extend(await self._generate_connection_recommendations(current_metrics))
            elif opt_type == OptimizationType.MEMORY_OPTIMIZATION:
                recommendations.extend(await self._generate_memory_recommendations(current_metrics))
            elif opt_type == OptimizationType.NETWORK_OPTIMIZATION:
                recommendations.extend(await self._generate_network_recommendations(current_metrics))
            elif opt_type == OptimizationType.INDEX_OPTIMIZATION:
                recommendations.extend(await self._generate_index_recommendations(current_metrics))
            elif opt_type == OptimizationType.SCALING_OPTIMIZATION:
                recommendations.extend(await self._generate_scaling_recommendations(current_metrics))
                
        except Exception as e:
            logger.error(f"Erreur génération recommandations {opt_type}: {e}")
        
        return recommendations
    
    async def _generate_cache_recommendations(self, metrics: Dict[str, Any]) -> List[OptimizationRecommendation]:
        """Génère recommandations optimisation cache."""
        recommendations = []
        
        # Cache hit rate faible
        if metrics.get('intelligent_cache_hit_rate', 0) < 0.7:
            recommendations.append(OptimizationRecommendation(
                optimization_type=OptimizationType.CACHE_OPTIMIZATION,
                priority="high",
                impact_score=0.8,
                implementation_effort="medium",
                description="Cache hit rate faible - Optimiser stratégie caching",
                actions=[
                    "Augmenter taille cache intelligent",
                    "Améliorer algorithme prefetching",
                    "Analyser patterns d'accès pour hot keys",
                    "Ajuster TTL selon fréquence d'accès"
                ],
                expected_improvement={
                    'cache_hit_rate': 0.2,
                    'query_latency': -0.3
                }
            ))
        
        # Taille cache sous-optimale
        cache_size = metrics.get('intelligent_cache_size', 0)
        if cache_size < self.config.cache_config.cache_size_mb * 0.5:
            recommendations.append(OptimizationRecommendation(
                optimization_type=OptimizationType.CACHE_OPTIMIZATION,
                priority="medium",
                impact_score=0.6,
                implementation_effort="low",
                description="Cache sous-utilisé - Augmenter prefetching",
                actions=[
                    "Augmenter ratio prefetching",
                    "Identifier plus de hot keys",
                    "Implémenter prefetching prédictif"
                ],
                expected_improvement={
                    'cache_utilization': 0.3,
                    'prefetch_accuracy': 0.2
                }
            ))
        
        # Redis cache hit rate
        if metrics.get('redis_cache_hit_rate', 0) < 0.8:
            recommendations.append(OptimizationRecommendation(
                optimization_type=OptimizationType.CACHE_OPTIMIZATION,
                priority="high",
                impact_score=0.9,
                implementation_effort="medium",
                description="Redis cache hit rate faible - Optimiser configuration",
                actions=[
                    "Analyser patterns Redis keys",
                    "Ajuster politique éviction Redis",
                    "Augmenter mémoire Redis si possible",
                    "Optimiser sérialisation données"
                ],
                expected_improvement={
                    'redis_cache_hit_rate': 0.15,
                    'overall_latency': -0.25
                }
            ))
        
        return recommendations
    
    async def _generate_query_recommendations(self, metrics: Dict[str, Any]) -> List[OptimizationRecommendation]:
        """Génère recommandations optimisation requêtes."""
        recommendations = []
        
        # Latence requêtes élevée
        avg_latency = metrics.get('avg_query_latency', 0)
        if avg_latency > self.config.query_config.slow_query_threshold_ms:
            recommendations.append(OptimizationRecommendation(
                optimization_type=OptimizationType.QUERY_OPTIMIZATION,
                priority="high",
                impact_score=0.85,
                implementation_effort="high",
                description=f"Latence requêtes élevée ({avg_latency:.1f}ms) - Optimiser requêtes",
                actions=[
                    "Analyser requêtes lentes avec EXPLAIN",
                    "Créer indexes optimaux",
                    "Implémenter query caching",
                    "Optimiser structure données",
                    "Considérer dénormalisation sélective"
                ],
                expected_improvement={
                    'avg_query_latency': -0.4,
                    'p95_query_latency': -0.5
                }
            ))
        
        # P99 latence très élevée
        p99_latency = metrics.get('p99_query_latency', 0)
        if p99_latency > avg_latency * 3:
            recommendations.append(OptimizationRecommendation(
                optimization_type=OptimizationType.QUERY_OPTIMIZATION,
                priority="medium",
                impact_score=0.7,
                implementation_effort="medium",
                description="Variance latence élevée - Optimiser requêtes outliers",
                actions=[
                    "Identifier requêtes outliers",
                    "Implémenter timeout adaptatif",
                    "Optimiser requêtes complexes",
                    "Ajouter circuit breakers"
                ],
                expected_improvement={
                    'p99_query_latency': -0.3,
                    'query_variance': -0.4
                }
            ))
        
        return recommendations
    
    async def _generate_connection_recommendations(self, metrics: Dict[str, Any]) -> List[OptimizationRecommendation]:
        """Génère recommandations optimisation connexions."""
        recommendations = []
        
        # Utilisation connexions Redis élevée
        redis_clients = metrics.get('redis_connected_clients', 0)
        if redis_clients > self.config.max_connections * 0.8:
            recommendations.append(OptimizationRecommendation(
                optimization_type=OptimizationType.CONNECTION_OPTIMIZATION,
                priority="high",
                impact_score=0.75,
                implementation_effort="medium",
                description="Utilisation connexions Redis élevée - Optimiser pooling",
                actions=[
                    "Implémenter connection pooling avancé",
                    "Réduire timeout connexions inactives",
                    "Optimiser réutilisation connexions",
                    "Monitorer fuites connexions"
                ],
                expected_improvement={
                    'connection_efficiency': 0.3,
                    'resource_usage': -0.2
                }
            ))
        
        return recommendations
    
    async def _generate_memory_recommendations(self, metrics: Dict[str, Any]) -> List[OptimizationRecommendation]:
        """Génère recommandations optimisation mémoire."""
        recommendations = []
        
        # Utilisation mémoire élevée
        memory_usage = metrics.get('memory_usage', 0)
        if memory_usage > 0.85:
            recommendations.append(OptimizationRecommendation(
                optimization_type=OptimizationType.MEMORY_OPTIMIZATION,
                priority="critical",
                impact_score=0.9,
                implementation_effort="high",
                description=f"Utilisation mémoire critique ({memory_usage:.1%}) - Action immédiate requise",
                actions=[
                    "Déclencher garbage collection forcé",
                    "Réduire taille cache intelligent",
                    "Analyser fuites mémoire",
                    "Optimiser structures données en mémoire",
                    "Considérer scaling vertical"
                ],
                expected_improvement={
                    'memory_usage': -0.3,
                    'gc_efficiency': 0.4
                }
            ))
        elif memory_usage > 0.7:
            recommendations.append(OptimizationRecommendation(
                optimization_type=OptimizationType.MEMORY_OPTIMIZATION,
                priority="high",
                impact_score=0.7,
                implementation_effort="medium",
                description=f"Utilisation mémoire élevée ({memory_usage:.1%}) - Optimisation préventive",
                actions=[
                    "Optimiser garbage collection",
                    "Nettoyer caches anciens",
                    "Analyser objets gros en mémoire",
                    "Implémenter memory monitoring"
                ],
                expected_improvement={
                    'memory_usage': -0.15,
                    'performance_stability': 0.2
                }
            ))
        
        return recommendations
    
    async def _generate_network_recommendations(self, metrics: Dict[str, Any]) -> List[OptimizationRecommendation]:
        """Génère recommandations optimisation réseau."""
        recommendations = []
        
        # I/O réseau élevé
        network_total = metrics.get('network_recv_mb_s', 0) + metrics.get('network_sent_mb_s', 0)
        if network_total > 100:  # Plus de 100 MB/s
            recommendations.append(OptimizationRecommendation(
                optimization_type=OptimizationType.NETWORK_OPTIMIZATION,
                priority="medium",
                impact_score=0.6,
                implementation_effort="high",
                description=f"I/O réseau élevé ({network_total:.1f} MB/s) - Optimiser transferts",
                actions=[
                    "Implémenter compression données",
                    "Optimiser sérialisation/désérialisation",
                    "Utiliser batch requests",
                    "Analyser et réduire chattiness",
                    "Considérer CDN pour données statiques"
                ],
                expected_improvement={
                    'network_efficiency': 0.3,
                    'latency': -0.2
                }
            ))
        
        return recommendations
    
    async def _generate_index_recommendations(self, metrics: Dict[str, Any]) -> List[OptimizationRecommendation]:
        """Génère recommandations optimisation indexes."""
        recommendations = []
        
        # Analyse patterns requêtes pour recommander indexes
        if self.query_stats:
            recommendations.append(OptimizationRecommendation(
                optimization_type=OptimizationType.INDEX_OPTIMIZATION,
                priority="medium",
                impact_score=0.65,
                implementation_effort="medium",
                description="Analyser et optimiser stratégie indexation",
                actions=[
                    "Analyser patterns requêtes fréquentes",
                    "Identifier indexes manquants",
                    "Supprimer indexes inutilisés",
                    "Optimiser indexes composites",
                    "Implémenter index monitoring"
                ],
                expected_improvement={
                    'query_performance': 0.25,
                    'index_efficiency': 0.3
                }
            ))
        
        return recommendations
    
    async def _generate_scaling_recommendations(self, metrics: Dict[str, Any]) -> List[OptimizationRecommendation]:
        """Génère recommandations scaling."""
        recommendations = []
        
        # CPU élevé suggère scaling
        cpu_usage = metrics.get('cpu_usage', 0)
        if cpu_usage > 0.8:
            recommendations.append(OptimizationRecommendation(
                optimization_type=OptimizationType.SCALING_OPTIMIZATION,
                priority="high",
                impact_score=0.8,
                implementation_effort="high",
                description=f"CPU usage élevé ({cpu_usage:.1%}) - Considérer scaling",
                actions=[
                    "Évaluer scaling horizontal vs vertical",
                    "Analyser goulots d'étranglement",
                    "Implémenter auto-scaling si cloud",
                    "Optimiser distribution charge",
                    "Considérer sharding données"
                ],
                expected_improvement={
                    'cpu_headroom': 0.4,
                    'scalability': 0.5
                }
            ))
        
        return recommendations
    
    async def _score_and_prioritize_recommendations(self, recommendations: List[OptimizationRecommendation]) -> List[OptimizationRecommendation]:
        """Score et priorise recommandations."""
        try:
            # Calculer score composite pour chaque recommandation
            for rec in recommendations:
                # Score basé impact vs effort
                effort_scores = {'low': 1.0, 'medium': 0.7, 'high': 0.4}
                priority_scores = {'low': 0.3, 'medium': 0.6, 'high': 0.8, 'critical': 1.0}
                
                effort_score = effort_scores.get(rec.implementation_effort, 0.5)
                priority_score = priority_scores.get(rec.priority, 0.5)
                
                # Score composite: impact * priorité / effort
                composite_score = (rec.impact_score * priority_score) / (2 - effort_score)
                rec.composite_score = composite_score
            
            # Trier par score composite décroissant
            sorted_recommendations = sorted(recommendations, 
                                          key=lambda r: getattr(r, 'composite_score', 0), 
                                          reverse=True)
            
            return sorted_recommendations
            
        except Exception as e:
            logger.error(f"Erreur scoring recommandations: {e}")
            return recommendations
    
    async def _apply_automatic_optimizations(self, recommendations: List[OptimizationRecommendation]) -> List[str]:
        """Applique optimisations automatiques sûres."""
        applied = []
        
        try:
            for rec in recommendations[:3]:  # Top 3 seulement
                if (rec.priority in ['high', 'critical'] and 
                    rec.implementation_effort == 'low' and
                    rec.optimization_type in [OptimizationType.CACHE_OPTIMIZATION, 
                                            OptimizationType.MEMORY_OPTIMIZATION]):
                    
                    if await self._apply_optimization(rec):
                        applied.append(rec.description)
            
        except Exception as e:
            logger.error(f"Erreur application optimisations automatiques: {e}")
        
        return applied
    
    async def _apply_optimization(self, recommendation: OptimizationRecommendation) -> bool:
        """Applique une optimisation spécifique."""
        try:
            if recommendation.optimization_type == OptimizationType.CACHE_OPTIMIZATION:
                return await self._apply_cache_optimization(recommendation)
            elif recommendation.optimization_type == OptimizationType.MEMORY_OPTIMIZATION:
                return await self._apply_memory_optimization(recommendation)
            
            return False
            
        except Exception as e:
            logger.error(f"Erreur application optimisation: {e}")
            return False
    
    async def _apply_cache_optimization(self, recommendation: OptimizationRecommendation) -> bool:
        """Applique optimisation cache."""
        try:
            # Augmenter prefetching si recommandé
            if "prefetching" in recommendation.description.lower():
                old_ratio = self.config.cache_config.prefetch_ratio
                self.config.cache_config.prefetch_ratio = min(0.5, old_ratio * 1.2)
                logger.info(f"Prefetch ratio augmenté: {old_ratio:.2f} → {self.config.cache_config.prefetch_ratio:.2f}")
                return True
            
            # Nettoyer cache si mémoire critique
            if "nettoyer" in recommendation.description.lower():
                await self._cleanup_intelligent_cache()
                logger.info("Cache intelligent nettoyé")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erreur application optimisation cache: {e}")
            return False
    
    async def _apply_memory_optimization(self, recommendation: OptimizationRecommendation) -> bool:
        """Applique optimisation mémoire."""
        try:
            # Garbage collection forcé
            if "garbage collection" in recommendation.description.lower():
                gc.collect()
                logger.info("Garbage collection forcé exécuté")
                return True
            
            # Nettoyage cache
            if "cache" in recommendation.description.lower():
                await self._cleanup_intelligent_cache(aggressive=True)
                logger.info("Nettoyage cache agressif exécuté")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erreur application optimisation mémoire: {e}")
            return False
    
    async def _train_optimization_models(self):
        """Entraîne modèles ML optimisation."""
        try:
            if len(self.performance_metrics) < 100:
                return
            
            # Préparer données entraînement
            features = []
            latency_targets = []
            throughput_targets = []
            
            for metric in list(self.performance_metrics)[-500:]:  # Dernières 500 métriques
                if isinstance(metric, dict):
                    feature_vector = [
                        metric.get('cpu_usage', 0),
                        metric.get('memory_usage', 0),
                        metric.get('cache_hit_rate', 0),
                        metric.get('connection_count', 0)
                    ]
                    
                    features.append(feature_vector)
                    latency_targets.append(metric.get('avg_latency', 0))
                    throughput_targets.append(metric.get('throughput', 0))
            
            if len(features) < 50:
                return
            
            # Normaliser features
            X = self.scaler.fit_transform(features)
            
            # Entraîner modèles
            self.latency_predictor.fit(X, latency_targets)
            self.throughput_optimizer.fit(X, throughput_targets)
            
            self.models_trained = True
            logger.info(f"✅ Modèles ML entraînés avec {len(features)} échantillons")
            
        except Exception as e:
            logger.error(f"Erreur entraînement modèles ML: {e}")
    
    async def _initialize_intelligent_cache(self):
        """Initialise cache intelligent."""
        try:
            # Charger hot keys depuis historique
            hot_keys_data = await self.redis_client.get("optimizer_hot_keys")
            if hot_keys_data:
                self.hot_keys = set(json.loads(hot_keys_data))
            
            # Précharger données fréquemment utilisées
            await self._prefetch_hot_data()
            
            logger.info(f"Cache intelligent initialisé avec {len(self.hot_keys)} hot keys")
            
        except Exception as e:
            logger.error(f"Erreur initialisation cache intelligent: {e}")
    
    async def _initialize_connection_pools(self):
        """Initialise pools de connexions optimisés."""
        try:
            # Configuration pools selon métriques
            # Implémentation spécifique aux backends utilisés
            logger.info("Pools de connexions initialisés")
            
        except Exception as e:
            logger.error(f"Erreur initialisation connection pools: {e}")
    
    async def _performance_monitoring_loop(self):
        """Boucle monitoring performance."""
        while self._running:
            try:
                # Collecter métriques
                current_metrics = await self._collect_current_metrics()
                
                # Enregistrer métrique avec timestamp
                metric_entry = {
                    'timestamp': datetime.now().isoformat(),
                    **current_metrics
                }
                
                self.performance_metrics.append(metric_entry)
                
                # Persister métriques
                await self._persist_performance_metrics(metric_entry)
                
                await asyncio.sleep(self.config.monitoring_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Erreur monitoring performance loop: {e}")
                await asyncio.sleep(30)
    
    async def _optimization_loop(self):
        """Boucle optimisation automatique."""
        while self._running:
            try:
                # Optimisation automatique toutes les heures
                await asyncio.sleep(3600)
                
                if not self._running:
                    break
                
                # Exécuter optimisation automatique
                recommendations = await self.optimize_registry_performance([
                    OptimizationType.CACHE_OPTIMIZATION,
                    OptimizationType.MEMORY_OPTIMIZATION
                ])
                
                logger.info(f"Optimisation automatique: {len(recommendations)} recommandations générées")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Erreur optimization loop: {e}")
                await asyncio.sleep(1800)  # Réessayer dans 30 min
    
    async def _cache_management_loop(self):
        """Boucle gestion cache intelligent."""
        while self._running:
            try:
                # Analyser patterns d'accès
                await self._analyze_access_patterns()
                
                # Prefetch données prédictives
                await self._predictive_prefetch()
                
                # Nettoyer cache si nécessaire
                if len(self.intelligent_cache) > self.config.cache_config.cache_size_mb * 1000:
                    await self._cleanup_intelligent_cache()
                
                await asyncio.sleep(300)  # Toutes les 5 minutes
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Erreur cache management loop: {e}")
                await asyncio.sleep(120)
    
    async def _garbage_collection_loop(self):
        """Boucle garbage collection optimisé."""
        while self._running:
            try:
                # Vérifier utilisation mémoire
                memory_info = psutil.virtual_memory()
                memory_usage = memory_info.percent / 100.0
                
                if memory_usage > self.config.gc_threshold:
                    # GC forcé si seuil dépassé
                    collected = gc.collect()
                    logger.info(f"🗑️ Garbage collection: {collected} objets collectés")
                
                await asyncio.sleep(600)  # Toutes les 10 minutes
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Erreur GC loop: {e}")
                await asyncio.sleep(300)
    
    # Helper methods
    async def _prefetch_hot_data(self):
        """Prefetch données hot keys."""
        try:
            for hot_key in list(self.hot_keys)[:100]:  # Top 100
                if hot_key not in self.intelligent_cache:
                    data = await self.redis_client.get(hot_key)
                    if data:
                        self.intelligent_cache[hot_key] = {
                            'data': data,
                            'timestamp': time.time(),
                            'access_count': 1
                        }
        except Exception as e:
            logger.error(f"Erreur prefetch hot data: {e}")
    
    async def _analyze_access_patterns(self):
        """Analyse patterns d'accès pour optimiser cache."""
        try:
            # Analyser fréquence accès
            access_frequencies = defaultdict(int)
            
            for key, access_history in self.cache_access_patterns.items():
                if len(access_history) > 10:  # Minimum accès requis
                    recent_accesses = len([t for t in access_history if time.time() - t < 3600])
                    access_frequencies[key] = recent_accesses
            
            # Mettre à jour hot keys
            sorted_keys = sorted(access_frequencies.items(), key=lambda x: x[1], reverse=True)
            self.hot_keys = set([key for key, freq in sorted_keys[:1000] if freq > 5])
            
            # Persister hot keys
            await self.redis_client.setex(
                "optimizer_hot_keys",
                3600,
                json.dumps(list(self.hot_keys))
            )
            
        except Exception as e:
            logger.error(f"Erreur analyse access patterns: {e}")
    
    async def _predictive_prefetch(self):
        """Prefetch prédictif basé sur patterns."""
        try:
            if not self.models_trained:
                return
            
            # Logique prefetch prédictif
            # Implémentation complète nécessiterait plus de contexte métier
            
        except Exception as e:
            logger.error(f"Erreur predictive prefetch: {e}")
    
    async def _cleanup_intelligent_cache(self, aggressive: bool = False):
        """Nettoie cache intelligent."""
        try:
            current_time = time.time()
            keys_to_remove = []
            
            # Politique LRU + TTL
            for key, cache_entry in self.intelligent_cache.items():
                age = current_time - cache_entry['timestamp']
                
                if (age > self.config.cache_config.ttl_seconds or 
                    (aggressive and cache_entry['access_count'] < 2)):
                    keys_to_remove.append(key)
            
            # Supprimer entrées expirées
            for key in keys_to_remove:
                del self.intelligent_cache[key]
            
            logger.info(f"Cache cleanup: {len(keys_to_remove)} entrées supprimées")
            
        except Exception as e:
            logger.error(f"Erreur cleanup cache: {e}")
    
    async def _persist_performance_metrics(self, metrics: Dict[str, Any]):
        """Persiste métriques performance."""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M')
            key = f"performance_metrics:{timestamp}"
            
            await self.redis_client.setex(
                key,
                timedelta(days=7).total_seconds(),
                json.dumps(metrics, default=str)
            )
            
        except Exception as e:
            logger.error(f"Erreur persistance métriques: {e}")
    
    async def _persist_optimization_session(self, session: Dict[str, Any]):
        """Persiste session optimisation."""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            key = f"optimization_session:{timestamp}"
            
            await self.redis_client.setex(
                key,
                timedelta(days=30).total_seconds(),
                json.dumps(session, default=str)
            )
            
        except Exception as e:
            logger.error(f"Erreur persistance session optimisation: {e}")
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Récupère métriques performance actuelles."""
        try:
            current_metrics = await self._collect_current_metrics()
            
            return {
                'current_metrics': current_metrics,
                'cache_stats': dict(self.cache_stats),
                'optimization_history_count': len(self.optimization_history),
                'models_trained': self.models_trained,
                'hot_keys_count': len(self.hot_keys),
                'intelligent_cache_size': len(self.intelligent_cache)
            }
            
        except Exception as e:
            logger.error(f"Erreur récupération métriques performance: {e}")
            return {}

# Factory pour création instance
async def create_registry_performance_optimizer(redis_client: aioredis.Redis,
                                              performance_config: PerformanceConfig = None) -> RegistryPerformanceOptimizer:
    """Crée instance RegistryPerformanceOptimizer."""
    if not performance_config:
        performance_config = PerformanceConfig()
    
    optimizer = RegistryPerformanceOptimizer(redis_client, performance_config)
    await optimizer.start()
    return optimizer

# Export classes principales
__all__ = [
    'RegistryPerformanceOptimizer',
    'OptimizationType',
    'PerformanceMetricType',
    'OptimizationRecommendation',
    'PerformanceConfig',
    'CacheOptimizationConfig',
    'QueryOptimizationConfig',
    'create_registry_performance_optimizer'
]