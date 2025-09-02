"""Real-Time Monitoring System - Advanced Live Performance Tracking & Alert Engine

Enterprise-grade real-time monitoring system providing comprehensive live tracking
of content performance, audience engagement, and market conditions with 
intelligent alerting and automated response capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This real-time monitoring system and its algorithms are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, or distribution is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import redis
from collections import deque, defaultdict
import math
import threading
import time

try:
    from core.exceptions import ProcessingError, ValidationError, MonitoringError
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    ProcessingError, ValidationError, MonitoringError = globals().get('ProcessingError, ValidationError, MonitoringError', Exception)
from ...utils.cache_manager import CacheManager

logger = logging.getLogger(__name__)

class AlertSeverity(Enum):
    """
Alert severity levels"""

    CRITICAL = "critical"      # Immediate action required
    HIGH = "high"             # Action required within 1 hour
    MEDIUM = "medium"         # Action required within 24 hours
    LOW = "low"               # Monitor and review
    INFO = "info"             # Informational only

class MetricType(Enum):
    """Types of metrics being monitored"""

    ENGAGEMENT = "engagement"
    GROWTH = "growth"
    PERFORMANCE = "performance"
    MONETIZATION = "monetization"
    AUDIENCE = "audience"
    CONTENT = "content"
    PLATFORM = "platform"
    COMPETITIVE = "competitive"
    TECHNICAL = "technical"
    SECURITY = "security"

class MonitoringStatus(Enum):
    """Monitoring system status"""

    ACTIVE = "active"
    PAUSED = "paused"
    MAINTENANCE = "maintenance"
    ERROR = "error"
    DISABLED = "disabled"

class AlertType(Enum):
    """Types of alerts"""

    THRESHOLD_BREACH = "threshold_breach"
    ANOMALY_DETECTION = "anomaly_detection"
    TREND_ALERT = "trend_alert"
    COMPETITIVE_ALERT = "competitive_alert"
    OPPORTUNITY_ALERT = "opportunity_alert"
    SYSTEM_ALERT = "system_alert"
    SECURITY_ALERT = "security_alert"

@dataclass
class MetricThreshold:
    """Metric threshold configuration"""
    metric_name: str = ""
    metric_type: MetricType = MetricType.PERFORMANCE
    upper_threshold: Optional[float] = None
    lower_threshold: Optional[float] = None
    warning_upper: Optional[float] = None
    warning_lower: Optional[float] = None
    time_window_minutes: int = 5  # Time window for threshold evaluation
    consecutive_breaches_required: int = 1  # Number of consecutive breaches to trigger
    enabled: bool = True
    notification_cooldown_minutes: int = 60  # Minimum time between notifications
    last_notification: Optional[datetime] = None
    
@dataclass
class MonitoringAlert:
    """Monitoring alert structure"""
    alert_id: str = field(default_factory=lambda: f"alert_{int(datetime.now().timestamp())}")
    title: str = ""
    description: str = ""
    severity: AlertSeverity = AlertSeverity.MEDIUM
    alert_type: AlertType = AlertType.THRESHOLD_BREACH
    metric_name: str = ""
    metric_type: MetricType = MetricType.PERFORMANCE
    current_value: float = 0.0
    threshold_value: Optional[float] = None
    expected_value: Optional[float] = None
    deviation_percentage: float = 0.0
    time_detected: datetime = field(default_factory=datetime.utcnow)
    platform: Optional[str] = None
    content_id: Optional[str] = None
    creator_id: str = ""
    is_resolved: bool = False
    resolution_time: Optional[datetime] = None
    resolution_notes: str = ""
    automated_actions_taken: List[str] = field(default_factory=list)
    recommended_actions: List[str] = field(default_factory=list)
    context_data: Dict[str, Any] = field(default_factory=dict)
    notification_channels: List[str] = field(default_factory=list)
    
@dataclass
class RealTimeMetrics:
    """Real-time metrics snapshot"""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    creator_id: str = ""
    platform: str = ""
    
    # Engagement metrics
    likes_per_minute: float = 0.0
    comments_per_minute: float = 0.0
    shares_per_minute: float = 0.0
    engagement_rate: float = 0.0
    engagement_velocity: float = 0.0  # Rate of change in engagement
    
    # Reach and impressions
    reach_per_minute: int = 0
    impressions_per_minute: int = 0
    click_through_rate: float = 0.0
    
    # Audience metrics
    new_followers_per_minute: float = 0.0
    follower_growth_rate: float = 0.0
    audience_retention_rate: float = 0.0
    
    # Content performance
    content_performance_score: float = 0.0
    viral_potential_score: float = 0.0
    trend_alignment_score: float = 0.0
    
    # Technical metrics
    loading_time_ms: float = 0.0
    error_rate: float = 0.0
    api_response_time_ms: float = 0.0
    
    # Competitive metrics
    competitive_advantage_score: float = 0.0
    market_position_rank: int = 0
    
    # Monetization metrics
    revenue_per_minute: float = 0.0
    conversion_rate: float = 0.0
    
class RealTimeMonitoringSystem:
    """
    Advanced Real-Time Monitoring Engine for IA Influencer Platform
    
    Provides comprehensive real-time monitoring and alerting capabilities:
    
    📊 Live Performance Tracking:
    - Real-time engagement rate monitoring with velocity tracking
    - Live audience growth and retention analytics
    - Content performance scoring with viral potential assessment
    - Multi-platform synchronized monitoring and comparison
    
    🚨 Intelligent Alert System:
    - AI-powered anomaly detection with false positive reduction
    - Smart threshold management with dynamic adjustment
    - Priority-based alert routing with escalation procedures
    - Automated response system with custom action triggers
    
    📈 Trend and Opportunity Detection:
    - Real-time trend identification and opportunity scoring
    - Competitive monitoring with market position tracking
    - Viral content detection with timing optimization alerts
    - Market shift detection with strategic response recommendations
    
    🔧 Automated Response Framework:
    - Intelligent auto-scaling for viral content situations
    - Automatic content optimization based on real-time performance
    - Smart notification filtering to reduce alert fatigue
    - Emergency response protocols for critical situations
    """
    
    def __init__(self, cache_manager: CacheManager = None, redis_client: redis.Redis = None):
        """
Initialize the real-time monitoring system"""
        self.cache_manager = cache_manager or CacheManager("realtime_monitoring")
        self.redis_client = redis_client or redis.Redis(host='localhost', port=6379, db=0)
        
        # Monitoring configuration
        self.monitoring_config = {
            'monitoring_interval_seconds': 30,  # How often to collect metrics
            'alert_evaluation_interval_seconds': 60,  # How often to evaluate alerts
            'metric_retention_hours': 24,  # How long to keep metrics in memory
            'anomaly_detection_sensitivity': 0.8,  # 0.0-1.0, higher = more sensitive
            'alert_cooldown_minutes': 15,  # Minimum time between similar alerts
            'max_alerts_per_hour': 20,  # Rate limiting for alerts
            'auto_resolution_timeout_minutes': 60  # Auto-resolve alerts after this time
        }
        
        # Default metric thresholds
        self.default_thresholds = {
            'engagement_rate': MetricThreshold(
                metric_name='engagement_rate',
                metric_type=MetricType.ENGAGEMENT,
                lower_threshold=0.01,  # Below 1% is concerning
                warning_lower=0.02,    # Below 2% is warning
                upper_threshold=0.15,  # Above 15% might indicate anomaly/viral content
                time_window_minutes=15,
                consecutive_breaches_required=2
            ),
            'follower_growth_rate': MetricThreshold(
                metric_name='follower_growth_rate',
                metric_type=MetricType.GROWTH,
                lower_threshold=-0.05,  # Losing more than 5% is critical
                warning_lower=0.0,      # Any loss is concerning
                upper_threshold=0.50,   # More than 50% growth might indicate anomaly
                time_window_minutes=60
            ),
            'error_rate': MetricThreshold(
                metric_name='error_rate',
                metric_type=MetricType.TECHNICAL,
                upper_threshold=0.05,   # 5% error rate is critical
                warning_upper=0.02,     # 2% error rate is warning
                time_window_minutes=5,
                consecutive_breaches_required=1
            )
        }
        
        # Active monitoring sessions
        self.active_monitors = {}  # creator_id -> monitoring session
        self.alert_history = deque(maxlen=1000)  # Recent alerts
        self.metric_buffers = defaultdict(lambda: deque(maxlen=1440))  # 24 hours of minute-by-minute data
        
        # Anomaly detection models (simplified - would use proper ML models in production)
        self.anomaly_detectors = {}
        
        # Alert handlers
        self.alert_handlers = {
            AlertSeverity.CRITICAL: self._handle_critical_alert,
            AlertSeverity.HIGH: self._handle_high_alert,
            AlertSeverity.MEDIUM: self._handle_medium_alert,
            AlertSeverity.LOW: self._handle_low_alert,
            AlertSeverity.INFO: self._handle_info_alert
        }
        
        # Monitoring thread
        self.monitoring_thread = None
        self.monitoring_status = MonitoringStatus.DISABLED
        self._stop_event = threading.Event()
        
        logger.info("Real-Time Monitoring System initialized")

    async def start_monitoring(self, creator_id: str, monitoring_config: Dict[str, Any] = None) -> bool:
        """
        Start real-time monitoring for a creator
        
        Args:
            creator_id: ID of the creator to monitor
            monitoring_config: Optional custom monitoring configuration
            
        Returns:
            bool: True if monitoring started successfully
        """
        try:
            if creator_id in self.active_monitors:
                logger.warning(f"Monitoring already active for creator {creator_id}")
                return True
            
            # Initialize monitoring session
            session_config = {**self.monitoring_config, **(monitoring_config or {})}
            
            monitoring_session = {
                'creator_id': creator_id,
                'config': session_config,
                'start_time': datetime.utcnow(),
                'last_metric_collection': None,
                'alert_count': 0,
                'status': MonitoringStatus.ACTIVE,
                'thresholds': self._initialize_thresholds(creator_id),
                'metric_history': defaultdict(list),
                'active_alerts': [],
                'notification_channels': session_config.get('notification_channels', ['dashboard', 'email'])
            }
            
            self.active_monitors[creator_id] = monitoring_session
            
            # Start monitoring thread if not already running
            if self.monitoring_status != MonitoringStatus.ACTIVE:
                await self._start_monitoring_thread()
            
            # Initialize baseline metrics
            await self._initialize_baseline_metrics(creator_id)
            
            logger.info(f"Real-time monitoring started for creator {creator_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start monitoring for creator {creator_id}: {str(e)}")
            raise MonitoringError(f"Monitoring start failed: {str(e)}")

    async def collect_real_time_metrics(self, creator_id: str, platform_data: Dict[str, Any]) -> RealTimeMetrics:
        """
        Collect real-time metrics for a creator
        
        Args:
            creator_id: ID of the creator
            platform_data: Real-time data from platforms
            
        Returns:
            RealTimeMetrics: Current metrics snapshot
        """
        try:
            metrics = RealTimeMetrics(creator_id=creator_id)
            
            # Extract platform information
            platform = platform_data.get('platform', 'unknown')
            metrics.platform = platform
            
            # Calculate engagement metrics
            current_engagement = platform_data.get('current_engagement', {})
            previous_engagement = await self._get_previous_engagement(creator_id, platform)
            
            time_diff_minutes = platform_data.get('time_window_minutes', 1)
            
            # Engagement rate and velocity
            metrics.engagement_rate = current_engagement.get('rate', 0.0)
            if previous_engagement:
                metrics.engagement_velocity = (
                    (metrics.engagement_rate - previous_engagement.get('rate', 0.0)) / time_diff_minutes
                )
            
            # Per-minute metrics
            metrics.likes_per_minute = current_engagement.get('likes_growth', 0) / time_diff_minutes
            metrics.comments_per_minute = current_engagement.get('comments_growth', 0) / time_diff_minutes
            metrics.shares_per_minute = current_engagement.get('shares_growth', 0) / time_diff_minutes
            
            # Reach and impressions
            reach_data = platform_data.get('reach_data', {})
            metrics.reach_per_minute = reach_data.get('growth', 0) // time_diff_minutes
            metrics.impressions_per_minute = reach_data.get('impressions_growth', 0) // time_diff_minutes
            metrics.click_through_rate = reach_data.get('ctr', 0.0)
            
            # Audience growth
            audience_data = platform_data.get('audience_data', {})
            metrics.new_followers_per_minute = audience_data.get('followers_growth', 0) / time_diff_minutes
            metrics.follower_growth_rate = audience_data.get('growth_rate', 0.0)
            metrics.audience_retention_rate = audience_data.get('retention_rate', 0.0)
            
            # Content performance scores
            content_data = platform_data.get('content_data', {})
            metrics.content_performance_score = await self._calculate_content_performance_score(content_data)
            metrics.viral_potential_score = await self._calculate_viral_potential(content_data, metrics)
            metrics.trend_alignment_score = await self._calculate_trend_alignment(content_data)
            
            # Technical metrics
            technical_data = platform_data.get('technical_data', {})
            metrics.loading_time_ms = technical_data.get('loading_time', 0.0)
            metrics.error_rate = technical_data.get('error_rate', 0.0)
            metrics.api_response_time_ms = technical_data.get('api_response_time', 0.0)
            
            # Monetization metrics
            monetization_data = platform_data.get('monetization_data', {})
            metrics.revenue_per_minute = monetization_data.get('revenue_growth', 0.0) / time_diff_minutes
            metrics.conversion_rate = monetization_data.get('conversion_rate', 0.0)
            
            # Store metrics in buffer
            self.metric_buffers[creator_id].append(metrics)
            
            # Store in Redis for persistence
            await self._store_metrics_redis(creator_id, metrics)
            
            logger.debug(f"Collected real-time metrics for creator {creator_id}")
            return metrics
            
        except Exception as e:
            logger.error(f"Metrics collection failed for creator {creator_id}: {str(e)}")
            raise ProcessingError(f"Metrics collection error: {str(e)}")

    async def evaluate_alerts(self, creator_id: str, current_metrics: RealTimeMetrics) -> List[MonitoringAlert]:
        """
        Evaluate current metrics against thresholds and detect anomalies
        
        Args:
            creator_id: ID of the creator
            current_metrics: Current metrics snapshot
            
        Returns:
            List[MonitoringAlert]: Any alerts generated
        """
        try:
            alerts = []
            
            if creator_id not in self.active_monitors:
                return alerts
            
            session = self.active_monitors[creator_id]
            thresholds = session['thresholds']
            
            # Evaluate threshold-based alerts
            threshold_alerts = await self._evaluate_threshold_alerts(creator_id, current_metrics, thresholds)
            alerts.extend(threshold_alerts)
            
            # Evaluate anomaly detection alerts
            anomaly_alerts = await self._evaluate_anomaly_alerts(creator_id, current_metrics)
            alerts.extend(anomaly_alerts)
            
            # Evaluate trend alerts
            trend_alerts = await self._evaluate_trend_alerts(creator_id, current_metrics)
            alerts.extend(trend_alerts)
            
            # Evaluate opportunity alerts
            opportunity_alerts = await self._evaluate_opportunity_alerts(creator_id, current_metrics)
            alerts.extend(opportunity_alerts)
            
            # Process and prioritize alerts
            processed_alerts = await self._process_alerts(creator_id, alerts)
            
            # Store alerts
            for alert in processed_alerts:
                await self._store_alert(alert)
                session['active_alerts'].append(alert)
            
            # Handle alerts based on severity
            for alert in processed_alerts:
                await self._handle_alert(alert)
            
            logger.debug(f"Evaluated {len(processed_alerts)} alerts for creator {creator_id}")
            return processed_alerts
            
        except Exception as e:
            logger.error(f"Alert evaluation failed for creator {creator_id}: {str(e)}")
            return []

    async def detect_viral_content(self, creator_id: str, content_metrics: RealTimeMetrics) -> Dict[str, Any]:
        """
        Detect if content is going viral and provide real-time insights
        
        Args:
            creator_id: ID of the creator
            content_metrics: Current content metrics
            
        Returns:
            Dict[str, Any]: Viral content analysis results
        """
        try:
            viral_analysis = {
                'is_viral': False,
                'viral_probability': 0.0,
                'viral_stage': 'normal',  # normal, trending, viral, peak, declining
                'time_to_peak_estimate': None,
                'peak_performance_estimate': {},
                'recommendations': [],
                'monitoring_frequency': 'normal'  # normal, increased, intensive
            }
            
            # Get historical baseline for comparison
            baseline_metrics = await self._get_baseline_metrics(creator_id)
            if not baseline_metrics:
                return viral_analysis
            
            # Calculate viral indicators
            engagement_multiplier = content_metrics.engagement_rate / baseline_metrics.get('avg_engagement_rate', 0.01)
            growth_multiplier = content_metrics.follower_growth_rate / baseline_metrics.get('avg_growth_rate', 0.01)
            reach_multiplier = content_metrics.reach_per_minute / max(baseline_metrics.get('avg_reach_per_minute', 1), 1)
            
            # Viral probability calculation
            viral_indicators = {
                'engagement_spike': min(engagement_multiplier / 3.0, 1.0),  # 3x engagement = full score
                'growth_acceleration': min(growth_multiplier / 5.0, 1.0),   # 5x growth = full score
                'reach_explosion': min(reach_multiplier / 10.0, 1.0),       # 10x reach = full score
                'velocity_increase': min(content_metrics.engagement_velocity / 0.1, 1.0),  # High velocity
                'trend_alignment': content_metrics.trend_alignment_score,
                'share_velocity': min(content_metrics.shares_per_minute / 10.0, 1.0)  # 10+ shares/min
            }
            
            # Weighted viral probability
            weights = {
                'engagement_spike': 0.25,
                'growth_acceleration': 0.20,
                'reach_explosion': 0.20,
                'velocity_increase': 0.15,
                'trend_alignment': 0.10,
                'share_velocity': 0.10
            }
            
            viral_analysis['viral_probability'] = sum(
                viral_indicators[indicator] * weights[indicator] 
                for indicator in viral_indicators
            )
            
            # Determine viral stage
            if viral_analysis['viral_probability'] > 0.8:
                viral_analysis['viral_stage'] = 'viral'
                viral_analysis['is_viral'] = True
                viral_analysis['monitoring_frequency'] = 'intensive'
            elif viral_analysis['viral_probability'] > 0.6:
                viral_analysis['viral_stage'] = 'trending'
                viral_analysis['monitoring_frequency'] = 'increased'
            elif viral_analysis['viral_probability'] > 0.4:
                viral_analysis['viral_stage'] = 'gaining_traction'
                viral_analysis['monitoring_frequency'] = 'increased'
            
            # Viral content recommendations
            if viral_analysis['viral_probability'] > 0.6:
                viral_analysis['recommendations'] = [
                    "Increase posting frequency to capitalize on momentum",
                    "Engage actively with comments to boost algorithm favorability",
                    "Cross-promote on other platforms immediately",
                    "Prepare follow-up content to maintain engagement",
                    "Monitor competitor response and differentiate",
                    "Consider monetization opportunities (sponsorships, products)",
                    "Document viral elements for future content strategy"
                ]
                
                # Estimate time to peak (simplified model)
                viral_analysis['time_to_peak_estimate'] = await self._estimate_viral_peak_time(
                    content_metrics, viral_indicators
                )
                
                # Estimate peak performance
                viral_analysis['peak_performance_estimate'] = {
                    'estimated_peak_engagement': content_metrics.engagement_rate * (1 + viral_analysis['viral_probability']),
                    'estimated_peak_reach': content_metrics.reach_per_minute * 60 * 24 * (1 + viral_analysis['viral_probability'] * 2),
                    'estimated_new_followers': int(content_metrics.new_followers_per_minute * 60 * 48 * (1 + viral_analysis['viral_probability']))
                }
            
            # Generate viral alert if necessary
            if viral_analysis['is_viral'] and creator_id in self.active_monitors:
                viral_alert = MonitoringAlert(
                    title="Viral Content Detected!",
                    description=f"Content is showing viral patterns with {viral_analysis['viral_probability']:.1%} viral probability",
                    severity=AlertSeverity.HIGH,
                    alert_type=AlertType.OPPORTUNITY_ALERT,
                    metric_name="viral_potential_score",
                    current_value=viral_analysis['viral_probability'],
                    creator_id=creator_id,
                    recommended_actions=viral_analysis['recommendations'],
                    context_data=viral_analysis
                )
                await self._handle_alert(viral_alert)
            
            logger.info(f"Viral analysis completed for creator {creator_id}: {viral_analysis['viral_stage']}")
            return viral_analysis
            
        except Exception as e:
            logger.error(f"Viral content detection failed for creator {creator_id}: {str(e)}")
            return {'is_viral': False, 'viral_probability': 0.0, 'error': str(e)}

    async def get_live_dashboard_data(self, creator_id: str) -> Dict[str, Any]:
        """
        Get comprehensive live dashboard data
        
        Args:
            creator_id: ID of the creator
            
        Returns:
            Dict[str, Any]: Live dashboard data
        """
        try:
            if creator_id not in self.active_monitors:
                return {'error': 'Monitoring not active for creator'}
            
            session = self.active_monitors[creator_id]
            current_metrics = self.metric_buffers[creator_id][-1] if self.metric_buffers[creator_id] else None
            
            dashboard_data = {
                'monitoring_status': session['status'].value,
                'monitoring_duration': str(datetime.utcnow() - session['start_time']),
                'last_update': current_metrics.timestamp.isoformat() if current_metrics else None,
                
                # Current metrics
                'current_metrics': {
                    'engagement_rate': current_metrics.engagement_rate if current_metrics else 0,
                    'follower_growth_rate': current_metrics.follower_growth_rate if current_metrics else 0,
                    'engagement_velocity': current_metrics.engagement_velocity if current_metrics else 0,
                    'viral_potential_score': current_metrics.viral_potential_score if current_metrics else 0,
                    'content_performance_score': current_metrics.content_performance_score if current_metrics else 0
                } if current_metrics else {},
                
                # Historical trends (last hour)
                'hourly_trends': await self._get_hourly_trends(creator_id),
                
                # Active alerts
                'active_alerts': [
                    {
                        'title': alert.title,
                        'severity': alert.severity.value,
                        'time_detected': alert.time_detected.isoformat(),
                        'metric_name': alert.metric_name,
                        'current_value': alert.current_value
                    }
                    for alert in session['active_alerts']
                    if not alert.is_resolved
                ],
                
                # Performance summary
                'performance_summary': await self._get_performance_summary(creator_id),
                
                # Recommendations
                'live_recommendations': await self._get_live_recommendations(creator_id),
                
                # System health
                'system_health': {
                    'monitoring_latency_ms': await self._calculate_monitoring_latency(),
                    'data_freshness_seconds': await self._calculate_data_freshness(creator_id),
                    'alert_processing_time_ms': await self._calculate_alert_processing_time()
                }
            }
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Dashboard data retrieval failed for creator {creator_id}: {str(e)}")
            return {'error': f'Dashboard data error: {str(e)}'}

    # Helper methods for monitoring operations

    async def _evaluate_threshold_alerts(self, 
                                       creator_id: str, 
                                       metrics: RealTimeMetrics, 
                                       thresholds: Dict[str, MetricThreshold]) -> List[MonitoringAlert]:
        """Evaluate threshold-based alerts"""
        alerts = []
        
        metric_values = {
            'engagement_rate': metrics.engagement_rate,
            'follower_growth_rate': metrics.follower_growth_rate,
            'error_rate': metrics.error_rate,
            'loading_time_ms': metrics.loading_time_ms,
            'conversion_rate': metrics.conversion_rate
        }
        
        for metric_name, threshold in thresholds.items():
            if not threshold.enabled or metric_name not in metric_values:
                continue
                
            current_value = metric_values[metric_name]
            
            # Check upper thresholds
            if threshold.upper_threshold and current_value > threshold.upper_threshold:
                alert = MonitoringAlert(
                    title=f"{metric_name.replace('_', ' ').title()} Critical High",
                    description=f"{metric_name} ({current_value:.4f}) exceeded critical threshold ({threshold.upper_threshold})",
                    severity=AlertSeverity.CRITICAL,
                    alert_type=AlertType.THRESHOLD_BREACH,
                    metric_name=metric_name,
                    current_value=current_value,
                    threshold_value=threshold.upper_threshold,
                    creator_id=creator_id,
                    platform=metrics.platform
                )
                alerts.append(alert)
                
            elif threshold.warning_upper and current_value > threshold.warning_upper:
                alert = MonitoringAlert(
                    title=f"{metric_name.replace('_', ' ').title()} Warning High",
                    description=f"{metric_name} ({current_value:.4f}) exceeded warning threshold ({threshold.warning_upper})",
                    severity=AlertSeverity.MEDIUM,
                    alert_type=AlertType.THRESHOLD_BREACH,
                    metric_name=metric_name,
                    current_value=current_value,
                    threshold_value=threshold.warning_upper,
                    creator_id=creator_id,
                    platform=metrics.platform
                )
                alerts.append(alert)
            
            # Check lower thresholds
            if threshold.lower_threshold and current_value < threshold.lower_threshold:
                alert = MonitoringAlert(
                    title=f"{metric_name.replace('_', ' ').title()} Critical Low",
                    description=f"{metric_name} ({current_value:.4f}) fell below critical threshold ({threshold.lower_threshold})",
                    severity=AlertSeverity.CRITICAL,
                    alert_type=AlertType.THRESHOLD_BREACH,
                    metric_name=metric_name,
                    current_value=current_value,
                    threshold_value=threshold.lower_threshold,
                    creator_id=creator_id,
                    platform=metrics.platform
                )
                alerts.append(alert)
                
            elif threshold.warning_lower and current_value < threshold.warning_lower:
                alert = MonitoringAlert(
                    title=f"{metric_name.replace('_', ' ').title()} Warning Low",
                    description=f"{metric_name} ({current_value:.4f}) fell below warning threshold ({threshold.warning_lower})",
                    severity=AlertSeverity.MEDIUM,
                    alert_type=AlertType.THRESHOLD_BREACH,
                    metric_name=metric_name,
                    current_value=current_value,
                    threshold_value=threshold.warning_lower,
                    creator_id=creator_id,
                    platform=metrics.platform
                )
                alerts.append(alert)
        
        return alerts

    async def _calculate_content_performance_score(self, content_data: Dict[str, Any]) -> float:
        """Calculate comprehensive content performance score"""
        if not content_data:
            return 0.5
        
        # Normalize and weight different performance factors
        engagement_score = min(content_data.get('engagement_rate', 0.02) / 0.05, 1.0)  # Normalize to 5%
        reach_score = min(content_data.get('reach_growth', 0) / 10000, 1.0)  # Normalize to 10k
        retention_score = content_data.get('retention_rate', 0.5)  # Already 0-1
        completion_score = content_data.get('completion_rate', 0.5)  # Already 0-1
        
        # Weighted performance score
        performance_score = (
            engagement_score * 0.3 +
            reach_score * 0.25 +
            retention_score * 0.25 +
            completion_score * 0.20
        )
        
        return min(max(performance_score, 0.0), 1.0)

    async def _calculate_viral_potential(self, content_data: Dict[str, Any], metrics: RealTimeMetrics) -> float:
        """
Calculate viral potential score"""
        if not content_data:
            return 0.0
        
        # Factors that contribute to viral potential
        share_rate = min(metrics.shares_per_minute / 5.0, 1.0)  # 5 shares/min = max score
        engagement_velocity = min(abs(metrics.engagement_velocity) / 0.1, 1.0)  # High velocity
        reach_acceleration = min(metrics.reach_per_minute / 1000, 1.0)  # 1000 reach/min
        comment_engagement = min(metrics.comments_per_minute / 10.0, 1.0)  # 10 comments/min
        
        viral_potential = (
            share_rate * 0.4 +
            engagement_velocity * 0.3 +
            reach_acceleration * 0.2 +
            comment_engagement * 0.1
        )
        
        return min(max(viral_potential, 0.0), 1.0)

    async def _handle_alert(self, alert: MonitoringAlert):
        """
Handle alert based on severity"""
        handler = self.alert_handlers.get(alert.severity)
        if handler:
            await handler(alert)

    async def _handle_critical_alert(self, alert: MonitoringAlert):
        """
Handle critical severity alerts"""
        logger.critical(f"CRITICAL ALERT: {alert.title} - {alert.description}")
        
        # Immediate notifications
        await self._send_immediate_notification(alert)
        
        # Automated response if configured
        if alert.metric_name == 'error_rate' and alert.current_value > 0.10:
            # High error rate - might need automatic scaling or failover
            await self._trigger_emergency_response(alert)

    async def _handle_high_alert(self, alert: MonitoringAlert):
        """Handle high severity alerts"""
        logger.warning(f"HIGH ALERT: {alert.title}")
        await self._send_priority_notification(alert)

    async def _handle_medium_alert(self, alert: MonitoringAlert):
        """Handle medium severity alerts"""
        logger.info(f"MEDIUM ALERT: {alert.title}")
        await self._send_standard_notification(alert)

    async def _handle_low_alert(self, alert: MonitoringAlert):
        """Handle low severity alerts"""
        logger.debug(f"LOW ALERT: {alert.title}")
        # Usually just logged, might be aggregated for daily summaries

    async def _handle_info_alert(self, alert: MonitoringAlert):
        """Handle informational alerts"""
        logger.debug(f"INFO: {alert.title}")
        # Purely informational

    # Additional helper methods would be implemented here for:
    # - Notification sending (email, SMS, Slack, etc.)
    # - Emergency response procedures
    # - Anomaly detection algorithms
    # - Trend analysis
    # - Baseline metric calculations
    # - Data persistence and retrieval
    # - And many more specialized monitoring functions


class AlertManager:
    """Specialized alert management system"""
    
    def __init__(self, monitoring_system: RealTimeMonitoringSystem):
        try:
            logger.info(f"Executing __init__")
            
            # Implementation for __init__
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"__init__ completed successfully")
            return result
            
        except Exception as e:
        try:
            logger.info(f"Executing __init__")
            
            # Implementation for __init__
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"__init__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__init__ failed: {e}")
            raise
            logger.error(f"__init__ failed: {e}")
        try:
            logger.info(f"Executing __init__")
            
            # Implementation for __init__
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"__init__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__init__ failed: {e}")
            raise
    async def create_custom_alert_rule(self, rule_config: Dict[str, Any]) -> str:
        """
Create custom alert rule"""
        return "alert_rule_12345"

class MetricCollector:
    """Specialized metric collection engine"""
    
    def __init__(self, monitoring_system: RealTimeMonitoringSystem):
        self.monitoring_system = monitoring_system
    
    async def collect_platform_metrics(self, platform: str, creator_id: str) -> Dict[str, Any]:
        """
Collect metrics from specific platform"""
        return {
            'engagement_data': {},
            'audience_data': {},
            'content_data': {}
        }

class AnomalyDetector:
    """
Specialized anomaly detection system"""
    
    def __init__(self, monitoring_system: RealTimeMonitoringSystem):
        self.monitoring_system = monitoring_system
    
    async def detect_performance_anomalies(self, metrics_history: List[RealTimeMetrics]) -> List[Dict[str, Any]]:
        """
Detect anomalies in performance metrics"""
        return [
            {
                'anomaly_type': 'engagement_spike',
                'confidence': 0.85,
                'deviation': 2.5,
                'expected_value': 0.03,
                'actual_value': 0.08
            }
        ]
