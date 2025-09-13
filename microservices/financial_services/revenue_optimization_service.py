"""
🎯 Revenue Optimization Microservice
AI-powered revenue optimization engine with dynamic pricing, market analysis, and performance tracking.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import json
import time
import logging
import uuid
import statistics
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from abc import ABC, abstractmethod
import threading
from datetime import datetime, timedelta
from collections import defaultdict, deque
from decimal import Decimal, ROUND_HALF_UP
import numpy as np
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class RevenueStream(str, Enum):
    """Revenue stream types"""
    CONTENT_SALES = "content_sales"
    SUBSCRIPTIONS = "subscriptions"
    COLLABORATIONS = "collaborations"
    LICENSING = "licensing"
    MERCHANDISE = "merchandise"
    SPONSORSHIPS = "sponsorships"
    ADVERTISING = "advertising"
    DONATIONS = "donations"
    COURSES = "courses"
    CONSULTING = "consulting"
    AFFILIATE = "affiliate"
    ROYALTIES = "royalties"


class PricingStrategy(str, Enum):
    """Pricing strategies"""
    FIXED = "fixed"
    DYNAMIC = "dynamic"
    TIERED = "tiered"
    SUBSCRIPTION = "subscription"
    PAY_PER_USE = "pay_per_use"
    FREEMIUM = "freemium"
    AUCTION = "auction"
    BUNDLE = "bundle"
    PENETRATION = "penetration"
    PREMIUM = "premium"


class MarketCondition(str, Enum):
    """Market conditions"""
    STRONG_DEMAND = "strong_demand"
    MODERATE_DEMAND = "moderate_demand"
    WEAK_DEMAND = "weak_demand"
    HIGH_COMPETITION = "high_competition"
    LOW_COMPETITION = "low_competition"
    SEASONAL_PEAK = "seasonal_peak"
    SEASONAL_LOW = "seasonal_low"


class OptimizationGoal(str, Enum):
    """Optimization goals"""
    MAXIMIZE_REVENUE = "maximize_revenue"
    MAXIMIZE_PROFIT = "maximize_profit"
    MAXIMIZE_VOLUME = "maximize_volume"
    INCREASE_MARKET_SHARE = "increase_market_share"
    CUSTOMER_ACQUISITION = "customer_acquisition"
    CUSTOMER_RETENTION = "customer_retention"
    BALANCED = "balanced"


@dataclass
class PricePoint:
    """Price point data"""
    price: Decimal
    currency: str = "USD"
    timestamp: datetime = field(default_factory=datetime.utcnow)
    confidence: float = 1.0
    reasoning: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'price': float(self.price),
            'currency': self.currency,
            'timestamp': self.timestamp.isoformat(),
            'confidence': self.confidence,
            'reasoning': self.reasoning
        }


@dataclass
class MarketData:
    """Market analysis data"""
    competitor_prices: List[Decimal] = field(default_factory=list)
    market_average: Optional[Decimal] = None
    market_median: Optional[Decimal] = None
    demand_elasticity: float = 1.0
    competition_level: float = 0.5
    market_condition: MarketCondition = MarketCondition.MODERATE_DEMAND
    seasonal_factor: float = 1.0
    trend_direction: str = "stable"  # "up", "down", "stable"
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'competitor_prices': [float(p) for p in self.competitor_prices],
            'market_average': float(self.market_average) if self.market_average else None,
            'market_median': float(self.market_median) if self.market_median else None,
            'demand_elasticity': self.demand_elasticity,
            'competition_level': self.competition_level,
            'market_condition': self.market_condition.value,
            'seasonal_factor': self.seasonal_factor,
            'trend_direction': self.trend_direction,
            'updated_at': self.updated_at.isoformat()
        }


@dataclass
class RevenueMetrics:
    """Revenue performance metrics"""
    total_revenue: Decimal = Decimal('0')
    revenue_per_stream: Dict[RevenueStream, Decimal] = field(default_factory=dict)
    conversion_rate: float = 0.0
    average_order_value: Decimal = Decimal('0')
    customer_lifetime_value: Decimal = Decimal('0')
    churn_rate: float = 0.0
    profit_margin: float = 0.0
    growth_rate: float = 0.0
    unit_economics: Dict[str, float] = field(default_factory=dict)
    period_start: datetime = field(default_factory=datetime.utcnow)
    period_end: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'total_revenue': float(self.total_revenue),
            'revenue_per_stream': {
                stream.value: float(amount) 
                for stream, amount in self.revenue_per_stream.items()
            },
            'conversion_rate': self.conversion_rate,
            'average_order_value': float(self.average_order_value),
            'customer_lifetime_value': float(self.customer_lifetime_value),
            'churn_rate': self.churn_rate,
            'profit_margin': self.profit_margin,
            'growth_rate': self.growth_rate,
            'unit_economics': self.unit_economics,
            'period_start': self.period_start.isoformat(),
            'period_end': self.period_end.isoformat()
        }


@dataclass
class OptimizationRecommendation:
    """Revenue optimization recommendation"""
    id: str
    recommendation_type: str
    title: str
    description: str
    priority: int  # 1-10
    expected_impact: Dict[str, float]  # percentage improvements
    implementation_effort: str  # low, medium, high
    timeline: str  # immediate, short-term, long-term
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'recommendation_type': self.recommendation_type,
            'title': self.title,
            'description': self.description,
            'priority': self.priority,
            'expected_impact': self.expected_impact,
            'implementation_effort': self.implementation_effort,
            'timeline': self.timeline,
            'created_at': self.created_at.isoformat()
        }


class PricingEngine:
    """Dynamic pricing engine"""
    
    def __init__(self):
        self.pricing_models = {}
        self.price_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
    def calculate_optimal_price(self, product_id: str, current_price: Decimal,
                              market_data: MarketData, metrics: RevenueMetrics,
                              strategy: PricingStrategy, goal: OptimizationGoal) -> PricePoint:
        """Calculate optimal price using AI algorithms"""
        try:
            base_price = current_price
            adjustment_factor = Decimal('1.0')
            
            # Market-based adjustments
            if market_data.market_average and market_data.market_average > 0:
                market_ratio = float(current_price / market_data.market_average)
                
                if strategy == PricingStrategy.PREMIUM and market_ratio < 1.2:
                    adjustment_factor *= Decimal('1.1')  # Price premium
                elif strategy == PricingStrategy.PENETRATION and market_ratio > 0.8:
                    adjustment_factor *= Decimal('0.9')  # Price discount
                    
            # Demand elasticity adjustments
            if market_data.demand_elasticity < 0.5:  # Low elasticity
                if goal == OptimizationGoal.MAXIMIZE_REVENUE:
                    adjustment_factor *= Decimal('1.05')
            elif market_data.demand_elasticity > 1.5:  # High elasticity
                if goal == OptimizationGoal.MAXIMIZE_VOLUME:
                    adjustment_factor *= Decimal('0.95')
                    
            # Competition adjustments
            if market_data.competition_level > 0.7:  # High competition
                adjustment_factor *= Decimal('0.98')
            elif market_data.competition_level < 0.3:  # Low competition
                adjustment_factor *= Decimal('1.02')
                
            # Seasonal adjustments
            adjustment_factor *= Decimal(str(market_data.seasonal_factor))
            
            # Performance-based adjustments
            if metrics.conversion_rate > 0.1:  # Good conversion
                if goal == OptimizationGoal.MAXIMIZE_REVENUE:
                    adjustment_factor *= Decimal('1.02')
            elif metrics.conversion_rate < 0.05:  # Poor conversion
                adjustment_factor *= Decimal('0.95')
                
            # Calculate final price
            optimal_price = base_price * adjustment_factor
            
            # Round to reasonable precision
            optimal_price = optimal_price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            
            # Generate reasoning
            reasoning = self._generate_pricing_reasoning(
                current_price, optimal_price, market_data, strategy, goal
            )
            
            # Calculate confidence based on data quality
            confidence = self._calculate_confidence(market_data, metrics)
            
            price_point = PricePoint(
                price=optimal_price,
                confidence=confidence,
                reasoning=reasoning
            )
            
            # Store in history
            self.price_history[product_id].append({
                'price': optimal_price,
                'timestamp': datetime.utcnow(),
                'strategy': strategy.value,
                'goal': goal.value
            })
            
            return price_point
            
        except Exception as e:
            logger.error(f"Error calculating optimal price: {str(e)}")
            return PricePoint(
                price=current_price,
                confidence=0.5,
                reasoning=f"Error in calculation: {str(e)}"
            )
            
    def _generate_pricing_reasoning(self, current_price: Decimal, optimal_price: Decimal,
                                  market_data: MarketData, strategy: PricingStrategy,
                                  goal: OptimizationGoal) -> str:
        """Generate human-readable pricing reasoning"""
        change_pct = float((optimal_price - current_price) / current_price * 100)
        
        reasoning_parts = []
        
        if abs(change_pct) < 1:
            reasoning_parts.append("Current price is near optimal")
        elif change_pct > 0:
            reasoning_parts.append(f"Recommend {change_pct:.1f}% price increase")
        else:
            reasoning_parts.append(f"Recommend {abs(change_pct):.1f}% price decrease")
            
        # Add market factors
        if market_data.market_condition == MarketCondition.STRONG_DEMAND:
            reasoning_parts.append("strong market demand supports higher pricing")
        elif market_data.market_condition == MarketCondition.WEAK_DEMAND:
            reasoning_parts.append("weak demand suggests lower pricing")
            
        if market_data.competition_level > 0.7:
            reasoning_parts.append("high competition requires competitive pricing")
        elif market_data.competition_level < 0.3:
            reasoning_parts.append("low competition allows premium pricing")
            
        # Add strategy context
        if strategy == PricingStrategy.PREMIUM:
            reasoning_parts.append("premium strategy targets higher margins")
        elif strategy == PricingStrategy.PENETRATION:
            reasoning_parts.append("penetration strategy prioritizes market share")
            
        return "; ".join(reasoning_parts)
        
    def _calculate_confidence(self, market_data: MarketData, metrics: RevenueMetrics) -> float:
        """Calculate confidence score for pricing recommendation"""
        confidence = 1.0
        
        # Reduce confidence if limited market data
        if len(market_data.competitor_prices) < 3:
            confidence *= 0.8
            
        # Reduce confidence if high elasticity (more uncertain)
        if market_data.demand_elasticity > 2.0:
            confidence *= 0.7
            
        # Reduce confidence if very recent data (less than 1 day)
        data_age_hours = (datetime.utcnow() - market_data.updated_at).total_seconds() / 3600
        if data_age_hours < 24:
            confidence *= 0.9
            
        # Increase confidence if good historical performance
        if metrics.conversion_rate > 0.1:
            confidence *= 1.1
            
        return min(1.0, max(0.1, confidence))


class MarketAnalyzer:
    """Market analysis and intelligence"""
    
    def __init__(self):
        self.market_cache: Dict[str, MarketData] = {}
        self.trend_data: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        
    async def analyze_market(self, product_category: str, region: str = "global") -> MarketData:
        """Analyze market conditions"""
        try:
            cache_key = f"{product_category}_{region}"
            
            # Check cache (refresh every hour)
            if cache_key in self.market_cache:
                data = self.market_cache[cache_key]
                if (datetime.utcnow() - data.updated_at).total_seconds() < 3600:
                    return data
                    
            # Simulate market analysis (in real implementation, this would call APIs)
            market_data = await self._fetch_market_data(product_category, region)
            
            # Store in cache
            self.market_cache[cache_key] = market_data
            
            # Update trend data
            self.trend_data[cache_key].append({
                'timestamp': datetime.utcnow(),
                'average_price': market_data.market_average,
                'competition_level': market_data.competition_level
            })
            
            return market_data
            
        except Exception as e:
            logger.error(f"Error analyzing market: {str(e)}")
            return MarketData()  # Return default data
            
    async def _fetch_market_data(self, category: str, region: str) -> MarketData:
        """Fetch market data from external sources"""
        # Simulate market data fetching
        await asyncio.sleep(0.1)  # Simulate API call
        
        # Generate realistic market data
        import random
        
        base_price = random.uniform(10, 1000)
        competitor_prices = [
            Decimal(str(round(base_price * random.uniform(0.8, 1.2), 2)))
            for _ in range(random.randint(3, 10))
        ]
        
        market_data = MarketData(
            competitor_prices=competitor_prices,
            market_average=Decimal(str(statistics.mean([float(p) for p in competitor_prices]))),
            market_median=Decimal(str(statistics.median([float(p) for p in competitor_prices]))),
            demand_elasticity=random.uniform(0.5, 2.0),
            competition_level=random.uniform(0.2, 0.9),
            market_condition=random.choice(list(MarketCondition)),
            seasonal_factor=random.uniform(0.8, 1.2),
            trend_direction=random.choice(["up", "down", "stable"])
        )
        
        return market_data
        
    def detect_trends(self, product_category: str, region: str = "global") -> Dict[str, Any]:
        """Detect market trends"""
        cache_key = f"{product_category}_{region}"
        
        if cache_key not in self.trend_data:
            return {"trend": "insufficient_data"}
            
        data_points = list(self.trend_data[cache_key])
        if len(data_points) < 10:
            return {"trend": "insufficient_data"}
            
        # Analyze price trends
        recent_prices = [p['average_price'] for p in data_points[-10:] if p['average_price']]
        if len(recent_prices) >= 2:
            price_trend = "stable"
            if recent_prices[-1] > recent_prices[0] * 1.05:
                price_trend = "increasing"
            elif recent_prices[-1] < recent_prices[0] * 0.95:
                price_trend = "decreasing"
        else:
            price_trend = "stable"
            
        # Analyze competition trends
        recent_competition = [p['competition_level'] for p in data_points[-10:]]
        competition_change = recent_competition[-1] - recent_competition[0] if len(recent_competition) >= 2 else 0
        
        return {
            "price_trend": price_trend,
            "competition_change": competition_change,
            "data_points": len(data_points),
            "analysis_date": datetime.utcnow().isoformat()
        }


class RecommendationEngine:
    """Revenue optimization recommendation engine"""
    
    def __init__(self):
        self.recommendation_history: List[OptimizationRecommendation] = []
        
    def generate_recommendations(self, metrics: RevenueMetrics, 
                               market_data: MarketData,
                               goal: OptimizationGoal) -> List[OptimizationRecommendation]:
        """Generate optimization recommendations"""
        recommendations = []
        
        try:
            # Price optimization recommendations
            if market_data.competition_level < 0.5 and metrics.profit_margin < 0.3:
                rec = OptimizationRecommendation(
                    id=str(uuid.uuid4()),
                    recommendation_type="pricing",
                    title="Increase Pricing for Higher Margins",
                    description="Low competition environment allows for premium pricing strategy",
                    priority=8,
                    expected_impact={"revenue": 15.0, "profit": 25.0},
                    implementation_effort="low",
                    timeline="immediate"
                )
                recommendations.append(rec)
                
            # Conversion optimization
            if metrics.conversion_rate < 0.05:
                rec = OptimizationRecommendation(
                    id=str(uuid.uuid4()),
                    recommendation_type="conversion",
                    title="Optimize Conversion Funnel",
                    description="Low conversion rate indicates optimization opportunities in user experience",
                    priority=9,
                    expected_impact={"revenue": 20.0, "conversions": 40.0},
                    implementation_effort="medium",
                    timeline="short-term"
                )
                recommendations.append(rec)
                
            # Revenue stream diversification
            if len(metrics.revenue_per_stream) < 3:
                rec = OptimizationRecommendation(
                    id=str(uuid.uuid4()),
                    recommendation_type="diversification",
                    title="Diversify Revenue Streams",
                    description="Adding new revenue streams reduces risk and increases total revenue potential",
                    priority=7,
                    expected_impact={"revenue": 30.0, "stability": 50.0},
                    implementation_effort="high",
                    timeline="long-term"
                )
                recommendations.append(rec)
                
            # Customer lifetime value optimization
            if metrics.customer_lifetime_value < metrics.average_order_value * 3:
                rec = OptimizationRecommendation(
                    id=str(uuid.uuid4()),
                    recommendation_type="retention",
                    title="Improve Customer Retention",
                    description="Low CLV suggests opportunities for better customer retention strategies",
                    priority=8,
                    expected_impact={"clv": 40.0, "revenue": 25.0},
                    implementation_effort="medium",
                    timeline="short-term"
                )
                recommendations.append(rec)
                
            # Market timing recommendations
            if market_data.market_condition == MarketCondition.SEASONAL_PEAK:
                rec = OptimizationRecommendation(
                    id=str(uuid.uuid4()),
                    recommendation_type="timing",
                    title="Capitalize on Seasonal Peak",
                    description="Market conditions favor increased marketing spend and premium pricing",
                    priority=9,
                    expected_impact={"revenue": 20.0, "market_share": 15.0},
                    implementation_effort="low",
                    timeline="immediate"
                )
                recommendations.append(rec)
                
            # Sort by priority
            recommendations.sort(key=lambda x: x.priority, reverse=True)
            
            # Store in history
            self.recommendation_history.extend(recommendations)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return []
            
    def get_recommendation_performance(self, recommendation_id: str) -> Dict[str, Any]:
        """Track recommendation performance"""
        # In a real implementation, this would track actual vs expected results
        return {
            "recommendation_id": recommendation_id,
            "implementation_status": "pending",
            "actual_impact": {},
            "performance_score": None
        }


class RevenueOptimizationService:
    """AI-powered Revenue Optimization Engine"""
    
    def __init__(self, name: str = "revenue_optimization_service"):
        self.name = name
        self.pricing_engine = PricingEngine()
        self.market_analyzer = MarketAnalyzer()
        self.recommendation_engine = RecommendationEngine()
        self.products: Dict[str, Dict[str, Any]] = {}  # product_id -> product_data
        self.revenue_data: Dict[str, RevenueMetrics] = {}  # product_id -> metrics
        self.optimization_history: List[Dict[str, Any]] = []
        self.running = False
        self.analysis_task = None
        self.stats = {
            'total_optimizations': 0,
            'revenue_improvements': 0,
            'products_tracked': 0,
            'average_improvement': 0.0
        }
        
    async def start(self):
        """Start revenue optimization service"""
        self.running = True
        
        # Start periodic analysis
        self.analysis_task = asyncio.create_task(self._periodic_analysis())
        
        logger.info(f"Started revenue optimization service: {self.name}")
        
    async def stop(self):
        """Stop revenue optimization service"""
        self.running = False
        
        if self.analysis_task:
            self.analysis_task.cancel()
            try:
                await self.analysis_task
            except asyncio.CancelledError:
                pass
                
        logger.info(f"Stopped revenue optimization service: {self.name}")
        
    async def register_product(self, product_id: str, product_data: Dict[str, Any]) -> bool:
        """Register product for optimization"""
        try:
            self.products[product_id] = {
                'id': product_id,
                'name': product_data.get('name', ''),
                'category': product_data.get('category', ''),
                'current_price': Decimal(str(product_data.get('price', 0))),
                'currency': product_data.get('currency', 'USD'),
                'strategy': PricingStrategy(product_data.get('strategy', 'dynamic')),
                'goal': OptimizationGoal(product_data.get('goal', 'maximize_revenue')),
                'region': product_data.get('region', 'global'),
                'registered_at': datetime.utcnow()
            }
            
            # Initialize metrics
            self.revenue_data[product_id] = RevenueMetrics()
            self.stats['products_tracked'] += 1
            
            logger.info(f"Registered product for optimization: {product_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error registering product: {str(e)}")
            return False
            
    async def update_revenue_metrics(self, product_id: str, metrics_data: Dict[str, Any]) -> bool:
        """Update revenue metrics for a product"""
        try:
            if product_id not in self.products:
                logger.error(f"Product {product_id} not registered")
                return False
                
            metrics = self.revenue_data[product_id]
            
            # Update metrics
            if 'total_revenue' in metrics_data:
                metrics.total_revenue = Decimal(str(metrics_data['total_revenue']))
                
            if 'conversion_rate' in metrics_data:
                metrics.conversion_rate = float(metrics_data['conversion_rate'])
                
            if 'average_order_value' in metrics_data:
                metrics.average_order_value = Decimal(str(metrics_data['average_order_value']))
                
            if 'customer_lifetime_value' in metrics_data:
                metrics.customer_lifetime_value = Decimal(str(metrics_data['customer_lifetime_value']))
                
            if 'churn_rate' in metrics_data:
                metrics.churn_rate = float(metrics_data['churn_rate'])
                
            if 'profit_margin' in metrics_data:
                metrics.profit_margin = float(metrics_data['profit_margin'])
                
            if 'revenue_per_stream' in metrics_data:
                for stream_name, amount in metrics_data['revenue_per_stream'].items():
                    stream = RevenueStream(stream_name)
                    metrics.revenue_per_stream[stream] = Decimal(str(amount))
                    
            metrics.period_end = datetime.utcnow()
            
            logger.info(f"Updated revenue metrics for product: {product_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating revenue metrics: {str(e)}")
            return False
            
    async def optimize_pricing(self, product_id: str) -> Optional[PricePoint]:
        """Optimize pricing for a product"""
        try:
            if product_id not in self.products:
                logger.error(f"Product {product_id} not registered")
                return None
                
            product = self.products[product_id]
            metrics = self.revenue_data[product_id]
            
            # Get market analysis
            market_data = await self.market_analyzer.analyze_market(
                product['category'], 
                product['region']
            )
            
            # Calculate optimal price
            optimal_price = self.pricing_engine.calculate_optimal_price(
                product_id,
                product['current_price'],
                market_data,
                metrics,
                product['strategy'],
                product['goal']
            )
            
            # Store optimization record
            self.optimization_history.append({
                'product_id': product_id,
                'timestamp': datetime.utcnow(),
                'old_price': product['current_price'],
                'new_price': optimal_price.price,
                'confidence': optimal_price.confidence,
                'reasoning': optimal_price.reasoning
            })
            
            self.stats['total_optimizations'] += 1
            
            logger.info(f"Optimized pricing for product {product_id}: {optimal_price.price}")
            return optimal_price
            
        except Exception as e:
            logger.error(f"Error optimizing pricing: {str(e)}")
            return None
            
    async def get_recommendations(self, product_id: str) -> List[OptimizationRecommendation]:
        """Get optimization recommendations for a product"""
        try:
            if product_id not in self.products:
                logger.error(f"Product {product_id} not registered")
                return []
                
            product = self.products[product_id]
            metrics = self.revenue_data[product_id]
            
            # Get market analysis
            market_data = await self.market_analyzer.analyze_market(
                product['category'], 
                product['region']
            )
            
            # Generate recommendations
            recommendations = self.recommendation_engine.generate_recommendations(
                metrics,
                market_data,
                product['goal']
            )
            
            logger.info(f"Generated {len(recommendations)} recommendations for product {product_id}")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting recommendations: {str(e)}")
            return []
            
    async def analyze_market_trends(self, category: str, region: str = "global") -> Dict[str, Any]:
        """Analyze market trends"""
        try:
            market_data = await self.market_analyzer.analyze_market(category, region)
            trends = self.market_analyzer.detect_trends(category, region)
            
            return {
                'market_data': market_data.to_dict(),
                'trends': trends,
                'analysis_timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing market trends: {str(e)}")
            return {}
            
    async def calculate_roi(self, product_id: str, investment: Decimal, 
                          timeframe_days: int = 30) -> Dict[str, Any]:
        """Calculate ROI projections"""
        try:
            if product_id not in self.products:
                return {"error": "Product not found"}
                
            metrics = self.revenue_data[product_id]
            
            # Simple ROI calculation
            daily_revenue = metrics.total_revenue / max(
                (metrics.period_end - metrics.period_start).days, 1
            )
            
            projected_revenue = daily_revenue * timeframe_days
            projected_profit = projected_revenue * Decimal(str(metrics.profit_margin))
            roi = ((projected_profit - investment) / investment) * 100 if investment > 0 else 0
            
            return {
                'investment': float(investment),
                'timeframe_days': timeframe_days,
                'projected_revenue': float(projected_revenue),
                'projected_profit': float(projected_profit),
                'roi_percentage': float(roi),
                'break_even_days': float(investment / daily_revenue) if daily_revenue > 0 else None
            }
            
        except Exception as e:
            logger.error(f"Error calculating ROI: {str(e)}")
            return {"error": str(e)}
            
    async def _periodic_analysis(self):
        """Periodic market analysis and optimization"""
        while self.running:
            try:
                await asyncio.sleep(3600)  # Every hour
                
                # Analyze all registered products
                for product_id in self.products.keys():
                    try:
                        # Update market data
                        product = self.products[product_id]
                        await self.market_analyzer.analyze_market(
                            product['category'], 
                            product['region']
                        )
                        
                        logger.debug(f"Updated market analysis for product {product_id}")
                        
                    except Exception as e:
                        logger.error(f"Error in periodic analysis for {product_id}: {str(e)}")
                        
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in periodic analysis: {str(e)}")
                
    def get_status(self) -> Dict[str, Any]:
        """Get service status"""
        return {
            "name": self.name,
            "status": "running" if self.running else "stopped",
            "stats": self.stats,
            "products_count": len(self.products),
            "optimization_history_count": len(self.optimization_history),
            "recommendation_history_count": len(self.recommendation_engine.recommendation_history),
            "products": list(self.products.keys()),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    def get_product_performance(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Get product performance summary"""
        if product_id not in self.products:
            return None
            
        product = self.products[product_id]
        metrics = self.revenue_data[product_id]
        
        # Get recent optimizations
        recent_optimizations = [
            opt for opt in self.optimization_history[-10:]
            if opt['product_id'] == product_id
        ]
        
        return {
            'product': product,
            'metrics': metrics.to_dict(),
            'recent_optimizations': recent_optimizations,
            'performance_score': min(100, max(0, 
                metrics.conversion_rate * 100 + 
                metrics.profit_margin * 50 + 
                (1 - metrics.churn_rate) * 30
            ))
        }


def create_revenue_optimization_service(config: Dict[str, Any] = None) -> RevenueOptimizationService:
    """Factory function to create Revenue Optimization service"""
    config = config or {}
    service_name = config.get('name', 'revenue_optimization_service')
    
    service = RevenueOptimizationService(service_name)
    
    # Configure analysis interval
    if 'analysis_interval' in config:
        # This would need to be implemented in the service
        pass
        
    return service


__all__ = [
    'RevenueOptimizationService', 'PricePoint', 'MarketData', 'RevenueMetrics',
    'OptimizationRecommendation', 'PricingEngine', 'MarketAnalyzer', 'RecommendationEngine',
    'RevenueStream', 'PricingStrategy', 'MarketCondition', 'OptimizationGoal',
    'create_revenue_optimization_service'
]