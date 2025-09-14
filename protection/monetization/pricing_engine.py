"""Pricing Engine - Professional dynamic pricing and optimization system.
Handles intelligent pricing strategies, A/B testing, and revenue optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import logging
import json
import uuid
from abc import ABC, abstractmethod
import random
import math

logger = logging.getLogger(__name__)


class PricingStrategy(Enum):
    """
Available pricing strategies."""

    FIXED = "fixed"
    DYNAMIC = "dynamic"
    DEMAND_BASED = "demand_based"
    TIERED = "tiered"
    BUNDLE = "bundle"
    PSYCHOLOGICAL = "psychological"
    COMPETITIVE = "competitive"
    VALUE_BASED = "value_based"
    FREEMIUM = "freemium"
    AUCTION = "auction"


class PriceTestStatus(Enum):
    """A/B test status for pricing."""

    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"
    CANCELLED = "cancelled"


class ContentType(Enum):
    """Content types for pricing."""

    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    PREMIUM = "premium"
    EXCLUSIVE = "exclusive"
    COLLABORATION = "collaboration"


@dataclass
class PricePoint:
    """Individual price point configuration."""
    price_id: str
    content_type: ContentType
    base_price: Decimal
    currency: str = "EUR"
    strategy: PricingStrategy = PricingStrategy.FIXED
    multipliers: Dict[str, float] = field(default_factory=dict)
    conditions: Dict[str, Any] = field(default_factory=dict)
    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def calculate_price(self, context: Dict[str, Any] = None) -> Decimal:
        """Calculate final price based on strategy and context."""
        context = context or {}
        price = self.base_price
        
        # Apply multipliers
        for factor, multiplier in self.multipliers.items():
            if factor in context:
                factor_value = context[factor]
                if isinstance(factor_value, (int, float)):
                    price *= Decimal(str(multiplier * factor_value))
        
        # Apply strategy-specific logic
        if self.strategy == PricingStrategy.DEMAND_BASED:
            demand_factor = context.get("demand_factor", 1.0)
            price *= Decimal(str(demand_factor))
        elif self.strategy == PricingStrategy.PSYCHOLOGICAL:
            price = self._apply_psychological_pricing(price)
        elif self.strategy == PricingStrategy.VALUE_BASED:
            value_score = context.get("value_score", 1.0)
            price *= Decimal(str(value_score))
        
        # Apply min/max constraints
        if self.min_price and price < self.min_price:
            price = self.min_price
        if self.max_price and price > self.max_price:
            price = self.max_price
        
        return price.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    
    def _apply_psychological_pricing(self, price: Decimal) -> Decimal:
        """Apply psychological pricing (e.g., $9.99 instead of $10.00)."""
        price_float = float(price)
        
        if price_float >= 10:
            # Round down to .99
            whole_part = int(price_float)
            return Decimal(f"{whole_part - 1}.99")
        else:
            # For prices under 10, use .99 or .49
            if price_float > 5:
                return Decimal("4.99")
            else:
                return Decimal("2.99")


@dataclass
class PriceTest:
    """A/B price testing configuration."""
    test_id: str
    name: str
    content_type: ContentType
    control_price: Decimal
    test_prices: List[Decimal]
    traffic_split: List[float] = field(default_factory=lambda: [0.5, 0.5])
    status: PriceTestStatus = PriceTestStatus.ACTIVE
    metrics: Dict[str, Any] = field(default_factory=dict)
    start_date: datetime = field(default_factory=datetime.utcnow)
    end_date: Optional[datetime] = None
    min_sample_size: int = 100
    confidence_level: float = 0.95
    winner: Optional[Decimal] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def get_price_for_user(self, user_id: str) -> Decimal:
        """
Get price for specific user based on test assignment."""
        # Simple hash-based assignment for consistency
        user_hash = hash(user_id + self.test_id) % 100
        cumulative_split = 0
        
        for i, split in enumerate(self.traffic_split):
            cumulative_split += split * 100
            if user_hash < cumulative_split:
                if i == 0:
                    return self.control_price
                else:
                    return self.test_prices[min(i - 1, len(self.test_prices) - 1)]
        
        return self.control_price
    
    def record_conversion(self, user_id: str, price: Decimal, revenue: Decimal) -> None:
        """
Record conversion for the test."""
        price_key = f"price_{price}"
        
        if price_key not in self.metrics:
            self.metrics[price_key] = {
                "exposures": 0,
                "conversions": 0,
                "revenue": Decimal("0"),
                "conversion_rate": 0.0,
                "avg_revenue": Decimal("0")
            }
        
        metrics = self.metrics[price_key]
        metrics["conversions"] += 1
        metrics["revenue"] += revenue
        metrics["conversion_rate"] = metrics["conversions"] / max(metrics["exposures"], 1)
        metrics["avg_revenue"] = metrics["revenue"] / max(metrics["conversions"], 1)
    
    def record_exposure(self, user_id: str, price: Decimal) -> None:
        """Record exposure for the test."""
        price_key = f"price_{price}"
        
        if price_key not in self.metrics:
            self.metrics[price_key] = {
                "exposures": 0,
                "conversions": 0,
                "revenue": Decimal("0"),
                "conversion_rate": 0.0,
                "avg_revenue": Decimal("0")
            }
        
        self.metrics[price_key]["exposures"] += 1


@dataclass
class DemandData:
    """Market demand data for pricing optimization."""
    content_type: ContentType
    time_period: datetime
    view_count: int
    conversion_count: int
    average_price: Decimal
    revenue: Decimal
    demand_score: float = 1.0
    
    def calculate_demand_factor(self) -> float:
        """
Calculate demand factor based on data."""
        if self.view_count == 0:
            return 1.0
        
        conversion_rate = self.conversion_count / self.view_count
        
        # Base demand on conversion rate and volume
        volume_factor = min(self.view_count / 1000, 2.0)  # Cap at 2x
        conversion_factor = min(conversion_rate * 10, 2.0)  # Cap at 2x
        
        return max(0.5, min(2.0, (volume_factor + conversion_factor) / 2))


class PricingEngine:
    """
    Professional dynamic pricing and optimization engine.
    Handles intelligent pricing strategies, A/B testing, and optimization.
    """
    
    def __init__(self) -> None:
        self.price_points: Dict[str, PricePoint] = {}
        self.active_tests: Dict[str, PriceTest] = {}
        self.demand_data: List[DemandData] = []
        self.pricing_history: List[Dict[str, Any]] = []
        self.default_prices = self._create_default_prices()
        self.optimization_rules: Dict[str, Any] = {}
        self.is_initialized = False
    
    async def initialize(self) -> bool:
        """
Initialize pricing engine."""
        try:
            # Create default price points
            for price_point in self.default_prices:
                self.price_points[price_point.price_id] = price_point
            
            # Initialize optimization rules
            self._initialize_optimization_rules()
            
            self.is_initialized = True
            logger.info("Pricing engine initialized")
            return True
            
        except Exception as e:
            logger.error(f"Pricing engine initialization failed: {e}")
            return False
    
    def _create_default_prices(self) -> List[PricePoint]:
        """Create default price points for different content types."""
        prices = []
        
        # Audio content pricing
        audio_price = PricePoint(
            price_id="audio_standard",
            content_type=ContentType.AUDIO,
            base_price=Decimal("0.99"),
            strategy=PricingStrategy.DYNAMIC,
            multipliers={
                "quality_score": 1.2,
                "popularity": 1.5,
                "exclusivity": 2.0
            },
            min_price=Decimal("0.49"),
            max_price=Decimal("9.99")
        )
        prices.append(audio_price)
        
        # Video content pricing
        video_price = PricePoint(
            price_id="video_standard",
            content_type=ContentType.VIDEO,
            base_price=Decimal("2.99"),
            strategy=PricingStrategy.DYNAMIC,
            multipliers={
                "quality_score": 1.3,
                "duration": 1.1,
                "popularity": 1.5
            },
            min_price=Decimal("0.99"),
            max_price=Decimal("19.99")
        )
        prices.append(video_price)
        
        # Image content pricing
        image_price = PricePoint(
            price_id="image_standard",
            content_type=ContentType.IMAGE,
            base_price=Decimal("0.49"),
            strategy=PricingStrategy.PSYCHOLOGICAL,
            multipliers={
                "resolution": 1.2,
                "artistic_value": 1.5
            },
            min_price=Decimal("0.29"),
            max_price=Decimal("4.99")
        )
        prices.append(image_price)
        
        # Premium content pricing
        premium_price = PricePoint(
            price_id="premium_content",
            content_type=ContentType.PREMIUM,
            base_price=Decimal("9.99"),
            strategy=PricingStrategy.VALUE_BASED,
            multipliers={
                "exclusivity": 2.0,
                "creator_reputation": 1.5
            },
            min_price=Decimal("4.99"),
            max_price=Decimal("49.99")
        )
        prices.append(premium_price)
        
        # Collaboration pricing
        collab_price = PricePoint(
            price_id="collaboration",
            content_type=ContentType.COLLABORATION,
            base_price=Decimal("19.99"),
            strategy=PricingStrategy.TIERED,
            multipliers={
                "participants": 1.2,
                "complexity": 1.5
            },
            min_price=Decimal("9.99"),
            max_price=Decimal("99.99")
        )
        prices.append(collab_price)
        
        return prices
    
    def _initialize_optimization_rules(self) -> None:
        """Initialize pricing optimization rules."""
        self.optimization_rules = {
            "demand_threshold": 1.5,  # Increase price if demand factor > 1.5
            "low_demand_threshold": 0.8,  # Decrease price if demand factor < 0.8
            "price_adjustment_rate": 0.1,  # 10% adjustment rate
            "min_test_duration_days": 7,  # Minimum test duration
            "max_price_increase": 0.5,  # Maximum 50% price increase
            "max_price_decrease": 0.3   # Maximum 30% price decrease
        }
    
    async def get_price(
        self, 
        content_type: ContentType, 
        user_id: str,
        context: Dict[str, Any] = None
    ) -> Decimal:
        """Get optimized price for content."""
        if not self.is_initialized:
            await self.initialize()
        
        context = context or {}
        
        try:
            # Check for active price tests
            for test in self.active_tests.values():
                if test.content_type == content_type and test.status == PriceTestStatus.ACTIVE:
                    test_price = test.get_price_for_user(user_id)
                    test.record_exposure(user_id, test_price)
                    logger.info(f"Price test price returned: {test_price} for user {user_id}")
                    return test_price
            
            # Get base price point
            price_point = self._get_price_point(content_type)
            if not price_point:
                logger.warning(f"No price point found for content type: {content_type}")
                return Decimal("1.99")  # Default fallback price
            
            # Add demand-based adjustments
            demand_factor = await self._calculate_demand_factor(content_type)
            context["demand_factor"] = demand_factor
            
            # Calculate final price
            final_price = price_point.calculate_price(context)
            
            # Log pricing decision
            self._log_pricing_decision(content_type, user_id, final_price, context)
            
            return final_price
            
        except Exception as e:
            logger.error(f"Price calculation failed: {e}")
            return Decimal("1.99")  # Safe fallback
    
    async def create_price_test(
        self,
        name: str,
        content_type: ContentType,
        control_price: Decimal,
        test_prices: List[Decimal],
        duration_days: int = 14
    ) -> Optional[PriceTest]:
        """Create a new A/B price test."""
        try:
            test_id = str(uuid.uuid4())
            end_date = datetime.utcnow() + timedelta(days=duration_days)
            
            # Calculate traffic split (equal split for simplicity)
            total_variants = len(test_prices) + 1  # +1 for control
            split = [1.0 / total_variants] * total_variants
            
            test = PriceTest(
                test_id=test_id,
                name=name,
                content_type=content_type,
                control_price=control_price,
                test_prices=test_prices,
                traffic_split=split,
                end_date=end_date
            )
            
            self.active_tests[test_id] = test
            
            logger.info(f"Price test created: {test_id} for {content_type.value}")
            return test
            
        except Exception as e:
            logger.error(f"Price test creation failed: {e}")
            return None
    
    async def analyze_price_test(self, test_id: str) -> Dict[str, Any]:
        """Analyze price test results."""
        test = self.active_tests.get(test_id)
        if not test:
            return {"error": "Test not found"}
        
        try:
            analysis = {
                "test_id": test_id,
                "name": test.name,
                "status": test.status.value,
                "duration_days": (datetime.utcnow() - test.start_date).days,
                "variants": [],
                "recommendation": "",
                "statistical_significance": False
            }
            
            # Analyze each variant
            best_revenue = Decimal("0")
            best_conversion = 0.0
            best_price = test.control_price
            
            for price_key, metrics in test.metrics.items():
                price = Decimal(price_key.replace("price_", ""))
                
                variant_analysis = {
                    "price": float(price),
                    "exposures": metrics["exposures"],
                    "conversions": metrics["conversions"],
                    "conversion_rate": metrics["conversion_rate"],
                    "total_revenue": float(metrics["revenue"]),
                    "avg_revenue_per_conversion": float(metrics["avg_revenue"])
                }
                
                analysis["variants"].append(variant_analysis)
                
                # Track best performing variant
                if metrics["revenue"] > best_revenue:
                    best_revenue = metrics["revenue"]
                    best_price = price
                
                if metrics["conversion_rate"] > best_conversion:
                    best_conversion = metrics["conversion_rate"]
            
            # Generate recommendation
            if best_revenue > Decimal("0"):
                analysis["recommendation"] = f"Price {best_price} shows best revenue performance"
                test.winner = best_price
            else:
                analysis["recommendation"] = "Insufficient data for recommendation"
            
            # Check statistical significance (simplified)
            total_conversions = sum(m["conversions"] for m in test.metrics.values())
            analysis["statistical_significance"] = total_conversions >= test.min_sample_size
            
            return analysis
            
        except Exception as e:
            logger.error(f"Price test analysis failed: {e}")
            return {"error": str(e)}
    
    async def optimize_prices(self) -> Dict[str, Any]:
        """Run automated price optimization."""
        try:
            optimization_results = {
                "optimized_count": 0,
                "skipped_count": 0,
                "adjustments": []
            }
            
            for content_type in ContentType:
                demand_factor = await self._calculate_demand_factor(content_type)
                price_point = self._get_price_point(content_type)
                
                if not price_point:
                    optimization_results["skipped_count"] += 1
                    continue
                
                # Determine if adjustment is needed
                adjustment_needed = False
                adjustment_factor = 1.0
                reason = ""
                
                if demand_factor > self.optimization_rules["demand_threshold"]:
                    # High demand - increase price
                    adjustment_factor = 1 + self.optimization_rules["price_adjustment_rate"]
                    adjustment_factor = min(adjustment_factor, 1 + self.optimization_rules["max_price_increase"])
                    adjustment_needed = True
                    reason = "High demand detected"
                    
                elif demand_factor < self.optimization_rules["low_demand_threshold"]:
                    # Low demand - decrease price
                    adjustment_factor = 1 - self.optimization_rules["price_adjustment_rate"]
                    adjustment_factor = max(adjustment_factor, 1 - self.optimization_rules["max_price_decrease"])
                    adjustment_needed = True
                    reason = "Low demand detected"
                
                if adjustment_needed:
                    old_price = price_point.base_price
                    new_price = (old_price * Decimal(str(adjustment_factor))).quantize(
                        Decimal("0.01"), rounding=ROUND_HALF_UP
                    )
                    
                    # Apply min/max constraints
                    if price_point.min_price and new_price < price_point.min_price:
                        new_price = price_point.min_price
                    if price_point.max_price and new_price > price_point.max_price:
                        new_price = price_point.max_price
                    
                    # Update price point
                    price_point.base_price = new_price
                    price_point.updated_at = datetime.utcnow()
                    
                    optimization_results["optimized_count"] += 1
                    optimization_results["adjustments"].append({
                        "content_type": content_type.value,
                        "old_price": float(old_price),
                        "new_price": float(new_price),
                        "demand_factor": demand_factor,
                        "reason": reason
                    })
                    
                    logger.info(f"Price optimized for {content_type.value}: {old_price} -> {new_price}")
                else:
                    optimization_results["skipped_count"] += 1
            
            return optimization_results
            
        except Exception as e:
            logger.error(f"Price optimization failed: {e}")
            return {"error": str(e)}
    
    async def get_pricing_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get pricing performance analytics."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            recent_history = [
                h for h in self.pricing_history
                if datetime.fromisoformat(h["timestamp"]) >= cutoff_date
            ]
            
            analytics = {
                "period_days": days,
                "total_pricing_decisions": len(recent_history),
                "avg_price_by_type": {},
                "price_distribution": {},
                "active_tests": len([t for t in self.active_tests.values() if t.status == PriceTestStatus.ACTIVE]),
                "optimization_opportunities": []
            }
            
            # Calculate averages by content type
            type_prices = {}
            for entry in recent_history:
                content_type = entry["content_type"]
                price = entry["final_price"]
                
                if content_type not in type_prices:
                    type_prices[content_type] = []
                type_prices[content_type].append(price)
            
            for content_type, prices in type_prices.items():
                analytics["avg_price_by_type"][content_type] = sum(prices) / len(prices)
            
            # Identify optimization opportunities
            for content_type in ContentType:
                demand_factor = await self._calculate_demand_factor(content_type)
                
                if demand_factor > 1.3:
                    analytics["optimization_opportunities"].append({
                        "content_type": content_type.value,
                        "opportunity": "price_increase",
                        "reason": f"High demand (factor: {demand_factor:.2f})"
                    })
                elif demand_factor < 0.7:
                    analytics["optimization_opportunities"].append({
                        "content_type": content_type.value,
                        "opportunity": "price_decrease",
                        "reason": f"Low demand (factor: {demand_factor:.2f})"
                    })
            
            return analytics
            
        except Exception as e:
            logger.error(f"Pricing analytics failed: {e}")
            return {"error": str(e)}
    
    async def record_purchase(
        self, 
        user_id: str, 
        content_type: ContentType, 
        price: Decimal,
        revenue: Decimal
    ) -> None:
        """Record a successful purchase for pricing optimization."""
        try:
            # Update active tests
            for test in self.active_tests.values():
                if test.content_type == content_type and test.status == PriceTestStatus.ACTIVE:
                    test.record_conversion(user_id, price, revenue)
            
            # Update demand data
            await self._update_demand_data(content_type, True, price, revenue)
            
            logger.info(f"Purchase recorded: {content_type.value}, price: {price}, revenue: {revenue}")
            
        except Exception as e:
            logger.error(f"Purchase recording failed: {e}")
    
    def get_price_point(self, content_type: ContentType) -> Optional[PricePoint]:
        """Get price point for content type."""
        return self._get_price_point(content_type)
    
    def list_active_tests(self) -> List[PriceTest]:
        """
List all active price tests."""
        return [
            test for test in self.active_tests.values()
            if test.status == PriceTestStatus.ACTIVE
        ]
    
    async def _get_price_point(self, content_type: ContentType) -> Optional[PricePoint]:
        """
Get price point for content type."""
        # Find exact match first
        for price_point in self.price_points.values():
            if price_point.content_type == content_type and price_point.is_active:
                return price_point
        
        # Fallback to standard pricing
        standard_id = f"{content_type.value}_standard"
        return self.price_points.get(standard_id)
    
    async def _calculate_demand_factor(self, content_type: ContentType) -> float:
        """Calculate demand factor for content type."""
        try:
            # Get recent demand data
            recent_data = [
                d for d in self.demand_data
                if d.content_type == content_type and 
                d.time_period >= datetime.utcnow() - timedelta(days=7)
            ]
            
            if not recent_data:
                return 1.0  # Neutral demand
            
            # Calculate average demand factor
            factors = [d.calculate_demand_factor() for d in recent_data]
            return sum(factors) / len(factors)
            
        except Exception as e:
            logger.error(f"Demand factor calculation failed: {e}")
            return 1.0
    
    async def _update_demand_data(
        self, 
        content_type: ContentType, 
        conversion: bool,
        price: Decimal,
        revenue: Decimal
    ) -> None:
        """Update demand data with new interaction."""
        try:
            # Find or create today's demand data
            today = datetime.utcnow().date()
            today_data = None
            
            for data in self.demand_data:
                if (data.content_type == content_type and 
                    data.time_period.date() == today):
                    today_data = data
                    break
            
            if not today_data:
                today_data = DemandData(
                    content_type=content_type,
                    time_period=datetime.combine(today, datetime.min.time()),
                    view_count=0,
                    conversion_count=0,
                    average_price=price,
                    revenue=Decimal("0")
                )
                self.demand_data.append(today_data)
            
            # Update data
            today_data.view_count += 1
            if conversion:
                today_data.conversion_count += 1
                today_data.revenue += revenue
            
            # Update average price
            today_data.average_price = (today_data.average_price + price) / 2
            
        except Exception as e:
            logger.error(f"Demand data update failed: {e}")
    
    def _log_pricing_decision(
        self, 
        content_type: ContentType, 
        user_id: str,
        final_price: Decimal,
        context: Dict[str, Any]
    ) -> None:
        """Log pricing decision for analytics."""
        try:
            log_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "content_type": content_type.value,
                "user_id": user_id,
                "final_price": float(final_price),
                "context": context
            }
            
            self.pricing_history.append(log_entry)
            
            # Keep only recent history (last 10000 entries)
            if len(self.pricing_history) > 10000:
                self.pricing_history = self.pricing_history[-5000:]
                
        except Exception as e:
            logger.error(f"Pricing decision logging failed: {e}")
