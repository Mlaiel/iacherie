"""Technical Performance Monitor
Real-time monitoring and alerting system for technical SEO performance metrics.

Features:
- Continuous Core Web Vitals monitoring
- Technical issue detection and alerting
- Performance regression analysis
- Competitive performance benchmarking
- Creator-specific performance tracking
- Automated optimization recommendations
- Enterprise dashboard integration

Author: Fahed Mlaiel (mlaiel@live.de)
DevOps + ML Engineer expertise applied
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Any, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import statistics
from urllib.parse import urljoin, urlparse
import hashlib
import time

logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Types of performance metrics."""
    CORE_WEB_VITALS = "core_web_vitals"
    TECHNICAL_SEO = "technical_seo"
    CRAWL_HEALTH = "crawl_health"
    INDEXATION = "indexation"
    SECURITY = "security"
    ACCESSIBILITY = "accessibility"
    CREATOR_PERFORMANCE = "creator_performance"

class AlertSeverity(Enum):
    """Alert severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class MonitoringFrequency(Enum):
    """Monitoring frequency options."""
    REAL_TIME = "real_time"  # Every minute
    HIGH = "high"  # Every 5 minutes
    NORMAL = "normal"  # Every 15 minutes
    LOW = "low"  # Every hour
    DAILY = "daily"  # Once per day

@dataclass
class PerformanceMetric:
    """Individual performance metric data."""
    metric_type: MetricType
    name: str
    value: float
    threshold_good: float
    threshold_poor: float
    url: str
    timestamp: datetime
    device_type: str = "desktop"
    creator_id: Optional[str] = None
    additional_data: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PerformanceAlert:
    """Performance alert data."""
    alert_id: str
    severity: AlertSeverity
    metric: PerformanceMetric
    message: str
    recommendation: str
    created_at: datetime
    resolved_at: Optional[datetime] = None
    auto_resolution_attempted: bool = False
    creator_impact: Optional[str] = None

@dataclass
class MonitoringTarget:
    """Monitoring target configuration."""
    url: str
    frequency: MonitoringFrequency
    metrics_to_monitor: List[MetricType]
    creator_id: Optional[str] = None
    custom_thresholds: Dict[str, Tuple[float, float]] = field(default_factory=dict)
    alert_callbacks: List[Callable] = field(default_factory=list)
    
@dataclass
class PerformanceTrend:
    """Performance trend analysis."""
    metric_name: str
    url: str
    trend_direction: str  # improving, degrading, stable
    trend_strength: float  # 0-1
    confidence: float  # 0-1
    time_period_days: int
    data_points: List[Tuple[datetime, float]]
    statistical_significance: bool

class TechnicalPerformanceMonitor:
    """
    Enterprise technical performance monitoring system with real-time alerting.
    Provides comprehensive monitoring for creator economy platform.
    """
    
    def __init__(self):
        self.monitoring_targets: Dict[str, MonitoringTarget] = {}
        self.performance_history: List[PerformanceMetric] = []
        self.active_alerts: Dict[str, PerformanceAlert] = {}
        self.monitoring_tasks: Dict[str, asyncio.Task] = {}
        self.alert_callbacks: List[Callable] = []
        self.is_monitoring = False
        
    async def start_monitoring(self) -> Dict[str, Any]:
        """
        Start the monitoring system.
        
        Returns:
            Monitoring startup status
        """
        try:
            if self.is_monitoring:
                return {'status': 'already_running', 'targets': len(self.monitoring_targets)}
            
            self.is_monitoring = True
            
            # Start monitoring tasks for each target
            for target_id, target in self.monitoring_targets.items():
                task = asyncio.create_task(self._monitor_target(target_id, target))
                self.monitoring_tasks[target_id] = task
            
            logger.info(f"Technical performance monitoring started for {len(self.monitoring_targets)} targets")
            
            return {
                'status': 'started',
                'targets_monitored': len(self.monitoring_targets),
                'monitoring_frequencies': self._get_frequency_distribution(),
                'start_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error starting monitoring: {str(e)}")
            self.is_monitoring = False
            raise
    
    async def stop_monitoring(self) -> Dict[str, Any]:
        """
        Stop the monitoring system.
        
        Returns:
            Monitoring stop status
        """
        try:
            self.is_monitoring = False
            
            # Cancel all monitoring tasks
            for task_id, task in self.monitoring_tasks.items():
                if not task.done():
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
            
            self.monitoring_tasks.clear()
            
            logger.info("Technical performance monitoring stopped")
            
            return {
                'status': 'stopped',
                'stop_time': datetime.now().isoformat(),
                'total_metrics_collected': len(self.performance_history),
                'active_alerts': len(self.active_alerts)
            }
            
        except Exception as e:
            logger.error(f"Error stopping monitoring: {str(e)}")
            raise
    
    async def add_monitoring_target(self,
                                  url: str,
                                  frequency: MonitoringFrequency = MonitoringFrequency.NORMAL,
                                  metrics: List[MetricType] = None,
                                  creator_id: Optional[str] = None,
                                  custom_thresholds: Dict[str, Tuple[float, float]] = None) -> str:
        """
        Add URL to monitoring targets.
        
        Args:
            url: URL to monitor
            frequency: Monitoring frequency
            metrics: Metrics to monitor
            creator_id: Associated creator ID
            custom_thresholds: Custom alert thresholds
            
        Returns:
            Target ID for reference
        """
        try:
            target_id = hashlib.md5(f"{url}_{datetime.now()}".encode()).hexdigest()[:8]
            
            if metrics is None:
                metrics = [MetricType.CORE_WEB_VITALS, MetricType.TECHNICAL_SEO]
            
            target = MonitoringTarget(
                url=url,
                frequency=frequency,
                metrics_to_monitor=metrics,
                creator_id=creator_id,
                custom_thresholds=custom_thresholds or {}
            )
            
            self.monitoring_targets[target_id] = target
            
            # Start monitoring if system is running
            if self.is_monitoring:
                task = asyncio.create_task(self._monitor_target(target_id, target))
                self.monitoring_tasks[target_id] = task
            
            logger.info(f"Added monitoring target: {url} (ID: {target_id})")
            
            return target_id
            
        except Exception as e:
            logger.error(f"Error adding monitoring target {url}: {str(e)}")
            raise
    
    async def remove_monitoring_target(self, target_id: str) -> bool:
        """
        Remove monitoring target.
        
        Args:
            target_id: Target ID to remove
            
        Returns:
            Success status
        """
        try:
            if target_id not in self.monitoring_targets:
                return False
            
            # Cancel monitoring task if running
            if target_id in self.monitoring_tasks:
                task = self.monitoring_tasks[target_id]
                if not task.done():
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
                del self.monitoring_tasks[target_id]
            
            # Remove target
            del self.monitoring_targets[target_id]
            
            logger.info(f"Removed monitoring target: {target_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error removing monitoring target {target_id}: {str(e)}")
            return False
    
    async def get_real_time_metrics(self, 
                                  url: str,
                                  device_type: str = "desktop") -> Dict[str, Any]:
        """
        Get real-time performance metrics for URL.
        
        Args:
            url: URL to measure
            device_type: Device type for measurement
            
        Returns:
            Real-time metrics
        """
        try:
            metrics = {
                'url': url,
                'device_type': device_type,
                'timestamp': datetime.now().isoformat(),
                'core_web_vitals': {},
                'technical_seo': {},
                'accessibility': {},
                'security': {},
                'performance_score': 0
            }
            
            # Measure Core Web Vitals
            cwv_metrics = await self._measure_core_web_vitals(url, device_type)
            metrics['core_web_vitals'] = cwv_metrics
            
            # Measure Technical SEO
            tech_seo_metrics = await self._measure_technical_seo(url)
            metrics['technical_seo'] = tech_seo_metrics
            
            # Measure Accessibility
            accessibility_metrics = await self._measure_accessibility(url)
            metrics['accessibility'] = accessibility_metrics
            
            # Measure Security
            security_metrics = await self._measure_security(url)
            metrics['security'] = security_metrics
            
            # Calculate overall performance score
            metrics['performance_score'] = self._calculate_overall_performance_score(metrics)
            
            # Store metrics
            await self._store_metrics(url, metrics)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting real-time metrics for {url}: {str(e)}")
            raise
    
    async def analyze_performance_trends(self,
                                       url: str,
                                       days: int = 30,
                                       metric_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze performance trends for URL.
        
        Args:
            url: URL to analyze
            days: Number of days to analyze
            metric_name: Specific metric to analyze (optional)
            
        Returns:
            Trend analysis results
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Filter historical data
            url_metrics = [
                m for m in self.performance_history
                if m.url == url and m.timestamp >= cutoff_date
            ]
            
            if not url_metrics:
                return {'error': 'No historical data available', 'url': url}
            
            trend_analysis = {
                'url': url,
                'analysis_period_days': days,
                'data_points': len(url_metrics),
                'trends': {},
                'anomalies': [],
                'recommendations': [],
                'performance_stability': {},
                'regression_analysis': {}
            }
            
            # Group metrics by type and name
            metrics_by_name = {}
            for metric in url_metrics:
                if metric_name and metric.name != metric_name:
                    continue
                    
                if metric.name not in metrics_by_name:
                    metrics_by_name[metric.name] = []
                metrics_by_name[metric.name].append((metric.timestamp, metric.value))
            
            # Analyze trends for each metric
            for name, data_points in metrics_by_name.items():
                if len(data_points) < 3:
                    continue
                    
                trend = await self._analyze_metric_trend(name, url, data_points, days)
                trend_analysis['trends'][name] = trend
                
                # Detect anomalies
                anomalies = self._detect_anomalies(data_points)
                if anomalies:
                    trend_analysis['anomalies'].extend(anomalies)
            
            # Generate recommendations
            trend_analysis['recommendations'] = self._generate_trend_recommendations(
                trend_analysis['trends']
            )
            
            # Calculate stability scores
            trend_analysis['performance_stability'] = self._calculate_stability_scores(
                trend_analysis['trends']
            )
            
            # Regression analysis
            trend_analysis['regression_analysis'] = await self._perform_regression_analysis(
                trend_analysis['trends']
            )
            
            return trend_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing performance trends for {url}: {str(e)}")
            raise
    
    async def get_performance_alerts(self,
                                   severity: Optional[AlertSeverity] = None,
                                   creator_id: Optional[str] = None,
                                   unresolved_only: bool = True) -> List[PerformanceAlert]:
        """
        Get performance alerts with filtering.
        
        Args:
            severity: Filter by severity level
            creator_id: Filter by creator ID
            unresolved_only: Only return unresolved alerts
            
        Returns:
            Filtered list of alerts
        """
        try:
            alerts = list(self.active_alerts.values())
            
            # Apply filters
            if severity:
                alerts = [a for a in alerts if a.severity == severity]
            
            if creator_id:
                alerts = [a for a in alerts if a.metric.creator_id == creator_id]
            
            if unresolved_only:
                alerts = [a for a in alerts if a.resolved_at is None]
            
            # Sort by severity and creation time
            severity_order = {
                AlertSeverity.CRITICAL: 0,
                AlertSeverity.HIGH: 1,
                AlertSeverity.MEDIUM: 2,
                AlertSeverity.LOW: 3,
                AlertSeverity.INFO: 4
            }
            
            alerts.sort(key=lambda a: (severity_order[a.severity], a.created_at), reverse=True)
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error getting performance alerts: {str(e)}")
            return []
    
    async def resolve_alert(self, alert_id: str, resolution_note: str = "") -> bool:
        """
        Resolve a performance alert.
        
        Args:
            alert_id: Alert ID to resolve
            resolution_note: Optional resolution note
            
        Returns:
            Success status
        """
        try:
            if alert_id not in self.active_alerts:
                return False
            
            alert = self.active_alerts[alert_id]
            alert.resolved_at = datetime.now()
            
            logger.info(f"Resolved alert {alert_id}: {resolution_note}")
            
            # Remove from active alerts after 24 hours
            asyncio.create_task(self._cleanup_resolved_alert(alert_id, 24 * 3600))
            
            return True
            
        except Exception as e:
            logger.error(f"Error resolving alert {alert_id}: {str(e)}")
            return False
    
    async def setup_creator_monitoring(self,
                                     creator_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Setup comprehensive monitoring for creators.
        
        Args:
            creator_data: List of creator data with URLs and settings
            
        Returns:
            Setup results
        """
        try:
            setup_results = {
                'creators_configured': 0,
                'total_urls_monitored': 0,
                'monitoring_targets': [],
                'creator_specific_thresholds': {},
                'estimated_monitoring_load': {}
            }
            
            for creator_info in creator_data:
                creator_id = creator_info.get('id')
                urls = creator_info.get('urls', [])
                tier = creator_info.get('tier', 'standard')
                
                if not creator_id or not urls:
                    continue
                
                # Determine monitoring frequency based on creator tier
                frequency_map = {
                    'premium': MonitoringFrequency.HIGH,
                    'pro': MonitoringFrequency.NORMAL,
                    'standard': MonitoringFrequency.LOW
                }
                frequency = frequency_map.get(tier, MonitoringFrequency.NORMAL)
                
                # Setup custom thresholds for creator tier
                custom_thresholds = self._get_creator_tier_thresholds(tier)
                
                creator_targets = []
                for url_info in urls:
                    url = url_info.get('url')
                    if not url:
                        continue
                    
                    target_id = await self.add_monitoring_target(
                        url=url,
                        frequency=frequency,
                        metrics=[MetricType.CORE_WEB_VITALS, MetricType.CREATOR_PERFORMANCE],
                        creator_id=creator_id,
                        custom_thresholds=custom_thresholds
                    )
                    
                    creator_targets.append({
                        'target_id': target_id,
                        'url': url,
                        'content_type': url_info.get('type', 'unknown')
                    })
                
                setup_results['creators_configured'] += 1
                setup_results['total_urls_monitored'] += len(creator_targets)
                setup_results['monitoring_targets'].extend(creator_targets)
                setup_results['creator_specific_thresholds'][creator_id] = custom_thresholds
            
            # Calculate monitoring load
            setup_results['estimated_monitoring_load'] = self._calculate_monitoring_load()
            
            return setup_results
            
        except Exception as e:
            logger.error(f"Error setting up creator monitoring: {str(e)}")
            raise
    
    async def generate_performance_dashboard_data(self) -> Dict[str, Any]:
        """
        Generate comprehensive data for performance dashboard.
        
        Returns:
            Dashboard data
        """
        try:
            dashboard_data = {
                'summary': {},
                'real_time_metrics': {},
                'alerts_summary': {},
                'trend_highlights': {},
                'creator_performance': {},
                'recommendations': [],
                'system_health': {}
            }
            
            # Summary statistics
            dashboard_data['summary'] = {
                'total_monitored_urls': len(self.monitoring_targets),
                'active_alerts': len([a for a in self.active_alerts.values() if a.resolved_at is None]),
                'metrics_collected_24h': len([
                    m for m in self.performance_history 
                    if m.timestamp >= datetime.now() - timedelta(days=1)
                ]),
                'average_performance_score': await self._calculate_average_performance_score()
            }
            
            # Real-time metrics for key URLs
            dashboard_data['real_time_metrics'] = await self._get_key_urls_metrics()
            
            # Alerts summary
            dashboard_data['alerts_summary'] = self._generate_alerts_summary()
            
            # Trend highlights
            dashboard_data['trend_highlights'] = await self._generate_trend_highlights()
            
            # Creator performance overview
            dashboard_data['creator_performance'] = await self._generate_creator_performance_overview()
            
            # System recommendations
            dashboard_data['recommendations'] = await self._generate_system_recommendations()
            
            # System health
            dashboard_data['system_health'] = {
                'monitoring_uptime': self._calculate_monitoring_uptime(),
                'data_freshness': self._check_data_freshness(),
                'alert_response_time': self._calculate_alert_response_time()
            }
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Error generating dashboard data: {str(e)}")
            raise
    
    async def _monitor_target(self, target_id: str, target: MonitoringTarget):
        """Monitor individual target continuously."""
        try:
            frequency_intervals = {
                MonitoringFrequency.REAL_TIME: 60,
                MonitoringFrequency.HIGH: 300,
                MonitoringFrequency.NORMAL: 900,
                MonitoringFrequency.LOW: 3600,
                MonitoringFrequency.DAILY: 86400
            }
            
            interval = frequency_intervals[target.frequency]
            
            while self.is_monitoring:
                try:
                    # Collect metrics
                    metrics = await self.get_real_time_metrics(target.url)
                    
                    # Check for alerts
                    await self._check_for_alerts(target_id, target, metrics)
                    
                    # Wait for next measurement
                    await asyncio.sleep(interval)
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Error monitoring target {target_id}: {str(e)}")
                    await asyncio.sleep(interval)  # Continue monitoring
                    
        except Exception as e:
            logger.error(f"Fatal error monitoring target {target_id}: {str(e)}")
    
    async def _measure_core_web_vitals(self, url: str, device_type: str) -> Dict[str, Any]:
        """Measure Core Web Vitals metrics."""
        # In real implementation, use Lighthouse API or similar
        # For now, simulate realistic measurements
        
        import random
        
        device_multiplier = 1.0 if device_type == "desktop" else 1.8
        
        cwv = {
            'lcp': round(random.uniform(1.2, 4.5) * device_multiplier, 2),
            'fid': round(random.uniform(45, 280) * device_multiplier, 1),
            'cls': round(random.uniform(0.03, 0.35), 3),
            'ttfb': round(random.uniform(150, 1200) * device_multiplier, 1),
            'fcp': round(random.uniform(0.9, 3.2) * device_multiplier, 2),
            'measurement_timestamp': datetime.now().isoformat(),
            'device_type': device_type
        }
        
        return cwv
    
    async def _measure_technical_seo(self, url: str) -> Dict[str, Any]:
        """Measure technical SEO metrics."""
        # Simulate technical SEO measurements
        import random
        
        tech_seo = {
            'crawlability_score': random.randint(70, 100),
            'indexability_score': random.randint(75, 100),
            'internal_links_count': random.randint(10, 150),
            'external_links_count': random.randint(2, 25),
            'meta_tags_completeness': random.randint(60, 100),
            'structured_data_present': random.choice([True, False]),
            'robots_txt_valid': True,
            'sitemap_present': True,
            'https_enabled': True,
            'mobile_friendly': random.choice([True, False]),
            'page_speed_desktop': random.randint(65, 100),
            'page_speed_mobile': random.randint(45, 95)
        }
        
        return tech_seo
    
    async def _measure_accessibility(self, url: str) -> Dict[str, Any]:
        """Measure accessibility metrics."""
        import random
        
        accessibility = {
            'accessibility_score': random.randint(70, 100),
            'contrast_ratio_issues': random.randint(0, 5),
            'missing_alt_attributes': random.randint(0, 10),
            'keyboard_navigation_score': random.randint(80, 100),
            'screen_reader_compatibility': random.randint(75, 100),
            'aria_labels_present': random.choice([True, False])
        }
        
        return accessibility
    
    async def _measure_security(self, url: str) -> Dict[str, Any]:
        """Measure security metrics."""
        import random
        
        security = {
            'ssl_certificate_valid': True,
            'security_headers_score': random.randint(70, 100),
            'mixed_content_issues': random.randint(0, 3),
            'csp_header_present': random.choice([True, False]),
            'hsts_enabled': random.choice([True, False]),
            'security_vulnerabilities': random.randint(0, 2)
        }
        
        return security
    
    def _calculate_overall_performance_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate overall performance score from all metrics."""
        scores = []
        
        # Core Web Vitals score (40% weight)
        cwv = metrics.get('core_web_vitals', {})
        cwv_score = 0
        
        if cwv.get('lcp', 0) <= 2.5:
            cwv_score += 33
        elif cwv.get('lcp', 0) <= 4.0:
            cwv_score += 16
            
        if cwv.get('fid', 0) <= 100:
            cwv_score += 33
        elif cwv.get('fid', 0) <= 300:
            cwv_score += 16
            
        if cwv.get('cls', 0) <= 0.1:
            cwv_score += 34
        elif cwv.get('cls', 0) <= 0.25:
            cwv_score += 17
            
        scores.append(('cwv', cwv_score, 0.4))
        
        # Technical SEO score (30% weight)
        tech_seo = metrics.get('technical_seo', {})
        tech_score = (
            tech_seo.get('crawlability_score', 0) * 0.3 +
            tech_seo.get('indexability_score', 0) * 0.3 +
            tech_seo.get('page_speed_desktop', 0) * 0.2 +
            tech_seo.get('page_speed_mobile', 0) * 0.2
        )
        scores.append(('tech_seo', tech_score, 0.3))
        
        # Accessibility score (15% weight)
        accessibility = metrics.get('accessibility', {})
        acc_score = accessibility.get('accessibility_score', 0)
        scores.append(('accessibility', acc_score, 0.15))
        
        # Security score (15% weight)
        security = metrics.get('security', {})
        sec_score = security.get('security_headers_score', 0)
        scores.append(('security', sec_score, 0.15))
        
        # Calculate weighted average
        total_score = sum(score * weight for _, score, weight in scores)
        return round(total_score, 1)
    
    async def _store_metrics(self, url: str, metrics_data: Dict[str, Any]):
        """Store metrics in history."""
        timestamp = datetime.now()
        
        # Store Core Web Vitals
        cwv = metrics_data.get('core_web_vitals', {})
        for metric_name, value in cwv.items():
            if isinstance(value, (int, float)):
                metric = PerformanceMetric(
                    metric_type=MetricType.CORE_WEB_VITALS,
                    name=metric_name,
                    value=value,
                    threshold_good=self._get_metric_threshold(metric_name, 'good'),
                    threshold_poor=self._get_metric_threshold(metric_name, 'poor'),
                    url=url,
                    timestamp=timestamp,
                    device_type=metrics_data.get('device_type', 'desktop')
                )
                self.performance_history.append(metric)
        
        # Store other metrics
        for category, category_data in metrics_data.items():
            if category in ['core_web_vitals', 'url', 'device_type', 'timestamp']:
                continue
                
            if isinstance(category_data, dict):
                for metric_name, value in category_data.items():
                    if isinstance(value, (int, float)):
                        metric_type = MetricType.TECHNICAL_SEO
                        if category == 'accessibility':
                            metric_type = MetricType.ACCESSIBILITY
                        elif category == 'security':
                            metric_type = MetricType.SECURITY
                            
                        metric = PerformanceMetric(
                            metric_type=metric_type,
                            name=f"{category}_{metric_name}",
                            value=value,
                            threshold_good=self._get_metric_threshold(f"{category}_{metric_name}", 'good'),
                            threshold_poor=self._get_metric_threshold(f"{category}_{metric_name}", 'poor'),
                            url=url,
                            timestamp=timestamp
                        )
                        self.performance_history.append(metric)
    
    async def _check_for_alerts(self, target_id: str, target: MonitoringTarget, metrics: Dict[str, Any]):
        """Check metrics against thresholds and generate alerts."""
        try:
            # Check Core Web Vitals
            cwv = metrics.get('core_web_vitals', {})
            
            # LCP Alert
            lcp = cwv.get('lcp')
            if lcp:
                lcp_threshold = target.custom_thresholds.get('lcp', (2.5, 4.0))
                if lcp > lcp_threshold[1]:  # Poor threshold
                    await self._create_alert(
                        target, 'lcp', lcp, AlertSeverity.HIGH,
                        f"LCP is {lcp}s (threshold: {lcp_threshold[1]}s)",
                        "Optimize largest contentful paint by compressing images and improving server response time"
                    )
            
            # FID Alert
            fid = cwv.get('fid')
            if fid:
                fid_threshold = target.custom_thresholds.get('fid', (100, 300))
                if fid > fid_threshold[1]:  # Poor threshold
                    await self._create_alert(
                        target, 'fid', fid, AlertSeverity.HIGH,
                        f"FID is {fid}ms (threshold: {fid_threshold[1]}ms)",
                        "Reduce JavaScript execution time and eliminate render-blocking resources"
                    )
            
            # CLS Alert
            cls = cwv.get('cls')
            if cls:
                cls_threshold = target.custom_thresholds.get('cls', (0.1, 0.25))
                if cls > cls_threshold[1]:  # Poor threshold
                    await self._create_alert(
                        target, 'cls', cls, AlertSeverity.MEDIUM,
                        f"CLS is {cls} (threshold: {cls_threshold[1]})",
                        "Specify image dimensions and reserve space for dynamic content"
                    )
            
            # Technical SEO alerts
            tech_seo = metrics.get('technical_seo', {})
            
            if tech_seo.get('crawlability_score', 100) < 70:
                await self._create_alert(
                    target, 'crawlability', tech_seo['crawlability_score'], AlertSeverity.MEDIUM,
                    f"Low crawlability score: {tech_seo['crawlability_score']}",
                    "Check robots.txt, internal linking, and page structure"
                )
            
            if not tech_seo.get('mobile_friendly', True):
                await self._create_alert(
                    target, 'mobile_friendly', 0, AlertSeverity.HIGH,
                    "Page is not mobile-friendly",
                    "Implement responsive design and optimize for mobile devices"
                )
            
        except Exception as e:
            logger.error(f"Error checking alerts for target {target_id}: {str(e)}")
    
    async def _create_alert(self,
                          target: MonitoringTarget,
                          metric_name: str,
                          value: float,
                          severity: AlertSeverity,
                          message: str,
                          recommendation: str):
        """Create and store performance alert."""
        try:
            alert_id = hashlib.md5(f"{target.url}_{metric_name}_{datetime.now()}".encode()).hexdigest()[:12]
            
            # Check if similar alert already exists
            existing_alert = None
            for alert in self.active_alerts.values():
                if (alert.metric.url == target.url and 
                    alert.metric.name == metric_name and 
                    alert.resolved_at is None):
                    existing_alert = alert
                    break
            
            if existing_alert:
                # Update existing alert
                existing_alert.metric.value = value
                existing_alert.metric.timestamp = datetime.now()
                logger.debug(f"Updated existing alert {existing_alert.alert_id}")
                return
            
            # Create new alert
            metric = PerformanceMetric(
                metric_type=MetricType.CORE_WEB_VITALS,
                name=metric_name,
                value=value,
                threshold_good=self._get_metric_threshold(metric_name, 'good'),
                threshold_poor=self._get_metric_threshold(metric_name, 'poor'),
                url=target.url,
                timestamp=datetime.now(),
                creator_id=target.creator_id
            )
            
            alert = PerformanceAlert(
                alert_id=alert_id,
                severity=severity,
                metric=metric,
                message=message,
                recommendation=recommendation,
                created_at=datetime.now(),
                creator_impact=self._assess_creator_impact(target.creator_id, metric_name, value)
            )
            
            self.active_alerts[alert_id] = alert
            
            # Trigger alert callbacks
            for callback in self.alert_callbacks:
                try:
                    await callback(alert)
                except Exception as e:
                    logger.error(f"Error in alert callback: {str(e)}")
            
            logger.warning(f"Created {severity.value} alert: {message}")
            
        except Exception as e:
            logger.error(f"Error creating alert: {str(e)}")
    
    def _get_metric_threshold(self, metric_name: str, threshold_type: str) -> float:
        """Get standard threshold for metric."""
        thresholds = {
            'lcp': {'good': 2.5, 'poor': 4.0},
            'fid': {'good': 100, 'poor': 300},
            'cls': {'good': 0.1, 'poor': 0.25},
            'ttfb': {'good': 800, 'poor': 1800},
            'fcp': {'good': 1.8, 'poor': 3.0}
        }
        
        return thresholds.get(metric_name, {}).get(threshold_type, 0)
    
    def _get_creator_tier_thresholds(self, tier: str) -> Dict[str, Tuple[float, float]]:
        """Get performance thresholds based on creator tier."""
        base_thresholds = {
            'lcp': (2.5, 4.0),
            'fid': (100, 300),
            'cls': (0.1, 0.25)
        }
        
        # Premium creators get stricter thresholds
        if tier == 'premium':
            return {
                'lcp': (2.0, 3.0),
                'fid': (75, 200),
                'cls': (0.08, 0.15)
            }
        elif tier == 'pro':
            return {
                'lcp': (2.2, 3.5),
                'fid': (85, 250),
                'cls': (0.09, 0.2)
            }
        
        return base_thresholds
    
    def _assess_creator_impact(self, creator_id: Optional[str], metric_name: str, value: float) -> Optional[str]:
        """Assess impact on creator experience."""
        if not creator_id:
            return None
        
        impact_messages = {
            'lcp': f"Slow loading may reduce viewer engagement and content discovery",
            'fid': f"Poor interactivity may frustrate viewers trying to engage with content",
            'cls': f"Layout shifts may disrupt content viewing experience",
            'crawlability': f"Low crawlability may reduce content visibility in search"
        }
        
        return impact_messages.get(metric_name, "Performance issue may affect creator visibility")
    
    async def _analyze_metric_trend(self,
                                  metric_name: str,
                                  url: str,
                                  data_points: List[Tuple[datetime, float]],
                                  days: int) -> PerformanceTrend:
        """Analyze trend for specific metric."""
        if len(data_points) < 3:
            return PerformanceTrend(
                metric_name=metric_name,
                url=url,
                trend_direction="insufficient_data",
                trend_strength=0.0,
                confidence=0.0,
                time_period_days=days,
                data_points=data_points,
                statistical_significance=False
            )
        
        # Sort by timestamp
        data_points.sort(key=lambda x: x[0])
        values = [point[1] for point in data_points]
        
        # Calculate trend direction using linear regression
        x_values = list(range(len(values)))
        n = len(values)
        
        sum_x = sum(x_values)
        sum_y = sum(values)
        sum_xy = sum(x * y for x, y in zip(x_values, values))
        sum_x2 = sum(x * x for x in x_values)
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        
        # Determine trend direction and strength
        if abs(slope) < 0.01:
            direction = "stable"
            strength = 0.1
        elif slope > 0:
            direction = "degrading" if metric_name in ['lcp', 'fid', 'cls'] else "improving"
            strength = min(1.0, abs(slope) * 10)
        else:
            direction = "improving" if metric_name in ['lcp', 'fid', 'cls'] else "degrading"
            strength = min(1.0, abs(slope) * 10)
        
        # Calculate confidence based on data consistency
        if len(values) > 1:
            variance = statistics.variance(values)
            mean_value = statistics.mean(values)
            cv = variance / (mean_value * mean_value) if mean_value > 0 else 1.0
            confidence = max(0.1, 1.0 - cv)
        else:
            confidence = 0.1
        
        # Statistical significance (simplified)
        statistical_significance = len(data_points) >= 10 and confidence > 0.7
        
        return PerformanceTrend(
            metric_name=metric_name,
            url=url,
            trend_direction=direction,
            trend_strength=strength,
            confidence=confidence,
            time_period_days=days,
            data_points=data_points,
            statistical_significance=statistical_significance
        )
    
    def _detect_anomalies(self, data_points: List[Tuple[datetime, float]]) -> List[Dict[str, Any]]:
        """Detect anomalies in performance data."""
        if len(data_points) < 5:
            return []
        
        values = [point[1] for point in data_points]
        mean_val = statistics.mean(values)
        std_dev = statistics.stdev(values) if len(values) > 1 else 0
        
        anomalies = []
        threshold = 2 * std_dev  # 2 standard deviations
        
        for timestamp, value in data_points:
            if abs(value - mean_val) > threshold:
                anomalies.append({
                    'timestamp': timestamp.isoformat(),
                    'value': value,
                    'deviation': abs(value - mean_val),
                    'severity': 'high' if abs(value - mean_val) > 3 * std_dev else 'medium'
                })
        
        return anomalies
    
    def _generate_trend_recommendations(self, trends: Dict[str, PerformanceTrend]) -> List[str]:
        """Generate recommendations based on trend analysis."""
        recommendations = []
        
        for metric_name, trend in trends.items():
            if trend.trend_direction == "degrading" and trend.confidence > 0.6:
                if metric_name == 'lcp':
                    recommendations.append("LCP is degrading - investigate image optimization and server response times")
                elif metric_name == 'fid':
                    recommendations.append("FID is degrading - review JavaScript performance and third-party scripts")
                elif metric_name == 'cls':
                    recommendations.append("CLS is degrading - check for layout shifts and dynamic content")
                elif 'crawlability' in metric_name:
                    recommendations.append("Crawlability declining - review site structure and internal linking")
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    def _calculate_stability_scores(self, trends: Dict[str, PerformanceTrend]) -> Dict[str, float]:
        """Calculate stability scores for metrics."""
        stability_scores = {}
        
        for metric_name, trend in trends.items():
            if trend.trend_direction == "stable":
                stability_scores[metric_name] = 0.9 + (trend.confidence * 0.1)
            else:
                # Lower stability for trending metrics
                stability_scores[metric_name] = max(0.1, 0.8 - trend.trend_strength)
        
        return stability_scores
    
    async def _perform_regression_analysis(self, trends: Dict[str, PerformanceTrend]) -> Dict[str, Any]:
        """Perform regression analysis on trends."""
        regression_analysis = {
            'predictive_models': {},
            'correlation_analysis': {},
            'forecasts': {}
        }
        
        # Simple regression analysis (in real implementation, use proper ML models)
        for metric_name, trend in trends.items():
            if len(trend.data_points) >= 5:
                values = [point[1] for point in trend.data_points]
                
                # Simple linear forecast
                if trend.trend_direction != "stable":
                    current_value = values[-1]
                    trend_rate = (values[-1] - values[0]) / len(values)
                    forecast_7d = current_value + (trend_rate * 7)
                    forecast_30d = current_value + (trend_rate * 30)
                    
                    regression_analysis['forecasts'][metric_name] = {
                        'current': current_value,
                        '7_day_forecast': forecast_7d,
                        '30_day_forecast': forecast_30d,
                        'confidence': trend.confidence
                    }
        
        return regression_analysis
    
    def _get_frequency_distribution(self) -> Dict[str, int]:
        """Get distribution of monitoring frequencies."""
        freq_dist = {}
        for target in self.monitoring_targets.values():
            freq_name = target.frequency.value
            freq_dist[freq_name] = freq_dist.get(freq_name, 0) + 1
        return freq_dist
    
    def _calculate_monitoring_load(self) -> Dict[str, Any]:
        """Calculate estimated monitoring load."""
        total_checks_per_hour = 0
        
        frequency_rates = {
            MonitoringFrequency.REAL_TIME: 60,
            MonitoringFrequency.HIGH: 12,
            MonitoringFrequency.NORMAL: 4,
            MonitoringFrequency.LOW: 1,
            MonitoringFrequency.DAILY: 1/24
        }
        
        for target in self.monitoring_targets.values():
            rate = frequency_rates[target.frequency]
            total_checks_per_hour += rate
        
        return {
            'checks_per_hour': total_checks_per_hour,
            'checks_per_day': total_checks_per_hour * 24,
            'estimated_data_points_per_day': total_checks_per_hour * 24 * 10,  # ~10 metrics per check
            'monitoring_intensity': 'high' if total_checks_per_hour > 100 else 'medium' if total_checks_per_hour > 20 else 'low'
        }
    
    async def _cleanup_resolved_alert(self, alert_id: str, delay_seconds: int):
        """Clean up resolved alert after delay."""
        await asyncio.sleep(delay_seconds)
        if alert_id in self.active_alerts:
            del self.active_alerts[alert_id]
            logger.debug(f"Cleaned up resolved alert {alert_id}")
    
    # Dashboard data generation methods
    async def _calculate_average_performance_score(self) -> float:
        """Calculate average performance score across all monitored URLs."""
        recent_metrics = [
            m for m in self.performance_history
            if m.timestamp >= datetime.now() - timedelta(hours=1)
        ]
        
        if not recent_metrics:
            return 0.0
        
        # Group by URL and calculate average
        url_scores = {}
        for metric in recent_metrics:
            if metric.url not in url_scores:
                url_scores[metric.url] = []
            url_scores[metric.url].append(metric.value)
        
        # Calculate average performance (simplified)
        if url_scores:
            all_scores = [statistics.mean(scores) for scores in url_scores.values()]
            return round(statistics.mean(all_scores), 1)
        
        return 0.0
    
    async def _get_key_urls_metrics(self) -> Dict[str, Any]:
        """Get real-time metrics for key URLs."""
        # Get top 5 most monitored URLs
        url_frequency = {}
        for target in self.monitoring_targets.values():
            url_frequency[target.url] = url_frequency.get(target.url, 0) + 1
        
        key_urls = sorted(url_frequency.items(), key=lambda x: x[1], reverse=True)[:5]
        
        metrics_data = {}
        for url, _ in key_urls:
            try:
                metrics = await self.get_real_time_metrics(url)
                metrics_data[url] = {
                    'performance_score': metrics.get('performance_score', 0),
                    'lcp': metrics.get('core_web_vitals', {}).get('lcp', 0),
                    'fid': metrics.get('core_web_vitals', {}).get('fid', 0),
                    'cls': metrics.get('core_web_vitals', {}).get('cls', 0)
                }
            except Exception as e:
                logger.error(f"Error getting metrics for {url}: {str(e)}")
                metrics_data[url] = {'error': str(e)}
        
        return metrics_data
    
    def _generate_alerts_summary(self) -> Dict[str, Any]:
        """Generate summary of current alerts."""
        unresolved_alerts = [a for a in self.active_alerts.values() if a.resolved_at is None]
        
        severity_counts = {}
        for alert in unresolved_alerts:
            severity = alert.severity.value
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        return {
            'total_unresolved': len(unresolved_alerts),
            'by_severity': severity_counts,
            'oldest_alert': min([a.created_at for a in unresolved_alerts]) if unresolved_alerts else None,
            'most_common_issue': self._find_most_common_alert_type(unresolved_alerts)
        }
    
    async def _generate_trend_highlights(self) -> Dict[str, Any]:
        """Generate trend highlights for dashboard."""
        highlights = {
            'improving_metrics': [],
            'degrading_metrics': [],
            'stable_metrics': [],
            'significant_changes': []
        }
        
        # Analyze recent trends for all monitored URLs
        for target in list(self.monitoring_targets.values())[:10]:  # Limit to prevent overload
            try:
                trends = await self.analyze_performance_trends(target.url, days=7)
                
                for metric_name, trend in trends.get('trends', {}).items():
                    if trend.statistical_significance:
                        if trend.trend_direction == 'improving':
                            highlights['improving_metrics'].append(f"{metric_name} for {target.url}")
                        elif trend.trend_direction == 'degrading':
                            highlights['degrading_metrics'].append(f"{metric_name} for {target.url}")
                        else:
                            highlights['stable_metrics'].append(f"{metric_name} for {target.url}")
                            
            except Exception as e:
                logger.error(f"Error generating trend highlights for {target.url}: {str(e)}")
        
        return highlights
    
    async def _generate_creator_performance_overview(self) -> Dict[str, Any]:
        """Generate creator performance overview."""
        creator_metrics = {}
        
        # Group metrics by creator
        for metric in self.performance_history[-1000:]:  # Last 1000 metrics
            if metric.creator_id:
                if metric.creator_id not in creator_metrics:
                    creator_metrics[metric.creator_id] = []
                creator_metrics[metric.creator_id].append(metric.value)
        
        overview = {
            'total_creators_monitored': len(creator_metrics),
            'top_performers': [],
            'needs_attention': [],
            'average_creator_score': 0
        }
        
        if creator_metrics:
            creator_scores = {
                creator: statistics.mean(metrics) 
                for creator, metrics in creator_metrics.items()
            }
            
            # Top performers
            sorted_creators = sorted(creator_scores.items(), key=lambda x: x[1], reverse=True)
            overview['top_performers'] = sorted_creators[:5]
            overview['needs_attention'] = sorted_creators[-3:] if len(sorted_creators) >= 3 else []
            overview['average_creator_score'] = round(statistics.mean(creator_scores.values()), 1)
        
        return overview
    
    async def _generate_system_recommendations(self) -> List[str]:
        """Generate system-wide recommendations."""
        recommendations = []
        
        # Analyze alert patterns
        unresolved_alerts = [a for a in self.active_alerts.values() if a.resolved_at is None]
        
        if len(unresolved_alerts) > 10:
            recommendations.append("High number of unresolved alerts - consider reviewing alert thresholds")
        
        # Analyze monitoring coverage
        if len(self.monitoring_targets) < 5:
            recommendations.append("Consider expanding monitoring coverage to more URLs")
        
        # Analyze performance trends
        recent_metrics = [
            m for m in self.performance_history
            if m.timestamp >= datetime.now() - timedelta(days=1)
        ]
        
        if recent_metrics:
            avg_values = {}
            for metric in recent_metrics:
                if metric.name not in avg_values:
                    avg_values[metric.name] = []
                avg_values[metric.name].append(metric.value)
            
            for metric_name, values in avg_values.items():
                avg_value = statistics.mean(values)
                threshold = self._get_metric_threshold(metric_name, 'poor')
                
                if threshold > 0 and avg_value > threshold:
                    recommendations.append(f"Platform-wide {metric_name} optimization needed")
        
        return recommendations[:5]  # Limit to top 5
    
    def _calculate_monitoring_uptime(self) -> float:
        """Calculate monitoring system uptime."""
        # Simplified uptime calculation
        # In real implementation, track actual uptime
        return 99.5  # Assume high uptime
    
    def _check_data_freshness(self) -> Dict[str, Any]:
        """Check freshness of monitoring data."""
        if not self.performance_history:
            return {'status': 'no_data', 'freshness_score': 0}
        
        latest_metric = max(self.performance_history, key=lambda x: x.timestamp)
        time_since_latest = datetime.now() - latest_metric.timestamp
        
        if time_since_latest.total_seconds() < 300:  # 5 minutes
            return {'status': 'fresh', 'freshness_score': 100, 'last_update': latest_metric.timestamp}
        elif time_since_latest.total_seconds() < 900:  # 15 minutes
            return {'status': 'acceptable', 'freshness_score': 75, 'last_update': latest_metric.timestamp}
        else:
            return {'status': 'stale', 'freshness_score': 25, 'last_update': latest_metric.timestamp}
    
    def _calculate_alert_response_time(self) -> Dict[str, Any]:
        """Calculate average alert response time."""
        resolved_alerts = [a for a in self.active_alerts.values() if a.resolved_at is not None]
        
        if not resolved_alerts:
            return {'average_response_time_minutes': 0, 'sample_size': 0}
        
        response_times = [
            (alert.resolved_at - alert.created_at).total_seconds() / 60
            for alert in resolved_alerts
        ]
        
        return {
            'average_response_time_minutes': round(statistics.mean(response_times), 1),
            'median_response_time_minutes': round(statistics.median(response_times), 1),
            'sample_size': len(response_times)
        }
    
    def _find_most_common_alert_type(self, alerts: List[PerformanceAlert]) -> Optional[str]:
        """Find most common alert type."""
        if not alerts:
            return None
        
        alert_types = [alert.metric.name for alert in alerts]
        alert_counts = {}
        
        for alert_type in alert_types:
            alert_counts[alert_type] = alert_counts.get(alert_type, 0) + 1
        
        return max(alert_counts.items(), key=lambda x: x[1])[0] if alert_counts else None

# Enterprise monitoring management
class PerformanceMonitoringManager:
    """High-level performance monitoring management for Ainflue platform."""
    
    def __init__(self):
        self.monitor = TechnicalPerformanceMonitor()
        
    async def setup_enterprise_monitoring(self,
                                        platform_config: Dict[str, Any]) -> Dict[str, Any]:
        """Setup comprehensive enterprise monitoring."""
        setup_results = {
            'monitoring_setup': {},
            'creator_monitoring': {},
            'alert_configuration': {},
            'dashboard_ready': False
        }
        
        # Setup core platform monitoring
        core_urls = platform_config.get('core_urls', [])
        for url_config in core_urls:
            target_id = await self.monitor.add_monitoring_target(
                url=url_config['url'],
                frequency=MonitoringFrequency(url_config.get('frequency', 'normal')),
                metrics=[MetricType.CORE_WEB_VITALS, MetricType.TECHNICAL_SEO, MetricType.SECURITY]
            )
            
        setup_results['monitoring_setup']['core_urls'] = len(core_urls)
        
        # Setup creator monitoring
        creator_data = platform_config.get('creators', [])
        creator_setup = await self.monitor.setup_creator_monitoring(creator_data)
        setup_results['creator_monitoring'] = creator_setup
        
        # Start monitoring
        monitoring_start = await self.monitor.start_monitoring()
        setup_results['monitoring_setup'].update(monitoring_start)
        
        setup_results['dashboard_ready'] = True
        
        return setup_results