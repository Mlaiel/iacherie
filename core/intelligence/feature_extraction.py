"""Feature Extraction - Advanced Feature Engineering for Content Intelligence

Comprehensive feature extraction system for multimedia content analysis.
Implements state-of-the-art feature engineering techniques across audio,
visual, text, and metadata domains for intelligent content processing.

Features:
- Multi-modal feature extraction
- Time-series feature engineering
- Statistical and spectral analysis
- Deep learning-based features
- Semantic feature extraction
- Performance optimization

Author: Fahed Mlaiel <mlaiel@live.de>
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Any, Union, Callable
from dataclasses import dataclass
from enum import Enum
import numpy as np
import pandas as pd
from datetime import datetime
import json
import os
from concurrent.futures import ThreadPoolExecutor

# Scientific Computing
import scipy.stats as stats
import scipy.signal as signal
import scipy.fft as fft
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import PCA, FastICA, TruncatedSVD
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
from sklearn.feature_selection import SelectKBest, f_classif, chi2, mutual_info_classif

# Computer Vision
import cv2
from skimage import feature, filters, measure, segmentation
from skimage.feature import local_binary_pattern, hog, greycomatrix, greycoprops

# Audio Processing
import librosa
import librosa.feature
import soundfile as sf

# Natural Language Processing
import spacy
from textstat import flesch_reading_ease, flesch_kincaid_grade, smog_index
import re
from collections import Counter

# Deep Learning Features
import torch
import torchvision.transforms as transforms
from transformers import AutoModel, AutoTokenizer

# Core Dependencies
from ..processors.feature_processor import FeatureProcessor
from ..extractors.audio_extractor import AudioExtractor
from ..extractors.visual_extractor import VisualExtractor
from ..extractors.text_extractor import TextExtractor


class FeatureType(Enum):
    """
Feature extraction types"""

    STATISTICAL = "statistical"
    SPECTRAL = "spectral"
    TEMPORAL = "temporal"
    SPATIAL = "spatial"
    SEMANTIC = "semantic"
    STRUCTURAL = "structural"
    BEHAVIORAL = "behavioral"
    CONTEXTUAL = "contextual"


class ContentModality(Enum):
    """Content modality types"""

    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    METADATA = "metadata"
    HYBRID = "hybrid"


@dataclass
class FeatureConfig:
    """Feature extraction configuration"""
    feature_type: FeatureType
    modality: ContentModality
    extraction_method: str
    parameters: Dict[str, Any]
    output_dimensions: int
    normalization: str
    selection_criteria: Optional[str] = None


@dataclass
class ExtractionResult:
    """
Feature extraction result"""
    feature_vector: np.ndarray
    feature_names: List[str]
    extraction_time: float
    quality_score: float
    metadata: Dict[str, Any]


class AudioFeatureExtractor:
    """
Advanced audio feature extraction"""
    
    def __init__(self, sample_rate: int = 22050):
        try:
            logger.info(f"Executing __init__")
            
            # Implementation for __init__
            # Implementation: Add specific business logic here

            logger.debug("Method implemented")
            result = None  # Replace with actual implementation
            
            logger.info(f"__init__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__init__ failed: {e}")
            raise
    def extract_spectral_features(self, audio_data: np.ndarray) -> Dict[str, np.ndarray]:
        """
Extract spectral features from audio"""
        features = {}
        
        # Basic spectral features
        features['mfcc'] = librosa.feature.mfcc(y=audio_data, sr=self.sample_rate, n_mfcc=13)
        features['chroma'] = librosa.feature.chroma(y=audio_data, sr=self.sample_rate)
        features['spectral_centroid'] = librosa.feature.spectral_centroid(y=audio_data, sr=self.sample_rate)
        features['spectral_bandwidth'] = librosa.feature.spectral_bandwidth(y=audio_data, sr=self.sample_rate)
        features['spectral_rolloff'] = librosa.feature.spectral_rolloff(y=audio_data, sr=self.sample_rate)
        features['zero_crossing_rate'] = librosa.feature.zero_crossing_rate(audio_data)
        
        # Advanced spectral features
        features['mel_spectrogram'] = librosa.feature.melspectrogram(y=audio_data, sr=self.sample_rate)
        features['tonnetz'] = librosa.feature.tonnetz(y=audio_data, sr=self.sample_rate)
        features['spectral_contrast'] = librosa.feature.spectral_contrast(y=audio_data, sr=self.sample_rate)
        
        # Rhythm and tempo features
        tempo, beats = librosa.beat.beat_track(y=audio_data, sr=self.sample_rate)
        features['tempo'] = np.array([tempo])
        features['beat_frames'] = beats
        
        return features
    
    def extract_temporal_features(self, audio_data: np.ndarray) -> Dict[str, float]:
        """
Extract temporal features from audio"""
        features = {}
        
        # Basic temporal statistics
        features['duration'] = len(audio_data) / self.sample_rate
        features['rms_energy'] = np.sqrt(np.mean(audio_data**2))
        features['peak_amplitude'] = np.max(np.abs(audio_data))
        features['zero_crossing_rate_mean'] = np.mean(librosa.feature.zero_crossing_rate(audio_data))
        
        # Onset detection
        onset_frames = librosa.onset.onset_detect(y=audio_data, sr=self.sample_rate)
        features['onset_density'] = len(onset_frames) / features['duration']
        
        # Dynamic range
        features['dynamic_range'] = np.max(audio_data) - np.min(audio_data)
        
        # Silence ratio
        silence_threshold = 0.01 * features['peak_amplitude']
        silence_ratio = np.sum(np.abs(audio_data) < silence_threshold) / len(audio_data)
        features['silence_ratio'] = silence_ratio
        
        return features


class VisualFeatureExtractor:
    """
Advanced visual feature extraction"""
    
    def __init__(self):
        """
Initialize visual feature extractor with computer vision models"""
        self.logger = logging.getLogger(f"{__name__}.VisualFeatureExtractor")
        self.feature_types = ['color', 'texture', 'shape', 'edges', 'keypoints']
        self.color_spaces = ['RGB', 'HSV', 'LAB', 'YUV', 'GRAY']
        self.texture_methods = ['LBP', 'GLCM', 'Gabor', 'Wavelet']
        self.edge_detectors = ['Canny', 'Sobel', 'Laplacian', 'Scharr']
        self.keypoint_algorithms = ['SIFT', 'SURF', 'ORB', 'FAST']
        self.shape_descriptors = ['Hu_moments', 'Fourier_descriptors', 'Contour_features']
        self.feature_cache = {}
        self.logger.info("VisualFeatureExtractor initialized with CV algorithms")
    
    def extract_color_features(self, image: np.ndarray) -> Dict[str, np.ndarray]:
        """Extract color-based features"""
        features = {}
        
        # Convert to different color spaces
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        
        # Color histograms
        features['bgr_histogram'] = np.concatenate([
            cv2.calcHist([image], [i], None, [256], [0, 256]).flatten()
            for i in range(3)
        ])
        
        features['hsv_histogram'] = np.concatenate([
            cv2.calcHist([hsv], [i], None, [256], [0, 256]).flatten()
            for i in range(3)
        ])
        
        # Color moments
        for i, channel in enumerate(['b', 'g', 'r']):
            channel_data = image[:, :, i].flatten()
            features[f'{channel}_mean'] = np.array([np.mean(channel_data)])
            features[f'{channel}_std'] = np.array([np.std(channel_data)])
            features[f'{channel}_skewness'] = np.array([stats.skew(channel_data)])
            features[f'{channel}_kurtosis'] = np.array([stats.kurtosis(channel_data)])
        
        # Dominant colors using K-means
        pixels = image.reshape(-1, 3)
        from sklearn.cluster import KMeans
        kmeans = KMeans(n_clusters=5, random_state=42)
        kmeans.fit(pixels)
        features['dominant_colors'] = kmeans.cluster_centers_.flatten()
        
        return features
    
    def extract_texture_features(self, image: np.ndarray) -> Dict[str, np.ndarray]:
        """
Extract texture features"""
        features = {}
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Local Binary Patterns
        lbp = local_binary_pattern(gray, P=8, R=1, method='uniform')
        features['lbp_histogram'] = np.histogram(lbp, bins=10)[0].astype(float)
        
        # HOG features
        hog_features = hog(gray, orientations=9, pixels_per_cell=(8, 8),
                          cells_per_block=(2, 2), visualize=False)
        features['hog'] = hog_features
        
        # Gray-Level Co-occurrence Matrix (GLCM)
        distances = [1, 2, 3]
        angles = [0, 45, 90, 135]
        properties = ['contrast', 'dissimilarity', 'homogeneity', 'energy']
        
        glcm_features = []
        for distance in distances:
            for angle in angles:
                glcm = greycomatrix(gray, [distance], [np.radians(angle)], 
                                 levels=256, symmetric=True, normed=True)
                for prop in properties:
                    glcm_features.append(greycoprops(glcm, prop)[0, 0])
        
        features['glcm'] = np.array(glcm_features)
        
        # Gabor filters
        gabor_responses = []
        for theta in range(0, 180, 30):
            for frequency in [0.1, 0.3, 0.5]:
                real, _ = filters.gabor(gray, frequency=frequency, theta=np.radians(theta))
                gabor_responses.extend([np.mean(real), np.std(real)])
        
        features['gabor'] = np.array(gabor_responses)
        
        return features
    
    def extract_shape_features(self, image: np.ndarray) -> Dict[str, np.ndarray]:
        """
Extract shape and structure features"""
        features = {}
        
        # Convert to grayscale and apply edge detection
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        
        # Contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            # Largest contour features
            largest_contour = max(contours, key=cv2.contourArea)
            
            features['contour_area'] = np.array([cv2.contourArea(largest_contour)])
            features['contour_perimeter'] = np.array([cv2.arcLength(largest_contour, True)])
            
            # Hu moments
            moments = cv2.moments(largest_contour)
            hu_moments = cv2.HuMoments(moments).flatten()
            features['hu_moments'] = hu_moments
            
            # Aspect ratio and extent
            x, y, w, h = cv2.boundingRect(largest_contour)
            features['aspect_ratio'] = np.array([w / h]) if h > 0 else np.array([0])
            features['extent'] = np.array([cv2.contourArea(largest_contour) / (w * h)]) if w * h > 0 else np.array([0])
        else:
            # Default values when no contours found
            features['contour_area'] = np.array([0])
            features['contour_perimeter'] = np.array([0])
            features['hu_moments'] = np.zeros(7)
            features['aspect_ratio'] = np.array([0])
            features['extent'] = np.array([0])
        
        # Edge density
        features['edge_density'] = np.array([np.sum(edges > 0) / edges.size])
        
        return features


class TextFeatureExtractor:
        try:
            logger.info(f"Executing __init__")
            
            # Implementation for __init__
            # Implementation: Add specific business logic here

            logger.debug("Method implemented")
            result = None  # Replace with actual implementation
            
            logger.info(f"__init__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__init__ failed: {e}")
            raise
        features['edge_density'] = np.array([np.sum(edges > 0) / edges.size])
        
        return features


class TextFeatureExtractor:
    """
Advanced text feature extraction"""
    
    def __init__(self):
        self.nlp = spacy.load('en_core_web_sm')
        
    def extract_linguistic_features(self, text: str) -> Dict[str, float]:
        """
Extract linguistic and readability features"""
        features = {}
        
        # Basic text statistics
        features['char_count'] = len(text)
        features['word_count'] = len(text.split())
        features['sentence_count'] = len([s for s in text.split('.') if s.strip()])
        features['paragraph_count'] = len([p for p in text.split('\n\n') if p.strip()])
        
        # Average lengths
        words = text.split()
        if words:
            features['avg_word_length'] = np.mean([len(word) for word in words])
            features['avg_sentence_length'] = features['word_count'] / features['sentence_count'] if features['sentence_count'] > 0 else 0
        else:
            features['avg_word_length'] = 0
            features['avg_sentence_length'] = 0
        
        # Readability scores
        try:
            features['flesch_reading_ease'] = flesch_reading_ease(text)
            features['flesch_kincaid_grade'] = flesch_kincaid_grade(text)
            features['smog_index'] = smog_index(text)
        except:
            features['flesch_reading_ease'] = 0
            features['flesch_kincaid_grade'] = 0
            features['smog_index'] = 0
        
        # Lexical diversity
        unique_words = set(words)
        features['lexical_diversity'] = len(unique_words) / len(words) if words else 0
        
        # Punctuation and capitalization
        features['punctuation_ratio'] = sum(1 for c in text if c in '.,!?;:') / len(text) if text else 0
        features['uppercase_ratio'] = sum(1 for c in text if c.isupper()) / len(text) if text else 0
        
        return features
    
    def extract_semantic_features(self, text: str) -> Dict[str, np.ndarray]:
        """
Extract semantic features using NLP"""
        features = {}
        
        # Process text with spaCy
        doc = self.nlp(text)
        
        # Part-of-speech distribution
        pos_counts = Counter([token.pos_ for token in doc])
        total_tokens = len(doc)
        pos_features = {}
        for pos_tag in ['NOUN', 'VERB', 'ADJ', 'ADV', 'PRON', 'DET', 'ADP', 'NUM', 'CONJ', 'PRT']:
            pos_features[f'pos_{pos_tag.lower()}'] = pos_counts.get(pos_tag, 0) / total_tokens if total_tokens > 0 else 0
        
        features['pos_distribution'] = np.array(list(pos_features.values()))
        
        # Named entity features
        entity_counts = Counter([ent.label_ for ent in doc.ents])
        entity_features = {}
        for entity_type in ['PERSON', 'ORG', 'GPE', 'MONEY', 'PERCENT', 'DATE', 'TIME']:
            entity_features[f'entity_{entity_type.lower()}'] = entity_counts.get(entity_type, 0)
        
        features['entity_distribution'] = np.array(list(entity_features.values()))
        
        # Dependency parsing features
        dep_counts = Counter([token.dep_ for token in doc])
        dep_features = {}
        for dep_label in ['nsubj', 'dobj', 'iobj', 'amod', 'advmod', 'prep', 'det', 'aux']:
            dep_features[f'dep_{dep_label}'] = dep_counts.get(dep_label, 0) / total_tokens if total_tokens > 0 else 0
        
        features['dependency_distribution'] = np.array(list(dep_features.values()))
        
        # Sentiment and emotion indicators
        sentiment_words = {
            'positive': ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic'],
            'negative': ['bad', 'terrible', 'awful', 'horrible', 'disappointing', 'frustrating'],
            'emotional': ['love', 'hate', 'excited', 'angry', 'sad', 'happy', 'surprised']
        }
        
        text_lower = text.lower()
        sentiment_features = {}
        for category, word_list in sentiment_words.items():
            sentiment_features[f'sentiment_{category}'] = sum(1 for word in word_list if word in text_lower) / len(words) if words else 0
        
        features['sentiment_indicators'] = np.array(list(sentiment_features.values()))
        
        return features
    
    def extract_tfidf_features(
        self,
        texts: List[str],
        max_features: int = 1000,
        ngram_range: Tuple[int, int] = (1, 2)
    ) -> Tuple[np.ndarray, List[str]]:
        """
Extract TF-IDF features from text corpus"""
        vectorizer = TfidfVectorizer(
            max_features=max_features,
            ngram_range=ngram_range,
            stop_words='english',
            lowercase=True,
            strip_accents='unicode'
        )
        
        tfidf_matrix = vectorizer.fit_transform(texts)
        feature_names = vectorizer.get_feature_names_out()
        
        return tfidf_matrix.toarray(), list(feature_names)


class MetadataFeatureExtractor:
    """
Extract features from content metadata"""
    
    def extract_temporal_features(self, metadata: Dict[str, Any]) -> Dict[str, float]:
        """
Extract temporal features from metadata"""
        features = {}
        
        # Creation time features
        if 'created_at' in metadata:
            created_at = pd.to_datetime(metadata['created_at'])
            features['hour_of_day'] = created_at.hour
            features['day_of_week'] = created_at.dayofweek
            features['month'] = created_at.month
            features['is_weekend'] = 1.0 if created_at.dayofweek >= 5 else 0.0
        
        # Duration features
        if 'duration' in metadata:
            duration = metadata['duration']
            features['duration_seconds'] = duration
            features['duration_minutes'] = duration / 60
            features['is_short_form'] = 1.0 if duration < 60 else 0.0
            features['is_long_form'] = 1.0 if duration > 600 else 0.0
        
        # Size features
        if 'file_size' in metadata:
            file_size = metadata['file_size']
            features['file_size_mb'] = file_size / (1024 * 1024)
            features['is_large_file'] = 1.0 if file_size > 100 * 1024 * 1024 else 0.0
        
        return features
    
    def extract_engagement_features(self, metadata: Dict[str, Any]) -> Dict[str, float]:
        """
Extract engagement-related features"""
        features = {}
        
        # Basic engagement metrics
        features['views'] = metadata.get('views', 0)
        features['likes'] = metadata.get('likes', 0)
        features['shares'] = metadata.get('shares', 0)
        features['comments'] = metadata.get('comments', 0)
        
        # Derived engagement features
        if features['views'] > 0:
            features['like_rate'] = features['likes'] / features['views']
            features['comment_rate'] = features['comments'] / features['views']
            features['share_rate'] = features['shares'] / features['views']
            features['engagement_rate'] = (features['likes'] + features['comments'] + features['shares']) / features['views']
        else:
            features['like_rate'] = 0
            features['comment_rate'] = 0
            features['share_rate'] = 0
            features['engagement_rate'] = 0
        
        # Platform-specific features
        features['platform_id'] = hash(metadata.get('platform', 'unknown')) % 1000
        features['has_hashtags'] = 1.0 if metadata.get('hashtags') else 0.0
        features['hashtag_count'] = len(metadata.get('hashtags', []))
        
        return features


class FeatureExtraction:
    """
    Comprehensive feature extraction system for content intelligence
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize feature extraction system
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize extractors
        self.audio_extractor = AudioFeatureExtractor()
        self.visual_extractor = VisualFeatureExtractor()
        self.text_extractor = TextFeatureExtractor()
        self.metadata_extractor = MetadataFeatureExtractor()
        
        # Initialize processors
        self._initialize_processors()
        
        # Feature tracking
        self.extraction_history = {}
        self.feature_cache = {}
        self.performance_metrics = {
            "extractions_performed": 0,
            "total_extraction_time": 0.0,
            "average_extraction_time": 0.0,
            "cache_hit_rate": 0.0,
            "feature_dimensions": {}
        }
    
    def _initialize_processors(self) -> None:
        """Initialize feature processors"""
        try:
            self.feature_processor = FeatureProcessor(self.config)
            self.audio_processor = AudioExtractor(self.config)
            self.visual_processor = VisualExtractor(self.config)
            self.text_processor = TextExtractor(self.config)
            
            self.logger.info("Feature processors initialized successfully")
            
        except Exception as e:
            self.logger.warning(f"Some processors could not be initialized: {e}")
    
    async def extract_features(
        self,
        content_data: Dict[str, Any],
        feature_configs: List[FeatureConfig],
        cache_key: Optional[str] = None
    ) -> Dict[str, ExtractionResult]:
        """
        Extract features from content data
        
        Args:
            content_data: Content data dictionary
            feature_configs: List of feature extraction configurations
            cache_key: Optional cache key for result caching
            
        Returns:
            Dict mapping feature types to extraction results
        """
        start_time = datetime.now()
        
        try:
            # Check cache if key provided
            if cache_key and cache_key in self.feature_cache:
                self.performance_metrics["cache_hit_rate"] = (
                    self.performance_metrics["cache_hit_rate"] * 0.9 + 0.1
                )
                return self.feature_cache[cache_key]
            
            results = {}
            
            # Process each feature configuration
            for config in feature_configs:
                try:
                    result = await self._extract_single_feature(content_data, config)
                    results[f"{config.modality.value}_{config.feature_type.value}"] = result
                    
                except Exception as e:
                    self.logger.error(f"Feature extraction failed for {config.modality.value}_{config.feature_type.value}: {e}")
                    continue
            
            # Cache results if key provided
            if cache_key:
                self.feature_cache[cache_key] = results
            
            # Update metrics
            extraction_time = (datetime.now() - start_time).total_seconds()
            self._update_extraction_metrics(extraction_time, results)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Feature extraction failed: {e}")
            return {}
    
    async def _extract_single_feature(
        self,
        content_data: Dict[str, Any],
        config: FeatureConfig
    ) -> ExtractionResult:
        """Extract a single feature type"""
        start_time = datetime.now()
        
        try:
            # Route to appropriate extractor based on modality
            if config.modality == ContentModality.AUDIO:
                features = await self._extract_audio_features(content_data, config)
            elif config.modality == ContentModality.VIDEO:
                features = await self._extract_video_features(content_data, config)
            elif config.modality == ContentModality.IMAGE:
                features = await self._extract_image_features(content_data, config)
            elif config.modality == ContentModality.TEXT:
                features = await self._extract_text_features(content_data, config)
            elif config.modality == ContentModality.METADATA:
                features = await self._extract_metadata_features(content_data, config)
            else:
                raise ValueError(f"Unsupported modality: {config.modality}")
            
            # Apply post-processing
            processed_features = await self._post_process_features(features, config)
            
            # Calculate quality score
            quality_score = self._calculate_feature_quality(processed_features)
            
            extraction_time = (datetime.now() - start_time).total_seconds()
            
            return ExtractionResult(
                feature_vector=processed_features['vector'],
                feature_names=processed_features['names'],
                extraction_time=extraction_time,
                quality_score=quality_score,
                metadata=processed_features.get('metadata', {})
            )
            
        except Exception as e:
            self.logger.error(f"Single feature extraction failed: {e}")
            raise
    
    async def _extract_audio_features(
        self,
        content_data: Dict[str, Any],
        config: FeatureConfig
    ) -> Dict[str, Any]:
        """Extract audio features"""
        audio_data = content_data.get('audio_data')
        if audio_data is None:
            raise ValueError("No audio data provided")
        
        if config.feature_type == FeatureType.SPECTRAL:
            return self.audio_extractor.extract_spectral_features(audio_data)
        elif config.feature_type == FeatureType.TEMPORAL:
            return self.audio_extractor.extract_temporal_features(audio_data)
        else:
            # Combined features
            spectral = self.audio_extractor.extract_spectral_features(audio_data)
            temporal = self.audio_extractor.extract_temporal_features(audio_data)
            return {**spectral, **temporal}
    
    async def _extract_video_features(
        self,
        content_data: Dict[str, Any],
        config: FeatureConfig
    ) -> Dict[str, Any]:
        """Extract video features (combination of visual and audio)"""
        features = {}
        
        # Extract visual features from frames
        if 'video_frames' in content_data:
            for i, frame in enumerate(content_data['video_frames'][:5]):  # Process first 5 frames
                frame_features = await self._extract_image_features({'image_data': frame}, config)
                for key, value in frame_features.items():
                    features[f'frame_{i}_{key}'] = value
        
        # Extract audio features if available
        if 'audio_data' in content_data:
            audio_features = await self._extract_audio_features(content_data, config)
            for key, value in audio_features.items():
                features[f'audio_{key}'] = value
        
        return features
    
    async def _extract_image_features(
        self,
        content_data: Dict[str, Any],
        config: FeatureConfig
    ) -> Dict[str, Any]:
        """
Extract image features"""
        image_data = content_data.get('image_data')
        if image_data is None:
            raise ValueError("No image data provided")
        
        if config.feature_type == FeatureType.SPECTRAL:
            return self.visual_extractor.extract_color_features(image_data)
        elif config.feature_type == FeatureType.STRUCTURAL:
            return self.visual_extractor.extract_texture_features(image_data)
        elif config.feature_type == FeatureType.SPATIAL:
            return self.visual_extractor.extract_shape_features(image_data)
        else:
            # Combined features
            color = self.visual_extractor.extract_color_features(image_data)
            texture = self.visual_extractor.extract_texture_features(image_data)
            shape = self.visual_extractor.extract_shape_features(image_data)
            return {**color, **texture, **shape}
    
    async def _extract_text_features(
        self,
        content_data: Dict[str, Any],
        config: FeatureConfig
    ) -> Dict[str, Any]:
        """Extract text features"""
        text_data = content_data.get('text_data')
        if text_data is None:
            raise ValueError("No text data provided")
        
        if config.feature_type == FeatureType.SEMANTIC:
            return self.text_extractor.extract_semantic_features(text_data)
        elif config.feature_type == FeatureType.STRUCTURAL:
            return {**self.text_extractor.extract_linguistic_features(text_data)}
        else:
            # Combined features
            semantic = self.text_extractor.extract_semantic_features(text_data)
            linguistic = self.text_extractor.extract_linguistic_features(text_data)
            
            # Convert linguistic features to arrays for consistency
            linguistic_arrays = {k: np.array([v]) for k, v in linguistic.items()}
            
            return {**semantic, **linguistic_arrays}
    
    async def _extract_metadata_features(
        self,
        content_data: Dict[str, Any],
        config: FeatureConfig
    ) -> Dict[str, Any]:
        """Extract metadata features"""
        metadata = content_data.get('metadata', {})
        
        if config.feature_type == FeatureType.TEMPORAL:
            return self.metadata_extractor.extract_temporal_features(metadata)
        elif config.feature_type == FeatureType.BEHAVIORAL:
            return self.metadata_extractor.extract_engagement_features(metadata)
        else:
            # Combined features
            temporal = self.metadata_extractor.extract_temporal_features(metadata)
            engagement = self.metadata_extractor.extract_engagement_features(metadata)
            return {**temporal, **engagement}
    
    async def _post_process_features(
        self,
        features: Dict[str, Any],
        config: FeatureConfig
    ) -> Dict[str, Any]:
        """
Post-process extracted features"""
        try:
            # Flatten all features into a single vector
            feature_vector = []
            feature_names = []
            
            for key, value in features.items():
                if isinstance(value, np.ndarray):
                    if value.ndim == 1:
                        feature_vector.extend(value)
                        feature_names.extend([f"{key}_{i}" for i in range(len(value))])
                    else:
                        # Flatten multi-dimensional arrays
                        flattened = value.flatten()
                        feature_vector.extend(flattened)
                        feature_names.extend([f"{key}_{i}" for i in range(len(flattened))])
                else:
                    # Scalar values
                    feature_vector.append(float(value))
                    feature_names.append(key)
            
            feature_vector = np.array(feature_vector)
            
            # Apply normalization
            if config.normalization == "standard":
                scaler = StandardScaler()
                feature_vector = scaler.fit_transform(feature_vector.reshape(-1, 1)).flatten()
            elif config.normalization == "minmax":
                scaler = MinMaxScaler()
                feature_vector = scaler.fit_transform(feature_vector.reshape(-1, 1)).flatten()
            elif config.normalization == "robust":
                scaler = RobustScaler()
                feature_vector = scaler.fit_transform(feature_vector.reshape(-1, 1)).flatten()
            
            # Apply dimensionality reduction if needed
            if config.output_dimensions > 0 and len(feature_vector) > config.output_dimensions:
                pca = PCA(n_components=config.output_dimensions)
                feature_vector = pca.fit_transform(feature_vector.reshape(1, -1)).flatten()
                feature_names = [f"pca_{i}" for i in range(config.output_dimensions)]
            
            # Feature selection if specified
            if config.selection_criteria and len(feature_vector) > config.output_dimensions:
                # This would require labels for supervised selection
                # For now, just use variance-based selection
                if len(feature_vector) > 1:
                    selector = SelectKBest(f_classif, k=min(config.output_dimensions, len(feature_vector)))
                    # Create dummy labels for unsupervised selection
                    dummy_labels = np.zeros(1)
                    try:
                        feature_vector = selector.fit_transform(
                            feature_vector.reshape(1, -1), dummy_labels
                        ).flatten()
                        selected_indices = selector.get_support(indices=True)
                        feature_names = [feature_names[i] for i in selected_indices]
                    except:
                        pass  # Keep original features if selection fails
            
            return {
                'vector': feature_vector,
                'names': feature_names,
                'metadata': {
                    'original_dimensions': len(features),
                    'final_dimensions': len(feature_vector),
                    'normalization': config.normalization,
                    'feature_type': config.feature_type.value,
                    'modality': config.modality.value
                }
            }
            
        except Exception as e:
            self.logger.error(f"Feature post-processing failed: {e}")
            # Return raw features as fallback
            return {
                'vector': np.array(list(features.values())).flatten(),
                'names': list(features.keys()),
                'metadata': {}
            }
    
    def _calculate_feature_quality(self, features: Dict[str, Any]) -> float:
        """Calculate quality score for extracted features"""
        try:
            feature_vector = features['vector']
            
            # Quality metrics
            completeness = 1.0 - (np.sum(np.isnan(feature_vector)) / len(feature_vector))
            variance = np.var(feature_vector) if len(feature_vector) > 1 else 0.0
            range_score = (np.max(feature_vector) - np.min(feature_vector)) if len(feature_vector) > 1 else 0.0
            
            # Normalize variance and range scores
            variance_score = min(variance, 1.0)
            range_score = min(range_score, 1.0)
            
            # Combined quality score
            quality = 0.4 * completeness + 0.3 * variance_score + 0.3 * range_score
            
            return min(max(quality, 0.0), 1.0)
            
        except Exception:
            return 0.5  # Default quality score
    
    def _update_extraction_metrics(
        self,
        extraction_time: float,
        results: Dict[str, ExtractionResult]
    ) -> None:
        """
Update extraction performance metrics"""
        self.performance_metrics["extractions_performed"] += 1
        self.performance_metrics["total_extraction_time"] += extraction_time
        
        # Update average extraction time
        self.performance_metrics["average_extraction_time"] = (
            self.performance_metrics["total_extraction_time"] /
            self.performance_metrics["extractions_performed"]
        )
        
        # Update feature dimensions tracking
        for feature_type, result in results.items():
            self.performance_metrics["feature_dimensions"][feature_type] = len(result.feature_vector)
    
    async def extract_multi_modal_features(
        self,
        content_data: Dict[str, Any],
        target_dimensions: int = 512
    ) -> ExtractionResult:
        """Extract comprehensive multi-modal features"""
        try:
            all_features = {}
            
            # Define feature configurations for each modality
            configs = []
            
            if 'audio_data' in content_data:
                configs.append(FeatureConfig(
                    feature_type=FeatureType.SPECTRAL,
                    modality=ContentModality.AUDIO,
                    extraction_method="librosa",
                    parameters={},
                    output_dimensions=128,
                    normalization="standard"
                ))
            
            if 'image_data' in content_data or 'video_frames' in content_data:
                configs.append(FeatureConfig(
                    feature_type=FeatureType.SPATIAL,
                    modality=ContentModality.IMAGE,
                    extraction_method="opencv",
                    parameters={},
                    output_dimensions=128,
                    normalization="standard"
                ))
            
            if 'text_data' in content_data:
                configs.append(FeatureConfig(
                    feature_type=FeatureType.SEMANTIC,
                    modality=ContentModality.TEXT,
                    extraction_method="spacy",
                    parameters={},
                    output_dimensions=128,
                    normalization="standard"
                ))
            
            if 'metadata' in content_data:
                configs.append(FeatureConfig(
                    feature_type=FeatureType.BEHAVIORAL,
                    modality=ContentModality.METADATA,
                    extraction_method="statistical",
                    parameters={},
                    output_dimensions=64,
                    normalization="standard"
                ))
            
            # Extract features for each configuration
            results = await self.extract_features(content_data, configs)
            
            # Combine all feature vectors
            combined_vector = []
            combined_names = []
            
            for feature_type, result in results.items():
                combined_vector.extend(result.feature_vector)
                combined_names.extend([f"{feature_type}_{name}" for name in result.feature_names])
            
            combined_vector = np.array(combined_vector)
            
            # Apply final dimensionality reduction if needed
            if len(combined_vector) > target_dimensions:
                pca = PCA(n_components=target_dimensions)
                combined_vector = pca.fit_transform(combined_vector.reshape(1, -1)).flatten()
                combined_names = [f"multimodal_pca_{i}" for i in range(target_dimensions)]
            
            return ExtractionResult(
                feature_vector=combined_vector,
                feature_names=combined_names,
                extraction_time=sum(r.extraction_time for r in results.values()),
                quality_score=np.mean([r.quality_score for r in results.values()]),
                metadata={
                    'modalities_used': list(results.keys()),
                    'total_dimensions': len(combined_vector),
                    'extraction_method': 'multi_modal'
                }
            )
            
        except Exception as e:
            self.logger.error(f"Multi-modal feature extraction failed: {e}")
            raise
    
    async def get_feature_importance(
        self,
        features: np.ndarray,
        targets: np.ndarray,
        feature_names: List[str]
    ) -> Dict[str, float]:
        """Calculate feature importance scores"""
        try:
            from sklearn.ensemble import RandomForestRegressor
            from sklearn.inspection import permutation_importance
            
            # Train a simple model to get feature importance
            rf = RandomForestRegressor(n_estimators=100, random_state=42)
            rf.fit(features.reshape(-1, 1) if features.ndim == 1 else features, targets)
            
            # Get feature importance
            if hasattr(rf, 'feature_importances_'):
                importance_scores = rf.feature_importances_
            else:
                importance_scores = np.ones(len(feature_names)) / len(feature_names)
            
            # Create importance dictionary
            importance_dict = {}
            for i, name in enumerate(feature_names):
                if i < len(importance_scores):
                    importance_dict[name] = float(importance_scores[i])
                else:
                    importance_dict[name] = 0.0
            
            return importance_dict
            
        except Exception as e:
            self.logger.error(f"Feature importance calculation failed: {e}")
            return {name: 1.0 / len(feature_names) for name in feature_names}
    
    async def get_extraction_metrics(self) -> Dict[str, Any]:
        """Get feature extraction performance metrics"""
        return self.performance_metrics.copy()
    
    def clear_cache(self) -> None:
        """
Clear feature extraction cache"""
        self.feature_cache.clear()
        self.logger.info("Feature extraction cache cleared")
