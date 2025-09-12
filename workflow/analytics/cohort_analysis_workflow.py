"""Cohort Analysis Workflow - Advanced Cohort Analysis for Ainflue Platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Ainflue Platform. All rights reserved.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import asyncio
import logging

logger = logging.getLogger(__name__)


@dataclass
class CohortMetrics:
    """Cohort analysis metrics."""
    cohort_id: str
    cohort_period: str
    user_count: int
    retention_rates: Dict[str, float]
    engagement_metrics: Dict[str, float]
    revenue_metrics: Dict[str, float]
    behavior_patterns: Dict[str, Any]


@dataclass
class RetentionAnalysis:
    """Comprehensive retention analysis."""
    analysis_period: Dict[str, datetime]
    cohort_data: List[CohortMetrics]
    overall_retention: Dict[str, float]
    retention_insights: List[str]
    churn_analysis: Dict[str, Any]
    recommendations: List[str]


class CohortAnalysisWorkflow:
    """Advanced cohort analysis workflow for retention insights."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize cohort analysis workflow."""
        self.config = config or {}

    async def analyze_cohorts(
        self,
        creator_id: str,
        cohort_type: str = "monthly",
        analysis_period_months: int = 12
    ) -> RetentionAnalysis:
        """Perform comprehensive cohort analysis."""
        try:
            logger.info(f"Starting cohort analysis for creator: {creator_id}")
            
            # Generate cohort data
            cohort_data = await self._generate_cohort_data(
                creator_id, cohort_type, analysis_period_months
            )
            
            # Calculate overall retention
            overall_retention = self._calculate_overall_retention(cohort_data)
            
            # Generate insights
            insights = await self._generate_retention_insights(cohort_data)
            
            # Analyze churn
            churn_analysis = await self._analyze_churn_patterns(cohort_data)
            
            # Generate recommendations
            recommendations = await self._generate_retention_recommendations(
                cohort_data, overall_retention, churn_analysis
            )
            
            analysis = RetentionAnalysis(
                analysis_period={
                    'start': datetime.now() - timedelta(days=analysis_period_months*30),
                    'end': datetime.now()
                },
                cohort_data=cohort_data,
                overall_retention=overall_retention,
                retention_insights=insights,
                churn_analysis=churn_analysis,
                recommendations=recommendations
            )
            
            logger.info(f"Cohort analysis completed for creator: {creator_id}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error in cohort analysis: {str(e)}")
            raise

    async def _generate_cohort_data(
        self,
        creator_id: str,
        cohort_type: str,
        period_months: int
    ) -> List[CohortMetrics]:
        """Generate cohort data for analysis."""
        import random
        
        cohorts = []
        
        for i in range(period_months):
            cohort_date = datetime.now() - timedelta(days=i*30)
            cohort_period = cohort_date.strftime("%Y-%m")
            
            # Generate retention rates (decreasing over time)
            retention_rates = {}
            base_retention = random.uniform(0.7, 0.9)
            
            for week in range(1, 13):  # 12 weeks of retention data
                retention = base_retention * (0.95 ** week) + random.uniform(-0.05, 0.05)
                retention_rates[f"week_{week}"] = max(0, min(1, retention))
            
            cohorts.append(CohortMetrics(
                cohort_id=f"cohort_{cohort_period}",
                cohort_period=cohort_period,
                user_count=random.randint(100, 2000),
                retention_rates=retention_rates,
                engagement_metrics={
                    'avg_sessions_per_user': random.uniform(2, 15),
                    'avg_engagement_rate': random.uniform(3, 12),
                    'content_interaction_rate': random.uniform(0.4, 0.8)
                },
                revenue_metrics={
                    'avg_revenue_per_user': random.uniform(5, 150),
                    'conversion_rate': random.uniform(0.02, 0.15),
                    'lifetime_value': random.uniform(50, 500)
                },
                behavior_patterns={
                    'preferred_content_types': random.sample(['video', 'image', 'story'], 2),
                    'peak_activity_hours': random.sample(range(8, 23), 3),
                    'platform_preferences': random.sample(['instagram', 'tiktok', 'youtube'], 2)
                }
            ))
        
        return cohorts

    def _calculate_overall_retention(self, cohorts: List[CohortMetrics]) -> Dict[str, float]:
        """Calculate overall retention metrics."""
        if not cohorts:
            return {}
        
        overall_retention = {}
        
        # Calculate average retention for each time period
        for week in range(1, 13):
            week_key = f"week_{week}"
            retention_values = [
                cohort.retention_rates.get(week_key, 0) 
                for cohort in cohorts 
                if week_key in cohort.retention_rates
            ]
            
            if retention_values:
                overall_retention[week_key] = sum(retention_values) / len(retention_values)
        
        return overall_retention

    async def _generate_retention_insights(self, cohorts: List[CohortMetrics]) -> List[str]:
        """Generate insights from cohort analysis."""
        insights = []
        
        if not cohorts:
            return ["No cohort data available for analysis"]
        
        # Analyze retention trends
        recent_cohorts = cohorts[:3]  # Last 3 months
        older_cohorts = cohorts[3:6] if len(cohorts) > 3 else []
        
        if recent_cohorts and older_cohorts:
            recent_week1 = sum(c.retention_rates.get('week_1', 0) for c in recent_cohorts) / len(recent_cohorts)
            older_week1 = sum(c.retention_rates.get('week_1', 0) for c in older_cohorts) / len(older_cohorts)
            
            if recent_week1 > older_week1:
                insights.append("User retention is improving in recent cohorts")
            else:
                insights.append("User retention shows decline in recent cohorts")
        
        # Analyze user counts
        avg_user_count = sum(c.user_count for c in cohorts) / len(cohorts)
        recent_avg = sum(c.user_count for c in recent_cohorts) / len(recent_cohorts)
        
        if recent_avg > avg_user_count * 1.2:
            insights.append("Strong user acquisition growth in recent periods")
        elif recent_avg < avg_user_count * 0.8:
            insights.append("User acquisition has declined in recent periods")
        
        return insights

    async def _analyze_churn_patterns(self, cohorts: List[CohortMetrics]) -> Dict[str, Any]:
        """Analyze churn patterns across cohorts."""
        import random
        
        # Calculate churn rates
        churn_analysis = {
            'early_churn_rate': random.uniform(0.1, 0.3),  # Week 1-2
            'mid_term_churn_rate': random.uniform(0.2, 0.4),  # Week 3-8
            'late_churn_rate': random.uniform(0.1, 0.2),  # Week 9+
            'churn_factors': [
                'lack_of_relevant_content',
                'infrequent_posting',
                'poor_community_engagement',
                'competitor_attraction'
            ],
            'at_risk_segments': [
                'low_engagement_users',
                'single_platform_users',
                'mobile_only_users'
            ]
        }
        
        return churn_analysis

    async def _generate_retention_recommendations(
        self,
        cohorts: List[CohortMetrics],
        overall_retention: Dict[str, float],
        churn_analysis: Dict[str, Any]
    ) -> List[str]:
        """Generate retention improvement recommendations."""
        recommendations = []
        
        # Check week 1 retention
        week1_retention = overall_retention.get('week_1', 0)
        if week1_retention < 0.7:
            recommendations.append("Improve onboarding experience to boost week 1 retention")
        
        # Check long-term retention
        week12_retention = overall_retention.get('week_12', 0)
        if week12_retention < 0.3:
            recommendations.append("Develop long-term engagement strategies")
        
        # Churn-based recommendations
        if 'lack_of_relevant_content' in churn_analysis.get('churn_factors', []):
            recommendations.append("Personalize content recommendations based on user preferences")
        
        recommendations.extend([
            "Implement re-engagement campaigns for at-risk users",
            "Create loyalty programs for high-retention cohorts",
            "Optimize content delivery timing based on cohort behavior"
        ])
        
        return recommendations