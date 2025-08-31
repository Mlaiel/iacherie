"""Performance Tracking Database Components

Enterprise performance tracking system for multi-format content creators with
real-time metrics collection, cross-platform analytics, and AI-powered insights.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

🚨 INTELLECTUAL PROPERTY WARNING: This code, concept, and architecture are 
the exclusive intellectual property of Fahed Mlaiel (mlaiel@live.de). 
Any use, copying, distribution, or exploitation without explicit written 
authorization is STRICTLY PROHIBITED and will be prosecuted.

Expert Project Team - Fahed Mlaiel:
- Lead AI Developer & Software Architect
- Senior Backend Engineer (Python/FastAPI/Django)  
- Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face)
- Database Administrator & Data Engineer (PostgreSQL/Redis/MongoDB)
- Backend Security Specialist
- Microservices Architect
- Audio Processing Engineer
- DevOps Engineer
- AI Prompt Engineer
"""import uuid
import json
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
from decimal import Decimal
from sqlalchemy import Column, String, DateTime, JSON, Boolean, Integer, Text, Index, BigInteger, Numeric
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
import logging

Base = declarative_base()
logger = logging.getLogger(__name__)


class ContentFormat(Enum):
    """Content format types"""    MUSIC = "music"
    VIDEO = "video"
    PHOTO = "photo"
    BLOG_POST = "blog_post"
    PODCAST = "podcast"
    LIVE_STREAM = "live_stream"
    SHORT_FORM = "short_form"
    DOCUMENT = "document"
    COURSE = "course"
    COMEDY = "comedy"


class PlatformType(Enum):
    """Platform types for content distribution"""    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    SPOTIFY = "spotify"
    SOUNDCLOUD = "soundcloud"
    TWITCH = "twitch"
    LINKEDIN = "linkedin"
    MEDIUM = "medium"
    SUBSTACK = "substack"
    PATREON = "patreon"
    ONLYFANS = "onlyfans"
    CUSTOM = "custom"


class MetricType(Enum):
    """Types of performance metrics"""    VIEWS = "views"
    LIKES = "likes"
    SHARES = "shares"
    COMMENTS = "comments"
    FOLLOWERS = "followers"
    SUBSCRIBERS = "subscribers"
    PLAYS = "plays"
    DOWNLOADS = "downloads"
    REVENUE = "revenue"
    ENGAGEMENT_RATE = "engagement_rate"
    RETENTION_RATE = "retention_rate"
    CLICK_THROUGH_RATE = "click_through_rate"
    CONVERSION_RATE = "conversion_rate"


@dataclass
class MetricSnapshot:
    """Performance metric snapshot"""    metric_type: MetricType
    value: Union[int, float, Decimal]
    timestamp: datetime
    platform: PlatformType
    content_id: str
    metadata: Dict[str, Any]


class ContentPerformance(Base):
    """    Database model for content performance tracking
    """    __tablename__ = "content_performance"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    creator_type = Column(String(50), nullable=False)
    content_format = Column(String(50), nullable=False)
    
    # Platform and distribution
    platform = Column(String(50), nullable=False, index=True)
    platform_content_id = Column(String(200), index=True)
    distribution_url = Column(Text)
    
    # Performance metrics
    total_views = Column(BigInteger, default=0)
    total_likes = Column(BigInteger, default=0)
    total_shares = Column(BigInteger, default=0)
    total_comments = Column(BigInteger, default=0)
    total_downloads = Column(BigInteger, default=0)
    total_plays = Column(BigInteger, default=0)
    
    # Engagement metrics
    engagement_rate = Column(Numeric(5, 4), default=0.0)
    retention_rate = Column(Numeric(5, 4), default=0.0)
    click_through_rate = Column(Numeric(5, 4), default=0.0)
    conversion_rate = Column(Numeric(5, 4), default=0.0)
    
    # Audience metrics
    unique_viewers = Column(BigInteger, default=0)
    returning_viewers = Column(BigInteger, default=0)
    new_followers = Column(Integer, default=0)
    new_subscribers = Column(Integer, default=0)
    
    # Revenue metrics
    total_revenue = Column(Numeric(15, 2), default=0.0)
    advertising_revenue = Column(Numeric(15, 2), default=0.0)
    subscription_revenue = Column(Numeric(15, 2), default=0.0)
    donation_revenue = Column(Numeric(15, 2), default=0.0)
    merchandise_revenue = Column(Numeric(15, 2), default=0.0)
    
    # Time-based metrics
    average_watch_time = Column(Integer, default=0)  # seconds
    peak_concurrent_viewers = Column(Integer, default=0)
    total_watch_time = Column(BigInteger, default=0)  # seconds
    
    # Geographic and demographic data
    top_countries = Column(JSON)
    age_demographics = Column(JSON)
    gender_demographics = Column(JSON)
    device_breakdown = Column(JSON)
    
    # Timing and trends
    published_at = Column(DateTime(timezone=True), nullable=False)
    first_metric_at = Column(DateTime(timezone=True))
    last_updated = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    peak_performance_at = Column(DateTime(timezone=True))
    
    # Analysis metadata
    performance_score = Column(Numeric(5, 2), default=0.0)
    virality_score = Column(Numeric(5, 2), default=0.0)
    quality_score = Column(Numeric(5, 2), default=0.0)
    trend_score = Column(Numeric(5, 2), default=0.0)
    
    # Platform-specific data
    platform_metadata = Column(JSON)
    algorithm_insights = Column(JSON)
    hashtag_performance = Column(JSON)
    
    # Comparison metrics
    category_rank = Column(Integer)
    similar_content_performance = Column(JSON)
    competitor_analysis = Column(JSON)
    
    is_active = Column(Boolean, default=True, nullable=False)
    
    __table_args__ = (
        Index('idx_content_perf_user_platform', 'user_id', 'platform'),
        Index('idx_content_perf_published', 'published_at'),
        Index('idx_content_perf_format', 'content_format'),
        Index('idx_content_perf_score', 'performance_score'),
        Index('idx_content_perf_revenue', 'total_revenue'),
        Index('idx_content_perf_engagement', 'engagement_rate'),
    )


class MetricsHistory(Base):
    """    Database model for historical metrics tracking
    """    __tablename__ = "metrics_history"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_performance_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    content_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Metric details
    metric_type = Column(String(50), nullable=False, index=True)
    metric_value = Column(Numeric(15, 4), nullable=False)
    previous_value = Column(Numeric(15, 4))
    change_amount = Column(Numeric(15, 4))
    change_percentage = Column(Numeric(8, 4))
    
    # Context
    platform = Column(String(50), nullable=False, index=True)
    measurement_timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    collection_method = Column(String(50))  # api, manual, estimated
    
    # Metadata
    external_factors = Column(JSON)  # holidays, events, trends
    campaign_context = Column(JSON)  # active campaigns, promotions
    platform_changes = Column(JSON)  # algorithm updates, feature changes
    
    # Quality indicators
    data_confidence = Column(Numeric(3, 2), default=1.0)
    is_outlier = Column(Boolean, default=False)
    outlier_reason = Column(String(200))
    
    # Aggregation context
    aggregation_period = Column(String(20))  # hourly, daily, weekly
    is_real_time = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    __table_args__ = (
        Index('idx_metrics_hist_content_metric', 'content_id', 'metric_type'),
        Index('idx_metrics_hist_platform_time', 'platform', 'measurement_timestamp'),
        Index('idx_metrics_hist_user_time', 'user_id', 'measurement_timestamp'),
    )


class PerformanceAlerts(Base):
    """    Database model for performance alerts and notifications
    """    __tablename__ = "performance_alerts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    content_id = Column(UUID(as_uuid=True), index=True)
    
    # Alert configuration
    alert_type = Column(String(50), nullable=False)  # threshold, anomaly, trend
    metric_type = Column(String(50), nullable=False)
    threshold_value = Column(Numeric(15, 4))
    comparison_operator = Column(String(10))  # >, <, =, >=, <=
    
    # Alert details
    alert_title = Column(String(200), nullable=False)
    alert_description = Column(Text)
    severity_level = Column(String(20), default="medium")  # low, medium, high, critical
    
    # Trigger conditions
    trigger_conditions = Column(JSON)
    time_window = Column(String(50))  # 1h, 24h, 7d, 30d
    minimum_data_points = Column(Integer, default=1)
    
    # Alert status
    is_active = Column(Boolean, default=True, nullable=False)
    is_triggered = Column(Boolean, default=False)
    last_triggered = Column(DateTime(timezone=True))
    trigger_count = Column(Integer, default=0)
    
    # Notification settings
    notification_channels = Column(JSON)  # email, sms, push, webhook
    notification_frequency = Column(String(20), default="immediate")
    
    # Creation and updates
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        Index('idx_perf_alerts_user_active', 'user_id', 'is_active'),
        Index('idx_perf_alerts_content', 'content_id'),
        Index('idx_perf_alerts_triggered', 'last_triggered'),
    )


class MetricsCollector:
    """    Enterprise metrics collection system with real-time processing
    """    
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.batch_size = 1000
        self.collection_intervals = {
            MetricType.VIEWS: timedelta(minutes=15),
            MetricType.ENGAGEMENT_RATE: timedelta(hours=1),
            MetricType.REVENUE: timedelta(hours=6)
        }
    
    async def collect_metrics(
        self,
        content_id: str,
        platform: PlatformType,
        metrics: Dict[MetricType, Union[int, float, Decimal]],
        timestamp: Optional[datetime] = None
    ) -> bool:
        """        Collect and store performance metrics
        
        Args:
            content_id: Content identifier
            platform: Platform where metrics were collected
            metrics: Dictionary of metrics and their values
            timestamp: Collection timestamp (defaults to now)
            
        Returns:
            Success status
        """        if timestamp is None:
            timestamp = datetime.now(timezone.utc)
        
        try:
            # Get or create content performance record
            content_performance = self.db_session.query(ContentPerformance).filter(
                ContentPerformance.content_id == content_id,
                ContentPerformance.platform == platform.value
            ).first()
            
            if not content_performance:
                logger.warning(f"Content performance record not found: {content_id} on {platform.value}")
                return False
            
            # Update main performance record
            previous_values = {}
            for metric_type, value in metrics.items():
                field_name = self._get_field_name(metric_type)
                if field_name and hasattr(content_performance, field_name):
                    previous_value = getattr(content_performance, field_name)
                    previous_values[metric_type] = previous_value
                    setattr(content_performance, field_name, value)
            
            content_performance.last_updated = timestamp
            
            # Create historical records
            for metric_type, value in metrics.items():
                previous_value = previous_values.get(metric_type, 0)
                change_amount = value - previous_value if previous_value else value
                change_percentage = (change_amount / previous_value * 100) if previous_value > 0 else 0
                
                history_record = MetricsHistory(
                    content_performance_id=content_performance.id,
                    content_id=content_id,
                    user_id=content_performance.user_id,
                    metric_type=metric_type.value,
                    metric_value=value,
                    previous_value=previous_value,
                    change_amount=change_amount,
                    change_percentage=change_percentage,
                    platform=platform.value,
                    measurement_timestamp=timestamp,
                    collection_method="api"
                )
                
                self.db_session.add(history_record)
            
            self.db_session.commit()
            
            # Check for alerts
            await self._check_performance_alerts(content_performance, metrics)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to collect metrics for {content_id}: {str(e)}")
            self.db_session.rollback()
            return False
    
    async def batch_collect_metrics(
        self,
        metrics_batch: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """        Collect metrics in batch for better performance
        
        Args:
            metrics_batch: List of metric collection requests
            
        Returns:
            Batch processing results
        """        successful = 0
        failed = 0
        errors = []
        
        for batch_item in metrics_batch:
            try:
                success = await self.collect_metrics(
                    content_id=batch_item['content_id'],
                    platform=PlatformType(batch_item['platform']),
                    metrics={
                        MetricType(k): v for k, v in batch_item['metrics'].items()
                    },
                    timestamp=batch_item.get('timestamp')
                )
                
                if success:
                    successful += 1
                else:
                    failed += 1
                    
            except Exception as e:
                failed += 1
                errors.append(f"Item {batch_item.get('content_id', 'unknown')}: {str(e)}")
        
        return {
            'total_processed': len(metrics_batch),
            'successful': successful,
            'failed': failed,
            'errors': errors
        }
    
    def _get_field_name(self, metric_type: MetricType) -> Optional[str]:
        """Map metric type to database field name"""        mapping = {
            MetricType.VIEWS: 'total_views',
            MetricType.LIKES: 'total_likes',
            MetricType.SHARES: 'total_shares',
            MetricType.COMMENTS: 'total_comments',
            MetricType.DOWNLOADS: 'total_downloads',
            MetricType.PLAYS: 'total_plays',
            MetricType.ENGAGEMENT_RATE: 'engagement_rate',
            MetricType.RETENTION_RATE: 'retention_rate',
            MetricType.CLICK_THROUGH_RATE: 'click_through_rate',
            MetricType.CONVERSION_RATE: 'conversion_rate',
            MetricType.REVENUE: 'total_revenue'
        }
        return mapping.get(metric_type)
    
    async def _check_performance_alerts(
        self,
        content_performance: ContentPerformance,
        metrics: Dict[MetricType, Union[int, float, Decimal]]
    ):
        """Check if any performance alerts should be triggered"""        # Get active alerts for this user/content
        alerts = self.db_session.query(PerformanceAlerts).filter(
            PerformanceAlerts.user_id == content_performance.user_id,
            PerformanceAlerts.is_active == True
        ).all()
        
        current_time = datetime.now(timezone.utc)
        
        for alert in alerts:
            # Check if alert applies to this content or is global
            if alert.content_id and str(alert.content_id) != str(content_performance.content_id):
                continue
            
            metric_type = MetricType(alert.metric_type)
            if metric_type not in metrics:
                continue
            
            current_value = metrics[metric_type]
            threshold = alert.threshold_value
            operator = alert.comparison_operator
            
            # Check threshold condition
            should_trigger = False
            if operator == '>' and current_value > threshold:
                should_trigger = True
            elif operator == '<' and current_value < threshold:
                should_trigger = True
            elif operator == '>=' and current_value >= threshold:
                should_trigger = True
            elif operator == '<=' and current_value <= threshold:
                should_trigger = True
            elif operator == '=' and current_value == threshold:
                should_trigger = True
            
            if should_trigger and not alert.is_triggered:
                alert.is_triggered = True
                alert.last_triggered = current_time
                alert.trigger_count += 1
                
                # Here you would integrate with notification system
                logger.info(f"Performance alert triggered: {alert.alert_title} for user {content_performance.user_id}")


class PerformanceTracker:
    """    Enterprise performance tracking with analytics and insights
    """    
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.metrics_collector = MetricsCollector(db_session)
    
    async def create_content_performance_record(
        self,
        content_id: str,
        user_id: str,
        creator_type: str,
        content_format: ContentFormat,
        platform: PlatformType,
        metadata: Dict[str, Any]
    ) -> str:
        """        Create initial performance tracking record for new content
        
        Args:
            content_id: Content identifier
            user_id: Creator user ID
            creator_type: Type of creator
            content_format: Format of content
            platform: Distribution platform
            metadata: Additional metadata
            
        Returns:
            Performance record ID
        """        performance_record = ContentPerformance(
            content_id=content_id,
            user_id=user_id,
            creator_type=creator_type,
            content_format=content_format.value,
            platform=platform.value,
            platform_content_id=metadata.get('platform_content_id'),
            distribution_url=metadata.get('distribution_url'),
            published_at=metadata.get('published_at', datetime.now(timezone.utc)),
            platform_metadata=metadata
        )
        
        self.db_session.add(performance_record)
        self.db_session.commit()
        
        logger.info(f"Created performance record for content: {content_id} on {platform.value}")
        return str(performance_record.id)
    
    async def get_content_performance(
        self,
        content_id: str,
        platform: Optional[PlatformType] = None,
        time_range: Optional[timedelta] = None
    ) -> List[Dict[str, Any]]:
        """        Get performance data for content
        
        Args:
            content_id: Content identifier
            platform: Optional platform filter
            time_range: Optional time range filter
            
        Returns:
            List of performance data
        """        query = self.db_session.query(ContentPerformance).filter(
            ContentPerformance.content_id == content_id,
            ContentPerformance.is_active == True
        )
        
        if platform:
            query = query.filter(ContentPerformance.platform == platform.value)
        
        if time_range:
            cutoff = datetime.now(timezone.utc) - time_range
            query = query.filter(ContentPerformance.published_at >= cutoff)
        
        performance_records = query.all()
        
        results = []
        for record in performance_records:
            performance_data = {
                'content_id': str(record.content_id),
                'platform': record.platform,
                'metrics': {
                    'total_views': int(record.total_views),
                    'total_likes': int(record.total_likes),
                    'total_shares': int(record.total_shares),
                    'total_comments': int(record.total_comments),
                    'engagement_rate': float(record.engagement_rate),
                    'total_revenue': float(record.total_revenue)
                },
                'demographics': {
                    'top_countries': record.top_countries,
                    'age_demographics': record.age_demographics,
                    'gender_demographics': record.gender_demographics
                },
                'scores': {
                    'performance_score': float(record.performance_score),
                    'virality_score': float(record.virality_score),
                    'quality_score': float(record.quality_score)
                },
                'published_at': record.published_at.isoformat(),
                'last_updated': record.last_updated.isoformat()
            }
            results.append(performance_data)
        
        return results
    
    async def get_performance_trends(
        self,
        user_id: str,
        metric_type: MetricType,
        time_range: timedelta = timedelta(days=30),
        platform: Optional[PlatformType] = None
    ) -> Dict[str, Any]:
        """        Get performance trends for user content
        
        Args:
            user_id: User identifier
            metric_type: Type of metric to analyze
            time_range: Time range for analysis
            platform: Optional platform filter
            
        Returns:
            Trend analysis data
        """        cutoff_date = datetime.now(timezone.utc) - time_range
        
        query = self.db_session.query(MetricsHistory).filter(
            MetricsHistory.user_id == user_id,
            MetricsHistory.metric_type == metric_type.value,
            MetricsHistory.measurement_timestamp >= cutoff_date
        )
        
        if platform:
            query = query.filter(MetricsHistory.platform == platform.value)
        
        metrics_data = query.order_by(MetricsHistory.measurement_timestamp).all()
        
        if not metrics_data:
            return {'trend': 'no_data', 'data_points': 0}
        
        # Calculate trend
        values = [float(record.metric_value) for record in metrics_data]
        timestamps = [record.measurement_timestamp for record in metrics_data]
        
        # Simple trend calculation
        if len(values) >= 2:
            recent_avg = sum(values[-len(values)//4:]) / max(len(values)//4, 1)
            earlier_avg = sum(values[:len(values)//4]) / max(len(values)//4, 1)
            
            if recent_avg > earlier_avg * 1.1:
                trend = 'increasing'
            elif recent_avg < earlier_avg * 0.9:
                trend = 'decreasing'
            else:
                trend = 'stable'
        else:
            trend = 'insufficient_data'
        
        return {
            'metric_type': metric_type.value,
            'trend': trend,
            'data_points': len(values),
            'min_value': min(values),
            'max_value': max(values),
            'avg_value': sum(values) / len(values),
            'latest_value': values[-1] if values else 0,
            'time_range_days': time_range.days,
            'data': [
                {
                    'value': float(record.metric_value),
                    'timestamp': record.measurement_timestamp.isoformat(),
                    'change_percentage': float(record.change_percentage) if record.change_percentage else 0
                }
                for record in metrics_data
            ]
        }
    
    async def get_creator_analytics_summary(
        self,
        user_id: str,
        time_range: timedelta = timedelta(days=30)
    ) -> Dict[str, Any]:
        """        Get comprehensive analytics summary for creator
        
        Args:
            user_id: Creator user ID
            time_range: Analysis time range
            
        Returns:
            Analytics summary
        """        cutoff_date = datetime.now(timezone.utc) - time_range
        
        # Get content performance
        performance_records = self.db_session.query(ContentPerformance).filter(
            ContentPerformance.user_id == user_id,
            ContentPerformance.published_at >= cutoff_date,
            ContentPerformance.is_active == True
        ).all()
        
        if not performance_records:
            return {'status': 'no_data', 'time_range_days': time_range.days}
        
        # Aggregate metrics
        total_views = sum(record.total_views for record in performance_records)
        total_revenue = sum(record.total_revenue for record in performance_records)
        avg_engagement = sum(record.engagement_rate for record in performance_records) / len(performance_records)
        
        # Platform distribution
        platform_stats = {}
        for record in performance_records:
            platform = record.platform
            if platform not in platform_stats:
                platform_stats[platform] = {'count': 0, 'views': 0, 'revenue': 0}
            platform_stats[platform]['count'] += 1
            platform_stats[platform]['views'] += record.total_views
            platform_stats[platform]['revenue'] += float(record.total_revenue)
        
        # Content format distribution
        format_stats = {}
        for record in performance_records:
            content_format = record.content_format
            if content_format not in format_stats:
                format_stats[content_format] = {'count': 0, 'avg_performance': 0}
            format_stats[content_format]['count'] += 1
        
        # Top performing content
        top_content = sorted(
            performance_records,
            key=lambda x: x.performance_score,
            reverse=True
        )[:5]
        
        return {
            'user_id': user_id,
            'time_range_days': time_range.days,
            'summary': {
                'total_content_pieces': len(performance_records),
                'total_views': int(total_views),
                'total_revenue': float(total_revenue),
                'average_engagement_rate': float(avg_engagement),
                'platforms_used': len(platform_stats)
            },
            'platform_distribution': platform_stats,
            'format_distribution': format_stats,
            'top_performing_content': [
                {
                    'content_id': str(record.content_id),
                    'platform': record.platform,
                    'performance_score': float(record.performance_score),
                    'total_views': int(record.total_views),
                    'total_revenue': float(record.total_revenue)
                }
                for record in top_content
            ],
            'generated_at': datetime.now(timezone.utc).isoformat()
        }
