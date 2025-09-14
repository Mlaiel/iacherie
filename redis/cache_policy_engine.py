"""
Cache Policy Engine module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠 Cache Policy Engine - Intelligence de Cache Enterprise
=========================================================

Moteur de politiques de cache intelligent avec IA pour optimisation
automatique des stratégies de mise en cache.

**Rôles Experts:**
- **Lead Dev IA**: Algorithmes IA pour optimisation cache automatique
- **ML Engineer**: Machine Learning pour prédiction patterns cache
- **Backend Senior**: Architecture cache haute performance
- **DBA**: Optimisation stockage et indexation cache

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import time
import json
import hashlib
from typing import Dict, Any, Optional, List, Union, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import yaml
import aioredis
from collections import defaultdict, deque
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CachePolicy(Enum):
    """Types de politiques de cache"""
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    FIFO = "fifo"  # First In, First Out
    TTL = "ttl"  # Time To Live
    ADAPTIVE = "adaptive"  # IA-driven adaptive
    PRIORITY = "priority"  # Priority-based
    SMART_TTL = "smart_ttl"  # ML-optimized TTL
    COST_AWARE = "cost_aware"  # Cost-optimization aware

class CacheLevel(Enum):
    """Niveaux de cache hiérarchique"""
    L1_MEMORY = "l1_memory"  # Cache mémoire ultra-rapide
    L2_REDIS = "l2_redis"  # Cache Redis principal
    L3_PERSISTENT = "l3_persistent"  # Cache persistant
    CDN = "cdn"  # Content Delivery Network

@dataclass
class CacheMetrics:
    """Métriques de performance cache"""
    key: str
    hit_count: int = 0
    miss_count: int = 0
    last_access: float = field(default_factory=time.time)
    creation_time: float = field(default_factory=time.time)
    access_frequency: float = 0.0
    size_bytes: int = 0
    computation_cost: float = 0.0  # Coût calcul original
    access_pattern: List[float] = field(default_factory=list)
    priority_score: float = 1.0

@dataclass
class CachePolicyConfig:
    """Configuration politique de cache"""
    policy_type: CachePolicy
    ttl_seconds: Optional[int] = None
    max_size: Optional[int] = None
    priority_weights: Dict[str, float] = field(default_factory=dict)
    ml_enabled: bool = True
    adaptive_learning: bool = True
    cost_threshold: float = 0.1

class CachePolicyEngine:
    """
    🧠 Moteur de Politiques Cache Intelligent
    
    **Lead Dev IA**: Orchestration IA cache adaptatif multi-niveaux
    **ML Engineer**: Algorithmes ML prédiction et optimisation cache
    **Backend Senior**: Architecture cache haute performance
    **DBA**: Gestion optimisée stockage et indexation
    """
    
    def __init__(self, redis_pool, config_path -> None: Optional[str] = None) -> None:
        self.redis_pool = redis_pool
        self.policies: Dict[str, CachePolicyConfig] = {}
        self.metrics: Dict[str, CacheMetrics] = {}
        self.ml_model: Optional[RandomForestRegressor] = None
        self.scaler: Optional[StandardScaler] = None
        
        # Cache local L1 pour performance ultra-rapide
        self.l1_cache: Dict[str, Any] = {}
        self.l1_max_size = 1000
        
        # Patterns d'accès pour ML
        self.access_patterns: deque = deque(maxlen=10000)
        self.pattern_features: List[List[float]] = []
        self.pattern_targets: List[float] = []
        
        # Configuration par défaut
        self._load_default_policies()
        
        if config_path:
            self._load_policies_from_config(config_path)
        
        # Initialisation modèle ML
        asyncio.create_task(self._initialize_ml_model())
        
        logger.info("🧠 Cache Policy Engine initialisé")
    
    def _load_default_policies(self) -> None:
        """**Backend Senior**: Politiques par défaut optimisées"""
        
        # Politique adaptative IA
        self.policies["adaptive_ai"] = CachePolicyConfig(
            policy_type=CachePolicy.ADAPTIVE,
            ttl_seconds=3600,
            max_size=10000,
            ml_enabled=True,
            adaptive_learning=True,
            priority_weights={
                "access_frequency": 0.3,
                "recency": 0.2,
                "size_efficiency": 0.2,
                "computation_cost": 0.3
            }
        )
        
        # Politique session utilisateur
        self.policies["user_session"] = CachePolicyConfig(
            policy_type=CachePolicy.TTL,
            ttl_seconds=1800,  # 30 minutes
            max_size=5000
        )
        
        # Politique contenu multimédia
        self.policies["media_content"] = CachePolicyConfig(
            policy_type=CachePolicy.SMART_TTL,
            ttl_seconds=7200,  # 2 heures
            ml_enabled=True,
            priority_weights={
                "access_frequency": 0.4,
                "content_popularity": 0.3,
                "size_efficiency": 0.3
            }
        )
        
        # Politique cache IA/ML
        self.policies["ai_inference"] = CachePolicyConfig(
            policy_type=CachePolicy.COST_AWARE,
            ttl_seconds=300,  # 5 minutes pour résultats ML
            cost_threshold=0.5,  # Coût élevé computation
            priority_weights={
                "computation_cost": 0.5,
                "access_frequency": 0.3,
                "accuracy_decay": 0.2
            }
        )
    
    def _load_policies_from_config(self, config_path -> None: str) -> None:
        """**DBA**: Chargement configuration depuis fichier"""
        try:
            with open(config_path, 'r') as f:
                config_data = yaml.safe_load(f)
                
            for policy_name, policy_config in config_data.get('cache_policies', {}).items():
                self.policies[policy_name] = CachePolicyConfig(
                    policy_type=CachePolicy(policy_config['type']),
                    ttl_seconds=policy_config.get('ttl_seconds'),
                    max_size=policy_config.get('max_size'),
                    priority_weights=policy_config.get('priority_weights', {}),
                    ml_enabled=policy_config.get('ml_enabled', True),
                    adaptive_learning=policy_config.get('adaptive_learning', True)
                )
                
            logger.info(f"✅ Politiques chargées depuis {config_path}")
            
        except Exception as e:
            logger.error(f"❌ Erreur chargement config {config_path}: {e}")
    
    async def _initialize_ml_model(self) -> None:
        """**ML Engineer**: Initialisation modèle ML optimisation cache"""
        try:
            # Modèle pour prédiction TTL optimal
            self.ml_model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
            self.scaler = StandardScaler()
            
            # Entraînement avec données historiques simulées
            await self._train_initial_model()
            
            logger.info("✅ Modèle ML cache initialisé")
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation ML: {e}")
    
    async def _train_initial_model(self) -> None:
        """**ML Engineer**: Entraînement initial avec données simulées"""
        # Génération données d'entraînement simulées
        n_samples = 1000
        features = []
        targets = []
        
        for _ in range(n_samples):
            # Features: access_freq, recency, size, computation_cost
            access_freq = np.random.exponential(1.0)
            recency = np.random.uniform(0, 86400)  # 24h en secondes
            size = np.random.lognormal(10, 2)  # Taille en bytes
            comp_cost = np.random.exponential(0.1)
            
            features.append([access_freq, recency, size, comp_cost])
            
            # Target: TTL optimal calculé heuristiquement
            ttl_optimal = min(
                86400,  # Max 24h
                max(
                    300,  # Min 5 minutes
                    int(3600 * access_freq * np.exp(-recency/3600) * comp_cost)
                )
            )
            targets.append(ttl_optimal)
        
        # Entraînement
        features_scaled = self.scaler.fit_transform(features)
        self.ml_model.fit(features_scaled, targets)
        
        self.pattern_features = features
        self.pattern_targets = targets
    
    async def set_cache(
        self, 
        key: str, 
        value: Any, 
        policy_name: str = "adaptive_ai",
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        **Lead Dev IA**: Mise en cache intelligente avec politique adaptative
        """
        try:
            policy = self.policies.get(policy_name)
            if not policy:
                logger.warning(f"⚠️ Politique {policy_name} inconnue, utilisation adaptive_ai")
                policy = self.policies["adaptive_ai"]
            
            # Calcul TTL intelligent
            ttl = await self._calculate_optimal_ttl(key, value, policy, context)
            
            # Sérialisation optimisée
            serialized_value = await self._serialize_value(value)
            size_bytes = len(serialized_value) if isinstance(serialized_value, (str, bytes)) else 0
            
            # Mise à jour métriques
            if key not in self.metrics:
                self.metrics[key] = CacheMetrics(key=key, size_bytes=size_bytes)
            
            self.metrics[key].creation_time = time.time()
            self.metrics[key].size_bytes = size_bytes
            
            # Cache L1 pour accès ultra-rapide
            if policy.policy_type == CachePolicy.ADAPTIVE and size_bytes < 1024:
                await self._set_l1_cache(key, value)
            
            # Cache L2 Redis principal
            async with self.redis_pool.get_connection() as redis_conn:
                success = await redis_conn.setex(key, ttl, serialized_value)
                
                # Stockage métadonnées
                await self._store_cache_metadata(redis_conn, key, ttl, policy_name, context)
                
                if success:
                    logger.debug(f"✅ Cache set: {key} (TTL: {ttl}s, Policy: {policy_name})")
                    
                    # Apprentissage ML
                    if policy.adaptive_learning:
                        await self._record_cache_pattern(key, "set", context)
                    
                    return True
                else:
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Erreur set cache {key}: {e}")
            return False
    
    async def get_cache(self, key: str, policy_name: str = "adaptive_ai") -> Optional[Any]:
        """**Backend Senior**: Récupération cache optimisée multi-niveaux"""
        try:
            start_time = time.time()
            
            # Tentative L1 cache d'abord
            if key in self.l1_cache:
                self._update_access_metrics(key, hit=True, level="L1")
                return self.l1_cache[key]
            
            # Tentative L2 Redis
            async with self.redis_pool.get_connection() as redis_conn:
                serialized_value = await redis_conn.get(key)
                
                if serialized_value:
                    # Hit L2
                    value = await self._deserialize_value(serialized_value)
                    self._update_access_metrics(key, hit=True, level="L2")
                    
                    # Promotion vers L1 si approprié
                    await self._consider_l1_promotion(key, value)
                    
                    # Mise à jour pattern d'accès pour ML
                    await self._record_cache_pattern(key, "hit")
                    
                    response_time = time.time() - start_time
                    logger.debug(f"✅ Cache hit: {key} ({response_time*1000:.2f}ms)")
                    
                    return value
                else:
                    # Miss
                    self._update_access_metrics(key, hit=False)
                    await self._record_cache_pattern(key, "miss")
                    
                    logger.debug(f"❌ Cache miss: {key}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Erreur get cache {key}: {e}")
            return None
    
    async def _calculate_optimal_ttl(
        self, 
        key: str, 
        value: Any, 
        policy: CachePolicyConfig,
        context: Optional[Dict[str, Any]] = None
    ) -> int:
        """**ML Engineer**: Calcul TTL optimal avec IA"""
        
        if policy.policy_type == CachePolicy.TTL:
            return policy.ttl_seconds or 3600
        
        if policy.policy_type == CachePolicy.SMART_TTL and self.ml_model and policy.ml_enabled:
            try:
                # Extraction features pour ML
                metrics = self.metrics.get(key, CacheMetrics(key=key))
                
                features = [
                    metrics.access_frequency,
                    time.time() - metrics.last_access,
                    metrics.size_bytes,
                    metrics.computation_cost
                ]
                
                # Prédiction TTL
                features_scaled = self.scaler.transform([features])
                predicted_ttl = self.ml_model.predict(features_scaled)[0]
                
                # Validation et ajustements
                ttl = max(300, min(86400, int(predicted_ttl)))
                
                logger.debug(f"🤖 TTL ML prédite pour {key}: {ttl}s")
                return ttl
                
            except Exception as e:
                logger.warning(f"⚠️ Erreur prédiction ML TTL: {e}")
        
        if policy.policy_type == CachePolicy.ADAPTIVE:
            # Logique adaptative basée sur métriques
            metrics = self.metrics.get(key, CacheMetrics(key=key))
            
            base_ttl = policy.ttl_seconds or 3600
            
            # Facteurs d'ajustement
            frequency_factor = min(2.0, 1.0 + metrics.access_frequency / 10.0)
            recency_factor = max(0.5, 1.0 - (time.time() - metrics.last_access) / 3600)
            
            adjusted_ttl = int(base_ttl * frequency_factor * recency_factor)
            return max(300, min(86400, adjusted_ttl))
        
        return policy.ttl_seconds or 3600
    
    async def _set_l1_cache(self, key -> None: str, value -> None: Any) -> None:
        """**Backend Senior**: Gestion cache L1 mémoire"""
        if len(self.l1_cache) >= self.l1_max_size:
            # Éviction LRU pour L1
            oldest_key = min(
                self.l1_cache.keys(),
                key=lambda k: self.metrics.get(k, CacheMetrics(key=k)).last_access
            )
            del self.l1_cache[oldest_key]
        
        self.l1_cache[key] = value
    
    async def _consider_l1_promotion(self, key -> None: str, value -> None: Any) -> None:
        """**ML Engineer**: Décision promotion cache L1 basée IA"""
        metrics = self.metrics.get(key, CacheMetrics(key=key))
        
        # Critères promotion L1
        high_frequency = metrics.access_frequency > 5.0
        recent_access = (time.time() - metrics.last_access) < 300  # 5 minutes
        small_size = metrics.size_bytes < 1024  # 1KB
        
        if high_frequency and recent_access and small_size:
            await self._set_l1_cache(key, value)
            logger.debug(f"⬆️ Promotion L1: {key}")
    
    def _update_access_metrics(self, key -> None: str, hit -> None: bool, level -> None: str = "L2") -> None:
        """**DBA**: Mise à jour métriques d'accès"""
        if key not in self.metrics:
            self.metrics[key] = CacheMetrics(key=key)
        
        metrics = self.metrics[key]
        current_time = time.time()
        
        if hit:
            metrics.hit_count += 1
            metrics.last_access = current_time
            
            # Calcul fréquence d'accès (moyenne mobile)
            time_diff = current_time - (metrics.last_access or current_time)
            if time_diff > 0:
                frequency = 1.0 / time_diff
                metrics.access_frequency = (
                    metrics.access_frequency * 0.9 + frequency * 0.1
                )
        else:
            metrics.miss_count += 1
    
    async def _record_cache_pattern(
        self, 
        key -> None: str, 
        operation -> None: str, 
        context -> None: Optional[Dict[str, Any]] = None
    ) -> None:
        """**ML Engineer**: Enregistrement patterns pour apprentissage ML"""
        pattern = {
            "timestamp": time.time(),
            "key": key,
            "operation": operation,
            "context": context or {}
        }
        
        self.access_patterns.append(pattern)
        
        # Mise à jour données entraînement ML
        if operation in ["hit", "miss"] and key in self.metrics:
            metrics = self.metrics[key]
            features = [
                metrics.access_frequency,
                time.time() - metrics.last_access,
                metrics.size_bytes,
                metrics.computation_cost
            ]
            
            # Target: 1 pour hit, 0 pour miss
            target = 1.0 if operation == "hit" else 0.0
            
            self.pattern_features.append(features)
            self.pattern_targets.append(target)
            
            # Re-entraînement périodique
            if len(self.pattern_features) % 1000 == 0:
                await self._retrain_model()
    
    async def _retrain_model(self) -> None:
        """**ML Engineer**: Re-entraînement modèle avec nouvelles données"""
        try:
            if len(self.pattern_features) < 100:
                return
            
            # Préparation données
            features_scaled = self.scaler.fit_transform(self.pattern_features[-1000:])
            targets = self.pattern_targets[-1000:]
            
            # Re-entraînement
            self.ml_model.fit(features_scaled, targets)
            
            logger.info("🔄 Modèle ML cache re-entraîné")
            
        except Exception as e:
            logger.error(f"❌ Erreur re-entraînement ML: {e}")
    
    async def _serialize_value(self, value: Any) -> str:
        """**Backend Senior**: Sérialisation optimisée"""
        try:
            if isinstance(value, (str, int, float, bool)):
                return str(value)
            elif isinstance(value, bytes):
                return value.decode('utf-8')
            else:
                return json.dumps(value, ensure_ascii=False)
        except Exception:
            return str(value)
    
    async def _deserialize_value(self, serialized: str) -> Any:
        """**Backend Senior**: Désérialisation optimisée"""
        try:
            # Tentative parsing JSON
            return json.loads(serialized)
        except (json.JSONDecodeError, TypeError):
            # Retour string brute
            return serialized
    
    async def _store_cache_metadata(
        self, 
        redis_conn, 
        key -> None: str, 
        ttl -> None: int, 
        policy_name -> None: str,
        context -> None: Optional[Dict[str, Any]] = None
    ) -> None:
        """**DBA**: Stockage métadonnées cache pour analytics"""
        metadata = {
            "policy": policy_name,
            "ttl": ttl,
            "created_at": time.time(),
            "context": context or {}
        }
        
        metadata_key = f"meta:{key}"
        await redis_conn.setex(
            metadata_key, 
            ttl + 300,  # 5 minutes de plus que TTL principal
            json.dumps(metadata)
        )
    
    async def invalidate_cache(self, pattern -> None: str = None, keys -> None: List[str] = None) -> None:
        """**Backend Senior**: Invalidation cache intelligente"""
        try:
            async with self.redis_pool.get_connection() as redis_conn:
                if keys:
                    # Invalidation clés spécifiques
                    result = await redis_conn.delete(*keys)
                    
                    # Nettoyage L1
                    for key in keys:
                        self.l1_cache.pop(key, None)
                        
                    logger.info(f"🗑️ {result} clés invalidées")
                    
                elif pattern:
                    # Invalidation par pattern
                    keys_to_delete = []
                    async for key in redis_conn.scan_iter(match=pattern):
                        keys_to_delete.append(key)
                    
                    if keys_to_delete:
                        result = await redis_conn.delete(*keys_to_delete)
                        
                        # Nettoyage L1
                        for key in keys_to_delete:
                            self.l1_cache.pop(key, None)
                            
                        logger.info(f"🗑️ {result} clés invalidées (pattern: {pattern})")
                        
        except Exception as e:
            logger.error(f"❌ Erreur invalidation cache: {e}")
    
    async def get_cache_analytics(self) -> Dict[str, Any]:
        """**DevOps**: Analytics détaillées cache"""
        
        total_keys = len(self.metrics)
        total_hits = sum(m.hit_count for m in self.metrics.values())
        total_misses = sum(m.miss_count for m in self.metrics.values())
        hit_ratio = total_hits / (total_hits + total_misses) if (total_hits + total_misses) > 0 else 0
        
        # Top clés par fréquence
        top_keys = sorted(
            self.metrics.items(),
            key=lambda x: x[1].access_frequency,
            reverse=True
        )[:10]
        
        # Distribution TTL
        async with self.redis_pool.get_connection() as redis_conn:
            ttl_distribution = {}
            for key in list(self.metrics.keys())[:100]:  # Sample
                ttl = await redis_conn.ttl(key)
                ttl_bucket = f"{ttl//300*300}-{(ttl//300+1)*300}s"  # Buckets 5min
                ttl_distribution[ttl_bucket] = ttl_distribution.get(ttl_bucket, 0) + 1
        
        return {
            "global_metrics": {
                "total_keys": total_keys,
                "total_hits": total_hits,
                "total_misses": total_misses,
                "hit_ratio": round(hit_ratio, 3),
                "l1_cache_size": len(self.l1_cache),
                "l1_max_size": self.l1_max_size
            },
            "top_keys": [
                {
                    "key": key,
                    "hit_count": metrics.hit_count,
                    "miss_count": metrics.miss_count,
                    "access_frequency": round(metrics.access_frequency, 3),
                    "size_bytes": metrics.size_bytes
                }
                for key, metrics in top_keys
            ],
            "ttl_distribution": ttl_distribution,
            "policies": list(self.policies.keys()),
            "ml_model_active": self.ml_model is not None,
            "pattern_samples": len(self.pattern_features)
        }
    
    async def optimize_policies(self) -> None:
        """**Lead Dev IA**: Optimisation automatique politiques cache"""
        analytics = await self.get_cache_analytics()
        
        # Optimisations basées sur analytics
        hit_ratio = analytics["global_metrics"]["hit_ratio"]
        
        if hit_ratio < 0.7:  # Taux hit faible
            # Augmentation TTL adaptatif
            for policy in self.policies.values():
                if policy.policy_type == CachePolicy.ADAPTIVE:
                    if policy.ttl_seconds:
                        policy.ttl_seconds = int(policy.ttl_seconds * 1.2)
                        
            logger.info("📈 TTL augmentés pour améliorer hit ratio")
        
        elif hit_ratio > 0.95:  # Taux hit très élevé
            # Optimisation mémoire
            for policy in self.policies.values():
                if policy.max_size:
                    policy.max_size = int(policy.max_size * 0.9)
                    
            logger.info("💾 Taille cache réduite pour optimiser mémoire")

# Factory function
async def create_cache_policy_engine(redis_pool, config_path -> None: Optional[str] = None) -> None:
    """**Lead Dev IA**: Factory création moteur politiques cache"""
    engine = CachePolicyEngine(redis_pool, config_path)
    return engine

if __name__ == "__main__":
    async def demo() -> None:
        """Démonstration Cache Policy Engine"""
        
        # Configuration Redis (simulé)
        class MockRedisPool:
    """MockRedisPool: class implementation"""
            def get_connection(self) -> None:
                from unittest.mock import AsyncMock
                return AsyncMock()
        
        # Création engine
        engine = await create_cache_policy_engine(MockRedisPool())
        
        # Tests mise en cache
        await engine.set_cache("user:123", {"name": "John", "email": "john@example.com"})
        await engine.set_cache("media:456", {"url": "video.mp4", "size": 1024000}, "media_content")
        
        # Récupération
        user_data = await engine.get_cache("user:123")
        print(f"Données utilisateur: {user_data}")
        
        # Analytics
        analytics = await engine.get_cache_analytics()
        print(f"Analytics cache: {analytics}")
        
        # Optimisation
        await engine.optimize_policies()
    
    asyncio.run(demo())