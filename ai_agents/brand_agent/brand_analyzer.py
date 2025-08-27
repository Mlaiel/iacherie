"""
Brand Analyzer - Advanced Brand Value & Performance Analysis System

Comprehensive brand analysis including value calculation, performance metrics,
competitive analysis, and market positioning for content creators and brands.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead AI Developer & Backend Senior Engineer
- Machine Learning Engineer & Audio Processing Specialist  
- Database Administrator & Security Expert
- Microservices Architect & DevOps Engineer
- AI Prompt Engineer & Content Protection Specialist
"""

import asyncio
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import math

from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity

from ...core.config import settings
from ...core.database import get_db_session
from ...utils.market_data import MarketDataProvider, CompetitorAnalyzer
from ...utils.social_analytics import SocialMediaAnalyzer
from ...utils.financial_calculator import BrandValueCalculator, ROIAnalyzer
from ...utils.ml_models import BrandPredictionModel, TrendAnalyzer

logger = logging.getLogger(__name__)

class BrandMetricType(Enum):
    """Types of brand metrics"""
    AWARENESS = "awareness"
    ENGAGEMENT = "engagement"
    SENTIMENT = "sentiment"
    REACH = "reach"
    CONVERSION = "conversion"
    LOYALTY = "loyalty"
    ADVOCACY = "advocacy"
    VALUE = "value"

class AnalysisTimeframe(Enum):
    """Analysis timeframe options"""
    HOURLY = "1h"
    DAILY = "1d" 
    WEEKLY = "1w"
    MONTHLY = "1m"
    QUARTERLY = "3m"
    YEARLY = "1y"

class BrandMaturityLevel(Enum):
    """Brand maturity classification"""
    EMERGING = "emerging"
    DEVELOPING = "developing"
    ESTABLISHED = "established"
    MATURE = "mature"
    LEGACY = "legacy"

@dataclass
class BrandMetrics:
    """Comprehensive brand performance metrics"""
    brand_id: str
    timeframe: AnalysisTimeframe
    awareness_score: float = 0.0
    engagement_rate: float = 0.0
    sentiment_score: float = 0.0
    reach_total: int = 0
    reach_organic: int = 0
    reach_paid: int = 0
    conversion_rate: float = 0.0
    loyalty_index: float = 0.0
    advocacy_score: float = 0.0
    brand_value_estimate: float = 0.0
    market_share: float = 0.0
    competitive_position: int = 0
    growth_rate: float = 0.0
    risk_score: float = 0.0
    calculated_at: datetime = field(default_factory=datetime.utcnow)
    data_sources: List[str] = field(default_factory=list)

@dataclass
class CompetitiveAnalysis:
    """Competitive landscape analysis"""
    brand_id: str
    competitor_landscape: List[Dict[str, Any]]
    market_position: int
    competitive_advantages: List[str]
    competitive_threats: List[str]
    market_opportunities: List[str]
    differentiation_score: float
    market_gap_analysis: Dict[str, Any]
    analyzed_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class BrandValueAssessment:
    """Comprehensive brand value assessment"""
    brand_id: str
    estimated_value: float
    value_components: Dict[str, float]
    valuation_method: str
    confidence_interval: Tuple[float, float]
    value_drivers: List[str]
    risk_factors: List[str]
    growth_potential: str
    assessed_at: datetime = field(default_factory=datetime.utcnow)
    assessment_validity: timedelta = field(default_factory=lambda: timedelta(days=90))

@dataclass
class BrandPerformanceReport:
    """Comprehensive brand performance analysis report"""
    report_id: str
    brand_id: str
    executive_summary: Dict[str, Any]
    key_metrics: BrandMetrics
    competitive_analysis: CompetitiveAnalysis
    value_assessment: BrandValueAssessment
    trends_analysis: Dict[str, Any]
    recommendations: List[str]
    action_items: List[Dict[str, Any]]
    generated_at: datetime = field(default_factory=datetime.utcnow)

class BrandAnalyzer:
    """
    Advanced Brand Value & Performance Analysis System
    
    Provides comprehensive brand analysis including:
    - Multi-dimensional brand metrics calculation
    - Competitive landscape analysis
    - Brand value estimation and assessment
    - Performance trend analysis
    - Market positioning insights
    - Growth opportunity identification
    """

    def __init__(self, brand_id: str):
        self.brand_id = brand_id
        
        # Initialize analysis components
        self.market_data_provider = MarketDataProvider()
        self.competitor_analyzer = CompetitorAnalyzer()
        self.social_analyzer = SocialMediaAnalyzer()
        self.value_calculator = BrandValueCalculator()
        self.roi_analyzer = ROIAnalyzer()
        self.prediction_model = BrandPredictionModel()
        self.trend_analyzer = TrendAnalyzer()
        
        # Data storage
        self.metrics_history: List[BrandMetrics] = []
        self.competitive_history: List[CompetitiveAnalysis] = []
        self.value_history: List[BrandValueAssessment] = []
        
        # Analysis models
        self.value_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.trend_model = None
        self.scaler = StandardScaler()
        
        # Configuration
        self.data_sources = [
            "social_media", "search_trends", "market_data", 
            "financial_data", "competitor_data", "consumer_surveys"
        ]
        
        logger.info(f"Brand analyzer initialized for brand: {brand_id}")

    async def analyze_brand_performance(self, timeframe: AnalysisTimeframe = AnalysisTimeframe.MONTHLY) -> BrandMetrics:
        """Comprehensive brand performance analysis"""
        try:
            logger.info(f"Starting brand performance analysis for timeframe: {timeframe.value}")
            
            # Collect data from all sources
            brand_data = await self._collect_brand_data(timeframe)
            
            # Calculate core metrics
            awareness_score = await self._calculate_awareness_score(brand_data)
            engagement_rate = await self._calculate_engagement_rate(brand_data)
            sentiment_score = await self._calculate_sentiment_score(brand_data)
            
            # Calculate reach metrics
            reach_metrics = await self._calculate_reach_metrics(brand_data)
            
            # Calculate business metrics
            conversion_rate = await self._calculate_conversion_rate(brand_data)
            loyalty_index = await self._calculate_loyalty_index(brand_data)
            advocacy_score = await self._calculate_advocacy_score(brand_data)
            
            # Calculate brand value
            brand_value = await self._estimate_brand_value(brand_data)
            
            # Calculate market metrics
            market_share = await self._calculate_market_share(brand_data)
            competitive_position = await self._calculate_competitive_position(brand_data)
            
            # Calculate growth and risk
            growth_rate = await self._calculate_growth_rate(brand_data)
            risk_score = await self._calculate_risk_score(brand_data)
            
            # Create metrics object
            metrics = BrandMetrics(
                brand_id=self.brand_id,
                timeframe=timeframe,
                awareness_score=awareness_score,
                engagement_rate=engagement_rate,
                sentiment_score=sentiment_score,
                reach_total=reach_metrics["total"],
                reach_organic=reach_metrics["organic"],
                reach_paid=reach_metrics["paid"],
                conversion_rate=conversion_rate,
                loyalty_index=loyalty_index,
                advocacy_score=advocacy_score,
                brand_value_estimate=brand_value,
                market_share=market_share,
                competitive_position=competitive_position,
                growth_rate=growth_rate,
                risk_score=risk_score,
                data_sources=list(brand_data.keys())
            )
            
            # Store metrics
            self.metrics_history.append(metrics)
            
            logger.info(f"Brand performance analysis completed. Value estimate: ${brand_value:,.2f}")
            return metrics
            
        except Exception as e:
            logger.error(f"Brand performance analysis failed: {str(e)}")
            raise

    async def _collect_brand_data(self, timeframe: AnalysisTimeframe) -> Dict[str, Any]:
        """Collect comprehensive brand data from all sources"""
        try:
            data = {}
            
            # Social media data
            data["social_media"] = await self.social_analyzer.get_brand_social_data(
                self.brand_id, timeframe.value
            )
            
            # Search trends data
            data["search_trends"] = await self.market_data_provider.get_search_trends(
                self.brand_id, timeframe.value
            )
            
            # Market data
            data["market_data"] = await self.market_data_provider.get_market_data(
                self.brand_id, timeframe.value
            )
            
            # Financial data (if available)
            data["financial_data"] = await self._get_financial_data(timeframe)
            
            # Competitor data
            data["competitor_data"] = await self.competitor_analyzer.get_competitor_data(
                self.brand_id, timeframe.value
            )
            
            # Consumer sentiment data
            data["consumer_sentiment"] = await self._get_consumer_sentiment_data(timeframe)
            
            return data
            
        except Exception as e:
            logger.error(f"Brand data collection failed: {str(e)}")
            return {}

    async def _calculate_awareness_score(self, brand_data: Dict[str, Any]) -> float:
        """Calculate brand awareness score (0-100)"""
        try:
            awareness_components = []
            
            # Search volume component
            search_data = brand_data.get("search_trends", {})
            search_volume = search_data.get("total_searches", 0)
            search_score = min(math.log10(max(search_volume, 1)) / 6, 1.0) * 30
            awareness_components.append(search_score)
            
            # Social media mentions component
            social_data = brand_data.get("social_media", {})
            mentions = social_data.get("total_mentions", 0)
            mention_score = min(math.log10(max(mentions, 1)) / 5, 1.0) * 25
            awareness_components.append(mention_score)
            
            # Brand recognition surveys (if available)
            survey_data = brand_data.get("consumer_sentiment", {})
            recognition_score = survey_data.get("brand_recognition", 0.5) * 25
            awareness_components.append(recognition_score)
            
            # Media coverage component
            media_coverage = social_data.get("media_mentions", 0)
            media_score = min(math.log10(max(media_coverage, 1)) / 4, 1.0) * 20
            awareness_components.append(media_score)
            
            total_awareness = sum(awareness_components)
            return min(max(total_awareness, 0), 100)
            
        except Exception as e:
            logger.error(f"Awareness score calculation failed: {str(e)}")
            return 0.0

    async def _calculate_engagement_rate(self, brand_data: Dict[str, Any]) -> float:
        """Calculate overall brand engagement rate"""
        try:
            social_data = brand_data.get("social_media", {})
            
            total_interactions = (
                social_data.get("likes", 0) + 
                social_data.get("comments", 0) + 
                social_data.get("shares", 0) + 
                social_data.get("clicks", 0)
            )
            
            total_reach = social_data.get("reach", 1)  # Avoid division by zero
            
            engagement_rate = (total_interactions / total_reach) * 100
            return min(engagement_rate, 100)  # Cap at 100%
            
        except Exception as e:
            logger.error(f"Engagement rate calculation failed: {str(e)}")
            return 0.0

    async def _calculate_sentiment_score(self, brand_data: Dict[str, Any]) -> float:
        """Calculate overall brand sentiment score (-1 to 1)"""
        try:
            social_data = brand_data.get("social_media", {})
            sentiment_data = brand_data.get("consumer_sentiment", {})
            
            # Social media sentiment
            social_sentiment = social_data.get("sentiment_score", 0.0)
            social_weight = 0.6
            
            # Consumer survey sentiment
            survey_sentiment = sentiment_data.get("overall_sentiment", 0.0)
            survey_weight = 0.4
            
            # Weighted average
            overall_sentiment = (
                social_sentiment * social_weight + 
                survey_sentiment * survey_weight
            )
            
            return max(min(overall_sentiment, 1.0), -1.0)
            
        except Exception as e:
            logger.error(f"Sentiment score calculation failed: {str(e)}")
            return 0.0

    async def _calculate_reach_metrics(self, brand_data: Dict[str, Any]) -> Dict[str, int]:
        """Calculate reach metrics breakdown"""
        try:
            social_data = brand_data.get("social_media", {})
            
            organic_reach = social_data.get("organic_reach", 0)
            paid_reach = social_data.get("paid_reach", 0)
            total_reach = organic_reach + paid_reach
            
            return {
                "total": total_reach,
                "organic": organic_reach,
                "paid": paid_reach
            }
            
        except Exception as e:
            logger.error(f"Reach metrics calculation failed: {str(e)}")
            return {"total": 0, "organic": 0, "paid": 0}

    async def _calculate_conversion_rate(self, brand_data: Dict[str, Any]) -> float:
        """Calculate brand conversion rate"""
        try:
            financial_data = brand_data.get("financial_data", {})
            social_data = brand_data.get("social_media", {})
            
            conversions = financial_data.get("conversions", 0)
            total_traffic = social_data.get("clicks", 0) + financial_data.get("website_visits", 0)
            
            if total_traffic == 0:
                return 0.0
            
            conversion_rate = (conversions / total_traffic) * 100
            return min(conversion_rate, 100)
            
        except Exception as e:
            logger.error(f"Conversion rate calculation failed: {str(e)}")
            return 0.0

    async def _calculate_loyalty_index(self, brand_data: Dict[str, Any]) -> float:
        """Calculate customer loyalty index (0-100)"""
        try:
            social_data = brand_data.get("social_media", {})
            financial_data = brand_data.get("financial_data", {})
            
            # Repeat customer rate
            repeat_rate = financial_data.get("repeat_customer_rate", 0.5)
            
            # Brand mention sentiment from existing customers
            customer_sentiment = social_data.get("customer_sentiment", 0.0)
            
            # Social media follower retention
            follower_retention = social_data.get("follower_retention_rate", 0.8)
            
            # Weighted loyalty score
            loyalty_index = (
                repeat_rate * 0.4 +
                (customer_sentiment + 1) / 2 * 0.3 +  # Convert -1,1 to 0,1
                follower_retention * 0.3
            ) * 100
            
            return min(max(loyalty_index, 0), 100)
            
        except Exception as e:
            logger.error(f"Loyalty index calculation failed: {str(e)}")
            return 50.0

    async def _calculate_advocacy_score(self, brand_data: Dict[str, Any]) -> float:
        """Calculate brand advocacy score (0-100)"""
        try:
            social_data = brand_data.get("social_media", {})
            
            # User-generated content score
            ugc_mentions = social_data.get("user_generated_content", 0)
            total_mentions = social_data.get("total_mentions", 1)
            ugc_ratio = ugc_mentions / total_mentions
            
            # Positive recommendation rate
            recommendation_rate = social_data.get("recommendation_rate", 0.5)
            
            # Share rate (viral coefficient)
            shares = social_data.get("shares", 0)
            total_interactions = social_data.get("total_interactions", 1)
            share_rate = shares / total_interactions
            
            # Net Promoter Score equivalent
            nps_equivalent = social_data.get("nps_equivalent", 0.0)  # -1 to 1
            
            # Weighted advocacy score
            advocacy_score = (
                ugc_ratio * 25 +
                recommendation_rate * 25 +
                share_rate * 25 +
                (nps_equivalent + 1) / 2 * 25  # Convert -1,1 to 0,1
            )
            
            return min(max(advocacy_score, 0), 100)
            
        except Exception as e:
            logger.error(f"Advocacy score calculation failed: {str(e)}")
            return 25.0

    async def _estimate_brand_value(self, brand_data: Dict[str, Any]) -> float:
        """Estimate brand value using multiple valuation methods"""
        try:
            # Revenue-based approach
            revenue_value = await self._calculate_revenue_based_value(brand_data)
            
            # Market-based approach
            market_value = await self._calculate_market_based_value(brand_data)
            
            # Cost-based approach
            cost_value = await self._calculate_cost_based_value(brand_data)
            
            # Income-based approach
            income_value = await self._calculate_income_based_value(brand_data)
            
            # Weighted average of all approaches
            total_value = (
                revenue_value * 0.3 +
                market_value * 0.3 +
                income_value * 0.3 +
                cost_value * 0.1
            )
            
            return max(total_value, 0)
            
        except Exception as e:
            logger.error(f"Brand value estimation failed: {str(e)}")
            return 0.0

    async def _calculate_revenue_based_value(self, brand_data: Dict[str, Any]) -> float:
        """Calculate brand value based on revenue metrics"""
        try:
            financial_data = brand_data.get("financial_data", {})
            
            annual_revenue = financial_data.get("annual_revenue", 0)
            revenue_growth_rate = financial_data.get("revenue_growth_rate", 0.05)
            brand_contribution = financial_data.get("brand_revenue_contribution", 0.3)
            
            # Brand-attributed revenue
            brand_revenue = annual_revenue * brand_contribution
            
            # Apply revenue multiple based on industry and growth
            industry_multiple = financial_data.get("industry_revenue_multiple", 3.0)
            growth_multiplier = 1 + max(revenue_growth_rate, 0)
            
            revenue_value = brand_revenue * industry_multiple * growth_multiplier
            
            return revenue_value
            
        except Exception as e:
            logger.error(f"Revenue-based value calculation failed: {str(e)}")
            return 0.0

    async def _calculate_market_based_value(self, brand_data: Dict[str, Any]) -> float:
        """Calculate brand value based on market comparables"""
        try:
            competitor_data = brand_data.get("competitor_data", {})
            market_data = brand_data.get("market_data", {})
            
            # Get comparable brand valuations
            comparable_valuations = competitor_data.get("comparable_brand_values", [])
            
            if not comparable_valuations:
                return 0.0
            
            # Calculate market position adjustment
            market_share = market_data.get("market_share", 0.01)
            competitive_position = competitor_data.get("competitive_ranking", 10)
            
            # Median comparable value as baseline
            median_value = np.median(comparable_valuations) if comparable_valuations else 0
            
            # Adjust based on relative market position
            position_multiplier = max(1 - (competitive_position - 1) * 0.1, 0.3)
            share_multiplier = 1 + math.log10(max(market_share * 100, 0.1)) / 10
            
            market_value = median_value * position_multiplier * share_multiplier
            
            return max(market_value, 0)
            
        except Exception as e:
            logger.error(f"Market-based value calculation failed: {str(e)}")
            return 0.0

    async def _calculate_cost_based_value(self, brand_data: Dict[str, Any]) -> float:
        """Calculate brand value based on development costs"""
        try:
            financial_data = brand_data.get("financial_data", {})
            
            # Brand development costs
            development_costs = financial_data.get("brand_development_costs", 0)
            marketing_spend = financial_data.get("annual_marketing_spend", 0)
            
            # Time and inflation adjustments
            brand_age_years = financial_data.get("brand_age_years", 1)
            annual_inflation = 0.03  # 3% average inflation
            
            # Depreciated development costs
            depreciated_development = development_costs * (0.9 ** brand_age_years)
            
            # Marketing spend contribution (3-year average)
            marketing_contribution = marketing_spend * 3 * 0.7  # 70% attributed to brand
            
            cost_value = depreciated_development + marketing_contribution
            
            return max(cost_value, 0)
            
        except Exception as e:
            logger.error(f"Cost-based value calculation failed: {str(e)}")
            return 0.0

    async def _calculate_income_based_value(self, brand_data: Dict[str, Any]) -> float:
        """Calculate brand value based on future income potential"""
        try:
            financial_data = brand_data.get("financial_data", {})
            
            # Brand-attributed cash flows
            annual_brand_cashflow = financial_data.get("brand_attributed_cashflow", 0)
            growth_rate = financial_data.get("expected_growth_rate", 0.05)
            discount_rate = financial_data.get("discount_rate", 0.10)
            
            if discount_rate <= growth_rate:
                discount_rate = growth_rate + 0.02  # Ensure discount rate > growth rate
            
            # DCF calculation (simplified perpetual growth model)
            next_year_cashflow = annual_brand_cashflow * (1 + growth_rate)
            terminal_value = next_year_cashflow / (discount_rate - growth_rate)
            
            # Present value
            present_value = terminal_value / (1 + discount_rate)
            
            return max(present_value, 0)
            
        except Exception as e:
            logger.error(f"Income-based value calculation failed: {str(e)}")
            return 0.0

    async def _calculate_market_share(self, brand_data: Dict[str, Any]) -> float:
        """Calculate brand market share"""
        try:
            market_data = brand_data.get("market_data", {})
            competitor_data = brand_data.get("competitor_data", {})
            
            brand_metrics = {
                "revenue": market_data.get("brand_revenue", 0),
                "customers": market_data.get("customer_count", 0),
                "awareness": market_data.get("brand_awareness", 0)
            }
            
            market_totals = {
                "revenue": market_data.get("total_market_revenue", 1),
                "customers": market_data.get("total_market_customers", 1),
                "awareness": market_data.get("total_market_awareness", 1)
            }
            
            # Calculate share across different dimensions
            revenue_share = brand_metrics["revenue"] / market_totals["revenue"]
            customer_share = brand_metrics["customers"] / market_totals["customers"]
            awareness_share = brand_metrics["awareness"] / market_totals["awareness"]
            
            # Weighted average market share
            market_share = (
                revenue_share * 0.5 +
                customer_share * 0.3 +
                awareness_share * 0.2
            )
            
            return min(max(market_share, 0), 1)
            
        except Exception as e:
            logger.error(f"Market share calculation failed: {str(e)}")
            return 0.01  # Default 1%

    async def _calculate_competitive_position(self, brand_data: Dict[str, Any]) -> int:
        """Calculate brand competitive position ranking"""
        try:
            competitor_data = brand_data.get("competitor_data", {})
            
            # Get competitor rankings across different metrics
            rankings = competitor_data.get("competitive_rankings", {})
            
            revenue_rank = rankings.get("revenue", 10)
            awareness_rank = rankings.get("awareness", 10)
            engagement_rank = rankings.get("engagement", 10)
            innovation_rank = rankings.get("innovation", 10)
            
            # Weighted average ranking
            overall_rank = (
                revenue_rank * 0.4 +
                awareness_rank * 0.3 +
                engagement_rank * 0.2 +
                innovation_rank * 0.1
            )
            
            return int(round(overall_rank))
            
        except Exception as e:
            logger.error(f"Competitive position calculation failed: {str(e)}")
            return 10  # Default middle ranking

    async def _calculate_growth_rate(self, brand_data: Dict[str, Any]) -> float:
        """Calculate brand growth rate"""
        try:
            # Get historical metrics for growth calculation
            if len(self.metrics_history) < 2:
                return 0.05  # Default 5% growth assumption
            
            current_metrics = self.metrics_history[-1]
            previous_metrics = self.metrics_history[-2]
            
            # Calculate growth across key metrics
            value_growth = (current_metrics.brand_value_estimate - previous_metrics.brand_value_estimate) / max(previous_metrics.brand_value_estimate, 1)
            awareness_growth = (current_metrics.awareness_score - previous_metrics.awareness_score) / max(previous_metrics.awareness_score, 1)
            engagement_growth = (current_metrics.engagement_rate - previous_metrics.engagement_rate) / max(previous_metrics.engagement_rate, 1)
            
            # Weighted average growth rate
            overall_growth = (
                value_growth * 0.5 +
                awareness_growth * 0.3 +
                engagement_growth * 0.2
            )
            
            return max(min(overall_growth, 1.0), -0.5)  # Cap between -50% and 100%
            
        except Exception as e:
            logger.error(f"Growth rate calculation failed: {str(e)}")
            return 0.05

    async def _calculate_risk_score(self, brand_data: Dict[str, Any]) -> float:
        """Calculate brand risk score (0-1, higher is riskier)"""
        try:
            risk_factors = []
            
            # Sentiment risk
            sentiment_score = brand_data.get("consumer_sentiment", {}).get("overall_sentiment", 0)
            sentiment_risk = max(0, -sentiment_score)  # Negative sentiment increases risk
            risk_factors.append(sentiment_risk * 0.3)
            
            # Market volatility risk
            market_data = brand_data.get("market_data", {})
            market_volatility = market_data.get("market_volatility", 0.2)
            risk_factors.append(market_volatility * 0.2)
            
            # Competitive pressure risk
            competitor_data = brand_data.get("competitor_data", {})
            competitive_pressure = competitor_data.get("competitive_pressure_index", 0.5)
            risk_factors.append(competitive_pressure * 0.2)
            
            # Financial stability risk
            financial_data = brand_data.get("financial_data", {})
            debt_ratio = financial_data.get("debt_to_equity_ratio", 0.3)
            financial_risk = min(debt_ratio, 1.0)
            risk_factors.append(financial_risk * 0.15)
            
            # Regulatory risk
            regulatory_risk = market_data.get("regulatory_risk_score", 0.1)
            risk_factors.append(regulatory_risk * 0.15)
            
            total_risk = sum(risk_factors)
            return min(max(total_risk, 0), 1)
            
        except Exception as e:
            logger.error(f"Risk score calculation failed: {str(e)}")
            return 0.3  # Default moderate risk

    async def perform_competitive_analysis(self) -> CompetitiveAnalysis:
        """Perform comprehensive competitive landscape analysis"""
        try:
            logger.info("Starting competitive analysis")
            
            # Get competitor data
            competitors = await self.competitor_analyzer.identify_competitors(self.brand_id)
            competitor_metrics = await self._analyze_competitor_metrics(competitors)
            
            # Calculate market position
            market_position = await self._calculate_market_position(competitor_metrics)
            
            # Identify competitive advantages and threats
            competitive_advantages = await self._identify_competitive_advantages(competitor_metrics)
            competitive_threats = await self._identify_competitive_threats(competitor_metrics)
            
            # Identify market opportunities
            market_opportunities = await self._identify_market_opportunities(competitor_metrics)
            
            # Calculate differentiation score
            differentiation_score = await self._calculate_differentiation_score(competitor_metrics)
            
            # Perform market gap analysis
            market_gap_analysis = await self._perform_market_gap_analysis(competitor_metrics)
            
            analysis = CompetitiveAnalysis(
                brand_id=self.brand_id,
                competitor_landscape=competitor_metrics,
                market_position=market_position,
                competitive_advantages=competitive_advantages,
                competitive_threats=competitive_threats,
                market_opportunities=market_opportunities,
                differentiation_score=differentiation_score,
                market_gap_analysis=market_gap_analysis
            )
            
            self.competitive_history.append(analysis)
            
            logger.info(f"Competitive analysis completed. Market position: #{market_position}")
            return analysis
            
        except Exception as e:
            logger.error(f"Competitive analysis failed: {str(e)}")
            raise

    async def assess_brand_value(self) -> BrandValueAssessment:
        """Perform comprehensive brand value assessment"""
        try:
            logger.info("Starting brand value assessment")
            
            # Get latest brand data
            brand_data = await self._collect_brand_data(AnalysisTimeframe.YEARLY)
            
            # Calculate estimated value
            estimated_value = await self._estimate_brand_value(brand_data)
            
            # Break down value components
            value_components = await self._calculate_value_components(brand_data)
            
            # Determine confidence interval
            confidence_interval = await self._calculate_confidence_interval(estimated_value, brand_data)
            
            # Identify value drivers and risk factors
            value_drivers = await self._identify_value_drivers(brand_data)
            risk_factors = await self._identify_risk_factors(brand_data)
            
            # Assess growth potential
            growth_potential = await self._assess_growth_potential(brand_data)
            
            assessment = BrandValueAssessment(
                brand_id=self.brand_id,
                estimated_value=estimated_value,
                value_components=value_components,
                valuation_method="multi_approach_weighted",
                confidence_interval=confidence_interval,
                value_drivers=value_drivers,
                risk_factors=risk_factors,
                growth_potential=growth_potential
            )
            
            self.value_history.append(assessment)
            
            logger.info(f"Brand value assessment completed. Estimated value: ${estimated_value:,.2f}")
            return assessment
            
        except Exception as e:
            logger.error(f"Brand value assessment failed: {str(e)}")
            raise

    async def generate_performance_report(self, 
                                         timeframe: AnalysisTimeframe = AnalysisTimeframe.QUARTERLY) -> BrandPerformanceReport:
        """Generate comprehensive brand performance report"""
        try:
            report_id = f"brand_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            logger.info(f"Generating brand performance report: {report_id}")
            
            # Perform all analyses
            key_metrics = await self.analyze_brand_performance(timeframe)
            competitive_analysis = await self.perform_competitive_analysis()
            value_assessment = await self.assess_brand_value()
            
            # Generate trends analysis
            trends_analysis = await self._analyze_performance_trends()
            
            # Generate executive summary
            executive_summary = await self._generate_executive_summary(
                key_metrics, competitive_analysis, value_assessment
            )
            
            # Generate recommendations and action items
            recommendations = await self._generate_recommendations(
                key_metrics, competitive_analysis, value_assessment, trends_analysis
            )
            action_items = await self._generate_action_items(recommendations)
            
            report = BrandPerformanceReport(
                report_id=report_id,
                brand_id=self.brand_id,
                executive_summary=executive_summary,
                key_metrics=key_metrics,
                competitive_analysis=competitive_analysis,
                value_assessment=value_assessment,
                trends_analysis=trends_analysis,
                recommendations=recommendations,
                action_items=action_items
            )
            
            logger.info(f"Brand performance report generated: {report_id}")
            return report
            
        except Exception as e:
            logger.error(f"Performance report generation failed: {str(e)}")
            raise

    async def _generate_executive_summary(self, 
                                          metrics: BrandMetrics,
                                          competitive: CompetitiveAnalysis,
                                          value: BrandValueAssessment) -> Dict[str, Any]:
        """Generate executive summary of brand performance"""
        try:
            # Determine brand health status
            health_score = (
                metrics.awareness_score * 0.2 +
                metrics.engagement_rate * 0.2 +
                (metrics.sentiment_score + 1) * 50 * 0.2 +  # Convert to 0-100
                metrics.advocacy_score * 0.2 +
                (1 - metrics.risk_score) * 100 * 0.2
            )
            
            health_status = "Excellent" if health_score >= 80 else \
                           "Good" if health_score >= 60 else \
                           "Fair" if health_score >= 40 else "Poor"
            
            # Key highlights
            highlights = []
            if metrics.growth_rate > 0.1:
                highlights.append(f"Strong growth rate of {metrics.growth_rate:.1%}")
            if competitive.market_position <= 3:
                highlights.append(f"Top market position (#{competitive.market_position})")
            if value.estimated_value > 1000000:
                highlights.append(f"High brand value of ${value.estimated_value:,.0f}")
            if metrics.sentiment_score > 0.3:
                highlights.append("Positive brand sentiment")
            
            # Key concerns
            concerns = []
            if metrics.risk_score > 0.6:
                concerns.append("High risk factors detected")
            if metrics.growth_rate < 0:
                concerns.append(f"Negative growth rate ({metrics.growth_rate:.1%})")
            if competitive.market_position > 10:
                concerns.append("Low competitive position")
            if metrics.sentiment_score < -0.2:
                concerns.append("Negative brand sentiment")
            
            return {
                "health_status": health_status,
                "health_score": round(health_score, 1),
                "key_highlights": highlights,
                "key_concerns": concerns,
                "brand_value": value.estimated_value,
                "market_position": competitive.market_position,
                "growth_rate": metrics.growth_rate,
                "sentiment_score": metrics.sentiment_score
            }
            
        except Exception as e:
            logger.error(f"Executive summary generation failed: {str(e)}")
            return {}

    async def _generate_recommendations(self, 
                                        metrics: BrandMetrics,
                                        competitive: CompetitiveAnalysis,
                                        value: BrandValueAssessment,
                                        trends: Dict[str, Any]) -> List[str]:
        """Generate strategic recommendations"""
        recommendations = []
        
        try:
            # Awareness recommendations
            if metrics.awareness_score < 50:
                recommendations.append("Increase brand awareness through targeted marketing campaigns")
                recommendations.append("Invest in search engine optimization and content marketing")
            
            # Engagement recommendations
            if metrics.engagement_rate < 5:
                recommendations.append("Improve content strategy to increase audience engagement")
                recommendations.append("Implement interactive marketing campaigns")
            
            # Sentiment recommendations
            if metrics.sentiment_score < 0:
                recommendations.append("Address negative sentiment through improved customer service")
                recommendations.append("Implement reputation management strategy")
            
            # Competitive recommendations
            if competitive.market_position > 5:
                recommendations.append("Strengthen competitive position through differentiation")
                recommendations.append("Focus on competitive advantages: " + ", ".join(competitive.competitive_advantages[:3]))
            
            # Growth recommendations
            if metrics.growth_rate < 0.05:
                recommendations.append("Implement growth acceleration strategies")
                recommendations.append("Explore new market opportunities")
            
            # Value optimization recommendations
            for driver in value.value_drivers[:3]:
                recommendations.append(f"Leverage value driver: {driver}")
            
            # Risk mitigation recommendations
            for risk in value.risk_factors[:3]:
                recommendations.append(f"Mitigate risk factor: {risk}")
                
        except Exception as e:
            logger.error(f"Recommendation generation failed: {str(e)}")
        
        return recommendations

    async def _generate_action_items(self, recommendations: List[str]) -> List[Dict[str, Any]]:
        """Generate specific action items from recommendations"""
        action_items = []
        
        try:
            priority_mapping = {
                "critical": 1,
                "high": 2, 
                "medium": 3,
                "low": 4
            }
            
            for i, recommendation in enumerate(recommendations):
                # Determine priority based on keywords
                priority = "medium"
                if any(word in recommendation.lower() for word in ["critical", "urgent", "immediate"]):
                    priority = "critical"
                elif any(word in recommendation.lower() for word in ["important", "address", "negative"]):
                    priority = "high"
                elif any(word in recommendation.lower() for word in ["explore", "consider", "optimize"]):
                    priority = "low"
                
                # Estimate timeline
                timeline = "3-6 months"
                if priority == "critical":
                    timeline = "1-2 weeks"
                elif priority == "high":
                    timeline = "1-2 months"
                elif priority == "low":
                    timeline = "6-12 months"
                
                action_item = {
                    "id": f"action_{i+1:03d}",
                    "description": recommendation,
                    "priority": priority,
                    "estimated_timeline": timeline,
                    "category": self._categorize_action(recommendation),
                    "status": "pending",
                    "assigned_to": None,
                    "due_date": None
                }
                
                action_items.append(action_item)
            
            # Sort by priority
            action_items.sort(key=lambda x: priority_mapping.get(x["priority"], 3))
            
        except Exception as e:
            logger.error(f"Action item generation failed: {str(e)}")
        
        return action_items

    def _categorize_action(self, action_description: str) -> str:
        """Categorize action item based on description"""
        description_lower = action_description.lower()
        
        if any(word in description_lower for word in ["marketing", "campaign", "awareness"]):
            return "Marketing"
        elif any(word in description_lower for word in ["content", "engagement", "social"]):
            return "Content Strategy"
        elif any(word in description_lower for word in ["competitive", "market", "position"]):
            return "Competitive Strategy"
        elif any(word in description_lower for word in ["risk", "security", "legal"]):
            return "Risk Management"
        elif any(word in description_lower for word in ["value", "financial", "revenue"]):
            return "Business Development"
        else:
            return "General Strategy"


class ValueCalculator:
    """
    Specialized Brand Value Calculator
    
    Advanced financial modeling for brand valuation using multiple methodologies.
    """

    def __init__(self):
        self.valuation_models = {
            "relief_from_royalty": self._relief_from_royalty_method,
            "premium_pricing": self._premium_pricing_method,
            "cost_of_capital": self._cost_of_capital_method,
            "market_multiples": self._market_multiples_method
        }
        
        logger.info("Brand value calculator initialized")

    async def calculate_comprehensive_value(self, brand_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate brand value using multiple methods"""
        try:
            valuations = {}
            
            for method_name, method_func in self.valuation_models.items():
                try:
                    valuation = await method_func(brand_data)
                    valuations[method_name] = valuation
                except Exception as e:
                    logger.warning(f"Valuation method {method_name} failed: {str(e)}")
                    valuations[method_name] = 0
            
            # Calculate weighted average
            weights = {
                "relief_from_royalty": 0.3,
                "premium_pricing": 0.3,
                "cost_of_capital": 0.2,
                "market_multiples": 0.2
            }
            
            weighted_value = sum(
                valuations[method] * weights.get(method, 0)
                for method in valuations
            )
            
            return {
                "comprehensive_value": weighted_value,
                "method_values": valuations,
                "confidence_score": self._calculate_confidence_score(valuations)
            }
            
        except Exception as e:
            logger.error(f"Comprehensive valuation failed: {str(e)}")
            return {"comprehensive_value": 0, "method_values": {}, "confidence_score": 0}

    async def _relief_from_royalty_method(self, brand_data: Dict[str, Any]) -> float:
        """Relief from royalty valuation method"""
        try:
            financial_data = brand_data.get("financial_data", {})
            
            branded_revenue = financial_data.get("branded_revenue", 0)
            royalty_rate = financial_data.get("industry_royalty_rate", 0.05)
            tax_rate = financial_data.get("tax_rate", 0.25)
            discount_rate = financial_data.get("discount_rate", 0.10)
            growth_rate = financial_data.get("growth_rate", 0.03)
            
            # After-tax royalty savings
            annual_royalty_savings = branded_revenue * royalty_rate * (1 - tax_rate)
            
            # Present value of perpetual royalty savings
            if discount_rate > growth_rate:
                brand_value = annual_royalty_savings * (1 + growth_rate) / (discount_rate - growth_rate)
            else:
                brand_value = annual_royalty_savings * 10  # Simple multiple if growth >= discount
            
            return max(brand_value, 0)
            
        except Exception as e:
            logger.error(f"Relief from royalty method failed: {str(e)}")
            return 0

    def _calculate_confidence_score(self, valuations: Dict[str, float]) -> float:
        """Calculate confidence score based on valuation consistency"""
        try:
            values = [v for v in valuations.values() if v > 0]
            
            if len(values) < 2:
                return 0.3  # Low confidence with insufficient methods
            
            # Calculate coefficient of variation
            mean_value = np.mean(values)
            std_value = np.std(values)
            
            if mean_value == 0:
                return 0.1
            
            cv = std_value / mean_value
            
            # Convert to confidence score (lower CV = higher confidence)
            confidence = max(0, 1 - cv)
            
            return min(confidence, 1.0)
            
        except Exception:
            return 0.5
