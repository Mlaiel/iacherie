"""⚡ Profiling Analytics Engine
============================

Advanced analytics and insights engine for profiling data from the Ainflue Creator Platform.
Provides ML-powered analysis, predictive optimization, and intelligent recommendations.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ INTELLECTUAL PROPERTY WARNING:
=====================================
This code is proprietary to Fahed Mlaiel <mlaiel@live.de>
- Commercial use FORBIDDEN without written authorization  
- Reverse engineering STRICTLY PROHIBITED
- Distribution FORBIDDEN without explicit license
- Violation = Automatic legal prosecution

🏢 ENTERPRISE USAGE:
- Enterprise license available on request
- Technical support included with license
- Maintenance and updates assured
- Technical team training provided
"""

import logging
import time
import threading
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import statistics
from collections import defaultdict, deque
import math

logger = logging.getLogger(__name__)

# Try to import machine learning libraries
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    logger.warning("numpy not available, some ML features disabled")

try:
    from sklearn.cluster import KMeans
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler
    from sklearn.decomposition import PCA
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False
    logger.warning("scikit-learn not available, ML analysis features disabled")

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    logger.warning("pandas not available, data analysis features limited")


class AnalysisType(Enum):
    """Types of profiling analysis"""
    PERFORMANCE_TREND = "performance_trend"
    ANOMALY_DETECTION = "anomaly_detection"
    BOTTLENECK_CLUSTERING = "bottleneck_clustering"
    OPTIMIZATION_PREDICTION = "optimization_prediction"
    CAPACITY_PLANNING = "capacity_planning"
    COST_ANALYSIS = "cost_analysis"
    USER_BEHAVIOR = "user_behavior"
    BUSINESS_IMPACT = "business_impact"


class InsightType(Enum):
    """Types of insights generated"""
    OPTIMIZATION = "optimization"
    WARNING = "warning"
    PREDICTION = "prediction"
    RECOMMENDATION = "recommendation"
    ANOMALY = "anomaly"
    TREND = "trend"


class PredictionHorizon(Enum):
    """Prediction time horizons"""
    SHORT_TERM = "short_term"    # 1-6 hours
    MEDIUM_TERM = "medium_term"  # 1-7 days
    LONG_TERM = "long_term"      # 1-4 weeks


@dataclass
class ProfilingInsight:
    """Generated insight from profiling analysis"""
    insight_id: str
    insight_type: InsightType
    title: str
    description: str
    confidence: float
    impact_score: float
    source_metrics: List[str]
    recommendations: List[str]
    predicted_outcome: Optional[str] = None
    time_horizon: Optional[PredictionHorizon] = None
    data_points: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PerformanceTrend:
    """Performance trend analysis result"""
    metric_name: str
    trend_direction: str  # "increasing", "decreasing", "stable", "volatile"
    slope: float
    r_squared: float
    prediction_24h: float
    prediction_7d: float
    confidence_interval: Tuple[float, float]
    anomaly_score: float


@dataclass
class OptimizationOpportunity:
    """Optimization opportunity identified by ML analysis"""
    opportunity_id: str
    area: str
    description: str
    potential_improvement: float
    implementation_effort: str  # "low", "medium", "high"
    roi_estimate: float
    priority_score: float
    dependencies: List[str] = field(default_factory=list)
    success_probability: float = 0.0


class ProfilingAnalyticsEngine:
    """
    Analytics engine for profiling data analysis and insights generation
    """
    
    def __init__(self, 
                 analysis_interval: float = 300.0,  # 5 minutes
                 data_retention_days: int = 30):
        self.analysis_interval = analysis_interval
        self.data_retention_days = data_retention_days
        self.is_running = False
        self.analysis_thread = None
        
        # Data storage
        self.profiling_data: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.generated_insights: deque = deque(maxlen=1000)
        self.optimization_opportunities: Dict[str, OptimizationOpportunity] = {}
        self.performance_trends: Dict[str, PerformanceTrend] = {}
        
        # ML models and analyzers
        self.anomaly_detectors: Dict[str, Any] = {}
        self.trend_analyzers: Dict[str, Any] = {}
        self.clustering_models: Dict[str, Any] = {}
        
        # Analysis configuration
        self.analysis_config = {
            'anomaly_detection_threshold': 0.1,
            'trend_analysis_min_points': 10,
            'clustering_min_samples': 5,
            'optimization_impact_threshold': 5.0,  # 5% improvement
            'prediction_confidence_threshold': 0.7
        }
        
        # Performance baselines
        self.performance_baselines: Dict[str, Dict] = {}
        
        logger.info("ProfilingAnalyticsEngine initialized")

    def start_analysis(self):
        """Start background analytics processing"""
        if not self.is_running:
            self.is_running = True
            self.analysis_thread = threading.Thread(
                target=self._analysis_loop,
                daemon=True
            )
            self.analysis_thread.start()
            logger.info("Profiling analytics started")

    def stop_analysis(self):
        """Stop background analytics processing"""
        self.is_running = False
        if self.analysis_thread:
            self.analysis_thread.join(timeout=5.0)
        logger.info("Profiling analytics stopped")

    def _analysis_loop(self):
        """Main analytics processing loop"""
        while self.is_running:
            try:
                # Run different types of analysis
                self._analyze_performance_trends()
                self._detect_anomalies()
                self._cluster_bottlenecks()
                self._predict_optimization_opportunities()
                self._analyze_capacity_requirements()
                self._generate_insights()
                self._cleanup_old_data()
                
                time.sleep(self.analysis_interval)
                
            except Exception as e:
                logger.error(f"Error in analytics loop: {e}")

    def ingest_profiling_data(self, metric_name: str, value: float, timestamp: datetime, metadata: Dict[str, Any] = None):
        """Ingest profiling data for analysis"""
        data_point = {
            'value': value,
            'timestamp': timestamp,
            'metadata': metadata or {}
        }
        
        self.profiling_data[metric_name].append(data_point)

    def ingest_batch_data(self, batch_data: Dict[str, List[Tuple[float, datetime, Dict]]]):
        """Ingest batch profiling data"""
        for metric_name, data_points in batch_data.items():
            for value, timestamp, metadata in data_points:
                self.ingest_profiling_data(metric_name, value, timestamp, metadata)

    def _analyze_performance_trends(self):
        """Analyze performance trends using time series analysis"""
        try:
            for metric_name, data_points in self.profiling_data.items():
                if len(data_points) < self.analysis_config['trend_analysis_min_points']:
                    continue
                
                # Extract time series data
                values = [dp['value'] for dp in data_points]
                timestamps = [dp['timestamp'] for dp in data_points]
                
                # Convert timestamps to numeric values for analysis
                if timestamps:
                    time_numeric = [(ts - timestamps[0]).total_seconds() for ts in timestamps]
                    
                    # Perform linear regression for trend analysis
                    trend_result = self._calculate_trend(time_numeric, values)
                    
                    if trend_result:
                        self.performance_trends[metric_name] = trend_result
                        
                        # Generate insight if significant trend detected
                        if abs(trend_result.slope) > 0.1 and trend_result.r_squared > 0.5:
                            self._generate_trend_insight(metric_name, trend_result)
                            
        except Exception as e:
            logger.error(f"Error analyzing performance trends: {e}")

    def _calculate_trend(self, x_values: List[float], y_values: List[float]) -> Optional[PerformanceTrend]:
        """Calculate trend statistics using linear regression"""
        try:
            if not HAS_NUMPY or len(x_values) < 3:
                return None
            
            x = np.array(x_values)
            y = np.array(y_values)
            
            # Calculate linear regression
            n = len(x)
            x_mean = np.mean(x)
            y_mean = np.mean(y)
            
            numerator = np.sum((x - x_mean) * (y - y_mean))
            denominator = np.sum((x - x_mean) ** 2)
            
            if denominator == 0:
                return None
            
            slope = numerator / denominator
            intercept = y_mean - slope * x_mean
            
            # Calculate R-squared
            y_pred = slope * x + intercept
            ss_tot = np.sum((y - y_mean) ** 2)
            ss_res = np.sum((y - y_pred) ** 2)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
            
            # Determine trend direction
            if abs(slope) < 0.01:
                trend_direction = "stable"
            elif slope > 0:
                trend_direction = "increasing"
            else:
                trend_direction = "decreasing"
            
            # Check for volatility
            std_dev = np.std(y)
            mean_val = np.mean(y)
            cv = (std_dev / mean_val) if mean_val != 0 else 0
            if cv > 0.3:  # High coefficient of variation
                trend_direction = "volatile"
            
            # Make predictions
            last_x = x[-1]
            prediction_24h = slope * (last_x + 24 * 3600) + intercept  # 24 hours in seconds
            prediction_7d = slope * (last_x + 7 * 24 * 3600) + intercept  # 7 days in seconds
            
            # Calculate confidence interval (simplified)
            std_error = np.sqrt(ss_res / (n - 2)) if n > 2 else 0
            confidence_interval = (prediction_24h - 2 * std_error, prediction_24h + 2 * std_error)
            
            # Calculate anomaly score based on recent deviations
            recent_values = y[-min(10, len(y)):]
            recent_predictions = slope * x[-len(recent_values):] + intercept
            anomaly_score = np.mean(np.abs(recent_values - recent_predictions)) / (std_dev + 1e-10)
            
            return PerformanceTrend(
                metric_name="",  # Will be set by caller
                trend_direction=trend_direction,
                slope=slope,
                r_squared=r_squared,
                prediction_24h=prediction_24h,
                prediction_7d=prediction_7d,
                confidence_interval=confidence_interval,
                anomaly_score=anomaly_score
            )
            
        except Exception as e:
            logger.error(f"Error calculating trend: {e}")
            return None

    def _detect_anomalies(self):
        """Detect anomalies using ML techniques"""
        try:
            if not HAS_SKLEARN:
                return
            
            for metric_name, data_points in self.profiling_data.items():
                if len(data_points) < 20:  # Need sufficient data
                    continue
                
                values = np.array([dp['value'] for dp in data_points]).reshape(-1, 1)
                
                # Use Isolation Forest for anomaly detection
                if metric_name not in self.anomaly_detectors:
                    self.anomaly_detectors[metric_name] = IsolationForest(
                        contamination=self.analysis_config['anomaly_detection_threshold'],
                        random_state=42
                    )
                    self.anomaly_detectors[metric_name].fit(values)
                
                # Detect anomalies in recent data
                recent_values = values[-10:]  # Last 10 data points
                anomaly_scores = self.anomaly_detectors[metric_name].decision_function(recent_values)
                anomalies = self.anomaly_detectors[metric_name].predict(recent_values)
                
                # Generate insights for anomalies
                for i, (score, is_anomaly) in enumerate(zip(anomaly_scores, anomalies)):
                    if is_anomaly == -1:  # Anomaly detected
                        self._generate_anomaly_insight(metric_name, recent_values[i][0], score)
                        
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")

    def _cluster_bottlenecks(self):
        """Cluster similar bottlenecks for pattern analysis"""
        try:
            if not HAS_SKLEARN or not HAS_NUMPY:
                return
            
            # Collect bottleneck data from all metrics
            bottleneck_features = []
            bottleneck_info = []
            
            for metric_name, data_points in self.profiling_data.items():
                for dp in data_points[-50:]:  # Recent data points
                    if dp['metadata'].get('is_bottleneck', False):
                        # Create feature vector
                        features = [
                            dp['value'],
                            dp['metadata'].get('cpu_usage', 0),
                            dp['metadata'].get('memory_usage', 0),
                            dp['metadata'].get('response_time', 0),
                            dp['metadata'].get('error_rate', 0)
                        ]
                        bottleneck_features.append(features)
                        bottleneck_info.append({
                            'metric_name': metric_name,
                            'timestamp': dp['timestamp'],
                            'value': dp['value']
                        })
            
            if len(bottleneck_features) >= self.analysis_config['clustering_min_samples']:
                # Perform clustering
                features_array = np.array(bottleneck_features)
                scaler = StandardScaler()
                scaled_features = scaler.fit_transform(features_array)
                
                # Determine optimal number of clusters (simple heuristic)
                n_clusters = min(5, max(2, len(bottleneck_features) // 10))
                
                kmeans = KMeans(n_clusters=n_clusters, random_state=42)
                cluster_labels = kmeans.fit_predict(scaled_features)
                
                # Analyze clusters
                self._analyze_bottleneck_clusters(cluster_labels, bottleneck_info, features_array)
                
        except Exception as e:
            logger.error(f"Error clustering bottlenecks: {e}")

    def _analyze_bottleneck_clusters(self, cluster_labels: 'np.ndarray', bottleneck_info: List[Dict], features: 'np.ndarray'):
        """Analyze bottleneck clusters to identify patterns"""
        try:
            cluster_analysis = defaultdict(list)
            
            for i, label in enumerate(cluster_labels):
                cluster_analysis[label].append({
                    'info': bottleneck_info[i],
                    'features': features[i]
                })
            
            # Generate insights for each cluster
            for cluster_id, cluster_data in cluster_analysis.items():
                if len(cluster_data) >= 3:  # Significant cluster
                    avg_features = np.mean([cd['features'] for cd in cluster_data], axis=0)
                    
                    insight = ProfilingInsight(
                        insight_id=f"cluster_{cluster_id}_{int(time.time())}",
                        insight_type=InsightType.TREND,
                        title=f"Bottleneck Pattern Cluster {cluster_id}",
                        description=f"Identified {len(cluster_data)} similar bottlenecks with common characteristics",
                        confidence=min(0.9, len(cluster_data) / 10.0),
                        impact_score=avg_features[0],  # Use value as impact
                        source_metrics=[cd['info']['metric_name'] for cd in cluster_data],
                        recommendations=[
                            "Investigate common root cause",
                            "Apply consistent optimization strategy",
                            "Monitor cluster metrics together"
                        ],
                        data_points={
                            'cluster_size': len(cluster_data),
                            'avg_value': float(avg_features[0]),
                            'affected_metrics': list(set(cd['info']['metric_name'] for cd in cluster_data))
                        }
                    )
                    
                    self.generated_insights.append(insight)
                    
        except Exception as e:
            logger.error(f"Error analyzing bottleneck clusters: {e}")

    def _predict_optimization_opportunities(self):
        """Predict optimization opportunities using ML analysis"""
        try:
            # Analyze each metric for optimization potential
            for metric_name, data_points in self.profiling_data.items():
                if len(data_points) < 20:
                    continue
                
                values = [dp['value'] for dp in data_points]
                
                # Calculate baseline performance
                if metric_name not in self.performance_baselines:
                    self.performance_baselines[metric_name] = {
                        'baseline_value': statistics.mean(values[:10]) if len(values) >= 10 else statistics.mean(values),
                        'best_value': min(values) if 'time' in metric_name.lower() or 'latency' in metric_name.lower() else max(values),
                        'worst_value': max(values) if 'time' in metric_name.lower() or 'latency' in metric_name.lower() else min(values)
                    }
                
                baseline = self.performance_baselines[metric_name]
                current_value = statistics.mean(values[-5:])  # Recent average
                
                # Calculate optimization potential
                if 'time' in metric_name.lower() or 'latency' in metric_name.lower():
                    # For latency metrics, improvement is reduction
                    potential_improvement = ((current_value - baseline['best_value']) / current_value) * 100
                else:
                    # For throughput metrics, improvement is increase
                    potential_improvement = ((baseline['best_value'] - current_value) / current_value) * 100
                
                if potential_improvement > self.analysis_config['optimization_impact_threshold']:
                    opportunity_id = f"opt_{metric_name}_{int(time.time())}"
                    
                    opportunity = OptimizationOpportunity(
                        opportunity_id=opportunity_id,
                        area=metric_name,
                        description=f"Potential {potential_improvement:.1f}% improvement in {metric_name}",
                        potential_improvement=potential_improvement,
                        implementation_effort=self._estimate_implementation_effort(metric_name),
                        roi_estimate=self._estimate_roi(metric_name, potential_improvement),
                        priority_score=potential_improvement * self._get_metric_criticality(metric_name),
                        success_probability=min(0.9, potential_improvement / 50.0)
                    )
                    
                    self.optimization_opportunities[opportunity_id] = opportunity
                    
                    # Generate optimization insight
                    self._generate_optimization_insight(opportunity)
                    
        except Exception as e:
            logger.error(f"Error predicting optimization opportunities: {e}")

    def _estimate_implementation_effort(self, metric_name: str) -> str:
        """Estimate implementation effort for optimization"""
        if any(keyword in metric_name.lower() for keyword in ['cache', 'memory', 'cpu']):
            return "medium"
        elif any(keyword in metric_name.lower() for keyword in ['database', 'network', 'storage']):
            return "high"
        else:
            return "low"

    def _estimate_roi(self, metric_name: str, improvement_percent: float) -> float:
        """Estimate ROI for optimization"""
        base_roi = improvement_percent / 10.0  # Simple heuristic
        
        # Adjust based on metric type
        if 'response_time' in metric_name.lower():
            return base_roi * 1.5  # User experience impact
        elif 'cpu' in metric_name.lower() or 'memory' in metric_name.lower():
            return base_roi * 1.2  # Resource cost savings
        else:
            return base_roi

    def _get_metric_criticality(self, metric_name: str) -> float:
        """Get criticality weight for a metric"""
        critical_keywords = ['response_time', 'error_rate', 'availability']
        high_keywords = ['cpu', 'memory', 'database']
        
        if any(keyword in metric_name.lower() for keyword in critical_keywords):
            return 1.0
        elif any(keyword in metric_name.lower() for keyword in high_keywords):
            return 0.8
        else:
            return 0.6

    def _analyze_capacity_requirements(self):
        """Analyze capacity requirements and scaling needs"""
        try:
            # Analyze resource usage trends
            resource_metrics = ['cpu_usage', 'memory_usage', 'disk_usage', 'network_usage']
            
            for metric_name in resource_metrics:
                if metric_name in self.profiling_data:
                    data_points = self.profiling_data[metric_name]
                    if len(data_points) >= 10:
                        values = [dp['value'] for dp in data_points]
                        
                        # Calculate growth rate
                        recent_avg = statistics.mean(values[-5:])
                        historical_avg = statistics.mean(values[:5])
                        
                        if historical_avg > 0:
                            growth_rate = ((recent_avg - historical_avg) / historical_avg) * 100
                            
                            # Predict future capacity needs
                            if growth_rate > 10:  # Growing more than 10%
                                self._generate_capacity_insight(metric_name, growth_rate, recent_avg)
                                
        except Exception as e:
            logger.error(f"Error analyzing capacity requirements: {e}")

    def _generate_insights(self):
        """Generate high-level insights from analysis results"""
        try:
            # Cross-metric correlation analysis
            self._analyze_metric_correlations()
            
            # Performance degradation detection
            self._detect_performance_degradation()
            
            # Business impact analysis
            self._analyze_business_impact()
            
        except Exception as e:
            logger.error(f"Error generating insights: {e}")

    def _analyze_metric_correlations(self):
        """Analyze correlations between different metrics"""
        try:
            if not HAS_NUMPY or len(self.profiling_data) < 2:
                return
            
            metric_names = list(self.profiling_data.keys())
            
            for i, metric1 in enumerate(metric_names):
                for metric2 in metric_names[i+1:]:
                    data1 = self.profiling_data[metric1]
                    data2 = self.profiling_data[metric2]
                    
                    if len(data1) >= 10 and len(data2) >= 10:
                        # Align timestamps and calculate correlation
                        correlation = self._calculate_correlation(data1, data2)
                        
                        if abs(correlation) > 0.7:  # Strong correlation
                            self._generate_correlation_insight(metric1, metric2, correlation)
                            
        except Exception as e:
            logger.error(f"Error analyzing metric correlations: {e}")

    def _calculate_correlation(self, data1: deque, data2: deque) -> float:
        """Calculate correlation between two metric time series"""
        try:
            if not HAS_NUMPY:
                return 0.0
            
            # Align data by timestamp
            aligned_data = []
            timestamps1 = {dp['timestamp']: dp['value'] for dp in data1}
            
            for dp2 in data2:
                if dp2['timestamp'] in timestamps1:
                    aligned_data.append((timestamps1[dp2['timestamp']], dp2['value']))
            
            if len(aligned_data) < 5:
                return 0.0
            
            values1, values2 = zip(*aligned_data)
            correlation_matrix = np.corrcoef(values1, values2)
            return correlation_matrix[0, 1] if not np.isnan(correlation_matrix[0, 1]) else 0.0
            
        except Exception as e:
            logger.error(f"Error calculating correlation: {e}")
            return 0.0

    def _detect_performance_degradation(self):
        """Detect overall performance degradation"""
        try:
            # Check if multiple metrics are showing negative trends
            degrading_metrics = []
            
            for metric_name, trend in self.performance_trends.items():
                if trend.trend_direction == "increasing" and any(
                    keyword in metric_name.lower() 
                    for keyword in ['latency', 'time', 'error', 'failure']
                ):
                    degrading_metrics.append(metric_name)
                elif trend.trend_direction == "decreasing" and any(
                    keyword in metric_name.lower() 
                    for keyword in ['throughput', 'success', 'availability']
                ):
                    degrading_metrics.append(metric_name)
            
            if len(degrading_metrics) >= 3:  # Multiple metrics degrading
                insight = ProfilingInsight(
                    insight_id=f"degradation_{int(time.time())}",
                    insight_type=InsightType.WARNING,
                    title="Performance Degradation Detected",
                    description=f"Multiple metrics showing degradation: {', '.join(degrading_metrics[:3])}",
                    confidence=0.8,
                    impact_score=len(degrading_metrics) * 10,
                    source_metrics=degrading_metrics,
                    recommendations=[
                        "Investigate system-wide performance issues",
                        "Check for infrastructure problems",
                        "Review recent changes",
                        "Scale resources if needed"
                    ],
                    data_points={'degrading_metrics_count': len(degrading_metrics)}
                )
                
                self.generated_insights.append(insight)
                
        except Exception as e:
            logger.error(f"Error detecting performance degradation: {e}")

    def _analyze_business_impact(self):
        """Analyze business impact of performance issues"""
        try:
            # Map technical metrics to business impact
            business_critical_metrics = {
                'response_time': 'user_experience',
                'error_rate': 'reliability',
                'availability': 'service_quality',
                'throughput': 'capacity'
            }
            
            high_impact_issues = []
            
            for metric_name, data_points in self.profiling_data.items():
                for technical_metric, business_area in business_critical_metrics.items():
                    if technical_metric in metric_name.lower():
                        recent_values = [dp['value'] for dp in list(data_points)[-10:]]
                        if recent_values:
                            avg_value = statistics.mean(recent_values)
                            
                            # Define business impact thresholds
                            thresholds = {
                                'response_time': 1000,  # 1 second
                                'error_rate': 5,        # 5%
                                'availability': 95,     # 95%
                                'throughput': 100       # 100 req/s
                            }
                            
                            threshold = thresholds.get(technical_metric, 0)
                            
                            if (technical_metric in ['response_time', 'error_rate'] and avg_value > threshold) or \
                               (technical_metric in ['availability', 'throughput'] and avg_value < threshold):
                                high_impact_issues.append({
                                    'metric': metric_name,
                                    'business_area': business_area,
                                    'value': avg_value,
                                    'threshold': threshold
                                })
            
            if high_impact_issues:
                self._generate_business_impact_insight(high_impact_issues)
                
        except Exception as e:
            logger.error(f"Error analyzing business impact: {e}")

    # Helper methods for generating specific types of insights

    def _generate_trend_insight(self, metric_name: str, trend: PerformanceTrend):
        """Generate insight for performance trend"""
        insight = ProfilingInsight(
            insight_id=f"trend_{metric_name}_{int(time.time())}",
            insight_type=InsightType.TREND,
            title=f"Performance Trend: {metric_name}",
            description=f"{metric_name} is {trend.trend_direction} with slope {trend.slope:.4f}",
            confidence=trend.r_squared,
            impact_score=abs(trend.slope) * 10,
            source_metrics=[metric_name],
            recommendations=self._get_trend_recommendations(trend),
            predicted_outcome=f"24h prediction: {trend.prediction_24h:.2f}",
            time_horizon=PredictionHorizon.SHORT_TERM,
            data_points={
                'slope': trend.slope,
                'r_squared': trend.r_squared,
                'prediction_24h': trend.prediction_24h,
                'prediction_7d': trend.prediction_7d
            }
        )
        
        self.generated_insights.append(insight)

    def _generate_anomaly_insight(self, metric_name: str, value: float, anomaly_score: float):
        """Generate insight for anomaly detection"""
        insight = ProfilingInsight(
            insight_id=f"anomaly_{metric_name}_{int(time.time())}",
            insight_type=InsightType.ANOMALY,
            title=f"Anomaly Detected: {metric_name}",
            description=f"Unusual value {value:.2f} detected for {metric_name}",
            confidence=min(0.9, abs(anomaly_score)),
            impact_score=abs(anomaly_score) * 10,
            source_metrics=[metric_name],
            recommendations=[
                "Investigate root cause of anomaly",
                "Check for system changes",
                "Monitor for recurring patterns",
                "Validate data accuracy"
            ],
            data_points={
                'anomaly_value': value,
                'anomaly_score': anomaly_score
            }
        )
        
        self.generated_insights.append(insight)

    def _generate_optimization_insight(self, opportunity: OptimizationOpportunity):
        """Generate insight for optimization opportunity"""
        insight = ProfilingInsight(
            insight_id=f"optimization_{opportunity.opportunity_id}",
            insight_type=InsightType.OPTIMIZATION,
            title=f"Optimization Opportunity: {opportunity.area}",
            description=opportunity.description,
            confidence=opportunity.success_probability,
            impact_score=opportunity.potential_improvement,
            source_metrics=[opportunity.area],
            recommendations=[
                f"Implement optimization for {opportunity.area}",
                f"Expected ROI: {opportunity.roi_estimate:.1f}",
                f"Implementation effort: {opportunity.implementation_effort}",
                "Monitor results post-implementation"
            ],
            data_points={
                'potential_improvement': opportunity.potential_improvement,
                'roi_estimate': opportunity.roi_estimate,
                'implementation_effort': opportunity.implementation_effort,
                'priority_score': opportunity.priority_score
            }
        )
        
        self.generated_insights.append(insight)

    def _generate_capacity_insight(self, metric_name: str, growth_rate: float, current_value: float):
        """Generate insight for capacity planning"""
        insight = ProfilingInsight(
            insight_id=f"capacity_{metric_name}_{int(time.time())}",
            insight_type=InsightType.PREDICTION,
            title=f"Capacity Planning: {metric_name}",
            description=f"{metric_name} growing at {growth_rate:.1f}% - current: {current_value:.1f}%",
            confidence=0.7,
            impact_score=growth_rate,
            source_metrics=[metric_name],
            recommendations=[
                "Plan capacity scaling",
                "Monitor resource usage closely",
                "Consider auto-scaling",
                "Review resource allocation"
            ],
            predicted_outcome=f"Capacity may be exceeded in {int(100/growth_rate)} periods",
            time_horizon=PredictionHorizon.MEDIUM_TERM,
            data_points={
                'growth_rate': growth_rate,
                'current_value': current_value
            }
        )
        
        self.generated_insights.append(insight)

    def _generate_correlation_insight(self, metric1: str, metric2: str, correlation: float):
        """Generate insight for metric correlation"""
        insight = ProfilingInsight(
            insight_id=f"correlation_{hash((metric1, metric2))}_{int(time.time())}",
            insight_type=InsightType.TREND,
            title=f"Strong Correlation: {metric1} & {metric2}",
            description=f"Strong correlation ({correlation:.3f}) detected between {metric1} and {metric2}",
            confidence=abs(correlation),
            impact_score=abs(correlation) * 10,
            source_metrics=[metric1, metric2],
            recommendations=[
                "Consider joint optimization",
                "Monitor both metrics together",
                "Investigate causal relationship",
                "Use correlation for prediction"
            ],
            data_points={'correlation': correlation}
        )
        
        self.generated_insights.append(insight)

    def _generate_business_impact_insight(self, high_impact_issues: List[Dict]):
        """Generate insight for business impact"""
        insight = ProfilingInsight(
            insight_id=f"business_impact_{int(time.time())}",
            insight_type=InsightType.WARNING,
            title="High Business Impact Issues Detected",
            description=f"{len(high_impact_issues)} performance issues affecting business metrics",
            confidence=0.9,
            impact_score=len(high_impact_issues) * 20,
            source_metrics=[issue['metric'] for issue in high_impact_issues],
            recommendations=[
                "Prioritize resolution of business-critical issues",
                "Escalate to management",
                "Implement immediate mitigation",
                "Plan long-term solutions"
            ],
            data_points={
                'affected_business_areas': list(set(issue['business_area'] for issue in high_impact_issues)),
                'issues_count': len(high_impact_issues)
            }
        )
        
        self.generated_insights.append(insight)

    def _get_trend_recommendations(self, trend: PerformanceTrend) -> List[str]:
        """Get recommendations based on trend analysis"""
        recommendations = []
        
        if trend.trend_direction == "increasing":
            recommendations.extend([
                "Monitor for potential performance degradation",
                "Consider preemptive optimization",
                "Plan capacity scaling"
            ])
        elif trend.trend_direction == "decreasing":
            recommendations.extend([
                "Investigate cause of decline",
                "Implement corrective measures",
                "Monitor for further degradation"
            ])
        elif trend.trend_direction == "volatile":
            recommendations.extend([
                "Investigate source of instability",
                "Implement smoothing mechanisms",
                "Review system configuration"
            ])
        else:  # stable
            recommendations.append("Maintain current performance levels")
        
        return recommendations

    def _cleanup_old_data(self):
        """Clean up old analytics data"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(days=self.data_retention_days)
            
            # Clean up old profiling data
            for metric_name in self.profiling_data:
                data_points = self.profiling_data[metric_name]
                while data_points and data_points[0]['timestamp'] < cutoff_time:
                    data_points.popleft()
            
            # Clean up old insights
            while (self.generated_insights and 
                   self.generated_insights[0].created_at < cutoff_time):
                self.generated_insights.popleft()
                
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")

    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get analytics engine performance summary"""
        return {
            "analytics_status": {
                "is_running": self.is_running,
                "analysis_interval": self.analysis_interval,
                "data_retention_days": self.data_retention_days
            },
            "data_summary": {
                "monitored_metrics": len(self.profiling_data),
                "total_data_points": sum(len(data) for data in self.profiling_data.values()),
                "generated_insights": len(self.generated_insights),
                "optimization_opportunities": len(self.optimization_opportunities)
            },
            "ml_models": {
                "anomaly_detectors": len(self.anomaly_detectors),
                "trend_analyzers": len(self.trend_analyzers),
                "clustering_models": len(self.clustering_models)
            },
            "recent_insights": [
                {
                    "type": insight.insight_type.value,
                    "title": insight.title,
                    "confidence": insight.confidence,
                    "impact_score": insight.impact_score,
                    "created_at": insight.created_at.isoformat()
                }
                for insight in list(self.generated_insights)[-10:]
            ],
            "top_opportunities": sorted(
                [
                    {
                        "area": opp.area,
                        "potential_improvement": opp.potential_improvement,
                        "roi_estimate": opp.roi_estimate,
                        "priority_score": opp.priority_score
                    }
                    for opp in self.optimization_opportunities.values()
                ],
                key=lambda x: x['priority_score'],
                reverse=True
            )[:5]
        }

    def get_insights(self, insight_type: Optional[InsightType] = None, limit: int = 50) -> List[ProfilingInsight]:
        """Get generated insights"""
        insights = list(self.generated_insights)
        
        if insight_type:
            insights = [i for i in insights if i.insight_type == insight_type]
        
        return sorted(insights, key=lambda x: x.created_at, reverse=True)[:limit]

    def get_optimization_opportunities(self, min_impact: float = 0.0) -> List[OptimizationOpportunity]:
        """Get optimization opportunities"""
        opportunities = [
            opp for opp in self.optimization_opportunities.values()
            if opp.potential_improvement >= min_impact
        ]
        
        return sorted(opportunities, key=lambda x: x.priority_score, reverse=True)

    def export_analytics(self, format: str = "json") -> str:
        """Export analytics results"""
        data = {
            "insights": [
                {
                    "insight_id": insight.insight_id,
                    "type": insight.insight_type.value,
                    "title": insight.title,
                    "description": insight.description,
                    "confidence": insight.confidence,
                    "impact_score": insight.impact_score,
                    "created_at": insight.created_at.isoformat()
                }
                for insight in list(self.generated_insights)[-100:]
            ],
            "optimization_opportunities": [
                {
                    "opportunity_id": opp.opportunity_id,
                    "area": opp.area,
                    "description": opp.description,
                    "potential_improvement": opp.potential_improvement,
                    "roi_estimate": opp.roi_estimate,
                    "priority_score": opp.priority_score
                }
                for opp in self.optimization_opportunities.values()
            ],
            "performance_trends": {
                metric: {
                    "trend_direction": trend.trend_direction,
                    "slope": trend.slope,
                    "r_squared": trend.r_squared,
                    "prediction_24h": trend.prediction_24h
                }
                for metric, trend in self.performance_trends.items()
            }
        }
        
        if format == "json":
            return json.dumps(data, indent=2)
        else:
            return str(data)


# Factory function
def create_profiling_analytics_engine(analysis_interval: float = 300.0,
                                     data_retention_days: int = 30,
                                     start_analysis: bool = True) -> ProfilingAnalyticsEngine:
    """
    Create and configure a profiling analytics engine
    
    Args:
        analysis_interval: Analysis interval in seconds
        data_retention_days: How long to retain data
        start_analysis: Start background analysis
        
    Returns:
        Configured ProfilingAnalyticsEngine instance
    """
    engine = ProfilingAnalyticsEngine(
        analysis_interval=analysis_interval,
        data_retention_days=data_retention_days
    )
    
    if start_analysis:
        engine.start_analysis()
    
    return engine


# Main execution
if __name__ == "__main__":
    # Example usage
    engine = create_profiling_analytics_engine(analysis_interval=30.0)  # 30 second intervals for demo
    
    try:
        print("Profiling analytics engine started...")
        
        # Simulate some profiling data
        import random
        
        for i in range(100):
            # Simulate various metrics
            engine.ingest_profiling_data(
                "response_time", 
                random.uniform(100, 500), 
                datetime.utcnow(),
                {'endpoint': '/api/upload'}
            )
            
            engine.ingest_profiling_data(
                "cpu_usage", 
                random.uniform(30, 80), 
                datetime.utcnow()
            )
            
            engine.ingest_profiling_data(
                "memory_usage", 
                random.uniform(40, 85), 
                datetime.utcnow()
            )
            
            time.sleep(0.1)  # Simulate time passing
        
        # Wait for analysis
        time.sleep(35)
        
        # Get analytics summary
        summary = engine.get_analytics_summary()
        print(f"Analytics summary: {json.dumps(summary, indent=2)}")
        
        # Get insights
        insights = engine.get_insights(limit=5)
        if insights:
            print(f"\nGenerated {len(insights)} insights:")
            for insight in insights:
                print(f"- {insight.title}: {insight.description}")
        
        # Get optimization opportunities
        opportunities = engine.get_optimization_opportunities()
        if opportunities:
            print(f"\nOptimization opportunities:")
            for opp in opportunities[:3]:
                print(f"- {opp.area}: {opp.potential_improvement:.1f}% improvement potential")
        
    finally:
        engine.stop_analysis()