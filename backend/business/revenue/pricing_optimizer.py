"""Pricing Optimizer - IA Influencer Agent Platform
================================================

Advanced dynamic pricing optimization engine using machine learning
and market intelligence for revenue maximization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from dataclasses import dataclass
from enum import Enum
import statistics
import uuid

logger = logging.getLogger(__name__)


class PricingStrategy(Enum):
    """Pricing strategies."""
    DYNAMIC = "dynamic"
    COMPETITIVE = "competitive" 
    VALUE_BASED = "value_based"
    PENETRATION = "penetration"
    PREMIUM = "premium"
    FREEMIUM = "freemium"


@dataclass
class PricePoint:
    """Price point with optimization data."""
    price: Decimal
    demand_elasticity: float
    conversion_probability: float
    revenue_potential: Decimal
    competitive_position: str


@dataclass
class PricingOptimization:
    """Pricing optimization result."""
    optimization_id: str
    current_price: Decimal
    optimal_price: Decimal
    price_adjustment: Decimal
    expected_revenue_impact: float
    confidence_score: float
    strategy: PricingStrategy
    market_conditions: Dict[str, Any]
    recommendations: List[str]


class PricingOptimizer:
    """Advanced pricing optimization engine."""
    
    def __init__(self, creator_id: str, config: Optional[Dict[str, Any]] = None):
        """Initialize pricing optimizer."""
        self.creator_id = creator_id
        self.config = config or {}
        self.pricing_history: List[Dict[str, Any]] = []
        self.market_data: Dict[str, Any] = {}
        
    async def optimize_pricing_strategy(
        self,
        current_pricing: Dict[str, Any],
        market_data: Dict[str, Any],
        performance_metrics: Dict[str, Any]
    ) -> PricingOptimization:
        """Optimize pricing strategy using advanced analytics."""
        try:
            # Analyze current pricing performance
            current_performance = await self._analyze_current_performance(
                current_pricing, performance_metrics
            )
            
            # Analyze market conditions
            market_analysis = await self._analyze_market_conditions(market_data)
            
            # Calculate demand elasticity
            demand_elasticity = await self._calculate_demand_elasticity(
                current_pricing, performance_metrics
            )
            
            # Generate pricing scenarios
            pricing_scenarios = await self._generate_pricing_scenarios(
                current_pricing, market_analysis, demand_elasticity
            )
            
            # Evaluate scenarios
            scenario_evaluations = await self._evaluate_pricing_scenarios(
                pricing_scenarios, market_analysis
            )
            
            # Select optimal pricing
            optimal_scenario = await self._select_optimal_pricing(scenario_evaluations)
            
            # Generate optimization result
            optimization = PricingOptimization(
                optimization_id=str(uuid.uuid4()),
                current_price=Decimal(str(current_pricing.get('base_price', 0))),
                optimal_price=optimal_scenario['price'],
                price_adjustment=optimal_scenario['price'] - Decimal(str(current_pricing.get('base_price', 0))),
                expected_revenue_impact=optimal_scenario['revenue_impact'],
                confidence_score=optimal_scenario['confidence'],
                strategy=optimal_scenario['strategy'],
                market_conditions=market_analysis,
                recommendations=await self._generate_pricing_recommendations(optimal_scenario)
            )
            
            # Store optimization
            await self._store_optimization(optimization)
            
            return optimization
            
        except Exception as e:
            logger.error(f"Pricing optimization failed: {e}")
            raise
    
    async def calculate_dynamic_pricing(
        self,
        base_price: Decimal,
        market_conditions: Dict[str, Any],
        real_time_factors: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate dynamic pricing based on real-time factors."""
        try:
            # Base dynamic price calculation
            dynamic_price = base_price
            
            # Apply market condition adjustments
            market_adjustment = await self._calculate_market_adjustment(market_conditions)
            dynamic_price *= (Decimal('1') + market_adjustment)
            
            # Apply demand-based adjustments
            demand_factor = real_time_factors.get('demand_factor', 1.0)
            demand_adjustment = await self._calculate_demand_adjustment(demand_factor)
            dynamic_price *= (Decimal('1') + demand_adjustment)
            
            # Apply competition-based adjustments
            competition_data = real_time_factors.get('competition_data', {})
            competition_adjustment = await self._calculate_competition_adjustment(
                base_price, competition_data
            )
            dynamic_price *= (Decimal('1') + competition_adjustment)
            
            # Apply time-based adjustments
            time_factor = await self._calculate_time_factor(real_time_factors)
            dynamic_price *= (Decimal('1') + time_factor)
            
            # Ensure price bounds
            min_price = base_price * Decimal('0.7')  # 30% minimum discount
            max_price = base_price * Decimal('1.5')  # 50% maximum premium
            
            final_price = max(min_price, min(max_price, dynamic_price))
            
            return {
                "base_price": float(base_price),
                "dynamic_price": float(final_price),
                "price_adjustment": float(final_price - base_price),
                "adjustment_percentage": float((final_price - base_price) / base_price * 100),
                "adjustments": {
                    "market_adjustment": float(market_adjustment),
                    "demand_adjustment": float(demand_adjustment),
                    "competition_adjustment": float(competition_adjustment),
                    "time_factor": float(time_factor)
                },
                "calculation_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Dynamic pricing calculation failed: {e}")
            raise
    
    async def analyze_price_sensitivity(
        self,
        pricing_experiments: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze price sensitivity from historical experiments."""
        try:
            if not pricing_experiments:
                return {"error": "No pricing experiment data provided"}
            
            # Extract price and conversion data
            price_points = []
            for experiment in pricing_experiments:
                price = float(experiment.get('price', 0))
                conversions = experiment.get('conversions', 0)
                impressions = experiment.get('impressions', 1)
                conversion_rate = conversions / impressions if impressions > 0 else 0
                
                price_points.append({
                    'price': price,
                    'conversion_rate': conversion_rate,
                    'revenue_per_impression': price * conversion_rate
                })
            
            # Sort by price
            price_points.sort(key=lambda x: x['price'])
            
            # Calculate price elasticity
            elasticity_values = []
            for i in range(1, len(price_points)):
                current = price_points[i]
                previous = price_points[i-1]
                
                if previous['price'] > 0 and previous['conversion_rate'] > 0:
                    price_change = (current['price'] - previous['price']) / previous['price']
                    demand_change = (current['conversion_rate'] - previous['conversion_rate']) / previous['conversion_rate']
                    
                    if price_change != 0:
                        elasticity = demand_change / price_change
                        elasticity_values.append(elasticity)
            
            # Calculate average elasticity
            avg_elasticity = statistics.mean(elasticity_values) if elasticity_values else 0
            
            # Find optimal price point
            optimal_point = max(price_points, key=lambda x: x['revenue_per_impression'])
            
            # Calculate sensitivity metrics
            sensitivity_analysis = {
                "price_elasticity": avg_elasticity,
                "optimal_price": optimal_point['price'],
                "optimal_conversion_rate": optimal_point['conversion_rate'],
                "optimal_revenue_per_impression": optimal_point['revenue_per_impression'],
                "price_sensitivity_level": await self._classify_price_sensitivity(avg_elasticity),
                "price_points_analyzed": len(price_points),
                "elasticity_range": {
                    "min": min(elasticity_values) if elasticity_values else 0,
                    "max": max(elasticity_values) if elasticity_values else 0
                }
            }
            
            # Generate insights
            insights = await self._generate_sensitivity_insights(sensitivity_analysis, price_points)
            
            return {
                "sensitivity_analysis": sensitivity_analysis,
                "insights": insights,
                "price_response_curve": price_points,
                "recommendations": await self._generate_sensitivity_recommendations(sensitivity_analysis)
            }
            
        except Exception as e:
            logger.error(f"Price sensitivity analysis failed: {e}")
            raise
    
    async def _analyze_current_performance(
        self,
        current_pricing: Dict[str, Any],
        performance_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze current pricing performance."""
        current_price = Decimal(str(current_pricing.get('base_price', 0)))
        conversion_rate = performance_metrics.get('conversion_rate', 0.05)
        revenue = performance_metrics.get('revenue', 0)
        volume = performance_metrics.get('volume', 0)
        
        # Calculate key performance indicators
        revenue_per_visitor = revenue / max(volume, 1)
        price_per_conversion = float(current_price) if conversion_rate > 0 else 0
        
        return {
            'current_price': float(current_price),
            'conversion_rate': conversion_rate,
            'revenue_per_visitor': revenue_per_visitor,
            'price_per_conversion': price_per_conversion,
            'total_revenue': revenue,
            'total_volume': volume
        }
    
    async def _analyze_market_conditions(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze current market conditions."""
        # Extract market indicators
        competitor_prices = market_data.get('competitor_prices', [])
        market_demand = market_data.get('market_demand', 'stable')
        seasonality = market_data.get('seasonality_factor', 1.0)
        economic_indicators = market_data.get('economic_indicators', {})
        
        # Calculate competitive positioning
        if competitor_prices:
            avg_competitor_price = statistics.mean(competitor_prices)
            min_competitor_price = min(competitor_prices)
            max_competitor_price = max(competitor_prices)
        else:
            avg_competitor_price = min_competitor_price = max_competitor_price = 0
        
        # Assess market conditions
        market_sentiment = await self._assess_market_sentiment(
            market_demand, economic_indicators
        )
        
        return {
            'competitor_analysis': {
                'average_price': avg_competitor_price,
                'price_range': {'min': min_competitor_price, 'max': max_competitor_price},
                'competitor_count': len(competitor_prices)
            },
            'market_demand': market_demand,
            'seasonality_factor': seasonality,
            'market_sentiment': market_sentiment,
            'economic_indicators': economic_indicators
        }
    
    async def _calculate_demand_elasticity(
        self,
        current_pricing: Dict[str, Any],
        performance_metrics: Dict[str, Any]
    ) -> float:
        """Calculate demand elasticity for current pricing."""
        # Use historical data or estimates
        price_changes = performance_metrics.get('price_changes', [])
        demand_changes = performance_metrics.get('demand_changes', [])
        
        if len(price_changes) >= 2 and len(demand_changes) >= 2:
            # Calculate elasticity from historical data
            elasticity_values = []
            for i in range(1, min(len(price_changes), len(demand_changes))):
                price_change_pct = price_changes[i] / max(price_changes[i-1], 0.01) - 1
                demand_change_pct = demand_changes[i] / max(demand_changes[i-1], 0.01) - 1
                
                if price_change_pct != 0:
                    elasticity = demand_change_pct / price_change_pct
                    elasticity_values.append(elasticity)
            
            if elasticity_values:
                return statistics.mean(elasticity_values)
        
        # Default elasticity based on industry estimates
        content_type = current_pricing.get('content_type', 'general')
        default_elasticities = {
            'premium': -1.8,    # Premium content is more elastic
            'standard': -1.2,   # Standard elasticity
            'basic': -0.8,      # Basic content is less elastic
            'general': -1.2
        }
        
        return default_elasticities.get(content_type, -1.2)
    
    async def _generate_pricing_scenarios(
        self,
        current_pricing: Dict[str, Any],
        market_analysis: Dict[str, Any],
        demand_elasticity: float
    ) -> List[Dict[str, Any]]:
        """Generate multiple pricing scenarios for evaluation."""
        base_price = Decimal(str(current_pricing.get('base_price', 0)))
        scenarios = []
        
        # Price adjustment ranges
        adjustments = [-0.20, -0.10, -0.05, 0.05, 0.10, 0.15, 0.20, 0.25]
        
        for adjustment in adjustments:
            new_price = base_price * (Decimal('1') + Decimal(str(adjustment)))
            
            # Estimate demand change using elasticity
            demand_change = demand_elasticity * adjustment
            
            # Calculate scenario metrics
            scenario = {
                'adjustment': adjustment,
                'price': new_price,
                'expected_demand_change': demand_change,
                'strategy': await self._determine_strategy_for_adjustment(adjustment),
                'competitive_position': await self._assess_competitive_position(
                    new_price, market_analysis
                )
            }
            
            scenarios.append(scenario)
        
        return scenarios
    
    async def _evaluate_pricing_scenarios(
        self,
        scenarios: List[Dict[str, Any]],
        market_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Evaluate pricing scenarios for revenue impact."""
        evaluated_scenarios = []
        
        for scenario in scenarios:
            # Calculate revenue impact
            revenue_impact = await self._calculate_revenue_impact(scenario, market_analysis)
            
            # Calculate risk assessment
            risk_score = await self._assess_pricing_risk(scenario, market_analysis)
            
            # Calculate confidence score
            confidence = await self._calculate_scenario_confidence(scenario, market_analysis)
            
            evaluated_scenario = {
                **scenario,
                'revenue_impact': revenue_impact,
                'risk_score': risk_score,
                'confidence': confidence,
                'overall_score': await self._calculate_overall_score(
                    revenue_impact, risk_score, confidence
                )
            }
            
            evaluated_scenarios.append(evaluated_scenario)
        
        return evaluated_scenarios
    
    async def _calculate_revenue_impact(
        self,
        scenario: Dict[str, Any],
        market_analysis: Dict[str, Any]
    ) -> float:
        """Calculate expected revenue impact of pricing scenario."""
        price_change = scenario['adjustment']
        demand_change = scenario['expected_demand_change']
        
        # Basic revenue impact calculation
        # Revenue = Price × Quantity
        # % Change in Revenue ≈ % Change in Price + % Change in Quantity
        revenue_impact = price_change + demand_change
        
        # Adjust for market conditions
        market_sentiment = market_analysis.get('market_sentiment', 'neutral')
        if market_sentiment == 'positive' and price_change > 0:
            revenue_impact *= 1.1  # 10% boost for positive market in price increases
        elif market_sentiment == 'negative' and price_change < 0:
            revenue_impact *= 1.05  # 5% boost for negative market in price decreases
        
        # Adjust for seasonality
        seasonality = market_analysis.get('seasonality_factor', 1.0)
        if seasonality > 1.0 and price_change > 0:
            revenue_impact *= 1.05  # Seasonal boost for price increases
        
        return revenue_impact
    
    async def _assess_pricing_risk(
        self,
        scenario: Dict[str, Any],
        market_analysis: Dict[str, Any]
    ) -> float:
        """Assess risk level of pricing scenario."""
        base_risk = 0.1  # 10% base risk
        
        price_change = abs(scenario['adjustment'])
        
        # Higher price changes carry more risk
        risk_multiplier = 1 + (price_change * 2)  # 2x risk for each 100% price change
        
        # Market condition adjustments
        market_sentiment = market_analysis.get('market_sentiment', 'neutral')
        if market_sentiment == 'negative':
            risk_multiplier *= 1.3  # 30% higher risk in negative market
        elif market_sentiment == 'positive':
            risk_multiplier *= 0.8  # 20% lower risk in positive market
        
        # Competitive position risk
        competitive_position = scenario.get('competitive_position', 'neutral')
        if competitive_position == 'above_market':
            risk_multiplier *= 1.2  # Higher risk when pricing above market
        elif competitive_position == 'below_market':
            risk_multiplier *= 0.9  # Lower risk when pricing below market
        
        final_risk = min(1.0, base_risk * risk_multiplier)  # Cap at 100%
        
        return final_risk
    
    async def _calculate_scenario_confidence(
        self,
        scenario: Dict[str, Any],
        market_analysis: Dict[str, Any]
    ) -> float:
        """Calculate confidence score for pricing scenario."""
        base_confidence = 0.7  # 70% base confidence
        
        # Data quality factor
        competitor_count = market_analysis.get('competitor_analysis', {}).get('competitor_count', 0)
        data_quality_factor = min(1.0, competitor_count / 5.0)  # Better confidence with more data
        
        # Market stability factor
        market_demand = market_analysis.get('market_demand', 'stable')
        if market_demand == 'stable':
            stability_factor = 1.0
        elif market_demand in ['growing', 'high']:
            stability_factor = 1.1
        else:
            stability_factor = 0.9
        
        # Price change magnitude factor
        price_change_magnitude = abs(scenario['adjustment'])
        if price_change_magnitude <= 0.1:  # Small changes are more predictable
            magnitude_factor = 1.1
        elif price_change_magnitude <= 0.2:
            magnitude_factor = 1.0
        else:
            magnitude_factor = 0.9
        
        final_confidence = min(0.95, base_confidence * data_quality_factor * stability_factor * magnitude_factor)
        
        return final_confidence
    
    async def _calculate_overall_score(
        self,
        revenue_impact: float,
        risk_score: float,
        confidence: float
    ) -> float:
        """Calculate overall score for pricing scenario."""
        # Weighted scoring: Revenue impact (50%), Risk (30%), Confidence (20%)
        risk_adjusted_impact = revenue_impact * (1 - risk_score)
        overall_score = (risk_adjusted_impact * 0.5) + (confidence * 0.5)
        
        return overall_score
    
    async def _select_optimal_pricing(
        self,
        evaluated_scenarios: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Select optimal pricing scenario."""
        # Sort by overall score
        sorted_scenarios = sorted(
            evaluated_scenarios,
            key=lambda x: x['overall_score'],
            reverse=True
        )
        
        return sorted_scenarios[0] if sorted_scenarios else {}
    
    async def _generate_pricing_recommendations(
        self,
        optimal_scenario: Dict[str, Any]
    ) -> List[str]:
        """Generate pricing recommendations."""
        recommendations = []
        
        adjustment = optimal_scenario.get('adjustment', 0)
        
        if adjustment > 0.15:
            recommendations.extend([
                "Implement price increase gradually over 2-3 weeks",
                "Monitor conversion rate closely during transition",
                "Prepare value justification messaging for customers"
            ])
        elif adjustment > 0:
            recommendations.extend([
                "Implement moderate price increase",
                "A/B test new pricing with small customer segment first"
            ])
        elif adjustment < -0.1:
            recommendations.extend([
                "Consider promotional pricing strategy",
                "Ensure sufficient margin for sustainable pricing",
                "Set time limit for promotional pricing"
            ])
        else:
            recommendations.append("Current pricing appears optimal")
        
        # Strategy-specific recommendations
        strategy = optimal_scenario.get('strategy', PricingStrategy.DYNAMIC)
        if strategy == PricingStrategy.PREMIUM:
            recommendations.append("Focus on premium value proposition and quality")
        elif strategy == PricingStrategy.COMPETITIVE:
            recommendations.append("Monitor competitor pricing closely")
        elif strategy == PricingStrategy.PENETRATION:
            recommendations.append("Plan pricing increase strategy for future")
        
        return recommendations
    
    async def _store_optimization(self, optimization: PricingOptimization) -> None:
        """Store pricing optimization result."""
        optimization_record = {
            'optimization_id': optimization.optimization_id,
            'creator_id': self.creator_id,
            'timestamp': datetime.utcnow().isoformat(),
            'current_price': float(optimization.current_price),
            'optimal_price': float(optimization.optimal_price),
            'expected_impact': optimization.expected_revenue_impact,
            'confidence': optimization.confidence_score,
            'strategy': optimization.strategy.value
        }
        
        self.pricing_history.append(optimization_record)
        
        # Keep only last 100 optimizations
        if len(self.pricing_history) > 100:
            self.pricing_history = self.pricing_history[-100:]
        
        logger.info(f"Stored pricing optimization {optimization.optimization_id}")
    
    # Helper methods for dynamic pricing
    async def _calculate_market_adjustment(self, market_conditions: Dict[str, Any]) -> Decimal:
        """Calculate market-based pricing adjustment."""
        market_demand = market_conditions.get('market_demand', 'stable')
        
        adjustments = {
            'very_high': Decimal('0.15'),
            'high': Decimal('0.10'),
            'growing': Decimal('0.05'),
            'stable': Decimal('0.00'),
            'declining': Decimal('-0.05'),
            'low': Decimal('-0.10'),
            'very_low': Decimal('-0.15')
        }
        
        return adjustments.get(market_demand, Decimal('0.00'))
    
    async def _calculate_demand_adjustment(self, demand_factor: float) -> Decimal:
        """Calculate demand-based pricing adjustment."""
        # demand_factor > 1.0 means higher than normal demand
        if demand_factor > 1.5:
            return Decimal('0.20')  # High demand surge
        elif demand_factor > 1.2:
            return Decimal('0.10')  # Moderate demand increase
        elif demand_factor > 1.0:
            return Decimal('0.05')  # Slight demand increase
        elif demand_factor < 0.5:
            return Decimal('-0.20')  # Low demand
        elif demand_factor < 0.8:
            return Decimal('-0.10')  # Below normal demand
        else:
            return Decimal('0.00')  # Normal demand
    
    async def _calculate_competition_adjustment(
        self,
        base_price: Decimal,
        competition_data: Dict[str, Any]
    ) -> Decimal:
        """Calculate competition-based pricing adjustment."""
        competitor_prices = competition_data.get('prices', [])
        
        if not competitor_prices:
            return Decimal('0.00')
        
        avg_competitor_price = Decimal(str(statistics.mean(competitor_prices)))
        
        # Calculate relative position
        if base_price > avg_competitor_price * Decimal('1.1'):
            return Decimal('-0.05')  # Lower price if significantly above market
        elif base_price < avg_competitor_price * Decimal('0.9'):
            return Decimal('0.03')  # Raise price if significantly below market
        else:
            return Decimal('0.00')  # Keep current pricing
    
    async def _calculate_time_factor(self, real_time_factors: Dict[str, Any]) -> Decimal:
        """Calculate time-based pricing adjustments."""
        current_hour = datetime.utcnow().hour
        day_of_week = datetime.utcnow().weekday()
        
        # Peak hours adjustment (business hours)
        if 9 <= current_hour <= 17:
            time_adjustment = Decimal('0.02')
        elif 18 <= current_hour <= 22:  # Evening premium
            time_adjustment = Decimal('0.05')
        else:
            time_adjustment = Decimal('-0.02')  # Off-peak discount
        
        # Weekend adjustment
        if day_of_week >= 5:  # Saturday or Sunday
            time_adjustment += Decimal('0.03')
        
        return time_adjustment
    
    async def _assess_market_sentiment(
        self,
        market_demand: str,
        economic_indicators: Dict[str, Any]
    ) -> str:
        """Assess overall market sentiment."""
        # Combine market demand and economic indicators
        demand_score = {
            'very_high': 5, 'high': 4, 'growing': 3,
            'stable': 2, 'declining': 1, 'low': 0, 'very_low': -1
        }.get(market_demand, 2)
        
        # Economic indicators (simplified)
        economic_score = 2  # Default neutral
        if economic_indicators.get('growth_rate', 0) > 0.03:
            economic_score += 1
        elif economic_indicators.get('growth_rate', 0) < 0:
            economic_score -= 1
        
        combined_score = (demand_score + economic_score) / 2
        
        if combined_score >= 3.5:
            return 'positive'
        elif combined_score <= 1.5:
            return 'negative'
        else:
            return 'neutral'
    
    async def _determine_strategy_for_adjustment(self, adjustment: float) -> PricingStrategy:
        """Determine pricing strategy based on adjustment."""
        if adjustment >= 0.2:
            return PricingStrategy.PREMIUM
        elif adjustment >= 0.05:
            return PricingStrategy.VALUE_BASED
        elif adjustment <= -0.15:
            return PricingStrategy.PENETRATION
        elif adjustment <= -0.05:
            return PricingStrategy.COMPETITIVE
        else:
            return PricingStrategy.DYNAMIC
    
    async def _assess_competitive_position(
        self,
        price: Decimal,
        market_analysis: Dict[str, Any]
    ) -> str:
        """Assess competitive position for given price."""
        competitor_analysis = market_analysis.get('competitor_analysis', {})
        avg_competitor_price = competitor_analysis.get('average_price', 0)
        
        if avg_competitor_price == 0:
            return 'unknown'
        
        price_ratio = float(price) / avg_competitor_price
        
        if price_ratio > 1.15:
            return 'above_market'
        elif price_ratio < 0.85:
            return 'below_market'
        else:
            return 'market_aligned'
    
    async def _classify_price_sensitivity(self, elasticity: float) -> str:
        """Classify price sensitivity level."""
        if elasticity < -2.0:
            return 'highly_sensitive'
        elif elasticity < -1.5:
            return 'moderately_sensitive'
        elif elasticity < -1.0:
            return 'somewhat_sensitive'
        else:
            return 'relatively_insensitive'
    
    async def _generate_sensitivity_insights(
        self,
        sensitivity_analysis: Dict[str, Any],
        price_points: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate insights from price sensitivity analysis."""
        insights = []
        
        elasticity = sensitivity_analysis['price_elasticity']
        sensitivity_level = sensitivity_analysis['price_sensitivity_level']
        
        insights.append(f"Price elasticity of {elasticity:.2f} indicates {sensitivity_level} demand")
        
        if elasticity < -1.5:
            insights.append("Customers are highly price-sensitive - focus on value optimization")
        elif elasticity > -0.5:
            insights.append("Low price sensitivity allows for premium pricing strategies")
        
        # Analyze price-revenue relationship
        max_revenue_point = max(price_points, key=lambda x: x['revenue_per_impression'])
        insights.append(f"Revenue is maximized at ${max_revenue_point['price']:.2f} price point")
        
        return insights
    
    async def _generate_sensitivity_recommendations(
        self,
        sensitivity_analysis: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations based on price sensitivity."""
        recommendations = []
        
        sensitivity_level = sensitivity_analysis['price_sensitivity_level']
        
        if sensitivity_level == 'highly_sensitive':
            recommendations.extend([
                "Focus on cost optimization rather than price increases",
                "Consider value-added bundling strategies",
                "Implement gradual pricing changes with strong value justification"
            ])
        elif sensitivity_level == 'relatively_insensitive':
            recommendations.extend([
                "Consider premium pricing strategy",
                "Test higher price points for revenue optimization",
                "Focus on quality and premium positioning"
            ])
        else:
            recommendations.extend([
                "Implement dynamic pricing based on demand",
                "Test price changes in small increments",
                "Monitor competitive pricing closely"
            ])
        
        optimal_price = sensitivity_analysis['optimal_price']
        recommendations.append(f"Target price point around ${optimal_price:.2f} for revenue optimization")
        
        return recommendations