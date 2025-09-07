"""Dynamic Pricing AI Engine - IA Dynamic Pricing Engine
======================================================

Enterprise-grade AI-powered dynamic pricing engine providing intelligent
real-time pricing optimization, market-based pricing strategies, and
automated price adjustments using advanced machine learning algorithms.

Architecture: Enterprise Production-Ready (Backend Level 3)
Module: backend/monetization/dynamic_pricing_ai_engine.py

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
    """Dynamic pricing strategies."""
    DEMAND_BASED = "demand_based"
    COMPETITION_BASED = "competition_based"
    VALUE_BASED = "value_based"
    TIME_BASED = "time_based"
    INVENTORY_BASED = "inventory_based"
    CUSTOMER_BASED = "customer_based"
    HYBRID = "hybrid"


class PriceAdjustmentReason(str, Enum):
    """Reasons for price adjustments."""
    HIGH_DEMAND = "high_demand"
    LOW_DEMAND = "low_demand"
    COMPETITOR_CHANGE = "competitor_change"
    SEASONAL_TREND = "seasonal_trend"
    INVENTORY_LEVEL = "inventory_level"
    CUSTOMER_SEGMENT = "customer_segment"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    MARKET_CONDITIONS = "market_conditions"


class PriceChangeDirection(str, Enum):
    """Direction of price changes."""
    INCREASE = "increase"
    DECREASE = "decrease"
    MAINTAIN = "maintain"


@dataclass
class PricingRule:
    """Dynamic pricing rule definition."""
    rule_id: str
    name: str
    strategy: PricingStrategy
    conditions: Dict[str, Any]
    min_price: Decimal
    max_price: Decimal
    base_price: Decimal
    adjustment_percentage: float
    priority: int
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class PriceRecommendation:
    """AI-generated price recommendation."""
    recommendation_id: str
    product_id: str
    current_price: Decimal
    recommended_price: Decimal
    price_change: Decimal
    change_direction: PriceChangeDirection
    change_percentage: float
    strategy_used: PricingStrategy
    adjustment_reason: PriceAdjustmentReason
    confidence_score: float
    expected_revenue_impact: Decimal
    expected_demand_change: float
    market_data: Dict[str, Any]
    ai_reasoning: str
    valid_until: datetime
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class MarketData:
    """Market data for pricing decisions."""
    competitor_prices: Dict[str, Decimal]
    demand_indicators: Dict[str, float]
    seasonal_factors: Dict[str, float]
    economic_indicators: Dict[str, float]
    customer_segments: Dict[str, Dict[str, Any]]
    inventory_levels: Dict[str, int]
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class PricingPerformance:
    """Pricing performance metrics."""
    product_id: str
    period_start: datetime
    period_end: datetime
    price_changes: int
    average_price: Decimal
    revenue_generated: Decimal
    units_sold: int
    conversion_rate: float
    price_elasticity: float
    competitor_comparison: Dict[str, Any]
    customer_satisfaction: float


class DynamicPricingAIEngine:
    """
    Advanced AI-powered dynamic pricing engine.
    
    Provides real-time pricing optimization using machine learning
    algorithms and market intelligence.
    """
    
    def __init__(self):
        """Initialize the dynamic pricing AI engine."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.pricing_rules: Dict[str, PricingRule] = {}
        self.price_history: Dict[str, List[PriceRecommendation]] = {}
        self.market_data_cache: Dict[str, MarketData] = {}
        self.performance_metrics: Dict[str, List[PricingPerformance]] = {}
        self.active_prices: Dict[str, Decimal] = {}
        self.initialized = False
        
        # AI model parameters
        self.demand_elasticity_models: Dict[str, Any] = {}
        self.market_prediction_models: Dict[str, Any] = {}
        self.price_optimization_models: Dict[str, Any] = {}
        
        self.logger.info("DynamicPricingAIEngine initialized")
    
    async def initialize(self) -> bool:
        """Initialize the dynamic pricing AI engine."""
        try:
            await self._load_pricing_models()
            await self._load_market_intelligence()
            await self._initialize_pricing_rules()
            
            self.initialized = True
            self.logger.info("DynamicPricingAIEngine initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize DynamicPricingAIEngine: {e}")
            return False
    
    async def _load_pricing_models(self):
        """Load AI pricing models."""
        # In production, this would load trained ML models
        self.demand_elasticity_models = {
            "subscription": {"elasticity": -1.2, "confidence": 0.85},
            "course": {"elasticity": -0.8, "confidence": 0.78},
            "merchandise": {"elasticity": -1.5, "confidence": 0.92},
            "digital_content": {"elasticity": -2.1, "confidence": 0.88}
        }
        
        self.logger.info("AI pricing models loaded")
    
    async def _load_market_intelligence(self):
        """Load market intelligence data."""
        # Sample market intelligence
        self.market_intelligence = {
            "competitor_tracking": {
                "update_frequency": "hourly",
                "confidence": 0.9,
                "coverage": 0.85
            },
            "demand_indicators": {
                "social_signals": 0.7,
                "search_trends": 0.8,
                "economic_factors": 0.6
            },
            "seasonal_patterns": {
                "q1": 0.9, "q2": 1.0, "q3": 1.1, "q4": 1.3
            }
        }
        
        self.logger.info("Market intelligence loaded")
    
    async def _initialize_pricing_rules(self):
        """Initialize default pricing rules."""
        default_rules = [
            PricingRule(
                rule_id="demand_surge",
                name="Demand Surge Pricing",
                strategy=PricingStrategy.DEMAND_BASED,
                conditions={"demand_increase": 0.3, "capacity_utilization": 0.8},
                min_price=Decimal("5.00"),
                max_price=Decimal("500.00"),
                base_price=Decimal("50.00"),
                adjustment_percentage=0.2,
                priority=1
            ),
            PricingRule(
                rule_id="competitor_match",
                name="Competitive Pricing",
                strategy=PricingStrategy.COMPETITION_BASED,
                conditions={"competitor_price_change": 0.1, "market_share": 0.3},
                min_price=Decimal("5.00"),
                max_price=Decimal("500.00"),
                base_price=Decimal("50.00"),
                adjustment_percentage=0.15,
                priority=2
            ),
            PricingRule(
                rule_id="seasonal_adjustment",
                name="Seasonal Pricing",
                strategy=PricingStrategy.TIME_BASED,
                conditions={"seasonal_factor": 0.2},
                min_price=Decimal("5.00"),
                max_price=Decimal("500.00"),
                base_price=Decimal("50.00"),
                adjustment_percentage=0.25,
                priority=3
            )
        ]
        
        for rule in default_rules:
            self.pricing_rules[rule.rule_id] = rule
        
        self.logger.info(f"Initialized {len(default_rules)} default pricing rules")
    
    async def get_price_recommendation(
        self,
        product_id: str,
        current_price: Decimal,
        market_data: Optional[MarketData] = None,
        strategy: Optional[PricingStrategy] = None
    ) -> PriceRecommendation:
        """Get AI-powered price recommendation for a product."""
        try:
            if not self.initialized:
                await self.initialize()
            
            # Get or generate market data
            if market_data is None:
                market_data = await self._collect_market_data(product_id)
            
            # Determine optimal pricing strategy
            if strategy is None:
                strategy = await self._select_optimal_strategy(product_id, market_data)
            
            # Calculate recommended price
            recommended_price = await self._calculate_optimal_price(
                product_id, current_price, market_data, strategy
            )
            
            # Calculate price change metrics
            price_change = recommended_price - current_price
            change_percentage = float(price_change / current_price * 100) if current_price > 0 else 0
            change_direction = (
                PriceChangeDirection.INCREASE if price_change > 0 
                else PriceChangeDirection.DECREASE if price_change < 0 
                else PriceChangeDirection.MAINTAIN
            )
            
            # Determine adjustment reason
            adjustment_reason = await self._determine_adjustment_reason(market_data, strategy)
            
            # Calculate confidence and impact
            confidence_score = await self._calculate_confidence(product_id, strategy, market_data)
            revenue_impact = await self._estimate_revenue_impact(
                product_id, current_price, recommended_price, market_data
            )
            demand_change = await self._estimate_demand_change(
                product_id, current_price, recommended_price
            )
            
            # Generate AI reasoning
            ai_reasoning = await self._generate_pricing_reasoning(
                product_id, current_price, recommended_price, strategy, market_data
            )
            
            recommendation = PriceRecommendation(
                recommendation_id=str(uuid4()),
                product_id=product_id,
                current_price=current_price,
                recommended_price=recommended_price,
                price_change=price_change,
                change_direction=change_direction,
                change_percentage=change_percentage,
                strategy_used=strategy,
                adjustment_reason=adjustment_reason,
                confidence_score=confidence_score,
                expected_revenue_impact=revenue_impact,
                expected_demand_change=demand_change,
                market_data=await self._serialize_market_data(market_data),
                ai_reasoning=ai_reasoning,
                valid_until=datetime.now() + timedelta(hours=24)
            )
            
            # Store recommendation
            if product_id not in self.price_history:
                self.price_history[product_id] = []
            self.price_history[product_id].append(recommendation)
            
            self.logger.info(f"Generated price recommendation for {product_id}: ${current_price} → ${recommended_price}")
            return recommendation
            
        except Exception as e:
            self.logger.error(f"Error generating price recommendation for {product_id}: {e}")
            raise
    
    async def _collect_market_data(self, product_id: str) -> MarketData:
        """Collect current market data for pricing decisions."""
        # In production, this would collect real market data
        # For now, return simulated market data
        
        import random
        
        return MarketData(
            competitor_prices={
                "competitor_1": Decimal(str(40 + random.random() * 20)),
                "competitor_2": Decimal(str(45 + random.random() * 15)),
                "competitor_3": Decimal(str(35 + random.random() * 25))
            },
            demand_indicators={
                "search_volume": 0.7 + random.random() * 0.3,
                "social_engagement": 0.6 + random.random() * 0.4,
                "website_traffic": 0.8 + random.random() * 0.2,
                "conversion_rate": 0.02 + random.random() * 0.03
            },
            seasonal_factors={
                "current_season": 1.0 + random.random() * 0.3,
                "holiday_effect": 0.9 + random.random() * 0.4,
                "market_cycle": 0.95 + random.random() * 0.1
            },
            economic_indicators={
                "consumer_confidence": 0.7 + random.random() * 0.2,
                "disposable_income": 0.8 + random.random() * 0.15,
                "market_volatility": 0.1 + random.random() * 0.2
            },
            customer_segments={
                "premium": {"price_sensitivity": 0.3, "demand_share": 0.2},
                "mainstream": {"price_sensitivity": 0.7, "demand_share": 0.6},
                "budget": {"price_sensitivity": 0.9, "demand_share": 0.2}
            },
            inventory_levels={
                "current_stock": 100,
                "reorder_point": 20,
                "lead_time_days": 7
            }
        )
    
    async def _select_optimal_strategy(self, product_id: str, market_data: MarketData) -> PricingStrategy:
        """Select optimal pricing strategy based on market conditions."""
        strategy_scores = {}
        
        # Analyze market conditions for strategy selection
        competitor_variance = self._calculate_price_variance(market_data.competitor_prices)
        demand_strength = mean(market_data.demand_indicators.values())
        seasonal_factor = market_data.seasonal_factors.get("current_season", 1.0)
        
        # Score different strategies
        strategy_scores[PricingStrategy.DEMAND_BASED] = demand_strength * 0.8
        strategy_scores[PricingStrategy.COMPETITION_BASED] = (1 - competitor_variance) * 0.7
        strategy_scores[PricingStrategy.TIME_BASED] = abs(seasonal_factor - 1.0) * 0.6
        strategy_scores[PricingStrategy.VALUE_BASED] = demand_strength * 0.9
        
        # Select strategy with highest score
        optimal_strategy = max(strategy_scores, key=strategy_scores.get)
        
        self.logger.debug(f"Selected {optimal_strategy.value} strategy for {product_id}")
        return optimal_strategy
    
    def _calculate_price_variance(self, competitor_prices: Dict[str, Decimal]) -> float:
        """Calculate price variance among competitors."""
        if len(competitor_prices) < 2:
            return 0.0
        
        prices = [float(price) for price in competitor_prices.values()]
        avg_price = mean(prices)
        
        if avg_price == 0:
            return 1.0
        
        variance = stdev(prices) / avg_price
        return min(variance, 1.0)
    
    async def _calculate_optimal_price(
        self,
        product_id: str,
        current_price: Decimal,
        market_data: MarketData,
        strategy: PricingStrategy
    ) -> Decimal:
        """Calculate optimal price using selected strategy."""
        
        if strategy == PricingStrategy.DEMAND_BASED:
            return await self._calculate_demand_based_price(product_id, current_price, market_data)
        
        elif strategy == PricingStrategy.COMPETITION_BASED:
            return await self._calculate_competition_based_price(product_id, current_price, market_data)
        
        elif strategy == PricingStrategy.TIME_BASED:
            return await self._calculate_time_based_price(product_id, current_price, market_data)
        
        elif strategy == PricingStrategy.VALUE_BASED:
            return await self._calculate_value_based_price(product_id, current_price, market_data)
        
        else:
            # Hybrid or default approach
            return await self._calculate_hybrid_price(product_id, current_price, market_data)
    
    async def _calculate_demand_based_price(
        self,
        product_id: str,
        current_price: Decimal,
        market_data: MarketData
    ) -> Decimal:
        """Calculate price based on demand indicators."""
        demand_score = mean(market_data.demand_indicators.values())
        
        # Apply demand-based adjustment
        if demand_score > 0.8:
            # High demand - increase price
            adjustment = 1.0 + (demand_score - 0.8) * 0.5  # Up to 10% increase
        elif demand_score < 0.4:
            # Low demand - decrease price
            adjustment = 1.0 - (0.4 - demand_score) * 0.3  # Up to 12% decrease
        else:
            # Moderate demand - small adjustment
            adjustment = 1.0 + (demand_score - 0.6) * 0.1
        
        new_price = current_price * Decimal(str(adjustment))
        
        # Apply pricing rule constraints
        return self._apply_pricing_constraints(product_id, new_price)
    
    async def _calculate_competition_based_price(
        self,
        product_id: str,
        current_price: Decimal,
        market_data: MarketData
    ) -> Decimal:
        """Calculate price based on competitor analysis."""
        competitor_prices = list(market_data.competitor_prices.values())
        
        if not competitor_prices:
            return current_price
        
        avg_competitor_price = Decimal(str(mean([float(p) for p in competitor_prices])))
        
        # Position slightly below average for competitiveness
        competitive_adjustment = 0.95  # 5% below average
        new_price = avg_competitor_price * Decimal(str(competitive_adjustment))
        
        return self._apply_pricing_constraints(product_id, new_price)
    
    async def _calculate_time_based_price(
        self,
        product_id: str,
        current_price: Decimal,
        market_data: MarketData
    ) -> Decimal:
        """Calculate price based on time and seasonal factors."""
        seasonal_factor = market_data.seasonal_factors.get("current_season", 1.0)
        holiday_effect = market_data.seasonal_factors.get("holiday_effect", 1.0)
        
        # Combine seasonal factors
        time_adjustment = (seasonal_factor + holiday_effect) / 2
        new_price = current_price * Decimal(str(time_adjustment))
        
        return self._apply_pricing_constraints(product_id, new_price)
    
    async def _calculate_value_based_price(
        self,
        product_id: str,
        current_price: Decimal,
        market_data: MarketData
    ) -> Decimal:
        """Calculate price based on perceived value."""
        # Use demand indicators as proxy for value perception
        value_score = mean(market_data.demand_indicators.values())
        
        # High value perception allows for premium pricing
        if value_score > 0.7:
            value_adjustment = 1.0 + (value_score - 0.7) * 0.4  # Up to 12% premium
        else:
            value_adjustment = 0.9 + value_score * 0.1  # Discount for low value perception
        
        new_price = current_price * Decimal(str(value_adjustment))
        
        return self._apply_pricing_constraints(product_id, new_price)
    
    async def _calculate_hybrid_price(
        self,
        product_id: str,
        current_price: Decimal,
        market_data: MarketData
    ) -> Decimal:
        """Calculate price using hybrid approach."""
        # Calculate prices using different strategies
        demand_price = await self._calculate_demand_based_price(product_id, current_price, market_data)
        competition_price = await self._calculate_competition_based_price(product_id, current_price, market_data)
        value_price = await self._calculate_value_based_price(product_id, current_price, market_data)
        
        # Weight the different approaches
        weights = {
            "demand": 0.4,
            "competition": 0.3,
            "value": 0.3
        }
        
        weighted_price = (
            demand_price * Decimal(str(weights["demand"])) +
            competition_price * Decimal(str(weights["competition"])) +
            value_price * Decimal(str(weights["value"]))
        )
        
        return self._apply_pricing_constraints(product_id, weighted_price)
    
    def _apply_pricing_constraints(self, product_id: str, proposed_price: Decimal) -> Decimal:
        """Apply pricing rule constraints to proposed price."""
        # Find applicable pricing rules
        applicable_rules = [
            rule for rule in self.pricing_rules.values()
            if rule.is_active
        ]
        
        if not applicable_rules:
            return proposed_price
        
        # Apply most restrictive constraints
        min_price = max(rule.min_price for rule in applicable_rules)
        max_price = min(rule.max_price for rule in applicable_rules)
        
        # Ensure price is within bounds
        constrained_price = max(min_price, min(proposed_price, max_price))
        
        return constrained_price
    
    async def _determine_adjustment_reason(
        self,
        market_data: MarketData,
        strategy: PricingStrategy
    ) -> PriceAdjustmentReason:
        """Determine the primary reason for price adjustment."""
        
        if strategy == PricingStrategy.DEMAND_BASED:
            demand_score = mean(market_data.demand_indicators.values())
            if demand_score > 0.8:
                return PriceAdjustmentReason.HIGH_DEMAND
            elif demand_score < 0.4:
                return PriceAdjustmentReason.LOW_DEMAND
        
        elif strategy == PricingStrategy.COMPETITION_BASED:
            return PriceAdjustmentReason.COMPETITOR_CHANGE
        
        elif strategy == PricingStrategy.TIME_BASED:
            seasonal_factor = market_data.seasonal_factors.get("current_season", 1.0)
            if abs(seasonal_factor - 1.0) > 0.1:
                return PriceAdjustmentReason.SEASONAL_TREND
        
        return PriceAdjustmentReason.PERFORMANCE_OPTIMIZATION
    
    async def _calculate_confidence(
        self,
        product_id: str,
        strategy: PricingStrategy,
        market_data: MarketData
    ) -> float:
        """Calculate confidence score for price recommendation."""
        base_confidence = 0.7
        
        # Adjust based on data quality
        data_quality = len(market_data.competitor_prices) / 5.0  # Assume 5 is ideal
        data_quality = min(data_quality, 1.0)
        
        # Adjust based on strategy reliability
        strategy_confidence = {
            PricingStrategy.DEMAND_BASED: 0.8,
            PricingStrategy.COMPETITION_BASED: 0.85,
            PricingStrategy.VALUE_BASED: 0.75,
            PricingStrategy.TIME_BASED: 0.7,
            PricingStrategy.HYBRID: 0.9
        }.get(strategy, 0.7)
        
        # Adjust based on market stability
        demand_variance = stdev(list(market_data.demand_indicators.values()))
        stability_factor = max(0, 1.0 - demand_variance)
        
        confidence = base_confidence * data_quality * strategy_confidence * stability_factor
        return min(confidence, 1.0)
    
    async def _estimate_revenue_impact(
        self,
        product_id: str,
        current_price: Decimal,
        new_price: Decimal,
        market_data: MarketData
    ) -> Decimal:
        """Estimate revenue impact of price change."""
        if current_price == 0:
            return Decimal("0")
        
        price_change_pct = float((new_price - current_price) / current_price)
        
        # Get demand elasticity for product type
        elasticity = self.demand_elasticity_models.get("subscription", {}).get("elasticity", -1.0)
        
        # Estimate demand change
        demand_change_pct = elasticity * price_change_pct
        
        # Estimate revenue change (simplified model)
        revenue_multiplier = (1 + price_change_pct) * (1 + demand_change_pct)
        
        # Assume baseline revenue for calculation
        baseline_revenue = Decimal("1000")  # This would come from actual data
        revenue_impact = baseline_revenue * (Decimal(str(revenue_multiplier)) - Decimal("1"))
        
        return revenue_impact
    
    async def _estimate_demand_change(
        self,
        product_id: str,
        current_price: Decimal,
        new_price: Decimal
    ) -> float:
        """Estimate demand change percentage."""
        if current_price == 0:
            return 0.0
        
        price_change_pct = float((new_price - current_price) / current_price)
        elasticity = self.demand_elasticity_models.get("subscription", {}).get("elasticity", -1.0)
        
        demand_change_pct = elasticity * price_change_pct
        return demand_change_pct
    
    async def _generate_pricing_reasoning(
        self,
        product_id: str,
        current_price: Decimal,
        recommended_price: Decimal,
        strategy: PricingStrategy,
        market_data: MarketData
    ) -> str:
        """Generate AI reasoning for price recommendation."""
        price_change = recommended_price - current_price
        change_pct = float(price_change / current_price * 100) if current_price > 0 else 0
        
        demand_score = mean(market_data.demand_indicators.values())
        competitor_avg = mean([float(p) for p in market_data.competitor_prices.values()]) if market_data.competitor_prices else 0
        
        direction = "increase" if price_change > 0 else "decrease" if price_change < 0 else "maintain"
        
        reasoning = f"""AI Pricing Analysis: Recommending {change_pct:+.1f}% price {direction} using {strategy.value.replace('_', ' ')} strategy. 
        
Market Factors:
• Demand strength: {demand_score:.1%} (market indicators show {'strong' if demand_score > 0.7 else 'moderate' if demand_score > 0.4 else 'weak'} demand)
• Competitor average: ${competitor_avg:.2f} (your current price is {'above' if float(current_price) > competitor_avg else 'below'} market)
• Price positioning: {'Premium' if float(recommended_price) > competitor_avg * 1.1 else 'Competitive' if float(recommended_price) > competitor_avg * 0.9 else 'Value'}

Expected Outcome: This adjustment optimizes for {strategy.value.replace('_', ' ')} while maintaining competitive positioning."""
        
        return reasoning
    
    async def _serialize_market_data(self, market_data: MarketData) -> Dict[str, Any]:
        """Serialize market data for storage."""
        return {
            "competitor_prices": {k: float(v) for k, v in market_data.competitor_prices.items()},
            "demand_indicators": market_data.demand_indicators,
            "seasonal_factors": market_data.seasonal_factors,
            "economic_indicators": market_data.economic_indicators,
            "timestamp": market_data.timestamp.isoformat()
        }
    
    async def apply_price_recommendation(
        self,
        recommendation_id: str,
        product_id: str
    ) -> bool:
        """Apply a price recommendation."""
        try:
            # Find recommendation
            product_history = self.price_history.get(product_id, [])
            recommendation = None
            
            for rec in product_history:
                if rec.recommendation_id == recommendation_id:
                    recommendation = rec
                    break
            
            if not recommendation:
                self.logger.error(f"Recommendation {recommendation_id} not found")
                return False
            
            # Check if still valid
            if recommendation.valid_until < datetime.now():
                self.logger.error(f"Recommendation {recommendation_id} has expired")
                return False
            
            # Apply the price
            self.active_prices[product_id] = recommendation.recommended_price
            
            self.logger.info(f"Applied price recommendation for {product_id}: ${recommendation.recommended_price}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error applying price recommendation: {e}")
            return False
    
    async def get_pricing_performance(
        self,
        product_id: str,
        period_days: int = 30
    ) -> Optional[PricingPerformance]:
        """Get pricing performance metrics for a product."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)
        
        # Get price changes in period
        product_history = self.price_history.get(product_id, [])
        period_recommendations = [
            rec for rec in product_history
            if start_date <= rec.created_at <= end_date
        ]
        
        if not period_recommendations:
            return None
        
        # Calculate performance metrics
        price_changes = len(period_recommendations)
        avg_price = mean([float(rec.recommended_price) for rec in period_recommendations])
        
        # Simulate performance data (in production, this would come from actual sales data)
        import random
        performance = PricingPerformance(
            product_id=product_id,
            period_start=start_date,
            period_end=end_date,
            price_changes=price_changes,
            average_price=Decimal(str(avg_price)),
            revenue_generated=Decimal(str(avg_price * (50 + random.randint(0, 100)))),
            units_sold=50 + random.randint(0, 100),
            conversion_rate=0.02 + random.random() * 0.03,
            price_elasticity=-1.0 - random.random(),
            competitor_comparison={"market_position": "competitive"},
            customer_satisfaction=0.7 + random.random() * 0.3
        )
        
        return performance
    
    async def create_pricing_rule(
        self,
        name: str,
        strategy: PricingStrategy,
        conditions: Dict[str, Any],
        min_price: Decimal,
        max_price: Decimal,
        base_price: Decimal,
        adjustment_percentage: float,
        priority: int = 5
    ) -> str:
        """Create a new pricing rule."""
        rule_id = str(uuid4())
        
        rule = PricingRule(
            rule_id=rule_id,
            name=name,
            strategy=strategy,
            conditions=conditions,
            min_price=min_price,
            max_price=max_price,
            base_price=base_price,
            adjustment_percentage=adjustment_percentage,
            priority=priority
        )
        
        self.pricing_rules[rule_id] = rule
        
        self.logger.info(f"Created pricing rule: {name} ({rule_id})")
        return rule_id


# Global instance
_dynamic_pricing_ai_engine = None


async def get_dynamic_pricing_ai_engine() -> DynamicPricingAIEngine:
    """Get the global dynamic pricing AI engine instance."""
    global _dynamic_pricing_ai_engine
    
    if _dynamic_pricing_ai_engine is None:
        _dynamic_pricing_ai_engine = DynamicPricingAIEngine()
        await _dynamic_pricing_ai_engine.initialize()
    
    return _dynamic_pricing_ai_engine


# Example usage
async def main():
    """Example usage of DynamicPricingAIEngine."""
    engine = await get_dynamic_pricing_ai_engine()
    
    product_id = "premium_course_001"
    current_price = Decimal("49.99")
    
    # Get price recommendation
    recommendation = await engine.get_price_recommendation(
        product_id=product_id,
        current_price=current_price,
        strategy=PricingStrategy.HYBRID
    )
    
    print(f"💰 Dynamic Pricing Recommendation for {product_id}")
    print(f"Current Price: ${recommendation.current_price}")
    print(f"Recommended Price: ${recommendation.recommended_price}")
    print(f"Price Change: {recommendation.change_direction.value} by {recommendation.change_percentage:+.1f}%")
    print(f"Strategy: {recommendation.strategy_used.value}")
    print(f"Reason: {recommendation.adjustment_reason.value}")
    print(f"Confidence: {recommendation.confidence_score:.1%}")
    print(f"Expected Revenue Impact: ${recommendation.expected_revenue_impact:+,.2f}")
    print(f"Expected Demand Change: {recommendation.expected_demand_change:+.1%}")
    
    print(f"\n🤖 AI Reasoning:")
    print(recommendation.ai_reasoning)
    
    # Apply recommendation
    success = await engine.apply_price_recommendation(
        recommendation.recommendation_id,
        product_id
    )
    
    if success:
        print(f"\n✅ Price recommendation applied successfully")
    
    # Get performance metrics
    performance = await engine.get_pricing_performance(product_id, period_days=30)
    if performance:
        print(f"\n📊 Pricing Performance (Last 30 days):")
        print(f"Price Changes: {performance.price_changes}")
        print(f"Average Price: ${performance.average_price:.2f}")
        print(f"Revenue Generated: ${performance.revenue_generated:,.2f}")
        print(f"Units Sold: {performance.units_sold}")
        print(f"Conversion Rate: {performance.conversion_rate:.2%}")


if __name__ == "__main__":
    asyncio.run(main())