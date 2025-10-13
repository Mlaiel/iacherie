"""
Serving Analytics
Advanced analytics and insights for model serving performance

This module provides:
- Real-time serving performance analytics
- Model performance comparison and trending
- Resource utilization analysis
- Prediction quality monitoring
- Business impact measurement

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np
import pandas as pd
from collections import defaultdict, deque
import json

logger = logging.getLogger(__name__)

class AnalyticsMetric(Enum):
    LATENCY = "latency"
    THROUGHPUT = "throughput" 
    ERROR_RATE = "error_rate"
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    GPU_USAGE = "gpu_usage"
    ACCURACY = "accuracy"
    PREDICTION_CONFIDENCE = "prediction_confidence"
    BUSINESS_VALUE = "business_value"

@dataclass
class ServingMetrics:
    """Serving metrics data point"""
    timestamp: datetime
    endpoint_id: str
    model_id: str
    model_version: str
    metrics: Dict[str, float]
    request_count: int
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class AnalyticsReport:
    """Analytics report structure"""
    report_id: str
    report_type: str
    time_range: Tuple[datetime, datetime]
    summary_metrics: Dict[str, Any]
    detailed_analysis: Dict[str, Any]
    insights: List[str]
    recommendations: List[str]
    generated_at: datetime

class ServingAnalytics:
    """
    Advanced analytics engine for model serving infrastructure
    Provides comprehensive insights into serving performance and quality
    """
    
    def __init__(self, retention_days: int = 30):
        self.metrics_buffer: deque = deque(maxlen=10000)
        self.aggregated_metrics: Dict[str, Dict[str, Any]] = {}
        self.retention_days = retention_days
        self.analytics_cache: Dict[str, Any] = {}
        self.alert_thresholds: Dict[str, float] = {
            "latency_p95_ms": 1000,
            "error_rate_percent": 5.0,
            "cpu_usage_percent": 80.0,
            "memory_usage_percent": 85.0
        }
        
    async def record_serving_metrics(
        self,
        endpoint_id: str,
        model_id: str,
        model_version: str,
        metrics: Dict[str, float],
        request_count: int = 1,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Record serving metrics for analysis
        
        Args:
            endpoint_id: Model endpoint identifier
            model_id: Model identifier
            model_version: Model version
            metrics: Performance metrics
            request_count: Number of requests in this measurement
            metadata: Additional metadata
        """
        try:
            serving_metric = ServingMetrics(
                timestamp=datetime.utcnow(),
                endpoint_id=endpoint_id,
                model_id=model_id,
                model_version=model_version,
                metrics=metrics,
                request_count=request_count,
                metadata=metadata or {}
            )
            
            self.metrics_buffer.append(serving_metric)
            
            # Update aggregated metrics
            await self._update_aggregated_metrics(serving_metric)
            
            # Check for alerts
            await self._check_alert_conditions(serving_metric)
            
            logger.debug(f"Recorded serving metrics for {endpoint_id}")
            
        except Exception as e:
            logger.error(f"Failed to record serving metrics: {e}")
    
    async def get_real_time_dashboard(
        self,
        time_window_minutes: int = 15
    ) -> Dict[str, Any]:
        """
        Get real-time dashboard data
        
        Args:
            time_window_minutes: Time window for real-time metrics
            
        Returns:
            dashboard_data: Real-time dashboard metrics
        """
        try:
            cutoff_time = datetime.utcnow() - timedelta(minutes=time_window_minutes)
            
            # Filter recent metrics
            recent_metrics = [
                m for m in self.metrics_buffer
                if m.timestamp >= cutoff_time
            ]
            
            if not recent_metrics:
                return {"message": "No recent metrics available"}
            
            # Calculate real-time statistics
            dashboard = {
                "time_window_minutes": time_window_minutes,
                "last_updated": datetime.utcnow().isoformat(),
                "total_requests": sum(m.request_count for m in recent_metrics),
                "active_endpoints": len(set(m.endpoint_id for m in recent_metrics)),
                "active_models": len(set(m.model_id for m in recent_metrics)),
                "performance_summary": {},
                "endpoint_breakdown": {},
                "alerts": []
            }
            
            # Performance summary
            all_latencies = [m.metrics.get("latency_ms", 0) for m in recent_metrics if "latency_ms" in m.metrics]
            all_error_rates = [m.metrics.get("error_rate", 0) for m in recent_metrics if "error_rate" in m.metrics]
            all_throughputs = [m.metrics.get("throughput_rps", 0) for m in recent_metrics if "throughput_rps" in m.metrics]
            
            if all_latencies:
                dashboard["performance_summary"]["latency"] = {
                    "mean_ms": np.mean(all_latencies),
                    "p50_ms": np.percentile(all_latencies, 50),
                    "p95_ms": np.percentile(all_latencies, 95),
                    "p99_ms": np.percentile(all_latencies, 99)
                }
            
            if all_error_rates:
                dashboard["performance_summary"]["error_rate"] = {
                    "mean_percent": np.mean(all_error_rates) * 100,
                    "max_percent": np.max(all_error_rates) * 100
                }
            
            if all_throughputs:
                dashboard["performance_summary"]["throughput"] = {
                    "total_rps": np.sum(all_throughputs),
                    "mean_rps": np.mean(all_throughputs),
                    "max_rps": np.max(all_throughputs)
                }
            
            # Endpoint breakdown
            endpoint_metrics = defaultdict(list)
            for metric in recent_metrics:
                endpoint_metrics[metric.endpoint_id].append(metric)
            
            for endpoint_id, metrics_list in endpoint_metrics.items():
                endpoint_latencies = [m.metrics.get("latency_ms", 0) for m in metrics_list if "latency_ms" in m.metrics]
                endpoint_requests = sum(m.request_count for m in metrics_list)
                
                dashboard["endpoint_breakdown"][endpoint_id] = {
                    "request_count": endpoint_requests,
                    "avg_latency_ms": np.mean(endpoint_latencies) if endpoint_latencies else 0,
                    "model_id": metrics_list[0].model_id,
                    "model_version": metrics_list[0].model_version
                }
            
            # Check for alerts
            dashboard["alerts"] = await self._get_active_alerts(recent_metrics)
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Failed to get real-time dashboard: {e}")
            raise
    
    async def generate_performance_report(
        self,
        start_time: datetime,
        end_time: datetime,
        model_ids: Optional[List[str]] = None
    ) -> AnalyticsReport:
        """
        Generate comprehensive performance report
        
        Args:
            start_time: Report start time
            end_time: Report end time
            model_ids: Specific model IDs to include (None for all)
            
        Returns:
            analytics_report: Comprehensive performance report
        """
        try:
            report_id = f"perf_report_{int(datetime.utcnow().timestamp())}"
            
            # Filter metrics by time range and models
            filtered_metrics = [
                m for m in self.metrics_buffer
                if start_time <= m.timestamp <= end_time and
                (model_ids is None or m.model_id in model_ids)
            ]
            
            if not filtered_metrics:
                return AnalyticsReport(
                    report_id=report_id,
                    report_type="performance",
                    time_range=(start_time, end_time),
                    summary_metrics={},
                    detailed_analysis={},
                    insights=["No data available for the specified time range"],
                    recommendations=[],
                    generated_at=datetime.utcnow()
                )
            
            # Summary metrics
            summary_metrics = await self._calculate_summary_metrics(filtered_metrics)
            
            # Detailed analysis
            detailed_analysis = {
                "model_comparison": await self._analyze_model_performance(filtered_metrics),
                "temporal_trends": await self._analyze_temporal_trends(filtered_metrics),
                "resource_utilization": await self._analyze_resource_utilization(filtered_metrics),
                "quality_metrics": await self._analyze_quality_metrics(filtered_metrics)
            }
            
            # Generate insights
            insights = await self._generate_performance_insights(summary_metrics, detailed_analysis)
            
            # Generate recommendations
            recommendations = await self._generate_performance_recommendations(
                summary_metrics, detailed_analysis, insights
            )
            
            report = AnalyticsReport(
                report_id=report_id,
                report_type="performance",
                time_range=(start_time, end_time),
                summary_metrics=summary_metrics,
                detailed_analysis=detailed_analysis,
                insights=insights,
                recommendations=recommendations,
                generated_at=datetime.utcnow()
            )
            
            logger.info(f"Generated performance report {report_id}")
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate performance report: {e}")
            raise
    
    async def analyze_model_comparison(
        self,
        model_ids: List[str],
        time_window_hours: int = 24,
        metrics_to_compare: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Compare performance across multiple models
        
        Args:
            model_ids: List of model IDs to compare
            time_window_hours: Time window for comparison
            metrics_to_compare: Specific metrics to compare
            
        Returns:
            comparison_analysis: Model comparison results
        """
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=time_window_hours)
            
            if metrics_to_compare is None:
                metrics_to_compare = ["latency_ms", "error_rate", "throughput_rps", "accuracy"]
            
            comparison_data = {}
            
            for model_id in model_ids:
                model_metrics = [
                    m for m in self.metrics_buffer
                    if m.model_id == model_id and m.timestamp >= cutoff_time
                ]
                
                if not model_metrics:
                    comparison_data[model_id] = {"status": "no_data"}
                    continue
                
                model_analysis = {}
                
                for metric_name in metrics_to_compare:
                    metric_values = [
                        m.metrics.get(metric_name, 0) for m in model_metrics
                        if metric_name in m.metrics
                    ]
                    
                    if metric_values:
                        model_analysis[metric_name] = {
                            "mean": np.mean(metric_values),
                            "std": np.std(metric_values),
                            "min": np.min(metric_values),
                            "max": np.max(metric_values),
                            "p95": np.percentile(metric_values, 95),
                            "sample_count": len(metric_values)
                        }
                
                model_analysis["total_requests"] = sum(m.request_count for m in model_metrics)
                model_analysis["active_endpoints"] = len(set(m.endpoint_id for m in model_metrics))
                
                comparison_data[model_id] = model_analysis
            
            # Generate comparison insights
            insights = await self._generate_comparison_insights(comparison_data, metrics_to_compare)
            
            return {
                "comparison_data": comparison_data,
                "metrics_compared": metrics_to_compare,
                "time_window_hours": time_window_hours,
                "insights": insights,
                "best_performers": await self._identify_best_performers(comparison_data, metrics_to_compare)
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze model comparison: {e}")
            raise
    
    async def get_business_impact_metrics(
        self,
        time_window_hours: int = 24
    ) -> Dict[str, Any]:
        """
        Calculate business impact metrics from serving performance
        
        Args:
            time_window_hours: Time window for analysis
            
        Returns:
            business_metrics: Business impact analysis
        """
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=time_window_hours)
            
            recent_metrics = [
                m for m in self.metrics_buffer
                if m.timestamp >= cutoff_time
            ]
            
            if not recent_metrics:
                return {"message": "No recent data for business impact analysis"}
            
            total_requests = sum(m.request_count for m in recent_metrics)
            
            # Calculate SLA compliance
            latencies = [m.metrics.get("latency_ms", 0) for m in recent_metrics if "latency_ms" in m.metrics]
            sla_latency_threshold = 500  # 500ms SLA
            sla_compliance = (len([l for l in latencies if l <= sla_latency_threshold]) / len(latencies) * 100) if latencies else 0
            
            # Calculate availability
            error_rates = [m.metrics.get("error_rate", 0) for m in recent_metrics if "error_rate" in m.metrics]
            availability = ((1 - np.mean(error_rates)) * 100) if error_rates else 100
            
            # Calculate cost efficiency
            cpu_usages = [m.metrics.get("cpu_usage", 0) for m in recent_metrics if "cpu_usage" in m.metrics]
            avg_cpu_usage = np.mean(cpu_usages) if cpu_usages else 0
            cost_efficiency = (total_requests / max(avg_cpu_usage, 1)) if avg_cpu_usage > 0 else 0
            
            # Calculate user experience score
            prediction_confidences = [
                m.metrics.get("prediction_confidence", 0.5) for m in recent_metrics 
                if "prediction_confidence" in m.metrics
            ]
            user_experience_score = np.mean(prediction_confidences) * 100 if prediction_confidences else 50
            
            business_metrics = {
                "time_window_hours": time_window_hours,
                "total_requests_served": total_requests,
                "sla_compliance_percent": sla_compliance,
                "availability_percent": availability,
                "cost_efficiency_score": cost_efficiency,
                "user_experience_score": user_experience_score,
                "revenue_impact": {
                    "requests_served": total_requests,
                    "estimated_revenue_per_request": 0.01,  # $0.01 per request estimate
                    "total_estimated_revenue": total_requests * 0.01
                },
                "quality_metrics": {
                    "avg_prediction_confidence": np.mean(prediction_confidences) if prediction_confidences else 0.5,
                    "accuracy_score": np.mean([
                        m.metrics.get("accuracy", 0.8) for m in recent_metrics 
                        if "accuracy" in m.metrics
                    ]) if recent_metrics else 0.8
                }
            }
            
            return business_metrics
            
        except Exception as e:
            logger.error(f"Failed to get business impact metrics: {e}")
            raise
    
    async def _update_aggregated_metrics(self, serving_metric: ServingMetrics) -> None:
        """Update aggregated metrics storage"""
        try:
            key = f"{serving_metric.model_id}_{serving_metric.model_version}"
            
            if key not in self.aggregated_metrics:
                self.aggregated_metrics[key] = {
                    "model_id": serving_metric.model_id,
                    "model_version": serving_metric.model_version,
                    "first_seen": serving_metric.timestamp,
                    "last_updated": serving_metric.timestamp,
                    "total_requests": 0,
                    "metrics_history": defaultdict(list)
                }
            
            agg_data = self.aggregated_metrics[key]
            agg_data["last_updated"] = serving_metric.timestamp
            agg_data["total_requests"] += serving_metric.request_count
            
            # Store metric values for trending
            for metric_name, value in serving_metric.metrics.items():
                agg_data["metrics_history"][metric_name].append({
                    "timestamp": serving_metric.timestamp,
                    "value": value
                })
                
                # Keep only recent history (last 1000 points)
                if len(agg_data["metrics_history"][metric_name]) > 1000:
                    agg_data["metrics_history"][metric_name] = \
                        agg_data["metrics_history"][metric_name][-1000:]
            
        except Exception as e:
            logger.error(f"Failed to update aggregated metrics: {e}")
    
    async def _check_alert_conditions(self, serving_metric: ServingMetrics) -> None:
        """Check if metrics trigger any alerts"""
        try:
            alerts = []
            
            for metric_name, value in serving_metric.metrics.items():
                threshold_key = f"{metric_name}_threshold"
                if threshold_key in self.alert_thresholds:
                    threshold = self.alert_thresholds[threshold_key]
                    if value > threshold:
                        alerts.append(f"{metric_name} exceeded threshold: {value} > {threshold}")
            
            if alerts:
                logger.warning(f"Alerts triggered for {serving_metric.endpoint_id}: {alerts}")
            
        except Exception as e:
            logger.error(f"Failed to check alert conditions: {e}")
    
    async def _calculate_summary_metrics(self, metrics: List[ServingMetrics]) -> Dict[str, Any]:
        """Calculate summary metrics from filtered data"""
        total_requests = sum(m.request_count for m in metrics)
        unique_models = len(set(m.model_id for m in metrics))
        unique_endpoints = len(set(m.endpoint_id for m in metrics))
        
        # Aggregate all metric values
        all_latencies = [m.metrics.get("latency_ms", 0) for m in metrics if "latency_ms" in m.metrics]
        all_error_rates = [m.metrics.get("error_rate", 0) for m in metrics if "error_rate" in m.metrics]
        all_throughputs = [m.metrics.get("throughput_rps", 0) for m in metrics if "throughput_rps" in m.metrics]
        
        summary = {
            "total_requests": total_requests,
            "unique_models": unique_models,
            "unique_endpoints": unique_endpoints,
            "time_span_hours": (max(m.timestamp for m in metrics) - min(m.timestamp for m in metrics)).total_seconds() / 3600
        }
        
        if all_latencies:
            summary["latency_summary"] = {
                "mean_ms": np.mean(all_latencies),
                "p50_ms": np.percentile(all_latencies, 50),
                "p95_ms": np.percentile(all_latencies, 95),
                "p99_ms": np.percentile(all_latencies, 99)
            }
        
        if all_error_rates:
            summary["error_summary"] = {
                "mean_rate": np.mean(all_error_rates),
                "max_rate": np.max(all_error_rates)
            }
        
        if all_throughputs:
            summary["throughput_summary"] = {
                "total_rps": np.sum(all_throughputs),
                "mean_rps": np.mean(all_throughputs),
                "peak_rps": np.max(all_throughputs)
            }
        
        return summary
    
    async def _analyze_model_performance(self, metrics: List[ServingMetrics]) -> Dict[str, Any]:
        """Analyze performance by model"""
        model_data = defaultdict(list)
        
        for metric in metrics:
            model_data[metric.model_id].append(metric)
        
        analysis = {}
        for model_id, model_metrics in model_data.items():
            latencies = [m.metrics.get("latency_ms", 0) for m in model_metrics if "latency_ms" in m.metrics]
            requests = sum(m.request_count for m in model_metrics)
            
            analysis[model_id] = {
                "total_requests": requests,
                "avg_latency_ms": np.mean(latencies) if latencies else 0,
                "p95_latency_ms": np.percentile(latencies, 95) if latencies else 0,
                "unique_versions": len(set(m.model_version for m in model_metrics))
            }
        
        return analysis
    
    async def _analyze_temporal_trends(self, metrics: List[ServingMetrics]) -> Dict[str, Any]:
        """Analyze trends over time"""
        # Group metrics by hour
        hourly_data = defaultdict(list)
        
        for metric in metrics:
            hour_key = metric.timestamp.replace(minute=0, second=0, microsecond=0)
            hourly_data[hour_key].append(metric)
        
        trends = {}
        for hour, hour_metrics in hourly_data.items():
            latencies = [m.metrics.get("latency_ms", 0) for m in hour_metrics if "latency_ms" in m.metrics]
            requests = sum(m.request_count for m in hour_metrics)
            
            trends[hour.isoformat()] = {
                "total_requests": requests,
                "avg_latency_ms": np.mean(latencies) if latencies else 0,
                "unique_models": len(set(m.model_id for m in hour_metrics))
            }
        
        return trends
    
    async def _analyze_resource_utilization(self, metrics: List[ServingMetrics]) -> Dict[str, Any]:
        """Analyze resource utilization patterns"""
        cpu_usages = [m.metrics.get("cpu_usage", 0) for m in metrics if "cpu_usage" in m.metrics]
        memory_usages = [m.metrics.get("memory_usage", 0) for m in metrics if "memory_usage" in m.metrics]
        gpu_usages = [m.metrics.get("gpu_usage", 0) for m in metrics if "gpu_usage" in m.metrics]
        
        analysis = {}
        
        if cpu_usages:
            analysis["cpu"] = {
                "avg_usage_percent": np.mean(cpu_usages),
                "peak_usage_percent": np.max(cpu_usages),
                "utilization_variance": np.var(cpu_usages)
            }
        
        if memory_usages:
            analysis["memory"] = {
                "avg_usage_percent": np.mean(memory_usages),
                "peak_usage_percent": np.max(memory_usages)
            }
        
        if gpu_usages:
            analysis["gpu"] = {
                "avg_usage_percent": np.mean(gpu_usages),
                "peak_usage_percent": np.max(gpu_usages)
            }
        
        return analysis
    
    async def _analyze_quality_metrics(self, metrics: List[ServingMetrics]) -> Dict[str, Any]:
        """Analyze prediction quality metrics"""
        accuracies = [m.metrics.get("accuracy", 0) for m in metrics if "accuracy" in m.metrics]
        confidences = [m.metrics.get("prediction_confidence", 0) for m in metrics if "prediction_confidence" in m.metrics]
        
        analysis = {}
        
        if accuracies:
            analysis["accuracy"] = {
                "mean": np.mean(accuracies),
                "std": np.std(accuracies),
                "min": np.min(accuracies),
                "max": np.max(accuracies)
            }
        
        if confidences:
            analysis["prediction_confidence"] = {
                "mean": np.mean(confidences),
                "low_confidence_ratio": len([c for c in confidences if c < 0.7]) / len(confidences)
            }
        
        return analysis
    
    async def _generate_performance_insights(
        self,
        summary_metrics: Dict[str, Any],
        detailed_analysis: Dict[str, Any]
    ) -> List[str]:
        """Generate performance insights"""
        insights = []
        
        # Latency insights
        if "latency_summary" in summary_metrics:
            latency = summary_metrics["latency_summary"]
            if latency["p95_ms"] > 1000:
                insights.append("High P95 latency detected - consider optimization")
            elif latency["p95_ms"] < 100:
                insights.append("Excellent latency performance")
        
        # Throughput insights
        if "throughput_summary" in summary_metrics:
            throughput = summary_metrics["throughput_summary"]
            if throughput["peak_rps"] > throughput["mean_rps"] * 3:
                insights.append("High traffic variability - consider auto-scaling")
        
        # Model performance insights
        model_analysis = detailed_analysis.get("model_comparison", {})
        if len(model_analysis) > 1:
            insights.append(f"Performance comparison available across {len(model_analysis)} models")
        
        return insights
    
    async def _generate_performance_recommendations(
        self,
        summary_metrics: Dict[str, Any],
        detailed_analysis: Dict[str, Any],
        insights: List[str]
    ) -> List[str]:
        """Generate performance recommendations"""
        recommendations = []
        
        # Latency recommendations
        if "latency_summary" in summary_metrics:
            latency = summary_metrics["latency_summary"]
            if latency["p95_ms"] > 500:
                recommendations.append("Consider implementing response caching to reduce latency")
                recommendations.append("Evaluate model optimization techniques")
        
        # Resource recommendations
        resource_analysis = detailed_analysis.get("resource_utilization", {})
        if "cpu" in resource_analysis and resource_analysis["cpu"]["avg_usage_percent"] > 80:
            recommendations.append("High CPU utilization - consider horizontal scaling")
        
        return recommendations
    
    async def _get_active_alerts(self, recent_metrics: List[ServingMetrics]) -> List[str]:
        """Get currently active alerts"""
        alerts = []
        
        # Check for high latency
        latencies = [m.metrics.get("latency_ms", 0) for m in recent_metrics if "latency_ms" in m.metrics]
        if latencies and np.percentile(latencies, 95) > self.alert_thresholds.get("latency_p95_ms", 1000):
            alerts.append("High P95 latency alert")
        
        # Check for high error rate
        error_rates = [m.metrics.get("error_rate", 0) for m in recent_metrics if "error_rate" in m.metrics]
        if error_rates and np.mean(error_rates) * 100 > self.alert_thresholds.get("error_rate_percent", 5):
            alerts.append("High error rate alert")
        
        return alerts
    
    async def _generate_comparison_insights(
        self,
        comparison_data: Dict[str, Any],
        metrics_compared: List[str]
    ) -> List[str]:
        """Generate insights from model comparison"""
        insights = []
        
        valid_models = {k: v for k, v in comparison_data.items() if v.get("status") != "no_data"}
        
        if len(valid_models) < 2:
            return ["Insufficient data for meaningful comparison"]
        
        # Find best performer for each metric
        for metric in metrics_compared:
            values = {}
            for model_id, data in valid_models.items():
                if metric in data:
                    values[model_id] = data[metric]["mean"]
            
            if values:
                best_model = min(values, key=values.get) if metric in ["latency_ms", "error_rate"] else max(values, key=values.get)
                insights.append(f"Best {metric} performance: {best_model}")
        
        return insights
    
    async def _identify_best_performers(
        self,
        comparison_data: Dict[str, Any],
        metrics_compared: List[str]
    ) -> Dict[str, str]:
        """Identify best performing models per metric"""
        best_performers = {}
        
        valid_models = {k: v for k, v in comparison_data.items() if v.get("status") != "no_data"}
        
        for metric in metrics_compared:
            values = {}
            for model_id, data in valid_models.items():
                if metric in data:
                    values[model_id] = data[metric]["mean"]
            
            if values:
                # Lower is better for latency and error_rate, higher is better for others
                best_model = (min(values, key=values.get) if metric in ["latency_ms", "error_rate"] 
                             else max(values, key=values.get))
                best_performers[metric] = best_model
        
        return best_performers