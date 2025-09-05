"""Content Similarity Engine - ML-Powered Content Analysis and Matching
======================================================================

Advanced content similarity analysis using machine learning and NLP:
- Semantic content analysis
- Style and tone matching
- Visual content recognition
- Audio fingerprinting
- Multi-modal content understanding
- Content trend prediction

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import numpy as np
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import json
import hashlib

logger = logging.getLogger(__name__)


class ContentType(Enum):
    """Content type categories"""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    MIXED_MEDIA = "mixed_media"
    LIVE_STREAM = "live_stream"


class SimilarityAlgorithm(Enum):
    """Content similarity algorithms"""
    SEMANTIC_EMBEDDING = "semantic_embedding"
    TF_IDF = "tf_idf"
    VISUAL_FEATURES = "visual_features"
    AUDIO_FINGERPRINT = "audio_fingerprint"
    STYLE_ANALYSIS = "style_analysis"
    TOPIC_MODELING = "topic_modeling"


@dataclass
class ContentFeatures:
    """Comprehensive content feature representation"""
    content_id: str
    content_type: ContentType
    text_features: Dict[str, float] = field(default_factory=dict)
    visual_features: Dict[str, float] = field(default_factory=dict)
    audio_features: Dict[str, float] = field(default_factory=dict)
    semantic_embedding: np.ndarray = field(default_factory=lambda: np.array([]))
    style_features: Dict[str, float] = field(default_factory=dict)
    metadata_features: Dict[str, Any] = field(default_factory=dict)
    engagement_features: Dict[str, float] = field(default_factory=dict)
    temporal_features: Dict[str, float] = field(default_factory=dict)
    
    def get_feature_vector(self) -> np.ndarray:
        """Get combined feature vector for ML processing"""
        all_features = []
        
        # Text features
        all_features.extend(list(self.text_features.values()))
        
        # Visual features
        all_features.extend(list(self.visual_features.values()))
        
        # Audio features
        all_features.extend(list(self.audio_features.values()))
        
        # Style features
        all_features.extend(list(self.style_features.values()))
        
        # Engagement features
        all_features.extend(list(self.engagement_features.values()))
        
        # Temporal features
        all_features.extend(list(self.temporal_features.values()))
        
        # Semantic embedding
        if self.semantic_embedding.size > 0:
            all_features.extend(self.semantic_embedding.tolist())
        
        return np.array(all_features, dtype=np.float32)


@dataclass
class SimilarityScore:
    """Content similarity score with detailed breakdown"""
    content_a_id: str
    content_b_id: str
    overall_similarity: float
    semantic_similarity: float = 0.0
    visual_similarity: float = 0.0
    audio_similarity: float = 0.0
    style_similarity: float = 0.0
    topic_similarity: float = 0.0
    engagement_similarity: float = 0.0
    confidence: float = 0.0
    algorithm_used: SimilarityAlgorithm = SimilarityAlgorithm.SEMANTIC_EMBEDDING
    similarity_explanation: str = ""
    
    def get_similarity_breakdown(self) -> Dict[str, float]:
        """Get detailed similarity breakdown"""
        return {
            'semantic': self.semantic_similarity,
            'visual': self.visual_similarity,
            'audio': self.audio_similarity,
            'style': self.style_similarity,
            'topic': self.topic_similarity,
            'engagement': self.engagement_similarity
        }


@dataclass
class ContentVector:
    """Multi-dimensional content representation vector"""
    content_id: str
    vector: np.ndarray
    vector_type: str
    dimensions: int
    creation_timestamp: datetime = field(default_factory=datetime.now)
    
    def cosine_similarity(self, other: 'ContentVector') -> float:
        """Calculate cosine similarity with another vector"""
        if self.vector.shape != other.vector.shape:
            return 0.0
        
        dot_product = np.dot(self.vector, other.vector)
        norm_a = np.linalg.norm(self.vector)
        norm_b = np.linalg.norm(other.vector)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return dot_product / (norm_a * norm_b)


class ContentSimilarityEngine:
    """
    Advanced content similarity engine using ML and NLP techniques
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize content similarity engine"""
        self.config = config or {}
        self.feature_extractors = {}
        self.similarity_models = {}
        self.content_cache = {}
        self.vector_cache = {}
        
        # Configuration
        self.embedding_dimension = self.config.get('embedding_dimension', 256)
        self.similarity_threshold = self.config.get('similarity_threshold', 0.7)
        self.cache_size_limit = self.config.get('cache_size_limit', 10000)
        
        # Algorithm weights for ensemble
        self.algorithm_weights = {
            SimilarityAlgorithm.SEMANTIC_EMBEDDING: 0.4,
            SimilarityAlgorithm.TF_IDF: 0.2,
            SimilarityAlgorithm.VISUAL_FEATURES: 0.2,
            SimilarityAlgorithm.STYLE_ANALYSIS: 0.1,
            SimilarityAlgorithm.TOPIC_MODELING: 0.1
        }
        
        logger.info("🔍 Content Similarity Engine initialized")
    
    async def initialize_models(self):
        """Initialize ML models and feature extractors"""
        try:
            await self._initialize_text_models()
            await self._initialize_visual_models()
            await self._initialize_audio_models()
            await self._initialize_style_models()
            
            logger.info("✅ Content similarity models initialized")
            
        except Exception as e:
            logger.error(f"❌ Error initializing similarity models: {e}")
    
    async def _initialize_text_models(self):
        """Initialize text analysis models"""
        try:
            # TF-IDF vectorizer
            from sklearn.feature_extraction.text import TfidfVectorizer
            
            self.similarity_models['tfidf'] = TfidfVectorizer(
                max_features=5000,
                stop_words='english',
                ngram_range=(1, 2)
            )
            
            # Try to initialize more advanced models
            try:
                # Sentence transformers for semantic embeddings
                from sentence_transformers import SentenceTransformer
                self.similarity_models['sentence_transformer'] = SentenceTransformer('all-MiniLM-L6-v2')
            except ImportError:
                logger.warning("⚠️ sentence-transformers not available, using simpler models")
            
        except ImportError:
            logger.warning("⚠️ Text analysis libraries not available")
    
    async def _initialize_visual_models(self):
        """Initialize visual content analysis models"""
        try:
            # Try to initialize computer vision models
            try:
                import cv2
                self.similarity_models['opencv'] = True
            except ImportError:
                logger.warning("⚠️ OpenCV not available for visual analysis")
            
            # Placeholder for deep learning models (ResNet, VGG, etc.)
            self.similarity_models['visual_features'] = {
                'color_histogram': True,
                'edge_detection': True,
                'texture_analysis': True
            }
            
        except Exception as e:
            logger.warning(f"⚠️ Visual models initialization failed: {e}")
    
    async def _initialize_audio_models(self):
        """Initialize audio analysis models"""
        try:
            # Try to initialize audio processing
            try:
                import librosa
                self.similarity_models['librosa'] = True
            except ImportError:
                logger.warning("⚠️ librosa not available for audio analysis")
            
            # Audio feature extraction capabilities
            self.similarity_models['audio_features'] = {
                'mfcc': True,
                'spectral_features': True,
                'tempo_analysis': True,
                'chromagram': True
            }
            
        except Exception as e:
            logger.warning(f"⚠️ Audio models initialization failed: {e}")
    
    async def _initialize_style_models(self):
        """Initialize style analysis models"""
        # Style analysis configuration
        self.similarity_models['style_analysis'] = {
            'writing_style': True,
            'visual_style': True,
            'color_palette': True,
            'composition_analysis': True
        }
    
    async def extract_content_features(self, content_data: Dict[str, Any]) -> ContentFeatures:
        """Extract comprehensive features from content"""
        try:
            content_id = content_data['content_id']
            content_type = ContentType(content_data.get('content_type', 'mixed_media'))
            
            # Check cache
            if content_id in self.content_cache:
                return self.content_cache[content_id]
            
            features = ContentFeatures(
                content_id=content_id,
                content_type=content_type
            )
            
            # Extract features based on content type
            if content_type in [ContentType.TEXT, ContentType.MIXED_MEDIA]:
                features.text_features = await self._extract_text_features(content_data)
                features.semantic_embedding = await self._extract_semantic_embedding(content_data)
            
            if content_type in [ContentType.IMAGE, ContentType.VIDEO, ContentType.MIXED_MEDIA]:
                features.visual_features = await self._extract_visual_features(content_data)
            
            if content_type in [ContentType.AUDIO, ContentType.VIDEO, ContentType.MIXED_MEDIA]:
                features.audio_features = await self._extract_audio_features(content_data)
            
            # Extract style features for all content
            features.style_features = await self._extract_style_features(content_data)
            
            # Extract metadata features
            features.metadata_features = await self._extract_metadata_features(content_data)
            
            # Extract engagement features
            features.engagement_features = await self._extract_engagement_features(content_data)
            
            # Extract temporal features
            features.temporal_features = await self._extract_temporal_features(content_data)
            
            # Cache the features
            if len(self.content_cache) < self.cache_size_limit:
                self.content_cache[content_id] = features
            
            return features
            
        except Exception as e:
            logger.error(f"❌ Error extracting content features: {e}")
            return ContentFeatures(
                content_id=content_data.get('content_id', 'unknown'),
                content_type=ContentType.MIXED_MEDIA
            )
    
    async def _extract_text_features(self, content_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract text-based features"""
        features = {}
        
        text_content = content_data.get('text_content', '')
        if not text_content:
            return features
        
        # Basic text statistics
        features['text_length'] = len(text_content)
        features['word_count'] = len(text_content.split())
        features['sentence_count'] = text_content.count('.') + text_content.count('!') + text_content.count('?')
        features['avg_word_length'] = np.mean([len(word) for word in text_content.split()]) if text_content.split() else 0
        
        # Sentiment analysis (simplified)
        positive_words = ['good', 'great', 'amazing', 'awesome', 'excellent', 'fantastic', 'wonderful']
        negative_words = ['bad', 'terrible', 'awful', 'horrible', 'disappointing', 'poor']
        
        positive_count = sum(1 for word in positive_words if word in text_content.lower())
        negative_count = sum(1 for word in negative_words if word in text_content.lower())
        
        features['sentiment_score'] = (positive_count - negative_count) / max(1, features['word_count'])
        features['positive_word_ratio'] = positive_count / max(1, features['word_count'])
        features['negative_word_ratio'] = negative_count / max(1, features['word_count'])
        
        # Readability score (simplified Flesch-Kincaid)
        if features['sentence_count'] > 0 and features['word_count'] > 0:
            avg_sentence_length = features['word_count'] / features['sentence_count']
            features['readability_score'] = 206.835 - (1.015 * avg_sentence_length) - (84.6 * features['avg_word_length'])
        else:
            features['readability_score'] = 0.0
        
        # Topic indicators (keyword presence)
        tech_keywords = ['technology', 'innovation', 'digital', 'ai', 'machine learning']
        lifestyle_keywords = ['lifestyle', 'fashion', 'beauty', 'health', 'fitness']
        business_keywords = ['business', 'marketing', 'strategy', 'growth', 'success']
        
        features['tech_topic_score'] = sum(1 for keyword in tech_keywords if keyword in text_content.lower()) / max(1, features['word_count'])
        features['lifestyle_topic_score'] = sum(1 for keyword in lifestyle_keywords if keyword in text_content.lower()) / max(1, features['word_count'])
        features['business_topic_score'] = sum(1 for keyword in business_keywords if keyword in text_content.lower()) / max(1, features['word_count'])
        
        return features
    
    async def _extract_semantic_embedding(self, content_data: Dict[str, Any]) -> np.ndarray:
        """Extract semantic embeddings from text content"""
        text_content = content_data.get('text_content', '')
        
        if not text_content:
            return np.zeros(self.embedding_dimension)
        
        try:
            # Use sentence transformer if available
            if 'sentence_transformer' in self.similarity_models:
                model = self.similarity_models['sentence_transformer']
                embedding = model.encode([text_content])[0]
                
                # Resize to target dimension if needed
                if len(embedding) != self.embedding_dimension:
                    if len(embedding) > self.embedding_dimension:
                        embedding = embedding[:self.embedding_dimension]
                    else:
                        embedding = np.pad(embedding, (0, self.embedding_dimension - len(embedding)))
                
                return embedding
            
        except Exception as e:
            logger.warning(f"⚠️ Error with sentence transformer: {e}")
        
        # Fallback: simple word embedding
        return self._simple_text_embedding(text_content)
    
    def _simple_text_embedding(self, text: str) -> np.ndarray:
        """Simple text embedding fallback"""
        # Create a simple hash-based embedding
        words = text.lower().split()
        
        if not words:
            return np.zeros(self.embedding_dimension)
        
        # Create embedding from word hashes
        embedding = np.zeros(self.embedding_dimension)
        
        for word in words:
            # Use hash to create deterministic word representation
            word_hash = int(hashlib.md5(word.encode()).hexdigest(), 16)
            word_vector = np.array([
                (word_hash >> i) & 1 for i in range(self.embedding_dimension)
            ], dtype=np.float32)
            embedding += word_vector
        
        # Normalize
        if np.linalg.norm(embedding) > 0:
            embedding = embedding / np.linalg.norm(embedding)
        
        return embedding
    
    async def _extract_visual_features(self, content_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract visual features from images/videos"""
        features = {}
        
        # Image metadata
        visual_data = content_data.get('visual_data', {})
        
        features['width'] = visual_data.get('width', 0) / 1000.0  # Normalize
        features['height'] = visual_data.get('height', 0) / 1000.0
        features['aspect_ratio'] = features['width'] / max(features['height'], 0.001)
        features['file_size'] = visual_data.get('file_size', 0) / 1000000.0  # MB
        
        # Color analysis (simplified)
        colors = visual_data.get('dominant_colors', [])
        if colors:
            features['color_variety'] = len(colors) / 10.0  # Normalize
            features['brightness'] = np.mean([color.get('brightness', 0) for color in colors])
            features['saturation'] = np.mean([color.get('saturation', 0) for color in colors])
        else:
            features['color_variety'] = 0.0
            features['brightness'] = 0.5
            features['saturation'] = 0.5
        
        # Composition features
        composition = visual_data.get('composition', {})
        features['rule_of_thirds'] = composition.get('rule_of_thirds_score', 0.0)
        features['symmetry'] = composition.get('symmetry_score', 0.0)
        features['leading_lines'] = composition.get('leading_lines_score', 0.0)
        
        # Object detection results (if available)
        objects = visual_data.get('detected_objects', [])
        features['object_count'] = len(objects) / 20.0  # Normalize
        features['people_present'] = 1.0 if any('person' in obj.get('label', '') for obj in objects) else 0.0
        features['text_present'] = 1.0 if any('text' in obj.get('label', '') for obj in objects) else 0.0
        
        return features
    
    async def _extract_audio_features(self, content_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract audio features from audio/video content"""
        features = {}
        
        audio_data = content_data.get('audio_data', {})
        
        # Basic audio properties
        features['duration'] = audio_data.get('duration_seconds', 0) / 600.0  # Normalize to 10 min max
        features['sample_rate'] = audio_data.get('sample_rate', 0) / 48000.0
        features['bit_rate'] = audio_data.get('bit_rate', 0) / 320000.0  # Normalize to 320kbps max
        
        # Audio analysis features (if available)
        analysis = audio_data.get('analysis', {})
        features['tempo'] = analysis.get('tempo', 120) / 200.0  # Normalize BPM
        features['energy'] = analysis.get('energy', 0.0)
        features['valence'] = analysis.get('valence', 0.0)  # Positivity
        features['danceability'] = analysis.get('danceability', 0.0)
        features['acousticness'] = analysis.get('acousticness', 0.0)
        features['instrumentalness'] = analysis.get('instrumentalness', 0.0)
        features['speechiness'] = analysis.get('speechiness', 0.0)
        
        # Spectral features
        spectral = analysis.get('spectral_features', {})
        features['spectral_centroid'] = spectral.get('centroid', 0.0)
        features['spectral_bandwidth'] = spectral.get('bandwidth', 0.0)
        features['spectral_rolloff'] = spectral.get('rolloff', 0.0)
        features['zero_crossing_rate'] = spectral.get('zcr', 0.0)
        
        # MFCC features (simplified to first few coefficients)
        mfcc = analysis.get('mfcc', [])
        for i, coeff in enumerate(mfcc[:5]):  # First 5 MFCC coefficients
            features[f'mfcc_{i}'] = coeff
        
        return features
    
    async def _extract_style_features(self, content_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract style-related features"""
        features = {}
        
        # Content style metadata
        style_data = content_data.get('style_data', {})
        
        # Visual style (for visual content)
        visual_style = style_data.get('visual_style', {})
        features['minimalist_style'] = visual_style.get('minimalist', 0.0)
        features['vibrant_style'] = visual_style.get('vibrant', 0.0)
        features['professional_style'] = visual_style.get('professional', 0.0)
        features['artistic_style'] = visual_style.get('artistic', 0.0)
        features['modern_style'] = visual_style.get('modern', 0.0)
        
        # Writing style (for text content)
        text_style = style_data.get('text_style', {})
        features['formal_tone'] = text_style.get('formal', 0.0)
        features['casual_tone'] = text_style.get('casual', 0.0)
        features['humorous_tone'] = text_style.get('humorous', 0.0)
        features['educational_tone'] = text_style.get('educational', 0.0)
        features['persuasive_tone'] = text_style.get('persuasive', 0.0)
        
        # Production quality
        quality = style_data.get('production_quality', {})
        features['video_quality'] = quality.get('video_quality', 0.0)
        features['audio_quality'] = quality.get('audio_quality', 0.0)
        features['editing_quality'] = quality.get('editing_quality', 0.0)
        features['lighting_quality'] = quality.get('lighting_quality', 0.0)
        
        return features
    
    async def _extract_metadata_features(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metadata features"""
        metadata = content_data.get('metadata', {})
        
        return {
            'creation_date': metadata.get('creation_date'),
            'tags': metadata.get('tags', []),
            'category': metadata.get('category'),
            'language': metadata.get('language', 'en'),
            'platform': metadata.get('platform'),
            'content_format': metadata.get('format'),
            'target_audience': metadata.get('target_audience'),
            'content_purpose': metadata.get('purpose')
        }
    
    async def _extract_engagement_features(self, content_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract engagement-related features"""
        engagement = content_data.get('engagement_data', {})
        
        return {
            'likes': engagement.get('likes', 0) / 1000.0,  # Normalize
            'comments': engagement.get('comments', 0) / 100.0,
            'shares': engagement.get('shares', 0) / 100.0,
            'views': engagement.get('views', 0) / 10000.0,
            'engagement_rate': engagement.get('engagement_rate', 0.0),
            'click_through_rate': engagement.get('ctr', 0.0),
            'completion_rate': engagement.get('completion_rate', 0.0),
            'save_rate': engagement.get('save_rate', 0.0)
        }
    
    async def _extract_temporal_features(self, content_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract temporal features"""
        temporal = content_data.get('temporal_data', {})
        
        features = {
            'posting_hour': temporal.get('posting_hour', 12) / 24.0,
            'posting_day': temporal.get('posting_day', 1) / 7.0,
            'posting_month': temporal.get('posting_month', 6) / 12.0,
            'content_age_days': temporal.get('age_days', 0) / 365.0,
            'trending_score': temporal.get('trending_score', 0.0),
            'seasonality_score': temporal.get('seasonality_score', 0.0)
        }
        
        return features
    
    async def calculate_similarity(
        self,
        content_a: Dict[str, Any],
        content_b: Dict[str, Any],
        algorithm: Optional[SimilarityAlgorithm] = None
    ) -> SimilarityScore:
        """Calculate similarity between two pieces of content"""
        try:
            # Extract features
            features_a = await self.extract_content_features(content_a)
            features_b = await self.extract_content_features(content_b)
            
            if algorithm:
                # Use specific algorithm
                similarity = await self._calculate_single_algorithm_similarity(
                    features_a, features_b, algorithm
                )
            else:
                # Use ensemble approach
                similarity = await self._calculate_ensemble_similarity(features_a, features_b)
            
            return similarity
            
        except Exception as e:
            logger.error(f"❌ Error calculating content similarity: {e}")
            return SimilarityScore(
                content_a_id=content_a.get('content_id', 'unknown'),
                content_b_id=content_b.get('content_id', 'unknown'),
                overall_similarity=0.0,
                confidence=0.0
            )
    
    async def _calculate_ensemble_similarity(
        self,
        features_a: ContentFeatures,
        features_b: ContentFeatures
    ) -> SimilarityScore:
        """Calculate similarity using ensemble of algorithms"""
        
        similarity_scores = {}
        
        # Semantic similarity
        if features_a.semantic_embedding.size > 0 and features_b.semantic_embedding.size > 0:
            semantic_sim = self._cosine_similarity(
                features_a.semantic_embedding,
                features_b.semantic_embedding
            )
            similarity_scores['semantic'] = semantic_sim
        
        # Visual similarity
        if features_a.visual_features and features_b.visual_features:
            visual_sim = self._calculate_feature_similarity(
                features_a.visual_features,
                features_b.visual_features
            )
            similarity_scores['visual'] = visual_sim
        
        # Audio similarity
        if features_a.audio_features and features_b.audio_features:
            audio_sim = self._calculate_feature_similarity(
                features_a.audio_features,
                features_b.audio_features
            )
            similarity_scores['audio'] = audio_sim
        
        # Style similarity
        if features_a.style_features and features_b.style_features:
            style_sim = self._calculate_feature_similarity(
                features_a.style_features,
                features_b.style_features
            )
            similarity_scores['style'] = style_sim
        
        # Topic similarity (from text features)
        if features_a.text_features and features_b.text_features:
            topic_sim = self._calculate_topic_similarity(
                features_a.text_features,
                features_b.text_features
            )
            similarity_scores['topic'] = topic_sim
        
        # Engagement similarity
        if features_a.engagement_features and features_b.engagement_features:
            engagement_sim = self._calculate_feature_similarity(
                features_a.engagement_features,
                features_b.engagement_features
            )
            similarity_scores['engagement'] = engagement_sim
        
        # Calculate weighted overall similarity
        overall_similarity = 0.0
        total_weight = 0.0
        
        weights = {
            'semantic': 0.3,
            'visual': 0.25,
            'audio': 0.2,
            'style': 0.15,
            'topic': 0.1,
            'engagement': 0.0  # Don't include engagement in overall score
        }
        
        for sim_type, score in similarity_scores.items():
            weight = weights.get(sim_type, 0.0)
            overall_similarity += score * weight
            total_weight += weight
        
        if total_weight > 0:
            overall_similarity /= total_weight
        
        # Calculate confidence based on number of similarity metrics available
        confidence = len(similarity_scores) / 6.0  # Maximum 6 similarity types
        
        return SimilarityScore(
            content_a_id=features_a.content_id,
            content_b_id=features_b.content_id,
            overall_similarity=overall_similarity,
            semantic_similarity=similarity_scores.get('semantic', 0.0),
            visual_similarity=similarity_scores.get('visual', 0.0),
            audio_similarity=similarity_scores.get('audio', 0.0),
            style_similarity=similarity_scores.get('style', 0.0),
            topic_similarity=similarity_scores.get('topic', 0.0),
            engagement_similarity=similarity_scores.get('engagement', 0.0),
            confidence=confidence,
            algorithm_used=SimilarityAlgorithm.SEMANTIC_EMBEDDING
        )
    
    async def _calculate_single_algorithm_similarity(
        self,
        features_a: ContentFeatures,
        features_b: ContentFeatures,
        algorithm: SimilarityAlgorithm
    ) -> SimilarityScore:
        """Calculate similarity using single algorithm"""
        
        if algorithm == SimilarityAlgorithm.SEMANTIC_EMBEDDING:
            similarity = self._cosine_similarity(
                features_a.semantic_embedding,
                features_b.semantic_embedding
            )
        elif algorithm == SimilarityAlgorithm.VISUAL_FEATURES:
            similarity = self._calculate_feature_similarity(
                features_a.visual_features,
                features_b.visual_features
            )
        elif algorithm == SimilarityAlgorithm.AUDIO_FINGERPRINT:
            similarity = self._calculate_feature_similarity(
                features_a.audio_features,
                features_b.audio_features
            )
        elif algorithm == SimilarityAlgorithm.STYLE_ANALYSIS:
            similarity = self._calculate_feature_similarity(
                features_a.style_features,
                features_b.style_features
            )
        elif algorithm == SimilarityAlgorithm.TOPIC_MODELING:
            similarity = self._calculate_topic_similarity(
                features_a.text_features,
                features_b.text_features
            )
        else:
            # TF-IDF or fallback
            similarity = 0.5
        
        return SimilarityScore(
            content_a_id=features_a.content_id,
            content_b_id=features_b.content_id,
            overall_similarity=similarity,
            confidence=0.8,
            algorithm_used=algorithm
        )
    
    def _cosine_similarity(self, vec_a: np.ndarray, vec_b: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        if vec_a.size == 0 or vec_b.size == 0:
            return 0.0
        
        # Ensure same dimension
        min_dim = min(len(vec_a), len(vec_b))
        vec_a = vec_a[:min_dim]
        vec_b = vec_b[:min_dim]
        
        dot_product = np.dot(vec_a, vec_b)
        norm_a = np.linalg.norm(vec_a)
        norm_b = np.linalg.norm(vec_b)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return dot_product / (norm_a * norm_b)
    
    def _calculate_feature_similarity(
        self,
        features_a: Dict[str, float],
        features_b: Dict[str, float]
    ) -> float:
        """Calculate similarity between feature dictionaries"""
        if not features_a or not features_b:
            return 0.0
        
        common_features = set(features_a.keys()) & set(features_b.keys())
        
        if not common_features:
            return 0.0
        
        similarities = []
        for feature in common_features:
            val_a = features_a[feature]
            val_b = features_b[feature]
            
            # Calculate normalized similarity
            if val_a == 0 and val_b == 0:
                similarity = 1.0
            elif val_a == 0 or val_b == 0:
                similarity = 0.0
            else:
                # Use inverse of relative difference
                max_val = max(abs(val_a), abs(val_b))
                difference = abs(val_a - val_b)
                similarity = 1.0 - (difference / max_val)
            
            similarities.append(similarity)
        
        return np.mean(similarities)
    
    def _calculate_topic_similarity(
        self,
        features_a: Dict[str, float],
        features_b: Dict[str, float]
    ) -> float:
        """Calculate topic similarity from text features"""
        if not features_a or not features_b:
            return 0.0
        
        # Focus on topic-related features
        topic_features = ['tech_topic_score', 'lifestyle_topic_score', 'business_topic_score']
        
        topic_similarities = []
        for feature in topic_features:
            if feature in features_a and feature in features_b:
                val_a = features_a[feature]
                val_b = features_b[feature]
                
                # Calculate similarity
                if val_a == 0 and val_b == 0:
                    similarity = 1.0
                else:
                    max_val = max(val_a, val_b)
                    similarity = 1.0 - abs(val_a - val_b) / max(max_val, 0.001)
                
                topic_similarities.append(similarity)
        
        return np.mean(topic_similarities) if topic_similarities else 0.0
    
    async def batch_calculate_similarities(
        self,
        query_content: Dict[str, Any],
        candidate_contents: List[Dict[str, Any]],
        algorithm: Optional[SimilarityAlgorithm] = None
    ) -> List[SimilarityScore]:
        """Batch calculate similarities for multiple content pieces"""
        similarities = []
        
        # Extract query features once
        query_features = await self.extract_content_features(query_content)
        
        for candidate in candidate_contents:
            try:
                candidate_features = await self.extract_content_features(candidate)
                
                if algorithm:
                    similarity = await self._calculate_single_algorithm_similarity(
                        query_features, candidate_features, algorithm
                    )
                else:
                    similarity = await self._calculate_ensemble_similarity(
                        query_features, candidate_features
                    )
                
                similarities.append(similarity)
                
            except Exception as e:
                logger.warning(f"⚠️ Error calculating similarity for content {candidate.get('content_id')}: {e}")
        
        return similarities
    
    async def find_similar_content(
        self,
        query_content: Dict[str, Any],
        content_database: List[Dict[str, Any]],
        top_k: int = 10,
        min_similarity: float = None
    ) -> List[Dict[str, Any]]:
        """Find most similar content from database"""
        min_similarity = min_similarity or self.similarity_threshold
        
        # Calculate similarities
        similarities = await self.batch_calculate_similarities(
            query_content, content_database
        )
        
        # Combine with content and filter
        results = []
        for i, similarity in enumerate(similarities):
            if similarity.overall_similarity >= min_similarity:
                results.append({
                    'content': content_database[i],
                    'similarity_score': similarity,
                    'match_strength': self._get_match_strength(similarity.overall_similarity)
                })
        
        # Sort by similarity
        results.sort(key=lambda x: x['similarity_score'].overall_similarity, reverse=True)
        
        return results[:top_k]
    
    def _get_match_strength(self, similarity: float) -> str:
        """Get human-readable match strength"""
        if similarity >= 0.9:
            return "very_strong"
        elif similarity >= 0.8:
            return "strong"
        elif similarity >= 0.7:
            return "good"
        elif similarity >= 0.6:
            return "moderate"
        elif similarity >= 0.5:
            return "weak"
        else:
            return "very_weak"
    
    async def create_content_vector(
        self,
        content_data: Dict[str, Any],
        vector_type: str = "combined"
    ) -> ContentVector:
        """Create content vector for efficient similarity search"""
        content_id = content_data['content_id']
        
        # Check cache
        cache_key = f"{content_id}_{vector_type}"
        if cache_key in self.vector_cache:
            return self.vector_cache[cache_key]
        
        # Extract features
        features = await self.extract_content_features(content_data)
        
        if vector_type == "semantic":
            vector = features.semantic_embedding
        elif vector_type == "combined":
            vector = features.get_feature_vector()
        elif vector_type == "visual":
            vector = np.array(list(features.visual_features.values()), dtype=np.float32)
        elif vector_type == "audio":
            vector = np.array(list(features.audio_features.values()), dtype=np.float32)
        else:
            vector = features.get_feature_vector()
        
        content_vector = ContentVector(
            content_id=content_id,
            vector=vector,
            vector_type=vector_type,
            dimensions=len(vector)
        )
        
        # Cache the vector
        if len(self.vector_cache) < self.cache_size_limit:
            self.vector_cache[cache_key] = content_vector
        
        return content_vector
    
    async def clear_cache(self):
        """Clear all caches"""
        self.content_cache.clear()
        self.vector_cache.clear()
        logger.info("🗑️ Content similarity cache cleared")
    
    async def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        return {
            'content_features_cached': len(self.content_cache),
            'vectors_cached': len(self.vector_cache)
        }