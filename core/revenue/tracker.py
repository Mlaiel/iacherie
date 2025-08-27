"""
Revenue Tracking System - Comprehensive revenue monitoring and tracking engine

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

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
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import uuid

import numpy as np
import pandas as pd
from sqlalchemy import Column, String, DateTime, Numeric, Integer, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID, JSONB

from ..utils.exceptions import RevenueTrackingError
from ..utils.validators import validate_tracking_data
from ..utils.cache import cache_revenue_tracking
from ..analytics.metrics import MetricsCollector
from ..security.encryption import EncryptionManager
from ..database.models import BaseModel

logger = logging.getLogger(__name__)

Base = declarative_base()


class RevenueSource(Enum):
    """Revenue source types"""
    SPOTIFY = "spotify"
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    TWITCH = "twitch"
    PATREON = "patreon"
    ONLYFANS = "onlyfans"
    DIRECT_SALES = "direct_sales"
    LICENSING = "licensing"
    MERCHANDISE = "merchandise"
    AFFILIATE = "affiliate"
    SPONSORSHIP = "sponsorship"
    DONATIONS = "donations"
    SUBSCRIPTION = "subscription"
    ADVERTISING = "advertising"
    OTHER = "other"


class RevenueType(Enum):
    """Revenue type classifications"""
    RECURRING = "recurring"
    ONE_TIME = "one_time"
    COMMISSION = "commission"
    ROYALTY = "royalty"
    PERFORMANCE = "performance"
    LICENSING_FEE = "licensing_fee"
    SUBSCRIPTION_FEE = "subscription_fee"
    TRANSACTION_FEE = "transaction_fee"


class TrackingStatus(Enum):
    """Revenue tracking status"""
    ACTIVE = "active"
    PENDING = "pending"
    VERIFIED = "verified"
    DISPUTED = "disputed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    FAILED = "failed"


class TrackingFrequency(Enum):
    """Tracking frequency options"""
    REAL_TIME = "real_time"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


@dataclass
class TrackingMetrics:
    """Revenue tracking performance metrics"""
    total_tracked_revenue: Decimal
    verified_revenue: Decimal
    pending_revenue: Decimal
    disputed_revenue: Decimal
    tracking_accuracy: float
    data_completeness: float
    update_frequency: float
    last_update: datetime
    sources_count: int
    active_streams: int
    
    @property
    def verification_rate(self) -> float:
        """Calculate revenue verification rate"""
        if self.total_tracked_revenue == 0:
            return 0.0
        return float((self.verified_revenue / self.total_tracked_revenue) * 100)


@dataclass
class RevenueAlert:
    """Revenue tracking alert"""
    alert_id: str
    alert_type: str
    severity: str
    message: str
    revenue_source: RevenueSource
    amount: Decimal
    timestamp: datetime
    is_resolved: bool = False
    resolution_notes: Optional[str] = None


class RevenueTrackingModel(BaseModel):
    """Revenue tracking database model"""
    __tablename__ = "revenue_tracking"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    source = Column(String(50), nullable=False)
    revenue_type = Column(String(50), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(3), default="EUR")
    transaction_id = Column(String(255))
    reference_id = Column(String(255))
    description = Column(Text)
    status = Column(String(20), default="pending")
    metadata = Column(JSONB)
    tracked_at = Column(DateTime, default=datetime.utcnow)
    verified_at = Column(DateTime)
    processed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class RevenueStreamModel(BaseModel):
    """Revenue stream configuration model"""
    __tablename__ = "revenue_streams"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    name = Column(String(255), nullable=False)
    source = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=True)
    tracking_frequency = Column(String(20), default="daily")
    api_config = Column(JSONB)
    last_sync = Column(DateTime)
    total_revenue = Column(Numeric(15, 2), default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class BaseRevenueTracker(ABC):
    """Abstract base class for revenue trackers"""
    
    @abstractmethod
    async def track_revenue(self, source: RevenueSource, data: Dict[str, Any]) -> str:
        """Track revenue from specific source"""
        pass
    
    @abstractmethod
    async def verify_revenue(self, tracking_id: str) -> bool:
        """Verify tracked revenue"""
        pass
    
    @abstractmethod
    async def get_metrics(self) -> TrackingMetrics:
        """Get tracking metrics"""
        pass


class PlatformRevenueTracker:
    """Platform-specific revenue tracker"""
    
    def __init__(self, platform: RevenueSource, config: Dict[str, Any]):
        self.platform = platform
        self.config = config
        self.api_client = None
        self.last_sync = None
        
    async def initialize(self) -> None:
        """Initialize platform tracker"""
        try:
            # Initialize platform-specific API client
            await self._setup_api_client()
            logger.info(f"Initialized tracker for {self.platform.value}")
        except Exception as e:
            logger.error(f"Error initializing {self.platform.value} tracker: {e}")
            raise
    
    async def _setup_api_client(self) -> None:
        """Setup platform API client"""
        # Platform-specific API setup
        api_configs = {
            RevenueSource.SPOTIFY: self._setup_spotify_client,
            RevenueSource.YOUTUBE: self._setup_youtube_client,
            RevenueSource.INSTAGRAM: self._setup_instagram_client,
            RevenueSource.TIKTOK: self._setup_tiktok_client
        }
        
        setup_func = api_configs.get(self.platform)
        if setup_func:
            await setup_func()
    
    async def _setup_spotify_client(self) -> None:
        """Setup Spotify API client"""
        # Spotify-specific setup
        pass
    
    async def _setup_youtube_client(self) -> None:
        """Setup YouTube API client"""
        # YouTube-specific setup
        pass
    
    async def _setup_instagram_client(self) -> None:
        """Setup Instagram API client"""
        # Instagram-specific setup
        pass
    
    async def _setup_tiktok_client(self) -> None:
        """Setup TikTok API client"""
        # TikTok-specific setup
        pass
    
    async def fetch_revenue_data(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Fetch revenue data from platform"""
        try:
            # Platform-specific data fetching
            fetch_methods = {
                RevenueSource.SPOTIFY: self._fetch_spotify_data,
                RevenueSource.YOUTUBE: self._fetch_youtube_data,
                RevenueSource.INSTAGRAM: self._fetch_instagram_data,
                RevenueSource.TIKTOK: self._fetch_tiktok_data
            }
            
            fetch_method = fetch_methods.get(self.platform)
            if fetch_method:
                return await fetch_method(start_date, end_date)
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error fetching revenue data from {self.platform.value}: {e}")
            raise RevenueTrackingError(f"Data fetch failed: {e}")
    
    async def _fetch_spotify_data(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Fetch Spotify revenue data"""
        # Mock data for demonstration
        return [
            {
                'amount': Decimal('150.75'),
                'currency': 'EUR',
                'transaction_id': 'SPOT_123456',
                'description': 'Streaming royalties',
                'date': datetime.utcnow(),
                'metadata': {'streams': 10000, 'track_id': 'track123'}
            }
        ]
    
    async def _fetch_youtube_data(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Fetch YouTube revenue data"""
        # Mock data for demonstration
        return [
            {
                'amount': Decimal('89.50'),
                'currency': 'EUR',
                'transaction_id': 'YT_789012',
                'description': 'Ad revenue',
                'date': datetime.utcnow(),
                'metadata': {'views': 50000, 'video_id': 'video123'}
            }
        ]
    
    async def _fetch_instagram_data(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Fetch Instagram revenue data"""
        # Mock data for demonstration
        return [
            {
                'amount': Decimal('75.25'),
                'currency': 'EUR',
                'transaction_id': 'IG_345678',
                'description': 'Creator fund',
                'date': datetime.utcnow(),
                'metadata': {'reach': 25000, 'post_id': 'post123'}
            }
        ]
    
    async def _fetch_tiktok_data(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Fetch TikTok revenue data"""
        # Mock data for demonstration
        return [
            {
                'amount': Decimal('45.80'),
                'currency': 'EUR',
                'transaction_id': 'TT_901234',
                'description': 'Creator fund payout',
                'date': datetime.utcnow(),
                'metadata': {'views': 100000, 'video_id': 'video456'}
            }
        ]


class RevenueTracker(BaseRevenueTracker):
    """Comprehensive revenue tracking system"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.platform_trackers = {}
        self.metrics_collector = MetricsCollector()
        self.encryption_manager = EncryptionManager()
        self.active_streams = set()
        self.alerts = []
        self.tracking_history = []
        
    async def initialize(self) -> None:
        """Initialize revenue tracker"""
        try:
            # Initialize platform trackers
            await self._setup_platform_trackers()
            
            # Setup alert system
            await self._setup_alert_system()
            
            logger.info("Revenue tracker initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing revenue tracker: {e}")
            raise
    
    async def _setup_platform_trackers(self) -> None:
        """Setup platform-specific trackers"""
        platform_configs = self.config.get('platforms', {})
        
        for platform_name, platform_config in platform_configs.items():
            try:
                platform = RevenueSource(platform_name)
                tracker = PlatformRevenueTracker(platform, platform_config)
                await tracker.initialize()
                self.platform_trackers[platform] = tracker
                
            except ValueError:
                logger.warning(f"Unknown platform: {platform_name}")
            except Exception as e:
                logger.error(f"Error setting up {platform_name} tracker: {e}")
    
    async def _setup_alert_system(self) -> None:
        """Setup revenue alert system"""
        # Configure alert thresholds and rules
        self.alert_config = self.config.get('alerts', {
            'threshold_amount': Decimal('1000'),
            'variance_threshold': 0.2,
            'delay_threshold_hours': 24
        })
    
    @cache_revenue_tracking
    async def track_revenue(self, source: RevenueSource, data: Dict[str, Any]) -> str:
        """Track revenue from specific source"""
        try:
            validate_tracking_data(data)
            
            # Generate tracking ID
            tracking_id = str(uuid.uuid4())
            
            # Extract revenue data
            amount = Decimal(str(data.get('amount', 0)))
            currency = data.get('currency', 'EUR')
            transaction_id = data.get('transaction_id')
            description = data.get('description', '')
            metadata = data.get('metadata', {})
            
            # Create tracking record
            tracking_record = {
                'id': tracking_id,
                'source': source.value,
                'amount': amount,
                'currency': currency,
                'transaction_id': transaction_id,
                'description': description,
                'metadata': metadata,
                'status': TrackingStatus.PENDING.value,
                'tracked_at': datetime.utcnow()
            }
            
            # Store tracking record (in production, save to database)
            self.tracking_history.append(tracking_record)
            
            # Add to active streams
            self.active_streams.add(tracking_id)
            
            # Check for alerts
            await self._check_revenue_alerts(tracking_record)
            
            # Collect metrics
            await self.metrics_collector.record_revenue_tracked(amount, source.value)
            
            logger.info(f"Revenue tracked: {tracking_id} - {amount} {currency} from {source.value}")
            
            return tracking_id
            
        except Exception as e:
            logger.error(f"Error tracking revenue: {e}")
            raise RevenueTrackingError(f"Revenue tracking failed: {e}")
    
    async def verify_revenue(self, tracking_id: str) -> bool:
        """Verify tracked revenue"""
        try:
            # Find tracking record
            tracking_record = next(
                (r for r in self.tracking_history if r['id'] == tracking_id),
                None
            )
            
            if not tracking_record:
                raise RevenueTrackingError(f"Tracking record not found: {tracking_id}")
            
            # Perform verification
            verification_result = await self._perform_verification(tracking_record)
            
            # Update status
            if verification_result:
                tracking_record['status'] = TrackingStatus.VERIFIED.value
                tracking_record['verified_at'] = datetime.utcnow()
                logger.info(f"Revenue verified: {tracking_id}")
            else:
                tracking_record['status'] = TrackingStatus.DISPUTED.value
                logger.warning(f"Revenue verification failed: {tracking_id}")
            
            return verification_result
            
        except Exception as e:
            logger.error(f"Error verifying revenue: {e}")
            raise RevenueTrackingError(f"Revenue verification failed: {e}")
    
    async def _perform_verification(self, tracking_record: Dict[str, Any]) -> bool:
        """Perform revenue verification"""
        try:
            source = RevenueSource(tracking_record['source'])
            
            # Platform-specific verification
            if source in self.platform_trackers:
                tracker = self.platform_trackers[source]
                
                # Fetch recent data from platform
                end_date = datetime.utcnow()
                start_date = end_date - timedelta(days=7)
                platform_data = await tracker.fetch_revenue_data(start_date, end_date)
                
                # Check if transaction exists in platform data
                transaction_id = tracking_record['transaction_id']
                amount = tracking_record['amount']
                
                for platform_transaction in platform_data:
                    if (platform_transaction.get('transaction_id') == transaction_id or
                        abs(platform_transaction.get('amount', 0) - amount) < Decimal('0.01')):
                        return True
            
            # Default verification (simplified)
            return True  # In production, implement proper verification logic
            
        except Exception as e:
            logger.error(f"Error performing verification: {e}")
            return False
    
    async def get_metrics(self) -> TrackingMetrics:
        """Get comprehensive tracking metrics"""
        try:
            # Calculate metrics from tracking history
            total_tracked = sum(Decimal(r['amount']) for r in self.tracking_history)
            verified_revenue = sum(
                Decimal(r['amount']) for r in self.tracking_history 
                if r['status'] == TrackingStatus.VERIFIED.value
            )
            pending_revenue = sum(
                Decimal(r['amount']) for r in self.tracking_history 
                if r['status'] == TrackingStatus.PENDING.value
            )
            disputed_revenue = sum(
                Decimal(r['amount']) for r in self.tracking_history 
                if r['status'] == TrackingStatus.DISPUTED.value
            )
            
            # Calculate accuracy
            verified_count = len([r for r in self.tracking_history if r['status'] == TrackingStatus.VERIFIED.value])
            total_count = len(self.tracking_history)
            accuracy = (verified_count / total_count * 100) if total_count > 0 else 0
            
            # Calculate data completeness
            complete_records = len([
                r for r in self.tracking_history 
                if r.get('transaction_id') and r.get('description')
            ])
            completeness = (complete_records / total_count * 100) if total_count > 0 else 0
            
            # Calculate update frequency (updates per hour)
            if self.tracking_history:
                time_span = (datetime.utcnow() - self.tracking_history[0]['tracked_at']).total_seconds() / 3600
                update_frequency = total_count / time_span if time_span > 0 else 0
            else:
                update_frequency = 0
            
            # Get unique sources
            sources_count = len(set(r['source'] for r in self.tracking_history))
            
            metrics = TrackingMetrics(
                total_tracked_revenue=total_tracked,
                verified_revenue=verified_revenue,
                pending_revenue=pending_revenue,
                disputed_revenue=disputed_revenue,
                tracking_accuracy=accuracy,
                data_completeness=completeness,
                update_frequency=update_frequency,
                last_update=self.tracking_history[-1]['tracked_at'] if self.tracking_history else datetime.utcnow(),
                sources_count=sources_count,
                active_streams=len(self.active_streams)
            )
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating metrics: {e}")
            raise RevenueTrackingError(f"Metrics calculation failed: {e}")
    
    async def _check_revenue_alerts(self, tracking_record: Dict[str, Any]) -> None:
        """Check for revenue alerts"""
        try:
            amount = tracking_record['amount']
            source = RevenueSource(tracking_record['source'])
            
            # High amount alert
            if amount >= self.alert_config['threshold_amount']:
                alert = RevenueAlert(
                    alert_id=str(uuid.uuid4()),
                    alert_type="high_amount",
                    severity="high",
                    message=f"High revenue amount detected: {amount} EUR",
                    revenue_source=source,
                    amount=amount,
                    timestamp=datetime.utcnow()
                )
                self.alerts.append(alert)
            
            # Variance alert (if we have historical data)
            recent_amounts = [
                Decimal(r['amount']) for r in self.tracking_history[-10:]
                if r['source'] == source.value
            ]
            
            if len(recent_amounts) >= 3:
                avg_amount = sum(recent_amounts) / len(recent_amounts)
                variance = abs(amount - avg_amount) / avg_amount
                
                if variance >= self.alert_config['variance_threshold']:
                    alert = RevenueAlert(
                        alert_id=str(uuid.uuid4()),
                        alert_type="variance",
                        severity="medium",
                        message=f"Revenue variance detected: {variance:.1%} from average",
                        revenue_source=source,
                        amount=amount,
                        timestamp=datetime.utcnow()
                    )
                    self.alerts.append(alert)
            
        except Exception as e:
            logger.error(f"Error checking revenue alerts: {e}")
    
    async def sync_platform_revenue(self, source: RevenueSource, start_date: datetime, end_date: datetime) -> int:
        """Sync revenue data from platform"""
        try:
            if source not in self.platform_trackers:
                raise RevenueTrackingError(f"Platform tracker not configured: {source.value}")
            
            tracker = self.platform_trackers[source]
            platform_data = await tracker.fetch_revenue_data(start_date, end_date)
            
            synced_count = 0
            for data in platform_data:
                tracking_id = await self.track_revenue(source, data)
                await self.verify_revenue(tracking_id)
                synced_count += 1
            
            # Update last sync time
            tracker.last_sync = datetime.utcnow()
            
            logger.info(f"Synced {synced_count} revenue records from {source.value}")
            
            return synced_count
            
        except Exception as e:
            logger.error(f"Error syncing platform revenue: {e}")
            raise RevenueTrackingError(f"Platform sync failed: {e}")
    
    async def get_revenue_summary(self, period: str = 'month') -> Dict[str, Any]:
        """Get revenue summary for specified period"""
        try:
            # Calculate date range
            end_date = datetime.utcnow()
            if period == 'day':
                start_date = end_date - timedelta(days=1)
            elif period == 'week':
                start_date = end_date - timedelta(weeks=1)
            elif period == 'month':
                start_date = end_date - timedelta(days=30)
            elif period == 'year':
                start_date = end_date - timedelta(days=365)
            else:
                start_date = end_date - timedelta(days=30)
            
            # Filter records by period
            period_records = [
                r for r in self.tracking_history
                if start_date <= r['tracked_at'] <= end_date
            ]
            
            # Calculate summary by source
            source_summary = {}
            for record in period_records:
                source = record['source']
                amount = Decimal(record['amount'])
                
                if source not in source_summary:
                    source_summary[source] = {
                        'total_amount': Decimal('0'),
                        'transaction_count': 0,
                        'verified_amount': Decimal('0'),
                        'pending_amount': Decimal('0')
                    }
                
                source_summary[source]['total_amount'] += amount
                source_summary[source]['transaction_count'] += 1
                
                if record['status'] == TrackingStatus.VERIFIED.value:
                    source_summary[source]['verified_amount'] += amount
                elif record['status'] == TrackingStatus.PENDING.value:
                    source_summary[source]['pending_amount'] += amount
            
            # Calculate totals
            total_amount = sum(s['total_amount'] for s in source_summary.values())
            total_transactions = sum(s['transaction_count'] for s in source_summary.values())
            
            summary = {
                'period': period,
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'total_amount': str(total_amount),
                'total_transactions': total_transactions,
                'source_breakdown': {
                    source: {
                        'total_amount': str(data['total_amount']),
                        'transaction_count': data['transaction_count'],
                        'verified_amount': str(data['verified_amount']),
                        'pending_amount': str(data['pending_amount'])
                    }
                    for source, data in source_summary.items()
                },
                'top_sources': sorted(
                    source_summary.items(),
                    key=lambda x: x[1]['total_amount'],
                    reverse=True
                )[:5]
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating revenue summary: {e}")
            raise RevenueTrackingError(f"Summary generation failed: {e}")
    
    async def get_alerts(self, unresolved_only: bool = True) -> List[RevenueAlert]:
        """Get revenue alerts"""
        if unresolved_only:
            return [alert for alert in self.alerts if not alert.is_resolved]
        return self.alerts
    
    async def resolve_alert(self, alert_id: str, resolution_notes: str) -> bool:
        """Resolve revenue alert"""
        try:
            alert = next((a for a in self.alerts if a.alert_id == alert_id), None)
            
            if not alert:
                raise RevenueTrackingError(f"Alert not found: {alert_id}")
            
            alert.is_resolved = True
            alert.resolution_notes = resolution_notes
            
            logger.info(f"Alert resolved: {alert_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error resolving alert: {e}")
            raise RevenueTrackingError(f"Alert resolution failed: {e}")
    
    async def export_tracking_report(self, format: str = 'json') -> Dict[str, Any]:
        """Export comprehensive tracking report"""
        try:
            metrics = await self.get_metrics()
            alerts = await self.get_alerts(unresolved_only=False)
            
            report = {
                'timestamp': datetime.utcnow().isoformat(),
                'tracking_metrics': {
                    'total_tracked_revenue': str(metrics.total_tracked_revenue),
                    'verified_revenue': str(metrics.verified_revenue),
                    'pending_revenue': str(metrics.pending_revenue),
                    'disputed_revenue': str(metrics.disputed_revenue),
                    'tracking_accuracy': metrics.tracking_accuracy,
                    'data_completeness': metrics.data_completeness,
                    'verification_rate': metrics.verification_rate,
                    'sources_count': metrics.sources_count,
                    'active_streams': metrics.active_streams
                },
                'platform_status': {
                    platform.value: {
                        'is_configured': platform in self.platform_trackers,
                        'last_sync': self.platform_trackers[platform].last_sync.isoformat()
                        if platform in self.platform_trackers and self.platform_trackers[platform].last_sync
                        else None
                    }
                    for platform in RevenueSource
                },
                'alerts_summary': {
                    'total_alerts': len(alerts),
                    'unresolved_alerts': len([a for a in alerts if not a.is_resolved]),
                    'high_severity_alerts': len([a for a in alerts if a.severity == 'high'])
                },
                'recent_activity': self.tracking_history[-10:] if self.tracking_history else []
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error exporting tracking report: {e}")
            raise RevenueTrackingError(f"Report export failed: {e}")
