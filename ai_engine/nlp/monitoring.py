"""
Advanced Monitoring Module for IA Influencer Agent Platform

Real-time monitoring and analytics system for content performance,
sentiment tracking, and trend analysis.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - Unauthorized use prohibited ⚠️
This software is proprietary and confidential. Contact: mlaiel@live.de
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple, Set, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
import json
import time
from abc import ABC, abstractmethod
import numpy as np
from enum import Enum

logger = logging.getLogger(__name__)

class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class MetricType(Enum):
    """Types of metrics to monitor"""
    ENGAGEMENT = "engagement"
    SENTIMENT = "sentiment"
    PERFORMANCE = "performance"
    CONTENT_QUALITY = "content_quality"
    BRAND_SAFETY = "brand_safety"
    TREND = "trend"
    AUDIENCE = "audience"

@dataclass
class MonitoringAlert:
    """Monitoring alert structure"""
    alert_id: str
    level: AlertLevel
    metric_type: MetricType
    title: str
    description: str
    value: float
    threshold: float
    timestamp: datetime
    source: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    resolved: bool = False
    resolution_timestamp: Optional[datetime] = None

@dataclass
class MetricSnapshot:
    """Snapshot of a metric at a point in time"""
    metric_name: str
    value: float
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TrendAnalysis:
    """Trend analysis result"""
    metric_name: str
    trend_direction: str  # rising, falling, stable, volatile
    trend_strength: float  # 0-1, how strong the trend is
    change_rate: float  # percentage change
    confidence: float  # confidence in the trend analysis
    time_period: str
    data_points: List[float]
    analysis_timestamp: datetime

@dataclass
class PerformanceReport:
    """Performance monitoring report"""
    report_id: str
    time_period: str
    metrics_summary: Dict[str, Any]
    trends: List[TrendAnalysis]
    alerts: List[MonitoringAlert]
    recommendations: List[str]
    generated_at: datetime
    next_report_due: datetime

@dataclass
class RealTimeMetrics:
    """Real-time metrics dashboard"""
    current_metrics: Dict[str, float]
    recent_changes: Dict[str, float]
    active_alerts: List[MonitoringAlert]
    trend_indicators: Dict[str, str]
    last_updated: datetime

class MetricCollector(ABC):
    """Abstract base class for metric collectors"""
    
    @abstractmethod
    async def collect_metrics(self) -> List[MetricSnapshot]:
        """Collect metrics from source"""
        pass
    
    @abstractmethod
    def get_collector_name(self) -> str:
        """Get collector name"""
        pass

class EngagementMetricCollector(MetricCollector):
    """Collector for engagement metrics"""
    
    def __init__(self, platform_apis: Dict[str, Any]):
        self.platform_apis = platform_apis
    
    async def collect_metrics(self) -> List[MetricSnapshot]:
        """Collect engagement metrics from platforms"""
        metrics = []
        timestamp = datetime.utcnow()
        
        # Simulate collecting metrics from different platforms
        platform_metrics = {
            'instagram': {
                'likes_per_post': np.random.normal(1500, 300),
                'comments_per_post': np.random.normal(150, 50),
                'shares_per_post': np.random.normal(75, 25),
                'engagement_rate': np.random.normal(4.5, 1.0)
            },
            'tiktok': {
                'views_per_video': np.random.normal(50000, 15000),
                'likes_per_video': np.random.normal(2500, 500),
                'comments_per_video': np.random.normal(200, 75),
                'engagement_rate': np.random.normal(6.2, 1.5)
            },
            'youtube': {
                'views_per_video': np.random.normal(25000, 8000),
                'likes_per_video': np.random.normal(800, 200),
                'comments_per_video': np.random.normal(120, 40),
                'watch_time_minutes': np.random.normal(3.5, 1.0)
            }
        }
        
        for platform, platform_data in platform_metrics.items():
            for metric_name, value in platform_data.items():
                metric = MetricSnapshot(
                    metric_name=f"{platform}_{metric_name}",
                    value=max(0, value),  # Ensure non-negative values
                    timestamp=timestamp,
                    tags={'platform': platform, 'type': 'engagement'},
                    metadata={'collector': self.get_collector_name()}
                )
                metrics.append(metric)
        
        return metrics
    
    def get_collector_name(self) -> str:
        return "engagement_collector"

class SentimentMetricCollector(MetricCollector):
    """Collector for sentiment metrics"""
    
    def __init__(self, nlp_analyzer):
        self.nlp_analyzer = nlp_analyzer
    
    async def collect_metrics(self) -> List[MetricSnapshot]:
        """Collect sentiment metrics"""
        metrics = []
        timestamp = datetime.utcnow()
        
        # Simulate sentiment data collection
        sentiment_data = {
            'overall_sentiment': np.random.normal(0.3, 0.2),  # Slightly positive
            'positive_mentions': np.random.normal(0.6, 0.15),
            'negative_mentions': np.random.normal(0.15, 0.1),
            'neutral_mentions': np.random.normal(0.25, 0.1),
            'brand_safety_score': np.random.normal(0.85, 0.1),
            'authenticity_score': np.random.normal(0.78, 0.15)
        }
        
        for metric_name, value in sentiment_data.items():
            metric = MetricSnapshot(
                metric_name=metric_name,
                value=np.clip(value, -1, 1) if 'sentiment' in metric_name else np.clip(value, 0, 1),
                timestamp=timestamp,
                tags={'type': 'sentiment'},
                metadata={'collector': self.get_collector_name()}
            )
            metrics.append(metric)
        
        return metrics
    
    def get_collector_name(self) -> str:
        return "sentiment_collector"

class PerformanceMetricCollector(MetricCollector):
    """Collector for performance metrics"""
    
    def __init__(self):
        pass
    
    async def collect_metrics(self) -> List[MetricSnapshot]:
        """Collect performance metrics"""
        metrics = []
        timestamp = datetime.utcnow()
        
        # Simulate performance data
        performance_data = {
            'follower_growth_rate': np.random.normal(2.5, 1.0),  # Percentage
            'content_reach': np.random.normal(15000, 5000),
            'impression_rate': np.random.normal(8.5, 2.0),
            'click_through_rate': np.random.normal(1.8, 0.5),
            'conversion_rate': np.random.normal(0.85, 0.3),
            'roi_percentage': np.random.normal(245, 75)
        }
        
        for metric_name, value in performance_data.items():
            metric = MetricSnapshot(
                metric_name=metric_name,
                value=max(0, value),
                timestamp=timestamp,
                tags={'type': 'performance'},
                metadata={'collector': self.get_collector_name()}
            )
            metrics.append(metric)
        
        return metrics
    
    def get_collector_name(self) -> str:
        return "performance_collector"

class AdvancedNLPMonitor:
    """
    Advanced NLP monitoring system
    
    Features:
    - Real-time metric collection
    - Trend analysis and forecasting
    - Intelligent alerting
    - Performance reporting
    - Anomaly detection
    - Custom dashboards
    - Automated insights
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._get_default_config()
        self.collectors: List[MetricCollector] = []
        self.metrics_store = defaultdict(deque)  # Store recent metrics
        self.alert_handlers: List[Callable] = []
        self.active_alerts: List[MonitoringAlert] = []
        self.trend_analyzer = TrendAnalyzer()
        self.anomaly_detector = AnomalyDetector()
        self.report_generator = ReportGenerator()
        self.is_monitoring = False
        self.monitoring_task = None
        
        # Initialize metric collectors
        self._initialize_collectors()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default monitoring configuration"""
        return {
            'collection_interval': 60,  # seconds
            'metrics_retention_days': 30,
            'trend_analysis_window': 24,  # hours
            'anomaly_detection_enabled': True,
            'real_time_alerts': True,
            'report_generation_interval': 3600,  # seconds (1 hour)
            'max_stored_metrics': 10000,
            'alert_thresholds': {
                'engagement_rate_drop': 20,  # percentage
                'sentiment_negative_spike': 0.3,
                'brand_safety_low': 0.6,
                'follower_growth_negative': -5
            }
        }
    
    def _initialize_collectors(self):
        """Initialize metric collectors"""
        # Add default collectors
        self.add_collector(EngagementMetricCollector({}))
        self.add_collector(SentimentMetricCollector(None))
        self.add_collector(PerformanceMetricCollector())
    
    def add_collector(self, collector: MetricCollector):
        """Add a metric collector"""
        self.collectors.append(collector)
        logger.info(f"Added collector: {collector.get_collector_name()}")
    
    def add_alert_handler(self, handler: Callable[[MonitoringAlert], None]):
        """Add an alert handler function"""
        self.alert_handlers.append(handler)
    
    async def start_monitoring(self):
        """Start the monitoring system"""
        if self.is_monitoring:
            logger.warning("Monitoring is already running")
            return
        
        self.is_monitoring = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("NLP monitoring started")
    
    async def stop_monitoring(self):
        """Stop the monitoring system"""
        if not self.is_monitoring:
            return
        
        self.is_monitoring = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        logger.info("NLP monitoring stopped")
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        last_report_time = datetime.utcnow()
        
        while self.is_monitoring:
            try:
                # Collect metrics from all collectors
                await self._collect_all_metrics()
                
                # Analyze trends
                await self._analyze_trends()
                
                # Detect anomalies
                if self.config['anomaly_detection_enabled']:
                    await self._detect_anomalies()
                
                # Check alert conditions
                if self.config['real_time_alerts']:
                    await self._check_alert_conditions()
                
                # Generate reports if needed
                current_time = datetime.utcnow()
                if (current_time - last_report_time).total_seconds() >= self.config['report_generation_interval']:
                    await self._generate_periodic_report()
                    last_report_time = current_time
                
                # Clean up old metrics
                await self._cleanup_old_metrics()
                
                # Wait for next collection interval
                await asyncio.sleep(self.config['collection_interval'])
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {str(e)}")
                await asyncio.sleep(self.config['collection_interval'])
    
    async def _collect_all_metrics(self):
        """Collect metrics from all collectors"""
        for collector in self.collectors:
            try:
                metrics = await collector.collect_metrics()
                
                for metric in metrics:
                    # Store metric
                    self.metrics_store[metric.metric_name].append(metric)
                    
                    # Limit stored metrics
                    if len(self.metrics_store[metric.metric_name]) > self.config['max_stored_metrics']:
                        self.metrics_store[metric.metric_name].popleft()
                
                logger.debug(f"Collected {len(metrics)} metrics from {collector.get_collector_name()}")
                
            except Exception as e:
                logger.error(f"Error collecting metrics from {collector.get_collector_name()}: {str(e)}")
    
    async def _analyze_trends(self):
        """Analyze trends in collected metrics"""
        for metric_name, metric_history in self.metrics_store.items():
            if len(metric_history) >= 10:  # Need minimum data points
                try:
                    trend_analysis = await self.trend_analyzer.analyze_trend(
                        metric_name, list(metric_history)
                    )
                    
                    # Store trend analysis results
                    # In production, this would be stored in a database
                    logger.debug(f"Trend analysis for {metric_name}: {trend_analysis.trend_direction}")
                    
                except Exception as e:
                    logger.error(f"Error analyzing trend for {metric_name}: {str(e)}")
    
    async def _detect_anomalies(self):
        """Detect anomalies in metrics"""
        for metric_name, metric_history in self.metrics_store.items():
            if len(metric_history) >= 20:  # Need sufficient history
                try:
                    is_anomaly, anomaly_score = await self.anomaly_detector.detect_anomaly(
                        metric_name, list(metric_history)
                    )
                    
                    if is_anomaly:
                        await self._create_anomaly_alert(metric_name, anomaly_score, metric_history[-1])
                    
                except Exception as e:
                    logger.error(f"Error detecting anomalies for {metric_name}: {str(e)}")
    
    async def _check_alert_conditions(self):
        """Check for alert conditions"""
        thresholds = self.config['alert_thresholds']
        
        for metric_name, metric_history in self.metrics_store.items():
            if len(metric_history) < 2:
                continue
            
            try:
                current_metric = metric_history[-1]
                previous_metric = metric_history[-2]
                
                # Check for engagement rate drop
                if 'engagement_rate' in metric_name:
                    change_percent = ((current_metric.value - previous_metric.value) / previous_metric.value) * 100
                    if change_percent < -thresholds['engagement_rate_drop']:
                        await self._create_threshold_alert(
                            metric_name, current_metric.value, change_percent,
                            AlertLevel.WARNING, "Engagement rate dropped significantly"
                        )
                
                # Check for negative sentiment spike
                if metric_name == 'negative_mentions':
                    if current_metric.value > thresholds['sentiment_negative_spike']:
                        await self._create_threshold_alert(
                            metric_name, current_metric.value, thresholds['sentiment_negative_spike'],
                            AlertLevel.ERROR, "Spike in negative sentiment detected"
                        )
                
                # Check for low brand safety
                if metric_name == 'brand_safety_score':
                    if current_metric.value < thresholds['brand_safety_low']:
                        await self._create_threshold_alert(
                            metric_name, current_metric.value, thresholds['brand_safety_low'],
                            AlertLevel.CRITICAL, "Brand safety score below threshold"
                        )
                
                # Check for negative follower growth
                if metric_name == 'follower_growth_rate':
                    if current_metric.value < thresholds['follower_growth_negative']:
                        await self._create_threshold_alert(
                            metric_name, current_metric.value, thresholds['follower_growth_negative'],
                            AlertLevel.WARNING, "Negative follower growth detected"
                        )
                
            except Exception as e:
                logger.error(f"Error checking alert conditions for {metric_name}: {str(e)}")
    
    async def _create_anomaly_alert(self, metric_name: str, anomaly_score: float, metric: MetricSnapshot):
        """Create an anomaly alert"""
        alert = MonitoringAlert(
            alert_id=self._generate_alert_id(),
            level=AlertLevel.WARNING if anomaly_score < 0.8 else AlertLevel.ERROR,
            metric_type=MetricType.PERFORMANCE,
            title=f"Anomaly detected in {metric_name}",
            description=f"Unusual pattern detected with anomaly score {anomaly_score:.2f}",
            value=metric.value,
            threshold=anomaly_score,
            timestamp=datetime.utcnow(),
            source="anomaly_detector",
            metadata={
                'metric_name': metric_name,
                'anomaly_score': anomaly_score,
                'metric_timestamp': metric.timestamp.isoformat()
            }
        )
        
        await self._trigger_alert(alert)
    
    async def _create_threshold_alert(self, metric_name: str, value: float, threshold: float,
                                    level: AlertLevel, description: str):
        """Create a threshold-based alert"""
        alert = MonitoringAlert(
            alert_id=self._generate_alert_id(),
            level=level,
            metric_type=self._get_metric_type_from_name(metric_name),
            title=f"Threshold exceeded for {metric_name}",
            description=description,
            value=value,
            threshold=threshold,
            timestamp=datetime.utcnow(),
            source="threshold_monitor",
            metadata={'metric_name': metric_name}
        )
        
        await self._trigger_alert(alert)
    
    async def _trigger_alert(self, alert: MonitoringAlert):
        """Trigger an alert"""
        self.active_alerts.append(alert)
        
        # Call alert handlers
        for handler in self.alert_handlers:
            try:
                await asyncio.create_task(handler(alert))
            except Exception as e:
                logger.error(f"Error in alert handler: {str(e)}")
        
        logger.warning(f"Alert triggered: {alert.title}")
    
    async def _generate_periodic_report(self):
        """Generate periodic performance report"""
        try:
            report = await self.report_generator.generate_report(
                self.metrics_store, self.active_alerts
            )
            
            # In production, this would be stored and/or sent to stakeholders
            logger.info(f"Generated periodic report: {report.report_id}")
            
        except Exception as e:
            logger.error(f"Error generating periodic report: {str(e)}")
    
    async def _cleanup_old_metrics(self):
        """Clean up old metrics beyond retention period"""
        cutoff_time = datetime.utcnow() - timedelta(days=self.config['metrics_retention_days'])
        
        for metric_name in self.metrics_store:
            # Remove old metrics
            while (self.metrics_store[metric_name] and 
                   self.metrics_store[metric_name][0].timestamp < cutoff_time):
                self.metrics_store[metric_name].popleft()
    
    def _get_metric_type_from_name(self, metric_name: str) -> MetricType:
        """Determine metric type from name"""
        if 'engagement' in metric_name:
            return MetricType.ENGAGEMENT
        elif 'sentiment' in metric_name:
            return MetricType.SENTIMENT
        elif 'brand_safety' in metric_name:
            return MetricType.BRAND_SAFETY
        elif 'trend' in metric_name:
            return MetricType.TREND
        else:
            return MetricType.PERFORMANCE
    
    def _generate_alert_id(self) -> str:
        """Generate unique alert ID"""
        import hashlib
        timestamp = str(time.time())
        return hashlib.md5(timestamp.encode()).hexdigest()[:12]
    
    async def get_real_time_metrics(self) -> RealTimeMetrics:
        """Get current real-time metrics"""
        current_metrics = {}
        recent_changes = {}
        trend_indicators = {}
        
        for metric_name, metric_history in self.metrics_store.items():
            if metric_history:
                current_metrics[metric_name] = metric_history[-1].value
                
                # Calculate recent change
                if len(metric_history) >= 2:
                    current_value = metric_history[-1].value
                    previous_value = metric_history[-2].value
                    change = ((current_value - previous_value) / previous_value) * 100 if previous_value != 0 else 0
                    recent_changes[metric_name] = change
                    
                    # Determine trend indicator
                    if change > 5:
                        trend_indicators[metric_name] = "rising"
                    elif change < -5:
                        trend_indicators[metric_name] = "falling"
                    else:
                        trend_indicators[metric_name] = "stable"
        
        return RealTimeMetrics(
            current_metrics=current_metrics,
            recent_changes=recent_changes,
            active_alerts=self.active_alerts.copy(),
            trend_indicators=trend_indicators,
            last_updated=datetime.utcnow()
        )
    
    async def get_metric_history(self, metric_name: str, hours: int = 24) -> List[MetricSnapshot]:
        """Get metric history for specified time period"""
        if metric_name not in self.metrics_store:
            return []
        
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        return [
            metric for metric in self.metrics_store[metric_name]
            if metric.timestamp >= cutoff_time
        ]
    
    async def resolve_alert(self, alert_id: str):
        """Resolve an active alert"""
        for alert in self.active_alerts:
            if alert.alert_id == alert_id:
                alert.resolved = True
                alert.resolution_timestamp = datetime.utcnow()
                logger.info(f"Alert resolved: {alert_id}")
                return
        
        logger.warning(f"Alert not found: {alert_id}")

class TrendAnalyzer:
    """Analyzes trends in metric data"""
    
    async def analyze_trend(self, metric_name: str, metric_history: List[MetricSnapshot]) -> TrendAnalysis:
        """Analyze trend in metric data"""
        if len(metric_history) < 10:
            return TrendAnalysis(
                metric_name=metric_name,
                trend_direction="insufficient_data",
                trend_strength=0.0,
                change_rate=0.0,
                confidence=0.0,
                time_period="insufficient",
                data_points=[],
                analysis_timestamp=datetime.utcnow()
            )
        
        # Extract values and calculate trend
        values = [metric.value for metric in metric_history]
        timestamps = [metric.timestamp for metric in metric_history]
        
        # Calculate simple linear trend
        x = np.arange(len(values))
        slope, intercept = np.polyfit(x, values, 1)
        
        # Determine trend direction
        if abs(slope) < 0.01:
            trend_direction = "stable"
        elif slope > 0:
            trend_direction = "rising"
        else:
            trend_direction = "falling"
        
        # Calculate trend strength (R-squared)
        predicted = slope * x + intercept
        ss_res = np.sum((values - predicted) ** 2)
        ss_tot = np.sum((values - np.mean(values)) ** 2)
        trend_strength = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        
        # Calculate change rate
        if len(values) >= 2:
            change_rate = ((values[-1] - values[0]) / values[0]) * 100 if values[0] != 0 else 0
        else:
            change_rate = 0
        
        # Calculate confidence based on data consistency
        confidence = min(1.0, trend_strength * (len(values) / 100))
        
        time_period = f"{len(metric_history)} data points"
        
        return TrendAnalysis(
            metric_name=metric_name,
            trend_direction=trend_direction,
            trend_strength=trend_strength,
            change_rate=change_rate,
            confidence=confidence,
            time_period=time_period,
            data_points=values,
            analysis_timestamp=datetime.utcnow()
        )

class AnomalyDetector:
    """Detects anomalies in metric data"""
    
    async def detect_anomaly(self, metric_name: str, metric_history: List[MetricSnapshot]) -> Tuple[bool, float]:
        """Detect if latest metric value is anomalous"""
        if len(metric_history) < 20:
            return False, 0.0
        
        # Get recent values (excluding the latest one for comparison)
        recent_values = [metric.value for metric in metric_history[:-1]]
        current_value = metric_history[-1].value
        
        # Calculate statistical measures
        mean_value = np.mean(recent_values)
        std_value = np.std(recent_values)
        
        if std_value == 0:
            return False, 0.0
        
        # Calculate z-score
        z_score = abs((current_value - mean_value) / std_value)
        
        # Determine if anomalous (z-score > 2.5 is considered anomalous)
        is_anomaly = z_score > 2.5
        
        # Calculate anomaly score (normalized z-score)
        anomaly_score = min(1.0, z_score / 4.0)
        
        return is_anomaly, anomaly_score

class ReportGenerator:
    """Generates monitoring reports"""
    
    async def generate_report(self, metrics_store: Dict[str, deque], 
                            active_alerts: List[MonitoringAlert]) -> PerformanceReport:
        """Generate comprehensive performance report"""
        
        report_id = self._generate_report_id()
        current_time = datetime.utcnow()
        
        # Calculate metrics summary
        metrics_summary = await self._calculate_metrics_summary(metrics_store)
        
        # Analyze trends for key metrics
        trends = await self._analyze_key_trends(metrics_store)
        
        # Generate recommendations
        recommendations = await self._generate_recommendations(metrics_summary, trends, active_alerts)
        
        return PerformanceReport(
            report_id=report_id,
            time_period="last_hour",
            metrics_summary=metrics_summary,
            trends=trends,
            alerts=active_alerts.copy(),
            recommendations=recommendations,
            generated_at=current_time,
            next_report_due=current_time + timedelta(hours=1)
        )
    
    async def _calculate_metrics_summary(self, metrics_store: Dict[str, deque]) -> Dict[str, Any]:
        """Calculate summary statistics for metrics"""
        summary = {}
        
        for metric_name, metric_history in metrics_store.items():
            if metric_history:
                values = [metric.value for metric in metric_history]
                
                summary[metric_name] = {
                    'current_value': values[-1],
                    'average': np.mean(values),
                    'min': np.min(values),
                    'max': np.max(values),
                    'std_dev': np.std(values),
                    'data_points': len(values)
                }
        
        return summary
    
    async def _analyze_key_trends(self, metrics_store: Dict[str, deque]) -> List[TrendAnalysis]:
        """Analyze trends for key metrics"""
        key_metrics = [
            'engagement_rate', 'overall_sentiment', 'follower_growth_rate',
            'brand_safety_score', 'content_reach'
        ]
        
        trends = []
        trend_analyzer = TrendAnalyzer()
        
        for metric_name in key_metrics:
            for full_metric_name in metrics_store.keys():
                if metric_name in full_metric_name and metrics_store[full_metric_name]:
                    trend = await trend_analyzer.analyze_trend(
                        full_metric_name, list(metrics_store[full_metric_name])
                    )
                    trends.append(trend)
                    break
        
        return trends
    
    async def _generate_recommendations(self, metrics_summary: Dict[str, Any],
                                      trends: List[TrendAnalysis],
                                      active_alerts: List[MonitoringAlert]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Analyze engagement trends
        engagement_trends = [t for t in trends if 'engagement' in t.metric_name]
        for trend in engagement_trends:
            if trend.trend_direction == "falling" and trend.confidence > 0.7:
                recommendations.append(
                    f"Engagement is declining for {trend.metric_name}. "
                    "Consider analyzing recent content quality and posting times."
                )
        
        # Analyze sentiment trends
        sentiment_trends = [t for t in trends if 'sentiment' in t.metric_name]
        for trend in sentiment_trends:
            if trend.trend_direction == "falling" and 'negative' not in trend.metric_name:
                recommendations.append(
                    "Sentiment is declining. Review recent content for potential issues "
                    "and consider engaging more positively with audience."
                )
        
        # Alert-based recommendations
        critical_alerts = [a for a in active_alerts if a.level == AlertLevel.CRITICAL]
        if critical_alerts:
            recommendations.append(
                f"Address {len(critical_alerts)} critical alerts immediately. "
                "Review brand safety and content quality."
            )
        
        # Brand safety recommendations
        brand_safety_metrics = {k: v for k, v in metrics_summary.items() if 'brand_safety' in k}
        for metric_name, metric_data in brand_safety_metrics.items():
            if metric_data['current_value'] < 0.7:
                recommendations.append(
                    "Brand safety score is low. Review content for potential issues "
                    "and ensure compliance with brand guidelines."
                )
        
        # Growth recommendations
        growth_metrics = {k: v for k, v in metrics_summary.items() if 'growth' in k}
        for metric_name, metric_data in growth_metrics.items():
            if metric_data['current_value'] < 0:
                recommendations.append(
                    "Follower growth is negative. Analyze content strategy and "
                    "consider audience engagement improvements."
                )
        
        if not recommendations:
            recommendations.append("All metrics are performing well. Continue current strategy.")
        
        return recommendations
    
    def _generate_report_id(self) -> str:
        """Generate unique report ID"""
        import hashlib
        timestamp = str(time.time())
        return f"report_{hashlib.md5(timestamp.encode()).hexdigest()[:8]}"

# Utility functions for monitoring
async def setup_basic_monitoring() -> AdvancedNLPMonitor:
    """Set up basic monitoring with default configuration"""
    monitor = AdvancedNLPMonitor()
    
    # Add basic alert handler
    async def console_alert_handler(alert: MonitoringAlert):
        print(f"ALERT [{alert.level.value.upper()}]: {alert.title}")
        print(f"Description: {alert.description}")
        print(f"Value: {alert.value}, Threshold: {alert.threshold}")
        print("-" * 50)
    
    monitor.add_alert_handler(console_alert_handler)
    
    return monitor

async def get_monitoring_dashboard(monitor: AdvancedNLPMonitor) -> Dict[str, Any]:
    """Get monitoring dashboard data"""
    real_time_metrics = await monitor.get_real_time_metrics()
    
    return {
        'current_metrics': real_time_metrics.current_metrics,
        'recent_changes': real_time_metrics.recent_changes,
        'active_alerts': len(real_time_metrics.active_alerts),
        'critical_alerts': len([a for a in real_time_metrics.active_alerts if a.level == AlertLevel.CRITICAL]),
        'trend_indicators': real_time_metrics.trend_indicators,
        'last_updated': real_time_metrics.last_updated.isoformat(),
        'system_status': 'healthy' if len(real_time_metrics.active_alerts) == 0 else 'needs_attention'
    }
