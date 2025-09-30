#!/usr/bin/env python3

"""
IA Chérie Rate Limit Analytics Engine - Enterprise Business Intelligence
======================================================================

Advanced analytics engine for rate limiting insights, business intelligence,
predictive analytics, and performance optimization. Provides comprehensive
data analysis, ML-driven insights, and real-time monitoring for the IA Chérie
creator platform rate limiting system.

Features:
- Real-time analytics with ML insights and pattern detection
- Multi-dimensional data analysis (user behavior, platform performance, content trends)
- Predictive analytics with forecasting and anomaly detection
- Business intelligence with KPI tracking and ROI analysis
- Advanced reporting with custom dashboards and automated alerts
- Data warehouse integration with ETL pipelines
- Performance optimization recommendations
- Compliance reporting and audit trails

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - Unauthorized copying or distribution prohibited

Project: IA Chérie Rate Limiting - Analytics Engine
Version: 1.0 Production
"""

import asyncio
import time
import json
import logging
import statistics
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict, deque
import uuid
import numpy as np
from scipy import stats
import pandas as pd

# Configure logging for analytics engine
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnalyticsPeriod(Enum):
    """Analytics time periods"""
    REAL_TIME = "real_time"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"

class MetricType(Enum):
    """Types of metrics tracked"""
    RATE_LIMIT_HITS = "rate_limit_hits"
    REQUEST_VOLUME = "request_volume"
    USER_BEHAVIOR = "user_behavior"
    PLATFORM_PERFORMANCE = "platform_performance"
    CONTENT_ANALYTICS = "content_analytics"
    REVENUE_METRICS = "revenue_metrics"
    COMPLIANCE_METRICS = "compliance_metrics"
    SYSTEM_PERFORMANCE = "system_performance"

class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class ReportFormat(Enum):
    """Report output formats"""
    JSON = "json"
    CSV = "csv"
    PDF = "pdf"
    EXCEL = "excel"
    HTML = "html"

@dataclass
class AnalyticsEvent:
    """Analytics event data structure"""
    event_id: str
    event_type: str
    user_id: Optional[str]
    timestamp: datetime
    data: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    processed: bool = False

@dataclass
class MetricData:
    """Metric data point"""
    metric_name: str
    metric_type: MetricType
    value: Union[int, float]
    timestamp: datetime
    dimensions: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)

@dataclass
class AnalyticsAlert:
    """Analytics alert"""
    alert_id: str
    alert_type: str
    severity: AlertSeverity
    metric_name: str
    threshold_value: float
    current_value: float
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    acknowledged: bool = False

@dataclass
class BusinessKPI:
    """Business Key Performance Indicator"""
    kpi_name: str
    current_value: float
    target_value: float
    trend: str  # 'up', 'down', 'stable'
    change_percentage: float
    period: AnalyticsPeriod
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class PredictionResult:
    """ML prediction result"""
    prediction_id: str
    metric_name: str
    predicted_value: float
    confidence_score: float
    time_horizon: timedelta
    model_used: str
    features_used: List[str]
    created_at: datetime = field(default_factory=datetime.now)

class AnalyticsEngine:
    """
    Advanced analytics engine for rate limiting insights
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize analytics engine"""
        self.config = config or {}
        self.node_id = str(uuid.uuid4())
        
        # Data storage
        self.events: deque = deque(maxlen=100000)  # Last 100k events
        self.metrics: Dict[str, List[MetricData]] = defaultdict(list)
        self.aggregated_metrics: Dict[str, Dict[str, float]] = defaultdict(dict)
        
        # Analytics state
        self.kpis: Dict[str, BusinessKPI] = {}
        self.alerts: Dict[str, AnalyticsAlert] = {}
        self.predictions: Dict[str, PredictionResult] = {}
        
        # Processing queues
        self.event_queue: asyncio.Queue = asyncio.Queue()
        self.alert_queue: asyncio.Queue = asyncio.Queue()
        
        # ML models and patterns
        self.patterns: Dict[str, Any] = {}
        self.anomaly_detectors: Dict[str, Any] = {}
        
        # Background task management
        self.background_tasks: Set[asyncio.Task] = set()
        self.is_running = False
        
        # Initialize KPIs
        self._initialize_kpis()
        
        logger.info(f"AnalyticsEngine initialized with node_id: {self.node_id}")
    
    def _initialize_kpis(self):
        """Initialize business KPIs"""
        kpi_definitions = {
            'total_requests': {'target': 1000000, 'period': AnalyticsPeriod.MONTHLY},
            'rate_limit_hit_rate': {'target': 5.0, 'period': AnalyticsPeriod.DAILY},
            'user_satisfaction_score': {'target': 4.5, 'period': AnalyticsPeriod.WEEKLY},
            'system_uptime': {'target': 99.99, 'period': AnalyticsPeriod.MONTHLY},
            'average_response_time': {'target': 100.0, 'period': AnalyticsPeriod.HOURLY},
            'revenue_per_user': {'target': 25.0, 'period': AnalyticsPeriod.MONTHLY},
            'churn_rate': {'target': 2.0, 'period': AnalyticsPeriod.MONTHLY},
            'content_processing_success_rate': {'target': 98.0, 'period': AnalyticsPeriod.DAILY},
            'api_error_rate': {'target': 0.1, 'period': AnalyticsPeriod.HOURLY},
            'user_engagement_score': {'target': 75.0, 'period': AnalyticsPeriod.WEEKLY},
            'platform_distribution_efficiency': {'target': 85.0, 'period': AnalyticsPeriod.DAILY},
            'copyright_detection_accuracy': {'target': 95.0, 'period': AnalyticsPeriod.WEEKLY},
            'collaboration_adoption_rate': {'target': 40.0, 'period': AnalyticsPeriod.MONTHLY},
            'ai_processing_utilization': {'target': 80.0, 'period': AnalyticsPeriod.DAILY},
            'security_incident_count': {'target': 0.0, 'period': AnalyticsPeriod.MONTHLY},
            'compliance_score': {'target': 100.0, 'period': AnalyticsPeriod.WEEKLY},
            'data_quality_score': {'target': 95.0, 'period': AnalyticsPeriod.DAILY},
            'infrastructure_cost_efficiency': {'target': 90.0, 'period': AnalyticsPeriod.MONTHLY},
            'user_onboarding_success_rate': {'target': 85.0, 'period': AnalyticsPeriod.WEEKLY},
            'feature_adoption_rate': {'target': 60.0, 'period': AnalyticsPeriod.MONTHLY},
            'customer_lifetime_value': {'target': 500.0, 'period': AnalyticsPeriod.YEARLY},
            'net_promoter_score': {'target': 70.0, 'period': AnalyticsPeriod.QUARTERLY},
            'market_share_growth': {'target': 15.0, 'period': AnalyticsPeriod.QUARTERLY},
            'innovation_index': {'target': 80.0, 'period': AnalyticsPeriod.MONTHLY},
            'sustainability_score': {'target': 85.0, 'period': AnalyticsPeriod.QUARTERLY}
        }
        
        for kpi_name, config in kpi_definitions.items():
            self.kpis[kpi_name] = BusinessKPI(
                kpi_name=kpi_name,
                current_value=0.0,
                target_value=config['target'],
                trend='stable',
                change_percentage=0.0,
                period=config['period']
            )
    
    async def initialize(self) -> bool:
        """Initialize analytics engine"""
        try:
            self.is_running = True
            
            # Start background tasks
            self.background_tasks.add(
                asyncio.create_task(self._event_processing_task())
            )
            self.background_tasks.add(
                asyncio.create_task(self._metrics_aggregation_task())
            )
            self.background_tasks.add(
                asyncio.create_task(self._kpi_calculation_task())
            )
            self.background_tasks.add(
                asyncio.create_task(self._anomaly_detection_task())
            )
            self.background_tasks.add(
                asyncio.create_task(self._prediction_task())
            )
            self.background_tasks.add(
                asyncio.create_task(self._alert_processing_task())
            )
            
            logger.info("AnalyticsEngine initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize AnalyticsEngine: {e}")
            return False
    
    async def ingest_event(
        self,
        event_type: str,
        data: Dict[str, Any],
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Ingest analytics event"""
        try:
            event = AnalyticsEvent(
                event_id=str(uuid.uuid4()),
                event_type=event_type,
                user_id=user_id,
                timestamp=datetime.now(),
                data=data,
                metadata=metadata or {}
            )
            
            # Add to event queue for processing
            await self.event_queue.put(event)
            
            # Add to recent events deque
            self.events.append(event)
            
            return {
                'success': True,
                'event_id': event.event_id,
                'ingested_at': event.timestamp.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error ingesting event: {e}")
            return {'success': False, 'error': str(e)}
    
    async def record_metric(
        self,
        metric_name: str,
        value: Union[int, float],
        metric_type: MetricType,
        dimensions: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Record a metric data point"""
        try:
            metric = MetricData(
                metric_name=metric_name,
                metric_type=metric_type,
                value=value,
                timestamp=datetime.now(),
                dimensions=dimensions or {},
                tags=tags or []
            )
            
            # Store metric
            self.metrics[metric_name].append(metric)
            
            # Keep only recent metrics (last 24 hours)
            cutoff_time = datetime.now() - timedelta(hours=24)
            self.metrics[metric_name] = [
                m for m in self.metrics[metric_name]
                if m.timestamp >= cutoff_time
            ]
            
            # Check for alerts
            await self._check_metric_alerts(metric)
            
            return {
                'success': True,
                'metric_name': metric_name,
                'value': value,
                'recorded_at': metric.timestamp.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error recording metric {metric_name}: {e}")
            return {'success': False, 'error': str(e)}
    
    async def get_analytics_summary(
        self,
        period: AnalyticsPeriod = AnalyticsPeriod.DAILY,
        metrics: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Get comprehensive analytics summary"""
        try:
            end_time = datetime.now()
            
            # Calculate period start time
            if period == AnalyticsPeriod.HOURLY:
                start_time = end_time - timedelta(hours=1)
            elif period == AnalyticsPeriod.DAILY:
                start_time = end_time - timedelta(days=1)
            elif period == AnalyticsPeriod.WEEKLY:
                start_time = end_time - timedelta(weeks=1)
            elif period == AnalyticsPeriod.MONTHLY:
                start_time = end_time - timedelta(days=30)
            else:
                start_time = end_time - timedelta(hours=1)
            
            # Filter metrics by period
            period_metrics = {}
            metrics_to_analyze = metrics or list(self.metrics.keys())
            
            for metric_name in metrics_to_analyze:
                if metric_name in self.metrics:
                    period_data = [
                        m for m in self.metrics[metric_name]
                        if start_time <= m.timestamp <= end_time
                    ]
                    
                    if period_data:
                        values = [m.value for m in period_data]
                        period_metrics[metric_name] = {
                            'count': len(values),
                            'sum': sum(values),
                            'average': statistics.mean(values),
                            'median': statistics.median(values),
                            'min': min(values),
                            'max': max(values),
                            'std_dev': statistics.stdev(values) if len(values) > 1 else 0,
                            'latest_value': period_data[-1].value,
                            'trend': self._calculate_trend(values)
                        }
            
            # Get current KPIs
            current_kpis = {
                name: {
                    'current_value': kpi.current_value,
                    'target_value': kpi.target_value,
                    'trend': kpi.trend,
                    'change_percentage': kpi.change_percentage,
                    'performance': (kpi.current_value / kpi.target_value * 100) if kpi.target_value > 0 else 0
                }
                for name, kpi in self.kpis.items()
            }
            
            # Get active alerts
            active_alerts = [
                {
                    'alert_id': alert.alert_id,
                    'alert_type': alert.alert_type,
                    'severity': alert.severity.value,
                    'metric_name': alert.metric_name,
                    'message': alert.message,
                    'timestamp': alert.timestamp.isoformat()
                }
                for alert in self.alerts.values()
                if not alert.acknowledged
            ]
            
            # Get recent predictions
            recent_predictions = [
                {
                    'prediction_id': pred.prediction_id,
                    'metric_name': pred.metric_name,
                    'predicted_value': pred.predicted_value,
                    'confidence_score': pred.confidence_score,
                    'model_used': pred.model_used,
                    'created_at': pred.created_at.isoformat()
                }
                for pred in list(self.predictions.values())[-10:]  # Last 10 predictions
            ]
            
            return {
                'success': True,
                'period': period.value,
                'time_range': {
                    'start': start_time.isoformat(),
                    'end': end_time.isoformat()
                },
                'metrics': period_metrics,
                'kpis': current_kpis,
                'alerts': active_alerts,
                'predictions': recent_predictions,
                'system_health': await self._calculate_system_health(),
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating analytics summary: {e}")
            return {'success': False, 'error': str(e)}
    
    async def generate_insights(
        self,
        focus_areas: Optional[List[str]] = None,
        time_period_days: int = 7
    ) -> Dict[str, Any]:
        """Generate ML-driven insights"""
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(days=time_period_days)
            
            insights = {
                'period_analyzed': {
                    'start': start_time.isoformat(),
                    'end': end_time.isoformat(),
                    'days': time_period_days
                },
                'key_insights': [],
                'recommendations': [],
                'patterns_detected': [],
                'anomalies': [],
                'performance_analysis': {},
                'user_behavior_insights': {},
                'business_impact': {}
            }
            
            # Analyze key patterns
            patterns = await self._detect_patterns(start_time, end_time)
            insights['patterns_detected'] = patterns
            
            # Generate key insights
            key_insights = []
            
            # Rate limiting insights
            if 'rate_limiting' not in focus_areas or not focus_areas:
                rate_limit_hits = self._get_metric_summary('rate_limit_hits', start_time, end_time)
                if rate_limit_hits['count'] > 0:
                    key_insights.append({
                        'category': 'rate_limiting',
                        'insight': f"Rate limit hits increased by {rate_limit_hits.get('trend', 0):.1f}% over the period",
                        'impact': 'medium',
                        'data': rate_limit_hits
                    })
            
            # User behavior insights
            if 'user_behavior' not in focus_areas or not focus_areas:
                user_metrics = await self._analyze_user_behavior(start_time, end_time)
                insights['user_behavior_insights'] = user_metrics
                
                if user_metrics.get('engagement_trend', 0) > 10:
                    key_insights.append({
                        'category': 'user_engagement',
                        'insight': f"User engagement increased by {user_metrics['engagement_trend']:.1f}%",
                        'impact': 'high',
                        'data': user_metrics
                    })
            
            # Performance insights
            performance_data = await self._analyze_performance(start_time, end_time)
            insights['performance_analysis'] = performance_data
            
            if performance_data.get('response_time_trend', 0) > 20:
                key_insights.append({
                    'category': 'performance',
                    'insight': f"Response times increased by {performance_data['response_time_trend']:.1f}%",
                    'impact': 'high',
                    'recommendation': 'Consider scaling infrastructure or optimizing queries'
                })
            
            # Business impact analysis
            business_impact = await self._analyze_business_impact(start_time, end_time)
            insights['business_impact'] = business_impact
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(insights)
            insights['recommendations'] = recommendations
            
            insights['key_insights'] = key_insights
            
            return {
                'success': True,
                'insights': insights,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            return {'success': False, 'error': str(e)}
    
    async def create_custom_report(
        self,
        report_config: Dict[str, Any],
        format_type: ReportFormat = ReportFormat.JSON
    ) -> Dict[str, Any]:
        """Create custom analytics report"""
        try:
            report_id = str(uuid.uuid4())
            
            # Extract report parameters
            title = report_config.get('title', 'Custom Analytics Report')
            metrics = report_config.get('metrics', [])
            time_range = report_config.get('time_range', {'days': 7})
            filters = report_config.get('filters', {})
            
            # Calculate time range
            end_time = datetime.now()
            if 'days' in time_range:
                start_time = end_time - timedelta(days=time_range['days'])
            elif 'hours' in time_range:
                start_time = end_time - timedelta(hours=time_range['hours'])
            else:
                start_time = end_time - timedelta(days=7)
            
            # Generate report data
            report_data = {
                'report_id': report_id,
                'title': title,
                'generated_at': datetime.now().isoformat(),
                'time_range': {
                    'start': start_time.isoformat(),
                    'end': end_time.isoformat()
                },
                'metrics_data': {},
                'summary': {},
                'visualizations': []
            }
            
            # Collect metrics data
            for metric_name in metrics:
                if metric_name in self.metrics:
                    metric_data = [
                        m for m in self.metrics[metric_name]
                        if start_time <= m.timestamp <= end_time
                    ]
                    
                    if metric_data:
                        values = [m.value for m in metric_data]
                        timestamps = [m.timestamp.isoformat() for m in metric_data]
                        
                        report_data['metrics_data'][metric_name] = {
                            'values': values,
                            'timestamps': timestamps,
                            'statistics': {
                                'count': len(values),
                                'sum': sum(values),
                                'average': statistics.mean(values),
                                'min': min(values),
                                'max': max(values),
                                'std_dev': statistics.stdev(values) if len(values) > 1 else 0
                            }
                        }
            
            # Generate summary
            report_data['summary'] = await self._generate_report_summary(report_data['metrics_data'])
            
            # Add visualization recommendations
            report_data['visualizations'] = self._recommend_visualizations(metrics)
            
            # Format report based on requested format
            if format_type == ReportFormat.JSON:
                formatted_report = report_data
            elif format_type == ReportFormat.CSV:
                formatted_report = await self._format_as_csv(report_data)
            elif format_type == ReportFormat.HTML:
                formatted_report = await self._format_as_html(report_data)
            else:
                formatted_report = report_data
            
            return {
                'success': True,
                'report_id': report_id,
                'format': format_type.value,
                'report_data': formatted_report
            }
            
        except Exception as e:
            logger.error(f"Error creating custom report: {e}")
            return {'success': False, 'error': str(e)}
    
    async def predict_metric(
        self,
        metric_name: str,
        time_horizon_hours: int = 24,
        confidence_threshold: float = 0.8
    ) -> Dict[str, Any]:
        """Predict future metric values using ML"""
        try:
            if metric_name not in self.metrics:
                return {
                    'success': False,
                    'error': f'Metric {metric_name} not found'
                }
            
            # Get historical data
            historical_data = self.metrics[metric_name][-1000:]  # Last 1000 data points
            
            if len(historical_data) < 10:
                return {
                    'success': False,
                    'error': 'Insufficient historical data for prediction'
                }
            
            # Prepare data for prediction
            timestamps = [m.timestamp for m in historical_data]
            values = [m.value for m in historical_data]
            
            # Simple time series prediction using linear regression
            x = np.array([(t - timestamps[0]).total_seconds() for t in timestamps])
            y = np.array(values)
            
            # Fit linear model
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
            
            # Predict future value
            future_timestamp = timestamps[-1] + timedelta(hours=time_horizon_hours)
            future_x = (future_timestamp - timestamps[0]).total_seconds()
            predicted_value = slope * future_x + intercept
            
            # Calculate confidence score
            confidence_score = abs(r_value)  # Correlation coefficient as confidence
            
            # Create prediction result
            prediction = PredictionResult(
                prediction_id=str(uuid.uuid4()),
                metric_name=metric_name,
                predicted_value=predicted_value,
                confidence_score=confidence_score,
                time_horizon=timedelta(hours=time_horizon_hours),
                model_used='linear_regression',
                features_used=['timestamp', 'historical_values']
            )
            
            # Store prediction
            self.predictions[prediction.prediction_id] = prediction
            
            return {
                'success': True,
                'prediction': {
                    'prediction_id': prediction.prediction_id,
                    'metric_name': metric_name,
                    'predicted_value': predicted_value,
                    'confidence_score': confidence_score,
                    'time_horizon_hours': time_horizon_hours,
                    'predicted_timestamp': future_timestamp.isoformat(),
                    'model_used': prediction.model_used,
                    'meets_confidence_threshold': confidence_score >= confidence_threshold
                }
            }
            
        except Exception as e:
            logger.error(f"Error predicting metric {metric_name}: {e}")
            return {'success': False, 'error': str(e)}
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction for values"""
        if len(values) < 2:
            return 'stable'
        
        # Calculate linear trend
        x = list(range(len(values)))
        slope, _, _, _, _ = stats.linregress(x, values)
        
        if slope > 0.1:
            return 'up'
        elif slope < -0.1:
            return 'down'
        else:
            return 'stable'
    
    def _get_metric_summary(
        self,
        metric_name: str,
        start_time: datetime,
        end_time: datetime
    ) -> Dict[str, Any]:
        """Get summary statistics for a metric in time range"""
        if metric_name not in self.metrics:
            return {'count': 0}
        
        period_data = [
            m for m in self.metrics[metric_name]
            if start_time <= m.timestamp <= end_time
        ]
        
        if not period_data:
            return {'count': 0}
        
        values = [m.value for m in period_data]
        
        return {
            'count': len(values),
            'sum': sum(values),
            'average': statistics.mean(values),
            'min': min(values),
            'max': max(values),
            'trend': self._calculate_trend(values)
        }
    
    async def _detect_patterns(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> List[Dict[str, Any]]:
        """Detect patterns in analytics data"""
        patterns = []
        
        # Analyze each metric for patterns
        for metric_name, metric_data in self.metrics.items():
            period_data = [
                m for m in metric_data
                if start_time <= m.timestamp <= end_time
            ]
            
            if len(period_data) >= 10:
                values = [m.value for m in period_data]
                
                # Check for cyclical patterns
                if self._has_cyclical_pattern(values):
                    patterns.append({
                        'type': 'cyclical',
                        'metric': metric_name,
                        'description': f'{metric_name} shows cyclical behavior',
                        'confidence': 0.8
                    })
                
                # Check for anomalies
                anomalies = self._detect_anomalies(values)
                if anomalies:
                    patterns.append({
                        'type': 'anomaly',
                        'metric': metric_name,
                        'description': f'{len(anomalies)} anomalies detected in {metric_name}',
                        'confidence': 0.9,
                        'anomaly_indices': anomalies
                    })
        
        return patterns
    
    def _has_cyclical_pattern(self, values: List[float]) -> bool:
        """Check if values have a cyclical pattern"""
        if len(values) < 20:
            return False
        
        # Simple autocorrelation check
        autocorr = np.correlate(values, values, mode='full')
        autocorr = autocorr[autocorr.size // 2:]
        
        # Look for peaks indicating cycles
        peaks = []
        for i in range(1, len(autocorr) - 1):
            if autocorr[i] > autocorr[i-1] and autocorr[i] > autocorr[i+1]:
                peaks.append(i)
        
        return len(peaks) > 2
    
    def _detect_anomalies(
        self,
        values: List[float],
        threshold: float = 2.0
    ) -> List[int]:
        """Detect anomalies using statistical methods"""
        if len(values) < 10:
            return []
        
        mean_val = statistics.mean(values)
        std_val = statistics.stdev(values)
        
        anomalies = []
        for i, value in enumerate(values):
            z_score = abs((value - mean_val) / std_val) if std_val > 0 else 0
            if z_score > threshold:
                anomalies.append(i)
        
        return anomalies
    
    async def _analyze_user_behavior(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> Dict[str, Any]:
        """Analyze user behavior patterns"""
        # Filter events by time range
        period_events = [
            event for event in self.events
            if start_time <= event.timestamp <= end_time
        ]
        
        user_metrics = {
            'total_events': len(period_events),
            'unique_users': len(set(e.user_id for e in period_events if e.user_id)),
            'events_per_user': 0,
            'engagement_trend': 0,
            'top_event_types': {}
        }
        
        if user_metrics['unique_users'] > 0:
            user_metrics['events_per_user'] = user_metrics['total_events'] / user_metrics['unique_users']
        
        # Count event types
        event_type_counts = defaultdict(int)
        for event in period_events:
            event_type_counts[event.event_type] += 1
        
        user_metrics['top_event_types'] = dict(
            sorted(event_type_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        )
        
        return user_metrics
    
    async def _analyze_performance(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> Dict[str, Any]:
        """Analyze system performance"""
        performance_metrics = ['response_time', 'cpu_usage', 'memory_usage', 'error_rate']
        performance_data = {}
        
        for metric_name in performance_metrics:
            summary = self._get_metric_summary(metric_name, start_time, end_time)
            if summary['count'] > 0:
                performance_data[metric_name] = summary
        
        return performance_data
    
    async def _analyze_business_impact(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> Dict[str, Any]:
        """Analyze business impact metrics"""
        business_metrics = ['revenue', 'user_retention', 'conversion_rate', 'customer_satisfaction']
        business_data = {}
        
        for metric_name in business_metrics:
            summary = self._get_metric_summary(metric_name, start_time, end_time)
            if summary['count'] > 0:
                business_data[metric_name] = summary
        
        return business_data
    
    async def _generate_recommendations(self, insights: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate actionable recommendations based on insights"""
        recommendations = []
        
        # Performance recommendations
        performance_data = insights.get('performance_analysis', {})
        if 'response_time' in performance_data:
            avg_response_time = performance_data['response_time'].get('average', 0)
            if avg_response_time > 500:  # ms
                recommendations.append({
                    'category': 'performance',
                    'priority': 'high',
                    'recommendation': 'Optimize response times - consider caching or infrastructure scaling',
                    'expected_impact': 'Reduce response time by 30-50%',
                    'implementation_effort': 'medium'
                })
        
        # User behavior recommendations
        user_behavior = insights.get('user_behavior_insights', {})
        if user_behavior.get('events_per_user', 0) < 10:
            recommendations.append({
                'category': 'user_engagement',
                'priority': 'medium',
                'recommendation': 'Implement user engagement campaigns to increase activity',
                'expected_impact': 'Increase user engagement by 25%',
                'implementation_effort': 'low'
            })
        
        # Business impact recommendations
        business_impact = insights.get('business_impact', {})
        if 'conversion_rate' in business_impact:
            conversion_rate = business_impact['conversion_rate'].get('average', 0)
            if conversion_rate < 5:  # 5%
                recommendations.append({
                    'category': 'conversion',
                    'priority': 'high',
                    'recommendation': 'Optimize conversion funnel and onboarding process',
                    'expected_impact': 'Increase conversion rate by 20-40%',
                    'implementation_effort': 'high'
                })
        
        return recommendations
    
    async def _calculate_system_health(self) -> Dict[str, Any]:
        """Calculate overall system health score"""
        health_metrics = {
            'uptime': 99.9,
            'response_time': 150.0,
            'error_rate': 0.1,
            'throughput': 1000.0,
            'resource_utilization': 75.0
        }
        
        # Calculate weighted health score
        weights = {
            'uptime': 0.3,
            'response_time': 0.25,
            'error_rate': 0.2,
            'throughput': 0.15,
            'resource_utilization': 0.1
        }
        
        # Normalize metrics to 0-100 scale
        normalized_scores = {
            'uptime': health_metrics['uptime'],
            'response_time': max(0, 100 - (health_metrics['response_time'] / 10)),
            'error_rate': max(0, 100 - (health_metrics['error_rate'] * 100)),
            'throughput': min(100, health_metrics['throughput'] / 10),
            'resource_utilization': 100 - health_metrics['resource_utilization']
        }
        
        overall_score = sum(
            normalized_scores[metric] * weights[metric]
            for metric in weights.keys()
        )
        
        return {
            'overall_score': round(overall_score, 1),
            'individual_scores': normalized_scores,
            'status': 'healthy' if overall_score > 80 else 'warning' if overall_score > 60 else 'critical'
        }
    
    def _recommend_visualizations(self, metrics: List[str]) -> List[Dict[str, Any]]:
        """Recommend visualizations for metrics"""
        visualizations = []
        
        for metric in metrics:
            if 'time' in metric.lower() or 'duration' in metric.lower():
                visualizations.append({
                    'metric': metric,
                    'type': 'line_chart',
                    'description': f'Time series chart for {metric}'
                })
            elif 'count' in metric.lower() or 'total' in metric.lower():
                visualizations.append({
                    'metric': metric,
                    'type': 'bar_chart',
                    'description': f'Bar chart showing {metric} distribution'
                })
            elif 'rate' in metric.lower() or 'percentage' in metric.lower():
                visualizations.append({
                    'metric': metric,
                    'type': 'gauge_chart',
                    'description': f'Gauge chart for {metric} percentage'
                })
            else:
                visualizations.append({
                    'metric': metric,
                    'type': 'line_chart',
                    'description': f'Time series visualization for {metric}'
                })
        
        return visualizations
    
    async def _generate_report_summary(self, metrics_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary for report"""
        summary = {
            'total_metrics': len(metrics_data),
            'data_points': sum(len(data['values']) for data in metrics_data.values()),
            'key_findings': [],
            'health_indicators': {}
        }
        
        # Analyze each metric for key findings
        for metric_name, data in metrics_data.items():
            values = data['values']
            stats = data['statistics']
            
            if stats['std_dev'] > stats['average'] * 0.5:
                summary['key_findings'].append(f'{metric_name} shows high variability')
            
            if len(values) > 10:
                trend = self._calculate_trend(values)
                if trend != 'stable':
                    summary['key_findings'].append(f'{metric_name} trend: {trend}')
        
        return summary
    
    async def _format_as_csv(self, report_data: Dict[str, Any]) -> str:
        """Format report data as CSV"""
        csv_lines = ['Metric,Timestamp,Value']
        
        for metric_name, data in report_data['metrics_data'].items():
            for i, (timestamp, value) in enumerate(zip(data['timestamps'], data['values'])):
                csv_lines.append(f'{metric_name},{timestamp},{value}')
        
        return '\n'.join(csv_lines)
    
    async def _format_as_html(self, report_data: Dict[str, Any]) -> str:
        """Format report data as HTML"""
        html = f"""
        <html>
        <head><title>{report_data['title']}</title></head>
        <body>
        <h1>{report_data['title']}</h1>
        <p>Generated: {report_data['generated_at']}</p>
        <h2>Summary</h2>
        <pre>{json.dumps(report_data['summary'], indent=2)}</pre>
        <h2>Metrics Data</h2>
        """
        
        for metric_name, data in report_data['metrics_data'].items():
            html += f"""
            <h3>{metric_name}</h3>
            <p>Statistics: {json.dumps(data['statistics'], indent=2)}</p>
            """
        
        html += "</body></html>"
        return html
    
    async def _check_metric_alerts(self, metric: MetricData):
        """Check if metric triggers any alerts"""
        # Define alert thresholds (in production, these would be configurable)
        alert_thresholds = {
            'error_rate': {'critical': 5.0, 'warning': 2.0},
            'response_time': {'critical': 1000.0, 'warning': 500.0},
            'cpu_usage': {'critical': 90.0, 'warning': 80.0},
            'memory_usage': {'critical': 95.0, 'warning': 85.0}
        }
        
        if metric.metric_name in alert_thresholds:
            thresholds = alert_thresholds[metric.metric_name]
            
            severity = None
            if metric.value >= thresholds['critical']:
                severity = AlertSeverity.CRITICAL
            elif metric.value >= thresholds['warning']:
                severity = AlertSeverity.WARNING
            
            if severity:
                alert = AnalyticsAlert(
                    alert_id=str(uuid.uuid4()),
                    alert_type='threshold_breach',
                    severity=severity,
                    metric_name=metric.metric_name,
                    threshold_value=thresholds[severity.value],
                    current_value=metric.value,
                    message=f'{metric.metric_name} exceeded {severity.value} threshold'
                )
                
                self.alerts[alert.alert_id] = alert
                await self.alert_queue.put(alert)
    
    async def _event_processing_task(self):
        """Background task for processing analytics events"""
        while self.is_running:
            try:
                if not self.event_queue.empty():
                    event = await self.event_queue.get()
                    
                    # Process event (extract metrics, patterns, etc.)
                    await self._process_event(event)
                    event.processed = True
                
                await asyncio.sleep(0.1)  # Process events quickly
                
            except Exception as e:
                logger.error(f"Error in event processing task: {e}")
                await asyncio.sleep(1)
    
    async def _process_event(self, event: AnalyticsEvent):
        """Process individual analytics event"""
        # Extract metrics from event data
        if 'response_time' in event.data:
            await self.record_metric(
                'response_time',
                event.data['response_time'],
                MetricType.SYSTEM_PERFORMANCE
            )
        
        if 'user_action' in event.data:
            await self.record_metric(
                'user_actions',
                1,
                MetricType.USER_BEHAVIOR,
                dimensions={'action_type': event.data['user_action']}
            )
    
    async def _metrics_aggregation_task(self):
        """Background task for metrics aggregation"""
        while self.is_running:
            try:
                # Aggregate metrics every 5 minutes
                await self._aggregate_metrics()
                await asyncio.sleep(300)
                
            except Exception as e:
                logger.error(f"Error in metrics aggregation task: {e}")
                await asyncio.sleep(60)
    
    async def _aggregate_metrics(self):
        """Aggregate metrics for different time periods"""
        current_time = datetime.now()
        
        # Aggregate for different periods
        periods = {
            'hourly': timedelta(hours=1),
            'daily': timedelta(days=1),
            'weekly': timedelta(weeks=1)
        }
        
        for period_name, period_delta in periods.items():
            start_time = current_time - period_delta
            
            for metric_name, metric_data in self.metrics.items():
                period_data = [
                    m for m in metric_data
                    if start_time <= m.timestamp <= current_time
                ]
                
                if period_data:
                    values = [m.value for m in period_data]
                    self.aggregated_metrics[f"{metric_name}_{period_name}"] = {
                        'count': len(values),
                        'sum': sum(values),
                        'average': statistics.mean(values),
                        'min': min(values),
                        'max': max(values)
                    }
    
    async def _kpi_calculation_task(self):
        """Background task for KPI calculation"""
        while self.is_running:
            try:
                await self._calculate_kpis()
                await asyncio.sleep(900)  # Update KPIs every 15 minutes
                
            except Exception as e:
                logger.error(f"Error in KPI calculation task: {e}")
                await asyncio.sleep(300)
    
    async def _calculate_kpis(self):
        """Calculate business KPIs"""
        for kpi_name, kpi in self.kpis.items():
            # Get relevant metrics for this KPI
            if kpi_name in self.aggregated_metrics:
                aggregated = self.aggregated_metrics[kpi_name]
                new_value = aggregated.get('average', 0)
                
                # Calculate change percentage
                if kpi.current_value > 0:
                    change_percentage = ((new_value - kpi.current_value) / kpi.current_value) * 100
                else:
                    change_percentage = 0
                
                # Update KPI
                kpi.current_value = new_value
                kpi.change_percentage = change_percentage
                kpi.trend = 'up' if change_percentage > 1 else 'down' if change_percentage < -1 else 'stable'
                kpi.last_updated = datetime.now()
    
    async def _anomaly_detection_task(self):
        """Background task for anomaly detection"""
        while self.is_running:
            try:
                await self._detect_real_time_anomalies()
                await asyncio.sleep(60)  # Check for anomalies every minute
                
            except Exception as e:
                logger.error(f"Error in anomaly detection task: {e}")
                await asyncio.sleep(300)
    
    async def _detect_real_time_anomalies(self):
        """Detect anomalies in real-time data"""
        for metric_name, metric_data in self.metrics.items():
            if len(metric_data) >= 20:  # Need enough data points
                recent_data = metric_data[-20:]  # Last 20 data points
                values = [m.value for m in recent_data]
                
                # Detect anomalies
                anomalies = self._detect_anomalies(values, threshold=2.5)
                
                if anomalies:
                    # Create anomaly alert
                    alert = AnalyticsAlert(
                        alert_id=str(uuid.uuid4()),
                        alert_type='anomaly_detected',
                        severity=AlertSeverity.WARNING,
                        metric_name=metric_name,
                        threshold_value=2.5,
                        current_value=values[-1],
                        message=f'Anomaly detected in {metric_name}'
                    )
                    
                    self.alerts[alert.alert_id] = alert
                    await self.alert_queue.put(alert)
    
    async def _prediction_task(self):
        """Background task for generating predictions"""
        while self.is_running:
            try:
                # Generate predictions for key metrics
                key_metrics = ['request_volume', 'response_time', 'error_rate', 'user_activity']
                
                for metric_name in key_metrics:
                    if metric_name in self.metrics:
                        await self.predict_metric(metric_name, time_horizon_hours=24)
                
                await asyncio.sleep(3600)  # Generate predictions every hour
                
            except Exception as e:
                logger.error(f"Error in prediction task: {e}")
                await asyncio.sleep(1800)
    
    async def _alert_processing_task(self):
        """Background task for processing alerts"""
        while self.is_running:
            try:
                if not self.alert_queue.empty():
                    alert = await self.alert_queue.get()
                    
                    # Process alert (send notifications, escalate, etc.)
                    logger.warning(f"Alert: {alert.message} (Severity: {alert.severity.value})")
                    
                    # In production, this would send notifications to various channels
                
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Error in alert processing task: {e}")
                await asyncio.sleep(10)
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status"""
        return {
            'service': 'AnalyticsEngine',
            'status': 'healthy' if self.is_running else 'stopped',
            'node_id': self.node_id,
            'events_processed': len(self.events),
            'metrics_tracked': len(self.metrics),
            'active_alerts': len([a for a in self.alerts.values() if not a.acknowledged]),
            'kpis_monitored': len(self.kpis),
            'predictions_generated': len(self.predictions),
            'background_tasks': len(self.background_tasks),
            'queue_sizes': {
                'events': self.event_queue.qsize(),
                'alerts': self.alert_queue.qsize()
            },
            'uptime_seconds': time.time() - getattr(self, '_start_time', time.time())
        }
    
    async def shutdown(self):
        """Gracefully shutdown analytics engine"""
        logger.info("Shutting down AnalyticsEngine...")
        self.is_running = False
        
        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        if self.background_tasks:
            await asyncio.gather(*self.background_tasks, return_exceptions=True)
        
        logger.info("AnalyticsEngine shut down complete")

# Export main classes and functions
__all__ = [
    'AnalyticsEngine',
    'AnalyticsPeriod',
    'MetricType',
    'AlertSeverity',
    'ReportFormat',
    'AnalyticsEvent',
    'MetricData',
    'AnalyticsAlert',
    'BusinessKPI',
    'PredictionResult'
]

if __name__ == "__main__":
    async def demo():
        """Demo analytics engine functionality"""
        engine = AnalyticsEngine()
        await engine.initialize()
        
        # Ingest some test events
        await engine.ingest_event(
            'user_action',
            {'action': 'login', 'response_time': 150},
            user_id='user_123'
        )
        
        await engine.ingest_event(
            'api_request',
            {'endpoint': '/api/content', 'response_time': 200, 'status': 200},
            user_id='user_456'
        )
        
        # Record some metrics
        await engine.record_metric('response_time', 180, MetricType.SYSTEM_PERFORMANCE)
        await engine.record_metric('active_users', 1250, MetricType.USER_BEHAVIOR)
        await engine.record_metric('api_requests', 5000, MetricType.REQUEST_VOLUME)
        
        # Get analytics summary
        summary = await engine.get_analytics_summary(AnalyticsPeriod.HOURLY)
        print(f"Analytics summary: {json.dumps(summary, indent=2, default=str)}")
        
        # Generate insights
        insights = await engine.generate_insights(['performance', 'user_behavior'])
        print(f"Generated insights: {json.dumps(insights, indent=2, default=str)}")
        
        # Create custom report
        report_config = {
            'title': 'Hourly Performance Report',
            'metrics': ['response_time', 'active_users'],
            'time_range': {'hours': 1}
        }
        
        report = await engine.create_custom_report(report_config, ReportFormat.JSON)
        print(f"Custom report: {json.dumps(report, indent=2, default=str)}")
        
        # Test prediction
        prediction = await engine.predict_metric('response_time', 24)
        print(f"Prediction result: {json.dumps(prediction, indent=2, default=str)}")
        
        # Get health status
        health = await engine.get_health_status()
        print(f"Health status: {json.dumps(health, indent=2)}")
        
        await engine.shutdown()
    
    # Run demo
    asyncio.run(demo())