"""
Advanced Multi-Platform Personalization Utilities & Performance Optimization

Ultra-sophisticated utility library providing advanced tools, validators, optimizers,
and performance enhancers for multi-format content creator personalization platform.

Business Logic Integration:
Data Validation → Performance Optimization → Caching Strategies → Security Utils →
Analytics Helpers → Content Processing → Feature Engineering → Model Optimization →
Multi-Platform Integration → Monitoring & Debugging

Advanced Features:
- High-Performance Caching (Redis, Memory, Hybrid)
- Advanced Data Validation & Schema Enforcement
- Performance Monitoring & Optimization
- Security Utilities & GDPR Compliance
- Multi-Format Content Processing
- Feature Engineering & Data Transformation
- Model Performance Optimization
- Async Processing & Concurrency Management
- Advanced Logging & Debugging
- Multi-Platform API Integration
- Statistical Analysis Utilities
- Machine Learning Helper Functions

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

 STRICT COPYRIGHT WARNING 
This code is the intellectual property of Fahed Mlaiel (mlaiel@live.de).
ANY unauthorized use, reproduction, or distribution is STRICTLY PROHIBITED.
Legal action will be taken against violators under German and international law.
Contact mlaiel@live.de for licensing inquiries.

Team Specialists:
- Lead IA Developer: Fahed Mlaiel (mlaiel@live.de)
- Backend Senior Engineer: Advanced microservices architecture
- ML Engineer: Deep learning & personalization algorithms  
- Database Administrator: High-performance data optimization
- Security Expert: Enterprise-grade protection systems
- Microservices Architect: Scalable distributed systems
- Audio Processing Specialist: Advanced audio AI algorithms
- DevOps Engineer: Production-ready infrastructure
- IA Prompt Engineer: Optimized AI model interactions
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple, Union, Callable, Set, Generator
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import pandas as pd
import json
import hashlib
import re
from collections import defaultdict, Counter, OrderedDict, deque
import time
import functools
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import threading
import multiprocessing as mp
import pickle
import gzip
import base64
import uuid
import asyncio
import aiohttp
import redis
from urllib.parse import urlparse, quote, unquote
import mimetypes
import magic
from PIL import Image
import librosa
import cv2
from textblob import TextBlob
import spacy
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score
import torch
import tensorflow as tf
import psutil
import sys
import os

from .core import UserProfile, ContentType, PersonalizationType
from .exceptions import PersonalizationError, ValidationError, PerformanceError, SecurityError


class ValidationLevel(Enum):
    """Validation strictness levels"""
    STRICT = "strict"
    MODERATE = "moderate"
    LENIENT = "lenient"
    DISABLED = "disabled"


class CacheStrategy(Enum):
    """Caching strategies for personalization data"""
    LRU = "lru"
    FIFO = "fifo"
    LIFO = "lifo"
    RANDOM = "random"
    TTL = "ttl"
    ADAPTIVE = "adaptive"


@dataclass
class PerformanceMetrics:
    """Performance metrics for operations"""
    
    execution_time: float
    memory_usage: float
    cache_hit_rate: float
    error_rate: float
    
    # Detailed timing
    processing_time: float = 0.0
    io_time: float = 0.0
    network_time: float = 0.0
    
    # Resource utilization
    cpu_usage: float = 0.0
    memory_peak: float = 0.0
    
    # Operation metadata
    operation_name: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    success: bool = True


class DataValidator:
    """
    Comprehensive data validation for personalization inputs.
    
    Features:
    - Schema validation
    - Data type checking
    - Range validation
    - Business rule validation
    - Performance optimization
    """
    
    def __init__(self, validation_level: ValidationLevel = ValidationLevel.MODERATE):
        self.logger = logging.getLogger(__name__)
        self.validation_level = validation_level
        
        # Validation rules cache
        self.validation_rules = self._initialize_validation_rules()
        self.schema_cache = {}
        
        # Performance tracking
        self.validation_stats = defaultdict(int)
        
        self.logger.info(f"Data validator initialized with {validation_level.value} validation")
    
    def _initialize_validation_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize validation rules for different data types"""



        
        return {
            'user_profile': {
                'required_fields': ['user_id', 'preferences'],
                'field_types': {
                    'user_id': str,
                    'preferences': dict,
                    'demographics': dict,
                    'behavior_patterns': dict
                },
                'constraints': {
                    'user_id': {'min_length': 1, 'max_length': 256},
                    'age': {'min_value': 13, 'max_value': 120},
                    'satisfaction_score': {'min_value': 0.0, 'max_value': 1.0}
                }
            },
            'content_item': {
                'required_fields': ['content_id', 'content_type'],
                'field_types': {
                    'content_id': str,
                    'content_type': str,
                    'metadata': dict,
                    'quality_score': float
                },
                'constraints': {
                    'content_id': {'min_length': 1, 'max_length': 256},
                    'quality_score': {'min_value': 0.0, 'max_value': 1.0},
                    'duration': {'min_value': 0}
                }
            },
            'recommendation': {
                'required_fields': ['user_id', 'content_id', 'relevance_score'],
                'field_types': {
                    'user_id': str,
                    'content_id': str,
                    'relevance_score': float,
                    'reasoning': dict
                },
                'constraints': {
                    'relevance_score': {'min_value': 0.0, 'max_value': 1.0},
                    'confidence': {'min_value': 0.0, 'max_value': 1.0}
                }
            },
            'feedback': {
                'required_fields': ['user_id', 'content_id', 'feedback_type'],
                'field_types': {
                    'user_id': str,
                    'content_id': str,
                    'feedback_type': str,
                    'value': (int, float),
                    'timestamp': datetime
                },
                'constraints': {
                    'rating': {'min_value': 0.0, 'max_value': 5.0},
                    'engagement_time': {'min_value': 0}
                }
            }
        }
    
    def validate_user_profile(self, profile_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate user profile data.
        
        Args:
            profile_data: User profile data to validate
            
        Returns:
            Tuple of (is_valid, error_messages)
        """



        try:
            return self._validate_data('user_profile', profile_data)
        except Exception as e:
            self.logger.error(f"User profile validation error: {e}")
            return False, [f"Validation error: {e}"]
    
    def validate_content_item(self, content_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate content item data.
        
        Args:
            content_data: Content item data to validate
            
        Returns:
            Tuple of (is_valid, error_messages)
        """



        try:
            return self._validate_data('content_item', content_data)
        except Exception as e:
            self.logger.error(f"Content item validation error: {e}")
            return False, [f"Validation error: {e}"]
    
    def validate_recommendation(self, rec_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate recommendation data.
        
        Args:
            rec_data: Recommendation data to validate
            
        Returns:
            Tuple of (is_valid, error_messages)
        """



        try:
            return self._validate_data('recommendation', rec_data)
        except Exception as e:
            self.logger.error(f"Recommendation validation error: {e}")
            return False, [f"Validation error: {e}"]
    
    def validate_feedback(self, feedback_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate feedback data.
        
        Args:
            feedback_data: Feedback data to validate
            
        Returns:
            Tuple of (is_valid, error_messages)
        """



        try:
            return self._validate_data('feedback', feedback_data)
        except Exception as e:
            self.logger.error(f"Feedback validation error: {e}")
            return False, [f"Validation error: {e}"]
    
    def _validate_data(self, data_type: str, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Generic data validation using rules"""
        
        if self.validation_level == ValidationLevel.DISABLED:
            return True, []
        
        # Get validation rules for data type
        rules = self.validation_rules.get(data_type, {})
        if not rules:
            return True, []  # No rules defined
        
        errors = []
        
        # Check required fields
        if self.validation_level in [ValidationLevel.STRICT, ValidationLevel.MODERATE]:
            required_fields = rules.get('required_fields', [])
            for field in required_fields:
                if field not in data:
                    errors.append(f"Missing required field: {field}")
        
        # Check field types
        if self.validation_level == ValidationLevel.STRICT:
            field_types = rules.get('field_types', {})
            for field, expected_type in field_types.items():
                if field in data:
                    value = data[field]
                    if not isinstance(value, expected_type):
                        errors.append(f"Field {field} has incorrect type. Expected {expected_type}, got {type(value)}")
        
        # Check constraints
        constraints = rules.get('constraints', {})
        for field, constraint_rules in constraints.items():
            if field in data:
                value = data[field]
                field_errors = self._validate_field_constraints(field, value, constraint_rules)
                errors.extend(field_errors)
        
        # Update validation stats
        self.validation_stats[f'{data_type}_validations'] += 1
        if errors:
            self.validation_stats[f'{data_type}_validation_failures'] += 1
        
        return len(errors) == 0, errors
    
    def _validate_field_constraints(
        self, 
        field_name: str, 
        value: Any, 
        constraints: Dict[str, Any]
    ) -> List[str]:
        """Validate field against constraints"""
        
        errors = []
        
        # Length constraints
        if 'min_length' in constraints and hasattr(value, '__len__'):
            if len(value) < constraints['min_length']:
                errors.append(f"Field {field_name} too short. Min: {constraints['min_length']}")
        
        if 'max_length' in constraints and hasattr(value, '__len__'):
            if len(value) > constraints['max_length']:
                errors.append(f"Field {field_name} too long. Max: {constraints['max_length']}")
        
        # Value constraints
        if 'min_value' in constraints and isinstance(value, (int, float)):
            if value < constraints['min_value']:
                errors.append(f"Field {field_name} too small. Min: {constraints['min_value']}")
        
        if 'max_value' in constraints and isinstance(value, (int, float)):
            if value > constraints['max_value']:
                errors.append(f"Field {field_name} too large. Max: {constraints['max_value']}")
        
        # Pattern constraints
        if 'pattern' in constraints and isinstance(value, str):
            if not re.match(constraints['pattern'], value):
                errors.append(f"Field {field_name} doesn't match required pattern")
        
        # Enum constraints
        if 'allowed_values' in constraints:
            if value not in constraints['allowed_values']:
                errors.append(f"Field {field_name} has invalid value. Allowed: {constraints['allowed_values']}")
        
        return errors
    
    def get_validation_stats(self) -> Dict[str, int]:
        """Get validation statistics"""



        return dict(self.validation_stats)


class PersonalizationCache:
    """
    High-performance caching system for personalization data.
    
    Features:
    - Multiple caching strategies
    - TTL support
    - Memory management
    - Performance monitoring
    - Automatic cleanup
    """
    
    def __init__(
        self, 
        max_size: int = 10000,
        default_ttl: timedelta = timedelta(hours=1),
        strategy: CacheStrategy = CacheStrategy.LRU
    ):
        self.logger = logging.getLogger(__name__)
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.strategy = strategy
        
        # Cache storage
        self.cache = {}
        self.access_times = {}
        self.insertion_times = {}
        self.ttl_times = {}
        
        # Performance tracking
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        
        # Thread safety
        self.lock = threading.RLock()
        
        # Background cleanup
        self.cleanup_thread = None
        self.running = True
        self._start_cleanup_thread()
        
        self.logger.info(f"Cache initialized: size={max_size}, ttl={default_ttl}, strategy={strategy.value}")
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        with self.lock:
            # Check if key exists
            if key not in self.cache:
                self.misses += 1
                return None
            
            # Check TTL
            if self._is_expired(key):
                self._remove_key(key)
                self.misses += 1
                return None
            
            # Update access time for LRU
            if self.strategy == CacheStrategy.LRU:
                self.access_times[key] = time.time()
            
            self.hits += 1
            return self.cache[key]
    
    def put(self, key: str, value: Any, ttl: Optional[timedelta] = None) -> None:
        """
        Put value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live (uses default if None)
        """
        with self.lock:
            current_time = time.time()
            
            # Set TTL
            ttl_time = current_time + (ttl or self.default_ttl).total_seconds()
            
            # Check if we need to evict
            if len(self.cache) >= self.max_size and key not in self.cache:
                self._evict_one()
            
            # Store value
            self.cache[key] = value
            self.access_times[key] = current_time
            self.insertion_times[key] = current_time
            self.ttl_times[key] = ttl_time
    
    def delete(self, key: str) -> bool:
        """
        Delete key from cache.
        
        Args:
            key: Cache key to delete
            
        Returns:
            True if key was deleted, False if not found
        """
        with self.lock:
            if key in self.cache:
                self._remove_key(key)
                return True
            return False
    
    def clear(self) -> None:
        """Clear all cached data"""
        with self.lock:
            self.cache.clear()
            self.access_times.clear()
            self.insertion_times.clear()
            self.ttl_times.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        with self.lock:
            total_requests = self.hits + self.misses
            hit_rate = self.hits / total_requests if total_requests > 0 else 0
            
            return {
                'size': len(self.cache),
                'max_size': self.max_size,
                'hits': self.hits,
                'misses': self.misses,
                'hit_rate': hit_rate,
                'evictions': self.evictions,
                'strategy': self.strategy.value
            }
    
    def _is_expired(self, key: str) -> bool:
        """Check if cache entry is expired"""



        return time.time() > self.ttl_times.get(key, float('inf'))
    
    def _remove_key(self, key: str) -> None:
        """Remove key and all associated metadata"""
        self.cache.pop(key, None)
        self.access_times.pop(key, None)
        self.insertion_times.pop(key, None)
        self.ttl_times.pop(key, None)
    
    def _evict_one(self) -> None:
        """Evict one entry based on strategy"""
        if not self.cache:
            return
        
        if self.strategy == CacheStrategy.LRU:
            # Evict least recently used
            key_to_evict = min(self.access_times.keys(), key=lambda k: self.access_times[k])
        elif self.strategy == CacheStrategy.FIFO:
            # Evict first inserted
            key_to_evict = min(self.insertion_times.keys(), key=lambda k: self.insertion_times[k])
        elif self.strategy == CacheStrategy.LIFO:
            # Evict last inserted
            key_to_evict = max(self.insertion_times.keys(), key=lambda k: self.insertion_times[k])
        elif self.strategy == CacheStrategy.TTL:
            # Evict soonest to expire
            key_to_evict = min(self.ttl_times.keys(), key=lambda k: self.ttl_times[k])
        else:  # RANDOM
            key_to_evict = np.random.choice(list(self.cache.keys()))
        
        self._remove_key(key_to_evict)
        self.evictions += 1
    
    def _start_cleanup_thread(self) -> None:
        """Start background cleanup thread"""
        def cleanup_expired():
            while self.running:
                try:
                    with self.lock:
                        current_time = time.time()
                        expired_keys = [
                            key for key, ttl_time in self.ttl_times.items()
                            if current_time > ttl_time
                        ]
                        
                        for key in expired_keys:
                            self._remove_key(key)
                    
                    time.sleep(60)  # Cleanup every minute
                except Exception as e:
                    self.logger.error(f"Cache cleanup error: {e}")
        
        self.cleanup_thread = threading.Thread(target=cleanup_expired, daemon=True)
        self.cleanup_thread.start()
    
    def __del__(self):
        """Cleanup on destruction"""
        self.running = False
        if self.cleanup_thread and self.cleanup_thread.is_alive():
            self.cleanup_thread.join(timeout=1)


class DataConverter:
    """
    Data conversion utilities for personalization.
    
    Features:
    - Format conversion
    - Schema transformation
    - Data normalization
    - Encoding/decoding
    - Performance optimization
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Conversion cache for performance
        self.conversion_cache = PersonalizationCache(max_size=1000)
        
        # Format handlers
        self.format_handlers = {
            'json': self._handle_json,
            'dict': self._handle_dict,
            'pandas': self._handle_pandas,
            'numpy': self._handle_numpy,
            'list': self._handle_list
        }
    
    def convert_user_profile(
        self, 
        profile_data: Any, 
        source_format: str, 
        target_format: str
    ) -> Any:
        """
        Convert user profile between formats.
        
        Args:
            profile_data: Profile data to convert
            source_format: Source data format
            target_format: Target data format
            
        Returns:
            Converted profile data
        """



        try:
            # Check cache first
            cache_key = self._generate_cache_key(profile_data, source_format, target_format)
            cached_result = self.conversion_cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Convert data
            result = self._convert_data(profile_data, source_format, target_format, 'user_profile')
            
            # Cache result
            self.conversion_cache.put(cache_key, result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"User profile conversion error: {e}")
            raise PersonalizationError(f"Failed to convert user profile: {e}")
    
    def convert_content_features(
        self, 
        content_data: Any, 
        source_format: str, 
        target_format: str
    ) -> Any:
        """
        Convert content features between formats.
        
        Args:
            content_data: Content data to convert
            source_format: Source data format
            target_format: Target data format
            
        Returns:
            Converted content data
        """



        try:
            return self._convert_data(content_data, source_format, target_format, 'content_features')
        except Exception as e:
            self.logger.error(f"Content features conversion error: {e}")
            raise PersonalizationError(f"Failed to convert content features: {e}")
    
    def normalize_scores(
        self, 
        scores: Union[List[float], np.ndarray],
        method: str = "min_max",
        target_range: Tuple[float, float] = (0.0, 1.0)
    ) -> np.ndarray:
        """
        Normalize scores to target range.
        
        Args:
            scores: Scores to normalize
            method: Normalization method ('min_max', 'z_score', 'robust')
            target_range: Target range for normalized scores
            
        Returns:
            Normalized scores
        """



        try:
            scores_array = np.array(scores)
            
            if method == "min_max":
                min_val, max_val = np.min(scores_array), np.max(scores_array)
                if max_val == min_val:
                    return np.full_like(scores_array, (target_range[0] + target_range[1]) / 2)
                
                normalized = (scores_array - min_val) / (max_val - min_val)
                return normalized * (target_range[1] - target_range[0]) + target_range[0]
            
            elif method == "z_score":
                mean_val, std_val = np.mean(scores_array), np.std(scores_array)
                if std_val == 0:
                    return np.full_like(scores_array, (target_range[0] + target_range[1]) / 2)
                
                z_scores = (scores_array - mean_val) / std_val
                # Map to target range (assuming 3-sigma range)
                normalized = (z_scores + 3) / 6  # Map [-3, 3] to [0, 1]
                return np.clip(normalized, 0, 1) * (target_range[1] - target_range[0]) + target_range[0]
            
            elif method == "robust":
                q25, q75 = np.percentile(scores_array, [25, 75])
                median_val = np.median(scores_array)
                
                if q75 == q25:
                    return np.full_like(scores_array, (target_range[0] + target_range[1]) / 2)
                
                normalized = (scores_array - median_val) / (q75 - q25)
                # Map to target range
                normalized = (normalized + 2) / 4  # Map [-2, 2] to [0, 1] approximately
                return np.clip(normalized, 0, 1) * (target_range[1] - target_range[0]) + target_range[0]
            
            else:
                raise ValueError(f"Unknown normalization method: {method}")
                
        except Exception as e:
            self.logger.error(f"Score normalization error: {e}")
            raise PersonalizationError(f"Failed to normalize scores: {e}")
    
    def encode_categorical_features(
        self, 
        features: Dict[str, Any],
        encoding_method: str = "one_hot"
    ) -> Dict[str, Any]:
        """
        Encode categorical features for ML models.
        
        Args:
            features: Features dictionary
            encoding_method: Encoding method ('one_hot', 'label', 'target')
            
        Returns:
            Encoded features
        """



        try:
            encoded_features = features.copy()
            
            for key, value in features.items():
                if isinstance(value, str) and encoding_method == "one_hot":
                    # Simple one-hot encoding for string values
                    unique_values = ['music', 'video', 'audio', 'text', 'image']  # Common categories
                    for cat_value in unique_values:
                        encoded_features[f"{key}_{cat_value}"] = 1.0 if value == cat_value else 0.0
                    
                    # Remove original categorical feature
                    del encoded_features[key]
                
                elif isinstance(value, list) and encoding_method == "one_hot":
                    # Multi-hot encoding for list values
                    all_values = set()
                    if isinstance(value, list):
                        all_values.update(value)
                    
                    for item in all_values:
                        encoded_features[f"{key}_{item}"] = 1.0
                    
                    # Remove original list feature
                    del encoded_features[key]
            
            return encoded_features
            
        except Exception as e:
            self.logger.error(f"Feature encoding error: {e}")
            raise PersonalizationError(f"Failed to encode features: {e}")
    
    def _convert_data(
        self, 
        data: Any, 
        source_format: str, 
        target_format: str, 
        data_type: str
    ) -> Any:
        """Generic data conversion"""
        
        # If formats are the same, return as-is
        if source_format == target_format:
            return data
        
        # Get handlers
        source_handler = self.format_handlers.get(source_format)
        target_handler = self.format_handlers.get(target_format)
        
        if not source_handler or not target_handler:
            raise ValueError(f"Unsupported format conversion: {source_format} -> {target_format}")
        
        # Convert through intermediate format (dict)
        if source_format != 'dict':
            intermediate = source_handler(data, 'to_dict')
        else:
            intermediate = data
        
        if target_format != 'dict':
            result = target_handler(intermediate, 'from_dict')
        else:
            result = intermediate
        
        return result
    
    def _handle_json(self, data: Any, operation: str) -> Any:
        """Handle JSON format conversions"""
        if operation == 'to_dict':
            return json.loads(data) if isinstance(data, str) else data
        elif operation == 'from_dict':
            return json.dumps(data, default=str)
        return data
    
    def _handle_dict(self, data: Any, operation: str) -> Any:
        """Handle dict format conversions"""



        return data  # Already in dict format
    
    def _handle_pandas(self, data: Any, operation: str) -> Any:
        """Handle pandas DataFrame conversions"""
        if operation == 'to_dict':
            return data.to_dict('records')[0] if len(data) > 0 else {}
        elif operation == 'from_dict':
            return pd.DataFrame([data])
        return data
    
    def _handle_numpy(self, data: Any, operation: str) -> Any:
        """Handle numpy array conversions"""
        if operation == 'to_dict':
            return {'features': data.tolist()}
        elif operation == 'from_dict':
            return np.array(data.get('features', []))
        return data
    
    def _handle_list(self, data: Any, operation: str) -> Any:
        """Handle list format conversions"""
        if operation == 'to_dict':
            return {'items': data}
        elif operation == 'from_dict':
            return data.get('items', [])
        return data
    
    def _generate_cache_key(self, data: Any, source_format: str, target_format: str) -> str:
        """Generate cache key for conversion"""
        # Create hash of data structure (not content)
        data_signature = str(type(data)) + str(len(str(data))[:100])
        key_string = f"{source_format}_{target_format}_{data_signature}"
        return hashlib.md5(key_string.encode()).hexdigest()


class PerformanceMonitor:
    """
    Performance monitoring for personalization operations.
    
    Features:
    - Execution time tracking
    - Memory usage monitoring
    - Cache performance analysis
    - Resource utilization tracking
    - Automated alerts
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Performance data storage
        self.performance_history = defaultdict(list)
        self.current_operations = {}
        
        # Alert thresholds
        self.alert_thresholds = {
            'execution_time': 5.0,  # seconds
            'memory_usage': 1024 * 1024 * 1024,  # 1GB
            'error_rate': 0.05,  # 5%
            'cache_hit_rate': 0.8  # 80%
        }
        
        # Performance aggregation
        self.aggregation_window = timedelta(minutes=5)
        self.last_aggregation = datetime.utcnow()
        
        # Thread safety
        self.lock = threading.RLock()
    
    def start_operation(self, operation_name: str) -> str:
        """
        Start monitoring an operation.
        
        Args:
            operation_name: Name of the operation
            
        Returns:
            Operation ID for tracking
        """
        operation_id = f"{operation_name}_{int(time.time() * 1000)}"
        
        with self.lock:
            self.current_operations[operation_id] = {
                'name': operation_name,
                'start_time': time.time(),
                'start_memory': self._get_memory_usage()
            }
        
        return operation_id
    
    def end_operation(
        self, 
        operation_id: str, 
        success: bool = True,
        additional_metrics: Optional[Dict[str, float]] = None
    ) -> PerformanceMetrics:
        """
        End monitoring an operation and record metrics.
        
        Args:
            operation_id: Operation ID from start_operation
            success: Whether operation was successful
            additional_metrics: Additional metrics to record
            
        Returns:
            Performance metrics for the operation
        """
        with self.lock:
            if operation_id not in self.current_operations:
                self.logger.warning(f"Unknown operation ID: {operation_id}")
                return PerformanceMetrics(0, 0, 0, 0)
            
            operation_data = self.current_operations.pop(operation_id)
            
            # Calculate metrics
            end_time = time.time()
            execution_time = end_time - operation_data['start_time']
            end_memory = self._get_memory_usage()
            memory_usage = end_memory - operation_data['start_memory']
            
            # Create performance metrics
            metrics = PerformanceMetrics(
                execution_time=execution_time,
                memory_usage=memory_usage,
                cache_hit_rate=0.0,  # Will be updated by cache if available
                error_rate=0.0 if success else 1.0,
                processing_time=execution_time,
                memory_peak=end_memory,
                operation_name=operation_data['name'],
                success=success
            )
            
            # Add additional metrics
            if additional_metrics:
                for key, value in additional_metrics.items():
                    if hasattr(metrics, key):
                        setattr(metrics, key, value)
            
            # Store in history
            self.performance_history[operation_data['name']].append(metrics)
            
            # Check for alerts
            self._check_performance_alerts(metrics)
            
            return metrics
    
    def get_operation_stats(self, operation_name: str) -> Dict[str, Any]:
        """
        Get performance statistics for an operation.
        
        Args:
            operation_name: Name of the operation
            
        Returns:
            Performance statistics
        """
        with self.lock:
            metrics_list = self.performance_history.get(operation_name, [])
            
            if not metrics_list:
                return {'status': 'no_data'}
            
            # Calculate statistics
            execution_times = [m.execution_time for m in metrics_list]
            memory_usages = [m.memory_usage for m in metrics_list]
            success_rate = sum(1 for m in metrics_list if m.success) / len(metrics_list)
            
            return {
                'operation_name': operation_name,
                'total_operations': len(metrics_list),
                'success_rate': success_rate,
                'execution_time': {
                    'mean': np.mean(execution_times),
                    'median': np.median(execution_times),
                    'std': np.std(execution_times),
                    'min': np.min(execution_times),
                    'max': np.max(execution_times),
                    'p95': np.percentile(execution_times, 95),
                    'p99': np.percentile(execution_times, 99)
                },
                'memory_usage': {
                    'mean': np.mean(memory_usages),
                    'median': np.median(memory_usages),
                    'max': np.max(memory_usages)
                }
            }
    
    def get_system_overview(self) -> Dict[str, Any]:
        """Get overall system performance overview"""
        
        with self.lock:
            all_operations = list(self.performance_history.keys())
            
            if not all_operations:
                return {'status': 'no_data'}
            
            # Aggregate metrics across all operations
            total_operations = sum(len(self.performance_history[op]) for op in all_operations)
            
            all_metrics = []
            for op_metrics in self.performance_history.values():
                all_metrics.extend(op_metrics)
            
            if not all_metrics:
                return {'status': 'no_data'}
            
            # Calculate system-wide metrics
            system_success_rate = sum(1 for m in all_metrics if m.success) / len(all_metrics)
            avg_execution_time = np.mean([m.execution_time for m in all_metrics])
            avg_memory_usage = np.mean([m.memory_usage for m in all_metrics])
            
            # Performance trends
            recent_metrics = [
                m for m in all_metrics 
                if m.timestamp > datetime.utcnow() - timedelta(hours=1)
            ]
            
            recent_success_rate = (
                sum(1 for m in recent_metrics if m.success) / len(recent_metrics)
                if recent_metrics else 0
            )
            
            return {
                'total_operations': total_operations,
                'operation_types': len(all_operations),
                'system_success_rate': system_success_rate,
                'recent_success_rate': recent_success_rate,
                'avg_execution_time': avg_execution_time,
                'avg_memory_usage': avg_memory_usage,
                'active_operations': len(self.current_operations),
                'performance_trend': self._calculate_performance_trend(all_metrics)
            }
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage (simplified)"""
        # In a real implementation, this would use psutil or similar
        # For now, return a placeholder value
        return 1024 * 1024 * 100  # 100MB placeholder
    
    def _check_performance_alerts(self, metrics: PerformanceMetrics) -> None:
        """Check if metrics trigger any performance alerts"""
        
        alerts = []
        
        if metrics.execution_time > self.alert_thresholds['execution_time']:
            alerts.append(f"High execution time: {metrics.execution_time:.2f}s")
        
        if metrics.memory_usage > self.alert_thresholds['memory_usage']:
            alerts.append(f"High memory usage: {metrics.memory_usage / 1024 / 1024:.2f}MB")
        
        if not metrics.success:
            alerts.append(f"Operation failed: {metrics.operation_name}")
        
        # Log alerts
        for alert in alerts:
            self.logger.warning(f"Performance alert: {alert}")
    
    def _calculate_performance_trend(self, metrics_list: List[PerformanceMetrics]) -> str:
        """Calculate performance trend direction"""
        
        if len(metrics_list) < 10:
            return "insufficient_data"
        
        # Get recent vs older metrics
        sorted_metrics = sorted(metrics_list, key=lambda m: m.timestamp)
        recent_metrics = sorted_metrics[-5:]
        older_metrics = sorted_metrics[-10:-5]
        
        # Compare execution times
        recent_avg = np.mean([m.execution_time for m in recent_metrics])
        older_avg = np.mean([m.execution_time for m in older_metrics])
        
        if recent_avg < older_avg * 0.9:
            return "improving"
        elif recent_avg > older_avg * 1.1:
            return "degrading"
        else:
            return "stable"


def performance_timer(operation_name: str):
    """
    Decorator for automatic performance monitoring.
    
    Args:
        operation_name: Name of the operation being monitored
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            monitor = PerformanceMonitor()
            operation_id = monitor.start_operation(operation_name)
            
            try:
                result = await func(*args, **kwargs)
                monitor.end_operation(operation_id, success=True)
                return result
            except Exception as e:
                monitor.end_operation(operation_id, success=False)
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            monitor = PerformanceMonitor()
            operation_id = monitor.start_operation(operation_name)
            
            try:
                result = func(*args, **kwargs)
                monitor.end_operation(operation_id, success=True)
                return result
            except Exception as e:
                monitor.end_operation(operation_id, success=False)
                raise
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


class FeatureExtractor:
    """
    Feature extraction utilities for personalization.
    
    Features:
    - Text feature extraction
    - Audio feature extraction
    - User behavior features
    - Content metadata features
    - Real-time feature computation
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Feature extraction cache
        self.feature_cache = PersonalizationCache(max_size=5000)
        
        # Pre-configured extractors
        self.text_vectorizer = None
        self.feature_scalers = {}
        
        self.logger.info("Feature extractor initialized")
    
    def extract_user_features(self, user_profile: UserProfile) -> Dict[str, float]:
        """
        Extract numerical features from user profile.
        
        Args:
            user_profile: User profile object
            
        Returns:
            Dictionary of numerical features
        """



        try:
            features = {}
            
            # Basic demographic features
            if hasattr(user_profile, 'age') and user_profile.age:
                features['age_normalized'] = min(user_profile.age / 100.0, 1.0)
            
            # Preference features
            if hasattr(user_profile, 'preferences') and user_profile.preferences:
                pref_dict = user_profile.preferences
                
                # Content type preferences
                content_types = ['music', 'video', 'audio', 'text', 'image']
                for content_type in content_types:
                    pref_key = f'preference_{content_type}'
                    features[pref_key] = pref_dict.get(content_type, 0.5)
                
                # Genre preferences
                if 'genres' in pref_dict:
                    genre_scores = pref_dict['genres']
                    if isinstance(genre_scores, dict):
                        for genre, score in genre_scores.items():
                            features[f'genre_{genre}'] = score
            
            # Behavioral features
            if hasattr(user_profile, 'behavior_patterns'):
                behavior = user_profile.behavior_patterns
                
                if isinstance(behavior, dict):
                    # Activity level
                    features['activity_level'] = behavior.get('activity_level', 0.5)
                    
                    # Engagement patterns
                    features['avg_engagement_time'] = min(
                        behavior.get('avg_engagement_time', 60) / 3600.0, 1.0  # Normalize to hours
                    )
                    
                    # Discovery vs familiarity
                    features['discovery_ratio'] = behavior.get('discovery_ratio', 0.5)
            
            # Temporal features
            current_hour = datetime.utcnow().hour
            features['hour_sin'] = np.sin(2 * np.pi * current_hour / 24)
            features['hour_cos'] = np.cos(2 * np.pi * current_hour / 24)
            
            current_day = datetime.utcnow().weekday()
            features['day_sin'] = np.sin(2 * np.pi * current_day / 7)
            features['day_cos'] = np.cos(2 * np.pi * current_day / 7)
            
            return features
            
        except Exception as e:
            self.logger.error(f"User feature extraction error: {e}")
            return {}
    
    def extract_content_features(self, content_metadata: Dict[str, Any]) -> Dict[str, float]:
        """
        Extract numerical features from content metadata.
        
        Args:
            content_metadata: Content metadata dictionary
            
        Returns:
            Dictionary of numerical features
        """



        try:
            features = {}
            
            # Basic content features
            content_type = content_metadata.get('content_type', 'unknown')
            content_types = ['music', 'video', 'audio', 'text', 'image']
            for ct in content_types:
                features[f'content_type_{ct}'] = 1.0 if content_type == ct else 0.0
            
            # Quality metrics
            features['quality_score'] = content_metadata.get('quality_score', 0.5)
            features['popularity_score'] = content_metadata.get('popularity_score', 0.5)
            
            # Temporal features
            created_date = content_metadata.get('created_date')
            if created_date:
                if isinstance(created_date, str):
                    created_date = datetime.fromisoformat(created_date)
                
                # Recency score (newer content gets higher score)
                days_old = (datetime.utcnow() - created_date).days
                features['recency_score'] = max(0.0, 1.0 - days_old / 365.0)  # Decay over a year
            
            # Duration features (for audio/video)
            duration = content_metadata.get('duration_seconds', 0)
            if duration > 0:
                # Normalize duration (log scale)
                features['duration_log'] = min(np.log(duration + 1) / np.log(3600 + 1), 1.0)
            
            # Engagement features
            features['view_count_log'] = np.log(content_metadata.get('view_count', 1) + 1) / 20.0
            features['like_ratio'] = content_metadata.get('like_ratio', 0.5)
            features['comment_ratio'] = content_metadata.get('comment_ratio', 0.0)
            
            # Genre/category features
            genres = content_metadata.get('genres', [])
            if isinstance(genres, list):
                common_genres = ['pop', 'rock', 'electronic', 'classical', 'jazz', 'folk']
                for genre in common_genres:
                    features[f'genre_{genre}'] = 1.0 if genre in genres else 0.0
            
            return features
            
        except Exception as e:
            self.logger.error(f"Content feature extraction error: {e}")
            return {}
    
    def extract_interaction_features(
        self, 
        user_id: str, 
        content_id: str,
        interaction_history: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """
        Extract features from user-content interaction history.
        
        Args:
            user_id: User identifier
            content_id: Content identifier
            interaction_history: History of interactions
            
        Returns:
            Dictionary of interaction features
        """



        try:
            features = {}
            
            # Filter interactions for this user
            user_interactions = [
                interaction for interaction in interaction_history
                if interaction.get('user_id') == user_id
            ]
            
            # Basic interaction stats
            features['total_interactions'] = len(user_interactions)
            features['interaction_frequency'] = len(user_interactions) / max(len(interaction_history), 1)
            
            if user_interactions:
                # Engagement statistics
                engagement_times = [
                    interaction.get('engagement_time', 0) 
                    for interaction in user_interactions
                ]
                features['avg_engagement_time'] = np.mean(engagement_times) / 3600.0  # Normalize to hours
                features['max_engagement_time'] = max(engagement_times) / 3600.0
                
                # Rating statistics
                ratings = [
                    interaction.get('rating', 0.5) 
                    for interaction in user_interactions 
                    if 'rating' in interaction
                ]
                if ratings:
                    features['avg_rating'] = np.mean(ratings)
                    features['rating_std'] = np.std(ratings)
                
                # Temporal patterns
                timestamps = [
                    datetime.fromisoformat(interaction['timestamp']) 
                    for interaction in user_interactions 
                    if 'timestamp' in interaction
                ]
                
                if len(timestamps) > 1:
                    # Calculate interaction intervals
                    intervals = [(timestamps[i] - timestamps[i-1]).total_seconds() 
                                for i in range(1, len(timestamps))]
                    features['avg_interaction_interval'] = np.mean(intervals) / 86400.0  # Normalize to days
                
                # Recent activity
                recent_cutoff = datetime.utcnow() - timedelta(days=7)
                recent_interactions = [
                    interaction for interaction in user_interactions
                    if 'timestamp' in interaction and 
                    datetime.fromisoformat(interaction['timestamp']) > recent_cutoff
                ]
                features['recent_activity_ratio'] = len(recent_interactions) / len(user_interactions)
            
            # Content-specific interaction features
            content_interactions = [
                interaction for interaction in interaction_history
                if interaction.get('content_id') == content_id
            ]
            
            features['content_interaction_count'] = len(content_interactions)
            features['content_popularity'] = len(content_interactions) / max(len(interaction_history), 1)
            
            if content_interactions:
                content_ratings = [
                    interaction.get('rating', 0.5) 
                    for interaction in content_interactions 
                    if 'rating' in interaction
                ]
                if content_ratings:
                    features['content_avg_rating'] = np.mean(content_ratings)
            
            return features
            
        except Exception as e:
            self.logger.error(f"Interaction feature extraction error: {e}")
            return {}
    
    def combine_features(self, *feature_dicts: Dict[str, float]) -> Dict[str, float]:
        """
        Combine multiple feature dictionaries into one.
        
        Args:
            *feature_dicts: Variable number of feature dictionaries
            
        Returns:
            Combined feature dictionary
        """



        try:
            combined = {}
            
            for feature_dict in feature_dicts:
                if isinstance(feature_dict, dict):
                    combined.update(feature_dict)
            
            return combined
            
        except Exception as e:
            self.logger.error(f"Feature combination error: {e}")
            return {}
    
    def normalize_features(
        self, 
        features: Dict[str, float],
        method: str = "min_max"
    ) -> Dict[str, float]:
        """
        Normalize feature values.
        
        Args:
            features: Feature dictionary to normalize
            method: Normalization method
            
        Returns:
            Normalized features
        """



        try:
            if not features:
                return features
            
            values = list(features.values())
            
            if method == "min_max":
                min_val, max_val = min(values), max(values)
                if max_val == min_val:
                    return {k: 0.5 for k in features.keys()}
                
                return {
                    k: (v - min_val) / (max_val - min_val)
                    for k, v in features.items()
                }
            
            elif method == "z_score":
                mean_val, std_val = np.mean(values), np.std(values)
                if std_val == 0:
                    return {k: 0.0 for k in features.keys()}
                
                return {
                    k: (v - mean_val) / std_val
                    for k, v in features.items()
                }
            
            else:
                return features  # No normalization
                
        except Exception as e:
            self.logger.error(f"Feature normalization error: {e}")
            return features


class ConfigurationManager:
    """
    Configuration management for personalization system.
    
    Features:
    - Environment-based configuration
    - Dynamic configuration updates
    - Configuration validation
    - Default value management
    - Configuration history
    """
    
    def __init__(self, config_file: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        
        # Configuration storage
        self.config = {}
        self.config_history = []
        self.default_config = self._load_default_config()
        
        # Load configuration
        if config_file:
            self.load_from_file(config_file)
        else:
            self.config = self.default_config.copy()
        
        self.logger.info("Configuration manager initialized")
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration values"""



        
        return {
            # Model configuration
            'models': {
                'collaborative_filtering': {
                    'n_factors': 50,
                    'regularization': 0.01,
                    'learning_rate': 0.005
                },
                'content_based': {
                    'similarity_threshold': 0.3,
                    'max_recommendations': 100
                },
                'hybrid': {
                    'collaborative_weight': 0.6,
                    'content_weight': 0.4
                }
            },
            
            # Cache configuration
            'cache': {
                'max_size': 10000,
                'default_ttl_hours': 1,
                'strategy': 'lru'
            },
            
            # Performance configuration
            'performance': {
                'max_execution_time': 5.0,
                'memory_limit_mb': 1024,
                'concurrent_operations': 10
            },
            
            # Analytics configuration
            'analytics': {
                'metrics_retention_days': 30,
                'aggregation_interval_minutes': 5,
                'alert_thresholds': {
                    'accuracy': 0.7,
                    'engagement': 0.5,
                    'response_time': 2.0
                }
            },
            
            # Validation configuration
            'validation': {
                'level': 'moderate',
                'strict_type_checking': False,
                'allow_missing_fields': True
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.
        
        Args:
            key: Configuration key (supports dot notation like 'models.collaborative_filtering.n_factors')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """



        try:
            keys = key.split('.')
            value = self.config
            
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
            
            return value
            
        except Exception as e:
            self.logger.error(f"Configuration get error: {e}")
            return default
    
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value using dot notation.
        
        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
        """



        try:
            # Store current config in history
            self.config_history.append({
                'timestamp': datetime.utcnow(),
                'config': self.config.copy()
            })
            
            # Keep only last 10 configurations in history
            if len(self.config_history) > 10:
                self.config_history.pop(0)
            
            # Set new value
            keys = key.split('.')
            current = self.config
            
            for k in keys[:-1]:
                if k not in current:
                    current[k] = {}
                current = current[k]
            
            current[keys[-1]] = value
            
            self.logger.info(f"Configuration updated: {key} = {value}")
            
        except Exception as e:
            self.logger.error(f"Configuration set error: {e}")
            raise PersonalizationError(f"Failed to set configuration: {e}")
    
    def load_from_file(self, config_file: str) -> None:
        """
        Load configuration from JSON file.
        
        Args:
            config_file: Path to configuration file
        """



        try:
            with open(config_file, 'r') as f:
                file_config = json.load(f)
            
            # Merge with default configuration
            self.config = self._merge_configs(self.default_config, file_config)
            
            self.logger.info(f"Configuration loaded from {config_file}")
            
        except Exception as e:
            self.logger.error(f"Configuration file load error: {e}")
            # Use default configuration on error
            self.config = self.default_config.copy()
    
    def save_to_file(self, config_file: str) -> None:
        """
        Save current configuration to JSON file.
        
        Args:
            config_file: Path to save configuration file
        """



        try:
            with open(config_file, 'w') as f:
                json.dump(self.config, f, indent=2, default=str)
            
            self.logger.info(f"Configuration saved to {config_file}")
            
        except Exception as e:
            self.logger.error(f"Configuration file save error: {e}")
            raise PersonalizationError(f"Failed to save configuration: {e}")
    
    def reset_to_defaults(self) -> None:
        """Reset configuration to default values"""
        
        self.config = self.default_config.copy()
        self.logger.info("Configuration reset to defaults")
    
    def validate_config(self) -> Tuple[bool, List[str]]:
        """
        Validate current configuration.
        
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        try:
            # Validate model configuration
            if 'models' in self.config:
                models_config = self.config['models']
                
                if 'collaborative_filtering' in models_config:
                    cf_config = models_config['collaborative_filtering']
                    if cf_config.get('n_factors', 0) <= 0:
                        errors.append("Collaborative filtering n_factors must be positive")
                    if cf_config.get('learning_rate', 0) <= 0:
                        errors.append("Collaborative filtering learning_rate must be positive")
                
                if 'hybrid' in models_config:
                    hybrid_config = models_config['hybrid']
                    total_weight = (hybrid_config.get('collaborative_weight', 0) + 
                                  hybrid_config.get('content_weight', 0))
                    if abs(total_weight - 1.0) > 0.01:
                        errors.append("Hybrid model weights must sum to 1.0")
            
            # Validate cache configuration
            if 'cache' in self.config:
                cache_config = self.config['cache']
                if cache_config.get('max_size', 0) <= 0:
                    errors.append("Cache max_size must be positive")
                if cache_config.get('default_ttl_hours', 0) <= 0:
                    errors.append("Cache default_ttl_hours must be positive")
            
            # Validate performance configuration
            if 'performance' in self.config:
                perf_config = self.config['performance']
                if perf_config.get('max_execution_time', 0) <= 0:
                    errors.append("Performance max_execution_time must be positive")
                if perf_config.get('memory_limit_mb', 0) <= 0:
                    errors.append("Performance memory_limit_mb must be positive")
            
            return len(errors) == 0, errors
            
        except Exception as e:
            self.logger.error(f"Configuration validation error: {e}")
            return False, [f"Validation error: {e}"]
    
    def _merge_configs(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge configuration dictionaries"""
        
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get summary of current configuration"""



        
        return {
            'total_keys': len(self._flatten_config(self.config)),
            'major_sections': list(self.config.keys()),
            'last_updated': (
                self.config_history[-1]['timestamp'].isoformat() 
                if self.config_history else "never"
            ),
            'validation_status': self.validate_config()[0]
        }
    
    def _flatten_config(self, config: Dict[str, Any], prefix: str = "") -> Dict[str, Any]:
        """Flatten nested configuration dictionary"""
        
        result = {}
        
        for key, value in config.items():
            full_key = f"{prefix}.{key}" if prefix else key
            
            if isinstance(value, dict):
                result.update(self._flatten_config(value, full_key))
            else:
                result[full_key] = value
        
        return result


# Global instances for easy access
_global_cache = None
_global_monitor = None
_global_config = None

def get_global_cache() -> PersonalizationCache:
    """Get global cache instance"""
    global _global_cache
    if _global_cache is None:
        _global_cache = PersonalizationCache()
    return _global_cache

def get_global_monitor() -> PerformanceMonitor:
    """Get global performance monitor instance"""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = PerformanceMonitor()
    return _global_monitor

def get_global_config() -> ConfigurationManager:
    """Get global configuration manager instance"""
    global _global_config
    if _global_config is None:
        _global_config = ConfigurationManager()
    return _global_config
