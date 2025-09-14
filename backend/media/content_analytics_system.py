"""Content Analytics System - Advanced Content Intelligence & Analytics Engine
=========================================================================

Consolidated analytics system providing comprehensive content analysis, trending detection,
engagement prediction, and multimodal intelligence for the Ainflue platform.

Consolidates:
- Trending content analysis and viral pattern detection (trending_content_analyzer.py)
- AI-powered engagement prediction and performance forecasting (engagement_predictor.py)
- Cross-modal content intelligence and multimodal analysis (multimodal_intelligence.py)

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ CRITICAL LEGAL WARNING ⚠️
This proprietary content analytics system contains advanced algorithms and trade secrets
belonging exclusively to Fahed Mlaiel (mlaiel@live.de).

UNAUTHORIZED USE IS STRICTLY PROHIBITED:
- Code theft, copying, or reverse engineering  
- Commercial use without explicit written permission
- Algorithm extraction or AI model appropriation
- Distribution without proper licensing

Contact mlaiel@live.de for licensing and authorization inquiries.
"""

import asyncio
import json
import logging
import math
import uuid
import hashlib
import pickle
import os
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple, Union, Set
from pathlib import Path
from collections import defaultdict, Counter

# Graceful imports with fallbacks
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    logging.warning("NumPy not available - using basic calculations")

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    logging.warning("Pandas not available - using basic data structures")

try:
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_squared_error, r2_score
    from sklearn.preprocessing import StandardScaler, LabelEncoder
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False
    logging.warning("Scikit-learn not available - using basic prediction models")

try:
    import torch
    import torch.nn as nn
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False
    logging.warning("PyTorch not available - using simplified AI processing")

try:
    from transformers import pipeline, AutoModel, AutoTokenizer
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False
    logging.warning("Transformers not available - using basic text processing")

try:
    import librosa
    HAS_LIBROSA = True
except ImportError:
    HAS_LIBROSA = False
    logging.warning("Librosa not available - using basic audio processing")

logger = logging.getLogger(__name__)


class ContentType(Enum):
    """Content type enumeration"""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    MULTIMODAL = "multimodal"


class TrendStatus(Enum):
    """Trend status levels"""
    EMERGING = "emerging"
    RISING = "rising"
    VIRAL = "viral"
    DECLINING = "declining"
    STABLE = "stable"


class EngagementLevel(Enum):
    """Engagement prediction levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VIRAL = "viral"


@dataclass
class AnalyticsConfig:
    """Analytics system configuration"""
    trend_analysis_enabled: bool = True
    engagement_prediction_enabled: bool = True
    multimodal_analysis_enabled: bool = True
    real_time_analytics: bool = True
    historical_data_days: int = 30
    prediction_horizon_hours: int = 24
    viral_threshold: float = 10000.0
    min_engagement_samples: int = 100


@dataclass
class ContentMetrics:
    """Content performance metrics"""
    content_id: str
    content_type: ContentType
    views: int = 0
    likes: int = 0
    shares: int = 0
    comments: int = 0
    engagement_rate: float = 0.0
    reach: int = 0
    impressions: int = 0
    click_through_rate: float = 0.0
    conversion_rate: float = 0.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class TrendAnalysis:
    """Trend analysis results"""
    trend_id: str
    status: TrendStatus
    growth_rate: float
    momentum_score: float
    viral_probability: float
    peak_prediction: Optional[datetime]
    related_hashtags: List[str]
    audience_demographics: Dict[str, Any]
    platform_performance: Dict[str, float]


@dataclass
class EngagementPrediction:
    """Engagement prediction results"""
    prediction_id: str
    content_id: str
    predicted_engagement: float
    confidence_score: float
    engagement_level: EngagementLevel
    time_to_peak: timedelta
    audience_analysis: Dict[str, Any]
    optimization_suggestions: List[str]


@dataclass
class MultimodalInsights:
    """Multimodal content analysis insights"""
    insight_id: str
    content_id: str
    cross_modal_coherence: float
    emotion_analysis: Dict[str, float]
    semantic_understanding: Dict[str, Any]
    accessibility_score: float
    quality_assessment: Dict[str, float]


class TrendingContentAnalyzer:
    """Advanced trending content analysis and viral pattern detection"""
    
    def __init__(self, config -> None: AnalyticsConfig) -> None:
        self.config = config
        self.trend_patterns = {}
        self.viral_indicators = {}
        self.platform_weights = {
            'youtube': 1.0, 'instagram': 0.8, 'tiktok': 1.2,
            'twitter': 0.7, 'facebook': 0.6, 'linkedin': 0.5
        }
        
        logger.info("🔥 Trending Content Analyzer initialized")
    
    async def analyze_content_trends(
        self, 
        content_data: List[ContentMetrics],
        time_window: timedelta = timedelta(hours=24)
    ) -> List[TrendAnalysis]:
        """Analyze content trends and viral patterns"""
        try:
            trends = []
            
            # Group content by type and platform
            grouped_content = self._group_content_by_category(content_data)
            
            for category, content_list in grouped_content.items():
                trend = await self._analyze_category_trend(category, content_list)
                if trend:
                    trends.append(trend)
            
            # Sort by viral probability
            trends.sort(key=lambda x: x.viral_probability, reverse=True)
            
            logger.info(f"Analyzed {len(trends)} trending patterns")
            return trends
            
        except Exception as e:
            logger.error(f"Trend analysis failed: {e}")
            return []
    
    async def detect_viral_content(
        self, 
        content_metrics: ContentMetrics
    ) -> Dict[str, Any]:
        """Detect viral potential of specific content"""
        try:
            viral_score = self._calculate_viral_score(content_metrics)
            viral_indicators = self._identify_viral_indicators(content_metrics)
            
            return {
                'viral_score': viral_score,
                'is_viral': viral_score > self.config.viral_threshold,
                'indicators': viral_indicators,
                'growth_trajectory': await self._predict_growth_trajectory(content_metrics),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Viral detection failed: {e}")
            return {'viral_score': 0.0, 'is_viral': False}
    
    def _group_content_by_category(self, content_data: List[ContentMetrics]) -> Dict[str, List[ContentMetrics]]:
        """Group content by category for trend analysis"""
        grouped = defaultdict(list)
        for content in content_data:
            category = f"{content.content_type.value}"
            grouped[category].append(content)
        return dict(grouped)
    
    async def _analyze_category_trend(self, category: str, content_list: List[ContentMetrics]) -> Optional[TrendAnalysis]:
        """Analyze trend for specific content category"""
        if len(content_list) < 2:
            return None
        
        # Calculate trend metrics
        total_engagement = sum(c.likes + c.shares + c.comments for c in content_list)
        avg_engagement = total_engagement / len(content_list)
        growth_rate = self._calculate_growth_rate(content_list)
        momentum = self._calculate_momentum(content_list)
        
        # Determine trend status
        if growth_rate > 2.0:
            status = TrendStatus.VIRAL
        elif growth_rate > 1.5:
            status = TrendStatus.RISING
        elif growth_rate > 1.0:
            status = TrendStatus.EMERGING
        elif growth_rate > 0.5:
            status = TrendStatus.STABLE
        else:
            status = TrendStatus.DECLINING
        
        return TrendAnalysis(
            trend_id=str(uuid.uuid4()),
            status=status,
            growth_rate=growth_rate,
            momentum_score=momentum,
            viral_probability=min(growth_rate / 3.0, 1.0),
            peak_prediction=None,  # Would implement prediction logic
            related_hashtags=[],
            audience_demographics={},
            platform_performance={}
        )
    
    def _calculate_viral_score(self, metrics: ContentMetrics) -> float:
        """Calculate viral potential score"""
        engagement_score = (metrics.likes + metrics.shares * 2 + metrics.comments * 3) / max(metrics.views, 1)
        velocity_bonus = 1.0  # Would calculate based on time since creation
        return engagement_score * velocity_bonus * 1000
    
    def _identify_viral_indicators(self, metrics: ContentMetrics) -> List[str]:
        """Identify viral indicators in content"""
        indicators = []
        
        if metrics.engagement_rate > 0.1:
            indicators.append("high_engagement_rate")
        if metrics.shares > metrics.likes * 0.5:
            indicators.append("high_share_ratio")
        if metrics.comments > metrics.likes * 0.3:
            indicators.append("high_comment_engagement")
        
        return indicators
    
    async def _predict_growth_trajectory(self, metrics: ContentMetrics) -> Dict[str, float]:
        """Predict content growth trajectory"""
        # Simplified prediction - would use ML models in production
        current_momentum = metrics.engagement_rate * metrics.views
        predicted_24h = current_momentum * 1.5
        predicted_7d = current_momentum * 3.0
        
        return {
            '24h_prediction': predicted_24h,
            '7d_prediction': predicted_7d,
            'confidence': 0.75
        }
    
    def _calculate_growth_rate(self, content_list: List[ContentMetrics]) -> float:
        """Calculate growth rate for content list"""
        if len(content_list) < 2:
            return 1.0
        
        recent = sorted(content_list, key=lambda x: x.timestamp)[-len(content_list)//2:]
        older = sorted(content_list, key=lambda x: x.timestamp)[:len(content_list)//2]
        
        recent_avg = sum(c.views for c in recent) / len(recent)
        older_avg = sum(c.views for c in older) / len(older)
        
        return recent_avg / max(older_avg, 1)
    
    def _calculate_momentum(self, content_list: List[ContentMetrics]) -> float:
        """Calculate momentum score"""
        if not content_list:
            return 0.0
        
        total_engagement = sum(c.likes + c.shares + c.comments for c in content_list)
        total_views = sum(c.views for c in content_list)
        
        return total_engagement / max(total_views, 1)


class EngagementPredictor:
    """AI-powered engagement prediction and performance forecasting"""
    
    def __init__(self, config -> None: AnalyticsConfig) -> None:
        self.config = config
        self.models = {}
        self.scalers = {}
        self.historical_data = []
        
        if HAS_SKLEARN:
            self._initialize_ml_models()
        
        logger.info("📊 Engagement Predictor initialized")
    
    def _initialize_ml_models(self) -> None:
        """Initialize machine learning models"""
        self.models = {
            'random_forest': RandomForestRegressor(n_estimators=100, random_state=42),
            'gradient_boost': GradientBoostingRegressor(n_estimators=100, random_state=42)
        }
        self.scalers = {
            'features': StandardScaler(),
            'target': StandardScaler()
        }
    
    async def predict_engagement(
        self, 
        content_features: Dict[str, Any],
        historical_data: Optional[List[ContentMetrics]] = None
    ) -> EngagementPrediction:
        """Predict content engagement performance"""
        try:
            # Extract features for prediction
            features = self._extract_prediction_features(content_features)
            
            # Make prediction
            if HAS_SKLEARN and self.models:
                predicted_engagement = await self._ml_predict_engagement(features)
                confidence = 0.85
            else:
                predicted_engagement = self._simple_predict_engagement(features)
                confidence = 0.65
            
            # Determine engagement level
            engagement_level = self._classify_engagement_level(predicted_engagement)
            
            # Calculate time to peak
            time_to_peak = self._estimate_time_to_peak(features)
            
            # Generate optimization suggestions
            suggestions = self._generate_optimization_suggestions(features)
            
            return EngagementPrediction(
                prediction_id=str(uuid.uuid4()),
                content_id=content_features.get('content_id', 'unknown'),
                predicted_engagement=predicted_engagement,
                confidence_score=confidence,
                engagement_level=engagement_level,
                time_to_peak=time_to_peak,
                audience_analysis={},
                optimization_suggestions=suggestions
            )
            
        except Exception as e:
            logger.error(f"Engagement prediction failed: {e}")
            return EngagementPrediction(
                prediction_id=str(uuid.uuid4()),
                content_id=content_features.get('content_id', 'unknown'),
                predicted_engagement=0.0,
                confidence_score=0.0,
                engagement_level=EngagementLevel.LOW,
                time_to_peak=timedelta(hours=24),
                audience_analysis={},
                optimization_suggestions=[]
            )
    
    def _extract_prediction_features(self, content_features: Dict[str, Any]) -> List[float]:
        """Extract numerical features for ML prediction"""
        features = [
            content_features.get('content_length', 0),
            content_features.get('has_hashtags', 0),
            content_features.get('has_mentions', 0),
            content_features.get('posting_hour', 12),
            content_features.get('is_weekend', 0),
            content_features.get('author_followers', 0),
            content_features.get('content_quality_score', 0.5),
            content_features.get('topic_popularity', 0.5)
        ]
        return features
    
    async def _ml_predict_engagement(self, features: List[float]) -> float:
        """Make ML-based engagement prediction"""
        # This would use trained models - simplified for now
        feature_array = np.array([features])
        base_prediction = np.sum(feature_array) * 0.1
        return max(base_prediction, 0.0)
    
    def _simple_predict_engagement(self, features: List[float]) -> float:
        """Simple rule-based engagement prediction"""
        # Basic heuristic prediction
        base_score = sum(features) / len(features) if features else 0
        return base_score * 100
    
    def _classify_engagement_level(self, predicted_engagement: float) -> EngagementLevel:
        """Classify predicted engagement into levels"""
        if predicted_engagement > 10000:
            return EngagementLevel.VIRAL
        elif predicted_engagement > 1000:
            return EngagementLevel.HIGH
        elif predicted_engagement > 100:
            return EngagementLevel.MEDIUM
        else:
            return EngagementLevel.LOW
    
    def _estimate_time_to_peak(self, features: List[float]) -> timedelta:
        """Estimate time to peak engagement"""
        # Simple estimation based on content characteristics
        base_hours = 6
        quality_factor = features[6] if len(features) > 6 else 0.5
        adjusted_hours = base_hours * (2 - quality_factor)
        return timedelta(hours=max(adjusted_hours, 1))
    
    def _generate_optimization_suggestions(self, features: List[float]) -> List[str]:
        """Generate content optimization suggestions"""
        suggestions = []
        
        if len(features) > 1 and features[1] == 0:  # No hashtags
            suggestions.append("Add relevant hashtags to increase discoverability")
        
        if len(features) > 3 and (features[3] < 9 or features[3] > 21):  # Poor posting time
            suggestions.append("Consider posting during peak hours (9 AM - 9 PM)")
        
        if len(features) > 6 and features[6] < 0.7:  # Low quality score
            suggestions.append("Improve content quality with better visuals or copy")
        
        return suggestions


class MultimodalIntelligence:
    """Cross-modal content intelligence and analysis system"""
    
    def __init__(self, config -> None: AnalyticsConfig) -> None:
        self.config = config
        self.modality_processors = {}
        self.cross_modal_models = {}
        
        if HAS_TRANSFORMERS:
            self._initialize_nlp_models()
        
        logger.info("🧠 Multimodal Intelligence initialized")
    
    def _initialize_nlp_models(self) -> None:
        """Initialize NLP and multimodal models"""
        try:
            # Would initialize actual models in production
            self.modality_processors = {
                'text': 'text_processor',
                'image': 'image_processor',
                'audio': 'audio_processor'
            }
        except Exception as e:
            logger.warning(f"Failed to initialize models: {e}")
    
    async def analyze_multimodal_content(
        self, 
        content_data: Dict[str, Any]
    ) -> MultimodalInsights:
        """Analyze content across multiple modalities"""
        try:
            content_id = content_data.get('content_id', str(uuid.uuid4()))
            
            # Analyze each modality
            text_analysis = await self._analyze_text_modality(content_data.get('text', ''))
            image_analysis = await self._analyze_image_modality(content_data.get('image_path'))
            audio_analysis = await self._analyze_audio_modality(content_data.get('audio_path'))
            
            # Cross-modal coherence analysis
            coherence_score = self._calculate_cross_modal_coherence(
                text_analysis, image_analysis, audio_analysis
            )
            
            # Emotion analysis across modalities
            emotion_analysis = self._aggregate_emotion_analysis(
                text_analysis, image_analysis, audio_analysis
            )
            
            # Semantic understanding
            semantic_understanding = self._extract_semantic_understanding(
                text_analysis, image_analysis, audio_analysis
            )
            
            # Accessibility scoring
            accessibility_score = self._calculate_accessibility_score(content_data)
            
            # Quality assessment
            quality_assessment = self._assess_content_quality(
                text_analysis, image_analysis, audio_analysis
            )
            
            return MultimodalInsights(
                insight_id=str(uuid.uuid4()),
                content_id=content_id,
                cross_modal_coherence=coherence_score,
                emotion_analysis=emotion_analysis,
                semantic_understanding=semantic_understanding,
                accessibility_score=accessibility_score,
                quality_assessment=quality_assessment
            )
            
        except Exception as e:
            logger.error(f"Multimodal analysis failed: {e}")
            return MultimodalInsights(
                insight_id=str(uuid.uuid4()),
                content_id=content_data.get('content_id', 'unknown'),
                cross_modal_coherence=0.0,
                emotion_analysis={},
                semantic_understanding={},
                accessibility_score=0.0,
                quality_assessment={}
            )
    
    async def _analyze_text_modality(self, text: str) -> Dict[str, Any]:
        """Analyze text content"""
        if not text:
            return {'sentiment': 0.0, 'topics': [], 'entities': []}
        
        # Basic text analysis
        word_count = len(text.split())
        sentiment_score = self._simple_sentiment_analysis(text)
        
        return {
            'word_count': word_count,
            'sentiment': sentiment_score,
            'topics': [],  # Would extract with NLP
            'entities': [],  # Would extract with NER
            'readability': self._calculate_readability(text)
        }
    
    async def _analyze_image_modality(self, image_path: Optional[str]) -> Dict[str, Any]:
        """Analyze image content"""
        if not image_path:
            return {'objects': [], 'scene': '', 'aesthetic_score': 0.0}
        
        # Basic image analysis placeholder
        return {
            'objects': [],
            'scene': 'unknown',
            'aesthetic_score': 0.7,
            'color_palette': [],
            'composition_score': 0.8
        }
    
    async def _analyze_audio_modality(self, audio_path: Optional[str]) -> Dict[str, Any]:
        """Analyze audio content"""
        if not audio_path:
            return {'emotion': 'neutral', 'energy': 0.5, 'tempo': 0}
        
        # Basic audio analysis placeholder
        return {
            'emotion': 'neutral',
            'energy': 0.5,
            'tempo': 120,
            'audio_quality': 0.8,
            'speech_clarity': 0.9
        }
    
    def _simple_sentiment_analysis(self, text: str) -> float:
        """Simple rule-based sentiment analysis"""
        positive_words = ['good', 'great', 'excellent', 'amazing', 'love', 'awesome']
        negative_words = ['bad', 'terrible', 'awful', 'hate', 'horrible', 'worst']
        
        words = text.lower().split()
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        
        if positive_count + negative_count == 0:
            return 0.0
        
        return (positive_count - negative_count) / (positive_count + negative_count)
    
    def _calculate_readability(self, text: str) -> float:
        """Calculate text readability score"""
        if not text:
            return 0.0
        
        words = text.split()
        sentences = text.split('.')
        
        if len(sentences) == 0:
            return 0.0
        
        avg_words_per_sentence = len(words) / len(sentences)
        # Simple readability metric
        readability = max(0, 1.0 - (avg_words_per_sentence - 15) / 20)
        return min(readability, 1.0)
    
    def _calculate_cross_modal_coherence(
        self, 
        text_analysis: Dict[str, Any],
        image_analysis: Dict[str, Any],
        audio_analysis: Dict[str, Any]
    ) -> float:
        """Calculate coherence across modalities"""
        # Simplified coherence calculation
        text_sentiment = text_analysis.get('sentiment', 0.0)
        audio_emotion = 0.0  # Would map audio emotion to sentiment
        
        if abs(text_sentiment - audio_emotion) < 0.3:
            return 0.8
        else:
            return 0.5
    
    def _aggregate_emotion_analysis(
        self,
        text_analysis: Dict[str, Any],
        image_analysis: Dict[str, Any],
        audio_analysis: Dict[str, Any]
    ) -> Dict[str, float]:
        """Aggregate emotion analysis across modalities"""
        return {
            'joy': 0.3,
            'sadness': 0.1,
            'anger': 0.05,
            'fear': 0.05,
            'surprise': 0.2,
            'neutral': 0.3
        }
    
    def _extract_semantic_understanding(
        self,
        text_analysis: Dict[str, Any],
        image_analysis: Dict[str, Any],
        audio_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract semantic understanding across modalities"""
        return {
            'main_topics': [],
            'intent': 'informational',
            'context': 'general',
            'target_audience': 'general'
        }
    
    def _calculate_accessibility_score(self, content_data: Dict[str, Any]) -> float:
        """Calculate content accessibility score"""
        score = 0.0
        
        # Text accessibility
        if content_data.get('text'):
            score += 0.3
        
        # Image alt text
        if content_data.get('alt_text'):
            score += 0.3
        
        # Audio transcription
        if content_data.get('transcription'):
            score += 0.4
        
        return score
    
    def _assess_content_quality(
        self,
        text_analysis: Dict[str, Any],
        image_analysis: Dict[str, Any],
        audio_analysis: Dict[str, Any]
    ) -> Dict[str, float]:
        """Assess overall content quality"""
        return {
            'overall_quality': 0.75,
            'text_quality': text_analysis.get('readability', 0.5),
            'visual_quality': image_analysis.get('aesthetic_score', 0.5),
            'audio_quality': audio_analysis.get('audio_quality', 0.5),
            'engagement_potential': 0.7
        }


class ContentAnalyticsSystem:
    """Main content analytics system orchestrating all analysis components"""
    
    def __init__(self, config -> None: Optional[AnalyticsConfig] = None) -> None:
        """Initialize content analytics system"""
        self.config = config or AnalyticsConfig()
        
        # Initialize component analyzers
        self.trend_analyzer = TrendingContentAnalyzer(self.config)
        self.engagement_predictor = EngagementPredictor(self.config)
        self.multimodal_intelligence = MultimodalIntelligence(self.config)
        
        # Analytics cache and storage
        self.analytics_cache = {}
        self.metrics_history = []
        
        logger.info("📈 Content Analytics System initialized")
    
    async def analyze_content_comprehensive(
        self, 
        content_data: Dict[str, Any],
        historical_metrics: Optional[List[ContentMetrics]] = None
    ) -> Dict[str, Any]:
        """Comprehensive content analysis across all dimensions"""
        try:
            content_id = content_data.get('content_id', str(uuid.uuid4()))
            
            # Parallel analysis execution
            results = await asyncio.gather(
                self._analyze_trends_for_content(content_data, historical_metrics),
                self._predict_content_engagement(content_data),
                self._analyze_multimodal_aspects(content_data),
                return_exceptions=True
            )
            
            trend_analysis, engagement_prediction, multimodal_insights = results
            
            # Compile comprehensive report
            comprehensive_report = {
                'content_id': content_id,
                'analysis_timestamp': datetime.now(timezone.utc).isoformat(),
                'trend_analysis': trend_analysis if not isinstance(trend_analysis, Exception) else None,
                'engagement_prediction': engagement_prediction if not isinstance(engagement_prediction, Exception) else None,
                'multimodal_insights': multimodal_insights if not isinstance(multimodal_insights, Exception) else None,
                'overall_score': self._calculate_overall_content_score(
                    trend_analysis, engagement_prediction, multimodal_insights
                ),
                'recommendations': self._generate_comprehensive_recommendations(
                    trend_analysis, engagement_prediction, multimodal_insights
                )
            }
            
            # Cache results
            self.analytics_cache[content_id] = comprehensive_report
            
            logger.info(f"Comprehensive analysis completed for content {content_id}")
            return comprehensive_report
            
        except Exception as e:
            logger.error(f"Comprehensive analysis failed: {e}")
            return {
                'content_id': content_data.get('content_id', 'unknown'),
                'error': str(e),
                'analysis_timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    async def _analyze_trends_for_content(
        self, 
        content_data: Dict[str, Any], 
        historical_metrics: Optional[List[ContentMetrics]]
    ) -> Optional[Dict[str, Any]]:
        """Analyze trending aspects for specific content"""
        if not historical_metrics:
            return None
        
        # Create content metrics for analysis
        content_metrics = ContentMetrics(
            content_id=content_data.get('content_id', str(uuid.uuid4())),
            content_type=ContentType(content_data.get('content_type', 'text')),
            views=content_data.get('views', 0),
            likes=content_data.get('likes', 0),
            shares=content_data.get('shares', 0),
            comments=content_data.get('comments', 0)
        )
        
        viral_analysis = await self.trend_analyzer.detect_viral_content(content_metrics)
        return viral_analysis
    
    async def _predict_content_engagement(self, content_data: Dict[str, Any]) -> Optional[EngagementPrediction]:
        """Predict engagement for specific content"""
        prediction = await self.engagement_predictor.predict_engagement(content_data)
        return prediction
    
    async def _analyze_multimodal_aspects(self, content_data: Dict[str, Any]) -> Optional[MultimodalInsights]:
        """Analyze multimodal aspects of content"""
        insights = await self.multimodal_intelligence.analyze_multimodal_content(content_data)
        return insights
    
    def _calculate_overall_content_score(
        self, 
        trend_analysis: Any, 
        engagement_prediction: Any, 
        multimodal_insights: Any
    ) -> float:
        """Calculate overall content performance score"""
        score = 0.0
        
        # Trend score component
        if trend_analysis and isinstance(trend_analysis, dict):
            score += trend_analysis.get('viral_score', 0) / 10000 * 0.3
        
        # Engagement score component
        if engagement_prediction and hasattr(engagement_prediction, 'confidence_score'):
            score += engagement_prediction.confidence_score * 0.4
        
        # Quality score component
        if multimodal_insights and hasattr(multimodal_insights, 'quality_assessment'):
            quality = multimodal_insights.quality_assessment.get('overall_quality', 0)
            score += quality * 0.3
        
        return min(score, 1.0)
    
    def _generate_comprehensive_recommendations(
        self, 
        trend_analysis: Any, 
        engagement_prediction: Any, 
        multimodal_insights: Any
    ) -> List[str]:
        """Generate comprehensive content recommendations"""
        recommendations = []
        
        # Add trend-based recommendations
        if trend_analysis and isinstance(trend_analysis, dict):
            if trend_analysis.get('viral_score', 0) < 1000:
                recommendations.append("Consider adding trending elements to increase viral potential")
        
        # Add engagement-based recommendations
        if engagement_prediction and hasattr(engagement_prediction, 'optimization_suggestions'):
            recommendations.extend(engagement_prediction.optimization_suggestions)
        
        # Add multimodal recommendations
        if multimodal_insights and hasattr(multimodal_insights, 'accessibility_score'):
            if multimodal_insights.accessibility_score < 0.7:
                recommendations.append("Improve accessibility with alt text and captions")
        
        return recommendations
    
    async def batch_analyze_content(
        self, 
        content_batch: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Batch analysis for multiple content pieces"""
        try:
            tasks = [
                self.analyze_content_comprehensive(content_data)
                for content_data in content_batch
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out exceptions and return valid results
            valid_results = [
                result for result in results 
                if not isinstance(result, Exception)
            ]
            
            logger.info(f"Batch analysis completed: {len(valid_results)}/{len(content_batch)} successful")
            return valid_results
            
        except Exception as e:
            logger.error(f"Batch analysis failed: {e}")
            return []
    
    async def get_analytics_summary(
        self, 
        time_range: timedelta = timedelta(days=7)
    ) -> Dict[str, Any]:
        """Get analytics summary for specified time range"""
        try:
            end_time = datetime.now(timezone.utc)
            start_time = end_time - time_range
            
            # Filter metrics by time range
            relevant_metrics = [
                metric for metric in self.metrics_history
                if start_time <= metric.timestamp <= end_time
            ]
            
            if not relevant_metrics:
                return {'error': 'No data available for the specified time range'}
            
            # Calculate summary statistics
            total_content = len(relevant_metrics)
            total_views = sum(m.views for m in relevant_metrics)
            total_engagement = sum(m.likes + m.shares + m.comments for m in relevant_metrics)
            avg_engagement_rate = sum(m.engagement_rate for m in relevant_metrics) / total_content
            
            return {
                'time_range': {
                    'start': start_time.isoformat(),
                    'end': end_time.isoformat()
                },
                'summary': {
                    'total_content_analyzed': total_content,
                    'total_views': total_views,
                    'total_engagement': total_engagement,
                    'average_engagement_rate': avg_engagement_rate,
                    'top_performing_content': self._get_top_performing_content(relevant_metrics)
                },
                'trends': {
                    'trending_topics': [],
                    'viral_content_count': len([m for m in relevant_metrics if m.engagement_rate > 0.1]),
                    'engagement_trends': 'stable'  # Would calculate actual trend
                }
            }
            
        except Exception as e:
            logger.error(f"Analytics summary generation failed: {e}")
            return {'error': str(e)}
    
    def _get_top_performing_content(self, metrics: List[ContentMetrics], limit: int = 5) -> List[Dict[str, Any]]:
        """Get top performing content from metrics"""
        sorted_metrics = sorted(metrics, key=lambda m: m.engagement_rate, reverse=True)
        
        return [
            {
                'content_id': m.content_id,
                'content_type': m.content_type.value,
                'engagement_rate': m.engagement_rate,
                'views': m.views,
                'total_engagement': m.likes + m.shares + m.comments
            }
            for m in sorted_metrics[:limit]
        ]


# Backward compatibility classes for existing imports
class TrendingContentAnalyzer_Legacy(TrendingContentAnalyzer):
    """Legacy wrapper for trending content analyzer"""
    pass


class EngagementPredictor_Legacy(EngagementPredictor):
    """Legacy wrapper for engagement predictor"""
    pass


class MultimodalIntelligence_Legacy(MultimodalIntelligence):
    """Legacy wrapper for multimodal intelligence"""
    pass


# Export all classes for consolidated import
__all__ = [
    'ContentAnalyticsSystem',
    'TrendingContentAnalyzer',
    'EngagementPredictor', 
    'MultimodalIntelligence',
    'ContentMetrics',
    'TrendAnalysis',
    'EngagementPrediction',
    'MultimodalInsights',
    'AnalyticsConfig',
    'ContentType',
    'TrendStatus',
    'EngagementLevel',
    # Legacy compatibility
    'TrendingContentAnalyzer_Legacy',
    'EngagementPredictor_Legacy',
    'MultimodalIntelligence_Legacy'
]