"""
Revenue Stream Tracker for IA Influencer Agent Platform
======================================================

Advanced revenue streaming and analytics system for real-time monetization
tracking, payment processing, and revenue optimization across platforms.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum
from decimal import Decimal
import json

from pydantic import BaseModel, Field
from redis.asyncio import Redis

from ...core.config import get_settings
from ...utils.logging import get_logger
from ...models.revenue import RevenueModel, PaymentModel
from .manager import StreamEvent

logger = get_logger(__name__)
settings = get_settings()


class RevenueSource(str, Enum):
    """Revenue source types"""
    STREAMING = "streaming"
    LICENSING = "licensing"
    SPONSORSHIP = "sponsorship"
    MERCHANDISE = "merchandise"
    TIPS = "tips"
    SUBSCRIPTION = "subscription"
    ADVERTISING = "advertising"
    ROYALTIES = "royalties"


class PaymentStatus(str, Enum):
    """Payment processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    DISPUTED = "disputed"


class CurrencyCode(str, Enum):
    """Supported currency codes"""
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    JPY = "JPY"
    CAD = "CAD"
    AUD = "AUD"
    CHF = "CHF"


@dataclass
class RevenueStream:
    """Revenue stream configuration"""
    id: str
    user_id: str
    content_id: Optional[str]
    source: RevenueSource
    platform: str
    currency: CurrencyCode
    rate_per_unit: Decimal
    minimum_payout: Decimal = Decimal("10.00")
    active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RevenueEvent:
    """Revenue generation event"""
    id: str
    stream_id: str
    user_id: str
    amount: Decimal
    currency: CurrencyCode
    source: RevenueSource
    platform: str
    reference_id: Optional[str]
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


class RevenueAnalytics(BaseModel):
    """Revenue analytics data"""
    user_id: str = Field(description="User identifier")
    total_revenue: Decimal = Field(default=Decimal("0"), description="Total revenue earned")
    pending_revenue: Decimal = Field(default=Decimal("0"), description="Pending revenue")
    paid_revenue: Decimal = Field(default=Decimal("0"), description="Already paid revenue")
    revenue_by_source: Dict[str, Decimal] = Field(default_factory=dict, description="Revenue by source")
    revenue_by_platform: Dict[str, Decimal] = Field(default_factory=dict, description="Revenue by platform")
    revenue_by_currency: Dict[str, Decimal] = Field(default_factory=dict, description="Revenue by currency")
    last_30_days: Decimal = Field(default=Decimal("0"), description="Revenue in last 30 days")
    growth_rate: float = Field(default=0.0, description="Revenue growth rate percentage")
    avg_daily_revenue: Decimal = Field(default=Decimal("0"), description="Average daily revenue")


class PaymentInfo(BaseModel):
    """Payment processing information"""
    payment_id: str = Field(description="Payment identifier")
    user_id: str = Field(description="User identifier")
    amount: Decimal = Field(description="Payment amount")
    currency: CurrencyCode = Field(description="Payment currency")
    status: PaymentStatus = Field(description="Payment status")
    method: str = Field(description="Payment method")
    reference: Optional[str] = Field(default=None, description="External reference")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    processed_at: Optional[datetime] = Field(default=None, description="Processing timestamp")
    fee_amount: Optional[Decimal] = Field(default=None, description="Processing fee")
    net_amount: Optional[Decimal] = Field(default=None, description="Net amount after fees")


class RevenueStreamer:
    """
    Enterprise-grade revenue streaming system for real-time monetization
    tracking, payment processing, and revenue analytics.
    """
    
    def __init__(self):
        self.redis: Optional[Redis] = None
        self.revenue_streams: Dict[str, RevenueStream] = {}
        self.user_analytics: Dict[str, RevenueAnalytics] = {}
        self.pending_payments: Dict[str, PaymentInfo] = {}
        self.exchange_rates: Dict[str, Dict[str, float]] = {}
        self._shutdown_event = asyncio.Event()
        
    async def initialize(self) -> None:
        """Initialize revenue streamer with Redis and payment processors"""
        try:
            from ...core.cache import get_redis_client
            self.redis = await get_redis_client()
            
            # Load existing revenue streams
            await self._load_revenue_streams()
            
            # Initialize exchange rates
            await self._update_exchange_rates()
            
            # Start background tasks
            asyncio.create_task(self._revenue_processor())
            asyncio.create_task(self._payment_processor())
            asyncio.create_task(self._analytics_updater())
            asyncio.create_task(self._exchange_rate_updater())
            
            logger.info("RevenueStreamer initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize RevenueStreamer: {e}")
            raise
            
    async def create_revenue_stream(
        self,
        user_id: str,
        source: RevenueSource,
        platform: str,
        currency: CurrencyCode,
        rate_per_unit: Decimal,
        content_id: Optional[str] = None,
        minimum_payout: Optional[Decimal] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create new revenue stream
        
        Args:
            user_id: User identifier
            source: Revenue source type
            platform: Platform name
            currency: Currency code
            rate_per_unit: Revenue rate per unit
            content_id: Optional content identifier
            minimum_payout: Minimum payout threshold
            metadata: Optional stream metadata
            
        Returns:
            Revenue stream identifier
        """
        try:
            from uuid import uuid4
            stream_id = str(uuid4())
            
            revenue_stream = RevenueStream(
                id=stream_id,
                user_id=user_id,
                content_id=content_id,
                source=source,
                platform=platform,
                currency=currency,
                rate_per_unit=rate_per_unit,
                minimum_payout=minimum_payout or Decimal("10.00"),
                metadata=metadata or {}
            )
            
            self.revenue_streams[stream_id] = revenue_stream
            
            # Store in Redis
            await self.redis.hset(
                f"revenue_stream:{stream_id}",
                mapping={
                    "user_id": user_id,
                    "source": source.value,
                    "platform": platform,
                    "currency": currency.value,
                    "rate_per_unit": str(rate_per_unit),
                    "minimum_payout": str(revenue_stream.minimum_payout),
                    "active": "true",
                    "created_at": revenue_stream.created_at.isoformat(),
                    "metadata": json.dumps(metadata or {})
                }
            )
            
            logger.info(f"Created revenue stream {stream_id} for user {user_id}")
            return stream_id
            
        except Exception as e:
            logger.error(f"Failed to create revenue stream: {e}")
            raise
            
    async def track_revenue_event(
        self,
        stream_id: str,
        amount: Decimal,
        reference_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Track revenue generation event
        
        Args:
            stream_id: Revenue stream identifier
            amount: Revenue amount
            reference_id: External reference identifier
            metadata: Optional event metadata
            
        Returns:
            Success status
        """
        try:
            if stream_id not in self.revenue_streams:
                logger.warning(f"Revenue stream {stream_id} not found")
                return False
                
            stream = self.revenue_streams[stream_id]
            
            if not stream.active:
                logger.warning(f"Revenue stream {stream_id} is inactive")
                return False
                
            from uuid import uuid4
            event = RevenueEvent(
                id=str(uuid4()),
                stream_id=stream_id,
                user_id=stream.user_id,
                amount=amount,
                currency=stream.currency,
                source=stream.source,
                platform=stream.platform,
                reference_id=reference_id,
                timestamp=datetime.now(timezone.utc),
                metadata=metadata or {}
            )
            
            # Store event in Redis
            await self.redis.xadd(
                f"revenue_events:{stream.user_id}",
                fields={
                    "event_id": event.id,
                    "stream_id": stream_id,
                    "amount": str(amount),
                    "currency": stream.currency.value,
                    "source": stream.source.value,
                    "platform": stream.platform,
                    "reference_id": reference_id or "",
                    "timestamp": event.timestamp.isoformat(),
                    "metadata": json.dumps(metadata or {})
                }
            )
            
            # Update user analytics
            await self._update_user_analytics(stream.user_id, event)
            
            logger.debug(f"Tracked revenue event {event.id} for ${amount}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to track revenue event: {e}")
            return False
            
    async def get_user_analytics(self, user_id: str) -> RevenueAnalytics:
        """Get revenue analytics for user"""
        if user_id not in self.user_analytics:
            self.user_analytics[user_id] = RevenueAnalytics(user_id=user_id)
            
        return self.user_analytics[user_id]
        
    async def get_revenue_streams(self, user_id: str) -> List[RevenueStream]:
        """Get all revenue streams for user"""
        return [
            stream for stream in self.revenue_streams.values()
            if stream.user_id == user_id
        ]
        
    async def update_revenue_stream(
        self,
        stream_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """Update revenue stream configuration"""
        try:
            if stream_id not in self.revenue_streams:
                return False
                
            stream = self.revenue_streams[stream_id]
            
            # Apply updates
            for key, value in updates.items():
                if hasattr(stream, key):
                    setattr(stream, key, value)
                    
            # Update in Redis
            redis_updates = {}
            for key, value in updates.items():
                if key in ["rate_per_unit", "minimum_payout"]:
                    redis_updates[key] = str(value)
                elif key == "active":
                    redis_updates[key] = "true" if value else "false"
                elif key == "metadata":
                    redis_updates[key] = json.dumps(value)
                else:
                    redis_updates[key] = str(value)
                    
            if redis_updates:
                await self.redis.hset(f"revenue_stream:{stream_id}", mapping=redis_updates)
                
            logger.info(f"Updated revenue stream {stream_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update revenue stream: {e}")
            return False
            
    async def initiate_payment(
        self,
        user_id: str,
        amount: Decimal,
        currency: CurrencyCode,
        method: str = "bank_transfer"
    ) -> Optional[str]:
        """
        Initiate payment to user
        
        Args:
            user_id: User identifier
            amount: Payment amount
            currency: Payment currency
            method: Payment method
            
        Returns:
            Payment identifier if successful
        """
        try:
            from uuid import uuid4
            payment_id = str(uuid4())
            
            # Calculate processing fees (2.9% + $0.30)
            fee_rate = Decimal("0.029")
            fixed_fee = Decimal("0.30")
            fee_amount = (amount * fee_rate) + fixed_fee
            net_amount = amount - fee_amount
            
            payment = PaymentInfo(
                payment_id=payment_id,
                user_id=user_id,
                amount=amount,
                currency=currency,
                status=PaymentStatus.PENDING,
                method=method,
                fee_amount=fee_amount,
                net_amount=net_amount
            )
            
            self.pending_payments[payment_id] = payment
            
            # Store in Redis
            await self.redis.hset(
                f"payment:{payment_id}",
                mapping={
                    "user_id": user_id,
                    "amount": str(amount),
                    "currency": currency.value,
                    "status": PaymentStatus.PENDING.value,
                    "method": method,
                    "fee_amount": str(fee_amount),
                    "net_amount": str(net_amount),
                    "created_at": payment.created_at.isoformat()
                }
            )
            
            logger.info(f"Initiated payment {payment_id} for user {user_id}: ${amount}")
            return payment_id
            
        except Exception as e:
            logger.error(f"Failed to initiate payment: {e}")
            return None
            
    async def get_payment_status(self, payment_id: str) -> Optional[PaymentInfo]:
        """Get payment status"""
        return self.pending_payments.get(payment_id)
        
    async def get_user_payments(self, user_id: str) -> List[PaymentInfo]:
        """Get all payments for user"""
        return [
            payment for payment in self.pending_payments.values()
            if payment.user_id == user_id
        ]
        
    async def calculate_pending_payout(self, user_id: str) -> Tuple[Decimal, CurrencyCode]:
        """Calculate pending payout amount for user"""
        try:
            analytics = await self.get_user_analytics(user_id)
            
            # Find the primary currency (highest revenue)
            primary_currency = CurrencyCode.USD
            if analytics.revenue_by_currency:
                primary_currency = CurrencyCode(
                    max(analytics.revenue_by_currency.items(), key=lambda x: x[1])[0]
                )
                
            # Convert all pending revenue to primary currency
            total_pending = Decimal("0")
            for currency_code, amount in analytics.revenue_by_currency.items():
                if currency_code == primary_currency.value:
                    total_pending += amount
                else:
                    # Apply exchange rate conversion
                    rate = self.exchange_rates.get(currency_code, {}).get(primary_currency.value, 1.0)
                    total_pending += amount * Decimal(str(rate))
                    
            return total_pending, primary_currency
            
        except Exception as e:
            logger.error(f"Failed to calculate pending payout: {e}")
            return Decimal("0"), CurrencyCode.USD
            
    async def get_revenue_forecast(
        self,
        user_id: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """Generate revenue forecast for user"""
        try:
            analytics = await self.get_user_analytics(user_id)
            
            # Calculate trend from last 30 days
            daily_avg = analytics.avg_daily_revenue
            growth_rate = analytics.growth_rate / 100
            
            # Generate forecast
            forecast = {
                "forecast_days": days,
                "current_daily_avg": float(daily_avg),
                "growth_rate": growth_rate,
                "projected_total": float(daily_avg * Decimal(str(days)) * (1 + Decimal(str(growth_rate)))),
                "confidence": 0.8 if analytics.total_revenue > Decimal("100") else 0.6,
                "recommendations": []
            }
            
            # Add recommendations
            if analytics.growth_rate < 0:
                forecast["recommendations"].append("Consider diversifying revenue sources")
            if len(analytics.revenue_by_platform) < 3:
                forecast["recommendations"].append("Expand to additional platforms")
            if analytics.avg_daily_revenue < Decimal("5"):
                forecast["recommendations"].append("Focus on content optimization for higher engagement")
                
            return forecast
            
        except Exception as e:
            logger.error(f"Failed to generate revenue forecast: {e}")
            return {}
            
    async def _load_revenue_streams(self) -> None:
        """Load existing revenue streams from Redis"""
        try:
            # Scan for revenue stream keys
            cursor = 0
            while True:
                cursor, keys = await self.redis.scan(cursor, match="revenue_stream:*")
                
                for key in keys:
                    stream_data = await self.redis.hgetall(key)
                    if stream_data:
                        stream_id = key.decode().split(":")[-1]
                        
                        stream = RevenueStream(
                            id=stream_id,
                            user_id=stream_data[b"user_id"].decode(),
                            source=RevenueSource(stream_data[b"source"].decode()),
                            platform=stream_data[b"platform"].decode(),
                            currency=CurrencyCode(stream_data[b"currency"].decode()),
                            rate_per_unit=Decimal(stream_data[b"rate_per_unit"].decode()),
                            minimum_payout=Decimal(stream_data[b"minimum_payout"].decode()),
                            active=stream_data[b"active"].decode() == "true",
                            created_at=datetime.fromisoformat(stream_data[b"created_at"].decode()),
                            metadata=json.loads(stream_data.get(b"metadata", b"{}").decode())
                        )
                        
                        self.revenue_streams[stream_id] = stream
                        
                if cursor == 0:
                    break
                    
            logger.info(f"Loaded {len(self.revenue_streams)} revenue streams")
            
        except Exception as e:
            logger.error(f"Failed to load revenue streams: {e}")
            
    async def _update_user_analytics(self, user_id: str, event: RevenueEvent) -> None:
        """Update user revenue analytics"""
        try:
            if user_id not in self.user_analytics:
                self.user_analytics[user_id] = RevenueAnalytics(user_id=user_id)
                
            analytics = self.user_analytics[user_id]
            
            # Update totals
            analytics.total_revenue += event.amount
            analytics.pending_revenue += event.amount
            
            # Update by source
            source_key = event.source.value
            if source_key not in analytics.revenue_by_source:
                analytics.revenue_by_source[source_key] = Decimal("0")
            analytics.revenue_by_source[source_key] += event.amount
            
            # Update by platform
            if event.platform not in analytics.revenue_by_platform:
                analytics.revenue_by_platform[event.platform] = Decimal("0")
            analytics.revenue_by_platform[event.platform] += event.amount
            
            # Update by currency
            currency_key = event.currency.value
            if currency_key not in analytics.revenue_by_currency:
                analytics.revenue_by_currency[currency_key] = Decimal("0")
            analytics.revenue_by_currency[currency_key] += event.amount
            
            # Calculate 30-day revenue
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=30)
            if event.timestamp >= cutoff_date:
                analytics.last_30_days += event.amount
                
            # Calculate average daily revenue
            days_active = max(1, (datetime.now(timezone.utc) - cutoff_date).days)
            analytics.avg_daily_revenue = analytics.last_30_days / Decimal(str(days_active))
            
        except Exception as e:
            logger.error(f"Failed to update user analytics: {e}")
            
    async def _update_exchange_rates(self) -> None:
        """Update currency exchange rates"""
        try:
            # Mock exchange rates - in production, use real API
            self.exchange_rates = {
                "USD": {"EUR": 0.85, "GBP": 0.73, "JPY": 110.0, "CAD": 1.25, "AUD": 1.35, "CHF": 0.92},
                "EUR": {"USD": 1.18, "GBP": 0.86, "JPY": 129.0, "CAD": 1.47, "AUD": 1.59, "CHF": 1.08},
                "GBP": {"USD": 1.37, "EUR": 1.16, "JPY": 150.0, "CAD": 1.71, "AUD": 1.85, "CHF": 1.26},
            }
            
            logger.debug("Updated exchange rates")
            
        except Exception as e:
            logger.error(f"Failed to update exchange rates: {e}")
            
    async def _revenue_processor(self) -> None:
        """Background revenue processing task"""
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(300)  # Process every 5 minutes
                
                # Process revenue events and update analytics
                for user_id in self.user_analytics.keys():
                    await self._recalculate_user_analytics(user_id)
                    
            except Exception as e:
                logger.error(f"Revenue processor error: {e}")
                
    async def _payment_processor(self) -> None:
        """Background payment processing task"""
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(60)  # Check every minute
                
                # Process pending payments
                for payment_id, payment in list(self.pending_payments.items()):
                    if payment.status == PaymentStatus.PENDING:
                        # Simulate payment processing
                        await self._process_payment(payment)
                        
            except Exception as e:
                logger.error(f"Payment processor error: {e}")
                
    async def _analytics_updater(self) -> None:
        """Background analytics update task"""
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(3600)  # Update every hour
                
                # Update analytics for all users
                for user_id in self.user_analytics.keys():
                    await self._calculate_growth_rate(user_id)
                    
            except Exception as e:
                logger.error(f"Analytics updater error: {e}")
                
    async def _exchange_rate_updater(self) -> None:
        """Background exchange rate update task"""
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(3600)  # Update every hour
                await self._update_exchange_rates()
                
            except Exception as e:
                logger.error(f"Exchange rate updater error: {e}")
                
    async def _recalculate_user_analytics(self, user_id: str) -> None:
        """Recalculate user analytics from events"""
        try:
            # This would query all revenue events for the user
            # and recalculate analytics - implementation depends on data storage
            pass
            
        except Exception as e:
            logger.error(f"Failed to recalculate analytics: {e}")
            
    async def _process_payment(self, payment: PaymentInfo) -> None:
        """Process individual payment"""
        try:
            # Update payment status
            payment.status = PaymentStatus.PROCESSING
            payment.processed_at = datetime.now(timezone.utc)
            
            # Simulate processing delay
            await asyncio.sleep(1)
            
            # Mark as completed (in production, integrate with payment gateway)
            payment.status = PaymentStatus.COMPLETED
            
            # Update user analytics
            analytics = await self.get_user_analytics(payment.user_id)
            analytics.paid_revenue += payment.net_amount
            analytics.pending_revenue -= payment.amount
            
            logger.info(f"Processed payment {payment.payment_id}")
            
        except Exception as e:
            logger.error(f"Failed to process payment: {e}")
            payment.status = PaymentStatus.FAILED
            
    async def _calculate_growth_rate(self, user_id: str) -> None:
        """Calculate revenue growth rate for user"""
        try:
            analytics = self.user_analytics.get(user_id)
            if not analytics:
                return
                
            # Calculate growth rate based on recent trends
            # This is a simplified calculation - in production, use more sophisticated methods
            current_month = analytics.last_30_days
            previous_month = analytics.total_revenue - current_month
            
            if previous_month > Decimal("0"):
                growth_rate = float((current_month - previous_month) / previous_month * 100)
                analytics.growth_rate = growth_rate
            else:
                analytics.growth_rate = 0.0
                
        except Exception as e:
            logger.error(f"Failed to calculate growth rate: {e}")
            
    async def shutdown(self) -> None:
        """Gracefully shutdown revenue streamer"""
        try:
            self._shutdown_event.set()
            
            if self.redis:
                await self.redis.close()
                
            logger.info("RevenueStreamer shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during revenue streamer shutdown: {e}")
