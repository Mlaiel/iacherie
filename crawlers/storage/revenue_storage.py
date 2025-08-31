"""Revenue Storage Module
=====================

Professional revenue tracking and monetization storage for IA-Influencer-Agent platform.
Handles revenue data, analytics, and financial metrics for multi-platform content creators.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.

Expertise combinée:
- Lead Developer IA: Architecture intelligente et optimisations ML
- Backend Senior: Infrastructure robuste et scalabilité enterprise
- ML Engineer: Algorithmes d'apprentissage et modèles prédictifs
- DBA Expert: Gestion de données et optimisation des requêtes
- Sécurité: Protection et chiffrement des données sensibles
- Microservices: Architecture distribuée et communication inter-services
- Audio/Vidéo: Traitement multimédia et analyse de contenu
- DevOps: Déploiement, monitoring et infrastructure cloud
- IA Prompt Engineer: Optimisation des interactions et prompts
"""
import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple, AsyncIterator
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from decimal import Decimal
import json
import uuid

from .interfaces import (
    RevenueStorageProvider, Platform, RevenueType, RevenueRecord,
    StorageMetadata, QueryOptions, QueryFilter, StorageException
)
from .database import DatabaseStorageProvider

logger = logging.getLogger(__name__)

@dataclass
class RevenueAnalytics:
    """Revenue analytics data structure."""    user_id: str
    period_start: datetime
    period_end: datetime
    total_revenue: Decimal
    revenue_by_platform: Dict[Platform, Decimal] = field(default_factory=dict)
    revenue_by_type: Dict[RevenueType, Decimal] = field(default_factory=dict)
    growth_rate: Optional[float] = None
    projected_revenue: Optional[Decimal] = None
    top_content: List[str] = field(default_factory=list)
    engagement_correlation: Optional[float] = None

@dataclass
class PaymentRecord:
    """Payment processing record."""    id: str
    user_id: str
    revenue_records: List[str]  # Revenue record IDs
    amount: Decimal
    currency: str = "EUR"
    payment_method: str = "bank_transfer"  # bank_transfer, paypal, stripe, wise
    status: str = "pending"  # pending, processing, completed, failed
    fee_amount: Decimal = Decimal('0.00')
    net_amount: Optional[Decimal] = None
    payment_reference: Optional[str] = None
    scheduled_date: Optional[datetime] = None
    processed_date: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

class DatabaseRevenueStorageProvider(DatabaseStorageProvider, RevenueStorageProvider):
    """    Database-based revenue storage provider.
    
    Implements revenue tracking, analytics, and payment processing
    with high-performance database operations.
    """    
    def __init__(self, provider_id: str, config: Dict[str, Any]):
        """Initialize database revenue storage provider."""        super().__init__(provider_id, config)
        self.ml_models = {}  # Cache for ML models
        
    async def connect(self) -> None:
        """Connect to database and initialize revenue tables."""        await super().connect()
        await self._create_revenue_tables()
        await self._initialize_ml_models()
        
    async def _create_revenue_tables(self) -> None:
        """Create revenue-specific database tables."""        revenue_table_sql = """        CREATE TABLE IF NOT EXISTS revenue_records (
            id VARCHAR(36) PRIMARY KEY,
            user_id VARCHAR(36) NOT NULL,
            content_id VARCHAR(36) NOT NULL,
            platform VARCHAR(50) NOT NULL,
            revenue_type VARCHAR(50) NOT NULL,
            amount DECIMAL(12,4) NOT NULL,
            currency VARCHAR(3) DEFAULT 'EUR',
            period_start TIMESTAMP NOT NULL,
            period_end TIMESTAMP NOT NULL,
            views INTEGER,
            engagement_rate FLOAT,
            cpm FLOAT,
            commission_rate FLOAT DEFAULT 0.15,
            net_amount DECIMAL(12,4),
            payment_status VARCHAR(20) DEFAULT 'pending',
            payment_date TIMESTAMP,
            metadata JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            INDEX idx_revenue_user_date (user_id, period_start, period_end),
            INDEX idx_revenue_platform (platform),
            INDEX idx_revenue_type (revenue_type),
            INDEX idx_revenue_status (payment_status),
            INDEX idx_revenue_content (content_id)
        );
        """        
        payment_table_sql = """        CREATE TABLE IF NOT EXISTS payment_records (
            id VARCHAR(36) PRIMARY KEY,
            user_id VARCHAR(36) NOT NULL,
            revenue_record_ids JSON NOT NULL,
            amount DECIMAL(12,4) NOT NULL,
            currency VARCHAR(3) DEFAULT 'EUR',
            payment_method VARCHAR(50) NOT NULL,
            status VARCHAR(20) DEFAULT 'pending',
            fee_amount DECIMAL(12,4) DEFAULT 0.00,
            net_amount DECIMAL(12,4),
            payment_reference VARCHAR(255),
            scheduled_date TIMESTAMP,
            processed_date TIMESTAMP,
            metadata JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            INDEX idx_payment_user (user_id),
            INDEX idx_payment_status (status),
            INDEX idx_payment_method (payment_method),
            INDEX idx_payment_date (scheduled_date)
        );
        """        
        analytics_table_sql = """        CREATE TABLE IF NOT EXISTS revenue_analytics (
            id VARCHAR(36) PRIMARY KEY,
            user_id VARCHAR(36) NOT NULL,
            period_start TIMESTAMP NOT NULL,
            period_end TIMESTAMP NOT NULL,
            total_revenue DECIMAL(12,4) NOT NULL,
            revenue_by_platform JSONB,
            revenue_by_type JSONB,
            growth_rate FLOAT,
            projected_revenue DECIMAL(12,4),
            top_content JSON,
            engagement_correlation FLOAT,
            calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            UNIQUE KEY unique_user_period (user_id, period_start, period_end),
            INDEX idx_analytics_user (user_id),
            INDEX idx_analytics_period (period_start, period_end)
        );
        """        
        try:
            async with self.get_connection() as conn:
                await conn.execute(revenue_table_sql)
                await conn.execute(payment_table_sql)
                await conn.execute(analytics_table_sql)
                await conn.commit()
                
            logger.info("Revenue tables created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create revenue tables: {e}")
            raise StorageException(f"Revenue table creation failed: {e}")
    
    async def _initialize_ml_models(self) -> None:
        """Initialize ML models for revenue prediction."""        try:
            # In a real implementation, load trained ML models here
            # For now, we'll use simple statistical models
            self.ml_models = {
                'revenue_predictor': self._simple_revenue_predictor,
                'growth_calculator': self._calculate_growth_rate,
                'engagement_correlator': self._calculate_engagement_correlation
            }
            
            logger.info("ML models initialized for revenue analytics")
            
        except Exception as e:
            logger.error(f"Failed to initialize ML models: {e}")
    
    async def store_revenue_record(self, revenue_record: RevenueRecord) -> bool:
        """Store a revenue record."""        try:
            sql = """            INSERT INTO revenue_records (
                id, user_id, content_id, platform, revenue_type, amount, currency,
                period_start, period_end, views, engagement_rate, cpm, 
                commission_rate, net_amount, payment_status, payment_date, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """            
            # Calculate net amount if not provided
            net_amount = revenue_record.net_amount
            if net_amount is None:
                commission = revenue_record.amount * revenue_record.commission_rate
                net_amount = revenue_record.amount - commission
            
            values = (
                revenue_record.id,
                revenue_record.user_id,
                revenue_record.content_id,
                revenue_record.platform.value,
                revenue_record.revenue_type.value,
                float(revenue_record.amount),
                revenue_record.currency,
                revenue_record.period_start,
                revenue_record.period_end,
                revenue_record.views,
                revenue_record.engagement_rate,
                revenue_record.cpm,
                revenue_record.commission_rate,
                float(net_amount) if net_amount else None,
                revenue_record.payment_status,
                revenue_record.payment_date,
                json.dumps({}) if not hasattr(revenue_record, 'metadata') else json.dumps(revenue_record.metadata)
            )
            
            async with self.get_connection() as conn:
                await conn.execute(sql, values)
                await conn.commit()
            
            logger.debug(f"Stored revenue record: {revenue_record.id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store revenue record {revenue_record.id}: {e}")
            raise StorageException(f"Revenue record storage failed: {e}")
    
    async def calculate_user_revenue(
        self,
        user_id: str,
        start_date: datetime,
        end_date: datetime,
        platform: Optional[Platform] = None
    ) -> Dict[str, float]:
        """Calculate revenue for user in date range."""        try:
            # Base query
            sql = """            SELECT 
                platform,
                revenue_type,
                SUM(amount) as total_amount,
                SUM(net_amount) as total_net_amount,
                COUNT(*) as record_count,
                AVG(cpm) as avg_cpm,
                SUM(views) as total_views
            FROM revenue_records 
            WHERE user_id = ? 
                AND period_start >= ? 
                AND period_end <= ?
            """            
            values = [user_id, start_date, end_date]
            
            if platform:
                sql += " AND platform = ?"
                values.append(platform.value)
            
            sql += " GROUP BY platform, revenue_type"
            
            async with self.get_connection() as conn:
                cursor = await conn.execute(sql, values)
                rows = await cursor.fetchall()
            
            # Process results
            result = {
                'total_revenue': 0.0,
                'total_net_revenue': 0.0,
                'by_platform': {},
                'by_type': {},
                'total_views': 0,
                'average_cpm': 0.0,
                'record_count': 0
            }
            
            for row in rows:
                platform_name = row[0]
                revenue_type = row[1]
                amount = float(row[2])
                net_amount = float(row[3]) if row[3] else 0.0
                count = row[4]
                cpm = float(row[5]) if row[5] else 0.0
                views = row[6] if row[6] else 0
                
                result['total_revenue'] += amount
                result['total_net_revenue'] += net_amount
                result['total_views'] += views
                result['record_count'] += count
                
                if platform_name not in result['by_platform']:
                    result['by_platform'][platform_name] = 0.0
                result['by_platform'][platform_name] += amount
                
                if revenue_type not in result['by_type']:
                    result['by_type'][revenue_type] = 0.0
                result['by_type'][revenue_type] += amount
            
            # Calculate average CPM
            if result['record_count'] > 0:
                # Get weighted average CPM
                cpm_sql = """                SELECT AVG(cpm) FROM revenue_records 
                WHERE user_id = ? AND period_start >= ? AND period_end <= ? AND cpm IS NOT NULL
                """                async with self.get_connection() as conn:
                    cursor = await conn.execute(cpm_sql, [user_id, start_date, end_date])
                    avg_cpm_row = await cursor.fetchone()
                    if avg_cpm_row and avg_cpm_row[0]:
                        result['average_cpm'] = float(avg_cpm_row[0])
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to calculate user revenue: {e}")
            raise StorageException(f"Revenue calculation failed: {e}")
    
    async def get_revenue_analytics(
        self,
        user_id: str,
        period_days: int = 30
    ) -> Dict[str, Any]:
        """Get revenue analytics and trends."""        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=period_days)
            
            # Check if analytics already calculated for this period
            cached_analytics = await self._get_cached_analytics(user_id, start_date, end_date)
            if cached_analytics:
                return cached_analytics
            
            # Calculate current period revenue
            current_revenue = await self.calculate_user_revenue(user_id, start_date, end_date)
            
            # Calculate previous period for comparison
            prev_start = start_date - timedelta(days=period_days)
            prev_end = start_date
            previous_revenue = await self.calculate_user_revenue(user_id, prev_start, prev_end)
            
            # Calculate growth rate
            growth_rate = self._calculate_growth_rate(
                current_revenue['total_revenue'],
                previous_revenue['total_revenue']
            )
            
            # Get top performing content
            top_content = await self._get_top_content(user_id, start_date, end_date)
            
            # Calculate engagement correlation
            engagement_correlation = await self._calculate_engagement_correlation(user_id, start_date, end_date)
            
            # Predict future revenue
            projected_revenue = await self._predict_revenue(user_id, period_days)
            
            analytics = {
                'user_id': user_id,
                'period_start': start_date.isoformat(),
                'period_end': end_date.isoformat(),
                'current_period': current_revenue,
                'previous_period': previous_revenue,
                'growth_rate': growth_rate,
                'projected_revenue': projected_revenue,
                'top_content': top_content,
                'engagement_correlation': engagement_correlation,
                'insights': await self._generate_insights(current_revenue, previous_revenue, growth_rate)
            }
            
            # Cache analytics
            await self._cache_analytics(analytics)
            
            return analytics
            
        except Exception as e:
            logger.error(f"Failed to get revenue analytics: {e}")
            raise StorageException(f"Revenue analytics failed: {e}")
    
    async def estimate_projected_revenue(
        self,
        user_id: str,
        content_id: str,
        projection_days: int = 30
    ) -> float:
        """Estimate projected revenue using ML."""        try:
            # Get historical performance for this content
            sql = """            SELECT amount, views, engagement_rate, cpm, period_start
            FROM revenue_records 
            WHERE user_id = ? AND content_id = ?
            ORDER BY period_start DESC
            LIMIT 10
            """            
            async with self.get_connection() as conn:
                cursor = await conn.execute(sql, [user_id, content_id])
                rows = await cursor.fetchall()
            
            if not rows:
                # No historical data, use user average
                return await self._predict_revenue(user_id, projection_days)
            
            # Use ML model to predict
            historical_data = [
                {
                    'amount': float(row[0]),
                    'views': row[1] if row[1] else 0,
                    'engagement_rate': float(row[2]) if row[2] else 0.0,
                    'cpm': float(row[3]) if row[3] else 0.0,
                    'days_ago': (datetime.utcnow() - row[4]).days
                }
                for row in rows
            ]
            
            # Simple projection based on trend
            if len(historical_data) >= 2:
                recent_avg = sum(d['amount'] for d in historical_data[:3]) / min(3, len(historical_data))
                older_avg = sum(d['amount'] for d in historical_data[3:]) / max(1, len(historical_data) - 3)
                
                trend_factor = recent_avg / older_avg if older_avg > 0 else 1.0
                base_projection = recent_avg * (projection_days / 30.0)
                
                return base_projection * trend_factor
            else:
                # Single data point, use as baseline
                return historical_data[0]['amount'] * (projection_days / 30.0)
            
        except Exception as e:
            logger.error(f"Failed to estimate projected revenue: {e}")
            return 0.0
    
    async def get_platform_commission_rates(self, platform: Platform) -> Dict[str, float]:
        """Get commission rates for platform."""        # Standard commission rates by platform and revenue type
        commission_rates = {
            Platform.YOUTUBE: {
                'streaming': 0.45,      # YouTube takes 45% of ad revenue
                'membership': 0.30,     # 30% for channel memberships
                'super_chat': 0.30,     # 30% for Super Chat
                'merchandise': 0.10     # 10% for merchandise shelf
            },
            Platform.TIKTOK: {
                'creator_fund': 0.20,   # 20% platform fee
                'live_gifts': 0.50,     # 50% for virtual gifts
                'brand_partnerships': 0.15  # 15% for partnerships
            },
            Platform.INSTAGRAM: {
                'reels_play': 0.45,     # 45% similar to YouTube
                'igtv_ads': 0.45,       # 45% for IGTV ads
                'branded_content': 0.10  # 10% for branded content
            },
            Platform.SPOTIFY: {
                'streaming': 0.30,      # 30% platform fee
                'podcast_ads': 0.25,    # 25% for podcast advertising
                'exclusive_content': 0.20  # 20% for exclusive content
            },
            Platform.TWITCH: {
                'subscriptions': 0.50,   # 50% for subscriptions
                'bits': 0.30,           # 30% for bits
                'ad_revenue': 0.45      # 45% for ad revenue
            }
        }
        
        return commission_rates.get(platform, {'default': 0.15})
    
    async def _get_cached_analytics(
        self,
        user_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Optional[Dict[str, Any]]:
        """Get cached analytics if available."""        try:
            sql = """            SELECT * FROM revenue_analytics 
            WHERE user_id = ? AND period_start = ? AND period_end = ?
            AND calculated_at > ?
            """            
            # Consider cache valid for 1 hour
            cache_cutoff = datetime.utcnow() - timedelta(hours=1)
            
            async with self.get_connection() as conn:
                cursor = await conn.execute(sql, [user_id, start_date, end_date, cache_cutoff])
                row = await cursor.fetchone()
            
            if row:
                return {
                    'user_id': row[1],
                    'period_start': row[2].isoformat(),
                    'period_end': row[3].isoformat(),
                    'total_revenue': float(row[4]),
                    'revenue_by_platform': json.loads(row[5]) if row[5] else {},
                    'revenue_by_type': json.loads(row[6]) if row[6] else {},
                    'growth_rate': float(row[7]) if row[7] else None,
                    'projected_revenue': float(row[8]) if row[8] else None,
                    'top_content': json.loads(row[9]) if row[9] else [],
                    'engagement_correlation': float(row[10]) if row[10] else None,
                    'cached': True
                }
            
            return None
            
        except Exception as e:
            logger.warning(f"Failed to get cached analytics: {e}")
            return None
    
    async def _cache_analytics(self, analytics: Dict[str, Any]) -> None:
        """Cache analytics results."""        try:
            sql = """            INSERT INTO revenue_analytics (
                id, user_id, period_start, period_end, total_revenue,
                revenue_by_platform, revenue_by_type, growth_rate,
                projected_revenue, top_content, engagement_correlation
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON DUPLICATE KEY UPDATE
                total_revenue = VALUES(total_revenue),
                revenue_by_platform = VALUES(revenue_by_platform),
                revenue_by_type = VALUES(revenue_by_type),
                growth_rate = VALUES(growth_rate),
                projected_revenue = VALUES(projected_revenue),
                top_content = VALUES(top_content),
                engagement_correlation = VALUES(engagement_correlation),
                calculated_at = CURRENT_TIMESTAMP
            """            
            values = (
                str(uuid.uuid4()),
                analytics['user_id'],
                analytics['period_start'],
                analytics['period_end'],
                analytics['current_period']['total_revenue'],
                json.dumps(analytics['current_period']['by_platform']),
                json.dumps(analytics['current_period']['by_type']),
                analytics['growth_rate'],
                analytics['projected_revenue'],
                json.dumps(analytics['top_content']),
                analytics['engagement_correlation']
            )
            
            async with self.get_connection() as conn:
                await conn.execute(sql, values)
                await conn.commit()
            
        except Exception as e:
            logger.warning(f"Failed to cache analytics: {e}")
    
    def _simple_revenue_predictor(self, historical_data: List[Dict[str, Any]]) -> float:
        """Simple revenue prediction based on historical data."""        if not historical_data:
            return 0.0
        
        # Calculate trend
        amounts = [d['amount'] for d in historical_data]
        if len(amounts) >= 2:
            # Simple linear trend
            recent_avg = sum(amounts[:len(amounts)//2]) / (len(amounts)//2)
            older_avg = sum(amounts[len(amounts)//2:]) / (len(amounts) - len(amounts)//2)
            
            if older_avg > 0:
                trend_factor = recent_avg / older_avg
                return amounts[0] * trend_factor * 1.1  # 10% growth assumption
        
        return sum(amounts) / len(amounts)
    
    def _calculate_growth_rate(self, current: float, previous: float) -> Optional[float]:
        """Calculate growth rate between periods."""        if previous == 0:
            return None if current == 0 else 100.0
        
        return ((current - previous) / previous) * 100.0
    
    async def _calculate_engagement_correlation(
        self,
        user_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Optional[float]:
        """Calculate correlation between engagement and revenue."""        try:
            sql = """            SELECT engagement_rate, amount 
            FROM revenue_records 
            WHERE user_id = ? AND period_start >= ? AND period_end <= ?
            AND engagement_rate IS NOT NULL AND engagement_rate > 0
            """            
            async with self.get_connection() as conn:
                cursor = await conn.execute(sql, [user_id, start_date, end_date])
                rows = await cursor.fetchall()
            
            if len(rows) < 3:
                return None
            
            # Simple correlation calculation
            engagements = [float(row[0]) for row in rows]
            revenues = [float(row[1]) for row in rows]
            
            # Calculate Pearson correlation coefficient
            n = len(engagements)
            sum_eng = sum(engagements)
            sum_rev = sum(revenues)
            sum_eng_sq = sum(e * e for e in engagements)
            sum_rev_sq = sum(r * r for r in revenues)
            sum_eng_rev = sum(e * r for e, r in zip(engagements, revenues))
            
            numerator = n * sum_eng_rev - sum_eng * sum_rev
            denominator = ((n * sum_eng_sq - sum_eng * sum_eng) * 
                          (n * sum_rev_sq - sum_rev * sum_rev)) ** 0.5
            
            if denominator == 0:
                return None
            
            correlation = numerator / denominator
            return max(-1.0, min(1.0, correlation))  # Clamp to [-1, 1]
            
        except Exception as e:
            logger.warning(f"Failed to calculate engagement correlation: {e}")
            return None
    
    async def _get_top_content(
        self,
        user_id: str,
        start_date: datetime,
        end_date: datetime,
        limit: int = 5
    ) -> List[str]:
        """Get top performing content by revenue."""        try:
            sql = """            SELECT content_id, SUM(amount) as total_revenue
            FROM revenue_records 
            WHERE user_id = ? AND period_start >= ? AND period_end <= ?
            GROUP BY content_id
            ORDER BY total_revenue DESC
            LIMIT ?
            """            
            async with self.get_connection() as conn:
                cursor = await conn.execute(sql, [user_id, start_date, end_date, limit])
                rows = await cursor.fetchall()
            
            return [row[0] for row in rows]
            
        except Exception as e:
            logger.warning(f"Failed to get top content: {e}")
            return []
    
    async def _predict_revenue(self, user_id: str, days: int) -> float:
        """Predict future revenue for user."""        try:
            # Get recent revenue data
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days * 2)  # Use 2x period for prediction
            
            sql = """            SELECT amount, period_start 
            FROM revenue_records 
            WHERE user_id = ? AND period_start >= ?
            ORDER BY period_start DESC
            """            
            async with self.get_connection() as conn:
                cursor = await conn.execute(sql, [user_id, start_date])
                rows = await cursor.fetchall()
            
            if not rows:
                return 0.0
            
            # Simple moving average with trend
            daily_revenues = {}
            for row in rows:
                date_key = row[1].date()
                if date_key not in daily_revenues:
                    daily_revenues[date_key] = 0.0
                daily_revenues[date_key] += float(row[0])
            
            if len(daily_revenues) < 7:
                # Not enough data, use average
                total_revenue = sum(daily_revenues.values())
                avg_daily = total_revenue / len(daily_revenues)
                return avg_daily * days
            
            # Calculate trend
            sorted_dates = sorted(daily_revenues.keys())
            recent_week = sum(daily_revenues[d] for d in sorted_dates[-7:]) / 7
            older_week = sum(daily_revenues[d] for d in sorted_dates[-14:-7]) / 7
            
            if older_week > 0:
                trend_factor = recent_week / older_week
            else:
                trend_factor = 1.0
            
            # Project forward with trend
            base_daily = recent_week
            projected_total = base_daily * days * trend_factor
            
            return max(0.0, projected_total)
            
        except Exception as e:
            logger.warning(f"Failed to predict revenue: {e}")
            return 0.0
    
    async def _generate_insights(
        self,
        current: Dict[str, Any],
        previous: Dict[str, Any],
        growth_rate: Optional[float]
    ) -> List[str]:
        """Generate revenue insights."""        insights = []
        
        if growth_rate is not None:
            if growth_rate > 20:
                insights.append(f"Excellent growth! Revenue increased by {growth_rate:.1f}%")
            elif growth_rate > 5:
                insights.append(f"Good growth of {growth_rate:.1f}% compared to previous period")
            elif growth_rate < -10:
                insights.append(f"Revenue declined by {abs(growth_rate):.1f}%, consider content strategy review")
        
        # Platform insights
        if current['by_platform']:
            top_platform = max(current['by_platform'].items(), key=lambda x: x[1])
            insights.append(f"{top_platform[0]} is your top revenue platform")
        
        # CPM insights
        if current.get('average_cpm', 0) > 5.0:
            insights.append("Strong CPM performance indicates high-value audience")
        elif current.get('average_cpm', 0) < 1.0:
            insights.append("Consider optimizing content for higher-value demographics")
        
        return insights

# Export revenue storage classes
__all__ = [
    'RevenueAnalytics',
    'PaymentRecord',
    'DatabaseRevenueStorageProvider'
]
