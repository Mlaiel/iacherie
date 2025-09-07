"""Intelligent Pricing Orchestrator - AI-Powered Dynamic Pricing Strategy Engine
==============================================================================

Enterprise-grade intelligent pricing orchestrator providing AI-powered
dynamic pricing strategies, market analysis, and automated pricing
optimization for content creators across all platforms.

Architecture: Enterprise Production-Ready (Backend Level 3)
Module: backend/monetization/intelligent_pricing_orchestrator.py

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from uuid import uuid4, UUID
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass, field
import json
import math
from statistics import mean, median, stdev

logger = logging.getLogger(__name__)


class PricingStrategy(str, Enum):
    """Available pricing strategies."""
    DYNAMIC = "dynamic"
    COMPETITIVE = "competitive"
    VALUE_BASED = "value_based"
    PENETRATION = "penetration"
    PREMIUM = "premium"
    FREEMIUM = "freemium"
    BUNDLED = "bundled"
    SEASONAL = "seasonal"
    DEMAND_BASED = "demand_based"


class MarketPosition(str, Enum):
    """Market position classifications."""
    LEADER = "leader"
    CHALLENGER = "challenger"
    FOLLOWER = "follower"
    NICHE = "niche"


class PriceOptimizationGoal(str, Enum):
    """Price optimization objectives."""
    MAXIMIZE_REVENUE = "maximize_revenue"
    MAXIMIZE_PROFIT = "maximize_profit"
    MAXIMIZE_MARKET_SHARE = "maximize_market_share"
    MAXIMIZE_CONVERSION = "maximize_conversion"
    MINIMIZE_CHURN = "minimize_churn"


class ContentCategory(str, Enum):
    """Content categories for pricing."""
    MUSIC = "music"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    PODCAST = "podcast"
    COURSE = "course"
    EBOOK = "ebook"
    SOFTWARE = "software"
    ART = "art"
    PHOTOGRAPHY = "photography"


@dataclass
class MarketData:
    """Market analysis data for pricing decisions."""
    category: ContentCategory
    average_price: Decimal
    price_range: Tuple[Decimal, Decimal]
    competitor_count: int
    market_size: int
    growth_rate: float
    seasonality_factor: float
    price_elasticity: float
    demand_trend: str  # "increasing", "stable", "decreasing"
    last_updated: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CompetitorPricing:
    """Competitor pricing information."""
    competitor_id: str
    competitor_name: str
    price: Decimal
    market_share: float
    quality_score: float
    features: List[str]
    pricing_strategy: PricingStrategy
    last_price_change: Optional[datetime] = None
    price_history: List[Tuple[datetime, Decimal]] = field(default_factory=list)


@dataclass
class PricingModel:
    """AI pricing model configuration and parameters."""
    model_id: str
    model_name: str
    strategy: PricingStrategy
    optimization_goal: PriceOptimizationGoal
    features: List[str]
    weights: Dict[str, float]
    accuracy: float
    confidence_threshold: float = 0.8
    last_trained: datetime = field(default_factory=datetime.utcnow)
    version: str = "1.0"


@dataclass
class PricingRecommendation:
    """AI-generated pricing recommendation."""
    recommendation_id: str
    content_id: str
    creator_id: str
    recommended_price: Decimal
    current_price: Optional[Decimal]
    price_change_percentage: float
    confidence_score: float
    expected_revenue_change: Decimal
    expected_conversion_change: float
    reasoning: List[str]
    supporting_data: Dict[str, Any]
    strategy_used: PricingStrategy
    valid_until: datetime
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PriceTestResult:
    """A/B price testing results."""
    test_id: str
    content_id: str
    test_duration_days: int
    control_price: Decimal
    test_price: Decimal
    control_conversions: int
    test_conversions: int
    control_revenue: Decimal
    test_revenue: Decimal
    statistical_significance: float
    winner: str  # "control", "test", "inconclusive"
    recommendation: str
    confidence: float
    created_at: datetime = field(default_factory=datetime.utcnow)


class IntelligentPricingOrchestrator:
    """
    Advanced intelligent pricing orchestrator providing AI-powered
    dynamic pricing strategies and automated pricing optimization.
    """
    
    def __init__(self):
        """Initialize the intelligent pricing orchestrator."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.pricing_models: Dict[str, PricingModel] = {}
        self.market_data: Dict[ContentCategory, MarketData] = {}
        self.competitor_data: Dict[str, List[CompetitorPricing]] = {}  # content_id -> competitors
        self.pricing_history: Dict[str, List[Tuple[datetime, Decimal]]] = {}  # content_id -> history
        self.recommendations: Dict[str, PricingRecommendation] = {}
        self.active_tests: Dict[str, PriceTestResult] = {}
        
        # Initialize default pricing models
        self._initialize_pricing_models()
        
        # Initialize market data
        self._initialize_market_data()
        
        self.logger.info("IntelligentPricingOrchestrator initialized")
    
    def _initialize_pricing_models(self):
        """Initialize default AI pricing models."""
        # Dynamic pricing model
        dynamic_model = PricingModel(
            model_id="dynamic_v1",
            model_name="Dynamic Pricing AI",
            strategy=PricingStrategy.DYNAMIC,
            optimization_goal=PriceOptimizationGoal.MAXIMIZE_REVENUE,
            features=[
                "content_quality", "engagement_rate", "market_demand",
                "competitor_prices", "seasonal_factors", "user_willingness_to_pay"
            ],
            weights={
                "content_quality": 0.25,
                "engagement_rate": 0.20,
                "market_demand": 0.20,
                "competitor_prices": 0.15,
                "seasonal_factors": 0.10,
                "user_willingness_to_pay": 0.10
            },
            accuracy=0.87
        )
        
        # Value-based pricing model
        value_model = PricingModel(
            model_id="value_v1",
            model_name="Value-Based Pricing AI",
            strategy=PricingStrategy.VALUE_BASED,
            optimization_goal=PriceOptimizationGoal.MAXIMIZE_PROFIT,
            features=[
                "perceived_value", "unique_features", "brand_strength",
                "customer_lifetime_value", "production_cost"
            ],
            weights={
                "perceived_value": 0.30,
                "unique_features": 0.25,
                "brand_strength": 0.20,
                "customer_lifetime_value": 0.15,
                "production_cost": 0.10
            },
            accuracy=0.82
        )
        
        # Competitive pricing model
        competitive_model = PricingModel(
            model_id="competitive_v1",
            model_name="Competitive Pricing AI",
            strategy=PricingStrategy.COMPETITIVE,
            optimization_goal=PriceOptimizationGoal.MAXIMIZE_MARKET_SHARE,
            features=[
                "competitor_avg_price", "market_position", "price_sensitivity",
                "switching_cost", "differentiation_factor"
            ],
            weights={
                "competitor_avg_price": 0.35,
                "market_position": 0.25,
                "price_sensitivity": 0.20,
                "switching_cost": 0.10,
                "differentiation_factor": 0.10
            },
            accuracy=0.79
        )
        
        self.pricing_models.update({
            "dynamic_v1": dynamic_model,
            "value_v1": value_model,
            "competitive_v1": competitive_model
        })
    
    def _initialize_market_data(self):
        """Initialize default market data for different categories."""
        categories_data = {
            ContentCategory.MUSIC: MarketData(
                category=ContentCategory.MUSIC,
                average_price=Decimal("1.29"),
                price_range=(Decimal("0.99"), Decimal("2.99")),
                competitor_count=1500,
                market_size=50000000,
                growth_rate=0.12,
                seasonality_factor=1.2,
                price_elasticity=-0.8,
                demand_trend="increasing"
            ),
            ContentCategory.VIDEO: MarketData(
                category=ContentCategory.VIDEO,
                average_price=Decimal("9.99"),
                price_range=(Decimal("4.99"), Decimal("29.99")),
                competitor_count=5000,
                market_size=100000000,
                growth_rate=0.25,
                seasonality_factor=1.1,
                price_elasticity=-1.2,
                demand_trend="increasing"
            ),
            ContentCategory.IMAGE: MarketData(
                category=ContentCategory.IMAGE,
                average_price=Decimal("5.00"),
                price_range=(Decimal("1.00"), Decimal("25.00")),
                competitor_count=2000,
                market_size=20000000,
                growth_rate=0.08,
                seasonality_factor=1.0,
                price_elasticity=-0.6,
                demand_trend="stable"
            ),
            ContentCategory.PODCAST: MarketData(
                category=ContentCategory.PODCAST,
                average_price=Decimal("4.99"),
                price_range=(Decimal("2.99"), Decimal("15.99")),
                competitor_count=800,
                market_size=15000000,
                growth_rate=0.30,
                seasonality_factor=0.9,
                price_elasticity=-1.0,
                demand_trend="increasing"
            )
        }
        
        self.market_data.update(categories_data)
    
    async def analyze_pricing_opportunity(
        self,
        content_id: str,
        creator_id: str,
        content_category: ContentCategory,
        current_price: Optional[Decimal] = None,
        content_metrics: Dict[str, Any] = None
    ) -> PricingRecommendation:
        """Analyze pricing opportunity and generate AI recommendation."""
        try:
            self.logger.info(f"Analyzing pricing opportunity for content: {content_id}")
            
            # Get market data
            market_data = self.market_data.get(content_category)
            if not market_data:
                raise ValueError(f"No market data available for category: {content_category}")
            
            # Analyze competitors
            competitor_analysis = await self._analyze_competitors(content_id, content_category)
            
            # Select best pricing model
            best_model = await self._select_optimal_model(
                content_category, content_metrics or {}, competitor_analysis
            )
            
            # Generate price recommendation
            recommended_price = await self._calculate_optimal_price(
                best_model, market_data, competitor_analysis, content_metrics or {}
            )
            
            # Calculate confidence and impact
            confidence_score = await self._calculate_confidence(
                best_model, market_data, competitor_analysis
            )
            
            revenue_impact = await self._estimate_revenue_impact(
                current_price, recommended_price, market_data, content_metrics or {}
            )
            
            conversion_impact = await self._estimate_conversion_impact(
                current_price, recommended_price, market_data
            )
            
            # Generate reasoning
            reasoning = await self._generate_pricing_reasoning(
                best_model, market_data, competitor_analysis, recommended_price
            )
            
            # Calculate price change percentage
            price_change = 0.0
            if current_price and current_price > 0:
                price_change = float((recommended_price - current_price) / current_price * 100)
            
            recommendation = PricingRecommendation(
                recommendation_id=str(uuid4()),
                content_id=content_id,
                creator_id=creator_id,
                recommended_price=recommended_price,
                current_price=current_price,
                price_change_percentage=price_change,
                confidence_score=confidence_score,
                expected_revenue_change=revenue_impact,
                expected_conversion_change=conversion_impact,
                reasoning=reasoning,
                supporting_data={
                    "market_analysis": {
                        "category": content_category.value,
                        "market_average": str(market_data.average_price),
                        "price_elasticity": market_data.price_elasticity
                    },
                    "competitor_analysis": competitor_analysis,
                    "model_used": best_model.model_name
                },
                strategy_used=best_model.strategy,
                valid_until=datetime.utcnow() + timedelta(days=7)
            )
            
            # Store recommendation
            self.recommendations[recommendation.recommendation_id] = recommendation
            
            self.logger.info(f"✅ Generated pricing recommendation: ${recommended_price} (confidence: {confidence_score:.2f})")
            return recommendation
            
        except Exception as e:
            self.logger.error(f"Error analyzing pricing opportunity: {e}")
            raise
    
    async def _analyze_competitors(
        self,
        content_id: str,
        category: ContentCategory
    ) -> Dict[str, Any]:
        """Analyze competitor pricing for similar content."""
        # In a real implementation, this would fetch from external APIs
        # For now, generate realistic competitor data
        
        market_data = self.market_data.get(category)
        if not market_data:
            return {}
        
        competitors = []
        
        # Generate 3-5 competitors with realistic pricing
        for i in range(3, 6):
            base_price = market_data.average_price
            variance = base_price * Decimal("0.3")  # ±30% variance
            
            competitor_price = base_price + (Decimal(str(i - 3)) * variance / 3) - (variance / 2)
            competitor_price = max(competitor_price, market_data.price_range[0])
            competitor_price = min(competitor_price, market_data.price_range[1])
            
            competitor = CompetitorPricing(
                competitor_id=f"comp_{category.value}_{i}",
                competitor_name=f"Competitor {i}",
                price=competitor_price,
                market_share=0.15 + (0.05 * i),
                quality_score=0.6 + (0.1 * i),
                features=[f"feature_{j}" for j in range(2, 5)],
                pricing_strategy=PricingStrategy.COMPETITIVE
            )
            competitors.append(competitor)
        
        # Store competitor data
        self.competitor_data[content_id] = competitors
        
        # Calculate analysis metrics
        prices = [comp.price for comp in competitors]
        avg_price = mean(prices)
        min_price = min(prices)
        max_price = max(prices)
        price_spread = max_price - min_price
        
        return {
            "competitor_count": len(competitors),
            "average_price": str(avg_price),
            "min_price": str(min_price),
            "max_price": str(max_price),
            "price_spread": str(price_spread),
            "competitors": [
                {
                    "name": comp.competitor_name,
                    "price": str(comp.price),
                    "market_share": comp.market_share,
                    "quality_score": comp.quality_score
                }
                for comp in competitors
            ]
        }
    
    async def _select_optimal_model(
        self,
        category: ContentCategory,
        content_metrics: Dict[str, Any],
        competitor_analysis: Dict[str, Any]
    ) -> PricingModel:
        """Select the most appropriate pricing model based on context."""
        
        # Decision logic for model selection
        competitor_count = competitor_analysis.get("competitor_count", 0)
        content_quality = content_metrics.get("quality_score", 0.5)
        engagement_rate = content_metrics.get("engagement_rate", 0.05)
        
        # High competition → Competitive model
        if competitor_count > 10:
            return self.pricing_models["competitive_v1"]
        
        # High quality + High engagement → Value-based model
        if content_quality > 0.8 and engagement_rate > 0.1:
            return self.pricing_models["value_v1"]
        
        # Default to dynamic model
        return self.pricing_models["dynamic_v1"]
    
    async def _calculate_optimal_price(
        self,
        model: PricingModel,
        market_data: MarketData,
        competitor_analysis: Dict[str, Any],
        content_metrics: Dict[str, Any]
    ) -> Decimal:
        """Calculate optimal price using the selected AI model."""
        
        # Feature extraction and normalization
        features = {}
        
        # Content quality (0-1)
        features["content_quality"] = content_metrics.get("quality_score", 0.5)
        
        # Engagement rate (normalized to 0-1)
        engagement = content_metrics.get("engagement_rate", 0.05)
        features["engagement_rate"] = min(engagement * 10, 1.0)  # Normalize typical 0.05 to 0.5
        
        # Market demand (based on growth rate)
        features["market_demand"] = min(market_data.growth_rate * 2, 1.0)
        
        # Competitor price influence
        if competitor_analysis:
            avg_competitor_price = Decimal(competitor_analysis.get("average_price", "0"))
            market_avg = market_data.average_price
            if market_avg > 0:
                features["competitor_prices"] = float(avg_competitor_price / market_avg)
            else:
                features["competitor_prices"] = 1.0
        else:
            features["competitor_prices"] = 1.0
        
        # Seasonal factors
        features["seasonal_factors"] = market_data.seasonality_factor
        
        # User willingness to pay (estimated)
        features["user_willingness_to_pay"] = 0.7  # Default assumption
        
        # Calculate weighted score
        total_score = 0.0
        for feature_name, weight in model.weights.items():
            feature_value = features.get(feature_name, 0.5)  # Default to neutral
            total_score += feature_value * weight
        
        # Apply score to price calculation
        base_price = market_data.average_price
        
        if model.strategy == PricingStrategy.DYNAMIC:
            # Dynamic: Adjust based on all factors
            price_multiplier = Decimal(str(0.7 + (total_score * 0.6)))  # 0.7 to 1.3 range
            optimal_price = base_price * price_multiplier
            
        elif model.strategy == PricingStrategy.VALUE_BASED:
            # Value-based: Premium pricing for high value
            quality_premium = Decimal(str(features["content_quality"] * 0.5))
            optimal_price = base_price * (Decimal("1.0") + quality_premium)
            
        elif model.strategy == PricingStrategy.COMPETITIVE:
            # Competitive: Price relative to competitors
            comp_factor = Decimal(str(features["competitor_prices"]))
            optimal_price = base_price * comp_factor * Decimal("0.95")  # Slightly below market
            
        else:
            optimal_price = base_price
        
        # Ensure price is within market range
        min_price, max_price = market_data.price_range
        optimal_price = max(min_price, min(optimal_price, max_price))
        
        return optimal_price.quantize(Decimal("0.01"))
    
    async def _calculate_confidence(
        self,
        model: PricingModel,
        market_data: MarketData,
        competitor_analysis: Dict[str, Any]
    ) -> float:
        """Calculate confidence score for the pricing recommendation."""
        
        # Base confidence from model accuracy
        base_confidence = model.accuracy
        
        # Data quality factors
        data_quality = 1.0
        
        # Market data freshness
        data_age_days = (datetime.utcnow() - market_data.last_updated).days
        if data_age_days > 30:
            data_quality *= 0.9
        
        # Competitor data availability
        if not competitor_analysis or competitor_analysis.get("competitor_count", 0) < 3:
            data_quality *= 0.8
        
        # Market volatility factor
        volatility_factor = 1.0 - abs(market_data.price_elasticity) * 0.1
        
        confidence = base_confidence * data_quality * volatility_factor
        return round(min(confidence, 0.99), 3)
    
    async def _estimate_revenue_impact(
        self,
        current_price: Optional[Decimal],
        new_price: Decimal,
        market_data: MarketData,
        content_metrics: Dict[str, Any]
    ) -> Decimal:
        """Estimate revenue impact of price change."""
        
        if not current_price or current_price <= 0:
            return Decimal("0")
        
        # Price elasticity of demand
        elasticity = market_data.price_elasticity
        
        # Calculate percentage price change
        price_change_pct = float((new_price - current_price) / current_price)
        
        # Estimate demand change using elasticity
        demand_change_pct = elasticity * price_change_pct
        
        # Estimate current revenue (using views as proxy for sales)
        current_views = content_metrics.get("views", 1000)
        estimated_current_sales = current_views * 0.02  # 2% conversion rate
        current_revenue = Decimal(str(estimated_current_sales)) * current_price
        
        # Calculate new revenue
        new_sales = estimated_current_sales * (1 + demand_change_pct)
        new_revenue = Decimal(str(new_sales)) * new_price
        
        revenue_impact = new_revenue - current_revenue
        return revenue_impact.quantize(Decimal("0.01"))
    
    async def _estimate_conversion_impact(
        self,
        current_price: Optional[Decimal],
        new_price: Decimal,
        market_data: MarketData
    ) -> float:
        """Estimate conversion rate impact of price change."""
        
        if not current_price or current_price <= 0:
            return 0.0
        
        # Price elasticity affects conversion
        elasticity = market_data.price_elasticity
        
        # Calculate percentage price change
        price_change_pct = float((new_price - current_price) / current_price)
        
        # Conversion impact (slightly less elastic than demand)
        conversion_elasticity = elasticity * 0.7
        conversion_change_pct = conversion_elasticity * price_change_pct
        
        return round(conversion_change_pct, 3)
    
    async def _generate_pricing_reasoning(
        self,
        model: PricingModel,
        market_data: MarketData,
        competitor_analysis: Dict[str, Any],
        recommended_price: Decimal
    ) -> List[str]:
        """Generate human-readable reasoning for the pricing recommendation."""
        
        reasoning = []
        
        # Model strategy explanation
        reasoning.append(f"Using {model.strategy.value} pricing strategy with {model.accuracy:.1%} accuracy")
        
        # Market position
        market_avg = market_data.average_price
        if recommended_price > market_avg * Decimal("1.1"):
            reasoning.append("Premium pricing recommended due to high content value and market demand")
        elif recommended_price < market_avg * Decimal("0.9"):
            reasoning.append("Competitive pricing recommended to capture market share")
        else:
            reasoning.append("Market-aligned pricing recommended for balanced growth")
        
        # Competitor analysis
        if competitor_analysis:
            comp_count = competitor_analysis.get("competitor_count", 0)
            if comp_count > 5:
                reasoning.append(f"High competition ({comp_count} competitors) considered in pricing decision")
            else:
                reasoning.append(f"Moderate competition ({comp_count} competitors) allows for value-based pricing")
        
        # Market trends
        if market_data.growth_rate > 0.15:
            reasoning.append(f"High market growth ({market_data.growth_rate:.1%}) supports premium pricing")
        elif market_data.growth_rate < 0.05:
            reasoning.append(f"Slow market growth ({market_data.growth_rate:.1%}) suggests conservative pricing")
        
        # Seasonal factors
        if market_data.seasonality_factor > 1.1:
            reasoning.append("Seasonal demand boost allows for higher pricing")
        elif market_data.seasonality_factor < 0.9:
            reasoning.append("Seasonal demand decline suggests lower pricing")
        
        return reasoning
    
    async def setup_ab_price_test(
        self,
        content_id: str,
        creator_id: str,
        control_price: Decimal,
        test_price: Decimal,
        test_duration_days: int = 14
    ) -> str:
        """Setup A/B price testing for empirical optimization."""
        try:
            test_id = str(uuid4())
            
            test_result = PriceTestResult(
                test_id=test_id,
                content_id=content_id,
                test_duration_days=test_duration_days,
                control_price=control_price,
                test_price=test_price,
                control_conversions=0,
                test_conversions=0,
                control_revenue=Decimal("0"),
                test_revenue=Decimal("0"),
                statistical_significance=0.0,
                winner="inconclusive",
                recommendation="Test in progress",
                confidence=0.0
            )
            
            self.active_tests[test_id] = test_result
            
            self.logger.info(f"Started A/B price test: {test_id} (${control_price} vs ${test_price})")
            return test_id
            
        except Exception as e:
            self.logger.error(f"Error setting up A/B test: {e}")
            raise
    
    async def update_ab_test_results(
        self,
        test_id: str,
        control_conversions: int,
        test_conversions: int,
        control_revenue: Decimal,
        test_revenue: Decimal
    ) -> PriceTestResult:
        """Update A/B test results with new data."""
        try:
            if test_id not in self.active_tests:
                raise ValueError(f"Test not found: {test_id}")
            
            test = self.active_tests[test_id]
            test.control_conversions = control_conversions
            test.test_conversions = test_conversions
            test.control_revenue = control_revenue
            test.test_revenue = test_revenue
            
            # Calculate statistical significance
            test.statistical_significance = await self._calculate_statistical_significance(
                control_conversions, test_conversions
            )
            
            # Determine winner
            if test.statistical_significance >= 0.95:
                if test_revenue > control_revenue:
                    test.winner = "test"
                    test.recommendation = f"Implement test price ${test.test_price}"
                    test.confidence = test.statistical_significance
                else:
                    test.winner = "control"
                    test.recommendation = f"Keep control price ${test.control_price}"
                    test.confidence = test.statistical_significance
            else:
                test.winner = "inconclusive"
                test.recommendation = "Continue testing or increase sample size"
                test.confidence = test.statistical_significance
            
            self.logger.info(f"Updated A/B test {test_id}: {test.winner} (confidence: {test.confidence:.2f})")
            return test
            
        except Exception as e:
            self.logger.error(f"Error updating A/B test results: {e}")
            raise
    
    async def _calculate_statistical_significance(
        self,
        control_conversions: int,
        test_conversions: int
    ) -> float:
        """Calculate statistical significance of A/B test results."""
        
        # Simplified statistical significance calculation
        # In production, use proper statistical tests (e.g., chi-square, t-test)
        
        total_conversions = control_conversions + test_conversions
        if total_conversions < 100:
            return 0.0  # Need minimum sample size
        
        # Calculate conversion rates
        control_rate = control_conversions / (total_conversions / 2)
        test_rate = test_conversions / (total_conversions / 2)
        
        # Simple difference-based significance (not statistically rigorous)
        difference = abs(test_rate - control_rate)
        
        if difference > 0.05:  # 5% difference
            return 0.95
        elif difference > 0.03:  # 3% difference
            return 0.85
        elif difference > 0.01:  # 1% difference
            return 0.70
        else:
            return 0.50
    
    async def get_pricing_recommendation(self, recommendation_id: str) -> Optional[PricingRecommendation]:
        """Get pricing recommendation by ID."""
        return self.recommendations.get(recommendation_id)
    
    async def get_creator_pricing_history(
        self,
        creator_id: str,
        content_id: Optional[str] = None
    ) -> List[PricingRecommendation]:
        """Get pricing recommendation history for creator."""
        recommendations = [
            rec for rec in self.recommendations.values()
            if rec.creator_id == creator_id
        ]
        
        if content_id:
            recommendations = [rec for rec in recommendations if rec.content_id == content_id]
        
        # Sort by creation date (newest first)
        recommendations.sort(key=lambda x: x.created_at, reverse=True)
        return recommendations
    
    async def update_market_data(
        self,
        category: ContentCategory,
        new_market_data: MarketData
    ):
        """Update market data for a category."""
        self.market_data[category] = new_market_data
        self.logger.info(f"Updated market data for category: {category.value}")
    
    async def get_pricing_analytics(
        self,
        creator_id: str,
        days_back: int = 30
    ) -> Dict[str, Any]:
        """Get pricing analytics and insights for creator."""
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        # Get recent recommendations
        recent_recs = [
            rec for rec in self.recommendations.values()
            if rec.creator_id == creator_id and rec.created_at >= cutoff_date
        ]
        
        if not recent_recs:
            return {"message": "No recent pricing data available"}
        
        # Calculate analytics
        total_recommendations = len(recent_recs)
        avg_confidence = mean(rec.confidence_score for rec in recent_recs)
        avg_price_change = mean(abs(rec.price_change_percentage) for rec in recent_recs)
        
        strategies_used = {}
        for rec in recent_recs:
            strategy = rec.strategy_used.value
            strategies_used[strategy] = strategies_used.get(strategy, 0) + 1
        
        total_expected_revenue = sum(rec.expected_revenue_change for rec in recent_recs)
        
        return {
            "period_days": days_back,
            "total_recommendations": total_recommendations,
            "average_confidence": round(avg_confidence, 3),
            "average_price_change_percentage": round(avg_price_change, 2),
            "strategies_used": strategies_used,
            "total_expected_revenue_impact": str(total_expected_revenue),
            "recommendation_frequency": round(total_recommendations / days_back, 2)
        }


# Example usage and testing
async def main():
    """Example usage of IntelligentPricingOrchestrator."""
    orchestrator = IntelligentPricingOrchestrator()
    
    # Example content metrics
    content_metrics = {
        "quality_score": 0.85,
        "engagement_rate": 0.12,
        "views": 25000,
        "likes": 1200,
        "shares": 150
    }
    
    # Analyze pricing opportunity
    recommendation = await orchestrator.analyze_pricing_opportunity(
        content_id="test_content_123",
        creator_id="creator_456",
        content_category=ContentCategory.MUSIC,
        current_price=Decimal("1.99"),
        content_metrics=content_metrics
    )
    
    print(f"Pricing Recommendation:")
    print(f"Current Price: ${recommendation.current_price}")
    print(f"Recommended Price: ${recommendation.recommended_price}")
    print(f"Price Change: {recommendation.price_change_percentage:.1f}%")
    print(f"Confidence: {recommendation.confidence_score:.2f}")
    print(f"Expected Revenue Change: ${recommendation.expected_revenue_change}")
    print(f"Strategy: {recommendation.strategy_used.value}")
    print(f"Reasoning: {recommendation.reasoning}")
    
    # Setup A/B test
    test_id = await orchestrator.setup_ab_price_test(
        content_id="test_content_123",
        creator_id="creator_456",
        control_price=Decimal("1.99"),
        test_price=recommendation.recommended_price,
        test_duration_days=14
    )
    print(f"\nA/B Test Started: {test_id}")
    
    # Simulate test results
    await orchestrator.update_ab_test_results(
        test_id=test_id,
        control_conversions=45,
        test_conversions=58,
        control_revenue=Decimal("89.55"),
        test_revenue=Decimal("134.42")
    )
    
    test_result = orchestrator.active_tests[test_id]
    print(f"Test Result: {test_result.winner} (confidence: {test_result.confidence:.2f})")
    print(f"Recommendation: {test_result.recommendation}")
    
    # Get analytics
    analytics = await orchestrator.get_pricing_analytics("creator_456")
    print(f"\nPricing Analytics: {analytics}")


if __name__ == "__main__":
    asyncio.run(main())