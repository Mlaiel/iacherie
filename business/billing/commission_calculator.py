"""
Commission Calculator Engine - Advanced commission calculation system
=====================================================================

Sophisticated commission calculation engine with tier-based structures,
performance bonuses, and automated distribution for content creators.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use prohibited.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import pandas as pd
import numpy as np
import redis
import asyncpg
from decimal import Decimal
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class CommissionTier(Enum):
    """Commission tier levels"""
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"

class CommissionType(Enum):
    """Types of commissions"""
    CONTENT_SALES = "content_sales"
    LICENSING_REVENUE = "licensing_revenue"
    SUBSCRIPTION_REVENUE = "subscription_revenue"
    ADVERTISING_REVENUE = "advertising_revenue"
    COLLABORATION_REVENUE = "collaboration_revenue"
    PLATFORM_FEES = "platform_fees"
    REFERRAL_BONUS = "referral_bonus"

@dataclass
class CommissionRule:
    """Commission calculation rule"""
    tier: CommissionTier
    commission_type: CommissionType
    base_rate: Decimal
    min_threshold: Decimal
    max_cap: Optional[Decimal]
    performance_multiplier: Decimal
    effective_from: datetime
    effective_to: Optional[datetime]

@dataclass
class CommissionData:
    """Commission calculation result"""
    commission_id: str
    creator_id: str
    revenue_amount: Decimal
    commission_rate: Decimal
    commission_amount: Decimal
    tier: CommissionTier
    commission_type: CommissionType
    calculation_period: tuple[datetime, datetime]
    performance_bonus: Decimal
    total_payout: Decimal
    currency: str

class CommissionCalculatorEngine:
    """
    Advanced commission calculation system with performance-based tiers,
    automated calculations, and real-time tracking for content creators.
    """
    
    def __init__(self, redis_client: redis.Redis, db_pool: asyncpg.Pool):
        self.redis = redis_client
        self.db_pool = db_pool
        self.commission_rules = {}
        
    async def initialize(self) -> None:
        """Initialize commission calculator engine"""
        try:
            await self._setup_database_tables()
            await self._load_commission_rules()
            await self._initialize_tier_thresholds()
            logger.info("Commission Calculator Engine initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Commission Calculator Engine: {e}")
            raise

    async def _setup_database_tables(self) -> None:
        """Setup database tables for commission management"""
        async with self.db_pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS commission_tiers (
                    id SERIAL PRIMARY KEY,
                    tier_name VARCHAR(20) NOT NULL,
                    min_revenue DECIMAL(15,2) NOT NULL,
                    min_sales_count INTEGER NOT NULL,
                    commission_multiplier DECIMAL(5,4) NOT NULL,
                    benefits TEXT[],
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS commission_rules (
                    id SERIAL PRIMARY KEY,
                    tier VARCHAR(20) NOT NULL,
                    commission_type VARCHAR(30) NOT NULL,
                    base_rate DECIMAL(5,4) NOT NULL,
                    min_threshold DECIMAL(15,2) NOT NULL,
                    max_cap DECIMAL(15,2),
                    performance_multiplier DECIMAL(5,4) DEFAULT 1.0,
                    effective_from DATE NOT NULL,
                    effective_to DATE,
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS commission_calculations (
                    id SERIAL PRIMARY KEY,
                    commission_id VARCHAR(100) UNIQUE NOT NULL,
                    creator_id VARCHAR(255) NOT NULL,
                    revenue_amount DECIMAL(15,2) NOT NULL,
                    commission_rate DECIMAL(5,4) NOT NULL,
                    commission_amount DECIMAL(15,2) NOT NULL,
                    tier VARCHAR(20) NOT NULL,
                    commission_type VARCHAR(30) NOT NULL,
                    calculation_period_start DATE NOT NULL,
                    calculation_period_end DATE NOT NULL,
                    performance_bonus DECIMAL(15,2) DEFAULT 0,
                    total_payout DECIMAL(15,2) NOT NULL,
                    currency VARCHAR(3) NOT NULL,
                    paid_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT NOW(),
                    INDEX idx_commissions_creator (creator_id, calculation_period_end DESC),
                    INDEX idx_commissions_type (commission_type, created_at DESC)
                );
            """)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS creator_performance_metrics (
                    id SERIAL PRIMARY KEY,
                    creator_id VARCHAR(255) NOT NULL,
                    metric_period DATE NOT NULL,
                    total_revenue DECIMAL(15,2) NOT NULL,
                    content_sales_count INTEGER DEFAULT 0,
                    engagement_score DECIMAL(5,2) DEFAULT 0,
                    customer_satisfaction DECIMAL(5,2) DEFAULT 0,
                    quality_score DECIMAL(5,2) DEFAULT 0,
                    current_tier VARCHAR(20) NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW(),
                    UNIQUE(creator_id, metric_period)
                );
            """)

    async def _load_commission_rules(self) -> None:
        """Load commission rules into memory"""
        try:
            # Initialize default commission rules
            default_rules = [
                # Content Sales Commissions
                CommissionRule(CommissionTier.BRONZE, CommissionType.CONTENT_SALES, Decimal('0.70'), Decimal('0'), None, Decimal('1.0'), datetime.now(), None),
                CommissionRule(CommissionTier.SILVER, CommissionType.CONTENT_SALES, Decimal('0.75'), Decimal('1000'), None, Decimal('1.1'), datetime.now(), None),
                CommissionRule(CommissionTier.GOLD, CommissionType.CONTENT_SALES, Decimal('0.80'), Decimal('5000'), None, Decimal('1.2'), datetime.now(), None),
                CommissionRule(CommissionTier.PLATINUM, CommissionType.CONTENT_SALES, Decimal('0.85'), Decimal('15000'), None, Decimal('1.3'), datetime.now(), None),
                CommissionRule(CommissionTier.DIAMOND, CommissionType.CONTENT_SALES, Decimal('0.90'), Decimal('50000'), None, Decimal('1.5'), datetime.now(), None),
                
                # Licensing Revenue Commissions
                CommissionRule(CommissionTier.BRONZE, CommissionType.LICENSING_REVENUE, Decimal('0.60'), Decimal('0'), None, Decimal('1.0'), datetime.now(), None),
                CommissionRule(CommissionTier.SILVER, CommissionType.LICENSING_REVENUE, Decimal('0.65'), Decimal('1000'), None, Decimal('1.1'), datetime.now(), None),
                CommissionRule(CommissionTier.GOLD, CommissionType.LICENSING_REVENUE, Decimal('0.70'), Decimal('5000'), None, Decimal('1.2'), datetime.now(), None),
                CommissionRule(CommissionTier.PLATINUM, CommissionType.LICENSING_REVENUE, Decimal('0.75'), Decimal('15000'), None, Decimal('1.3'), datetime.now(), None),
                CommissionRule(CommissionTier.DIAMOND, CommissionType.LICENSING_REVENUE, Decimal('0.80'), Decimal('50000'), None, Decimal('1.5'), datetime.now(), None),
            ]
            
            # Store rules in structured format
            for rule in default_rules:
                key = f"{rule.tier.value}_{rule.commission_type.value}"
                self.commission_rules[key] = rule
                
        except Exception as e:
            logger.error(f"Failed to load commission rules: {e}")

    async def _initialize_tier_thresholds(self) -> None:
        """Initialize creator tier thresholds"""
        try:
            tier_thresholds = {
                CommissionTier.BRONZE: {'min_revenue': 0, 'min_sales': 0, 'multiplier': 1.0},
                CommissionTier.SILVER: {'min_revenue': 1000, 'min_sales': 10, 'multiplier': 1.1},
                CommissionTier.GOLD: {'min_revenue': 5000, 'min_sales': 50, 'multiplier': 1.2},
                CommissionTier.PLATINUM: {'min_revenue': 15000, 'min_sales': 150, 'multiplier': 1.3},
                CommissionTier.DIAMOND: {'min_revenue': 50000, 'min_sales': 500, 'multiplier': 1.5}
            }
            
            # Cache tier thresholds
            for tier, thresholds in tier_thresholds.items():
                self.redis.hmset(f"tier_thresholds_{tier.value}", thresholds)
                
        except Exception as e:
            logger.error(f"Failed to initialize tier thresholds: {e}")

    async def calculate_commission(self, creator_id: str, revenue_data: Dict[str, Any],
                                 commission_type: CommissionType,
                                 calculation_period: tuple[datetime, datetime]) -> CommissionData:
        """Calculate commission for creator based on revenue and performance"""
        try:
            # Get creator's current tier
            creator_tier = await self._get_creator_tier(creator_id, calculation_period[1])
            
            # Get commission rule
            rule_key = f"{creator_tier.value}_{commission_type.value}"
            rule = self.commission_rules.get(rule_key)
            
            if not rule:
                # Fallback to bronze tier
                rule_key = f"{CommissionTier.BRONZE.value}_{commission_type.value}"
                rule = self.commission_rules.get(rule_key)
                creator_tier = CommissionTier.BRONZE
            
            if not rule:
                raise HTTPException(status_code=400, detail="Commission rule not found")
            
            # Calculate base commission
            revenue_amount = Decimal(str(revenue_data.get('amount', 0)))
            base_commission_rate = rule.base_rate
            base_commission = revenue_amount * base_commission_rate
            
            # Apply performance multiplier
            performance_metrics = await self._get_creator_performance(creator_id, calculation_period)
            performance_multiplier = self._calculate_performance_multiplier(performance_metrics, rule)
            
            adjusted_commission_rate = base_commission_rate * performance_multiplier
            commission_amount = revenue_amount * adjusted_commission_rate
            
            # Calculate performance bonus
            performance_bonus = await self._calculate_performance_bonus(
                creator_id, revenue_amount, performance_metrics, creator_tier
            )
            
            # Apply caps if specified
            if rule.max_cap and commission_amount > rule.max_cap:
                commission_amount = rule.max_cap
            
            total_payout = commission_amount + performance_bonus
            
            commission_id = f"comm_{creator_id}_{commission_type.value}_{int(datetime.now().timestamp())}"
            
            commission_data = CommissionData(
                commission_id=commission_id,
                creator_id=creator_id,
                revenue_amount=revenue_amount,
                commission_rate=adjusted_commission_rate,
                commission_amount=commission_amount,
                tier=creator_tier,
                commission_type=commission_type,
                calculation_period=calculation_period,
                performance_bonus=performance_bonus,
                total_payout=total_payout,
                currency=revenue_data.get('currency', 'USD')
            )
            
            # Store commission calculation
            await self._store_commission_calculation(commission_data)
            
            logger.info(f"Calculated commission for creator {creator_id}: {float(total_payout)} {commission_data.currency}")
            return commission_data
            
        except Exception as e:
            logger.error(f"Failed to calculate commission: {e}")
            raise HTTPException(status_code=500, detail="Commission calculation failed")

    async def _get_creator_tier(self, creator_id: str, as_of_date: datetime) -> CommissionTier:
        """Get creator's current tier based on performance"""
        try:
            async with self.db_pool.acquire() as conn:
                # Get creator's performance metrics
                performance = await conn.fetchrow("""
                    SELECT 
                        COALESCE(SUM(total_revenue), 0) as total_revenue,
                        COALESCE(SUM(content_sales_count), 0) as total_sales,
                        COALESCE(AVG(engagement_score), 0) as avg_engagement,
                        COALESCE(AVG(quality_score), 0) as avg_quality
                    FROM creator_performance_metrics 
                    WHERE creator_id = $1 
                    AND metric_period >= $2 - INTERVAL '12 months'
                    AND metric_period <= $3
                """, creator_id, as_of_date.date(), as_of_date.date())
                
                if not performance:
                    return CommissionTier.BRONZE
                
                total_revenue = float(performance['total_revenue'])
                total_sales = int(performance['total_sales'])
                
                # Determine tier based on performance
                if total_revenue >= 50000 and total_sales >= 500:
                    return CommissionTier.DIAMOND
                elif total_revenue >= 15000 and total_sales >= 150:
                    return CommissionTier.PLATINUM
                elif total_revenue >= 5000 and total_sales >= 50:
                    return CommissionTier.GOLD
                elif total_revenue >= 1000 and total_sales >= 10:
                    return CommissionTier.SILVER
                else:
                    return CommissionTier.BRONZE
                    
        except Exception as e:
            logger.error(f"Failed to get creator tier: {e}")
            return CommissionTier.BRONZE

    async def _get_creator_performance(self, creator_id: str, calculation_period: tuple[datetime, datetime]) -> Dict[str, Any]:
        """Get creator performance metrics for period"""
        try:
            async with self.db_pool.acquire() as conn:
                metrics = await conn.fetchrow("""
                    SELECT 
                        COALESCE(AVG(engagement_score), 0) as engagement_score,
                        COALESCE(AVG(customer_satisfaction), 0) as customer_satisfaction,
                        COALESCE(AVG(quality_score), 0) as quality_score,
                        COUNT(*) as active_months
                    FROM creator_performance_metrics 
                    WHERE creator_id = $1 
                    AND metric_period BETWEEN $2 AND $3
                """, creator_id, calculation_period[0].date(), calculation_period[1].date())
                
                return dict(metrics) if metrics else {
                    'engagement_score': 0,
                    'customer_satisfaction': 0,
                    'quality_score': 0,
                    'active_months': 0
                }
                
        except Exception as e:
            logger.error(f"Failed to get creator performance: {e}")
            return {}

    def _calculate_performance_multiplier(self, performance_metrics: Dict[str, Any], rule: CommissionRule) -> Decimal:
        """Calculate performance-based multiplier"""
        try:
            base_multiplier = rule.performance_multiplier
            
            # Engagement score impact (0-20% bonus)
            engagement_score = performance_metrics.get('engagement_score', 0)
            engagement_bonus = min(engagement_score / 100 * 0.2, 0.2)
            
            # Quality score impact (0-15% bonus)
            quality_score = performance_metrics.get('quality_score', 0)
            quality_bonus = min(quality_score / 100 * 0.15, 0.15)
            
            # Customer satisfaction impact (0-10% bonus)
            satisfaction_score = performance_metrics.get('customer_satisfaction', 0)
            satisfaction_bonus = min(satisfaction_score / 100 * 0.1, 0.1)
            
            total_multiplier = base_multiplier * (1 + engagement_bonus + quality_bonus + satisfaction_bonus)
            
            return Decimal(str(min(total_multiplier, 2.0)))  # Cap at 2x multiplier
            
        except Exception as e:
            logger.error(f"Failed to calculate performance multiplier: {e}")
            return Decimal('1.0')

    async def _calculate_performance_bonus(self, creator_id: str, revenue_amount: Decimal,
                                         performance_metrics: Dict[str, Any], tier: CommissionTier) -> Decimal:
        """Calculate additional performance bonus"""
        try:
            bonus = Decimal('0.00')
            
            # Tier-based bonus rates
            tier_bonus_rates = {
                CommissionTier.BRONZE: Decimal('0.01'),    # 1%
                CommissionTier.SILVER: Decimal('0.02'),    # 2%
                CommissionTier.GOLD: Decimal('0.03'),      # 3%
                CommissionTier.PLATINUM: Decimal('0.05'),  # 5%
                CommissionTier.DIAMOND: Decimal('0.08')    # 8%
            }
            
            base_bonus_rate = tier_bonus_rates.get(tier, Decimal('0.01'))
            
            # Exceptional performance bonus
            engagement_score = performance_metrics.get('engagement_score', 0)
            quality_score = performance_metrics.get('quality_score', 0)
            
            if engagement_score > 90 and quality_score > 90:
                # Excellence bonus for top performers
                bonus = revenue_amount * base_bonus_rate * Decimal('2.0')
            elif engagement_score > 80 and quality_score > 80:
                # High performance bonus
                bonus = revenue_amount * base_bonus_rate * Decimal('1.5')
            elif engagement_score > 70 or quality_score > 70:
                # Standard performance bonus
                bonus = revenue_amount * base_bonus_rate
            
            # Monthly revenue milestones
            if revenue_amount > Decimal('10000'):
                bonus += Decimal('500.00')  # $500 milestone bonus
            elif revenue_amount > Decimal('5000'):
                bonus += Decimal('200.00')  # $200 milestone bonus
            elif revenue_amount > Decimal('2000'):
                bonus += Decimal('50.00')   # $50 milestone bonus
            
            return bonus
            
        except Exception as e:
            logger.error(f"Failed to calculate performance bonus: {e}")
            return Decimal('0.00')

    async def _store_commission_calculation(self, commission_data: CommissionData) -> None:
        """Store commission calculation in database"""
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO commission_calculations 
                    (commission_id, creator_id, revenue_amount, commission_rate, commission_amount,
                     tier, commission_type, calculation_period_start, calculation_period_end,
                     performance_bonus, total_payout, currency)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                """,
                commission_data.commission_id,
                commission_data.creator_id,
                commission_data.revenue_amount,
                commission_data.commission_rate,
                commission_data.commission_amount,
                commission_data.tier.value,
                commission_data.commission_type.value,
                commission_data.calculation_period[0].date(),
                commission_data.calculation_period[1].date(),
                commission_data.performance_bonus,
                commission_data.total_payout,
                commission_data.currency
                )
        except Exception as e:
            logger.error(f"Failed to store commission calculation: {e}")

    async def calculate_bulk_commissions(self, calculation_date: datetime) -> Dict[str, List[CommissionData]]:
        """Calculate commissions for all creators for a specific period"""
        try:
            # Get all active creators
            async with self.db_pool.acquire() as conn:
                creators = await conn.fetch("""
                    SELECT DISTINCT creator_id 
                    FROM creator_performance_metrics 
                    WHERE metric_period = $1
                """, calculation_date.date())
                
                results = {
                    'successful': [],
                    'failed': []
                }
                
                period_start = calculation_date.replace(day=1)
                if calculation_date.month == 12:
                    period_end = calculation_date.replace(year=calculation_date.year + 1, month=1, day=1) - timedelta(days=1)
                else:
                    period_end = calculation_date.replace(month=calculation_date.month + 1, day=1) - timedelta(days=1)
                
                calculation_period = (period_start, period_end)
                
                for creator in creators:
                    creator_id = creator['creator_id']
                    
                    try:
                        # Get revenue data for creator
                        revenue_data = await self._get_creator_revenue_data(creator_id, calculation_period)
                        
                        # Calculate commissions for different types
                        for commission_type in CommissionType:
                            type_revenue = revenue_data.get(commission_type.value, 0)
                            if type_revenue > 0:
                                commission = await self.calculate_commission(
                                    creator_id, 
                                    {'amount': type_revenue, 'currency': 'USD'}, 
                                    commission_type, 
                                    calculation_period
                                )
                                results['successful'].append(commission)
                                
                    except Exception as e:
                        logger.error(f"Failed to calculate commission for creator {creator_id}: {e}")
                        results['failed'].append({
                            'creator_id': creator_id,
                            'error': str(e)
                        })
                
                return results
                
        except Exception as e:
            logger.error(f"Failed to calculate bulk commissions: {e}")
            return {'successful': [], 'failed': []}

    async def _get_creator_revenue_data(self, creator_id: str, period: tuple[datetime, datetime]) -> Dict[str, float]:
        """Get revenue data by type for creator"""
        try:
            async with self.db_pool.acquire() as conn:
                revenue_data = await conn.fetchrow("""
                    SELECT 
                        COALESCE(SUM(CASE WHEN revenue_type = 'content_sales' THEN amount ELSE 0 END), 0) as content_sales,
                        COALESCE(SUM(CASE WHEN revenue_type = 'licensing_revenue' THEN amount ELSE 0 END), 0) as licensing_revenue,
                        COALESCE(SUM(CASE WHEN revenue_type = 'subscription_revenue' THEN amount ELSE 0 END), 0) as subscription_revenue,
                        COALESCE(SUM(CASE WHEN revenue_type = 'advertising_revenue' THEN amount ELSE 0 END), 0) as advertising_revenue,
                        COALESCE(SUM(CASE WHEN revenue_type = 'collaboration_revenue' THEN amount ELSE 0 END), 0) as collaboration_revenue
                    FROM revenue_transactions 
                    WHERE creator_id = $1 
                    AND transaction_date BETWEEN $2 AND $3
                """, creator_id, period[0].date(), period[1].date())
                
                return dict(revenue_data) if revenue_data else {}
                
        except Exception as e:
            logger.error(f"Failed to get creator revenue data: {e}")
            return {}

    async def get_commission_dashboard_data(self, creator_id: str) -> Dict[str, Any]:
        """Get comprehensive commission dashboard data"""
        try:
            async with self.db_pool.acquire() as conn:
                # Commission summary
                summary = await conn.fetchrow("""
                    SELECT 
                        COUNT(*) as total_calculations,
                        COALESCE(SUM(total_payout), 0) as total_earned,
                        COALESCE(SUM(performance_bonus), 0) as total_bonuses,
                        COALESCE(AVG(commission_rate), 0) as avg_commission_rate,
                        MAX(tier) as current_tier
                    FROM commission_calculations 
                    WHERE creator_id = $1
                    AND created_at >= CURRENT_DATE - INTERVAL '12 months'
                """, creator_id)
                
                # Monthly commission trends
                monthly_trends = await conn.fetch("""
                    SELECT 
                        DATE_TRUNC('month', calculation_period_end) as month,
                        SUM(total_payout) as total_payout,
                        AVG(commission_rate) as avg_rate,
                        COUNT(*) as calculation_count
                    FROM commission_calculations 
                    WHERE creator_id = $1
                    AND calculation_period_end >= CURRENT_DATE - INTERVAL '12 months'
                    GROUP BY DATE_TRUNC('month', calculation_period_end)
                    ORDER BY month DESC
                """, creator_id)
                
                # Commission by type
                by_type = await conn.fetch("""
                    SELECT 
                        commission_type,
                        SUM(total_payout) as total_payout,
                        COUNT(*) as count
                    FROM commission_calculations 
                    WHERE creator_id = $1
                    AND calculation_period_end >= CURRENT_DATE - INTERVAL '3 months'
                    GROUP BY commission_type
                    ORDER BY total_payout DESC
                """, creator_id)
                
                return {
                    'creator_id': creator_id,
                    'summary': {
                        'total_calculations': int(summary['total_calculations']) if summary else 0,
                        'total_earned': float(summary['total_earned']) if summary else 0,
                        'total_bonuses': float(summary['total_bonuses']) if summary else 0,
                        'avg_commission_rate': float(summary['avg_commission_rate']) if summary else 0,
                        'current_tier': summary['current_tier'] if summary else 'bronze'
                    },
                    'monthly_trends': [
                        {
                            'month': trend['month'].strftime('%Y-%m'),
                            'total_payout': float(trend['total_payout']),
                            'avg_rate': float(trend['avg_rate']),
                            'calculation_count': int(trend['calculation_count'])
                        }
                        for trend in monthly_trends
                    ],
                    'commission_by_type': [
                        {
                            'commission_type': comm['commission_type'],
                            'total_payout': float(comm['total_payout']),
                            'count': int(comm['count'])
                        }
                        for comm in by_type
                    ],
                    'generated_at': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Failed to get commission dashboard data: {e}")
            raise HTTPException(status_code=500, detail="Commission dashboard data retrieval failed")
