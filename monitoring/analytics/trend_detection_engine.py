"""
Ainflue Platform - Trend Detection Engine
=========================================

Advanced trend detection system for identifying emerging patterns, viral content,
market opportunities, and predictive analytics across the Ainflue platform.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import statistics
import uuid
from collections import defaultdict, deque
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TrendType(Enum):
    """Types of trends to detect."""
    CONTENT_VIRAL = "content_viral"
    GENRE_EMERGING = "genre_emerging"
    COLLABORATION_PATTERN = "collaboration_pattern"
    MONETIZATION_OPPORTUNITY = "monetization_opportunity"
    PLATFORM_SHIFT = "platform_shift"
    AUDIENCE_BEHAVIOR = "audience_behavior"
    TECHNOLOGY_ADOPTION = "technology_adoption"
    MARKET_SENTIMENT = "market_sentiment"

class TrendStrength(Enum):
    """Strength levels of detected trends."""
    WEAK = "weak"
    MODERATE = "moderate"
    STRONG = "strong"
    VIRAL = "viral"

class TrendDirection(Enum):
    """Direction of trend movement."""
    ASCENDING = "ascending"
    DESCENDING = "descending"
    STABLE = "stable"
    VOLATILE = "volatile"

@dataclass
class DetectedTrend:
    """Detected trend with analytics data."""
    trend_id: str
    trend_type: TrendType
    name: str
    description: str
    strength: TrendStrength
    direction: TrendDirection
    confidence_score: float
    detection_time: datetime
    
    # Trend metrics
    growth_rate: float
    engagement_score: float
    reach_potential: int
    duration_prediction_days: int
    
    # Supporting data
    data_points: List[Dict[str, Any]] = field(default_factory=list)
    related_content: List[str] = field(default_factory=list)
    key_influencers: List[str] = field(default_factory=list)
    geographic_spread: Dict[str, float] = field(default_factory=dict)
    
    # AI insights
    ai_predictions: Dict[str, Any] = field(default_factory=dict)
    market_impact: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)

@dataclass
class TrendSignal:
    """Signal indicating potential trend."""
    signal_id: str
    signal_type: str
    strength: float
    timestamp: datetime
    source_data: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)

class TrendDetectionEngine:
    """
    Advanced trend detection engine for Ainflue platform.
    
    Features:
    - Real-time trend detection across multiple data sources
    - ML-powered pattern recognition and prediction
    - Cross-platform trend correlation
    - Viral content early identification
    - Market opportunity prediction
    - Audience behavior analysis
    - Technology adoption tracking
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize trend detection engine."""
        self.config = config or {}
        self.detected_trends: Dict[str, DetectedTrend] = {}
        self.trend_signals: List[TrendSignal] = []
        self.historical_data: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # Detection thresholds
        self.detection_thresholds = {
            "viral_growth_rate": 10.0,      # 10x growth
            "emerging_engagement": 2.0,      # 2x normal engagement
            "platform_shift": 0.3,          # 30% change
            "sentiment_change": 0.5,         # 50% sentiment shift
            "adoption_rate": 0.2             # 20% adoption rate
        }
        
        # Trend pattern definitions
        self.trend_patterns = {
            "exponential_growth": {"min_growth": 2.0, "duration_hours": 6},
            "viral_spike": {"growth_acceleration": 5.0, "peak_duration": 2},
            "sustained_growth": {"min_growth": 1.5, "duration_days": 7},
            "cyclical_pattern": {"repetition_days": 7, "consistency": 0.8}
        }
        
        logger.info("📈 Trend Detection Engine initialized")
    
    async def analyze_content_trends(
        self,
        content_data: List[Dict[str, Any]],
        time_window_hours: int = 24
    ) -> List[DetectedTrend]:
        """Analyze content trends in specified time window."""
        content_trends = []
        
        try:
            # Group content by various dimensions
            content_by_genre = self._group_content_by_genre(content_data)
            content_by_creator = self._group_content_by_creator(content_data)
            content_by_platform = self._group_content_by_platform(content_data)
            
            # Detect viral content trends
            viral_trends = await self._detect_viral_content_trends(content_data)
            content_trends.extend(viral_trends)
            
            # Detect emerging genre trends
            genre_trends = await self._detect_genre_trends(content_by_genre)
            content_trends.extend(genre_trends)
            
            # Detect collaboration patterns
            collaboration_trends = await self._detect_collaboration_trends(content_data)
            content_trends.extend(collaboration_trends)
            
            # Detect platform-specific trends
            platform_trends = await self._detect_platform_trends(content_by_platform)
            content_trends.extend(platform_trends)
            
            logger.info(f"📈 Detected {len(content_trends)} content trends")
            return content_trends
            
        except Exception as e:
            logger.error(f"❌ Error analyzing content trends: {e}")
            return []
    
    async def _detect_viral_content_trends(self, content_data: List[Dict[str, Any]]) -> List[DetectedTrend]:
        """Detect viral content trends."""
        viral_trends = []
        
        # Calculate engagement velocity for each content piece
        for content in content_data:
            content_id = content.get("id")
            engagement_rate = content.get("engagement_rate", 0)
            view_count = content.get("view_count", 0)
            creation_time = datetime.fromisoformat(content.get("created_at", datetime.utcnow().isoformat()))
            
            # Calculate viral score
            viral_score = await self._calculate_viral_score(
                engagement_rate, view_count, creation_time
            )
            
            if viral_score > self.detection_thresholds["viral_growth_rate"]:
                trend = DetectedTrend(
                    trend_id=f"viral_{content_id}_{int(time.time())}",
                    trend_type=TrendType.CONTENT_VIRAL,
                    name=f"Viral Content: {content.get('title', 'Unknown')}",
                    description=f"Content showing viral characteristics with {viral_score:.1f}x growth",
                    strength=self._determine_viral_strength(viral_score),
                    direction=TrendDirection.ASCENDING,
                    confidence_score=min(1.0, viral_score / 20),
                    detection_time=datetime.utcnow(),
                    growth_rate=viral_score,
                    engagement_score=engagement_rate,
                    reach_potential=int(view_count * viral_score),
                    duration_prediction_days=self._predict_viral_duration(viral_score),
                    related_content=[content_id],
                    key_influencers=[content.get("creator_id")],
                    ai_predictions={
                        "peak_engagement_time": self._predict_peak_time(viral_score),
                        "total_reach_prediction": int(view_count * viral_score * 2),
                        "monetization_potential": self._calculate_monetization_potential(viral_score, engagement_rate)
                    }
                )
                
                viral_trends.append(trend)
                self.detected_trends[trend.trend_id] = trend
        
        return viral_trends
    
    async def _detect_genre_trends(self, content_by_genre: Dict[str, List[Dict[str, Any]]]) -> List[DetectedTrend]:
        """Detect emerging genre trends."""
        genre_trends = []
        
        for genre, content_list in content_by_genre.items():
            if len(content_list) < 3:  # Need minimum data points
                continue
            
            # Calculate genre metrics
            total_engagement = sum(c.get("engagement_rate", 0) for c in content_list)
            avg_engagement = total_engagement / len(content_list)
            
            # Compare with historical genre performance
            historical_avg = await self._get_historical_genre_performance(genre)
            
            if historical_avg and avg_engagement > historical_avg * self.detection_thresholds["emerging_engagement"]:
                growth_rate = (avg_engagement - historical_avg) / historical_avg
                
                trend = DetectedTrend(
                    trend_id=f"genre_{genre}_{int(time.time())}",
                    trend_type=TrendType.GENRE_EMERGING,
                    name=f"Emerging Genre: {genre}",
                    description=f"Genre showing {growth_rate:.1%} growth in engagement",
                    strength=self._determine_trend_strength(growth_rate),
                    direction=TrendDirection.ASCENDING,
                    confidence_score=min(1.0, growth_rate * 2),
                    detection_time=datetime.utcnow(),
                    growth_rate=growth_rate,
                    engagement_score=avg_engagement,
                    reach_potential=sum(c.get("view_count", 0) for c in content_list),
                    duration_prediction_days=self._predict_genre_trend_duration(growth_rate),
                    related_content=[c.get("id") for c in content_list],
                    key_influencers=[c.get("creator_id") for c in content_list[:5]],
                    ai_predictions={
                        "market_saturation_time": self._predict_market_saturation(genre, growth_rate),
                        "cross_genre_influence": self._analyze_cross_genre_influence(genre, content_list)
                    }
                )
                
                genre_trends.append(trend)
                self.detected_trends[trend.trend_id] = trend
        
        return genre_trends
    
    async def _detect_collaboration_trends(self, content_data: List[Dict[str, Any]]) -> List[DetectedTrend]:
        """Detect collaboration pattern trends."""
        collaboration_trends = []
        
        # Identify collaborative content
        collaborative_content = [
            c for c in content_data 
            if c.get("collaboration_id") or len(c.get("creators", [])) > 1
        ]
        
        if len(collaborative_content) < 5:
            return collaboration_trends
        
        # Analyze collaboration success patterns
        collaboration_success_rate = await self._calculate_collaboration_success_rate(collaborative_content)
        historical_success_rate = await self._get_historical_collaboration_success()
        
        if collaboration_success_rate > historical_success_rate * 1.2:  # 20% improvement
            trend = DetectedTrend(
                trend_id=f"collaboration_success_{int(time.time())}",
                trend_type=TrendType.COLLABORATION_PATTERN,
                name="Increasing Collaboration Success",
                description=f"Collaboration success rate increased to {collaboration_success_rate:.1%}",
                strength=TrendStrength.MODERATE,
                direction=TrendDirection.ASCENDING,
                confidence_score=0.8,
                detection_time=datetime.utcnow(),
                growth_rate=(collaboration_success_rate - historical_success_rate) / historical_success_rate,
                engagement_score=sum(c.get("engagement_rate", 0) for c in collaborative_content) / len(collaborative_content),
                reach_potential=sum(c.get("view_count", 0) for c in collaborative_content),
                duration_prediction_days=30,
                related_content=[c.get("id") for c in collaborative_content],
                key_influencers=list(set(c.get("creator_id") for c in collaborative_content)),
                ai_predictions={
                    "optimal_collaboration_size": self._predict_optimal_collaboration_size(collaborative_content),
                    "best_collaboration_types": self._identify_best_collaboration_types(collaborative_content)
                }
            )
            
            collaboration_trends.append(trend)
            self.detected_trends[trend.trend_id] = trend
        
        return collaboration_trends
    
    async def _detect_platform_trends(self, content_by_platform: Dict[str, List[Dict[str, Any]]]) -> List[DetectedTrend]:
        """Detect platform-specific trends."""
        platform_trends = []
        
        for platform, content_list in content_by_platform.items():
            if len(content_list) < 10:  # Need minimum data points
                continue
            
            # Calculate platform performance
            total_engagement = sum(c.get("engagement_rate", 0) for c in content_list)
            total_views = sum(c.get("view_count", 0) for c in content_list)
            
            # Compare with other platforms
            platform_score = (total_engagement + total_views / 10000) / len(content_list)
            
            # Check for significant platform shifts
            historical_score = await self._get_historical_platform_score(platform)
            
            if historical_score and abs(platform_score - historical_score) / historical_score > self.detection_thresholds["platform_shift"]:
                trend_direction = TrendDirection.ASCENDING if platform_score > historical_score else TrendDirection.DESCENDING
                change_rate = (platform_score - historical_score) / historical_score
                
                trend = DetectedTrend(
                    trend_id=f"platform_{platform}_{int(time.time())}",
                    trend_type=TrendType.PLATFORM_SHIFT,
                    name=f"Platform Shift: {platform}",
                    description=f"Platform showing {change_rate:.1%} change in performance",
                    strength=self._determine_trend_strength(abs(change_rate)),
                    direction=trend_direction,
                    confidence_score=min(1.0, abs(change_rate) * 3),
                    detection_time=datetime.utcnow(),
                    growth_rate=change_rate,
                    engagement_score=total_engagement / len(content_list),
                    reach_potential=total_views,
                    duration_prediction_days=self._predict_platform_trend_duration(abs(change_rate)),
                    related_content=[c.get("id") for c in content_list[:10]],
                    ai_predictions={
                        "platform_opportunity": self._analyze_platform_opportunity(platform, change_rate),
                        "competitive_impact": self._assess_competitive_impact(platform, change_rate)
                    }
                )
                
                platform_trends.append(trend)
                self.detected_trends[trend.trend_id] = trend
        
        return platform_trends
    
    async def detect_market_trends(
        self,
        market_data: Dict[str, Any],
        sentiment_data: List[Dict[str, Any]]
    ) -> List[DetectedTrend]:
        """Detect broader market trends."""
        market_trends = []
        
        try:
            # Analyze sentiment trends
            sentiment_trends = await self._analyze_sentiment_trends(sentiment_data)
            market_trends.extend(sentiment_trends)
            
            # Analyze technology adoption trends
            tech_trends = await self._analyze_technology_trends(market_data)
            market_trends.extend(tech_trends)
            
            # Analyze monetization opportunities
            monetization_trends = await self._analyze_monetization_trends(market_data)
            market_trends.extend(monetization_trends)
            
            logger.info(f"📈 Detected {len(market_trends)} market trends")
            return market_trends
            
        except Exception as e:
            logger.error(f"❌ Error detecting market trends: {e}")
            return []
    
    async def get_trend_insights(self, period_days: int = 7) -> Dict[str, Any]:
        """Get comprehensive trend insights."""
        try:
            cutoff_time = datetime.utcnow() - timedelta(days=period_days)
            recent_trends = [
                trend for trend in self.detected_trends.values()
                if trend.detection_time >= cutoff_time
            ]
            
            insights = {
                "period_days": period_days,
                "total_trends_detected": len(recent_trends),
                "trend_breakdown": self._analyze_trend_breakdown(recent_trends),
                "top_trends": self._get_top_trends(recent_trends),
                "emerging_opportunities": self._identify_emerging_opportunities(recent_trends),
                "trend_predictions": await self._generate_trend_predictions(recent_trends),
                "actionable_insights": self._generate_actionable_insights(recent_trends)
            }
            
            logger.info(f"📈 Generated trend insights for {period_days} days")
            return insights
            
        except Exception as e:
            logger.error(f"❌ Error generating trend insights: {e}")
            return {"error": str(e)}
    
    # Helper methods
    def _group_content_by_genre(self, content_data: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group content by genre."""
        content_by_genre = defaultdict(list)
        for content in content_data:
            genre = content.get("genre", "unknown")
            content_by_genre[genre].append(content)
        return dict(content_by_genre)
    
    def _group_content_by_creator(self, content_data: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group content by creator."""
        content_by_creator = defaultdict(list)
        for content in content_data:
            creator_id = content.get("creator_id", "unknown")
            content_by_creator[creator_id].append(content)
        return dict(content_by_creator)
    
    def _group_content_by_platform(self, content_data: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group content by platform."""
        content_by_platform = defaultdict(list)
        for content in content_data:
            platform = content.get("platform", "unknown")
            content_by_platform[platform].append(content)
        return dict(content_by_platform)
    
    async def _calculate_viral_score(self, engagement_rate: float, view_count: int, creation_time: datetime) -> float:
        """Calculate viral score for content."""
        age_hours = (datetime.utcnow() - creation_time).total_seconds() / 3600
        
        # Viral score based on engagement rate, views, and time
        if age_hours <= 0:
            return 0
        
        engagement_factor = engagement_rate * 100  # Convert to percentage
        view_velocity = view_count / max(age_hours, 1)
        
        viral_score = (engagement_factor + view_velocity / 100) * (24 / max(age_hours, 1))
        return max(0, viral_score)
    
    def _determine_viral_strength(self, viral_score: float) -> TrendStrength:
        """Determine viral strength based on score."""
        if viral_score >= 50:
            return TrendStrength.VIRAL
        elif viral_score >= 20:
            return TrendStrength.STRONG
        elif viral_score >= 10:
            return TrendStrength.MODERATE
        else:
            return TrendStrength.WEAK
    
    def _determine_trend_strength(self, growth_rate: float) -> TrendStrength:
        """Determine trend strength based on growth rate."""
        if growth_rate >= 3.0:
            return TrendStrength.VIRAL
        elif growth_rate >= 1.5:
            return TrendStrength.STRONG
        elif growth_rate >= 0.5:
            return TrendStrength.MODERATE
        else:
            return TrendStrength.WEAK
    
    def _predict_viral_duration(self, viral_score: float) -> int:
        """Predict how long viral content will remain viral."""
        if viral_score >= 50:
            return 7  # 1 week
        elif viral_score >= 20:
            return 3  # 3 days
        elif viral_score >= 10:
            return 1  # 1 day
        else:
            return 0
    
    def _predict_genre_trend_duration(self, growth_rate: float) -> int:
        """Predict genre trend duration."""
        if growth_rate >= 2.0:
            return 30  # 1 month
        elif growth_rate >= 1.0:
            return 14  # 2 weeks
        else:
            return 7   # 1 week
    
    def _predict_platform_trend_duration(self, change_rate: float) -> int:
        """Predict platform trend duration."""
        if change_rate >= 1.0:
            return 60  # 2 months
        elif change_rate >= 0.5:
            return 30  # 1 month
        else:
            return 14  # 2 weeks
    
    def _predict_peak_time(self, viral_score: float) -> str:
        """Predict when viral content will peak."""
        if viral_score >= 50:
            return "6-12 hours"
        elif viral_score >= 20:
            return "1-2 days"
        else:
            return "2-3 days"
    
    def _calculate_monetization_potential(self, viral_score: float, engagement_rate: float) -> float:
        """Calculate monetization potential."""
        return min(1.0, (viral_score * engagement_rate) / 100)
    
    # Placeholder methods for historical data (would integrate with data store)
    async def _get_historical_genre_performance(self, genre: str) -> Optional[float]:
        """Get historical genre performance."""
        # Would query historical database
        return 0.05  # 5% baseline engagement
    
    async def _get_historical_collaboration_success(self) -> float:
        """Get historical collaboration success rate."""
        return 0.7  # 70% baseline success rate
    
    async def _get_historical_platform_score(self, platform: str) -> Optional[float]:
        """Get historical platform score."""
        return 10.0  # Baseline platform score
    
    async def _calculate_collaboration_success_rate(self, collaborative_content: List[Dict[str, Any]]) -> float:
        """Calculate collaboration success rate."""
        if not collaborative_content:
            return 0.0
        
        successful = sum(1 for c in collaborative_content if c.get("engagement_rate", 0) > 0.05)
        return successful / len(collaborative_content)
    
    # Analysis helper methods
    async def _analyze_sentiment_trends(self, sentiment_data: List[Dict[str, Any]]) -> List[DetectedTrend]:
        """Analyze sentiment trends."""
        return []  # Placeholder implementation
    
    async def _analyze_technology_trends(self, market_data: Dict[str, Any]) -> List[DetectedTrend]:
        """Analyze technology adoption trends."""
        return []  # Placeholder implementation
    
    async def _analyze_monetization_trends(self, market_data: Dict[str, Any]) -> List[DetectedTrend]:
        """Analyze monetization opportunity trends."""
        return []  # Placeholder implementation
    
    def _analyze_trend_breakdown(self, trends: List[DetectedTrend]) -> Dict[str, int]:
        """Analyze breakdown of trends by type."""
        breakdown = defaultdict(int)
        for trend in trends:
            breakdown[trend.trend_type.value] += 1
        return dict(breakdown)
    
    def _get_top_trends(self, trends: List[DetectedTrend], top_n: int = 5) -> List[Dict[str, Any]]:
        """Get top trends by strength and confidence."""
        sorted_trends = sorted(
            trends,
            key=lambda t: (t.strength.value, t.confidence_score),
            reverse=True
        )
        
        return [
            {
                "name": trend.name,
                "type": trend.trend_type.value,
                "strength": trend.strength.value,
                "confidence": trend.confidence_score,
                "growth_rate": trend.growth_rate
            }
            for trend in sorted_trends[:top_n]
        ]
    
    def _identify_emerging_opportunities(self, trends: List[DetectedTrend]) -> List[str]:
        """Identify emerging opportunities from trends."""
        opportunities = []
        
        viral_trends = [t for t in trends if t.trend_type == TrendType.CONTENT_VIRAL]
        if viral_trends:
            opportunities.append("Capitalize on viral content momentum")
        
        genre_trends = [t for t in trends if t.trend_type == TrendType.GENRE_EMERGING]
        if genre_trends:
            opportunities.append(f"Invest in emerging genres: {', '.join([t.name for t in genre_trends[:3]])}")
        
        collaboration_trends = [t for t in trends if t.trend_type == TrendType.COLLABORATION_PATTERN]
        if collaboration_trends:
            opportunities.append("Enhance collaboration matching algorithms")
        
        return opportunities
    
    async def _generate_trend_predictions(self, trends: List[DetectedTrend]) -> Dict[str, Any]:
        """Generate predictions based on current trends."""
        return {
            "next_viral_genre": self._predict_next_viral_genre(trends),
            "platform_growth_leaders": self._predict_platform_leaders(trends),
            "collaboration_success_factors": self._identify_success_factors(trends)
        }
    
    def _generate_actionable_insights(self, trends: List[DetectedTrend]) -> List[str]:
        """Generate actionable insights from trends."""
        insights = []
        
        strong_trends = [t for t in trends if t.strength in [TrendStrength.STRONG, TrendStrength.VIRAL]]
        if strong_trends:
            insights.append(f"Focus marketing efforts on {len(strong_trends)} strong trends")
        
        ascending_trends = [t for t in trends if t.direction == TrendDirection.ASCENDING]
        if ascending_trends:
            insights.append("Increase content production in ascending trend categories")
        
        return insights
    
    def _predict_next_viral_genre(self, trends: List[DetectedTrend]) -> str:
        """Predict next viral genre."""
        genre_trends = [t for t in trends if t.trend_type == TrendType.GENRE_EMERGING]
        if genre_trends:
            return max(genre_trends, key=lambda t: t.growth_rate).name
        return "Electronic"
    
    def _predict_platform_leaders(self, trends: List[DetectedTrend]) -> List[str]:
        """Predict platform growth leaders."""
        platform_trends = [t for t in trends if t.trend_type == TrendType.PLATFORM_SHIFT]
        ascending_platforms = [
            t.name for t in platform_trends 
            if t.direction == TrendDirection.ASCENDING
        ]
        return ascending_platforms[:3]
    
    def _identify_success_factors(self, trends: List[DetectedTrend]) -> List[str]:
        """Identify collaboration success factors."""
        return ["Creator compatibility", "Audience overlap", "Content quality", "Timing"]
    
    # Prediction helper methods (simplified implementations)
    def _predict_optimal_collaboration_size(self, collaborative_content: List[Dict[str, Any]]) -> int:
        """Predict optimal collaboration size."""
        return 3  # Simplified prediction
    
    def _identify_best_collaboration_types(self, collaborative_content: List[Dict[str, Any]]) -> List[str]:
        """Identify best collaboration types."""
        return ["music_collaboration", "cross_promotion"]  # Simplified
    
    def _predict_market_saturation(self, genre: str, growth_rate: float) -> str:
        """Predict market saturation time."""
        if growth_rate > 2.0:
            return "2-3 months"
        elif growth_rate > 1.0:
            return "6-8 months"
        else:
            return "1+ year"
    
    def _analyze_cross_genre_influence(self, genre: str, content_list: List[Dict[str, Any]]) -> Dict[str, float]:
        """Analyze cross-genre influence."""
        return {"electronic": 0.3, "pop": 0.6, "hip_hop": 0.1}  # Simplified
    
    def _analyze_platform_opportunity(self, platform: str, change_rate: float) -> str:
        """Analyze platform opportunity."""
        if change_rate > 0.5:
            return "high_growth_opportunity"
        elif change_rate > 0.2:
            return "moderate_opportunity"
        else:
            return "maintain_presence"
    
    def _assess_competitive_impact(self, platform: str, change_rate: float) -> str:
        """Assess competitive impact."""
        if abs(change_rate) > 0.5:
            return "high_impact"
        elif abs(change_rate) > 0.2:
            return "medium_impact"
        else:
            return "low_impact"

# Global instance
trend_detection_engine = TrendDetectionEngine()

__all__ = [
    'TrendDetectionEngine',
    'DetectedTrend',
    'TrendSignal',
    'TrendType',
    'TrendStrength',
    'TrendDirection',
    'trend_detection_engine'
]