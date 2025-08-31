"""
Revenue Allocation Engine - Intelligent revenue distribution and allocation optimization

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

  STRICT COPYRIGHT WARNING 
This code is the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, reproduction, modification, or distribution without explicit 
written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import uuid

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from sklearn.cluster import KMeans

from ..utils.exceptions import RevenueAllocationError
from ..utils.validators import validate_allocation_data
from ..utils.cache import cache_revenue_allocation
from ..analytics.metrics import MetricsCollector
from ..security.encryption import EncryptionManager

logger = logging.getLogger(__name__)


class AllocationStrategy(Enum):
    """Revenue allocation strategies"""
    EQUAL_DISTRIBUTION = "equal_distribution"
    PERFORMANCE_BASED = "performance_based"
    PRIORITY_WEIGHTED = "priority_weighted"
    RISK_ADJUSTED = "risk_adjusted"
    GROWTH_FOCUSED = "growth_focused"
    BALANCED_PORTFOLIO = "balanced_portfolio"
    DYNAMIC_OPTIMIZATION = "dynamic_optimization"
    MARKET_DRIVEN = "market_driven"


class AllocationPriority(Enum):
    """Allocation priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    OPTIONAL = "optional"


class AllocationConstraint(Enum):
    """Allocation constraint types"""
    MINIMUM_AMOUNT = "minimum_amount"
    MAXIMUM_AMOUNT = "maximum_amount"
    PERCENTAGE_LIMIT = "percentage_limit"
    DEPENDENCY = "dependency"
    EXCLUSIVITY = "exclusivity"
    TIMING = "timing"


@dataclass
class AllocationTarget:
    """Revenue allocation target"""
    target_id: str
    name: str
    category: str
    priority: AllocationPriority
    minimum_allocation: Decimal
    maximum_allocation: Decimal
    preferred_percentage: float
    current_allocation: Decimal
    performance_score: float
    risk_score: float
    constraints: List[Dict[str, Any]] = field(default_factory=list)
    
    @property
    def allocation_percentage(self) -> float:
        """Calculate current allocation percentage"""
        # This would be calculated based on total available amount
        return 0.0  # Placeholder
    
    @property
    def is_satisfied(self) -> bool:
        """Check if allocation constraints are satisfied"""



        return (self.minimum_allocation <= self.current_allocation <= self.maximum_allocation)


@dataclass
class AllocationMetrics:
    """Revenue allocation performance metrics"""
    total_amount: Decimal
    allocated_amount: Decimal
    unallocated_amount: Decimal
    allocation_efficiency: float
    satisfaction_rate: float
    risk_score: float
    diversification_score: float
    optimization_score: float
    constraint_violations: int
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def allocation_rate(self) -> float:
        """Calculate allocation rate"""
        if self.total_amount == 0:
            return 0.0
        return float((self.allocated_amount / self.total_amount) * 100)


@dataclass
class AllocationResult:
    """Revenue allocation result"""
    allocation_id: str
    strategy_used: AllocationStrategy
    targets: List[AllocationTarget]
    metrics: AllocationMetrics
    recommendations: List[str]
    warnings: List[str]
    execution_time: float
    created_at: datetime = field(default_factory=datetime.utcnow)


class BaseAllocationOptimizer(ABC):
    """Abstract base class for allocation optimizers"""
    
    @abstractmethod
    async def optimize(
        self,
        total_amount: Decimal,
        targets: List[AllocationTarget],
        constraints: Dict[str, Any]
    ) -> List[AllocationTarget]:
        """Optimize allocation across targets"""
        pass


class PerformanceBasedOptimizer(BaseAllocationOptimizer):
    """Performance-based allocation optimizer"""
    
    async def optimize(
        self,
        total_amount: Decimal,
        targets: List[AllocationTarget],
        constraints: Dict[str, Any]
    ) -> List[AllocationTarget]:
        """Optimize based on performance scores"""



        try:
            # Calculate total performance score
            total_performance = sum(target.performance_score for target in targets)
            
            if total_performance == 0:
                # Fall back to equal distribution
                amount_per_target = total_amount / len(targets)
                for target in targets:
                    target.current_allocation = amount_per_target
                return targets
            
            # Allocate based on performance scores
            for target in targets:
                performance_ratio = target.performance_score / total_performance
                allocated_amount = total_amount * Decimal(str(performance_ratio))
                
                # Apply constraints
                allocated_amount = max(target.minimum_allocation, allocated_amount)
                allocated_amount = min(target.maximum_allocation, allocated_amount)
                
                target.current_allocation = allocated_amount
            
            return targets
            
        except Exception as e:
            logger.error(f"Error in performance-based optimization: {e}")
            raise RevenueAllocationError(f"Performance optimization failed: {e}")


class RiskAdjustedOptimizer(BaseAllocationOptimizer):
    """Risk-adjusted allocation optimizer"""
    
    async def optimize(
        self,
        total_amount: Decimal,
        targets: List[AllocationTarget],
        constraints: Dict[str, Any]
    ) -> List[AllocationTarget]:
        """Optimize based on risk-adjusted returns"""



        try:
            # Calculate risk-adjusted scores
            risk_adjusted_scores = []
            for target in targets:
                # Risk-adjusted performance = performance / (1 + risk)
                risk_adjusted_score = target.performance_score / (1 + target.risk_score)
                risk_adjusted_scores.append(risk_adjusted_score)
            
            total_risk_adjusted = sum(risk_adjusted_scores)
            
            if total_risk_adjusted == 0:
                # Fall back to equal distribution
                amount_per_target = total_amount / len(targets)
                for target in targets:
                    target.current_allocation = amount_per_target
                return targets
            
            # Allocate based on risk-adjusted scores
            for i, target in enumerate(targets):
                ratio = risk_adjusted_scores[i] / total_risk_adjusted
                allocated_amount = total_amount * Decimal(str(ratio))
                
                # Apply constraints
                allocated_amount = max(target.minimum_allocation, allocated_amount)
                allocated_amount = min(target.maximum_allocation, allocated_amount)
                
                target.current_allocation = allocated_amount
            
            return targets
            
        except Exception as e:
            logger.error(f"Error in risk-adjusted optimization: {e}")
            raise RevenueAllocationError(f"Risk-adjusted optimization failed: {e}")


class DynamicOptimizer(BaseAllocationOptimizer):
    """Dynamic optimization using mathematical optimization"""
    
    async def optimize(
        self,
        total_amount: Decimal,
        targets: List[AllocationTarget],
        constraints: Dict[str, Any]
    ) -> List[AllocationTarget]:
        """Optimize using mathematical optimization"""



        try:
            n_targets = len(targets)
            
            # Define objective function (maximize utility)
            def objective(allocations):
                total_utility = 0
                for i, target in enumerate(targets):
                    allocation = allocations[i]
                    # Utility = performance * allocation - risk * allocation^2
                    utility = (target.performance_score * allocation - 
                              target.risk_score * allocation ** 2)
                    total_utility += utility
                return -total_utility  # Negative for minimization
            
            # Define constraints
            constraint_functions = []
            
            # Budget constraint
            def budget_constraint(allocations):
                return float(total_amount) - sum(allocations)
            
            constraint_functions.append({
                'type': 'eq',
                'fun': budget_constraint
            })
            
            # Individual target constraints
            for i, target in enumerate(targets):
                # Minimum constraint
                def min_constraint(allocations, idx=i, min_val=float(target.minimum_allocation)):
                    return allocations[idx] - min_val
                
                # Maximum constraint
                def max_constraint(allocations, idx=i, max_val=float(target.maximum_allocation)):
                    return max_val - allocations[idx]
                
                constraint_functions.extend([
                    {'type': 'ineq', 'fun': min_constraint},
                    {'type': 'ineq', 'fun': max_constraint}
                ])
            
            # Initial guess (equal distribution)
            initial_guess = [float(total_amount) / n_targets] * n_targets
            
            # Bounds for each allocation
            bounds = [
                (float(target.minimum_allocation), float(target.maximum_allocation))
                for target in targets
            ]
            
            # Optimize
            result = minimize(
                objective,
                initial_guess,
                method='SLSQP',
                bounds=bounds,
                constraints=constraint_functions
            )
            
            if result.success:
                # Update allocations
                for i, target in enumerate(targets):
                    target.current_allocation = Decimal(str(result.x[i]))
            else:
                # Fall back to performance-based allocation
                performance_optimizer = PerformanceBasedOptimizer()
                targets = await performance_optimizer.optimize(total_amount, targets, constraints)
            
            return targets
            
        except Exception as e:
            logger.error(f"Error in dynamic optimization: {e}")
            # Fall back to simpler method
            performance_optimizer = PerformanceBasedOptimizer()
            return await performance_optimizer.optimize(total_amount, targets, constraints)


class RevenueAllocator:
    """Comprehensive revenue allocation system"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.optimizers = {}
        self.allocation_history = []
        self.metrics_collector = MetricsCollector()
        self.encryption_manager = EncryptionManager()
        
    async def initialize(self) -> None:
        """Initialize revenue allocator"""



        try:
            # Initialize optimizers
            self.optimizers = {
                AllocationStrategy.PERFORMANCE_BASED: PerformanceBasedOptimizer(),
                AllocationStrategy.RISK_ADJUSTED: RiskAdjustedOptimizer(),
                AllocationStrategy.DYNAMIC_OPTIMIZATION: DynamicOptimizer()
            }
            
            logger.info("Revenue allocator initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing revenue allocator: {e}")
            raise
    
    @cache_revenue_allocation
    async def allocate_revenue(
        self,
        total_amount: Decimal,
        targets: List[AllocationTarget],
        strategy: AllocationStrategy = AllocationStrategy.DYNAMIC_OPTIMIZATION,
        constraints: Optional[Dict[str, Any]] = None
    ) -> AllocationResult:
        """Allocate revenue across targets using specified strategy"""



        try:
            validate_allocation_data({'total_amount': total_amount, 'targets': targets})
            
            start_time = datetime.utcnow()
            constraints = constraints or {}
            
            # Validate total amount
            if total_amount <= 0:
                raise RevenueAllocationError("Total amount must be positive")
            
            # Validate targets
            if not targets:
                raise RevenueAllocationError("No allocation targets provided")
            
            # Check minimum allocation requirements
            total_minimum = sum(target.minimum_allocation for target in targets)
            if total_amount < total_minimum:
                raise RevenueAllocationError(
                    f"Total amount ({total_amount}) is less than minimum requirements ({total_minimum})"
                )
            
            # Select optimizer
            optimizer = self.optimizers.get(strategy)
            if not optimizer:
                # Fall back to performance-based
                optimizer = self.optimizers[AllocationStrategy.PERFORMANCE_BASED]
                strategy = AllocationStrategy.PERFORMANCE_BASED
            
            # Perform optimization
            optimized_targets = await optimizer.optimize(total_amount, targets, constraints)
            
            # Calculate metrics
            metrics = await self._calculate_allocation_metrics(total_amount, optimized_targets)
            
            # Generate recommendations and warnings
            recommendations = await self._generate_recommendations(optimized_targets, metrics)
            warnings = await self._generate_warnings(optimized_targets, metrics)
            
            # Create result
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            result = AllocationResult(
                allocation_id=str(uuid.uuid4()),
                strategy_used=strategy,
                targets=optimized_targets,
                metrics=metrics,
                recommendations=recommendations,
                warnings=warnings,
                execution_time=execution_time
            )
            
            # Store in history
            self.allocation_history.append(result)
            
            # Collect metrics
            await self.metrics_collector.record_allocation_metrics(metrics)
            
            logger.info(f"Revenue allocated: {result.allocation_id} - {total_amount} across {len(targets)} targets")
            
            return result
            
        except Exception as e:
            logger.error(f"Error allocating revenue: {e}")
            raise RevenueAllocationError(f"Revenue allocation failed: {e}")
    
    async def _calculate_allocation_metrics(
        self,
        total_amount: Decimal,
        targets: List[AllocationTarget]
    ) -> AllocationMetrics:
        """Calculate allocation performance metrics"""



        try:
            allocated_amount = sum(target.current_allocation for target in targets)
            unallocated_amount = total_amount - allocated_amount
            
            # Allocation efficiency (how much of total amount is allocated)
            allocation_efficiency = float((allocated_amount / total_amount) * 100) if total_amount > 0 else 0
            
            # Satisfaction rate (percentage of targets with satisfied constraints)
            satisfied_targets = len([t for t in targets if t.is_satisfied])
            satisfaction_rate = (satisfied_targets / len(targets) * 100) if targets else 0
            
            # Average risk score
            risk_score = np.mean([target.risk_score for target in targets]) if targets else 0
            
            # Diversification score (based on allocation distribution)
            allocations = [float(target.current_allocation) for target in targets]
            if sum(allocations) > 0:
                normalized_allocations = [a / sum(allocations) for a in allocations]
                # Calculate Herfindahl-Hirschman Index (lower = more diversified)
                hhi = sum(a ** 2 for a in normalized_allocations)
                diversification_score = (1 - hhi) * 100  # Convert to percentage
            else:
                diversification_score = 0
            
            # Optimization score (based on performance-weighted allocation)
            total_performance = sum(target.performance_score for target in targets)
            if total_performance > 0:
                expected_utility = 0
                for target in targets:
                    weight = target.performance_score / total_performance
                    allocation_ratio = float(target.current_allocation / total_amount)
                    expected_utility += weight * allocation_ratio
                optimization_score = expected_utility * 100
            else:
                optimization_score = 50  # Neutral score
            
            # Count constraint violations
            constraint_violations = len([t for t in targets if not t.is_satisfied])
            
            return AllocationMetrics(
                total_amount=total_amount,
                allocated_amount=allocated_amount,
                unallocated_amount=unallocated_amount,
                allocation_efficiency=allocation_efficiency,
                satisfaction_rate=satisfaction_rate,
                risk_score=risk_score,
                diversification_score=diversification_score,
                optimization_score=optimization_score,
                constraint_violations=constraint_violations
            )
            
        except Exception as e:
            logger.error(f"Error calculating allocation metrics: {e}")
            raise RevenueAllocationError(f"Metrics calculation failed: {e}")
    
    async def _generate_recommendations(
        self,
        targets: List[AllocationTarget],
        metrics: AllocationMetrics
    ) -> List[str]:
        """Generate allocation recommendations"""
        recommendations = []
        
        # Efficiency recommendations
        if metrics.allocation_efficiency < 95:
            recommendations.append(
                "Consider allocating remaining unallocated amount to improve efficiency"
            )
        
        # Diversification recommendations
        if metrics.diversification_score < 50:
            recommendations.append(
                "Consider improving diversification by balancing allocations across targets"
            )
        
        # Risk recommendations
        if metrics.risk_score > 0.7:
            recommendations.append(
                "High overall risk detected - consider reducing allocation to high-risk targets"
            )
        
        # Performance recommendations
        if metrics.optimization_score < 60:
            recommendations.append(
                "Allocation may not be optimal - consider reallocating based on performance scores"
            )
        
        # Target-specific recommendations
        high_performing_targets = [t for t in targets if t.performance_score > 0.8]
        if high_performing_targets:
            under_allocated = [
                t for t in high_performing_targets 
                if float(t.current_allocation) < float(t.maximum_allocation) * 0.8
            ]
            if under_allocated:
                recommendations.append(
                    f"Consider increasing allocation to high-performing targets: {', '.join(t.name for t in under_allocated[:3])}"
                )
        
        return recommendations
    
    async def _generate_warnings(
        self,
        targets: List[AllocationTarget],
        metrics: AllocationMetrics
    ) -> List[str]:
        """Generate allocation warnings"""
        warnings = []
        
        # Constraint violation warnings
        if metrics.constraint_violations > 0:
            violated_targets = [t for t in targets if not t.is_satisfied]
            warnings.append(
                f"Constraint violations detected in {len(violated_targets)} targets"
            )
        
        # Risk warnings
        high_risk_targets = [t for t in targets if t.risk_score > 0.8]
        if high_risk_targets:
            total_high_risk_allocation = sum(t.current_allocation for t in high_risk_targets)
            if total_high_risk_allocation > metrics.total_amount * Decimal('0.5'):
                warnings.append("Over 50% of allocation is in high-risk targets")
        
        # Concentration warnings
        if metrics.diversification_score < 30:
            warnings.append("Low diversification - allocation is highly concentrated")
        
        # Performance warnings
        low_performing_targets = [t for t in targets if t.performance_score < 0.3]
        if low_performing_targets:
            total_low_performance_allocation = sum(t.current_allocation for t in low_performing_targets)
            if total_low_performance_allocation > metrics.total_amount * Decimal('0.3'):
                warnings.append("Over 30% of allocation is in low-performing targets")
        
        return warnings
    
    async def rebalance_allocation(
        self,
        allocation_id: str,
        new_total_amount: Optional[Decimal] = None,
        strategy: Optional[AllocationStrategy] = None
    ) -> AllocationResult:
        """Rebalance existing allocation"""



        try:
            # Find original allocation
            original_allocation = next(
                (a for a in self.allocation_history if a.allocation_id == allocation_id),
                None
            )
            
            if not original_allocation:
                raise RevenueAllocationError(f"Allocation not found: {allocation_id}")
            
            # Use new amount or keep original
            total_amount = new_total_amount or original_allocation.metrics.total_amount
            
            # Use new strategy or keep original
            rebalance_strategy = strategy or original_allocation.strategy_used
            
            # Reset current allocations
            targets = original_allocation.targets.copy()
            for target in targets:
                target.current_allocation = Decimal('0')
            
            # Perform new allocation
            return await self.allocate_revenue(total_amount, targets, rebalance_strategy)
            
        except Exception as e:
            logger.error(f"Error rebalancing allocation: {e}")
            raise RevenueAllocationError(f"Rebalancing failed: {e}")
    
    async def simulate_allocation_scenarios(
        self,
        base_amount: Decimal,
        targets: List[AllocationTarget],
        scenarios: List[Dict[str, Any]]
    ) -> Dict[str, AllocationResult]:
        """Simulate different allocation scenarios"""



        try:
            results = {}
            
            for scenario in scenarios:
                scenario_name = scenario.get('name', 'Unnamed Scenario')
                scenario_amount = Decimal(str(scenario.get('amount', base_amount)))
                scenario_strategy = AllocationStrategy(
                    scenario.get('strategy', AllocationStrategy.DYNAMIC_OPTIMIZATION.value)
                )
                
                # Modify targets based on scenario
                scenario_targets = []
                for target in targets:
                    scenario_target = AllocationTarget(
                        target_id=target.target_id,
                        name=target.name,
                        category=target.category,
                        priority=target.priority,
                        minimum_allocation=target.minimum_allocation,
                        maximum_allocation=target.maximum_allocation,
                        preferred_percentage=target.preferred_percentage,
                        current_allocation=Decimal('0'),
                        performance_score=target.performance_score,
                        risk_score=target.risk_score,
                        constraints=target.constraints.copy()
                    )
                    
                    # Apply scenario modifications
                    modifications = scenario.get('target_modifications', {})
                    if target.target_id in modifications:
                        mod = modifications[target.target_id]
                        if 'performance_multiplier' in mod:
                            scenario_target.performance_score *= mod['performance_multiplier']
                        if 'risk_multiplier' in mod:
                            scenario_target.risk_score *= mod['risk_multiplier']
                        if 'max_allocation_multiplier' in mod:
                            scenario_target.maximum_allocation *= Decimal(str(mod['max_allocation_multiplier']))
                    
                    scenario_targets.append(scenario_target)
                
                # Run allocation
                result = await self.allocate_revenue(
                    scenario_amount,
                    scenario_targets,
                    scenario_strategy
                )
                
                results[scenario_name] = result
            
            return results
            
        except Exception as e:
            logger.error(f"Error simulating allocation scenarios: {e}")
            raise RevenueAllocationError(f"Scenario simulation failed: {e}")
    
    async def optimize_allocation_constraints(
        self,
        targets: List[AllocationTarget],
        total_amount: Decimal
    ) -> List[AllocationTarget]:
        """Optimize allocation constraints for better results"""



        try:
            optimized_targets = []
            
            for target in targets:
                optimized_target = AllocationTarget(
                    target_id=target.target_id,
                    name=target.name,
                    category=target.category,
                    priority=target.priority,
                    minimum_allocation=target.minimum_allocation,
                    maximum_allocation=target.maximum_allocation,
                    preferred_percentage=target.preferred_percentage,
                    current_allocation=target.current_allocation,
                    performance_score=target.performance_score,
                    risk_score=target.risk_score,
                    constraints=target.constraints.copy()
                )
                
                # Optimize constraints based on performance and risk
                if target.performance_score > 0.8 and target.risk_score < 0.3:
                    # High performance, low risk - increase maximum allocation
                    optimized_target.maximum_allocation = min(
                        total_amount * Decimal('0.4'),  # Max 40% of total
                        target.maximum_allocation * Decimal('1.2')
                    )
                elif target.performance_score < 0.3 or target.risk_score > 0.8:
                    # Low performance or high risk - decrease maximum allocation
                    optimized_target.maximum_allocation = max(
                        target.minimum_allocation,
                        target.maximum_allocation * Decimal('0.8')
                    )
                
                # Adjust minimum allocation based on priority
                if target.priority in [AllocationPriority.CRITICAL, AllocationPriority.HIGH]:
                    optimized_target.minimum_allocation = max(
                        target.minimum_allocation,
                        total_amount * Decimal('0.05')  # At least 5% for high priority
                    )
                
                optimized_targets.append(optimized_target)
            
            return optimized_targets
            
        except Exception as e:
            logger.error(f"Error optimizing allocation constraints: {e}")
            raise RevenueAllocationError(f"Constraint optimization failed: {e}")
    
    async def get_allocation_analytics(self, period_days: int = 30) -> Dict[str, Any]:
        """Get allocation analytics for specified period"""



        try:
            # Filter allocations by period
            cutoff_date = datetime.utcnow() - timedelta(days=period_days)
            recent_allocations = [
                a for a in self.allocation_history
                if a.created_at >= cutoff_date
            ]
            
            if not recent_allocations:
                return {'message': 'No allocations in specified period'}
            
            # Calculate analytics
            total_allocations = len(recent_allocations)
            
            # Strategy usage
            strategy_usage = {}
            for allocation in recent_allocations:
                strategy = allocation.strategy_used.value
                strategy_usage[strategy] = strategy_usage.get(strategy, 0) + 1
            
            # Average metrics
            avg_efficiency = np.mean([a.metrics.allocation_efficiency for a in recent_allocations])
            avg_satisfaction = np.mean([a.metrics.satisfaction_rate for a in recent_allocations])
            avg_diversification = np.mean([a.metrics.diversification_score for a in recent_allocations])
            avg_optimization = np.mean([a.metrics.optimization_score for a in recent_allocations])
            
            # Performance trends
            efficiency_trend = [a.metrics.allocation_efficiency for a in recent_allocations[-10:]]
            satisfaction_trend = [a.metrics.satisfaction_rate for a in recent_allocations[-10:]]
            
            # Top performing strategies
            strategy_performance = {}
            for allocation in recent_allocations:
                strategy = allocation.strategy_used.value
                if strategy not in strategy_performance:
                    strategy_performance[strategy] = []
                strategy_performance[strategy].append(allocation.metrics.optimization_score)
            
            avg_strategy_performance = {
                strategy: np.mean(scores)
                for strategy, scores in strategy_performance.items()
            }
            
            analytics = {
                'period_days': period_days,
                'total_allocations': total_allocations,
                'strategy_usage': strategy_usage,
                'average_metrics': {
                    'efficiency': avg_efficiency,
                    'satisfaction_rate': avg_satisfaction,
                    'diversification_score': avg_diversification,
                    'optimization_score': avg_optimization
                },
                'performance_trends': {
                    'efficiency': efficiency_trend,
                    'satisfaction': satisfaction_trend
                },
                'strategy_performance': avg_strategy_performance,
                'best_strategy': max(avg_strategy_performance, key=avg_strategy_performance.get)
                if avg_strategy_performance else None,
                'constraint_violations': sum(a.metrics.constraint_violations for a in recent_allocations),
                'total_recommendations': sum(len(a.recommendations) for a in recent_allocations),
                'total_warnings': sum(len(a.warnings) for a in recent_allocations)
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error generating allocation analytics: {e}")
            raise RevenueAllocationError(f"Analytics generation failed: {e}")
    
    async def export_allocation_report(self, allocation_id: str) -> Dict[str, Any]:
        """Export detailed allocation report"""



        try:
            allocation = next(
                (a for a in self.allocation_history if a.allocation_id == allocation_id),
                None
            )
            
            if not allocation:
                raise RevenueAllocationError(f"Allocation not found: {allocation_id}")
            
            report = {
                'allocation_info': {
                    'id': allocation.allocation_id,
                    'strategy': allocation.strategy_used.value,
                    'created_at': allocation.created_at.isoformat(),
                    'execution_time': allocation.execution_time
                },
                'financial_summary': {
                    'total_amount': str(allocation.metrics.total_amount),
                    'allocated_amount': str(allocation.metrics.allocated_amount),
                    'unallocated_amount': str(allocation.metrics.unallocated_amount),
                    'allocation_rate': allocation.metrics.allocation_rate
                },
                'performance_metrics': {
                    'allocation_efficiency': allocation.metrics.allocation_efficiency,
                    'satisfaction_rate': allocation.metrics.satisfaction_rate,
                    'risk_score': allocation.metrics.risk_score,
                    'diversification_score': allocation.metrics.diversification_score,
                    'optimization_score': allocation.metrics.optimization_score,
                    'constraint_violations': allocation.metrics.constraint_violations
                },
                'target_allocations': [
                    {
                        'id': target.target_id,
                        'name': target.name,
                        'category': target.category,
                        'priority': target.priority.value,
                        'allocated_amount': str(target.current_allocation),
                        'minimum_required': str(target.minimum_allocation),
                        'maximum_allowed': str(target.maximum_allocation),
                        'performance_score': target.performance_score,
                        'risk_score': target.risk_score,
                        'is_satisfied': target.is_satisfied
                    }
                    for target in allocation.targets
                ],
                'recommendations': allocation.recommendations,
                'warnings': allocation.warnings,
                'generated_at': datetime.utcnow().isoformat()
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error exporting allocation report: {e}")
            raise RevenueAllocationError(f"Report export failed: {e}")
