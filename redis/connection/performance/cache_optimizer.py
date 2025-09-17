#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 Redis Cache Optimizer - Enterprise Performance Module
========================================================

**Rôles Experts:**
- **Performance Engineer**: Advanced caching strategies optimization
- **Backend Senior**: Cache architecture and algorithms
- **DBA**: Database caching optimization
- **DevOps**: Cache monitoring and performance tuning

Optimiseur cache Redis pour stratégies de cache avancées avec
gestion intelligente et optimisation automatique.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import time
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class CacheStrategy(Enum):
    """Stratégies de cache"""
    LRU = "lru"                 # Least Recently Used
    LFU = "lfu"                 # Least Frequently Used
    FIFO = "fifo"               # First In First Out
    ADAPTIVE = "adaptive"        # Adaptatif intelligent
    WRITE_THROUGH = "write_through"
    WRITE_BACK = "write_back"

class CacheTier(Enum):
    """Niveaux performance cache"""
    OPTIMAL = "optimal"         # > 95% hit ratio
    GOOD = "good"              # 85-95% hit ratio
    ACCEPTABLE = "acceptable"   # 70-85% hit ratio
    POOR = "poor"              # 50-70% hit ratio
    CRITICAL = "critical"       # < 50% hit ratio

@dataclass
class CacheMetrics:
    """Métriques cache"""
    hit_ratio: float = 0.0
    miss_ratio: float = 0.0
    total_requests: int = 0
    cache_size_mb: float = 0.0
    eviction_count: int = 0
    current_tier: CacheTier = CacheTier.GOOD
    average_access_time_ms: float = 0.0
    hit_history: deque = field(default_factory=lambda: deque(maxlen=1000))

@dataclass
class CacheConfig:
    """Configuration optimisation cache"""
    max_memory_mb: int = 1024
    strategy: CacheStrategy = CacheStrategy.ADAPTIVE
    default_ttl: int = 3600
    enable_compression: bool = True
    prefetch_enabled: bool = True
    monitoring_interval: float = 5.0

class CacheOptimizer:
    """Optimiseur cache Redis enterprise"""
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self.metrics = CacheMetrics()
        self.is_running = False
        self._cache_data = {}
        self._access_patterns = defaultdict(list)
        self._monitoring_task = None
        
    async def start(self):
        """Démarrage optimiseur cache"""
        if self.is_running:
            return
            
        logger.info("🚀 Démarrage optimiseur cache Redis")
        self.is_running = True
        
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("✅ Optimiseur cache démarré")
    
    async def stop(self):
        """Arrêt optimiseur cache"""
        if not self.is_running:
            return
            
        logger.info("🛑 Arrêt optimiseur cache")
        self.is_running = False
        
        if self._monitoring_task:
            self._monitoring_task.cancel()
        
        logger.info("✅ Optimiseur cache arrêté")
    
    async def get(self, key: str) -> Optional[Any]:
        """Récupération cache optimisée"""
        start_time = time.perf_counter()
        
        if key in self._cache_data:
            # Cache hit
            data = self._cache_data[key]
            access_time = (time.perf_counter() - start_time) * 1000
            await self._record_hit(key, access_time)
            return data['value']
        else:
            # Cache miss
            access_time = (time.perf_counter() - start_time) * 1000
            await self._record_miss(key, access_time)
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Stockage cache optimisé"""
        try:
            ttl = ttl or self.config.default_ttl
            
            self._cache_data[key] = {
                'value': value,
                'created_at': time.time(),
                'ttl': ttl,
                'access_count': 0,
                'last_access': time.time()
            }
            
            await self._optimize_cache_size()
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur stockage cache: {e}")
            return False
    
    async def _record_hit(self, key: str, access_time_ms: float):
        """Enregistrement cache hit"""
        self.metrics.total_requests += 1
        
        # Mise à jour statistiques accès
        if key in self._cache_data:
            self._cache_data[key]['access_count'] += 1
            self._cache_data[key]['last_access'] = time.time()
        
        # Mise à jour métriques
        await self._update_metrics(True, access_time_ms)
    
    async def _record_miss(self, key: str, access_time_ms: float):
        """Enregistrement cache miss"""
        self.metrics.total_requests += 1
        
        # Enregistrement pattern d'accès
        self._access_patterns[key].append(time.time())
        
        # Mise à jour métriques
        await self._update_metrics(False, access_time_ms)
    
    async def _update_metrics(self, is_hit: bool, access_time_ms: float):
        """Mise à jour métriques"""
        self.metrics.hit_history.append(1 if is_hit else 0)
        
        # Calcul ratio hit/miss
        if len(self.metrics.hit_history) > 0:
            hits = sum(self.metrics.hit_history)
            total = len(self.metrics.hit_history)
            self.metrics.hit_ratio = hits / total
            self.metrics.miss_ratio = 1 - self.metrics.hit_ratio
        
        # Mise à jour temps d'accès moyen
        self.metrics.average_access_time_ms = (
            self.metrics.average_access_time_ms * 0.9 + access_time_ms * 0.1
        )
        
        # Mise à jour tier
        await self._update_cache_tier()
    
    async def _update_cache_tier(self):
        """Mise à jour tier cache"""
        hit_ratio = self.metrics.hit_ratio
        
        if hit_ratio >= 0.95:
            self.metrics.current_tier = CacheTier.OPTIMAL
        elif hit_ratio >= 0.85:
            self.metrics.current_tier = CacheTier.GOOD
        elif hit_ratio >= 0.70:
            self.metrics.current_tier = CacheTier.ACCEPTABLE
        elif hit_ratio >= 0.50:
            self.metrics.current_tier = CacheTier.POOR
        else:
            self.metrics.current_tier = CacheTier.CRITICAL
    
    async def _optimize_cache_size(self):
        """Optimisation taille cache"""
        # Simulation calcul taille
        estimated_size_mb = len(self._cache_data) * 0.001  # Estimation simplifiée
        self.metrics.cache_size_mb = estimated_size_mb
        
        if estimated_size_mb > self.config.max_memory_mb:
            await self._evict_entries()
    
    async def _evict_entries(self):
        """Éviction entrées cache"""
        target_size = self.config.max_memory_mb * 0.8  # 80% de la limite
        current_size = self.metrics.cache_size_mb
        
        if current_size <= target_size:
            return
        
        # Sélection entrées à évincer selon stratégie
        entries_to_evict = []
        
        if self.config.strategy == CacheStrategy.LRU:
            # Tri par dernière utilisation
            sorted_entries = sorted(
                self._cache_data.items(),
                key=lambda x: x[1]['last_access']
            )
        elif self.config.strategy == CacheStrategy.LFU:
            # Tri par fréquence d'utilisation
            sorted_entries = sorted(
                self._cache_data.items(),
                key=lambda x: x[1]['access_count']
            )
        else:  # ADAPTIVE
            # Combinaison intelligent
            current_time = time.time()
            sorted_entries = sorted(
                self._cache_data.items(),
                key=lambda x: (
                    (current_time - x[1]['last_access']) / max(1, x[1]['access_count'])
                ),
                reverse=True
            )
        
        # Éviction jusqu'à atteindre la taille cible
        evicted_count = 0
        for key, _ in sorted_entries:
            if self.metrics.cache_size_mb <= target_size:
                break
            
            del self._cache_data[key]
            evicted_count += 1
            self.metrics.cache_size_mb *= 0.999  # Réduction estimée
        
        self.metrics.eviction_count += evicted_count
        
        if evicted_count > 0:
            logger.info(f"🗑️ {evicted_count} entrées cache évincées")
    
    async def _monitoring_loop(self):
        """Boucle monitoring cache"""
        while self.is_running:
            try:
                await self._collect_cache_metrics()
                await asyncio.sleep(self.config.monitoring_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Erreur monitoring cache: {e}")
                await asyncio.sleep(1.0)
    
    async def _collect_cache_metrics(self):
        """Collection métriques cache"""
        # Nettoyage TTL expirés
        await self._cleanup_expired_entries()
        
        # Log métriques
        logger.info(
            f"📊 Cache: {self.metrics.hit_ratio:.2%} hit ratio, "
            f"{self.metrics.cache_size_mb:.1f}MB, "
            f"tier: {self.metrics.current_tier.value}"
        )
    
    async def _cleanup_expired_entries(self):
        """Nettoyage entrées expirées"""
        current_time = time.time()
        expired_keys = []
        
        for key, data in self._cache_data.items():
            if current_time - data['created_at'] > data['ttl']:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self._cache_data[key]
        
        if expired_keys:
            logger.debug(f"🧹 {len(expired_keys)} entrées expirées nettoyées")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Récupération métriques cache"""
        return {
            'hit_ratio': self.metrics.hit_ratio,
            'miss_ratio': self.metrics.miss_ratio,
            'total_requests': self.metrics.total_requests,
            'cache_size_mb': self.metrics.cache_size_mb,
            'eviction_count': self.metrics.eviction_count,
            'current_tier': self.metrics.current_tier.value,
            'average_access_time_ms': self.metrics.average_access_time_ms,
            'entry_count': len(self._cache_data),
            'max_memory_mb': self.config.max_memory_mb,
            'strategy': self.config.strategy.value
        }

# Factory function
async def create_cache_optimizer(
    max_memory_mb: int = 1024,
    strategy: CacheStrategy = CacheStrategy.ADAPTIVE
) -> CacheOptimizer:
    """Création optimiseur cache configuré"""
    config = CacheConfig(
        max_memory_mb=max_memory_mb,
        strategy=strategy
    )
    
    optimizer = CacheOptimizer(config)
    await optimizer.start()
    return optimizer

# Export public API
__all__ = [
    'CacheOptimizer',
    'CacheStrategy',
    'CacheTier',
    'CacheMetrics',
    'CacheConfig',
    'create_cache_optimizer'
]