"""Price Optimizer - Machine Learning Price Optimization Engine
===========================================================

Advanced AI-powered price optimization system for marketplace transactions,
using machine learning to determine optimal pricing strategies and maximize revenue.

Features:
- Dynamic pricing based on market conditions and demand
- ML-based price prediction and optimization algorithms
- Real-time market analysis and competitor pricing
- Revenue optimization and profit margin calculations
- A/B testing framework for pricing strategies

Architecture: Enterprise Production-Ready (Backend Level 3)
Module: backend/marketplace/price_optimizer.py

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
import asyncio
import random
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
import uuid
import json
import statistics

logger = logging.getLogger(__name__)

class PricingStrategy(Enum):
    """Pricing strategy enumeration"""
    DYNAMIC = "dynamic"              # AI-driven dynamic pricing
    COMPETITIVE = "competitive"      # Competitor-based pricing
    VALUE_BASED = "value_based"      # Value-based pricing
    COST_PLUS = "cost_plus"         # Cost-plus pricing
    PENETRATION = "penetration"      # Market penetration pricing
    SKIMMING = "skimming"           # Price skimming
    PSYCHOLOGICAL = "psychological"  # Psychological pricing
    BUNDLE = "bundle"               # Bundle pricing
    AUCTION = "auction"             # Auction-based pricing

class MarketCondition(Enum):
    """Market condition enumeration"""
    HIGH_DEMAND = "high_demand"
    NORMAL_DEMAND = "normal_demand"
    LOW_DEMAND = "low_demand"
    SEASONAL_PEAK = "seasonal_peak"
    SEASONAL_LOW = "seasonal_low"
    TRENDING = "trending"
    SATURATED = "saturated"
    EMERGING = "emerging"

class PriceOptimizationGoal(Enum):
    """Price optimization goal"""
    MAXIMIZE_REVENUE = "maximize_revenue"
    MAXIMIZE_PROFIT = "maximize_profit"
    MAXIMIZE_VOLUME = "maximize_volume"
    MAXIMIZE_MARKET_SHARE = "maximize_market_share"
    TARGET_MARGIN = "target_margin"
    COMPETITIVE_POSITION = "competitive_position"

@dataclass
class PricingModel:
    """ML pricing model configuration"""
    model_id: str
    name: str
    algorithm: str  # "linear_regression", "random_forest", "neural_network", etc.
    features: List[str]
    target: str = "optimal_price"
    accuracy_score: float = 0.0
    last_trained: Optional[datetime] = None
    model_parameters: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MarketData:
    """Market data for pricing analysis"""
    data_id: str
    product_category: str
    timestamp: datetime
    demand_score: float  # 0.0 to 1.0
    competition_level: float  # 0.0 to 1.0
    market_condition: MarketCondition
    average_market_price: Decimal
    price_range_min: Decimal
    price_range_max: Decimal
    volume_trend: float  # -1.0 to 1.0 (negative = declining, positive = growing)
    seasonality_factor: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PriceOptimizationRequest:
    """Price optimization request"""
    request_id: str
    product_id: str
    product_category: str
    current_price: Decimal
    cost_price: Optional[Decimal] = None
    target_margin: Optional[float] = None
    optimization_goal: PriceOptimizationGoal = PriceOptimizationGoal.MAXIMIZE_REVENUE
    strategy: PricingStrategy = PricingStrategy.DYNAMIC
    constraints: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class PriceRecommendation:
    """Price optimization recommendation"""
    recommendation_id: str
    request_id: str
    product_id: str
    current_price: Decimal
    recommended_price: Decimal
    confidence_score: float  # 0.0 to 1.0
    expected_revenue_impact: float  # Percentage change
    expected_volume_impact: float  # Percentage change
    price_sensitivity: float  # Elasticity measure
    market_position: str  # "premium", "competitive", "discount"
    strategy_used: PricingStrategy
    reasoning: str = ""
    risk_assessment: str = "low"  # "low", "medium", "high"
    valid_until: Optional[datetime] = None
    a_b_test_candidate: bool = False
    generated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PriceTestResult:
    """A/B test result for pricing"""
    test_id: str
    product_id: str
    control_price: Decimal
    test_price: Decimal
    control_revenue: Decimal
    test_revenue: Decimal
    control_volume: int
    test_volume: int
    statistical_significance: float
    winner: str  # "control", "test", "inconclusive"
    lift_percentage: float
    test_duration_days: int
    completed_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

class PriceOptimizer:
    """Advanced ML-powered price optimization engine"""
    
    def __init__(self):
        self.pricing_models: Dict[str, PricingModel] = {}
        self.market_data: Dict[str, MarketData] = {}
        self.optimization_requests: Dict[str, PriceOptimizationRequest] = {}
        self.recommendations: Dict[str, PriceRecommendation] = {}
        self.price_tests: Dict[str, PriceTestResult] = {}
        self.historical_prices: Dict[str, List[Dict[str, Any]]] = {}
        
        # Initialize default models
        self._initialize_default_models()
    
    def _initialize_default_models(self):
        """Initialize default pricing models"""
        default_models = [
            PricingModel(
                model_id="demand_elasticity_model",
                name="Demand Elasticity Model",
                algorithm="linear_regression",
                features=["price", "demand_score", "competition_level", "seasonality"],
                target="sales_volume"
            ),
            PricingModel(
                model_id="revenue_optimization_model",
                name="Revenue Optimization Model",
                algorithm="random_forest",
                features=["price", "market_condition", "competitor_prices", "demand_trend"],
                target="revenue"
            ),
            PricingModel(
                model_id="competitive_positioning_model",
                name="Competitive Positioning Model",
                algorithm="neural_network",
                features=["competitor_prices", "market_share", "brand_strength", "quality_score"],
                target="optimal_price_position"
            )
        ]
        
        for model in default_models:
            self.pricing_models[model.model_id] = model
    
    async def optimize_price(
        self,
        product_id: str,
        product_category: str,
        current_price: Decimal,
        cost_price: Optional[Decimal] = None,
        optimization_goal: PriceOptimizationGoal = PriceOptimizationGoal.MAXIMIZE_REVENUE,
        strategy: PricingStrategy = PricingStrategy.DYNAMIC,
        constraints: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> PriceRecommendation:
        """Generate optimal price recommendation"""
        try:
            request_id = f"price_req_{uuid.uuid4().hex[:12]}"
            
            # Create optimization request
            request = PriceOptimizationRequest(
                request_id=request_id,
                product_id=product_id,
                product_category=product_category,
                current_price=current_price,
                cost_price=cost_price,
                optimization_goal=optimization_goal,
                strategy=strategy,
                constraints=constraints or {},
                context=context or {}
            )
            
            self.optimization_requests[request_id] = request
            
            # Gather market data
            market_data = await self._gather_market_data(product_category)
            
            # Apply pricing strategy
            if strategy == PricingStrategy.DYNAMIC:
                recommendation = await self._dynamic_pricing(request, market_data)
            elif strategy == PricingStrategy.COMPETITIVE:
                recommendation = await self._competitive_pricing(request, market_data)
            elif strategy == PricingStrategy.VALUE_BASED:
                recommendation = await self._value_based_pricing(request, market_data)
            elif strategy == PricingStrategy.PSYCHOLOGICAL:
                recommendation = await self._psychological_pricing(request, market_data)
            else:
                recommendation = await self._default_pricing(request, market_data)
            
            # Apply constraints
            recommendation = await self._apply_constraints(recommendation, request.constraints)
            
            # Calculate risk assessment
            recommendation.risk_assessment = await self._assess_price_risk(recommendation, market_data)
            
            # Set validity period
            recommendation.valid_until = datetime.utcnow() + timedelta(hours=24)
            
            # Determine if A/B test candidate
            recommendation.a_b_test_candidate = await self._should_ab_test(recommendation)
            
            self.recommendations[recommendation.recommendation_id] = recommendation
            
            logger.info(f"Price optimization completed: {product_id} -> {recommendation.recommended_price}")
            return recommendation
            
        except Exception as e:
            logger.error(f"Error optimizing price: {e}")
            raise
    
    async def _gather_market_data(self, product_category: str) -> MarketData:
        """Gather and analyze market data"""
        data_id = f"market_{uuid.uuid4().hex[:12]}"
        
        # Mock market data - in production would fetch from real market sources
        market_data = MarketData(
            data_id=data_id,
            product_category=product_category,
            timestamp=datetime.utcnow(),
            demand_score=random.uniform(0.3, 0.9),  # Random for demo
            competition_level=random.uniform(0.2, 0.8),
            market_condition=random.choice(list(MarketCondition)),
            average_market_price=Decimal(str(random.uniform(50, 500))),
            price_range_min=Decimal(str(random.uniform(20, 100))),
            price_range_max=Decimal(str(random.uniform(200, 1000))),
            volume_trend=random.uniform(-0.3, 0.5),
            seasonality_factor=random.uniform(0.8, 1.3)
        )
        
        self.market_data[data_id] = market_data
        return market_data
    
    async def _dynamic_pricing(
        self,
        request: PriceOptimizationRequest,
        market_data: MarketData
    ) -> PriceRecommendation:
        """Apply dynamic pricing strategy using ML"""
        # Simulate ML model prediction
        features = {
            "current_price": float(request.current_price),
            "demand_score": market_data.demand_score,
            "competition_level": market_data.competition_level,
            "market_condition": self._encode_market_condition(market_data.market_condition),
            "seasonality": market_data.seasonality_factor,
            "volume_trend": market_data.volume_trend
        }
        
        # ML prediction (simplified)
        price_multiplier = await self._predict_optimal_multiplier(features, request.optimization_goal)
        recommended_price = request.current_price * Decimal(str(price_multiplier))
        
        # Calculate expected impacts
        revenue_impact = await self._calculate_revenue_impact(
            request.current_price, recommended_price, market_data
        )
        volume_impact = await self._calculate_volume_impact(
            request.current_price, recommended_price, market_data
        )
        
        # Calculate price sensitivity
        price_sensitivity = await self._calculate_price_sensitivity(market_data)
        
        # Determine market position
        market_position = await self._determine_market_position(
            recommended_price, market_data.average_market_price
        )
        
        # Generate reasoning
        reasoning = f"Dynamic pricing based on {market_data.market_condition.value} market conditions. "
        reasoning += f"Demand score: {market_data.demand_score:.2f}, "
        reasoning += f"Competition level: {market_data.competition_level:.2f}"
        
        recommendation = PriceRecommendation(
            recommendation_id=f"rec_{uuid.uuid4().hex[:12]}",
            request_id=request.request_id,
            product_id=request.product_id,
            current_price=request.current_price,
            recommended_price=recommended_price,
            confidence_score=0.85,  # Would be calculated by ML model
            expected_revenue_impact=revenue_impact,
            expected_volume_impact=volume_impact,
            price_sensitivity=price_sensitivity,
            market_position=market_position,
            strategy_used=PricingStrategy.DYNAMIC,
            reasoning=reasoning
        )
        
        return recommendation
    
    async def _competitive_pricing(
        self,
        request: PriceOptimizationRequest,
        market_data: MarketData
    ) -> PriceRecommendation:
        """Apply competitive pricing strategy"""
        # Position relative to market average
        if request.optimization_goal == PriceOptimizationGoal.MAXIMIZE_MARKET_SHARE:
            # Price below market average
            recommended_price = market_data.average_market_price * Decimal("0.95")
            market_position = "competitive"
        elif request.optimization_goal == PriceOptimizationGoal.MAXIMIZE_PROFIT:
            # Price slightly above market average
            recommended_price = market_data.average_market_price * Decimal("1.05")
            market_position = "premium"
        else:
            # Match market average
            recommended_price = market_data.average_market_price
            market_position = "competitive"
        
        revenue_impact = await self._calculate_revenue_impact(
            request.current_price, recommended_price, market_data
        )
        volume_impact = await self._calculate_volume_impact(
            request.current_price, recommended_price, market_data
        )
        
        reasoning = f"Competitive positioning at {market_position} level relative to market average of {market_data.average_market_price}"
        
        return PriceRecommendation(
            recommendation_id=f"rec_{uuid.uuid4().hex[:12]}",
            request_id=request.request_id,
            product_id=request.product_id,
            current_price=request.current_price,
            recommended_price=recommended_price,
            confidence_score=0.75,
            expected_revenue_impact=revenue_impact,
            expected_volume_impact=volume_impact,
            price_sensitivity=await self._calculate_price_sensitivity(market_data),
            market_position=market_position,
            strategy_used=PricingStrategy.COMPETITIVE,
            reasoning=reasoning
        )
    
    async def _value_based_pricing(
        self,
        request: PriceOptimizationRequest,
        market_data: MarketData
    ) -> PriceRecommendation:
        """Apply value-based pricing strategy"""
        # Value-based pricing considers customer perceived value
        value_multiplier = 1.0
        
        # Adjust based on market conditions
        if market_data.market_condition == MarketCondition.HIGH_DEMAND:
            value_multiplier = 1.2
        elif market_data.market_condition == MarketCondition.LOW_DEMAND:
            value_multiplier = 0.9
        elif market_data.market_condition == MarketCondition.TRENDING:
            value_multiplier = 1.15
        
        # Adjust based on competition
        if market_data.competition_level < 0.3:
            value_multiplier *= 1.1  # Low competition, can charge more
        elif market_data.competition_level > 0.7:
            value_multiplier *= 0.95  # High competition, need to be competitive
        
        recommended_price = request.current_price * Decimal(str(value_multiplier))
        
        revenue_impact = await self._calculate_revenue_impact(
            request.current_price, recommended_price, market_data
        )
        volume_impact = await self._calculate_volume_impact(
            request.current_price, recommended_price, market_data
        )
        
        market_position = "premium" if value_multiplier > 1.05 else "competitive"
        reasoning = f"Value-based pricing considering {market_data.market_condition.value} conditions and {market_data.competition_level:.1%} competition level"
        
        return PriceRecommendation(
            recommendation_id=f"rec_{uuid.uuid4().hex[:12]}",
            request_id=request.request_id,
            product_id=request.product_id,
            current_price=request.current_price,
            recommended_price=recommended_price,
            confidence_score=0.70,
            expected_revenue_impact=revenue_impact,
            expected_volume_impact=volume_impact,
            price_sensitivity=await self._calculate_price_sensitivity(market_data),
            market_position=market_position,
            strategy_used=PricingStrategy.VALUE_BASED,
            reasoning=reasoning
        )
    
    async def _psychological_pricing(
        self,
        request: PriceOptimizationRequest,
        market_data: MarketData
    ) -> PriceRecommendation:
        """Apply psychological pricing strategy"""
        # Start with value-based price
        base_rec = await self._value_based_pricing(request, market_data)
        
        # Apply psychological pricing rules
        recommended_price = self._apply_psychological_rules(base_rec.recommended_price)
        
        reasoning = f"Psychological pricing applied to value-based recommendation. "
        reasoning += "Price adjusted for psychological appeal (e.g., ending in .99)"
        
        return PriceRecommendation(
            recommendation_id=f"rec_{uuid.uuid4().hex[:12]}",
            request_id=request.request_id,
            product_id=request.product_id,
            current_price=request.current_price,
            recommended_price=recommended_price,
            confidence_score=0.65,
            expected_revenue_impact=base_rec.expected_revenue_impact,
            expected_volume_impact=base_rec.expected_volume_impact + 5.0,  # Boost from psychological pricing
            price_sensitivity=base_rec.price_sensitivity,
            market_position=base_rec.market_position,
            strategy_used=PricingStrategy.PSYCHOLOGICAL,
            reasoning=reasoning
        )
    
    def _apply_psychological_rules(self, price: Decimal) -> Decimal:
        """Apply psychological pricing rules"""
        price_float = float(price)
        
        # Apply .99 ending for prices under 1000
        if price_float < 1000:
            # Round to nearest dollar and subtract 0.01
            rounded_price = round(price_float)
            if rounded_price > price_float:
                return Decimal(str(rounded_price - 0.01))
            else:
                return Decimal(str(rounded_price + 0.99))
        else:
            # For higher prices, use round numbers ending in 5 or 0
            rounded_price = round(price_float / 10) * 10
            if rounded_price % 10 == 0:
                return Decimal(str(rounded_price - 5))
            else:
                return Decimal(str(rounded_price))
    
    async def _default_pricing(
        self,
        request: PriceOptimizationRequest,
        market_data: MarketData
    ) -> PriceRecommendation:
        """Apply default pricing strategy"""
        # Simple cost-plus if cost is available
        if request.cost_price:
            target_margin = request.target_margin or 0.3  # 30% default margin
            recommended_price = request.cost_price * Decimal(str(1 + target_margin))
        else:
            # Small adjustment based on market conditions
            if market_data.demand_score > 0.7:
                recommended_price = request.current_price * Decimal("1.05")
            elif market_data.demand_score < 0.4:
                recommended_price = request.current_price * Decimal("0.95")
            else:
                recommended_price = request.current_price
        
        return PriceRecommendation(
            recommendation_id=f"rec_{uuid.uuid4().hex[:12]}",
            request_id=request.request_id,
            product_id=request.product_id,
            current_price=request.current_price,
            recommended_price=recommended_price,
            confidence_score=0.50,
            expected_revenue_impact=0.0,
            expected_volume_impact=0.0,
            price_sensitivity=0.5,
            market_position="competitive",
            strategy_used=PricingStrategy.COST_PLUS,
            reasoning="Default pricing strategy applied"
        )
    
    async def _predict_optimal_multiplier(
        self,
        features: Dict[str, float],
        goal: PriceOptimizationGoal
    ) -> float:
        """Predict optimal price multiplier using ML (simulated)"""
        # Simplified ML prediction - in production would use trained models
        base_multiplier = 1.0
        
        # Adjust based on demand
        demand_adjustment = (features["demand_score"] - 0.5) * 0.2
        base_multiplier += demand_adjustment
        
        # Adjust based on competition
        competition_adjustment = (0.5 - features["competition_level"]) * 0.15
        base_multiplier += competition_adjustment
        
        # Adjust based on optimization goal
        if goal == PriceOptimizationGoal.MAXIMIZE_REVENUE:
            base_multiplier *= 1.05
        elif goal == PriceOptimizationGoal.MAXIMIZE_VOLUME:
            base_multiplier *= 0.95
        elif goal == PriceOptimizationGoal.MAXIMIZE_PROFIT:
            base_multiplier *= 1.1
        
        # Apply bounds
        return max(0.7, min(1.5, base_multiplier))
    
    async def _calculate_revenue_impact(
        self,
        current_price: Decimal,
        new_price: Decimal,
        market_data: MarketData
    ) -> float:
        """Calculate expected revenue impact percentage"""
        price_change = float((new_price - current_price) / current_price)
        
        # Simple elasticity model
        price_elasticity = market_data.demand_score * -1.5  # Higher demand = less elastic
        volume_change = price_change * price_elasticity
        
        # Revenue impact = (1 + price_change) * (1 + volume_change) - 1
        revenue_impact = (1 + price_change) * (1 + volume_change) - 1
        
        return revenue_impact * 100  # Return as percentage
    
    async def _calculate_volume_impact(
        self,
        current_price: Decimal,
        new_price: Decimal,
        market_data: MarketData
    ) -> float:
        """Calculate expected volume impact percentage"""
        price_change = float((new_price - current_price) / current_price)
        
        # Volume impact based on price elasticity
        price_elasticity = market_data.demand_score * -1.2
        volume_impact = price_change * price_elasticity
        
        return volume_impact * 100  # Return as percentage
    
    async def _calculate_price_sensitivity(self, market_data: MarketData) -> float:
        """Calculate price sensitivity measure"""
        # Higher competition and lower demand = higher price sensitivity
        base_sensitivity = 0.5
        competition_factor = market_data.competition_level * 0.3
        demand_factor = (1 - market_data.demand_score) * 0.2
        
        return min(1.0, base_sensitivity + competition_factor + demand_factor)
    
    async def _determine_market_position(
        self,
        recommended_price: Decimal,
        market_average: Decimal
    ) -> str:
        """Determine market position based on price relative to market"""
        ratio = float(recommended_price / market_average)
        
        if ratio > 1.1:
            return "premium"
        elif ratio < 0.9:
            return "discount"
        else:
            return "competitive"
    
    def _encode_market_condition(self, condition: MarketCondition) -> float:
        """Encode market condition as numerical value"""
        encoding = {
            MarketCondition.HIGH_DEMAND: 0.9,
            MarketCondition.NORMAL_DEMAND: 0.5,
            MarketCondition.LOW_DEMAND: 0.1,
            MarketCondition.SEASONAL_PEAK: 0.8,
            MarketCondition.SEASONAL_LOW: 0.2,
            MarketCondition.TRENDING: 0.85,
            MarketCondition.SATURATED: 0.3,
            MarketCondition.EMERGING: 0.7
        }
        return encoding.get(condition, 0.5)
    
    async def _apply_constraints(
        self,
        recommendation: PriceRecommendation,
        constraints: Dict[str, Any]
    ) -> PriceRecommendation:
        """Apply pricing constraints to recommendation"""
        if not constraints:
            return recommendation
        
        adjusted_price = recommendation.recommended_price
        
        # Apply minimum price constraint
        if "min_price" in constraints:
            min_price = Decimal(str(constraints["min_price"]))
            adjusted_price = max(adjusted_price, min_price)
        
        # Apply maximum price constraint
        if "max_price" in constraints:
            max_price = Decimal(str(constraints["max_price"]))
            adjusted_price = min(adjusted_price, max_price)
        
        # Apply maximum change constraint
        if "max_change_percent" in constraints:
            max_change = float(constraints["max_change_percent"]) / 100
            current_price = recommendation.current_price
            max_increase = current_price * Decimal(str(1 + max_change))
            max_decrease = current_price * Decimal(str(1 - max_change))
            adjusted_price = max(max_decrease, min(max_increase, adjusted_price))
        
        # Update recommendation if price was adjusted
        if adjusted_price != recommendation.recommended_price:
            recommendation.recommended_price = adjusted_price
            recommendation.confidence_score *= 0.9  # Reduce confidence due to constraints
            recommendation.reasoning += " (Adjusted for constraints)"
        
        return recommendation
    
    async def _assess_price_risk(
        self,
        recommendation: PriceRecommendation,
        market_data: MarketData
    ) -> str:
        """Assess risk level of price recommendation"""
        risk_factors = 0
        
        # Large price changes are risky
        price_change = abs(float((recommendation.recommended_price - recommendation.current_price) / recommendation.current_price))
        if price_change > 0.2:
            risk_factors += 2
        elif price_change > 0.1:
            risk_factors += 1
        
        # High competition increases risk
        if market_data.competition_level > 0.7:
            risk_factors += 1
        
        # Low demand increases risk of price increases
        if market_data.demand_score < 0.3 and recommendation.recommended_price > recommendation.current_price:
            risk_factors += 1
        
        # Market volatility
        if market_data.volume_trend < -0.2:
            risk_factors += 1
        
        if risk_factors >= 3:
            return "high"
        elif risk_factors >= 2:
            return "medium"
        else:
            return "low"
    
    async def _should_ab_test(self, recommendation: PriceRecommendation) -> bool:
        """Determine if recommendation should be A/B tested"""
        # A/B test for significant price changes with medium confidence
        price_change = abs(float((recommendation.recommended_price - recommendation.current_price) / recommendation.current_price))
        
        return (price_change > 0.05 and 
                recommendation.confidence_score < 0.9 and 
                recommendation.risk_assessment != "low")
    
    async def create_ab_test(
        self,
        recommendation_id: str,
        test_duration_days: int = 14,
        traffic_split: float = 0.5
    ) -> str:
        """Create A/B test for price recommendation"""
        try:
            recommendation = self.recommendations.get(recommendation_id)
            if not recommendation:
                raise ValueError(f"Recommendation {recommendation_id} not found")
            
            test_id = f"test_{uuid.uuid4().hex[:12]}"
            
            # In production, would set up actual A/B test infrastructure
            logger.info(f"A/B test created: {test_id} for product {recommendation.product_id}")
            
            return test_id
            
        except Exception as e:
            logger.error(f"Error creating A/B test: {e}")
            raise
    
    async def analyze_ab_test(self, test_id: str) -> PriceTestResult:
        """Analyze A/B test results"""
        try:
            # Mock test results - in production would fetch actual test data
            control_revenue = Decimal(str(random.uniform(10000, 15000)))
            test_revenue = Decimal(str(random.uniform(9000, 16000)))
            control_volume = int(random.uniform(100, 200))
            test_volume = int(random.uniform(90, 210))
            
            # Statistical significance (simplified)
            revenue_lift = float((test_revenue - control_revenue) / control_revenue * 100)
            statistical_significance = min(0.99, abs(revenue_lift) / 10)  # Simplified calculation
            
            winner = "test" if test_revenue > control_revenue and statistical_significance > 0.8 else \
                    "control" if control_revenue > test_revenue and statistical_significance > 0.8 else \
                    "inconclusive"
            
            result = PriceTestResult(
                test_id=test_id,
                product_id=f"product_{uuid.uuid4().hex[:8]}",
                control_price=Decimal("100.00"),
                test_price=Decimal("105.00"),
                control_revenue=control_revenue,
                test_revenue=test_revenue,
                control_volume=control_volume,
                test_volume=test_volume,
                statistical_significance=statistical_significance,
                winner=winner,
                lift_percentage=revenue_lift,
                test_duration_days=14
            )
            
            self.price_tests[test_id] = result
            
            logger.info(f"A/B test analyzed: {test_id} - Winner: {winner}")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing A/B test: {e}")
            raise
    
    def get_recommendation(self, recommendation_id: str) -> Optional[PriceRecommendation]:
        """Get price recommendation by ID"""
        return self.recommendations.get(recommendation_id)
    
    def get_test_result(self, test_id: str) -> Optional[PriceTestResult]:
        """Get A/B test result by ID"""
        return self.price_tests.get(test_id)
    
    async def get_pricing_analytics(self) -> Dict[str, Any]:
        """Get pricing analytics and insights"""
        total_recommendations = len(self.recommendations)
        
        if total_recommendations == 0:
            return {"total_recommendations": 0}
        
        # Calculate average confidence
        avg_confidence = statistics.mean(
            rec.confidence_score for rec in self.recommendations.values()
        )
        
        # Strategy breakdown
        strategy_breakdown = {}
        for rec in self.recommendations.values():
            strategy = rec.strategy_used.value
            strategy_breakdown[strategy] = strategy_breakdown.get(strategy, 0) + 1
        
        # Risk distribution
        risk_distribution = {}
        for rec in self.recommendations.values():
            risk = rec.risk_assessment
            risk_distribution[risk] = risk_distribution.get(risk, 0) + 1
        
        # Price change distribution
        price_changes = []
        for rec in self.recommendations.values():
            change = float((rec.recommended_price - rec.current_price) / rec.current_price * 100)
            price_changes.append(change)
        
        avg_price_change = statistics.mean(price_changes) if price_changes else 0
        
        return {
            "total_recommendations": total_recommendations,
            "average_confidence": avg_confidence,
            "average_price_change_percent": avg_price_change,
            "strategy_breakdown": strategy_breakdown,
            "risk_distribution": risk_distribution,
            "ab_tests_completed": len(self.price_tests),
            "models_available": len(self.pricing_models)
        }

# Example usage
async def main():
    """Example usage of PriceOptimizer"""
    optimizer = PriceOptimizer()
    
    # Optimize price for a product
    recommendation = await optimizer.optimize_price(
        product_id="product_123",
        product_category="digital_content",
        current_price=Decimal("100.00"),
        cost_price=Decimal("60.00"),
        optimization_goal=PriceOptimizationGoal.MAXIMIZE_REVENUE,
        strategy=PricingStrategy.DYNAMIC,
        constraints={"min_price": 80.00, "max_price": 150.00}
    )
    
    print(f"Price recommendation: ${recommendation.recommended_price}")
    print(f"Expected revenue impact: {recommendation.expected_revenue_impact:.1f}%")
    print(f"Confidence: {recommendation.confidence_score:.2f}")
    print(f"Risk level: {recommendation.risk_assessment}")
    
    # Create A/B test if recommended
    if recommendation.a_b_test_candidate:
        test_id = await optimizer.create_ab_test(recommendation.recommendation_id)
        print(f"A/B test created: {test_id}")
    
    # Get analytics
    analytics = await optimizer.get_pricing_analytics()
    print(f"Pricing analytics: {analytics}")

if __name__ == "__main__":
    asyncio.run(main())