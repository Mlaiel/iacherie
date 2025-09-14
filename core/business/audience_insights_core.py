"""
Ainflue Core Business - Audience Insights Core
===============================================

Enterprise-grade audience analytics and insights system providing deep audience
understanding, behavior analysis, demographic insights, and engagement patterns.
Enables creators to understand and grow their audience effectively.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import json

# Third-party imports (with fallbacks)
try:
    import numpy as np
    import pandas as pd
    ANALYTICS_LIBS_AVAILABLE = True
except ImportError:
    ANALYTICS_LIBS_AVAILABLE = False

logger = logging.getLogger(__name__)

class AudienceSegment(str, Enum):
    """Audience segment types"""
    DEMOGRAPHICS = "demographics"
    BEHAVIORAL = "behavioral"
    PSYCHOGRAPHIC = "psychographic"
    GEOGRAPHIC = "geographic"
    TECHNOGRAPHIC = "technographic"
    ENGAGEMENT_BASED = "engagement_based"

class EngagementType(str, Enum):
    """Types of audience engagement"""
    VIEW = "view"
    LIKE = "like"
    COMMENT = "comment"
    SHARE = "share"
    FOLLOW = "follow"
    SUBSCRIBE = "subscribe"
    PURCHASE = "purchase"
    DOWNLOAD = "download"

class AudienceMetricType(str, Enum):
    """Audience metric types"""
    REACH = "reach"
    IMPRESSIONS = "impressions"
    ENGAGEMENT_RATE = "engagement_rate"
    RETENTION_RATE = "retention_rate"
    CONVERSION_RATE = "conversion_rate"
    LIFETIME_VALUE = "lifetime_value"
    CHURN_RATE = "churn_rate"
    GROWTH_RATE = "growth_rate"

@dataclass
class AudienceMember:
    """Individual audience member profile"""
    user_id: str
    demographics: Dict[str, Any] = field(default_factory=dict)
    geographic_info: Dict[str, str] = field(default_factory=dict)
    device_info: Dict[str, str] = field(default_factory=dict)
    interests: List[str] = field(default_factory=list)
    behavior_patterns: Dict[str, Any] = field(default_factory=dict)
    engagement_history: List[Dict[str, Any]] = field(default_factory=list)
    subscription_status: str = "free"
    lifetime_value: float = 0.0
    acquisition_date: datetime = field(default_factory=datetime.utcnow)
    last_active: datetime = field(default_factory=datetime.utcnow)
    risk_score: float = 0.0  # Churn risk

@dataclass
class AudienceSegmentData:
    """Audience segment analytics data"""
    segment_id: str
    segment_name: str
    segment_type: AudienceSegment
    criteria: Dict[str, Any]
    member_count: int = 0
    growth_rate: float = 0.0
    engagement_rate: float = 0.0
    avg_lifetime_value: float = 0.0
    top_content: List[str] = field(default_factory=list)
    demographics: Dict[str, Any] = field(default_factory=dict)
    behavior_insights: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)

@dataclass
class EngagementInsight:
    """Audience engagement insight"""
    metric_type: AudienceMetricType
    value: float
    trend: str  # "increasing", "decreasing", "stable"
    change_percentage: float
    time_period: str
    confidence_score: float
    contributing_factors: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

@dataclass
class AudienceReport:
    """Comprehensive audience analytics report"""
    creator_id: str
    report_period: Tuple[datetime, datetime]
    total_audience: int
    segments: List[AudienceSegmentData]
    engagement_insights: List[EngagementInsight]
    demographic_breakdown: Dict[str, Any]
    geographic_distribution: Dict[str, Any]
    behavioral_patterns: Dict[str, Any]
    growth_metrics: Dict[str, float]
    retention_metrics: Dict[str, float]
    content_performance: Dict[str, Any]
    recommendations: List[str] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class AudienceMetrics:
    """Audience insights system metrics"""
    total_audience_members: int = 0
    total_segments: int = 0
    reports_generated: int = 0
    insights_calculated: int = 0
    predictions_made: int = 0
    avg_processing_time: float = 0.0
    accuracy_score: float = 0.0

class AudienceInsightsCore:
    """Enterprise audience analytics and insights system"""
    
    def __init__(self, level -> None: str = "enterprise") -> None:
        """Initialize audience insights core"""
        self.level = level
        self.audience_members: Dict[str, AudienceMember] = {}
        self.segments: Dict[str, AudienceSegmentData] = {}
        self.engagement_data: List[Dict[str, Any]] = []
        self.metrics = AudienceMetrics()
        
        # Analytics configurations
        self.segment_update_interval = 3600  # 1 hour
        self.insight_calculation_interval = 86400  # 24 hours
        self.retention_analysis_days = [1, 7, 30, 90]
        
        # Machine learning models (placeholders)
        self.churn_prediction_model = None
        self.ltv_prediction_model = None
        self.engagement_prediction_model = None
        
        # Caching
        self._insights_cache: Dict[str, Any] = {}
        self._cache_ttl = 3600
        
        logger.info(f"👥 Audience Insights Core initialized - Level: {level}")

    async def add_audience_member(self, member -> None: AudienceMember) -> None:
        """Add or update audience member"""
        self.audience_members[member.user_id] = member
        self.metrics.total_audience_members = len(self.audience_members)
        
        # Update segments
        await self._update_member_segments(member)
        
        logger.debug(f"Added/updated audience member: {member.user_id}")

    async def record_engagement(
        self,
        user_id -> None: str,
        content_id -> None: str,
        engagement_type -> None: EngagementType,
        value -> None: float = 1.0,
        metadata -> None: Optional[Dict[str, Any]] = None
    ) -> None:
        """Record audience engagement event"""
        
        engagement_event = {
            "user_id": user_id,
            "content_id": content_id,
            "engagement_type": engagement_type.value,
            "value": value,
            "timestamp": datetime.utcnow(),
            "metadata": metadata or {}
        }
        
        self.engagement_data.append(engagement_event)
        
        # Update member engagement history
        if user_id in self.audience_members:
            member = self.audience_members[user_id]
            member.engagement_history.append(engagement_event)
            member.last_active = engagement_event["timestamp"]
            
            # Update behavior patterns
            await self._update_behavior_patterns(member, engagement_event)
        
        logger.debug(f"Recorded engagement: {user_id} -> {content_id} ({engagement_type.value})")

    async def _update_behavior_patterns(self, member -> None: AudienceMember, engagement_event -> None: Dict[str, Any]) -> None:
        """Update member behavior patterns"""
        
        patterns = member.behavior_patterns
        
        # Engagement frequency
        engagement_type = engagement_event["engagement_type"]
        patterns[f"{engagement_type}_count"] = patterns.get(f"{engagement_type}_count", 0) + 1
        
        # Time-based patterns
        hour = engagement_event["timestamp"].hour
        day_of_week = engagement_event["timestamp"].weekday()
        
        patterns.setdefault("active_hours", {})
        patterns["active_hours"][str(hour)] = patterns["active_hours"].get(str(hour), 0) + 1
        
        patterns.setdefault("active_days", {})
        patterns["active_days"][str(day_of_week)] = patterns["active_days"].get(str(day_of_week), 0) + 1
        
        # Content preferences
        content_id = engagement_event["content_id"]
        patterns.setdefault("content_interactions", [])
        patterns["content_interactions"].append(content_id)
        
        # Keep only recent interactions (last 100)
        if len(patterns["content_interactions"]) > 100:
            patterns["content_interactions"] = patterns["content_interactions"][-100:]

    async def create_audience_segment(
        self,
        segment_name: str,
        segment_type: AudienceSegment,
        criteria: Dict[str, Any]
    ) -> str:
        """Create new audience segment"""
        
        segment_id = f"segment_{int(time.time())}_{len(self.segments)}"
        
        segment = AudienceSegmentData(
            segment_id=segment_id,
            segment_name=segment_name,
            segment_type=segment_type,
            criteria=criteria
        )
        
        self.segments[segment_id] = segment
        self.metrics.total_segments += 1
        
        # Populate segment with matching members
        await self._populate_segment(segment)
        
        logger.info(f"Created audience segment: {segment_name} ({segment_id})")
        return segment_id

    async def _populate_segment(self, segment -> None: AudienceSegmentData) -> None:
        """Populate segment with matching audience members"""
        
        matching_members = []
        
        for member in self.audience_members.values():
            if await self._member_matches_criteria(member, segment.criteria, segment.segment_type):
                matching_members.append(member)
        
        segment.member_count = len(matching_members)
        
        # Calculate segment metrics
        if matching_members:
            await self._calculate_segment_metrics(segment, matching_members)

    async def _member_matches_criteria(
        self,
        member: AudienceMember,
        criteria: Dict[str, Any],
        segment_type: AudienceSegment
    ) -> bool:
        """Check if member matches segment criteria"""
        
        try:
            if segment_type == AudienceSegment.DEMOGRAPHICS:
                return self._match_demographics(member, criteria)
            elif segment_type == AudienceSegment.BEHAVIORAL:
                return self._match_behavioral(member, criteria)
            elif segment_type == AudienceSegment.GEOGRAPHIC:
                return self._match_geographic(member, criteria)
            elif segment_type == AudienceSegment.ENGAGEMENT_BASED:
                return self._match_engagement(member, criteria)
            else:
                return True
                
        except Exception as e:
            logger.error(f"Error matching criteria: {str(e)}")
            return False

    def _match_demographics(self, member: AudienceMember, criteria: Dict[str, Any]) -> bool:
        """Match demographic criteria"""
        
        for key, value in criteria.items():
            member_value = member.demographics.get(key)
            
            if isinstance(value, dict):
                # Range criteria (e.g., age: {"min": 18, "max": 65})
                if "min" in value and member_value and member_value < value["min"]:
                    return False
                if "max" in value and member_value and member_value > value["max"]:
                    return False
            elif isinstance(value, list):
                # Multiple choice criteria
                if member_value not in value:
                    return False
            else:
                # Exact match
                if member_value != value:
                    return False
        
        return True

    def _match_behavioral(self, member: AudienceMember, criteria: Dict[str, Any]) -> bool:
        """Match behavioral criteria"""
        
        patterns = member.behavior_patterns
        
        for key, value in criteria.items():
            if key == "min_engagement_count":
                total_engagements = sum(
                    patterns.get(f"{etype}_count", 0) 
                    for etype in ["view", "like", "comment", "share"]
                )
                if total_engagements < value:
                    return False
            
            elif key == "active_hours":
                # Check if user is active during specified hours
                active_hours = patterns.get("active_hours", {})
                if not any(hour in active_hours for hour in value):
                    return False
            
            elif key == "subscription_status":
                if member.subscription_status != value:
                    return False
        
        return True

    def _match_geographic(self, member: AudienceMember, criteria: Dict[str, Any]) -> bool:
        """Match geographic criteria"""
        
        geo_info = member.geographic_info
        
        for key, value in criteria.items():
            member_value = geo_info.get(key)
            
            if isinstance(value, list):
                if member_value not in value:
                    return False
            else:
                if member_value != value:
                    return False
        
        return True

    def _match_engagement(self, member: AudienceMember, criteria: Dict[str, Any]) -> bool:
        """Match engagement-based criteria"""
        
        # Calculate engagement metrics
        recent_engagements = [
            e for e in member.engagement_history
            if (datetime.utcnow() - e["timestamp"]).days <= 30
        ]
        
        engagement_rate = len(recent_engagements) / 30 if recent_engagements else 0
        
        for key, value in criteria.items():
            if key == "min_engagement_rate":
                if engagement_rate < value:
                    return False
            elif key == "engagement_types":
                recent_types = {e["engagement_type"] for e in recent_engagements}
                if not any(etype in recent_types for etype in value):
                    return False
        
        return True

    async def _calculate_segment_metrics(
        self,
        segment -> None: AudienceSegmentData,
        members -> None: List[AudienceMember]
    ) -> None:
        """Calculate metrics for segment"""
        
        if not members:
            return
        
        # Calculate engagement rate
        total_engagements = 0
        total_members = len(members)
        
        for member in members:
            recent_engagements = [
                e for e in member.engagement_history
                if (datetime.utcnow() - e["timestamp"]).days <= 30
            ]
            total_engagements += len(recent_engagements)
        
        segment.engagement_rate = total_engagements / (total_members * 30) if total_members > 0 else 0
        
        # Calculate average lifetime value
        segment.avg_lifetime_value = sum(m.lifetime_value for m in members) / total_members
        
        # Demographics breakdown
        segment.demographics = self._calculate_demographics_breakdown(members)
        
        # Behavior insights
        segment.behavior_insights = self._calculate_behavior_insights(members)

    def _calculate_demographics_breakdown(self, members: List[AudienceMember]) -> Dict[str, Any]:
        """Calculate demographics breakdown for segment"""
        
        breakdown = {}
        
        # Age distribution
        ages = [m.demographics.get("age") for m in members if m.demographics.get("age")]
        if ages:
            breakdown["age"] = {
                "average": sum(ages) / len(ages),
                "median": sorted(ages)[len(ages) // 2],
                "distribution": dict(Counter(ages))
            }
        
        # Gender distribution
        genders = [m.demographics.get("gender") for m in members if m.demographics.get("gender")]
        if genders:
            gender_counts = Counter(genders)
            total = len(genders)
            breakdown["gender"] = {
                key: count / total for key, count in gender_counts.items()
            }
        
        return breakdown

    def _calculate_behavior_insights(self, members: List[AudienceMember]) -> Dict[str, Any]:
        """Calculate behavior insights for segment"""
        
        insights = {}
        
        # Most active hours
        all_active_hours = defaultdict(int)
        for member in members:
            active_hours = member.behavior_patterns.get("active_hours", {})
            for hour, count in active_hours.items():
                all_active_hours[hour] += count
        
        if all_active_hours:
            insights["peak_hours"] = sorted(
                all_active_hours.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:3]
        
        # Content preferences
        all_content = []
        for member in members:
            content_interactions = member.behavior_patterns.get("content_interactions", [])
            all_content.extend(content_interactions)
        
        if all_content:
            content_counts = Counter(all_content)
            insights["popular_content"] = list(content_counts.most_common(10))
        
        return insights

    async def generate_audience_report(
        self,
        creator_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> AudienceReport:
        """Generate comprehensive audience report"""
        
        start_time = time.time()
        
        try:
            # Filter audience for creator
            creator_audience = [
                member for member in self.audience_members.values()
                if self._is_creator_audience(member, creator_id)
            ]
            
            # Calculate engagement insights
            engagement_insights = await self._calculate_engagement_insights(
                creator_audience, start_date, end_date
            )
            
            # Get relevant segments
            relevant_segments = [
                segment for segment in self.segments.values()
                if segment.member_count > 0
            ]
            
            # Generate report
            report = AudienceReport(
                creator_id=creator_id,
                report_period=(start_date, end_date),
                total_audience=len(creator_audience),
                segments=relevant_segments,
                engagement_insights=engagement_insights,
                demographic_breakdown=self._calculate_demographics_breakdown(creator_audience),
                geographic_distribution=self._calculate_geographic_distribution(creator_audience),
                behavioral_patterns=self._calculate_overall_behavior_patterns(creator_audience),
                growth_metrics=await self._calculate_growth_metrics(creator_id, start_date, end_date),
                retention_metrics=await self._calculate_retention_metrics(creator_audience),
                content_performance=await self._analyze_content_performance(creator_id, start_date, end_date),
                recommendations=await self._generate_recommendations(creator_audience, engagement_insights)
            )
            
            # Update metrics
            self.metrics.reports_generated += 1
            processing_time = time.time() - start_time
            self.metrics.avg_processing_time = (
                self.metrics.avg_processing_time * 0.9 + processing_time * 0.1
            )
            
            logger.info(f"Generated audience report for creator {creator_id}")
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate audience report: {str(e)}")
            raise

    def _is_creator_audience(self, member: AudienceMember, creator_id: str) -> bool:
        """Check if member is part of creator's audience"""
        
        # Check if member has engaged with creator's content
        for engagement in member.engagement_history:
            content_id = engagement.get("content_id", "")
            if creator_id in content_id:  # Simple check, could be more sophisticated
                return True
        
        return False

    async def _calculate_engagement_insights(
        self,
        audience: List[AudienceMember],
        start_date: datetime,
        end_date: datetime
    ) -> List[EngagementInsight]:
        """Calculate engagement insights for time period"""
        
        insights = []
        
        # Filter engagements for time period
        period_engagements = []
        for member in audience:
            for engagement in member.engagement_history:
                timestamp = engagement["timestamp"]
                if start_date <= timestamp <= end_date:
                    period_engagements.append(engagement)
        
        # Calculate engagement rate
        if audience and period_engagements:
            days_in_period = (end_date - start_date).days
            avg_engagements_per_user = len(period_engagements) / len(audience)
            engagement_rate = avg_engagements_per_user / days_in_period if days_in_period > 0 else 0
            
            insight = EngagementInsight(
                metric_type=AudienceMetricType.ENGAGEMENT_RATE,
                value=engagement_rate,
                trend="stable",  # Would need historical data for trend
                change_percentage=0.0,
                time_period=f"{start_date.date()} to {end_date.date()}",
                confidence_score=0.8,
                recommendations=["Maintain current engagement strategies"]
            )
            insights.append(insight)
        
        self.metrics.insights_calculated += len(insights)
        return insights

    def _calculate_geographic_distribution(self, audience: List[AudienceMember]) -> Dict[str, Any]:
        """Calculate geographic distribution of audience"""
        
        distribution = {}
        
        # Country distribution
        countries = [m.geographic_info.get("country") for m in audience if m.geographic_info.get("country")]
        if countries:
            country_counts = Counter(countries)
            total = len(countries)
            distribution["countries"] = {
                country: count / total for country, count in country_counts.items()
            }
        
        # City distribution
        cities = [m.geographic_info.get("city") for m in audience if m.geographic_info.get("city")]
        if cities:
            city_counts = Counter(cities)
            distribution["top_cities"] = list(city_counts.most_common(10))
        
        return distribution

    def _calculate_overall_behavior_patterns(self, audience: List[AudienceMember]) -> Dict[str, Any]:
        """Calculate overall behavior patterns"""
        
        patterns = {}
        
        # Aggregate all patterns
        all_patterns = defaultdict(int)
        for member in audience:
            member_patterns = member.behavior_patterns
            for key, value in member_patterns.items():
                if isinstance(value, dict):
                    for subkey, subvalue in value.items():
                        all_patterns[f"{key}_{subkey}"] += subvalue
                elif isinstance(value, (int, float)):
                    all_patterns[key] += value
        
        patterns["aggregated_patterns"] = dict(all_patterns)
        return patterns

    async def _calculate_growth_metrics(
        self,
        creator_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, float]:
        """Calculate audience growth metrics"""
        
        # This would require historical data
        # For now, return basic metrics
        metrics = {
            "growth_rate": 0.05,  # 5% growth
            "acquisition_rate": 0.03,  # 3% new users
            "churn_rate": 0.02  # 2% churn
        }
        
        return metrics

    async def _calculate_retention_metrics(self, audience: List[AudienceMember]) -> Dict[str, float]:
        """Calculate audience retention metrics"""
        
        metrics = {}
        
        for days in self.retention_analysis_days:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Count members who were active before cutoff and after
            active_before = [m for m in audience if m.acquisition_date < cutoff_date]
            still_active = [
                m for m in active_before 
                if m.last_active > cutoff_date
            ]
            
            if active_before:
                retention_rate = len(still_active) / len(active_before)
                metrics[f"retention_{days}d"] = retention_rate
        
        return metrics

    async def _analyze_content_performance(
        self,
        creator_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Analyze content performance for creator"""
        
        # Filter engagements for creator's content in time period
        creator_engagements = [
            engagement for engagement in self.engagement_data
            if (start_date <= engagement["timestamp"] <= end_date and
                creator_id in engagement.get("content_id", ""))
        ]
        
        # Aggregate by content
        content_performance = defaultdict(lambda: {"views": 0, "likes": 0, "shares": 0, "comments": 0})
        
        for engagement in creator_engagements:
            content_id = engagement["content_id"]
            engagement_type = engagement["engagement_type"]
            content_performance[content_id][engagement_type] += 1
        
        # Calculate performance scores
        performance_data = {}
        for content_id, metrics in content_performance.items():
            total_engagement = sum(metrics.values())
            performance_data[content_id] = {
                **metrics,
                "total_engagement": total_engagement,
                "engagement_score": total_engagement * 0.1 + metrics.get("likes", 0) * 0.3
            }
        
        return {
            "content_performance": dict(performance_data),
            "top_performing": sorted(
                performance_data.items(),
                key=lambda x: x[1]["engagement_score"],
                reverse=True
            )[:10]
        }

    async def _generate_recommendations(
        self,
        audience: List[AudienceMember],
        insights: List[EngagementInsight]
    ) -> List[str]:
        """Generate recommendations based on audience analysis"""
        
        recommendations = []
        
        if not audience:
            return ["Focus on audience acquisition strategies"]
        
        # Engagement-based recommendations
        avg_engagement = sum(
            len(m.engagement_history) for m in audience
        ) / len(audience) if audience else 0
        
        if avg_engagement < 5:
            recommendations.append("Increase content posting frequency to boost engagement")
        
        # Time-based recommendations
        peak_hours = defaultdict(int)
        for member in audience:
            active_hours = member.behavior_patterns.get("active_hours", {})
            for hour, count in active_hours.items():
                peak_hours[hour] += count
        
        if peak_hours:
            best_hour = max(peak_hours.items(), key=lambda x: x[1])[0]
            recommendations.append(f"Post content around {best_hour}:00 for maximum engagement")
        
        # Demographic recommendations
        demographics = self._calculate_demographics_breakdown(audience)
        if "age" in demographics:
            avg_age = demographics["age"].get("average", 0)
            if avg_age < 25:
                recommendations.append("Consider creating content that appeals to younger audiences")
            elif avg_age > 45:
                recommendations.append("Focus on content that resonates with mature audiences")
        
        return recommendations

    async def predict_churn_risk(self, user_id: str) -> float:
        """Predict churn risk for user"""
        
        if user_id not in self.audience_members:
            return 0.5  # Unknown user
        
        member = self.audience_members[user_id]
        
        # Simple churn risk calculation
        days_since_last_active = (datetime.utcnow() - member.last_active).days
        recent_engagement_count = len([
            e for e in member.engagement_history
            if (datetime.utcnow() - e["timestamp"]).days <= 7
        ])
        
        # Risk factors
        risk_score = 0.0
        
        # Time since last activity
        if days_since_last_active > 30:
            risk_score += 0.4
        elif days_since_last_active > 14:
            risk_score += 0.2
        
        # Low engagement
        if recent_engagement_count == 0:
            risk_score += 0.3
        elif recent_engagement_count < 3:
            risk_score += 0.1
        
        # Subscription status
        if member.subscription_status == "free":
            risk_score += 0.1
        
        member.risk_score = min(risk_score, 1.0)
        self.metrics.predictions_made += 1
        
        return member.risk_score

    async def get_high_risk_users(self, threshold: float = 0.7) -> List[AudienceMember]:
        """Get users with high churn risk"""
        
        high_risk_users = []
        
        for member in self.audience_members.values():
            risk_score = await self.predict_churn_risk(member.user_id)
            if risk_score >= threshold:
                high_risk_users.append(member)
        
        return sorted(high_risk_users, key=lambda x: x.risk_score, reverse=True)

    async def _update_member_segments(self, member -> None: AudienceMember) -> None:
        """Update member's segment memberships"""
        
        for segment in self.segments.values():
            if await self._member_matches_criteria(member, segment.criteria, segment.segment_type):
                # Member belongs to this segment - update count if needed
                pass

    def get_metrics(self) -> AudienceMetrics:
        """Get audience insights metrics"""
        return self.metrics

    async def health_check(self) -> bool:
        """Health check for audience insights system"""
        try:
            # Test basic operations
            if self.audience_members:
                sample_member = list(self.audience_members.values())[0]
                await self.predict_churn_risk(sample_member.user_id)
            
            return True
            
        except Exception as e:
            logger.error(f"Audience insights health check failed: {str(e)}")
            return False

# Module exports
__all__ = [
    "AudienceInsightsCore", "AudienceSegment", "EngagementType", "AudienceMetricType",
    "AudienceMember", "AudienceSegmentData", "EngagementInsight", "AudienceReport",
    "AudienceMetrics"
]

logger.info("👥 Audience Insights Core module loaded")