"""
Feature Extractor - Advanced ML Feature Engineering & Extraction System

Industrial-grade feature extraction providing comprehensive feature engineering,
multi-modal feature extraction, automated feature selection, and feature pipeline
optimization for the IA-Influencer-Agent ML platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

  CRITICAL LEGAL NOTICE:
This feature extraction system and methodologies are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission
is strictly PROHIBITED and will result in legal action.

ALL RIGHTS RESERVED - FAHED MLAIEL ©2025
"""

import asyncio
import logging
import time
import uuid
import json
import pickle
import joblib
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Tuple, Callable, Set
from pathlib import Path
import numpy as np
import pandas as pd
import traceback
from collections import defaultdict
import re

# Core ML and data processing
import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer, HashingVectorizer
from sklearn.feature_selection import (
    SelectKBest, SelectFromModel, RFE, RFECV,
    mutual_info_classif, mutual_info_regression,
    f_classif, f_regression, chi2
)
from sklearn.preprocessing import (
    StandardScaler, MinMaxScaler, RobustScaler, PowerTransformer,
    LabelEncoder, OneHotEncoder, OrdinalEncoder,
    PolynomialFeatures, SplineTransformer
)
from sklearn.decomposition import PCA, TruncatedSVD, FastICA, FactorAnalysis
from sklearn.manifold import TSNE, UMAP
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
import scipy.sparse as sp
from scipy import stats

# Deep learning for feature extraction
import tensorflow as tf
import torch
import torch.nn as nn
from transformers import AutoModel, AutoTokenizer, AutoFeatureExtractor

# Image processing
try:
    import cv2
    import PIL
    from PIL import Image
    from skimage import feature, filters, segmentation
    import imagehash
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

# Audio processing
try:
    import librosa
    import soundfile as sf
    from scipy.signal import spectrogram
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False

# Video processing
try:
    from moviepy.editor import VideoFileClip
    import face_recognition
    VIDEO_AVAILABLE = True
except ImportError:
    VIDEO_AVAILABLE = False

# Natural Language Processing
import spacy
import nltk
from textstat import flesch_reading_ease, flesch_kincaid_grade

# Platform imports
try:
    from core.config import settings
except ImportError:
    # Fallback settings
    settings = type('Settings', (), {'debug': True, 'log_level': 'INFO'})()
try:
    from core.database import get_db_session
except ImportError:
    # Fallback database classes
    class DatabaseManager: pass
    get_db_session = DatabaseManager
try:
    from core.exceptions import FeatureExtractionError, ValidationError
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    FeatureExtractionError, ValidationError = globals().get('FeatureExtractionError, ValidationError', Exception)
from ...security.encryption import ContentEncryption
from ...utils.performance_monitor import PerformanceMonitor
from ...utils.cache import CacheManager

# Prometheus monitoring
from prometheus_client import Counter, Histogram, Gauge

logger = logging.getLogger(__name__)

class FeatureType(Enum):
    """Feature extraction types"""
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    NUMERICAL = "numerical"
    CATEGORICAL = "categorical"
    TIME_SERIES = "time_series"
    MULTIMODAL = "multimodal"

class ExtractionMethod(Enum):
    """Feature extraction methods"""
    STATISTICAL = "statistical"
    TRANSFORMER = "transformer"
    EMBEDDING = "embedding"
    HANDCRAFTED = "handcrafted"
    DEEP_LEARNING = "deep_learning"
    FREQUENCY_DOMAIN = "frequency_domain"
    SPATIAL = "spatial"

class FeaturePriority(Enum):
    """Feature priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class FeatureConfig:
    """Comprehensive feature extraction configuration"""
    extraction_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    feature_types: List[FeatureType] = field(default_factory=list)
    extraction_methods: List[ExtractionMethod] = field(default_factory=list)
    priority: FeaturePriority = FeaturePriority.MEDIUM
    
    # Content settings
    content_types: List[str] = field(default_factory=list)  # text, image, audio, video
    max_features: Optional[int] = None
    feature_selection: bool = True
    dimensionality_reduction: bool = False
    
    # Text feature settings
    text_vectorizer: str = "tfidf"  # tfidf, count, hash, transformer
    max_text_features: int = 10000
    ngram_range: Tuple[int, int] = (1, 3)
    min_df: int = 2
    max_df: float = 0.95
    use_stopwords: bool = True
    language: str = "en"
    
    # Image feature settings
    image_size: Tuple[int, int] = (224, 224)
    color_space: str = "RGB"  # RGB, HSV, LAB
    extract_color_histogram: bool = True
    extract_texture_features: bool = True
    extract_shape_features: bool = True
    use_pretrained_cnn: bool = True
    cnn_model: str = "resnet50"
    
    # Audio feature settings
    sample_rate: int = 22050
    n_mels: int = 128
    n_fft: int = 2048
    hop_length: int = 512
    extract_mfcc: bool = True
    extract_spectral: bool = True
    extract_temporal: bool = True
    extract_rhythm: bool = True
    
    # Video feature settings
    fps_extraction: int = 1
    extract_motion: bool = True
    extract_scene_changes: bool = True
    extract_face_features: bool = False
    extract_object_features: bool = False
    
    # Numerical feature settings
    scaling_method: str = "standard"  # standard, minmax, robust, power
    polynomial_features: bool = False
    polynomial_degree: int = 2
    interaction_features: bool = False
    
    # Feature selection settings
    selection_method: str = "mutual_info"  # mutual_info, f_test, chi2, rfe, model_based
    k_best_features: int = 1000
    selection_threshold: float = 0.01
    
    # Dimensionality reduction settings
    reduction_method: str = "pca"  # pca, svd, ica, umap, tsne
    n_components: Optional[int] = None
    variance_threshold: float = 0.95
    
    # Performance settings
    batch_size: int = 32
    parallel_workers: int = 4
    use_gpu: bool = True
    cache_features: bool = True
    
    # Advanced settings
    ensemble_features: bool = False
    cross_validation: bool = False
    feature_importance: bool = True
    quality_metrics: bool = True
    
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class FeatureMetrics:
    """Comprehensive feature extraction metrics"""
    # Feature statistics
    total_features: int = 0
    selected_features: int = 0
    feature_types_count: Dict[str, int] = field(default_factory=dict)
    extraction_methods_count: Dict[str, int] = field(default_factory=dict)
    
    # Quality metrics
    feature_correlation_matrix: Optional[np.ndarray] = None
    feature_importance_scores: Dict[str, float] = field(default_factory=dict)
    mutual_information_scores: Dict[str, float] = field(default_factory=dict)
    variance_scores: Dict[str, float] = field(default_factory=dict)
    
    # Performance metrics
    extraction_time_seconds: float = 0.0
    memory_usage_mb: float = 0.0
    processing_rate_items_per_second: float = 0.0
    
    # Validation metrics
    feature_completeness: float = 0.0  # % of non-null features
    feature_uniqueness: float = 0.0   # % of unique values
    feature_stability: float = 0.0     # consistency across batches
    
    # Resource utilization
    cpu_usage_percent: float = 0.0
    memory_peak_mb: float = 0.0
    gpu_usage_percent: float = 0.0
    
    last_updated: datetime = field(default_factory=datetime.utcnow)

@dataclass
class FeatureExtractionResult:
    """Complete feature extraction result"""
    extraction_id: str
    content_id: str
    feature_types: List[str]
    
    # Feature data
    features: Optional[np.ndarray] = None
    feature_names: List[str] = field(default_factory=list)
    feature_metadata: Dict[str, Any] = field(default_factory=dict)
    sparse_features: Optional[sp.csr_matrix] = None
    
    # Multi-modal features
    text_features: Optional[np.ndarray] = None
    image_features: Optional[np.ndarray] = None
    audio_features: Optional[np.ndarray] = None
    video_features: Optional[np.ndarray] = None
    
    # Feature analysis
    feature_importance: Dict[str, float] = field(default_factory=dict)
    feature_correlations: Dict[str, float] = field(default_factory=dict)
    feature_statistics: Dict[str, Dict[str, float]] = field(default_factory=dict)
    
    # Quality metrics
    metrics: Optional[FeatureMetrics] = None
    validation_results: Dict[str, Any] = field(default_factory=dict)
    
    # Processing details
    config: Optional[FeatureConfig] = None
    processing_log: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    
    # Execution details
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    total_duration_seconds: float = 0.0
    
    created_at: datetime = field(default_factory=datetime.utcnow)

class FeatureExtractor:
    """
    Ultra-Advanced Feature Extraction Engine
    
    Comprehensive feature extraction system providing:
    - Multi-modal feature extraction (text, image, audio, video)
    - Advanced feature engineering and transformation
    - Automated feature selection and dimensionality reduction
    - Deep learning-based feature extraction
    - Statistical and handcrafted feature extraction
    - Feature quality assessment and validation
    - Performance optimization and caching
    - Real-time and batch processing capabilities
    """
    
    # Prometheus metrics
    EXTRACTION_JOBS = Counter('feature_extractor_jobs_total', 'Total extraction jobs', ['content_type', 'status'])
    EXTRACTION_DURATION = Histogram('feature_extractor_duration_seconds', 'Extraction duration', ['content_type'])
    ACTIVE_EXTRACTIONS = Gauge('feature_extractor_active_jobs', 'Active extraction jobs')
    FEATURES_EXTRACTED = Counter('feature_extractor_features_total', 'Total features extracted', ['feature_type'])
    EXTRACTION_QUALITY = Gauge('feature_extractor_quality_score', 'Feature extraction quality', ['content_id'])
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.extractor_id = f"extractor_{uuid.uuid4().hex[:8]}"
        
        # Feature extraction job management
        self.active_extractions: Dict[str, FeatureConfig] = {}
        self.completed_extractions: Dict[str, FeatureExtractionResult] = {}
        self.extraction_queue = asyncio.Queue()
        
        # Performance monitoring
        self.performance_monitor = PerformanceMonitor(f"extractor_{self.extractor_id}")
        
        # Cache management
        self.cache_manager = CacheManager("feature_cache")
        
        # Feature extractors registry
        self.feature_extractors = self._initialize_feature_extractors()
        
        # Pre-trained models cache
        self.pretrained_models = {}
        
        # NLP models
        self.nlp_models = {}
        
        # Background tasks
        self.background_tasks = set()
        
        logger.info(f"FeatureExtractor initialized: {self.extractor_id}")
    
    async def initialize(self) -> bool:
        """Initialize feature extractor"""



        try:
            # Load NLP models
            if self.config.get("enable_nlp", True):
                await self._load_nlp_models()
            
            # Load pre-trained models
            if self.config.get("enable_pretrained", True):
                await self._load_pretrained_models()
            
            # Start background extraction processor
            task = asyncio.create_task(self._process_extraction_queue())
            self.background_tasks.add(task)
            task.add_done_callback(self.background_tasks.discard)
            
            logger.info("FeatureExtractor successfully initialized")
            return True
            
        except Exception as e:
            logger.error(f"FeatureExtractor initialization failed: {str(e)}")
            return False

    async def extract_features(self,
                             content: Any,
                             content_type: str,
                             content_id: str,
                             config: FeatureConfig,
                             async_execution: bool = False) -> Union[FeatureExtractionResult, str]:
        """
        Comprehensive multi-modal feature extraction
        
        Args:
            content: Content data to extract features from
            content_type: Type of content (text, image, audio, video)
            content_id: Unique identifier for content
            config: Feature extraction configuration
            async_execution: Whether to execute extraction asynchronously
            
        Returns:
            FeatureExtractionResult: Complete extraction results or job_id if async
        """
        extraction_id = config.extraction_id
        
        try:
            logger.info(f"Starting feature extraction: {extraction_id} ({content_type})")
            
            # Validate configuration and content
            validation_result = await self._validate_extraction_config(config, content_type)
            if not validation_result["valid"]:
                raise ValueError(f"Configuration validation failed: {validation_result['errors']}")
            
            # Register extraction job
            self.active_extractions[extraction_id] = config
            
            # Update metrics
            self.EXTRACTION_JOBS.labels(content_type=content_type, status="started").inc()
            self.ACTIVE_EXTRACTIONS.inc()
            
            if async_execution:
                # Queue for background processing
                await self.extraction_queue.put({
                    "extraction_id": extraction_id,
                    "content": content,
                    "content_type": content_type,
                    "content_id": content_id,
                    "config": config
                })
                return extraction_id
            else:
                # Execute synchronously
                result = await self._execute_feature_extraction(
                    content, content_type, content_id, config
                )
                
                # Clean up
                if extraction_id in self.active_extractions:
                    del self.active_extractions[extraction_id]
                self.completed_extractions[extraction_id] = result
                self.ACTIVE_EXTRACTIONS.dec()
                
                return result
                
        except Exception as e:
            # Handle extraction failure
            if extraction_id in self.active_extractions:
                del self.active_extractions[extraction_id]
            
            self.EXTRACTION_JOBS.labels(content_type=content_type, status="failed").inc()
            self.ACTIVE_EXTRACTIONS.dec()
            
            error_result = FeatureExtractionResult(
                extraction_id=extraction_id,
                content_id=content_id,
                feature_types=[content_type]
            )
            error_result.errors.append(str(e))
            error_result.start_time = config.created_at
            error_result.end_time = datetime.utcnow()
            
            self.completed_extractions[extraction_id] = error_result
            logger.error(f"Feature extraction {extraction_id} failed: {str(e)}")
            
            if not async_execution:
                raise FeatureExtractionError(f"Feature extraction failed: {str(e)}")
            
            return error_result

    async def extract_text_features(self,
                                  text: str,
                                  config: FeatureConfig = None) -> Dict[str, np.ndarray]:
        """
        Comprehensive text feature extraction
        """



        try:
            logger.info("Starting text feature extraction")
            
            config = config or FeatureConfig()
            text_features = {}
            
            # Preprocessing
            processed_text = await self._preprocess_text(text, config)
            
            # Statistical features
            if ExtractionMethod.STATISTICAL in config.extraction_methods:
                statistical_features = await self._extract_statistical_text_features(processed_text)
                text_features["statistical"] = statistical_features
            
            # Vectorization features
            if config.text_vectorizer == "tfidf":
                tfidf_features = await self._extract_tfidf_features(processed_text, config)
                text_features["tfidf"] = tfidf_features
            elif config.text_vectorizer == "count":
                count_features = await self._extract_count_features(processed_text, config)
                text_features["count"] = count_features
            elif config.text_vectorizer == "hash":
                hash_features = await self._extract_hash_features(processed_text, config)
                text_features["hash"] = hash_features
            
            # Transformer-based features
            if ExtractionMethod.TRANSFORMER in config.extraction_methods:
                transformer_features = await self._extract_transformer_features(processed_text, config)
                text_features["transformer"] = transformer_features
            
            # Linguistic features
            linguistic_features = await self._extract_linguistic_features(text, processed_text)
            text_features["linguistic"] = linguistic_features
            
            # Sentiment and emotion features
            sentiment_features = await self._extract_sentiment_features(text)
            text_features["sentiment"] = sentiment_features
            
            # Named entity features
            entity_features = await self._extract_entity_features(processed_text)
            text_features["entities"] = entity_features
            
            # Topic features
            topic_features = await self._extract_topic_features(processed_text, config)
            text_features["topics"] = topic_features
            
            logger.info("Text feature extraction completed")
            return text_features
            
        except Exception as e:
            logger.error(f"Text feature extraction failed: {str(e)}")
            raise FeatureExtractionError(f"Text feature extraction failed: {str(e)}")

    async def extract_image_features(self,
                                   image: np.ndarray,
                                   config: FeatureConfig = None) -> Dict[str, np.ndarray]:
        """
        Comprehensive image feature extraction
        """



        try:
            logger.info("Starting image feature extraction")
            
            if not CV2_AVAILABLE:
                raise FeatureExtractionError("Image processing libraries not available")
            
            config = config or FeatureConfig()
            image_features = {}
            
            # Preprocessing
            processed_image = await self._preprocess_image(image, config)
            
            # Statistical features
            if ExtractionMethod.STATISTICAL in config.extraction_methods:
                statistical_features = await self._extract_statistical_image_features(processed_image)
                image_features["statistical"] = statistical_features
            
            # Color features
            if config.extract_color_histogram:
                color_features = await self._extract_color_features(processed_image, config)
                image_features["color"] = color_features
            
            # Texture features
            if config.extract_texture_features:
                texture_features = await self._extract_texture_features(processed_image)
                image_features["texture"] = texture_features
            
            # Shape features
            if config.extract_shape_features:
                shape_features = await self._extract_shape_features(processed_image)
                image_features["shape"] = shape_features
            
            # Deep learning features
            if config.use_pretrained_cnn and ExtractionMethod.DEEP_LEARNING in config.extraction_methods:
                cnn_features = await self._extract_cnn_features(processed_image, config)
                image_features["cnn"] = cnn_features
            
            # Edge and corner features
            edge_features = await self._extract_edge_features(processed_image)
            image_features["edges"] = edge_features
            
            # Hash features for duplicate detection
            hash_features = await self._extract_image_hash_features(processed_image)
            image_features["hash"] = hash_features
            
            logger.info("Image feature extraction completed")
            return image_features
            
        except Exception as e:
            logger.error(f"Image feature extraction failed: {str(e)}")
            raise FeatureExtractionError(f"Image feature extraction failed: {str(e)}")

    async def extract_audio_features(self,
                                   audio: np.ndarray,
                                   sample_rate: int,
                                   config: FeatureConfig = None) -> Dict[str, np.ndarray]:
        """
        Comprehensive audio feature extraction
        """



        try:
            logger.info("Starting audio feature extraction")
            
            if not AUDIO_AVAILABLE:
                raise FeatureExtractionError("Audio processing libraries not available")
            
            config = config or FeatureConfig()
            audio_features = {}
            
            # Preprocessing
            processed_audio = await self._preprocess_audio(audio, sample_rate, config)
            
            # Statistical features
            if ExtractionMethod.STATISTICAL in config.extraction_methods:
                statistical_features = await self._extract_statistical_audio_features(processed_audio)
                audio_features["statistical"] = statistical_features
            
            # MFCC features
            if config.extract_mfcc:
                mfcc_features = await self._extract_mfcc_features(processed_audio, sample_rate, config)
                audio_features["mfcc"] = mfcc_features
            
            # Spectral features
            if config.extract_spectral:
                spectral_features = await self._extract_spectral_features(processed_audio, sample_rate, config)
                audio_features["spectral"] = spectral_features
            
            # Temporal features
            if config.extract_temporal:
                temporal_features = await self._extract_temporal_features(processed_audio, sample_rate)
                audio_features["temporal"] = temporal_features
            
            # Rhythm features
            if config.extract_rhythm:
                rhythm_features = await self._extract_rhythm_features(processed_audio, sample_rate)
                audio_features["rhythm"] = rhythm_features
            
            # Frequency domain features
            if ExtractionMethod.FREQUENCY_DOMAIN in config.extraction_methods:
                frequency_features = await self._extract_frequency_features(processed_audio, sample_rate, config)
                audio_features["frequency"] = frequency_features
            
            # Chroma features
            chroma_features = await self._extract_chroma_features(processed_audio, sample_rate)
            audio_features["chroma"] = chroma_features
            
            logger.info("Audio feature extraction completed")
            return audio_features
            
        except Exception as e:
            logger.error(f"Audio feature extraction failed: {str(e)}")
            raise FeatureExtractionError(f"Audio feature extraction failed: {str(e)}")

    async def extract_video_features(self,
                                   video_path: str,
                                   config: FeatureConfig = None) -> Dict[str, np.ndarray]:
        """
        Comprehensive video feature extraction
        """



        try:
            logger.info("Starting video feature extraction")
            
            if not VIDEO_AVAILABLE:
                raise FeatureExtractionError("Video processing libraries not available")
            
            config = config or FeatureConfig()
            video_features = {}
            
            # Load video
            video_clip = VideoFileClip(video_path)
            
            # Extract frames
            frames = await self._extract_video_frames(video_clip, config)
            
            # Frame-based features
            frame_features = []
            for frame in frames:
                frame_feat = await self.extract_image_features(frame, config)
                frame_features.append(np.concatenate([feat.flatten() for feat in frame_feat.values()]))
            
            if frame_features:
                video_features["frames"] = np.array(frame_features)
                
                # Aggregate frame features
                video_features["frame_mean"] = np.mean(video_features["frames"], axis=0)
                video_features["frame_std"] = np.std(video_features["frames"], axis=0)
                video_features["frame_max"] = np.max(video_features["frames"], axis=0)
                video_features["frame_min"] = np.min(video_features["frames"], axis=0)
            
            # Motion features
            if config.extract_motion:
                motion_features = await self._extract_motion_features(frames)
                video_features["motion"] = motion_features
            
            # Scene change detection
            if config.extract_scene_changes:
                scene_features = await self._extract_scene_change_features(frames)
                video_features["scene_changes"] = scene_features
            
            # Face features
            if config.extract_face_features:
                face_features = await self._extract_face_features(frames)
                video_features["faces"] = face_features
            
            # Audio features from video
            if video_clip.audio:
                audio_array = video_clip.audio.to_soundarray()
                if len(audio_array.shape) > 1:
                    audio_array = audio_array.mean(axis=1)  # Convert to mono
                
                audio_features = await self.extract_audio_features(
                    audio_array, 
                    video_clip.audio.fps,
                    config
                )
                video_features.update({f"audio_{k}": v for k, v in audio_features.items()})
            
            video_clip.close()
            
            logger.info("Video feature extraction completed")
            return video_features
            
        except Exception as e:
            logger.error(f"Video feature extraction failed: {str(e)}")
            raise FeatureExtractionError(f"Video feature extraction failed: {str(e)}")

    async def select_features(self,
                            features: np.ndarray,
                            target: np.ndarray,
                            feature_names: List[str],
                            config: FeatureConfig) -> Tuple[np.ndarray, List[str], Dict[str, float]]:
        """
        Advanced feature selection using multiple methods
        """



        try:
            logger.info("Starting feature selection")
            
            selected_features = features.copy()
            selected_names = feature_names.copy()
            feature_scores = {}
            
            # Remove constant features
            constant_filter = features.std(axis=0) > 0
            selected_features = selected_features[:, constant_filter]
            selected_names = [name for i, name in enumerate(selected_names) if constant_filter[i]]
            
            # Correlation-based filtering
            if selected_features.shape[1] > 1:
                corr_matrix = np.corrcoef(selected_features.T)
                high_corr_mask = np.ones(selected_features.shape[1], dtype=bool)
                
                for i in range(corr_matrix.shape[0]):
                    for j in range(i+1, corr_matrix.shape[1]):
                        if abs(corr_matrix[i, j]) > 0.95:
                            high_corr_mask[j] = False
                
                selected_features = selected_features[:, high_corr_mask]
                selected_names = [name for i, name in enumerate(selected_names) if high_corr_mask[i]]
            
            # Statistical feature selection
            if config.selection_method == "mutual_info":
                if len(np.unique(target)) < 20:  # Classification
                    selector = SelectKBest(mutual_info_classif, k=min(config.k_best_features, selected_features.shape[1]))
                else:  # Regression
                    selector = SelectKBest(mutual_info_regression, k=min(config.k_best_features, selected_features.shape[1]))
                    
                selected_features = selector.fit_transform(selected_features, target)
                scores = selector.scores_
                selected_indices = selector.get_support(indices=True)
                selected_names = [selected_names[i] for i in selected_indices]
                feature_scores.update({name: scores[i] for i, name in enumerate(selected_names)})
                
            elif config.selection_method == "f_test":
                if len(np.unique(target)) < 20:  # Classification
                    selector = SelectKBest(f_classif, k=min(config.k_best_features, selected_features.shape[1]))
                else:  # Regression
                    selector = SelectKBest(f_regression, k=min(config.k_best_features, selected_features.shape[1]))
                    
                selected_features = selector.fit_transform(selected_features, target)
                scores = selector.scores_
                selected_indices = selector.get_support(indices=True)
                selected_names = [selected_names[i] for i in selected_indices]
                feature_scores.update({name: scores[i] for i, name in enumerate(selected_names)})
            
            elif config.selection_method == "rfe":
                # Recursive Feature Elimination
                if len(np.unique(target)) < 20:  # Classification
                    estimator = RandomForestClassifier(n_estimators=50, random_state=42)
                else:  # Regression
                    estimator = RandomForestRegressor(n_estimators=50, random_state=42)
                
                selector = RFE(estimator, n_features_to_select=min(config.k_best_features, selected_features.shape[1]))
                selected_features = selector.fit_transform(selected_features, target)
                selected_indices = selector.get_support(indices=True)
                selected_names = [selected_names[i] for i in selected_indices]
                
                # Get feature importance from estimator
                estimator.fit(selected_features, target)
                importances = estimator.feature_importances_
                feature_scores.update({name: importances[i] for i, name in enumerate(selected_names)})
            
            logger.info(f"Feature selection completed: {len(selected_names)} features selected")
            return selected_features, selected_names, feature_scores
            
        except Exception as e:
            logger.error(f"Feature selection failed: {str(e)}")
            raise FeatureExtractionError(f"Feature selection failed: {str(e)}")

    async def reduce_dimensionality(self,
                                  features: np.ndarray,
                                  config: FeatureConfig) -> Tuple[np.ndarray, Any]:
        """
        Advanced dimensionality reduction
        """



        try:
            logger.info("Starting dimensionality reduction")
            
            n_components = config.n_components or min(features.shape[1] // 2, 100)
            
            if config.reduction_method == "pca":
                reducer = PCA(n_components=n_components)
                reduced_features = reducer.fit_transform(features)
                
            elif config.reduction_method == "svd":
                reducer = TruncatedSVD(n_components=n_components)
                reduced_features = reducer.fit_transform(features)
                
            elif config.reduction_method == "ica":
                reducer = FastICA(n_components=n_components, random_state=42)
                reduced_features = reducer.fit_transform(features)
                
            elif config.reduction_method == "umap":
                try:
                    reducer = UMAP(n_components=n_components, random_state=42)
                    reduced_features = reducer.fit_transform(features)
                except Exception:
                    # Fallback to PCA if UMAP fails
                    reducer = PCA(n_components=n_components)
                    reduced_features = reducer.fit_transform(features)
                    
            elif config.reduction_method == "tsne":
                reducer = TSNE(n_components=min(n_components, 3), random_state=42)
                reduced_features = reducer.fit_transform(features)
                
            else:
                # Default to PCA
                reducer = PCA(n_components=n_components)
                reduced_features = reducer.fit_transform(features)
            
            logger.info(f"Dimensionality reduction completed: {features.shape[1]} -> {reduced_features.shape[1]}")
            return reduced_features, reducer
            
        except Exception as e:
            logger.error(f"Dimensionality reduction failed: {str(e)}")
            raise FeatureExtractionError(f"Dimensionality reduction failed: {str(e)}")

    # Private helper methods
    async def _execute_feature_extraction(self,
                                        content: Any,
                                        content_type: str,
                                        content_id: str,
                                        config: FeatureConfig) -> FeatureExtractionResult:
        """Execute complete feature extraction pipeline"""
        start_time = datetime.utcnow()
        extraction_id = config.extraction_id
        
        try:
            logger.info(f"Executing feature extraction: {extraction_id}")
            
            # Initialize result
            result = FeatureExtractionResult(
                extraction_id=extraction_id,
                content_id=content_id,
                feature_types=[content_type],
                start_time=start_time,
                config=config
            )
            
            with self.performance_monitor.monitor_context():
                all_features = {}
                
                # Extract features based on content type
                if content_type == "text" or FeatureType.TEXT in config.feature_types:
                    result.processing_log.append("Extracting text features")
                    text_features = await self.extract_text_features(content, config)
                    all_features.update(text_features)
                    result.text_features = np.concatenate([f.flatten() for f in text_features.values()])
                
                elif content_type == "image" or FeatureType.IMAGE in config.feature_types:
                    result.processing_log.append("Extracting image features")
                    image_features = await self.extract_image_features(content, config)
                    all_features.update(image_features)
                    result.image_features = np.concatenate([f.flatten() for f in image_features.values()])
                
                elif content_type == "audio" or FeatureType.AUDIO in config.feature_types:
                    result.processing_log.append("Extracting audio features")
                    sample_rate = config.sample_rate
                    audio_features = await self.extract_audio_features(content, sample_rate, config)
                    all_features.update(audio_features)
                    result.audio_features = np.concatenate([f.flatten() for f in audio_features.values()])
                
                elif content_type == "video" or FeatureType.VIDEO in config.feature_types:
                    result.processing_log.append("Extracting video features")
                    video_features = await self.extract_video_features(content, config)
                    all_features.update(video_features)
                    result.video_features = np.concatenate([f.flatten() for f in video_features.values()])
                
                # Combine all features
                if all_features:
                    combined_features = np.concatenate([f.flatten() for f in all_features.values()])
                    feature_names = []
                    
                    for category, features in all_features.items():
                        if features.ndim == 1:
                            feature_names.extend([f"{category}_{i}" for i in range(len(features))])
                        else:
                            feature_names.extend([f"{category}_{i}" for i in range(features.shape[0] * features.shape[1])])
                    
                    result.features = combined_features.reshape(1, -1)
                    result.feature_names = feature_names
                    
                    # Feature selection
                    if config.feature_selection and len(feature_names) > config.k_best_features:
                        result.processing_log.append("Performing feature selection")
                        # Note: For single sample, we can't do supervised feature selection
                        # Instead, we do unsupervised feature selection based on variance
                        feature_variance = np.var(result.features, axis=0)
                        top_indices = np.argsort(feature_variance)[-config.k_best_features:]
                        result.features = result.features[:, top_indices]
                        result.feature_names = [result.feature_names[i] for i in top_indices]
                    
                    # Dimensionality reduction
                    if config.dimensionality_reduction and result.features.shape[1] > 100:
                        result.processing_log.append("Applying dimensionality reduction")
                        reduced_features, reducer = await self.reduce_dimensionality(result.features, config)
                        result.features = reduced_features
                        result.feature_metadata["dimensionality_reducer"] = reducer
                
                # Calculate metrics
                metrics = FeatureMetrics()
                if result.features is not None:
                    metrics.total_features = len(result.feature_names)
                    metrics.selected_features = result.features.shape[1]
                    metrics.feature_types_count = {content_type: metrics.total_features}
                    metrics.extraction_methods_count = {method.value: 1 for method in config.extraction_methods}
                
                metrics.extraction_time_seconds = (datetime.utcnow() - start_time).total_seconds()
                result.metrics = metrics
                
                # Complete extraction
                result.end_time = datetime.utcnow()
                result.total_duration_seconds = (result.end_time - result.start_time).total_seconds()
                
                # Update Prometheus metrics
                self.FEATURES_EXTRACTED.labels(feature_type=content_type).inc(metrics.total_features)
                self.EXTRACTION_DURATION.labels(content_type=content_type).observe(result.total_duration_seconds)
                self.EXTRACTION_JOBS.labels(content_type=content_type, status="completed").inc()
                
                logger.info(f"Feature extraction {extraction_id} completed successfully")
                logger.info(f"Extracted {metrics.total_features} features in {metrics.extraction_time_seconds:.2f}s")
                
                return result
                
        except Exception as e:
            result.errors.append(str(e))
            result.end_time = datetime.utcnow()
            result.total_duration_seconds = (result.end_time - result.start_time).total_seconds()
            
            self.EXTRACTION_JOBS.labels(content_type=content_type, status="failed").inc()
            
            logger.error(f"Feature extraction {extraction_id} failed: {str(e)}")
            raise

    def _initialize_feature_extractors(self) -> Dict[str, Dict[str, Any]]:
        """Initialize feature extractors registry"""



        return {
            "text": {
                "statistical": ["word_count", "char_count", "sentence_count", "avg_word_length"],
                "vectorizers": ["tfidf", "count", "hash"],
                "transformers": ["bert", "roberta", "distilbert"],
                "linguistic": ["pos_tags", "named_entities", "dependencies"],
                "sentiment": ["polarity", "subjectivity", "emotion"],
                "readability": ["flesch_reading_ease", "flesch_kincaid_grade"]
            },
            "image": {
                "statistical": ["mean", "std", "skewness", "kurtosis"],
                "color": ["rgb_histogram", "hsv_histogram", "dominant_colors"],
                "texture": ["lbp", "glcm", "gabor", "wavelet"],
                "shape": ["contours", "moments", "fourier_descriptors"],
                "cnn": ["resnet", "vgg", "inception", "mobilenet"],
                "edges": ["canny", "sobel", "laplacian"],
                "hash": ["phash", "dhash", "whash"]
            },
            "audio": {
                "statistical": ["mean", "std", "skewness", "kurtosis", "energy"],
                "mfcc": ["mfcc_coefficients", "delta_mfcc", "delta2_mfcc"],
                "spectral": ["centroid", "bandwidth", "rolloff", "zcr"],
                "temporal": ["rms", "onset_strength", "tempo"],
                "rhythm": ["beat_tracker", "pulse", "rhythm_patterns"],
                "frequency": ["fft", "stft", "mel_spectrogram"],
                "chroma": ["chroma_stft", "chroma_cqt", "chroma_cens"]
            },
            "video": {
                "frames": ["frame_statistics", "frame_differences"],
                "motion": ["optical_flow", "motion_vectors"],
                "scenes": ["scene_detection", "shot_boundaries"],
                "faces": ["face_detection", "face_recognition", "emotion"],
                "objects": ["object_detection", "object_tracking"]
            }
        }

    async def _load_nlp_models(self):
        """Load NLP models"""



        try:
            # Load spaCy model
            try:
                self.nlp_models["spacy"] = spacy.load("en_core_web_sm")
            except IOError:
                logger.warning("spaCy English model not found, using blank model")
                self.nlp_models["spacy"] = spacy.blank("en")
            
            # Download NLTK data
            try:
                import nltk
                nltk.download('punkt', quiet=True)
                nltk.download('stopwords', quiet=True)
                nltk.download('vader_lexicon', quiet=True)
                nltk.download('averaged_perceptron_tagger', quiet=True)
            except Exception as e:
                logger.warning(f"NLTK data download failed: {e}")
            
            logger.info("NLP models loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load NLP models: {e}")

    async def _load_pretrained_models(self):
        """Load pre-trained models"""



        try:
            # Load Transformers models (lightweight versions)
            if self.config.get("enable_transformers", False):
                try:
                    self.pretrained_models["tokenizer"] = AutoTokenizer.from_pretrained("distilbert-base-uncased")
                    self.pretrained_models["text_model"] = AutoModel.from_pretrained("distilbert-base-uncased")
                except Exception as e:
                    logger.warning(f"Failed to load transformer models: {e}")
            
            logger.info("Pre-trained models loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load pre-trained models: {e}")

    async def _validate_extraction_config(self, config: FeatureConfig, content_type: str) -> Dict[str, Any]:
        """Validate extraction configuration"""
        errors = []
        
        if not config.feature_types and not content_type:
            errors.append("Either feature_types or content_type must be specified")
        
        if content_type == "image" and not CV2_AVAILABLE:
            errors.append("Image processing libraries not available")
        
        if content_type == "audio" and not AUDIO_AVAILABLE:
            errors.append("Audio processing libraries not available")
        
        if content_type == "video" and not VIDEO_AVAILABLE:
            errors.append("Video processing libraries not available")
        
        return {"valid": len(errors) == 0, "errors": errors}

    async def _preprocess_text(self, text: str, config: FeatureConfig) -> str:
        """Preprocess text for feature extraction"""



        try:
            # Basic cleaning
            text = text.lower().strip()
            
            # Remove special characters if needed
            if config.config.get("remove_special_chars", False):
                text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
            
            # Remove extra whitespace
            text = re.sub(r'\s+', ' ', text)
            
            return text
            
        except Exception as e:
            logger.error(f"Text preprocessing failed: {e}")
            return text

    async def _preprocess_image(self, image: np.ndarray, config: FeatureConfig) -> np.ndarray:
        """Preprocess image for feature extraction"""



        try:
            if not CV2_AVAILABLE:
                return image
            
            # Resize image
            if image.shape[:2] != config.image_size:
                image = cv2.resize(image, config.image_size)
            
            # Color space conversion
            if config.color_space == "HSV" and len(image.shape) == 3:
                image = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
            elif config.color_space == "LAB" and len(image.shape) == 3:
                image = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
            
            return image
            
        except Exception as e:
            logger.error(f"Image preprocessing failed: {e}")
            return image

    async def _preprocess_audio(self, audio: np.ndarray, sample_rate: int, config: FeatureConfig) -> np.ndarray:
        """Preprocess audio for feature extraction"""



        try:
            if not AUDIO_AVAILABLE:
                return audio
            
            # Normalize audio
            audio = librosa.util.normalize(audio)
            
            # Resample if needed
            if sample_rate != config.sample_rate:
                audio = librosa.resample(audio, orig_sr=sample_rate, target_sr=config.sample_rate)
            
            return audio
            
        except Exception as e:
            logger.error(f"Audio preprocessing failed: {e}")
            return audio

    # Continue with more helper methods for specific feature extraction...
    # For brevity, including the essential structure and main extraction methods

    async def _process_extraction_queue(self):
        """Background extraction job processor"""
        while True:
            try:
                job_data = await self.extraction_queue.get()
                
                extraction_id = job_data["extraction_id"]
                content = job_data["content"]
                content_type = job_data["content_type"]
                content_id = job_data["content_id"]
                config = job_data["config"]
                
                logger.info(f"Processing queued extraction: {extraction_id}")
                
                try:
                    result = await self._execute_feature_extraction(content, content_type, content_id, config)
                    
                    # Clean up
                    if extraction_id in self.active_extractions:
                        del self.active_extractions[extraction_id]
                    self.completed_extractions[extraction_id] = result
                    self.ACTIVE_EXTRACTIONS.dec()
                    
                    logger.info(f"Queued extraction completed: {extraction_id}")
                    
                except Exception as e:
                    # Handle extraction failure
                    if extraction_id in self.active_extractions:
                        del self.active_extractions[extraction_id]
                    
                    error_result = FeatureExtractionResult(
                        extraction_id=extraction_id,
                        content_id=content_id,
                        feature_types=[content_type]
                    )
                    error_result.errors.append(str(e))
                    error_result.start_time = config.created_at
                    error_result.end_time = datetime.utcnow()
                    
                    self.completed_extractions[extraction_id] = error_result
                    self.ACTIVE_EXTRACTIONS.dec()
                    
                    logger.error(f"Queued extraction failed: {extraction_id} - {str(e)}")
                
                self.extraction_queue.task_done()
                
            except Exception as e:
                logger.error(f"Extraction queue processor error: {str(e)}")
                await asyncio.sleep(5)

# Additional feature extraction implementations would continue here...
# The structure provides a comprehensive foundation for all feature extraction needs

class FeaturePipeline:
    """
    Advanced Feature Pipeline for End-to-End Feature Processing
    """
    
    def __init__(self, extractor: FeatureExtractor):
        self.extractor = extractor
        self.pipeline_id = f"pipeline_{uuid.uuid4().hex[:8]}"
        
        logger.info(f"FeaturePipeline initialized: {self.pipeline_id}")
    
    async def create_pipeline(self, 
                            steps: List[Dict[str, Any]],
                            pipeline_name: str) -> str:
        """Create feature processing pipeline"""



        try:
            pipeline_config = {
                "pipeline_id": str(uuid.uuid4()),
                "name": pipeline_name,
                "steps": steps,
                "created_at": datetime.utcnow()
            }
            
            # Validate pipeline steps
            for step in steps:
                if "type" not in step or "config" not in step:
                    raise ValueError(f"Invalid pipeline step: {step}")
            
            logger.info(f"Feature pipeline created: {pipeline_name}")
            return pipeline_config["pipeline_id"]
            
        except Exception as e:
            logger.error(f"Pipeline creation failed: {str(e)}")
            raise FeatureExtractionError(f"Pipeline creation failed: {str(e)}")
    
    async def execute_pipeline(self, 
                             pipeline_id: str,
                             content: Any,
                             content_type: str) -> FeatureExtractionResult:
        """Execute feature processing pipeline"""



        try:
            logger.info(f"Executing pipeline: {pipeline_id}")
            
            # Load pipeline configuration
            # This would load from database/cache in real implementation
            
            # Execute pipeline steps
            result = await self.extractor.extract_features(
                content, content_type, str(uuid.uuid4()), FeatureConfig()
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Pipeline execution failed: {str(e)}")
            raise FeatureExtractionError(f"Pipeline execution failed: {str(e)}")
