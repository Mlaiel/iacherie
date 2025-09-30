"""
Model Cache Manager - Intelligent AI Model Caching System
========================================================

Enterprise-grade caching system for AI models in the Ainflue platform.
Optimizes model loading, inference speed, and resource utilization across 53 AI agents.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue Infrastructure - AI Optimization Module
Expert Role: Lead Dev IA + ML Engineer + Backend Senior
Version: 1.0 Production Enterprise

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
==========================================
Cette architecture est la propriété intellectuelle EXCLUSIVE de Fahed Mlaiel (mlaiel@live.de).
Toute reproduction, modification, distribution ou vol d'idée/concept/code sans autorisation 
écrite PERSONNELLE est STRICTEMENT INTERDITE et sera poursuivie en justice.
"""

import asyncio
import logging
import hashlib
import pickle
import json
import time
import threading
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import weakref
import psutil
import torch
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import redis
import sqlite3
from pathlib import Path
import shutil
import tempfile

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CacheStrategy(Enum):
    """Cache replacement strategies"""
    LRU = "least_recently_used"
    LFU = "least_frequently_used"
    FIFO = "first_in_first_out"
    TTL = "time_to_live"
    ADAPTIVE = "adaptive"
    PRIORITY = "priority_based"

class CacheTier(Enum):
    """Cache tier levels for different storage types"""
    MEMORY = "memory"
    SSD = "ssd"
    HDD = "hdd"
    NETWORK = "network"
    REMOTE = "remote"

class ModelStatus(Enum):
    """Model status in cache"""
    LOADING = "loading"
    READY = "ready"
    EVICTING = "evicting"
    ERROR = "error"
    WARMING = "warming"

@dataclass
class CachedModel:
    """Cached model metadata and data"""
    model_id: str
    model_name: str
    model_size_mb: float
    cache_tier: CacheTier
    status: ModelStatus
    last_accessed: datetime
    access_count: int
    load_time_ms: float
    cache_key: str
    priority_score: float
    ttl_expires: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)

@dataclass
class CacheMetrics:
    """Cache performance metrics"""
    hit_rate: float
    miss_rate: float
    eviction_rate: float
    average_load_time: float
    memory_utilization: float
    total_requests: int
    cache_size_mb: float
    active_models: int

class ModelCacheManager:
    """
    Intelligent AI Model Cache Manager
    
    Provides enterprise-grade caching for AI models with multi-tier storage,
    intelligent eviction policies, and performance optimization for the Ainflue platform.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Model Cache Manager"""
        self.config = config or self._get_default_config()
        self.cache_storage = {}  # In-memory cache
        self.cache_metadata = {}  # Model metadata
        self.access_stats = {}  # Access statistics
        self.cache_lock = threading.RLock()
        self.eviction_scheduler = None
        self.cache_metrics = CacheMetrics(0, 0, 0, 0, 0, 0, 0, 0)
        
        # Initialize storage tiers
        self._initialize_storage_tiers()
        
        # Initialize cache strategies
        self._initialize_cache_strategies()
        
        # Start background tasks
        self._start_background_tasks()
        
        logger.info("💾 Model Cache Manager initialized - Enterprise caching ready")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for model cache manager"""
        return {
            "memory_cache": {
                "max_size_gb": 8.0,
                "max_models": 50,
                "strategy": CacheStrategy.ADAPTIVE.value
            },
            "ssd_cache": {
                "max_size_gb": 100.0,
                "max_models": 200,
                "strategy": CacheStrategy.LRU.value,
                "path": "/var/cache/ainflue/models/ssd"
            },
            "hdd_cache": {
                "max_size_gb": 500.0,
                "max_models": 1000,
                "strategy": CacheStrategy.FIFO.value,
                "path": "/var/cache/ainflue/models/hdd"
            },
            "network_cache": {
                "redis_url": "redis://localhost:6379/0",
                "max_size_gb": 50.0,
                "ttl_hours": 24
            },
            "eviction_policies": {
                "memory_threshold": 0.85,
                "check_interval_seconds": 30,
                "aggressive_cleanup_threshold": 0.95
            },
            "preloading": {
                "enabled": True,
                "popular_models": ["image_enhance", "audio_process", "content_analyze"],
                "preload_on_startup": True,
                "prediction_enabled": True
            },
            "compression": {
                "enabled": True,
                "algorithm": "zstd",
                "compression_level": 3
            },
            "monitoring": {
                "metrics_collection": True,
                "performance_tracking": True,
                "alert_thresholds": {
                    "hit_rate_min": 0.80,
                    "memory_usage_max": 0.90,
                    "load_time_max": 5.0
                }
            }
        }
    
    def _initialize_storage_tiers(self) -> None:
        """Initialize multi-tier storage system"""
        # Create cache directories
        for tier in ["ssd", "hdd"]:
            cache_path = Path(self.config[f"{tier}_cache"]["path"])
            cache_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize Redis connection for network cache
        try:
            import redis
            self.redis_client = redis.from_url(
                self.config["network_cache"]["redis_url"],
                decode_responses=False
            )
            # Test connection
            self.redis_client.ping()
            logger.info("✅ Redis network cache connected")
        except Exception as e:
            logger.warning(f"⚠️ Redis connection failed: {e}")
            self.redis_client = None
        
        # Initialize metadata database
        self._initialize_metadata_db()
    
    def _initialize_metadata_db(self) -> None:
        """Initialize SQLite database for cache metadata"""
        self.db_path = Path(self.config["ssd_cache"]["path"]) / "cache_metadata.db"
        
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cached_models (
                    model_id TEXT PRIMARY KEY,
                    model_name TEXT,
                    model_size_mb REAL,
                    cache_tier TEXT,
                    status TEXT,
                    last_accessed TIMESTAMP,
                    access_count INTEGER,
                    load_time_ms REAL,
                    cache_key TEXT,
                    priority_score REAL,
                    ttl_expires TIMESTAMP,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS access_stats (
                    model_id TEXT,
                    access_time TIMESTAMP,
                    load_time_ms REAL,
                    cache_tier TEXT,
                    hit BOOLEAN
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_model_access 
                ON access_stats(model_id, access_time)
            """)
    
    def _initialize_cache_strategies(self) -> None:
        """Initialize cache replacement strategies"""
        self.strategies = {
            CacheStrategy.LRU: self._lru_eviction,
            CacheStrategy.LFU: self._lfu_eviction,
            CacheStrategy.FIFO: self._fifo_eviction,
            CacheStrategy.TTL: self._ttl_eviction,
            CacheStrategy.ADAPTIVE: self._adaptive_eviction,
            CacheStrategy.PRIORITY: self._priority_eviction
        }
    
    def _start_background_tasks(self) -> None:
        """Start background maintenance tasks"""
        # Start eviction scheduler
        self.eviction_scheduler = threading.Thread(
            target=self._eviction_scheduler_loop,
            daemon=True
        )
        self.eviction_scheduler.start()
        
        # Start metrics collection
        self.metrics_collector = threading.Thread(
            target=self._metrics_collection_loop,
            daemon=True
        )
        self.metrics_collector.start()
        
        # Preload popular models if enabled
        if self.config["preloading"]["preload_on_startup"]:
            threading.Thread(target=self._preload_popular_models, daemon=True).start()
    
    async def get_model(self, model_id: str, model_loader: Callable) -> Any:
        """
        Get model from cache or load if not cached
        
        Args:
            model_id: Unique identifier for the model
            model_loader: Function to load the model if not in cache
            
        Returns:
            Loaded model object
        """
        start_time = time.time()
        
        try:
            # Check cache first
            cached_model = await self._get_from_cache(model_id)
            
            if cached_model is not None:
                # Cache hit
                await self._record_access(model_id, time.time() - start_time, True)
                logger.debug(f"💾 Cache HIT for model: {model_id}")
                return cached_model
            
            # Cache miss - load model
            logger.debug(f"💾 Cache MISS for model: {model_id}")
            model = await self._load_and_cache_model(model_id, model_loader)
            
            load_time = time.time() - start_time
            await self._record_access(model_id, load_time, False)
            
            return model
            
        except Exception as e:
            logger.error(f"❌ Failed to get model {model_id}: {str(e)}")
            raise
    
    async def _get_from_cache(self, model_id: str) -> Optional[Any]:
        """Get model from appropriate cache tier"""
        with self.cache_lock:
            # Check memory cache first
            if model_id in self.cache_storage:
                cached_model = self.cache_storage[model_id]
                if cached_model.status == ModelStatus.READY:
                    await self._update_access_stats(model_id)
                    return cached_model.metadata.get("model_object")
            
            # Check SSD cache
            ssd_path = self._get_ssd_cache_path(model_id)
            if ssd_path.exists():
                model = await self._load_from_ssd(model_id, ssd_path)
                if model is not None:
                    # Promote to memory cache if there's space
                    await self._promote_to_memory(model_id, model)
                    return model
            
            # Check network cache (Redis)
            if self.redis_client:
                model = await self._load_from_network_cache(model_id)
                if model is not None:
                    # Cache in local tiers
                    await self._cache_locally(model_id, model)
                    return model
        
        return None
    
    async def _load_and_cache_model(self, model_id: str, model_loader: Callable) -> Any:
        """Load model and cache in appropriate tiers"""
        load_start = time.time()
        
        # Mark model as loading
        await self._set_model_status(model_id, ModelStatus.LOADING)
        
        try:
            # Load the model
            model = await asyncio.get_event_loop().run_in_executor(
                None, model_loader
            )
            
            load_time = (time.time() - load_start) * 1000  # Convert to ms
            
            # Calculate model size
            model_size = self._calculate_model_size(model)
            
            # Create cached model entry
            cached_model = CachedModel(
                model_id=model_id,
                model_name=f"model_{model_id}",
                model_size_mb=model_size,
                cache_tier=CacheTier.MEMORY,
                status=ModelStatus.READY,
                last_accessed=datetime.now(),
                access_count=1,
                load_time_ms=load_time,
                cache_key=self._generate_cache_key(model_id),
                priority_score=self._calculate_priority_score(model_id, model_size, load_time),
                metadata={"model_object": model}
            )
            
            # Cache in multiple tiers
            await self._cache_in_tiers(cached_model)
            
            logger.info(f"✅ Model {model_id} loaded and cached ({model_size:.1f}MB, {load_time:.1f}ms)")
            return model
            
        except Exception as e:
            await self._set_model_status(model_id, ModelStatus.ERROR)
            logger.error(f"❌ Failed to load model {model_id}: {str(e)}")
            raise
    
    async def _cache_in_tiers(self, cached_model: CachedModel) -> None:
        """Cache model in appropriate storage tiers"""
        with self.cache_lock:
            # Always try to cache in memory first
            if self._can_cache_in_memory(cached_model.model_size_mb):
                self.cache_storage[cached_model.model_id] = cached_model
                self.cache_metadata[cached_model.model_id] = cached_model
            else:
                # Evict models to make space
                await self._evict_for_space(cached_model.model_size_mb, CacheTier.MEMORY)
                self.cache_storage[cached_model.model_id] = cached_model
                self.cache_metadata[cached_model.model_id] = cached_model
        
        # Cache in SSD
        if self._can_cache_in_ssd(cached_model.model_size_mb):
            await self._save_to_ssd(cached_model)
        
        # Cache in network (Redis)
        if self.redis_client and self._can_cache_in_network(cached_model.model_size_mb):
            await self._save_to_network_cache(cached_model)
        
        # Update metadata database
        await self._update_metadata_db(cached_model)
    
    def _can_cache_in_memory(self, model_size_mb: float) -> bool:
        """Check if model can be cached in memory"""
        current_memory = self._get_current_memory_usage()
        max_memory = self.config["memory_cache"]["max_size_gb"] * 1024
        return (current_memory + model_size_mb) <= max_memory
    
    def _can_cache_in_ssd(self, model_size_mb: float) -> bool:
        """Check if model can be cached in SSD"""
        current_ssd = self._get_current_ssd_usage()
        max_ssd = self.config["ssd_cache"]["max_size_gb"] * 1024
        return (current_ssd + model_size_mb) <= max_ssd
    
    def _can_cache_in_network(self, model_size_mb: float) -> bool:
        """Check if model can be cached in network"""
        if not self.redis_client:
            return False
        
        try:
            info = self.redis_client.info()
            used_memory_mb = info.get("used_memory", 0) / (1024 * 1024)
            max_memory_mb = self.config["network_cache"]["max_size_gb"] * 1024
            return (used_memory_mb + model_size_mb) <= max_memory_mb
        except:
            return False
    
    async def _evict_for_space(self, required_space_mb: float, tier: CacheTier) -> None:
        """Evict models to make space for new model"""
        strategy = CacheStrategy(self.config[f"{tier.value}_cache"]["strategy"])
        eviction_func = self.strategies[strategy]
        
        models_to_evict = await eviction_func(required_space_mb, tier)
        
        for model_id in models_to_evict:
            await self._evict_model(model_id, tier)
            logger.info(f"🗑️ Evicted model {model_id} from {tier.value} cache")
    
    async def _lru_eviction(self, required_space_mb: float, tier: CacheTier) -> List[str]:
        """Least Recently Used eviction strategy"""
        candidates = []
        
        if tier == CacheTier.MEMORY:
            candidates = [
                (model_id, cached_model.last_accessed, cached_model.model_size_mb)
                for model_id, cached_model in self.cache_storage.items()
            ]
        
        # Sort by last accessed time (oldest first)
        candidates.sort(key=lambda x: x[1])
        
        evict_list = []
        freed_space = 0.0
        
        for model_id, _, size_mb in candidates:
            evict_list.append(model_id)
            freed_space += size_mb
            if freed_space >= required_space_mb:
                break
        
        return evict_list
    
    async def _lfu_eviction(self, required_space_mb: float, tier: CacheTier) -> List[str]:
        """Least Frequently Used eviction strategy"""
        candidates = []
        
        if tier == CacheTier.MEMORY:
            candidates = [
                (model_id, cached_model.access_count, cached_model.model_size_mb)
                for model_id, cached_model in self.cache_storage.items()
            ]
        
        # Sort by access count (least used first)
        candidates.sort(key=lambda x: x[1])
        
        evict_list = []
        freed_space = 0.0
        
        for model_id, _, size_mb in candidates:
            evict_list.append(model_id)
            freed_space += size_mb
            if freed_space >= required_space_mb:
                break
        
        return evict_list
    
    async def _fifo_eviction(self, required_space_mb: float, tier: CacheTier) -> List[str]:
        """First In First Out eviction strategy"""
        # For simplicity, treating creation time as insertion time
        return await self._lru_eviction(required_space_mb, tier)
    
    async def _ttl_eviction(self, required_space_mb: float, tier: CacheTier) -> List[str]:
        """Time To Live eviction strategy"""
        expired_models = []
        current_time = datetime.now()
        
        for model_id, cached_model in self.cache_storage.items():
            if cached_model.ttl_expires and current_time > cached_model.ttl_expires:
                expired_models.append(model_id)
        
        # If expired models provide enough space, return them
        expired_space = sum(
            self.cache_storage[model_id].model_size_mb 
            for model_id in expired_models
        )
        
        if expired_space >= required_space_mb:
            return expired_models[:int(required_space_mb / 100)]  # Approximate
        
        # Fall back to LRU for additional space
        additional_needed = required_space_mb - expired_space
        additional_evictions = await self._lru_eviction(additional_needed, tier)
        
        return expired_models + additional_evictions
    
    async def _adaptive_eviction(self, required_space_mb: float, tier: CacheTier) -> List[str]:
        """Adaptive eviction strategy based on usage patterns"""
        # Combine multiple factors: recency, frequency, size, priority
        candidates = []
        
        for model_id, cached_model in self.cache_storage.items():
            # Calculate composite score
            recency_score = (datetime.now() - cached_model.last_accessed).total_seconds() / 3600
            frequency_score = 1.0 / (cached_model.access_count + 1)
            size_score = cached_model.model_size_mb / 1000  # Normalize
            priority_score = 1.0 - cached_model.priority_score
            
            composite_score = (recency_score * 0.3 + frequency_score * 0.3 + 
                             size_score * 0.2 + priority_score * 0.2)
            
            candidates.append((model_id, composite_score, cached_model.model_size_mb))
        
        # Sort by composite score (higher means more likely to evict)
        candidates.sort(key=lambda x: x[1], reverse=True)
        
        evict_list = []
        freed_space = 0.0
        
        for model_id, _, size_mb in candidates:
            evict_list.append(model_id)
            freed_space += size_mb
            if freed_space >= required_space_mb:
                break
        
        return evict_list
    
    async def _priority_eviction(self, required_space_mb: float, tier: CacheTier) -> List[str]:
        """Priority-based eviction strategy"""
        candidates = [
            (model_id, cached_model.priority_score, cached_model.model_size_mb)
            for model_id, cached_model in self.cache_storage.items()
        ]
        
        # Sort by priority (lowest priority first)
        candidates.sort(key=lambda x: x[1])
        
        evict_list = []
        freed_space = 0.0
        
        for model_id, _, size_mb in candidates:
            evict_list.append(model_id)
            freed_space += size_mb
            if freed_space >= required_space_mb:
                break
        
        return evict_list
    
    async def _evict_model(self, model_id: str, tier: CacheTier) -> None:
        """Evict model from specified tier"""
        with self.cache_lock:
            if tier == CacheTier.MEMORY and model_id in self.cache_storage:
                del self.cache_storage[model_id]
            
            if tier == CacheTier.SSD:
                ssd_path = self._get_ssd_cache_path(model_id)
                if ssd_path.exists():
                    ssd_path.unlink()
            
            if tier == CacheTier.NETWORK and self.redis_client:
                cache_key = self._generate_cache_key(model_id)
                self.redis_client.delete(cache_key)
    
    def _get_ssd_cache_path(self, model_id: str) -> Path:
        """Get SSD cache file path for model"""
        cache_dir = Path(self.config["ssd_cache"]["path"])
        return cache_dir / f"{model_id}.cache"
    
    async def _save_to_ssd(self, cached_model: CachedModel) -> None:
        """Save model to SSD cache"""
        try:
            ssd_path = self._get_ssd_cache_path(cached_model.model_id)
            model_data = {
                "model_object": cached_model.metadata.get("model_object"),
                "metadata": cached_model.__dict__
            }
            
            # Use compression if enabled
            if self.config["compression"]["enabled"]:
                import zstandard as zstd
                cctx = zstd.ZstdCompressor(level=self.config["compression"]["compression_level"])
                compressed_data = cctx.compress(pickle.dumps(model_data))
                
                with open(ssd_path, "wb") as f:
                    f.write(compressed_data)
            else:
                with open(ssd_path, "wb") as f:
                    pickle.dump(model_data, f)
                    
        except Exception as e:
            logger.error(f"❌ Failed to save model {cached_model.model_id} to SSD: {str(e)}")
    
    async def _load_from_ssd(self, model_id: str, ssd_path: Path) -> Optional[Any]:
        """Load model from SSD cache"""
        try:
            with open(ssd_path, "rb") as f:
                if self.config["compression"]["enabled"]:
                    import zstandard as zstd
                    dctx = zstd.ZstdDecompressor()
                    compressed_data = f.read()
                    decompressed_data = dctx.decompress(compressed_data)
                    model_data = pickle.loads(decompressed_data)
                else:
                    model_data = pickle.load(f)
            
            return model_data["model_object"]
            
        except Exception as e:
            logger.error(f"❌ Failed to load model {model_id} from SSD: {str(e)}")
            # Clean up corrupted cache file
            if ssd_path.exists():
                ssd_path.unlink()
            return None
    
    async def _save_to_network_cache(self, cached_model: CachedModel) -> None:
        """Save model to network cache (Redis)"""
        if not self.redis_client:
            return
        
        try:
            cache_key = cached_model.cache_key
            model_data = {
                "model_object": cached_model.metadata.get("model_object"),
                "metadata": cached_model.__dict__
            }
            
            # Serialize and compress
            serialized_data = pickle.dumps(model_data)
            
            if self.config["compression"]["enabled"]:
                import zstandard as zstd
                cctx = zstd.ZstdCompressor()
                compressed_data = cctx.compress(serialized_data)
                data_to_store = compressed_data
            else:
                data_to_store = serialized_data
            
            # Set with TTL
            ttl_hours = self.config["network_cache"]["ttl_hours"]
            self.redis_client.setex(cache_key, ttl_hours * 3600, data_to_store)
            
        except Exception as e:
            logger.error(f"❌ Failed to save model {cached_model.model_id} to network cache: {str(e)}")
    
    async def _load_from_network_cache(self, model_id: str) -> Optional[Any]:
        """Load model from network cache (Redis)"""
        if not self.redis_client:
            return None
        
        try:
            cache_key = self._generate_cache_key(model_id)
            cached_data = self.redis_client.get(cache_key)
            
            if cached_data is None:
                return None
            
            # Decompress and deserialize
            if self.config["compression"]["enabled"]:
                import zstandard as zstd
                dctx = zstd.ZstdDecompressor()
                decompressed_data = dctx.decompress(cached_data)
                model_data = pickle.loads(decompressed_data)
            else:
                model_data = pickle.loads(cached_data)
            
            return model_data["model_object"]
            
        except Exception as e:
            logger.error(f"❌ Failed to load model {model_id} from network cache: {str(e)}")
            return None
    
    def _calculate_model_size(self, model: Any) -> float:
        """Calculate model size in MB"""
        try:
            if hasattr(model, "get_memory_footprint"):
                return model.get_memory_footprint() / (1024 * 1024)
            elif hasattr(model, "parameters"):
                # PyTorch model
                param_size = sum(p.numel() * p.element_size() for p in model.parameters())
                buffer_size = sum(b.numel() * b.element_size() for b in model.buffers())
                return (param_size + buffer_size) / (1024 * 1024)
            else:
                # Fallback: use pickle size
                return len(pickle.dumps(model)) / (1024 * 1024)
        except:
            return 100.0  # Default estimate
    
    def _calculate_priority_score(self, model_id: str, size_mb: float, load_time_ms: float) -> float:
        """Calculate priority score for model (higher = more important)"""
        # Priority factors:
        # 1. Popular models get higher priority
        # 2. Smaller models get higher priority (cache efficiency)
        # 3. Faster loading models get higher priority
        # 4. Recently loaded models get higher priority
        
        popular_models = self.config["preloading"]["popular_models"]
        popularity_score = 1.0 if model_id in popular_models else 0.5
        
        # Inverse relationship with size (smaller = higher priority)
        size_score = max(0.1, 1.0 - (size_mb / 1000))
        
        # Inverse relationship with load time
        load_time_score = max(0.1, 1.0 - (load_time_ms / 10000))
        
        # Combine scores
        priority_score = (popularity_score * 0.4 + size_score * 0.3 + load_time_score * 0.3)
        
        return min(1.0, max(0.0, priority_score))
    
    def _generate_cache_key(self, model_id: str) -> str:
        """Generate cache key for model"""
        return f"ainflue:model_cache:{model_id}"
    
    async def _update_access_stats(self, model_id: str) -> None:
        """Update access statistics for model"""
        with self.cache_lock:
            if model_id in self.cache_storage:
                cached_model = self.cache_storage[model_id]
                cached_model.last_accessed = datetime.now()
                cached_model.access_count += 1
    
    async def _record_access(self, model_id: str, load_time_ms: float, cache_hit: bool) -> None:
        """Record access statistics"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                conn.execute("""
                    INSERT INTO access_stats 
                    (model_id, access_time, load_time_ms, cache_tier, hit)
                    VALUES (?, ?, ?, ?, ?)
                """, (model_id, datetime.now(), load_time_ms, "memory", cache_hit))
        except Exception as e:
            logger.error(f"❌ Failed to record access stats: {str(e)}")
    
    async def _update_metadata_db(self, cached_model: CachedModel) -> None:
        """Update metadata database"""
        try:
            metadata_json = json.dumps({k: v for k, v in cached_model.metadata.items() 
                                      if k != "model_object"})
            
            with sqlite3.connect(str(self.db_path)) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO cached_models 
                    (model_id, model_name, model_size_mb, cache_tier, status,
                     last_accessed, access_count, load_time_ms, cache_key,
                     priority_score, ttl_expires, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    cached_model.model_id, cached_model.model_name,
                    cached_model.model_size_mb, cached_model.cache_tier.value,
                    cached_model.status.value, cached_model.last_accessed,
                    cached_model.access_count, cached_model.load_time_ms,
                    cached_model.cache_key, cached_model.priority_score,
                    cached_model.ttl_expires, metadata_json
                ))
        except Exception as e:
            logger.error(f"❌ Failed to update metadata DB: {str(e)}")
    
    async def _set_model_status(self, model_id: str, status: ModelStatus) -> None:
        """Set model status"""
        with self.cache_lock:
            if model_id in self.cache_metadata:
                self.cache_metadata[model_id].status = status
    
    def _get_current_memory_usage(self) -> float:
        """Get current memory cache usage in MB"""
        return sum(model.model_size_mb for model in self.cache_storage.values())
    
    def _get_current_ssd_usage(self) -> float:
        """Get current SSD cache usage in MB"""
        cache_dir = Path(self.config["ssd_cache"]["path"])
        total_size = 0
        
        for cache_file in cache_dir.glob("*.cache"):
            try:
                total_size += cache_file.stat().st_size
            except:
                continue
                
        return total_size / (1024 * 1024)
    
    def _eviction_scheduler_loop(self) -> None:
        """Background eviction scheduler loop"""
        while True:
            try:
                # Check memory usage
                memory_usage = self._get_current_memory_usage()
                max_memory = self.config["memory_cache"]["max_size_gb"] * 1024
                usage_ratio = memory_usage / max_memory if max_memory > 0 else 0
                
                threshold = self.config["eviction_policies"]["memory_threshold"]
                aggressive_threshold = self.config["eviction_policies"]["aggressive_cleanup_threshold"]
                
                if usage_ratio > aggressive_threshold:
                    # Aggressive cleanup
                    space_to_free = memory_usage * 0.3  # Free 30%
                    asyncio.run(self._evict_for_space(space_to_free, CacheTier.MEMORY))
                elif usage_ratio > threshold:
                    # Normal cleanup
                    space_to_free = memory_usage * 0.1  # Free 10%
                    asyncio.run(self._evict_for_space(space_to_free, CacheTier.MEMORY))
                
                # Sleep until next check
                interval = self.config["eviction_policies"]["check_interval_seconds"]
                time.sleep(interval)
                
            except Exception as e:
                logger.error(f"❌ Eviction scheduler error: {str(e)}")
                time.sleep(60)
    
    def _metrics_collection_loop(self) -> None:
        """Background metrics collection loop"""
        while True:
            try:
                # Collect cache metrics
                self._update_cache_metrics()
                time.sleep(60)  # Update metrics every minute
            except Exception as e:
                logger.error(f"❌ Metrics collection error: {str(e)}")
                time.sleep(60)
    
    def _update_cache_metrics(self) -> None:
        """Update cache performance metrics"""
        try:
            # Calculate hit rate from recent access stats
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.execute("""
                    SELECT COUNT(*) as total, SUM(CAST(hit AS INTEGER)) as hits
                    FROM access_stats 
                    WHERE access_time > datetime('now', '-1 hour')
                """)
                result = cursor.fetchone()
                
                total_requests = result[0] if result[0] else 0
                hits = result[1] if result[1] else 0
                
                hit_rate = hits / total_requests if total_requests > 0 else 0
                miss_rate = 1.0 - hit_rate
                
                # Calculate average load time
                cursor = conn.execute("""
                    SELECT AVG(load_time_ms) 
                    FROM access_stats 
                    WHERE access_time > datetime('now', '-1 hour')
                """)
                avg_load_time = cursor.fetchone()[0] or 0
            
            # Update metrics
            self.cache_metrics = CacheMetrics(
                hit_rate=hit_rate,
                miss_rate=miss_rate,
                eviction_rate=0.0,  # TODO: Calculate from eviction events
                average_load_time=avg_load_time,
                memory_utilization=self._get_current_memory_usage() / (self.config["memory_cache"]["max_size_gb"] * 1024),
                total_requests=total_requests,
                cache_size_mb=self._get_current_memory_usage(),
                active_models=len(self.cache_storage)
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to update cache metrics: {str(e)}")
    
    def _preload_popular_models(self) -> None:
        """Preload popular models into cache"""
        popular_models = self.config["preloading"]["popular_models"]
        
        for model_id in popular_models:
            try:
                # Mock model loader for preloading
                def mock_loader():
                    return f"preloaded_model_{model_id}"
                
                # Preload model
                asyncio.run(self.get_model(model_id, mock_loader))
                logger.info(f"✅ Preloaded popular model: {model_id}")
                
            except Exception as e:
                logger.error(f"❌ Failed to preload model {model_id}: {str(e)}")
    
    async def warmup_model(self, model_id: str, model_loader: Callable) -> None:
        """Warm up model in cache without returning it"""
        try:
            await self._set_model_status(model_id, ModelStatus.WARMING)
            await self._load_and_cache_model(model_id, model_loader)
            logger.info(f"🔥 Model {model_id} warmed up in cache")
        except Exception as e:
            logger.error(f"❌ Failed to warm up model {model_id}: {str(e)}")
    
    async def invalidate_model(self, model_id: str) -> None:
        """Invalidate and remove model from all cache tiers"""
        with self.cache_lock:
            # Remove from memory
            if model_id in self.cache_storage:
                del self.cache_storage[model_id]
            
            if model_id in self.cache_metadata:
                del self.cache_metadata[model_id]
        
        # Remove from SSD
        ssd_path = self._get_ssd_cache_path(model_id)
        if ssd_path.exists():
            ssd_path.unlink()
        
        # Remove from network cache
        if self.redis_client:
            cache_key = self._generate_cache_key(model_id)
            self.redis_client.delete(cache_key)
        
        logger.info(f"🗑️ Model {model_id} invalidated from all cache tiers")
    
    def get_cache_status(self) -> Dict[str, Any]:
        """Get comprehensive cache status"""
        return {
            "memory_cache": {
                "active_models": len(self.cache_storage),
                "total_size_mb": self._get_current_memory_usage(),
                "max_size_mb": self.config["memory_cache"]["max_size_gb"] * 1024,
                "utilization": self._get_current_memory_usage() / (self.config["memory_cache"]["max_size_gb"] * 1024)
            },
            "ssd_cache": {
                "total_size_mb": self._get_current_ssd_usage(),
                "max_size_mb": self.config["ssd_cache"]["max_size_gb"] * 1024,
                "utilization": self._get_current_ssd_usage() / (self.config["ssd_cache"]["max_size_gb"] * 1024)
            },
            "performance_metrics": {
                "hit_rate": self.cache_metrics.hit_rate,
                "miss_rate": self.cache_metrics.miss_rate,
                "average_load_time_ms": self.cache_metrics.average_load_time,
                "total_requests": self.cache_metrics.total_requests
            },
            "recent_models": [
                {
                    "model_id": model.model_id,
                    "size_mb": model.model_size_mb,
                    "last_accessed": model.last_accessed.isoformat(),
                    "access_count": model.access_count,
                    "status": model.status.value
                }
                for model in sorted(self.cache_storage.values(), 
                                  key=lambda x: x.last_accessed, reverse=True)[:10]
            ]
        }
    
    async def cleanup(self) -> None:
        """Cleanup cache manager resources"""
        logger.info("🧹 Cleaning up Model Cache Manager")
        
        # Stop background tasks
        self.monitoring_active = False
        
        # Close Redis connection
        if self.redis_client:
            self.redis_client.close()
        
        # Clear in-memory caches
        with self.cache_lock:
            self.cache_storage.clear()
            self.cache_metadata.clear()
        
        logger.info("✅ Model Cache Manager cleanup completed")

# Example usage and testing
if __name__ == "__main__":
    async def test_model_cache_manager():
        """Test the Model Cache Manager"""
        cache_manager = ModelCacheManager()
        
        # Mock model loader
        def load_test_model():
            import time
            time.sleep(0.1)  # Simulate load time
            return {"model_data": "test_model_weights", "size": 100}
        
        # Test model caching
        print("💾 Testing Model Cache Manager...")
        
        # First access (cache miss)
        start_time = time.time()
        model1 = await cache_manager.get_model("test_model_001", load_test_model)
        first_load_time = time.time() - start_time
        print(f"   First load: {first_load_time:.3f}s")
        
        # Second access (cache hit)
        start_time = time.time()
        model2 = await cache_manager.get_model("test_model_001", load_test_model)
        second_load_time = time.time() - start_time
        print(f"   Second load: {second_load_time:.3f}s")
        
        # Verify speedup
        speedup = first_load_time / second_load_time if second_load_time > 0 else float('inf')
        print(f"   Cache speedup: {speedup:.1f}x")
        
        # Get cache status
        status = cache_manager.get_cache_status()
        print(f"   Active models: {status['memory_cache']['active_models']}")
        print(f"   Hit rate: {status['performance_metrics']['hit_rate']:.2f}")
        
        # Cleanup
        await cache_manager.cleanup()
        print("✅ Model Cache Manager test completed")
    
    # Run test
    asyncio.run(test_model_cache_manager())