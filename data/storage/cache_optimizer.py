"""
Cache Optimizer module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
⚠️ AVERTISSEMENT: Ce module fait partie du système propriétaire Ainflue
Toute reproduction, distribution ou modification non autorisée est strictement interdite.
© 2024 Ainflue - Tous droits réservés

Cache Optimizer - Enterprise Cache & CDN Management System
=========================================================

Professional cache optimization and CDN management for multi-format content.
Supports intelligent caching strategies, CDN distribution, and performance optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
"""

import asyncio
import logging
import json
import hashlib
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import tempfile
import aiofiles
import aiohttp
from concurrent.futures import ThreadPoolExecutor
import threading
from collections import defaultdict, OrderedDict
import weakref

try:
    import redis.asyncio as redis
    import memcache
    import aiomcache
    from pymongo import MongoClient
    import boto3
    from botocore.exceptions import ClientError
    import psutil
    import numpy as np
    from sklearn.preprocessing import MinMaxScaler
    from sklearn.cluster import KMeans
    import joblib
except ImportError as e:
    logging.warning(f"Dépendance optionnelle manquante: {e}")


class CacheLevel(Enum):
    """Niveaux de cache hiérarchique"""
    L1_MEMORY = "l1_memory"       # RAM locale
    L2_REDIS = "l2_redis"         # Redis distribué
    L3_SSD = "l3_ssd"            # Cache SSD local
    L4_CDN = "l4_cdn"            # CDN edge cache


class CacheStrategy(Enum):
    """Stratégies de cache"""
    LRU = "lru"                   # Least Recently Used
    LFU = "lfu"                   # Least Frequently Used
    FIFO = "fifo"                 # First In First Out
    TTL = "ttl"                   # Time To Live
    ADAPTIVE = "adaptive"         # ML-based adaptive
    PREDICTIVE = "predictive"     # Predictive preloading


class EvictionPolicy(Enum):
    """Politiques d'éviction"""
    SIZE_BASED = "size_based"
    TIME_BASED = "time_based"
    FREQUENCY_BASED = "frequency_based"
    PRIORITY_BASED = "priority_based"
    ML_OPTIMIZED = "ml_optimized"


class CacheHitRatio(Enum):
    """Classifications du hit ratio"""
    EXCELLENT = "excellent"       # >95%
    GOOD = "good"                # 85-95%
    ACCEPTABLE = "acceptable"     # 70-85%
    POOR = "poor"                # 50-70%
    CRITICAL = "critical"         # <50%


class CDNProvider(Enum):
    """Fournisseurs CDN supportés"""
    CLOUDFLARE = "cloudflare"
    FASTLY = "fastly"
    CLOUDFRONT = "cloudfront"
    AZURE_CDN = "azure_cdn"
    GOOGLE_CDN = "google_cdn"
    KEYCDN = "keycdn"


@dataclass
class CacheEntry:
    """Entrée de cache"""
    key: str
    data: bytes
    size: int
    created_at: datetime
    last_accessed: datetime
    access_count: int = 0
    ttl: Optional[int] = None  # secondes
    priority: int = 1
    tags: Set[str] = field(default_factory=set)
    compression_ratio: float = 0.0
    checksum: Optional[str] = None


@dataclass
class CacheMetrics:
    """Métriques de cache"""
    hit_count: int = 0
    miss_count: int = 0
    eviction_count: int = 0
    total_requests: int = 0
    total_size: int = 0
    average_latency: float = 0.0
    peak_memory_usage: int = 0
    compression_savings: int = 0


@dataclass
class CacheConfig:
    """Configuration de cache"""
    max_size: int = 1024 * 1024 * 1024  # 1GB
    max_entries: int = 100000
    default_ttl: int = 3600  # 1 heure
    strategy: CacheStrategy = CacheStrategy.ADAPTIVE
    eviction_policy: EvictionPolicy = EvictionPolicy.ML_OPTIMIZED
    compression_enabled: bool = True
    encryption_enabled: bool = False
    prefetch_enabled: bool = True
    analytics_enabled: bool = True


@dataclass
class CDNConfig:
    """Configuration CDN"""
    provider: CDNProvider
    zone_id: Optional[str] = None
    api_key: Optional[str] = None
    secret_key: Optional[str] = None
    edge_locations: List[str] = field(default_factory=list)
    cache_ttl: int = 86400  # 24 heures
    compression_enabled: bool = True
    security_headers: bool = True
    custom_rules: List[Dict] = field(default_factory=list)


class MemoryCache:
    """Cache mémoire L1 avec LRU optimisé"""
    
    def __init__(self, config -> None: CacheConfig) -> None:
        self.config = config
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.metrics = CacheMetrics()
        self._lock = threading.RLock()
        
        # Index pour recherche rapide
        self._tag_index: Dict[str, Set[str]] = defaultdict(set)
        self._size_index: Dict[int, Set[str]] = defaultdict(set)
    
    def get(self, key: str) -> Optional[bytes]:
        """Récupère une valeur du cache"""
        with self._lock:
            if key in self.cache:
                entry = self.cache[key]
                
                # Vérification TTL
                if entry.ttl and (datetime.now() - entry.created_at).total_seconds() > entry.ttl:
                    del self.cache[key]
                    self.metrics.miss_count += 1
                    return None
                
                # Mise à jour des statistiques d'accès
                entry.last_accessed = datetime.now()
                entry.access_count += 1
                
                # Déplacement en fin (LRU)
                self.cache.move_to_end(key)
                
                self.metrics.hit_count += 1
                self.metrics.total_requests += 1
                
                return entry.data
            
            self.metrics.miss_count += 1
            self.metrics.total_requests += 1
            return None
    
    def put(self, key: str, data: bytes, ttl: Optional[int] = None, 
            priority: int = 1, tags: Set[str] = None) -> bool:
        """Stocke une valeur dans le cache"""
        with self._lock:
            # Compression si activée
            compressed_data = data
            compression_ratio = 0.0
            
            if self.config.compression_enabled and len(data) > 1024:
                compressed_data = self._compress_data(data)
                compression_ratio = (len(data) - len(compressed_data)) / len(data) * 100
            
            # Calcul du checksum
            checksum = hashlib.sha256(data).hexdigest()
            
            entry = CacheEntry(
                key=key,
                data=compressed_data,
                size=len(compressed_data),
                created_at=datetime.now(),
                last_accessed=datetime.now(),
                ttl=ttl or self.config.default_ttl,
                priority=priority,
                tags=tags or set(),
                compression_ratio=compression_ratio,
                checksum=checksum
            )
            
            # Vérification de l'espace disponible
            if not self._has_space_for(entry):
                if not self._make_space_for(entry):
                    return False
            
            # Suppression de l'ancienne entrée si elle existe
            if key in self.cache:
                old_entry = self.cache[key]
                self._remove_from_indexes(key, old_entry)
                self.metrics.total_size -= old_entry.size
            
            # Ajout de la nouvelle entrée
            self.cache[key] = entry
            self._add_to_indexes(key, entry)
            self.metrics.total_size += entry.size
            
            return True
    
    def _has_space_for(self, entry: CacheEntry) -> bool:
        """Vérifie si il y a assez d'espace pour l'entrée"""
        return (
            len(self.cache) < self.config.max_entries and
            self.metrics.total_size + entry.size <= self.config.max_size
        )
    
    def _make_space_for(self, entry: CacheEntry) -> bool:
        """Libère de l'espace pour une nouvelle entrée"""
        space_needed = entry.size
        space_freed = 0
        
        if self.config.eviction_policy == EvictionPolicy.ML_OPTIMIZED:
            candidates = self._get_ml_eviction_candidates()
        else:
            candidates = self._get_standard_eviction_candidates()
        
        for key in candidates:
            if key in self.cache:
                old_entry = self.cache[key]
                space_freed += old_entry.size
                
                del self.cache[key]
                self._remove_from_indexes(key, old_entry)
                self.metrics.total_size -= old_entry.size
                self.metrics.eviction_count += 1
                
                if space_freed >= space_needed:
                    break
        
        return space_freed >= space_needed
    
    def _get_ml_eviction_candidates(self) -> List[str]:
        """Obtient les candidats à l'éviction via ML"""
        if not self.cache:
            return []
        
        # Calcul des scores d'éviction basés sur plusieurs facteurs
        candidates = []
        current_time = datetime.now()
        
        for key, entry in self.cache.items():
            # Facteurs pour le score d'éviction
            time_since_access = (current_time - entry.last_accessed).total_seconds()
            time_since_creation = (current_time - entry.created_at).total_seconds()
            
            # Score composite (plus élevé = plus probable d'être évincé)
            score = (
                time_since_access * 0.4 +           # Temps depuis dernier accès
                time_since_creation * 0.2 +         # Âge de l'entrée
                (1.0 / max(entry.access_count, 1)) * 0.3 +  # Fréquence d'accès inverse
                entry.size / 1024 * 0.1             # Taille normalisée
            ) / max(entry.priority, 1)              # Divisé par priorité
            
            candidates.append((score, key))
        
        # Tri par score décroissant
        candidates.sort(reverse=True)
        return [key for _, key in candidates]
    
    def _get_standard_eviction_candidates(self) -> List[str]:
        """Obtient les candidats à l'éviction standard (LRU)"""
        # Retourne les clés dans l'ordre LRU
        return list(self.cache.keys())
    
    def _add_to_indexes(self, key -> None: str, entry -> None: CacheEntry) -> None:
        """Ajoute aux index de recherche"""
        for tag in entry.tags:
            self._tag_index[tag].add(key)
        
        size_bucket = entry.size // 1024  # Buckets de 1KB
        self._size_index[size_bucket].add(key)
    
    def _remove_from_indexes(self, key -> None: str, entry -> None: CacheEntry) -> None:
        """Supprime des index de recherche"""
        for tag in entry.tags:
            self._tag_index[tag].discard(key)
            if not self._tag_index[tag]:
                del self._tag_index[tag]
        
        size_bucket = entry.size // 1024
        self._size_index[size_bucket].discard(key)
        if not self._size_index[size_bucket]:
            del self._size_index[size_bucket]
    
    def _compress_data(self, data: bytes) -> bytes:
        """Compresse les données"""
        import gzip
        return gzip.compress(data)
    
    def _decompress_data(self, data: bytes) -> bytes:
        """Décompresse les données"""
        import gzip
        return gzip.decompress(data)
    
    def invalidate_by_tags(self, tags: Set[str]) -> int:
        """Invalide les entrées par tags"""
        with self._lock:
            keys_to_remove = set()
            
            for tag in tags:
                if tag in self._tag_index:
                    keys_to_remove.update(self._tag_index[tag])
            
            for key in keys_to_remove:
                if key in self.cache:
                    entry = self.cache[key]
                    del self.cache[key]
                    self._remove_from_indexes(key, entry)
                    self.metrics.total_size -= entry.size
            
            return len(keys_to_remove)
    
    def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques du cache"""
        with self._lock:
            hit_ratio = (
                self.metrics.hit_count / max(self.metrics.total_requests, 1) * 100
            )
            
            return {
                'entries_count': len(self.cache),
                'total_size': self.metrics.total_size,
                'hit_count': self.metrics.hit_count,
                'miss_count': self.metrics.miss_count,
                'hit_ratio': hit_ratio,
                'eviction_count': self.metrics.eviction_count,
                'memory_usage_percent': (self.metrics.total_size / self.config.max_size) * 100,
                'compression_savings': self.metrics.compression_savings
            }


class RedisCache:
    """Cache Redis L2 distribué"""
    
    def __init__(self, config -> None: CacheConfig, redis_url -> None: str = "redis -> None://localhost -> None:6379") -> None:
        self.config = config
        self.redis_url = redis_url
        self.redis_client: Optional[redis.Redis] = None
        self.metrics = CacheMetrics()
        
    async def connect(self) -> None:
        """Connexion à Redis"""
        try:
            self.redis_client = redis.from_url(self.redis_url)
            await self.redis_client.ping()
            logging.info("Connexion Redis établie")
        except Exception as e:
            logging.error(f"Erreur connexion Redis: {e}")
            raise
    
    async def get(self, key: str) -> Optional[bytes]:
        """Récupère une valeur de Redis"""
        if not self.redis_client:
            await self.connect()
        
        try:
            start_time = time.time()
            data = await self.redis_client.get(key)
            latency = time.time() - start_time
            
            if data:
                self.metrics.hit_count += 1
                self.metrics.average_latency = (
                    (self.metrics.average_latency * self.metrics.hit_count + latency) /
                    (self.metrics.hit_count + 1)
                )
                return data
            else:
                self.metrics.miss_count += 1
                return None
                
        except Exception as e:
            logging.error(f"Erreur Redis GET {key}: {e}")
            self.metrics.miss_count += 1
            return None
    
    async def put(self, key: str, data: bytes, ttl: Optional[int] = None) -> bool:
        """Stocke une valeur dans Redis"""
        if not self.redis_client:
            await self.connect()
        
        try:
            expire_time = ttl or self.config.default_ttl
            await self.redis_client.setex(key, expire_time, data)
            return True
        except Exception as e:
            logging.error(f"Erreur Redis SET {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Supprime une clé de Redis"""
        if not self.redis_client:
            await self.connect()
        
        try:
            result = await self.redis_client.delete(key)
            return result > 0
        except Exception as e:
            logging.error(f"Erreur Redis DELETE {key}: {e}")
            return False
    
    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalide les clés matchant un pattern"""
        if not self.redis_client:
            await self.connect()
        
        try:
            keys = await self.redis_client.keys(pattern)
            if keys:
                deleted = await self.redis_client.delete(*keys)
                return deleted
            return 0
        except Exception as e:
            logging.error(f"Erreur Redis invalidation pattern {pattern}: {e}")
            return 0


class CDNManager:
    """Gestionnaire CDN L4"""
    
    def __init__(self, config -> None: CDNConfig) -> None:
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self) -> None:
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.session:
            await self.session.close()
    
    async def purge_cache(self, urls: List[str]) -> bool:
        """Purge le cache CDN pour des URLs"""
        try:
            if self.config.provider == CDNProvider.CLOUDFLARE:
                return await self._purge_cloudflare(urls)
            elif self.config.provider == CDNProvider.FASTLY:
                return await self._purge_fastly(urls)
            elif self.config.provider == CDNProvider.CLOUDFRONT:
                return await self._purge_cloudfront(urls)
            else:
                logging.warning(f"Provider CDN non supporté: {self.config.provider}")
                return False
        except Exception as e:
            logging.error(f"Erreur purge CDN: {e}")
            return False
    
    async def _purge_cloudflare(self, urls: List[str]) -> bool:
        """Purge Cloudflare"""
        if not self.session:
            return False
        
        headers = {
            'Authorization': f'Bearer {self.config.api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'files': urls
        }
        
        url = f"https://api.cloudflare.com/client/v4/zones/{self.config.zone_id}/purge_cache"
        
        async with self.session.post(url, headers=headers, json=payload) as response:
            return response.status == 200
    
    async def _purge_fastly(self, urls: List[str]) -> bool:
        """Purge Fastly"""
        if not self.session:
            return False
        
        headers = {
            'Fastly-Token': self.config.api_key,
            'Content-Type': 'application/json'
        }
        
        success_count = 0
        for url in urls:
            async with self.session.post(
                f"https://api.fastly.com/purge/{url}",
                headers=headers
            ) as response:
                if response.status == 200:
                    success_count += 1
        
        return success_count == len(urls)
    
    async def _purge_cloudfront(self, urls: List[str]) -> bool:
        """Purge CloudFront"""
        try:
            import boto3
            
            client = boto3.client('cloudfront')
            
            response = client.create_invalidation(
                DistributionId=self.config.zone_id,
                InvalidationBatch={
                    'Paths': {
                        'Quantity': len(urls),
                        'Items': urls
                    },
                    'CallerReference': f"cache_purge_{int(time.time())}"
                }
            )
            
            return response['ResponseMetadata']['HTTPStatusCode'] == 201
            
        except Exception as e:
            logging.error(f"Erreur purge CloudFront: {e}")
            return False
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Obtient les statistiques CDN"""
        try:
            if self.config.provider == CDNProvider.CLOUDFLARE:
                return await self._get_cloudflare_stats()
            else:
                return {'provider': self.config.provider.value, 'stats': 'not_implemented'}
        except Exception as e:
            logging.error(f"Erreur stats CDN: {e}")
            return {}
    
    async def _get_cloudflare_stats(self) -> Dict[str, Any]:
        """Statistiques Cloudflare"""
        if not self.session:
            return {}
        
        headers = {
            'Authorization': f'Bearer {self.config.api_key}',
            'Content-Type': 'application/json'
        }
        
        # Analytics des dernières 24h
        end_time = datetime.now()
        start_time = end_time - timedelta(days=1)
        
        params = {
            'since': start_time.isoformat(),
            'until': end_time.isoformat(),
            'continuous': 'true'
        }
        
        url = f"https://api.cloudflare.com/client/v4/zones/{self.config.zone_id}/analytics/dashboard"
        
        try:
            async with self.session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('result', {})
                return {}
        except Exception:
            return {}


class PredictiveEngine:
    """Moteur de prédiction pour le preloading"""
    
    def __init__(self) -> None:
        self.access_patterns: Dict[str, List[Tuple[datetime, str]]] = defaultdict(list)
        self.model = None
        self.scaler = MinMaxScaler()
        self._lock = threading.Lock()
        
    def record_access(self, user_id -> None: str, resource_key -> None: str) -> None:
        """Enregistre un accès pour l'analyse"""
        with self._lock:
            self.access_patterns[user_id].append((datetime.now(), resource_key))
            
            # Limitation de l'historique
            if len(self.access_patterns[user_id]) > 1000:
                self.access_patterns[user_id] = self.access_patterns[user_id][-1000:]
    
    def train_model(self) -> bool:
        """Entraîne le modèle de prédiction"""
        try:
            # Extraction des features temporelles
            features = []
            labels = []
            
            for user_id, accesses in self.access_patterns.items():
                if len(accesses) < 5:  # Pas assez de données
                    continue
                
                for i in range(len(accesses) - 1):
                    current_time, current_resource = accesses[i]
                    next_time, next_resource = accesses[i + 1]
                    
                    # Features: heure, jour semaine, intervalle depuis dernier accès
                    hour = current_time.hour
                    weekday = current_time.weekday()
                    
                    # Intervalle en minutes
                    if i > 0:
                        prev_time = accesses[i - 1][0]
                        interval = (current_time - prev_time).total_seconds() / 60
                    else:
                        interval = 0
                    
                    features.append([hour, weekday, interval])
                    labels.append(hash(next_resource) % 1000)  # Simplification
            
            if len(features) < 50:  # Pas assez de données pour l'entraînement
                return False
            
            # Normalisation et entraînement
            features_scaled = self.scaler.fit_transform(features)
            
            from sklearn.ensemble import RandomForestClassifier
            self.model = RandomForestClassifier(n_estimators=100, random_state=42)
            self.model.fit(features_scaled, labels)
            
            logging.info(f"Modèle de prédiction entraîné avec {len(features)} échantillons")
            return True
            
        except Exception as e:
            logging.error(f"Erreur entraînement modèle prédictif: {e}")
            return False
    
    def predict_next_resources(self, user_id: str, num_predictions: int = 5) -> List[str]:
        """Prédit les prochaines ressources à accéder"""
        if not self.model or user_id not in self.access_patterns:
            return []
        
        try:
            accesses = self.access_patterns[user_id]
            if len(accesses) < 2:
                return []
            
            # Préparation des features pour la prédiction
            current_time = datetime.now()
            last_access_time = accesses[-1][0]
            
            hour = current_time.hour
            weekday = current_time.weekday()
            interval = (current_time - last_access_time).total_seconds() / 60
            
            features = self.scaler.transform([[hour, weekday, interval]])
            
            # Prédiction avec probabilités
            probabilities = self.model.predict_proba(features)[0]
            
            # Sélection des top prédictions
            top_indices = np.argsort(probabilities)[-num_predictions:][::-1]
            
            # Conversion en clés de ressources (simplifiée)
            predictions = [f"resource_{idx}" for idx in top_indices]
            
            return predictions
            
        except Exception as e:
            logging.error(f"Erreur prédiction ressources: {e}")
            return []


class CacheOptimizer:
    """
    Optimiseur de cache enterprise avec IA
    
    Features:
    - Cache hiérarchique multi-niveau (L1-L4)
    - Stratégies adaptatives basées sur ML
    - Prédiction et preloading intelligent
    - Gestion CDN automatisée
    - Optimisation en temps réel
    - Analytics et monitoring avancé
    """
    
    def __init__(self, 
                 cache_config -> None: CacheConfig,
                 cdn_config -> None: Optional[CDNConfig] = None,
                 redis_url -> None: str = "redis -> None://localhost -> None:6379") -> None:
        
        self.logger = logging.getLogger(__name__)
        self.cache_config = cache_config
        self.cdn_config = cdn_config
        
        # Caches hiérarchiques
        self.l1_cache = MemoryCache(cache_config)
        self.l2_cache = RedisCache(cache_config, redis_url)
        self.l3_cache: Optional[Any] = None  # SSD cache (à implémenter)
        self.cdn_manager = CDNManager(cdn_config) if cdn_config else None
        
        # Moteur prédictif
        self.predictive_engine = PredictiveEngine()
        
        # Métriques globales
        self.global_metrics = {
            'total_requests': 0,
            'l1_hits': 0,
            'l2_hits': 0,
            'l3_hits': 0,
            'cdn_hits': 0,
            'misses': 0,
            'preload_success': 0
        }
        
        # Thread pool pour opérations asynchrones
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Tâches de maintenance
        self._maintenance_task: Optional[asyncio.Task] = None
        self._prediction_task: Optional[asyncio.Task] = None
        
    async def get(self, key: str, user_id: Optional[str] = None) -> Optional[bytes]:
        """
        Récupère une valeur du cache hiérarchique
        
        Args:
            key: Clé de cache
            user_id: ID utilisateur pour analytics prédictifs
            
        Returns:
            Données mises en cache ou None
        """
        
        self.global_metrics['total_requests'] += 1
        
        # Enregistrement de l'accès pour prédiction
        if user_id:
            self.predictive_engine.record_access(user_id, key)
        
        # L1: Cache mémoire
        data = self.l1_cache.get(key)
        if data:
            self.global_metrics['l1_hits'] += 1
            self.logger.debug(f"Cache L1 hit: {key}")
            
            # Déclenchement du preloading prédictif
            if user_id and self.cache_config.prefetch_enabled:
                asyncio.create_task(self._predictive_preload(user_id))
            
            return data
        
        # L2: Redis cache
        data = await self.l2_cache.get(key)
        if data:
            self.global_metrics['l2_hits'] += 1
            self.logger.debug(f"Cache L2 hit: {key}")
            
            # Promotion vers L1
            asyncio.create_task(self._promote_to_l1(key, data))
            return data
        
        # L3: SSD cache (si disponible)
        if self.l3_cache:
            data = await self._get_from_l3(key)
            if data:
                self.global_metrics['l3_hits'] += 1
                self.logger.debug(f"Cache L3 hit: {key}")
                
                # Promotion vers L2 et L1
                asyncio.create_task(self._promote_to_l2(key, data))
                asyncio.create_task(self._promote_to_l1(key, data))
                return data
        
        # CDN: Cache edge
        if self.cdn_manager:
            data = await self._get_from_cdn(key)
            if data:
                self.global_metrics['cdn_hits'] += 1
                self.logger.debug(f"CDN hit: {key}")
                
                # Promotion vers tous les niveaux inférieurs
                asyncio.create_task(self._promote_to_all_levels(key, data))
                return data
        
        # Miss complet
        self.global_metrics['misses'] += 1
        self.logger.debug(f"Cache miss: {key}")
        return None
    
    async def put(self, key: str, data: bytes, 
                  ttl: Optional[int] = None,
                  priority: int = 1,
                  tags: Set[str] = None,
                  levels: List[CacheLevel] = None) -> bool:
        """
        Stocke une valeur dans le cache hiérarchique
        
        Args:
            key: Clé de cache
            data: Données à mettre en cache
            ttl: Durée de vie en secondes
            priority: Priorité (1-10)
            tags: Tags pour invalidation groupée
            levels: Niveaux de cache à utiliser
            
        Returns:
            True si stockage réussi
        """
        
        if not levels:
            levels = [CacheLevel.L1_MEMORY, CacheLevel.L2_REDIS]
        
        success = True
        
        # Stockage dans les niveaux spécifiés
        if CacheLevel.L1_MEMORY in levels:
            l1_success = self.l1_cache.put(key, data, ttl, priority, tags)
            success = success and l1_success
        
        if CacheLevel.L2_REDIS in levels:
            l2_success = await self.l2_cache.put(key, data, ttl)
            success = success and l2_success
        
        if CacheLevel.L3_SSD in levels and self.l3_cache:
            l3_success = await self._put_to_l3(key, data, ttl)
            success = success and l3_success
        
        if CacheLevel.L4_CDN in levels and self.cdn_manager:
            # Pour CDN, on doit souvent passer par un storage intermédiaire
            cdn_success = await self._put_to_cdn(key, data)
            success = success and cdn_success
        
        return success
    
    async def invalidate(self, key: str, levels: List[CacheLevel] = None) -> bool:
        """Invalide une clé dans les niveaux spécifiés"""
        
        if not levels:
            levels = list(CacheLevel)
        
        success = True
        
        if CacheLevel.L1_MEMORY in levels:
            self.l1_cache.cache.pop(key, None)
        
        if CacheLevel.L2_REDIS in levels:
            l2_success = await self.l2_cache.delete(key)
            success = success and l2_success
        
        if CacheLevel.L3_SSD in levels and self.l3_cache:
            l3_success = await self._delete_from_l3(key)
            success = success and l3_success
        
        if CacheLevel.L4_CDN in levels and self.cdn_manager:
            cdn_success = await self.cdn_manager.purge_cache([key])
            success = success and cdn_success
        
        return success
    
    async def invalidate_by_tags(self, tags: Set[str]) -> int:
        """Invalide les entrées par tags"""
        
        # L1 cache
        l1_count = self.l1_cache.invalidate_by_tags(tags)
        
        # L2 cache (Redis) - invalidation par pattern
        l2_count = 0
        for tag in tags:
            pattern = f"*{tag}*"
            l2_count += await self.l2_cache.invalidate_pattern(pattern)
        
        return l1_count + l2_count
    
    async def _promote_to_l1(self, key -> None: str, data -> None: bytes) -> None:
        """Promotion vers cache L1"""
        self.l1_cache.put(key, data)
    
    async def _promote_to_l2(self, key -> None: str, data -> None: bytes) -> None:
        """Promotion vers cache L2"""
        await self.l2_cache.put(key, data)
    
    async def _promote_to_all_levels(self, key -> None: str, data -> None: bytes) -> None:
        """Promotion vers tous les niveaux inférieurs"""
        await self._promote_to_l1(key, data)
        await self._promote_to_l2(key, data)
        if self.l3_cache:
            await self._put_to_l3(key, data)
    
    async def _get_from_l3(self, key: str) -> Optional[bytes]:
        """Récupération depuis cache L3 (SSD)"""
        # Implémentation simplifiée - en production: cache SSD optimisé
        return None
    
    async def _put_to_l3(self, key: str, data: bytes, ttl: Optional[int] = None) -> bool:
        """Stockage vers cache L3 (SSD)"""
        # Implémentation simplifiée
        return True
    
    async def _delete_from_l3(self, key: str) -> bool:
        """Suppression du cache L3"""
        # Implémentation simplifiée
        return True
    
    async def _get_from_cdn(self, key: str) -> Optional[bytes]:
        """Récupération depuis CDN"""
        # En pratique, le CDN gère ses propres caches
        # Ici on simule une vérification de disponibilité
        return None
    
    async def _put_to_cdn(self, key: str, data: bytes) -> bool:
        """Upload vers CDN"""
        # Simulation d'upload vers CDN
        return True
    
    async def _predictive_preload(self, user_id -> None: str) -> None:
        """Preloading prédictif basé sur ML"""
        
        try:
            predictions = self.predictive_engine.predict_next_resources(user_id, 3)
            
            for predicted_key in predictions:
                # Vérification si déjà en cache
                if self.l1_cache.get(predicted_key):
                    continue
                
                # Simulation de chargement prédictif
                # En production: récupération depuis source de données
                predicted_data = f"predicted_data_for_{predicted_key}".encode()
                
                # Stockage avec priorité plus faible
                success = await self.put(
                    predicted_key, 
                    predicted_data, 
                    priority=5,  # Priorité moyenne
                    levels=[CacheLevel.L1_MEMORY]
                )
                
                if success:
                    self.global_metrics['preload_success'] += 1
                    self.logger.debug(f"Preload réussi: {predicted_key}")
                    
        except Exception as e:
            self.logger.error(f"Erreur preloading prédictif: {e}")
    
    async def optimize_cache_strategy(self) -> Dict[str, Any]:
        """Optimise la stratégie de cache basée sur les métriques"""
        
        stats = self.get_comprehensive_stats()
        
        recommendations = {
            'current_performance': {},
            'recommendations': [],
            'optimizations_applied': []
        }
        
        # Analyse du hit ratio global
        total_hits = (stats['l1_hits'] + stats['l2_hits'] + 
                     stats['l3_hits'] + stats['cdn_hits'])
        total_requests = stats['total_requests']
        
        if total_requests > 0:
            hit_ratio = total_hits / total_requests * 100
            recommendations['current_performance']['global_hit_ratio'] = hit_ratio
            
            if hit_ratio < 70:
                recommendations['recommendations'].append({
                    'type': 'increase_cache_size',
                    'priority': 'high',
                    'description': 'Hit ratio faible, augmenter la taille du cache'
                })
            
            # Analyse de la distribution des hits
            l1_ratio = stats['l1_hits'] / max(total_hits, 1) * 100
            
            if l1_ratio < 60:  # Moins de 60% des hits en L1
                recommendations['recommendations'].append({
                    'type': 'optimize_l1_strategy',
                    'priority': 'medium',
                    'description': 'Optimiser la stratégie L1 pour plus de hits locaux'
                })
                
                # Ajustement automatique de la taille L1
                if hasattr(self.cache_config, 'max_size'):
                    new_size = int(self.cache_config.max_size * 1.2)
                    self.cache_config.max_size = new_size
                    recommendations['optimizations_applied'].append(
                        f"Taille cache L1 augmentée à {new_size // (1024*1024)}MB"
                    )
        
        # Optimisation prédictive
        if self.cache_config.prefetch_enabled:
            preload_success_rate = (
                self.global_metrics['preload_success'] / 
                max(self.global_metrics['total_requests'], 1) * 100
            )
            
            if preload_success_rate > 10:  # Plus de 10% de preload réussi
                recommendations['recommendations'].append({
                    'type': 'increase_prefetch_aggressiveness',
                    'priority': 'low',
                    'description': 'Preloading efficace, augmenter agressivité'
                })
        
        return recommendations
    
    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """Retourne des statistiques complètes"""
        
        l1_stats = self.l1_cache.get_stats()
        
        stats = {
            # Métriques globales
            'total_requests': self.global_metrics['total_requests'],
            'l1_hits': self.global_metrics['l1_hits'],
            'l2_hits': self.global_metrics['l2_hits'],
            'l3_hits': self.global_metrics['l3_hits'],
            'cdn_hits': self.global_metrics['cdn_hits'],
            'misses': self.global_metrics['misses'],
            'preload_success': self.global_metrics['preload_success'],
            
            # Statistiques L1
            'l1_cache': l1_stats,
            
            # Statistiques L2
            'l2_cache': {
                'hit_count': self.l2_cache.metrics.hit_count,
                'miss_count': self.l2_cache.metrics.miss_count,
                'average_latency': self.l2_cache.metrics.average_latency
            },
            
            # Performance système
            'system': {
                'memory_usage': psutil.virtual_memory().percent,
                'cpu_usage': psutil.cpu_percent(),
                'disk_io': dict(psutil.disk_io_counters()._asdict()) if psutil.disk_io_counters() else {}
            }
        }
        
        # Calculs de ratios
        if stats['total_requests'] > 0:
            total_hits = (stats['l1_hits'] + stats['l2_hits'] + 
                         stats['l3_hits'] + stats['cdn_hits'])
            
            stats['global_hit_ratio'] = total_hits / stats['total_requests'] * 100
            stats['miss_ratio'] = stats['misses'] / stats['total_requests'] * 100
            stats['l1_hit_ratio'] = stats['l1_hits'] / stats['total_requests'] * 100
            stats['l2_hit_ratio'] = stats['l2_hits'] / stats['total_requests'] * 100
        
        return stats
    
    async def start_maintenance_tasks(self) -> None:
        """Démarre les tâches de maintenance"""
        
        self._maintenance_task = asyncio.create_task(self._maintenance_loop())
        self._prediction_task = asyncio.create_task(self._prediction_training_loop())
        
        self.logger.info("Tâches de maintenance démarrées")
    
    async def stop_maintenance_tasks(self) -> None:
        """Arrête les tâches de maintenance"""
        
        if self._maintenance_task:
            self._maintenance_task.cancel()
            try:
                await self._maintenance_task
            except asyncio.CancelledError:
                pass
        
        if self._prediction_task:
            self._prediction_task.cancel()
            try:
                await self._prediction_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("Tâches de maintenance arrêtées")
    
    async def _maintenance_loop(self) -> None:
        """Boucle de maintenance périodique"""
        
        while True:
            try:
                await asyncio.sleep(300)  # 5 minutes
                
                # Optimisation automatique
                await self.optimize_cache_strategy()
                
                # Nettoyage des entrées expirées
                await self._cleanup_expired_entries()
                
                # Statistiques de performance
                stats = self.get_comprehensive_stats()
                self.logger.info(f"Cache stats: Hit ratio global {stats.get('global_hit_ratio', 0):.1f}%")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Erreur maintenance cache: {e}")
    
    async def _prediction_training_loop(self) -> None:
        """Boucle d'entraînement du modèle prédictif"""
        
        while True:
            try:
                await asyncio.sleep(3600)  # 1 heure
                
                # Entraînement du modèle prédictif
                success = self.predictive_engine.train_model()
                if success:
                    self.logger.info("Modèle prédictif mis à jour")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Erreur entraînement prédictif: {e}")
    
    async def _cleanup_expired_entries(self) -> None:
        """Nettoie les entrées expirées"""
        
        # Nettoyage L1 (géré automatiquement par get())
        # Nettoyage L2 géré par Redis TTL
        # Nettoyage L3 si implémenté
        
        pass
    
    async def __aenter__(self) -> None:
        """Context manager entry"""
        if self.cdn_manager:
            await self.cdn_manager.__aenter__()
        await self.l2_cache.connect()
        await self.start_maintenance_tasks()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit"""
        await self.stop_maintenance_tasks()
        if self.cdn_manager:
            await self.cdn_manager.__aexit__(exc_type, exc_val, exc_tb)
        self.executor.shutdown(wait=True)


# Instance globale pour utilisation dans l'application
cache_optimizer: Optional[CacheOptimizer] = None


async def initialize_cache_optimizer(
    cache_config: Optional[CacheConfig] = None,
    cdn_config: Optional[CDNConfig] = None,
    redis_url: str = "redis://localhost:6379"
) -> CacheOptimizer:
    """
    Initialise l'optimiseur de cache global
    
    Args:
        cache_config: Configuration cache
        cdn_config: Configuration CDN
        redis_url: URL Redis
        
    Returns:
        Instance CacheOptimizer
    """
    
    global cache_optimizer
    
    if not cache_config:
        cache_config = CacheConfig()
    
    cache_optimizer = CacheOptimizer(cache_config, cdn_config, redis_url)
    await cache_optimizer.__aenter__()
    
    return cache_optimizer


async def get_cache_optimizer() -> Optional[CacheOptimizer]:
    """Retourne l'instance globale du cache optimizer"""
    return cache_optimizer


async def cache_get(key: str, user_id: Optional[str] = None) -> Optional[bytes]:
    """Interface simplifiée pour récupération cache"""
    if cache_optimizer:
        return await cache_optimizer.get(key, user_id)
    return None


async def cache_put(key: str, data: bytes, ttl: Optional[int] = None) -> bool:
    """Interface simplifiée pour stockage cache"""
    if cache_optimizer:
        return await cache_optimizer.put(key, data, ttl)
    return False


if __name__ == "__main__":
    # Test de l'optimiseur de cache
    import sys
    
    async def test_cache_optimizer() -> None:
        print("Test Cache Optimizer Ainflue")
        
        # Configuration de test
        cache_config = CacheConfig(
            max_size=50 * 1024 * 1024,  # 50MB
            strategy=CacheStrategy.ADAPTIVE,
            prefetch_enabled=True
        )
        
        # Initialisation
        optimizer = await initialize_cache_optimizer(cache_config)
        
        try:
            # Test de base
            test_data = b"Hello Ainflue Cache System!"
            
            # Stockage
            success = await optimizer.put("test_key", test_data)
            print(f"Stockage: {'Réussi' if success else 'Échec'}")
            
            # Récupération
            retrieved = await optimizer.get("test_key", "user_123")
            print(f"Récupération: {'Réussi' if retrieved == test_data else 'Échec'}")
            
            # Test prédictif
            for i in range(10):
                await optimizer.get(f"resource_{i}", "user_123")
                await asyncio.sleep(0.1)
            
            # Attente pour permettre la prédiction
            await asyncio.sleep(2)
            
            # Statistiques
            stats = optimizer.get_comprehensive_stats()
            print(f"\nStatistiques:")
            print(f"- Requêtes totales: {stats['total_requests']}")
            print(f"- Hit ratio global: {stats.get('global_hit_ratio', 0):.1f}%")
            print(f"- Hits L1: {stats['l1_hits']}")
            print(f"- Hits L2: {stats['l2_hits']}")
            print(f"- Preload réussi: {stats['preload_success']}")
            
            # Test d'optimisation
            optimization = await optimizer.optimize_cache_strategy()
            print(f"\nOptimisations: {len(optimization['recommendations'])} recommandations")
            
        finally:
            await optimizer.__aexit__(None, None, None)
    
    asyncio.run(test_cache_optimizer())
