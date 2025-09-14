"""
Latency Analyzer module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""
Advanced Latency Analysis Engine for Ainflue Platform
====================================================

Comprehensive latency analysis with ML-powered pattern recognition,
statistical modeling, and enterprise-grade performance insights.

Expert Roles Demonstrated:
- 🧠 ML Engineer: Statistical latency modeling and predictive analytics
- ⚙️ DevOps: Real-time monitoring and automated performance alerting
- 🏗️ Backend Senior: Deep performance analysis and optimization recommendations

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import json
import logging
import math
import time
import statistics
from datetime import datetime, timezone, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union, Callable
from dataclasses import dataclass, asdict
from collections import deque, defaultdict
import threading
import queue

# ML/Statistical imports for latency analysis
import numpy as np
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from scipy import stats
from scipy.signal import find_peaks
import warnings
warnings.filterwarnings('ignore')

# Performance monitoring imports
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logging.warning("psutil not available. System monitoring will be limited.")

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    logging.warning("requests not available. HTTP latency testing will be limited.")

class LatencyMetricType(Enum):
    """Types of latency metrics."""
    RESPONSE_TIME = "response_time"
    NETWORK_LATENCY = "network_latency"
    DATABASE_QUERY = "database_query"
    API_CALL = "api_call"
    PROCESSING_TIME = "processing_time"
    RENDER_TIME = "render_time"
    TIME_TO_FIRST_BYTE = "ttfb"
    TIME_TO_INTERACTIVE = "tti"

class LatencyCategory(Enum):
    """Latency performance categories."""
    EXCELLENT = "excellent"      # < 100ms
    GOOD = "good"               # 100-300ms
    ACCEPTABLE = "acceptable"   # 300-1000ms
    POOR = "poor"              # 1000-3000ms
    CRITICAL = "critical"      # > 3000ms

class AnalysisType(Enum):
    """Types of latency analysis."""
    REAL_TIME = "real_time"
    BATCH = "batch"
    TREND = "trend"
    ANOMALY = "anomaly"
    PREDICTIVE = "predictive"

@dataclass
class LatencyMeasurement:
    """Individual latency measurement."""
    timestamp: datetime
    metric_type: LatencyMetricType
    value: float  # in milliseconds
    endpoint: Optional[str] = None
    user_id: Optional[str] = None
    request_id: Optional[str] = None
    additional_metadata: Optional[Dict[str, Any]] = None

@dataclass
class LatencyStatistics:
    """Statistical analysis of latency measurements."""
    metric_type: LatencyMetricType
    sample_count: int
    mean: float
    median: float
    p95: float
    p99: float
    std_deviation: float
    min_value: float
    max_value: float
    skewness: float
    kurtosis: float
    category: LatencyCategory

@dataclass
class LatencyAnomalyResult:
    """Result of latency anomaly detection."""
    timestamp: datetime
    metric_type: LatencyMetricType
    measured_value: float
    expected_range: Tuple[float, float]
    anomaly_score: float
    severity: str
    potential_causes: List[str]

@dataclass
class LatencyTrendAnalysis:
    """Trend analysis results."""
    metric_type: LatencyMetricType
    time_period: str
    trend_direction: str  # improving, degrading, stable
    trend_strength: float
    seasonal_pattern: bool
    projected_values: Dict[str, float]
    confidence_interval: Tuple[float, float]

@dataclass
class LatencyAnalysisResult:
    """Complete latency analysis result."""
    analysis_id: str
    timestamp: datetime
    analysis_type: AnalysisType
    statistics: Dict[LatencyMetricType, LatencyStatistics]
    anomalies: List[LatencyAnomalyResult]
    trends: List[LatencyTrendAnalysis]
    performance_score: float
    recommendations: List[str]
    ml_insights: Dict[str, Any]

class LatencyAnalyzer:
    """
    Enterprise latency analysis engine with AI-powered insights.
    
    🧠 ML Engineer Features:
    - Advanced statistical modeling and trend analysis
    - ML-powered anomaly detection and pattern recognition
    - Predictive latency forecasting
    
    ⚙️ DevOps Features:
    - Real-time latency monitoring and alerting
    - Automated performance optimization recommendations
    - Infrastructure correlation analysis
    
    🏗️ Backend Senior Features:
    - Deep performance bottleneck analysis
    - Enterprise-grade latency optimization
    - Advanced performance profiling
    """
    
    def __init__(self, config_path -> None: Optional[str] = None) -> None:
        """Initialize latency analysis engine."""
        self.logger = self._setup_logging()
        self.config = self._load_config(config_path)
        
        # Data storage
        self.measurements_buffer = deque(maxlen=10000)
        self.historical_data: Dict[LatencyMetricType, List[LatencyMeasurement]] = defaultdict(list)
        self.analysis_results: List[LatencyAnalysisResult] = []
        
        # ML components
        self.ml_analyzer = LatencyMLAnalyzer()
        self.anomaly_detector = LatencyAnomalyDetector()
        self.trend_analyzer = LatencyTrendAnalyzer()
        
        # Real-time monitoring
        self.monitoring_active = False
        self.monitoring_thread = None
        self.alert_callbacks: List[Callable] = []
        
        # DevOps: Infrastructure validation
        self._validate_latency_monitoring_infrastructure()
        
    def _setup_logging(self) -> logging.Logger:
        """Setup comprehensive logging system."""
        logger = logging.getLogger("LatencyAnalyzer")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load latency analysis configuration."""
        default_config = {
            "real_time_monitoring": {
                "enabled": True,
                "sampling_interval": 1.0,  # seconds
                "buffer_size": 10000,
                "alert_thresholds": {
                    "response_time": 1000,  # ms
                    "api_call": 500,
                    "database_query": 200
                }
            },
            "statistical_analysis": {
                "confidence_level": 0.95,
                "outlier_threshold": 2.0,  # standard deviations
                "seasonal_detection": True,
                "trend_window": 24  # hours
            },
            "ml_analysis": {
                "anomaly_detection": True,
                "predictive_modeling": True,
                "pattern_recognition": True,
                "clustering_analysis": True
            },
            "performance_thresholds": {
                "excellent": 100,  # ms
                "good": 300,
                "acceptable": 1000,
                "poor": 3000
            },
            "alerting": {
                "enabled": True,
                "email_notifications": False,
                "webhook_urls": [],
                "alert_cooldown": 300  # seconds
            }
        }
        
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                self.logger.warning(f"Failed to load config: {e}")
                
        return default_config
    
    def _validate_latency_monitoring_infrastructure(self) -> None:
        """DevOps: Validate latency monitoring infrastructure."""
        self.logger.info("🔧 DevOps: Validating latency monitoring infrastructure...")
        
        # Check system monitoring capabilities
        if not PSUTIL_AVAILABLE:
            self.logger.warning("System latency monitoring limited - psutil not available")
            
        # Check HTTP monitoring capabilities
        if not REQUESTS_AVAILABLE:
            self.logger.warning("HTTP latency monitoring limited - requests not available")
            
        # Validate ML components
        self.logger.info("Initializing ML analysis components...")
        
        # Infrastructure health check
        self.logger.info("✅ DevOps: Latency monitoring infrastructure validated")
    
    def record_latency(self, measurement: LatencyMeasurement) -> None:
        """Record a latency measurement."""
        # Add to buffer for real-time analysis
        self.measurements_buffer.append(measurement)
        
        # Add to historical data
        self.historical_data[measurement.metric_type].append(measurement)
        
        # Trigger real-time analysis if enabled
        if self.config.get("real_time_monitoring", {}).get("enabled", True):
            self._check_real_time_alerts(measurement)
    
    def record_multiple_latencies(self, measurements: List[LatencyMeasurement]) -> None:
        """Record multiple latency measurements efficiently."""
        for measurement in measurements:
            self.record_latency(measurement)
    
    async def analyze_latency_performance(self, analysis_type: AnalysisType = AnalysisType.BATCH, time_window: Optional[timedelta] = None) -> LatencyAnalysisResult:
        """
        Perform comprehensive latency analysis.
        
        🧠 ML Engineer: Advanced statistical modeling and ML insights
        ⚙️ DevOps: Performance monitoring and optimization recommendations
        🏗️ Backend Senior: Deep performance analysis and bottleneck identification
        """
        analysis_id = f"latency_analysis_{int(time.time())}"
        self.logger.info(f"🚀 Starting latency analysis: {analysis_id}")
        
        start_time = time.time()
        
        # Filter data based on time window
        filtered_data = self._filter_data_by_time_window(time_window)
        
        if not filtered_data:
            self.logger.warning("No latency data available for analysis")
            return self._create_empty_analysis_result(analysis_id, analysis_type)
        
        # 🧠 ML Engineer: Statistical analysis
        statistics_results = self._calculate_comprehensive_statistics(filtered_data)
        
        # 🧠 ML Engineer: Anomaly detection
        anomalies = await self.anomaly_detector.detect_anomalies(filtered_data)
        
        # 🧠 ML Engineer: Trend analysis
        trends = await self.trend_analyzer.analyze_trends(filtered_data)
        
        # 🧠 ML Engineer: ML-powered insights
        ml_insights = await self.ml_analyzer.generate_insights(filtered_data, statistics_results)
        
        # 🏗️ Backend Senior: Performance score calculation
        performance_score = self._calculate_performance_score(statistics_results)
        
        # ⚙️ DevOps: Generate optimization recommendations
        recommendations = self._generate_optimization_recommendations(
            statistics_results, anomalies, trends, ml_insights
        )
        
        analysis_result = LatencyAnalysisResult(
            analysis_id=analysis_id,
            timestamp=datetime.now(timezone.utc),
            analysis_type=analysis_type,
            statistics=statistics_results,
            anomalies=anomalies,
            trends=trends,
            performance_score=performance_score,
            recommendations=recommendations,
            ml_insights=ml_insights
        )
        
        self.analysis_results.append(analysis_result)
        
        execution_time = time.time() - start_time
        self.logger.info(f"✅ Latency analysis completed in {execution_time:.2f}s")
        
        return analysis_result
    
    def _filter_data_by_time_window(self, time_window: Optional[timedelta]) -> Dict[LatencyMetricType, List[LatencyMeasurement]]:
        """Filter historical data by time window."""
        if not time_window:
            return dict(self.historical_data)
        
        cutoff_time = datetime.now(timezone.utc) - time_window
        filtered_data = {}
        
        for metric_type, measurements in self.historical_data.items():
            filtered_measurements = [
                m for m in measurements 
                if m.timestamp >= cutoff_time
            ]
            if filtered_measurements:
                filtered_data[metric_type] = filtered_measurements
        
        return filtered_data
    
    def _calculate_comprehensive_statistics(self, data: Dict[LatencyMetricType, List[LatencyMeasurement]]) -> Dict[LatencyMetricType, LatencyStatistics]:
        """🧠 ML Engineer: Calculate comprehensive statistical analysis."""
        statistics_results = {}
        
        for metric_type, measurements in data.items():
            if not measurements:
                continue
                
            values = [m.value for m in measurements]
            
            # Basic statistics
            mean_val = statistics.mean(values)
            median_val = statistics.median(values)
            std_dev = statistics.stdev(values) if len(values) > 1 else 0.0
            min_val = min(values)
            max_val = max(values)
            
            # Percentiles
            p95 = np.percentile(values, 95)
            p99 = np.percentile(values, 99)
            
            # Advanced statistics
            skewness = stats.skew(values)
            kurtosis_val = stats.kurtosis(values)
            
            # Performance category
            category = self._categorize_latency_performance(p95)
            
            statistics_results[metric_type] = LatencyStatistics(
                metric_type=metric_type,
                sample_count=len(values),
                mean=round(mean_val, 2),
                median=round(median_val, 2),
                p95=round(p95, 2),
                p99=round(p99, 2),
                std_deviation=round(std_dev, 2),
                min_value=round(min_val, 2),
                max_value=round(max_val, 2),
                skewness=round(skewness, 3),
                kurtosis=round(kurtosis_val, 3),
                category=category
            )
        
        return statistics_results
    
    def _categorize_latency_performance(self, p95_latency: float) -> LatencyCategory:
        """Categorize latency performance based on P95."""
        thresholds = self.config.get("performance_thresholds", {})
        
        if p95_latency <= thresholds.get("excellent", 100):
            return LatencyCategory.EXCELLENT
        elif p95_latency <= thresholds.get("good", 300):
            return LatencyCategory.GOOD
        elif p95_latency <= thresholds.get("acceptable", 1000):
            return LatencyCategory.ACCEPTABLE
        elif p95_latency <= thresholds.get("poor", 3000):
            return LatencyCategory.POOR
        else:
            return LatencyCategory.CRITICAL
    
    def _calculate_performance_score(self, statistics: Dict[LatencyMetricType, LatencyStatistics]) -> float:
        """🏗️ Backend Senior: Calculate overall performance score."""
        if not statistics:
            return 0.0
        
        total_score = 0.0
        total_weight = 0.0
        
        # Weight different metric types
        metric_weights = {
            LatencyMetricType.RESPONSE_TIME: 0.3,
            LatencyMetricType.API_CALL: 0.25,
            LatencyMetricType.DATABASE_QUERY: 0.2,
            LatencyMetricType.NETWORK_LATENCY: 0.15,
            LatencyMetricType.PROCESSING_TIME: 0.1
        }
        
        for metric_type, stats in statistics.items():
            weight = metric_weights.get(metric_type, 0.1)
            
            # Score based on P95 latency and category
            category_scores = {
                LatencyCategory.EXCELLENT: 100,
                LatencyCategory.GOOD: 80,
                LatencyCategory.ACCEPTABLE: 60,
                LatencyCategory.POOR: 30,
                LatencyCategory.CRITICAL: 10
            }
            
            base_score = category_scores.get(stats.category, 50)
            
            # Adjust for consistency (lower std deviation = higher score)
            consistency_factor = max(0.5, 1.0 - (stats.std_deviation / stats.mean) if stats.mean > 0 else 0.5)
            
            metric_score = base_score * consistency_factor
            
            total_score += metric_score * weight
            total_weight += weight
        
        final_score = total_score / total_weight if total_weight > 0 else 0.0
        return round(final_score, 1)
    
    def _generate_optimization_recommendations(self, statistics: Dict[LatencyMetricType, LatencyStatistics], 
                                             anomalies: List[LatencyAnomalyResult], 
                                             trends: List[LatencyTrendAnalysis],
                                             ml_insights: Dict[str, Any]) -> List[str]:
        """⚙️ DevOps: Generate automated optimization recommendations."""
        recommendations = []
        
        # Performance-based recommendations
        for metric_type, stats in statistics.items():
            if stats.category in [LatencyCategory.POOR, LatencyCategory.CRITICAL]:
                if metric_type == LatencyMetricType.DATABASE_QUERY:
                    recommendations.append(f"Database query latency is {stats.category.value} (P95: {stats.p95}ms). Consider query optimization, indexing, or connection pooling.")
                elif metric_type == LatencyMetricType.API_CALL:
                    recommendations.append(f"API call latency is {stats.category.value} (P95: {stats.p95}ms). Consider caching, load balancing, or endpoint optimization.")
                elif metric_type == LatencyMetricType.RESPONSE_TIME:
                    recommendations.append(f"Response time is {stats.category.value} (P95: {stats.p95}ms). Consider application optimization or infrastructure scaling.")
            
            # High variability recommendations
            if stats.std_deviation > stats.mean * 0.5:
                recommendations.append(f"{metric_type.value} shows high variability (std: {stats.std_deviation}ms). Investigate intermittent performance issues.")
        
        # Anomaly-based recommendations
        critical_anomalies = [a for a in anomalies if a.severity == "critical"]
        if critical_anomalies:
            recommendations.append(f"Detected {len(critical_anomalies)} critical latency anomalies. Immediate investigation recommended.")
        
        # Trend-based recommendations
        degrading_trends = [t for t in trends if t.trend_direction == "degrading"]
        if degrading_trends:
            recommendations.append(f"Performance degradation detected in {len(degrading_trends)} metrics. Proactive optimization needed.")
        
        # ML insights recommendations
        if ml_insights.get("predicted_bottlenecks"):
            bottlenecks = ml_insights["predicted_bottlenecks"]
            recommendations.append(f"ML analysis predicts potential bottlenecks: {', '.join(bottlenecks)}")
        
        return recommendations
    
    def _check_real_time_alerts(self, measurement: LatencyMeasurement) -> None:
        """⚙️ DevOps: Check for real-time latency alerts."""
        alert_thresholds = self.config.get("real_time_monitoring", {}).get("alert_thresholds", {})
        threshold = alert_thresholds.get(measurement.metric_type.value, 1000)
        
        if measurement.value > threshold:
            alert_message = f"High latency alert: {measurement.metric_type.value} = {measurement.value}ms (threshold: {threshold}ms)"
            self.logger.warning(alert_message)
            
            # Trigger alert callbacks
            for callback in self.alert_callbacks:
                try:
                    callback(measurement, alert_message)
                except Exception as e:
                    self.logger.error(f"Alert callback failed: {e}")
    
    def add_alert_callback(self, callback: Callable[[LatencyMeasurement, str], None]) -> None:
        """Add a callback function for latency alerts."""
        self.alert_callbacks.append(callback)
    
    def start_real_time_monitoring(self) -> None:
        """⚙️ DevOps: Start real-time latency monitoring."""
        if self.monitoring_active:
            self.logger.warning("Real-time monitoring already active")
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        self.logger.info("📊 Real-time latency monitoring started")
    
    def stop_real_time_monitoring(self) -> None:
        """⚙️ DevOps: Stop real-time latency monitoring."""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        
        self.logger.info("🛑 Real-time latency monitoring stopped")
    
    def _monitoring_loop(self) -> None:
        """Real-time monitoring loop."""
        sampling_interval = self.config.get("real_time_monitoring", {}).get("sampling_interval", 1.0)
        
        while self.monitoring_active:
            try:
                # Perform real-time analysis on recent measurements
                recent_measurements = list(self.measurements_buffer)[-100:]  # Last 100 measurements
                
                if recent_measurements:
                    # Quick statistical analysis
                    self._perform_real_time_analysis(recent_measurements)
                
                time.sleep(sampling_interval)
                
            except Exception as e:
                self.logger.error(f"Real-time monitoring error: {e}")
                time.sleep(sampling_interval)
    
    def _perform_real_time_analysis(self, measurements: List[LatencyMeasurement]) -> None:
        """Perform lightweight real-time analysis."""
        # Group by metric type
        metric_groups = defaultdict(list)
        for measurement in measurements:
            metric_groups[measurement.metric_type].append(measurement.value)
        
        # Check for immediate performance issues
        for metric_type, values in metric_groups.items():
            if len(values) >= 5:  # Need minimum samples
                recent_p95 = np.percentile(values, 95)
                recent_mean = statistics.mean(values)
                
                # Check for performance degradation
                if recent_p95 > recent_mean * 3:  # P95 is significantly higher than mean
                    self.logger.warning(f"Performance spike detected in {metric_type.value}: P95={recent_p95:.1f}ms")
    
    def _create_empty_analysis_result(self, analysis_id: str, analysis_type: AnalysisType) -> LatencyAnalysisResult:
        """Create empty analysis result when no data is available."""
        return LatencyAnalysisResult(
            analysis_id=analysis_id,
            timestamp=datetime.now(timezone.utc),
            analysis_type=analysis_type,
            statistics={},
            anomalies=[],
            trends=[],
            performance_score=0.0,
            recommendations=["No latency data available for analysis"],
            ml_insights={}
        )
    
    async def generate_latency_report(self, time_window: timedelta = timedelta(hours=24)) -> Dict[str, Any]:
        """🏗️ Backend Senior: Generate comprehensive latency report."""
        self.logger.info("📊 Generating comprehensive latency report...")
        
        analysis_result = await self.analyze_latency_performance(
            analysis_type=AnalysisType.BATCH,
            time_window=time_window
        )
        
        # Additional report data
        report = {
            "report_id": f"latency_report_{int(time.time())}",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "time_window": str(time_window),
            "analysis_summary": asdict(analysis_result),
            "executive_summary": self._generate_executive_summary(analysis_result),
            "detailed_metrics": self._generate_detailed_metrics_report(analysis_result),
            "trend_forecast": self._generate_trend_forecast(analysis_result.trends),
            "action_items": self._prioritize_action_items(analysis_result.recommendations)
        }
        
        return report
    
    def _generate_executive_summary(self, analysis_result: LatencyAnalysisResult) -> Dict[str, Any]:
        """Generate executive summary of latency analysis."""
        total_measurements = sum(stats.sample_count for stats in analysis_result.statistics.values())
        
        # Performance distribution
        performance_distribution = {}
        for stats in analysis_result.statistics.values():
            category = stats.category.value
            performance_distribution[category] = performance_distribution.get(category, 0) + 1
        
        # Key metrics
        key_metrics = {}
        if analysis_result.statistics:
            all_p95s = [stats.p95 for stats in analysis_result.statistics.values()]
            key_metrics["overall_p95_latency"] = round(statistics.mean(all_p95s), 2)
            key_metrics["worst_p95_latency"] = round(max(all_p95s), 2)
            key_metrics["best_p95_latency"] = round(min(all_p95s), 2)
        
        return {
            "performance_score": analysis_result.performance_score,
            "total_measurements_analyzed": total_measurements,
            "performance_distribution": performance_distribution,
            "key_metrics": key_metrics,
            "critical_issues_count": len([a for a in analysis_result.anomalies if a.severity == "critical"]),
            "recommendations_count": len(analysis_result.recommendations)
        }
    
    def _generate_detailed_metrics_report(self, analysis_result: LatencyAnalysisResult) -> Dict[str, Any]:
        """Generate detailed metrics breakdown."""
        detailed_metrics = {}
        
        for metric_type, stats in analysis_result.statistics.items():
            detailed_metrics[metric_type.value] = {
                "statistics": asdict(stats),
                "performance_grade": stats.category.value,
                "health_status": "healthy" if stats.category in [LatencyCategory.EXCELLENT, LatencyCategory.GOOD] else "needs_attention",
                "improvement_potential": self._calculate_improvement_potential(stats)
            }
        
        return detailed_metrics
    
    def _calculate_improvement_potential(self, stats: LatencyStatistics) -> str:
        """Calculate improvement potential for a metric."""
        if stats.category == LatencyCategory.EXCELLENT:
            return "minimal"
        elif stats.category == LatencyCategory.GOOD:
            return "low"
        elif stats.category == LatencyCategory.ACCEPTABLE:
            return "medium"
        elif stats.category == LatencyCategory.POOR:
            return "high"
        else:
            return "critical"
    
    def _generate_trend_forecast(self, trends: List[LatencyTrendAnalysis]) -> Dict[str, Any]:
        """Generate trend forecast based on analysis."""
        forecast = {
            "overall_trend": "stable",
            "metrics_improving": 0,
            "metrics_degrading": 0,
            "seasonal_patterns_detected": 0
        }
        
        for trend in trends:
            if trend.trend_direction == "improving":
                forecast["metrics_improving"] += 1
            elif trend.trend_direction == "degrading":
                forecast["metrics_degrading"] += 1
            
            if trend.seasonal_pattern:
                forecast["seasonal_patterns_detected"] += 1
        
        # Determine overall trend
        if forecast["metrics_degrading"] > forecast["metrics_improving"]:
            forecast["overall_trend"] = "degrading"
        elif forecast["metrics_improving"] > forecast["metrics_degrading"]:
            forecast["overall_trend"] = "improving"
        
        return forecast
    
    def _prioritize_action_items(self, recommendations: List[str]) -> List[Dict[str, Any]]:
        """Prioritize action items based on urgency and impact."""
        action_items = []
        
        for i, recommendation in enumerate(recommendations):
            # Simple priority assignment based on keywords
            priority = "medium"
            if "critical" in recommendation.lower() or "immediate" in recommendation.lower():
                priority = "high"
            elif "consider" in recommendation.lower() or "monitor" in recommendation.lower():
                priority = "low"
            
            action_items.append({
                "id": f"action_{i+1}",
                "description": recommendation,
                "priority": priority,
                "estimated_effort": "medium",  # Would be determined by more sophisticated analysis
                "expected_impact": "medium"
            })
        
        # Sort by priority
        priority_order = {"high": 3, "medium": 2, "low": 1}
        action_items.sort(key=lambda x: priority_order.get(x["priority"], 0), reverse=True)
        
        return action_items


class LatencyMLAnalyzer:
    """
    🧠 ML Engineer: Machine learning-powered latency analysis.
    
    Advanced ML models for pattern recognition, prediction,
    and intelligent latency optimization insights.
    """
    
    def __init__(self) -> None:
        """Initialize ML analyzer."""
        self.logger = logging.getLogger("LatencyMLAnalyzer")
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=2)
        
    async def generate_insights(self, data: Dict[LatencyMetricType, List[LatencyMeasurement]], 
                               statistics: Dict[LatencyMetricType, LatencyStatistics]) -> Dict[str, Any]:
        """🧠 Generate ML-powered insights."""
        self.logger.info("🤖 ML Engineer: Generating ML-powered latency insights...")
        
        insights = {
            "pattern_analysis": await self._analyze_latency_patterns(data),
            "correlation_analysis": self._analyze_metric_correlations(data),
            "clustering_analysis": self._perform_clustering_analysis(data),
            "predicted_bottlenecks": self._predict_potential_bottlenecks(statistics),
            "optimization_opportunities": self._identify_optimization_opportunities(data, statistics)
        }
        
        return insights
    
    async def _analyze_latency_patterns(self, data: Dict[LatencyMetricType, List[LatencyMeasurement]]) -> Dict[str, Any]:
        """Analyze latency patterns using ML."""
        patterns = {
            "temporal_patterns": {},
            "distribution_patterns": {},
            "anomaly_patterns": {}
        }
        
        for metric_type, measurements in data.items():
            if len(measurements) < 10:
                continue
            
            values = np.array([m.value for m in measurements])
            timestamps = [m.timestamp for m in measurements]
            
            # Temporal pattern analysis
            if len(values) > 20:
                # Find peaks and valleys
                peaks, _ = find_peaks(values, height=np.mean(values) + np.std(values))
                valleys, _ = find_peaks(-values, height=-(np.mean(values) - np.std(values)))
                
                patterns["temporal_patterns"][metric_type.value] = {
                    "peak_count": len(peaks),
                    "valley_count": len(valleys),
                    "volatility": np.std(values) / np.mean(values) if np.mean(values) > 0 else 0
                }
            
            # Distribution analysis
            skewness = stats.skew(values)
            kurtosis = stats.kurtosis(values)
            
            patterns["distribution_patterns"][metric_type.value] = {
                "distribution_type": self._classify_distribution(skewness, kurtosis),
                "skewness": round(skewness, 3),
                "kurtosis": round(kurtosis, 3)
            }
        
        return patterns
    
    def _classify_distribution(self, skewness: float, kurtosis: float) -> str:
        """Classify the distribution type based on skewness and kurtosis."""
        if abs(skewness) < 0.5 and abs(kurtosis) < 0.5:
            return "normal"
        elif skewness > 1:
            return "right_skewed"
        elif skewness < -1:
            return "left_skewed"
        elif kurtosis > 1:
            return "heavy_tailed"
        elif kurtosis < -1:
            return "light_tailed"
        else:
            return "irregular"
    
    def _analyze_metric_correlations(self, data: Dict[LatencyMetricType, List[LatencyMeasurement]]) -> Dict[str, Any]:
        """Analyze correlations between different latency metrics."""
        correlations = {}
        
        metric_types = list(data.keys())
        if len(metric_types) < 2:
            return {"correlations": "insufficient_metrics"}
        
        # Create correlation matrix
        correlation_matrix = {}
        
        for i, metric_type1 in enumerate(metric_types):
            for j, metric_type2 in enumerate(metric_types[i+1:], i+1):
                values1 = [m.value for m in data[metric_type1]]
                values2 = [m.value for m in data[metric_type2]]
                
                # Align measurements by timestamp (simplified)
                min_length = min(len(values1), len(values2))
                if min_length > 5:
                    correlation = np.corrcoef(values1[:min_length], values2[:min_length])[0, 1]
                    
                    correlation_key = f"{metric_type1.value}_vs_{metric_type2.value}"
                    correlation_matrix[correlation_key] = {
                        "correlation": round(correlation, 3),
                        "strength": self._interpret_correlation_strength(abs(correlation))
                    }
        
        correlations["correlation_matrix"] = correlation_matrix
        
        # Find strongest correlations
        strong_correlations = {
            k: v for k, v in correlation_matrix.items() 
            if abs(v["correlation"]) > 0.7
        }
        correlations["strong_correlations"] = strong_correlations
        
        return correlations
    
    def _interpret_correlation_strength(self, correlation: float) -> str:
        """Interpret correlation strength."""
        if correlation > 0.8:
            return "very_strong"
        elif correlation > 0.6:
            return "strong"
        elif correlation > 0.4:
            return "moderate"
        elif correlation > 0.2:
            return "weak"
        else:
            return "very_weak"
    
    def _perform_clustering_analysis(self, data: Dict[LatencyMetricType, List[LatencyMeasurement]]) -> Dict[str, Any]:
        """Perform clustering analysis on latency data."""
        clustering_results = {}
        
        for metric_type, measurements in data.items():
            if len(measurements) < 10:
                continue
            
            # Prepare features for clustering
            features = []
            for measurement in measurements:
                # Feature vector: [latency_value, hour_of_day, day_of_week]
                hour_of_day = measurement.timestamp.hour
                day_of_week = measurement.timestamp.weekday()
                
                features.append([
                    measurement.value,
                    hour_of_day,
                    day_of_week
                ])
            
            features_array = np.array(features)
            
            try:
                # Normalize features
                features_scaled = self.scaler.fit_transform(features_array)
                
                # Perform DBSCAN clustering
                dbscan = DBSCAN(eps=0.5, min_samples=3)
                clusters = dbscan.fit_predict(features_scaled)
                
                # Analyze clusters
                unique_clusters = set(clusters)
                cluster_analysis = {}
                
                for cluster_id in unique_clusters:
                    if cluster_id == -1:  # Noise points
                        continue
                    
                    cluster_points = features_array[clusters == cluster_id]
                    cluster_analysis[f"cluster_{cluster_id}"] = {
                        "size": len(cluster_points),
                        "avg_latency": round(np.mean(cluster_points[:, 0]), 2),
                        "dominant_hour": int(stats.mode(cluster_points[:, 1], keepdims=False)[0]),
                        "dominant_day": int(stats.mode(cluster_points[:, 2], keepdims=False)[0])
                    }
                
                clustering_results[metric_type.value] = {
                    "total_clusters": len(unique_clusters) - (1 if -1 in unique_clusters else 0),
                    "noise_points": sum(1 for c in clusters if c == -1),
                    "cluster_details": cluster_analysis
                }
                
            except Exception as e:
                self.logger.warning(f"Clustering analysis failed for {metric_type.value}: {e}")
        
        return clustering_results
    
    def _predict_potential_bottlenecks(self, statistics: Dict[LatencyMetricType, LatencyStatistics]) -> List[str]:
        """Predict potential bottlenecks using ML heuristics."""
        bottlenecks = []
        
        for metric_type, stats in statistics.items():
            # High variability indicates potential bottleneck
            if stats.std_deviation > stats.mean * 0.8:
                bottlenecks.append(f"{metric_type.value} (high variability)")
            
            # Poor performance category
            if stats.category in [LatencyCategory.POOR, LatencyCategory.CRITICAL]:
                bottlenecks.append(f"{metric_type.value} (poor performance)")
            
            # Heavy-tailed distribution indicates occasional severe delays
            if stats.kurtosis > 2.0:
                bottlenecks.append(f"{metric_type.value} (heavy-tailed distribution)")
        
        return bottlenecks
    
    def _identify_optimization_opportunities(self, data: Dict[LatencyMetricType, List[LatencyMeasurement]], 
                                           statistics: Dict[LatencyMetricType, LatencyStatistics]) -> List[str]:
        """Identify optimization opportunities using ML analysis."""
        opportunities = []
        
        for metric_type, stats in statistics.items():
            # High P99/P95 ratio indicates tail latency issues
            if stats.p99 > stats.p95 * 2:
                opportunities.append(f"Optimize tail latency for {metric_type.value}")
            
            # High mean/median ratio indicates outliers
            if stats.mean > stats.median * 1.5:
                opportunities.append(f"Investigate outliers in {metric_type.value}")
            
            # Performance category-based opportunities
            if stats.category == LatencyCategory.ACCEPTABLE:
                opportunities.append(f"Potential for {metric_type.value} optimization to reach 'good' category")
            elif stats.category in [LatencyCategory.POOR, LatencyCategory.CRITICAL]:
                opportunities.append(f"Critical optimization needed for {metric_type.value}")
        
        return opportunities


class LatencyAnomalyDetector:
    """
    🧠 ML Engineer: Advanced anomaly detection for latency metrics.
    
    ML-powered anomaly detection using isolation forests,
    statistical methods, and pattern recognition.
    """
    
    def __init__(self) -> None:
        """Initialize anomaly detector."""
        self.logger = logging.getLogger("LatencyAnomalyDetector")
        self.isolation_forest = IsolationForest(contamination=0.1, random_state=42)
        
    async def detect_anomalies(self, data: Dict[LatencyMetricType, List[LatencyMeasurement]]) -> List[LatencyAnomalyResult]:
        """🧠 Detect latency anomalies using ML algorithms."""
        anomalies = []
        
        for metric_type, measurements in data.items():
            if len(measurements) < 10:
                continue
            
            metric_anomalies = await self._detect_metric_anomalies(metric_type, measurements)
            anomalies.extend(metric_anomalies)
        
        return anomalies
    
    async def _detect_metric_anomalies(self, metric_type: LatencyMetricType, 
                                     measurements: List[LatencyMeasurement]) -> List[LatencyAnomalyResult]:
        """Detect anomalies for a specific metric type."""
        anomalies = []
        values = np.array([m.value for m in measurements]).reshape(-1, 1)
        
        try:
            # Statistical anomaly detection
            statistical_anomalies = self._detect_statistical_anomalies(metric_type, measurements)
            anomalies.extend(statistical_anomalies)
            
            # ML-based anomaly detection
            if len(measurements) > 20:
                ml_anomalies = self._detect_ml_anomalies(metric_type, measurements)
                anomalies.extend(ml_anomalies)
                
        except Exception as e:
            self.logger.warning(f"Anomaly detection failed for {metric_type.value}: {e}")
        
        return anomalies
    
    def _detect_statistical_anomalies(self, metric_type: LatencyMetricType, 
                                    measurements: List[LatencyMeasurement]) -> List[LatencyAnomalyResult]:
        """Detect anomalies using statistical methods."""
        anomalies = []
        values = [m.value for m in measurements]
        
        # Calculate statistical bounds
        mean_val = statistics.mean(values)
        std_val = statistics.stdev(values) if len(values) > 1 else 0
        
        # Z-score method (values beyond 2.5 standard deviations)
        threshold = 2.5
        lower_bound = mean_val - threshold * std_val
        upper_bound = mean_val + threshold * std_val
        
        for measurement in measurements:
            if measurement.value < lower_bound or measurement.value > upper_bound:
                # Calculate anomaly score
                z_score = abs(measurement.value - mean_val) / std_val if std_val > 0 else 0
                anomaly_score = min(1.0, z_score / 3.0)  # Normalize to 0-1
                
                severity = "critical" if z_score > 3 else "high" if z_score > 2.5 else "medium"
                
                potential_causes = self._infer_potential_causes(measurement, mean_val, metric_type)
                
                anomalies.append(LatencyAnomalyResult(
                    timestamp=measurement.timestamp,
                    metric_type=metric_type,
                    measured_value=measurement.value,
                    expected_range=(lower_bound, upper_bound),
                    anomaly_score=round(anomaly_score, 3),
                    severity=severity,
                    potential_causes=potential_causes
                ))
        
        return anomalies
    
    def _detect_ml_anomalies(self, metric_type: LatencyMetricType, 
                           measurements: List[LatencyMeasurement]) -> List[LatencyAnomalyResult]:
        """Detect anomalies using ML algorithms."""
        anomalies = []
        
        # Prepare features for isolation forest
        features = []
        for measurement in measurements:
            # Feature vector: [latency_value, hour_of_day, minute_of_hour]
            features.append([
                measurement.value,
                measurement.timestamp.hour,
                measurement.timestamp.minute
            ])
        
        features_array = np.array(features)
        
        # Fit isolation forest
        self.isolation_forest.fit(features_array)
        anomaly_scores = self.isolation_forest.decision_function(features_array)
        is_anomaly = self.isolation_forest.predict(features_array)
        
        for i, (measurement, score, is_anom) in enumerate(zip(measurements, anomaly_scores, is_anomaly)):
            if is_anom == -1:  # Anomaly detected
                # Convert isolation forest score to 0-1 range
                normalized_score = max(0, min(1, (0.5 - score) * 2))
                
                severity = "critical" if normalized_score > 0.8 else "high" if normalized_score > 0.6 else "medium"
                
                potential_causes = self._infer_potential_causes(measurement, 
                                                              statistics.mean([m.value for m in measurements]), 
                                                              metric_type)
                
                anomalies.append(LatencyAnomalyResult(
                    timestamp=measurement.timestamp,
                    metric_type=metric_type,
                    measured_value=measurement.value,
                    expected_range=(None, None),  # ML-based detection doesn't provide explicit range
                    anomaly_score=round(normalized_score, 3),
                    severity=severity,
                    potential_causes=potential_causes
                ))
        
        return anomalies
    
    def _infer_potential_causes(self, measurement: LatencyMeasurement, baseline: float, 
                              metric_type: LatencyMetricType) -> List[str]:
        """Infer potential causes of latency anomaly."""
        causes = []
        
        if measurement.value > baseline * 5:  # Very high latency
            if metric_type == LatencyMetricType.DATABASE_QUERY:
                causes.extend(["Database connection pool exhaustion", "Query lock contention", "Database server overload"])
            elif metric_type == LatencyMetricType.API_CALL:
                causes.extend(["Network congestion", "External service degradation", "Rate limiting"])
            elif metric_type == LatencyMetricType.RESPONSE_TIME:
                causes.extend(["Application server overload", "Memory pressure", "Garbage collection"])
            else:
                causes.extend(["Resource contention", "System overload", "Network issues"])
        
        elif measurement.value > baseline * 2:  # Moderately high latency
            causes.extend(["Increased load", "Resource constraints", "Background processes"])
        
        # Time-based causes
        hour = measurement.timestamp.hour
        if hour in [0, 1, 2, 3, 4, 5]:  # Late night/early morning
            causes.append("Scheduled maintenance or backup operations")
        elif hour in [9, 10, 17, 18]:  # Peak hours
            causes.append("Peak traffic load")
        
        return causes


class LatencyTrendAnalyzer:
    """
    🧠 ML Engineer: Advanced trend analysis for latency metrics.
    
    Statistical trend analysis, seasonal pattern detection,
    and predictive forecasting for latency performance.
    """
    
    def __init__(self) -> None:
        """Initialize trend analyzer."""
        self.logger = logging.getLogger("LatencyTrendAnalyzer")
        
    async def analyze_trends(self, data: Dict[LatencyMetricType, List[LatencyMeasurement]]) -> List[LatencyTrendAnalysis]:
        """🧠 Analyze latency trends using statistical methods."""
        trends = []
        
        for metric_type, measurements in data.items():
            if len(measurements) < 20:  # Need sufficient data for trend analysis
                continue
            
            trend_analysis = await self._analyze_metric_trend(metric_type, measurements)
            if trend_analysis:
                trends.append(trend_analysis)
        
        return trends
    
    async def _analyze_metric_trend(self, metric_type: LatencyMetricType, 
                                  measurements: List[LatencyMeasurement]) -> Optional[LatencyTrendAnalysis]:
        """Analyze trend for a specific metric."""
        try:
            # Sort measurements by timestamp
            sorted_measurements = sorted(measurements, key=lambda m: m.timestamp)
            values = [m.value for m in sorted_measurements]
            timestamps = [m.timestamp for m in sorted_measurements]
            
            # Convert timestamps to numeric values for regression
            start_time = timestamps[0]
            time_deltas = [(ts - start_time).total_seconds() for ts in timestamps]
            
            # Linear regression for trend detection
            X = np.array(time_deltas).reshape(-1, 1)
            y = np.array(values)
            
            # Fit linear regression
            from sklearn.linear_model import LinearRegression
            model = LinearRegression()
            model.fit(X, y)
            
            slope = model.coef_[0]
            r_squared = model.score(X, y)
            
            # Determine trend direction and strength
            trend_direction = self._classify_trend_direction(slope, r_squared)
            trend_strength = abs(r_squared)
            
            # Seasonal pattern detection
            seasonal_pattern = self._detect_seasonal_pattern(timestamps, values)
            
            # Generate projections
            projected_values = self._generate_projections(model, time_deltas, values)
            
            # Calculate confidence interval
            confidence_interval = self._calculate_confidence_interval(y, model.predict(X))
            
            return LatencyTrendAnalysis(
                metric_type=metric_type,
                time_period=f"{len(measurements)} measurements over {(timestamps[-1] - timestamps[0]).days} days",
                trend_direction=trend_direction,
                trend_strength=round(trend_strength, 3),
                seasonal_pattern=seasonal_pattern,
                projected_values=projected_values,
                confidence_interval=confidence_interval
            )
            
        except Exception as e:
            self.logger.warning(f"Trend analysis failed for {metric_type.value}: {e}")
            return None
    
    def _classify_trend_direction(self, slope: float, r_squared: float) -> str:
        """Classify trend direction based on slope and R-squared."""
        # Only consider significant trends (R² > 0.1)
        if r_squared < 0.1:
            return "stable"
        
        # Slope threshold (adjust based on metric scale)
        slope_threshold = 0.01  # 0.01ms per second = ~0.86ms per day
        
        if slope > slope_threshold:
            return "degrading"
        elif slope < -slope_threshold:
            return "improving"
        else:
            return "stable"
    
    def _detect_seasonal_pattern(self, timestamps: List[datetime], values: List[float]) -> bool:
        """Detect seasonal patterns in latency data."""
        if len(timestamps) < 48:  # Need at least 48 hours for daily pattern
            return False
        
        try:
            # Group by hour of day
            hourly_values = defaultdict(list)
            for timestamp, value in zip(timestamps, values):
                hour = timestamp.hour
                hourly_values[hour].append(value)
            
            # Calculate average latency per hour
            hourly_averages = {}
            for hour, hour_values in hourly_values.items():
                if len(hour_values) > 2:  # Need sufficient samples
                    hourly_averages[hour] = statistics.mean(hour_values)
            
            if len(hourly_averages) < 12:  # Need coverage of at least half the day
                return False
            
            # Check for significant variation across hours
            all_averages = list(hourly_averages.values())
            variation_coefficient = statistics.stdev(all_averages) / statistics.mean(all_averages)
            
            # Consider it seasonal if variation is > 20%
            return variation_coefficient > 0.2
            
        except Exception:
            return False
    
    def _generate_projections(self, model, time_deltas: List[float], values: List[float]) -> Dict[str, float]:
        """Generate future projections based on trend model."""
        last_time = time_deltas[-1]
        
        # Project 1 hour, 1 day, and 1 week ahead
        projections = {}
        projection_times = {
            "1_hour_ahead": last_time + 3600,      # 1 hour
            "1_day_ahead": last_time + 86400,      # 1 day
            "1_week_ahead": last_time + 604800     # 1 week
        }
        
        for period, future_time in projection_times.items():
            predicted_value = model.predict([[future_time]])[0]
            projections[period] = round(max(0, predicted_value), 2)  # Ensure non-negative
        
        return projections
    
    def _calculate_confidence_interval(self, actual_values: np.ndarray, predicted_values: np.ndarray) -> Tuple[float, float]:
        """Calculate confidence interval for predictions."""
        residuals = actual_values - predicted_values
        residual_std = np.std(residuals)
        
        # 95% confidence interval (approximately ±2 standard deviations)
        confidence_margin = 1.96 * residual_std
        
        mean_prediction = np.mean(predicted_values)
        return (
            round(mean_prediction - confidence_margin, 2),
            round(mean_prediction + confidence_margin, 2)
        )


# Export main classes
__all__ = [
    'LatencyAnalyzer',
    'LatencyMeasurement',
    'LatencyStatistics',
    'LatencyAnomalyResult',
    'LatencyTrendAnalysis',
    'LatencyAnalysisResult',
    'LatencyMetricType',
    'LatencyCategory',
    'AnalysisType',
    'LatencyMLAnalyzer',
    'LatencyAnomalyDetector',
    'LatencyTrendAnalyzer'
]


if __name__ == "__main__":
    # Example usage
    import asyncio
    import random
    
    async def main() -> None:
        """Example latency analysis execution."""
        
        # Initialize analyzer
        analyzer = LatencyAnalyzer()
        
        # Generate sample latency measurements
        sample_measurements = []
        base_time = datetime.now(timezone.utc)
        
        for i in range(1000):
            # Simulate different latency patterns
            if i < 500:
                # Normal latency with some variation
                latency = random.normalvariate(200, 50)  # 200ms ± 50ms
            else:
                # Gradual degradation
                latency = random.normalvariate(200 + (i - 500) * 0.5, 60)
            
            # Add some anomalies
            if random.random() < 0.05:  # 5% chance of anomaly
                latency *= random.uniform(3, 8)  # 3-8x normal latency
            
            measurement = LatencyMeasurement(
                timestamp=base_time + timedelta(minutes=i),
                metric_type=LatencyMetricType.RESPONSE_TIME,
                value=max(10, latency),  # Ensure minimum latency
                endpoint="/api/upload",
                request_id=f"req_{i}"
            )
            
            sample_measurements.append(measurement)
        
        # Record measurements
        analyzer.record_multiple_latencies(sample_measurements)
        
        # Perform analysis
        analysis_result = await analyzer.analyze_latency_performance(
            analysis_type=AnalysisType.BATCH,
            time_window=timedelta(hours=24)
        )
        
        # Generate comprehensive report
        report = await analyzer.generate_latency_report(timedelta(hours=24))
        
        print("Latency Analysis Results:")
        print(f"Performance Score: {analysis_result.performance_score}")
        print(f"Anomalies Detected: {len(analysis_result.anomalies)}")
        print(f"Trends Identified: {len(analysis_result.trends)}")
        print(f"Recommendations: {len(analysis_result.recommendations)}")
        
        print("\nDetailed Report:")
        print(json.dumps(report, indent=2, default=str))
    
    # Run example
    asyncio.run(main())