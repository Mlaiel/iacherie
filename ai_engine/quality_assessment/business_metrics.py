"""
Business Metrics Module

Advanced business intelligence and performance metrics for content creators and influencers.
Provides comprehensive ROI analysis, monetization insights, and business growth indicators.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

 STRICT COPYRIGHT WARNING 
This software and all associated concepts, algorithms, and implementations are the exclusive 
intellectual property of Fahed Mlaiel (mlaiel@live.de). Any unauthorized use, reproduction, 
distribution, modification, or appropriation of this code, in whole or in part, without 
explicit written permission from Fahed Mlaiel is strictly prohibited and will be prosecuted 
to the full extent of the law.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
from collections import defaultdict
import json

from ..core.base_models import BaseAIModel, ModelConfig, ModelType, ModelProvider
from ..core.exceptions import QualityCheckError, BusinessMetricsError
from ..core.performance import PerformanceMonitor, monitor_performance
from ..core.metrics import MetricsCollector, metrics_collector

# Instanciation des modules de monitoring
performance_monitor = PerformanceMonitor()

logger = logging.getLogger(__name__)


class RevenueStream(Enum):
    """Revenue stream types"""
    SPONSORED_CONTENT = "sponsored_content"
    AFFILIATE_MARKETING = "affiliate_marketing"
    PRODUCT_SALES = "product_sales"
    COURSE_SALES = "course_sales"
    MEMBERSHIP = "membership"
    DONATIONS = "donations"
    AD_REVENUE = "ad_revenue"
    BRAND_PARTNERSHIPS = "brand_partnerships"
    LICENSING = "licensing"
    CONSULTING = "consulting"
    SPEAKING = "speaking"
    MERCHANDISING = "merchandising"


class BusinessModel(Enum):
    """Business model types for creators"""
    INFLUENCER = "influencer"
    EDUCATOR = "educator"
    ENTERTAINER = "entertainer"
    CONSULTANT = "consultant"
    ENTREPRENEUR = "entrepreneur"
    ARTIST = "artist"
    JOURNALIST = "journalist"
    LIFESTYLE_BRAND = "lifestyle_brand"


class GrowthStage(Enum):
    """Business growth stages"""
    STARTUP = "startup"  # < 10K followers
    EMERGING = "emerging"  # 10K - 100K followers
    ESTABLISHED = "established"  # 100K - 1M followers
    ENTERPRISE = "enterprise"  # > 1M followers


class MonetizationMaturity(Enum):
    """Monetization maturity levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


@dataclass
class AudienceMetrics:
    """Audience-related business metrics"""
    total_followers: int = field(default=0)
    engagement_rate: float = field(default=0.0)
    audience_quality_score: float = field(default=50.0)
    
    # Demographic value
    target_demographic_percentage: float = field(default=50.0)
    high_value_demographic_percentage: float = field(default=30.0)
    geographic_distribution_score: float = field(default=50.0)
    
    # Engagement quality
    authentic_engagement_rate: float = field(default=0.0)
    comment_sentiment_score: float = field(default=50.0)
    share_to_like_ratio: float = field(default=0.1)
    
    # Audience development
    follower_growth_rate: float = field(default=0.0)
    retention_rate: float = field(default=80.0)
    audience_loyalty_score: float = field(default=50.0)


@dataclass
class ContentPerformanceMetrics:
    """Content performance business metrics"""
    average_views: float = field(default=0.0)
    average_engagement: float = field(default=0.0)
    content_consistency_score: float = field(default=50.0)
    
    # Content value metrics
    viral_content_percentage: float = field(default=5.0)
    evergreen_content_percentage: float = field(default=20.0)
    conversion_content_percentage: float = field(default=10.0)
    
    # Performance trends
    view_growth_trend: float = field(default=0.0)
    engagement_growth_trend: float = field(default=0.0)
    content_quality_trend: float = field(default=0.0)
    
    # Platform performance
    platform_performance_scores: Dict[str, float] = field(default_factory=dict)
    cross_platform_synergy: float = field(default=50.0)


@dataclass
class MonetizationMetrics:
    """Monetization and revenue metrics"""
    total_revenue: float = field(default=0.0)
    revenue_per_follower: float = field(default=0.0)
    revenue_per_post: float = field(default=0.0)
    
    # Revenue streams
    revenue_streams: Dict[RevenueStream, float] = field(default_factory=dict)
    revenue_diversification_score: float = field(default=30.0)
    primary_revenue_dependency: float = field(default=70.0)
    
    # Conversion metrics
    conversion_rate: float = field(default=1.0)
    average_order_value: float = field(default=0.0)
    customer_lifetime_value: float = field(default=0.0)
    
    # Monetization efficiency
    cost_per_acquisition: float = field(default=0.0)
    return_on_ad_spend: float = field(default=0.0)
    profit_margin: float = field(default=20.0)


@dataclass
class BrandMetrics:
    """Brand development and partnership metrics"""
    brand_awareness_score: float = field(default=30.0)
    brand_perception_score: float = field(default=50.0)
    brand_consistency_score: float = field(default=50.0)
    
    # Partnership metrics
    brand_partnership_value: float = field(default=0.0)
    partnership_quality_score: float = field(default=50.0)
    brand_alignment_score: float = field(default=50.0)
    
    # Market positioning
    niche_authority_score: float = field(default=40.0)
    competitive_advantage_score: float = field(default=50.0)
    market_share_estimate: float = field(default=1.0)
    
    # Brand development
    personal_brand_strength: float = field(default=50.0)
    thought_leadership_score: float = field(default=30.0)
    industry_influence_score: float = field(default=25.0)


@dataclass
class BusinessGrowthMetrics:
    """Business growth and development metrics"""
    growth_stage: GrowthStage = field(default=GrowthStage.STARTUP)
    growth_velocity: float = field(default=5.0)
    scalability_score: float = field(default=50.0)
    
    # Financial growth
    revenue_growth_rate: float = field(default=0.0)
    profit_growth_rate: float = field(default=0.0)
    investment_efficiency: float = field(default=50.0)
    
    # Operational metrics
    content_production_efficiency: float = field(default=50.0)
    team_productivity_score: float = field(default=70.0)
    process_optimization_score: float = field(default=50.0)
    
    # Future potential
    market_expansion_potential: float = field(default=60.0)
    new_revenue_opportunities: List[str] = field(default_factory=list)
    risk_mitigation_score: float = field(default=50.0)


@dataclass
class BusinessHealthMetrics:
    """Overall business health indicators"""
    financial_stability_score: float = field(default=50.0)
    operational_efficiency_score: float = field(default=50.0)
    strategic_position_score: float = field(default=50.0)
    
    # Risk assessment
    business_risk_score: float = field(default=40.0)
    market_risk_score: float = field(default=50.0)
    operational_risk_score: float = field(default=30.0)
    
    # Sustainability metrics
    long_term_viability_score: float = field(default=60.0)
    innovation_capability_score: float = field(default=50.0)
    adaptation_agility_score: float = field(default=50.0)
    
    # Overall health
    business_health_score: float = field(default=50.0)
    success_probability: float = field(default=50.0)


@dataclass
class BusinessMetricsProfile:
    """Comprehensive business metrics profile"""
    # Business identification
    business_model: BusinessModel = field(default=BusinessModel.INFLUENCER)
    monetization_maturity: MonetizationMaturity = field(default=MonetizationMaturity.BEGINNER)
    
    # Core metrics
    audience_metrics: AudienceMetrics = field(default_factory=AudienceMetrics)
    content_metrics: ContentPerformanceMetrics = field(default_factory=ContentPerformanceMetrics)
    monetization_metrics: MonetizationMetrics = field(default_factory=MonetizationMetrics)
    brand_metrics: BrandMetrics = field(default_factory=BrandMetrics)
    growth_metrics: BusinessGrowthMetrics = field(default_factory=BusinessGrowthMetrics)
    health_metrics: BusinessHealthMetrics = field(default_factory=BusinessHealthMetrics)
    
    # Strategic insights
    key_performance_indicators: Dict[str, float] = field(default_factory=dict)
    competitive_benchmarks: Dict[str, float] = field(default_factory=dict)
    optimization_priorities: List[str] = field(default_factory=list)
    
    # Recommendations
    strategic_recommendations: List[str] = field(default_factory=list)
    monetization_opportunities: List[str] = field(default_factory=list)
    growth_strategies: List[str] = field(default_factory=list)
    
    # Overall scores
    business_performance_score: float = field(default=50.0)
    roi_score: float = field(default=40.0)
    market_position_score: float = field(default=50.0)


@dataclass
class BusinessMetricsAnalysis:
    """Business metrics analysis container"""
    profile: BusinessMetricsProfile = field(default_factory=BusinessMetricsProfile)
    
    # Performance indicators
    revenue_efficiency: float = field(default=40.0)
    audience_value: float = field(default=50.0)
    content_roi: float = field(default=45.0)
    brand_value: float = field(default=50.0)
    
    # Market insights
    industry_benchmarks: Dict[str, float] = field(default_factory=dict)
    competitive_position: str = field(default="average")
    market_opportunities: List[str] = field(default_factory=list)
    
    # Future projections
    projected_growth: Dict[str, float] = field(default_factory=dict)
    revenue_forecast: Dict[str, float] = field(default_factory=dict)
    risk_factors: List[str] = field(default_factory=list)
    
    # Metadata
    analysis_timestamp: datetime = field(default_factory=datetime.now)
    processing_time: float = field(default=0.0)
    confidence: float = field(default=0.0)


class BusinessMetricsAnalyzer(BaseAIModel):
    """
    Professional Business Metrics Analyzer
    
    Provides comprehensive business intelligence for:
    - Content creators and influencers
    - Creator economy businesses
    - Digital marketing agencies
    - Brand partnership teams
    - Investment analysts in creator economy
    """
    
    def __init__(self, config: Optional[ModelConfig] = None):
        """Initialize business metrics analyzer"""
        super().__init__(config or ModelConfig(
            name="business_metrics_analyzer",
            model_type=ModelType.BUSINESS_INTELLIGENCE,
            provider=ModelProvider.LOCAL
        ))
        
        self.performance_monitor = performance_monitor
        self.metrics_collector = metrics_collector
        
        # Industry benchmarks (simplified)
        self.industry_benchmarks = {
            'engagement_rate': {
                'instagram': {'micro': 3.5, 'macro': 1.8, 'mega': 1.2},
                'tiktok': {'micro': 9.0, 'macro': 5.5, 'mega': 4.0},
                'youtube': {'micro': 4.0, 'macro': 2.2, 'mega': 1.5}
            },
            'revenue_per_1k_followers': {
                'fashion': 15.0,
                'fitness': 12.0,
                'food': 10.0,
                'tech': 18.0,
                'lifestyle': 11.0,
                'business': 20.0
            },
            'conversion_rates': {
                'affiliate_marketing': 2.5,
                'course_sales': 1.5,
                'product_sales': 3.0,
                'sponsored_content': 0.8
            }
        }
        
        # Revenue stream potential mapping
        self.revenue_stream_potential = {
            BusinessModel.INFLUENCER: {
                RevenueStream.SPONSORED_CONTENT: 0.9,
                RevenueStream.AFFILIATE_MARKETING: 0.8,
                RevenueStream.BRAND_PARTNERSHIPS: 0.85,
                RevenueStream.MERCHANDISING: 0.6
            },
            BusinessModel.EDUCATOR: {
                RevenueStream.COURSE_SALES: 0.95,
                RevenueStream.CONSULTING: 0.8,
                RevenueStream.MEMBERSHIP: 0.75,
                RevenueStream.SPEAKING: 0.7
            },
            BusinessModel.ENTREPRENEUR: {
                RevenueStream.PRODUCT_SALES: 0.9,
                RevenueStream.CONSULTING: 0.85,
                RevenueStream.LICENSING: 0.7,
                RevenueStream.SPEAKING: 0.75
            }
        }
        
        logger.info("Business Metrics Analyzer initialized successfully")
    
    @monitor_performance
    async def analyze_business_metrics(
        self,
        business_data: Dict[str, Any],
        analysis_options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive business metrics analysis
        
        Args:
            business_data: Business performance data and metrics
            analysis_options: Analysis configuration options
            
        Returns:
            Dict containing complete business metrics analysis
            
        Raises:
            QualityCheckError: If analysis fails
            BusinessMetricsError: If business data is invalid
        """
        start_time = datetime.now()
        
        try:
            if not business_data:
                raise BusinessMetricsError("Empty business data provided")
            
            # Create metrics profile
            profile = BusinessMetricsProfile()
            
            # Classify business model
            await self._classify_business_model(business_data, profile)
            
            # Analyze core metrics
            await self._analyze_audience_metrics(business_data, profile)
            await self._analyze_content_performance(business_data, profile)
            await self._analyze_monetization_metrics(business_data, profile)
            await self._analyze_brand_metrics(business_data, profile)
            await self._analyze_growth_metrics(business_data, profile)
            await self._analyze_business_health(business_data, profile)
            
            # Calculate KPIs and benchmarks
            self._calculate_key_performance_indicators(profile)
            self._calculate_competitive_benchmarks(profile)
            
            # Generate strategic insights
            self._generate_strategic_recommendations(profile)
            self._identify_optimization_priorities(profile)
            
            # Create analysis container
            analysis = BusinessMetricsAnalysis(profile=profile)
            await self._calculate_performance_indicators(profile, analysis)
            await self._analyze_market_position(business_data, profile, analysis)
            await self._project_future_performance(profile, analysis)
            
            end_time = datetime.now()
            analysis.processing_time = (end_time - start_time).total_seconds()
            analysis.confidence = self._calculate_confidence(profile, business_data)
            
            # Prepare result
            result = {
                'business_performance_score': profile.business_performance_score,
                'confidence': analysis.confidence,
                'business_classification': {
                    'business_model': profile.business_model.value,
                    'monetization_maturity': profile.monetization_maturity.value,
                    'growth_stage': profile.growth_metrics.growth_stage.value
                },
                'audience_metrics': {
                    'total_followers': profile.audience_metrics.total_followers,
                    'engagement_rate': profile.audience_metrics.engagement_rate,
                    'audience_quality_score': profile.audience_metrics.audience_quality_score,
                    'authentic_engagement_rate': profile.audience_metrics.authentic_engagement_rate,
                    'follower_growth_rate': profile.audience_metrics.follower_growth_rate,
                    'retention_rate': profile.audience_metrics.retention_rate,
                    'audience_loyalty_score': profile.audience_metrics.audience_loyalty_score
                },
                'content_performance': {
                    'average_views': profile.content_metrics.average_views,
                    'average_engagement': profile.content_metrics.average_engagement,
                    'content_consistency_score': profile.content_metrics.content_consistency_score,
                    'viral_content_percentage': profile.content_metrics.viral_content_percentage,
                    'evergreen_content_percentage': profile.content_metrics.evergreen_content_percentage,
                    'view_growth_trend': profile.content_metrics.view_growth_trend,
                    'platform_performance_scores': profile.content_metrics.platform_performance_scores
                },
                'monetization_analysis': {
                    'total_revenue': profile.monetization_metrics.total_revenue,
                    'revenue_per_follower': profile.monetization_metrics.revenue_per_follower,
                    'revenue_per_post': profile.monetization_metrics.revenue_per_post,
                    'revenue_streams': {stream.value: amount for stream, amount in profile.monetization_metrics.revenue_streams.items()},
                    'revenue_diversification_score': profile.monetization_metrics.revenue_diversification_score,
                    'conversion_rate': profile.monetization_metrics.conversion_rate,
                    'customer_lifetime_value': profile.monetization_metrics.customer_lifetime_value,
                    'profit_margin': profile.monetization_metrics.profit_margin
                },
                'brand_analysis': {
                    'brand_awareness_score': profile.brand_metrics.brand_awareness_score,
                    'brand_perception_score': profile.brand_metrics.brand_perception_score,
                    'brand_consistency_score': profile.brand_metrics.brand_consistency_score,
                    'niche_authority_score': profile.brand_metrics.niche_authority_score,
                    'competitive_advantage_score': profile.brand_metrics.competitive_advantage_score,
                    'personal_brand_strength': profile.brand_metrics.personal_brand_strength,
                    'thought_leadership_score': profile.brand_metrics.thought_leadership_score
                },
                'growth_analysis': {
                    'growth_velocity': profile.growth_metrics.growth_velocity,
                    'scalability_score': profile.growth_metrics.scalability_score,
                    'revenue_growth_rate': profile.growth_metrics.revenue_growth_rate,
                    'market_expansion_potential': profile.growth_metrics.market_expansion_potential,
                    'new_revenue_opportunities': profile.growth_metrics.new_revenue_opportunities
                },
                'business_health': {
                    'financial_stability_score': profile.health_metrics.financial_stability_score,
                    'operational_efficiency_score': profile.health_metrics.operational_efficiency_score,
                    'strategic_position_score': profile.health_metrics.strategic_position_score,
                    'business_risk_score': profile.health_metrics.business_risk_score,
                    'long_term_viability_score': profile.health_metrics.long_term_viability_score,
                    'business_health_score': profile.health_metrics.business_health_score
                },
                'key_performance_indicators': profile.key_performance_indicators,
                'competitive_benchmarks': profile.competitive_benchmarks,
                'performance_indicators': {
                    'revenue_efficiency': analysis.revenue_efficiency,
                    'audience_value': analysis.audience_value,
                    'content_roi': analysis.content_roi,
                    'brand_value': analysis.brand_value
                },
                'market_insights': {
                    'competitive_position': analysis.competitive_position,
                    'industry_benchmarks': analysis.industry_benchmarks,
                    'market_opportunities': analysis.market_opportunities
                },
                'strategic_insights': {
                    'optimization_priorities': profile.optimization_priorities,
                    'strategic_recommendations': profile.strategic_recommendations,
                    'monetization_opportunities': profile.monetization_opportunities,
                    'growth_strategies': profile.growth_strategies
                },
                'future_projections': {
                    'projected_growth': analysis.projected_growth,
                    'revenue_forecast': analysis.revenue_forecast,
                    'risk_factors': analysis.risk_factors
                },
                'overall_scores': {
                    'roi_score': profile.roi_score,
                    'market_position_score': profile.market_position_score
                }
            }
            
            # Log metrics
            self.metrics_collector.track_business_metric(
                metric_name="business_metrics_analysis_completed",
                value=1,
                metadata={
                    'performance_score': profile.business_performance_score,
                    'business_model': profile.business_model.value,
                    'revenue': profile.monetization_metrics.total_revenue,
                    'processing_time': analysis.processing_time
                }
            )
            
            logger.info(f"Business metrics analysis completed: {profile.business_performance_score:.2f}/100")
            return result
            
        except Exception as e:
            logger.error(f"Business metrics analysis failed: {str(e)}")
            self.metrics_collector.capture_errors("business_metrics_analysis_error", str(e))
            raise QualityCheckError(f"Business metrics analysis failed: {str(e)}") from e
    
    async def _classify_business_model(self, business_data: Dict[str, Any], profile: BusinessMetricsProfile):
        """Classify business model and monetization maturity"""



        try:
            content_type = business_data.get('content_type', 'general').lower()
            revenue_streams = business_data.get('revenue_streams', [])
            follower_count = business_data.get('followers', 0)
            
            # Business model classification
            model_indicators = {
                BusinessModel.INFLUENCER: ['sponsored', 'brand', 'partnership', 'affiliate'],
                BusinessModel.EDUCATOR: ['course', 'tutorial', 'education', 'teaching'],
                BusinessModel.ENTERTAINER: ['entertainment', 'comedy', 'music', 'performance'],
                BusinessModel.CONSULTANT: ['consulting', 'advice', 'expertise', 'service'],
                BusinessModel.ENTREPRENEUR: ['business', 'startup', 'product', 'company'],
                BusinessModel.ARTIST: ['art', 'creative', 'design', 'artistic']
            }
            
            model_scores = {}
            for model, indicators in model_indicators.items():
                score = sum(1 for indicator in indicators 
                           if indicator in content_type or 
                           any(indicator in stream.lower() for stream in revenue_streams))
                model_scores[model] = score
            
            if model_scores and max(model_scores.values()) > 0:
                profile.business_model = max(model_scores, key=model_scores.get)
            
            # Monetization maturity classification
            revenue_diversity = len(set(revenue_streams))
            total_revenue = business_data.get('total_revenue', 0)
            
            if revenue_diversity >= 4 and total_revenue > 100000:
                profile.monetization_maturity = MonetizationMaturity.EXPERT
            elif revenue_diversity >= 3 and total_revenue > 50000:
                profile.monetization_maturity = MonetizationMaturity.ADVANCED
            elif revenue_diversity >= 2 and total_revenue > 10000:
                profile.monetization_maturity = MonetizationMaturity.INTERMEDIATE
            else:
                profile.monetization_maturity = MonetizationMaturity.BEGINNER
            
            # Growth stage classification
            if follower_count >= 1000000:
                profile.growth_metrics.growth_stage = GrowthStage.ENTERPRISE
            elif follower_count >= 100000:
                profile.growth_metrics.growth_stage = GrowthStage.ESTABLISHED
            elif follower_count >= 10000:
                profile.growth_metrics.growth_stage = GrowthStage.EMERGING
            else:
                profile.growth_metrics.growth_stage = GrowthStage.STARTUP
            
        except Exception as e:
            logger.warning(f"Business model classification failed: {str(e)}")
    
    async def _analyze_audience_metrics(self, business_data: Dict[str, Any], profile: BusinessMetricsProfile):
        """Analyze audience-related business metrics"""



        try:
            audience_data = business_data.get('audience', {})
            engagement_data = business_data.get('engagement', {})
            
            # Basic audience metrics
            profile.audience_metrics.total_followers = business_data.get('followers', 0)
            profile.audience_metrics.engagement_rate = engagement_data.get('rate', 0.0)
            
            # Audience quality assessment
            quality_factors = []
            
            # Demographic alignment
            target_demo = audience_data.get('target_demographic_percentage', 50.0)
            profile.audience_metrics.target_demographic_percentage = target_demo
            quality_factors.append(target_demo)
            
            # High-value demographics
            high_value_demo = audience_data.get('high_value_percentage', 30.0)
            profile.audience_metrics.high_value_demographic_percentage = high_value_demo
            quality_factors.append(high_value_demo * 1.5)  # Weight higher
            
            # Geographic distribution
            geo_score = audience_data.get('geographic_distribution_score', 50.0)
            profile.audience_metrics.geographic_distribution_score = geo_score
            quality_factors.append(geo_score)
            
            profile.audience_metrics.audience_quality_score = np.mean(quality_factors)
            
            # Engagement quality
            authentic_engagement = engagement_data.get('authentic_rate', 0.0)
            profile.audience_metrics.authentic_engagement_rate = authentic_engagement
            
            sentiment_score = engagement_data.get('sentiment_score', 50.0)
            profile.audience_metrics.comment_sentiment_score = sentiment_score
            
            share_like_ratio = engagement_data.get('share_to_like_ratio', 0.1)
            profile.audience_metrics.share_to_like_ratio = share_like_ratio
            
            # Growth and retention
            growth_rate = audience_data.get('growth_rate', 0.0)
            profile.audience_metrics.follower_growth_rate = growth_rate
            
            retention_rate = audience_data.get('retention_rate', 80.0)
            profile.audience_metrics.retention_rate = retention_rate
            
            # Audience loyalty calculation
            loyalty_factors = [
                retention_rate,
                sentiment_score,
                authentic_engagement * 100,  # Convert to percentage
                min(100, share_like_ratio * 1000)  # Normalize
            ]
            
            profile.audience_metrics.audience_loyalty_score = np.mean(loyalty_factors)
            
        except Exception as e:
            logger.warning(f"Audience metrics analysis failed: {str(e)}")
    
    async def _analyze_content_performance(self, business_data: Dict[str, Any], profile: BusinessMetricsProfile):
        """Analyze content performance metrics"""



        try:
            content_data = business_data.get('content_performance', {})
            
            # Basic performance metrics
            profile.content_metrics.average_views = content_data.get('average_views', 0.0)
            profile.content_metrics.average_engagement = content_data.get('average_engagement', 0.0)
            
            # Content consistency
            consistency_score = content_data.get('consistency_score', 50.0)
            profile.content_metrics.content_consistency_score = consistency_score
            
            # Content value analysis
            viral_percentage = content_data.get('viral_content_percentage', 5.0)
            profile.content_metrics.viral_content_percentage = viral_percentage
            
            evergreen_percentage = content_data.get('evergreen_percentage', 20.0)
            profile.content_metrics.evergreen_content_percentage = evergreen_percentage
            
            conversion_percentage = content_data.get('conversion_percentage', 10.0)
            profile.content_metrics.conversion_content_percentage = conversion_percentage
            
            # Performance trends
            view_trend = content_data.get('view_growth_trend', 0.0)
            profile.content_metrics.view_growth_trend = view_trend
            
            engagement_trend = content_data.get('engagement_growth_trend', 0.0)
            profile.content_metrics.engagement_growth_trend = engagement_trend
            
            quality_trend = content_data.get('quality_trend', 0.0)
            profile.content_metrics.content_quality_trend = quality_trend
            
            # Platform performance
            platform_data = content_data.get('platforms', {})
            platform_scores = {}
            
            for platform, data in platform_data.items():
                performance_factors = [
                    data.get('engagement_rate', 0) * 100,
                    data.get('reach_rate', 0) * 100,
                    data.get('conversion_rate', 0) * 100,
                    data.get('growth_rate', 0) * 100
                ]
                platform_scores[platform] = np.mean([f for f in performance_factors if f > 0])
            
            profile.content_metrics.platform_performance_scores = platform_scores
            
            # Cross-platform synergy
            if len(platform_scores) > 1:
                variance = np.var(list(platform_scores.values()))
                # Lower variance indicates better synergy
                synergy_score = max(0, 100 - variance)
                profile.content_metrics.cross_platform_synergy = synergy_score
            
        except Exception as e:
            logger.warning(f"Content performance analysis failed: {str(e)}")
    
    async def _analyze_monetization_metrics(self, business_data: Dict[str, Any], profile: BusinessMetricsProfile):
        """Analyze monetization and revenue metrics"""



        try:
            revenue_data = business_data.get('revenue', {})
            conversion_data = business_data.get('conversions', {})
            
            # Basic revenue metrics
            total_revenue = revenue_data.get('total', 0.0)
            profile.monetization_metrics.total_revenue = total_revenue
            
            followers = profile.audience_metrics.total_followers
            if followers > 0:
                profile.monetization_metrics.revenue_per_follower = total_revenue / followers
            
            posts_count = business_data.get('posts_count', 1)
            profile.monetization_metrics.revenue_per_post = total_revenue / posts_count
            
            # Revenue streams analysis
            streams_data = revenue_data.get('streams', {})
            revenue_streams = {}
            
            for stream_name, amount in streams_data.items():
                try:
                    stream_enum = RevenueStream(stream_name.lower())
                    revenue_streams[stream_enum] = amount
                except ValueError:
                    # Handle unknown revenue streams
                    logger.warning(f"Unknown revenue stream: {stream_name}")
            
            profile.monetization_metrics.revenue_streams = revenue_streams
            
            # Revenue diversification
            active_streams = len([s for s in revenue_streams.values() if s > 0])
            max_streams = len(RevenueStream)
            diversification_score = (active_streams / max_streams) * 100
            profile.monetization_metrics.revenue_diversification_score = diversification_score
            
            # Primary revenue dependency
            if revenue_streams:
                max_revenue = max(revenue_streams.values())
                dependency = (max_revenue / total_revenue) * 100 if total_revenue > 0 else 100
                profile.monetization_metrics.primary_revenue_dependency = dependency
            
            # Conversion metrics
            conversion_rate = conversion_data.get('rate', 1.0)
            profile.monetization_metrics.conversion_rate = conversion_rate
            
            avg_order_value = conversion_data.get('average_order_value', 0.0)
            profile.monetization_metrics.average_order_value = avg_order_value
            
            customer_ltv = conversion_data.get('lifetime_value', 0.0)
            profile.monetization_metrics.customer_lifetime_value = customer_ltv
            
            # Efficiency metrics
            cost_per_acquisition = conversion_data.get('cost_per_acquisition', 0.0)
            profile.monetization_metrics.cost_per_acquisition = cost_per_acquisition
            
            roas = conversion_data.get('return_on_ad_spend', 0.0)
            profile.monetization_metrics.return_on_ad_spend = roas
            
            profit_margin = revenue_data.get('profit_margin', 20.0)
            profile.monetization_metrics.profit_margin = profit_margin
            
        except Exception as e:
            logger.warning(f"Monetization metrics analysis failed: {str(e)}")
    
    async def _analyze_brand_metrics(self, business_data: Dict[str, Any], profile: BusinessMetricsProfile):
        """Analyze brand development and partnership metrics"""



        try:
            brand_data = business_data.get('brand', {})
            partnership_data = business_data.get('partnerships', {})
            
            # Brand awareness and perception
            awareness_score = brand_data.get('awareness_score', 30.0)
            profile.brand_metrics.brand_awareness_score = awareness_score
            
            perception_score = brand_data.get('perception_score', 50.0)
            profile.brand_metrics.brand_perception_score = perception_score
            
            consistency_score = brand_data.get('consistency_score', 50.0)
            profile.brand_metrics.brand_consistency_score = consistency_score
            
            # Partnership metrics
            partnership_value = partnership_data.get('total_value', 0.0)
            profile.brand_metrics.brand_partnership_value = partnership_value
            
            partnership_quality = partnership_data.get('quality_score', 50.0)
            profile.brand_metrics.partnership_quality_score = partnership_quality
            
            brand_alignment = partnership_data.get('alignment_score', 50.0)
            profile.brand_metrics.brand_alignment_score = brand_alignment
            
            # Market positioning
            niche_authority = brand_data.get('niche_authority_score', 40.0)
            profile.brand_metrics.niche_authority_score = niche_authority
            
            competitive_advantage = brand_data.get('competitive_advantage_score', 50.0)
            profile.brand_metrics.competitive_advantage_score = competitive_advantage
            
            market_share = brand_data.get('market_share_estimate', 1.0)
            profile.brand_metrics.market_share_estimate = market_share
            
            # Brand development
            personal_brand_strength = brand_data.get('personal_brand_strength', 50.0)
            profile.brand_metrics.personal_brand_strength = personal_brand_strength
            
            thought_leadership = brand_data.get('thought_leadership_score', 30.0)
            profile.brand_metrics.thought_leadership_score = thought_leadership
            
            industry_influence = brand_data.get('industry_influence_score', 25.0)
            profile.brand_metrics.industry_influence_score = industry_influence
            
        except Exception as e:
            logger.warning(f"Brand metrics analysis failed: {str(e)}")
    
    async def _analyze_growth_metrics(self, business_data: Dict[str, Any], profile: BusinessMetricsProfile):
        """Analyze business growth and development metrics"""



        try:
            growth_data = business_data.get('growth', {})
            
            # Growth velocity (follower growth rate as proxy)
            velocity = growth_data.get('velocity', 5.0)
            profile.growth_metrics.growth_velocity = velocity
            
            # Scalability assessment
            scalability_factors = []
            
            # Content production scalability
            content_efficiency = growth_data.get('content_production_efficiency', 50.0)
            profile.growth_metrics.content_production_efficiency = content_efficiency
            scalability_factors.append(content_efficiency)
            
            # Team productivity
            team_productivity = growth_data.get('team_productivity_score', 70.0)
            profile.growth_metrics.team_productivity_score = team_productivity
            scalability_factors.append(team_productivity)
            
            # Process optimization
            process_optimization = growth_data.get('process_optimization_score', 50.0)
            profile.growth_metrics.process_optimization_score = process_optimization
            scalability_factors.append(process_optimization)
            
            profile.growth_metrics.scalability_score = np.mean(scalability_factors)
            
            # Financial growth
            revenue_growth = growth_data.get('revenue_growth_rate', 0.0)
            profile.growth_metrics.revenue_growth_rate = revenue_growth
            
            profit_growth = growth_data.get('profit_growth_rate', 0.0)
            profile.growth_metrics.profit_growth_rate = profit_growth
            
            investment_efficiency = growth_data.get('investment_efficiency', 50.0)
            profile.growth_metrics.investment_efficiency = investment_efficiency
            
            # Future potential
            market_expansion = growth_data.get('market_expansion_potential', 60.0)
            profile.growth_metrics.market_expansion_potential = market_expansion
            
            # New revenue opportunities
            opportunities = growth_data.get('new_revenue_opportunities', [])
            profile.growth_metrics.new_revenue_opportunities = opportunities
            
            risk_mitigation = growth_data.get('risk_mitigation_score', 50.0)
            profile.growth_metrics.risk_mitigation_score = risk_mitigation
            
        except Exception as e:
            logger.warning(f"Growth metrics analysis failed: {str(e)}")
    
    async def _analyze_business_health(self, business_data: Dict[str, Any], profile: BusinessMetricsProfile):
        """Analyze overall business health indicators"""



        try:
            # Financial stability
            financial_factors = [
                profile.monetization_metrics.profit_margin,
                profile.monetization_metrics.revenue_diversification_score,
                min(100, profile.monetization_metrics.total_revenue / 1000),  # Revenue scale
                profile.growth_metrics.revenue_growth_rate * 10  # Growth importance
            ]
            
            profile.health_metrics.financial_stability_score = np.mean([f for f in financial_factors if f >= 0])
            
            # Operational efficiency
            operational_factors = [
                profile.growth_metrics.content_production_efficiency,
                profile.growth_metrics.team_productivity_score,
                profile.growth_metrics.process_optimization_score,
                profile.content_metrics.content_consistency_score
            ]
            
            profile.health_metrics.operational_efficiency_score = np.mean(operational_factors)
            
            # Strategic position
            strategic_factors = [
                profile.brand_metrics.competitive_advantage_score,
                profile.brand_metrics.niche_authority_score,
                profile.audience_metrics.audience_quality_score,
                profile.growth_metrics.scalability_score
            ]
            
            profile.health_metrics.strategic_position_score = np.mean(strategic_factors)
            
            # Risk assessment
            business_risks = []
            
            # High dependency on single revenue stream
            if profile.monetization_metrics.primary_revenue_dependency > 80:
                business_risks.append("high_revenue_concentration")
            
            # Low audience engagement
            if profile.audience_metrics.engagement_rate < 2.0:
                business_risks.append("low_engagement")
            
            # Declining growth
            if profile.growth_metrics.revenue_growth_rate < 0:
                business_risks.append("negative_growth")
            
            risk_score = len(business_risks) * 20
            profile.health_metrics.business_risk_score = min(100, risk_score)
            
            # Market and operational risks (simplified)
            profile.health_metrics.market_risk_score = 50.0  # Market volatility
            profile.health_metrics.operational_risk_score = 30.0  # Operations stability
            
            # Sustainability metrics
            sustainability_factors = [
                profile.brand_metrics.personal_brand_strength,
                profile.audience_metrics.audience_loyalty_score,
                profile.monetization_metrics.revenue_diversification_score,
                profile.growth_metrics.scalability_score
            ]
            
            profile.health_metrics.long_term_viability_score = np.mean(sustainability_factors)
            
            # Innovation and adaptation
            innovation_factors = [
                profile.content_metrics.viral_content_percentage * 2,  # Innovation indicator
                profile.growth_metrics.market_expansion_potential,
                profile.brand_metrics.thought_leadership_score,
                profile.growth_metrics.investment_efficiency
            ]
            
            profile.health_metrics.innovation_capability_score = np.mean(innovation_factors)
            
            adaptation_factors = [
                profile.content_metrics.content_quality_trend + 50,  # Normalize
                profile.audience_metrics.follower_growth_rate * 10 + 50,  # Normalize
                profile.growth_metrics.process_optimization_score
            ]
            
            profile.health_metrics.adaptation_agility_score = np.mean([f for f in adaptation_factors if f >= 0])
            
            # Overall business health
            health_components = [
                profile.health_metrics.financial_stability_score,
                profile.health_metrics.operational_efficiency_score,
                profile.health_metrics.strategic_position_score,
                profile.health_metrics.long_term_viability_score
            ]
            
            profile.health_metrics.business_health_score = np.mean(health_components)
            
            # Success probability
            success_factors = [
                profile.health_metrics.business_health_score,
                profile.growth_metrics.growth_velocity * 5 + 50,  # Normalize
                profile.brand_metrics.competitive_advantage_score,
                profile.audience_metrics.audience_quality_score
            ]
            
            profile.health_metrics.success_probability = np.mean(success_factors)
            
        except Exception as e:
            logger.warning(f"Business health analysis failed: {str(e)}")
    
    def _calculate_key_performance_indicators(self, profile: BusinessMetricsProfile):
        """Calculate key performance indicators"""



        try:
            kpis = {}
            
            # Revenue KPIs
            kpis['revenue_per_follower'] = profile.monetization_metrics.revenue_per_follower
            kpis['revenue_growth_rate'] = profile.growth_metrics.revenue_growth_rate
            kpis['profit_margin'] = profile.monetization_metrics.profit_margin
            
            # Audience KPIs
            kpis['engagement_rate'] = profile.audience_metrics.engagement_rate
            kpis['follower_growth_rate'] = profile.audience_metrics.follower_growth_rate
            kpis['audience_quality_score'] = profile.audience_metrics.audience_quality_score
            
            # Content KPIs
            kpis['content_consistency_score'] = profile.content_metrics.content_consistency_score
            kpis['viral_content_percentage'] = profile.content_metrics.viral_content_percentage
            kpis['content_roi'] = profile.content_metrics.average_engagement / max(1, profile.content_metrics.average_views) * 100
            
            # Business KPIs
            kpis['revenue_diversification'] = profile.monetization_metrics.revenue_diversification_score
            kpis['brand_strength'] = profile.brand_metrics.personal_brand_strength
            kpis['scalability_score'] = profile.growth_metrics.scalability_score
            
            # Overall performance KPIs
            performance_components = [
                profile.audience_metrics.audience_quality_score * 0.25,
                profile.content_metrics.content_consistency_score * 0.25,
                profile.monetization_metrics.revenue_diversification_score * 0.25,
                profile.brand_metrics.personal_brand_strength * 0.25
            ]
            
            kpis['overall_performance'] = sum(performance_components)
            profile.business_performance_score = kpis['overall_performance']
            
            # ROI calculation
            roi_components = [
                profile.monetization_metrics.profit_margin,
                profile.monetization_metrics.return_on_ad_spend,
                profile.growth_metrics.investment_efficiency
            ]
            
            profile.roi_score = np.mean([c for c in roi_components if c > 0])
            
            # Market position
            position_components = [
                profile.brand_metrics.competitive_advantage_score,
                profile.brand_metrics.niche_authority_score,
                profile.brand_metrics.market_share_estimate * 10,  # Scale up
                profile.audience_metrics.audience_quality_score
            ]
            
            profile.market_position_score = np.mean(position_components)
            
            profile.key_performance_indicators = kpis
            
        except Exception as e:
            logger.warning(f"KPI calculation failed: {str(e)}")
    
    def _calculate_competitive_benchmarks(self, profile: BusinessMetricsProfile):
        """Calculate competitive benchmarks"""



        try:
            benchmarks = {}
            
            # Get industry benchmarks based on business model
            model = profile.business_model.value
            
            # Engagement rate benchmarks
            user_engagement = profile.audience_metrics.engagement_rate
            
            # Simplified benchmark comparison
            if user_engagement >= 5.0:
                benchmarks['engagement_performance'] = 'excellent'
            elif user_engagement >= 3.0:
                benchmarks['engagement_performance'] = 'good'
            elif user_engagement >= 1.5:
                benchmarks['engagement_performance'] = 'average'
            else:
                benchmarks['engagement_performance'] = 'below_average'
            
            # Revenue benchmarks
            revenue_per_follower = profile.monetization_metrics.revenue_per_follower
            
            if revenue_per_follower >= 0.02:  # $0.02 per follower
                benchmarks['monetization_performance'] = 'excellent'
            elif revenue_per_follower >= 0.01:
                benchmarks['monetization_performance'] = 'good'
            elif revenue_per_follower >= 0.005:
                benchmarks['monetization_performance'] = 'average'
            else:
                benchmarks['monetization_performance'] = 'below_average'
            
            # Growth benchmarks
            growth_rate = profile.audience_metrics.follower_growth_rate
            
            if growth_rate >= 20:  # 20% monthly growth
                benchmarks['growth_performance'] = 'excellent'
            elif growth_rate >= 10:
                benchmarks['growth_performance'] = 'good'
            elif growth_rate >= 5:
                benchmarks['growth_performance'] = 'average'
            else:
                benchmarks['growth_performance'] = 'below_average'
            
            # Content performance benchmarks
            consistency = profile.content_metrics.content_consistency_score
            
            if consistency >= 90:
                benchmarks['content_performance'] = 'excellent'
            elif consistency >= 75:
                benchmarks['content_performance'] = 'good'
            elif consistency >= 60:
                benchmarks['content_performance'] = 'average'
            else:
                benchmarks['content_performance'] = 'below_average'
            
            profile.competitive_benchmarks = benchmarks
            
        except Exception as e:
            logger.warning(f"Competitive benchmarks calculation failed: {str(e)}")
    
    def _generate_strategic_recommendations(self, profile: BusinessMetricsProfile):
        """Generate strategic recommendations"""
        recommendations = []
        monetization_opportunities = []
        growth_strategies = []
        
        # Revenue diversification recommendations
        if profile.monetization_metrics.revenue_diversification_score < 50:
            recommendations.append("Diversify revenue streams to reduce dependency risks")
            monetization_opportunities.extend([
                "Explore affiliate marketing opportunities",
                "Consider launching digital products or courses",
                "Investigate brand partnership possibilities"
            ])
        
        # Audience quality recommendations
        if profile.audience_metrics.audience_quality_score < 70:
            recommendations.append("Focus on improving audience quality and engagement")
            growth_strategies.extend([
                "Implement targeted content strategy for ideal audience",
                "Engage more actively with high-value followers",
                "Use audience insights to refine content approach"
            ])
        
        # Content optimization recommendations
        if profile.content_metrics.content_consistency_score < 75:
            recommendations.append("Improve content consistency and quality")
            growth_strategies.extend([
                "Develop content calendar and production schedule",
                "Invest in content quality improvement tools and training",
                "Analyze top-performing content for replication strategies"
            ])
        
        # Brand development recommendations
        if profile.brand_metrics.personal_brand_strength < 60:
            recommendations.append("Strengthen personal brand development")
            growth_strategies.extend([
                "Define clear brand values and messaging",
                "Increase thought leadership content production",
                "Build strategic partnerships for brand enhancement"
            ])
        
        # Monetization maturity recommendations
        if profile.monetization_maturity == MonetizationMaturity.BEGINNER:
            monetization_opportunities.extend([
                "Start with sponsored content and affiliate marketing",
                "Build email list for direct marketing",
                "Create simple digital products or services"
            ])
        elif profile.monetization_maturity == MonetizationMaturity.INTERMEDIATE:
            monetization_opportunities.extend([
                "Launch premium content or membership programs",
                "Develop signature courses or coaching programs",
                "Explore speaking and consulting opportunities"
            ])
        
        # Scalability recommendations
        if profile.growth_metrics.scalability_score < 60:
            recommendations.append("Improve business scalability and operations")
            growth_strategies.extend([
                "Automate repetitive tasks and processes",
                "Build team or outsource content production",
                "Develop systematic approach to content creation"
            ])
        
        # Platform optimization
        platform_scores = profile.content_metrics.platform_performance_scores
        if platform_scores:
            underperforming_platforms = [p for p, s in platform_scores.items() if s < 50]
            if underperforming_platforms:
                recommendations.append(f"Optimize performance on {', '.join(underperforming_platforms)}")
        
        profile.strategic_recommendations = recommendations
        profile.monetization_opportunities = monetization_opportunities
        profile.growth_strategies = growth_strategies
    
    def _identify_optimization_priorities(self, profile: BusinessMetricsProfile):
        """Identify optimization priorities"""
        priorities = []
        
        # Score all areas and identify lowest-performing
        areas = {
            'audience_quality': profile.audience_metrics.audience_quality_score,
            'content_consistency': profile.content_metrics.content_consistency_score,
            'revenue_diversification': profile.monetization_metrics.revenue_diversification_score,
            'brand_development': profile.brand_metrics.personal_brand_strength,
            'business_scalability': profile.growth_metrics.scalability_score,
            'operational_efficiency': profile.health_metrics.operational_efficiency_score
        }
        
        # Sort by score (ascending) to get priorities
        sorted_areas = sorted(areas.items(), key=lambda x: x[1])
        
        # Take bottom 3 as priority areas
        for area, score in sorted_areas[:3]:
            if score < 70:  # Only include if below threshold
                priorities.append(area)
        
        profile.optimization_priorities = priorities
    
    async def _calculate_performance_indicators(self, profile: BusinessMetricsProfile, analysis: BusinessMetricsAnalysis):
        """Calculate performance indicators"""



        try:
            # Revenue efficiency
            revenue_factors = [
                profile.monetization_metrics.profit_margin,
                profile.monetization_metrics.revenue_per_follower * 10000,  # Scale up
                profile.monetization_metrics.conversion_rate * 50,  # Scale up
                profile.monetization_metrics.revenue_diversification_score
            ]
            
            analysis.revenue_efficiency = np.mean([f for f in revenue_factors if f > 0])
            
            # Audience value
            audience_factors = [
                profile.audience_metrics.audience_quality_score,
                profile.audience_metrics.audience_loyalty_score,
                profile.audience_metrics.authentic_engagement_rate * 100,
                profile.audience_metrics.retention_rate
            ]
            
            analysis.audience_value = np.mean(audience_factors)
            
            # Content ROI
            content_factors = [
                profile.content_metrics.content_consistency_score,
                profile.content_metrics.viral_content_percentage * 2,  # Weight viral content
                profile.content_metrics.evergreen_content_percentage,
                profile.content_metrics.conversion_content_percentage * 3  # Weight conversion content
            ]
            
            analysis.content_roi = np.mean(content_factors)
            
            # Brand value
            brand_factors = [
                profile.brand_metrics.personal_brand_strength,
                profile.brand_metrics.niche_authority_score,
                profile.brand_metrics.thought_leadership_score,
                profile.brand_metrics.competitive_advantage_score
            ]
            
            analysis.brand_value = np.mean(brand_factors)
            
        except Exception as e:
            logger.warning(f"Performance indicators calculation failed: {str(e)}")
    
    async def _analyze_market_position(self, business_data: Dict[str, Any], profile: BusinessMetricsProfile, analysis: BusinessMetricsAnalysis):
        """Analyze market position and opportunities"""



        try:
            # Competitive position assessment
            performance_score = profile.business_performance_score
            
            if performance_score >= 80:
                analysis.competitive_position = "leader"
            elif performance_score >= 65:
                analysis.competitive_position = "strong"
            elif performance_score >= 50:
                analysis.competitive_position = "average"
            elif performance_score >= 35:
                analysis.competitive_position = "weak"
            else:
                analysis.competitive_position = "poor"
            
            # Industry benchmarks
            category = business_data.get('category', 'general')
            
            # Simplified industry benchmarks
            industry_benchmarks = {
                'average_engagement_rate': self.industry_benchmarks.get('engagement_rate', {}).get('instagram', {}).get('micro', 3.5),
                'average_revenue_per_1k': self.industry_benchmarks.get('revenue_per_1k_followers', {}).get(category, 12.0),
                'average_conversion_rate': self.industry_benchmarks.get('conversion_rates', {}).get('affiliate_marketing', 2.5)
            }
            
            analysis.industry_benchmarks = industry_benchmarks
            
            # Market opportunities
            opportunities = []
            
            # Based on growth stage
            if profile.growth_metrics.growth_stage == GrowthStage.STARTUP:
                opportunities.extend([
                    "Focus on niche audience building",
                    "Develop signature content style",
                    "Build foundational revenue streams"
                ])
            elif profile.growth_metrics.growth_stage == GrowthStage.EMERGING:
                opportunities.extend([
                    "Scale successful content formats",
                    "Diversify revenue streams",
                    "Build strategic partnerships"
                ])
            elif profile.growth_metrics.growth_stage == GrowthStage.ESTABLISHED:
                opportunities.extend([
                    "Launch premium offerings",
                    "Expand to new platforms",
                    "Develop team and systems"
                ])
            
            # Based on business model
            model_opportunities = self.revenue_stream_potential.get(profile.business_model, {})
            for stream, potential in model_opportunities.items():
                if potential > 0.7 and stream not in profile.monetization_metrics.revenue_streams:
                    opportunities.append(f"Explore {stream.value} opportunities")
            
            analysis.market_opportunities = opportunities
            
        except Exception as e:
            logger.warning(f"Market position analysis failed: {str(e)}")
    
    async def _project_future_performance(self, profile: BusinessMetricsProfile, analysis: BusinessMetricsAnalysis):
        """Project future performance and risks"""



        try:
            # Growth projections (simplified linear projections)
            current_growth = profile.growth_metrics.growth_velocity
            
            projected_growth = {
                '3_months': current_growth * 3,
                '6_months': current_growth * 6 * 0.9,  # Slight deceleration
                '12_months': current_growth * 12 * 0.8  # More deceleration
            }
            
            analysis.projected_growth = projected_growth
            
            # Revenue forecast
            current_revenue = profile.monetization_metrics.total_revenue
            revenue_growth_rate = profile.growth_metrics.revenue_growth_rate / 100
            
            revenue_forecast = {
                '3_months': current_revenue * (1 + revenue_growth_rate * 3),
                '6_months': current_revenue * (1 + revenue_growth_rate * 6),
                '12_months': current_revenue * (1 + revenue_growth_rate * 12)
            }
            
            analysis.revenue_forecast = revenue_forecast
            
            # Risk factors
            risk_factors = []
            
            # High revenue concentration risk
            if profile.monetization_metrics.primary_revenue_dependency > 70:
                risk_factors.append("High dependency on single revenue stream")
            
            # Low audience engagement risk
            if profile.audience_metrics.engagement_rate < 2.0:
                risk_factors.append("Low audience engagement threatens reach")
            
            # Content consistency risk
            if profile.content_metrics.content_consistency_score < 60:
                risk_factors.append("Inconsistent content may impact growth")
            
            # Market saturation risk
            if profile.brand_metrics.competitive_advantage_score < 50:
                risk_factors.append("Limited differentiation in competitive market")
            
            # Platform dependency risk
            platform_scores = profile.content_metrics.platform_performance_scores
            if len(platform_scores) <= 1:
                risk_factors.append("Over-dependence on single platform")
            
            # Financial sustainability risk
            if profile.monetization_metrics.profit_margin < 15:
                risk_factors.append("Low profit margins threaten sustainability")
            
            analysis.risk_factors = risk_factors
            
        except Exception as e:
            logger.warning(f"Future performance projection failed: {str(e)}")
    
    def _calculate_confidence(self, profile: BusinessMetricsProfile, business_data: Dict[str, Any]) -> float:
        """Calculate analysis confidence score"""
        confidence = 0.8  # Base confidence
        
        # Adjust based on data completeness
        data_completeness_factors = [
            'followers' in business_data,
            'revenue' in business_data,
            'engagement' in business_data,
            'content_performance' in business_data,
            'audience' in business_data
        ]
        
        completeness_score = sum(data_completeness_factors) / len(data_completeness_factors)
        confidence += (completeness_score - 0.5) * 0.2
        
        # Adjust based on revenue data quality
        if profile.monetization_metrics.total_revenue > 0:
            confidence += 0.1
        
        # Adjust based on audience size (more reliable with larger audience)
        if profile.audience_metrics.total_followers > 10000:
            confidence += 0.05
        elif profile.audience_metrics.total_followers < 1000:
            confidence -= 0.1
        
        # Adjust based on business maturity
        if profile.monetization_maturity in [MonetizationMaturity.ADVANCED, MonetizationMaturity.EXPERT]:
            confidence += 0.05
        
        return max(0.5, min(1.0, confidence))

    async def connect(self) -> bool:
        """Connect to business metrics analysis service"""



        return True
    
    async def disconnect(self) -> bool:
        """Disconnect from business metrics analysis service"""



        return True
    
    async def process(self, data: Any) -> Dict[str, Any]:
        """Process business metrics data"""



        return await self.analyze_business_metrics(data)


# Global business metrics analyzer instance
# business_metrics_analyzer = BusinessMetricsAnalyzer()  # Commented out for testing


async def analyze_business_performance(business_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenient function for business metrics analysis
    
    Args:
        business_data: Business performance data and metrics
        
    Returns:
        Dict containing business metrics analysis results
    """



    try:
        result = await business_metrics_analyzer.analyze_business_metrics(business_data)
        return result
    except Exception as e:
        logger.error(f"Business metrics analysis error: {str(e)}")
        return {
            'error': str(e),
            'success': False
        }
