"""⚡ Feature Cache Optimizer - High-Performance Feature Caching
=====================================================================
Module: ml/feature_stores/feature_cache_optimizer.py
Author: Fahed Mlaiel (mlaiel@live.de)
=====================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 HIGH-PERFORMANCE FEATURE CACHING
Intelligent feature caching with optimized eviction policies
- Multi-tier caching strategy (memory, SSD, network)
- Predictive preloading basé sur creator patterns
- Intelligent eviction avec usage analytics
- Creator-specific cache optimization
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
import hashlib
import pickle
import threading
from pathlib import Path
from collections import defaultdict, OrderedDict
import numpy as np
import pandas as pd

# Configuration
logger = logging.getLogger(__name__)

class CacheTier(Enum):
    """Niveaux de cache"""
    
    L1_MEMORY = "l1_memory"        # RAM ultra-rapide
    L2_SSD = "l2_ssd"             # SSD local
    L3_NETWORK = "l3_network"      # Redis/Memcached
    L4_STORAGE = "l4_storage"      # Stockage persistant

class EvictionPolicy(Enum):
    """Politiques d'éviction"""
    
    LRU = "lru"                   # Least Recently Used
    LFU = "lfu"                   # Least Frequently Used
    TTL = "ttl"                   # Time To Live
    CREATOR_AWARE = "creator_aware"  # Creator-specific prioritization
    PREDICTIVE = "predictive"      # ML-powered prediction

class CacheHitType(Enum):
    """Types de cache hits"""
    
    HIT = "hit"
    MISS = "miss"
    PARTIAL_HIT = "partial_hit"
    PREFETCH_HIT = "prefetch_hit"

@dataclass
class CacheEntry:
    """Entrée de cache"""
    
    key: str
    value: Any
    tier: CacheTier
    created_at: datetime
    last_accessed: datetime
    access_count: int = 0
    creator_types: List[str] = field(default_factory=list)
    size_bytes: int = 0
    ttl_seconds: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_expired(self) -> bool:
        """Vérifier si l'entrée a expiré"""
        if self.ttl_seconds is None:
            return False
        return time.time() - self.created_at.timestamp() > self.ttl_seconds
    
    @property
    def age_seconds(self) -> float:
        """Âge de l'entrée en secondes"""
        return time.time() - self.created_at.timestamp()

@dataclass
class CacheStats:
    """Statistiques de cache"""
    
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    memory_usage_bytes: int = 0
    storage_usage_bytes: int = 0
    avg_access_time_ms: float = 0.0
    hit_rate: float = 0.0
    creator_stats: Dict[str, Dict[str, int]] = field(default_factory=dict)

@dataclass
class PrefetchPrediction:
    """Prédiction de prefetch"""
    
    key: str
    confidence: float
    predicted_access_time: datetime
    creator_type: str
    reasons: List[str] = field(default_factory=list)

class FeatureCacheOptimizer:
    """
    ⚡ Feature Cache Optimizer
    
    Cache multi-niveaux intelligent avec:
    - Optimisation automatique des performances
    - Prédiction ML des accès futurs
    - Éviction intelligente creator-aware
    - Analytics en temps réel
    """
    
    def __init__(
        self,
        l1_max_size_mb -> None: int = 512,         # 512MB RAM cache
        l2_max_size_gb -> None: int = 10,          # 10GB SSD cache
        l3_max_size_gb -> None: int = 100,         # 100GB network cache
        default_ttl -> None: int = 3600,           # 1 heure par défaut
        enable_prefetch -> None: bool = True,
        enable_analytics -> None: bool = True
    ) -> None:
        self.l1_max_size_bytes = l1_max_size_mb * 1024 * 1024
        self.l2_max_size_bytes = l2_max_size_gb * 1024 * 1024 * 1024
        self.l3_max_size_bytes = l3_max_size_gb * 1024 * 1024 * 1024
        self.default_ttl = default_ttl
        self.enable_prefetch = enable_prefetch
        self.enable_analytics = enable_analytics
        
        # Caches multi-niveaux
        self.l1_cache: OrderedDict[str, CacheEntry] = OrderedDict()  # LRU automatique
        self.l2_cache: Dict[str, CacheEntry] = {}
        self.l3_cache: Dict[str, CacheEntry] = {}
        
        # Index pour recherche rapide
        self.key_to_tier: Dict[str, CacheTier] = {}
        self.creator_index: Dict[str, List[str]] = defaultdict(list)
        
        # Statistiques et analytics
        self.stats = CacheStats()
        self.access_patterns: Dict[str, List[datetime]] = defaultdict(list)
        self.creator_patterns: Dict[str, Dict[str, List[datetime]]] = defaultdict(lambda: defaultdict(list))
        
        # Configuration des politiques d'éviction
        self.eviction_policies: Dict[CacheTier, EvictionPolicy] = {
            CacheTier.L1_MEMORY: EvictionPolicy.LRU,
            CacheTier.L2_SSD: EvictionPolicy.LFU,
            CacheTier.L3_NETWORK: EvictionPolicy.CREATOR_AWARE
        }
        
        # Thread lock pour thread safety
        self.lock = threading.RLock()
        
        # Prédicteur de prefetch
        self.prefetch_predictions: List[PrefetchPrediction] = []
        
        logger.info("⚡ Feature Cache Optimizer initialized")
    
    async def get(
        self,
        key: str,
        creator_type: Optional[str] = None,
        default: Any = None
    ) -> Tuple[Any, CacheHitType]:
        """Récupérer une feature du cache"""
        
        start_time = time.time()
        
        with self.lock:
            # Vérifier L1 cache (memory)
            if key in self.l1_cache:
                entry = self.l1_cache[key]
                if not entry.is_expired:
                    # Move to end (LRU)
                    self.l1_cache.move_to_end(key)
                    entry.last_accessed = datetime.now()
                    entry.access_count += 1
                    
                    self._update_access_patterns(key, creator_type)
                    self._update_stats_hit(start_time)
                    
                    return entry.value, CacheHitType.HIT
                else:
                    # Entrée expirée
                    del self.l1_cache[key]
            
            # Vérifier L2 cache (SSD)
            if key in self.l2_cache:
                entry = self.l2_cache[key]
                if not entry.is_expired:
                    # Promouvoir vers L1 si populaire
                    if entry.access_count > 5:
                        await self._promote_to_l1(key, entry)
                    
                    entry.last_accessed = datetime.now()
                    entry.access_count += 1
                    
                    self._update_access_patterns(key, creator_type)
                    self._update_stats_hit(start_time)
                    
                    return entry.value, CacheHitType.HIT
                else:
                    del self.l2_cache[key]
            
            # Vérifier L3 cache (network)
            if key in self.l3_cache:
                entry = self.l3_cache[key]
                if not entry.is_expired:
                    # Promouvoir vers L2 si populaire
                    if entry.access_count > 10:
                        await self._promote_to_l2(key, entry)
                    
                    entry.last_accessed = datetime.now()
                    entry.access_count += 1
                    
                    self._update_access_patterns(key, creator_type)
                    self._update_stats_hit(start_time)
                    
                    return entry.value, CacheHitType.HIT
                else:
                    del self.l3_cache[key]
            
            # Cache miss
            self._update_stats_miss()
            return default, CacheHitType.MISS
    
    async def set(
        self,
        key: str,
        value: Any,
        creator_types: Optional[List[str]] = None,
        ttl: Optional[int] = None,
        tier: Optional[CacheTier] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Stocker une feature dans le cache"""
        
        with self.lock:
            # Calculer la taille
            size_bytes = self._calculate_size(value)
            
            # Déterminer le tier optimal
            if tier is None:
                tier = self._determine_optimal_tier(size_bytes, creator_types)
            
            # Créer l'entrée
            entry = CacheEntry(
                key=key,
                value=value,
                tier=tier,
                created_at=datetime.now(),
                last_accessed=datetime.now(),
                creator_types=creator_types or [],
                size_bytes=size_bytes,
                ttl_seconds=ttl or self.default_ttl,
                metadata=metadata or {}
            )
            
            # Stocker dans le tier approprié
            success = await self._store_in_tier(key, entry, tier)
            
            if success:
                # Mettre à jour les index
                self.key_to_tier[key] = tier
                for creator_type in entry.creator_types:
                    self.creator_index[creator_type].append(key)
                
                # Déclencher le prefetch si activé
                if self.enable_prefetch:
                    await self._trigger_prefetch_analysis(key, creator_types)
            
            return success
    
    async def _store_in_tier(
        self,
        key: str,
        entry: CacheEntry,
        tier: CacheTier
    ) -> bool:
        """Stocker dans un tier spécifique"""
        
        if tier == CacheTier.L1_MEMORY:
            # Vérifier la capacité L1
            if self._get_l1_size() + entry.size_bytes > self.l1_max_size_bytes:
                await self._evict_from_l1()
            
            self.l1_cache[key] = entry
            return True
        
        elif tier == CacheTier.L2_SSD:
            # Vérifier la capacité L2
            if self._get_l2_size() + entry.size_bytes > self.l2_max_size_bytes:
                await self._evict_from_l2()
            
            self.l2_cache[key] = entry
            return True
        
        elif tier == CacheTier.L3_NETWORK:
            # Vérifier la capacité L3
            if self._get_l3_size() + entry.size_bytes > self.l3_max_size_bytes:
                await self._evict_from_l3()
            
            self.l3_cache[key] = entry
            return True
        
        return False
    
    def _determine_optimal_tier(
        self,
        size_bytes: int,
        creator_types: Optional[List[str]]
    ) -> CacheTier:
        """Déterminer le tier optimal pour une feature"""
        
        # Features très petites et très accédées → L1
        if size_bytes < 1024 * 1024:  # < 1MB
            return CacheTier.L1_MEMORY
        
        # Features moyennes et populaires → L2
        if size_bytes < 100 * 1024 * 1024:  # < 100MB
            return CacheTier.L2_SSD
        
        # Features larges → L3
        return CacheTier.L3_NETWORK
    
    async def _evict_from_l1(self) -> None:
        """Éviction intelligente du cache L1"""
        
        policy = self.eviction_policies[CacheTier.L1_MEMORY]
        
        if policy == EvictionPolicy.LRU:
            # LRU automatique avec OrderedDict
            if self.l1_cache:
                key, entry = self.l1_cache.popitem(last=False)
                # Dégrader vers L2 si populaire
                if entry.access_count > 3:
                    await self._demote_to_l2(key, entry)
                self.stats.evictions += 1
        
        elif policy == EvictionPolicy.CREATOR_AWARE:
            # Éviction basée sur la priorité des creators
            await self._creator_aware_eviction(CacheTier.L1_MEMORY)
    
    async def _evict_from_l2(self) -> None:
        """Éviction intelligente du cache L2"""
        
        policy = self.eviction_policies[CacheTier.L2_SSD]
        
        if policy == EvictionPolicy.LFU:
            # Trouver l'entrée la moins fréquemment utilisée
            min_count = float('inf')
            evict_key = None
            
            for key, entry in self.l2_cache.items():
                if entry.access_count < min_count:
                    min_count = entry.access_count
                    evict_key = key
            
            if evict_key:
                entry = self.l2_cache.pop(evict_key)
                # Dégrader vers L3
                await self._demote_to_l3(evict_key, entry)
                self.stats.evictions += 1
    
    async def _evict_from_l3(self) -> None:
        """Éviction du cache L3"""
        
        # Supprimer les entrées les plus anciennes
        oldest_key = None
        oldest_time = datetime.now()
        
        for key, entry in self.l3_cache.items():
            if entry.last_accessed < oldest_time:
                oldest_time = entry.last_accessed
                oldest_key = key
        
        if oldest_key:
            del self.l3_cache[oldest_key]
            if oldest_key in self.key_to_tier:
                del self.key_to_tier[oldest_key]
            self.stats.evictions += 1
    
    async def _promote_to_l1(self, key -> None: str, entry -> None: CacheEntry) -> None:
        """Promouvoir une entrée vers L1"""
        
        # Copier vers L1
        entry.tier = CacheTier.L1_MEMORY
        await self._store_in_tier(key, entry, CacheTier.L1_MEMORY)
        
        # Supprimer de L2
        if key in self.l2_cache:
            del self.l2_cache[key]
        
        logger.debug(f"⬆️ Promoted {key} to L1 cache")
    
    async def _promote_to_l2(self, key -> None: str, entry -> None: CacheEntry) -> None:
        """Promouvoir une entrée vers L2"""
        
        # Copier vers L2
        entry.tier = CacheTier.L2_SSD
        await self._store_in_tier(key, entry, CacheTier.L2_SSD)
        
        # Supprimer de L3
        if key in self.l3_cache:
            del self.l3_cache[key]
        
        logger.debug(f"⬆️ Promoted {key} to L2 cache")
    
    async def _demote_to_l2(self, key -> None: str, entry -> None: CacheEntry) -> None:
        """Dégrader une entrée vers L2"""
        
        entry.tier = CacheTier.L2_SSD
        await self._store_in_tier(key, entry, CacheTier.L2_SSD)
        
        logger.debug(f"⬇️ Demoted {key} to L2 cache")
    
    async def _demote_to_l3(self, key -> None: str, entry -> None: CacheEntry) -> None:
        """Dégrader une entrée vers L3"""
        
        entry.tier = CacheTier.L3_NETWORK
        await self._store_in_tier(key, entry, CacheTier.L3_NETWORK)
        
        logger.debug(f"⬇️ Demoted {key} to L3 cache")
    
    async def _trigger_prefetch_analysis(
        self,
        key -> None: str,
        creator_types -> None: Optional[List[str]]
    ) -> None:
        """Déclencher l'analyse de prefetch"""
        
        if not self.enable_prefetch or not creator_types:
            return
        
        # Analyser les patterns pour prédire les prochains accès
        predictions = await self._predict_next_accesses(key, creator_types)
        
        for prediction in predictions:
            if prediction.confidence > 0.7:  # Seuil de confiance
                await self._schedule_prefetch(prediction)
    
    async def _predict_next_accesses(
        self,
        current_key: str,
        creator_types: List[str]
    ) -> List[PrefetchPrediction]:
        """Prédire les prochains accès"""
        
        predictions = []
        
        for creator_type in creator_types:
            # Analyser les patterns d'accès du creator
            creator_patterns = self.creator_patterns[creator_type]
            
            # Logique de prédiction simple (à améliorer avec ML)
            for feature_key, access_times in creator_patterns.items():
                if feature_key != current_key and len(access_times) > 2:
                    # Calculer la probabilité d'accès
                    recent_accesses = [t for t in access_times if (datetime.now() - t).total_seconds() < 3600]
                    
                    if len(recent_accesses) > 0:
                        confidence = min(len(recent_accesses) / 10.0, 0.9)
                        predicted_time = datetime.now() + timedelta(minutes=5)
                        
                        prediction = PrefetchPrediction(
                            key=feature_key,
                            confidence=confidence,
                            predicted_access_time=predicted_time,
                            creator_type=creator_type,
                            reasons=[f"Pattern detected for {creator_type}"]
                        )
                        predictions.append(prediction)
        
        return predictions
    
    async def _schedule_prefetch(self, prediction -> None: PrefetchPrediction) -> None:
        """Planifier un prefetch"""
        
        # Simple: ajouter à la liste des prédictions
        # Dans un vrai système, on utiliserait un scheduler async
        self.prefetch_predictions.append(prediction)
        
        logger.debug(f"🔮 Scheduled prefetch for {prediction.key} (confidence: {prediction.confidence:.2f})")
    
    def _update_access_patterns(self, key -> None: str, creator_type -> None: Optional[str]) -> None:
        """Mettre à jour les patterns d'accès"""
        
        now = datetime.now()
        
        # Pattern global
        self.access_patterns[key].append(now)
        
        # Pattern par creator
        if creator_type:
            self.creator_patterns[creator_type][key].append(now)
        
        # Garder seulement les 100 derniers accès
        if len(self.access_patterns[key]) > 100:
            self.access_patterns[key] = self.access_patterns[key][-100:]
        
        if creator_type and len(self.creator_patterns[creator_type][key]) > 100:
            self.creator_patterns[creator_type][key] = self.creator_patterns[creator_type][key][-100:]
    
    def _update_stats_hit(self, start_time -> None: float) -> None:
        """Mettre à jour les stats pour un hit"""
        
        self.stats.hits += 1
        access_time_ms = (time.time() - start_time) * 1000
        
        # Moyenne mobile pour le temps d'accès
        alpha = 0.1
        self.stats.avg_access_time_ms = (
            alpha * access_time_ms + 
            (1 - alpha) * self.stats.avg_access_time_ms
        )
        
        # Taux de hit
        total_requests = self.stats.hits + self.stats.misses
        self.stats.hit_rate = self.stats.hits / total_requests if total_requests > 0 else 0.0
    
    def _update_stats_miss(self) -> None:
        """Mettre à jour les stats pour un miss"""
        
        self.stats.misses += 1
        
        # Taux de hit
        total_requests = self.stats.hits + self.stats.misses
        self.stats.hit_rate = self.stats.hits / total_requests if total_requests > 0 else 0.0
    
    def _calculate_size(self, value: Any) -> int:
        """Calculer la taille d'une valeur"""
        
        if isinstance(value, (str, bytes)):
            return len(value.encode('utf-8') if isinstance(value, str) else value)
        elif isinstance(value, (int, float)):
            return 8
        elif isinstance(value, np.ndarray):
            return value.nbytes
        elif isinstance(value, pd.DataFrame):
            return value.memory_usage(deep=True).sum()
        else:
            # Estimation avec pickle
            try:
                return len(pickle.dumps(value))
            except:
                return 1024  # 1KB par défaut
    
    def _get_l1_size(self) -> int:
        """Obtenir la taille du cache L1"""
        return sum(entry.size_bytes for entry in self.l1_cache.values())
    
    def _get_l2_size(self) -> int:
        """Obtenir la taille du cache L2"""
        return sum(entry.size_bytes for entry in self.l2_cache.values())
    
    def _get_l3_size(self) -> int:
        """Obtenir la taille du cache L3"""
        return sum(entry.size_bytes for entry in self.l3_cache.values())
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Obtenir les statistiques du cache"""
        
        # Mettre à jour les tailles
        self.stats.memory_usage_bytes = self._get_l1_size()
        self.stats.storage_usage_bytes = self._get_l2_size() + self._get_l3_size()
        
        return {
            'performance': {
                'hit_rate': self.stats.hit_rate,
                'total_hits': self.stats.hits,
                'total_misses': self.stats.misses,
                'avg_access_time_ms': self.stats.avg_access_time_ms,
                'total_evictions': self.stats.evictions
            },
            'storage': {
                'l1_entries': len(self.l1_cache),
                'l2_entries': len(self.l2_cache),
                'l3_entries': len(self.l3_cache),
                'l1_size_mb': self._get_l1_size() / 1024 / 1024,
                'l2_size_gb': self._get_l2_size() / 1024 / 1024 / 1024,
                'l3_size_gb': self._get_l3_size() / 1024 / 1024 / 1024
            },
            'optimization': {
                'prefetch_predictions': len(self.prefetch_predictions),
                'tracked_patterns': len(self.access_patterns),
                'creator_patterns': len(self.creator_patterns)
            }
        }
    
    async def invalidate(self, key: str) -> bool:
        """Invalider une entrée du cache"""
        
        with self.lock:
            invalidated = False
            
            if key in self.l1_cache:
                del self.l1_cache[key]
                invalidated = True
            
            if key in self.l2_cache:
                del self.l2_cache[key]
                invalidated = True
            
            if key in self.l3_cache:
                del self.l3_cache[key]
                invalidated = True
            
            if key in self.key_to_tier:
                del self.key_to_tier[key]
            
            return invalidated
    
    async def clear_cache(self, tier -> None: Optional[CacheTier] = None) -> None:
        """Vider le cache"""
        
        with self.lock:
            if tier is None or tier == CacheTier.L1_MEMORY:
                self.l1_cache.clear()
            
            if tier is None or tier == CacheTier.L2_SSD:
                self.l2_cache.clear()
            
            if tier is None or tier == CacheTier.L3_NETWORK:
                self.l3_cache.clear()
            
            if tier is None:
                self.key_to_tier.clear()
                self.creator_index.clear()
                self.access_patterns.clear()
                self.creator_patterns.clear()
                self.stats = CacheStats()

# Usage Example
async def main() -> None:
    """Exemple d'utilisation du Feature Cache Optimizer"""
    
    cache = FeatureCacheOptimizer(
        l1_max_size_mb=256,
        l2_max_size_gb=5,
        enable_prefetch=True
    )
    
    # Stocker des features
    await cache.set(
        "user_engagement_musician_123",
        {"score": 0.85, "trend": "increasing"},
        creator_types=["musician"],
        ttl=1800
    )
    
    await cache.set(
        "content_features_audio_456",
        np.random.rand(128),  # Embedding
        creator_types=["musician"],
        tier=CacheTier.L2_SSD
    )
    
    # Récupérer des features
    value, hit_type = await cache.get("user_engagement_musician_123", "musician")
    print(f"Retrieved value: {value}, Hit type: {hit_type}")
    
    # Statistiques
    stats = await cache.get_cache_stats()
    print(f"Cache stats: {stats}")

if __name__ == "__main__":
    asyncio.run(main())