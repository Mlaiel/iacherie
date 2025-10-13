"""💰 Tiered Pricing Calculator - Enterprise Revenue Management
============================================================

Advanced tiered pricing calculation system for dynamic pricing strategies,
volume discounts, and performance-based pricing optimization.

Performance Target: < 20ms pricing calculations
Enterprise Features:
- Dynamic tier management with ML optimization
- Performance-based pricing adjustments  
- Volume discount calculations
- Price elasticity analysis
- Real-time pricing strategy optimization

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ INTELLECTUAL PROPERTY WARNING:
This code is proprietary and confidential. Commercial use, modification, 
or distribution without explicit written permission is strictly prohibited.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import json

logger = logging.getLogger(__name__)

class PricingTierType(Enum):
    """Pricing tier types for different strategies."""
    VOLUME_BASED = "volume_based"
    PERFORMANCE_BASED = "performance_based"
    SUBSCRIPTION_BASED = "subscription_based"
    CREATOR_TIER_BASED = "creator_tier_based"
    PROMOTIONAL = "promotional"
    DYNAMIC_ML = "dynamic_ml"

class DiscountType(Enum):
    """Types of discount strategies."""
    PERCENTAGE = "percentage"
    FIXED_AMOUNT = "fixed_amount"
    TIERED_PERCENTAGE = "tiered_percentage"
    BULK_DISCOUNT = "bulk_discount"
    LOYALTY_BONUS = "loyalty_bonus"

@dataclass
class PricingTier:
    """Individual pricing tier configuration."""
    tier_id: str
    tier_name: str
    min_threshold: Decimal
    max_threshold: Optional[Decimal]
    base_rate: Decimal
    discount_percentage: Decimal = Decimal('0')
    tier_type: PricingTierType = PricingTierType.VOLUME_BASED
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PricingCalculation:
    """Result of pricing calculation."""
    calculation_id: str
    original_amount: Decimal
    final_amount: Decimal
    applied_tier: PricingTier
    discount_amount: Decimal
    tier_savings: Decimal
    calculation_time: float
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PriceElasticityAnalysis:
    """Price elasticity analysis results."""
    current_price: Decimal
    optimal_price: Decimal
    elasticity_coefficient: float
    demand_forecast: Dict[str, float]
    revenue_impact: Dict[str, Decimal]
    confidence_score: float

class PricingTiers:
    """Manages pricing tier configurations and calculations."""
    
    def __init__(self):
        self.tiers: List[PricingTier] = []
        self.active_promotions: Dict[str, Dict] = {}
        
    def add_tier(self, tier: PricingTier) -> bool:
        """Add a new pricing tier."""
        try:
            # Validate tier doesn't overlap with existing tiers
            if self._validate_tier_thresholds(tier):
                self.tiers.append(tier)
                self.tiers.sort(key=lambda t: t.min_threshold)
                return True
            return False
        except Exception as e:
            logger.error(f"Error adding tier: {e}")
            return False
    
    def _validate_tier_thresholds(self, new_tier: PricingTier) -> bool:
        """Validate tier thresholds don't overlap."""
        for existing_tier in self.tiers:
            if existing_tier.tier_type != new_tier.tier_type:
                continue
                
            # Check for overlap
            if (new_tier.min_threshold < existing_tier.max_threshold and 
                new_tier.max_threshold > existing_tier.min_threshold):
                return False
        return True
    
    def get_applicable_tier(self, amount: Decimal, tier_type: PricingTierType) -> Optional[PricingTier]:
        """Find the applicable tier for given amount."""
        applicable_tiers = [
            tier for tier in self.tiers 
            if (tier.tier_type == tier_type and 
                tier.is_active and
                tier.min_threshold <= amount and
                (tier.max_threshold is None or amount <= tier.max_threshold))
        ]
        return applicable_tiers[0] if applicable_tiers else None

class ThresholdManager:
    """Manages dynamic threshold adjustments based on performance."""
    
    def __init__(self):
        self.threshold_history: Dict[str, List[Dict]] = {}
        self.performance_metrics: Dict[str, Dict] = {}
    
    async def adjust_thresholds_based_on_performance(
        self, 
        tier_id: str, 
        performance_data: Dict[str, Any]
    ) -> Dict[str, Decimal]:
        """Adjust tier thresholds based on performance metrics."""
        try:
            # Analyze performance trends
            conversion_rate = performance_data.get('conversion_rate', 0.1)
            volume_trend = performance_data.get('volume_trend', 1.0)
            revenue_efficiency = performance_data.get('revenue_efficiency', 0.8)
            
            # Calculate adjustment factors
            threshold_adjustment = Decimal(str(1.0 + (conversion_rate - 0.1) * 0.5))
            max_adjustment = Decimal('1.5')  # Maximum 50% adjustment
            min_adjustment = Decimal('0.7')  # Minimum 30% reduction
            
            # Clamp adjustment within bounds
            threshold_adjustment = max(min_adjustment, min(max_adjustment, threshold_adjustment))
            
            return {
                'threshold_multiplier': threshold_adjustment,
                'recommended_adjustment': threshold_adjustment,
                'confidence_score': min(1.0, revenue_efficiency * 1.2)
            }
            
        except Exception as e:
            logger.error(f"Error adjusting thresholds: {e}")
            return {'threshold_multiplier': Decimal('1.0'), 'confidence_score': 0.0}

class DiscountCalculator:
    """Calculates various types of discounts and promotions."""
    
    def __init__(self):
        self.discount_rules: Dict[str, Dict] = {}
        self.loyalty_multipliers: Dict[str, float] = {}
    
    async def calculate_volume_discount(
        self, 
        amount: Decimal, 
        volume_tier: str,
        discount_type: DiscountType
    ) -> Tuple[Decimal, Dict[str, Any]]:
        """Calculate volume-based discounts."""
        try:
            discount_amount = Decimal('0')
            discount_details = {
                'discount_type': discount_type.value,
                'volume_tier': volume_tier,
                'applied_rules': []
            }
            
            if discount_type == DiscountType.PERCENTAGE:
                discount_percentage = self._get_volume_discount_percentage(amount)
                discount_amount = amount * discount_percentage / Decimal('100')
                discount_details['discount_percentage'] = float(discount_percentage)
                
            elif discount_type == DiscountType.TIERED_PERCENTAGE:
                discount_amount, tier_details = self._calculate_tiered_discount(amount)
                discount_details.update(tier_details)
                
            elif discount_type == DiscountType.BULK_DISCOUNT:
                discount_amount = self._calculate_bulk_discount(amount)
                discount_details['bulk_discount_applied'] = True
            
            return discount_amount, discount_details
            
        except Exception as e:
            logger.error(f"Error calculating volume discount: {e}")
            return Decimal('0'), {}
    
    def _get_volume_discount_percentage(self, amount: Decimal) -> Decimal:
        """Get volume discount percentage based on amount."""
        if amount >= Decimal('10000'):
            return Decimal('15')  # 15% for high volume
        elif amount >= Decimal('5000'):
            return Decimal('10')  # 10% for medium volume
        elif amount >= Decimal('1000'):
            return Decimal('5')   # 5% for low volume
        return Decimal('0')
    
    def _calculate_tiered_discount(self, amount: Decimal) -> Tuple[Decimal, Dict]:
        """Calculate tiered percentage discounts."""
        total_discount = Decimal('0')
        tier_details = {'tiers_applied': []}
        
        # Progressive discount tiers
        tiers = [
            (Decimal('1000'), Decimal('2')),   # 2% on first $1000
            (Decimal('4000'), Decimal('5')),   # 5% on next $4000  
            (Decimal('5000'), Decimal('8')),   # 8% on next $5000
            (None, Decimal('12'))              # 12% on remaining
        ]
        
        remaining_amount = amount
        for tier_limit, discount_rate in tiers:
            if remaining_amount <= 0:
                break
                
            tier_amount = min(remaining_amount, tier_limit) if tier_limit else remaining_amount
            tier_discount = tier_amount * discount_rate / Decimal('100')
            total_discount += tier_discount
            
            tier_details['tiers_applied'].append({
                'amount': float(tier_amount),
                'rate': float(discount_rate),
                'discount': float(tier_discount)
            })
            
            remaining_amount -= tier_amount
            
        return total_discount, tier_details
    
    def _calculate_bulk_discount(self, amount: Decimal) -> Decimal:
        """Calculate bulk discount for large purchases."""
        if amount >= Decimal('50000'):
            return amount * Decimal('0.20')  # 20% bulk discount
        elif amount >= Decimal('25000'):
            return amount * Decimal('0.15')  # 15% bulk discount
        elif amount >= Decimal('10000'):
            return amount * Decimal('0.10')  # 10% bulk discount
        return Decimal('0')

class OptimizationEngine:
    """ML-powered pricing optimization engine."""
    
    def __init__(self):
        self.optimization_models: Dict[str, Any] = {}
        self.historical_performance: List[Dict] = []
    
    async def optimize_pricing_strategy(
        self, 
        current_strategy: Dict[str, Any],
        performance_metrics: Dict[str, float]
    ) -> Dict[str, Any]:
        """Optimize pricing strategy using ML algorithms."""
        try:
            # Analyze current performance
            revenue_efficiency = performance_metrics.get('revenue_efficiency', 0.8)
            conversion_rate = performance_metrics.get('conversion_rate', 0.1)
            customer_satisfaction = performance_metrics.get('customer_satisfaction', 0.7)
            
            # Calculate optimization scores
            overall_score = (revenue_efficiency * 0.4 + 
                           conversion_rate * 10 * 0.4 + 
                           customer_satisfaction * 0.2)
            
            # Generate optimization recommendations
            recommendations = {
                'overall_score': overall_score,
                'recommended_changes': [],
                'expected_impact': {},
                'confidence_level': 0.85
            }
            
            # Price elasticity optimization
            if conversion_rate < 0.05:  # Low conversion
                recommendations['recommended_changes'].append({
                    'action': 'reduce_pricing_tiers',
                    'adjustment': -0.15,
                    'reason': 'Low conversion rate detected'
                })
            
            # Revenue optimization
            if revenue_efficiency < 0.7:  # Low revenue efficiency
                recommendations['recommended_changes'].append({
                    'action': 'optimize_tier_thresholds',
                    'adjustment': 0.1,
                    'reason': 'Revenue efficiency below target'
                })
            
            # Customer satisfaction optimization
            if customer_satisfaction < 0.6:  # Low satisfaction
                recommendations['recommended_changes'].append({
                    'action': 'add_loyalty_discounts',
                    'adjustment': 0.05,
                    'reason': 'Customer satisfaction needs improvement'
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error optimizing pricing strategy: {e}")
            return {'overall_score': 0.0, 'recommended_changes': []}

class TieredPricingCalculator:
    """Enterprise tiered pricing calculator with ML optimization."""
    
    def __init__(self):
        self.pricing_tiers = PricingTiers()
        self.threshold_manager = ThresholdManager()
        self.discount_calculator = DiscountCalculator()
        self.optimization_engine = OptimizationEngine()
        self.calculation_cache: Dict[str, PricingCalculation] = {}
        
        # Initialize default tiers
        self._initialize_default_tiers()
    
    def _initialize_default_tiers(self):
        """Initialize default pricing tiers."""
        default_tiers = [
            PricingTier(
                tier_id="starter",
                tier_name="Starter Tier",
                min_threshold=Decimal('0'),
                max_threshold=Decimal('1000'),
                base_rate=Decimal('0.05'),
                discount_percentage=Decimal('0'),
                tier_type=PricingTierType.VOLUME_BASED
            ),
            PricingTier(
                tier_id="professional",
                tier_name="Professional Tier", 
                min_threshold=Decimal('1000'),
                max_threshold=Decimal('10000'),
                base_rate=Decimal('0.04'),
                discount_percentage=Decimal('5'),
                tier_type=PricingTierType.VOLUME_BASED
            ),
            PricingTier(
                tier_id="enterprise",
                tier_name="Enterprise Tier",
                min_threshold=Decimal('10000'),
                max_threshold=None,
                base_rate=Decimal('0.03'),
                discount_percentage=Decimal('15'),
                tier_type=PricingTierType.VOLUME_BASED
            )
        ]
        
        for tier in default_tiers:
            self.pricing_tiers.add_tier(tier)
    
    async def calculate_tiered_pricing(
        self, 
        amount: Decimal,
        tier_type: PricingTierType = PricingTierType.VOLUME_BASED,
        creator_id: Optional[str] = None
    ) -> PricingCalculation:
        """Calculate tiered pricing for given amount."""
        start_time = datetime.utcnow()
        
        try:
            # Get applicable tier
            applicable_tier = self.pricing_tiers.get_applicable_tier(amount, tier_type)
            if not applicable_tier:
                # Use default tier if none found
                applicable_tier = self._get_default_tier(tier_type)
            
            # Calculate base pricing
            base_fee = amount * applicable_tier.base_rate
            tier_discount = base_fee * applicable_tier.discount_percentage / Decimal('100')
            
            # Apply additional discounts
            additional_discount, discount_details = await self.discount_calculator.calculate_volume_discount(
                amount, applicable_tier.tier_id, DiscountType.PERCENTAGE
            )
            
            # Calculate final amounts
            total_discount = tier_discount + additional_discount
            final_amount = base_fee - total_discount
            tier_savings = amount - final_amount
            
            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            calculation = PricingCalculation(
                calculation_id=f"calc_{datetime.utcnow().timestamp()}",
                original_amount=amount,
                final_amount=final_amount,
                applied_tier=applicable_tier,
                discount_amount=total_discount,
                tier_savings=tier_savings,
                calculation_time=processing_time,
                metadata={
                    'base_fee': float(base_fee),
                    'tier_discount': float(tier_discount),
                    'additional_discount': float(additional_discount),
                    'discount_details': discount_details,
                    'tier_type': tier_type.value,
                    'creator_id': creator_id
                }
            )
            
            # Cache calculation
            self.calculation_cache[calculation.calculation_id] = calculation
            
            return calculation
            
        except Exception as e:
            logger.error(f"Error calculating tiered pricing: {e}")
            raise
    
    def _get_default_tier(self, tier_type: PricingTierType) -> PricingTier:
        """Get default tier for fallback."""
        return PricingTier(
            tier_id="default",
            tier_name="Default Tier",
            min_threshold=Decimal('0'),
            max_threshold=None,
            base_rate=Decimal('0.05'),
            discount_percentage=Decimal('0'),
            tier_type=tier_type
        )
    
    async def manage_pricing_thresholds(
        self, 
        tier_id: str,
        performance_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Manage and adjust pricing thresholds."""
        try:
            # Get threshold adjustments
            adjustments = await self.threshold_manager.adjust_thresholds_based_on_performance(
                tier_id, performance_data
            )
            
            # Find and update tier
            for tier in self.pricing_tiers.tiers:
                if tier.tier_id == tier_id:
                    multiplier = adjustments.get('threshold_multiplier', Decimal('1.0'))
                    
                    # Apply adjustments
                    tier.min_threshold *= multiplier
                    if tier.max_threshold:
                        tier.max_threshold *= multiplier
                    
                    tier.metadata['last_adjustment'] = datetime.utcnow().isoformat()
                    tier.metadata['adjustment_factor'] = float(multiplier)
                    
                    break
            
            return {
                'tier_id': tier_id,
                'adjustments_applied': adjustments,
                'status': 'success'
            }
            
        except Exception as e:
            logger.error(f"Error managing pricing thresholds: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def apply_volume_discounts(
        self, 
        amount: Decimal,
        volume_tier: str = "standard"
    ) -> Tuple[Decimal, Dict[str, Any]]:
        """Apply volume-based discounts."""
        try:
            return await self.discount_calculator.calculate_volume_discount(
                amount, volume_tier, DiscountType.TIERED_PERCENTAGE
            )
        except Exception as e:
            logger.error(f"Error applying volume discounts: {e}")
            return Decimal('0'), {}
    
    async def optimize_pricing_strategies(
        self, 
        current_performance: Dict[str, float]
    ) -> Dict[str, Any]:
        """Optimize pricing strategies using ML."""
        try:
            current_strategy = {
                'tier_count': len(self.pricing_tiers.tiers),
                'discount_strategies': ['volume', 'tiered', 'loyalty'],
                'optimization_targets': ['revenue', 'conversion', 'satisfaction']
            }
            
            return await self.optimization_engine.optimize_pricing_strategy(
                current_strategy, current_performance
            )
            
        except Exception as e:
            logger.error(f"Error optimizing pricing strategies: {e}")
            return {}
    
    async def handle_promotional_pricing(
        self, 
        promotion_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle promotional pricing campaigns."""
        try:
            promotion_id = promotion_config.get('promotion_id')
            discount_rate = Decimal(str(promotion_config.get('discount_rate', 0.1)))
            valid_until = promotion_config.get('valid_until')
            
            # Create promotional tier
            promo_tier = PricingTier(
                tier_id=f"promo_{promotion_id}",
                tier_name=f"Promotion {promotion_id}",
                min_threshold=Decimal('0'),
                max_threshold=None,
                base_rate=Decimal('0.05'),
                discount_percentage=discount_rate * Decimal('100'),
                tier_type=PricingTierType.PROMOTIONAL,
                metadata={
                    'promotion_id': promotion_id,
                    'valid_until': valid_until,
                    'campaign_type': promotion_config.get('campaign_type', 'general')
                }
            )
            
            # Add promotional tier
            if self.pricing_tiers.add_tier(promo_tier):
                return {
                    'status': 'success',
                    'promotion_id': promotion_id,
                    'tier_id': promo_tier.tier_id,
                    'discount_rate': float(discount_rate),
                    'message': 'Promotional pricing activated'
                }
            else:
                return {
                    'status': 'error',
                    'message': 'Failed to activate promotional pricing'
                }
                
        except Exception as e:
            logger.error(f"Error handling promotional pricing: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def calculate_price_elasticity(
        self, 
        current_price: Decimal,
        demand_data: List[Dict[str, float]]
    ) -> PriceElasticityAnalysis:
        """Calculate price elasticity and optimal pricing."""
        try:
            # Simple price elasticity calculation
            if len(demand_data) < 2:
                elasticity_coefficient = -1.0  # Default elasticity
            else:
                # Calculate elasticity from historical data
                price_changes = []
                quantity_changes = []
                
                for i in range(1, len(demand_data)):
                    prev_data = demand_data[i-1]
                    curr_data = demand_data[i]
                    
                    price_change = (curr_data['price'] - prev_data['price']) / prev_data['price']
                    quantity_change = (curr_data['quantity'] - prev_data['quantity']) / prev_data['quantity']
                    
                    if price_change != 0:
                        elasticity = quantity_change / price_change
                        price_changes.append(price_change)
                        quantity_changes.append(elasticity)
                
                elasticity_coefficient = sum(quantity_changes) / len(quantity_changes) if quantity_changes else -1.0
            
            # Calculate optimal price (simplified)
            optimal_price_multiplier = 1.0 + (abs(elasticity_coefficient) - 1.0) * 0.1
            optimal_price = current_price * Decimal(str(optimal_price_multiplier))
            
            # Generate demand forecast
            demand_forecast = {
                'current_demand': 100.0,
                'optimal_demand': 100.0 * (1.0 + abs(elasticity_coefficient) * 0.1),
                'elasticity_impact': elasticity_coefficient * 100.0
            }
            
            # Calculate revenue impact
            current_revenue = current_price * Decimal('100')  # Assume base quantity of 100
            optimal_revenue = optimal_price * Decimal(str(demand_forecast['optimal_demand']))
            
            revenue_impact = {
                'current_revenue': current_revenue,
                'optimal_revenue': optimal_revenue,
                'revenue_change': optimal_revenue - current_revenue,
                'revenue_change_percentage': float((optimal_revenue - current_revenue) / current_revenue * 100)
            }
            
            return PriceElasticityAnalysis(
                current_price=current_price,
                optimal_price=optimal_price,
                elasticity_coefficient=elasticity_coefficient,
                demand_forecast=demand_forecast,
                revenue_impact=revenue_impact,
                confidence_score=min(0.95, len(demand_data) / 10.0)
            )
            
        except Exception as e:
            logger.error(f"Error calculating price elasticity: {e}")
            # Return default analysis
            return PriceElasticityAnalysis(
                current_price=current_price,
                optimal_price=current_price,
                elasticity_coefficient=-1.0,
                demand_forecast={'current_demand': 100.0},
                revenue_impact={'current_revenue': current_price * Decimal('100')},
                confidence_score=0.5
            )
    
    async def implement_dynamic_tiers(
        self, 
        market_conditions: Dict[str, float]
    ) -> Dict[str, Any]:
        """Implement dynamic pricing tiers based on market conditions."""
        try:
            market_volatility = market_conditions.get('volatility', 0.1)
            demand_level = market_conditions.get('demand_level', 1.0)
            competition_pressure = market_conditions.get('competition_pressure', 0.5)
            
            # Calculate dynamic adjustment factor
            adjustment_factor = 1.0 + (demand_level - 1.0) * 0.2 - competition_pressure * 0.15
            adjustment_factor = max(0.7, min(1.5, adjustment_factor))  # Clamp between 70% and 150%
            
            dynamic_tiers_created = 0
            
            # Create dynamic tiers based on current market conditions
            for base_tier in self.pricing_tiers.tiers[:3]:  # Only adjust first 3 tiers
                if base_tier.tier_type == PricingTierType.VOLUME_BASED:
                    dynamic_tier = PricingTier(
                        tier_id=f"dynamic_{base_tier.tier_id}",
                        tier_name=f"Dynamic {base_tier.tier_name}",
                        min_threshold=base_tier.min_threshold,
                        max_threshold=base_tier.max_threshold,
                        base_rate=base_tier.base_rate * Decimal(str(adjustment_factor)),
                        discount_percentage=base_tier.discount_percentage,
                        tier_type=PricingTierType.DYNAMIC_ML,
                        metadata={
                            'base_tier_id': base_tier.tier_id,
                            'adjustment_factor': adjustment_factor,
                            'market_conditions': market_conditions,
                            'created_at': datetime.utcnow().isoformat()
                        }
                    )
                    
                    if self.pricing_tiers.add_tier(dynamic_tier):
                        dynamic_tiers_created += 1
            
            return {
                'status': 'success',
                'dynamic_tiers_created': dynamic_tiers_created,
                'adjustment_factor': adjustment_factor,
                'market_conditions': market_conditions,
                'message': f'Created {dynamic_tiers_created} dynamic pricing tiers'
            }
            
        except Exception as e:
            logger.error(f"Error implementing dynamic tiers: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def generate_pricing_analytics(
        self, 
        time_range: Optional[Tuple[datetime, datetime]] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive pricing analytics."""
        try:
            if not time_range:
                end_time = datetime.utcnow()
                start_time = end_time - timedelta(days=30)
                time_range = (start_time, end_time)
            
            # Analyze cached calculations
            relevant_calculations = [
                calc for calc in self.calculation_cache.values()
                if start_time <= datetime.fromisoformat(calc.metadata.get('created_at', datetime.utcnow().isoformat())) <= end_time
            ]
            
            if not relevant_calculations:
                return {
                    'status': 'no_data',
                    'message': 'No pricing calculations found in the specified time range'
                }
            
            # Calculate analytics
            total_calculations = len(relevant_calculations)
            avg_processing_time = sum(calc.calculation_time for calc in relevant_calculations) / total_calculations
            total_savings = sum(calc.tier_savings for calc in relevant_calculations)
            total_original_amount = sum(calc.original_amount for calc in relevant_calculations)
            
            # Tier usage analysis
            tier_usage = {}
            for calc in relevant_calculations:
                tier_id = calc.applied_tier.tier_id
                tier_usage[tier_id] = tier_usage.get(tier_id, 0) + 1
            
            # Performance metrics
            avg_discount_percentage = float(sum(calc.discount_amount / calc.original_amount for calc in relevant_calculations if calc.original_amount > 0) / total_calculations * 100)
            
            analytics = {
                'time_range': {
                    'start': time_range[0].isoformat(),
                    'end': time_range[1].isoformat()
                },
                'summary': {
                    'total_calculations': total_calculations,
                    'avg_processing_time_ms': round(avg_processing_time, 2),
                    'total_savings': float(total_savings),
                    'total_original_amount': float(total_original_amount),
                    'savings_percentage': float(total_savings / total_original_amount * 100) if total_original_amount > 0 else 0.0,
                    'avg_discount_percentage': round(avg_discount_percentage, 2)
                },
                'tier_usage': tier_usage,
                'performance_targets': {
                    'target_processing_time_ms': 20.0,
                    'actual_avg_processing_time_ms': round(avg_processing_time, 2),
                    'performance_ratio': min(1.0, 20.0 / avg_processing_time) if avg_processing_time > 0 else 1.0
                },
                'recommendations': []
            }
            
            # Generate recommendations
            if avg_processing_time > 20.0:
                analytics['recommendations'].append({
                    'type': 'performance',
                    'message': 'Processing time exceeds target of 20ms',
                    'suggestion': 'Consider optimizing tier lookup algorithms'
                })
            
            if avg_discount_percentage < 5.0:
                analytics['recommendations'].append({
                    'type': 'pricing',
                    'message': 'Low discount rates may indicate conservative pricing',
                    'suggestion': 'Consider more aggressive discount strategies for customer acquisition'
                })
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error generating pricing analytics: {e}")
            return {'status': 'error', 'error': str(e)}

# Export main class
__all__ = ["TieredPricingCalculator", "PricingTier", "PricingCalculation", "PriceElasticityAnalysis"]