"""
Content Classification Service - Enterprise Microservice
======================================================

Advanced AI-powered content classification and tagging system with multi-model
analysis, hierarchical categorization, and automated content organization.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING ⚠️
This code is proprietary and confidential. Unauthorized use, reproduction,
distribution, or modification is strictly prohibited and will be prosecuted
to the full extent of the law.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, field
from pydantic import BaseModel, Field
import json
import uuid
from collections import defaultdict
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContentType(str, Enum):
    """Content type classification."""
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    TEXT = "text"
    DOCUMENT = "document"
    MIXED_MEDIA = "mixed_media"


class ClassificationModel(str, Enum):
    """Available classification models."""
    VISUAL_CLASSIFIER = "visual_classifier"
    AUDIO_CLASSIFIER = "audio_classifier"
    TEXT_CLASSIFIER = "text_classifier"
    MULTI_MODAL_CLASSIFIER = "multi_modal_classifier"
    SENTIMENT_ANALYZER = "sentiment_analyzer"
    TOPIC_CLASSIFIER = "topic_classifier"
    GENRE_CLASSIFIER = "genre_classifier"
    QUALITY_CLASSIFIER = "quality_classifier"
    CONTENT_SAFETY_CLASSIFIER = "content_safety_classifier"


class CategoryLevel(str, Enum):
    """Category hierarchy levels."""
    LEVEL_1_PRIMARY = "level_1_primary"
    LEVEL_2_SECONDARY = "level_2_secondary"
    LEVEL_3_SPECIFIC = "level_3_specific"
    LEVEL_4_DETAILED = "level_4_detailed"


class ConfidenceLevel(str, Enum):
    """Confidence levels for classifications."""
    VERY_LOW = "very_low"      # 0.0 - 0.2
    LOW = "low"                # 0.2 - 0.4
    MEDIUM = "medium"          # 0.4 - 0.6
    HIGH = "high"              # 0.6 - 0.8
    VERY_HIGH = "very_high"    # 0.8 - 1.0


class SafetyRating(str, Enum):
    """Content safety ratings."""
    SAFE = "safe"
    CAUTION = "caution"
    RESTRICTED = "restricted"
    ADULT_ONLY = "adult_only"
    UNSAFE = "unsafe"


@dataclass
class ClassificationResult:
    """Single classification result."""
    category: str
    level: CategoryLevel
    confidence: float
    model_used: ClassificationModel
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Tag:
    """Content tag with metadata."""
    tag: str
    confidence: float
    source: ClassificationModel
    category: Optional[str] = None
    weight: float = 1.0
    verified: bool = False
    created_at: datetime = field(default_factory=datetime.now)


class ContentClassificationRequest(BaseModel):
    """Content classification request."""
    content_id: str = Field(..., description="Content identifier")
    content_type: ContentType = Field(..., description="Type of content")
    content_url: Optional[str] = Field(None, description="URL to content file")
    content_data: Optional[bytes] = Field(None, description="Raw content data")
    text_content: Optional[str] = Field(None, description="Text content for analysis")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    models_to_use: List[ClassificationModel] = Field(default_factory=list, description="Specific models to use")
    include_safety_check: bool = Field(default=True, description="Include safety classification")
    generate_tags: bool = Field(default=True, description="Generate tags")
    hierarchical_classification: bool = Field(default=True, description="Use hierarchical classification")


class ContentClassification(BaseModel):
    """Complete content classification."""
    content_id: str = Field(..., description="Content identifier")
    content_type: ContentType = Field(..., description="Content type")
    primary_category: str = Field(..., description="Primary category")
    secondary_categories: List[str] = Field(default_factory=list, description="Secondary categories")
    hierarchical_categories: Dict[CategoryLevel, List[str]] = Field(default_factory=dict)
    tags: List[Tag] = Field(default_factory=list, description="Generated tags")
    confidence_scores: Dict[str, float] = Field(default_factory=dict, description="Confidence per category")
    safety_rating: SafetyRating = Field(default=SafetyRating.SAFE)
    sentiment_score: Optional[float] = Field(None, description="Sentiment score (-1 to 1)")
    quality_score: Optional[float] = Field(None, description="Quality score (0 to 1)")
    topics: List[str] = Field(default_factory=list, description="Identified topics")
    genres: List[str] = Field(default_factory=list, description="Content genres")
    themes: List[str] = Field(default_factory=list, description="Content themes")
    keywords: List[str] = Field(default_factory=list, description="Extracted keywords")
    languages_detected: List[str] = Field(default_factory=list, description="Detected languages")
    classification_time: float = Field(default=0.0, description="Time taken for classification")
    models_used: List[ClassificationModel] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    last_updated: datetime = Field(default_factory=datetime.now)


class ClassificationAnalytics(BaseModel):
    """Classification analytics and insights."""
    period_start: datetime
    period_end: datetime
    total_classifications: int
    category_distribution: Dict[str, int]
    content_type_distribution: Dict[ContentType, int]
    safety_distribution: Dict[SafetyRating, int]
    average_confidence: float
    most_common_tags: List[Tuple[str, int]]
    model_performance: Dict[ClassificationModel, Dict[str, float]]
    processing_times: Dict[str, float]


class ContentClassificationService:
    """
    Enterprise Content Classification Service
    
    Provides AI-powered content classification with multi-model analysis,
    hierarchical categorization, safety filtering, and automated tagging.
    """
    
    def __init__(self):
        self.classifications: Dict[str, ContentClassification] = {}
        self.classification_models: Dict[ClassificationModel, Any] = {}
        self.category_hierarchies: Dict[str, Dict[CategoryLevel, Set[str]]] = {}
        self.tag_vocabularies: Dict[str, Set[str]] = {}
        self.safety_rules: List[Dict[str, Any]] = []
        self.classification_templates: Dict[ContentType, Dict[str, Any]] = {}
        self.model_performance_metrics: Dict[ClassificationModel, Dict[str, float]] = {}
        
        # Initialize system
        self._initialize_classification_models()
        self._initialize_category_hierarchies()
        self._initialize_tag_vocabularies()
        self._initialize_safety_rules()
        self._initialize_classification_templates()
        
        logger.info("ContentClassificationService initialized successfully")
    
    def _initialize_classification_models(self):
        """Initialize classification models and their configurations."""
        self.classification_models = {
            ClassificationModel.VISUAL_CLASSIFIER: {
                "model_name": "ResNet50_ImageNet",
                "confidence_threshold": 0.5,
                "categories": ["objects", "scenes", "activities", "concepts"],
                "preprocessing": {"resize": (224, 224), "normalize": True}
            },
            ClassificationModel.AUDIO_CLASSIFIER: {
                "model_name": "YAMNet_AudioSet",
                "confidence_threshold": 0.4,
                "categories": ["music", "speech", "sound_effects", "ambient"],
                "preprocessing": {"sample_rate": 16000, "duration": 30}
            },
            ClassificationModel.TEXT_CLASSIFIER: {
                "model_name": "BERT_Multilingual",
                "confidence_threshold": 0.6,
                "categories": ["topics", "domains", "intent", "style"],
                "preprocessing": {"max_length": 512, "truncation": True}
            },
            ClassificationModel.MULTI_MODAL_CLASSIFIER: {
                "model_name": "CLIP_ViT_B32",
                "confidence_threshold": 0.5,
                "categories": ["cross_modal", "context", "narrative"],
                "preprocessing": {"joint_embedding": True}
            },
            ClassificationModel.SENTIMENT_ANALYZER: {
                "model_name": "RoBERTa_Sentiment",
                "confidence_threshold": 0.7,
                "categories": ["positive", "negative", "neutral"],
                "output_range": (-1.0, 1.0)
            },
            ClassificationModel.TOPIC_CLASSIFIER: {
                "model_name": "LDA_Topic_Model",
                "confidence_threshold": 0.3,
                "categories": ["technology", "business", "entertainment", "education"],
                "num_topics": 50
            },
            ClassificationModel.GENRE_CLASSIFIER: {
                "model_name": "Genre_CNN",
                "confidence_threshold": 0.4,
                "categories": ["music_genres", "video_genres", "text_genres"],
                "specialized": True
            },
            ClassificationModel.QUALITY_CLASSIFIER: {
                "model_name": "Quality_Assessment",
                "confidence_threshold": 0.5,
                "categories": ["technical_quality", "aesthetic_quality", "content_quality"],
                "output_range": (0.0, 1.0)
            },
            ClassificationModel.CONTENT_SAFETY_CLASSIFIER: {
                "model_name": "Safety_Detector",
                "confidence_threshold": 0.8,
                "categories": ["safe", "questionable", "adult", "harmful"],
                "strict_mode": True
            }
        }
    
    def _initialize_category_hierarchies(self):
        """Initialize hierarchical category structures."""
        self.category_hierarchies = {
            "entertainment": {
                CategoryLevel.LEVEL_1_PRIMARY: {"entertainment"},
                CategoryLevel.LEVEL_2_SECONDARY: {"music", "video", "gaming", "comedy"},
                CategoryLevel.LEVEL_3_SPECIFIC: {
                    "pop_music", "rock_music", "electronic_music",
                    "tutorial_video", "music_video", "documentary",
                    "indie_game", "mobile_game", "pc_game",
                    "stand_up_comedy", "sketch_comedy", "satire"
                },
                CategoryLevel.LEVEL_4_DETAILED: {
                    "pop_ballad", "pop_dance", "progressive_rock", "heavy_metal",
                    "house_music", "techno", "dubstep", "ambient",
                    "how_to_tutorial", "product_review", "unboxing",
                    "platformer_game", "rpg_game", "puzzle_game"
                }
            },
            "education": {
                CategoryLevel.LEVEL_1_PRIMARY: {"education"},
                CategoryLevel.LEVEL_2_SECONDARY: {"academic", "professional", "personal_development", "skills"},
                CategoryLevel.LEVEL_3_SPECIFIC: {
                    "mathematics", "science", "history", "language",
                    "programming", "business", "marketing", "design",
                    "fitness", "cooking", "art", "music_theory"
                },
                CategoryLevel.LEVEL_4_DETAILED: {
                    "calculus", "algebra", "physics", "chemistry",
                    "python_programming", "web_development", "data_science",
                    "digital_marketing", "graphic_design", "ui_ux"
                }
            },
            "business": {
                CategoryLevel.LEVEL_1_PRIMARY: {"business"},
                CategoryLevel.LEVEL_2_SECONDARY: {"corporate", "startup", "finance", "marketing"},
                CategoryLevel.LEVEL_3_SPECIFIC: {
                    "strategy", "operations", "hr", "sales",
                    "investment", "banking", "crypto", "trading",
                    "content_marketing", "social_media", "advertising"
                },
                CategoryLevel.LEVEL_4_DETAILED: {
                    "business_plan", "market_analysis", "financial_modeling",
                    "stock_analysis", "portfolio_management", "risk_assessment"
                }
            }
        }
    
    def _initialize_tag_vocabularies(self):
        """Initialize tag vocabularies for different domains."""
        self.tag_vocabularies = {
            "general": {
                "creative", "professional", "educational", "entertaining",
                "informative", "tutorial", "review", "demo", "showcase",
                "behind_the_scenes", "live", "recorded", "animated", "documentary"
            },
            "music": {
                "instrumental", "vocal", "acoustic", "electronic", "live_performance",
                "studio_recording", "remix", "cover", "original", "collaboration",
                "upbeat", "melancholic", "energetic", "calm", "dramatic"
            },
            "video": {
                "cinematic", "handheld", "static_shot", "dynamic", "montage",
                "time_lapse", "slow_motion", "high_definition", "4k", "aerial",
                "indoor", "outdoor", "portrait", "landscape", "close_up"
            },
            "technology": {
                "programming", "software", "hardware", "ai", "machine_learning",
                "web_development", "mobile_app", "database", "cloud", "security",
                "open_source", "tutorial", "beginner", "advanced", "intermediate"
            },
            "art": {
                "digital_art", "traditional_art", "abstract", "realistic", "stylized",
                "portrait", "landscape", "still_life", "conceptual", "minimalist",
                "colorful", "monochrome", "detailed", "simple", "experimental"
            }
        }
    
    def _initialize_safety_rules(self):
        """Initialize content safety classification rules."""
        self.safety_rules = [
            {
                "rule_id": "explicit_content",
                "keywords": ["explicit", "adult", "nsfw", "mature"],
                "categories": ["adult_content", "sexual"],
                "action": SafetyRating.ADULT_ONLY,
                "confidence_required": 0.8
            },
            {
                "rule_id": "violence",
                "keywords": ["violence", "blood", "weapon", "fight"],
                "categories": ["violence", "graphic"],
                "action": SafetyRating.RESTRICTED,
                "confidence_required": 0.7
            },
            {
                "rule_id": "hate_speech",
                "keywords": ["hate", "discrimination", "offensive"],
                "categories": ["hate_speech", "harassment"],
                "action": SafetyRating.UNSAFE,
                "confidence_required": 0.9
            },
            {
                "rule_id": "medical_advice",
                "keywords": ["medical", "diagnosis", "treatment", "medication"],
                "categories": ["medical", "health"],
                "action": SafetyRating.CAUTION,
                "confidence_required": 0.6
            },
            {
                "rule_id": "financial_advice",
                "keywords": ["investment", "trading", "financial_advice"],
                "categories": ["financial", "investment"],
                "action": SafetyRating.CAUTION,
                "confidence_required": 0.6
            }
        ]
    
    def _initialize_classification_templates(self):
        """Initialize classification templates for different content types."""
        self.classification_templates = {
            ContentType.IMAGE: {
                "required_models": [
                    ClassificationModel.VISUAL_CLASSIFIER,
                    ClassificationModel.CONTENT_SAFETY_CLASSIFIER
                ],
                "optional_models": [
                    ClassificationModel.QUALITY_CLASSIFIER,
                    ClassificationModel.MULTI_MODAL_CLASSIFIER
                ],
                "features_to_extract": ["objects", "scenes", "colors", "composition", "style"],
                "hierarchical_levels": 3
            },
            ContentType.VIDEO: {
                "required_models": [
                    ClassificationModel.VISUAL_CLASSIFIER,
                    ClassificationModel.AUDIO_CLASSIFIER,
                    ClassificationModel.CONTENT_SAFETY_CLASSIFIER
                ],
                "optional_models": [
                    ClassificationModel.MULTI_MODAL_CLASSIFIER,
                    ClassificationModel.GENRE_CLASSIFIER,
                    ClassificationModel.QUALITY_CLASSIFIER
                ],
                "features_to_extract": ["scenes", "actions", "audio", "narrative", "style"],
                "hierarchical_levels": 4
            },
            ContentType.AUDIO: {
                "required_models": [
                    ClassificationModel.AUDIO_CLASSIFIER,
                    ClassificationModel.GENRE_CLASSIFIER
                ],
                "optional_models": [
                    ClassificationModel.QUALITY_CLASSIFIER,
                    ClassificationModel.CONTENT_SAFETY_CLASSIFIER
                ],
                "features_to_extract": ["genre", "mood", "instruments", "tempo", "quality"],
                "hierarchical_levels": 3
            },
            ContentType.TEXT: {
                "required_models": [
                    ClassificationModel.TEXT_CLASSIFIER,
                    ClassificationModel.TOPIC_CLASSIFIER,
                    ClassificationModel.SENTIMENT_ANALYZER
                ],
                "optional_models": [
                    ClassificationModel.CONTENT_SAFETY_CLASSIFIER,
                    ClassificationModel.QUALITY_CLASSIFIER
                ],
                "features_to_extract": ["topics", "sentiment", "style", "language", "readability"],
                "hierarchical_levels": 4
            }
        }
    
    async def classify_content(self, request: ContentClassificationRequest) -> ContentClassification:
        """Classify content using multiple AI models."""
        start_time = datetime.now()
        
        try:
            # Determine models to use
            models_to_use = request.models_to_use
            if not models_to_use:
                template = self.classification_templates.get(request.content_type)
                if template:
                    models_to_use = template["required_models"] + template["optional_models"]
                else:
                    models_to_use = [ClassificationModel.MULTI_MODAL_CLASSIFIER]
            
            # Initialize classification result
            classification = ContentClassification(
                content_id=request.content_id,
                content_type=request.content_type,
                primary_category="uncategorized"
            )
            
            classification_results = []
            all_tags = []
            confidence_scores = {}
            
            # Apply each model
            for model in models_to_use:
                try:
                    results = await self._apply_classification_model(model, request)
                    classification_results.extend(results)
                    
                    # Extract model-specific data
                    if model == ClassificationModel.SENTIMENT_ANALYZER:
                        classification.sentiment_score = await self._extract_sentiment(results)
                    elif model == ClassificationModel.QUALITY_CLASSIFIER:
                        classification.quality_score = await self._extract_quality(results)
                    elif model == ClassificationModel.CONTENT_SAFETY_CLASSIFIER:
                        classification.safety_rating = await self._extract_safety_rating(results)
                    elif model == ClassificationModel.TOPIC_CLASSIFIER:
                        classification.topics = await self._extract_topics(results)
                    elif model == ClassificationModel.GENRE_CLASSIFIER:
                        classification.genres = await self._extract_genres(results)
                    
                    # Generate tags from this model
                    if request.generate_tags:
                        model_tags = await self._generate_tags_from_results(results, model)
                        all_tags.extend(model_tags)
                    
                    # Store confidence scores
                    for result in results:
                        confidence_scores[result.category] = result.confidence
                    
                except Exception as e:
                    logger.error(f"Error applying model {model}: {e}")
                    continue
            
            # Process classification results
            if classification_results:
                # Determine primary category
                primary_result = max(classification_results, key=lambda r: r.confidence)
                classification.primary_category = primary_result.category
                
                # Determine secondary categories
                secondary_results = [r for r in classification_results 
                                   if r.category != classification.primary_category and r.confidence > 0.5]
                classification.secondary_categories = [r.category for r in secondary_results]
                
                # Build hierarchical categories
                if request.hierarchical_classification:
                    classification.hierarchical_categories = await self._build_hierarchical_categories(
                        classification_results
                    )
                
                # Process and deduplicate tags
                classification.tags = await self._process_tags(all_tags)
                
                # Extract keywords and themes
                classification.keywords = await self._extract_keywords(classification_results, request)
                classification.themes = await self._extract_themes(classification_results)
                
                # Detect languages if text content
                if request.text_content:
                    classification.languages_detected = await self._detect_languages(request.text_content)
            
            # Set confidence scores
            classification.confidence_scores = confidence_scores
            
            # Record models used
            classification.models_used = models_to_use
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            classification.classification_time = processing_time
            
            # Store classification
            self.classifications[request.content_id] = classification
            
            logger.info(f"Classified content {request.content_id} in {processing_time:.2f}s")
            return classification
            
        except Exception as e:
            logger.error(f"Error classifying content {request.content_id}: {e}")
            
            # Return minimal classification on error
            return ContentClassification(
                content_id=request.content_id,
                content_type=request.content_type,
                primary_category="error",
                classification_time=(datetime.now() - start_time).total_seconds()
            )
    
    async def _apply_classification_model(
        self, 
        model: ClassificationModel, 
        request: ContentClassificationRequest
    ) -> List[ClassificationResult]:
        """Apply specific classification model to content."""
        try:
            model_config = self.classification_models.get(model)
            if not model_config:
                return []
            
            # Simulate model inference based on model type
            if model == ClassificationModel.VISUAL_CLASSIFIER:
                return await self._classify_visual_content(request, model_config)
            elif model == ClassificationModel.AUDIO_CLASSIFIER:
                return await self._classify_audio_content(request, model_config)
            elif model == ClassificationModel.TEXT_CLASSIFIER:
                return await self._classify_text_content(request, model_config)
            elif model == ClassificationModel.MULTI_MODAL_CLASSIFIER:
                return await self._classify_multimodal_content(request, model_config)
            elif model == ClassificationModel.SENTIMENT_ANALYZER:
                return await self._analyze_sentiment(request, model_config)
            elif model == ClassificationModel.TOPIC_CLASSIFIER:
                return await self._classify_topics(request, model_config)
            elif model == ClassificationModel.GENRE_CLASSIFIER:
                return await self._classify_genre(request, model_config)
            elif model == ClassificationModel.QUALITY_CLASSIFIER:
                return await self._assess_quality(request, model_config)
            elif model == ClassificationModel.CONTENT_SAFETY_CLASSIFIER:
                return await self._classify_safety(request, model_config)
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error applying model {model}: {e}")
            return []
    
    async def _classify_visual_content(
        self, 
        request: ContentClassificationRequest, 
        model_config: Dict[str, Any]
    ) -> List[ClassificationResult]:
        """Classify visual content (images/videos)."""
        # Placeholder for actual visual classification
        # In real implementation, would use TensorFlow/PyTorch models
        
        results = []
        
        # Simulate object detection
        detected_objects = ["person", "car", "building", "tree", "sky"]
        for obj in detected_objects:
            confidence = 0.6 + (hash(obj + request.content_id) % 30) / 100
            results.append(ClassificationResult(
                category=f"object_{obj}",
                level=CategoryLevel.LEVEL_3_SPECIFIC,
                confidence=confidence,
                model_used=ClassificationModel.VISUAL_CLASSIFIER,
                metadata={"object_type": obj, "bounding_box": None}
            ))
        
        # Simulate scene classification
        scenes = ["outdoor", "indoor", "urban", "nature"]
        scene = scenes[hash(request.content_id) % len(scenes)]
        results.append(ClassificationResult(
            category=f"scene_{scene}",
            level=CategoryLevel.LEVEL_2_SECONDARY,
            confidence=0.75,
            model_used=ClassificationModel.VISUAL_CLASSIFIER,
            metadata={"scene_type": scene}
        ))
        
        return results
    
    async def _classify_audio_content(
        self, 
        request: ContentClassificationRequest, 
        model_config: Dict[str, Any]
    ) -> List[ClassificationResult]:
        """Classify audio content."""
        # Placeholder for actual audio classification
        results = []
        
        # Simulate audio classification
        audio_categories = ["music", "speech", "sound_effects", "ambient"]
        for category in audio_categories:
            confidence = 0.4 + (hash(category + request.content_id) % 40) / 100
            results.append(ClassificationResult(
                category=category,
                level=CategoryLevel.LEVEL_2_SECONDARY,
                confidence=confidence,
                model_used=ClassificationModel.AUDIO_CLASSIFIER,
                metadata={"audio_features": {"tempo": 120, "key": "C_major"}}
            ))
        
        return results
    
    async def _classify_text_content(
        self, 
        request: ContentClassificationRequest, 
        model_config: Dict[str, Any]
    ) -> List[ClassificationResult]:
        """Classify text content."""
        if not request.text_content:
            return []
        
        results = []
        text = request.text_content.lower()
        
        # Simple keyword-based classification (placeholder)
        if any(word in text for word in ["tutorial", "how to", "guide", "learn"]):
            results.append(ClassificationResult(
                category="educational",
                level=CategoryLevel.LEVEL_1_PRIMARY,
                confidence=0.8,
                model_used=ClassificationModel.TEXT_CLASSIFIER,
                metadata={"text_features": {"word_count": len(text.split())}}
            ))
        
        if any(word in text for word in ["review", "opinion", "experience"]):
            results.append(ClassificationResult(
                category="review",
                level=CategoryLevel.LEVEL_2_SECONDARY,
                confidence=0.7,
                model_used=ClassificationModel.TEXT_CLASSIFIER
            ))
        
        if any(word in text for word in ["technology", "programming", "software"]):
            results.append(ClassificationResult(
                category="technology",
                level=CategoryLevel.LEVEL_1_PRIMARY,
                confidence=0.75,
                model_used=ClassificationModel.TEXT_CLASSIFIER
            ))
        
        return results
    
    async def _classify_multimodal_content(
        self, 
        request: ContentClassificationRequest, 
        model_config: Dict[str, Any]
    ) -> List[ClassificationResult]:
        """Classify content using multimodal analysis."""
        # Placeholder for multimodal classification
        results = []
        
        # Simulate cross-modal understanding
        if request.content_type == ContentType.VIDEO and request.text_content:
            results.append(ClassificationResult(
                category="narrative_content",
                level=CategoryLevel.LEVEL_2_SECONDARY,
                confidence=0.65,
                model_used=ClassificationModel.MULTI_MODAL_CLASSIFIER,
                metadata={"modalities": ["visual", "text"]}
            ))
        
        return results
    
    async def _analyze_sentiment(
        self, 
        request: ContentClassificationRequest, 
        model_config: Dict[str, Any]
    ) -> List[ClassificationResult]:
        """Analyze sentiment of content."""
        if not request.text_content:
            return []
        
        # Placeholder sentiment analysis
        text = request.text_content.lower()
        
        positive_words = ["good", "great", "excellent", "amazing", "love", "wonderful"]
        negative_words = ["bad", "terrible", "awful", "hate", "horrible", "worst"]
        
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        if positive_count > negative_count:
            sentiment = "positive"
            confidence = min(0.9, 0.5 + (positive_count - negative_count) * 0.1)
        elif negative_count > positive_count:
            sentiment = "negative"
            confidence = min(0.9, 0.5 + (negative_count - positive_count) * 0.1)
        else:
            sentiment = "neutral"
            confidence = 0.6
        
        return [ClassificationResult(
            category=f"sentiment_{sentiment}",
            level=CategoryLevel.LEVEL_2_SECONDARY,
            confidence=confidence,
            model_used=ClassificationModel.SENTIMENT_ANALYZER,
            metadata={"sentiment_score": confidence if sentiment == "positive" else -confidence}
        )]
    
    async def _classify_topics(
        self, 
        request: ContentClassificationRequest, 
        model_config: Dict[str, Any]
    ) -> List[ClassificationResult]:
        """Classify content topics."""
        if not request.text_content:
            return []
        
        # Placeholder topic classification
        text = request.text_content.lower()
        results = []
        
        topic_keywords = {
            "technology": ["ai", "software", "programming", "computer", "tech"],
            "business": ["marketing", "sales", "finance", "strategy", "company"],
            "education": ["learn", "study", "course", "tutorial", "education"],
            "entertainment": ["movie", "music", "game", "fun", "entertainment"]
        }
        
        for topic, keywords in topic_keywords.items():
            relevance = sum(1 for keyword in keywords if keyword in text)
            if relevance > 0:
                confidence = min(0.9, 0.3 + relevance * 0.15)
                results.append(ClassificationResult(
                    category=f"topic_{topic}",
                    level=CategoryLevel.LEVEL_2_SECONDARY,
                    confidence=confidence,
                    model_used=ClassificationModel.TOPIC_CLASSIFIER,
                    metadata={"keyword_matches": relevance}
                ))
        
        return results
    
    async def _classify_genre(
        self, 
        request: ContentClassificationRequest, 
        model_config: Dict[str, Any]
    ) -> List[ClassificationResult]:
        """Classify content genre."""
        # Placeholder genre classification
        results = []
        
        if request.content_type == ContentType.AUDIO:
            # Music genre classification
            genres = ["pop", "rock", "electronic", "classical", "jazz"]
            genre = genres[hash(request.content_id) % len(genres)]
            confidence = 0.6 + (hash(genre + request.content_id) % 30) / 100
            
            results.append(ClassificationResult(
                category=f"music_genre_{genre}",
                level=CategoryLevel.LEVEL_3_SPECIFIC,
                confidence=confidence,
                model_used=ClassificationModel.GENRE_CLASSIFIER,
                metadata={"genre_family": "music"}
            ))
        
        elif request.content_type == ContentType.VIDEO:
            # Video genre classification
            genres = ["tutorial", "entertainment", "documentary", "review"]
            genre = genres[hash(request.content_id) % len(genres)]
            confidence = 0.55 + (hash(genre + request.content_id) % 35) / 100
            
            results.append(ClassificationResult(
                category=f"video_genre_{genre}",
                level=CategoryLevel.LEVEL_3_SPECIFIC,
                confidence=confidence,
                model_used=ClassificationModel.GENRE_CLASSIFIER,
                metadata={"genre_family": "video"}
            ))
        
        return results
    
    async def _assess_quality(
        self, 
        request: ContentClassificationRequest, 
        model_config: Dict[str, Any]
    ) -> List[ClassificationResult]:
        """Assess content quality."""
        # Placeholder quality assessment
        quality_score = 0.7 + (hash(request.content_id) % 30) / 100
        
        if quality_score > 0.8:
            quality_level = "high_quality"
        elif quality_score > 0.6:
            quality_level = "medium_quality"
        else:
            quality_level = "low_quality"
        
        return [ClassificationResult(
            category=f"quality_{quality_level}",
            level=CategoryLevel.LEVEL_2_SECONDARY,
            confidence=0.75,
            model_used=ClassificationModel.QUALITY_CLASSIFIER,
            metadata={"quality_score": quality_score}
        )]
    
    async def _classify_safety(
        self, 
        request: ContentClassificationRequest, 
        model_config: Dict[str, Any]
    ) -> List[ClassificationResult]:
        """Classify content safety."""
        # Apply safety rules
        safety_rating = SafetyRating.SAFE
        confidence = 0.9
        
        if request.text_content:
            text = request.text_content.lower()
            
            for rule in self.safety_rules:
                if any(keyword in text for keyword in rule["keywords"]):
                    safety_rating = rule["action"]
                    confidence = rule["confidence_required"]
                    break
        
        return [ClassificationResult(
            category=f"safety_{safety_rating.value}",
            level=CategoryLevel.LEVEL_1_PRIMARY,
            confidence=confidence,
            model_used=ClassificationModel.CONTENT_SAFETY_CLASSIFIER,
            metadata={"safety_rating": safety_rating.value}
        )]
    
    async def _extract_sentiment(self, results: List[ClassificationResult]) -> Optional[float]:
        """Extract sentiment score from classification results."""
        for result in results:
            if "sentiment_score" in result.metadata:
                return result.metadata["sentiment_score"]
        return None
    
    async def _extract_quality(self, results: List[ClassificationResult]) -> Optional[float]:
        """Extract quality score from classification results."""
        for result in results:
            if "quality_score" in result.metadata:
                return result.metadata["quality_score"]
        return None
    
    async def _extract_safety_rating(self, results: List[ClassificationResult]) -> SafetyRating:
        """Extract safety rating from classification results."""
        for result in results:
            if "safety_rating" in result.metadata:
                try:
                    return SafetyRating(result.metadata["safety_rating"])
                except ValueError:
                    pass
        return SafetyRating.SAFE
    
    async def _extract_topics(self, results: List[ClassificationResult]) -> List[str]:
        """Extract topics from classification results."""
        topics = []
        for result in results:
            if result.category.startswith("topic_"):
                topic = result.category.replace("topic_", "")
                topics.append(topic)
        return topics
    
    async def _extract_genres(self, results: List[ClassificationResult]) -> List[str]:
        """Extract genres from classification results."""
        genres = []
        for result in results:
            if "genre" in result.category:
                genre = result.category.split("_")[-1]
                genres.append(genre)
        return genres
    
    async def _generate_tags_from_results(
        self, 
        results: List[ClassificationResult], 
        model: ClassificationModel
    ) -> List[Tag]:
        """Generate tags from classification results."""
        tags = []
        
        for result in results:
            # Create tag from category
            tag_text = result.category.replace("_", " ").title()
            
            tag = Tag(
                tag=tag_text,
                confidence=result.confidence,
                source=model,
                category=result.category,
                weight=result.confidence
            )
            tags.append(tag)
            
            # Generate additional tags from metadata
            if "object_type" in result.metadata:
                obj_tag = Tag(
                    tag=result.metadata["object_type"],
                    confidence=result.confidence * 0.8,
                    source=model,
                    category="object"
                )
                tags.append(obj_tag)
        
        return tags
    
    async def _process_tags(self, all_tags: List[Tag]) -> List[Tag]:
        """Process and deduplicate tags."""
        # Group tags by text
        tag_groups = defaultdict(list)
        for tag in all_tags:
            tag_groups[tag.tag.lower()].append(tag)
        
        # Merge duplicate tags
        processed_tags = []
        for tag_text, tags in tag_groups.items():
            if len(tags) == 1:
                processed_tags.append(tags[0])
            else:
                # Merge tags with same text
                merged_confidence = max(tag.confidence for tag in tags)
                merged_weight = sum(tag.weight for tag in tags) / len(tags)
                best_source = max(tags, key=lambda t: t.confidence).source
                
                merged_tag = Tag(
                    tag=tags[0].tag,
                    confidence=merged_confidence,
                    source=best_source,
                    category=tags[0].category,
                    weight=merged_weight,
                    verified=any(tag.verified for tag in tags)
                )
                processed_tags.append(merged_tag)
        
        # Sort by confidence and return top tags
        processed_tags.sort(key=lambda t: t.confidence, reverse=True)
        return processed_tags[:20]  # Limit to top 20 tags
    
    async def _build_hierarchical_categories(
        self, 
        results: List[ClassificationResult]
    ) -> Dict[CategoryLevel, List[str]]:
        """Build hierarchical category structure."""
        hierarchical = defaultdict(list)
        
        for result in results:
            if result.confidence > 0.5:  # Only include confident classifications
                hierarchical[result.level].append(result.category)
        
        # Remove duplicates
        for level in hierarchical:
            hierarchical[level] = list(set(hierarchical[level]))
        
        return dict(hierarchical)
    
    async def _extract_keywords(
        self, 
        results: List[ClassificationResult], 
        request: ContentClassificationRequest
    ) -> List[str]:
        """Extract keywords from content and classification results."""
        keywords = set()
        
        # Extract from classification categories
        for result in results:
            if result.confidence > 0.6:
                category_words = result.category.replace("_", " ").split()
                keywords.update(category_words)
        
        # Extract from text content if available
        if request.text_content:
            # Simple keyword extraction (placeholder)
            words = re.findall(r'\b\w{4,}\b', request.text_content.lower())
            # Filter common words (simplified)
            filtered_words = [w for w in words if w not in 
                             {'this', 'that', 'with', 'have', 'will', 'from', 'they', 'been', 'were'}]
            keywords.update(filtered_words[:10])
        
        return list(keywords)[:15]  # Limit to 15 keywords
    
    async def _extract_themes(self, results: List[ClassificationResult]) -> List[str]:
        """Extract themes from classification results."""
        themes = set()
        
        theme_mapping = {
            "educational": "learning",
            "entertainment": "fun",
            "technology": "innovation",
            "business": "professional",
            "art": "creative",
            "music": "artistic",
            "nature": "natural",
            "urban": "metropolitan"
        }
        
        for result in results:
            if result.confidence > 0.6:
                for key, theme in theme_mapping.items():
                    if key in result.category.lower():
                        themes.add(theme)
        
        return list(themes)
    
    async def _detect_languages(self, text: str) -> List[str]:
        """Detect languages in text content."""
        # Placeholder language detection
        # In real implementation, would use langdetect or similar
        
        # Simple detection based on common words
        language_indicators = {
            "en": ["the", "and", "that", "have", "for", "not", "with", "you"],
            "es": ["el", "de", "que", "y", "en", "un", "es", "se"],
            "fr": ["le", "de", "et", "à", "un", "il", "être", "et"],
            "de": ["der", "die", "und", "in", "den", "von", "zu", "das"]
        }
        
        text_lower = text.lower()
        detected = []
        
        for lang, indicators in language_indicators.items():
            matches = sum(1 for word in indicators if word in text_lower)
            if matches >= 2:  # Require at least 2 indicator words
                detected.append(lang)
        
        return detected if detected else ["en"]  # Default to English
    
    # Public API methods
    async def get_classification(self, content_id: str) -> Optional[ContentClassification]:
        """Get classification for content."""
        return self.classifications.get(content_id)
    
    async def update_classification(
        self, 
        content_id: str, 
        updates: Dict[str, Any]
    ) -> bool:
        """Update classification with manual corrections."""
        try:
            if content_id not in self.classifications:
                return False
            
            classification = self.classifications[content_id]
            
            # Apply updates
            for key, value in updates.items():
                if hasattr(classification, key):
                    setattr(classification, key, value)
            
            classification.last_updated = datetime.now()
            
            logger.info(f"Updated classification for content {content_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating classification: {e}")
            return False
    
    async def search_by_classification(
        self, 
        category: str,
        content_type: Optional[ContentType] = None,
        min_confidence: float = 0.5
    ) -> List[str]:
        """Search content by classification category."""
        try:
            matching_content = []
            
            for content_id, classification in self.classifications.items():
                # Content type filter
                if content_type and classification.content_type != content_type:
                    continue
                
                # Check primary category
                if classification.primary_category == category:
                    primary_confidence = classification.confidence_scores.get(category, 0)
                    if primary_confidence >= min_confidence:
                        matching_content.append(content_id)
                        continue
                
                # Check secondary categories
                if category in classification.secondary_categories:
                    category_confidence = classification.confidence_scores.get(category, 0)
                    if category_confidence >= min_confidence:
                        matching_content.append(content_id)
                        continue
                
                # Check hierarchical categories
                for level_categories in classification.hierarchical_categories.values():
                    if category in level_categories:
                        matching_content.append(content_id)
                        break
            
            return matching_content
            
        except Exception as e:
            logger.error(f"Error searching by classification: {e}")
            return []
    
    async def get_classification_analytics(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> ClassificationAnalytics:
        """Get classification analytics for time period."""
        try:
            # Filter classifications by date range
            period_classifications = [
                c for c in self.classifications.values()
                if start_date <= c.created_at <= end_date
            ]
            
            total_classifications = len(period_classifications)
            
            if total_classifications == 0:
                return ClassificationAnalytics(
                    period_start=start_date,
                    period_end=end_date,
                    total_classifications=0,
                    category_distribution={},
                    content_type_distribution={},
                    safety_distribution={},
                    average_confidence=0.0,
                    most_common_tags=[],
                    model_performance={},
                    processing_times={}
                )
            
            # Calculate distributions
            category_dist = defaultdict(int)
            content_type_dist = defaultdict(int)
            safety_dist = defaultdict(int)
            
            all_tags = defaultdict(int)
            confidence_scores = []
            processing_times = []
            model_usage = defaultdict(int)
            
            for classification in period_classifications:
                # Category distribution
                category_dist[classification.primary_category] += 1
                for category in classification.secondary_categories:
                    category_dist[category] += 1
                
                # Content type distribution
                content_type_dist[classification.content_type] += 1
                
                # Safety distribution
                safety_dist[classification.safety_rating] += 1
                
                # Tags
                for tag in classification.tags:
                    all_tags[tag.tag] += 1
                
                # Confidence scores
                if classification.confidence_scores:
                    confidence_scores.extend(classification.confidence_scores.values())
                
                # Processing times
                processing_times.append(classification.classification_time)
                
                # Model usage
                for model in classification.models_used:
                    model_usage[model] += 1
            
            # Calculate averages
            avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
            
            # Most common tags
            most_common_tags = sorted(all_tags.items(), key=lambda x: x[1], reverse=True)[:10]
            
            # Model performance (placeholder)
            model_performance = {}
            for model in model_usage:
                model_performance[model] = {
                    "usage_count": model_usage[model],
                    "average_confidence": avg_confidence,  # Simplified
                    "success_rate": 0.95  # Placeholder
                }
            
            # Processing time statistics
            avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0.0
            
            return ClassificationAnalytics(
                period_start=start_date,
                period_end=end_date,
                total_classifications=total_classifications,
                category_distribution=dict(category_dist),
                content_type_distribution={k.value: v for k, v in content_type_dist.items()},
                safety_distribution={k.value: v for k, v in safety_dist.items()},
                average_confidence=avg_confidence,
                most_common_tags=most_common_tags,
                model_performance={k.value: v for k, v in model_performance.items()},
                processing_times={"average": avg_processing_time, "total": sum(processing_times)}
            )
            
        except Exception as e:
            logger.error(f"Error getting classification analytics: {e}")
            return ClassificationAnalytics(
                period_start=start_date,
                period_end=end_date,
                total_classifications=0,
                category_distribution={},
                content_type_distribution={},
                safety_distribution={},
                average_confidence=0.0,
                most_common_tags=[],
                model_performance={},
                processing_times={}
            )
    
    def get_service_metrics(self) -> Dict[str, Any]:
        """Get comprehensive service metrics."""
        total_classifications = len(self.classifications)
        
        if total_classifications == 0:
            return {
                "total_classifications": 0,
                "models_available": len(self.classification_models),
                "category_hierarchies": len(self.category_hierarchies),
                "safety_rules": len(self.safety_rules),
                "tag_vocabularies": len(self.tag_vocabularies)
            }
        
        # Calculate distributions
        content_type_dist = defaultdict(int)
        safety_dist = defaultdict(int)
        processing_times = []
        
        for classification in self.classifications.values():
            content_type_dist[classification.content_type.value] += 1
            safety_dist[classification.safety_rating.value] += 1
            processing_times.append(classification.classification_time)
        
        avg_processing_time = sum(processing_times) / len(processing_times)
        
        return {
            "total_classifications": total_classifications,
            "models_available": len(self.classification_models),
            "category_hierarchies": len(self.category_hierarchies),
            "safety_rules": len(self.safety_rules),
            "tag_vocabularies": len(self.tag_vocabularies),
            "content_type_distribution": dict(content_type_dist),
            "safety_distribution": dict(safety_dist),
            "average_processing_time": avg_processing_time,
            "classification_templates": len(self.classification_templates)
        }


# Global service instance
_classification_service_instance = None

def get_content_classification_service() -> ContentClassificationService:
    """Get singleton instance of ContentClassificationService."""
    global _classification_service_instance
    if _classification_service_instance is None:
        _classification_service_instance = ContentClassificationService()
    return _classification_service_instance


# Example usage and testing
async def example_usage():
    """Example usage of Content Classification Service."""
    service = get_content_classification_service()
    
    # Classify text content
    text_request = ContentClassificationRequest(
        content_id="content_text_123",
        content_type=ContentType.TEXT,
        text_content="This is a comprehensive tutorial on machine learning and artificial intelligence. "
                    "We will cover neural networks, deep learning, and practical applications.",
        include_safety_check=True,
        generate_tags=True,
        hierarchical_classification=True
    )
    
    text_classification = await service.classify_content(text_request)
    print(f"Text Classification:")
    print(f"  Primary Category: {text_classification.primary_category}")
    print(f"  Topics: {text_classification.topics}")
    print(f"  Tags: {[tag.tag for tag in text_classification.tags[:5]]}")
    print(f"  Safety Rating: {text_classification.safety_rating}")
    print(f"  Processing Time: {text_classification.classification_time:.2f}s")
    
    # Classify video content
    video_request = ContentClassificationRequest(
        content_id="content_video_456",
        content_type=ContentType.VIDEO,
        content_url="https://example.com/video.mp4",
        text_content="Amazing nature documentary about wildlife in Africa",
        models_to_use=[
            ClassificationModel.VISUAL_CLASSIFIER,
            ClassificationModel.AUDIO_CLASSIFIER,
            ClassificationModel.CONTENT_SAFETY_CLASSIFIER
        ]
    )
    
    video_classification = await service.classify_content(video_request)
    print(f"\nVideo Classification:")
    print(f"  Primary Category: {video_classification.primary_category}")
    print(f"  Secondary Categories: {video_classification.secondary_categories}")
    print(f"  Genres: {video_classification.genres}")
    print(f"  Quality Score: {video_classification.quality_score}")
    
    # Search by classification
    educational_content = await service.search_by_classification(
        "educational",
        content_type=ContentType.TEXT,
        min_confidence=0.5
    )
    print(f"\nEducational Content Found: {educational_content}")
    
    # Get analytics
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    analytics = await service.get_classification_analytics(start_date, end_date)
    print(f"\nClassification Analytics:")
    print(f"  Total Classifications: {analytics.total_classifications}")
    print(f"  Average Confidence: {analytics.average_confidence:.2f}")
    print(f"  Most Common Tags: {analytics.most_common_tags[:3]}")
    
    # Get service metrics
    metrics = service.get_service_metrics()
    print(f"\nService Metrics: {metrics}")


if __name__ == "__main__":
    # Run example
    asyncio.run(example_usage())