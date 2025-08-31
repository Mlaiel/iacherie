"""Stream Analytics Engine for IA Influencer Agent Platform
=======================================================

Advanced analytics engine for real-time stream performance analysis,
trend detection, and predictive insights for content optimization.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import pandas as pd
from statistics import mean, median, stdev
import json

from pydantic import BaseModel, Field
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

from ...core.config import get_settings
from ...utils.logging import get_logger
from .manager import StreamEvent

logger = get_logger(__name__)
settings = get_settings()


class AnalyticsMetric(str, Enum):
    """Analytics metric types"""    THROUGHPUT = "throughput"
    LATENCY = "latency"
    ERROR_RATE = "error_rate"
    SUCCESS_RATE = "success_rate"
    ENGAGEMENT = "engagement"
    RETENTION = "retention"
    CONVERSION = "conversion"
    GROWTH = "growth"


class TrendDirection(str, Enum):
    """Trend direction indicators"""    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"
    VOLATILE = "volatile"


class AlertType(str, Enum):
    """Analytics alert types"""    ANOMALY = "anomaly"
    THRESHOLD = "threshold"
    TREND = "trend"
    PATTERN = "pattern"


@dataclass
class MetricValue:
    """Metric value with timestamp"""    timestamp: datetime
    value: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TrendAnalysis:
    """Trend analysis result"""    metric: AnalyticsMetric
    direction: TrendDirection
    slope: float
    confidence: float
    start_value: float
    end_value: float
    change_percent: float
    analysis_period: timedelta


@dataclass
class AnomalyDetection:
    """Anomaly detection result"""    timestamp: datetime
    metric: AnalyticsMetric
    value: float
    expected_value: float
    deviation_score: float
    severity: str
    description: str


class StreamMetrics(BaseModel):
    """Stream performance metrics"""    stream_id: str = Field(description="Stream identifier")
    total_events: int = Field(default=0, description="Total events processed")
    events_per_second: float = Field(default=0.0, description="Current throughput")
    average_latency: float = Field(default=0.0, description="Average processing latency")
    success_rate: float = Field(default=100.0, description="Success rate percentage")
    error_rate: float = Field(default=0.0, description="Error rate percentage")
    peak_throughput: float = Field(default=0.0, description="Peak throughput observed")
    uptime_percentage: float = Field(default=100.0, description="Uptime percentage")
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AnalyticsInsight(BaseModel):
    """Analytics insight result"""    insight_type: str = Field(description="Type of insight")
    title: str = Field(description="Insight title")
    description: str = Field(description="Detailed description")
    confidence: float = Field(description="Confidence score (0-1)")
    priority: str = Field(description="Priority level")
    recommendations: List[str] = Field(default_factory=list, description="Action recommendations")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class StreamAnalytics:
    """    Advanced analytics engine for real-time stream performance analysis,
    anomaly detection, trend analysis, and predictive insights.
    """    
    def __init__(self):
        self.metrics_history: Dict[str, List[MetricValue]] = {}
        self.stream_metrics: Dict[str, StreamMetrics] = {}
        self.trend_cache: Dict[str, TrendAnalysis] = {}
        self.anomaly_cache: Dict[str, List[AnomalyDetection]] = {}
        self.analytics_callbacks: List[Any] = []
        self._shutdown_event = asyncio.Event()
        
    async def initialize(self) -> None:
        """Initialize stream analytics engine"""        try:
            # Start background analytics tasks
            asyncio.create_task(self._trend_analyzer())
            asyncio.create_task(self._anomaly_detector())
            asyncio.create_task(self._metrics_aggregator())
            asyncio.create_task(self._insight_generator())
            
            logger.info("StreamAnalytics initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize StreamAnalytics: {e}")
            raise
            
    async def record_metric(
        self,
        stream_id: str,
        metric: AnalyticsMetric,
        value: float,
        timestamp: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """        Record metric value for analytics
        
        Args:
            stream_id: Stream identifier
            metric: Metric type
            value: Metric value
            timestamp: Optional timestamp
            metadata: Optional metadata
        """        try:
            if timestamp is None:
                timestamp = datetime.now(timezone.utc)
                
            metric_key = f"{stream_id}_{metric.value}"
            
            if metric_key not in self.metrics_history:
                self.metrics_history[metric_key] = []
                
            metric_value = MetricValue(
                timestamp=timestamp,
                value=value,
                metadata=metadata or {}
            )
            
            self.metrics_history[metric_key].append(metric_value)
            
            # Keep only last 10000 metrics per stream
            if len(self.metrics_history[metric_key]) > 10000:
                self.metrics_history[metric_key] = self.metrics_history[metric_key][-10000:]
                
            # Update real-time metrics
            await self._update_stream_metrics(stream_id, metric, value)
            
        except Exception as e:
            logger.error(f"Failed to record metric: {e}")
            
    async def get_stream_metrics(self, stream_id: str) -> Optional[StreamMetrics]:
        """Get current metrics for stream"""        return self.stream_metrics.get(stream_id)
        
    async def get_metric_history(
        self,
        stream_id: str,
        metric: AnalyticsMetric,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 1000
    ) -> List[MetricValue]:
        """        Get metric history for stream
        
        Args:
            stream_id: Stream identifier
            metric: Metric type
            start_time: Start time filter
            end_time: End time filter
            limit: Maximum number of values
            
        Returns:
            List of metric values
        """        try:
            metric_key = f"{stream_id}_{metric.value}"
            
            if metric_key not in self.metrics_history:
                return []
                
            history = self.metrics_history[metric_key]
            
            # Apply time filters
            if start_time or end_time:
                filtered_history = []
                for metric_value in history:
                    if start_time and metric_value.timestamp < start_time:
                        continue
                    if end_time and metric_value.timestamp > end_time:
                        continue
                    filtered_history.append(metric_value)
                history = filtered_history
                
            # Apply limit
            if len(history) > limit:
                history = history[-limit:]
                
            return history
            
        except Exception as e:
            logger.error(f"Failed to get metric history: {e}")
            return []
            
    async def analyze_trend(
        self,
        stream_id: str,
        metric: AnalyticsMetric,
        period_hours: int = 24
    ) -> Optional[TrendAnalysis]:
        """        Analyze trend for metric over specified period
        
        Args:
            stream_id: Stream identifier
            metric: Metric type
            period_hours: Analysis period in hours
            
        Returns:
            Trend analysis result
        """        try:
            end_time = datetime.now(timezone.utc)
            start_time = end_time - timedelta(hours=period_hours)
            
            history = await self.get_metric_history(stream_id, metric, start_time, end_time)
            
            if len(history) < 10:  # Need at least 10 data points
                return None
                
            # Extract values and timestamps
            values = [mv.value for mv in history]
            timestamps = [mv.timestamp.timestamp() for mv in history]
            
            # Perform linear regression
            slope, intercept, r_value, p_value, std_err = stats.linregress(timestamps, values)
            
            # Determine trend direction
            if abs(slope) < 0.001:  # Very small slope
                direction = TrendDirection.STABLE
            elif slope > 0:
                direction = TrendDirection.INCREASING
            else:
                direction = TrendDirection.DECREASING
                
            # Check for volatility
            if stdev(values) > mean(values) * 0.5:  # High volatility
                direction = TrendDirection.VOLATILE
                
            # Calculate change percentage
            start_value = values[0]
            end_value = values[-1]
            change_percent = ((end_value - start_value) / start_value * 100) if start_value != 0 else 0
            
            trend = TrendAnalysis(
                metric=metric,
                direction=direction,
                slope=slope,
                confidence=abs(r_value),
                start_value=start_value,
                end_value=end_value,
                change_percent=change_percent,
                analysis_period=timedelta(hours=period_hours)
            )
            
            # Cache result
            trend_key = f"{stream_id}_{metric.value}"
            self.trend_cache[trend_key] = trend
            
            return trend
            
        except Exception as e:
            logger.error(f"Failed to analyze trend: {e}")
            return None
            
    async def detect_anomalies(
        self,
        stream_id: str,
        metric: AnalyticsMetric,
        sensitivity: float = 2.0
    ) -> List[AnomalyDetection]:
        """        Detect anomalies in metric using statistical methods
        
        Args:
            stream_id: Stream identifier
            metric: Metric type
            sensitivity: Sensitivity threshold (standard deviations)
            
        Returns:
            List of detected anomalies
        """        try:
            # Get recent history
            end_time = datetime.now(timezone.utc)
            start_time = end_time - timedelta(hours=24)
            
            history = await self.get_metric_history(stream_id, metric, start_time, end_time)
            
            if len(history) < 20:  # Need sufficient data
                return []
                
            values = [mv.value for mv in history]
            
            # Calculate statistical parameters
            mean_value = mean(values)
            std_value = stdev(values) if len(values) > 1 else 0
            
            anomalies = []
            
            # Detect outliers using z-score
            for metric_value in history[-10:]:  # Check last 10 values
                z_score = abs((metric_value.value - mean_value) / std_value) if std_value > 0 else 0
                
                if z_score > sensitivity:
                    severity = "high" if z_score > 3.0 else "medium"
                    
                    anomaly = AnomalyDetection(
                        timestamp=metric_value.timestamp,
                        metric=metric,
                        value=metric_value.value,
                        expected_value=mean_value,
                        deviation_score=z_score,
                        severity=severity,
                        description=f"{metric.value} value {metric_value.value:.2f} deviates {z_score:.2f} standard deviations from mean {mean_value:.2f}"
                    )
                    anomalies.append(anomaly)
                    
            # Cache anomalies
            anomaly_key = f"{stream_id}_{metric.value}"
            if anomaly_key not in self.anomaly_cache:
                self.anomaly_cache[anomaly_key] = []
            self.anomaly_cache[anomaly_key].extend(anomalies)
            
            # Keep only recent anomalies
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=48)
            self.anomaly_cache[anomaly_key] = [
                a for a in self.anomaly_cache[anomaly_key]
                if a.timestamp >= cutoff_time
            ]
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Failed to detect anomalies: {e}")
            return []
            
    async def generate_insights(self, stream_id: str) -> List[AnalyticsInsight]:
        """        Generate actionable insights for stream
        
        Args:
            stream_id: Stream identifier
            
        Returns:
            List of analytics insights
        """        try:
            insights = []
            
            # Get current metrics
            metrics = await self.get_stream_metrics(stream_id)
            if not metrics:
                return insights
                
            # Performance insights
            if metrics.error_rate > 5.0:
                insights.append(AnalyticsInsight(
                    insight_type="performance",
                    title="High Error Rate Detected",
                    description=f"Error rate is {metrics.error_rate:.1f}%, which is above the recommended threshold of 5%",
                    confidence=0.9,
                    priority="high",
                    recommendations=[
                        "Review error logs for common failure patterns",
                        "Implement retry mechanisms for transient failures",
                        "Monitor upstream dependencies"
                    ]
                ))
                
            if metrics.average_latency > 5.0:
                insights.append(AnalyticsInsight(
                    insight_type="performance",
                    title="High Processing Latency",
                    description=f"Average latency is {metrics.average_latency:.1f}s, consider optimization",
                    confidence=0.8,
                    priority="medium",
                    recommendations=[
                        "Profile processing bottlenecks",
                        "Implement caching strategies",
                        "Consider parallel processing"
                    ]
                ))
                
            # Throughput insights
            if metrics.events_per_second < 1.0 and metrics.total_events > 100:
                insights.append(AnalyticsInsight(
                    insight_type="throughput",
                    title="Low Throughput Detected",
                    description=f"Current throughput is {metrics.events_per_second:.2f} events/sec",
                    confidence=0.7,
                    priority="medium",
                    recommendations=[
                        "Analyze processing pipeline efficiency",
                        "Implement batch processing",
                        "Scale processing resources"
                    ]
                ))
                
            # Trend-based insights
            for metric_type in [AnalyticsMetric.THROUGHPUT, AnalyticsMetric.ERROR_RATE]:
                trend = await self.analyze_trend(stream_id, metric_type, 24)
                if trend:
                    if trend.direction == TrendDirection.DECREASING and metric_type == AnalyticsMetric.THROUGHPUT:
                        insights.append(AnalyticsInsight(
                            insight_type="trend",
                            title="Decreasing Throughput Trend",
                            description=f"Throughput has decreased by {abs(trend.change_percent):.1f}% over 24 hours",
                            confidence=trend.confidence,
                            priority="medium",
                            recommendations=[
                                "Investigate recent changes",
                                "Check system resources",
                                "Review recent deployments"
                            ]
                        ))
                        
                    elif trend.direction == TrendDirection.INCREASING and metric_type == AnalyticsMetric.ERROR_RATE:
                        insights.append(AnalyticsInsight(
                            insight_type="trend",
                            title="Increasing Error Rate Trend",
                            description=f"Error rate has increased by {trend.change_percent:.1f}% over 24 hours",
                            confidence=trend.confidence,
                            priority="high",
                            recommendations=[
                                "Investigate error patterns",
                                "Check data quality",
                                "Review configuration changes"
                            ]
                        ))
                        
            return insights
            
        except Exception as e:
            logger.error(f"Failed to generate insights: {e}")
            return []
            
    async def get_performance_summary(self, stream_id: str) -> Dict[str, Any]:
        """Get comprehensive performance summary for stream"""        try:
            metrics = await self.get_stream_metrics(stream_id)
            insights = await self.generate_insights(stream_id)
            
            # Get recent anomalies
            recent_anomalies = []
            for metric_type in AnalyticsMetric:
                anomaly_key = f"{stream_id}_{metric_type.value}"
                if anomaly_key in self.anomaly_cache:
                    recent_anomalies.extend(self.anomaly_cache[anomaly_key][-5:])
                    
            # Calculate health score
            health_score = 100.0
            if metrics:
                health_score -= metrics.error_rate * 2  # Penalty for errors
                health_score -= max(0, (metrics.average_latency - 1.0) * 10)  # Penalty for high latency
                health_score = max(0, min(100, health_score))
                
            return {
                "stream_id": stream_id,
                "health_score": health_score,
                "status": "healthy" if health_score > 80 else "degraded" if health_score > 50 else "critical",
                "metrics": metrics.dict() if metrics else {},
                "insights": [insight.dict() for insight in insights],
                "recent_anomalies": len(recent_anomalies),
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get performance summary: {e}")
            return {}
            
    async def compare_streams(self, stream_ids: List[str]) -> Dict[str, Any]:
        """Compare performance across multiple streams"""        try:
            comparison = {
                "streams": {},
                "rankings": {},
                "insights": []
            }
            
            stream_data = []
            for stream_id in stream_ids:
                metrics = await self.get_stream_metrics(stream_id)
                if metrics:
                    stream_data.append((stream_id, metrics))
                    comparison["streams"][stream_id] = metrics.dict()
                    
            if not stream_data:
                return comparison
                
            # Rank streams by different metrics
            comparison["rankings"]["throughput"] = sorted(
                stream_data, key=lambda x: x[1].events_per_second, reverse=True
            )[:5]
            
            comparison["rankings"]["success_rate"] = sorted(
                stream_data, key=lambda x: x[1].success_rate, reverse=True
            )[:5]
            
            comparison["rankings"]["latency"] = sorted(
                stream_data, key=lambda x: x[1].average_latency
            )[:5]
            
            # Generate comparative insights
            throughputs = [metrics.events_per_second for _, metrics in stream_data]
            avg_throughput = mean(throughputs)
            
            outliers = [
                stream_id for stream_id, metrics in stream_data
                if abs(metrics.events_per_second - avg_throughput) > stdev(throughputs) * 2
            ]
            
            if outliers:
                comparison["insights"].append({
                    "type": "comparison",
                    "title": "Performance Outliers Detected",
                    "description": f"Streams {', '.join(outliers)} show significant performance differences",
                    "recommendations": ["Investigate configuration differences", "Standardize processing pipelines"]
                })
                
            return comparison
            
        except Exception as e:
            logger.error(f"Failed to compare streams: {e}")
            return {}
            
    async def _update_stream_metrics(
        self,
        stream_id: str,
        metric: AnalyticsMetric,
        value: float
    ) -> None:
        """Update real-time stream metrics"""        try:
            if stream_id not in self.stream_metrics:
                self.stream_metrics[stream_id] = StreamMetrics(stream_id=stream_id)
                
            metrics = self.stream_metrics[stream_id]
            
            if metric == AnalyticsMetric.THROUGHPUT:
                metrics.events_per_second = value
                metrics.peak_throughput = max(metrics.peak_throughput, value)
            elif metric == AnalyticsMetric.LATENCY:
                metrics.average_latency = value
            elif metric == AnalyticsMetric.ERROR_RATE:
                metrics.error_rate = value
                metrics.success_rate = 100.0 - value
            elif metric == AnalyticsMetric.SUCCESS_RATE:
                metrics.success_rate = value
                metrics.error_rate = 100.0 - value
                
            metrics.last_updated = datetime.now(timezone.utc)
            
        except Exception as e:
            logger.error(f"Failed to update stream metrics: {e}")
            
    async def _trend_analyzer(self) -> None:
        """Background trend analysis task"""        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(300)  # Analyze every 5 minutes
                
                # Analyze trends for all streams
                for stream_id in self.stream_metrics.keys():
                    for metric in [AnalyticsMetric.THROUGHPUT, AnalyticsMetric.ERROR_RATE]:
                        await self.analyze_trend(stream_id, metric)
                        
            except Exception as e:
                logger.error(f"Trend analyzer error: {e}")
                
    async def _anomaly_detector(self) -> None:
        """Background anomaly detection task"""        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(60)  # Check every minute
                
                # Detect anomalies for all streams
                for stream_id in self.stream_metrics.keys():
                    for metric in [AnalyticsMetric.THROUGHPUT, AnalyticsMetric.LATENCY, AnalyticsMetric.ERROR_RATE]:
                        anomalies = await self.detect_anomalies(stream_id, metric)
                        
                        # Notify callbacks for high-severity anomalies
                        for anomaly in anomalies:
                            if anomaly.severity == "high":
                                await self._notify_anomaly(anomaly)
                                
            except Exception as e:
                logger.error(f"Anomaly detector error: {e}")
                
    async def _metrics_aggregator(self) -> None:
        """Background metrics aggregation task"""        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(30)  # Aggregate every 30 seconds
                
                # Update aggregated metrics
                for stream_id in self.stream_metrics.keys():
                    await self._calculate_uptime(stream_id)
                    
            except Exception as e:
                logger.error(f"Metrics aggregator error: {e}")
                
    async def _insight_generator(self) -> None:
        """Background insight generation task"""        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(900)  # Generate insights every 15 minutes
                
                # Generate insights for all streams
                for stream_id in self.stream_metrics.keys():
                    insights = await self.generate_insights(stream_id)
                    
                    # Notify callbacks for high-priority insights
                    for insight in insights:
                        if insight.priority == "high":
                            await self._notify_insight(insight)
                            
            except Exception as e:
                logger.error(f"Insight generator error: {e}")
                
    async def _calculate_uptime(self, stream_id: str) -> None:
        """Calculate uptime percentage for stream"""        try:
            # Get error events in last 24 hours
            error_history = await self.get_metric_history(
                stream_id,
                AnalyticsMetric.ERROR_RATE,
                datetime.now(timezone.utc) - timedelta(hours=24)
            )
            
            if not error_history:
                return
                
            # Calculate uptime based on error rate
            total_periods = len(error_history)
            error_periods = sum(1 for mv in error_history if mv.value > 50.0)  # >50% error rate
            
            uptime = ((total_periods - error_periods) / total_periods * 100) if total_periods > 0 else 100
            
            if stream_id in self.stream_metrics:
                self.stream_metrics[stream_id].uptime_percentage = uptime
                
        except Exception as e:
            logger.error(f"Failed to calculate uptime: {e}")
            
    async def _notify_anomaly(self, anomaly: AnomalyDetection) -> None:
        """Notify callbacks about anomaly"""        for callback in self.analytics_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback("anomaly", anomaly)
                else:
                    callback("anomaly", anomaly)
            except Exception as e:
                logger.error(f"Anomaly callback error: {e}")
                
    async def _notify_insight(self, insight: AnalyticsInsight) -> None:
        """Notify callbacks about insight"""        for callback in self.analytics_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback("insight", insight)
                else:
                    callback("insight", insight)
            except Exception as e:
                logger.error(f"Insight callback error: {e}")
                
    async def register_callback(self, callback: Any) -> None:
        """Register analytics callback"""        self.analytics_callbacks.append(callback)
        
    async def shutdown(self) -> None:
        """Gracefully shutdown analytics engine"""        try:
            self._shutdown_event.set()
            logger.info("StreamAnalytics shutdown completed")
        except Exception as e:
            logger.error(f"Error during analytics shutdown: {e}")
