"""Content Classification AI - Automated Content Classification System

Advanced AI system for automatically classifying and categorizing media content
across multiple dimensions including genre, style, quality, audience, and purpose.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

LEGAL WARNING: This code is the exclusive property of Fahed Mlaiel.
Unauthorized use, reproduction, or distribution is strictly prohibited.
"""

import asyncio
import json
import logging
import numpy as np
from datetime import datetime, timezone
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple, Union, Set
import uuid
from collections import defaultdict

# AI/ML dependencies with graceful fallbacks
try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False
    logging.warning("PyTorch not available - using basic classification")

try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False
    logging.warning("Transformers not available - using rule-based classification")

try:
    import sklearn
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.ensemble import RandomForestClassifier
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False
    logging.warning("Scikit-learn not available - using basic classification")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ClassificationDimension(Enum):
    """Content classification dimensions"""
    GENRE = "genre"
    STYLE = "style"
    QUALITY = "quality"
    TARGET_AUDIENCE = "target_audience"
    PURPOSE = "purpose"
    EMOTION = "emotion"
    COMPLEXITY = "complexity"
    PROFESSIONALISM = "professionalism"
    MONETIZATION_POTENTIAL = "monetization_potential"
    VIRAL_POTENTIAL = "viral_potential"
    BRAND_SAFETY = "brand_safety"
    CONTENT_TYPE = "content_type"


class ContentType(Enum):
    """Types of content"""
    EDUCATIONAL = "educational"
    ENTERTAINMENT = "entertainment"
    PROMOTIONAL = "promotional"
    NEWS = "news"
    TUTORIAL = "tutorial"
    REVIEW = "review"
    DOCUMENTARY = "documentary"
    MUSIC = "music"
    GAMING = "gaming"
    LIFESTYLE = "lifestyle"
    BUSINESS = "business"
    TECHNOLOGY = "technology"
    CREATIVE = "creative"
    PERSONAL = "personal"


class AudienceSegment(Enum):
    """Target audience segments"""
    CHILDREN = "children"
    TEENS = "teens"
    YOUNG_ADULTS = "young_adults"
    ADULTS = "adults"
    SENIORS = "seniors"
    PROFESSIONALS = "professionals"
    STUDENTS = "students"
    PARENTS = "parents"
    ENTREPRENEURS = "entrepreneurs"
    CREATIVES = "creatives"
    GENERAL = "general"


class QualityLevel(Enum):
    """Content quality levels"""
    POOR = "poor"
    BASIC = "basic"
    GOOD = "good"
    EXCELLENT = "excellent"
    PROFESSIONAL = "professional"


class MonetizationPotential(Enum):
    """Monetization potential levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    PREMIUM = "premium"


@dataclass
class ClassificationResult:
    """Classification result for a single dimension"""
    dimension: ClassificationDimension
    predicted_class: str
    confidence: float
    alternatives: List[Tuple[str, float]] = field(default_factory=list)
    features_used: List[str] = field(default_factory=list)
    model_used: str = "unknown"
    processing_time: float = 0.0


@dataclass
class ContentClassification:
    """Complete content classification results"""
    content_id: str
    content_type: Optional[str] = None
    
    # Classification results by dimension
    classifications: Dict[ClassificationDimension, ClassificationResult] = field(default_factory=dict)
    
    # Aggregated insights
    primary_genre: Optional[str] = None
    target_audience: Optional[str] = None
    quality_score: float = 0.0
    monetization_potential: Optional[str] = None
    viral_score: float = 0.0
    brand_safety_score: float = 0.0
    
    # Recommendations
    recommendations: List[Dict[str, Any]] = field(default_factory=list)
    
    # Metadata
    classified_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    total_processing_time: float = 0.0
    confidence_score: float = 0.0


@dataclass
class ClassificationModel:
    """Classification model configuration"""
    dimension: ClassificationDimension
    model_type: str
    model_path: Optional[str] = None
    classes: List[str] = field(default_factory=list)
    features: List[str] = field(default_factory=list)
    accuracy: float = 0.0
    trained_at: Optional[datetime] = None
    version: str = "1.0"


class ContentClassificationAI:
    """Advanced AI-powered content classification system"""
    
    def __init__(self, model_cache_size: int = 10):
        """Initialize content classification AI
        
        Args:
            model_cache_size: Maximum number of models to keep in memory
        """
        self.models: Dict[ClassificationDimension, ClassificationModel] = {}
        self.model_cache = {}
        self.max_cache_size = model_cache_size
        
        # Initialize default models and classification schemes
        self._initialize_classification_schemes()
        self._load_default_models()
        
        logger.info("ContentClassificationAI initialized successfully")
    
    def _initialize_classification_schemes(self):
        """Initialize default classification schemes"""
        self.classification_schemes = {
            ClassificationDimension.GENRE: {
                "classes": [
                    "educational", "entertainment", "news", "tutorial", "review",
                    "documentary", "music", "gaming", "lifestyle", "business",
                    "technology", "creative", "sports", "travel", "food"
                ],
                "features": ["keywords", "structure", "language_style", "visual_elements"]
            },
            ClassificationDimension.TARGET_AUDIENCE: {
                "classes": [
                    "children", "teens", "young_adults", "adults", "seniors",
                    "professionals", "students", "parents", "general"
                ],
                "features": ["language_complexity", "topics", "visual_style", "duration"]
            },
            ClassificationDimension.QUALITY: {
                "classes": ["poor", "basic", "good", "excellent", "professional"],
                "features": ["technical_quality", "content_depth", "presentation", "engagement"]
            },
            ClassificationDimension.PURPOSE: {
                "classes": [
                    "inform", "entertain", "educate", "promote", "inspire",
                    "demonstrate", "persuade", "document", "express"
                ],
                "features": ["intent_keywords", "structure", "call_to_action", "tone"]
            },
            ClassificationDimension.EMOTION: {
                "classes": [
                    "positive", "negative", "neutral", "exciting", "calming",
                    "inspiring", "humorous", "serious", "dramatic"
                ],
                "features": ["sentiment", "energy_level", "color_palette", "music_mood"]
            },
            ClassificationDimension.COMPLEXITY: {
                "classes": ["simple", "moderate", "complex", "expert"],
                "features": ["technical_terms", "concept_density", "prerequisites", "depth"]
            },
            ClassificationDimension.PROFESSIONALISM: {
                "classes": ["casual", "semi_professional", "professional", "corporate"],
                "features": ["production_quality", "presentation_style", "language_formality"]
            },
            ClassificationDimension.MONETIZATION_POTENTIAL: {
                "classes": ["low", "medium", "high", "premium"],
                "features": ["audience_size", "engagement_potential", "commercial_appeal", "niche_value"]
            },
            ClassificationDimension.BRAND_SAFETY: {
                "classes": ["safe", "caution", "risky", "unsafe"],
                "features": ["content_appropriateness", "controversial_topics", "language_safety"]
            }
        }
    
    def _load_default_models(self):
        """Load default classification models"""
        try:
            # Initialize basic models for each dimension
            for dimension, scheme in self.classification_schemes.items():
                model = ClassificationModel(
                    dimension=dimension,
                    model_type="rule_based",
                    classes=scheme["classes"],
                    features=scheme["features"],
                    accuracy=0.75,  # Estimated accuracy for rule-based models
                    trained_at=datetime.now(timezone.utc)
                )
                self.models[dimension] = model
            
            # Load advanced models if transformers available
            if HAS_TRANSFORMERS:
                try:
                    # Sentiment analysis for emotion classification
                    self.sentiment_classifier = pipeline(
                        "sentiment-analysis",
                        model="cardiffnlp/twitter-roberta-base-sentiment-latest"
                    )
                    logger.info("Sentiment analysis model loaded")
                except Exception as e:
                    logger.warning(f"Failed to load sentiment model: {e}")
            
            # Load sklearn models if available
            if HAS_SKLEARN:
                self._initialize_sklearn_models()
                
        except Exception as e:
            logger.error(f"Error loading default models: {e}")
    
    def _initialize_sklearn_models(self):
        """Initialize scikit-learn based models"""
        try:
            # Text vectorizer for feature extraction
            self.text_vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words='english',
                ngram_range=(1, 2)
            )
            
            # Sample classifiers (would be trained with real data)
            self.genre_classifier = RandomForestClassifier(n_estimators=100)
            self.quality_classifier = MultinomialNB()
            
            logger.info("Scikit-learn models initialized")
            
        except Exception as e:
            logger.warning(f"Failed to initialize sklearn models: {e}")
    
    async def classify_content(self, content_data: Dict[str, Any], 
                             dimensions: Optional[List[ClassificationDimension]] = None) -> ContentClassification:
        """Classify content across multiple dimensions
        
        Args:
            content_data: Content information and features
            dimensions: Specific dimensions to classify (if None, classifies all)
            
        Returns:
            Classification results
        """
        try:
            start_time = datetime.now(timezone.utc)
            
            content_id = content_data.get("id", str(uuid.uuid4()))
            classification = ContentClassification(content_id=content_id)
            
            # Determine dimensions to classify
            if dimensions is None:
                dimensions = list(self.classification_schemes.keys())
            
            # Extract features from content
            features = await self._extract_classification_features(content_data)
            
            # Classify each dimension
            for dimension in dimensions:
                try:
                    result = await self._classify_dimension(dimension, features, content_data)
                    if result:
                        classification.classifications[dimension] = result
                except Exception as e:
                    logger.error(f"Error classifying dimension {dimension}: {e}")
            
            # Generate aggregated insights
            await self._generate_aggregated_insights(classification, features)
            
            # Generate recommendations
            classification.recommendations = await self._generate_classification_recommendations(
                classification, features
            )
            
            # Calculate overall confidence
            if classification.classifications:
                confidences = [r.confidence for r in classification.classifications.values()]
                classification.confidence_score = np.mean(confidences)
            
            # Record processing time
            end_time = datetime.now(timezone.utc)
            classification.total_processing_time = (end_time - start_time).total_seconds()
            
            logger.info(f"Classified content {content_id} across {len(dimensions)} dimensions")
            return classification
            
        except Exception as e:
            logger.error(f"Error in content classification: {e}")
            raise
    
    async def _extract_classification_features(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract features for classification
        
        Args:
            content_data: Raw content data
            
        Returns:
            Extracted features
        """
        features = {
            "text_content": "",
            "keywords": [],
            "metadata": {},
            "technical_quality": 0.7,
            "duration": 0,
            "file_size": 0,
            "language_complexity": 0.5,
            "visual_elements": [],
            "audio_features": {}
        }
        
        try:
            # Extract text content
            if "text" in content_data:
                features["text_content"] = content_data["text"]
                features["keywords"] = await self._extract_keywords(content_data["text"])
                features["language_complexity"] = self._calculate_language_complexity(content_data["text"])
            
            # Extract metadata
            features["metadata"] = content_data.get("metadata", {})
            features["title"] = content_data.get("title", "")
            features["description"] = content_data.get("description", "")
            
            # Extract technical features
            if "file_info" in content_data:
                file_info = content_data["file_info"]
                features["duration"] = file_info.get("duration", 0)
                features["file_size"] = file_info.get("file_size", 0)
                features["resolution"] = file_info.get("resolution", (0, 0))
                features["format"] = file_info.get("format", "")
            
            # Extract visual features
            if "visual_analysis" in content_data:
                visual = content_data["visual_analysis"]
                features["visual_elements"] = visual.get("detected_objects", [])
                features["color_palette"] = visual.get("dominant_colors", [])
                features["visual_complexity"] = visual.get("complexity_score", 0.5)
            
            # Extract audio features
            if "audio_analysis" in content_data:
                audio = content_data["audio_analysis"]
                features["audio_features"] = {
                    "tempo": audio.get("tempo", 120),
                    "energy": audio.get("energy", 0.5),
                    "mood": audio.get("mood", "neutral"),
                    "has_speech": audio.get("has_speech", False),
                    "has_music": audio.get("has_music", False)
                }
            
            # Calculate derived features
            features["content_length_category"] = self._categorize_content_length(features["duration"])
            features["production_quality_score"] = self._estimate_production_quality(features)
            features["engagement_indicators"] = self._extract_engagement_indicators(features)
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting classification features: {e}")
            return features
    
    async def _classify_dimension(self, dimension: ClassificationDimension, 
                                features: Dict[str, Any], 
                                content_data: Dict[str, Any]) -> Optional[ClassificationResult]:
        """Classify content for a specific dimension
        
        Args:
            dimension: Classification dimension
            features: Extracted features
            content_data: Original content data
            
        Returns:
            Classification result
        """
        try:
            start_time = datetime.now()
            
            if dimension == ClassificationDimension.GENRE:
                result = await self._classify_genre(features)
            elif dimension == ClassificationDimension.TARGET_AUDIENCE:
                result = await self._classify_target_audience(features)
            elif dimension == ClassificationDimension.QUALITY:
                result = await self._classify_quality(features)
            elif dimension == ClassificationDimension.PURPOSE:
                result = await self._classify_purpose(features)
            elif dimension == ClassificationDimension.EMOTION:
                result = await self._classify_emotion(features)
            elif dimension == ClassificationDimension.COMPLEXITY:
                result = await self._classify_complexity(features)
            elif dimension == ClassificationDimension.PROFESSIONALISM:
                result = await self._classify_professionalism(features)
            elif dimension == ClassificationDimension.MONETIZATION_POTENTIAL:
                result = await self._classify_monetization_potential(features)
            elif dimension == ClassificationDimension.BRAND_SAFETY:
                result = await self._classify_brand_safety(features)
            else:
                logger.warning(f"Unknown classification dimension: {dimension}")
                return None
            
            # Record processing time
            if result:
                result.processing_time = (datetime.now() - start_time).total_seconds()
            
            return result
            
        except Exception as e:
            logger.error(f"Error classifying dimension {dimension}: {e}")
            return None
    
    async def _classify_genre(self, features: Dict[str, Any]) -> ClassificationResult:
        """Classify content genre"""
        try:
            # Rule-based genre classification
            text_content = features.get("text_content", "").lower()
            keywords = features.get("keywords", [])
            title = features.get("title", "").lower()
            
            genre_scores = {}
            
            # Educational indicators
            educational_keywords = ["learn", "tutorial", "guide", "how to", "explain", "course", "lesson"]
            educational_score = sum(1 for keyword in educational_keywords if keyword in text_content)
            genre_scores["educational"] = educational_score / 10
            
            # Entertainment indicators
            entertainment_keywords = ["fun", "funny", "comedy", "entertainment", "show", "game", "play"]
            entertainment_score = sum(1 for keyword in entertainment_keywords if keyword in text_content)
            genre_scores["entertainment"] = entertainment_score / 10
            
            # Business indicators
            business_keywords = ["business", "marketing", "strategy", "profit", "revenue", "corporate"]
            business_score = sum(1 for keyword in business_keywords if keyword in text_content)
            genre_scores["business"] = business_score / 10
            
            # Technology indicators
            tech_keywords = ["technology", "software", "programming", "code", "digital", "app", "tech"]
            tech_score = sum(1 for keyword in tech_keywords if keyword in text_content)
            genre_scores["technology"] = tech_score / 10
            
            # Music indicators
            music_keywords = ["music", "song", "album", "artist", "band", "concert", "audio"]
            music_score = sum(1 for keyword in music_keywords if keyword in text_content)
            if features.get("audio_features", {}).get("has_music", False):
                music_score += 0.5
            genre_scores["music"] = music_score / 10
            
            # Review indicators
            review_keywords = ["review", "rating", "opinion", "recommend", "pros", "cons", "verdict"]
            review_score = sum(1 for keyword in review_keywords if keyword in text_content)
            genre_scores["review"] = review_score / 10
            
            # Default to general if no strong indicators
            if not any(score > 0.3 for score in genre_scores.values()):
                genre_scores["general"] = 0.5
            
            # Find best genre
            best_genre = max(genre_scores, key=genre_scores.get)
            confidence = min(genre_scores[best_genre], 1.0)
            
            # Generate alternatives
            alternatives = sorted(
                [(genre, score) for genre, score in genre_scores.items() if genre != best_genre],
                key=lambda x: x[1], reverse=True
            )[:3]
            
            return ClassificationResult(
                dimension=ClassificationDimension.GENRE,
                predicted_class=best_genre,
                confidence=confidence,
                alternatives=alternatives,
                features_used=["text_content", "keywords", "audio_features"],
                model_used="rule_based"
            )
            
        except Exception as e:
            logger.error(f"Error in genre classification: {e}")
            return ClassificationResult(
                dimension=ClassificationDimension.GENRE,
                predicted_class="general",
                confidence=0.5,
                model_used="fallback"
            )
    
    async def _classify_target_audience(self, features: Dict[str, Any]) -> ClassificationResult:
        """Classify target audience"""
        try:
            text_content = features.get("text_content", "").lower()
            language_complexity = features.get("language_complexity", 0.5)
            duration = features.get("duration", 0)
            
            audience_scores = {}
            
            # Children indicators
            children_keywords = ["kids", "children", "family", "cartoon", "animation", "simple"]
            children_score = sum(1 for keyword in children_keywords if keyword in text_content)
            if language_complexity < 0.3:
                children_score += 0.3
            if 0 < duration < 300:  # Short content
                children_score += 0.2
            audience_scores["children"] = children_score / 5
            
            # Teens indicators
            teen_keywords = ["teen", "young", "school", "college", "gaming", "social media"]
            teen_score = sum(1 for keyword in teen_keywords if keyword in text_content)
            if 0.3 <= language_complexity < 0.6:
                teen_score += 0.2
            audience_scores["teens"] = teen_score / 5
            
            # Professionals indicators
            professional_keywords = ["professional", "business", "career", "workplace", "industry"]
            professional_score = sum(1 for keyword in professional_keywords if keyword in text_content)
            if language_complexity > 0.7:
                professional_score += 0.3
            audience_scores["professionals"] = professional_score / 5
            
            # General adult indicators
            adult_keywords = ["adult", "mature", "general", "lifestyle"]
            adult_score = sum(1 for keyword in adult_keywords if keyword in text_content)
            if 0.4 <= language_complexity <= 0.7:
                adult_score += 0.3
            audience_scores["adults"] = adult_score / 5
            
            # Students indicators
            student_keywords = ["student", "learn", "study", "education", "university", "academic"]
            student_score = sum(1 for keyword in student_keywords if keyword in text_content)
            audience_scores["students"] = student_score / 5
            
            # Default to general
            if not any(score > 0.3 for score in audience_scores.values()):
                audience_scores["general"] = 0.6
            
            best_audience = max(audience_scores, key=audience_scores.get)
            confidence = min(audience_scores[best_audience], 1.0)
            
            alternatives = sorted(
                [(aud, score) for aud, score in audience_scores.items() if aud != best_audience],
                key=lambda x: x[1], reverse=True
            )[:3]
            
            return ClassificationResult(
                dimension=ClassificationDimension.TARGET_AUDIENCE,
                predicted_class=best_audience,
                confidence=confidence,
                alternatives=alternatives,
                features_used=["text_content", "language_complexity", "duration"],
                model_used="rule_based"
            )
            
        except Exception as e:
            logger.error(f"Error in audience classification: {e}")
            return ClassificationResult(
                dimension=ClassificationDimension.TARGET_AUDIENCE,
                predicted_class="general",
                confidence=0.5,
                model_used="fallback"
            )
    
    async def _classify_quality(self, features: Dict[str, Any]) -> ClassificationResult:
        """Classify content quality"""
        try:
            quality_score = 0.0
            
            # Technical quality factors
            production_quality = features.get("production_quality_score", 0.5)
            quality_score += production_quality * 0.3
            
            # Content depth (based on text length and complexity)
            text_length = len(features.get("text_content", ""))
            if text_length > 1000:
                quality_score += 0.2
            elif text_length > 500:
                quality_score += 0.15
            elif text_length > 100:
                quality_score += 0.1
            
            # Language complexity
            language_complexity = features.get("language_complexity", 0.5)
            quality_score += language_complexity * 0.2
            
            # Duration appropriateness
            duration = features.get("duration", 0)
            if 300 <= duration <= 3600:  # 5 minutes to 1 hour
                quality_score += 0.15
            elif 60 <= duration < 300 or 3600 < duration <= 7200:
                quality_score += 0.1
            else:
                quality_score += 0.05
            
            # Visual/Audio quality
            visual_complexity = features.get("visual_complexity", 0.5)
            quality_score += visual_complexity * 0.15
            
            # Normalize to 0-1
            quality_score = min(quality_score, 1.0)
            
            # Map to quality levels
            if quality_score >= 0.9:
                quality_level = "professional"
                confidence = 0.9
            elif quality_score >= 0.75:
                quality_level = "excellent"
                confidence = 0.85
            elif quality_score >= 0.6:
                quality_level = "good"
                confidence = 0.8
            elif quality_score >= 0.4:
                quality_level = "basic"
                confidence = 0.75
            else:
                quality_level = "poor"
                confidence = 0.7
            
            # Generate alternatives
            quality_levels = ["poor", "basic", "good", "excellent", "professional"]
            current_index = quality_levels.index(quality_level)
            
            alternatives = []
            for i, level in enumerate(quality_levels):
                if i != current_index:
                    # Distance-based scoring
                    distance = abs(i - current_index)
                    alt_score = max(0, quality_score - (distance * 0.2))
                    alternatives.append((level, alt_score))
            
            alternatives = sorted(alternatives, key=lambda x: x[1], reverse=True)[:3]
            
            return ClassificationResult(
                dimension=ClassificationDimension.QUALITY,
                predicted_class=quality_level,
                confidence=confidence,
                alternatives=alternatives,
                features_used=["production_quality_score", "text_content", "language_complexity", "duration"],
                model_used="composite_scoring"
            )
            
        except Exception as e:
            logger.error(f"Error in quality classification: {e}")
            return ClassificationResult(
                dimension=ClassificationDimension.QUALITY,
                predicted_class="basic",
                confidence=0.5,
                model_used="fallback"
            )
    
    async def _classify_purpose(self, features: Dict[str, Any]) -> ClassificationResult:
        """Classify content purpose"""
        try:
            text_content = features.get("text_content", "").lower()
            title = features.get("title", "").lower()
            
            purpose_scores = {}
            
            # Inform purpose
            inform_keywords = ["news", "information", "facts", "data", "report", "update", "announce"]
            inform_score = sum(1 for keyword in inform_keywords if keyword in text_content or keyword in title)
            purpose_scores["inform"] = inform_score / 10
            
            # Educate purpose
            educate_keywords = ["learn", "teach", "education", "tutorial", "guide", "explain", "course"]
            educate_score = sum(1 for keyword in educate_keywords if keyword in text_content or keyword in title)
            purpose_scores["educate"] = educate_score / 10
            
            # Entertain purpose
            entertain_keywords = ["fun", "entertainment", "comedy", "humor", "amusing", "enjoyable"]
            entertain_score = sum(1 for keyword in entertain_keywords if keyword in text_content or keyword in title)
            purpose_scores["entertain"] = entertain_score / 10
            
            # Promote purpose
            promote_keywords = ["buy", "sale", "offer", "discount", "brand", "product", "service", "advertise"]
            promote_score = sum(1 for keyword in promote_keywords if keyword in text_content or keyword in title)
            purpose_scores["promote"] = promote_score / 10
            
            # Inspire purpose
            inspire_keywords = ["inspire", "motivate", "success", "achievement", "dream", "goal", "aspire"]
            inspire_score = sum(1 for keyword in inspire_keywords if keyword in text_content or keyword in title)
            purpose_scores["inspire"] = inspire_score / 10
            
            # Demonstrate purpose
            demo_keywords = ["demo", "demonstration", "show how", "example", "walkthrough", "step by step"]
            demo_score = sum(1 for keyword in demo_keywords if keyword in text_content or keyword in title)
            purpose_scores["demonstrate"] = demo_score / 10
            
            # Default to inform if no clear purpose
            if not any(score > 0.2 for score in purpose_scores.values()):
                purpose_scores["inform"] = 0.5
            
            best_purpose = max(purpose_scores, key=purpose_scores.get)
            confidence = min(purpose_scores[best_purpose], 1.0)
            
            alternatives = sorted(
                [(purpose, score) for purpose, score in purpose_scores.items() if purpose != best_purpose],
                key=lambda x: x[1], reverse=True
            )[:3]
            
            return ClassificationResult(
                dimension=ClassificationDimension.PURPOSE,
                predicted_class=best_purpose,
                confidence=confidence,
                alternatives=alternatives,
                features_used=["text_content", "title"],
                model_used="keyword_analysis"
            )
            
        except Exception as e:
            logger.error(f"Error in purpose classification: {e}")
            return ClassificationResult(
                dimension=ClassificationDimension.PURPOSE,
                predicted_class="inform",
                confidence=0.5,
                model_used="fallback"
            )
    
    async def _classify_emotion(self, features: Dict[str, Any]) -> ClassificationResult:
        """Classify emotional tone"""
        try:
            text_content = features.get("text_content", "")
            
            # Use transformer model if available
            if hasattr(self, "sentiment_classifier") and text_content:
                try:
                    sentiment_result = self.sentiment_classifier(text_content[:512])
                    
                    # Map sentiment to emotion categories
                    emotion_mapping = {
                        "POSITIVE": "positive",
                        "NEGATIVE": "negative",
                        "NEUTRAL": "neutral"
                    }
                    
                    sentiment_label = sentiment_result[0]["label"]
                    confidence = sentiment_result[0]["score"]
                    emotion = emotion_mapping.get(sentiment_label, "neutral")
                    
                    return ClassificationResult(
                        dimension=ClassificationDimension.EMOTION,
                        predicted_class=emotion,
                        confidence=confidence,
                        features_used=["text_content"],
                        model_used="transformer_sentiment"
                    )
                    
                except Exception as e:
                    logger.warning(f"Transformer sentiment analysis failed: {e}")
            
            # Fallback to rule-based emotion classification
            emotion_scores = {}
            text_lower = text_content.lower()
            
            # Positive emotion keywords
            positive_keywords = ["happy", "joy", "excited", "amazing", "wonderful", "great", "love", "fantastic"]
            positive_score = sum(1 for keyword in positive_keywords if keyword in text_lower)
            emotion_scores["positive"] = positive_score / 20
            
            # Negative emotion keywords
            negative_keywords = ["sad", "angry", "hate", "terrible", "awful", "bad", "disappointed", "frustrated"]
            negative_score = sum(1 for keyword in negative_keywords if keyword in text_lower)
            emotion_scores["negative"] = negative_score / 20
            
            # Exciting keywords
            exciting_keywords = ["exciting", "thrilling", "adventure", "energy", "dynamic", "fast", "action"]
            exciting_score = sum(1 for keyword in exciting_keywords if keyword in text_lower)
            emotion_scores["exciting"] = exciting_score / 20
            
            # Calming keywords
            calming_keywords = ["calm", "peaceful", "relaxing", "gentle", "quiet", "serene", "tranquil"]
            calming_score = sum(1 for keyword in calming_keywords if keyword in text_lower)
            emotion_scores["calming"] = calming_score / 20
            
            # Consider audio features
            audio_features = features.get("audio_features", {})
            if audio_features:
                tempo = audio_features.get("tempo", 120)
                energy = audio_features.get("energy", 0.5)
                
                if tempo > 140 and energy > 0.7:
                    emotion_scores["exciting"] += 0.3
                elif tempo < 80 and energy < 0.3:
                    emotion_scores["calming"] += 0.3
            
            # Default to neutral
            if not any(score > 0.2 for score in emotion_scores.values()):
                emotion_scores["neutral"] = 0.6
            
            best_emotion = max(emotion_scores, key=emotion_scores.get)
            confidence = min(emotion_scores[best_emotion], 1.0)
            
            alternatives = sorted(
                [(emotion, score) for emotion, score in emotion_scores.items() if emotion != best_emotion],
                key=lambda x: x[1], reverse=True
            )[:3]
            
            return ClassificationResult(
                dimension=ClassificationDimension.EMOTION,
                predicted_class=best_emotion,
                confidence=confidence,
                alternatives=alternatives,
                features_used=["text_content", "audio_features"],
                model_used="rule_based_emotion"
            )
            
        except Exception as e:
            logger.error(f"Error in emotion classification: {e}")
            return ClassificationResult(
                dimension=ClassificationDimension.EMOTION,
                predicted_class="neutral",
                confidence=0.5,
                model_used="fallback"
            )
    
    async def _classify_complexity(self, features: Dict[str, Any]) -> ClassificationResult:
        """Classify content complexity"""
        try:
            complexity_score = 0.0
            
            # Language complexity
            language_complexity = features.get("language_complexity", 0.5)
            complexity_score += language_complexity * 0.4
            
            # Content length factor
            text_length = len(features.get("text_content", ""))
            if text_length > 2000:
                complexity_score += 0.2
            elif text_length > 1000:
                complexity_score += 0.15
            elif text_length > 500:
                complexity_score += 0.1
            
            # Technical terms detection
            text_content = features.get("text_content", "").lower()
            technical_keywords = [
                "algorithm", "implementation", "framework", "architecture", "methodology",
                "optimization", "analysis", "synthesis", "paradigm", "infrastructure"
            ]
            tech_score = sum(1 for keyword in technical_keywords if keyword in text_content)
            complexity_score += min(tech_score / 10, 0.3)
            
            # Duration factor
            duration = features.get("duration", 0)
            if duration > 3600:  # > 1 hour
                complexity_score += 0.1
            elif duration > 1800:  # > 30 minutes
                complexity_score += 0.05
            
            # Normalize
            complexity_score = min(complexity_score, 1.0)
            
            # Map to complexity levels
            if complexity_score >= 0.8:
                complexity_level = "expert"
                confidence = 0.85
            elif complexity_score >= 0.6:
                complexity_level = "complex"
                confidence = 0.8
            elif complexity_score >= 0.4:
                complexity_level = "moderate"
                confidence = 0.8
            else:
                complexity_level = "simple"
                confidence = 0.75
            
            return ClassificationResult(
                dimension=ClassificationDimension.COMPLEXITY,
                predicted_class=complexity_level,
                confidence=confidence,
                features_used=["language_complexity", "text_content", "duration"],
                model_used="composite_complexity"
            )
            
        except Exception as e:
            logger.error(f"Error in complexity classification: {e}")
            return ClassificationResult(
                dimension=ClassificationDimension.COMPLEXITY,
                predicted_class="moderate",
                confidence=0.5,
                model_used="fallback"
            )
    
    async def _classify_professionalism(self, features: Dict[str, Any]) -> ClassificationResult:
        """Classify professionalism level"""
        try:
            professionalism_score = 0.0
            
            # Production quality
            production_quality = features.get("production_quality_score", 0.5)
            professionalism_score += production_quality * 0.4
            
            # Language formality
            text_content = features.get("text_content", "").lower()
            formal_indicators = [
                "we are pleased", "furthermore", "therefore", "consequently", "moreover",
                "professional", "corporate", "business", "enterprise", "organization"
            ]
            formal_score = sum(1 for indicator in formal_indicators if indicator in text_content)
            professionalism_score += min(formal_score / 10, 0.3)
            
            # Casual indicators (negative for professionalism)
            casual_indicators = ["lol", "omg", "yeah", "gonna", "wanna", "hey guys", "awesome", "cool"]
            casual_score = sum(1 for indicator in casual_indicators if indicator in text_content)
            professionalism_score -= min(casual_score / 10, 0.2)
            
            # Technical presentation
            if features.get("visual_elements"):
                professionalism_score += 0.1
            
            # Duration appropriateness for professional content
            duration = features.get("duration", 0)
            if 300 <= duration <= 1800:  # 5-30 minutes is professional
                professionalism_score += 0.1
            
            # Normalize
            professionalism_score = max(0, min(professionalism_score, 1.0))
            
            # Map to professionalism levels
            if professionalism_score >= 0.8:
                level = "corporate"
                confidence = 0.85
            elif professionalism_score >= 0.6:
                level = "professional"
                confidence = 0.8
            elif professionalism_score >= 0.4:
                level = "semi_professional"
                confidence = 0.75
            else:
                level = "casual"
                confidence = 0.7
            
            return ClassificationResult(
                dimension=ClassificationDimension.PROFESSIONALISM,
                predicted_class=level,
                confidence=confidence,
                features_used=["production_quality_score", "text_content", "visual_elements"],
                model_used="formality_analysis"
            )
            
        except Exception as e:
            logger.error(f"Error in professionalism classification: {e}")
            return ClassificationResult(
                dimension=ClassificationDimension.PROFESSIONALISM,
                predicted_class="semi_professional",
                confidence=0.5,
                model_used="fallback"
            )
    
    async def _classify_monetization_potential(self, features: Dict[str, Any]) -> ClassificationResult:
        """Classify monetization potential"""
        try:
            monetization_score = 0.0
            
            # Quality factor
            production_quality = features.get("production_quality_score", 0.5)
            monetization_score += production_quality * 0.3
            
            # Content length (longer content often has higher monetization potential)
            duration = features.get("duration", 0)
            if duration >= 600:  # 10+ minutes
                monetization_score += 0.2
            elif duration >= 300:  # 5+ minutes
                monetization_score += 0.15
            elif duration >= 120:  # 2+ minutes
                monetization_score += 0.1
            
            # Commercial indicators
            text_content = features.get("text_content", "").lower()
            commercial_keywords = [
                "brand", "product", "service", "business", "marketing", "advertise",
                "sponsor", "partnership", "collaboration", "monetize", "revenue"
            ]
            commercial_score = sum(1 for keyword in commercial_keywords if keyword in text_content)
            monetization_score += min(commercial_score / 10, 0.2)
            
            # Target audience value
            engagement_indicators = features.get("engagement_indicators", [])
            if "professional_audience" in engagement_indicators:
                monetization_score += 0.15
            if "broad_appeal" in engagement_indicators:
                monetization_score += 0.1
            
            # Content category value
            keywords = features.get("keywords", [])
            high_value_topics = ["business", "finance", "technology", "education", "health", "lifestyle"]
            topic_value = sum(1 for topic in high_value_topics if any(topic in keyword for keyword in keywords))
            monetization_score += min(topic_value / 10, 0.15)
            
            # Normalize
            monetization_score = min(monetization_score, 1.0)
            
            # Map to monetization levels
            if monetization_score >= 0.75:
                level = "premium"
                confidence = 0.85
            elif monetization_score >= 0.6:
                level = "high"
                confidence = 0.8
            elif monetization_score >= 0.4:
                level = "medium"
                confidence = 0.75
            else:
                level = "low"
                confidence = 0.7
            
            return ClassificationResult(
                dimension=ClassificationDimension.MONETIZATION_POTENTIAL,
                predicted_class=level,
                confidence=confidence,
                features_used=["production_quality_score", "duration", "text_content", "keywords"],
                model_used="commercial_analysis"
            )
            
        except Exception as e:
            logger.error(f"Error in monetization classification: {e}")
            return ClassificationResult(
                dimension=ClassificationDimension.MONETIZATION_POTENTIAL,
                predicted_class="medium",
                confidence=0.5,
                model_used="fallback"
            )
    
    async def _classify_brand_safety(self, features: Dict[str, Any]) -> ClassificationResult:
        """Classify brand safety level"""
        try:
            safety_score = 1.0  # Start with safe
            
            text_content = features.get("text_content", "").lower()
            
            # Controversial topics (reduce safety)
            controversial_keywords = [
                "controversy", "scandal", "conflict", "politics", "religion", "violence",
                "inappropriate", "offensive", "controversial", "debate", "argument"
            ]
            controversial_count = sum(1 for keyword in controversial_keywords if keyword in text_content)
            safety_score -= min(controversial_count / 10, 0.4)
            
            # Negative language (reduce safety)
            negative_keywords = [
                "hate", "anger", "violence", "illegal", "dangerous", "harmful",
                "toxic", "abuse", "discrimination", "explicit"
            ]
            negative_count = sum(1 for keyword in negative_keywords if keyword in text_content)
            safety_score -= min(negative_count / 10, 0.3)
            
            # Professional indicators (increase safety)
            professional_keywords = [
                "professional", "business", "educational", "informative", "helpful",
                "positive", "constructive", "family-friendly", "appropriate"
            ]
            professional_count = sum(1 for keyword in professional_keywords if keyword in text_content)
            safety_score += min(professional_count / 20, 0.2)
            
            # Quality factor (higher quality often safer)
            production_quality = features.get("production_quality_score", 0.5)
            if production_quality > 0.7:
                safety_score += 0.1
            
            # Normalize
            safety_score = max(0, min(safety_score, 1.0))
            
            # Map to safety levels
            if safety_score >= 0.8:
                level = "safe"
                confidence = 0.9
            elif safety_score >= 0.6:
                level = "caution"
                confidence = 0.8
            elif safety_score >= 0.4:
                level = "risky"
                confidence = 0.75
            else:
                level = "unsafe"
                confidence = 0.8
            
            return ClassificationResult(
                dimension=ClassificationDimension.BRAND_SAFETY,
                predicted_class=level,
                confidence=confidence,
                features_used=["text_content", "production_quality_score"],
                model_used="safety_analysis"
            )
            
        except Exception as e:
            logger.error(f"Error in brand safety classification: {e}")
            return ClassificationResult(
                dimension=ClassificationDimension.BRAND_SAFETY,
                predicted_class="caution",
                confidence=0.5,
                model_used="fallback"
            )
    
    async def _generate_aggregated_insights(self, classification: ContentClassification, 
                                          features: Dict[str, Any]):
        """Generate aggregated insights from individual classifications"""
        try:
            # Primary genre
            if ClassificationDimension.GENRE in classification.classifications:
                classification.primary_genre = classification.classifications[ClassificationDimension.GENRE].predicted_class
            
            # Target audience
            if ClassificationDimension.TARGET_AUDIENCE in classification.classifications:
                classification.target_audience = classification.classifications[ClassificationDimension.TARGET_AUDIENCE].predicted_class
            
            # Quality score
            if ClassificationDimension.QUALITY in classification.classifications:
                quality_result = classification.classifications[ClassificationDimension.QUALITY]
                quality_mapping = {"poor": 0.2, "basic": 0.4, "good": 0.6, "excellent": 0.8, "professional": 1.0}
                classification.quality_score = quality_mapping.get(quality_result.predicted_class, 0.5)
            
            # Monetization potential
            if ClassificationDimension.MONETIZATION_POTENTIAL in classification.classifications:
                classification.monetization_potential = classification.classifications[ClassificationDimension.MONETIZATION_POTENTIAL].predicted_class
            
            # Viral score (simplified calculation)
            viral_factors = []
            
            # Emotion factor
            if ClassificationDimension.EMOTION in classification.classifications:
                emotion = classification.classifications[ClassificationDimension.EMOTION].predicted_class
                if emotion in ["exciting", "positive", "inspiring"]:
                    viral_factors.append(0.3)
                elif emotion == "humorous":
                    viral_factors.append(0.4)
                else:
                    viral_factors.append(0.1)
            
            # Quality factor
            viral_factors.append(classification.quality_score * 0.2)
            
            # Duration factor (shorter content often more viral)
            duration = features.get("duration", 0)
            if 15 <= duration <= 300:  # 15 seconds to 5 minutes
                viral_factors.append(0.2)
            elif 300 < duration <= 600:
                viral_factors.append(0.15)
            else:
                viral_factors.append(0.05)
            
            # Engagement indicators
            engagement_indicators = features.get("engagement_indicators", [])
            if "broad_appeal" in engagement_indicators:
                viral_factors.append(0.15)
            if "interactive_elements" in engagement_indicators:
                viral_factors.append(0.1)
            
            classification.viral_score = min(sum(viral_factors), 1.0)
            
            # Brand safety score
            if ClassificationDimension.BRAND_SAFETY in classification.classifications:
                safety_result = classification.classifications[ClassificationDimension.BRAND_SAFETY]
                safety_mapping = {"unsafe": 0.2, "risky": 0.4, "caution": 0.6, "safe": 0.9}
                classification.brand_safety_score = safety_mapping.get(safety_result.predicted_class, 0.5)
            
        except Exception as e:
            logger.error(f"Error generating aggregated insights: {e}")
    
    async def _generate_classification_recommendations(self, classification: ContentClassification,
                                                     features: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate actionable recommendations based on classification"""
        recommendations = []
        
        try:
            # Quality improvements
            if classification.quality_score < 0.6:
                recommendations.append({
                    "type": "quality_improvement",
                    "priority": "high",
                    "title": "Improve Content Quality",
                    "description": "Consider enhancing production quality, content depth, or presentation",
                    "specific_actions": [
                        "Improve audio/video quality",
                        "Add more detailed content",
                        "Enhance visual presentation"
                    ]
                })
            
            # Monetization opportunities
            if (classification.monetization_potential in ["medium", "high", "premium"] and 
                classification.quality_score > 0.6):
                recommendations.append({
                    "type": "monetization",
                    "priority": "medium",
                    "title": "Monetization Opportunity",
                    "description": f"This content has {classification.monetization_potential} monetization potential",
                    "specific_actions": [
                        "Consider enabling advertisements",
                        "Explore sponsorship opportunities",
                        "Create premium version"
                    ]
                })
            
            # Audience targeting
            if classification.target_audience and classification.target_audience != "general":
                recommendations.append({
                    "type": "audience_targeting",
                    "priority": "medium",
                    "title": "Audience-Specific Optimization",
                    "description": f"Optimize for {classification.target_audience} audience",
                    "specific_actions": [
                        f"Tailor content style for {classification.target_audience}",
                        "Adjust complexity level appropriately",
                        "Use audience-specific platforms"
                    ]
                })
            
            # Brand safety concerns
            if classification.brand_safety_score < 0.7:
                recommendations.append({
                    "type": "brand_safety",
                    "priority": "high",
                    "title": "Brand Safety Review",
                    "description": "Content may have brand safety concerns",
                    "specific_actions": [
                        "Review content for controversial topics",
                        "Consider content moderation",
                        "Add appropriate disclaimers"
                    ]
                })
            
            # Viral potential optimization
            if classification.viral_score > 0.6:
                recommendations.append({
                    "type": "viral_optimization",
                    "priority": "low",
                    "title": "Viral Potential Enhancement",
                    "description": "Content shows good viral potential",
                    "specific_actions": [
                        "Optimize for social media sharing",
                        "Add engaging hooks",
                        "Time release for maximum impact"
                    ]
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return []
    
    # Helper methods
    async def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text (simplified)"""
        try:
            words = text.lower().split()
            # Remove common stop words
            stop_words = {"the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "a", "an"}
            keywords = [word.strip(".,!?;:") for word in words if word not in stop_words and len(word) > 3]
            
            # Return most frequent words as keywords
            word_freq = {}
            for word in keywords:
                word_freq[word] = word_freq.get(word, 0) + 1
            
            sorted_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
            return [word for word, freq in sorted_keywords[:20]]  # Top 20 keywords
            
        except Exception:
            return []
    
    def _calculate_language_complexity(self, text: str) -> float:
        """Calculate language complexity score"""
        try:
            words = text.split()
            sentences = text.split('.')
            
            if not words or not sentences:
                return 0.5
            
            # Average word length
            avg_word_length = sum(len(word) for word in words) / len(words)
            
            # Average sentence length
            avg_sentence_length = len(words) / len(sentences)
            
            # Complex word count (words > 6 characters)
            complex_words = sum(1 for word in words if len(word) > 6)
            complex_ratio = complex_words / len(words)
            
            # Combine factors
            complexity = (
                min(avg_word_length / 10, 0.4) +
                min(avg_sentence_length / 30, 0.4) +
                min(complex_ratio, 0.2)
            )
            
            return min(complexity, 1.0)
            
        except Exception:
            return 0.5
    
    def _categorize_content_length(self, duration: float) -> str:
        """Categorize content by length"""
        if duration < 60:
            return "short"
        elif duration < 600:
            return "medium"
        elif duration < 3600:
            return "long"
        else:
            return "very_long"
    
    def _estimate_production_quality(self, features: Dict[str, Any]) -> float:
        """Estimate production quality from features"""
        quality_score = 0.5  # Base score
        
        try:
            # File size factor (larger files often higher quality)
            file_size = features.get("file_size", 0)
            if file_size > 100 * 1024 * 1024:  # > 100MB
                quality_score += 0.2
            elif file_size > 50 * 1024 * 1024:  # > 50MB
                quality_score += 0.1
            
            # Resolution factor
            resolution = features.get("resolution", (0, 0))
            total_pixels = resolution[0] * resolution[1]
            if total_pixels > 1920 * 1080:  # HD+
                quality_score += 0.2
            elif total_pixels > 1280 * 720:  # HD
                quality_score += 0.1
            
            # Duration appropriateness
            duration = features.get("duration", 0)
            if 120 <= duration <= 3600:  # 2 minutes to 1 hour
                quality_score += 0.1
            
            return min(quality_score, 1.0)
            
        except Exception:
            return 0.5
    
    def _extract_engagement_indicators(self, features: Dict[str, Any]) -> List[str]:
        """Extract engagement indicators from features"""
        indicators = []
        
        try:
            # Professional audience indicator
            language_complexity = features.get("language_complexity", 0.5)
            if language_complexity > 0.7:
                indicators.append("professional_audience")
            
            # Broad appeal indicator
            text_content = features.get("text_content", "").lower()
            broad_keywords = ["everyone", "all", "general", "popular", "common", "universal"]
            if any(keyword in text_content for keyword in broad_keywords):
                indicators.append("broad_appeal")
            
            # Interactive elements
            interactive_keywords = ["question", "comment", "share", "like", "subscribe", "follow"]
            if any(keyword in text_content for keyword in interactive_keywords):
                indicators.append("interactive_elements")
            
            # Trending topics
            trending_keywords = ["trending", "viral", "popular", "latest", "new", "update"]
            if any(keyword in text_content for keyword in trending_keywords):
                indicators.append("trending_topics")
            
            return indicators
            
        except Exception:
            return []


# Convenience functions for easy usage
async def classify_content_auto(content_data: Dict[str, Any]) -> Dict[str, Any]:
    """Automatically classify content across all dimensions
    
    Args:
        content_data: Content information and features
        
    Returns:
        Classification results
    """
    classifier = ContentClassificationAI()
    classification = await classifier.classify_content(content_data)
    
    # Convert to serializable format
    result = {
        "content_id": classification.content_id,
        "primary_genre": classification.primary_genre,
        "target_audience": classification.target_audience,
        "quality_score": classification.quality_score,
        "monetization_potential": classification.monetization_potential,
        "viral_score": classification.viral_score,
        "brand_safety_score": classification.brand_safety_score,
        "confidence_score": classification.confidence_score,
        "processing_time": classification.total_processing_time,
        "classifications": {},
        "recommendations": classification.recommendations
    }
    
    # Add individual classification results
    for dimension, classification_result in classification.classifications.items():
        result["classifications"][dimension.value] = {
            "predicted_class": classification_result.predicted_class,
            "confidence": classification_result.confidence,
            "alternatives": classification_result.alternatives,
            "model_used": classification_result.model_used
        }
    
    return result


async def classify_content_quality(content_data: Dict[str, Any]) -> Dict[str, Any]:
    """Classify content quality specifically
    
    Args:
        content_data: Content information and features
        
    Returns:
        Quality classification result
    """
    classifier = ContentClassificationAI()
    classification = await classifier.classify_content(
        content_data, 
        dimensions=[ClassificationDimension.QUALITY]
    )
    
    quality_result = classification.classifications.get(ClassificationDimension.QUALITY)
    if quality_result:
        return {
            "quality_level": quality_result.predicted_class,
            "quality_score": classification.quality_score,
            "confidence": quality_result.confidence,
            "alternatives": quality_result.alternatives
        }
    
    return {"quality_level": "unknown", "quality_score": 0.0, "confidence": 0.0}


if __name__ == "__main__":
    # Example usage
    async def main():
        # Create content classification AI
        classifier = ContentClassificationAI()
        
        # Example content data
        content_data = {
            "id": "example_content_123",
            "title": "How to Build a Successful Business",
            "text": "Building a successful business requires careful planning, market research, and execution...",
            "metadata": {"category": "business", "tags": ["entrepreneurship", "business", "startup"]},
            "file_info": {"duration": 1200, "file_size": 50 * 1024 * 1024, "format": "mp4"},
            "visual_analysis": {"detected_objects": ["person", "office"], "complexity_score": 0.6},
            "audio_analysis": {"tempo": 120, "energy": 0.5, "has_speech": True, "has_music": False}
        }
        
        # Classify content
        print("Content Classification AI initialized")
        print("Ready to classify content across multiple dimensions:")
        print("- Genre, Quality, Target Audience, Purpose, Emotion")
        print("- Complexity, Professionalism, Monetization Potential")
        print("- Brand Safety, Viral Potential")
    
    asyncio.run(main())