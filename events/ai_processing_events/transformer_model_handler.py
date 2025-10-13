"""Transformer Model Handler

Enterprise-grade transformer model handling system for the IA Influencer Agent platform.
Provides specialized handling for transformer-based models including BERT, GPT, T5, and other
attention-based architectures with optimized inference, fine-tuning, and deployment capabilities.

This module handles transformer models following the business logic:
Model Loading → Configuration → Fine-tuning → Inference → Optimization → Deployment

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is proprietary and confidential. Unauthorized use, reproduction,
or distribution without explicit written permission from Fahed Mlaiel (mlaiel@live.de)
is strictly prohibited and may result in legal action.
"""

import logging
import asyncio
import threading
import time
import json
from typing import Dict, Any, Optional, List, Union, Callable, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import hashlib

# Core imports
from ..core.base_event_handler import BaseEventHandler
from ..core.event_priority import EventPriority
from ..core.event_status import EventStatus

logger = logging.getLogger(__name__)

class TransformerType(Enum):
    """Transformer model types"""
    
    BERT = "bert"
    GPT = "gpt"
    T5 = "t5"
    ROBERTA = "roberta"
    ALBERT = "albert"
    DISTILBERT = "distilbert"
    ELECTRA = "electra"
    DEBERTA = "deberta"
    BLOOM = "bloom"
    GPT_NEO = "gpt_neo"
    CLIP = "clip"
    DALLE = "dalle"
    WHISPER = "whisper"
    CODEGEN = "codegen"
    INSTRUCTION_GPT = "instruction_gpt"

class TaskType(Enum):
    """Supported task types for transformers"""
    
    TEXT_CLASSIFICATION = "text_classification"
    TOKEN_CLASSIFICATION = "token_classification"
    QUESTION_ANSWERING = "question_answering"
    TEXT_GENERATION = "text_generation"
    SUMMARIZATION = "summarization"
    TRANSLATION = "translation"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    NAMED_ENTITY_RECOGNITION = "named_entity_recognition"
    LANGUAGE_MODELING = "language_modeling"
    FEATURE_EXTRACTION = "feature_extraction"
    EMBEDDING_GENERATION = "embedding_generation"
    SIMILARITY_SEARCH = "similarity_search"
    CONTENT_MODERATION = "content_moderation"
    CREATIVE_WRITING = "creative_writing"
    CODE_GENERATION = "code_generation"

class OptimizationLevel(Enum):
    """Model optimization levels"""
    
    NONE = "none"
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    MAXIMUM = "maximum"

class ModelState(Enum):
    """Transformer model states"""
    
    UNLOADED = "unloaded"
    LOADING = "loading"
    LOADED = "loaded"
    FINE_TUNING = "fine_tuning"
    OPTIMIZING = "optimizing"
    READY = "ready"
    BUSY = "busy"
    ERROR = "error"

@dataclass
class TransformerConfig:
    """Transformer model configuration"""
    
    model_id: str
    model_name: str
    transformer_type: TransformerType
    task_type: TaskType
    model_path: Optional[str] = None
    tokenizer_path: Optional[str] = None
    config_path: Optional[str] = None
    vocab_size: int = 50000
    hidden_size: int = 768
    num_layers: int = 12
    num_attention_heads: int = 12
    intermediate_size: int = 3072
    max_position_embeddings: int = 512
    dropout_rate: float = 0.1
    attention_dropout: float = 0.1
    layer_norm_eps: float = 1e-12
    use_cache: bool = True
    optimization_level: OptimizationLevel = OptimizationLevel.BASIC
    quantization_enabled: bool = False
    mixed_precision: bool = False
    gradient_checkpointing: bool = False
    custom_config: Dict[str, Any] = field(default_factory=dict)
    
    def get_memory_estimate(self) -> int:
        """Estimate memory usage in MB"""
        # Rough estimation based on model parameters
        param_count = self.vocab_size * self.hidden_size  # Embedding layer
        param_count += self.num_layers * (
            4 * self.hidden_size * self.hidden_size +  # Attention weights
            2 * self.hidden_size * self.intermediate_size  # FFN weights
        )
        
        # Each parameter is typically 4 bytes (float32)
        memory_mb = (param_count * 4) / (1024 * 1024)
        
        # Add overhead for activations and caching
        memory_mb *= 1.5
        
        # Adjust for optimization level
        if self.quantization_enabled:
            memory_mb *= 0.5
        if self.mixed_precision:
            memory_mb *= 0.75
        
        return int(memory_mb)

@dataclass
class TransformerInferenceRequest:
    """Transformer inference request"""
    
    request_id: str
    model_id: str
    task_type: TaskType
    input_data: Union[str, List[str], Dict[str, Any]]
    generation_config: Dict[str, Any] = field(default_factory=dict)
    tokenization_config: Dict[str, Any] = field(default_factory=dict)
    post_processing_config: Dict[str, Any] = field(default_factory=dict)
    return_attention_weights: bool = False
    return_hidden_states: bool = False
    max_length: Optional[int] = None
    temperature: float = 1.0
    top_p: float = 0.9
    top_k: int = 50
    num_return_sequences: int = 1
    do_sample: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert request to dictionary"""
        return {
            'request_id': self.request_id,
            'model_id': self.model_id,
            'task_type': self.task_type.value,
            'input_data': self.input_data,
            'generation_config': self.generation_config,
            'tokenization_config': self.tokenization_config,
            'post_processing_config': self.post_processing_config,
            'return_attention_weights': self.return_attention_weights,
            'return_hidden_states': self.return_hidden_states,
            'max_length': self.max_length,
            'temperature': self.temperature,
            'top_p': self.top_p,
            'top_k': self.top_k,
            'num_return_sequences': self.num_return_sequences,
            'do_sample': self.do_sample,
            'created_at': self.created_at.isoformat()
        }

@dataclass
class TransformerInferenceResult:
    """Transformer inference result"""
    
    request_id: str
    model_id: str
    task_type: TaskType
    success: bool
    outputs: Any = None
    attention_weights: Optional[List[np.ndarray]] = None
    hidden_states: Optional[List[np.ndarray]] = None
    logits: Optional[np.ndarray] = None
    confidence_scores: Optional[List[float]] = None
    processing_time: float = 0.0
    tokenization_time: float = 0.0
    inference_time: float = 0.0
    post_processing_time: float = 0.0
    token_count: int = 0
    memory_used: int = 0  # MB
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    completed_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary"""
        return {
            'request_id': self.request_id,
            'model_id': self.model_id,
            'task_type': self.task_type.value,
            'success': self.success,
            'outputs': self.outputs,
            'confidence_scores': self.confidence_scores,
            'processing_time': self.processing_time,
            'tokenization_time': self.tokenization_time,
            'inference_time': self.inference_time,
            'post_processing_time': self.post_processing_time,
            'token_count': self.token_count,
            'memory_used': self.memory_used,
            'error_message': self.error_message,
            'metadata': self.metadata,
            'completed_at': self.completed_at.isoformat()
        }

class TransformerModelInstance(ABC):
    """Abstract transformer model instance"""
    
    def __init__(self, config: TransformerConfig):
        self.config = config
        self.model = None
        self.tokenizer = None
        self.state = ModelState.UNLOADED
        self.load_time = None
        self.last_inference_time = None
        self.total_inferences = 0
        self.total_tokens_processed = 0
        self.average_inference_time = 0.0
        self.lock = threading.RLock()
    
    @abstractmethod
    async def load_model(self) -> bool:
        """Load the transformer model"""
        pass
    
    @abstractmethod
    async def unload_model(self) -> bool:
        """Unload the transformer model"""
        pass
    
    @abstractmethod
    async def inference(self, request: TransformerInferenceRequest) -> TransformerInferenceResult:
        """Run transformer inference"""
        pass
    
    @abstractmethod
    async def fine_tune(self, 
                       training_data: Any, 
                       validation_data: Optional[Any] = None,
                       training_config: Optional[Dict[str, Any]] = None) -> bool:
        """Fine-tune the transformer model"""
        pass
    
    def update_performance_stats(self, inference_time: float, token_count: int):
        """Update model performance statistics"""
        with self.lock:
            self.total_inferences += 1
            self.total_tokens_processed += token_count
            self.last_inference_time = inference_time
            
            if self.average_inference_time == 0.0:
                self.average_inference_time = inference_time
            else:
                # Exponential moving average
                alpha = 0.1
                self.average_inference_time = (alpha * inference_time + 
                                             (1 - alpha) * self.average_inference_time)
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get model performance statistics"""
        with self.lock:
            tokens_per_second = 0.0
            if self.average_inference_time > 0:
                avg_tokens = self.total_tokens_processed / max(self.total_inferences, 1)
                tokens_per_second = avg_tokens / self.average_inference_time
            
            return {
                'model_id': self.config.model_id,
                'transformer_type': self.config.transformer_type.value,
                'state': self.state.value,
                'total_inferences': self.total_inferences,
                'total_tokens_processed': self.total_tokens_processed,
                'average_inference_time': self.average_inference_time,
                'tokens_per_second': tokens_per_second,
                'load_time': self.load_time.isoformat() if self.load_time else None,
                'memory_estimate': self.config.get_memory_estimate()
            }

class DummyTransformerInstance(TransformerModelInstance):
    """Dummy transformer instance for testing"""
    
    async def load_model(self) -> bool:
        """Load dummy transformer model"""
        try:
            self.state = ModelState.LOADING
            
            # Simulate model loading time
            await asyncio.sleep(2.0)
            
            # Create dummy model and tokenizer
            self.model = f"dummy_{self.config.transformer_type.value}_model"
            self.tokenizer = f"dummy_{self.config.transformer_type.value}_tokenizer"
            
            self.state = ModelState.LOADED
            self.load_time = datetime.now()
            
            logger.info(f"Dummy transformer model {self.config.model_id} loaded")
            return True
            
        except Exception as e:
            self.state = ModelState.ERROR
            logger.error(f"Failed to load dummy transformer {self.config.model_id}: {str(e)}")
            return False
    
    async def unload_model(self) -> bool:
        """Unload dummy transformer model"""
        try:
            self.model = None
            self.tokenizer = None
            self.state = ModelState.UNLOADED
            
            logger.info(f"Dummy transformer model {self.config.model_id} unloaded")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unload dummy transformer {self.config.model_id}: {str(e)}")
            return False
    
    async def inference(self, request: TransformerInferenceRequest) -> TransformerInferenceResult:
        """Run dummy transformer inference"""
        start_time = time.time()
        
        result = TransformerInferenceResult(
            request_id=request.request_id,
            model_id=request.model_id,
            task_type=request.task_type,
            success=False
        )
        
        try:
            if self.state != ModelState.LOADED:
                raise RuntimeError(f"Model not loaded, current state: {self.state}")
            
            self.state = ModelState.BUSY
            
            # Tokenization simulation
            tokenization_start = time.time()
            
            # Simulate tokenization
            if isinstance(request.input_data, str):
                token_count = len(request.input_data.split()) * 1.3  # Rough estimation
            elif isinstance(request.input_data, list):
                token_count = sum(len(text.split()) * 1.3 for text in request.input_data)
            else:
                token_count = 50  # Default
            
            token_count = int(token_count)
            result.token_count = token_count
            result.tokenization_time = time.time() - tokenization_start
            
            # Inference simulation
            inference_start = time.time()
            
            # Simulate inference time based on model size and token count
            base_inference_time = self.config.hidden_size / 10000.0  # Larger models take longer
            token_factor = token_count / 100.0
            inference_time = max(0.01, base_inference_time * token_factor)
            
            await asyncio.sleep(inference_time)
            
            result.inference_time = time.time() - inference_start
            
            # Post-processing simulation
            post_processing_start = time.time()
            
            # Generate dummy outputs based on task type
            outputs = self._generate_dummy_outputs(request)
            result.outputs = outputs
            
            # Generate dummy confidence scores
            if request.num_return_sequences > 1:
                result.confidence_scores = [
                    np.random.uniform(0.7, 0.95) for _ in range(request.num_return_sequences)
                ]
            else:
                result.confidence_scores = [np.random.uniform(0.8, 0.95)]
            
            result.post_processing_time = time.time() - post_processing_start
            
            # Generate attention weights if requested
            if request.return_attention_weights:
                num_layers = self.config.num_layers
                num_heads = self.config.num_attention_heads
                seq_length = min(token_count, 20)  # Limit for dummy data
                
                result.attention_weights = [
                    np.random.rand(num_heads, seq_length, seq_length) 
                    for _ in range(num_layers)
                ]
            
            # Generate hidden states if requested
            if request.return_hidden_states:
                hidden_size = self.config.hidden_size
                seq_length = min(token_count, 20)
                
                result.hidden_states = [
                    np.random.rand(seq_length, hidden_size) 
                    for _ in range(self.config.num_layers + 1)  # +1 for embeddings
                ]
            
            result.success = True
            result.processing_time = time.time() - start_time
            result.memory_used = self.config.get_memory_estimate()
            
            # Update performance stats
            self.update_performance_stats(result.inference_time, token_count)
            
            logger.debug(f"Dummy transformer inference completed for {request.request_id}")
            
        except Exception as e:
            result.error_message = str(e)
            result.processing_time = time.time() - start_time
            logger.error(f"Dummy transformer inference failed for {request.request_id}: {str(e)}")
        
        finally:
            self.state = ModelState.LOADED
        
        return result
    
    def _generate_dummy_outputs(self, request: TransformerInferenceRequest) -> Any:
        """Generate dummy outputs based on task type"""
        task_type = request.task_type
        
        if task_type == TaskType.TEXT_CLASSIFICATION:
            # Return classification results
            labels = ["positive", "negative", "neutral"]
            scores = np.random.dirichlet([1, 1, 1])
            return {
                "labels": labels,
                "scores": scores.tolist(),
                "predicted_label": labels[np.argmax(scores)]
            }
        
        elif task_type == TaskType.TEXT_GENERATION:
            # Return generated text
            if isinstance(request.input_data, str):
                prompt = request.input_data[:50]  # Use first 50 chars as reference
            else:
                prompt = "Generated"
            
            generated_texts = []
            for i in range(request.num_return_sequences):
                generated_text = f"{prompt} continuation {i+1} with additional content..."
                generated_texts.append(generated_text)
            
            return generated_texts if len(generated_texts) > 1 else generated_texts[0]
        
        elif task_type == TaskType.QUESTION_ANSWERING:
            # Return QA result
            return {
                "answer": "This is a dummy answer based on the context provided.",
                "start": 0,
                "end": 10,
                "score": np.random.uniform(0.8, 0.95)
            }
        
        elif task_type == TaskType.SUMMARIZATION:
            # Return summary
            return {
                "summary_text": "This is a dummy summary of the input text content.",
                "compression_ratio": np.random.uniform(0.2, 0.4)
            }
        
        elif task_type == TaskType.TRANSLATION:
            # Return translation
            return {
                "translation_text": "This is a dummy translation of the input text.",
                "source_language": "auto",
                "target_language": "en"
            }
        
        elif task_type == TaskType.SENTIMENT_ANALYSIS:
            # Return sentiment
            sentiment_score = np.random.uniform(-1, 1)
            return {
                "sentiment": "positive" if sentiment_score > 0.1 else "negative" if sentiment_score < -0.1 else "neutral",
                "score": sentiment_score,
                "confidence": abs(sentiment_score)
            }
        
        elif task_type == TaskType.NAMED_ENTITY_RECOGNITION:
            # Return NER results
            return {
                "entities": [
                    {"text": "Example Entity", "label": "PERSON", "start": 0, "end": 14, "confidence": 0.9},
                    {"text": "Organization", "label": "ORG", "start": 20, "end": 32, "confidence": 0.85}
                ]
            }
        
        elif task_type == TaskType.FEATURE_EXTRACTION:
            # Return feature vectors
            feature_dim = self.config.hidden_size
            if isinstance(request.input_data, list):
                return [np.random.rand(feature_dim).tolist() for _ in request.input_data]
            else:
                return np.random.rand(feature_dim).tolist()
        
        elif task_type == TaskType.EMBEDDING_GENERATION:
            # Return embeddings
            embedding_dim = self.config.hidden_size
            if isinstance(request.input_data, list):
                return [np.random.rand(embedding_dim).tolist() for _ in request.input_data]
            else:
                return np.random.rand(embedding_dim).tolist()
        
        else:
            # Default output
            return {
                "result": "Dummy output for unsupported task type",
                "task_type": task_type.value
            }
    
    async def fine_tune(self, 
                       training_data: Any, 
                       validation_data: Optional[Any] = None,
                       training_config: Optional[Dict[str, Any]] = None) -> bool:
        """Simulate fine-tuning"""
        try:
            self.state = ModelState.FINE_TUNING
            
            # Simulate fine-tuning time
            await asyncio.sleep(5.0)
            
            self.state = ModelState.LOADED
            
            logger.info(f"Dummy fine-tuning completed for {self.config.model_id}")
            return True
            
        except Exception as e:
            self.state = ModelState.ERROR
            logger.error(f"Dummy fine-tuning failed for {self.config.model_id}: {str(e)}")
            return False

class TransformerModelHandler(BaseEventHandler):
    """
    Enterprise Transformer Model Handler
    
    Provides specialized handling for transformer-based models including BERT, GPT, T5,
    and other attention-based architectures with optimized inference, fine-tuning,
    and deployment capabilities for the IA Influencer Agent platform.
    """
    
    def __init__(self, max_models: int = 10, max_workers: int = 4):
        super().__init__()
        
        self.max_models = max_models
        self.max_workers = max_workers
        
        # Model management
        self.model_configs: Dict[str, TransformerConfig] = {}
        self.model_instances: Dict[str, TransformerModelInstance] = {}
        self.model_usage_order: List[str] = []  # LRU tracking
        
        # Request processing
        self.request_queue = asyncio.Queue(maxsize=1000)
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
        # Performance tracking
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.average_processing_time = 0.0
        
        # Task-specific optimizations
        self.task_optimizations = {
            TaskType.TEXT_GENERATION: {'batch_size': 1, 'use_cache': True},
            TaskType.TEXT_CLASSIFICATION: {'batch_size': 8, 'use_cache': False},
            TaskType.FEATURE_EXTRACTION: {'batch_size': 16, 'use_cache': False}
        }
        
        self.is_running = False
        self.lock = threading.RLock()
        
        logger.info("Transformer Model Handler initialized")
    
    async def start_handler(self):
        """Start the transformer model handler"""
        self.is_running = True
        
        # Start worker tasks
        for i in range(self.max_workers):
            asyncio.create_task(self._worker_loop(f"transformer_worker_{i}"))
        
        # Start monitoring tasks
        asyncio.create_task(self._monitor_performance())
        asyncio.create_task(self._optimize_model_allocation())
        
        logger.info("Transformer Model Handler started")
    
    async def stop_handler(self):
        """Stop the transformer model handler"""
        self.is_running = False
        
        # Unload all models
        for model_id in list(self.model_instances.keys()):
            await self.unload_model(model_id)
        
        # Shutdown executor
        self.executor.shutdown(wait=True)
        
        logger.info("Transformer Model Handler stopped")
    
    async def register_model(self, config: TransformerConfig) -> bool:
        """Register a transformer model configuration"""
        try:
            with self.lock:
                self.model_configs[config.model_id] = config
            
            logger.info(f"Transformer model {config.model_id} registered successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register transformer model {config.model_id}: {str(e)}")
            return False
    
    async def load_model(self, model_id: str) -> bool:
        """Load a transformer model"""
        try:
            config = self.model_configs.get(model_id)
            if not config:
                logger.error(f"Model {model_id} not registered")
                return False
            
            # Check if model is already loaded
            if model_id in self.model_instances:
                logger.info(f"Model {model_id} already loaded")
                return True
            
            # Check if we need to unload models due to limit
            if len(self.model_instances) >= self.max_models:
                await self._unload_lru_model()
            
            # Create model instance (using dummy implementation)
            model_instance = DummyTransformerInstance(config)
            
            # Load the model
            success = await model_instance.load_model()
            if success:
                with self.lock:
                    self.model_instances[model_id] = model_instance
                    self.model_usage_order.append(model_id)
                
                logger.info(f"Transformer model {model_id} loaded successfully")
                return True
            else:
                logger.error(f"Failed to load transformer model {model_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error loading transformer model {model_id}: {str(e)}")
            return False
    
    async def unload_model(self, model_id: str) -> bool:
        """Unload a transformer model"""
        try:
            with self.lock:
                model_instance = self.model_instances.get(model_id)
                if not model_instance:
                    logger.warning(f"Model {model_id} not loaded")
                    return False
                
                # Unload the model
                success = await model_instance.unload_model()
                if success:
                    del self.model_instances[model_id]
                    if model_id in self.model_usage_order:
                        self.model_usage_order.remove(model_id)
                    
                    logger.info(f"Transformer model {model_id} unloaded successfully")
                    return True
                else:
                    logger.error(f"Failed to unload transformer model {model_id}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error unloading transformer model {model_id}: {str(e)}")
            return False
    
    async def submit_inference_request(self, request: TransformerInferenceRequest) -> str:
        """Submit a transformer inference request"""
        try:
            # Validate request
            if not self._validate_request(request):
                raise ValueError("Invalid transformer inference request")
            
            # Check if model is loaded
            if request.model_id not in self.model_instances:
                # Try to load the model
                success = await self.load_model(request.model_id)
                if not success:
                    raise RuntimeError(f"Failed to load model {request.model_id}")
            
            # Add to queue
            await self.request_queue.put(request)
            self.total_requests += 1
            
            logger.debug(f"Transformer inference request {request.request_id} queued")
            return request.request_id
            
        except Exception as e:
            logger.error(f"Failed to submit transformer inference request: {str(e)}")
            raise
    
    def _validate_request(self, request: TransformerInferenceRequest) -> bool:
        """Validate transformer inference request"""
        try:
            # Check if model is registered
            if request.model_id not in self.model_configs:
                logger.error(f"Model {request.model_id} not registered")
                return False
            
            # Check input data
            if request.input_data is None:
                logger.error("Input data is required")
                return False
            
            # Validate task type compatibility
            config = self.model_configs[request.model_id]
            if config.task_type != request.task_type:
                logger.warning(f"Task type mismatch: model configured for {config.task_type}, "
                             f"request for {request.task_type}")
            
            return True
            
        except Exception as e:
            logger.error(f"Request validation error: {str(e)}")
            return False
    
    async def _worker_loop(self, worker_id: str):
        """Main worker loop for processing inference requests"""
        logger.info(f"Transformer worker {worker_id} started")
        
        while self.is_running:
            try:
                # Get next request from queue
                request = await asyncio.wait_for(
                    self.request_queue.get(),
                    timeout=1.0
                )
                
                # Process the request
                result = await self._process_inference_request(request)
                
                # Update statistics
                if result.success:
                    self.successful_requests += 1
                else:
                    self.failed_requests += 1
                
                self._update_performance_metrics(result)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Transformer worker {worker_id} error: {str(e)}")
                await asyncio.sleep(1.0)
        
        logger.info(f"Transformer worker {worker_id} stopped")
    
    async def _process_inference_request(self, request: TransformerInferenceRequest) -> TransformerInferenceResult:
        """Process a single transformer inference request"""
        try:
            # Get model instance
            model_instance = self.model_instances.get(request.model_id)
            if not model_instance:
                raise RuntimeError(f"Model {request.model_id} not available")
            
            # Update model usage order
            self._update_model_usage(request.model_id)
            
            # Apply task-specific optimizations
            self._apply_task_optimizations(request)
            
            # Run inference
            result = await model_instance.inference(request)
            
            logger.debug(f"Transformer inference completed for {request.request_id}")
            return result
            
        except Exception as e:
            # Create error result
            result = TransformerInferenceResult(
                request_id=request.request_id,
                model_id=request.model_id,
                task_type=request.task_type,
                success=False,
                error_message=str(e)
            )
            
            logger.error(f"Transformer inference failed for {request.request_id}: {str(e)}")
            return result
    
    def _apply_task_optimizations(self, request: TransformerInferenceRequest):
        """Apply task-specific optimizations to request"""
        task_opts = self.task_optimizations.get(request.task_type, {})
        
        for key, value in task_opts.items():
            if key not in request.generation_config:
                request.generation_config[key] = value
    
    def _update_model_usage(self, model_id: str):
        """Update model usage order for LRU tracking"""
        with self.lock:
            if model_id in self.model_usage_order:
                self.model_usage_order.remove(model_id)
                self.model_usage_order.append(model_id)
    
    def _update_performance_metrics(self, result: TransformerInferenceResult):
        """Update handler performance metrics"""
        # Update average processing time
        if self.total_requests > 0:
            alpha = 0.1
            self.average_processing_time = (alpha * result.processing_time + 
                                          (1 - alpha) * self.average_processing_time)
    
    async def _unload_lru_model(self):
        """Unload least recently used model"""
        if self.model_usage_order:
            lru_model_id = self.model_usage_order[0]
            logger.info(f"Unloading LRU transformer model: {lru_model_id}")
            await self.unload_model(lru_model_id)
    
    async def _monitor_performance(self):
        """Monitor transformer handler performance"""
        while self.is_running:
            try:
                stats = self.get_handler_stats()
                logger.info(f"Transformer Handler Stats: {json.dumps(stats, indent=2)}")
                
                # Check for performance issues
                if stats['success_rate'] < 0.95:
                    logger.warning(f"Low success rate: {stats['success_rate']:.2%}")
                
                if stats['average_processing_time'] > 5.0:
                    logger.warning(f"High processing time: {stats['average_processing_time']:.2f}s")
                
                await asyncio.sleep(300)  # Monitor every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in transformer performance monitoring: {str(e)}")
                await asyncio.sleep(300)
    
    async def _optimize_model_allocation(self):
        """Optimize model allocation based on usage patterns"""
        while self.is_running:
            try:
                # Analyze model usage and unload unused models
                current_time = datetime.now()
                
                for model_id, instance in list(self.model_instances.items()):
                    stats = instance.get_performance_stats()
                    
                    # Unload models with very low usage
                    if (stats['total_inferences'] < 5 and 
                        instance.load_time and
                        (current_time - instance.load_time).total_seconds() > 3600):  # 1 hour
                        
                        logger.info(f"Unloading underused transformer model: {model_id}")
                        await self.unload_model(model_id)
                
                await asyncio.sleep(600)  # Optimize every 10 minutes
                
            except Exception as e:
                logger.error(f"Error in transformer model optimization: {str(e)}")
                await asyncio.sleep(600)
    
    def get_handler_stats(self) -> Dict[str, Any]:
        """Get comprehensive handler statistics"""
        success_rate = self.successful_requests / max(self.total_requests, 1)
        
        with self.lock:
            model_stats = {}
            for model_id, instance in self.model_instances.items():
                model_stats[model_id] = instance.get_performance_stats()
            
            transformer_types = {}
            for config in self.model_configs.values():
                t_type = config.transformer_type.value
                transformer_types[t_type] = transformer_types.get(t_type, 0) + 1
        
        return {
            'total_requests': self.total_requests,
            'successful_requests': self.successful_requests,
            'failed_requests': self.failed_requests,
            'success_rate': success_rate,
            'average_processing_time': self.average_processing_time,
            'queue_size': self.request_queue.qsize(),
            'loaded_models': len(self.model_instances),
            'registered_models': len(self.model_configs),
            'transformer_types': transformer_types,
            'model_performance': model_stats,
            'is_running': self.is_running
        }
    
    async def handle_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle transformer model events"""
        try:
            event_type = event_data.get('event_type')
            
            if event_type == 'inference_request':
                # Create inference request from event data
                request = TransformerInferenceRequest(
                    request_id=event_data.get('request_id', f"transformer_{int(time.time())}"),
                    model_id=event_data.get('model_id'),
                    task_type=TaskType(event_data.get('task_type')),
                    input_data=event_data.get('input_data'),
                    generation_config=event_data.get('generation_config', {}),
                    max_length=event_data.get('max_length'),
                    temperature=event_data.get('temperature', 1.0),
                    top_p=event_data.get('top_p', 0.9),
                    top_k=event_data.get('top_k', 50)
                )
                
                # Submit request
                request_id = await self.submit_inference_request(request)
                
                return {
                    'status': 'success',
                    'request_id': request_id,
                    'message': 'Transformer inference request submitted successfully'
                }
            
            elif event_type == 'load_model':
                model_id = event_data.get('model_id')
                success = await self.load_model(model_id)
                
                return {
                    'status': 'success' if success else 'error',
                    'message': f'Model {model_id} loaded' if success else f'Failed to load model {model_id}'
                }
            
            elif event_type == 'unload_model':
                model_id = event_data.get('model_id')
                success = await self.unload_model(model_id)
                
                return {
                    'status': 'success' if success else 'error',
                    'message': f'Model {model_id} unloaded' if success else f'Failed to unload model {model_id}'
                }
            
            elif event_type == 'get_stats':
                stats = self.get_handler_stats()
                return {
                    'status': 'success',
                    'handler_stats': stats
                }
            
            else:
                return {
                    'status': 'error',
                    'message': f'Unknown event type: {event_type}'
                }
                
        except Exception as e:
            logger.error(f"Error handling transformer model event: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }

# Export classes and functions
__all__ = [
    'TransformerType',
    'TaskType',
    'OptimizationLevel',
    'ModelState',
    'TransformerConfig',
    'TransformerInferenceRequest',
    'TransformerInferenceResult',
    'TransformerModelInstance',
    'DummyTransformerInstance',
    'TransformerModelHandler'
]