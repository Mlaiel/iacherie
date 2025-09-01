"""Subscription Billing Engine - Automated subscription billing system
===================================================================

Advanced subscription billing management with flexible plans, proration,
dunning management, and revenue recognition for SaaS creators.

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

class SubscriptionPlan(Enum):
    """
Subscription plan types"""

    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"

class BillingCycle(Enum):
    """Billing cycle options"""

    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUALLY = "annually"
    LIFETIME = "lifetime"

class SubscriptionStatus(Enum):
    """Subscription status"""

    ACTIVE = "active"
    TRIAL = "trial"
    PAST_DUE = "past_due"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    SUSPENDED = "suspended"

@dataclass
class SubscriptionData:
    """Subscription data structure"""
    subscription_id: str
    customer_id: str
    plan: SubscriptionPlan
    billing_cycle: BillingCycle
    status: SubscriptionStatus
    current_period_start: datetime
    current_period_end: datetime
    amount: Decimal
    currency: str
    trial_end: Optional[datetime]
    cancelled_at: Optional[datetime]

class SubscriptionBillingEngine:
    """
    Advanced subscription billing system with automated charging,
    proration calculations, and dunning management.
    """
    
    def __init__(self, redis_client: redis.Redis, db_pool: asyncpg.Pool):
        self.redis = redis_client
        self.db_pool = db_pool
        
    async def initialize(self) -> None:
        """
Initialize subscription billing engine"""
        try:
            await self._setup_database_tables()
            await self._load_subscription_plans()
            logger.info("Subscription Billing Engine initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Subscription Billing Engine: {e}")
            raise

    async def _setup_database_tables(self) -> None:
        """Setup database tables for subscription billing"""
        async with self.db_pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS subscription_plans (
                    id SERIAL PRIMARY KEY,
                    plan_name VARCHAR(50) NOT NULL,
                    monthly_price DECIMAL(10,2) NOT NULL,
                    quarterly_price DECIMAL(10,2),
                    annual_price DECIMAL(10,2),
                    features JSONB NOT NULL,
                    limits JSONB NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS subscriptions (
                    id SERIAL PRIMARY KEY,
                    subscription_id VARCHAR(100) UNIQUE NOT NULL,
                    customer_id VARCHAR(255) NOT NULL,
                    plan VARCHAR(50) NOT NULL,
                    billing_cycle VARCHAR(20) NOT NULL,
                    status VARCHAR(20) NOT NULL,
                    current_period_start DATE NOT NULL,
                    current_period_end DATE NOT NULL,
                    amount DECIMAL(10,2) NOT NULL,
                    currency VARCHAR(3) NOT NULL,
                    trial_end DATE,
                    cancelled_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW(),
                    INDEX idx_subscriptions_customer (customer_id, status),
                    INDEX idx_subscriptions_billing (current_period_end, status)
                );
            """)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS subscription_invoices (
                    id SERIAL PRIMARY KEY,
                    invoice_id VARCHAR(100) UNIQUE NOT NULL,
                    subscription_id VARCHAR(100) REFERENCES subscriptions(subscription_id),
                    amount DECIMAL(10,2) NOT NULL,
                    period_start DATE NOT NULL,
                    period_end DATE NOT NULL,
                    status VARCHAR(20) NOT NULL,
                    due_date DATE NOT NULL,
                    paid_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """)

    async def _load_subscription_plans(self) -> None:
        """
Load subscription plans configuration"""
        try:
            plans_config = {
                SubscriptionPlan.STARTER: {
                    'monthly_price': Decimal('29.99'),
                    'quarterly_price': Decimal('79.99'),
                    'annual_price': Decimal('299.99'),
                    'features': ['Basic Analytics', 'Content Protection', 'Email Support'],
                    'limits': {'storage_gb': 50, 'api_calls': 10000, 'projects': 3}
                },
                SubscriptionPlan.PROFESSIONAL: {
                    'monthly_price': Decimal('99.99'),
                    'quarterly_price': Decimal('269.99'),
                    'annual_price': Decimal('999.99'),
                    'features': ['Advanced Analytics', 'AI Tools', 'Priority Support', 'Custom Branding'],
                    'limits': {'storage_gb': 500, 'api_calls': 100000, 'projects': 25}
                },
                SubscriptionPlan.ENTERPRISE: {
                    'monthly_price': Decimal('299.99'),
                    'quarterly_price': Decimal('799.99'),
                    'annual_price': Decimal('2999.99'),
                    'features': ['Enterprise Analytics', 'White Label', 'Dedicated Support', 'Custom Integrations'],
                    'limits': {'storage_gb': 5000, 'api_calls': 1000000, 'projects': 100}
                }
            }
            
            # Cache plans in Redis
            for plan, config in plans_config.items():
                self.redis.hmset(f"subscription_plan_{plan.value}", {
                    'monthly_price': str(config['monthly_price']),
                    'quarterly_price': str(config['quarterly_price']),
                    'annual_price': str(config['annual_price'])
                })
                
        except Exception as e:
            logger.error(f"Failed to load subscription plans: {e}")

    async def create_subscription(self, customer_id: str, plan: SubscriptionPlan,
                                billing_cycle: BillingCycle, trial_days: int = 0) -> SubscriptionData:
        """Create new subscription"""
        try:
            subscription_id = f"sub_{customer_id}_{int(datetime.now().timestamp())}"
            
            # Get plan pricing
            amount = await self._get_plan_price(plan, billing_cycle)
            
            # Calculate billing periods
            now = datetime.now()
            if trial_days > 0:
                trial_end = now + timedelta(days=trial_days)
                period_start = trial_end
                status = SubscriptionStatus.TRIAL
            else:
                trial_end = None
                period_start = now
                status = SubscriptionStatus.ACTIVE
            
            period_end = self._calculate_period_end(period_start, billing_cycle)
            
            subscription = SubscriptionData(
                subscription_id=subscription_id,
                customer_id=customer_id,
                plan=plan,
                billing_cycle=billing_cycle,
                status=status,
                current_period_start=period_start,
                current_period_end=period_end,
                amount=amount,
                currency='USD',
                trial_end=trial_end,
                cancelled_at=None
            )
            
            await self._store_subscription(subscription)
            
            # Create initial invoice if not trial
            if trial_days == 0:
                await self._create_subscription_invoice(subscription)
            
            return subscription
            
        except Exception as e:
            logger.error(f"Failed to create subscription: {e}")
            raise HTTPException(status_code=500, detail="Subscription creation failed")

    async def _get_plan_price(self, plan: SubscriptionPlan, billing_cycle: BillingCycle) -> Decimal:
        """Get plan price for billing cycle"""
        try:
            if billing_cycle == BillingCycle.MONTHLY:
                price_key = 'monthly_price'
            elif billing_cycle == BillingCycle.QUARTERLY:
                price_key = 'quarterly_price'
            elif billing_cycle == BillingCycle.ANNUALLY:
                price_key = 'annual_price'
            else:
                price_key = 'monthly_price'
            
            cached_price = self.redis.hget(f"subscription_plan_{plan.value}", price_key)
            if cached_price:
                return Decimal(cached_price.decode())
            
            # Fallback pricing
            base_prices = {
                SubscriptionPlan.STARTER: Decimal('29.99'),
                SubscriptionPlan.PROFESSIONAL: Decimal('99.99'),
                SubscriptionPlan.ENTERPRISE: Decimal('299.99')
            }
            
            return base_prices.get(plan, Decimal('29.99'))
            
        except Exception as e:
            logger.error(f"Failed to get plan price: {e}")
            return Decimal('29.99')

    def _calculate_period_end(self, start_date: datetime, billing_cycle: BillingCycle) -> datetime:
        """Calculate billing period end date"""
        if billing_cycle == BillingCycle.MONTHLY:
            return start_date + timedelta(days=30)
        elif billing_cycle == BillingCycle.QUARTERLY:
            return start_date + timedelta(days=90)
        elif billing_cycle == BillingCycle.ANNUALLY:
            return start_date + timedelta(days=365)
        else:
            return start_date + timedelta(days=30)

    async def _store_subscription(self, subscription: SubscriptionData) -> None:
        """
Store subscription in database"""
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO subscriptions 
                    (subscription_id, customer_id, plan, billing_cycle, status,
                     current_period_start, current_period_end, amount, currency, trial_end)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                """,
                subscription.subscription_id,
                subscription.customer_id,
                subscription.plan.value,
                subscription.billing_cycle.value,
                subscription.status.value,
                subscription.current_period_start.date(),
                subscription.current_period_end.date(),
                subscription.amount,
                subscription.currency,
                subscription.trial_end.date() if subscription.trial_end else None
                )
        except Exception as e:
            logger.error(f"Failed to store subscription: {e}")

    async def _create_subscription_invoice(self, subscription: SubscriptionData) -> None:
        """Create subscription invoice"""
        try:
            invoice_id = f"inv_{subscription.subscription_id}_{int(datetime.now().timestamp())}"
            
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO subscription_invoices 
                    (invoice_id, subscription_id, amount, period_start, period_end, status, due_date)
                    VALUES ($1, $2, $3, $4, $5, 'pending', $6)
                """,
                invoice_id,
                subscription.subscription_id,
                subscription.amount,
                subscription.current_period_start.date(),
                subscription.current_period_end.date(),
                datetime.now().date()
                )
        except Exception as e:
            logger.error(f"Failed to create subscription invoice: {e}")

    async def process_subscription_renewals(self) -> Dict[str, Any]:
        """Process subscription renewals for due subscriptions"""
        try:
            async with self.db_pool.acquire() as conn:
                # Get subscriptions due for renewal
                due_subscriptions = await conn.fetch("""
                    SELECT subscription_id FROM subscriptions 
                    WHERE status = 'active' 
                    AND current_period_end <= CURRENT_DATE
                """)
                
                processed = {'success': 0, 'failed': 0, 'details': []}
                
                for sub_row in due_subscriptions:
                    try:
                        subscription = await self._get_subscription(sub_row['subscription_id'])
                        if subscription:
                            await self._renew_subscription(subscription)
                            processed['success'] += 1
                    except Exception as e:
                        processed['failed'] += 1
                        processed['details'].append({
                            'subscription_id': sub_row['subscription_id'],
                            'error': str(e)
                        })
                
                return processed
                
        except Exception as e:
            logger.error(f"Failed to process subscription renewals: {e}")
            return {'success': 0, 'failed': 0, 'details': []}

    async def _get_subscription(self, subscription_id: str) -> Optional[SubscriptionData]:
        """Get subscription by ID"""
        try:
            async with self.db_pool.acquire() as conn:
                sub_row = await conn.fetchrow("""
                    SELECT * FROM subscriptions WHERE subscription_id = $1
                """, subscription_id)
                
                if not sub_row:
                    return None
                
                return SubscriptionData(
                    subscription_id=sub_row['subscription_id'],
                    customer_id=sub_row['customer_id'],
                    plan=SubscriptionPlan(sub_row['plan']),
                    billing_cycle=BillingCycle(sub_row['billing_cycle']),
                    status=SubscriptionStatus(sub_row['status']),
                    current_period_start=datetime.combine(sub_row['current_period_start'], datetime.min.time()),
                    current_period_end=datetime.combine(sub_row['current_period_end'], datetime.min.time()),
                    amount=sub_row['amount'],
                    currency=sub_row['currency'],
                    trial_end=datetime.combine(sub_row['trial_end'], datetime.min.time()) if sub_row['trial_end'] else None,
                    cancelled_at=sub_row['cancelled_at']
                )
                
        except Exception as e:
            logger.error(f"Failed to get subscription: {e}")
            return None

    async def _renew_subscription(self, subscription: SubscriptionData) -> None:
        """Renew subscription for next period"""
        try:
            # Calculate new period
            new_period_start = subscription.current_period_end
            new_period_end = self._calculate_period_end(new_period_start, subscription.billing_cycle)
            
            # Update subscription
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    UPDATE subscriptions 
                    SET current_period_start = $1, current_period_end = $2, updated_at = NOW()
                    WHERE subscription_id = $3
                """,
                new_period_start.date(),
                new_period_end.date(),
                subscription.subscription_id
                )
            
            # Create renewal invoice
            subscription.current_period_start = new_period_start
            subscription.current_period_end = new_period_end
            await self._create_subscription_invoice(subscription)
            
        except Exception as e:
            logger.error(f"Failed to renew subscription: {e}")

    async def cancel_subscription(self, subscription_id: str, immediate: bool = False) -> bool:
        """Cancel subscription"""
        try:
            async with self.db_pool.acquire() as conn:
                if immediate:
                    # Cancel immediately
                    await conn.execute("""
                        UPDATE subscriptions 
                        SET status = 'cancelled', cancelled_at = NOW(), updated_at = NOW()
                        WHERE subscription_id = $1
                    """, subscription_id)
                else:
                    # Cancel at period end
                    await conn.execute("""
                        UPDATE subscriptions 
                        SET cancelled_at = NOW(), updated_at = NOW()
                        WHERE subscription_id = $1
                    """, subscription_id)
                
                return True
                
        except Exception as e:
            logger.error(f"Failed to cancel subscription: {e}")
            return False

    async def get_subscription_dashboard_data(self, customer_id: str) -> Dict[str, Any]:
        """Get subscription dashboard data"""
        try:
            async with self.db_pool.acquire() as conn:
                # Current subscriptions
                current_subs = await conn.fetch("""
                    SELECT subscription_id, plan, status, current_period_end, amount
                    FROM subscriptions 
                    WHERE customer_id = $1 
                    AND status IN ('active', 'trial', 'past_due')
                """, customer_id)
                
                # Subscription history
                history = await conn.fetch("""
                    SELECT subscription_id, plan, status, created_at, cancelled_at
                    FROM subscriptions 
                    WHERE customer_id = $1
                    ORDER BY created_at DESC
                    LIMIT 10
                """, customer_id)
                
                # Usage summary
                usage = await conn.fetchrow("""
                    SELECT 
                        COUNT(*) as total_subscriptions,
                        COALESCE(SUM(CASE WHEN status = 'active' THEN amount ELSE 0 END), 0) as monthly_cost
                    FROM subscriptions 
                    WHERE customer_id = $1
                """, customer_id)
                
                return {
                    'customer_id': customer_id,
                    'current_subscriptions': [
                        {
                            'subscription_id': sub['subscription_id'],
                            'plan': sub['plan'],
                            'status': sub['status'],
                            'next_billing_date': sub['current_period_end'].isoformat(),
                            'amount': float(sub['amount'])
                        }
                        for sub in current_subs
                    ],
                    'subscription_history': [
                        {
                            'subscription_id': sub['subscription_id'],
                            'plan': sub['plan'],
                            'status': sub['status'],
                            'created_at': sub['created_at'].isoformat(),
                            'cancelled_at': sub['cancelled_at'].isoformat() if sub['cancelled_at'] else None
                        }
                        for sub in history
                    ],
                    'usage_summary': {
                        'total_subscriptions': int(usage['total_subscriptions']) if usage else 0,
                        'monthly_cost': float(usage['monthly_cost']) if usage else 0
                    },
                    'generated_at': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Failed to get subscription dashboard data: {e}")
            raise HTTPException(status_code=500, detail="Subscription dashboard data retrieval failed")
