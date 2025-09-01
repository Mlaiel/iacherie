"""Content Intelligence Engine
===========================

Professional multi-format content analysis and intelligence system.
Implements advanced AI for content understanding, classification, and optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import json
import hashlib
import numpy as np
from pathlib import Path

import torch
import torch.nn.functional as F
from transformers import (
    AutoTokenizer, AutoModel, pipeline,
    CLIPProcessor, CLIPModel
)
import librosa
import cv2
from PIL import Image
import imagehash
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import spacy
from langdetect import detect

from ..core.config import get_settings
from ..core.exceptions import ContentAnalysisError
from ..database.models import ContentAnalysis, TrendPrediction
from ..utils.cache_manager import CacheManager
from ..utils.metrics_collector import MetricsCollector

logger = logging.getLogger(__name__)
settings = get_settings()

class ContentType(Enum):
    """
Content type enumeration."""

    AUDIO = "audio"
    VIDEO = "video" 
    IMAGE = "image"
    TEXT = "text"
    MIXED = "mixed"

class ContentCategory(Enum):
    """Content category classification."""

    MUSIC = "music"
    PODCAST = "podcast"
    EDUCATIONAL = "educational"
    ENTERTAINMENT = "entertainment"
    NEWS = "news"
    LIFESTYLE = "lifestyle"
    GAMING = "gaming"
    SPORTS = "sports"
    TECHNOLOGY = "technology"
    ARTS = "arts"

@dataclass
class ContentFeatures:
    """Content feature extraction results."""
    content_id: str
    content_type: ContentType
    features: Dict[str, Union[float, List[float], str]]
    embeddings: Optional[np.ndarray]
    metadata: Dict[str, Any]
    confidence_score: float
    processing_time: float
    timestamp: datetime

@dataclass
class ContentInsights:
    """
Content intelligence insights."""
    content_id: str
    category: ContentCategory
    sentiment_score: float
    engagement_prediction: float
    viral_potential: float
    trending_topics: List[str]
    audience_segments: List[str]
    optimization_suggestions: List[str]
    collaboration_opportunities: List[Dict[str, Any]]
    monetization_potential: float

class ContentIntelligenceEngine:
    """
    Advanced content intelligence engine for multi-format analysis.
    
    Features:
    - Multi-modal content analysis (audio, video, image, text)
    - AI-powered feature extraction
    - Sentiment and engagement prediction
    - Trend detection and viral potential scoring
    - Collaboration opportunity matching
    - Content optimization recommendations
    """
    
    def __init__(self):
        self.cache_manager = CacheManager()
        self.metrics_collector = MetricsCollector()
        self._initialize_models()
        
    def _initialize_models(self):
        """
Initialize AI models for content analysis."""
        try:
            # Text analysis models
            self.text_tokenizer = AutoTokenizer.from_pretrained(
                "sentence-transformers/all-MiniLM-L6-v2"
            )
            self.text_model = AutoModel.from_pretrained(
                "sentence-transformers/all-MiniLM-L6-v2"
            )
            
            # CLIP for multimodal analysis
            self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
            self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
            
            # Sentiment analysis
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest"
            )
            
            # Named entity recognition
            self.nlp = spacy.load("en_core_web_sm")
            
            # TF-IDF for topic extraction
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words='english',
                ngram_range=(1, 3)
            )
            
            logger.info("Content intelligence models initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize models: {e}")
            raise ContentAnalysisError(f"Model initialization failed: {e}")
    
    async def analyze_content(
        self,
        content_data: Union[str, bytes, Path],
        content_type: ContentType,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ContentFeatures:
        """
        Analyze content and extract comprehensive features.
        
        Args:
            content_data: Content data (file path, text, or binary data)
            content_type: Type of content to analyze
            metadata: Additional metadata for analysis
            
        Returns:
            ContentFeatures object with extracted features
        """
        start_time = datetime.now()
        
        try:
            # Generate content ID
            content_id = self._generate_content_id(content_data, content_type)
            
            # Check cache
            cached_features = await self.cache_manager.get(f"content_features:{content_id}")
            if cached_features:
                return ContentFeatures(**cached_features)
            
            # Extract features based on content type
            features = {}
            embeddings = None
            
            if content_type == ContentType.TEXT:
                features, embeddings = await self._analyze_text_content(content_data)
            elif content_type == ContentType.IMAGE:
                features, embeddings = await self._analyze_image_content(content_data)
            elif content_type == ContentType.AUDIO:
                features, embeddings = await self._analyze_audio_content(content_data)
            elif content_type == ContentType.VIDEO:
                features, embeddings = await self._analyze_video_content(content_data)
            elif content_type == ContentType.MIXED:
                features, embeddings = await self._analyze_mixed_content(content_data)
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence(features)
            
            # Create content features object
            content_features = ContentFeatures(
                content_id=content_id,
                content_type=content_type,
                features=features,
                embeddings=embeddings,
                metadata=metadata or {},
                confidence_score=confidence_score,
                processing_time=(datetime.now() - start_time).total_seconds(),
                timestamp=datetime.now()
            )
            
            # Cache results
            await self.cache_manager.set(
                f"content_features:{content_id}",
                asdict(content_features),
                ttl=3600
            )
            
            # Collect metrics
            self.metrics_collector.increment("content_analysis_completed")
            self.metrics_collector.histogram(
                "content_analysis_duration",
                content_features.processing_time
            )
            
            return content_features
            
        except Exception as e:
            logger.error(f"Content analysis failed: {e}")
            self.metrics_collector.increment("content_analysis_failed")
            raise ContentAnalysisError(f"Content analysis failed: {e}")
    
    async def _analyze_text_content(self, text_data: str) -> Tuple[Dict[str, Any], np.ndarray]:
        """Analyze text content and extract features."""
        features = {}
        
        # Basic text statistics
        features['word_count'] = len(text_data.split())
        features['char_count'] = len(text_data)
        features['sentence_count'] = len(text_data.split('.'))
        
        # Language detection
        try:
            features['language'] = detect(text_data)
        except:
            features['language'] = 'unknown'
        
        # Sentiment analysis
        sentiment = self.sentiment_analyzer(text_data[:512])[0]
        features['sentiment_label'] = sentiment['label']
        features['sentiment_score'] = sentiment['score']
        
        # Named entity recognition
        doc = self.nlp(text_data[:1000000])  # Limit for performance
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        features['entities'] = entities
        features['entity_count'] = len(entities)
        
        # Topic extraction using TF-IDF
        try:
            tfidf_matrix = self.tfidf_vectorizer.fit_transform([text_data])
            feature_names = self.tfidf_vectorizer.get_feature_names_out()
            scores = tfidf_matrix.toarray()[0]
            top_indices = scores.argsort()[-10:][::-1]
            features['top_topics'] = [feature_names[i] for i in top_indices if scores[i] > 0]
        except:
            features['top_topics'] = []
        
        # Generate embeddings
        inputs = self.text_tokenizer(
            text_data[:512],
            return_tensors="pt",
            truncation=True,
            padding=True
        )
        
        with torch.no_grad():
            outputs = self.text_model(**inputs)
            embeddings = outputs.last_hidden_state.mean(dim=1).numpy()[0]
        
        # Readability metrics
        features['avg_sentence_length'] = features['word_count'] / max(features['sentence_count'], 1)
        features['complexity_score'] = self._calculate_text_complexity(text_data)
        
        return features, embeddings
    
    async def _analyze_image_content(self, image_data: Union[str, Path, bytes]) -> Tuple[Dict[str, Any], np.ndarray]:
        """Analyze image content and extract features."""
        features = {}
        
        # Load image
        if isinstance(image_data, (str, Path)):
            image = Image.open(image_data)
        else:
            image = Image.open(io.BytesIO(image_data))
        
        # Basic image properties
        features['width'], features['height'] = image.size
        features['aspect_ratio'] = features['width'] / features['height']
        features['format'] = image.format
        features['mode'] = image.mode
        
        # Color analysis
        if image.mode == 'RGB':
            colors = image.getcolors(maxcolors=256*256*256)
            if colors:
                dominant_color = max(colors, key=lambda x: x[0])[1]
                features['dominant_color'] = dominant_color
        
        # Perceptual hashing
        features['perceptual_hash'] = str(imagehash.phash(image))
        features['average_hash'] = str(imagehash.average_hash(image))
        features['difference_hash'] = str(imagehash.dhash(image))
        
        # CLIP embeddings for semantic understanding
        inputs = self.clip_processor(images=image, return_tensors="pt")
        with torch.no_grad():
            image_embeddings = self.clip_model.get_image_features(**inputs)
            embeddings = image_embeddings.numpy()[0]
        
        # Visual complexity estimation
        gray_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
        features['visual_complexity'] = cv2.Laplacian(gray_image, cv2.CV_64F).var()
        
        return features, embeddings
    
    async def _analyze_audio_content(self, audio_data: Union[str, Path, bytes]) -> Tuple[Dict[str, Any], np.ndarray]:
        """Analyze audio content and extract features."""
        features = {}
        
        # Load audio
        if isinstance(audio_data, (str, Path)):
            y, sr = librosa.load(audio_data)
        else:
            y, sr = librosa.load(io.BytesIO(audio_data))
        
        # Basic audio properties
        features['duration'] = len(y) / sr
        features['sample_rate'] = sr
        features['channels'] = 1 if y.ndim == 1 else y.shape[0]
        
        # Spectral features
        features['spectral_centroid'] = float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)))
        features['spectral_bandwidth'] = float(np.mean(librosa.feature.spectral_bandwidth(y=y, sr=sr)))
        features['spectral_rolloff'] = float(np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr)))
        features['zero_crossing_rate'] = float(np.mean(librosa.feature.zero_crossing_rate(y)))
        
        # MFCC features
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        features['mfcc_mean'] = np.mean(mfcc, axis=1).tolist()
        features['mfcc_std'] = np.std(mfcc, axis=1).tolist()
        
        # Tempo and rhythm
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
        features['tempo'] = float(tempo)
        features['beat_count'] = len(beats)
        
        # Chroma features for harmony analysis
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        features['chroma_mean'] = np.mean(chroma, axis=1).tolist()
        
        # Energy and dynamics
        features['rms_energy'] = float(np.mean(librosa.feature.rms(y=y)))
        
        # Use MFCC as embeddings
        embeddings = np.mean(mfcc, axis=1)
        
        return features, embeddings
    
    async def _analyze_video_content(self, video_data: Union[str, Path]) -> Tuple[Dict[str, Any], np.ndarray]:
        """
Analyze video content and extract features."""
        features = {}
        
        # Open video
        cap = cv2.VideoCapture(str(video_data))
        
        # Basic video properties
        features['fps'] = cap.get(cv2.CAP_PROP_FPS)
        features['frame_count'] = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        features['duration'] = features['frame_count'] / features['fps'] if features['fps'] > 0 else 0
        features['width'] = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        features['height'] = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        features['aspect_ratio'] = features['width'] / features['height']
        
        # Sample frames for analysis
        frame_features = []
        sample_count = min(10, int(features['frame_count']))
        frame_interval = max(1, features['frame_count'] // sample_count)
        
        for i in range(0, int(features['frame_count']), frame_interval):
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, frame = cap.read()
            if ret:
                # Convert to PIL Image for CLIP
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_frame = Image.fromarray(frame_rgb)
                
                # Extract frame features
                inputs = self.clip_processor(images=pil_frame, return_tensors="pt")
                with torch.no_grad():
                    frame_embedding = self.clip_model.get_image_features(**inputs)
                    frame_features.append(frame_embedding.numpy()[0])
        
        cap.release()
        
        # Aggregate frame embeddings
        if frame_features:
            embeddings = np.mean(frame_features, axis=0)
            features['visual_variance'] = float(np.var(frame_features))
        else:
            embeddings = np.zeros(512)  # Default CLIP embedding size
            features['visual_variance'] = 0.0
        
        # Motion analysis
        features['scene_changes'] = len(frame_features)  # Simplified
        
        return features, embeddings
    
    async def _analyze_mixed_content(self, content_data: Dict[str, Any]) -> Tuple[Dict[str, Any], np.ndarray]:
        """Analyze mixed content (multiple formats)."""
        features = {}
        all_embeddings = []
        
        for content_type, data in content_data.items():
            if content_type == 'text':
                text_features, text_embeddings = await self._analyze_text_content(data)
                features['text'] = text_features
                all_embeddings.append(text_embeddings)
            elif content_type == 'image':
                image_features, image_embeddings = await self._analyze_image_content(data)
                features['image'] = image_features
                all_embeddings.append(image_embeddings)
            elif content_type == 'audio':
                audio_features, audio_embeddings = await self._analyze_audio_content(data)
                features['audio'] = audio_features
                all_embeddings.append(audio_embeddings)
        
        # Combine embeddings
        if all_embeddings:
            # Normalize to same dimension and average
            min_dim = min(emb.shape[0] for emb in all_embeddings)
            normalized_embeddings = [emb[:min_dim] for emb in all_embeddings]
            embeddings = np.mean(normalized_embeddings, axis=0)
        else:
            embeddings = np.zeros(384)  # Default dimension
        
        return features, embeddings
    
    async def generate_insights(self, content_features: ContentFeatures) -> ContentInsights:
        """
Generate intelligent insights from content features."""
        try:
            # Classify content category
            category = self._classify_content_category(content_features)
            
            # Predict sentiment and engagement
            sentiment_score = self._extract_sentiment_score(content_features)
            engagement_prediction = self._predict_engagement(content_features)
            
            # Calculate viral potential
            viral_potential = self._calculate_viral_potential(content_features)
            
            # Extract trending topics
            trending_topics = self._extract_trending_topics(content_features)
            
            # Identify audience segments
            audience_segments = self._identify_audience_segments(content_features)
            
            # Generate optimization suggestions
            optimization_suggestions = self._generate_optimization_suggestions(content_features)
            
            # Find collaboration opportunities
            collaboration_opportunities = await self._find_collaboration_opportunities(content_features)
            
            # Calculate monetization potential
            monetization_potential = self._calculate_monetization_potential(content_features)
            
            return ContentInsights(
                content_id=content_features.content_id,
                category=category,
                sentiment_score=sentiment_score,
                engagement_prediction=engagement_prediction,
                viral_potential=viral_potential,
                trending_topics=trending_topics,
                audience_segments=audience_segments,
                optimization_suggestions=optimization_suggestions,
                collaboration_opportunities=collaboration_opportunities,
                monetization_potential=monetization_potential
            )
            
        except Exception as e:
            logger.error(f"Insight generation failed: {e}")
            raise ContentAnalysisError(f"Insight generation failed: {e}")
    
    def _generate_content_id(self, content_data: Any, content_type: ContentType) -> str:
        """Generate unique content ID."""
        content_str = str(content_data) + str(content_type.value)
        return hashlib.sha256(content_str.encode()).hexdigest()[:16]
    
    def _calculate_confidence(self, features: Dict[str, Any]) -> float:
        """
Calculate confidence score for analysis."""
        # Simple confidence calculation based on feature completeness
        total_features = len(features)
        non_empty_features = sum(1 for v in features.values() if v is not None and v != "" and v != [])
        return min(0.95, non_empty_features / max(total_features, 1))
    
    def _calculate_text_complexity(self, text: str) -> float:
        """Calculate text complexity score."""
        words = text.split()
        avg_word_length = sum(len(word) for word in words) / max(len(words), 1)
        unique_words = len(set(words.lower()))
        vocabulary_diversity = unique_words / max(len(words), 1)
        return (avg_word_length * 0.3 + vocabulary_diversity * 0.7) * 10
    
    def _classify_content_category(self, content_features: ContentFeatures) -> ContentCategory:
        """
Classify content into categories using AI."""
        # Simplified classification logic
        features = content_features.features
        
        if content_features.content_type == ContentType.AUDIO:
            if features.get('tempo', 0) > 0:
                return ContentCategory.MUSIC
            else:
                return ContentCategory.PODCAST
        
        if 'text' in features:
            text_features = features['text']
            topics = text_features.get('top_topics', [])
            
            music_keywords = ['music', 'song', 'album', 'artist', 'band']
            tech_keywords = ['technology', 'ai', 'programming', 'software']
            
            if any(keyword in ' '.join(topics).lower() for keyword in music_keywords):
                return ContentCategory.MUSIC
            elif any(keyword in ' '.join(topics).lower() for keyword in tech_keywords):
                return ContentCategory.TECHNOLOGY
        
        return ContentCategory.ENTERTAINMENT  # Default
    
    def _extract_sentiment_score(self, content_features: ContentFeatures) -> float:
        """
Extract sentiment score from content features."""
        if 'text' in content_features.features:
            return content_features.features['text'].get('sentiment_score', 0.5)
        return 0.5  # Neutral default
    
    def _predict_engagement(self, content_features: ContentFeatures) -> float:
        """
Predict engagement score using ML."""
        # Simplified engagement prediction
        score = 0.5
        
        if content_features.content_type == ContentType.VIDEO:
            # Higher engagement for optimal video length
            duration = content_features.features.get('duration', 0)
            if 30 <= duration <= 300:  # 30s to 5min
                score += 0.2
        
        if 'text' in content_features.features:
            sentiment = content_features.features['text'].get('sentiment_score', 0.5)
            if sentiment > 0.7:  # Positive sentiment
                score += 0.15
        
        return min(1.0, score)
    
    def _calculate_viral_potential(self, content_features: ContentFeatures) -> float:
        """
Calculate viral potential score."""
        # Simplified viral potential calculation
        potential = 0.3
        
        # High visual complexity can be engaging
        if 'image' in content_features.features:
            complexity = content_features.features['image'].get('visual_complexity', 0)
            if complexity > 1000:  # High complexity threshold
                potential += 0.2
        
        # Trending topics boost viral potential
        if 'text' in content_features.features:
            topics = content_features.features['text'].get('top_topics', [])
            if len(topics) > 5:
                potential += 0.1
        
        return min(1.0, potential)
    
    def _extract_trending_topics(self, content_features: ContentFeatures) -> List[str]:
        """
Extract trending topics from content."""
        if 'text' in content_features.features:
            return content_features.features['text'].get('top_topics', [])[:5]
        return []
    
    def _identify_audience_segments(self, content_features: ContentFeatures) -> List[str]:
        """
Identify target audience segments."""
        segments = []
        
        category = self._classify_content_category(content_features)
        
        if category == ContentCategory.MUSIC:
            segments.extend(['music_lovers', 'young_adults', 'artists'])
        elif category == ContentCategory.TECHNOLOGY:
            segments.extend(['tech_enthusiasts', 'developers', 'early_adopters'])
        elif category == ContentCategory.ENTERTAINMENT:
            segments.extend(['general_audience', 'entertainment_seekers'])
        
        return segments
    
    def _generate_optimization_suggestions(self, content_features: ContentFeatures) -> List[str]:
        """
Generate content optimization suggestions."""
        suggestions = []
        
        if content_features.content_type == ContentType.TEXT:
            word_count = content_features.features.get('word_count', 0)
            if word_count < 300:
                suggestions.append("Consider expanding content to improve SEO")
            elif word_count > 2000:
                suggestions.append("Consider breaking into multiple posts for better engagement")
        
        if content_features.content_type == ContentType.VIDEO:
            duration = content_features.features.get('duration', 0)
            if duration > 600:  # 10 minutes
                suggestions.append("Consider shorter format for social media")
        
        sentiment = self._extract_sentiment_score(content_features)
        if sentiment < 0.3:
            suggestions.append("Consider more positive messaging for better engagement")
        
        return suggestions
    
    async def _find_collaboration_opportunities(self, content_features: ContentFeatures) -> List[Dict[str, Any]]:
        """Find collaboration opportunities based on content analysis."""
        opportunities = []
        
        category = self._classify_content_category(content_features)
        trending_topics = self._extract_trending_topics(content_features)
        
        # Mock collaboration opportunities
        if category == ContentCategory.MUSIC:
            opportunities.append({
                'type': 'artist_collaboration',
                'description': 'Connect with similar genre artists',
                'potential_reach': 10000,
                'confidence': 0.8
            })
        
        if len(trending_topics) > 3:
            opportunities.append({
                'type': 'trend_collaboration',
                'description': f'Collaborate on trending topics: {", ".join(trending_topics[:3])}',
                'potential_reach': 5000,
                'confidence': 0.6
            })
        
        return opportunities
    
    def _calculate_monetization_potential(self, content_features: ContentFeatures) -> float:
        """Calculate monetization potential score."""
        potential = 0.4  # Base potential
        
        engagement = self._predict_engagement(content_features)
        viral = self._calculate_viral_potential(content_features)
        
        # High engagement and viral potential increase monetization
        potential += (engagement * 0.3 + viral * 0.3)
        
        # Professional content categories have higher potential
        category = self._classify_content_category(content_features)
        if category in [ContentCategory.MUSIC, ContentCategory.TECHNOLOGY, ContentCategory.EDUCATIONAL]:
            potential += 0.1
        
        return min(1.0, potential)

# Factory function
def create_content_intelligence_engine() -> ContentIntelligenceEngine:
    """
Create and return a content intelligence engine instance."""
    return ContentIntelligenceEngine()
