"""
Embedding Generator

This module provides advanced embedding generation for multiple content types
with support for multiple models, fine-tuning, and optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

WARNING: This code is proprietary to Fahed Mlaiel. Any unauthorized copying, modification, 
or distribution without explicit written permission is strictly prohibited and will result 
in legal action under German and international copyright law.
"""

import os
import json
import logging
import asyncio
from typing import Dict, List, Optional, Tuple, Any, Union, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from enum import Enum
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image
import librosa
import cv2
from transformers import (
    AutoModel, AutoTokenizer, AutoProcessor,
    CLIPModel, CLIPProcessor,
    Wav2Vec2Model, Wav2Vec2Processor,
    BertModel, BertTokenizer,
    ViTModel, ViTProcessor,
    AutoFeatureExtractor
)
from sentence_transformers import SentenceTransformer
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from backend.core.config import get_settings
from backend.core.database import get_db_session
from backend.models.content_fingerprints import ContentFingerprint
from backend.utils.exceptions import EmbeddingError, ModelError
from backend.utils.performance import measure_execution_time
from backend.utils.caching import CacheManager
from backend.utils.file_processing import FileProcessor

logger = logging.getLogger(__name__)
settings = get_settings()


class EmbeddingModel(Enum):
    """Supported embedding models"""
    # Text models
    BERT_BASE = "bert-base-uncased"
    BERT_LARGE = "bert-large-uncased"
    SENTENCE_TRANSFORMER = "all-MiniLM-L6-v2"
    ROBERTA = "roberta-base"
    DISTILBERT = "distilbert-base-uncased"
    
    # Image models
    CLIP_VIT_B32 = "openai/clip-vit-base-patch32"
    CLIP_VIT_L14 = "openai/clip-vit-large-patch14"
    VIT_BASE = "google/vit-base-patch16-224"
    RESNET50 = "microsoft/resnet-50"
    
    # Audio models
    WAV2VEC2 = "facebook/wav2vec2-base-960h"
    HUBERT = "facebook/hubert-base-ls960"
    WHISPER = "openai/whisper-base"
    
    # Multi-modal models
    CLIP_MULTI = "openai/clip-vit-base-patch32"
    BLIP = "Salesforce/blip-image-captioning-base"


class ContentType(Enum):
    """Content types for embedding generation"""
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"


class EmbeddingStrategy(Enum):
    """Embedding generation strategies"""
    SINGLE_MODEL = "single_model"
    ENSEMBLE = "ensemble"
    HIERARCHICAL = "hierarchical"
    ADAPTIVE = "adaptive"
    FINE_TUNED = "fine_tuned"


@dataclass
class EmbeddingConfig:
    """Embedding generation configuration"""
    model_name: EmbeddingModel
    content_type: ContentType
    dimension: int
    normalize: bool = True
    strategy: EmbeddingStrategy = EmbeddingStrategy.SINGLE_MODEL
    ensemble_weights: Optional[List[float]] = None
    fine_tune_data: Optional[str] = None
    preprocessing_params: Optional[Dict[str, Any]] = None
    postprocessing_params: Optional[Dict[str, Any]] = None


@dataclass
class EmbeddingResult:
    """Embedding generation result"""
    content_id: str
    embedding: np.ndarray
    model_used: str
    generation_time: float
    confidence_score: float
    metadata: Dict[str, Any]
    preprocessing_info: Optional[Dict[str, Any]] = None
    quality_metrics: Optional[Dict[str, float]] = None


@dataclass
class ModelPerformance:
    """Model performance metrics"""
    model_name: str
    content_type: str
    total_generations: int
    avg_generation_time: float
    success_rate: float
    quality_score: float
    memory_usage_mb: float
    last_updated: datetime


class EmbeddingGenerator:
    """
    Advanced embedding generator for multi-modal content.
    
    Features:
    - Support for multiple embedding models (BERT, CLIP, Wav2Vec2, etc.)
    - Multi-modal embedding generation
    - Ensemble and hierarchical embedding strategies
    - Model fine-tuning capabilities
    - Adaptive model selection
    - Performance monitoring and optimization
    - Caching and batch processing
    """
    
    def __init__(
        self,
        cache_manager: CacheManager = None,
        file_processor: FileProcessor = None,
        device: str = "auto",
        max_batch_size: int = 32,
        enable_fine_tuning: bool = True
    ):
        """
        Initialize embedding generator
        
        Args:
            cache_manager: Cache manager for embeddings
            file_processor: File processing utilities
            device: Compute device (cpu, cuda, auto)
            max_batch_size: Maximum batch size for processing
            enable_fine_tuning: Enable model fine-tuning
        """
        self.cache_manager = cache_manager or CacheManager()
        self.file_processor = file_processor or FileProcessor()
        self.max_batch_size = max_batch_size
        self.enable_fine_tuning = enable_fine_tuning
        
        # Device configuration
        if device == "auto":
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)
        
        # Model storage
        self.models: Dict[str, Any] = {}
        self.tokenizers: Dict[str, Any] = {}
        self.processors: Dict[str, Any] = {}
        self.scalers: Dict[str, Any] = {}
        
        # Model configurations
        self.model_configs: Dict[str, EmbeddingConfig] = {}
        
        # Performance tracking
        self.model_performance: Dict[str, ModelPerformance] = {}
        
        # Generation statistics
        self.generation_stats = {
            "total_embeddings": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "avg_generation_time": 0.0,
            "batch_generations": 0,
            "errors": 0
        }
        
        # Content type specific configurations
        self.content_configs = self._initialize_content_configs()
        
        logger.info(
            f"Initialized EmbeddingGenerator - Device: {self.device}, "
            f"Batch Size: {max_batch_size}, Fine-tuning: {enable_fine_tuning}"
        )
    
    async def initialize(self) -> None:
        """Initialize embedding models and processors"""



        try:
            # Load default models for each content type
            await self._load_default_models()
            
            # Initialize scalers
            await self._initialize_scalers()
            
            logger.info("Embedding generator initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize embedding generator: {str(e)}")
            raise EmbeddingError(f"Embedding generator initialization failed: {str(e)}")
    
    @measure_execution_time
    async def generate_embedding(
        self,
        content: Union[str, np.ndarray, Image.Image],
        content_type: ContentType,
        content_id: str = None,
        config: EmbeddingConfig = None
    ) -> EmbeddingResult:
        """
        Generate embedding for content
        
        Args:
            content: Content to embed (text, image array, audio array, etc.)
            content_type: Type of content
            content_id: Optional content identifier
            config: Optional embedding configuration
            
        Returns:
            Embedding result with metadata
        """



        try:
            start_time = datetime.now()
            
            # Use default config if not provided
            if config is None:
                config = self.content_configs[content_type]
            
            # Generate cache key
            cache_key = self._generate_cache_key(content, content_type, config)
            
            # Check cache first
            cached_result = await self.cache_manager.get(cache_key)
            if cached_result:
                self.generation_stats["cache_hits"] += 1
                logger.debug(f"Retrieved cached embedding for {content_type.value}")
                return EmbeddingResult(**cached_result)
            
            self.generation_stats["cache_misses"] += 1
            
            # Preprocess content
            preprocessed_content = await self._preprocess_content(content, content_type, config)
            
            # Generate embedding based on strategy
            if config.strategy == EmbeddingStrategy.SINGLE_MODEL:
                embedding = await self._generate_single_model_embedding(
                    preprocessed_content, content_type, config
                )
            elif config.strategy == EmbeddingStrategy.ENSEMBLE:
                embedding = await self._generate_ensemble_embedding(
                    preprocessed_content, content_type, config
                )
            elif config.strategy == EmbeddingStrategy.HIERARCHICAL:
                embedding = await self._generate_hierarchical_embedding(
                    preprocessed_content, content_type, config
                )
            elif config.strategy == EmbeddingStrategy.ADAPTIVE:
                embedding = await self._generate_adaptive_embedding(
                    preprocessed_content, content_type, config
                )
            else:
                raise EmbeddingError(f"Unsupported strategy: {config.strategy}")
            
            # Post-process embedding
            final_embedding = await self._postprocess_embedding(embedding, config)
            
            # Calculate quality metrics
            quality_metrics = await self._calculate_quality_metrics(final_embedding, content_type)
            
            # Calculate confidence score
            confidence_score = await self._calculate_confidence_score(
                final_embedding, content_type, quality_metrics
            )
            
            # Create result
            generation_time = (datetime.now() - start_time).total_seconds()
            
            result = EmbeddingResult(
                content_id=content_id or f"temp_{datetime.now().timestamp()}",
                embedding=final_embedding,
                model_used=config.model_name.value,
                generation_time=generation_time,
                confidence_score=confidence_score,
                metadata={
                    "content_type": content_type.value,
                    "strategy": config.strategy.value,
                    "dimension": len(final_embedding),
                    "device": str(self.device),
                    "timestamp": datetime.now().isoformat()
                },
                quality_metrics=quality_metrics
            )
            
            # Cache result
            await self.cache_manager.set(
                cache_key, asdict(result), ttl=settings.EMBEDDING_CACHE_TTL
            )
            
            # Update statistics
            self._update_generation_stats(generation_time, True)
            self._update_model_performance(config.model_name.value, content_type, generation_time)
            
            logger.debug(
                f"Generated {content_type.value} embedding: dim={len(final_embedding)}, "
                f"time={generation_time:.3f}s, confidence={confidence_score:.3f}"
            )
            
            return result
            
        except Exception as e:
            self.generation_stats["errors"] += 1
            logger.error(f"Embedding generation failed: {str(e)}")
            raise EmbeddingError(f"Embedding generation failed: {str(e)}")
    
    @measure_execution_time
    async def generate_batch_embeddings(
        self,
        contents: List[Tuple[Union[str, np.ndarray, Image.Image], ContentType, str]],
        config: EmbeddingConfig = None
    ) -> List[EmbeddingResult]:
        """
        Generate embeddings for batch of content
        
        Args:
            contents: List of (content, content_type, content_id) tuples
            config: Optional embedding configuration
            
        Returns:
            List of embedding results
        """



        try:
            start_time = datetime.now()
            results = []
            
            # Group contents by type for efficient processing
            grouped_contents = {}
            for i, (content, content_type, content_id) in enumerate(contents):
                if content_type not in grouped_contents:
                    grouped_contents[content_type] = []
                grouped_contents[content_type].append((i, content, content_id))
            
            # Process each content type
            for content_type, type_contents in grouped_contents.items():
                # Use appropriate config for content type
                type_config = config or self.content_configs[content_type]
                
                # Process in batches
                for i in range(0, len(type_contents), self.max_batch_size):
                    batch = type_contents[i:i + self.max_batch_size]
                    batch_results = await self._process_content_batch(batch, content_type, type_config)
                    results.extend(batch_results)
            
            # Sort results by original order
            results.sort(key=lambda x: int(x.content_id.split('_')[1]) if '_' in x.content_id else 0)
            
            # Update batch statistics
            self.generation_stats["batch_generations"] += 1
            batch_time = (datetime.now() - start_time).total_seconds()
            
            logger.info(
                f"Generated {len(results)} batch embeddings in {batch_time:.3f}s "
                f"(avg: {batch_time/len(results):.3f}s per embedding)"
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Batch embedding generation failed: {str(e)}")
            raise EmbeddingError(f"Batch embedding generation failed: {str(e)}")
    
    async def fine_tune_model(
        self,
        model_name: EmbeddingModel,
        content_type: ContentType,
        training_data: List[Tuple[Any, np.ndarray]],
        validation_data: List[Tuple[Any, np.ndarray]] = None,
        epochs: int = 5,
        learning_rate: float = 1e-5
    ) -> Dict[str, Any]:
        """
        Fine-tune embedding model on specific data
        
        Args:
            model_name: Model to fine-tune
            content_type: Content type for fine-tuning
            training_data: List of (content, target_embedding) pairs
            validation_data: Optional validation data
            epochs: Number of training epochs
            learning_rate: Learning rate for fine-tuning
            
        Returns:
            Fine-tuning results and metrics
        """



        try:
            if not self.enable_fine_tuning:
                raise EmbeddingError("Fine-tuning is disabled")
            
            logger.info(f"Starting fine-tuning for {model_name.value} on {content_type.value}")
            
            # Load base model
            model_key = f"{model_name.value}_{content_type.value}"
            if model_key not in self.models:
                await self._load_model(model_name, content_type)
            
            base_model = self.models[model_key]
            
            # Create fine-tuning adapter
            fine_tuned_model = await self._create_fine_tuning_adapter(
                base_model, content_type, training_data[0][1].shape[-1]
            )
            
            # Prepare data loaders
            train_loader = self._create_data_loader(training_data, batch_size=16)
            val_loader = None
            if validation_data:
                val_loader = self._create_data_loader(validation_data, batch_size=16)
            
            # Fine-tuning loop
            optimizer = torch.optim.AdamW(fine_tuned_model.parameters(), lr=learning_rate)
            criterion = nn.MSELoss()
            
            training_metrics = {
                "train_losses": [],
                "val_losses": [],
                "epochs": epochs,
                "learning_rate": learning_rate
            }
            
            for epoch in range(epochs):
                # Training phase
                fine_tuned_model.train()
                epoch_train_loss = 0.0
                
                for batch_idx, (inputs, targets) in enumerate(train_loader):
                    inputs, targets = inputs.to(self.device), targets.to(self.device)
                    
                    optimizer.zero_grad()
                    outputs = fine_tuned_model(inputs)
                    loss = criterion(outputs, targets)
                    loss.backward()
                    optimizer.step()
                    
                    epoch_train_loss += loss.item()
                
                avg_train_loss = epoch_train_loss / len(train_loader)
                training_metrics["train_losses"].append(avg_train_loss)
                
                # Validation phase
                if val_loader:
                    fine_tuned_model.eval()
                    epoch_val_loss = 0.0
                    
                    with torch.no_grad():
                        for inputs, targets in val_loader:
                            inputs, targets = inputs.to(self.device), targets.to(self.device)
                            outputs = fine_tuned_model(inputs)
                            loss = criterion(outputs, targets)
                            epoch_val_loss += loss.item()
                    
                    avg_val_loss = epoch_val_loss / len(val_loader)
                    training_metrics["val_losses"].append(avg_val_loss)
                    
                    logger.info(
                        f"Epoch {epoch+1}/{epochs}: "
                        f"Train Loss: {avg_train_loss:.4f}, Val Loss: {avg_val_loss:.4f}"
                    )
                else:
                    logger.info(f"Epoch {epoch+1}/{epochs}: Train Loss: {avg_train_loss:.4f}")
            
            # Save fine-tuned model
            fine_tuned_key = f"{model_key}_finetuned"
            self.models[fine_tuned_key] = fine_tuned_model
            
            # Update model config
            fine_tuned_config = EmbeddingConfig(
                model_name=model_name,
                content_type=content_type,
                dimension=training_data[0][1].shape[-1],
                strategy=EmbeddingStrategy.FINE_TUNED
            )
            self.model_configs[fine_tuned_key] = fine_tuned_config
            
            logger.info(f"Fine-tuning completed for {model_name.value}")
            return training_metrics
            
        except Exception as e:
            logger.error(f"Fine-tuning failed: {str(e)}")
            raise ModelError(f"Fine-tuning failed: {str(e)}")
    
    async def compare_models(
        self,
        content_samples: List[Tuple[Any, ContentType]],
        models: List[EmbeddingModel],
        metrics: List[str] = ["generation_time", "quality_score", "consistency"]
    ) -> Dict[str, Dict[str, float]]:
        """
        Compare performance of different embedding models
        
        Args:
            content_samples: Sample content for comparison
            models: Models to compare
            metrics: Metrics to evaluate
            
        Returns:
            Comparison results for each model
        """



        try:
            comparison_results = {}
            
            for model in models:
                model_results = {metric: 0.0 for metric in metrics}
                
                for content, content_type in content_samples:
                    config = EmbeddingConfig(
                        model_name=model,
                        content_type=content_type,
                        dimension=512  # Default dimension
                    )
                    
                    # Generate embedding
                    result = await self.generate_embedding(content, content_type, config=config)
                    
                    # Evaluate metrics
                    if "generation_time" in metrics:
                        model_results["generation_time"] += result.generation_time
                    
                    if "quality_score" in metrics and result.quality_metrics:
                        model_results["quality_score"] += result.quality_metrics.get("overall_quality", 0.0)
                    
                    if "consistency" in metrics:
                        # Generate again and check consistency
                        result2 = await self.generate_embedding(content, content_type, config=config)
                        consistency = np.corrcoef(result.embedding, result2.embedding)[0, 1]
                        model_results["consistency"] += consistency
                
                # Average the metrics
                num_samples = len(content_samples)
                for metric in metrics:
                    model_results[metric] /= num_samples
                
                comparison_results[model.value] = model_results
            
            logger.info(f"Model comparison completed for {len(models)} models")
            return comparison_results
            
        except Exception as e:
            logger.error(f"Model comparison failed: {str(e)}")
            raise EmbeddingError(f"Model comparison failed: {str(e)}")
    
    async def get_model_performance(self) -> Dict[str, ModelPerformance]:
        """Get performance metrics for all models"""



        return self.model_performance.copy()
    
    async def get_generation_statistics(self) -> Dict[str, Any]:
        """Get embedding generation statistics"""
        stats = self.generation_stats.copy()
        
        # Add cache efficiency
        total_requests = stats["cache_hits"] + stats["cache_misses"]
        stats["cache_hit_ratio"] = stats["cache_hits"] / max(total_requests, 1)
        
        # Add error rate
        stats["error_rate"] = stats["errors"] / max(stats["total_embeddings"], 1)
        
        return stats
    
    async def _load_default_models(self) -> None:
        """Load default models for each content type"""



        try:
            # Text models
            await self._load_model(EmbeddingModel.SENTENCE_TRANSFORMER, ContentType.TEXT)
            
            # Image models
            await self._load_model(EmbeddingModel.CLIP_VIT_B32, ContentType.IMAGE)
            
            # Audio models
            await self._load_model(EmbeddingModel.WAV2VEC2, ContentType.AUDIO)
            
            logger.info("Default models loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load default models: {str(e)}")
            raise ModelError(f"Default model loading failed: {str(e)}")
    
    async def _load_model(self, model_name: EmbeddingModel, content_type: ContentType) -> None:
        """Load a specific model and its components"""



        try:
            model_key = f"{model_name.value}_{content_type.value}"
            
            if model_key in self.models:
                return  # Already loaded
            
            logger.info(f"Loading model {model_name.value} for {content_type.value}")
            
            if content_type == ContentType.TEXT:
                if model_name == EmbeddingModel.SENTENCE_TRANSFORMER:
                    model = SentenceTransformer(model_name.value, device=str(self.device))
                    self.models[model_key] = model
                else:
                    model = AutoModel.from_pretrained(model_name.value).to(self.device)
                    tokenizer = AutoTokenizer.from_pretrained(model_name.value)
                    self.models[model_key] = model
                    self.tokenizers[model_key] = tokenizer
            
            elif content_type == ContentType.IMAGE:
                if "clip" in model_name.value.lower():
                    model = CLIPModel.from_pretrained(model_name.value).to(self.device)
                    processor = CLIPProcessor.from_pretrained(model_name.value)
                    self.models[model_key] = model
                    self.processors[model_key] = processor
                elif "vit" in model_name.value.lower():
                    model = ViTModel.from_pretrained(model_name.value).to(self.device)
                    processor = ViTProcessor.from_pretrained(model_name.value)
                    self.models[model_key] = model
                    self.processors[model_key] = processor
            
            elif content_type == ContentType.AUDIO:
                if model_name == EmbeddingModel.WAV2VEC2:
                    model = Wav2Vec2Model.from_pretrained(model_name.value).to(self.device)
                    processor = Wav2Vec2Processor.from_pretrained(model_name.value)
                    self.models[model_key] = model
                    self.processors[model_key] = processor
            
            # Initialize performance tracking
            self.model_performance[model_key] = ModelPerformance(
                model_name=model_name.value,
                content_type=content_type.value,
                total_generations=0,
                avg_generation_time=0.0,
                success_rate=1.0,
                quality_score=0.0,
                memory_usage_mb=0.0,
                last_updated=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            logger.error(f"Failed to load model {model_name.value}: {str(e)}")
            raise ModelError(f"Model loading failed: {str(e)}")
    
    async def _preprocess_content(
        self, content: Any, content_type: ContentType, config: EmbeddingConfig
    ) -> Any:
        """Preprocess content based on type and configuration"""



        try:
            if content_type == ContentType.TEXT:
                if isinstance(content, str):
                    # Text preprocessing
                    processed_content = content.strip().lower()
                    
                    # Apply custom preprocessing if specified
                    if config.preprocessing_params:
                        max_length = config.preprocessing_params.get("max_length", 512)
                        processed_content = processed_content[:max_length]
                    
                    return processed_content
            
            elif content_type == ContentType.IMAGE:
                if isinstance(content, (np.ndarray, Image.Image)):
                    # Image preprocessing
                    if isinstance(content, np.ndarray):
                        # Convert numpy array to PIL Image
                        if content.shape[-1] == 3:  # RGB
                            image = Image.fromarray(content.astype(np.uint8))
                        else:
                            image = Image.fromarray(content.astype(np.uint8), mode='L')
                    else:
                        image = content
                    
                    # Apply preprocessing parameters
                    if config.preprocessing_params:
                        size = config.preprocessing_params.get("size", (224, 224))
                        image = image.resize(size, Image.Resampling.LANCZOS)
                    
                    return image
            
            elif content_type == ContentType.AUDIO:
                if isinstance(content, np.ndarray):
                    # Audio preprocessing
                    processed_audio = content
                    
                    # Apply preprocessing parameters
                    if config.preprocessing_params:
                        sample_rate = config.preprocessing_params.get("sample_rate", 16000)
                        max_duration = config.preprocessing_params.get("max_duration", 30)
                        
                        # Resample if needed
                        if sample_rate != 16000:  # Default for most models
                            processed_audio = librosa.resample(
                                processed_audio, orig_sr=sample_rate, target_sr=16000
                            )
                        
                        # Trim to max duration
                        max_samples = max_duration * 16000
                        if len(processed_audio) > max_samples:
                            processed_audio = processed_audio[:max_samples]
                    
                    return processed_audio
            
            return content
            
        except Exception as e:
            logger.error(f"Content preprocessing failed: {str(e)}")
            raise EmbeddingError(f"Content preprocessing failed: {str(e)}")
    
    async def _generate_single_model_embedding(
        self, content: Any, content_type: ContentType, config: EmbeddingConfig
    ) -> np.ndarray:
        """Generate embedding using a single model"""



        try:
            model_key = f"{config.model_name.value}_{content_type.value}"
            
            if model_key not in self.models:
                await self._load_model(config.model_name, content_type)
            
            model = self.models[model_key]
            
            if content_type == ContentType.TEXT:
                if config.model_name == EmbeddingModel.SENTENCE_TRANSFORMER:
                    # SentenceTransformer
                    embedding = model.encode(content)
                else:
                    # Transformer models
                    tokenizer = self.tokenizers[model_key]
                    inputs = tokenizer(
                        content, return_tensors="pt", padding=True, truncation=True, max_length=512
                    ).to(self.device)
                    
                    with torch.no_grad():
                        outputs = model(**inputs)
                        # Use mean pooling of last hidden states
                        embedding = outputs.last_hidden_state.mean(dim=1).cpu().numpy()[0]
            
            elif content_type == ContentType.IMAGE:
                processor = self.processors[model_key]
                
                if "clip" in config.model_name.value.lower():
                    # CLIP model
                    inputs = processor(images=content, return_tensors="pt").to(self.device)
                    with torch.no_grad():
                        image_features = model.get_image_features(**inputs)
                        embedding = image_features.cpu().numpy()[0]
                else:
                    # ViT or other vision models
                    inputs = processor(images=content, return_tensors="pt").to(self.device)
                    with torch.no_grad():
                        outputs = model(**inputs)
                        embedding = outputs.last_hidden_state.mean(dim=1).cpu().numpy()[0]
            
            elif content_type == ContentType.AUDIO:
                processor = self.processors[model_key]
                
                # Wav2Vec2 or similar
                inputs = processor(
                    content, sampling_rate=16000, return_tensors="pt", padding=True
                ).to(self.device)
                
                with torch.no_grad():
                    outputs = model(**inputs)
                    # Use mean pooling of last hidden states
                    embedding = outputs.last_hidden_state.mean(dim=1).cpu().numpy()[0]
            
            else:
                raise EmbeddingError(f"Unsupported content type: {content_type}")
            
            return embedding.astype(np.float32)
            
        except Exception as e:
            logger.error(f"Single model embedding generation failed: {str(e)}")
            raise EmbeddingError(f"Single model embedding generation failed: {str(e)}")
    
    async def _generate_ensemble_embedding(
        self, content: Any, content_type: ContentType, config: EmbeddingConfig
    ) -> np.ndarray:
        """Generate embedding using ensemble of models"""



        try:
            # Get available models for content type
            available_models = self._get_available_models(content_type)
            
            if len(available_models) < 2:
                # Fall back to single model
                return await self._generate_single_model_embedding(content, content_type, config)
            
            embeddings = []
            weights = config.ensemble_weights or [1.0] * len(available_models)
            
            # Generate embeddings from each model
            for i, model_name in enumerate(available_models[:len(weights)]):
                model_config = EmbeddingConfig(
                    model_name=model_name,
                    content_type=content_type,
                    dimension=config.dimension,
                    strategy=EmbeddingStrategy.SINGLE_MODEL
                )
                
                embedding = await self._generate_single_model_embedding(
                    content, content_type, model_config
                )
                embeddings.append(embedding * weights[i])
            
            # Combine embeddings (weighted average)
            ensemble_embedding = np.mean(embeddings, axis=0)
            
            return ensemble_embedding.astype(np.float32)
            
        except Exception as e:
            logger.error(f"Ensemble embedding generation failed: {str(e)}")
            raise EmbeddingError(f"Ensemble embedding generation failed: {str(e)}")
    
    async def _generate_hierarchical_embedding(
        self, content: Any, content_type: ContentType, config: EmbeddingConfig
    ) -> np.ndarray:
        """Generate hierarchical embedding with multiple levels"""



        try:
            # Generate embeddings at different levels/scales
            embeddings = []
            
            if content_type == ContentType.IMAGE:
                # Multi-scale image embeddings
                scales = [224, 384, 512]  # Different input sizes
                
                for scale in scales:
                    # Resize content for this scale
                    scaled_content = content.resize((scale, scale), Image.Resampling.LANCZOS)
                    
                    # Generate embedding for this scale
                    scale_embedding = await self._generate_single_model_embedding(
                        scaled_content, content_type, config
                    )
                    embeddings.append(scale_embedding)
            
            elif content_type == ContentType.TEXT:
                # Multi-granularity text embeddings
                # Sentence level, paragraph level, etc.
                sentences = content.split('.')
                
                for sentence in sentences[:3]:  # Use first 3 sentences
                    if sentence.strip():
                        sentence_embedding = await self._generate_single_model_embedding(
                            sentence.strip(), content_type, config
                        )
                        embeddings.append(sentence_embedding)
            
            else:
                # For other types, fall back to single model
                return await self._generate_single_model_embedding(content, content_type, config)
            
            # Combine hierarchical embeddings
            if embeddings:
                hierarchical_embedding = np.concatenate(embeddings)
                
                # Reduce dimension if needed
                if len(hierarchical_embedding) > config.dimension:
                    # Use PCA or truncation to reduce dimension
                    hierarchical_embedding = hierarchical_embedding[:config.dimension]
                
                return hierarchical_embedding.astype(np.float32)
            else:
                return await self._generate_single_model_embedding(content, content_type, config)
            
        except Exception as e:
            logger.error(f"Hierarchical embedding generation failed: {str(e)}")
            raise EmbeddingError(f"Hierarchical embedding generation failed: {str(e)}")
    
    async def _generate_adaptive_embedding(
        self, content: Any, content_type: ContentType, config: EmbeddingConfig
    ) -> np.ndarray:
        """Generate embedding using adaptive model selection"""



        try:
            # Select best model based on content characteristics and performance
            best_model = await self._select_adaptive_model(content, content_type)
            
            adaptive_config = EmbeddingConfig(
                model_name=best_model,
                content_type=content_type,
                dimension=config.dimension,
                strategy=EmbeddingStrategy.SINGLE_MODEL
            )
            
            return await self._generate_single_model_embedding(content, content_type, adaptive_config)
            
        except Exception as e:
            logger.error(f"Adaptive embedding generation failed: {str(e)}")
            raise EmbeddingError(f"Adaptive embedding generation failed: {str(e)}")
    
    async def _postprocess_embedding(self, embedding: np.ndarray, config: EmbeddingConfig) -> np.ndarray:
        """Post-process embedding (normalization, scaling, etc.)"""



        try:
            processed_embedding = embedding.copy()
            
            # Normalize if requested
            if config.normalize:
                norm = np.linalg.norm(processed_embedding)
                if norm > 0:
                    processed_embedding = processed_embedding / norm
            
            # Apply scaling if configured
            if config.postprocessing_params:
                scaling_method = config.postprocessing_params.get("scaling")
                
                if scaling_method == "standard":
                    scaler_key = f"{config.model_name.value}_{config.content_type.value}_standard"
                    if scaler_key in self.scalers:
                        processed_embedding = self.scalers[scaler_key].transform(
                            processed_embedding.reshape(1, -1)
                        )[0]
                
                elif scaling_method == "minmax":
                    scaler_key = f"{config.model_name.value}_{config.content_type.value}_minmax"
                    if scaler_key in self.scalers:
                        processed_embedding = self.scalers[scaler_key].transform(
                            processed_embedding.reshape(1, -1)
                        )[0]
            
            # Ensure correct dimension
            if len(processed_embedding) != config.dimension:
                if len(processed_embedding) > config.dimension:
                    processed_embedding = processed_embedding[:config.dimension]
                else:
                    # Pad with zeros
                    padding = np.zeros(config.dimension - len(processed_embedding))
                    processed_embedding = np.concatenate([processed_embedding, padding])
            
            return processed_embedding.astype(np.float32)
            
        except Exception as e:
            logger.error(f"Embedding post-processing failed: {str(e)}")
            return embedding.astype(np.float32)
    
    async def _calculate_quality_metrics(
        self, embedding: np.ndarray, content_type: ContentType
    ) -> Dict[str, float]:
        """Calculate quality metrics for embedding"""



        try:
            metrics = {}
            
            # Basic statistics
            metrics["mean"] = float(np.mean(embedding))
            metrics["std"] = float(np.std(embedding))
            metrics["norm"] = float(np.linalg.norm(embedding))
            metrics["sparsity"] = float(np.sum(np.abs(embedding) < 1e-6) / len(embedding))
            
            # Distribution metrics
            metrics["entropy"] = self._calculate_entropy(embedding)
            metrics["kurtosis"] = float(self._calculate_kurtosis(embedding))
            metrics["skewness"] = float(self._calculate_skewness(embedding))
            
            # Quality score (combination of metrics)
            quality_score = (
                (1.0 - metrics["sparsity"]) * 0.3 +
                min(metrics["entropy"], 1.0) * 0.3 +
                min(metrics["std"], 1.0) * 0.2 +
                (1.0 - min(abs(metrics["kurtosis"]), 1.0)) * 0.2
            )
            metrics["overall_quality"] = quality_score
            
            return metrics
            
        except Exception as e:
            logger.error(f"Quality metrics calculation failed: {str(e)}")
            return {"overall_quality": 0.5}  # Default quality
    
    async def _calculate_confidence_score(
        self, embedding: np.ndarray, content_type: ContentType, quality_metrics: Dict[str, float]
    ) -> float:
        """Calculate confidence score for embedding"""



        try:
            # Base confidence from quality metrics
            base_confidence = quality_metrics.get("overall_quality", 0.5)
            
            # Adjust based on content type specific factors
            if content_type == ContentType.TEXT:
                # Text-specific confidence adjustments
                if quality_metrics.get("entropy", 0) > 0.7:
                    base_confidence += 0.1
            
            elif content_type == ContentType.IMAGE:
                # Image-specific confidence adjustments
                if quality_metrics.get("std", 0) > 0.1:  # Good variation
                    base_confidence += 0.1
            
            elif content_type == ContentType.AUDIO:
                # Audio-specific confidence adjustments
                if quality_metrics.get("sparsity", 1.0) < 0.1:  # Low sparsity is good
                    base_confidence += 0.1
            
            return min(max(base_confidence, 0.0), 1.0)
            
        except Exception as e:
            logger.error(f"Confidence score calculation failed: {str(e)}")
            return 0.5
    
    def _calculate_entropy(self, embedding: np.ndarray) -> float:
        """Calculate entropy of embedding values"""



        try:
            # Discretize values for entropy calculation
            hist, _ = np.histogram(embedding, bins=50, density=True)
            hist = hist + 1e-8  # Avoid log(0)
            return float(-np.sum(hist * np.log(hist)))
        except:
            return 0.0
    
    def _calculate_kurtosis(self, embedding: np.ndarray) -> float:
        """Calculate kurtosis of embedding values"""



        try:
            mean = np.mean(embedding)
            std = np.std(embedding)
            if std == 0:
                return 0.0
            normalized = (embedding - mean) / std
            return float(np.mean(normalized ** 4) - 3)
        except:
            return 0.0
    
    def _calculate_skewness(self, embedding: np.ndarray) -> float:
        """Calculate skewness of embedding values"""



        try:
            mean = np.mean(embedding)
            std = np.std(embedding)
            if std == 0:
                return 0.0
            normalized = (embedding - mean) / std
            return float(np.mean(normalized ** 3))
        except:
            return 0.0
    
    async def _select_adaptive_model(
        self, content: Any, content_type: ContentType
    ) -> EmbeddingModel:
        """Select best model adaptively based on content and performance"""



        try:
            available_models = self._get_available_models(content_type)
            
            if not available_models:
                # Return default model for content type
                return self.content_configs[content_type].model_name
            
            # Score models based on performance metrics
            model_scores = {}
            
            for model in available_models:
                model_key = f"{model.value}_{content_type.value}"
                
                if model_key in self.model_performance:
                    perf = self.model_performance[model_key]
                    
                    # Calculate composite score
                    score = (
                        perf.success_rate * 0.3 +
                        perf.quality_score * 0.3 +
                        (1.0 / max(perf.avg_generation_time, 0.001)) * 0.2 +  # Faster is better
                        (1.0 / max(perf.memory_usage_mb, 1.0)) * 0.2  # Less memory is better
                    )
                    
                    model_scores[model] = score
                else:
                    # Default score for unknown models
                    model_scores[model] = 0.5
            
            # Return model with highest score
            best_model = max(model_scores.keys(), key=lambda k: model_scores[k])
            return best_model
            
        except Exception as e:
            logger.error(f"Adaptive model selection failed: {str(e)}")
            return self.content_configs[content_type].model_name
    
    def _get_available_models(self, content_type: ContentType) -> List[EmbeddingModel]:
        """Get available models for content type"""
        if content_type == ContentType.TEXT:
            return [
                EmbeddingModel.SENTENCE_TRANSFORMER,
                EmbeddingModel.BERT_BASE,
                EmbeddingModel.ROBERTA,
                EmbeddingModel.DISTILBERT
            ]
        elif content_type == ContentType.IMAGE:
            return [
                EmbeddingModel.CLIP_VIT_B32,
                EmbeddingModel.VIT_BASE,
                EmbeddingModel.RESNET50
            ]
        elif content_type == ContentType.AUDIO:
            return [
                EmbeddingModel.WAV2VEC2,
                EmbeddingModel.HUBERT
            ]
        else:
            return []
    
    def _initialize_content_configs(self) -> Dict[ContentType, EmbeddingConfig]:
        """Initialize default configurations for each content type"""



        return {
            ContentType.TEXT: EmbeddingConfig(
                model_name=EmbeddingModel.SENTENCE_TRANSFORMER,
                content_type=ContentType.TEXT,
                dimension=384,
                normalize=True,
                preprocessing_params={"max_length": 512}
            ),
            ContentType.IMAGE: EmbeddingConfig(
                model_name=EmbeddingModel.CLIP_VIT_B32,
                content_type=ContentType.IMAGE,
                dimension=512,
                normalize=True,
                preprocessing_params={"size": (224, 224)}
            ),
            ContentType.AUDIO: EmbeddingConfig(
                model_name=EmbeddingModel.WAV2VEC2,
                content_type=ContentType.AUDIO,
                dimension=768,
                normalize=True,
                preprocessing_params={"sample_rate": 16000, "max_duration": 30}
            ),
            ContentType.VIDEO: EmbeddingConfig(
                model_name=EmbeddingModel.CLIP_VIT_B32,
                content_type=ContentType.VIDEO,
                dimension=512,
                normalize=True,
                strategy=EmbeddingStrategy.HIERARCHICAL
            )
        }
    
    async def _initialize_scalers(self) -> None:
        """Initialize scalers for embedding normalization"""



        try:
            # Initialize standard and minmax scalers for each model/content type combination
            for content_type in ContentType:
                for model in self._get_available_models(content_type):
                    base_key = f"{model.value}_{content_type.value}"
                    
                    self.scalers[f"{base_key}_standard"] = StandardScaler()
                    self.scalers[f"{base_key}_minmax"] = MinMaxScaler()
            
        except Exception as e:
            logger.error(f"Failed to initialize scalers: {str(e)}")
    
    async def _process_content_batch(
        self,
        batch: List[Tuple[int, Any, str]],
        content_type: ContentType,
        config: EmbeddingConfig
    ) -> List[EmbeddingResult]:
        """Process a batch of content for embedding generation"""



        try:
            results = []
            
            # Process each item in batch
            for original_idx, content, content_id in batch:
                try:
                    result = await self.generate_embedding(
                        content, content_type, content_id, config
                    )
                    # Store original index for sorting
                    result.content_id = f"{original_idx}_{content_id}"
                    results.append(result)
                    
                except Exception as e:
                    logger.error(f"Failed to process content {content_id}: {str(e)}")
                    # Create error result
                    error_result = EmbeddingResult(
                        content_id=f"{original_idx}_{content_id}",
                        embedding=np.zeros(config.dimension, dtype=np.float32),
                        model_used=config.model_name.value,
                        generation_time=0.0,
                        confidence_score=0.0,
                        metadata={"error": str(e)}
                    )
                    results.append(error_result)
            
            return results
            
        except Exception as e:
            logger.error(f"Batch processing failed: {str(e)}")
            return []
    
    def _generate_cache_key(
        self, content: Any, content_type: ContentType, config: EmbeddingConfig
    ) -> str:
        """Generate cache key for content and configuration"""
        import hashlib
        
        try:
            # Create a hash of content and config
            content_hash = ""
            
            if isinstance(content, str):
                content_hash = hashlib.md5(content.encode()).hexdigest()
            elif isinstance(content, np.ndarray):
                content_hash = hashlib.md5(content.tobytes()).hexdigest()
            elif isinstance(content, Image.Image):
                import io
                buf = io.BytesIO()
                content.save(buf, format='PNG')
                content_hash = hashlib.md5(buf.getvalue()).hexdigest()
            
            config_str = f"{config.model_name.value}_{config.strategy.value}_{config.dimension}"
            config_hash = hashlib.md5(config_str.encode()).hexdigest()
            
            return f"emb_{content_type.value}_{content_hash[:16]}_{config_hash[:16]}"
            
        except Exception as e:
            logger.error(f"Cache key generation failed: {str(e)}")
            return f"emb_{content_type.value}_{datetime.now().timestamp()}"
    
    def _update_generation_stats(self, generation_time: float, success: bool) -> None:
        """Update generation statistics"""
        self.generation_stats["total_embeddings"] += 1
        
        if success:
            # Update average generation time
            total = self.generation_stats["total_embeddings"]
            current_avg = self.generation_stats["avg_generation_time"]
            new_avg = ((current_avg * (total - 1)) + generation_time) / total
            self.generation_stats["avg_generation_time"] = new_avg
    
    def _update_model_performance(
        self, model_name: str, content_type: ContentType, generation_time: float
    ) -> None:
        """Update model performance metrics"""
        model_key = f"{model_name}_{content_type.value}"
        
        if model_key not in self.model_performance:
            self.model_performance[model_key] = ModelPerformance(
                model_name=model_name,
                content_type=content_type.value,
                total_generations=0,
                avg_generation_time=0.0,
                success_rate=1.0,
                quality_score=0.0,
                memory_usage_mb=0.0,
                last_updated=datetime.now(timezone.utc)
            )
        
        perf = self.model_performance[model_key]
        perf.total_generations += 1
        
        # Update average generation time
        total = perf.total_generations
        current_avg = perf.avg_generation_time
        perf.avg_generation_time = ((current_avg * (total - 1)) + generation_time) / total
        
        perf.last_updated = datetime.now(timezone.utc)
    
    async def _create_fine_tuning_adapter(
        self, base_model: nn.Module, content_type: ContentType, target_dim: int
    ) -> nn.Module:
        """Create a fine-tuning adapter for base model"""



        try:
            # Simple adapter architecture
            class EmbeddingAdapter(nn.Module):
                def __init__(self, base_model, hidden_dim, output_dim):
                    super().__init__()
                    self.base_model = base_model
                    self.adapter = nn.Sequential(
                        nn.Linear(hidden_dim, hidden_dim // 2),
                        nn.ReLU(),
                        nn.Dropout(0.1),
                        nn.Linear(hidden_dim // 2, output_dim)
                    )
                    
                    # Freeze base model
                    for param in self.base_model.parameters():
                        param.requires_grad = False
                
                def forward(self, x):
                    with torch.no_grad():
                        base_features = self.base_model(x)
                    
                    # Extract appropriate features based on model type
                    if hasattr(base_features, 'last_hidden_state'):
                        features = base_features.last_hidden_state.mean(dim=1)
                    elif hasattr(base_features, 'pooler_output'):
                        features = base_features.pooler_output
                    else:
                        features = base_features
                    
                    return self.adapter(features)
            
            # Determine input dimension
            if hasattr(base_model, 'config'):
                hidden_dim = base_model.config.hidden_size
            else:
                hidden_dim = 768  # Default
            
            adapter = EmbeddingAdapter(base_model, hidden_dim, target_dim)
            return adapter.to(self.device)
            
        except Exception as e:
            logger.error(f"Failed to create fine-tuning adapter: {str(e)}")
            raise ModelError(f"Adapter creation failed: {str(e)}")
    
    def _create_data_loader(self, data: List[Tuple[Any, np.ndarray]], batch_size: int):
        """Create data loader for fine-tuning"""



        try:
            from torch.utils.data import DataLoader, TensorDataset
            
            inputs = []
            targets = []
            
            for content, target in data:
                # Convert content to tensor (simplified)
                if isinstance(content, str):
                    # Tokenize text content
                    input_tensor = torch.tensor([hash(content) % 1000])  # Simplified
                elif isinstance(content, np.ndarray):
                    input_tensor = torch.from_numpy(content).float()
                else:
                    input_tensor = torch.tensor([0])  # Placeholder
                
                target_tensor = torch.from_numpy(target).float()
                
                inputs.append(input_tensor)
                targets.append(target_tensor)
            
            # Pad inputs to same size if needed
            if inputs and len(inputs[0].shape) > 0:
                max_len = max(len(inp) for inp in inputs)
                padded_inputs = []
                for inp in inputs:
                    if len(inp) < max_len:
                        padding = torch.zeros(max_len - len(inp))
                        inp = torch.cat([inp, padding])
                    padded_inputs.append(inp)
                inputs = padded_inputs
            
            input_tensor = torch.stack(inputs)
            target_tensor = torch.stack(targets)
            
            dataset = TensorDataset(input_tensor, target_tensor)
            return DataLoader(dataset, batch_size=batch_size, shuffle=True)
            
        except Exception as e:
            logger.error(f"Failed to create data loader: {str(e)}")
            raise ModelError(f"Data loader creation failed: {str(e)}")
    
    async def close(self) -> None:
        """Close embedding generator and cleanup resources"""



        try:
            # Clear models from GPU memory
            for model_key, model in self.models.items():
                if hasattr(model, 'cpu'):
                    model.cpu()
                del model
            
            # Clear caches
            self.models.clear()
            self.tokenizers.clear()
            self.processors.clear()
            self.scalers.clear()
            
            # Clear CUDA cache if available
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            logger.info("Embedding generator closed successfully")
            
        except Exception as e:
            logger.error(f"Error closing embedding generator: {str(e)}")
