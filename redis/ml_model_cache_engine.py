#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 ML Model Cache Engine - Intelligence Cache Modèles IA
========================================================

Moteur de cache spécialisé pour modèles ML avec optimisation des inférences,
gestion des versions et distribution intelligente des modèles.

**Rôles Experts:**
- **ML Engineer**: Optimisation cache modèles et inférences IA
- **Lead Dev IA**: Orchestration intelligente modèles multi-providers
- **Backend Senior**: Architecture cache haute performance ML
- **DevOps**: Monitoring performance et déploiement modèles

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import time
import hashlib
import pickle
import json
import gzip
from typing import Dict, Any, Optional, List, Union, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import numpy as np
import aioredis
from collections import defaultdict, deque
import torch
import joblib
from sklearn.base import BaseEstimator
import tensorflow as tf

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelType(Enum):
    """Types de modèles ML supportés"""
    SKLEARN = "sklearn"
    PYTORCH = "pytorch"
    TENSORFLOW = "tensorflow"
    HUGGINGFACE = "huggingface"
    CUSTOM = "custom"
    ONNX = "onnx"

class CacheStrategy(Enum):
    """Stratégies de cache modèles"""
    MEMORY_ONLY = "memory_only"  # Cache mémoire uniquement
    REDIS_ONLY = "redis_only"  # Cache Redis uniquement
    HYBRID = "hybrid"  # Mémoire + Redis
    PERSISTENT = "persistent"  # Avec persistance disque
    DISTRIBUTED = "distributed"  # Cache distribué

class ModelStatus(Enum):
    """Status des modèles en cache"""
    LOADING = "loading"
    READY = "ready"
    UPDATING = "updating"
    ERROR = "error"
    EXPIRED = "expired"

@dataclass
class ModelMetadata:
    """Métadonnées modèle ML"""
    model_id: str
    model_type: ModelType
    version: str
    framework_version: str
    size_bytes: int
    input_shape: Optional[Tuple] = None
    output_shape: Optional[Tuple] = None
    preprocessing_steps: List[str] = field(default_factory=list)
    postprocessing_steps: List[str] = field(default_factory=list)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    last_used: float = field(default_factory=time.time)
    usage_count: int = 0
    average_inference_time: float = 0.0

@dataclass
class CacheEntry:
    """Entrée cache modèle"""
    model_id: str
    model_data: Any  # Modèle sérialisé
    metadata: ModelMetadata
    status: ModelStatus = ModelStatus.READY
    cached_at: float = field(default_factory=time.time)
    access_count: int = 0
    last_access: float = field(default_factory=time.time)
    ttl: Optional[int] = None
    cache_key: str = ""

@dataclass
class InferenceCache:
    """Cache résultats d'inférence"""
    input_hash: str
    model_id: str
    model_version: str
    result: Any
    confidence: Optional[float] = None
    inference_time: float = 0.0
    cached_at: float = field(default_factory=time.time)
    access_count: int = 0

class MLModelCacheEngine:
    """
    🤖 Moteur de Cache Modèles ML Enterprise
    
    **ML Engineer:**
    - Cache intelligent modèles ML avec optimisation automatique
    - Gestion versions et compatibility checking avancé
    - Cache inférences avec invalidation intelligente
    - Optimisation mémoire spécialisée pour ML workloads
    
    **Lead Dev IA:**
    - Orchestration multi-providers (OpenAI, HuggingFace, Custom)
    - Load balancing modèles et distribution intelligente
    - Fallback automatique et modèles de secours
    - Monitoring performance IA temps réel
    
    **Backend Senior:**
    - Architecture cache haute performance pour ML
    - Sérialisation optimisée modèles lourds
    - Compression et streaming modèles volumineux
    - Gestion mémoire spécialisée tensors et matrices
    
    **DevOps:**
    - Monitoring déploiement et performance modèles
    - Pipeline CI/CD modèles avec A/B testing
    - Métriques business et technique détaillées
    - Alertes proactives dégradation modèles
    """
    
    def __init__(self, redis_pool, config: Optional[Dict[str, Any]] = None):
        self.redis_pool = redis_pool
        self.config = config or {}
        
        # Configuration cache
        self.cache_strategy = CacheStrategy(self.config.get('cache_strategy', 'hybrid'))
        self.max_memory_models = self.config.get('max_memory_models', 10)
        self.max_model_size_mb = self.config.get('max_model_size_mb', 500)
        self.inference_cache_ttl = self.config.get('inference_cache_ttl', 3600)
        self.model_cache_ttl = self.config.get('model_cache_ttl', 86400)
        
        # Cache mémoire local (L1)
        self.memory_cache: Dict[str, CacheEntry] = {}
        self.inference_cache: Dict[str, InferenceCache] = {}
        
        # Métadonnées et monitoring
        self.model_registry: Dict[str, ModelMetadata] = {}
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "loads": 0,
            "inference_cache_hits": 0,
            "inference_cache_misses": 0
        }
        
        # Queue chargement asynchrone
        self.loading_queue: deque = deque()
        self.loading_in_progress: Set[str] = set()
        
        # Monitoring performance
        self.performance_metrics: deque = deque(maxlen=1000)
        
        # Tâches background
        asyncio.create_task(self._background_loader())
        asyncio.create_task(self._cache_maintenance_loop())
        asyncio.create_task(self._performance_monitoring_loop())
        
        logger.info(f"🤖 ML Model Cache Engine initialisé (stratégie: {self.cache_strategy.value})")
    
    async def register_model(
        self,
        model_id: str,
        model_type: ModelType,
        version: str,
        model_path_or_data: Union[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """**ML Engineer**: Enregistrement modèle dans le registry"""
        try:
            # Création métadonnées
            model_metadata = ModelMetadata(
                model_id=model_id,
                model_type=model_type,
                version=version,
                framework_version=self._get_framework_version(model_type),
                size_bytes=0  # Sera calculé lors du chargement
            )
            
            # Ajout métadonnées personnalisées
            if metadata:
                for key, value in metadata.items():
                    if hasattr(model_metadata, key):
                        setattr(model_metadata, key, value)
                    elif key == "tags":
                        model_metadata.tags.extend(value if isinstance(value, list) else [value])
                    elif key == "performance_metrics":
                        model_metadata.performance_metrics.update(value)
            
            # Stockage dans registry
            self.model_registry[model_id] = model_metadata
            
            # Persistance métadonnées Redis
            await self._persist_model_metadata(model_metadata)
            
            # Chargement préemptif si configuré
            if self.config.get('preload_models', False):
                await self.load_model(model_id, model_path_or_data)
            
            logger.info(f"✅ Modèle enregistré: {model_id} v{version} ({model_type.value})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur enregistrement modèle {model_id}: {e}")
            return False
    
    def _get_framework_version(self, model_type: ModelType) -> str:
        """**ML Engineer**: Détection version framework"""
        try:
            if model_type == ModelType.SKLEARN:
                import sklearn
                return sklearn.__version__
            elif model_type == ModelType.PYTORCH:
                return torch.__version__
            elif model_type == ModelType.TENSORFLOW:
                return tf.__version__
            elif model_type == ModelType.HUGGINGFACE:
                import transformers
                return transformers.__version__
            else:
                return "unknown"
        except ImportError:
            return "not_installed"
    
    async def load_model(
        self, 
        model_id: str, 
        model_path_or_data: Union[str, Any],
        force_reload: bool = False
    ) -> bool:
        """**Backend Senior**: Chargement modèle avec optimisations"""
        
        # Vérification cache existant
        if not force_reload and model_id in self.memory_cache:
            cache_entry = self.memory_cache[model_id]
            if cache_entry.status == ModelStatus.READY:
                cache_entry.last_access = time.time()
                cache_entry.access_count += 1
                self.cache_stats["hits"] += 1
                return True
        
        # Vérification chargement en cours
        if model_id in self.loading_in_progress:
            logger.info(f"⏳ Modèle {model_id} déjà en cours de chargement")
            return False
        
        try:
            self.loading_in_progress.add(model_id)
            start_time = time.time()
            
            # Récupération métadonnées
            metadata = self.model_registry.get(model_id)
            if not metadata:
                logger.error(f"❌ Modèle {model_id} non enregistré")
                return False
            
            # Chargement selon type
            model_data = await self._load_model_by_type(
                metadata.model_type, 
                model_path_or_data
            )
            
            if model_data is None:
                return False
            
            # Calcul taille modèle
            size_bytes = await self._calculate_model_size(model_data, metadata.model_type)
            metadata.size_bytes = size_bytes
            
            # Vérification limite taille
            if size_bytes > self.max_model_size_mb * 1024 * 1024:
                logger.warning(
                    f"⚠️ Modèle {model_id} trop volumineux "
                    f"({size_bytes/1024/1024:.1f}MB > {self.max_model_size_mb}MB)"
                )
                # Cache Redis uniquement pour gros modèles
                if self.cache_strategy != CacheStrategy.MEMORY_ONLY:
                    await self._cache_model_redis_only(model_id, model_data, metadata)
                return True
            
            # Création entrée cache
            cache_key = self._generate_cache_key(model_id, metadata.version)
            cache_entry = CacheEntry(
                model_id=model_id,
                model_data=model_data,
                metadata=metadata,
                status=ModelStatus.READY,
                cache_key=cache_key,
                ttl=self.model_cache_ttl
            )
            
            # Gestion éviction si cache plein
            await self._ensure_memory_capacity()
            
            # Stockage cache mémoire
            self.memory_cache[model_id] = cache_entry
            
            # Cache Redis si stratégie hybride
            if self.cache_strategy in [CacheStrategy.HYBRID, CacheStrategy.REDIS_ONLY]:
                await self._cache_model_redis(cache_entry)
            
            # Mise à jour métriques
            load_time = time.time() - start_time
            metadata.last_used = time.time()
            self.cache_stats["loads"] += 1
            
            logger.info(
                f"✅ Modèle chargé: {model_id} "
                f"({size_bytes/1024/1024:.1f}MB, {load_time:.2f}s)"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur chargement modèle {model_id}: {e}")
            return False
        finally:
            self.loading_in_progress.discard(model_id)
    
    async def _load_model_by_type(
        self, 
        model_type: ModelType, 
        model_path_or_data: Union[str, Any]
    ) -> Optional[Any]:
        """**ML Engineer**: Chargement spécialisé par type de modèle"""
        try:
            if model_type == ModelType.SKLEARN:
                if isinstance(model_path_or_data, str):
                    return joblib.load(model_path_or_data)
                else:
                    return model_path_or_data
            
            elif model_type == ModelType.PYTORCH:
                if isinstance(model_path_or_data, str):
                    return torch.load(model_path_or_data, map_location='cpu')
                else:
                    return model_path_or_data
            
            elif model_type == ModelType.TENSORFLOW:
                if isinstance(model_path_or_data, str):
                    return tf.keras.models.load_model(model_path_or_data)
                else:
                    return model_path_or_data
            
            elif model_type == ModelType.HUGGINGFACE:
                # Gestion modèles HuggingFace
                from transformers import AutoModel, AutoTokenizer
                if isinstance(model_path_or_data, str):
                    model = AutoModel.from_pretrained(model_path_or_data)
                    tokenizer = AutoTokenizer.from_pretrained(model_path_or_data)
                    return {"model": model, "tokenizer": tokenizer}
                else:
                    return model_path_or_data
            
            elif model_type == ModelType.CUSTOM:
                # Modèles personnalisés - sérialisation pickle
                if isinstance(model_path_or_data, str):
                    with open(model_path_or_data, 'rb') as f:
                        return pickle.load(f)
                else:
                    return model_path_or_data
            
            else:
                logger.error(f"❌ Type de modèle non supporté: {model_type}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erreur chargement modèle {model_type}: {e}")
            return None
    
    async def _calculate_model_size(self, model_data: Any, model_type: ModelType) -> int:
        """**Backend Senior**: Calcul taille mémoire modèle"""
        try:
            if model_type == ModelType.PYTORCH:
                if hasattr(model_data, 'parameters'):
                    total_params = sum(p.numel() for p in model_data.parameters())
                    return total_params * 4  # Float32 = 4 bytes
                else:
                    return len(pickle.dumps(model_data))
            
            elif model_type == ModelType.TENSORFLOW:
                if hasattr(model_data, 'count_params'):
                    return model_data.count_params() * 4
                else:
                    return len(pickle.dumps(model_data))
            
            elif model_type == ModelType.HUGGINGFACE:
                if isinstance(model_data, dict) and 'model' in model_data:
                    # Estimation basée sur nombre de paramètres
                    model = model_data['model']
                    if hasattr(model, 'num_parameters'):
                        return model.num_parameters() * 4
                return len(pickle.dumps(model_data))
            
            else:
                # Sérialisation générique pour estimation
                return len(pickle.dumps(model_data))
                
        except Exception as e:
            logger.warning(f"⚠️ Erreur calcul taille modèle: {e}")
            return 1024 * 1024  # 1MB par défaut
    
    async def get_model(self, model_id: str) -> Optional[Any]:
        """**Lead Dev IA**: Récupération modèle avec stratégie intelligente"""
        start_time = time.time()
        
        try:
            # Vérification cache mémoire L1
            if model_id in self.memory_cache:
                cache_entry = self.memory_cache[model_id]
                if cache_entry.status == ModelStatus.READY:
                    # Mise à jour métriques accès
                    cache_entry.last_access = time.time()
                    cache_entry.access_count += 1
                    self.cache_stats["hits"] += 1
                    
                    # Enregistrement performance
                    access_time = time.time() - start_time
                    self.performance_metrics.append({
                        "model_id": model_id,
                        "access_time": access_time,
                        "cache_level": "memory",
                        "timestamp": time.time()
                    })
                    
                    return cache_entry.model_data
            
            # Tentative cache Redis L2
            if self.cache_strategy in [CacheStrategy.HYBRID, CacheStrategy.REDIS_ONLY]:
                model_data = await self._get_model_from_redis(model_id)
                if model_data:
                    # Promotion vers cache mémoire si approprié
                    await self._promote_to_memory_cache(model_id, model_data)
                    
                    access_time = time.time() - start_time
                    self.performance_metrics.append({
                        "model_id": model_id,
                        "access_time": access_time,
                        "cache_level": "redis",
                        "timestamp": time.time()
                    })
                    
                    return model_data
            
            # Cache miss
            self.cache_stats["misses"] += 1
            logger.debug(f"❌ Cache miss pour modèle: {model_id}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération modèle {model_id}: {e}")
            return None
    
    async def predict(
        self,
        model_id: str,
        input_data: Any,
        use_inference_cache: bool = True,
        cache_result: bool = True
    ) -> Optional[Dict[str, Any]]:
        """**ML Engineer**: Prédiction avec cache intelligent des inférences"""
        
        start_time = time.time()
        
        try:
            # Génération hash pour cache inférence
            input_hash = self._generate_input_hash(input_data) if use_inference_cache else None
            
            # Vérification cache inférence
            if input_hash and input_hash in self.inference_cache:
                inference_entry = self.inference_cache[input_hash]
                if inference_entry.model_id == model_id:
                    # Hit cache inférence
                    inference_entry.access_count += 1
                    self.cache_stats["inference_cache_hits"] += 1
                    
                    return {
                        "result": inference_entry.result,
                        "confidence": inference_entry.confidence,
                        "inference_time": inference_entry.inference_time,
                        "cached": True,
                        "cache_age": time.time() - inference_entry.cached_at
                    }
            
            # Récupération modèle
            model = await self.get_model(model_id)
            if model is None:
                logger.error(f"❌ Modèle {model_id} non disponible")
                return None
            
            # Exécution inférence
            result = await self._execute_inference(model_id, model, input_data)
            
            if result is None:
                return None
            
            inference_time = time.time() - start_time
            
            # Cache résultat si demandé
            if cache_result and input_hash:
                await self._cache_inference_result(
                    input_hash, model_id, result, inference_time
                )
            
            # Mise à jour statistiques modèle
            metadata = self.model_registry.get(model_id)
            if metadata:
                metadata.usage_count += 1
                metadata.last_used = time.time()
                # Moyenne mobile temps inférence
                if metadata.average_inference_time == 0:
                    metadata.average_inference_time = inference_time
                else:
                    metadata.average_inference_time = (
                        metadata.average_inference_time * 0.9 + inference_time * 0.1
                    )
            
            self.cache_stats["inference_cache_misses"] += 1
            
            return {
                "result": result,
                "confidence": None,  # À implémenter selon modèle
                "inference_time": inference_time,
                "cached": False,
                "model_metadata": metadata.__dict__ if metadata else {}
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur prédiction {model_id}: {e}")
            return None
    
    async def _execute_inference(self, model_id: str, model: Any, input_data: Any) -> Optional[Any]:
        """**ML Engineer**: Exécution inférence selon type de modèle"""
        try:
            metadata = self.model_registry.get(model_id)
            if not metadata:
                return None
            
            model_type = metadata.model_type
            
            if model_type == ModelType.SKLEARN:
                if hasattr(model, 'predict'):
                    return model.predict(input_data)
                elif hasattr(model, 'transform'):
                    return model.transform(input_data)
                else:
                    return None
            
            elif model_type == ModelType.PYTORCH:
                model.eval()
                with torch.no_grad():
                    if isinstance(input_data, np.ndarray):
                        input_tensor = torch.from_numpy(input_data).float()
                    else:
                        input_tensor = input_data
                    
                    output = model(input_tensor)
                    return output.numpy() if hasattr(output, 'numpy') else output
            
            elif model_type == ModelType.TENSORFLOW:
                return model.predict(input_data)
            
            elif model_type == ModelType.HUGGINGFACE:
                if isinstance(model, dict) and 'model' in model:
                    hf_model = model['model']
                    tokenizer = model.get('tokenizer')
                    
                    if tokenizer and isinstance(input_data, str):
                        # Tokenisation automatique
                        inputs = tokenizer(input_data, return_tensors="pt", padding=True, truncation=True)
                        outputs = hf_model(**inputs)
                        return outputs.last_hidden_state.detach().numpy()
                    else:
                        outputs = hf_model(input_data)
                        return outputs.last_hidden_state.detach().numpy()
                else:
                    return model(input_data)
            
            elif model_type == ModelType.CUSTOM:
                # Modèle personnalisé - tentative d'appel direct
                if callable(model):
                    return model(input_data)
                elif hasattr(model, 'predict'):
                    return model.predict(input_data)
                elif hasattr(model, '__call__'):
                    return model(input_data)
                else:
                    logger.error(f"❌ Modèle personnalisé {model_id} non callable")
                    return None
            
            else:
                logger.error(f"❌ Type de modèle non supporté pour inférence: {model_type}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erreur exécution inférence {model_id}: {e}")
            return None
    
    def _generate_input_hash(self, input_data: Any) -> str:
        """**Backend Senior**: Génération hash robuste pour cache inférence"""
        try:
            if isinstance(input_data, np.ndarray):
                # Hash spécialisé pour arrays NumPy
                return hashlib.sha256(input_data.tobytes()).hexdigest()[:16]
            elif isinstance(input_data, (list, tuple)):
                # Conversion en string pour hash
                input_str = str(input_data)
            elif isinstance(input_data, str):
                input_str = input_data
            elif hasattr(input_data, 'numpy'):
                # Tensors PyTorch/TensorFlow
                return hashlib.sha256(input_data.numpy().tobytes()).hexdigest()[:16]
            else:
                # Sérialisation générique
                input_str = json.dumps(input_data, sort_keys=True, default=str)
            
            return hashlib.sha256(input_str.encode()).hexdigest()[:16]
            
        except Exception as e:
            logger.warning(f"⚠️ Erreur génération hash: {e}")
            return hashlib.sha256(str(input_data).encode()).hexdigest()[:16]
    
    async def _cache_inference_result(
        self,
        input_hash: str,
        model_id: str,
        result: Any,
        inference_time: float
    ):
        """**Backend Senior**: Cache résultat inférence avec gestion TTL"""
        try:
            metadata = self.model_registry.get(model_id)
            model_version = metadata.version if metadata else "unknown"
            
            inference_entry = InferenceCache(
                input_hash=input_hash,
                model_id=model_id,
                model_version=model_version,
                result=result,
                inference_time=inference_time
            )
            
            # Gestion taille cache inférence
            if len(self.inference_cache) > 10000:  # Limite cache inférence
                # Éviction LRU
                oldest_hash = min(
                    self.inference_cache.keys(),
                    key=lambda h: self.inference_cache[h].cached_at
                )
                del self.inference_cache[oldest_hash]
            
            self.inference_cache[input_hash] = inference_entry
            
            # Cache Redis pour persistance
            if self.cache_strategy in [CacheStrategy.HYBRID, CacheStrategy.REDIS_ONLY]:
                await self._cache_inference_redis(input_hash, inference_entry)
            
        except Exception as e:
            logger.error(f"❌ Erreur cache inférence: {e}")
    
    async def _ensure_memory_capacity(self):
        """**Backend Senior**: Gestion capacité cache mémoire avec éviction intelligente"""
        if len(self.memory_cache) >= self.max_memory_models:
            # Éviction basée sur score composite
            eviction_scores = {}
            current_time = time.time()
            
            for model_id, cache_entry in self.memory_cache.items():
                # Score basé sur: récence, fréquence, taille
                recency = current_time - cache_entry.last_access
                frequency = cache_entry.access_count / max(1, (current_time - cache_entry.cached_at) / 3600)
                size_penalty = cache_entry.metadata.size_bytes / (1024 * 1024)  # MB
                
                # Score composite (plus bas = éviction prioritaire)
                score = frequency / (1 + recency / 3600) - size_penalty * 0.1
                eviction_scores[model_id] = score
            
            # Éviction du modèle avec plus bas score
            model_to_evict = min(eviction_scores.keys(), key=lambda k: eviction_scores[k])
            
            del self.memory_cache[model_to_evict]
            self.cache_stats["evictions"] += 1
            
            logger.info(f"🗑️ Modèle évincé: {model_to_evict} (score: {eviction_scores[model_to_evict]:.3f})")
    
    def _generate_cache_key(self, model_id: str, version: str) -> str:
        """**Backend Senior**: Génération clé cache consistante"""
        return f"ml_model:{model_id}:{version}"
    
    async def _cache_model_redis(self, cache_entry: CacheEntry):
        """**Backend Senior**: Cache modèle Redis avec compression"""
        try:
            async with self.redis_pool.get_connection() as redis_conn:
                # Sérialisation et compression
                serialized_model = pickle.dumps(cache_entry.model_data)
                compressed_model = gzip.compress(serialized_model)
                
                # Métadonnées séparées
                metadata_dict = cache_entry.metadata.__dict__.copy()
                metadata_dict['cached_at'] = cache_entry.cached_at
                metadata_dict['status'] = cache_entry.status.value
                
                # Stockage avec TTL
                pipeline = redis_conn.pipeline()
                pipeline.setex(
                    cache_entry.cache_key,
                    cache_entry.ttl or self.model_cache_ttl,
                    compressed_model
                )
                pipeline.setex(
                    f"{cache_entry.cache_key}:metadata",
                    cache_entry.ttl or self.model_cache_ttl,
                    json.dumps(metadata_dict)
                )
                await pipeline.execute()
                
                logger.debug(f"💾 Modèle mis en cache Redis: {cache_entry.model_id}")
                
        except Exception as e:
            logger.error(f"❌ Erreur cache Redis: {e}")
    
    async def _get_model_from_redis(self, model_id: str) -> Optional[Any]:
        """**Backend Senior**: Récupération modèle depuis Redis"""
        try:
            metadata = self.model_registry.get(model_id)
            if not metadata:
                return None
            
            cache_key = self._generate_cache_key(model_id, metadata.version)
            
            async with self.redis_pool.get_connection() as redis_conn:
                compressed_model = await redis_conn.get(cache_key)
                
                if compressed_model:
                    # Décompression et désérialisation
                    serialized_model = gzip.decompress(compressed_model)
                    model_data = pickle.loads(serialized_model)
                    
                    logger.debug(f"📥 Modèle récupéré depuis Redis: {model_id}")
                    return model_data
                
                return None
                
        except Exception as e:
            logger.error(f"❌ Erreur récupération Redis: {e}")
            return None
    
    async def _cache_inference_redis(self, input_hash: str, inference_entry: InferenceCache):
        """**Backend Senior**: Cache inférence Redis"""
        try:
            async with self.redis_pool.get_connection() as redis_conn:
                cache_key = f"inference:{input_hash}"
                cache_data = {
                    "model_id": inference_entry.model_id,
                    "model_version": inference_entry.model_version,
                    "result": pickle.dumps(inference_entry.result).hex(),
                    "confidence": inference_entry.confidence,
                    "inference_time": inference_entry.inference_time,
                    "cached_at": inference_entry.cached_at
                }
                
                await redis_conn.setex(
                    cache_key,
                    self.inference_cache_ttl,
                    json.dumps(cache_data)
                )
                
        except Exception as e:
            logger.error(f"❌ Erreur cache inférence Redis: {e}")
    
    async def _persist_model_metadata(self, metadata: ModelMetadata):
        """**DevOps**: Persistance métadonnées modèle"""
        try:
            async with self.redis_pool.get_connection() as redis_conn:
                metadata_key = f"model_metadata:{metadata.model_id}"
                metadata_dict = metadata.__dict__.copy()
                
                await redis_conn.hset(
                    metadata_key,
                    mapping={k: json.dumps(v) for k, v in metadata_dict.items()}
                )
                
                # Index par type de modèle
                await redis_conn.sadd(f"models_by_type:{metadata.model_type.value}", metadata.model_id)
                
        except Exception as e:
            logger.error(f"❌ Erreur persistance métadonnées: {e}")
    
    async def _background_loader(self):
        """**DevOps**: Chargeur de modèles en arrière-plan"""
        while True:
            try:
                await asyncio.sleep(1)
                
                if self.loading_queue:
                    model_id, model_path = self.loading_queue.popleft()
                    await self.load_model(model_id, model_path)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Erreur background loader: {e}")
    
    async def _cache_maintenance_loop(self):
        """**DevOps**: Maintenance cache périodique"""
        while True:
            try:
                await asyncio.sleep(300)  # Toutes les 5 minutes
                
                current_time = time.time()
                
                # Nettoyage cache inférence expiré
                expired_inference = []
                for hash_key, entry in self.inference_cache.items():
                    if current_time - entry.cached_at > self.inference_cache_ttl:
                        expired_inference.append(hash_key)
                
                for hash_key in expired_inference:
                    del self.inference_cache[hash_key]
                
                if expired_inference:
                    logger.info(f"🧹 {len(expired_inference)} entrées cache inférence expirées nettoyées")
                
                # Mise à jour métriques modèles
                await self._update_model_metrics()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Erreur maintenance cache: {e}")
    
    async def _performance_monitoring_loop(self):
        """**DevOps**: Monitoring performance continu"""
        while True:
            try:
                await asyncio.sleep(60)  # Chaque minute
                
                # Calcul métriques performance
                if self.performance_metrics:
                    recent_metrics = list(self.performance_metrics)[-100:]  # 100 dernières
                    avg_access_time = np.mean([m["access_time"] for m in recent_metrics])
                    
                    # Alertes performance
                    if avg_access_time > 1.0:  # > 1 seconde
                        logger.warning(f"⚠️ Performance dégradée: {avg_access_time:.2f}s moyenne")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Erreur monitoring performance: {e}")
    
    async def _update_model_metrics(self):
        """**DevOps**: Mise à jour métriques modèles"""
        for model_id, metadata in self.model_registry.items():
            try:
                # Persistance métriques mises à jour
                await self._persist_model_metadata(metadata)
                
            except Exception as e:
                logger.error(f"❌ Erreur mise à jour métriques {model_id}: {e}")
    
    async def get_cache_dashboard(self) -> Dict[str, Any]:
        """**DevOps**: Dashboard cache ML complet"""
        
        # Statistiques globales
        total_memory_usage = sum(
            entry.metadata.size_bytes 
            for entry in self.memory_cache.values()
        )
        
        # Top modèles par utilisation
        top_models = sorted(
            self.model_registry.items(),
            key=lambda x: x[1].usage_count,
            reverse=True
        )[:10]
        
        # Métriques performance récentes
        recent_perf = list(self.performance_metrics)[-100:] if self.performance_metrics else []
        avg_access_time = np.mean([m["access_time"] for m in recent_perf]) if recent_perf else 0
        
        return {
            "cache_statistics": {
                "models_in_memory": len(self.memory_cache),
                "total_memory_usage_mb": round(total_memory_usage / 1024 / 1024, 2),
                "inference_cache_size": len(self.inference_cache),
                "cache_hit_ratio": (
                    self.cache_stats["hits"] / 
                    (self.cache_stats["hits"] + self.cache_stats["misses"] + 1) * 100
                ),
                "inference_hit_ratio": (
                    self.cache_stats["inference_cache_hits"] /
                    (self.cache_stats["inference_cache_hits"] + self.cache_stats["inference_cache_misses"] + 1) * 100
                )
            },
            "performance_metrics": {
                "average_access_time_ms": round(avg_access_time * 1000, 2),
                "models_loaded": self.cache_stats["loads"],
                "cache_evictions": self.cache_stats["evictions"]
            },
            "model_registry": {
                "total_models": len(self.model_registry),
                "models_by_type": self._get_models_by_type_stats(),
                "top_models": [
                    {
                        "model_id": model_id,
                        "usage_count": metadata.usage_count,
                        "avg_inference_time_ms": round(metadata.average_inference_time * 1000, 2),
                        "size_mb": round(metadata.size_bytes / 1024 / 1024, 2)
                    }
                    for model_id, metadata in top_models
                ]
            },
            "cache_strategy": self.cache_strategy.value,
            "configuration": {
                "max_memory_models": self.max_memory_models,
                "max_model_size_mb": self.max_model_size_mb,
                "model_cache_ttl": self.model_cache_ttl,
                "inference_cache_ttl": self.inference_cache_ttl
            }
        }
    
    def _get_models_by_type_stats(self) -> Dict[str, int]:
        """**DevOps**: Statistiques modèles par type"""
        stats = defaultdict(int)
        for metadata in self.model_registry.values():
            stats[metadata.model_type.value] += 1
        return dict(stats)
    
    async def invalidate_model(self, model_id: str):
        """**ML Engineer**: Invalidation modèle et cache associé"""
        try:
            # Suppression cache mémoire
            if model_id in self.memory_cache:
                del self.memory_cache[model_id]
            
            # Suppression cache Redis
            metadata = self.model_registry.get(model_id)
            if metadata:
                cache_key = self._generate_cache_key(model_id, metadata.version)
                
                async with self.redis_pool.get_connection() as redis_conn:
                    await redis_conn.delete(cache_key)
                    await redis_conn.delete(f"{cache_key}:metadata")
            
            # Invalidation cache inférence associé
            inference_to_remove = []
            for hash_key, entry in self.inference_cache.items():
                if entry.model_id == model_id:
                    inference_to_remove.append(hash_key)
            
            for hash_key in inference_to_remove:
                del self.inference_cache[hash_key]
            
            logger.info(f"🗑️ Modèle invalidé: {model_id}")
            
        except Exception as e:
            logger.error(f"❌ Erreur invalidation modèle {model_id}: {e}")

# Factory function
async def create_ml_model_cache_engine(redis_pool, config: Optional[Dict[str, Any]] = None):
    """**Lead Dev IA**: Factory création moteur cache ML"""
    return MLModelCacheEngine(redis_pool, config)

if __name__ == "__main__":
    async def demo():
        """Démonstration ML Model Cache Engine"""
        
        # Configuration Redis simulée
        class MockRedisPool:
            def get_connection(self):
                from unittest.mock import AsyncMock
                return AsyncMock()
        
        # Configuration moteur
        config = {
            'cache_strategy': 'hybrid',
            'max_memory_models': 5,
            'inference_cache_ttl': 1800
        }
        
        # Création moteur
        engine = await create_ml_model_cache_engine(MockRedisPool(), config)
        
        # Simulation modèle scikit-learn
        from sklearn.ensemble import RandomForestClassifier
        mock_model = RandomForestClassifier(n_estimators=10)
        
        # Enregistrement modèle
        await engine.register_model(
            "test_classifier",
            ModelType.SKLEARN,
            "1.0.0",
            mock_model,
            {"tags": ["classification", "test"]}
        )
        
        # Chargement
        success = await engine.load_model("test_classifier", mock_model)
        print(f"Modèle chargé: {success}")
        
        # Test récupération
        retrieved_model = await engine.get_model("test_classifier")
        print(f"Modèle récupéré: {retrieved_model is not None}")
        
        # Dashboard
        dashboard = await engine.get_cache_dashboard()
        print(f"Dashboard: {dashboard['cache_statistics']}")
    
    asyncio.run(demo())