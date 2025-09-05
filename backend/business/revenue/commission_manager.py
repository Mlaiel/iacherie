"""Commission Manager - IA Influencer Agent Platform
=================================================

Advanced commission management system for affiliate marketing,
sponsorships, and revenue sharing with automated calculations.

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
import uuid

logger = logging.getLogger(__name__)


class CommissionType(Enum):
    """Types of commissions."""
    AFFILIATE = "affiliate"
    SPONSORSHIP = "sponsorship" 
    REFERRAL = "referral"
    COLLABORATION = "collaboration"
    PLATFORM_SHARE = "platform_share"
    PERFORMANCE_BONUS = "performance_bonus"


class CommissionStructure(Enum):
    """Commission calculation structures."""
    FLAT_RATE = "flat_rate"
    PERCENTAGE = "percentage"
    TIERED = "tiered"
    PERFORMANCE_BASED = "performance_based"
    HYBRID = "hybrid"


@dataclass
class CommissionRule:
    """Commission calculation rule."""
    rule_id: str
    commission_type: CommissionType
    structure: CommissionStructure
    rate: Decimal
    minimum_threshold: Optional[Decimal] = None
    maximum_cap: Optional[Decimal] = None
    tier_rules: Optional[List[Dict[str, Any]]] = None
    performance_metrics: Optional[Dict[str, Any]] = None


@dataclass
class Commission:
    """Commission calculation result."""
    commission_id: str
    payee_id: str
    commission_type: CommissionType
    base_amount: Decimal
    commission_rate: Decimal
    commission_amount: Decimal
    net_payout: Decimal
    calculation_details: Dict[str, Any]
    payment_status: str
    created_at: datetime


class CommissionManager:
    """Advanced commission management and calculation system."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize commission manager."""
        self.config = config or {}
        self.commission_rules: Dict[str, CommissionRule] = {}
        self.commission_history: List[Commission] = []
        self.pending_payouts: List[Commission] = []
        
    async def calculate_commission(
        self,
        payee_id: str,
        commission_type: CommissionType,
        transaction_data: Dict[str, Any],
        custom_rules: Optional[Dict[str, Any]] = None
    ) -> Commission:
        """Calculate commission for a specific transaction."""
        try:
            # Get applicable commission rule
            rule = await self._get_commission_rule(commission_type, payee_id, custom_rules)
            
            # Extract base amount from transaction
            base_amount = Decimal(str(transaction_data.get('amount', 0)))
            
            # Calculate commission based on structure
            commission_result = await self._calculate_by_structure(
                base_amount, rule, transaction_data
            )
            
            # Apply caps and thresholds
            final_commission = await self._apply_commission_limits(
                commission_result, rule
            )
            
            # Create commission record
            commission = Commission(
                commission_id=str(uuid.uuid4()),
                payee_id=payee_id,
                commission_type=commission_type,
                base_amount=base_amount,
                commission_rate=commission_result['rate'],
                commission_amount=final_commission,
                net_payout=final_commission,  # Before deductions
                calculation_details=commission_result,
                payment_status='pending',
                created_at=datetime.utcnow()
            )
            
            # Store commission
            await self._store_commission(commission)
            
            return commission
            
        except Exception as e:
            logger.error(f"Commission calculation failed: {e}")
            raise
    
    async def calculate_batch_commissions(
        self,
        transactions: List[Dict[str, Any]],
        commission_mapping: Dict[str, CommissionType]
    ) -> Dict[str, Any]:
        """Calculate commissions for multiple transactions."""
        try:
            commission_results = []
            total_commissions = Decimal('0')
            
            for transaction in transactions:
                payee_id = transaction.get('payee_id')
                commission_type = commission_mapping.get(payee_id, CommissionType.AFFILIATE)
                
                commission = await self.calculate_commission(
                    payee_id, commission_type, transaction
                )
                
                commission_results.append(commission)
                total_commissions += commission.commission_amount
            
            # Generate batch summary
            batch_summary = await self._generate_batch_summary(commission_results)
            
            return {
                "batch_id": str(uuid.uuid4()),
                "transaction_count": len(transactions),
                "commission_results": [self._serialize_commission(c) for c in commission_results],
                "total_commissions": float(total_commissions),
                "batch_summary": batch_summary,
                "processing_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Batch commission calculation failed: {e}")
            raise
    
    async def optimize_commission_structure(
        self,
        historical_data: List[Dict[str, Any]],
        optimization_goals: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Optimize commission structures for better performance."""
        try:
            # Analyze current performance
            current_performance = await self._analyze_commission_performance(historical_data)
            
            # Generate optimization scenarios
            optimization_scenarios = await self._generate_optimization_scenarios(
                current_performance, optimization_goals
            )
            
            # Simulate scenarios
            scenario_results = await self._simulate_commission_scenarios(
                historical_data, optimization_scenarios
            )
            
            # Recommend optimal structure
            optimal_structure = await self._recommend_optimal_structure(
                scenario_results, optimization_goals
            )
            
            return {
                "current_performance": current_performance,
                "optimization_scenarios": optimization_scenarios,
                "scenario_results": scenario_results,
                "recommended_structure": optimal_structure,
                "projected_improvements": await self._calculate_projected_improvements(
                    current_performance, optimal_structure
                )
            }
            
        except Exception as e:
            logger.error(f"Commission optimization failed: {e}")
            raise
    
    async def _get_commission_rule(
        self,
        commission_type: CommissionType,
        payee_id: str,
        custom_rules: Optional[Dict[str, Any]] = None
    ) -> CommissionRule:
        """Get applicable commission rule."""
        # Check for custom rules first
        if custom_rules:
            return await self._create_rule_from_custom(custom_rules, commission_type)
        
        # Check for existing rule
        rule_key = f"{commission_type.value}_{payee_id}"
        if rule_key in self.commission_rules:
            return self.commission_rules[rule_key]
        
        # Use default rule for commission type
        return await self._get_default_rule(commission_type)
    
    async def _create_rule_from_custom(
        self,
        custom_rules: Dict[str, Any],
        commission_type: CommissionType
    ) -> CommissionRule:
        """Create commission rule from custom parameters."""
        structure_str = custom_rules.get('structure', 'percentage')
        structure = CommissionStructure(structure_str)
        
        return CommissionRule(
            rule_id=str(uuid.uuid4()),
            commission_type=commission_type,
            structure=structure,
            rate=Decimal(str(custom_rules.get('rate', 0.1))),
            minimum_threshold=Decimal(str(custom_rules.get('minimum_threshold', 0))) if custom_rules.get('minimum_threshold') else None,
            maximum_cap=Decimal(str(custom_rules.get('maximum_cap', 0))) if custom_rules.get('maximum_cap') else None,
            tier_rules=custom_rules.get('tier_rules'),
            performance_metrics=custom_rules.get('performance_metrics')
        )
    
    async def _get_default_rule(self, commission_type: CommissionType) -> CommissionRule:
        """Get default commission rule for type."""
        default_rules = {
            CommissionType.AFFILIATE: {
                'structure': CommissionStructure.PERCENTAGE,
                'rate': Decimal('0.10'),  # 10%
                'minimum_threshold': Decimal('25.00'),
                'maximum_cap': None
            },
            CommissionType.SPONSORSHIP: {
                'structure': CommissionStructure.FLAT_RATE,
                'rate': Decimal('100.00'),  # $100 flat
                'minimum_threshold': None,
                'maximum_cap': Decimal('5000.00')
            },
            CommissionType.REFERRAL: {
                'structure': CommissionStructure.TIERED,
                'rate': Decimal('0.05'),  # Base 5%
                'tier_rules': [
                    {'min': 0, 'max': 1000, 'rate': 0.05},
                    {'min': 1000, 'max': 5000, 'rate': 0.07},
                    {'min': 5000, 'max': float('inf'), 'rate': 0.10}
                ]
            },
            CommissionType.COLLABORATION: {
                'structure': CommissionStructure.PERCENTAGE,
                'rate': Decimal('0.15'),  # 15%
                'minimum_threshold': Decimal('50.00'),
                'maximum_cap': None
            },
            CommissionType.PLATFORM_SHARE: {
                'structure': CommissionStructure.PERCENTAGE,
                'rate': Decimal('0.05'),  # 5%
                'minimum_threshold': None,
                'maximum_cap': None
            },
            CommissionType.PERFORMANCE_BONUS: {
                'structure': CommissionStructure.PERFORMANCE_BASED,
                'rate': Decimal('0.20'),  # 20% bonus
                'performance_metrics': {
                    'target_metric': 'conversion_rate',
                    'threshold': 0.05,
                    'multiplier': 2.0
                }
            }
        }
        
        rule_config = default_rules.get(commission_type, default_rules[CommissionType.AFFILIATE])
        
        return CommissionRule(
            rule_id=str(uuid.uuid4()),
            commission_type=commission_type,
            structure=rule_config['structure'],
            rate=rule_config['rate'],
            minimum_threshold=rule_config.get('minimum_threshold'),
            maximum_cap=rule_config.get('maximum_cap'),
            tier_rules=rule_config.get('tier_rules'),
            performance_metrics=rule_config.get('performance_metrics')
        )
    
    async def _calculate_by_structure(
        self,
        base_amount: Decimal,
        rule: CommissionRule,
        transaction_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate commission based on structure type."""
        if rule.structure == CommissionStructure.FLAT_RATE:
            return await self._calculate_flat_rate(base_amount, rule)
        elif rule.structure == CommissionStructure.PERCENTAGE:
            return await self._calculate_percentage(base_amount, rule)
        elif rule.structure == CommissionStructure.TIERED:
            return await self._calculate_tiered(base_amount, rule)
        elif rule.structure == CommissionStructure.PERFORMANCE_BASED:
            return await self._calculate_performance_based(base_amount, rule, transaction_data)
        elif rule.structure == CommissionStructure.HYBRID:
            return await self._calculate_hybrid(base_amount, rule, transaction_data)
        else:
            # Default to percentage
            return await self._calculate_percentage(base_amount, rule)
    
    async def _calculate_flat_rate(
        self,
        base_amount: Decimal,
        rule: CommissionRule
    ) -> Dict[str, Any]:
        """Calculate flat rate commission."""
        commission_amount = rule.rate
        
        return {
            'method': 'flat_rate',
            'base_amount': float(base_amount),
            'flat_rate': float(rule.rate),
            'commission_amount': float(commission_amount),
            'rate': float(commission_amount / base_amount) if base_amount > 0 else 0
        }
    
    async def _calculate_percentage(
        self,
        base_amount: Decimal,
        rule: CommissionRule
    ) -> Dict[str, Any]:
        """Calculate percentage-based commission."""
        commission_amount = base_amount * rule.rate
        
        return {
            'method': 'percentage',
            'base_amount': float(base_amount),
            'percentage_rate': float(rule.rate),
            'commission_amount': float(commission_amount),
            'rate': float(rule.rate)
        }
    
    async def _calculate_tiered(
        self,
        base_amount: Decimal,
        rule: CommissionRule
    ) -> Dict[str, Any]:
        """Calculate tiered commission."""
        if not rule.tier_rules:
            # Fallback to base rate
            return await self._calculate_percentage(base_amount, rule)
        
        total_commission = Decimal('0')
        calculation_breakdown = []
        
        remaining_amount = base_amount
        
        for tier in rule.tier_rules:
            tier_min = Decimal(str(tier['min']))
            tier_max = Decimal(str(tier['max']))
            tier_rate = Decimal(str(tier['rate']))
            
            if remaining_amount <= 0:
                break
            
            # Calculate amount in this tier
            if base_amount <= tier_min:
                continue
            
            tier_start = max(tier_min, Decimal('0'))
            tier_end = min(tier_max, base_amount) if tier_max != float('inf') else base_amount
            tier_amount = tier_end - tier_start
            
            if tier_amount > 0:
                tier_commission = tier_amount * tier_rate
                total_commission += tier_commission
                
                calculation_breakdown.append({
                    'tier_range': f"{float(tier_start)}-{float(tier_end)}",
                    'tier_amount': float(tier_amount),
                    'tier_rate': float(tier_rate),
                    'tier_commission': float(tier_commission)
                })
        
        effective_rate = total_commission / base_amount if base_amount > 0 else Decimal('0')
        
        return {
            'method': 'tiered',
            'base_amount': float(base_amount),
            'commission_amount': float(total_commission),
            'rate': float(effective_rate),
            'tier_breakdown': calculation_breakdown
        }
    
    async def _calculate_performance_based(
        self,
        base_amount: Decimal,
        rule: CommissionRule,
        transaction_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate performance-based commission."""
        base_commission = base_amount * rule.rate
        
        if not rule.performance_metrics:
            return {
                'method': 'performance_based',
                'base_amount': float(base_amount),
                'base_commission': float(base_commission),
                'commission_amount': float(base_commission),
                'rate': float(rule.rate),
                'performance_multiplier': 1.0
            }
        
        # Get performance metrics
        target_metric = rule.performance_metrics.get('target_metric')
        threshold = rule.performance_metrics.get('threshold', 0)
        multiplier = rule.performance_metrics.get('multiplier', 1.0)
        
        # Get actual performance value
        actual_performance = transaction_data.get(target_metric, 0)
        
        # Calculate performance multiplier
        if actual_performance >= threshold:
            performance_multiplier = Decimal(str(multiplier))
        else:
            performance_multiplier = Decimal('1.0')
        
        final_commission = base_commission * performance_multiplier
        
        return {
            'method': 'performance_based',
            'base_amount': float(base_amount),
            'base_commission': float(base_commission),
            'commission_amount': float(final_commission),
            'rate': float(final_commission / base_amount) if base_amount > 0 else 0,
            'performance_multiplier': float(performance_multiplier),
            'performance_details': {
                'metric': target_metric,
                'actual_value': actual_performance,
                'threshold': threshold,
                'multiplier': multiplier
            }
        }
    
    async def _calculate_hybrid(
        self,
        base_amount: Decimal,
        rule: CommissionRule,
        transaction_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate hybrid commission (combination of methods)."""
        # Base percentage commission
        percentage_commission = base_amount * rule.rate
        
        # Performance bonus
        performance_bonus = Decimal('0')
        if rule.performance_metrics:
            performance_result = await self._calculate_performance_based(
                base_amount, rule, transaction_data
            )
            performance_bonus = Decimal(str(performance_result['commission_amount'])) - percentage_commission
        
        total_commission = percentage_commission + performance_bonus
        
        return {
            'method': 'hybrid',
            'base_amount': float(base_amount),
            'percentage_commission': float(percentage_commission),
            'performance_bonus': float(performance_bonus),
            'commission_amount': float(total_commission),
            'rate': float(total_commission / base_amount) if base_amount > 0 else 0
        }
    
    async def _apply_commission_limits(
        self,
        commission_result: Dict[str, Any],
        rule: CommissionRule
    ) -> Decimal:
        """Apply minimum thresholds and maximum caps."""
        commission_amount = Decimal(str(commission_result['commission_amount']))
        
        # Apply minimum threshold
        if rule.minimum_threshold and commission_amount < rule.minimum_threshold:
            return Decimal('0')  # No commission if below threshold
        
        # Apply maximum cap
        if rule.maximum_cap and commission_amount > rule.maximum_cap:
            return rule.maximum_cap
        
        return commission_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    async def _store_commission(self, commission: Commission) -> None:
        """Store commission record."""
        self.commission_history.append(commission)
        self.pending_payouts.append(commission)
        
        # Keep only last 1000 records
        if len(self.commission_history) > 1000:
            self.commission_history = self.commission_history[-1000:]
        
        logger.info(f"Stored commission {commission.commission_id} for payee {commission.payee_id}")
    
    async def _generate_batch_summary(
        self,
        commission_results: List[Commission]
    ) -> Dict[str, Any]:
        """Generate summary for batch commission calculation."""
        if not commission_results:
            return {}
        
        total_base = sum(float(c.base_amount) for c in commission_results)
        total_commission = sum(float(c.commission_amount) for c in commission_results)
        
        # Group by commission type
        type_breakdown = {}
        for commission in commission_results:
            comm_type = commission.commission_type.value
            if comm_type not in type_breakdown:
                type_breakdown[comm_type] = {
                    'count': 0,
                    'total_base': 0,
                    'total_commission': 0
                }
            
            type_breakdown[comm_type]['count'] += 1
            type_breakdown[comm_type]['total_base'] += float(commission.base_amount)
            type_breakdown[comm_type]['total_commission'] += float(commission.commission_amount)
        
        # Calculate average rates
        for comm_type in type_breakdown:
            breakdown = type_breakdown[comm_type]
            if breakdown['total_base'] > 0:
                breakdown['average_rate'] = breakdown['total_commission'] / breakdown['total_base']
            else:
                breakdown['average_rate'] = 0
        
        return {
            'total_base_amount': total_base,
            'total_commission_amount': total_commission,
            'overall_commission_rate': total_commission / total_base if total_base > 0 else 0,
            'commission_count': len(commission_results),
            'type_breakdown': type_breakdown
        }
    
    def _serialize_commission(self, commission: Commission) -> Dict[str, Any]:
        """Serialize commission for JSON output."""
        return {
            'commission_id': commission.commission_id,
            'payee_id': commission.payee_id,
            'commission_type': commission.commission_type.value,
            'base_amount': float(commission.base_amount),
            'commission_rate': float(commission.commission_rate),
            'commission_amount': float(commission.commission_amount),
            'net_payout': float(commission.net_payout),
            'calculation_details': commission.calculation_details,
            'payment_status': commission.payment_status,
            'created_at': commission.created_at.isoformat()
        }
    
    # Additional optimization and analysis methods
    async def _analyze_commission_performance(
        self,
        historical_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze current commission structure performance."""
        if not historical_data:
            return {}
        
        total_revenue = sum(float(item.get('revenue', 0)) for item in historical_data)
        total_commissions = sum(float(item.get('commission', 0)) for item in historical_data)
        
        avg_commission_rate = total_commissions / total_revenue if total_revenue > 0 else 0
        
        # Analyze by commission type
        type_performance = {}
        for item in historical_data:
            comm_type = item.get('commission_type', 'unknown')
            if comm_type not in type_performance:
                type_performance[comm_type] = {
                    'revenue': 0,
                    'commissions': 0,
                    'count': 0
                }
            
            type_performance[comm_type]['revenue'] += float(item.get('revenue', 0))
            type_performance[comm_type]['commissions'] += float(item.get('commission', 0))
            type_performance[comm_type]['count'] += 1
        
        # Calculate rates for each type
        for comm_type in type_performance:
            perf = type_performance[comm_type]
            perf['avg_rate'] = perf['commissions'] / perf['revenue'] if perf['revenue'] > 0 else 0
            perf['avg_commission'] = perf['commissions'] / perf['count'] if perf['count'] > 0 else 0
        
        return {
            'total_revenue': total_revenue,
            'total_commissions': total_commissions,
            'avg_commission_rate': avg_commission_rate,
            'type_performance': type_performance,
            'data_points': len(historical_data)
        }
    
    async def _generate_optimization_scenarios(
        self,
        current_performance: Dict[str, Any],
        optimization_goals: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate commission optimization scenarios."""
        scenarios = []
        
        current_rate = current_performance.get('avg_commission_rate', 0.1)
        
        # Scenario 1: Increase commissions to boost motivation
        scenarios.append({
            'name': 'increased_motivation',
            'description': 'Increase commission rates by 20% to boost partner motivation',
            'rate_adjustment': 1.2,
            'expected_volume_increase': 0.15,
            'cost_increase': 0.2
        })
        
        # Scenario 2: Tiered structure for volume incentives
        scenarios.append({
            'name': 'tiered_volume',
            'description': 'Implement tiered structure to incentivize higher volumes',
            'structure_change': 'tiered',
            'tier_multipliers': [1.0, 1.3, 1.6],
            'expected_volume_increase': 0.25,
            'cost_increase': 0.15
        })
        
        # Scenario 3: Performance-based bonuses
        scenarios.append({
            'name': 'performance_bonuses',
            'description': 'Add performance bonuses for high-quality referrals',
            'bonus_structure': 'performance_based',
            'quality_threshold': 0.8,
            'bonus_multiplier': 1.5,
            'expected_quality_improvement': 0.3
        })
        
        return scenarios
    
    async def _simulate_commission_scenarios(
        self,
        historical_data: List[Dict[str, Any]],
        scenarios: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Simulate different commission scenarios."""
        scenario_results = {}
        
        for scenario in scenarios:
            scenario_name = scenario['name']
            
            # Apply scenario adjustments to historical data
            adjusted_data = await self._apply_scenario_adjustments(historical_data, scenario)
            
            # Calculate projected performance
            projected_performance = await self._calculate_projected_performance(adjusted_data, scenario)
            
            scenario_results[scenario_name] = {
                'scenario_config': scenario,
                'projected_performance': projected_performance,
                'cost_benefit_analysis': await self._analyze_cost_benefit(projected_performance, scenario)
            }
        
        return scenario_results
    
    async def _apply_scenario_adjustments(
        self,
        historical_data: List[Dict[str, Any]],
        scenario: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Apply scenario adjustments to historical data."""
        adjusted_data = []
        
        for item in historical_data:
            adjusted_item = item.copy()
            
            # Apply rate adjustments
            if 'rate_adjustment' in scenario:
                adjusted_item['commission'] = float(item.get('commission', 0)) * scenario['rate_adjustment']
            
            # Apply volume adjustments
            if 'expected_volume_increase' in scenario:
                adjusted_item['volume_multiplier'] = 1 + scenario['expected_volume_increase']
            
            adjusted_data.append(adjusted_item)
        
        return adjusted_data
    
    async def _calculate_projected_performance(
        self,
        adjusted_data: List[Dict[str, Any]],
        scenario: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate projected performance for scenario."""
        total_revenue = sum(float(item.get('revenue', 0)) for item in adjusted_data)
        total_commissions = sum(float(item.get('commission', 0)) for item in adjusted_data)
        
        # Apply volume multipliers
        volume_increase = scenario.get('expected_volume_increase', 0)
        projected_revenue = total_revenue * (1 + volume_increase)
        projected_commissions = total_commissions * (1 + volume_increase)
        
        return {
            'projected_revenue': projected_revenue,
            'projected_commissions': projected_commissions,
            'projected_commission_rate': projected_commissions / projected_revenue if projected_revenue > 0 else 0,
            'volume_increase': volume_increase
        }
    
    async def _analyze_cost_benefit(
        self,
        projected_performance: Dict[str, Any],
        scenario: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze cost-benefit of scenario."""
        additional_revenue = projected_performance['projected_revenue'] - projected_performance.get('baseline_revenue', 0)
        additional_costs = projected_performance['projected_commissions'] - projected_performance.get('baseline_commissions', 0)
        
        roi = (additional_revenue - additional_costs) / additional_costs if additional_costs > 0 else 0
        
        return {
            'additional_revenue': additional_revenue,
            'additional_costs': additional_costs,
            'net_benefit': additional_revenue - additional_costs,
            'roi': roi,
            'payback_period_months': 12 / roi if roi > 0 else float('inf')
        }
    
    async def _recommend_optimal_structure(
        self,
        scenario_results: Dict[str, Any],
        optimization_goals: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Recommend optimal commission structure."""
        best_scenario = None
        best_score = 0
        
        for scenario_name, results in scenario_results.items():
            cost_benefit = results['cost_benefit_analysis']
            
            # Calculate composite score based on goals
            roi_weight = optimization_goals.get('roi_weight', 0.4)
            volume_weight = optimization_goals.get('volume_weight', 0.3)
            quality_weight = optimization_goals.get('quality_weight', 0.3)
            
            roi_score = min(1.0, cost_benefit['roi'] / 2.0)  # Normalize ROI
            volume_score = results['projected_performance'].get('volume_increase', 0)
            quality_score = results['scenario_config'].get('expected_quality_improvement', 0)
            
            composite_score = (
                roi_score * roi_weight +
                volume_score * volume_weight +
                quality_score * quality_weight
            )
            
            if composite_score > best_score:
                best_score = composite_score
                best_scenario = scenario_name
        
        return {
            'recommended_scenario': best_scenario,
            'recommendation_score': best_score,
            'scenario_details': scenario_results.get(best_scenario, {}),
            'implementation_priority': 'high' if best_score > 0.7 else 'medium' if best_score > 0.4 else 'low'
        }
    
    async def _calculate_projected_improvements(
        self,
        current_performance: Dict[str, Any],
        optimal_structure: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate projected improvements from optimization."""
        if not optimal_structure.get('scenario_details'):
            return {}
        
        scenario_details = optimal_structure['scenario_details']
        current_revenue = current_performance.get('total_revenue', 0)
        current_commissions = current_performance.get('total_commissions', 0)
        
        projected_performance = scenario_details.get('projected_performance', {})
        projected_revenue = projected_performance.get('projected_revenue', current_revenue)
        projected_commissions = projected_performance.get('projected_commissions', current_commissions)
        
        revenue_improvement = ((projected_revenue - current_revenue) / current_revenue * 100) if current_revenue > 0 else 0
        commission_efficiency = ((projected_revenue / projected_commissions) / (current_revenue / current_commissions) - 1) * 100 if current_commissions > 0 else 0
        
        return {
            'revenue_improvement_percent': revenue_improvement,
            'commission_efficiency_improvement_percent': commission_efficiency,
            'projected_additional_revenue': projected_revenue - current_revenue,
            'projected_additional_commissions': projected_commissions - current_commissions,
            'implementation_timeline': '2-4 weeks',
            'confidence_level': 'high' if optimal_structure['recommendation_score'] > 0.7 else 'medium'
        }