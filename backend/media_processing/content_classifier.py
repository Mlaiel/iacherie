"""
Content Classifier module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""🔍 Content Classifier - AI Classification & Metadata Extraction Engine
================================================================================
Module: backend/media_processing/content_classifier.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead AI Developer + ML Engineer + NLP Expert + Computer Vision + Data Scientist
Type: Consolidated Content Classification System - Production-Ready
Responsibility: Advanced AI-powered content classification and intelligent metadata extraction
==============================================================================================

⚠️  EXCLUSIVE INTELLECTUAL PROPERTY - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use strictly prohibited and subject to legal prosecution.
Contact: mlaiel@live.de

🎯 CONSOLIDATED FROM:
- content_classification_ai.py (AI Classification Engine)
- intelligent_metadata_extractor.py (Intelligent Metadata Extraction)

🚀 ENTERPRISE CAPABILITIES:
- Multi-modal content classification with deep learning
- Intelligent metadata extraction and enrichment
- Advanced tagging and categorization systems
- Content quality assessment and scoring
- Semantic content understanding and indexing
- Business-relevant classification for Ainflue workflows
"""

import asyncio
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import structlog

# AI/ML imports
try:
    import torch
    import torch.nn.functional as F
    from transformers import (
        AutoModel, AutoTokenizer, AutoProcessor,
        CLIPModel, CLIPProcessor,
        pipeline, AutoImageProcessor,
        AutoModelForImageClassification
    )
    import cv2
    from PIL import Image, ExifTags
    import librosa
    from sentence_transformers import SentenceTransformer
    import spacy
    _AI_AVAILABLE = True
except ImportError:
    _AI_AVAILABLE = False

# Internal imports
from .processing_exceptions import (
    AIProcessingError,
    ModelInferenceError,
    ValidationError,
    handle_processing_errors
)

# Structured logging
logger = structlog.get_logger(__name__)

# =============================================================================
# CONFIGURATION & ENUMS
# =============================================================================

class ContentCategory(Enum):
    """Content categories for classification"""
    MUSIC = "music"
    PODCAST = "podcast"
    PHOTOGRAPHY = "photography"
    VIDEOGRAPHY = "videography"
    BLOG_POST = "blog_post"
    TUTORIAL = "tutorial"
    ENTERTAINMENT = "entertainment"
    EDUCATIONAL = "educational"
    COMMERCIAL = "commercial"
    ARTISTIC = "artistic"
    DOCUMENTARY = "documentary"
    GAMING = "gaming"
    LIFESTYLE = "lifestyle"
    TECHNOLOGY = "technology"
    SPORTS = "sports"
    FASHION = "fashion"
    FOOD = "food"
    TRAVEL = "travel"
    NEWS = "news"
    OTHER = "other"

class QualityLevel(Enum):
    """Content quality levels"""
    PROFESSIONAL = "professional"
    SEMI_PROFESSIONAL = "semi_professional"
    AMATEUR = "amateur"
    BASIC = "basic"
    LOW_QUALITY = "low_quality"

class AudienceType(Enum):
    """Target audience types"""
    GENERAL = "general"
    YOUNG_ADULTS = "young_adults"
    PROFESSIONALS = "professionals"
    CREATIVE_COMMUNITY = "creative_community"
    ENTERTAINMENT_SEEKERS = "entertainment_seekers"
    EDUCATIONAL = "educational"
    NICHE_ENTHUSIASTS = "niche_enthusiasts"

class ContentMood(Enum):
    """Content mood classification"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    ENERGETIC = "energetic"
    CALM = "calm"
    DRAMATIC = "dramatic"
    HUMOROUS = "humorous"
    SERIOUS = "serious"
    INSPIRATIONAL = "inspirational"
    MELANCHOLIC = "melancholic"

@dataclass
class ClassificationResult:
    """Content classification result"""
    category: ContentCategory
    subcategories: List[str] = field(default_factory=list)
    confidence: float = 0.0
    quality_level: Optional[QualityLevel] = None
    audience_type: Optional[AudienceType] = None
    mood: Optional[ContentMood] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MetadataExtractionResult:
    """Metadata extraction result"""
    title: Optional[str] = None
    description: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    technical_metadata: Dict[str, Any] = field(default_factory=dict)
    semantic_metadata: Dict[str, Any] = field(default_factory=dict)
    business_metadata: Dict[str, Any] = field(default_factory=dict)
    extracted_entities: List[Dict[str, Any]] = field(default_factory=list)
    sentiment_analysis: Dict[str, Any] = field(default_factory=dict)
    content_summary: Optional[str] = None

@dataclass
class ContentAnalysisResult:
    """Complete content analysis result"""
    classification: ClassificationResult
    metadata: MetadataExtractionResult
    processing_time_ms: int = 0
    confidence_scores: Dict[str, float] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)

# =============================================================================
# SPECIALIZED CLASSIFIERS
# =============================================================================

class ImageClassifier:
    """Specialized image content classifier"""
    
    def __init__(self) -> None:
        self.clip_model = None
        self.clip_processor = None
        self.image_classifier = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
    
    async def initialize(self) -> None:
        """Initialize image classification models"""
        if not _AI_AVAILABLE:
            logger.warning("AI libraries not available, using fallback classification")
            return
        
        try:
            # Initialize CLIP for general understanding
            self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
            self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
            self.clip_model.to(self.device)
            
            # Initialize specialized image classifier
            self.image_classifier = pipeline(
                "image-classification",
                model="google/vit-base-patch16-224",
                device=0 if self.device == "cuda" else -1
            )
            
            logger.info("Image classifier initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize image classifier: {e}")
    
    async def classify_image(self, image_path: str) -> ClassificationResult:
        """Classify image content"""
        try:
            image = Image.open(image_path).convert('RGB')
            
            # Basic classification without AI if models not available
            if self.clip_model is None:
                return self._fallback_image_classification(image, image_path)
            
            # CLIP-based classification
            category_prompts = [
                "a professional photograph",
                "amateur photography",
                "artistic image",
                "commercial photograph",
                "nature photography",
                "portrait photography",
                "street photography",
                "fashion photography",
                "food photography",
                "travel photography"
            ]
            
            inputs = self.clip_processor(
                text=category_prompts,
                images=image,
                return_tensors="pt",
                padding=True
            )
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = self.clip_model(**inputs)
                probs = outputs.logits_per_image.softmax(dim=1)
                
            # Get best match
            best_idx = probs.argmax().item()
            confidence = probs[0][best_idx].item()
            
            # Map to content categories
            category_mapping = {
                0: ContentCategory.PHOTOGRAPHY,
                1: ContentCategory.PHOTOGRAPHY,
                2: ContentCategory.ARTISTIC,
                3: ContentCategory.COMMERCIAL,
                4: ContentCategory.PHOTOGRAPHY,
                5: ContentCategory.PHOTOGRAPHY,
                6: ContentCategory.PHOTOGRAPHY,
                7: ContentCategory.FASHION,
                8: ContentCategory.FOOD,
                9: ContentCategory.TRAVEL
            }
            
            category = category_mapping.get(best_idx, ContentCategory.PHOTOGRAPHY)
            
            # Determine quality level based on image properties
            quality_level = self._assess_image_quality(image)
            
            # Extract tags
            tags = self._extract_image_tags(image, category_prompts[best_idx])
            
            return ClassificationResult(
                category=category,
                subcategories=[category_prompts[best_idx]],
                confidence=confidence,
                quality_level=quality_level,
                audience_type=AudienceType.GENERAL,
                tags=tags,
                metadata={'source': 'clip_classification'}
            )
            
        except Exception as e:
            logger.error(f"Image classification failed: {e}")
            return ClassificationResult(
                category=ContentCategory.OTHER,
                confidence=0.0,
                metadata={'error': str(e)}
            )
    
    def _fallback_image_classification(self, image: Image.Image, image_path: str) -> ClassificationResult:
        """Fallback image classification without AI"""
        width, height = image.size
        aspect_ratio = width / height
        
        # Basic classification based on image properties
        if 0.8 <= aspect_ratio <= 1.2:
            category = ContentCategory.PHOTOGRAPHY
            subcategories = ["square_format"]
        elif aspect_ratio > 1.5:
            category = ContentCategory.PHOTOGRAPHY
            subcategories = ["landscape_format"]
        else:
            category = ContentCategory.PHOTOGRAPHY
            subcategories = ["portrait_format"]
        
        quality_level = self._assess_image_quality(image)
        
        return ClassificationResult(
            category=category,
            subcategories=subcategories,
            confidence=0.6,
            quality_level=quality_level,
            audience_type=AudienceType.GENERAL,
            tags=["photography", "visual_content"],
            metadata={'source': 'fallback_classification'}
        )
    
    def _assess_image_quality(self, image: Image.Image) -> QualityLevel:
        """Assess image quality level"""
        width, height = image.size
        total_pixels = width * height
        
        if total_pixels >= 4000000:  # 4MP+
            return QualityLevel.PROFESSIONAL
        elif total_pixels >= 2000000:  # 2MP+
            return QualityLevel.SEMI_PROFESSIONAL
        elif total_pixels >= 1000000:  # 1MP+
            return QualityLevel.AMATEUR
        elif total_pixels >= 500000:   # 0.5MP+
            return QualityLevel.BASIC
        else:
            return QualityLevel.LOW_QUALITY
    
    def _extract_image_tags(self, image: Image.Image, category_prompt: str) -> List[str]:
        """Extract relevant tags from image"""
        tags = ["visual_content", "image"]
        
        # Add tags based on classification
        if "professional" in category_prompt:
            tags.extend(["professional", "high_quality"])
        if "artistic" in category_prompt:
            tags.extend(["artistic", "creative"])
        if "commercial" in category_prompt:
            tags.extend(["commercial", "business"])
        
        # Add format tags
        width, height = image.size
        if width > height:
            tags.append("landscape")
        elif height > width:
            tags.append("portrait")
        else:
            tags.append("square")
        
        return tags

class AudioClassifier:
    """Specialized audio content classifier"""
    
    def __init__(self) -> None:
        self.audio_classifier = None
        self.emotion_classifier = None
    
    async def initialize(self) -> None:
        """Initialize audio classification models"""
        try:
            if _AI_AVAILABLE:
                # Initialize audio classification pipeline
                self.audio_classifier = pipeline(
                    "audio-classification",
                    model="facebook/wav2vec2-base-960h",
                    device=0 if torch.cuda.is_available() else -1
                )
                
                logger.info("Audio classifier initialized successfully")
            else:
                logger.warning("AI libraries not available, using fallback audio classification")
                
        except Exception as e:
            logger.warning(f"Failed to initialize AI audio classifier: {e}")
    
    async def classify_audio(self, audio_path: str) -> ClassificationResult:
        """Classify audio content"""
        try:
            # Load audio file
            audio, sr = librosa.load(audio_path, sr=16000)
            
            # Extract audio features for classification
            features = self._extract_audio_features(audio, sr)
            
            # Classify based on features
            category = self._classify_audio_by_features(features)
            
            # Determine quality and mood
            quality_level = self._assess_audio_quality(audio, sr)
            mood = self._detect_audio_mood(features)
            
            # Extract tags
            tags = self._extract_audio_tags(features, category)
            
            return ClassificationResult(
                category=category,
                subcategories=self._get_audio_subcategories(features),
                confidence=0.75,  # Based on feature analysis
                quality_level=quality_level,
                audience_type=self._determine_audio_audience(features),
                mood=mood,
                tags=tags,
                metadata={'source': 'feature_based_classification', 'features': features}
            )
            
        except Exception as e:
            logger.error(f"Audio classification failed: {e}")
            return ClassificationResult(
                category=ContentCategory.OTHER,
                confidence=0.0,
                metadata={'error': str(e)}
            )
    
    def _extract_audio_features(self, audio: np.ndarray, sr: int) -> Dict[str, Any]:
        """Extract comprehensive audio features"""
        try:
            features = {}
            
            # Basic properties
            features['duration'] = len(audio) / sr
            features['sample_rate'] = sr
            
            # Spectral features
            features['spectral_centroid'] = float(librosa.feature.spectral_centroid(y=audio, sr=sr).mean())
            features['spectral_bandwidth'] = float(librosa.feature.spectral_bandwidth(y=audio, sr=sr).mean())
            features['spectral_rolloff'] = float(librosa.feature.spectral_rolloff(y=audio, sr=sr).mean())
            
            # Rhythmic features
            tempo, _ = librosa.beat.beat_track(y=audio, sr=sr)
            features['tempo'] = float(tempo)
            
            # Harmonic features
            features['zero_crossing_rate'] = float(librosa.feature.zero_crossing_rate(audio).mean())
            
            # MFCC features
            mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)
            features['mfcc_mean'] = mfccs.mean(axis=1).tolist()
            features['mfcc_std'] = mfccs.std(axis=1).tolist()
            
            # Energy features
            features['rms_energy'] = float(librosa.feature.rms(y=audio).mean())
            
            return features
            
        except Exception as e:
            logger.warning(f"Audio feature extraction failed: {e}")
            return {}
    
    def _classify_audio_by_features(self, features: Dict[str, Any]) -> ContentCategory:
        """Classify audio based on extracted features"""
        if not features:
            return ContentCategory.OTHER
        
        tempo = features.get('tempo', 0)
        spectral_centroid = features.get('spectral_centroid', 0)
        duration = features.get('duration', 0)
        
        # Music classification
        if tempo > 60 and spectral_centroid > 1000:
            if duration > 60:  # Longer tracks likely music
                return ContentCategory.MUSIC
            else:
                return ContentCategory.ENTERTAINMENT
        
        # Podcast/speech classification
        elif tempo < 200 and spectral_centroid < 3000:
            if duration > 300:  # 5+ minutes likely podcast
                return ContentCategory.PODCAST
            else:
                return ContentCategory.EDUCATIONAL
        
        # Default classification
        return ContentCategory.ENTERTAINMENT
    
    def _assess_audio_quality(self, audio: np.ndarray, sr: int) -> QualityLevel:
        """Assess audio quality level"""
        # Calculate signal-to-noise ratio estimation
        rms_energy = librosa.feature.rms(y=audio).mean()
        
        if sr >= 44100 and rms_energy > 0.1:
            return QualityLevel.PROFESSIONAL
        elif sr >= 22050 and rms_energy > 0.05:
            return QualityLevel.SEMI_PROFESSIONAL
        elif sr >= 16000 and rms_energy > 0.02:
            return QualityLevel.AMATEUR
        elif rms_energy > 0.01:
            return QualityLevel.BASIC
        else:
            return QualityLevel.LOW_QUALITY
    
    def _detect_audio_mood(self, features: Dict[str, Any]) -> ContentMood:
        """Detect audio mood from features"""
        tempo = features.get('tempo', 0)
        energy = features.get('rms_energy', 0)
        
        if tempo > 120 and energy > 0.1:
            return ContentMood.ENERGETIC
        elif tempo < 80 and energy < 0.05:
            return ContentMood.CALM
        elif energy > 0.15:
            return ContentMood.DRAMATIC
        else:
            return ContentMood.NEUTRAL
    
    def _get_audio_subcategories(self, features: Dict[str, Any]) -> List[str]:
        """Get audio subcategories based on features"""
        subcategories = []
        
        tempo = features.get('tempo', 0)
        if tempo > 140:
            subcategories.append("high_tempo")
        elif tempo < 60:
            subcategories.append("low_tempo")
        else:
            subcategories.append("medium_tempo")
        
        duration = features.get('duration', 0)
        if duration > 300:
            subcategories.append("long_form")
        elif duration < 60:
            subcategories.append("short_form")
        else:
            subcategories.append("medium_form")
        
        return subcategories
    
    def _determine_audio_audience(self, features: Dict[str, Any]) -> AudienceType:
        """Determine target audience based on audio features"""
        tempo = features.get('tempo', 0)
        duration = features.get('duration', 0)
        
        if tempo > 120 and duration < 240:  # Fast, short
            return AudienceType.YOUNG_ADULTS
        elif duration > 1800:  # Long form content
            return AudienceType.EDUCATIONAL
        else:
            return AudienceType.GENERAL
    
    def _extract_audio_tags(self, features: Dict[str, Any], category: ContentCategory) -> List[str]:
        """Extract relevant tags from audio features"""
        tags = ["audio_content"]
        
        # Add category-specific tags
        if category == ContentCategory.MUSIC:
            tags.extend(["music", "audio", "sound"])
        elif category == ContentCategory.PODCAST:
            tags.extend(["podcast", "speech", "voice"])
        
        # Add tempo-based tags
        tempo = features.get('tempo', 0)
        if tempo > 140:
            tags.append("upbeat")
        elif tempo < 80:
            tags.append("slow")
        
        return tags

class TextClassifier:
    """Specialized text content classifier"""
    
    def __init__(self) -> None:
        self.sentiment_classifier = None
        self.nlp_model = None
        self.text_classifier = None
    
    async def initialize(self) -> None:
        """Initialize text classification models"""
        try:
            if _AI_AVAILABLE:
                # Initialize sentiment analysis
                self.sentiment_classifier = pipeline(
                    "sentiment-analysis",
                    model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                    device=0 if torch.cuda.is_available() else -1
                )
                
                # Initialize text classification
                self.text_classifier = pipeline(
                    "text-classification",
                    model="facebook/bart-large-mnli",
                    device=0 if torch.cuda.is_available() else -1
                )
                
                # Initialize spaCy for NER and linguistic analysis
                try:
                    self.nlp_model = spacy.load("en_core_web_sm")
                except OSError:
                    logger.warning("spaCy model not found, some features will be limited")
                
                logger.info("Text classifier initialized successfully")
            else:
                logger.warning("AI libraries not available, using fallback text classification")
                
        except Exception as e:
            logger.warning(f"Failed to initialize AI text classifier: {e}")
    
    async def classify_text(self, text: str) -> ClassificationResult:
        """Classify text content"""
        try:
            # Basic text analysis
            word_count = len(text.split())
            char_count = len(text)
            
            # Classify content type based on text characteristics
            category = self._classify_text_by_characteristics(text, word_count)
            
            # Determine quality level
            quality_level = self._assess_text_quality(text, word_count, char_count)
            
            # Detect mood/sentiment
            mood = await self._detect_text_mood(text)
            
            # Extract tags
            tags = self._extract_text_tags(text, category)
            
            return ClassificationResult(
                category=category,
                subcategories=self._get_text_subcategories(text, word_count),
                confidence=0.8,
                quality_level=quality_level,
                audience_type=self._determine_text_audience(text),
                mood=mood,
                tags=tags,
                metadata={
                    'word_count': word_count,
                    'char_count': char_count,
                    'source': 'text_analysis'
                }
            )
            
        except Exception as e:
            logger.error(f"Text classification failed: {e}")
            return ClassificationResult(
                category=ContentCategory.OTHER,
                confidence=0.0,
                metadata={'error': str(e)}
            )
    
    def _classify_text_by_characteristics(self, text: str, word_count: int) -> ContentCategory:
        """Classify text based on characteristics"""
        text_lower = text.lower()
        
        # Blog post indicators
        if word_count > 300 and any(keyword in text_lower for keyword in 
                                   ['blog', 'article', 'post', 'today', 'experience']):
            return ContentCategory.BLOG_POST
        
        # Tutorial indicators
        elif any(keyword in text_lower for keyword in 
                ['tutorial', 'how to', 'step', 'guide', 'learn', 'instruction']):
            return ContentCategory.TUTORIAL
        
        # Educational content
        elif any(keyword in text_lower for keyword in 
                ['education', 'study', 'course', 'lesson', 'academic']):
            return ContentCategory.EDUCATIONAL
        
        # News indicators
        elif any(keyword in text_lower for keyword in 
                ['news', 'breaking', 'report', 'announcement', 'update']):
            return ContentCategory.NEWS
        
        # Technology content
        elif any(keyword in text_lower for keyword in 
                ['technology', 'tech', 'software', 'programming', 'code']):
            return ContentCategory.TECHNOLOGY
        
        # Default to blog post for longer content, other for short
        elif word_count > 100:
            return ContentCategory.BLOG_POST
        else:
            return ContentCategory.OTHER
    
    def _assess_text_quality(self, text: str, word_count: int, char_count: int) -> QualityLevel:
        """Assess text quality level"""
        # Calculate readability metrics
        sentences = len([s for s in text.split('.') if s.strip()])
        avg_sentence_length = word_count / max(sentences, 1)
        
        # Professional indicators
        professional_indicators = [
            word_count > 500,
            avg_sentence_length > 10,
            char_count / word_count > 4,  # Average word length
            text.count(',') / word_count > 0.02,  # Comma usage
        ]
        
        professional_score = sum(professional_indicators)
        
        if professional_score >= 3:
            return QualityLevel.PROFESSIONAL
        elif professional_score >= 2:
            return QualityLevel.SEMI_PROFESSIONAL
        elif professional_score >= 1:
            return QualityLevel.AMATEUR
        elif word_count > 50:
            return QualityLevel.BASIC
        else:
            return QualityLevel.LOW_QUALITY
    
    async def _detect_text_mood(self, text: str) -> ContentMood:
        """Detect text mood using sentiment analysis"""
        try:
            if self.sentiment_classifier and len(text.strip()) > 0:
                # Truncate text if too long for model
                text_sample = text[:512] if len(text) > 512 else text
                
                result = self.sentiment_classifier(text_sample)
                label = result[0]['label'].lower()
                confidence = result[0]['score']
                
                if 'positive' in label and confidence > 0.7:
                    return ContentMood.POSITIVE
                elif 'negative' in label and confidence > 0.7:
                    return ContentMood.NEGATIVE
                else:
                    return ContentMood.NEUTRAL
            else:
                # Fallback sentiment analysis
                positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic']
                negative_words = ['bad', 'terrible', 'awful', 'horrible', 'disappointing']
                
                text_lower = text.lower()
                positive_count = sum(1 for word in positive_words if word in text_lower)
                negative_count = sum(1 for word in negative_words if word in text_lower)
                
                if positive_count > negative_count:
                    return ContentMood.POSITIVE
                elif negative_count > positive_count:
                    return ContentMood.NEGATIVE
                else:
                    return ContentMood.NEUTRAL
                    
        except Exception as e:
            logger.warning(f"Mood detection failed: {e}")
            return ContentMood.NEUTRAL
    
    def _get_text_subcategories(self, text: str, word_count: int) -> List[str]:
        """Get text subcategories"""
        subcategories = []
        
        if word_count > 1000:
            subcategories.append("long_form")
        elif word_count > 300:
            subcategories.append("medium_form")
        else:
            subcategories.append("short_form")
        
        # Add content type indicators
        text_lower = text.lower()
        if any(keyword in text_lower for keyword in ['opinion', 'think', 'believe']):
            subcategories.append("opinion")
        if any(keyword in text_lower for keyword in ['fact', 'research', 'study']):
            subcategories.append("factual")
        
        return subcategories
    
    def _determine_text_audience(self, text: str) -> AudienceType:
        """Determine target audience for text"""
        text_lower = text.lower()
        
        # Professional content indicators
        if any(keyword in text_lower for keyword in 
               ['business', 'professional', 'industry', 'corporate']):
            return AudienceType.PROFESSIONALS
        
        # Educational content indicators
        elif any(keyword in text_lower for keyword in 
                ['learn', 'education', 'study', 'academic']):
            return AudienceType.EDUCATIONAL
        
        # Creative community indicators
        elif any(keyword in text_lower for keyword in 
                ['creative', 'art', 'design', 'inspiration']):
            return AudienceType.CREATIVE_COMMUNITY
        
        # Young adults indicators
        elif any(keyword in text_lower for keyword in 
                ['trend', 'social', 'lifestyle', 'fun']):
            return AudienceType.YOUNG_ADULTS
        
        else:
            return AudienceType.GENERAL
    
    def _extract_text_tags(self, text: str, category: ContentCategory) -> List[str]:
        """Extract relevant tags from text"""
        tags = ["text_content"]
        
        # Add category-specific tags
        if category == ContentCategory.BLOG_POST:
            tags.extend(["blog", "article", "writing"])
        elif category == ContentCategory.TUTORIAL:
            tags.extend(["tutorial", "guide", "howto"])
        elif category == ContentCategory.EDUCATIONAL:
            tags.extend(["education", "learning", "knowledge"])
        
        # Extract keywords based on content
        text_lower = text.lower()
        
        # Technology tags
        if any(keyword in text_lower for keyword in ['tech', 'software', 'digital']):
            tags.append("technology")
        
        # Creative tags
        if any(keyword in text_lower for keyword in ['creative', 'art', 'design']):
            tags.append("creative")
        
        # Business tags
        if any(keyword in text_lower for keyword in ['business', 'marketing', 'strategy']):
            tags.append("business")
        
        return tags

# =============================================================================
# METADATA EXTRACTOR
# =============================================================================

class MetadataExtractor:
    """Intelligent metadata extraction engine"""
    
    def __init__(self) -> None:
        self.nlp_model = None
        self.keyword_extractor = None
    
    async def initialize(self) -> None:
        """Initialize metadata extraction models"""
        try:
            if _AI_AVAILABLE:
                # Initialize spaCy for NER
                try:
                    self.nlp_model = spacy.load("en_core_web_sm")
                except OSError:
                    logger.warning("spaCy model not found, using limited metadata extraction")
                
                logger.info("Metadata extractor initialized successfully")
            else:
                logger.warning("AI libraries not available, using basic metadata extraction")
                
        except Exception as e:
            logger.warning(f"Failed to initialize metadata extractor: {e}")
    
    async def extract_metadata(
        self,
        content_path: str,
        content_type: str,
        classification_result: ClassificationResult
    ) -> MetadataExtractionResult:
        """Extract comprehensive metadata from content"""
        
        try:
            if content_type.lower() == 'image':
                return await self._extract_image_metadata(content_path, classification_result)
            elif content_type.lower() == 'audio':
                return await self._extract_audio_metadata(content_path, classification_result)
            elif content_type.lower() == 'video':
                return await self._extract_video_metadata(content_path, classification_result)
            elif content_type.lower() == 'text':
                return await self._extract_text_metadata(content_path, classification_result)
            else:
                return await self._extract_generic_metadata(content_path, classification_result)
                
        except Exception as e:
            logger.error(f"Metadata extraction failed: {e}")
            return MetadataExtractionResult()
    
    async def _extract_image_metadata(
        self,
        image_path: str,
        classification: ClassificationResult
    ) -> MetadataExtractionResult:
        """Extract metadata from image files"""
        
        try:
            image = Image.open(image_path)
            
            # Technical metadata
            technical_metadata = {
                'width': image.width,
                'height': image.height,
                'mode': image.mode,
                'format': image.format,
                'file_size': Path(image_path).stat().st_size
            }
            
            # Extract EXIF data if available
            if hasattr(image, '_getexif') and image._getexif():
                exif = {
                    ExifTags.TAGS[k]: v
                    for k, v in image._getexif().items()
                    if k in ExifTags.TAGS
                }
                technical_metadata['exif'] = exif
            
            # Generate semantic metadata
            semantic_metadata = {
                'aspect_ratio': image.width / image.height,
                'orientation': 'landscape' if image.width > image.height else 'portrait' if image.height > image.width else 'square',
                'resolution_category': self._categorize_resolution(image.width, image.height)
            }
            
            # Business metadata
            business_metadata = {
                'commercial_use_potential': self._assess_commercial_potential(classification),
                'platform_suitability': self._assess_platform_suitability(classification, technical_metadata),
                'estimated_engagement': self._estimate_engagement(classification, semantic_metadata)
            }
            
            # Generate keywords
            keywords = self._generate_image_keywords(classification, semantic_metadata)
            
            return MetadataExtractionResult(
                title=f"{classification.category.value.title()} Image",
                keywords=keywords,
                technical_metadata=technical_metadata,
                semantic_metadata=semantic_metadata,
                business_metadata=business_metadata
            )
            
        except Exception as e:
            logger.error(f"Image metadata extraction failed: {e}")
            return MetadataExtractionResult()
    
    async def _extract_audio_metadata(
        self,
        audio_path: str,
        classification: ClassificationResult
    ) -> MetadataExtractionResult:
        """Extract metadata from audio files"""
        
        try:
            # Load audio for analysis
            audio, sr = librosa.load(audio_path, sr=None)
            duration = len(audio) / sr
            
            # Technical metadata
            technical_metadata = {
                'duration_seconds': duration,
                'sample_rate': sr,
                'channels': 1,  # librosa loads as mono by default
                'file_size': Path(audio_path).stat().st_size
            }
            
            # Extract advanced audio features
            tempo, _ = librosa.beat.beat_track(y=audio, sr=sr)
            spectral_centroid = librosa.feature.spectral_centroid(y=audio, sr=sr).mean()
            
            semantic_metadata = {
                'tempo': float(tempo),
                'spectral_centroid': float(spectral_centroid),
                'duration_category': 'short' if duration < 60 else 'medium' if duration < 300 else 'long'
            }
            
            # Business metadata
            business_metadata = {
                'streaming_platform_suitability': self._assess_audio_platform_suitability(classification, semantic_metadata),
                'monetization_potential': self._assess_audio_monetization(classification, duration),
                'playlist_recommendations': self._recommend_playlists(classification, semantic_metadata)
            }
            
            # Generate keywords
            keywords = self._generate_audio_keywords(classification, semantic_metadata)
            
            return MetadataExtractionResult(
                title=f"{classification.category.value.title()} Audio",
                keywords=keywords,
                technical_metadata=technical_metadata,
                semantic_metadata=semantic_metadata,
                business_metadata=business_metadata
            )
            
        except Exception as e:
            logger.error(f"Audio metadata extraction failed: {e}")
            return MetadataExtractionResult()
    
    async def _extract_text_metadata(
        self,
        text_path: str,
        classification: ClassificationResult
    ) -> MetadataExtractionResult:
        """Extract metadata from text content"""
        
        try:
            # Read text content
            with open(text_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            # Technical metadata
            technical_metadata = {
                'character_count': len(text),
                'word_count': len(text.split()),
                'paragraph_count': len(text.split('\n\n')),
                'file_size': Path(text_path).stat().st_size
            }
            
            # Extract entities and keywords
            entities = []
            keywords = []
            
            if self.nlp_model:
                doc = self.nlp_model(text[:1000000])  # Limit for performance
                
                # Extract named entities
                entities = [
                    {'text': ent.text, 'label': ent.label_, 'start': ent.start_char, 'end': ent.end_char}
                    for ent in doc.ents
                ]
                
                # Extract keywords (noun phrases)
                keywords = [chunk.text.lower() for chunk in doc.noun_chunks if len(chunk.text) > 2]
            
            # Semantic metadata
            semantic_metadata = {
                'readability_level': self._assess_readability(text),
                'content_density': len(set(text.lower().split())) / len(text.split()) if text.split() else 0,
                'formality_level': self._assess_formality(text)
            }
            
            # Business metadata
            business_metadata = {
                'seo_potential': self._assess_seo_potential(text, keywords),
                'social_sharing_potential': self._assess_social_sharing(classification, text),
                'target_platforms': self._recommend_text_platforms(classification, semantic_metadata)
            }
            
            # Generate summary
            content_summary = self._generate_text_summary(text)
            
            return MetadataExtractionResult(
                title=self._extract_title(text),
                description=content_summary,
                keywords=keywords[:20],  # Limit keywords
                technical_metadata=technical_metadata,
                semantic_metadata=semantic_metadata,
                business_metadata=business_metadata,
                extracted_entities=entities[:50],  # Limit entities
                content_summary=content_summary
            )
            
        except Exception as e:
            logger.error(f"Text metadata extraction failed: {e}")
            return MetadataExtractionResult()
    
    async def _extract_video_metadata(
        self,
        video_path: str,
        classification: ClassificationResult
    ) -> MetadataExtractionResult:
        """Extract metadata from video files"""
        
        try:
            # Extract video information using OpenCV
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = frame_count / fps if fps > 0 else 0
            cap.release()
            
            # Technical metadata
            technical_metadata = {
                'duration_seconds': duration,
                'fps': fps,
                'width': width,
                'height': height,
                'frame_count': frame_count,
                'file_size': Path(video_path).stat().st_size
            }
            
            # Semantic metadata
            semantic_metadata = {
                'aspect_ratio': width / height if height > 0 else 1,
                'resolution_category': self._categorize_video_resolution(width, height),
                'duration_category': self._categorize_duration(duration)
            }
            
            # Business metadata
            business_metadata = {
                'platform_optimization': self._optimize_for_video_platforms(semantic_metadata),
                'monetization_strategy': self._suggest_video_monetization(classification, duration),
                'audience_retention_prediction': self._predict_retention(classification, duration)
            }
            
            # Generate keywords
            keywords = self._generate_video_keywords(classification, semantic_metadata)
            
            return MetadataExtractionResult(
                title=f"{classification.category.value.title()} Video",
                keywords=keywords,
                technical_metadata=technical_metadata,
                semantic_metadata=semantic_metadata,
                business_metadata=business_metadata
            )
            
        except Exception as e:
            logger.error(f"Video metadata extraction failed: {e}")
            return MetadataExtractionResult()
    
    async def _extract_generic_metadata(
        self,
        content_path: str,
        classification: ClassificationResult
    ) -> MetadataExtractionResult:
        """Extract basic metadata for unknown content types"""
        
        try:
            file_stats = Path(content_path).stat()
            
            technical_metadata = {
                'file_size': file_stats.st_size,
                'created_time': file_stats.st_ctime,
                'modified_time': file_stats.st_mtime,
                'file_extension': Path(content_path).suffix
            }
            
            return MetadataExtractionResult(
                title=f"{classification.category.value.title()} Content",
                keywords=[classification.category.value],
                technical_metadata=technical_metadata
            )
            
        except Exception as e:
            logger.error(f"Generic metadata extraction failed: {e}")
            return MetadataExtractionResult()
    
    # Helper methods for metadata extraction
    def _categorize_resolution(self, width: int, height: int) -> str:
        """Categorize image resolution"""
        total_pixels = width * height
        if total_pixels >= 8000000:  # 8MP+
            return "ultra_high"
        elif total_pixels >= 2000000:  # 2MP+
            return "high"
        elif total_pixels >= 500000:   # 0.5MP+
            return "medium"
        else:
            return "low"
    
    def _assess_commercial_potential(self, classification: ClassificationResult) -> str:
        """Assess commercial use potential"""
        if classification.quality_level in [QualityLevel.PROFESSIONAL, QualityLevel.SEMI_PROFESSIONAL]:
            return "high"
        elif classification.quality_level == QualityLevel.AMATEUR:
            return "medium"
        else:
            return "low"
    
    def _assess_platform_suitability(self, classification: ClassificationResult, technical: Dict) -> Dict[str, float]:
        """Assess suitability for different platforms"""
        aspect_ratio = technical.get('width', 1) / technical.get('height', 1)
        
        suitability = {
            'instagram': 0.9 if 0.8 <= aspect_ratio <= 1.91 else 0.5,
            'facebook': 0.8,
            'twitter': 0.7,
            'linkedin': 0.9 if classification.category in [ContentCategory.COMMERCIAL, ContentCategory.EDUCATIONAL] else 0.5,
            'pinterest': 0.9 if aspect_ratio < 1 else 0.6  # Prefers vertical
        }
        
        return suitability
    
    def _estimate_engagement(self, classification: ClassificationResult, semantic: Dict) -> str:
        """Estimate potential engagement"""
        factors = [
            classification.quality_level in [QualityLevel.PROFESSIONAL, QualityLevel.SEMI_PROFESSIONAL],
            classification.audience_type == AudienceType.YOUNG_ADULTS,
            semantic.get('orientation') == 'portrait'
        ]
        
        score = sum(factors)
        if score >= 2:
            return "high"
        elif score == 1:
            return "medium"
        else:
            return "low"
    
    def _generate_image_keywords(self, classification: ClassificationResult, semantic: Dict) -> List[str]:
        """Generate keywords for images"""
        keywords = [
            classification.category.value,
            semantic.get('orientation', 'unknown'),
            semantic.get('resolution_category', 'unknown'),
            'visual_content',
            'image'
        ]
        
        keywords.extend(classification.tags)
        return list(set(keywords))  # Remove duplicates
    
    def _generate_audio_keywords(self, classification: ClassificationResult, semantic: Dict) -> List[str]:
        """Generate keywords for audio"""
        keywords = [
            classification.category.value,
            semantic.get('duration_category', 'unknown'),
            'audio_content',
            'sound'
        ]
        
        if semantic.get('tempo', 0) > 120:
            keywords.append('upbeat')
        elif semantic.get('tempo', 0) < 80:
            keywords.append('slow')
        
        keywords.extend(classification.tags)
        return list(set(keywords))
    
    def _generate_video_keywords(self, classification: ClassificationResult, semantic: Dict) -> List[str]:
        """Generate keywords for videos"""
        keywords = [
            classification.category.value,
            semantic.get('resolution_category', 'unknown'),
            semantic.get('duration_category', 'unknown'),
            'video_content',
            'visual'
        ]
        
        if semantic.get('aspect_ratio', 1) > 1.5:
            keywords.append('widescreen')
        elif semantic.get('aspect_ratio', 1) < 0.7:
            keywords.append('vertical')
        
        keywords.extend(classification.tags)
        return list(set(keywords))
    
    def _assess_readability(self, text: str) -> str:
        """Assess text readability level"""
        words = text.split()
        sentences = [s for s in text.split('.') if s.strip()]
        
        avg_sentence_length = len(words) / max(len(sentences), 1)
        avg_word_length = sum(len(word) for word in words) / max(len(words), 1)
        
        if avg_sentence_length > 20 or avg_word_length > 6:
            return "advanced"
        elif avg_sentence_length > 15 or avg_word_length > 5:
            return "intermediate"
        else:
            return "basic"
    
    def _assess_formality(self, text: str) -> str:
        """Assess text formality level"""
        formal_indicators = text.count(',') + text.count(';') + text.count(':')
        informal_indicators = text.count('!') + text.count('?') + len([w for w in text.split() if w.lower() in ['you', 'your', 'we', 'our']])
        
        if formal_indicators > informal_indicators * 2:
            return "formal"
        elif informal_indicators > formal_indicators * 2:
            return "informal"
        else:
            return "neutral"
    
    def _extract_title(self, text: str) -> str:
        """Extract or generate title from text"""
        lines = text.split('\n')
        
        # Look for a title-like first line
        if lines and len(lines[0]) < 100 and not lines[0].endswith('.'):
            return lines[0].strip()
        
        # Generate title from first sentence
        sentences = text.split('.')
        if sentences:
            first_sentence = sentences[0].strip()
            if len(first_sentence) < 100:
                return first_sentence
        
        # Fallback to first few words
        words = text.split()[:10]
        return ' '.join(words) + ('...' if len(text.split()) > 10 else '')
    
    def _generate_text_summary(self, text: str) -> str:
        """Generate a summary of text content"""
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        
        if len(sentences) <= 2:
            return text[:200] + ('...' if len(text) > 200 else '')
        
        # Return first sentence or first 200 characters
        first_sentence = sentences[0]
        if len(first_sentence) <= 200:
            return first_sentence
        else:
            return first_sentence[:200] + '...'

# =============================================================================
# MAIN CONTENT CLASSIFIER
# =============================================================================

class ContentClassifier:
    """Main content classification and metadata extraction engine"""
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        """Initialize content classifier"""
        self.config = config or self._get_default_config()
        
        # Initialize specialized classifiers
        self.image_classifier = ImageClassifier()
        self.audio_classifier = AudioClassifier()
        self.text_classifier = TextClassifier()
        
        # Initialize metadata extractor
        self.metadata_extractor = MetadataExtractor()
        
        # Processing statistics
        self.processing_stats = {
            'total_classifications': 0,
            'successful_classifications': 0,
            'failed_classifications': 0,
            'category_counts': {category.value: 0 for category in ContentCategory}
        }
        
        # Cache for results
        self.classification_cache: Dict[str, ContentAnalysisResult] = {}
        
        # Initialized flag
        self._initialized = False
        
        logger.info(
            "Content classifier initialized",
            ai_available=_AI_AVAILABLE,
            config=self.config,
            version="3.0.0"
        )
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            'cache_enabled': True,
            'cache_ttl_seconds': 3600,
            'confidence_threshold': 0.5,
            'enable_metadata_extraction': True,
            'enable_recommendations': True,
            'max_keywords': 20,
            'max_entities': 50
        }
    
    async def initialize(self) -> None:
        """Initialize all classifiers"""
        if self._initialized:
            return
        
        try:
            await asyncio.gather(
                self.image_classifier.initialize(),
                self.audio_classifier.initialize(),
                self.text_classifier.initialize(),
                self.metadata_extractor.initialize()
            )
            self._initialized = True
            logger.info("All content classifiers initialized")
        except Exception as e:
            logger.error(f"Failed to initialize content classifier: {e}")
            raise
    
    @handle_processing_errors("content_classification")
    async def classify_content(
        self,
        content_path: str,
        content_type: str,
        options: Optional[Dict[str, Any]] = None
    ) -> ContentAnalysisResult:
        """Classify content and extract metadata"""
        
        if not self._initialized:
            await self.initialize()
        
        start_time = time.time()
        options = options or {}
        
        # Update statistics
        self.processing_stats['total_classifications'] += 1
        
        try:
            # Check cache first
            if self.config.get('cache_enabled'):
                cache_key = self._generate_cache_key(content_path, content_type, options)
                if cache_key in self.classification_cache:
                    cached_result = self.classification_cache[cache_key]
                    logger.info("Using cached classification result", cache_key=cache_key)
                    return cached_result
            
            # Perform classification based on content type
            classification_result = None
            
            if content_type.lower() in ['image', 'photo', 'picture']:
                classification_result = await self.image_classifier.classify_image(content_path)
            elif content_type.lower() in ['audio', 'music', 'sound']:
                classification_result = await self.audio_classifier.classify_audio(content_path)
            elif content_type.lower() in ['text', 'document', 'article']:
                with open(content_path, 'r', encoding='utf-8') as f:
                    text_content = f.read()
                classification_result = await self.text_classifier.classify_text(text_content)
            else:
                # Default classification for unknown types
                classification_result = ClassificationResult(
                    category=ContentCategory.OTHER,
                    confidence=0.5,
                    tags=['unknown_type'],
                    metadata={'content_type': content_type}
                )
            
            # Extract metadata if enabled
            metadata_result = MetadataExtractionResult()
            if self.config.get('enable_metadata_extraction', True):
                metadata_result = await self.metadata_extractor.extract_metadata(
                    content_path, content_type, classification_result
                )
            
            # Generate recommendations if enabled
            recommendations = []
            if self.config.get('enable_recommendations', True):
                recommendations = self._generate_recommendations(classification_result, metadata_result)
            
            # Calculate confidence scores
            confidence_scores = self._calculate_confidence_scores(classification_result, metadata_result)
            
            processing_time = int((time.time() - start_time) * 1000)
            
            # Create final result
            result = ContentAnalysisResult(
                classification=classification_result,
                metadata=metadata_result,
                processing_time_ms=processing_time,
                confidence_scores=confidence_scores,
                recommendations=recommendations
            )
            
            # Cache result if enabled
            if self.config.get('cache_enabled'):
                self.classification_cache[cache_key] = result
            
            # Update statistics
            self.processing_stats['successful_classifications'] += 1
            self.processing_stats['category_counts'][classification_result.category.value] += 1
            
            logger.info(
                "Content classification completed",
                category=classification_result.category.value,
                confidence=classification_result.confidence,
                processing_time_ms=processing_time
            )
            
            return result
            
        except Exception as e:
            self.processing_stats['failed_classifications'] += 1
            logger.error(f"Content classification failed: {e}")
            raise
    
    def _generate_recommendations(
        self,
        classification: ClassificationResult,
        metadata: MetadataExtractionResult
    ) -> List[str]:
        """Generate content optimization recommendations"""
        recommendations = []
        
        # Quality-based recommendations
        if classification.quality_level == QualityLevel.LOW_QUALITY:
            recommendations.append("Consider improving content quality for better engagement")
        elif classification.quality_level == QualityLevel.BASIC:
            recommendations.append("Enhance content with better equipment or editing")
        
        # Category-specific recommendations
        if classification.category == ContentCategory.MUSIC:
            recommendations.extend([
                "Add genre tags for better discoverability",
                "Consider creating playlist-ready versions",
                "Optimize for streaming platforms"
            ])
        elif classification.category == ContentCategory.PHOTOGRAPHY:
            recommendations.extend([
                "Use relevant location tags",
                "Consider different aspect ratios for various platforms",
                "Add descriptive captions"
            ])
        elif classification.category == ContentCategory.BLOG_POST:
            recommendations.extend([
                "Optimize for SEO with relevant keywords",
                "Break up long paragraphs for readability",
                "Add compelling headlines"
            ])
        
        # Platform-specific recommendations
        if hasattr(metadata, 'business_metadata') and metadata.business_metadata:
            platform_suitability = metadata.business_metadata.get('platform_suitability', {})
            best_platform = max(platform_suitability.items(), key=lambda x: x[1], default=(None, 0))
            if best_platform[0] and best_platform[1] > 0.8:
                recommendations.append(f"Optimize for {best_platform[0]} - highest platform compatibility")
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    def _calculate_confidence_scores(
        self,
        classification: ClassificationResult,
        metadata: MetadataExtractionResult
    ) -> Dict[str, float]:
        """Calculate overall confidence scores"""
        scores = {
            'classification_confidence': classification.confidence,
            'metadata_completeness': 0.0,
            'overall_quality': 0.0
        }
        
        # Calculate metadata completeness
        metadata_fields = [
            metadata.title,
            metadata.description,
            metadata.keywords,
            metadata.technical_metadata,
            metadata.semantic_metadata
        ]
        
        non_empty_fields = sum(1 for field in metadata_fields if field)
        scores['metadata_completeness'] = non_empty_fields / len(metadata_fields)
        
        # Calculate overall quality
        quality_factors = [
            classification.confidence,
            scores['metadata_completeness'],
            1.0 if classification.quality_level in [QualityLevel.PROFESSIONAL, QualityLevel.SEMI_PROFESSIONAL] else 0.5
        ]
        
        scores['overall_quality'] = sum(quality_factors) / len(quality_factors)
        
        return scores
    
    def _generate_cache_key(
        self,
        content_path: str,
        content_type: str,
        options: Dict[str, Any]
    ) -> str:
        """Generate cache key for classification request"""
        import hashlib
        
        # Get file modification time for cache invalidation
        try:
            mtime = Path(content_path).stat().st_mtime
        except:
            mtime = 0
        
        key_components = [
            content_path,
            content_type,
            str(mtime),
            str(sorted(options.items()))
        ]
        
        key_string = "|".join(key_components)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        return {
            **self.processing_stats,
            'cache_size': len(self.classification_cache),
            'initialized': self._initialized
        }
    
    async def cleanup(self) -> None:
        """Cleanup resources"""
        # Clear cache
        self.classification_cache.clear()
        
        # Reset initialized flag
        self._initialized = False
        
        logger.info("Content classifier cleanup completed")

# =============================================================================
# GLOBAL CLASSIFIER INSTANCE
# =============================================================================

_content_classifier: Optional[ContentClassifier] = None

def get_content_classifier(config: Optional[Dict[str, Any]] = None) -> ContentClassifier:
    """Get global content classifier instance"""
    global _content_classifier
    if _content_classifier is None:
        _content_classifier = ContentClassifier(config)
    return _content_classifier

# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    'ContentClassifier',
    'ImageClassifier',
    'AudioClassifier',
    'TextClassifier',
    'MetadataExtractor',
    'ClassificationResult',
    'MetadataExtractionResult',
    'ContentAnalysisResult',
    'ContentCategory',
    'QualityLevel',
    'AudienceType',
    'ContentMood',
    'get_content_classifier'
]

# Initialize logging
logger.info(
    "Content classifier module initialized",
    module="media_processing.content_classifier",
    ai_available=_AI_AVAILABLE,
    version="3.0.0"
)
