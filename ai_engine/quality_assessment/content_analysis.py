"""Content Analysis Module

Advanced multi-dimensional content analysis for creators and influencers.
Provides comprehensive content intelligence and performance insights.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING ⚠️
This software and all associated concepts, algorithms, and implementations are the exclusive 
intellectual property of Fahed Mlaiel (mlaiel@live.de). Any unauthorized use, reproduction, 
distribution, modification, or appropriation of this code, in whole or in part, without 
explicit written permission from Fahed Mlaiel is strictly prohibited and will be prosecuted 
to the full extent of the law.
"""
import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import numpy as np
from collections import defaultdict, Counter

from ..core.base_models import BaseAIModel, ModelConfig
from ..core.exceptions import QualityCheckError, ContentValidationError
from ..core.performance import PerformanceMonitor, monitor_performance
from ..core.metrics import MetricsCollector, metrics_collector

logger = logging.getLogger(__name__)


class ContentCategory(Enum):
    """Content category classifications"""    ENTERTAINMENT = "entertainment"
    EDUCATION = "education"
    LIFESTYLE = "lifestyle"
    TECHNOLOGY = "technology"
    BUSINESS = "business"
    HEALTH_FITNESS = "health_fitness"
    TRAVEL = "travel"
    FOOD = "food"
    FASHION = "fashion"
    MUSIC = "music"
    SPORTS = "sports"
    NEWS = "news"
    GAMING = "gaming"
    ART_DESIGN = "art_design"
    PERSONAL_DEVELOPMENT = "personal_development"


class ContentFormat(Enum):
    """Content format types"""    VIDEO_SHORT = "video_short"  # < 60 seconds
    VIDEO_MEDIUM = "video_medium"  # 1-10 minutes
    VIDEO_LONG = "video_long"  # > 10 minutes
    AUDIO_PODCAST = "audio_podcast"
    AUDIO_MUSIC = "audio_music"
    IMAGE_PHOTO = "image_photo"
    IMAGE_GRAPHIC = "image_graphic"
    TEXT_ARTICLE = "text_article"
    TEXT_POST = "text_post"
    MIXED_MEDIA = "mixed_media"


class AudienceSegment(Enum):
    """Target audience segments"""    GEN_Z = "gen_z"  # 16-24
    MILLENNIALS = "millennials"  # 25-40
    GEN_X = "gen_x"  # 41-56
    BOOMERS = "boomers"  # 57+
    TEENS = "teens"  # 13-17
    PROFESSIONALS = "professionals"
    STUDENTS = "students"
    PARENTS = "parents"
    ENTREPRENEURS = "entrepreneurs"


class EngagementType(Enum):
    """Types of engagement patterns"""    VIRAL = "viral"
    EDUCATIONAL = "educational"
    INSPIRATIONAL = "inspirational"
    CONTROVERSIAL = "controversial"
    ENTERTAINING = "entertaining"
    INFORMATIONAL = "informational"
    COMMERCIAL = "commercial"
    COMMUNITY_BUILDING = "community_building"


@dataclass
class TrendAnalysis:
    """Content trend analysis results"""    trending_topics: List[str] = field(default_factory=list)
    hashtag_relevance: Dict[str, float] = field(default_factory=dict)
    seasonal_relevance: float = field(default=0.0)
    timing_score: float = field(default=50.0)
    trend_alignment: float = field(default=50.0)
    
    # Virality indicators
    viral_elements: List[str] = field(default_factory=list)
    meme_potential: float = field(default=30.0)
    shareability_factors: List[str] = field(default_factory=list)


@dataclass
class AudienceAnalysis:
    """Target audience analysis"""    primary_audience: AudienceSegment = field(default=AudienceSegment.MILLENNIALS)
    secondary_audiences: List[AudienceSegment] = field(default_factory=list)
    audience_match_score: float = field(default=50.0)
    
    # Demographic insights
    age_range: Tuple[int, int] = field(default=(18, 65))
    gender_distribution: Dict[str, float] = field(default_factory=dict)
    geographic_appeal: List[str] = field(default_factory=list)
    
    # Behavioral insights
    consumption_patterns: Dict[str, float] = field(default_factory=dict)
    engagement_preferences: List[str] = field(default_factory=list)
    platform_affinity: Dict[str, float] = field(default_factory=dict)


@dataclass
class CompetitorAnalysis:
    """Competitive landscape analysis"""    content_saturation: float = field(default=50.0)
    differentiation_score: float = field(default=50.0)
    competitive_advantage: List[str] = field(default_factory=list)
    
    # Market positioning
    uniqueness_factors: List[str] = field(default_factory=list)
    market_gap_opportunities: List[str] = field(default_factory=list)
    competitive_threats: List[str] = field(default_factory=list)


@dataclass
class ContentTheme:
    """Content thematic analysis"""    primary_theme: str = field(default="general")
    secondary_themes: List[str] = field(default_factory=list)
    emotional_themes: List[str] = field(default_factory=list)
    
    # Theme scoring
    theme_consistency: float = field(default=50.0)
    theme_relevance: float = field(default=50.0)
    brand_alignment: float = field(default=50.0)


@dataclass
class ContentStructureAnalysis:
    """Content structure and flow analysis"""    narrative_structure: str = field(default="linear")
    pacing_score: float = field(default=50.0)
    attention_retention: float = field(default=50.0)
    
    # Hook analysis
    opening_strength: float = field(default=50.0)
    hook_effectiveness: float = field(default=50.0)
    closing_impact: float = field(default=50.0)
    
    # Flow metrics
    transition_quality: float = field(default=50.0)
    logical_progression: float = field(default=50.0)
    climax_placement: float = field(default=50.0)


@dataclass
class ContentAnalysisProfile:
    """Comprehensive content analysis profile"""    # Classification
    category: ContentCategory = field(default=ContentCategory.ENTERTAINMENT)
    format: ContentFormat = field(default=ContentFormat.MIXED_MEDIA)
    engagement_type: EngagementType = field(default=EngagementType.ENTERTAINING)
    
    # Core analysis components
    trend_analysis: TrendAnalysis = field(default_factory=TrendAnalysis)
    audience_analysis: AudienceAnalysis = field(default_factory=AudienceAnalysis)
    competitor_analysis: CompetitorAnalysis = field(default_factory=CompetitorAnalysis)
    theme_analysis: ContentTheme = field(default_factory=ContentTheme)
    structure_analysis: ContentStructureAnalysis = field(default_factory=ContentStructureAnalysis)
    
    # Performance predictions
    engagement_prediction: float = field(default=50.0)
    reach_potential: float = field(default=50.0)
    conversion_likelihood: float = field(default=30.0)
    brand_impact: float = field(default=50.0)
    
    # Optimization insights
    optimization_score: float = field(default=50.0)
    improvement_areas: List[str] = field(default_factory=list)
    strategic_recommendations: List[str] = field(default_factory=list)
    
    # Overall scoring
    content_intelligence_score: float = field(default=50.0)
    market_readiness: float = field(default=50.0)
    success_probability: float = field(default=50.0)


@dataclass
class ContentAnalysisMetrics:
    """Content analysis metrics container"""    profile: ContentAnalysisProfile = field(default_factory=ContentAnalysisProfile)
    
    # Performance indicators
    viral_potential: float = field(default=30.0)
    monetization_potential: float = field(default=40.0)
    educational_value: float = field(default=50.0)
    entertainment_value: float = field(default=50.0)
    
    # Strategic metrics
    brand_consistency: float = field(default=50.0)
    message_clarity: float = field(default=50.0)
    call_to_action_effectiveness: float = field(default=40.0)
    
    # Risk assessment
    controversy_risk: float = field(default=20.0)
    copyright_risk: float = field(default=10.0)
    platform_compliance: float = field(default=80.0)
    
    # Metadata
    analysis_timestamp: datetime = field(default_factory=datetime.now)
    processing_time: float = field(default=0.0)
    confidence: float = field(default=0.0)


class ContentAnalyzer(BaseAIModel):
    """    Professional Content Analyzer
    
    Provides comprehensive content intelligence for:
    - Content creators and influencers
    - Digital marketing strategists
    - Social media managers
    - Brand content teams
    - Creator economy platforms
    """    
    def __init__(self, config: Optional[ModelConfig] = None):
        """Initialize content analyzer"""        super().__init__(config or ModelConfig(
            model_name="content_analyzer",
            provider="internal",
            version="1.0.0"
        ))
        
        self.performance_monitor = performance_monitor
        self.metrics_collector = metrics_collector
        
        # Content classification models
        self._initialize_classification_models()
        
        # Trend databases (simplified)
        self.trending_topics = {
            'general': ['AI', 'sustainability', 'remote work', 'mental health', 'cryptocurrency'],
            'technology': ['AI', 'blockchain', 'cybersecurity', 'cloud computing', 'IoT'],
            'lifestyle': ['wellness', 'minimalism', 'productivity', 'self-care', 'mindfulness'],
            'business': ['entrepreneurship', 'digital transformation', 'leadership', 'innovation'],
            'entertainment': ['streaming', 'gaming', 'pop culture', 'viral challenges', 'memes']
        }
        
        # Platform-specific insights
        self.platform_insights = {
            'instagram': {
                'optimal_posting_times': [9, 11, 13, 17, 19],
                'preferred_formats': [ContentFormat.IMAGE_PHOTO, ContentFormat.VIDEO_SHORT],
                'engagement_drivers': ['visual_appeal', 'storytelling', 'hashtags']
            },
            'tiktok': {
                'optimal_posting_times': [6, 10, 19, 20],
                'preferred_formats': [ContentFormat.VIDEO_SHORT],
                'engagement_drivers': ['trends', 'music', 'creativity', 'authenticity']
            },
            'youtube': {
                'optimal_posting_times': [14, 15, 16, 17],
                'preferred_formats': [ContentFormat.VIDEO_MEDIUM, ContentFormat.VIDEO_LONG],
                'engagement_drivers': ['value', 'entertainment', 'consistency', 'thumbnails']
            },
            'linkedin': {
                'optimal_posting_times': [8, 12, 17, 18],
                'preferred_formats': [ContentFormat.TEXT_ARTICLE, ContentFormat.TEXT_POST],
                'engagement_drivers': ['expertise', 'insights', 'networking', 'professional_value']
            }
        }
        
        logger.info("Content Analyzer initialized successfully")
    
    def _initialize_classification_models(self):
        """Initialize content classification models"""        try:
            # Category keywords mapping
            self.category_keywords = {
                ContentCategory.ENTERTAINMENT: ['funny', 'comedy', 'music', 'movie', 'celebrity', 'meme'],
                ContentCategory.EDUCATION: ['learn', 'tutorial', 'how-to', 'guide', 'lesson', 'knowledge'],
                ContentCategory.LIFESTYLE: ['life', 'daily', 'routine', 'wellness', 'health', 'fashion'],
                ContentCategory.TECHNOLOGY: ['tech', 'software', 'AI', 'digital', 'innovation', 'gadget'],
                ContentCategory.BUSINESS: ['business', 'entrepreneur', 'marketing', 'finance', 'strategy'],
                ContentCategory.HEALTH_FITNESS: ['fitness', 'workout', 'health', 'nutrition', 'wellness'],
                ContentCategory.TRAVEL: ['travel', 'destination', 'vacation', 'explore', 'adventure'],
                ContentCategory.FOOD: ['food', 'recipe', 'cooking', 'restaurant', 'cuisine', 'chef']
            }
            
            # Audience segment indicators
            self.audience_indicators = {
                AudienceSegment.GEN_Z: ['tiktok', 'viral', 'trend', 'aesthetic', 'authentic', 'social justice'],
                AudienceSegment.MILLENNIALS: ['nostalgia', 'work-life balance', 'experiences', 'brands', 'social media'],
                AudienceSegment.PROFESSIONALS: ['career', 'leadership', 'productivity', 'networking', 'growth'],
                AudienceSegment.STUDENTS: ['study', 'university', 'budget', 'tips', 'future', 'learning']
            }
            
        except Exception as e:
            logger.warning(f"Classification model initialization warning: {str(e)}")
    
    @monitor_performance
    async def analyze_content(
        self,
        content_data: Dict[str, Any],
        analysis_options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """        Comprehensive content analysis
        
        Args:
            content_data: Content information including text, metadata, etc.
            analysis_options: Analysis configuration options
            
        Returns:
            Dict containing complete content analysis
            
        Raises:
            QualityCheckError: If analysis fails
            ContentValidationError: If content data is invalid
        """        start_time = datetime.now()
        
        try:
            if not content_data:
                raise ContentValidationError("Empty content data provided")
            
            # Extract content components
            text_content = content_data.get('text', '')
            media_type = content_data.get('media_type', 'unknown')
            metadata = content_data.get('metadata', {})
            
            # Create analysis profile
            profile = ContentAnalysisProfile()
            
            # Perform comprehensive analysis
            await self._classify_content(content_data, profile)
            await self._analyze_trends_and_timing(content_data, profile)
            await self._analyze_target_audience(content_data, profile)
            await self._analyze_competitive_landscape(content_data, profile)
            await self._analyze_content_themes(content_data, profile)
            await self._analyze_content_structure(content_data, profile)
            await self._predict_performance(profile)
            
            # Generate optimization insights
            self._generate_optimization_recommendations(profile)
            
            # Calculate strategic scores
            self._calculate_strategic_scores(profile)
            
            # Create metrics
            metrics = ContentAnalysisMetrics(profile=profile)
            await self._analyze_content_risks(content_data, profile, metrics)
            await self._calculate_value_metrics(profile, metrics)
            
            end_time = datetime.now()
            metrics.processing_time = (end_time - start_time).total_seconds()
            metrics.confidence = self._calculate_confidence(profile, content_data)
            
            # Prepare result
            result = {
                'content_intelligence_score': profile.content_intelligence_score,
                'confidence': metrics.confidence,
                'classification': {
                    'category': profile.category.value,
                    'format': profile.format.value,
                    'engagement_type': profile.engagement_type.value
                },
                'trend_analysis': {
                    'trending_topics': profile.trend_analysis.trending_topics,
                    'hashtag_relevance': profile.trend_analysis.hashtag_relevance,
                    'seasonal_relevance': profile.trend_analysis.seasonal_relevance,
                    'timing_score': profile.trend_analysis.timing_score,
                    'trend_alignment': profile.trend_analysis.trend_alignment,
                    'viral_elements': profile.trend_analysis.viral_elements,
                    'meme_potential': profile.trend_analysis.meme_potential
                },
                'audience_analysis': {
                    'primary_audience': profile.audience_analysis.primary_audience.value,
                    'secondary_audiences': [aud.value for aud in profile.audience_analysis.secondary_audiences],
                    'audience_match_score': profile.audience_analysis.audience_match_score,
                    'age_range': profile.audience_analysis.age_range,
                    'engagement_preferences': profile.audience_analysis.engagement_preferences,
                    'platform_affinity': profile.audience_analysis.platform_affinity
                },
                'competitive_analysis': {
                    'content_saturation': profile.competitor_analysis.content_saturation,
                    'differentiation_score': profile.competitor_analysis.differentiation_score,
                    'competitive_advantage': profile.competitor_analysis.competitive_advantage,
                    'uniqueness_factors': profile.competitor_analysis.uniqueness_factors,
                    'market_gap_opportunities': profile.competitor_analysis.market_gap_opportunities
                },
                'theme_analysis': {
                    'primary_theme': profile.theme_analysis.primary_theme,
                    'secondary_themes': profile.theme_analysis.secondary_themes,
                    'emotional_themes': profile.theme_analysis.emotional_themes,
                    'theme_consistency': profile.theme_analysis.theme_consistency,
                    'brand_alignment': profile.theme_analysis.brand_alignment
                },
                'structure_analysis': {
                    'narrative_structure': profile.structure_analysis.narrative_structure,
                    'pacing_score': profile.structure_analysis.pacing_score,
                    'attention_retention': profile.structure_analysis.attention_retention,
                    'opening_strength': profile.structure_analysis.opening_strength,
                    'hook_effectiveness': profile.structure_analysis.hook_effectiveness,
                    'closing_impact': profile.structure_analysis.closing_impact
                },
                'performance_predictions': {
                    'engagement_prediction': profile.engagement_prediction,
                    'reach_potential': profile.reach_potential,
                    'conversion_likelihood': profile.conversion_likelihood,
                    'brand_impact': profile.brand_impact,
                    'viral_potential': metrics.viral_potential,
                    'monetization_potential': metrics.monetization_potential
                },
                'value_metrics': {
                    'educational_value': metrics.educational_value,
                    'entertainment_value': metrics.entertainment_value,
                    'brand_consistency': metrics.brand_consistency,
                    'message_clarity': metrics.message_clarity,
                    'call_to_action_effectiveness': metrics.call_to_action_effectiveness
                },
                'risk_assessment': {
                    'controversy_risk': metrics.controversy_risk,
                    'copyright_risk': metrics.copyright_risk,
                    'platform_compliance': metrics.platform_compliance
                },
                'optimization': {
                    'optimization_score': profile.optimization_score,
                    'improvement_areas': profile.improvement_areas,
                    'strategic_recommendations': profile.strategic_recommendations,
                    'market_readiness': profile.market_readiness,
                    'success_probability': profile.success_probability
                }
            }
            
            # Log metrics
            self.metrics_collector.track_business_metric(
                metric_name="content_analysis_completed",
                value=1,
                metadata={
                    'intelligence_score': profile.content_intelligence_score,
                    'category': profile.category.value,
                    'format': profile.format.value,
                    'processing_time': metrics.processing_time
                }
            )
            
            logger.info(f"Content analysis completed: {profile.content_intelligence_score:.2f}/100")
            return result
            
        except Exception as e:
            logger.error(f"Content analysis failed: {str(e)}")
            self.metrics_collector.capture_errors("content_analysis_error", str(e))
            raise QualityCheckError(f"Content analysis failed: {str(e)}") from e
    
    async def _classify_content(self, content_data: Dict[str, Any], profile: ContentAnalysisProfile):
        """Classify content category, format, and engagement type"""        try:
            text_content = content_data.get('text', '').lower()
            media_type = content_data.get('media_type', 'unknown')
            metadata = content_data.get('metadata', {})
            
            # Classify category based on keywords
            category_scores = {}
            for category, keywords in self.category_keywords.items():
                score = sum(1 for keyword in keywords if keyword in text_content)
                category_scores[category] = score
            
            if category_scores and max(category_scores.values()) > 0:
                profile.category = max(category_scores, key=category_scores.get)
            
            # Classify format based on media type and content characteristics
            if media_type == 'video':
                duration = metadata.get('duration', 0)
                if duration < 60:
                    profile.format = ContentFormat.VIDEO_SHORT
                elif duration < 600:
                    profile.format = ContentFormat.VIDEO_MEDIUM
                else:
                    profile.format = ContentFormat.VIDEO_LONG
            elif media_type == 'audio':
                duration = metadata.get('duration', 0)
                if duration > 300:  # 5+ minutes
                    profile.format = ContentFormat.AUDIO_PODCAST
                else:
                    profile.format = ContentFormat.AUDIO_MUSIC
            elif media_type == 'image':
                if metadata.get('is_graphic', False):
                    profile.format = ContentFormat.IMAGE_GRAPHIC
                else:
                    profile.format = ContentFormat.IMAGE_PHOTO
            elif text_content:
                word_count = len(text_content.split())
                if word_count > 500:
                    profile.format = ContentFormat.TEXT_ARTICLE
                else:
                    profile.format = ContentFormat.TEXT_POST
            
            # Classify engagement type
            engagement_indicators = {
                EngagementType.VIRAL: ['challenge', 'trend', 'viral', 'share', 'tag'],
                EngagementType.EDUCATIONAL: ['learn', 'how', 'tutorial', 'guide', 'explain'],
                EngagementType.INSPIRATIONAL: ['inspire', 'motivate', 'achieve', 'dream', 'success'],
                EngagementType.ENTERTAINING: ['funny', 'hilarious', 'laugh', 'entertainment', 'comedy'],
                EngagementType.INFORMATIONAL: ['news', 'information', 'update', 'fact', 'data'],
                EngagementType.COMMERCIAL: ['buy', 'sale', 'offer', 'product', 'service']
            }
            
            engagement_scores = {}
            for eng_type, indicators in engagement_indicators.items():
                score = sum(1 for indicator in indicators if indicator in text_content)
                engagement_scores[eng_type] = score
            
            if engagement_scores and max(engagement_scores.values()) > 0:
                profile.engagement_type = max(engagement_scores, key=engagement_scores.get)
            
        except Exception as e:
            logger.warning(f"Content classification failed: {str(e)}")
    
    async def _analyze_trends_and_timing(self, content_data: Dict[str, Any], profile: ContentAnalysisProfile):
        """Analyze content trends and timing relevance"""        try:
            text_content = content_data.get('text', '').lower()
            hashtags = content_data.get('hashtags', [])
            category = profile.category.value
            
            # Analyze trending topics
            relevant_trends = []
            if category in self.trending_topics:
                for topic in self.trending_topics[category]:
                    if topic.lower() in text_content:
                        relevant_trends.append(topic)
            
            # Add general trends
            for topic in self.trending_topics['general']:
                if topic.lower() in text_content and topic not in relevant_trends:
                    relevant_trends.append(topic)
            
            profile.trend_analysis.trending_topics = relevant_trends
            
            # Hashtag relevance analysis
            for hashtag in hashtags:
                hashtag_clean = hashtag.strip('#').lower()
                relevance = 0.5  # Base relevance
                
                # Check if hashtag relates to trending topics
                for trend in relevant_trends:
                    if trend.lower() in hashtag_clean:
                        relevance += 0.3
                
                # Check hashtag popularity (simplified)
                if len(hashtag_clean) < 15 and not hashtag_clean.isdigit():
                    relevance += 0.2
                
                profile.trend_analysis.hashtag_relevance[hashtag] = min(1.0, relevance)
            
            # Seasonal relevance (simplified)
            current_month = datetime.now().month
            seasonal_keywords = {
                1: ['new year', 'resolution', 'fresh start'],
                2: ['valentine', 'love', 'heart'],
                3: ['spring', 'renewal', 'growth'],
                6: ['summer', 'vacation', 'sun'],
                9: ['back to school', 'autumn', 'fall'],
                12: ['christmas', 'holiday', 'year end']
            }
            
            seasonal_score = 0.5  # Base score
            if current_month in seasonal_keywords:
                for keyword in seasonal_keywords[current_month]:
                    if keyword in text_content:
                        seasonal_score += 0.15
            
            profile.trend_analysis.seasonal_relevance = min(1.0, seasonal_score)
            
            # Timing score (simplified - based on current hour)
            current_hour = datetime.now().hour
            optimal_hours = [9, 11, 13, 17, 19, 20]  # General optimal posting times
            
            if current_hour in optimal_hours:
                profile.trend_analysis.timing_score = 85
            elif current_hour in [8, 10, 12, 14, 16, 18, 21]:
                profile.trend_analysis.timing_score = 70
            else:
                profile.trend_analysis.timing_score = 50
            
            # Overall trend alignment
            alignment_factors = [
                len(relevant_trends) * 15,  # Trending topic alignment
                profile.trend_analysis.seasonal_relevance * 50,
                profile.trend_analysis.timing_score
            ]
            
            profile.trend_analysis.trend_alignment = min(100, np.mean(alignment_factors))
            
            # Viral elements detection
            viral_indicators = [
                'challenge', 'trend', 'viral', 'amazing', 'incredible', 'shocking',
                'unbelievable', 'must see', 'you won\'t believe', 'breaking'
            ]
            
            viral_elements = []
            for indicator in viral_indicators:
                if indicator in text_content:
                    viral_elements.append(indicator)
            
            profile.trend_analysis.viral_elements = viral_elements
            profile.trend_analysis.meme_potential = min(100, len(viral_elements) * 20 + 30)
            
        except Exception as e:
            logger.warning(f"Trends analysis failed: {str(e)}")
    
    async def _analyze_target_audience(self, content_data: Dict[str, Any], profile: ContentAnalysisProfile):
        """Analyze target audience and demographic appeal"""        try:
            text_content = content_data.get('text', '').lower()
            metadata = content_data.get('metadata', {})
            
            # Audience classification based on content indicators
            audience_scores = {}
            for audience, indicators in self.audience_indicators.items():
                score = sum(1 for indicator in indicators if indicator in text_content)
                audience_scores[audience] = score
            
            # Set primary audience
            if audience_scores and max(audience_scores.values()) > 0:
                profile.audience_analysis.primary_audience = max(audience_scores, key=audience_scores.get)
            
            # Set secondary audiences (those with positive scores)
            secondary = [aud for aud, score in audience_scores.items() 
                        if score > 0 and aud != profile.audience_analysis.primary_audience]
            profile.audience_analysis.secondary_audiences = secondary[:3]  # Top 3
            
            # Age range estimation based on primary audience
            age_ranges = {
                AudienceSegment.TEENS: (13, 17),
                AudienceSegment.GEN_Z: (16, 24),
                AudienceSegment.MILLENNIALS: (25, 40),
                AudienceSegment.GEN_X: (41, 56),
                AudienceSegment.BOOMERS: (57, 75),
                AudienceSegment.STUDENTS: (16, 25),
                AudienceSegment.PROFESSIONALS: (25, 55),
                AudienceSegment.PARENTS: (25, 50),
                AudienceSegment.ENTREPRENEURS: (22, 45)
            }
            
            profile.audience_analysis.age_range = age_ranges.get(
                profile.audience_analysis.primary_audience, (18, 65)
            )
            
            # Gender distribution (simplified estimation)
            gender_indicators = {
                'male': ['sports', 'gaming', 'tech', 'business', 'finance'],
                'female': ['beauty', 'fashion', 'lifestyle', 'wellness', 'parenting'],
                'neutral': ['education', 'travel', 'food', 'entertainment', 'news']
            }
            
            gender_scores = {gender: 0 for gender in ['male', 'female', 'neutral']}
            
            for gender, keywords in gender_indicators.items():
                for keyword in keywords:
                    if keyword in text_content:
                        gender_scores[gender] += 1
            
            total_gender_score = sum(gender_scores.values())
            if total_gender_score > 0:
                profile.audience_analysis.gender_distribution = {
                    gender: (score / total_gender_score) * 100 
                    for gender, score in gender_scores.items()
                }
            else:
                profile.audience_analysis.gender_distribution = {
                    'male': 40, 'female': 40, 'neutral': 20
                }
            
            # Platform affinity based on content characteristics
            platform_scores = {
                'instagram': 0,
                'tiktok': 0,
                'youtube': 0,
                'linkedin': 0,
                'twitter': 0,
                'facebook': 0
            }
            
            # Instagram affinity
            instagram_indicators = ['photo', 'visual', 'aesthetic', 'style', 'fashion']
            platform_scores['instagram'] = sum(1 for ind in instagram_indicators if ind in text_content)
            
            # TikTok affinity
            tiktok_indicators = ['trend', 'viral', 'dance', 'challenge', 'short']
            platform_scores['tiktok'] = sum(1 for ind in tiktok_indicators if ind in text_content)
            
            # YouTube affinity
            youtube_indicators = ['tutorial', 'how-to', 'vlog', 'review', 'explain']
            platform_scores['youtube'] = sum(1 for ind in youtube_indicators if ind in text_content)
            
            # LinkedIn affinity
            linkedin_indicators = ['professional', 'career', 'business', 'networking', 'industry']
            platform_scores['linkedin'] = sum(1 for ind in linkedin_indicators if ind in text_content)
            
            # Normalize scores
            max_platform_score = max(platform_scores.values()) if platform_scores.values() else 1
            if max_platform_score > 0:
                profile.audience_analysis.platform_affinity = {
                    platform: (score / max_platform_score) * 100 
                    for platform, score in platform_scores.items()
                }
            
            # Audience match score
            match_factors = [
                len(profile.audience_analysis.secondary_audiences) * 15,  # Multiple audience appeal
                max(platform_scores.values()) * 20,  # Platform alignment
                50  # Base score
            ]
            
            profile.audience_analysis.audience_match_score = min(100, sum(match_factors))
            
            # Engagement preferences
            preferences = []
            if 'visual' in text_content or 'photo' in text_content:
                preferences.append('visual_content')
            if 'video' in text_content or 'watch' in text_content:
                preferences.append('video_content')
            if 'comment' in text_content or 'share' in text_content:
                preferences.append('social_interaction')
            if 'learn' in text_content or 'educational' in text_content:
                preferences.append('educational_content')
            
            profile.audience_analysis.engagement_preferences = preferences
            
        except Exception as e:
            logger.warning(f"Audience analysis failed: {str(e)}")
    
    async def _analyze_competitive_landscape(self, content_data: Dict[str, Any], profile: ContentAnalysisProfile):
        """Analyze competitive landscape and differentiation"""        try:
            text_content = content_data.get('text', '').lower()
            category = profile.category.value
            
            # Content saturation estimation (simplified)
            high_saturation_categories = ['entertainment', 'lifestyle', 'fashion']
            medium_saturation_categories = ['education', 'business', 'technology']
            
            if category in high_saturation_categories:
                base_saturation = 75
            elif category in medium_saturation_categories:
                base_saturation = 60
            else:
                base_saturation = 45
            
            profile.competitor_analysis.content_saturation = base_saturation
            
            # Differentiation factors
            unique_indicators = [
                'unique', 'exclusive', 'first', 'original', 'innovative',
                'breakthrough', 'pioneering', 'revolutionary', 'never before'
            ]
            
            differentiation_score = 40  # Base score
            uniqueness_factors = []
            
            for indicator in unique_indicators:
                if indicator in text_content:
                    differentiation_score += 10
                    uniqueness_factors.append(indicator)
            
            profile.competitor_analysis.differentiation_score = min(100, differentiation_score)
            profile.competitor_analysis.uniqueness_factors = uniqueness_factors
            
            # Competitive advantages
            advantage_indicators = {
                'expertise': ['expert', 'specialist', 'professional', 'certified'],
                'authenticity': ['authentic', 'genuine', 'real', 'honest'],
                'innovation': ['innovative', 'new', 'cutting-edge', 'advanced'],
                'quality': ['high-quality', 'premium', 'professional', 'excellence'],
                'accessibility': ['easy', 'simple', 'beginner', 'accessible']
            }
            
            competitive_advantages = []
            for advantage, keywords in advantage_indicators.items():
                if any(keyword in text_content for keyword in keywords):
                    competitive_advantages.append(advantage)
            
            profile.competitor_analysis.competitive_advantage = competitive_advantages
            
            # Market gap opportunities
            gap_opportunities = []
            
            # Under-served demographics
            if profile.audience_analysis.primary_audience in [AudienceSegment.GEN_X, AudienceSegment.BOOMERS]:
                gap_opportunities.append('older_demographic_focus')
            
            # Niche categories
            niche_categories = ['health_fitness', 'personal_development', 'art_design']
            if profile.category.value in niche_categories:
                gap_opportunities.append('niche_expertise')
            
            # Educational content gap
            if profile.engagement_type == EngagementType.EDUCATIONAL:
                gap_opportunities.append('educational_content_shortage')
            
            profile.competitor_analysis.market_gap_opportunities = gap_opportunities
            
            # Competitive threats
            threats = []
            if profile.competitor_analysis.content_saturation > 70:
                threats.append('high_market_saturation')
            if not competitive_advantages:
                threats.append('limited_differentiation')
            if profile.format == ContentFormat.VIDEO_SHORT:
                threats.append('platform_algorithm_dependence')
            
            profile.competitor_analysis.competitive_threats = threats
            
        except Exception as e:
            logger.warning(f"Competitive analysis failed: {str(e)}")
    
    async def _analyze_content_themes(self, content_data: Dict[str, Any], profile: ContentAnalysisProfile):
        """Analyze content themes and messaging"""        try:
            text_content = content_data.get('text', '').lower()
            
            # Primary theme detection based on category
            category_themes = {
                ContentCategory.ENTERTAINMENT: 'entertainment',
                ContentCategory.EDUCATION: 'learning',
                ContentCategory.LIFESTYLE: 'lifestyle',
                ContentCategory.TECHNOLOGY: 'innovation',
                ContentCategory.BUSINESS: 'success',
                ContentCategory.HEALTH_FITNESS: 'wellness'
            }
            
            profile.theme_analysis.primary_theme = category_themes.get(
                profile.category, 'general'
            )
            
            # Secondary themes
            theme_keywords = {
                'motivation': ['motivate', 'inspire', 'achieve', 'goal', 'success'],
                'community': ['community', 'together', 'share', 'connect', 'family'],
                'innovation': ['new', 'innovative', 'future', 'technology', 'advanced'],
                'authenticity': ['real', 'authentic', 'genuine', 'honest', 'true'],
                'empowerment': ['empower', 'strong', 'independent', 'confident', 'capable'],
                'sustainability': ['sustainable', 'eco', 'green', 'environment', 'planet']
            }
            
            secondary_themes = []
            for theme, keywords in theme_keywords.items():
                if any(keyword in text_content for keyword in keywords):
                    secondary_themes.append(theme)
            
            profile.theme_analysis.secondary_themes = secondary_themes[:3]  # Top 3
            
            # Emotional themes
            emotion_keywords = {
                'joy': ['happy', 'joy', 'celebration', 'excited', 'fun'],
                'inspiration': ['inspire', 'motivate', 'uplift', 'encourage', 'hope'],
                'nostalgia': ['remember', 'memories', 'childhood', 'past', 'nostalgic'],
                'concern': ['worry', 'concern', 'problem', 'issue', 'challenge'],
                'curiosity': ['wonder', 'question', 'explore', 'discover', 'mystery']
            }
            
            emotional_themes = []
            for emotion, keywords in emotion_keywords.items():
                if any(keyword in text_content for keyword in keywords):
                    emotional_themes.append(emotion)
            
            profile.theme_analysis.emotional_themes = emotional_themes
            
            # Theme consistency (simplified)
            theme_count = len(secondary_themes) + len(emotional_themes)
            if theme_count <= 3:
                profile.theme_analysis.theme_consistency = 90  # Focused themes
            elif theme_count <= 5:
                profile.theme_analysis.theme_consistency = 70  # Moderate focus
            else:
                profile.theme_analysis.theme_consistency = 50  # Too many themes
            
            # Theme relevance to category
            category_relevant_themes = {
                ContentCategory.ENTERTAINMENT: ['joy', 'fun', 'community'],
                ContentCategory.EDUCATION: ['learning', 'curiosity', 'empowerment'],
                ContentCategory.BUSINESS: ['success', 'innovation', 'empowerment'],
                ContentCategory.LIFESTYLE: ['authenticity', 'wellness', 'community']
            }
            
            relevant_themes = category_relevant_themes.get(profile.category, [])
            theme_relevance = 50  # Base score
            
            for theme in secondary_themes + emotional_themes:
                if theme in relevant_themes:
                    theme_relevance += 15
            
            profile.theme_analysis.theme_relevance = min(100, theme_relevance)
            
            # Brand alignment (simplified assessment)
            brand_indicators = ['brand', 'mission', 'values', 'vision', 'purpose']
            brand_mentions = sum(1 for indicator in brand_indicators if indicator in text_content)
            
            alignment_factors = [
                profile.theme_analysis.theme_consistency,
                profile.theme_analysis.theme_relevance,
                min(100, brand_mentions * 20 + 50)
            ]
            
            profile.theme_analysis.brand_alignment = np.mean(alignment_factors)
            
        except Exception as e:
            logger.warning(f"Theme analysis failed: {str(e)}")
    
    async def _analyze_content_structure(self, content_data: Dict[str, Any], profile: ContentAnalysisProfile):
        """Analyze content structure and narrative flow"""        try:
            text_content = content_data.get('text', '')
            metadata = content_data.get('metadata', {})
            
            # Narrative structure detection
            structure_indicators = {
                'linear': ['first', 'then', 'next', 'finally', 'conclusion'],
                'problem_solution': ['problem', 'issue', 'solution', 'solve', 'fix'],
                'story': ['story', 'once', 'happened', 'experience', 'journey'],
                'comparison': ['versus', 'compared', 'better', 'different', 'contrast'],
                'list': ['tips', 'ways', 'steps', 'methods', 'reasons']
            }
            
            structure_scores = {}
            for structure, indicators in structure_indicators.items():
                score = sum(1 for indicator in indicators if indicator.lower() in text_content.lower())
                structure_scores[structure] = score
            
            if structure_scores and max(structure_scores.values()) > 0:
                profile.structure_analysis.narrative_structure = max(structure_scores, key=structure_scores.get)
            
            # Pacing analysis (based on sentence and paragraph length)
            sentences = text_content.split('.')
            paragraphs = text_content.split('\n\n')
            
            if sentences and paragraphs:
                avg_sentence_length = np.mean([len(s.split()) for s in sentences if s.strip()])
                avg_paragraph_length = np.mean([len(p.split()) for p in paragraphs if p.strip()])
                
                # Optimal pacing scores
                if 15 <= avg_sentence_length <= 25:
                    sentence_pacing = 90
                elif 10 <= avg_sentence_length <= 30:
                    sentence_pacing = 75
                else:
                    sentence_pacing = 60
                
                if 50 <= avg_paragraph_length <= 150:
                    paragraph_pacing = 90
                elif 30 <= avg_paragraph_length <= 200:
                    paragraph_pacing = 75
                else:
                    paragraph_pacing = 60
                
                profile.structure_analysis.pacing_score = (sentence_pacing + paragraph_pacing) / 2
            
            # Hook analysis (first 50 words)
            opening_text = ' '.join(text_content.split()[:50]).lower()
            
            hook_indicators = [
                'question', 'imagine', 'what if', 'did you know', 'surprising',
                'shocking', 'secret', 'mistake', 'truth', 'amazing'
            ]
            
            hook_score = 40  # Base score
            for indicator in hook_indicators:
                if indicator in opening_text:
                    hook_score += 15
            
            # Question hooks
            if '?' in opening_text:
                hook_score += 20
            
            # Strong opening words
            strong_openers = ['imagine', 'picture', 'stop', 'wait', 'listen']
            if any(opener in opening_text[:20] for opener in strong_openers):
                hook_score += 15
            
            profile.structure_analysis.opening_strength = min(100, hook_score)
            profile.structure_analysis.hook_effectiveness = min(100, hook_score)
            
            # Closing analysis (last 50 words)
            closing_text = ' '.join(text_content.split()[-50:]).lower()
            
            closing_indicators = [
                'conclusion', 'summary', 'remember', 'takeaway', 'action',
                'next steps', 'call to action', 'subscribe', 'follow', 'share'
            ]
            
            closing_score = 40  # Base score
            for indicator in closing_indicators:
                if indicator in closing_text:
                    closing_score += 15
            
            profile.structure_analysis.closing_impact = min(100, closing_score)
            
            # Attention retention factors
            retention_factors = []
            
            # Variety in content
            if len(set(sentences)) / len(sentences) > 0.8:  # Unique sentences
                retention_factors.append(80)
            else:
                retention_factors.append(60)
            
            # Engagement elements
            engagement_elements = ['?', '!', 'you', 'your', 'we', 'us']
            engagement_count = sum(text_content.lower().count(element) for element in engagement_elements)
            retention_factors.append(min(100, engagement_count * 5 + 40))
            
            # Content length appropriateness
            word_count = len(text_content.split())
            if profile.format in [ContentFormat.VIDEO_SHORT, ContentFormat.TEXT_POST]:
                if word_count <= 150:
                    retention_factors.append(90)
                else:
                    retention_factors.append(60)
            elif profile.format in [ContentFormat.TEXT_ARTICLE, ContentFormat.VIDEO_MEDIUM]:
                if 300 <= word_count <= 800:
                    retention_factors.append(90)
                else:
                    retention_factors.append(70)
            
            profile.structure_analysis.attention_retention = np.mean(retention_factors)
            
            # Transition quality (simplified)
            transition_words = [
                'however', 'moreover', 'furthermore', 'additionally', 'meanwhile',
                'therefore', 'consequently', 'in contrast', 'on the other hand'
            ]
            
            transition_count = sum(1 for word in transition_words if word in text_content.lower())
            transition_density = transition_count / max(1, len(paragraphs))
            
            if 0.1 <= transition_density <= 0.3:
                profile.structure_analysis.transition_quality = 90
            elif transition_density <= 0.5:
                profile.structure_analysis.transition_quality = 75
            else:
                profile.structure_analysis.transition_quality = 60
            
            # Logical progression
            logical_indicators = ['because', 'since', 'due to', 'as a result', 'this leads to']
            logical_count = sum(1 for indicator in logical_indicators if indicator in text_content.lower())
            
            profile.structure_analysis.logical_progression = min(100, logical_count * 20 + 50)
            
        except Exception as e:
            logger.warning(f"Structure analysis failed: {str(e)}")
    
    async def _predict_performance(self, profile: ContentAnalysisProfile):
        """Predict content performance metrics"""        try:
            # Engagement prediction factors
            engagement_factors = [
                profile.trend_analysis.trend_alignment,
                profile.audience_analysis.audience_match_score,
                profile.structure_analysis.hook_effectiveness,
                profile.structure_analysis.attention_retention,
                len(profile.trend_analysis.viral_elements) * 10 + 50
            ]
            
            profile.engagement_prediction = np.mean(engagement_factors)
            
            # Reach potential factors
            reach_factors = [
                profile.trend_analysis.viral_elements and 80 or 50,  # Viral elements boost reach
                profile.audience_analysis.platform_affinity.get('instagram', 50) if profile.audience_analysis.platform_affinity else 50,
                profile.trend_analysis.hashtag_relevance and np.mean(list(profile.trend_analysis.hashtag_relevance.values())) * 100 or 50,
                profile.structure_analysis.opening_strength
            ]
            
            profile.reach_potential = np.mean(reach_factors)
            
            # Conversion likelihood factors
            conversion_factors = [
                profile.structure_analysis.closing_impact,
                profile.theme_analysis.brand_alignment,
                profile.engagement_type == EngagementType.COMMERCIAL and 80 or 40,
                profile.audience_analysis.audience_match_score
            ]
            
            profile.conversion_likelihood = np.mean(conversion_factors)
            
            # Brand impact factors
            brand_factors = [
                profile.theme_analysis.brand_alignment,
                profile.theme_analysis.theme_consistency,
                profile.competitor_analysis.differentiation_score,
                profile.audience_analysis.audience_match_score
            ]
            
            profile.brand_impact = np.mean(brand_factors)
            
        except Exception as e:
            logger.warning(f"Performance prediction failed: {str(e)}")
    
    def _generate_optimization_recommendations(self, profile: ContentAnalysisProfile):
        """Generate optimization recommendations"""        recommendations = []
        improvement_areas = []
        
        # Trend alignment recommendations
        if profile.trend_analysis.trend_alignment < 70:
            recommendations.append("Incorporate more trending topics and hashtags for better discoverability")
            improvement_areas.append("trend_alignment")
        
        # Audience targeting recommendations
        if profile.audience_analysis.audience_match_score < 70:
            recommendations.append("Refine content to better match target audience preferences")
            improvement_areas.append("audience_targeting")
        
        # Competitive positioning recommendations
        if profile.competitor_analysis.differentiation_score < 60:
            recommendations.append("Strengthen unique value proposition and differentiation factors")
            improvement_areas.append("differentiation")
        
        # Structure improvements
        if profile.structure_analysis.hook_effectiveness < 70:
            recommendations.append("Improve opening hook to capture attention more effectively")
            improvement_areas.append("content_hook")
        
        if profile.structure_analysis.closing_impact < 70:
            recommendations.append("Strengthen call-to-action and closing for better conversion")
            improvement_areas.append("call_to_action")
        
        # Theme consistency
        if profile.theme_analysis.theme_consistency < 70:
            recommendations.append("Focus on fewer, more consistent themes for clearer messaging")
            improvement_areas.append("theme_focus")
        
        # Performance optimization
        if profile.engagement_prediction < 70:
            recommendations.append("Add more engaging elements like questions, polls, or interactive content")
            improvement_areas.append("engagement_elements")
        
        # Platform-specific optimizations
        top_platform = max(profile.audience_analysis.platform_affinity.items(), key=lambda x: x[1])[0] if profile.audience_analysis.platform_affinity else 'instagram'
        
        platform_recommendations = {
            'instagram': "Optimize visual appeal and use relevant hashtags for Instagram",
            'tiktok': "Incorporate trending sounds and challenges for TikTok virality",
            'youtube': "Improve thumbnail and title for better YouTube click-through rates",
            'linkedin': "Enhance professional value and industry insights for LinkedIn"
        }
        
        if top_platform in platform_recommendations:
            recommendations.append(platform_recommendations[top_platform])
        
        profile.improvement_areas = improvement_areas
        profile.strategic_recommendations = recommendations
    
    def _calculate_strategic_scores(self, profile: ContentAnalysisProfile):
        """Calculate strategic and overall scores"""        try:
            # Optimization score
            optimization_factors = [
                profile.trend_analysis.trend_alignment,
                profile.audience_analysis.audience_match_score,
                profile.competitor_analysis.differentiation_score,
                profile.theme_analysis.theme_consistency,
                profile.structure_analysis.attention_retention
            ]
            
            profile.optimization_score = np.mean(optimization_factors)
            
            # Market readiness
            readiness_factors = [
                profile.trend_analysis.timing_score,
                profile.competitor_analysis.differentiation_score,
                profile.audience_analysis.audience_match_score,
                profile.structure_analysis.hook_effectiveness
            ]
            
            profile.market_readiness = np.mean(readiness_factors)
            
            # Success probability
            success_factors = [
                profile.engagement_prediction * 0.3,
                profile.reach_potential * 0.25,
                profile.optimization_score * 0.25,
                profile.market_readiness * 0.2
            ]
            
            profile.success_probability = sum(success_factors)
            
            # Overall content intelligence score
            intelligence_factors = [
                profile.optimization_score * 0.25,
                profile.engagement_prediction * 0.25,
                profile.reach_potential * 0.2,
                profile.brand_impact * 0.15,
                profile.market_readiness * 0.15
            ]
            
            profile.content_intelligence_score = sum(intelligence_factors)
            
        except Exception as e:
            logger.warning(f"Strategic score calculation failed: {str(e)}")
            profile.content_intelligence_score = 50
    
    async def _analyze_content_risks(self, content_data: Dict[str, Any], profile: ContentAnalysisProfile, metrics: ContentAnalysisMetrics):
        """Analyze content risks and compliance"""        try:
            text_content = content_data.get('text', '').lower()
            
            # Controversy risk assessment
            controversial_topics = [
                'politics', 'religion', 'controversial', 'scandal', 'debate',
                'protest', 'conflict', 'war', 'discrimination'
            ]
            
            controversy_score = 0
            for topic in controversial_topics:
                if topic in text_content:
                    controversy_score += 20
            
            metrics.controversy_risk = min(100, controversy_score)
            
            # Copyright risk assessment
            copyright_indicators = [
                'song', 'music', 'movie', 'film', 'brand', 'trademark',
                'copyrighted', 'licensed', 'cover', 'remix'
            ]
            
            copyright_score = 0
            for indicator in copyright_indicators:
                if indicator in text_content:
                    copyright_score += 15
            
            metrics.copyright_risk = min(100, copyright_score)
            
            # Platform compliance assessment
            compliance_factors = []
            
            # Content appropriateness
            inappropriate_content = ['explicit', 'adult', 'violence', 'hate', 'spam']
            if not any(word in text_content for word in inappropriate_content):
                compliance_factors.append(90)
            else:
                compliance_factors.append(40)
            
            # Community guidelines compliance
            community_friendly = ['positive', 'helpful', 'educational', 'inspiring']
            if any(word in text_content for word in community_friendly):
                compliance_factors.append(85)
            else:
                compliance_factors.append(70)
            
            # Content authenticity
            authenticity_indicators = ['authentic', 'genuine', 'real', 'honest']
            if any(word in text_content for word in authenticity_indicators):
                compliance_factors.append(80)
            else:
                compliance_factors.append(60)
            
            metrics.platform_compliance = np.mean(compliance_factors)
            
        except Exception as e:
            logger.warning(f"Risk analysis failed: {str(e)}")
    
    async def _calculate_value_metrics(self, profile: ContentAnalysisProfile, metrics: ContentAnalysisMetrics):
        """Calculate content value metrics"""        try:
            # Educational value
            educational_indicators = [
                profile.engagement_type == EngagementType.EDUCATIONAL,
                profile.category in [ContentCategory.EDUCATION, ContentCategory.TECHNOLOGY],
                'learn' in profile.theme_analysis.secondary_themes,
                len(profile.structure_analysis.narrative_structure) > 0
            ]
            
            metrics.educational_value = sum(indicator * 25 for indicator in educational_indicators)
            
            # Entertainment value
            entertainment_indicators = [
                profile.engagement_type == EngagementType.ENTERTAINING,
                profile.category == ContentCategory.ENTERTAINMENT,
                'joy' in profile.theme_analysis.emotional_themes,
                len(profile.trend_analysis.viral_elements) > 0
            ]
            
            metrics.entertainment_value = sum(indicator * 25 for indicator in entertainment_indicators)
            
            # Brand consistency
            metrics.brand_consistency = profile.theme_analysis.brand_alignment
            
            # Message clarity
            clarity_factors = [
                profile.theme_analysis.theme_consistency,
                profile.structure_analysis.logical_progression,
                profile.structure_analysis.transition_quality
            ]
            
            metrics.message_clarity = np.mean(clarity_factors)
            
            # Call to action effectiveness
            metrics.call_to_action_effectiveness = profile.structure_analysis.closing_impact
            
            # Viral potential (comprehensive)
            viral_factors = [
                profile.trend_analysis.meme_potential,
                profile.engagement_prediction,
                len(profile.trend_analysis.viral_elements) * 15 + 30,
                profile.structure_analysis.hook_effectiveness
            ]
            
            metrics.viral_potential = np.mean(viral_factors)
            
            # Monetization potential
            monetization_factors = [
                profile.engagement_type == EngagementType.COMMERCIAL and 80 or 40,
                profile.conversion_likelihood,
                profile.brand_impact,
                profile.audience_analysis.audience_match_score
            ]
            
            metrics.monetization_potential = np.mean(monetization_factors)
            
        except Exception as e:
            logger.warning(f"Value metrics calculation failed: {str(e)}")
    
    def _calculate_confidence(self, profile: ContentAnalysisProfile, content_data: Dict[str, Any]) -> float:
        """Calculate analysis confidence score"""        confidence = 0.85  # Base confidence
        
        # Adjust based on content completeness
        text_length = len(content_data.get('text', ''))
        if text_length > 100:
            confidence += 0.1
        elif text_length < 50:
            confidence -= 0.15
        
        # Adjust based on metadata availability
        metadata = content_data.get('metadata', {})
        if metadata:
            confidence += 0.05
        
        # Adjust based on analysis completeness
        if profile.trend_analysis.trending_topics:
            confidence += 0.05
        
        if profile.audience_analysis.platform_affinity:
            confidence += 0.05
        
        return max(0.6, min(1.0, confidence))


# Global content analyzer instance
# content_analyzer = ContentAnalyzer()  # Commented out for testing


async def analyze_content_intelligence(content_data: Dict[str, Any]) -> Dict[str, Any]:
    """    Convenient function for content intelligence analysis
    
    Args:
        content_data: Content information and metadata
        
    Returns:
        Dict containing content analysis results
    """    try:
        result = await content_analyzer.analyze_content(content_data)
        return result
    except Exception as e:
        logger.error(f"Content analysis error: {str(e)}")
        return {
            'error': str(e),
            'success': False
        }
