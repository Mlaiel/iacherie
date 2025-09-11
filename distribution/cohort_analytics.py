"""
Cohort Analytics Engine
=====================

Advanced cohort analysis system for Ainflue Distribution Platform.
Tracks user behavior, retention, and engagement patterns across cohorts.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de
"""

import asyncio
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone, timedelta
import logging
from collections import defaultdict
import json

logger = logging.getLogger(__name__)

class CohortType(Enum):
    """Types of cohort analysis"""
    ACQUISITION = "acquisition"  # Based on first interaction date
    BEHAVIORAL = "behavioral"  # Based on specific actions
    REVENUE = "revenue"  # Based on first purchase
    ENGAGEMENT = "engagement"  # Based on engagement levels
    PLATFORM = "platform"  # Based on platform discovery
    CONTENT_TYPE = "content_type"  # Based on content preferences

class PeriodType(Enum):
    """Time period granularity for analysis"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"

class MetricType(Enum):
    """Types of metrics to analyze"""
    RETENTION = "retention"
    ENGAGEMENT = "engagement"
    REVENUE = "revenue"
    CONTENT_CONSUMPTION = "content_consumption"
    PLATFORM_USAGE = "platform_usage"
    CONVERSION = "conversion"

@dataclass
class UserEvent:
    """Individual user event for cohort analysis"""
    user_id: str
    event_type: str
    event_timestamp: datetime
    platform: str
    content_id: Optional[str] = None
    engagement_score: float = 0.0
    revenue: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CohortDefinition:
    """Definition of a cohort for analysis"""
    cohort_id: str
    cohort_type: CohortType
    period_type: PeriodType
    start_date: datetime
    end_date: datetime
    criteria: Dict[str, Any] = field(default_factory=dict)
    description: str = ""

@dataclass
class CohortMetrics:
    """Metrics for a specific cohort period"""
    cohort_id: str
    period_number: int
    total_users: int
    active_users: int
    retention_rate: float
    avg_engagement: float
    total_revenue: float
    avg_revenue_per_user: float
    conversion_rate: float
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CohortAnalysisResult:
    """Complete cohort analysis results"""
    cohort_definition: CohortDefinition
    cohort_size: int
    periods_analyzed: int
    metrics_by_period: List[CohortMetrics]
    summary_stats: Dict[str, Any]
    insights: List[str]
    recommendations: List[str]

class CohortAnalytics:
    """
    Advanced cohort analytics engine
    
    Features:
    - Multi-dimensional cohort analysis
    - Retention rate calculations
    - Revenue cohort tracking
    - Engagement pattern analysis
    - Cross-platform cohort comparison
    - Predictive cohort modeling
    - Automated insight generation
    """
    
    def __init__(self):
        self.user_events: List[UserEvent] = []
        self.cohorts: Dict[str, CohortDefinition] = {}
        self.analysis_cache: Dict[str, CohortAnalysisResult] = {}
        self._user_first_seen: Dict[str, datetime] = {}
        self._user_platform_first_seen: Dict[str, Dict[str, datetime]] = defaultdict(dict)
        
    async def add_user_events(self, events: List[UserEvent]):
        """Add user events for cohort analysis"""
        for event in events:
            self.user_events.append(event)
            
            # Track first seen dates
            if event.user_id not in self._user_first_seen:
                self._user_first_seen[event.user_id] = event.event_timestamp
            else:
                if event.event_timestamp < self._user_first_seen[event.user_id]:
                    self._user_first_seen[event.user_id] = event.event_timestamp
                    
            # Track platform first seen
            if event.platform not in self._user_platform_first_seen[event.user_id]:
                self._user_platform_first_seen[event.user_id][event.platform] = event.event_timestamp
            else:
                if event.event_timestamp < self._user_platform_first_seen[event.user_id][event.platform]:
                    self._user_platform_first_seen[event.user_id][event.platform] = event.event_timestamp
                    
        logger.info(f"Added {len(events)} user events for cohort analysis")
        
    async def define_cohort(self, definition: CohortDefinition):
        """Define a new cohort for analysis"""
        self.cohorts[definition.cohort_id] = definition
        logger.info(f"Defined cohort {definition.cohort_id} of type {definition.cohort_type.value}")
        
    async def analyze_cohort(self, cohort_id: str, refresh_cache: bool = False) -> CohortAnalysisResult:
        """
        Perform comprehensive cohort analysis
        
        Args:
            cohort_id: ID of the cohort to analyze
            refresh_cache: Whether to refresh cached results
            
        Returns:
            CohortAnalysisResult with complete analysis
        """
        if cohort_id not in self.cohorts:
            raise ValueError(f"Cohort {cohort_id} not found")
            
        # Check cache first
        if not refresh_cache and cohort_id in self.analysis_cache:
            logger.info(f"Returning cached results for cohort {cohort_id}")
            return self.analysis_cache[cohort_id]
            
        definition = self.cohorts[cohort_id]
        logger.info(f"Analyzing cohort {cohort_id} of type {definition.cohort_type.value}")
        
        # Identify cohort users
        cohort_users = await self._identify_cohort_users(definition)
        
        if not cohort_users:
            logger.warning(f"No users found for cohort {cohort_id}")
            return CohortAnalysisResult(
                cohort_definition=definition,
                cohort_size=0,
                periods_analyzed=0,
                metrics_by_period=[],
                summary_stats={},
                insights=["No users found in this cohort"],
                recommendations=[]
            )
            
        # Analyze metrics by period
        metrics_by_period = await self._analyze_cohort_periods(definition, cohort_users)
        
        # Generate summary statistics
        summary_stats = await self._generate_summary_stats(metrics_by_period)
        
        # Generate insights and recommendations
        insights = await self._generate_insights(definition, metrics_by_period, summary_stats)
        recommendations = await self._generate_recommendations(definition, metrics_by_period, summary_stats)
        
        result = CohortAnalysisResult(
            cohort_definition=definition,
            cohort_size=len(cohort_users),
            periods_analyzed=len(metrics_by_period),
            metrics_by_period=metrics_by_period,
            summary_stats=summary_stats,
            insights=insights,
            recommendations=recommendations
        )
        
        # Cache the result
        self.analysis_cache[cohort_id] = result
        
        logger.info(f"Completed analysis for cohort {cohort_id}: {len(cohort_users)} users across {len(metrics_by_period)} periods")
        return result
        
    async def _identify_cohort_users(self, definition: CohortDefinition) -> List[str]:
        """Identify users belonging to a specific cohort"""
        cohort_users = set()
        
        if definition.cohort_type == CohortType.ACQUISITION:
            # Users who first interacted during the cohort period
            for user_id, first_seen in self._user_first_seen.items():
                if definition.start_date <= first_seen <= definition.end_date:
                    cohort_users.add(user_id)
                    
        elif definition.cohort_type == CohortType.BEHAVIORAL:
            # Users who performed specific actions during the period
            target_action = definition.criteria.get("action_type")
            for event in self.user_events:
                if (event.event_type == target_action and
                    definition.start_date <= event.event_timestamp <= definition.end_date):
                    cohort_users.add(event.user_id)
                    
        elif definition.cohort_type == CohortType.REVENUE:
            # Users who made their first purchase during the period
            user_first_purchase = {}
            for event in self.user_events:
                if event.revenue > 0:
                    if event.user_id not in user_first_purchase:
                        user_first_purchase[event.user_id] = event.event_timestamp
                    else:
                        if event.event_timestamp < user_first_purchase[event.user_id]:
                            user_first_purchase[event.user_id] = event.event_timestamp
                            
            for user_id, first_purchase in user_first_purchase.items():
                if definition.start_date <= first_purchase <= definition.end_date:
                    cohort_users.add(user_id)
                    
        elif definition.cohort_type == CohortType.ENGAGEMENT:
            # Users with specific engagement levels during the period
            min_engagement = definition.criteria.get("min_engagement", 0.0)
            for event in self.user_events:
                if (event.engagement_score >= min_engagement and
                    definition.start_date <= event.event_timestamp <= definition.end_date):
                    cohort_users.add(event.user_id)
                    
        elif definition.cohort_type == CohortType.PLATFORM:
            # Users who first used a specific platform during the period
            target_platform = definition.criteria.get("platform")
            for user_id, platform_first_seen in self._user_platform_first_seen.items():
                if target_platform in platform_first_seen:
                    first_seen = platform_first_seen[target_platform]
                    if definition.start_date <= first_seen <= definition.end_date:
                        cohort_users.add(user_id)
                        
        elif definition.cohort_type == CohortType.CONTENT_TYPE:
            # Users who first consumed specific content types during the period
            target_content_type = definition.criteria.get("content_type")
            for event in self.user_events:
                if (event.metadata.get("content_type") == target_content_type and
                    definition.start_date <= event.event_timestamp <= definition.end_date):
                    cohort_users.add(event.user_id)
                    
        return list(cohort_users)
        
    async def _analyze_cohort_periods(
        self, 
        definition: CohortDefinition, 
        cohort_users: List[str]
    ) -> List[CohortMetrics]:
        """Analyze cohort metrics across time periods"""
        metrics_by_period = []
        
        # Determine period duration
        if definition.period_type == PeriodType.DAILY:
            period_delta = timedelta(days=1)
        elif definition.period_type == PeriodType.WEEKLY:
            period_delta = timedelta(weeks=1)
        elif definition.period_type == PeriodType.MONTHLY:
            period_delta = timedelta(days=30)
        elif definition.period_type == PeriodType.QUARTERLY:
            period_delta = timedelta(days=90)
            
        # Analyze each period after cohort creation
        current_date = definition.end_date
        period_number = 0
        
        # Analyze up to 12 periods or until no data
        while period_number < 12:
            period_start = current_date + (period_delta * period_number)
            period_end = period_start + period_delta
            
            # Check if we have data for this period
            has_data = any(
                event.event_timestamp >= period_start and event.event_timestamp < period_end
                for event in self.user_events
            )
            
            if not has_data and period_number > 0:
                break
                
            # Calculate metrics for this period
            metrics = await self._calculate_period_metrics(
                cohort_users, period_start, period_end, period_number
            )
            
            metrics.cohort_id = definition.cohort_id
            metrics_by_period.append(metrics)
            
            period_number += 1
            
        return metrics_by_period
        
    async def _calculate_period_metrics(
        self,
        cohort_users: List[str],
        period_start: datetime,
        period_end: datetime,
        period_number: int
    ) -> CohortMetrics:
        """Calculate metrics for a specific period"""
        # Get events for cohort users in this period
        period_events = [
            event for event in self.user_events
            if (event.user_id in cohort_users and
                period_start <= event.event_timestamp < period_end)
        ]
        
        # Calculate basic metrics
        active_users = len(set(event.user_id for event in period_events))
        total_users = len(cohort_users)
        retention_rate = active_users / total_users if total_users > 0 else 0.0
        
        # Calculate engagement metrics
        engagement_scores = [event.engagement_score for event in period_events if event.engagement_score > 0]
        avg_engagement = sum(engagement_scores) / len(engagement_scores) if engagement_scores else 0.0
        
        # Calculate revenue metrics
        revenue_events = [event for event in period_events if event.revenue > 0]
        total_revenue = sum(event.revenue for event in revenue_events)
        avg_revenue_per_user = total_revenue / active_users if active_users > 0 else 0.0
        
        # Calculate conversion metrics
        converting_users = len(set(event.user_id for event in revenue_events))
        conversion_rate = converting_users / active_users if active_users > 0 else 0.0
        
        # Additional metadata
        metadata = {
            "period_start": period_start.isoformat(),
            "period_end": period_end.isoformat(),
            "total_events": len(period_events),
            "platforms_used": len(set(event.platform for event in period_events)),
            "content_consumed": len(set(event.content_id for event in period_events if event.content_id)),
            "avg_events_per_user": len(period_events) / active_users if active_users > 0 else 0.0
        }
        
        return CohortMetrics(
            cohort_id="",  # Will be set by caller
            period_number=period_number,
            total_users=total_users,
            active_users=active_users,
            retention_rate=retention_rate,
            avg_engagement=avg_engagement,
            total_revenue=total_revenue,
            avg_revenue_per_user=avg_revenue_per_user,
            conversion_rate=conversion_rate,
            metadata=metadata
        )
        
    async def _generate_summary_stats(self, metrics_by_period: List[CohortMetrics]) -> Dict[str, Any]:
        """Generate summary statistics for the cohort"""
        if not metrics_by_period:
            return {}
            
        retention_rates = [m.retention_rate for m in metrics_by_period]
        engagement_scores = [m.avg_engagement for m in metrics_by_period]
        revenue_per_user = [m.avg_revenue_per_user for m in metrics_by_period]
        
        return {
            "initial_size": metrics_by_period[0].total_users,
            "periods_tracked": len(metrics_by_period),
            "retention_stats": {
                "initial_retention": retention_rates[0] if retention_rates else 0.0,
                "final_retention": retention_rates[-1] if retention_rates else 0.0,
                "avg_retention": sum(retention_rates) / len(retention_rates) if retention_rates else 0.0,
                "retention_decline_rate": self._calculate_decline_rate(retention_rates)
            },
            "engagement_stats": {
                "initial_engagement": engagement_scores[0] if engagement_scores else 0.0,
                "final_engagement": engagement_scores[-1] if engagement_scores else 0.0,
                "avg_engagement": sum(engagement_scores) / len(engagement_scores) if engagement_scores else 0.0,
                "engagement_trend": self._calculate_trend(engagement_scores)
            },
            "revenue_stats": {
                "total_revenue": sum(m.total_revenue for m in metrics_by_period),
                "avg_revenue_per_user": sum(revenue_per_user) / len(revenue_per_user) if revenue_per_user else 0.0,
                "revenue_trend": self._calculate_trend(revenue_per_user),
                "lifetime_value_estimate": self._estimate_lifetime_value(revenue_per_user)
            }
        }
        
    def _calculate_decline_rate(self, values: List[float]) -> float:
        """Calculate the decline rate between first and last values"""
        if len(values) < 2 or values[0] == 0:
            return 0.0
        return (values[0] - values[-1]) / values[0]
        
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction for a series of values"""
        if len(values) < 2:
            return "insufficient_data"
            
        # Simple linear regression slope
        n = len(values)
        x_values = list(range(n))
        
        x_mean = sum(x_values) / n
        y_mean = sum(values) / n
        
        numerator = sum((x_values[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x_values[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return "stable"
            
        slope = numerator / denominator
        
        if slope > 0.01:
            return "increasing"
        elif slope < -0.01:
            return "decreasing"
        else:
            return "stable"
            
    def _estimate_lifetime_value(self, revenue_per_user: List[float]) -> float:
        """Estimate lifetime value based on revenue trend"""
        if len(revenue_per_user) < 2:
            return sum(revenue_per_user) if revenue_per_user else 0.0
            
        # Simple extrapolation based on trend
        trend = self._calculate_trend(revenue_per_user)
        
        if trend == "increasing":
            # Assume continued growth for 12 periods
            last_value = revenue_per_user[-1]
            growth_rate = (revenue_per_user[-1] / revenue_per_user[0]) ** (1 / len(revenue_per_user)) - 1
            return sum(last_value * (1 + growth_rate) ** i for i in range(12))
        elif trend == "stable":
            # Use average revenue for 12 periods
            avg_revenue = sum(revenue_per_user) / len(revenue_per_user)
            return avg_revenue * 12
        else:
            # Assume declining value
            return sum(revenue_per_user) * 1.5  # Conservative estimate
            
    async def _generate_insights(
        self,
        definition: CohortDefinition,
        metrics_by_period: List[CohortMetrics],
        summary_stats: Dict[str, Any]
    ) -> List[str]:
        """Generate actionable insights from cohort analysis"""
        insights = []
        
        if not metrics_by_period:
            return ["No data available for analysis"]
            
        retention_stats = summary_stats.get("retention_stats", {})
        engagement_stats = summary_stats.get("engagement_stats", {})
        revenue_stats = summary_stats.get("revenue_stats", {})
        
        # Retention insights
        final_retention = retention_stats.get("final_retention", 0.0)
        retention_decline = retention_stats.get("retention_decline_rate", 0.0)
        
        if final_retention > 0.5:
            insights.append("Strong cohort retention - users are highly engaged with your content")
        elif final_retention > 0.3:
            insights.append("Moderate cohort retention - opportunity for improvement in user engagement")
        else:
            insights.append("Low cohort retention - significant churn indicates need for retention strategies")
            
        if retention_decline > 0.7:
            insights.append("Steep retention decline - users are dropping off quickly after initial engagement")
        elif retention_decline < 0.3:
            insights.append("Good retention stability - users remain engaged over time")
            
        # Engagement insights
        engagement_trend = engagement_stats.get("engagement_trend", "stable")
        avg_engagement = engagement_stats.get("avg_engagement", 0.0)
        
        if engagement_trend == "increasing":
            insights.append("User engagement is growing over time - your content strategy is working")
        elif engagement_trend == "decreasing":
            insights.append("User engagement is declining - consider refreshing content strategy")
            
        if avg_engagement > 0.1:
            insights.append("High user engagement levels indicate strong content-audience fit")
        elif avg_engagement < 0.05:
            insights.append("Low engagement levels suggest content may not resonate with this cohort")
            
        # Revenue insights
        revenue_trend = revenue_stats.get("revenue_trend", "stable")
        ltv_estimate = revenue_stats.get("lifetime_value_estimate", 0.0)
        
        if revenue_trend == "increasing":
            insights.append("Revenue per user is growing - strong monetization trajectory")
        elif revenue_trend == "decreasing":
            insights.append("Revenue per user is declining - review monetization strategies")
            
        if ltv_estimate > 50:
            insights.append(f"High estimated lifetime value (${ltv_estimate:.2f}) indicates valuable cohort")
        elif ltv_estimate < 10:
            insights.append(f"Low estimated lifetime value (${ltv_estimate:.2f}) suggests need for monetization improvement")
            
        # Cohort-specific insights
        if definition.cohort_type == CohortType.PLATFORM:
            platform = definition.criteria.get("platform")
            insights.append(f"This {platform} acquisition cohort shows platform-specific user behavior patterns")
        elif definition.cohort_type == CohortType.CONTENT_TYPE:
            content_type = definition.criteria.get("content_type")
            insights.append(f"Users who discovered your content through {content_type} show distinct engagement patterns")
            
        return insights
        
    async def _generate_recommendations(
        self,
        definition: CohortDefinition,
        metrics_by_period: List[CohortMetrics],
        summary_stats: Dict[str, Any]
    ) -> List[str]:
        """Generate actionable recommendations based on cohort analysis"""
        recommendations = []
        
        if not metrics_by_period:
            return ["Collect more user data to enable cohort analysis"]
            
        retention_stats = summary_stats.get("retention_stats", {})
        engagement_stats = summary_stats.get("engagement_stats", {})
        revenue_stats = summary_stats.get("revenue_stats", {})
        
        # Retention recommendations
        final_retention = retention_stats.get("final_retention", 0.0)
        if final_retention < 0.3:
            recommendations.append("Implement onboarding improvements and early engagement campaigns")
            recommendations.append("Create retention-focused content for the first 30 days")
            
        # Engagement recommendations
        engagement_trend = engagement_stats.get("engagement_trend", "stable")
        if engagement_trend == "decreasing":
            recommendations.append("Introduce gamification elements to boost engagement")
            recommendations.append("Personalize content recommendations based on user preferences")
            
        # Revenue recommendations
        revenue_trend = revenue_stats.get("revenue_trend", "stable")
        if revenue_trend == "decreasing":
            recommendations.append("Review pricing strategy and introduce value-added services")
            recommendations.append("Create targeted monetization campaigns for high-value users")
            
        # General recommendations based on cohort performance
        if len(metrics_by_period) >= 3:
            recent_retention = metrics_by_period[-1].retention_rate
            early_retention = metrics_by_period[1].retention_rate if len(metrics_by_period) > 1 else 0
            
            if recent_retention > early_retention:
                recommendations.append("Your retention is improving over time - scale successful strategies")
            else:
                recommendations.append("Focus on long-term user value creation and loyalty programs")
                
        return recommendations
        
    async def compare_cohorts(self, cohort_ids: List[str]) -> Dict[str, Any]:
        """Compare multiple cohorts and identify patterns"""
        if len(cohort_ids) < 2:
            raise ValueError("At least 2 cohorts required for comparison")
            
        # Analyze all cohorts
        cohort_results = {}
        for cohort_id in cohort_ids:
            cohort_results[cohort_id] = await self.analyze_cohort(cohort_id)
            
        # Generate comparison insights
        comparison = {
            "cohorts_compared": len(cohort_ids),
            "comparison_summary": {},
            "best_performing": {},
            "recommendations": []
        }
        
        # Compare key metrics
        retention_rates = {
            cid: result.summary_stats.get("retention_stats", {}).get("final_retention", 0.0)
            for cid, result in cohort_results.items()
        }
        
        engagement_rates = {
            cid: result.summary_stats.get("engagement_stats", {}).get("avg_engagement", 0.0)
            for cid, result in cohort_results.items()
        }
        
        ltv_estimates = {
            cid: result.summary_stats.get("revenue_stats", {}).get("lifetime_value_estimate", 0.0)
            for cid, result in cohort_results.items()
        }
        
        # Identify best performers
        comparison["best_performing"] = {
            "retention": max(retention_rates, key=retention_rates.get),
            "engagement": max(engagement_rates, key=engagement_rates.get),
            "lifetime_value": max(ltv_estimates, key=ltv_estimates.get)
        }
        
        # Generate comparison recommendations
        best_retention_cohort = comparison["best_performing"]["retention"]
        best_retention_def = cohort_results[best_retention_cohort].cohort_definition
        
        comparison["recommendations"].append(
            f"Replicate strategies from {best_retention_cohort} ({best_retention_def.cohort_type.value}) "
            f"which shows highest retention rate ({retention_rates[best_retention_cohort]:.2%})"
        )
        
        return comparison
    
    async def analyze_cohorts(self, cohort_ids: List[str] = None, 
                            period_type: PeriodType = PeriodType.MONTHLY) -> Dict[str, Any]:
        """
        Analyze multiple cohorts or all defined cohorts
        
        Args:
            cohort_ids: List of specific cohort IDs to analyze, or None for all
            period_type: Period type for analysis grouping
            
        Returns:
            Dictionary containing analysis results for all cohorts
        """
        try:
            if cohort_ids is None:
                # Analyze all defined cohorts
                cohort_ids = list(self.cohort_definitions.keys())
            
            results = {}
            summary_stats = {
                'total_cohorts_analyzed': 0,
                'total_users_analyzed': 0,
                'average_retention_rate': 0.0,
                'best_performing_cohort': None,
                'worst_performing_cohort': None
            }
            
            retention_rates = []
            
            for cohort_id in cohort_ids:
                if cohort_id in self.cohort_definitions:
                    # Analyze individual cohort
                    cohort_result = await self.analyze_cohort(cohort_id)
                    results[cohort_id] = {
                        'cohort_size': cohort_result.cohort_size,
                        'retention_rate': cohort_result.summary_stats.get('retention_rate', 0.0),
                        'periods_analyzed': cohort_result.periods_analyzed,
                        'summary_stats': cohort_result.summary_stats,
                        'insights': cohort_result.insights
                    }
                    
                    retention_rates.append(cohort_result.summary_stats.get('retention_rate', 0.0))
                    summary_stats['total_users_analyzed'] += cohort_result.cohort_size
                    summary_stats['total_cohorts_analyzed'] += 1
            
            # Calculate summary statistics
            if retention_rates:
                summary_stats['average_retention_rate'] = np.mean(retention_rates)
                
                # Find best and worst performing cohorts
                if len(retention_rates) > 0:
                    best_idx = np.argmax(retention_rates)
                    worst_idx = np.argmin(retention_rates)
                    
                    cohort_ids_list = list(results.keys())
                    summary_stats['best_performing_cohort'] = {
                        'cohort_id': cohort_ids_list[best_idx],
                        'retention_rate': retention_rates[best_idx]
                    }
                    summary_stats['worst_performing_cohort'] = {
                        'cohort_id': cohort_ids_list[worst_idx], 
                        'retention_rate': retention_rates[worst_idx]
                    }
            
            return {
                'summary_stats': summary_stats,
                'cohort_results': results,
                'analyzed_at': datetime.now(timezone.utc).isoformat(),
                'period_type': period_type.value
            }
            
        except Exception as e:
            self.logger.error(f"Cohorts analysis failed: {e}")
            raise

# Usage example
async def example_usage():
    """Example usage of CohortAnalytics"""
    analytics = CohortAnalytics()
    
    # Generate sample user events
    sample_events = []
    base_time = datetime.now(timezone.utc) - timedelta(days=90)
    
    for user_id in range(1, 1001):  # 1000 users
        # First interaction
        first_event = UserEvent(
            user_id=f"user_{user_id}",
            event_type="signup",
            event_timestamp=base_time + timedelta(days=user_id % 30),
            platform="instagram",
            engagement_score=0.5 + (user_id % 10) * 0.05
        )
        sample_events.append(first_event)
        
        # Follow-up interactions
        for day in range(1, 60):
            if (user_id + day) % 3 == 0:  # Some users more active
                event = UserEvent(
                    user_id=f"user_{user_id}",
                    event_type="engagement",
                    event_timestamp=first_event.event_timestamp + timedelta(days=day),
                    platform="instagram",
                    engagement_score=0.3 + (day % 5) * 0.1,
                    revenue=5.0 if day % 10 == 0 else 0.0
                )
                sample_events.append(event)
                
    await analytics.add_user_events(sample_events)
    
    # Define acquisition cohort
    cohort_def = CohortDefinition(
        cohort_id="instagram_acquisition_week1",
        cohort_type=CohortType.ACQUISITION,
        period_type=PeriodType.WEEKLY,
        start_date=base_time,
        end_date=base_time + timedelta(days=7),
        description="Users acquired in first week on Instagram"
    )
    
    await analytics.define_cohort(cohort_def)
    
    # Analyze cohort
    result = await analytics.analyze_cohort("instagram_acquisition_week1")
    
    print(f"Cohort Analysis Results:")
    print(f"Cohort Size: {result.cohort_size}")
    print(f"Periods Analyzed: {result.periods_analyzed}")
    print(f"Summary Stats: {json.dumps(result.summary_stats, indent=2)}")
    print(f"Insights: {result.insights}")
    print(f"Recommendations: {result.recommendations}")

if __name__ == "__main__":
    asyncio.run(example_usage())

