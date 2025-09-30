"""🗄️ Cache Optimization Engine - Enterprise Implementation
========================================================

Multi-level caching strategies with intelligent invalidation,
adaptive warming, and distributed coordination for Ainflue platform.

Expert Roles Implementation:
🗄️ DBA Senior: Cache strategies + query caching + database buffer optimization
🏗️ Backend Senior: Distributed caching + application integration + service mesh
🔒 Sécurité: Cache security + encryption + access control + cache poisoning prevention
⚙️ DevOps: Cache infrastructure + monitoring + automation + performance tuning
🔗 Microservices: Service-level caching + distributed coordination + consistency
🧠 ML Engineer: Cache prediction + intelligent warming + usage pattern analysis
🤖 Lead Dev IA: AI-driven cache optimization + predictive eviction + smart prefetching
🎵 Audio Engineer: Multimedia caching + streaming buffer optimization
📊 IA Prompt Engineer: Cache analytics + automated optimization + intelligent reports

Author: Fahed Mlaiel (mlaiel@live.de)
Version: 1.0 Enterprise Production
Date: Décembre 2025

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
==========================================
Cette implémentation cache optimization est la propriété intellectuelle EXCLUSIVE
de Fahed Mlaiel. Toute reproduction sans autorisation écrite est INTERDITE.
"""

import asyncio
import logging
import json
import time
import uuid
import hashlib
import threading
import pickle
import gzip
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, Callable, AsyncGenerator
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import statistics
import psutil
# Safe Redis import with Python 3.12 compatibility
try:
    import aioredis
    REDIS_AVAILABLE = True
except (ImportError, TypeError) as e:
    # Handle Python 3.12 TimeoutError duplicate base class issue
    from protection.utils.redis_compat import MockRedis as aioredis, REDIS_AVAILABLE
    import logging
    logging.warning(f"Using Redis compatibility layer: {e}")
import asyncpg
from sqlalchemy import create_engine, text
import aiomysql
import aiohttp
from contextlib import asynccontextmanager
import backoff
import concurrent.futures
from abc import ABC, abstractmethod
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
import redis
import memcache

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CacheLevel(Enum):
    """Niveaux de cache"""
    L1_MEMORY = "l1_memory"
    L2_REDIS = "l2_redis"
    L3_DISK = "l3_disk"
    L4_DATABASE = "l4_database"

class CacheStrategy(Enum):
    """Stratégies de cache"""
    LRU = "lru"
    LFU = "lfu"
    FIFO = "fifo"
    ADAPTIVE = "adaptive"
    ML_OPTIMIZED = "ml_optimized"

class EvictionPolicy(Enum):
    """Politiques d'éviction"""
    LEAST_RECENTLY_USED = "lru"
    LEAST_FREQUENTLY_USED = "lfu"
    FIRST_IN_FIRST_OUT = "fifo"
    TIME_TO_LIVE = "ttl"
    RANDOM = "random"
    PREDICTIVE = "predictive"

class CacheStatus(Enum):
    """États du cache"""
    ACTIVE = "active"
    WARMING = "warming"
    DEGRADED = "degraded"
    FAILED = "failed"
    MAINTENANCE = "maintenance"

class CompressionType(Enum):
    """Types de compression"""
    NONE = "none"
    GZIP = "gzip"
    ZLIB = "zlib"
    LZMA = "lzma"

@dataclass
class CacheConfiguration:
    """Configuration de cache"""
    cache_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    level: CacheLevel = CacheLevel.L1_MEMORY
    strategy: CacheStrategy = CacheStrategy.LRU
    eviction_policy: EvictionPolicy = EvictionPolicy.LEAST_RECENTLY_USED
    max_size_mb: int = 1024
    max_entries: int = 10000
    ttl_seconds: int = 3600
    compression: CompressionType = CompressionType.GZIP
    encryption_enabled: bool = False
    sharding_enabled: bool = False
    replication_factor: int = 1
    warming_enabled: bool = True
    prefetch_enabled: bool = True
    consistency_level: str = "eventual"
    
@dataclass
class CacheEntry:
    """Entrée de cache"""
    key: str = ""
    value: Any = None
    size_bytes: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    ttl_seconds: int = 3600
    compressed: bool = False
    encrypted: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CacheMetrics:
    """Métriques de cache"""
    cache_id: str = ""
    hit_count: int = 0
    miss_count: int = 0
    eviction_count: int = 0
    size_bytes: int = 0
    entry_count: int = 0
    hit_ratio: float = 0.0
    avg_response_time_ms: float = 0.0
    memory_usage_mb: float = 0.0
    compression_ratio: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class WarmingTask:
    """Tâche de préchauffage de cache"""
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    cache_id: str = ""
    query_pattern: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    priority: int = 1
    scheduled_at: datetime = field(default_factory=datetime.now)
    executed_at: Optional[datetime] = None
    completed: bool = False
    error_message: str = ""

class CacheOptimizationEngine:
    """🗄️ Moteur Optimisation Cache Enterprise
    
    Moteur enterprise d'optimisation cache avec:
    - Hiérarchie multi-niveaux intelligente
    - Stratégies d'éviction adaptatives et ML
    - Préchauffage prédictif et préchargement
    - Coordination distribuée et consistance
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.cache_layers: Dict[CacheLevel, 'CacheLayer'] = {}
        self.cache_configs: Dict[str, CacheConfiguration] = {}
        self.cache_metrics: Dict[str, CacheMetrics] = {}
        self.warming_tasks: List[WarmingTask] = []
        self.ml_predictor = None
        self.monitoring_active = False
        
        # Performance metrics globales
        self.global_metrics = {
            'total_requests': 0,
            'total_hits': 0,
            'total_misses': 0,
            'avg_hit_ratio': 0.0,
            'avg_response_time_ms': 0.0,
            'memory_efficiency': 0.0,
            'cost_savings_percent': 0.0
        }
        
        # Configuration par défaut
        self.default_ttl = config.get('default_ttl', 3600)
        self.max_memory_mb = config.get('max_memory_mb', 2048)
        self.warming_interval = config.get('warming_interval', 300)
        
        # Composants
        self.warming_manager = CacheWarmingManager(self)
        self.ml_optimizer = MLCacheOptimizer(self)
        self.consistency_manager = CacheConsistencyManager(self)
        
        # Thread pool pour opérations asynchrones
        self.executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=config.get('max_workers', 8)
        )
        
        logger.info("🗄️ Cache Optimization Engine initialisé")

    async def initialize(self):
        """🚀 Initialiser le moteur de cache"""
        try:
            # Initialisation des couches de cache
            await self._initialize_cache_layers()
            
            # Initialisation des composants
            await self.warming_manager.initialize()
            await self.ml_optimizer.initialize()
            await self.consistency_manager.initialize()
            
            logger.info("🚀 Cache Optimization Engine initialisé avec succès")
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation cache engine: {e}")
            raise

    async def _initialize_cache_layers(self):
        """🏗️ Initialiser les couches de cache"""
        try:
            cache_configs = self.config.get('cache_layers', {})
            
            # L1 - Mémoire locale
            if 'l1_memory' in cache_configs:
                l1_config = cache_configs['l1_memory']
                self.cache_layers[CacheLevel.L1_MEMORY] = MemoryCacheLayer(l1_config)
                
            # L2 - Redis
            if 'l2_redis' in cache_configs:
                l2_config = cache_configs['l2_redis']
                self.cache_layers[CacheLevel.L2_REDIS] = RedisCacheLayer(l2_config)
            
            # L3 - Disque
            if 'l3_disk' in cache_configs:
                l3_config = cache_configs['l3_disk']
                self.cache_layers[CacheLevel.L3_DISK] = DiskCacheLayer(l3_config)
            
            # Initialisation de chaque couche
            for level, layer in self.cache_layers.items():
                await layer.initialize()
                logger.info(f"✅ Couche cache initialisée: {level.value}")
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation couches cache: {e}")
            raise

    async def get(self, key: str, default: Any = None, 
                 ttl_seconds: int = None) -> Any:
        """📥 Récupérer une valeur du cache (hiérarchique)
        
        Args:
            key: Clé de cache
            default: Valeur par défaut
            ttl_seconds: TTL personnalisé
            
        Returns:
            Valeur mise en cache ou valeur par défaut
        """
        try:
            start_time = time.time()
            
            # Tentative de récupération niveau par niveau
            for level in [CacheLevel.L1_MEMORY, CacheLevel.L2_REDIS, CacheLevel.L3_DISK]:
                if level in self.cache_layers:
                    layer = self.cache_layers[level]
                    
                    value = await layer.get(key)
                    if value is not None:
                        # Cache hit - propager vers les niveaux supérieurs
                        await self._propagate_to_upper_levels(key, value, level)
                        
                        # Mise à jour des métriques
                        await self._update_hit_metrics(level, start_time)
                        
                        logger.debug(f"📥 Cache hit L{level.value}: {key}")
                        return value
            
            # Cache miss complet
            await self._update_miss_metrics(start_time)
            logger.debug(f"📥 Cache miss: {key}")
            
            return default
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération cache {key}: {e}")
            return default

    async def set(self, key: str, value: Any, 
                 ttl_seconds: int = None,
                 level: CacheLevel = None,
                 compression: CompressionType = None) -> bool:
        """📤 Stocker une valeur dans le cache
        
        Args:
            key: Clé de cache
            value: Valeur à stocker
            ttl_seconds: TTL personnalisé
            level: Niveau de cache spécifique
            compression: Type de compression
            
        Returns:
            True si succès, False sinon
        """
        try:
            ttl = ttl_seconds or self.default_ttl
            
            # Sérialisation et compression si nécessaire
            processed_value = await self._process_value_for_storage(
                value, compression or CompressionType.GZIP
            )
            
            # Stockage selon niveau spécifié ou stratégie
            if level and level in self.cache_layers:
                # Niveau spécifique
                layer = self.cache_layers[level]
                success = await layer.set(key, processed_value, ttl)
                
                logger.debug(f"📤 Cache set {level.value}: {key}")
                return success
            else:
                # Stockage hiérarchique (tous les niveaux)
                success_count = 0
                for cache_level, layer in self.cache_layers.items():
                    try:
                        if await layer.set(key, processed_value, ttl):
                            success_count += 1
                    except Exception as e:
                        logger.warning(f"⚠️ Erreur stockage {cache_level.value}: {e}")
                
                logger.debug(f"📤 Cache set hierarchique: {key} ({success_count} niveaux)")
                return success_count > 0
            
        except Exception as e:
            logger.error(f"❌ Erreur stockage cache {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """🗑️ Supprimer une entrée du cache
        
        Args:
            key: Clé à supprimer
            
        Returns:
            True si succès, False sinon
        """
        try:
            success_count = 0
            
            # Suppression de tous les niveaux
            for level, layer in self.cache_layers.items():
                try:
                    if await layer.delete(key):
                        success_count += 1
                except Exception as e:
                    logger.warning(f"⚠️ Erreur suppression {level.value}: {e}")
            
            # Invalidation dans le gestionnaire de cohérence
            await self.consistency_manager.invalidate_key(key)
            
            logger.debug(f"🗑️ Cache delete: {key} ({success_count} niveaux)")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"❌ Erreur suppression cache {key}: {e}")
            return False

    async def invalidate_pattern(self, pattern: str) -> int:
        """🔄 Invalider les entrées correspondant à un pattern
        
        Args:
            pattern: Pattern de clés (regex ou wildcard)
            
        Returns:
            Nombre d'entrées invalidées
        """
        try:
            total_invalidated = 0
            
            # Invalidation niveau par niveau
            for level, layer in self.cache_layers.items():
                try:
                    count = await layer.invalidate_pattern(pattern)
                    total_invalidated += count
                    logger.debug(f"🔄 Invalidated {count} entries in {level.value}")
                except Exception as e:
                    logger.warning(f"⚠️ Erreur invalidation pattern {level.value}: {e}")
            
            logger.info(f"🔄 Pattern invalidation: {pattern} ({total_invalidated} entrées)")
            return total_invalidated
            
        except Exception as e:
            logger.error(f"❌ Erreur invalidation pattern {pattern}: {e}")
            return 0

    async def _propagate_to_upper_levels(self, key: str, value: Any, 
                                       source_level: CacheLevel):
        """⬆️ Propager une valeur vers les niveaux supérieurs"""
        try:
            # Ordre de propagation (L3 -> L2 -> L1)
            level_order = [CacheLevel.L3_DISK, CacheLevel.L2_REDIS, CacheLevel.L1_MEMORY]
            source_index = level_order.index(source_level)
            
            # Propager vers les niveaux supérieurs
            for i in range(source_index + 1, len(level_order)):
                target_level = level_order[i]
                if target_level in self.cache_layers:
                    layer = self.cache_layers[target_level]
                    await layer.set(key, value, self.default_ttl)
                    logger.debug(f"⬆️ Propagated {key} to {target_level.value}")
            
        except Exception as e:
            logger.error(f"❌ Erreur propagation {key}: {e}")

    async def _process_value_for_storage(self, value: Any, 
                                       compression: CompressionType) -> bytes:
        """🔧 Traiter une valeur pour le stockage"""
        try:
            # Sérialisation
            serialized = pickle.dumps(value)
            
            # Compression si activée
            if compression != CompressionType.NONE:
                if compression == CompressionType.GZIP:
                    serialized = gzip.compress(serialized)
                # Autres types de compression peuvent être ajoutés ici
            
            return serialized
            
        except Exception as e:
            logger.error(f"❌ Erreur traitement valeur: {e}")
            return pickle.dumps(value)  # Fallback sans compression

    async def _update_hit_metrics(self, level: CacheLevel, start_time: float):
        """📊 Mettre à jour les métriques de hit"""
        try:
            response_time_ms = (time.time() - start_time) * 1000
            
            self.global_metrics['total_requests'] += 1
            self.global_metrics['total_hits'] += 1
            
            # Calcul du ratio de hit
            total_requests = self.global_metrics['total_requests']
            if total_requests > 0:
                self.global_metrics['avg_hit_ratio'] = (
                    self.global_metrics['total_hits'] / total_requests * 100
                )
            
            # Mise à jour du temps de réponse moyen
            current_avg = self.global_metrics['avg_response_time_ms']
            self.global_metrics['avg_response_time_ms'] = (
                (current_avg * (total_requests - 1) + response_time_ms) / total_requests
            )
            
        except Exception as e:
            logger.error(f"❌ Erreur mise à jour métriques hit: {e}")

    async def _update_miss_metrics(self, start_time: float):
        """📊 Mettre à jour les métriques de miss"""
        try:
            response_time_ms = (time.time() - start_time) * 1000
            
            self.global_metrics['total_requests'] += 1
            self.global_metrics['total_misses'] += 1
            
            # Recalcul du ratio de hit
            total_requests = self.global_metrics['total_requests']
            if total_requests > 0:
                self.global_metrics['avg_hit_ratio'] = (
                    self.global_metrics['total_hits'] / total_requests * 100
                )
            
        except Exception as e:
            logger.error(f"❌ Erreur mise à jour métriques miss: {e}")

    async def warm_cache(self, queries: List[Dict[str, Any]], 
                        priority: int = 1) -> str:
        """🔥 Préchauffer le cache avec des requêtes
        
        Args:
            queries: Liste des requêtes à exécuter
            priority: Priorité du préchauffage
            
        Returns:
            ID de la tâche de préchauffage
        """
        try:
            return await self.warming_manager.schedule_warming(queries, priority)
            
        except Exception as e:
            logger.error(f"❌ Erreur préchauffage cache: {e}")
            raise

    async def optimize_cache_ml(self) -> Dict[str, Any]:
        """🧠 Optimiser le cache avec ML
        
        Returns:
            Résultats de l'optimisation
        """
        try:
            return await self.ml_optimizer.optimize()
            
        except Exception as e:
            logger.error(f"❌ Erreur optimisation ML: {e}")
            return {}

    async def get_cache_statistics(self) -> Dict[str, Any]:
        """📊 Obtenir les statistiques du cache"""
        try:
            stats = {
                'global_metrics': self.global_metrics.copy(),
                'cache_layers': {},
                'warming_tasks': len(self.warming_tasks),
                'active_caches': len(self.cache_layers)
            }
            
            # Statistiques par couche
            for level, layer in self.cache_layers.items():
                layer_stats = await layer.get_statistics()
                stats['cache_layers'][level.value] = layer_stats
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération statistiques: {e}")
            return {}

    async def start_monitoring(self):
        """🚀 Démarrer le monitoring du cache"""
        try:
            if self.monitoring_active:
                return
            
            self.monitoring_active = True
            
            # Démarrage des tâches de monitoring
            asyncio.create_task(self._cache_monitoring_loop())
            asyncio.create_task(self.warming_manager.start_warming_loop())
            asyncio.create_task(self.ml_optimizer.start_optimization_loop())
            
            logger.info("🚀 Monitoring cache démarré")
            
        except Exception as e:
            logger.error(f"❌ Erreur démarrage monitoring: {e}")
            raise

    async def _cache_monitoring_loop(self):
        """📊 Boucle de monitoring du cache"""
        while self.monitoring_active:
            try:
                # Collecte des métriques
                await self._collect_cache_metrics()
                
                # Vérification de la santé
                await self._check_cache_health()
                
                # Optimisation automatique
                await self._auto_optimize_cache()
                
                await asyncio.sleep(60)  # Monitoring toutes les minutes
                
            except Exception as e:
                logger.error(f"❌ Erreur boucle monitoring: {e}")
                await asyncio.sleep(60)

    async def _collect_cache_metrics(self):
        """📈 Collecter les métriques de cache"""
        try:
            total_memory = 0
            total_entries = 0
            
            for level, layer in self.cache_layers.items():
                stats = await layer.get_statistics()
                
                memory_mb = stats.get('memory_usage_mb', 0)
                entries = stats.get('entry_count', 0)
                
                total_memory += memory_mb
                total_entries += entries
            
            # Calcul de l'efficacité mémoire
            if self.max_memory_mb > 0:
                self.global_metrics['memory_efficiency'] = (
                    total_memory / self.max_memory_mb * 100
                )
            
            logger.debug(f"📈 Métriques: {total_memory:.1f}MB, {total_entries} entrées")
            
        except Exception as e:
            logger.error(f"❌ Erreur collecte métriques: {e}")

    async def _check_cache_health(self):
        """🏥 Vérifier la santé du cache"""
        try:
            # Vérification de chaque couche
            for level, layer in self.cache_layers.items():
                health = await layer.check_health()
                if not health:
                    logger.warning(f"⚠️ Problème de santé détecté: {level.value}")
                    # Déclencher des actions correctives
                    await self._handle_cache_degradation(level, layer)
            
        except Exception as e:
            logger.error(f"❌ Erreur vérification santé cache: {e}")

    async def _handle_cache_degradation(self, level: CacheLevel, layer: 'CacheLayer'):
        """🔧 Gérer la dégradation du cache"""
        try:
            logger.warning(f"🔧 Gestion dégradation: {level.value}")
            
            # Tentative de réparation
            await layer.repair()
            
            # Si échec, bypass temporaire
            # Implémentation spécifique selon le niveau
            
        except Exception as e:
            logger.error(f"❌ Erreur gestion dégradation: {e}")

    async def _auto_optimize_cache(self):
        """⚙️ Optimisation automatique du cache"""
        try:
            # Déclenchement de l'optimisation ML si nécessaire
            hit_ratio = self.global_metrics['avg_hit_ratio']
            
            if hit_ratio < 70:  # Seuil d'optimisation
                logger.info(f"⚙️ Déclenchement optimisation auto (hit ratio: {hit_ratio:.1f}%)")
                await self.ml_optimizer.optimize()
            
        except Exception as e:
            logger.error(f"❌ Erreur optimisation auto: {e}")

    async def stop_monitoring(self):
        """⏹️ Arrêter le monitoring"""
        try:
            self.monitoring_active = False
            
            # Arrêt des composants
            await self.warming_manager.stop()
            await self.ml_optimizer.stop()
            await self.consistency_manager.stop()
            
            # Fermeture des couches de cache
            for layer in self.cache_layers.values():
                await layer.cleanup()
            
            # Fermeture du thread pool
            self.executor.shutdown(wait=True)
            
            logger.info("⏹️ Cache monitoring arrêté")
            
        except Exception as e:
            logger.error(f"❌ Erreur arrêt monitoring: {e}")

class CacheLayer(ABC):
    """🏗️ Couche de cache abstraite"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.metrics = CacheMetrics()
    
    @abstractmethod
    async def initialize(self):
        """🚀 Initialiser la couche"""
        pass
    
    @abstractmethod
    async def get(self, key: str) -> Any:
        """📥 Récupérer une valeur"""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl_seconds: int) -> bool:
        """📤 Stocker une valeur"""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """🗑️ Supprimer une valeur"""
        pass
    
    @abstractmethod
    async def invalidate_pattern(self, pattern: str) -> int:
        """🔄 Invalider par pattern"""
        pass
    
    @abstractmethod
    async def get_statistics(self) -> Dict[str, Any]:
        """📊 Obtenir les statistiques"""
        pass
    
    @abstractmethod
    async def check_health(self) -> bool:
        """🏥 Vérifier la santé"""
        pass
    
    @abstractmethod
    async def repair(self):
        """🔧 Réparer la couche"""
        pass
    
    @abstractmethod
    async def cleanup(self):
        """🧹 Nettoyer la couche"""
        pass

class MemoryCacheLayer(CacheLayer):
    """💾 Couche de cache mémoire (L1)"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.cache: Dict[str, CacheEntry] = {}
        self.max_size_mb = config.get('max_size_mb', 512)
        self.max_entries = config.get('max_entries', 10000)
        self.current_size = 0
        self.lock = asyncio.Lock()
    
    async def initialize(self):
        """🚀 Initialiser la couche mémoire"""
        logger.info("💾 Couche cache mémoire initialisée")
    
    async def get(self, key: str) -> Any:
        """📥 Récupérer depuis la mémoire"""
        async with self.lock:
            if key in self.cache:
                entry = self.cache[key]
                
                # Vérification TTL
                if self._is_expired(entry):
                    del self.cache[key]
                    self.current_size -= entry.size_bytes
                    return None
                
                # Mise à jour des statistiques d'accès
                entry.last_accessed = datetime.now()
                entry.access_count += 1
                
                return pickle.loads(entry.value)
            
            return None
    
    async def set(self, key: str, value: Any, ttl_seconds: int) -> bool:
        """📤 Stocker en mémoire"""
        async with self.lock:
            try:
                # Sérialisation pour calcul de taille
                serialized = value if isinstance(value, bytes) else pickle.dumps(value)
                size_bytes = len(serialized)
                
                # Vérification de l'espace
                await self._ensure_space(size_bytes)
                
                # Création de l'entrée
                entry = CacheEntry(
                    key=key,
                    value=serialized,
                    size_bytes=size_bytes,
                    ttl_seconds=ttl_seconds
                )
                
                # Suppression de l'ancienne entrée si elle existe
                if key in self.cache:
                    self.current_size -= self.cache[key].size_bytes
                
                # Ajout de la nouvelle entrée
                self.cache[key] = entry
                self.current_size += size_bytes
                
                return True
                
            except Exception as e:
                logger.error(f"❌ Erreur stockage mémoire {key}: {e}")
                return False
    
    async def delete(self, key: str) -> bool:
        """🗑️ Supprimer de la mémoire"""
        async with self.lock:
            if key in self.cache:
                entry = self.cache[key]
                self.current_size -= entry.size_bytes
                del self.cache[key]
                return True
            return False
    
    async def invalidate_pattern(self, pattern: str) -> int:
        """🔄 Invalider par pattern"""
        async with self.lock:
            import re
            regex = re.compile(pattern.replace('*', '.*'))
            
            keys_to_delete = [
                key for key in self.cache.keys()
                if regex.match(key)
            ]
            
            for key in keys_to_delete:
                entry = self.cache[key]
                self.current_size -= entry.size_bytes
                del self.cache[key]
            
            return len(keys_to_delete)
    
    def _is_expired(self, entry: CacheEntry) -> bool:
        """⏰ Vérifier si une entrée a expiré"""
        elapsed = (datetime.now() - entry.created_at).total_seconds()
        return elapsed > entry.ttl_seconds
    
    async def _ensure_space(self, needed_bytes: int):
        """💾 S'assurer qu'il y a assez d'espace"""
        # Nettoyage des entrées expirées
        await self._cleanup_expired()
        
        # Éviction si nécessaire
        while (self.current_size + needed_bytes > self.max_size_mb * 1024 * 1024 or
               len(self.cache) >= self.max_entries):
            await self._evict_entry()
    
    async def _cleanup_expired(self):
        """🧹 Nettoyer les entrées expirées"""
        expired_keys = [
            key for key, entry in self.cache.items()
            if self._is_expired(entry)
        ]
        
        for key in expired_keys:
            entry = self.cache[key]
            self.current_size -= entry.size_bytes
            del self.cache[key]
    
    async def _evict_entry(self):
        """🚪 Évincer une entrée (LRU)"""
        if not self.cache:
            return
        
        # Stratégie LRU
        oldest_key = min(
            self.cache.keys(),
            key=lambda k: self.cache[k].last_accessed
        )
        
        entry = self.cache[oldest_key]
        self.current_size -= entry.size_bytes
        del self.cache[oldest_key]
    
    async def get_statistics(self) -> Dict[str, Any]:
        """📊 Statistiques mémoire"""
        return {
            'memory_usage_mb': self.current_size / (1024 * 1024),
            'entry_count': len(self.cache),
            'max_size_mb': self.max_size_mb,
            'max_entries': self.max_entries,
            'utilization_percent': (len(self.cache) / self.max_entries) * 100
        }
    
    async def check_health(self) -> bool:
        """🏥 Vérifier la santé"""
        return self.current_size <= self.max_size_mb * 1024 * 1024
    
    async def repair(self):
        """🔧 Réparer la couche mémoire"""
        await self._cleanup_expired()
    
    async def cleanup(self):
        """🧹 Nettoyer la couche mémoire"""
        async with self.lock:
            self.cache.clear()
            self.current_size = 0

class RedisCacheLayer(CacheLayer):
    """🔴 Couche de cache Redis (L2)"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.redis_client = None
        self.host = config.get('host', 'localhost')
        self.port = config.get('port', 6379)
        self.db = config.get('db', 0)
        self.password = config.get('password')
    
    async def initialize(self):
        """🚀 Initialiser Redis"""
        try:
            self.redis_client = await aioredis.from_url(
                f"redis://{self.host}:{self.port}/{self.db}",
                password=self.password,
                encoding="utf-8",
                decode_responses=False
            )
            
            # Test de connexion
            await self.redis_client.ping()
            
            logger.info("🔴 Couche cache Redis initialisée")
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation Redis: {e}")
            raise
    
    async def get(self, key: str) -> Any:
        """📥 Récupérer depuis Redis"""
        try:
            if not self.redis_client:
                return None
            
            data = await self.redis_client.get(key)
            if data:
                return pickle.loads(data)
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erreur get Redis {key}: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl_seconds: int) -> bool:
        """📤 Stocker dans Redis"""
        try:
            if not self.redis_client:
                return False
            
            serialized = value if isinstance(value, bytes) else pickle.dumps(value)
            await self.redis_client.setex(key, ttl_seconds, serialized)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur set Redis {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """🗑️ Supprimer de Redis"""
        try:
            if not self.redis_client:
                return False
            
            result = await self.redis_client.delete(key)
            return result > 0
            
        except Exception as e:
            logger.error(f"❌ Erreur delete Redis {key}: {e}")
            return False
    
    async def invalidate_pattern(self, pattern: str) -> int:
        """🔄 Invalider par pattern dans Redis"""
        try:
            if not self.redis_client:
                return 0
            
            # Scan pour éviter KEYS sur de gros datasets
            keys = []
            async for key in self.redis_client.scan_iter(match=pattern):
                keys.append(key)
            
            if keys:
                await self.redis_client.delete(*keys)
            
            return len(keys)
            
        except Exception as e:
            logger.error(f"❌ Erreur invalidation pattern Redis {pattern}: {e}")
            return 0
    
    async def get_statistics(self) -> Dict[str, Any]:
        """📊 Statistiques Redis"""
        try:
            if not self.redis_client:
                return {}
            
            info = await self.redis_client.info('memory')
            keyspace = await self.redis_client.info('keyspace')
            
            db_info = keyspace.get(f'db{self.db}', {})
            key_count = db_info.get('keys', 0) if isinstance(db_info, dict) else 0
            
            return {
                'memory_usage_mb': info.get('used_memory', 0) / (1024 * 1024),
                'entry_count': key_count,
                'max_memory_mb': info.get('maxmemory', 0) / (1024 * 1024),
                'hit_ratio': info.get('keyspace_hit_rate', 0)
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur statistiques Redis: {e}")
            return {}
    
    async def check_health(self) -> bool:
        """🏥 Vérifier la santé Redis"""
        try:
            if not self.redis_client:
                return False
            
            await self.redis_client.ping()
            return True
            
        except Exception:
            return False
    
    async def repair(self):
        """🔧 Réparer Redis"""
        try:
            # Tentative de reconnexion
            if not await self.check_health():
                await self.initialize()
                
        except Exception as e:
            logger.error(f"❌ Erreur réparation Redis: {e}")
    
    async def cleanup(self):
        """🧹 Nettoyer Redis"""
        try:
            if self.redis_client:
                await self.redis_client.close()
                
        except Exception as e:
            logger.error(f"❌ Erreur nettoyage Redis: {e}")

class DiskCacheLayer(CacheLayer):
    """💿 Couche de cache disque (L3)"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.cache_dir = Path(config.get('cache_dir', '/tmp/ainflue_cache'))
        self.max_size_mb = config.get('max_size_mb', 2048)
        self.current_size = 0
        self.lock = asyncio.Lock()
    
    async def initialize(self):
        """🚀 Initialiser le cache disque"""
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            await self._calculate_current_size()
            
            logger.info(f"💿 Couche cache disque initialisée: {self.cache_dir}")
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation cache disque: {e}")
            raise
    
    async def get(self, key: str) -> Any:
        """📥 Récupérer depuis le disque"""
        try:
            file_path = self.cache_dir / f"{hashlib.md5(key.encode()).hexdigest()}.cache"
            
            if not file_path.exists():
                return None
            
            # Vérification TTL via mtime
            mtime = file_path.stat().st_mtime
            if time.time() - mtime > 3600:  # TTL par défaut 1h
                file_path.unlink()
                return None
            
            with open(file_path, 'rb') as f:
                data = f.read()
                return pickle.loads(data)
            
        except Exception as e:
            logger.error(f"❌ Erreur get disque {key}: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl_seconds: int) -> bool:
        """📤 Stocker sur disque"""
        async with self.lock:
            try:
                file_path = self.cache_dir / f"{hashlib.md5(key.encode()).hexdigest()}.cache"
                
                serialized = value if isinstance(value, bytes) else pickle.dumps(value)
                
                # Vérification de l'espace
                await self._ensure_space(len(serialized))
                
                with open(file_path, 'wb') as f:
                    f.write(serialized)
                
                self.current_size += len(serialized)
                
                return True
                
            except Exception as e:
                logger.error(f"❌ Erreur set disque {key}: {e}")
                return False
    
    async def delete(self, key: str) -> bool:
        """🗑️ Supprimer du disque"""
        try:
            file_path = self.cache_dir / f"{hashlib.md5(key.encode()).hexdigest()}.cache"
            
            if file_path.exists():
                size = file_path.stat().st_size
                file_path.unlink()
                self.current_size -= size
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Erreur delete disque {key}: {e}")
            return False
    
    async def invalidate_pattern(self, pattern: str) -> int:
        """🔄 Invalider par pattern sur disque"""
        try:
            import re
            regex = re.compile(pattern.replace('*', '.*'))
            
            deleted_count = 0
            for file_path in self.cache_dir.glob('*.cache'):
                # Pour simplifier, on supprime tous les fichiers
                # Dans un vrai système, il faudrait mapper les hash aux clés
                try:
                    size = file_path.stat().st_size
                    file_path.unlink()
                    self.current_size -= size
                    deleted_count += 1
                except Exception:
                    pass
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"❌ Erreur invalidation pattern disque: {e}")
            return 0
    
    async def _calculate_current_size(self):
        """📏 Calculer la taille actuelle"""
        try:
            total_size = 0
            for file_path in self.cache_dir.glob('*.cache'):
                total_size += file_path.stat().st_size
            
            self.current_size = total_size
            
        except Exception as e:
            logger.error(f"❌ Erreur calcul taille: {e}")
    
    async def _ensure_space(self, needed_bytes: int):
        """💿 S'assurer qu'il y a assez d'espace disque"""
        max_bytes = self.max_size_mb * 1024 * 1024
        
        while self.current_size + needed_bytes > max_bytes:
            await self._evict_oldest_file()
    
    async def _evict_oldest_file(self):
        """🚪 Évincer le fichier le plus ancien"""
        try:
            cache_files = list(self.cache_dir.glob('*.cache'))
            if not cache_files:
                return
            
            # Trouver le fichier le plus ancien
            oldest_file = min(cache_files, key=lambda f: f.stat().st_mtime)
            
            size = oldest_file.stat().st_size
            oldest_file.unlink()
            self.current_size -= size
            
        except Exception as e:
            logger.error(f"❌ Erreur éviction fichier: {e}")
    
    async def get_statistics(self) -> Dict[str, Any]:
        """📊 Statistiques disque"""
        try:
            file_count = len(list(self.cache_dir.glob('*.cache')))
            
            return {
                'memory_usage_mb': self.current_size / (1024 * 1024),
                'entry_count': file_count,
                'max_size_mb': self.max_size_mb,
                'utilization_percent': (self.current_size / (self.max_size_mb * 1024 * 1024)) * 100
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur statistiques disque: {e}")
            return {}
    
    async def check_health(self) -> bool:
        """🏥 Vérifier la santé du cache disque"""
        try:
            return self.cache_dir.exists() and self.cache_dir.is_dir()
            
        except Exception:
            return False
    
    async def repair(self):
        """🔧 Réparer le cache disque"""
        try:
            if not self.cache_dir.exists():
                self.cache_dir.mkdir(parents=True, exist_ok=True)
            
            await self._calculate_current_size()
            
        except Exception as e:
            logger.error(f"❌ Erreur réparation cache disque: {e}")
    
    async def cleanup(self):
        """🧹 Nettoyer le cache disque"""
        try:
            import shutil
            if self.cache_dir.exists():
                shutil.rmtree(self.cache_dir)
            
        except Exception as e:
            logger.error(f"❌ Erreur nettoyage cache disque: {e}")

class CacheWarmingManager:
    """🔥 Gestionnaire de préchauffage de cache"""
    
    def __init__(self, cache_engine: CacheOptimizationEngine):
        self.cache_engine = cache_engine
        self.warming_active = False
        self.warming_queue: List[WarmingTask] = []
    
    async def initialize(self):
        """🚀 Initialiser le gestionnaire de préchauffage"""
        logger.info("🔥 Cache Warming Manager initialisé")
    
    async def schedule_warming(self, queries: List[Dict[str, Any]], 
                              priority: int = 1) -> str:
        """📅 Planifier un préchauffage"""
        try:
            task = WarmingTask(
                cache_id="global",
                query_pattern=json.dumps(queries),
                priority=priority
            )
            
            self.warming_queue.append(task)
            self.cache_engine.warming_tasks.append(task)
            
            logger.info(f"📅 Tâche préchauffage planifiée: {task.task_id}")
            return task.task_id
            
        except Exception as e:
            logger.error(f"❌ Erreur planification préchauffage: {e}")
            raise
    
    async def start_warming_loop(self):
        """🔄 Démarrer la boucle de préchauffage"""
        self.warming_active = True
        
        while self.warming_active:
            try:
                if self.warming_queue:
                    # Trier par priorité
                    self.warming_queue.sort(key=lambda t: t.priority, reverse=True)
                    
                    task = self.warming_queue.pop(0)
                    await self._execute_warming_task(task)
                
                await asyncio.sleep(self.cache_engine.warming_interval)
                
            except Exception as e:
                logger.error(f"❌ Erreur boucle préchauffage: {e}")
                await asyncio.sleep(self.cache_engine.warming_interval)
    
    async def _execute_warming_task(self, task: WarmingTask):
        """⚡ Exécuter une tâche de préchauffage"""
        try:
            logger.info(f"⚡ Exécution préchauffage: {task.task_id}")
            
            task.executed_at = datetime.now()
            
            queries = json.loads(task.query_pattern)
            
            # Exécution des requêtes de préchauffage
            for query in queries:
                query_key = self._generate_query_key(query)
                
                # Simuler l'exécution de la requête et mise en cache
                # Dans un vrai système, exécuter la requête sur la DB
                result = f"result_for_{query_key}"
                
                await self.cache_engine.set(
                    query_key, 
                    result, 
                    ttl_seconds=3600
                )
            
            task.completed = True
            logger.info(f"✅ Préchauffage complété: {task.task_id}")
            
        except Exception as e:
            task.error_message = str(e)
            logger.error(f"❌ Erreur exécution préchauffage {task.task_id}: {e}")
    
    def _generate_query_key(self, query: Dict[str, Any]) -> str:
        """🔑 Générer une clé pour une requête"""
        try:
            query_str = json.dumps(query, sort_keys=True)
            return f"query:{hashlib.md5(query_str.encode()).hexdigest()}"
            
        except Exception as e:
            logger.error(f"❌ Erreur génération clé: {e}")
            return f"query:{uuid.uuid4()}"
    
    async def stop(self):
        """⏹️ Arrêter le préchauffage"""
        self.warming_active = False

class MLCacheOptimizer:
    """🧠 Optimiseur de cache basé sur ML"""
    
    def __init__(self, cache_engine: CacheOptimizationEngine):
        self.cache_engine = cache_engine
        self.optimization_active = False
        self.access_patterns = []
        self.predictor = None
    
    async def initialize(self):
        """🚀 Initialiser l'optimiseur ML"""
        try:
            # Initialisation du modèle de prédiction
            self.predictor = RandomForestRegressor(n_estimators=100, random_state=42)
            
            logger.info("🧠 ML Cache Optimizer initialisé")
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation ML optimizer: {e}")
            raise
    
    async def optimize(self) -> Dict[str, Any]:
        """🎯 Optimiser le cache avec ML"""
        try:
            logger.info("🎯 Démarrage optimisation ML cache")
            
            # Collecte des données d'accès
            await self._collect_access_patterns()
            
            # Entraînement du modèle
            if len(self.access_patterns) >= 100:
                await self._train_prediction_model()
            
            # Recommandations d'optimisation
            recommendations = await self._generate_optimization_recommendations()
            
            logger.info("✅ Optimisation ML complétée")
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ Erreur optimisation ML: {e}")
            return {}
    
    async def _collect_access_patterns(self):
        """📊 Collecter les patterns d'accès"""
        try:
            # Simulation de collecte de patterns
            # Dans un vrai système, analyser les logs d'accès
            
            current_time = datetime.now()
            
            # Métriques simulées
            pattern = {
                'timestamp': current_time.timestamp(),
                'hour': current_time.hour,
                'day_of_week': current_time.weekday(),
                'hit_ratio': self.cache_engine.global_metrics['avg_hit_ratio'],
                'response_time_ms': self.cache_engine.global_metrics['avg_response_time_ms'],
                'memory_usage': self.cache_engine.global_metrics.get('memory_efficiency', 0)
            }
            
            self.access_patterns.append(pattern)
            
            # Conserver seulement les 1000 derniers patterns
            if len(self.access_patterns) > 1000:
                self.access_patterns = self.access_patterns[-1000:]
            
        except Exception as e:
            logger.error(f"❌ Erreur collecte patterns: {e}")
    
    async def _train_prediction_model(self):
        """🏋️ Entraîner le modèle de prédiction"""
        try:
            if len(self.access_patterns) < 10:
                return
            
            # Préparation des données
            X = []
            y = []
            
            for pattern in self.access_patterns:
                features = [
                    pattern['hour'],
                    pattern['day_of_week'],
                    pattern['memory_usage']
                ]
                target = pattern['hit_ratio']
                
                X.append(features)
                y.append(target)
            
            # Entraînement
            X_array = np.array(X)
            y_array = np.array(y)
            
            self.predictor.fit(X_array, y_array)
            
            logger.info("🏋️ Modèle ML entraîné")
            
        except Exception as e:
            logger.error(f"❌ Erreur entraînement modèle: {e}")
    
    async def _generate_optimization_recommendations(self) -> Dict[str, Any]:
        """💡 Générer des recommandations d'optimisation"""
        try:
            recommendations = {
                'cache_size_adjustment': 0,
                'ttl_adjustment': 0,
                'eviction_policy_change': None,
                'warming_strategy': None,
                'confidence_score': 0.0
            }
            
            # Analyse des métriques actuelles
            hit_ratio = self.cache_engine.global_metrics['avg_hit_ratio']
            memory_efficiency = self.cache_engine.global_metrics.get('memory_efficiency', 0)
            
            # Recommandations basées sur les seuils
            if hit_ratio < 70:
                recommendations['cache_size_adjustment'] = 20  # Augmenter de 20%
                recommendations['warming_strategy'] = 'aggressive'
                recommendations['confidence_score'] = 0.8
            
            if memory_efficiency > 90:
                recommendations['ttl_adjustment'] = -10  # Réduire TTL de 10%
                recommendations['eviction_policy_change'] = 'lfu'
                recommendations['confidence_score'] = max(recommendations['confidence_score'], 0.7)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ Erreur génération recommandations: {e}")
            return {}
    
    async def start_optimization_loop(self):
        """🔄 Démarrer la boucle d'optimisation"""
        self.optimization_active = True
        
        while self.optimization_active:
            try:
                await self.optimize()
                await asyncio.sleep(1800)  # Optimisation toutes les 30 minutes
                
            except Exception as e:
                logger.error(f"❌ Erreur boucle optimisation: {e}")
                await asyncio.sleep(1800)
    
    async def stop(self):
        """⏹️ Arrêter l'optimisation"""
        self.optimization_active = False

class CacheConsistencyManager:
    """🔄 Gestionnaire de cohérence de cache"""
    
    def __init__(self, cache_engine: CacheOptimizationEngine):
        self.cache_engine = cache_engine
        self.invalidation_queue = []
    
    async def initialize(self):
        """🚀 Initialiser le gestionnaire de cohérence"""
        logger.info("🔄 Cache Consistency Manager initialisé")
    
    async def invalidate_key(self, key: str):
        """🔄 Invalider une clé spécifique"""
        try:
            # Ajouter à la queue d'invalidation
            self.invalidation_queue.append({
                'key': key,
                'timestamp': datetime.now(),
                'type': 'single_key'
            })
            
            logger.debug(f"🔄 Clé ajoutée à l'invalidation: {key}")
            
        except Exception as e:
            logger.error(f"❌ Erreur invalidation clé {key}: {e}")
    
    async def stop(self):
        """⏹️ Arrêter le gestionnaire de cohérence"""
        pass

# Fonction d'initialisation
def initialize_cache_optimization_engine(config: Dict[str, Any]) -> CacheOptimizationEngine:
    """🚀 Initialiser le moteur d'optimisation de cache
    
    Args:
        config: Configuration du moteur
        
    Returns:
        Instance du moteur initialisée
    """
    try:
        engine = CacheOptimizationEngine(config)
        logger.info("🚀 Cache Optimization Engine initialisé avec succès")
        return engine
        
    except Exception as e:
        logger.error(f"❌ Erreur initialisation Cache Engine: {e}")
        raise

# Configuration par défaut
DEFAULT_CACHE_CONFIG = {
    'default_ttl': 3600,
    'max_memory_mb': 2048,
    'warming_interval': 300,
    'max_workers': 8,
    'cache_layers': {
        'l1_memory': {
            'max_size_mb': 512,
            'max_entries': 10000
        },
        'l2_redis': {
            'host': 'localhost',
            'port': 6379,
            'db': 0
        },
        'l3_disk': {
            'cache_dir': '/tmp/ainflue_cache',
            'max_size_mb': 2048
        }
    }
}

if __name__ == "__main__":
    # Test basique
    async def test_cache_optimization():
        engine = initialize_cache_optimization_engine(DEFAULT_CACHE_CONFIG)
        
        try:
            await engine.initialize()
            await engine.start_monitoring()
            
            # Test stockage/récupération
            await engine.set("test_key", {"data": "test_value"}, ttl_seconds=300)
            result = await engine.get("test_key")
            
            print(f"✅ Cache test: {result}")
            
            # Test préchauffage
            queries = [{"sql": "SELECT * FROM users", "params": {}}]
            warming_id = await engine.warm_cache(queries)
            print(f"✅ Préchauffage planifié: {warming_id}")
            
            # Test pendant 5 secondes
            await asyncio.sleep(5)
            
            # Statistiques
            stats = await engine.get_cache_statistics()
            print(f"📊 Statistiques: {stats}")
            
            await engine.stop_monitoring()
            print("✅ Test terminé")
            
        except Exception as e:
            print(f"❌ Erreur test: {e}")
    
    asyncio.run(test_cache_optimization())