"""
🌍 MONITORING DISTRIBUTION - Distribution Performance Analyzer
Advanced distribution performance analysis and optimization for Ainflue platform
Performance Engineer + DevOps Implementation

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
import json
import time
from concurrent.futures import ThreadPoolExecutor
import aiohttp
import psutil

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DistributionChannel(Enum):
    """Distribution channels for content delivery"""
    CDN_PRIMARY = "cdn_primary"
    CDN_SECONDARY = "cdn_secondary"
    EDGE_SERVERS = "edge_servers"
    ORIGIN_SERVERS = "origin_servers"
    PEER_TO_PEER = "peer_to_peer"
    MOBILE_OPTIMIZED = "mobile_optimized"
    STREAMING_SERVERS = "streaming_servers"
    CACHE_LAYERS = "cache_layers"

class PerformanceMetric(Enum):
    """Performance metrics to track"""
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    BANDWIDTH_UTILIZATION = "bandwidth_utilization"
    CACHE_HIT_RATE = "cache_hit_rate"
    ERROR_RATE = "error_rate"
    AVAILABILITY = "availability"
    TIME_TO_FIRST_BYTE = "time_to_first_byte"
    DOWNLOAD_SPEED = "download_speed"
    CONCURRENT_CONNECTIONS = "concurrent_connections"
    QUEUE_LENGTH = "queue_length"

class AnalysisType(Enum):
    """Types of performance analysis"""
    REAL_TIME = "real_time"
    HISTORICAL = "historical"
    PREDICTIVE = "predictive"
    COMPARATIVE = "comparative"
    ANOMALY_DETECTION = "anomaly_detection"
    CAPACITY_PLANNING = "capacity_planning"

class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

@dataclass
class PerformanceDataPoint:
    """Single performance measurement"""
    timestamp: datetime
    channel: DistributionChannel
    metric: PerformanceMetric
    value: float
    unit: str
    region: str
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PerformanceBaseline:
    """Performance baseline for comparison"""
    metric: PerformanceMetric
    channel: DistributionChannel
    baseline_value: float
    threshold_warning: float
    threshold_critical: float
    measurement_period: str
    confidence_level: float
    last_updated: datetime

@dataclass
class PerformanceAnomaly:
    """Detected performance anomaly"""
    anomaly_id: str
    metric: PerformanceMetric
    channel: DistributionChannel
    detected_at: datetime
    severity: AlertSeverity
    deviation_percentage: float
    expected_value: float
    actual_value: float
    duration_minutes: int
    affected_regions: List[str]
    root_cause_analysis: str
    recommended_actions: List[str] = field(default_factory=list)

@dataclass
class CapacityForecast:
    """Capacity planning forecast"""
    channel: DistributionChannel
    metric: PerformanceMetric
    forecast_period_days: int
    current_capacity: float
    predicted_demand: float
    capacity_utilization: float
    scaling_recommendation: str
    confidence_score: float
    risk_factors: List[str] = field(default_factory=list)

class DistributionPerformanceAnalyzer:
    """
    🌍 Advanced Distribution Performance Analyzer for Ainflue Platform
    
    Enterprise-grade performance analysis with:
    - Real-time performance monitoring across all distribution channels
    - Advanced anomaly detection with ML-powered insights
    - Predictive capacity planning and scaling recommendations
    - Cross-channel performance comparison and optimization
    - Geographic performance analysis and regional optimization
    - Automated performance baselining and threshold management
    - Integration with CDN providers and edge infrastructure
    - Performance-driven content routing optimization
    """
    
    def __init__(self, db_url: str = None, redis_url: str = None):
        """Initialize distribution performance analyzer"""
        self.db_url = db_url
        self.redis_url = redis_url
        
        # Data storage
        self.performance_data: Dict[str, List[PerformanceDataPoint]] = {}
        self.baselines: Dict[str, PerformanceBaseline] = {}
        self.anomalies: List[PerformanceAnomaly] = []
        self.forecasts: Dict[str, CapacityForecast] = {}
        
        # Analysis configuration
        self.data_retention_days = 30
        self.anomaly_detection_window = 60  # minutes
        self.baseline_update_interval = 24  # hours
        
        # Performance thresholds
        self.default_thresholds = {
            PerformanceMetric.LATENCY: {'warning': 500, 'critical': 2000},  # ms
            PerformanceMetric.THROUGHPUT: {'warning': 0.8, 'critical': 0.5},  # ratio of expected
            PerformanceMetric.ERROR_RATE: {'warning': 0.05, 'critical': 0.1},  # percentage
            PerformanceMetric.AVAILABILITY: {'warning': 0.95, 'critical': 0.90},  # percentage
            PerformanceMetric.CACHE_HIT_RATE: {'warning': 0.85, 'critical': 0.70}  # percentage
        }
        
        # Regional configuration
        self.monitored_regions = [
            'us-east-1', 'us-west-2', 'eu-west-1', 'eu-central-1',
            'ap-southeast-1', 'ap-northeast-1', 'ap-south-1'
        ]
        
        logger.info("🌍 Distribution Performance Analyzer initialized")

    async def collect_performance_metrics(
        self,
        start_time: datetime = None,
        end_time: datetime = None,
        channels: List[DistributionChannel] = None,
        regions: List[str] = None
    ) -> Dict[str, List[PerformanceDataPoint]]:
        """
        📊 Collect performance metrics from all distribution channels
        
        Gather comprehensive performance data for analysis
        """
        try:
            if end_time is None:
                end_time = datetime.now()
            if start_time is None:
                start_time = end_time - timedelta(hours=1)
            
            if channels is None:
                channels = list(DistributionChannel)
            
            if regions is None:
                regions = self.monitored_regions
            
            logger.info(f"📊 Collecting performance metrics: {start_time} to {end_time}")
            
            collected_data = {}
            
            # Collect metrics for each channel
            for channel in channels:
                channel_data = []
                
                # Collect metrics for each region
                for region in regions:
                    region_data = await self._collect_channel_region_metrics(
                        channel, region, start_time, end_time
                    )
                    channel_data.extend(region_data)
                
                if channel_data:
                    collected_data[channel.value] = channel_data
                    
                    # Store in memory for analysis
                    if channel.value not in self.performance_data:
                        self.performance_data[channel.value] = []
                    self.performance_data[channel.value].extend(channel_data)
                    
                    # Maintain data retention
                    cutoff_time = datetime.now() - timedelta(days=self.data_retention_days)
                    self.performance_data[channel.value] = [
                        dp for dp in self.performance_data[channel.value]
                        if dp.timestamp >= cutoff_time
                    ]
            
            total_data_points = sum(len(data) for data in collected_data.values())
            logger.info(f"✅ Collected {total_data_points} performance data points")
            
            return collected_data
            
        except Exception as e:
            logger.error(f"❌ Error collecting performance metrics: {e}")
            return {}

    async def _collect_channel_region_metrics(
        self,
        channel: DistributionChannel,
        region: str,
        start_time: datetime,
        end_time: datetime
    ) -> List[PerformanceDataPoint]:
        """Collect metrics for specific channel and region"""
        try:
            data_points = []
            
            # Simulate metric collection - would integrate with real monitoring systems
            current_time = start_time
            interval = timedelta(minutes=5)
            
            while current_time <= end_time:
                # Generate realistic performance data
                metrics_data = self._generate_realistic_metrics(channel, region, current_time)
                
                for metric, value_info in metrics_data.items():
                    data_point = PerformanceDataPoint(
                        timestamp=current_time,
                        channel=channel,
                        metric=metric,
                        value=value_info['value'],
                        unit=value_info['unit'],
                        region=region,
                        metadata={
                            'source': 'monitoring_agent',
                            'collection_method': 'automated'
                        }
                    )
                    data_points.append(data_point)
                
                current_time += interval
            
            return data_points
            
        except Exception as e:
            logger.error(f"Error collecting metrics for {channel} in {region}: {e}")
            return []

    def _generate_realistic_metrics(
        self,
        channel: DistributionChannel,
        region: str,
        timestamp: datetime
    ) -> Dict[PerformanceMetric, Dict[str, Any]]:
        """Generate realistic performance metrics for simulation"""
        # Base values with some variance
        base_latency = 50  # ms
        base_throughput = 1000  # Mbps
        base_cache_hit_rate = 0.85
        
        # Add regional variance
        regional_factors = {
            'us-east-1': 1.0,
            'us-west-2': 1.1,
            'eu-west-1': 1.3,
            'eu-central-1': 1.2,
            'ap-southeast-1': 1.8,
            'ap-northeast-1': 1.6,
            'ap-south-1': 2.0
        }
        
        regional_factor = regional_factors.get(region, 1.5)
        
        # Add time-based variance (higher load during peak hours)
        hour = timestamp.hour
        time_factor = 1.0
        if 8 <= hour <= 10 or 18 <= hour <= 22:  # Peak hours
            time_factor = 1.4
        elif 2 <= hour <= 6:  # Low usage
            time_factor = 0.7
        
        # Channel-specific adjustments
        channel_factors = {
            DistributionChannel.CDN_PRIMARY: {'latency': 0.8, 'throughput': 1.2},
            DistributionChannel.CDN_SECONDARY: {'latency': 1.1, 'throughput': 0.9},
            DistributionChannel.EDGE_SERVERS: {'latency': 0.6, 'throughput': 1.0},
            DistributionChannel.ORIGIN_SERVERS: {'latency': 1.5, 'throughput': 0.8},
            DistributionChannel.PEER_TO_PEER: {'latency': 2.0, 'throughput': 0.6}
        }
        
        channel_factor = channel_factors.get(channel, {'latency': 1.0, 'throughput': 1.0})
        
        # Generate metrics with realistic variance
        metrics = {
            PerformanceMetric.LATENCY: {
                'value': max(10, base_latency * regional_factor * time_factor * 
                           channel_factor['latency'] * np.random.normal(1.0, 0.2)),
                'unit': 'ms'
            },
            PerformanceMetric.THROUGHPUT: {
                'value': max(100, base_throughput * channel_factor['throughput'] * 
                           np.random.normal(1.0, 0.15)),
                'unit': 'Mbps'
            },
            PerformanceMetric.CACHE_HIT_RATE: {
                'value': min(1.0, max(0.5, base_cache_hit_rate * np.random.normal(1.0, 0.1))),
                'unit': 'ratio'
            },
            PerformanceMetric.ERROR_RATE: {
                'value': max(0, min(0.2, 0.02 * time_factor * np.random.exponential(1.0))),
                'unit': 'ratio'
            },
            PerformanceMetric.AVAILABILITY: {
                'value': min(1.0, max(0.8, 0.998 * np.random.normal(1.0, 0.005))),
                'unit': 'ratio'
            },
            PerformanceMetric.TIME_TO_FIRST_BYTE: {
                'value': max(5, base_latency * 0.3 * regional_factor * np.random.normal(1.0, 0.25)),
                'unit': 'ms'
            },
            PerformanceMetric.BANDWIDTH_UTILIZATION: {
                'value': min(1.0, max(0.1, 0.6 * time_factor * np.random.normal(1.0, 0.2))),
                'unit': 'ratio'
            }
        }
        
        return metrics

    async def analyze_performance_trends(
        self,
        channel: DistributionChannel,
        metric: PerformanceMetric,
        period_hours: int = 24
    ) -> Dict[str, Any]:
        """
        📈 Analyze performance trends for specific channel and metric
        
        Identify patterns and trends in performance data
        """
        try:
            logger.info(f"📈 Analyzing trends: {channel} - {metric} ({period_hours}h)")
            
            # Get data for analysis
            if channel.value not in self.performance_data:
                return {'error': f'No data available for {channel}'}
            
            cutoff_time = datetime.now() - timedelta(hours=period_hours)
            relevant_data = [
                dp for dp in self.performance_data[channel.value]
                if dp.metric == metric and dp.timestamp >= cutoff_time
            ]
            
            if len(relevant_data) < 10:
                return {'error': 'Insufficient data for trend analysis'}
            
            # Convert to time series
            df = pd.DataFrame([
                {
                    'timestamp': dp.timestamp,
                    'value': dp.value,
                    'region': dp.region
                }
                for dp in relevant_data
            ])
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.set_index('timestamp').sort_index()
            
            # Overall trend analysis
            trend_analysis = {
                'metric': metric.value,
                'channel': channel.value,
                'period_hours': period_hours,
                'data_points': len(relevant_data),
                'overall_trend': {},
                'regional_trends': {},
                'statistical_summary': {},
                'anomalies_detected': [],
                'recommendations': []
            }
            
            # Calculate overall statistics
            values = df['value'].values
            trend_analysis['statistical_summary'] = {
                'mean': float(np.mean(values)),
                'median': float(np.median(values)),
                'std': float(np.std(values)),
                'min': float(np.min(values)),
                'max': float(np.max(values)),
                'percentile_95': float(np.percentile(values, 95)),
                'percentile_99': float(np.percentile(values, 99))
            }
            
            # Trend direction analysis
            if len(values) > 1:
                # Simple linear trend
                x = np.arange(len(values))
                slope, intercept = np.polyfit(x, values, 1)
                
                trend_direction = 'stable'
                if abs(slope) > np.std(values) * 0.1:
                    trend_direction = 'increasing' if slope > 0 else 'decreasing'
                
                trend_analysis['overall_trend'] = {
                    'direction': trend_direction,
                    'slope': float(slope),
                    'correlation': float(np.corrcoef(x, values)[0, 1]),
                    'trend_strength': abs(float(np.corrcoef(x, values)[0, 1]))
                }
            
            # Regional trend analysis
            for region in df['region'].unique():
                region_data = df[df['region'] == region]['value'].values
                if len(region_data) > 5:
                    region_mean = float(np.mean(region_data))
                    region_trend = 'stable'
                    
                    if len(region_data) > 1:
                        x_region = np.arange(len(region_data))
                        slope_region, _ = np.polyfit(x_region, region_data, 1)
                        if abs(slope_region) > np.std(region_data) * 0.1:
                            region_trend = 'increasing' if slope_region > 0 else 'decreasing'
                    
                    trend_analysis['regional_trends'][region] = {
                        'mean_value': region_mean,
                        'trend_direction': region_trend,
                        'data_points': len(region_data),
                        'deviation_from_overall': region_mean - trend_analysis['statistical_summary']['mean']
                    }
            
            # Detect anomalies in the trend
            anomalies = self._detect_trend_anomalies(values, metric, channel)
            trend_analysis['anomalies_detected'] = anomalies
            
            # Generate recommendations
            recommendations = self._generate_trend_recommendations(trend_analysis, metric, channel)
            trend_analysis['recommendations'] = recommendations
            
            logger.info(f"✅ Trend analysis completed: {trend_analysis['overall_trend']['direction']} trend")
            return trend_analysis
            
        except Exception as e:
            logger.error(f"❌ Error analyzing performance trends: {e}")
            return {'error': str(e)}

    def _detect_trend_anomalies(
        self,
        values: np.ndarray,
        metric: PerformanceMetric,
        channel: DistributionChannel
    ) -> List[Dict[str, Any]]:
        """Detect anomalies in trend data"""
        anomalies = []
        
        try:
            if len(values) < 10:
                return anomalies
            
            # Statistical anomaly detection
            mean_val = np.mean(values)
            std_val = np.std(values)
            
            # Z-score based detection
            z_scores = np.abs((values - mean_val) / std_val)
            anomaly_threshold = 2.5
            
            anomaly_indices = np.where(z_scores > anomaly_threshold)[0]
            
            for idx in anomaly_indices:
                anomaly = {
                    'index': int(idx),
                    'value': float(values[idx]),
                    'z_score': float(z_scores[idx]),
                    'deviation_from_mean': float(values[idx] - mean_val),
                    'severity': 'high' if z_scores[idx] > 3.0 else 'medium'
                }
                anomalies.append(anomaly)
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Error detecting trend anomalies: {e}")
            return []

    def _generate_trend_recommendations(
        self,
        trend_analysis: Dict[str, Any],
        metric: PerformanceMetric,
        channel: DistributionChannel
    ) -> List[str]:
        """Generate recommendations based on trend analysis"""
        recommendations = []
        
        try:
            overall_trend = trend_analysis.get('overall_trend', {})
            stats = trend_analysis.get('statistical_summary', {})
            
            # Performance degradation
            if overall_trend.get('direction') == 'increasing' and metric in [
                PerformanceMetric.LATENCY, PerformanceMetric.ERROR_RATE
            ]:
                recommendations.append(f"Performance degradation detected in {metric.value} - investigate root cause")
            
            elif overall_trend.get('direction') == 'decreasing' and metric in [
                PerformanceMetric.THROUGHPUT, PerformanceMetric.CACHE_HIT_RATE, PerformanceMetric.AVAILABILITY
            ]:
                recommendations.append(f"Performance degradation detected in {metric.value} - optimize {channel.value}")
            
            # High variance
            if stats.get('std', 0) > stats.get('mean', 0) * 0.3:
                recommendations.append("High performance variance detected - stabilize the distribution pipeline")
            
            # Channel-specific recommendations
            if channel == DistributionChannel.CDN_PRIMARY:
                if metric == PerformanceMetric.CACHE_HIT_RATE and stats.get('mean', 0) < 0.8:
                    recommendations.append("CDN cache hit rate is low - review caching strategy")
            
            elif channel == DistributionChannel.EDGE_SERVERS:
                if metric == PerformanceMetric.LATENCY and stats.get('mean', 0) > 100:
                    recommendations.append("Edge server latency is high - consider geographic optimization")
            
            # Regional recommendations
            regional_trends = trend_analysis.get('regional_trends', {})
            poor_regions = [
                region for region, data in regional_trends.items()
                if abs(data.get('deviation_from_overall', 0)) > stats.get('std', 0)
            ]
            
            if poor_regions:
                recommendations.append(f"Performance issues in regions: {', '.join(poor_regions)}")
            
            # Anomaly recommendations
            anomalies = trend_analysis.get('anomalies_detected', [])
            if len(anomalies) > len(trend_analysis.get('data_points', 0)) * 0.05:  # >5% anomalies
                recommendations.append("High number of performance anomalies - implement automated alerting")
            
            if not recommendations:
                recommendations.append("Performance is within acceptable ranges")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return ["Unable to generate specific recommendations"]

    async def detect_performance_anomalies(
        self,
        window_minutes: int = None
    ) -> List[PerformanceAnomaly]:
        """
        🚨 Detect performance anomalies across all channels
        
        Real-time anomaly detection with severity classification
        """
        try:
            if window_minutes is None:
                window_minutes = self.anomaly_detection_window
            
            logger.info(f"🚨 Detecting performance anomalies ({window_minutes}min window)")
            
            cutoff_time = datetime.now() - timedelta(minutes=window_minutes)
            detected_anomalies = []
            
            # Analyze each channel
            for channel in DistributionChannel:
                if channel.value not in self.performance_data:
                    continue
                
                channel_data = self.performance_data[channel.value]
                recent_data = [dp for dp in channel_data if dp.timestamp >= cutoff_time]
                
                if len(recent_data) < 5:
                    continue
                
                # Analyze each metric
                for metric in PerformanceMetric:
                    metric_data = [dp for dp in recent_data if dp.metric == metric]
                    
                    if len(metric_data) < 3:
                        continue
                    
                    # Detect anomalies for this metric
                    metric_anomalies = await self._detect_metric_anomalies(
                        channel, metric, metric_data
                    )
                    detected_anomalies.extend(metric_anomalies)
            
            # Store detected anomalies
            self.anomalies.extend(detected_anomalies)
            
            # Clean up old anomalies
            cutoff_cleanup = datetime.now() - timedelta(hours=24)
            self.anomalies = [
                anomaly for anomaly in self.anomalies
                if anomaly.detected_at >= cutoff_cleanup
            ]
            
            logger.info(f"✅ Detected {len(detected_anomalies)} new performance anomalies")
            return detected_anomalies
            
        except Exception as e:
            logger.error(f"❌ Error detecting performance anomalies: {e}")
            return []

    async def _detect_metric_anomalies(
        self,
        channel: DistributionChannel,
        metric: PerformanceMetric,
        metric_data: List[PerformanceDataPoint]
    ) -> List[PerformanceAnomaly]:
        """Detect anomalies for specific metric"""
        anomalies = []
        
        try:
            if len(metric_data) < 3:
                return anomalies
            
            # Get baseline for comparison
            baseline_key = f"{channel.value}_{metric.value}"
            baseline = self.baselines.get(baseline_key)
            
            if not baseline:
                # Create baseline if not exists
                baseline = await self._create_baseline(channel, metric, metric_data)
                if baseline:
                    self.baselines[baseline_key] = baseline
                else:
                    return anomalies
            
            # Check latest values against baseline
            latest_data = sorted(metric_data, key=lambda x: x.timestamp)[-3:]  # Last 3 points
            
            for data_point in latest_data:
                deviation = abs(data_point.value - baseline.baseline_value) / baseline.baseline_value
                
                severity = AlertSeverity.INFO
                if data_point.value > baseline.threshold_critical:
                    severity = AlertSeverity.CRITICAL
                elif data_point.value > baseline.threshold_warning:
                    severity = AlertSeverity.WARNING
                
                # Only create anomaly if significant deviation
                if deviation > 0.2 or severity in [AlertSeverity.WARNING, AlertSeverity.CRITICAL]:
                    anomaly_id = f"anomaly_{channel.value}_{metric.value}_{int(data_point.timestamp.timestamp())}"
                    
                    # Analyze affected regions
                    affected_regions = [data_point.region]
                    
                    # Root cause analysis (simplified)
                    root_cause = self._analyze_root_cause(channel, metric, data_point, baseline)
                    
                    # Recommended actions
                    actions = self._generate_anomaly_actions(channel, metric, severity, data_point)
                    
                    anomaly = PerformanceAnomaly(
                        anomaly_id=anomaly_id,
                        metric=metric,
                        channel=channel,
                        detected_at=data_point.timestamp,
                        severity=severity,
                        deviation_percentage=deviation * 100,
                        expected_value=baseline.baseline_value,
                        actual_value=data_point.value,
                        duration_minutes=5,  # Simplified
                        affected_regions=affected_regions,
                        root_cause_analysis=root_cause,
                        recommended_actions=actions
                    )
                    
                    anomalies.append(anomaly)
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Error detecting metric anomalies: {e}")
            return []

    async def _create_baseline(
        self,
        channel: DistributionChannel,
        metric: PerformanceMetric,
        recent_data: List[PerformanceDataPoint]
    ) -> Optional[PerformanceBaseline]:
        """Create performance baseline from historical data"""
        try:
            if len(recent_data) < 10:
                return None
            
            values = [dp.value for dp in recent_data]
            mean_value = np.mean(values)
            std_value = np.std(values)
            
            # Set thresholds based on metric type
            if metric in self.default_thresholds:
                thresholds = self.default_thresholds[metric]
                warning_threshold = thresholds['warning']
                critical_threshold = thresholds['critical']
            else:
                # Dynamic thresholds based on data
                warning_threshold = mean_value + 2 * std_value
                critical_threshold = mean_value + 3 * std_value
            
            baseline = PerformanceBaseline(
                metric=metric,
                channel=channel,
                baseline_value=mean_value,
                threshold_warning=warning_threshold,
                threshold_critical=critical_threshold,
                measurement_period='24h',
                confidence_level=0.95,
                last_updated=datetime.now()
            )
            
            return baseline
            
        except Exception as e:
            logger.error(f"Error creating baseline: {e}")
            return None

    def _analyze_root_cause(
        self,
        channel: DistributionChannel,
        metric: PerformanceMetric,
        data_point: PerformanceDataPoint,
        baseline: PerformanceBaseline
    ) -> str:
        """Analyze potential root cause of anomaly"""
        try:
            # Simplified root cause analysis
            if metric == PerformanceMetric.LATENCY:
                if data_point.value > baseline.baseline_value * 2:
                    return "High latency may be due to network congestion or server overload"
                else:
                    return "Moderate latency increase detected"
            
            elif metric == PerformanceMetric.ERROR_RATE:
                if data_point.value > 0.1:
                    return "High error rate indicates potential service degradation"
                else:
                    return "Elevated error rate detected"
            
            elif metric == PerformanceMetric.CACHE_HIT_RATE:
                if data_point.value < 0.7:
                    return "Low cache hit rate may indicate cache invalidation or cold cache"
                else:
                    return "Cache performance below optimal"
            
            else:
                return f"Performance anomaly detected in {metric.value}"
                
        except Exception as e:
            logger.error(f"Error analyzing root cause: {e}")
            return "Unable to determine root cause"

    def _generate_anomaly_actions(
        self,
        channel: DistributionChannel,
        metric: PerformanceMetric,
        severity: AlertSeverity,
        data_point: PerformanceDataPoint
    ) -> List[str]:
        """Generate recommended actions for anomaly"""
        actions = []
        
        try:
            if severity == AlertSeverity.CRITICAL:
                actions.append("Immediate investigation required")
                actions.append("Consider failover to backup systems")
            
            if metric == PerformanceMetric.LATENCY:
                actions.extend([
                    "Check network connectivity and routing",
                    "Monitor server resource utilization",
                    "Consider content caching optimization"
                ])
            
            elif metric == PerformanceMetric.ERROR_RATE:
                actions.extend([
                    "Review application logs for error patterns",
                    "Check upstream service dependencies",
                    "Verify configuration changes"
                ])
            
            elif metric == PerformanceMetric.THROUGHPUT:
                actions.extend([
                    "Monitor bandwidth utilization",
                    "Check for traffic spikes",
                    "Consider scaling resources"
                ])
            
            # Channel-specific actions
            if channel == DistributionChannel.CDN_PRIMARY:
                actions.append("Check CDN provider status and configuration")
            elif channel == DistributionChannel.EDGE_SERVERS:
                actions.append("Monitor edge server health and capacity")
            
            if not actions:
                actions.append("Monitor performance closely")
            
            return actions
            
        except Exception as e:
            logger.error(f"Error generating anomaly actions: {e}")
            return ["Review performance metrics manually"]

    async def generate_capacity_forecast(
        self,
        channel: DistributionChannel,
        metric: PerformanceMetric,
        forecast_days: int = 30
    ) -> Optional[CapacityForecast]:
        """
        📊 Generate capacity planning forecast
        
        Predict future capacity needs based on trends
        """
        try:
            logger.info(f"📊 Generating capacity forecast: {channel} - {metric} ({forecast_days} days)")
            
            if channel.value not in self.performance_data:
                return None
            
            # Get historical data for forecasting
            cutoff_time = datetime.now() - timedelta(days=forecast_days * 2)  # Use 2x period for history
            historical_data = [
                dp for dp in self.performance_data[channel.value]
                if dp.metric == metric and dp.timestamp >= cutoff_time
            ]
            
            if len(historical_data) < 50:  # Need sufficient data
                return None
            
            # Prepare time series data
            df = pd.DataFrame([
                {'timestamp': dp.timestamp, 'value': dp.value}
                for dp in historical_data
            ])
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.set_index('timestamp').sort_index()
            
            # Resample to daily averages
            daily_data = df.resample('D')['value'].mean().dropna()
            
            if len(daily_data) < 7:
                return None
            
            # Simple trend-based forecasting
            values = daily_data.values
            x = np.arange(len(values))
            
            # Fit linear trend
            slope, intercept = np.polyfit(x, values, 1)
            
            # Project future values
            future_x = np.arange(len(values), len(values) + forecast_days)
            predicted_values = slope * future_x + intercept
            
            # Calculate current capacity and utilization
            current_capacity = self._get_current_capacity(channel, metric)
            current_value = values[-1]
            predicted_peak = np.max(predicted_values)
            
            capacity_utilization = predicted_peak / current_capacity if current_capacity > 0 else 0
            
            # Determine scaling recommendation
            if capacity_utilization > 0.9:
                scaling_recommendation = "Critical: Immediate capacity increase required"
            elif capacity_utilization > 0.8:
                scaling_recommendation = "Warning: Plan capacity increase within 2 weeks"
            elif capacity_utilization > 0.7:
                scaling_recommendation = "Monitor: Consider capacity planning"
            else:
                scaling_recommendation = "Sufficient: Current capacity adequate"
            
            # Calculate confidence score
            r_squared = np.corrcoef(x, values)[0, 1] ** 2
            confidence_score = min(0.95, max(0.1, r_squared))
            
            # Identify risk factors
            risk_factors = []
            if confidence_score < 0.7:
                risk_factors.append("Low prediction confidence due to irregular patterns")
            if slope > np.std(values) * 0.1:
                risk_factors.append("Rapid growth trend detected")
            if capacity_utilization > 0.8:
                risk_factors.append("High projected capacity utilization")
            
            forecast = CapacityForecast(
                channel=channel,
                metric=metric,
                forecast_period_days=forecast_days,
                current_capacity=current_capacity,
                predicted_demand=predicted_peak,
                capacity_utilization=capacity_utilization,
                scaling_recommendation=scaling_recommendation,
                confidence_score=confidence_score,
                risk_factors=risk_factors
            )
            
            # Store forecast
            forecast_key = f"{channel.value}_{metric.value}"
            self.forecasts[forecast_key] = forecast
            
            logger.info(f"✅ Capacity forecast generated: {capacity_utilization:.1%} utilization predicted")
            return forecast
            
        except Exception as e:
            logger.error(f"❌ Error generating capacity forecast: {e}")
            return None

    def _get_current_capacity(
        self,
        channel: DistributionChannel,
        metric: PerformanceMetric
    ) -> float:
        """Get current capacity limits for channel and metric"""
        # Simplified capacity limits - would be configurable in production
        capacity_limits = {
            (DistributionChannel.CDN_PRIMARY, PerformanceMetric.THROUGHPUT): 10000,  # Mbps
            (DistributionChannel.CDN_PRIMARY, PerformanceMetric.CONCURRENT_CONNECTIONS): 100000,
            (DistributionChannel.EDGE_SERVERS, PerformanceMetric.THROUGHPUT): 5000,
            (DistributionChannel.EDGE_SERVERS, PerformanceMetric.CONCURRENT_CONNECTIONS): 50000,
            (DistributionChannel.ORIGIN_SERVERS, PerformanceMetric.THROUGHPUT): 2000,
            (DistributionChannel.ORIGIN_SERVERS, PerformanceMetric.CONCURRENT_CONNECTIONS): 20000,
        }
        
        return capacity_limits.get((channel, metric), 1000)  # Default capacity

    async def compare_channel_performance(
        self,
        metrics: List[PerformanceMetric] = None,
        period_hours: int = 24
    ) -> Dict[str, Any]:
        """
        🔄 Compare performance across all distribution channels
        
        Cross-channel performance analysis and ranking
        """
        try:
            if metrics is None:
                metrics = [
                    PerformanceMetric.LATENCY,
                    PerformanceMetric.THROUGHPUT,
                    PerformanceMetric.AVAILABILITY,
                    PerformanceMetric.ERROR_RATE
                ]
            
            logger.info(f"🔄 Comparing channel performance ({period_hours}h)")
            
            cutoff_time = datetime.now() - timedelta(hours=period_hours)
            comparison = {
                'comparison_period_hours': period_hours,
                'metrics_analyzed': [m.value for m in metrics],
                'channel_rankings': {},
                'metric_comparisons': {},
                'performance_summary': {},
                'recommendations': []
            }
            
            # Analyze each metric across channels
            for metric in metrics:
                metric_data = {}
                
                for channel in DistributionChannel:
                    if channel.value not in self.performance_data:
                        continue
                    
                    channel_metric_data = [
                        dp for dp in self.performance_data[channel.value]
                        if dp.metric == metric and dp.timestamp >= cutoff_time
                    ]
                    
                    if channel_metric_data:
                        values = [dp.value for dp in channel_metric_data]
                        metric_data[channel.value] = {
                            'mean': np.mean(values),
                            'median': np.median(values),
                            'std': np.std(values),
                            'min': np.min(values),
                            'max': np.max(values),
                            'data_points': len(values)
                        }
                
                comparison['metric_comparisons'][metric.value] = metric_data
                
                # Rank channels for this metric
                if metric_data:
                    # For latency and error rate, lower is better
                    reverse_ranking = metric in [PerformanceMetric.LATENCY, PerformanceMetric.ERROR_RATE]
                    
                    ranked_channels = sorted(
                        metric_data.items(),
                        key=lambda x: x[1]['mean'],
                        reverse=not reverse_ranking
                    )
                    
                    comparison['channel_rankings'][metric.value] = [
                        {
                            'channel': channel,
                            'rank': idx + 1,
                            'mean_value': data['mean'],
                            'performance_score': self._calculate_performance_score(metric, data['mean'])
                        }
                        for idx, (channel, data) in enumerate(ranked_channels)
                    ]
            
            # Calculate overall performance summary
            channel_scores = {}
            for channel in DistributionChannel:
                if channel.value in self.performance_data:
                    scores = []
                    for metric in metrics:
                        rankings = comparison['channel_rankings'].get(metric.value, [])
                        channel_ranking = next(
                            (r for r in rankings if r['channel'] == channel.value),
                            None
                        )
                        if channel_ranking:
                            scores.append(channel_ranking['performance_score'])
                    
                    if scores:
                        channel_scores[channel.value] = {
                            'overall_score': np.mean(scores),
                            'metric_scores': dict(zip([m.value for m in metrics], scores))
                        }
            
            comparison['performance_summary'] = channel_scores
            
            # Generate recommendations
            if channel_scores:
                best_channel = max(channel_scores.items(), key=lambda x: x[1]['overall_score'])
                worst_channel = min(channel_scores.items(), key=lambda x: x[1]['overall_score'])
                
                comparison['recommendations'] = [
                    f"Best performing channel: {best_channel[0]} (score: {best_channel[1]['overall_score']:.2f})",
                    f"Channel needing improvement: {worst_channel[0]} (score: {worst_channel[1]['overall_score']:.2f})",
                    "Consider routing more traffic to top-performing channels",
                    "Investigate performance issues in underperforming channels"
                ]
            
            logger.info(f"✅ Channel performance comparison completed")
            return comparison
            
        except Exception as e:
            logger.error(f"❌ Error comparing channel performance: {e}")
            return {}

    def _calculate_performance_score(
        self,
        metric: PerformanceMetric,
        value: float
    ) -> float:
        """Calculate normalized performance score (0-1)"""
        try:
            # Define target values for each metric
            targets = {
                PerformanceMetric.LATENCY: {'target': 50, 'max_acceptable': 500},  # ms
                PerformanceMetric.THROUGHPUT: {'target': 1000, 'min_acceptable': 100},  # Mbps
                PerformanceMetric.AVAILABILITY: {'target': 0.999, 'min_acceptable': 0.95},  # ratio
                PerformanceMetric.ERROR_RATE: {'target': 0.001, 'max_acceptable': 0.05},  # ratio
                PerformanceMetric.CACHE_HIT_RATE: {'target': 0.95, 'min_acceptable': 0.70}  # ratio
            }
            
            if metric not in targets:
                return 0.5  # Default score
            
            target_config = targets[metric]
            
            # For metrics where lower is better (latency, error rate)
            if metric in [PerformanceMetric.LATENCY, PerformanceMetric.ERROR_RATE]:
                target = target_config['target']
                max_acceptable = target_config['max_acceptable']
                
                if value <= target:
                    return 1.0
                elif value >= max_acceptable:
                    return 0.0
                else:
                    return 1.0 - (value - target) / (max_acceptable - target)
            
            # For metrics where higher is better (throughput, availability, cache hit rate)
            else:
                target = target_config['target']
                min_acceptable = target_config['min_acceptable']
                
                if value >= target:
                    return 1.0
                elif value <= min_acceptable:
                    return 0.0
                else:
                    return (value - min_acceptable) / (target - min_acceptable)
            
        except Exception as e:
            logger.error(f"Error calculating performance score: {e}")
            return 0.5

    async def generate_performance_report(
        self,
        report_period_hours: int = 24
    ) -> Dict[str, Any]:
        """
        📊 Generate comprehensive performance report
        
        Complete analysis of distribution performance
        """
        try:
            logger.info(f"📊 Generating performance report ({report_period_hours}h)")
            
            cutoff_time = datetime.now() - timedelta(hours=report_period_hours)
            
            report = {
                'report_generated_at': datetime.now().isoformat(),
                'report_period_hours': report_period_hours,
                'executive_summary': {},
                'channel_performance': {},
                'anomaly_summary': {},
                'capacity_analysis': {},
                'regional_performance': {},
                'recommendations': [],
                'action_items': []
            }
            
            # Executive summary
            total_data_points = sum(
                len([dp for dp in data if dp.timestamp >= cutoff_time])
                for data in self.performance_data.values()
            )
            
            recent_anomalies = [
                anomaly for anomaly in self.anomalies
                if anomaly.detected_at >= cutoff_time
            ]
            
            critical_anomalies = [
                anomaly for anomaly in recent_anomalies
                if anomaly.severity == AlertSeverity.CRITICAL
            ]
            
            report['executive_summary'] = {
                'total_data_points_analyzed': total_data_points,
                'channels_monitored': len([ch for ch in DistributionChannel if ch.value in self.performance_data]),
                'regions_monitored': len(self.monitored_regions),
                'anomalies_detected': len(recent_anomalies),
                'critical_issues': len(critical_anomalies),
                'overall_health_status': 'good' if len(critical_anomalies) == 0 else 'needs_attention'
            }
            
            # Channel performance analysis
            channel_comparison = await self.compare_channel_performance(period_hours=report_period_hours)
            report['channel_performance'] = channel_comparison
            
            # Anomaly summary
            anomaly_by_channel = {}
            anomaly_by_metric = {}
            
            for anomaly in recent_anomalies:
                channel = anomaly.channel.value
                metric = anomaly.metric.value
                
                if channel not in anomaly_by_channel:
                    anomaly_by_channel[channel] = []
                anomaly_by_channel[channel].append(anomaly)
                
                if metric not in anomaly_by_metric:
                    anomaly_by_metric[metric] = []
                anomaly_by_metric[metric].append(anomaly)
            
            report['anomaly_summary'] = {
                'by_channel': {
                    channel: {
                        'count': len(anomalies),
                        'critical_count': len([a for a in anomalies if a.severity == AlertSeverity.CRITICAL]),
                        'most_recent': max(anomalies, key=lambda x: x.detected_at).detected_at.isoformat() if anomalies else None
                    }
                    for channel, anomalies in anomaly_by_channel.items()
                },
                'by_metric': {
                    metric: len(anomalies) for metric, anomalies in anomaly_by_metric.items()
                }
            }
            
            # Capacity analysis
            capacity_forecasts = {}
            for channel in DistributionChannel:
                for metric in [PerformanceMetric.THROUGHPUT, PerformanceMetric.CONCURRENT_CONNECTIONS]:
                    forecast = await self.generate_capacity_forecast(channel, metric, 30)
                    if forecast:
                        key = f"{channel.value}_{metric.value}"
                        capacity_forecasts[key] = {
                            'capacity_utilization': forecast.capacity_utilization,
                            'scaling_recommendation': forecast.scaling_recommendation,
                            'confidence_score': forecast.confidence_score
                        }
            
            report['capacity_analysis'] = capacity_forecasts
            
            # Generate recommendations
            recommendations = []
            
            if critical_anomalies:
                recommendations.append(f"Immediate attention required: {len(critical_anomalies)} critical performance issues")
            
            high_utilization_forecasts = [
                f for f in capacity_forecasts.values()
                if f['capacity_utilization'] > 0.8
            ]
            
            if high_utilization_forecasts:
                recommendations.append(f"Capacity planning needed: {len(high_utilization_forecasts)} channels approaching limits")
            
            # Add specific channel recommendations
            if 'performance_summary' in channel_comparison:
                scores = channel_comparison['performance_summary']
                if scores:
                    worst_channel = min(scores.items(), key=lambda x: x[1]['overall_score'])
                    if worst_channel[1]['overall_score'] < 0.7:
                        recommendations.append(f"Optimize {worst_channel[0]} channel performance (score: {worst_channel[1]['overall_score']:.2f})")
            
            if not recommendations:
                recommendations.append("All distribution channels performing within acceptable ranges")
            
            report['recommendations'] = recommendations
            
            # Action items
            action_items = []
            
            if critical_anomalies:
                action_items.extend([
                    "Investigate and resolve critical performance anomalies",
                    "Implement additional monitoring for affected channels"
                ])
            
            if high_utilization_forecasts:
                action_items.append("Review capacity scaling plans for high-utilization channels")
            
            if len(recent_anomalies) > 10:
                action_items.append("Review anomaly detection thresholds and alerting rules")
            
            if not action_items:
                action_items.append("Continue regular performance monitoring")
            
            report['action_items'] = action_items
            
            logger.info(f"✅ Performance report generated: {report['executive_summary']['overall_health_status']} status")
            return report
            
        except Exception as e:
            logger.error(f"❌ Error generating performance report: {e}")
            return {}

# Usage example
async def main():
    """Test the distribution performance analyzer"""
    try:
        # Initialize analyzer
        analyzer = DistributionPerformanceAnalyzer()
        
        # Collect performance metrics
        metrics = await analyzer.collect_performance_metrics()
        print(f"Collected metrics from {len(metrics)} channels")
        
        # Analyze trends
        trend_analysis = await analyzer.analyze_performance_trends(
            DistributionChannel.CDN_PRIMARY,
            PerformanceMetric.LATENCY
        )
        print(f"Trend analysis: {trend_analysis.get('overall_trend', {}).get('direction', 'unknown')} trend detected")
        
        # Detect anomalies
        anomalies = await analyzer.detect_performance_anomalies()
        print(f"Detected {len(anomalies)} performance anomalies")
        
        # Generate capacity forecast
        forecast = await analyzer.generate_capacity_forecast(
            DistributionChannel.CDN_PRIMARY,
            PerformanceMetric.THROUGHPUT
        )
        if forecast:
            print(f"Capacity forecast: {forecast.capacity_utilization:.1%} utilization predicted")
        
        # Compare channel performance
        comparison = await analyzer.compare_channel_performance()
        print(f"Channel comparison completed for {len(comparison.get('metric_comparisons', {}))} metrics")
        
        # Generate comprehensive report
        report = await analyzer.generate_performance_report()
        print(f"Report generated: {report.get('executive_summary', {}).get('overall_health_status', 'unknown')} health status")
        
    except Exception as e:
        print(f"Error in distribution performance analysis: {e}")

if __name__ == "__main__":
    asyncio.run(main())