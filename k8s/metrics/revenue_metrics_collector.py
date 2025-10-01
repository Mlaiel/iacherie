"""IA Influencer Agent - Revenue & Monetization Metrics Collector
Advanced revenue tracking and monetization analytics for multi-platform creators

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited

⚠️  AVERTISSEMENT LÉGAL STRICT ⚠️
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution sans autorisation 
écrite explicite est strictement interdite et fera l'objet de poursuites 
judiciaires selon la loi allemande et internationale.

Contact autorisé: mlaiel@live.de

Équipe de développement:
- Lead Developer IA & Architecte: Fahed Mlaiel
- Backend Senior Engineer: Fahed Mlaiel  
- ML Engineer: Fahed Mlaiel
- DBA & Data Engineer: Fahed Mlaiel
- DevOps Engineer: Fahed Mlaiel
- Security Specialist: Fahed Mlaiel
- Audio Processing Expert: Fahed Mlaiel

Features:
- Multi-platform revenue tracking (YouTube, Instagram, TikTok, Spotify, etc.)
- Licensing deal analytics and performance
- Creator earnings optimization metrics
- Cross-platform revenue attribution
- ROI calculation for content protection
- Payment processing performance
- Revenue forecasting and trends
- Commission and fee tracking
"""

import asyncio
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, asdict
from enum import Enum
from decimal import Decimal, ROUND_HALF_UP
import statistics
from collections import defaultdict

from backend.core.logging import get_logger
from backend.utils.redis_manager import RedisManager
from backend.utils.database import get_database_session
from .config import get_metrics_config

logger = get_logger(__name__)
metrics_config = get_metrics_config()


class RevenueSource(Enum):
    """
Revenue source types"""

    PLATFORM_REVENUE = "platform_revenue"          # Direct platform earnings
    LICENSING_DEAL = "licensing_deal"              # Content licensing
    PROTECTION_RECOVERY = "protection_recovery"    # Recovered from violations
    COLLABORATION = "collaboration"                # Creator collaborations
    SPONSORED_CONTENT = "sponsored_content"        # Brand sponsorships
    SUBSCRIPTION = "subscription"                  # Platform subscriptions
    MERCHANDISE = "merchandise"                    # Merchandise sales
    LIVE_PERFORMANCE = "live_performance"          # Live streaming/concerts


class Platform(Enum):
    """Supported platforms"""

    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    SPOTIFY = "spotify"
    SOUNDCLOUD = "soundcloud"
    TWITCH = "twitch"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    PATREON = "patreon"
    ONLYFANS = "onlyfans"
    CAMEO = "cameo"


class Currency(Enum):
    """Supported currencies"""

    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    CAD = "CAD"
    AUD = "AUD"
    JPY = "JPY"
    CHF = "CHF"
    SEK = "SEK"
    NOK = "NOK"
    DKK = "DKK"


class PaymentStatus(Enum):
    """Payment processing status"""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    DISPUTED = "disputed"


@dataclass
class RevenueTransaction:
    """Revenue transaction record"""
    transaction_id: str
    tenant_id: str
    user_id: str
    platform: Platform
    revenue_source: RevenueSource
    gross_amount: Decimal
    net_amount: Decimal
    currency: Currency
    exchange_rate: Optional[Decimal]
    commission_rate: float
    commission_amount: Decimal
    payment_status: PaymentStatus
    content_id: Optional[str]
    license_id: Optional[str]
    timestamp: datetime
    payout_date: Optional[datetime]
    metadata: Optional[Dict[str, Any]]


@dataclass
class LicensingDeal:
    """
Licensing deal record"""
    deal_id: str
    tenant_id: str
    licensor_id: str
    licensee_id: str
    content_id: str
    deal_type: str
    total_value: Decimal
    currency: Currency
    duration_months: int
    start_date: datetime
    end_date: datetime
    exclusivity: bool
    territory: str
    usage_rights: List[str]
    revenue_share: float
    status: str
    metadata: Optional[Dict[str, Any]]


class RevenueMetricsCollector:
    """
    Advanced revenue and monetization metrics collector
    
    Tracks revenue across all platforms, licensing deals, and monetization
    strategies for content creators in the IA Influencer ecosystem
    """
    
    def __init__(self):
        self.redis_manager = RedisManager()
        self.logger = logger
        
        # Currency conversion rates cache
        self.exchange_rates = {}
        self.rates_last_updated = None
        
        # Revenue tracking buffers
        self.revenue_buffer = []
        self.licensing_buffer = []
        
        # Start background processing
        self.processing_task = asyncio.create_task(self._start_background_processing())
    
    async def track_revenue_transaction(
        self,
        tenant_id: str,
        user_id: str,
        platform: Platform,
        revenue_source: RevenueSource,
        gross_amount: Decimal,
        currency: Currency,
        commission_rate: float = 0.15,  # 15% default commission
        content_id: Optional[str] = None,
        license_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
Track a revenue transaction"""
        
        transaction_id = f"txn_{int(datetime.now().timestamp())}_{user_id}"
        
        # Calculate commission and net amount
        commission_amount = gross_amount * Decimal(str(commission_rate))
        net_amount = gross_amount - commission_amount
        
        # Get exchange rate to USD for normalization
        exchange_rate = await self._get_exchange_rate(currency)
        
        transaction = RevenueTransaction(
            transaction_id=transaction_id,
            tenant_id=tenant_id,
            user_id=user_id,
            platform=platform,
            revenue_source=revenue_source,
            gross_amount=gross_amount,
            net_amount=net_amount,
            currency=currency,
            exchange_rate=exchange_rate,
            commission_rate=commission_rate,
            commission_amount=commission_amount,
            payment_status=PaymentStatus.PENDING,
            content_id=content_id,
            license_id=license_id,
            timestamp=datetime.now(timezone.utc),
            payout_date=None,
            metadata=metadata
        )
        
        # Store transaction
        await self._store_revenue_transaction(transaction)
        
        # Update real-time metrics
        await self._update_realtime_revenue_metrics(transaction)
        
        # Add to processing buffer
        self.revenue_buffer.append(transaction)
        
        return transaction_id
    
    async def track_licensing_deal(
        self,
        tenant_id: str,
        licensor_id: str,
        licensee_id: str,
        content_id: str,
        deal_type: str,
        total_value: Decimal,
        currency: Currency,
        duration_months: int,
        exclusivity: bool = False,
        territory: str = "global",
        usage_rights: Optional[List[str]] = None,
        revenue_share: float = 0.7,  # 70% to creator
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Track a licensing deal"""
        
        deal_id = f"deal_{int(datetime.now().timestamp())}_{licensor_id}"
        
        start_date = datetime.now(timezone.utc)
        end_date = start_date + timedelta(days=duration_months * 30)
        
        deal = LicensingDeal(
            deal_id=deal_id,
            tenant_id=tenant_id,
            licensor_id=licensor_id,
            licensee_id=licensee_id,
            content_id=content_id,
            deal_type=deal_type,
            total_value=total_value,
            currency=currency,
            duration_months=duration_months,
            start_date=start_date,
            end_date=end_date,
            exclusivity=exclusivity,
            territory=territory,
            usage_rights=usage_rights or ["streaming", "download"],
            revenue_share=revenue_share,
            status="active",
            metadata=metadata
        )
        
        # Store licensing deal
        await self._store_licensing_deal(deal)
        
        # Create initial revenue transaction for the deal
        creator_amount = total_value * Decimal(str(revenue_share))
        await self.track_revenue_transaction(
            tenant_id=tenant_id,
            user_id=licensor_id,
            platform=Platform.SPOTIFY,  # Default platform for licensing
            revenue_source=RevenueSource.LICENSING_DEAL,
            gross_amount=creator_amount,
            currency=currency,
            commission_rate=0.05,  # Lower commission for licensing deals
            license_id=deal_id,
            metadata={"deal_type": deal_type, "territory": territory}
        )
        
        return deal_id
    
    async def update_payment_status(
        self,
        transaction_id: str,
        status: PaymentStatus,
        payout_date: Optional[datetime] = None
    ) -> None:
        """Update payment status for a transaction"""
        
        try:
            async with get_database_session() as session:
                await session.execute(
                    """
                    UPDATE revenue_transactions 
                    SET payment_status = $1, payout_date = $2, updated_at = NOW()
                    WHERE transaction_id = $3
                    """,
                    status.value,
                    payout_date,
                    transaction_id
                )
                await session.commit()
                
                # Update real-time metrics
                await self.redis_manager.increment(
                    f"payment_status:{status.value}",
                    expire=3600
                )
                
        except Exception as e:
            self.logger.error(f"Error updating payment status: {e}")
    
    async def get_revenue_analytics(
        self,
        tenant_id: str,
        user_id: Optional[str] = None,
        platform: Optional[Platform] = None,
        time_range: str = "30d",
        currency: Currency = Currency.USD
    ) -> Dict[str, Any]:
        """Get comprehensive revenue analytics"""
        
        try:
            # Parse time range
            if time_range == "24h":
                start_time = datetime.now(timezone.utc) - timedelta(hours=24)
            elif time_range == "7d":
                start_time = datetime.now(timezone.utc) - timedelta(days=7)
            elif time_range == "30d":
                start_time = datetime.now(timezone.utc) - timedelta(days=30)
            elif time_range == "90d":
                start_time = datetime.now(timezone.utc) - timedelta(days=90)
            elif time_range == "1y":
                start_time = datetime.now(timezone.utc) - timedelta(days=365)
            else:
                start_time = datetime.now(timezone.utc) - timedelta(days=30)
            
            async with get_database_session() as session:
                # Build query filters
                filters = ["tenant_id = $1", "timestamp >= $2"]
                params = [tenant_id, start_time]
                
                if user_id:
                    filters.append(f"user_id = ${len(params) + 1}")
                    params.append(user_id)
                
                if platform:
                    filters.append(f"platform = ${len(params) + 1}")
                    params.append(platform.value)
                
                where_clause = " AND ".join(filters)
                
                # Get revenue summary
                revenue_summary = await session.fetchrow(f"""
                    SELECT 
                        COUNT(*) as transaction_count,
                        SUM(gross_amount * COALESCE(exchange_rate, 1)) as total_gross_usd,
                        SUM(net_amount * COALESCE(exchange_rate, 1)) as total_net_usd,
                        SUM(commission_amount * COALESCE(exchange_rate, 1)) as total_commission_usd,
                        AVG(gross_amount * COALESCE(exchange_rate, 1)) as avg_transaction_usd,
                        COUNT(DISTINCT user_id) as unique_creators,
                        COUNT(CASE WHEN payment_status = 'completed' THEN 1 END) as completed_payments
                    FROM revenue_transactions 
                    WHERE {where_clause}
                """, *params)
                
                # Get revenue by source
                revenue_by_source = await session.fetch(f"""
                    SELECT 
                        revenue_source,
                        COUNT(*) as transaction_count,
                        SUM(gross_amount * COALESCE(exchange_rate, 1)) as total_gross_usd,
                        SUM(net_amount * COALESCE(exchange_rate, 1)) as total_net_usd
                    FROM revenue_transactions 
                    WHERE {where_clause}
                    GROUP BY revenue_source
                    ORDER BY total_gross_usd DESC
                """, *params)
                
                # Get revenue by platform
                revenue_by_platform = await session.fetch(f"""
                    SELECT 
                        platform,
                        COUNT(*) as transaction_count,
                        SUM(gross_amount * COALESCE(exchange_rate, 1)) as total_gross_usd,
                        SUM(net_amount * COALESCE(exchange_rate, 1)) as total_net_usd,
                        AVG(commission_rate) as avg_commission_rate
                    FROM revenue_transactions 
                    WHERE {where_clause}
                    GROUP BY platform
                    ORDER BY total_gross_usd DESC
                """, *params)
                
                # Get daily revenue trend
                daily_revenue = await session.fetch(f"""
                    SELECT 
                        DATE(timestamp) as date,
                        SUM(gross_amount * COALESCE(exchange_rate, 1)) as daily_gross_usd,
                        SUM(net_amount * COALESCE(exchange_rate, 1)) as daily_net_usd,
                        COUNT(*) as daily_transactions
                    FROM revenue_transactions 
                    WHERE {where_clause}
                    GROUP BY DATE(timestamp)
                    ORDER BY date DESC
                    LIMIT 30
                """, *params)
                
                # Calculate growth metrics
                previous_period_start = start_time - (datetime.now(timezone.utc) - start_time)
                previous_revenue = await session.fetchrow(f"""
                    SELECT SUM(gross_amount * COALESCE(exchange_rate, 1)) as previous_gross_usd
                    FROM revenue_transactions 
                    WHERE tenant_id = $1 AND timestamp >= $2 AND timestamp < $3
                """, tenant_id, previous_period_start, start_time)
                
                current_gross = float(revenue_summary["total_gross_usd"] or 0)
                previous_gross = float(previous_revenue["previous_gross_usd"] or 0)
                
                growth_rate = (
                    ((current_gross - previous_gross) / max(previous_gross, 1)) * 100
                    if previous_gross > 0 else 0
                )
                
                return {
                    "time_range": time_range,
                    "currency": currency.value,
                    "summary": {
                        "transaction_count": revenue_summary["transaction_count"],
                        "total_gross_usd": current_gross,
                        "total_net_usd": float(revenue_summary["total_net_usd"] or 0),
                        "total_commission_usd": float(revenue_summary["total_commission_usd"] or 0),
                        "avg_transaction_usd": float(revenue_summary["avg_transaction_usd"] or 0),
                        "unique_creators": revenue_summary["unique_creators"],
                        "payment_completion_rate": (
                            revenue_summary["completed_payments"] / 
                            max(revenue_summary["transaction_count"], 1)
                        ),
                        "growth_rate_percent": growth_rate
                    },
                    "revenue_by_source": [
                        {
                            "source": row["revenue_source"],
                            "transaction_count": row["transaction_count"],
                            "total_gross_usd": float(row["total_gross_usd"]),
                            "total_net_usd": float(row["total_net_usd"]),
                            "percentage": (float(row["total_gross_usd"]) / max(current_gross, 1)) * 100
                        }
                        for row in revenue_by_source
                    ],
                    "revenue_by_platform": [
                        {
                            "platform": row["platform"],
                            "transaction_count": row["transaction_count"],
                            "total_gross_usd": float(row["total_gross_usd"]),
                            "total_net_usd": float(row["total_net_usd"]),
                            "avg_commission_rate": float(row["avg_commission_rate"]),
                            "percentage": (float(row["total_gross_usd"]) / max(current_gross, 1)) * 100
                        }
                        for row in revenue_by_platform
                    ],
                    "daily_trend": [
                        {
                            "date": row["date"].isoformat(),
                            "gross_usd": float(row["daily_gross_usd"]),
                            "net_usd": float(row["daily_net_usd"]),
                            "transactions": row["daily_transactions"]
                        }
                        for row in daily_revenue
                    ],
                    "generated_at": datetime.now(timezone.utc).isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"Error getting revenue analytics: {e}")
            return {}
    
    async def get_licensing_analytics(
        self,
        tenant_id: str,
        user_id: Optional[str] = None,
        time_range: str = "30d"
    ) -> Dict[str, Any]:
        """Get licensing deal analytics"""
        
        try:
            # Parse time range
            if time_range == "30d":
                start_time = datetime.now(timezone.utc) - timedelta(days=30)
            elif time_range == "90d":
                start_time = datetime.now(timezone.utc) - timedelta(days=90)
            elif time_range == "1y":
                start_time = datetime.now(timezone.utc) - timedelta(days=365)
            else:
                start_time = datetime.now(timezone.utc) - timedelta(days=30)
            
            async with get_database_session() as session:
                # Build query filters
                filters = ["tenant_id = $1", "start_date >= $2"]
                params = [tenant_id, start_time]
                
                if user_id:
                    filters.append(f"licensor_id = ${len(params) + 1}")
                    params.append(user_id)
                
                where_clause = " AND ".join(filters)
                
                # Get licensing summary
                licensing_summary = await session.fetchrow(f"""
                    SELECT 
                        COUNT(*) as total_deals,
                        SUM(total_value) as total_value_usd,
                        AVG(total_value) as avg_deal_value,
                        AVG(duration_months) as avg_duration_months,
                        AVG(revenue_share) as avg_revenue_share,
                        COUNT(CASE WHEN exclusivity = true THEN 1 END) as exclusive_deals,
                        COUNT(CASE WHEN status = 'active' THEN 1 END) as active_deals
                    FROM licensing_deals 
                    WHERE {where_clause}
                """, *params)
                
                # Get deals by type
                deals_by_type = await session.fetch(f"""
                    SELECT 
                        deal_type,
                        COUNT(*) as deal_count,
                        SUM(total_value) as total_value,
                        AVG(total_value) as avg_value
                    FROM licensing_deals 
                    WHERE {where_clause}
                    GROUP BY deal_type
                    ORDER BY total_value DESC
                """, *params)
                
                # Get top performing content
                top_content = await session.fetch(f"""
                    SELECT 
                        content_id,
                        COUNT(*) as licensing_count,
                        SUM(total_value) as total_licensing_value,
                        AVG(revenue_share) as avg_revenue_share
                    FROM licensing_deals 
                    WHERE {where_clause}
                    GROUP BY content_id
                    ORDER BY total_licensing_value DESC
                    LIMIT 10
                """, *params)
                
                return {
                    "time_range": time_range,
                    "summary": {
                        "total_deals": licensing_summary["total_deals"],
                        "total_value_usd": float(licensing_summary["total_value_usd"] or 0),
                        "avg_deal_value": float(licensing_summary["avg_deal_value"] or 0),
                        "avg_duration_months": float(licensing_summary["avg_duration_months"] or 0),
                        "avg_revenue_share": float(licensing_summary["avg_revenue_share"] or 0),
                        "exclusive_deals": licensing_summary["exclusive_deals"],
                        "active_deals": licensing_summary["active_deals"],
                        "exclusivity_rate": (
                            licensing_summary["exclusive_deals"] / 
                            max(licensing_summary["total_deals"], 1)
                        )
                    },
                    "deals_by_type": [
                        {
                            "deal_type": row["deal_type"],
                            "deal_count": row["deal_count"],
                            "total_value": float(row["total_value"]),
                            "avg_value": float(row["avg_value"])
                        }
                        for row in deals_by_type
                    ],
                    "top_performing_content": [
                        {
                            "content_id": row["content_id"],
                            "licensing_count": row["licensing_count"],
                            "total_value": float(row["total_licensing_value"]),
                            "avg_revenue_share": float(row["avg_revenue_share"])
                        }
                        for row in top_content
                    ],
                    "generated_at": datetime.now(timezone.utc).isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"Error getting licensing analytics: {e}")
            return {}
    
    async def calculate_creator_performance_score(
        self,
        tenant_id: str,
        user_id: str,
        time_range: str = "90d"
    ) -> Dict[str, Any]:
        """Calculate comprehensive creator performance score"""
        
        try:
            # Get revenue analytics
            revenue_data = await self.get_revenue_analytics(
                tenant_id=tenant_id,
                user_id=user_id,
                time_range=time_range
            )
            
            # Get licensing analytics
            licensing_data = await self.get_licensing_analytics(
                tenant_id=tenant_id,
                user_id=user_id,
                time_range=time_range
            )
            
            # Calculate performance metrics
            total_revenue = revenue_data.get("summary", {}).get("total_gross_usd", 0)
            growth_rate = revenue_data.get("summary", {}).get("growth_rate_percent", 0)
            licensing_deals = licensing_data.get("summary", {}).get("total_deals", 0)
            
            # Calculate diversification score (based on revenue sources)
            revenue_sources = len(revenue_data.get("revenue_by_source", []))
            platform_diversity = len(revenue_data.get("revenue_by_platform", []))
            
            # Calculate performance score (0-100)
            revenue_score = min(total_revenue / 10000 * 30, 30)  # Max 30 points for $10k revenue
            growth_score = max(min(growth_rate / 50 * 25, 25), -10)  # Max 25 points for 50% growth
            diversification_score = min((revenue_sources + platform_diversity) * 2.5, 20)  # Max 20 points
            licensing_score = min(licensing_deals * 5, 25)  # Max 25 points for licensing
            
            total_score = revenue_score + growth_score + diversification_score + licensing_score
            
            return {
                "user_id": user_id,
                "time_range": time_range,
                "performance_score": round(total_score, 2),
                "score_breakdown": {
                    "revenue_score": round(revenue_score, 2),
                    "growth_score": round(growth_score, 2),
                    "diversification_score": round(diversification_score, 2),
                    "licensing_score": round(licensing_score, 2)
                },
                "metrics": {
                    "total_revenue_usd": total_revenue,
                    "growth_rate_percent": growth_rate,
                    "revenue_sources": revenue_sources,
                    "platform_diversity": platform_diversity,
                    "licensing_deals": licensing_deals
                },
                "performance_tier": (
                    "Elite" if total_score >= 80 else
                    "Advanced" if total_score >= 60 else
                    "Intermediate" if total_score >= 40 else
                    "Emerging" if total_score >= 20 else
                    "Beginner"
                ),
                "calculated_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating creator performance score: {e}")
            return {"error": str(e)}
    
    async def _get_exchange_rate(self, currency: Currency) -> Decimal:
        """Get exchange rate to USD"""
        if currency == Currency.USD:
            return Decimal("1.0")
        
        # Check cache
        if (self.rates_last_updated and 
            datetime.now() - self.rates_last_updated < timedelta(hours=1)):
            return self.exchange_rates.get(currency.value, Decimal("1.0"))
        
        # Mock exchange rates (in production, use real API)
        mock_rates = {
            "EUR": Decimal("1.10"),
            "GBP": Decimal("1.25"),
            "CAD": Decimal("0.75"),
            "AUD": Decimal("0.68"),
            "JPY": Decimal("0.0067"),
            "CHF": Decimal("1.12"),
            "SEK": Decimal("0.096"),
            "NOK": Decimal("0.094"),
            "DKK": Decimal("0.148")
        }
        
        self.exchange_rates = mock_rates
        self.rates_last_updated = datetime.now()
        
        return mock_rates.get(currency.value, Decimal("1.0"))
    
    async def _store_revenue_transaction(self, transaction: RevenueTransaction) -> None:
        """Store revenue transaction in database"""
        try:
            async with get_database_session() as session:
                await session.execute(
                    """
                    INSERT INTO revenue_transactions 
                    (transaction_id, tenant_id, user_id, platform, revenue_source, 
                     gross_amount, net_amount, currency, exchange_rate, commission_rate, 
                     commission_amount, payment_status, content_id, license_id, 
                     timestamp, payout_date, metadata)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17)
                    """,
                    transaction.transaction_id,
                    transaction.tenant_id,
                    transaction.user_id,
                    transaction.platform.value,
                    transaction.revenue_source.value,
                    float(transaction.gross_amount),
                    float(transaction.net_amount),
                    transaction.currency.value,
                    float(transaction.exchange_rate) if transaction.exchange_rate else None,
                    transaction.commission_rate,
                    float(transaction.commission_amount),
                    transaction.payment_status.value,
                    transaction.content_id,
                    transaction.license_id,
                    transaction.timestamp,
                    transaction.payout_date,
                    json.dumps(transaction.metadata) if transaction.metadata else None
                )
                await session.commit()
                
        except Exception as e:
            self.logger.error(f"Error storing revenue transaction: {e}")
    
    async def _store_licensing_deal(self, deal: LicensingDeal) -> None:
        """Store licensing deal in database"""
        try:
            async with get_database_session() as session:
                await session.execute(
                    """
                    INSERT INTO licensing_deals 
                    (deal_id, tenant_id, licensor_id, licensee_id, content_id, deal_type, 
                     total_value, currency, duration_months, start_date, end_date, 
                     exclusivity, territory, usage_rights, revenue_share, status, metadata)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17)
                    """,
                    deal.deal_id,
                    deal.tenant_id,
                    deal.licensor_id,
                    deal.licensee_id,
                    deal.content_id,
                    deal.deal_type,
                    float(deal.total_value),
                    deal.currency.value,
                    deal.duration_months,
                    deal.start_date,
                    deal.end_date,
                    deal.exclusivity,
                    deal.territory,
                    json.dumps(deal.usage_rights),
                    deal.revenue_share,
                    deal.status,
                    json.dumps(deal.metadata) if deal.metadata else None
                )
                await session.commit()
                
        except Exception as e:
            self.logger.error(f"Error storing licensing deal: {e}")
    
    async def _update_realtime_revenue_metrics(self, transaction: RevenueTransaction) -> None:
        """Update real-time revenue metrics in Redis"""
        try:
            # Update daily totals
            today = datetime.now(timezone.utc).date().isoformat()
            
            await self.redis_manager.increment(
                f"daily_revenue:{transaction.tenant_id}:{today}",
                float(transaction.gross_amount),
                expire=86400 * 2  # 2 days
            )
            
            # Update platform totals
            await self.redis_manager.increment(
                f"platform_revenue:{transaction.tenant_id}:{transaction.platform.value}",
                float(transaction.gross_amount),
                expire=3600  # 1 hour
            )
            
            # Update source totals
            await self.redis_manager.increment(
                f"source_revenue:{transaction.tenant_id}:{transaction.revenue_source.value}",
                float(transaction.gross_amount),
                expire=3600  # 1 hour
            )
            
        except Exception as e:
            self.logger.error(f"Error updating real-time revenue metrics: {e}")
    
    async def _start_background_processing(self) -> None:
        """Start background processing tasks"""
        while True:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes
                
                # Process revenue buffer
                if self.revenue_buffer:
                    await self._process_revenue_analytics()
                
                # Update exchange rates
                await self._update_exchange_rates()
                
            except Exception as e:
                self.logger.error(f"Error in background processing: {e}")
                await asyncio.sleep(60)
    
    async def _process_revenue_analytics(self) -> None:
        """Process revenue analytics for performance optimization"""
        try:
            # Process recent transactions for insights
            # This could include ML predictions, trend analysis, etc.
            pass
        except Exception as e:
            self.logger.error(f"Error processing revenue analytics: {e}")
    
    async def _update_exchange_rates(self) -> None:
        """Update currency exchange rates"""
        try:
            # In production, integrate with real exchange rate API
            # For now, using mock rates
            pass
        except Exception as e:
            self.logger.error(f"Error updating exchange rates: {e}")
