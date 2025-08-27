"""
Royalty Distributor Engine - Automated royalty distribution system
==================================================================

Sophisticated royalty distribution engine for multi-stakeholder content
monetization with automated calculations and payments.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use prohibited.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import redis
import asyncpg
from decimal import Decimal
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class DistributionStatus(Enum):
    """Royalty distribution status"""
    PENDING = "pending"
    CALCULATED = "calculated"
    APPROVED = "approved"
    DISTRIBUTED = "distributed"
    FAILED = "failed"

class RoyaltyType(Enum):
    """Types of royalties"""
    CONTENT_SALES = "content_sales"
    STREAMING = "streaming"
    LICENSING = "licensing"
    COLLABORATION = "collaboration"
    PERFORMANCE = "performance"

@dataclass
class RoyaltyStakeholder:
    """Royalty stakeholder information"""
    stakeholder_id: str
    name: str
    role: str
    share_percentage: Decimal
    payment_method: str
    account_details: Dict[str, Any]

@dataclass
class RoyaltyData:
    """Royalty distribution data"""
    distribution_id: str
    content_id: str
    total_revenue: Decimal
    royalty_type: RoyaltyType
    distribution_period: tuple[datetime, datetime]
    stakeholders: List[RoyaltyStakeholder]
    status: DistributionStatus
    currency: str
    fees_deducted: Decimal
    net_distributable: Decimal

class RoyaltyDistributorEngine:
    """
    Advanced royalty distribution system with automated calculations,
    multi-stakeholder support, and compliance tracking.
    """
    
    def __init__(self, redis_client: redis.Redis, db_pool: asyncpg.Pool):
        self.redis = redis_client
        self.db_pool = db_pool
        
    async def initialize(self) -> None:
        """Initialize royalty distributor engine"""
        try:
            await self._setup_database_tables()
            await self._load_distribution_rules()
            logger.info("Royalty Distributor Engine initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Royalty Distributor Engine: {e}")
            raise

    async def _setup_database_tables(self) -> None:
        """Setup database tables for royalty distribution"""
        async with self.db_pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS content_stakeholders (
                    id SERIAL PRIMARY KEY,
                    content_id VARCHAR(255) NOT NULL,
                    stakeholder_id VARCHAR(255) NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    role VARCHAR(50) NOT NULL,
                    share_percentage DECIMAL(5,4) NOT NULL,
                    payment_method VARCHAR(50) NOT NULL,
                    account_details JSONB,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT NOW(),
                    UNIQUE(content_id, stakeholder_id)
                );
            """)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS royalty_distributions (
                    id SERIAL PRIMARY KEY,
                    distribution_id VARCHAR(100) UNIQUE NOT NULL,
                    content_id VARCHAR(255) NOT NULL,
                    total_revenue DECIMAL(15,2) NOT NULL,
                    royalty_type VARCHAR(30) NOT NULL,
                    distribution_period_start DATE NOT NULL,
                    distribution_period_end DATE NOT NULL,
                    status VARCHAR(20) NOT NULL,
                    currency VARCHAR(3) NOT NULL,
                    fees_deducted DECIMAL(15,2) DEFAULT 0,
                    net_distributable DECIMAL(15,2) NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW(),
                    distributed_at TIMESTAMP,
                    INDEX idx_distributions_content (content_id, distribution_period_end DESC),
                    INDEX idx_distributions_status (status, created_at)
                );
            """)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS royalty_payments (
                    id SERIAL PRIMARY KEY,
                    payment_id VARCHAR(100) UNIQUE NOT NULL,
                    distribution_id VARCHAR(100) REFERENCES royalty_distributions(distribution_id),
                    stakeholder_id VARCHAR(255) NOT NULL,
                    amount DECIMAL(15,2) NOT NULL,
                    share_percentage DECIMAL(5,4) NOT NULL,
                    payment_status VARCHAR(20) NOT NULL,
                    payment_method VARCHAR(50) NOT NULL,
                    transaction_reference VARCHAR(255),
                    created_at TIMESTAMP DEFAULT NOW(),
                    paid_at TIMESTAMP
                );
            """)

    async def _load_distribution_rules(self) -> None:
        """Load royalty distribution rules"""
        try:
            # Distribution fee rates by type
            fee_rates = {
                RoyaltyType.CONTENT_SALES: Decimal('0.05'),      # 5%
                RoyaltyType.STREAMING: Decimal('0.03'),          # 3%
                RoyaltyType.LICENSING: Decimal('0.08'),          # 8%
                RoyaltyType.COLLABORATION: Decimal('0.04'),      # 4%
                RoyaltyType.PERFORMANCE: Decimal('0.06')         # 6%
            }
            
            # Cache fee rates
            for royalty_type, rate in fee_rates.items():
                self.redis.setex(f"distribution_fee_{royalty_type.value}", 3600, str(rate))
                
        except Exception as e:
            logger.error(f"Failed to load distribution rules: {e}")

    async def calculate_royalty_distribution(self, content_id: str, total_revenue: Decimal,
                                           royalty_type: RoyaltyType,
                                           distribution_period: tuple[datetime, datetime]) -> RoyaltyData:
        """Calculate royalty distribution for content"""
        try:
            # Get content stakeholders
            stakeholders = await self._get_content_stakeholders(content_id)
            if not stakeholders:
                raise HTTPException(status_code=400, detail="No stakeholders found for content")
            
            # Validate total share percentage
            total_share = sum(s.share_percentage for s in stakeholders)
            if abs(total_share - Decimal('1.0')) > Decimal('0.001'):
                raise HTTPException(status_code=400, detail="Stakeholder shares must total 100%")
            
            # Calculate distribution fees
            fee_rate = await self._get_distribution_fee_rate(royalty_type)
            fees_deducted = total_revenue * fee_rate
            net_distributable = total_revenue - fees_deducted
            
            distribution_id = f"dist_{content_id}_{royalty_type.value}_{int(datetime.now().timestamp())}"
            
            royalty_data = RoyaltyData(
                distribution_id=distribution_id,
                content_id=content_id,
                total_revenue=total_revenue,
                royalty_type=royalty_type,
                distribution_period=distribution_period,
                stakeholders=stakeholders,
                status=DistributionStatus.CALCULATED,
                currency='USD',
                fees_deducted=fees_deducted,
                net_distributable=net_distributable
            )
            
            # Store distribution record
            await self._store_distribution(royalty_data)
            
            # Calculate individual payments
            await self._calculate_stakeholder_payments(royalty_data)
            
            return royalty_data
            
        except Exception as e:
            logger.error(f"Failed to calculate royalty distribution: {e}")
            raise HTTPException(status_code=500, detail="Royalty distribution calculation failed")

    async def _get_content_stakeholders(self, content_id: str) -> List[RoyaltyStakeholder]:
        """Get stakeholders for content"""
        try:
            async with self.db_pool.acquire() as conn:
                stakeholder_rows = await conn.fetch("""
                    SELECT stakeholder_id, name, role, share_percentage, payment_method, account_details
                    FROM content_stakeholders 
                    WHERE content_id = $1 AND is_active = TRUE
                    ORDER BY share_percentage DESC
                """, content_id)
                
                return [
                    RoyaltyStakeholder(
                        stakeholder_id=row['stakeholder_id'],
                        name=row['name'],
                        role=row['role'],
                        share_percentage=row['share_percentage'],
                        payment_method=row['payment_method'],
                        account_details=row['account_details'] or {}
                    )
                    for row in stakeholder_rows
                ]
                
        except Exception as e:
            logger.error(f"Failed to get content stakeholders: {e}")
            return []

    async def _get_distribution_fee_rate(self, royalty_type: RoyaltyType) -> Decimal:
        """Get distribution fee rate for royalty type"""
        try:
            cached_rate = self.redis.get(f"distribution_fee_{royalty_type.value}")
            if cached_rate:
                return Decimal(cached_rate.decode())
            
            # Default fee rate
            return Decimal('0.05')  # 5%
            
        except Exception as e:
            logger.error(f"Failed to get distribution fee rate: {e}")
            return Decimal('0.05')

    async def _store_distribution(self, royalty_data: RoyaltyData) -> None:
        """Store royalty distribution record"""
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO royalty_distributions 
                    (distribution_id, content_id, total_revenue, royalty_type,
                     distribution_period_start, distribution_period_end, status,
                     currency, fees_deducted, net_distributable)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                """,
                royalty_data.distribution_id,
                royalty_data.content_id,
                royalty_data.total_revenue,
                royalty_data.royalty_type.value,
                royalty_data.distribution_period[0].date(),
                royalty_data.distribution_period[1].date(),
                royalty_data.status.value,
                royalty_data.currency,
                royalty_data.fees_deducted,
                royalty_data.net_distributable
                )
        except Exception as e:
            logger.error(f"Failed to store distribution: {e}")

    async def _calculate_stakeholder_payments(self, royalty_data: RoyaltyData) -> None:
        """Calculate individual stakeholder payments"""
        try:
            async with self.db_pool.acquire() as conn:
                for stakeholder in royalty_data.stakeholders:
                    payment_amount = royalty_data.net_distributable * stakeholder.share_percentage
                    payment_id = f"pay_{royalty_data.distribution_id}_{stakeholder.stakeholder_id}"
                    
                    await conn.execute("""
                        INSERT INTO royalty_payments 
                        (payment_id, distribution_id, stakeholder_id, amount, 
                         share_percentage, payment_status, payment_method)
                        VALUES ($1, $2, $3, $4, $5, 'pending', $6)
                    """,
                    payment_id,
                    royalty_data.distribution_id,
                    stakeholder.stakeholder_id,
                    payment_amount,
                    stakeholder.share_percentage,
                    stakeholder.payment_method
                    )
                    
        except Exception as e:
            logger.error(f"Failed to calculate stakeholder payments: {e}")

    async def process_distribution_payments(self, distribution_id: str) -> Dict[str, Any]:
        """Process payments for a royalty distribution"""
        try:
            # Get pending payments
            async with self.db_pool.acquire() as conn:
                payments = await conn.fetch("""
                    SELECT payment_id, stakeholder_id, amount, payment_method
                    FROM royalty_payments 
                    WHERE distribution_id = $1 AND payment_status = 'pending'
                """, distribution_id)
                
                results = {'successful': 0, 'failed': 0, 'details': []}
                
                for payment in payments:
                    try:
                        # Process payment based on method
                        payment_result = await self._process_stakeholder_payment(
                            payment['payment_id'],
                            payment['stakeholder_id'],
                            payment['amount'],
                            payment['payment_method']
                        )
                        
                        if payment_result['success']:
                            await conn.execute("""
                                UPDATE royalty_payments 
                                SET payment_status = 'completed', 
                                    transaction_reference = $1,
                                    paid_at = NOW()
                                WHERE payment_id = $2
                            """, payment_result['transaction_id'], payment['payment_id'])
                            
                            results['successful'] += 1
                        else:
                            await conn.execute("""
                                UPDATE royalty_payments 
                                SET payment_status = 'failed'
                                WHERE payment_id = $1
                            """, payment['payment_id'])
                            
                            results['failed'] += 1
                            results['details'].append({
                                'payment_id': payment['payment_id'],
                                'error': payment_result['error']
                            })
                            
                    except Exception as e:
                        results['failed'] += 1
                        results['details'].append({
                            'payment_id': payment['payment_id'],
                            'error': str(e)
                        })
                
                # Update distribution status
                if results['failed'] == 0:
                    await conn.execute("""
                        UPDATE royalty_distributions 
                        SET status = 'distributed', distributed_at = NOW()
                        WHERE distribution_id = $1
                    """, distribution_id)
                else:
                    await conn.execute("""
                        UPDATE royalty_distributions 
                        SET status = 'failed'
                        WHERE distribution_id = $1
                    """, distribution_id)
                
                return results
                
        except Exception as e:
            logger.error(f"Failed to process distribution payments: {e}")
            return {'successful': 0, 'failed': 0, 'details': []}

    async def _process_stakeholder_payment(self, payment_id: str, stakeholder_id: str,
                                         amount: Decimal, payment_method: str) -> Dict[str, Any]:
        """Process individual stakeholder payment"""
        try:
            # Get stakeholder payment details
            stakeholder_details = await self._get_stakeholder_payment_details(stakeholder_id)
            
            if payment_method == "bank_transfer":
                return await self._process_bank_transfer(amount, stakeholder_details)
            elif payment_method == "paypal":
                return await self._process_paypal_payment(amount, stakeholder_details)
            elif payment_method == "stripe":
                return await self._process_stripe_transfer(amount, stakeholder_details)
            else:
                return {
                    'success': False,
                    'error': f"Unsupported payment method: {payment_method}"
                }
                
        except Exception as e:
            logger.error(f"Failed to process stakeholder payment: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def _get_stakeholder_payment_details(self, stakeholder_id: str) -> Dict[str, Any]:
        """Get stakeholder payment details"""
        try:
            async with self.db_pool.acquire() as conn:
                details = await conn.fetchrow("""
                    SELECT account_details FROM content_stakeholders 
                    WHERE stakeholder_id = $1
                """, stakeholder_id)
                
                return details['account_details'] if details else {}
                
        except Exception as e:
            logger.error(f"Failed to get stakeholder payment details: {e}")
            return {}

    async def _process_bank_transfer(self, amount: Decimal, details: Dict[str, Any]) -> Dict[str, Any]:
        """Process bank transfer payment"""
        try:
            # Mock bank transfer processing
            transaction_id = f"bank_{int(datetime.now().timestamp())}"
            
            return {
                'success': True,
                'transaction_id': transaction_id,
                'method': 'bank_transfer'
            }
            
        except Exception as e:
            logger.error(f"Bank transfer failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def _process_paypal_payment(self, amount: Decimal, details: Dict[str, Any]) -> Dict[str, Any]:
        """Process PayPal payment"""
        try:
            transaction_id = f"paypal_{int(datetime.now().timestamp())}"
            
            return {
                'success': True,
                'transaction_id': transaction_id,
                'method': 'paypal'
            }
            
        except Exception as e:
            logger.error(f"PayPal payment failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def _process_stripe_transfer(self, amount: Decimal, details: Dict[str, Any]) -> Dict[str, Any]:
        """Process Stripe transfer"""
        try:
            transaction_id = f"stripe_{int(datetime.now().timestamp())}"
            
            return {
                'success': True,
                'transaction_id': transaction_id,
                'method': 'stripe'
            }
            
        except Exception as e:
            logger.error(f"Stripe transfer failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def add_content_stakeholder(self, content_id: str, stakeholder_data: Dict[str, Any]) -> bool:
        """Add stakeholder to content"""
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO content_stakeholders 
                    (content_id, stakeholder_id, name, role, share_percentage, 
                     payment_method, account_details)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                    ON CONFLICT (content_id, stakeholder_id) 
                    DO UPDATE SET 
                        share_percentage = EXCLUDED.share_percentage,
                        payment_method = EXCLUDED.payment_method,
                        account_details = EXCLUDED.account_details
                """,
                content_id,
                stakeholder_data['stakeholder_id'],
                stakeholder_data['name'],
                stakeholder_data['role'],
                Decimal(str(stakeholder_data['share_percentage'])),
                stakeholder_data['payment_method'],
                stakeholder_data.get('account_details', {})
                )
                
                return True
                
        except Exception as e:
            logger.error(f"Failed to add content stakeholder: {e}")
            return False

    async def get_royalty_dashboard_data(self, stakeholder_id: str) -> Dict[str, Any]:
        """Get royalty dashboard data for stakeholder"""
        try:
            async with self.db_pool.acquire() as conn:
                # Payment summary
                summary = await conn.fetchrow("""
                    SELECT 
                        COUNT(*) as total_payments,
                        COALESCE(SUM(amount), 0) as total_earned,
                        COUNT(CASE WHEN payment_status = 'completed' THEN 1 END) as completed_payments,
                        COUNT(CASE WHEN payment_status = 'pending' THEN 1 END) as pending_payments
                    FROM royalty_payments 
                    WHERE stakeholder_id = $1
                    AND created_at >= CURRENT_DATE - INTERVAL '12 months'
                """, stakeholder_id)
                
                # Recent payments
                recent_payments = await conn.fetch("""
                    SELECT 
                        rp.payment_id,
                        rp.amount,
                        rp.payment_status,
                        rp.created_at,
                        rd.content_id,
                        rd.royalty_type
                    FROM royalty_payments rp
                    JOIN royalty_distributions rd ON rp.distribution_id = rd.distribution_id
                    WHERE rp.stakeholder_id = $1
                    ORDER BY rp.created_at DESC
                    LIMIT 10
                """, stakeholder_id)
                
                # Monthly earnings
                monthly_earnings = await conn.fetch("""
                    SELECT 
                        DATE_TRUNC('month', created_at) as month,
                        SUM(amount) as earnings,
                        COUNT(*) as payment_count
                    FROM royalty_payments 
                    WHERE stakeholder_id = $1
                    AND payment_status = 'completed'
                    AND created_at >= CURRENT_DATE - INTERVAL '12 months'
                    GROUP BY DATE_TRUNC('month', created_at)
                    ORDER BY month DESC
                """, stakeholder_id)
                
                return {
                    'stakeholder_id': stakeholder_id,
                    'summary': {
                        'total_payments': int(summary['total_payments']) if summary else 0,
                        'total_earned': float(summary['total_earned']) if summary else 0,
                        'completed_payments': int(summary['completed_payments']) if summary else 0,
                        'pending_payments': int(summary['pending_payments']) if summary else 0
                    },
                    'recent_payments': [
                        {
                            'payment_id': pay['payment_id'],
                            'amount': float(pay['amount']),
                            'status': pay['payment_status'],
                            'content_id': pay['content_id'],
                            'royalty_type': pay['royalty_type'],
                            'created_at': pay['created_at'].isoformat()
                        }
                        for pay in recent_payments
                    ],
                    'monthly_earnings': [
                        {
                            'month': earning['month'].strftime('%Y-%m'),
                            'earnings': float(earning['earnings']),
                            'payment_count': int(earning['payment_count'])
                        }
                        for earning in monthly_earnings
                    ],
                    'generated_at': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Failed to get royalty dashboard data: {e}")
            raise HTTPException(status_code=500, detail="Royalty dashboard data retrieval failed")
