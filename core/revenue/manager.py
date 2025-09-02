"""Revenue Management System - Strategic revenue portfolio and target management

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  STRICT COPYRIGHT WARNING ⚠️
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
from sqlalchemy import Column, String, DateTime, Numeric, Integer, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID, JSONB

from ..utils.exceptions import RevenueManagementError
from ..utils.validators import validate_revenue_management_data
from ..utils.cache import cache_revenue_management
from ..analytics.metrics import MetricsCollector
from ..security.encryption import EncryptionManager

logger = logging.getLogger(__name__)


class RevenueGoalType(Enum):
    """
Revenue goal types"""

    TOTAL_REVENUE = "total_revenue"
    MONTHLY_RECURRING = "monthly_recurring"
    QUARTERLY_TARGET = "quarterly_target"
    ANNUAL_TARGET = "annual_target"
    GROWTH_RATE = "growth_rate"
    PLATFORM_SPECIFIC = "platform_specific"
    CONTENT_SPECIFIC = "content_specific"
    DIVERSIFICATION = "diversification"


class PortfolioStrategy(Enum):
    """Revenue portfolio strategies"""

    CONSERVATIVE = "conservative"
    BALANCED = "balanced"
    AGGRESSIVE = "aggressive"
    GROWTH_FOCUSED = "growth_focused"
    DIVERSIFIED = "diversified"
    PLATFORM_CONCENTRATED = "platform_concentrated"
    HIGH_RISK_HIGH_REWARD = "high_risk_high_reward"
    STABLE_INCOME = "stable_income"


class RevenueCategory(Enum):
    """Revenue categorization"""

    PRIMARY = "primary"
    SECONDARY = "secondary"
    PASSIVE = "passive"
    ACTIVE = "active"
    EXPERIMENTAL = "experimental"
    LEGACY = "legacy"
    STRATEGIC = "strategic"
    OPPORTUNISTIC = "opportunistic"


@dataclass
class RevenueTarget:
    """Revenue target configuration"""
    target_id: str
    name: str
    goal_type: RevenueGoalType
    target_amount: Decimal
    current_amount: Decimal
    currency: str
    start_date: datetime
    end_date: datetime
    category: RevenueCategory
    priority: int
    description: str
    milestones: List[Dict[str, Any]] = field(default_factory=list)
    
    @property
    def progress_percentage(self) -> float:
        """
Calculate progress percentage"""
        if self.target_amount == 0:
            return 0.0
        return float((self.current_amount / self.target_amount) * 100)
    
    @property
    def remaining_amount(self) -> Decimal:
        """
Calculate remaining amount to reach target"""
        return max(Decimal('0'), self.target_amount - self.current_amount)
    
    @property
    def days_remaining(self) -> int:
        """
Calculate days remaining to reach target"""
        return max(0, (self.end_date - datetime.utcnow()).days)
    
    @property
    def daily_required_rate(self) -> Decimal:
        """
Calculate daily revenue rate required to meet target"""
        if self.days_remaining == 0:
            return Decimal('0')
        return self.remaining_amount / self.days_remaining


@dataclass
class RevenuePortfolio:
    """
Revenue portfolio configuration"""
    portfolio_id: str
    name: str
    strategy: PortfolioStrategy
    targets: List[RevenueTarget]
    risk_tolerance: float
    diversification_score: float
    total_target: Decimal
    total_current: Decimal
    created_at: datetime
    updated_at: datetime
    
    @property
    def overall_progress(self) -> float:
        """
Calculate overall portfolio progress"""
        if self.total_target == 0:
            return 0.0
        return float((self.total_current / self.total_target) * 100)
    
    @property
    def target_count(self) -> int:
        """
Get number of targets in portfolio"""
        return len(self.targets)
    
    @property
    def achieved_targets(self) -> int:
        """
Get number of achieved targets"""
        return len([t for t in self.targets if t.progress_percentage >= 100])


@dataclass
class PerformanceMetrics:
    """
Revenue performance metrics"""
    period_start: datetime
    period_end: datetime
    total_revenue: Decimal
    target_revenue: Decimal
    variance: Decimal
    growth_rate: float
    portfolio_performance: float
    risk_adjusted_return: float
    sharpe_ratio: float
    diversification_ratio: float
    
    @property
    def variance_percentage(self) -> float:
        """
Calculate variance as percentage"""
        if self.target_revenue == 0:
            return 0.0
        return float((self.variance / self.target_revenue) * 100)


class RevenueManager:
    """
Comprehensive revenue management system"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.portfolios = {}
        self.targets = {}
        self.metrics_collector = MetricsCollector()
        self.encryption_manager = EncryptionManager()
        self.performance_history = []
        
    async def initialize(self) -> None:
        """
Initialize revenue manager"""
        try:
            # Load existing portfolios and targets
            await self._load_portfolios()
            await self._load_targets()
            
            # Setup performance tracking
            await self._setup_performance_tracking()
            
            logger.info("Revenue manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing revenue manager: {e}")
            raise
    
    async def _load_portfolios(self) -> None:
        """Load existing revenue portfolios"""
        # In production, load from database
        # For now, create sample portfolio
        sample_portfolio = RevenuePortfolio(
            portfolio_id=str(uuid.uuid4()),
            name="Main Revenue Portfolio",
            strategy=PortfolioStrategy.BALANCED,
            targets=[],
            risk_tolerance=0.6,
            diversification_score=0.8,
            total_target=Decimal('10000'),
            total_current=Decimal('0'),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        self.portfolios[sample_portfolio.portfolio_id] = sample_portfolio
    
    async def _load_targets(self) -> None:
        try:
                    # Request validation
                    if not data:
                        raise ValueError("Invalid request")
            
                    # Process request
                    result = await self._handle__load_targets_request(data)
            
                    # Return response
                    return {"status": "success", "data": result}
            
                except Exception as e:
                    logger.error(f"API handler _load_targets failed: {e}")
                    return {"status": "error", "message": str(e)}
    async def _setup_performance_tracking(self) -> None:
        """
Setup performance tracking system"""
        self.performance_config = self.config.get('performance', {
            'tracking_frequency': 'daily',
            'benchmark_period': 30,
            'risk_free_rate': 0.02
        })
    
    async def create_portfolio(
        self,
        name: str,
        strategy: PortfolioStrategy,
        risk_tolerance: float,
        description: Optional[str] = None
    ) -> str:
        """
Create new revenue portfolio"""
        try:
            portfolio_id = str(uuid.uuid4())
            
            portfolio = RevenuePortfolio(
                portfolio_id=portfolio_id,
                name=name,
                strategy=strategy,
                targets=[],
                risk_tolerance=risk_tolerance,
                diversification_score=0.0,
                total_target=Decimal('0'),
                total_current=Decimal('0'),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            self.portfolios[portfolio_id] = portfolio
            
            logger.info(f"Portfolio created: {portfolio_id} - {name}")
            
            return portfolio_id
            
        except Exception as e:
            logger.error(f"Error creating portfolio: {e}")
            raise RevenueManagementError(f"Portfolio creation failed: {e}")
    
    async def create_target(
        self,
        portfolio_id: str,
        name: str,
        goal_type: RevenueGoalType,
        target_amount: Decimal,
        end_date: datetime,
        category: RevenueCategory,
        priority: int = 1,
        description: str = ""
    ) -> str:
        """Create new revenue target"""
        try:
            if portfolio_id not in self.portfolios:
                raise RevenueManagementError(f"Portfolio not found: {portfolio_id}")
            
            target_id = str(uuid.uuid4())
            
            target = RevenueTarget(
                target_id=target_id,
                name=name,
                goal_type=goal_type,
                target_amount=target_amount,
                current_amount=Decimal('0'),
                currency=self.config.get('default_currency', 'EUR'),
                start_date=datetime.utcnow(),
                end_date=end_date,
                category=category,
                priority=priority,
                description=description
            )
            
            # Add to portfolio
            portfolio = self.portfolios[portfolio_id]
            portfolio.targets.append(target)
            portfolio.total_target += target_amount
            portfolio.updated_at = datetime.utcnow()
            
            # Update diversification score
            await self._update_diversification_score(portfolio_id)
            
            self.targets[target_id] = target
            
            logger.info(f"Target created: {target_id} - {name}")
            
            return target_id
            
        except Exception as e:
            logger.error(f"Error creating target: {e}")
            raise RevenueManagementError(f"Target creation failed: {e}")
    
    async def update_target_progress(self, target_id: str, amount: Decimal) -> None:
        """Update target progress"""
        try:
            if target_id not in self.targets:
                raise RevenueManagementError(f"Target not found: {target_id}")
            
            target = self.targets[target_id]
            old_amount = target.current_amount
            target.current_amount += amount
            
            # Update portfolio totals
            for portfolio in self.portfolios.values():
                if target in portfolio.targets:
                    portfolio.total_current += amount
                    portfolio.updated_at = datetime.utcnow()
                    break
            
            # Check for milestone achievements
            await self._check_milestone_achievements(target)
            
            logger.info(f"Target progress updated: {target_id} - {old_amount} -> {target.current_amount}")
            
        except Exception as e:
            logger.error(f"Error updating target progress: {e}")
            raise RevenueManagementError(f"Progress update failed: {e}")
    
    async def _check_milestone_achievements(self, target: RevenueTarget) -> None:
        """Check and record milestone achievements"""
        try:
            progress = target.progress_percentage
            
            # Standard milestones: 25%, 50%, 75%, 100%
            milestones = [25, 50, 75, 100]
            
            for milestone in milestones:
                milestone_key = f"milestone_{milestone}"
                
                # Check if milestone is reached and not already recorded
                if (progress >= milestone and 
                    not any(m.get('percentage') == milestone for m in target.milestones)):
                    
                    milestone_record = {
                        'percentage': milestone,
                        'achieved_at': datetime.utcnow(),
                        'amount_at_achievement': target.current_amount,
                        'days_taken': (datetime.utcnow() - target.start_date).days
                    }
                    
                    target.milestones.append(milestone_record)
                    
                    logger.info(f"Milestone achieved: {target.target_id} - {milestone}%")
            
        except Exception as e:
            logger.error(f"Error checking milestones: {e}")
    
    async def _update_diversification_score(self, portfolio_id: str) -> None:
        """Update portfolio diversification score"""
        try:
            portfolio = self.portfolios[portfolio_id]
            
            if not portfolio.targets:
                portfolio.diversification_score = 0.0
                return
            
            # Calculate diversification based on target categories and types
            categories = set(target.category for target in portfolio.targets)
            goal_types = set(target.goal_type for target in portfolio.targets)
            
            # Simple diversification score calculation
            category_diversity = len(categories) / len(RevenueCategory)
            type_diversity = len(goal_types) / len(RevenueGoalType)
            
            # Weight distribution
            amounts = [target.target_amount for target in portfolio.targets]
            total_amount = sum(amounts)
            
            if total_amount > 0:
                weights = [amount / total_amount for amount in amounts]
                # Calculate Herfindahl-Hirschman Index (lower = more diversified)
                hhi = sum(w ** 2 for w in weights)
                weight_diversity = 1 - hhi
            else:
                weight_diversity = 0.0
            
            # Combine scores
            portfolio.diversification_score = (
                category_diversity * 0.3 +
                type_diversity * 0.3 +
                weight_diversity * 0.4
            )
            
        except Exception as e:
            logger.error(f"Error updating diversification score: {e}")
    
    async def analyze_portfolio_performance(self, portfolio_id: str, period_days: int = 30) -> PerformanceMetrics:
        """Analyze portfolio performance"""
        try:
            if portfolio_id not in self.portfolios:
                raise RevenueManagementError(f"Portfolio not found: {portfolio_id}")
            
            portfolio = self.portfolios[portfolio_id]
            
            # Calculate performance metrics
            period_end = datetime.utcnow()
            period_start = period_end - timedelta(days=period_days)
            
            # Get historical data (simplified for demo)
            total_revenue = portfolio.total_current
            target_revenue = portfolio.total_target
            variance = total_revenue - target_revenue
            
            # Calculate growth rate (simplified)
            growth_rate = 0.05  # 5% demo value
            
            # Portfolio performance
            portfolio_performance = portfolio.overall_progress / 100
            
            # Risk-adjusted return (simplified)
            risk_adjusted_return = portfolio_performance / max(portfolio.risk_tolerance, 0.01)
            
            # Sharpe ratio (simplified)
            risk_free_rate = self.performance_config.get('risk_free_rate', 0.02)
            excess_return = growth_rate - risk_free_rate
            sharpe_ratio = excess_return / max(portfolio.risk_tolerance, 0.01)
            
            metrics = PerformanceMetrics(
                period_start=period_start,
                period_end=period_end,
                total_revenue=total_revenue,
                target_revenue=target_revenue,
                variance=variance,
                growth_rate=growth_rate,
                portfolio_performance=portfolio_performance,
                risk_adjusted_return=risk_adjusted_return,
                sharpe_ratio=sharpe_ratio,
                diversification_ratio=portfolio.diversification_score
            )
            
            # Store in history
            self.performance_history.append({
                'portfolio_id': portfolio_id,
                'timestamp': datetime.utcnow(),
                'metrics': metrics
            })
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error analyzing portfolio performance: {e}")
            raise RevenueManagementError(f"Performance analysis failed: {e}")
    
    async def get_portfolio_recommendations(self, portfolio_id: str) -> List[Dict[str, Any]]:
        """Get portfolio optimization recommendations"""
        try:
            if portfolio_id not in self.portfolios:
                raise RevenueManagementError(f"Portfolio not found: {portfolio_id}")
            
            portfolio = self.portfolios[portfolio_id]
            recommendations = []
            
            # Analyze portfolio
            performance = await self.analyze_portfolio_performance(portfolio_id)
            
            # Diversification recommendations
            if portfolio.diversification_score < 0.6:
                recommendations.append({
                    'type': 'diversification',
                    'priority': 'high',
                    'title': 'Improve Portfolio Diversification',
                    'description': 'Consider adding revenue targets from different categories or platforms',
                    'expected_impact': 'Reduced risk and more stable revenue',
                    'action_items': [
                        'Add targets from underrepresented categories',
                        'Consider new revenue streams',
                        'Balance target amounts across categories'
                    ]
                })
            
            # Performance recommendations
            if performance.portfolio_performance < 0.7:
                recommendations.append({
                    'type': 'performance',
                    'priority': 'high',
                    'title': 'Improve Target Achievement',
                    'description': 'Focus on underperforming targets and optimize strategies',
                    'expected_impact': 'Increased overall portfolio performance',
                    'action_items': [
                        'Review underperforming targets',
                        'Adjust target amounts or timelines',
                        'Implement performance improvement strategies'
                    ]
                })
            
            # Risk recommendations
            if portfolio.risk_tolerance > 0.8:
                recommendations.append({
                    'type': 'risk',
                    'priority': 'medium',
                    'title': 'Consider Risk Reduction',
                    'description': 'High risk tolerance may lead to volatile revenue',
                    'expected_impact': 'More stable and predictable revenue',
                    'action_items': [
                        'Add conservative revenue targets',
                        'Reduce exposure to high-risk opportunities',
                        'Implement risk management strategies'
                    ]
                })
            
            # Growth recommendations
            recent_growth = performance.growth_rate
            if recent_growth < 0.02:  # Less than 2% growth
                recommendations.append({
                    'type': 'growth',
                    'priority': 'medium',
                    'title': 'Accelerate Revenue Growth',
                    'description': 'Current growth rate is below optimal levels',
                    'expected_impact': 'Increased revenue growth rate',
                    'action_items': [
                        'Identify high-growth opportunities',
                        'Increase investment in top-performing areas',
                        'Optimize content and marketing strategies'
                    ]
                })
            
            # Target management recommendations
            overdue_targets = [
                t for t in portfolio.targets 
                if t.end_date < datetime.utcnow() and t.progress_percentage < 100
            ]
            
            if overdue_targets:
                recommendations.append({
                    'type': 'target_management',
                    'priority': 'high',
                    'title': 'Address Overdue Targets',
                    'description': f'{len(overdue_targets)} targets are overdue',
                    'expected_impact': 'Improved target achievement and planning',
                    'action_items': [
                        'Review overdue targets',
                        'Extend deadlines or adjust targets',
                        'Improve target planning and monitoring'
                    ]
                })
            
            # Sort by priority
            priority_order = {'high': 3, 'medium': 2, 'low': 1}
            recommendations.sort(key=lambda x: priority_order.get(x['priority'], 0), reverse=True)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            raise RevenueManagementError(f"Recommendation generation failed: {e}")
    
    async def simulate_portfolio_scenarios(
        self,
        portfolio_id: str,
        scenarios: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Simulate different portfolio scenarios"""
        try:
            if portfolio_id not in self.portfolios:
                raise RevenueManagementError(f"Portfolio not found: {portfolio_id}")
            
            portfolio = self.portfolios[portfolio_id]
            results = {}
            
            for scenario in scenarios:
                scenario_name = scenario.get('name', 'Unnamed Scenario')
                
                # Create scenario portfolio (copy)
                scenario_portfolio = RevenuePortfolio(
                    portfolio_id=f"{portfolio_id}_scenario",
                    name=f"{portfolio.name} - {scenario_name}",
                    strategy=portfolio.strategy,
                    targets=portfolio.targets.copy(),
                    risk_tolerance=portfolio.risk_tolerance,
                    diversification_score=portfolio.diversification_score,
                    total_target=portfolio.total_target,
                    total_current=portfolio.total_current,
                    created_at=portfolio.created_at,
                    updated_at=datetime.utcnow()
                )
                
                # Apply scenario modifications
                modifications = scenario.get('modifications', {})
                
                # Modify targets based on scenario
                for target in scenario_portfolio.targets:
                    if 'revenue_multiplier' in modifications:
                        target.current_amount *= Decimal(str(modifications['revenue_multiplier']))
                    
                    if 'target_adjustment' in modifications:
                        target.target_amount *= Decimal(str(modifications['target_adjustment']))
                
                # Recalculate totals
                scenario_portfolio.total_current = sum(t.current_amount for t in scenario_portfolio.targets)
                scenario_portfolio.total_target = sum(t.target_amount for t in scenario_portfolio.targets)
                
                # Calculate scenario performance
                scenario_performance = scenario_portfolio.overall_progress
                scenario_variance = scenario_portfolio.total_current - scenario_portfolio.total_target
                
                results[scenario_name] = {
                    'total_revenue': str(scenario_portfolio.total_current),
                    'total_target': str(scenario_portfolio.total_target),
                    'performance': scenario_performance,
                    'variance': str(scenario_variance),
                    'achieved_targets': len([
                        t for t in scenario_portfolio.targets 
                        if t.progress_percentage >= 100
                    ]),
                    'total_targets': len(scenario_portfolio.targets),
                    'risk_assessment': self._assess_scenario_risk(scenario_portfolio, modifications)
                }
            
            return {
                'portfolio_id': portfolio_id,
                'scenarios': results,
                'comparison': await self._compare_scenarios(results)
            }
            
        except Exception as e:
            logger.error(f"Error simulating portfolio scenarios: {e}")
            raise RevenueManagementError(f"Scenario simulation failed: {e}")
    
    def _assess_scenario_risk(self, portfolio: RevenuePortfolio, modifications: Dict[str, Any]) -> str:
        """Assess risk level for scenario"""
        risk_factors = 0
        
        # High revenue multiplier increases risk
        if modifications.get('revenue_multiplier', 1.0) > 1.5:
            risk_factors += 1
        
        # Low diversification increases risk
        if portfolio.diversification_score < 0.5:
            risk_factors += 1
        
        # High target adjustments increase risk
        if modifications.get('target_adjustment', 1.0) > 1.3:
            risk_factors += 1
        
        if risk_factors >= 2:
            return 'high'
        elif risk_factors == 1:
            return 'medium'
        else:
            return 'low'
    
    async def _compare_scenarios(self, scenarios: Dict[str, Any]) -> Dict[str, Any]:
        """
Compare scenario results"""
        if not scenarios:
            return {}
        
        # Find best and worst performing scenarios
        performances = {name: data['performance'] for name, data in scenarios.items()}
        
        best_scenario = max(performances, key=performances.get)
        worst_scenario = min(performances, key=performances.get)
        
        # Calculate average performance
        avg_performance = sum(performances.values()) / len(performances)
        
        return {
            'best_scenario': {
                'name': best_scenario,
                'performance': performances[best_scenario]
            },
            'worst_scenario': {
                'name': worst_scenario,
                'performance': performances[worst_scenario]
            },
            'average_performance': avg_performance,
            'performance_range': max(performances.values()) - min(performances.values())
        }
    
    async def get_target_insights(self, target_id: str) -> Dict[str, Any]:
        """
Get detailed insights for specific target"""
        try:
            if target_id not in self.targets:
                raise RevenueManagementError(f"Target not found: {target_id}")
            
            target = self.targets[target_id]
            
            insights = {
                'target_info': {
                    'name': target.name,
                    'progress': target.progress_percentage,
                    'remaining_amount': str(target.remaining_amount),
                    'days_remaining': target.days_remaining,
                    'daily_required_rate': str(target.daily_required_rate)
                },
                'achievement_probability': await self._calculate_achievement_probability(target),
                'milestone_progress': target.milestones,
                'recommendations': await self._get_target_recommendations(target),
                'risk_factors': await self._identify_target_risks(target),
                'optimization_opportunities': await self._identify_optimization_opportunities(target)
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating target insights: {e}")
            raise RevenueManagementError(f"Target insights generation failed: {e}")
    
    async def _calculate_achievement_probability(self, target: RevenueTarget) -> float:
        """Calculate probability of target achievement"""
        try:
            # Simple probability calculation based on current progress and time remaining
            progress = target.progress_percentage
            days_remaining = target.days_remaining
            
            if days_remaining <= 0:
                return 1.0 if progress >= 100 else 0.0
            
            # Calculate required daily rate vs current rate
            if target.milestones:
                # Calculate current rate based on milestones
                days_elapsed = (datetime.utcnow() - target.start_date).days
                if days_elapsed > 0:
                    current_rate = target.current_amount / days_elapsed
                    required_rate = target.daily_required_rate
                    
                    if required_rate == 0:
                        return 1.0
                    
                    rate_ratio = current_rate / required_rate
                    
                    # Simple probability model
                    if rate_ratio >= 1.0:
                        probability = min(0.95, 0.7 + rate_ratio * 0.2)
                    else:
                        probability = max(0.05, rate_ratio * 0.7)
                    
                    return probability
            
            # Fallback: based on progress and time
            time_progress = 1.0 - (days_remaining / max(1, (target.end_date - target.start_date).days))
            
            if progress / 100 >= time_progress:
                return min(0.9, 0.6 + (progress / 100) * 0.3)
            else:
                return max(0.1, (progress / 100) * 0.6)
                
        except Exception as e:
            logger.error(f"Error calculating achievement probability: {e}")
            return 0.5  # Default probability
    
    async def _get_target_recommendations(self, target: RevenueTarget) -> List[str]:
        """Get recommendations for specific target"""
        recommendations = []
        
        # Progress-based recommendations
        if target.progress_percentage < 25 and target.days_remaining < 30:
            recommendations.append("Consider extending deadline or reducing target amount")
        
        if target.progress_percentage > 90:
            recommendations.append("Target likely to be achieved - consider increasing for next period")
        
        # Rate-based recommendations
        if target.daily_required_rate > target.current_amount / max(1, (datetime.utcnow() - target.start_date).days):
            recommendations.append("Increase daily revenue generation activities")
        
        # Category-based recommendations
        if target.category == RevenueCategory.EXPERIMENTAL:
            recommendations.append("Monitor closely and be prepared to pivot strategy")
        
        return recommendations
    
    async def _identify_target_risks(self, target: RevenueTarget) -> List[str]:
        """Identify risks for specific target"""
        risks = []
        
        # Time-based risks
        if target.days_remaining < 7 and target.progress_percentage < 80:
            risks.append("High risk of missing deadline")
        
        # Amount-based risks
        if target.daily_required_rate > target.target_amount * Decimal('0.1'):
            risks.append("Very high daily rate required - may be unrealistic")
        
        # Category-based risks
        if target.category == RevenueCategory.EXPERIMENTAL:
            risks.append("Experimental revenue stream - high uncertainty")
        
        return risks
    
    async def _identify_optimization_opportunities(self, target: RevenueTarget) -> List[str]:
        """Identify optimization opportunities for target"""
        opportunities = []
        
        # Performance-based opportunities
        if target.progress_percentage > 50 and target.days_remaining > 30:
            opportunities.append("Ahead of schedule - opportunity to increase target")
        
        # Milestone-based opportunities
        if len(target.milestones) >= 2:
            # Check if acceleration is possible
            recent_milestones = sorted(target.milestones, key=lambda x: x['achieved_at'])[-2:]
            if len(recent_milestones) == 2:
                time_diff = (recent_milestones[1]['achieved_at'] - recent_milestones[0]['achieved_at']).days
                if time_diff < 30:  # Fast milestone achievement
                    opportunities.append("Fast progress detected - consider accelerating timeline")
        
        return opportunities
    
    async def export_portfolio_report(self, portfolio_id: str) -> Dict[str, Any]:
        """Export comprehensive portfolio report"""
        try:
            if portfolio_id not in self.portfolios:
                raise RevenueManagementError(f"Portfolio not found: {portfolio_id}")
            
            portfolio = self.portfolios[portfolio_id]
            performance = await self.analyze_portfolio_performance(portfolio_id)
            recommendations = await self.get_portfolio_recommendations(portfolio_id)
            
            report = {
                'portfolio_info': {
                    'id': portfolio.portfolio_id,
                    'name': portfolio.name,
                    'strategy': portfolio.strategy.value,
                    'risk_tolerance': portfolio.risk_tolerance,
                    'diversification_score': portfolio.diversification_score,
                    'created_at': portfolio.created_at.isoformat(),
                    'updated_at': portfolio.updated_at.isoformat()
                },
                'financial_summary': {
                    'total_target': str(portfolio.total_target),
                    'total_current': str(portfolio.total_current),
                    'overall_progress': portfolio.overall_progress,
                    'target_count': portfolio.target_count,
                    'achieved_targets': portfolio.achieved_targets
                },
                'performance_metrics': {
                    'total_revenue': str(performance.total_revenue),
                    'variance': str(performance.variance),
                    'variance_percentage': performance.variance_percentage,
                    'growth_rate': performance.growth_rate,
                    'portfolio_performance': performance.portfolio_performance,
                    'risk_adjusted_return': performance.risk_adjusted_return,
                    'sharpe_ratio': performance.sharpe_ratio
                },
                'targets_summary': [
                    {
                        'id': target.target_id,
                        'name': target.name,
                        'goal_type': target.goal_type.value,
                        'category': target.category.value,
                        'progress': target.progress_percentage,
                        'target_amount': str(target.target_amount),
                        'current_amount': str(target.current_amount),
                        'days_remaining': target.days_remaining,
                        'milestones_achieved': len(target.milestones)
                    }
                    for target in portfolio.targets
                ],
                'recommendations': recommendations,
                'generated_at': datetime.utcnow().isoformat()
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error exporting portfolio report: {e}")
            raise RevenueManagementError(f"Report export failed: {e}")
