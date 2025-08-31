"""Revenue Cache for IA Influencer Agent Platform
Specialized caching for monetization, revenue tracking, and financial analytics

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use prohibited.
"""
import asyncio
import logging
import json
from typing import Any, Dict, List, Optional, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from decimal import Decimal
import statistics

from .redis_cache import RedisCache, RedisConfig
from .memory_cache import MemoryCache

logger = logging.getLogger(__name__)

class RevenueSource(Enum):
    """Revenue sources"""
    SPOTIFY = "spotify"
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    APPLE_MUSIC = "apple_music"
    DEEZER = "deezer"
    LICENSING = "licensing"
    DIRECT_SALES = "direct_sales"
    DONATIONS = "donations"
    MERCHANDISE = "merchandise"
    LIVE_PERFORMANCES = "live_performances"
    SYNC_LICENSING = "sync_licensing"

class RevenueType(Enum):
    """Types of revenue"""
    STREAMING = "streaming"
    DOWNLOADS = "downloads"
    LICENSING_FEES = "licensing_fees"
    ROYALTIES = "royalties"
    ADVERTISING = "advertising"
    SUBSCRIPTION = "subscription"
    COMMISSION = "commission"
    TIP = "tip"
    SALE = "sale"

class PaymentStatus(Enum):
    """Payment processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

@dataclass
class RevenueEntry:
    """Revenue entry data structure"""
    entry_id: str
    user_id: str
    content_id: Optional[str]
    tenant_id: Optional[str]
    
    # Revenue details
    revenue_source: RevenueSource
    revenue_type: RevenueType
    amount: Decimal
    currency: str
    
    # Period information
    period_start: datetime
    period_end: datetime
    recorded_at: datetime
    
    # Platform data
    platform_data: Dict[str, Any]
    raw_data: Dict[str, Any]
    
    # Metadata
    content_title: Optional[str] = None
    content_type: Optional[str] = None
    geographic_region: Optional[str] = None
    
    # Processing
    payment_status: PaymentStatus = PaymentStatus.PENDING
    processed_at: Optional[datetime] = None
    processing_fee: Decimal = Decimal('0.00')
    net_amount: Optional[Decimal] = None
    
    def __post_init__(self):
        if self.net_amount is None:
            self.net_amount = self.amount - self.processing_fee
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        # Convert Decimal and datetime objects for JSON serialization
        data['amount'] = str(self.amount)
        data['processing_fee'] = str(self.processing_fee)
        data['net_amount'] = str(self.net_amount)
        data['period_start'] = self.period_start.isoformat()
        data['period_end'] = self.period_end.isoformat()
        data['recorded_at'] = self.recorded_at.isoformat()
        if self.processed_at:
            data['processed_at'] = self.processed_at.isoformat()
        data['revenue_source'] = self.revenue_source.value
        data['revenue_type'] = self.revenue_type.value
        data['payment_status'] = self.payment_status.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RevenueEntry':
        """Create from dictionary"""
        # Convert string values back to appropriate types
        data['amount'] = Decimal(data['amount'])
        data['processing_fee'] = Decimal(data['processing_fee'])
        data['net_amount'] = Decimal(data['net_amount'])
        data['period_start'] = datetime.fromisoformat(data['period_start'])
        data['period_end'] = datetime.fromisoformat(data['period_end'])
        data['recorded_at'] = datetime.fromisoformat(data['recorded_at'])
        if data.get('processed_at'):
            data['processed_at'] = datetime.fromisoformat(data['processed_at'])
        data['revenue_source'] = RevenueSource(data['revenue_source'])
        data['revenue_type'] = RevenueType(data['revenue_type'])
        data['payment_status'] = PaymentStatus(data['payment_status'])
        return cls(**data)

@dataclass
class RevenueAnalytics:
    """Revenue analytics summary"""
    user_id: str
    period_start: datetime
    period_end: datetime
    
    # Totals
    total_revenue: Decimal
    total_fees: Decimal
    net_revenue: Decimal
    
    # Breakdowns
    revenue_by_source: Dict[str, Decimal]
    revenue_by_type: Dict[str, Decimal]
    revenue_by_content: Dict[str, Decimal]
    revenue_by_region: Dict[str, Decimal]
    
    # Performance metrics
    growth_rate: float
    average_per_day: Decimal
    top_performing_content: List[Dict[str, Any]]
    
    # Predictions
    projected_monthly: Decimal
    projected_yearly: Decimal
    
    generated_at: datetime

class RevenueCache:
    """
    Advanced revenue cache for monetization tracking and financial analytics
    Handles revenue data aggregation and performance optimization
    """
    
    def __init__(self,
                 redis_config: RedisConfig,
                 default_currency: str = "EUR",
                 retention_months: int = 24):
        
        self.default_currency = default_currency
        self.retention_months = retention_months
        
        # Initialize caches
        self.redis_cache = RedisCache(redis_config)
        self.memory_cache = MemoryCache(
            max_size=5000,
            default_ttl=1800  # 30 minutes
        )
        
        # Cache key prefixes
        self.REVENUE_PREFIX = "revenue:entry"
        self.USER_REVENUE_PREFIX = "revenue:user"
        self.CONTENT_REVENUE_PREFIX = "revenue:content"
        self.ANALYTICS_PREFIX = "revenue:analytics"
        self.DAILY_TOTALS_PREFIX = "revenue:daily"
        self.MONTHLY_TOTALS_PREFIX = "revenue:monthly"
        self.PLATFORM_TOTALS_PREFIX = "revenue:platform"
        self.PAYMENT_QUEUE_PREFIX = "revenue:payment_queue"
        
        # Currency conversion rates cache
        self.EXCHANGE_RATES_PREFIX = "revenue:exchange_rates"
        
        # Statistics
        self._stats = {
            'revenue_entries': 0,
            'total_revenue_tracked': Decimal('0.00'),
            'payments_processed': 0,
            'analytics_generated': 0,
            'cache_hits': 0,
            'cache_misses': 0
        }
        
        logger.info("RevenueCache initialized")
    
    async def initialize(self):
        """Initialize cache connections"""
        await self.redis_cache.connect()
    
    def _generate_entry_id(self, user_id: str, timestamp: datetime) -> str:
        """Generate unique revenue entry ID"""
        timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")
        return f"{user_id}_{timestamp_str}_{hash(str(timestamp.microsecond)) % 10000:04d}"
    
    async def record_revenue(self,
                           user_id: str,
                           revenue_source: RevenueSource,
                           revenue_type: RevenueType,
                           amount: Union[Decimal, float, str],
                           currency: str,
                           period_start: datetime,
                           period_end: datetime,
                           platform_data: Dict[str, Any],
                           content_id: Optional[str] = None,
                           tenant_id: Optional[str] = None,
                           content_title: Optional[str] = None,
                           content_type: Optional[str] = None,
                           geographic_region: Optional[str] = None,
                           processing_fee: Union[Decimal, float, str] = "0.00") -> str:
        """Record revenue entry"""
        
        try:
            # Convert amount to Decimal
            if not isinstance(amount, Decimal):
                amount = Decimal(str(amount))
            if not isinstance(processing_fee, Decimal):
                processing_fee = Decimal(str(processing_fee))
            
            # Generate entry ID
            entry_id = self._generate_entry_id(user_id, datetime.utcnow())
            
            # Create revenue entry
            revenue_entry = RevenueEntry(
                entry_id=entry_id,
                user_id=user_id,
                content_id=content_id,
                tenant_id=tenant_id,
                revenue_source=revenue_source,
                revenue_type=revenue_type,
                amount=amount,
                currency=currency,
                period_start=period_start,
                period_end=period_end,
                recorded_at=datetime.utcnow(),
                platform_data=platform_data,
                raw_data=platform_data.copy(),
                content_title=content_title,
                content_type=content_type,
                geographic_region=geographic_region,
                processing_fee=processing_fee
            )
            
            # Store revenue entry
            entry_key = f"{self.REVENUE_PREFIX}:{entry_id}"
            await self.redis_cache.set(
                entry_key,
                json.dumps(revenue_entry.to_dict()),
                ttl=86400 * 30 * self.retention_months
            )
            
            # Update user revenue index
            await self._update_user_revenue_index(user_id, entry_id, period_start)
            
            # Update content revenue index if applicable
            if content_id:
                await self._update_content_revenue_index(content_id, entry_id, amount, currency)
            
            # Update daily and monthly totals
            await self._update_daily_totals(user_id, period_start, amount, currency, revenue_source)
            await self._update_monthly_totals(user_id, period_start, amount, currency, revenue_source)
            
            # Update platform totals
            await self._update_platform_totals(revenue_source, amount, currency, period_start)
            
            # Update statistics
            self._stats['revenue_entries'] += 1
            if currency == self.default_currency:
                self._stats['total_revenue_tracked'] += amount
            
            logger.info(f"Recorded revenue: {entry_id} ({amount} {currency})")
            return entry_id
            
        except Exception as e:
            logger.error(f"Failed to record revenue: {e}")
            return ""
    
    async def get_revenue_entry(self, entry_id: str) -> Optional[RevenueEntry]:
        """Get revenue entry by ID"""
        
        # Try memory cache first
        cache_key = f"revenue_entry:{entry_id}"
        cached_entry = self.memory_cache.get(cache_key)
        if cached_entry:
            self._stats['cache_hits'] += 1
            return cached_entry
        
        # Try Redis cache
        entry_key = f"{self.REVENUE_PREFIX}:{entry_id}"
        entry_data = await self.redis_cache.get(entry_key)
        
        if entry_data:
            try:
                entry_dict = json.loads(entry_data)
                revenue_entry = RevenueEntry.from_dict(entry_dict)
                
                # Cache in memory
                self.memory_cache.set(cache_key, revenue_entry, ttl=300)
                
                self._stats['cache_hits'] += 1
                return revenue_entry
                
            except Exception as e:
                logger.error(f"Failed to deserialize revenue entry: {e}")
        
        self._stats['cache_misses'] += 1
        return None
    
    async def get_user_revenue(self,
                             user_id: str,
                             start_date: Optional[datetime] = None,
                             end_date: Optional[datetime] = None,
                             revenue_source: Optional[RevenueSource] = None,
                             limit: int = 1000) -> List[RevenueEntry]:
        """Get revenue entries for user"""
        
        try:
            # Get user revenue index
            user_key = f"{self.USER_REVENUE_PREFIX}:{user_id}"
            index_data = await self.redis_cache.get(user_key)
            
            if not index_data:
                return []
            
            entry_index = json.loads(index_data)
            
            # Filter by date range
            filtered_entries = []
            for entry_info in entry_index:
                entry_date = datetime.fromisoformat(entry_info['period_start'])
                
                # Date range filter
                if start_date and entry_date < start_date:
                    continue
                if end_date and entry_date > end_date:
                    continue
                
                # Revenue source filter
                if revenue_source and entry_info.get('revenue_source') != revenue_source.value:
                    continue
                
                filtered_entries.append(entry_info)
            
            # Sort by date (most recent first)
            filtered_entries.sort(key=lambda x: x['period_start'], reverse=True)
            
            # Limit results
            filtered_entries = filtered_entries[:limit]
            
            # Fetch full revenue entries
            revenue_entries = []
            for entry_info in filtered_entries:
                revenue_entry = await self.get_revenue_entry(entry_info['entry_id'])
                if revenue_entry:
                    revenue_entries.append(revenue_entry)
            
            return revenue_entries
            
        except Exception as e:
            logger.error(f"Failed to get user revenue: {e}")
            return []
    
    async def get_content_revenue(self,
                                content_id: str,
                                start_date: Optional[datetime] = None,
                                end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Get revenue summary for specific content"""
        
        try:
            content_key = f"{self.CONTENT_REVENUE_PREFIX}:{content_id}"
            revenue_data = await self.redis_cache.get(content_key)
            
            if not revenue_data:
                return {
                    'content_id': content_id,
                    'total_revenue': Decimal('0.00'),
                    'currency': self.default_currency,
                    'entry_count': 0,
                    'revenue_by_source': {},
                    'revenue_by_type': {}
                }
            
            content_revenue = json.loads(revenue_data)
            
            # Convert string amounts back to Decimal
            for key, value in content_revenue.items():
                if 'revenue' in key or 'amount' in key:
                    if isinstance(value, dict):
                        for k, v in value.items():
                            if isinstance(v, str) and v.replace('.', '').replace('-', '').isdigit():
                                content_revenue[key][k] = Decimal(v)
                    elif isinstance(value, str) and value.replace('.', '').replace('-', '').isdigit():
                        content_revenue[key] = Decimal(value)
            
            return content_revenue
            
        except Exception as e:
            logger.error(f"Failed to get content revenue: {e}")
            return {}
    
    async def generate_analytics(self,
                               user_id: str,
                               period_start: datetime,
                               period_end: datetime) -> RevenueAnalytics:
        """Generate comprehensive revenue analytics"""
        
        try:
            # Check cache first
            analytics_key = f"{self.ANALYTICS_PREFIX}:{user_id}:{period_start.date()}:{period_end.date()}"
            cached_analytics = self.memory_cache.get(analytics_key)
            
            if cached_analytics:
                self._stats['cache_hits'] += 1
                return cached_analytics
            
            # Get revenue entries for period
            revenue_entries = await self.get_user_revenue(user_id, period_start, period_end)
            
            if not revenue_entries:
                # Return empty analytics
                return RevenueAnalytics(
                    user_id=user_id,
                    period_start=period_start,
                    period_end=period_end,
                    total_revenue=Decimal('0.00'),
                    total_fees=Decimal('0.00'),
                    net_revenue=Decimal('0.00'),
                    revenue_by_source={},
                    revenue_by_type={},
                    revenue_by_content={},
                    revenue_by_region={},
                    growth_rate=0.0,
                    average_per_day=Decimal('0.00'),
                    top_performing_content=[],
                    projected_monthly=Decimal('0.00'),
                    projected_yearly=Decimal('0.00'),
                    generated_at=datetime.utcnow()
                )
            
            # Calculate totals
            total_revenue = sum(entry.amount for entry in revenue_entries)
            total_fees = sum(entry.processing_fee for entry in revenue_entries)
            net_revenue = total_revenue - total_fees
            
            # Revenue by source
            revenue_by_source = {}
            for entry in revenue_entries:
                source = entry.revenue_source.value
                revenue_by_source[source] = revenue_by_source.get(source, Decimal('0.00')) + entry.amount
            
            # Revenue by type
            revenue_by_type = {}
            for entry in revenue_entries:
                rev_type = entry.revenue_type.value
                revenue_by_type[rev_type] = revenue_by_type.get(rev_type, Decimal('0.00')) + entry.amount
            
            # Revenue by content
            revenue_by_content = {}
            for entry in revenue_entries:
                if entry.content_id:
                    content_key = f"{entry.content_id}:{entry.content_title or 'Unknown'}"
                    revenue_by_content[content_key] = revenue_by_content.get(content_key, Decimal('0.00')) + entry.amount
            
            # Revenue by region
            revenue_by_region = {}
            for entry in revenue_entries:
                if entry.geographic_region:
                    region = entry.geographic_region
                    revenue_by_region[region] = revenue_by_region.get(region, Decimal('0.00')) + entry.amount
            
            # Calculate growth rate (compare with previous period)
            period_duration = period_end - period_start
            previous_start = period_start - period_duration
            previous_entries = await self.get_user_revenue(user_id, previous_start, period_start)
            
            previous_revenue = sum(entry.amount for entry in previous_entries)
            growth_rate = float((total_revenue - previous_revenue) / previous_revenue * 100) if previous_revenue > 0 else 0.0
            
            # Average per day
            days_in_period = (period_end - period_start).days or 1
            average_per_day = total_revenue / days_in_period
            
            # Top performing content
            top_performing_content = [
                {
                    'content_key': content_key,
                    'revenue': str(revenue),
                    'percentage': float(revenue / total_revenue * 100) if total_revenue > 0 else 0.0
                }
                for content_key, revenue in sorted(revenue_by_content.items(), key=lambda x: x[1], reverse=True)[:10]
            ]
            
            # Projections
            if days_in_period > 0:
                daily_average = total_revenue / days_in_period
                projected_monthly = daily_average * 30
                projected_yearly = daily_average * 365
            else:
                projected_monthly = Decimal('0.00')
                projected_yearly = Decimal('0.00')
            
            # Create analytics object
            analytics = RevenueAnalytics(
                user_id=user_id,
                period_start=period_start,
                period_end=period_end,
                total_revenue=total_revenue,
                total_fees=total_fees,
                net_revenue=net_revenue,
                revenue_by_source={k: str(v) for k, v in revenue_by_source.items()},
                revenue_by_type={k: str(v) for k, v in revenue_by_type.items()},
                revenue_by_content={k: str(v) for k, v in revenue_by_content.items()},
                revenue_by_region={k: str(v) for k, v in revenue_by_region.items()},
                growth_rate=growth_rate,
                average_per_day=average_per_day,
                top_performing_content=top_performing_content,
                projected_monthly=projected_monthly,
                projected_yearly=projected_yearly,
                generated_at=datetime.utcnow()
            )
            
            # Cache analytics for 1 hour
            self.memory_cache.set(analytics_key, analytics, ttl=3600)
            
            self._stats['analytics_generated'] += 1
            return analytics
            
        except Exception as e:
            logger.error(f"Failed to generate analytics: {e}")
            raise
    
    async def update_payment_status(self,
                                  entry_id: str,
                                  payment_status: PaymentStatus,
                                  processed_at: Optional[datetime] = None) -> bool:
        """Update payment status for revenue entry"""
        
        try:
            revenue_entry = await self.get_revenue_entry(entry_id)
            if not revenue_entry:
                return False
            
            # Update payment status
            revenue_entry.payment_status = payment_status
            if processed_at:
                revenue_entry.processed_at = processed_at
            elif payment_status == PaymentStatus.COMPLETED:
                revenue_entry.processed_at = datetime.utcnow()
            
            # Store updated entry
            entry_key = f"{self.REVENUE_PREFIX}:{entry_id}"
            await self.redis_cache.set(
                entry_key,
                json.dumps(revenue_entry.to_dict()),
                ttl=86400 * 30 * self.retention_months
            )
            
            # Update memory cache
            cache_key = f"revenue_entry:{entry_id}"
            self.memory_cache.set(cache_key, revenue_entry, ttl=300)
            
            # Update statistics
            if payment_status == PaymentStatus.COMPLETED:
                self._stats['payments_processed'] += 1
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update payment status: {e}")
            return False
    
    async def queue_payment(self,
                          user_id: str,
                          amount: Decimal,
                          currency: str,
                          payment_method: str,
                          entry_ids: List[str]) -> str:
        """Queue payment for processing"""
        
        try:
            import uuid
            payment_id = str(uuid.uuid4())
            
            payment_data = {
                'payment_id': payment_id,
                'user_id': user_id,
                'amount': str(amount),
                'currency': currency,
                'payment_method': payment_method,
                'entry_ids': entry_ids,
                'queued_at': datetime.utcnow().isoformat(),
                'status': PaymentStatus.PENDING.value
            }
            
            payment_key = f"{self.PAYMENT_QUEUE_PREFIX}:{payment_id}"
            await self.redis_cache.set(
                payment_key,
                json.dumps(payment_data),
                ttl=86400 * 7  # 7 days
            )
            
            return payment_id
            
        except Exception as e:
            logger.error(f"Failed to queue payment: {e}")
            return ""
    
    async def _update_user_revenue_index(self, user_id: str, entry_id: str, period_start: datetime):
        """Update user revenue index"""
        
        user_key = f"{self.USER_REVENUE_PREFIX}:{user_id}"
        index_data = await self.redis_cache.get(user_key)
        
        if index_data:
            entry_index = json.loads(index_data)
        else:
            entry_index = []
        
        # Add new entry
        entry_index.append({
            'entry_id': entry_id,
            'period_start': period_start.isoformat()
        })
        
        # Keep only recent entries (limit to 10000 entries)
        entry_index = entry_index[-10000:]
        
        await self.redis_cache.set(
            user_key,
            json.dumps(entry_index),
            ttl=86400 * 30 * self.retention_months
        )
    
    async def _update_content_revenue_index(self, content_id: str, entry_id: str, amount: Decimal, currency: str):
        """Update content revenue index"""
        
        content_key = f"{self.CONTENT_REVENUE_PREFIX}:{content_id}"
        revenue_data = await self.redis_cache.get(content_key)
        
        if revenue_data:
            content_revenue = json.loads(revenue_data)
        else:
            content_revenue = {
                'content_id': content_id,
                'total_revenue': '0.00',
                'currency': currency,
                'entry_count': 0,
                'last_updated': datetime.utcnow().isoformat()
            }
        
        # Update totals
        current_total = Decimal(content_revenue['total_revenue'])
        content_revenue['total_revenue'] = str(current_total + amount)
        content_revenue['entry_count'] += 1
        content_revenue['last_updated'] = datetime.utcnow().isoformat()
        
        await self.redis_cache.set(
            content_key,
            json.dumps(content_revenue),
            ttl=86400 * 30 * self.retention_months
        )
    
    async def _update_daily_totals(self, user_id: str, date: datetime, amount: Decimal, currency: str, source: RevenueSource):
        """Update daily revenue totals"""
        
        date_key = date.strftime('%Y-%m-%d')
        daily_key = f"{self.DAILY_TOTALS_PREFIX}:{user_id}:{date_key}"
        
        daily_data = await self.redis_cache.get(daily_key)
        if daily_data:
            totals = json.loads(daily_data)
        else:
            totals = {
                'date': date_key,
                'total_amount': '0.00',
                'currency': currency,
                'by_source': {}
            }
        
        # Update totals
        current_total = Decimal(totals['total_amount'])
        totals['total_amount'] = str(current_total + amount)
        
        source_key = source.value
        current_source = Decimal(totals['by_source'].get(source_key, '0.00'))
        totals['by_source'][source_key] = str(current_source + amount)
        
        await self.redis_cache.set(daily_key, json.dumps(totals), ttl=86400 * 90)  # 90 days
    
    async def _update_monthly_totals(self, user_id: str, date: datetime, amount: Decimal, currency: str, source: RevenueSource):
        """Update monthly revenue totals"""
        
        month_key = date.strftime('%Y-%m')
        monthly_key = f"{self.MONTHLY_TOTALS_PREFIX}:{user_id}:{month_key}"
        
        monthly_data = await self.redis_cache.get(monthly_key)
        if monthly_data:
            totals = json.loads(monthly_data)
        else:
            totals = {
                'month': month_key,
                'total_amount': '0.00',
                'currency': currency,
                'by_source': {}
            }
        
        # Update totals
        current_total = Decimal(totals['total_amount'])
        totals['total_amount'] = str(current_total + amount)
        
        source_key = source.value
        current_source = Decimal(totals['by_source'].get(source_key, '0.00'))
        totals['by_source'][source_key] = str(current_source + amount)
        
        await self.redis_cache.set(monthly_key, json.dumps(totals), ttl=86400 * 730)  # 2 years
    
    async def _update_platform_totals(self, source: RevenueSource, amount: Decimal, currency: str, date: datetime):
        """Update platform-wide totals"""
        
        date_key = date.strftime('%Y-%m-%d')
        platform_key = f"{self.PLATFORM_TOTALS_PREFIX}:{source.value}:{date_key}"
        
        platform_data = await self.redis_cache.get(platform_key)
        if platform_data:
            totals = json.loads(platform_data)
        else:
            totals = {
                'source': source.value,
                'date': date_key,
                'total_amount': '0.00',
                'currency': currency,
                'user_count': 0
            }
        
        current_total = Decimal(totals['total_amount'])
        totals['total_amount'] = str(current_total + amount)
        
        await self.redis_cache.set(platform_key, json.dumps(totals), ttl=86400 * 365)  # 1 year
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        redis_stats = await self.redis_cache.get_stats()
        memory_stats = self.memory_cache.get_stats()
        
        # Convert Decimal to string for JSON serialization
        revenue_stats = {}
        for key, value in self._stats.items():
            if isinstance(value, Decimal):
                revenue_stats[key] = str(value)
            else:
                revenue_stats[key] = value
        
        return {
            'revenue_stats': revenue_stats,
            'redis_stats': redis_stats,
            'memory_stats': memory_stats,
            'default_currency': self.default_currency,
            'retention_months': self.retention_months,
            'supported_sources': [source.value for source in RevenueSource],
            'supported_types': [rev_type.value for rev_type in RevenueType]
        }
    
    async def close(self):
        """Close cache connections"""
        await self.redis_cache.close()
        self.memory_cache.close()

class MonetizationCache(RevenueCache):
    """
    Specialized cache for monetization strategies and optimization
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Additional prefixes for monetization
        self.OPTIMIZATION_PREFIX = "monetization:optimization"
        self.STRATEGY_PREFIX = "monetization:strategy"
        self.FORECAST_PREFIX = "monetization:forecast"
    
    async def store_optimization_result(self,
                                      user_id: str,
                                      strategy: str,
                                      improvement: float,
                                      recommendations: List[str]) -> bool:
        """Store monetization optimization results"""
        
        try:
            optimization_key = f"{self.OPTIMIZATION_PREFIX}:{user_id}"
            
            optimization_data = {
                'user_id': user_id,
                'strategy': strategy,
                'improvement_percentage': improvement,
                'recommendations': recommendations,
                'generated_at': datetime.utcnow().isoformat()
            }
            
            await self.redis_cache.set(
                optimization_key,
                json.dumps(optimization_data),
                ttl=86400 * 7  # 7 days
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to store optimization result: {e}")
            return False
    
    async def get_optimization_recommendations(self, user_id: str) -> Dict[str, Any]:
        """Get monetization optimization recommendations"""
        
        optimization_key = f"{self.OPTIMIZATION_PREFIX}:{user_id}"
        optimization_data = await self.redis_cache.get(optimization_key)
        
        if optimization_data:
            return json.loads(optimization_data)
        
        return {}
    
    async def store_revenue_forecast(self,
                                   user_id: str,
                                   forecast_data: Dict[str, Any],
                                   confidence_level: float) -> bool:
        """Store revenue forecast"""
        
        try:
            forecast_key = f"{self.FORECAST_PREFIX}:{user_id}"
            
            forecast_info = {
                'user_id': user_id,
                'forecast_data': forecast_data,
                'confidence_level': confidence_level,
                'generated_at': datetime.utcnow().isoformat()
            }
            
            await self.redis_cache.set(
                forecast_key,
                json.dumps(forecast_info),
                ttl=86400 * 30  # 30 days
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to store forecast: {e}")
            return False
    
    async def get_revenue_forecast(self, user_id: str) -> Dict[str, Any]:
        """Get revenue forecast"""
        
        forecast_key = f"{self.FORECAST_PREFIX}:{user_id}"
        forecast_data = await self.redis_cache.get(forecast_key)
        
        if forecast_data:
            return json.loads(forecast_data)
        
        return {}
