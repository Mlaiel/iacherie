#!/usr/bin/env python3
"""
🔧 Automated Feature Engineering Engine
ML Engineer Implementation - Advanced Feature Discovery & Synthesis

Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
Contact: mlaiel@live.de

Enterprise automated feature engineering with deep feature synthesis,
multimodal feature fusion, and creator-specific feature generation.
"""

import asyncio
import logging
import json
import numpy as np
import pandas as pd
import pickle
from typing import Dict, List, Tuple, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import itertools
from concurrent.futures import ThreadPoolExecutor
import time
from pathlib import Path
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
from sklearn.feature_selection import SelectKBest, f_classif, mutual_info_classif
from sklearn.decomposition import PCA, FastICA, TruncatedSVD
from sklearn.cluster import KMeans
import librosa
import cv2
from transformers import AutoTokenizer, AutoModel
import torch
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class FeatureType(Enum):
    """Types of features"""
    NUMERICAL = "numerical"
    CATEGORICAL = "categorical"
    TEXT = "text"
    AUDIO = "audio"
    IMAGE = "image"
    TIME_SERIES = "time_series"
    BEHAVIORAL = "behavioral"
    SYNTHETIC = "synthetic"

class TransformationType(Enum):
    """Feature transformation types"""
    POLYNOMIAL = "polynomial"
    LOGARITHMIC = "logarithmic"
    EXPONENTIAL = "exponential"
    TRIGONOMETRIC = "trigonometric"
    INTERACTION = "interaction"
    AGGREGATION = "aggregation"
    BINNING = "binning"
    ENCODING = "encoding"

class CreatorType(Enum):
    """Creator types for specialized feature engineering"""
    MUSICIAN = "musician"
    BLOGGER = "blogger"
    PHOTOGRAPHER = "photographer"
    INFLUENCER = "influencer"
    COMEDIAN = "comedian"
    GENERAL = "general"

@dataclass
class FeatureMetadata:
    """Metadata for generated features"""
    name: str
    feature_type: FeatureType
    transformation: TransformationType
    importance_score: float = 0.0
    correlation_with_target: float = 0.0
    creation_timestamp: float = field(default_factory=time.time)
    source_features: List[str] = field(default_factory=list)
    computation_cost: float = 0.0
    stability_score: float = 0.0
    interpretability_score: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'name': self.name,
            'feature_type': self.feature_type.value,
            'transformation': self.transformation.value,
            'importance_score': self.importance_score,
            'correlation_with_target': self.correlation_with_target,
            'creation_timestamp': self.creation_timestamp,
            'source_features': self.source_features,
            'computation_cost': self.computation_cost,
            'stability_score': self.stability_score,
            'interpretability_score': self.interpretability_score
        }

@dataclass
class FeatureEngineeringConfig:
    """Configuration for automated feature engineering"""
    creator_type: CreatorType = CreatorType.GENERAL
    max_features: int = 1000
    max_polynomial_degree: int = 3
    enable_interactions: bool = True
    enable_aggregations: bool = True
    enable_dimensionality_reduction: bool = True
    target_correlation_threshold: float = 0.1
    feature_importance_threshold: float = 0.01
    stability_threshold: float = 0.7
    max_computation_time_seconds: int = 3600
    enable_multimodal_fusion: bool = True
    parallel_workers: int = 8

class AudioFeatureExtractor:
    """Specialized audio feature extraction for musicians"""
    
    @staticmethod
    def extract_audio_features(audio_data: np.ndarray, sr: int = 22050) -> Dict[str, float]:
        """Extract comprehensive audio features"""
        features = {}
        
        try:
            # Basic audio characteristics
            features['duration'] = len(audio_data) / sr
            features['rms_energy'] = float(np.sqrt(np.mean(audio_data ** 2)))
            features['zero_crossing_rate'] = float(np.mean(librosa.feature.zero_crossing_rate(audio_data)[0]))
            
            # Spectral features
            spectral_centroids = librosa.feature.spectral_centroid(y=audio_data, sr=sr)[0]
            features['spectral_centroid_mean'] = float(np.mean(spectral_centroids))
            features['spectral_centroid_std'] = float(np.std(spectral_centroids))
            
            spectral_rolloff = librosa.feature.spectral_rolloff(y=audio_data, sr=sr)[0]
            features['spectral_rolloff_mean'] = float(np.mean(spectral_rolloff))
            
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio_data, sr=sr)[0]
            features['spectral_bandwidth_mean'] = float(np.mean(spectral_bandwidth))
            
            # MFCC features
            mfccs = librosa.feature.mfcc(y=audio_data, sr=sr, n_mfcc=13)
            for i in range(13):
                features[f'mfcc_{i}_mean'] = float(np.mean(mfccs[i]))
                features[f'mfcc_{i}_std'] = float(np.std(mfccs[i]))
            
            # Chroma features
            chroma = librosa.feature.chroma_stft(y=audio_data, sr=sr)
            features['chroma_mean'] = float(np.mean(chroma))
            features['chroma_std'] = float(np.std(chroma))
            
            # Tempo and rhythm
            tempo, _ = librosa.beat.beat_track(y=audio_data, sr=sr)
            features['tempo'] = float(tempo)
            
            # Harmonic and percussive components
            harmonic, percussive = librosa.effects.hpss(audio_data)
            features['harmonic_energy'] = float(np.sqrt(np.mean(harmonic ** 2)))
            features['percussive_energy'] = float(np.sqrt(np.mean(percussive ** 2)))
            
        except Exception as e:
            logger.warning(f"⚠️ Audio feature extraction error: {str(e)}")
        
        return features

class ImageFeatureExtractor:
    """Specialized image feature extraction for photographers"""
    
    @staticmethod
    def extract_image_features(image_data: np.ndarray) -> Dict[str, float]:
        """Extract comprehensive image features"""
        features = {}
        
        try:
            # Convert to grayscale if needed
            if len(image_data.shape) == 3:
                gray = cv2.cvtColor(image_data, cv2.COLOR_RGB2GRAY)
            else:
                gray = image_data
            
            # Basic image statistics
            features['width'], features['height'] = image_data.shape[:2]
            features['aspect_ratio'] = features['width'] / features['height']
            features['mean_brightness'] = float(np.mean(gray))
            features['brightness_std'] = float(np.std(gray))
            
            # Color features (if color image)
            if len(image_data.shape) == 3:
                for i, channel in enumerate(['red', 'green', 'blue']):
                    features[f'{channel}_mean'] = float(np.mean(image_data[:, :, i]))
                    features[f'{channel}_std'] = float(np.std(image_data[:, :, i]))
            
            # Texture features
            # Sobel edge detection
            sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            features['edge_density'] = float(np.mean(np.sqrt(sobel_x**2 + sobel_y**2)))
            
            # Laplacian variance (focus measure)
            features['focus_measure'] = float(cv2.Laplacian(gray, cv2.CV_64F).var())
            
            # Histogram features
            hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
            features['histogram_entropy'] = float(-np.sum(hist * np.log(hist + 1e-10)))
            
            # Contrast and homogeneity
            features['contrast'] = float(np.std(gray))
            
        except Exception as e:
            logger.warning(f"⚠️ Image feature extraction error: {str(e)}")
        
        return features

class TextFeatureExtractor:
    """Specialized text feature extraction for bloggers"""
    
    def __init__(self):
        try:
            self.tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')
            self.model = AutoModel.from_pretrained('bert-base-uncased')
        except:
            logger.warning("⚠️ BERT model not available, using basic text features")
            self.tokenizer = None
            self.model = None
    
    def extract_text_features(self, text: str) -> Dict[str, float]:
        """Extract comprehensive text features"""
        features = {}
        
        try:
            # Basic text statistics
            features['text_length'] = len(text)
            features['word_count'] = len(text.split())
            features['sentence_count'] = text.count('.') + text.count('!') + text.count('?')
            features['avg_word_length'] = np.mean([len(word) for word in text.split()])
            
            # Advanced linguistic features
            features['exclamation_count'] = text.count('!')
            features['question_count'] = text.count('?')
            features['uppercase_ratio'] = sum(1 for c in text if c.isupper()) / len(text)
            features['digit_ratio'] = sum(1 for c in text if c.isdigit()) / len(text)
            
            # Readability approximation (simplified)
            avg_sentence_length = features['word_count'] / max(1, features['sentence_count'])
            features['avg_sentence_length'] = avg_sentence_length
            
            # Semantic features using BERT (if available)
            if self.tokenizer and self.model:
                try:
                    inputs = self.tokenizer(text[:512], return_tensors="pt", truncation=True, padding=True)
                    with torch.no_grad():
                        outputs = self.model(**inputs)
                        embeddings = outputs.last_hidden_state.mean(dim=1).squeeze()
                    
                    # Use first 10 dimensions of BERT embeddings as features
                    for i in range(min(10, embeddings.shape[0])):
                        features[f'bert_dim_{i}'] = float(embeddings[i])
                except Exception as e:
                    logger.warning(f"⚠️ BERT feature extraction failed: {str(e)}")
            
        except Exception as e:
            logger.warning(f"⚠️ Text feature extraction error: {str(e)}")
        
        return features

class AutomatedFeatureEngineeringEngine:
    """
    🔧 Automated Feature Engineering Engine
    
    Advanced feature discovery, synthesis, and optimization for creator-specific
    AI models with multimodal data fusion and intelligent feature selection.
    """
    
    def __init__(self, config: FeatureEngineeringConfig):
        self.config = config
        self.feature_metadata: Dict[str, FeatureMetadata] = {}
        self.generated_features: pd.DataFrame = pd.DataFrame()
        self.feature_transformers: Dict[str, Any] = {}
        self.executor = ThreadPoolExecutor(max_workers=config.parallel_workers)
        
        # Initialize specialized extractors
        self.audio_extractor = AudioFeatureExtractor()
        self.image_extractor = ImageFeatureExtractor()
        self.text_extractor = TextFeatureExtractor()
        
        # Feature generation statistics
        self.stats = {
            'total_features_generated': 0,
            'features_selected': 0,
            'computation_time_seconds': 0.0,
            'feature_types_distribution': {},
            'transformation_types_distribution': {}
        }
        
        logger.info(f"🔧 Automated Feature Engineering Engine initialized for {config.creator_type.value}")
    
    async def engineer_features(
        self,
        data: Dict[str, Any],
        target: Optional[np.ndarray] = None,
        validation_data: Optional[Dict[str, Any]] = None
    ) -> Tuple[pd.DataFrame, Dict[str, FeatureMetadata]]:
        """
        Main feature engineering pipeline
        
        Args:
            data: Input data dictionary with different modalities
            target: Target variable for supervised feature selection
            validation_data: Validation data for stability testing
            
        Returns:
            Tuple of (engineered_features_df, feature_metadata_dict)
        """
        start_time = time.time()
        logger.info(f"🚀 Starting automated feature engineering for {self.config.creator_type.value}")
        
        try:
            # Step 1: Extract base features from multimodal data
            base_features = await self._extract_multimodal_features(data)
            logger.info(f"📊 Extracted {len(base_features.columns)} base features")
            
            # Step 2: Generate synthetic features
            synthetic_features = await self._generate_synthetic_features(base_features, target)
            logger.info(f"🧬 Generated {len(synthetic_features.columns)} synthetic features")
            
            # Step 3: Combine all features
            all_features = pd.concat([base_features, synthetic_features], axis=1)
            
            # Step 4: Feature selection and ranking
            selected_features, feature_scores = await self._select_optimal_features(
                all_features, target
            )
            logger.info(f"🎯 Selected {len(selected_features.columns)} optimal features")
            
            # Step 5: Feature stability validation (if validation data provided)
            if validation_data:
                stability_scores = await self._validate_feature_stability(
                    selected_features, validation_data
                )
                await self._update_stability_scores(stability_scores)
            
            # Step 6: Update metadata and statistics
            await self._finalize_feature_metadata(selected_features, feature_scores)
            
            self.generated_features = selected_features
            computation_time = time.time() - start_time
            self.stats['computation_time_seconds'] = computation_time
            
            logger.info(f"✅ Feature engineering completed in {computation_time:.2f}s")
            logger.info(f"📈 Final feature set: {len(selected_features.columns)} features")
            
            return selected_features, self.feature_metadata
            
        except Exception as e:
            logger.error(f"❌ Feature engineering failed: {str(e)}")
            raise
    
    async def _extract_multimodal_features(self, data: Dict[str, Any]) -> pd.DataFrame:
        """Extract features from multimodal data"""
        all_features = {}
        
        # Process each data modality
        for data_type, data_content in data.items():
            try:
                if data_type == 'audio' and isinstance(data_content, np.ndarray):
                    audio_features = self.audio_extractor.extract_audio_features(data_content)
                    all_features.update({f"audio_{k}": v for k, v in audio_features.items()})
                
                elif data_type == 'image' and isinstance(data_content, np.ndarray):
                    image_features = self.image_extractor.extract_image_features(data_content)
                    all_features.update({f"image_{k}": v for k, v in image_features.items()})
                
                elif data_type == 'text' and isinstance(data_content, str):
                    text_features = self.text_extractor.extract_text_features(data_content)
                    all_features.update({f"text_{k}": v for k, v in text_features.items()})
                
                elif data_type == 'behavioral' and isinstance(data_content, dict):
                    behavioral_features = await self._extract_behavioral_features(data_content)
                    all_features.update({f"behavioral_{k}": v for k, v in behavioral_features.items()})
                
                elif data_type == 'numerical' and isinstance(data_content, (dict, pd.DataFrame)):
                    if isinstance(data_content, dict):
                        all_features.update({f"numerical_{k}": v for k, v in data_content.items()})
                    else:
                        for col in data_content.columns:
                            all_features[f"numerical_{col}"] = data_content[col].values[0] if len(data_content) > 0 else 0
                
            except Exception as e:
                logger.warning(f"⚠️ Failed to extract {data_type} features: {str(e)}")
        
        # Create metadata for base features
        for feature_name in all_features.keys():
            self.feature_metadata[feature_name] = FeatureMetadata(
                name=feature_name,
                feature_type=self._infer_feature_type(feature_name),
                transformation=TransformationType.ENCODING,
                source_features=[],
                interpretability_score=1.0
            )
        
        return pd.DataFrame([all_features])
    
    async def _extract_behavioral_features(self, behavioral_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract behavioral features specific to creator types"""
        features = {}
        
        try:
            # Common behavioral features
            features['engagement_rate'] = behavioral_data.get('likes', 0) / max(1, behavioral_data.get('views', 1))
            features['share_rate'] = behavioral_data.get('shares', 0) / max(1, behavioral_data.get('views', 1))
            features['comment_rate'] = behavioral_data.get('comments', 0) / max(1, behavioral_data.get('views', 1))
            
            # Creator-specific behavioral features
            if self.config.creator_type == CreatorType.MUSICIAN:
                features['average_listen_duration'] = behavioral_data.get('avg_listen_duration', 0)
                features['playlist_additions'] = behavioral_data.get('playlist_additions', 0)
                features['repeat_listen_rate'] = behavioral_data.get('repeat_listens', 0) / max(1, behavioral_data.get('unique_listeners', 1))
            
            elif self.config.creator_type == CreatorType.BLOGGER:
                features['average_read_time'] = behavioral_data.get('avg_read_time', 0)
                features['bounce_rate'] = behavioral_data.get('bounces', 0) / max(1, behavioral_data.get('page_views', 1))
                features['social_shares'] = behavioral_data.get('social_shares', 0)
            
            elif self.config.creator_type == CreatorType.PHOTOGRAPHER:
                features['download_rate'] = behavioral_data.get('downloads', 0) / max(1, behavioral_data.get('views', 1))
                features['save_rate'] = behavioral_data.get('saves', 0) / max(1, behavioral_data.get('views', 1))
                features['commercial_interest'] = behavioral_data.get('commercial_inquiries', 0)
            
            # Time-based features
            features['creation_hour'] = behavioral_data.get('creation_hour', 0)
            features['creation_day_of_week'] = behavioral_data.get('creation_day_of_week', 0)
            features['time_since_last_post'] = behavioral_data.get('time_since_last_post', 0)
            
        except Exception as e:
            logger.warning(f"⚠️ Behavioral feature extraction error: {str(e)}")
        
        return features
    
    async def _generate_synthetic_features(
        self, 
        base_features: pd.DataFrame, 
        target: Optional[np.ndarray] = None
    ) -> pd.DataFrame:
        """Generate synthetic features through transformations and interactions"""
        synthetic_features = pd.DataFrame(index=base_features.index)
        
        # Get numerical columns for transformation
        numerical_cols = base_features.select_dtypes(include=[np.number]).columns.tolist()
        
        if not numerical_cols:
            logger.warning("⚠️ No numerical columns found for synthetic feature generation")
            return synthetic_features
        
        # 1. Polynomial features
        if self.config.max_polynomial_degree > 1:
            poly_features = await self._generate_polynomial_features(
                base_features[numerical_cols]
            )
            synthetic_features = pd.concat([synthetic_features, poly_features], axis=1)
        
        # 2. Mathematical transformations
        math_features = await self._generate_mathematical_transformations(
            base_features[numerical_cols]
        )
        synthetic_features = pd.concat([synthetic_features, math_features], axis=1)
        
        # 3. Interaction features
        if self.config.enable_interactions:
            interaction_features = await self._generate_interaction_features(
                base_features[numerical_cols]
            )
            synthetic_features = pd.concat([synthetic_features, interaction_features], axis=1)
        
        # 4. Aggregation features
        if self.config.enable_aggregations:
            agg_features = await self._generate_aggregation_features(
                base_features[numerical_cols]
            )
            synthetic_features = pd.concat([synthetic_features, agg_features], axis=1)
        
        # 5. Dimensionality reduction features
        if self.config.enable_dimensionality_reduction and len(numerical_cols) > 5:
            dim_red_features = await self._generate_dimensionality_reduction_features(
                base_features[numerical_cols]
            )
            synthetic_features = pd.concat([synthetic_features, dim_red_features], axis=1)
        
        # Remove any infinite or NaN values
        synthetic_features = synthetic_features.replace([np.inf, -np.inf], np.nan)
        synthetic_features = synthetic_features.fillna(0)
        
        return synthetic_features
    
    async def _generate_polynomial_features(self, features: pd.DataFrame) -> pd.DataFrame:
        """Generate polynomial features"""
        poly_features = pd.DataFrame(index=features.index)
        
        try:
            from sklearn.preprocessing import PolynomialFeatures
            
            # Limit to prevent explosion of features
            max_cols = min(10, len(features.columns))
            selected_cols = features.columns[:max_cols]
            
            poly = PolynomialFeatures(
                degree=min(self.config.max_polynomial_degree, 2),
                include_bias=False,
                interaction_only=False
            )
            
            poly_array = poly.fit_transform(features[selected_cols])
            poly_names = poly.get_feature_names_out(selected_cols)
            
            # Create new features (excluding original features)
            for i, name in enumerate(poly_names):
                if name not in selected_cols:
                    feature_name = f"poly_{name}"
                    poly_features[feature_name] = poly_array[:, i]
                    
                    # Create metadata
                    self.feature_metadata[feature_name] = FeatureMetadata(
                        name=feature_name,
                        feature_type=FeatureType.SYNTHETIC,
                        transformation=TransformationType.POLYNOMIAL,
                        source_features=selected_cols.tolist(),
                        interpretability_score=0.7
                    )
            
        except Exception as e:
            logger.warning(f"⚠️ Polynomial feature generation failed: {str(e)}")
        
        return poly_features
    
    async def _generate_mathematical_transformations(self, features: pd.DataFrame) -> pd.DataFrame:
        """Generate mathematical transformation features"""
        math_features = pd.DataFrame(index=features.index)
        
        for col in features.columns:
            try:
                values = features[col].values
                
                # Skip if all values are zero or negative for log transform
                if np.all(values <= 0):
                    continue
                
                # Logarithmic transformation
                if np.all(values > 0):
                    log_name = f"log_{col}"
                    math_features[log_name] = np.log1p(values)
                    
                    self.feature_metadata[log_name] = FeatureMetadata(
                        name=log_name,
                        feature_type=FeatureType.SYNTHETIC,
                        transformation=TransformationType.LOGARITHMIC,
                        source_features=[col],
                        interpretability_score=0.8
                    )
                
                # Square root transformation
                if np.all(values >= 0):
                    sqrt_name = f"sqrt_{col}"
                    math_features[sqrt_name] = np.sqrt(values)
                    
                    self.feature_metadata[sqrt_name] = FeatureMetadata(
                        name=sqrt_name,
                        feature_type=FeatureType.SYNTHETIC,
                        transformation=TransformationType.EXPONENTIAL,
                        source_features=[col],
                        interpretability_score=0.8
                    )
                
                # Trigonometric transformations
                sin_name = f"sin_{col}"
                cos_name = f"cos_{col}"
                math_features[sin_name] = np.sin(values)
                math_features[cos_name] = np.cos(values)
                
                for trig_name, trig_type in [(sin_name, TransformationType.TRIGONOMETRIC), 
                                           (cos_name, TransformationType.TRIGONOMETRIC)]:
                    self.feature_metadata[trig_name] = FeatureMetadata(
                        name=trig_name,
                        feature_type=FeatureType.SYNTHETIC,
                        transformation=trig_type,
                        source_features=[col],
                        interpretability_score=0.6
                    )
                
            except Exception as e:
                logger.warning(f"⚠️ Math transformation failed for {col}: {str(e)}")
        
        return math_features
    
    async def _generate_interaction_features(self, features: pd.DataFrame) -> pd.DataFrame:
        """Generate interaction features between pairs of features"""
        interaction_features = pd.DataFrame(index=features.index)
        
        # Limit combinations to prevent explosion
        max_combinations = min(50, len(features.columns) * (len(features.columns) - 1) // 2)
        feature_pairs = list(itertools.combinations(features.columns, 2))[:max_combinations]
        
        for col1, col2 in feature_pairs:
            try:
                # Multiplication interaction
                mult_name = f"interact_{col1}_x_{col2}"
                interaction_features[mult_name] = features[col1] * features[col2]
                
                # Division interaction (with safe division)
                div_name = f"interact_{col1}_div_{col2}"
                interaction_features[div_name] = features[col1] / (features[col2] + 1e-8)
                
                # Create metadata
                for name, values in [(mult_name, interaction_features[mult_name]), 
                                   (div_name, interaction_features[div_name])]:
                    self.feature_metadata[name] = FeatureMetadata(
                        name=name,
                        feature_type=FeatureType.SYNTHETIC,
                        transformation=TransformationType.INTERACTION,
                        source_features=[col1, col2],
                        interpretability_score=0.5
                    )
                
            except Exception as e:
                logger.warning(f"⚠️ Interaction feature generation failed for {col1} x {col2}: {str(e)}")
        
        return interaction_features
    
    async def _generate_aggregation_features(self, features: pd.DataFrame) -> pd.DataFrame:
        """Generate aggregation features"""
        agg_features = pd.DataFrame(index=features.index)
        
        try:
            # Statistical aggregations across all features
            agg_features['mean_all'] = features.mean(axis=1)
            agg_features['std_all'] = features.std(axis=1)
            agg_features['max_all'] = features.max(axis=1)
            agg_features['min_all'] = features.min(axis=1)
            agg_features['range_all'] = agg_features['max_all'] - agg_features['min_all']
            agg_features['skew_all'] = features.skew(axis=1)
            
            # Count-based features
            agg_features['positive_count'] = (features > 0).sum(axis=1)
            agg_features['negative_count'] = (features < 0).sum(axis=1)
            agg_features['zero_count'] = (features == 0).sum(axis=1)
            
            # Create metadata for aggregation features
            for col in agg_features.columns:
                self.feature_metadata[col] = FeatureMetadata(
                    name=col,
                    feature_type=FeatureType.SYNTHETIC,
                    transformation=TransformationType.AGGREGATION,
                    source_features=features.columns.tolist(),
                    interpretability_score=0.9
                )
            
        except Exception as e:
            logger.warning(f"⚠️ Aggregation feature generation failed: {str(e)}")
        
        return agg_features
    
    async def _generate_dimensionality_reduction_features(self, features: pd.DataFrame) -> pd.DataFrame:
        """Generate dimensionality reduction features"""
        dim_red_features = pd.DataFrame(index=features.index)
        
        try:
            # Standardize features first
            scaler = StandardScaler()
            scaled_features = scaler.fit_transform(features)
            
            # PCA features
            n_components = min(5, len(features.columns))
            pca = PCA(n_components=n_components)
            pca_features = pca.fit_transform(scaled_features)
            
            for i in range(n_components):
                col_name = f"pca_component_{i}"
                dim_red_features[col_name] = pca_features[:, i]
                
                self.feature_metadata[col_name] = FeatureMetadata(
                    name=col_name,
                    feature_type=FeatureType.SYNTHETIC,
                    transformation=TransformationType.AGGREGATION,
                    source_features=features.columns.tolist(),
                    interpretability_score=0.3
                )
            
            # ICA features
            if len(features.columns) >= 3:
                ica_components = min(3, len(features.columns))
                ica = FastICA(n_components=ica_components, random_state=42)
                ica_features = ica.fit_transform(scaled_features)
                
                for i in range(ica_components):
                    col_name = f"ica_component_{i}"
                    dim_red_features[col_name] = ica_features[:, i]
                    
                    self.feature_metadata[col_name] = FeatureMetadata(
                        name=col_name,
                        feature_type=FeatureType.SYNTHETIC,
                        transformation=TransformationType.AGGREGATION,
                        source_features=features.columns.tolist(),
                        interpretability_score=0.2
                    )
            
        except Exception as e:
            logger.warning(f"⚠️ Dimensionality reduction failed: {str(e)}")
        
        return dim_red_features
    
    async def _select_optimal_features(
        self, 
        features: pd.DataFrame, 
        target: Optional[np.ndarray] = None
    ) -> Tuple[pd.DataFrame, Dict[str, float]]:
        """Select optimal features using multiple criteria"""
        feature_scores = {}
        
        # If no target provided, use unsupervised feature selection
        if target is None:
            logger.info("🎯 Using unsupervised feature selection")
            selected_features, scores = await self._unsupervised_feature_selection(features)
        else:
            logger.info("🎯 Using supervised feature selection")
            selected_features, scores = await self._supervised_feature_selection(features, target)
        
        feature_scores.update(scores)
        
        # Apply additional filtering criteria
        final_features = await self._apply_feature_filters(selected_features, feature_scores)
        
        return final_features, feature_scores
    
    async def _supervised_feature_selection(
        self, 
        features: pd.DataFrame, 
        target: np.ndarray
    ) -> Tuple[pd.DataFrame, Dict[str, float]]:
        """Supervised feature selection using target variable"""
        feature_scores = {}
        
        try:
            # Correlation with target
            for col in features.columns:
                corr = np.corrcoef(features[col].values, target)[0, 1]
                feature_scores[col] = abs(corr) if not np.isnan(corr) else 0.0
            
            # Mutual information
            try:
                mi_scores = mutual_info_classif(features, target, random_state=42)
                for i, col in enumerate(features.columns):
                    feature_scores[f"{col}_mi"] = mi_scores[i]
                    # Combine correlation and MI scores
                    feature_scores[col] = (feature_scores[col] + mi_scores[i]) / 2
            except Exception as e:
                logger.warning(f"⚠️ Mutual information calculation failed: {str(e)}")
            
            # Select top features
            sorted_features = sorted(
                feature_scores.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            # Select top features up to max_features limit
            selected_count = min(self.config.max_features, len(sorted_features))
            selected_feature_names = [name for name, score in sorted_features[:selected_count]
                                    if score >= self.config.target_correlation_threshold]
            
            selected_features = features[selected_feature_names]
            
        except Exception as e:
            logger.error(f"❌ Supervised feature selection failed: {str(e)}")
            # Fallback to all features
            selected_features = features
            feature_scores = {col: 0.5 for col in features.columns}
        
        return selected_features, feature_scores
    
    async def _unsupervised_feature_selection(
        self, 
        features: pd.DataFrame
    ) -> Tuple[pd.DataFrame, Dict[str, float]]:
        """Unsupervised feature selection based on variance and correlation"""
        feature_scores = {}
        
        try:
            # Variance-based scoring
            for col in features.columns:
                variance = features[col].var()
                feature_scores[col] = variance if not np.isnan(variance) else 0.0
            
            # Remove highly correlated features
            correlation_matrix = features.corr().abs()
            upper_triangle = correlation_matrix.where(
                np.triu(np.ones(correlation_matrix.shape), k=1).astype(bool)
            )
            
            # Find features with correlation > 0.95
            high_corr_features = [column for column in upper_triangle.columns 
                                if any(upper_triangle[column] > 0.95)]
            
            # Remove high correlation features with lower variance
            for feature in high_corr_features:
                if feature in feature_scores:
                    feature_scores[feature] *= 0.5  # Penalize highly correlated features
            
            # Select features based on variance threshold
            variance_threshold = np.percentile(list(feature_scores.values()), 25)
            selected_feature_names = [name for name, score in feature_scores.items()
                                    if score >= variance_threshold]
            
            # Limit to max_features
            if len(selected_feature_names) > self.config.max_features:
                sorted_features = sorted(
                    feature_scores.items(),
                    key=lambda x: x[1],
                    reverse=True
                )
                selected_feature_names = [name for name, score in sorted_features[:self.config.max_features]]
            
            selected_features = features[selected_feature_names]
            
        except Exception as e:
            logger.error(f"❌ Unsupervised feature selection failed: {str(e)}")
            # Fallback to all features
            selected_features = features
            feature_scores = {col: 0.5 for col in features.columns}
        
        return selected_features, feature_scores
    
    async def _apply_feature_filters(
        self, 
        features: pd.DataFrame, 
        feature_scores: Dict[str, float]
    ) -> pd.DataFrame:
        """Apply additional feature filtering criteria"""
        filtered_columns = []
        
        for col in features.columns:
            # Check feature importance threshold
            if feature_scores.get(col, 0) < self.config.feature_importance_threshold:
                continue
            
            # Check for infinite or NaN values
            if features[col].isna().any() or np.isinf(features[col]).any():
                continue
            
            # Check for constant features
            if features[col].nunique() <= 1:
                continue
            
            filtered_columns.append(col)
        
        return features[filtered_columns]
    
    async def _validate_feature_stability(
        self, 
        features: pd.DataFrame, 
        validation_data: Dict[str, Any]
    ) -> Dict[str, float]:
        """Validate feature stability on validation data"""
        stability_scores = {}
        
        try:
            # Extract features from validation data
            val_features = await self._extract_multimodal_features(validation_data)
            
            # Compare feature distributions
            for col in features.columns:
                if col in val_features.columns:
                    # Simple stability measure: correlation between train and val distributions
                    train_vals = features[col].values
                    val_vals = val_features[col].values
                    
                    # Ensure same length for comparison
                    min_len = min(len(train_vals), len(val_vals))
                    if min_len > 0:
                        correlation = np.corrcoef(
                            train_vals[:min_len], 
                            val_vals[:min_len]
                        )[0, 1]
                        stability_scores[col] = abs(correlation) if not np.isnan(correlation) else 0.0
                    else:
                        stability_scores[col] = 0.0
                else:
                    stability_scores[col] = 0.0  # Feature not found in validation
            
        except Exception as e:
            logger.warning(f"⚠️ Feature stability validation failed: {str(e)}")
            stability_scores = {col: 0.5 for col in features.columns}
        
        return stability_scores
    
    async def _update_stability_scores(self, stability_scores: Dict[str, float]):
        """Update feature metadata with stability scores"""
        for feature_name, stability in stability_scores.items():
            if feature_name in self.feature_metadata:
                self.feature_metadata[feature_name].stability_score = stability
    
    async def _finalize_feature_metadata(
        self, 
        features: pd.DataFrame, 
        feature_scores: Dict[str, float]
    ):
        """Finalize feature metadata with scores and statistics"""
        for col in features.columns:
            if col in self.feature_metadata:
                self.feature_metadata[col].importance_score = feature_scores.get(col, 0.0)
                
                # Update statistics
                feature_type = self.feature_metadata[col].feature_type
                transformation_type = self.feature_metadata[col].transformation
                
                self.stats['feature_types_distribution'][feature_type.value] = \
                    self.stats['feature_types_distribution'].get(feature_type.value, 0) + 1
                
                self.stats['transformation_types_distribution'][transformation_type.value] = \
                    self.stats['transformation_types_distribution'].get(transformation_type.value, 0) + 1
        
        self.stats['total_features_generated'] = len(self.feature_metadata)
        self.stats['features_selected'] = len(features.columns)
    
    def _infer_feature_type(self, feature_name: str) -> FeatureType:
        """Infer feature type from feature name"""
        if 'audio' in feature_name:
            return FeatureType.AUDIO
        elif 'image' in feature_name:
            return FeatureType.IMAGE
        elif 'text' in feature_name:
            return FeatureType.TEXT
        elif 'behavioral' in feature_name:
            return FeatureType.BEHAVIORAL
        elif any(prefix in feature_name for prefix in ['poly_', 'log_', 'sqrt_', 'sin_', 'cos_', 'interact_']):
            return FeatureType.SYNTHETIC
        else:
            return FeatureType.NUMERICAL
    
    def export_feature_engineering_report(self, output_path: str) -> Dict[str, Any]:
        """Export comprehensive feature engineering report"""
        report = {
            "feature_engineering_summary": {
                "config": {
                    "creator_type": self.config.creator_type.value,
                    "max_features": self.config.max_features,
                    "enable_interactions": self.config.enable_interactions,
                    "enable_aggregations": self.config.enable_aggregations,
                    "target_correlation_threshold": self.config.target_correlation_threshold
                },
                "statistics": self.stats,
                "performance": {
                    "features_generated": self.stats['total_features_generated'],
                    "features_selected": self.stats['features_selected'],
                    "selection_rate": self.stats['features_selected'] / max(1, self.stats['total_features_generated']),
                    "computation_time_seconds": self.stats['computation_time_seconds']
                }
            },
            "feature_metadata": {
                name: metadata.to_dict() 
                for name, metadata in self.feature_metadata.items()
            },
            "feature_rankings": sorted(
                [
                    {
                        "name": name,
                        "importance_score": metadata.importance_score,
                        "stability_score": metadata.stability_score,
                        "interpretability_score": metadata.interpretability_score,
                        "feature_type": metadata.feature_type.value,
                        "transformation": metadata.transformation.value
                    }
                    for name, metadata in self.feature_metadata.items()
                ],
                key=lambda x: x['importance_score'],
                reverse=True
            )
        }
        
        # Save to file
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"💾 Feature engineering report exported to {output_path}")
        return report
    
    def get_feature_engineering_summary(self) -> Dict[str, Any]:
        """Get summary of feature engineering results"""
        return {
            "automated_feature_engineering": "v1.0",
            "creator_type": self.config.creator_type.value,
            "results": {
                "total_features_generated": self.stats['total_features_generated'],
                "features_selected": self.stats['features_selected'],
                "computation_time_seconds": self.stats['computation_time_seconds'],
                "feature_types": self.stats['feature_types_distribution'],
                "transformation_types": self.stats['transformation_types_distribution']
            },
            "top_features": [
                {
                    "name": name,
                    "importance": metadata.importance_score,
                    "type": metadata.feature_type.value,
                    "stability": metadata.stability_score
                }
                for name, metadata in sorted(
                    self.feature_metadata.items(),
                    key=lambda x: x[1].importance_score,
                    reverse=True
                )[:10]
            ]
        }

# Factory for creating specialized feature engineering configurations
class FeatureEngineeringFactory:
    """Factory for creating specialized feature engineering configurations"""
    
    @staticmethod
    def create_musician_engineer() -> AutomatedFeatureEngineeringEngine:
        """Create feature engineer optimized for musicians"""
        config = FeatureEngineeringConfig(
            creator_type=CreatorType.MUSICIAN,
            max_features=500,
            enable_interactions=True,
            enable_aggregations=True,
            target_correlation_threshold=0.15,
            enable_multimodal_fusion=True
        )
        return AutomatedFeatureEngineeringEngine(config)
    
    @staticmethod
    def create_blogger_engineer() -> AutomatedFeatureEngineeringEngine:
        """Create feature engineer optimized for bloggers"""
        config = FeatureEngineeringConfig(
            creator_type=CreatorType.BLOGGER,
            max_features=800,
            enable_interactions=True,
            enable_aggregations=True,
            target_correlation_threshold=0.1,
            enable_multimodal_fusion=True
        )
        return AutomatedFeatureEngineeringEngine(config)
    
    @staticmethod
    def create_photographer_engineer() -> AutomatedFeatureEngineeringEngine:
        """Create feature engineer optimized for photographers"""
        config = FeatureEngineeringConfig(
            creator_type=CreatorType.PHOTOGRAPHER,
            max_features=600,
            enable_interactions=True,
            enable_aggregations=True,
            target_correlation_threshold=0.12,
            enable_multimodal_fusion=True
        )
        return AutomatedFeatureEngineeringEngine(config)

async def main():
    """Example usage of Automated Feature Engineering Engine"""
    # Create musician-specific feature engineer
    engineer = FeatureEngineeringFactory.create_musician_engineer()
    
    # Mock data for demonstration
    data = {
        'audio': np.random.rand(22050),  # 1 second of audio at 22kHz
        'text': "This is a sample song description with emotional lyrics",
        'behavioral': {
            'likes': 150,
            'views': 1000,
            'shares': 25,
            'avg_listen_duration': 180,
            'playlist_additions': 5
        },
        'numerical': {
            'duration_seconds': 240,
            'tempo': 120,
            'key': 5
        }
    }
    
    # Create mock target for supervised learning
    target = np.random.rand(1)  # Engagement score
    
    # Engineer features
    engineered_features, metadata = await engineer.engineer_features(
        data=data,
        target=target
    )
    
    print(f"🔧 Generated {len(engineered_features.columns)} features")
    print(f"📊 Feature types: {engineer.stats['feature_types_distribution']}")
    
    # Export report
    report = engineer.export_feature_engineering_report(
        "/tmp/feature_engineering_report_musician.json"
    )
    
    # Print summary
    summary = engineer.get_feature_engineering_summary()
    print(f"📈 Summary: {json.dumps(summary, indent=2)}")

if __name__ == "__main__":
    asyncio.run(main())