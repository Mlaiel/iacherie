"""
 Revenue Tracker - Ultra-Advanced Multi-Platform Revenue Tracking System
=========================================================================

Industrial-grade revenue tracking system providing real-time monitoring,
historical analytics, performance insights, and automated notifications
for content creators across all platforms.

Created by: Fahed Mlaiel <mlaiel@live.de>
© 2025 Fahed Mlaiel. All rights reserved.

Team Specialists:
- Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer

 STRICT COPYRIGHT WARNING - UNAUTHORIZED USE PROHIBITED 
Contact mlaiel@live.de for licensing inquiries.

Business Logic: Multi-Format Upload → AI Protection → SEO → Collaboration → Revenue Tracking
==========================================================================================
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
import uuid
import json
import numpy as np
from concurrent.futures import ThreadPoolExecutor

from ...core.database import DatabaseManager
from ...core.security import SecurityManager
from ...core.monitoring import MetricsCollector
from ...core.notifications import NotificationManager
from ...ai.engines.trend_analysis_engine import TrendAnalysisEngine
from ...integrations.platforms import PlatformManager

logger = logging.getLogger(__name__)


class TrackingFrequency(Enum):
    """Revenue tracking frequency options"""
    REAL_TIME = "real_time"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class TrackingStatus(Enum):
    """Revenue tracking status"""
    ACTIVE = "active"
    PAUSED = "paused"
    ERROR = "error"
    MAINTENANCE = "maintenance"
    STOPPED = "stopped"


@dataclass
class RevenueSnapshot:
    """Revenue snapshot data structure"""
    snapshot_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    creator_id: str = ""
    platform: str = ""
    revenue_streams: Dict[str, Decimal] = field(default_factory=dict)
    total_revenue: Decimal = Decimal('0')
    period_start: datetime = field(default_factory=datetime.utcnow)
    period_end: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class TrackingAlert:
    """Revenue tracking alert configuration"""
    alert_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    creator_id: str = ""
    alert_type: str = ""
    threshold_value: Decimal = Decimal('0')
    comparison_operator: str = ">"
    frequency: TrackingFrequency = TrackingFrequency.DAILY
    is_active: bool = True
    last_triggered: Optional[datetime] = None
    notification_channels: List[str] = field(default_factory=list)


class RevenueTracker:
    """
    Ultra-advanced revenue tracking system for multi-platform content creators
    
    Features:
    - Real-time revenue monitoring across all platforms
    - Historical revenue analytics and trend analysis
    - Automated alerts and notifications
    - Performance benchmarking and insights
    - Revenue goal tracking and forecasting
    - Anomaly detection and fraud prevention
    - Multi-currency tracking and conversion
    - Custom dashboard and reporting
    """
    
    def __init__(self,
                 db_manager: DatabaseManager,
                 security_manager: SecurityManager,
                 metrics_collector: MetricsCollector,
                 notification_manager: NotificationManager):
        self.db = db_manager
        self.security = security_manager
        self.metrics = metrics_collector
        self.notifications = notification_manager
        self.trend_analysis = TrendAnalysisEngine()
        self.platform_manager = PlatformManager()
        
        # Tracking configuration
        self._tracking_configs = {}
        self._active_trackers = {}
        self._alert_configs = {}
        
        # Performance metrics
        self._tracking_metrics = {
            'snapshots_taken': 0,
            'alerts_triggered': 0,
            'errors_encountered': 0,
            'uptime_start': datetime.utcnow()
        }
        
    async def initialize(self):
        """Initialize the revenue tracking system"""



        try:
            # Load tracking configurations
            await self._load_tracking_configurations()
            
            # Initialize trend analysis engine
            await self.trend_analysis.initialize()
            
            # Setup platform connections
            await self.platform_manager.initialize()
            
            # Start background tracking tasks
            await self._start_background_tasks()
            
            logger.info("Revenue tracker initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize revenue tracker: {e}")
            raise

    async def start_tracking(self,
                           creator_id: str,
                           platforms: List[str],
                           frequency: TrackingFrequency = TrackingFrequency.HOURLY,
                           custom_config: Optional[Dict[str, Any]] = None) -> str:
        """
        Start revenue tracking for a creator across specified platforms
        
        Args:
            creator_id: Unique creator identifier
            platforms: List of platforms to track
            frequency: Tracking frequency
            custom_config: Custom tracking configuration
            
        Returns:
            Tracking session ID
        """



        try:
            # Validate creator and platforms
            await self._validate_tracking_request(creator_id, platforms)
            
            # Generate tracking session ID
            tracking_id = str(uuid.uuid4())
            
            # Create tracking configuration
            tracking_config = {
                'tracking_id': tracking_id,
                'creator_id': creator_id,
                'platforms': platforms,
                'frequency': frequency,
                'status': TrackingStatus.ACTIVE,
                'started_at': datetime.utcnow(),
                'config': custom_config or {},
                'snapshots_taken': 0,
                'last_snapshot': None,
                'next_snapshot': self._calculate_next_snapshot_time(frequency)
            }
            
            # Store tracking configuration
            await self._store_tracking_config(tracking_config)
            
            # Add to active trackers
            self._active_trackers[tracking_id] = tracking_config
            
            # Schedule initial snapshot
            await self._schedule_revenue_snapshot(tracking_id)
            
            logger.info(f"Started revenue tracking for creator {creator_id} with ID {tracking_id}")
            return tracking_id
            
        except Exception as e:
            logger.error(f"Failed to start revenue tracking: {e}")
            raise

    async def stop_tracking(self, tracking_id: str, creator_id: str) -> bool:
        """
        Stop revenue tracking for a specific session
        
        Args:
            tracking_id: Tracking session ID
            creator_id: Creator ID for validation
            
        Returns:
            Success status
        """



        try:
            # Validate tracking session
            if tracking_id not in self._active_trackers:
                raise ValueError(f"Tracking session {tracking_id} not found")
            
            tracking_config = self._active_trackers[tracking_id]
            
            # Validate creator ownership
            if tracking_config['creator_id'] != creator_id:
                raise ValueError("Unauthorized access to tracking session")
            
            # Update status to stopped
            tracking_config['status'] = TrackingStatus.STOPPED
            tracking_config['stopped_at'] = datetime.utcnow()
            
            # Update database
            await self._update_tracking_status(tracking_id, TrackingStatus.STOPPED)
            
            # Remove from active trackers
            del self._active_trackers[tracking_id]
            
            logger.info(f"Stopped revenue tracking for session {tracking_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop revenue tracking: {e}")
            return False

    async def take_revenue_snapshot(self,
                                  tracking_id: str,
                                  force_snapshot: bool = False) -> RevenueSnapshot:
        """
        Take a revenue snapshot for a tracking session
        
        Args:
            tracking_id: Tracking session ID
            force_snapshot: Force snapshot even if not scheduled
            
        Returns:
            Revenue snapshot data
        """



        try:
            # Get tracking configuration
            if tracking_id not in self._active_trackers:
                raise ValueError(f"Tracking session {tracking_id} not active")
            
            tracking_config = self._active_trackers[tracking_id]
            
            # Check if snapshot is due (unless forced)
            if not force_snapshot and not self._is_snapshot_due(tracking_config):
                raise ValueError("Snapshot not due yet")
            
            # Collect revenue data from all platforms
            revenue_data = await self._collect_platform_revenue_data(tracking_config)
            
            # Create revenue snapshot
            snapshot = RevenueSnapshot(
                creator_id=tracking_config['creator_id'],
                platform="multi_platform",
                revenue_streams=revenue_data['streams'],
                total_revenue=revenue_data['total'],
                period_start=tracking_config['last_snapshot'] or tracking_config['started_at'],
                period_end=datetime.utcnow(),
                metadata={
                    'tracking_id': tracking_id,
                    'platforms_tracked': tracking_config['platforms'],
                    'snapshot_type': 'forced' if force_snapshot else 'scheduled',
                    'collection_duration': revenue_data['collection_duration'],
                    'data_quality_score': revenue_data['quality_score']
                }
            )
            
            # Store snapshot
            await self._store_revenue_snapshot(snapshot)
            
            # Update tracking configuration
            tracking_config['snapshots_taken'] += 1
            tracking_config['last_snapshot'] = datetime.utcnow()
            tracking_config['next_snapshot'] = self._calculate_next_snapshot_time(
                tracking_config['frequency']
            )
            
            # Update metrics
            self._tracking_metrics['snapshots_taken'] += 1
            await self.metrics.record_revenue_snapshot(snapshot)
            
            # Check for alerts
            await self._check_revenue_alerts(snapshot)
            
            # Analyze trends
            await self._analyze_revenue_trends(snapshot)
            
            logger.info(f"Revenue snapshot taken for tracking {tracking_id}: ${snapshot.total_revenue}")
            return snapshot
            
        except Exception as e:
            logger.error(f"Failed to take revenue snapshot: {e}")
            self._tracking_metrics['errors_encountered'] += 1
            raise

    async def get_tracking_status(self,
                                creator_id: str,
                                tracking_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get tracking status for a creator or specific session
        
        Args:
            creator_id: Creator ID
            tracking_id: Specific tracking session (optional)
            
        Returns:
            Tracking status information
        """



        try:
            if tracking_id:
                # Get specific tracking session status
                if tracking_id in self._active_trackers:
                    config = self._active_trackers[tracking_id]
                    return {
                        'tracking_id': tracking_id,
                        'status': config['status'].value,
                        'platforms': config['platforms'],
                        'frequency': config['frequency'].value,
                        'started_at': config['started_at'].isoformat(),
                        'snapshots_taken': config['snapshots_taken'],
                        'last_snapshot': config['last_snapshot'].isoformat() if config['last_snapshot'] else None,
                        'next_snapshot': config['next_snapshot'].isoformat(),
                    }
                else:
                    # Check database for inactive sessions
                    return await self._get_inactive_tracking_status(tracking_id)
            
            else:
                # Get all tracking sessions for creator
                return await self._get_creator_tracking_status(creator_id)
                
        except Exception as e:
            logger.error(f"Failed to get tracking status: {e}")
            raise

    async def get_revenue_history(self,
                                creator_id: str,
                                date_range: Tuple[datetime, datetime],
                                platforms: Optional[List[str]] = None,
                                aggregation: str = "daily") -> Dict[str, Any]:
        """
        Get historical revenue data for a creator
        
        Args:
            creator_id: Creator ID
            date_range: Date range for history
            platforms: Specific platforms (optional)
            aggregation: Data aggregation level (daily/weekly/monthly)
            
        Returns:
            Historical revenue data
        """



        try:
            # Build query conditions
            conditions = ["creator_id = %s", "created_at BETWEEN %s AND %s"]
            params = [creator_id, date_range[0], date_range[1]]
            
            if platforms:
                # Filter by platforms in metadata
                platforms_filter = " OR ".join([
                    f"metadata::json->'platforms_tracked' @> '[\"{platform}\"]'"
                    for platform in platforms
                ])
                conditions.append(f"({platforms_filter})")
            
            # Determine aggregation query
            if aggregation == "hourly":
                date_trunc = "hour"
            elif aggregation == "daily":
                date_trunc = "day"
            elif aggregation == "weekly":
                date_trunc = "week"
            elif aggregation == "monthly":
                date_trunc = "month"
            else:
                date_trunc = "day"
            
            # Execute query
            query = f"""
                SELECT 
                    DATE_TRUNC('{date_trunc}', created_at) as period,
                    SUM(total_revenue) as total_revenue,
                    AVG(total_revenue) as avg_revenue,
                    COUNT(*) as snapshot_count,
                    MIN(total_revenue) as min_revenue,
                    MAX(total_revenue) as max_revenue
                FROM revenue_snapshots 
                WHERE {' AND '.join(conditions)}
                GROUP BY DATE_TRUNC('{date_trunc}', created_at)
                ORDER BY period ASC
            """
            
            history_data = await self.db.fetch_all(query, params)
            
            # Calculate additional metrics
            total_periods = len(history_data)
            total_revenue = sum(row['total_revenue'] for row in history_data)
            avg_period_revenue = total_revenue / total_periods if total_periods > 0 else 0
            
            # Growth calculation
            growth_rate = 0
            if len(history_data) >= 2:
                first_period = history_data[0]['total_revenue']
                last_period = history_data[-1]['total_revenue']
                if first_period > 0:
                    growth_rate = ((last_period - first_period) / first_period) * 100
            
            return {
                'creator_id': creator_id,
                'date_range': {
                    'start': date_range[0].isoformat(),
                    'end': date_range[1].isoformat()
                },
                'aggregation': aggregation,
                'summary': {
                    'total_periods': total_periods,
                    'total_revenue': float(total_revenue),
                    'average_period_revenue': float(avg_period_revenue),
                    'growth_rate_percent': round(growth_rate, 2),
                    'highest_revenue_period': float(max((row['max_revenue'] for row in history_data), default=0)),
                    'lowest_revenue_period': float(min((row['min_revenue'] for row in history_data), default=0))
                },
                'data': [
                    {
                        'period': row['period'].isoformat(),
                        'total_revenue': float(row['total_revenue']),
                        'average_revenue': float(row['avg_revenue']),
                        'snapshot_count': row['snapshot_count'],
                        'min_revenue': float(row['min_revenue']),
                        'max_revenue': float(row['max_revenue'])
                    }
                    for row in history_data
                ],
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get revenue history: {e}")
            raise

    async def setup_revenue_alert(self,
                                creator_id: str,
                                alert_config: Dict[str, Any]) -> str:
        """
        Setup automated revenue alert
        
        Args:
            creator_id: Creator ID
            alert_config: Alert configuration
            
        Returns:
            Alert ID
        """



        try:
            # Validate alert configuration
            await self._validate_alert_config(alert_config)
            
            # Create alert
            alert = TrackingAlert(
                creator_id=creator_id,
                alert_type=alert_config['type'],
                threshold_value=Decimal(str(alert_config['threshold'])),
                comparison_operator=alert_config.get('operator', '>'),
                frequency=TrackingFrequency(alert_config.get('frequency', 'daily')),
                notification_channels=alert_config.get('channels', ['email'])
            )
            
            # Store alert
            await self._store_revenue_alert(alert)
            
            # Add to active alerts
            self._alert_configs[alert.alert_id] = alert
            
            logger.info(f"Revenue alert {alert.alert_id} created for creator {creator_id}")
            return alert.alert_id
            
        except Exception as e:
            logger.error(f"Failed to setup revenue alert: {e}")
            raise

    async def _collect_platform_revenue_data(self, tracking_config: Dict[str, Any]) -> Dict[str, Any]:
        """Collect revenue data from all tracked platforms"""
        start_time = datetime.utcnow()
        revenue_streams = {}
        total_revenue = Decimal('0')
        quality_scores = []
        
        try:
            # Collect data from each platform concurrently
            tasks = []
            for platform in tracking_config['platforms']:
                task = self._collect_single_platform_data(
                    platform, 
                    tracking_config['creator_id'],
                    tracking_config.get('config', {}).get(platform, {})
                )
                tasks.append(task)
            
            # Wait for all platform data collection
            platform_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for i, platform in enumerate(tracking_config['platforms']):
                if not isinstance(platform_results[i], Exception):
                    platform_data = platform_results[i]
                    revenue_streams[platform] = platform_data['revenue']
                    total_revenue += platform_data['revenue']
                    quality_scores.append(platform_data['quality_score'])
                else:
                    logger.error(f"Failed to collect data from {platform}: {platform_results[i]}")
                    revenue_streams[platform] = Decimal('0')
                    quality_scores.append(0.0)
            
            collection_duration = (datetime.utcnow() - start_time).total_seconds()
            average_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
            
            return {
                'streams': revenue_streams,
                'total': total_revenue,
                'collection_duration': collection_duration,
                'quality_score': average_quality
            }
            
        except Exception as e:
            logger.error(f"Failed to collect platform revenue data: {e}")
            raise

    async def _collect_single_platform_data(self,
                                           platform: str,
                                           creator_id: str,
                                           platform_config: Dict[str, Any]) -> Dict[str, Any]:
        """Collect revenue data from a single platform"""



        try:
            # Get platform integration
            platform_integration = await self.platform_manager.get_platform(platform)
            
            # Fetch latest revenue data
            revenue_data = await platform_integration.fetch_current_revenue(
                creator_id, platform_config
            )
            
            # Validate data quality
            quality_score = await self._assess_data_quality(platform, revenue_data)
            
            return {
                'revenue': Decimal(str(revenue_data.get('total_revenue', 0))),
                'quality_score': quality_score,
                'data_timestamp': datetime.utcnow(),
                'raw_data': revenue_data
            }
            
        except Exception as e:
            logger.error(f"Failed to collect {platform} data: {e}")
            return {
                'revenue': Decimal('0'),
                'quality_score': 0.0,
                'data_timestamp': datetime.utcnow(),
                'error': str(e)
            }

    async def _check_revenue_alerts(self, snapshot: RevenueSnapshot):
        """Check if any alerts should be triggered based on snapshot"""



        try:
            # Get active alerts for creator
            creator_alerts = [
                alert for alert in self._alert_configs.values()
                if alert.creator_id == snapshot.creator_id and alert.is_active
            ]
            
            for alert in creator_alerts:
                should_trigger = await self._evaluate_alert_condition(alert, snapshot)
                
                if should_trigger:
                    await self._trigger_revenue_alert(alert, snapshot)
                    self._tracking_metrics['alerts_triggered'] += 1
            
        except Exception as e:
            logger.error(f"Failed to check revenue alerts: {e}")

    async def _evaluate_alert_condition(self, alert: TrackingAlert, snapshot: RevenueSnapshot) -> bool:
        """Evaluate if alert condition is met"""



        try:
            comparison_value = snapshot.total_revenue
            threshold = alert.threshold_value
            operator = alert.comparison_operator
            
            if operator == '>':
                return comparison_value > threshold
            elif operator == '<':
                return comparison_value < threshold
            elif operator == '>=':
                return comparison_value >= threshold
            elif operator == '<=':
                return comparison_value <= threshold
            elif operator == '==':
                return comparison_value == threshold
            else:
                return False
                
        except Exception as e:
            logger.error(f"Failed to evaluate alert condition: {e}")
            return False

    async def _trigger_revenue_alert(self, alert: TrackingAlert, snapshot: RevenueSnapshot):
        """Trigger revenue alert notification"""



        try:
            # Prepare notification data
            notification_data = {
                'alert_id': alert.alert_id,
                'creator_id': alert.creator_id,
                'alert_type': alert.alert_type,
                'threshold_value': float(alert.threshold_value),
                'current_value': float(snapshot.total_revenue),
                'snapshot_id': snapshot.snapshot_id,
                'triggered_at': datetime.utcnow().isoformat()
            }
            
            # Send notifications through configured channels
            for channel in alert.notification_channels:
                await self.notifications.send_revenue_alert(
                    channel, alert.creator_id, notification_data
                )
            
            # Update alert last triggered time
            alert.last_triggered = datetime.utcnow()
            await self._update_alert_last_triggered(alert.alert_id)
            
            logger.info(f"Revenue alert {alert.alert_id} triggered for creator {alert.creator_id}")
            
        except Exception as e:
            logger.error(f"Failed to trigger revenue alert: {e}")

    async def _analyze_revenue_trends(self, snapshot: RevenueSnapshot):
        """Analyze revenue trends and patterns"""



        try:
            # Get historical data for trend analysis
            historical_snapshots = await self.db.fetch_all("""
                SELECT total_revenue, created_at
                FROM revenue_snapshots 
                WHERE creator_id = %s 
                ORDER BY created_at DESC 
                LIMIT 30
            """, (snapshot.creator_id,))
            
            if len(historical_snapshots) < 3:
                return  # Not enough data for trend analysis
            
            # Prepare data for analysis
            revenue_values = [float(s['total_revenue']) for s in historical_snapshots]
            timestamps = [s['created_at'] for s in historical_snapshots]
            
            # Perform trend analysis
            trends = await self.trend_analysis.analyze_revenue_trends(
                revenue_values, timestamps
            )
            
            # Store trend insights
            await self._store_trend_analysis(snapshot.creator_id, trends)
            
        except Exception as e:
            logger.error(f"Failed to analyze revenue trends: {e}")

    def _calculate_next_snapshot_time(self, frequency: TrackingFrequency) -> datetime:
        """Calculate next snapshot time based on frequency"""
        now = datetime.utcnow()
        
        if frequency == TrackingFrequency.REAL_TIME:
            return now + timedelta(minutes=5)
        elif frequency == TrackingFrequency.HOURLY:
            return now + timedelta(hours=1)
        elif frequency == TrackingFrequency.DAILY:
            return now + timedelta(days=1)
        elif frequency == TrackingFrequency.WEEKLY:
            return now + timedelta(weeks=1)
        elif frequency == TrackingFrequency.MONTHLY:
            return now + timedelta(days=30)
        else:
            return now + timedelta(hours=1)

    def _is_snapshot_due(self, tracking_config: Dict[str, Any]) -> bool:
        """Check if snapshot is due for a tracking configuration"""
        next_snapshot = tracking_config.get('next_snapshot')
        if not next_snapshot:
            return True
        
        return datetime.utcnow() >= next_snapshot

    async def _validate_tracking_request(self, creator_id: str, platforms: List[str]):
        """Validate tracking request parameters"""
        if not creator_id:
            raise ValueError("Creator ID is required")
        
        if not platforms:
            raise ValueError("At least one platform must be specified")
        
        # Validate platforms are supported
        supported_platforms = await self.platform_manager.get_supported_platforms()
        for platform in platforms:
            if platform not in supported_platforms:
                raise ValueError(f"Platform {platform} is not supported")

    async def _load_tracking_configurations(self):
        """Load existing tracking configurations from database"""



        try:
            configs = await self.db.fetch_all("""
                SELECT * FROM revenue_tracking_configs 
                WHERE status = 'active'
            """)
            
            for config in configs:
                self._active_trackers[config['tracking_id']] = {
                    'tracking_id': config['tracking_id'],
                    'creator_id': config['creator_id'],
                    'platforms': json.loads(config['platforms']),
                    'frequency': TrackingFrequency(config['frequency']),
                    'status': TrackingStatus(config['status']),
                    'started_at': config['started_at'],
                    'config': json.loads(config['config'] or '{}'),
                    'snapshots_taken': config['snapshots_taken'],
                    'last_snapshot': config['last_snapshot'],
                    'next_snapshot': config['next_snapshot']
                }
                
        except Exception as e:
            logger.error(f"Failed to load tracking configurations: {e}")

    async def _store_tracking_config(self, config: Dict[str, Any]):
        """Store tracking configuration in database"""



        try:
            query = """
                INSERT INTO revenue_tracking_configs 
                (tracking_id, creator_id, platforms, frequency, status, 
                 started_at, config, snapshots_taken, next_snapshot)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            await self.db.execute(query, (
                config['tracking_id'],
                config['creator_id'],
                json.dumps(config['platforms']),
                config['frequency'].value,
                config['status'].value,
                config['started_at'],
                json.dumps(config['config']),
                config['snapshots_taken'],
                config['next_snapshot']
            ))
            
        except Exception as e:
            logger.error(f"Failed to store tracking config: {e}")
            raise

    async def _store_revenue_snapshot(self, snapshot: RevenueSnapshot):
        """Store revenue snapshot in database"""



        try:
            query = """
                INSERT INTO revenue_snapshots 
                (snapshot_id, creator_id, platform, revenue_streams, total_revenue,
                 period_start, period_end, metadata, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            await self.db.execute(query, (
                snapshot.snapshot_id,
                snapshot.creator_id,
                snapshot.platform,
                json.dumps({k: str(v) for k, v in snapshot.revenue_streams.items()}),
                snapshot.total_revenue,
                snapshot.period_start,
                snapshot.period_end,
                json.dumps(snapshot.metadata, default=str),
                snapshot.created_at
            ))
            
        except Exception as e:
            logger.error(f"Failed to store revenue snapshot: {e}")
            raise

    async def _start_background_tasks(self):
        """Start background tracking tasks"""
        # This would start asyncio tasks for automated tracking
        # Implementation would depend on specific async framework used
        pass

    async def cleanup(self):
        """Cleanup tracking resources"""



        try:
            # Stop all active tracking sessions
            for tracking_id in list(self._active_trackers.keys()):
                await self._update_tracking_status(tracking_id, TrackingStatus.STOPPED)
            
            # Close platform connections
            await self.platform_manager.cleanup()
            
            logger.info("Revenue tracker cleanup completed")
            
        except Exception as e:
            logger.error(f"Revenue tracker cleanup failed: {e}")
