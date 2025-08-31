"""
Dynamic Pricing Optimization Engine
Advanced pricing optimization with elasticity analysis and A/B testing.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import json
import logging
import math
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import random

logger = logging.getLogger(__name__)


class PricingStrategy(Enum):
    """Available pricing strategies"""
    PENETRATION = "penetration"  # Low price to gain market share
    SKIMMING = "skimming"       # High price for premium positioning
    COMPETITIVE = "competitive"  # Match competitor prices
    VALUE_BASED = "value_based" # Price based on perceived value
    DYNAMIC = "dynamic"         # Real-time price adjustments
    SEASONAL = "seasonal"       # Season-based pricing


class MarketCondition(Enum):
    """Market condition types"""
    BULL = "bull"         # Growing market
    BEAR = "bear"         # Declining market
    STABLE = "stable"     # Stable market
    VOLATILE = "volatile" # High volatility


@dataclass
class PricePoint:
    """Individual price point data"""
    price: float
    demand: int
    revenue: float
    conversion_rate: float
    timestamp: datetime
    platform: str
    market_conditions: Dict[str, Any]


@dataclass
class ElasticityAnalysis:
    """Price elasticity analysis result"""
    content_id: str
    platform: str
    price_elasticity: float
    demand_elasticity: float
    revenue_elasticity: float
    optimal_price_range: Tuple[float, float]
    current_position: str  # "elastic", "inelastic", "unitary"
    elasticity_confidence: float
    analysis_period_days: int
    calculated_at: datetime


@dataclass
class PricingRecommendation:
    """Comprehensive pricing recommendation"""
    content_id: str
    platform: str
    current_price: float
    recommended_price: float
    strategy: PricingStrategy
    expected_revenue_lift: float
    expected_demand_change: float
    confidence_score: float
    risk_assessment: str
    implementation_timeline: str
    monitoring_metrics: List[str]
    ab_test_suggestion: Dict[str, Any]
    generated_at: datetime


class DynamicPricingEngine:
    """Advanced dynamic pricing optimization engine"""
    
    def __init__(self):
        self.pricing_history = {}
        self.elasticity_cache = {}
        self.competitor_data = {}
        self.ab_tests = {}
        self.market_intelligence = {}
        self.pricing_rules = self._initialize_pricing_rules()
        
    async def analyze_price_elasticity(
        self,
        content_id: str,
        platform: str,
        pricing_history: List[PricePoint],
        analysis_period_days: int = 30
    ) -> ElasticityAnalysis:
        """Analyze price elasticity of demand"""
        try:
            if len(pricing_history) < 10:
                logger.warning(f"Insufficient pricing data for elasticity analysis: {len(pricing_history)} points")
                return self._create_default_elasticity_analysis(content_id, platform)
            
            # Filter data to analysis period
            cutoff_date = datetime.now() - timedelta(days=analysis_period_days)
            recent_data = [p for p in pricing_history if p.timestamp >= cutoff_date]
            
            if len(recent_data) < 5:
                recent_data = pricing_history[-10:]  # Use last 10 points
            
            # Sort by price for analysis
            sorted_data = sorted(recent_data, key=lambda x: x.price)
            
            # Calculate elasticity using different methods
            price_elasticity = await self._calculate_price_elasticity(sorted_data)
            demand_elasticity = await self._calculate_demand_elasticity(sorted_data)
            revenue_elasticity = await self._calculate_revenue_elasticity(sorted_data)
            
            # Determine optimal price range
            optimal_range = await self._find_optimal_price_range(sorted_data, price_elasticity)
            
            # Classify elasticity position
            current_position = self._classify_elasticity_position(price_elasticity)
            
            # Calculate confidence based on data quality
            elasticity_confidence = min(1.0, len(recent_data) / 20.0)
            
            analysis = ElasticityAnalysis(
                content_id=content_id,
                platform=platform,
                price_elasticity=price_elasticity,
                demand_elasticity=demand_elasticity,
                revenue_elasticity=revenue_elasticity,
                optimal_price_range=optimal_range,
                current_position=current_position,
                elasticity_confidence=elasticity_confidence,
                analysis_period_days=analysis_period_days,
                calculated_at=datetime.now()
            )
            
            # Cache the result
            cache_key = f"{content_id}_{platform}"
            self.elasticity_cache[cache_key] = analysis
            
            logger.info(f"Elasticity analysis completed for {content_id} on {platform}: {price_elasticity:.3f}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing price elasticity: {str(e)}")
            return self._create_default_elasticity_analysis(content_id, platform)
    
    async def generate_pricing_recommendation(
        self,
        content_id: str,
        platform: str,
        current_price: float,
        content_type: str,
        market_conditions: Optional[Dict[str, Any]] = None
    ) -> PricingRecommendation:
        """Generate comprehensive pricing recommendation"""
        try:
            # Get elasticity analysis
            elasticity_key = f"{content_id}_{platform}"
            elasticity_analysis = self.elasticity_cache.get(elasticity_key)
            
            # Get competitor analysis (mock)
            competitor_analysis = await self._get_competitor_analysis(content_type, platform)
            
            # Determine optimal strategy
            strategy = await self._determine_optimal_strategy(
                elasticity_analysis, competitor_analysis, market_conditions
            )
            
            # Calculate recommended price
            recommended_price = await self._calculate_recommended_price(
                current_price, strategy, elasticity_analysis, competitor_analysis
            )
            
            # Estimate impact
            revenue_lift = await self._estimate_revenue_lift(
                current_price, recommended_price, elasticity_analysis
            )
            
            demand_change = await self._estimate_demand_change(
                current_price, recommended_price, elasticity_analysis
            )
            
            # Calculate confidence score
            confidence_score = await self._calculate_recommendation_confidence(
                elasticity_analysis, competitor_analysis, market_conditions
            )
            
            # Risk assessment
            risk_assessment = await self._assess_pricing_risk(
                current_price, recommended_price, strategy, market_conditions
            )
            
            # Implementation timeline
            timeline = await self._determine_implementation_timeline(strategy, risk_assessment)
            
            # Monitoring metrics
            monitoring_metrics = await self._define_monitoring_metrics(strategy)
            
            # A/B test suggestion
            ab_test_suggestion = await self._suggest_ab_test_parameters(
                current_price, recommended_price, confidence_score
            )
            
            recommendation = PricingRecommendation(
                content_id=content_id,
                platform=platform,
                current_price=current_price,
                recommended_price=recommended_price,
                strategy=strategy,
                expected_revenue_lift=revenue_lift,
                expected_demand_change=demand_change,
                confidence_score=confidence_score,
                risk_assessment=risk_assessment,
                implementation_timeline=timeline,
                monitoring_metrics=monitoring_metrics,
                ab_test_suggestion=ab_test_suggestion,
                generated_at=datetime.now()
            )
            
            logger.info(f"Pricing recommendation generated for {content_id}: {recommended_price:.2f}")
            return recommendation
            
        except Exception as e:
            logger.error(f"Error generating pricing recommendation: {str(e)}")
            return PricingRecommendation(
                content_id=content_id,
                platform=platform,
                current_price=current_price,
                recommended_price=current_price,
                strategy=PricingStrategy.COMPETITIVE,
                expected_revenue_lift=0.0,
                expected_demand_change=0.0,
                confidence_score=0.0,
                risk_assessment="Error in analysis",
                implementation_timeline="Manual review required",
                monitoring_metrics=[],
                ab_test_suggestion={},
                generated_at=datetime.now()
            )
    
    # Private helper methods
    
    async def _calculate_price_elasticity(self, price_points: List[PricePoint]) -> float:
        """Calculate price elasticity of demand"""
        try:
            if len(price_points) < 2:
                return -1.0  # Default elasticity
            
            # Calculate percentage changes
            elasticity_values = []
            
            for i in range(1, len(price_points)):
                prev_point = price_points[i-1]
                curr_point = price_points[i]
                
                if prev_point.price > 0 and prev_point.demand > 0:
                    price_change = (curr_point.price - prev_point.price) / prev_point.price
                    demand_change = (curr_point.demand - prev_point.demand) / prev_point.demand
                    
                    if price_change != 0:
                        elasticity = demand_change / price_change
                        elasticity_values.append(elasticity)
            
            if not elasticity_values:
                return -1.0
            
            # Average elasticity
            avg_elasticity = statistics.mean(elasticity_values)
            
            # Bound elasticity to reasonable range
            return max(-10.0, min(avg_elasticity, 0.0))
            
        except Exception as e:
            logger.error(f"Error calculating price elasticity: {str(e)}")
            return -1.0
    
    async def _calculate_demand_elasticity(self, price_points: List[PricePoint]) -> float:
        """Calculate demand elasticity"""
        try:
            demands = [p.demand for p in price_points]
            if len(demands) < 2:
                return 0.0
            
            # Calculate coefficient of variation
            mean_demand = statistics.mean(demands)
            std_demand = statistics.stdev(demands) if len(demands) > 1 else 0
            
            return std_demand / mean_demand if mean_demand > 0 else 0.0
            
        except Exception as e:
            logger.error(f"Error calculating demand elasticity: {str(e)}")
            return 0.0
    
    async def _calculate_revenue_elasticity(self, price_points: List[PricePoint]) -> float:
        """Calculate revenue elasticity"""
        try:
            if len(price_points) < 2:
                return 0.0
            
            revenue_elasticity_values = []
            
            for i in range(1, len(price_points)):
                prev_point = price_points[i-1]
                curr_point = price_points[i]
                
                if prev_point.price > 0 and prev_point.revenue > 0:
                    price_change = (curr_point.price - prev_point.price) / prev_point.price
                    revenue_change = (curr_point.revenue - prev_point.revenue) / prev_point.revenue
                    
                    if price_change != 0:
                        elasticity = revenue_change / price_change
                        revenue_elasticity_values.append(elasticity)
            
            return statistics.mean(revenue_elasticity_values) if revenue_elasticity_values else 0.0
            
        except Exception as e:
            logger.error(f"Error calculating revenue elasticity: {str(e)}")
            return 0.0
    
    async def _find_optimal_price_range(
        self, 
        price_points: List[PricePoint], 
        elasticity: float
    ) -> Tuple[float, float]:
        """Find optimal price range based on revenue maximization"""
        try:
            if not price_points:
                return (0.0, 0.0)
            
            # Find price point with maximum revenue
            max_revenue_point = max(price_points, key=lambda p: p.revenue)
            optimal_price = max_revenue_point.price
            
            # Calculate range based on elasticity
            if abs(elasticity) > 1.5:  # Elastic demand
                price_range = optimal_price * 0.2  # 20% range
            elif abs(elasticity) < 0.5:  # Inelastic demand
                price_range = optimal_price * 0.4  # 40% range
            else:
                price_range = optimal_price * 0.3  # 30% range
            
            lower_bound = max(0.1, optimal_price - price_range)
            upper_bound = optimal_price + price_range
            
            return (lower_bound, upper_bound)
            
        except Exception as e:
            logger.error(f"Error finding optimal price range: {str(e)}")
            return (0.0, 0.0)
    
    def _classify_elasticity_position(self, elasticity: float) -> str:
        """Classify elasticity position"""
        if elasticity < -1.0:
            return "elastic"
        elif elasticity > -1.0 and elasticity < 0.0:
            return "inelastic"
        elif abs(elasticity) < 0.1:
            return "unitary"
        else:
            return "unknown"
    
    def _create_default_elasticity_analysis(self, content_id: str, platform: str) -> ElasticityAnalysis:
        """Create default elasticity analysis"""
        return ElasticityAnalysis(
            content_id=content_id,
            platform=platform,
            price_elasticity=-1.0,
            demand_elasticity=0.5,
            revenue_elasticity=0.0,
            optimal_price_range=(0.0, 0.0),
            current_position="unknown",
            elasticity_confidence=0.0,
            analysis_period_days=30,
            calculated_at=datetime.now()
        )
    
    async def _get_competitor_analysis(self, content_type: str, platform: str) -> Dict[str, Any]:
        """Get competitor analysis (mock implementation)"""
        return {
            "average_competitor_price": 5.0,
            "price_range": (2.0, 10.0),
            "market_position": "at",
            "competitive_advantage_score": 0.7
        }
    
    async def _determine_optimal_strategy(
        self,
        elasticity_analysis: Optional[ElasticityAnalysis],
        competitor_analysis: Optional[Dict[str, Any]],
        market_conditions: Optional[Dict[str, Any]]
    ) -> PricingStrategy:
        """Determine optimal pricing strategy"""
        try:
            # Default to competitive pricing
            if not elasticity_analysis and not competitor_analysis:
                return PricingStrategy.COMPETITIVE
            
            # If elastic demand, consider penetration pricing
            if elasticity_analysis and elasticity_analysis.current_position == "elastic":
                return PricingStrategy.PENETRATION
            
            # If inelastic demand, consider skimming
            if elasticity_analysis and elasticity_analysis.current_position == "inelastic":
                return PricingStrategy.SKIMMING
            
            # If above market, consider competitive pricing
            if competitor_analysis and competitor_analysis.get("market_position") == "above":
                return PricingStrategy.COMPETITIVE
            
            # If market is volatile, use dynamic pricing
            if market_conditions and market_conditions.get('volatility', 'low') == 'high':
                return PricingStrategy.DYNAMIC
            
            return PricingStrategy.VALUE_BASED
            
        except Exception as e:
            logger.error(f"Error determining optimal strategy: {str(e)}")
            return PricingStrategy.COMPETITIVE
    
    async def _calculate_recommended_price(
        self,
        current_price: float,
        strategy: PricingStrategy,
        elasticity_analysis: Optional[ElasticityAnalysis],
        competitor_analysis: Optional[Dict[str, Any]]
    ) -> float:
        """Calculate recommended price based on strategy"""
        try:
            if strategy == PricingStrategy.PENETRATION:
                # Reduce price by 10-20%
                return current_price * 0.85
                
            elif strategy == PricingStrategy.SKIMMING:
                # Increase price by 10-15%
                return current_price * 1.12
                
            elif strategy == PricingStrategy.COMPETITIVE:
                # Match average competitor price
                if competitor_analysis:
                    return competitor_analysis.get("average_competitor_price", current_price)
                return current_price
                
            elif strategy == PricingStrategy.VALUE_BASED:
                # Price based on optimal range
                if elasticity_analysis and elasticity_analysis.optimal_price_range[0] > 0:
                    lower, upper = elasticity_analysis.optimal_price_range
                    return (lower + upper) / 2
                return current_price * 1.05
                
            elif strategy == PricingStrategy.DYNAMIC:
                # Small adjustment based on market conditions
                return current_price * random.uniform(0.95, 1.05)
                
            else:
                return current_price
                
        except Exception as e:
            logger.error(f"Error calculating recommended price: {str(e)}")
            return current_price
    
    async def _estimate_revenue_lift(
        self,
        current_price: float,
        recommended_price: float,
        elasticity_analysis: Optional[ElasticityAnalysis]
    ) -> float:
        """Estimate revenue lift from price change"""
        try:
            if current_price == 0 or not elasticity_analysis:
                return 0.0
            
            price_change_percent = (recommended_price - current_price) / current_price
            
            # Use revenue elasticity if available
            revenue_elasticity = elasticity_analysis.revenue_elasticity
            
            if abs(revenue_elasticity) > 0.1:
                revenue_lift = revenue_elasticity * price_change_percent
            else:
                # Estimate based on price elasticity
                price_elasticity = elasticity_analysis.price_elasticity
                # Revenue lift = price change + demand change
                demand_change = price_elasticity * price_change_percent
                revenue_lift = price_change_percent + demand_change
            
            return revenue_lift * 100  # Return as percentage
            
        except Exception as e:
            logger.error(f"Error estimating revenue lift: {str(e)}")
            return 0.0
    
    async def _estimate_demand_change(
        self,
        current_price: float,
        recommended_price: float,
        elasticity_analysis: Optional[ElasticityAnalysis]
    ) -> float:
        """Estimate demand change from price change"""
        try:
            if current_price == 0 or not elasticity_analysis:
                return 0.0
            
            price_change_percent = (recommended_price - current_price) / current_price
            price_elasticity = elasticity_analysis.price_elasticity
            
            demand_change = price_elasticity * price_change_percent
            return demand_change * 100  # Return as percentage
            
        except Exception as e:
            logger.error(f"Error estimating demand change: {str(e)}")
            return 0.0
    
    async def _calculate_recommendation_confidence(
        self,
        elasticity_analysis: Optional[ElasticityAnalysis],
        competitor_analysis: Optional[Dict[str, Any]],
        market_conditions: Optional[Dict[str, Any]]
    ) -> float:
        """Calculate confidence score for recommendation"""
        try:
            confidence_factors = []
            
            if elasticity_analysis:
                confidence_factors.append(elasticity_analysis.elasticity_confidence)
            
            if competitor_analysis:
                # Higher confidence if we have good competitor data
                confidence_factors.append(0.8)
            
            if market_conditions:
                # Market stability affects confidence
                stability = market_conditions.get('stability', 'medium')
                if stability == 'high':
                    confidence_factors.append(0.9)
                elif stability == 'medium':
                    confidence_factors.append(0.7)
                else:
                    confidence_factors.append(0.5)
            
            if not confidence_factors:
                return 0.5
            
            return statistics.mean(confidence_factors)
            
        except Exception as e:
            logger.error(f"Error calculating recommendation confidence: {str(e)}")
            return 0.5
    
    async def _assess_pricing_risk(
        self,
        current_price: float,
        recommended_price: float,
        strategy: PricingStrategy,
        market_conditions: Optional[Dict[str, Any]]
    ) -> str:
        """Assess pricing risk"""
        try:
            price_change_percent = abs(recommended_price - current_price) / current_price if current_price > 0 else 0
            
            if price_change_percent > 0.2:  # >20% change
                risk_level = "High"
            elif price_change_percent > 0.1:  # >10% change
                risk_level = "Medium"
            else:
                risk_level = "Low"
            
            # Adjust for strategy
            if strategy == PricingStrategy.SKIMMING:
                risk_level = "Medium-High" if risk_level == "Medium" else risk_level
            elif strategy == PricingStrategy.PENETRATION:
                risk_level = "Medium" if risk_level == "High" else risk_level
            
            # Market conditions adjustment
            if market_conditions and market_conditions.get('volatility', 'low') == 'high':
                if risk_level == "Low":
                    risk_level = "Medium"
                elif risk_level == "Medium":
                    risk_level = "High"
            
            return risk_level
            
        except Exception as e:
            logger.error(f"Error assessing pricing risk: {str(e)}")
            return "Unknown"
    
    async def _determine_implementation_timeline(
        self,
        strategy: PricingStrategy,
        risk_assessment: str
    ) -> str:
        """Determine implementation timeline"""
        try:
            if risk_assessment == "High":
                return "Gradual implementation over 2-4 weeks with A/B testing"
            elif risk_assessment in ["Medium", "Medium-High"]:
                return "Phased implementation over 1-2 weeks"
            else:
                return "Immediate implementation possible"
                
        except Exception as e:
            logger.error(f"Error determining implementation timeline: {str(e)}")
            return "Manual review required"
    
    async def _define_monitoring_metrics(self, strategy: PricingStrategy) -> List[str]:
        """Define monitoring metrics for strategy"""
        base_metrics = [
            "conversion_rate",
            "revenue_per_visitor",
            "total_revenue",
            "demand_volume"
        ]
        
        strategy_specific = {
            PricingStrategy.PENETRATION: ["market_share", "competitor_response"],
            PricingStrategy.SKIMMING: ["customer_retention", "premium_perception"],
            PricingStrategy.COMPETITIVE: ["price_position_vs_competitors"],
            PricingStrategy.VALUE_BASED: ["customer_satisfaction", "perceived_value"],
            PricingStrategy.DYNAMIC: ["price_sensitivity", "demand_elasticity"]
        }
        
        return base_metrics + strategy_specific.get(strategy, [])
    
    async def _suggest_ab_test_parameters(
        self,
        current_price: float,
        recommended_price: float,
        confidence_score: float
    ) -> Dict[str, Any]:
        """Suggest A/B test parameters"""
        try:
            price_change = abs(recommended_price - current_price) / current_price if current_price > 0 else 0
            
            # Suggest smaller test if large price change or low confidence
            if price_change > 0.15 or confidence_score < 0.7:
                test_price = current_price + (recommended_price - current_price) * 0.5
                duration_hours = 168  # 1 week
                traffic_split = 0.2   # 20% test traffic
            else:
                test_price = recommended_price
                duration_hours = 72   # 3 days
                traffic_split = 0.5   # 50% test traffic
            
            return {
                "test_price": round(test_price, 2),
                "duration_hours": duration_hours,
                "traffic_split": traffic_split,
                "minimum_sample_size": 1000,
                "success_metrics": ["conversion_rate", "revenue_per_visitor"]
            }
            
        except Exception as e:
            logger.error(f"Error suggesting A/B test parameters: {str(e)}")
            return {}
    
    def _initialize_pricing_rules(self) -> Dict[str, Any]:
        """Initialize pricing rules and constraints"""
        return {
            "min_price": 0.10,
            "max_price_increase_percent": 50,
            "max_price_decrease_percent": 30,
            "ab_test_min_duration_hours": 24,
            "ab_test_max_duration_hours": 336,  # 2 weeks
            "minimum_confidence_for_auto_implementation": 0.8
        }