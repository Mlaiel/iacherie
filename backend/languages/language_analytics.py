"""Language Analytics - Language Usage Analytics and Insights Engine
================================================================================
Module: backend/languages/language_analytics.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Industrial Language Analytics Engine - Usage Tracking and Business Insights
Responsibility: Language preference tracking, translation performance metrics, market penetration insights
Technologies: Python, Analytics, Data Processing, Statistical Analysis, Business Intelligence
================================================================================

⚠️  PROPRIETARY SOFTWARE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use strictly prohibited and subject to legal prosecution.
Contact: mlaiel@live.de

BUSINESS LOGIC:
Usage data collection → Language preference analysis → Performance metrics → 
Cultural engagement tracking → Market insights → ROI calculations → Business recommendations
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone, timedelta
import json
import statistics
from collections import defaultdict, Counter

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

logger = logging.getLogger(__name__)


class AnalyticsMetric(Enum):
    """Analytics metrics for language usage"""
    USAGE_FREQUENCY = "usage_frequency"
    TRANSLATION_VOLUME = "translation_volume"
    QUALITY_SCORES = "quality_scores"
    USER_ENGAGEMENT = "user_engagement"
    CULTURAL_ADAPTATION = "cultural_adaptation"
    PERFORMANCE_METRICS = "performance_metrics"
    MARKET_PENETRATION = "market_penetration"
    ROI_ANALYSIS = "roi_analysis"


class TimeGranularity(Enum):
    """Time granularity for analytics"""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class MarketSegment(Enum):
    """Market segments for analysis"""
    ENTERPRISE = "enterprise"
    SMB = "smb"
    CONSUMER = "consumer"
    EDUCATION = "education"
    GOVERNMENT = "government"
    HEALTHCARE = "healthcare"
    FINANCIAL = "financial"


class EngagementType(Enum):
    """Types of user engagement"""
    TRANSLATION_REQUEST = "translation_request"
    QUALITY_FEEDBACK = "quality_feedback"
    CULTURAL_ADAPTATION = "cultural_adaptation"
    CONTENT_LOCALIZATION = "content_localization"
    API_USAGE = "api_usage"
    UI_INTERACTION = "ui_interaction"


@dataclass
class AnalyticsRequest:
    """Request for analytics data"""
    metrics: List[AnalyticsMetric]
    start_date: datetime
    end_date: datetime
    languages: Optional[List[str]] = None
    markets: Optional[List[str]] = None
    granularity: TimeGranularity = TimeGranularity.DAILY
    segment: Optional[MarketSegment] = None
    include_projections: bool = False


@dataclass
class LanguageUsageData:
    """Language usage statistics"""
    language_code: str
    total_requests: int
    unique_users: int
    translation_volume: int
    quality_score: float
    engagement_rate: float
    revenue_impact: float
    growth_rate: float
    market_share: float


@dataclass
class TranslationPerformanceData:
    """Translation performance metrics"""
    language_pair: str
    total_translations: int
    average_quality: float
    average_latency: float
    success_rate: float
    error_rate: float
    user_satisfaction: float
    cost_per_translation: float


@dataclass
class CulturalEngagementData:
    """Cultural engagement metrics"""
    culture_region: str
    adaptation_requests: int
    engagement_score: float
    cultural_accuracy: float
    feedback_sentiment: float
    retention_rate: float
    conversion_rate: float


@dataclass
class MarketPenetrationData:
    """Market penetration analysis"""
    market_region: str
    total_addressable_market: int
    current_users: int
    penetration_rate: float
    growth_potential: float
    competitive_position: str
    revenue_opportunity: float


@dataclass
class ROIAnalysisData:
    """ROI analysis for language investments"""
    language_code: str
    investment_cost: float
    revenue_generated: float
    roi_percentage: float
    payback_period_days: int
    customer_acquisition_cost: float
    customer_lifetime_value: float


@dataclass
class AnalyticsResult:
    """Comprehensive analytics result"""
    language_usage: List[LanguageUsageData] = field(default_factory=list)
    translation_performance: List[TranslationPerformanceData] = field(default_factory=list)
    cultural_engagement: List[CulturalEngagementData] = field(default_factory=list)
    market_penetration: List[MarketPenetrationData] = field(default_factory=list)
    roi_analysis: List[ROIAnalysisData] = field(default_factory=list)
    insights: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    trends: Dict[str, Any] = field(default_factory=dict)
    projections: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UsageEvent:
    """Individual usage event for tracking"""
    event_id: str
    timestamp: datetime
    user_id: str
    language_code: str
    event_type: EngagementType
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LanguageInsight:
    """Business insight about language usage"""
    insight_type: str
    language_code: str
    description: str
    impact_score: float
    confidence: float
    recommended_actions: List[str]


class LanguageAnalyticsEngine:
    """
    Advanced language analytics engine providing comprehensive
    insights into language usage, performance, and business impact
    """
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        """Initialize language analytics engine"""
        self.config = config or {}
        self.usage_events = []
        self.cached_analytics = {}
        self.insights_cache = {}
        
        # Analytics configuration
        self.analytics_config = {
            "retention_days": 365,
            "min_sample_size": 100,
            "confidence_threshold": 0.8,
            "trend_window_days": 30
        }
        
        # Market data (would typically come from external sources)
        self.market_data = self._initialize_market_data()
        
        # Revenue models
        self.revenue_models = {
            "translation_per_word": 0.02,
            "api_per_request": 0.001,
            "subscription_monthly": 29.99,
            "enterprise_annual": 10000.0
        }
        
        logger.info("LanguageAnalyticsEngine initialized")
    
    async def generate_analytics(self, request: AnalyticsRequest) -> AnalyticsResult:
        """
        Generate comprehensive language analytics
        
        Args:
            request: Analytics request parameters
            
        Returns:
            AnalyticsResult with usage patterns, performance metrics, and insights
        """
        try:
            start_time = datetime.now(timezone.utc)
            
            result = AnalyticsResult()
            
            # Generate analytics for each requested metric
            for metric in request.metrics:
                if metric == AnalyticsMetric.USAGE_FREQUENCY:
                    result.language_usage = await self._analyze_language_usage(request)
                elif metric == AnalyticsMetric.TRANSLATION_VOLUME:
                    result.translation_performance = await self._analyze_translation_performance(request)
                elif metric == AnalyticsMetric.CULTURAL_ADAPTATION:
                    result.cultural_engagement = await self._analyze_cultural_engagement(request)
                elif metric == AnalyticsMetric.MARKET_PENETRATION:
                    result.market_penetration = await self._analyze_market_penetration(request)
                elif metric == AnalyticsMetric.ROI_ANALYSIS:
                    result.roi_analysis = await self._analyze_roi(request)
            
            # Generate insights and recommendations
            result.insights = await self._generate_insights(request, result)
            result.recommendations = await self._generate_recommendations(request, result)
            
            # Identify trends
            result.trends = await self._identify_trends(request, result)
            
            # Generate projections if requested
            if request.include_projections:
                result.projections = await self._generate_projections(request, result)
            
            result.metadata = {
                "request_id": f"analytics_{int(start_time.timestamp())}",
                "processing_time": (datetime.now(timezone.utc) - start_time).total_seconds(),
                "metrics_generated": len(request.metrics),
                "date_range_days": (request.end_date - request.start_date).days,
                "languages_analyzed": len(request.languages) if request.languages else 0
            }
            
            logger.info(f"Analytics generated for {len(request.metrics)} metrics "
                       f"({request.granularity.value} granularity)")
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating analytics: {str(e)}")
            return AnalyticsResult(
                metadata={"error": str(e)}
            )
    
    async def track_usage_event(self, event: UsageEvent) -> bool:
        """
        Track a language usage event
        
        Args:
            event: Usage event to track
            
        Returns:
            Success status
        """
        try:
            self.usage_events.append(event)
            
            # Maintain event history within retention period
            cutoff_date = datetime.now(timezone.utc) - timedelta(
                days=self.analytics_config["retention_days"]
            )
            self.usage_events = [
                e for e in self.usage_events if e.timestamp >= cutoff_date
            ]
            
            # Clear relevant caches
            self._invalidate_analytics_cache()
            
            logger.debug(f"Usage event tracked: {event.event_type.value} for {event.language_code}")
            return True
            
        except Exception as e:
            logger.error(f"Error tracking usage event: {str(e)}")
            return False
    
    async def get_language_insights(self, language_code: str, 
                                  days_back: int = 30) -> List[LanguageInsight]:
        """
        Get business insights for a specific language
        
        Args:
            language_code: Language to analyze
            days_back: Number of days to analyze
            
        Returns:
            List of business insights
        """
        insights = []
        
        # Get usage data for the language
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days_back)
        
        language_events = [
            e for e in self.usage_events
            if e.language_code == language_code and start_date <= e.timestamp <= end_date
        ]
        
        if len(language_events) < self.analytics_config["min_sample_size"]:
            return insights
        
        # Growth trend insight
        growth_insight = await self._analyze_growth_trend(language_code, language_events)
        if growth_insight:
            insights.append(growth_insight)
        
        # Quality trend insight
        quality_insight = await self._analyze_quality_trend(language_code, language_events)
        if quality_insight:
            insights.append(quality_insight)
        
        # Usage pattern insight
        pattern_insight = await self._analyze_usage_patterns(language_code, language_events)
        if pattern_insight:
            insights.append(pattern_insight)
        
        # Revenue opportunity insight
        revenue_insight = await self._analyze_revenue_opportunity(language_code, language_events)
        if revenue_insight:
            insights.append(revenue_insight)
        
        return insights
    
    async def get_top_performing_languages(self, metric: AnalyticsMetric, 
                                         limit: int = 10) -> List[Tuple[str, float]]:
        """
        Get top performing languages by specific metric
        
        Args:
            metric: Metric to rank by
            limit: Number of languages to return
            
        Returns:
            List of (language_code, score) tuples
        """
        language_scores = {}
        
        # Calculate scores based on metric
        for event in self.usage_events:
            lang = event.language_code
            if lang not in language_scores:
                language_scores[lang] = []
            
            # Add metric-specific score
            if metric == AnalyticsMetric.USAGE_FREQUENCY:
                language_scores[lang].append(1.0)
            elif metric == AnalyticsMetric.USER_ENGAGEMENT:
                engagement_score = event.metadata.get("engagement_score", 0.5)
                language_scores[lang].append(engagement_score)
            elif metric == AnalyticsMetric.QUALITY_SCORES:
                quality_score = event.metadata.get("quality_score", 0.7)
                language_scores[lang].append(quality_score)
        
        # Calculate average scores
        avg_scores = {
            lang: statistics.mean(scores) if scores else 0.0
            for lang, scores in language_scores.items()
        }
        
        # Sort and return top performers
        sorted_languages = sorted(avg_scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_languages[:limit]
    
    async def _analyze_language_usage(self, request: AnalyticsRequest) -> List[LanguageUsageData]:
        """Analyze language usage patterns"""
        usage_data = []
        
        # Filter events by request criteria
        filtered_events = self._filter_events_by_request(request)
        
        # Group by language
        language_groups = defaultdict(list)
        for event in filtered_events:
            language_groups[event.language_code].append(event)
        
        for language_code, events in language_groups.items():
            # Calculate usage metrics
            total_requests = len(events)
            unique_users = len(set(e.user_id for e in events))
            
            # Calculate quality score
            quality_scores = [e.metadata.get("quality_score", 0.7) for e in events]
            avg_quality = statistics.mean(quality_scores) if quality_scores else 0.7
            
            # Calculate engagement rate
            engagement_events = [e for e in events if e.event_type == EngagementType.UI_INTERACTION]
            engagement_rate = len(engagement_events) / total_requests if total_requests > 0 else 0.0
            
            # Calculate revenue impact (placeholder)
            revenue_impact = total_requests * self.revenue_models["api_per_request"]
            
            # Calculate growth rate
            growth_rate = await self._calculate_growth_rate(language_code, request.start_date, request.end_date)
            
            # Calculate market share
            total_all_requests = len(filtered_events)
            market_share = total_requests / total_all_requests if total_all_requests > 0 else 0.0
            
            usage_data.append(LanguageUsageData(
                language_code=language_code,
                total_requests=total_requests,
                unique_users=unique_users,
                translation_volume=len([e for e in events if e.event_type == EngagementType.TRANSLATION_REQUEST]),
                quality_score=avg_quality,
                engagement_rate=engagement_rate,
                revenue_impact=revenue_impact,
                growth_rate=growth_rate,
                market_share=market_share
            ))
        
        return sorted(usage_data, key=lambda x: x.total_requests, reverse=True)
    
    async def _analyze_translation_performance(self, request: AnalyticsRequest) -> List[TranslationPerformanceData]:
        """Analyze translation performance metrics"""
        performance_data = []
        
        # Filter translation events
        translation_events = [
            e for e in self._filter_events_by_request(request)
            if e.event_type == EngagementType.TRANSLATION_REQUEST
        ]
        
        # Group by language pairs
        pair_groups = defaultdict(list)
        for event in translation_events:
            source_lang = event.metadata.get("source_language", "auto")
            target_lang = event.language_code
            pair_key = f"{source_lang}-{target_lang}"
            pair_groups[pair_key].append(event)
        
        for pair_key, events in pair_groups.items():
            if len(events) < 10:  # Skip pairs with insufficient data
                continue
            
            # Calculate performance metrics
            total_translations = len(events)
            
            quality_scores = [e.metadata.get("quality_score", 0.7) for e in events]
            average_quality = statistics.mean(quality_scores)
            
            latencies = [e.metadata.get("latency_ms", 500) for e in events]
            average_latency = statistics.mean(latencies) / 1000.0  # Convert to seconds
            
            success_events = [e for e in events if e.metadata.get("success", True)]
            success_rate = len(success_events) / total_translations
            error_rate = 1.0 - success_rate
            
            satisfaction_scores = [e.metadata.get("user_satisfaction", 0.8) for e in events]
            user_satisfaction = statistics.mean(satisfaction_scores)
            
            cost_per_translation = self.revenue_models["api_per_request"]
            
            performance_data.append(TranslationPerformanceData(
                language_pair=pair_key,
                total_translations=total_translations,
                average_quality=average_quality,
                average_latency=average_latency,
                success_rate=success_rate,
                error_rate=error_rate,
                user_satisfaction=user_satisfaction,
                cost_per_translation=cost_per_translation
            ))
        
        return sorted(performance_data, key=lambda x: x.total_translations, reverse=True)
    
    async def _analyze_cultural_engagement(self, request: AnalyticsRequest) -> List[CulturalEngagementData]:
        """Analyze cultural engagement metrics"""
        engagement_data = []
        
        # Filter cultural adaptation events
        cultural_events = [
            e for e in self._filter_events_by_request(request)
            if e.event_type == EngagementType.CULTURAL_ADAPTATION
        ]
        
        # Group by culture regions
        region_groups = defaultdict(list)
        for event in cultural_events:
            region = event.metadata.get("culture_region", "unknown")
            region_groups[region].append(event)
        
        for region, events in region_groups.items():
            if len(events) < 5:  # Skip regions with insufficient data
                continue
            
            adaptation_requests = len(events)
            
            engagement_scores = [e.metadata.get("engagement_score", 0.6) for e in events]
            engagement_score = statistics.mean(engagement_scores)
            
            accuracy_scores = [e.metadata.get("cultural_accuracy", 0.7) for e in events]
            cultural_accuracy = statistics.mean(accuracy_scores)
            
            sentiment_scores = [e.metadata.get("feedback_sentiment", 0.6) for e in events]
            feedback_sentiment = statistics.mean(sentiment_scores)
            
            # Calculate retention and conversion (placeholder)
            retention_rate = 0.75
            conversion_rate = 0.15
            
            engagement_data.append(CulturalEngagementData(
                culture_region=region,
                adaptation_requests=adaptation_requests,
                engagement_score=engagement_score,
                cultural_accuracy=cultural_accuracy,
                feedback_sentiment=feedback_sentiment,
                retention_rate=retention_rate,
                conversion_rate=conversion_rate
            ))
        
        return sorted(engagement_data, key=lambda x: x.engagement_score, reverse=True)
    
    async def _analyze_market_penetration(self, request: AnalyticsRequest) -> List[MarketPenetrationData]:
        """Analyze market penetration by region"""
        penetration_data = []
        
        # Get market data for analysis
        for market_region, market_info in self.market_data.items():
            if request.markets and market_region not in request.markets:
                continue
            
            # Get events for this market
            market_events = [
                e for e in self._filter_events_by_request(request)
                if e.metadata.get("market_region") == market_region
            ]
            
            current_users = len(set(e.user_id for e in market_events))
            total_addressable_market = market_info.get("population", 1000000)
            
            penetration_rate = current_users / total_addressable_market * 100
            
            # Calculate growth potential based on current penetration
            if penetration_rate < 1.0:
                growth_potential = 0.9
            elif penetration_rate < 5.0:
                growth_potential = 0.7
            else:
                growth_potential = 0.3
            
            competitive_position = "growing" if penetration_rate > 1.0 else "emerging"
            
            revenue_opportunity = (total_addressable_market * 0.05 * 
                                 self.revenue_models["subscription_monthly"] * 12)
            
            penetration_data.append(MarketPenetrationData(
                market_region=market_region,
                total_addressable_market=total_addressable_market,
                current_users=current_users,
                penetration_rate=penetration_rate,
                growth_potential=growth_potential,
                competitive_position=competitive_position,
                revenue_opportunity=revenue_opportunity
            ))
        
        return sorted(penetration_data, key=lambda x: x.revenue_opportunity, reverse=True)
    
    async def _analyze_roi(self, request: AnalyticsRequest) -> List[ROIAnalysisData]:
        """Analyze ROI for language investments"""
        roi_data = []
        
        # Filter events by request criteria
        filtered_events = self._filter_events_by_request(request)
        
        # Group by language
        language_groups = defaultdict(list)
        for event in filtered_events:
            language_groups[event.language_code].append(event)
        
        for language_code, events in language_groups.items():
            if len(events) < 50:  # Skip languages with insufficient data
                continue
            
            # Calculate investment cost (placeholder)
            investment_cost = 10000.0  # Base localization cost
            
            # Calculate revenue generated
            translation_requests = len([e for e in events if e.event_type == EngagementType.TRANSLATION_REQUEST])
            api_revenue = translation_requests * self.revenue_models["api_per_request"]
            
            subscription_users = len(set(e.user_id for e in events)) * 0.1  # 10% conversion rate
            subscription_revenue = subscription_users * self.revenue_models["subscription_monthly"] * 12
            
            revenue_generated = api_revenue + subscription_revenue
            
            # Calculate ROI
            roi_percentage = ((revenue_generated - investment_cost) / investment_cost) * 100 if investment_cost > 0 else 0
            
            # Calculate payback period
            monthly_revenue = revenue_generated / 12
            payback_period_days = int((investment_cost / monthly_revenue) * 30) if monthly_revenue > 0 else 999
            
            # Calculate CAC and LTV (placeholder)
            customer_acquisition_cost = investment_cost / len(set(e.user_id for e in events)) if events else 0
            customer_lifetime_value = subscription_revenue / subscription_users if subscription_users > 0 else 0
            
            roi_data.append(ROIAnalysisData(
                language_code=language_code,
                investment_cost=investment_cost,
                revenue_generated=revenue_generated,
                roi_percentage=roi_percentage,
                payback_period_days=payback_period_days,
                customer_acquisition_cost=customer_acquisition_cost,
                customer_lifetime_value=customer_lifetime_value
            ))
        
        return sorted(roi_data, key=lambda x: x.roi_percentage, reverse=True)
    
    async def _generate_insights(self, request: AnalyticsRequest, result: AnalyticsResult) -> List[str]:
        """Generate business insights from analytics data"""
        insights = []
        
        # Language usage insights
        if result.language_usage:
            top_language = max(result.language_usage, key=lambda x: x.total_requests)
            insights.append(f"Top performing language: {top_language.language_code} "
                          f"with {top_language.total_requests:,} requests")
            
            high_growth_langs = [l for l in result.language_usage if l.growth_rate > 0.2]
            if high_growth_langs:
                insights.append(f"{len(high_growth_langs)} languages showing high growth (>20%)")
        
        # Translation performance insights
        if result.translation_performance:
            low_quality_pairs = [p for p in result.translation_performance if p.average_quality < 0.7]
            if low_quality_pairs:
                insights.append(f"{len(low_quality_pairs)} language pairs need quality improvement")
            
            high_latency_pairs = [p for p in result.translation_performance if p.average_latency > 2.0]
            if high_latency_pairs:
                insights.append(f"{len(high_latency_pairs)} language pairs have high latency (>2s)")
        
        # Market penetration insights
        if result.market_penetration:
            high_opportunity_markets = [m for m in result.market_penetration if m.growth_potential > 0.7]
            if high_opportunity_markets:
                insights.append(f"{len(high_opportunity_markets)} markets offer high growth potential")
        
        # ROI insights
        if result.roi_analysis:
            profitable_languages = [r for r in result.roi_analysis if r.roi_percentage > 100]
            insights.append(f"{len(profitable_languages)} languages showing positive ROI")
            
            quick_payback_languages = [r for r in result.roi_analysis if r.payback_period_days < 365]
            if quick_payback_languages:
                insights.append(f"{len(quick_payback_languages)} languages with quick payback (<1 year)")
        
        return insights
    
    async def _generate_recommendations(self, request: AnalyticsRequest, result: AnalyticsResult) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Quality improvement recommendations
        if result.translation_performance:
            low_quality_pairs = [p for p in result.translation_performance if p.average_quality < 0.7]
            if low_quality_pairs:
                recommendations.append("Invest in improving translation quality for underperforming language pairs")
        
        # Growth opportunity recommendations
        if result.language_usage:
            high_growth_langs = [l for l in result.language_usage if l.growth_rate > 0.3]
            if high_growth_langs:
                recommendations.append("Increase marketing investment in high-growth languages")
        
        # Market expansion recommendations
        if result.market_penetration:
            high_opportunity_markets = [m for m in result.market_penetration 
                                      if m.growth_potential > 0.8 and m.penetration_rate < 2.0]
            if high_opportunity_markets:
                recommendations.append("Target market expansion in high-potential, low-penetration regions")
        
        # ROI optimization recommendations
        if result.roi_analysis:
            negative_roi_languages = [r for r in result.roi_analysis if r.roi_percentage < 0]
            if negative_roi_languages:
                recommendations.append("Review investment strategy for languages with negative ROI")
        
        return recommendations
    
    async def _identify_trends(self, request: AnalyticsRequest, result: AnalyticsResult) -> Dict[str, Any]:
        """Identify trends in the data"""
        trends = {}
        
        if result.language_usage:
            # Growth trend
            avg_growth = statistics.mean([l.growth_rate for l in result.language_usage])
            trends["overall_growth_rate"] = avg_growth
            
            # Quality trend
            avg_quality = statistics.mean([l.quality_score for l in result.language_usage])
            trends["overall_quality_score"] = avg_quality
            
            # Engagement trend
            avg_engagement = statistics.mean([l.engagement_rate for l in result.language_usage])
            trends["overall_engagement_rate"] = avg_engagement
        
        return trends
    
    async def _generate_projections(self, request: AnalyticsRequest, result: AnalyticsResult) -> Dict[str, Any]:
        """Generate future projections based on current trends"""
        projections = {}
        
        if result.language_usage and NUMPY_AVAILABLE:
            # Simple linear projection based on growth rates
            total_requests_current = sum(l.total_requests for l in result.language_usage)
            avg_growth_rate = statistics.mean([l.growth_rate for l in result.language_usage])
            
            # Project 6 months ahead
            projected_requests_6m = total_requests_current * (1 + avg_growth_rate * 0.5)
            projections["total_requests_6m"] = int(projected_requests_6m)
            
            # Project 12 months ahead
            projected_requests_12m = total_requests_current * (1 + avg_growth_rate)
            projections["total_requests_12m"] = int(projected_requests_12m)
        
        return projections
    
    def _filter_events_by_request(self, request: AnalyticsRequest) -> List[UsageEvent]:
        """Filter events based on request criteria"""
        filtered_events = []
        
        for event in self.usage_events:
            # Check date range
            if not (request.start_date <= event.timestamp <= request.end_date):
                continue
            
            # Check language filter
            if request.languages and event.language_code not in request.languages:
                continue
            
            # Check market filter
            if request.markets:
                event_market = event.metadata.get("market_region")
                if event_market not in request.markets:
                    continue
            
            filtered_events.append(event)
        
        return filtered_events
    
    async def _calculate_growth_rate(self, language_code: str, start_date: datetime, end_date: datetime) -> float:
        """Calculate growth rate for a language"""
        # Split period in half to compare
        mid_date = start_date + (end_date - start_date) / 2
        
        first_half_events = [
            e for e in self.usage_events
            if e.language_code == language_code and start_date <= e.timestamp <= mid_date
        ]
        
        second_half_events = [
            e for e in self.usage_events
            if e.language_code == language_code and mid_date < e.timestamp <= end_date
        ]
        
        if len(first_half_events) == 0:
            return 1.0 if len(second_half_events) > 0 else 0.0
        
        growth_rate = (len(second_half_events) - len(first_half_events)) / len(first_half_events)
        return max(-0.9, min(5.0, growth_rate))  # Cap between -90% and 500%
    
    async def _analyze_growth_trend(self, language_code: str, events: List[UsageEvent]) -> Optional[LanguageInsight]:
        """Analyze growth trend for a language"""
        if len(events) < 30:
            return None
        
        # Calculate weekly usage
        weekly_usage = defaultdict(int)
        for event in events:
            week_key = event.timestamp.strftime("%Y-W%U")
            weekly_usage[week_key] += 1
        
        usage_values = list(weekly_usage.values())
        if len(usage_values) < 3:
            return None
        
        # Calculate trend
        if NUMPY_AVAILABLE:
            x = np.arange(len(usage_values))
            slope = np.polyfit(x, usage_values, 1)[0]
        else:
            # Simple slope calculation
            slope = (usage_values[-1] - usage_values[0]) / len(usage_values)
        
        if slope > 5:
            return LanguageInsight(
                insight_type="growth",
                language_code=language_code,
                description=f"Strong growth trend detected (+{slope:.1f} requests/week)",
                impact_score=0.8,
                confidence=0.85,
                recommended_actions=["Increase marketing investment", "Expand language support"]
            )
        
        return None
    
    async def _analyze_quality_trend(self, language_code: str, events: List[UsageEvent]) -> Optional[LanguageInsight]:
        """Analyze quality trend for a language"""
        quality_scores = [e.metadata.get("quality_score") for e in events if "quality_score" in e.metadata]
        
        if len(quality_scores) < 20:
            return None
        
        avg_quality = statistics.mean(quality_scores)
        
        if avg_quality < 0.7:
            return LanguageInsight(
                insight_type="quality",
                language_code=language_code,
                description=f"Quality below threshold ({avg_quality:.2f})",
                impact_score=0.9,
                confidence=0.9,
                recommended_actions=["Improve translation models", "Add human review"]
            )
        
        return None
    
    async def _analyze_usage_patterns(self, language_code: str, events: List[UsageEvent]) -> Optional[LanguageInsight]:
        """Analyze usage patterns for a language"""
        # Analyze usage by hour
        hourly_usage = defaultdict(int)
        for event in events:
            hour = event.timestamp.hour
            hourly_usage[hour] += 1
        
        if hourly_usage:
            peak_hour = max(hourly_usage.items(), key=lambda x: x[1])
            if peak_hour[1] > len(events) * 0.2:  # >20% of usage in one hour
                return LanguageInsight(
                    insight_type="usage_pattern",
                    language_code=language_code,
                    description=f"Peak usage at hour {peak_hour[0]} ({peak_hour[1]} requests)",
                    impact_score=0.6,
                    confidence=0.8,
                    recommended_actions=["Optimize server capacity for peak hours"]
                )
        
        return None
    
    async def _analyze_revenue_opportunity(self, language_code: str, events: List[UsageEvent]) -> Optional[LanguageInsight]:
        """Analyze revenue opportunity for a language"""
        unique_users = len(set(e.user_id for e in events))
        current_revenue = len(events) * self.revenue_models["api_per_request"]
        
        # Estimate potential with 5% conversion to premium
        potential_revenue = unique_users * 0.05 * self.revenue_models["subscription_monthly"] * 12
        
        if potential_revenue > current_revenue * 10:
            return LanguageInsight(
                insight_type="revenue_opportunity",
                language_code=language_code,
                description=f"High revenue potential: ${potential_revenue:,.0f} vs current ${current_revenue:,.0f}",
                impact_score=0.9,
                confidence=0.7,
                recommended_actions=["Implement premium features", "Target enterprise customers"]
            )
        
        return None
    
    def _initialize_market_data(self) -> Dict[str, Dict[str, Any]]:
        """Initialize market data for analysis"""
        return {
            "US": {"population": 330000000, "gdp_per_capita": 65000, "internet_penetration": 0.89},
            "EU": {"population": 450000000, "gdp_per_capita": 35000, "internet_penetration": 0.87},
            "JP": {"population": 125000000, "gdp_per_capita": 40000, "internet_penetration": 0.93},
            "CN": {"population": 1400000000, "gdp_per_capita": 12000, "internet_penetration": 0.73},
            "IN": {"population": 1380000000, "gdp_per_capita": 2500, "internet_penetration": 0.50},
            "BR": {"population": 215000000, "gdp_per_capita": 9000, "internet_penetration": 0.74},
            "DE": {"population": 83000000, "gdp_per_capita": 46000, "internet_penetration": 0.89},
            "FR": {"population": 68000000, "gdp_per_capita": 39000, "internet_penetration": 0.85},
            "UK": {"population": 67000000, "gdp_per_capita": 42000, "internet_penetration": 0.95}
        }
    
    def _invalidate_analytics_cache(self) -> None:
        """Invalidate analytics cache when new data is added"""
        self.cached_analytics.clear()
        self.insights_cache.clear()
    
    async def get_analytics_summary(self) -> Dict[str, Any]:
        """Get summary of analytics capabilities and current data"""
        return {
            "total_events_tracked": len(self.usage_events),
            "unique_languages": len(set(e.language_code for e in self.usage_events)),
            "unique_users": len(set(e.user_id for e in self.usage_events)),
            "supported_metrics": [metric.value for metric in AnalyticsMetric],
            "time_granularities": [tg.value for tg in TimeGranularity],
            "market_segments": [ms.value for ms in MarketSegment],
            "engagement_types": [et.value for et in EngagementType],
            "data_retention_days": self.analytics_config["retention_days"],
            "markets_configured": len(self.market_data)
        }