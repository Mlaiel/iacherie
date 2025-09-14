"""Content Trend Analysis Engine
Advanced trend detection and viral content prediction for multimedia content.

This module provides comprehensive trend analysis including viral content prediction,
trending topic detection, content lifecycle analysis, and market trend insights.

Author: Fahed Mlaiel <mlaiel@live.de>
Project Team: Lead AI Developer + Backend Senior Engineer + ML Engineer + 
              Database Administrator + Security Expert + Microservices Architect +
              Multimedia Processing Specialist + DevOps Engineer + AI Prompt Engineer

⚠️ COPYRIGHT PROTECTION ⚠️
This code is proprietary and confidential. Unauthorized use is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

import logging
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import asyncio
from enum import Enum
from collections import defaultdict, deque
import hashlib
import json

logger = logging.getLogger(__name__)

class TrendType(Enum):
    """Types of trends"""
    VIRAL = "viral"
    EMERGING = "emerging"
    DECLINING = "declining"
    SEASONAL = "seasonal"
    CYCLICAL = "cyclical"
    PLATFORM_SPECIFIC = "platform_specific"

class TrendStrength(Enum):
    """Trend strength levels"""
    WEAK = "weak"
    MODERATE = "moderate"
    STRONG = "strong"
    EXPLOSIVE = "explosive"

@dataclass
class TrendData:
    """Trend data structure"""
    trend_id: str
    trend_name: str
    trend_type: TrendType
    detection_date: datetime
    
    # Trend characteristics
    strength: TrendStrength = TrendStrength.MODERATE
    velocity: float = 0.0  # Rate of growth/decline
    reach: int = 0  # Number of people/content affected
    engagement_rate: float = 0.0
    
    # Content analysis
    related_keywords: List[str] = field(default_factory=list)
    content_categories: List[str] = field(default_factory=list)
    hashtags: List[str] = field(default_factory=list)
    
    # Platform distribution
    platform_distribution: Dict[str, float] = field(default_factory=dict)
    demographic_distribution: Dict[str, float] = field(default_factory=dict)
    
    # Predictions
    predicted_peak_date: Optional[datetime] = None
    predicted_lifespan: Optional[timedelta] = None
    virality_probability: float = 0.0
    sustainability_score: float = 0.0
    
    # Supporting data
    sample_content: List[Dict[str, Any]] = field(default_factory=list)
    influencers: List[str] = field(default_factory=list)
    growth_data: List[Tuple[datetime, float]] = field(default_factory=list)
    
    # Market insights
    commercial_potential: float = 0.0
    competition_level: float = 0.0
    entry_difficulty: float = 0.0

@dataclass
class ViralityPrediction:
    """Viral content prediction"""
    content_id: str
    prediction_date: datetime
    
    # Prediction scores
    virality_score: float = 0.0  # 0-1 probability of going viral
    time_to_viral: Optional[timedelta] = None
    predicted_peak_views: int = 0
    predicted_total_views: int = 0
    
    # Contributing factors
    content_quality_factor: float = 0.0
    timing_factor: float = 0.0
    trend_alignment_factor: float = 0.0
    creator_influence_factor: float = 0.0
    platform_algorithm_factor: float = 0.0
    
    # Confidence metrics
    prediction_confidence: float = 0.0
    model_accuracy: float = 0.0
    
    # Recommendations
    optimization_suggestions: List[str] = field(default_factory=list)
    timing_recommendations: List[str] = field(default_factory=list)
    
    # Actual performance (for validation)
    actual_viral: Optional[bool] = None
    actual_peak_views: Optional[int] = None
    validation_date: Optional[datetime] = None

@dataclass
class ContentLifecycle:
    """Content lifecycle analysis"""
    content_id: str
    lifecycle_start: datetime
    
    # Lifecycle stages
    introduction_phase: Dict[str, Any] = field(default_factory=dict)
    growth_phase: Dict[str, Any] = field(default_factory=dict)
    maturity_phase: Dict[str, Any] = field(default_factory=dict)
    decline_phase: Dict[str, Any] = field(default_factory=dict)
    
    # Phase durations
    intro_duration: Optional[timedelta] = None
    growth_duration: Optional[timedelta] = None
    maturity_duration: Optional[timedelta] = None
    decline_duration: Optional[timedelta] = None
    
    # Lifecycle metrics
    total_lifecycle_value: float = 0.0
    peak_performance_date: Optional[datetime] = None
    longevity_score: float = 0.0
    
    # Current status
    current_phase: str = "introduction"
    phase_progress: float = 0.0  # 0-1 progress through current phase


class TrendAnalyzer:
    """Main trend analysis engine"""
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        self.logger = logger.getChild(self.__class__.__name__)
        
        # Data storage
        self.detected_trends: Dict[str, TrendData] = {}
        self.trend_history: deque = deque(maxlen=1000)
        
        # Analysis parameters
        self.trend_detection_window = self.config.get('trend_detection_window_hours', 24)
        self.viral_threshold = self.config.get('viral_threshold', 100000)  # views
        self.trend_velocity_threshold = self.config.get('trend_velocity_threshold', 0.5)
        
        # Machine learning models (simplified)
        self.virality_model_weights = self._initialize_virality_model()
        
    def _initialize_virality_model(self) -> Dict[str, float]:
        """Initialize virality prediction model weights"""
        return {
            'content_quality': 0.25,
            'timing': 0.20,
            'trend_alignment': 0.20,
            'creator_influence': 0.15,
            'platform_algorithm': 0.10,
            'engagement_velocity': 0.10
        }
    
    async def detect_trends(self, content_data: List[Dict[str, Any]], 
                          time_window_hours: int = 24) -> List[TrendData]:
        """Detect emerging trends from content data"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=time_window_hours)
            
            # Filter recent content
            recent_content = [
                item for item in content_data
                if item.get('upload_date', datetime.now()) >= cutoff_time
            ]
            
            if len(recent_content) < 10:  # Need sufficient data
                return []
            
            # Detect different types of trends
            trends = []
            
            # Keyword/hashtag trends
            keyword_trends = await self._detect_keyword_trends(recent_content)
            trends.extend(keyword_trends)
            
            # Content category trends
            category_trends = await self._detect_category_trends(recent_content)
            trends.extend(category_trends)
            
            # Platform-specific trends
            platform_trends = await self._detect_platform_trends(recent_content)
            trends.extend(platform_trends)
            
            # Viral content trends
            viral_trends = await self._detect_viral_trends(recent_content)
            trends.extend(viral_trends)
            
            # Store detected trends
            for trend in trends:
                self.detected_trends[trend.trend_id] = trend
                self.trend_history.append(trend)
            
            return trends
            
        except Exception as e:
            self.logger.error(f"Trend detection failed: {e}")
            return []
    
    async def _detect_keyword_trends(self, content_data: List[Dict[str, Any]]) -> List[TrendData]:
        """Detect trending keywords and hashtags"""
        trends = []
        
        try:
            # Extract keywords and hashtags
            keyword_data = defaultdict(lambda: {'count': 0, 'views': 0, 'engagement': 0, 'content': []})
            
            for item in content_data:
                tags = item.get('tags', [])
                title = item.get('title', '')
                views = item.get('views', 0)
                likes = item.get('likes', 0)
                shares = item.get('shares', 0)
                engagement = likes + shares
                
                # Process hashtags from tags
                for tag in tags:
                    tag_lower = tag.lower()
                    keyword_data[tag_lower]['count'] += 1
                    keyword_data[tag_lower]['views'] += views
                    keyword_data[tag_lower]['engagement'] += engagement
                    keyword_data[tag_lower]['content'].append(item)
                
                # Extract keywords from title (simplified)
                title_words = title.lower().split()
                for word in title_words:
                    if len(word) > 3:  # Filter short words
                        keyword_data[word]['count'] += 1
                        keyword_data[word]['views'] += views
                        keyword_data[word]['engagement'] += engagement
                        keyword_data[word]['content'].append(item)
            
            # Analyze keyword trends
            for keyword, data in keyword_data.items():
                if data['count'] < 5:  # Need minimum occurrence
                    continue
                
                avg_views = data['views'] / data['count']
                avg_engagement = data['engagement'] / data['count']
                
                # Calculate trend strength
                strength_score = min(data['count'] / 100.0, 1.0) * min(avg_views / 10000.0, 1.0)
                
                if strength_score > 0.3:  # Threshold for trend detection
                    trend = TrendData(
                        trend_id=f"keyword_{keyword}_{int(datetime.now().timestamp())}",
                        trend_name=f"#{keyword}",
                        trend_type=TrendType.EMERGING,
                        detection_date=datetime.now(),
                        reach=data['count'],
                        engagement_rate=avg_engagement / max(avg_views, 1),
                        related_keywords=[keyword],
                        sample_content=data['content'][:3]  # Top 3 examples
                    )
                    
                    # Determine trend strength
                    if strength_score > 0.8:
                        trend.strength = TrendStrength.EXPLOSIVE
                    elif strength_score > 0.6:
                        trend.strength = TrendStrength.STRONG
                    else:
                        trend.strength = TrendStrength.MODERATE
                    
                    trends.append(trend)
            
        except Exception as e:
            self.logger.error(f"Keyword trend detection failed: {e}")
        
        return trends
    
    async def _detect_category_trends(self, content_data: List[Dict[str, Any]]) -> List[TrendData]:
        """Detect trending content categories"""
        trends = []
        
        try:
            # Analyze content categories
            category_data = defaultdict(lambda: {'count': 0, 'views': 0, 'engagement': 0})
            
            for item in content_data:
                category = item.get('category', 'uncategorized')
                views = item.get('views', 0)
                likes = item.get('likes', 0)
                shares = item.get('shares', 0)
                
                category_data[category]['count'] += 1
                category_data[category]['views'] += views
                category_data[category]['engagement'] += likes + shares
            
            # Calculate category performance
            total_content = len(content_data)
            
            for category, data in category_data.items():
                if data['count'] < 3:  # Need minimum content
                    continue
                
                category_share = data['count'] / total_content
                avg_views = data['views'] / data['count']
                avg_engagement = data['engagement'] / data['count']
                
                # Detect if category is trending
                if category_share > 0.2 and avg_views > 5000:  # Significant share and performance
                    trend = TrendData(
                        trend_id=f"category_{category}_{int(datetime.now().timestamp())}",
                        trend_name=f"{category.title()} Content",
                        trend_type=TrendType.EMERGING,
                        detection_date=datetime.now(),
                        reach=data['count'],
                        engagement_rate=avg_engagement / max(avg_views, 1),
                        content_categories=[category]
                    )
                    
                    trends.append(trend)
            
        except Exception as e:
            self.logger.error(f"Category trend detection failed: {e}")
        
        return trends
    
    async def _detect_platform_trends(self, content_data: List[Dict[str, Any]]) -> List[TrendData]:
        """Detect platform-specific trends"""
        trends = []
        
        try:
            # Group by platform
            platform_data = defaultdict(lambda: {'content': [], 'total_views': 0, 'total_engagement': 0})
            
            for item in content_data:
                platform = item.get('platform', 'unknown')
                views = item.get('views', 0)
                engagement = item.get('likes', 0) + item.get('shares', 0)
                
                platform_data[platform]['content'].append(item)
                platform_data[platform]['total_views'] += views
                platform_data[platform]['total_engagement'] += engagement
            
            # Analyze platform performance
            for platform, data in platform_data.items():
                content_count = len(data['content'])
                
                if content_count < 5:  # Need minimum content
                    continue
                
                avg_views = data['total_views'] / content_count
                avg_engagement = data['total_engagement'] / content_count
                
                # Check if platform performance is significantly above average
                overall_avg_views = sum(item.get('views', 0) for item in content_data) / len(content_data)
                
                if avg_views > overall_avg_views * 1.5:  # 50% above average
                    trend = TrendData(
                        trend_id=f"platform_{platform}_{int(datetime.now().timestamp())}",
                        trend_name=f"{platform.title()} Platform Trend",
                        trend_type=TrendType.PLATFORM_SPECIFIC,
                        detection_date=datetime.now(),
                        reach=content_count,
                        engagement_rate=avg_engagement / max(avg_views, 1),
                        platform_distribution={platform: 1.0}
                    )
                    
                    trends.append(trend)
            
        except Exception as e:
            self.logger.error(f"Platform trend detection failed: {e}")
        
        return trends
    
    async def _detect_viral_trends(self, content_data: List[Dict[str, Any]]) -> List[TrendData]:
        """Detect viral content patterns"""
        trends = []
        
        try:
            # Find viral content
            viral_content = [
                item for item in content_data
                if item.get('views', 0) > self.viral_threshold
            ]
            
            if len(viral_content) < 3:  # Need minimum viral content
                return trends
            
            # Analyze common characteristics of viral content
            common_tags = defaultdict(int)
            common_categories = defaultdict(int)
            
            for item in viral_content:
                tags = item.get('tags', [])
                category = item.get('category', 'uncategorized')
                
                for tag in tags:
                    common_tags[tag.lower()] += 1
                common_categories[category] += 1
            
            # Find most common viral characteristics
            viral_tags = [tag for tag, count in common_tags.items() if count >= 2]
            viral_categories = [cat for cat, count in common_categories.items() if count >= 2]
            
            if viral_tags or viral_categories:
                trend = TrendData(
                    trend_id=f"viral_pattern_{int(datetime.now().timestamp())}",
                    trend_name="Viral Content Pattern",
                    trend_type=TrendType.VIRAL,
                    detection_date=datetime.now(),
                    strength=TrendStrength.EXPLOSIVE,
                    reach=len(viral_content),
                    related_keywords=viral_tags,
                    content_categories=viral_categories,
                    sample_content=viral_content[:3]  # Top 3 viral examples
                )
                
                trends.append(trend)
            
        except Exception as e:
            self.logger.error(f"Viral trend detection failed: {e}")
        
        return trends
    
    async def predict_content_lifecycle(self, content_id: str, 
                                      content_data: Dict[str, Any],
                                      historical_performance: Optional[List[Dict[str, Any]]] = None) -> ContentLifecycle:
        """Predict content lifecycle stages and durations"""
        try:
            lifecycle = ContentLifecycle(
                content_id=content_id,
                lifecycle_start=content_data.get('upload_date', datetime.now())
            )
            
            # Analyze current performance
            current_views = content_data.get('views', 0)
            current_engagement = content_data.get('likes', 0) + content_data.get('shares', 0)
            
            # Determine current phase based on performance trajectory
            if historical_performance:
                lifecycle.current_phase = await self._determine_lifecycle_phase(
                    current_views, current_engagement, historical_performance
                )
            
            # Predict phase durations based on content type and performance
            await self._predict_phase_durations(lifecycle, content_data)
            
            # Calculate lifecycle metrics
            await self._calculate_lifecycle_metrics(lifecycle, content_data)
            
            return lifecycle
            
        except Exception as e:
            self.logger.error(f"Content lifecycle prediction failed: {e}")
            return ContentLifecycle(content_id=content_id, lifecycle_start=datetime.now())
    
    async def _determine_lifecycle_phase(self, current_views: int, current_engagement: int,
                                       historical_performance: List[Dict[str, Any]]) -> str:
        """Determine current lifecycle phase"""
        try:
            if len(historical_performance) < 3:
                return "introduction"
            
            # Analyze performance trend
            recent_views = [item.get('views', 0) for item in historical_performance[-3:]]
            view_trend = np.polyfit(range(len(recent_views)), recent_views, 1)[0]
            
            max_views = max(item.get('views', 0) for item in historical_performance)
            
            # Determine phase based on trends and peak performance
            if current_views < max_views * 0.3:
                return "introduction"
            elif view_trend > 0 and current_views < max_views * 0.8:
                return "growth"
            elif current_views >= max_views * 0.8:
                return "maturity"
            else:
                return "decline"
            
        except Exception as e:
            self.logger.error(f"Lifecycle phase determination failed: {e}")
            return "introduction"
    
    async def _predict_phase_durations(self, lifecycle -> None: ContentLifecycle, content_data -> None: Dict[str, Any]) -> None:
        """Predict lifecycle phase durations"""
        try:
            content_type = content_data.get('content_type', 'video')
            
            # Base durations by content type (in hours)
            base_durations = {
                'video': {'intro': 6, 'growth': 24, 'maturity': 72, 'decline': 168},
                'image': {'intro': 2, 'growth': 8, 'maturity': 24, 'decline': 72},
                'audio': {'intro': 4, 'growth': 12, 'maturity': 48, 'decline': 120}
            }
            
            durations = base_durations.get(content_type, base_durations['video'])
            
            # Adjust based on content quality and creator influence
            quality_multiplier = content_data.get('quality_score', 0.7)
            creator_influence = content_data.get('creator_followers', 1000) / 10000.0
            
            adjustment_factor = 1 + quality_multiplier * 0.5 + min(creator_influence, 1.0) * 0.3
            
            lifecycle.intro_duration = timedelta(hours=durations['intro'] * adjustment_factor)
            lifecycle.growth_duration = timedelta(hours=durations['growth'] * adjustment_factor)
            lifecycle.maturity_duration = timedelta(hours=durations['maturity'] * adjustment_factor)
            lifecycle.decline_duration = timedelta(hours=durations['decline'] * adjustment_factor)
            
        except Exception as e:
            self.logger.error(f"Phase duration prediction failed: {e}")
    
    async def _calculate_lifecycle_metrics(self, lifecycle -> None: ContentLifecycle, content_data -> None: Dict[str, Any]) -> None:
        """Calculate lifecycle performance metrics"""
        try:
            # Calculate total lifecycle value (simplified)
            views = content_data.get('views', 0)
            engagement = content_data.get('likes', 0) + content_data.get('shares', 0)
            
            lifecycle.total_lifecycle_value = views * 0.001 + engagement * 0.01  # Simplified value calculation
            
            # Calculate longevity score
            expected_lifespan = sum([
                lifecycle.intro_duration or timedelta(0),
                lifecycle.growth_duration or timedelta(0),
                lifecycle.maturity_duration or timedelta(0),
                lifecycle.decline_duration or timedelta(0)
            ], timedelta(0))
            
            if expected_lifespan.total_seconds() > 0:
                lifecycle.longevity_score = min(expected_lifespan.total_seconds() / (7 * 24 * 3600), 1.0)  # Normalize to 1 week
            
        except Exception as e:
            self.logger.error(f"Lifecycle metrics calculation failed: {e}")


class ViralityPredictor:
    """Viral content prediction engine"""
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        self.logger = logger.getChild(self.__class__.__name__)
        
        # Model parameters
        self.model_weights = self.config.get('model_weights', {
            'content_quality': 0.25,
            'timing': 0.20,
            'trend_alignment': 0.20,
            'creator_influence': 0.15,
            'platform_algorithm': 0.10,
            'engagement_velocity': 0.10
        })
        
        # Prediction thresholds
        self.viral_thresholds = self.config.get('viral_thresholds', {
            'high_probability': 0.8,
            'medium_probability': 0.6,
            'low_probability': 0.4
        })
    
    async def predict_virality(self, content_data: Dict[str, Any],
                             current_trends: List[TrendData],
                             creator_profile: Optional[Dict[str, Any]] = None) -> ViralityPrediction:
        """Predict the likelihood of content going viral"""
        try:
            prediction = ViralityPrediction(
                content_id=content_data['content_id'],
                prediction_date=datetime.now()
            )
            
            # Calculate component factors
            prediction.content_quality_factor = await self._calculate_quality_factor(content_data)
            prediction.timing_factor = await self._calculate_timing_factor(content_data)
            prediction.trend_alignment_factor = await self._calculate_trend_alignment(content_data, current_trends)
            prediction.creator_influence_factor = await self._calculate_creator_influence(creator_profile)
            prediction.platform_algorithm_factor = await self._calculate_platform_factor(content_data)
            prediction.engagement_velocity = await self._calculate_engagement_velocity(content_data)
            
            # Calculate overall virality score
            virality_score = (
                prediction.content_quality_factor * self.model_weights['content_quality'] +
                prediction.timing_factor * self.model_weights['timing'] +
                prediction.trend_alignment_factor * self.model_weights['trend_alignment'] +
                prediction.creator_influence_factor * self.model_weights['creator_influence'] +
                prediction.platform_algorithm_factor * self.model_weights['platform_algorithm'] +
                prediction.engagement_velocity * self.model_weights['engagement_velocity']
            )
            
            prediction.virality_score = min(max(virality_score, 0.0), 1.0)
            
            # Generate predictions
            await self._generate_viral_predictions(prediction, content_data)
            
            # Generate recommendations
            await self._generate_viral_recommendations(prediction, content_data)
            
            return prediction
            
        except Exception as e:
            self.logger.error(f"Virality prediction failed: {e}")
            return ViralityPrediction(content_id=content_data.get('content_id', 'unknown'), prediction_date=datetime.now())
    
    async def _calculate_quality_factor(self, content_data: Dict[str, Any]) -> float:
        """Calculate content quality factor"""
        try:
            quality_score = content_data.get('quality_score', 0.5)
            resolution = content_data.get('resolution', '720p')
            duration = content_data.get('duration', 60)  # seconds
            
            # Resolution bonus
            resolution_bonus = 0.0
            if '1080p' in resolution or '1920' in str(resolution):
                resolution_bonus = 0.2
            elif '4K' in resolution or '2160' in str(resolution):
                resolution_bonus = 0.3
            
            # Duration factor (optimal around 60-180 seconds for viral content)
            if 30 <= duration <= 300:
                duration_factor = 1.0
            else:
                duration_factor = 0.8
            
            return min((quality_score + resolution_bonus) * duration_factor, 1.0)
            
        except Exception as e:
            self.logger.error(f"Quality factor calculation failed: {e}")
            return 0.5
    
    async def _calculate_timing_factor(self, content_data: Dict[str, Any]) -> float:
        """Calculate timing factor based on upload time"""
        try:
            upload_date = content_data.get('upload_date', datetime.now())
            
            # Optimal posting hours (generally 12-3pm and 7-9pm)
            hour = upload_date.hour
            if 12 <= hour <= 15 or 19 <= hour <= 21:
                hour_factor = 1.0
            elif 9 <= hour <= 11 or 16 <= hour <= 18:
                hour_factor = 0.8
            else:
                hour_factor = 0.6
            
            # Optimal days (Tuesday to Thursday generally better)
            weekday = upload_date.weekday()
            if 1 <= weekday <= 3:  # Tuesday to Thursday
                day_factor = 1.0
            elif weekday in [0, 4]:  # Monday, Friday
                day_factor = 0.8
            else:  # Weekend
                day_factor = 0.7
            
            return (hour_factor + day_factor) / 2
            
        except Exception as e:
            self.logger.error(f"Timing factor calculation failed: {e}")
            return 0.7
    
    async def _calculate_trend_alignment(self, content_data: Dict[str, Any], 
                                       current_trends: List[TrendData]) -> float:
        """Calculate alignment with current trends"""
        try:
            if not current_trends:
                return 0.5
            
            content_tags = [tag.lower() for tag in content_data.get('tags', [])]
            content_category = content_data.get('category', '').lower()
            content_title = content_data.get('title', '').lower()
            
            alignment_score = 0.0
            max_alignment = 0.0
            
            for trend in current_trends:
                trend_score = 0.0
                
                # Check keyword alignment
                for keyword in trend.related_keywords:
                    if keyword in content_tags or keyword in content_title:
                        trend_score += 0.3
                
                # Check category alignment
                if content_category in [cat.lower() for cat in trend.content_categories]:
                    trend_score += 0.4
                
                # Weight by trend strength
                if trend.strength == TrendStrength.EXPLOSIVE:
                    trend_score *= 1.5
                elif trend.strength == TrendStrength.STRONG:
                    trend_score *= 1.2
                
                max_alignment = max(max_alignment, trend_score)
            
            return min(max_alignment, 1.0)
            
        except Exception as e:
            self.logger.error(f"Trend alignment calculation failed: {e}")
            return 0.5
    
    async def _calculate_creator_influence(self, creator_profile: Optional[Dict[str, Any]]) -> float:
        """Calculate creator influence factor"""
        try:
            if not creator_profile:
                return 0.3  # Default for unknown creator
            
            followers = creator_profile.get('followers', 0)
            avg_engagement_rate = creator_profile.get('avg_engagement_rate', 0.02)
            viral_content_count = creator_profile.get('viral_content_count', 0)
            
            # Follower factor (logarithmic scale)
            if followers > 0:
                follower_factor = min(np.log10(followers) / 6.0, 1.0)  # Normalize to 1M followers
            else:
                follower_factor = 0.1
            
            # Engagement factor
            engagement_factor = min(avg_engagement_rate * 20, 1.0)  # Normalize to 5% engagement
            
            # Viral history factor
            viral_factor = min(viral_content_count / 10.0, 1.0)  # Normalize to 10 viral contents
            
            return (follower_factor * 0.5 + engagement_factor * 0.3 + viral_factor * 0.2)
            
        except Exception as e:
            self.logger.error(f"Creator influence calculation failed: {e}")
            return 0.3
    
    async def _calculate_platform_factor(self, content_data: Dict[str, Any]) -> float:
        """Calculate platform algorithm factor"""
        try:
            platform = content_data.get('platform', 'unknown').lower()
            
            # Platform-specific viral potential
            platform_factors = {
                'tiktok': 0.9,      # High viral potential
                'youtube': 0.8,     # Good viral potential
                'instagram': 0.7,   # Moderate viral potential
                'twitter': 0.6,     # Lower viral potential
                'facebook': 0.5,    # Declining viral potential
                'linkedin': 0.4     # Professional, lower viral potential
            }
            
            base_factor = platform_factors.get(platform, 0.6)
            
            # Content type optimization for platform
            content_type = content_data.get('content_type', 'video')
            
            if platform == 'tiktok' and content_type == 'video':
                base_factor *= 1.1
            elif platform == 'instagram' and content_type == 'image':
                base_factor *= 1.1
            elif platform == 'youtube' and content_type == 'video':
                base_factor *= 1.05
            
            return min(base_factor, 1.0)
            
        except Exception as e:
            self.logger.error(f"Platform factor calculation failed: {e}")
            return 0.6
    
    async def _calculate_engagement_velocity(self, content_data: Dict[str, Any]) -> float:
        """Calculate early engagement velocity"""
        try:
            # This would typically use real-time engagement data
            # For now, we'll use upload recency as a proxy
            
            upload_date = content_data.get('upload_date', datetime.now())
            hours_since_upload = (datetime.now() - upload_date).total_seconds() / 3600
            
            views = content_data.get('views', 0)
            likes = content_data.get('likes', 0)
            shares = content_data.get('shares', 0)
            
            if hours_since_upload > 0:
                views_per_hour = views / hours_since_upload
                engagement_per_hour = (likes + shares) / hours_since_upload
                
                # Normalize based on typical viral thresholds
                velocity_score = min(views_per_hour / 1000.0, 1.0) * 0.7 + min(engagement_per_hour / 100.0, 1.0) * 0.3
                
                return min(velocity_score, 1.0)
            
            return 0.5  # Default for brand new content
            
        except Exception as e:
            self.logger.error(f"Engagement velocity calculation failed: {e}")
            return 0.5
    
    async def _generate_viral_predictions(self, prediction -> None: ViralityPrediction, content_data -> None: Dict[str, Any]) -> None:
        """Generate specific viral predictions"""
        try:
            # Time to viral prediction
            if prediction.virality_score > 0.7:
                prediction.time_to_viral = timedelta(hours=6)
            elif prediction.virality_score > 0.5:
                prediction.time_to_viral = timedelta(hours=24)
            elif prediction.virality_score > 0.3:
                prediction.time_to_viral = timedelta(hours=72)
            
            # View predictions
            base_views = content_data.get('views', 0)
            
            if prediction.virality_score > 0.8:
                prediction.predicted_peak_views = max(base_views * 100, 1000000)
                prediction.predicted_total_views = max(base_views * 150, 1500000)
            elif prediction.virality_score > 0.6:
                prediction.predicted_peak_views = max(base_views * 50, 500000)
                prediction.predicted_total_views = max(base_views * 75, 750000)
            elif prediction.virality_score > 0.4:
                prediction.predicted_peak_views = max(base_views * 20, 100000)
                prediction.predicted_total_views = max(base_views * 30, 150000)
            
            # Confidence calculation
            factor_variance = np.var([
                prediction.content_quality_factor,
                prediction.timing_factor,
                prediction.trend_alignment_factor,
                prediction.creator_influence_factor,
                prediction.platform_algorithm_factor
            ])
            
            prediction.prediction_confidence = max(0.0, 1.0 - factor_variance * 2)
            
        except Exception as e:
            self.logger.error(f"Viral prediction generation failed: {e}")
    
    async def _generate_viral_recommendations(self, prediction -> None: ViralityPrediction, content_data -> None: Dict[str, Any]) -> None:
        """Generate optimization recommendations"""
        try:
            recommendations = []
            timing_recs = []
            
            # Quality recommendations
            if prediction.content_quality_factor < 0.7:
                recommendations.append("Improve video/audio quality and resolution")
                recommendations.append("Enhance visual appeal with better lighting/editing")
            
            # Timing recommendations
            if prediction.timing_factor < 0.7:
                timing_recs.append("Consider posting during peak hours (12-3pm or 7-9pm)")
                timing_recs.append("Tuesday to Thursday typically perform better")
            
            # Trend alignment recommendations
            if prediction.trend_alignment_factor < 0.5:
                recommendations.append("Incorporate trending hashtags and topics")
                recommendations.append("Align content with current popular themes")
            
            # Platform optimization
            if prediction.platform_algorithm_factor < 0.7:
                recommendations.append("Optimize content format for the specific platform")
                recommendations.append("Use platform-specific features and tools")
            
            # Engagement velocity recommendations
            if prediction.engagement_velocity < 0.5:
                recommendations.append("Add compelling hooks in the first few seconds")
                recommendations.append("Include clear calls-to-action for engagement")
            
            prediction.optimization_suggestions = recommendations
            prediction.timing_recommendations = timing_recs
            
        except Exception as e:
            self.logger.error(f"Viral recommendations generation failed: {e}")


class ContentTrendEngine:
    """Main content trend analysis engine combining all components"""
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        self.logger = logger.getChild(self.__class__.__name__)
        
        # Initialize components
        self.trend_analyzer = TrendAnalyzer(config)
        self.virality_predictor = ViralityPredictor(config)
        
    async def analyze_content_trends(self, content_data: List[Dict[str, Any]],
                                   creator_profiles: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Comprehensive content trend analysis"""
        try:
            analysis_result = {
                'analysis_timestamp': datetime.now(),
                'detected_trends': [],
                'virality_predictions': [],
                'lifecycle_analyses': [],
                'trend_insights': [],
                'recommendations': []
            }
            
            # Detect current trends
            detected_trends = await self.trend_analyzer.detect_trends(content_data)
            analysis_result['detected_trends'] = [trend.__dict__ for trend in detected_trends]
            
            # Generate virality predictions for recent content
            recent_content = [
                item for item in content_data
                if (datetime.now() - item.get('upload_date', datetime.now())).days < 1
            ]
            
            for content_item in recent_content[:10]:  # Limit to top 10 recent
                creator_profile = None
                if creator_profiles:
                    creator_id = content_item.get('creator_id')
                    creator_profile = next(
                        (profile for profile in creator_profiles if profile.get('creator_id') == creator_id),
                        None
                    )
                
                prediction = await self.virality_predictor.predict_virality(
                    content_item, detected_trends, creator_profile
                )
                analysis_result['virality_predictions'].append(prediction.__dict__)
            
            # Analyze content lifecycles
            for content_item in content_data[:5]:  # Top 5 content items
                lifecycle = await self.trend_analyzer.predict_content_lifecycle(
                    content_item['content_id'], content_item
                )
                analysis_result['lifecycle_analyses'].append(lifecycle.__dict__)
            
            # Generate insights and recommendations
            insights = await self._generate_trend_insights(detected_trends, analysis_result['virality_predictions'])
            analysis_result['trend_insights'] = insights
            
            recommendations = await self._generate_strategic_recommendations(detected_trends, analysis_result)
            analysis_result['recommendations'] = recommendations
            
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"Content trend analysis failed: {e}")
            return {'error': str(e), 'analysis_timestamp': datetime.now()}
    
    async def _generate_trend_insights(self, trends: List[TrendData], predictions: List[Dict[str, Any]]) -> List[str]:
        """Generate strategic insights from trend analysis"""
        insights = []
        
        try:
            # Trend strength insights
            strong_trends = [t for t in trends if t.strength in [TrendStrength.STRONG, TrendStrength.EXPLOSIVE]]
            if strong_trends:
                insights.append(f"Detected {len(strong_trends)} strong trends that could drive significant engagement")
            
            # Virality insights
            high_viral_predictions = [p for p in predictions if p.get('virality_score', 0) > 0.7]
            if high_viral_predictions:
                insights.append(f"{len(high_viral_predictions)} pieces of content have high viral potential")
            
            # Platform insights
            platform_trends = [t for t in trends if t.trend_type == TrendType.PLATFORM_SPECIFIC]
            if platform_trends:
                platforms = list(set([list(t.platform_distribution.keys())[0] for t in platform_trends if t.platform_distribution]))
                insights.append(f"Platform-specific trends detected on: {', '.join(platforms)}")
            
        except Exception as e:
            self.logger.error(f"Trend insights generation failed: {e}")
        
        return insights
    
    async def _generate_strategic_recommendations(self, trends: List[TrendData], analysis_result: Dict[str, Any]) -> List[str]:
        """Generate strategic recommendations"""
        recommendations = []
        
        try:
            # Trend-based recommendations
            if trends:
                trending_keywords = []
                for trend in trends:
                    trending_keywords.extend(trend.related_keywords)
                
                if trending_keywords:
                    top_keywords = list(set(trending_keywords))[:5]
                    recommendations.append(f"Incorporate trending keywords: {', '.join(top_keywords)}")
            
            # Quality-based recommendations
            predictions = analysis_result.get('virality_predictions', [])
            if predictions:
                avg_quality_factor = np.mean([p.get('content_quality_factor', 0.5) for p in predictions])
                
                if avg_quality_factor < 0.6:
                    recommendations.append("Focus on improving overall content quality for better viral potential")
            
            # Timing recommendations
            if predictions:
                avg_timing_factor = np.mean([p.get('timing_factor', 0.5) for p in predictions])
                
                if avg_timing_factor < 0.6:
                    recommendations.append("Optimize posting times for better reach and engagement")
            
            # Platform optimization
            platform_factors = [p.get('platform_algorithm_factor', 0.5) for p in predictions]
            if platform_factors and np.mean(platform_factors) < 0.6:
                recommendations.append("Optimize content format and strategy for specific platforms")
            
        except Exception as e:
            self.logger.error(f"Strategic recommendations generation failed: {e}")
        
        return recommendations