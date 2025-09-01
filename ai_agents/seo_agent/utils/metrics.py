"""SEO Metrics Module - Advanced SEO Performance Tracking

Comprehensive metrics collection, analysis, and reporting system for SEO performance
monitoring, campaign tracking, and optimization effectiveness measurement.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  IMPORTANT LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import numpy as np
from collections import defaultdict, deque
import statistics

logger = logging.getLogger(__name__)

class MetricType(Enum):
    """
Types of SEO metrics"""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"
    RATE = "rate"

class MetricCategory(Enum):
    """Categories of SEO metrics"""

    CONTENT = "content"
    KEYWORDS = "keywords"
    TECHNICAL = "technical"
    PERFORMANCE = "performance"
    CAMPAIGNS = "campaigns"
    TRAFFIC = "traffic"
    RANKINGS = "rankings"
    CONVERSIONS = "conversions"

@dataclass
class MetricPoint:
    """Single metric data point"""
    timestamp: datetime
    value: float
    labels: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MetricSeries:
    """
Time series of metric points"""
    name: str
    metric_type: MetricType
    category: MetricCategory
    points: List[MetricPoint] = field(default_factory=list)
    description: str = ""
    unit: str = ""

class SEOMetricsCollector:
    """
    Advanced SEO metrics collection and analysis system.
    
    Features:
    - Real-time metrics collection
    - Time-series data storage
    - Statistical analysis and trends
    - Performance benchmarking
    - Alert threshold monitoring
    - Custom metric definitions
    - Data aggregation and rollups
    - Export and reporting
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # Metrics storage
        self.metrics: Dict[str, MetricSeries] = {}
        self.metric_buffers: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        
        # Aggregation settings
        self.aggregation_intervals = {
            '1m': timedelta(minutes=1),
            '5m': timedelta(minutes=5),
            '1h': timedelta(hours=1),
            '1d': timedelta(days=1),
            '1w': timedelta(weeks=1)
        }
        
        # Alert thresholds
        self.alert_thresholds = {
            'seo_score_drop': 0.1,  # 10% drop
            'page_load_time_increase': 1.0,  # 1 second increase
            'ranking_position_drop': 5,  # 5 position drop
            'traffic_drop': 0.2,  # 20% drop
            'conversion_rate_drop': 0.15  # 15% drop
        }
        
        # Performance tracking
        self.performance_baseline = {}
        self.trend_analysis_window = timedelta(days=30)
        
        # Data retention
        self.retention_periods = {
            'raw': timedelta(days=7),
            'hourly': timedelta(days=30),
            'daily': timedelta(days=365),
            'weekly': timedelta(days=730)
        }
        
    async def initialize(self):
        """
Initialize metrics collector"""
        try:
            # Initialize core SEO metrics
            await self._initialize_core_metrics()
            
            # Start background tasks
            asyncio.create_task(self._metrics_aggregation_loop())
            asyncio.create_task(self._alert_monitoring_loop())
            asyncio.create_task(self._data_cleanup_loop())
            
            logger.info("SEO Metrics Collector initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize SEO Metrics Collector: {e}")
            raise
    
    async def _initialize_core_metrics(self):
        """Initialize core SEO metrics"""
        
        core_metrics = [
            # Content Metrics
            MetricSeries(
                "content_seo_score", MetricType.GAUGE, MetricCategory.CONTENT,
                description="Overall SEO score for content", unit="score"
            ),
            MetricSeries(
                "content_word_count", MetricType.GAUGE, MetricCategory.CONTENT,
                description="Word count of content", unit="words"
            ),
            MetricSeries(
                "content_readability_score", MetricType.GAUGE, MetricCategory.CONTENT,
                description="Readability score of content", unit="score"
            ),
            
            # Keyword Metrics
            MetricSeries(
                "keyword_density", MetricType.GAUGE, MetricCategory.KEYWORDS,
                description="Keyword density percentage", unit="percent"
            ),
            MetricSeries(
                "keyword_ranking_position", MetricType.GAUGE, MetricCategory.RANKINGS,
                description="Keyword ranking position", unit="position"
            ),
            MetricSeries(
                "keyword_search_volume", MetricType.GAUGE, MetricCategory.KEYWORDS,
                description="Monthly search volume for keyword", unit="searches"
            ),
            
            # Technical Metrics
            MetricSeries(
                "page_load_time", MetricType.TIMER, MetricCategory.TECHNICAL,
                description="Page load time", unit="seconds"
            ),
            MetricSeries(
                "mobile_friendly_score", MetricType.GAUGE, MetricCategory.TECHNICAL,
                description="Mobile friendliness score", unit="score"
            ),
            MetricSeries(
                "core_web_vitals_lcp", MetricType.TIMER, MetricCategory.TECHNICAL,
                description="Largest Contentful Paint", unit="seconds"
            ),
            
            # Performance Metrics
            MetricSeries(
                "organic_traffic", MetricType.GAUGE, MetricCategory.TRAFFIC,
                description="Organic search traffic", unit="visitors"
            ),
            MetricSeries(
                "click_through_rate", MetricType.GAUGE, MetricCategory.PERFORMANCE,
                description="Search result click-through rate", unit="percent"
            ),
            MetricSeries(
                "bounce_rate", MetricType.GAUGE, MetricCategory.PERFORMANCE,
                description="Page bounce rate", unit="percent"
            ),
            
            # Campaign Metrics
            MetricSeries(
                "campaign_optimization_score", MetricType.GAUGE, MetricCategory.CAMPAIGNS,
                description="Campaign optimization effectiveness", unit="score"
            ),
            MetricSeries(
                "campaign_roi", MetricType.GAUGE, MetricCategory.CAMPAIGNS,
                description="Campaign return on investment", unit="ratio"
            ),
            
            # Conversion Metrics
            MetricSeries(
                "conversion_rate", MetricType.GAUGE, MetricCategory.CONVERSIONS,
                description="SEO traffic conversion rate", unit="percent"
            ),
            MetricSeries(
                "goal_completions", MetricType.COUNTER, MetricCategory.CONVERSIONS,
                description="Number of goal completions", unit="count"
            )
        ]
        
        for metric in core_metrics:
            self.metrics[metric.name] = metric
    
    def record_metric(
        self,
        metric_name: str,
        value: float,
        labels: Dict[str, str] = None,
        metadata: Dict[str, Any] = None,
        timestamp: Optional[datetime] = None
    ):
        """Record a single metric point"""
        try:
            if metric_name not in self.metrics:
                logger.warning(f"Unknown metric: {metric_name}")
                return
            
            point = MetricPoint(
                timestamp=timestamp or datetime.utcnow(),
                value=value,
                labels=labels or {},
                metadata=metadata or {}
            )
            
            # Add to metric series
            self.metrics[metric_name].points.append(point)
            
            # Add to buffer for real-time processing
            self.metric_buffers[metric_name].append(point)
            
        except Exception as e:
            logger.error(f"Error recording metric {metric_name}: {e}")
    
    def record_seo_analysis_metrics(self, analysis_results: Dict[str, Any]):
        """Record metrics from SEO analysis results"""
        try:
            content_id = analysis_results.get('content_id', 'unknown')
            labels = {'content_id': content_id}
            
            # Content metrics
            if 'seo_score' in analysis_results:
                self.record_metric(
                    'content_seo_score', 
                    analysis_results['seo_score'],
                    labels=labels
                )
            
            # Extract detailed metrics from analysis
            if 'content_analysis' in analysis_results:
                content_analysis = analysis_results['content_analysis']
                
                if 'word_count' in content_analysis:
                    self.record_metric(
                        'content_word_count',
                        content_analysis['word_count'],
                        labels=labels
                    )
                
                if 'content_quality_score' in content_analysis:
                    self.record_metric(
                        'content_readability_score',
                        content_analysis['content_quality_score'],
                        labels=labels
                    )
            
            # Keyword metrics
            if 'keyword_analysis' in analysis_results:
                keyword_analysis = analysis_results['keyword_analysis']
                
                if 'keyword_densities' in keyword_analysis:
                    for keyword, density in keyword_analysis['keyword_densities'].items():
                        keyword_labels = {**labels, 'keyword': keyword}
                        self.record_metric(
                            'keyword_density',
                            density,
                            labels=keyword_labels
                        )
            
            # Technical metrics
            if 'technical_analysis' in analysis_results:
                technical_analysis = analysis_results['technical_analysis']
                
                if 'page_speed' in technical_analysis:
                    self.record_metric(
                        'page_load_time',
                        technical_analysis['page_speed'],
                        labels=labels
                    )
                
                if 'mobile_friendly' in technical_analysis:
                    mobile_score = 1.0 if technical_analysis['mobile_friendly'] else 0.0
                    self.record_metric(
                        'mobile_friendly_score',
                        mobile_score,
                        labels=labels
                    )
            
        except Exception as e:
            logger.error(f"Error recording SEO analysis metrics: {e}")
    
    def record_campaign_metrics(self, campaign_data: Dict[str, Any]):
        """Record metrics from campaign execution"""
        try:
            campaign_id = campaign_data.get('campaign_id', 'unknown')
            labels = {'campaign_id': campaign_id}
            
            # Campaign optimization score
            if 'optimization_score' in campaign_data:
                self.record_metric(
                    'campaign_optimization_score',
                    campaign_data['optimization_score'],
                    labels=labels
                )
            
            # Campaign ROI
            if 'roi_analysis' in campaign_data:
                roi_data = campaign_data['roi_analysis']
                if 'roi' in roi_data:
                    self.record_metric(
                        'campaign_roi',
                        roi_data['roi'],
                        labels=labels
                    )
            
        except Exception as e:
            logger.error(f"Error recording campaign metrics: {e}")
    
    def record_ranking_metrics(self, ranking_data: Dict[str, Any]):
        """Record keyword ranking metrics"""
        try:
            for keyword, ranking_info in ranking_data.items():
                if isinstance(ranking_info, dict) and 'position' in ranking_info:
                    labels = {
                        'keyword': keyword,
                        'search_engine': ranking_info.get('search_engine', 'google'),
                        'location': ranking_info.get('location', 'US')
                    }
                    
                    self.record_metric(
                        'keyword_ranking_position',
                        ranking_info['position'],
                        labels=labels
                    )
                    
                    # Record search volume if available
                    if 'search_volume' in ranking_info:
                        self.record_metric(
                            'keyword_search_volume',
                            ranking_info['search_volume'],
                            labels=labels
                        )
            
        except Exception as e:
            logger.error(f"Error recording ranking metrics: {e}")
    
    def record_traffic_metrics(self, traffic_data: Dict[str, Any]):
        """Record traffic and performance metrics"""
        try:
            labels = {
                'source': traffic_data.get('source', 'organic'),
                'page': traffic_data.get('page', 'unknown')
            }
            
            # Organic traffic
            if 'organic_visitors' in traffic_data:
                self.record_metric(
                    'organic_traffic',
                    traffic_data['organic_visitors'],
                    labels=labels
                )
            
            # Click-through rate
            if 'ctr' in traffic_data:
                self.record_metric(
                    'click_through_rate',
                    traffic_data['ctr'] * 100,  # Convert to percentage
                    labels=labels
                )
            
            # Bounce rate
            if 'bounce_rate' in traffic_data:
                self.record_metric(
                    'bounce_rate',
                    traffic_data['bounce_rate'] * 100,  # Convert to percentage
                    labels=labels
                )
            
            # Conversion metrics
            if 'conversions' in traffic_data:
                self.record_metric(
                    'goal_completions',
                    traffic_data['conversions'],
                    labels=labels
                )
            
            if 'conversion_rate' in traffic_data:
                self.record_metric(
                    'conversion_rate',
                    traffic_data['conversion_rate'] * 100,  # Convert to percentage
                    labels=labels
                )
            
        except Exception as e:
            logger.error(f"Error recording traffic metrics: {e}")
    
    def get_metric_summary(self, metric_name: str, time_window: timedelta = None) -> Dict[str, Any]:
        """Get statistical summary of a metric"""
        try:
            if metric_name not in self.metrics:
                return {'error': f'Metric {metric_name} not found'}
            
            metric = self.metrics[metric_name]
            
            # Filter points by time window
            if time_window:
                cutoff_time = datetime.utcnow() - time_window
                points = [p for p in metric.points if p.timestamp >= cutoff_time]
            else:
                points = metric.points
            
            if not points:
                return {'error': 'No data points found'}
            
            values = [p.value for p in points]
            
            summary = {
                'metric_name': metric_name,
                'count': len(values),
                'min': min(values),
                'max': max(values),
                'mean': statistics.mean(values),
                'median': statistics.median(values),
                'std_dev': statistics.stdev(values) if len(values) > 1 else 0,
                'latest_value': values[-1],
                'latest_timestamp': points[-1].timestamp.isoformat(),
                'time_window': str(time_window) if time_window else 'all_time'
            }
            
            # Calculate trend
            if len(values) >= 2:
                trend = self._calculate_trend(values)
                summary['trend'] = trend
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting metric summary for {metric_name}: {e}")
            return {'error': str(e)}
    
    def get_performance_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive performance dashboard data"""
        try:
            dashboard = {
                'timestamp': datetime.utcnow().isoformat(),
                'overview': {},
                'content_metrics': {},
                'keyword_metrics': {},
                'technical_metrics': {},
                'traffic_metrics': {},
                'alerts': []
            }
            
            # Overview metrics
            dashboard['overview'] = {
                'total_content_analyzed': len(self.metric_buffers.get('content_seo_score', [])),
                'avg_seo_score': self._get_recent_average('content_seo_score'),
                'total_keywords_tracked': len(self.metric_buffers.get('keyword_ranking_position', [])),
                'avg_page_load_time': self._get_recent_average('page_load_time')
            }
            
            # Content metrics
            dashboard['content_metrics'] = {
                'seo_score': self.get_metric_summary('content_seo_score', timedelta(days=7)),
                'word_count': self.get_metric_summary('content_word_count', timedelta(days=7)),
                'readability': self.get_metric_summary('content_readability_score', timedelta(days=7))
            }
            
            # Keyword metrics
            dashboard['keyword_metrics'] = {
                'ranking_positions': self.get_metric_summary('keyword_ranking_position', timedelta(days=7)),
                'keyword_density': self.get_metric_summary('keyword_density', timedelta(days=7))
            }
            
            # Technical metrics
            dashboard['technical_metrics'] = {
                'page_load_time': self.get_metric_summary('page_load_time', timedelta(days=7)),
                'mobile_score': self.get_metric_summary('mobile_friendly_score', timedelta(days=7))
            }
            
            # Traffic metrics
            dashboard['traffic_metrics'] = {
                'organic_traffic': self.get_metric_summary('organic_traffic', timedelta(days=7)),
                'click_through_rate': self.get_metric_summary('click_through_rate', timedelta(days=7)),
                'conversion_rate': self.get_metric_summary('conversion_rate', timedelta(days=7))
            }
            
            # Check for alerts
            dashboard['alerts'] = self._check_alerts()
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Error generating performance dashboard: {e}")
            return {'error': str(e)}
    
    def _get_recent_average(self, metric_name: str, window_minutes: int = 60) -> float:
        """Get average value for metric in recent time window"""
        try:
            if metric_name not in self.metric_buffers:
                return 0.0
            
            cutoff_time = datetime.utcnow() - timedelta(minutes=window_minutes)
            recent_points = [
                p for p in self.metric_buffers[metric_name] 
                if p.timestamp >= cutoff_time
            ]
            
            if not recent_points:
                return 0.0
            
            return statistics.mean([p.value for p in recent_points])
            
        except Exception:
            return 0.0
    
    def _calculate_trend(self, values: List[float]) -> str:
        """
Calculate trend direction for values"""
        if len(values) < 2:
            return 'stable'
        
        # Simple linear trend calculation
        x = np.arange(len(values))
        slope = np.polyfit(x, values, 1)[0]
        
        if slope > 0.1:
            return 'increasing'
        elif slope < -0.1:
            return 'decreasing'
        else:
            return 'stable'
    
    def _check_alerts(self) -> List[Dict[str, Any]]:
        """
Check for metric-based alerts"""
        alerts = []
        
        try:
            # SEO score drop alert
            recent_seo_scores = [
                p.value for p in self.metric_buffers.get('content_seo_score', [])
                if p.timestamp >= datetime.utcnow() - timedelta(hours=24)
            ]
            
            if len(recent_seo_scores) >= 2:
                current_avg = statistics.mean(recent_seo_scores[-5:])  # Last 5 points
                previous_avg = statistics.mean(recent_seo_scores[-10:-5])  # Previous 5 points
                
                if current_avg < previous_avg * (1 - self.alert_thresholds['seo_score_drop']):
                    alerts.append({
                        'type': 'seo_score_drop',
                        'severity': 'warning',
                        'message': f'SEO score dropped by {((previous_avg - current_avg) / previous_avg * 100):.1f}%',
                        'current_value': current_avg,
                        'previous_value': previous_avg,
                        'timestamp': datetime.utcnow().isoformat()
                    })
            
            # Page load time increase alert
            recent_load_times = [
                p.value for p in self.metric_buffers.get('page_load_time', [])
                if p.timestamp >= datetime.utcnow() - timedelta(hours=24)
            ]
            
            if recent_load_times:
                avg_load_time = statistics.mean(recent_load_times)
                if avg_load_time > 3.0:  # More than 3 seconds
                    alerts.append({
                        'type': 'page_load_time_high',
                        'severity': 'warning',
                        'message': f'Average page load time is {avg_load_time:.2f}s (threshold: 3.0s)',
                        'current_value': avg_load_time,
                        'threshold': 3.0,
                        'timestamp': datetime.utcnow().isoformat()
                    })
            
        except Exception as e:
            logger.error(f"Error checking alerts: {e}")
        
        return alerts
    
    async def _metrics_aggregation_loop(self):
        """Background task for metrics aggregation"""
        while True:
            try:
                # Perform hourly aggregation
                await self._aggregate_metrics('1h')
                
                # Sleep for 1 hour
                await asyncio.sleep(3600)
                
            except Exception as e:
                logger.error(f"Metrics aggregation error: {e}")
                await asyncio.sleep(300)  # Retry after 5 minutes
    
    async def _alert_monitoring_loop(self):
        """Background task for alert monitoring"""
        while True:
            try:
                alerts = self._check_alerts()
                
                # Process alerts (send notifications, etc.)
                if alerts:
                    await self._process_alerts(alerts)
                
                # Check every 5 minutes
                await asyncio.sleep(300)
                
            except Exception as e:
                logger.error(f"Alert monitoring error: {e}")
                await asyncio.sleep(300)
    
    async def _data_cleanup_loop(self):
        """Background task for data cleanup based on retention policies"""
        while True:
            try:
                await self._cleanup_old_data()
                
                # Cleanup daily
                await asyncio.sleep(86400)
                
            except Exception as e:
                logger.error(f"Data cleanup error: {e}")
                await asyncio.sleep(3600)  # Retry after 1 hour
    
    async def _aggregate_metrics(self, interval: str):
        """Aggregate metrics for specified interval"""
        # Implementation would aggregate raw metrics into time buckets
        logger.debug(f"Aggregating metrics for interval: {interval}")
    
    async def _process_alerts(self, alerts: List[Dict[str, Any]]):
        """Process and send alerts"""
        for alert in alerts:
            logger.warning(f"SEO Alert: {alert['message']}")
            # Implementation would send notifications via email, Slack, etc.
    
    async def _cleanup_old_data(self):
        """Clean up old metric data based on retention policies"""
        current_time = datetime.utcnow()
        
        for metric_name, metric in self.metrics.items():
            # Remove old points based on retention policy
            retention_period = self.retention_periods.get('raw', timedelta(days=7))
            cutoff_time = current_time - retention_period
            
            original_count = len(metric.points)
            metric.points = [p for p in metric.points if p.timestamp >= cutoff_time]
            
            removed_count = original_count - len(metric.points)
            if removed_count > 0:
                logger.debug(f"Cleaned up {removed_count} old points for metric {metric_name}")

# Export main classes
__all__ = [
    'SEOMetricsCollector',
    'MetricType',
    'MetricCategory',
    'MetricPoint',
    'MetricSeries'
]
