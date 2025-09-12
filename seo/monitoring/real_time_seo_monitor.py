"""Real-time SEO Monitor - Advanced Real-time SEO Performance Monitoring
Comprehensive real-time monitoring system for SEO performance including ranking changes,
traffic anomalies, technical issues, and competitive intelligence.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid
import statistics
import numpy as np
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class MonitoringMetric(Enum):
    """SEO metrics to monitor"""
    RANKINGS = "rankings"
    ORGANIC_TRAFFIC = "organic_traffic"
    CLICK_THROUGH_RATE = "click_through_rate"
    IMPRESSIONS = "impressions"
    CORE_WEB_VITALS = "core_web_vitals"
    PAGE_SPEED = "page_speed"
    INDEXATION_STATUS = "indexation_status"
    BACKLINKS = "backlinks"
    BRAND_MENTIONS = "brand_mentions"
    COMPETITOR_ACTIVITY = "competitor_activity"
    TECHNICAL_ERRORS = "technical_errors"
    CONTENT_FRESHNESS = "content_freshness"


class AlertType(Enum):
    """Types of SEO alerts"""
    RANKING_DROP = "ranking_drop"
    TRAFFIC_SPIKE = "traffic_spike"
    TRAFFIC_DROP = "traffic_drop"
    TECHNICAL_ERROR = "technical_error"
    INDEXATION_ISSUE = "indexation_issue"
    COMPETITOR_MOVEMENT = "competitor_movement"
    CORE_WEB_VITALS_ISSUE = "core_web_vitals_issue"
    BACKLINK_LOSS = "backlink_loss"
    CONTENT_ISSUE = "content_issue"
    SECURITY_ISSUE = "security_issue"


@dataclass
class SEOAlert:
    """SEO monitoring alert"""
    alert_id: str
    alert_type: AlertType
    severity: AlertSeverity
    metric: MonitoringMetric
    message: str
    detected_at: datetime
    affected_url: str
    current_value: float
    previous_value: float
    threshold_value: float
    change_percentage: float
    impact_assessment: str
    recommended_actions: List[str] = field(default_factory=list)
    related_data: Dict[str, Any] = field(default_factory=dict)
    status: str = "active"
    resolved_at: Optional[datetime] = None
    resolution_notes: str = ""


@dataclass
class MetricDataPoint:
    """Single metric data point"""
    timestamp: datetime
    metric: MonitoringMetric
    value: float
    url: str
    keyword: Optional[str] = None
    device: str = "desktop"
    location: str = "global"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MonitoringRule:
    """Monitoring rule configuration"""
    rule_id: str
    name: str
    metric: MonitoringMetric
    threshold_type: str  # "absolute", "percentage", "standard_deviation"
    threshold_value: float
    comparison_period: timedelta
    alert_severity: AlertSeverity
    enabled: bool = True
    urls: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    conditions: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RealTimeReport:
    """Real-time SEO monitoring report"""
    report_id: str
    generated_at: datetime
    active_alerts: List[SEOAlert]
    metric_summary: Dict[MonitoringMetric, Dict[str, float]]
    performance_trends: Dict[str, List[float]]
    anomaly_detection: Dict[str, Any]
    competitive_intelligence: Dict[str, Any]
    system_health: Dict[str, str]
    recommendations: List[str]


class RealTimeSEOMonitor:
    """Advanced real-time SEO monitoring system"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize real-time SEO monitor
        
        Args:
            config: Configuration including monitoring rules, data sources
        """
        self.config = config
        self.monitoring_rules: List[MonitoringRule] = []
        self.metric_data: Dict[MonitoringMetric, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.alerts: List[SEOAlert] = []
        self.alert_callbacks: List[Callable] = []
        self.anomaly_detectors = {}
        self.baseline_metrics = {}
        self.monitoring_active = False
        self.monitoring_interval = config.get('monitoring_interval', 60)  # seconds
        
        # Initialize anomaly detection models
        self._initialize_anomaly_detection()
        
    def _initialize_anomaly_detection(self):
        """Initialize anomaly detection models for each metric"""
        for metric in MonitoringMetric:
            self.anomaly_detectors[metric] = {
                'moving_average_window': 100,
                'std_dev_threshold': 2.5,
                'seasonal_patterns': {},
                'historical_data': deque(maxlen=1000)
            }
    
    async def start_monitoring(self):
        """Start real-time SEO monitoring"""
        try:
            self.monitoring_active = True
            logger.info("Starting real-time SEO monitoring")
            
            # Start monitoring tasks
            monitoring_tasks = [
                asyncio.create_task(self._monitor_rankings()),
                asyncio.create_task(self._monitor_traffic()),
                asyncio.create_task(self._monitor_technical_health()),
                asyncio.create_task(self._monitor_competitors()),
                asyncio.create_task(self._process_alerts()),
                asyncio.create_task(self._anomaly_detection_loop())
            ]
            
            # Wait for monitoring tasks
            await asyncio.gather(*monitoring_tasks, return_exceptions=True)
            
        except Exception as e:
            logger.error(f"Error in real-time monitoring: {str(e)}")
            self.monitoring_active = False
    
    async def stop_monitoring(self):
        """Stop real-time SEO monitoring"""
        self.monitoring_active = False
        logger.info("Stopped real-time SEO monitoring")
    
    async def add_monitoring_rule(self, rule: MonitoringRule):
        """Add a new monitoring rule"""
        try:
            self.monitoring_rules.append(rule)
            logger.info(f"Added monitoring rule: {rule.name}")
            
            # Initialize baseline for new rule
            await self._initialize_baseline_for_rule(rule)
            
        except Exception as e:
            logger.error(f"Error adding monitoring rule: {str(e)}")
    
    async def _monitor_rankings(self):
        """Monitor search rankings in real-time"""
        try:
            while self.monitoring_active:
                # Get current rankings data
                rankings_data = await self._fetch_rankings_data()
                
                for data_point in rankings_data:
                    # Store metric data
                    self.metric_data[MonitoringMetric.RANKINGS].append(data_point)
                    
                    # Check for ranking changes
                    await self._check_ranking_alerts(data_point)
                
                await asyncio.sleep(self.monitoring_interval)
                
        except Exception as e:
            logger.error(f"Error in rankings monitoring: {str(e)}")
    
    async def _monitor_traffic(self):
        """Monitor organic traffic in real-time"""
        try:
            while self.monitoring_active:
                # Get current traffic data
                traffic_data = await self._fetch_traffic_data()
                
                for data_point in traffic_data:
                    # Store metric data
                    self.metric_data[MonitoringMetric.ORGANIC_TRAFFIC].append(data_point)
                    
                    # Check for traffic anomalies
                    await self._check_traffic_alerts(data_point)
                
                await asyncio.sleep(self.monitoring_interval)
                
        except Exception as e:
            logger.error(f"Error in traffic monitoring: {str(e)}")
    
    async def _monitor_technical_health(self):
        """Monitor technical SEO health in real-time"""
        try:
            while self.monitoring_active:
                # Check Core Web Vitals
                cwv_data = await self._fetch_core_web_vitals()
                for data_point in cwv_data:
                    self.metric_data[MonitoringMetric.CORE_WEB_VITALS].append(data_point)
                    await self._check_technical_alerts(data_point)
                
                # Check indexation status
                indexation_data = await self._fetch_indexation_status()
                for data_point in indexation_data:
                    self.metric_data[MonitoringMetric.INDEXATION_STATUS].append(data_point)
                    await self._check_indexation_alerts(data_point)
                
                # Check for technical errors
                error_data = await self._fetch_technical_errors()
                for data_point in error_data:
                    self.metric_data[MonitoringMetric.TECHNICAL_ERRORS].append(data_point)
                    await self._check_error_alerts(data_point)
                
                await asyncio.sleep(self.monitoring_interval * 2)  # Less frequent for technical checks
                
        except Exception as e:
            logger.error(f"Error in technical health monitoring: {str(e)}")
    
    async def _monitor_competitors(self):
        """Monitor competitor activities in real-time"""
        try:
            while self.monitoring_active:
                # Get competitor data
                competitor_data = await self._fetch_competitor_data()
                
                for data_point in competitor_data:
                    self.metric_data[MonitoringMetric.COMPETITOR_ACTIVITY].append(data_point)
                    await self._check_competitor_alerts(data_point)
                
                await asyncio.sleep(self.monitoring_interval * 5)  # Less frequent for competitor monitoring
                
        except Exception as e:
            logger.error(f"Error in competitor monitoring: {str(e)}")
    
    async def _process_alerts(self):
        """Process and manage alerts"""
        try:
            while self.monitoring_active:
                # Process pending alerts
                for alert in self.alerts:
                    if alert.status == "active":
                        await self._process_alert(alert)
                
                # Clean up old resolved alerts
                cutoff_time = datetime.now() - timedelta(days=7)
                self.alerts = [
                    alert for alert in self.alerts
                    if alert.status == "active" or 
                    (alert.resolved_at and alert.resolved_at > cutoff_time)
                ]
                
                await asyncio.sleep(30)  # Process alerts every 30 seconds
                
        except Exception as e:
            logger.error(f"Error in alert processing: {str(e)}")
    
    async def _anomaly_detection_loop(self):
        """Run anomaly detection algorithms"""
        try:
            while self.monitoring_active:
                for metric in MonitoringMetric:
                    if self.metric_data[metric]:
                        anomalies = await self._detect_anomalies(metric)
                        
                        for anomaly in anomalies:
                            await self._create_anomaly_alert(metric, anomaly)
                
                await asyncio.sleep(300)  # Run anomaly detection every 5 minutes
                
        except Exception as e:
            logger.error(f"Error in anomaly detection: {str(e)}")
    
    async def _check_ranking_alerts(self, data_point: MetricDataPoint):
        """Check for ranking-related alerts"""
        try:
            # Get previous ranking for comparison
            previous_data = await self._get_previous_metric_value(
                MonitoringMetric.RANKINGS, 
                data_point.url, 
                data_point.keyword
            )
            
            if previous_data:
                change = data_point.value - previous_data.value
                change_percentage = (change / previous_data.value) * 100 if previous_data.value > 0 else 0
                
                # Check ranking drop thresholds
                for rule in self.monitoring_rules:
                    if (rule.metric == MonitoringMetric.RANKINGS and 
                        rule.enabled and 
                        (not rule.urls or data_point.url in rule.urls) and
                        (not rule.keywords or data_point.keyword in rule.keywords)):
                        
                        if self._evaluate_threshold(change, change_percentage, rule):
                            alert = SEOAlert(
                                alert_id=self._generate_alert_id(),
                                alert_type=AlertType.RANKING_DROP if change > 0 else AlertType.RANKING_DROP,  # Higher rank number = drop
                                severity=rule.alert_severity,
                                metric=MonitoringMetric.RANKINGS,
                                message=f"Ranking change detected for '{data_point.keyword}' on {data_point.url}: {change:+.1f} positions",
                                detected_at=datetime.now(),
                                affected_url=data_point.url,
                                current_value=data_point.value,
                                previous_value=previous_data.value,
                                threshold_value=rule.threshold_value,
                                change_percentage=change_percentage,
                                impact_assessment=await self._assess_ranking_impact(change, data_point),
                                recommended_actions=await self._get_ranking_recommendations(change, data_point)
                            )
                            
                            await self._trigger_alert(alert)
            
        except Exception as e:
            logger.error(f"Error checking ranking alerts: {str(e)}")
    
    async def _check_traffic_alerts(self, data_point: MetricDataPoint):
        """Check for traffic-related alerts"""
        try:
            # Get baseline traffic for comparison
            baseline = await self._get_baseline_value(MonitoringMetric.ORGANIC_TRAFFIC, data_point.url)
            
            if baseline:
                change_percentage = ((data_point.value - baseline) / baseline) * 100
                
                for rule in self.monitoring_rules:
                    if (rule.metric == MonitoringMetric.ORGANIC_TRAFFIC and 
                        rule.enabled and 
                        (not rule.urls or data_point.url in rule.urls)):
                        
                        if abs(change_percentage) > rule.threshold_value:
                            alert_type = AlertType.TRAFFIC_SPIKE if change_percentage > 0 else AlertType.TRAFFIC_DROP
                            
                            alert = SEOAlert(
                                alert_id=self._generate_alert_id(),
                                alert_type=alert_type,
                                severity=rule.alert_severity,
                                metric=MonitoringMetric.ORGANIC_TRAFFIC,
                                message=f"Traffic {'spike' if change_percentage > 0 else 'drop'} detected for {data_point.url}: {change_percentage:+.1f}%",
                                detected_at=datetime.now(),
                                affected_url=data_point.url,
                                current_value=data_point.value,
                                previous_value=baseline,
                                threshold_value=rule.threshold_value,
                                change_percentage=change_percentage,
                                impact_assessment=await self._assess_traffic_impact(change_percentage, data_point),
                                recommended_actions=await self._get_traffic_recommendations(change_percentage, data_point)
                            )
                            
                            await self._trigger_alert(alert)
            
        except Exception as e:
            logger.error(f"Error checking traffic alerts: {str(e)}")
    
    async def _check_technical_alerts(self, data_point: MetricDataPoint):
        """Check for technical SEO alerts"""
        try:
            # Core Web Vitals thresholds
            cwv_thresholds = {
                'lcp': 2.5,  # Largest Contentful Paint (seconds)
                'fid': 0.1,  # First Input Delay (seconds)
                'cls': 0.1   # Cumulative Layout Shift
            }
            
            if data_point.metadata.get('metric_type') in cwv_thresholds:
                threshold = cwv_thresholds[data_point.metadata['metric_type']]
                
                if data_point.value > threshold:
                    alert = SEOAlert(
                        alert_id=self._generate_alert_id(),
                        alert_type=AlertType.CORE_WEB_VITALS_ISSUE,
                        severity=AlertSeverity.HIGH,
                        metric=MonitoringMetric.CORE_WEB_VITALS,
                        message=f"Core Web Vitals issue: {data_point.metadata['metric_type'].upper()} exceeds threshold ({data_point.value:.3f} > {threshold})",
                        detected_at=datetime.now(),
                        affected_url=data_point.url,
                        current_value=data_point.value,
                        previous_value=threshold,
                        threshold_value=threshold,
                        change_percentage=((data_point.value - threshold) / threshold) * 100,
                        impact_assessment="Core Web Vitals impact user experience and SEO rankings",
                        recommended_actions=[
                            "Optimize page loading performance",
                            "Reduce server response times",
                            "Minimize layout shifts",
                            "Optimize images and resources"
                        ]
                    )
                    
                    await self._trigger_alert(alert)
            
        except Exception as e:
            logger.error(f"Error checking technical alerts: {str(e)}")
    
    async def _check_indexation_alerts(self, data_point: MetricDataPoint):
        """Check for indexation issues"""
        try:
            # If indexation status drops below threshold
            if data_point.value < 0.9:  # 90% indexation threshold
                alert = SEOAlert(
                    alert_id=self._generate_alert_id(),
                    alert_type=AlertType.INDEXATION_ISSUE,
                    severity=AlertSeverity.HIGH,
                    metric=MonitoringMetric.INDEXATION_STATUS,
                    message=f"Indexation issue detected: {data_point.value:.1%} of pages indexed",
                    detected_at=datetime.now(),
                    affected_url=data_point.url,
                    current_value=data_point.value,
                    previous_value=0.9,
                    threshold_value=0.9,
                    change_percentage=((data_point.value - 0.9) / 0.9) * 100,
                    impact_assessment="Low indexation affects organic visibility",
                    recommended_actions=[
                        "Check for crawl errors",
                        "Review robots.txt and sitemap",
                        "Investigate blocked pages",
                        "Submit pages for re-indexing"
                    ]
                )
                
                await self._trigger_alert(alert)
            
        except Exception as e:
            logger.error(f"Error checking indexation alerts: {str(e)}")
    
    async def _check_error_alerts(self, data_point: MetricDataPoint):
        """Check for technical error alerts"""
        try:
            # If error count exceeds threshold
            if data_point.value > 10:  # More than 10 errors
                alert = SEOAlert(
                    alert_id=self._generate_alert_id(),
                    alert_type=AlertType.TECHNICAL_ERROR,
                    severity=AlertSeverity.HIGH if data_point.value > 50 else AlertSeverity.MEDIUM,
                    metric=MonitoringMetric.TECHNICAL_ERRORS,
                    message=f"Technical errors detected: {int(data_point.value)} errors found",
                    detected_at=datetime.now(),
                    affected_url=data_point.url,
                    current_value=data_point.value,
                    previous_value=10,
                    threshold_value=10,
                    change_percentage=((data_point.value - 10) / 10) * 100,
                    impact_assessment="Technical errors can impact crawling and indexing",
                    recommended_actions=[
                        "Review server logs",
                        "Fix broken links",
                        "Resolve server errors",
                        "Update sitemap"
                    ]
                )
                
                await self._trigger_alert(alert)
            
        except Exception as e:
            logger.error(f"Error checking error alerts: {str(e)}")
    
    async def _check_competitor_alerts(self, data_point: MetricDataPoint):
        """Check for competitor activity alerts"""
        try:
            # Significant competitor movement
            if abs(data_point.value) > 5:  # 5+ position change
                alert = SEOAlert(
                    alert_id=self._generate_alert_id(),
                    alert_type=AlertType.COMPETITOR_MOVEMENT,
                    severity=AlertSeverity.MEDIUM,
                    metric=MonitoringMetric.COMPETITOR_ACTIVITY,
                    message=f"Competitor movement detected: {data_point.metadata.get('competitor', 'Unknown')} changed {data_point.value:+.1f} positions",
                    detected_at=datetime.now(),
                    affected_url=data_point.url,
                    current_value=data_point.value,
                    previous_value=0,
                    threshold_value=5,
                    change_percentage=0,
                    impact_assessment="Competitor changes may affect market positioning",
                    recommended_actions=[
                        "Analyze competitor strategy",
                        "Review content gaps",
                        "Assess backlink opportunities",
                        "Monitor keyword targeting"
                    ]
                )
                
                await self._trigger_alert(alert)
            
        except Exception as e:
            logger.error(f"Error checking competitor alerts: {str(e)}")
    
    async def _detect_anomalies(self, metric: MonitoringMetric) -> List[Dict[str, Any]]:
        """Detect anomalies in metric data using statistical methods"""
        try:
            anomalies = []
            data_points = list(self.metric_data[metric])
            
            if len(data_points) < 50:  # Need sufficient data for anomaly detection
                return anomalies
            
            # Extract values for analysis
            values = [dp.value for dp in data_points[-100:]]  # Last 100 data points
            
            # Calculate statistical measures
            mean = statistics.mean(values)
            std_dev = statistics.stdev(values) if len(values) > 1 else 0
            
            # Z-score based anomaly detection
            threshold = self.anomaly_detectors[metric]['std_dev_threshold']
            
            for i, data_point in enumerate(data_points[-10:]):  # Check last 10 points
                if std_dev > 0:
                    z_score = abs(data_point.value - mean) / std_dev
                    
                    if z_score > threshold:
                        anomalies.append({
                            'data_point': data_point,
                            'z_score': z_score,
                            'deviation': data_point.value - mean,
                            'severity': 'high' if z_score > threshold * 1.5 else 'medium'
                        })
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Error detecting anomalies for {metric}: {str(e)}")
            return []
    
    async def _create_anomaly_alert(self, metric: MonitoringMetric, anomaly: Dict[str, Any]):
        """Create alert for detected anomaly"""
        try:
            data_point = anomaly['data_point']
            
            alert = SEOAlert(
                alert_id=self._generate_alert_id(),
                alert_type=AlertType.TRAFFIC_SPIKE if anomaly['deviation'] > 0 else AlertType.TRAFFIC_DROP,
                severity=AlertSeverity.HIGH if anomaly['severity'] == 'high' else AlertSeverity.MEDIUM,
                metric=metric,
                message=f"Statistical anomaly detected in {metric.value}: Z-score {anomaly['z_score']:.2f}",
                detected_at=datetime.now(),
                affected_url=data_point.url,
                current_value=data_point.value,
                previous_value=data_point.value - anomaly['deviation'],
                threshold_value=self.anomaly_detectors[metric]['std_dev_threshold'],
                change_percentage=0,
                impact_assessment="Statistical anomaly may indicate significant change",
                recommended_actions=[
                    "Investigate underlying cause",
                    "Verify data accuracy",
                    "Check for external factors",
                    "Monitor continued performance"
                ]
            )
            
            await self._trigger_alert(alert)
            
        except Exception as e:
            logger.error(f"Error creating anomaly alert: {str(e)}")
    
    async def _trigger_alert(self, alert: SEOAlert):
        """Trigger an alert and notify stakeholders"""
        try:
            # Add to alerts list
            self.alerts.append(alert)
            
            # Call alert callbacks
            for callback in self.alert_callbacks:
                try:
                    await callback(alert)
                except Exception as e:
                    logger.error(f"Error in alert callback: {str(e)}")
            
            logger.warning(f"SEO Alert: {alert.message}")
            
        except Exception as e:
            logger.error(f"Error triggering alert: {str(e)}")
    
    async def _process_alert(self, alert: SEOAlert):
        """Process and enrich alert data"""
        try:
            # Auto-resolve certain types of alerts if conditions improve
            if alert.alert_type in [AlertType.TRAFFIC_SPIKE, AlertType.TRAFFIC_DROP]:
                current_value = await self._get_current_metric_value(alert.metric, alert.affected_url)
                if current_value and abs(current_value - alert.previous_value) < alert.threshold_value:
                    alert.status = "resolved"
                    alert.resolved_at = datetime.now()
                    alert.resolution_notes = "Metric returned to normal range"
            
        except Exception as e:
            logger.error(f"Error processing alert: {str(e)}")
    
    async def generate_realtime_report(self) -> RealTimeReport:
        """Generate real-time SEO monitoring report"""
        try:
            active_alerts = [alert for alert in self.alerts if alert.status == "active"]
            
            # Metric summary
            metric_summary = {}
            for metric in MonitoringMetric:
                if self.metric_data[metric]:
                    recent_values = [dp.value for dp in list(self.metric_data[metric])[-100:]]
                    metric_summary[metric] = {
                        'current': recent_values[-1] if recent_values else 0,
                        'average': statistics.mean(recent_values) if recent_values else 0,
                        'min': min(recent_values) if recent_values else 0,
                        'max': max(recent_values) if recent_values else 0,
                        'trend': 'stable'  # Would calculate actual trend
                    }
            
            # Performance trends
            performance_trends = {}
            for metric in MonitoringMetric:
                if self.metric_data[metric]:
                    recent_values = [dp.value for dp in list(self.metric_data[metric])[-24:]]  # Last 24 data points
                    performance_trends[metric.value] = recent_values
            
            # Anomaly detection summary
            anomaly_detection = {
                'anomalies_detected': len([a for a in active_alerts if 'anomaly' in a.message.lower()]),
                'most_volatile_metric': 'rankings',  # Would calculate actual volatility
                'stability_score': 0.8  # Would calculate based on variance
            }
            
            # Competitive intelligence
            competitive_intelligence = {
                'competitor_movements': len([a for a in active_alerts if a.alert_type == AlertType.COMPETITOR_MOVEMENT]),
                'market_volatility': 'medium',
                'opportunity_score': 0.7
            }
            
            # System health
            system_health = {
                'monitoring_status': 'active' if self.monitoring_active else 'inactive',
                'data_freshness': 'good',
                'alert_system': 'operational',
                'coverage': f"{len(self.monitoring_rules)} rules active"
            }
            
            # Recommendations
            recommendations = await self._generate_realtime_recommendations(active_alerts, metric_summary)
            
            return RealTimeReport(
                report_id=str(uuid.uuid4()),
                generated_at=datetime.now(),
                active_alerts=active_alerts,
                metric_summary=metric_summary,
                performance_trends=performance_trends,
                anomaly_detection=anomaly_detection,
                competitive_intelligence=competitive_intelligence,
                system_health=system_health,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Error generating real-time report: {str(e)}")
            raise
    
    # Data fetching methods (would integrate with real APIs)
    async def _fetch_rankings_data(self) -> List[MetricDataPoint]:
        """Fetch current rankings data"""
        # Mock data - would integrate with Google Search Console, SEMrush, etc.
        return [
            MetricDataPoint(
                timestamp=datetime.now(),
                metric=MonitoringMetric.RANKINGS,
                value=5.0,  # Position 5
                url="https://example.com/page1",
                keyword="target keyword",
                device="desktop"
            )
        ]
    
    async def _fetch_traffic_data(self) -> List[MetricDataPoint]:
        """Fetch current traffic data"""
        # Mock data - would integrate with Google Analytics, etc.
        return [
            MetricDataPoint(
                timestamp=datetime.now(),
                metric=MonitoringMetric.ORGANIC_TRAFFIC,
                value=1500.0,  # Daily organic sessions
                url="https://example.com"
            )
        ]
    
    async def _fetch_core_web_vitals(self) -> List[MetricDataPoint]:
        """Fetch Core Web Vitals data"""
        # Mock data - would integrate with PageSpeed Insights, CrUX API
        return [
            MetricDataPoint(
                timestamp=datetime.now(),
                metric=MonitoringMetric.CORE_WEB_VITALS,
                value=2.1,  # LCP in seconds
                url="https://example.com",
                metadata={'metric_type': 'lcp'}
            )
        ]
    
    async def _fetch_indexation_status(self) -> List[MetricDataPoint]:
        """Fetch indexation status data"""
        return [
            MetricDataPoint(
                timestamp=datetime.now(),
                metric=MonitoringMetric.INDEXATION_STATUS,
                value=0.95,  # 95% indexed
                url="https://example.com"
            )
        ]
    
    async def _fetch_technical_errors(self) -> List[MetricDataPoint]:
        """Fetch technical errors data"""
        return [
            MetricDataPoint(
                timestamp=datetime.now(),
                metric=MonitoringMetric.TECHNICAL_ERRORS,
                value=3.0,  # 3 errors
                url="https://example.com"
            )
        ]
    
    async def _fetch_competitor_data(self) -> List[MetricDataPoint]:
        """Fetch competitor data"""
        return [
            MetricDataPoint(
                timestamp=datetime.now(),
                metric=MonitoringMetric.COMPETITOR_ACTIVITY,
                value=2.0,  # +2 position change
                url="https://example.com",
                metadata={'competitor': 'competitor.com'}
            )
        ]
    
    # Helper methods
    def _generate_alert_id(self) -> str:
        """Generate unique alert ID"""
        return f"alert_{uuid.uuid4().hex[:8]}"
    
    async def _get_previous_metric_value(self, metric: MonitoringMetric, url: str, keyword: Optional[str] = None) -> Optional[MetricDataPoint]:
        """Get previous metric value for comparison"""
        data_points = [
            dp for dp in self.metric_data[metric]
            if dp.url == url and (not keyword or dp.keyword == keyword)
        ]
        return data_points[-2] if len(data_points) >= 2 else None
    
    async def _get_baseline_value(self, metric: MonitoringMetric, url: str) -> Optional[float]:
        """Get baseline value for metric"""
        if metric in self.baseline_metrics and url in self.baseline_metrics[metric]:
            return self.baseline_metrics[metric][url]
        
        # Calculate baseline from historical data
        data_points = [dp for dp in self.metric_data[metric] if dp.url == url]
        if len(data_points) >= 30:
            values = [dp.value for dp in data_points[-30:]]
            return statistics.mean(values)
        
        return None
    
    async def _get_current_metric_value(self, metric: MonitoringMetric, url: str) -> Optional[float]:
        """Get current metric value"""
        data_points = [dp for dp in self.metric_data[metric] if dp.url == url]
        return data_points[-1].value if data_points else None
    
    def _evaluate_threshold(self, change: float, change_percentage: float, rule: MonitoringRule) -> bool:
        """Evaluate if threshold is exceeded"""
        if rule.threshold_type == "absolute":
            return abs(change) > rule.threshold_value
        elif rule.threshold_type == "percentage":
            return abs(change_percentage) > rule.threshold_value
        elif rule.threshold_type == "standard_deviation":
            # Would implement standard deviation logic
            return abs(change) > rule.threshold_value
        return False
    
    async def _initialize_baseline_for_rule(self, rule: MonitoringRule):
        """Initialize baseline metrics for new rule"""
        # Would initialize baseline calculations
        pass
    
    async def _assess_ranking_impact(self, change: float, data_point: MetricDataPoint) -> str:
        """Assess impact of ranking change"""
        if abs(change) > 10:
            return "High impact - significant ranking change"
        elif abs(change) > 5:
            return "Medium impact - moderate ranking change"
        else:
            return "Low impact - minor ranking fluctuation"
    
    async def _assess_traffic_impact(self, change_percentage: float, data_point: MetricDataPoint) -> str:
        """Assess impact of traffic change"""
        if abs(change_percentage) > 50:
            return "High impact - significant traffic change"
        elif abs(change_percentage) > 20:
            return "Medium impact - moderate traffic change"
        else:
            return "Low impact - minor traffic fluctuation"
    
    async def _get_ranking_recommendations(self, change: float, data_point: MetricDataPoint) -> List[str]:
        """Get recommendations for ranking changes"""
        if change > 0:  # Ranking dropped
            return [
                "Analyze competitor content strategies",
                "Review and update content",
                "Check for technical issues",
                "Audit backlink profile"
            ]
        else:  # Ranking improved
            return [
                "Monitor to ensure stability",
                "Analyze successful factors",
                "Apply learnings to other pages"
            ]
    
    async def _get_traffic_recommendations(self, change_percentage: float, data_point: MetricDataPoint) -> List[str]:
        """Get recommendations for traffic changes"""
        if change_percentage < 0:  # Traffic dropped
            return [
                "Check for technical issues",
                "Analyze ranking changes",
                "Review seasonal patterns",
                "Investigate algorithm updates"
            ]
        else:  # Traffic increased
            return [
                "Analyze traffic sources",
                "Optimize for conversion",
                "Scale successful strategies"
            ]
    
    async def _generate_realtime_recommendations(self, alerts: List[SEOAlert], metrics: Dict) -> List[str]:
        """Generate real-time recommendations"""
        recommendations = []
        
        if any(alert.severity == AlertSeverity.CRITICAL for alert in alerts):
            recommendations.append("Address critical alerts immediately")
        
        if len(alerts) > 10:
            recommendations.append("High alert volume - review monitoring thresholds")
        
        recommendations.extend([
            "Monitor Core Web Vitals for user experience",
            "Track competitor movements for opportunities",
            "Maintain content freshness and quality"
        ])
        
        return recommendations
    
    def add_alert_callback(self, callback: Callable[[SEOAlert], None]):
        """Add callback function for alert notifications"""
        self.alert_callbacks.append(callback)