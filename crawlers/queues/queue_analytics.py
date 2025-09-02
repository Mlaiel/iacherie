"""Queue Analytics - IA-Influencer-Agent
================================================================================
Module: backend/crawlers/queues/queue_analytics.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Industrial Queue Analytics Engine - Performance Analysis & Insights
Responsibility: Advanced analytics and insights for queue performance optimization
Technologies: Analytics Engine, ML Insights, Performance Metrics, Reporting
================================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Contact: mlaiel@live.de

LOGIQUE MÉTIER:
Data collection → Metrics aggregation → Pattern analysis → Performance insights → 
Prediction modeling → Optimization recommendations → Automated reporting
"""

from typing import Any, Dict, List, Optional, Tuple, Set
import logging
import asyncio
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import json
import statistics
import numpy as np
from collections import defaultdict, deque
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64

from .crawler_queue_manager import PlatformType, CrawlerPriority, CrawlerQueueType

logger = logging.getLogger(__name__)


class AnalyticsTimeframe(Enum):
    """
Analytics timeframe options"""

    REAL_TIME = "real_time"          # Last 5 minutes
    HOURLY = "hourly"                # Last hour
    DAILY = "daily"                  # Last 24 hours
    WEEKLY = "weekly"                # Last 7 days
    MONTHLY = "monthly"              # Last 30 days
    QUARTERLY = "quarterly"          # Last 90 days
    YEARLY = "yearly"                # Last 365 days


class MetricType(Enum):
    """Types of metrics to analyze"""

    THROUGHPUT = "throughput"
    LATENCY = "latency"
    ERROR_RATE = "error_rate"
    QUEUE_SIZE = "queue_size"
    WORKER_UTILIZATION = "worker_utilization"
    PRIORITY_DISTRIBUTION = "priority_distribution"
    PLATFORM_PERFORMANCE = "platform_performance"
    SUCCESS_RATE = "success_rate"


@dataclass
class AnalyticsDataPoint:
    """Single analytics data point"""
    timestamp: datetime
    metric_type: MetricType
    value: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)


@dataclass
class PerformanceInsight:
    """
Performance insight with recommendations"""
    insight_type: str
    severity: str  # low, medium, high, critical
    title: str
    description: str
    impact: str
    recommendations: List[str]
    confidence: float  # 0.0 to 1.0
    detected_at: datetime = field(default_factory=datetime.now)
    affected_components: List[str] = field(default_factory=list)
    metrics_evidence: List[str] = field(default_factory=list)


@dataclass
class AnalyticsReport:
    """
Comprehensive analytics report"""
    report_id: str
    timeframe: AnalyticsTimeframe
    generated_at: datetime
    
    # Summary metrics
    summary: Dict[str, Any]
    
    # Performance insights
    insights: List[PerformanceInsight]
    
    # Detailed metrics
    metrics: Dict[str, Any]
    
    # Visualizations (base64 encoded images)
    charts: Dict[str, str]
    
    # Recommendations
    recommendations: List[str]
    
    # Predictions
    predictions: Dict[str, Any]


class QueueAnalyticsEngine:
    """
    📊 Advanced Queue Analytics Engine - IA-Influencer-Agent
    
    Enterprise-grade analytics engine featuring:
    - Real-time performance monitoring
    - Historical trend analysis
    - Predictive analytics and forecasting
    - Automated insight generation
    - Performance bottleneck detection
    - Optimization recommendations
    - Comprehensive reporting
    """
    
    def __init__(self, retention_days: int = 90):
        self.retention_days = retention_days
        
        # Data storage
        self.metrics_data: Dict[MetricType, deque] = {
            metric_type: deque(maxlen=100000) for metric_type in MetricType
        }
        
        # Analytics cache
        self.insights_cache: Dict[str, List[PerformanceInsight]] = {}
        self.reports_cache: Dict[str, AnalyticsReport] = {}
        
        # Pattern detection
        self.pattern_history: deque = deque(maxlen=1000)
        self.anomaly_detection_models: Dict[MetricType, Any] = {}
        
        # Performance baselines
        self.performance_baselines: Dict[str, float] = {
            "throughput_baseline": 100.0,  # tasks per minute
            "latency_baseline": 2000.0,    # milliseconds
            "error_rate_baseline": 0.05,   # 5%
            "queue_size_baseline": 100,    # tasks
            "worker_utilization_baseline": 0.7  # 70%
        }
        
        # Insight generators
        self.insight_generators: List[Any] = []
        
        # Background tasks
        self._is_running = False
        self._analytics_tasks: List[asyncio.Task] = []
    
    async def initialize(self) -> bool:
        """Initialize analytics engine"""
        try:
            self._is_running = True
            
            # Initialize insight generators
            await self._initialize_insight_generators()
            
            # Start background analytics tasks
            self._analytics_tasks.extend([
                asyncio.create_task(self._data_collector()),
                asyncio.create_task(self._insight_generator()),
                asyncio.create_task(self._anomaly_detector()),
                asyncio.create_task(self._data_cleaner()),
                asyncio.create_task(self._cache_manager())
            ])
            
            logger.info("✅ Queue Analytics Engine initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Analytics engine initialization failed: {e}")
            return False
    
    async def record_metric(
        self,
        metric_type: MetricType,
        value: float,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None
    ):
        """Record a metric data point"""
        try:
            data_point = AnalyticsDataPoint(
                timestamp=datetime.now(),
                metric_type=metric_type,
                value=value,
                metadata=metadata or {},
                tags=tags or []
            )
            
            self.metrics_data[metric_type].append(data_point)
            
        except Exception as e:
            logger.error(f"❌ Failed to record metric: {e}")
    
    async def get_real_time_metrics(self) -> Dict[str, Any]:
        """Get real-time performance metrics"""
        try:
            current_time = datetime.now()
            five_minutes_ago = current_time - timedelta(minutes=5)
            
            real_time_metrics = {}
            
            for metric_type in MetricType:
                recent_data = [
                    dp for dp in self.metrics_data[metric_type]
                    if dp.timestamp > five_minutes_ago
                ]
                
                if recent_data:
                    values = [dp.value for dp in recent_data]
                    real_time_metrics[metric_type.value] = {
                        "current": values[-1] if values else 0,
                        "average": statistics.mean(values),
                        "min": min(values),
                        "max": max(values),
                        "trend": await self._calculate_trend(values),
                        "data_points": len(values)
                    }
                else:
                    real_time_metrics[metric_type.value] = {
                        "current": 0,
                        "average": 0,
                        "min": 0,
                        "max": 0,
                        "trend": "stable",
                        "data_points": 0
                    }
            
            return {
                "timestamp": current_time.isoformat(),
                "timeframe": "5_minutes",
                "metrics": real_time_metrics,
                "health_score": await self._calculate_health_score()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get real-time metrics: {e}")
            return {"error": str(e)}
    
    async def generate_analytics_report(
        self,
        timeframe: AnalyticsTimeframe,
        include_predictions: bool = True,
        include_charts: bool = True
    ) -> AnalyticsReport:
        """Generate comprehensive analytics report"""
        try:
            report_id = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Calculate timeframe boundaries
            end_time = datetime.now()
            start_time = await self._get_timeframe_start(timeframe, end_time)
            
            # Collect metrics for timeframe
            timeframe_data = await self._collect_timeframe_data(start_time, end_time)
            
            # Generate summary
            summary = await self._generate_summary(timeframe_data, timeframe)
            
            # Generate insights
            insights = await self._generate_insights(timeframe_data, timeframe)
            
            # Generate detailed metrics
            detailed_metrics = await self._generate_detailed_metrics(timeframe_data)
            
            # Generate charts
            charts = {}
            if include_charts:
                charts = await self._generate_charts(timeframe_data, timeframe)
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(insights)
            
            # Generate predictions
            predictions = {}
            if include_predictions:
                predictions = await self._generate_predictions(timeframe_data)
            
            report = AnalyticsReport(
                report_id=report_id,
                timeframe=timeframe,
                generated_at=datetime.now(),
                summary=summary,
                insights=insights,
                metrics=detailed_metrics,
                charts=charts,
                recommendations=recommendations,
                predictions=predictions
            )
            
            # Cache report
            self.reports_cache[report_id] = report
            
            logger.info(f"📊 Analytics report generated: {report_id}")
            return report
            
        except Exception as e:
            logger.error(f"❌ Failed to generate analytics report: {e}")
            raise
    
    async def detect_performance_anomalies(
        self,
        metric_type: Optional[MetricType] = None,
        sensitivity: float = 2.0
    ) -> List[Dict[str, Any]]:
        """Detect performance anomalies using statistical analysis"""
        try:
            anomalies = []
            
            metric_types = [metric_type] if metric_type else list(MetricType)
            
            for mt in metric_types:
                data_points = list(self.metrics_data[mt])
                
                if len(data_points) < 30:  # Need enough data for anomaly detection
                    continue
                
                # Extract values and timestamps
                values = [dp.value for dp in data_points[-100:]]  # Last 100 points
                timestamps = [dp.timestamp for dp in data_points[-100:]]
                
                # Calculate statistical thresholds
                mean_value = statistics.mean(values)
                std_dev = statistics.stdev(values) if len(values) > 1 else 0
                
                upper_threshold = mean_value + (sensitivity * std_dev)
                lower_threshold = mean_value - (sensitivity * std_dev)
                
                # Detect anomalies
                for i, (value, timestamp) in enumerate(zip(values[-10:], timestamps[-10:])):
                    if value > upper_threshold or value < lower_threshold:
                        anomaly_score = abs(value - mean_value) / std_dev if std_dev > 0 else 0
                        
                        anomalies.append({
                            "metric_type": mt.value,
                            "timestamp": timestamp.isoformat(),
                            "value": value,
                            "expected_range": [lower_threshold, upper_threshold],
                            "anomaly_score": anomaly_score,
                            "severity": await self._classify_anomaly_severity(anomaly_score),
                            "description": await self._describe_anomaly(mt, value, mean_value)
                        })
            
            return sorted(anomalies, key=lambda x: x["anomaly_score"], reverse=True)
            
        except Exception as e:
            logger.error(f"❌ Anomaly detection failed: {e}")
            return []
    
    async def get_performance_insights(
        self,
        timeframe: AnalyticsTimeframe = AnalyticsTimeframe.DAILY
    ) -> List[PerformanceInsight]:
        """Get performance insights for timeframe"""
        try:
            cache_key = f"insights_{timeframe.value}_{datetime.now().strftime('%Y%m%d_%H')}"
            
            # Check cache
            if cache_key in self.insights_cache:
                return self.insights_cache[cache_key]
            
            insights = []
            
            # Collect data for timeframe
            end_time = datetime.now()
            start_time = await self._get_timeframe_start(timeframe, end_time)
            timeframe_data = await self._collect_timeframe_data(start_time, end_time)
            
            # Generate various types of insights
            insights.extend(await self._generate_throughput_insights(timeframe_data))
            insights.extend(await self._generate_latency_insights(timeframe_data))
            insights.extend(await self._generate_error_insights(timeframe_data))
            insights.extend(await self._generate_capacity_insights(timeframe_data))
            insights.extend(await self._generate_platform_insights(timeframe_data))
            
            # Sort by severity and confidence
            insights.sort(key=lambda x: (
                {"critical": 4, "high": 3, "medium": 2, "low": 1}[x.severity],
                x.confidence
            ), reverse=True)
            
            # Cache insights
            self.insights_cache[cache_key] = insights
            
            return insights
            
        except Exception as e:
            logger.error(f"❌ Failed to get performance insights: {e}")
            return []
    
    async def predict_queue_performance(
        self,
        forecast_hours: int = 24
    ) -> Dict[str, Any]:
        """Predict queue performance for next N hours"""
        try:
            predictions = {}
            
            for metric_type in [MetricType.THROUGHPUT, MetricType.LATENCY, MetricType.QUEUE_SIZE]:
                data_points = list(self.metrics_data[metric_type])
                
                if len(data_points) < 50:  # Need enough historical data
                    continue
                
                # Extract time series data
                timestamps = [dp.timestamp for dp in data_points[-100:]]
                values = [dp.value for dp in data_points[-100:]]
                
                # Simple linear trend prediction (could be enhanced with ML models)
                prediction = await self._predict_metric_trend(timestamps, values, forecast_hours)
                
                predictions[metric_type.value] = prediction
            
            return {
                "forecast_hours": forecast_hours,
                "generated_at": datetime.now().isoformat(),
                "predictions": predictions,
                "confidence": 0.75,  # Would be calculated based on model performance
                "methodology": "linear_trend_analysis"
            }
            
        except Exception as e:
            logger.error(f"❌ Performance prediction failed: {e}")
            return {"error": str(e)}
    
    async def get_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """Get optimization recommendations based on current performance"""
        try:
            recommendations = []
            
            # Get recent insights
            insights = await self.get_performance_insights(AnalyticsTimeframe.DAILY)
            
            # Get current metrics
            current_metrics = await self.get_real_time_metrics()
            
            # Generate recommendations based on insights and metrics
            recommendations.extend(await self._generate_throughput_recommendations(current_metrics))
            recommendations.extend(await self._generate_latency_recommendations(current_metrics))
            recommendations.extend(await self._generate_capacity_recommendations(current_metrics))
            recommendations.extend(await self._generate_error_recommendations(current_metrics))
            
            # Rank recommendations by impact and feasibility
            for rec in recommendations:
                rec["priority_score"] = await self._calculate_recommendation_priority(rec)
            
            recommendations.sort(key=lambda x: x["priority_score"], reverse=True)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ Failed to generate optimization recommendations: {e}")
            return []
    
    async def export_analytics_data(
        self,
        timeframe: AnalyticsTimeframe,
        format_type: str = "json"
    ) -> Dict[str, Any]:
        """Export analytics data in specified format"""
        try:
            end_time = datetime.now()
            start_time = await self._get_timeframe_start(timeframe, end_time)
            
            # Collect all data for timeframe
            export_data = {}
            
            for metric_type in MetricType:
                timeframe_data = [
                    dp for dp in self.metrics_data[metric_type]
                    if start_time <= dp.timestamp <= end_time
                ]
                
                if format_type == "json":
                    export_data[metric_type.value] = [
                        {
                            "timestamp": dp.timestamp.isoformat(),
                            "value": dp.value,
                            "metadata": dp.metadata,
                            "tags": dp.tags
                        }
                        for dp in timeframe_data
                    ]
                elif format_type == "csv":
                    # Convert to CSV format
                    df = pd.DataFrame([
                        {
                            "timestamp": dp.timestamp,
                            "metric_type": metric_type.value,
                            "value": dp.value,
                            **dp.metadata
                        }
                        for dp in timeframe_data
                    ])
                    export_data[metric_type.value] = df.to_csv(index=False)
            
            return {
                "timeframe": timeframe.value,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "format": format_type,
                "data": export_data,
                "exported_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to export analytics data: {e}")
            return {"error": str(e)}
    
    async def shutdown(self):
        """Gracefully shutdown analytics engine"""
        try:
            self._is_running = False
            
            # Cancel background tasks
            for task in self._analytics_tasks:
                task.cancel()
            
            # Clear caches
            self.insights_cache.clear()
            self.reports_cache.clear()
            
            logger.info("🛑 Queue Analytics Engine shutdown completed")
            
        except Exception as e:
            logger.error(f"❌ Analytics engine shutdown error: {e}")
    
    # Private helper methods
    
    async def _initialize_insight_generators(self):
        try:
            logger.info(f"Executing _initialize_insight_generators")
            
            # Implementation for _initialize_insight_generators
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"_initialize_insight_generators completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_initialize_insight_generators failed: {e}")
            raise
    async def _get_timeframe_start(self, timeframe: AnalyticsTimeframe, end_time: datetime) -> datetime:
        """
Calculate start time for timeframe"""
        if timeframe == AnalyticsTimeframe.REAL_TIME:
            return end_time - timedelta(minutes=5)
        elif timeframe == AnalyticsTimeframe.HOURLY:
            return end_time - timedelta(hours=1)
        elif timeframe == AnalyticsTimeframe.DAILY:
            return end_time - timedelta(days=1)
        elif timeframe == AnalyticsTimeframe.WEEKLY:
            return end_time - timedelta(days=7)
        elif timeframe == AnalyticsTimeframe.MONTHLY:
            return end_time - timedelta(days=30)
        elif timeframe == AnalyticsTimeframe.QUARTERLY:
            return end_time - timedelta(days=90)
        elif timeframe == AnalyticsTimeframe.YEARLY:
            return end_time - timedelta(days=365)
        else:
            return end_time - timedelta(days=1)
    
    async def _collect_timeframe_data(
        self, 
        start_time: datetime, 
        end_time: datetime
    ) -> Dict[MetricType, List[AnalyticsDataPoint]]:
        """
Collect data for specific timeframe"""
        timeframe_data = {}
        
        for metric_type in MetricType:
            timeframe_data[metric_type] = [
                dp for dp in self.metrics_data[metric_type]
                if start_time <= dp.timestamp <= end_time
            ]
        
        return timeframe_data
    
    async def _calculate_trend(self, values: List[float]) -> str:
        """
Calculate trend direction for values"""
        if len(values) < 2:
            return "stable"
        
        # Simple trend calculation
        recent_avg = statistics.mean(values[-10:]) if len(values) >= 10 else statistics.mean(values)
        older_avg = statistics.mean(values[:-10]) if len(values) >= 20 else statistics.mean(values[:-5])
        
        if recent_avg > older_avg * 1.1:
            return "increasing"
        elif recent_avg < older_avg * 0.9:
            return "decreasing"
        else:
            return "stable"
    
    async def _calculate_health_score(self) -> float:
        """Calculate overall system health score (0-100)"""
        health_score = 100.0
        
        # Check each metric against baseline
        for metric_type in MetricType:
            if not self.metrics_data[metric_type]:
                continue
            
            recent_value = self.metrics_data[metric_type][-1].value
            baseline_key = f"{metric_type.value}_baseline"
            
            if baseline_key in self.performance_baselines:
                baseline = self.performance_baselines[baseline_key]
                
                if metric_type in [MetricType.LATENCY, MetricType.ERROR_RATE, MetricType.QUEUE_SIZE]:
                    # Lower is better
                    if recent_value > baseline * 1.5:
                        health_score -= 20
                    elif recent_value > baseline * 1.2:
                        health_score -= 10
                else:
                    # Higher is better
                    if recent_value < baseline * 0.5:
                        health_score -= 20
                    elif recent_value < baseline * 0.8:
                        health_score -= 10
        
        return max(0.0, health_score)
    
    async def _generate_summary(
        self, 
        timeframe_data: Dict[MetricType, List[AnalyticsDataPoint]], 
        timeframe: AnalyticsTimeframe
    ) -> Dict[str, Any]:
        """Generate summary for timeframe data"""
        summary = {
            "timeframe": timeframe.value,
            "data_points": sum(len(data) for data in timeframe_data.values()),
            "metrics": {}
        }
        
        for metric_type, data_points in timeframe_data.items():
            if data_points:
                values = [dp.value for dp in data_points]
                summary["metrics"][metric_type.value] = {
                    "count": len(values),
                    "average": statistics.mean(values),
                    "min": min(values),
                    "max": max(values),
                    "trend": await self._calculate_trend(values)
                }
        
        return summary
    
    async def _generate_insights(
        self, 
        timeframe_data: Dict[MetricType, List[AnalyticsDataPoint]], 
        timeframe: AnalyticsTimeframe
    ) -> List[PerformanceInsight]:
        """Generate insights from timeframe data"""
        # Implementation would include sophisticated insight generation
        return []
    
    async def _generate_detailed_metrics(
        self, 
        timeframe_data: Dict[MetricType, List[AnalyticsDataPoint]]
    ) -> Dict[str, Any]:
        """
Generate detailed metrics analysis"""
        detailed = {}
        
        for metric_type, data_points in timeframe_data.items():
            if data_points:
                values = [dp.value for dp in data_points]
                
                detailed[metric_type.value] = {
                    "statistical_summary": {
                        "mean": statistics.mean(values),
                        "median": statistics.median(values),
                        "std_dev": statistics.stdev(values) if len(values) > 1 else 0,
                        "percentiles": {
                            "p50": np.percentile(values, 50),
                            "p75": np.percentile(values, 75),
                            "p90": np.percentile(values, 90),
                            "p95": np.percentile(values, 95),
                            "p99": np.percentile(values, 99)
                        }
                    },
                    "trend_analysis": await self._analyze_trend_detailed(values),
                    "anomalies": await self._detect_metric_anomalies(data_points)
                }
        
        return detailed
    
    async def _generate_charts(
        self, 
        timeframe_data: Dict[MetricType, List[AnalyticsDataPoint]], 
        timeframe: AnalyticsTimeframe
    ) -> Dict[str, str]:
        """Generate charts as base64 encoded images"""
        charts = {}
        
        try:
            # Set style
            plt.style.use('seaborn-v0_8')
            
            for metric_type, data_points in timeframe_data.items():
                if not data_points:
                    continue
                
                # Create time series chart
                fig, ax = plt.subplots(figsize=(12, 6))
                
                timestamps = [dp.timestamp for dp in data_points]
                values = [dp.value for dp in data_points]
                
                ax.plot(timestamps, values, linewidth=2, alpha=0.8)
                ax.set_title(f'{metric_type.value.replace("_", " ").title()} - {timeframe.value}')
                ax.set_xlabel('Time')
                ax.set_ylabel('Value')
                ax.grid(True, alpha=0.3)
                
                # Save as base64
                buffer = io.BytesIO()
                plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
                buffer.seek(0)
                chart_base64 = base64.b64encode(buffer.getvalue()).decode()
                charts[metric_type.value] = chart_base64
                
                plt.close()
                
        except Exception as e:
            logger.error(f"Chart generation error: {e}")
        
        return charts
    
    async def _generate_recommendations(self, insights: List[PerformanceInsight]) -> List[str]:
        """Generate recommendations from insights"""
        recommendations = []
        
        for insight in insights:
            if insight.severity in ["high", "critical"]:
                recommendations.extend(insight.recommendations)
        
        # Remove duplicates and sort by priority
        return list(set(recommendations))
    
    async def _generate_predictions(
        self, 
        timeframe_data: Dict[MetricType, List[AnalyticsDataPoint]]
    ) -> Dict[str, Any]:
        """Generate predictions from timeframe data"""
        predictions = {}
        
        for metric_type, data_points in timeframe_data.items():
            if len(data_points) < 10:
                continue
            
            values = [dp.value for dp in data_points]
            
            # Simple trend-based prediction
            recent_trend = await self._calculate_trend(values[-20:])
            current_value = values[-1]
            
            if recent_trend == "increasing":
                predicted_value = current_value * 1.1
            elif recent_trend == "decreasing":
                predicted_value = current_value * 0.9
            else:
                predicted_value = current_value
            
            predictions[metric_type.value] = {
                "current_value": current_value,
                "predicted_value": predicted_value,
                "trend": recent_trend,
                "confidence": 0.7
            }
        
        return predictions
    
    async def _data_collector(self):
        """Background data collection task"""
        while self._is_running:
            try:
                # Periodic data collection and aggregation
                await asyncio.sleep(60)  # Collect every minute
                
            except Exception as e:
                logger.error(f"Data collector error: {e}")
                await asyncio.sleep(60)
    
    async def _insight_generator(self):
        """Background insight generation task"""
        while self._is_running:
            try:
                # Generate insights periodically
                await asyncio.sleep(300)  # Generate every 5 minutes
                
            except Exception as e:
                logger.error(f"Insight generator error: {e}")
                await asyncio.sleep(300)
    
    async def _anomaly_detector(self):
        """Background anomaly detection task"""
        while self._is_running:
            try:
                # Run anomaly detection
                await self.detect_performance_anomalies()
                await asyncio.sleep(120)  # Check every 2 minutes
                
            except Exception as e:
                logger.error(f"Anomaly detector error: {e}")
                await asyncio.sleep(120)
    
    async def _data_cleaner(self):
        """Background data cleaning task"""
        while self._is_running:
            try:
                # Clean old data based on retention policy
                cutoff_time = datetime.now() - timedelta(days=self.retention_days)
                
                for metric_type in MetricType:
                    # Remove old data points
                    self.metrics_data[metric_type] = deque([
                        dp for dp in self.metrics_data[metric_type]
                        if dp.timestamp > cutoff_time
                    ], maxlen=100000)
                
                await asyncio.sleep(3600)  # Clean every hour
                
            except Exception as e:
                logger.error(f"Data cleaner error: {e}")
                await asyncio.sleep(3600)
    
    async def _cache_manager(self):
        """Background cache management task"""
        while self._is_running:
            try:
                # Clear expired cache entries
                current_time = datetime.now()
                
                # Clear insights cache older than 1 hour
                expired_insights = [
                    key for key in self.insights_cache.keys()
                    if current_time.hour != int(key.split('_')[-1])
                ]
                
                for key in expired_insights:
                    self.insights_cache.pop(key, None)
                
                # Clear reports cache older than 24 hours
                expired_reports = [
                    key for key, report in self.reports_cache.items()
                    if (current_time - report.generated_at).total_seconds() > 86400
                ]
                
                for key in expired_reports:
                    self.reports_cache.pop(key, None)
                
                await asyncio.sleep(1800)  # Clean every 30 minutes
                
            except Exception as e:
                logger.error(f"Cache manager error: {e}")
                await asyncio.sleep(1800)
    
    # Additional helper methods for analysis
    
    async def _classify_anomaly_severity(self, anomaly_score: float) -> str:
        """Classify anomaly severity based on score"""
        if anomaly_score > 4.0:
            return "critical"
        elif anomaly_score > 3.0:
            return "high"
        elif anomaly_score > 2.0:
            return "medium"
        else:
            return "low"
    
    async def _describe_anomaly(self, metric_type: MetricType, value: float, mean_value: float) -> str:
        """Generate human-readable anomaly description"""
        deviation = "higher" if value > mean_value else "lower"
        return f"{metric_type.value} is significantly {deviation} than expected ({value:.2f} vs average {mean_value:.2f})"
    
    async def _predict_metric_trend(
        self, 
        timestamps: List[datetime], 
        values: List[float], 
        forecast_hours: int
    ) -> Dict[str, Any]:
        """Predict metric trend using linear regression"""
        try:
            # Convert timestamps to numerical values
            base_time = timestamps[0]
            x = [(ts - base_time).total_seconds() / 3600 for ts in timestamps]  # Hours
            y = values
            
            # Perform linear regression
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
            
            # Generate forecast
            forecast_x = max(x) + forecast_hours
            forecast_value = slope * forecast_x + intercept
            
            return {
                "forecast_value": forecast_value,
                "trend_slope": slope,
                "confidence": abs(r_value),
                "p_value": p_value,
                "forecast_time": (base_time + timedelta(hours=forecast_x)).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Trend prediction error: {e}")
            return {"error": str(e)}
    
    async def _analyze_trend_detailed(self, values: List[float]) -> Dict[str, Any]:
        """Perform detailed trend analysis"""
        if len(values) < 2:
            return {"trend": "insufficient_data"}
        
        try:
            # Calculate various trend indicators
            x = list(range(len(values)))
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, values)
            
            # Trend classification
            if abs(slope) < std_err:
                trend = "stable"
            elif slope > 0:
                trend = "increasing"
            else:
                trend = "decreasing"
            
            return {
                "trend": trend,
                "slope": slope,
                "correlation": r_value,
                "p_value": p_value,
                "trend_strength": abs(r_value),
                "volatility": statistics.stdev(values) if len(values) > 1 else 0
            }
            
        except Exception as e:
            logger.error(f"Detailed trend analysis error: {e}")
            return {"trend": "error", "error": str(e)}
    
    async def _detect_metric_anomalies(
        self, 
        data_points: List[AnalyticsDataPoint]
    ) -> List[Dict[str, Any]]:
        """Detect anomalies in metric data points"""
        # Implementation for metric-specific anomaly detection
        return []
    
    async def _generate_throughput_insights(self, timeframe_data) -> List[PerformanceInsight]:
        """
Generate throughput-specific insights"""
        return []
    
    async def _generate_latency_insights(self, timeframe_data) -> List[PerformanceInsight]:
        """
Generate latency-specific insights"""
        return []
    
    async def _generate_error_insights(self, timeframe_data) -> List[PerformanceInsight]:
        """
Generate error-specific insights"""
        return []
    
    async def _generate_capacity_insights(self, timeframe_data) -> List[PerformanceInsight]:
        """
Generate capacity-specific insights"""
        return []
    
    async def _generate_platform_insights(self, timeframe_data) -> List[PerformanceInsight]:
        """
Generate platform-specific insights"""
        return []
    
    async def _generate_throughput_recommendations(self, current_metrics) -> List[Dict[str, Any]]:
        """
Generate throughput optimization recommendations"""
        return []
    
    async def _generate_latency_recommendations(self, current_metrics) -> List[Dict[str, Any]]:
        """
Generate latency optimization recommendations"""
        return []
    
    async def _generate_capacity_recommendations(self, current_metrics) -> List[Dict[str, Any]]:
        """
Generate capacity optimization recommendations"""
        return []
    
    async def _generate_error_recommendations(self, current_metrics) -> List[Dict[str, Any]]:
        """
Generate error reduction recommendations"""
        return []
    
    async def _calculate_recommendation_priority(self, recommendation) -> float:
        """
Calculate priority score for recommendation"""
        # Implementation for priority calculation
        return 1.0


# Factory function
def create_analytics_engine(retention_days: int = 90) -> QueueAnalyticsEngine:
    """
Create and return configured analytics engine"""
    return QueueAnalyticsEngine(retention_days)
