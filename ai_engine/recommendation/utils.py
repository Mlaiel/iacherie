"""
Ultra-Advanced Utilities for Enterprise Recommendation System
Production-ready utilities, helpers, and infrastructure components

Copyright (c) 2025 Fahed Mlaiel <mlaiel@live.de>
⚠️  STRICT WARNING: Unauthorized use, copying, or stealing of this concept, 
    code, or intellectual property without explicit written authorization 
    from Fahed Mlaiel is strictly prohibited and will result in legal action.

Lead Developer: Fahed Mlaiel
Development Team Specialties:
- Lead Dev + AI Architect Developer
- Senior Backend Developer (Python/FastAPI/Django)
- Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face)
- DBA & Data Engineer (PostgreSQL/Redis/MongoDB)
- Backend Security Specialist
- Microservices Architect
- Audio Developer
- DevOps Engineer
- AI Prompt Engineer
Email: mlaiel@live.de
"""

import asyncio
import logging
import hashlib
import pickle
import json
import gzip
import time
from typing import Dict, List, Optional, Any, Union, Tuple, Set, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from decimal import Decimal
from functools import wraps, lru_cache
from contextlib import asynccontextmanager
import uuid
import numpy as np
import pandas as pd
from pathlib import Path
import redis
import psycopg2
from sqlalchemy import create_engine, text
import structlog

from .models import (
    RecommendationRequest, RecommendationResponse, 
    ContentRecommendation, UserProfile, ContentFormat, PlatformType
)
from .exceptions import RecommendationError, ValidationError, CacheError
from ..core.base_models import ModelStatus, HealthCheck


logger = structlog.get_logger(__name__)


# Performance monitoring decorators
def measure_performance(operation_name: str):
    """Decorator to measure operation performance"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                execution_time = (time.time() - start_time) * 1000
                logger.info(
                    f"{operation_name} completed successfully",
                    execution_time_ms=execution_time,
                    operation=operation_name
                )
                return result
            except Exception as e:
                execution_time = (time.time() - start_time) * 1000
                logger.error(
                    f"{operation_name} failed",
                    error=str(e),
                    execution_time_ms=execution_time,
                    operation=operation_name
                )
                raise
        return wrapper
    return decorator


def cache_result(ttl_seconds: int = 3600, cache_key_prefix: str = "rec"):
    """Advanced caching decorator with intelligent cache management"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key based on function args
            cache_key = _generate_cache_key(func.__name__, cache_key_prefix, args, kwargs)
            
            # Try to get from cache first
            try:
                cached_result = await _get_from_cache(cache_key)
                if cached_result:
                    logger.debug("Cache hit", cache_key=cache_key, function=func.__name__)
                    return cached_result
            except Exception as e:
                logger.warning("Cache read failed", error=str(e), cache_key=cache_key)
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            
            try:
                await _set_to_cache(cache_key, result, ttl_seconds)
                logger.debug("Result cached", cache_key=cache_key, ttl=ttl_seconds)
            except Exception as e:
                logger.warning("Cache write failed", error=str(e), cache_key=cache_key)
            
            return result
        return wrapper
    return decorator


def validate_request(validation_schema: Dict[str, Any]):
    """Advanced request validation decorator"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Validate request parameters
            request_data = kwargs.get('request') or (args[1] if len(args) > 1 else None)
            
            if request_data:
                validation_errors = await _validate_data(request_data, validation_schema)
                if validation_errors:
                    raise ValidationError(f"Validation errors: {validation_errors}")
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


class ModelManager:
    """Enterprise-grade model management and lifecycle"""
    
    def __init__(self, model_cache_size: int = 10):
        self.model_cache = {}
        self.model_metadata = {}
        self.max_cache_size = model_cache_size
        self.load_times = {}
        self.usage_stats = {}
        self.logger = structlog.get_logger(__name__)
        
    async def load_model(self, model_name: str, model_path: str, force_reload: bool = False) -> Any:
        """Load and cache AI models with intelligent management"""
        if model_name in self.model_cache and not force_reload:
            self.usage_stats[model_name] = self.usage_stats.get(model_name, 0) + 1
            return self.model_cache[model_name]
        
        try:
            start_time = time.time()
            
            # Load model based on type
            if model_path.endswith('.pkl'):
                with open(model_path, 'rb') as f:
                    model = pickle.load(f)
            elif model_path.endswith('.json'):
                with open(model_path, 'r') as f:
                    model = json.load(f)
            else:
                # Assume it's a Hugging Face model
                from transformers import AutoModel
                model = AutoModel.from_pretrained(model_path)
            
            load_time = time.time() - start_time
            
            # Manage cache size
            if len(self.model_cache) >= self.max_cache_size:
                await self._evict_least_used_model()
            
            # Cache the model
            self.model_cache[model_name] = model
            self.load_times[model_name] = load_time
            self.usage_stats[model_name] = 1
            self.model_metadata[model_name] = {
                'path': model_path,
                'loaded_at': datetime.now(),
                'load_time_seconds': load_time,
                'memory_usage_mb': self._estimate_model_size(model)
            }
            
            self.logger.info(
                "Model loaded successfully",
                model_name=model_name,
                load_time_ms=load_time * 1000,
                cache_size=len(self.model_cache)
            )
            
            return model
            
        except Exception as e:
            self.logger.error("Failed to load model", model_name=model_name, error=str(e))
            raise RecommendationError(f"Model loading failed: {str(e)}")
    
    async def _evict_least_used_model(self):
        """Evict the least used model from cache"""
        if not self.model_cache:
            return
            
        least_used_model = min(self.usage_stats.items(), key=lambda x: x[1])
        model_name = least_used_model[0]
        
        del self.model_cache[model_name]
        del self.usage_stats[model_name]
        del self.load_times[model_name]
        del self.model_metadata[model_name]
        
        self.logger.info("Evicted least used model", model_name=model_name)
    
    def _estimate_model_size(self, model: Any) -> float:
        """Estimate model memory usage in MB"""
        try:
            if hasattr(model, 'num_parameters'):
                # For transformers models
                return model.num_parameters() * 4 / (1024 * 1024)  # Assume float32
            elif hasattr(model, '__sizeof__'):
                return model.__sizeof__() / (1024 * 1024)
            else:
                return 0.0
        except:
            return 0.0
    
    def get_model_stats(self) -> Dict[str, Any]:
        """Get comprehensive model statistics"""
        return {
            'cached_models': list(self.model_cache.keys()),
            'cache_size': len(self.model_cache),
            'usage_stats': self.usage_stats.copy(),
            'load_times': self.load_times.copy(),
            'metadata': self.model_metadata.copy(),
            'total_memory_mb': sum(
                meta.get('memory_usage_mb', 0) 
                for meta in self.model_metadata.values()
            )
        }


class PerformanceMonitor:
    """Advanced performance monitoring and alerting system"""
    
    def __init__(self):
        self.metrics = {}
        self.alerts = {}
        self.thresholds = {
            'latency_p95_ms': 500,
            'error_rate': 0.05,
            'cache_hit_ratio': 0.7,
            'memory_usage_mb': 8192,
            'cpu_usage_percent': 80
        }
        self.logger = structlog.get_logger(__name__)
    
    def record_metric(self, metric_name: str, value: float, tags: Dict[str, str] = None):
        """Record a performance metric"""
        timestamp = datetime.now()
        
        if metric_name not in self.metrics:
            self.metrics[metric_name] = []
        
        self.metrics[metric_name].append({
            'value': value,
            'timestamp': timestamp,
            'tags': tags or {}
        })
        
        # Keep only recent metrics (last hour)
        cutoff = timestamp - timedelta(hours=1)
        self.metrics[metric_name] = [
            m for m in self.metrics[metric_name] 
            if m['timestamp'] > cutoff
        ]
        
        # Check for alerts
        self._check_alerts(metric_name, value)
    
    def _check_alerts(self, metric_name: str, value: float):
        """Check if metric value triggers alerts"""
        if metric_name in self.thresholds:
            threshold = self.thresholds[metric_name]
            
            # Different alert logic for different metrics
            if metric_name == 'cache_hit_ratio' and value < threshold:
                self._trigger_alert(metric_name, value, threshold, "below")
            elif metric_name != 'cache_hit_ratio' and value > threshold:
                self._trigger_alert(metric_name, value, threshold, "above")
    
    def _trigger_alert(self, metric_name: str, value: float, threshold: float, condition: str):
        """Trigger performance alert"""
        alert_key = f"{metric_name}_{condition}_threshold"
        
        # Rate limit alerts (max 1 per 5 minutes per metric)
        now = datetime.now()
        if alert_key in self.alerts:
            last_alert = self.alerts[alert_key]
            if (now - last_alert) < timedelta(minutes=5):
                return
        
        self.alerts[alert_key] = now
        
        self.logger.warning(
            "Performance alert triggered",
            metric=metric_name,
            value=value,
            threshold=threshold,
            condition=condition,
            alert_time=now.isoformat()
        )
    
    def get_metrics_summary(self, time_window: timedelta = timedelta(hours=1)) -> Dict[str, Any]:
        """Get comprehensive metrics summary"""
        cutoff = datetime.now() - time_window
        summary = {}
        
        for metric_name, values in self.metrics.items():
            recent_values = [
                v['value'] for v in values 
                if v['timestamp'] > cutoff
            ]
            
            if recent_values:
                summary[metric_name] = {
                    'count': len(recent_values),
                    'mean': np.mean(recent_values),
                    'median': np.median(recent_values),
                    'p95': np.percentile(recent_values, 95),
                    'p99': np.percentile(recent_values, 99),
                    'min': np.min(recent_values),
                    'max': np.max(recent_values),
                    'std': np.std(recent_values)
                }
        
        return {
            'metrics': summary,
            'time_window_hours': time_window.total_seconds() / 3600,
            'alert_count': len(self.alerts),
            'recent_alerts': [
                {
                    'alert': alert_key,
                    'triggered_at': timestamp.isoformat()
                }
                for alert_key, timestamp in self.alerts.items()
                if (datetime.now() - timestamp) < time_window
            ]
        }


class DataValidator:
    """Enterprise-grade data validation and sanitization"""
    
    @staticmethod
    def validate_user_profile(profile: UserProfile) -> List[str]:
        """Validate user profile data"""
        errors = []
        
        if not profile.user_id:
            errors.append("user_id is required")
        
        if not profile.username:
            errors.append("username is required")
        
        if profile.personalization_level < 0 or profile.personalization_level > 1:
            errors.append("personalization_level must be between 0 and 1")
        
        if profile.influence_score < 0:
            errors.append("influence_score must be non-negative")
        
        return errors
    
    @staticmethod
    def validate_recommendation_request(request: RecommendationRequest) -> List[str]:
        """Validate recommendation request data"""
        errors = []
        
        if not request.user_id:
            errors.append("user_id is required")
        
        if request.max_results <= 0:
            errors.append("max_results must be positive")
        
        if not 0 <= request.min_confidence_score <= 1:
            errors.append("min_confidence_score must be between 0 and 1")
        
        if not 0 <= request.diversification_factor <= 1:
            errors.append("diversification_factor must be between 0 and 1")
        
        if not 0 <= request.novelty_factor <= 1:
            errors.append("novelty_factor must be between 0 and 1")
        
        return errors
    
    @staticmethod
    def sanitize_text_input(text: str) -> str:
        """Sanitize text input for security"""
        if not text:
            return ""
        
        # Remove potential XSS/injection attempts
        import re
        text = re.sub(r'<[^>]*>', '', text)  # Remove HTML tags
        text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)  # Remove javascript
        text = re.sub(r'on\w+\s*=', '', text, flags=re.IGNORECASE)  # Remove event handlers
        
        return text.strip()


class CacheManager:
    """Enterprise-grade caching management system"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis_client = None
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'errors': 0
        }
        self.logger = structlog.get_logger(__name__)
    
    async def initialize(self):
        """Initialize cache connection"""
        try:
            import aioredis
            self.redis_client = await aioredis.from_url(self.redis_url)
            await self.redis_client.ping()
            self.logger.info("Cache manager initialized successfully")
        except Exception as e:
            self.logger.error("Failed to initialize cache", error=str(e))
            raise CacheError(f"Cache initialization failed: {str(e)}")
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            if not self.redis_client:
                return None
                
            cached_data = await self.redis_client.get(key)
            
            if cached_data:
                self.cache_stats['hits'] += 1
                # Decompress and deserialize
                decompressed = gzip.decompress(cached_data)
                return pickle.loads(decompressed)
            else:
                self.cache_stats['misses'] += 1
                return None
                
        except Exception as e:
            self.cache_stats['errors'] += 1
            self.logger.warning("Cache get failed", key=key, error=str(e))
            return None
    
    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache with compression"""
        try:
            if not self.redis_client:
                return False
            
            # Serialize and compress
            serialized = pickle.dumps(value)
            compressed = gzip.compress(serialized)
            
            await self.redis_client.setex(key, ttl, compressed)
            self.cache_stats['sets'] += 1
            return True
            
        except Exception as e:
            self.cache_stats['errors'] += 1
            self.logger.warning("Cache set failed", key=key, error=str(e))
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            if not self.redis_client:
                return False
            
            result = await self.redis_client.delete(key)
            return bool(result)
            
        except Exception as e:
            self.logger.warning("Cache delete failed", key=key, error=str(e))
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        try:
            if not self.redis_client:
                return 0
            
            keys = await self.redis_client.keys(pattern)
            if keys:
                return await self.redis_client.delete(*keys)
            return 0
            
        except Exception as e:
            self.logger.warning("Cache clear pattern failed", pattern=pattern, error=str(e))
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
        hit_ratio = self.cache_stats['hits'] / total_requests if total_requests > 0 else 0
        
        return {
            'stats': self.cache_stats.copy(),
            'hit_ratio': hit_ratio,
            'total_requests': total_requests,
            'error_rate': self.cache_stats['errors'] / max(total_requests, 1)
        }
    
    async def health_check(self) -> HealthCheck:
        """Check cache health"""
        try:
            if not self.redis_client:
                return HealthCheck(
                    healthy=False,
                    status="disconnected",
                    message="Redis client not initialized"
                )
            
            # Test connection with ping
            await self.redis_client.ping()
            
            # Get Redis info
            info = await self.redis_client.info()
            memory_usage = info.get('used_memory', 0)
            max_memory = info.get('maxmemory', 0)
            
            memory_usage_percent = (memory_usage / max_memory * 100) if max_memory > 0 else 0
            
            is_healthy = memory_usage_percent < 90  # Alert if memory usage > 90%
            
            return HealthCheck(
                healthy=is_healthy,
                status="connected" if is_healthy else "degraded",
                message=f"Memory usage: {memory_usage_percent:.1f}%",
                metrics={
                    'memory_usage_bytes': memory_usage,
                    'memory_usage_percent': memory_usage_percent,
                    'cache_stats': self.get_stats()
                }
            )
            
        except Exception as e:
            return HealthCheck(
                healthy=False,
                status="error",
                message=str(e)
            )


# Utility Functions
def generate_cache_key(*args, **kwargs) -> str:
    """Generate deterministic cache key from arguments"""
    key_data = {
        'args': str(args),
        'kwargs': sorted(kwargs.items())
    }
    key_string = json.dumps(key_data, sort_keys=True)
    return hashlib.sha256(key_string.encode()).hexdigest()[:16]


def calculate_similarity(vector1: np.ndarray, vector2: np.ndarray) -> float:
    """Calculate cosine similarity between two vectors"""
    try:
        # Handle zero vectors
        if np.linalg.norm(vector1) == 0 or np.linalg.norm(vector2) == 0:
            return 0.0
        
        similarity = np.dot(vector1, vector2) / (np.linalg.norm(vector1) * np.linalg.norm(vector2))
        return float(np.clip(similarity, -1, 1))  # Ensure value is in [-1, 1]
        
    except Exception as e:
        logger.warning("Similarity calculation failed", error=str(e))
        return 0.0


def normalize_scores(scores: List[float]) -> List[float]:
    """Normalize scores to [0, 1] range"""
    if not scores:
        return []
    
    scores = np.array(scores)
    min_score = np.min(scores)
    max_score = np.max(scores)
    
    if max_score - min_score == 0:
        return [0.5] * len(scores)  # All scores are the same
    
    normalized = (scores - min_score) / (max_score - min_score)
    return normalized.tolist()


def weighted_score(scores: Dict[str, float], weights: Dict[str, float]) -> float:
    """Calculate weighted average score"""
    if not scores or not weights:
        return 0.0
    
    total_weighted_score = 0.0
    total_weight = 0.0
    
    for metric, score in scores.items():
        weight = weights.get(metric, 0.0)
        total_weighted_score += score * weight
        total_weight += weight
    
    return total_weighted_score / total_weight if total_weight > 0 else 0.0


async def initialize_models() -> bool:
    """Initialize all recommendation models"""
    try:
        logger.info("Starting model initialization process")
        
        # Initialize model manager
        model_manager = ModelManager()
        
        # List of models to load
        models_to_load = [
            ('content_embeddings', 'sentence-transformers/all-MiniLM-L6-v2'),
            ('sentiment_analyzer', 'cardiffnlp/twitter-roberta-base-sentiment-latest'),
            ('genre_classifier', 'models/music_genre_classifier.pkl'),
            ('engagement_predictor', 'models/engagement_predictor.pkl'),
            ('viral_predictor', 'models/viral_predictor.pkl')
        ]
        
        # Load models concurrently
        load_tasks = [
            model_manager.load_model(name, path)
            for name, path in models_to_load
        ]
        
        results = await asyncio.gather(*load_tasks, return_exceptions=True)
        
        # Check for failures
        failed_models = [
            (models_to_load[i][0], str(results[i]))
            for i, result in enumerate(results)
            if isinstance(result, Exception)
        ]
        
        if failed_models:
            logger.error("Some models failed to load", failed_models=failed_models)
            return False
        
        logger.info(
            "All models initialized successfully",
            models_loaded=len(models_to_load),
            stats=model_manager.get_model_stats()
        )
        
        return True
        
    except Exception as e:
        logger.error("Model initialization failed", error=str(e))
        return False


async def health_check() -> Dict[str, Any]:
    """Comprehensive system health check"""
    health_status = {
        'overall_healthy': True,
        'timestamp': datetime.now().isoformat(),
        'components': {}
    }
    
    try:
        # Check cache health
        cache_manager = CacheManager()
        await cache_manager.initialize()
        cache_health = await cache_manager.health_check()
        health_status['components']['cache'] = asdict(cache_health)
        
        if not cache_health.healthy:
            health_status['overall_healthy'] = False
        
        # Check model availability
        model_manager = ModelManager()
        model_stats = model_manager.get_model_stats()
        health_status['components']['models'] = {
            'healthy': len(model_stats['cached_models']) > 0,
            'cached_models': model_stats['cached_models'],
            'total_memory_mb': model_stats['total_memory_mb']
        }
        
        # Check performance metrics
        perf_monitor = PerformanceMonitor()
        perf_summary = perf_monitor.get_metrics_summary()
        health_status['components']['performance'] = {
            'healthy': perf_summary['alert_count'] == 0,
            'metrics_available': len(perf_summary['metrics']) > 0,
            'alert_count': perf_summary['alert_count']
        }
        
        # Overall health determination
        unhealthy_components = [
            name for name, comp in health_status['components'].items()
            if not comp.get('healthy', True)
        ]
        
        health_status['overall_healthy'] = len(unhealthy_components) == 0
        health_status['unhealthy_components'] = unhealthy_components
        
    except Exception as e:
        health_status['overall_healthy'] = False
        health_status['error'] = str(e)
        logger.error("Health check failed", error=str(e))
    
    return health_status


def performance_metrics() -> Dict[str, Any]:
    """Get comprehensive performance metrics"""
    perf_monitor = PerformanceMonitor()
    return perf_monitor.get_metrics_summary()


async def recommendation_validator(recommendations: List[ContentRecommendation]) -> List[str]:
    """Validate recommendation quality and consistency"""
    errors = []
    
    if not recommendations:
        errors.append("No recommendations provided")
        return errors
    
    # Check for duplicate recommendations
    content_ids = [rec.content_id for rec in recommendations]
    if len(content_ids) != len(set(content_ids)):
        errors.append("Duplicate recommendations found")
    
    # Validate individual recommendations
    for i, rec in enumerate(recommendations):
        if not rec.content_id:
            errors.append(f"Recommendation {i}: content_id is required")
        
        if not 0 <= rec.confidence_score <= 1:
            errors.append(f"Recommendation {i}: confidence_score must be between 0 and 1")
        
        if not 0 <= rec.relevance_score <= 1:
            errors.append(f"Recommendation {i}: relevance_score must be between 0 and 1")
        
        if rec.predicted_views < 0:
            errors.append(f"Recommendation {i}: predicted_views cannot be negative")
    
    return errors


# Helper functions for internal use
async def _validate_data(data: Any, schema: Dict[str, Any]) -> List[str]:
    """Internal data validation helper"""
    errors = []
    # Implementation would depend on specific validation schema format
    return errors


async def _get_from_cache(cache_key: str) -> Optional[Any]:
    """Internal cache retrieval helper"""
    # This would use the global cache manager instance
    return None


async def _set_to_cache(cache_key: str, value: Any, ttl: int) -> bool:
    """Internal cache storage helper"""
    # This would use the global cache manager instance
    return True


def _generate_cache_key(func_name: str, prefix: str, args: tuple, kwargs: dict) -> str:
    """Internal cache key generation helper"""
    return generate_cache_key(func_name, prefix, args, kwargs)

import asyncio
import logging
import os
import json
import pickle
import hashlib
import time
import psutil
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import numpy as np
from pathlib import Path
try:
    import aioredis
except ImportError:
    aioredis = None
try:
    import aiofiles
except ImportError:
    aiofiles = None
from concurrent.futures import ThreadPoolExecutor
import functools

from .models import (
    ContentRecommendation,
    CreatorProfile,
    Platform,
    ContentType,
    CollaborationMatch,
    TrendInsight,
    RevenueStrategy
)
from .exceptions import RecommendationError, ValidationError
from ..core.base_models import ModelStatus


@dataclass
class SystemHealth:
    """System health status"""
    status: str = "unknown"
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    disk_usage: float = 0.0
    active_connections: int = 0
    cache_hit_ratio: float = 0.0
    model_status: Dict[str, str] = None
    last_check: datetime = None
    uptime: timedelta = None
    error_rate: float = 0.0
    response_time: float = 0.0


@dataclass
class PerformanceMetrics:
    """Performance metrics tracking"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    peak_response_time: float = 0.0
    requests_per_second: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0
    model_predictions: int = 0
    recommendation_accuracy: float = 0.0
    user_satisfaction: float = 0.0
    system_errors: List[str] = None


class ModelManager:
    """
    Model lifecycle management and initialization
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.models = {}
        self.model_status = {}
        self.initialization_lock = asyncio.Lock()
    
    async def initialize_models(self, config: Dict[str, Any]) -> bool:
        """
        Initialize all AI models for the recommendation system
        
        Args:
            config: Configuration dictionary with model settings
            
        Returns:
            True if all models initialized successfully
        """
        async with self.initialization_lock:
            try:
                self.logger.info("Starting model initialization...")
                
                # Initialize content analysis models
                await self._initialize_content_models(config.get("content_models", {}))
                
                # Initialize collaboration matching models
                await self._initialize_collaboration_models(config.get("collaboration_models", {}))
                
                # Initialize trend analysis models
                await self._initialize_trend_models(config.get("trend_models", {}))
                
                # Initialize revenue optimization models
                await self._initialize_revenue_models(config.get("revenue_models", {}))
                
                # Initialize protection models
                await self._initialize_protection_models(config.get("protection_models", {}))
                
                # Validate all models
                validation_results = await self._validate_all_models()
                
                if all(validation_results.values()):
                    self.logger.info("All models initialized successfully")
                    return True
                else:
                    failed_models = [k for k, v in validation_results.items() if not v]
                    self.logger.error(f"Failed to initialize models: {failed_models}")
                    return False
                    
            except Exception as e:
                self.logger.error(f"Model initialization failed: {str(e)}")
                raise RecommendationError(f"Model initialization failed: {str(e)}")
    
    async def _initialize_content_models(self, config: Dict[str, Any]):
        """Initialize content analysis models"""
        self.logger.info("Initializing content analysis models...")
        
        # NLP models for text analysis
        self.models["text_analyzer"] = await self._load_text_analysis_model(config)
        self.model_status["text_analyzer"] = ModelStatus.READY
        
        # Computer vision models for image analysis
        self.models["image_analyzer"] = await self._load_image_analysis_model(config)
        self.model_status["image_analyzer"] = ModelStatus.READY
        
        # Audio analysis models
        self.models["audio_analyzer"] = await self._load_audio_analysis_model(config)
        self.model_status["audio_analyzer"] = ModelStatus.READY
        
        # Video analysis models
        self.models["video_analyzer"] = await self._load_video_analysis_model(config)
        self.model_status["video_analyzer"] = ModelStatus.READY
    
    async def _initialize_collaboration_models(self, config: Dict[str, Any]):
        """Initialize collaboration matching models"""
        self.logger.info("Initializing collaboration models...")
        
        # Creator similarity models
        self.models["creator_similarity"] = await self._load_creator_similarity_model(config)
        self.model_status["creator_similarity"] = ModelStatus.READY
        
        # Audience overlap models
        self.models["audience_overlap"] = await self._load_audience_overlap_model(config)
        self.model_status["audience_overlap"] = ModelStatus.READY
    
    async def _initialize_trend_models(self, config: Dict[str, Any]):
        """Initialize trend analysis models"""
        self.logger.info("Initializing trend analysis models...")
        
        # Trend detection models
        self.models["trend_detector"] = await self._load_trend_detection_model(config)
        self.model_status["trend_detector"] = ModelStatus.READY
        
        # Viral prediction models
        self.models["viral_predictor"] = await self._load_viral_prediction_model(config)
        self.model_status["viral_predictor"] = ModelStatus.READY
    
    async def _initialize_revenue_models(self, config: Dict[str, Any]):
        """Initialize revenue optimization models"""
        self.logger.info("Initializing revenue optimization models...")
        
        # Revenue prediction models
        self.models["revenue_predictor"] = await self._load_revenue_prediction_model(config)
        self.model_status["revenue_predictor"] = ModelStatus.READY
    
    async def _initialize_protection_models(self, config: Dict[str, Any]):
        """Initialize content protection models"""
        self.logger.info("Initializing protection models...")
        
        # Content fingerprinting models
        self.models["fingerprinter"] = await self._load_fingerprinting_model(config)
        self.model_status["fingerprinter"] = ModelStatus.READY
    
    async def _load_text_analysis_model(self, config: Dict[str, Any]):
        """Load text analysis model"""
        # Placeholder for actual model loading
        return {"model": "text_analyzer", "status": "loaded"}
    
    async def _load_image_analysis_model(self, config: Dict[str, Any]):
        """Load image analysis model"""
        # Placeholder for actual model loading
        return {"model": "image_analyzer", "status": "loaded"}
    
    async def _load_audio_analysis_model(self, config: Dict[str, Any]):
        """Load audio analysis model"""
        # Placeholder for actual model loading
        return {"model": "audio_analyzer", "status": "loaded"}
    
    async def _load_video_analysis_model(self, config: Dict[str, Any]):
        """Load video analysis model"""
        # Placeholder for actual model loading
        return {"model": "video_analyzer", "status": "loaded"}
    
    async def _load_creator_similarity_model(self, config: Dict[str, Any]):
        """Load creator similarity model"""
        # Placeholder for actual model loading
        return {"model": "creator_similarity", "status": "loaded"}
    
    async def _load_audience_overlap_model(self, config: Dict[str, Any]):
        """Load audience overlap model"""
        # Placeholder for actual model loading
        return {"model": "audience_overlap", "status": "loaded"}
    
    async def _load_trend_detection_model(self, config: Dict[str, Any]):
        """Load trend detection model"""
        # Placeholder for actual model loading
        return {"model": "trend_detector", "status": "loaded"}
    
    async def _load_viral_prediction_model(self, config: Dict[str, Any]):
        """Load viral prediction model"""
        # Placeholder for actual model loading
        return {"model": "viral_predictor", "status": "loaded"}
    
    async def _load_revenue_prediction_model(self, config: Dict[str, Any]):
        """Load revenue prediction model"""
        # Placeholder for actual model loading
        return {"model": "revenue_predictor", "status": "loaded"}
    
    async def _load_fingerprinting_model(self, config: Dict[str, Any]):
        """Load content fingerprinting model"""
        # Placeholder for actual model loading
        return {"model": "fingerprinter", "status": "loaded"}
    
    async def _validate_all_models(self) -> Dict[str, bool]:
        """Validate all loaded models"""
        validation_results = {}
        
        for model_name, model in self.models.items():
            try:
                # Perform basic validation
                is_valid = model is not None and model.get("status") == "loaded"
                validation_results[model_name] = is_valid
                
                if is_valid:
                    self.logger.info(f"Model {model_name} validated successfully")
                else:
                    self.logger.error(f"Model {model_name} validation failed")
                    
            except Exception as e:
                self.logger.error(f"Error validating model {model_name}: {str(e)}")
                validation_results[model_name] = False
        
        return validation_results
    
    def get_model_status(self) -> Dict[str, str]:
        """Get status of all models"""
        return {name: status.value for name, status in self.model_status.items()}


class HealthChecker:
    """
    System health monitoring and diagnostics
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.health_history = []
        self.alert_thresholds = {
            "cpu_usage": 80.0,
            "memory_usage": 85.0,
            "disk_usage": 90.0,
            "error_rate": 5.0,
            "response_time": 5.0
        }
    
    async def health_check(self, components: Optional[List[str]] = None) -> SystemHealth:
        """
        Perform comprehensive system health check
        
        Args:
            components: Specific components to check, or None for all
            
        Returns:
            SystemHealth object with current system status
        """
        try:
            self.logger.info("Performing system health check...")
            
            health = SystemHealth()
            health.last_check = datetime.now()
            
            # Check system resources
            health.cpu_usage = psutil.cpu_percent(interval=1)
            health.memory_usage = psutil.virtual_memory().percent
            health.disk_usage = psutil.disk_usage('/').percent
            
            # Check system uptime
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            health.uptime = datetime.now() - boot_time
            
            # Check model status (placeholder)
            health.model_status = {"all_models": "healthy"}
            
            # Calculate overall health status
            health.status = self._calculate_health_status(health)
            
            # Store health history
            self.health_history.append(health)
            
            # Keep only last 100 health checks
            if len(self.health_history) > 100:
                self.health_history = self.health_history[-100:]
            
            self.logger.info(f"Health check completed - Status: {health.status}")
            return health
            
        except Exception as e:
            self.logger.error(f"Health check failed: {str(e)}")
            return SystemHealth(status="error", last_check=datetime.now())
    
    def _calculate_health_status(self, health: SystemHealth) -> str:
        """Calculate overall health status based on metrics"""
        critical_issues = 0
        warning_issues = 0
        
        # Check CPU usage
        if health.cpu_usage > self.alert_thresholds["cpu_usage"]:
            critical_issues += 1
        elif health.cpu_usage > self.alert_thresholds["cpu_usage"] * 0.8:
            warning_issues += 1
        
        # Check memory usage
        if health.memory_usage > self.alert_thresholds["memory_usage"]:
            critical_issues += 1
        elif health.memory_usage > self.alert_thresholds["memory_usage"] * 0.8:
            warning_issues += 1
        
        # Check disk usage
        if health.disk_usage > self.alert_thresholds["disk_usage"]:
            critical_issues += 1
        elif health.disk_usage > self.alert_thresholds["disk_usage"] * 0.8:
            warning_issues += 1
        
        # Determine overall status
        if critical_issues > 0:
            return "critical"
        elif warning_issues > 1:
            return "warning"
        else:
            return "healthy"
    
    async def get_health_trend(self, hours: int = 24) -> Dict[str, Any]:
        """Get health trends over specified time period"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_health = [h for h in self.health_history if h.last_check >= cutoff_time]
        
        if not recent_health:
            return {"error": "No health data available for specified period"}
        
        trend = {
            "period_hours": hours,
            "data_points": len(recent_health),
            "average_cpu": np.mean([h.cpu_usage for h in recent_health]),
            "average_memory": np.mean([h.memory_usage for h in recent_health]),
            "average_disk": np.mean([h.disk_usage for h in recent_health]),
            "status_distribution": {}
        }
        
        # Calculate status distribution
        status_counts = {}
        for health in recent_health:
            status_counts[health.status] = status_counts.get(health.status, 0) + 1
        
        total_points = len(recent_health)
        trend["status_distribution"] = {
            status: (count / total_points) * 100 
            for status, count in status_counts.items()
        }
        
        return trend


class PerformanceTracker:
    """
    Performance metrics tracking and analysis
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.metrics = PerformanceMetrics(system_errors=[])
        self.response_times = []
        self.start_time = datetime.now()
    
    def track_request(self, success: bool, response_time: float):
        """Track a request and its performance"""
        self.metrics.total_requests += 1
        
        if success:
            self.metrics.successful_requests += 1
        else:
            self.metrics.failed_requests += 1
        
        # Update response time metrics
        self.response_times.append(response_time)
        self.metrics.average_response_time = np.mean(self.response_times)
        self.metrics.peak_response_time = max(self.response_times)
        
        # Calculate requests per second
        elapsed_time = (datetime.now() - self.start_time).total_seconds()
        if elapsed_time > 0:
            self.metrics.requests_per_second = self.metrics.total_requests / elapsed_time
        
        # Keep only last 1000 response times for memory efficiency
        if len(self.response_times) > 1000:
            self.response_times = self.response_times[-1000:]
    
    def track_cache_hit(self):
        """Track cache hit"""
        self.metrics.cache_hits += 1
    
    def track_cache_miss(self):
        """Track cache miss"""
        self.metrics.cache_misses += 1
    
    def get_cache_hit_ratio(self) -> float:
        """Calculate cache hit ratio"""
        total_cache_requests = self.metrics.cache_hits + self.metrics.cache_misses
        if total_cache_requests == 0:
            return 0.0
        return self.metrics.cache_hits / total_cache_requests
    
    def get_metrics(self) -> PerformanceMetrics:
        """Get current performance metrics"""
        # Update cache hit ratio
        if hasattr(self.metrics, 'cache_hit_ratio'):
            self.metrics.cache_hit_ratio = self.get_cache_hit_ratio()
        
        return self.metrics


class RecommendationValidator:
    """
    Validation utilities for recommendation system
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def validate_creator_profile(self, profile: CreatorProfile) -> Dict[str, Any]:
        """
        Validate creator profile for completeness and correctness
        
        Args:
            profile: Creator profile to validate
            
        Returns:
            Validation result with errors and warnings
        """
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "suggestions": []
        }
        
        # Required field validation
        required_fields = ["creator_id", "display_name", "platforms"]
        for field in required_fields:
            if not getattr(profile, field, None):
                validation_result["errors"].append(f"Missing required field: {field}")
                validation_result["is_valid"] = False
        
        # Platform validation
        if profile.platforms:
            valid_platforms = set(Platform)
            for platform in profile.platforms:
                if platform not in valid_platforms:
                    validation_result["errors"].append(f"Invalid platform: {platform}")
                    validation_result["is_valid"] = False
        
        # Follower count validation
        if profile.followers_count:
            for platform, count in profile.followers_count.items():
                if count < 0:
                    validation_result["errors"].append(f"Invalid follower count for {platform}: {count}")
                    validation_result["is_valid"] = False
        
        # Engagement rate validation
        if profile.engagement_rate:
            for platform, rate in profile.engagement_rate.items():
                if not 0 <= rate <= 1:
                    validation_result["errors"].append(f"Invalid engagement rate for {platform}: {rate}")
                    validation_result["is_valid"] = False
        
        # Content type validation
        if profile.content_types:
            valid_content_types = set(ContentType)
            for content_type in profile.content_types:
                if content_type not in valid_content_types:
                    validation_result["errors"].append(f"Invalid content type: {content_type}")
                    validation_result["is_valid"] = False
        
        # Warnings for missing optional but important fields
        if not profile.genres:
            validation_result["warnings"].append("No genres specified - may limit recommendation accuracy")
        
        if not profile.target_audience:
            validation_result["warnings"].append("No target audience specified - may limit personalization")
        
        # Suggestions for improvement
        if profile.followers_count and sum(profile.followers_count.values()) < 1000:
            validation_result["suggestions"].append("Consider growing follower base for better monetization opportunities")
        
        if not profile.bio or len(profile.bio) < 50:
            validation_result["suggestions"].append("Add a comprehensive bio to improve profile matching")
        
        return validation_result
    
    async def validate_recommendation(self, recommendation: ContentRecommendation) -> Dict[str, Any]:
        """
        Validate content recommendation for quality and completeness
        
        Args:
            recommendation: Content recommendation to validate
            
        Returns:
            Validation result
        """
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "quality_score": 0.0
        }
        
        # Required field validation
        required_fields = ["recommendation_id", "content_type", "title", "description"]
        for field in required_fields:
            if not getattr(recommendation, field, None):
                validation_result["errors"].append(f"Missing required field: {field}")
                validation_result["is_valid"] = False
        
        # Score validation
        score_fields = ["relevance_score", "engagement_prediction", "viral_potential", "monetization_potential"]
        for field in score_fields:
            score = getattr(recommendation, field, None)
            if score is not None and not 0 <= score <= 1:
                validation_result["errors"].append(f"Invalid score for {field}: {score}")
                validation_result["is_valid"] = False
        
        # Content validation
        if recommendation.title and len(recommendation.title) < 5:
            validation_result["warnings"].append("Title is very short - may not be engaging")
        
        if recommendation.description and len(recommendation.description) < 20:
            validation_result["warnings"].append("Description is very short - may lack detail")
        
        # Calculate quality score
        quality_factors = []
        
        if recommendation.relevance_score:
            quality_factors.append(recommendation.relevance_score)
        
        if recommendation.engagement_prediction:
            quality_factors.append(recommendation.engagement_prediction)
        
        if recommendation.explanations and len(recommendation.explanations) > 0:
            quality_factors.append(0.8)  # Has explanations
        
        if recommendation.hashtags and len(recommendation.hashtags) > 0:
            quality_factors.append(0.7)  # Has hashtags
        
        validation_result["quality_score"] = np.mean(quality_factors) if quality_factors else 0.0
        
        return validation_result


# Utility functions

def timing_decorator(func):
    """Decorator to time function execution"""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            end_time = time.time()
            execution_time = end_time - start_time
            logging.getLogger(__name__).info(f"Function {func.__name__} took {execution_time:.4f} seconds")
    
    return wrapper


def cache_result(ttl_seconds: int = 300):
    """Decorator to cache function results with TTL"""
    def decorator(func):
        cache = {}
        
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Check if result is in cache and not expired
            if cache_key in cache:
                result, timestamp = cache[cache_key]
                if time.time() - timestamp < ttl_seconds:
                    return result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            cache[cache_key] = (result, time.time())
            
            # Clean up old cache entries
            current_time = time.time()
            expired_keys = [k for k, (_, ts) in cache.items() if current_time - ts > ttl_seconds]
            for key in expired_keys:
                del cache[key]
            
            return result
        
        return wrapper
    return decorator


async def safe_json_load(file_path: str) -> Optional[Dict[str, Any]]:
    """Safely load JSON file with error handling"""
    try:
        async with aiofiles.open(file_path, 'r') as f:
            content = await f.read()
            return json.loads(content)
    except FileNotFoundError:
        logging.getLogger(__name__).warning(f"File not found: {file_path}")
        return None
    except json.JSONDecodeError as e:
        logging.getLogger(__name__).error(f"JSON decode error in {file_path}: {str(e)}")
        return None
    except Exception as e:
        logging.getLogger(__name__).error(f"Error loading {file_path}: {str(e)}")
        return None


async def safe_json_save(data: Any, file_path: str) -> bool:
    """Safely save data to JSON file"""
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        async with aiofiles.open(file_path, 'w') as f:
            await f.write(json.dumps(data, indent=2, default=str))
        return True
    except Exception as e:
        logging.getLogger(__name__).error(f"Error saving to {file_path}: {str(e)}")
        return False


def sanitize_input(text: str, max_length: int = 1000) -> str:
    """Sanitize user input text"""
    if not isinstance(text, str):
        return ""
    
    # Remove potentially harmful characters
    sanitized = text.replace("<", "&lt;").replace(">", "&gt;")
    
    # Limit length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + "..."
    
    return sanitized.strip()


def calculate_similarity(vector1: List[float], vector2: List[float]) -> float:
    """Calculate cosine similarity between two vectors"""
    try:
        v1 = np.array(vector1)
        v2 = np.array(vector2)
        
        # Calculate cosine similarity
        dot_product = np.dot(v1, v2)
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    except Exception:
        return 0.0


def generate_content_hash(content: Dict[str, Any]) -> str:
    """Generate consistent hash for content"""
    # Create a normalized string representation
    content_str = json.dumps(content, sort_keys=True, default=str)
    return hashlib.sha256(content_str.encode()).hexdigest()


async def batch_process(
    items: List[Any],
    processor: Callable,
    batch_size: int = 10,
    max_workers: int = 4
) -> List[Any]:
    """Process items in batches with concurrency control"""
    results = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            
            # Process batch concurrently
            futures = [executor.submit(processor, item) for item in batch]
            
            # Collect results
            for future in futures:
                try:
                    result = future.result(timeout=30)  # 30-second timeout
                    results.append(result)
                except Exception as e:
                    logging.getLogger(__name__).error(f"Batch processing error: {str(e)}")
                    results.append(None)
    
    return results


def format_duration(seconds: float) -> str:
    """Format duration in seconds to human-readable string"""
    if seconds < 60:
        return f"{seconds:.2f} seconds"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f} minutes"
    else:
        hours = seconds / 3600
        return f"{hours:.1f} hours"


def format_number(number: Union[int, float], precision: int = 2) -> str:
    """Format number with appropriate units (K, M, B)"""
    if number < 1000:
        return str(number)
    elif number < 1000000:
        return f"{number/1000:.{precision}f}K"
    elif number < 1000000000:
        return f"{number/1000000:.{precision}f}M"
    else:
        return f"{number/1000000000:.{precision}f}B"


async def validate_url(url: str) -> bool:
    """Validate if URL is accessible"""
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.head(url, timeout=10) as response:
                return response.status < 400
    except Exception:
        return False


def extract_hashtags(text: str) -> List[str]:
    """Extract hashtags from text"""
    import re
    hashtag_pattern = r'#\w+'
    hashtags = re.findall(hashtag_pattern, text)
    return [tag.lower() for tag in hashtags]


def extract_mentions(text: str) -> List[str]:
    """Extract mentions from text"""
    import re
    mention_pattern = r'@\w+'
    mentions = re.findall(mention_pattern, text)
    return [mention.lower() for mention in mentions]


def normalize_platform_name(platform_name: str) -> Optional[Platform]:
    """Normalize platform name to Platform enum"""
    platform_mapping = {
        "youtube": Platform.YOUTUBE,
        "yt": Platform.YOUTUBE,
        "tiktok": Platform.TIKTOK,
        "tt": Platform.TIKTOK,
        "instagram": Platform.INSTAGRAM,
        "ig": Platform.INSTAGRAM,
        "insta": Platform.INSTAGRAM,
        "twitter": Platform.TWITTER,
        "x": Platform.TWITTER,
        "facebook": Platform.FACEBOOK,
        "fb": Platform.FACEBOOK,
        "linkedin": Platform.LINKEDIN,
        "snapchat": Platform.SNAPCHAT,
        "twitch": Platform.TWITCH,
        "discord": Platform.DISCORD,
        "reddit": Platform.REDDIT,
        "pinterest": Platform.PINTEREST
    }
    
    normalized = platform_name.lower().strip()
    return platform_mapping.get(normalized)


# Initialize module-level components
model_manager = ModelManager()
health_checker = HealthChecker()
performance_tracker = PerformanceTracker()
recommendation_validator = RecommendationValidator()


# Public API functions

async def initialize_models(config: Optional[Dict[str, Any]] = None) -> bool:
    """
    Initialize all AI models for the recommendation system
    
    Args:
        config: Optional configuration for model initialization
        
    Returns:
        True if initialization successful
    """
    if config is None:
        config = {
            "content_models": {},
            "collaboration_models": {},
            "trend_models": {},
            "revenue_models": {},
            "protection_models": {}
        }
    
    return await model_manager.initialize_models(config)


async def health_check(components: Optional[List[str]] = None) -> SystemHealth:
    """
    Perform system health check
    
    Args:
        components: Specific components to check
        
    Returns:
        SystemHealth object
    """
    return await health_checker.health_check(components)


async def performance_metrics() -> PerformanceMetrics:
    """
    Get current performance metrics
    
    Returns:
        PerformanceMetrics object
    """
    return performance_tracker.get_metrics()


async def recommendation_validator_check(recommendation: ContentRecommendation) -> Dict[str, Any]:
    """
    Validate a content recommendation
    
    Args:
        recommendation: Recommendation to validate
        
    Returns:
        Validation result
    """
    return await recommendation_validator.validate_recommendation(recommendation)
