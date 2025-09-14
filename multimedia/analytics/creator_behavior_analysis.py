"""Creator Behavior Analysis Engine
Advanced creator behavior patterns, content strategy analysis, and performance optimization.

This module provides comprehensive creator behavior analysis including content patterns,
performance trends, audience insights, and optimization recommendations for content creators.

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
import statistics

logger = logging.getLogger(__name__)

class CreatorType(Enum):
    """Creator classification types"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    PROFESSIONAL = "professional"
    INFLUENCER = "influencer"

class ContentCategory(Enum):
    """Content category classifications"""
    ENTERTAINMENT = "entertainment"
    EDUCATION = "education"
    MUSIC = "music"
    GAMING = "gaming"
    LIFESTYLE = "lifestyle"
    BUSINESS = "business"
    TECHNOLOGY = "technology"
    TRAVEL = "travel"
    FOOD = "food"
    FITNESS = "fitness"
    ART = "art"
    NEWS = "news"

@dataclass
class CreatorProfile:
    """Comprehensive creator profile"""
    creator_id: str
    creator_name: str
    creation_date: datetime
    
    # Classification
    creator_type: CreatorType = CreatorType.BEGINNER
    primary_category: Optional[ContentCategory] = None
    secondary_categories: List[ContentCategory] = field(default_factory=list)
    
    # Content statistics
    total_content_created: int = 0
    total_views: int = 0
    total_likes: int = 0
    total_shares: int = 0
    total_comments: int = 0
    
    # Performance metrics
    average_quality_score: float = 0.0
    average_engagement_rate: float = 0.0
    viral_content_count: int = 0
    consistency_score: float = 0.0
    
    # Behavioral patterns
    posting_frequency: float = 0.0  # posts per day
    optimal_posting_hours: List[int] = field(default_factory=list)
    content_length_preference: str = "medium"  # short, medium, long
    platform_preferences: List[str] = field(default_factory=list)
    
    # Audience insights
    audience_size: int = 0
    audience_growth_rate: float = 0.0
    audience_demographics: Dict[str, Any] = field(default_factory=dict)
    audience_engagement_patterns: Dict[str, float] = field(default_factory=dict)
    
    # Content strategy
    content_themes: List[str] = field(default_factory=list)
    trending_topics_adoption: float = 0.0
    original_content_ratio: float = 0.0
    collaboration_frequency: float = 0.0
    
    # Performance trends
    performance_trend: str = "stable"  # growing, stable, declining
    best_performing_content_type: Optional[str] = None
    improvement_areas: List[str] = field(default_factory=list)
    
    # Monetization
    monetization_enabled: bool = False
    revenue_per_view: float = 0.0
    monetization_efficiency: float = 0.0

@dataclass
class ContentPattern:
    """Content creation pattern analysis"""
    pattern_id: str
    creator_id: str
    pattern_type: str  # temporal, thematic, format, quality
    
    description: str
    confidence: float = 0.0
    
    # Pattern details
    frequency: Optional[float] = None
    duration: Optional[timedelta] = None
    triggers: List[str] = field(default_factory=list)
    
    # Performance impact
    impact_on_views: float = 0.0
    impact_on_engagement: float = 0.0
    impact_on_quality: float = 0.0
    
    # Recommendations
    optimization_suggestions: List[str] = field(default_factory=list)
    
    # Metadata
    detection_date: datetime = field(default_factory=datetime.now)
    last_occurrence: Optional[datetime] = None

@dataclass
class TrendAnalysis:
    """Trend detection and analysis"""
    analysis_id: str
    analysis_date: datetime
    trend_type: str  # content, performance, audience, platform
    
    # Trend characteristics
    trend_direction: str  # up, down, stable, volatile
    trend_strength: float = 0.0
    trend_duration: Optional[timedelta] = None
    
    # Affected metrics
    affected_metrics: List[str] = field(default_factory=list)
    metric_changes: Dict[str, float] = field(default_factory=dict)
    
    # Predictions
    predicted_continuation: float = 0.0  # Probability trend continues
    forecasted_values: Dict[str, float] = field(default_factory=dict)
    
    # Influencing factors
    external_factors: List[str] = field(default_factory=list)
    seasonal_influence: float = 0.0
    platform_algorithm_impact: float = 0.0


class CreatorAnalyzer:
    """Main creator behavior analysis engine"""
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        self.logger = logger.getChild(self.__class__.__name__)
        
        # Data storage
        self.creator_profiles: Dict[str, CreatorProfile] = {}
        self.content_patterns: Dict[str, List[ContentPattern]] = defaultdict(list)
        self.trend_analyses: deque = deque(maxlen=1000)
        
        # Analysis parameters
        self.analysis_window_days = self.config.get('analysis_window_days', 30)
        self.pattern_confidence_threshold = self.config.get('pattern_confidence_threshold', 0.7)
        
        # Performance classification thresholds
        self.performance_thresholds = self.config.get('performance_thresholds', {
            'viral_view_threshold': 100000,
            'high_engagement_threshold': 0.05,
            'consistency_threshold': 0.8,
            'quality_threshold': 0.75
        })
    
    async def analyze_creator_behavior(self, creator_id: str, 
                                     content_data: List[Dict[str, Any]]) -> CreatorProfile:
        """Comprehensive creator behavior analysis"""
        try:
            # Initialize or update creator profile
            if creator_id in self.creator_profiles:
                profile = self.creator_profiles[creator_id]
            else:
                profile = CreatorProfile(
                    creator_id=creator_id,
                    creator_name=content_data[0].get('creator_name', f'Creator_{creator_id}'),
                    creation_date=datetime.now()
                )
                self.creator_profiles[creator_id] = profile
            
            # Analyze content statistics
            await self._analyze_content_statistics(profile, content_data)
            
            # Analyze behavioral patterns
            await self._analyze_behavioral_patterns(profile, content_data)
            
            # Analyze performance trends
            await self._analyze_performance_trends(profile, content_data)
            
            # Analyze audience insights
            await self._analyze_audience_insights(profile, content_data)
            
            # Generate content strategy insights
            await self._analyze_content_strategy(profile, content_data)
            
            # Classify creator type
            await self._classify_creator_type(profile)
            
            # Generate improvement recommendations
            await self._generate_improvement_recommendations(profile)
            
            return profile
            
        except Exception as e:
            self.logger.error(f"Creator behavior analysis failed for {creator_id}: {e}")
            raise
    
    async def _analyze_content_statistics(self, profile -> None: CreatorProfile, 
                                        content_data -> None: List[Dict[str, Any]]) -> None:
        """Analyze basic content statistics"""
        try:
            profile.total_content_created = len(content_data)
            
            if content_data:
                profile.total_views = sum(item.get('views', 0) for item in content_data)
                profile.total_likes = sum(item.get('likes', 0) for item in content_data)
                profile.total_shares = sum(item.get('shares', 0) for item in content_data)
                profile.total_comments = sum(item.get('comments', 0) for item in content_data)
                
                # Calculate average metrics
                quality_scores = [item.get('quality_score', 0) for item in content_data if item.get('quality_score')]
                if quality_scores:
                    profile.average_quality_score = np.mean(quality_scores)
                
                # Calculate engagement rate
                if profile.total_views > 0:
                    total_engagement = profile.total_likes + profile.total_shares + profile.total_comments
                    profile.average_engagement_rate = total_engagement / profile.total_views
                
                # Count viral content
                viral_threshold = self.performance_thresholds['viral_view_threshold']
                profile.viral_content_count = sum(1 for item in content_data if item.get('views', 0) > viral_threshold)
            
        except Exception as e:
            self.logger.error(f"Content statistics analysis failed: {e}")
    
    async def _analyze_behavioral_patterns(self, profile -> None: CreatorProfile, 
                                         content_data -> None: List[Dict[str, Any]]) -> None:
        """Analyze creator behavioral patterns"""
        try:
            if not content_data:
                return
            
            # Posting frequency analysis
            sorted_content = sorted(content_data, key=lambda x: x.get('upload_date', datetime.now()))
            
            if len(sorted_content) > 1:
                date_diffs = []
                for i in range(1, len(sorted_content)):
                    prev_date = sorted_content[i-1].get('upload_date')
                    curr_date = sorted_content[i].get('upload_date')
                    
                    if prev_date and curr_date:
                        diff = (curr_date - prev_date).total_seconds() / 86400  # days
                        date_diffs.append(diff)
                
                if date_diffs:
                    avg_interval = np.mean(date_diffs)
                    profile.posting_frequency = 1.0 / avg_interval if avg_interval > 0 else 0.0
                    
                    # Calculate consistency score
                    interval_std = np.std(date_diffs)
                    profile.consistency_score = 1.0 / (1.0 + interval_std / avg_interval) if avg_interval > 0 else 0.0
            
            # Optimal posting hours analysis
            upload_hours = []
            for item in content_data:
                upload_date = item.get('upload_date')
                if upload_date:
                    upload_hours.append(upload_date.hour)
            
            if upload_hours:
                # Find most common hours
                hour_counts = defaultdict(int)
                for hour in upload_hours:
                    hour_counts[hour] += 1
                
                # Get top 3 hours
                top_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:3]
                profile.optimal_posting_hours = [hour for hour, count in top_hours]
            
            # Content length preference
            lengths = [item.get('duration', 0) for item in content_data if item.get('duration')]
            if lengths:
                avg_length = np.mean(lengths)
                if avg_length < 60:  # Less than 1 minute
                    profile.content_length_preference = "short"
                elif avg_length < 300:  # Less than 5 minutes
                    profile.content_length_preference = "medium"
                else:
                    profile.content_length_preference = "long"
            
            # Platform preferences
            platforms = [item.get('platform') for item in content_data if item.get('platform')]
            if platforms:
                platform_counts = defaultdict(int)
                for platform in platforms:
                    platform_counts[platform] += 1
                
                sorted_platforms = sorted(platform_counts.items(), key=lambda x: x[1], reverse=True)
                profile.platform_preferences = [platform for platform, count in sorted_platforms[:3]]
            
        except Exception as e:
            self.logger.error(f"Behavioral patterns analysis failed: {e}")
    
    async def _analyze_performance_trends(self, profile -> None: CreatorProfile, 
                                        content_data -> None: List[Dict[str, Any]]) -> None:
        """Analyze performance trends over time"""
        try:
            if len(content_data) < 5:  # Need sufficient data
                return
            
            # Sort by date
            sorted_content = sorted(content_data, key=lambda x: x.get('upload_date', datetime.now()))
            
            # Analyze view trends
            views = [item.get('views', 0) for item in sorted_content]
            if views:
                # Simple trend analysis using linear regression
                x = np.arange(len(views))
                coeffs = np.polyfit(x, views, 1)
                trend_slope = coeffs[0]
                
                if trend_slope > 0.1 * np.mean(views):  # Significant positive trend
                    profile.performance_trend = "growing"
                elif trend_slope < -0.1 * np.mean(views):  # Significant negative trend
                    profile.performance_trend = "declining"
                else:
                    profile.performance_trend = "stable"
            
            # Analyze best performing content type
            content_types = defaultdict(list)
            for item in sorted_content:
                content_type = item.get('content_type', 'unknown')
                views = item.get('views', 0)
                content_types[content_type].append(views)
            
            if content_types:
                type_averages = {
                    content_type: np.mean(view_list)
                    for content_type, view_list in content_types.items()
                }
                
                best_type = max(type_averages.items(), key=lambda x: x[1])
                profile.best_performing_content_type = best_type[0]
            
        except Exception as e:
            self.logger.error(f"Performance trends analysis failed: {e}")
    
    async def _analyze_audience_insights(self, profile -> None: CreatorProfile, 
                                       content_data -> None: List[Dict[str, Any]]) -> None:
        """Analyze audience insights and growth patterns"""
        try:
            # Calculate audience size (using unique viewers as proxy)
            total_unique_viewers = set()
            for item in content_data:
                viewers = item.get('unique_viewers', [])
                total_unique_viewers.update(viewers)
            
            profile.audience_size = len(total_unique_viewers)
            
            # Analyze audience growth (simplified)
            if len(content_data) > 10:
                recent_content = content_data[-5:]  # Last 5 pieces
                older_content = content_data[-10:-5]  # Previous 5 pieces
                
                recent_avg_views = np.mean([item.get('views', 0) for item in recent_content])
                older_avg_views = np.mean([item.get('views', 0) for item in older_content])
                
                if older_avg_views > 0:
                    growth_rate = (recent_avg_views - older_avg_views) / older_avg_views
                    profile.audience_growth_rate = growth_rate
            
            # Analyze engagement patterns
            engagement_by_time = defaultdict(list)
            for item in content_data:
                upload_date = item.get('upload_date')
                if upload_date:
                    hour = upload_date.hour
                    views = item.get('views', 0)
                    likes = item.get('likes', 0)
                    
                    if views > 0:
                        engagement_rate = likes / views
                        engagement_by_time[hour].append(engagement_rate)
            
            # Calculate average engagement by time
            avg_engagement_by_time = {}
            for hour, rates in engagement_by_time.items():
                if rates:
                    avg_engagement_by_time[str(hour)] = np.mean(rates)
            
            profile.audience_engagement_patterns = avg_engagement_by_time
            
        except Exception as e:
            self.logger.error(f"Audience insights analysis failed: {e}")
    
    async def _analyze_content_strategy(self, profile -> None: CreatorProfile, 
                                      content_data -> None: List[Dict[str, Any]]) -> None:
        """Analyze content strategy and themes"""
        try:
            # Analyze content themes
            themes = []
            for item in content_data:
                tags = item.get('tags', [])
                title = item.get('title', '')
                description = item.get('description', '')
                
                # Extract themes from tags, title, and description
                # This is simplified - in practice would use NLP
                themes.extend(tags)
            
            if themes:
                theme_counts = defaultdict(int)
                for theme in themes:
                    theme_counts[theme.lower()] += 1
                
                # Get top themes
                top_themes = sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)[:10]
                profile.content_themes = [theme for theme, count in top_themes]
            
            # Analyze trending topics adoption
            # This would integrate with trend detection in practice
            profile.trending_topics_adoption = 0.7  # Placeholder
            
            # Analyze original vs adapted content
            original_content = sum(1 for item in content_data if item.get('is_original', True))
            if content_data:
                profile.original_content_ratio = original_content / len(content_data)
            
            # Analyze collaboration frequency
            collaborations = sum(1 for item in content_data if item.get('is_collaboration', False))
            if content_data:
                profile.collaboration_frequency = collaborations / len(content_data)
            
        except Exception as e:
            self.logger.error(f"Content strategy analysis failed: {e}")
    
    async def _classify_creator_type(self, profile -> None: CreatorProfile) -> None:
        """Classify creator type based on behavior and performance"""
        try:
            score = 0
            
            # Content volume factor
            if profile.total_content_created > 100:
                score += 2
            elif profile.total_content_created > 50:
                score += 1
            
            # Engagement factor
            if profile.average_engagement_rate > 0.05:
                score += 2
            elif profile.average_engagement_rate > 0.02:
                score += 1
            
            # Quality factor
            if profile.average_quality_score > 0.8:
                score += 2
            elif profile.average_quality_score > 0.6:
                score += 1
            
            # Consistency factor
            if profile.consistency_score > 0.8:
                score += 2
            elif profile.consistency_score > 0.6:
                score += 1
            
            # Viral content factor
            if profile.viral_content_count > 10:
                score += 2
            elif profile.viral_content_count > 0:
                score += 1
            
            # Classify based on score
            if score >= 8:
                profile.creator_type = CreatorType.PROFESSIONAL
            elif score >= 6:
                profile.creator_type = CreatorType.ADVANCED
            elif score >= 4:
                profile.creator_type = CreatorType.INTERMEDIATE
            else:
                profile.creator_type = CreatorType.BEGINNER
            
            # Special case for influencers
            if profile.audience_size > 100000 and profile.average_engagement_rate > 0.03:
                profile.creator_type = CreatorType.INFLUENCER
            
        except Exception as e:
            self.logger.error(f"Creator type classification failed: {e}")
    
    async def _generate_improvement_recommendations(self, profile -> None: CreatorProfile) -> None:
        """Generate personalized improvement recommendations"""
        try:
            recommendations = []
            
            # Quality recommendations
            if profile.average_quality_score < 0.7:
                recommendations.append("Focus on improving content quality through better equipment or editing")
            
            # Consistency recommendations
            if profile.consistency_score < 0.6:
                recommendations.append("Establish a more consistent posting schedule")
            
            # Engagement recommendations
            if profile.average_engagement_rate < 0.02:
                recommendations.append("Improve engagement by asking questions and encouraging comments")
            
            # Content strategy recommendations
            if profile.original_content_ratio < 0.8:
                recommendations.append("Focus on creating more original content")
            
            # Collaboration recommendations
            if profile.collaboration_frequency < 0.1:
                recommendations.append("Consider collaborating with other creators to expand reach")
            
            # Platform optimization
            if len(profile.platform_preferences) < 2:
                recommendations.append("Expand to additional platforms to increase reach")
            
            # Trending topics
            if profile.trending_topics_adoption < 0.5:
                recommendations.append("Stay updated with trending topics in your niche")
            
            profile.improvement_areas = recommendations
            
        except Exception as e:
            self.logger.error(f"Improvement recommendations generation failed: {e}")


class ContentPatternAnalyzer:
    """Content pattern detection and analysis"""
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        self.logger = logger.getChild(self.__class__.__name__)
    
    async def detect_content_patterns(self, creator_id: str, 
                                    content_data: List[Dict[str, Any]]) -> List[ContentPattern]:
        """Detect patterns in content creation behavior"""
        try:
            patterns = []
            
            # Temporal patterns
            temporal_patterns = await self._detect_temporal_patterns(creator_id, content_data)
            patterns.extend(temporal_patterns)
            
            # Thematic patterns
            thematic_patterns = await self._detect_thematic_patterns(creator_id, content_data)
            patterns.extend(thematic_patterns)
            
            # Quality patterns
            quality_patterns = await self._detect_quality_patterns(creator_id, content_data)
            patterns.extend(quality_patterns)
            
            # Performance patterns
            performance_patterns = await self._detect_performance_patterns(creator_id, content_data)
            patterns.extend(performance_patterns)
            
            return patterns
            
        except Exception as e:
            self.logger.error(f"Content pattern detection failed for {creator_id}: {e}")
            return []
    
    async def _detect_temporal_patterns(self, creator_id: str, 
                                      content_data: List[Dict[str, Any]]) -> List[ContentPattern]:
        """Detect temporal posting patterns"""
        patterns = []
        
        try:
            if len(content_data) < 10:
                return patterns
            
            # Extract posting times
            posting_times = []
            for item in content_data:
                upload_date = item.get('upload_date')
                if upload_date:
                    posting_times.append(upload_date)
            
            if not posting_times:
                return patterns
            
            # Analyze weekly patterns
            weekday_counts = defaultdict(int)
            for time in posting_times:
                weekday_counts[time.weekday()] += 1
            
            # Find dominant weekdays
            total_posts = len(posting_times)
            for weekday, count in weekday_counts.items():
                frequency = count / total_posts
                
                if frequency > 0.3:  # More than 30% of posts on this weekday
                    pattern = ContentPattern(
                        pattern_id=f"temporal_weekday_{weekday}_{creator_id}",
                        creator_id=creator_id,
                        pattern_type="temporal",
                        description=f"Prefers posting on weekday {weekday}",
                        confidence=frequency,
                        frequency=frequency
                    )
                    patterns.append(pattern)
            
            # Analyze hourly patterns
            hour_counts = defaultdict(int)
            for time in posting_times:
                hour_counts[time.hour] += 1
            
            for hour, count in hour_counts.items():
                frequency = count / total_posts
                
                if frequency > 0.2:  # More than 20% of posts at this hour
                    pattern = ContentPattern(
                        pattern_id=f"temporal_hour_{hour}_{creator_id}",
                        creator_id=creator_id,
                        pattern_type="temporal",
                        description=f"Prefers posting at hour {hour}",
                        confidence=frequency,
                        frequency=frequency
                    )
                    patterns.append(pattern)
            
        except Exception as e:
            self.logger.error(f"Temporal pattern detection failed: {e}")
        
        return patterns
    
    async def _detect_thematic_patterns(self, creator_id: str, 
                                      content_data: List[Dict[str, Any]]) -> List[ContentPattern]:
        """Detect thematic content patterns"""
        patterns = []
        
        try:
            # Extract themes/tags
            all_themes = []
            for item in content_data:
                tags = item.get('tags', [])
                all_themes.extend([tag.lower() for tag in tags])
            
            if not all_themes:
                return patterns
            
            # Analyze theme frequency
            theme_counts = defaultdict(int)
            for theme in all_themes:
                theme_counts[theme] += 1
            
            total_content = len(content_data)
            
            for theme, count in theme_counts.items():
                frequency = count / total_content
                
                if frequency > 0.3:  # Theme appears in more than 30% of content
                    pattern = ContentPattern(
                        pattern_id=f"thematic_{theme}_{creator_id}",
                        creator_id=creator_id,
                        pattern_type="thematic",
                        description=f"Frequently creates content about {theme}",
                        confidence=frequency,
                        frequency=frequency
                    )
                    patterns.append(pattern)
            
        except Exception as e:
            self.logger.error(f"Thematic pattern detection failed: {e}")
        
        return patterns
    
    async def _detect_quality_patterns(self, creator_id: str, 
                                     content_data: List[Dict[str, Any]]) -> List[ContentPattern]:
        """Detect quality-related patterns"""
        patterns = []
        
        try:
            quality_scores = [item.get('quality_score', 0) for item in content_data if item.get('quality_score')]
            
            if len(quality_scores) < 5:
                return patterns
            
            # Analyze quality trends
            avg_quality = np.mean(quality_scores)
            quality_std = np.std(quality_scores)
            
            if quality_std < 0.1:  # Very consistent quality
                pattern = ContentPattern(
                    pattern_id=f"quality_consistent_{creator_id}",
                    creator_id=creator_id,
                    pattern_type="quality",
                    description="Maintains consistent quality across content",
                    confidence=1.0 - quality_std,
                    optimization_suggestions=["Continue maintaining quality standards"]
                )
                patterns.append(pattern)
            
            elif quality_std > 0.3:  # Highly variable quality
                pattern = ContentPattern(
                    pattern_id=f"quality_variable_{creator_id}",
                    creator_id=creator_id,
                    pattern_type="quality",
                    description="Quality varies significantly across content",
                    confidence=quality_std,
                    optimization_suggestions=[
                        "Establish quality control processes",
                        "Review content before publishing"
                    ]
                )
                patterns.append(pattern)
            
        except Exception as e:
            self.logger.error(f"Quality pattern detection failed: {e}")
        
        return patterns
    
    async def _detect_performance_patterns(self, creator_id: str, 
                                         content_data: List[Dict[str, Any]]) -> List[ContentPattern]:
        """Detect performance-related patterns"""
        patterns = []
        
        try:
            # Analyze view patterns
            views = [item.get('views', 0) for item in content_data]
            
            if len(views) < 5:
                return patterns
            
            avg_views = np.mean(views)
            view_std = np.std(views)
            
            # Detect viral content pattern
            viral_threshold = avg_views + 2 * view_std
            viral_content = [v for v in views if v > viral_threshold]
            
            if len(viral_content) > len(views) * 0.1:  # More than 10% viral content
                pattern = ContentPattern(
                    pattern_id=f"performance_viral_{creator_id}",
                    creator_id=creator_id,
                    pattern_type="performance",
                    description="Regularly creates viral content",
                    confidence=len(viral_content) / len(views),
                    impact_on_views=float(np.mean(viral_content) - avg_views),
                    optimization_suggestions=["Analyze viral content elements for replication"]
                )
                patterns.append(pattern)
            
        except Exception as e:
            self.logger.error(f"Performance pattern detection failed: {e}")
        
        return patterns


class TrendDetector:
    """Trend detection and analysis for creator behavior"""
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        self.logger = logger.getChild(self.__class__.__name__)
    
    async def detect_trends(self, creator_profiles: List[CreatorProfile]) -> List[TrendAnalysis]:
        """Detect trends across creator behaviors"""
        try:
            trends = []
            
            # Performance trends
            performance_trends = await self._detect_performance_trends(creator_profiles)
            trends.extend(performance_trends)
            
            # Content trends
            content_trends = await self._detect_content_trends(creator_profiles)
            trends.extend(content_trends)
            
            # Audience trends
            audience_trends = await self._detect_audience_trends(creator_profiles)
            trends.extend(audience_trends)
            
            return trends
            
        except Exception as e:
            self.logger.error(f"Trend detection failed: {e}")
            return []
    
    async def _detect_performance_trends(self, profiles: List[CreatorProfile]) -> List[TrendAnalysis]:
        """Detect performance trends across creators"""
        trends = []
        
        try:
            if len(profiles) < 10:
                return trends
            
            # Analyze engagement rate trends
            engagement_rates = [p.average_engagement_rate for p in profiles if p.average_engagement_rate > 0]
            
            if engagement_rates:
                avg_engagement = np.mean(engagement_rates)
                engagement_std = np.std(engagement_rates)
                
                # Check for overall engagement trend
                high_engagement_creators = sum(1 for rate in engagement_rates if rate > avg_engagement + engagement_std)
                low_engagement_creators = sum(1 for rate in engagement_rates if rate < avg_engagement - engagement_std)
                
                if high_engagement_creators > len(engagement_rates) * 0.3:
                    trend = TrendAnalysis(
                        analysis_id=f"engagement_up_{int(datetime.now().timestamp())}",
                        analysis_date=datetime.now(),
                        trend_type="performance",
                        trend_direction="up",
                        trend_strength=high_engagement_creators / len(engagement_rates),
                        affected_metrics=["engagement_rate"],
                        metric_changes={"engagement_rate": avg_engagement}
                    )
                    trends.append(trend)
            
        except Exception as e:
            self.logger.error(f"Performance trend detection failed: {e}")
        
        return trends
    
    async def _detect_content_trends(self, profiles: List[CreatorProfile]) -> List[TrendAnalysis]:
        """Detect content creation trends"""
        trends = []
        
        try:
            # Analyze posting frequency trends
            posting_frequencies = [p.posting_frequency for p in profiles if p.posting_frequency > 0]
            
            if posting_frequencies:
                avg_frequency = np.mean(posting_frequencies)
                
                trend = TrendAnalysis(
                    analysis_id=f"posting_frequency_{int(datetime.now().timestamp())}",
                    analysis_date=datetime.now(),
                    trend_type="content",
                    trend_direction="stable",
                    trend_strength=0.8,
                    affected_metrics=["posting_frequency"],
                    metric_changes={"posting_frequency": avg_frequency}
                )
                trends.append(trend)
            
        except Exception as e:
            self.logger.error(f"Content trend detection failed: {e}")
        
        return trends
    
    async def _detect_audience_trends(self, profiles: List[CreatorProfile]) -> List[TrendAnalysis]:
        """Detect audience growth trends"""
        trends = []
        
        try:
            # Analyze audience growth trends
            growth_rates = [p.audience_growth_rate for p in profiles if p.audience_growth_rate != 0]
            
            if growth_rates:
                avg_growth = np.mean(growth_rates)
                
                if avg_growth > 0.1:  # More than 10% growth
                    trend = TrendAnalysis(
                        analysis_id=f"audience_growth_{int(datetime.now().timestamp())}",
                        analysis_date=datetime.now(),
                        trend_type="audience",
                        trend_direction="up",
                        trend_strength=avg_growth,
                        affected_metrics=["audience_growth_rate"],
                        metric_changes={"audience_growth_rate": avg_growth}
                    )
                    trends.append(trend)
            
        except Exception as e:
            self.logger.error(f"Audience trend detection failed: {e}")
        
        return trends