"""
Eviction Strategy Optimizer module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠 Eviction Strategy Optimizer - Optimiseur Stratégies d'Éviction Enterprise
==========================================================================

Optimiseur intelligent des stratégies d'éviction cache avec IA pour maximiser
l'efficacité et minimiser les misses critiques.

**Rôles Experts:**
- **Lead Dev IA**: Algorithmes IA pour optimisation éviction intelligente
- **ML Engineer**: Machine Learning pour prédiction patterns éviction optimaux
- **Backend Senior**: Architecture éviction haute performance
- **DBA**: Optimisation mémoire et stratégies stockage

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import time
import json
import hashlib
from typing import Dict, Any, Optional, List, Union, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import yaml
import aioredis
from collections import defaultdict, deque
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
import heapq

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EvictionStrategy(Enum):
    """Stratégies d'éviction disponibles"""
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    TTL_BASED = "ttl_based"  # Time To Live priority
    SIZE_AWARE = "size_aware"  # Size-based eviction
    COST_BENEFIT = "cost_benefit"  # Cost-benefit analysis
    ML_OPTIMIZED = "ml_optimized"  # Machine Learning optimized
    ADAPTIVE_HYBRID = "adaptive_hybrid"  # Adaptive multi-strategy
    PRIORITY_SCORE = "priority_score"  # Custom priority scoring

class EvictionTrigger(Enum):
    """Déclencheurs d'éviction"""
    MEMORY_PRESSURE = "memory_pressure"
    SIZE_LIMIT = "size_limit"
    TTL_EXPIRY = "ttl_expiry"
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    ML_PREDICTION = "ml_prediction"

@dataclass
class CacheItem:
    """Représentation d'un élément de cache"""
    key: str
    size_bytes: int
    creation_time: float
    last_access_time: float
    access_count: int
    ttl_seconds: Optional[int]
    priority_score: float
    computation_cost: float
    hit_count: int = 0
    miss_count: int = 0
    eviction_resistance: float = 1.0  # Résistance à l'éviction (0-1)

@dataclass
class EvictionMetrics:
    """Métriques d'éviction"""
    total_evictions: int = 0
    successful_evictions: int = 0
    memory_freed_bytes: int = 0
    average_item_age: float = 0.0
    eviction_efficiency: float = 0.0
    strategy_performance: Dict[str, float] = field(default_factory=dict)
    last_eviction_time: float = 0.0

class EvictionStrategyOptimizer:
    """
    🧠 Optimiseur Stratégies d'Éviction Enterprise
    
    **Lead Dev IA**: Orchestration IA éviction multi-stratégies adaptatives
    **ML Engineer**: Algorithmes ML prédiction éviction optimale
    **Backend Senior**: Architecture éviction haute performance
    **DBA**: Optimisation mémoire et gestion stockage intelligent
    """
    
    def __init__(self, redis_pool, config -> None: Optional[Dict[str, Any]] = None) -> None:
        self.redis_pool = redis_pool
        self.config = config or self._get_default_config()
        
        # Cache items tracking
        self.cache_items: Dict[str, CacheItem] = {}
        self.eviction_queue: List[Tuple[float, str]] = []  # Priority queue
        
        # ML Model pour prédiction éviction optimale
        self.ml_model: Optional[GradientBoostingClassifier] = None
        self.scaler: Optional[StandardScaler] = None
        
        # Métriques et analytics
        self.metrics = EvictionMetrics()
        self.strategy_history: deque = deque(maxlen=10000)
        
        # Configuration thresholds
        self.memory_threshold = self.config.get('memory_threshold', 0.85)
        self.size_threshold = self.config.get('size_threshold', 100000000)  # 100MB
        self.eviction_batch_size = self.config.get('eviction_batch_size', 100)
        
        # Stratégie par défaut
        self.current_strategy = EvictionStrategy.ADAPTIVE_HYBRID
        
        logger.info("🧠 Eviction Strategy Optimizer initialisé")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """**DBA**: Configuration par défaut optimisée"""
        return {
            'memory_threshold': 0.85,
            'size_threshold': 100000000,  # 100MB
            'eviction_batch_size': 100,
            'ml_enabled': True,
            'adaptive_learning': True,
            'strategy_weights': {
                'lru': 0.2,
                'lfu': 0.2,
                'ttl_based': 0.15,
                'size_aware': 0.15,
                'cost_benefit': 0.2,
                'ml_optimized': 0.1
            },
            'priority_factors': {
                'access_frequency': 0.3,
                'recency': 0.25,
                'size_efficiency': 0.2,
                'computation_cost': 0.25
            }
        }
    
    async def initialize_ml_model(self) -> None:
        """**ML Engineer**: Initialisation modèle ML éviction"""
        try:
            self.ml_model = GradientBoostingClassifier(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=6,
                random_state=42
            )
            self.scaler = StandardScaler()
            
            # Entraînement avec données simulées
            await self._train_initial_model()
            
            logger.info("✅ Modèle ML éviction initialisé")
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation ML éviction: {e}")
    
    async def _train_initial_model(self) -> None:
        """**ML Engineer**: Entraînement initial avec données simulées"""
        try:
            # Génération données d'entraînement
            n_samples = 2000
            features = []
            targets = []
            
            for _ in range(n_samples):
                # Features: age, access_freq, size, ttl_remaining, hit_ratio
                age = np.random.exponential(3600)  # Age en secondes
                access_freq = np.random.exponential(1.0)
                size = np.random.lognormal(10, 2)
                ttl_remaining = np.random.uniform(0, 7200)
                hit_ratio = np.random.beta(8, 2)  # Biaisé vers hit élevé
                computation_cost = np.random.exponential(0.1)
                
                features.append([age, access_freq, size, ttl_remaining, hit_ratio, computation_cost])
                
                # Target: probabilité d'éviction (0=garder, 1=évincer)
                # Logique: évincer si âgé, peu accédé, gros, TTL court
                eviction_prob = (
                    0.3 * min(1.0, age / 7200) +  # Age factor
                    0.2 * max(0.0, 1.0 - access_freq) +  # Inverse access freq
                    0.2 * min(1.0, size / 1000000) +  # Size factor
                    0.2 * max(0.0, 1.0 - ttl_remaining / 3600) +  # TTL urgency
                    0.1 * max(0.0, 1.0 - hit_ratio)  # Low hit ratio
                )
                
                targets.append(1 if eviction_prob > 0.6 else 0)
            
            # Entraînement
            features_scaled = self.scaler.fit_transform(features)
            self.ml_model.fit(features_scaled, targets)
            
            accuracy = self.ml_model.score(features_scaled, targets)
            logger.info(f"🎯 Modèle ML éviction entraîné - Précision: {accuracy:.3f}")
            
        except Exception as e:
            logger.error(f"❌ Erreur entraînement ML éviction: {e}")
    
    async def register_cache_item(self, key -> None: str, size_bytes -> None: int, ttl_seconds -> None: Optional[int] = None) -> None:
        """**Backend Senior**: Enregistrement nouvel élément cache"""
        try:
            current_time = time.time()
            
            # Calcul score priorité initial
            priority_score = await self._calculate_priority_score(
                key, size_bytes, current_time, ttl_seconds
            )
            
            self.cache_items[key] = CacheItem(
                key=key,
                size_bytes=size_bytes,
                creation_time=current_time,
                last_access_time=current_time,
                access_count=1,
                ttl_seconds=ttl_seconds,
                priority_score=priority_score,
                computation_cost=0.1  # Valeur par défaut
            )
            
            logger.debug(f"📝 Élément cache enregistré: {key} ({size_bytes} bytes)")
            
        except Exception as e:
            logger.error(f"❌ Erreur enregistrement cache {key}: {e}")
    
    async def update_access_metrics(self, key -> None: str, hit -> None: bool = True) -> None:
        """**DBA**: Mise à jour métriques d'accès"""
        if key in self.cache_items:
            item = self.cache_items[key]
            current_time = time.time()
            
            item.last_access_time = current_time
            item.access_count += 1
            
            if hit:
                item.hit_count += 1
            else:
                item.miss_count += 1
            
            # Recalcul score priorité
            item.priority_score = await self._calculate_priority_score(
                key, item.size_bytes, current_time, item.ttl_seconds, item
            )
    
    async def _calculate_priority_score(
        self, 
        key: str, 
        size_bytes: int, 
        current_time: float,
        ttl_seconds: Optional[int] = None,
        existing_item: Optional[CacheItem] = None
    ) -> float:
        """**Lead Dev IA**: Calcul score priorité intelligent multi-facteurs"""
        
        factors = self.config['priority_factors']
        score = 0.0
        
        # Facteur fréquence d'accès
        if existing_item:
            access_frequency = existing_item.access_count / max(1, current_time - existing_item.creation_time)
            score += factors['access_frequency'] * min(1.0, access_frequency / 0.1)  # Normalized
        
        # Facteur récence
        if existing_item:
            recency = max(0, 1.0 - (current_time - existing_item.last_access_time) / 3600)
            score += factors['recency'] * recency
        
        # Facteur efficacité taille (inverse de la taille)
        size_efficiency = max(0, 1.0 - size_bytes / 10000000)  # 10MB max
        score += factors['size_efficiency'] * size_efficiency
        
        # Facteur coût computation
        if existing_item:
            computation_factor = min(1.0, existing_item.computation_cost / 1.0)
            score += factors['computation_cost'] * computation_factor
        
        return min(1.0, max(0.0, score))
    
    async def should_evict_item(self, key: str) -> Tuple[bool, float, str]:
        """**ML Engineer**: Décision éviction avec ML"""
        
        if key not in self.cache_items:
            return False, 0.0, "Item not found"
        
        item = self.cache_items[key]
        current_time = time.time()
        
        # Éviction basée ML si disponible
        if self.ml_model and self.config.get('ml_enabled', True):
            try:
                features = self._extract_ml_features(item, current_time)
                features_scaled = self.scaler.transform([features])
                eviction_prob = self.ml_model.predict_proba(features_scaled)[0][1]
                
                return eviction_prob > 0.6, eviction_prob, "ML prediction"
                
            except Exception as e:
                logger.warning(f"⚠️ Erreur prédiction ML: {e}")
        
        # Fallback éviction heuristique
        return await self._heuristic_eviction_decision(item, current_time)
    
    def _extract_ml_features(self, item: CacheItem, current_time: float) -> List[float]:
        """**ML Engineer**: Extraction features pour ML"""
        age = current_time - item.creation_time
        access_freq = item.access_count / max(1, age)
        ttl_remaining = 0
        
        if item.ttl_seconds:
            ttl_remaining = max(0, item.ttl_seconds - age)
        
        hit_ratio = item.hit_count / max(1, item.hit_count + item.miss_count)
        
        return [
            age,
            access_freq,
            item.size_bytes,
            ttl_remaining,
            hit_ratio,
            item.computation_cost
        ]
    
    async def _heuristic_eviction_decision(self, item: CacheItem, current_time: float) -> Tuple[bool, float, str]:
        """**Backend Senior**: Décision éviction heuristique"""
        
        # TTL expiré
        if item.ttl_seconds:
            age = current_time - item.creation_time
            if age >= item.ttl_seconds:
                return True, 1.0, "TTL expired"
        
        # Score priorité faible
        if item.priority_score < 0.2:
            return True, 0.8, "Low priority score"
        
        # Élément très ancien sans accès récent
        age = current_time - item.creation_time
        last_access_age = current_time - item.last_access_time
        
        if age > 7200 and last_access_age > 3600:  # 2h age, 1h sans accès
            return True, 0.7, "Aged without recent access"
        
        # Gros élément peu utilisé
        if item.size_bytes > 1000000 and item.access_count < 5:  # 1MB, <5 accès
            return True, 0.6, "Large item with low usage"
        
        return False, item.priority_score, "Keep item"
    
    async def execute_eviction_strategy(
        self, 
        strategy: EvictionStrategy = None,
        target_memory_mb: Optional[int] = None,
        items_to_evict: Optional[int] = None
    ) -> Dict[str, Any]:
        """**Lead Dev IA**: Exécution stratégie éviction intelligente"""
        
        strategy = strategy or self.current_strategy
        start_time = time.time()
        
        logger.info(f"🔄 Exécution éviction stratégie: {strategy.value}")
        
        try:
            # Sélection candidats éviction
            candidates = await self._select_eviction_candidates(strategy, target_memory_mb, items_to_evict)
            
            if not candidates:
                return {
                    'success': True,
                    'evicted_count': 0,
                    'memory_freed': 0,
                    'message': 'No eviction needed'
                }
            
            # Exécution éviction
            evicted_items = []
            total_memory_freed = 0
            
            for key in candidates[:self.eviction_batch_size]:
                if await self._evict_item(key):
                    item = self.cache_items.get(key)
                    if item:
                        evicted_items.append({
                            'key': key,
                            'size_bytes': item.size_bytes,
                            'age': start_time - item.creation_time,
                            'access_count': item.access_count
                        })
                        total_memory_freed += item.size_bytes
            
            # Mise à jour métriques
            self.metrics.total_evictions += len(evicted_items)
            self.metrics.successful_evictions += len(evicted_items)
            self.metrics.memory_freed_bytes += total_memory_freed
            self.metrics.last_eviction_time = start_time
            
            # Calcul efficacité
            if len(candidates) > 0:
                self.metrics.eviction_efficiency = len(evicted_items) / len(candidates)
            
            result = {
                'success': True,
                'strategy': strategy.value,
                'evicted_count': len(evicted_items),
                'memory_freed': total_memory_freed,
                'candidates_considered': len(candidates),
                'efficiency': self.metrics.eviction_efficiency,
                'execution_time': time.time() - start_time,
                'evicted_items': evicted_items[:10]  # Échantillon
            }
            
            logger.info(f"✅ Éviction terminée: {len(evicted_items)} éléments, {total_memory_freed} bytes libérés")
            
            # Apprentissage adaptatif
            if self.config.get('adaptive_learning', True):
                await self._update_strategy_performance(strategy, result)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Erreur exécution éviction: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _select_eviction_candidates(
        self, 
        strategy: EvictionStrategy,
        target_memory_mb: Optional[int],
        items_to_evict: Optional[int]
    ) -> List[str]:
        """**Backend Senior**: Sélection candidats éviction selon stratégie"""
        
        candidates = []
        current_time = time.time()
        
        if strategy == EvictionStrategy.LRU:
            # Least Recently Used
            sorted_items = sorted(
                self.cache_items.items(),
                key=lambda x: x[1].last_access_time
            )
            candidates = [key for key, _ in sorted_items]
            
        elif strategy == EvictionStrategy.LFU:
            # Least Frequently Used
            sorted_items = sorted(
                self.cache_items.items(),
                key=lambda x: x[1].access_count
            )
            candidates = [key for key, _ in sorted_items]
            
        elif strategy == EvictionStrategy.TTL_BASED:
            # TTL priority
            ttl_items = []
            for key, item in self.cache_items.items():
                if item.ttl_seconds:
                    remaining_ttl = item.ttl_seconds - (current_time - item.creation_time)
                    ttl_items.append((remaining_ttl, key))
            
            ttl_items.sort()
            candidates = [key for _, key in ttl_items]
            
        elif strategy == EvictionStrategy.SIZE_AWARE:
            # Size-based (plus gros d'abord)
            sorted_items = sorted(
                self.cache_items.items(),
                key=lambda x: x[1].size_bytes,
                reverse=True
            )
            candidates = [key for key, _ in sorted_items]
            
        elif strategy == EvictionStrategy.ML_OPTIMIZED:
            # ML-based éviction
            ml_scores = []
            for key, item in self.cache_items.items():
                should_evict, prob, _ = await self.should_evict_item(key)
                if should_evict:
                    ml_scores.append((prob, key))
            
            ml_scores.sort(reverse=True)
            candidates = [key for _, key in ml_scores]
            
        elif strategy == EvictionStrategy.PRIORITY_SCORE:
            # Priority score based
            sorted_items = sorted(
                self.cache_items.items(),
                key=lambda x: x[1].priority_score
            )
            candidates = [key for key, _ in sorted_items]
            
        elif strategy == EvictionStrategy.ADAPTIVE_HYBRID:
            # Combinaison intelligente de stratégies
            candidates = await self._hybrid_candidate_selection()
        
        # Limitation selon critères
        if target_memory_mb:
            candidates = await self._limit_by_memory_target(candidates, target_memory_mb)
        
        if items_to_evict:
            candidates = candidates[:items_to_evict]
        
        return candidates
    
    async def _hybrid_candidate_selection(self) -> List[str]:
        """**Lead Dev IA**: Sélection hybride intelligente"""
        
        strategy_weights = self.config['strategy_weights']
        candidate_scores = defaultdict(float)
        
        # Score LRU
        lru_candidates = await self._select_eviction_candidates(EvictionStrategy.LRU, None, None)
        for i, key in enumerate(lru_candidates):
            candidate_scores[key] += strategy_weights['lru'] * (1.0 - i / len(lru_candidates))
        
        # Score LFU
        lfu_candidates = await self._select_eviction_candidates(EvictionStrategy.LFU, None, None)
        for i, key in enumerate(lfu_candidates):
            candidate_scores[key] += strategy_weights['lfu'] * (1.0 - i / len(lfu_candidates))
        
        # Score TTL
        ttl_candidates = await self._select_eviction_candidates(EvictionStrategy.TTL_BASED, None, None)
        for i, key in enumerate(ttl_candidates):
            candidate_scores[key] += strategy_weights['ttl_based'] * (1.0 - i / len(ttl_candidates))
        
        # Score ML si disponible
        if self.ml_model:
            ml_candidates = await self._select_eviction_candidates(EvictionStrategy.ML_OPTIMIZED, None, None)
            for i, key in enumerate(ml_candidates):
                candidate_scores[key] += strategy_weights['ml_optimized'] * (1.0 - i / len(ml_candidates))
        
        # Tri par score combiné
        sorted_candidates = sorted(
            candidate_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [key for key, _ in sorted_candidates]
    
    async def _limit_by_memory_target(self, candidates: List[str], target_memory_mb: int) -> List[str]:
        """**DBA**: Limitation candidats par cible mémoire"""
        
        target_bytes = target_memory_mb * 1024 * 1024
        accumulated_bytes = 0
        limited_candidates = []
        
        for key in candidates:
            if key in self.cache_items:
                item_size = self.cache_items[key].size_bytes
                if accumulated_bytes + item_size <= target_bytes:
                    limited_candidates.append(key)
                    accumulated_bytes += item_size
                else:
                    break
        
        return limited_candidates
    
    async def _evict_item(self, key: str) -> bool:
        """**Backend Senior**: Éviction effective d'un élément"""
        try:
            # Suppression Redis
            async with self.redis_pool.get_connection() as redis_conn:
                deleted = await redis_conn.delete(key)
                
                if deleted:
                    # Suppression métadonnées
                    await redis_conn.delete(f"meta:{key}")
                    
                    # Suppression tracking local
                    if key in self.cache_items:
                        del self.cache_items[key]
                    
                    logger.debug(f"🗑️ Élément évincé: {key}")
                    return True
                else:
                    logger.warning(f"⚠️ Élément non trouvé pour éviction: {key}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Erreur éviction {key}: {e}")
            return False
    
    async def _update_strategy_performance(self, strategy -> None: EvictionStrategy, result -> None: Dict[str, Any]) -> None:
        """**ML Engineer**: Mise à jour performance stratégies"""
        
        performance_score = result['efficiency'] * 0.5 + (1.0 - result['execution_time'] / 10.0) * 0.5
        
        if strategy.value not in self.metrics.strategy_performance:
            self.metrics.strategy_performance[strategy.value] = performance_score
        else:
            # Moyenne mobile
            current_score = self.metrics.strategy_performance[strategy.value]
            self.metrics.strategy_performance[strategy.value] = current_score * 0.9 + performance_score * 0.1
        
        # Enregistrement historique
        self.strategy_history.append({
            'timestamp': time.time(),
            'strategy': strategy.value,
            'performance': performance_score,
            'evicted_count': result['evicted_count'],
            'memory_freed': result['memory_freed']
        })
    
    async def get_optimal_strategy(self) -> EvictionStrategy:
        """**Lead Dev IA**: Sélection stratégie optimale basée performance"""
        
        if not self.metrics.strategy_performance:
            return EvictionStrategy.ADAPTIVE_HYBRID
        
        best_strategy = max(
            self.metrics.strategy_performance.items(),
            key=lambda x: x[1]
        )[0]
        
        return EvictionStrategy(best_strategy)
    
    async def get_eviction_analytics(self) -> Dict[str, Any]:
        """**DevOps**: Analytics détaillées éviction"""
        
        total_items = len(self.cache_items)
        total_size = sum(item.size_bytes for item in self.cache_items.values())
        
        # Distribution âges
        current_time = time.time()
        ages = [current_time - item.creation_time for item in self.cache_items.values()]
        avg_age = np.mean(ages) if ages else 0
        
        # Distribution tailles
        sizes = [item.size_bytes for item in self.cache_items.values()]
        avg_size = np.mean(sizes) if sizes else 0
        
        return {
            'cache_state': {
                'total_items': total_items,
                'total_size_bytes': total_size,
                'total_size_mb': total_size / (1024 * 1024),
                'average_age_seconds': avg_age,
                'average_size_bytes': avg_size
            },
            'eviction_metrics': {
                'total_evictions': self.metrics.total_evictions,
                'successful_evictions': self.metrics.successful_evictions,
                'memory_freed_mb': self.metrics.memory_freed_bytes / (1024 * 1024),
                'eviction_efficiency': self.metrics.eviction_efficiency,
                'last_eviction': self.metrics.last_eviction_time
            },
            'strategy_performance': self.metrics.strategy_performance,
            'current_strategy': self.current_strategy.value,
            'recommended_strategy': (await self.get_optimal_strategy()).value,
            'thresholds': {
                'memory_threshold': self.memory_threshold,
                'size_threshold': self.size_threshold,
                'eviction_batch_size': self.eviction_batch_size
            }
        }

# Factory function
async def create_eviction_optimizer(redis_pool, config -> None: Optional[Dict[str, Any]] = None) -> None:
    """**Lead Dev IA**: Factory création optimiseur éviction"""
    optimizer = EvictionStrategyOptimizer(redis_pool, config)
    
    if config and config.get('ml_enabled', True):
        await optimizer.initialize_ml_model()
    
    return optimizer

if __name__ == "__main__":
    async def demo() -> None:
        """Démonstration Eviction Strategy Optimizer"""
        
        # Configuration Redis simulée
        class MockRedisPool:
    """MockRedisPool: class implementation"""
            def get_connection(self) -> None:
                from unittest.mock import AsyncMock
                mock = AsyncMock()
                mock.delete.return_value = 1
                return mock
        
        # Création optimizer
        optimizer = await create_eviction_optimizer(MockRedisPool())
        
        # Simulation éléments cache
        await optimizer.register_cache_item("user:123", 1024, 3600)
        await optimizer.register_cache_item("media:456", 5000000, 7200)
        await optimizer.register_cache_item("temp:789", 2048, 300)
        
        # Simulation accès
        await optimizer.update_access_metrics("user:123", hit=True)
        await optimizer.update_access_metrics("media:456", hit=False)
        
        # Test éviction
        result = await optimizer.execute_eviction_strategy(EvictionStrategy.ADAPTIVE_HYBRID)
        print(f"Résultat éviction: {result}")
        
        # Analytics
        analytics = await optimizer.get_eviction_analytics()
        print(f"Analytics éviction: {analytics}")
    
    asyncio.run(demo())