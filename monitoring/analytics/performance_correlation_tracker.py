"""
🔍 MONITORING ANALYTICS - Performance Correlation Tracker
Enterprise performance correlation analysis for Ainflue platform
Backend Senior + DevOps Engineer Implementation

© 2025 Fahed Mlaiel - All Rights Reserved
Contact: mlaiel@live.de
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats import pearsonr, spearmanr, kendalltau
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import DBSCAN
import json
import redis
from sqlalchemy import create_engine, text
import asyncpg

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Types of performance metrics to track"""
    SYSTEM_PERFORMANCE = "system_performance"
    BUSINESS_METRICS = "business_metrics"
    USER_EXPERIENCE = "user_experience"
    CONTENT_METRICS = "content_metrics"
    REVENUE_METRICS = "revenue_metrics"
    ENGAGEMENT_METRICS = "engagement_metrics"
    TECHNICAL_METRICS = "technical_metrics"

class CorrelationType(Enum):
    """Types of correlation analysis"""
    PEARSON = "pearson"
    SPEARMAN = "spearman"
    KENDALL = "kendall"
    CROSS_CORRELATION = "cross_correlation"
    PARTIAL_CORRELATION = "partial_correlation"
    CANONICAL_CORRELATION = "canonical_correlation"

class AlertSeverity(Enum):
    """Correlation alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

@dataclass
class PerformanceMetric:
    """Individual performance metric data point"""
    metric_id: str
    metric_name: str
    metric_type: MetricType
    value: float
    timestamp: datetime
    dimensions: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CorrelationResult:
    """Correlation analysis result"""
    metric_1: str
    metric_2: str
    correlation_type: CorrelationType
    correlation_coefficient: float
    p_value: float
    is_significant: bool
    confidence_interval: Tuple[float, float]
    sample_size: int
    timeframe: str
    analysis_timestamp: datetime

@dataclass
class CorrelationAlert:
    """Correlation-based alert"""
    alert_id: str
    metric_pair: Tuple[str, str]
    correlation_change: float
    current_correlation: float
    previous_correlation: float
    severity: AlertSeverity
    message: str
    timestamp: datetime
    recommended_actions: List[str] = field(default_factory=list)

class PerformanceCorrelationTracker:
    """
    🔍 Advanced Performance Correlation Tracker for Ainflue Platform
    
    Enterprise-grade correlation analysis with:
    - Real-time metric correlation monitoring
    - Advanced statistical correlation methods
    - Cross-metric performance impact analysis
    - Predictive correlation alerting
    - Business metric to technical metric mapping
    - Performance bottleneck identification
    - Causal relationship discovery
    """
    
    def __init__(self, db_url -> None: str, redis_url -> None: str = None) -> None:
        """Initialize performance correlation tracker"""
        self.db_url = db_url
        self.redis_url = redis_url
        self.engine = create_engine(db_url)
        
        # Redis for caching
        if redis_url:
            self.redis_client = redis.from_url(redis_url)
        else:
            self.redis_client = None
        
        # Data storage
        self.metrics_data: Dict[str, List[PerformanceMetric]] = {}
        self.correlation_results: List[CorrelationResult] = []
        self.correlation_cache: Dict[str, CorrelationResult] = {}
        self.alerts: List[CorrelationAlert] = []
        
        # Analysis configuration
        self.correlation_threshold = 0.7
        self.significance_level = 0.05
        self.min_sample_size = 30
        self.correlation_history_days = 30
        
        # Metric relationships
        self.metric_relationships: Dict[str, Set[str]] = {}
        self.business_technical_mapping: Dict[str, List[str]] = {}
        
        logger.info("🔍 Performance Correlation Tracker initialized")

    async def collect_system_metrics(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> List[PerformanceMetric]:
        """
        ⚡ Collect system performance metrics
        
        Gather CPU, memory, network, disk metrics
        """
        try:
            logger.info(f"⚡ Collecting system metrics: {start_time} to {end_time}")
            
            # Query system metrics from monitoring database
            query = text("""
                SELECT 
                    metric_name,
                    metric_value,
                    timestamp,
                    host,
                    service,
                    tags
                FROM system_metrics 
                WHERE timestamp BETWEEN :start_time AND :end_time
                ORDER BY timestamp ASC
            """)
            
            result = self.engine.execute(query, {
                'start_time': start_time,
                'end_time': end_time
            })
            
            metrics = []
            for row in result:
                metric = PerformanceMetric(
                    metric_id=f"sys_{row.metric_name}_{row.timestamp}",
                    metric_name=row.metric_name,
                    metric_type=MetricType.SYSTEM_PERFORMANCE,
                    value=float(row.metric_value),
                    timestamp=row.timestamp,
                    dimensions={
                        'host': row.host,
                        'service': row.service
                    },
                    metadata={'tags': row.tags or {}}
                )
                metrics.append(metric)
            
            # Store in memory for correlation analysis
            for metric in metrics:
                if metric.metric_name not in self.metrics_data:
                    self.metrics_data[metric.metric_name] = []
                self.metrics_data[metric.metric_name].append(metric)
            
            logger.info(f"✅ Collected {len(metrics)} system metrics")
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Error collecting system metrics: {e}")
            return []

    async def collect_business_metrics(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> List[PerformanceMetric]:
        """
        💰 Collect business performance metrics
        
        Gather revenue, user engagement, content metrics
        """
        try:
            logger.info(f"💰 Collecting business metrics: {start_time} to {end_time}")
            
            # Revenue metrics
            revenue_query = text("""
                SELECT 
                    DATE_TRUNC('hour', created_at) as timestamp,
                    'revenue_per_hour' as metric_name,
                    SUM(amount) as metric_value,
                    COUNT(*) as transaction_count
                FROM transactions 
                WHERE created_at BETWEEN :start_time AND :end_time
                GROUP BY DATE_TRUNC('hour', created_at)
                ORDER BY timestamp ASC
            """)
            
            # User engagement metrics
            engagement_query = text("""
                SELECT 
                    DATE_TRUNC('hour', timestamp) as timestamp,
                    'avg_engagement_score' as metric_name,
                    AVG(engagement_score) as metric_value,
                    COUNT(*) as user_count
                FROM user_engagement 
                WHERE timestamp BETWEEN :start_time AND :end_time
                GROUP BY DATE_TRUNC('hour', timestamp)
                ORDER BY timestamp ASC
            """)
            
            # Content metrics
            content_query = text("""
                SELECT 
                    DATE_TRUNC('hour', created_at) as timestamp,
                    'content_uploads_per_hour' as metric_name,
                    COUNT(*) as metric_value
                FROM content 
                WHERE created_at BETWEEN :start_time AND :end_time
                GROUP BY DATE_TRUNC('hour', created_at)
                ORDER BY timestamp ASC
            """)
            
            metrics = []
            
            # Process revenue metrics
            revenue_result = self.engine.execute(revenue_query, {
                'start_time': start_time,
                'end_time': end_time
            })
            
            for row in revenue_result:
                metric = PerformanceMetric(
                    metric_id=f"biz_revenue_{row.timestamp}",
                    metric_name=row.metric_name,
                    metric_type=MetricType.BUSINESS_METRICS,
                    value=float(row.metric_value or 0),
                    timestamp=row.timestamp,
                    dimensions={'transaction_count': row.transaction_count}
                )
                metrics.append(metric)
            
            # Process engagement metrics
            engagement_result = self.engine.execute(engagement_query, {
                'start_time': start_time,
                'end_time': end_time
            })
            
            for row in engagement_result:
                metric = PerformanceMetric(
                    metric_id=f"biz_engagement_{row.timestamp}",
                    metric_name=row.metric_name,
                    metric_type=MetricType.BUSINESS_METRICS,
                    value=float(row.metric_value or 0),
                    timestamp=row.timestamp,
                    dimensions={'user_count': row.user_count}
                )
                metrics.append(metric)
            
            # Process content metrics
            content_result = self.engine.execute(content_query, {
                'start_time': start_time,
                'end_time': end_time
            })
            
            for row in content_result:
                metric = PerformanceMetric(
                    metric_id=f"biz_content_{row.timestamp}",
                    metric_name=row.metric_name,
                    metric_type=MetricType.BUSINESS_METRICS,
                    value=float(row.metric_value or 0),
                    timestamp=row.timestamp
                )
                metrics.append(metric)
            
            # Store metrics
            for metric in metrics:
                if metric.metric_name not in self.metrics_data:
                    self.metrics_data[metric.metric_name] = []
                self.metrics_data[metric.metric_name].append(metric)
            
            logger.info(f"✅ Collected {len(metrics)} business metrics")
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Error collecting business metrics: {e}")
            return []

    async def collect_technical_metrics(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> List[PerformanceMetric]:
        """
        🔧 Collect technical performance metrics
        
        API response times, error rates, throughput
        """
        try:
            logger.info(f"🔧 Collecting technical metrics: {start_time} to {end_time}")
            
            # API performance metrics
            api_query = text("""
                SELECT 
                    DATE_TRUNC('minute', timestamp) as timestamp,
                    endpoint,
                    AVG(response_time_ms) as avg_response_time,
                    COUNT(*) as request_count,
                    SUM(CASE WHEN status_code >= 400 THEN 1 ELSE 0 END) as error_count
                FROM api_requests 
                WHERE timestamp BETWEEN :start_time AND :end_time
                GROUP BY DATE_TRUNC('minute', timestamp), endpoint
                ORDER BY timestamp ASC
            """)
            
            # Database performance metrics
            db_query = text("""
                SELECT 
                    DATE_TRUNC('minute', timestamp) as timestamp,
                    'avg_query_duration' as metric_name,
                    AVG(duration_ms) as metric_value,
                    COUNT(*) as query_count
                FROM database_queries 
                WHERE timestamp BETWEEN :start_time AND :end_time
                GROUP BY DATE_TRUNC('minute', timestamp)
                ORDER BY timestamp ASC
            """)
            
            metrics = []
            
            # Process API metrics
            api_result = self.engine.execute(api_query, {
                'start_time': start_time,
                'end_time': end_time
            })
            
            for row in api_result:
                # Response time metric
                response_time_metric = PerformanceMetric(
                    metric_id=f"tech_response_time_{row.endpoint}_{row.timestamp}",
                    metric_name=f"response_time_{row.endpoint}",
                    metric_type=MetricType.TECHNICAL_METRICS,
                    value=float(row.avg_response_time or 0),
                    timestamp=row.timestamp,
                    dimensions={
                        'endpoint': row.endpoint,
                        'request_count': row.request_count
                    }
                )
                metrics.append(response_time_metric)
                
                # Error rate metric
                error_rate = (row.error_count / max(1, row.request_count)) * 100
                error_rate_metric = PerformanceMetric(
                    metric_id=f"tech_error_rate_{row.endpoint}_{row.timestamp}",
                    metric_name=f"error_rate_{row.endpoint}",
                    metric_type=MetricType.TECHNICAL_METRICS,
                    value=error_rate,
                    timestamp=row.timestamp,
                    dimensions={
                        'endpoint': row.endpoint,
                        'error_count': row.error_count,
                        'request_count': row.request_count
                    }
                )
                metrics.append(error_rate_metric)
            
            # Process database metrics
            db_result = self.engine.execute(db_query, {
                'start_time': start_time,
                'end_time': end_time
            })
            
            for row in db_result:
                metric = PerformanceMetric(
                    metric_id=f"tech_db_{row.timestamp}",
                    metric_name=row.metric_name,
                    metric_type=MetricType.TECHNICAL_METRICS,
                    value=float(row.metric_value or 0),
                    timestamp=row.timestamp,
                    dimensions={'query_count': row.query_count}
                )
                metrics.append(metric)
            
            # Store metrics
            for metric in metrics:
                if metric.metric_name not in self.metrics_data:
                    self.metrics_data[metric.metric_name] = []
                self.metrics_data[metric.metric_name].append(metric)
            
            logger.info(f"✅ Collected {len(metrics)} technical metrics")
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Error collecting technical metrics: {e}")
            return []

    async def calculate_pearson_correlation(
        self,
        metric_1: str,
        metric_2: str,
        timeframe_hours: int = 24
    ) -> Optional[CorrelationResult]:
        """
        📊 Calculate Pearson correlation between two metrics
        
        Linear correlation analysis
        """
        try:
            logger.info(f"📊 Calculating Pearson correlation: {metric_1} vs {metric_2}")
            
            # Get metric data
            data_1 = self._get_metric_time_series(metric_1, timeframe_hours)
            data_2 = self._get_metric_time_series(metric_2, timeframe_hours)
            
            if len(data_1) < self.min_sample_size or len(data_2) < self.min_sample_size:
                logger.warning(f"Insufficient data for correlation analysis")
                return None
            
            # Align time series
            aligned_data = self._align_time_series(data_1, data_2)
            if len(aligned_data) < self.min_sample_size:
                return None
            
            values_1 = [point[1] for point in aligned_data]
            values_2 = [point[2] for point in aligned_data]
            
            # Calculate Pearson correlation
            correlation_coef, p_value = pearsonr(values_1, values_2)
            
            # Calculate confidence interval
            n = len(values_1)
            fisher_z = np.arctanh(correlation_coef)
            se = 1 / np.sqrt(n - 3)
            ci_lower = np.tanh(fisher_z - 1.96 * se)
            ci_upper = np.tanh(fisher_z + 1.96 * se)
            
            result = CorrelationResult(
                metric_1=metric_1,
                metric_2=metric_2,
                correlation_type=CorrelationType.PEARSON,
                correlation_coefficient=correlation_coef,
                p_value=p_value,
                is_significant=p_value < self.significance_level,
                confidence_interval=(ci_lower, ci_upper),
                sample_size=n,
                timeframe=f"{timeframe_hours}h",
                analysis_timestamp=datetime.now()
            )
            
            # Cache result
            cache_key = f"pearson_{metric_1}_{metric_2}_{timeframe_hours}h"
            self.correlation_cache[cache_key] = result
            
            logger.info(f"✅ Pearson correlation: {correlation_coef:.3f} (p={p_value:.3f})")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error calculating Pearson correlation: {e}")
            return None

    async def calculate_spearman_correlation(
        self,
        metric_1: str,
        metric_2: str,
        timeframe_hours: int = 24
    ) -> Optional[CorrelationResult]:
        """
        📈 Calculate Spearman rank correlation
        
        Non-parametric correlation for monotonic relationships
        """
        try:
            logger.info(f"📈 Calculating Spearman correlation: {metric_1} vs {metric_2}")
            
            # Get metric data
            data_1 = self._get_metric_time_series(metric_1, timeframe_hours)
            data_2 = self._get_metric_time_series(metric_2, timeframe_hours)
            
            if len(data_1) < self.min_sample_size or len(data_2) < self.min_sample_size:
                return None
            
            # Align time series
            aligned_data = self._align_time_series(data_1, data_2)
            if len(aligned_data) < self.min_sample_size:
                return None
            
            values_1 = [point[1] for point in aligned_data]
            values_2 = [point[2] for point in aligned_data]
            
            # Calculate Spearman correlation
            correlation_coef, p_value = spearmanr(values_1, values_2)
            
            # Approximate confidence interval for Spearman
            n = len(values_1)
            se = 1 / np.sqrt(n - 3)
            ci_lower = max(-1, correlation_coef - 1.96 * se)
            ci_upper = min(1, correlation_coef + 1.96 * se)
            
            result = CorrelationResult(
                metric_1=metric_1,
                metric_2=metric_2,
                correlation_type=CorrelationType.SPEARMAN,
                correlation_coefficient=correlation_coef,
                p_value=p_value,
                is_significant=p_value < self.significance_level,
                confidence_interval=(ci_lower, ci_upper),
                sample_size=n,
                timeframe=f"{timeframe_hours}h",
                analysis_timestamp=datetime.now()
            )
            
            # Cache result
            cache_key = f"spearman_{metric_1}_{metric_2}_{timeframe_hours}h"
            self.correlation_cache[cache_key] = result
            
            logger.info(f"✅ Spearman correlation: {correlation_coef:.3f} (p={p_value:.3f})")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error calculating Spearman correlation: {e}")
            return None

    async def calculate_cross_correlation(
        self,
        metric_1: str,
        metric_2: str,
        max_lag_hours: int = 6
    ) -> Dict[str, Any]:
        """
        🔄 Calculate cross-correlation with time lags
        
        Identify lead-lag relationships between metrics
        """
        try:
            logger.info(f"🔄 Calculating cross-correlation: {metric_1} vs {metric_2}")
            
            # Get metric data
            data_1 = self._get_metric_time_series(metric_1, 48)  # Extended timeframe
            data_2 = self._get_metric_time_series(metric_2, 48)
            
            if len(data_1) < self.min_sample_size or len(data_2) < self.min_sample_size:
                return {}
            
            # Align and resample to regular intervals
            aligned_data = self._align_time_series(data_1, data_2)
            if len(aligned_data) < self.min_sample_size:
                return {}
            
            values_1 = np.array([point[1] for point in aligned_data])
            values_2 = np.array([point[2] for point in aligned_data])
            
            # Normalize values
            values_1 = (values_1 - np.mean(values_1)) / np.std(values_1)
            values_2 = (values_2 - np.mean(values_2)) / np.std(values_2)
            
            # Calculate cross-correlation for different lags
            correlations = {}
            max_lag_samples = min(max_lag_hours, len(values_1) // 4)
            
            for lag in range(-max_lag_samples, max_lag_samples + 1):
                if lag == 0:
                    corr = np.corrcoef(values_1, values_2)[0, 1]
                elif lag > 0:
                    # Metric 1 leads metric 2
                    if lag < len(values_1):
                        corr = np.corrcoef(values_1[:-lag], values_2[lag:])[0, 1]
                    else:
                        continue
                else:
                    # Metric 2 leads metric 1
                    lag_abs = abs(lag)
                    if lag_abs < len(values_2):
                        corr = np.corrcoef(values_1[lag_abs:], values_2[:-lag_abs])[0, 1]
                    else:
                        continue
                
                if not np.isnan(corr):
                    correlations[lag] = corr
            
            # Find best correlation and lag
            if correlations:
                best_lag = max(correlations.keys(), key=lambda k: abs(correlations[k]))
                best_correlation = correlations[best_lag]
                
                result = {
                    'metric_1': metric_1,
                    'metric_2': metric_2,
                    'correlations': correlations,
                    'best_lag': best_lag,
                    'best_correlation': best_correlation,
                    'analysis_timestamp': datetime.now().isoformat(),
                    'interpretation': self._interpret_cross_correlation(
                        metric_1, metric_2, best_lag, best_correlation
                    )
                }
                
                logger.info(f"✅ Best cross-correlation: {best_correlation:.3f} at lag {best_lag}")
                return result
            
            return {}
            
        except Exception as e:
            logger.error(f"❌ Error calculating cross-correlation: {e}")
            return {}

    async def detect_correlation_anomalies(
        self,
        lookback_days: int = 7
    ) -> List[CorrelationAlert]:
        """
        🚨 Detect anomalies in correlation patterns
        
        Alert on significant correlation changes
        """
        try:
            logger.info(f"🚨 Detecting correlation anomalies (lookback: {lookback_days} days)")
            
            alerts = []
            current_time = datetime.now()
            
            # Get list of metric pairs to monitor
            metric_pairs = self._get_monitored_metric_pairs()
            
            for metric_1, metric_2 in metric_pairs:
                try:
                    # Calculate current correlation
                    current_correlation = await self.calculate_pearson_correlation(
                        metric_1, metric_2, timeframe_hours=24
                    )
                    
                    if not current_correlation:
                        continue
                    
                    # Get historical correlation
                    historical_correlation = await self._get_historical_correlation(
                        metric_1, metric_2, lookback_days
                    )
                    
                    if historical_correlation is None:
                        continue
                    
                    # Calculate correlation change
                    correlation_change = abs(
                        current_correlation.correlation_coefficient - historical_correlation
                    )
                    
                    # Determine severity
                    severity = self._determine_correlation_alert_severity(
                        correlation_change, current_correlation.is_significant
                    )
                    
                    if severity != AlertSeverity.INFO:
                        alert = CorrelationAlert(
                            alert_id=f"corr_alert_{metric_1}_{metric_2}_{current_time.isoformat()}",
                            metric_pair=(metric_1, metric_2),
                            correlation_change=correlation_change,
                            current_correlation=current_correlation.correlation_coefficient,
                            previous_correlation=historical_correlation,
                            severity=severity,
                            message=self._generate_correlation_alert_message(
                                metric_1, metric_2, correlation_change, severity
                            ),
                            timestamp=current_time,
                            recommended_actions=self._generate_correlation_recommendations(
                                metric_1, metric_2, correlation_change, severity
                            )
                        )
                        alerts.append(alert)
                
                except Exception as e:
                    logger.error(f"Error processing correlation for {metric_1}-{metric_2}: {e}")
                    continue
            
            self.alerts.extend(alerts)
            
            logger.info(f"✅ Detected {len(alerts)} correlation anomalies")
            return alerts
            
        except Exception as e:
            logger.error(f"❌ Error detecting correlation anomalies: {e}")
            return []

    async def analyze_business_technical_correlations(self) -> Dict[str, Any]:
        """
        💼 Analyze correlations between business and technical metrics
        
        Map business impact to technical performance
        """
        try:
            logger.info("💼 Analyzing business-technical correlations")
            
            # Define business-technical metric mappings
            business_metrics = [
                'revenue_per_hour',
                'avg_engagement_score',
                'content_uploads_per_hour'
            ]
            
            technical_metrics = [
                'response_time_/api/upload',
                'response_time_/api/content',
                'avg_query_duration',
                'error_rate_/api/upload'
            ]
            
            correlations = {}
            significant_correlations = []
            
            # Calculate all combinations
            for business_metric in business_metrics:
                correlations[business_metric] = {}
                
                for technical_metric in technical_metrics:
                    # Calculate multiple correlation types
                    pearson_result = await self.calculate_pearson_correlation(
                        business_metric, technical_metric
                    )
                    spearman_result = await self.calculate_spearman_correlation(
                        business_metric, technical_metric
                    )
                    
                    correlations[business_metric][technical_metric] = {
                        'pearson': pearson_result,
                        'spearman': spearman_result
                    }
                    
                    # Check for significant correlations
                    if pearson_result and pearson_result.is_significant:
                        if abs(pearson_result.correlation_coefficient) > self.correlation_threshold:
                            significant_correlations.append({
                                'business_metric': business_metric,
                                'technical_metric': technical_metric,
                                'correlation_type': 'pearson',
                                'correlation': pearson_result.correlation_coefficient,
                                'p_value': pearson_result.p_value,
                                'impact_description': self._describe_business_technical_impact(
                                    business_metric, technical_metric, pearson_result.correlation_coefficient
                                )
                            })
            
            # Generate insights
            insights = self._generate_business_technical_insights(significant_correlations)
            
            result = {
                'analysis_timestamp': datetime.now().isoformat(),
                'correlations': correlations,
                'significant_correlations': significant_correlations,
                'insights': insights,
                'summary': {
                    'total_pairs_analyzed': len(business_metrics) * len(technical_metrics),
                    'significant_correlations_found': len(significant_correlations),
                    'strongest_correlation': max(
                        significant_correlations,
                        key=lambda x: abs(x['correlation']),
                        default=None
                    )
                }
            }
            
            logger.info(f"✅ Found {len(significant_correlations)} significant business-technical correlations")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error analyzing business-technical correlations: {e}")
            return {}

    async def generate_correlation_dashboard_data(self) -> Dict[str, Any]:
        """
        📊 Generate correlation dashboard data
        
        Prepare data for visualization and monitoring
        """
        try:
            logger.info("📊 Generating correlation dashboard data")
            
            dashboard_data = {
                'timestamp': datetime.now().isoformat(),
                'correlation_matrix': {},
                'time_series_correlations': {},
                'correlation_alerts': [],
                'top_correlations': [],
                'correlation_trends': {},
                'performance_impact_map': {}
            }
            
            # Get all available metrics
            all_metrics = list(self.metrics_data.keys())
            
            # Build correlation matrix
            correlation_matrix = {}
            for metric_1 in all_metrics[:10]:  # Limit for performance
                correlation_matrix[metric_1] = {}
                for metric_2 in all_metrics[:10]:
                    if metric_1 != metric_2:
                        correlation = await self.calculate_pearson_correlation(metric_1, metric_2)
                        if correlation:
                            correlation_matrix[metric_1][metric_2] = correlation.correlation_coefficient
                        else:
                            correlation_matrix[metric_1][metric_2] = 0.0
                    else:
                        correlation_matrix[metric_1][metric_2] = 1.0
            
            dashboard_data['correlation_matrix'] = correlation_matrix
            
            # Get recent alerts
            recent_alerts = [alert for alert in self.alerts 
                           if (datetime.now() - alert.timestamp).hours < 24]
            dashboard_data['correlation_alerts'] = [
                {
                    'metric_pair': alert.metric_pair,
                    'severity': alert.severity.value,
                    'message': alert.message,
                    'timestamp': alert.timestamp.isoformat(),
                    'correlation_change': alert.correlation_change
                }
                for alert in recent_alerts
            ]
            
            # Top correlations
            all_correlations = []
            for result in self.correlation_results:
                if result.is_significant:
                    all_correlations.append({
                        'metric_1': result.metric_1,
                        'metric_2': result.metric_2,
                        'correlation': result.correlation_coefficient,
                        'p_value': result.p_value,
                        'type': result.correlation_type.value
                    })
            
            # Sort by absolute correlation value
            all_correlations.sort(key=lambda x: abs(x['correlation']), reverse=True)
            dashboard_data['top_correlations'] = all_correlations[:10]
            
            # Performance impact mapping
            dashboard_data['performance_impact_map'] = await self._build_performance_impact_map()
            
            logger.info("✅ Correlation dashboard data generated")
            return dashboard_data
            
        except Exception as e:
            logger.error(f"❌ Error generating dashboard data: {e}")
            return {}

    # Helper methods
    
    def _get_metric_time_series(self, metric_name: str, timeframe_hours: int) -> List[Tuple[datetime, float]]:
        """Get time series data for a metric"""
        if metric_name not in self.metrics_data:
            return []
        
        cutoff_time = datetime.now() - timedelta(hours=timeframe_hours)
        relevant_metrics = [
            m for m in self.metrics_data[metric_name]
            if m.timestamp >= cutoff_time
        ]
        
        # Sort by timestamp and return as time series
        relevant_metrics.sort(key=lambda x: x.timestamp)
        return [(m.timestamp, m.value) for m in relevant_metrics]

    def _align_time_series(
        self,
        data_1: List[Tuple[datetime, float]],
        data_2: List[Tuple[datetime, float]]
    ) -> List[Tuple[datetime, float, float]]:
        """Align two time series by timestamp"""
        aligned = []
        
        # Create dictionaries for faster lookup
        dict_1 = {timestamp: value for timestamp, value in data_1}
        dict_2 = {timestamp: value for timestamp, value in data_2}
        
        # Find common timestamps
        common_timestamps = set(dict_1.keys()) & set(dict_2.keys())
        
        for timestamp in sorted(common_timestamps):
            aligned.append((timestamp, dict_1[timestamp], dict_2[timestamp]))
        
        return aligned

    def _get_monitored_metric_pairs(self) -> List[Tuple[str, str]]:
        """Get list of metric pairs to monitor for correlations"""
        pairs = []
        
        # Business-technical pairs
        business_metrics = ['revenue_per_hour', 'avg_engagement_score', 'content_uploads_per_hour']
        technical_metrics = ['response_time_/api/upload', 'avg_query_duration', 'error_rate_/api/upload']
        
        for business in business_metrics:
            for technical in technical_metrics:
                pairs.append((business, technical))
        
        # System metrics pairs
        system_metrics = [m for m in self.metrics_data.keys() if 'cpu' in m or 'memory' in m]
        for i, metric_1 in enumerate(system_metrics):
            for metric_2 in system_metrics[i+1:]:
                pairs.append((metric_1, metric_2))
        
        return pairs

    async def _get_historical_correlation(
        self,
        metric_1: str,
        metric_2: str,
        lookback_days: int
    ) -> Optional[float]:
        """Get historical correlation for comparison"""
        try:
            # Try to get from cache first
            cache_key = f"historical_{metric_1}_{metric_2}_{lookback_days}d"
            
            if self.redis_client:
                cached = self.redis_client.get(cache_key)
                if cached:
                    return float(cached)
            
            # Calculate historical correlation
            end_time = datetime.now() - timedelta(days=1)
            start_time = end_time - timedelta(days=lookback_days)
            
            # This would query historical data from database
            # For now, return a simulated historical correlation
            historical_correlation = 0.5  # Placeholder
            
            # Cache the result
            if self.redis_client:
                self.redis_client.setex(cache_key, 3600, str(historical_correlation))
            
            return historical_correlation
            
        except Exception as e:
            logger.error(f"Error getting historical correlation: {e}")
            return None

    def _determine_correlation_alert_severity(
        self,
        correlation_change: float,
        is_significant: bool
    ) -> AlertSeverity:
        """Determine alert severity based on correlation change"""
        if not is_significant:
            return AlertSeverity.INFO
        
        if correlation_change > 0.5:
            return AlertSeverity.CRITICAL
        elif correlation_change > 0.3:
            return AlertSeverity.WARNING
        elif correlation_change > 0.1:
            return AlertSeverity.INFO
        else:
            return AlertSeverity.INFO

    def _generate_correlation_alert_message(
        self,
        metric_1: str,
        metric_2: str,
        correlation_change: float,
        severity: AlertSeverity
    ) -> str:
        """Generate alert message for correlation change"""
        severity_prefix = {
            AlertSeverity.CRITICAL: "🚨 CRITICAL",
            AlertSeverity.WARNING: "⚠️ WARNING",
            AlertSeverity.INFO: "ℹ️ INFO"
        }
        
        return (f"{severity_prefix.get(severity, '📊')} Correlation change detected: "
                f"{metric_1} vs {metric_2} changed by {correlation_change:.3f}")

    def _generate_correlation_recommendations(
        self,
        metric_1: str,
        metric_2: str,
        correlation_change: float,
        severity: AlertSeverity
    ) -> List[str]:
        """Generate recommendations for correlation changes"""
        recommendations = []
        
        if severity == AlertSeverity.CRITICAL:
            recommendations.extend([
                f"Investigate immediate impact of {metric_1} on {metric_2}",
                "Check for system anomalies or configuration changes",
                "Review recent deployments or infrastructure changes"
            ])
        elif severity == AlertSeverity.WARNING:
            recommendations.extend([
                f"Monitor {metric_1} and {metric_2} trends closely",
                "Consider correlation trend analysis"
            ])
        
        recommendations.append("Update correlation thresholds if change is expected")
        return recommendations

    def _interpret_cross_correlation(
        self,
        metric_1: str,
        metric_2: str,
        best_lag: int,
        correlation: float
    ) -> str:
        """Interpret cross-correlation results"""
        if best_lag == 0:
            return f"{metric_1} and {metric_2} are contemporaneously correlated"
        elif best_lag > 0:
            return f"{metric_1} leads {metric_2} by {best_lag} time periods"
        else:
            return f"{metric_2} leads {metric_1} by {abs(best_lag)} time periods"

    def _describe_business_technical_impact(
        self,
        business_metric: str,
        technical_metric: str,
        correlation: float
    ) -> str:
        """Describe the impact between business and technical metrics"""
        correlation_strength = "strong" if abs(correlation) > 0.7 else "moderate"
        correlation_direction = "positive" if correlation > 0 else "negative"
        
        return (f"{correlation_strength.title()} {correlation_direction} correlation: "
                f"improvements in {technical_metric} are associated with "
                f"{'increases' if correlation > 0 else 'decreases'} in {business_metric}")

    def _generate_business_technical_insights(
        self,
        significant_correlations: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate insights from business-technical correlations"""
        insights = []
        
        if not significant_correlations:
            insights.append("No significant business-technical correlations found")
            return insights
        
        # Response time insights
        response_time_correlations = [
            c for c in significant_correlations
            if 'response_time' in c['technical_metric']
        ]
        
        if response_time_correlations:
            insights.append(
                f"API response times show significant correlation with business metrics. "
                f"Focus on performance optimization for maximum business impact."
            )
        
        # Error rate insights
        error_rate_correlations = [
            c for c in significant_correlations
            if 'error_rate' in c['technical_metric']
        ]
        
        if error_rate_correlations:
            insights.append(
                f"Error rates directly impact business performance. "
                f"Prioritize reliability improvements."
            )
        
        # Revenue insights
        revenue_correlations = [
            c for c in significant_correlations
            if 'revenue' in c['business_metric']
        ]
        
        if revenue_correlations:
            strongest_revenue_correlation = max(
                revenue_correlations,
                key=lambda x: abs(x['correlation'])
            )
            insights.append(
                f"Revenue is most strongly correlated with {strongest_revenue_correlation['technical_metric']}. "
                f"Optimize this metric for direct revenue impact."
            )
        
        return insights

    async def _build_performance_impact_map(self) -> Dict[str, Any]:
        """Build performance impact mapping"""
        impact_map = {
            'business_drivers': {},
            'technical_bottlenecks': {},
            'impact_chains': []
        }
        
        # Simplified impact mapping
        # In production, this would analyze complex correlation networks
        
        return impact_map

# Usage example
async def main() -> None:
    """Test the performance correlation tracker"""
    try:
        # Initialize tracker
        tracker = PerformanceCorrelationTracker("postgresql://user:pass@localhost/ainflue")
        
        # Collect metrics
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=24)
        
        await tracker.collect_system_metrics(start_time, end_time)
        await tracker.collect_business_metrics(start_time, end_time)
        await tracker.collect_technical_metrics(start_time, end_time)
        
        # Analyze correlations
        correlation = await tracker.calculate_pearson_correlation(
            'revenue_per_hour', 'response_time_/api/upload'
        )
        print(f"Revenue-Response Time Correlation: {correlation.correlation_coefficient if correlation else 'None'}")
        
        # Detect anomalies
        alerts = await tracker.detect_correlation_anomalies()
        print(f"Correlation alerts generated: {len(alerts)}")
        
        # Business-technical analysis
        business_analysis = await tracker.analyze_business_technical_correlations()
        print(f"Business-technical insights: {len(business_analysis.get('insights', []))}")
        
        # Generate dashboard data
        dashboard = await tracker.generate_correlation_dashboard_data()
        print(f"Dashboard data generated with {len(dashboard.get('top_correlations', []))} top correlations")
        
    except Exception as e:
        print(f"Error in correlation tracking: {e}")

if __name__ == "__main__":
    asyncio.run(main())