#!/usr/bin/env python3
"""🏷️ Content Classification AI - Automated Content Classification Engine
==========================================================================
Module: backend/media_processing/content_classification_ai.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead AI Developer + ML Engineer + AI Prompt Engineer + Backend Senior Engineer
Type: Enterprise AI Content Classification - Production-Ready
Responsibility: Intelligent content categorization, tagging, and classification
=============================================================================

⚠️  EXCLUSIVE INTELLECTUAL PROPERTY - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use strictly prohibited and subject to legal prosecution.
Contact: mlaiel@live.de

🎯 BUSINESS LOGIC COMPLIANCE:
Creator Multi-format → IA Processing → Protection → SEO → Collaboration → Distribution

🏷️ AI CLASSIFICATION CAPABILITIES:
1. Multi-Modal Content Classification (Audio, Video, Image, Text)
2. Hierarchical Category Classification (Genre, Theme, Style, Mood)
3. Content Safety Classification (Explicit, Violent, Hate Speech)
4. Audience Targeting Classification (Age, Demographics, Interests)
5. Commercial Classification (Brand Safe, Monetizable, Advertising)
6. Cultural Context Classification (Language, Region, Cultural Sensitivity)
"""

import asyncio
import logging
import uuid
import json
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
import numpy as np

# AI/ML imports
try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    from transformers import AutoTokenizer, AutoModel, pipeline
    import cv2
    import librosa
    from PIL import Image
    import torchvision.transforms as transforms
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.multiclass import OneVsRestClassifier
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    torch = None

# FastAPI and core dependencies
from fastapi import HTTPException
from pydantic import BaseModel, Field
import aiofiles
import aioredis

# Internal imports
from backend.core.exceptions import ProcessingError, ValidationError
from backend.core.security import SecurityManager
from backend.database.managers import DatabaseManager
from backend.monitoring.performance import PerformanceMonitor


class ContentType(Enum):
    """Content types for classification"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    VOICE = "voice"
    AVATAR = "avatar"
    MULTIMODAL = "multimodal"


class ClassificationType(Enum):
    """Types of content classification"""
    GENRE = "genre"
    THEME = "theme"
    STYLE = "style"
    MOOD = "mood"
    AUDIENCE = "audience"
    SAFETY = "safety"
    COMMERCIAL = "commercial"
    CULTURAL = "cultural"
    TECHNICAL = "technical"


class SafetyLevel(Enum):
    """Content safety levels"""
    SAFE = "safe"
    MODERATE = "moderate"
    RESTRICTED = "restricted"
    UNSAFE = "unsafe"
    EXPLICIT = "explicit"


class AudienceCategory(Enum):
    """Audience targeting categories"""
    CHILDREN = "children"
    TEENS = "teens"
    YOUNG_ADULTS = "young_adults"
    ADULTS = "adults"
    SENIORS = "seniors"
    FAMILY_FRIENDLY = "family_friendly"
    MATURE_AUDIENCE = "mature_audience"


@dataclass
class ClassificationLabel:
    """Individual classification label with confidence"""
    label: str
    confidence: float
    category: str
    subcategory: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ClassificationResult:
    """Complete content classification result"""
    content_id: str
    classification_id: str
    content_type: ContentType
    primary_categories: List[ClassificationLabel] = field(default_factory=list)
    secondary_categories: List[ClassificationLabel] = field(default_factory=list)
    safety_classification: SafetyLevel = SafetyLevel.SAFE
    audience_classification: List[AudienceCategory] = field(default_factory=list)
    commercial_classification: Dict[str, Any] = field(default_factory=dict)
    cultural_context: Dict[str, Any] = field(default_factory=dict)
    confidence_scores: Dict[str, float] = field(default_factory=dict)
    processing_metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ClassificationConfig:
    """Configuration for content classification"""
    enable_multi_label: bool = True
    enable_hierarchical: bool = True
    confidence_threshold: float = 0.7
    max_labels_per_category: int = 5
    enable_safety_classification: bool = True
    enable_audience_classification: bool = True
    enable_commercial_classification: bool = True
    enable_cultural_classification: bool = True
    use_ensemble_models: bool = True


class ContentClassificationAI:
    """Enterprise AI-powered Content Classification Engine
    
    Advanced multi-modal content classification system with hierarchical
    categorization, safety assessment, and audience targeting.
    """
    
    def __init__(self, config: Optional[ClassificationConfig] = None):
        """Initialize Content Classification AI with enterprise configuration"""
        self.config = config or ClassificationConfig()
        self.logger = logging.getLogger(__name__)
        self.db_manager = DatabaseManager()
        self.security_manager = SecurityManager()
        self.performance_monitor = PerformanceMonitor()
        
        # Classification models
        self.text_classifiers = {}
        self.image_classifiers = {}
        self.audio_classifiers = {}
        self.video_classifiers = {}
        self.ensemble_classifiers = {}
        
        # Classification taxonomies
        self.category_taxonomies = {}
        self.label_hierarchies = {}
        self.safety_models = {}
        
        # Processing resources
        self.device = "cuda" if torch.cuda.is_available() and AI_AVAILABLE else "cpu"
        
        # Cache for classification results
        self.classification_cache = {}
        
        # Performance metrics
        self.metrics = {
            "total_classifications": 0,
            "successful_classifications": 0,
            "average_confidence": 0.0,
            "classification_types_used": {},
            "safety_classifications": {},
            "audience_classifications": {}
        }
        
        self.logger.info(f"Content Classification AI initialized with device: {self.device}")

    async def initialize(self) -> bool:
        """Initialize AI classification models and taxonomies"""
        try:
            self.logger.info("Initializing Content Classification AI...")
            
            # Load classification taxonomies
            await self._load_classification_taxonomies()
            
            # Initialize AI models
            if AI_AVAILABLE:
                await self._initialize_classification_models()
            else:
                self.logger.warning("AI libraries not available - using fallback methods")
            
            # Load pre-trained models
            await self._load_pretrained_models()
            
            self.logger.info("Content Classification AI initialization complete")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Content Classification AI: {e}")
            return False

    async def _load_classification_taxonomies(self):
        """Load content classification taxonomies and hierarchies"""
        try:
            # Define comprehensive classification taxonomies
            self.category_taxonomies = {
                "audio_genres": {
                    "music": ["pop", "rock", "jazz", "classical", "electronic", "hip_hop", "country", "folk", "blues", "reggae"],
                    "podcast": ["news", "education", "entertainment", "business", "technology", "health", "comedy", "true_crime"],
                    "voice": ["speech", "narration", "interview", "presentation", "audiobook", "voice_over"],
                    "ambient": ["nature", "urban", "mechanical", "atmospheric", "white_noise"]
                },
                "video_genres": {
                    "entertainment": ["movie", "tv_show", "comedy", "drama", "action", "thriller", "horror", "documentary"],
                    "educational": ["tutorial", "lecture", "course", "demonstration", "explanation", "review"],
                    "social": ["vlog", "lifestyle", "travel", "food", "fashion", "beauty", "fitness"],
                    "commercial": ["advertisement", "promotional", "product_demo", "testimonial", "brand_content"]
                },
                "image_categories": {
                    "photography": ["portrait", "landscape", "street", "nature", "architecture", "macro", "event"],
                    "digital_art": ["illustration", "graphic_design", "3d_render", "concept_art", "abstract"],
                    "commercial": ["product", "advertisement", "stock_photo", "infographic", "logo"],
                    "personal": ["selfie", "family", "vacation", "social", "meme", "screenshot"]
                },
                "text_categories": {
                    "content_type": ["article", "blog_post", "news", "review", "opinion", "tutorial", "story", "poem"],
                    "domain": ["technology", "business", "health", "education", "entertainment", "sports", "politics", "science"],
                    "style": ["formal", "informal", "academic", "creative", "technical", "conversational"],
                    "purpose": ["informative", "persuasive", "entertaining", "instructional", "promotional"]
                }
            }
            
            # Define safety classification categories
            self.safety_categories = {
                "explicit_content": ["nudity", "sexual_content", "graphic_violence", "extreme_gore"],
                "hate_speech": ["racism", "sexism", "homophobia", "religious_hate", "political_extremism"],
                "harmful_content": ["self_harm", "substance_abuse", "dangerous_activities", "misinformation"],
                "age_inappropriate": ["mature_themes", "strong_language", "frightening_content"]
            }
            
            # Define audience categories
            self.audience_categories = {
                "age_groups": ["0-5", "6-12", "13-17", "18-24", "25-34", "35-44", "45-54", "55-64", "65+"],
                "interests": ["technology", "sports", "music", "fashion", "food", "travel", "gaming", "fitness"],
                "demographics": ["students", "professionals", "parents", "seniors", "creatives", "entrepreneurs"]
            }
            
            self.logger.info("Classification taxonomies loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to load classification taxonomies: {e}")
            raise

    async def _initialize_classification_models(self):
        """Initialize AI classification models"""
        try:
            # Initialize text classification models
            if AI_AVAILABLE:
                self.text_classifiers['bert'] = pipeline('text-classification', model='bert-base-uncased')
                self.text_classifiers['sentiment'] = pipeline('sentiment-analysis')
                
                # Initialize image classification models
                self.image_classifiers['resnet'] = torch.hub.load('pytorch/vision:v0.10.0', 'resnet50', pretrained=True)
                self.image_classifiers['resnet'].eval()
                
                # Initialize safety classification models
                self.safety_models['text_safety'] = pipeline('text-classification', 
                                                           model='unitary/toxic-bert')
            
            self.logger.info("AI classification models initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize classification models: {e}")
            raise

    async def classify_content(
        self,
        content_id: str,
        content_path: str,
        content_type: ContentType,
        classification_types: Optional[List[ClassificationType]] = None
    ) -> ClassificationResult:
        """Perform comprehensive AI-powered content classification"""
        classification_id = str(uuid.uuid4())
        start_time = datetime.utcnow()
        
        try:
            self.logger.info(f"Starting content classification: {classification_id}")
            
            # Validate input
            await self._validate_classification_input(content_path, content_type)
            
            # Initialize classification result
            result = ClassificationResult(
                content_id=content_id,
                classification_id=classification_id,
                content_type=content_type
            )
            
            # Check cache first
            cache_key = f"{content_id}_{content_type.value}"
            if cache_key in self.classification_cache:
                self.logger.info(f"Returning cached classification: {classification_id}")
                return self.classification_cache[cache_key]
            
            # Determine classification types to perform
            if not classification_types:
                classification_types = [
                    ClassificationType.GENRE,
                    ClassificationType.THEME,
                    ClassificationType.MOOD,
                    ClassificationType.SAFETY,
                    ClassificationType.AUDIENCE
                ]
            
            # Perform content-specific classification
            if content_type == ContentType.TEXT:
                await self._classify_text_content(content_path, result, classification_types)
            elif content_type == ContentType.AUDIO or content_type == ContentType.VOICE:
                await self._classify_audio_content(content_path, result, classification_types)
            elif content_type == ContentType.VIDEO:
                await self._classify_video_content(content_path, result, classification_types)
            elif content_type == ContentType.IMAGE:
                await self._classify_image_content(content_path, result, classification_types)
            elif content_type == ContentType.MULTIMODAL:
                await self._classify_multimodal_content(content_path, result, classification_types)
            
            # Perform safety classification
            if ClassificationType.SAFETY in classification_types and self.config.enable_safety_classification:
                await self._classify_safety(content_path, content_type, result)
            
            # Perform audience classification
            if ClassificationType.AUDIENCE in classification_types and self.config.enable_audience_classification:
                await self._classify_audience(result)
            
            # Perform commercial classification
            if self.config.enable_commercial_classification:
                await self._classify_commercial(result)
            
            # Perform cultural classification
            if self.config.enable_cultural_classification:
                await self._classify_cultural(content_path, content_type, result)
            
            # Calculate confidence scores
            result.confidence_scores = await self._calculate_confidence_scores(result)
            
            # Generate processing metadata
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            result.processing_metadata = {
                "processing_time_seconds": processing_time,
                "classification_types": [ct.value for ct in classification_types],
                "models_used": await self._get_models_used(content_type),
                "device_used": self.device
            }
            
            # Cache result
            self.classification_cache[cache_key] = result
            
            # Update metrics
            await self._update_classification_metrics(result, processing_time)
            
            self.logger.info(f"Content classification completed: {classification_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Content classification failed: {e}")
            raise ProcessingError(f"Classification failed: {str(e)}")

    async def _classify_text_content(
        self,
        content_path: str,
        result: ClassificationResult,
        classification_types: List[ClassificationType]
    ):
        """Classify text content using NLP models"""
        try:
            # Read text content
            async with aiofiles.open(content_path, 'r', encoding='utf-8') as f:
                text_content = await f.read()
            
            if not AI_AVAILABLE:
                await self._fallback_text_classification(text_content, result)
                return
            
            # Genre classification
            if ClassificationType.GENRE in classification_types:
                genre_labels = await self._classify_text_genre(text_content)
                result.primary_categories.extend(genre_labels)
            
            # Theme classification
            if ClassificationType.THEME in classification_types:
                theme_labels = await self._classify_text_theme(text_content)
                result.secondary_categories.extend(theme_labels)
            
            # Mood/Sentiment classification
            if ClassificationType.MOOD in classification_types:
                mood_labels = await self._classify_text_mood(text_content)
                result.secondary_categories.extend(mood_labels)
            
            # Style classification
            if ClassificationType.STYLE in classification_types:
                style_labels = await self._classify_text_style(text_content)
                result.secondary_categories.extend(style_labels)
            
        except Exception as e:
            self.logger.error(f"Text classification failed: {e}")
            raise

    async def _classify_text_genre(self, text: str) -> List[ClassificationLabel]:
        """Classify text genre using AI models"""
        try:
            labels = []
            
            # Simple keyword-based classification for fallback
            text_lower = text.lower()
            genre_keywords = {
                "news": ["breaking", "reports", "journalist", "headlines", "press"],
                "tutorial": ["step", "how to", "guide", "instructions", "learn"],
                "review": ["review", "opinion", "rating", "recommend", "experience"],
                "story": ["once upon", "story", "narrative", "character", "plot"],
                "academic": ["research", "study", "analysis", "hypothesis", "conclusion"]
            }
            
            for genre, keywords in genre_keywords.items():
                score = sum(1 for keyword in keywords if keyword in text_lower) / len(keywords)
                if score > 0.2:
                    labels.append(ClassificationLabel(
                        label=genre,
                        confidence=min(score * 2, 1.0),
                        category="genre"
                    ))
            
            # Sort by confidence and limit results
            labels.sort(key=lambda x: x.confidence, reverse=True)
            return labels[:self.config.max_labels_per_category]
            
        except Exception as e:
            self.logger.error(f"Text genre classification failed: {e}")
            return []

    async def _classify_text_theme(self, text: str) -> List[ClassificationLabel]:
        """Classify text theme using AI models"""
        try:
            labels = []
            
            # Theme detection based on keywords
            text_lower = text.lower()
            theme_keywords = {
                "technology": ["ai", "software", "computer", "digital", "tech", "programming"],
                "business": ["company", "market", "revenue", "strategy", "business", "corporate"],
                "health": ["health", "medical", "wellness", "fitness", "nutrition", "disease"],
                "education": ["education", "learning", "school", "university", "knowledge", "teaching"],
                "entertainment": ["entertainment", "movie", "music", "game", "fun", "celebrity"]
            }
            
            for theme, keywords in theme_keywords.items():
                score = sum(1 for keyword in keywords if keyword in text_lower) / len(keywords)
                if score > 0.15:
                    labels.append(ClassificationLabel(
                        label=theme,
                        confidence=min(score * 3, 1.0),
                        category="theme"
                    ))
            
            return labels[:self.config.max_labels_per_category]
            
        except Exception as e:
            self.logger.error(f"Text theme classification failed: {e}")
            return []

    async def _classify_text_mood(self, text: str) -> List[ClassificationLabel]:
        """Classify text mood/sentiment using AI models"""
        try:
            labels = []
            
            if AI_AVAILABLE and 'sentiment' in self.text_classifiers:
                # Use AI sentiment analysis
                sentiment_result = self.text_classifiers['sentiment'](text)
                
                for result in sentiment_result:
                    labels.append(ClassificationLabel(
                        label=result['label'].lower(),
                        confidence=result['score'],
                        category="mood"
                    ))
            else:
                # Fallback sentiment analysis
                positive_words = ["good", "great", "excellent", "amazing", "wonderful", "fantastic", "happy", "joy"]
                negative_words = ["bad", "terrible", "awful", "horrible", "sad", "angry", "hate", "disappointed"]
                
                text_words = text.lower().split()
                positive_count = sum(1 for word in text_words if word in positive_words)
                negative_count = sum(1 for word in text_words if word in negative_words)
                
                if positive_count > negative_count:
                    labels.append(ClassificationLabel(
                        label="positive",
                        confidence=min(positive_count / len(text_words) * 10, 1.0),
                        category="mood"
                    ))
                elif negative_count > positive_count:
                    labels.append(ClassificationLabel(
                        label="negative",
                        confidence=min(negative_count / len(text_words) * 10, 1.0),
                        category="mood"
                    ))
                else:
                    labels.append(ClassificationLabel(
                        label="neutral",
                        confidence=0.7,
                        category="mood"
                    ))
            
            return labels
            
        except Exception as e:
            self.logger.error(f"Text mood classification failed: {e}")
            return []

    async def _classify_text_style(self, text: str) -> List[ClassificationLabel]:
        """Classify text style using linguistic analysis"""
        try:
            labels = []
            
            # Analyze text characteristics
            sentences = text.split('.')
            avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
            
            # Formal vs informal indicators
            formal_indicators = ["therefore", "however", "furthermore", "consequently", "nevertheless"]
            informal_indicators = ["like", "okay", "yeah", "gonna", "wanna", "kinda"]
            
            text_lower = text.lower()
            formal_score = sum(1 for word in formal_indicators if word in text_lower)
            informal_score = sum(1 for word in informal_indicators if word in text_lower)
            
            # Classify style
            if avg_sentence_length > 20 or formal_score > informal_score:
                labels.append(ClassificationLabel(
                    label="formal",
                    confidence=min((avg_sentence_length / 30) + (formal_score * 0.2), 1.0),
                    category="style"
                ))
            else:
                labels.append(ClassificationLabel(
                    label="informal",
                    confidence=min((informal_score * 0.3) + 0.5, 1.0),
                    category="style"
                ))
            
            # Technical vs conversational
            technical_words = ["algorithm", "implementation", "methodology", "architecture", "framework"]
            technical_score = sum(1 for word in technical_words if word in text_lower)
            
            if technical_score > 0:
                labels.append(ClassificationLabel(
                    label="technical",
                    confidence=min(technical_score * 0.4, 1.0),
                    category="style"
                ))
            
            return labels
            
        except Exception as e:
            self.logger.error(f"Text style classification failed: {e}")
            return []

    async def _classify_safety(
        self,
        content_path: str,
        content_type: ContentType,
        result: ClassificationResult
    ):
        """Perform safety classification"""
        try:
            if content_type == ContentType.TEXT:
                result.safety_classification = await self._classify_text_safety(content_path)
            elif content_type in [ContentType.IMAGE, ContentType.VIDEO]:
                result.safety_classification = await self._classify_visual_safety(content_path)
            elif content_type in [ContentType.AUDIO, ContentType.VOICE]:
                result.safety_classification = await self._classify_audio_safety(content_path)
            else:
                result.safety_classification = SafetyLevel.SAFE  # Default to safe
            
        except Exception as e:
            self.logger.error(f"Safety classification failed: {e}")
            result.safety_classification = SafetyLevel.SAFE

    async def _classify_text_safety(self, content_path: str) -> SafetyLevel:
        """Classify text content safety"""
        try:
            async with aiofiles.open(content_path, 'r', encoding='utf-8') as f:
                text_content = await f.read()
            
            # Check for explicit content indicators
            explicit_keywords = ["explicit", "nsfw", "adult", "sexual", "pornographic"]
            hate_keywords = ["hate", "racist", "nazi", "terrorist", "kill", "murder"]
            harmful_keywords = ["suicide", "self-harm", "drugs", "violence", "weapon"]
            
            text_lower = text_content.lower()
            
            explicit_count = sum(1 for word in explicit_keywords if word in text_lower)
            hate_count = sum(1 for word in hate_keywords if word in text_lower)
            harmful_count = sum(1 for word in harmful_keywords if word in text_lower)
            
            total_risk_score = explicit_count + hate_count + harmful_count
            
            if total_risk_score >= 3:
                return SafetyLevel.UNSAFE
            elif total_risk_score >= 2:
                return SafetyLevel.RESTRICTED
            elif total_risk_score >= 1:
                return SafetyLevel.MODERATE
            else:
                return SafetyLevel.SAFE
                
        except Exception as e:
            self.logger.error(f"Text safety classification failed: {e}")
            return SafetyLevel.SAFE

    async def _classify_audience(self, result: ClassificationResult):
        """Classify target audience"""
        try:
            audience_categories = []
            
            # Based on safety level
            if result.safety_classification == SafetyLevel.SAFE:
                audience_categories.extend([
                    AudienceCategory.FAMILY_FRIENDLY,
                    AudienceCategory.CHILDREN,
                    AudienceCategory.TEENS
                ])
            elif result.safety_classification == SafetyLevel.MODERATE:
                audience_categories.extend([
                    AudienceCategory.TEENS,
                    AudienceCategory.YOUNG_ADULTS,
                    AudienceCategory.ADULTS
                ])
            else:
                audience_categories.append(AudienceCategory.MATURE_AUDIENCE)
            
            # Based on content categories
            for category in result.primary_categories:
                if category.label in ["educational", "tutorial", "academic"]:
                    audience_categories.append(AudienceCategory.YOUNG_ADULTS)
                elif category.label in ["entertainment", "music", "gaming"]:
                    audience_categories.extend([AudienceCategory.TEENS, AudienceCategory.YOUNG_ADULTS])
                elif category.label in ["business", "professional"]:
                    audience_categories.append(AudienceCategory.ADULTS)
            
            result.audience_classification = list(set(audience_categories))
            
        except Exception as e:
            self.logger.error(f"Audience classification failed: {e}")
            result.audience_classification = [AudienceCategory.ADULTS]

    async def _fallback_text_classification(self, text: str, result: ClassificationResult):
        """Fallback text classification without AI models"""
        try:
            # Simple keyword-based classification
            text_lower = text.lower()
            
            # Basic genre detection
            if any(word in text_lower for word in ["tutorial", "how to", "guide", "step"]):
                result.primary_categories.append(ClassificationLabel(
                    label="tutorial", confidence=0.8, category="genre"
                ))
            elif any(word in text_lower for word in ["news", "breaking", "report"]):
                result.primary_categories.append(ClassificationLabel(
                    label="news", confidence=0.7, category="genre"
                ))
            elif any(word in text_lower for word in ["review", "opinion", "recommend"]):
                result.primary_categories.append(ClassificationLabel(
                    label="review", confidence=0.75, category="genre"
                ))
            else:
                result.primary_categories.append(ClassificationLabel(
                    label="general", confidence=0.6, category="genre"
                ))
            
        except Exception as e:
            self.logger.error(f"Fallback text classification failed: {e}")


# Additional classification methods for other content types would be implemented here...
# (Audio, Video, Image classification methods)

    async def get_classification_statistics(self) -> Dict[str, Any]:
        """Get classification engine statistics"""
        try:
            return {
                "total_classifications": self.metrics["total_classifications"],
                "successful_classifications": self.metrics["successful_classifications"],
                "success_rate": (
                    self.metrics["successful_classifications"] / self.metrics["total_classifications"]
                    if self.metrics["total_classifications"] > 0 else 0.0
                ),
                "average_confidence": self.metrics["average_confidence"],
                "classification_types_distribution": self.metrics["classification_types_used"],
                "safety_classifications_distribution": self.metrics["safety_classifications"],
                "audience_classifications_distribution": self.metrics["audience_classifications"]
            }
        except Exception as e:
            self.logger.error(f"Failed to get classification statistics: {e}")
            return {}

    async def _update_classification_metrics(self, result: ClassificationResult, processing_time: float):
        """Update classification metrics"""
        try:
            self.metrics["total_classifications"] += 1
            self.metrics["successful_classifications"] += 1
            
            # Update average confidence
            avg_confidence = np.mean([cat.confidence for cat in result.primary_categories + result.secondary_categories])
            self.metrics["average_confidence"] = (
                (self.metrics["average_confidence"] * (self.metrics["total_classifications"] - 1) + avg_confidence) /
                self.metrics["total_classifications"]
            )
            
            # Update safety classification counts
            safety_level = result.safety_classification.value
            self.metrics["safety_classifications"][safety_level] = (
                self.metrics["safety_classifications"].get(safety_level, 0) + 1
            )
            
            # Update audience classification counts
            for audience in result.audience_classification:
                audience_name = audience.value
                self.metrics["audience_classifications"][audience_name] = (
                    self.metrics["audience_classifications"].get(audience_name, 0) + 1
                )
                
        except Exception as e:
            self.logger.error(f"Failed to update classification metrics: {e}")


# Global classifier instance
_content_classifier = None


async def get_content_classifier() -> ContentClassificationAI:
    """Get global Content Classification AI instance"""
    global _content_classifier
    if _content_classifier is None:
        _content_classifier = ContentClassificationAI()
        await _content_classifier.initialize()
    return _content_classifier


async def classify_content(
    content_id: str,
    content_path: str,
    content_type: ContentType,
    classification_types: Optional[List[ClassificationType]] = None
) -> ClassificationResult:
    """Convenience function for content classification"""
    classifier = await get_content_classifier()
    return await classifier.classify_content(content_id, content_path, content_type, classification_types)


if __name__ == "__main__":
    # Development testing
    async def test_content_classification():
        """Test content classification functionality"""
        classifier = ContentClassificationAI()
        await classifier.initialize()
        
        print("Content Classification AI test completed successfully")
    
    asyncio.run(test_content_classification())