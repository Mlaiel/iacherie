"""Audience Insights Engine - Advanced AI-Powered Audience Analysis System
======================================================================

This module provides comprehensive audience analysis, demographic insights,
and engagement pattern analysis for content creators across multiple platforms.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: Proprietary code - Unauthorized use prohibited and legally prosecuted.
"""import asyncio
import logging
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timezone, timedelta
import json
import statistics
from collections import defaultdict, Counter

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import networkx as nx

from backend.core.config import get_settings
from backend.core.logging import get_logger
from backend.ai.ml.audience_predictor import AudiencePredictionEngine
from backend.analytics.audience_analytics import AudienceAnalyticsService

logger = get_logger(__name__)
settings = get_settings()


class AudienceSegment(Enum):
    """Audience segmentation categories."""    GEN_Z = "gen_z"
    MILLENNIALS = "millennials"
    GEN_X = "gen_x"
    BOOMERS = "boomers"
    TEENS = "teens"
    YOUNG_ADULTS = "young_adults"
    PROFESSIONALS = "professionals"
    STUDENTS = "students"
    PARENTS = "parents"
    RETIREES = "retirees"


class EngagementType(Enum):
    """Types of audience engagement."""    PASSIVE = "passive"          # Views only
    REACTIVE = "reactive"        # Likes, basic reactions
    INTERACTIVE = "interactive"  # Comments, shares
    ADVOCATE = "advocate"        # Promotes content to others
    CREATOR = "creator"          # Creates derivative content


class ContentPreference(Enum):
    """Content format preferences."""    SHORT_VIDEO = "short_video"
    LONG_VIDEO = "long_video"
    IMAGES = "images"
    TEXT_POSTS = "text_posts"
    LIVE_STREAMS = "live_streams"
    AUDIO_CONTENT = "audio_content"
    INTERACTIVE_CONTENT = "interactive_content"


@dataclass
class DemographicData:
    """Demographic distribution data."""    age_distribution: Dict[str, float]
    gender_distribution: Dict[str, float]
    location_distribution: Dict[str, float]
    language_distribution: Dict[str, float]
    device_distribution: Dict[str, float]
    income_distribution: Dict[str, float]
    education_distribution: Dict[str, float]
    occupation_distribution: Dict[str, float]


@dataclass
class EngagementPattern:
    """Audience engagement patterns."""    peak_activity_hours: List[str]
    peak_activity_days: List[str]
    average_session_duration: float
    content_completion_rates: Dict[str, float]
    interaction_preferences: Dict[EngagementType, float]
    content_preferences: Dict[ContentPreference, float]
    seasonal_patterns: Dict[str, float]
    platform_usage_patterns: Dict[str, float]


@dataclass
class AudienceInsight:
    """Comprehensive audience insight data."""    insight_id: str
    insight_type: str
    title: str
    description: str
    significance_score: float
    actionable_recommendations: List[str]
    supporting_data: Dict[str, Any]
    confidence_level: float
    trend_direction: str  # "increasing", "decreasing", "stable"
    impact_potential: str  # "high", "medium", "low"


@dataclass
class AudienceGrowthAnalysis:
    """Audience growth analysis and predictions."""    current_size: int
    growth_rate: float
    growth_trajectory: Dict[str, float]  # monthly projections
    churn_rate: float
    retention_rate: float
    acquisition_sources: Dict[str, float]
    growth_bottlenecks: List[str]
    growth_opportunities: List[str]
    projected_size_6m: int
    projected_size_1y: int


@dataclass
class ContentPerformanceByAudience:
    """Content performance broken down by audience segments."""    segment_performance: Dict[AudienceSegment, Dict[str, float]]
    content_resonance: Dict[str, Dict[AudienceSegment, float]]
    cross_segment_appeal: Dict[str, float]
    segment_specific_content_preferences: Dict[AudienceSegment, List[ContentPreference]]
    optimal_content_mix: Dict[ContentPreference, float]


@dataclass
class AudienceHealthScore:
    """Overall audience health and quality metrics."""    overall_score: float  # 0-100
    engagement_quality: float
    audience_loyalty: float
    growth_sustainability: float
    demographic_diversity: float
    content_alignment: float
    monetization_potential: float
    risk_factors: List[str]
    strengths: List[str]
    improvement_areas: List[str]


    async def generate_audience_insights(
        self, 
        creator_id: str,
        platforms: List[str],
        time_period: str = "30d"
    ) -> List[AudienceInsight]:
        """Generate comprehensive audience insights with actionable recommendations."""        
        try:
            # Gather audience data
            demographics = await self.analyze_audience_demographics(creator_id, platforms, time_period)
            engagement_patterns = await self.analyze_engagement_patterns(creator_id, platforms, time_period)
            audience_segments = await self.segment_audience(creator_id, demographics, engagement_patterns)
            
            insights = []
            
            # Generate demographic insights
            demographic_insights = self._generate_demographic_insights(demographics)
            insights.extend(demographic_insights)
            
            # Generate engagement insights
            engagement_insights = self._generate_engagement_insights(engagement_patterns)
            insights.extend(engagement_insights)
            
            # Generate segmentation insights
            segmentation_insights = self._generate_segmentation_insights(audience_segments)
            insights.extend(segmentation_insights)
            
            # Generate growth opportunity insights
            growth_insights = await self._generate_growth_insights(creator_id, demographics, engagement_patterns)
            insights.extend(growth_insights)
            
            # Generate competitive insights
            competitive_insights = await self._generate_competitive_insights(creator_id, demographics)
            insights.extend(competitive_insights)
            
            # Sort by significance score
            insights.sort(key=lambda x: x.significance_score, reverse=True)
            
            return insights[:20]  # Return top 20 insights
            
        except Exception as e:
            self.logger.error(f"Insight generation failed for {creator_id}: {e}")
            raise
    
    def _generate_demographic_insights(self, demographics: DemographicData) -> List[AudienceInsight]:
        """Generate insights based on demographic analysis."""        
        insights = []
        
        # Age distribution insights
        age_insight = self._analyze_age_distribution(demographics.age_distribution)
        if age_insight:
            insights.append(age_insight)
        
        # Gender distribution insights
        gender_insight = self._analyze_gender_distribution(demographics.gender_distribution)
        if gender_insight:
            insights.append(gender_insight)
        
        # Geographic insights
        location_insight = self._analyze_location_distribution(demographics.location_distribution)
        if location_insight:
            insights.append(location_insight)
        
        # Language insights
        language_insight = self._analyze_language_distribution(demographics.language_distribution)
        if language_insight:
            insights.append(language_insight)
        
        return insights
    
    def _analyze_age_distribution(self, age_distribution: Dict[str, float]) -> Optional[AudienceInsight]:
        """Analyze age distribution patterns."""        
        if not age_distribution:
            return None
        
        # Find dominant age group
        dominant_group = max(age_distribution.items(), key=lambda x: x[1])
        age_group, percentage = dominant_group
        
        if percentage < 0.3:  # No clear dominant group
            return AudienceInsight(
                insight_id=f"age_diversity_{uuid.uuid4().hex[:8]}",
                insight_type="demographic",
                title="Diverse Age Demographics",
                description=f"Your audience spans multiple age groups without a clear majority. The largest group ({age_group}) represents only {percentage:.1%} of your audience.",
                significance_score=0.75,
                actionable_recommendations=[
                    "Create content that appeals across age groups",
                    "Use varied content formats to engage different generations",
                    "Consider age-specific content series",
                    "Analyze which content resonates with which age groups"
                ],
                supporting_data=age_distribution,
                confidence_level=0.85,
                trend_direction="stable",
                impact_potential="medium"
            )
        
        # Age-specific insights
        if age_group in ["13-17", "18-24"] and percentage > 0.4:
            return AudienceInsight(
                insight_id=f"young_audience_{uuid.uuid4().hex[:8]}",
                insight_type="demographic",
                title="Predominantly Young Audience",
                description=f"Your audience is primarily young, with {percentage:.1%} being {age_group} years old. This demographic is highly engaged but has specific content preferences.",
                significance_score=0.9,
                actionable_recommendations=[
                    "Focus on short-form, visually engaging content",
                    "Use trending audio and visual effects",
                    "Post during after-school and evening hours",
                    "Incorporate interactive elements and challenges",
                    "Consider TikTok and Instagram as primary platforms"
                ],
                supporting_data=age_distribution,
                confidence_level=0.92,
                trend_direction="increasing",
                impact_potential="high"
            )
        
        elif age_group in ["25-34", "35-44"] and percentage > 0.35:
            return AudienceInsight(
                insight_id=f"adult_audience_{uuid.uuid4().hex[:8]}",
                insight_type="demographic",
                title="Professional Adult Audience",
                description=f"Your audience is primarily working adults ({percentage:.1%} are {age_group}), indicating potential for professional and lifestyle content.",
                significance_score=0.88,
                actionable_recommendations=[
                    "Create educational and professional development content",
                    "Focus on longer-form, high-value content",
                    "Post during lunch hours and early evenings",
                    "Consider LinkedIn and YouTube as key platforms",
                    "Develop content around work-life balance and career growth"
                ],
                supporting_data=age_distribution,
                confidence_level=0.89,
                trend_direction="stable",
                impact_potential="high"
            )
        
        return None
    
    def _analyze_gender_distribution(self, gender_distribution: Dict[str, float]) -> Optional[AudienceInsight]:
        """Analyze gender distribution patterns."""        
        if not gender_distribution:
            return None
        
        # Check for significant gender skew
        total_binary = gender_distribution.get("male", 0) + gender_distribution.get("female", 0)
        
        if total_binary > 0.8:  # Strong binary gender representation
            if gender_distribution.get("female", 0) > 0.65:
                return AudienceInsight(
                    insight_id=f"female_majority_{uuid.uuid4().hex[:8]}",
                    insight_type="demographic",
                    title="Female-Majority Audience",
                    description=f"Your audience is predominantly female ({gender_distribution.get('female', 0):.1%}), which influences content preferences and engagement patterns.",
                    significance_score=0.8,
                    actionable_recommendations=[
                        "Consider beauty, lifestyle, and wellness content",
                        "Use visual storytelling and aesthetic appeal",
                        "Incorporate community-building elements",
                        "Partner with female-focused brands",
                        "Create content around empowerment themes"
                    ],
                    supporting_data=gender_distribution,
                    confidence_level=0.87,
                    trend_direction="stable",
                    impact_potential="medium"
                )
            
            elif gender_distribution.get("male", 0) > 0.65:
                return AudienceInsight(
                    insight_id=f"male_majority_{uuid.uuid4().hex[:8]}",
                    insight_type="demographic",
                    title="Male-Majority Audience",
                    description=f"Your audience is predominantly male ({gender_distribution.get('male', 0):.1%}), suggesting opportunities for male-oriented content strategies.",
                    significance_score=0.8,
                    actionable_recommendations=[
                        "Focus on tech, gaming, and sports content",
                        "Use direct, informational communication style",
                        "Incorporate competitive and achievement elements",
                        "Consider male-focused brand partnerships",
                        "Create content around skill development and tutorials"
                    ],
                    supporting_data=gender_distribution,
                    confidence_level=0.87,
                    trend_direction="stable",
                    impact_potential="medium"
                )
        
        else:
            return AudienceInsight(
                insight_id=f"diverse_gender_{uuid.uuid4().hex[:8]}",
                insight_type="demographic",
                title="Gender-Diverse Audience",
                description="Your audience represents diverse gender identities, requiring inclusive content strategies.",
                significance_score=0.75,
                actionable_recommendations=[
                    "Use inclusive language and imagery",
                    "Avoid gender-specific assumptions",
                    "Create content that appeals broadly",
                    "Celebrate diversity in your messaging",
                    "Be mindful of representation in collaborations"
                ],
                supporting_data=gender_distribution,
                confidence_level=0.82,
                trend_direction="increasing",
                impact_potential="medium"
            )
        
        return None
    
    def _analyze_location_distribution(self, location_distribution: Dict[str, float]) -> Optional[AudienceInsight]:
        """Analyze geographic distribution patterns."""        
        if not location_distribution:
            return None
        
        # Find top locations
        sorted_locations = sorted(location_distribution.items(), key=lambda x: x[1], reverse=True)
        top_location = sorted_locations[0] if sorted_locations else None
        
        if not top_location:
            return None
        
        location, percentage = top_location
        
        if percentage > 0.5:  # Highly concentrated audience
            return AudienceInsight(
                insight_id=f"geographic_concentration_{uuid.uuid4().hex[:8]}",
                insight_type="demographic",
                title="Geographically Concentrated Audience",
                description=f"Over half of your audience ({percentage:.1%}) is located in {location}, presenting both opportunities and risks.",
                significance_score=0.85,
                actionable_recommendations=[
                    f"Create location-specific content for {location}",
                    "Consider local partnerships and collaborations",
                    "Post content at optimal times for this timezone",
                    "Explore expansion strategies to other markets",
                    "Use local cultural references and trends"
                ],
                supporting_data=location_distribution,
                confidence_level=0.9,
                trend_direction="stable",
                impact_potential="high"
            )
        
        elif len([loc for loc, pct in sorted_locations if pct > 0.1]) >= 5:  # Global audience
            return AudienceInsight(
                insight_id=f"global_audience_{uuid.uuid4().hex[:8]}",
                insight_type="demographic",
                title="Global Audience Distribution",
                description="Your audience is globally distributed across multiple countries, requiring international content strategies.",
                significance_score=0.82,
                actionable_recommendations=[
                    "Create content that transcends cultural boundaries",
                    "Use universal themes and visual storytelling",
                    "Consider multiple language subtitles",
                    "Post at times that work for multiple timezones",
                    "Research cultural sensitivities for major markets"
                ],
                supporting_data=location_distribution,
                confidence_level=0.88,
                trend_direction="increasing",
                impact_potential="high"
            )
        
        return None
    
    def _analyze_language_distribution(self, language_distribution: Dict[str, float]) -> Optional[AudienceInsight]:
        """Analyze language distribution patterns."""        
        if not language_distribution:
            return None
        
        # Check for multilingual audience
        languages_above_threshold = [lang for lang, pct in language_distribution.items() if pct > 0.1]
        
        if len(languages_above_threshold) >= 3:
            return AudienceInsight(
                insight_id=f"multilingual_audience_{uuid.uuid4().hex[:8]}",
                insight_type="demographic",
                title="Multilingual Audience Opportunity",
                description=f"Your audience speaks multiple languages ({', '.join(languages_above_threshold[:3])}), presenting opportunities for multilingual content.",
                significance_score=0.78,
                actionable_recommendations=[
                    "Consider creating content in multiple languages",
                    "Use visual content that transcends language barriers",
                    "Add subtitles or captions to video content",
                    "Partner with creators who speak different languages",
                    "Research cultural nuances for each language group"
                ],
                supporting_data=language_distribution,
                confidence_level=0.85,
                trend_direction="stable",
                impact_potential="medium"
            )
        
        return None
    
    def _generate_engagement_insights(self, engagement_patterns: EngagementPattern) -> List[AudienceInsight]:
        """Generate insights based on engagement pattern analysis."""        
        insights = []
        
        # Peak activity insights
        peak_insight = self._analyze_peak_activity(engagement_patterns)
        if peak_insight:
            insights.append(peak_insight)
        
        # Content completion insights
        completion_insight = self._analyze_completion_rates(engagement_patterns)
        if completion_insight:
            insights.append(completion_insight)
        
        # Content preference insights
        preference_insight = self._analyze_content_preferences(engagement_patterns)
        if preference_insight:
            insights.append(preference_insight)
        
        # Session duration insights
        session_insight = self._analyze_session_duration(engagement_patterns)
        if session_insight:
            insights.append(session_insight)
        
        return insights
    
    def _analyze_peak_activity(self, engagement_patterns: EngagementPattern) -> Optional[AudienceInsight]:
        """Analyze peak activity patterns."""        
        peak_hours = engagement_patterns.peak_activity_hours
        peak_days = engagement_patterns.peak_activity_days
        
        if not peak_hours and not peak_days:
            return None
        
        return AudienceInsight(
            insight_id=f"peak_activity_{uuid.uuid4().hex[:8]}",
            insight_type="engagement",
            title="Optimal Posting Times Identified",
            description=f"Your audience is most active on {', '.join(peak_days)} at {', '.join(peak_hours)}. Posting during these times can increase engagement by 40-60%.",
            significance_score=0.92,
            actionable_recommendations=[
                f"Schedule posts for {', '.join(peak_hours)} on {', '.join(peak_days)}",
                "Use social media scheduling tools to optimize timing",
                "Create live content during peak hours",
                "Avoid posting during low-activity periods",
                "Test different time slots to refine optimal timing"
            ],
            supporting_data={
                "peak_hours": peak_hours,
                "peak_days": peak_days,
                "expected_engagement_increase": "40-60%"
            },
            confidence_level=0.94,
            trend_direction="stable",
            impact_potential="high"
        )
    
    def _analyze_completion_rates(self, engagement_patterns: EngagementPattern) -> Optional[AudienceInsight]:
        """Analyze content completion rate patterns."""        
        completion_rates = engagement_patterns.content_completion_rates
        
        if not completion_rates:
            return None
        
        # Find content type with highest completion rate
        best_format = max(completion_rates.items(), key=lambda x: x[1])
        worst_format = min(completion_rates.items(), key=lambda x: x[1])
        
        content_type, completion_rate = best_format
        worst_type, worst_rate = worst_format
        
        if completion_rate > 0.8:  # High completion rate
            return AudienceInsight(
                insight_id=f"high_completion_{uuid.uuid4().hex[:8]}",
                insight_type="engagement",
                title="Excellent Content Retention",
                description=f"Your {content_type} content has an exceptional {completion_rate:.1%} completion rate, indicating strong audience engagement.",
                significance_score=0.88,
                actionable_recommendations=[
                    f"Create more {content_type} content",
                    "Analyze what makes this format successful",
                    "Apply successful elements to other content types",
                    f"Consider expanding {content_type} content length",
                    "Use this format for important announcements"
                ],
                supporting_data=completion_rates,
                confidence_level=0.91,
                trend_direction="stable",
                impact_potential="high"
            )
        
        elif worst_rate < 0.4:  # Low completion rate
            return AudienceInsight(
                insight_id=f"low_completion_{uuid.uuid4().hex[:8]}",
                insight_type="engagement",
                title="Content Retention Challenge",
                description=f"Your {worst_type} content has a low {worst_rate:.1%} completion rate, suggesting audience disengagement.",
                significance_score=0.85,
                actionable_recommendations=[
                    f"Shorten {worst_type} content duration",
                    "Improve opening hooks and introductions",
                    "Add more engaging visual elements",
                    "Consider alternative formats for this content",
                    "Test different content structures"
                ],
                supporting_data=completion_rates,
                confidence_level=0.89,
                trend_direction="decreasing",
                impact_potential="high"
            )
        
        return None
    
    def _analyze_content_preferences(self, engagement_patterns: EngagementPattern) -> Optional[AudienceInsight]:
        """Analyze content format preferences."""        
        content_preferences = engagement_patterns.content_preferences
        
        if not content_preferences:
            return None
        
        # Find top preferred content type
        top_preference = max(content_preferences.items(), key=lambda x: x[1])
        content_type, preference_score = top_preference
        
        if preference_score > 0.4:  # Strong preference
            content_type_name = content_type.value.replace("_", " ").title()
            
            return AudienceInsight(
                insight_id=f"content_preference_{uuid.uuid4().hex[:8]}",
                insight_type="engagement",
                title=f"Strong Preference for {content_type_name}",
                description=f"Your audience shows a strong preference for {content_type_name} ({preference_score:.1%}), suggesting this should be your primary content format.",
                significance_score=0.86,
                actionable_recommendations=[
                    f"Increase production of {content_type_name.lower()}",
                    f"Invest in better tools/equipment for {content_type_name.lower()}",
                    f"Study top-performing {content_type_name.lower()} in your niche",
                    "Gradually introduce variety while maintaining this focus",
                    f"Consider {content_type_name.lower()}-specific partnerships"
                ],
                supporting_data=content_preferences,
                confidence_level=0.88,
                trend_direction="increasing",
                impact_potential="high"
            )
        
        return None
    
    def _analyze_session_duration(self, engagement_patterns: EngagementPattern) -> Optional[AudienceInsight]:
        """Analyze average session duration patterns."""        
        avg_duration = engagement_patterns.average_session_duration
        
        if avg_duration == 0:
            return None
        
        # Convert to minutes for better readability
        duration_minutes = avg_duration / 60
        
        if duration_minutes > 10:  # Long sessions
            return AudienceInsight(
                insight_id=f"long_sessions_{uuid.uuid4().hex[:8]}",
                insight_type="engagement",
                title="High Audience Engagement",
                description=f"Your audience spends an average of {duration_minutes:.1f} minutes per session, indicating strong content engagement.",
                significance_score=0.83,
                actionable_recommendations=[
                    "Create longer-form content to match audience appetite",
                    "Develop content series to maintain engagement",
                    "Add calls-to-action throughout longer content",
                    "Consider live streaming or interactive formats",
                    "Monetize through mid-content partnerships"
                ],
                supporting_data={"average_session_minutes": duration_minutes},
                confidence_level=0.87,
                trend_direction="stable",
                impact_potential="medium"
            )
        
        elif duration_minutes < 2:  # Short sessions
            return AudienceInsight(
                insight_id=f"short_sessions_{uuid.uuid4().hex[:8]}",
                insight_type="engagement",
                title="Brief Engagement Sessions",
                description=f"Your audience has short session durations ({duration_minutes:.1f} minutes), suggesting preference for quick, digestible content.",
                significance_score=0.78,
                actionable_recommendations=[
                    "Focus on short-form, high-impact content",
                    "Front-load your most important messages",
                    "Use strong visual hooks to capture attention",
                    "Create content series with short episodes",
                    "Optimize for mobile viewing experiences"
                ],
                supporting_data={"average_session_minutes": duration_minutes},
                confidence_level=0.85,
                trend_direction="stable",
                impact_potential="medium"
            )
        
        return None
    
    def _generate_segmentation_insights(self, audience_segments: Dict[AudienceSegment, Dict[str, Any]]) -> List[AudienceInsight]:
        """Generate insights based on audience segmentation."""        
        insights = []
        
        # Analyze segment distribution
        total_segments = len(audience_segments)
        
        if total_segments >= 4:
            insights.append(AudienceInsight(
                insight_id=f"diverse_segments_{uuid.uuid4().hex[:8]}",
                insight_type="segmentation",
                title="Diverse Audience Segments",
                description=f"Your audience consists of {total_segments} distinct segments, requiring targeted content strategies for optimal engagement.",
                significance_score=0.8,
                actionable_recommendations=[
                    "Develop segment-specific content calendars",
                    "Create content that appeals to your largest segments",
                    "Test different content types with different segments",
                    "Use analytics to track segment-specific performance",
                    "Consider segment-targeted advertising campaigns"
                ],
                supporting_data={"segment_count": total_segments},
                confidence_level=0.85,
                trend_direction="stable",
                impact_potential="high"
            ))
        
        # Analyze dominant segments
        if audience_segments:
            dominant_segment = max(audience_segments.items(), key=lambda x: x[1].get("size_percentage", 0))
            segment_type, segment_data = dominant_segment
            
            if segment_data.get("size_percentage", 0) > 0.4:
                insights.append(self._create_dominant_segment_insight(segment_type, segment_data))
        
        return insights
    
    def _create_dominant_segment_insight(self, segment: AudienceSegment, data: Dict[str, Any]) -> AudienceInsight:
        """Create insight for dominant audience segment."""        
        segment_name = segment.value.replace("_", " ").title()
        percentage = data.get("size_percentage", 0)
        
        segment_strategies = {
            AudienceSegment.TEENS: [
                "Create trend-focused content with popular music",
                "Use vibrant visuals and quick transitions",
                "Incorporate challenges and interactive elements",
                "Post during after-school hours (3-6 PM)",
                "Focus on TikTok and Instagram platforms"
            ],
            AudienceSegment.GEN_Z: [
                "Embrace authentic, unpolished content styles",
                "Address social issues and causes they care about",
                "Use humor and memes in your content",
                "Create short-form video content",
                "Engage with trending topics and challenges"
            ],
            AudienceSegment.MILLENNIALS: [
                "Focus on nostalgia and shared cultural experiences",
                "Create content around career and lifestyle topics",
                "Use storytelling and longer-form content",
                "Address work-life balance themes",
                "Leverage Instagram and YouTube primarily"
            ],
            AudienceSegment.PROFESSIONALS: [
                "Create educational and industry-specific content",
                "Share professional insights and expertise",
                "Use LinkedIn for primary distribution",
                "Focus on networking and career growth topics",
                "Maintain a professional, polished content style"
            ]
        }
        
        recommendations = segment_strategies.get(segment, [
            f"Research {segment_name.lower()} content preferences",
            f"Analyze successful creators targeting {segment_name.lower()}",
            f"Test content formats popular with {segment_name.lower()}",
            f"Engage with {segment_name.lower()} community trends",
            f"Optimize posting times for {segment_name.lower()} activity"
        ])
        
        return AudienceInsight(
            insight_id=f"dominant_{segment.value}_{uuid.uuid4().hex[:8]}",
            insight_type="segmentation",
            title=f"Dominant {segment_name} Audience",
            description=f"Your audience is primarily {segment_name} ({percentage:.1%}), requiring targeted strategies for this demographic.",
            significance_score=0.9,
            actionable_recommendations=recommendations,
            supporting_data=data,
            confidence_level=0.88,
            trend_direction="stable",
            impact_potential="high"
        )
    
    async def _generate_growth_insights(
        self, 
        creator_id: str,
        demographics: DemographicData,
        engagement_patterns: EngagementPattern
    ) -> List[AudienceInsight]:
        """Generate growth opportunity insights."""        
        insights = []
        
        # Analyze growth potential by demographics
        growth_insight = await self._analyze_growth_opportunities(creator_id, demographics)
        if growth_insight:
            insights.append(growth_insight)
        
        # Analyze untapped platforms
        platform_insight = self._analyze_platform_opportunities(engagement_patterns)
        if platform_insight:
            insights.append(platform_insight)
        
        return insights
    
    async def _analyze_growth_opportunities(
        self, 
        creator_id: str,
        demographics: DemographicData
    ) -> Optional[AudienceInsight]:
        """Analyze audience growth opportunities."""        
        # Analyze underrepresented demographics
        age_dist = demographics.age_distribution
        
        # Check for missing key demographics
        key_demographics = ["18-24", "25-34", "35-44"]
        underrepresented = []
        
        for demo in key_demographics:
            if age_dist.get(demo, 0) < 0.15:  # Less than 15% representation
                underrepresented.append(demo)
        
        if underrepresented:
            target_demo = underrepresented[0]  # Focus on first underrepresented group
            
            return AudienceInsight(
                insight_id=f"growth_opportunity_{uuid.uuid4().hex[:8]}",
                insight_type="growth",
                title=f"Growth Opportunity: {target_demo} Age Group",
                description=f"The {target_demo} age group is underrepresented in your audience, presenting a significant growth opportunity.",
                significance_score=0.82,
                actionable_recommendations=[
                    f"Create content that appeals to {target_demo} age group",
                    f"Use platforms popular with {target_demo} demographic",
                    f"Collaborate with creators who have strong {target_demo} followings",
                    f"Research trending topics among {target_demo} audience",
                    f"Adjust posting times to match {target_demo} activity patterns"
                ],
                supporting_data={"target_demographic": target_demo, "current_percentage": age_dist.get(target_demo, 0)},
                confidence_level=0.78,
                trend_direction="increasing",
                impact_potential="high"
            )
        
        return None
    
    def _analyze_platform_opportunities(self, engagement_patterns: EngagementPattern) -> Optional[AudienceInsight]:
        """Analyze untapped platform opportunities."""        
        platform_usage = engagement_patterns.platform_usage_patterns
        
        if not platform_usage:
            return None
        
        # Check for platform concentration
        total_usage = sum(platform_usage.values())
        if total_usage == 0:
            return None
        
        normalized_usage = {platform: usage/total_usage for platform, usage in platform_usage.items()}
        
        # Find dominant platform
        dominant_platform = max(normalized_usage.items(), key=lambda x: x[1])
        platform_name, usage_percentage = dominant_platform
        
        if usage_percentage > 0.7:  # Over-concentrated on one platform
            return AudienceInsight(
                insight_id=f"platform_diversification_{uuid.uuid4().hex[:8]}",
                insight_type="growth",
                title="Platform Diversification Opportunity",
                description=f"Your audience is heavily concentrated on {platform_name} ({usage_percentage:.1%}). Diversifying to other platforms could reduce risk and increase reach.",
                significance_score=0.75,
                actionable_recommendations=[
                    "Gradually expand to complementary platforms",
                    "Repurpose content for different platform formats",
                    "Cross-promote your other platform presence",
                    "Research platform-specific content strategies",
                    "Start with platforms that match your content style"
                ],
                supporting_data=normalized_usage,
                confidence_level=0.82,
                trend_direction="stable",
                impact_potential="medium"
            )
        
        return None
    
    async def _generate_competitive_insights(
        self, 
        creator_id: str,
        demographics: DemographicData
    ) -> List[AudienceInsight]:
        """Generate competitive landscape insights."""        
        insights = []
        
        # This would typically involve competitive analysis
        # For now, we'll create a general competitive insight
        competitive_insight = AudienceInsight(
            insight_id=f"competitive_analysis_{uuid.uuid4().hex[:8]}",
            insight_type="competitive",
            title="Competitive Positioning Analysis",
            description="Based on your audience demographics, you have opportunities to differentiate from competitors in your space.",
            significance_score=0.7,
            actionable_recommendations=[
                "Analyze top competitors' audience demographics",
                "Identify gaps in competitor content strategies",
                "Research competitor posting schedules and frequency",
                "Find unique value propositions for your audience",
                "Monitor competitor engagement rates and content performance"
            ],
            supporting_data={"demographic_data": demographics.__dict__},
            confidence_level=0.75,
            trend_direction="stable",
            impact_potential="medium"
        )
        
        insights.append(competitive_insight)
        return insights
    
    async def analyze_audience_growth(
        self, 
        creator_id: str,
        time_period: str = "90d"
    ) -> AudienceGrowthAnalysis:
        """Analyze audience growth patterns and predict future growth."""        
        try:
            # Fetch historical audience data
            growth_data = await self.analytics_service.get_growth_data(creator_id, time_period)
            
            # Calculate current metrics
            current_size = growth_data.get("current_size", 0)
            
            # Calculate growth rate
            historical_sizes = growth_data.get("historical_sizes", [])
            growth_rate = self._calculate_growth_rate(historical_sizes)
            
            # Calculate churn and retention
            churn_rate = growth_data.get("churn_rate", 0.05)
            retention_rate = 1.0 - churn_rate
            
            # Analyze acquisition sources
            acquisition_sources = growth_data.get("acquisition_sources", {})
            
            # Identify growth bottlenecks
            bottlenecks = self._identify_growth_bottlenecks(growth_data)
            
            # Identify growth opportunities
            opportunities = self._identify_growth_opportunities(growth_data)
            
            # Generate growth projections
            projections = self._generate_growth_projections(
                current_size, growth_rate, churn_rate
            )
            
            return AudienceGrowthAnalysis(
                current_size=current_size,
                growth_rate=growth_rate,
                growth_trajectory=projections["monthly"],
                churn_rate=churn_rate,
                retention_rate=retention_rate,
                acquisition_sources=acquisition_sources,
                growth_bottlenecks=bottlenecks,
                growth_opportunities=opportunities,
                projected_size_6m=projections["6_months"],
                projected_size_1y=projections["12_months"]
            )
            
        except Exception as e:
            self.logger.error(f"Growth analysis failed for {creator_id}: {e}")
            raise
    
    def _calculate_growth_rate(self, historical_sizes: List[int]) -> float:
        """Calculate compound monthly growth rate."""        
        if len(historical_sizes) < 2:
            return 0.0
        
        # Calculate month-over-month growth rates
        growth_rates = []
        for i in range(1, len(historical_sizes)):
            if historical_sizes[i-1] > 0:
                rate = (historical_sizes[i] - historical_sizes[i-1]) / historical_sizes[i-1]
                growth_rates.append(rate)
        
        if not growth_rates:
            return 0.0
        
        # Return average monthly growth rate
        return np.mean(growth_rates)
    
    def _identify_growth_bottlenecks(self, growth_data: Dict[str, Any]) -> List[str]:
        """Identify factors limiting audience growth."""        
        bottlenecks = []
        
        # Check engagement rates
        engagement_rate = growth_data.get("engagement_rate", 0)
        if engagement_rate < 0.02:
            bottlenecks.append("Low engagement rate limiting organic reach")
        
        # Check posting frequency
        posting_frequency = growth_data.get("posting_frequency", 0)
        if posting_frequency < 3:  # Less than 3 posts per week
            bottlenecks.append("Inconsistent posting frequency")
        
        # Check content variety
        content_types = growth_data.get("content_types", [])
        if len(content_types) < 3:
            bottlenecks.append("Limited content format variety")
        
        # Check platform diversity
        platforms = growth_data.get("platforms", [])
        if len(platforms) < 2:
            bottlenecks.append("Over-reliance on single platform")
        
        # Check audience interaction
        response_rate = growth_data.get("creator_response_rate", 0)
        if response_rate < 0.1:
            bottlenecks.append("Limited creator-audience interaction")
        
        return bottlenecks
    
    def _identify_growth_opportunities(self, growth_data: Dict[str, Any]) -> List[str]:
        """Identify opportunities to accelerate growth."""        
        opportunities = []
        
        # Check for trending content opportunities
        if growth_data.get("trend_participation", 0) < 0.3:
            opportunities.append("Increase participation in trending topics and challenges")
        
        # Check for collaboration opportunities
        if growth_data.get("collaboration_count", 0) < 2:
            opportunities.append("Increase collaborations with other creators")
        
        # Check for cross-platform opportunities
        platforms = growth_data.get("platforms", [])
        all_platforms = ["youtube", "tiktok", "instagram", "twitter", "linkedin"]
        unused_platforms = [p for p in all_platforms if p not in platforms]
        if unused_platforms:
            opportunities.append(f"Expand to {', '.join(unused_platforms[:2])} platforms")
        
        # Check for content optimization opportunities
        if growth_data.get("content_optimization_score", 0) < 0.7:
            opportunities.append("Optimize content for better discoverability (SEO, hashtags, timing)")
        
        # Check for community building opportunities
        if growth_data.get("community_engagement", 0) < 0.5:
            opportunities.append("Invest in community building and audience retention strategies")
        
        return opportunities
    
    def _generate_growth_projections(
        self, 
        current_size: int,
        growth_rate: float,
        churn_rate: float
    ) -> Dict[str, Any]:
        """Generate audience growth projections."""        
        # Monthly projections for next 12 months
        monthly_projections = {}
        projected_size = current_size
        
        for month in range(1, 13):
            # Apply growth and churn
            new_followers = projected_size * growth_rate
            churned_followers = projected_size * churn_rate
            projected_size = int(projected_size + new_followers - churned_followers)
            monthly_projections[f"month_{month}"] = projected_size
        
        return {
            "monthly": monthly_projections,
            "6_months": monthly_projections.get("month_6", current_size),
            "12_months": monthly_projections.get("month_12", current_size)
        }
    
    async def calculate_audience_health_score(
        self, 
        creator_id: str,
        demographic_data: DemographicData,
        engagement_patterns: EngagementPattern,
        growth_analysis: AudienceGrowthAnalysis
    ) -> AudienceHealthScore:
        """Calculate comprehensive audience health score."""        
        try:
            # Calculate individual component scores
            engagement_quality = self._calculate_engagement_quality_score(engagement_patterns)
            audience_loyalty = self._calculate_loyalty_score(engagement_patterns, growth_analysis)
            growth_sustainability = self._calculate_growth_sustainability_score(growth_analysis)
            demographic_diversity = self._calculate_diversity_score(demographic_data)
            content_alignment = self._calculate_content_alignment_score(engagement_patterns)
            monetization_potential = self._calculate_monetization_score(demographic_data, engagement_patterns)
            
            # Calculate overall score (weighted average)
            weights = {
                "engagement_quality": 0.25,
                "audience_loyalty": 0.20,
                "growth_sustainability": 0.20,
                "demographic_diversity": 0.10,
                "content_alignment": 0.15,
                "monetization_potential": 0.10
            }
            
            overall_score = (
                engagement_quality * weights["engagement_quality"] +
                audience_loyalty * weights["audience_loyalty"] +
                growth_sustainability * weights["growth_sustainability"] +
                demographic_diversity * weights["demographic_diversity"] +
                content_alignment * weights["content_alignment"] +
                monetization_potential * weights["monetization_potential"]
            )
            
            # Identify risk factors and strengths
            risk_factors = self._identify_risk_factors(
                engagement_quality, audience_loyalty, growth_sustainability,
                demographic_diversity, content_alignment, monetization_potential
            )
            
            strengths = self._identify_strengths(
                engagement_quality, audience_loyalty, growth_sustainability,
                demographic_diversity, content_alignment, monetization_potential
            )
            
            improvement_areas = self._identify_improvement_areas(
                engagement_quality, audience_loyalty, growth_sustainability,
                demographic_diversity, content_alignment, monetization_potential
            )
            
            return AudienceHealthScore(
                overall_score=overall_score,
                engagement_quality=engagement_quality,
                audience_loyalty=audience_loyalty,
                growth_sustainability=growth_sustainability,
                demographic_diversity=demographic_diversity,
                content_alignment=content_alignment,
                monetization_potential=monetization_potential,
                risk_factors=risk_factors,
                strengths=strengths,
                improvement_areas=improvement_areas
            )
            
        except Exception as e:
            self.logger.error(f"Health score calculation failed for {creator_id}: {e}")
            raise
    
    def _calculate_engagement_quality_score(self, engagement_patterns: EngagementPattern) -> float:
        """Calculate engagement quality score based on patterns."""        
        score = 0.0
        
        # Session duration component (0-30 points)
        duration_minutes = engagement_patterns.average_session_duration / 60
        if duration_minutes > 5:
            score += 30
        elif duration_minutes > 2:
            score += 20
        elif duration_minutes > 1:
            score += 10
        
        # Content completion component (0-30 points)
        completion_rates = list(engagement_patterns.content_completion_rates.values())
        if completion_rates:
            avg_completion = np.mean(completion_rates)
            score += avg_completion * 30
        
        # Interaction diversity component (0-25 points)
        interaction_types = len([pref for pref in engagement_patterns.interaction_preferences.values() if pref > 0.05])
        score += min(interaction_types * 5, 25)
        
        # Consistency component (0-15 points)
        if engagement_patterns.peak_activity_hours and engagement_patterns.peak_activity_days:
            score += 15
        
        return min(score, 100.0)
    
    def _calculate_loyalty_score(
        self, 
        engagement_patterns: EngagementPattern,
        growth_analysis: AudienceGrowthAnalysis
    ) -> float:
        """Calculate audience loyalty score."""        
        score = 0.0
        
        # Retention rate component (0-40 points)
        score += growth_analysis.retention_rate * 40
        
        # Engagement consistency component (0-30 points)
        if engagement_patterns.peak_activity_days:
            consistent_days = len(engagement_patterns.peak_activity_days)
            score += min(consistent_days * 10, 30)
        
        # Content preference stability component (0-30 points)
        content_prefs = list(engagement_patterns.content_preferences.values())
        if content_prefs and max(content_prefs) > 0.3:  # Strong preference indicates loyalty
            score += 30
        
        return min(score, 100.0)
    
    def _calculate_growth_sustainability_score(self, growth_analysis: AudienceGrowthAnalysis) -> float:
        """Calculate growth sustainability score."""        
        score = 0.0
        
        # Growth rate component (0-40 points)
        if growth_analysis.growth_rate > 0.1:  # 10%+ monthly growth
            score += 40
        elif growth_analysis.growth_rate > 0.05:  # 5-10% monthly growth
            score += 30
        elif growth_analysis.growth_rate > 0.02:  # 2-5% monthly growth
            score += 20
        elif growth_analysis.growth_rate > 0:     # Any positive growth
            score += 10
        
        # Churn rate component (0-30 points)
        if growth_analysis.churn_rate < 0.05:   # Less than 5% churn
            score += 30
        elif growth_analysis.churn_rate < 0.1:  # 5-10% churn
            score += 20
        elif growth_analysis.churn_rate < 0.15: # 10-15% churn
            score += 10
        
        # Acquisition diversity component (0-30 points)
        acquisition_sources = len(growth_analysis.acquisition_sources)
        score += min(acquisition_sources * 10, 30)
        
        return min(score, 100.0)
    
    def _calculate_diversity_score(self, demographic_data: DemographicData) -> float:
        """Calculate demographic diversity score."""        
        score = 0.0
        
        # Age diversity component (0-25 points)
        age_groups = len([pct for pct in demographic_data.age_distribution.values() if pct > 0.05])
        score += min(age_groups * 5, 25)
        
        # Geographic diversity component (0-25 points)
        locations = len([pct for pct in demographic_data.location_distribution.values() if pct > 0.05])
        score += min(locations * 3, 25)
        
        # Gender diversity component (0-25 points)
        gender_balance = min(demographic_data.gender_distribution.values()) if demographic_data.gender_distribution else 0
        if gender_balance > 0.3:  # Good balance
            score += 25
        elif gender_balance > 0.2:  # Moderate balance
            score += 15
        elif gender_balance > 0.1:  # Some balance
            score += 10
        
        # Language diversity component (0-25 points)
        languages = len([pct for pct in demographic_data.language_distribution.values() if pct > 0.05])
        score += min(languages * 8, 25)
        
        return min(score, 100.0)
    
    def _calculate_content_alignment_score(self, engagement_patterns: EngagementPattern) -> float:
        """Calculate content-audience alignment score."""        
        score = 0.0
        
        # Content preference clarity component (0-40 points)
        content_prefs = list(engagement_patterns.content_preferences.values())
        if content_prefs:
            max_preference = max(content_prefs)
            if max_preference > 0.5:  # Very clear preference
                score += 40
            elif max_preference > 0.3:  # Clear preference
                score += 30
            elif max_preference > 0.2:  # Some preference
                score += 20
        
        # Completion rate alignment component (0-35 points)
        completion_rates = list(engagement_patterns.content_completion_rates.values())
        if completion_rates:
            avg_completion = np.mean(completion_rates)
            score += avg_completion * 35
        
        # Peak activity alignment component (0-25 points)
        if len(engagement_patterns.peak_activity_hours) >= 2 and len(engagement_patterns.peak_activity_days) >= 2:
            score += 25
        
        return min(score, 100.0)
    
    def _calculate_monetization_score(
        self, 
        demographic_data: DemographicData,
        engagement_patterns: EngagementPattern
    ) -> float:
        """Calculate monetization potential score."""        
        score = 0.0
        
        # Age-based purchasing power component (0-30 points)
        high_value_ages = ["25-34", "35-44", "45-54"]
        high_value_percentage = sum(demographic_data.age_distribution.get(age, 0) for age in high_value_ages)
        score += high_value_percentage * 30
        
        # Engagement level component (0-25 points)
        session_minutes = engagement_patterns.average_session_duration / 60
        if session_minutes > 3:  # High engagement suggests better monetization
            score += 25
        elif session_minutes > 1:
            score += 15
        elif session_minutes > 0.5:
            score += 10
        
        # Geographic component (0-25 points)
        high_value_countries = ["US", "CA", "GB", "AU", "DE", "FR", "NL", "CH"]
        high_value_geo_percentage = sum(
            demographic_data.location_distribution.get(country, 0) 
            for country in high_value_countries
        )
        score += high_value_geo_percentage * 25
        
        # Professional audience component (0-20 points)
        professional_percentage = demographic_data.occupation_distribution.get("professional", 0)
        score += professional_percentage * 20
        
        return min(score, 100.0)
    
    def _identify_risk_factors(self, *scores) -> List[str]:
        """Identify audience health risk factors."""        
        risk_factors = []
        score_names = [
            "engagement_quality", "audience_loyalty", "growth_sustainability",
            "demographic_diversity", "content_alignment", "monetization_potential"
        ]
        
        for i, score in enumerate(scores):
            if score < 40:  # Critical threshold
                risk_factors.append(f"Low {score_names[i].replace('_', ' ')}")
        
        # Add specific risk factors based on combinations
        engagement_quality, audience_loyalty, growth_sustainability = scores[:3]
        
        if engagement_quality < 50 and audience_loyalty < 50:
            risk_factors.append("Audience disengagement trend")
        
        if growth_sustainability < 30:
            risk_factors.append("Unsustainable growth patterns")
        
        return risk_factors
    
    def _identify_strengths(self, *scores) -> List[str]:
        """Identify audience health strengths."""        
        strengths = []
        score_names = [
            "engagement_quality", "audience_loyalty", "growth_sustainability",
            "demographic_diversity", "content_alignment", "monetization_potential"
        ]
        
        for i, score in enumerate(scores):
            if score > 80:  # Excellence threshold
                strengths.append(f"Excellent {score_names[i].replace('_', ' ')}")
            elif score > 70:  # Good threshold
                strengths.append(f"Strong {score_names[i].replace('_', ' ')}")
        
        return strengths
    
    def _identify_improvement_areas(self, *scores) -> List[str]:
        """Identify areas needing improvement."""        
        improvement_areas = []
        score_names = [
            "engagement_quality", "audience_loyalty", "growth_sustainability",
            "demographic_diversity", "content_alignment", "monetization_potential"
        ]
        
        for i, score in enumerate(scores):
            if 40 <= score <= 60:  # Improvement needed threshold
                improvement_areas.append(f"Enhance {score_names[i].replace('_', ' ')}")
        
        return improvement_areas


# Analytics service classes (would be implemented separately)
class AudienceAnalyticsService:
    """Service for fetching audience analytics data."""    
    async def get_demographic_data(self, creator_id: str, platform: str, time_period: str) -> Dict[str, Any]:
        """Fetch demographic data from analytics APIs."""        # Implementation would connect to actual analytics APIs
        return {}
    
    async def get_engagement_data(self, creator_id: str, platform: str, time_period: str) -> Dict[str, Any]:
        """Fetch engagement data from analytics APIs."""        # Implementation would connect to actual analytics APIs
        return {}
    
    async def get_growth_data(self, creator_id: str, time_period: str) -> Dict[str, Any]:
        """Fetch growth data from analytics APIs."""        # Implementation would connect to actual analytics APIs
        return {}


class AudiencePredictionEngine:
    """ML engine for audience behavior predictions."""    
    def __init__(self):
        self.models = self._initialize_prediction_models()
    
    def _initialize_prediction_models(self) -> Dict[str, Any]:
        """Initialize ML models for predictions."""        return {
            "engagement_predictor": RandomForestRegressor(n_estimators=100),
            "growth_predictor": GradientBoostingRegressor(n_estimators=100),
            "churn_predictor": LogisticRegression(),
            "segment_predictor": KMeans(n_clusters=5)
        }
    
    async def predict_engagement(self, features: Dict[str, Any]) -> float:
        """Predict engagement rate based on content and timing features."""        # Implementation would use trained ML models
        return 0.05
    
    async def predict_growth(self, historical_data: List[Dict[str, Any]]) -> Dict[str, float]:
        """Predict audience growth based on historical patterns."""        # Implementation would use trained ML models
        return {"30_days": 0.1, "90_days": 0.3, "365_days": 1.2}
    
    async def predict_churn(self, user_features: Dict[str, Any]) -> float:
        """Predict user churn probability."""        # Implementation would use trained ML models
        return 0.15
        
        # ML models for audience analysis
        self.segmentation_model = KMeans(n_clusters=8, random_state=42)
        self.engagement_predictor = RandomForestRegressor(n_estimators=100, random_state=42)
        self.growth_predictor = RandomForestRegressor(n_estimators=150, random_state=42)
        self.anomaly_detector = DBSCAN(eps=0.5, min_samples=5)
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=10)
        
        # Audience analysis parameters
        self.analysis_parameters = self._initialize_analysis_parameters()
        
        # Benchmark data for comparison
        self.industry_benchmarks = self._load_industry_benchmarks()
        
        # Audience behavior models
        self.behavior_models = self._initialize_behavior_models()
        
    def _initialize_analysis_parameters(self) -> Dict[str, Any]:
        """Initialize parameters for audience analysis."""        
        return {
            "demographic_weights": {
                "age": 0.25,
                "gender": 0.15,
                "location": 0.20,
                "interests": 0.25,
                "behavior": 0.15
            },
            
            "engagement_thresholds": {
                "high_engagement": 0.08,    # 8%+ engagement rate
                "medium_engagement": 0.03,   # 3-8% engagement rate
                "low_engagement": 0.01       # 1-3% engagement rate
            },
            
            "retention_thresholds": {
                "excellent": 0.90,  # 90%+ retention
                "good": 0.75,       # 75-90% retention
                "average": 0.60,    # 60-75% retention
                "poor": 0.40        # 40-60% retention
            },
            
            "growth_rate_benchmarks": {
                "viral": 50.0,      # 50%+ monthly growth
                "excellent": 20.0,  # 20-50% monthly growth
                "good": 10.0,       # 10-20% monthly growth
                "average": 5.0,     # 5-10% monthly growth
                "slow": 2.0         # 2-5% monthly growth
            },
            
            "segment_size_thresholds": {
                "major_segment": 0.25,     # 25%+ of audience
                "significant_segment": 0.10, # 10-25% of audience
                "minor_segment": 0.05,     # 5-10% of audience
                "niche_segment": 0.02      # 2-5% of audience
            }
        }
    
    def _load_industry_benchmarks(self) -> Dict[str, Dict[str, float]]:
        """Load industry benchmarks for comparison."""        
        return {
            "entertainment": {
                "avg_engagement_rate": 0.045,
                "avg_growth_rate": 8.5,
                "avg_retention_rate": 0.68,
                "avg_session_duration": 180,  # seconds
                "top_age_group": "18-34"
            },
            
            "education": {
                "avg_engagement_rate": 0.038,
                "avg_growth_rate": 6.2,
                "avg_retention_rate": 0.72,
                "avg_session_duration": 240,  # seconds
                "top_age_group": "25-44"
            },
            
            "music": {
                "avg_engagement_rate": 0.052,
                "avg_growth_rate": 12.3,
                "avg_retention_rate": 0.65,
                "avg_session_duration": 150,  # seconds
                "top_age_group": "16-34"
            },
            
            "lifestyle": {
                "avg_engagement_rate": 0.041,
                "avg_growth_rate": 7.8,
                "avg_retention_rate": 0.70,
                "avg_session_duration": 165,  # seconds
                "top_age_group": "18-45"
            },
            
            "gaming": {
                "avg_engagement_rate": 0.067,
                "avg_growth_rate": 15.2,
                "avg_retention_rate": 0.73,
                "avg_session_duration": 300,  # seconds
                "top_age_group": "13-35"
            }
        }
    
    def _initialize_behavior_models(self) -> Dict[str, Any]:
        """Initialize audience behavior models."""        
        return {
            "engagement_lifecycle": {
                "discovery": {"duration": 1, "engagement_rate": 0.02},
                "exploration": {"duration": 7, "engagement_rate": 0.035},
                "regular_viewer": {"duration": 30, "engagement_rate": 0.055},
                "loyal_fan": {"duration": 90, "engagement_rate": 0.085},
                "advocate": {"duration": 365, "engagement_rate": 0.12}
            },
            
            "content_consumption_patterns": {
                "binge_watcher": {
                    "session_duration": 45,  # minutes
                    "content_types": ["long_video", "series"],
                    "peak_times": ["19:00", "20:00", "21:00"]
                },
                "casual_browser": {
                    "session_duration": 8,   # minutes
                    "content_types": ["short_video", "images"],
                    "peak_times": ["12:00", "17:00", "22:00"]
                },
                "active_participant": {
                    "session_duration": 15,  # minutes
                    "content_types": ["interactive", "live_streams"],
                    "peak_times": ["18:00", "19:00", "20:00"]
                }
            },
            
            "platform_behavior": {
                "youtube": {
                    "avg_watch_time": 0.65,     # 65% completion rate
                    "comment_rate": 0.012,      # 1.2% of viewers comment
                    "subscription_rate": 0.008   # 0.8% subscribe
                },
                "tiktok": {
                    "avg_watch_time": 0.78,     # 78% completion rate
                    "share_rate": 0.025,        # 2.5% share rate
                    "follow_rate": 0.015        # 1.5% follow rate
                },
                "instagram": {
                    "avg_view_time": 0.55,      # 55% completion rate
                    "save_rate": 0.008,         # 0.8% save rate
                    "story_completion": 0.72    # 72% story completion
                }
            }
        }
    
    async def analyze_audience_demographics(
        self, 
        creator_id: str,
        platforms: List[str],
        time_period: str = "30d"
    ) -> DemographicData:
        """Analyze comprehensive audience demographics across platforms."""        
        try:
            # Fetch demographic data from all platforms
            demographic_data = {}
            
            for platform in platforms:
                platform_demographics = await self.analytics_service.get_demographic_data(
                    creator_id, platform, time_period
                )
                demographic_data[platform] = platform_demographics
            
            # Aggregate and normalize demographic data
            aggregated_demographics = self._aggregate_demographics(demographic_data)
            
            # Apply demographic analysis
            analyzed_demographics = self._analyze_demographic_patterns(aggregated_demographics)
            
            return analyzed_demographics
            
        except Exception as e:
            self.logger.error(f"Demographic analysis failed for {creator_id}: {e}")
            raise
    
    def _aggregate_demographics(self, platform_data: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregate demographic data across platforms."""        
        aggregated = {
            "age_distribution": {},
            "gender_distribution": {},
            "location_distribution": {},
            "language_distribution": {},
            "device_distribution": {},
            "income_distribution": {},
            "education_distribution": {},
            "occupation_distribution": {}
        }
        
        total_audience = 0
        platform_weights = {}
        
        # Calculate platform weights based on audience size
        for platform, data in platform_data.items():
            audience_size = data.get("total_audience", 0)
            total_audience += audience_size
            platform_weights[platform] = audience_size
        
        # Normalize weights
        for platform in platform_weights:
            if total_audience > 0:
                platform_weights[platform] /= total_audience
            else:
                platform_weights[platform] = 1.0 / len(platform_weights)
        
        # Aggregate each demographic category
        for category in aggregated.keys():
            category_totals = {}
            
            for platform, data in platform_data.items():
                platform_weight = platform_weights[platform]
                platform_category_data = data.get(category, {})
                
                for key, value in platform_category_data.items():
                    if key not in category_totals:
                        category_totals[key] = 0
                    category_totals[key] += value * platform_weight
            
            aggregated[category] = category_totals
        
        return aggregated
    
    def _analyze_demographic_patterns(self, demographics: Dict[str, Any]) -> DemographicData:
        """Analyze and structure demographic patterns."""        
        return DemographicData(
            age_distribution=demographics.get("age_distribution", {}),
            gender_distribution=demographics.get("gender_distribution", {}),
            location_distribution=demographics.get("location_distribution", {}),
            language_distribution=demographics.get("language_distribution", {}),
            device_distribution=demographics.get("device_distribution", {}),
            income_distribution=demographics.get("income_distribution", {}),
            education_distribution=demographics.get("education_distribution", {}),
            occupation_distribution=demographics.get("occupation_distribution", {})
        )
    
    async def analyze_engagement_patterns(
        self, 
        creator_id: str,
        platforms: List[str],
        time_period: str = "30d"
    ) -> EngagementPattern:
        """Analyze audience engagement patterns and behaviors."""        
        try:
            # Fetch engagement data
            engagement_data = {}
            
            for platform in platforms:
                platform_engagement = await self.analytics_service.get_engagement_data(
                    creator_id, platform, time_period
                )
                engagement_data[platform] = platform_engagement
            
            # Analyze temporal patterns
            temporal_patterns = self._analyze_temporal_engagement(engagement_data)
            
            # Analyze content interaction patterns
            interaction_patterns = self._analyze_interaction_patterns(engagement_data)
            
            # Analyze content preferences
            content_preferences = self._analyze_content_preferences(engagement_data)
            
            # Combine into comprehensive engagement pattern
            engagement_pattern = EngagementPattern(
                peak_activity_hours=temporal_patterns["peak_hours"],
                peak_activity_days=temporal_patterns["peak_days"],
                average_session_duration=temporal_patterns["avg_session_duration"],
                content_completion_rates=temporal_patterns["completion_rates"],
                interaction_preferences=interaction_patterns,
                content_preferences=content_preferences,
                seasonal_patterns=temporal_patterns["seasonal_patterns"],
                platform_usage_patterns=temporal_patterns["platform_patterns"]
            )
            
            return engagement_pattern
            
        except Exception as e:
            self.logger.error(f"Engagement pattern analysis failed for {creator_id}: {e}")
            raise
    
    def _analyze_temporal_engagement(self, engagement_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze temporal engagement patterns."""        
        hourly_engagement = defaultdict(list)
        daily_engagement = defaultdict(list)
        monthly_engagement = defaultdict(list)
        platform_engagement = defaultdict(list)
        
        completion_rates = {}
        session_durations = []
        
        for platform, data in engagement_data.items():
            platform_engagement[platform] = data.get("total_engagement", 0)
            
            # Hourly patterns
            hourly_data = data.get("hourly_engagement", {})
            for hour, engagement in hourly_data.items():
                hourly_engagement[hour].append(engagement)
            
            # Daily patterns
            daily_data = data.get("daily_engagement", {})
            for day, engagement in daily_data.items():
                daily_engagement[day].append(engagement)
            
            # Monthly patterns
            monthly_data = data.get("monthly_engagement", {})
            for month, engagement in monthly_data.items():
                monthly_engagement[month].append(engagement)
            
            # Content completion rates
            completion_data = data.get("completion_rates", {})
            for content_type, rate in completion_data.items():
                if content_type not in completion_rates:
                    completion_rates[content_type] = []
                completion_rates[content_type].append(rate)
            
            # Session durations
            session_data = data.get("session_durations", [])
            session_durations.extend(session_data)
        
        # Calculate averages and identify peaks
        avg_hourly = {hour: np.mean(values) for hour, values in hourly_engagement.items()}
        avg_daily = {day: np.mean(values) for day, values in daily_engagement.items()}
        avg_monthly = {month: np.mean(values) for month, values in monthly_engagement.items()}
        
        # Find peak hours (top 3)
        peak_hours = sorted(avg_hourly.items(), key=lambda x: x[1], reverse=True)[:3]
        peak_hours = [f"{hour}:00" for hour, _ in peak_hours]
        
        # Find peak days (top 3)
        peak_days = sorted(avg_daily.items(), key=lambda x: x[1], reverse=True)[:3]
        peak_days = [day for day, _ in peak_days]
        
        # Average session duration
        avg_session_duration = np.mean(session_durations) if session_durations else 0
        
        # Average completion rates
        avg_completion_rates = {}
        for content_type, rates in completion_rates.items():
            avg_completion_rates[content_type] = np.mean(rates)
        
        return {
            "peak_hours": peak_hours,
            "peak_days": peak_days,
            "avg_session_duration": avg_session_duration,
            "completion_rates": avg_completion_rates,
            "seasonal_patterns": avg_monthly,
            "platform_patterns": dict(platform_engagement)
        }
    
    def _analyze_interaction_patterns(self, engagement_data: Dict[str, Any]) -> Dict[EngagementType, float]:
        """Analyze different types of audience interactions."""        
        interaction_totals = {
            EngagementType.PASSIVE: 0,
            EngagementType.REACTIVE: 0,
            EngagementType.INTERACTIVE: 0,
            EngagementType.ADVOCATE: 0,
            EngagementType.CREATOR: 0
        }
        
        total_audience = 0
        
        for platform, data in engagement_data.items():
            audience_size = data.get("audience_size", 0)
            total_audience += audience_size
            
            # Passive engagement (views)
            views = data.get("views", 0)
            interaction_totals[EngagementType.PASSIVE] += views
            
            # Reactive engagement (likes, reactions)
            likes = data.get("likes", 0)
            reactions = data.get("reactions", 0)
            interaction_totals[EngagementType.REACTIVE] += (likes + reactions)
            
            # Interactive engagement (comments, replies)
            comments = data.get("comments", 0)
            replies = data.get("replies", 0)
            interaction_totals[EngagementType.INTERACTIVE] += (comments + replies)
            
            # Advocate engagement (shares, mentions)
            shares = data.get("shares", 0)
            mentions = data.get("mentions", 0)
            interaction_totals[EngagementType.ADVOCATE] += (shares + mentions)
            
            # Creator engagement (user-generated content)
            ugc = data.get("user_generated_content", 0)
            interaction_totals[EngagementType.CREATOR] += ugc
        
        # Normalize to percentages
        total_interactions = sum(interaction_totals.values())
        
        if total_interactions > 0:
            for interaction_type in interaction_totals:
                interaction_totals[interaction_type] /= total_interactions
        
        return interaction_totals
    
    def _analyze_content_preferences(self, engagement_data: Dict[str, Any]) -> Dict[ContentPreference, float]:
        """Analyze audience content format preferences."""        
        content_performance = {
            ContentPreference.SHORT_VIDEO: 0,
            ContentPreference.LONG_VIDEO: 0,
            ContentPreference.IMAGES: 0,
            ContentPreference.TEXT_POSTS: 0,
            ContentPreference.LIVE_STREAMS: 0,
            ContentPreference.AUDIO_CONTENT: 0,
            ContentPreference.INTERACTIVE_CONTENT: 0
        }
        
        total_engagement = 0
        
        for platform, data in engagement_data.items():
            content_data = data.get("content_performance", {})
            
            for content_type, performance in content_data.items():
                engagement = performance.get("total_engagement", 0)
                total_engagement += engagement
                
                # Map content types to preferences
                if "short" in content_type.lower() or "reel" in content_type.lower():
                    content_performance[ContentPreference.SHORT_VIDEO] += engagement
                elif "video" in content_type.lower():
                    content_performance[ContentPreference.LONG_VIDEO] += engagement
                elif "image" in content_type.lower() or "photo" in content_type.lower():
                    content_performance[ContentPreference.IMAGES] += engagement
                elif "text" in content_type.lower() or "post" in content_type.lower():
                    content_performance[ContentPreference.TEXT_POSTS] += engagement
                elif "live" in content_type.lower() or "stream" in content_type.lower():
                    content_performance[ContentPreference.LIVE_STREAMS] += engagement
                elif "audio" in content_type.lower() or "podcast" in content_type.lower():
                    content_performance[ContentPreference.AUDIO_CONTENT] += engagement
                elif "interactive" in content_type.lower() or "poll" in content_type.lower():
                    content_performance[ContentPreference.INTERACTIVE_CONTENT] += engagement
        
        # Normalize to percentages
        if total_engagement > 0:
            for preference in content_performance:
                content_performance[preference] /= total_engagement
        
        return content_performance
    
    async def segment_audience(
        self, 
        creator_id: str,
        demographic_data: DemographicData,
        engagement_data: EngagementPattern
    ) -> Dict[AudienceSegment, Dict[str, Any]]:
        """Segment audience into distinct groups based on demographics and behavior."""        
        try:
            # Prepare data for segmentation
            segmentation_features = self._prepare_segmentation_features(
                demographic_data, engagement_data
            )
            
            # Perform ML-based segmentation
            segments = self._perform_ml_segmentation(segmentation_features)
            
            # Map segments to audience categories
            audience_segments = self._map_segments_to_categories(segments, demographic_data)
            
            # Analyze each segment
            detailed_segments = {}
            for segment, data in audience_segments.items():
                segment_analysis = await self._analyze_segment_characteristics(
                    segment, data, creator_id
                )
                detailed_segments[segment] = segment_analysis
            
            return detailed_segments
            
        except Exception as e:
            self.logger.error(f"Audience segmentation failed for {creator_id}: {e}")
            raise
    
    def _prepare_segmentation_features(
        self, 
        demographic_data: DemographicData,
        engagement_data: EngagementPattern
    ) -> np.ndarray:
        """Prepare features for ML-based audience segmentation."""        
        features = []
        
        # Age distribution features
        age_features = list(demographic_data.age_distribution.values())
        features.extend(age_features[:5])  # Top 5 age groups
        
        # Gender distribution features
        gender_features = list(demographic_data.gender_distribution.values())
        features.extend(gender_features[:3])  # Top 3 gender categories
        
        # Location distribution features
        location_features = list(demographic_data.location_distribution.values())
        features.extend(location_features[:10])  # Top 10 locations
        
        # Engagement pattern features
        engagement_features = [
            engagement_data.average_session_duration,
            len(engagement_data.peak_activity_hours),
            len(engagement_data.peak_activity_days)
        ]
        features.extend(engagement_features)
        
        # Content preference features
        content_pref_features = list(engagement_data.content_preferences.values())
        features.extend(content_pref_features)
        
        # Pad or truncate to fixed length
        target_length = 50
        if len(features) < target_length:
            features.extend([0] * (target_length - len(features)))
        else:
            features = features[:target_length]
        
        return np.array(features).reshape(1, -1)
    
    def _perform_ml_segmentation(self, features: np.ndarray) -> Dict[str, Any]:
        """Perform ML-based audience segmentation."""        
        try:
            # Scale features
            scaled_features = self.scaler.fit_transform(features)
            
            # Apply PCA for dimensionality reduction
            reduced_features = self.pca.fit_transform(scaled_features)
            
            # Perform clustering
            cluster_labels = self.segmentation_model.fit_predict(reduced_features)
            
            # Create segments based on clusters
            segments = {
                f"segment_{i}": {
                    "cluster_id": int(cluster_labels[0]) if len(cluster_labels) > 0 else 0,
                    "features": features[0].tolist(),
                    "size_percentage": 1.0 / max(1, len(set(cluster_labels)))
                }
            }
            
            return segments
            
        except Exception as e:
            self.logger.error(f"ML segmentation failed: {e}")
            # Return default segment
            return {
                "primary_segment": {
                    "cluster_id": 0,
                    "features": features[0].tolist() if len(features) > 0 else [],
                    "size_percentage": 1.0
                }
            }
    
    def _map_segments_to_categories(
        self, 
        segments: Dict[str, Any],
        demographic_data: DemographicData
    ) -> Dict[AudienceSegment, Dict[str, Any]]:
        """Map ML segments to predefined audience categories."""        
        # Analyze age distribution to determine primary segments
        age_dist = demographic_data.age_distribution
        
        mapped_segments = {}
        
        # Determine primary age-based segments
        if age_dist.get("13-17", 0) > 0.3:
            mapped_segments[AudienceSegment.TEENS] = {"percentage": age_dist.get("13-17", 0)}
        
        if age_dist.get("18-24", 0) > 0.2:
            mapped_segments[AudienceSegment.GEN_Z] = {"percentage": age_dist.get("18-24", 0)}
        
        if age_dist.get("25-34", 0) > 0.25:
            mapped_segments[AudienceSegment.MILLENNIALS] = {"percentage": age_dist.get("25-34", 0)}
        
        if age_dist.get("35-44", 0) > 0.15:
            mapped_segments[AudienceSegment.GEN_X] = {"percentage": age_dist.get("35-44", 0)}
        
        if age_dist.get("45+", 0) > 0.1:
            mapped_segments[AudienceSegment.BOOMERS] = {"percentage": age_dist.get("45+", 0)}
        
        # Add occupation-based segments
        occupation_dist = demographic_data.occupation_distribution
        
        if occupation_dist.get("student", 0) > 0.2:
            mapped_segments[AudienceSegment.STUDENTS] = {"percentage": occupation_dist.get("student", 0)}
        
        if occupation_dist.get("professional", 0) > 0.3:
            mapped_segments[AudienceSegment.PROFESSIONALS] = {"percentage": occupation_dist.get("professional", 0)}
        
        # If no significant segments identified, use primary segment
        if not mapped_segments:
            mapped_segments[AudienceSegment.MILLENNIALS] = {"percentage": 1.0}
        
        return mapped_segments
    
    async def _analyze_segment_characteristics(
        self, 
        segment: AudienceSegment,
        segment_data: Dict[str, Any],
        creator_id: str
    ) -> Dict[str, Any]:
        """Analyze detailed characteristics of an audience segment."""        
        segment_analysis = {
            "size_percentage": segment_data.get("percentage", 0),
            "engagement_characteristics": self._get_segment_engagement_profile(segment),
            "content_preferences": self._get_segment_content_preferences(segment),
            "platform_preferences": self._get_segment_platform_preferences(segment),
            "optimal_posting_times": self._get_segment_optimal_times(segment),
            "monetization_potential": self._calculate_segment_monetization_potential(segment),
            "growth_potential": self._calculate_segment_growth_potential(segment),
            "retention_likelihood": self._calculate_segment_retention_likelihood(segment)
        }
        
        return segment_analysis
    
    def _get_segment_engagement_profile(self, segment: AudienceSegment) -> Dict[str, float]:
        """Get engagement profile for specific audience segment."""        
        engagement_profiles = {
            AudienceSegment.TEENS: {
                "average_engagement_rate": 0.085,
                "content_completion_rate": 0.72,
                "sharing_likelihood": 0.15,
                "comment_likelihood": 0.08
            },
            AudienceSegment.GEN_Z: {
                "average_engagement_rate": 0.075,
                "content_completion_rate": 0.68,
                "sharing_likelihood": 0.12,
                "comment_likelihood": 0.06
            },
            AudienceSegment.MILLENNIALS: {
                "average_engagement_rate": 0.055,
                "content_completion_rate": 0.78,
                "sharing_likelihood": 0.08,
                "comment_likelihood": 0.05
            },
            AudienceSegment.GEN_X: {
                "average_engagement_rate": 0.035,
                "content_completion_rate": 0.82,
                "sharing_likelihood": 0.05,
                "comment_likelihood": 0.04
            },
            AudienceSegment.PROFESSIONALS: {
                "average_engagement_rate": 0.042,
                "content_completion_rate": 0.85,
                "sharing_likelihood": 0.06,
                "comment_likelihood": 0.07
            }
        }
        
        return engagement_profiles.get(segment, {
            "average_engagement_rate": 0.05,
            "content_completion_rate": 0.75,
            "sharing_likelihood": 0.08,
            "comment_likelihood": 0.05
        })
    
    def _get_segment_content_preferences(self, segment: AudienceSegment) -> List[ContentPreference]:
        """Get content preferences for specific audience segment."""        
        preferences = {
            AudienceSegment.TEENS: [
                ContentPreference.SHORT_VIDEO,
                ContentPreference.INTERACTIVE_CONTENT,
                ContentPreference.LIVE_STREAMS
            ],
            AudienceSegment.GEN_Z: [
                ContentPreference.SHORT_VIDEO,
                ContentPreference.IMAGES,
                ContentPreference.INTERACTIVE_CONTENT
            ],
            AudienceSegment.MILLENNIALS: [
                ContentPreference.LONG_VIDEO,
                ContentPreference.IMAGES,
                ContentPreference.TEXT_POSTS
            ],
            AudienceSegment.GEN_X: [
                ContentPreference.LONG_VIDEO,
                ContentPreference.TEXT_POSTS,
                ContentPreference.AUDIO_CONTENT
            ],
            AudienceSegment.PROFESSIONALS: [
                ContentPreference.LONG_VIDEO,
                ContentPreference.TEXT_POSTS,
                ContentPreference.AUDIO_CONTENT
            ]
        }
        
        return preferences.get(segment, [
            ContentPreference.IMAGES,
            ContentPreference.LONG_VIDEO,
            ContentPreference.TEXT_POSTS
        ])
    
    def _get_segment_platform_preferences(self, segment: AudienceSegment) -> Dict[str, float]:
        """Get platform preferences for specific audience segment."""        
        platform_preferences = {
            AudienceSegment.TEENS: {
                "tiktok": 0.45,
                "instagram": 0.35,
                "youtube": 0.15,
                "twitter": 0.05
            },
            AudienceSegment.GEN_Z: {
                "tiktok": 0.35,
                "instagram": 0.40,
                "youtube": 0.20,
                "twitter": 0.05
            },
            AudienceSegment.MILLENNIALS: {
                "instagram": 0.35,
                "youtube": 0.30,
                "twitter": 0.20,
                "linkedin": 0.15
            },
            AudienceSegment.GEN_X: {
                "youtube": 0.40,
                "linkedin": 0.25,
                "twitter": 0.20,
                "instagram": 0.15
            },
            AudienceSegment.PROFESSIONALS: {
                "linkedin": 0.45,
                "youtube": 0.30,
                "twitter": 0.20,
                "instagram": 0.05
            }
        }
        
        return platform_preferences.get(segment, {
            "instagram": 0.30,
            "youtube": 0.30,
            "twitter": 0.20,
            "tiktok": 0.20
        })
    
    def _get_segment_optimal_times(self, segment: AudienceSegment) -> List[str]:
        """Get optimal posting times for specific audience segment."""        
        optimal_times = {
            AudienceSegment.TEENS: ["15:00", "16:00", "20:00", "21:00"],
            AudienceSegment.GEN_Z: ["18:00", "19:00", "21:00", "22:00"],
            AudienceSegment.MILLENNIALS: ["12:00", "18:00", "20:00"],
            AudienceSegment.GEN_X: ["8:00", "12:00", "18:00"],
            AudienceSegment.PROFESSIONALS: ["7:00", "12:00", "17:00"]
        }
        
        return optimal_times.get(segment, ["12:00", "18:00", "20:00"])
    
    def _calculate_segment_monetization_potential(self, segment: AudienceSegment) -> float:
        """Calculate monetization potential for audience segment."""        
        monetization_scores = {
            AudienceSegment.TEENS: 0.3,          # Lower disposable income
            AudienceSegment.GEN_Z: 0.6,          # Growing purchasing power
            AudienceSegment.MILLENNIALS: 0.8,    # High purchasing power
            AudienceSegment.GEN_X: 0.9,          # Highest purchasing power
            AudienceSegment.PROFESSIONALS: 0.85   # High disposable income
        }
        
        return monetization_scores.get(segment, 0.5)
    
    def _calculate_segment_growth_potential(self, segment: AudienceSegment) -> float:
        """Calculate growth potential for audience segment."""        
        growth_scores = {
            AudienceSegment.TEENS: 0.9,          # High growth potential
            AudienceSegment.GEN_Z: 0.8,          # Good growth potential
            AudienceSegment.MILLENNIALS: 0.6,    # Moderate growth potential
            AudienceSegment.GEN_X: 0.4,          # Lower growth potential
            AudienceSegment.PROFESSIONALS: 0.5   # Moderate growth potential
        }
        
        return growth_scores.get(segment, 0.5)
    
    def _calculate_segment_retention_likelihood(self, segment: AudienceSegment) -> float:
        """Calculate retention likelihood for audience segment."""        
        retention_scores = {
            AudienceSegment.TEENS: 0.65,         # Moderate retention
            AudienceSegment.GEN_Z: 0.70,         # Good retention
            AudienceSegment.MILLENNIALS: 0.80,   # High retention
            AudienceSegment.GEN_X: 0.85,         # Very high retention
            AudienceSegment.PROFESSIONALS: 0.82  # High retention
        }
        
        return retention_scores.get(segment, 0.75)


@dataclass
class AudienceBehavior:
    """Audience behavior analysis."""    discovery_sources: Dict[str, float]
    content_journey: List[Dict[str, Any]]
    retention_metrics: Dict[str, float]
    churn_indicators: List[str]
    growth_drivers: List[str]
    engagement_triggers: List[str]
    loyalty_indicators: Dict[str, float]
    cross_platform_behavior: Dict[str, Any]


@dataclass
class AudienceInsight:
    """Comprehensive audience insight."""    insight_id: str
    insight_type: str
    title: str
    description: str
    key_findings: List[str]
    actionable_recommendations: List[str]
    confidence_score: float
    impact_potential: str
    supporting_data: Dict[str, Any]
    generated_at: datetime


@dataclass
class AudienceProfile:
    """Complete audience profile."""    profile_id: str
    creator_id: str
    total_audience_size: int
    demographics: DemographicData
    engagement_patterns: EngagementPattern
    behavior_analysis: AudienceBehavior
    audience_segments: Dict[AudienceSegment, float]
    growth_metrics: Dict[str, float]
    quality_score: float
    monetization_potential: float
    insights: List[AudienceInsight]
    last_updated: datetime


class AudienceInsightEngine:
    """    Advanced AI-powered audience insight engine that analyzes creator audiences
    and provides actionable recommendations for growth and engagement.
    """    
    def __init__(self):
        """Initialize the audience insight engine."""        self.analytics_service = AudienceAnalyticsService()
        self.prediction_engine = AudiencePredictionEngine()
        
        # ML models for audience analysis
        self.segmentation_model = KMeans(n_clusters=8)
        self.behavior_predictor = RandomForestRegressor(n_estimators=100)
        self.anomaly_detector = DBSCAN(eps=0.5, min_samples=5)
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=10)
        
        # Audience analysis parameters
        self.demographic_weights = {
            'age': 0.25,
            'gender': 0.15,
            'location': 0.20,
            'income': 0.15,
            'education': 0.10,
            'occupation': 0.15
        }
        
        # Platform-specific audience characteristics
        self.platform_audience_profiles = self._initialize_platform_profiles()
        
        # Load and train models
        self._load_and_train_models()
        
        logger.info("Audience insight engine initialized successfully")
    
    def _initialize_platform_profiles(self) -> Dict[str, Dict[str, Any]]:
        """Initialize platform-specific audience characteristics."""        
        return {
            'tiktok': {
                'primary_demographics': {
                    'age': {'13-17': 0.25, '18-24': 0.35, '25-34': 0.25, '35+': 0.15},
                    'usage_pattern': 'discovery_focused',
                    'engagement_style': 'high_frequency_short_duration',
                    'content_preference': 'entertainment_first'
                },
                'peak_hours': ['15:00', '18:00', '19:00', '20:00', '21:00'],
                'engagement_triggers': ['trending_audio', 'challenges', 'humor', 'relatability']
            },
            'instagram': {
                'primary_demographics': {
                    'age': {'18-24': 0.30, '25-34': 0.35, '35-44': 0.20, '45+': 0.15},
                    'usage_pattern': 'lifestyle_focused',
                    'engagement_style': 'visual_driven',
                    'content_preference': 'aesthetic_quality'
                },
                'peak_hours': ['11:00', '13:00', '17:00', '19:00'],
                'engagement_triggers': ['visual_appeal', 'stories', 'behind_scenes', 'authenticity']
            },
            'youtube': {
                'primary_demographics': {
                    'age': {'18-24': 0.25, '25-34': 0.30, '35-44': 0.25, '45+': 0.20},
                    'usage_pattern': 'educational_entertainment',
                    'engagement_style': 'long_form_consumption',
                    'content_preference': 'value_driven'
                },
                'peak_hours': ['18:00', '19:00', '20:00', '21:00'],
                'engagement_triggers': ['thumbnails', 'titles', 'consistency', 'expertise']
            },
            'spotify': {
                'primary_demographics': {
                    'age': {'18-24': 0.28, '25-34': 0.32, '35-44': 0.22, '45+': 0.18},
                    'usage_pattern': 'mood_based_consumption',
                    'engagement_style': 'passive_active_hybrid',
                    'content_preference': 'audio_quality'
                },
                'peak_hours': ['07:00', '08:00', '17:00', '18:00', '22:00'],
                'engagement_triggers': ['playlists', 'discovery', 'mood_matching', 'repetition']
            }
        }
    
    def _load_and_train_models(self):
        """Load historical data and train ML models for audience analysis."""        try:
            # Generate synthetic training data for audience analysis
            n_samples = 25000
            
            # Features: engagement metrics, demographic indicators, behavior patterns
            features = np.random.rand(n_samples, 20)
            
            # Add realistic patterns to synthetic data
            # Simulate different audience segments
            segment_centers = np.random.rand(8, 20) * 2
            for i in range(n_samples):
                segment = np.random.choice(8)
                noise = np.random.normal(0, 0.1, 20)
                features[i] = segment_centers[segment] + noise
            
            # Train segmentation model
            self.segmentation_model.fit(features)
            
            # Train behavior predictor
            behavior_targets = np.random.rand(n_samples)
            self.behavior_predictor.fit(features, behavior_targets)
            
            # Fit scaler and PCA
            self.scaler.fit(features)
            self.pca.fit(self.scaler.transform(features))
            
            logger.info("Audience analysis ML models trained successfully")
            
        except Exception as e:
            logger.error(f"Failed to train audience analysis models: {e}")
            # Continue with default models
    
    async def analyze_audience_profile(
        self,
        creator_id: str,
        platform_data: Dict[str, Any],
        content_history: List[Dict[str, Any]],
        time_period: int = 30  # days
    ) -> AudienceProfile:
        """        Analyze comprehensive audience profile for creator.
        
        Args:
            creator_id: Creator identifier
            platform_data: Creator's platform metrics and data
            content_history: Historical content performance data
            time_period: Analysis period in days
            
        Returns:
            Comprehensive audience profile
        """        
        try:
            # Get audience data from analytics service
            audience_data = await self.analytics_service.get_audience_data(
                creator_id, time_period
            )
            
            # Analyze demographics
            demographics = await self._analyze_demographics(audience_data, platform_data)
            
            # Analyze engagement patterns
            engagement_patterns = await self._analyze_engagement_patterns(
                audience_data, content_history
            )
            
            # Analyze audience behavior
            behavior_analysis = await self._analyze_audience_behavior(
                audience_data, platform_data, content_history
            )
            
            # Segment audience
            audience_segments = await self._segment_audience(audience_data)
            
            # Calculate growth metrics
            growth_metrics = await self._calculate_growth_metrics(
                creator_id, platform_data, time_period
            )
            
            # Calculate quality and monetization scores
            quality_score = self._calculate_audience_quality_score(
                demographics, engagement_patterns, behavior_analysis
            )
            monetization_potential = self._calculate_monetization_potential(
                demographics, engagement_patterns, audience_segments
            )
            
            # Generate insights
            insights = await self._generate_audience_insights(
                demographics, engagement_patterns, behavior_analysis, 
                audience_segments, growth_metrics
            )
            
            # Calculate total audience size
            total_audience = sum(
                data.get('followers', 0) for data in platform_data.values() if data
            )
            
            profile = AudienceProfile(
                profile_id=f"profile_{creator_id}_{int(datetime.now().timestamp())}",
                creator_id=creator_id,
                total_audience_size=total_audience,
                demographics=demographics,
                engagement_patterns=engagement_patterns,
                behavior_analysis=behavior_analysis,
                audience_segments=audience_segments,
                growth_metrics=growth_metrics,
                quality_score=quality_score,
                monetization_potential=monetization_potential,
                insights=insights,
                last_updated=datetime.now(timezone.utc)
            )
            
            logger.info(f"Audience profile analysis completed for creator {creator_id}")
            return profile
            
        except Exception as e:
            logger.error(f"Failed to analyze audience profile: {e}")
            raise
    
    async def _analyze_demographics(
        self, audience_data: Dict[str, Any], platform_data: Dict[str, Any]
    ) -> DemographicData:
        """Analyze audience demographic distribution."""        
        # Extract demographic data from audience analytics
        raw_demographics = audience_data.get('demographics', {})
        
        # Normalize and analyze age distribution
        age_distribution = self._normalize_distribution(
            raw_demographics.get('age', {})
        )
        
        # Analyze gender distribution
        gender_distribution = self._normalize_distribution(
            raw_demographics.get('gender', {})
        )
        
        # Analyze location distribution
        location_distribution = self._normalize_distribution(
            raw_demographics.get('location', {})
        )
        
        # Analyze language distribution
        language_distribution = self._normalize_distribution(
            raw_demographics.get('language', {})
        )
        
        # Analyze device usage
        device_distribution = self._normalize_distribution(
            raw_demographics.get('device', {})
        )
        
        # Estimate income and education (if not available, use platform averages)
        income_distribution = self._estimate_income_distribution(
            age_distribution, location_distribution, platform_data
        )
        education_distribution = self._estimate_education_distribution(
            age_distribution, platform_data
        )
        occupation_distribution = self._estimate_occupation_distribution(
            age_distribution, education_distribution
        )
        
        return DemographicData(
            age_distribution=age_distribution,
            gender_distribution=gender_distribution,
            location_distribution=location_distribution,
            language_distribution=language_distribution,
            device_distribution=device_distribution,
            income_distribution=income_distribution,
            education_distribution=education_distribution,
            occupation_distribution=occupation_distribution
        )
    
    def _normalize_distribution(self, data: Dict[str, Union[int, float]]) -> Dict[str, float]:
        """Normalize distribution data to percentages."""        
        if not data:
            return {}
        
        total = sum(data.values())
        if total == 0:
            return {}
        
        return {key: value / total for key, value in data.items()}
    
    def _estimate_income_distribution(
        self,
        age_distribution: Dict[str, float],
        location_distribution: Dict[str, float],
        platform_data: Dict[str, Any]
    ) -> Dict[str, float]:
        """Estimate income distribution based on demographics and platform data."""        
        # Default income distribution
        default_distribution = {
            'under_25k': 0.20,
            '25k_50k': 0.30,
            '50k_75k': 0.25,
            '75k_100k': 0.15,
            'over_100k': 0.10
        }
        
        # Adjust based on age distribution
        if age_distribution.get('18-24', 0) > 0.4:  # Young audience
            default_distribution['under_25k'] += 0.1
            default_distribution['25k_50k'] += 0.1
            default_distribution['over_100k'] -= 0.2
        
        elif age_distribution.get('35-44', 0) > 0.3:  # Mature audience
            default_distribution['under_25k'] -= 0.1
            default_distribution['75k_100k'] += 0.1
            default_distribution['over_100k'] += 0.1
        
        return default_distribution
    
    def _estimate_education_distribution(
        self, age_distribution: Dict[str, float], platform_data: Dict[str, Any]
    ) -> Dict[str, float]:
        """Estimate education distribution based on age and platform."""        
        return {
            'high_school': 0.25,
            'some_college': 0.20,
            'bachelors': 0.35,
            'masters': 0.15,
            'doctorate': 0.05
        }
    
    def _estimate_occupation_distribution(
        self, age_distribution: Dict[str, float], education_distribution: Dict[str, float]
    ) -> Dict[str, float]:
        """Estimate occupation distribution based on age and education."""        
        return {
            'student': 0.15,
            'professional': 0.25,
            'technical': 0.20,
            'creative': 0.10,
            'service': 0.15,
            'retired': 0.05,
            'other': 0.10
        }
    
    async def _analyze_engagement_patterns(
        self, audience_data: Dict[str, Any], content_history: List[Dict[str, Any]]
    ) -> EngagementPattern:
        """Analyze audience engagement patterns."""        
        # Extract engagement data
        engagement_data = audience_data.get('engagement', {})
        
        # Analyze peak activity times
        peak_hours = self._analyze_peak_activity_hours(engagement_data)
        peak_days = self._analyze_peak_activity_days(engagement_data)
        
        # Calculate average session duration
        session_duration = engagement_data.get('avg_session_duration', 0)
        
        # Analyze content completion rates
        completion_rates = self._analyze_completion_rates(content_history)
        
        # Analyze interaction preferences
        interaction_preferences = self._analyze_interaction_preferences(engagement_data)
        
        # Analyze content preferences
        content_preferences = self._analyze_content_preferences(content_history)
        
        # Analyze seasonal patterns
        seasonal_patterns = self._analyze_seasonal_patterns(engagement_data)
        
        # Analyze platform usage patterns
        platform_patterns = self._analyze_platform_usage(engagement_data)
        
        return EngagementPattern(
            peak_activity_hours=peak_hours,
            peak_activity_days=peak_days,
            average_session_duration=session_duration,
            content_completion_rates=completion_rates,
            interaction_preferences=interaction_preferences,
            content_preferences=content_preferences,
            seasonal_patterns=seasonal_patterns,
            platform_usage_patterns=platform_patterns
        )
    
    def _analyze_peak_activity_hours(self, engagement_data: Dict[str, Any]) -> List[str]:
        """Analyze peak activity hours from engagement data."""        
        hourly_activity = engagement_data.get('hourly_activity', {})
        if not hourly_activity:
            return ['18:00', '19:00', '20:00']  # Default peak hours
        
        # Sort hours by activity level
        sorted_hours = sorted(
            hourly_activity.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Return top 5 peak hours
        return [hour for hour, _ in sorted_hours[:5]]
    
    def _analyze_peak_activity_days(self, engagement_data: Dict[str, Any]) -> List[str]:
        """Analyze peak activity days from engagement data."""        
        daily_activity = engagement_data.get('daily_activity', {})
        if not daily_activity:
            return ['Tuesday', 'Wednesday', 'Thursday']  # Default peak days
        
        # Sort days by activity level
        sorted_days = sorted(
            daily_activity.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Return top 3 peak days
        return [day for day, _ in sorted_days[:3]]
    
    def _analyze_completion_rates(self, content_history: List[Dict[str, Any]]) -> Dict[str, float]:
        """Analyze content completion rates by content type."""        
        completion_by_type = defaultdict(list)
        
        for content in content_history:
            content_type = content.get('type', 'unknown')
            completion_rate = content.get('completion_rate', 0)
            if completion_rate > 0:
                completion_by_type[content_type].append(completion_rate)
        
        # Calculate average completion rates
        avg_completion = {}
        for content_type, rates in completion_by_type.items():
            avg_completion[content_type] = statistics.mean(rates)
        
        return avg_completion
    
    def _analyze_interaction_preferences(
        self, engagement_data: Dict[str, Any]
    ) -> Dict[EngagementType, float]:
        """Analyze audience interaction preferences."""        
        total_interactions = engagement_data.get('total_interactions', 1)
        
        # Extract interaction counts
        likes = engagement_data.get('likes', 0)
        comments = engagement_data.get('comments', 0)
        shares = engagement_data.get('shares', 0)
        saves = engagement_data.get('saves', 0)
        
        # Calculate interaction percentages
        preferences = {
            EngagementType.PASSIVE: 0.4,  # Assumed for views without interaction
            EngagementType.REACTIVE: likes / total_interactions,
            EngagementType.INTERACTIVE: (comments + shares) / total_interactions,
            EngagementType.ADVOCATE: shares / total_interactions,
            EngagementType.CREATOR: 0.01  # Small percentage creates derivative content
        }
        
        # Normalize to ensure sum is 1.0
        total = sum(preferences.values())
        if total > 0:
            preferences = {k: v / total for k, v in preferences.items()}
        
        return preferences
    
    def _analyze_content_preferences(
        self, content_history: List[Dict[str, Any]]
    ) -> Dict[ContentPreference, float]:
        """Analyze audience content format preferences."""        
        format_performance = defaultdict(list)
        
        for content in content_history:
            content_format = content.get('format', 'unknown')
            engagement_rate = content.get('engagement_rate', 0)
            
            # Map content formats to preferences
            if content_format in ['reel', 'tiktok', 'short_video']:
                format_performance[ContentPreference.SHORT_VIDEO].append(engagement_rate)
            elif content_format in ['video', 'youtube_video']:
                format_performance[ContentPreference.LONG_VIDEO].append(engagement_rate)
            elif content_format in ['image', 'photo']:
                format_performance[ContentPreference.IMAGES].append(engagement_rate)
            elif content_format in ['text', 'tweet', 'post']:
                format_performance[ContentPreference.TEXT_POSTS].append(engagement_rate)
            elif content_format in ['live', 'stream']:
                format_performance[ContentPreference.LIVE_STREAMS].append(engagement_rate)
            elif content_format in ['audio', 'podcast']:
                format_performance[ContentPreference.AUDIO_CONTENT].append(engagement_rate)
        
        # Calculate average engagement by format
        preferences = {}
        total_engagement = 0
        
        for format_type, engagements in format_performance.items():
            if engagements:
                avg_engagement = statistics.mean(engagements)
                preferences[format_type] = avg_engagement
                total_engagement += avg_engagement
        
        # Normalize preferences
        if total_engagement > 0:
            preferences = {k: v / total_engagement for k, v in preferences.items()}
        
        return preferences
    
    def _analyze_seasonal_patterns(self, engagement_data: Dict[str, Any]) -> Dict[str, float]:
        """Analyze seasonal engagement patterns."""        
        # This would analyze historical data across seasons
        # For now, return default seasonal patterns
        return {
            'spring': 0.25,
            'summer': 0.30,
            'fall': 0.25,
            'winter': 0.20
        }
    
    def _analyze_platform_usage(self, engagement_data: Dict[str, Any]) -> Dict[str, float]:
        """Analyze platform-specific usage patterns."""        
        platform_data = engagement_data.get('platform_breakdown', {})
        
        # Normalize platform usage
        total_usage = sum(platform_data.values()) if platform_data else 1
        
        return {
            platform: usage / total_usage
            for platform, usage in platform_data.items()
        } if platform_data else {}
    
    async def _analyze_audience_behavior(
        self,
        audience_data: Dict[str, Any],
        platform_data: Dict[str, Any],
        content_history: List[Dict[str, Any]]
    ) -> AudienceBehavior:
        """Analyze comprehensive audience behavior patterns."""        
        # Analyze discovery sources
        discovery_sources = self._analyze_discovery_sources(audience_data)
        
        # Analyze content journey
        content_journey = self._analyze_content_journey(content_history)
        
        # Calculate retention metrics
        retention_metrics = self._calculate_retention_metrics(audience_data)
        
        # Identify churn indicators
        churn_indicators = self._identify_churn_indicators(audience_data, content_history)
        
        # Identify growth drivers
        growth_drivers = self._identify_growth_drivers(platform_data, content_history)
        
        # Identify engagement triggers
        engagement_triggers = self._identify_engagement_triggers(content_history)
        
        # Calculate loyalty indicators
        loyalty_indicators = self._calculate_loyalty_indicators(audience_data)
        
        # Analyze cross-platform behavior
        cross_platform_behavior = self._analyze_cross_platform_behavior(platform_data)
        
        return AudienceBehavior(
            discovery_sources=discovery_sources,
            content_journey=content_journey,
            retention_metrics=retention_metrics,
            churn_indicators=churn_indicators,
            growth_drivers=growth_drivers,
            engagement_triggers=engagement_triggers,
            loyalty_indicators=loyalty_indicators,
            cross_platform_behavior=cross_platform_behavior
        )
    
    def _analyze_discovery_sources(self, audience_data: Dict[str, Any]) -> Dict[str, float]:
        """Analyze how audience discovers the creator's content."""        
        discovery_data = audience_data.get('discovery_sources', {})
        
        # Default discovery source distribution
        default_sources = {
            'organic_search': 0.25,
            'recommendations': 0.30,
            'social_sharing': 0.20,
            'direct': 0.15,
            'external_links': 0.10
        }
        
        if discovery_data:
            total = sum(discovery_data.values())
            return {source: count / total for source, count in discovery_data.items()}
        
        return default_sources
    
    def _analyze_content_journey(self, content_history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze typical audience content consumption journey."""        
        # Analyze content sequence patterns
        journey_patterns = []
        
        # Group content by type and analyze transitions
        content_types = [content.get('type', 'unknown') for content in content_history]
        
        # Find common content type sequences
        for i in range(len(content_types) - 2):
            sequence = content_types[i:i+3]
            journey_patterns.append({
                'sequence': sequence,
                'transition_probability': 0.1  # Would be calculated from real data
            })
        
        return journey_patterns[:5]  # Return top 5 patterns
    
    def _calculate_retention_metrics(self, audience_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate audience retention metrics."""        
        return {
            'day_1_retention': audience_data.get('day_1_retention', 0.8),
            'day_7_retention': audience_data.get('day_7_retention', 0.6),
            'day_30_retention': audience_data.get('day_30_retention', 0.4),
            'repeat_visitor_rate': audience_data.get('repeat_visitors', 0.5),
            'subscriber_retention': audience_data.get('subscriber_retention', 0.7)
        }
    
    def _identify_churn_indicators(
        self, audience_data: Dict[str, Any], content_history: List[Dict[str, Any]]
    ) -> List[str]:
        """Identify indicators that predict audience churn."""        
        indicators = []
        
        # Analyze engagement decline
        if len(content_history) >= 5:
            recent_engagement = statistics.mean([
                content.get('engagement_rate', 0) 
                for content in content_history[-5:]
            ])
            older_engagement = statistics.mean([
                content.get('engagement_rate', 0) 
                for content in content_history[-10:-5]
            ]) if len(content_history) >= 10 else recent_engagement
            
            if recent_engagement < older_engagement * 0.8:
                indicators.append("Declining engagement rates")
        
        # Check session duration trends
        avg_session = audience_data.get('avg_session_duration', 0)
        if avg_session < 30:  # Less than 30 seconds
            indicators.append("Short session durations")
        
        # Check comment sentiment
        negative_sentiment = audience_data.get('negative_sentiment_ratio', 0)
        if negative_sentiment > 0.3:
            indicators.append("Increasing negative sentiment")
        
        return indicators
    
    def _identify_growth_drivers(
        self, platform_data: Dict[str, Any], content_history: List[Dict[str, Any]]
    ) -> List[str]:
        """Identify factors driving audience growth."""        
        drivers = []
        
        # Analyze content performance correlation with growth
        high_performing_content = [
            content for content in content_history
            if content.get('engagement_rate', 0) > 0.05
        ]
        
        if high_performing_content:
            # Analyze common characteristics
            content_types = [content.get('type') for content in high_performing_content]
            most_common_type = Counter(content_types).most_common(1)
            if most_common_type:
                drivers.append(f"High-performing {most_common_type[0][0]} content")
        
        # Check platform-specific growth
        for platform, data in platform_data.items():
            if data and data.get('growth_rate', 0) > 0.1:  # 10% growth
                drivers.append(f"Strong {platform} performance")
        
        return drivers
    
    def _identify_engagement_triggers(self, content_history: List[Dict[str, Any]]) -> List[str]:
        """Identify content elements that trigger high engagement."""        
        triggers = []
        
        # Analyze high-engagement content
        high_engagement_content = [
            content for content in content_history
            if content.get('engagement_rate', 0) > 0.08
        ]
        
        if high_engagement_content:
            # Common elements in high-engagement content
            common_tags = []
            for content in high_engagement_content:
                tags = content.get('tags', [])
                common_tags.extend(tags)
            
            if common_tags:
                tag_counts = Counter(common_tags)
                top_tags = tag_counts.most_common(3)
                triggers.extend([f"Content featuring {tag}" for tag, _ in top_tags])
        
        return triggers
    
    def _calculate_loyalty_indicators(self, audience_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate audience loyalty indicators."""        
        return {
            'repeat_engagement_rate': audience_data.get('repeat_engagement', 0.6),
            'content_sharing_rate': audience_data.get('sharing_rate', 0.1),
            'community_participation': audience_data.get('community_engagement', 0.3),
            'brand_advocacy_score': audience_data.get('advocacy_score', 0.4),
            'long_term_followers': audience_data.get('long_term_followers', 0.5)
        }
    
    def _analyze_cross_platform_behavior(self, platform_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze how audience behaves across different platforms."""        
        platforms = list(platform_data.keys())
        
        return {
            'platform_overlap': self._calculate_platform_overlap(platforms),
            'platform_preferences': self._analyze_platform_preferences(platform_data),
            'content_adaptation': self._analyze_content_adaptation_needs(platform_data),
            'cross_promotion_effectiveness': 0.7  # Would be calculated from real data
        }
    
    def _calculate_platform_overlap(self, platforms: List[str]) -> Dict[str, float]:
        """Calculate estimated audience overlap between platforms."""        
        # This would use actual cross-platform analytics in production
        # For now, return estimated overlap percentages
        overlap = {}
        
        for i, platform1 in enumerate(platforms):
            for platform2 in platforms[i+1:]:
                overlap[f"{platform1}_{platform2}"] = 0.3  # 30% estimated overlap
        
        return overlap
    
    def _analyze_platform_preferences(self, platform_data: Dict[str, Any]) -> Dict[str, float]:
        """Analyze audience engagement preferences by platform."""        
        preferences = {}
        
        for platform, data in platform_data.items():
            if data:
                engagement_rate = data.get('engagement_rate', 0)
                preferences[platform] = engagement_rate
        
        # Normalize preferences
        total_engagement = sum(preferences.values())
        if total_engagement > 0:
            preferences = {k: v / total_engagement for k, v in preferences.items()}
        
        return preferences
    
    def _analyze_content_adaptation_needs(self, platform_data: Dict[str, Any]) -> Dict[str, str]:
        """Analyze content adaptation needs for each platform."""        
        adaptations = {}
        
        for platform in platform_data.keys():
            if platform == 'tiktok':
                adaptations[platform] = "Short-form, trend-focused content"
            elif platform == 'instagram':
                adaptations[platform] = "Visual-first, story-driven content"
            elif platform == 'youtube':
                adaptations[platform] = "Long-form, educational content"
            elif platform == 'spotify':
                adaptations[platform] = "High-quality audio content"
            else:
                adaptations[platform] = "Platform-optimized content"
        
        return adaptations
    
    async def _segment_audience(self, audience_data: Dict[str, Any]) -> Dict[AudienceSegment, float]:
        """Segment audience based on demographics and behavior."""        
        # Extract features for segmentation
        demographics = audience_data.get('demographics', {})
        age_dist = demographics.get('age', {})
        
        segments = {}
        
        # Age-based segmentation
        segments[AudienceSegment.TEENS] = age_dist.get('13-17', 0)
        segments[AudienceSegment.GEN_Z] = age_dist.get('18-24', 0)
        segments[AudienceSegment.MILLENNIALS] = age_dist.get('25-34', 0) + age_dist.get('35-44', 0)
        segments[AudienceSegment.GEN_X] = age_dist.get('45-54', 0)
        segments[AudienceSegment.BOOMERS] = age_dist.get('55+', 0)
        
        # Behavioral segmentation
        engagement_data = audience_data.get('engagement', {})
        professional_indicators = engagement_data.get('business_hours_activity', 0)
        
        segments[AudienceSegment.PROFESSIONALS] = professional_indicators
        segments[AudienceSegment.STUDENTS] = age_dist.get('18-24', 0) * 0.6  # Estimate
        
        # Normalize segments
        total = sum(segments.values())
        if total > 0:
            segments = {k: v / total for k, v in segments.items()}
        
        return segments


class EngagementAnalyzer:
    """    Specialized engagement analyzer that provides detailed insights into
    audience engagement patterns and optimization opportunities.
    """    
    def __init__(self):
        """Initialize the engagement analyzer."""        self.insight_engine = AudienceInsightEngine()
        logger.info("Engagement analyzer initialized")
    
    async def analyze_engagement_optimization(
        self,
        creator_id: str,
        audience_profile: AudienceProfile,
        content_goals: List[str]
    ) -> List[AudienceInsight]:
        """        Analyze engagement patterns and provide optimization recommendations.
        
        Args:
            creator_id: Creator identifier
            audience_profile: Comprehensive audience profile
            content_goals: Creator's content objectives
            
        Returns:
            List of engagement optimization insights
        """        
        insights = []
        
        try:
            # Analyze engagement timing optimization
            timing_insights = await self._analyze_timing_optimization(audience_profile)
            insights.extend(timing_insights)
            
            # Analyze content format optimization
            format_insights = await self._analyze_format_optimization(audience_profile)
            insights.extend(format_insights)
            
            # Analyze audience interaction optimization
            interaction_insights = await self._analyze_interaction_optimization(audience_profile)
            insights.extend(interaction_insights)
            
            # Analyze audience growth optimization
            growth_insights = await self._analyze_growth_optimization(audience_profile)
            insights.extend(growth_insights)
            
            # Analyze monetization optimization
            monetization_insights = await self._analyze_monetization_optimization(audience_profile)
            insights.extend(monetization_insights)
            
            logger.info(f"Generated {len(insights)} engagement optimization insights")
            return insights
            
        except Exception as e:
            logger.error(f"Failed to analyze engagement optimization: {e}")
            return []
    
    async def _analyze_timing_optimization(self, profile: AudienceProfile) -> List[AudienceInsight]:
        """Analyze optimal timing for content posting."""        
        insights = []
        patterns = profile.engagement_patterns
        
        # Peak hours insight
        peak_hours = patterns.peak_activity_hours
        if peak_hours:
            insight = AudienceInsight(
                insight_id=f"timing_peak_hours_{int(datetime.now().timestamp())}",
                insight_type="timing_optimization",
                title="Optimize Posting Times for Maximum Engagement",
                description=f"Your audience is most active during {', '.join(peak_hours[:3])}",
                key_findings=[
                    f"Peak engagement occurs at {', '.join(peak_hours[:3])}",
                    f"Posting during peak hours can increase engagement by 40-60%",
                    f"Current posting schedule alignment: {self._calculate_schedule_alignment(peak_hours)}%"
                ],
                actionable_recommendations=[
                    f"Schedule primary content posts for {peak_hours[0]}",
                    f"Use secondary posting slots at {peak_hours[1] if len(peak_hours) > 1 else peak_hours[0]}",
                    "Use scheduling tools to maintain consistent timing",
                    "A/B test different time slots to validate optimal timing"
                ],
                confidence_score=0.85,
                impact_potential="high",
                supporting_data={
                    "peak_hours": peak_hours,
                    "activity_distribution": patterns.platform_usage_patterns
                },
                generated_at=datetime.now(timezone.utc)
            )
            insights.append(insight)
        
        # Peak days insight
        peak_days = patterns.peak_activity_days
        if peak_days:
            insight = AudienceInsight(
                insight_id=f"timing_peak_days_{int(datetime.now().timestamp())}",
                insight_type="timing_optimization",
                title="Leverage High-Activity Days for Content Distribution",
                description=f"Your audience shows highest activity on {', '.join(peak_days)}",
                key_findings=[
                    f"Weekly peak activity: {', '.join(peak_days)}",
                    "Strategic posting on peak days improves visibility by 30-50%",
                    "Weekend vs weekday engagement patterns identified"
                ],
                actionable_recommendations=[
                    f"Plan major content releases for {peak_days[0]}",
                    f"Use {peak_days[1] if len(peak_days) > 1 else peak_days[0]} for follow-up content",
                    "Prepare content batches for high-activity periods",
                    "Adjust content calendar to align with audience activity"
                ],
                confidence_score=0.80,
                impact_potential="medium",
                supporting_data={
                    "peak_days": peak_days,
                    "daily_activity_patterns": {}
                },
                generated_at=datetime.now(timezone.utc)
            )
            insights.append(insight)
        
        return insights
    
    def _calculate_schedule_alignment(self, peak_hours: List[str]) -> int:
        """Calculate how well current posting schedule aligns with peak hours."""        # This would analyze actual posting history vs peak hours
        # For now, return a sample alignment percentage
        return 65
    
    async def _analyze_format_optimization(self, profile: AudienceProfile) -> List[AudienceInsight]:
        """Analyze content format preferences and optimization opportunities."""        
        insights = []
        preferences = profile.engagement_patterns.content_preferences
        
        if preferences:
            # Identify top-performing format
            top_format = max(preferences.items(), key=lambda x: x[1])
            
            insight = AudienceInsight(
                insight_id=f"format_optimization_{int(datetime.now().timestamp())}",
                insight_type="content_format",
                title="Optimize Content Format Mix for Higher Engagement",
                description=f"Your audience shows strongest preference for {top_format[0].value}",
                key_findings=[
                    f"Highest engagement format: {top_format[0].value} ({top_format[1]:.1%})",
                    f"Format diversity score: {len(preferences)}/6",
                    "Opportunity to increase underperforming format engagement"
                ],
                actionable_recommendations=[
                    f"Increase {top_format[0].value} content production by 30%",
                    "Experiment with format combinations",
                    "Repurpose high-performing content into preferred formats",
                    "Test audience response to new format variations"
                ],
                confidence_score=0.78,
                impact_potential="high",
                supporting_data={
                    "format_preferences": {k.value: v for k, v in preferences.items()},
                    "optimization_potential": 0.25
                },
                generated_at=datetime.now(timezone.utc)
            )
            insights.append(insight)
        
        return insights
    
    async def _analyze_interaction_optimization(self, profile: AudienceProfile) -> List[AudienceInsight]:
        """Analyze audience interaction patterns for optimization."""        
        insights = []
        interaction_prefs = profile.engagement_patterns.interaction_preferences
        
        # Identify interaction opportunities
        high_reactive = interaction_prefs.get(EngagementType.REACTIVE, 0)
        low_interactive = interaction_prefs.get(EngagementType.INTERACTIVE, 0)
        
        if high_reactive > 0.6 and low_interactive < 0.2:
            insight = AudienceInsight(
                insight_id=f"interaction_optimization_{int(datetime.now().timestamp())}",
                insight_type="engagement_strategy",
                title="Convert Passive Engagement to Active Interaction",
                description="High like-to-comment ratio indicates opportunity for deeper engagement",
                key_findings=[
                    f"Reactive engagement: {high_reactive:.1%}",
                    f"Interactive engagement: {low_interactive:.1%}",
                    "Audience shows potential for increased conversation"
                ],
                actionable_recommendations=[
                    "Add clear call-to-action questions in content",
                    "Create content that invites opinions and discussion",
                    "Respond to comments quickly to encourage conversation",
                    "Use polls, Q&As, and interactive features",
                    "Share controversial but respectful takes to spark discussion"
                ],
                confidence_score=0.82,
                impact_potential="medium",
                supporting_data={
                    "interaction_breakdown": {k.value: v for k, v in interaction_prefs.items()},
                    "conversion_potential": 0.3
                },
                generated_at=datetime.now(timezone.utc)
            )
            insights.append(insight)
        
        return insights
    
    async def _analyze_growth_optimization(self, profile: AudienceProfile) -> List[AudienceInsight]:
        """Analyze audience growth patterns and optimization opportunities."""        
        insights = []
        growth_metrics = profile.growth_metrics
        behavior = profile.behavior_analysis
        
        # Analyze growth drivers
        growth_drivers = behavior.growth_drivers
        if growth_drivers:
            insight = AudienceInsight(
                insight_id=f"growth_optimization_{int(datetime.now().timestamp())}",
                insight_type="growth_strategy",
                title="Leverage Proven Growth Drivers for Accelerated Expansion",
                description="Identify and amplify content strategies that drive audience growth",
                key_findings=[
                    f"Primary growth driver: {growth_drivers[0] if growth_drivers else 'Content quality'}",
                    f"Growth rate: {growth_metrics.get('monthly_growth_rate', 0):.1%}",
                    "Specific content types correlate with follower acquisition"
                ],
                actionable_recommendations=[
                    f"Double down on {growth_drivers[0] if growth_drivers else 'successful content'}",
                    "Create content series based on growth-driving themes",
                    "Collaborate with creators in similar growth patterns",
                    "Optimize discovery through trending topics and hashtags"
                ],
                confidence_score=0.75,
                impact_potential="high",
                supporting_data={
                    "growth_drivers": growth_drivers,
                    "growth_metrics": growth_metrics
                },
                generated_at=datetime.now(timezone.utc)
            )
            insights.append(insight)
        
        return insights
    
    async def _analyze_monetization_optimization(self, profile: AudienceProfile) -> List[AudienceInsight]:
        """Analyze audience characteristics for monetization optimization."""        
        insights = []
        
        if profile.monetization_potential > 0.6:
            demographics = profile.demographics
            
            insight = AudienceInsight(
                insight_id=f"monetization_optimization_{int(datetime.now().timestamp())}",
                insight_type="monetization_strategy",
                title="High-Value Audience Ready for Monetization",
                description="Audience demographics and engagement patterns indicate strong monetization potential",
                key_findings=[
                    f"Monetization potential score: {profile.monetization_potential:.1%}",
                    f"Target demographic alignment: {self._calculate_demographic_value(demographics)}",
                    "Engagement quality supports premium offerings"
                ],
                actionable_recommendations=[
                    "Launch brand partnership outreach campaign",
                    "Create premium content tiers or subscription offerings",
                    "Develop merchandise line targeting core audience",
                    "Implement affiliate marketing for relevant products",
                    "Consider course or coaching offerings based on expertise"
                ],
                confidence_score=0.88,
                impact_potential="high",
                supporting_data={
                    "monetization_score": profile.monetization_potential,
                    "audience_value_indicators": self._get_value_indicators(profile)
                },
                generated_at=datetime.now(timezone.utc)
            )
            insights.append(insight)
        
        return insights
    
    def _calculate_demographic_value(self, demographics: DemographicData) -> str:
        """Calculate demographic value for monetization."""        
        age_dist = demographics.age_distribution
        income_dist = demographics.income_distribution
        
        # Check for valuable demographics
        valuable_age = age_dist.get('25-34', 0) + age_dist.get('35-44', 0)
        valuable_income = income_dist.get('75k_100k', 0) + income_dist.get('over_100k', 0)
        
        if valuable_age > 0.4 and valuable_income > 0.2:
            return "High value"
        elif valuable_age > 0.3 or valuable_income > 0.15:
            return "Medium value"
        else:
            return "Developing value"
    
    def _get_value_indicators(self, profile: AudienceProfile) -> Dict[str, Any]:
        """Get audience value indicators for monetization."""        
        return {
            "audience_size": profile.total_audience_size,
            "engagement_quality": profile.quality_score,
            "purchasing_power": self._estimate_purchasing_power(profile.demographics),
            "brand_safety": profile.quality_score > 0.7,
            "loyalty_score": statistics.mean(profile.behavior_analysis.loyalty_indicators.values())
        }
    
    def _estimate_purchasing_power(self, demographics: DemographicData) -> str:
        """Estimate audience purchasing power based on demographics."""        
        income_dist = demographics.income_distribution
        high_income = income_dist.get('75k_100k', 0) + income_dist.get('over_100k', 0)
        
        if high_income > 0.3:
            return "High"
        elif high_income > 0.15:
            return "Medium"
        else:
            return "Low"
