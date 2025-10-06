"""
Market Intelligence Module - Advanced Market Analysis & Competitive Intelligence
================================================================================

Real-time market trend analysis, competitive intelligence gathering,
forecasting engines, and dynamic pricing optimization.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Set, Tuple
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
from dataclasses import dataclass, field
from enum import Enum
import json
import statistics
from collections import defaultdict, deque
import numpy as np

logger = logging.getLogger(__name__)


class MarketSegment(Enum):
    """
        Market segments"""
    ENTERPRISE = "enterprise"
    SMB = "smb"
    STARTUP = "startup"
    INDIVIDUAL = "individual"
    INFLUENCER = "influencer"
    CREATOR = "creator"
    AGENCY = "agency"


class TrendDirection(Enum):
    """Trend direction indicators"""
    RISING = "rising"
    FALLING = "falling"
    STABLE = "stable"
    VOLATILE = "volatile"


class CompetitorTier(Enum):
    """Competitor classification"""
    DIRECT = "direct"
    INDIRECT = "indirect"
    SUBSTITUTE = "substitute"
    POTENTIAL = "potential"


@dataclass
class MarketTrend:
    """Market trend data"""
    trend_id: str
    name: str
    category: str
    direction: TrendDirection
    momentum: float
    confidence: float
    data_points: List[float] = field(default_factory=list)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    forecast: Optional[List[float]] = None
    volatility: float = 0.0
    
    
@dataclass
class CompetitorProfile:
    """
        Competitor intelligence profile"""
    competitor_id: str
    name: str
    tier: CompetitorTier
    market_share: float
    pricing_strategy: Dict[str, Any]
    strengths: List[str]
    weaknesses: List[str]
    products: List[Dict[str, Any]]
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class PricingRecommendation:
    """
        Pricing strategy recommendation"""
    product_id: str
    current_price: Decimal
    recommended_price: Decimal
    expected_revenue_impact: Decimal
    confidence: float
    reasoning: List[str]
    elasticity: float
    competitive_position: str


class MarketTrendAnalyzer:
    """
        Advanced market trend analysis and prediction"""
    
    def __init__(self):
        self.trends: Dict[str, MarketTrend] = {}
        self.historical_data: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.segments: Dict[MarketSegment, Dict[str, Any]] = {}
        self.alerts: List[Dict[str, Any]] = []
        logger.info("MarketTrendAnalyzer initialized")
    
    async def analyze_trend(
        self,
        trend_name: str,
        data_points: List[float],
        category: str = "general"
    ) -> MarketTrend:
        """Analyze market trend from data points"""
        
        if len(data_points) < 3:
            direction = TrendDirection.STABLE
            momentum = 0.0

            volatility = 0.0
        else:
            recent = data_points[-10:]

            direction = self._calculate_direction(recent)


            momentum = self._calculate_momentum(recent)


            volatility = statistics.stdev(recent) if len(recent) > 1 else 0.0

        
        confidence = min(len(data_points) / 100.0, 1.0)


        
        forecast = await self._generate_forecast(data_points)


        
        trend = MarketTrend(
            trend_id=f"trend_{trend_name}_{datetime.now().timestamp()}",
            name=trend_name,
            category=category,
            direction=direction,
            momentum=momentum,
            confidence=confidence,
            data_points=data_points,
            forecast=forecast,
            volatility=volatility
        )

        
        self.trends[trend.trend_id] = trend
        self.historical_data[trend_name].extend(data_points)

        
        if volatility > 0.3:
            self.alerts.append({
                "type": "high_volatility",
                "trend": trend_name,
                "volatility": volatility,
                "timestamp": datetime.now(timezone.utc)
            })

        
        logger.info(f"Trend analyzed: {trend_name} - {direction.value}, momentum: {momentum:.2f}")
        return trend
    
    def _calculate_direction(self, data: List[float]) -> TrendDirection:
        """Calculate trend direction"""
        if len(data) < 2:
            return TrendDirection.STABLE
        
        slope = (data[-1] - data[0]) / len(data)

        volatility = statistics.stdev(data) if len(data) > 1 else 0
        
        if volatility > abs(slope) * 2:
            return TrendDirection.VOLATILE
        elif slope > 0.05:
            return TrendDirection.RISING
        elif slope < -0.05:
            return TrendDirection.FALLING
        else:
            return TrendDirection.STABLE
    
    def _calculate_momentum(self, data: List[float]) -> float:
        """
        Calculate trend momentum"""
        if len(data) < 2:
            return 0.0

        
        changes = [data[i+1] - data[i] for i in range(len(data)-1)]

        recent_momentum = statistics.mean(changes[-5:]) if len(changes) >= 5 else statistics.mean(changes)

        
        return max(-1.0, min(1.0, recent_momentum))
    
    async def _generate_forecast(self, historical: List[float], periods: int = 10) -> List[float]:
        """
        Generate simple forecast using exponential smoothing"""
        if len(historical) < 3:
            return [historical[-1]] * periods if historical else [0.0] * periods

        
        alpha = 0.3

        forecast = []

        last_value = historical[-1]

        last_trend = (historical[-1] - historical[-2]) if len(historical) >= 2 else 0
        
        for _ in range(periods):
            next_value = last_value + last_trend
            forecast.append(next_value)


            last_value = alpha * next_value + (1 - alpha) * last_value
            last_trend *= 0.9
        
        return forecast
    
    async def detect_anomalies(self, trend_name: str) -> List[Dict[str, Any]]:
        """
        Detect anomalies in trend data"""
        anomalies = []
        
        if trend_name not in self.historical_data:
            return anomalies

        
        data = list(self.historical_data[trend_name])
        if len(data) < 10:
            return anomalies

        
        mean = statistics.mean(data)

        std = statistics.stdev(data)

        threshold = 2.5 * std
        
        for i, value in enumerate(data):
            if abs(value - mean) > threshold:
                anomalies.append({
                    "index": i,
                    "value": value,
                    "deviation": abs(value - mean) / std,
                    "type": "outlier"
                })

        
        return anomalies
    
    async def segment_analysis(self, segment: MarketSegment) -> Dict[str, Any]:
        """Analyze specific market segment"""
        segment_trends = {k: v for k, v in self.trends.items() if segment.value in v.category}
        
        if not segment_trends:
            return {
                "segment": segment.value,
                "trend_count": 0,
                "average_momentum": 0.0,
                "dominant_direction": "stable",
                "opportunities": []
            }

        
        momentums = [t.momentum for t in segment_trends.values()]

        directions = [t.direction for t in segment_trends.values()]

        
        direction_counts = {}
        for d in directions:
            direction_counts[d.value] = direction_counts.get(d.value, 0) + 1

        
        dominant = max(direction_counts.items(), key=lambda x: x[1])[0]

        
        opportunities = []
        for trend in segment_trends.values():
            if trend.direction == TrendDirection.RISING and trend.momentum > 0.3:
                opportunities.append({
                    "trend": trend.name,
                    "momentum": trend.momentum,
                    "confidence": trend.confidence
                })

        
        return {
            "segment": segment.value,
            "trend_count": len(segment_trends),
            "average_momentum": statistics.mean(momentums) if momentums else 0.0,
            "dominant_direction": dominant,
            "opportunities": sorted(opportunities, key=lambda x: x["momentum"], reverse=True)[:5]
        }


class ForecastingEngine:
    """Advanced forecasting with multiple models"""
    
    def __init__(self):
        self.models: Dict[str, Any] = {}
        self.forecasts: Dict[str, List[float]] = {}
        self.accuracy_history: Dict[str, List[float]] = defaultdict(list)
        logger.info("ForecastingEngine initialized")
    
    async def generate_forecast(
        self,
        historical_data: List[float],
        periods: int = 30,
        model_type: str = "ensemble"
    ) -> Dict[str, Any]:
        """Generate multi-model forecast"""
        
        if len(historical_data) < 10:
            simple_forecast = [historical_data[-1]] * periods if historical_data else [0.0] * periods
            return {
                "forecast": simple_forecast,
                "confidence_intervals": [(v*0.9, v*1.1) for v in simple_forecast],
                "model": "simple",
                "accuracy": 0.5
            }

        
        forecasts = {}
        forecasts["linear"] = await self._linear_forecast(historical_data, periods)
        forecasts["exponential"] = await self._exponential_forecast(historical_data, periods)
        forecasts["moving_average"] = await self._moving_average_forecast(historical_data, periods)

        
        if model_type == "ensemble":
            final_forecast = [
                statistics.mean([forecasts[m][i] for m in forecasts])

                for i in range(periods)
            ]
        else:
            final_forecast = forecasts.get(model_type, forecasts["exponential"])


        
        confidence_intervals = self._calculate_confidence_intervals(final_forecast, historical_data)


        
        accuracy = self._estimate_accuracy(historical_data)

        
        return {
            "forecast": final_forecast,
            "confidence_intervals": confidence_intervals,
            "model": model_type,
            "accuracy": accuracy,
            "individual_models": forecasts
        }
    
    async def _linear_forecast(self, data: List[float], periods: int) -> List[float]:
        """Linear regression forecast"""
        n = len(data)

        x = np.arange(n)

        y = np.array(data)


        
        slope = (n * np.sum(x * y) - np.sum(x) * np.sum(y)) / (n * np.sum(x**2) - np.sum(x)**2)

        intercept = (np.sum(y) - slope * np.sum(x)) / n

        
        forecast = [slope * (n + i) + intercept for i in range(periods)]
        return forecast
    
    async def _exponential_forecast(self, data: List[float], periods: int) -> List[float]:
        """
        Exponential smoothing forecast"""
        alpha = 0.3

        beta = 0.1

        
        level = data[0]

        trend = (data[-1] - data[0]) / len(data)


        
        forecast = []
        for _ in range(periods):
            next_val = level + trend
            forecast.append(next_val)


            
            new_level = alpha * next_val + (1 - alpha) * (level + trend)


            trend = beta * (new_level - level) + (1 - beta) * trend

            level = new_level
        
        return forecast
    
    async def _moving_average_forecast(self, data: List[float], periods: int, window: int = 10) -> List[float]:
        """
        Moving average forecast"""
        recent = data[-window:]

        avg = statistics.mean(recent)

        trend = (data[-1] - data[-window]) / window

        
        forecast = [avg + trend * (i + 1) for i in range(periods)]
        return forecast
    
    def _calculate_confidence_intervals(
        self,
        forecast: List[float],
        historical: List[float],
        confidence: float = 0.95
    ) -> List[Tuple[float, float]]:
        """
        Calculate confidence intervals for forecast"""
        std = statistics.stdev(historical) if len(historical) > 1 else 0

        z_score = 1.96

        
        intervals = []
        for i, value in enumerate(forecast):
            margin = z_score * std * (1 + i * 0.1)

            intervals.append((value - margin, value + margin))

        
        return intervals
    
    def _estimate_accuracy(self, historical: List[float]) -> float:
        """
        Estimate forecast accuracy based on historical performance"""
        if len(historical) < 20:
            return 0.6

        
        test_size = len(historical) // 4

        train = historical[:-test_size]

        test = historical[-test_size:]
        
        try:
            errors = []
            for i in range(len(test)):
                predicted = statistics.mean(train[-10:])


                actual = test[i]

                error = abs(predicted - actual) / (actual + 1e-6)

                errors.append(error)


            
            avg_error = statistics.mean(errors)


            accuracy = max(0.0, min(1.0, 1.0 - avg_error))

            return accuracy
        except:
            return 0.7


class CompetitiveIntelligenceGatherer:
    """
        Competitive intelligence and market positioning"""
    
    def __init__(self):
        self.competitors: Dict[str, CompetitorProfile] = {}
        self.market_share_history: Dict[str, List[float]] = defaultdict(list)
        self.intelligence_reports: List[Dict[str, Any]] = []
        logger.info("CompetitiveIntelligenceGatherer initialized")
    
    async def add_competitor(
        self,
        name: str,
        tier: CompetitorTier,
        market_share: float,
        pricing: Dict[str, Any],
        products: List[Dict[str, Any]]
    ) -> CompetitorProfile:
        """Add or update competitor profile"""
        
        competitor_id = f"comp_{name.lower().replace(' ', '_')}"
        
        strengths = self._analyze_strengths(pricing, products, market_share)

        weaknesses = self._analyze_weaknesses(pricing, products, market_share)


        
        profile = CompetitorProfile(
            competitor_id=competitor_id,
            name=name,
            tier=tier,
            market_share=market_share,
            pricing_strategy=pricing,
            strengths=strengths,
            weaknesses=weaknesses,
            products=products
        )

        
        self.competitors[competitor_id] = profile
        self.market_share_history[competitor_id].append(market_share)

        
        logger.info(f"Competitor added: {name} ({tier.value}), market share: {market_share:.1%}")
        return profile
    
    def _analyze_strengths(
        self,
        pricing: Dict[str, Any],
        products: List[Dict[str, Any]],
        market_share: float
    ) -> List[str]:
        """Analyze competitor strengths"""
        strengths = []
        
        if market_share > 0.15:
            strengths.append("Strong market presence")

        
        if len(products) > 10:
            strengths.append("Diverse product portfolio")


        
        avg_price = pricing.get("average_price", 0)
        if avg_price > 0 and avg_price < 50:
            strengths.append("Competitive pricing")

        
        if pricing.get("discount_frequency", 0) > 0.3:
            strengths.append("Aggressive promotional strategy")

        
        return strengths if strengths else ["Standard market position"]
    
    def _analyze_weaknesses(
        self,
        pricing: Dict[str, Any],
        products: List[Dict[str, Any]],
        market_share: float
    ) -> List[str]:
        """Analyze competitor weaknesses"""
        weaknesses = []
        
        if market_share < 0.05:
            weaknesses.append("Limited market penetration")

        
        if len(products) < 3:
            weaknesses.append("Narrow product range")


        
        price_variance = pricing.get("price_variance", 0)
        if price_variance > 0.3:
            weaknesses.append("Inconsistent pricing strategy")

        
        return weaknesses if weaknesses else ["No obvious weaknesses detected"]
    
    async def generate_competitive_report(self) -> Dict[str, Any]:
        """Generate comprehensive competitive intelligence report"""
        
        if not self.competitors:
            return {
                "total_competitors": 0,
                "market_concentration": 0.0,
                "competitive_intensity": "low",
                "threats": [],
                "opportunities": []
            }

        
        market_shares = [c.market_share for c in self.competitors.values()]

        hhi = sum(share ** 2 for share in market_shares)


        
        direct_competitors = [c for c in self.competitors.values() if c.tier == CompetitorTier.DIRECT]

        
        threats = []

        opportunities = []
        
        for comp in self.competitors.values():
            if comp.market_share > 0.2:
                threats.append(f"{comp.name}: Dominant market position ({comp.market_share:.1%})")

            
            if len(comp.weaknesses) > len(comp.strengths):
                opportunities.append(f"{comp.name}: Multiple exploitable weaknesses")


        
        competitive_intensity = "high" if hhi < 0.15 else "medium" if hhi < 0.25 else "low"
        
        return {
            "total_competitors": len(self.competitors),
            "direct_competitors": len(direct_competitors),
            "market_concentration": hhi,
            "competitive_intensity": competitive_intensity,
            "threats": threats[:5],
            "opportunities": opportunities[:5],
            "market_leader": max(self.competitors.values(), key=lambda c: c.market_share).name if self.competitors else None
        }
    
    async def benchmark_position(
        self,
        our_market_share: float,
        our_pricing: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Benchmark our position against competitors"""
        
        if not self.competitors:
            return {
                "market_position": "unknown",
                "price_position": "unknown",
                "recommendations": ["Gather competitive intelligence"]
            }

        
        competitors_by_share = sorted(self.competitors.values(), key=lambda c: c.market_share, reverse=True)

        our_rank = sum(1 for c in competitors_by_share if c.market_share > our_market_share) + 1

        
        avg_competitor_price = statistics.mean([
            c.pricing_strategy.get("average_price", 0)

            for c in self.competitors.values()
        ])

        our_price = our_pricing.get("average_price", 0)


        
        price_position = "premium" if our_price > avg_competitor_price * 1.2 else \
                        "competitive" if our_price > avg_competitor_price * 0.8 else "discount"
        
        recommendations = []
        if our_rank > len(competitors_by_share) / 2:
            recommendations.append("Focus on market share growth")
        if price_position == "premium" and our_market_share < 0.1:
            recommendations.append("Consider price adjustment or value demonstration")

        
        return {
            "market_position": f"#{our_rank} of {len(competitors_by_share) + 1}",
            "market_share": our_market_share,
            "price_position": price_position,
            "price_vs_average": (our_price / avg_competitor_price - 1) if avg_competitor_price else 0,
            "recommendations": recommendations
        }


class PricingStrategyOptimizer:
    """Dynamic pricing optimization based on market intelligence"""
    
    def __init__(self):
        self.pricing_rules: Dict[str, Dict[str, Any]] = {}
        self.price_history: Dict[str, List[Tuple[datetime, Decimal]]] = defaultdict(list)
        self.elasticity_data: Dict[str, float] = {}
        logger.info("PricingStrategyOptimizer initialized")
    
    async def optimize_price(
        self,
        product_id: str,
        current_price: Decimal,
        demand_data: List[float],
        competitor_prices: List[Decimal],
        cost: Decimal
    ) -> PricingRecommendation:
        """Optimize pricing based on multiple factors"""
        
        elasticity = await self._calculate_elasticity(product_id, demand_data)

        competitive_position = await self._analyze_competitive_position(current_price, competitor_prices)


        
        optimal_price = await self._calculate_optimal_price(
            current_price, elasticity, competitor_prices, cost
        )


        
        revenue_impact = await self._estimate_revenue_impact(
            current_price, optimal_price, elasticity, demand_data
        )


        
        reasoning = self._generate_reasoning(
            current_price, optimal_price, elasticity,
            competitive_position, revenue_impact
        )


        
        confidence = self._calculate_confidence(len(demand_data), elasticity)


        
        recommendation = PricingRecommendation(
            product_id=product_id,
            current_price=current_price,
            recommended_price=optimal_price,
            expected_revenue_impact=revenue_impact,
            confidence=confidence,
            reasoning=reasoning,
            elasticity=elasticity,
            competitive_position=competitive_position
        )

        
        self.price_history[product_id].append((datetime.now(timezone.utc), optimal_price))

        
        logger.info(f"Price optimized for {product_id}: ${current_price} → ${optimal_price}")
        return recommendation
    
    async def _calculate_elasticity(
        self,
        product_id: str,
        demand_data: List[float]
    ) -> float:
        """Calculate price elasticity of demand"""
        
        if product_id in self.elasticity_data:
            return self.elasticity_data[product_id]
        
        if len(demand_data) < 10:
            default_elasticity = -1.2
            self.elasticity_data[product_id] = default_elasticity
            return default_elasticity

        
        price_changes = [0.05, -0.05, 0.10, -0.10]

        demand_responses = demand_data[-4:] if len(demand_data) >= 4 else demand_data
        
        if len(demand_responses) >= 2:
            elasticities = []
            for i in range(len(demand_responses) - 1):
                price_change_pct = price_changes[i] if i < len(price_changes) else 0.05

                demand_change_pct = (demand_responses[i+1] - demand_responses[i]) / (demand_responses[i] + 1e-6)

                
                if price_change_pct != 0:
                    elasticity = demand_change_pct / price_change_pct
                    elasticities.append(elasticity)


            
            avg_elasticity = statistics.mean(elasticities) if elasticities else -1.2
            self.elasticity_data[product_id] = avg_elasticity
            return avg_elasticity
        
        return -1.2
    
    async def _analyze_competitive_position(
        self,
        our_price: Decimal,
        competitor_prices: List[Decimal]
    ) -> str:
        """
        Analyze our price position vs competitors"""
        
        if not competitor_prices:
            return "no_competition"
        
        avg_competitor = sum(competitor_prices) / len(competitor_prices)

        
        if our_price > avg_competitor * Decimal("1.2"):
            return "premium"
        elif our_price > avg_competitor * Decimal("0.8"):
            return "competitive"
        else:
            return "discount"
    
    async def _calculate_optimal_price(
        self,
        current_price: Decimal,
        elasticity: float,
        competitor_prices: List[Decimal],
        cost: Decimal
    ) -> Decimal:
        """Calculate optimal price point"""
        
        min_price = cost * Decimal("1.2")

        
        if competitor_prices:
            avg_competitor = sum(competitor_prices) / len(competitor_prices)


            market_price = avg_competitor * Decimal("0.95")
        else:
            market_price = current_price
        
        if abs(elasticity) > 1.5:
            elasticity_optimal = cost / Decimal(str(1 + 1/abs(elasticity)))
        else:
            elasticity_optimal = current_price * Decimal("1.05")


        
        candidates = [
            max(min_price, market_price),
            max(min_price, elasticity_optimal),
            max(min_price, current_price * Decimal("0.95")),
            max(min_price, current_price * Decimal("1.05"))
        ]

        
        optimal = sum(candidates) / len(candidates)

        optimal = optimal.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        
        return max(min_price, optimal)
    
    async def _estimate_revenue_impact(
        self,
        current_price: Decimal,
        new_price: Decimal,
        elasticity: float,
        demand_data: List[float]
    ) -> Decimal:
        """Estimate revenue impact of price change"""
        
        price_change_pct = float((new_price - current_price) / current_price)

        demand_change_pct = elasticity * price_change_pct

        
        current_demand = statistics.mean(demand_data[-10:]) if len(demand_data) >= 10 else 100.0

        new_demand = current_demand * (1 + demand_change_pct)


        
        current_revenue = current_price * Decimal(str(current_demand))

        new_revenue = new_price * Decimal(str(new_demand))


        
        impact = new_revenue - current_revenue
        return impact.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    
    def _generate_reasoning(
        self,
        current_price: Decimal,
        optimal_price: Decimal,
        elasticity: float,
        competitive_position: str,
        revenue_impact: Decimal
    ) -> List[str]:
        """Generate human-readable reasoning"""
        reasoning = []

        
        price_diff_pct = float((optimal_price - current_price) / current_price * 100)

        
        if abs(price_diff_pct) < 2:
            reasoning.append("Current price is near optimal")
        elif price_diff_pct > 0:
            reasoning.append(f"Price increase of {price_diff_pct:.1f}% recommended")
        else:
            reasoning.append(f"Price decrease of {abs(price_diff_pct):.1f}% recommended")

        
        if abs(elasticity) > 1.5:
            reasoning.append("High price sensitivity detected - demand is elastic")
        else:
            reasoning.append("Low price sensitivity - demand is inelastic")

        
        reasoning.append(f"Competitive position: {competitive_position}")

        
        if revenue_impact > 0:
            reasoning.append(f"Expected revenue increase: ${revenue_impact}")
        else:
            reasoning.append(f"Expected revenue impact: ${revenue_impact}")

        
        return reasoning
    
    def _calculate_confidence(self, data_points: int, elasticity: float) -> float:
        """Calculate confidence in recommendation"""
        
        data_confidence = min(data_points / 100.0, 1.0)

        elasticity_confidence = 1.0 - min(abs(abs(elasticity) - 1.2) / 2.0, 0.5)

        
        return (data_confidence * 0.6 + elasticity_confidence * 0.4)
    
    async def dynamic_pricing_rules(
        self,
        product_id: str,
        rules: Dict[str, Any]
    ) -> None:
        """
        Set dynamic pricing rules"""
        self.pricing_rules[product_id] = {
            "min_price": rules.get("min_price"),
            "max_price": rules.get("max_price"),
            "peak_multiplier": rules.get("peak_multiplier", 1.2),
            "off_peak_multiplier": rules.get("off_peak_multiplier", 0.9),
            "competitor_threshold": rules.get("competitor_threshold", 0.95),
            "auto_adjust": rules.get("auto_adjust", True)
        }
        logger.info(f"Dynamic pricing rules set for {product_id}")
