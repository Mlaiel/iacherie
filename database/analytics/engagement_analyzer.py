"""Engagement Analytics Module - IA Influencer Agent + Content Protection Platform

Advanced engagement analysis system for multi-format content creators with
real-time engagement tracking, sentiment analysis, and AI-powered insights.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

🚨 INTELLECTUAL PROPERTY WARNING: This code, concept, and architecture are 
the exclusive intellectual property of Fahed Mlaiel (mlaiel@live.de). 
Any use, copying, distribution, or exploitation without explicit written 
authorization is STRICTLY PROHIBITED and will be prosecuted.

Expert Project Team - Fahed Mlaiel:
- Lead AI Developer & Software Architect
- Senior Backend Engineer (Python/FastAPI/Django)  
- Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face)
- Database Administrator & Data Engineer (PostgreSQL/Redis/MongoDB)
- Backend Security Specialist
- Microservices Architect
- Audio Processing Engineer
- DevOps Engineer
- AI Prompt Engineer
"""import uuid
import json
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from decimal import Decimal
from sqlalchemy import Column, String, DateTime, JSON, Boolean, Integer, Text, Index, BigInteger, Numeric, Float
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
import logging
import numpy as np
from collections import defaultdict
import statistics

Base = declarative_base()
logger = logging.getLogger(__name__)


class EngagementType(Enum):
    """Types of engagement interactions"""    LIKE = "like"
    COMMENT = "comment"
    SHARE = "share"
    SAVE = "save"
    CLICK = "click"
    VIEW = "view"
    FOLLOW = "follow"
    MENTION = "mention"
    STORY_VIEW = "story_view"
    REEL_WATCH = "reel_watch"


class SentimentType(Enum):
    """Sentiment analysis types"""    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"


class EngagementMetric(Base):
    """    Enterprise-grade engagement metrics tracking model
    
    Stores detailed engagement data with advanced analytics capabilities
    for multi-platform content performance analysis.
    """    __tablename__ = "engagement_metrics"
    
    # Primary identifiers
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, nullable=False, index=True)
    content_id = Column(String(255), nullable=False, index=True)
    platform = Column(String(50), nullable=False, index=True)
    
    # Engagement data
    engagement_type = Column(String(20), nullable=False)
    engagement_value = Column(BigInteger, default=0)
    engagement_rate = Column(Numeric(10, 6))
    unique_engagers = Column(Integer, default=0)
    
    # Time-based metrics
    measurement_timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    time_period = Column(String(20), default="hourly")  # hourly, daily, weekly
    
    # Advanced metrics
    engagement_velocity = Column(Numeric(10, 4))  # Rate of change
    engagement_quality_score = Column(Numeric(5, 2))
    viral_coefficient = Column(Numeric(8, 4))
    
    # Demographic breakdowns
    age_distribution = Column(JSON)
    gender_distribution = Column(JSON)
    geographic_distribution = Column(JSON)
    device_distribution = Column(JSON)
    
    # Sentiment and content analysis
    sentiment_score = Column(Numeric(5, 2))
    sentiment_distribution = Column(JSON)
    content_elements = Column(JSON)
    
    # AI-derived insights
    ai_insights = Column(JSON)
    optimization_suggestions = Column(JSON)
    trend_indicators = Column(JSON)
    
    # Performance benchmarking
    industry_percentile = Column(Numeric(5, 2))
    competitor_comparison = Column(JSON)
    platform_benchmark = Column(Numeric(10, 6))
    
    # Metadata
    data_source = Column(String(100))
    confidence_score = Column(Numeric(5, 2))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_engagement_user_platform', 'user_id', 'platform'),
        Index('idx_engagement_content_time', 'content_id', 'measurement_timestamp'),
        Index('idx_engagement_type_time', 'engagement_type', 'measurement_timestamp'),
    )


@dataclass
class EngagementInsight:
    """Data class for engagement insights"""    insight_type: str
    title: str
    description: str
    confidence: float
    impact_score: float
    actionable_recommendations: List[str]
    supporting_data: Dict[str, Any]
    trend_direction: str  # increasing, decreasing, stable
    time_frame: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""        return {
            "insight_type": self.insight_type,
            "title": self.title,
            "description": self.description,
            "confidence": self.confidence,
            "impact_score": self.impact_score,
            "actionable_recommendations": self.actionable_recommendations,
            "supporting_data": self.supporting_data,
            "trend_direction": self.trend_direction,
            "time_frame": self.time_frame
        }


@dataclass
class AudienceInsights:
    """Comprehensive audience insights data class"""    total_audience_size: int
    active_audience_percentage: float
    audience_growth_rate: float
    engagement_distribution: Dict[str, float]
    top_content_themes: List[str]
    optimal_posting_times: List[str]
    audience_sentiment: Dict[str, float]
    demographic_breakdown: Dict[str, Any]
    behavioral_patterns: Dict[str, Any]
    retention_metrics: Dict[str, float]
    influence_score: float
    community_health_score: float


class EngagementAnalyzer:
    """    Enterprise-grade engagement analytics engine
    
    Provides comprehensive engagement analysis with AI-powered insights,
    sentiment analysis, and predictive capabilities for content optimization.
    """    
    def __init__(self, db_session: Session):
        """        Initialize engagement analyzer with database session
        
        Args:
            db_session: Database session for analytics operations
        """        self.db = db_session
        self.logger = logging.getLogger(__name__)
    
    async def record_engagement(
        self,
        user_id: int,
        content_id: str,
        platform: str,
        engagement_data: Dict[str, Any]
    ) -> EngagementMetric:
        """        Record new engagement data with comprehensive metrics
        
        Args:
            user_id: User identifier
            content_id: Content identifier  
            platform: Platform name
            engagement_data: Engagement metrics data
            
        Returns:
            Created engagement metric record
        """        try:
            # Calculate derived metrics
            engagement_rate = self._calculate_engagement_rate(engagement_data)
            quality_score = self._calculate_quality_score(engagement_data)
            viral_coefficient = self._calculate_viral_coefficient(engagement_data)
            
            # Create engagement metric record
            engagement_metric = EngagementMetric(
                user_id=user_id,
                content_id=content_id,
                platform=platform,
                engagement_type=engagement_data.get("type", "general"),
                engagement_value=engagement_data.get("value", 0),
                engagement_rate=engagement_rate,
                unique_engagers=engagement_data.get("unique_engagers", 0),
                measurement_timestamp=engagement_data.get("timestamp", datetime.utcnow()),
                time_period=engagement_data.get("time_period", "hourly"),
                engagement_velocity=engagement_data.get("velocity"),
                engagement_quality_score=quality_score,
                viral_coefficient=viral_coefficient,
                age_distribution=engagement_data.get("age_distribution"),
                gender_distribution=engagement_data.get("gender_distribution"),
                geographic_distribution=engagement_data.get("geographic_distribution"),
                device_distribution=engagement_data.get("device_distribution"),
                sentiment_score=engagement_data.get("sentiment_score"),
                sentiment_distribution=engagement_data.get("sentiment_distribution"),
                content_elements=engagement_data.get("content_elements"),
                ai_insights=engagement_data.get("ai_insights"),
                optimization_suggestions=engagement_data.get("optimization_suggestions"),
                trend_indicators=engagement_data.get("trend_indicators"),
                industry_percentile=engagement_data.get("industry_percentile"),
                competitor_comparison=engagement_data.get("competitor_comparison"),
                platform_benchmark=engagement_data.get("platform_benchmark"),
                data_source=engagement_data.get("data_source", "api"),
                confidence_score=engagement_data.get("confidence_score", 0.8)
            )
            
            self.db.add(engagement_metric)
            self.db.commit()
            
            self.logger.info(f"Recorded engagement for user {user_id}, content {content_id}")
            return engagement_metric
            
        except Exception as e:
            self.logger.error(f"Failed to record engagement: {str(e)}")
            self.db.rollback()
            raise
    
    def _calculate_engagement_rate(self, engagement_data: Dict[str, Any]) -> float:
        """Calculate engagement rate from raw data"""        total_engagement = engagement_data.get("total_engagement", 0)
        total_reach = engagement_data.get("total_reach", 1)
        
        if total_reach == 0:
            return 0.0
        
        return float(total_engagement / total_reach)
    
    def _calculate_quality_score(self, engagement_data: Dict[str, Any]) -> float:
        """Calculate engagement quality score"""        # Factors: comment ratio, share ratio, save ratio, time spent
        comments = engagement_data.get("comments", 0)
        shares = engagement_data.get("shares", 0) 
        saves = engagement_data.get("saves", 0)
        likes = engagement_data.get("likes", 0)
        views = engagement_data.get("views", 1)
        
        # Weight different engagement types
        comment_weight = 3.0
        share_weight = 2.5
        save_weight = 2.0
        like_weight = 1.0
        
        quality_score = (
            (comments * comment_weight + 
             shares * share_weight + 
             saves * save_weight + 
             likes * like_weight) / (views * 10)
        ) * 100
        
        return min(100.0, quality_score)  # Cap at 100
    
    def _calculate_viral_coefficient(self, engagement_data: Dict[str, Any]) -> float:
        """Calculate viral coefficient for content"""        shares = engagement_data.get("shares", 0)
        original_reach = engagement_data.get("original_reach", 1)
        secondary_reach = engagement_data.get("secondary_reach", 0)
        
        if original_reach == 0:
            return 0.0
        
        viral_coefficient = (shares + secondary_reach) / original_reach
        return viral_coefficient
    
    async def analyze_engagement_trends(
        self,
        user_id: int,
        days_back: int = 30,
        platform: Optional[str] = None
    ) -> List[EngagementInsight]:
        """        Analyze engagement trends with AI-powered insights
        
        Args:
            user_id: User identifier
            days_back: Number of days to analyze
            platform: Specific platform filter
            
        Returns:
            List of engagement insights
        """        try:
            # Build query filters
            filters = [EngagementMetric.user_id == user_id]
            
            start_date = datetime.utcnow() - timedelta(days=days_back)
            filters.append(EngagementMetric.measurement_timestamp >= start_date)
            
            if platform:
                filters.append(EngagementMetric.platform == platform)
            
            # Get engagement data
            engagement_data = self.db.query(EngagementMetric).filter(*filters).all()
            
            if not engagement_data:
                return []
            
            # Analyze trends
            insights = []
            
            # Trend analysis
            trend_insight = await self._analyze_trend_patterns(engagement_data)
            if trend_insight:
                insights.append(trend_insight)
            
            # Platform performance analysis
            platform_insight = await self._analyze_platform_performance(engagement_data)
            if platform_insight:
                insights.append(platform_insight)
            
            # Content type performance
            content_insight = await self._analyze_content_performance(engagement_data)
            if content_insight:
                insights.append(content_insight)
            
            # Audience behavior patterns
            behavior_insight = await self._analyze_audience_behavior(engagement_data)
            if behavior_insight:
                insights.append(behavior_insight)
            
            # Optimization opportunities
            optimization_insight = await self._identify_optimization_opportunities(engagement_data)
            if optimization_insight:
                insights.append(optimization_insight)
            
            self.logger.info(f"Generated {len(insights)} engagement insights for user {user_id}")
            return insights
            
        except Exception as e:
            self.logger.error(f"Failed to analyze engagement trends: {str(e)}")
            raise
    
    async def _analyze_trend_patterns(self, engagement_data: List[EngagementMetric]) -> Optional[EngagementInsight]:
        """Analyze engagement trend patterns"""        
        if len(engagement_data) < 7:  # Need minimum data points
            return None
        
        # Calculate trend over time
        daily_engagement = defaultdict(list)
        
        for metric in engagement_data:
            day = metric.measurement_timestamp.date()
            daily_engagement[day].append(float(metric.engagement_rate) if metric.engagement_rate else 0)
        
        # Calculate daily averages
        daily_averages = []
        sorted_days = sorted(daily_engagement.keys())
        
        for day in sorted_days:
            avg_engagement = statistics.mean(daily_engagement[day])
            daily_averages.append(avg_engagement)
        
        # Analyze trend direction
        if len(daily_averages) < 3:
            return None
        
        recent_avg = statistics.mean(daily_averages[-3:])  # Last 3 days
        earlier_avg = statistics.mean(daily_averages[:3])  # First 3 days
        
        change_percentage = ((recent_avg - earlier_avg) / earlier_avg * 100) if earlier_avg > 0 else 0
        
        if abs(change_percentage) < 5:
            trend_direction = "stable"
            title = "Engagement Remains Stable"
            description = f"Engagement rate has remained relatively stable with {change_percentage:.1f}% change"
        elif change_percentage > 0:
            trend_direction = "increasing"
            title = "Positive Engagement Trend"
            description = f"Engagement rate has increased by {change_percentage:.1f}% over the analysis period"
        else:
            trend_direction = "decreasing" 
            title = "Declining Engagement Trend"
            description = f"Engagement rate has decreased by {abs(change_percentage):.1f}% over the analysis period"
        
        recommendations = []
        if trend_direction == "increasing":
            recommendations = [
                "Continue current content strategy",
                "Analyze successful content elements for replication",
                "Consider increasing posting frequency"
            ]
        elif trend_direction == "decreasing":
            recommendations = [
                "Review recent content performance",
                "Test new content formats and styles",
                "Analyze audience feedback for improvement opportunities",
                "Consider adjusting posting schedule"
            ]
        else:
            recommendations = [
                "Test new content variations to boost engagement",
                "Experiment with different posting times",
                "Analyze competitor strategies for inspiration"
            ]
        
        return EngagementInsight(
            insight_type="trend_analysis",
            title=title,
            description=description,
            confidence=0.8,
            impact_score=abs(change_percentage) / 10,  # Normalize to 0-10 scale
            actionable_recommendations=recommendations,
            supporting_data={
                "change_percentage": change_percentage,
                "recent_average": recent_avg,
                "earlier_average": earlier_avg,
                "data_points": len(daily_averages)
            },
            trend_direction=trend_direction,
            time_frame=f"{len(sorted_days)} days"
        )
    
    async def _analyze_platform_performance(self, engagement_data: List[EngagementMetric]) -> Optional[EngagementInsight]:
        """Analyze performance across different platforms"""        
        platform_metrics = defaultdict(list)
        
        for metric in engagement_data:
            if metric.engagement_rate:
                platform_metrics[metric.platform].append(float(metric.engagement_rate))
        
        if len(platform_metrics) < 2:
            return None
        
        # Calculate platform averages
        platform_averages = {}
        for platform, rates in platform_metrics.items():
            platform_averages[platform] = statistics.mean(rates)
        
        # Find best and worst performing platforms
        best_platform = max(platform_averages, key=platform_averages.get)
        worst_platform = min(platform_averages, key=platform_averages.get)
        
        best_rate = platform_averages[best_platform]
        worst_rate = platform_averages[worst_platform]
        
        improvement_potential = ((best_rate - worst_rate) / worst_rate * 100) if worst_rate > 0 else 0
        
        return EngagementInsight(
            insight_type="platform_performance",
            title=f"Platform Performance Analysis",
            description=f"{best_platform.title()} is your best performing platform with {best_rate:.2%} average engagement",
            confidence=0.9,
            impact_score=improvement_potential / 20,  # Normalize
            actionable_recommendations=[
                f"Focus more content efforts on {best_platform}",
                f"Analyze what works well on {best_platform} and apply to other platforms",
                f"Consider reducing content frequency on {worst_platform} or improving content quality",
                "Test cross-platform content adaptation strategies"
            ],
            supporting_data={
                "platform_averages": platform_averages,
                "best_platform": best_platform,
                "worst_platform": worst_platform,
                "improvement_potential": improvement_potential
            },
            trend_direction="stable",
            time_frame="current_period"
        )
    
    async def _analyze_content_performance(self, engagement_data: List[EngagementMetric]) -> Optional[EngagementInsight]:
        """Analyze content type performance patterns"""        
        # Analyze content elements if available
        content_performance = defaultdict(list)
        
        for metric in engagement_data:
            if metric.content_elements and metric.engagement_rate:
                content_type = metric.content_elements.get("type", "unknown")
                content_performance[content_type].append(float(metric.engagement_rate))
        
        if not content_performance:
            return None
        
        # Calculate content type averages
        content_averages = {}
        for content_type, rates in content_performance.items():
            if rates:  # Only if we have data
                content_averages[content_type] = statistics.mean(rates)
        
        if not content_averages:
            return None
        
        # Find best performing content type
        best_content_type = max(content_averages, key=content_averages.get)
        best_rate = content_averages[best_content_type]
        
        return EngagementInsight(
            insight_type="content_performance",
            title=f"Top Content Type: {best_content_type.title()}",
            description=f"{best_content_type.title()} content generates {best_rate:.2%} average engagement",
            confidence=0.85,
            impact_score=7.5,
            actionable_recommendations=[
                f"Create more {best_content_type} content",
                f"Analyze successful {best_content_type} posts for common elements",
                "Test variations within this content type",
                "Consider dedicating specific days to this content type"
            ],
            supporting_data={
                "content_averages": content_averages,
                "best_content_type": best_content_type,
                "sample_size": {ct: len(rates) for ct, rates in content_performance.items()}
            },
            trend_direction="stable",
            time_frame="current_period"
        )
    
    async def _analyze_audience_behavior(self, engagement_data: List[EngagementMetric]) -> Optional[EngagementInsight]:
        """Analyze audience behavior patterns"""        
        # Analyze posting time performance
        hourly_performance = defaultdict(list)
        
        for metric in engagement_data:
            if metric.engagement_rate and metric.measurement_timestamp:
                hour = metric.measurement_timestamp.hour
                hourly_performance[hour].append(float(metric.engagement_rate))
        
        if not hourly_performance:
            return None
        
        # Calculate hourly averages
        hourly_averages = {}
        for hour, rates in hourly_performance.items():
            hourly_averages[hour] = statistics.mean(rates)
        
        # Find best performing hours
        sorted_hours = sorted(hourly_averages.items(), key=lambda x: x[1], reverse=True)
        best_hours = sorted_hours[:3]  # Top 3 hours
        
        best_hours_str = ", ".join([f"{hour}:00" for hour, _ in best_hours])
        
        return EngagementInsight(
            insight_type="audience_behavior",
            title="Optimal Posting Times Identified",
            description=f"Your audience is most active at {best_hours_str}",
            confidence=0.8,
            impact_score=6.0,
            actionable_recommendations=[
                f"Schedule more content during peak hours: {best_hours_str}",
                "Test content performance at different times",
                "Consider audience timezone differences",
                "Use scheduling tools to maintain consistency"
            ],
            supporting_data={
                "hourly_averages": hourly_averages,
                "best_hours": best_hours,
                "total_time_points": len(hourly_performance)
            },
            trend_direction="stable",
            time_frame="daily_patterns"
        )
    
    async def _identify_optimization_opportunities(self, engagement_data: List[EngagementMetric]) -> Optional[EngagementInsight]:
        """Identify specific optimization opportunities"""        
        # Analyze quality scores and identify improvement areas
        quality_scores = [
            float(metric.engagement_quality_score) 
            for metric in engagement_data 
            if metric.engagement_quality_score
        ]
        
        if not quality_scores:
            return None
        
        avg_quality = statistics.mean(quality_scores)
        
        # Determine optimization focus based on quality score
        if avg_quality < 30:
            focus_area = "content_quality"
            title = "Focus on Content Quality Improvement" 
            description = f"Average quality score ({avg_quality:.1f}/100) indicates significant room for improvement"
            recommendations = [
                "Improve content production value and storytelling",
                "Focus on creating more engaging hooks",
                "Increase content depth and value proposition",
                "Test different content formats and styles"
            ]
        elif avg_quality < 60:
            focus_area = "engagement_optimization"
            title = "Optimize Engagement Tactics"
            description = f"Quality score ({avg_quality:.1f}/100) shows moderate performance with optimization potential"
            recommendations = [
                "Add more interactive elements to content",
                "Improve call-to-action effectiveness", 
                "Test different posting frequencies",
                "Engage more actively with audience comments"
            ]
        else:
            focus_area = "growth_acceleration"
            title = "Scale High-Quality Performance"
            description = f"Strong quality score ({avg_quality:.1f}/100) suggests readiness for growth acceleration"
            recommendations = [
                "Increase content frequency while maintaining quality",
                "Expand to additional platforms or formats",
                "Develop content series and campaigns",
                "Consider paid promotion for top-performing content"
            ]
        
        return EngagementInsight(
            insight_type="optimization_opportunity",
            title=title,
            description=description,
            confidence=0.9,
            impact_score=8.0,
            actionable_recommendations=recommendations,
            supporting_data={
                "average_quality_score": avg_quality,
                "focus_area": focus_area,
                "sample_size": len(quality_scores)
            },
            trend_direction="stable",
            time_frame="optimization_focus"
        )
    
    async def generate_audience_insights(
        self,
        user_id: int,
        analysis_period_days: int = 30
    ) -> AudienceInsights:
        """        Generate comprehensive audience insights
        
        Args:
            user_id: User identifier
            analysis_period_days: Period for analysis
            
        Returns:
            Comprehensive audience insights
        """        try:
            # Get engagement data for analysis period
            start_date = datetime.utcnow() - timedelta(days=analysis_period_days)
            
            engagement_data = self.db.query(EngagementMetric).filter(
                EngagementMetric.user_id == user_id,
                EngagementMetric.measurement_timestamp >= start_date
            ).all()
            
            if not engagement_data:
                # Return default insights for new users
                return AudienceInsights(
                    total_audience_size=0,
                    active_audience_percentage=0.0,
                    audience_growth_rate=0.0,
                    engagement_distribution={},
                    top_content_themes=[],
                    optimal_posting_times=[],
                    audience_sentiment={"positive": 0, "neutral": 0, "negative": 0},
                    demographic_breakdown={},
                    behavioral_patterns={},
                    retention_metrics={},
                    influence_score=0.0,
                    community_health_score=0.0
                )
            
            # Calculate comprehensive metrics
            total_audience = self._calculate_total_audience_size(engagement_data)
            active_percentage = self._calculate_active_audience_percentage(engagement_data)
            growth_rate = self._calculate_audience_growth_rate(engagement_data)
            engagement_dist = self._calculate_engagement_distribution(engagement_data)
            content_themes = self._extract_top_content_themes(engagement_data)
            optimal_times = self._identify_optimal_posting_times(engagement_data)
            sentiment = self._analyze_audience_sentiment(engagement_data)
            demographics = self._analyze_demographic_breakdown(engagement_data)
            behavioral = self._analyze_behavioral_patterns(engagement_data)
            retention = self._calculate_retention_metrics(engagement_data)
            influence = self._calculate_influence_score(engagement_data)
            community_health = self._calculate_community_health_score(engagement_data)
            
            return AudienceInsights(
                total_audience_size=total_audience,
                active_audience_percentage=active_percentage,
                audience_growth_rate=growth_rate,
                engagement_distribution=engagement_dist,
                top_content_themes=content_themes,
                optimal_posting_times=optimal_times,
                audience_sentiment=sentiment,
                demographic_breakdown=demographics,
                behavioral_patterns=behavioral,
                retention_metrics=retention,
                influence_score=influence,
                community_health_score=community_health
            )
            
        except Exception as e:
            self.logger.error(f"Failed to generate audience insights: {str(e)}")
            raise
    
    def _calculate_total_audience_size(self, engagement_data: List[EngagementMetric]) -> int:
        """Calculate total audience size from engagement data"""        unique_engagers = set()
        
        for metric in engagement_data:
            if metric.unique_engagers:
                unique_engagers.add(metric.unique_engagers)
        
        # Estimate total audience (engagers are typically 3-10% of total audience)
        total_engagers = len(unique_engagers)
        estimated_total = int(total_engagers * 15)  # Conservative multiplier
        
        return estimated_total
    
    def _calculate_active_audience_percentage(self, engagement_data: List[EngagementMetric]) -> float:
        """Calculate active audience percentage"""        if not engagement_data:
            return 0.0
        
        # Calculate based on recent engagement patterns
        recent_data = [m for m in engagement_data if m.measurement_timestamp >= datetime.utcnow() - timedelta(days=7)]
        
        if not recent_data:
            return 0.0
        
        total_engagers = sum(m.unique_engagers or 0 for m in recent_data)
        total_audience = self._calculate_total_audience_size(engagement_data)
        
        if total_audience == 0:
            return 0.0
        
        return min(100.0, (total_engagers / total_audience) * 100)
    
    def _calculate_audience_growth_rate(self, engagement_data: List[EngagementMetric]) -> float:
        """Calculate audience growth rate"""        if len(engagement_data) < 14:  # Need at least 2 weeks of data
            return 0.0
        
        # Compare first week vs last week
        mid_date = datetime.utcnow() - timedelta(days=7)
        
        early_data = [m for m in engagement_data if m.measurement_timestamp < mid_date]
        recent_data = [m for m in engagement_data if m.measurement_timestamp >= mid_date]
        
        if not early_data or not recent_data:
            return 0.0
        
        early_audience = self._calculate_total_audience_size(early_data)
        recent_audience = self._calculate_total_audience_size(recent_data)
        
        if early_audience == 0:
            return 0.0
        
        growth_rate = ((recent_audience - early_audience) / early_audience) * 100
        return growth_rate
    
    def _calculate_engagement_distribution(self, engagement_data: List[EngagementMetric]) -> Dict[str, float]:
        """Calculate engagement type distribution"""        engagement_counts = defaultdict(int)
        total_engagement = 0
        
        for metric in engagement_data:
            engagement_counts[metric.engagement_type] += metric.engagement_value or 0
            total_engagement += metric.engagement_value or 0
        
        if total_engagement == 0:
            return {}
        
        # Convert to percentages
        distribution = {
            eng_type: (count / total_engagement) * 100
            for eng_type, count in engagement_counts.items()
        }
        
        return distribution
    
    def _extract_top_content_themes(self, engagement_data: List[EngagementMetric]) -> List[str]:
        """Extract top content themes from content elements"""        theme_performance = defaultdict(list)
        
        for metric in engagement_data:
            if metric.content_elements and metric.engagement_rate:
                themes = metric.content_elements.get("themes", [])
                for theme in themes:
                    theme_performance[theme].append(float(metric.engagement_rate))
        
        # Calculate average performance per theme
        theme_averages = {
            theme: statistics.mean(rates)
            for theme, rates in theme_performance.items()
            if rates
        }
        
        # Return top 5 themes by performance
        sorted_themes = sorted(theme_averages.items(), key=lambda x: x[1], reverse=True)
        return [theme for theme, _ in sorted_themes[:5]]
    
    def _identify_optimal_posting_times(self, engagement_data: List[EngagementMetric]) -> List[str]:
        """Identify optimal posting times"""        hourly_performance = defaultdict(list)
        
        for metric in engagement_data:
            if metric.engagement_rate and metric.measurement_timestamp:
                hour = metric.measurement_timestamp.hour
                hourly_performance[hour].append(float(metric.engagement_rate))
        
        # Calculate hourly averages
        hourly_averages = {
            hour: statistics.mean(rates)
            for hour, rates in hourly_performance.items()
            if rates
        }
        
        # Return top 3 hours formatted as time strings
        sorted_hours = sorted(hourly_averages.items(), key=lambda x: x[1], reverse=True)
        optimal_times = [f"{hour:02d}:00" for hour, _ in sorted_hours[:3]]
        
        return optimal_times
    
    def _analyze_audience_sentiment(self, engagement_data: List[EngagementMetric]) -> Dict[str, float]:
        """Analyze overall audience sentiment"""        sentiment_scores = []
        
        for metric in engagement_data:
            if metric.sentiment_score:
                sentiment_scores.append(float(metric.sentiment_score))
        
        if not sentiment_scores:
            return {"positive": 0, "neutral": 0, "negative": 0}
        
        avg_sentiment = statistics.mean(sentiment_scores)
        
        # Distribute sentiment (simplified model)
        if avg_sentiment > 0.1:
            return {"positive": 70, "neutral": 25, "negative": 5}
        elif avg_sentiment < -0.1:
            return {"positive": 15, "neutral": 35, "negative": 50}
        else:
            return {"positive": 40, "neutral": 50, "negative": 10}
    
    def _analyze_demographic_breakdown(self, engagement_data: List[EngagementMetric]) -> Dict[str, Any]:
        """Analyze demographic breakdown"""        demographics = {
            "age_groups": {},
            "gender_distribution": {},
            "geographic_regions": {},
            "device_types": {}
        }
        
        # Aggregate demographic data
        for metric in engagement_data:
            if metric.age_distribution:
                for age_group, count in metric.age_distribution.items():
                    demographics["age_groups"][age_group] = demographics["age_groups"].get(age_group, 0) + count
            
            if metric.gender_distribution:
                for gender, count in metric.gender_distribution.items():
                    demographics["gender_distribution"][gender] = demographics["gender_distribution"].get(gender, 0) + count
            
            if metric.geographic_distribution:
                for region, count in metric.geographic_distribution.items():
                    demographics["geographic_regions"][region] = demographics["geographic_regions"].get(region, 0) + count
            
            if metric.device_distribution:
                for device, count in metric.device_distribution.items():
                    demographics["device_types"][device] = demographics["device_types"].get(device, 0) + count
        
        return demographics
    
    def _analyze_behavioral_patterns(self, engagement_data: List[EngagementMetric]) -> Dict[str, Any]:
        """Analyze audience behavioral patterns"""        patterns = {
            "peak_activity_hours": [],
            "engagement_frequency": "regular",
            "content_preference_patterns": {},
            "interaction_style": "mixed"
        }
        
        # Analyze time-based patterns
        hourly_activity = defaultdict(int)
        for metric in engagement_data:
            if metric.measurement_timestamp:
                hour = metric.measurement_timestamp.hour
                hourly_activity[hour] += metric.engagement_value or 0
        
        # Find peak hours
        sorted_hours = sorted(hourly_activity.items(), key=lambda x: x[1], reverse=True)
        patterns["peak_activity_hours"] = [hour for hour, _ in sorted_hours[:3]]
        
        return patterns
    
    def _calculate_retention_metrics(self, engagement_data: List[EngagementMetric]) -> Dict[str, float]:
        """Calculate audience retention metrics"""        # Simplified retention calculation
        metrics = {
            "weekly_retention": 0.0,
            "monthly_retention": 0.0,
            "engagement_consistency": 0.0
        }
        
        if len(engagement_data) < 7:
            return metrics
        
        # Calculate engagement consistency over time
        daily_engagement = defaultdict(float)
        for metric in engagement_data:
            day = metric.measurement_timestamp.date()
            daily_engagement[day] += float(metric.engagement_rate) if metric.engagement_rate else 0
        
        if len(daily_engagement) > 1:
            engagement_values = list(daily_engagement.values())
            consistency = 1.0 - (statistics.stdev(engagement_values) / statistics.mean(engagement_values)) if statistics.mean(engagement_values) > 0 else 0
            metrics["engagement_consistency"] = max(0, min(1, consistency))
        
        # Estimate retention rates based on engagement patterns
        metrics["weekly_retention"] = min(0.8, metrics["engagement_consistency"] * 1.2)
        metrics["monthly_retention"] = min(0.6, metrics["engagement_consistency"] * 0.9)
        
        return metrics
    
    def _calculate_influence_score(self, engagement_data: List[EngagementMetric]) -> float:
        """Calculate overall influence score"""        if not engagement_data:
            return 0.0
        
        # Factors: engagement quality, reach, viral coefficient
        quality_scores = [float(m.engagement_quality_score) for m in engagement_data if m.engagement_quality_score]
        viral_coefficients = [float(m.viral_coefficient) for m in engagement_data if m.viral_coefficient]
        
        avg_quality = statistics.mean(quality_scores) if quality_scores else 0
        avg_viral = statistics.mean(viral_coefficients) if viral_coefficients else 0
        
        # Combined influence score (0-100 scale)
        influence_score = (avg_quality * 0.6 + avg_viral * 40 * 0.4)
        
        return min(100.0, influence_score)
    
    def _calculate_community_health_score(self, engagement_data: List[EngagementMetric]) -> float:
        """Calculate community health score"""        if not engagement_data:
            return 0.0
        
        # Factors: sentiment, engagement distribution, growth stability
        sentiment_scores = [float(m.sentiment_score) for m in engagement_data if m.sentiment_score]
        engagement_rates = [float(m.engagement_rate) for m in engagement_data if m.engagement_rate]
        
        avg_sentiment = statistics.mean(sentiment_scores) if sentiment_scores else 0
        engagement_stability = 1.0 - (statistics.stdev(engagement_rates) / statistics.mean(engagement_rates)) if engagement_rates and statistics.mean(engagement_rates) > 0 else 0
        
        # Normalize sentiment to 0-1 scale (assuming sentiment is -1 to 1)
        normalized_sentiment = (avg_sentiment + 1) / 2
        
        # Combined health score (0-100 scale)
        health_score = (normalized_sentiment * 50 + engagement_stability * 50)
        
        return min(100.0, max(0.0, health_score))


# Export classes and functions
__all__ = [
    "EngagementAnalyzer",
    "AudienceInsights", 
    "EngagementMetric",
    "EngagementInsight",
    "EngagementType",
    "SentimentType"
]
