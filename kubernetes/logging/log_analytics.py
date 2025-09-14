"""IA Influencer Agent - Log Analytics Engine
Advanced log analytics and insights for monitoring

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited

WARNING: This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit 
written permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import statistics
import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest

from ...core.config import settings
from ...core.exceptions import LoggingError, AnalyticsError
from .elasticsearch_manager import ElasticsearchManager, QueryBuilder
from .log_aggregator import LogEntry, LogLevel


class AlertSeverity(str, Enum):
    """
Alert severity levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TrendDirection(str, Enum):
    """Trend direction indicators"""

    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"
    VOLATILE = "volatile"


@dataclass
class LogAlert:
    """Log-based alert definition"""
    id: str
    name: str
    description: str
    query: str
    threshold: float
    severity: AlertSeverity
    time_window_minutes: int
    enabled: bool = True
    created_at: Optional[datetime] = None
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """
Convert to dictionary"""
        data = asdict(self)
        if self.created_at:
            data['created_at'] = self.created_at.isoformat()
        if self.last_triggered:
            data['last_triggered'] = self.last_triggered.isoformat()
        return data


@dataclass
class LogMetric:
    """
Log metric definition"""
    name: str
    description: str
    query: str
    aggregation: str  # count, avg, sum, min, max
    field: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None
    time_window_minutes: int = 60
    
    def to_dict(self) -> Dict[str, Any]:
        """
Convert to dictionary"""
        return asdict(self)


@dataclass
class AnalyticsResult:
    """
Analytics computation result"""
    metric_name: str
    value: Union[float, int, str]
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """
Convert to dictionary"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


class AnomalyDetector:
    """
Machine learning-based anomaly detection for logs"""
    
    def __init__(self) -> None:
        self.isolation_forest = IsolationForest(
            contamination=0.1,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.is_trained = False
    
    def prepare_features(self, log_data: List[Dict[str, Any]]) -> np.ndarray:
        """
Prepare features for anomaly detection"""
        features = []
        
        for log_entry in log_data:
            feature_vector = [
                # Temporal features
                log_entry.get('hour', 0),
                log_entry.get('day_of_week', 0),
                
                # Log level encoding
                {'DEBUG': 0, 'INFO': 1, 'WARNING': 2, 'ERROR': 3, 'CRITICAL': 4}.get(
                    log_entry.get('level', 'INFO'), 1
                ),
                
                # Message length
                len(log_entry.get('message', '')),
                
                # Processing time if available
                log_entry.get('metadata', {}).get('processing_time_ms', 0),
                
                # Service hash (simple encoding)
                hash(log_entry.get('service', '')) % 1000,
                
                # User activity indicator
                1 if log_entry.get('user_id') else 0,
            ]
            
            features.append(feature_vector)
        
        return np.array(features)
    
    async def train(self, training_data -> None: List[Dict[str, Any]]) -> None:
        """
Train anomaly detection model"""
        if len(training_data) < 100:
            raise AnalyticsError("Insufficient training data (minimum 100 samples)")
        
        features = self.prepare_features(training_data)
        scaled_features = self.scaler.fit_transform(features)
        
        self.isolation_forest.fit(scaled_features)
        self.is_trained = True
        
        logging.info(f"Trained anomaly detector on {len(training_data)} samples")
    
    async def detect_anomalies(self, log_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect anomalies in log data"""
        if not self.is_trained:
            raise AnalyticsError("Anomaly detector not trained")
        
        if not log_data:
            return []
        
        features = self.prepare_features(log_data)
        scaled_features = self.scaler.transform(features)
        
        # Predict anomalies (-1 = anomaly, 1 = normal)
        predictions = self.isolation_forest.predict(scaled_features)
        scores = self.isolation_forest.score_samples(scaled_features)
        
        anomalies = []
        for i, (prediction, score) in enumerate(zip(predictions, scores)):
            if prediction == -1:
                log_entry = log_data[i].copy()
                log_entry['anomaly_score'] = float(score)
                log_entry['anomaly_detected_at'] = datetime.now(timezone.utc).isoformat()
                anomalies.append(log_entry)
        
        return anomalies


class LogPatternAnalyzer:
    """Analyze log patterns and extract insights"""
    
    def __init__(self) -> None:
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
    async def analyze_error_patterns(self, error_logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
Analyze patterns in error logs"""
        if not error_logs:
            return {"patterns": [], "summary": "No error logs to analyze"}
        
        # Group errors by similarity
        error_groups = {}
        for error_log in error_logs:
            error_type = error_log.get('metadata', {}).get('error_code', 'unknown')
            service = error_log.get('service', 'unknown')
            key = f"{service}:{error_type}"
            
            if key not in error_groups:
                error_groups[key] = {
                    'count': 0,
                    'first_seen': error_log.get('timestamp'),
                    'last_seen': error_log.get('timestamp'),
                    'services': set(),
                    'users_affected': set(),
                    'sample_messages': []
                }
            
            group = error_groups[key]
            group['count'] += 1
            group['services'].add(service)
            
            if error_log.get('user_id'):
                group['users_affected'].add(error_log['user_id'])
            
            if len(group['sample_messages']) < 5:
                group['sample_messages'].append(error_log.get('message', ''))
        
        # Convert sets to lists for JSON serialization
        patterns = []
        for key, group in error_groups.items():
            pattern = {
                'pattern_id': key,
                'count': group['count'],
                'first_seen': group['first_seen'],
                'last_seen': group['last_seen'],
                'services': list(group['services']),
                'users_affected_count': len(group['users_affected']),
                'sample_messages': group['sample_messages']
            }
            patterns.append(pattern)
        
        # Sort by frequency
        patterns.sort(key=lambda x: x['count'], reverse=True)
        try:
                    # AI model processing
                    if not hasattr(self, 'model') or self.model is None:
                        raise RuntimeError("AI model not initialized")
            
                    # Preprocess input
                    processed_input = await self._preprocess_analyze_user_activity_patterns_input(user_logs)
            
                    # Run inference
                    result = await self.model.predict(processed_input)
            
                    # Postprocess result
                    final_result = await self._postprocess_analyze_user_activity_patterns_result(result)
            
                    logger.info(f"AI processing analyze_user_activity_patterns completed")
                    return final_result
            
                except Exception as e:
                    logger.error(f"AI processing analyze_user_activity_patterns failed: {e}")
                    raise
        patterns = {
            'total_users': total_users,
            'avg_actions_per_user': statistics.mean(action_counts),
            'median_actions_per_user': statistics.median(action_counts),
            'most_active_user': max(user_activity.keys(), key=lambda u: user_activity[u]['total_actions']),
            'avg_sessions_per_user': statistics.mean(session_counts),
            'peak_activity_hour': self._find_peak_hour(user_activity),
            'service_usage_distribution': self._calculate_service_distribution(user_activity)
        }
        
        return patterns
    
    def _find_peak_hour(self, user_activity: Dict[str, Any]) -> int:
        """Find peak activity hour across all users"""
        hourly_totals = [0] * 24
        for data in user_activity.values():
            for hour, count in enumerate(data['hourly_activity']):
                hourly_totals[hour] += count
        
        return hourly_totals.index(max(hourly_totals))
    
    def _calculate_service_distribution(self, user_activity: Dict[str, Any]) -> Dict[str, int]:
        """
Calculate service usage distribution"""
        service_counts = {}
        for data in user_activity.values():
            for service in data['services_used']:
                service_counts[service] = service_counts.get(service, 0) + 1
        
        return service_counts


class TrendAnalyzer:
    """
Analyze trends in log data"""
    
    async def analyze_volume_trends(self, 
                                   log_data: List[Dict[str, Any]],
                                   time_bucket_minutes: int = 60) -> Dict[str, Any]:
        """
Analyze log volume trends over time"""
        if not log_data:
            return {"trend": TrendDirection.STABLE, "data_points": []}
        
        # Group logs by time buckets
        time_buckets = {}
        for log in log_data:
            try:
                timestamp = datetime.fromisoformat(log.get('timestamp', '').replace('Z', '+00:00'))
                # Round to nearest bucket
                bucket_time = timestamp.replace(
                    minute=(timestamp.minute // time_bucket_minutes) * time_bucket_minutes,
                    second=0,
                    microsecond=0
                )
                
                bucket_key = bucket_time.isoformat()
                time_buckets[bucket_key] = time_buckets.get(bucket_key, 0) + 1
                
            except:
                continue
        
        # Sort by time
        sorted_buckets = sorted(time_buckets.items())
        timestamps = [item[0] for item in sorted_buckets]
        counts = [item[1] for item in sorted_buckets]
        
        if len(counts) < 2:
            return {
                "trend": TrendDirection.STABLE,
                "data_points": sorted_buckets,
                "analysis": "Insufficient data for trend analysis"
            }
        
        # Calculate trend
        trend_direction = self._calculate_trend_direction(counts)
        volatility = self._calculate_volatility(counts)
        
        return {
            "trend": trend_direction,
            "volatility": volatility,
            "data_points": sorted_buckets,
            "total_logs": sum(counts),
            "avg_per_bucket": statistics.mean(counts),
            "peak_bucket": max(sorted_buckets, key=lambda x: x[1]),
            "analysis_timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def _calculate_trend_direction(self, values: List[int]) -> TrendDirection:
        """Calculate trend direction from values"""
        if len(values) < 3:
            return TrendDirection.STABLE
        
        # Simple linear trend
        x = range(len(values))
        slope = np.polyfit(x, values, 1)[0]
        
        # Calculate relative change
        avg_value = statistics.mean(values)
        relative_slope = slope / max(avg_value, 1)
        
        if relative_slope > 0.1:
            return TrendDirection.INCREASING
        elif relative_slope < -0.1:
            return TrendDirection.DECREASING
        else:
            # Check volatility
            std_dev = statistics.stdev(values)
            cv = std_dev / max(avg_value, 1)  # Coefficient of variation
            
            if cv > 0.5:
                return TrendDirection.VOLATILE
            else:
                return TrendDirection.STABLE
    
    def _calculate_volatility(self, values: List[int]) -> float:
        """
Calculate volatility score"""
        if len(values) < 2:
            return 0.0
        
        mean_val = statistics.mean(values)
        std_dev = statistics.stdev(values)
        
        # Return coefficient of variation
        return std_dev / max(mean_val, 1)


class LogAnalyticsEngine:
    """
Complete log analytics engine for IA Influencer Agent"""
    
    def __init__(self, elasticsearch_manager -> None: ElasticsearchManager) -> None:
        self.es_manager = elasticsearch_manager
        self.anomaly_detector = AnomalyDetector()
        self.pattern_analyzer = LogPatternAnalyzer()
        self.trend_analyzer = TrendAnalyzer()
        self.alerts: List[LogAlert] = []
        self.metrics: List[LogMetric] = []
        self._setup_default_alerts_and_metrics()
    
    def _setup_default_alerts_and_metrics(self) -> None:
        """
Setup default alerts and metrics for IA Influencer Agent"""
        
        # Default alerts
        default_alerts = [
            LogAlert(
                id="high_error_rate",
                name="High Error Rate",
                description="Error rate exceeds 5% in 15 minutes",
                query='level:ERROR OR level:CRITICAL',
                threshold=0.05,
                severity=AlertSeverity.HIGH,
                time_window_minutes=15
            ),
            LogAlert(
                id="ai_processing_failures",
                name="AI Processing Failures",
                description="AI processing failures exceed 10 in 30 minutes",
                query='service:ai* AND level:ERROR',
                threshold=10,
                severity=AlertSeverity.MEDIUM,
                time_window_minutes=30
            ),
            LogAlert(
                id="fingerprinting_anomalies",
                name="Fingerprinting Anomalies",
                description="Fingerprinting errors exceed 5 in 10 minutes",
                query='service:fingerprinting AND level:ERROR',
                threshold=5,
                severity=AlertSeverity.HIGH,
                time_window_minutes=10
            ),
            LogAlert(
                id="user_auth_failures",
                name="Authentication Failures",
                description="Authentication failures exceed 20 in 5 minutes",
                query='module:auth AND level:ERROR',
                threshold=20,
                severity=AlertSeverity.CRITICAL,
                time_window_minutes=5
            ),
            LogAlert(
                id="revenue_processing_errors",
                name="Revenue Processing Errors",
                description="Revenue processing errors detected",
                query='service:monetization AND level:ERROR',
                threshold=1,
                severity=AlertSeverity.CRITICAL,
                time_window_minutes=60
            )
        ]
        
        self.alerts.extend(default_alerts)
        
        # Default metrics
        default_metrics = [
            LogMetric(
                name="log_volume",
                description="Total log volume per hour",
                query="*",
                aggregation="count",
                time_window_minutes=60
            ),
            LogMetric(
                name="error_rate",
                description="Error rate percentage",
                query="level:ERROR OR level:CRITICAL",
                aggregation="count",
                time_window_minutes=60
            ),
            LogMetric(
                name="avg_processing_time",
                description="Average processing time",
                query="metadata.processing_time_ms:*",
                aggregation="avg",
                field="metadata.processing_time_ms",
                time_window_minutes=60
            ),
            LogMetric(
                name="unique_users",
                description="Unique active users",
                query="user_id:*",
                aggregation="cardinality",
                field="user_id",
                time_window_minutes=60
            ),
            LogMetric(
                name="fingerprint_success_rate",
                description="Fingerprinting success rate",
                query="service:fingerprinting",
                aggregation="count",
                filters={"level": "INFO"},
                time_window_minutes=60
            )
        ]
        
        self.metrics.extend(default_metrics)
    
    async def compute_metrics(self, time_range_hours: int = 24) -> List[AnalyticsResult]:
        """Compute all defined metrics"""
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(hours=time_range_hours)
        
        results = []
        
        for metric in self.metrics:
            try:
                value = await self._compute_single_metric(metric, start_time, end_time)
                
                result = AnalyticsResult(
                    metric_name=metric.name,
                    value=value,
                    timestamp=datetime.now(timezone.utc),
                    metadata={
                        "description": metric.description,
                        "time_range_hours": time_range_hours,
                        "aggregation": metric.aggregation
                    }
                )
                
                results.append(result)
                
            except Exception as e:
                logging.error(f"Failed to compute metric '{metric.name}': {e}")
                
                # Add error result
                error_result = AnalyticsResult(
                    metric_name=metric.name,
                    value=0,
                    timestamp=datetime.now(timezone.utc),
                    metadata={"error": str(e)}
                )
                results.append(error_result)
        
        return results
    
    async def _compute_single_metric(self, 
                                    metric: LogMetric,
                                    start_time: datetime,
                                    end_time: datetime) -> Union[float, int]:
        """Compute a single metric value"""
        
        query_builder = QueryBuilder().add_time_range(start_time, end_time)
        
        # Add filters if specified
        if metric.filters:
            for field, value in metric.filters.items():
                query_builder.query["bool"]["filter"].append({
                    "term": {field: value}
                })
        
        # Add aggregation based on type
        if metric.aggregation == "count":
            query_builder.add_aggregation("metric_value", {
                "filter": {"query_string": {"query": metric.query}}
            })
        elif metric.aggregation == "avg" and metric.field:
            query_builder.add_aggregation("metric_value", {
                "avg": {"field": metric.field}
            })
        elif metric.aggregation == "sum" and metric.field:
            query_builder.add_aggregation("metric_value", {
                "sum": {"field": metric.field}
            })
        elif metric.aggregation == "cardinality" and metric.field:
            query_builder.add_aggregation("metric_value", {
                "cardinality": {"field": metric.field}
            })
        
        # Execute query
        result = await self.es_manager.search_logs(query_builder, size=0)
        
        # Extract value from aggregation
        agg_result = result.get("aggregations", {}).get("metric_value", {})
        
        if metric.aggregation == "count":
            return agg_result.get("doc_count", 0)
        elif metric.aggregation in ["avg", "sum"]:
            return agg_result.get("value", 0)
        elif metric.aggregation == "cardinality":
            return agg_result.get("value", 0)
        
        return 0
    
    async def check_alerts(self) -> List[Dict[str, Any]]:
        """Check all defined alerts"""
        triggered_alerts = []
        current_time = datetime.now(timezone.utc)
        
        for alert in self.alerts:
            if not alert.enabled:
                continue
            
            try:
                start_time = current_time - timedelta(minutes=alert.time_window_minutes)
                
                # Build query
                query_builder = (QueryBuilder()
                               .add_time_range(start_time, current_time)
                               .add_text_search(alert.query))
                
                # Get log count
                result = await self.es_manager.search_logs(query_builder, size=0)
                current_count = result["total"]
                
                # Check threshold
                if current_count >= alert.threshold:
                    # Alert triggered
                    alert.last_triggered = current_time
                    alert.trigger_count += 1
                    
                    triggered_alert = {
                        "alert": alert.to_dict(),
                        "current_value": current_count,
                        "threshold": alert.threshold,
                        "triggered_at": current_time.isoformat(),
                        "time_window_minutes": alert.time_window_minutes
                    }
                    
                    triggered_alerts.append(triggered_alert)
                    
                    logging.warning(f"Alert '{alert.name}' triggered: {current_count} >= {alert.threshold}")
                
            except Exception as e:
                logging.error(f"Failed to check alert '{alert.name}': {e}")
        
        return triggered_alerts
    
    async def detect_anomalies(self, hours_back: int = 24) -> List[Dict[str, Any]]:
        """Detect anomalies in recent logs"""
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(hours=hours_back)
        
        # Get recent logs for training and detection
        query_builder = QueryBuilder().add_time_range(start_time, end_time)
        
        logs_result = await self.es_manager.search_logs(query_builder, size=1000)
        logs = logs_result["hits"]
        
        if len(logs) < 100:
            return []
        
        # Split data for training and detection
        training_size = int(len(logs) * 0.7)
        training_data = logs[:training_size]
        detection_data = logs[training_size:]
        
        # Train and detect
        await self.anomaly_detector.train(training_data)
        anomalies = await self.anomaly_detector.detect_anomalies(detection_data)
        
        return anomalies
    
    async def analyze_error_patterns(self, hours_back: int = 24) -> Dict[str, Any]:
        """Analyze error patterns in recent logs"""
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(hours=hours_back)
        
        # Get error logs
        query_builder = (QueryBuilder()
                        .add_time_range(start_time, end_time)
                        .add_level_filter([LogLevel.ERROR, LogLevel.CRITICAL]))
        
        error_result = await self.es_manager.search_logs(query_builder, size=1000)
        error_logs = error_result["hits"]
        
        return await self.pattern_analyzer.analyze_error_patterns(error_logs)
    
    async def analyze_user_activity(self, hours_back: int = 24) -> Dict[str, Any]:
        """Analyze user activity patterns"""
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(hours=hours_back)
        
        # Get user activity logs
        query_builder = (QueryBuilder()
                        .add_time_range(start_time, end_time)
                        .add_text_search("user_id:*"))
        
        user_result = await self.es_manager.search_logs(query_builder, size=2000)
        user_logs = user_result["hits"]
        
        return await self.pattern_analyzer.analyze_user_activity_patterns(user_logs)
    
    async def analyze_trends(self, hours_back: int = 24) -> Dict[str, Any]:
        """Analyze log volume and error trends"""
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(hours=hours_back)
        
        # Get all logs for volume analysis
        volume_query = QueryBuilder().add_time_range(start_time, end_time)
        volume_result = await self.es_manager.search_logs(volume_query, size=5000)
        volume_logs = volume_result["hits"]
        
        # Get error logs for error trend analysis
        error_query = (QueryBuilder()
                      .add_time_range(start_time, end_time)
                      .add_level_filter([LogLevel.ERROR, LogLevel.CRITICAL]))
        error_result = await self.es_manager.search_logs(error_query, size=1000)
        error_logs = error_result["hits"]
        
        # Analyze trends
        volume_trends = await self.trend_analyzer.analyze_volume_trends(volume_logs, 60)
        error_trends = await self.trend_analyzer.analyze_volume_trends(error_logs, 60)
        
        return {
            "volume_trends": volume_trends,
            "error_trends": error_trends,
            "analysis_period_hours": hours_back,
            "total_logs_analyzed": len(volume_logs),
            "total_errors_analyzed": len(error_logs)
        }
    
    async def generate_dashboard_data(self) -> Dict[str, Any]:
        """Generate comprehensive dashboard data"""
        # Compute current metrics
        metrics = await self.compute_metrics(24)
        
        # Check alerts
        alerts = await self.check_alerts()
        
        # Analyze trends
        trends = await self.analyze_trends(24)
        
        # Detect anomalies
        anomalies = await self.detect_anomalies(24)
        
        # Analyze patterns
        error_patterns = await self.analyze_error_patterns(24)
        user_activity = await self.analyze_user_activity(24)
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metrics": [metric.to_dict() for metric in metrics],
            "active_alerts": alerts,
            "trends": trends,
            "anomalies": {
                "count": len(anomalies),
                "recent_anomalies": anomalies[:10]  # Last 10 anomalies
            },
            "error_patterns": error_patterns,
            "user_activity": user_activity,
            "system_health": {
                "total_metrics": len(metrics),
                "enabled_alerts": len([a for a in self.alerts if a.enabled]),
                "triggered_alerts": len(alerts),
                "anomalies_detected": len(anomalies)
            }
        }
    
    def add_alert(self, alert -> None: LogAlert) -> None:
        """Add custom alert"""
        self.alerts.append(alert)
    
    def add_metric(self, metric -> None: LogMetric) -> None:
        """
Add custom metric"""
        self.metrics.append(metric)
    
    def get_alert(self, alert_id: str) -> Optional[LogAlert]:
        """
Get alert by ID"""
        for alert in self.alerts:
            if alert.id == alert_id:
                return alert
        return None
    
    def update_alert(self, alert_id: str, **kwargs) -> bool:
        """
Update alert configuration"""
        alert = self.get_alert(alert_id)
        if alert:
            for key, value in kwargs.items():
                if hasattr(alert, key):
                    setattr(alert, key, value)
            return True
        return False
    
    def delete_alert(self, alert_id: str) -> bool:
        """
Delete alert"""
        for i, alert in enumerate(self.alerts):
            if alert.id == alert_id:
                del self.alerts[i]
                return True
        return False

# File has syntax issues - needs manual review