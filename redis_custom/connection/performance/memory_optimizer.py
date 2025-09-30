#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠 Redis Memory Optimizer - Enterprise Performance Module
=========================================================

**Rôles Experts:**
- **Performance Engineer**: Intelligent memory management optimization
- **Backend Senior**: Memory usage patterns and optimization
- **DBA**: Database memory optimization strategies
- **DevOps**: Memory monitoring and alerting

Optimiseur mémoire Redis pour gestion intelligente avec
optimisation automatique et monitoring temps-réel.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ AVERTISSEMENT LÉGAL:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

🏢 USAGE ENTREPRISE:
- Licence entreprise disponible sur demande
- Support technique inclus avec licence
- Maintenance et mises à jour assurées
- Formation équipe technique fournie
"""

import asyncio
import time
import logging
import statistics
import gc
import psutil
from typing import Dict, List, Optional, Any, Tuple, Union, Set
from dataclasses import dataclass, field
from enum import Enum
from collections import deque, defaultdict
import weakref
import threading

# Import Redis with fallback
try:
    import sys
    import importlib
    # Temporarily remove the local redis module from the path
    original_path = sys.path[:]
    local_redis_path = [p for p in sys.path if 'IA Chérie' in p and 'redis' not in p]
    sys.path = [p for p in sys.path if 'IA Chérie' not in p] + local_redis_path
    
    redis_module = importlib.import_module('redis')
    if hasattr(redis_module, 'asyncio'):
        redis = redis_module.asyncio
    else:
        redis = redis_module
    
    # Restore original path
    sys.path = original_path
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

logger = logging.getLogger(__name__)

class MemoryTier(Enum):
    """Niveaux d'utilisation mémoire"""
    OPTIMAL = "optimal"          # < 70% utilisation
    GOOD = "good"                # 70-80% utilisation
    WARNING = "warning"          # 80-90% utilisation
    CRITICAL = "critical"        # 90-95% utilisation
    EMERGENCY = "emergency"      # > 95% utilisation

class OptimizationStrategy(Enum):
    """Stratégies d'optimisation mémoire"""
    AGGRESSIVE = "aggressive"    # Optimisation agressive
    BALANCED = "balanced"        # Équilibre performance/mémoire
    CONSERVATIVE = "conservative" # Conservation mémoire prioritaire
    ADAPTIVE = "adaptive"        # Adaptation automatique

class EvictionPolicy(Enum):
    """Politiques d'éviction"""
    LRU = "lru"                  # Least Recently Used
    LFU = "lfu"                  # Least Frequently Used
    TTL = "ttl"                  # Time To Live
    SIZE_BASED = "size_based"    # Basé sur la taille
    INTELLIGENT = "intelligent"   # IA-powered

@dataclass
class MemoryMetrics:
    """Métriques mémoire"""
    total_memory_mb: float = 0.0
    used_memory_mb: float = 0.0
    available_memory_mb: float = 0.0
    memory_usage_percent: float = 0.0
    peak_memory_mb: float = 0.0
    redis_memory_mb: float = 0.0
    connection_memory_mb: float = 0.0
    cache_memory_mb: float = 0.0
    current_tier: MemoryTier = MemoryTier.GOOD
    fragmentation_ratio: float = 1.0
    memory_efficiency: float = 100.0
    gc_collections: int = 0
    last_gc_time: float = 0.0
    memory_history: deque = field(default_factory=lambda: deque(maxlen=1000))

@dataclass
class OptimizationConfig:
    """Configuration optimisation mémoire"""
    max_memory_mb: Optional[int] = None  # Auto-detect si None
    target_memory_usage: float = 0.8    # 80% max
    warning_threshold: float = 0.85     # 85% warning
    critical_threshold: float = 0.95    # 95% critical
    optimization_strategy: OptimizationStrategy = OptimizationStrategy.BALANCED
    eviction_policy: EvictionPolicy = EvictionPolicy.INTELLIGENT
    enable_auto_gc: bool = True
    gc_threshold: float = 0.9           # Déclenchement GC à 90%
    enable_memory_compression: bool = True
    enable_connection_pooling: bool = True
    max_connection_memory_mb: int = 100
    monitoring_interval: float = 5.0
    optimization_interval: float = 60.0
    enable_memory_alerts: bool = True

class MemoryPool:
    """Pool mémoire optimisé"""
    
    def __init__(self, max_size_mb: int):
        self.max_size_mb = max_size_mb
        self.allocated_objects = weakref.WeakSet()
        self.size_tracker = defaultdict(int)
        self.lock = threading.Lock()
    
    def allocate(self, obj: Any, size_hint: int = 0) -> bool:
        """Allocation objet avec suivi"""
        with self.lock:
            estimated_size = size_hint or self._estimate_size(obj)
            
            if self._get_current_size() + estimated_size > self.max_size_mb * 1024 * 1024:
                return False  # Allocation refusée
            
            self.allocated_objects.add(obj)
            self.size_tracker[id(obj)] = estimated_size
            return True
    
    def deallocate(self, obj: Any):
        """Libération objet"""
        with self.lock:
            obj_id = id(obj)
            if obj_id in self.size_tracker:
                del self.size_tracker[obj_id]
            
            if obj in self.allocated_objects:
                self.allocated_objects.discard(obj)
    
    def _estimate_size(self, obj: Any) -> int:
        """Estimation taille objet"""
        try:
            return sys.getsizeof(obj)
        except:
            return 1024  # Estimation par défaut
    
    def _get_current_size(self) -> int:
        """Taille actuelle du pool"""
        return sum(self.size_tracker.values())
    
    def get_stats(self) -> Dict[str, Any]:
        """Statistiques pool"""
        with self.lock:
            return {
                'max_size_mb': self.max_size_mb,
                'current_size_mb': self._get_current_size() / (1024 * 1024),
                'object_count': len(self.allocated_objects),
                'utilization_percent': (self._get_current_size() / (self.max_size_mb * 1024 * 1024)) * 100
            }

class ConnectionMemoryManager:
    """Gestionnaire mémoire connexions"""
    
    def __init__(self, max_memory_mb: int):
        self.max_memory_mb = max_memory_mb
        self.connection_registry = {}
        self.memory_usage = defaultdict(int)
        self.lock = asyncio.Lock()
    
    async def register_connection(self, connection_id: str, estimated_memory: int = 1024):
        """Enregistrement connexion"""
        async with self.lock:
            if self._get_total_memory() + estimated_memory > self.max_memory_mb * 1024 * 1024:
                raise MemoryError("Limite mémoire connexions atteinte")
            
            self.connection_registry[connection_id] = {
                'created_at': time.time(),
                'memory_usage': estimated_memory,
                'last_activity': time.time()
            }
            self.memory_usage[connection_id] = estimated_memory
    
    async def unregister_connection(self, connection_id: str):
        """Désenregistrement connexion"""
        async with self.lock:
            if connection_id in self.connection_registry:
                del self.connection_registry[connection_id]
                del self.memory_usage[connection_id]
    
    async def update_activity(self, connection_id: str):
        """Mise à jour activité connexion"""
        async with self.lock:
            if connection_id in self.connection_registry:
                self.connection_registry[connection_id]['last_activity'] = time.time()
    
    async def cleanup_idle_connections(self, max_idle_seconds: int = 300):
        """Nettoyage connexions inactives"""
        current_time = time.time()
        idle_connections = []
        
        async with self.lock:
            for conn_id, info in self.connection_registry.items():
                if current_time - info['last_activity'] > max_idle_seconds:
                    idle_connections.append(conn_id)
        
        for conn_id in idle_connections:
            await self.unregister_connection(conn_id)
            logger.info(f"🧹 Connexion inactive nettoyée: {conn_id}")
        
        return len(idle_connections)
    
    def _get_total_memory(self) -> int:
        """Mémoire totale utilisée"""
        return sum(self.memory_usage.values())
    
    def get_stats(self) -> Dict[str, Any]:
        """Statistiques mémoire connexions"""
        return {
            'max_memory_mb': self.max_memory_mb,
            'current_memory_mb': self._get_total_memory() / (1024 * 1024),
            'connection_count': len(self.connection_registry),
            'utilization_percent': (self._get_total_memory() / (self.max_memory_mb * 1024 * 1024)) * 100
        }

class MemoryOptimizer:
    """Optimiseur mémoire Redis enterprise"""
    
    def __init__(self, config: OptimizationConfig):
        self.config = config
        self.metrics = MemoryMetrics()
        self.memory_pool = MemoryPool(config.max_connection_memory_mb)
        self.connection_manager = ConnectionMemoryManager(config.max_connection_memory_mb)
        self.is_running = False
        self._monitoring_task = None
        self._optimization_task = None
        self._cached_data = weakref.WeakValueDictionary()
        self._compression_enabled = config.enable_memory_compression
        
        # Auto-detection mémoire système
        if config.max_memory_mb is None:
            system_memory = psutil.virtual_memory()
            self.config.max_memory_mb = int(system_memory.total / (1024 * 1024) * 0.8)  # 80% de la RAM
    
    async def start(self):
        """Démarrage optimiseur mémoire"""
        if self.is_running:
            return
            
        logger.info("🧠 Démarrage optimiseur mémoire Redis")
        self.is_running = True
        
        # Initialisation
        await self._initialize_memory_tracking()
        
        # Démarrage monitoring
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        
        # Démarrage optimisation
        self._optimization_task = asyncio.create_task(self._optimization_loop())
        
        logger.info("✅ Optimiseur mémoire démarré")
    
    async def stop(self):
        """Arrêt optimiseur mémoire"""
        if not self.is_running:
            return
            
        logger.info("🛑 Arrêt optimiseur mémoire")
        self.is_running = False
        
        if self._monitoring_task:
            self._monitoring_task.cancel()
        if self._optimization_task:
            self._optimization_task.cancel()
        
        await self._cleanup_memory()
        logger.info("✅ Optimiseur mémoire arrêté")
    
    async def _initialize_memory_tracking(self):
        """Initialisation suivi mémoire"""
        # Collection initiale métriques
        await self._collect_memory_metrics()
        logger.info(f"📊 Mémoire système: {self.metrics.total_memory_mb:.0f} MB")
        logger.info(f"🎯 Limite configurée: {self.config.max_memory_mb} MB")
    
    async def allocate_memory(self, obj: Any, size_hint: int = 0) -> bool:
        """Allocation mémoire contrôlée"""
        # Vérification limites
        if not await self._check_memory_limits():
            await self._trigger_emergency_cleanup()
            return False
        
        # Allocation via pool
        success = self.memory_pool.allocate(obj, size_hint)
        if not success:
            await self._optimize_memory_usage()
            success = self.memory_pool.allocate(obj, size_hint)
        
        return success
    
    async def deallocate_memory(self, obj: Any):
        """Libération mémoire"""
        self.memory_pool.deallocate(obj)
    
    async def register_connection(self, connection_id: str, estimated_memory: int = 1024):
        """Enregistrement connexion avec suivi mémoire"""
        try:
            await self.connection_manager.register_connection(connection_id, estimated_memory)
            return True
        except MemoryError:
            await self._optimize_connection_memory()
            try:
                await self.connection_manager.register_connection(connection_id, estimated_memory)
                return True
            except MemoryError:
                logger.error(f"❌ Impossible d'allouer mémoire pour connexion {connection_id}")
                return False
    
    async def unregister_connection(self, connection_id: str):
        """Désenregistrement connexion"""
        await self.connection_manager.unregister_connection(connection_id)
    
    async def cache_data(self, key: str, data: Any, ttl: int = 3600) -> bool:
        """Cache données avec gestion mémoire"""
        # Vérification taille
        estimated_size = sys.getsizeof(data)
        
        if not await self._check_cache_memory_available(estimated_size):
            await self._evict_cache_data()
            
            if not await self._check_cache_memory_available(estimated_size):
                return False
        
        # Compression si activée
        if self._compression_enabled and estimated_size > 1024:
            data = await self._compress_data(data)
        
        self._cached_data[key] = {
            'data': data,
            'created_at': time.time(),
            'ttl': ttl,
            'size': estimated_size,
            'access_count': 0,
            'last_access': time.time()
        }
        
        return True
    
    async def get_cached_data(self, key: str) -> Optional[Any]:
        """Récupération données en cache"""
        if key not in self._cached_data:
            return None
        
        cache_entry = self._cached_data[key]
        current_time = time.time()
        
        # Vérification TTL
        if current_time - cache_entry['created_at'] > cache_entry['ttl']:
            del self._cached_data[key]
            return None
        
        # Mise à jour statistiques accès
        cache_entry['access_count'] += 1
        cache_entry['last_access'] = current_time
        
        data = cache_entry['data']
        
        # Décompression si nécessaire
        if self._compression_enabled:
            data = await self._decompress_data(data)
        
        return data
    
    async def _collect_memory_metrics(self):
        """Collection métriques mémoire"""
        # Mémoire système
        system_memory = psutil.virtual_memory()
        self.metrics.total_memory_mb = system_memory.total / (1024 * 1024)
        self.metrics.used_memory_mb = system_memory.used / (1024 * 1024)
        self.metrics.available_memory_mb = system_memory.available / (1024 * 1024)
        self.metrics.memory_usage_percent = system_memory.percent
        
        # Mémoire pic
        self.metrics.peak_memory_mb = max(
            self.metrics.peak_memory_mb,
            self.metrics.used_memory_mb
        )
        
        # Mémoire spécifique Redis
        await self._collect_redis_memory_info()
        
        # Mémoire connexions
        conn_stats = self.connection_manager.get_stats()
        self.metrics.connection_memory_mb = conn_stats['current_memory_mb']
        
        # Mémoire cache
        self.metrics.cache_memory_mb = self._calculate_cache_memory()
        
        # Fragmentation
        self.metrics.fragmentation_ratio = self._calculate_fragmentation_ratio()
        
        # Efficacité mémoire
        self.metrics.memory_efficiency = self._calculate_memory_efficiency()
        
        # Historique
        self.metrics.memory_history.append(self.metrics.memory_usage_percent)
        
        # Mise à jour tier
        await self._update_memory_tier()
    
    async def _collect_redis_memory_info(self):
        """Collection info mémoire Redis"""
        if not REDIS_AVAILABLE:
            self.metrics.redis_memory_mb = 0
            return
        
        try:
            # Simulation info mémoire Redis
            self.metrics.redis_memory_mb = self.metrics.used_memory_mb * 0.1  # 10% estimé
        except Exception as e:
            logger.error(f"❌ Erreur collection mémoire Redis: {e}")
            self.metrics.redis_memory_mb = 0
    
    def _calculate_cache_memory(self) -> float:
        """Calcul mémoire cache"""
        total_size = 0
        for cache_entry in self._cached_data.values():
            total_size += cache_entry['size']
        return total_size / (1024 * 1024)
    
    def _calculate_fragmentation_ratio(self) -> float:
        """Calcul ratio fragmentation"""
        # Simulation ratio fragmentation
        if self.metrics.memory_usage_percent > 90:
            return 1.5  # Fragmentation élevée
        elif self.metrics.memory_usage_percent > 70:
            return 1.2  # Fragmentation modérée
        else:
            return 1.0  # Fragmentation normale
    
    def _calculate_memory_efficiency(self) -> float:
        """Calcul efficacité mémoire"""
        # Efficacité basée sur fragmentation et utilisation
        base_efficiency = 100.0
        
        if self.metrics.fragmentation_ratio > 1.3:
            base_efficiency -= 20
        elif self.metrics.fragmentation_ratio > 1.1:
            base_efficiency -= 10
        
        if self.metrics.memory_usage_percent > 90:
            base_efficiency -= 15
        elif self.metrics.memory_usage_percent > 80:
            base_efficiency -= 5
        
        return max(0, base_efficiency)
    
    async def _update_memory_tier(self):
        """Mise à jour tier mémoire"""
        usage_percent = self.metrics.memory_usage_percent
        
        if usage_percent >= 95:
            self.metrics.current_tier = MemoryTier.EMERGENCY
        elif usage_percent >= 90:
            self.metrics.current_tier = MemoryTier.CRITICAL
        elif usage_percent >= 80:
            self.metrics.current_tier = MemoryTier.WARNING
        elif usage_percent >= 70:
            self.metrics.current_tier = MemoryTier.GOOD
        else:
            self.metrics.current_tier = MemoryTier.OPTIMAL
    
    async def _check_memory_limits(self) -> bool:
        """Vérification limites mémoire"""
        return self.metrics.memory_usage_percent < self.config.critical_threshold * 100
    
    async def _check_cache_memory_available(self, required_size: int) -> bool:
        """Vérification mémoire cache disponible"""
        current_cache_mb = self._calculate_cache_memory()
        required_mb = required_size / (1024 * 1024)
        
        return current_cache_mb + required_mb < self.config.max_connection_memory_mb * 0.5
    
    async def _monitoring_loop(self):
        """Boucle monitoring mémoire"""
        while self.is_running:
            try:
                await self._collect_memory_metrics()
                await self._check_memory_alerts()
                await asyncio.sleep(self.config.monitoring_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Erreur monitoring mémoire: {e}")
                await asyncio.sleep(1.0)
    
    async def _optimization_loop(self):
        """Boucle optimisation mémoire"""
        while self.is_running:
            try:
                await self._optimize_memory_usage()
                await asyncio.sleep(self.config.optimization_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Erreur optimisation mémoire: {e}")
                await asyncio.sleep(5.0)
    
    async def _check_memory_alerts(self):
        """Vérification alertes mémoire"""
        if not self.config.enable_memory_alerts:
            return
        
        usage_percent = self.metrics.memory_usage_percent
        
        if usage_percent >= self.config.critical_threshold * 100:
            logger.critical(
                f"🚨 MÉMOIRE CRITIQUE: {usage_percent:.1f}% "
                f"(seuil: {self.config.critical_threshold * 100:.1f}%)"
            )
        elif usage_percent >= self.config.warning_threshold * 100:
            logger.warning(
                f"⚠️ MÉMOIRE ÉLEVÉE: {usage_percent:.1f}% "
                f"(seuil: {self.config.warning_threshold * 100:.1f}%)"
            )
    
    async def _optimize_memory_usage(self):
        """Optimisation utilisation mémoire"""
        current_tier = self.metrics.current_tier
        
        if current_tier in [MemoryTier.EMERGENCY, MemoryTier.CRITICAL]:
            await self._trigger_emergency_cleanup()
        elif current_tier == MemoryTier.WARNING:
            await self._trigger_aggressive_cleanup()
        elif current_tier == MemoryTier.GOOD:
            await self._trigger_maintenance_cleanup()
    
    async def _trigger_emergency_cleanup(self):
        """Nettoyage d'urgence mémoire"""
        logger.warning("🚨 Déclenchement nettoyage d'urgence mémoire")
        
        # Éviction cache agressive
        await self._evict_cache_data(eviction_ratio=0.5)
        
        # Nettoyage connexions inactives
        await self.connection_manager.cleanup_idle_connections(max_idle_seconds=60)
        
        # Garbage collection forcé
        if self.config.enable_auto_gc:
            await self._trigger_garbage_collection()
    
    async def _trigger_aggressive_cleanup(self):
        """Nettoyage agressif"""
        logger.info("⚡ Déclenchement nettoyage agressif mémoire")
        
        # Éviction cache modérée
        await self._evict_cache_data(eviction_ratio=0.3)
        
        # Nettoyage connexions inactives
        await self.connection_manager.cleanup_idle_connections(max_idle_seconds=120)
    
    async def _trigger_maintenance_cleanup(self):
        """Nettoyage maintenance"""
        logger.debug("🧹 Nettoyage maintenance mémoire")
        
        # Éviction cache légère
        await self._evict_cache_data(eviction_ratio=0.1)
        
        # Nettoyage connexions inactives
        await self.connection_manager.cleanup_idle_connections(max_idle_seconds=300)
    
    async def _optimize_connection_memory(self):
        """Optimisation mémoire connexions"""
        logger.info("🔗 Optimisation mémoire connexions")
        
        # Nettoyage connexions inactives agressif
        cleaned = await self.connection_manager.cleanup_idle_connections(max_idle_seconds=30)
        
        if cleaned > 0:
            logger.info(f"✅ {cleaned} connexions nettoyées")
    
    async def _evict_cache_data(self, eviction_ratio: float = 0.2):
        """Éviction données cache"""
        if not self._cached_data:
            return
        
        cache_items = list(self._cached_data.items())
        evict_count = int(len(cache_items) * eviction_ratio)
        
        if evict_count == 0:
            return
        
        # Tri selon politique éviction
        if self.config.eviction_policy == EvictionPolicy.LRU:
            cache_items.sort(key=lambda x: x[1]['last_access'])
        elif self.config.eviction_policy == EvictionPolicy.LFU:
            cache_items.sort(key=lambda x: x[1]['access_count'])
        elif self.config.eviction_policy == EvictionPolicy.TTL:
            cache_items.sort(key=lambda x: x[1]['created_at'])
        elif self.config.eviction_policy == EvictionPolicy.SIZE_BASED:
            cache_items.sort(key=lambda x: x[1]['size'], reverse=True)
        else:  # INTELLIGENT
            # Combinaison score intelligent
            current_time = time.time()
            cache_items.sort(key=lambda x: (
                (current_time - x[1]['last_access']) / x[1]['access_count']
                if x[1]['access_count'] > 0 else float('inf')
            ), reverse=True)
        
        # Éviction
        evicted_keys = []
        for i in range(evict_count):
            if i < len(cache_items):
                key = cache_items[i][0]
                if key in self._cached_data:
                    del self._cached_data[key]
                    evicted_keys.append(key)
        
        if evicted_keys:
            logger.info(f"🗑️ {len(evicted_keys)} entrées cache évincées")
    
    async def _trigger_garbage_collection(self):
        """Déclenchement garbage collection"""
        start_time = time.time()
        
        # Garbage collection
        collected = gc.collect()
        
        gc_time = time.time() - start_time
        self.metrics.gc_collections += 1
        self.metrics.last_gc_time = gc_time
        
        logger.info(f"🗑️ GC: {collected} objets collectés en {gc_time:.3f}s")
    
    async def _compress_data(self, data: Any) -> Any:
        """Compression données"""
        # Simulation compression (implementation réelle utiliserait zlib/gzip)
        return data
    
    async def _decompress_data(self, data: Any) -> Any:
        """Décompression données"""
        # Simulation décompression
        return data
    
    async def _cleanup_memory(self):
        """Nettoyage final mémoire"""
        # Vidage cache
        self._cached_data.clear()
        
        # Garbage collection final
        if self.config.enable_auto_gc:
            await self._trigger_garbage_collection()
    
    def get_metrics(self) -> Dict[str, Any]:
        """Récupération métriques mémoire"""
        pool_stats = self.memory_pool.get_stats()
        conn_stats = self.connection_manager.get_stats()
        
        return {
            'total_memory_mb': self.metrics.total_memory_mb,
            'used_memory_mb': self.metrics.used_memory_mb,
            'available_memory_mb': self.metrics.available_memory_mb,
            'memory_usage_percent': self.metrics.memory_usage_percent,
            'peak_memory_mb': self.metrics.peak_memory_mb,
            'redis_memory_mb': self.metrics.redis_memory_mb,
            'connection_memory_mb': self.metrics.connection_memory_mb,
            'cache_memory_mb': self.metrics.cache_memory_mb,
            'current_tier': self.metrics.current_tier.value,
            'fragmentation_ratio': self.metrics.fragmentation_ratio,
            'memory_efficiency': self.metrics.memory_efficiency,
            'gc_collections': self.metrics.gc_collections,
            'last_gc_time': self.metrics.last_gc_time,
            'pool_stats': pool_stats,
            'connection_stats': conn_stats,
            'cache_entries': len(self._cached_data),
            'target_memory_usage': self.config.target_memory_usage,
            'max_memory_mb': self.config.max_memory_mb
        }

# Factory function pour création optimiseur
async def create_memory_optimizer(
    max_memory_mb: Optional[int] = None,
    target_usage: float = 0.8,
    strategy: OptimizationStrategy = OptimizationStrategy.BALANCED
) -> MemoryOptimizer:
    """Création optimiseur mémoire configuré"""
    config = OptimizationConfig(
        max_memory_mb=max_memory_mb,
        target_memory_usage=target_usage,
        optimization_strategy=strategy
    )
    
    optimizer = MemoryOptimizer(config)
    await optimizer.start()
    return optimizer

# Export public API
__all__ = [
    'MemoryOptimizer',
    'MemoryTier',
    'OptimizationStrategy',
    'EvictionPolicy',
    'MemoryMetrics',
    'OptimizationConfig',
    'MemoryPool',
    'ConnectionMemoryManager',
    'create_memory_optimizer'
]