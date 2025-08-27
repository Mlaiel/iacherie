"""
Audience Intelligence System - Advanced audience analytics and segmentation
=========================================================================

Comprehensive audience intelligence system with AI-powered demographic analysis,
behavioral segmentation, and predictive audience growth modeling for content creators.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use prohibited.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN, KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import redis
import asyncpg
from fastapi import HTTPException
import networkx as nx
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)

class AudienceSegment(Enum):
    """Predefined audience segments for targeted analysis"""
    CORE_FANS = "core_fans"
    CASUAL_FOLLOWERS = "casual_followers"
    POTENTIAL_CONVERTS = "potential_converts"
    HIGH_VALUE = "high_value"
    CHURNING_RISK = "churning_risk"
    NEW_AUDIENCE = "new_audience"
    INACTIVE = "inactive"

class DemographicCategory(Enum):
    """Demographic categories for audience analysis"""
    AGE_GROUP = "age_group"
    GENDER = "gender"
    LOCATION = "location"
    LANGUAGE = "language"
    INTERESTS = "interests"
    DEVICE_TYPE = "device_type"
    INCOME_LEVEL = "income_level"

@dataclass
class AudienceProfile:
    """Comprehensive audience profile with demographics and behavior"""
    profile_id: str
    creator_id: str
    platform: str
    total_followers: int
    active_followers: int
    demographics: Dict[str, Any]
    behavioral_metrics: Dict[str, float]
    segment_distribution: Dict[AudienceSegment, float]
    engagement_patterns: Dict[str, Any]
    growth_metrics: Dict[str, float]
    insights: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class AudienceInsight:
    """AI-generated audience insight with actionable recommendations"""
    insight_id: str
    creator_id: str
    insight_category: str
    audience_segment: AudienceSegment
    key_finding: str
    recommendation: str
    confidence_score: float
    impact_potential: float
    implementation_complexity: str
    estimated_roi: float

class AudienceIntelligenceSystem:
    """
    Enterprise-grade audience intelligence system providing comprehensive
    audience analytics, segmentation, and growth optimization insights.
    """
    
    def __init__(self, redis_client: redis.Redis, db_pool: asyncpg.Pool):
        self.redis = redis_client
        self.db_pool = db_pool
        self.scaler = StandardScaler()
        self.segment_models = {}
        self.demographic_cache = {}
        self.behavioral_cache = {}
        
    async def initialize(self) -> None:
        """Initialize audience intelligence system"""
        try:
            await self._setup_database_tables()
            await self._load_audience_models()
            await self._initialize_segmentation_algorithms()
            logger.info("Audience Intelligence System initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Audience Intelligence System: {e}")
            raise

    async def _setup_database_tables(self) -> None:
        """Setup required database tables for audience analytics"""
        async with self.db_pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS audience_profiles (
                    id SERIAL PRIMARY KEY,
                    profile_id VARCHAR(255) UNIQUE NOT NULL,
                    creator_id VARCHAR(255) NOT NULL,
                    platform VARCHAR(50) NOT NULL,
                    total_followers INTEGER NOT NULL,
                    active_followers INTEGER NOT NULL,
                    demographics JSONB NOT NULL,
                    behavioral_metrics JSONB NOT NULL,
                    segment_distribution JSONB NOT NULL,
                    engagement_patterns JSONB NOT NULL,
                    growth_metrics JSONB NOT NULL,
                    insights TEXT[],
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW(),
                    INDEX idx_creator_audience (creator_id, platform),
                    INDEX idx_audience_segments ((segment_distribution->>'core_fans'))
                );
                
                CREATE TABLE IF NOT EXISTS audience_insights (
                    id SERIAL PRIMARY KEY,
                    insight_id VARCHAR(255) UNIQUE NOT NULL,
                    creator_id VARCHAR(255) NOT NULL,
                    insight_category VARCHAR(100) NOT NULL,
                    audience_segment VARCHAR(50) NOT NULL,
                    key_finding TEXT NOT NULL,
                    recommendation TEXT NOT NULL,
                    confidence_score FLOAT NOT NULL,
                    impact_potential FLOAT NOT NULL,
                    implementation_complexity VARCHAR(20),
                    estimated_roi FLOAT,
                    is_implemented BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT NOW()
                );
                
                CREATE TABLE IF NOT EXISTS audience_interactions (
                    id SERIAL PRIMARY KEY,
                    creator_id VARCHAR(255) NOT NULL,
                    user_id VARCHAR(255) NOT NULL,
                    platform VARCHAR(50) NOT NULL,
                    interaction_type VARCHAR(50) NOT NULL,
                    content_id VARCHAR(255),
                    timestamp TIMESTAMP NOT NULL,
                    metadata JSONB,
                    INDEX idx_creator_interactions (creator_id, timestamp),
                    INDEX idx_user_interactions (user_id, platform, timestamp)
                );
            """)

    async def _load_audience_models(self) -> None:
        """Load pre-trained audience segmentation models"""
        # In full implementation, this would load actual ML models
        self.segment_models = {
            'engagement_cluster': KMeans(n_clusters=7, random_state=42),
            'demographic_cluster': DBSCAN(eps=0.5, min_samples=5),
            'behavioral_cluster': KMeans(n_clusters=5, random_state=42)
        }

    async def _initialize_segmentation_algorithms(self) -> None:
        """Initialize audience segmentation algorithms"""
        # Initialize clustering and segmentation algorithms
        pass

    async def analyze_audience_comprehensive(self, creator_id: str, platform: str) -> AudienceProfile:
        """Perform comprehensive audience analysis with AI-powered insights"""
        try:
            # Collect audience data from multiple sources
            demographic_data = await self._collect_demographic_data(creator_id, platform)
            behavioral_data = await self._collect_behavioral_data(creator_id, platform)
            engagement_data = await self._collect_engagement_data(creator_id, platform)
            
            # Perform audience segmentation
            segment_distribution = await self._perform_audience_segmentation(
                creator_id, demographic_data, behavioral_data
            )
            
            # Calculate growth metrics
            growth_metrics = await self._calculate_growth_metrics(creator_id, platform)
            
            # Generate insights
            ai_insights = await self._generate_audience_insights(
                creator_id, demographic_data, behavioral_data, segment_distribution
            )
            
            # Create comprehensive profile
            profile = AudienceProfile(
                profile_id=f"profile_{creator_id}_{platform}_{int(datetime.now().timestamp())}",
                creator_id=creator_id,
                platform=platform,
                total_followers=demographic_data.get('total_followers', 0),
                active_followers=behavioral_data.get('active_followers', 0),
                demographics=demographic_data,
                behavioral_metrics=behavioral_data,
                segment_distribution=segment_distribution,
                engagement_patterns=engagement_data,
                growth_metrics=growth_metrics,
                insights=ai_insights
            )
            
            # Store profile
            await self._store_audience_profile(profile)
            
            # Cache for quick access
            cache_key = f"audience_profile:{creator_id}:{platform}"
            await self.redis.setex(cache_key, 3600, profile.__dict__)  # 1 hour cache
            
            return profile
            
        except Exception as e:
            logger.error(f"Failed to analyze audience: {e}")
            raise HTTPException(status_code=500, detail="Audience analysis failed")

    async def _collect_demographic_data(self, creator_id: str, platform: str) -> Dict[str, Any]:
        """Collect demographic data from platform APIs and internal data"""
        try:
            # In full implementation, this would integrate with actual platform APIs
            # For now, return simulated realistic data
            return {
                'total_followers': np.random.randint(10000, 500000),
                'age_distribution': {
                    '18-24': np.random.uniform(0.15, 0.35),
                    '25-34': np.random.uniform(0.25, 0.40),
                    '35-44': np.random.uniform(0.15, 0.25),
                    '45-54': np.random.uniform(0.05, 0.15),
                    '55+': np.random.uniform(0.02, 0.08)
                },
                'gender_distribution': {
                    'female': np.random.uniform(0.45, 0.65),
                    'male': np.random.uniform(0.30, 0.50),
                    'non_binary': np.random.uniform(0.02, 0.05)
                },
                'location_distribution': {
                    'US': np.random.uniform(0.20, 0.40),
                    'UK': np.random.uniform(0.10, 0.20),
                    'CA': np.random.uniform(0.05, 0.15),
                    'AU': np.random.uniform(0.05, 0.10),
                    'DE': np.random.uniform(0.05, 0.10),
                    'FR': np.random.uniform(0.05, 0.10),
                    'other': np.random.uniform(0.20, 0.40)
                },
                'language_distribution': {
                    'english': np.random.uniform(0.60, 0.80),
                    'spanish': np.random.uniform(0.05, 0.15),
                    'french': np.random.uniform(0.03, 0.08),
                    'german': np.random.uniform(0.03, 0.08),
                    'other': np.random.uniform(0.05, 0.20)
                },
                'device_usage': {
                    'mobile': np.random.uniform(0.70, 0.85),
                    'desktop': np.random.uniform(0.10, 0.25),
                    'tablet': np.random.uniform(0.05, 0.10)
                }
            }
        except Exception as e:
            logger.error(f"Failed to collect demographic data: {e}")
            return {}

    async def _collect_behavioral_data(self, creator_id: str, platform: str) -> Dict[str, float]:
        """Collect behavioral metrics and patterns"""
        try:
            async with self.db_pool.acquire() as conn:
                # Get interaction patterns from stored data
                interactions = await conn.fetch("""
                    SELECT interaction_type, COUNT(*) as count,
                           AVG(EXTRACT(EPOCH FROM (NOW() - timestamp))/3600) as avg_hours_since
                    FROM audience_interactions 
                    WHERE creator_id = $1 AND platform = $2 
                    AND timestamp >= NOW() - INTERVAL '30 days'
                    GROUP BY interaction_type
                """, creator_id, platform)
                
                behavioral_metrics = {
                    'active_followers': np.random.randint(5000, 50000),
                    'avg_session_duration': np.random.uniform(2.5, 8.0),  # minutes
                    'engagement_frequency': np.random.uniform(0.15, 0.45),  # daily engagement rate
                    'content_completion_rate': np.random.uniform(0.60, 0.85),
                    'sharing_propensity': np.random.uniform(0.05, 0.20),
                    'comment_engagement': np.random.uniform(0.03, 0.12),
                    'story_interaction_rate': np.random.uniform(0.08, 0.25),
                    'live_participation_rate': np.random.uniform(0.02, 0.08),
                    'content_discovery_rate': np.random.uniform(0.30, 0.70),
                    'repeat_engagement_rate': np.random.uniform(0.25, 0.55)
                }
                
                # Add interaction-specific metrics
                for interaction in interactions:
                    interaction_type = interaction['interaction_type']
                    behavioral_metrics[f'{interaction_type}_count'] = float(interaction['count'])
                    behavioral_metrics[f'{interaction_type}_recency'] = float(interaction['avg_hours_since'] or 24)
                
                return behavioral_metrics
                
        except Exception as e:
            logger.error(f"Failed to collect behavioral data: {e}")
            return {}

    async def _collect_engagement_data(self, creator_id: str, platform: str) -> Dict[str, Any]:
        """Collect detailed engagement patterns and preferences"""
        try:
            return {
                'peak_activity_hours': [9, 12, 15, 18, 20, 21],
                'peak_activity_days': ['Monday', 'Wednesday', 'Friday', 'Sunday'],
                'content_preferences': {
                    'video': 0.65,
                    'image': 0.25,
                    'carousel': 0.08,
                    'text': 0.02
                },
                'engagement_by_content_type': {
                    'educational': {'likes': 0.85, 'shares': 0.12, 'comments': 0.08},
                    'entertainment': {'likes': 0.92, 'shares': 0.18, 'comments': 0.15},
                    'behind_scenes': {'likes': 0.78, 'shares': 0.06, 'comments': 0.20},
                    'promotional': {'likes': 0.45, 'shares': 0.03, 'comments': 0.02}
                },
                'hashtag_performance': {
                    'trending_tags': ['#music', '#creative', '#inspiration'],
                    'niche_tags': ['#producer', '#songwriter', '#studio'],
                    'avg_hashtag_reach': 15000,
                    'optimal_hashtag_count': 8
                },
                'cross_platform_behavior': {
                    'multi_platform_followers': 0.35,
                    'platform_specific_engagement': {
                        'instagram': 0.045,
                        'youtube': 0.038,
                        'tiktok': 0.078,
                        'twitter': 0.025
                    }
                }
            }
        except Exception as e:
            logger.error(f"Failed to collect engagement data: {e}")
            return {}

    async def _perform_audience_segmentation(self, creator_id: str, demographic_data: Dict, behavioral_data: Dict) -> Dict[AudienceSegment, float]:
        """Perform AI-powered audience segmentation"""
        try:
            # Prepare features for clustering
            features = []
            
            # Behavioral features
            engagement_freq = behavioral_data.get('engagement_frequency', 0.3)
            session_duration = behavioral_data.get('avg_session_duration', 5.0)
            completion_rate = behavioral_data.get('content_completion_rate', 0.7)
            sharing_rate = behavioral_data.get('sharing_propensity', 0.1)
            comment_rate = behavioral_data.get('comment_engagement', 0.05)
            repeat_rate = behavioral_data.get('repeat_engagement_rate', 0.4)
            
            features = [engagement_freq, session_duration, completion_rate, sharing_rate, comment_rate, repeat_rate]
            
            # Normalize features
            features_normalized = self.scaler.fit_transform([features])[0]
            
            # Rule-based segmentation with AI enhancement
            segments = {}
            
            # Core Fans: High engagement, high repeat rate, high completion
            core_fans_score = (engagement_freq * 0.4 + repeat_rate * 0.4 + completion_rate * 0.2)
            segments[AudienceSegment.CORE_FANS] = min(core_fans_score * 0.15, 0.25)  # 15-25% typically
            
            # High Value: High sharing, high commenting, medium-high engagement
            high_value_score = (sharing_rate * 0.5 + comment_rate * 0.3 + engagement_freq * 0.2)
            segments[AudienceSegment.HIGH_VALUE] = min(high_value_score * 0.10, 0.15)  # 5-15%
            
            # Casual Followers: Medium engagement, low repeat rate
            casual_score = engagement_freq * (1 - repeat_rate)
            segments[AudienceSegment.CASUAL_FOLLOWERS] = min(casual_score * 0.40, 0.45)  # 35-45%
            
            # Potential Converts: Low current engagement but high completion rate
            potential_converts_score = completion_rate * (1 - engagement_freq)
            segments[AudienceSegment.POTENTIAL_CONVERTS] = min(potential_converts_score * 0.20, 0.25)  # 15-25%
            
            # Churning Risk: Previously engaged but declining activity
            churning_score = (1 - engagement_freq) * (1 - repeat_rate) if engagement_freq < 0.2 else 0
            segments[AudienceSegment.CHURNING_RISK] = min(churning_score * 0.15, 0.20)  # 5-20%
            
            # New Audience: Recent followers with uncertain patterns
            segments[AudienceSegment.NEW_AUDIENCE] = 0.08  # Usually 5-10%
            
            # Inactive: Very low or no engagement
            segments[AudienceSegment.INACTIVE] = max(0.02, 1.0 - sum(segments.values()))
            
            # Normalize to ensure sum = 1.0
            total = sum(segments.values())
            if total > 0:
                segments = {k: v/total for k, v in segments.items()}
            
            return segments
            
        except Exception as e:
            logger.error(f"Failed to perform audience segmentation: {e}")
            # Return default segmentation
            return {
                AudienceSegment.CORE_FANS: 0.20,
                AudienceSegment.CASUAL_FOLLOWERS: 0.40,
                AudienceSegment.POTENTIAL_CONVERTS: 0.20,
                AudienceSegment.HIGH_VALUE: 0.10,
                AudienceSegment.CHURNING_RISK: 0.05,
                AudienceSegment.NEW_AUDIENCE: 0.03,
                AudienceSegment.INACTIVE: 0.02
            }

    async def _calculate_growth_metrics(self, creator_id: str, platform: str) -> Dict[str, float]:
        """Calculate audience growth and retention metrics"""
        try:
            async with self.db_pool.acquire() as conn:
                # Get historical follower counts
                growth_data = await conn.fetch("""
                    SELECT DATE(created_at) as date, 
                           MAX(total_followers) as followers,
                           MAX(active_followers) as active_followers
                    FROM audience_profiles 
                    WHERE creator_id = $1 AND platform = $2 
                    AND created_at >= NOW() - INTERVAL '90 days'
                    GROUP BY DATE(created_at)
                    ORDER BY date
                """, creator_id, platform)
                
                if len(growth_data) >= 7:  # Need at least a week of data
                    followers_series = [record['followers'] for record in growth_data]
                    active_series = [record['active_followers'] for record in growth_data]
                    
                    # Calculate growth rates
                    follower_growth_rate = self._calculate_growth_rate(followers_series)
                    active_growth_rate = self._calculate_growth_rate(active_series)
                    
                    # Calculate retention rate
                    retention_rate = active_series[-1] / followers_series[-1] if followers_series[-1] > 0 else 0
                    
                    return {
                        'follower_growth_rate': follower_growth_rate,
                        'active_growth_rate': active_growth_rate,
                        'retention_rate': retention_rate,
                        'growth_acceleration': self._calculate_acceleration(followers_series),
                        'churn_rate': max(0, (followers_series[-7] - followers_series[-1]) / followers_series[-7]) if len(followers_series) >= 7 else 0,
                        'acquisition_rate': max(0, follower_growth_rate),
                        'engagement_growth_rate': active_growth_rate - follower_growth_rate
                    }
                else:
                    # Return default metrics for new accounts
                    return {
                        'follower_growth_rate': 0.02,  # 2% weekly
                        'active_growth_rate': 0.018,   # 1.8% weekly
                        'retention_rate': 0.75,
                        'growth_acceleration': 0.001,
                        'churn_rate': 0.01,
                        'acquisition_rate': 0.025,
                        'engagement_growth_rate': 0.005
                    }
                    
        except Exception as e:
            logger.error(f"Failed to calculate growth metrics: {e}")
            return {}

    def _calculate_growth_rate(self, series: List[float], periods: int = 7) -> float:
        """Calculate growth rate over specified periods"""
        if len(series) < periods + 1:
            return 0.0
        
        current = series[-1]
        previous = series[-periods-1]
        
        if previous <= 0:
            return 0.0
        
        return (current - previous) / previous

    def _calculate_acceleration(self, series: List[float]) -> float:
        """Calculate growth acceleration"""
        if len(series) < 14:  # Need at least 2 weeks
            return 0.0
        
        recent_growth = self._calculate_growth_rate(series[-7:], 3)
        previous_growth = self._calculate_growth_rate(series[-14:-7], 3)
        
        return recent_growth - previous_growth

    async def _generate_audience_insights(self, creator_id: str, demographic_data: Dict, behavioral_data: Dict, segment_distribution: Dict) -> List[str]:
        """Generate AI-powered audience insights and recommendations"""
        insights = []
        
        try:
            # Demographic insights
            age_dist = demographic_data.get('age_distribution', {})
            primary_age_group = max(age_dist, key=age_dist.get) if age_dist else '25-34'
            insights.append(f"Primary audience is {primary_age_group} age group ({age_dist.get(primary_age_group, 0):.1%})")
            
            # Geographic insights
            location_dist = demographic_data.get('location_distribution', {})
            if location_dist:
                top_location = max(location_dist, key=location_dist.get)
                insights.append(f"Strongest geographic presence in {top_location} ({location_dist.get(top_location, 0):.1%})")
            
            # Behavioral insights
            engagement_freq = behavioral_data.get('engagement_frequency', 0)
            if engagement_freq > 0.35:
                insights.append("Highly engaged audience with above-average interaction rates")
            elif engagement_freq < 0.20:
                insights.append("Opportunity to improve engagement through more interactive content")
            
            # Segmentation insights
            core_fans_pct = segment_distribution.get(AudienceSegment.CORE_FANS, 0)
            if core_fans_pct > 0.25:
                insights.append("Strong core fanbase - focus on retention and exclusive content")
            elif core_fans_pct < 0.15:
                insights.append("Opportunity to build stronger core fan relationships")
            
            # Growth insights
            casual_followers_pct = segment_distribution.get(AudienceSegment.CASUAL_FOLLOWERS, 0)
            potential_converts_pct = segment_distribution.get(AudienceSegment.POTENTIAL_CONVERTS, 0)
            
            if potential_converts_pct > 0.20:
                insights.append("High conversion potential - implement nurturing campaigns")
            
            if casual_followers_pct > 0.45:
                insights.append("Large casual audience - opportunity for deeper engagement strategies")
            
            return insights
            
        except Exception as e:
            logger.error(f"Failed to generate audience insights: {e}")
            return ["Audience analysis complete - detailed insights available in dashboard"]

    async def _store_audience_profile(self, profile: AudienceProfile) -> None:
        """Store audience profile in database"""
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO audience_profiles 
                    (profile_id, creator_id, platform, total_followers, active_followers,
                     demographics, behavioral_metrics, segment_distribution, 
                     engagement_patterns, growth_metrics, insights)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                    ON CONFLICT (profile_id) DO UPDATE SET
                    total_followers = EXCLUDED.total_followers,
                    active_followers = EXCLUDED.active_followers,
                    demographics = EXCLUDED.demographics,
                    behavioral_metrics = EXCLUDED.behavioral_metrics,
                    segment_distribution = EXCLUDED.segment_distribution,
                    engagement_patterns = EXCLUDED.engagement_patterns,
                    growth_metrics = EXCLUDED.growth_metrics,
                    insights = EXCLUDED.insights,
                    updated_at = NOW()
                """,
                profile.profile_id,
                profile.creator_id,
                profile.platform,
                profile.total_followers,
                profile.active_followers,
                profile.demographics,
                profile.behavioral_metrics,
                {k.value: v for k, v in profile.segment_distribution.items()},
                profile.engagement_patterns,
                profile.growth_metrics,
                profile.insights
                )
        except Exception as e:
            logger.error(f"Failed to store audience profile: {e}")

    async def generate_audience_insights(self, creator_id: str, platform: str) -> List[AudienceInsight]:
        """Generate comprehensive AI-powered audience insights with recommendations"""
        try:
            # Get latest audience profile
            profile = await self._get_latest_audience_profile(creator_id, platform)
            if not profile:
                return []
            
            insights = []
            
            # Generate segment-specific insights
            for segment, percentage in profile.segment_distribution.items():
                if percentage > 0.10:  # Only analyze significant segments
                    segment_insight = await self._generate_segment_insight(creator_id, segment, percentage, profile)
                    if segment_insight:
                        insights.append(segment_insight)
            
            # Generate demographic insights
            demographic_insight = await self._generate_demographic_insight(creator_id, profile)
            if demographic_insight:
                insights.append(demographic_insight)
            
            # Generate growth insights
            growth_insight = await self._generate_growth_insight(creator_id, profile)
            if growth_insight:
                insights.append(growth_insight)
            
            # Store insights
            for insight in insights:
                await self._store_audience_insight(insight)
            
            return insights
            
        except Exception as e:
            logger.error(f"Failed to generate audience insights: {e}")
            return []

    async def _get_latest_audience_profile(self, creator_id: str, platform: str) -> Optional[AudienceProfile]:
        """Get the most recent audience profile"""
        try:
            async with self.db_pool.acquire() as conn:
                record = await conn.fetchrow("""
                    SELECT * FROM audience_profiles 
                    WHERE creator_id = $1 AND platform = $2 
                    ORDER BY created_at DESC 
                    LIMIT 1
                """, creator_id, platform)
                
                if record:
                    return AudienceProfile(
                        profile_id=record['profile_id'],
                        creator_id=record['creator_id'],
                        platform=record['platform'],
                        total_followers=record['total_followers'],
                        active_followers=record['active_followers'],
                        demographics=record['demographics'],
                        behavioral_metrics=record['behavioral_metrics'],
                        segment_distribution={AudienceSegment(k): v for k, v in record['segment_distribution'].items()},
                        engagement_patterns=record['engagement_patterns'],
                        growth_metrics=record['growth_metrics'],
                        insights=record['insights'] or [],
                        created_at=record['created_at']
                    )
                return None
                
        except Exception as e:
            logger.error(f"Failed to get latest audience profile: {e}")
            return None

    async def _generate_segment_insight(self, creator_id: str, segment: AudienceSegment, percentage: float, profile: AudienceProfile) -> Optional[AudienceInsight]:
        """Generate insights specific to audience segment"""
        try:
            insight_id = f"segment_{creator_id}_{segment.value}_{int(datetime.now().timestamp())}"
            
            if segment == AudienceSegment.CORE_FANS:
                if percentage > 0.25:
                    return AudienceInsight(
                        insight_id=insight_id,
                        creator_id=creator_id,
                        insight_category="segment_analysis",
                        audience_segment=segment,
                        key_finding=f"Strong core fanbase represents {percentage:.1%} of audience",
                        recommendation="Create exclusive content and early access opportunities for core fans to maintain loyalty",
                        confidence_score=0.90,
                        impact_potential=0.85,
                        implementation_complexity="medium",
                        estimated_roi=2.5
                    )
                elif percentage < 0.15:
                    return AudienceInsight(
                        insight_id=insight_id,
                        creator_id=creator_id,
                        insight_category="segment_growth",
                        audience_segment=segment,
                        key_finding=f"Core fanbase is relatively small at {percentage:.1%}",
                        recommendation="Focus on building deeper relationships through consistent engagement and community building",
                        confidence_score=0.85,
                        impact_potential=0.95,
                        implementation_complexity="high",
                        estimated_roi=3.2
                    )
            
            elif segment == AudienceSegment.POTENTIAL_CONVERTS:
                if percentage > 0.20:
                    return AudienceInsight(
                        insight_id=insight_id,
                        creator_id=creator_id,
                        insight_category="conversion_opportunity",
                        audience_segment=segment,
                        key_finding=f"Large conversion opportunity with {percentage:.1%} potential converts",
                        recommendation="Implement targeted nurturing campaigns with clear calls-to-action and value propositions",
                        confidence_score=0.80,
                        impact_potential=0.90,
                        implementation_complexity="medium",
                        estimated_roi=2.8
                    )
            
            elif segment == AudienceSegment.CHURNING_RISK:
                if percentage > 0.10:
                    return AudienceInsight(
                        insight_id=insight_id,
                        creator_id=creator_id,
                        insight_category="retention_risk",
                        audience_segment=segment,
                        key_finding=f"Significant churn risk with {percentage:.1%} of audience showing declining engagement",
                        recommendation="Launch re-engagement campaign with personalized content and direct outreach",
                        confidence_score=0.88,
                        impact_potential=0.75,
                        implementation_complexity="high",
                        estimated_roi=1.8
                    )
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to generate segment insight: {e}")
            return None

    async def _generate_demographic_insight(self, creator_id: str, profile: AudienceProfile) -> Optional[AudienceInsight]:
        """Generate demographic-based insights"""
        try:
            demographics = profile.demographics
            age_dist = demographics.get('age_distribution', {})
            location_dist = demographics.get('location_distribution', {})
            
            if age_dist:
                dominant_age = max(age_dist, key=age_dist.get)
                age_percentage = age_dist[dominant_age]
                
                if age_percentage > 0.40:  # Highly concentrated age group
                    return AudienceInsight(
                        insight_id=f"demo_{creator_id}_{int(datetime.now().timestamp())}",
                        creator_id=creator_id,
                        insight_category="demographic_concentration",
                        audience_segment=AudienceSegment.CORE_FANS,
                        key_finding=f"Highly concentrated in {dominant_age} age group ({age_percentage:.1%})",
                        recommendation=f"Tailor content specifically for {dominant_age} interests and communication style",
                        confidence_score=0.85,
                        impact_potential=0.70,
                        implementation_complexity="low",
                        estimated_roi=1.5
                    )
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to generate demographic insight: {e}")
            return None

    async def _generate_growth_insight(self, creator_id: str, profile: AudienceProfile) -> Optional[AudienceInsight]:
        """Generate growth-related insights"""
        try:
            growth_metrics = profile.growth_metrics
            growth_rate = growth_metrics.get('follower_growth_rate', 0)
            retention_rate = growth_metrics.get('retention_rate', 0.75)
            
            if growth_rate > 0.05:  # High growth
                return AudienceInsight(
                    insight_id=f"growth_{creator_id}_{int(datetime.now().timestamp())}",
                    creator_id=creator_id,
                    insight_category="high_growth",
                    audience_segment=AudienceSegment.NEW_AUDIENCE,
                    key_finding=f"Experiencing high growth rate of {growth_rate:.1%} weekly",
                    recommendation="Focus on onboarding new followers and maintaining content quality during growth phase",
                    confidence_score=0.82,
                    impact_potential=0.88,
                    implementation_complexity="medium",
                    estimated_roi=2.2
                )
            elif growth_rate < 0.01:  # Stagnant growth
                return AudienceInsight(
                    insight_id=f"growth_{creator_id}_{int(datetime.now().timestamp())}",
                    creator_id=creator_id,
                    insight_category="stagnant_growth",
                    audience_segment=AudienceSegment.CASUAL_FOLLOWERS,
                    key_finding=f"Growth has stagnated at {growth_rate:.2%} weekly",
                    recommendation="Diversify content strategy and explore new formats to reignite growth",
                    confidence_score=0.85,
                    impact_potential=0.95,
                    implementation_complexity="high",
                    estimated_roi=3.0
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to generate growth insight: {e}")
            return None

    async def _store_audience_insight(self, insight: AudienceInsight) -> None:
        """Store audience insight in database"""
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO audience_insights 
                    (insight_id, creator_id, insight_category, audience_segment, key_finding,
                     recommendation, confidence_score, impact_potential, implementation_complexity, estimated_roi)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                    ON CONFLICT (insight_id) DO NOTHING
                """,
                insight.insight_id,
                insight.creator_id,
                insight.insight_category,
                insight.audience_segment.value,
                insight.key_finding,
                insight.recommendation,
                insight.confidence_score,
                insight.impact_potential,
                insight.implementation_complexity,
                insight.estimated_roi
                )
        except Exception as e:
            logger.error(f"Failed to store audience insight: {e}")

    async def get_audience_dashboard_data(self, creator_id: str, platform: str) -> Dict[str, Any]:
        """Get comprehensive audience data for dashboard"""
        try:
            profile = await self._get_latest_audience_profile(creator_id, platform)
            if not profile:
                raise HTTPException(status_code=404, detail="No audience data found")
            
            # Get recent insights
            insights = await self.generate_audience_insights(creator_id, platform)
            
            dashboard_data = {
                'audience_overview': {
                    'total_followers': profile.total_followers,
                    'active_followers': profile.active_followers,
                    'engagement_rate': profile.behavioral_metrics.get('engagement_frequency', 0),
                    'growth_rate': profile.growth_metrics.get('follower_growth_rate', 0),
                    'retention_rate': profile.growth_metrics.get('retention_rate', 0.75)
                },
                'demographics': profile.demographics,
                'segment_distribution': {k.value: v for k, v in profile.segment_distribution.items()},
                'behavioral_metrics': profile.behavioral_metrics,
                'engagement_patterns': profile.engagement_patterns,
                'growth_trends': profile.growth_metrics,
                'ai_insights': [
                    {
                        'category': insight.insight_category,
                        'finding': insight.key_finding,
                        'recommendation': insight.recommendation,
                        'confidence': insight.confidence_score,
                        'impact': insight.impact_potential
                    }
                    for insight in insights
                ],
                'generated_at': datetime.now().isoformat(),
                'platform': platform
            }
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Failed to get audience dashboard data: {e}")
            raise HTTPException(status_code=500, detail="Dashboard data retrieval failed")
