"""Advanced Revenue Tracking and Analytics Processor
Professional Industrial Financial Data Management Engine

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 IA Influencer Agent Platform
License: Proprietary - All Rights Reserved

WARNING: This code is proprietary and confidential. Any unauthorized copying,
distribution, or use without explicit written permission from Fahed Mlaiel
is strictly prohibited and may result in legal action.
"""

import asyncio
import json
import logging
from datetime import datetime, timezone, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional, Union, Tuple, Any
from enum import Enum
import pandas as pd
import numpy as np
from dataclasses import dataclass

from backend.core.database import get_database
from backend.core.exceptions import ProcessingError, ValidationError
from backend.core.security import SecurityManager
from backend.utils.notifications import NotificationManager
from backend.utils.analytics import AnalyticsEngine

logger = logging.getLogger(__name__)


class RevenueType(Enum):
    """
Revenue type enumeration"""

    STREAMING = "streaming"
    LICENSING = "licensing"
    SYNC = "synchronization"
    MECHANICAL = "mechanical"
    PERFORMANCE = "performance"
    DIGITAL_SALES = "digital_sales"
    PHYSICAL_SALES = "physical_sales"
    MERCHANDISING = "merchandising"
    SPONSORSHIP = "sponsorship"
    COLLABORATION = "collaboration"
    SUBSCRIPTION = "subscription"
    AD_REVENUE = "ad_revenue"
    NFT_SALES = "nft_sales"
    OTHER = "other"


class PaymentStatus(Enum):
    """Payment status enumeration"""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    DISPUTED = "disputed"
    REFUNDED = "refunded"


@dataclass
class RevenueRecord:
    """Revenue record data structure"""
    id: str
    user_id: str
    content_id: str
    platform: str
    revenue_type: RevenueType
    gross_amount: Decimal
    net_amount: Decimal
    currency: str
    exchange_rate: Decimal
    platform_fee: Decimal
    service_fee: Decimal
    tax_amount: Decimal
    payment_status: PaymentStatus
    transaction_date: datetime
    settlement_date: Optional[datetime]
    reference_id: str
    metadata: Dict[str, Any]


class RevenueTrackingProcessor:
    """
Advanced revenue tracking and analytics processor"""
    
    def __init__(self):
        self.db = get_database()
        self.security = SecurityManager()
        self.notifications = NotificationManager()
        self.analytics = AnalyticsEngine()
        
        # Platform commission rates
        self.platform_rates = {
            'spotify': Decimal('0.70'),
            'apple_music': Decimal('0.68'),
            'youtube': Decimal('0.55'),
            'soundcloud': Decimal('0.85'),
            'bandcamp': Decimal('0.90'),
            'beatport': Decimal('0.70'),
            'amazon_music': Decimal('0.73'),
            'tidal': Decimal('0.75'),
            'deezer': Decimal('0.71'),
            'pandora': Decimal('0.60'),
            'generic': Decimal('0.70')
        }
        
        # Currency exchange API settings
        self.base_currency = 'USD'
        self.supported_currencies = [
            'USD', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD', 'CHF', 'CNY', 'SEK', 'NZD'
        ]

    async def process_revenue_data(
        self,
        raw_data: Dict[str, Any],
        platform: str,
        user_id: str
    ) -> List[RevenueRecord]:
        """
Process raw revenue data from various platforms"""
        try:
            logger.info(f"Processing revenue data for user {user_id} from {platform}")
            
            # Validate input data
            await self._validate_revenue_data(raw_data, platform, user_id)
            
            # Parse platform-specific data format
            parsed_records = await self._parse_platform_data(raw_data, platform, user_id)
            
            # Process each record
            processed_records = []
            for record_data in parsed_records:
                processed_record = await self._process_single_record(record_data, platform)
                processed_records.append(processed_record)
            
            # Store in database
            await self._store_revenue_records(processed_records)
            
            # Update analytics
            await self._update_revenue_analytics(processed_records, user_id)
            
            # Send notifications if needed
            await self._check_revenue_notifications(processed_records, user_id)
            
            return processed_records
            
        except Exception as e:
            logger.error(f"Error processing revenue data: {str(e)}")
            raise ProcessingError(f"Revenue processing failed: {str(e)}")

    async def _validate_revenue_data(
        self,
        raw_data: Dict[str, Any],
        platform: str,
        user_id: str
    ) -> None:
        """Validate incoming revenue data"""
        if not raw_data:
            raise ValidationError("Revenue data cannot be empty")
        
        if not platform:
            raise ValidationError("Platform must be specified")
        
        if not user_id:
            raise ValidationError("User ID must be specified")
        
        # Platform-specific validation
        required_fields = self._get_required_fields(platform)
        
        if isinstance(raw_data, list):
            for record in raw_data:
                for field in required_fields:
                    if field not in record:
                        raise ValidationError(f"Required field '{field}' missing from record")
        else:
            for field in required_fields:
                if field not in raw_data:
                    raise ValidationError(f"Required field '{field}' missing")

    def _get_required_fields(self, platform: str) -> List[str]:
        """Get required fields for platform data"""
        base_fields = ['amount', 'currency', 'date', 'content_id']
        
        platform_fields = {
            'spotify': base_fields + ['streams', 'country'],
            'apple_music': base_fields + ['plays', 'territory'],
            'youtube': base_fields + ['views', 'watch_time'],
            'soundcloud': base_fields + ['plays'],
            'bandcamp': base_fields + ['sales_type'],
            'generic': base_fields
        }
        
        return platform_fields.get(platform, base_fields)

    async def _parse_platform_data(
        self,
        raw_data: Dict[str, Any],
        platform: str,
        user_id: str
    ) -> List[Dict[str, Any]]:
        """
Parse platform-specific data format"""
        try:
            if platform == 'spotify':
                return await self._parse_spotify_data(raw_data, user_id)
            elif platform == 'apple_music':
                return await self._parse_apple_music_data(raw_data, user_id)
            elif platform == 'youtube':
                return await self._parse_youtube_data(raw_data, user_id)
            elif platform == 'soundcloud':
                return await self._parse_soundcloud_data(raw_data, user_id)
            elif platform == 'bandcamp':
                return await self._parse_bandcamp_data(raw_data, user_id)
            else:
                return await self._parse_generic_data(raw_data, user_id)
                
        except Exception as e:
            logger.error(f"Error parsing {platform} data: {str(e)}")
            raise ProcessingError(f"Data parsing failed for {platform}: {str(e)}")

    async def _parse_spotify_data(self, data: Dict, user_id: str) -> List[Dict]:
        """Parse Spotify streaming data"""
        records = []
        
        # Handle different Spotify data formats
        if 'reports' in data:
            for report in data['reports']:
                for row in report.get('rows', []):
                    record = {
                        'user_id': user_id,
                        'content_id': row.get('track_id') or row.get('isrc'),
                        'title': row.get('track_name'),
                        'artist': row.get('artist_name'),
                        'streams': int(row.get('streams', 0)),
                        'gross_amount': Decimal(str(row.get('royalties', 0))),
                        'currency': row.get('currency', 'USD'),
                        'country': row.get('country'),
                        'date': self._parse_date(row.get('date')),
                        'revenue_type': RevenueType.STREAMING,
                        'platform_specific': {
                            'streams': row.get('streams'),
                            'country': row.get('country'),
                            'subscription_type': row.get('subscription_type')
                        }
                    }
                    records.append(record)
        
        return records

    async def _parse_apple_music_data(self, data: Dict, user_id: str) -> List[Dict]:
        """
Parse Apple Music data"""
        records = []
        
        if 'data' in data:
            for item in data['data']:
                record = {
                    'user_id': user_id,
                    'content_id': item.get('adam_id') or item.get('isrc'),
                    'title': item.get('title'),
                    'artist': item.get('artist'),
                    'plays': int(item.get('plays', 0)),
                    'gross_amount': Decimal(str(item.get('royalty', 0))),
                    'currency': item.get('currency', 'USD'),
                    'territory': item.get('territory'),
                    'date': self._parse_date(item.get('start_date')),
                    'revenue_type': RevenueType.STREAMING,
                    'platform_specific': {
                        'plays': item.get('plays'),
                        'territory': item.get('territory'),
                        'subscription_type': item.get('subscription_type')
                    }
                }
                records.append(record)
        
        return records

    async def _parse_youtube_data(self, data: Dict, user_id: str) -> List[Dict]:
        """
Parse YouTube analytics data"""
        records = []
        
        if 'rows' in data:
            for row in data['rows']:
                record = {
                    'user_id': user_id,
                    'content_id': row.get('video_id'),
                    'title': row.get('video_title'),
                    'views': int(row.get('views', 0)),
                    'watch_time': float(row.get('watch_time_minutes', 0)),
                    'gross_amount': Decimal(str(row.get('estimated_revenue', 0))),
                    'currency': 'USD',  # YouTube typically reports in USD
                    'date': self._parse_date(row.get('date')),
                    'revenue_type': RevenueType.AD_REVENUE,
                    'platform_specific': {
                        'views': row.get('views'),
                        'watch_time_minutes': row.get('watch_time_minutes'),
                        'cpm': row.get('cpm'),
                        'rpm': row.get('rpm')
                    }
                }
                records.append(record)
        
        return records

    async def _parse_soundcloud_data(self, data: Dict, user_id: str) -> List[Dict]:
        """
Parse SoundCloud data"""
        records = []
        
        if 'tracks' in data:
            for track in data['tracks']:
                record = {
                    'user_id': user_id,
                    'content_id': str(track.get('id')),
                    'title': track.get('title'),
                    'plays': int(track.get('playback_count', 0)),
                    'gross_amount': Decimal(str(track.get('revenue', 0))),
                    'currency': track.get('currency', 'USD'),
                    'date': self._parse_date(track.get('created_at')),
                    'revenue_type': RevenueType.STREAMING,
                    'platform_specific': {
                        'plays': track.get('playback_count'),
                        'likes': track.get('likes_count'),
                        'reposts': track.get('reposts_count')
                    }
                }
                records.append(record)
        
        return records

    async def _parse_bandcamp_data(self, data: Dict, user_id: str) -> List[Dict]:
        """
Parse Bandcamp sales data"""
        records = []
        
        if 'sales' in data:
            for sale in data['sales']:
                record = {
                    'user_id': user_id,
                    'content_id': sale.get('item_id'),
                    'title': sale.get('item_title'),
                    'sales_type': sale.get('item_type'),  # album, track, merchandise
                    'gross_amount': Decimal(str(sale.get('amount', 0))),
                    'currency': sale.get('currency', 'USD'),
                    'date': self._parse_date(sale.get('sale_date')),
                    'revenue_type': self._determine_bandcamp_revenue_type(sale.get('item_type')),
                    'platform_specific': {
                        'item_type': sale.get('item_type'),
                        'quantity': sale.get('quantity', 1),
                        'discount': sale.get('discount'),
                        'fan_id': sale.get('fan_id')
                    }
                }
                records.append(record)
        
        return records

    async def _parse_generic_data(self, data: Dict, user_id: str) -> List[Dict]:
        """
Parse generic revenue data format"""
        records = []
        
        # Handle both single record and array of records
        items = data if isinstance(data, list) else [data]
        
        for item in items:
            record = {
                'user_id': user_id,
                'content_id': item.get('content_id'),
                'title': item.get('title'),
                'gross_amount': Decimal(str(item.get('amount', 0))),
                'currency': item.get('currency', 'USD'),
                'date': self._parse_date(item.get('date')),
                'revenue_type': RevenueType(item.get('revenue_type', 'other')),
                'platform_specific': item.get('metadata', {})
            }
            records.append(record)
        
        return records

    def _determine_bandcamp_revenue_type(self, item_type: str) -> RevenueType:
        """
Determine revenue type based on Bandcamp item type"""
        if item_type in ['track', 'album']:
            return RevenueType.DIGITAL_SALES
        elif item_type in ['vinyl', 'cd', 'cassette']:
            return RevenueType.PHYSICAL_SALES
        elif item_type in ['shirt', 'poster', 'merchandise']:
            return RevenueType.MERCHANDISING
        else:
            return RevenueType.OTHER

    def _parse_date(self, date_str: Union[str, datetime, None]) -> datetime:
        """
Parse date from various formats"""
        if not date_str:
            return datetime.now(timezone.utc)
        
        if isinstance(date_str, datetime):
            return date_str if date_str.tzinfo else date_str.replace(tzinfo=timezone.utc)
        
        # Try different date formats
        formats = [
            '%Y-%m-%d',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%SZ',
            '%Y-%m-%dT%H:%M:%S.%fZ',
            '%d/%m/%Y',
            '%m/%d/%Y'
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.replace(tzinfo=timezone.utc)
            except ValueError:
                continue
        
        # Fallback to current time
        logger.warning(f"Could not parse date: {date_str}, using current time")
        return datetime.now(timezone.utc)

    async def _process_single_record(
        self,
        record_data: Dict[str, Any],
        platform: str
    ) -> RevenueRecord:
        """Process a single revenue record"""
        try:
            # Generate unique ID
            record_id = self._generate_record_id(record_data, platform)
            
            # Get exchange rate
            exchange_rate = await self._get_exchange_rate(
                record_data['currency'],
                self.base_currency,
                record_data['date']
            )
            
            # Calculate amounts
            gross_amount = record_data['gross_amount']
            platform_fee = await self._calculate_platform_fee(gross_amount, platform)
            service_fee = await self._calculate_service_fee(gross_amount)
            tax_amount = await self._calculate_tax(gross_amount, record_data.get('country'))
            net_amount = gross_amount - platform_fee - service_fee - tax_amount
            
            # Create revenue record
            record = RevenueRecord(
                id=record_id,
                user_id=record_data['user_id'],
                content_id=record_data['content_id'],
                platform=platform,
                revenue_type=record_data['revenue_type'],
                gross_amount=gross_amount,
                net_amount=net_amount,
                currency=record_data['currency'],
                exchange_rate=exchange_rate,
                platform_fee=platform_fee,
                service_fee=service_fee,
                tax_amount=tax_amount,
                payment_status=PaymentStatus.PENDING,
                transaction_date=record_data['date'],
                settlement_date=None,
                reference_id=record_data.get('reference_id', ''),
                metadata={
                    'title': record_data.get('title'),
                    'artist': record_data.get('artist'),
                    'platform_specific': record_data.get('platform_specific', {}),
                    'processed_at': datetime.now(timezone.utc).isoformat()
                }
            )
            
            return record
            
        except Exception as e:
            logger.error(f"Error processing record: {str(e)}")
            raise ProcessingError(f"Record processing failed: {str(e)}")

    def _generate_record_id(self, record_data: Dict, platform: str) -> str:
        """Generate unique record ID"""
        import hashlib
        
        # Create hash from key fields
        key_fields = [
            record_data['user_id'],
            record_data['content_id'],
            platform,
            record_data['date'].isoformat(),
            str(record_data['gross_amount'])
        ]
        
        hash_input = '|'.join(key_fields)
        return hashlib.sha256(hash_input.encode()).hexdigest()[:16]

    async def _get_exchange_rate(
        self,
        from_currency: str,
        to_currency: str,
        date: datetime
    ) -> Decimal:
        """
Get exchange rate for currency conversion"""
        if from_currency == to_currency:
            return Decimal('1.0')
        
        try:
            # Check cache first
            cache_key = f"exchange_rate:{from_currency}:{to_currency}:{date.date()}"
            cached_rate = await self._get_cached_exchange_rate(cache_key)
            
            if cached_rate:
                return cached_rate
            
            # Fetch from external API (implement your preferred provider)
            rate = await self._fetch_exchange_rate(from_currency, to_currency, date)
            
            # Cache the result
            await self._cache_exchange_rate(cache_key, rate)
            
            return rate
            
        except Exception as e:
            logger.warning(f"Could not get exchange rate, using 1.0: {str(e)}")
            return Decimal('1.0')

    async def _fetch_exchange_rate(
        self,
        from_currency: str,
        to_currency: str,
        date: datetime
    ) -> Decimal:
        """Fetch exchange rate from external API"""
        # This would integrate with your preferred exchange rate API
        # For now, return a placeholder
        return Decimal('1.0')

    async def _get_cached_exchange_rate(self, cache_key: str) -> Optional[Decimal]:
        """
Get cached exchange rate if available and not expired"""
        try:
            import json
            
            # Try Redis first if available
            if hasattr(self, 'redis_client') and self.redis_client:
                cached_data = await self.redis_client.get(cache_key)
                if cached_data:
                    data = json.loads(cached_data)
                    return Decimal(data["rate"])
            
            # Fallback to in-memory cache
            if hasattr(self, '_rate_cache') and cache_key in self._rate_cache:
                cache_entry = self._rate_cache[cache_key]
                if time.time() < cache_entry.get("expires_at", 0):
                    return Decimal(cache_entry["rate"])
                else:
                    # Remove expired entry
                    del self._rate_cache[cache_key]
            
            return None
            
        except Exception as e:
            logger.warning(f"Failed to get cached exchange rate: {e}")
            return None

    async def _cache_exchange_rate(self, cache_key: str, rate: Decimal) -> None:
        """Cache exchange rate with expiration"""
        try:
            import redis.asyncio as redis
            import json
            
            # Cache for 1 hour (3600 seconds)
            cache_data = {
                "rate": str(rate),
                "timestamp": time.time(),
                "source": "exchange_api"
            }
            
            # Use Redis if available, otherwise use in-memory cache
            if hasattr(self, 'redis_client') and self.redis_client:
                await self.redis_client.setex(
                    cache_key,
                    3600,  # 1 hour expiration
                    json.dumps(cache_data)
                )
            else:
                # Fallback to in-memory cache
                if not hasattr(self, '_rate_cache'):
                    self._rate_cache = {}
                self._rate_cache[cache_key] = {
                    **cache_data,
                    "expires_at": time.time() + 3600
                }
                
            logger.debug(f"Cached exchange rate {rate} for key {cache_key}")
            
        except Exception as e:
            logger.warning(f"Failed to cache exchange rate: {e}")
            # Cache failure shouldn't break the main flow

    async def _calculate_platform_fee(self, amount: Decimal, platform: str) -> Decimal:
        """Calculate platform commission fee"""
        rate = self.platform_rates.get(platform, self.platform_rates['generic'])
        platform_commission = Decimal('1.0') - rate
        return (amount * platform_commission).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    async def _calculate_service_fee(self, amount: Decimal) -> Decimal:
        """
Calculate our service fee"""
        service_rate = Decimal('0.05')  # 5% service fee
        return (amount * service_rate).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    async def _calculate_tax(self, amount: Decimal, country: Optional[str]) -> Decimal:
        """
Calculate tax amount based on jurisdiction"""
        # This would implement tax calculation based on user location
        # For now, return 0 as taxes are typically handled separately
        return Decimal('0.00')

    async def _store_revenue_records(self, records: List[RevenueRecord]) -> None:
        """
Store revenue records in database"""
        try:
            query = """
            INSERT INTO revenue_records (
                id, user_id, content_id, platform, revenue_type,
                gross_amount, net_amount, currency, exchange_rate,
                platform_fee, service_fee, tax_amount, payment_status,
                transaction_date, settlement_date, reference_id, metadata,
                created_at, updated_at
            ) VALUES (
                $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13,
                $14, $15, $16, $17, NOW(), NOW()
            ) ON CONFLICT (id) DO UPDATE SET
                gross_amount = EXCLUDED.gross_amount,
                net_amount = EXCLUDED.net_amount,
                payment_status = EXCLUDED.payment_status,
                settlement_date = EXCLUDED.settlement_date,
                metadata = EXCLUDED.metadata,
                updated_at = NOW()
            """
            
            for record in records:
                await self.db.execute(
                    query,
                    record.id,
                    record.user_id,
                    record.content_id,
                    record.platform,
                    record.revenue_type.value,
                    float(record.gross_amount),
                    float(record.net_amount),
                    record.currency,
                    float(record.exchange_rate),
                    float(record.platform_fee),
                    float(record.service_fee),
                    float(record.tax_amount),
                    record.payment_status.value,
                    record.transaction_date,
                    record.settlement_date,
                    record.reference_id,
                    json.dumps(record.metadata)
                )
            
            logger.info(f"Stored {len(records)} revenue records")
            
        except Exception as e:
            logger.error(f"Error storing revenue records: {str(e)}")
            raise ProcessingError(f"Revenue storage failed: {str(e)}")

    async def _update_revenue_analytics(
        self,
        records: List[RevenueRecord],
        user_id: str
    ) -> None:
        """Update revenue analytics and aggregations"""
        try:
            # Update daily aggregations
            await self._update_daily_aggregations(records, user_id)
            
            # Update monthly aggregations
            await self._update_monthly_aggregations(records, user_id)
            
            # Update platform statistics
            await self._update_platform_statistics(records, user_id)
            
            # Update content performance metrics
            await self._update_content_metrics(records, user_id)
            
        except Exception as e:
            logger.error(f"Error updating revenue analytics: {str(e)}")

    async def _update_daily_aggregations(
        self,
        records: List[RevenueRecord],
        user_id: str
    ) -> None:
        """Update daily revenue aggregations"""
        daily_data = {}
        
        for record in records:
            date_key = record.transaction_date.date()
            if date_key not in daily_data:
                daily_data[date_key] = {
                    'gross_revenue': Decimal('0'),
                    'net_revenue': Decimal('0'),
                    'platform_fees': Decimal('0'),
                    'service_fees': Decimal('0'),
                    'record_count': 0
                }
            
            daily_data[date_key]['gross_revenue'] += record.gross_amount
            daily_data[date_key]['net_revenue'] += record.net_amount
            daily_data[date_key]['platform_fees'] += record.platform_fee
            daily_data[date_key]['service_fees'] += record.service_fee
            daily_data[date_key]['record_count'] += 1
        
        # Store daily aggregations
        for date, data in daily_data.items():
            await self._upsert_daily_aggregation(user_id, date, data)

    async def _upsert_daily_aggregation(
        self,
        user_id: str,
        date: datetime.date,
        data: Dict[str, Any]
    ) -> None:
        """
Upsert daily aggregation record"""
        query = """
        INSERT INTO revenue_daily_aggregations (
            user_id, date, gross_revenue, net_revenue,
            platform_fees, service_fees, record_count, updated_at
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, NOW())
        ON CONFLICT (user_id, date) DO UPDATE SET
            gross_revenue = EXCLUDED.gross_revenue,
            net_revenue = EXCLUDED.net_revenue,
            platform_fees = EXCLUDED.platform_fees,
            service_fees = EXCLUDED.service_fees,
            record_count = EXCLUDED.record_count,
            updated_at = NOW()
        """
        
        await self.db.execute(
            query,
            user_id,
            date,
            float(data['gross_revenue']),
            float(data['net_revenue']),
            float(data['platform_fees']),
            float(data['service_fees']),
            data['record_count']
        )

    async def _check_revenue_notifications(
        self,
        records: List[RevenueRecord],
        user_id: str
    ) -> None:
        """
Check if revenue notifications should be sent"""
        try:
            # Calculate total revenue from this batch
            total_revenue = sum(record.net_amount for record in records)
            
            # Check for milestone notifications
            milestones = [100, 500, 1000, 5000, 10000]
            
            for milestone in milestones:
                if total_revenue >= milestone:
                    await self.notifications.send_revenue_milestone(
                        user_id,
                        milestone,
                        total_revenue
                    )
            
            # Check for unusual activity
            if len(records) > 100:  # Large batch
                await self.notifications.send_revenue_alert(
                    user_id,
                    f"Large revenue batch processed: {len(records)} records"
                )
            
        except Exception as e:
            logger.error(f"Error checking revenue notifications: {str(e)}")

    async def get_revenue_summary(
        self,
        user_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        platform: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get comprehensive revenue summary for user"""
        try:
            # Set default date range
            if not end_date:
                end_date = datetime.now(timezone.utc)
            if not start_date:
                start_date = end_date - timedelta(days=30)
            
            # Build query conditions
            conditions = ["user_id = $1", "transaction_date >= $2", "transaction_date <= $3"]
            params = [user_id, start_date, end_date]
            
            if platform:
                conditions.append("platform = $4")
                params.append(platform)
            
            where_clause = " AND ".join(conditions)
            
            # Get summary statistics
            query = f"""
            SELECT 
                COUNT(*) as total_records,
                SUM(gross_amount) as total_gross,
                SUM(net_amount) as total_net,
                SUM(platform_fee) as total_platform_fees,
                SUM(service_fee) as total_service_fees,
                AVG(gross_amount) as avg_gross,
                platform,
                revenue_type
            FROM revenue_records
            WHERE {where_clause}
            GROUP BY platform, revenue_type
            ORDER BY total_gross DESC
            """
            
            rows = await self.db.fetch(query, *params)
            
            # Format results
            summary = {
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                },
                'totals': {
                    'records': 0,
                    'gross_revenue': Decimal('0'),
                    'net_revenue': Decimal('0'),
                    'platform_fees': Decimal('0'),
                    'service_fees': Decimal('0')
                },
                'by_platform': {},
                'by_revenue_type': {}
            }
            
            for row in rows:
                # Update totals
                summary['totals']['records'] += row['total_records']
                summary['totals']['gross_revenue'] += Decimal(str(row['total_gross'] or 0))
                summary['totals']['net_revenue'] += Decimal(str(row['total_net'] or 0))
                summary['totals']['platform_fees'] += Decimal(str(row['total_platform_fees'] or 0))
                summary['totals']['service_fees'] += Decimal(str(row['total_service_fees'] or 0))
                
                # Platform breakdown
                platform_key = row['platform']
                if platform_key not in summary['by_platform']:
                    summary['by_platform'][platform_key] = {
                        'records': 0,
                        'gross_revenue': Decimal('0'),
                        'net_revenue': Decimal('0')
                    }
                
                summary['by_platform'][platform_key]['records'] += row['total_records']
                summary['by_platform'][platform_key]['gross_revenue'] += Decimal(str(row['total_gross'] or 0))
                summary['by_platform'][platform_key]['net_revenue'] += Decimal(str(row['total_net'] or 0))
                
                # Revenue type breakdown
                revenue_type = row['revenue_type']
                if revenue_type not in summary['by_revenue_type']:
                    summary['by_revenue_type'][revenue_type] = {
                        'records': 0,
                        'gross_revenue': Decimal('0'),
                        'net_revenue': Decimal('0')
                    }
                
                summary['by_revenue_type'][revenue_type]['records'] += row['total_records']
                summary['by_revenue_type'][revenue_type]['gross_revenue'] += Decimal(str(row['total_gross'] or 0))
                summary['by_revenue_type'][revenue_type]['net_revenue'] += Decimal(str(row['total_net'] or 0))
            
            # Convert Decimals to float for JSON serialization
            summary = self._convert_decimals_to_float(summary)
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting revenue summary: {str(e)}")
            raise ProcessingError(f"Revenue summary failed: {str(e)}")

    def _convert_decimals_to_float(self, obj: Any) -> Any:
        """Recursively convert Decimal objects to float"""
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, dict):
            return {k: self._convert_decimals_to_float(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_decimals_to_float(item) for item in obj]
        else:
            return obj

    async def cleanup_old_records(self, days_old: int = 2555) -> int:
        """
Clean up old revenue records"""
        try:
            query = """
            DELETE FROM revenue_records
            WHERE created_at < NOW() - INTERVAL '%s days'
            AND payment_status = 'completed'
            """
            
            result = await self.db.execute(query, days_old)
            deleted_count = result.split()[-1] if result else 0
            
            logger.info(f"Cleaned up {deleted_count} old revenue records")
            return int(deleted_count)
            
        except Exception as e:
            logger.error(f"Error cleaning up revenue records: {str(e)}")
            raise ProcessingError(f"Revenue cleanup failed: {str(e)}")
