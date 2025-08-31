"""
Content Optimizer - Advanced AI-Powered Content Enhancement Engine
================================================================

This module provides comprehensive content optimization capabilities using advanced AI
models to enhance content quality, engagement potential, and platform compliance
across multiple content formats.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: Proprietary code - Unauthorized use prohibited and legally prosecuted.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timezone
import json

import numpy as np
from PIL import Image
import cv2
import librosa
import torch
from transformers import (
    AutoTokenizer, AutoModel, GPT2LMHeadModel,
    BlipProcessor, BlipForConditionalGeneration
)
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from backend.core.config import get_settings
from backend.core.logging import get_logger
from backend.ai.nlp.text_processor import TextProcessor
from backend.ai.vision.image_analyzer import ImageAnalyzer
from backend.ai.audio.audio_processor import AudioProcessor

logger = get_logger(__name__)
settings = get_settings()


class ContentType(Enum):
    """Content types supported by the optimization engine."""
    MUSIC = "music"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    PODCAST = "podcast"
    LIVE_STREAM = "live_stream"


class OptimizationLevel(Enum):
    """Optimization intensity levels."""
    BASIC = "basic"
    ADVANCED = "advanced"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


@dataclass
class OptimizationMetrics:
    """Metrics for content optimization analysis."""
    engagement_score: float
    quality_score: float
    seo_score: float
    brand_safety_score: float
    monetization_potential: float
    viral_potential: float
    accessibility_score: float
    platform_compliance: Dict[str, float]
    optimization_suggestions: List[str]
    confidence_level: float


@dataclass
class ContentOptimizationRequest:
    """Request structure for content optimization."""
    content_id: str
    content_type: ContentType
    content_data: Union[str, bytes, Dict[str, Any]]
    target_platforms: List[str]
    optimization_level: OptimizationLevel
    target_audience: Optional[Dict[str, Any]] = None
    brand_guidelines: Optional[Dict[str, Any]] = None
    monetization_goals: Optional[List[str]] = None
    custom_parameters: Optional[Dict[str, Any]] = None


@dataclass
class OptimizationResult:
    """Result structure for content optimization."""
    request_id: str
    content_id: str
    original_metrics: OptimizationMetrics
    optimized_metrics: OptimizationMetrics
    optimization_recommendations: List[Dict[str, Any]]
    enhanced_content: Optional[Dict[str, Any]]
    processing_time: float
    optimization_strategy: str
    platform_specific_versions: Dict[str, Any]
    monetization_insights: Dict[str, Any]
    performance_predictions: Dict[str, float]
    created_at: datetime


class ContentOptimizer:
    """
    Advanced AI-powered content optimization engine for multi-format content.
    
    This class provides comprehensive content optimization capabilities using
    state-of-the-art AI models for enhancing engagement, quality, and monetization
    potential across multiple platforms and content formats.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the content optimizer with advanced AI models."""
        self.config = config or {}
        self.logger = get_logger(f"{__name__}.{self.__class__.__name__}")
        
        # Initialize AI models for different content types
        self._initialize_models()
        
        # Platform-specific optimization rules
        self.platform_rules = self._load_platform_rules()
        
        # Content quality metrics
        self.quality_analyzer = ContentQualityAnalyzer()
        
        # SEO and engagement optimizer
        self.seo_optimizer = SEOOptimizer()
        
        # Brand safety validator
        self.brand_safety = BrandSafetyValidator()
        
        # Monetization advisor
        self.monetization_advisor = MonetizationAdvisor()
        
    def _initialize_models(self):
        """Initialize AI models for content optimization."""



        try:
            # Text analysis models
            self.text_tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
            self.text_model = AutoModel.from_pretrained("bert-base-uncased")
            
            # Image analysis models
            self.image_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
            self.image_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
            
            # Audio analysis models (initialized when needed)
            self.audio_processor = None
            
            # GPT model for content generation
            self.content_generator = GPT2LMHeadModel.from_pretrained("gpt2-medium")
            
            self.logger.info("AI models initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize AI models: {e}")
            raise
    
    def _load_platform_rules(self) -> Dict[str, Dict[str, Any]]:
        """Load platform-specific optimization rules."""



        return {
            "youtube": {
                "title_length": {"min": 10, "max": 100, "optimal": 60},
                "description_length": {"min": 125, "max": 5000, "optimal": 200},
                "tags_count": {"min": 5, "max": 15, "optimal": 10},
                "thumbnail_size": {"width": 1280, "height": 720},
                "video_duration": {"min": 60, "max": 3600, "optimal": 480},
                "upload_frequency": {"min": 1, "max": 7, "optimal": 3},
                "engagement_window": 48,  # hours
                "monetization_threshold": 1000  # subscribers
            },
            "tiktok": {
                "title_length": {"min": 10, "max": 150, "optimal": 100},
                "video_duration": {"min": 15, "max": 180, "optimal": 60},
                "hashtags_count": {"min": 3, "max": 10, "optimal": 5},
                "trending_window": 6,  # hours
                "optimal_posting_times": ["18:00", "19:00", "20:00"],
                "engagement_rate": {"min": 0.05, "target": 0.15}
            },
            "instagram": {
                "caption_length": {"min": 50, "max": 2200, "optimal": 300},
                "hashtags_count": {"min": 5, "max": 30, "optimal": 11},
                "image_size": {"width": 1080, "height": 1080},
                "story_duration": {"min": 5, "max": 15, "optimal": 10},
                "reel_duration": {"min": 15, "max": 90, "optimal": 30},
                "posting_frequency": {"min": 1, "max": 3, "optimal": 1}
            },
            "spotify": {
                "track_duration": {"min": 30, "max": 600, "optimal": 210},
                "album_tracks": {"min": 3, "max": 20, "optimal": 10},
                "metadata_quality": {"min": 0.8, "target": 0.95},
                "cover_art_size": {"width": 3000, "height": 3000},
                "genre_tags": {"min": 1, "max": 5, "optimal": 3},
                "release_frequency": {"min": 1, "max": 12, "optimal": 4}  # per year
            },
            "twitter": {
                "text_length": {"min": 10, "max": 280, "optimal": 140},
                "hashtags_count": {"min": 1, "max": 5, "optimal": 2},
                "media_count": {"min": 1, "max": 4, "optimal": 1},
                "thread_length": {"min": 2, "max": 25, "optimal": 5},
                "engagement_window": 24  # hours
            }
        }
    
    async def optimize_content(
        self, 
        request: ContentOptimizationRequest
    ) -> OptimizationResult:
        """
        Optimize content using advanced AI analysis and platform-specific rules.
        
        Args:
            request: Content optimization request with all parameters
            
        Returns:
            OptimizationResult: Comprehensive optimization results
        """
        start_time = datetime.now(timezone.utc)
        request_id = f"opt_{int(start_time.timestamp())}"
        
        try:
            self.logger.info(f"Starting content optimization for {request.content_id}")
            
            # Analyze original content
            original_metrics = await self._analyze_content_metrics(
                request.content_data,
                request.content_type,
                request.target_platforms
            )
            
            # Generate optimization recommendations
            recommendations = await self._generate_recommendations(
                request,
                original_metrics
            )
            
            # Apply optimizations
            enhanced_content = await self._apply_optimizations(
                request,
                recommendations
            )
            
            # Analyze optimized content
            optimized_metrics = await self._analyze_content_metrics(
                enhanced_content,
                request.content_type,
                request.target_platforms
            )
            
            # Generate platform-specific versions
            platform_versions = await self._create_platform_versions(
                enhanced_content,
                request.target_platforms,
                request.content_type
            )
            
            # Calculate monetization insights
            monetization_insights = await self._calculate_monetization_insights(
                optimized_metrics,
                request.monetization_goals or []
            )
            
            # Predict performance
            performance_predictions = await self._predict_performance(
                optimized_metrics,
                request.target_platforms
            )
            
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            result = OptimizationResult(
                request_id=request_id,
                content_id=request.content_id,
                original_metrics=original_metrics,
                optimized_metrics=optimized_metrics,
                optimization_recommendations=recommendations,
                enhanced_content=enhanced_content,
                processing_time=processing_time,
                optimization_strategy=request.optimization_level.value,
                platform_specific_versions=platform_versions,
                monetization_insights=monetization_insights,
                performance_predictions=performance_predictions,
                created_at=start_time
            )
            
            self.logger.info(f"Content optimization completed for {request.content_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Content optimization failed: {e}")
            raise
    
    async def _analyze_content_metrics(
        self,
        content_data: Union[str, bytes, Dict[str, Any]],
        content_type: ContentType,
        target_platforms: List[str]
    ) -> OptimizationMetrics:
        """Analyze content and calculate comprehensive metrics."""
        
        # Initialize metrics
        engagement_score = 0.0
        quality_score = 0.0
        seo_score = 0.0
        brand_safety_score = 0.0
        monetization_potential = 0.0
        viral_potential = 0.0
        accessibility_score = 0.0
        platform_compliance = {}
        suggestions = []
        confidence_level = 0.0
        
        try:
            if content_type == ContentType.TEXT:
                # Text content analysis
                text_metrics = await self._analyze_text_content(content_data)
                engagement_score = text_metrics["engagement"]
                quality_score = text_metrics["quality"]
                seo_score = text_metrics["seo"]
                
            elif content_type == ContentType.IMAGE:
                # Image content analysis
                image_metrics = await self._analyze_image_content(content_data)
                engagement_score = image_metrics["visual_appeal"]
                quality_score = image_metrics["technical_quality"]
                
            elif content_type == ContentType.VIDEO:
                # Video content analysis
                video_metrics = await self._analyze_video_content(content_data)
                engagement_score = video_metrics["engagement"]
                quality_score = video_metrics["production_quality"]
                
            elif content_type == ContentType.MUSIC:
                # Music content analysis
                audio_metrics = await self._analyze_audio_content(content_data)
                engagement_score = audio_metrics["musicality"]
                quality_score = audio_metrics["audio_quality"]
                
            # Brand safety analysis
            brand_safety_score = await self._analyze_brand_safety(content_data, content_type)
            
            # Platform compliance analysis
            for platform in target_platforms:
                compliance_score = await self._check_platform_compliance(
                    content_data, content_type, platform
                )
                platform_compliance[platform] = compliance_score
            
            # Monetization potential calculation
            monetization_potential = await self._calculate_monetization_potential(
                content_data, content_type, target_platforms
            )
            
            # Viral potential analysis
            viral_potential = await self._analyze_viral_potential(
                content_data, content_type
            )
            
            # Accessibility score
            accessibility_score = await self._calculate_accessibility_score(
                content_data, content_type
            )
            
            # Generate optimization suggestions
            suggestions = await self._generate_optimization_suggestions(
                content_data, content_type, target_platforms
            )
            
            # Calculate overall confidence
            confidence_level = np.mean([
                engagement_score, quality_score, seo_score,
                brand_safety_score, monetization_potential
            ])
            
        except Exception as e:
            self.logger.error(f"Content metrics analysis failed: {e}")
            suggestions.append("Failed to analyze content metrics")
        
        return OptimizationMetrics(
            engagement_score=engagement_score,
            quality_score=quality_score,
            seo_score=seo_score,
            brand_safety_score=brand_safety_score,
            monetization_potential=monetization_potential,
            viral_potential=viral_potential,
            accessibility_score=accessibility_score,
            platform_compliance=platform_compliance,
            optimization_suggestions=suggestions,
            confidence_level=confidence_level
        )
    performance_predictions: Dict[str, float]
    processing_time: float
    created_at: datetime


class OptimizationEngine:
    """
    Advanced AI-powered content optimization engine that analyzes and enhances
    content across multiple formats and platforms.
    """
    
    def __init__(self):
        """Initialize the optimization engine with AI models and processors."""
        self.text_processor = TextProcessor()
        self.image_analyzer = ImageAnalyzer()
        self.audio_processor = AudioProcessor()
        
        # Load AI models for optimization
        self._load_optimization_models()
        
        # Platform-specific optimization rules
        self.platform_rules = {
            'youtube': {
                'title_max_length': 100,
                'description_max_length': 5000,
                'tags_max_count': 15,
                'optimal_duration': {'min': 8*60, 'max': 15*60},
                'thumbnail_dimensions': (1280, 720),
                'video_quality': ['1080p', '4K'],
                'engagement_factors': ['watch_time', 'comments', 'likes', 'shares']
            },
            'instagram': {
                'caption_max_length': 2200,
                'hashtags_max_count': 30,
                'optimal_aspect_ratios': ['1:1', '4:5', '9:16'],
                'story_duration': 15,
                'reel_duration': {'min': 15, 'max': 90},
                'engagement_factors': ['likes', 'comments', 'shares', 'saves']
            },
            'tiktok': {
                'caption_max_length': 300,
                'hashtags_max_count': 20,
                'video_duration': {'min': 15, 'max': 180},
                'aspect_ratio': '9:16',
                'engagement_factors': ['views', 'likes', 'shares', 'comments']
            },
            'spotify': {
                'track_title_max_length': 100,
                'artist_bio_max_length': 1500,
                'playlist_title_max_length': 100,
                'audio_quality': ['320kbps', 'lossless'],
                'genre_tags_max': 10,
                'engagement_factors': ['streams', 'saves', 'playlists', 'followers']
            }
        }
        
        self.optimization_cache = {}
        logger.info("Content optimization engine initialized successfully")
    
    def _load_optimization_models(self):
        """Load AI models for content optimization."""



        try:
            # Text optimization models
            self.tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')
            self.text_model = AutoModel.from_pretrained('bert-base-uncased')
            
            # Image optimization models
            self.blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
            self.blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
            
            # TF-IDF for SEO optimization
            self.tfidf_vectorizer = TfidfVectorizer(max_features=10000, stop_words='english')
            
            logger.info("AI optimization models loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load optimization models: {e}")
            raise
    
    async def optimize_content(self, request: ContentOptimizationRequest) -> OptimizationResult:
        """
        Optimize content based on the provided request parameters.
        
        Args:
            request: Content optimization request
            
        Returns:
            OptimizationResult: Comprehensive optimization results
        """
        start_time = datetime.now(timezone.utc)
        
        try:
            # Analyze original content
            original_metrics = await self._analyze_content_metrics(
                request.content_data,
                request.content_type,
                request.target_platforms
            )
            
            # Generate optimization recommendations
            recommendations = await self._generate_recommendations(
                request, original_metrics
            )
            
            # Apply optimizations if requested
            enhanced_content = None
            if request.optimization_level != OptimizationLevel.BASIC:
                enhanced_content = await self._apply_optimizations(
                    request, recommendations
                )
            
            # Calculate optimized metrics
            optimized_metrics = await self._calculate_optimized_metrics(
                original_metrics, recommendations
            )
            
            # Generate performance predictions
            predictions = await self._predict_performance(
                request, optimized_metrics
            )
            
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            result = OptimizationResult(
                request_id=f"opt_{int(start_time.timestamp())}_{request.content_id}",
                content_id=request.content_id,
                original_metrics=original_metrics,
                optimized_metrics=optimized_metrics,
                optimization_recommendations=recommendations,
                enhanced_content=enhanced_content,
                performance_predictions=predictions,
                processing_time=processing_time,
                created_at=start_time
            )
            
            logger.info(f"Content optimization completed for {request.content_id}")
            return result
            
        except Exception as e:
            logger.error(f"Content optimization failed for {request.content_id}: {e}")
            raise
    
    async def _analyze_content_metrics(
        self,
        content_data: Union[str, bytes, Dict[str, Any]],
        content_type: ContentType,
        target_platforms: List[str]
    ) -> OptimizationMetrics:
        """Analyze content and calculate baseline metrics."""
        
        if content_type == ContentType.TEXT:
            return await self._analyze_text_metrics(content_data, target_platforms)
        elif content_type == ContentType.IMAGE:
            return await self._analyze_image_metrics(content_data, target_platforms)
        elif content_type == ContentType.MUSIC:
            return await self._analyze_audio_metrics(content_data, target_platforms)
        elif content_type == ContentType.VIDEO:
            return await self._analyze_video_metrics(content_data, target_platforms)
        else:
            # Default analysis for other content types
            return await self._analyze_generic_metrics(content_data, target_platforms)
    
    async def _analyze_text_metrics(
        self, text: str, target_platforms: List[str]
    ) -> OptimizationMetrics:
        """Analyze text content metrics."""
        
        # Text quality analysis
        word_count = len(text.split())
        readability_score = self._calculate_readability(text)
        sentiment_score = await self.text_processor.analyze_sentiment(text)
        
        # SEO analysis
        seo_score = self._calculate_seo_score(text)
        
        # Platform compliance
        platform_compliance = {}
        for platform in target_platforms:
            compliance = self._check_platform_compliance(text, platform, ContentType.TEXT)
            platform_compliance[platform] = compliance
        
        # Engagement prediction
        engagement_score = self._predict_text_engagement(text, target_platforms)
        
        # Brand safety
        brand_safety_score = await self._analyze_brand_safety(text)
        
        return OptimizationMetrics(
            engagement_score=engagement_score,
            quality_score=min(readability_score * 0.7 + sentiment_score['compound'] * 0.3, 1.0),
            seo_score=seo_score,
            brand_safety_score=brand_safety_score,
            monetization_potential=self._calculate_monetization_potential(text, ContentType.TEXT),
            viral_potential=self._calculate_viral_potential(text, target_platforms),
            accessibility_score=self._calculate_accessibility_score(text, ContentType.TEXT),
            platform_compliance=platform_compliance,
            optimization_suggestions=[],
            confidence_level=0.85
        )
    
    async def _analyze_image_metrics(
        self, image_data: bytes, target_platforms: List[str]
    ) -> OptimizationMetrics:
        """Analyze image content metrics."""
        
        # Load and analyze image
        image = Image.open(io.BytesIO(image_data))
        
        # Image quality metrics
        quality_metrics = await self.image_analyzer.analyze_quality(image)
        
        # Visual appeal scoring
        visual_appeal = self._score_visual_appeal(image)
        
        # Platform compliance
        platform_compliance = {}
        for platform in target_platforms:
            compliance = self._check_image_platform_compliance(image, platform)
            platform_compliance[platform] = compliance
        
        # Engagement prediction
        engagement_score = self._predict_image_engagement(image, target_platforms)
        
        return OptimizationMetrics(
            engagement_score=engagement_score,
            quality_score=quality_metrics.get('overall_score', 0.7),
            seo_score=0.6,  # Images have lower SEO impact without proper metadata
            brand_safety_score=quality_metrics.get('safety_score', 0.9),
            monetization_potential=self._calculate_monetization_potential(image, ContentType.IMAGE),
            viral_potential=visual_appeal * 0.8,
            accessibility_score=self._calculate_accessibility_score(image, ContentType.IMAGE),
            platform_compliance=platform_compliance,
            optimization_suggestions=[],
            confidence_level=0.8
        )
    
    async def _generate_recommendations(
        self,
        request: ContentOptimizationRequest,
        metrics: OptimizationMetrics
    ) -> List[Dict[str, Any]]:
        """Generate comprehensive optimization recommendations."""
        
        recommendations = []
        
        # Quality improvements
        if metrics.quality_score < 0.7:
            recommendations.extend(await self._generate_quality_recommendations(
                request.content_type, request.content_data
            ))
        
        # SEO optimizations
        if metrics.seo_score < 0.8:
            recommendations.extend(await self._generate_seo_recommendations(
                request.content_type, request.content_data, request.target_platforms
            ))
        
        # Engagement optimizations
        if metrics.engagement_score < 0.6:
            recommendations.extend(await self._generate_engagement_recommendations(
                request.content_type, request.target_platforms
            ))
        
        # Platform-specific optimizations
        for platform in request.target_platforms:
            platform_recs = await self._generate_platform_recommendations(
                platform, request.content_type, metrics
            )
            recommendations.extend(platform_recs)
        
        # Monetization optimizations
        if request.monetization_goals:
            monetization_recs = await self._generate_monetization_recommendations(
                request.monetization_goals, metrics
            )
            recommendations.extend(monetization_recs)
        
        return recommendations
    
    def _calculate_readability(self, text: str) -> float:
        """Calculate text readability score using Flesch Reading Ease."""
        words = text.split()
        sentences = text.split('.')
        syllables = sum([self._count_syllables(word) for word in words])
        
        if len(sentences) == 0 or len(words) == 0:
            return 0.5
        
        avg_sentence_length = len(words) / len(sentences)
        avg_syllables_per_word = syllables / len(words)
        
        flesch_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
        
        # Normalize to 0-1 scale
        return max(0, min(1, flesch_score / 100))
    
    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word (simple heuristic)."""
        word = word.lower()
        vowels = 'aeiouy'
        count = sum(1 for char in word if char in vowels)
        if word.endswith('e'):
            count -= 1
        return max(1, count)
    
    def _calculate_seo_score(self, text: str) -> float:
        """Calculate SEO optimization score for text content."""
        score = 0.5  # Base score
        
        # Check for keywords density
        words = text.lower().split()
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Optimal keyword density (2-5%)
        total_words = len(words)
        if total_words > 0:
            max_freq = max(word_freq.values())
            keyword_density = max_freq / total_words
            
            if 0.02 <= keyword_density <= 0.05:
                score += 0.2
            elif 0.01 <= keyword_density <= 0.08:
                score += 0.1
        
        # Check for title and structure
        if any(char.isupper() for char in text):
            score += 0.1
        
        # Check length (optimal 300-2000 words)
        if 300 <= len(words) <= 2000:
            score += 0.2
        elif 100 <= len(words) <= 3000:
            score += 0.1
        
        return min(1.0, score)
    
    async def _analyze_brand_safety(self, content: Union[str, Any]) -> float:
        """Analyze content for brand safety compliance."""
        # Implement brand safety scoring using AI models
        # This would integrate with content moderation APIs
        
        safety_score = 0.9  # Default high safety score
        
        if isinstance(content, str):
            # Check for problematic keywords
            problematic_keywords = [
                'hate', 'violence', 'explicit', 'inappropriate',
                'illegal', 'harmful', 'offensive'
            ]
            
            text_lower = content.lower()
            for keyword in problematic_keywords:
                if keyword in text_lower:
                    safety_score -= 0.1
        
        return max(0.0, min(1.0, safety_score))
    
    def _calculate_monetization_potential(
        self, content: Any, content_type: ContentType
    ) -> float:
        """Calculate monetization potential based on content analysis."""
        
        base_score = 0.5
        
        if content_type == ContentType.MUSIC:
            # Music has high monetization potential
            base_score = 0.8
        elif content_type == ContentType.VIDEO:
            base_score = 0.7
        elif content_type == ContentType.IMAGE:
            base_score = 0.4
        elif content_type == ContentType.TEXT:
            base_score = 0.3
        
        # Additional factors would be analyzed here
        # (brand partnerships, affiliate potential, etc.)
        
        return base_score
    
    def _calculate_viral_potential(
        self, content: Any, target_platforms: List[str]
    ) -> float:
        """Calculate viral potential based on content and platform analysis."""
        
        viral_score = 0.5  # Base score
        
        # Platform-specific viral factors
        platform_viral_multipliers = {
            'tiktok': 1.3,
            'instagram': 1.1,
            'youtube': 1.0,
            'twitter': 1.2,
            'spotify': 0.8
        }
        
        if target_platforms:
            avg_multiplier = sum(
                platform_viral_multipliers.get(platform, 1.0)
                for platform in target_platforms
            ) / len(target_platforms)
            viral_score *= avg_multiplier
        
        return min(1.0, viral_score)
    
    def _calculate_accessibility_score(
        self, content: Any, content_type: ContentType
    ) -> float:
        """Calculate accessibility score for content."""
        
        # Default accessibility scores by content type
        accessibility_scores = {
            ContentType.TEXT: 0.9,      # Text is highly accessible
            ContentType.IMAGE: 0.6,     # Needs alt text
            ContentType.MUSIC: 0.7,     # Needs transcription
            ContentType.VIDEO: 0.5,     # Needs captions and audio description
            ContentType.PODCAST: 0.6,   # Needs transcription
            ContentType.LIVE_STREAM: 0.4  # Harder to make accessible
        }
        
        return accessibility_scores.get(content_type, 0.5)
    
    def _check_platform_compliance(
        self, content: str, platform: str, content_type: ContentType
    ) -> float:
        """Check content compliance with platform-specific rules."""
        
        if platform not in self.platform_rules:
            return 0.8  # Default compliance score
        
        rules = self.platform_rules[platform]
        compliance_score = 1.0
        
        if content_type == ContentType.TEXT:
            # Check text length limits
            text_length = len(content)
            if 'caption_max_length' in rules:
                if text_length > rules['caption_max_length']:
                    compliance_score -= 0.3
                elif text_length > rules['caption_max_length'] * 0.9:
                    compliance_score -= 0.1
        
        return max(0.0, compliance_score)
    
    def _check_image_platform_compliance(self, image: Image.Image, platform: str) -> float:
        """Check image compliance with platform-specific requirements."""
        
        if platform not in self.platform_rules:
            return 0.8
        
        rules = self.platform_rules[platform]
        compliance_score = 1.0
        
        # Check aspect ratio if specified
        if 'optimal_aspect_ratios' in rules:
            width, height = image.size
            aspect_ratio = width / height
            
            # Check if aspect ratio matches platform requirements
            optimal_ratios = rules['optimal_aspect_ratios']
            ratio_matches = False
            
            for ratio_str in optimal_ratios:
                if ':' in ratio_str:
                    w, h = map(int, ratio_str.split(':'))
                    target_ratio = w / h
                    if abs(aspect_ratio - target_ratio) < 0.1:
                        ratio_matches = True
                        break
            
            if not ratio_matches:
                compliance_score -= 0.2
        
        return max(0.0, compliance_score)
    
    def _predict_text_engagement(self, text: str, platforms: List[str]) -> float:
        """Predict engagement potential for text content."""
        
        engagement_score = 0.5  # Base score
        
        # Length optimization
        word_count = len(text.split())
        if 50 <= word_count <= 300:
            engagement_score += 0.2
        elif 10 <= word_count <= 500:
            engagement_score += 0.1
        
        # Question marks increase engagement
        if '?' in text:
            engagement_score += 0.1
        
        # Call-to-action phrases
        cta_phrases = ['like', 'share', 'comment', 'follow', 'subscribe', 'click']
        for phrase in cta_phrases:
            if phrase.lower() in text.lower():
                engagement_score += 0.05
                break
        
        # Emoji presence
        emoji_pattern = r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]'
        import re
        if re.search(emoji_pattern, text):
            engagement_score += 0.1
        
        return min(1.0, engagement_score)
    
    def _predict_image_engagement(self, image: Image.Image, platforms: List[str]) -> float:
        """Predict engagement potential for image content."""
        
        engagement_score = 0.5  # Base score
        
        # Color diversity
        colors = image.getcolors(maxcolors=256*256*256)
        if colors and len(colors) > 50:
            engagement_score += 0.1
        
        # Resolution quality
        width, height = image.size
        pixel_count = width * height
        if pixel_count >= 1920 * 1080:  # Full HD or higher
            engagement_score += 0.2
        elif pixel_count >= 1280 * 720:  # HD
            engagement_score += 0.1
        
        return min(1.0, engagement_score)
    
    def _score_visual_appeal(self, image: Image.Image) -> float:
        """Score visual appeal of an image using computer vision."""
        
        # Convert to OpenCV format
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Calculate composition metrics
        appeal_score = 0.5
        
        # Rule of thirds
        height, width = cv_image.shape[:2]
        thirds_x = [width // 3, 2 * width // 3]
        thirds_y = [height // 3, 2 * height // 3]
        
        # Color harmony
        hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
        hist = cv2.calcHist([hsv], [0], None, [180], [0, 180])
        color_variance = np.var(hist)
        
        if 500 < color_variance < 2000:  # Good color distribution
            appeal_score += 0.2
        
        # Brightness and contrast
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        brightness = np.mean(gray)
        contrast = np.std(gray)
        
        if 80 < brightness < 180 and contrast > 30:
            appeal_score += 0.1
        
        return min(1.0, appeal_score)
    
    async def _calculate_optimized_metrics(
        self,
        original_metrics: OptimizationMetrics,
        recommendations: List[Dict[str, Any]]
    ) -> OptimizationMetrics:
        """Calculate projected metrics after applying optimizations."""
        
        # Start with original metrics
        optimized = OptimizationMetrics(
            engagement_score=original_metrics.engagement_score,
            quality_score=original_metrics.quality_score,
            seo_score=original_metrics.seo_score,
            brand_safety_score=original_metrics.brand_safety_score,
            monetization_potential=original_metrics.monetization_potential,
            viral_potential=original_metrics.viral_potential,
            accessibility_score=original_metrics.accessibility_score,
            platform_compliance=original_metrics.platform_compliance.copy(),
            optimization_suggestions=recommendations,
            confidence_level=original_metrics.confidence_level
        )
        
        # Apply improvements based on recommendations
        for rec in recommendations:
            impact = rec.get('impact', 0.1)
            category = rec.get('category', 'general')
            
            if category == 'engagement':
                optimized.engagement_score = min(1.0, optimized.engagement_score + impact)
            elif category == 'quality':
                optimized.quality_score = min(1.0, optimized.quality_score + impact)
            elif category == 'seo':
                optimized.seo_score = min(1.0, optimized.seo_score + impact)
            elif category == 'monetization':
                optimized.monetization_potential = min(1.0, optimized.monetization_potential + impact)
        
        return optimized


class ContentQualityAnalyzer:
    """Advanced content quality analysis engine."""
    
    def __init__(self):
        self.logger = get_logger(f"{__name__}.{self.__class__.__name__}")
        
    async def analyze_text_quality(self, text: str) -> Dict[str, float]:
        """Analyze text content quality metrics."""
        
        quality_metrics = {
            "readability": self._calculate_readability(text),
            "grammar": self._check_grammar_quality(text),
            "coherence": self._analyze_coherence(text),
            "informativeness": self._assess_informativeness(text),
            "engagement": self._predict_engagement(text)
        }
        
        return quality_metrics
    
    def _calculate_readability(self, text: str) -> float:
        """Calculate text readability score."""
        
        words = text.split()
        sentences = text.split('.')
        
        if not words or not sentences:
            return 0.0
        
        # Flesch Reading Ease approximation
        avg_sentence_length = len(words) / len(sentences)
        avg_word_length = sum(len(word) for word in words) / len(words)
        
        # Simplified readability calculation
        readability = 1.0 - (avg_sentence_length / 50 + avg_word_length / 10) * 0.5
        
        return max(0.0, min(1.0, readability))
    
    def _check_grammar_quality(self, text: str) -> float:
        """Basic grammar quality assessment."""
        
        # Simple grammar checks
        quality_score = 1.0
        
        # Check for basic punctuation
        if not any(punct in text for punct in '.!?'):
            quality_score -= 0.2
        
        # Check for capitalization
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        for sentence in sentences:
            if sentence and not sentence[0].isupper():
                quality_score -= 0.1
                break
        
        return max(0.0, quality_score)
    
    def _analyze_coherence(self, text: str) -> float:
        """Analyze text coherence and flow."""
        
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        
        if len(sentences) < 2:
            return 0.8  # Single sentence has reasonable coherence
        
        # Simple coherence measure based on sentence similarity
        coherence_score = 0.8  # Base score
        
        # Check for topic consistency (simplified)
        words = set(text.lower().split())
        common_words = len(words) / len(text.split())
        
        if common_words > 0.3:  # Good word reuse indicates coherence
            coherence_score += 0.1
        
        return min(1.0, coherence_score)
    
    def _assess_informativeness(self, text: str) -> float:
        """Assess how informative the content is."""
        
        words = text.split()
        unique_words = set(word.lower() for word in words)
        
        # Vocabulary richness
        vocab_richness = len(unique_words) / len(words) if words else 0
        
        # Length factor
        length_factor = min(1.0, len(words) / 100)  # Optimal around 100 words
        
        # Information density
        info_score = (vocab_richness * 0.6 + length_factor * 0.4)
        
        return min(1.0, info_score)
    
    def _predict_engagement(self, text: str) -> float:
        """Predict engagement potential of text content."""
        
        engagement_indicators = [
            ('?', 0.1),  # Questions
            ('!', 0.05), # Exclamations
            ('you', 0.05), # Direct address
            ('how', 0.05), # How-to content
            ('why', 0.05), # Explanatory content
            ('amazing', 0.03), # Positive adjectives
            ('incredible', 0.03),
            ('must', 0.03), # Urgency
            ('now', 0.03)
        ]
        
        engagement_score = 0.5  # Base score
        text_lower = text.lower()
        
        for indicator, boost in engagement_indicators:
            if indicator in text_lower:
                engagement_score += boost
        
        return min(1.0, engagement_score)


class SEOOptimizer:
    """SEO optimization engine for content."""
    
    def __init__(self):
        self.logger = get_logger(f"{__name__}.{self.__class__.__name__}")
        
    async def optimize_seo(self, content: str, keywords: List[str]) -> Dict[str, Any]:
        """Optimize content for SEO."""
        
        seo_analysis = {
            "keyword_density": self._analyze_keyword_density(content, keywords),
            "title_optimization": self._optimize_title(content, keywords),
            "meta_description": self._generate_meta_description(content, keywords),
            "readability": self._assess_seo_readability(content),
            "structure": self._analyze_content_structure(content),
            "recommendations": []
        }
        
        # Generate SEO recommendations
        seo_analysis["recommendations"] = self._generate_seo_recommendations(
            content, keywords, seo_analysis
        )
        
        return seo_analysis
    
    def _analyze_keyword_density(self, content: str, keywords: List[str]) -> Dict[str, float]:
        """Analyze keyword density in content."""
        
        content_lower = content.lower()
        word_count = len(content.split())
        
        keyword_density = {}
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            occurrences = content_lower.count(keyword_lower)
            density = (occurrences / word_count) * 100 if word_count > 0 else 0
            keyword_density[keyword] = density
        
        return keyword_density
    
    def _optimize_title(self, content: str, keywords: List[str]) -> str:
        """Generate optimized title with keywords."""
        
        # Extract first sentence as potential title
        sentences = content.split('.')
        first_sentence = sentences[0].strip() if sentences else ""
        
        # If no clear title, generate one with primary keyword
        if not first_sentence or len(first_sentence) > 100:
            primary_keyword = keywords[0] if keywords else "Content"
            title = f"Ultimate Guide to {primary_keyword}"
        else:
            title = first_sentence
        
        # Ensure title length is optimal (50-60 characters)
        if len(title) > 60:
            title = title[:57] + "..."
        
        return title
    
    def _generate_meta_description(self, content: str, keywords: List[str]) -> str:
        """Generate SEO-optimized meta description."""
        
        # Extract first 150-160 characters as meta description
        description = content[:150].strip()
        
        # Ensure it ends at a word boundary
        if len(content) > 150:
            last_space = description.rfind(' ')
            if last_space > 100:  # Ensure minimum length
                description = description[:last_space] + "..."
        
        return description
    
    def _assess_seo_readability(self, content: str) -> float:
        """Assess content readability for SEO."""
        
        words = content.split()
        sentences = content.split('.')
        
        if not words or not sentences:
            return 0.0
        
        # Average sentence length (optimal: 15-20 words)
        avg_sentence_length = len(words) / len(sentences)
        sentence_score = 1.0 if 15 <= avg_sentence_length <= 20 else 0.8
        
        # Paragraph structure (check for line breaks)
        paragraphs = content.split('\n\n')
        paragraph_score = 1.0 if len(paragraphs) > 1 else 0.7
        
        readability_score = (sentence_score + paragraph_score) / 2
        
        return readability_score
    
    def _analyze_content_structure(self, content: str) -> Dict[str, Any]:
        """Analyze content structure for SEO."""
        
        structure = {
            "has_headings": bool(re.search(r'^#+ ', content, re.MULTILINE)),
            "has_lists": bool(re.search(r'^\* |^\d+\. ', content, re.MULTILINE)),
            "paragraph_count": len(content.split('\n\n')),
            "word_count": len(content.split()),
            "reading_time": len(content.split()) / 200  # Average reading speed
        }
        
        return structure
    
    def _generate_seo_recommendations(
        self, 
        content: str, 
        keywords: List[str], 
        analysis: Dict[str, Any]
    ) -> List[str]:
        """Generate SEO improvement recommendations."""
        
        recommendations = []
        
        # Keyword density recommendations
        keyword_density = analysis.get("keyword_density", {})
        for keyword, density in keyword_density.items():
            if density < 1:
                recommendations.append(f"Increase usage of keyword '{keyword}' (current: {density:.1f}%)")
            elif density > 3:
                recommendations.append(f"Reduce usage of keyword '{keyword}' (current: {density:.1f}%)")
        
        # Structure recommendations
        structure = analysis.get("structure", {})
        if not structure.get("has_headings"):
            recommendations.append("Add headings to improve content structure")
        
        if not structure.get("has_lists"):
            recommendations.append("Consider adding bullet points or numbered lists")
        
        word_count = structure.get("word_count", 0)
        if word_count < 300:
            recommendations.append("Consider expanding content (current: {word_count} words)")
        elif word_count > 2000:
            recommendations.append("Consider breaking content into smaller sections")
        
        return recommendations


class BrandSafetyValidator:
    """Brand safety and content compliance validator."""
    
    def __init__(self):
        self.logger = get_logger(f"{__name__}.{self.__class__.__name__}")
        self.unsafe_keywords = self._load_unsafe_keywords()
        
    def _load_unsafe_keywords(self) -> List[str]:
        """Load list of potentially unsafe keywords."""
        
        # Basic unsafe content categories
        unsafe_categories = [
            # Violence and harmful content
            "violence", "hate", "discrimination", "harassment",
            # Adult content
            "explicit", "adult", "sexual",
            # Illegal activities
            "drugs", "illegal", "piracy", "copyright",
            # Controversial topics (platform-dependent)
            "political", "religious extremism", "conspiracy"
        ]
        
        return unsafe_categories
    
    async def validate_brand_safety(self, content: str) -> Dict[str, Any]:
        """Validate content for brand safety compliance."""
        
        safety_analysis = {
            "safety_score": self._calculate_safety_score(content),
            "risk_factors": self._identify_risk_factors(content),
            "compliance_level": "high",  # high, medium, low
            "recommendations": []
        }
        
        # Determine compliance level
        if safety_analysis["safety_score"] < 0.6:
            safety_analysis["compliance_level"] = "low"
        elif safety_analysis["safety_score"] < 0.8:
            safety_analysis["compliance_level"] = "medium"
        
        # Generate safety recommendations
        safety_analysis["recommendations"] = self._generate_safety_recommendations(
            content, safety_analysis["risk_factors"]
        )
        
        return safety_analysis
    
    def _calculate_safety_score(self, content: str) -> float:
        """Calculate overall brand safety score."""
        
        content_lower = content.lower()
        risk_count = 0
        total_words = len(content.split())
        
        # Check for unsafe keywords
        for keyword in self.unsafe_keywords:
            if keyword in content_lower:
                risk_count += content_lower.count(keyword)
        
        # Calculate safety score (1.0 = completely safe, 0.0 = high risk)
        if total_words == 0:
            return 1.0
        
        risk_ratio = risk_count / total_words
        safety_score = max(0.0, 1.0 - risk_ratio * 5)  # Amplify risk impact
        
        return safety_score
    
    def _identify_risk_factors(self, content: str) -> List[str]:
        """Identify specific risk factors in content."""
        
        risk_factors = []
        content_lower = content.lower()
        
        # Check for different risk categories
        risk_categories = {
            "violent_language": ["kill", "death", "violence", "fight", "attack"],
            "hate_speech": ["hate", "discrimination", "racism", "sexism"],
            "adult_content": ["sexual", "explicit", "adult", "mature"],
            "illegal_activities": ["drugs", "illegal", "piracy", "steal"],
            "misinformation": ["conspiracy", "fake", "hoax", "false claim"]
        }
        
        for category, keywords in risk_categories.items():
            for keyword in keywords:
                if keyword in content_lower:
                    risk_factors.append(f"{category}: {keyword}")
                    break  # Only add category once
        
        return risk_factors
    
    def _generate_safety_recommendations(
        self, 
        content: str, 
        risk_factors: List[str]
    ) -> List[str]:
        """Generate recommendations to improve brand safety."""
        
        recommendations = []
        
        if risk_factors:
            recommendations.append("Review content for potentially unsafe language")
            recommendations.append("Consider alternative phrasing for flagged terms")
        
        # Content-specific recommendations
        if "violent_language" in str(risk_factors):
            recommendations.append("Remove or replace violent language")
        
        if "hate_speech" in str(risk_factors):
            recommendations.append("Ensure content promotes inclusivity and respect")
        
        if "adult_content" in str(risk_factors):
            recommendations.append("Add appropriate content warnings if necessary")
        
        if not risk_factors:
            recommendations.append("Content meets brand safety standards")
        
        return recommendations


class MonetizationAdvisor:
    """Monetization strategy and revenue optimization advisor."""
    
    def __init__(self):
        self.logger = get_logger(f"{__name__}.{self.__class__.__name__}")
        
    async def analyze_monetization_potential(
        self, 
        content: str, 
        content_type: ContentType,
        platforms: List[str]
    ) -> Dict[str, Any]:
        """Analyze content monetization potential."""
        
        monetization_analysis = {
            "revenue_potential": self._calculate_revenue_potential(content, content_type),
            "monetization_strategies": self._suggest_monetization_strategies(content_type, platforms),
            "optimization_opportunities": self._identify_optimization_opportunities(content),
            "platform_specific_advice": self._generate_platform_advice(platforms, content_type),
            "estimated_earnings": self._estimate_potential_earnings(content, content_type, platforms)
        }
        
        return monetization_analysis
    
    def _calculate_revenue_potential(self, content: str, content_type: ContentType) -> float:
        """Calculate revenue potential score."""
        
        base_potential = {
            ContentType.MUSIC: 0.7,      # High streaming potential
            ContentType.VIDEO: 0.8,      # High ad revenue potential  
            ContentType.IMAGE: 0.5,      # Limited direct monetization
            ContentType.TEXT: 0.4,       # Primarily through engagement
            ContentType.PODCAST: 0.6,    # Sponsorship potential
            ContentType.LIVE_STREAM: 0.9 # High engagement and donation potential
        }
        
        potential = base_potential.get(content_type, 0.5)
        
        # Adjust based on content quality indicators
        if len(content.split()) > 100:  # Substantial content
            potential += 0.1
        
        # Check for commercial intent keywords
        commercial_keywords = ["buy", "purchase", "product", "service", "offer", "deal"]
        if any(keyword in content.lower() for keyword in commercial_keywords):
            potential += 0.1
        
        return min(1.0, potential)
    
    def _suggest_monetization_strategies(
        self, 
        content_type: ContentType, 
        platforms: List[str]
    ) -> List[Dict[str, Any]]:
        """Suggest platform-specific monetization strategies."""
        
        strategies = []
        
        for platform in platforms:
            platform_strategies = self._get_platform_monetization_options(platform, content_type)
            strategies.extend(platform_strategies)
        
        return strategies
    
    def _get_platform_monetization_options(
        self, 
        platform: str, 
        content_type: ContentType
    ) -> List[Dict[str, Any]]:
        """Get monetization options for specific platform."""
        
        options = []
        
        if platform.lower() == "youtube":
            if content_type == ContentType.VIDEO:
                options.extend([
                    {"strategy": "AdSense Revenue", "potential": "high", "requirement": "1000+ subscribers"},
                    {"strategy": "Channel Memberships", "potential": "medium", "requirement": "1000+ subscribers"},
                    {"strategy": "Super Chat/Thanks", "potential": "medium", "requirement": "live streaming"},
                    {"strategy": "Brand Sponsorships", "potential": "high", "requirement": "engaged audience"}
                ])
        
        elif platform.lower() == "spotify":
            if content_type == ContentType.MUSIC:
                options.extend([
                    {"strategy": "Streaming Royalties", "potential": "medium", "requirement": "distribution deal"},
                    {"strategy": "Playlist Placement", "potential": "high", "requirement": "quality content"},
                    {"strategy": "Fan Funding", "potential": "medium", "requirement": "loyal fanbase"}
                ])
        
        elif platform.lower() == "instagram":
            options.extend([
                {"strategy": "Sponsored Posts", "potential": "high", "requirement": "10k+ followers"},
                {"strategy": "Affiliate Marketing", "potential": "medium", "requirement": "engaged audience"},
                {"strategy": "Product Sales", "potential": "high", "requirement": "business account"}
            ])
        
        elif platform.lower() == "tiktok":
            options.extend([
                {"strategy": "Creator Fund", "potential": "medium", "requirement": "10k+ followers"},
                {"strategy": "Live Gifts", "potential": "medium", "requirement": "live streaming"},
                {"strategy": "Brand Partnerships", "potential": "high", "requirement": "viral content"}
            ])
        
        return options
    
    def _identify_optimization_opportunities(self, content: str) -> List[str]:
        """Identify opportunities to optimize content for monetization."""
        
        opportunities = []
        
        # Call-to-action opportunities
        if "subscribe" not in content.lower():
            opportunities.append("Add subscription call-to-action")
        
        if "like" not in content.lower():
            opportunities.append("Include engagement prompts (like, share)")
        
        # Commercial opportunities
        if "link" not in content.lower():
            opportunities.append("Consider adding relevant affiliate links")
        
        # Content expansion opportunities
        word_count = len(content.split())
        if word_count < 50:
            opportunities.append("Expand content for better monetization potential")
        
        return opportunities
    
    def _generate_platform_advice(
        self, 
        platforms: List[str], 
        content_type: ContentType
    ) -> Dict[str, List[str]]:
        """Generate platform-specific monetization advice."""
        
        advice = {}
        
        for platform in platforms:
            platform_advice = []
            
            if platform.lower() == "youtube" and content_type == ContentType.VIDEO:
                platform_advice.extend([
                    "Optimize for 10+ minute videos for mid-roll ads",
                    "Create compelling thumbnails for higher CTR",
                    "Use trending keywords in titles and descriptions",
                    "Engage with comments to boost algorithm ranking"
                ])
            
            elif platform.lower() == "spotify" and content_type == ContentType.MUSIC:
                platform_advice.extend([
                    "Submit to playlist curators for increased exposure",
                    "Optimize metadata with relevant genres and moods",
                    "Release consistently to maintain algorithm favor",
                    "Collaborate with other artists for cross-promotion"
                ])
            
            elif platform.lower() == "instagram":
                platform_advice.extend([
                    "Post during peak engagement hours",
                    "Use relevant hashtags but avoid banned ones",
                    "Create story highlights for important content",
                    "Engage with your audience through comments and DMs"
                ])
            
            advice[platform] = platform_advice
        
        return advice
    
    def _estimate_potential_earnings(
        self, 
        content: str, 
        content_type: ContentType, 
        platforms: List[str]
    ) -> Dict[str, Dict[str, float]]:
        """Estimate potential earnings by platform."""
        
        earnings_estimates = {}
        
        # Base earnings rates (per 1000 views/streams)
        base_rates = {
            "youtube": {"video": 2.0, "music": 1.0},
            "spotify": {"music": 4.0},
            "instagram": {"image": 0.5, "video": 1.0},
            "tiktok": {"video": 0.3}
        }
        
        for platform in platforms:
            if platform.lower() in base_rates:
                platform_rates = base_rates[platform.lower()]
                content_key = content_type.value
                
                if content_key in platform_rates:
                    base_rate = platform_rates[content_key]
                    
                    # Estimate different scenarios
                    earnings_estimates[platform] = {
                        "conservative": base_rate * 1000,      # 1M views
                        "moderate": base_rate * 5000,         # 5M views
                        "optimistic": base_rate * 10000       # 10M views
                    }
        
        return earnings_estimates
    
    async def _predict_performance(
        self,
        request: ContentOptimizationRequest,
        metrics: OptimizationMetrics
    ) -> Dict[str, float]:
        """Predict content performance across different metrics."""
        
        predictions = {}
        
        # Platform-specific performance predictions
        for platform in request.target_platforms:
            platform_score = metrics.platform_compliance.get(platform, 0.8)
            
            # Base performance calculation
            base_performance = (
                metrics.engagement_score * 0.4 +
                metrics.quality_score * 0.3 +
                platform_score * 0.3
            )
            
            # Platform-specific adjustments
            if platform == 'youtube':
                predictions[f'{platform}_views'] = base_performance * 10000
                predictions[f'{platform}_watch_time'] = base_performance * 0.6
            elif platform == 'instagram':
                predictions[f'{platform}_likes'] = base_performance * 1000
                predictions[f'{platform}_reach'] = base_performance * 5000
            elif platform == 'tiktok':
                predictions[f'{platform}_views'] = base_performance * 50000
                predictions[f'{platform}_shares'] = base_performance * 100
            elif platform == 'spotify':
                predictions[f'{platform}_streams'] = base_performance * 1000
                predictions[f'{platform}_saves'] = base_performance * 50
        
        # Overall performance metrics
        predictions['overall_engagement'] = metrics.engagement_score
        predictions['monetization_score'] = metrics.monetization_potential
        predictions['viral_probability'] = metrics.viral_potential
        
        return predictions


class ContentOptimizer:
    """
    Main content optimizer class that provides high-level optimization services
    for creators and influencers.
    """
    
    def __init__(self):
        """Initialize the content optimizer."""
        self.engine = OptimizationEngine()
        self.optimization_history = {}
        logger.info("Content optimizer initialized")
    
    async def optimize_for_platforms(
        self,
        content_id: str,
        content_type: ContentType,
        content_data: Union[str, bytes, Dict[str, Any]],
        target_platforms: List[str],
        optimization_level: OptimizationLevel = OptimizationLevel.ADVANCED
    ) -> OptimizationResult:
        """
        Optimize content for specific platforms.
        
        Args:
            content_id: Unique identifier for the content
            content_type: Type of content being optimized
            content_data: The actual content data
            target_platforms: List of target platforms
            optimization_level: Level of optimization to apply
            
        Returns:
            OptimizationResult: Comprehensive optimization results
        """
        request = ContentOptimizationRequest(
            content_id=content_id,
            content_type=content_type,
            content_data=content_data,
            target_platforms=target_platforms,
            optimization_level=optimization_level
        )
        
        result = await self.engine.optimize_content(request)
        
        # Store optimization history
        self.optimization_history[content_id] = result
        
        return result
    
    async def get_optimization_suggestions(
        self,
        content_type: ContentType,
        target_platforms: List[str]
    ) -> List[Dict[str, Any]]:
        """Get general optimization suggestions for content type and platforms."""
        
        suggestions = []
        
        # Platform-specific suggestions
        for platform in target_platforms:
            platform_suggestions = self._get_platform_suggestions(platform, content_type)
            suggestions.extend(platform_suggestions)
        
        # Content type specific suggestions
        content_suggestions = self._get_content_type_suggestions(content_type)
        suggestions.extend(content_suggestions)
        
        return suggestions
    
    def _get_platform_suggestions(self, platform: str, content_type: ContentType) -> List[Dict[str, Any]]:
        """Get platform-specific optimization suggestions."""
        
        suggestions = []
        
        if platform == 'youtube':
            suggestions.extend([
                {
                    'category': 'engagement',
                    'title': 'Optimize Video Title',
                    'description': 'Use compelling titles with keywords in the first 60 characters',
                    'impact': 0.2,
                    'priority': 'high'
                },
                {
                    'category': 'seo',
                    'title': 'Add Custom Thumbnail',
                    'description': 'Create eye-catching thumbnails with high contrast and clear text',
                    'impact': 0.15,
                    'priority': 'high'
                }
            ])
        
        elif platform == 'instagram':
            suggestions.extend([
                {
                    'category': 'engagement',
                    'title': 'Use Relevant Hashtags',
                    'description': 'Include 5-10 relevant hashtags with mix of popular and niche tags',
                    'impact': 0.25,
                    'priority': 'high'
                },
                {
                    'category': 'quality',
                    'title': 'Post High-Quality Images',
                    'description': 'Use images with resolution of at least 1080x1080 pixels',
                    'impact': 0.1,
                    'priority': 'medium'
                }
            ])
        
        return suggestions
    
    def _get_content_type_suggestions(self, content_type: ContentType) -> List[Dict[str, Any]]:
        """Get content type specific suggestions."""
        
        suggestions = []
        
        if content_type == ContentType.MUSIC:
            suggestions.extend([
                {
                    'category': 'quality',
                    'title': 'Audio Quality Optimization',
                    'description': 'Ensure audio is mastered at -14 LUFS for streaming platforms',
                    'impact': 0.2,
                    'priority': 'high'
                },
                {
                    'category': 'monetization',
                    'title': 'Add Metadata',
                    'description': 'Include complete metadata with genre, mood, and instrument tags',
                    'impact': 0.15,
                    'priority': 'medium'
                }
            ])
        
        elif content_type == ContentType.VIDEO:
            suggestions.extend([
                {
                    'category': 'engagement',
                    'title': 'Hook in First 15 Seconds',
                    'description': 'Create compelling opening that hooks viewers immediately',
                    'impact': 0.3,
                    'priority': 'high'
                },
                {
                    'category': 'quality',
                    'title': 'Optimize Video Length',
                    'description': 'Keep videos between 8-15 minutes for optimal retention',
                    'impact': 0.15,
                    'priority': 'medium'
                }
            ])
        
        return suggestions
    
    async def analyze_competitor_content(
        self,
        competitor_content: List[Dict[str, Any]],
        content_type: ContentType
    ) -> Dict[str, Any]:
        """Analyze competitor content to identify optimization opportunities."""
        
        analysis = {
            'average_engagement': 0.0,
            'common_themes': [],
            'successful_strategies': [],
            'opportunities': []
        }
        
        if not competitor_content:
            return analysis
        
        # Calculate average engagement
        total_engagement = sum(
            content.get('engagement_score', 0) for content in competitor_content
        )
        analysis['average_engagement'] = total_engagement / len(competitor_content)
        
        # Identify common themes (simplified implementation)
        all_tags = []
        for content in competitor_content:
            tags = content.get('tags', [])
            all_tags.extend(tags)
        
        # Count tag frequency
        tag_counts = {}
        for tag in all_tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        # Get most common themes
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
        analysis['common_themes'] = [tag for tag, count in sorted_tags[:10]]
        
        # Identify successful strategies
        high_performing = [
            content for content in competitor_content
            if content.get('engagement_score', 0) > analysis['average_engagement']
        ]
        
        if high_performing:
            strategies = set()
            for content in high_performing:
                content_strategies = content.get('strategies', [])
                strategies.update(content_strategies)
            analysis['successful_strategies'] = list(strategies)
        
        return analysis
    
    async def get_optimization_history(self, content_id: str) -> Optional[OptimizationResult]:
        """Get optimization history for specific content."""



        return self.optimization_history.get(content_id)
    
    async def bulk_optimize(
        self,
        content_items: List[Dict[str, Any]],
        optimization_level: OptimizationLevel = OptimizationLevel.ADVANCED
    ) -> List[OptimizationResult]:
        """Optimize multiple content items in bulk."""
        
        results = []
        
        # Process items in parallel for efficiency
        tasks = []
        for item in content_items:
            request = ContentOptimizationRequest(
                content_id=item['content_id'],
                content_type=ContentType(item['content_type']),
                content_data=item['content_data'],
                target_platforms=item['target_platforms'],
                optimization_level=optimization_level,
                target_audience=item.get('target_audience'),
                brand_guidelines=item.get('brand_guidelines'),
                monetization_goals=item.get('monetization_goals')
            )
            tasks.append(self.engine.optimize_content(request))
        
        # Execute all optimizations concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and log errors
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Failed to optimize content {content_items[i]['content_id']}: {result}")
            else:
                valid_results.append(result)
                # Store in history
                self.optimization_history[result.content_id] = result
        
        return valid_results
