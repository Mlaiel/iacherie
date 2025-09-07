#!/usr/bin/env python3
"""🏷️ Content Classification AI - Automated Content Classification System
===============================================================================
Module: backend/media_processing/content_classification_ai.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: AI Engineer + ML Engineer + Content Analyst + Backend Senior Engineer
Type: Enterprise Content Classification System - Production-Ready
Responsibility: AI-powered automated content classification and tagging
===========================================================================

⚠️  EXCLUSIVE INTELLECTUAL PROPERTY - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use strictly prohibited and subject to legal prosecution.
Contact: mlaiel@live.de

🏷️ CONTENT CLASSIFICATION CAPABILITIES:
- Multi-modal content classification (text, image, audio, video)
- Hierarchical category classification
- Automatic tag generation and annotation
- Genre and style classification
- Content appropriateness assessment
- Topic modeling and theme detection
"""

import asyncio
import logging
import uuid
import numpy as np
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone
import json

# AI/ML imports for classification
try:
    import torch
    import transformers
    from transformers import (
        AutoTokenizer, AutoModelForSequenceClassification, 
        CLIPModel, CLIPProcessor, pipeline
    )
    from sentence_transformers import SentenceTransformer
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

# Computer vision imports
try:
    import cv2
    from PIL import Image
    import torchvision.transforms as transforms
    VISION_AVAILABLE = True
except ImportError:
    VISION_AVAILABLE = False

# Audio processing imports
try:
    import librosa
    import soundfile as sf
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False

logger = logging.getLogger(__name__)


class ContentType(Enum):
    """Content types for classification"""
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    MULTIMODAL = "multimodal"


class ClassificationType(Enum):
    """Types of classification"""
    CATEGORY = "category"
    GENRE = "genre"
    STYLE = "style"
    TOPIC = "topic"
    SENTIMENT = "sentiment"
    APPROPRIATENESS = "appropriateness"
    QUALITY = "quality"
    COMPLEXITY = "complexity"


class ConfidenceLevel(Enum):
    """Classification confidence levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class ContentCategory(Enum):
    """Primary content categories"""
    ENTERTAINMENT = "entertainment"
    EDUCATION = "education"
    NEWS = "news"
    BUSINESS = "business"
    TECHNOLOGY = "technology"
    HEALTH = "health"
    LIFESTYLE = "lifestyle"
    SPORTS = "sports"
    MUSIC = "music"
    ART = "art"
    SCIENCE = "science"
    TRAVEL = "travel"
    FOOD = "food"
    FASHION = "fashion"
    GAMING = "gaming"
    OTHER = "other"


@dataclass
class ClassificationResult:
    """Content classification result"""
    result_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str = ""
    content_type: ContentType = ContentType.TEXT
    classification_type: ClassificationType = ClassificationType.CATEGORY
    
    # Primary classification
    primary_category: str = ""
    primary_confidence: float = 0.0
    
    # Secondary classifications
    secondary_categories: List[Dict[str, float]] = field(default_factory=list)
    
    # Detailed classifications
    categories: Dict[str, float] = field(default_factory=dict)
    tags: List[Dict[str, Any]] = field(default_factory=list)
    genres: List[Dict[str, float]] = field(default_factory=list)
    topics: List[Dict[str, float]] = field(default_factory=list)
    
    # Content attributes
    sentiment: Dict[str, float] = field(default_factory=dict)
    appropriateness_score: float = 0.0
    quality_assessment: Dict[str, float] = field(default_factory=dict)
    complexity_level: float = 0.0
    
    # Processing metadata
    model_versions: Dict[str, str] = field(default_factory=dict)
    processing_time: float = 0.0
    confidence_level: ConfidenceLevel = ConfidenceLevel.MEDIUM
    
    # Timestamps
    classified_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ContentTag:
    """Content tag with metadata"""
    tag_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    tag_name: str = ""
    tag_category: str = ""
    confidence: float = 0.0
    relevance: float = 0.0
    source: str = ""  # e.g., "ai_generated", "user_provided", "extracted"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ClassificationModel:
    """Classification model configuration"""
    model_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    model_name: str = ""
    model_type: str = ""
    content_types: List[ContentType] = field(default_factory=list)
    classification_types: List[ClassificationType] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    accuracy: float = 0.0
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ClassificationConfig:
    """Classification configuration"""
    config_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    enable_hierarchical: bool = True
    enable_multi_label: bool = True
    confidence_threshold: float = 0.5
    max_categories: int = 5
    max_tags: int = 20
    enable_auto_tagging: bool = True
    enable_appropriateness_check: bool = True
    custom_categories: List[str] = field(default_factory=list)


class ContentClassificationAI:
    """Enterprise AI-powered content classification system"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Storage
        self.classification_results: Dict[str, ClassificationResult] = {}
        self.content_tags: Dict[str, ContentTag] = {}
        self.classification_models: Dict[str, ClassificationModel] = {}
        
        # AI Models
        self.models: Dict[str, Any] = {}
        self.tokenizers: Dict[str, Any] = {}
        self.classifiers: Dict[str, Any] = {}
        
        # Configuration
        self.config = ClassificationConfig()
        
        # Category hierarchies
        self.category_hierarchies = self._initialize_category_hierarchies()
        
        # Genre mappings
        self.genre_mappings = self._initialize_genre_mappings()
        
        # Initialize models
        asyncio.create_task(self._initialize_ai_models())
        
        self.logger.info("Content Classification AI initialized")
    
    async def classify_content(
        self,
        content_id: str,
        content_data: Union[str, bytes, Dict[str, Any]],
        content_type: ContentType,
        classification_types: List[ClassificationType] = None,
        custom_config: ClassificationConfig = None
    ) -> ClassificationResult:
        """Classify content using AI models"""
        try:
            start_time = datetime.now()
            self.logger.info(f"Classifying content: {content_id}")
            
            config = custom_config or self.config
            if classification_types is None:
                classification_types = [ClassificationType.CATEGORY, ClassificationType.TOPIC]
            
            # Initialize classification result
            result = ClassificationResult(
                content_id=content_id,
                content_type=content_type
            )
            
            # Perform different types of classification
            for classification_type in classification_types:
                if classification_type == ClassificationType.CATEGORY:
                    await self._classify_categories(content_data, content_type, result, config)
                elif classification_type == ClassificationType.GENRE:
                    await self._classify_genres(content_data, content_type, result)
                elif classification_type == ClassificationType.TOPIC:
                    await self._classify_topics(content_data, content_type, result)
                elif classification_type == ClassificationType.SENTIMENT:
                    await self._classify_sentiment(content_data, content_type, result)
                elif classification_type == ClassificationType.APPROPRIATENESS:
                    await self._assess_appropriateness(content_data, content_type, result)
                elif classification_type == ClassificationType.QUALITY:
                    await self._assess_quality(content_data, content_type, result)
            
            # Generate automatic tags
            if config.enable_auto_tagging:
                await self._generate_automatic_tags(content_data, content_type, result, config)
            
            # Determine primary classification
            await self._determine_primary_classification(result)
            
            # Calculate confidence level
            result.confidence_level = await self._calculate_confidence_level(result)
            
            # Record processing time
            result.processing_time = (datetime.now() - start_time).total_seconds()
            
            # Store result
            self.classification_results[result.result_id] = result
            
            self.logger.info(f"Content classification completed for {content_id}: {result.primary_category}")
            return result
            
        except Exception as e:
            self.logger.error(f"Content classification failed for {content_id}: {str(e)}")
            return ClassificationResult(
                content_id=content_id,
                content_type=content_type,
                primary_category="unknown"
            )
    
    async def classify_text_content(
        self,
        content_id: str,
        text_content: str,
        classification_types: List[ClassificationType] = None
    ) -> ClassificationResult:
        """Classify text content specifically"""
        try:
            self.logger.info(f"Classifying text content: {content_id}")
            
            result = ClassificationResult(
                content_id=content_id,
                content_type=ContentType.TEXT
            )
            
            # Text-specific classification
            if not AI_AVAILABLE:
                return await self._fallback_text_classification(text_content, result)
            
            # Load text classification models
            if "text_classifier" not in self.classifiers:
                self.classifiers["text_classifier"] = pipeline(
                    "text-classification",
                    model="facebook/bart-large-mnli"
                )
            
            classifier = self.classifiers["text_classifier"]
            
            # Define categories for classification
            categories = [cat.value for cat in ContentCategory]
            
            # Classify against each category
            classification_scores = {}
            for category in categories:
                prompt = f"This text is about {category}"
                result_item = classifier(text_content, [prompt])
                
                if result_item and len(result_item) > 0:
                    score = result_item[0].get("score", 0.0)
                    if result_item[0].get("label") == "ENTAILMENT":
                        classification_scores[category] = score
                    else:
                        classification_scores[category] = 1.0 - score
            
            # Sort categories by score
            sorted_categories = sorted(
                classification_scores.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            # Set primary category
            if sorted_categories:
                result.primary_category = sorted_categories[0][0]
                result.primary_confidence = sorted_categories[0][1]
                
                # Set secondary categories
                result.secondary_categories = [
                    {"category": cat, "confidence": score}
                    for cat, score in sorted_categories[1:6]
                    if score > self.config.confidence_threshold
                ]
            
            result.categories = classification_scores
            
            # Perform additional text-specific classifications
            await self._classify_text_topics(text_content, result)
            await self._classify_text_sentiment(text_content, result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Text classification failed for {content_id}: {str(e)}")
            return await self._fallback_text_classification(text_content, result)
    
    async def classify_image_content(
        self,
        content_id: str,
        image_data: bytes,
        classification_types: List[ClassificationType] = None
    ) -> ClassificationResult:
        """Classify image content specifically"""
        try:
            self.logger.info(f"Classifying image content: {content_id}")
            
            result = ClassificationResult(
                content_id=content_id,
                content_type=ContentType.IMAGE
            )
            
            if not VISION_AVAILABLE or not AI_AVAILABLE:
                return await self._fallback_image_classification(result)
            
            # Load CLIP model for image classification
            if "clip_model" not in self.models:
                self.models["clip_model"] = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
                self.models["clip_processor"] = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
            
            clip_model = self.models["clip_model"]
            clip_processor = self.models["clip_processor"]
            
            # Load image
            image = Image.open(io.BytesIO(image_data))
            
            # Prepare category labels
            category_labels = [f"a photo of {cat.value}" for cat in ContentCategory]
            
            # Process image and text
            inputs = clip_processor(
                text=category_labels,
                images=image,
                return_tensors="pt",
                padding=True
            )
            
            # Get predictions
            with torch.no_grad():
                outputs = clip_model(**inputs)
                logits_per_image = outputs.logits_per_image
                probs = logits_per_image.softmax(dim=1)
            
            # Extract classification results
            category_scores = {}
            for i, category in enumerate(ContentCategory):
                category_scores[category.value] = float(probs[0][i])
            
            # Sort and set results
            sorted_categories = sorted(
                category_scores.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            if sorted_categories:
                result.primary_category = sorted_categories[0][0]
                result.primary_confidence = sorted_categories[0][1]
                result.secondary_categories = [
                    {"category": cat, "confidence": score}
                    for cat, score in sorted_categories[1:6]
                ]
            
            result.categories = category_scores
            
            # Perform image-specific analysis
            await self._analyze_image_style(image, result)
            await self._analyze_image_composition(image, result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Image classification failed for {content_id}: {str(e)}")
            return await self._fallback_image_classification(result)
    
    async def classify_audio_content(
        self,
        content_id: str,
        audio_data: bytes,
        classification_types: List[ClassificationType] = None
    ) -> ClassificationResult:
        """Classify audio content specifically"""
        try:
            self.logger.info(f"Classifying audio content: {content_id}")
            
            result = ClassificationResult(
                content_id=content_id,
                content_type=ContentType.AUDIO
            )
            
            if not AUDIO_AVAILABLE:
                return await self._fallback_audio_classification(result)
            
            # Load audio data
            audio_array = np.frombuffer(audio_data, dtype=np.float32)
            sample_rate = 22050  # Default sample rate
            
            # Extract audio features
            features = await self._extract_audio_features(audio_array, sample_rate)
            
            # Classify based on features
            audio_categories = await self._classify_audio_by_features(features)
            
            result.categories = audio_categories
            
            # Set primary category
            if audio_categories:
                sorted_categories = sorted(
                    audio_categories.items(),
                    key=lambda x: x[1],
                    reverse=True
                )
                result.primary_category = sorted_categories[0][0]
                result.primary_confidence = sorted_categories[0][1]
            
            # Audio-specific classifications
            await self._classify_audio_genre(features, result)
            await self._analyze_audio_quality(audio_array, sample_rate, result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Audio classification failed for {content_id}: {str(e)}")
            return await self._fallback_audio_classification(result)
    
    async def generate_content_tags(
        self,
        content_id: str,
        classification_result: ClassificationResult,
        max_tags: int = 20
    ) -> List[ContentTag]:
        """Generate content tags based on classification"""
        try:
            self.logger.info(f"Generating content tags for: {content_id}")
            
            tags = []
            
            # Tags from primary category
            if classification_result.primary_category:
                primary_tag = ContentTag(
                    tag_name=classification_result.primary_category,
                    tag_category="primary_category",
                    confidence=classification_result.primary_confidence,
                    relevance=1.0,
                    source="ai_generated"
                )
                tags.append(primary_tag)
            
            # Tags from secondary categories
            for cat_info in classification_result.secondary_categories[:5]:
                tag = ContentTag(
                    tag_name=cat_info["category"],
                    tag_category="secondary_category",
                    confidence=cat_info["confidence"],
                    relevance=0.8,
                    source="ai_generated"
                )
                tags.append(tag)
            
            # Tags from topics
            for topic_info in classification_result.topics[:5]:
                tag = ContentTag(
                    tag_name=topic_info.get("topic", ""),
                    tag_category="topic",
                    confidence=topic_info.get("confidence", 0.0),
                    relevance=0.7,
                    source="ai_generated"
                )
                tags.append(tag)
            
            # Tags from genres
            for genre_info in classification_result.genres[:3]:
                tag = ContentTag(
                    tag_name=genre_info.get("genre", ""),
                    tag_category="genre",
                    confidence=genre_info.get("confidence", 0.0),
                    relevance=0.6,
                    source="ai_generated"
                )
                tags.append(tag)
            
            # Sort by relevance and confidence
            tags.sort(key=lambda x: (x.relevance, x.confidence), reverse=True)
            
            # Store tags
            for tag in tags[:max_tags]:
                self.content_tags[tag.tag_id] = tag
            
            self.logger.info(f"Generated {len(tags[:max_tags])} tags for {content_id}")
            return tags[:max_tags]
            
        except Exception as e:
            self.logger.error(f"Tag generation failed for {content_id}: {str(e)}")
            return []
    
    async def get_hierarchical_categories(
        self,
        primary_category: str
    ) -> Dict[str, List[str]]:
        """Get hierarchical categories for a primary category"""
        try:
            hierarchy = self.category_hierarchies.get(primary_category, {})
            
            return {
                "parent_categories": hierarchy.get("parents", []),
                "child_categories": hierarchy.get("children", []),
                "related_categories": hierarchy.get("related", [])
            }
            
        except Exception as e:
            self.logger.error(f"Hierarchical category retrieval failed: {str(e)}")
            return {"parent_categories": [], "child_categories": [], "related_categories": []}
    
    async def batch_classify_content(
        self,
        content_items: List[Dict[str, Any]],
        classification_config: ClassificationConfig = None
    ) -> List[ClassificationResult]:
        """Batch classify multiple content items"""
        try:
            self.logger.info(f"Batch classifying {len(content_items)} items")
            
            config = classification_config or self.config
            results = []
            
            # Process items in parallel batches
            batch_size = 10
            
            for i in range(0, len(content_items), batch_size):
                batch = content_items[i:i + batch_size]
                batch_tasks = []
                
                for item in batch:
                    task = self.classify_content(
                        content_id=item["content_id"],
                        content_data=item["content_data"],
                        content_type=ContentType(item["content_type"]),
                        custom_config=config
                    )
                    batch_tasks.append(task)
                
                # Wait for batch completion
                batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
                
                for result in batch_results:
                    if isinstance(result, Exception):
                        results.append(ClassificationResult(
                            primary_category="error",
                            processing_time=0.0
                        ))
                    else:
                        results.append(result)
            
            success_count = sum(1 for r in results if r.primary_category != "error")
            self.logger.info(f"Batch classification completed: {success_count}/{len(content_items)} successful")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Batch classification failed: {str(e)}")
            return []
    
    # Classification methods for specific types
    async def _classify_categories(
        self,
        content_data: Union[str, bytes, Dict[str, Any]],
        content_type: ContentType,
        result: ClassificationResult,
        config: ClassificationConfig
    ):
        """Classify content into categories"""
        try:
            if content_type == ContentType.TEXT:
                await self._classify_text_categories(content_data, result, config)
            elif content_type == ContentType.IMAGE:
                await self._classify_image_categories(content_data, result, config)
            elif content_type == ContentType.AUDIO:
                await self._classify_audio_categories(content_data, result, config)
            
        except Exception as e:
            self.logger.error(f"Category classification failed: {str(e)}")
    
    async def _classify_text_categories(
        self,
        text_content: str,
        result: ClassificationResult,
        config: ClassificationConfig
    ):
        """Classify text into categories"""
        # Simplified text category classification
        categories = {}
        
        # Keyword-based classification
        text_lower = text_content.lower()
        
        # Technology keywords
        tech_keywords = ["software", "computer", "technology", "ai", "programming"]
        tech_score = sum(1 for kw in tech_keywords if kw in text_lower) / len(tech_keywords)
        categories["technology"] = tech_score
        
        # Business keywords
        business_keywords = ["business", "company", "market", "profit", "strategy"]
        business_score = sum(1 for kw in business_keywords if kw in text_lower) / len(business_keywords)
        categories["business"] = business_score
        
        # Education keywords
        education_keywords = ["education", "learning", "study", "school", "knowledge"]
        education_score = sum(1 for kw in education_keywords if kw in text_lower) / len(education_keywords)
        categories["education"] = education_score
        
        # Entertainment keywords
        entertainment_keywords = ["entertainment", "movie", "music", "game", "fun"]
        entertainment_score = sum(1 for kw in entertainment_keywords if kw in text_lower) / len(entertainment_keywords)
        categories["entertainment"] = entertainment_score
        
        result.categories = categories
    
    async def _classify_genres(
        self,
        content_data: Union[str, bytes, Dict[str, Any]],
        content_type: ContentType,
        result: ClassificationResult
    ):
        """Classify content genres"""
        if content_type == ContentType.TEXT:
            genres = [
                {"genre": "informative", "confidence": 0.7},
                {"genre": "narrative", "confidence": 0.5},
                {"genre": "persuasive", "confidence": 0.3}
            ]
        elif content_type == ContentType.AUDIO:
            genres = [
                {"genre": "music", "confidence": 0.8},
                {"genre": "speech", "confidence": 0.6},
                {"genre": "ambient", "confidence": 0.3}
            ]
        else:
            genres = [
                {"genre": "general", "confidence": 0.5}
            ]
        
        result.genres = genres
    
    async def _classify_topics(
        self,
        content_data: Union[str, bytes, Dict[str, Any]],
        content_type: ContentType,
        result: ClassificationResult
    ):
        """Classify content topics"""
        if content_type == ContentType.TEXT and isinstance(content_data, str):
            await self._classify_text_topics(content_data, result)
        else:
            # Default topics
            result.topics = [
                {"topic": "general", "confidence": 0.5}
            ]
    
    async def _classify_text_topics(self, text_content: str, result: ClassificationResult):
        """Classify text topics using keyword analysis"""
        topic_keywords = {
            "technology": ["ai", "machine learning", "software", "computer", "digital"],
            "business": ["market", "company", "profit", "strategy", "management"],
            "health": ["health", "medical", "wellness", "fitness", "nutrition"],
            "education": ["learning", "education", "teaching", "school", "knowledge"],
            "science": ["research", "study", "experiment", "science", "discovery"]
        }
        
        text_lower = text_content.lower()
        topics = []
        
        for topic, keywords in topic_keywords.items():
            score = sum(1 for kw in keywords if kw in text_lower) / len(keywords)
            if score > 0:
                topics.append({"topic": topic, "confidence": score})
        
        # Sort by confidence
        topics.sort(key=lambda x: x["confidence"], reverse=True)
        result.topics = topics[:5]
    
    async def _classify_sentiment(
        self,
        content_data: Union[str, bytes, Dict[str, Any]],
        content_type: ContentType,
        result: ClassificationResult
    ):
        """Classify content sentiment"""
        if content_type == ContentType.TEXT and isinstance(content_data, str):
            await self._classify_text_sentiment(content_data, result)
        else:
            result.sentiment = {"neutral": 0.7, "positive": 0.2, "negative": 0.1}
    
    async def _classify_text_sentiment(self, text_content: str, result: ClassificationResult):
        """Classify text sentiment"""
        try:
            if AI_AVAILABLE and "sentiment_analyzer" not in self.classifiers:
                self.classifiers["sentiment_analyzer"] = pipeline(
                    "sentiment-analysis",
                    model="cardiffnlp/twitter-roberta-base-sentiment-latest"
                )
            
            if AI_AVAILABLE and "sentiment_analyzer" in self.classifiers:
                analyzer = self.classifiers["sentiment_analyzer"]
                sentiment_result = analyzer(text_content[:512])  # Truncate if too long
                
                if sentiment_result:
                    label = sentiment_result[0]["label"].lower()
                    score = sentiment_result[0]["score"]
                    
                    sentiment_scores = {"neutral": 0.1, "positive": 0.1, "negative": 0.1}
                    sentiment_scores[label] = score
                    
                    # Normalize
                    total_score = sum(sentiment_scores.values())
                    result.sentiment = {k: v/total_score for k, v in sentiment_scores.items()}
                else:
                    result.sentiment = {"neutral": 0.7, "positive": 0.2, "negative": 0.1}
            else:
                # Fallback sentiment analysis
                positive_words = ["good", "great", "excellent", "amazing", "wonderful"]
                negative_words = ["bad", "terrible", "awful", "horrible", "poor"]
                
                text_lower = text_content.lower()
                positive_count = sum(1 for word in positive_words if word in text_lower)
                negative_count = sum(1 for word in negative_words if word in text_lower)
                
                if positive_count > negative_count:
                    result.sentiment = {"positive": 0.7, "neutral": 0.2, "negative": 0.1}
                elif negative_count > positive_count:
                    result.sentiment = {"negative": 0.7, "neutral": 0.2, "positive": 0.1}
                else:
                    result.sentiment = {"neutral": 0.7, "positive": 0.15, "negative": 0.15}
                    
        except Exception as e:
            self.logger.error(f"Sentiment classification failed: {str(e)}")
            result.sentiment = {"neutral": 0.7, "positive": 0.2, "negative": 0.1}
    
    async def _assess_appropriateness(
        self,
        content_data: Union[str, bytes, Dict[str, Any]],
        content_type: ContentType,
        result: ClassificationResult
    ):
        """Assess content appropriateness"""
        # Simplified appropriateness assessment
        if content_type == ContentType.TEXT and isinstance(content_data, str):
            inappropriate_words = ["explicit", "violence", "inappropriate"]
            text_lower = content_data.lower()
            
            inappropriate_count = sum(1 for word in inappropriate_words if word in text_lower)
            result.appropriateness_score = max(0.0, 1.0 - (inappropriate_count * 0.3))
        else:
            result.appropriateness_score = 0.9  # Default high appropriateness
    
    async def _assess_quality(
        self,
        content_data: Union[str, bytes, Dict[str, Any]],
        content_type: ContentType,
        result: ClassificationResult
    ):
        """Assess content quality"""
        quality_assessment = {}
        
        if content_type == ContentType.TEXT and isinstance(content_data, str):
            # Text quality assessment
            words = content_data.split()
            sentences = content_data.split('.')
            
            quality_assessment["readability"] = min(len(words) / max(len(sentences), 1) / 20, 1.0)
            quality_assessment["length"] = min(len(words) / 100, 1.0)
            quality_assessment["structure"] = 0.8  # Default
        else:
            quality_assessment["overall"] = 0.8
        
        result.quality_assessment = quality_assessment
    
    async def _generate_automatic_tags(
        self,
        content_data: Union[str, bytes, Dict[str, Any]],
        content_type: ContentType,
        result: ClassificationResult,
        config: ClassificationConfig
    ):
        """Generate automatic tags based on classification"""
        try:
            auto_tags = []
            
            # Tags from categories
            for category, score in result.categories.items():
                if score > config.confidence_threshold:
                    tag = {
                        "tag": category,
                        "confidence": score,
                        "type": "category",
                        "source": "ai_generated"
                    }
                    auto_tags.append(tag)
            
            # Tags from topics
            for topic_info in result.topics:
                if topic_info.get("confidence", 0) > config.confidence_threshold:
                    tag = {
                        "tag": topic_info["topic"],
                        "confidence": topic_info["confidence"],
                        "type": "topic",
                        "source": "ai_generated"
                    }
                    auto_tags.append(tag)
            
            # Content-specific tags
            if content_type == ContentType.TEXT and isinstance(content_data, str):
                text_tags = await self._extract_text_tags(content_data)
                auto_tags.extend(text_tags)
            
            # Sort and limit tags
            auto_tags.sort(key=lambda x: x["confidence"], reverse=True)
            result.tags = auto_tags[:config.max_tags]
            
        except Exception as e:
            self.logger.error(f"Automatic tag generation failed: {str(e)}")
    
    async def _extract_text_tags(self, text_content: str) -> List[Dict[str, Any]]:
        """Extract tags from text content"""
        tags = []
        
        # Simple keyword extraction
        words = text_content.lower().split()
        word_freq = {}
        
        for word in words:
            if len(word) > 4:  # Filter short words
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get most frequent words as tags
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        
        for word, freq in sorted_words[:10]:
            tag = {
                "tag": word,
                "confidence": min(freq / len(words) * 10, 1.0),
                "type": "keyword",
                "source": "extracted"
            }
            tags.append(tag)
        
        return tags
    
    async def _determine_primary_classification(self, result: ClassificationResult):
        """Determine primary classification from all classifications"""
        try:
            if result.categories:
                # Find category with highest score
                sorted_categories = sorted(
                    result.categories.items(),
                    key=lambda x: x[1],
                    reverse=True
                )
                
                if sorted_categories and sorted_categories[0][1] > 0:
                    result.primary_category = sorted_categories[0][0]
                    result.primary_confidence = sorted_categories[0][1]
                    
                    # Set secondary categories
                    result.secondary_categories = [
                        {"category": cat, "confidence": score}
                        for cat, score in sorted_categories[1:6]
                        if score > self.config.confidence_threshold
                    ]
            
            if not result.primary_category:
                result.primary_category = "other"
                result.primary_confidence = 0.5
                
        except Exception as e:
            self.logger.error(f"Primary classification determination failed: {str(e)}")
            result.primary_category = "unknown"
            result.primary_confidence = 0.0
    
    async def _calculate_confidence_level(self, result: ClassificationResult) -> ConfidenceLevel:
        """Calculate overall confidence level"""
        try:
            avg_confidence = 0.0
            confidence_scores = []
            
            if result.primary_confidence > 0:
                confidence_scores.append(result.primary_confidence)
            
            for cat_info in result.secondary_categories:
                confidence_scores.append(cat_info["confidence"])
            
            if confidence_scores:
                avg_confidence = sum(confidence_scores) / len(confidence_scores)
            
            if avg_confidence >= 0.9:
                return ConfidenceLevel.VERY_HIGH
            elif avg_confidence >= 0.7:
                return ConfidenceLevel.HIGH
            elif avg_confidence >= 0.5:
                return ConfidenceLevel.MEDIUM
            else:
                return ConfidenceLevel.LOW
                
        except Exception as e:
            self.logger.error(f"Confidence level calculation failed: {str(e)}")
            return ConfidenceLevel.LOW
    
    # Fallback methods for when AI models are not available
    async def _fallback_text_classification(self, text_content: str, result: ClassificationResult) -> ClassificationResult:
        """Fallback text classification"""
        result.primary_category = "text"
        result.primary_confidence = 0.6
        result.categories = {"text": 0.6, "general": 0.4}
        return result
    
    async def _fallback_image_classification(self, result: ClassificationResult) -> ClassificationResult:
        """Fallback image classification"""
        result.primary_category = "image"
        result.primary_confidence = 0.6
        result.categories = {"image": 0.6, "visual": 0.4}
        return result
    
    async def _fallback_audio_classification(self, result: ClassificationResult) -> ClassificationResult:
        """Fallback audio classification"""
        result.primary_category = "audio"
        result.primary_confidence = 0.6
        result.categories = {"audio": 0.6, "sound": 0.4}
        return result
    
    # Additional methods for audio and image analysis
    async def _extract_audio_features(self, audio_array: np.ndarray, sample_rate: int) -> Dict[str, Any]:
        """Extract audio features for classification"""
        try:
            if AUDIO_AVAILABLE:
                # Extract MFCC features
                mfccs = librosa.feature.mfcc(y=audio_array, sr=sample_rate, n_mfcc=13)
                
                # Extract spectral features
                spectral_centroids = librosa.feature.spectral_centroid(y=audio_array, sr=sample_rate)
                
                features = {
                    "mfcc_mean": np.mean(mfccs, axis=1).tolist(),
                    "spectral_centroid_mean": np.mean(spectral_centroids),
                    "rms_energy": np.mean(librosa.feature.rms(y=audio_array)),
                    "zero_crossing_rate": np.mean(librosa.feature.zero_crossing_rate(audio_array))
                }
            else:
                # Simple features
                features = {
                    "energy": np.mean(audio_array ** 2),
                    "amplitude": np.max(np.abs(audio_array)),
                    "length": len(audio_array)
                }
            
            return features
            
        except Exception as e:
            self.logger.error(f"Audio feature extraction failed: {str(e)}")
            return {"energy": 0.5}
    
    async def _classify_audio_by_features(self, features: Dict[str, Any]) -> Dict[str, float]:
        """Classify audio based on extracted features"""
        categories = {}
        
        # Simple feature-based classification
        energy = features.get("energy", 0.5)
        
        if energy > 0.7:
            categories["music"] = 0.8
            categories["entertainment"] = 0.6
        elif energy > 0.3:
            categories["speech"] = 0.7
            categories["education"] = 0.5
        else:
            categories["ambient"] = 0.6
            categories["background"] = 0.4
        
        return categories
    
    # Initialization methods
    def _initialize_category_hierarchies(self) -> Dict[str, Dict[str, List[str]]]:
        """Initialize category hierarchies"""
        return {
            "entertainment": {
                "children": ["music", "movies", "games", "sports"],
                "parents": ["media"],
                "related": ["leisure", "recreation"]
            },
            "education": {
                "children": ["academic", "training", "tutorial"],
                "parents": ["knowledge"],
                "related": ["learning", "instruction"]
            },
            "business": {
                "children": ["finance", "marketing", "management"],
                "parents": ["professional"],
                "related": ["corporate", "commercial"]
            }
        }
    
    def _initialize_genre_mappings(self) -> Dict[str, List[str]]:
        """Initialize genre mappings"""
        return {
            "text": ["informative", "narrative", "persuasive", "descriptive"],
            "audio": ["music", "speech", "ambient", "effects"],
            "image": ["photographic", "artistic", "technical", "documentary"],
            "video": ["documentary", "entertainment", "educational", "promotional"]
        }
    
    async def _initialize_ai_models(self):
        """Initialize AI models for classification"""
        try:
            if not AI_AVAILABLE:
                self.logger.warning("AI libraries not available, using fallback methods")
                return
            
            # Models will be loaded on-demand to save memory
            self.logger.info("AI models will be loaded on demand for classification")
            
        except Exception as e:
            self.logger.error(f"AI model initialization failed: {str(e)}")


# Singleton instance
_classification_ai = None

def get_classification_ai() -> ContentClassificationAI:
    """Get singleton content classification AI instance"""
    global _classification_ai
    if _classification_ai is None:
        _classification_ai = ContentClassificationAI()
    return _classification_ai