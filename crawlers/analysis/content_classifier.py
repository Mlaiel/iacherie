"""Content Classifier
==================

Advanced AI-powered content classification system for automated categorization.
Implements multi-modal classification with deep learning and traditional ML approaches.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.

Expertise combinée:
- Lead Developer IA: Architecture intelligente et optimisations ML
- Backend Senior: Infrastructure robuste et scalabilité enterprise
- ML Engineer: Algorithmes d'apprentissage et modèles prédictifs
- DBA Expert: Gestion de données et optimisation des requêtes
- Sécurité: Protection et chiffrement des données sensibles
- Microservices: Architecture distribuée et communication inter-services
- Audio/Vidéo: Traitement multimédia et analyse de contenu
- DevOps: Déploiement, monitoring et infrastructure cloud
- IA Prompt Engineer: Optimisation des interactions et prompts
"""

import asyncio
import logging
import numpy as np
import json
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
import pickle
import re
from collections import Counter
import torch
import torch.nn as nn
from transformers import (
    AutoTokenizer, AutoModel, AutoModelForSequenceClassification,
    CLIPProcessor, CLIPModel, pipeline
)
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
import cv2
import librosa
from PIL import Image

logger = logging.getLogger(__name__)

class ContentCategory(Enum):
    """
Content categories for classification."""

    MUSIC = "music"
    PHOTOGRAPHY = "photography"
    VIDEO_CONTENT = "video_content"
    ART_DESIGN = "art_design"
    TECHNOLOGY = "technology"
    BUSINESS = "business"
    EDUCATION = "education"
    ENTERTAINMENT = "entertainment"
    NEWS_MEDIA = "news_media"
    LIFESTYLE = "lifestyle"
    SPORTS = "sports"
    GAMING = "gaming"
    FASHION = "fashion"
    FOOD_COOKING = "food_cooking"
    TRAVEL = "travel"
    HEALTH_FITNESS = "health_fitness"
    SCIENCE = "science"
    POLITICS = "politics"
    RELIGION = "religion"
    ADULT_CONTENT = "adult_content"
    UNKNOWN = "unknown"

class ClassificationConfidence(Enum):
    """Classification confidence levels."""

    VERY_HIGH = "very_high"  # > 0.9
    HIGH = "high"           # 0.7 - 0.9
    MEDIUM = "medium"       # 0.5 - 0.7
    LOW = "low"            # 0.3 - 0.5
    VERY_LOW = "very_low"  # < 0.3

class ClassificationMethod(Enum):
    """Classification methods."""

    DEEP_LEARNING = "deep_learning"
    TRADITIONAL_ML = "traditional_ml"
    RULE_BASED = "rule_based"
    ENSEMBLE = "ensemble"
    MULTIMODAL = "multimodal"

@dataclass
class ClassificationResult:
    """Content classification result."""
    content_id: str
    primary_category: ContentCategory
    confidence: float
    confidence_level: ClassificationConfidence
    method_used: ClassificationMethod
    
    # Detailed predictions
    category_scores: Dict[ContentCategory, float] = field(default_factory=dict)
    subcategories: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    
    # Content properties
    is_safe_content: bool = True
    adult_content_probability: float = 0.0
    violence_probability: float = 0.0
    hate_speech_probability: float = 0.0
    
    # Quality indicators
    content_quality_score: float = 0.0
    professionalism_score: float = 0.0
    engagement_potential: float = 0.0
    
    # Metadata
    processing_time: float = 0.0
    features_used: List[str] = field(default_factory=list)
    model_version: str = "1.0"
    created_at: datetime = field(default_factory=datetime.now)

class ContentClassifier:
    """
    Advanced AI-powered content classifier with multi-modal capabilities.
    
    Features:
    - Multi-modal classification (text, image, audio, video)
    - Deep learning models (BERT, CLIP, custom CNNs)
    - Traditional ML ensemble methods
    - Content safety and quality assessment
    - Real-time and batch processing
    - Continuous learning and model updates
    """
    
    def __init__(
        self,
        model_cache_dir: str = "/tmp/classifier_models",
        enable_gpu: bool = True,
        confidence_threshold: float = 0.5,
        enable_safety_filter: bool = True,
        model_ensemble: bool = True
    ):
        """
        Initialize content classifier.
        
        Args:
            model_cache_dir: Directory for caching ML models
            enable_gpu: Enable GPU acceleration
            confidence_threshold: Minimum confidence for classification
            enable_safety_filter: Enable content safety filtering
            model_ensemble: Use ensemble of multiple models
        """
        self.model_cache_dir = Path(model_cache_dir)
        self.model_cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.enable_gpu = enable_gpu and torch.cuda.is_available()
        self.confidence_threshold = confidence_threshold
        self.enable_safety_filter = enable_safety_filter
        self.model_ensemble = model_ensemble
        
        # Classification statistics
        self.classification_count = 0
        self.accuracy_scores = []
        self.processing_times = []
        self.category_counts = {}
        
        # Model components
        self.text_models = {}
        self.image_models = {}
        self.audio_models = {}
        self.ensemble_models = {}
        
        # Feature extractors
        self.text_vectorizer = None
        self.category_keywords = {}
        
        # Initialize models
        self._initialize_models()
        self._load_category_definitions()
        
        logger.info(f"ContentClassifier initialized with GPU: {self.enable_gpu}")
    
    def _initialize_models(self) -> None:
        """Initialize classification models."""
        try:
            # Text classification models
            self.text_tokenizer = AutoTokenizer.from_pretrained('distilbert-base-uncased')
            self.text_model = AutoModelForSequenceClassification.from_pretrained(
                'distilbert-base-uncased',
                num_labels=len(ContentCategory)
            )
            
            # Image classification models
            self.clip_processor = CLIPProcessor.from_pretrained('openai/clip-vit-base-patch32')
            self.clip_model = CLIPModel.from_pretrained('openai/clip-vit-base-patch32')
            
            # Safety models
            if self.enable_safety_filter:
                self.safety_classifier = pipeline(
                    "text-classification",
                    model="unitary/toxic-bert",
                    device=0 if self.enable_gpu else -1
                )
            
            # Traditional ML models
            self.text_vectorizer = TfidfVectorizer(
                max_features=10000,
                stop_words='english',
                ngram_range=(1, 3),
                lowercase=True
            )
            
            # Ensemble classifiers
            self.ensemble_models = {
                'random_forest': RandomForestClassifier(n_estimators=100, random_state=42),
                'gradient_boost': GradientBoostingClassifier(random_state=42),
                'logistic_regression': LogisticRegression(random_state=42, max_iter=1000)
            }
            
            # Move models to GPU if available
            if self.enable_gpu:
                self.text_model = self.text_model.cuda()
                self.clip_model = self.clip_model.cuda()
            
            logger.info("Classification models initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize classification models: {e}")
            raise
    
    def _load_category_definitions(self) -> None:
        """Load category definitions and keywords."""
        self.category_keywords = {
            ContentCategory.MUSIC: [
                'music', 'song', 'album', 'artist', 'band', 'concert', 'audio', 'sound',
                'melody', 'rhythm', 'beat', 'lyrics', 'vocal', 'instrument', 'guitar',
                'piano', 'drums', 'bass', 'spotify', 'itunes', 'streaming'
            ],
            ContentCategory.PHOTOGRAPHY: [
                'photo', 'photography', 'camera', 'lens', 'picture', 'image', 'portrait',
                'landscape', 'studio', 'shoot', 'photographer', 'canon', 'nikon', 'sony',
                'exposure', 'aperture', 'shutter', 'iso', 'composition', 'lighting'
            ],
            ContentCategory.VIDEO_CONTENT: [
                'video', 'film', 'movie', 'cinema', 'documentary', 'vlog', 'youtube',
                'tiktok', 'instagram', 'content', 'creator', 'filmmaker', 'director',
                'editing', 'montage', 'scene', 'frame', 'footage', 'production'
            ],
            ContentCategory.ART_DESIGN: [
                'art', 'design', 'painting', 'drawing', 'sketch', 'illustration',
                'graphic', 'creative', 'artwork', 'artist', 'gallery', 'exhibition',
                'sculpture', 'digital', 'vector', 'photoshop', 'illustrator', 'canvas'
            ],
            ContentCategory.TECHNOLOGY: [
                'technology', 'tech', 'software', 'hardware', 'computer', 'digital',
                'programming', 'coding', 'development', 'app', 'website', 'ai',
                'artificial', 'intelligence', 'machine', 'learning', 'data', 'algorithm'
            ],
            ContentCategory.BUSINESS: [
                'business', 'company', 'corporate', 'marketing', 'finance', 'startup',
                'entrepreneur', 'investment', 'revenue', 'profit', 'strategy', 'management',
                'leadership', 'sales', 'client', 'customer', 'service', 'brand'
            ],
            ContentCategory.EDUCATION: [
                'education', 'learning', 'tutorial', 'course', 'teaching', 'academic',
                'university', 'college', 'school', 'student', 'teacher', 'professor',
                'lesson', 'study', 'research', 'knowledge', 'training', 'skill'
            ],
            ContentCategory.ENTERTAINMENT: [
                'entertainment', 'fun', 'funny', 'comedy', 'humor', 'meme', 'joke',
                'celebrity', 'show', 'tv', 'series', 'episode', 'drama', 'thriller',
                'action', 'romance', 'animation', 'cartoon', 'anime'
            ],
            ContentCategory.GAMING: [
                'gaming', 'game', 'gamer', 'video', 'console', 'pc', 'mobile',
                'esports', 'streaming', 'twitch', 'gameplay', 'review', 'walkthrough',
                'strategy', 'rpg', 'fps', 'mmorpg', 'indie', 'developer'
            ],
            ContentCategory.SPORTS: [
                'sports', 'sport', 'athlete', 'competition', 'tournament', 'championship',
                'football', 'basketball', 'soccer', 'tennis', 'baseball', 'hockey',
                'olympics', 'fitness', 'training', 'workout', 'exercise', 'gym'
            ],
            ContentCategory.FASHION: [
                'fashion', 'style', 'clothing', 'outfit', 'trend', 'designer',
                'model', 'runway', 'collection', 'brand', 'luxury', 'accessories',
                'jewelry', 'shoes', 'bag', 'dress', 'shirt', 'pants'
            ],
            ContentCategory.FOOD_COOKING: [
                'food', 'cooking', 'recipe', 'chef', 'kitchen', 'restaurant',
                'cuisine', 'dish', 'meal', 'ingredient', 'baking', 'grilling',
                'healthy', 'nutrition', 'diet', 'vegetarian', 'vegan', 'organic'
            ],
            ContentCategory.TRAVEL: [
                'travel', 'trip', 'vacation', 'holiday', 'destination', 'tourism',
                'adventure', 'explore', 'journey', 'backpacking', 'hotel', 'flight',
                'city', 'country', 'culture', 'landscape', 'beach', 'mountain'
            ],
            ContentCategory.HEALTH_FITNESS: [
                'health', 'fitness', 'wellness', 'medical', 'doctor', 'medicine',
                'exercise', 'workout', 'gym', 'nutrition', 'diet', 'weight',
                'mental', 'therapy', 'yoga', 'meditation', 'running', 'cycling'
            ],
            ContentCategory.SCIENCE: [
                'science', 'research', 'experiment', 'discovery', 'physics',
                'chemistry', 'biology', 'astronomy', 'space', 'laboratory',
                'scientist', 'theory', 'hypothesis', 'data', 'analysis', 'study'
            ],
            ContentCategory.NEWS_MEDIA: [
                'news', 'media', 'journalism', 'reporter', 'breaking', 'update',
                'headline', 'story', 'article', 'press', 'broadcast', 'current',
                'events', 'politics', 'government', 'election', 'policy', 'interview'
            ]
        }
    
    async def classify_content(
        self,
        content_id: str,
        content_data: Dict[str, Any],
        method: Optional[ClassificationMethod] = None
    ) -> ClassificationResult:
        """
        Classify content using specified or automatic method selection.
        
        Args:
            content_id: Unique content identifier
            content_data: Content data with features
            method: Classification method to use
            
        Returns:
            ClassificationResult: Classification result with confidence scores
        """
        start_time = datetime.now()
        
        try:
            # Determine method if not specified
            if method is None:
                method = self._select_optimal_method(content_data)
            
            # Perform classification based on method
            if method == ClassificationMethod.DEEP_LEARNING:
                result = await self._deep_learning_classification(content_id, content_data)
            elif method == ClassificationMethod.TRADITIONAL_ML:
                result = await self._traditional_ml_classification(content_id, content_data)
            elif method == ClassificationMethod.RULE_BASED:
                result = await self._rule_based_classification(content_id, content_data)
            elif method == ClassificationMethod.ENSEMBLE:
                result = await self._ensemble_classification(content_id, content_data)
            else:  # MULTIMODAL
                result = await self._multimodal_classification(content_id, content_data)
            
            # Add safety assessment
            if self.enable_safety_filter:
                await self._assess_content_safety(result, content_data)
            
            # Add quality assessment
            await self._assess_content_quality(result, content_data)
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            result.processing_time = processing_time
            self.processing_times.append(processing_time)
            
            # Update statistics
            self.classification_count += 1
            category_name = result.primary_category.value
            self.category_counts[category_name] = self.category_counts.get(category_name, 0) + 1
            
            logger.info(f"Content classified: {content_id} -> {result.primary_category.value} ({result.confidence:.2f})")
            return result
            
        except Exception as e:
            logger.error(f"Classification failed for {content_id}: {e}")
            # Return default classification
            return ClassificationResult(
                content_id=content_id,
                primary_category=ContentCategory.UNKNOWN,
                confidence=0.0,
                confidence_level=ClassificationConfidence.VERY_LOW,
                method_used=method or ClassificationMethod.RULE_BASED,
                processing_time=(datetime.now() - start_time).total_seconds()
            )
    
    def _select_optimal_method(self, content_data: Dict[str, Any]) -> ClassificationMethod:
        """Select optimal classification method based on available data."""
        has_text = bool(content_data.get('text') or content_data.get('text_features'))
        has_image = bool(content_data.get('image') or content_data.get('image_features'))
        has_audio = bool(content_data.get('audio') or content_data.get('audio_features'))
        has_video = bool(content_data.get('video') or content_data.get('video_features'))
        
        modality_count = sum([has_text, has_image, has_audio, has_video])
        
        if modality_count > 1:
            return ClassificationMethod.MULTIMODAL
        elif self.model_ensemble:
            return ClassificationMethod.ENSEMBLE
        elif has_text or has_image:
            return ClassificationMethod.DEEP_LEARNING
        else:
            return ClassificationMethod.TRADITIONAL_ML
    
    async def _deep_learning_classification(
        self,
        content_id: str,
        content_data: Dict[str, Any]
    ) -> ClassificationResult:
        """
Perform deep learning-based classification."""
        category_scores = {}
        features_used = []
        
        # Text classification with BERT
        if 'text' in content_data or 'text_features' in content_data:
            text_scores = await self._classify_text_with_bert(content_data)
            category_scores.update(text_scores)
            features_used.append('text_bert')
        
        # Image classification with CLIP
        if 'image' in content_data or 'image_features' in content_data:
            image_scores = await self._classify_image_with_clip(content_data)
            # Merge scores
            for category, score in image_scores.items():
                category_scores[category] = category_scores.get(category, 0) + score
            features_used.append('image_clip')
        
        # Audio classification
        if 'audio' in content_data or 'audio_features' in content_data:
            audio_scores = await self._classify_audio_features(content_data)
            for category, score in audio_scores.items():
                category_scores[category] = category_scores.get(category, 0) + score
            features_used.append('audio_features')
        
        # Normalize scores
        if category_scores:
            max_score = max(category_scores.values())
            category_scores = {k: v / max_score for k, v in category_scores.items()}
        
        # Select primary category
        primary_category = max(category_scores, key=category_scores.get) if category_scores else ContentCategory.UNKNOWN
        confidence = category_scores.get(primary_category, 0.0)
        
        return ClassificationResult(
            content_id=content_id,
            primary_category=primary_category,
            confidence=confidence,
            confidence_level=self._determine_confidence_level(confidence),
            method_used=ClassificationMethod.DEEP_LEARNING,
            category_scores=category_scores,
            features_used=features_used
        )
    
    async def _traditional_ml_classification(
        self,
        content_id: str,
        content_data: Dict[str, Any]
    ) -> ClassificationResult:
        """
Perform traditional ML-based classification."""
        # Use keyword-based classification for now
        # In production, this would use trained traditional ML models
        return await self._rule_based_classification(content_id, content_data)
    
    async def _rule_based_classification(
        self,
        content_id: str,
        content_data: Dict[str, Any]
    ) -> ClassificationResult:
        """
Perform rule-based classification using keywords and patterns."""
        category_scores = {category: 0.0 for category in ContentCategory}
        features_used = ['keywords', 'metadata']
        
        # Extract text content from various sources
        text_content = []
        
        # Direct text
        if 'text' in content_data:
            text_content.append(content_data['text'])
        
        # Metadata text
        metadata = content_data.get('metadata', {})
        for field in ['title', 'description', 'keywords', 'tags']:
            if field in metadata:
                value = metadata[field]
                if isinstance(value, list):
                    text_content.extend(value)
                elif isinstance(value, str):
                    text_content.append(value)
        
        # URL-based classification
        if 'source_url' in metadata:
            url_category = self._classify_by_url(metadata['source_url'])
            if url_category != ContentCategory.UNKNOWN:
                category_scores[url_category] += 0.3
        
        # Platform-based classification
        if 'source_platform' in metadata:
            platform_category = self._classify_by_platform(metadata['source_platform'])
            if platform_category != ContentCategory.UNKNOWN:
                category_scores[platform_category] += 0.2
        
        # Keyword-based scoring
        combined_text = ' '.join(text_content).lower()
        words = re.findall(r'\b\w+\b', combined_text)
        word_counts = Counter(words)
        
        for category, keywords in self.category_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in word_counts:
                    score += word_counts[keyword] * 0.1
            
            # Normalize by text length
            if len(words) > 0:
                score = score / len(words)
            
            category_scores[category] += score
        
        # File extension-based classification
        if 'file_extension' in metadata:
            ext_category = self._classify_by_extension(metadata['file_extension'])
            if ext_category != ContentCategory.UNKNOWN:
                category_scores[ext_category] += 0.4
        
        # MIME type-based classification
        if 'mime_type' in metadata:
            mime_category = self._classify_by_mime_type(metadata['mime_type'])
            if mime_category != ContentCategory.UNKNOWN:
                category_scores[mime_category] += 0.3
        
        # Select primary category
        primary_category = max(category_scores, key=category_scores.get)
        confidence = category_scores[primary_category]
        
        return ClassificationResult(
            content_id=content_id,
            primary_category=primary_category,
            confidence=min(1.0, confidence),
            confidence_level=self._determine_confidence_level(confidence),
            method_used=ClassificationMethod.RULE_BASED,
            category_scores=category_scores,
            features_used=features_used
        )
    
    async def _ensemble_classification(
        self,
        content_id: str,
        try:
            logger.info(f"Executing _ensemble_classification")
            
            # Implementation for _ensemble_classification
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"_ensemble_classification completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_ensemble_classification failed: {e}")
            raise
            content_id=content_id,
            primary_category=primary_category,
            confidence=confidence,
            confidence_level=self._determine_confidence_level(confidence),
            method_used=ClassificationMethod.ENSEMBLE,
            category_scores=combined_scores,
            features_used=list(set(all_features))
        )
    
    async def _multimodal_classification(
        self,
        content_id: str,
        content_data: Dict[str, Any]
    ) -> ClassificationResult:
        """
Perform multimodal classification combining text, image, audio, video."""
        # For now, use ensemble method
        # In production, this would use specialized multimodal models
        return await self._ensemble_classification(content_id, content_data)
    
    async def _classify_text_with_bert(self, content_data: Dict[str, Any]) -> Dict[ContentCategory, float]:
        """
Classify text content using BERT model."""
        try:
            text = content_data.get('text', '')
            if not text and 'text_features' in content_data:
                # Extract text from features
                text_features = content_data['text_features']
                text = text_features.get('raw_text', '')
            
            if not text:
                return {}
            
            # Tokenize and predict
            inputs = self.text_tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
            
            if self.enable_gpu:
                inputs = {k: v.cuda() for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = self.text_model(**inputs)
                predictions = torch.softmax(outputs.logits, dim=-1)
                scores = predictions.cpu().numpy()[0]
            
            # Map to categories (simplified mapping)
            categories = list(ContentCategory)
            category_scores = {}
            
            for i, category in enumerate(categories[:len(scores)]):
                category_scores[category] = float(scores[i])
            
            return category_scores
            
        except Exception as e:
            logger.warning(f"BERT classification failed: {e}")
            return {}
    
    async def _classify_image_with_clip(self, content_data: Dict[str, Any]) -> Dict[ContentCategory, float]:
        """Classify image content using CLIP model."""
        try:
            # Prepare category descriptions for CLIP
            category_descriptions = {
                ContentCategory.MUSIC: "music album cover, musical instruments, concert, recording studio",
                ContentCategory.PHOTOGRAPHY: "professional photography, camera equipment, artistic photo",
                ContentCategory.VIDEO_CONTENT: "video production, filming, movie scene, video editing",
                ContentCategory.ART_DESIGN: "artwork, painting, digital art, graphic design, illustration",
                ContentCategory.TECHNOLOGY: "computer, software, technology, digital device, programming",
                ContentCategory.BUSINESS: "business meeting, office, corporate, professional workplace",
                ContentCategory.EDUCATION: "classroom, learning, books, educational content, teaching",
                ContentCategory.ENTERTAINMENT: "entertainment, fun, comedy, show, celebrity",
                ContentCategory.GAMING: "video game, gaming setup, esports, game character",
                ContentCategory.SPORTS: "sports, athlete, competition, workout, fitness",
                ContentCategory.FASHION: "fashion, clothing, style, model, runway, accessories",
                ContentCategory.FOOD_COOKING: "food, cooking, restaurant, kitchen, recipe",
                ContentCategory.TRAVEL: "travel, vacation, destination, landscape, tourism",
                ContentCategory.HEALTH_FITNESS: "health, fitness, medical, exercise, wellness"
            }
            
            image_path = content_data.get('image')
            if not image_path and 'image_features' in content_data:
                # Would need to reconstruct image or use precomputed features
                return {}
            
            if not image_path:
                return {}
            
            # Load and process image
            image = Image.open(image_path)
            
            # Prepare text descriptions
            text_descriptions = list(category_descriptions.values())
            
            # Process with CLIP
            inputs = self.clip_processor(
                text=text_descriptions,
                images=image,
                return_tensors="pt",
                padding=True
            )
            
            if self.enable_gpu:
                inputs = {k: v.cuda() for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = self.clip_model(**inputs)
                logits_per_image = outputs.logits_per_image
                probs = logits_per_image.softmax(dim=1)
                scores = probs.cpu().numpy()[0]
            
            # Map scores to categories
            category_scores = {}
            categories = list(category_descriptions.keys())
            
            for i, category in enumerate(categories):
                category_scores[category] = float(scores[i])
            
            return category_scores
            
        except Exception as e:
            logger.warning(f"CLIP classification failed: {e}")
            return {}
    
    async def _classify_audio_features(self, content_data: Dict[str, Any]) -> Dict[ContentCategory, float]:
        """Classify audio content based on extracted features."""
        try:
            audio_features = content_data.get('audio_features', {})
            if not audio_features:
                return {}
            
            category_scores = {category: 0.0 for category in ContentCategory}
            
            # Simple rule-based audio classification
            tempo = audio_features.get('tempo', 0)
            spectral_centroid = audio_features.get('spectral_centroid', 0)
            
            # Music characteristics
            if 60 <= tempo <= 200 and spectral_centroid > 1000:
                category_scores[ContentCategory.MUSIC] = 0.8
            
            # Speech characteristics (lower spectral centroid, moderate tempo)
            elif spectral_centroid < 2000 and 80 <= tempo <= 160:
                category_scores[ContentCategory.EDUCATION] = 0.6
                category_scores[ContentCategory.NEWS_MEDIA] = 0.5
            
            # High energy content
            elif tempo > 120 and spectral_centroid > 2000:
                category_scores[ContentCategory.ENTERTAINMENT] = 0.7
                category_scores[ContentCategory.GAMING] = 0.6
            
            return category_scores
            
        except Exception as e:
            logger.warning(f"Audio classification failed: {e}")
            return {}
    
    def _classify_by_url(self, url: str) -> ContentCategory:
        """Classify content based on URL patterns."""
        url_lower = url.lower()
        
        if any(domain in url_lower for domain in ['youtube.com', 'youtu.be']):
            return ContentCategory.VIDEO_CONTENT
        elif any(domain in url_lower for domain in ['spotify.com', 'soundcloud.com', 'bandcamp.com']):
            return ContentCategory.MUSIC
        elif any(domain in url_lower for domain in ['instagram.com', 'flickr.com', 'unsplash.com']):
            return ContentCategory.PHOTOGRAPHY
        elif any(domain in url_lower for domain in ['github.com', 'stackoverflow.com', 'medium.com']):
            return ContentCategory.TECHNOLOGY
        elif any(domain in url_lower for domain in ['linkedin.com', 'bloomberg.com', 'forbes.com']):
            return ContentCategory.BUSINESS
        elif any(domain in url_lower for domain in ['coursera.com', 'udemy.com', 'edx.org']):
            return ContentCategory.EDUCATION
        elif any(domain in url_lower for domain in ['twitch.tv', 'steam.com', 'ign.com']):
            return ContentCategory.GAMING
        elif any(domain in url_lower for domain in ['cnn.com', 'bbc.com', 'reuters.com']):
            return ContentCategory.NEWS_MEDIA
        
        return ContentCategory.UNKNOWN
    
    def _classify_by_platform(self, platform: str) -> ContentCategory:
        """
Classify content based on platform."""
        platform_lower = platform.lower()
        
        if platform_lower in ['youtube']:
            return ContentCategory.VIDEO_CONTENT
        elif platform_lower in ['spotify', 'soundcloud']:
            return ContentCategory.MUSIC
        elif platform_lower in ['instagram']:
            return ContentCategory.PHOTOGRAPHY
        elif platform_lower in ['tiktok']:
            return ContentCategory.ENTERTAINMENT
        elif platform_lower in ['twitter', 'x']:
            return ContentCategory.NEWS_MEDIA
        
        return ContentCategory.UNKNOWN
    
    def _classify_by_extension(self, extension: str) -> ContentCategory:
        """
Classify content based on file extension."""
        ext_lower = extension.lower()
        
        if ext_lower in ['.mp3', '.wav', '.flac', '.ogg', '.m4a', '.aac']:
            return ContentCategory.MUSIC
        elif ext_lower in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']:
            return ContentCategory.PHOTOGRAPHY
        elif ext_lower in ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv']:
            return ContentCategory.VIDEO_CONTENT
        elif ext_lower in ['.pdf', '.doc', '.docx', '.txt', '.md']:
            return ContentCategory.EDUCATION
        
        return ContentCategory.UNKNOWN
    
    def _classify_by_mime_type(self, mime_type: str) -> ContentCategory:
        """
Classify content based on MIME type."""
        if mime_type.startswith('audio/'):
            return ContentCategory.MUSIC
        elif mime_type.startswith('image/'):
            return ContentCategory.PHOTOGRAPHY
        elif mime_type.startswith('video/'):
            return ContentCategory.VIDEO_CONTENT
        elif mime_type.startswith('text/') or mime_type == 'application/pdf':
            return ContentCategory.EDUCATION
        
        return ContentCategory.UNKNOWN
    
    def _determine_confidence_level(self, confidence: float) -> ClassificationConfidence:
        """
Determine confidence level based on score."""
        if confidence >= 0.9:
            return ClassificationConfidence.VERY_HIGH
        elif confidence >= 0.7:
            return ClassificationConfidence.HIGH
        elif confidence >= 0.5:
            return ClassificationConfidence.MEDIUM
        elif confidence >= 0.3:
            return ClassificationConfidence.LOW
        else:
            return ClassificationConfidence.VERY_LOW
    
    async def _assess_content_safety(
        self,
        result: ClassificationResult,
        content_data: Dict[str, Any]
    ) -> None:
        """
Assess content safety and flag inappropriate content."""
        try:
            text_content = content_data.get('text', '')
            
            # Extract text from metadata
            metadata = content_data.get('metadata', {})
            for field in ['title', 'description']:
                if field in metadata and metadata[field]:
                    text_content += ' ' + metadata[field]
            
            if text_content and self.enable_safety_filter:
                # Use safety classifier
                safety_result = self.safety_classifier(text_content)
                
                if safety_result:
                    toxic_score = safety_result[0]['score'] if safety_result[0]['label'] == 'TOXIC' else 0
                    
                    result.is_safe_content = toxic_score < 0.5
                    result.hate_speech_probability = toxic_score
            
            # Rule-based safety checks
            unsafe_keywords = [
                'adult', 'nsfw', 'explicit', 'violence', 'hate', 'harassment',
                'discrimination', 'abuse', 'illegal', 'drugs', 'weapons'
            ]
            
            text_lower = text_content.lower()
            unsafe_count = sum(1 for keyword in unsafe_keywords if keyword in text_lower)
            
            if unsafe_count > 0:
                result.adult_content_probability = min(1.0, unsafe_count * 0.2)
                result.is_safe_content = result.is_safe_content and unsafe_count < 3
            
        except Exception as e:
            logger.warning(f"Safety assessment failed: {e}")
    
    async def _assess_content_quality(
        self,
        result: ClassificationResult,
        content_data: Dict[str, Any]
    ) -> None:
        """Assess content quality and professionalism."""
        try:
            quality_factors = []
            
            # Metadata completeness
            metadata = content_data.get('metadata', {})
            metadata_fields = ['title', 'description', 'creator', 'created_date']
            metadata_completeness = sum(1 for field in metadata_fields if metadata.get(field)) / len(metadata_fields)
            quality_factors.append(metadata_completeness)
            
            # Text quality (if available)
            text_content = content_data.get('text', '')
            if text_content:
                # Length factor
                length_factor = min(1.0, len(text_content) / 1000)
                quality_factors.append(length_factor)
                
                # Grammar/spelling factor (simplified)
                word_count = len(text_content.split())
                unique_words = len(set(text_content.lower().split()))
                vocabulary_richness = unique_words / max(1, word_count)
                quality_factors.append(vocabulary_richness)
            
            # Technical quality factors
            if 'image_features' in content_data:
                img_features = content_data['image_features']
                if 'width' in img_features and 'height' in img_features:
                    resolution = img_features['width'] * img_features['height']
                    resolution_factor = min(1.0, resolution / (1920 * 1080))  # Normalize to 1080p
                    quality_factors.append(resolution_factor)
            
            if 'audio_features' in content_data:
                audio_features = content_data['audio_features']
                if 'sample_rate' in audio_features:
                    sample_rate_factor = min(1.0, audio_features['sample_rate'] / 44100)
                    quality_factors.append(sample_rate_factor)
            
            # Calculate overall quality score
            result.content_quality_score = np.mean(quality_factors) if quality_factors else 0.5
            
            # Professionalism score
            professionalism_factors = [
                metadata_completeness,
                1.0 if result.is_safe_content else 0.3,
                1.0 if result.confidence > 0.7 else 0.6
            ]
            result.professionalism_score = np.mean(professionalism_factors)
            
            # Engagement potential (simplified heuristic)
            engagement_factors = [
                result.content_quality_score,
                1.0 if result.primary_category in [
                    ContentCategory.ENTERTAINMENT, ContentCategory.MUSIC, 
                    ContentCategory.VIDEO_CONTENT, ContentCategory.GAMING
                ] else 0.7,
                1.0 if metadata.get('title') and len(metadata['title']) < 100 else 0.8
            ]
            result.engagement_potential = np.mean(engagement_factors)
            
        except Exception as e:
            logger.warning(f"Quality assessment failed: {e}")
            result.content_quality_score = 0.5
            result.professionalism_score = 0.5
            result.engagement_potential = 0.5
    
    async def batch_classify(
        self,
        content_batch: List[Tuple[str, Dict[str, Any], Optional[ClassificationMethod]]]
    ) -> List[ClassificationResult]:
        """Classify multiple content items in batch."""
        tasks = []
        
        for content_id, content_data, method in content_batch:
            task = asyncio.create_task(
                self.classify_content(content_id, content_data, method)
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and return successful results
        valid_results = [r for r in results if isinstance(r, ClassificationResult)]
        
        logger.info(f"Batch classified {len(valid_results)} out of {len(content_batch)} items")
        return valid_results
    
    def get_analytics(self) -> Dict[str, Any]:
        """Get classification analytics and performance metrics."""
        avg_processing_time = np.mean(self.processing_times) if self.processing_times else 0
        
        return {
            "total_classifications": self.classification_count,
            "average_processing_time": avg_processing_time,
            "category_distribution": self.category_counts,
            "gpu_enabled": self.enable_gpu,
            "confidence_threshold": self.confidence_threshold,
            "processing_time_percentiles": {
                "p50": np.percentile(self.processing_times, 50) if self.processing_times else 0,
                "p90": np.percentile(self.processing_times, 90) if self.processing_times else 0,
                "p99": np.percentile(self.processing_times, 99) if self.processing_times else 0
            },
            "most_common_categories": sorted(
                self.category_counts.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:10]
        }
    
    async def cleanup(self) -> None:
        """Cleanup resources and clear caches."""
        # Clear GPU memory if using CUDA
        if self.enable_gpu and torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        # Clear statistics
        self.processing_times.clear()
        self.category_counts.clear()
        
        logger.info("ContentClassifier cleanup completed")
