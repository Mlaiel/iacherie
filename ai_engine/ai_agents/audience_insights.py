"""Audience Insights Agent

Specialized AI agent for comprehensive audience analysis, demographic insights,
behavioral pattern recognition, and personalized audience development strategies.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use is strictly prohibited.
"""

import asyncio
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import logging
import numpy as np
import pandas as pd

from .base_agent import BaseAIAgent, AgentCapability, AgentConfiguration, AgentTask
# AudienceAnalyzer est défini inline dans collaboration_matcher.py, utilisons les analytics existants
from ..analytics.engagement_analytics import EngagementAnalyzer
# DemographicPredictor n'existe pas encore, utilisons une classe mock
from ..core.content_types import SocialPlatform, ContentType

logger = logging.getLogger(__name__)


class AudienceSegment(Enum):
    """
Audience segmentation categories"""

    DEMOGRAPHIC = "demographic"
    BEHAVIORAL = "behavioral"
    PSYCHOGRAPHIC = "psychographic"
    GEOGRAPHIC = "geographic"
    ENGAGEMENT_BASED = "engagement_based"
    CONTENT_PREFERENCE = "content_preference"
    PLATFORM_BEHAVIOR = "platform_behavior"
    PURCHASE_BEHAVIOR = "purchase_behavior"


class EngagementPattern(Enum):
    """Audience engagement patterns"""

    HIGH_FREQUENCY = "high_frequency"
    BINGE_CONSUMER = "binge_consumer"
    CASUAL_BROWSER = "casual_browser"
    LOYAL_FAN = "loyal_fan"
    TREND_FOLLOWER = "trend_follower"
    PREMIUM_SEEKER = "premium_seeker"
    SOCIAL_SHARER = "social_sharer"
    SILENT_CONSUMER = "silent_consumer"


@dataclass
class DemographicProfile:
    """Comprehensive demographic profile"""
    age_range: str = ""
    gender_distribution: Dict[str, float] = field(default_factory=dict)
    location_data: Dict[str, float] = field(default_factory=dict)
    education_level: Dict[str, float] = field(default_factory=dict)
    income_bracket: Dict[str, float] = field(default_factory=dict)
    occupation_categories: Dict[str, float] = field(default_factory=dict)
    language_preferences: Dict[str, float] = field(default_factory=dict)
    device_preferences: Dict[str, float] = field(default_factory=dict)


@dataclass
class BehavioralProfile:
    """Audience behavioral patterns"""
    content_preferences: Dict[ContentType, float] = field(default_factory=dict)
    platform_activity: Dict[SocialPlatform, Dict[str, Any]] = field(default_factory=dict)
    engagement_times: Dict[str, List[int]] = field(default_factory=dict)  # day -> hours
    interaction_patterns: Dict[str, float] = field(default_factory=dict)
    content_consumption_rate: float = 0.0
    sharing_likelihood: float = 0.0
    comment_engagement: float = 0.0
    story_completion_rate: float = 0.0
    video_watch_time: float = 0.0
    music_listening_duration: float = 0.0


@dataclass
class PsychographicProfile:
    """
Audience psychographic insights"""
    interests: Dict[str, float] = field(default_factory=dict)
    values: Dict[str, float] = field(default_factory=dict)
    lifestyle_indicators: Dict[str, float] = field(default_factory=dict)
    personality_traits: Dict[str, float] = field(default_factory=dict)
    motivational_drivers: Dict[str, float] = field(default_factory=dict)
    brand_affinity: Dict[str, float] = field(default_factory=dict)
    content_themes_resonance: Dict[str, float] = field(default_factory=dict)


@dataclass
class AudienceInsight:
    """
Comprehensive audience insight"""
    insight_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    segment_name: str = ""
    segment_type: AudienceSegment = AudienceSegment.DEMOGRAPHIC
    size_percentage: float = 0.0
    growth_trend: float = 0.0
    demographic_profile: DemographicProfile = field(default_factory=DemographicProfile)
    behavioral_profile: BehavioralProfile = field(default_factory=BehavioralProfile)
    psychographic_profile: PsychographicProfile = field(default_factory=PsychographicProfile)
    engagement_pattern: EngagementPattern = EngagementPattern.CASUAL_BROWSER
    content_recommendations: List[str] = field(default_factory=list)
    platform_strategies: Dict[SocialPlatform, Dict[str, Any]] = field(default_factory=dict)
    monetization_potential: float = 0.0
    collaboration_opportunities: List[str] = field(default_factory=list)
    predicted_actions: List[Dict[str, Any]] = field(default_factory=list)
    confidence_score: float = 0.0
    data_freshness: datetime = field(default_factory=datetime.utcnow)


@dataclass 
class AudienceAnalysisRequest:
    """Request for audience analysis"""
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    creator_id: str = ""
    platforms: List[SocialPlatform] = field(default_factory=list)
    time_range: timedelta = field(default=timedelta(days=30))
    analysis_depth: str = "comprehensive"  # basic, standard, comprehensive
    include_predictive: bool = True
    segment_criteria: Dict[str, Any] = field(default_factory=dict)
    custom_metrics: List[str] = field(default_factory=list)


class AudienceInsightsAgent(BaseAIAgent):
    """
    Advanced audience insights and analytics agent
    
    Capabilities:
    - Multi-dimensional audience segmentation
    - Behavioral pattern recognition
    - Demographic trend analysis
    - Psychographic profiling
    - Engagement optimization recommendations
    - Predictive audience modeling
    - Cross-platform audience mapping
    - Personalization strategy development
    """
    
    def __init__(self, config: AgentConfiguration):
        # Ensure required capabilities
        required_capabilities = {
            AgentCapability.ANALYSIS,
            AgentCapability.DATA_PROCESSING,
            AgentCapability.PREDICTIVE_MODELING,
            AgentCapability.AUDIENCE_SEGMENTATION,
            AgentCapability.BEHAVIORAL_ANALYSIS
        }
        
        config.capabilities.update(required_capabilities)
        super().__init__(config)
        
        # Initialize analysis components
        self.audience_analyzer = self._create_mock_analyzer()
        self.demographic_predictor = self._create_mock_predictor()
        
        # Analytics storage
        self.audience_segments: Dict[str, AudienceInsight] = {}
        self.analysis_history: List[Dict[str, Any]] = []
        self.segment_performance: Dict[str, Dict[str, float]] = {}
        
        logger.info(f"Audience Insights Agent {self.agent_id} initialized successfully")
    
    def _create_mock_analyzer(self):
        """Create mock audience analyzer for testing compatibility"""
        class MockAudienceAnalyzer:
            async def analyze_demographics(self, data): return {}
            async def analyze_behavior(self, data): return {}
            async def segment_audience(self, data, criteria): return []
        return MockAudienceAnalyzer()
    
    def _create_mock_predictor(self):
        """
Create mock demographic predictor for testing compatibility"""
        class MockDemographicPredictor:
            async def predict_demographics(self, behavioral_data): return {}
            async def predict_engagement(self, demographic_data): return 0.0
        return MockDemographicPredictor()
    
    async def analyze_audience(self, request: AudienceAnalysisRequest) -> List[AudienceInsight]:
        """
        Perform comprehensive audience analysis across multiple dimensions
        """
        try:
            logger.info(f"Starting comprehensive audience analysis for creator {request.creator_id}")
            
            # Collect multi-platform data
            audience_data = await self._collect_audience_data(request)
            
            # Perform segmentation analysis
            segments = await self._perform_audience_segmentation(audience_data, request)
            
            # Generate insights for each segment
            insights = []
            for segment in segments:
                insight = await self._generate_segment_insight(segment, audience_data, request)
                insights.append(insight)
                self.audience_segments[insight.insight_id] = insight
            
            # Store analysis history
            self.analysis_history.append({
                'request_id': request.request_id,
                'creator_id': request.creator_id,
                'timestamp': datetime.utcnow(),
                'segments_count': len(insights),
                'platforms_analyzed': len(request.platforms)
            })
            
            logger.info(f"Generated {len(insights)} audience insights for creator {request.creator_id}")
            return insights
            
        except Exception as e:
            logger.error(f"Audience analysis failed: {str(e)}")
            return []
    
    async def _collect_audience_data(self, request: AudienceAnalysisRequest) -> Dict[str, Any]:
        """Collect comprehensive audience data from multiple sources"""
        audience_data = {
            'demographics': {},
            'behavior': {},
            'engagement': {},
            'content_preferences': {},
            'platform_activity': {}
        }
        
        for platform in request.platforms:
            platform_data = await self._collect_platform_data(platform, request)
            audience_data['platform_activity'][platform.value] = platform_data
        
        return audience_data
    
    async def _collect_platform_data(self, platform: SocialPlatform, request: AudienceAnalysisRequest) -> Dict[str, Any]:
        """
Collect platform-specific audience data"""
        # Mock data collection - in production, this would integrate with platform APIs
        return {
            'followers_count': 10000 + hash(request.creator_id) % 50000,
            'engagement_rate': 0.03 + (hash(request.creator_id) % 100) / 1000,
            'demographics': self._generate_mock_demographics(),
            'activity_patterns': self._generate_mock_activity_patterns(),
            'content_performance': self._generate_mock_content_performance()
        }
    
    def _generate_mock_demographics(self) -> Dict[str, Any]:
        """
Generate realistic mock demographic data"""
        return {
            'age_distribution': {
                '18-24': 0.25,
                '25-34': 0.35, 
                '35-44': 0.25,
                '45-54': 0.10,
                '55+': 0.05
            },
            'gender': {'female': 0.6, 'male': 0.35, 'other': 0.05},
            'locations': {
                'US': 0.4, 'UK': 0.15, 'Canada': 0.12,
                'Australia': 0.08, 'Germany': 0.10, 'Other': 0.15
            }
        }
    
    def _generate_mock_activity_patterns(self) -> Dict[str, Any]:
        """
Generate realistic activity pattern data"""
        return {
            'peak_hours': [19, 20, 21],  # 7-9 PM
            'active_days': ['Monday', 'Wednesday', 'Friday', 'Sunday'],
            'session_duration_avg': 12.5,  # minutes
            'content_interaction_rate': 0.045
        }
    
    def _generate_mock_content_performance(self) -> Dict[str, Any]:
        """
Generate content performance insights"""
        return {
            'top_content_types': {
                ContentType.VIDEO.value: 0.4,
                ContentType.IMAGE.value: 0.3,
                ContentType.AUDIO.value: 0.2,
                ContentType.TEXT.value: 0.1
            },
            'engagement_by_type': {
                'likes': 0.85, 'comments': 0.12, 
                'shares': 0.08, 'saves': 0.15
            }
        }
    
    async def _perform_audience_segmentation(self, audience_data: Dict[str, Any], request: AudienceAnalysisRequest) -> List[Dict[str, Any]]:
        """
Perform intelligent audience segmentation"""
        segments = []
        
        # Demographic-based segments
        age_segments = self._create_age_based_segments(audience_data)
        segments.extend(age_segments)
        
        # Behavioral segments  
        behavior_segments = self._create_behavioral_segments(audience_data)
        segments.extend(behavior_segments)
        
        # Engagement-based segments
        engagement_segments = self._create_engagement_segments(audience_data)
        segments.extend(engagement_segments)
        
        return segments[:10]  # Return top 10 most significant segments
    
    def _create_age_based_segments(self, audience_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
Create age-based audience segments"""
        return [
            {
                'name': 'Gen Z Creators',
                'type': AudienceSegment.DEMOGRAPHIC,
                'criteria': {'age_range': '18-24'},
                'size': 0.25,
                'characteristics': ['trending_content', 'short_form_video', 'mobile_first']
            },
            {
                'name': 'Millennial Professionals', 
                'type': AudienceSegment.DEMOGRAPHIC,
                'criteria': {'age_range': '25-34'},
                'size': 0.35,
                'characteristics': ['quality_content', 'educational', 'career_focused']
            }
        ]
    
    def _create_behavioral_segments(self, audience_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
Create behavior-based segments"""
        return [
            {
                'name': 'Heavy Consumers',
                'type': AudienceSegment.BEHAVIORAL,
                'criteria': {'daily_usage': '>2hours'},
                'size': 0.15,
                'characteristics': ['high_engagement', 'early_adopter', 'trend_setter']
            },
            {
                'name': 'Casual Browsers',
                'type': AudienceSegment.BEHAVIORAL,
                'criteria': {'weekly_usage': '<5hours'},
                'size': 0.45,
                'characteristics': ['quality_over_quantity', 'specific_interests', 'selective']
            }
        ]
    
    def _create_engagement_segments(self, audience_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
Create engagement-based segments"""
        return [
            {
                'name': 'Super Fans',
                'type': AudienceSegment.ENGAGEMENT_BASED,
                'criteria': {'engagement_rate': '>10%'},
                'size': 0.08,
                'characteristics': ['loyal', 'advocate', 'premium_buyer']
            },
            {
                'name': 'Social Sharers',
                'type': AudienceSegment.ENGAGEMENT_BASED,
                'criteria': {'share_rate': '>5%'},
                'size': 0.12,
                'characteristics': ['amplifier', 'network_influencer', 'viral_catalyst']
            }
        ]
    
    async def _generate_segment_insight(self, segment_data: Dict[str, Any], audience_data: Dict[str, Any], request: AudienceAnalysisRequest) -> AudienceInsight:
        """
Generate comprehensive insight for audience segment"""
        
        # Create demographic profile
        demographic_profile = self._build_demographic_profile(segment_data, audience_data)
        
        # Create behavioral profile
        behavioral_profile = self._build_behavioral_profile(segment_data, audience_data)
        
        # Create psychographic profile
        psychographic_profile = self._build_psychographic_profile(segment_data, audience_data)
        
        # Generate recommendations
        content_recommendations = self._generate_content_recommendations(segment_data)
        platform_strategies = self._generate_platform_strategies(segment_data)
        
        # Calculate metrics
        monetization_potential = self._calculate_monetization_potential(segment_data)
        confidence_score = self._calculate_confidence_score(segment_data, audience_data)
        
        return AudienceInsight(
            segment_name=segment_data['name'],
            segment_type=segment_data['type'],
            size_percentage=segment_data['size'],
            demographic_profile=demographic_profile,
            behavioral_profile=behavioral_profile,
            psychographic_profile=psychographic_profile,
            content_recommendations=content_recommendations,
            platform_strategies=platform_strategies,
            monetization_potential=monetization_potential,
            confidence_score=confidence_score,
            engagement_pattern=self._determine_engagement_pattern(segment_data)
        )
    
    def _build_demographic_profile(self, segment_data: Dict[str, Any], audience_data: Dict[str, Any]) -> DemographicProfile:
        """
Build detailed demographic profile"""
        return DemographicProfile(
            age_range=segment_data.get('criteria', {}).get('age_range', '25-34'),
            gender_distribution={'female': 0.55, 'male': 0.40, 'other': 0.05},
            location_data={'US': 0.45, 'International': 0.55},
            education_level={'college': 0.65, 'graduate': 0.25, 'other': 0.10},
            income_bracket={'mid': 0.50, 'high': 0.30, 'low': 0.20}
        )
    
    def _build_behavioral_profile(self, segment_data: Dict[str, Any], audience_data: Dict[str, Any]) -> BehavioralProfile:
        """
Build comprehensive behavioral profile"""
        return BehavioralProfile(
            content_preferences={
                ContentType.VIDEO: 0.45,
                ContentType.IMAGE: 0.30,
                ContentType.AUDIO: 0.15,
                ContentType.TEXT: 0.10
            },
            engagement_times={'weekday': [12, 18, 20], 'weekend': [10, 14, 19]},
            interaction_patterns={'like': 0.8, 'comment': 0.15, 'share': 0.05},
            content_consumption_rate=0.75,
            sharing_likelihood=0.12,
            comment_engagement=0.08
        )
    
    def _build_psychographic_profile(self, segment_data: Dict[str, Any], audience_data: Dict[str, Any]) -> PsychographicProfile:
        """
Build psychographic profile"""
        return PsychographicProfile(
            interests={'music': 0.8, 'technology': 0.6, 'lifestyle': 0.7},
            values={'authenticity': 0.9, 'creativity': 0.85, 'community': 0.75},
            lifestyle_indicators={'urban': 0.6, 'digital_native': 0.8, 'socially_conscious': 0.7},
            personality_traits={'openness': 0.75, 'conscientiousness': 0.65}
        )
    
    def _generate_content_recommendations(self, segment_data: Dict[str, Any]) -> List[str]:
        """
Generate tailored content recommendations"""
        base_recommendations = [
            "Create authentic behind-the-scenes content",
            "Share personal stories and experiences",
            "Develop educational content series",
            "Collaborate with similar creators",
            "Use trending audio and hashtags strategically"
        ]
        
        # Customize based on segment characteristics
        if 'trending_content' in segment_data.get('characteristics', []):
            base_recommendations.append("Participate in viral trends quickly")
            base_recommendations.append("Create short-form, digestible content")
        
        if 'quality_content' in segment_data.get('characteristics', []):
            base_recommendations.append("Focus on high-production value content")
            base_recommendations.append("Develop in-depth tutorials and guides")
        
        return base_recommendations[:8]
    
    def _generate_platform_strategies(self, segment_data: Dict[str, Any]) -> Dict[SocialPlatform, Dict[str, Any]]:
        """Generate platform-specific strategies"""
        return {
            SocialPlatform.INSTAGRAM: {
                'content_types': ['stories', 'reels', 'posts'],
                'posting_frequency': 'daily',
                'best_times': ['19:00', '21:00'],
                'hashtag_strategy': 'trending + niche mix'
            },
            SocialPlatform.TIKTOK: {
                'content_types': ['short_videos', 'trends'],
                'posting_frequency': '2-3x daily', 
                'best_times': ['18:00', '20:00'],
                'strategy': 'viral_potential_focus'
            }
        }
    
    def _calculate_monetization_potential(self, segment_data: Dict[str, Any]) -> float:
        """
Calculate monetization potential for segment"""
        base_potential = 0.5
        
        # Increase based on engagement characteristics
        characteristics = segment_data.get('characteristics', [])
        if 'premium_buyer' in characteristics:
            base_potential += 0.3
        if 'loyal' in characteristics:
            base_potential += 0.2
        if 'advocate' in characteristics:
            base_potential += 0.15
        
        return min(base_potential, 1.0)
    
    def _calculate_confidence_score(self, segment_data: Dict[str, Any], audience_data: Dict[str, Any]) -> float:
        """
Calculate confidence score for insights"""
        # Base confidence based on data completeness
        data_completeness = len(audience_data.keys()) / 5  # 5 expected data categories
        segment_size = segment_data.get('size', 0)
        
        # Higher confidence for larger segments with complete data
        confidence = min(data_completeness * 0.7 + segment_size * 0.3, 1.0)
        return round(confidence, 2)
    
    def _determine_engagement_pattern(self, segment_data: Dict[str, Any]) -> EngagementPattern:
        """
Determine engagement pattern for segment"""
        characteristics = segment_data.get('characteristics', [])
        
        if 'high_engagement' in characteristics:
            return EngagementPattern.HIGH_FREQUENCY
        elif 'loyal' in characteristics:
            return EngagementPattern.LOYAL_FAN
        elif 'early_adopter' in characteristics:
            return EngagementPattern.TREND_FOLLOWER
        elif 'amplifier' in characteristics:
            return EngagementPattern.SOCIAL_SHARER
        else:
            return EngagementPattern.CASUAL_BROWSER
    
    async def get_segment_performance(self, segment_id: str) -> Dict[str, float]:
        """
Get performance metrics for specific segment"""
        if segment_id in self.segment_performance:
            return self.segment_performance[segment_id]
        
        # Generate mock performance data
        performance = {
            'engagement_rate': 0.045 + hash(segment_id) % 50 / 1000,
            'conversion_rate': 0.02 + hash(segment_id) % 20 / 1000,
            'growth_rate': 0.15 + hash(segment_id) % 30 / 100,
            'retention_rate': 0.75 + hash(segment_id) % 25 / 100
        }
        
        self.segment_performance[segment_id] = performance
        return performance
    
    async def predict_audience_behavior(self, segment_id: str, time_horizon_days: int = 30) -> Dict[str, Any]:
        """
Predict future audience behavior patterns"""
        if segment_id not in self.audience_segments:
            return {}
        
        segment = self.audience_segments[segment_id]
        
        predictions = {
            'growth_forecast': {
                'expected_growth': 0.12 * (time_horizon_days / 30),
                'confidence_interval': [0.08, 0.16],
                'key_drivers': ['content_quality', 'trending_participation', 'collaboration_frequency']
            },
            'engagement_forecast': {
                'expected_rate': segment.behavioral_profile.comment_engagement * 1.1,
                'peak_periods': ['weekends', 'evenings'],
                'content_preferences_shift': {'video': +0.05, 'live': +0.03}
            },
            'monetization_readiness': {
                'timeline': f"{max(15, 30 - int(segment.monetization_potential * 20))} days",
                'recommended_strategies': ['premium_content', 'merchandise', 'brand_partnerships']
            }
        }
        
        return predictions


__all__ = [
    "AudienceInsightsAgent", 
    "AudienceInsight",
    "AudienceAnalysisRequest", 
    "DemographicProfile",
    "BehavioralProfile", 
    "PsychographicProfile",
    "AudienceSegment",
    "EngagementPattern"
]
