"""
Content Analytics Module - Advanced Analytics Engine for Content Performance

Module fournissant des analytics avancés pour la performance, l'engagement et 
la monétisation du contenu multimédia.

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Analytics Expert, Data Scientist, Business Intelligence Specialist  
Copyright: Fahed Mlaiel - All rights reserved

⚠️  AVERTISSEMENT LÉGAL ⚠️
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution non autorisée
est strictement interdite et fera l'objet de poursuites judiciaires.
Contact: mlaiel@live.de
"""

from typing import Dict, List, Any, Optional, Union, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
import uuid
import json
import asyncio
import logging
from decimal import Decimal

import pandas as pd
import numpy as np
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

logger = logging.getLogger(__name__)
Base = declarative_base()

class AnalyticsMetric(Enum):
    """Types of analytics metrics tracked"""
    VIEWS = "views"
    PLAYS = "plays"
    DOWNLOADS = "downloads"
    SHARES = "shares"
    LIKES = "likes"
    COMMENTS = "comments"
    SAVES = "saves"
    REVENUE = "revenue"
    ENGAGEMENT_RATE = "engagement_rate"
    CONVERSION_RATE = "conversion_rate"
    RETENTION_RATE = "retention_rate"
    CLICK_THROUGH_RATE = "click_through_rate"

class TimeFrame(Enum):
    """Analytics time frame periods"""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    REAL_TIME = "real_time"
    CUSTOM = "custom"

class Platform(Enum):
    """Supported platforms for analytics tracking"""
    SPOTIFY = "spotify"
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    SOUNDCLOUD = "soundcloud"
    BANDCAMP = "bandcamp"
    APPLE_MUSIC = "apple_music"
    AMAZON_MUSIC = "amazon_music"
    DEEZER = "deezer"
    TWITCH = "twitch"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"

@dataclass
class ContentPerformanceMetrics:
    """Comprehensive content performance metrics"""
    content_id: str
    platform: Platform
    timestamp: datetime
    
    # Engagement metrics
    views: int = 0
    unique_views: int = 0
    plays: int = 0
    complete_plays: int = 0
    partial_plays: int = 0
    downloads: int = 0
    shares: int = 0
    likes: int = 0
    dislikes: int = 0
    comments: int = 0
    saves: int = 0
    
    # Revenue metrics
    revenue: Decimal = Decimal('0.00')
    revenue_currency: str = "EUR"
    rpm: Optional[Decimal] = None  # Revenue per mille
    cpm: Optional[Decimal] = None  # Cost per mille
    
    # Audience metrics
    watch_time_minutes: float = 0.0
    average_view_duration: float = 0.0
    audience_retention: float = 0.0
    demographics: Dict[str, Any] = field(default_factory=dict)
    geographic_data: Dict[str, int] = field(default_factory=dict)
    
    # Quality metrics
    engagement_rate: float = 0.0
    conversion_rate: float = 0.0
    click_through_rate: float = 0.0
    bounce_rate: float = 0.0
    
    # Platform-specific metrics
    platform_specific: Dict[str, Any] = field(default_factory=dict)

class ContentAnalytics(Base):
    """Content analytics database model"""
    __tablename__ = "content_analytics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    platform = Column(String(50), nullable=False)
    metric_type = Column(String(50), nullable=False)
    time_frame = Column(String(20), nullable=False)
    
    # Temporal data
    recorded_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    
    # Metrics data
    metrics = Column(JSONB, nullable=False, default={})
    raw_data = Column(JSONB, nullable=True)
    
    # Calculated fields
    total_engagement = Column(Float, default=0.0)
    engagement_rate = Column(Float, default=0.0)
    revenue_amount = Column(Float, default=0.0)
    revenue_currency = Column(String(3), default="EUR")
    
    # Metadata
    data_quality_score = Column(Float, default=1.0)
    confidence_level = Column(Float, default=1.0)
    is_estimated = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class AnalyticsEngine:
    """Advanced analytics processing engine"""
    
    def __init__(self):
        self.supported_platforms = list(Platform)
        self.metric_calculators = self._initialize_calculators()
    
    def _initialize_calculators(self) -> Dict[str, callable]:
        """Initialize metric calculation functions"""
        return {
            'engagement_rate': self._calculate_engagement_rate,
            'conversion_rate': self._calculate_conversion_rate,
            'retention_rate': self._calculate_retention_rate,
            'revenue_per_view': self._calculate_revenue_per_view,
            'growth_rate': self._calculate_growth_rate,
            'audience_quality': self._calculate_audience_quality,
            'content_score': self._calculate_content_score,
            'viral_potential': self._calculate_viral_potential
        }
    
    async def process_content_analytics(
        self, 
        content_id: str, 
        platform_data: Dict[Platform, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Process comprehensive analytics for content across platforms"""
        try:
            analytics_results = {}
            
            for platform, data in platform_data.items():
                platform_analytics = await self._process_platform_analytics(
                    content_id, platform, data
                )
                analytics_results[platform.value] = platform_analytics
            
            # Calculate cross-platform metrics
            cross_platform_metrics = await self._calculate_cross_platform_metrics(
                analytics_results
            )
            
            return {
                'content_id': content_id,
                'platform_analytics': analytics_results,
                'cross_platform_metrics': cross_platform_metrics,
                'processed_at': datetime.utcnow(),
                'next_update': datetime.utcnow() + timedelta(hours=1)
            }
            
        except Exception as e:
            logger.error(f"Error processing analytics for content {content_id}: {e}")
            raise
    
    async def _process_platform_analytics(
        self, 
        content_id: str, 
        platform: Platform, 
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process analytics for a specific platform"""
        metrics = ContentPerformanceMetrics(
            content_id=content_id,
            platform=platform,
            timestamp=datetime.utcnow(),
            **data
        )
        
        # Calculate derived metrics
        calculated_metrics = {}
        for metric_name, calculator in self.metric_calculators.items():
            try:
                calculated_metrics[metric_name] = await calculator(metrics, data)
            except Exception as e:
                logger.warning(f"Failed to calculate {metric_name}: {e}")
                calculated_metrics[metric_name] = None
        
        return {
            'raw_metrics': data,
            'calculated_metrics': calculated_metrics,
            'platform': platform.value,
            'quality_score': calculated_metrics.get('content_score', 0.0)
        }
    
    async def _calculate_engagement_rate(
        self, 
        metrics: ContentPerformanceMetrics, 
        raw_data: Dict[str, Any]
    ) -> float:
        """Calculate engagement rate"""
        if metrics.views == 0:
            return 0.0
        
        total_engagement = (
            metrics.likes + metrics.comments + 
            metrics.shares + metrics.saves
        )
        return (total_engagement / metrics.views) * 100
    
    async def _calculate_conversion_rate(
        self, 
        metrics: ContentPerformanceMetrics, 
        raw_data: Dict[str, Any]
    ) -> float:
        """Calculate conversion rate"""
        if metrics.views == 0:
            return 0.0
        
        conversions = metrics.downloads + metrics.saves
        return (conversions / metrics.views) * 100
    
    async def _calculate_retention_rate(
        self, 
        metrics: ContentPerformanceMetrics, 
        raw_data: Dict[str, Any]
    ) -> float:
        """Calculate audience retention rate"""
        if metrics.plays == 0:
            return 0.0
        
        return (metrics.complete_plays / metrics.plays) * 100
    
    async def _calculate_revenue_per_view(
        self, 
        metrics: ContentPerformanceMetrics, 
        raw_data: Dict[str, Any]
    ) -> float:
        """Calculate revenue per view"""
        if metrics.views == 0:
            return 0.0
        
        return float(metrics.revenue / metrics.views)
    
    async def _calculate_growth_rate(
        self, 
        metrics: ContentPerformanceMetrics, 
        raw_data: Dict[str, Any]
    ) -> float:
        """Calculate growth rate compared to previous period"""
        # Implementation would compare with historical data
        return 0.0  # Placeholder
    
    async def _calculate_audience_quality(
        self, 
        metrics: ContentPerformanceMetrics, 
        raw_data: Dict[str, Any]
    ) -> float:
        """Calculate audience quality score"""
        quality_factors = []
        
        # Engagement quality
        if metrics.views > 0:
            engagement_ratio = (metrics.likes + metrics.comments) / metrics.views
            quality_factors.append(min(engagement_ratio * 100, 10))
        
        # Retention quality
        if metrics.plays > 0:
            retention_ratio = metrics.complete_plays / metrics.plays
            quality_factors.append(retention_ratio * 10)
        
        # Geographic diversity (if available)
        if metrics.geographic_data:
            geo_diversity = len(metrics.geographic_data) / 50  # Normalize to 50 countries
            quality_factors.append(min(geo_diversity * 10, 10))
        
        return sum(quality_factors) / len(quality_factors) if quality_factors else 0.0
    
    async def _calculate_content_score(
        self, 
        metrics: ContentPerformanceMetrics, 
        raw_data: Dict[str, Any]
    ) -> float:
        """Calculate overall content performance score"""
        scores = []
        
        # Engagement score (40% weight)
        engagement_rate = await self._calculate_engagement_rate(metrics, raw_data)
        scores.append(min(engagement_rate / 10, 10) * 0.4)
        
        # Retention score (30% weight)
        retention_rate = await self._calculate_retention_rate(metrics, raw_data)
        scores.append((retention_rate / 100) * 10 * 0.3)
        
        # Revenue score (20% weight)
        revenue_per_view = await self._calculate_revenue_per_view(metrics, raw_data)
        revenue_score = min(revenue_per_view * 1000, 10)  # Normalize
        scores.append(revenue_score * 0.2)
        
        # Audience quality score (10% weight)
        audience_quality = await self._calculate_audience_quality(metrics, raw_data)
        scores.append(audience_quality * 0.1)
        
        return sum(scores)
    
    async def _calculate_viral_potential(
        self, 
        metrics: ContentPerformanceMetrics, 
        raw_data: Dict[str, Any]
    ) -> float:
        """Calculate viral potential score"""
        viral_indicators = []
        
        # Share rate
        if metrics.views > 0:
            share_rate = metrics.shares / metrics.views
            viral_indicators.append(min(share_rate * 100, 10))
        
        # Growth velocity (would need historical data)
        # Placeholder for now
        viral_indicators.append(5.0)
        
        # Platform-specific viral indicators
        if metrics.platform == Platform.TIKTOK:
            # TikTok-specific viral metrics
            viral_indicators.append(7.0)
        elif metrics.platform == Platform.YOUTUBE:
            # YouTube-specific viral metrics
            viral_indicators.append(6.0)
        
        return sum(viral_indicators) / len(viral_indicators) if viral_indicators else 0.0
    
    async def _calculate_cross_platform_metrics(
        self, 
        platform_analytics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate metrics across all platforms"""
        total_views = sum(
            analytics.get('raw_metrics', {}).get('views', 0) 
            for analytics in platform_analytics.values()
        )
        
        total_revenue = sum(
            analytics.get('raw_metrics', {}).get('revenue', 0) 
            for analytics in platform_analytics.values()
        )
        
        avg_engagement_rate = np.mean([
            analytics.get('calculated_metrics', {}).get('engagement_rate', 0)
            for analytics in platform_analytics.values()
        ])
        
        avg_content_score = np.mean([
            analytics.get('calculated_metrics', {}).get('content_score', 0)
            for analytics in platform_analytics.values()
        ])
        
        return {
            'total_views': total_views,
            'total_revenue': total_revenue,
            'average_engagement_rate': avg_engagement_rate,
            'average_content_score': avg_content_score,
            'platform_count': len(platform_analytics),
            'top_performing_platform': max(
                platform_analytics.items(),
                key=lambda x: x[1].get('calculated_metrics', {}).get('content_score', 0)
            )[0] if platform_analytics else None
        }

class RealtimeAnalytics:
    """Real-time analytics processing system"""
    
    def __init__(self):
        self.active_streams = {}
        self.metric_buffers = {}
    
    async def start_realtime_tracking(self, content_id: str, platforms: List[Platform]):
        """Start real-time analytics tracking for content"""
        for platform in platforms:
            stream_key = f"{content_id}_{platform.value}"
            self.active_streams[stream_key] = {
                'content_id': content_id,
                'platform': platform,
                'started_at': datetime.utcnow(),
                'metrics': {}
            }
    
    async def update_realtime_metric(
        self, 
        content_id: str, 
        platform: Platform, 
        metric: AnalyticsMetric, 
        value: Any
    ):
        """Update real-time metric value"""
        stream_key = f"{content_id}_{platform.value}"
        if stream_key in self.active_streams:
            self.active_streams[stream_key]['metrics'][metric.value] = {
                'value': value,
                'timestamp': datetime.utcnow()
            }
    
    async def get_realtime_metrics(self, content_id: str) -> Dict[str, Any]:
        """Get current real-time metrics for content"""
        content_streams = {
            k: v for k, v in self.active_streams.items() 
            if v['content_id'] == content_id
        }
        
        return {
            'content_id': content_id,
            'active_platforms': list(content_streams.keys()),
            'metrics': content_streams,
            'last_updated': datetime.utcnow()
        }

# Export classes and functions
__all__ = [
    'AnalyticsMetric',
    'TimeFrame', 
    'Platform',
    'ContentPerformanceMetrics',
    'ContentAnalytics',
    'AnalyticsEngine',
    'RealtimeAnalytics'
]
