"""
Automated Revenue Distribution Engine
====================================

Professional revenue distribution system for content creators.
Handles multi-platform revenue aggregation, smart distribution,
performance-based allocation, and automated partner payouts.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved

WARNING: Unauthorized use, copying, or distribution of this code is strictly 
prohibited and subject to legal action under German and international copyright law.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass
from enum import Enum
from decimal import Decimal, ROUND_HALF_UP
import uuid
import json

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from redis import Redis
import numpy as np

from ..models.distribution_model import DistributionModel, StakeholderModel
from ..models.revenue_model import RevenueModel
from .revenue_calculator import Currency, RevenueCalculator
from .payment_processor import PaymentProcessor, PaymentRequest, PaymentGateway


class DistributionType(Enum):
    """Revenue distribution types"""
    EQUAL_SPLIT = "equal_split"
    PERFORMANCE_BASED = "performance_based"
    CUSTOM_PERCENTAGE = "custom_percentage"
    HYBRID = "hybrid"
    TIERED = "tiered"


class StakeholderType(Enum):
    """Types of revenue stakeholders"""
    CREATOR = "creator"
    COLLABORATOR = "collaborator"
    PRODUCER = "producer"
    LABEL = "label"
    MANAGER = "manager"
    PLATFORM = "platform"
    INVESTOR = "investor"
    CHARITY = "charity"


class DistributionStatus(Enum):
    """Distribution processing status"""
    PENDING = "pending"
    CALCULATING = "calculating"
    APPROVED = "approved"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    DISPUTED = "disputed"


@dataclass
class Stakeholder:
    """Revenue stakeholder definition"""
    stakeholder_id: str
    name: str
    type: StakeholderType
    percentage: Decimal
    minimum_amount: Decimal
    payment_info: Dict[str, str]
    metadata: Dict[str, Any]


@dataclass
class DistributionRule:
    """Revenue distribution rule"""
    rule_id: str
    content_id: str
    distribution_type: DistributionType
    stakeholders: List[Stakeholder]
    performance_weights: Dict[str, Decimal]
    minimum_distribution: Decimal
    distribution_frequency: str
    auto_approve_threshold: Decimal
    active: bool


@dataclass
class DistributionCalculation:
    """Revenue distribution calculation result"""
    distribution_id: str
    content_id: str
    total_revenue: Decimal
    currency: Currency
    period_start: datetime
    period_end: datetime
    stakeholder_amounts: Dict[str, Decimal]
    performance_metrics: Dict[str, Any]
    calculation_method: DistributionType
    approval_required: bool


@dataclass
class DistributionResult:
    """Distribution execution result"""
    distribution_id: str
    status: DistributionStatus
    total_distributed: Decimal
    successful_payments: int
    failed_payments: int
    payment_results: List[Dict]
    execution_time: datetime
    error_messages: List[str]


class DistributionEngine:
    """
    Professional revenue distribution engine for IA Influencer Agent platform.
    
    Provides automated revenue distribution, stakeholder management,
    performance-based allocation, and comprehensive payout processing
    for content creator monetization.
    """
    
    def __init__(self, db_session: AsyncSession, redis_client: Redis,
                 revenue_calculator: RevenueCalculator, payment_processor: PaymentProcessor):
        """
        Initialize DistributionEngine.
        
        Args:
            db_session: Async database session
            redis_client: Redis client for caching
            revenue_calculator: Revenue calculation service
            payment_processor: Payment processing service
        """
        self.db_session = db_session
        self.redis = redis_client
        self.revenue_calculator = revenue_calculator
        self.payment_processor = payment_processor
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.cache_ttl = 1800  # 30 minutes
        self.auto_approve_threshold = Decimal('1000.00')  # €1000
        self.minimum_distribution = Decimal('10.00')  # €10
        self.processing_fee_percentage = Decimal('0.02')  # 2%
        
        # Performance weight factors
        self.performance_factors = {
            'views': Decimal('0.30'),
            'engagement': Decimal('0.25'),
            'conversion': Decimal('0.20'),
            'retention': Decimal('0.15'),
            'viral_factor': Decimal('0.10')
        }
    
    async def create_distribution_rule(self, rule: DistributionRule) -> str:
        """
        Create a new revenue distribution rule.
        
        Args:
            rule: Distribution rule configuration
            
        Returns:
            Rule identifier
        """



        try:
            # Validate rule
            await self._validate_distribution_rule(rule)
            
            # Store rule in database
            rule_id = await self._store_distribution_rule(rule)
            
            # Cache rule for quick access
            await self._cache_distribution_rule(rule_id, rule)
            
            self.logger.info(f"Distribution rule created: {rule_id}")
            return rule_id
            
        except Exception as e:
            self.logger.error(f"Error creating distribution rule: {str(e)}")
            raise
    
    async def calculate_distribution(self, content_id: str, period_days: int = 30) -> DistributionCalculation:
        """
        Calculate revenue distribution for content.
        
        Args:
            content_id: Content identifier
            period_days: Distribution period in days
            
        Returns:
            Distribution calculation result
        """



        try:
            # Get distribution rule for content
            rule = await self._get_distribution_rule(content_id)
            if not rule:
                raise ValueError(f"No distribution rule found for content {content_id}")
            
            # Calculate total revenue for period
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=period_days)
            
            total_revenue = await self._calculate_period_revenue(
                content_id, start_date, end_date
            )
            
            if total_revenue < rule.minimum_distribution:
                raise ValueError(
                    f"Revenue {total_revenue} below minimum distribution threshold {rule.minimum_distribution}"
                )
            
            # Get performance metrics
            performance_metrics = await self._get_performance_metrics(
                content_id, start_date, end_date
            )
            
            # Calculate stakeholder distributions
            stakeholder_amounts = await self._calculate_stakeholder_amounts(
                rule, total_revenue, performance_metrics
            )
            
            # Create distribution record
            distribution_id = str(uuid.uuid4())
            
            calculation = DistributionCalculation(
                distribution_id=distribution_id,
                content_id=content_id,
                total_revenue=total_revenue,
                currency=Currency.EUR,  # Default currency
                period_start=start_date,
                period_end=end_date,
                stakeholder_amounts=stakeholder_amounts,
                performance_metrics=performance_metrics,
                calculation_method=rule.distribution_type,
                approval_required=total_revenue > rule.auto_approve_threshold
            )
            
            # Store calculation
            await self._store_distribution_calculation(calculation)
            
            return calculation
            
        except Exception as e:
            self.logger.error(f"Error calculating distribution: {str(e)}")
            raise
    
    async def execute_distribution(self, distribution_id: str, 
                                 auto_approve: bool = False) -> DistributionResult:
        """
        Execute revenue distribution and process payments.
        
        Args:
            distribution_id: Distribution calculation identifier
            auto_approve: Whether to auto-approve without manual review
            
        Returns:
            Distribution execution result
        """



        try:
            # Get distribution calculation
            calculation = await self._get_distribution_calculation(distribution_id)
            if not calculation:
                raise ValueError(f"Distribution calculation not found: {distribution_id}")
            
            # Check approval status
            if calculation.approval_required and not auto_approve:
                # Require manual approval
                await self._request_manual_approval(distribution_id)
                return DistributionResult(
                    distribution_id=distribution_id,
                    status=DistributionStatus.PENDING,
                    total_distributed=Decimal('0'),
                    successful_payments=0,
                    failed_payments=0,
                    payment_results=[],
                    execution_time=datetime.utcnow(),
                    error_messages=["Manual approval required"]
                )
            
            # Update status to processing
            await self._update_distribution_status(distribution_id, DistributionStatus.PROCESSING)
            
            # Process payments to stakeholders
            payment_results = []
            successful_payments = 0
            failed_payments = 0
            total_distributed = Decimal('0')
            error_messages = []
            
            for stakeholder_id, amount in calculation.stakeholder_amounts.items():
                try:
                    # Get stakeholder payment info
                    stakeholder = await self._get_stakeholder_info(stakeholder_id)
                    
                    if amount < stakeholder.minimum_amount:
                        # Skip if below minimum threshold
                        payment_results.append({
                            'stakeholder_id': stakeholder_id,
                            'amount': float(amount),
                            'status': 'skipped',
                            'reason': 'Below minimum threshold'
                        })
                        continue
                    
                    # Create payment request
                    payment_request = PaymentRequest(
                        user_id=stakeholder_id,
                        amount=amount,
                        currency=calculation.currency,
                        gateway=PaymentGateway.STRIPE,  # Default gateway
                        description=f"Revenue distribution for content {calculation.content_id}",
                        metadata={
                            'distribution_id': distribution_id,
                            'content_id': calculation.content_id,
                            'stakeholder_type': stakeholder.type.value
                        },
                        recipient_info=stakeholder.payment_info
                    )
                    
                    # Process payment
                    payment_result = await self.payment_processor.process_payout(payment_request)
                    
                    payment_results.append({
                        'stakeholder_id': stakeholder_id,
                        'amount': float(amount),
                        'status': payment_result.status.value,
                        'payment_id': payment_result.payment_id,
                        'transaction_id': payment_result.transaction_id,
                        'fees': float(payment_result.fees),
                        'net_amount': float(payment_result.net_amount)
                    })
                    
                    if payment_result.status.value in ['completed', 'processing']:
                        successful_payments += 1
                        total_distributed += amount
                    else:
                        failed_payments += 1
                        error_messages.append(
                            f"Payment failed for {stakeholder_id}: {payment_result.error_message}"
                        )
                
                except Exception as e:
                    failed_payments += 1
                    error_messages.append(f"Error processing payment for {stakeholder_id}: {str(e)}")
                    payment_results.append({
                        'stakeholder_id': stakeholder_id,
                        'amount': float(amount),
                        'status': 'failed',
                        'error': str(e)
                    })
            
            # Determine final status
            if failed_payments == 0:
                final_status = DistributionStatus.COMPLETED
            elif successful_payments > 0:
                final_status = DistributionStatus.COMPLETED  # Partial success
            else:
                final_status = DistributionStatus.FAILED
            
            # Update distribution status
            await self._update_distribution_status(distribution_id, final_status)
            
            # Create result
            result = DistributionResult(
                distribution_id=distribution_id,
                status=final_status,
                total_distributed=total_distributed,
                successful_payments=successful_payments,
                failed_payments=failed_payments,
                payment_results=payment_results,
                execution_time=datetime.utcnow(),
                error_messages=error_messages
            )
            
            # Store execution result
            await self._store_distribution_result(result)
            
            # Send notifications
            await self._send_distribution_notifications(result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error executing distribution: {str(e)}")
            raise
    
    async def get_distribution_history(self, content_id: str, limit: int = 50) -> List[Dict]:
        """
        Get distribution history for content.
        
        Args:
            content_id: Content identifier
            limit: Maximum number of records
            
        Returns:
            Distribution history records
        """



        try:
            query = select(DistributionModel).where(
                DistributionModel.content_id == content_id
            ).order_by(DistributionModel.created_at.desc()).limit(limit)
            
            result = await self.db_session.execute(query)
            distributions = result.scalars().all()
            
            history = []
            for dist in distributions:
                history.append({
                    'distribution_id': dist.id,
                    'total_revenue': float(dist.total_revenue),
                    'currency': dist.currency,
                    'period_start': dist.period_start.isoformat(),
                    'period_end': dist.period_end.isoformat(),
                    'status': dist.status,
                    'stakeholder_count': len(dist.stakeholder_amounts),
                    'total_distributed': float(dist.total_distributed),
                    'created_at': dist.created_at.isoformat(),
                    'executed_at': dist.executed_at.isoformat() if dist.executed_at else None
                })
            
            return history
            
        except Exception as e:
            self.logger.error(f"Error getting distribution history: {str(e)}")
            return []
    
    async def optimize_distribution_strategy(self, content_id: str) -> Dict[str, Any]:
        """
        Analyze and optimize distribution strategy for content.
        
        Args:
            content_id: Content identifier
            
        Returns:
            Optimization recommendations and analysis
        """



        try:
            # Get current distribution rule
            current_rule = await self._get_distribution_rule(content_id)
            if not current_rule:
                raise ValueError(f"No distribution rule found for content {content_id}")
            
            # Analyze historical performance
            historical_data = await self._analyze_historical_distributions(content_id)
            
            # Calculate optimization opportunities
            opportunities = []
            
            # Performance-based optimization
            if current_rule.distribution_type != DistributionType.PERFORMANCE_BASED:
                performance_impact = await self._calculate_performance_impact(content_id)
                if performance_impact['potential_increase'] > 0.1:  # 10% improvement
                    opportunities.append({
                        'type': 'performance_based',
                        'description': 'Switch to performance-based distribution',
                        'potential_increase_percent': performance_impact['potential_increase'] * 100,
                        'impact_score': 8.5,
                        'implementation_effort': 'medium'
                    })
            
            # Stakeholder optimization
            stakeholder_analysis = await self._analyze_stakeholder_performance(content_id)
            if stakeholder_analysis['underperforming_count'] > 0:
                opportunities.append({
                    'type': 'stakeholder_optimization',
                    'description': 'Optimize underperforming stakeholder allocations',
                    'potential_increase_percent': 15.0,
                    'impact_score': 7.0,
                    'implementation_effort': 'high'
                })
            
            # Frequency optimization
            frequency_analysis = await self._analyze_distribution_frequency(content_id)
            if frequency_analysis['optimal_frequency'] != current_rule.distribution_frequency:
                opportunities.append({
                    'type': 'frequency_optimization',
                    'description': f"Change distribution frequency to {frequency_analysis['optimal_frequency']}",
                    'potential_increase_percent': 8.0,
                    'impact_score': 6.5,
                    'implementation_effort': 'low'
                })
            
            # Threshold optimization
            if current_rule.minimum_distribution > self.minimum_distribution:
                opportunities.append({
                    'type': 'threshold_optimization',
                    'description': 'Lower minimum distribution threshold',
                    'potential_increase_percent': 5.0,
                    'impact_score': 5.0,
                    'implementation_effort': 'low'
                })
            
            # Sort by impact score
            opportunities.sort(key=lambda x: x['impact_score'], reverse=True)
            
            return {
                'content_id': content_id,
                'current_strategy': {
                    'distribution_type': current_rule.distribution_type.value,
                    'stakeholder_count': len(current_rule.stakeholders),
                    'frequency': current_rule.distribution_frequency,
                    'minimum_amount': float(current_rule.minimum_distribution)
                },
                'historical_performance': historical_data,
                'optimization_opportunities': opportunities[:5],  # Top 5
                'estimated_annual_impact': sum(op['potential_increase_percent'] for op in opportunities[:3]) * 0.8,
                'recommendations': [
                    "Consider implementing performance-based distribution",
                    "Review stakeholder contributions regularly",
                    "Optimize distribution frequency based on revenue patterns",
                    "Monitor and adjust thresholds based on performance"
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Error optimizing distribution strategy: {str(e)}")
            return {}
    
    async def process_bulk_distributions(self, content_ids: List[str]) -> List[DistributionResult]:
        """
        Process distributions for multiple content items.
        
        Args:
            content_ids: List of content identifiers
            
        Returns:
            List of distribution results
        """



        try:
            results = []
            
            for content_id in content_ids:
                try:
                    # Calculate distribution
                    calculation = await self.calculate_distribution(content_id)
                    
                    # Execute distribution
                    result = await self.execute_distribution(
                        calculation.distribution_id, 
                        auto_approve=True
                    )
                    
                    results.append(result)
                    
                    # Add small delay to avoid overwhelming payment processors
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    self.logger.error(f"Error processing distribution for {content_id}: {str(e)}")
                    # Create failed result
                    results.append(DistributionResult(
                        distribution_id=str(uuid.uuid4()),
                        status=DistributionStatus.FAILED,
                        total_distributed=Decimal('0'),
                        successful_payments=0,
                        failed_payments=1,
                        payment_results=[],
                        execution_time=datetime.utcnow(),
                        error_messages=[str(e)]
                    ))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error processing bulk distributions: {str(e)}")
            return []
    
    # Private helper methods
    
    async def _validate_distribution_rule(self, rule: DistributionRule):
        """Validate distribution rule"""
        # Check stakeholder percentages sum to 100%
        total_percentage = sum(s.percentage for s in rule.stakeholders)
        if abs(total_percentage - Decimal('100.0')) > Decimal('0.01'):
            raise ValueError(f"Stakeholder percentages must sum to 100%, got {total_percentage}")
        
        # Validate stakeholder data
        for stakeholder in rule.stakeholders:
            if stakeholder.percentage <= 0:
                raise ValueError(f"Stakeholder percentage must be positive: {stakeholder.stakeholder_id}")
            
            if not stakeholder.payment_info:
                raise ValueError(f"Payment info required for stakeholder: {stakeholder.stakeholder_id}")
    
    async def _get_distribution_rule(self, content_id: str) -> Optional[DistributionRule]:
        """Get distribution rule for content"""
        # Check cache first
        cache_key = f"distribution_rule:{content_id}"
        cached_rule = await self._get_from_cache(cache_key)
        if cached_rule:
            return DistributionRule(**cached_rule)
        
        # Query database
        # Placeholder implementation
        return None
    
    async def _calculate_period_revenue(self, content_id: str, start_date: datetime,
                                      end_date: datetime) -> Decimal:
        """Calculate total revenue for period"""
        # Use revenue calculator to get period revenue
        # Placeholder implementation
        return Decimal('1000.00')  # Sample revenue
    
    async def _get_performance_metrics(self, content_id: str, start_date: datetime,
                                     end_date: datetime) -> Dict[str, Any]:
        """Get performance metrics for content"""
        # Get performance data from analytics
        # Placeholder implementation
        return {
            'views': 50000,
            'engagement_rate': 0.08,
            'conversion_rate': 0.025,
            'retention_rate': 0.65,
            'viral_factor': 1.2
        }
    
    async def _calculate_stakeholder_amounts(self, rule: DistributionRule, 
                                           total_revenue: Decimal,
                                           performance_metrics: Dict) -> Dict[str, Decimal]:
        """Calculate distribution amounts for stakeholders"""
        amounts = {}
        
        if rule.distribution_type == DistributionType.EQUAL_SPLIT:
            # Equal distribution
            per_stakeholder = total_revenue / len(rule.stakeholders)
            for stakeholder in rule.stakeholders:
                amounts[stakeholder.stakeholder_id] = per_stakeholder
                
        elif rule.distribution_type == DistributionType.CUSTOM_PERCENTAGE:
            # Custom percentage distribution
            for stakeholder in rule.stakeholders:
                amounts[stakeholder.stakeholder_id] = (
                    total_revenue * stakeholder.percentage / Decimal('100')
                )
                
        elif rule.distribution_type == DistributionType.PERFORMANCE_BASED:
            # Performance-based distribution
            amounts = await self._calculate_performance_based_distribution(
                rule, total_revenue, performance_metrics
            )
            
        elif rule.distribution_type == DistributionType.HYBRID:
            # Hybrid distribution (base percentage + performance bonus)
            amounts = await self._calculate_hybrid_distribution(
                rule, total_revenue, performance_metrics
            )
        
        return amounts
    
    async def _calculate_performance_based_distribution(self, rule: DistributionRule,
                                                      total_revenue: Decimal,
                                                      performance_metrics: Dict) -> Dict[str, Decimal]:
        """Calculate performance-based distribution"""
        amounts = {}
        
        # Calculate performance scores for each stakeholder
        stakeholder_scores = {}
        total_score = Decimal('0')
        
        for stakeholder in rule.stakeholders:
            # Get stakeholder-specific performance contribution
            contribution_score = await self._calculate_stakeholder_contribution(
                stakeholder, performance_metrics
            )
            stakeholder_scores[stakeholder.stakeholder_id] = contribution_score
            total_score += contribution_score
        
        # Distribute based on performance scores
        for stakeholder in rule.stakeholders:
            if total_score > 0:
                performance_share = stakeholder_scores[stakeholder.stakeholder_id] / total_score
                amounts[stakeholder.stakeholder_id] = total_revenue * performance_share
            else:
                # Fallback to equal split if no performance data
                amounts[stakeholder.stakeholder_id] = total_revenue / len(rule.stakeholders)
        
        return amounts
    
    async def _calculate_stakeholder_contribution(self, stakeholder: Stakeholder,
                                                performance_metrics: Dict) -> Decimal:
        """Calculate stakeholder contribution score"""
        # Base contribution based on stakeholder type
        type_weights = {
            StakeholderType.CREATOR: Decimal('1.0'),
            StakeholderType.COLLABORATOR: Decimal('0.8'),
            StakeholderType.PRODUCER: Decimal('0.6'),
            StakeholderType.MANAGER: Decimal('0.4'),
            StakeholderType.PLATFORM: Decimal('0.2')
        }
        
        base_score = type_weights.get(stakeholder.type, Decimal('0.5'))
        
        # Apply performance multipliers based on metrics
        performance_multiplier = Decimal('1.0')
        
        if 'engagement_rate' in performance_metrics:
            engagement = Decimal(str(performance_metrics['engagement_rate']))
            performance_multiplier *= (Decimal('1.0') + engagement)
        
        if 'viral_factor' in performance_metrics:
            viral = Decimal(str(performance_metrics['viral_factor']))
            performance_multiplier *= viral
        
        return base_score * performance_multiplier
    
    async def _store_distribution_rule(self, rule: DistributionRule) -> str:
        """Store distribution rule in database"""
        # Implementation would store in database
        return rule.rule_id
    
    async def _cache_distribution_rule(self, rule_id: str, rule: DistributionRule):
        """Cache distribution rule"""
        cache_key = f"distribution_rule:{rule.content_id}"
        await self._save_to_cache(cache_key, rule.__dict__)
    
    async def _get_from_cache(self, key: str) -> Optional[Dict]:
        """Get data from cache"""



        try:
            cached_data = await self.redis.get(key)
            return json.loads(cached_data) if cached_data else None
        except:
            return None
    
    async def _save_to_cache(self, key: str, data: Dict, ttl: int = None):
        """Save data to cache"""



        try:
            ttl = ttl or self.cache_ttl
            await self.redis.setex(key, ttl, json.dumps(data, default=str))
        except Exception as e:
            self.logger.warning(f"Cache save failed: {str(e)}")
    
    # Additional helper methods would be implemented here...
    
    async def _store_distribution_calculation(self, calculation: DistributionCalculation):
        """Store distribution calculation in database"""
        pass
    
    async def _get_distribution_calculation(self, distribution_id: str) -> Optional[DistributionCalculation]:
        """Get distribution calculation from database"""



        return None
    
    async def _update_distribution_status(self, distribution_id: str, status: DistributionStatus):
        """Update distribution status"""
        pass
    
    async def _get_stakeholder_info(self, stakeholder_id: str) -> Stakeholder:
        """Get stakeholder information"""
        # Placeholder implementation
        return Stakeholder(
            stakeholder_id=stakeholder_id,
            name="Sample Stakeholder",
            type=StakeholderType.COLLABORATOR,
            percentage=Decimal('25.0'),
            minimum_amount=Decimal('10.0'),
            payment_info={'bank_account': '123456789'},
            metadata={}
        )
    
    async def _analyze_historical_distributions(self, content_id: str) -> Dict:
        """Analyze historical distribution performance"""



        return {'average_amount': 500.0, 'distribution_count': 12}
    
    async def _calculate_performance_impact(self, content_id: str) -> Dict:
        """Calculate potential performance impact"""



        return {'potential_increase': 0.15}
    
    async def _analyze_stakeholder_performance(self, content_id: str) -> Dict:
        """Analyze stakeholder performance"""



        return {'underperforming_count': 1}
    
    async def _analyze_distribution_frequency(self, content_id: str) -> Dict:
        """Analyze optimal distribution frequency"""



        return {'optimal_frequency': 'weekly'}
