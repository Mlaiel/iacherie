"""Advanced AI Models Management Module for IA Influencer Agent Platform

Comprehensive AI/ML model management system for loading, optimizing,
and serving multiple NLP models efficiently.

Created by: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - Unauthorized use prohibited ⚠️
This software is proprietary and confidential. Contact: mlaiel@live.de
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
import json
import pickle
import os
from pathlib import Path
import threading
from concurrent.futures import ThreadPoolExecutor
import hashlib
import time
from enum import Enum

logger = logging.getLogger(__name__)

class ModelType(Enum):
    """
Types of AI models"""

    SENTIMENT_ANALYSIS = "sentiment_analysis"
    TEXT_CLASSIFICATION = "text_classification"
    NAMED_ENTITY_RECOGNITION = "named_entity_recognition"
    TOPIC_MODELING = "topic_modeling"
    TRANSLATION = "translation"
    SUMMARIZATION = "summarization"
    GENERATION = "generation"
    EMBEDDING = "embedding"
    KEYWORD_EXTRACTION = "keyword_extraction"
    CONTENT_SCORING = "content_scoring"

class ModelStatus(Enum):
    """Model status states"""

    UNLOADED = "unloaded"
    LOADING = "loading"
    LOADED = "loaded"
    ERROR = "error"
    OPTIMIZING = "optimizing"
    UPDATING = "updating"

@dataclass
class ModelConfig:
    """Model configuration"""
    model_id: str
    model_type: ModelType
    model_path: str
    model_class: str
    version: str
    description: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    requirements: List[str] = field(default_factory=list)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    memory_requirements: int = 0  # MB
    gpu_required: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class ModelInstance:
    """
Loaded model instance"""
    config: ModelConfig
    model: Any  # The actual model object
    status: ModelStatus
    load_time: datetime
    last_used: datetime
    usage_count: int = 0
    memory_usage: int = 0  # MB
    error_message: Optional[str] = None
    performance_stats: Dict[str, float] = field(default_factory=dict)

@dataclass
class ModelPrediction:
    """
Model prediction result"""
    model_id: str
    input_data: Any
    prediction: Any
    confidence: float
    processing_time: float
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ModelPerformanceMetrics:
    """
Model performance metrics"""
    model_id: str
    total_predictions: int
    average_processing_time: float
    accuracy_score: float
    error_rate: float
    memory_efficiency: float
    cpu_usage: float
    gpu_usage: float
    last_evaluation: datetime

class BaseNLPModel(ABC):
    """
Abstract base class for NLP models"""
    
    def __init__(self, config: ModelConfig):
        self.config = config
        self.is_loaded = False
        self.model = None
    
    @abstractmethod
    async def load_model(self):
        """
Load the model"""
        pass
    
    @abstractmethod
    async def predict(self, input_data: Any) -> Any:
        """
Make prediction"""
        pass
    
    @abstractmethod
    async def batch_predict(self, input_batch: List[Any]) -> List[Any]:
        """
Make batch predictions"""
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """
Get model information"""
        pass
    
    async def unload_model(self):
        """
Unload the model"""
        self.model = None
        self.is_loaded = False

class SentimentAnalysisModel(BaseNLPModel):
    """
Sentiment analysis model"""
    
    async def load_model(self):
        """
Load sentiment analysis model"""
        # In production, this would load actual models like BERT, RoBERTa, etc.
        await asyncio.sleep(0.1)  # Simulate loading time
        
        # Simulated model loading
        self.model = {
            'type': 'sentiment_classifier',
            'vocab_size': 50000,
            'embedding_dim': 768,
            'classes': ['positive', 'negative', 'neutral']
        }
        self.is_loaded = True
        logger.info(f"Sentiment analysis model loaded: {self.config.model_id}")
    
    async def predict(self, input_data: str) -> Dict[str, Any]:
        """Predict sentiment"""
        if not self.is_loaded:
            await self.load_model()
        
        # Simulate sentiment analysis
        import random
        sentiments = ['positive', 'negative', 'neutral']
        predicted_sentiment = random.choice(sentiments)
        confidence = random.uniform(0.7, 0.95)
        
        return {
            'sentiment': predicted_sentiment,
            'confidence': confidence,
            'scores': {
                'positive': random.uniform(0.1, 0.9),
                'negative': random.uniform(0.1, 0.9),
                'neutral': random.uniform(0.1, 0.9)
            }
        }
    
    async def batch_predict(self, input_batch: List[str]) -> List[Dict[str, Any]]:
        """
Batch sentiment prediction"""
        results = []
        for text in input_batch:
            result = await self.predict(text)
            results.append(result)
        return results
    
    def get_model_info(self) -> Dict[str, Any]:
        """
Get sentiment model information"""
        return {
            'model_type': 'sentiment_analysis',
            'architecture': 'transformer_based',
            'training_data': 'social_media_sentiment_dataset',
            'accuracy': 0.92,
            'f1_score': 0.91
        }

class TextClassificationModel(BaseNLPModel):
    """
Text classification model"""
    
    async def load_model(self):
        """
Load text classification model"""
        await asyncio.sleep(0.15)  # Simulate loading time
        
        self.model = {
            'type': 'text_classifier',
            'categories': ['technology', 'lifestyle', 'business', 'entertainment', 'education'],
            'vocab_size': 75000,
            'max_sequence_length': 512
        }
        self.is_loaded = True
        logger.info(f"Text classification model loaded: {self.config.model_id}")
    
    async def predict(self, input_data: str) -> Dict[str, Any]:
        """Predict text category"""
        if not self.is_loaded:
            await self.load_model()
        
        import random
        categories = self.model['categories']
        predicted_category = random.choice(categories)
        confidence = random.uniform(0.75, 0.95)
        
        # Generate scores for all categories
        scores = {cat: random.uniform(0.05, 0.3) for cat in categories}
        scores[predicted_category] = confidence
        
        return {
            'category': predicted_category,
            'confidence': confidence,
            'scores': scores
        }
    
    async def batch_predict(self, input_batch: List[str]) -> List[Dict[str, Any]]:
        """
Batch text classification"""
        results = []
        for text in input_batch:
            result = await self.predict(text)
            results.append(result)
        return results
    
    def get_model_info(self) -> Dict[str, Any]:
        return {
            'model_type': 'text_classification',
            'architecture': 'bert_based',
            'num_classes': len(self.model['categories']) if self.model else 0,
            'accuracy': 0.89
        }

class EmbeddingModel(BaseNLPModel):
    """
Text embedding model"""
    
    async def load_model(self):
        """
Load embedding model"""
        await asyncio.sleep(0.2)  # Simulate loading time
        
        self.model = {
            'type': 'embedding_model',
            'embedding_dim': 768,
            'model_name': 'sentence-transformers/all-MiniLM-L6-v2',
            'max_seq_length': 384
        }
        self.is_loaded = True
        logger.info(f"Embedding model loaded: {self.config.model_id}")
    
    async def predict(self, input_data: str) -> List[float]:
        """Generate text embedding"""
        if not self.is_loaded:
            await self.load_model()
        
        # Simulate embedding generation
        import numpy as np
        embedding_dim = self.model['embedding_dim']
        embedding = np.random.normal(0, 1, embedding_dim).tolist()
        
        return embedding
    
    async def batch_predict(self, input_batch: List[str]) -> List[List[float]]:
        """
Batch embedding generation"""
        results = []
        for text in input_batch:
            embedding = await self.predict(text)
            results.append(embedding)
        return results
    
    def get_model_info(self) -> Dict[str, Any]:
        return {
            'model_type': 'embedding',
            'embedding_dimension': self.model['embedding_dim'] if self.model else 0,
            'similarity_metric': 'cosine'
        }

class AdvancedModelManager:
    """
    Advanced AI model management system
    
    Features:
    - Dynamic model loading/unloading
    - Model caching and optimization
    - Performance monitoring
    - Resource management
    - Model versioning
    - Batch processing
    - Auto-scaling
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._get_default_config()
        self.models: Dict[str, ModelInstance] = {}
        self.model_configs: Dict[str, ModelConfig] = {}
        self.executor = ThreadPoolExecutor(max_workers=self.config['max_workers'])
        self.cache_manager = ModelCacheManager(self.config['cache_config'])
        self.performance_monitor = ModelPerformanceMonitor()
        self.resource_manager = ResourceManager()
        
        # Load model configurations
        self._load_model_configurations()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """
Get default configuration"""
        return {
            'models_directory': './models',
            'max_loaded_models': 10,
            'memory_limit_mb': 8192,
            'auto_unload_unused': True,
            'unused_model_timeout': 3600,  # seconds
            'max_workers': 4,
            'enable_gpu': False,
            'cache_config': {
                'enabled': True,
                'max_cache_size': 1000,
                'cache_ttl': 1800  # seconds
            },
            'performance_monitoring': {
                'enabled': True,
                'metrics_retention_days': 30
            }
        }
    
    def _load_model_configurations(self):
        """
Load model configurations"""
        # Define available models
        model_configs = [
            ModelConfig(
                model_id="sentiment_v1",
                model_type=ModelType.SENTIMENT_ANALYSIS,
                model_path="./models/sentiment_v1",
                model_class="SentimentAnalysisModel",
                version="1.0.0",
                description="Advanced sentiment analysis for social media content",
                parameters={'max_length': 512, 'batch_size': 32},
                memory_requirements=512,
                performance_metrics={'accuracy': 0.92, 'f1_score': 0.91}
            ),
            ModelConfig(
                model_id="classification_v2",
                model_type=ModelType.TEXT_CLASSIFICATION,
                model_path="./models/classification_v2",
                model_class="TextClassificationModel",
                version="2.1.0",
                description="Multi-category content classification",
                parameters={'num_classes': 5, 'max_length': 384},
                memory_requirements=768,
                performance_metrics={'accuracy': 0.89, 'macro_f1': 0.87}
            ),
            ModelConfig(
                model_id="embeddings_v1",
                model_type=ModelType.EMBEDDING,
                model_path="./models/embeddings_v1",
                model_class="EmbeddingModel",
                version="1.2.0",
                description="Semantic embeddings for content similarity",
                parameters={'embedding_dim': 768, 'normalize': True},
                memory_requirements=1024,
                performance_metrics={'cosine_similarity_accuracy': 0.85}
            )
        ]
        
        for config in model_configs:
            self.model_configs[config.model_id] = config
        
        logger.info(f"Loaded {len(model_configs)} model configurations")
    
    async def load_model(self, model_id: str, force_reload: bool = False) -> bool:
        """Load a specific model"""
        if model_id not in self.model_configs:
            logger.error(f"Model configuration not found: {model_id}")
            return False
        
        # Check if model is already loaded
        if model_id in self.models and not force_reload:
            if self.models[model_id].status == ModelStatus.LOADED:
                logger.info(f"Model already loaded: {model_id}")
                return True
        
        config = self.model_configs[model_id]
        
        # Check resource availability
        if not await self.resource_manager.check_resources(config):
            logger.warning(f"Insufficient resources to load model: {model_id}")
            
            # Try to free up resources
            await self._free_resources_for_model(config)
            
            if not await self.resource_manager.check_resources(config):
                logger.error(f"Cannot load model due to resource constraints: {model_id}")
                return False
        
        try:
            # Create model instance
            model_instance = ModelInstance(
                config=config,
                model=None,
                status=ModelStatus.LOADING,
                load_time=datetime.utcnow(),
                last_used=datetime.utcnow()
            )
            
            self.models[model_id] = model_instance
            
            # Load the actual model
            nlp_model = await self._create_model_instance(config)
            await nlp_model.load_model()
            
            # Update model instance
            model_instance.model = nlp_model
            model_instance.status = ModelStatus.LOADED
            model_instance.memory_usage = config.memory_requirements
            
            logger.info(f"Model loaded successfully: {model_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading model {model_id}: {str(e)}")
            if model_id in self.models:
                self.models[model_id].status = ModelStatus.ERROR
                self.models[model_id].error_message = str(e)
            return False
    
    async def unload_model(self, model_id: str) -> bool:
        """Unload a specific model"""
        if model_id not in self.models:
            logger.warning(f"Model not found for unloading: {model_id}")
            return False
        
        try:
            model_instance = self.models[model_id]
            
            if model_instance.model and hasattr(model_instance.model, 'unload_model'):
                await model_instance.model.unload_model()
            
            model_instance.status = ModelStatus.UNLOADED
            model_instance.model = None
            model_instance.memory_usage = 0
            
            logger.info(f"Model unloaded successfully: {model_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error unloading model {model_id}: {str(e)}")
            return False
    
    async def predict(self, model_id: str, input_data: Any, use_cache: bool = True) -> ModelPrediction:
        """Make prediction using specified model"""
        start_time = time.time()
        
        # Check cache first
        if use_cache and self.cache_manager.enabled:
            cached_result = await self.cache_manager.get_cached_prediction(model_id, input_data)
            if cached_result:
                logger.debug(f"Cache hit for model {model_id}")
                return cached_result
        
        # Ensure model is loaded
        if not await self._ensure_model_loaded(model_id):
            raise RuntimeError(f"Failed to load model: {model_id}")
        
        model_instance = self.models[model_id]
        
        try:
            # Make prediction
            prediction = await model_instance.model.predict(input_data)
            processing_time = time.time() - start_time
            
            # Update usage statistics
            model_instance.usage_count += 1
            model_instance.last_used = datetime.utcnow()
            
            # Create prediction result
            result = ModelPrediction(
                model_id=model_id,
                input_data=input_data,
                prediction=prediction,
                confidence=self._extract_confidence(prediction),
                processing_time=processing_time,
                timestamp=datetime.utcnow(),
                metadata={'model_version': model_instance.config.version}
            )
            
            # Cache result
            if use_cache and self.cache_manager.enabled:
                await self.cache_manager.cache_prediction(result)
            
            # Update performance metrics
            await self.performance_monitor.record_prediction(model_id, processing_time, True)
            
            return result
            
        except Exception as e:
            logger.error(f"Prediction error for model {model_id}: {str(e)}")
            await self.performance_monitor.record_prediction(model_id, time.time() - start_time, False)
            raise
    
    async def batch_predict(self, model_id: str, input_batch: List[Any], 
                          batch_size: int = None) -> List[ModelPrediction]:
        """Make batch predictions"""
        if not await self._ensure_model_loaded(model_id):
            raise RuntimeError(f"Failed to load model: {model_id}")
        
        model_instance = self.models[model_id]
        batch_size = batch_size or self.config.get('default_batch_size', 32)
        
        # Process in batches
        results = []
        for i in range(0, len(input_batch), batch_size):
            batch = input_batch[i:i + batch_size]
            
            start_time = time.time()
            try:
                predictions = await model_instance.model.batch_predict(batch)
                processing_time = time.time() - start_time
                
                # Convert to ModelPrediction objects
                for j, (input_data, prediction) in enumerate(zip(batch, predictions)):
                    result = ModelPrediction(
                        model_id=model_id,
                        input_data=input_data,
                        prediction=prediction,
                        confidence=self._extract_confidence(prediction),
                        processing_time=processing_time / len(batch),
                        timestamp=datetime.utcnow(),
                        metadata={'batch_index': i + j, 'model_version': model_instance.config.version}
                    )
                    results.append(result)
                
                # Update statistics
                model_instance.usage_count += len(batch)
                model_instance.last_used = datetime.utcnow()
                
                await self.performance_monitor.record_batch_prediction(
                    model_id, len(batch), processing_time, True
                )
                
            except Exception as e:
                logger.error(f"Batch prediction error for model {model_id}: {str(e)}")
                await self.performance_monitor.record_batch_prediction(
                    model_id, len(batch), time.time() - start_time, False
                )
                raise
        
        return results
    
    async def get_model_status(self, model_id: str = None) -> Dict[str, Any]:
        """Get status of specific model or all models"""
        if model_id:
            if model_id not in self.models:
                return {'error': f'Model not found: {model_id}'}
            
            model_instance = self.models[model_id]
            return {
                'model_id': model_id,
                'status': model_instance.status.value,
                'load_time': model_instance.load_time.isoformat(),
                'last_used': model_instance.last_used.isoformat(),
                'usage_count': model_instance.usage_count,
                'memory_usage_mb': model_instance.memory_usage,
                'error_message': model_instance.error_message
            }
        else:
            # Return status for all models
            status = {}
            for mid, model_instance in self.models.items():
                status[mid] = {
                    'status': model_instance.status.value,
                    'memory_usage_mb': model_instance.memory_usage,
                    'usage_count': model_instance.usage_count,
                    'last_used': model_instance.last_used.isoformat()
                }
            
            # Add resource usage summary
            status['summary'] = {
                'total_loaded_models': len([m for m in self.models.values() if m.status == ModelStatus.LOADED]),
                'total_memory_usage_mb': sum(m.memory_usage for m in self.models.values()),
                'available_memory_mb': self.config['memory_limit_mb'] - sum(m.memory_usage for m in self.models.values())
            }
            
            return status
    
    async def optimize_models(self):
        """
Optimize loaded models (unload unused models, etc.)"""
        if not self.config['auto_unload_unused']:
            return
        
        current_time = datetime.utcnow()
        timeout_threshold = timedelta(seconds=self.config['unused_model_timeout'])
        
        models_to_unload = []
        
        for model_id, model_instance in self.models.items():
            if (model_instance.status == ModelStatus.LOADED and 
                current_time - model_instance.last_used > timeout_threshold):
                models_to_unload.append(model_id)
        
        for model_id in models_to_unload:
            logger.info(f"Auto-unloading unused model: {model_id}")
            await self.unload_model(model_id)
    
    async def get_performance_metrics(self, model_id: str = None) -> Dict[str, Any]:
        """Get performance metrics for models"""
        return await self.performance_monitor.get_metrics(model_id)
    
    async def _ensure_model_loaded(self, model_id: str) -> bool:
        """
Ensure model is loaded and ready"""
        if model_id not in self.models:
            return await self.load_model(model_id)
        
        model_instance = self.models[model_id]
        
        if model_instance.status == ModelStatus.LOADED:
            return True
        elif model_instance.status == ModelStatus.ERROR:
            # Try to reload
            return await self.load_model(model_id, force_reload=True)
        elif model_instance.status == ModelStatus.UNLOADED:
            return await self.load_model(model_id)
        else:
            # Model is loading, wait for it
            max_wait = 30  # seconds
            wait_time = 0
            while model_instance.status == ModelStatus.LOADING and wait_time < max_wait:
                await asyncio.sleep(0.5)
                wait_time += 0.5
            
            return model_instance.status == ModelStatus.LOADED
    
    async def _create_model_instance(self, config: ModelConfig) -> BaseNLPModel:
        """
Create model instance based on configuration"""
        if config.model_type == ModelType.SENTIMENT_ANALYSIS:
            return SentimentAnalysisModel(config)
        elif config.model_type == ModelType.TEXT_CLASSIFICATION:
            return TextClassificationModel(config)
        elif config.model_type == ModelType.EMBEDDING:
            return EmbeddingModel(config)
        else:
            raise ValueError(f"Unsupported model type: {config.model_type}")
    
    async def _free_resources_for_model(self, config: ModelConfig):
        """Free up resources to load a new model"""
        if not self.config['auto_unload_unused']:
            return
        
        # Find least recently used models to unload
        loaded_models = [
            (model_id, model_instance) for model_id, model_instance in self.models.items()
            if model_instance.status == ModelStatus.LOADED
        ]
        
        # Sort by last used time
        loaded_models.sort(key=lambda x: x[1].last_used)
        
        required_memory = config.memory_requirements
        current_usage = sum(m.memory_usage for _, m in loaded_models)
        available_memory = self.config['memory_limit_mb'] - current_usage
        
        if available_memory >= required_memory:
            return
        
        # Unload models until we have enough memory
        memory_to_free = required_memory - available_memory
        freed_memory = 0
        
        for model_id, model_instance in loaded_models:
            if freed_memory >= memory_to_free:
                break
            
            logger.info(f"Unloading model to free memory: {model_id}")
            await self.unload_model(model_id)
            freed_memory += model_instance.memory_usage
    
    def _extract_confidence(self, prediction: Any) -> float:
        """Extract confidence score from prediction"""
        if isinstance(prediction, dict):
            if 'confidence' in prediction:
                return prediction['confidence']
            elif 'score' in prediction:
                return prediction['score']
            elif 'probability' in prediction:
                return prediction['probability']
        
        return 0.5  # Default confidence

class ModelCacheManager:
    """
Manages prediction caching"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.enabled = config.get('enabled', True)
        self.cache = {}
        self.cache_timestamps = {}
        self.max_size = config.get('max_cache_size', 1000)
        self.ttl = config.get('cache_ttl', 1800)  # seconds
    
    async def get_cached_prediction(self, model_id: str, input_data: Any) -> Optional[ModelPrediction]:
        """
Get cached prediction if available"""
        if not self.enabled:
            return None
        
        cache_key = self._generate_cache_key(model_id, input_data)
        
        if cache_key in self.cache:
            # Check if cache entry is still valid
            if time.time() - self.cache_timestamps[cache_key] < self.ttl:
                return self.cache[cache_key]
            else:
                # Remove expired entry
                del self.cache[cache_key]
                del self.cache_timestamps[cache_key]
        
        return None
    
    async def cache_prediction(self, prediction: ModelPrediction):
        """
Cache a prediction result"""
        if not self.enabled:
            return
        
        cache_key = self._generate_cache_key(prediction.model_id, prediction.input_data)
        
        # Manage cache size
        if len(self.cache) >= self.max_size:
            await self._evict_oldest_entries()
        
        self.cache[cache_key] = prediction
        self.cache_timestamps[cache_key] = time.time()
    
    def _generate_cache_key(self, model_id: str, input_data: Any) -> str:
        """
Generate cache key for input"""
        data_str = str(input_data)
        key_string = f"{model_id}:{data_str}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    async def _evict_oldest_entries(self):
        """Evict oldest cache entries"""
        # Remove 20% of oldest entries
        num_to_remove = max(1, len(self.cache) // 5)
        
        # Sort by timestamp
        sorted_entries = sorted(self.cache_timestamps.items(), key=lambda x: x[1])
        
        for cache_key, _ in sorted_entries[:num_to_remove]:
            if cache_key in self.cache:
                del self.cache[cache_key]
            if cache_key in self.cache_timestamps:
                del self.cache_timestamps[cache_key]

class ModelPerformanceMonitor:
    """
Monitors model performance metrics"""
    
    def __init__(self):
        self.metrics = defaultdict(lambda: {
            'total_predictions': 0,
            'successful_predictions': 0,
            'total_processing_time': 0.0,
            'error_count': 0,
            'last_updated': datetime.utcnow()
        })
    
    async def record_prediction(self, model_id: str, processing_time: float, success: bool):
        """
Record a single prediction"""
        metrics = self.metrics[model_id]
        
        metrics['total_predictions'] += 1
        metrics['total_processing_time'] += processing_time
        metrics['last_updated'] = datetime.utcnow()
        
        if success:
            metrics['successful_predictions'] += 1
        else:
            metrics['error_count'] += 1
    
    async def record_batch_prediction(self, model_id: str, batch_size: int, 
                                    processing_time: float, success: bool):
        """
Record batch prediction"""
        metrics = self.metrics[model_id]
        
        metrics['total_predictions'] += batch_size
        metrics['total_processing_time'] += processing_time
        metrics['last_updated'] = datetime.utcnow()
        
        if success:
            metrics['successful_predictions'] += batch_size
        else:
            metrics['error_count'] += batch_size
    
    async def get_metrics(self, model_id: str = None) -> Dict[str, Any]:
        """
Get performance metrics"""
        if model_id:
            if model_id in self.metrics:
                metrics = self.metrics[model_id]
                return {
                    'model_id': model_id,
                    'total_predictions': metrics['total_predictions'],
                    'success_rate': metrics['successful_predictions'] / max(metrics['total_predictions'], 1),
                    'error_rate': metrics['error_count'] / max(metrics['total_predictions'], 1),
                    'average_processing_time': metrics['total_processing_time'] / max(metrics['total_predictions'], 1),
                    'last_updated': metrics['last_updated'].isoformat()
                }
            else:
                return {'error': f'No metrics found for model: {model_id}'}
        else:
            # Return metrics for all models
            all_metrics = {}
            for mid, metrics in self.metrics.items():
                all_metrics[mid] = {
                    'total_predictions': metrics['total_predictions'],
                    'success_rate': metrics['successful_predictions'] / max(metrics['total_predictions'], 1),
                    'average_processing_time': metrics['total_processing_time'] / max(metrics['total_predictions'], 1)
                }
            return all_metrics

class ResourceManager:
    """
Manages computational resources"""
    
    def __init__(self):
        self.memory_usage = 0
        self.cpu_usage = 0
        self.gpu_usage = 0
    
    async def check_resources(self, model_config: ModelConfig) -> bool:
        """
Check if resources are available for model"""
        # Simplified resource checking
        # In production, this would check actual system resources
        return True
    
    async def get_resource_usage(self) -> Dict[str, float]:
        """
Get current resource usage"""
        return {
            'memory_usage_mb': self.memory_usage,
            'cpu_usage_percent': self.cpu_usage,
            'gpu_usage_percent': self.gpu_usage
        }

# Utility functions
async def create_model_manager(config: Dict[str, Any] = None) -> AdvancedModelManager:
    """
Create and initialize model manager"""
    manager = AdvancedModelManager(config)
    return manager

async def load_essential_models(manager: AdvancedModelManager) -> bool:
    """
Load essential models for NLP operations"""
    essential_models = ['sentiment_v1', 'classification_v2', 'embeddings_v1']
    
    success_count = 0
    for model_id in essential_models:
        if await manager.load_model(model_id):
            success_count += 1
        else:
            logger.warning(f"Failed to load essential model: {model_id}")
    
    logger.info(f"Loaded {success_count}/{len(essential_models)} essential models")
    return success_count == len(essential_models)
